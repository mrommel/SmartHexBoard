import unittest

from smarthexboard.smarthexboardlib.core.base import WeightedStringList
from smarthexboard.smarthexboardlib.game.ai.cities import WeightedFlavorList, WeightedYieldList, BuildableItemWeights, \
	BuildableType, BuildingWeights, DistrictWeights, UnitWeights, WonderWeights, BuildableItem, CityStrategyAdoptions, \
	CityStrategyType, CityStrategyAI
from smarthexboard.smarthexboardlib.game.baseTypes import HandicapType
from smarthexboard.smarthexboardlib.game.buildings import BuildingType
from smarthexboard.smarthexboardlib.game.cities import City
from smarthexboard.smarthexboardlib.game.civilizations import CivilizationType, WeightedCivilizationList, LeaderType
from smarthexboard.smarthexboardlib.game.districts import DistrictType
from smarthexboard.smarthexboardlib.game.flavors import FlavorType
from smarthexboard.smarthexboardlib.game.game import GameModel
from smarthexboard.smarthexboardlib.game.generation import UserInterfaceImpl
from smarthexboard.smarthexboardlib.game.playerMechanics import WeightedCivicList, WeightedTechList
from smarthexboard.smarthexboardlib.game.players import Player
from smarthexboard.smarthexboardlib.game.projects import ProjectType
from smarthexboard.smarthexboardlib.game.states.builds import BuildType
from smarthexboard.smarthexboardlib.game.states.victories import VictoryType
from smarthexboard.smarthexboardlib.game.types import CivicType, TechType
from smarthexboard.smarthexboardlib.game.unitTypes import UnitType
from smarthexboard.smarthexboardlib.game.wonders import WonderType
from smarthexboard.smarthexboardlib.map.base import HexPoint
from smarthexboard.smarthexboardlib.map.map import WeightedBuildList
from smarthexboard.smarthexboardlib.map.types import YieldType, TerrainType
from smarthexboard.tests.test_utils import MapModelMock


class TestWeightedList(unittest.TestCase):
	def helper(self, cls, types, extra):
		items = cls()
		for item in types:
			items.addWeight(0.5, item)

		items.addWeight(0.01, extra)

		top3Items = items.top3()
		itemsArray = top3Items.distributeByWeight()
		self.assertEqual(len(itemsArray), 100)

		for item in types:
			self.assertIn(item, itemsArray)

	def test_flavors(self):
		self.helper(
			WeightedFlavorList,
			[FlavorType.gold, FlavorType.production, FlavorType.growth],
			FlavorType.wonder
		)

	def test_yields(self):
		self.helper(
			WeightedYieldList,
			[YieldType.gold, YieldType.production, YieldType.food],
			YieldType.science
		)

	def test_civilizations(self):
		self.helper(
			WeightedCivilizationList,
			[CivilizationType.england, CivilizationType.greece, CivilizationType.rome],
			CivilizationType.barbarian
		)

	def test_civics(self):
		self.helper(
			WeightedCivicList,
			[CivicType.mysticism, CivicType.futureCivic, CivicType.naturalHistory],
			CivicType.earlyEmpire
		)

	def test_techs(self):
		self.helper(
			WeightedTechList,
			[TechType.pottery, TechType.steel, TechType.steamPower],
			TechType.archery
		)

	def test_buildables(self):
		self.helper(
			BuildableItemWeights,
			[BuildableType.unit, BuildableType.wonder, BuildableType.project],
			BuildableType.building
		)

	def test_buildings(self):
		self.helper(
			BuildingWeights,
			[BuildingType.palace, BuildingType.library, BuildingType.arena],
			BuildingType.waterMill
		)

	def test_districts(self):
		self.helper(
			DistrictWeights,
			[DistrictType.campus, DistrictType.cityCenter, DistrictType.harbor],
			DistrictType.encampment
		)

	def test_units(self):
		self.helper(
			UnitWeights,
			[UnitType.settler, UnitType.warrior, UnitType.archer],
			UnitType.trebuchet
		)

	def test_wonders(self):
		self.helper(
			WonderWeights,
			[WonderType.etemenanki, WonderType.colosseum, WonderType.colossus],
			WonderType.pyramids
		)

	def test_builds(self):
		self.helper(
			WeightedBuildList,
			[BuildType.removeMarsh, BuildType.removeRainforest, BuildType.pasture],
			BuildType.farm
		)

	def test_strings(self):
		self.helper(
			WeightedStringList,
			["abc", "def", "ghi"],
			"jiu"
		)


class TestBuildableItem(unittest.TestCase):
	def test_constructor(self):
		player = Player(LeaderType.trajan, human=True)
		player.initialize()

		item = BuildableItem(DistrictType.campus, HexPoint(2, 3))

		self.assertEqual(item.buildableType, BuildableType.district)
		self.assertEqual(item.districtType, DistrictType.campus)
		self.assertEqual(item.location, HexPoint(2, 3))
		self.assertEqual(item.productionLeftFor(player), 54.0)
		self.assertIsNotNone(item.__repr__())

		item = BuildableItem(BuildingType.monument)

		self.assertEqual(item.buildableType, BuildableType.building)
		self.assertEqual(item.buildingType, BuildingType.monument)
		self.assertIsNone(item.location)
		self.assertEqual(item.productionLeftFor(player), 60.0)
		self.assertIsNotNone(item.__repr__())

		item = BuildableItem(UnitType.warrior)

		self.assertEqual(item.buildableType, BuildableType.unit)
		self.assertEqual(item.unitType, UnitType.warrior)
		self.assertIsNone(item.location)
		self.assertEqual(item.productionLeftFor(player), 40.0)
		self.assertIsNotNone(item.__repr__())

		item = BuildableItem(WonderType.colosseum, HexPoint(2, 3))

		self.assertEqual(item.buildableType, BuildableType.wonder)
		self.assertEqual(item.wonderType, WonderType.colosseum)
		self.assertEqual(item.location, HexPoint(2, 3))
		self.assertEqual(item.productionLeftFor(player), 400.0)
		self.assertIsNotNone(item.__repr__())

		item = BuildableItem(ProjectType.none, HexPoint(2, 3))

		self.assertEqual(item.buildableType, BuildableType.project)
		self.assertEqual(item.projectType, ProjectType.none)
		self.assertEqual(item.location, HexPoint(2, 3))
		self.assertEqual(item.productionLeftFor(player), 0.0)
		self.assertIsNotNone(item.__repr__())


class TestCityStrategyAdoption(unittest.TestCase):
	def test_constructor(self):
		adoptions = CityStrategyAdoptions()

		for cityStrategyType in list(CityStrategyType):
			self.assertEqual(adoptions.adopted(cityStrategyType), False)
			self.assertEqual(adoptions.turnOfAdoption(cityStrategyType), -1)


class TestCityStrategyAI(unittest.TestCase):
	def test_constructor(self):
		# GIVEN
		mapModel = MapModelMock(24, 20, TerrainType.grass)
		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=mapModel
		)

		# add UI
		simulation.userInterface = UserInterfaceImpl()

		# players
		playerTrajan = Player(LeaderType.trajan, human=False)
		playerTrajan.initialize()
		simulation.players.append(playerTrajan)

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=playerTrajan)
		city.initialize(simulation)

		cityStrategy = CityStrategyAI(city)

		# WHEN
		cityStrategy.doTurn(simulation)

		# THEN
		self.assertIsNotNone(cityStrategy)
