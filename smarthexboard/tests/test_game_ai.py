import os
import sys
import unittest

import django

from smarthexboard.smarthexboardlib.game.ai.economicStrategies import EconomicStrategyType
from smarthexboard.smarthexboardlib.game.ai.economics import EconomicStrategyAdoptions
from smarthexboard.smarthexboardlib.game.ai.homeland import HomelandUnit, HomelandAI, HomelandMoveType, HomelandMove
from smarthexboard.smarthexboardlib.game.baseTypes import HandicapType
from smarthexboard.smarthexboardlib.game.civilizations import LeaderType
from smarthexboard.smarthexboardlib.game.game import GameModel
from smarthexboard.smarthexboardlib.game.generation import UserInterfaceImpl
from smarthexboard.smarthexboardlib.game.players import Player
from smarthexboard.smarthexboardlib.game.states.builds import BuildType
from smarthexboard.smarthexboardlib.game.states.victories import VictoryType
from smarthexboard.smarthexboardlib.game.unitTypes import UnitType, UnitAutomationType
from smarthexboard.smarthexboardlib.game.units import Unit
from smarthexboard.smarthexboardlib.map.base import HexPoint
from smarthexboard.smarthexboardlib.map.types import TerrainType
from smarthexboard.tests.test_utils import MapModelMock

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smarthexboard.settings')
django.setup()


class TestHomelandUnit(unittest.TestCase):
	def test_homelandUnit_eq(self):
		# GIVEN
		player = Player(LeaderType.alexander)
		player.initialize()

		unit0 = Unit(location=HexPoint(1, 1), unitType=UnitType.settler, player=player)
		homelandUnit0 = HomelandUnit(unit0)

		unit1 = Unit(location=HexPoint(1, 2), unitType=UnitType.settler, player=player)
		homelandUnit1 = HomelandUnit(unit1)

		unit2 = Unit(location=HexPoint(1, 3), unitType=UnitType.settler, player=player)
		homelandUnit2 = HomelandUnit(unit2)

		# WHEN
		homelandUnit0.movesToTarget = 3
		homelandUnit1.movesToTarget = 3
		homelandUnit2.movesToTarget = 5

		# THEN
		self.assertTrue(homelandUnit0 == homelandUnit1)
		self.assertTrue(homelandUnit0 == homelandUnit0)
		self.assertFalse(homelandUnit0 == homelandUnit2)
		self.assertFalse(homelandUnit1 == homelandUnit2)

	def test_homelandUnit_lt(self):
		# GIVEN
		player = Player(LeaderType.alexander)
		player.initialize()

		unit0 = Unit(location=HexPoint(1, 1), unitType=UnitType.settler, player=player)
		homelandUnit0 = HomelandUnit(unit0)

		unit1 = Unit(location=HexPoint(1, 2), unitType=UnitType.settler, player=player)
		homelandUnit1 = HomelandUnit(unit1)

		unit2 = Unit(location=HexPoint(1, 3), unitType=UnitType.settler, player=player)
		homelandUnit2 = HomelandUnit(unit2)

		# WHEN
		homelandUnit0.movesToTarget = 3
		homelandUnit1.movesToTarget = 3
		homelandUnit2.movesToTarget = 5

		# THEN
		self.assertFalse(homelandUnit0 < homelandUnit1)
		self.assertTrue(homelandUnit0 < homelandUnit2)
		self.assertTrue(homelandUnit1 < homelandUnit2)
		self.assertFalse(homelandUnit1 < homelandUnit1)


