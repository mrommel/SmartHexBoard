import unittest

import pytest

from smarthexboard.smarthexboardlib.game.ai.army import ArmyFormationSlot, Army
from smarthexboard.smarthexboardlib.game.ai.militaryTypes import UnitFormationType, UnitFormationPosition
from smarthexboard.smarthexboardlib.game.baseTypes import HandicapType
from smarthexboard.smarthexboardlib.game.civilizations import LeaderType
from smarthexboard.smarthexboardlib.game.game import GameModel
from smarthexboard.smarthexboardlib.game.generation import UserInterfaceImpl
from smarthexboard.smarthexboardlib.game.operations import Operation
from smarthexboard.smarthexboardlib.game.players import Player
from smarthexboard.smarthexboardlib.game.states.victories import VictoryType
from smarthexboard.smarthexboardlib.game.unitTypes import UnitOperationType, UnitType
from smarthexboard.smarthexboardlib.game.units import Unit
from smarthexboard.smarthexboardlib.map.base import HexPoint
from smarthexboard.smarthexboardlib.map.types import UnitDomainType
from smarthexboard.tests.test_utils import MapModelMock
from smarthexboard.utils import is_valid_uuid


class TestArmyFormationSlot(unittest.TestCase):
	def test_constructor(self):
		formationSlot = ArmyFormationSlot(None, estimatedTurnAtCheckpoint=7, startedOnOperation=False)
		self.assertEqual(formationSlot.turnAtCheckpoint(), 7)
		self.assertEqual(formationSlot.hasStartedOnOperation(), False)

	def test_estimatedTurnAtCheckpoint(self):
		# GIVEN
		formationSlot = ArmyFormationSlot(None, estimatedTurnAtCheckpoint=7, startedOnOperation=False)

		# WHEN
		before = formationSlot.turnAtCheckpoint()
		formationSlot.setTurnAtCheckpoint(9)
		after = formationSlot.turnAtCheckpoint()

		# THEN
		self.assertEqual(before, 7)
		self.assertEqual(after, 9)

	def test_turnAtCheckpoint(self):
		# GIVEN
		formationSlot = ArmyFormationSlot(None, estimatedTurnAtCheckpoint=7, startedOnOperation=False)

		# WHEN
		before = formationSlot.hasStartedOnOperation()
		formationSlot.setStartedOnOperation(True)
		after = formationSlot.hasStartedOnOperation()

		# THEN
		self.assertEqual(before, False)
		self.assertEqual(after, True)


