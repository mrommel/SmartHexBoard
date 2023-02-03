import json
from json import JSONEncoder

from smarthexboard.map.base import Array2D, Size, HexPoint, HexDirection
from smarthexboard.map.types import TerrainType, FeatureType, ResourceType, ClimateZone, MovementType, RouteType


class Tile:
	pass


class Tile:
	"""
		class that holds a single tile of a Map

		it has a TerrainType, FeatureType, ResourceType and a boolean value for being hilly (or not)
	"""

	def __init__(self, point: HexPoint, terrain: TerrainType):
		"""
			constructs a Tile from a TerrainType

			@param point: location of the tile
			@param terrain: TerrainType
		"""
		self.point = point
		self.terrain = terrain
		self.is_hills = False
		self.feature = FeatureType.none
		self._resource = ResourceType.none  # property is hidden
		self.resource_quantity = 0
		self.river_value = 0
		self.climate_zone = ClimateZone.temperate
		self.route = RouteType.none

	def isWater(self):
		return self.terrain.isWater()

	def isLand(self):
		return self.terrain.isLand()

	def resourceFor(self, player) -> ResourceType:
		"""if no player is provided, no check for tech"""
		if self._resource != ResourceType.none:
			valid = True

			# check if already visible to player
			reveal_tech = self._resource._data().reveal_tech
			if reveal_tech is not None:
				if player is not None:
					if not player.has(reveal_tech):
						valid = False

			reveal_civic = self._resource._data().reveal_civic
			if reveal_civic is not None:
				if player is not None:
					if not player.has(reveal_civic):
						valid = False

			if valid:
				return self._resource

		return ResourceType.none

	def isImpassable(self, movement_ype):
		# start with terrain cost
		terrain_cost = self.terrain.movementCost(movement_ype)

		if terrain_cost == MovementType.max:
			return True

		if self.feature != FeatureType.none:
			feature_cost = self.feature.movementCost(movement_ype)

			if feature_cost == MovementType.max:
				return True

		return False

	def movementCost(self, movement_type: MovementType, from_tile: Tile) -> int:
		"""
			cost to enter a terrain given the specified movement_type

			@param movement_type: type of movement
			@param from_tile: tile the unit comes from
			@return: movement cost to go from {from_tile} to this tile
		"""
		# start with terrain cost
		terrain_cost = self.terrain.movementCost(movement_type)

		if terrain_cost == MovementType.max:
			return MovementType.max

		# hills
		hill_costs = 1.0 if self.is_hills else 0.0

		# add feature costs
		feature_costs = 0.0
		if self.feature != FeatureType.none:
			feature_cost = self.feature.movementCost(movement_type)

			if feature_cost == MovementType.max:
				return MovementType.max

			feature_costs = feature_cost

		# add river crossing cost
		river_cost = 0.0
		if from_tile.isRiverToCrossTowards(self):
			river_cost = 3.0  # FIXME - river cost per movementType

		# https://civilization.fandom.com/wiki/Roads_(Civ6)
		if self.hasAnyRoute():
			terrain_cost = self.route.movementCost()

			if self.route != RouteType.ancientRoad:
				river_cost = 0.0

			hill_costs = 0.0
			feature_costs = 0.0

		return terrain_cost + hill_costs + feature_costs + river_cost

	def isRiverToCrossTowards(self, target: Tile) -> bool:
		if not self.isNeighborTo(target.point):
			return False

		direction = self.point.directionTowards(target.point)

		if direction == HexDirection.north:
			return self.isRiverInNorth()
		elif direction == HexDirection.northEast:
			return self.isRiverInNorthEast()
		elif direction == HexDirection.southEast:
			return self.isRiverInSouthEast()
		elif direction == HexDirection.south:
			return target.isRiverInNorth()
		elif direction == HexDirection.southWest:
			return target.isRiverInNorthEast()
		elif direction == HexDirection.northWest:
			return target.isRiverInSouthEast()

	def to_dict(self):
		return {
			'terrain': self.terrain.value,
			'isHills': self.is_hills,
			'feature': self.feature.value,
			'resource': self._resource.value,
			'resource_quantity': self.resource_quantity
		}

	def isNeighborTo(self, candidate: HexPoint) -> bool:
		return self.point.distance(candidate) == 1

	def isRiverInNorth(self):
		"""river in north can flow from east or west direction"""
		# 0x01 => east
		# 0x02 => west
		return self.river_value & 0x01 > 0 or self.river_value & 0x02 > 0

	def isRiverInNorthEast(self):
		"""river in north-east can flow to northwest or southeast direction"""
		# 0x04 => northWest
		# 0x08 => southEast
		return self.river_value & 0x04 > 0 or self.river_value & 0x08 > 0

	def isRiverInSouthEast(self):
		"""river in south-east can flow to northeast or southwest direction"""
		# 0x16 => northWest
		# 0x32 => southEast
		return self.river_value & 0x10 > 0 or self.river_value & 0x20 > 0

	def hasAnyRoute(self):
		return False

	def canHaveResource(self, grid, resource: ResourceType, ignore_latitude: bool = False) -> bool:

		if resource == ResourceType.none:
			return True

		# only one resource per tile
		if self._resource != ResourceType.none:
			return False

		# no resources on natural wonders
		if self.feature.isNaturalWonder():
			return False

		# no resources on mountains
		if self.feature == FeatureType.mountains:
			return False

		if self.feature != FeatureType.none:
			if not resource.canBePlacedOnFeature(self.feature):
				return False

			if not resource.canBePlacedOnFeatureTerrain(self.terrain):
				return False
		else:
			# only checked if no feature
			if not resource.canBePlacedOnTerrain(self.terrain):
				return False

		if self.is_hills:
			if not resource.canBePlacedOnHills():
				return False
		elif self.isFlatlands():
			if not resource.canBePlacedOnFlatlands():
				return False

		if grid.riverAt(self.point):
			if not resource.canBePlacedOnRiverSide():
				return False

		return True

	def isFlatlands(self):
		if not self.terrain.isLand():
			return False

		if self.feature == FeatureType.mountains or self.feature == FeatureType.mountEverest or self.feature == FeatureType.mountKilimanjaro:
			return False

		return True