class TestHomelandAI(unittest.TestCase):
	def test_constructor(self):
		player = Player(LeaderType.alexander, human=False)
		player.initialize()

		mapModel = MapModelMock(24, 20, TerrainType.grass)
		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[player],
			map=mapModel
		)

		homeland = HomelandAI(player)

		self.assertEqual(homeland.currentTurnUnits, [])
		self.assertEqual(homeland.currentTurnUnits, [])
		self.assertEqual(homeland.currentMoveUnits, [])
		self.assertEqual(homeland.currentMoveHighPriorityUnits, [])

		self.assertEqual(homeland.movePriorityList, [])
		self.assertEqual(homeland.movePriorityTurn, 0)

		self.assertEqual(homeland.currentBestMoveUnit, None)
		self.assertEqual(homeland.currentBestMoveUnitTurns, sys.maxsize)
		self.assertEqual(homeland.currentBestMoveHighPriorityUnit, None)
		self.assertEqual(homeland.currentBestMoveHighPriorityUnitTurns, sys.maxsize)

		self.assertEqual(homeland.targetedCities, [])
		self.assertEqual(homeland.targetedSentryPoints, [])
		self.assertEqual(homeland.targetedForts, [])
		self.assertEqual(homeland.targetedNavalResources, [])
		self.assertEqual(homeland.targetedHomelandRoads, [])
		self.assertEqual(homeland.targetedAncientRuins, [])

	def test_human_units(self):
		player = Player(LeaderType.alexander, human=True)
		player.initialize()

		mapModel = MapModelMock(24, 20, TerrainType.grass)
		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[player],
			map=mapModel
		)

		simulation.userInterface = UserInterfaceImpl()

		scout = Unit(HexPoint(3, 3), UnitType.scout, player)
		scout.automate(UnitAutomationType.explore, simulation)
		simulation.addUnit(scout)

		builder = Unit(HexPoint(3, 4), UnitType.builder, player)
		builder.automate(UnitAutomationType.build, simulation)
		simulation.addUnit(builder)

		# settler = Unit(HexPoint(4, 3), UnitType.settler, player)
		# simulation.addUnit(settler)

		warrior = Unit(HexPoint(4, 4), UnitType.warrior, player)
		warrior.automate(UnitAutomationType.explore, simulation)
		simulation.addUnit(warrior)

		homeland = HomelandAI(player)
		homeland.doTurn(simulation)

		priorityList = [
			HomelandMove(moveType=HomelandMoveType.tradeUnit, priority=103),
			HomelandMove(moveType=HomelandMoveType.settle, priority=58),
			HomelandMove(moveType=HomelandMoveType.aircraftToTheFront, priority=51),
			HomelandMove(moveType=HomelandMoveType.ancientRuins, priority=41),
			HomelandMove(moveType=HomelandMoveType.explore, priority=36),
			HomelandMove(moveType=HomelandMoveType.exploreSea, priority=36),
			HomelandMove(moveType=HomelandMoveType.heal, priority=31),
			HomelandMove(moveType=HomelandMoveType.toSafety, priority=31),
			HomelandMove(moveType=HomelandMoveType.worker, priority=30),
			HomelandMove(moveType=HomelandMoveType.workerSea, priority=30),
			HomelandMove(moveType=HomelandMoveType.upgrade, priority=30),
			HomelandMove(moveType=HomelandMoveType.sentry, priority=21),
			HomelandMove(moveType=HomelandMoveType.mobileReserve, priority=16),
			HomelandMove(moveType=HomelandMoveType.garrison, priority=11),
			HomelandMove(moveType=HomelandMoveType.none, priority=0),
			HomelandMove(moveType=HomelandMoveType.unassigned, priority=0),
			HomelandMove(moveType=HomelandMoveType.patrol, priority=0)
		]

		self.assertEqual(homeland.currentTurnUnits, [])
		self.assertEqual(homeland.currentTurnUnits, [])
		self.assertEqual(homeland.currentMoveUnits, [])
		self.assertEqual(homeland.currentMoveHighPriorityUnits, [])

		self.assertEqual(homeland.movePriorityList, priorityList)
		self.assertEqual(homeland.movePriorityTurn, 0)

		self.assertEqual(homeland.currentBestMoveUnit, None)
		self.assertEqual(homeland.currentBestMoveUnitTurns, sys.maxsize)
		self.assertEqual(homeland.currentBestMoveHighPriorityUnit, None)
		self.assertEqual(homeland.currentBestMoveHighPriorityUnitTurns, sys.maxsize)

		self.assertEqual(homeland.targetedCities, [])
		self.assertEqual(homeland.targetedSentryPoints, [])
		self.assertEqual(homeland.targetedForts, [])
		self.assertEqual(homeland.targetedNavalResources, [])
		self.assertEqual(homeland.targetedHomelandRoads, [])
		self.assertEqual(homeland.targetedAncientRuins, [])

	def test_ai_units(self):
		player = Player(LeaderType.alexander, human=False)
		player.initialize()

		mapModel = MapModelMock(24, 20, TerrainType.grass)
		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[player],
			map=mapModel
		)

		simulation.userInterface = UserInterfaceImpl()

		scout = Unit(HexPoint(3, 3), UnitType.scout, player)
		scout.automate(UnitAutomationType.explore, simulation)
		simulation.addUnit(scout)

		builder = Unit(HexPoint(3, 4), UnitType.builder, player)
		builder.automate(UnitAutomationType.build, simulation)
		simulation.addUnit(builder)

		# settler = Unit(HexPoint(4, 3), UnitType.settler, player)
		# simulation.addUnit(settler)

		warrior = Unit(HexPoint(4, 4), UnitType.warrior, player)
		warrior.automate(UnitAutomationType.explore, simulation)
		simulation.addUnit(warrior)

		homeland = HomelandAI(player)
		homeland.doTurn(simulation)

		expectedTurnUnits = [
			HomelandUnit(Unit(HexPoint(3, 3), UnitType.scout, player)),
			HomelandUnit(Unit(HexPoint(4, 4), UnitType.warrior, player))
		]

		priorityList = [
			HomelandMove(moveType=HomelandMoveType.tradeUnit, priority=103),
			HomelandMove(moveType=HomelandMoveType.settle, priority=58),
			HomelandMove(moveType=HomelandMoveType.aircraftToTheFront, priority=51),
			HomelandMove(moveType=HomelandMoveType.ancientRuins, priority=41),
			HomelandMove(moveType=HomelandMoveType.explore, priority=36),
			HomelandMove(moveType=HomelandMoveType.exploreSea, priority=36),
			HomelandMove(moveType=HomelandMoveType.heal, priority=31),
			HomelandMove(moveType=HomelandMoveType.toSafety, priority=31),
			HomelandMove(moveType=HomelandMoveType.worker, priority=30),
			HomelandMove(moveType=HomelandMoveType.workerSea, priority=30),
			HomelandMove(moveType=HomelandMoveType.upgrade, priority=30),
			HomelandMove(moveType=HomelandMoveType.sentry, priority=21),
			HomelandMove(moveType=HomelandMoveType.mobileReserve, priority=16),
			HomelandMove(moveType=HomelandMoveType.garrison, priority=11),
			HomelandMove(moveType=HomelandMoveType.none, priority=0),
			HomelandMove(moveType=HomelandMoveType.unassigned, priority=0),
			HomelandMove(moveType=HomelandMoveType.patrol, priority=0)
		]

		self.assertEqual(homeland.currentTurnUnits, [])
		self.assertEqual(homeland.currentMoveUnits, expectedTurnUnits)
		self.assertEqual(homeland.currentMoveHighPriorityUnits, [])

		self.assertEqual(homeland.movePriorityList, priorityList)
		self.assertEqual(homeland.movePriorityTurn, 0)

		self.assertEqual(homeland.currentBestMoveUnit, None)
		self.assertEqual(homeland.currentBestMoveUnitTurns, sys.maxsize)
		self.assertEqual(homeland.currentBestMoveHighPriorityUnit, None)
		self.assertEqual(homeland.currentBestMoveHighPriorityUnitTurns, sys.maxsize)

		self.assertEqual(homeland.targetedCities, [])
		self.assertEqual(homeland.targetedSentryPoints, [])
		self.assertEqual(homeland.targetedForts, [])
		self.assertEqual(homeland.targetedNavalResources, [])
		self.assertEqual(homeland.targetedHomelandRoads, [])
		self.assertEqual(homeland.targetedAncientRuins, [])


