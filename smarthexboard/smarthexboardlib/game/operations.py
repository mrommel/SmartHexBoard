import logging
import sys
from typing import Optional, List

from smarthexboard.smarthexboardlib.core.base import InvalidEnumError, WeightedBaseList
from smarthexboard.smarthexboardlib.game.ai.army import Army, ArmyFormationSlotConstants
from smarthexboard.smarthexboardlib.game.ai.militaryTypes import UnitFormationSlot, UnitFormationType, OperationMoveType, OperationStateType, \
	OperationStateReason, ArmyState, TemporaryZone, TacticalTargetType
from smarthexboard.smarthexboardlib.game.unitMissions import UnitMission
from smarthexboard.smarthexboardlib.game.unitTypes import UnitOperationType, UnitTaskType, UnitMapType, UnitMissionType
from smarthexboard.smarthexboardlib.map.base import HexArea, HexPoint
from smarthexboard.smarthexboardlib.map.improvements import ImprovementType
from smarthexboard.smarthexboardlib.map.path_finding.finder import AStarPathfinder
from smarthexboard.smarthexboardlib.map.path_finding.path import HexPath
from smarthexboard.smarthexboardlib.map.types import UnitMovementType, UnitDomainType, MapSize, TerrainType
from smarthexboard.smarthexboardlib.utils.base import lastOrNone


class OperationSlot:
	def __init__(self, operation, army, slot: UnitFormationSlot, index: int):
		self.operation = operation
		self.army = army
		self.slot: UnitFormationSlot = slot
		self.index: int = index


class OperationSearchUnit:
	def __init__(self, unit, distance: int):
		self.unit = unit
		self.distance = distance

	def __lt__(self, other):
		if isinstance(other, OperationSearchUnit):
			return self.distance < other.distance

		raise Exception(f'Cannot compare OperationSearchUnit and {type(other)}')


