import math
import random
import sys

from smarthexboard.map.base import Array2D, Point, HexPoint, HexDirection
from smarthexboard.map.map import Map
from smarthexboard.map.types import ClimateZone, MapType, MapSize, TerrainType, FeatureType, MapAge
from smarthexboard.perlin_noise.perlin_noise import PerlinNoise


# https://www.redblobgames.com/maps/terrain-from-noise/
class HeightMap(Array2D):
	def __init__(self, width: int, height: int, octaves: int = 4):
		super().__init__(width, height, 0.0)
		self.width = width
		self.height = height
		self._generate(octaves)
		self._normalize()

	def _generate(self, octaves: int):
		"""
			generates the heightmap based on the input parameters

			@param octaves: object
		"""

		noise1 = PerlinNoise(octaves=1 * octaves)
		noise2 = PerlinNoise(octaves=2 * octaves)
		noise3 = PerlinNoise(octaves=4 * octaves)
		noise4 = PerlinNoise(octaves=8 * octaves)

		for x in range(self.width):
			for y in range(self.height):
				nx = float(x) / float(self.width)
				ny = float(y) / float(self.height)

				value0 = 1.00 * noise1.noise([nx, ny])
				value1 = 0.50 * noise2.noise([nx, ny])
				value2 = 0.25 * noise3.noise([nx, ny])
				value3 = 0.125 * noise4.noise([nx, ny])

				value = math.fabs(value0 + value1 + value2 + value3)  # / 1.875

				self.values[y][x] = value

	def _normalize(self):
		min_value = 1000.0
		max_value = -1000.0

		for x in range(self.width):
			for y in range(self.height):
				min_value = min(min_value, self.values[y][x])
				max_value = max(max_value, self.values[y][x])

		for x in range(self.width):
			for y in range(self.height):
				self.values[y][x] = (self.values[y][x] - min_value) / (max_value - min_value)

	def findThresholdAbove(self, percentage):
		"""
			this function takes the complete height map into account for land only

			@param percentage: value to check
			@return: heightmap value where percentage is above
		"""
		tmp_array = []

		# fill from map
		for x in range(self.width):
			for y in range(self.height):
				tmp_array.append(self.values[y][x])

		# sorted smallest first, highest last
		tmp_array.sort()
		tmp_array.reverse()

		threshold_index = math.floor(len(tmp_array) * percentage)

		return tmp_array[threshold_index]


class MapOptions:
	def __init__(self, map_size: MapSize, map_type: MapType):
		self.map_size = map_size
		self.map_type = map_type
		self.rivers = 20
		self.age = MapAge.normal

	def mountains_percentage(self):
		""" Percentage of mountain on land """
		if self.age == MapAge.young:
			return 0.08
		elif self.age == MapAge.normal:
			return 0.06
		elif self.age == MapAge.old:
			return 0.04

	def waterPercentage(self):
		""" abc """
		if self.map_type == MapType.continents:
			return 0.52  # low
		elif self.map_type == MapType.earth:
			return 0.65
		elif self.map_type == MapType.pangaea:
			return 0.65
		elif self.map_type == MapType.archipelago:
			return 0.65
		#
		#         case .custom:
		#
		#             switch enhanced.sealevel {
		#
		#             case .low:
		#                 return 0.52
		#             case .normal:
		#                 return 0.65
		#             case .high:
		#                 return 0.81

	def land_percentage(self):
		return 1.0 - self.waterPercentage()


class MapGeneratorState:
	def __init__(self, value, message):
		self.value = value
		self.message = message


