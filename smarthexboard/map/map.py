import json
from json import JSONEncoder

from smarthexboard.map.base import Array2D, Size, HexPoint
from smarthexboard.map.types import TerrainType, FeatureType, ResourceType, ClimateZone


class Tile:
	"""
		class that holds a single tile of a Map

		it has a TerrainType, FeatureType, ResourceType and a boolean value for being hilly (or not)
	"""
	def __init__(self, terrain: TerrainType):
		"""
			constructs a Tile from a TerrainType

			@param terrain: TerrainType
		"""
		self.terrain = terrain
		self.is_hills = False
		self.feature = FeatureType.none
		self.resource = ResourceType.none
		self.climate_zone = ClimateZone.temperate

	def to_dict(self):
		return {
			'terrain': self.terrain.value,
			'isHills': self.is_hills,
			'feature': self.feature.value,
			'resource': self.resource.value
		}

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
				self.tiles.values[y][x] = Tile(TerrainType.ocean)

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
			raise AttributeError(f'Map.modifyIsHillsAt with wrong attributes: {x_or_hex} / {y_or_is_hills} / {is_hills}')

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


	def tileStatistics(self, grid_point, radius):

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

	def to_dict(self):
		return {
			'width': self.width,
			'height': self.height,
			'tiles': self.tiles.to_dict()
		}