class Operation:
	def __init__(self, operationType: UnitOperationType):
		self.operationType: UnitOperationType = operationType
		self.moveType: OperationMoveType = OperationMoveType.none
		self.state: OperationStateType = OperationStateType.none
		self.stateReason: OperationStateReason = OperationStateReason.none
		self.player = None
		self.enemy = None
		self.defaultArea: Optional[HexArea] = None
		self.shouldReplaceLossesWithReinforcements: bool = False
		self.lastTurnMovedValue: int = -1

		# positions
		self.startPosition: Optional[HexPoint] = None
		self.musterPosition: Optional[HexPoint] = None
		self.targetPosition: Optional[HexPoint] = None

		self.army: Optional[Army] = None
		self.listOfUnitsWeStillNeedToBuild = []
		self.listOfUnitsCitiesHaveCommittedToBuild = []

		self.reset()

	def canTacticalAIInterruptOperation(self) -> bool:
		return False

	def __eq__(self, other):
		if isinstance(other, Operation):
			if self.operationType != other.operationType:
				return False

			if self.moveType != other.moveType:
				return False

			if self.state != other.state:
				return False

			if self.stateReason != other.stateReason:
				return False

			if self.player != other.player:
				return False

			return True

		raise Exception(f'One simply cannot compare Operations and {type(other)}s')

	def initialize(self, player, enemy, area: Optional[HexArea], target: Optional[HexPoint], muster: Optional[HexPoint], simulation):
		self.player = player
		self.enemy = enemy
		self.defaultArea = area

		self.updateTargetTo(target)
		self.musterPosition = muster

		# create the armies that are needed and set the state to ARMYAISTATE_WAITING_FOR_UNITS_TO_REINFORCE
		self.buildListOfUnitsWeStillNeedToBuild()
		_ = self.grabUnitsFromTheReserves(None, None, simulation)

		#
		self.setLastTurnMoved(simulation.currentTurn)

	def doTurn(self):
		"""Log current status of the operation"""
		self.logOperationStatus()

	def unitWasRemoved(self, army, slot: UnitFormationSlot):
		"""Handles notification that a unit in this operation was lost. Can be overridden if needed"""
		# For now, response is based on phase of operation
		if self.state == OperationStateType.aborted or self.state == OperationStateType.successful:
			# AI_OPERATION_STATE_ABORTED
			# AI_OPERATION_STATE_SUCCESSFUL_FINISH
			pass
		elif self.state == OperationStateType.recruitingUnits:
			# If recruiting units, read this unit to the list of what we need
			slotIndex = -1
			for index, formationSlot in enumerate(army.formation.slots()):
				if formationSlot == slot:
					slotIndex = index

			if slotIndex == -1:
				raise Exception(f'cannot find slot {slot} in formation {army.formation}')

			operationSlot = OperationSlot(self, self.army, slot, slotIndex)
			self.listOfUnitsWeStillNeedToBuild.append(operationSlot)
		elif self.state == OperationStateType.gatheringForces or self.state == OperationStateType.movingToTarget or \
			self.state == OperationStateType.atTarget:
			# AI_OPERATION_STATE_GATHERING_FORCES:
			# AI_OPERATION_STATE_MOVING_TO_TARGET:
			# AI_OPERATION_STATE_AT_TARGET:
			# If down below half strength, abort
			if self.army is not None and self.army.formation is not None:
				if self.army.numberOfSlotsFilled() <= 0 or \
					self.army.numberOfSlotsFilled() < self.army.formation.numberOfFormationSlotEntries() / 2:
					# Abort
					self.state = OperationStateType.aborted  # AI_OPERATION_STATE_ABORTED;
					self.stateReason = OperationStateReason.halfStrength  # AI_ABORT_HALF_STRENGTH;

		return

	def updateTargetTo(self, target: Optional[HexPoint]):
		if target is not None and not isinstance(target, HexPoint):
			raise Exception(f'target mut be None or HexPoint but got {type(target)} instead')

		self.targetPosition = target

	def isAllNavalOperation(self) -> bool:
		return False

	def isMixedLandNavalOperation(self) -> bool:
		return False

	def lastTurnMoved(self) -> int:
		return self.lastTurnMovedValue

	def setLastTurnMoved(self, lastTurnMoved: int):
		self.lastTurnMovedValue = lastTurnMoved

	def formation(self, simulation) -> UnitFormationType:
		return UnitFormationType.none

	def checkOnTarget(self, simulation) -> bool:
		"""See if armies are ready to hand off units to the tactical AI (and do so if ready)"""
		if self.army is None:
			return False

		if self.moveType == OperationMoveType.none:
			# NOOP
			return False

		elif self.moveType == OperationMoveType.singleHex:
			if self.army is not None:
				if self.army.numberOfSlotsFilled() >= 1:
					civilian = self.army.unitAt(0)

					if self.state == OperationStateType.none:
						# NOOP
						return False
					elif self.state == OperationStateType.aborted:
						# NOOP
						return False
					elif self.state == OperationStateType.gatheringForces:
						if self.army.numberOfSlotsFilled() == 1:
							self.armyInPosition(simulation)
							return True
						else:
							escort = self.army.unitAt(1)
							if escort.location == civilian.location:
								self.armyInPosition(simulation)
								return True
					elif self.state == OperationStateType.movingToTarget:
						self.armyInPosition(simulation)
						return True
					elif self.state == OperationStateType.recruitingUnits or self.state == OperationStateType.atTarget or \
						self.state == OperationStateType.successful:
						self.armyInPosition(simulation)
						return False
				else:
					raise Exception("Found an escort operation with no units in it.")

		elif self.moveType == OperationMoveType.enemyTerritory:
			# Let each army perform its own check
			gatheredTolerance = self.gatherTolerance(self.army, self.musterPosition, simulation)
			if self.army is not None:
				if self.army.numberOfSlotsFilled() >= 1:
					if self.state == OperationStateType.none:
						# NOOP
						return False
					elif self.state == OperationStateType.aborted:
						# NOOP
						return False
					elif self.state == OperationStateType.gatheringForces:
						domain: UnitDomainType = UnitDomainType.sea if self.isAllNavalOperation() or self.isMixedLandNavalOperation() else UnitDomainType.land
						centerOfMass: Optional[HexPoint] = self.army.centerOfMass(domain, simulation)

						if centerOfMass is not None and self.musterPosition is not None:
							if centerOfMass.distance(self.musterPosition) <= gatheredTolerance and \
								self.army.furthestUnitDistance(self.musterPosition) <= gatheredTolerance * 3 / 2:
								self.armyInPosition(simulation)
								return True
					elif self.state == OperationStateType.movingToTarget:
						domain: UnitDomainType = UnitDomainType.sea if self.isAllNavalOperation() or self.isMixedLandNavalOperation() else UnitDomainType.land
						centerOfMass: Optional[HexPoint] = self.army.centerOfMass(domain, simulation)

						if centerOfMass is not None and self.targetPosition is not None:
							if centerOfMass.distance(self.targetPosition) <= gatheredTolerance and \
								self.army.furthestUnitDistanceTowards(self.targetPosition) <= gatheredTolerance * 3 / 2:
								self.armyInPosition(simulation)
								return True

					elif self.state == OperationStateType.recruitingUnits or self.state == OperationStateType.atTarget or \
						self.state == OperationStateType.successful:
						# NOOP
						return False

				else:
					raise Exception("Found an army operation with no units in it.")
		elif self.moveType == OperationMoveType.navalEscort:
			# Let each army perform its own check
			gatheredTolerance = self.gatherTolerance(self.army, self.musterPosition, simulation)

			if self.army is not None:
				if self.army.numberOfSlotsFilled() >= 1:
					if self.state == OperationStateType.none:
						# NOOP
						return False
					elif self.state == OperationStateType.aborted:
						# NOOP
						return False
					elif self.state == OperationStateType.gatheringForces:
						centerOfMass: Optional[HexPoint] = self.army.centerOfMass(UnitDomainType.sea, simulation)

						if centerOfMass is not None and self.musterPosition is not None:
							if centerOfMass.distance(self.musterPosition) <= gatheredTolerance and self.army.furthestUnitDistanceTowards(self.musterPosition) <= gatheredTolerance * 3:
								self.armyInPosition(simulation)
								return True
					elif self.state == OperationStateType.movingToTarget:
						centerOfMass: Optional[HexPoint] = self.army.centerOfMass(UnitDomainType.sea, simulation)

						if centerOfMass is not None and self.targetPosition is not None:
							if centerOfMass.distance(self.targetPosition) <= gatheredTolerance and self.army.furthestUnitDistanceTowards(self.targetPosition) <= gatheredTolerance * 3:
								self.armyInPosition(simulation)
								return True
					elif self.state == OperationStateType.recruitingUnits or self.state == OperationStateType.atTarget or \
						self.state == OperationStateType.successful:
						# NOOP
						return False
				else:
					raise Exception("Found an army operation with no units in it.")
		elif self.moveType == OperationMoveType.freeformNaval:
			# Let each army perform its own check
			gatheredTolerance = self.gatherTolerance(self.army, self.musterPosition, simulation)

			if self.army is not None:
				if self.army.numberOfSlotsFilled() >= 1:
					if self.state == OperationStateType.none:
						# NOOP
						return False
					elif self.state == OperationStateType.aborted:
						# NOOP
						return False
					elif self.state == OperationStateType.gatheringForces:
						centerOfMass: Optional[HexPoint] = self.army.centerOfMass(UnitDomainType.sea, simulation)

						if centerOfMass is not None and self.musterPosition is not None:
							if centerOfMass.distance(self.musterPosition) <= gatheredTolerance and self.army.furthestUnitDistanceTowards(self.musterPosition) <= gatheredTolerance * 3 / 2:
								self.armyInPosition(simulation)
								return True
					elif self.state == OperationStateType.movingToTarget:
						# Never in a final position
						return False
					elif self.state == OperationStateType.recruitingUnits or self.state == OperationStateType.atTarget or \
						self.state == OperationStateType.successful:
						# NOOP
						return False
		elif self.moveType == OperationMoveType.rebase:
			# NOOP
			return False

		return False

	def grabUnitsFromTheReserves(self, musterPosition: Optional[HexPoint], targetPosition: Optional[HexPoint],
								 simulation) -> bool:
		"""Assigns available units to our operation. Returns true if all needed units assigned."""
		returnVal = True

		# Copy over the list
		secondList: List[OperationSlot] = []
		for item in self.listOfUnitsWeStillNeedToBuild:
			secondList.append(item)

		# Clear main list
		self.listOfUnitsWeStillNeedToBuild = []

		for item in secondList:
			(success, required) = self.findBestFitReserveUnit(item, simulation)

			# If any fail, check to see if they were required
			if not success:
				if required:
					# Return false to say that operation is not ready to roll yet
					returnVal = False

					# And add them back to the list of units needed
					self.listOfUnitsWeStillNeedToBuild.append(item)
				else:
					# this slot will not be filled(but is not required)
					self.army.disableSlot(item.slot)

		return returnVal

	def buildListOfUnitsWeStillNeedToBuild(self):
		self.listOfUnitsCitiesHaveCommittedToBuild = []
		self.listOfUnitsWeStillNeedToBuild = []

		if self.army is not None:
			# if it is still waiting on initial units
			if self.army.state == ArmyState.waitingForUnitsToReinforce:
				index = 0
				for slot in self.army.formation.slots():
					operationSlot = OperationSlot(self, self.army, slot, index)
					self.listOfUnitsWeStillNeedToBuild.append(operationSlot)
					index += 1

		return

	def findBestFitReserveUnit(self, slot: OperationSlot, simulation) -> (bool, bool):
		searchList: List[OperationSearchUnit] = []

		for loopUnit in simulation.unitsOf(self.player):
			# Make sure he's not needed by the tactical AI or already in an army or scouting
			if loopUnit.army() is None and loopUnit.task() != UnitTaskType.explore and loopUnit.task() != UnitTaskType.exploreSea:
				# Is this unit one of the requested types?
				# if unit.task() == slot.slot.primaryUnitTask or unit.task() == slot.slot.secondaryUnitTask:
				if loopUnit.hasTask(slot.slot.primaryUnitTask) or loopUnit.hasTask(slot.slot.secondaryUnitTask):
					# Is his health okay?
					if not loopUnit.isCombatUnit() or loopUnit.healthPoints() >= 75:  # AI_OPERATIONAL_PERCENT_HEALTH_FOR_OPERATION
						if (not self.isAllNavalOperation() and not self.isMixedLandNavalOperation()) or \
							loopUnit.domain() == UnitDomainType.sea or loopUnit.canEverEmbark():
							if self.musterPosition is not None:
								distance = self.musterPosition.distance(loopUnit.location)
								if loopUnit.domain() == UnitDomainType.land and simulation.areaOf(
									loopUnit.location) != simulation.areaOf(self.musterPosition):
									distance *= 2
							elif self.targetPosition is not None:
								distance = self.targetPosition.distance(loopUnit.location)
							else:
								distance = sys.maxsize

							searchList.append(OperationSearchUnit(loopUnit, distance))

		bestUnit = self.closestUnitIn(searchList, needToCheckTarget=True, simulation=simulation)

		# Did we find one?
		if bestUnit is not None:
			self.army.addUnit(bestUnit, slot.index)
			return True, True

		# If not required, let our calling routine know that
		return True, slot.slot.required

	def closestUnitIn(self, searchList: List[OperationSearchUnit], needToCheckTarget: bool,
					  simulation):  # -> Optional[Unit]:
		bestUnit = None
		bestDistance: float = float(UnitMovementType.max.value)

		sortedSearchList = sorted(searchList)  # .sorted(by: { $0.distance < $1.distance})

		for searchUnit in sortedSearchList:
			unit = searchUnit.unit
			if unit is None:
				continue

			pathFinderDataSource = simulation.ignoreUnitsPathfinderDataSource(
				unit.movementType(),
				searchUnit.unit.player,
				canEmbark=self.player.canEmbark(),
				canEnterOcean=self.player.canEnterOcean()
			)
			pathFinder = AStarPathfinder(pathFinderDataSource)

			searchUnitLocation = searchUnit.unit.location
			if searchUnitLocation is not None:
				pathDistance = 10000

				# Now loop through the units, using the pathfinder to do the final evaluation
				if self.musterPosition is not None:
					path = pathFinder.shortestPath(searchUnitLocation, self.musterPosition)
					if path is not None:
						pathDistance = len(path.points())
					else:
						continue

				if needToCheckTarget:
					if self.targetPosition is not None:
						path = pathFinder.shortestPath(searchUnitLocation, self.targetPosition)
						if path is not None:
							pathDistance = len(path.points())
						else:
							continue

				# Reasonably close?
				if pathDistance <= float(searchUnit.distance) and pathDistance <= bestDistance:
					bestUnit = searchUnit.unit

				if pathDistance < bestDistance:
					bestUnit = searchUnit.unit
					bestDistance = pathDistance

				# Were we far away?  If so, this is probably the best we are going to do
				if searchUnit.distance >= 8:  # AI_HOMELAND_ESTIMATE_TURNS_DISTANCE
					break

		return bestUnit

	def doDelayedDeath(self, simulation) -> bool:
		"""Delete the operation if marked to go away"""
		if self.shouldAbort(simulation):
			if self.state == OperationStateType.successful:
				self.kill(OperationStateReason.success)
			else:
				self.kill(OperationStateReason.killed)
			
			return True

		return False

	def shouldAbort(self, simulation) -> bool:
		# Mark units in successful operation
		if self.state == OperationStateType.successful:
			for unit in self.army.units():
				unit.setDeployFromOperationTurnTo(simulation.currentTurn)

		return self.state == OperationStateType.aborted or self.state == OperationStateType.successful

	def kill(self, reason: OperationStateReason):
		"""Perform the deletion of this operation"""
		if (self.state == OperationStateType.aborted or self.state == OperationStateType.successful) and \
			self.stateReason == OperationStateReason.none:
			self.stateReason = reason

		self.logOperationEnd()
		self.player.deleteOperation(self)
		self.uninit()

	def uninit(self):
		"""Delete allocated objects"""
		# hopefully if this has been init'ed this should not happen
		if self.player is not None:
			# remove the army (which should, in turn, free up its units for other tasks)
			if self.army is not None:
				self.army.kill()
				self.player.armies.removeArmy(self.army)

		# clear out the lists
		self.army = None
		self.listOfUnitsWeStillNeedToBuild = []
		self.listOfUnitsCitiesHaveCommittedToBuild = []

		self.reset()

	def reset(self):
		self.player = None
		self.state = OperationStateType.aborted
		self.stateReason = OperationStateReason.none
		self.targetPosition = None
		self.musterPosition = None
		self.startPosition = None
		self.moveType = OperationMoveType.none
		self.lastTurnMovedValue = -1
		self.defaultArea = None
		self.army = None

	def armyInPosition(self, simulation):
		# raise Exception(f"not implemented yet - should be implemented by child class: {type(self)}")
		stateChanged: bool = False

		if self.state == OperationStateType.gatheringForces:  # AI_OPERATION_STATE_GATHERING_FORCES
			# If we were gathering forces, we're all set to move out
			self.state = OperationStateType.movingToTarget  # AI_OPERATION_STATE_MOVING_TO_TARGET
			stateChanged = True
			self.army.state = ArmyState.movingToDestination  # ARMYAISTATE_MOVING_TO_DESTINATION
		elif self.state == OperationStateType.movingToTarget:  # AI_OPERATION_STATE_MOVING_TO_TARGET
			# If we are moving to our target, check and see if we are there
			if self.army is not None and self.targetPosition is not None and self.army.position == self.targetPosition:
				self.state = OperationStateType.atTarget  # AI_OPERATION_STATE_AT_TARGET;
				stateChanged = True
		elif self.state == OperationStateType.aborted or self.state == OperationStateType.recruitingUnits or \
			self.state == OperationStateType.atTarget or self.state == OperationStateType.successful:
			pass
		else:
			raise Exception(f'State {self.state} not handled')

		return stateChanged

	def gatherTolerance(self, army, position: Optional[HexPoint], simulation) -> int:
		validPlotsNearby: int = 0
		tacticalMap = simulation.tacticalAnalysisMap()

		# Find out how many units are trying to gather
		numUnits = army.numberOfSlotsFilled()

		# If not more than 1, zero tolerance is fine (we should get the unit to the gather point)
		if numUnits < 1:
			return 0

		radius = 1 if numUnits <= 2 else (2 if numUnits <= 6 else 3)
		for pt in position.areaWithRadius(radius):
			if not simulation.valid(pt):
				continue

			cell = tacticalMap.plots.values[pt.y][pt.x]

			if (self.isMixedLandNavalOperation() and cell.canUseForOperationGathering()) or \
				cell.canUseForOperationGatheringCheckWater(self.isAllNavalOperation()):

				if (self.isMixedLandNavalOperation() or self.isAllNavalOperation()) and not self.army.isAllOceanGoing(simulation) and cell.ocean:
					continue

				validPlotsNearby += 1

		# Find more valid plots than units?
		if validPlotsNearby > numUnits:
			# If so, just use normal range for this many units
			return radius
		else:
			# Something constrained here, give ourselves a lot of leeway
			return 3

	def setDefaultArea(self, area: Optional[HexArea]):
		self.defaultArea = area

	def operationStartCity(self, simulation):
		"""Find the area where our operation is occurring"""
		startCityValue = simulation.cityAt(self.startPosition)
		if startCityValue is not None:
			return startCityValue

		bestTotal: int = 0
		bestArea: Optional[HexArea] = None
		bestCity = None

		# Do we still have a capital?
		capitalCity = simulation.capitalOf(self.player)

		if capitalCity is not None:
			return capitalCity

		# No capital, find the area with the most combined cities between us and our enemy (and need at least 1 from each)
		for loopArea in simulation.areas():
			if loopArea.isWater():
				continue

			myCities = simulation.citiesInAreaOf(self.player, loopArea)
			if len(myCities) > 0:
				if self.enemy is not None and not self.enemy.isBarbarian():
					enemyCities = simulation.citiesInAreaOf(self.enemy, loopArea)
					if len(enemyCities) == 0:
						continue
				else:
					enemyCities = 0

				if (myCities + enemyCities) > bestTotal:
					bestTotal = myCities + enemyCities
					bestArea = loopArea

		if bestArea is not None:
			# Know which continent to use, now use our largest city there as the start city
			bestTotal = 0
			for loopCity in simulation.citiesOf(self.player):
				if loopCity.area() == bestArea:
					if loopCity.population() > bestTotal:
						bestTotal = loopCity.population()
						bestCity = loopCity

			return bestCity

		return None

	def numberOfUnitsNeededToBeBuilt(self) -> int:
		return len(self.listOfUnitsWeStillNeedToBuild)

	def isCivilianRequired(self) -> bool:
		raise Exception('niy')

	def percentFromMusterPointToTarget(self, simulation) -> int:
		"""Report percentage distance traveled from muster point to target (using army that is furthest along)"""
		rtnValue: int = 0
		if self.state == OperationStateType.gatheringForces or self.state == OperationStateType.aborted or \
			self.state == OperationStateType.recruitingUnits:
			return 0
		elif self.state == OperationStateType.atTarget or self.state == OperationStateType.successful:
			return 100
		elif self.state == OperationStateType.movingToTarget:
			# Let each army perform its own update
			if self.army is not None:
				if self.army.goal is not None:
					iDistanceMusterToTarget: int = 0
					iDistanceCurrentToTarget: int = 0

					domain: UnitDomainType = UnitDomainType.sea if self.isAllNavalOperation() or self.isMixedLandNavalOperation() else UnitDomainType.land

					centerOfMassValue: Optional[HexPoint] = self.army.centerOfMass(domain, simulation)

					if centerOfMassValue is None:
						return 0

					# Use the step pathfinder to compute distance
					pathFinderDataSource = simulation.ignoreUnitsPathfinderDataSource(
						UnitMovementType.walk if domain == UnitDomainType.land else UnitMovementType.swim,
						self.player,
						canEmbark=self.player.canEmbark(),
						canEnterOcean=self.player.canEnterOcean()
					)
					pathFinder = AStarPathfinder(pathFinderDataSource)

					pathFromMusterToTarget = pathFinder.shortestPath(self.musterPosition, self.targetPosition)
					pathFromCurrentToTarget = pathFinder.shortestPath(centerOfMassValue, self.targetPosition)

					iDistanceMusterToTarget = 0 if pathFromMusterToTarget is None else len(pathFromMusterToTarget.points())
					iDistanceCurrentToTarget = 0 if pathFromCurrentToTarget is None else len(pathFromCurrentToTarget.points())

					if iDistanceMusterToTarget <= 0:
						return 0
					elif iDistanceCurrentToTarget <= 2:
						# If within 2 of the final goal, consider ourselves there
						return 100
					else:
						iTempValue: int = 100 - int(100 * iDistanceCurrentToTarget / iDistanceMusterToTarget)
						if iTempValue > rtnValue:
							rtnValue = iTempValue
				else:
					raise Exception("Operational AI army without a goal plot! Send save to MiRo")

		return rtnValue

	def logOperationStart(self):
		"""Log that an operation has started"""
		strTemp = f'=== Operation: {self.player.name()} ({self.player.leader.civilization().title()}), '
		strTemp += f'{self.operationType}, '
		strTemp += f'Started, Army: {self.army.identifier[0:8]}, '
		strTemp += f'Units Recruited: {self.army.numberOfSlotsFilled()}, '
		strTemp += f'Max Formation Size: {self.army.numberOfFormationEntries()}, '
		strTemp += f'{self.state}'
		logging.info(strTemp)

	def logOperationStatus(self):
		strTemp = f'=== Operation: {self.player.name()} ({self.player.leader.civilization().title()}), '
		strTemp += f'{self.operationType}, '

		if self.state == OperationStateType.aborted:
			strTemp += 'Aborted'
		elif self.state == OperationStateType.recruitingUnits:
			strTemp += f'Recruiting Units, Army: {self.army.identifier[0:8]}, Muster Turn: {self.army.turnAtNextCheckpoint()}, SLOT DETAIL: '
			for formationEntry in self.army.formationEntries:
				if formationEntry.turnAtCheckpoint() == ArmyFormationSlotConstants.unknownTurnAtCheckpoint:
					strTemp += "No Info, "
				elif formationEntry.turnAtCheckpoint() == ArmyFormationSlotConstants.notIncludingInOperation:
					strTemp += "Skipping, "
				elif formationEntry.unit is None:
					strTemp += f"Training - Turn {formationEntry.turnAtCheckpoint()}, "
				elif formationEntry.hasStartedOnOperation():
					if formationEntry.unit is not None:
						strTemp += f"Gathering at {formationEntry.unit.location}, "
				else:
					if formationEntry.unit is not None:
						strTemp += f"{formationEntry.unit.name()} - Turn {formationEntry.turnAtCheckpoint()}, "
		elif self.state == OperationStateType.gatheringForces:
			strTemp += f"Gathering Forces, Army: {self.army.identifier[0:8]}, Gather units at {self.army.position}, "
			for formationEntry in self.army.formationEntries:
				if formationEntry.unit is not None:
					strTemp += f"{formationEntry.unit.name()} at {formationEntry.unit.location}, "
		elif self.state == OperationStateType.movingToTarget:
			strTemp += f"Moving To Target, Army: {self.army.identifier[0:8]} at {self.army.position}, Target {self.targetPosition}, "
			for formationEntry in self.army.formationEntries:
				if formationEntry.unit is not None:
					strTemp += f"{formationEntry.unit.name()} at {formationEntry.unit.location}, "
		elif self.state == OperationStateType.atTarget:
			strTemp += "At Target"
		elif self.state == OperationStateType.successful:
			strTemp += "Completed"
		else:
			raise Exception(f'State {self.state} not handled')

		logging.info(strTemp)

	def logOperationEnd(self):
		"""Log that an operation has ended"""
		strTemp = f'=== Operation: {self.player.name()} ({self.player.leader.civilization().title()}), '
		strTemp += f'{self.operationType}, '
		strTemp += "Ended, "

		if self.stateReason == OperationStateReason.success:
			strTemp += "Success"
		elif self.stateReason == OperationStateReason.noTarget:
			strTemp += "No target"
		elif self.stateReason == OperationStateReason.repeatTarget:
			strTemp += "Repeat target"
		elif self.stateReason == OperationStateReason.lostTarget:
			strTemp += "Lost target"
		elif self.stateReason == OperationStateReason.targetAlreadyCaptured:
			strTemp += "Target already captured"
		elif self.stateReason == OperationStateReason.noRoomDeploy:
			strTemp += "No room to deploy"
		elif self.stateReason == OperationStateReason.halfStrength:
			strTemp += "Half strength"
		elif self.stateReason == OperationStateReason.noMuster:
			strTemp += "No muster point"
		elif self.stateReason == OperationStateReason.lostCivilian:
			strTemp += "Lost civilian"
		elif self.stateReason == OperationStateReason.escortDied:
			strTemp += "Escort died"
		# elif self.stateReason == OperationStateReason.noNukes:
		#	strTemp += "No nukes"
		elif self.stateReason == OperationStateReason.killed:
			strTemp += "Killed"
		elif self.stateReason == OperationStateReason.none:
			strTemp += "None"
		else:
			raise Exception(f'Reason {self.stateReason} not handled')

		logging.info(strTemp)

	def computeCenterOfMassForTurn(self, closestCurrentCenterOfMassOnPath: HexPoint, simulation) -> Optional[HexPoint]:
		"""Pick this turn's desired "center of mass" for the army"""
		rtnValue: Optional[HexPoint] = None

		if self.state == OperationStateType.aborted or self.state == OperationStateType.atTarget or \
			self.state == OperationStateType.successful:
			# NOOP
			pass
		elif self.state == OperationStateType.recruitingUnits or self.state == OperationStateType.gatheringForces:
			# Just use the muster point if we're still recruiting/gathering
			rtnValue = self.musterPosition
		elif self.state == OperationStateType.movingToTarget:
			goalPoint: Optional[HexPoint] = self.army.goal

			# Is goal a city and we're a naval operation?  If so, go just offshore.
			if goalPoint is None:
				return None
			
			goalPlot = simulation.tileAt(goalPoint)
			
			if goalPlot is None:
				return None

			if not goalPlot.isWater() and self.isAllNavalOperation():
				goalPoint = self.player.militaryAI.coastalPlotAdjacentTo(goalPoint, self.army, simulation)

			lastTurnArmyPlot = self.army.position

			domain: UnitDomainType = UnitDomainType.sea if self.isAllNavalOperation() or self.isMixedLandNavalOperation() else UnitDomainType.land
			centerOfMass = self.army.centerOfMass(domain, simulation)

			if lastTurnArmyPlot is not None and centerOfMass is not None and goalPoint is not None:
				# Push center of mass forward a number of hexes equal to average movement
				pathFinderDataSource = simulation.ignoreUnitsPathfinderDataSource(
					UnitMovementType.walk,
					self.player,
					canEmbark=self.player.canEmbark(),
					canEnterOcean=self.player.canEnterOcean()
				)
				pathFinder = AStarPathfinder(pathFinderDataSource)

				path = pathFinder.shortestPath(lastTurnArmyPlot, goalPoint)

				bestDistanceToCenterOfMass: float = 10000000000.0
				bestNodeIndex: int = 0
				nodesOnPath: [HexPoint] = []

				# Starting at the end, loop until we find the plot closest to center of mass
				for point in reversed(path.points()):
					nodesOnPath.append(point)
					distanceToCenterOfMass = point.distance(centerOfMass)

					if distanceToCenterOfMass < bestDistanceToCenterOfMass:
						bestDistanceToCenterOfMass = distanceToCenterOfMass
						bestNodeIndex = len(nodesOnPath) - 1

				# Now move back up path from the best node a number of spaces equal to army's movement rate
				if bestNodeIndex > self.army.movementRate(simulation):
					rtnValue = nodesOnPath[bestNodeIndex - self.army.movementRate(simulation)]
				else:
					rtnValue = nodesOnPath[0]
		else:
			raise InvalidEnumError(self.state)

		return rtnValue


