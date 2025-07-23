""" unittest module """
import logging
import unittest

from smarthexboard.smarthexboardlib.game.baseTypes import HandicapType
from smarthexboard.smarthexboardlib.game.civilizations import LeaderType
from smarthexboard.smarthexboardlib.game.game import GameModel
from smarthexboard.smarthexboardlib.game.generation import UserInterfaceImpl
from smarthexboard.smarthexboardlib.game.players import Player
from smarthexboard.smarthexboardlib.game.states.builds import BuildType
from smarthexboard.smarthexboardlib.game.states.victories import VictoryType
from smarthexboard.smarthexboardlib.game.types import TechType, CivicType
from smarthexboard.smarthexboardlib.game.unitTypes import UnitType
from smarthexboard.smarthexboardlib.game.units import Unit
from smarthexboard.smarthexboardlib.map.areas import Continent
from smarthexboard.smarthexboardlib.map.base import Array2D, HexDirection, HexPoint, HexCube, HexArea, BoundingBox, Size
from smarthexboard.smarthexboardlib.map.generation import HeightMap, MapOptions, MapGenerator
from smarthexboard.smarthexboardlib.map.improvements import ImprovementType
from smarthexboard.smarthexboardlib.map.map import Tile, FlowDirection, MapModel, River
from smarthexboard.smarthexboardlib.map.path_finding.finder import AStarPathfinder, MoveTypeIgnoreUnitsOptions, \
	MoveTypeIgnoreUnitsPathfinderDataSource
from smarthexboard.smarthexboardlib.map.path_finding.path import HexPath
from smarthexboard.smarthexboardlib.map.types import MapSize, MapType, TerrainType, FeatureType, ResourceType, \
	UnitMovementType, AppealLevel
from smarthexboard.tests.test_utils import MapModelMock


class TestMapAssets(unittest.TestCase):
	def test_mapSize_data(self):
		for mapSize in list(MapSize):
			_ = mapSize.title()

	def test_mapType_data(self):
		for mapType in list(MapType):
			_ = mapType.title()

	def test_terrain_data(self):
		for terrain in list(TerrainType):
			_ = terrain.title()
			_ = terrain.textures()

	def test_feature_data(self):
		for feature in list(FeatureType):
			_ = feature.title()
			_ = feature.textures()

	def test_resource_data(self):
		for resource in list(ResourceType):
			_ = resource.title()
			_ = resource.texture()


class TestArray2D(unittest.TestCase):
	def test_constructor(self):
		"""Test the Array2D constructor"""
		arr1 = Array2D(3, 4)
		self.assertEqual(arr1.width, 3)
		self.assertEqual(arr1.height, 4)


class TestHexDirection(unittest.TestCase):
	def test_constructor(self):
		"""Test the HexDirection constructor"""
		direction = HexDirection.north
		self.assertEqual(direction.value, 'north')
		self.assertEqual(direction.name, 'north')

		direction = HexDirection.southEast
		self.assertEqual(direction.value, 'southEast')
		self.assertEqual(direction.name, 'southEast')

		with self.assertRaises(ValueError):
			_ = HexDirection(10)

	def test_opposite(self):
		"""Test the HexDirection opposite method"""
		self.assertEqual(HexDirection.north.opposite(), HexDirection.south)
		self.assertEqual(HexDirection.south.opposite(), HexDirection.north)
		self.assertEqual(HexDirection.northEast.opposite(), HexDirection.southWest)
		self.assertEqual(HexDirection.southWest.opposite(), HexDirection.northEast)
		self.assertEqual(HexDirection.southEast.opposite(), HexDirection.northWest)
		self.assertEqual(HexDirection.northWest.opposite(), HexDirection.southEast)

	def test_clockwiseNeighbor(self):
		"""Test the HexDirection clockwise method"""
		self.assertEqual(HexDirection.north.clockwiseNeighbor(), HexDirection.northEast)
		self.assertEqual(HexDirection.northEast.clockwiseNeighbor(), HexDirection.southEast)
		self.assertEqual(HexDirection.southEast.clockwiseNeighbor(), HexDirection.south)
		self.assertEqual(HexDirection.south.clockwiseNeighbor(), HexDirection.southWest)
		self.assertEqual(HexDirection.southWest.clockwiseNeighbor(), HexDirection.northWest)
		self.assertEqual(HexDirection.northWest.clockwiseNeighbor(), HexDirection.north)


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

		self.assertEqual(len(area1._points), 7)  # 1 + 6
		self.assertEqual(len(area2._points), 19)  # 1 + 6 + 12


class TestHexPath(unittest.TestCase):
	def test_constructor(self):
		# GIVEN
		path = HexPath([HexPoint(0, 0), HexPoint(0, 1)], [0.0, 1.0])

		# THEN
		self.assertEqual(len(path._points), 2)
		self.assertEqual(len(path._costs), 2)

	def test_firstSegments(self):
		# GIVEN
		path = HexPath([HexPoint(0, 0), HexPoint(0, 1), HexPoint(0, 2), HexPoint(0, 3)], [0.0, 1.0, 1.0, 1.0])

		# WHEN
		seg = path.firstSegments(2)

		# THEN
		self.assertEqual(len(seg._points), 2)
		self.assertEqual(len(seg._costs), 2)
		self.assertEqual(seg.points()[0], HexPoint(0, 0))
		self.assertEqual(seg.points()[1], HexPoint(0, 1))


