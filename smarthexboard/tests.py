""" unittest module """
import unittest

from smarthexboard.map.base import Size, Array2D, HexCube, HexPoint
from smarthexboard.map.generation import HeightMap
from smarthexboard.map.map import Map


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


if __name__ == '__main__':
	unittest.main()