class TestArmy(unittest.TestCase):
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

	def test_constructor(self):
		army = Army(None, None, UnitFormationType.settlerEscort)

		self.assertTrue(is_valid_uuid(army.identifier))
		self.assertEqual(len(army.formationEntries), 2)

	def test_equal(self):
		army1 = Army(None, None, UnitFormationType.settlerEscort)
		army2 = Army(None, None, UnitFormationType.navalEscort)

		self.assertEqual(army1, army1)
		self.assertNotEqual(army1, army2)

		with pytest.raises(Exception):
			a = army1 == UnitFormationType.settlerEscort

	def test_disableSlot(self):
		army = Army(None, None, UnitFormationType.settlerEscort)

		with pytest.raises(Exception):
			army.disableSlot(None)

	def test_removeUnit(self):
		# GIVEN
		operation = Operation(UnitOperationType.foundCity)
		army = Army(self.playerAlexander, operation, UnitFormationType.settlerEscort)

		settler = Unit(HexPoint(5, 5), UnitType.settler, self.playerAlexander)
		self.simulation.addUnit(settler)

		# WHEN
		removeUnitWithoutUnits = army.removeUnit(settler)

		army.addUnit(settler, 0)

		removeUnitWithUnit = army.removeUnit(settler)

		# THEN
		self.assertEqual(removeUnitWithoutUnits, False)
		self.assertEqual(removeUnitWithUnit, True)

	def test_doTurn(self):
		# GIVEN
		operation = Operation(UnitOperationType.foundCity)
		army = Army(self.playerAlexander, operation, UnitFormationType.settlerEscort)

		settler = Unit(HexPoint(5, 5), UnitType.settler, self.playerAlexander)
		self.simulation.addUnit(settler)

		# WHEN
		army.doTurn(self.simulation)

		# THEN
		self.assertTrue(True)

	# ...

	def test_turnAtNextCheckpoint(self):
		# GIVEN
		operation = Operation(UnitOperationType.foundCity)
		army = Army(self.playerAlexander, operation, UnitFormationType.settlerEscort)

		settler = Unit(HexPoint(12, 13), UnitType.settler, self.playerAlexander)
		self.simulation.addUnit(settler)

		warrior = Unit(HexPoint(12, 12), UnitType.warrior, self.playerAlexander)
		self.simulation.addUnit(warrior)

		# WHEN
		army.addUnit(settler, 0)
		army.addUnit(warrior, 1)
		army.position = HexPoint(13, 13)

		turnAtNextCheckpointWithoutUnits = army.turnAtNextCheckpoint()

		army.updateCheckpointTurns(self.simulation)

		turnAtNextCheckpointWithUnits = army.turnAtNextCheckpoint()

		# THEN
		self.assertEqual(turnAtNextCheckpointWithoutUnits, -1)  # default
		self.assertEqual(turnAtNextCheckpointWithUnits, 1)

	# ...

	def test_numberOfUnitsAt(self):
		# GIVEN
		operation = Operation(UnitOperationType.foundCity)
		army = Army(self.playerAlexander, operation, UnitFormationType.settlerEscort)

		settler = Unit(HexPoint(5, 5), UnitType.settler, self.playerAlexander)
		self.simulation.addUnit(settler)

		warrior = Unit(HexPoint(5, 6), UnitType.warrior, self.playerAlexander)
		self.simulation.addUnit(warrior)

		# WHEN
		numberOfUnitsAtWithoutUnits = army.numberOfUnitsAt(UnitFormationPosition.civilianSupport)

		army.addUnit(settler, 0)
		army.addUnit(warrior, 1)

		numberOfUnitsAtWithUnits = army.numberOfUnitsAt(UnitFormationPosition.civilianSupport)

		# THEN
		self.assertEqual(numberOfUnitsAtWithoutUnits, 0)  # default
		self.assertEqual(numberOfUnitsAtWithUnits, 1)

	def test_centerOfMass(self):
		# GIVEN
		operation = Operation(UnitOperationType.foundCity)
		army = Army(self.playerAlexander, operation, UnitFormationType.settlerEscort)

		settler = Unit(HexPoint(5, 5), UnitType.settler, self.playerAlexander)
		self.simulation.addUnit(settler)

		warrior = Unit(HexPoint(5, 6), UnitType.warrior, self.playerAlexander)
		self.simulation.addUnit(warrior)

		# WHEN
		centerOfMassWithoutUnits = army.centerOfMass(UnitDomainType.land, self.simulation)

		army.addUnit(settler, 0)
		army.addUnit(warrior, 1)

		centerOfMassWithUnits = army.centerOfMass(UnitDomainType.land, self.simulation)

		# THEN
		self.assertEqual(centerOfMassWithoutUnits, None)  # default
		self.assertEqual(centerOfMassWithUnits, HexPoint(6, 7))

	def test_furthestUnitDistanceTowards(self):
		# GIVEN
		operation = Operation(UnitOperationType.foundCity)
		army = Army(self.playerAlexander, operation, UnitFormationType.settlerEscort)

		settler = Unit(HexPoint(5, 5), UnitType.settler, self.playerAlexander)
		self.simulation.addUnit(settler)

		warrior = Unit(HexPoint(5, 6), UnitType.warrior, self.playerAlexander)
		self.simulation.addUnit(warrior)

		# WHEN
		furthestUnitDistanceTowardsWithoutUnits = army.furthestUnitDistanceTowards(HexPoint(17, 2))

		army.addUnit(settler, 0)
		army.addUnit(warrior, 1)

		furthestUnitDistanceTowardsWithUnits = army.furthestUnitDistanceTowards(HexPoint(17, 2))

		# THEN
		self.assertEqual(furthestUnitDistanceTowardsWithoutUnits, 0)  # default
		self.assertEqual(furthestUnitDistanceTowardsWithUnits, 14)

	def test_isAllOceanGoing(self):
		# GIVEN
		operation = Operation(UnitOperationType.foundCity)
		army = Army(self.playerAlexander, operation, UnitFormationType.settlerEscort)

		settler = Unit(HexPoint(5, 5), UnitType.settler, self.playerAlexander)
		self.simulation.addUnit(settler)

		warrior = Unit(HexPoint(5, 6), UnitType.warrior, self.playerAlexander)
		self.simulation.addUnit(warrior)

		# WHEN
		isAllOceanGoingWithoutUnits = army.isAllOceanGoing(self.simulation)

		army.addUnit(settler, 0)
		army.addUnit(warrior, 1)

		isAllOceanGoingWithUnits = army.isAllOceanGoing(self.simulation)

		# THEN
		self.assertEqual(isAllOceanGoingWithoutUnits, True)  # default
		self.assertEqual(isAllOceanGoingWithUnits, False)

	def test_totalPower(self):
		# GIVEN
		operation = Operation(UnitOperationType.foundCity)
		army = Army(self.playerAlexander, operation, UnitFormationType.settlerEscort)

		settler = Unit(HexPoint(5, 5), UnitType.settler, self.playerAlexander)
		self.simulation.addUnit(settler)

		warrior = Unit(HexPoint(5, 6), UnitType.warrior, self.playerAlexander)
		self.simulation.addUnit(warrior)

		# WHEN
		totalPowerWithoutUnits = army.totalPower()

		army.addUnit(settler, 0)
		army.addUnit(warrior, 1)

		totalPowerWithUnits = army.totalPower()

		# THEN
		self.assertEqual(totalPowerWithoutUnits, 0)  # default
		self.assertEqual(totalPowerWithUnits, 109)

	# ...

	def test_furthestUnitDistance(self):
		# GIVEN
		operation = Operation(UnitOperationType.foundCity)
		army = Army(self.playerAlexander, operation, UnitFormationType.settlerEscort)

		settler = Unit(HexPoint(5, 5), UnitType.settler, self.playerAlexander)
		self.simulation.addUnit(settler)

		warrior = Unit(HexPoint(5, 6), UnitType.warrior, self.playerAlexander)
		self.simulation.addUnit(warrior)

		# WHEN
		furthestUnitDistanceWithoutUnits = army.furthestUnitDistance(HexPoint(7, 7))

		army.addUnit(settler, 0)
		army.addUnit(warrior, 1)

		furthestUnitDistanceWithUnits = army.furthestUnitDistance(HexPoint(7, 7))

		# THEN
		self.assertEqual(furthestUnitDistanceWithoutUnits, 0)  # default
		self.assertEqual(furthestUnitDistanceWithUnits, 3)

	def test_movementRate(self):
		# GIVEN
		operation = Operation(UnitOperationType.foundCity)
		army = Army(self.playerAlexander, operation, UnitFormationType.settlerEscort)

		settler = Unit(HexPoint(5, 5), UnitType.settler, self.playerAlexander)
		self.simulation.addUnit(settler)

		warrior = Unit(HexPoint(5, 6), UnitType.warrior, self.playerAlexander)
		self.simulation.addUnit(warrior)

		# WHEN
		movementWithoutUnits = army.movementRate(self.simulation)

		army.addUnit(settler, 0)
		army.addUnit(warrior, 1)

		movementWithUnits = army.movementRate(self.simulation)

		# THEN
		self.assertEqual(movementWithoutUnits, 2)  # default
		self.assertEqual(movementWithUnits, 2)