class EscortedOperation(Operation):
	"""based on CvAIEscortedOperation
	Base class for operations that are one military unit and one civilian
	"""
	def __init__(self, operationType: UnitOperationType, escorted: bool, civilianType: UnitTaskType):
		self.escorted = escorted
		self.civilianType = civilianType

		Operation.__init__(self, operationType=operationType)

	# Kick off this operation
	def initialize(self, player, enemy, area: HexArea, target: Optional[HexPoint] = None,
				   muster: Optional[HexPoint] = None, simulation = None):
		super().initialize(player, enemy, area, target, muster, simulation)

		self.reset()
		self.moveType = OperationMoveType.singleHex
		self.player = player

		civilian = self.findBestCivilian(simulation)
		if civilian is not None:

			# Find a destination (not worrying about safe paths)
			targetSite = self.findBestTarget(civilian, onlySafePaths=True, simulation=simulation)
			if targetSite is not None:
				self.updateTargetTo(targetSite.point)

				# create the armies that are needed and set the state to ARMYAISTATE_WAITING_FOR_UNITS_TO_REINFORCE
				army = Army(player, self, self.formation(simulation))
				army.state = ArmyState.waitingForUnitsToReinforce

				# Figure out the initial rally point - for this operation it is wherever our civilian is standing
				army.goal = targetSite.point
				army.muster = civilian.location
				army.position = civilian.location
				army.area = simulation.areaOf(civilian.location)

				# Add the settler to our army
				army.addUnit(civilian, 0)

				self.army = army

				# Add the escort as a unit we need to build
				self.listOfUnitsWeStillNeedToBuild = []

				escortSlotIndex = 1
				escortFormationSlot = army.formation.slots()[escortSlotIndex]
				thisOperationSlot = OperationSlot(self, army, escortFormationSlot, escortSlotIndex)
				self.listOfUnitsWeStillNeedToBuild.append(thisOperationSlot)

				# try to get the escort from existing units that are waiting around
				self.grabUnitsFromTheReserves(muster, targetSite.point, simulation)
				if army.numberOfSlotsFilled() > 1:
					army.state = ArmyState.waitingForUnitsToCatchUp
					self.state = OperationStateType.gatheringForces
				else:
					# There was no escort immediately available. Let's look for a "safe" city site instead
					newTarget = self.findBestTarget(civilian, onlySafePaths=True, simulation=simulation)

					# If no better target, we'll wait it out for an escort
					if newTarget is None:
						# Need to add it back in to list of what to build (was cleared before since marked optional)
						self.listOfUnitsWeStillNeedToBuild = []

						escortSlotIndex = 1
						escortFormationSlot = army.formation.slots()[escortSlotIndex]
						thisOperationSlot2 = OperationSlot(self, army, escortFormationSlot, escortSlotIndex)
						self.listOfUnitsWeStillNeedToBuild.append(thisOperationSlot2)

						self.state = OperationStateType.recruitingUnits
					else:
						# Send the settler by himself to this safe location
						self.escorted = False

						# Clear the list of units we need
						self.listOfUnitsWeStillNeedToBuild = []

						# Change the muster point
						self.army.goal = newTarget
						self.musterPosition = civilian.location
						self.army.position = civilian.location

						# Send the settler directly to the target
						self.army.state = ArmyState.movingToDestination
						self.state = OperationStateType.movingToTarget

				self.logOperationStart()
			else:
				# Lost our target, abort
				self.state = OperationStateType.aborted
				self.stateReason = OperationStateReason.lostTarget

		return

	def formation(self, simulation) -> UnitFormationType:
		raise Exception("must be overridden")

	def findBestTarget(self, unit, onlySafePaths: bool = True, simulation=None):  # -> Tile
		raise Exception("need to be overriden")

	# / Find the civilian we want to use
	def findBestCivilian(self, simulation):  # -> Unit:
		assert self.player is not None

		units = simulation.unitsOf(self.player)

		for unit in units:
			if unit.task() == self.civilianType:
				if unit.army() is None:
					capital = simulation.capitalOf(self.player)

					if capital is not None:
						capitalArea = simulation.areaOf(capital.location)
						unitArea = simulation.areaOf(unit.location)

						if capitalArea is not None and unitArea is not None:
							if capitalArea == unitArea:
								return unit
						else:
							# FIXME:
							return unit

		return None

	def retargetCivilian(self, unit, army: Army, simulation) -> bool:
		# Find the best city site (taking into account whether we are escorted)
		betterTarget = self.findBestTarget(unit, simulation=simulation)

		# No targets at all!  Abort
		if betterTarget is None:
			self.state = OperationStateType.aborted
			self.stateReason = OperationStateReason.noTarget
			return False
		# If this is a new target, switch to it
		elif betterTarget.point != self.targetPosition:
			self.updateTargetTo(betterTarget.point)
			self.army.goal = betterTarget.point
		else:
			self.state = OperationStateType.aborted
			self.stateReason = OperationStateReason.repeatTarget
			return False

		self.army.state = ArmyState.movingToDestination
		self.state = OperationStateType.movingToTarget

		return True


