import os
import unittest

import django

from smarthexboard.smarthexboardlib.game.ai.cities import BuildableType, CitySpecializationType
from smarthexboard.smarthexboardlib.game.baseTypes import HandicapType
from smarthexboard.smarthexboardlib.game.buildings import BuildingType
from smarthexboard.smarthexboardlib.game.cities import City
from smarthexboard.smarthexboardlib.game.cityStates import CityStateType
from smarthexboard.smarthexboardlib.game.civilizations import LeaderType
from smarthexboard.smarthexboardlib.game.districts import DistrictType
from smarthexboard.smarthexboardlib.game.game import GameModel
from smarthexboard.smarthexboardlib.game.generation import UserInterfaceImpl
from smarthexboard.smarthexboardlib.game.governments import GovernmentType
from smarthexboard.smarthexboardlib.game.players import Player
from smarthexboard.smarthexboardlib.game.religions import PantheonType
from smarthexboard.smarthexboardlib.game.states.builds import BuildType
from smarthexboard.smarthexboardlib.game.states.victories import VictoryType
from smarthexboard.smarthexboardlib.game.types import TechType, CivicType
from smarthexboard.smarthexboardlib.game.unitTypes import UnitType
from smarthexboard.smarthexboardlib.game.units import Unit
from smarthexboard.smarthexboardlib.game.wonders import WonderType
from smarthexboard.smarthexboardlib.map.base import HexPoint
from smarthexboard.smarthexboardlib.map.improvements import ImprovementType
from smarthexboard.smarthexboardlib.map.map import MapModel, Tile
from smarthexboard.smarthexboardlib.map.types import TerrainType, FeatureType, ResourceType
from smarthexboard.tests.test_utils import MapModelMock

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()


class TestCityProduction(unittest.TestCase):
	def setUp(self) -> None:
		self.mapModel = MapModelMock(24, 20, TerrainType.grass)
		self.simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=self.mapModel
		)

		# add UI
		self.simulation.userInterface = UserInterfaceImpl()

		# players
		self.playerTrajan = Player(LeaderType.trajan, human=False)
		self.playerTrajan.initialize()
		self.simulation.players.append(self.playerTrajan)

	def test_chooseProduction(self):
		# GIVEN

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.simulation)

		# WHEN
		city.doProduction(allowNoProduction=False, simulation=self.simulation)

		# THEN
		self.assertIsNotNone(city.currentBuildableItem())
		self.assertIn(city.currentBuildableItem().buildableType, [BuildableType.building, BuildableType.unit])

		if city.currentBuildableItem().buildableType == BuildableType.building:
			self.assertEqual(city.currentBuildableItem().buildingType, BuildingType.monument)
		elif city.currentBuildableItem().buildableType == BuildableType.unit:
			self.assertIn(city.currentBuildableItem().unitType, [UnitType.warrior, UnitType.builder, UnitType.scout, UnitType.slinger])

	def test_building_monument(self):
		# GIVEN

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.simulation)

		# WHEN
		buildingBefore = city._buildQueue.isCurrentlyBuildingBuilding(BuildingType.monument)
		city.startBuildingBuilding(BuildingType.monument)
		buildingAfter = city._buildQueue.isCurrentlyBuildingBuilding(BuildingType.monument)

		# THEN
		self.assertEqual(buildingBefore, False)
		self.assertEqual(buildingAfter, True)


class TestCityDistricts(unittest.TestCase):
	def setUp(self) -> None:
		self.mapModel = MapModelMock(24, 20, TerrainType.grass)
		self.simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=self.mapModel
		)

		# add UI
		self.simulation.userInterface = UserInterfaceImpl()

		# players
		self.playerTrajan = Player(LeaderType.trajan, human=False)
		self.playerTrajan.initialize()
		self.simulation.players.append(self.playerTrajan)

	def test_districts(self):
		# GIVEN

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.simulation)

		# WHEN
		city.districts.build(DistrictType.campus, HexPoint(5, 5))

		# THEN
		self.assertEqual(city.districts.hasAny(), True)
		self.assertEqual(city.districts.hasAnySpecialtyDistrict(), True)
		self.assertEqual(city.districts.hasDistrict(DistrictType.campus), True)
		self.assertEqual(city.districts.hasDistrict(DistrictType.theaterSquare), False)
		self.assertEqual(city.districts.numberOfSpecialtyDistricts(), 1)

	def test_district_location(self):
		# GIVEN

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.simulation)

		# WHEN
		city.districts.build(DistrictType.campus, HexPoint(5, 5))

		# THEN
		self.assertEqual(city.districts.hasDistrict(DistrictType.campus), True)
		self.assertEqual(city.districts.locationOfDistrict(DistrictType.campus), HexPoint(5, 5))
		self.assertEqual(city.districts.locationOfDistrict(DistrictType.theaterSquare), None)


