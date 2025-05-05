""" unittest module """
import unittest
from pprint import pprint
from typing import Union, Optional

import smarthexboard
from smarthexboard.smarthexboardlib.game.cities import City
from smarthexboard.smarthexboardlib.game.generation import GameGenerator
from smarthexboard.smarthexboardlib.game.unitTypes import UnitMapType, UnitType
from smarthexboard.smarthexboardlib.game.units import Unit
from smarthexboard.smarthexboardlib.serialisation.game import GameModelSchema
from smarthexboard.smarthexboardlib.serialisation.map import CitySchema
from smarthexboard.utils import parseLocation, parseUnitMapType
from .smarthexboardlib.game.achievements import CivicAchievements
from .smarthexboardlib.game.baseTypes import HandicapType
from .smarthexboardlib.game.buildings import BuildingType
from .smarthexboardlib.game.civilizations import LeaderType
from .smarthexboardlib.game.game import GameModel
from .smarthexboardlib.game.players import Player
from .smarthexboardlib.game.states.victories import VictoryType
from .smarthexboardlib.game.types import CivicType, TechType
from .smarthexboardlib.map.base import Size, Array2D, HexCube, HexPoint, HexDirection
from .smarthexboardlib.map.generation import HeightMap, MapGenerator, MapOptions
from .smarthexboardlib.map.map import MapModel, Tile
from .smarthexboardlib.map.path_finding.finder import AStarPathfinder, MoveTypeIgnoreUnitsPathfinderDataSource, \
	MoveTypeIgnoreUnitsOptions
from .smarthexboardlib.map.types import UnitMovementType, TerrainType, FeatureType, MapSize, MapType


class MapModelMock:
	pass


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

		area1 = hex1.areaWithRadius(1)
		area2 = hex1.areaWithRadius(2)

		self.assertEqual(len(area1.points()), 7)  # 1 + 6
		self.assertEqual(len(area2.points()), 19)  # 1 + 6 + 12


