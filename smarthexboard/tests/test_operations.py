import unittest

import pytest

from smarthexboard.smarthexboardlib.game.ai.militaryTypes import OperationStateType
from smarthexboard.smarthexboardlib.game.baseTypes import HandicapType
from smarthexboard.smarthexboardlib.game.civilizations import LeaderType
from smarthexboard.smarthexboardlib.game.game import GameModel
from smarthexboard.smarthexboardlib.game.generation import UserInterfaceImpl
from smarthexboard.smarthexboardlib.game.operations import FoundCityOperation, NavalAttackOperation
from smarthexboard.smarthexboardlib.game.players import Player
from smarthexboard.smarthexboardlib.game.states.victories import VictoryType
from smarthexboard.smarthexboardlib.game.unitTypes import UnitType, UnitOperationType
from smarthexboard.smarthexboardlib.game.units import Unit
from smarthexboard.smarthexboardlib.map.base import HexPoint
from smarthexboard.tests.test_utils import MapModelMock


class TestOperation(unittest.TestCase):
	def setUp(self) -> None:
		self.mapModel = MapModelMock.duelMap()

		# players
		self.playerBarbarian = Player(LeaderType.barbar, human=False)
		self.playerBarbarian.initialize()

		self.playerAlexander = Player(LeaderType.alexander, human=False)
		self.playerAlexander.initialize()

		self.playerTrajan = Player(LeaderType.trajan, human=True)
		self.playerTrajan.initialize()

		self.simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[self.playerBarbarian, self.playerAlexander, self.playerTrajan],
			map=self.mapModel
		)

		# add UI
		self.simulation.userInterface = UserInterfaceImpl()

		# add human scout (so that the game is not finished)
		playerTrajanScout = Unit(HexPoint(11, 19), UnitType.scout, self.playerTrajan)
		self.simulation.addUnit(playerTrajanScout)

	def test_equal(self):
		# GIVEN
		operation1 = FoundCityOperation()
		operation1.player = self.playerAlexander
		operation2 = NavalAttackOperation()
		operation3 = FoundCityOperation()
		operation3.player = self.playerTrajan
		operation4 = FoundCityOperation()
		operation4.player = self.playerAlexander

		# WHEN

		# THEN
		self.assertEqual(operation1, operation1)
		self.assertNotEqual(operation1, operation2)
		self.assertNotEqual(operation1, operation3)
		self.assertEqual(operation1, operation4)
		operation4.state = OperationStateType.atTarget
		self.assertNotEqual(operation1, operation4)

		with pytest.raises(Exception):
			b = operation1 == 3

	# ...

	def test_updateTargetTo(self):
		# GIVEN
		operation1 = FoundCityOperation()

		# WHEN
		operation1.updateTargetTo(HexPoint(3, 3))

		# THEN
		self.assertEqual(operation1.targetPosition, HexPoint(3, 3))
		with pytest.raises(Exception):
			operation1.updateTargetTo(1)


class TestOperations(unittest.TestCase):
	def setUp(self) -> None:
		self.mapModel = MapModelMock.duelMap()

		# players
		self.playerBarbarian = Player(LeaderType.barbar, human=False)
		self.playerBarbarian.initialize()

		self.playerAlexander = Player(LeaderType.alexander, human=False)
		self.playerAlexander.initialize()

		self.playerTrajan = Player(LeaderType.trajan, human=True)
		self.playerTrajan.initialize()

		self.simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[self.playerBarbarian, self.playerAlexander, self.playerTrajan],
			map=self.mapModel
		)

		# add UI
		self.simulation.userInterface = UserInterfaceImpl()

		# add human scout (so that the game is not finished)
		playerTrajanScout = Unit(HexPoint(11, 19), UnitType.scout, self.playerTrajan)
		self.simulation.addUnit(playerTrajanScout)

	def test_foundCity_operation(self):
		# GIVEN

		# WHEN
		self.playerAlexander.addOperation(
			UnitOperationType.foundCity,
			None,
			None,
			self.simulation.areaOf(HexPoint(5, 5)),
			None,
			self.simulation
		)

		# THEN
		self.assertEqual(len(self.playerAlexander.operations.operationsOfType(UnitOperationType.foundCity)), 1)

	def test_foundCity_operation_execute(self):
		# GIVEN
		# city
		self.playerAlexander.foundAt(HexPoint(26, 17), "Capital", self.simulation)

		# settler
		playerAlexanderSettler = Unit(HexPoint(27, 17), UnitType.settler, self.playerAlexander)
		self.simulation.addUnit(playerAlexanderSettler)

		# warrior
		playerAlexanderWarrior = Unit(HexPoint(27, 17), UnitType.warrior, self.playerAlexander)
		self.simulation.addUnit(playerAlexanderWarrior)

		humanPlayer = self.simulation.humanPlayer()

		self.mapModel.discoverRadius(self.playerAlexander, HexPoint(27, 17), 6, self.simulation)

		# WHEN
		# self.playerAlexander.doTurn(self.simulation)
		while not (humanPlayer.hasProcessedAutoMoves() and humanPlayer.turnFinished()):

			if self.playerAlexander.isTurnActive():
				print('active')

			self.simulation.update()

			if humanPlayer.isTurnActive():
				break

		# THEN
		self.assertEqual(len(self.playerAlexander.operations.operationsOfType(UnitOperationType.foundCity)), 1)