class TestCityBuildings(unittest.TestCase):
	def setUp(self) -> None:
		self.mapModel = MapModelMock(24, 20, TerrainType.grass)
		self.simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=self.mapModel
		)

		# add UI
		self.simulation.userInterface = UserInterfaceImpl()

		# players
		self.playerTrajan = Player(LeaderType.trajan, human=False)
		self.playerTrajan.initialize()
		self.simulation.players.append(self.playerTrajan)

	def test_housing(self):
		# GIVEN
		self.playerTrajan.government.setGovernment(GovernmentType.monarchy, self.simulation)

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.simulation)

		# WHEN
		housingBefore = city.buildings.housing()
		city.buildings.build(BuildingType.ancientWalls)
		housingAfter = city.buildings.housing()

		# THEN
		self.assertEqual(city.buildings.hasBuilding(BuildingType.ancientWalls), True)
		self.assertEqual(housingBefore, 1.0)
		self.assertEqual(housingAfter, 2)


class TestCityCitizens(unittest.TestCase):
	def setUp(self) -> None:
		self.mapModel = MapModelMock(24, 20, TerrainType.grass)
		self.simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=self.mapModel
		)

		# add UI
		self.simulation.userInterface = UserInterfaceImpl()

		# players
		self.playerTrajan = Player(LeaderType.trajan, human=False)
		self.playerTrajan.initialize()
		self.simulation.players.append(self.playerTrajan)

	def test_turn_small(self):
		# GIVEN

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=False, player=self.playerTrajan)
		city.initialize(self.simulation)

		# WHEN
		city.setLastTurnFoodEarned(5)
		city.cityCitizens.doTurn(simulation=self.simulation)

		# THEN
		# self.assertNotEqual(city.currentBuildableItem(), None)

	def test_turn_capital(self):
		# GIVEN

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.simulation)

		# WHEN
		city.cityStrategy.specializationValue = CitySpecializationType.productionWonder
		city.setLastTurnFoodEarned(2)
		city.cityCitizens.doTurn(simulation=self.simulation)

		# THEN
		# self.assertNotEqual(city.currentBuildableItem(), None)

	def test_workedTileLocations(self):
		# GIVEN

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.simulation)

		# WHEN
		workedTileLocations = city.cityCitizens.workedTileLocations()

		# THEN
		self.assertListEqual(workedTileLocations, [city.location])

	def test_turn_forceWorking(self):
		# GIVEN

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.simulation)
		# city.setPopulation(newPopulation=2, reassignCitizen=True, simulation=simulation)

		# WHEN
		city.cityCitizens.doTurn(self.simulation)
		# city.cityCitizens.forceWorkingPlotAt(HexPoint(4, 4), force=True, simulation=simulation)

		# THEN
		numUnassignedCitizens = city.cityCitizens.numberOfUnassignedCitizens()
		numCitizensWorkingPlots = city.cityCitizens.numberOfCitizensWorkingPlots()
		self.assertEqual(numUnassignedCitizens, 0)
		self.assertEqual(numCitizensWorkingPlots, 1)
		# self.assertEqual(city.cityCitizens.isForcedWorkedAt(HexPoint(4, 4)), True)
		# self.assertEqual(city.cityCitizens.isForcedWorkedAt(HexPoint(4, 6)), False)

	def test_canWorkAt(self):
		# GIVEN

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.simulation)
		self.simulation.addCity(city)

		otherCity = City('Potsdam', HexPoint(9, 5), isCapital=False, player=self.playerTrajan)
		otherCity.initialize(self.simulation)
		self.simulation.addCity(otherCity)
		otherCity.doAcquirePlot(HexPoint(7, 4), self.simulation)

		self.simulation.tileAt(HexPoint(4, 5)).setTerrain(TerrainType.sea)
		self.simulation.tileAt(HexPoint(4, 5)).setFeature(FeatureType.ice)

		# WHEN
		canWorkAtOtherCity = city.cityCitizens.canWorkAt(HexPoint(7, 4), self.simulation)
		canWorkAtIce = city.cityCitizens.canWorkAt(HexPoint(4, 5), self.simulation)
		canWorkAtValid = city.cityCitizens.canWorkAt(HexPoint(5, 4), self.simulation)

		# THEN
		self.assertFalse(canWorkAtOtherCity)
		self.assertFalse(canWorkAtIce)
		self.assertTrue(canWorkAtValid)

	def test_forceWorkingPlotAt(self):
		# GIVEN

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.simulation)
		city.setPopulation(2, True, self.simulation)
		city.cityCitizens.doReallocateCitizens(self.simulation)
		self.simulation.addCity(city)

		self.simulation.tileAt(HexPoint(5, 3)).setTerrain(TerrainType.tundra)

		# WHEN
		city.cityCitizens.forceWorkingPlotAt(HexPoint(5, 4), force=True, simulation=self.simulation)
		forceWorkingPlotAtValid = city.cityCitizens.isForcedWorkedAt(HexPoint(5, 4))

		city.cityCitizens.forceWorkingPlotAt(HexPoint(5, 4), force=True, simulation=self.simulation)
		city.cityCitizens.forceWorkingPlotAt(HexPoint(4, 4), force=True, simulation=self.simulation)
		city.cityCitizens.forceWorkingPlotAt(HexPoint(5, 3), force=True, simulation=self.simulation)
		forceWorkingPlotAtRemoved = city.cityCitizens.isForcedWorkedAt(HexPoint(5, 3))

		# THEN
		self.assertTrue(forceWorkingPlotAtValid)
		self.assertFalse(forceWorkingPlotAtRemoved)

	def test_population_decrease(self):
		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.simulation)
		city.setPopulation(newPopulation=5, reassignCitizen=True, simulation=self.simulation)
		city.cityCitizens.doReallocateCitizens(self.simulation)

		# WHEN
		workingCitizenBefore = city.cityCitizens.numberOfCitizensWorkingPlots()
		city.setPopulation(newPopulation=4, reassignCitizen=True, simulation=self.simulation)
		# city.trainUnit(UnitType.settler, self.simulation)
		city.cityCitizens.doTurn(self.simulation)
		workingCitizenAfter = city.cityCitizens.numberOfCitizensWorkingPlots()

		# THEN
		self.assertEqual(workingCitizenBefore, 5)
		self.assertEqual(workingCitizenAfter, 4)


