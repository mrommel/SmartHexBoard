import logging
import sys
from typing import Optional

from smarthexboard.smarthexboardlib.core.base import WeightedBaseList
from smarthexboard.smarthexboardlib.game.ai.baseTypes import MilitaryStrategyType, PlayerStateAllWars, DefenseState
from smarthexboard.smarthexboardlib.game.ai.economicStrategies import EconomicStrategyType
from smarthexboard.smarthexboardlib.game.ai.economics import PurchaseType
from smarthexboard.smarthexboardlib.game.ai.grandStrategies import GrandStrategyAIType
from smarthexboard.smarthexboardlib.game.ai.militaryStrategies import MilitaryStrategyAdoptions
from smarthexboard.smarthexboardlib.game.ai.militaryTypes import MilitaryThreatType, UnitFormationSlot, ArmyType, MilitaryTarget, OperationStateType, \
	AttackApproachType
from smarthexboard.smarthexboardlib.game.baseTypes import PlayerWarStateType, StrengthType, PlayerTargetValueType, HandicapType
from smarthexboard.smarthexboardlib.game.buildings import BuildingType
from smarthexboard.smarthexboardlib.game.cities import City
from smarthexboard.smarthexboardlib.game.flavors import Flavors, FlavorType
from smarthexboard.smarthexboardlib.game.operations import OperationStateReason, UnitFormationHelper, UnitFormationType, Operation
from smarthexboard.smarthexboardlib.game.unitTypes import UnitDomainType, UnitTaskType, UnitMapType, UnitOperationType, UnitType
from smarthexboard.smarthexboardlib.map.base import HexPoint
from smarthexboard.smarthexboardlib.map.improvements import ImprovementType
from smarthexboard.smarthexboardlib.map.path_finding.finder import AStarPathfinder
from smarthexboard.smarthexboardlib.map.types import YieldType, TerrainType, UnitMovementType, FeatureType
from smarthexboard.smarthexboardlib.utils.base import firstOrNone


class MilitaryBaseData:
	def __init__(self):
		self.numLandUnits = 0
		self.numRangedLandUnits = 0
		self.numMobileLandUnits = 0
		# var numAirUnits = 0
		# var numAntiAirUnits = 0
		self.numMeleeLandUnits = 0
		self.numNavalUnits = 0
		self.numLandUnitsInArmies = 0
		self.numNavalUnitsInArmies = 0
		self.recommendedMilitarySize = 0
		self.mandatoryReserveSize = 0

	def reset(self):
		self.numLandUnits = 0
		self.numRangedLandUnits = 0
		self.numMobileLandUnits = 0
		# self.numAirUnits = 0
		# self.numAntiAirUnits = 0
		self.numMeleeLandUnits = 0
		self.numNavalUnits = 0
		self.numLandUnitsInArmies = 0
		self.numNavalUnitsInArmies = 0
		self.recommendedMilitarySize = 0
		self.mandatoryReserveSize = 0


class BarbarianData:
	def __init__(self):
		self.barbarianCampCount = 0
		self.visibleBarbarianCount = 0

	def reset(self):
		self.barbarianCampCount = 0
		self.visibleBarbarianCount = 0


class MilitaryAIHelpers:
	@staticmethod
	def computeRecommendedNavySize(player, simulation) -> int:
		"""How many military units should we have given current threats?"""
		iFlavorNaval: int = player.grandStrategyAI.personalityAndGrandStrategy(FlavorType.naval)
		# cap at 10?

		# Start with 1
		iNumUnitsWanted: int = 1
		iNumCoastalCities: int = 0

		for loopCity in simulation.citiesOf(player):
			if loopCity.isCoastal(simulation):
				iNumCoastalCities += 1

		iNumUnitsWanted += iNumCoastalCities
		# Scale up or down based on true threat level and a bit by flavors (multiplier should range from about 0.75 to 2.0)
		dMultiplier = 0.75 + (player.militaryAI.highestThreat(simulation).value() / 4.0) + (float(iFlavorNaval) / 40.0)
		iNumUnitsWanted = int(float(iNumUnitsWanted) * dMultiplier * 0.67)  # AI_STRATEGY_NAVAL_UNITS_PER_CITY

		iNumUnitsWanted = max(1, iNumUnitsWanted)

		if player.economicAI.isUsingStrategy(EconomicStrategyType.navalMap) or \
			player.economicAI.isUsingStrategy(EconomicStrategyType.expandToOtherContinents):
			iNumUnitsWanted *= 3
			iNumUnitsWanted /= 2

		if player.leader.civilization().isCoastalCiv():
			iNumUnitsWanted *= 3
			iNumUnitsWanted /= 2

		# if we are going for conquest we want at least one more task force
		iGT = simulation.currentTurn
		iGT = min(iGT, 200)
		if player.grandStrategyAI.activeStrategy == GrandStrategyAIType.conquest:
			iNumUnitsWanted += (10 * iGT) / 200

		return iNumUnitsWanted

	@classmethod
	def numberOfFillableSlots(cls, player, formation: UnitFormationType, requiresNavalMoves: bool, simulation) -> (int, int, int):
		"""How many slots in this army can we fill right now with available units?"""
		willBeFilled = 0
		landReservesUsed = 0
		slotsToFill = formation.slots()
		slotsNotFilled: [UnitFormationSlot] = []

		mustBeDeepWaterNaval: bool = player.canEnterOcean() and formation.isRequiresNavalUnitConsistency()

		for loopUnit in simulation.unitsOf(player):
			# Don't count scouts
			if loopUnit.task() != UnitTaskType.explore and loopUnit.task() != UnitTaskType.exploreSea:
				# Don't count units that are damaged too heavily
				if loopUnit.healthPoints() > loopUnit.maxHealthPoints() * 80 / 100:  # AI_OPERATIONAL_PERCENT_HEALTH_FOR_OPERATION
					if loopUnit.army() is None and loopUnit.canRecruitFromTacticalAI():
						if loopUnit.deployFromOperationTurn() + 4 < simulation.currentTurn:  # AI_TACTICAL_MAP_TEMP_ZONE_TURNS
							if not requiresNavalMoves or loopUnit.domain() == UnitDomainType.sea or loopUnit.canEverEmbark():
								if not mustBeDeepWaterNaval or loopUnit.domain() != UnitDomainType.sea or not loopUnit.isImpassableTerrain(TerrainType.ocean):
									for slotEntry in slotsToFill:
										if loopUnit.hasTask(slotEntry.primaryUnitTask) or loopUnit.hasTask(slotEntry.secondaryUnitTask):
											willBeFilled += 1

											if loopUnit.domain() == UnitDomainType.land:
												landReservesUsed += 1
												break
										else:
											slotsNotFilled.append(slotEntry)

		# Now go back through remaining slots and see how many were required, we'll need that many more units
		numberSlotsRequired = willBeFilled
		for slotNotFilled in slotsNotFilled:
			if slotNotFilled.required:
				numberSlotsRequired += 1

		numberLandReservesUsed = landReservesUsed

		return willBeFilled, numberSlotsRequired, numberLandReservesUsed

	@classmethod
	def firstSlotCityCanFill(cls, player, formation: UnitFormationType, requiresNavalMoves: bool, atCoastalCity: bool, secondaryUnit: bool, simulation) -> UnitTaskType:
		"""Army needs more units, which should we build next?"""
		slotsToFill = formation.slots()

		mustBeDeepWaterNaval: bool = player.canEmbarkAllWaterPassage() and formation.isRequiresNavalUnitConsistency()

		for loopUnit in simulation.unitsOf(player):
			# Don't count scouts
			if loopUnit.task() == UnitTaskType.explore or loopUnit.task() == UnitTaskType.exploreSea:
				continue

			# Don't count units that are damaged too heavily
			if loopUnit.healthPoints() < (loopUnit.maxHealthPoints() * 80 / 100):  # AI_OPERATIONAL_PERCENT_HEALTH_FOR_OPERATION
				continue

			if loopUnit.army() is None and loopUnit.canRecruitFromTacticalAI():
				if loopUnit.deployFromOperationTurn() + 4 < simulation.currentTurn:  # AI_TACTICAL_MAP_TEMP_ZONE_TURNS
					if not requiresNavalMoves or loopUnit.domain() == UnitDomainType.sea or loopUnit.canEverEmbark():
						if not mustBeDeepWaterNaval or loopUnit.domain() != UnitDomainType.sea or not loopUnit.isImpassableTerrain(TerrainType.ocean):
							for idx, slotEntry in enumerate(slotsToFill):
								if loopUnit.hasTask(slotEntry.primaryUnitTask) or loopUnit.hasTask(slotEntry.secondaryUnitTask):
									del slotsToFill[idx]
									break

		# If coastal city, try to find the first one that is a naval AI type
		if atCoastalCity:
			for thisSlotIndex, slotEntry in enumerate(slotsToFill):
				if slotEntry.required:
					task: UnitTaskType = slotEntry.primaryUnitTask
					if task == UnitTaskType.assaultSea or task == UnitTaskType.attackSea or task == UnitTaskType.reserveSea or task == UnitTaskType.escortSea:
						if not secondaryUnit:
							return slotEntry.primaryUnitTask
						else:
							return slotEntry.secondaryUnitTask

		# Now go back through remaining slots and find first required one
		for thisSlotIndex, slotEntry in enumerate(slotsToFill):
			if slotEntry.required:
				if not secondaryUnit:
					return slotEntry.primaryUnitTask
				else:
					return slotEntry.secondaryUnitTask

		return UnitTaskType.none
	