class TestFeatureType(unittest.TestCase):
	def test_isPossibleOn(self):
		"""Test isPossibleOn"""
		tile = Tile(HexPoint(0, 0), TerrainType.grass)
		feature = FeatureType.none

		# cannot place FeatureType.none on any tile
		self.assertEqual(feature.isPossibleOn(tile), False)

		# forest
		feature = FeatureType.forest
		tile._terrainValue = TerrainType.ocean
		self.assertEqual(feature.isPossibleOn(tile), False)
		tile._terrainValue = TerrainType.snow
		self.assertEqual(feature.isPossibleOn(tile), False)
		tile._terrainValue = TerrainType.plains
		self.assertEqual(feature.isPossibleOn(tile), True)
		tile._terrainValue = TerrainType.grass
		self.assertEqual(feature.isPossibleOn(tile), True)

		# rainforest
		feature = FeatureType.rainforest
		tile._terrainValue = TerrainType.plains
		self.assertEqual(feature.isPossibleOn(tile), True)
		tile._terrainValue = TerrainType.grass
		self.assertEqual(feature.isPossibleOn(tile), False)

		# floodplains
		feature = FeatureType.floodplains
		tile._terrainValue = TerrainType.plains
		self.assertEqual(feature.isPossibleOn(tile), True)
		tile._terrainValue = TerrainType.grass
		self.assertEqual(feature.isPossibleOn(tile), True)

		# marsh
		feature = FeatureType.marsh
		tile._terrainValue = TerrainType.plains
		self.assertEqual(feature.isPossibleOn(tile), False)
		tile._terrainValue = TerrainType.grass
		self.assertEqual(feature.isPossibleOn(tile), True)

		# oasis
		feature = FeatureType.oasis
		tile._terrainValue = TerrainType.plains
		self.assertEqual(feature.isPossibleOn(tile), False)
		tile._terrainValue = TerrainType.grass
		self.assertEqual(feature.isPossibleOn(tile), False)
		tile._terrainValue = TerrainType.desert
		self.assertEqual(feature.isPossibleOn(tile), True)

		# reef
		feature = FeatureType.reef
		tile._terrainValue = TerrainType.ocean
		self.assertEqual(feature.isPossibleOn(tile), False)
		tile._terrainValue = TerrainType.shore
		self.assertEqual(feature.isPossibleOn(tile), True)
		tile._terrainValue = TerrainType.plains
		self.assertEqual(feature.isPossibleOn(tile), False)

		# ice
		feature = FeatureType.ice
		tile._terrainValue = TerrainType.snow
		self.assertEqual(feature.isPossibleOn(tile), False)
		tile._terrainValue = TerrainType.shore
		self.assertEqual(feature.isPossibleOn(tile), True)
		tile._terrainValue = TerrainType.plains
		self.assertEqual(feature.isPossibleOn(tile), False)

		# atoll
		feature = FeatureType.atoll
		tile._terrainValue = TerrainType.ocean
		self.assertEqual(feature.isPossibleOn(tile), True)
		tile._terrainValue = TerrainType.shore
		self.assertEqual(feature.isPossibleOn(tile), True)
		tile._terrainValue = TerrainType.plains
		self.assertEqual(feature.isPossibleOn(tile), False)

		# volcano
		feature = FeatureType.volcano
		tile._terrainValue = TerrainType.ocean
		self.assertEqual(feature.isPossibleOn(tile), False)
		tile._terrainValue = TerrainType.grass
		self.assertEqual(feature.isPossibleOn(tile), False)
		tile._terrainValue = TerrainType.plains
		self.assertEqual(feature.isPossibleOn(tile), False)
		tile._terrainValue = TerrainType.tundra
		self.assertEqual(feature.isPossibleOn(tile), False)

		# mountains
		feature = FeatureType.mountains
		tile._terrainValue = TerrainType.ocean
		self.assertEqual(feature.isPossibleOn(tile), False)
		tile._terrainValue = TerrainType.desert
		self.assertEqual(feature.isPossibleOn(tile), True)
		tile._terrainValue = TerrainType.plains
		self.assertEqual(feature.isPossibleOn(tile), True)

		# lake
		feature = FeatureType.lake
		tile._terrainValue = TerrainType.grass
		self.assertEqual(feature.isPossibleOn(tile), True)
		tile._terrainValue = TerrainType.desert
		self.assertEqual(feature.isPossibleOn(tile), True)
		tile._terrainValue = TerrainType.plains
		self.assertEqual(feature.isPossibleOn(tile), True)

		# fallout
		feature = FeatureType.fallout
		tile._terrainValue = TerrainType.ocean
		self.assertEqual(feature.isPossibleOn(tile), False)
		tile._terrainValue = TerrainType.desert
		self.assertEqual(feature.isPossibleOn(tile), True)
		tile._terrainValue = TerrainType.plains
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
		self.assertEqual(tile.terrain(), TerrainType.tundra)

	def test_river_n(self):
		tile = Tile(HexPoint(3, 2), TerrainType.tundra)
		tile._riverValue = 1

		self.assertEqual(tile.isRiverInNorth(), True)
		self.assertEqual(tile.isRiverInNorthEast(), False)
		self.assertEqual(tile.isRiverInSouthEast(), False)

	def test_river_ne(self):
		tile = Tile(HexPoint(3, 2), TerrainType.tundra)
		tile._riverValue = 4

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

		self.assertEqual(grass_tile.movementCost(UnitMovementType.walk, tundra_tile), 1)
		self.assertEqual(mountains_tile.movementCost(UnitMovementType.walk, tundra_tile), 1)
		self.assertEqual(ocean_tile.movementCost(UnitMovementType.walk, tundra_tile), UnitMovementType.max.value)