class TestImprovementType(unittest.TestCase):
	def test_farm_yields(self):
		player = Player(LeaderType.trajan, human=False)
		player.initialize()

		farmYields = ImprovementType.farm.yieldsFor(player)
		self.assertEqual(farmYields.food, 1)
		self.assertEqual(farmYields.production, 0)
		self.assertEqual(farmYields.gold, 0)

		tile = Tile(HexPoint(0, 0), TerrainType.grass)
		tile.setOwner(player)
		self.assertEqual(ImprovementType.farm.isPossibleOn(tile), True)

	def test_mine_yields(self):
		mapModel = MapModelMock(10, 10, TerrainType.ocean)
		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=mapModel
		)

		player = Player(LeaderType.trajan, human=False)
		player.initialize()
		player.techs.discover(TechType.mining, simulation)

		mineYields = ImprovementType.mine.yieldsFor(player)
		self.assertEqual(mineYields.food, 0)
		self.assertEqual(mineYields.production, 1)
		self.assertEqual(mineYields.gold, 0)

		tile = Tile(HexPoint(0, 0), TerrainType.grass)
		self.assertEqual(ImprovementType.mine.isPossibleOn(tile), False)

		tile.setOwner(player)
		self.assertEqual(ImprovementType.mine.isPossibleOn(tile), False)

		tile.setResource(ResourceType.iron)
		self.assertEqual(ImprovementType.mine.isPossibleOn(tile), True)

		tile.setResource(ResourceType.none)
		tile.setHills(True)
		self.assertEqual(ImprovementType.mine.isPossibleOn(tile), True)

	def test_pasture_yields(self):
		mapModel = MapModelMock(10, 10, TerrainType.ocean)
		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=mapModel
		)

		player = Player(LeaderType.trajan, human=False)
		player.initialize()
		player.techs.discover(TechType.animalHusbandry, simulation)

		pastureYields = ImprovementType.pasture.yieldsFor(player)
		self.assertEqual(pastureYields.food, 0)
		self.assertEqual(pastureYields.production, 1)
		self.assertEqual(pastureYields.gold, 0)

		player.techs.discover(TechType.stirrups, simulation)
		pastureYields = ImprovementType.pasture.yieldsFor(player)
		self.assertEqual(pastureYields.food, 1)
		self.assertEqual(pastureYields.production, 1)
		self.assertEqual(pastureYields.gold, 0)

		player.techs.discover(TechType.robotics, simulation)
		pastureYields = ImprovementType.pasture.yieldsFor(player)
		self.assertEqual(pastureYields.food, 2)
		self.assertEqual(pastureYields.production, 2)
		self.assertEqual(pastureYields.gold, 0)

		player.techs.discover(TechType.replaceableParts, simulation)
		pastureYields = ImprovementType.pasture.yieldsFor(player)
		self.assertEqual(pastureYields.food, 2)
		self.assertEqual(pastureYields.production, 3)
		self.assertEqual(pastureYields.gold, 0)

		tile = Tile(HexPoint(0, 0), TerrainType.grass)
		self.assertEqual(ImprovementType.pasture.isPossibleOn(tile), False)

		tile.setOwner(player)
		self.assertEqual(ImprovementType.pasture.isPossibleOn(tile), False)

		tile.setResource(ResourceType.cattle)
		self.assertEqual(ImprovementType.pasture.isPossibleOn(tile), True)

	def test_plantation_yields(self):
		mapModel = MapModelMock(10, 10, TerrainType.ocean)
		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=mapModel
		)

		player = Player(LeaderType.trajan, human=False)
		player.initialize()
		player.techs.discover(TechType.irrigation, simulation)

		plantationYields = ImprovementType.plantation.yieldsFor(player)
		self.assertEqual(plantationYields.food, 0)
		self.assertEqual(plantationYields.production, 0)
		self.assertEqual(plantationYields.gold, 2)

		tile = Tile(HexPoint(0, 0), TerrainType.grass)
		tile.setOwner(player)
		self.assertEqual(ImprovementType.plantation.isPossibleOn(tile), False)

		tile.setResource(ResourceType.citrus)
		self.assertEqual(ImprovementType.plantation.isPossibleOn(tile), True)

	def test_fishingBoats_yields(self):
		mapModel = MapModelMock(10, 10, TerrainType.ocean)
		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=mapModel
		)

		player = Player(LeaderType.trajan, human=False)
		player.initialize()
		player.techs.discover(TechType.sailing, simulation)

		fishingBoatsYields = ImprovementType.fishingBoats.yieldsFor(player)
		self.assertEqual(fishingBoatsYields.food, 1)
		self.assertEqual(fishingBoatsYields.production, 0)
		self.assertEqual(fishingBoatsYields.gold, 0)

		tile = Tile(HexPoint(0, 0), TerrainType.grass)
		tile.setOwner(player)
		self.assertEqual(ImprovementType.fishingBoats.isPossibleOn(tile), False)

		tile.setResource(ResourceType.whales)
		self.assertEqual(ImprovementType.fishingBoats.isPossibleOn(tile), True)

	def test_camp_yields(self):
		mapModel = MapModelMock(10, 10, TerrainType.ocean)
		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=mapModel
		)

		player = Player(LeaderType.trajan, human=False)
		player.initialize()
		player.techs.discover(TechType.animalHusbandry, simulation)

		campYields = ImprovementType.camp.yieldsFor(player)
		self.assertEqual(campYields.food, 0)
		self.assertEqual(campYields.production, 0)
		self.assertEqual(campYields.gold, 1)

		tile = Tile(HexPoint(0, 0), TerrainType.grass)
		tile.setOwner(player)
		self.assertEqual(ImprovementType.camp.isPossibleOn(tile), False)

		tile.setResource(ResourceType.furs)
		self.assertEqual(ImprovementType.camp.isPossibleOn(tile), True)