class TestCityBasics(unittest.TestCase):

	def setUp(self) -> None:
		mapModel = MapModel(10, 10)

		# center
		centerTile = mapModel.tileAt(HexPoint(1, 1))
		centerTile.setTerrain(terrain=TerrainType.grass)
		centerTile.setHills(hills=False)
		centerTile.setImprovement(improvement=ImprovementType.farm)

		# another
		anotherTile = mapModel.tileAt(HexPoint(1, 2))
		anotherTile.setTerrain(terrain=TerrainType.plains)
		anotherTile.setHills(hills=True)
		anotherTile.setImprovement(improvement=ImprovementType.mine)

		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=mapModel
		)
		simulation.userInterface = UserInterfaceImpl()

		playerTrajan = Player(leader=LeaderType.trajan, human=False)
		playerTrajan.initialize()

		playerTrajan.government.setGovernment(governmentType=GovernmentType.autocracy, simulation=simulation)
		playerTrajan.techs.discover(tech=TechType.mining, simulation=simulation)

		city = City(name='Berlin', location=HexPoint(1, 1), isCapital=True, player=playerTrajan)
		city.initialize(simulation)

		self.city = city
		self.simulation = simulation

	def test_city_initial_yields(self):
		"""Test the initial city yields"""
		# GIVEN
		self.city.setPopulation(2, reassignCitizen=False, simulation=self.simulation)

		# WHEN
		foodYield = self.city.foodPerTurn(simulation=self.simulation)
		productionYield = self.city.productionPerTurn(simulation=self.simulation)
		goldYield = self.city.goldPerTurn(simulation=self.simulation)

		# THEN
		self.assertEqual(foodYield, 7.0)
		self.assertEqual(productionYield, 4.0)
		self.assertEqual(goldYield, 6.0)

	def test_city_worked_yields(self):
		"""Test the worked city yields"""
		self.city.setPopulation(3, reassignCitizen=False, simulation=self.simulation)

		self.city.cityCitizens.setWorkedAt(location=HexPoint(1, 0), worked=True)
		self.city.cityCitizens.setWorkedAt(location=HexPoint(1, 1), worked=True)

		# WHEN
		foodYield = self.city.foodPerTurn(simulation=self.simulation)
		productionYield = self.city.productionPerTurn(simulation=self.simulation)
		goldYield = self.city.goldPerTurn(simulation=self.simulation)

		# THEN
		self.assertEqual(foodYield, 8.0)
		self.assertEqual(productionYield, 4.0)
		self.assertEqual(goldYield, 6.0)

	def test_city_no_growth(self):
		# GIVEN

		# WHEN
		self.city.doTurn(self.simulation)

		# THEN
		self.assertEqual(self.city.population(), 1)

	def test_city_growth_from_food(self):
		# GIVEN
		self.city.setFoodBasket(20)

		# WHEN
		self.city.doTurn(self.simulation)

		# THEN
		self.assertEqual(self.city.population(), 2)

	def test_city_turn(self):
		# GIVEN
		self.city.setPopulation(2, reassignCitizen=False, simulation=self.simulation)

		# WHEN
		foodBefore = self.city.foodBasket()
		self.city.doTurn(self.simulation)
		foodAfter = self.city.foodBasket()

		# THEN
		self.assertEqual(foodBefore, 1.0)
		self.assertAlmostEqual(foodAfter, 6.5)