class MilitaryAI:
	def __init__(self, player):

		self.player = player
		self.militaryStrategyAdoption = MilitaryStrategyAdoptions()
		self.baseData = MilitaryBaseData()
		self._barbarianDataValue = BarbarianData()
		self._flavors = Flavors()
		self._totalThreatWeight: int = 0

		self._landDefenseState: DefenseState = DefenseState.none
		self._navalDefenseState: DefenseState = DefenseState.none

		self._armyTypeBeingBuilt: ArmyType = ArmyType.none
		self._numberOfLandAttacksRequested: int = 0
		self._numberOfNavalAttacksRequested: int = 0

	def doTurn(self, simulation):
		self.updateBaseData(simulation)
		self.updateBarbarianData(simulation)
		self.updateDefenseState(simulation)
		self.updateMilitaryStrategies(simulation)
		self.updateThreats(simulation)

		if not self.player.isHuman():
			self.updateOperations(simulation)
			# self.makeEmergencyPurchases()
			# self.requestImprovements()
			# self.disbandObsoleteUnits()

	def updateBaseData(self, simulation):
		self.baseData.reset()

		for unit in simulation.unitsOf(self.player):
			# Don't count exploration units
			if unit.task() == UnitTaskType.explore or unit.task() == UnitTaskType.exploreSea:
				continue

			# Don't count civilians
			if not unit.hasTask(UnitTaskType.attack):
				continue

			if unit.domain() == UnitDomainType.land:
				self.baseData.numLandUnits += 1

				if unit.hasTask(UnitTaskType.ranged):
					self.baseData.numRangedLandUnits += 1

				if unit.moves() > 2:
					self.baseData.numMobileLandUnits += 1

			elif unit.domain() == UnitDomainType.sea:
				self.baseData.numNavalUnits += 1

		flavorOffense = float(self.player.valueOfStrategyAndPersonalityFlavor(FlavorType.offense))
		flavorDefense = float(self.player.valueOfStrategyAndPersonalityFlavor(FlavorType.defense))

		# Scale up or down based on true threat level and a bit by flavors(multiplier should range from about 0.5 to
		# about 1.5)
		multiplier = (0.40 + float(self.highestThreat(simulation).value()) + flavorOffense + flavorDefense) / 100.0

		# first get the number of defenders that we think we need

		# Start with 3, to protect the capital
		numUnitsWanted = 3.0

		# 1 Unit per City & 1 per Settler
		numUnitsWanted += float(len(simulation.citiesOf(self.player))) * 1.0
		allUnits = simulation.unitsOf(self.player)
		settlers = list(filter(lambda unit: unit.task() == UnitTaskType.settle, allUnits))
		numUnitsWanted += float(len(settlers)) * 1.0

		self.baseData.mandatoryReserveSize = int(float(numUnitsWanted) * multiplier)

		# add in a few for the difficulty level (all above Chieftain are boosted)
		# int iDifficulty = max(0, GC.getGame().getHandicapInfo().GetID() - 1);
		# m_iMandatoryReserveSize += (iDifficulty * 3 / 2);

		self.baseData.mandatoryReserveSize = max(1, self.baseData.mandatoryReserveSize)

		# now we add in the strike forces we think we will need
		numUnitsWanted = 7  # size of a basic attack

		# if we are going for conquest we want at least one more task force
		if self.player.grandStrategyAI.activeStrategy == GrandStrategyAIType.conquest:
			numUnitsWanted *= 2

		# add in a few more if the player is bold
		numUnitsWanted += float(self.player.leader.boldness())

		# add in more if we are playing on a high difficulty
		# iNumUnitsWanted += iDifficulty * 3

		numUnitsWanted *= multiplier

		numUnitsWanted = max(1, numUnitsWanted)

		self.baseData.recommendedMilitarySize = self.baseData.mandatoryReserveSize + int(numUnitsWanted)

	def highestThreat(self, simulation) -> MilitaryThreatType:
		# See if the threats we are facing have changed
		highestThreatByPlayer: MilitaryThreatType = MilitaryThreatType.none

		for otherPlayer in simulation.players:
			if otherPlayer == self.player:
				continue

			if not self.player.hasMetWith(otherPlayer):
				continue

			threat = self.player.diplomacyAI.militaryThreatOf(otherPlayer)

			if highestThreatByPlayer.value() < threat.value():
				highestThreatByPlayer = threat

		return highestThreatByPlayer

	def barbarianData(self) -> BarbarianData:
		return self._barbarianDataValue

	def updateBarbarianData(self, simulation):
		self._barbarianDataValue.reset()

		for point in simulation.points():
			tile = simulation.tileAt(point)

			if tile.isDiscoveredBy(self.player):
				if tile.hasImprovement(ImprovementType.barbarianCamp):
					self._barbarianDataValue.barbarianCampCount += 1

					# Count it as 5 camps if sitting inside our territory, that is annoying!
					if tile.hasOwner() and self.player == tile.owner():
						self._barbarianDataValue.barbarianCampCount += 4

			if tile.isVisibleTo(self.player):
				unit = simulation.unitAt(point, UnitMapType.combat)
				if unit is not None:
					if unit.isBarbarian() and unit.unitType == UnitMapType.combat:
						self._barbarianDataValue.visibleBarbarianCount += 1

	def updateDefenseState(self, simulation):
		"""Update how we're doing on defensive units"""
		# Derive data we'll need
		iLandUnitsNotInArmies: int = self.baseData.numLandUnits
		iNavalUnitsNotInArmies: int = self.baseData.numNavalUnits

		if iLandUnitsNotInArmies < self.baseData.mandatoryReserveSize:
			self._landDefenseState = DefenseState.critical  # DEFENSE_STATE_CRITICAL
		elif iLandUnitsNotInArmies < self.baseData.recommendedMilitarySize:
			self._landDefenseState = DefenseState.needed  # DEFENSE_STATE_NEEDED
		elif iLandUnitsNotInArmies < self.baseData.recommendedMilitarySize * 5 / 4:
			self._landDefenseState = DefenseState.neutral  # DEFENSE_STATE_NEUTRAL
		else:
			self._landDefenseState = DefenseState.enough  # DEFENSE_STATE_ENOUGH;

		iNavySize = MilitaryAIHelpers.computeRecommendedNavySize(self.player, simulation)

		if iNavalUnitsNotInArmies <= (iNavySize / 2):
			self._navalDefenseState = DefenseState.critical  # DEFENSE_STATE_CRITICAL
		elif iNavalUnitsNotInArmies <= iNavySize:
			self._navalDefenseState = DefenseState.needed  # DEFENSE_STATE_NEEDED;
		elif iNavalUnitsNotInArmies <= iNavySize * 5 / 4:
			self._navalDefenseState = DefenseState.neutral  # DEFENSE_STATE_NEUTRAL
		else:
			self._navalDefenseState = DefenseState.enough  # DEFENSE_STATE_ENOUGH

		return

	def adopted(self, militaryStrategy: MilitaryStrategyType) -> bool:
		return self.militaryStrategyAdoption.adopted(militaryStrategy)

	def updateMilitaryStrategies(self, simulation):
		for militaryStrategyType in list(MilitaryStrategyType):
			# Minor Civs can't run some Strategies
			if self.player.isCityState() and militaryStrategyType.isNoMinorCivs():
				continue

			# Some strategies ONLY for Minor Civs
			if not self.player.isCityState() and militaryStrategyType.isOnlyMinorCivs():
				continue

			# check tech
			requiredTech = militaryStrategyType.requiredTech()
			isTechGiven = True if requiredTech is None else self.player.hasTech(requiredTech)
			obsoleteTech = militaryStrategyType.obsoleteTech()
			isTechObsolete = False if obsoleteTech is None else self.player.hasTech(obsoleteTech)

			# Do we already have this EconomicStrategy adopted?
			shouldCityStrategyStart = True
			if self.militaryStrategyAdoption.adopted(militaryStrategyType):
				shouldCityStrategyStart = False
			elif not isTechGiven:
				shouldCityStrategyStart = False
			elif simulation.currentTurn < militaryStrategyType.notBeforeTurnElapsed():  # Not time to check this yet?
				shouldCityStrategyStart = False

			shouldCityStrategyEnd = False
			if self.militaryStrategyAdoption.adopted(militaryStrategyType):
				if militaryStrategyType.checkEachTurns() > 0:
					# Is it a turn where we want to check to see if this Strategy is maintained?
					if simulation.currentTurn - self.militaryStrategyAdoption.turnOfAdoptionOf(militaryStrategyType) % militaryStrategyType.checkEachTurns() == 0:
						shouldCityStrategyEnd = True

				if shouldCityStrategyEnd and militaryStrategyType.minimumAdoptionTurns() > 0:
					# Has the minimum # of turns passed for this Strategy?
					if simulation.currentTurn < self.militaryStrategyAdoption.turnOfAdoptionOf(militaryStrategyType) + militaryStrategyType.minimumAdoptionTurns():
						shouldCityStrategyEnd = False

			# Check EconomicStrategy Triggers
			# Functionality and existence of specific CityStrategies is hardcoded here, but data is stored in XML,
			# so it's easier to modify
			if shouldCityStrategyStart or shouldCityStrategyEnd:
				# Has the Tech which obsoletes this Strategy? If so, Strategy should be deactivated regardless of other factors
				strategyShouldBeActive = False

				# Strategy isn't obsolete, so test triggers as normal
				if not isTechObsolete:
					strategyShouldBeActive = militaryStrategyType.shouldBeActiveFor(self.player, simulation)

				# This variable keeps track of whether we should be doing something(i.e.Strategy is active now
				# but should be turned off, OR Strategy is inactive and should be enabled)
				bAdoptOrEndStrategy = False

				# Strategy should be on, and if it's not, turn it on
				if strategyShouldBeActive:
					if shouldCityStrategyStart:
						bAdoptOrEndStrategy = True
					elif shouldCityStrategyEnd:
						bAdoptOrEndStrategy = False
				else:
					# Strategy should be off, and if it's not, turn it off
					if shouldCityStrategyStart:
						bAdoptOrEndStrategy = False
					elif shouldCityStrategyEnd:
						bAdoptOrEndStrategy = True

				if bAdoptOrEndStrategy:
					if shouldCityStrategyStart:
						self.militaryStrategyAdoption.adopt(militaryStrategyType, turnOfAdoption=simulation.currentTurn)
						logging.info(f'Player {self.player.leader} has adopted {militaryStrategyType} in turn {simulation.currentTurn}')
					elif shouldCityStrategyEnd:
						self.militaryStrategyAdoption.abandon(militaryStrategyType)
						logging.info(f'Player {self.player.leader} has abandoned {militaryStrategyType} in turn {simulation.currentTurn}')

		self.updateFlavors()

		# logging.info("military strategy flavors")
		# logging.info(self.flavors)

	def updateThreats(self, simulation):
		diplomacyAI = self.player.diplomacyAI

		self._totalThreatWeight = 0

		for otherPlayer in simulation.players:
			# Is this a player we have relations with?
			if self.player == otherPlayer:
				continue

			if not self.player.hasMetWith(otherPlayer):
				continue

			threat = diplomacyAI.militaryThreatOf(otherPlayer)
			self._totalThreatWeight += threat.weight()

		return

	def updateOperations(self, simulation):
		diplomacyAI = self.player.diplomacyAI

		# SEE IF THERE ARE OPERATIONS THAT NEED TO BE ABORTED

		# Are we willing to risk pressing forward vs. barbarians?
		willingToAcceptRisk = (self._totalThreatWeight / 2) < self.barbarianThreatTotal()
		# if self.player.leader.ability() ==.convertLandBarbarians
		#    willingToAcceptRisk = True

		#
		# Operations vs.Barbarians
		#
		# If we have aborted the eradicate barbarian strategy or if the threat level from civilisations is
		# significantly higher than from barbs, we better abort all of them
		if not self.adopted(MilitaryStrategyType.eradicateBarbarians) or self.adopted(MilitaryStrategyType.atWar) or \
			not willingToAcceptRisk:

			for operation in self.player.operationsOfType(UnitOperationType.destroyBarbarianCamp):
				operation.kill(OperationStateReason.warStateChange)

		#
		# Operation vs.Other Civilisations
		#
		# Are our wars over?
		if not self.adopted(MilitaryStrategyType.atWar):
			for operation in self.player.operationsOfType(UnitOperationType.basicCityAttack):
				operation.kill(OperationStateReason.warStateChange)

			for operation in self.player.operationsOfType(UnitOperationType.pillageEnemy):
				operation.kill(OperationStateReason.warStateChange)

			for operation in self.player.operationsOfType(UnitOperationType.rapidResponse):
				operation.kill(OperationStateReason.warStateChange)

			for operation in self.player.operationsOfType(UnitOperationType.cityCloseDefense):
				operation.kill(OperationStateReason.warStateChange)

			for operation in self.player.operationsOfType(UnitOperationType.navalAttack):
				operation.kill(OperationStateReason.warStateChange)
		else:
			# Are any of our strategies inappropriate given the type of war we are fighting
			for otherPlayer in simulation.players:
				# Is this a player we have relations with?
				if self.player != otherPlayer and self.player.hasMetWith(otherPlayer):

					# If we've made peace with this player, abort all operations related to him
					# added the check for STATE_ALL_WARS_LOSING so that if the player is losing all wars,
					# that they will cancel scheduled attacks
					if self.player.isForcePeaceWith(otherPlayer) or diplomacyAI.stateOfAllWars == PlayerStateAllWars.losing:
						operation = self.sneakAttackOperationAgainst(otherPlayer)
						if operation is not None:
							operation.kill(OperationStateReason.warStateChange)

						operation = self.basicAttackOperationAgainst(otherPlayer)
						if operation is not None:
							operation.kill(OperationStateReason.warStateChange)

						operation = self.showOfForceOperationAgainst(otherPlayer)
						if operation is not None:
							operation.kill(OperationStateReason.warStateChange)

						operation = self.pureNavalAttackOperationAgainst(otherPlayer)
						if operation is not None:
							operation.kill(OperationStateReason.warStateChange)

					warState: PlayerWarStateType = diplomacyAI.warStateTowards(otherPlayer)

					if warState == PlayerWarStateType.nearlyDefeated:
						# If nearly defeated, call off all operations in enemy territory
						for operation in self.player.operationsOfType(UnitOperationType.basicCityAttack):
							if operation.enemy == otherPlayer:
								operation.kill(OperationStateReason.warStateChange)

						for operation in self.player.operationsOfType(UnitOperationType.pillageEnemy):
							if operation.enemy == otherPlayer:
								operation.kill(OperationStateReason.warStateChange)

						for operation in self.player.operationsOfType(UnitOperationType.navalAttack):
							if operation.enemy == otherPlayer:
								operation.kill(OperationStateReason.warStateChange)

					elif warState == PlayerWarStateType.defensive:
						# If we are losing, make sure attacks are not running
						for operation in self.player.operationsOfType(UnitOperationType.basicCityAttack):
							if operation.enemy == otherPlayer:
								operation.kill(OperationStateReason.warStateChange)

						for operation in self.player.operationsOfType(UnitOperationType.pillageEnemy):
							if operation.enemy == otherPlayer:
								operation.kill(OperationStateReason.warStateChange)

						for operation in self.player.operationsOfType(UnitOperationType.navalAttack):
							if operation.enemy == otherPlayer:
								operation.kill(OperationStateReason.warStateChange)

					elif warState == PlayerWarStateType.offensive or warState == PlayerWarStateType.nearlyWon:
						# If we are dominant, shouldn't be running a defensive strategy
						for operation in self.player.operationsOfType(UnitOperationType.rapidResponse):
							if operation.enemy == otherPlayer:
								operation.kill(OperationStateReason.warStateChange)

						for operation in self.player.operationsOfType(UnitOperationType.cityCloseDefense):
							if operation.enemy == otherPlayer:
								operation.kill(OperationStateReason.warStateChange)

					elif warState == PlayerWarStateType.stalemate or warState == PlayerWarStateType.calm or \
						warState == PlayerWarStateType.none:
						# NOOP
						pass

			# Are there city defense operations for cities that no longer need defending?
			for city in simulation.citiesOf(self.player):
				if city.threatValue() == 0:
					for operation in self.player.operationsOfType(UnitOperationType.cityCloseDefense):
						if operation.targetPosition == city.location:
							operation.kill(OperationStateReason.warStateChange)

			# Are we running a rapid response tactic and the overall threat level is very low?
			if self._totalThreatWeight <= 3:
				for operation in self.player.operationsOfType(UnitOperationType.rapidResponse):
					operation.kill(OperationStateReason.warStateChange)

		# SEE WHAT OPERATIONS WE SHOULD ADD
		#
		# Operation vs.Barbarians
		#
		# If running the eradicate barbarian strategy, the threat is low (no higher than 1 major threat),
		# we're not at war, /*and we have enough units*/, then launch a new operation.
		# Which one is based on whether we saw any barbarian camps
		if self.adopted(MilitaryStrategyType.eradicateBarbarians) and not self.adopted(MilitaryStrategyType.atWar) and \
			not self.adopted(MilitaryStrategyType.empireDefenseCritical) and \
			len(self.player.operationsOfType(UnitOperationType.destroyBarbarianCamp)) == 0 and willingToAcceptRisk:

			# We should have AI build for this
			self.player.addOperation(
				UnitOperationType.destroyBarbarianCamp,
				simulation.barbarianPlayer(),
				None,
				None,
				None,
				simulation
			)

		# Operation vs.Other Civilisations
		# If at war, consider launching an operation
		if self.adopted(MilitaryStrategyType.atWar):
			for otherPlayer in simulation.players:
				# Is this a player we have relations with?
				if self.player != otherPlayer and self.player.hasMetWith(otherPlayer):
					warState: PlayerWarStateType = diplomacyAI.warStateTowards(otherPlayer)

					# always consider nuking them
					# FIXME

					if warState == PlayerWarStateType.none:
						# NOOP
						pass

					elif warState == PlayerWarStateType.nearlyDefeated or warState == PlayerWarStateType.defensive:
						# NOOP
						threatenedCity = self.mostThreatenedCity(simulation)
						# fixme
						pass

					elif warState == PlayerWarStateType.stalemate:
						# If roughly equal in number, let's try to annoy him with raids
						unitsList = simulation.unitsOf(self.player)
						(numRequiredSlots, _, filledSlots) = UnitFormationHelper.numberOfFillableSlots(unitsList, UnitFormationType.fastPillagers)

						# Not willing to build units to get this off the ground
						if filledSlots >= numRequiredSlots:  # and landReservesUsed <= self.landReservesAvailable(): fixme
							self.requestPillageEnemyTowards(otherPlayer, simulation)

					elif warState == PlayerWarStateType.calm:
						requestAttack = False
						militaryStrength: StrengthType = diplomacyAI.militaryStrengthOf(otherPlayer)
						targetValue: PlayerTargetValueType = diplomacyAI.targetValueOf(otherPlayer)

						if militaryStrength <= StrengthType.average and targetValue > PlayerTargetValueType.impossible:
							requestAttack = True

						if requestAttack:
							self.requestBasicAttackTowards(otherPlayer, simulation=simulation)
						else:
							unitsList = simulation.unitsOf(self.player)
							(numRequiredSlots, _, filledSlots) = UnitFormationHelper.numberOfFillableSlots(unitsList, UnitFormationType.fastPillagers)

							# Not willing to build units to get this off the ground
							if filledSlots >= numRequiredSlots:  # and landReservesUsed <= self.andReservesAvailable():
								self.requestPillageEnemyTowards(otherPlayer, simulation)

					elif warState == PlayerWarStateType.offensive or warState == PlayerWarStateType.nearlyWon:
						# If we are dominant, time to take down one of his cities
						self.requestBasicAttackTowards(otherPlayer, simulation=simulation)

		#
		# Naval operations(vs.opportunity targets)
		#
		unitsList = simulation.unitsOf(self.player)
		(numRequiredSlots, _, filledSlots) = UnitFormationHelper.numberOfFillableSlots(unitsList, UnitFormationType.navalSquadron)

		# Not willing to build units to get this off the ground
		if filledSlots >= numRequiredSlots:
			# Total number of these operations can't exceed (FLAVOR_NAVAL / 2)
			flavorNaval: int = self.player.valueOfPersonalityFlavor(FlavorType.naval)
			numSuperiority: int = self.player.numberOfOperationsOfType(UnitOperationType.navalSuperiority)
			numBombard: int = self.player.numberOfOperationsOfType(UnitOperationType.navalBombard)

			if (numSuperiority + numBombard) <= (flavorNaval / 2):
				if self.player.hasOperationsOfType(UnitOperationType.colonize):
					# If I have a colonization operation underway, start up naval superiority as extra escorts
					self.player.addOperation(UnitOperationType.navalSuperiority, None, None, None, None, simulation)
				elif self.adopted(MilitaryStrategyType.eradicateBarbarians):
					# If fighting off barbarians, start naval bombardment
					self.player.addOperation(UnitOperationType.navalBombard, None, None, None, None, simulation)
				elif numSuperiority > numBombard:
					# Otherwise choose based on which operation we have more of
					self.player.addOperation(UnitOperationType.navalBombard, None, None, None, None, simulation)
				else:
					self.player.addOperation(UnitOperationType.navalSuperiority, None, None, None, None, simulation)

		return

	def updateFlavors(self):
		self._flavors.reset()

		for militaryStrategyType in list(MilitaryStrategyType):
			if self.militaryStrategyAdoption.adopted(militaryStrategyType):
				for militaryStrategyTypeFlavor in militaryStrategyType.flavorModifiers():
					self._flavors += militaryStrategyTypeFlavor

	def mostThreatenedCity(self, simulation) -> Optional[City]:
		highestThreatValue = 0
		highestThreatenedCity: Optional[City] = None

		for city in simulation.citiesOf(self.player):
			threadValue = city.threatValue() * city.population()

			if city.isCapital():
				threadValue *= 125
				threadValue /= 100

			if threadValue > highestThreatValue:
				highestThreatValue = threadValue
				highestThreatenedCity = city

		return highestThreatenedCity

	def barbarianThreatTotal(self) -> int:
		"""How threatening are the barbarians?"""
		rtnValue = 0

		# Major threat for each camp seen
		rtnValue += self._barbarianDataValue.barbarianCampCount * 3  # AI_MILITARY_THREAT_WEIGHT_MAJOR

		# One minor threat for every X barbarians
		rtnValue += self._barbarianDataValue.visibleBarbarianCount / 2  # AI_MILITARY_BARBARIANS_FOR_MINOR_THREAT

		return rtnValue

	def numberOfPlayersAtWarWith(self, simulation) -> int:
		number = 0

		for otherPlayer in simulation.players:
			if self.player == otherPlayer:
				continue

			if not self.player.hasMetWith(otherPlayer):
				continue

			warState = self.player.diplomacyAI.warStateTowards(otherPlayer)
			if warState != PlayerWarStateType.none:
				number += 1

		return number

	def powerOfStrongestBuildableUnit(self, domain: UnitDomainType) -> int:
		"""How strong is the best unit we can train for this domain?"""
		rtnValue = 0
		for unitType in list(UnitType):
			if unitType.domain() == domain:
				thisPower = unitType.power()  # Test the power first, it is much less costly than testing canTrain
				if thisPower > rtnValue:
					if self.player.canTrain(unitType, continueFlag=False, testVisible=False, ignoreCost=True, ignoreUniqueUnitStatus=False):
						rtnValue = thisPower

		return rtnValue

	def buyEmergencyBuildingIn(self, city, simulation) -> bool:
		"""Spend money to quickly add a defensive building to a city"""
		# Loop through adding the available buildings
		for building in list(BuildingType):
			# Make sure this building can be built now
			if city.canBuildBuilding(building, simulation) and building.defense() > 0:
				if city.canPurchaseBuilding(building, YieldType.gold, simulation):
					goldCost = city.goldPurchaseCostOfBuilding(building, simulation)
					priority = 400  # AI_GOLD_PRIORITY_DEFENSIVE_BUILDING
					if self.player.economicAI.canWithdrawMoneyForPurchase(PurchaseType.building, goldCost, priority):
						self.player.treasury.changeGoldBy(-goldCost)
						result: bool = city.buildBuilding(building, simulation)
						logging.info(f'Emergency Building Purchase of {building} in {city.name()}')
						return result

		return False

	def buyEmergencyUnit(self, task: UnitTaskType, city, simulation):
		"""Spend money to quickly add a unit to a city"""
		# Get the best unit with this AI type
		unitType: UnitType = city.cityStrategyAI.unitProductionAI.recommendUnit(task, simulation)
		if unitType != UnitType.none:
			# Can we buy the primary unit type at the start city?
			if city.canPurchaseUnit(unitType, YieldType.gold, simulation):
				goldCost = city.goldPurchaseCostOfUnit(unitType, simulation)
				priority = 500  # AI_GOLD_PRIORITY_UNIT
				if self.player.economicAI.canWithdrawMoneyForPurchase(PurchaseType.unit, goldCost, priority):
					if city.player == self.player:  # Player must own the city or this will create a unit for another player
						# This is an EXTRA build for the operation beyond any that are already assigned to this city,
						# so pass in the right flag to CreateUnit()
						city.trainUnit(unitType, simulation)
						self.player.treasury.changeGoldBy(-goldCost)
						# fixme: pUnit->setMoves(0);
						logging.info(f'Emergency Building Purchase of {unitType} in {city.name()}')
						return

			# Try again with Faith
			if city.canPurchaseUnit(unitType, YieldType.faith, simulation):
				faithCost = city.faithPurchaseCostOfUnit(unitType, simulation)
				if city.player == self.player:  # Player must own the city or this will create a unit for another player
					city.trainUnit(unitType, simulation)
					self.player.changeFaith(-faithCost)
					# fixme: pUnit->setMoves(0);
					logging.info(f'Emergency Building Purchase of {unitType} in {city.name()}')
					return

		return

	def landDefenseState(self) -> DefenseState:
		return self._landDefenseState

	def navalDefenseState(self) -> DefenseState:
		return self._navalDefenseState

	def requestPillageEnemyTowards(self, otherPlayer, simulation) -> bool:
		"""Send an army to force concessions"""
		filledSlots, numRequiredSlots, landReservesUsed = MilitaryAIHelpers.numberOfFillableSlots(self.player, UnitFormationType.fastPillagers, requiresNavalMoves=False, simulation=simulation)

		if filledSlots >= numRequiredSlots and landReservesUsed <= self.landReservesAvailable():
			operation = self.player.addOperation(UnitOperationType.pillageEnemy, otherPlayer, None, None, None, simulation)
			if operation is not None:
				if not operation.shouldAbort(simulation):
					return True

		return False

	def cityStateAttackOperationAgainst(self, otherPlayer) -> Optional[Operation]:
		"""Get a pointer to the basic attack against a target"""
		allCityStateOperations = self.player.operationsOfType(UnitOperationType.cityStateAttack)
		cityStateOperationsAgainstPlayer = list(filter(lambda o: o.enemy == otherPlayer, allCityStateOperations))
		hasOperationUnderway: bool = len(cityStateOperationsAgainstPlayer) > 0

		if hasOperationUnderway:
			return firstOrNone(cityStateOperationsAgainstPlayer)
		else:
			allCityStateNavalOperations = self.player.operationsOfType(UnitOperationType.cityStateNavalAttack)
			cityStateNavalOperationsAgainstPlayer = list(filter(lambda o: o.enemy == otherPlayer, allCityStateNavalOperations))
			hasNavalOperationUnderway: bool = len(cityStateNavalOperationsAgainstPlayer) > 0

			if hasNavalOperationUnderway:
				return firstOrNone(cityStateNavalOperationsAgainstPlayer)

		return None

	def sneakAttackOperationAgainst(self, otherPlayer) -> Optional[Operation]:
		"""Get a pointer to the sneak attack operation against a target"""
		allSneackAttackOperations = self.player.operationsOfType(UnitOperationType.sneakCityAttack)
		sneackAttackOperationsAgainstPlayer = list(filter(lambda o: o.enemy == otherPlayer, allSneackAttackOperations))
		hasOperationUnderway: bool = len(sneackAttackOperationsAgainstPlayer) > 0

		if hasOperationUnderway:
			return firstOrNone(sneackAttackOperationsAgainstPlayer)

		allSneackAttackNavalOperations = self.player.operationsOfType(UnitOperationType.navalSneakAttack)
		sneackAttackNavalOperationsAgainstPlayer = list(filter(lambda o: o.enemy == otherPlayer, allSneackAttackNavalOperations))
		hasNavalOperationUnderway: bool = len(sneackAttackNavalOperationsAgainstPlayer) > 0

		if hasNavalOperationUnderway:
			return firstOrNone(sneackAttackNavalOperationsAgainstPlayer)

		return None

	def basicAttackOperationAgainst(self, otherPlayer) -> Optional[Operation]:
		"""Get a pointer to the basic attack against a target"""
		allBasicCityAttackOperations = self.player.operationsOfType(UnitOperationType.basicCityAttack)
		basicCityAttackOperationsAgainstPlayer = list(filter(lambda o: o.enemy == otherPlayer, allBasicCityAttackOperations))
		hasOperationUnderway: bool = len(basicCityAttackOperationsAgainstPlayer) > 0

		if hasOperationUnderway:
			return firstOrNone(basicCityAttackOperationsAgainstPlayer)

		allNavalAttackOperations = self.player.operationsOfType(UnitOperationType.navalAttack)
		navalAttackOperationsAgainstPlayer = list(filter(lambda o: o.enemy == otherPlayer, allNavalAttackOperations))
		hasOperationUnderway: bool = len(navalAttackOperationsAgainstPlayer) > 0

		if hasOperationUnderway:
			return firstOrNone(navalAttackOperationsAgainstPlayer)

		return None

	def showOfForceOperationAgainst(self, otherPlayer) -> Optional[Operation]:
		"""Get a pointer to the show of force operation against a target"""
		allSmallCityAttackOperations = self.player.operationsOfType(UnitOperationType.smallCityAttack)
		smallCityAttackOperationsAgainstPlayer = list(filter(lambda o: o.enemy == otherPlayer, allSmallCityAttackOperations))
		return firstOrNone(smallCityAttackOperationsAgainstPlayer)

	def pureNavalAttackOperationAgainst(self, otherPlayer) -> Optional[Operation]:
		"""Get a pointer to the pure naval operation against a target"""
		allPureNavalCityOperations = self.player.operationsOfType(UnitOperationType.pureNavalCityAttack)
		pureNavalCityAttackOperationsAgainstPlayer = list(filter(lambda o: o.enemy == otherPlayer, allPureNavalCityOperations))
		return firstOrNone(pureNavalCityAttackOperationsAgainstPlayer)

	def landReservesAvailable(self) -> int:
		return self.baseData.numLandUnits - self.baseData.numLandUnitsInArmies - self.baseData.mandatoryReserveSize

	def unitTypeForArmyIn(self, city, simulation) -> Optional[UnitType]:
		"""Which unit should be built next for our army"""
		if self._armyTypeBeingBuilt == ArmyType.none:
			return None

		# Look for required units first
		if self._armyTypeBeingBuilt == ArmyType.navalInvasion:
			formation = UnitFormationType.navalInvasion  # MUFORMATION_NAVAL_INVASION
		elif simulation.handicap > HandicapType.king:
			formation = UnitFormationType.biggerCityAttackForce  # MUFORMATION_BIGGER_CITY_ATTACK_FORCE
		else:
			formation = UnitFormationType.basicCityAttackForce  # MUFORMATION_BASIC_CITY_ATTACK_FORCE

		unitTask: UnitTaskType = MilitaryAIHelpers.firstSlotCityCanFill(
			self.player,
			formation,
			self._armyTypeBeingBuilt == ArmyType.navalInvasion,
			simulation.isCoastalAt(city.location),
			secondaryUnit=False,
			simulation=simulation
		)
		unitType: UnitType = city.cityStrategyAI.unitProductionAI.recommendUnit(unitTask, simulation)

		if unitType == UnitType.none:
			unitTask: UnitTaskType = MilitaryAIHelpers.firstSlotCityCanFill(
				self.player,
				formation,
				self._armyTypeBeingBuilt == ArmyType.navalInvasion,
				simulation.isCoastalAt(city.location),
				secondaryUnit=True,  # <=
				simulation=simulation
			)
			unitType = city.cityStrategyAI.unitProductionAI.recommendUnit(unitTask, simulation)

		return unitType

	def requestCityStateAttackAgainst(self, enemyPlayer, simulation) -> bool:
		"""Request for an attack on a city state"""
		target, _ = self.findBestAttackTarget(UnitOperationType.cityStateAttack, enemyPlayer, simulation)
		if target is not None and target.targetCity is not None:
			if target.attackBySea:
				if self.isAttackReady(UnitFormationType.cityStateInvasion, UnitOperationType.cityStateNavalAttack, simulation):
					operation = self.player.addOperation(
						UnitOperationType.cityStateNavalAttack,
						enemyPlayer,
						target.targetCity,
						simulation.areaOf(target.targetCity.location),
						target.musterCity,
						simulation
					)
					if operation is not None and not operation.shouldAbort(simulation):
						return True
				else:
					self._numberOfNavalAttacksRequested += 1
					self._armyTypeBeingBuilt: ArmyType = ArmyType.land if (self._numberOfLandAttacksRequested > self._numberOfNavalAttacksRequested) else ArmyType.navalInvasion
			else:
				if self.isAttackReady(UnitFormationType.cityStateAttackForce, UnitOperationType.cityStateAttack, simulation):
					operation = self.player.addOperation(
						UnitOperationType.cityStateAttack,
						enemyPlayer,
						target.targetCity,
						simulation.areaOf(target.targetCity.location),
						target.musterCity,
						simulation
					)
					if operation is not None and not operation.shouldAbort(simulation):
						return True
				else:
					self._numberOfLandAttacksRequested += 1
					self._armyTypeBeingBuilt: ArmyType = ArmyType.land if (self._numberOfLandAttacksRequested > self._numberOfNavalAttacksRequested) else ArmyType.navalInvasion

			return True

		return False

	def requestSneakAttackAgainst(self, enemyPlayer, simulation) -> bool:
		"""Requests for sneak attack on a city of a player we're not at war with. Returns true if operation started."""
		# Let's only allow us to be sneak attacking one opponent at a time, so abort
		# if already have one of these operations active against any opponent
		if self.player.numberOfOperationsOfType(UnitOperationType.navalSneakAttack) > 0:
			return False

		if self.player.numberOfOperationsOfType(UnitOperationType.sneakCityAttack) > 0:
			return False

		target, _ = self.findBestAttackTarget(UnitOperationType.sneakCityAttack, enemyPlayer, simulation)
		if target is not None and target.targetCity is not None:
			if target.attackBySea:
				if self.isAttackReady(UnitFormationType.navalInvasion, UnitOperationType.navalSneakAttack, simulation):
					operation = self.player.addOperation(
						UnitOperationType.navalSneakAttack,
						enemyPlayer,
						target.targetCity,
						simulation.areaOf(target.targetCity.location),
						target.musterCity,
						simulation
					)
					if operation is not None and not operation.shouldAbort(simulation):
						return True
				else:
					self._numberOfNavalAttacksRequested += 1
					self._armyTypeBeingBuilt: ArmyType = ArmyType.land if (self._numberOfLandAttacksRequested > self._numberOfNavalAttacksRequested) else ArmyType.navalInvasion
			else:
				formation: UnitFormationType = UnitFormationType.biggerCityAttackForce if simulation.handicap > HandicapType.king else UnitFormationType.basicCityAttackForce
				if self.isAttackReady(formation, UnitOperationType.sneakCityAttack, simulation):
					operation = self.player.addOperation(
						UnitOperationType.sneakCityAttack,
						enemyPlayer,
						target.targetCity,
						simulation.areaOf(target.targetCity.location),
						target.musterCity,
						simulation
					)
					if operation is not None and not operation.shouldAbort(simulation):
						return True
				else:
					self._numberOfLandAttacksRequested += 1
					self._armyTypeBeingBuilt: ArmyType = ArmyType.land if (self._numberOfLandAttacksRequested > self._numberOfNavalAttacksRequested) else ArmyType.navalInvasion

		return False

	def findBestAttackTarget(self, operationType: UnitOperationType, enemyPlayer, simulation) -> (Optional[MilitaryTarget], int):
		"""Best target by land OR sea"""
		prelimWeightedTargetList = WeightedBaseList()
		# Estimate the relative strength of units near our cities and near their cities (can't use TacticalAnalysisMap
		# because we may not be at war - and that it isn't current if we are calling this from the DiploAI)
		for friendlyCity in simulation.citiesOf(self.player):
			generalInTheVicinity: bool = False
			power: int = 0
			for loopUnit in simulation.unitsOf(self.player):
				if loopUnit.isCombatUnit():
					distance = loopUnit.location.distance(friendlyCity.location)
					if distance <= 5:
						power += loopUnit.power()

				if not generalInTheVicinity and loopUnit.isGreatGeneral():
					distance = loopUnit.location.distance(friendlyCity.location)
					if distance <= 5:
						generalInTheVicinity = True

			if generalInTheVicinity:
				power *= 11
				power /= 10

			friendlyCity.updateScratchIntValue(power)

		for enemyCity in simulation.citiesOf(enemyPlayer):
			if not simulation.tileAt(enemyCity.location).isDiscoveredBy(self.player):
				continue

			generalInTheVicinity: bool = False
			power: int = 0
			for loopUnit in simulation.unitsOf(enemyPlayer):
				if loopUnit.isCombatUnit():
					distance = loopUnit.location.distance(enemyCity.location)
					if distance <= 5:
						power += loopUnit.power()

				if not generalInTheVicinity and loopUnit.isGreatGeneral():
					distance = loopUnit.location.distance(enemyCity.location)
					if distance <= 5:
						generalInTheVicinity = True

			if generalInTheVicinity:
				power *= 11
				power /= 10

			enemyCity.updateScratchIntValue(power)

		# Build a list of all the possible start city/target city pairs
		# static CvWeightedVector<CvMilitaryTarget, SAFE_ESTIMATE_NUM_CITIES* 10, true> prelimWeightedTargetList;
		# prelimWeightedTargetList.clear();
		for friendlyCity in simulation.citiesOf(self.player):
			for enemyCity in simulation.citiesOf(enemyPlayer):
				if not simulation.tileAt(enemyCity.location).isDiscoveredBy(self.player):
					continue

				target = MilitaryTarget()
				target.musterCity = friendlyCity
				target.targetCity = enemyCity
				target.musterNearbyUnitPower = friendlyCity.scratchIntValue()
				target.targetNearbyUnitPower = enemyCity.scratchIntValue()

				if operationType == UnitOperationType.pureNavalCityAttack:
					target.attackBySea = True

					if simulation.isCoastalAt(friendlyCity.location) and simulation.isCoastalAt(enemyCity.location):
						target.pathLength = friendlyCity.location.distance(enemyCity.location)
				else:
					self.shouldAttackBySea(enemyPlayer, target, simulation)

					if not simulation.isCoastalAt(friendlyCity.location) and target.attackBySea:
						continue

				if target.pathLength > 0:
					# Start by using the path length as the weight, shorter paths have higher weight
					weight = (10000 - target.pathLength)
					prelimWeightedTargetList.setWeight(weight, target)

		# Let's score the 25 shortest paths ... anything more than that means there are too many interior
		# cities from one (or both) sides being considered
		prelimWeightedTargetList.sortByValue(reverse=True)
		weightedTargetList = WeightedBaseList()
		targetsConsidered: int = 0
		for target, weight in prelimWeightedTargetList.items():
			if targetsConsidered > 25:
				continue

			# If a sea target, we haven't checked the path yet.  Do that now
			if target.attackBySea:
				if not simulation.isCoastalAt(target.musterCity.location):
					continue

				if not simulation.isCoastalAt(target.targetCity.location):
					continue

				seaPlotNearMuster: HexPoint = self.coastalPlotAdjacentToTarget(target.musterCity.location, None, simulation)
				seaPlotNearTarget: HexPoint = self.coastalPlotAdjacentToTarget(target.targetCity.location, None, simulation)

				# Now check path
				pathFinderDataSource = simulation.ignoreUnitsPathfinderDataSource(
					UnitMovementType.swim,
					self.player,
					canEmbark=True,
					canEnterOcean=False
				)
				pathFinder = AStarPathfinder(pathFinderDataSource)

				if not pathFinder.doesPathExist(seaPlotNearMuster, seaPlotNearTarget):
					continue

			weight = self.scoreTarget(target, operationType, simulation)
			weightedTargetList.setWeight(weight, target)
			targetsConsidered += 1

		# Didn't find anything, abort
		if len(weightedTargetList.items()) == 0:
			# Call off the attack
			return None, -1

		weightedTargetList.sortByValue(reverse=True)
		# LogAttackTargets(eAIOperationType, eEnemy, weightedTargetList);

		if weightedTargetList.totalWeights() <= 0:
			# Call off the attack
			return None, -1

		chosenTarget = weightedTargetList.chooseFromTopChoices()
		winningScore = self.scoreTarget(chosenTarget, operationType, simulation)
		# LogChosenTarget(eAIOperationType, eEnemy, chosenTarget);
		return chosenTarget, winningScore

	def isAttackReady(self, formation: UnitFormationType, operationType: UnitOperationType, simulation) -> bool:
		"""Do we have the forces at hand for an attack?"""
		# Do we already have an operation of this type that is building units?
		operationsOfType: [Operation] = self.player.operationsOfType(operationType)
		hasOperationUnderway = len(operationsOfType) > 0
		if hasOperationUnderway:
			firstOperation: Optional[Operation] = firstOrNone(operationsOfType)
			if firstOperation.state != OperationStateType.recruitingUnits:
				return False

		requiresNavalMoves: bool = False
		if formation == UnitFormationType.navalInvasion or formation == UnitFormationType.navalSquadron or \
			formation == UnitFormationType.cityStateInvasion or formation == UnitFormationType.pureNavalCityAttack:
			requiresNavalMoves = True

		filledSlots, numberSlotsRequired, _ = MilitaryAIHelpers.numberOfFillableSlots(self.player, formation, requiresNavalMoves, simulation)
		if filledSlots >= numberSlotsRequired:
			return True

		return False

	def shouldAttackBySea(self, enemyPlayer, target: MilitaryTarget, simulation):
		"""Is it better to attack this target by sea?"""
		pathLength: int = 0
		plotDistance = target.musterCity.location.distance(target.targetCity.location)

		# Can embark
		if self.player.canEmbark():
			# On different landmasses?
			musterArea = simulation.areaOf(target.musterCity.location)
			targetArea = simulation.areaOf(target.targetCity.location)
			if musterArea is not None and targetArea is not None and musterArea != targetArea:
				target.attackBySea = True
				target.pathLength = plotDistance
				return

			# No step path between muster point and target?
			pathFinderDataSource = simulation.ignoreUnitsPathfinderDataSource(
				UnitMovementType.swim,
				self.player,
				canEmbark=True,
				canEnterOcean=False
			)
			pathFinder = AStarPathfinder(pathFinderDataSource)

			if not pathFinder.doesPathExist(target.musterCity.location, target.targetCity.location):
				target.attackBySea = True
				target.pathLength = plotDistance
				return

			# Land path is over twice as long as direct path
			pathFinderDataSource = simulation.ignoreUnitsPathfinderDataSource(
				UnitMovementType.walk,
				self.player,
				canEmbark=True,
				canEnterOcean=False
			)
			pathFinder = AStarPathfinder(pathFinderDataSource)
			path = pathFinder.shortestPath(target.musterCity.location, target.targetCity.location)

			if path is not None and len(path.points()) > 2 * plotDistance:
				target.attackBySea = True
				target.pathLength = plotDistance
				return
		else:  # Can't embark yet
			pathFinderDataSource = simulation.ignoreUnitsPathfinderDataSource(
				UnitMovementType.walk,
				self.player,
				canEmbark=True,
				canEnterOcean=False
			)
			pathFinder = AStarPathfinder(pathFinderDataSource)
			path = pathFinder.shortestPath(target.musterCity.location, target.targetCity.location)

			if path is None:
				target.pathLength = -1  # Call off attack, no path
				return
			else:
				target.pathLength = len(path.points())
				return

		target.attackBySea = False
		target.pathLength = pathLength
		return

	def scoreTarget(self, target: MilitaryTarget, operationType: UnitOperationType, simulation) -> int:
		"""Come up with a target priority looking at distance, strength, approaches (high score = more desirable target)"""
		rtnValue = 1  # Start with a high base number since divide into it later
		# Take into account distance to target (and use higher multipliers for land paths)
		if not target.attackBySea:
			if target.pathLength < 10:
				rtnValue *= 16
			elif target.pathLength < 15:
				rtnValue *= 8
			elif target.pathLength < 20:
				rtnValue *= 4
			else:
				rtnValue *= 2

			# Double if we can assemble troops in muster city with airlifts
			if target.musterCity.canAirlift():
				rtnValue *= 2
		else:
			if target.pathLength < 12:
				rtnValue *= 5
			elif target.pathLength < 20:
				rtnValue *= 3
			elif target.pathLength < 30:
				rtnValue *= 2

			# If coming over sea, inland cities are trickier
			if not simulation.isCoastalAt(target.targetCity.location):
				rtnValue /= 2

		# Is this a sneak attack? If so distance is REALLY important (want to target spaces on edge of empire)
		# So let's cube what we have so far
		if operationType == UnitOperationType.sneakCityAttack or operationType == UnitOperationType.navalSneakAttack:
			rtnValue = rtnValue * rtnValue * rtnValue

		approachMultiplier: int = 0
		attackApproach = self.evaluateMilitaryApproaches(target.targetCity, True, target.attackBySea, simulation)  # Assume units coming by sea can disembark
		if attackApproach == AttackApproachType.unrestricted:  # ATTACK_APPROACH_UNRESTRICTED
			approachMultiplier = 10
		elif attackApproach == AttackApproachType.open:  # ATTACK_APPROACH_OPEN
			approachMultiplier = 8
		elif attackApproach == AttackApproachType.neutral:  # ATTACK_APPROACH_NEUTRAL
			approachMultiplier = 4
		elif attackApproach == AttackApproachType.limited:  # ATTACK_APPROACH_LIMITED
			approachMultiplier = 2
		elif attackApproach == AttackApproachType.restricted:  # ATTACK_APPROACH_RESTRICTED
			approachMultiplier = 1
		elif attackApproach == AttackApproachType.none:  # ATTACK_APPROACH_NONE
			approachMultiplier = 0

		rtnValue *= approachMultiplier

		# should probably give a bonus if these cities are adjacent

		# Don't want to start at a city that isn't connected to our capital
		if not target.musterCity.isRouteToCapitalConnected() and not target.musterCity.isCapital():
			rtnValue /= 4

		# this won't work if we are "just checking" as the zone are only built for actual war war opponents
		# TODO come up with a better way to do this that is always correct

		friendlyStrength = target.musterNearbyUnitPower
		enemyStrength = target.targetNearbyUnitPower + (target.targetCity.strengthValue() / 50)
		friendlyStrength = max(1, friendlyStrength)
		enemyStrength = max(1, enemyStrength)
		ratio = int((friendlyStrength * 100) / enemyStrength)
		ratio = min(1000, ratio)
		rtnValue *= ratio

		if target.targetCity.isOriginalCapital():
			rtnValue *= 250  # AI_MILITARY_CAPTURING_ORIGINAL_CAPITAL
			rtnValue /= 100

		if target.targetCity.originalLeader() == self.player.leader and \
			target.targetCity.originalCityState == self.player.cityState:
			rtnValue *= 150  # AI_MILITARY_RECAPTURING_OWN_CITY
			rtnValue /= 100

		# Don't want it to already be targeted by an operation that's not well on its way
		if self.player.isCityAlreadyTargeted(target.targetCity, UnitDomainType.none, 50, simulation):
			rtnValue /= 10

		rtnValue /= 1000

		# Economic value of target unsigned long
		economicValue = 1 + (target.targetCity.population() / 3)
		# TODO: un-hardcode this
		# filter out all but the most productive
		economicValue += target.targetCity.foodPerTurn(simulation) / 10
		economicValue += target.targetCity.productionPerTurn(simulation) / 10
		economicValue += target.targetCity.sciencePerTurn(simulation) / 10
		economicValue += target.targetCity.goldPerTurn(simulation) / 10
		economicValue += target.targetCity.culturePerTurn(simulation) / 10
		economicValue += target.targetCity.faithPerTurn(simulation) / 10
		rtnValue *= economicValue

		rtnValue /= 10

		return min(10000000, rtnValue)

	def evaluateMilitaryApproaches(self, targetCity, attackByLand: bool, attackBySea: bool, simulation) -> AttackApproachType:
		"""How open an approach do we have to this city if we want to attack it?"""
		numBlocked = 0

		# Look at each of the six plots around the city
		for loopPoint in targetCity.location.neighbors():
			loopPlot = simulation.tileAt(loopPoint)

			# Blocked if edge of map
			if loopPlot is None:
				numBlocked += 1
			else:
				# For now, assume no one coming in over a lake
				if loopPlot.feature() == FeatureType.lake:
					numBlocked += 1
				# Coast but attack is not by sea?
				elif loopPlot.isWater() and not attackBySea:
					numBlocked += 1
				# Land
				elif not loopPlot.isWater():
					if not attackByLand:
						numBlocked += 1
					else:
						if loopPlot.isImpassable(UnitMovementType.walk) or loopPlot.feature() == FeatureType.mountains:
							numBlocked += 1

		if numBlocked == 0:
			return AttackApproachType.unrestricted  # ATTACK_APPROACH_UNRESTRICTED
		elif numBlocked == 1 or numBlocked == 2:
			return AttackApproachType.open  # ATTACK_APPROACH_OPEN
		elif numBlocked == 3:
			return AttackApproachType.neutral  # ATTACK_APPROACH_NEUTRAL
		elif numBlocked == 4:
			return AttackApproachType.limited  # ATTACK_APPROACH_LIMITED;
		elif numBlocked == 5:
			return AttackApproachType.restricted  # ATTACK_APPROACH_RESTRICTED;
		elif numBlocked == 6:
			return AttackApproachType.none  # ATTACK_APPROACH_NONE;

		return AttackApproachType.unrestricted

	def coastalPlotAdjacentToTarget(self, location: HexPoint, army, simulation) -> Optional[HexPoint]:
		initialUnit = None
		bestDistance: int = sys.maxsize
		coastalPoint = None

		if army is not None:
			initialUnit = firstOrNone(army.units())

		# Find a coastal water tile adjacent to enemy city
		for neighbor in location.neighbors():
			adjacentPlot = simulation.tileAt(neighbor)

			if adjacentPlot is None:
				continue

			if adjacentPlot.terrain() == TerrainType.shore:
				# Check for path if we have a unit, otherwise don't worry about it
				if initialUnit is not None:
					if initialUnit.turnsToReach(adjacentPlot, simulation) < sys.maxsize:
						distance = initialUnit.location.distance(neighbor)
						if distance < bestDistance:
							bestDistance = distance
							coastalPoint = neighbor
				else:
					return neighbor

		return coastalPoint

	def requestBasicAttackTowards(self, otherPlayer, numberOfUnitsWillingBuild: int = 1, simulation=None) -> bool:
		"""Send an army to take a city"""
		if simulation is None:
			raise Exception('simulation not provided')

		(target, winningScore) = self.findBestAttackTarget(UnitOperationType.basicCityAttack, otherPlayer, simulation)
		return self.requestSpecificAttackAgainst(target, numberOfUnitsWillingBuild, simulation)

	def requestSpecificAttackAgainst(self, target: MilitaryTarget, numberOfUnitsWillingBuild: int, simulation) -> bool:
		operation: Optional[Operation] = None
		numRequiredSlots: int = 0
		landReservesUsed: int = 0
		filledSlots: int = 0

		if target.targetCity is not None:
			if target.attackBySea:
				filledSlots, numberSlotsRequired, _ = MilitaryAIHelpers.numberOfFillableSlots(self.player, UnitFormationType.navalInvasion, True, simulation)
				if (numRequiredSlots - filledSlots) <= numberOfUnitsWillingBuild and landReservesUsed <= self.landReservesAvailable():
					operation = self.player.addOperation(UnitOperationType.navalAttack, target.targetCity.player, target.targetCity, simulation.areaOf(target.targetCity.location), None, simulation=simulation)
			else:
				formation: UnitFormationType = UnitFormationType.biggerCityAttackForce if simulation.handicap > HandicapType.prince else UnitFormationType.basicCityAttackForce
				filledSlots, numberSlotsRequired, _ = MilitaryAIHelpers.numberOfFillableSlots(self.player, formation, False, simulation)

				if (numRequiredSlots - filledSlots) <= numberOfUnitsWillingBuild and landReservesUsed <= self.landReservesAvailable():
					operation = self.player.addOperation(UnitOperationType.basicCityAttack, target.targetCity.player, target.targetCity, simulation.areaOf(target.targetCity.location), target.musterCity, simulation=simulation)

					if operation is not None:
						if not operation.shouldAbort(simulation) and target.targetCity.isCoastal(simulation):
							flavorNaval = self.player.valueOfStrategyAndPersonalityFlavor(FlavorType.naval)
							numSuperiority = self.player.numberOfOperationsOf(UnitOperationType.navalSuperiority)
							numBombard = self.player.numberOfOperationsOf(UnitOperationType.navalBombard)
							maxOperations = flavorNaval / 2
							# major naval map = > maxOperations *= 2

							if numSuperiority + numBombard <= maxOperations:
								self.player.addOperation(UnitOperationType.navalSuperiority, None, None, None, None, simulation)

			if operation is not None:
				if not operation.shouldAbort(simulation):
					return True

		return False

	def requestShowOfForce(self, otherPlayer, simulation) -> bool:
		"""Send an army to force concessions"""
		target = self.findBestAttackTarget(UnitOperationType.sneakCityAttack, otherPlayer, simulation)
		if target.targetCity is not None:
			if target.attackBySea:
				operation = self.player.addOperation(
					UnitOperationType.navalSneakAttack,
					otherPlayer,
					target.targetCity,
					simulation.areaOf(target.targetCity.location),
					target.musterCity,
					simulation
				)
				if operation is not None and not operation.shouldAbort():
					return True
			else:
				operation = self.player.addOperation(
					UnitOperationType.smallCityAttack,
					otherPlayer,
					target.targetCity,
					simulation.areaOf(target.targetCity.location),
					target.musterCity,
					simulation
				)
				if operation is not None and not operation.shouldAbort():
					return True

		return False
	