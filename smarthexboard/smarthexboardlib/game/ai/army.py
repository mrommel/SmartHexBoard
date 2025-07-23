import sys
import uuid
from typing import Optional, List

from smarthexboard.smarthexboardlib.game.ai.militaryTypes import UnitFormationType, ArmyState, UnitFormationPosition
from smarthexboard.smarthexboardlib.map import constants
from smarthexboard.smarthexboardlib.map.base import HexPoint, HexArea
from smarthexboard.smarthexboardlib.map.types import UnitDomainType


class ArmyFormationSlotConstants:
	unknownTurnAtCheckpoint = -1
	notIncludingInOperation = -2


class ArmyFormationSlot:
	def __init__(self, unit=None, estimatedTurnAtCheckpoint: int = ArmyFormationSlotConstants.unknownTurnAtCheckpoint,
	             startedOnOperation: bool = False):
		self.unit = unit
		self.estimatedTurnAtCheckpoint = estimatedTurnAtCheckpoint
		self.startedOnOperation = startedOnOperation

	def __repr__(self):  # pragma: no cover
		return f'ArmyFormationSlot({self.unit}, turn@checkpoint: {self.estimatedTurnAtCheckpoint}, started: {self.startedOnOperation})'

	def turnAtCheckpoint(self) -> int:
		return self.estimatedTurnAtCheckpoint

	def setTurnAtCheckpoint(self, value: int):
		self.estimatedTurnAtCheckpoint = value

	def hasStartedOnOperation(self) -> bool:
		return self.startedOnOperation

	def setStartedOnOperation(self, value: bool):
		self.startedOnOperation = value


