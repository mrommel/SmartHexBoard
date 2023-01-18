import math

from smarthexboard.map.base import Array2D, Point
from smarthexboard.map.map import Map
from smarthexboard.map.types import ClimateZone, MapType, MapSize, TerrainType
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

		noise1 = PerlinNoise(octaves=1*octaves)
		noise2 = PerlinNoise(octaves=2*octaves)
		noise3 = PerlinNoise(octaves=4*octaves)
		noise4 = PerlinNoise(octaves=8*octaves)

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
		self.plots = Array2D(self.width, self.height, TerrainType.sea)
		self.distance_to_coast = Array2D(self.width, self.height, 0)
		self.climate_zones = Array2D(self.width, self.height, ClimateZone.polar)
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
		self._setClimateZones()

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
		pass

	def _refineClimate(self):
		pass

	def _refineTerrain(self, grid, height_map, moisture_map):
		pass

	def _blendTerrains(self, grid):
		pass

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