class FoundCityOperation(EscortedOperation):
	def __init__(self):
		super().__init__(UnitOperationType.foundCity, escorted=True, civilianType=UnitTaskType.settle)

	def formation(self, simulation) -> UnitFormationType:
		return UnitFormationType.settlerEscort  # MUFORMATION_SETTLER_ESCORT

	def armyInPosition(self, simulation) -> bool:
		"""If at target, found city; if at muster point, merge settler and escort and move out"""

		if self.state == OperationStateType.none:
			# NOOP
			pass
		elif self.state == OperationStateType.aborted:
			# In all other cases use base class version
			return Operation.armyInPosition(self, simulation)

		elif self.state == OperationStateType.recruitingUnits:
			# In all other cases use base class version
			return Operation.armyInPosition(self, simulation)

		elif self.state == OperationStateType.gatheringForces:
			# If we were gathering forces, we have to insist that any escort is in the same plot as the settler.
			# If not we 'll fall through and just stay in this state.

			# No escort, can just let base class handle it
			if not self.escorted:
				return Operation.armyInPosition(self, simulation)

			settler = self.army.unitAt(0)
			escort = self.army.unitAt(1)

			if escort is None:
				# Escort died while gathering forces. Abort (and return TRUE since state changed)
				self.state = OperationStateType.aborted
				self.stateReason = OperationStateReason.escortDied
				return True

			if escort is not None and settler is not None and escort.location == settler.location:
				# let's see if the target still makes sense (this is modified from RetargetCivilian)
				betterTarget = self.findBestTarget(settler, simulation=simulation)

				# No targets at all!  Abort
				if betterTarget is None:
					self.state = OperationStateType.aborted
					self.stateReason = OperationStateReason.noTarget
					return False

				# If we have a target, check if we should apply it
				if self.targetPosition != betterTarget.point:
					logging.debug(f'=== Operation: changing target from {self.targetPosition} to {betterTarget.point}')
					self.updateTargetTo(betterTarget.point)
					self.army.goal = betterTarget.point

				return Operation.armyInPosition(self, simulation)

		elif self.state == OperationStateType.movingToTarget or self.state == OperationStateType.atTarget:
			# Call base class version and see, if it thinks we're done
			stateChanged = Operation.armyInPosition(self, simulation)

			# Now get the settler
			settler = self.army.unitAt(0)
			if settler is not None:
				targetTile = simulation.tileAt(self.targetPosition)
				targetOwner = targetTile.owner()

				# FIXME: or GetTargetPlot()->IsAdjacentOwnedByOtherTeam(pSettler->getTeam())
				if targetOwner is not None and targetOwner.leader != self.player.leader:
					self.retargetCivilian(settler, self.army, simulation)
					settler.finishMoves()

					escort = self.army.unitAt(1)
					if escort is not None:
						escort.finishMoves()

				elif settler.location == self.targetPosition and settler.canMove() and \
					settler.canFoundAt(settler.location, simulation):
					# If the settler made it, we don't care about the entire army
					settler.pushMission(UnitMission(UnitMissionType.found), simulation)
					self.state = OperationStateType.successful

				elif settler.location == self.targetPosition and not settler.canFoundAt(settler.location, simulation):
					# If we 're at our target, but can no longer found a city, might be someone else beat us to this area
					# So move back out, picking a new target
					self.retargetCivilian(settler, self.army, simulation)
					settler.finishMoves()

					escort = self.army.unitAt(1)
					if escort is not None:
						escort.finishMoves()

			return stateChanged

		elif self.state == OperationStateType.successful:
			# NOOP
			pass

		return False

	# Find the plot where we want to settle
	def findBestTarget(self, unit, onlySafePaths: bool = True, simulation=None):  # -> Optional[Tile]:
		if simulation is None:
			raise Exception('simulation must not be None')

		tile = self.player.bestSettlePlotFor(unit, escorted=onlySafePaths, sameArea=True, simulation=simulation)

		if tile is not None:
			return tile

		self.defaultArea = None
		return self.player.bestSettlePlotFor(unit, escorted=onlySafePaths, sameArea=False, simulation=simulation)


class CityCloseDefenseOperation(Operation):
	def __init__(self):
		super().__init__(UnitOperationType.cityCloseDefense)