class TestMap(unittest.TestCase):
	def test_constructor(self):
		"""Test that the map constructor versions work"""
		map1 = MapModel(3, 4)
		self.assertEqual(map1.width, 3)
		self.assertEqual(map1.height, 4)

		map2 = MapModel(Size(5, 2))
		self.assertEqual(map2.width, 5)
		self.assertEqual(map2.height, 2)

		with self.assertRaises(AttributeError):
			_ = MapModel(5.2, 1)

	def test_valid(self):
		"""Test that a point is on the map (or not)"""
		map1 = MapModel(3, 4)

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
		map1 = MapModel(2, 2)
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

		# map db values to
		mapSize: MapSize = MapSize.duel
		mapType: MapType = MapType.continents
		leader: LeaderType = LeaderType.alexander

		options = MapOptions(mapSize=mapSize, mapType=mapType, leader=leader)
		generator = MapGenerator(options)

		grid = generator.generate(_callback)

		self.assertEqual(grid.width, 32)
		self.assertEqual(grid.height, 22)
		self.assertEqual(self.last_state_value, 1.0)


class TestPathfinding(unittest.TestCase):
	def test_path_finding(self):
		"""Test the astar algorithm"""
		grid = MapModelMock(10, 10, TerrainType.grass)
		grid.modifyFeatureAt(HexPoint(1, 2), FeatureType.mountains)  # put a mountain into the path

		player = Player(LeaderType.alexander, human=False)
		simulation = GameModel(
			victoryTypes=[VictoryType.science],
			handicap=HandicapType.settler,
			turnsElapsed=0,
			players=[player],
			map=grid
		)

		grid.discover(player, simulation)

		datasource_options = MoveTypeIgnoreUnitsOptions(ignore_sight=True, can_embark=False, can_enter_ocean=False)
		datasource = MoveTypeIgnoreUnitsPathfinderDataSource(grid, UnitMovementType.walk, player, datasource_options)
		finder = AStarPathfinder(datasource)

		path = finder.shortestPath(HexPoint(0, 0), HexPoint(2, 3))

		# print(path)
		self.assertIsNotNone(path)
		target_path = [HexPoint(0, 0), HexPoint(1, 1), HexPoint(2, 1), HexPoint(2, 2), HexPoint(2, 3), ]
		self.assertEqual(len(path.points()), 5)
		for i, n in enumerate(target_path):
			self.assertEqual(n, path.points()[i])


class TestAssets(unittest.TestCase):
	def test_techs_data(self):
		for tech in list(TechType):
			_ = tech.name()

	def test_civics_data(self):
		for civic in list(CivicType):
			_ = civic.name()

	def test_civics_envoys(self):
		# https://civilization.fandom.com/wiki/Envoy_(Civ6)
		# The following civics grant free Envoy Envoys upon discovery: Mysticism, Military Training, Theology,
		# Naval Tradition, Mercenaries, Colonialism, Opera and Ballet, Natural History, Scorched Earth, Conservation,
		# Capitalism, Nuclear Program, and Cultural Heritage (and, in Gathering Storm, Near Future Governance and
		# Global Warming Mitigation). The civics between Mercenaries and Conservation grant +2, while Conservation and
		# all others afterward grant +3.
		civics_with_envoys = [
			CivicType.mysticism, CivicType.militaryTradition, CivicType.theology, CivicType.navalTradition,
			CivicType.mercenaries, CivicType.colonialism, CivicType.operaAndBallet, CivicType.naturalHistory,
			CivicType.scorchedEarth, CivicType.conservation, CivicType.capitalism, CivicType.nuclearProgram,
			CivicType.culturalHeritage, CivicType.nearFutureGovernance, CivicType.globalWarmingMitigation
		]

		for civic_with_envoys in civics_with_envoys:
			self.assertGreater(civic_with_envoys.envoys(), 0, f'envoys of {civic_with_envoys} should be greater than zero')

	def test_civics_governors(self):
		# Civic Tree - There are a total of 13 civics that will grant 1 Governor Title. They are State Workforce,
		# Early Empire, Defensive Tactics, Recorded History, Medieval Faires, Guilds, Civil Engineering, Nationalism,
		# Mass Media, Mobilization, Globalization, Social Media, and Near Future Governance. Advancing through the
		# civic tree is the most basic and most common way of acquiring Governor Titles.
		civics_with_governors = [
			CivicType.stateWorkforce, CivicType.earlyEmpire, CivicType.defensiveTactics, CivicType.recordedHistory,
			CivicType.medievalFaires, CivicType.guilds, CivicType.civilEngineering, CivicType.nationalism,
			CivicType.massMedia, CivicType.mobilization, CivicType.globalization, CivicType.socialMedia,
			CivicType.nearFutureGovernance
		]

		for civic_with_governors in civics_with_governors:
			self.assertTrue(civic_with_governors.hasGovernorTitle(), f'envoys of {civic_with_governors} should be True')

	def test_civic_achievements(self):
		achievements = CivicAchievements(CivicType.gamesAndRecreation)

		self.assertIn(BuildingType.arena, achievements.buildingTypes)