class MapGenerator:
	def __init__(self, options: MapOptions):
		self.options = options
		self.width = options.map_size.size().width
		self.height = options.map_size.size().height

		# prepare terrain, distanceToCoast and zones
		self.plots = Array2D(self.width, self.height)

		for y in range(self.height):
			for x in range(self.width):
				self.plots.values[y][x] = TerrainType.sea

		self.distance_to_coast = Array2D(self.width, self.height, 0)
		self.climate_zones = Array2D(self.width, self.height)

		for y in range(self.height):
			for x in range(self.width):
				self.climate_zones.values[y][x] = ClimateZone.polar

		self.spring_locations = []

	def generate(self, callback):
		callback(MapGeneratorState(0.0, "TXT_KEY_MAP_GENERATOR_START"))
		grid = Map(self.width, self.height)

		height_map = self._generateHeightMap()
		moisture_map = HeightMap(self.width, self.height)

		callback(MapGeneratorState(0.1, "TXT_KEY_MAP_GENERATOR_INITED"))

		# 1st step: land / water
		threshold = height_map.findThresholdAbove(0.40)  # 40 % is land
		self._fillFromElevation(height_map, threshold)

		callback(MapGeneratorState(0.3, "TXT_KEY_MAP_GENERATOR_ELEVATION"))

		# 2nd step: climate
		self._setClimateZones(grid)

		callback(MapGeneratorState(0.35, "TXT_KEY_MAP_GENERATOR_CLIMATE"))

		# 2.1nd step: refine climate based on cost distance
		self._prepareDistanceToCoast()
		self._refineClimate()

		callback(MapGeneratorState(0.4, "TXT_KEY_MAP_GENERATOR_COASTAL"))

		# 3rd step: refine terrain
		self._refineTerrain(grid, height_map, moisture_map)
		self._blendTerrains(grid)

		callback(MapGeneratorState(0.5, "TXT_KEY_MAP_GENERATOR_TERRAIN"))

		self._placeResources(grid)

		callback(MapGeneratorState(0.6, "TXT_KEY_MAP_GENERATOR_RESOURCES"))

		# 4th step: rivers
		self._placeRivers(self.options.rivers, grid, height_map)

		callback(MapGeneratorState(0.7, "TXT_KEY_MAP_GENERATOR_RIVERS"))

		# 5th step: features
		self._refineFeatures(grid)

		callback(MapGeneratorState(0.8, "TXT_KEY_MAP_GENERATOR_FEATURES"))

		# 6th step: features
		self._refineNaturalWonders(grid)

		callback(MapGeneratorState(0.83, "TXT_KEY_MAP_GENERATOR_NATURAL_WONDERS"))

		# 7th step: continents & oceans
		self._identifyContinents(grid)

		callback(MapGeneratorState(0.86, "TXT_KEY_MAP_GENERATOR_CONTINENTS"))

		self._identifyOceans(grid)

		callback(MapGeneratorState(0.9, "TXT_KEY_MAP_GENERATOR_OCEANS"))

		self._identifyStartPositions(grid)

		callback(MapGeneratorState(0.95, "TXT_KEY_MAP_GENERATOR_POSITIONS"))

		self._addGoodyHuts(grid)

		callback(MapGeneratorState(0.99, "TXT_KEY_MAP_GENERATOR_GOODIES"))

		# debug
		# grid.modifyIsHillsAt(2, 2, True)
		# grid.modifyIsHillsAt(2, 3, True)

		return grid

	def _generateHeightMap(self):
		if self.options.map_type == MapType.continents:
			return HeightMap(self.width, self.height, 4)
		elif self.options.map_type == MapType.pangaea:
			return HeightMap(self.width, self.height, 2)
		elif self.options.map_type == MapType.archipelago:
			return HeightMap(self.width, self.height, 8)
		else:
			return HeightMap(self.width, self.height, 4)  # fallback

	def _fillFromElevation(self, height_map, threshold):

		for x in range(self.width):
			for y in range(self.height):
				tile_height = height_map.values[y][x]
				if tile_height > threshold:
					self.plots.values[y][x] = TerrainType.land
					print('above threshold')
				else:
					self.plots.values[y][x] = TerrainType.sea
					print('below threshold')

	def _setClimateZones(self, grid):
		self.climate_zones.fill(ClimateZone.temperate)

		for x in range(self.width):
			for y in range(self.height):
				latitude = abs((self.height / 2 - y)) / (self.height / 2.0)

				if latitude > 0.9 or y == 0 or y == (self.height - 1):
					self.climate_zones.values[y][x] = ClimateZone.polar
				elif latitude > 0.65:
					self.climate_zones.values[y][x] = ClimateZone.sub_polar
				elif latitude > 0.4:
					self.climate_zones.values[y][x] = ClimateZone.temperate
				elif latitude > 0.2:
					self.climate_zones.values[y][x] = ClimateZone.sub_tropic
				else:
					self.climate_zones.values[y][x] = ClimateZone.tropic

	def _prepareDistanceToCoast(self):
		self.distance_to_coast.fill(sys.maxsize)

		action_happened = True
		while action_happened:
			# reset
			action_happened = False

			for x in range(self.width):
				for y in range(self.height):
					# this needs to be analyzed
					if self.distance_to_coast.values[y][x] == sys.maxsize:
						# if field is ocean = > no distance
						if self.plots.values[y][x] == TerrainType.sea:
							self.distance_to_coast.values[y][x] = 0
							action_happened = True
						else:
							# check neighbors
							distance = sys.maxsize
							point = HexPoint(x, y)

							for direction in HexDirection.list():
								neighbor = point.neighbor(direction, 1)

								if 0 <= neighbor.x < self.width and 0 <= neighbor.y < self.height:
									if self.distance_to_coast.values[neighbor.y][neighbor.x] < sys.maxsize:
										distance = min(distance,
										               self.distance_to_coast.values[neighbor.y][neighbor.x] + 1)

							if distance < sys.maxsize:
								self.distance_to_coast.values[y][x] = distance
								action_happened = True

	def _refineClimate(self):
		for x in range(self.width):
			for y in range(self.height):
				distance = self.distance_to_coast.values[y][x]

				if distance < 2:
					self.climate_zones.values[y][x] = self.climate_zones.values[y][x].moderate()

	# 3rd step methods
	def _refineTerrain(self, grid, height_map, moisture_map):
		land_plots = 0

		for x in range(self.width):
			for y in range(self.height):
				grid_point = HexPoint(x, y)

				if self.plots.values[y][x] == TerrainType.sea:
					# check is next continent
					next_to_continent = any(
						map(lambda neighbor: grid.valid(neighbor) and grid.terrainAt(neighbor).isLand(),
						    grid_point.neighbors()))

					if height_map.values[y][x] > 0.1 or next_to_continent:
						grid.modifyTerrainAt(grid_point, TerrainType.shore)
					else:
						grid.modifyTerrainAt(grid_point, TerrainType.ocean)
				else:
					land_plots = land_plots + 1

					# grid.modifyTerrainAt(grid_point, TerrainType.grass)
					self._updateBiome(
						grid_point,
						grid,
						height_map.values[y][x],
						moisture_map.values[y][x],
						self.climate_zones.values[y][x]
					)

		for x in range(self.width):
			for y in range(self.height):
				grid_point = HexPoint(x, y)

				if grid.terrainAt(grid_point) == TerrainType.ocean:
					should_be_shore = False

					for neighbor in grid_point.neighbors():
						if not grid.valid(neighbor):
							continue

						neighbor_terrain = grid.terrainAt(neighbor)

						if neighbor_terrain.isLand():
							should_be_shore = True
							break

					if should_be_shore:
						grid.modifyTerrainAt(grid_point, TerrainType.shore)

		# Expanding coasts (MapGenerator.Lua)
		# Chance for each eligible plot to become an expansion is 1 / iExpansionDiceroll.
		# Default is two passes at 1/4 chance per eligible plot on each pass.
		for _ in range(2):
			shallow_water_plots = []
			for x in range(self.width):
				for y in range(self.height):
					grid_point = HexPoint(x, y)

					if grid.terrainAt(grid_point) == TerrainType.ocean:
						is_adjacent_to_shallow_water = False

						for neighbor in grid_point.neighbors():
							if not grid.valid(neighbor):
								continue
							neighbor_terrain = grid.terrainAt(neighbor)

							if neighbor_terrain == TerrainType.shore and random.random() <= 0.2:
								is_adjacent_to_shallow_water = True
								break

						if is_adjacent_to_shallow_water:
							shallow_water_plots.append(grid_point)

			for shallow_water_plot in shallow_water_plots:
				grid.modifyTerrainAt(shallow_water_plot, TerrainType.shore)

		# get the highest percent tiles from height map
		combined_percentage = self.options.mountains_percentage() * self.options.land_percentage()
		mountain_threshold = height_map.findThresholdAbove(combined_percentage)

		number_of_mountains = 0

		for x in range(self.width):
			for y in range(self.height):
				grid_point = HexPoint(x, y)

				if height_map.values[y][x] >= mountain_threshold:
					grid.modifyFeatureAt(grid_point, FeatureType.mountains)
					number_of_mountains += 1
		#
		#         # remove some mountains, where there are mountain neighbors
		#         let points = grid.points().shuffled
		#
		#         for gridPoint in points {
		#
		#             var mountainNeighbors = 0
		#             var numberNeighbors = 0
		#
		#             for neighbor in gridPoint.neighbors() {
		#
		#                 guard let neighborTile = grid.tile(at: neighbor) else {
		#                     continue
		#                 }
		#
		#                 if neighborTile.feature() == .mountains || neighborTile.feature() == .mountEverest || neighborTile.feature() == .mountKilimanjaro {
		#                     mountainNeighbors += 1
		#                 }
		#
		#                 numberNeighbors += 1
		#             }
		#
		#             if (numberNeighbors == 6 && mountainNeighbors >= 5) || (numberNeighbors == 5 && mountainNeighbors >= 4) {
		#                 grid.set(feature: .none, at: gridPoint)
		#                 print("mountain removed")
		#             }
		#         }
		#
		print(f"Number of Mountains: {number_of_mountains}")

	def _updateBiome(self, grid_point, grid, elevation, moisture, climate_zone):
		# from http://www.redblobgames.com/maps/terrain-from-noise/
		if climate_zone == ClimateZone.polar:
			self._updateBiomeForPolar(grid_point, grid, elevation, moisture)
		elif climate_zone == ClimateZone.sub_polar:
			self._updateBiomeForSubpolar(grid_point, grid, elevation, moisture)
		elif climate_zone == ClimateZone.temperate:
			self._updateBiomeForTemperate(grid_point, grid, elevation, moisture)
		elif climate_zone == ClimateZone.sub_tropic:
			self._updateBiomeForSubtropic(grid_point, grid, elevation, moisture)
		else:  # tropic
			self._updateBiomeForTropic(grid_point, grid, elevation, moisture)

	def _updateBiomeForPolar(self, grid_point, grid, elevation, moisture):
		if random.random() > 0.5:
			grid.modifyIsHillsAt(grid_point, True)

		grid.modifyTerrainAt(grid_point, TerrainType.snow)

	def _updateBiomeForSubpolar(self, grid_point, grid, elevation, moisture):
		if elevation > 0.7 and random.random() > 0.7:
			grid.modifyIsHillsAt(grid_point, True)
			grid.modifyTerrainAt(grid_point, TerrainType.snow)
			return

		if elevation > 0.5 and random.random() > 0.6:
			grid.modifyTerrainAt(grid_point, TerrainType.snow)
			return

		if random.random() > 0.85:
			grid.modifyIsHillsAt(grid_point, True)

		grid.modifyTerrainAt(grid_point, TerrainType.tundra)

	def _updateBiomeForTemperate(self, grid_point, grid, elevation, moisture):
		if elevation > 0.7 and random.random() > 0.7:
			grid.modifyIsHillsAt(grid_point, True)
			grid.modifyTerrainAt(grid_point, TerrainType.grass)
			return

		if random.random() > 0.85:
			grid.modifyIsHillsAt(grid_point, True)

		if moisture < 0.5:
			grid.modifyTerrainAt(grid_point, TerrainType.plains)
		else:
			grid.modifyTerrainAt(grid_point, TerrainType.grass)

	def _updateBiomeForSubtropic(self, grid_point, grid, elevation, moisture):
		if elevation > 0.7 and random.random() > 0.7:
			grid.modifyIsHillsAt(grid_point, True)
			grid.modifyTerrainAt(grid_point, TerrainType.plains)
			return

		if random.random() > 0.85:
			grid.modifyIsHillsAt(grid_point, True)

		if moisture < 0.2:
			if random.random() < 0.3:
				grid.modifyTerrainAt(grid_point, TerrainType.desert)
			else:
				grid.modifyTerrainAt(grid_point, TerrainType.plains)
		elif moisture < 0.6:
			grid.modifyTerrainAt(grid_point, TerrainType.plains)
		else:
			grid.modifyTerrainAt(grid_point, TerrainType.grass)

	def _updateBiomeForTropic(self, grid_point, grid, elevation, moisture):
		if elevation > 0.7 and random.random() > 0.7:
			grid.modifyIsHillsAt(grid_point, True)
			grid.modifyTerrainAt(grid_point, TerrainType.plains)
			return

		if random.random() > 0.85:
			grid.modifyIsHillsAt(grid_point, True)

		# arid
		if moisture < 0.3:
			if random.random() < 0.4:
				grid.modifyTerrainAt(grid_point, TerrainType.desert)
			else:
				grid.modifyTerrainAt(grid_point, TerrainType.plains)
		else:
			grid.modifyTerrainAt(grid_point, TerrainType.plains)

	def _blendTerrains(self, grid):
		# hillsBlendPercent = 0.45 -- Chance for flat land to become hills per near mountain. Requires at least 2 near mountains.
		terrain_blend_range = 3  # range to smooth terrain (desert surrounded by plains turns to plains, etc)
		terrain_blend_random = 0.6  # random modifier for terrain smoothing

		points = grid.points()
		random.shuffle(points)

		for pt in points:
			tile = grid.tileAt(pt)

			if tile.terrain.isWater():
				continue

			if tile.feature == FeatureType.mountains:
				num_near_mountains = 0

				for neighbor in pt.neighbors():
					if not grid.valid(neighbor):
						continue

					neighbor_feature = grid.featureAt(neighbor)

					if neighbor_feature == FeatureType.mountains:
						num_near_mountains = num_near_mountains + 1

				if 2 <= num_near_mountains <= 4:
					#self.createPossibleMountainPass(at: tile.point, on: gridRef)
					print(f'createPossibleMountainPass({pt})')
					pass

			else:
				rand_percent = 1.0 + random.random() * 2.0 * terrain_blend_random - terrain_blend_random
				plot_percents = grid.tileStatistics(pt, terrain_blend_range)
				if tile.terrain == TerrainType.grass:
					if plot_percents.desert + plot_percents.snow >= 0.33 * rand_percent:
						tile.terrain = TerrainType.plains
						if tile.feature == FeatureType.marsh:
							tile.feature = FeatureType.forest
				elif tile.terrain == TerrainType.plains:
					if plot_percents.desert >= 0.5 * rand_percent:
						# plot:SetTerrainType(TerrainTypes.TERRAIN_DESERT, true, true)
						pass
				elif tile.terrain == TerrainType.desert:
					if plot_percents.grass + plot_percents.snow >= 0.25 * rand_percent:
						tile.terrain = TerrainType.plains
				elif tile.feature == FeatureType.rainforest and tile.feature == FeatureType.marsh:
					if plot_percents.snow + plot_percents.tundra + plot_percents.desert >= 0.25 * rand_percent:
						tile.feature = FeatureType.none
				elif tile.terrain == TerrainType.tundra:
					if 2.0 * plot_percents.grass + plot_percents.plains + plot_percents.desert >= 0.5 * rand_percent:
						tile.terrain = TerrainType.plains

	def _placeResources(self, grid):
		pass

	def _placeRivers(self, rivers, grid, height_map):
		pass

	def _refineFeatures(self, grid):
		pass

	def _refineNaturalWonders(self, grid):
		pass

	def _identifyContinents(self, grid):
		pass

	def _identifyOceans(self, grid):
		pass

	def _identifyStartPositions(self, grid):
		pass

	def _addGoodyHuts(self, grid):
		pass