class TestFeatureType(unittest.TestCase):
	def test_isPossibleOn(self):
		"""Test isPossibleOn"""
		tile = Tile(HexPoint(0, 0), TerrainType.grass)
		feature = FeatureType.none

		# cannot place FeatureType.none on any tile
		self.assertEqual(feature.isPossibleOn(tile), False)

		# forest
		feature = FeatureType.forest
		tile.setTerrain(TerrainType.ocean)
		self.assertEqual(feature.isPossibleOn(tile), False)
		tile.setTerrain(TerrainType.snow)
		self.assertEqual(feature.isPossibleOn(tile), False)
		tile.setTerrain(TerrainType.plains)
		self.assertEqual(feature.isPossibleOn(tile), True)
		tile.setTerrain(TerrainType.grass)
		self.assertEqual(feature.isPossibleOn(tile), True)

		# rainforest
		feature = FeatureType.rainforest
		tile.setTerrain(TerrainType.plains)
		self.assertEqual(feature.isPossibleOn(tile), True)
		tile.setTerrain(TerrainType.grass)
		self.assertEqual(feature.isPossibleOn(tile), False)

		# floodplains
		feature = FeatureType.floodplains
		tile.setTerrain(TerrainType.plains)
		self.assertEqual(feature.isPossibleOn(tile), True)
		tile.setTerrain(TerrainType.grass)
		self.assertEqual(feature.isPossibleOn(tile), True)

		# marsh
		feature = FeatureType.marsh
		tile.setTerrain(TerrainType.plains)
		self.assertEqual(feature.isPossibleOn(tile), False)
		tile.setTerrain(TerrainType.grass)
		self.assertEqual(feature.isPossibleOn(tile), True)

		# oasis
		feature = FeatureType.oasis
		tile.setTerrain(TerrainType.plains)
		self.assertEqual(feature.isPossibleOn(tile), False)
		tile.setTerrain(TerrainType.grass)
		self.assertEqual(feature.isPossibleOn(tile), False)
		tile.setTerrain(TerrainType.desert)
		self.assertEqual(feature.isPossibleOn(tile), True)

		# reef
		feature = FeatureType.reef
		tile.setTerrain(TerrainType.ocean)
		self.assertEqual(feature.isPossibleOn(tile), False)
		tile.setTerrain(TerrainType.shore)
		self.assertEqual(feature.isPossibleOn(tile), True)
		tile.setTerrain(TerrainType.plains)
		self.assertEqual(feature.isPossibleOn(tile), False)

		# ice
		feature = FeatureType.ice
		tile.setTerrain(TerrainType.snow)
		self.assertEqual(feature.isPossibleOn(tile), False)
		tile.setTerrain(TerrainType.shore)
		self.assertEqual(feature.isPossibleOn(tile), True)
		tile.setTerrain(TerrainType.plains)
		self.assertEqual(feature.isPossibleOn(tile), False)

		# atoll
		feature = FeatureType.atoll
		tile.setTerrain(TerrainType.ocean)
		self.assertEqual(feature.isPossibleOn(tile), True)
		tile.setTerrain(TerrainType.shore)
		self.assertEqual(feature.isPossibleOn(tile), True)
		tile.setTerrain(TerrainType.plains)
		self.assertEqual(feature.isPossibleOn(tile), False)

		# volcano
		feature = FeatureType.volcano
		tile.setTerrain(TerrainType.ocean)
		self.assertEqual(feature.isPossibleOn(tile), False)
		tile.setTerrain(TerrainType.grass)
		self.assertEqual(feature.isPossibleOn(tile), False)
		tile.setTerrain(TerrainType.plains)
		self.assertEqual(feature.isPossibleOn(tile), False)
		tile.setTerrain(TerrainType.tundra)
		self.assertEqual(feature.isPossibleOn(tile), False)

		# mountains
		feature = FeatureType.mountains
		tile.setTerrain(TerrainType.ocean)
		self.assertEqual(feature.isPossibleOn(tile), False)
		tile.setTerrain(TerrainType.desert)
		self.assertEqual(feature.isPossibleOn(tile), True)
		tile.setTerrain(TerrainType.plains)
		self.assertEqual(feature.isPossibleOn(tile), True)

		# lake
		feature = FeatureType.lake
		tile.setTerrain(TerrainType.grass)
		self.assertEqual(feature.isPossibleOn(tile), True)
		tile.setTerrain(TerrainType.desert)
		self.assertEqual(feature.isPossibleOn(tile), True)
		tile.setTerrain(TerrainType.plains)
		self.assertEqual(feature.isPossibleOn(tile), True)

		# fallout
		feature = FeatureType.fallout
		tile.setTerrain(TerrainType.ocean)
		self.assertEqual(feature.isPossibleOn(tile), False)
		tile.setTerrain(TerrainType.desert)
		self.assertEqual(feature.isPossibleOn(tile), True)
		tile.setTerrain(TerrainType.plains)
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
	def setUp(self):
		Tile.resetRiverCache()

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
		tile.setRiverFlowInNorthEast(FlowDirection.northWest)

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
		mountains_tile.setFeature(FeatureType.mountains)
		ocean_tile = Tile(HexPoint(3, 1), TerrainType.shore)
		naturalWonder_tile = Tile(HexPoint(3, 1), TerrainType.grass)
		naturalWonder_tile.setFeature(FeatureType.mountKilimanjaro)

		self.assertEqual(grass_tile.movementCost(UnitMovementType.walk, tundra_tile), 1)
		self.assertEqual(mountains_tile.movementCost(UnitMovementType.walk, tundra_tile), 3)
		self.assertEqual(ocean_tile.movementCost(UnitMovementType.walk, tundra_tile), UnitMovementType.max.value)
		self.assertEqual(naturalWonder_tile.movementCost(UnitMovementType.walk, tundra_tile), UnitMovementType.max.value)

	def test_isImpassable(self):
		naturalWonder_tile = Tile(HexPoint(3, 1), TerrainType.grass)
		naturalWonder_tile.setFeature(FeatureType.mountKilimanjaro)

		self.assertEqual(naturalWonder_tile.isImpassable(UnitMovementType.walk), True)

	def test_resource_visibility(self):
		tile = Tile(HexPoint(3, 1), TerrainType.grass)
		tile._resourceValue = ResourceType.oil

		mapModel = MapModelMock(10, 10, TerrainType.ocean)

		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=mapModel
		)
		simulation.userInterface = UserInterfaceImpl()

		player = Player(LeaderType.trajan, human=False)
		player.initialize()

		self.assertEqual(tile.resourceFor(player), ResourceType.none)

		player.techs.discover(TechType.refining, simulation)

		self.assertEqual(tile.resourceFor(player), ResourceType.oil)

		tile._resourceValue = ResourceType.antiquitySite

		self.assertEqual(tile.resourceFor(player), ResourceType.none)

		player.civics.discover(CivicType.naturalHistory, simulation)

		self.assertEqual(tile.resourceFor(player), ResourceType.antiquitySite)

	def test_improvement_getset(self):
		tile = Tile(HexPoint(3, 2), TerrainType.grass)

		self.assertEqual(tile.improvement(), ImprovementType.none)  # initial

		tile.setImprovement(ImprovementType.farm)
		self.assertEqual(tile.improvement(), ImprovementType.farm)
		self.assertEqual(tile.hasAnyImprovement(), True)

		tile.removeImprovement()
		self.assertEqual(tile.improvement(), ImprovementType.none)
		self.assertEqual(tile.hasAnyImprovement(), False)

	def test_improvement_pillage(self):
		tile = Tile(HexPoint(3, 2), TerrainType.tundra)

		self.assertEqual(tile.isImprovementPillaged(), False)  # initial

		tile.setImprovementPillaged(True)
		self.assertEqual(tile.isImprovementPillaged(), True)

		tile.setImprovementPillaged(False)
		self.assertEqual(tile.isImprovementPillaged(), False)

	def test_seeThroughLevel(self):
		tile = Tile(HexPoint(3, 2), TerrainType.tundra)
		self.assertEqual(tile.seeThroughLevel(), 0)

		tile.setHills(True)
		self.assertEqual(tile.seeThroughLevel(), 1)

		tile.setFeature(FeatureType.mountains)
		self.assertEqual(tile.seeThroughLevel(), 4)

		tile.setHills(False)
		self.assertEqual(tile.seeThroughLevel(), 3)

		tile.setFeature(FeatureType.forest)
		self.assertEqual(tile.seeThroughLevel(), 1)

		tile.setHills(True)
		self.assertEqual(tile.seeThroughLevel(), 2)

	def test_productionFromFeatureRemoval(self):
		tile = Tile(HexPoint(3, 2), TerrainType.tundra)
		tile.setFeature(FeatureType.forest)

		self.assertEqual(tile.productionFromFeatureRemoval(BuildType.removeForest), 20)

		tile = Tile(HexPoint(3, 2), TerrainType.grass)
		tile.setFeature(FeatureType.forest)

		self.assertEqual(tile.productionFromFeatureRemoval(BuildType.farm), 20)

		tile = Tile(HexPoint(3, 2), TerrainType.grass)
		tile.setFeature(FeatureType.forest)

		self.assertEqual(tile.productionFromFeatureRemoval(BuildType.removeRoad), 0)

	def test_eurekas(self):
		mapModel = MapModelMock(10, 10, TerrainType.ocean)

		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=mapModel
		)
		simulation.userInterface = UserInterfaceImpl()

		player = Player(LeaderType.trajan, human=False)
		player.initialize()
		player.techs.discover(TechType.mining, simulation)  # for the mine check - to reveal iron
		player.techs.discover(TechType.pottery, simulation)  # for the farm check - to reveal wheat
		player.techs.discover(TechType.animalHusbandry, simulation)  # for the pasture check - to reveal horses

		tile = Tile(HexPoint(3, 2), TerrainType.grass)

		# Masonry - To Boost: Build a quarry
		self.assertEqual(player.techs.eurekaTriggeredFor(TechType.masonry), False)
		tile.updateEurekas(ImprovementType.quarry, player, simulation)
		self.assertEqual(player.techs.eurekaTriggeredFor(TechType.masonry), True)

		# Wheel - To Boost: Mine a resource
		self.assertEqual(player.techs.eurekaTriggeredFor(TechType.wheel), False)
		tile.setResource(ResourceType.copper)
		tile.updateEurekas(ImprovementType.mine, player, simulation)
		self.assertEqual(player.techs.eurekaTriggeredFor(TechType.wheel), True)

		# Irrigation - To Boost: Farm a resource
		self.assertEqual(player.techs.eurekaTriggeredFor(TechType.irrigation), False)
		tile.setResource(ResourceType.wheat)
		tile.updateEurekas(ImprovementType.farm, player, simulation)
		self.assertEqual(player.techs.eurekaTriggeredFor(TechType.irrigation), True)

		# Horseback Riding - To Boost: Build a pasture
		self.assertEqual(player.techs.eurekaTriggeredFor(TechType.horsebackRiding), False)
		tile.setResource(ResourceType.horses)
		tile.updateEurekas(ImprovementType.pasture, player, simulation)
		self.assertEqual(player.techs.eurekaTriggeredFor(TechType.horsebackRiding), True)

		# Iron Working - To Boost: Build an Iron Mine
		self.assertEqual(player.techs.eurekaTriggeredFor(TechType.ironWorking), False)
		tile.setResource(ResourceType.iron)
		tile.updateEurekas(ImprovementType.mine, player, simulation)
		self.assertEqual(player.techs.eurekaTriggeredFor(TechType.ironWorking), True)

		# Apprenticeship - To Boost: Build 3 mines

		# Ballistics - To Boost: Build 2 Forts

		# Rifling - To Boost: Build a Niter Mine

	def test_continent(self):
		tile0 = Tile(HexPoint(1, 1), TerrainType.grass)
		tile0.continentIdentifier = 'abc'

		tile1 = Tile(HexPoint(1, 2), TerrainType.desert)
		tile1.continentIdentifier = 'abc'

		tile2 = Tile(HexPoint(1, 3), TerrainType.ocean)
		tile2.continentIdentifier = 'def'

		self.assertEqual(tile0.sameContinentAs(tile1), True)
		self.assertEqual(tile0.continentIdentifier, tile1.continentIdentifier)

		self.assertEqual(tile0.sameContinentAs(tile2), False)
		self.assertNotEqual(tile0.continentIdentifier, tile2.continentIdentifier)