class EnemyTerritoryOperation(Operation):
	def __init__(self, operation: UnitOperationType):
		super().__init__(operation)

	def initialize(self, player, enemy, area: Optional[HexArea], target: Optional[HexPoint], muster: Optional[HexPoint], simulation):
		"""Kick off this operation"""
		super().initialize(player, enemy, area, target, muster, simulation)

		self.moveType = OperationMoveType.enemyTerritory

		# create the armies that are needed and set the state to ARMYAISTATE_WAITING_FOR_UNITS_TO_REINFORCE
		self.army = Army(player, self, self.formation(simulation))
		self.army.state = ArmyState.waitingForUnitsToReinforce

		# Figure out the initial rally point
		targetPlot = self.findBestTarget(simulation)
		if targetPlot is not None:
			self.targetPosition = targetPlot
			self.army.goal = targetPlot

			newMusterPlot = self.selectInitialMusterPoint(simulation)
			if newMusterPlot is not None:
				self.musterPosition = newMusterPlot.point
				self.army.position = newMusterPlot.point
				self.defaultArea = simulation.areaOf(newMusterPlot.point)

				if self.defaultArea != simulation.areaOf(targetPlot):
					self.army.goal = targetPlot
				else:
					pathFinderDataSource = simulation.ignoreUnitsPathfinderDataSource(
						UnitMovementType.walk,
						self.player,
						canEmbark=self.player.canEmbark(),
						canEnterOcean=self.player.canEnterOcean()
					)
					pathFinder = AStarPathfinder(pathFinderDataSource)

					path = pathFinder.shortestPath(self.musterPosition, self.targetPosition)
					if path is not None:
						reducedPath: HexPath = path.pathWithout(self.deployRange())
						deployPoint = lastOrNone(reducedPath.points())

						if deployPoint is not None:
							self.army.goal = deployPoint
					else:
						# No path, abort
						self.state = OperationStateType.aborted
						self.stateReason = OperationStateReason.lostPath

				# Find the list of units we need to build before starting this operation in earnest
				self.buildListOfUnitsWeStillNeedToBuild()

				# try to get as many units as possible from existing units that are waiting around
				if self.grabUnitsFromTheReserves(self.musterPosition, self.targetPosition, simulation):
					self.army.state = ArmyState.waitingForUnitsToCatchUp
					self.state = OperationStateType.gatheringForces
				else:
					self.state = OperationStateType.recruitingUnits
				# LogOperationStart();

			else:
				# No muster point, abort
				self.state = OperationStateType.aborted
				self.stateReason = OperationStateReason.noMuster
		else:
			# Lost our target, abort
			self.state = OperationStateType.aborted
			self.stateReason = OperationStateReason.lostTarget

		return

	def deployRange(self) -> int:
		"""How close to target do we end up?"""
		return 4  # AI_OPERATIONAL_CITY_ATTACK_DEPLOY_RANGE

	def maximumRecruitTurns(self) -> int:
		"""How long will we wait for a recruit to show up?"""
		return 10 # AI_OPERATIONAL_MAX_RECRUIT_TURNS_ENEMY_TERRITORY

	def findBestTarget(self, simulation) -> Optional[HexPoint]:
		raise Exception('Must be overwritten by subclass')

	def selectInitialMusterPoint(self, simulation):  # -> Optional[Tile]
		"""Figure out the initial rally point"""
		player = self.player
		dangerPlotsAI = self.player.dangerPlotsAI

		deployPoint: Optional[HexPoint] = None
		musterPoint: Optional[HexPoint] = None

		startCity = self.operationStartCity(simulation)
		if startCity is not None:
			startCityPlot = simulation.tileAt(startCity.location)
			if startCityPlot is not None:
				# Different areas? If so, just muster at start city
				if startCityPlot.area != simulation.areaOf(self.army.goal):
					self.musterPosition = startCityPlot.point
					return startCityPlot

				# Generate path
				pathFinderDataSource = simulation.ignoreUnitsPathfinderDataSource(
					UnitMovementType.walk,
					self.player,
					canEmbark=player.canEmbark(),
					canEnterOcean=player.canEnterOcean()
				)
				pathFinder = AStarPathfinder(pathFinderDataSource)

				path = pathFinder.shortestPath(startCity.location, self.army.goal)
				if path is not None:
					spacesFromTarget = 0
					dangerousPlots = 0

					# Starting at the end, loop until we find a plot from this owner
					for pathItem in reversed(path.points()):
						pathPlot = simulation.tileAt(pathItem)

						# Is this the deploy-point?
						if spacesFromTarget == self.deployRange():
							deployPoint = pathItem

						# Check and see if this plot has the right owner
						if pathPlot.hasOwner() and player == pathPlot.owner():
							musterPoint = pathItem
							break
						else:
							# Is this a dangerous plot?
							if dangerPlotsAI.dangerAt(pathItem) > 0:
								dangerousPlots += 1

						# Move to the previous plot on the path
						spacesFromTarget += 1

					# Is the path safe? If so, let's just muster at the deploy-point
					if spacesFromTarget > 0 and (dangerousPlots * 100 / spacesFromTarget) < 20:  # AI_OPERATIONAL_PERCENT_DANGER_FOR_FORWARD_MUSTER
						if deployPoint is not None:
							musterPoint = deployPoint

		if musterPoint is not None:
			self.musterPosition = musterPoint
			return simulation.tileAt(musterPoint)
		else:
			logging.warning(f"No muster point found, Operation aborting, Target was {self.army.goal}")

		return None


class BasicCityAttackOperation(EnemyTerritoryOperation):
	def __init__(self, operation: Optional[UnitOperationType] = None):
		super().__init__(UnitOperationType.basicCityAttack if operation is None else operation)

	def initialize(self, player, enemy, area: Optional[HexArea], target: Optional[HexPoint], muster: Optional[HexPoint], simulation):
		"""Kick off this operation"""
		self.player = player
		self.enemy = enemy
		self.defaultArea = area
		self.shouldReplaceLossesWithReinforcements = False

		self.moveType = OperationMoveType.enemyTerritory
		self.startPosition = muster

		# create the armies that are needed and set the state to ARMYAISTATE_WAITING_FOR_UNITS_TO_REINFORCE
		self.army = Army(player, self, self.formation(simulation))
		self.army.state = ArmyState.waitingForUnitsToReinforce

		if target is not None:
			self.targetPosition = target
			self.army.goal = target
			self.musterPosition = muster

			self.army.position = muster
			self.defaultArea = simulation.areaOf(muster)

			# Reset our destination to be a few plots shy of the final target
			pathFinderDataSource = simulation.ignoreUnitsPathfinderDataSource(
				UnitMovementType.walk,
				self.player,
				canEmbark=self.player.canEmbark(),
				canEnterOcean=self.player.canEnterOcean()
			)
			pathFinder = AStarPathfinder(pathFinderDataSource)

			path = pathFinder.shortestPath(self.musterPosition, self.targetPosition)
			if path is not None:
				reducedPath: HexPath = path.pathWithout(self.deployRange())
				deployPoint = reducedPath.points()[-1]
				self.army.goal = deployPoint

				# Find the list of units we need to build before starting this operation in earnest
				self.buildListOfUnitsWeStillNeedToBuild()

				# try to get as many units as possible from existing units that are waiting around
				if self.grabUnitsFromTheReserves(self.musterPosition, self.targetPosition, simulation):
					self.army.state = ArmyState.waitingForUnitsToCatchUp
					self.state = ArmyState.gatheringForces
				else:
					self.state = ArmyState.recruitingUnits

				self.logOperationStart()
			else:
				self.state = OperationStateType.aborted
				self.stateReason = OperationStateReason.lostPath
		else:
			# Lost our target, abort
			self.state = OperationStateType.aborted
			self.stateReason = OperationStateReason.lostTarget

		return


class PillageEnemyOperation(Operation):
	def __init__(self):
		super().__init__(UnitOperationType.pillageEnemy)


class RapidResponseOperation(Operation):
	def __init__(self):
		super().__init__(UnitOperationType.rapidResponse)


class EnemyTerritoryOperation(Operation):
	def __init__(self, operationType: UnitOperationType):
		super().__init__(operationType)

	def initialize(self, player, enemy, area: Optional[HexArea], target: Optional[HexPoint], muster: Optional[HexPoint], simulation):
		super().initialize(player, enemy, area, target, muster, simulation)

		self.moveType = OperationMoveType.enemyTerritory

		# create the armies that are needed and set the state to ARMYAISTATE_WAITING_FOR_UNITS_TO_REINFORCE
		self.army = Army(player, self, self.formation(simulation))
		self.army.state = ArmyState.waitingForUnitsToReinforce

		# Figure out the initial rally point
		targetPlot = self.findBestTarget(simulation=simulation)
		if targetPlot is not None:
			self.targetPosition = targetPlot
			self.army.goal = targetPlot

			newMusterPlot = self.selectInitialMusterPoint(simulation)
			if newMusterPlot is not None:
				self.musterPosition = newMusterPlot.point
				self.army.position = newMusterPlot.point
				self.defaultArea = simulation.areaOf(newMusterPlot.point)

				if self.defaultArea != simulation.areaOf(targetPlot):
					self.army.goal = targetPlot
				else:
					pathFinderDataSource = simulation.ignoreUnitsPathfinderDataSource(
						UnitMovementType.walk,
						self.player,
						canEmbark=self.player.canEmbark(),
						canEnterOcean=self.player.canEnterOcean()
					)
					pathFinder = AStarPathfinder(pathFinderDataSource)

					path = pathFinder.shortestPath(self.musterPosition, self.targetPosition)
					if path is not None:
						reducedPath = path.pathWithout(self.deployRange())
						deployPoint = reducedPath.points()[-1]
						self.army.goal = deployPoint
					else:
						# No path, abort
						self.state = OperationStateType.aborted
						self.stateReason = OperationStateReason.lostPath

				# Find the list of units we need to build before starting this operation in earnest
				self.buildListOfUnitsWeStillNeedToBuild()

				# try to get as many units as possible from existing units that are waiting around
				if self.grabUnitsFromTheReserves(self.musterPosition, self.targetPosition, simulation):

					self.army.state = ArmyState.waitingForUnitsToCatchUp
					self.state = OperationStateType.gatheringForces
				else:
					self.state = OperationStateType.recruitingUnits

				self.logOperationStart()
			else:
				# No muster point, abort
				self.state = OperationStateType.aborted
				self.stateReason = OperationStateReason.noMuster
		else:
			# Lost our target, abort
			self.state = OperationStateType.aborted
			self.stateReason = OperationStateReason.lostTarget

		return

	def formation(self, simulation) -> UnitFormationType:
		return UnitFormationType.none

	def deployRange(self) -> int:
		"""How close to target do we end up?"""
		return 4  # AI_OPERATIONAL_CITY_ATTACK_DEPLOY_RANGE

	# How long will we wait for a recruit to show up?
	def maximumRecruitTurns(self) -> int:
		return 10  # AI_OPERATIONAL_MAX_RECRUIT_TURNS_ENEMY_TERRITORY

	def selectInitialMusterPoint(self, simulation):  # -> Optional[Tile]:
		"""Figure out the initial rally point"""
		dangerPlotsAI = self.player.dangerPlotsAI

		deployPlot: Optional[HexPoint] = None
		musterPlot: Optional[HexPoint] = None

		startCity = self.operationStartCity(simulation)
		if startCity is not None:
			startCityPlot = simulation.tileAt(startCity.location)
			if startCity is not None:
				# Different areas?  If so, just muster at start city
				if startCityPlot.area() != simulation.areaOf(self.army.goal):
					self.musterPosition = startCityPlot.point
					return startCityPlot

				# Generate path
				pathFinderDataSource = simulation.ignoreUnitsPathfinderDataSource(
					UnitMovementType.walk,
					self.player,
					canEmbark=self.player.canEmbark(),
					canEnterOcean=self.player.canEnterOcean()
				)
				pathFinder = AStarPathfinder(pathFinderDataSource)

				path = pathFinder.shortestPath(startCity.location, self.army.goal)
				if path is not None:
					spacesFromTarget = 0
					dangerousPlots = 0

					# Starting at the end, loop until we find a plot from this owner
					for pathItem in reversed(path.points()):
						pathPlot = simulation.tileAt(pathItem)

						# Is this the deploy point?
						if spacesFromTarget == self.deployRange():
							deployPlot = pathItem

						# Check and see if this plot has the right owner
						if pathPlot.hasOwner() and self.player == pathPlot.owner():
							musterPlot = pathItem
							break
						else:
							# Is this a dangerous plot?
							if dangerPlotsAI.dangerAt(pathItem) > 0:
								dangerousPlots += 1

						# Move to the previous plot on the path
						spacesFromTarget += 1

					# Is the path safe?  If so, let's just muster at the deploy point
					if spacesFromTarget > 0 and (
						dangerousPlots * 100 / spacesFromTarget) < 20:  # AI_OPERATIONAL_PERCENT_DANGER_FOR_FORWARD_MUSTER
						if deployPlot is not None:
							musterPlot = deployPlot

		if musterPlot is not None:
			self.musterPosition = musterPlot
			return simulation.tileAt(musterPlot)
		else:
			logging.debug(f"No muster point found, Operation aborting, Target was, {self.army.goal}")

		return None

	def findBestTarget(self, simulation) -> Optional[HexPoint]:
		raise Exception("function called CvEnemyTerritoryOperation::findBestTarget() - should be overriden")


