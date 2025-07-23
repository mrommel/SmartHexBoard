import os
from typing import Union, Optional

from smarthexboard.smarthexboardlib.map.base import HexPoint
from smarthexboard.smarthexboardlib.map.map import MapModel
from smarthexboard.smarthexboardlib.map.types import TerrainType, MapSize
from smarthexboard.smarthexboardlib.serialisation.map import MapModelSchema


class BetweenAssertMixin(object):
	def assertBetween(self, x, lo, hi):
		if not (lo <= x <= hi):
			raise AssertionError('%r not between %r and %r' % (x, lo, hi))


class MapModelMock(MapModel):
	def __init__(self, width_or_size: Union[int, MapSize], height_or_terrain: Optional[Union[int, TerrainType]] = None,
	             terrain: Optional[TerrainType] = None):

		if isinstance(width_or_size, int) and isinstance(height_or_terrain, int) and isinstance(terrain, TerrainType):
			width = width_or_size
			height = height_or_terrain
			super().__init__(width, height)

			for point in self.points():
				self.modifyTerrainAt(point, terrain)
		elif isinstance(width_or_size, MapSize) and isinstance(height_or_terrain, TerrainType):
			width = width_or_size.size().width()
			height = width_or_size.size().height()
			terrain = height_or_terrain
			super().__init__(width, height)

			for point in self.points():
				self.modifyTerrainAt(point, terrain)
		elif isinstance(width_or_size, MapModel):
			self.__dict__ = width_or_size.__dict__.copy()
		else:
			raise Exception('wrong combination of parameters')

	def discover(self, player, simulation):
		for point in self.points():
			self.tiles.values[point.y][point.x].discoverBy(player, simulation)

	def discoverRadius(self, player, pt: HexPoint, radius: int, simulation):
		for point in pt.areaWithRadius(radius):
			tile = self.tileAt(point)

			if tile is None:
				continue

			tile.discoverBy(player, simulation)

	@staticmethod
	def duelMap() -> 'MapModelMock':
		path = f'{os.getcwd()}/game/tests/files/duel.map'
		if os.path.exists(f'{os.getcwd()}/files/duel.map'):
			path = f'{os.getcwd()}/files/duel.map'

		if not os.path.exists(path):
			raise FileNotFoundError(f"Map file '{path}' does not exist.")

		with open(path, "r") as file:
			fileContent = file.read()

			obj_dict = MapModelSchema().loads(fileContent)
			return MapModelMock(MapModel(obj_dict))