class TestBoundingBox(unittest.TestCase):
	def test_constructor(self):
		boundingBox = BoundingBox([HexPoint(1, 1), HexPoint(2, 2), HexPoint(3, 3)])
		self.assertEqual(boundingBox.width(), 2)
		self.assertEqual(boundingBox.height(), 2)


class TestHexArea(unittest.TestCase):
	def test_constructor(self):
		area0 = HexArea([HexPoint(1, 1), HexPoint(2, 2), HexPoint(3, 3)])
		self.assertEqual(area0._points, [HexPoint(1, 1), HexPoint(2, 2), HexPoint(3, 3)])

		area1 = HexArea(HexPoint(1, 1))
		self.assertEqual(area1._points, [HexPoint(1, 1)])

		area2 = HexArea(HexPoint(1, 1), radius=1)
		self.assertEqual(area2._points, [HexPoint(0, 0), HexPoint(0, 1), HexPoint(0, 2), HexPoint(2, 1), HexPoint(1, 0), HexPoint(1, 1), HexPoint(1, 2)])

	def test_center(self):
		area = HexArea([HexPoint(1, 1), HexPoint(2, 2), HexPoint(3, 3)])
		self.assertEqual(area.center(), HexPoint(2, 2))

	def test_boundingBox(self):
		area0 = HexArea([HexPoint(1, 1), HexPoint(1, 2)])
		boundingBox0 = area0.boundingBox()
		expectedBoundingBox = BoundingBox()
		expectedBoundingBox.minX = 1
		expectedBoundingBox.minY = 1
		expectedBoundingBox.maxX = 1
		expectedBoundingBox.maxY = 2
		self.assertEqual(boundingBox0, expectedBoundingBox)


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

	def test_tileAt(self):
		mapModel = MapModelMock(4, 6, TerrainType.ocean)

		for x in range(4):
			for y in range(6):
				tile = mapModel.tileAt(x, y)
				self.assertEqual(tile.terrain(), TerrainType.ocean)

				tile = mapModel.tileAt(HexPoint(x, y))
				self.assertEqual(tile.terrain(), TerrainType.ocean)

	def test_average_tile_appeal(self):
		# GIVEN
		mapModel = MapModelMock(10, 10, TerrainType.ocean)

		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=mapModel
		)
		simulation.userInterface = UserInterfaceImpl()

		tile = mapModel.tileAt(HexPoint(3, 3))

		# WHEN
		appeal = tile.appeal(simulation)
		appealLevel = tile.appealLevel(simulation)

		# GIVEN
		self.assertEqual(appeal, 0)
		self.assertEqual(appealLevel, AppealLevel.average)

	def test_breathtaking_appeal(self):
		# GIVEN
		mapModel = MapModelMock(10, 10, TerrainType.ocean)

		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=mapModel
		)
		simulation.userInterface = UserInterfaceImpl()

		tile = mapModel.tileAt(HexPoint(3, 3))
		tile.setFeature(FeatureType.mountains)

		# WHEN
		appeal = tile.appeal(simulation)
		appealLevel = tile.appealLevel(simulation)

		# GIVEN
		self.assertEqual(appeal, 4)
		self.assertEqual(appealLevel, AppealLevel.breathtaking)

	def test_breathtaking_appeal2(self):
		# GIVEN
		mapModel = MapModelMock(10, 10, TerrainType.ocean)

		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=mapModel
		)
		simulation.userInterface = UserInterfaceImpl()

		tile = mapModel.tileAt(HexPoint(3, 3))
		tile.setFeature(FeatureType.mountKilimanjaro)

		# WHEN
		appeal = tile.appeal(simulation)
		appealLevel = tile.appealLevel(simulation)

		# GIVEN
		self.assertEqual(appeal, 5)
		self.assertEqual(appealLevel, AppealLevel.breathtaking)

	def test_discovery(self):
		# GIVEN
		mapModel = MapModelMock(10, 10, TerrainType.ocean)
		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=mapModel
		)

		player = Player(LeaderType.trajan, human=True)
		player.initialize()

		tile = mapModel.tileAt(HexPoint(3, 1))

		# WHEN
		discoveredBefore = tile.isDiscoveredBy(player)
		tile.discoverBy(player, simulation)
		discoveredAfter = tile.isDiscoveredBy(player)
		# tile.sightBy(player)

		# THEN
		self.assertEqual(discoveredBefore, False)
		self.assertEqual(discoveredAfter, True)

	def test_sight(self):
		# GIVEN
		mapModel = MapModelMock(10, 10, TerrainType.ocean)

		player = Player(LeaderType.trajan, human=True)
		player.initialize()

		tile = mapModel.tileAt(HexPoint(3, 1))

		# WHEN
		discoveredBefore = tile.isVisibleTo(player)
		tile.sightBy(player)
		discoveredAfter = tile.isVisibleTo(player)

		# THEN
		self.assertEqual(discoveredBefore, False)
		self.assertEqual(discoveredAfter, True)

	def test_isRiverToCrossTowards_ns(self):
		# GIVEN
		mapModel = MapModelMock(10, 10, TerrainType.ocean)

		tileNorth = mapModel.tileAt(HexPoint(3, 1))
		tileSouth = mapModel.tileAt(HexPoint(3, 2))

		# WHEN
		riverNorthSouthBefore = tileNorth.isRiverToCrossTowards(tileSouth)
		riverSouthNorthBefore = tileSouth.isRiverToCrossTowards(tileNorth)
		tileSouth.setRiver(River('Spree'), FlowDirection.west)
		riverNorthSouthAfter = tileNorth.isRiverToCrossTowards(tileSouth)
		riverSouthNorthAfter = tileSouth.isRiverToCrossTowards(tileNorth)

		# THEN
		self.assertEqual(riverNorthSouthBefore, False)
		self.assertEqual(riverSouthNorthBefore, False)
		self.assertEqual(riverNorthSouthAfter, True)
		self.assertEqual(riverSouthNorthAfter, True)

	def test_continents(self):
		# GIVEN
		mapModel = MapModelMock(10, 10, TerrainType.grass)

		continent = Continent(12, 'Europe', mapModel)
		mapModel.continents.append(continent)

		# WHEN
		continentBefore = mapModel.continentAt(HexPoint(2, 2))
		mapModel.setContinent(continent, HexPoint(2, 2))
		continentAfter = mapModel.continentAt(HexPoint(2, 2))

		# THEN
		self.assertIsNone(continentBefore)
		self.assertEqual(continentAfter, continent)

	def test_tile(self):
		# GIVEN
		mapModel = MapModelMock(10, 10, TerrainType.grass)

		tile0terrain = mapModel.tileAt(HexPoint(0, 0)).terrain()
		tile1terrain = mapModel.tileAt(1, 1).terrain()

		# WHEN
		mapModel.modifyTerrainAt(HexPoint(0, 0), TerrainType.ocean)
		mapModel.modifyTerrainAt(1, 1, TerrainType.desert)

		# THEN
		self.assertEqual(tile0terrain, TerrainType.grass)
		self.assertEqual(mapModel.tileAt(HexPoint(0, 0)).terrain(), TerrainType.ocean)
		self.assertEqual(tile1terrain, TerrainType.grass)
		self.assertEqual(mapModel.tileAt(1, 1).terrain(), TerrainType.desert)

	def test_modifyTerrain(self):
		# GIVEN
		mapModel = MapModelMock(10, 10, TerrainType.grass)

		terrain0before = mapModel.terrainAt(HexPoint(0, 0))
		terrain1before = mapModel.terrainAt(1, 1)

		# WHEN
		mapModel.modifyTerrainAt(HexPoint(0, 0), TerrainType.ocean)
		mapModel.modifyTerrainAt(1, 1, TerrainType.desert)

		# THEN
		self.assertEqual(terrain0before, TerrainType.grass)
		self.assertEqual(mapModel.terrainAt(HexPoint(0, 0)), TerrainType.ocean)
		self.assertEqual(terrain1before, TerrainType.grass)
		self.assertEqual(mapModel.terrainAt(1, 1), TerrainType.desert)

	def test_modifyHills(self):
		# GIVEN
		mapModel = MapModelMock(10, 10, TerrainType.grass)

		hills0before = mapModel.isHillsAt(HexPoint(0, 0))
		hills1before = mapModel.isHillsAt(1, 1)

		# WHEN
		mapModel.modifyIsHillsAt(HexPoint(0, 0), True)
		mapModel.modifyIsHillsAt(1, 1, True)

		# THEN
		self.assertEqual(hills0before, False)
		self.assertEqual(mapModel.isHillsAt(HexPoint(0, 0)), True)
		self.assertEqual(hills1before, False)
		self.assertEqual(mapModel.isHillsAt(1, 1), True)