class DestroyBarbarianCampOperation(EnemyTerritoryOperation):
	def __init__(self):
		super().__init__(UnitOperationType.destroyBarbarianCamp)
		self.civilianRescue = False
		self.unitToRescue = None

	def formation(self, simulation) -> UnitFormationType:
		return UnitFormationType.antiBarbarianTeam  # MUFORMATION_ANTI_BARBARIAN_TEAM

	def deployRange(self) -> int:
		"""How close to target do we end up?"""
		return 2  # AI_OPERATIONAL_BARBARIAN_CAMP_DEPLOY_RANGE

	def armyInPosition(self, simulation) -> bool:
		# Same as default version except if just gathered forces, check to see if a better target has presented itself
		if self.army is None:
			raise Exception("cant get basics")

		stateChanged = False

		# If we were gathering forces, let's make sure a better target hasn't presented itself
		if self.state == OperationStateType.gatheringForces:
			# First do base case processing
			stateChanged = Operation.armyInPosition(self, simulation)

			# Now revisit target
			possibleBetterTarget = self.findBestTarget(simulation=simulation)

			# If no target left, abort
			if possibleBetterTarget is None:
				self.state = OperationStateType.aborted
				self.stateReason = OperationStateReason.lostTarget
			elif possibleBetterTarget != self.targetPosition:
				# If target changed, reset to this new one
				# If we're traveling on a single continent, set our destination to be a few plots shy of the final target
				armyArea = simulation.areaOf(self.army.position)
				if armyArea == simulation.areaOf(possibleBetterTarget):
					# Reset our destination to be a few plots shy of the final target
					pathFinderDataSource = simulation.ignoreUnitsPathfinderDataSource(
						UnitMovementType.walk,
						self.player,
						canEmbark=self.player.canEmbark(),
						canEnterOcean=False
					)
					pathFinder = AStarPathfinder(pathFinderDataSource)

					path = pathFinder.shortestPath(self.army.position, possibleBetterTarget)
					if path is not None:
						reducedPath = path.pathWithout(2)  # AI_OPERATIONAL_BARBARIAN_CAMP_DEPLOY_RANGE
						deployPoint = reducedPath.points()[-1]
						self.army.goal = deployPoint
						self.targetPosition = deployPoint
				else:
					# Coming in from the sea. Just head to the camp
					self.army.goal = possibleBetterTarget
					self.targetPosition = possibleBetterTarget

		# See if reached our target, if so give control of these units to the tactical AI
		elif self.state == OperationStateType.movingToTarget:
			if self.army.position.distance(self.army.goal) <= 1:
				# Notify tactical AI to focus on this area
				zone = TemporaryZone(
					location=self.targetPosition,
					lastTurn=simulation.currentTurn + 5,  # AI_TACTICAL_MAP_TEMP_ZONE_TURNS
					targetType=TacticalTargetType.barbarianCamp,
					navalMission=False
				)

				self.player.tacticalAI.addTemporaryZone(zone)

				self.state = OperationStateType.successful

		# In all  other cases use base class version
		elif self.state == OperationStateType.aborted or self.state == OperationStateType.recruitingUnits or \
			self.state == OperationStateType.atTarget:
			return Operation.armyInPosition(self, simulation)

		return stateChanged

	def shouldAbort(self, simulation) -> bool:
		# Returns true when we should abort the operation totally (besides when we have lost all units in it)
		targetPosition = self.targetPosition

		if targetPosition is None:
			return True

		targetPlot = simulation.tileAt(targetPosition)

		if targetPlot is None:
			return True

		# If parent says we're done, don't even check anything else
		rtnValue = Operation.shouldAbort(self, simulation)

		if not rtnValue:
			# See if our target camp is still there
			if not self.civilianRescue and targetPlot.improvement() != ImprovementType.barbarianCamp:
				# Success!  The camp is gone
				logging.debug(f"Barbarian camp at {targetPosition} no longer exists. Aborting")

				return True
			elif self.civilianRescue:
				# is the unit rescued?
				if self.unitToRescue is None or self.unitToRescue.isDelayedDeath():
					logging.debug(f"Civilian can no longer be rescued from barbarians. Aborting")

					return True
				else:
					if self.unitToRescue.originalLeader != self.player.leader or \
						(
							self.unitToRescue.task() != UnitTaskType.settle and self.unitToRescue.task() != UnitTaskType.work):
						logging.info(f"Civilian can no longer be rescued from barbarians. Aborting")

						return True

			elif self.state != OperationStateType.recruitingUnits:
				# If down below strength of camp, abort
				campDefender = simulation.unitAt(targetPosition, UnitMapType.combat)
				if campDefender is not None and self.army.totalPower() < campDefender.power():
					logging.info(f"Barbarian camp stronger {campDefender.power()} than our units army.totalPower(). Aborting")

					return True

		return rtnValue

	def findBestTarget(self, simulation) -> Optional[HexPoint]:
		"""Find the barbarian camp we want to eliminate"""
		barbarianPlayer = simulation.barbarianPlayer()
		player = self.player

		self.civilianRescue = False

		bestDistance: int = sys.maxsize
		bestPlot: Optional[HexPoint] = None

		startCity = self.operationStartCity(simulation)
		if startCity is not None:

			# look for good captured civilians of ours (settlers and workers, not missionaries)
			# these will be even more important than just a camp
			# btw - the AI will cheat here - as a human I would use a combination of memory and intuition to find these,
			# since our current AI has neither of these...
			pathFinderDataSource = simulation.ignoreUnitsPathfinderDataSource(
				UnitMovementType.walk,
				self.player,
				canEmbark=self.player.canEmbark(),
				canEnterOcean=False
			)
			pathFinder = AStarPathfinder(pathFinderDataSource)

			for loopUnit in simulation.unitsOf(barbarianPlayer):
				if loopUnit.originalPlayer() == player and (
					loopUnit.task() == UnitTaskType.settle or loopUnit.task() == UnitTaskType.work):
					path = pathFinder.shortestPath(loopUnit.location, startCity.location)
					distance: int = sys.maxsize if path is None else len(path.points())

					if distance < bestDistance:
						bestDistance = distance
						bestPlot = loopUnit.location
						self.civilianRescue = True
						self.unitToRescue = loopUnit

			# no unit to capture - check for camps
			if bestPlot is None:
				mapSize: MapSize = simulation.mapSize()

				# Look at map for Barbarian camps
				for x in range(mapSize.size().width()):
					for y in range(mapSize.size().height()):
						tile = simulation.tileAt(x, y)
						if tile.isDiscoveredBy(self.player):
							if tile.hasImprovement(ImprovementType.barbarianCamp):
								path = pathFinder.shortestPath(tile.point, startCity.location)
								distance: int = sys.maxsize if path is None else len(path.points())

								if distance < bestDistance:
									bestDistance = distance
									bestPlot = tile.point

		return bestPlot


class NavalEscortedOperation(Operation):
	"""Base class for operations that require a naval escort for land units
	CvAINavalEscortedOperation"""
	def __init__(self, operationType: UnitOperationType):
		Operation.__init__(self, operationType)

		self.civilianType: UnitTaskType = UnitTaskType.settle
		self.initialAreaID: int = -1

	def initialize(self, player, enemy, area: Optional[HexArea], target: Optional[HexPoint], muster: Optional[HexPoint], simulation):
		"""Kick off this operation"""
		self.reset()
		self.moveType = OperationMoveType.navalEscort  # AI_OPERATION_MOVETYPE_NAVAL_ESCORT
		self.player = player
		self.setDefaultArea(area)  # Area settler starts in

		# Find the free civilian (that triggered this operation)
		ourCivilian = self.findBestCivilian(simulation)
		self.initialAreaID = ourCivilian.area()
		startCity = self.operationStartCity(simulation)

		if ourCivilian is not None and self.initialAreaID != -1 and startCity is not None:
			# Find a destination (not worrying about safe paths)
			targetSite = self.findBestTarget(ourCivilian, simulation)

			if targetSite is not None:
				self.updateTargetTo(targetSite.point)

				# create the armies that are needed and set the state to ARMYAISTATE_WAITING_FOR_UNITS_TO_REINFORCE
				self.army = Army(player, self, self.formation(simulation))  # fixme
				self.army.state = ArmyState.waitingForUnitsToReinforce

				self.army.goal = targetSite.point
				self.updateTargetTo(targetSite.point)
				self.army.position = targetSite.point

				# Add the settler to our army
				self.army.addUnit(ourCivilian, 0)

				# try to get the escort from existing units that are waiting around
				self.buildListOfUnitsWeStillNeedToBuild()

				# Try to get as many units as possible from existing units that are waiting around
				if self.grabUnitsFromTheReserves(self.musterPosition, None, simulation):
					self.army.state = ArmyState.waitingForUnitsToCatchUp
					self.state = OperationStateType.gatheringForces  # AI_OPERATION_STATE_GATHERING_FORCES
				else:
					self.state = OperationStateType.recruitingUnits  # AI_OPERATION_STATE_RECRUITING_UNITS
			
				self.logOperationStart()
			else:
				# Lost our target, abort
				self.state = OperationStateType.aborted  # AI_OPERATION_STATE_ABORTED
				self.stateReason = OperationStateReason.lostTarget  # AI_ABORT_LOST_TARGET

		return

	def formation(self, simulation) -> UnitFormationType:
		return UnitFormationType.colonizationParty

	def operationStartCity(self, simulation):  # -> City
		"""Find the port our operation will leave from"""
		if self.startPosition is not None:
			return simulation.cityAt(self.startPosition)

		# Find first coastal city in same area as settler
		for city in simulation.citiesOf(self.player):
			if simulation.isCoastalAt(city.location):
				cityArea = simulation.areaOf(city.location)
				if cityArea is not None:
					if cityArea == self.defaultArea:
						return city

		return None

	def unitWasRemoved(self, army, slot: UnitFormationSlot):
		"""Always abort if settler is removed"""
		# Assumes civilian is in the first slot of the formation
		if slot.primaryUnitTask == UnitTaskType.settle or slot.primaryUnitTask == UnitTaskType.settlerSea:
			self.state = OperationStateType.aborted
			self.stateReason = OperationStateReason.lostCivilian

	def findBestCivilian(self, simulation):
		"""Find the civilian we want to use"""
		assert self.player is not None

		units = simulation.unitsOf(self.player)

		for unit in units:
			if unit.task() == self.civilianType:
				if unit.army() is None:
					return unit

		return None

	def targetPlot(self, simulation):  # -> Optional[Tile]
		if self.targetPosition is not None:
			return simulation.tileAt(self.targetPosition)

		return None

	def armyInPosition(self, simulation) -> bool:
		"""If at target, found city; if at muster point, merge settler and escort and move out"""
		stateChanged: bool = False

		if self.state == OperationStateType.movingToTarget or self.state == OperationStateType.atTarget:
			# Call base class version and see if it thinks we're done
			stateChanged = Operation.armyInPosition(self, simulation)

			# Now get the settler
			settler = self.army.unitAt(0)
			if settler is not None:
				targetPlot = self.targetPlot(simulation)
				targetPlotOwner = targetPlot.owner()

				if (targetPlotOwner is not None and self.player != targetPlotOwner) or \
					simulation.isAdjacentOwnedOtherThan(self.targetPosition, settler.player):

					logging.debug(f"Not at target, but can no longer settle here. Target was {self.targetPosition}")
					self.retargetCivilian(settler, self.army, simulation)
					settler.finishMoves()

					escort = self.army.unitAt(1)
					if escort is not None:
						escort.finishMoves()

				# If the settler made it, we don't care about the entire army
				elif settler.location == self.targetPosition and settler.canMove() and \
					settler.canFoundAt(settler.location, simulation):

					settler.pushMission(UnitMission(UnitMissionType.found), simulation)
					logging.debug(f"City founded, at {settler.location}")

					self.state = OperationStateType.successful

				# If we're at our target, but can no longer found a city, might be someone else beat us to this area
				# So move back out, picking a new target
				elif settler.location == self.targetPosition and not settler.canFoundAt(settler.location, simulation):
					logging.debug(f"At target but can no longer settle here. Target was {settler.location}")

					self.retargetCivilian(settler, self.army, simulation)
					settler.finishMoves()

					escort = self.army.unitAt(1)
					if escort is not None:
						escort.finishMoves()

		# In all other cases use base class version
		if self.state == OperationStateType.gatheringForces or self.state == OperationStateType.aborted or \
			self.state == OperationStateType.recruitingUnits:

			return Operation.armyInPosition(self, simulation)

		return stateChanged

	def findBestTarget(self, unit, simulation):
		"""Find the plot where we want to settle"""
		return self.player.bestSettlePlotFor(unit, escorted=True, sameArea=False, simulation=simulation)

	def retargetCivilian(self, civilian, army, simulation) -> bool:
		"""Start the civilian off to a new target plot"""
		# Find the best city site (taking into account whether we are escorted)
		betterTarget = self.findBestTarget(civilian, simulation)

		if betterTarget is None:
			# No targets at all!  Abort
			self.state = OperationStateType.aborted
			self.stateReason = OperationStateReason.noTarget
			return False

		if betterTarget.point != self.targetPosition:
			# If this is a new target, switch to it
			self.targetPosition = betterTarget.point
			self.army.goal = betterTarget.point

		self.army.state = ArmyState.movingToDestination
		self.state = OperationStateType.movingToTarget

		return True

	def isCivilianRequired(self) -> bool:
		return True


