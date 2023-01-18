import json
from json import JSONEncoder

from smarthexboard.map.base import Array2D, Size
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
		self.isHills = False
		self.feature = FeatureType.none
		self.resource = ResourceType.none
		self.climate_zone = ClimateZone.temperate

	def to_dict(self):
		return {
			'terrain': self.terrain.value,
			'isHills': self.isHills,
			'feature': self.feature.value,
			'resource': self.resource.value
		}


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

		self.tiles = Array2D(self.width, self.height, Tile(TerrainType.ocean))

	def terrainAt(self, x_or_hex, y=None):
		if isinstance(x_or_hex, HexPoint) and y is None:
			hexPoint = x_or_hex
			return self.tiles[hexPoint.y][hexPoint.x]
		elif isinstance(x_or_hex, int) and isinstance(y, int):
			x = x_or_hex
			return self.tiles[y][x]

	def to_dict(self):
		return {
			'width': self.width,
			'height': self.height,
			'tiles': self.tiles.to_dict()
		}
