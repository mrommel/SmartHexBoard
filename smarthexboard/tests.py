""" unittest module """
import unittest
import uuid

import pytest

from smarthexboard.game.types import TechType
from smarthexboard.map.base import Size, Array2D, HexCube, HexPoint, HexDirection
from smarthexboard.map.generation import HeightMap, MapGenerator, MapOptions
from smarthexboard.map.map import Map, Tile
from smarthexboard.map.types import MovementType, TerrainType, FeatureType
from smarthexboard.models import HandicapType, LeaderType, Player, GameModel, MapModel, PlayerTech, MapSize, MapType
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
		expected = [
			HexPoint(26, 4),
			HexPoint(27, 4),
			HexPoint(28, 5),
			HexPoint(27, 6),
			HexPoint(26, 6),
			HexPoint(26, 5)
		]
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

	def test_distance(self):
		"""Test the HexPoint distance"""
		hex1 = HexPoint(3, 2)
		hex2 = HexPoint(5, 4)
		hex3 = HexPoint(17, 5)

		self.assertEqual(hex1.distance(hex1), 0)
		self.assertEqual(hex1.distance(hex2), 3)
		self.assertEqual(hex2.distance(hex1), 3)
		self.assertEqual(hex1.distance(hex3), 15)
		self.assertEqual(hex3.distance(hex1), 15)
		self.assertEqual(hex2.distance(hex3), 12)
		self.assertEqual(hex3.distance(hex2), 12)

	def test_areaWith(self):
		"""Test the HexPoint areaWith"""
		hex1 = HexPoint(3, 2)

		area1 = hex1.areaWith(1)
		area2 = hex1.areaWith(2)

		self.assertEqual(len(area1.points), 7)  # 1 + 6
		self.assertEqual(len(area2.points), 19)  # 1 + 6 + 12


class TestFeatureType(unittest.TestCase):
	def test_isPossibleOn(self):
		"""Test isPossibleOn"""
		tile = Tile(HexPoint(0, 0), TerrainType.grass)
		feature = FeatureType.none

		# cannot place FeatureType.none on any tile
		self.assertEqual(feature.isPossibleOn(tile), False)

		# forest
		feature = FeatureType.forest
		tile.terrain = TerrainType.ocean
		self.assertEqual(feature.isPossibleOn(tile), False)
		tile.terrain = TerrainType.snow
		self.assertEqual(feature.isPossibleOn(tile), False)
		tile.terrain = TerrainType.plains
		self.assertEqual(feature.isPossibleOn(tile), True)
		tile.terrain = TerrainType.grass
		self.assertEqual(feature.isPossibleOn(tile), True)

		# rainforest
		feature = FeatureType.rainforest
		tile.terrain = TerrainType.plains
		self.assertEqual(feature.isPossibleOn(tile), True)
		tile.terrain = TerrainType.grass
		self.assertEqual(feature.isPossibleOn(tile), False)

		# floodplains
		feature = FeatureType.floodplains
		tile.terrain = TerrainType.plains
		self.assertEqual(feature.isPossibleOn(tile), True)
		tile.terrain = TerrainType.grass
		self.assertEqual(feature.isPossibleOn(tile), True)

		# marsh
		feature = FeatureType.marsh
		tile.terrain = TerrainType.plains
		self.assertEqual(feature.isPossibleOn(tile), False)
		tile.terrain = TerrainType.grass
		self.assertEqual(feature.isPossibleOn(tile), True)

		# oasis
		feature = FeatureType.oasis
		tile.terrain = TerrainType.plains
		self.assertEqual(feature.isPossibleOn(tile), False)
		tile.terrain = TerrainType.grass
		self.assertEqual(feature.isPossibleOn(tile), False)
		tile.terrain = TerrainType.desert
		self.assertEqual(feature.isPossibleOn(tile), True)

		# reef
		feature = FeatureType.reef
		tile.terrain = TerrainType.ocean
		self.assertEqual(feature.isPossibleOn(tile), False)
		tile.terrain = TerrainType.shore
		self.assertEqual(feature.isPossibleOn(tile), True)
		tile.terrain = TerrainType.plains
		self.assertEqual(feature.isPossibleOn(tile), False)

		# ice
		feature = FeatureType.ice
		tile.terrain = TerrainType.snow
		self.assertEqual(feature.isPossibleOn(tile), False)
		tile.terrain = TerrainType.shore
		self.assertEqual(feature.isPossibleOn(tile), True)
		tile.terrain = TerrainType.plains
		self.assertEqual(feature.isPossibleOn(tile), False)

		# atoll
		feature = FeatureType.atoll
		tile.terrain = TerrainType.ocean
		self.assertEqual(feature.isPossibleOn(tile), True)
		tile.terrain = TerrainType.shore
		self.assertEqual(feature.isPossibleOn(tile), True)
		tile.terrain = TerrainType.plains
		self.assertEqual(feature.isPossibleOn(tile), False)

		# volcano
		feature = FeatureType.volcano
		tile.terrain = TerrainType.ocean
		self.assertEqual(feature.isPossibleOn(tile), False)
		tile.terrain = TerrainType.grass
		self.assertEqual(feature.isPossibleOn(tile), False)
		tile.terrain = TerrainType.plains
		self.assertEqual(feature.isPossibleOn(tile), False)
		tile.terrain = TerrainType.tundra
		self.assertEqual(feature.isPossibleOn(tile), False)

		# mountains
		feature = FeatureType.mountains
		tile.terrain = TerrainType.ocean
		self.assertEqual(feature.isPossibleOn(tile), False)
		tile.terrain = TerrainType.desert
		self.assertEqual(feature.isPossibleOn(tile), True)
		tile.terrain = TerrainType.plains
		self.assertEqual(feature.isPossibleOn(tile), True)

		# lake
		feature = FeatureType.lake
		tile.terrain = TerrainType.grass
		self.assertEqual(feature.isPossibleOn(tile), True)
		tile.terrain = TerrainType.desert
		self.assertEqual(feature.isPossibleOn(tile), True)
		tile.terrain = TerrainType.plains
		self.assertEqual(feature.isPossibleOn(tile), True)

		# fallout
		feature = FeatureType.fallout
		tile.terrain = TerrainType.ocean
		self.assertEqual(feature.isPossibleOn(tile), False)
		tile.terrain = TerrainType.desert
		self.assertEqual(feature.isPossibleOn(tile), True)
		tile.terrain = TerrainType.plains
		self.assertEqual(feature.isPossibleOn(tile), True)


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

	def test_isWater(self):
		tile = Tile(HexPoint(3, 2), TerrainType.tundra)

		self.assertEqual(tile.isWater(), False)

	def test_isLand(self):
		tile = Tile(HexPoint(3, 2), TerrainType.tundra)

		self.assertEqual(tile.isLand(), True)

	def test_movementCost(self):
		tundra_tile = Tile(HexPoint(3, 2), TerrainType.tundra)

		grass_tile = Tile(HexPoint(3, 1), TerrainType.grass)
		mountains_tile = Tile(HexPoint(3, 1), TerrainType.grass)
		mountains_tile.feature = FeatureType.mountains
		ocean_tile = Tile(HexPoint(3, 1), TerrainType.shore)

		self.assertEqual(grass_tile.movementCost(MovementType.walk, tundra_tile), 1)
		self.assertEqual(mountains_tile.movementCost(MovementType.walk, tundra_tile), 3)
		self.assertEqual(ocean_tile.movementCost(MovementType.walk, tundra_tile), MovementType.max)


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

	def test_valid(self):
		"""Test that a point is on the map (or not)"""
		map1 = Map(3, 4)

		self.assertEqual(map1.valid(2, 3), True)
		self.assertEqual(map1.valid(HexPoint(2, 3)), True)

		self.assertEqual(map1.valid(-1, 3), False)
		self.assertEqual(map1.valid(HexPoint(-1, 3)), False)

	def test_points(self):
		"""Test that points returns all map points"""
		expected = [
			HexPoint(0, 0),
			HexPoint(0, 1),
			HexPoint(1, 0),
			HexPoint(1, 1),
		]
		map1 = Map(2, 2)
		map_points = map1.points()

		self.assertEqual(len(map_points), 4)
		for index in range(4):
			self.assertEqual(map_points[index], expected[index])