class NavalAttackOperation(NavalEscortedOperation):
	"""Attack a city from the sea"""
	def __init__(self):
		super().__init__(UnitOperationType.navalAttack)
		self.civilianType = UnitTaskType.none

	def formation(self, simulation) -> UnitFormationType:
		return UnitFormationType.navalInvasion

	def isCivilianRequired(self) -> bool:
		return False

	def initialize(self, player, enemy, area: Optional[HexArea], target: Optional[HexPoint], muster: Optional[HexPoint], simulation):
		"""Kick off this operation"""
		super().initialize(player, enemy, area, target, muster, simulation)

		self.moveType = OperationMoveType.navalEscort
		self.startPosition = muster

		if target is not None:
			self.targetPosition = target

			# create the armies that are needed and set the state to ARMYAISTATE_WAITING_FOR_UNITS_TO_REINFORCE
			self.army = Army(self.player, self, self.formation(simulation))
			self.army.state = ArmyState.waitingForUnitsToReinforce
			self.army.goal = target

			self.musterPosition = muster
			self.army.position = muster

			self.buildListOfUnitsWeStillNeedToBuild()

			# Try to get as many units as possible from existing units that are waiting around
			if self.grabUnitsFromTheReserves(muster, None, simulation):
				self.army.state = ArmyState.waitingForUnitsToCatchUp
				self.state = OperationStateType.gatheringForces
			else:
				self.state = OperationStateType.recruitingUnits
			# self.logOperationStart();
		else:
			# Lost our target, abort
			self.state = OperationStateType.aborted
			self.stateReason = OperationStateReason.lostTarget

		return

	def unitWasRemoved(self, army, slot: UnitFormationSlot):
		"""Always abort if settler is removed"""
		# Call root class version
		return super().unitWasRemoved(army, slot)

	def armyInPosition(self, simulation) -> bool:
		"""If at target, found city; if at muster point, merge settler and escort and move out"""
		if self.state == OperationStateType.movingToTarget:
			centerOfMass = self.army.centerOfMass(UnitDomainType.sea, simulation)
			if centerOfMass is not None:
				# Are we within tactical range of our target? (larger than usual range for a naval attack)
				if centerOfMass.distance(self.targetPosition) <= 4 * 2:  # AI_OPERATIONAL_CITY_ATTACK_DEPLOY_RANGE
					# Notify Diplo AI we're in place for attack
					self.player.diplomacyAI.updateMusteringForAttackAgainst(self.enemy, True)

					# Notify tactical AI to focus on this area
					zone = TemporaryZone(self.targetPosition, simulation.currentTurn + 5, TacticalTargetType.city, navalMission=True)
					self.player.tacticalAI.addTemporaryZone(zone)

					self.state = OperationStateType.successful
					return True
		# In all other cases use base class version
		elif self.state == OperationStateType.gatheringForces or self.state == OperationStateType.aborted or \
		     self.state == OperationStateType.recruitingUnits or self.state == OperationStateType.atTarget:
			return super().armyInPosition(simulation)

		return False

	def operationStartCity(self, simulation):
		"""Find the port our operation will leave from"""
		if self.startPosition is not None:
			return simulation.cityAt(self.startPosition)

		return self.player.militaryAI.nearestCoastalCityTowards(self.enemy, simulation)

	def findBestTarget(self, unit, simulation):
		"""Find the city we want to attack"""
		raise Exception("Obsolete function called CvAIOperationNavalAttack::FindBestTarget()")


class NavalOperation(EnemyTerritoryOperation):
	"""Send out a squadron of naval units to bomb enemy forces on the coast"""
	def __init__(self, operationType: UnitOperationType):
		super().__init__(operationType)

	def initialize(self, player, enemy, area: Optional[HexArea], target: Optional[HexPoint], muster: Optional[HexPoint], simulation):
		"""Kick off this operation override"""
		super().initialize(player, enemy, area, target, muster, simulation)

		self.moveType = OperationMoveType.enemyTerritory

		# create the armies that are needed and set the state to ARMYAISTATE_WAITING_FOR_UNITS_TO_REINFORCE
		self.army = Army(self.player, self, self.formation(simulation))
		self.army.state = ArmyState.waitingForUnitsToReinforce

		if target is not None:
			self.targetPosition = target
			self.army.goal = target

			# Muster just off the coast
			coastalMuster = simulation.coastalPlotAdjacent(muster)
			if coastalMuster is not None:
				self.defaultArea = coastalMuster.area()
				self.startPosition = coastalMuster.point
				self.musterPosition = coastalMuster.point
				self.army.position = coastalMuster.point

				# Find the list of units we need to build before starting this operation in earnest
				self.buildListOfUnitsWeStillNeedToBuild()

				# try to get as many units as possible from existing units that are waiting around
				if self.grabUnitsFromTheReserves(coastalMuster.point, coastalMuster.point, simulation):
					self.army.state = ArmyState.waitingForUnitsToCatchUp
					self.state = OperationStateType.gatheringForces
				else:
					self.state = OperationStateType.recruitingUnits

				# self.logOperationStart()
			else:
				# No muster point, abort
				self.state = OperationStateType.aborted
				self.stateReason = OperationStateReason.noMuster
		else:
			# Lost our target, abort
			self.state = OperationStateType.aborted
			self.stateReason = OperationStateReason.lostTarget

		return

	def formation(self, simulation) -> UnitFormationType:
		return UnitFormationType.navalSquadron  # MUFORMATION_NAVAL_SQUADRON

	def isAllNavalOperation(self) -> bool:
		return True

	def maximumRecruitTurns(self) -> int:
		"""Let naval units come from afar override"""
		return sys.maxsize

	def deployRange(self) -> int:
		"""How far out from the target city do we want to gather?"""
		return 4  # AI_OPERATIONAL_NAVAL_BOMBARDMENT_DEPLOY_RANGE

	def armyInPosition(self, simulation) -> bool:
		"""Same as default version except if just gathered forces and this operation never reaches a final target
		(just keeps attacking until dead or the operation is ended)"""
		if self.enemy is None or self.army is None:
			self.state = OperationStateType.aborted
			self.stateReason = OperationStateReason.noTarget

		stateChanged: bool = False

		if self.state == OperationStateType.gatheringForces:
			# If we were gathering forces, let's make sure a better target hasn't presented itself
			# First do base case processing
			stateChanged = super().armyInPosition(simulation)

			# Is target still under enemy control?
			if self.targetPosition is not None:
				targetTile = simulation.tileAt(self.targetPosition)

				if targetTile.hasOwner() and self.enemy != targetTile.owner():
					self.state = OperationStateType.aborted
					self.stateReason = OperationStateReason.targetAlreadyCaptured

		elif self.state == OperationStateType.movingToTarget:
			# See if within 2 spaces of our target, if so give control of these units to the tactical AI
			if self.army.position.distance(self.targetPosition) < 2:
				# Notify tactical AI to focus on this area
				zone = TemporaryZone(self.targetPosition, simulation.currentTurn + 5, TacticalTargetType.city)
				self.player.tacticalAI.addTemporaryZone(zone)

				self.state = OperationStateType.successful

		# In all other cases use base class version
		elif self.state == OperationStateType.aborted or self.state == OperationStateType.recruitingUnits or \
			self.state == OperationStateType.atTarget:
			return super().armyInPosition(simulation)


		return stateChanged

	def shouldAbort(self, simulation) -> bool:
		"""Returns true when we should abort the operation totally (besides when we have lost all units in it)"""
		# If parent says we're done, don't even check anything else
		rtnValue = super().shouldAbort(simulation)

		if not rtnValue:
			if self.targetPosition is None:
				return True

		if self.targetPosition is None or self.enemy is None:
			return False

		targetPlot = simulation.tileAt(self.targetPosition)

		# See if our target city is still owned by our enemy
		if not targetPlot.hasOwner() or self.enemy != targetPlot.owner():
			# Success! The city has been captured / destroyed
			return True

		return rtnValue

	def findBestTarget(self, simulation) -> Optional[HexPoint]:
		"""Find a plot next to the city we want to attack"""
		raise Exception("Obsolete function called CvAIOperationPureNavalCityAttack::FindBestTarget()")

	#  Which unit would we like to use to kick off this operation?
	def findInitialUnit(self, simulation):
		for loopUnit in simulation.unitsOf(self.player):
			# skip explorer
			if loopUnit.task() == UnitTaskType.exploreSea:
				continue

			if loopUnit.hasTask(UnitTaskType.attackSea) and loopUnit.army() is None:
				return loopUnit

		return None

	# Find the port our operation will leave from
	def operationStartCity(self, simulation):
		if self.startPosition is not None:
			return simulation.cityAt(self.startPosition)

		# Just find first coastal city
		for city in simulation.citiesOf(self.player):
			if simulation.isCoastalAt(city.location):
				return city

		return None