class TestMapGenerator(unittest.TestCase):

	def setUp(self):
		self.last_state_value = 0.0

	def test_constructor(self):
		"""Test the MapGenerator constructor"""

		def _callback(state):
			logging.debug(f'Progress: {state.value} - {state.message} ')
			self.last_state_value = state.value

		options = MapOptions(mapSize=MapSize.duel, mapType=MapType.continents, leader=LeaderType.trajan)
		generator = MapGenerator(options)

		grid = generator.generate(_callback)

		self.assertEqual(grid.width, 32)
		self.assertEqual(grid.height, 22)
		self.assertEqual(self.last_state_value, 1.0)


class TestPathfinding(unittest.TestCase):
	def test_path(self):
		path = HexPath([HexPoint(1, 1), HexPoint(2, 1), HexPoint(2, 2)])
		self.assertEqual(path, path)
		self.assertEqual(path.firstIndexOf(HexPoint(2, 1)), 1)

		reversePath = HexPath([HexPoint(2, 2), HexPoint(2, 1), HexPoint(1, 1)])
		self.assertEqual(path.reversed(), reversePath)

		path.append(HexPoint(2, 3), 2.0)
		extendedPath = HexPath([HexPoint(1, 1), HexPoint(2, 1), HexPoint(2, 2), HexPoint(2, 3)])
		self.assertEqual(path, extendedPath)

	def test_generation_request(self):
		"""Test astar"""
		grid = MapModel(10, 10)
		for pt in grid.points():
			grid.modifyTerrainAt(pt, TerrainType.grass)

		player = Player(leader=LeaderType.trajan, human=True)

		grid.modifyFeatureAt(HexPoint(1, 2), FeatureType.mountains)  # put a mountain into the path

		datasource_options = MoveTypeIgnoreUnitsOptions(ignore_sight=True, can_embark=False, can_enter_ocean=False)
		datasource = MoveTypeIgnoreUnitsPathfinderDataSource(grid, UnitMovementType.walk, player, datasource_options)
		finder = AStarPathfinder(datasource)

		path = finder.shortestPath(HexPoint(0, 0), HexPoint(2, 3))

		# logging.debug(path)
		target_path = [HexPoint(0, 0), HexPoint(1, 1), HexPoint(2, 1), HexPoint(2, 2), HexPoint(2, 3), ]
		self.assertEqual(len(path.points()), 5)
		for i, n in enumerate(target_path):
			self.assertEqual(n, path.points()[i])

	def test_turnsToReachTarget(self):
		# GIVEN
		mapModel = MapModelMock(10, 10, TerrainType.grass)
		mapModel.modifyFeatureAt(HexPoint(1, 2), FeatureType.mountains)  # put a mountain into the path

		player = Player(leader=LeaderType.trajan, human=True)
		player.initialize()

		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[player],
			map=mapModel
		)

		playerScout = Unit(HexPoint(5, 5), UnitType.scout, player)
		simulation.addUnit(playerScout)

		datasource_options = MoveTypeIgnoreUnitsOptions(ignore_sight=True, can_embark=False, can_enter_ocean=False)
		datasource = MoveTypeIgnoreUnitsPathfinderDataSource(mapModel, UnitMovementType.walk, player, datasource_options)
		finder = AStarPathfinder(datasource)

		# WHEN
		turns: int = finder.turnsToReachTarget(playerScout, HexPoint(2, 3), simulation)
		exist: bool = finder.doesPathExist(HexPoint(5, 5), HexPoint(2, 3))

		# THEN
		self.assertAlmostEqual(turns, 1)
		self.assertEqual(exist, True)

	def test_unitMovement(self):
		# GIVEN
		mapModel = MapModelMock(10, 10, TerrainType.shore)
		mapModel.modifyTerrainAt(HexPoint(1, 1), TerrainType.grass)
		mapModel.modifyTerrainAt(HexPoint(1, 2), TerrainType.grass)
		mapModel.modifyTerrainAt(HexPoint(2, 2), TerrainType.grass)

		player = Player(leader=LeaderType.trajan, human=True)
		player.initialize()

		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[player],
			map=mapModel
		)

		playerSettler = Unit(HexPoint(1, 1), UnitType.settler, player)
		simulation.addUnit(playerSettler)

		# WHEN
		path = playerSettler.pathTowards(HexPoint(2, 2), [], simulation)

		# THEN
		self.assertIsNotNone(path)
		self.assertEqual(len(path.points()), 3)
		self.assertEqual(path.points(), [HexPoint(1, 1), HexPoint(1, 2), HexPoint(2, 2)])

	def test_unitMovementDifferentBlockingUnitType(self):
		# GIVEN
		mapModel = MapModelMock(10, 10, TerrainType.shore)
		mapModel.modifyTerrainAt(HexPoint(1, 1), TerrainType.grass)
		mapModel.modifyTerrainAt(HexPoint(1, 2), TerrainType.grass)
		mapModel.modifyTerrainAt(HexPoint(2, 2), TerrainType.grass)

		player = Player(leader=LeaderType.trajan, human=True)
		player.initialize()

		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[player],
			map=mapModel
		)

		playerSettler = Unit(HexPoint(1, 1), UnitType.settler, player)
		simulation.addUnit(playerSettler)

		playerWarrior = Unit(HexPoint(1, 2), UnitType.warrior, player)
		simulation.addUnit(playerWarrior)

		# WHEN
		path = playerSettler.pathTowards(HexPoint(2, 2), [], simulation)

		# THEN
		self.assertIsNotNone(path)
		self.assertEqual(len(path.points()), 3)
		self.assertEqual(path.points(), [HexPoint(1, 1), HexPoint(1, 2), HexPoint(2, 2)])

	def test_unitMovementSameBlockingUnitType(self):
		# GIVEN
		mapModel = MapModelMock(10, 10, TerrainType.shore)
		mapModel.modifyTerrainAt(HexPoint(1, 1), TerrainType.grass)
		mapModel.modifyTerrainAt(HexPoint(1, 2), TerrainType.grass)
		mapModel.modifyTerrainAt(HexPoint(2, 2), TerrainType.grass)

		player = Player(leader=LeaderType.trajan, human=True)
		player.initialize()

		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[player],
			map=mapModel
		)

		playerSettler = Unit(HexPoint(1, 1), UnitType.settler, player)
		simulation.addUnit(playerSettler)

		playerBuilder = Unit(HexPoint(1, 2), UnitType.builder, player)
		simulation.addUnit(playerBuilder)

		# WHEN
		path = playerSettler.pathTowards(HexPoint(2, 2), [], simulation)

		# THEN
		self.assertIsNone(path)

	def test_blockingUnit(self):
		# GIVEN
		mapModel = MapModelMock(10, 10, TerrainType.shore)
		mapModel.modifyTerrainAt(HexPoint(1, 1), TerrainType.grass)
		mapModel.modifyTerrainAt(HexPoint(1, 2), TerrainType.grass)
		mapModel.modifyTerrainAt(HexPoint(2, 2), TerrainType.grass)

		player = Player(leader=LeaderType.trajan, human=True)
		player.initialize()

		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[player],
			map=mapModel
		)

		playerSettler = Unit(HexPoint(1, 1), UnitType.settler, player)
		simulation.addUnit(playerSettler)

		# blocking unit of same type
		playerBuilder = Unit(HexPoint(1, 2), UnitType.builder, player)
		simulation.addUnit(playerBuilder)

		datasource = simulation.unitAwarePathfinderDataSource(playerSettler)

		# WHEN
		coords = datasource.walkableAdjacentTilesCoords(HexPoint(1, 1))

		# THEN
		self.assertEqual(coords, [])