class TileStatistics:
	def __init__(self):
		self.ocean = 0.0
		self.shore = 0.0
		self.plains = 0.0
		self.grass = 0.0
		self.desert = 0.0
		self.tundra = 0.0
		self.snow = 0.0

	def normalize(self, factor):
		self.ocean /= factor
		self.shore /= factor
		self.plains /= factor
		self.grass /= factor
		self.desert /= factor
		self.tundra /= factor
		self.snow /= factor


class Map:
	def __init__(self, width, height=None):
		if isinstance(width, Size) and height is None:
			size = width
			self.width = size.width
			self.height = size.height
		elif isinstance(width, int) and isinstance(height, int):
			self.width = width
			self.height = height
		else:
			raise AttributeError(f'Map with wrong attributes: {width} / {height}')

		self.tiles = Array2D(self.width, self.height)

		# create a unique Tile per place
		for y in range(self.height):
			for x in range(self.width):
				self.tiles.values[y][x] = Tile(HexPoint(x, y), TerrainType.ocean)

	def valid(self, x_or_hex, y=None):
		if isinstance(x_or_hex, HexPoint) and y is None:
			hex_point = x_or_hex
			return 0 <= hex_point.x < self.width and 0 <= hex_point.y < self.height
		elif isinstance(x_or_hex, int) and isinstance(y, int):
			x = x_or_hex
			return 0 <= x < self.width and 0 <= y < self.height
		else:
			raise AttributeError(f'Map.valid with wrong attributes: {x_or_hex} / {y}')

	def points(self):
		point_arr = []

		for x in range(self.width):
			for y in range(self.height):
				point_arr.append(HexPoint(x, y))

		return point_arr

	def tileAt(self, x_or_hex, y=None):
		if isinstance(x_or_hex, HexPoint) and y is None:
			hex_point = x_or_hex
			return self.tiles.values[hex_point.y][hex_point.x]
		elif isinstance(x_or_hex, int) and isinstance(y, int):
			x = x_or_hex
			return self.tiles.values[y][x]
		else:
			raise AttributeError(f'Map.tileAt with wrong attributes: {x_or_hex} / {y}')

	def terrainAt(self, x_or_hex, y=None):
		if isinstance(x_or_hex, HexPoint) and y is None:
			hex_point = x_or_hex
			return self.tiles.values[hex_point.y][hex_point.x].terrain
		elif isinstance(x_or_hex, int) and isinstance(y, int):
			x = x_or_hex
			return self.tiles.values[y][x].terrain
		else:
			raise AttributeError(f'Map.terrainAt with wrong attributes: {x_or_hex} / {y}')

	def modifyTerrainAt(self, x_or_hex, y_or_terrain, terrain=None):
		if isinstance(x_or_hex, HexPoint) and isinstance(y_or_terrain, TerrainType) and terrain is None:
			hex_point = x_or_hex
			terrain_type = y_or_terrain
			self.tiles.values[hex_point.y][hex_point.x].terrain = terrain_type
		elif isinstance(x_or_hex, int) and isinstance(y_or_terrain, int) and isinstance(terrain, TerrainType):
			x = x_or_hex
			y = y_or_terrain
			terrain_type = terrain
			self.tiles.values[y][x].terrain = terrain_type
		else:
			raise AttributeError(f'Map.modifyTerrainAt with wrong attributes: {x_or_hex} / {y_or_terrain} / {terrain}')

	def isHillsAtt(self, x_or_hex, y=None):
		if isinstance(x_or_hex, HexPoint) and y is None:
			hex_point = x_or_hex
			return self.tiles.values[hex_point.y][hex_point.x].is_hills
		elif isinstance(x_or_hex, int) and isinstance(y, int):
			x = x_or_hex
			return self.tiles.values[y][x].is_hills
		else:
			raise AttributeError(f'Map.isHillsAtt with wrong attributes: {x_or_hex} / {y}')

	def modifyIsHillsAt(self, x_or_hex, y_or_is_hills, is_hills=None):
		if isinstance(x_or_hex, HexPoint) and isinstance(y_or_is_hills, bool) and is_hills is None:
			hex_point = x_or_hex
			is_hills = y_or_is_hills
			self.tiles.values[hex_point.y][hex_point.x].is_hills = is_hills
		elif isinstance(x_or_hex, int) and isinstance(y_or_is_hills, int) and isinstance(is_hills, bool):
			x = x_or_hex
			y = y_or_is_hills
			self.tiles.values[y][x].is_hills = is_hills
		else:
			raise AttributeError(
				f'Map.modifyIsHillsAt with wrong attributes: {x_or_hex} / {y_or_is_hills} / {is_hills}')

	def featureAt(self, x_or_hex, y=None):
		if isinstance(x_or_hex, HexPoint) and y is None:
			hex_point = x_or_hex
			return self.tiles.values[hex_point.y][hex_point.x].feature
		elif isinstance(x_or_hex, int) and isinstance(y, int):
			x = x_or_hex
			return self.tiles.values[y][x].feature
		else:
			raise AttributeError(f'Map.featureAt with wrong attributes: {x_or_hex} / {y}')

	def modifyFeatureAt(self, x_or_hex, y_or_terrain, feature=None):
		if isinstance(x_or_hex, HexPoint) and isinstance(y_or_terrain, FeatureType) and feature is None:
			hex_point = x_or_hex
			feature_type = y_or_terrain
			self.tiles.values[hex_point.y][hex_point.x].feature = feature_type
		elif isinstance(x_or_hex, int) and isinstance(y_or_terrain, int) and isinstance(feature, TerrainType):
			x = x_or_hex
			y = y_or_terrain
			feature_type = feature
			self.tiles.values[y][x].feature = feature_type
		else:
			raise AttributeError(f'Map.modifyTerrainAt with wrong attributes: {x_or_hex} / {y_or_terrain} / {feature}')

	def riverAt(self, x_or_hex, y=None):
		"""@return True, if this tile has a river - False otherwise"""
		if isinstance(x_or_hex, HexPoint) and y is None:
			hex_point = x_or_hex
			return self.tiles.values[hex_point.y][hex_point.x].river_value > 0
		elif isinstance(x_or_hex, int) and isinstance(y, int):
			x = x_or_hex
			return self.tiles.values[y][x].river_value > 0
		else:
			raise AttributeError(f'Map.riverAt with wrong attributes: {x_or_hex} / {y}')

	def tileStatistics(self, grid_point: HexPoint, radius: int):

		valid_tiles = 0.0
		stats = TileStatistics()

		for pt in grid_point.areaWith(radius):
			if not self.valid(pt):
				continue

			tile = self.tileAt(pt)

			if tile.terrain == TerrainType.ocean:
				stats.ocean += 1
			elif tile.terrain == TerrainType.shore:
				stats.shore += 1
			elif tile.terrain == TerrainType.plains:
				stats.plains += 1
			elif tile.terrain == TerrainType.grass:
				stats.grass += 1
			elif tile.terrain == TerrainType.desert:
				stats.desert += 1
			elif tile.terrain == TerrainType.tundra:
				stats.tundra += 1
			elif tile.terrain == TerrainType.snow:
				stats.snow += 1

			valid_tiles += 1.0

		# normalize
		stats.normalize(valid_tiles)

		return stats

	def canHaveFeature(self, grid_point: HexPoint, feature_type: FeatureType):
		tile = self.tileAt(grid_point)

		# check tile itself (no surroundings)
		if feature_type.isPossibleOn(tile):
			# additional check for flood plains
			if feature_type == FeatureType.floodplains:
				return self.riverAt(grid_point)

			#  no natural wonders on resources
			if feature_type.isNaturalWonder() and tile.hasAnyResourceFor(None):
				return False

			return True

		return False

	def to_dict(self):
		return {
			'width': self.width,
			'height': self.height,
			'tiles': self.tiles.to_dict()
		}