class NavalSuperiorityOperation(NavalOperation):
	"""Send out a squadron of naval units to rule the seas"""
	def __init__(self):
		super().__init__(UnitOperationType.navalSuperiority)

	def initialize(self, player, enemy, area: Optional[HexArea], target: Optional[HexPoint], muster: Optional[HexPoint], simulation):
		"""Kick off this operation"""
		super().initialize(player, enemy, area, target, muster, simulation)

		self.moveType = OperationMoveType.freeformNaval

		if self.operationStartCity(simulation) is not None:
			# create the armies that are needed and set the state to ARMYAISTATE_WAITING_FOR_UNITS_TO_REINFORCE
			self.army = Army(self.player, self, self.formation(simulation))
			self.army.state = ArmyState.waitingForUnitsToReinforce

			# Figure out the initial rally point
			targetPlot = self.findBestTarget(simulation)
			if targetPlot is not None:
				self.targetPosition = targetPlot
				self.army.goal = targetPlot

				if self.selectInitialMusterPoint(simulation) is not None:
					self.army.position = self.musterPosition
					self.area = simulation.areaOf(self.musterPosition)

					# Find the list of units we need to build before starting this operation in earnest
					self.buildListOfUnitsWeStillNeedToBuild()

					# try to get as many units as possible from existing units that are waiting around
					if self.grabUnitsFromTheReserves(self.musterPosition, self.musterPosition, simulation):
						self.army.state = ArmyState.waitingForUnitsToCatchUp
						self.state = OperationStateType.movingToTarget
					else:
						self.state = OperationStateType.recruitingUnits

					# self.logOperationStart()
				else:
					# No muster point, abort
					self.state = OperationStateType.aborted
					self.stateReason = OperationStateReason.noMuster
			else:
				# Lost our target, abort
				self.state = OperationStateType.aborted
				self.stateReason = OperationStateReason.lostTarget

		return

	def armyInPosition(self, simulation) -> bool:
		"""Same as default version except if just gathered forces and this operation never reaches a final target
		(just keeps attacking until dead or the operation is ended)"""
		stateChanged: bool = False

		# If we were gathering forces, let's make sure a better target hasn't presented itself
		if self.state == OperationStateType.gatheringForces or self.state == OperationStateType.movingToTarget:
			# First do base case processing
			stateChanged = super().armyInPosition(simulation)

			# Now revisit target
			possibleBetterTarget = self.findBestTarget(simulation)

			if possibleBetterTarget is None:
				# If no target left, abort
				self.state = OperationStateType.aborted
				self.stateReason = OperationStateReason.noTarget
			# If target changed, reset to this new one
			elif possibleBetterTarget != self.targetPosition:
				pathFinderDataSource = simulation.ignoreUnitsPathfinderDataSource(
					UnitMovementType.swim,
					self.player,
					canEmbark=True,
					canEnterOcean=self.player.canEnterOcean()
				)
				pathFinder = AStarPathfinder(pathFinderDataSource)

				# Reset our destination to be a few plots shy of the final target
				path = pathFinder.shortestPath(self.army.position, possibleBetterTarget)
				if path is not None:
					reducedPath: HexPath = path.pathWithout(self.deployRange())
					deployPoint = lastOrNone(reducedPath.points())

					if deployPoint is not None:
						self.army.goal = deployPoint
						self.targetPosition = deployPoint

		# In all other cases use base class version
		elif self.state == OperationStateType.aborted or self.state == OperationStateType.recruitingUnits or \
			self.state == OperationStateType.atTarget:
			return super().armyInPosition(simulation)

		return stateChanged

	def reachablePlotFor(self, unit, plots: WeightedBaseList, simulation) -> (Optional[HexPoint], int):
		"""Return the first reachable plot in the weighted plot list.
		It is assumed that the list has yet to be sorted and will do so."""
		bestPointRef: Optional[HexPoint] = None
		bestWeight = sys.maxsize
		bestTurns = 0

		pathFinderDataSource = simulation.ignoreUnitsPathfinderDataSource(
			UnitMovementType.swim,
			self.player,
			canEmbark=True,
			canEnterOcean=self.player.canEnterOcean()
		)
		pathFinder = AStarPathfinder(pathFinderDataSource)

		if len(plots.values()) > 0:
			# This will check all the plots that have the same weight.It will mean a few more path-finds, but it will
			# be more accurate.
			for plot, weight in plots.items():
				if bestPointRef is not None:
					# Already found one of a lower weight
					if weight > bestWeight:
						break

					turnsCalculated = pathFinder.turnsToReachTarget(unit, plot, simulation)

					if turnsCalculated != sys.maxsize:
						if turnsCalculated < bestTurns:
							bestWeight = weight
							bestPointRef = plot
							bestTurns = turnsCalculated

							if bestTurns == 1:
								# Not getting better than this
								break
				else:
					turnsCalculated = pathFinder.turnsToReachTarget(unit, plot, simulation)

					if turnsCalculated != sys.maxsize:
						bestWeight = weight
						bestPointRef = plot
						bestTurns = turnsCalculated

						if bestTurns == 1:
							# Not getting better than this
							break

		if bestPointRef is not None:
			return bestPointRef, bestTurns

		return None, -1

	def findBestTarget(self, simulation) -> Optional[HexPoint]:
		"""Find the nearest enemy naval unit to eliminate"""
		bestPlot: Optional[HexPoint] = None
		closestEnemyDistance: int = sys.maxsize
		enemyCoastalCity = None

		closestCampDistance: int = sys.maxsize
		coastalBarbarianCamp = None
		weightedPoints = WeightedBaseList()
		initialUnit = None

		if self.army is not None:
			firstArmyUnit = self.army.unitAt(0)
			if firstArmyUnit is not None:
				initialUnit = firstArmyUnit
			else:
				initialUnit = self.findInitialUnit(simulation)
		else:
			initialUnit = self.findInitialUnit(simulation)

		if initialUnit is not None:
			baseMoves = initialUnit.maxMoves(simulation)

			# Look at map for enemy naval units
			for loopPoint in simulation.points():
				loopPlot = simulation.tileAt(loopPoint)

				if loopPlot.isDiscoveredBy(self.player):
					if loopPlot.isWater():
						# handle multiple units at one plot
						for loopUnit in simulation.unitsAt(loopPoint):
							if loopUnit.player.isEnemyOf(self.player):
								plotDistance = initialUnit.location.distance(loopPoint)
								score = baseMoves * plotDistance

								if loopUnit.isTrading():
									# we want to plunder trade routes of possible
									score /= 3

								if loopUnit.isEmbarked():
									# we want to take out embarked units more than ships
									score = (score * 2) / 3

								weightedPoints.addWeight(score, loopPoint)
					elif simulation.cityAt(loopPoint) is not None and simulation.isCoastalAt(loopPoint):
						# Backup plan is a coastal enemy city
						city = simulation.cityAt(loopPoint)
						if city is not None:
							if self.player.isAtWarWith(city.player):
								distance = initialUnit.location.distance(city.location)

								if distance < closestEnemyDistance:
									closestEnemyDistance = distance
									enemyCoastalCity = city
					elif simulation.isCoastalAt(loopPoint) and loopPlot.hasImprovement(ImprovementType.barbarianCamp):
						distance = initialUnit.location.distance(loopPoint)
						if distance < closestCampDistance:
							closestCampDistance = distance
							coastalBarbarianCamp = loopPlot

			bestTurns: int = -1
			bestPlot, bestTurns = self.reachablePlotFor(initialUnit, weightedPoints, simulation)

			# None found, patrol over near closest enemy coastal city, or if not that a water tile adjacent to a camp
			if bestPlot is None:
				if enemyCoastalCity is not None:
					# Find a coastal water tile adjacent to enemy city
					for adjacentPoint in enemyCoastalCity.location.neighbors():
						adjacentPlot = simulation.tileAt(adjacentPoint)

						if adjacentPlot is None:
							continue

						if adjacentPlot.terrain() == TerrainType.shore:
							if initialUnit.pathTowards(adjacentPoint, options=[], simulation=simulation) is not None:
								bestPlot = adjacentPoint
				else:
					if coastalBarbarianCamp is not None:
						# Find a coastal water tile adjacent to camp
						for adjacentPoint in coastalBarbarianCamp.point.neighbors():
							adjacentPlot = simulation.tileAt(adjacentPoint)

							if adjacentPlot is None:
								continue

							if adjacentPlot.terrain() == TerrainType.shore:
								if initialUnit.pathTowards(adjacentPoint, options=[], simulation=simulation) is not None:
									bestPlot = adjacentPoint

		return bestPlot


	def canTacticalAIInterruptOperation(self) -> bool:
		return True


class NavalBombardmentOperation(Operation):
	def __init__(self):
		super().__init__(UnitOperationType.navalBombard)


class NavalEscortedOperation(Operation):
	def __init__(self):
		super().__init__(UnitOperationType.colonize)  # ???
		self.civilianType = UnitTaskType.settle


class QuickColonizeOperation(Operation):
	def __init__(self):
		super().__init__(UnitOperationType.quickColonize)


class PureNavalCityAttackOperation(Operation):
	def __init__(self):
		super().__init__(UnitOperationType.pureNavalCityAttack)


class SmallCityAttackOperation(Operation):
	def __init__(self):
		super().__init__(UnitOperationType.smallCityAttack)


class QuickSneakCityAttackOperation(BasicCityAttackOperation):
	def __init__(self):
		super().__init__(UnitOperationType.sneakCityAttack)


class QuickSneakCityAttackOperation(Operation):
	def __init__(self):
		super().__init__(UnitOperationType.sneakCityAttack)


class SneakCityAttackOperation(Operation):
	def __init__(self):
		super().__init__(UnitOperationType.sneakCityAttack)


class NavalSneakAttackOperation(Operation):
	def __init__(self):
		super().__init__(UnitOperationType.navalSneakAttack)


class UnitFormationHelper:

	@staticmethod
	def numberOfFillableSlots(units, formation: UnitFormationType) -> (int, int, int):

		numberSlotsRequired: int = 0
		numberLandReservesUsed: int = 0
		willBeFilled: int = 0

		slots = formation.slots()

		for unit in units:

			# Don't count scouts
			if unit.task() == UnitTaskType.explore or unit.task() == UnitTaskType.exploreSea:
				continue

			# can't use unit in an army
			if unit.army() is not None:
				continue

			for slot in slots:
				if unit.task() == slot.primaryUnitTask or unit.task() == slot.secondaryUnitTask:
					slot.filled = True

					willBeFilled += 1

					if unit.domain() == UnitDomainType.land:
						numberLandReservesUsed += 1

		# Now go back through remaining slots and see how many were required, we'll need that many more units
		for slot in slots:
			if slot.required and not slot.filled:
				numberSlotsRequired += 1

		return numberSlotsRequired, numberLandReservesUsed, willBeFilled
