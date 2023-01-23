""" unittest module """
import json
import unittest
import uuid

from smarthexboard.map.base import Size, Array2D, HexCube, HexPoint, HexDirection
from smarthexboard.map.generation import HeightMap, MapGenerator, MapOptions, MapGeneratorState
from smarthexboard.map.map import Map
from django.test import Client

from smarthexboard.map.types import MapSize, MapType
from smarthexboard.utils import is_valid_uuid


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
		"""Test the HexPoint neighbor"""
		# north
		hex1 = HexPoint(27, 5)
		neighbor_ne = hex1.neighbor(HexDirection.northEast, 1)
		self.assertEqual(neighbor_ne, HexPoint(27, 4))
		self.assertEqual(neighbor_ne.neighbor(HexDirection.southWest, 1), hex1)


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


class TestMapGenerationRequest(unittest.TestCase):
	def test_generation_request(self):
		"""Test that the map generation request (async)"""
		client = Client()
		response = client.post('/smarthexboard/generate_map')
		self.assertEqual(response.status_code, 201)

		json_object = json.loads(response.content)
		map_uuid = json_object['uuid']
		self.assertEqual(is_valid_uuid(map_uuid), True)

if __name__ == '__main__':
	unittest.main()
