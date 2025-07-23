import unittest

from smarthexboard.smarthexboardlib.game.baseTypes import HandicapType
from smarthexboard.smarthexboardlib.game.cities import City
from smarthexboard.smarthexboardlib.game.civilizations import LeaderType
from smarthexboard.smarthexboardlib.game.game import GameModel
from smarthexboard.smarthexboardlib.game.generation import UserInterfaceImpl
from smarthexboard.smarthexboardlib.game.players import Player
from smarthexboard.smarthexboardlib.game.states.builds import BuildType
from smarthexboard.smarthexboardlib.game.states.victories import VictoryType
from smarthexboard.smarthexboardlib.game.unitMissions import UnitMission
from smarthexboard.smarthexboardlib.game.unitTypes import UnitType, UnitMissionType, UnitActivityType
from smarthexboard.smarthexboardlib.game.units import Unit
from smarthexboard.smarthexboardlib.map.base import HexPoint
from smarthexboard.smarthexboardlib.map.improvements import ImprovementType
from smarthexboard.smarthexboardlib.map.types import TerrainType
from smarthexboard.tests.test_utils import MapModelMock


class TestUnitMissions(unittest.TestCase):

	def setUp(self) -> None:
		self.mapModel = MapModelMock(24, 20, TerrainType.grass)
		self.simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=self.mapModel
		)

		self.playerTrajan = Player(leader=LeaderType.trajan, cityState=None, human=False)
		self.playerTrajan.initialize()
		self.simulation.players.append(self.playerTrajan)

		playerVictoria = Player(leader=LeaderType.victoria, cityState=None, human=True)
		playerVictoria.initialize()
		self.simulation.players.append(playerVictoria)

		# add UI
		self.simulation.userInterface = UserInterfaceImpl()

	def test_found_mission(self):
		# GIVEN
		playerTrajanSettler = Unit(HexPoint(5, 5), UnitType.settler, self.playerTrajan)
		self.simulation.addUnit(playerTrajanSettler)

		# WHEN
		playerTrajanSettler.pushMission(UnitMission(missionType=UnitMissionType.found), self.simulation)
		playerTrajanSettler.updateMission(self.simulation)

		# THEN
		self.assertEqual(playerTrajanSettler.peekMission(), None)

	def test_moveTo_mission(self):
		# GIVEN
		playerTrajanScout = Unit(HexPoint(5, 5), UnitType.scout, self.playerTrajan)
		self.simulation.addUnit(playerTrajanScout)

		# WHEN
		playerTrajanScout.pushMission(UnitMission(missionType=UnitMissionType.moveTo, target=HexPoint(4, 1)), self.simulation)
		playerTrajanScout.updateMission(self.simulation)

		# THEN
		self.assertEqual(playerTrajanScout.peekMission().missionType, UnitMissionType.moveTo)
		self.assertEqual(playerTrajanScout.location, HexPoint(3, 2))

	def test_followPath_mission(self):
		# GIVEN
		# initial unit
		playerTrajanWarrior = Unit(HexPoint(15, 16), UnitType.warrior, self.playerTrajan)
		self.simulation.addUnit(playerTrajanWarrior)

		# this is cheating
		self.mapModel.discover(self.playerTrajan, self.simulation)

		# WHEN
		path = playerTrajanWarrior.pathTowards(HexPoint(2, 3), options=None, simulation=self.simulation)
		playerTrajanWarrior.pushMission(UnitMission(missionType=UnitMissionType.followPath, path=path), simulation=self.simulation)

		# THEN
		self.assertIsNotNone(playerTrajanWarrior.peekMission())
		self.assertEqual(playerTrajanWarrior.peekMission().missionType, UnitMissionType.followPath)
		self.assertEqual(playerTrajanWarrior.peekMission().path, path)
		self.assertNotEqual(playerTrajanWarrior.location, HexPoint(15, 16))

	def test_fortify_mission(self):
		# GIVEN
		# initial unit
		playerTrajanWarrior = Unit(HexPoint(15, 16), UnitType.warrior, self.playerTrajan)
		self.simulation.addUnit(playerTrajanWarrior)

		# this is cheating
		self.mapModel.discover(self.playerTrajan, self.simulation)

		# initial city
		city = City(name='Berlin', location=HexPoint(15, 17), isCapital=True, player=self.playerTrajan)
		city.initialize(self.simulation)
		self.simulation.addCity(city)

		# WHEN
		playerTrajanWarrior.pushMission(UnitMission(missionType=UnitMissionType.fortify), simulation=self.simulation)

		# THEN
		self.assertIsNone(playerTrajanWarrior.peekMission())
		self.assertEqual(playerTrajanWarrior.isFortified(), True)
		self.assertEqual(playerTrajanWarrior.location, HexPoint(15, 16))

	def test_garrison_mission(self):
		# GIVEN
		# initial unit
		playerTrajanWarrior = Unit(HexPoint(15, 16), UnitType.warrior, self.playerTrajan)
		self.simulation.addUnit(playerTrajanWarrior)

		# initial city
		city = City(name='Berlin', location=HexPoint(15, 16), isCapital=True, player=self.playerTrajan)
		city.initialize(self.simulation)
		self.simulation.addCity(city)

		# this is cheating
		self.mapModel.discover(self.playerTrajan, self.simulation)

		# WHEN
		playerTrajanWarrior.pushMission(UnitMission(missionType=UnitMissionType.garrison), simulation=self.simulation)

		# THEN
		self.assertIsNone(playerTrajanWarrior.peekMission())
		self.assertEqual(playerTrajanWarrior.isGarrisoned(), True)
		self.assertEqual(playerTrajanWarrior.location, HexPoint(15, 16))
		self.assertEqual(city.hasGarrison(), True)

	def test_build_mission(self):
		# GIVEN
		# unit
		playerTrajanBuilder = Unit(HexPoint(15, 16), UnitType.builder, self.playerTrajan)
		self.simulation.addUnit(playerTrajanBuilder)

		self.mapModel.tileAt(HexPoint(15, 16)).setOwner(self.playerTrajan)

		# WHEN
		playerTrajanBuilder.pushMission(UnitMission(missionType=UnitMissionType.build, buildType=BuildType.farm), simulation=self.simulation)

		# THEN
		self.assertIsNone(playerTrajanBuilder.peekMission())
		self.assertEqual(playerTrajanBuilder.location, HexPoint(15, 16))
		self.assertEqual(self.mapModel.improvementAt(HexPoint(15, 16)), ImprovementType.farm)
		self.assertEqual(playerTrajanBuilder.buildCharges(), 2)

	def test_heal_mission(self):
		# GIVEN
		# unit
		playerTrajanBuilder = Unit(HexPoint(15, 16), UnitType.builder, self.playerTrajan)
		playerTrajanBuilder.setHealthPoints(95)
		self.simulation.addUnit(playerTrajanBuilder)

		self.mapModel.tileAt(HexPoint(15, 16)).setOwner(self.playerTrajan)

		# WHEN
		playerTrajanBuilder.pushMission(UnitMission(missionType=UnitMissionType.heal), simulation=self.simulation)
		self.playerTrajan.doUnitReset(self.simulation)

		# THEN
		self.assertIsNone(playerTrajanBuilder.peekMission())
		self.assertEqual(playerTrajanBuilder.activityType(), UnitActivityType.heal)
		self.assertEqual(playerTrajanBuilder.damage(), 0)  #
		self.assertEqual(playerTrajanBuilder.healthPoints(), 100)  #

	def test_pillage_mission(self):
		# GIVEN
		# another player
		playerAlexander = Player(leader=LeaderType.alexander, cityState=None, human=False)
		playerAlexander.initialize()
		self.simulation.players.append(playerAlexander)

		# initial unit
		playerTrajanWarrior = Unit(HexPoint(15, 15), UnitType.warrior, self.playerTrajan)
		self.simulation.addUnit(playerTrajanWarrior)

		# initial city
		city = City(name='Athens', location=HexPoint(15, 16), isCapital=True, player=playerAlexander)
		city.initialize(self.simulation)
		self.simulation.addCity(city)

		tile = self.simulation.tileAt(HexPoint(15, 15))
		tile.setImprovement(ImprovementType.farm)

		# this is cheating
		self.mapModel.discover(self.playerTrajan, self.simulation)

		# WHEN
		playerTrajanWarrior.pushMission(UnitMission(missionType=UnitMissionType.pillage, target=HexPoint(15, 15)), simulation=self.simulation)

		# THEN
		self.assertIsNone(playerTrajanWarrior.peekMission())
		self.assertEqual(playerTrajanWarrior.location, HexPoint(15, 15))
		self.assertEqual(tile.isImprovementPillaged(), True)