class TestEconomics(unittest.TestCase):
	def test_adoption(self):
		# GIVEN
		adoptions = EconomicStrategyAdoptions()

		# WHEN
		adoptions.adopt(EconomicStrategyType.losingMoney, turnOfAdoption=2)

		# THEN
		self.assertTrue(adoptions.adopted(EconomicStrategyType.losingMoney))
		self.assertEqual(adoptions.turnOfAdoption(EconomicStrategyType.losingMoney), 2)
		self.assertFalse(adoptions.adopted(EconomicStrategyType.foundCity))
		self.assertEqual(adoptions.turnOfAdoption(EconomicStrategyType.foundCity), -1)

	def test_abandon(self):
		# GIVEN
		adoptions = EconomicStrategyAdoptions()
		adoptions.adopt(EconomicStrategyType.losingMoney, turnOfAdoption=2)

		# WHEN
		adoptions.abandon(EconomicStrategyType.losingMoney)

		# THEN
		self.assertFalse(adoptions.adopted(EconomicStrategyType.losingMoney))


class TestBuilds(unittest.TestCase):
	def test_buildOn(self):
		mapModel = MapModelMock(10, 10, TerrainType.grass)
		tile = mapModel.tileAt(HexPoint(1, 1))
		buildTime = BuildType.farm.buildTimeOn(tile)

		self.assertEqual(buildTime, 600)