class TestCity(unittest.TestCase):

	def setUp(self) -> None:
		self.mapModel = MapModelMock.duelMap()  # MapModelMock(24, 20, TerrainType.grass)

		# players
		playerBarbarian = Player(LeaderType.barbar, human=False)
		playerBarbarian.initialize()

		self.playerCityState = Player(LeaderType.cityState, human=False)
		self.playerCityState.cityState = CityStateType.auckland
		self.playerCityState.initialize()

		self.playerAlexander = Player(LeaderType.alexander, human=False)
		self.playerAlexander.initialize()

		self.playerTrajan = Player(LeaderType.trajan, human=True)
		self.playerTrajan.initialize()

		self.simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[playerBarbarian, self.playerCityState, self.playerAlexander, self.playerTrajan],
			map=self.mapModel
		)

		# add UI
		self.simulation.userInterface = UserInterfaceImpl()

	def test_initialize(self):
		# GIVEN

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=self.playerAlexander)

		# WHEN
		city.initialize(self.simulation)

		# THEN
		self.assertTrue(city.districts.hasDistrict(DistrictType.cityCenter))

	def test_no_growth(self):
		# GIVEN

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.simulation)

		# WHEN
		_ = city.doTurn(self.simulation)
		notifications = self.playerTrajan.notifications.notifications

		# THEN
		self.assertEqual(city.population(), 1)
		self.assertEqual(len(notifications), 1)  # don't notify user about any change

	def test_one_growth(self):
		# GIVEN

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.simulation)
		city.setFoodBasket(20)

		# WHEN
		city.doTurn(self.simulation)
		notifications = self.playerTrajan.notifications.notifications

		# THEN
		self.assertEqual(city.population(), 2)
		self.assertEqual(len(notifications), 2)  # notify user about growth

	def test_turn(self):
		# GIVEN

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=self.playerAlexander)
		city.initialize(self.simulation)

		# WHEN
		city.doTurn(simulation=self.simulation)

		# THEN
		self.assertIsNotNone(city.currentBuildableItem())

	def test_feature_removal(self):
		# GIVEN
		self.mapModel.tileAt(HexPoint(5, 5)).setFeature(FeatureType.forest)

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=self.playerAlexander)
		city.initialize(self.simulation)
		city.startBuildingBuilding(BuildingType.monument)

		builder = Unit(HexPoint(5, 5), UnitType.builder, self.playerAlexander)
		self.simulation.addUnit(builder)

		progressBefore = city._buildQueue.buildingOf(BuildingType.monument).productionLeftFor(self.playerAlexander)

		self.playerAlexander.techs.discover(TechType.mining, self.simulation)

		# WHEN
		builder.doBuild(BuildType.removeForest, self.simulation)
		city.doTurn(simulation=self.simulation)
		progressAfter = city._buildQueue.buildingOf(BuildingType.monument).productionLeftFor(self.playerAlexander)

		# THEN
		self.assertEqual(progressBefore, 60.0)
		self.assertEqual(progressAfter, 57.0)

	def test_bestLocationForDistrict(self):
		# GIVEN

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.simulation)

		# WHEN
		campusLocation = city.bestLocationForDistrict(DistrictType.campus, simulation=self.simulation)
		harborLocation = city.bestLocationForDistrict(DistrictType.harbor, simulation=self.simulation)

		# THEN
		self.assertIn(campusLocation, [HexPoint(3, 4), HexPoint(4, 4), HexPoint(4, 6)])
		self.assertIn(harborLocation, [HexPoint(3, 5), HexPoint(4, 5), HexPoint(5, 5)])

	def test_healthPoints(self):
		# GIVEN

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.simulation)

		# WHEN
		healthPointsNormal = city.maxHealthPoints()
		city.buildings.build(BuildingType.ancientWalls)
		healthPointsAncientWalls = city.maxHealthPoints()

		# THEN
		self.assertEqual(healthPointsNormal, 200)
		self.assertEqual(healthPointsAncientWalls, 300)

	def test_cityShrink(self):
		# GIVEN

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.simulation)
		city.setPopulation(4, False, self.simulation)
		city.cityCitizens.doReallocateCitizens(self.simulation)

		# WHEN
		workedTilesBefore = len(city.cityCitizens.workedTileLocations())
		city.setPopulation(3, True, self.simulation)
		city.cityCitizens.doValidateForcedWorkingPlots(self.simulation)
		workedTilesAfter = len(city.cityCitizens.workedTileLocations())

		# THEN
		self.assertEqual(workedTilesBefore, 5)
		self.assertEqual(workedTilesAfter, 4)

	def test_updateEurekas(self):
		# GIVEN
		self.simulation.tileAt(HexPoint(4, 5)).setTerrain(TerrainType.grass)
		self.simulation.tileAt(HexPoint(3, 5)).setTerrain(TerrainType.shore)

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.simulation)
		self.simulation.addCity(city)

		city2 = City('Berlin', HexPoint(10, 5), isCapital=False, player=self.playerTrajan)
		city2.initialize(self.simulation)
		self.simulation.addCity(city2)

		# WHEN
		# CivicType.stateWorkforce
		stateWorkforceTriggeredBefore = self.playerTrajan.civics.inspirationTriggeredFor(CivicType.stateWorkforce)
		city.buildDistrict(DistrictType.campus, HexPoint(4, 4), self.simulation)
		stateWorkforceTriggeredAfter = self.playerTrajan.civics.inspirationTriggeredFor(CivicType.stateWorkforce)

		# CivicType.militaryTraining
		militaryTrainingTriggeredBefore = self.playerTrajan.civics.inspirationTriggeredFor(CivicType.militaryTraining)
		city.buildDistrict(DistrictType.encampment, HexPoint(4, 5), self.simulation)
		militaryTrainingTriggeredAfter = self.playerTrajan.civics.inspirationTriggeredFor(CivicType.militaryTraining)

		# CivicType.recordedHistory
		recordedHistoryTriggeredBefore = self.playerTrajan.civics.inspirationTriggeredFor(CivicType.recordedHistory)
		city2.buildDistrict(DistrictType.campus, HexPoint(11, 5), self.simulation)
		recordedHistoryTriggeredAfter = self.playerTrajan.civics.inspirationTriggeredFor(CivicType.recordedHistory)

		# TechType.construction
		constructionTriggeredBefore = self.playerTrajan.techs.eurekaTriggeredFor(TechType.construction)
		city.buildBuilding(BuildingType.waterMill, self.simulation)
		constructionTriggeredAfter = self.playerTrajan.techs.eurekaTriggeredFor(TechType.construction)

		# TechType.engineering
		engineeringTriggeredBefore = self.playerTrajan.techs.eurekaTriggeredFor(TechType.engineering)
		city.buildBuilding(BuildingType.ancientWalls, self.simulation)
		engineeringTriggeredAfter = self.playerTrajan.techs.eurekaTriggeredFor(TechType.engineering)

		# TechType.shipBuilding
		self.playerTrajan.techs.discover(TechType.sailing, self.simulation)
		shipBuildingTriggeredBefore = self.playerTrajan.techs.eurekaTriggeredFor(TechType.shipBuilding)
		city.trainUnit(UnitType.galley, self.simulation)
		city.trainUnit(UnitType.galley, self.simulation)
		shipBuildingTriggeredAfter = self.playerTrajan.techs.eurekaTriggeredFor(TechType.shipBuilding)

		# TechType.economics
		economicsTriggeredBefore = self.playerTrajan.techs.eurekaTriggeredFor(TechType.economics)
		city.buildBuilding(BuildingType.bank, self.simulation)
		city2.buildBuilding(BuildingType.bank, self.simulation)
		economicsTriggeredAfter = self.playerTrajan.techs.eurekaTriggeredFor(TechType.economics)

		# THEN
		self.assertFalse(stateWorkforceTriggeredBefore)
		self.assertTrue(stateWorkforceTriggeredAfter)
		self.assertFalse(militaryTrainingTriggeredBefore)
		self.assertTrue(militaryTrainingTriggeredAfter)
		self.assertFalse(recordedHistoryTriggeredBefore)
		self.assertTrue(recordedHistoryTriggeredAfter)
		self.assertFalse(constructionTriggeredBefore)
		self.assertTrue(constructionTriggeredAfter)
		self.assertFalse(engineeringTriggeredBefore)
		self.assertTrue(engineeringTriggeredAfter)
		self.assertFalse(shipBuildingTriggeredBefore)
		self.assertTrue(shipBuildingTriggeredAfter)
		self.assertFalse(economicsTriggeredBefore)
		self.assertTrue(economicsTriggeredAfter)

	def test_productionPerTurn_petra(self):
		# GIVEN

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.simulation)
		self.simulation.addCity(city)

		self.simulation.tileAt(HexPoint(5, 5)).setTerrain(TerrainType.desert)

		# WHEN
		productionNormal = city.productionPerTurn(self.simulation)

		# city has petra: +2 Food, +2 Gold, and +1 Production
		# on all Desert tiles for this city(non - Floodplains).
		city.buildWonder(WonderType.petra, HexPoint(5, 5), self.simulation)

		city.cityCitizens.setWorkedAt(HexPoint(5, 5), worked=True)
		productionPetra = city.productionPerTurn(self.simulation)

		# THEN
		self.assertEqual(productionNormal, 3.0)
		self.assertEqual(productionPetra, 4.0)

	def test_productionPerTurn_motherRussia(self):
		# GIVEN
		playerPeter = Player(LeaderType.peter, cityState=None, human=False)
		playerPeter.initialize()

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=playerPeter)
		city.initialize(self.simulation)
		self.simulation.addCity(city)

		self.simulation.tileAt(HexPoint(5, 5)).setTerrain(TerrainType.tundra)

		# WHEN
		productionNormal = city.productionPerTurn(self.simulation)

		# motherRussia - Tundra tiles provide + 1 Faith and +1 Production, in addition to their usual yields.
		city.cityCitizens.setWorkedAt(HexPoint(5, 5), worked=True)
		productionMotherRussia = city.productionPerTurn(self.simulation)

		# THEN
		self.assertEqual(productionNormal, 3.0)
		self.assertEqual(productionMotherRussia, 4.0)

	def test_productionPerTurn_stBasilsCathedral(self):
		# GIVEN

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.simulation)
		self.simulation.addCity(city)

		self.simulation.tileAt(HexPoint(5, 5)).setTerrain(TerrainType.tundra)
		city.cityCitizens.setWorkedAt(HexPoint(5, 5), worked=True)

		# WHEN
		productionNormal = city.productionPerTurn(self.simulation)

		# stBasilsCathedral - +1 Food, +1 Production, and +1 Culture on all Tundra tiles for this city.
		city.buildWonder(WonderType.stBasilsCathedral, HexPoint(6, 5), self.simulation)

		productionStBasilsCathedral = city.productionPerTurn(self.simulation)

		# THEN
		self.assertEqual(productionNormal, 3.0)
		self.assertEqual(productionStBasilsCathedral, 4.0)

	def test_productionPerTurn_hueyTeocalli_in_another_city(self):
		# GIVEN

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.simulation)
		self.simulation.addCity(city)

		city2 = City('Potsdam', HexPoint(10, 5), isCapital=False, player=self.playerTrajan)
		city2.initialize(self.simulation)
		self.simulation.addCity(city2)

		self.simulation.tileAt(HexPoint(5, 5)).setFeature(FeatureType.lake)
		city.cityCitizens.setWorkedAt(HexPoint(5, 5), worked=True)

		# WHEN
		productionNormal = city.productionPerTurn(self.simulation)

		# player has hueyTeocalli: +1 Food and +1 Production for each Lake tile in your empire.
		city2.buildWonder(WonderType.hueyTeocalli, HexPoint(9, 5), self.simulation)

		productionHueyTeocalli = city.productionPerTurn(self.simulation)

		# THEN
		self.assertEqual(productionNormal, 3.0)
		self.assertEqual(productionHueyTeocalli, 4.0)

	def test_productionPerTurn_chichenItza(self):
		# GIVEN

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.simulation)
		self.simulation.addCity(city)

		self.simulation.tileAt(HexPoint(5, 5)).setFeature(FeatureType.rainforest)
		city.cityCitizens.setWorkedAt(HexPoint(5, 5), worked=True)

		# WHEN
		productionNormal = city.productionPerTurn(self.simulation)

		# chichenItza: +2 Culture and +1 Production to all Rainforest tiles for this city.
		city.buildWonder(WonderType.chichenItza, HexPoint(6, 5), self.simulation)

		productionChichenItza = city.productionPerTurn(self.simulation)

		# THEN
		self.assertEqual(productionNormal, 3.0)
		self.assertEqual(productionChichenItza, 4.0)

	def test_productionPerTurn_etemenanki_in_another_city(self):
		# GIVEN

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.simulation)
		self.simulation.addCity(city)

		city2 = City('Potsdam', HexPoint(10, 5), isCapital=False, player=self.playerTrajan)
		city2.initialize(self.simulation)
		self.simulation.addCity(city2)

		self.simulation.tileAt(HexPoint(5, 5)).setFeature(FeatureType.marsh)
		city.cityCitizens.setWorkedAt(HexPoint(5, 5), worked=True)

		# WHEN
		productionNormal = city.productionPerTurn(self.simulation)

		# player has etemenanki: +2 Science and +1 Production to all Marsh tiles in your empire.
		city2.buildWonder(WonderType.etemenanki, HexPoint(6, 5), self.simulation)

		productionEtemenanki = city.productionPerTurn(self.simulation)

		# THEN
		self.assertEqual(productionNormal, 3.0)
		self.assertEqual(productionEtemenanki, 4.0)

	def test_productionPerTurn_etemenanki(self):
		# GIVEN

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.simulation)
		self.simulation.addCity(city)

		self.simulation.tileAt(HexPoint(5, 5)).setFeature(FeatureType.floodplains)
		city.cityCitizens.setWorkedAt(HexPoint(5, 5), worked=True)

		# WHEN
		productionNormal = city.productionPerTurn(self.simulation)

		# etemenanki: +1 Science and +1 Production on all Floodplains tiles in this city.
		city.buildWonder(WonderType.etemenanki, HexPoint(6, 5), self.simulation)

		productionEtemenanki = city.productionPerTurn(self.simulation)

		# THEN
		self.assertEqual(productionNormal, 3.0)
		self.assertEqual(productionEtemenanki, 4.0)

	def test_productionPerTurn_godOfTheSea(self):
		# GIVEN

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.simulation)
		self.simulation.addCity(city)

		self.simulation.tileAt(HexPoint(5, 5)).setTerrain(TerrainType.shore)
		self.simulation.tileAt(HexPoint(5, 5)).setImprovement(ImprovementType.fishingBoats)
		city.cityCitizens.setWorkedAt(HexPoint(5, 5), worked=True)

		# WHEN
		productionNormal = city.productionPerTurn(self.simulation)

		# godOfTheSea - 1 Production from Fishing Boats.
		self.playerTrajan.religion.foundPantheon(PantheonType.godOfTheSea, self.simulation)

		productionEtemenanki = city.productionPerTurn(self.simulation)

		# THEN
		self.assertEqual(productionNormal, 3.0)
		self.assertEqual(productionEtemenanki, 4.0)

	def test_build_wonder_statueOfZeus(self):
		# GIVEN

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.simulation)
		self.simulation.addCity(city)

		numberOfUnitsBefore = len(self.simulation.unitsOf(self.playerTrajan))

		# WHEN
		city.buildWonder(WonderType.statueOfZeus, HexPoint(5, 5), self.simulation)
		numberOfUnitsAfter = len(self.simulation.unitsOf(self.playerTrajan))

		# THEN
		self.assertEqual(numberOfUnitsBefore, 0)
		self.assertEqual(numberOfUnitsAfter, 7)

	def test_huge_city(self):
		# GIVEN

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.simulation)
		self.simulation.addCity(city)

		for pt in city.location.areaWithRadius(3):
			tile = self.simulation.tileAt(pt)

			if not tile.hasOwner():
				city.doAcquirePlot(pt, self.simulation)

		city.setPopulation(20, reassignCitizen=True, simulation=self.simulation)
		city.cityCitizens.doReallocateCitizens(self.simulation)

		# districts
		city.buildDistrict(DistrictType.campus, HexPoint(7, 5), self.simulation)
		city.buildDistrict(DistrictType.holySite, HexPoint(8, 5), self.simulation)

		# buildings
		city.buildBuilding(BuildingType.library, self.simulation)
		city.buildBuilding(BuildingType.shrine, self.simulation)

		# wonders
		city.buildWonder(WonderType.pyramids, HexPoint(6, 5), self.simulation)

		# WHEN
		city.doTurn(self.simulation)

		production = city.productionPerTurn(self.simulation)
		food = city.foodPerTurn(self.simulation)
		gold = city.goldPerTurn(self.simulation)
		science = city.sciencePerTurn(self.simulation)
		culture = city.culturePerTurn(self.simulation)
		faith = city.faithPerTurn(self.simulation)

		# THEN
		self.assertEqual(production, 14.0)
		self.assertEqual(food, 44.0)
		self.assertEqual(gold, 17.0)
		self.assertEqual(science, 17.0)  # 19.0
		self.assertEqual(culture, 12.0)
		self.assertEqual(faith, 2.5)

	def test_nearby_pressure(self):
		# GIVEN
		# domestic cities
		city = City("Kinshasa", HexPoint(9, 5), isCapital=False, player=self.playerAlexander)
		city.initialize(self.simulation)
		self.simulation.addCity(city)
		city.setPopulation(5, reassignCitizen=False, simulation=self.simulation)

		cityMbanzaMbata = City("MbanzaMbata", HexPoint(5, 5), isCapital=False, player=self.playerAlexander)
		cityMbanzaMbata.initialize(self.simulation)
		self.simulation.addCity(cityMbanzaMbata)
		cityMbanzaMbata.setPopulation(2, reassignCitizen=False, simulation=self.simulation)

		# foreign cities
		cityManchester = City("Manchester", HexPoint(13, 5), isCapital=False, player=self.playerTrajan)
		cityManchester.initialize(self.simulation)
		self.simulation.addCity(cityManchester)
		cityManchester.setPopulation(2, reassignCitizen=False, simulation=self.simulation)

		cityLiverpool = City("Liverpool", HexPoint(16, 5), isCapital=False, player=self.playerTrajan)
		cityLiverpool.initialize(self.simulation)
		self.simulation.addCity(cityLiverpool)
		cityLiverpool.setPopulation(11, reassignCitizen=False, simulation=self.simulation)

		# WHEN
		distanceKinshasaToMbanzaMbata = cityMbanzaMbata.location.distance(city.location)
		distanceKinshasaToManchester = cityManchester.location.distance(city.location)
		distanceKinshasaToLiverpool = cityLiverpool.location.distance(city.location)
		pressureKinshasa = city.loyaltyPressureFromNearbyCitizen(self.simulation)

		# THEN
		# https://civilization.fandom.com/wiki/Loyalty_(Civ6)#Loyalty_lens
		# Example of pressure from nearby citizens
		#
		# The image to the right contains a small island with 5 cities, 1 city-state which we ignore,
		# 2 English cities (experiencing a Normal Age) and 2 Congolese cities (experiencing a Dark Age).
		# If we calculate the pressure for the city of Kinshasa:
		#
		# Domestic = 0.5 * [ 5 * (10-0) + 2 * (10-4) ] = 31
		# Foreign = [ 1 * 11 * (10-7) + 1 * 2 * (10-4) ] = 45
		# Pressure = 10 * (31 - 45) / (min[31,45] + 0.5) = -4.4

		# pre-checks
		self.assertEqual(city.population(), 5)
		self.assertEqual(distanceKinshasaToMbanzaMbata, 4)
		self.assertEqual(cityMbanzaMbata.population(), 2)

		self.assertEqual(distanceKinshasaToManchester, 4)
		self.assertEqual(cityManchester.population(), 2)

		self.assertEqual(distanceKinshasaToLiverpool, 7)
		self.assertEqual(cityLiverpool.population(), 11)

		self.assertEqual(pressureKinshasa, 3.7362637362637363)  # -4.444444444444445

	def test_amountOfNearbyTerrain(self):
		# GIVEN

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.simulation)
		self.simulation.addCity(city)

		# WHEN
		amountOfNearbyTerrain_plains = city.amountOfNearbyTerrain(TerrainType.plains, self.simulation)
		amountOfNearbyTerrain_grass = city.amountOfNearbyTerrain(TerrainType.grass, self.simulation)
		amountOfNearbyTerrain_shore = city.amountOfNearbyTerrain(TerrainType.shore, self.simulation)

		# THEN
		self.assertEqual(amountOfNearbyTerrain_plains, 5.0)
		self.assertEqual(amountOfNearbyTerrain_grass, 2.0)
		self.assertEqual(amountOfNearbyTerrain_shore, 12.0)

	def test_amountOfNearbyResource(self):
		# GIVEN

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.simulation)
		self.simulation.addCity(city)

		self.playerTrajan.techs.discover(TechType.mining, self.simulation)
		self.playerTrajan.techs.discover(TechType.bronzeWorking, self.simulation)
		self.playerTrajan.techs.discover(TechType.animalHusbandry, self.simulation)

		self.simulation.tileAt(HexPoint(5, 5)).setResource(ResourceType.iron)
		self.simulation.tileAt(HexPoint(3, 5)).setResource(ResourceType.sheep)
		self.simulation.tileAt(HexPoint(4, 4)).setResource(ResourceType.sheep)

		# WHEN
		amountOfNearbyIron = city.amountOfNearbyResource(ResourceType.iron, self.simulation)
		amountOfNearbySheep = city.amountOfNearbyResource(ResourceType.sheep, self.simulation)
		amountOfNearbyUranium = city.amountOfNearbyResource(ResourceType.uranium, self.simulation)

		# THEN
		self.assertEqual(amountOfNearbyIron, 1.0)
		self.assertEqual(amountOfNearbySheep, 2.0)
		self.assertEqual(amountOfNearbyUranium, 0.0)

	def test_city_state_cannot_build_settler(self):
		# GIVEN

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=self.playerCityState)
		city.initialize(self.simulation)
		self.simulation.addCity(city)

		# WHEN
		canBuildSettler = city.canTrainUnit(UnitType.settler, self.simulation)

		# THEN
		self.assertEqual(canBuildSettler, False)

	def test_wonderCity(self):
		# GIVEN
		self.playerAlexander.techs.discover(TechType.pottery, self.simulation)
		self.playerAlexander.techs.discover(TechType.masonry, self.simulation)

		self.playerAlexander.foundAt(HexPoint(29, 7), "Capital", self.simulation)
		capitalCity: City = self.simulation.cityAt(HexPoint(29, 7))

		capitalTile: Tile = self.simulation.tileAt(HexPoint(30, 7))
		capitalTile.setHills(False)
		capitalTile.setTerrain(TerrainType.desert)

		# WHEN
		canBuild = capitalCity.canBuildWonder(WonderType.pyramids, HexPoint(30, 7), self.simulation)

		# THEN
		self.assertEqual(True, canBuild)

	def test_numberOfPlotsAcquiredBy(self):
		# GIVEN

		# own city
		ownCity = City('Berlin', HexPoint(4, 4), isCapital=True, player=self.playerAlexander)
		ownCity.initialize(self.simulation)
		self.simulation.addCity(ownCity)

		# foreign city
		foreignCity = City('London', HexPoint(9, 4), isCapital=True, player=self.playerTrajan)
		foreignCity.initialize(self.simulation)
		self.simulation.addCity(foreignCity)

		# WHEN
		acquiredBefore = foreignCity.numberOfPlotsAcquiredBy(self.playerAlexander)
		bought = ownCity.doBuyPlot(HexPoint(7, 4), self.simulation)
		acquiredAfter = foreignCity.numberOfPlotsAcquiredBy(self.playerAlexander)

		# THEN
		self.assertEqual(acquiredBefore, 0)
		self.assertTrue(bought)
		self.assertEqual(acquiredAfter, 1)