class Army:
	def __init__(self, player, operation, formation: UnitFormationType):
		self.goal: HexPoint = constants.invalidHexPoint
		self.muster: HexPoint = constants.invalidHexPoint
		self.position: HexPoint = constants.invalidHexPoint

		self.area: Optional[HexArea]
		self.formationEntries: List[ArmyFormationSlot] = []

		self.identifier = str(uuid.uuid4())
		self.owner = player
		self.operation = operation
		self.formation: UnitFormationType = formation
		self.domain: UnitDomainType = UnitDomainType.land
		self.state: ArmyState = ArmyState.waitingForUnitsToReinforce

		# Build all the formation entries
		for _ in range(len(self.formation.slots())):
			self.formationEntries.append(ArmyFormationSlot())

	def __eq__(self, other):
		if isinstance(other, Army):
			return self.identifier == other.identifier

		raise Exception(f'One simply cannot compare Armies and {type(other)}s')

	def disableSlot(self, slot):
		raise Exception("not implemented yet")

	def addUnit(self, unit, index: int):
		self.formationEntries[index].unit = unit
		unit.assignTo(self)

	def removeUnit(self, unit) -> bool:
		"""Remove a unit from the army"""
		wasOneOrMoreRemoved: bool = False

		for slot in self.formationEntries:
			if slot.unit is not None and slot.unit == unit:
				# Clears unit's army ID and erase from formation entries
				unit.army = None
				slot.unit = None
				wasOneOrMoreRemoved = True

				# Tell the associate operation that a unit was lost
				self.operation.unitWasRemoved(self, slot)

		return wasOneOrMoreRemoved

	def kill(self):
		"""Delete the army"""
		for entry in self.formationEntries:
			if entry.unit is not None:
				entry.unit.assignTo(None)

	def doTurn(self, simulation):
		"""Process another turn for the army"""
		self.doDelayedDeath()

	def doDelayedDeath(self) -> bool:
		"""Kill off the army if waiting to die (returns true if army was killed)"""
		if self.numberOfSlotsFilled() == 0 and self.state != ArmyState.waitingForUnitsToReinforce:
			self.kill()
			return True

		return False

	def numberOfSlotsFilled(self) -> int:
		"""How many slots do we currently have filled?"""
		rtnValue = 0

		for formationEntry in self.formationEntries:
			if formationEntry.unit is not None:
				rtnValue += 1

		return rtnValue

	def numberOfFormationEntries(self) -> int:
		"""How many slots are there in this formation if filled"""
		return len(self.formationEntries)

	def units(self):  # -> [Unit]:
		"""all units without order or slot relation"""
		returnArray = []

		for entry in self.formationEntries:
			if entry.unit is not None:
				returnArray.append(entry.unit)

		return returnArray

	def unitAt(self, slotIndex: int):  # -> Optional[Unit]:
		return self.formationEntries[slotIndex].unit

	def setEstimatedTurn(self, turn: int, slotId: int, simulation):
		turnAtCheckpoint: int = 0

		if turn == ArmyFormationSlotConstants.notIncludingInOperation or \
			turn == ArmyFormationSlotConstants.unknownTurnAtCheckpoint:
			turnAtCheckpoint = turn
		else:
			turnAtCheckpoint = simulation.currentTurn + turn

		self.formationEntries[slotId].setTurnAtCheckpoint(turnAtCheckpoint)
		return

	def turnAtNextCheckpoint(self) -> int:
		"""What turn will the army as a whole arrive at target?"""
		rtnValue = ArmyFormationSlotConstants.notIncludingInOperation

		for formationEntry in self.formationEntries:
			if formationEntry.estimatedTurnAtCheckpoint == ArmyFormationSlotConstants.unknownTurnAtCheckpoint:
				return ArmyFormationSlotConstants.unknownTurnAtCheckpoint
			elif formationEntry.estimatedTurnAtCheckpoint > rtnValue:
				rtnValue = formationEntry.estimatedTurnAtCheckpoint

		return rtnValue

	def updateCheckpointTurns(self, simulation):
		for (index, formationEntry) in enumerate(self.formationEntries):
			# No re-estimate for units being built
			if formationEntry.unit is not None:
				turnsToReachCheckpoint = formationEntry.unit.turnsToReach(self.position, simulation)
				if turnsToReachCheckpoint < sys.maxsize:
					self.setEstimatedTurn(turnsToReachCheckpoint, index, simulation)

		return

	def numberOfUnitsAt(self, position: UnitFormationPosition) -> int:
		"""How many units of this type are in army?"""
		rtnValue = 0

		for (index, formationEntry) in enumerate(self.formationEntries):
			if formationEntry.unit is not None:
				if formationEntry.unit.moves() > 0:
					slot = self.formation.slots()[index]
					if slot.position == position:
						rtnValue += 1

		return rtnValue

	def centerOfMass(self, domain: UnitDomainType, simulation) -> Optional[HexPoint]:
		"""Get center of mass of units in army (account for world wrap!)"""
		totalX = 0
		totalY = 0

		worldWidth = simulation.mapSize().size().width()
		referenceUnitX = -1
		numUnits = 0

		rtnValue: Optional[HexPoint] = None

		for unit in self.units():
			if unit is not None:
				# first unit will set the ref
				if referenceUnitX == -1:
					referenceUnitX = unit.location.x

				worldWrapAdjust: bool = False
				diff = unit.location.x - referenceUnitX
				if abs(diff) > worldWidth / 2:
					worldWrapAdjust = True

				if worldWrapAdjust:
					totalX += unit.location.x + worldWidth
				else:
					totalX += unit.location.x

				totalY += unit.location.y
				numUnits += 1

		if numUnits > 0:
			averageX = int((totalX + (numUnits / 2)) / numUnits)
			if averageX >= worldWidth:
				averageX -= worldWidth

			averageY = int((totalY + (numUnits / 2)) / numUnits)

			rtnValue = HexPoint(averageX, averageY)

		# Domain check
		if domain != UnitDomainType.none and rtnValue is not None:
			rtnPlot = simulation.tileAt(rtnValue)
			if rtnPlot is None:
				raise Exception("cant get rtnValue plot")

			if rtnPlot.isWater() and domain == UnitDomainType.land or not rtnPlot.isWater() and domain == UnitDomainType.sea:
				# Find an adjacent plot that works
				for loopPoint in rtnValue.neighbors():
					loopPlot = simulation.tileAt(loopPoint)
					if loopPlot is None:
						continue

					if loopPlot.isWater() and domain == UnitDomainType.sea or not loopPlot.isWater() and domain == UnitDomainType.land:
						return loopPoint

				# Try two plots out if really having problems
				for loopPoint in rtnValue.areaWithRadius(2):

					if loopPoint.distance(rtnValue) == 2:
						loopPlot = simulation.tileAt(loopPoint)
						if loopPlot is None:
							continue

						if loopPlot.isWater() and domain == UnitDomainType.sea or not loopPlot.isWater() and domain == UnitDomainType.land:
							return loopPoint

				# Give up - just use location of first unit
				rtnValue = self.unitAt(0).location

		return rtnValue

	def furthestUnitDistanceTowards(self, point: HexPoint) -> int:
		"""Return distance from this plot of unit in army farthest away"""
		largestDistance = 0

		for unit in self.units():
			distance = point.distance(unit.location)
			if distance > largestDistance:
				largestDistance = distance

		return int(largestDistance)

	def isAllOceanGoing(self, simulation) -> bool:
		"""Can all units in this army move on ocean?"""
		for unit in self.units():
			if unit.domain() != UnitDomainType.sea and not unit.canEmbarkInto(None, simulation):
				return False

		# If can move over ocean, not a coastal vessel
		# FIXME if unit.isImpassable(terrain: .ocean) {
		#	return False

		return True

	def totalPower(self) -> int:
		"""Total unit power"""
		sumOfPower = 0

		for unit in self.units():
			sumOfPower += unit.power()

		return sumOfPower

	def canTacticalAIInterrupt(self) -> bool:
		"""Is this part of an operation that allows units to be poached by tactical AI?"""
		# If the operation is still assembling, by all means interrupt it
		if self.state == ArmyState.waitingForUnitsToReinforce or \
			self.state == ArmyState.waitingForUnitsToCatchUp:
			return True

		if self.operation is not None:
			return self.operation.canTacticalAIInterruptOperation()

		return False

	def furthestUnitDistance(self, point: HexPoint) -> int:
		"""Return distance from this plot of unit in army farthest away"""
		largestDistance = 0

		for unit in self.units():
			distance = point.distance(unit.location)

			if distance > largestDistance:
				largestDistance = int(distance)

		return largestDistance

	def movementRate(self, simulation) -> int:
		"""Find average speed of units in army"""
		movementAverage: int = 2  # A reasonable default
		numUnits: int = 0
		totalMovementAllowance: int = 0

		for unit in self.units():
			numUnits += 1
			totalMovementAllowance += unit.baseMoves(simulation=simulation)

		if numUnits > 0:
			movementAverage = int((totalMovementAllowance + int(numUnits / 2)) / numUnits)

		return movementAverage