class TestSerialization(unittest.TestCase):
	def test_serialize_game(self):
		def callbackFunc(state):
			print(f'Progress: {state.value} - {state.message}')

		options = MapOptions(mapSize=MapSize.duel, mapType=MapType.continents, leader=LeaderType.alexander)
		generator = MapGenerator(options)

		mapModel = generator.generate(callbackFunc)

		gameGenerator = GameGenerator()
		gameModel = gameGenerator.generate(mapModel, HandicapType.settler)

		json_dict = GameModelSchema().dump(gameModel)
		self.assertEqual(json_dict['currentTurn'], 0)
		map_json_dict = json_dict['mapModel']
		self.assertEqual(map_json_dict['width'], 32)
		self.assertEqual(map_json_dict['height'], 22)
		self.assertGreater(len(map_json_dict['units']), 0)

	def test_serialize_and_restore_game(self):
		def callbackFunc(state):
			pass

		options = MapOptions(mapSize=MapSize.duel, mapType=MapType.continents, leader=LeaderType.alexander)
		generator = MapGenerator(options)

		mapModel = generator.generate(callbackFunc)

		gameGenerator = GameGenerator()
		gameModel = gameGenerator.generate(mapModel, HandicapType.settler)

		alexander = gameModel.playerFor(LeaderType.alexander)
		gameModel.addUnit(Unit(location=HexPoint(1, 2), unitType=UnitType.warrior, player=alexander))
		berlin = City(name='Berlin', location=HexPoint(1, 2), player=alexander, isCapital=True)
		gameModel.addCity(berlin)

		# berlin_result = CitySchema().dump(berlin)
		# pprint(berlin_result, indent=2)
		# restored_berlin = CitySchema().load(berlin_result)
		# print(restored_berlin.player)

		json_str = GameModelSchema().dump(gameModel)
		# print(json_str)
		restoredGame = GameModelSchema().load(json_str)
		#
		# self.assertEqual(gameModel.playerFor(LeaderType.alexander).name(), restoredGame.playerFor(LeaderType.alexander).name())


class TestRequestParsing(unittest.TestCase):
	def test_parseLocation(self):
		self.assertEqual(parseLocation('2,2'), HexPoint(2, 2))
		self.assertEqual(parseLocation(',32'), None)
		self.assertEqual(parseLocation(''), None)
		self.assertEqual(parseLocation(','), None)
		self.assertEqual(parseLocation('-32'), None)

	def test_parseUnitMapType(self):
		self.assertEqual(parseUnitMapType('combat'), UnitMapType.combat)
		self.assertEqual(parseUnitMapType('civilian'), UnitMapType.civilian)
		self.assertEqual(parseUnitMapType('None'), None)


if __name__ == '__main__':
	unittest.main()