class TestMapGenerator(unittest.TestCase):

	def setUp(self):
		self.last_state_value = 0.0

	def test_constructor(self):
		"""Test the MapGenerator constructor"""

		def _callback(state):
			print(f'Progress: {state.value} - {state.message} ')
			self.last_state_value = state.value

		options = MapOptions(map_size=MapSize.DUEL, map_type=MapType.CONTINENTS)
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


class TestGame(unittest.TestCase):
	@pytest.mark.django_db
	def test_game_creation(self):
		"""Test game"""
		map_model = MapModel(uuid=uuid.uuid4(), content='')
		map_model.save()
		game = GameModel(uuid=uuid.uuid4(), map=map_model, name='Test game', turn=0, handicap=HandicapType.SETTLER)
		game.save()

		player1 = Player(leader=LeaderType.ALEXANDER, game=game)
		player1.save()
		player2 = Player(leader=LeaderType.TRAJAN, game=game)
		player2.save()

		players = game.players()
		self.assertEqual(len(players), 2)
		self.assertEqual(players[0], player1)
		self.assertEqual(players[1], player2)

	@pytest.mark.django_db
	def test_game_tech(self):
		map_model = MapModel(uuid=uuid.uuid4(), content='')
		map_model.save()
		game_model = GameModel(uuid=uuid.uuid4(), map=map_model, name='Test game', turn=0, handicap=HandicapType.SETTLER)
		game_model.save()

		player1 = Player(leader=LeaderType.ALEXANDER, game=game_model)
		player1.save()

		player1Tech1 = PlayerTech(player=player1, tech_identifier='pottery', progress=25, eureka=False)
		player1Tech1.save()

		player1Tech2 = PlayerTech(player=player1, tech_identifier='irrigation', progress=20, eureka=False)
		player1Tech2.save()

		canResearchPottery = player1.canResearch(TechType.pottery)
		self.assertEqual(canResearchPottery, False)

		canResearchIrrigation = player1.canResearch(TechType.irrigation)
		self.assertEqual(canResearchIrrigation, True)


if __name__ == '__main__':
	unittest.main()
