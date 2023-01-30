""" unittest module """
import unittest

from smarthexboard.map.base import Size, Array2D, HexCube, HexPoint, HexDirection
from smarthexboard.map.generation import HeightMap, MapGenerator, MapOptions
from smarthexboard.map.map import Map, Tile
from smarthexboard.map.types import MapSize, MapType, MovementType, TerrainType, FeatureType
from smarthexboard.path_finding.finder import AStarPathfinder, MoveTypeIgnoreUnitsPathfinderDataSource, \
	MoveTypeIgnoreUnitsOptions


class TestArray2D(unittest.TestCase):
	def test_constructor(self):
		"""Test the Array2D constructor"""
		arr1 = Array2D(3, 4)
		self.assertEqual(arr1.width, 3)
		self.assertEqual(arr1.height, 4)


class TestHexPoint(unittest.TestCase):
	def test_constructor(self):
		"""Test the HexPoint constructor"""
		hex1 = HexPoint(27, 5)
		self.assertEqual(hex1.x, 27)
		self.assertEqual(hex1.y, 5)

		hex2 = HexPoint(HexCube(2, 1, 3))
		self.assertEqual(hex2.x, 4)
		self.assertEqual(hex2.y, 3)

		with self.assertRaises(AttributeError):
			_ = HexPoint(1, None)

	def test_neighbor_n_s(self):
		"""Test the HexPoint neighbor"""
		# north
		hex1 = HexPoint(27, 5)
		neighbor_n = hex1.neighbor(HexDirection.north, 1)

		self.assertEqual(neighbor_n, HexPoint(26, 4))
		self.assertEqual(neighbor_n.neighbor(HexDirection.south, 1), hex1)

	def test_neighbor_ne_sw(self):
		"""Test the HexPoint neighbor in north-east and south-west"""
		# north
		hex1 = HexPoint(27, 5)
		neighbor_ne = hex1.neighbor(HexDirection.northEast, 1)

		self.assertEqual(neighbor_ne, HexPoint(27, 4))
		self.assertEqual(neighbor_ne.neighbor(HexDirection.southWest, 1), hex1)

	def test_neighbors(self):
		"""Test the HexPoint neighbors"""
		expected = [HexPoint(26, 4), HexPoint(27, 4), HexPoint(28, 5), HexPoint(27, 6), HexPoint(26, 6), HexPoint(26, 5)]
		hex1 = HexPoint(27, 5)
		neighbors = hex1.neighbors()

		self.assertEqual(len(neighbors), 6)
		for index in range(6):
			self.assertEqual(neighbors[index], expected[index])

	def test_directionTowards(self):
		"""Test the HexPoint neighbors"""
		hex1 = HexPoint(27, 5)
		far_direction = hex1.directionTowards(HexPoint(10, 5))
		near_direction = hex1.directionTowards(HexPoint(28, 5))

		self.assertEqual(far_direction, HexDirection.northWest)
		self.assertEqual(near_direction, HexDirection.southEast)


class TestHeightMap(unittest.TestCase):
	def test_constructor(self):
		"""Test the HeightMap constructor"""
		height_map1 = HeightMap(3, 4)
		self.assertEqual(height_map1.width, 3)
		self.assertEqual(height_map1.height, 4)

	def test_findThresholdAbove(self):
		"""Test the HeightMap findThresholdAbove method"""
		height_map1 = HeightMap(3, 3)
		height_map1.values[0][0] = 0.1
		height_map1.values[0][1] = 0.2
		height_map1.values[0][2] = 0.3
		height_map1.values[1][0] = 0.4
		height_map1.values[1][1] = 0.5
		height_map1.values[1][2] = 0.6
		height_map1.values[2][0] = 0.7
		height_map1.values[2][1] = 0.8
		height_map1.values[2][2] = 0.9
		self.assertEqual(height_map1.findThresholdAbove(0.5), 0.5)


class TestTile(unittest.TestCase):
	def test_constructor(self):
		"""Test that the tile constructor versions work"""
		tile = Tile(HexPoint(3, 2), TerrainType.tundra)

		self.assertEqual(tile.point, HexPoint(3, 2))
		self.assertEqual(tile.point.x, 3)
		self.assertEqual(tile.point.y, 2)
		self.assertEqual(tile.terrain, TerrainType.tundra)

	def test_river_n(self):
		tile = Tile(HexPoint(3, 2), TerrainType.tundra)
		tile.river_value = 1

		self.assertEqual(tile.isRiverInNorth(), True)
		self.assertEqual(tile.isRiverInNorthEast(), False)
		self.assertEqual(tile.isRiverInSouthEast(), False)

	def test_river_ne(self):
		tile = Tile(HexPoint(3, 2), TerrainType.tundra)
		tile.river_value = 4

		self.assertEqual(tile.isRiverInNorth(), False)
		self.assertEqual(tile.isRiverInNorthEast(), True)
		self.assertEqual(tile.isRiverInSouthEast(), False)


class TestMap(unittest.TestCase):
	def test_constructor(self):
		"""Test that the map constructor versions work"""
		map1 = Map(3, 4)
		self.assertEqual(map1.width, 3)
		self.assertEqual(map1.height, 4)

		map2 = Map(Size(5, 2))
		self.assertEqual(map2.width, 5)
		self.assertEqual(map2.height, 2)

		with self.assertRaises(AttributeError):
			_ = Map(5.2, 1)


class TestMapGenerator(unittest.TestCase):

	def setUp(self):
		self.last_state_value = 0.0

	def test_constructor(self):
		"""Test the MapGenerator constructor"""
		def _callback(state):
			print(f'Progress: {state.value} - {state.message} ')
			self.last_state_value = state.value

		options = MapOptions(map_size=MapSize.duel, map_type=MapType.continents)
		generator = MapGenerator(options)

		grid = generator.generate(_callback)

		self.assertEqual(grid.width, 32)
		self.assertEqual(grid.height, 22)
		self.assertEqual(self.last_state_value, 1.0)


class TestPathfinding(unittest.TestCase):
	def test_generation_request(self):
		"""Test astar"""
		grid = Map(10, 10)
		for pt in grid.points():
			grid.modifyTerrainAt(pt, TerrainType.grass)

		grid.modifyFeatureAt(HexPoint(1, 2), FeatureType.mountains)  # put a mountain into the path

		datasource_options = MoveTypeIgnoreUnitsOptions(ignore_sight=False, can_embark=False, can_enter_ocean=False)
		datasource = MoveTypeIgnoreUnitsPathfinderDataSource(grid, MovementType.walk, datasource_options)
		finder = AStarPathfinder(datasource)

		path = finder.shortestPath(HexPoint(0, 0), HexPoint(2, 3))

		# print(path)
		target_path = [HexPoint(0, 0), HexPoint(1, 1), HexPoint(2, 1), HexPoint(2, 2), HexPoint(2, 3), ]
		self.assertEqual(len(path), 5)
		for i, n in enumerate(target_path):
			self.assertEqual(n, path[i])


if __name__ == '__main__':
	unittest.main()
