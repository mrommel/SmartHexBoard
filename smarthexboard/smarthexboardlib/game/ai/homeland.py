import logging
import random
import sys
from typing import Optional

from smarthexboard.smarthexboardlib.game.ai.builderTasking import BuilderDirectiveType, BuilderDirective
from smarthexboard.smarthexboardlib.game.ai.militaryStrategies import ReconStateType
from smarthexboard.smarthexboardlib.game.ai.militaryStrategies import ReconStateType
from smarthexboard.smarthexboardlib.game.cities import City
from smarthexboard.smarthexboardlib.game.flavors import FlavorType
from smarthexboard.smarthexboardlib.game.states.builds import BuildType
from smarthexboard.smarthexboardlib.game.tradeRoutes import TradeRoute
from smarthexboard.smarthexboardlib.game.unitTypes import UnitTaskType, UnitMapType, UnitMissionType
from smarthexboard.smarthexboardlib.game.units import Unit, UnitAutomationType, UnitMission
from smarthexboard.smarthexboardlib.map import constants
from smarthexboard.smarthexboardlib.map.base import HexPoint
from smarthexboard.smarthexboardlib.map.improvements import ImprovementType
from smarthexboard.smarthexboardlib.map.path_finding.finder import AStarPathfinder
from smarthexboard.smarthexboardlib.map.types import UnitDomainType, UnitMovementType, Yields
from smarthexboard.smarthexboardlib.core.base import ExtendedEnum, InvalidEnumError, contains
from smarthexboard.smarthexboardlib.utils.base import firstOrNone


class HomelandMoveTypeData:
	def __init__(self, name: str, priority: int):
		self.name = name
		self.priority = priority


class HomelandMoveType(ExtendedEnum):
	none = 'none'  # AI_HOMELAND_MOVE_NONE = -1,
	unassigned = 'unassigned'  # AI_HOMELAND_MOVE_UNASSIGNED,
	explore = 'explore'  # AI_HOMELAND_MOVE_EXPLORE,
	exploreSea = 'exploreSea'  # AI_HOMELAND_MOVE_EXPLORE_SEA,
	settle = 'settle'  # AI_HOMELAND_MOVE_SETTLE,
	garrison = 'garrison'  # AI_HOMELAND_MOVE_GARRISON,
	heal = 'heal'  # AI_HOMELAND_MOVE_HEAL,
	toSafety = 'toSafety'  # AI_HOMELAND_MOVE_TO_SAFETY,
	mobileReserve = 'mobileReserve'  # AI_HOMELAND_MOVE_MOBILE_RESERVE,
	sentry = 'sentry'  # AI_HOMELAND_MOVE_SENTRY,
	worker = 'worker'  # AI_HOMELAND_MOVE_WORKER,
	workerSea = 'workerSea'  # AI_HOMELAND_MOVE_WORKER_SEA,
	patrol = 'patrol'  # AI_HOMELAND_MOVE_PATROL,
	upgrade = 'upgrade'  # AI_HOMELAND_MOVE_UPGRADE,
	ancientRuins = 'ancientRuins'  # AI_HOMELAND_MOVE_ANCIENT_RUINS,
	# garrisonCityState = ''  # AI_HOMELAND_MOVE_GARRISON_CITY_STATE,
	# writer = ''  # AI_HOMELAND_MOVE_WRITER,
	# artistGoldenAge = ''  # AI_HOMELAND_MOVE_ARTIST_GOLDEN_AGE,
	# musician = ''  # AI_HOMELAND_MOVE_MUSICIAN,
	# scientistFreeTech = ''  # AI_HOMELAND_MOVE_SCIENTIST_FREE_TECH,
	# none = ''  # AI_HOMELAND_MOVE_MERCHANT_TRADE,
	# none = ''  # AI_HOMELAND_MOVE_ENGINEER_HURRY,
	# none = ''  # AI_HOMELAND_MOVE_GENERAL_GARRISON,
	# none = ''  # AI_HOMELAND_MOVE_ADMIRAL_GARRISON,
	# none = ''  # AI_HOMELAND_MOVE_SPACESHIP_PART,
	aircraftToTheFront = 'aircraftToTheFront'  # AI_HOMELAND_MOVE_AIRCRAFT_TO_THE_FRONT,
	# none = ''  # AI_HOMELAND_MOVE_PROPHET_RELIGION,
	# missionary = ''  # AI_HOMELAND_MOVE_MISSIONARY,
	# inquisitor = ''  # AI_HOMELAND_MOVE_INQUISITOR,
	tradeUnit = 'tradeUnit'  # AI_HOMELAND_MOVE_TRADE_UNIT,

	# archaeologist = ''  # AI_HOMELAND_MOVE_ARCHAEOLOGIST,
	# addSpaceshipPart = ''  # AI_HOMELAND_MOVE_ADD_SPACESHIP_PART,
	# airlift = ''  # AI_HOMELAND_MOVE_AIRLIFT

	def title(self) -> str:
		return self._data().name

	def priority(self) -> int:
		return self._data().priority

	def _data(self) -> HomelandMoveTypeData:
		if self == HomelandMoveType.none:
			return HomelandMoveTypeData(name="none", priority=0)
		elif self == HomelandMoveType.unassigned:
			return HomelandMoveTypeData(name="unassigned", priority=0)

		elif self == HomelandMoveType.explore:
			return HomelandMoveTypeData(name="explore", priority=35)
		elif self == HomelandMoveType.exploreSea:
			return HomelandMoveTypeData(name="exploreSea", priority=35)
		elif self == HomelandMoveType.settle:
			return HomelandMoveTypeData(name="settle", priority=50)
		elif self == HomelandMoveType.garrison:
			return HomelandMoveTypeData(name="garrison", priority=10)
		elif self == HomelandMoveType.heal:
			return HomelandMoveTypeData(name="heal", priority=30)
		elif self == HomelandMoveType.toSafety:
			return HomelandMoveTypeData(name="toSafety", priority=30)
		elif self == HomelandMoveType.mobileReserve:
			return HomelandMoveTypeData(name="mobileReserve", priority=15)
		elif self == HomelandMoveType.sentry:
			return HomelandMoveTypeData(name="sentry", priority=20)
		elif self == HomelandMoveType.worker:
			return HomelandMoveTypeData(name="worker", priority=30)
		elif self == HomelandMoveType.workerSea:
			return HomelandMoveTypeData(name="workerSea", priority=30)
		elif self == HomelandMoveType.patrol:
			return HomelandMoveTypeData(name="patrol", priority=0)
		elif self == HomelandMoveType.upgrade:
			return HomelandMoveTypeData(name="upgrade", priority=25)
		elif self == HomelandMoveType.ancientRuins:
			return HomelandMoveTypeData(name="ancientRuins", priority=40)
		elif self == HomelandMoveType.aircraftToTheFront:
			return HomelandMoveTypeData(name="aircraftToTheFront", priority=50)

		elif self == HomelandMoveType.tradeUnit:
			return HomelandMoveTypeData(name="tradeUnit", priority=100)

		raise InvalidEnumError(self)


class HomelandMove:
	"""Object stored in the list of move priorities (movePriorityList)"""

	def __init__(self, moveType: HomelandMoveType, priority: int = 0):
		self.moveType = moveType
		self.priority = priority

	def __lt__(self, other):
		if isinstance(other, HomelandMove):
			return self.priority > other.priority

		raise Exception('wrong type: HomelandMove expected')

	def __eq__(self, other) -> bool:
		if isinstance(other, HomelandMove):
			return self.moveType == other.moveType and self.priority == other.priority

		raise Exception('wrong type: HomelandMove expected')

	def __repr__(self):
		return f'HomelandMove(moveType={self.moveType}, priority={self.priority})'


class HomelandUnit:
	"""Object stored in the list of current move units (m_CurrentMoveUnits)"""

	def __init__(self, unit):
		self.unit = unit
		self.movesToTarget: int = 0
		self.target: Optional[HexPoint] = None

	def __lt__(self, other):
		if isinstance(other, HomelandUnit):
			return self.movesToTarget < other.movesToTarget

		raise Exception('wrong type: HomelandUnit expected')

	def __eq__(self, other) -> bool:
		if isinstance(other, HomelandUnit):
			return self.movesToTarget == other.movesToTarget

		raise Exception(f'wrong type: HomelandUnit expected but got {type(other)}')

	def copy(self):
		c = HomelandUnit(self.unit)
		c.movesToTarget = self.movesToTarget
		c.target = self.target
		return c


class HomelandTargetType(ExtendedEnum):
	city = 'city'  # AI_HOMELAND_TARGET_CITY
	sentryPoint = 'sentryPoint'  # AI_HOMELAND_TARGET_SENTRY_POINT
	fort = 'fort'  # AI_HOMELAND_TARGET_FORT
	navalResource = 'navalResource'  # AI_HOMELAND_TARGET_NAVAL_RESOURCE
	homeRoad = 'homeRoad'  # AI_HOMELAND_TARGET_HOME_ROAD
	ancientRuin = 'ancientRuin'  # AI_HOMELAND_TARGET_ANCIENT_RUIN


class HomelandTarget:
	"""
	A target of opportunity for the Homeland AI this turn

	Key Attributes:
	- Arises during processing of CvHomelandAI::FindHomelandTargets()
	- Targets are reexamined each turn (so shouldn't need to be serialized)
	"""

	def __init__(self, targetType: HomelandTargetType):
		self.targetType = targetType
		self.target: Optional[HexPoint] = None
		self.city: Optional[City] = None
		self.threatValue: int = 0
		self.improvement: ImprovementType = ImprovementType.none
		self.auxData = None
		self.auxIntData = None

	def copy(self):
		t = HomelandTarget(self.targetType)
		t.target = self.target
		t.city = self.city
		t.threatValue = self.threatValue
		t.improvement = self.improvement
		t.auxData = self.auxData
		t.auxIntData = self.auxIntData
		return t

	def __lt__(self, other):
		if isinstance(other, HomelandTarget):
			return self.threatValue < other.threatValue

		raise Exception('wrong type: HomelandTarget expected')

	def __eq__(self, other) -> bool:
		if isinstance(other, HomelandTarget):
			return self.threatValue == other.threatValue

		raise Exception('wrong type: HomelandTarget expected')


class HomelandAI:
	flavorDampening = 0.3  # AI_TACTICAL_FLAVOR_DAMPENING_FOR_MOVE_PRIORITIZATION
	defensiveMoveTurns = 4  # AI_HOMELAND_MAX_DEFENSIVE_MOVE_TURNS
	maxDangerLevel = 100000.0  # MAX_DANGER_VALUE

	def __init__(self, player):
		self.player = player
		self.currentTurnUnits: [Unit] = []
		self.currentMoveUnits: [HomelandUnit] = []
		self.currentMoveHighPriorityUnits: [HomelandUnit] = []

		self.movePriorityList: [HomelandMove] = []
		self.movePriorityTurn: int = 0

		self.currentBestMoveUnit: Optional[Unit] = None
		self.currentBestMoveUnitTurns: int = sys.maxsize
		self.currentBestMoveHighPriorityUnit: Optional[Unit] = None
		self.currentBestMoveHighPriorityUnitTurns: int = sys.maxsize

		self.targetedCities: [HomelandTarget] = []
		self.targetedSentryPoints: [HomelandTarget] = []
		self.targetedForts: [HomelandTarget] = []
		self.targetedNavalResources: [HomelandTarget] = []
		self.targetedHomelandRoads: [HomelandTarget] = []
		self.targetedAncientRuins: [HomelandTarget] = []

	def doTurn(self, simulation):
		"""Update the AI for units"""
		# no homeland for barbarians
		if self.player.isBarbarian():
			for loopUnit in simulation.unitsOf(self.player):
				if not loopUnit.processedInTurn():
					loopUnit.setTurnProcessedTo(True)

			return

		if self.player.isHuman():
			self.findAutomatedUnits(simulation)
		else:
			self.recruitUnits(simulation)

		# Make sure we have a unit to handle
		if len(self.currentTurnUnits) > 0:
			# Make sure the economic plots are up - to - date, it has a caching system in it.
			self.player.economicAI.updatePlots(simulation)

			# Start by establishing the priority order for moves this turn
			self.establishHomelandPriorities(simulation)

			# Put together lists of places we may want to move toward
			self.findHomelandTargets(simulation)

			# Loop through each move assigning units when available
			self.assignHomelandMoves(simulation)

		return

	def recruitUnits(self, simulation):
		"""Mark all the units that will be under homeland AI control this turn"""
		self.currentTurnUnits = []

		# Loop through our units
		for unit in simulation.unitsOf(self.player):
			# Never want immobile / dead units or ones that have already moved
			if not unit.processedInTurn() and not unit.isDelayedDeath() and unit.task() != UnitTaskType.unknown and unit.canMove():
				self.currentTurnUnits.append(unit)

		return

	def establishHomelandPriorities(self, simulation):
		"""Choose which moves to emphasize this turn"""
		flavorDefense = int(
			float(self.player.valueOfPersonalityFlavor(FlavorType.defense)) * HomelandAI.flavorDampening)
		# flavorOffense = Int(Double(player.valueOfPersonalityFlavor(of:.offense)) *self.flavorDampening)
		flavorExpand = self.player.valueOfPersonalityFlavor(FlavorType.expansion)
		flavorImprove = 0
		flavorNavalImprove = 0
		flavorExplore = int(float(self.player.valueOfPersonalityFlavor(FlavorType.recon)) * HomelandAI.flavorDampening)
		flavorGold = self.player.valueOfPersonalityFlavor(FlavorType.gold)
		# flavorScience = player.valueOfPersonalityFlavor(of:.science)
		# flavorWonder = player.valueOfPersonalityFlavor(of:.wonder)
		flavorMilitaryTraining = self.player.valueOfPersonalityFlavor(FlavorType.militaryTraining)

		self.movePriorityList = []
		self.movePriorityTurn = simulation.currentTurn

		# Loop through each possible homeland move(other than "none" or "unassigned")
		for homelandMoveType in list(HomelandMoveType):
			priority = homelandMoveType.priority()

			# Garrisons must beat out sentries if policies encourage garrisoning
			if homelandMoveType == HomelandMoveType.garrison:
				if self.player.government.hasPolicyEncouragingGarrisons():
					priority = 20 + 1  # AI_HOMELAND_MOVE_PRIORITY_SENTRY + 1
				else:
					priority = 10  # AI_HOMELAND_MOVE_PRIORITY_GARRISON

			# Make sure base priority is not negative
			if priority >= 0:

				# Defensive moves
				if homelandMoveType in [
					HomelandMoveType.garrison, HomelandMoveType.heal, HomelandMoveType.toSafety,
					HomelandMoveType.mobileReserve, HomelandMoveType.sentry, HomelandMoveType.aircraftToTheFront]:
					priority += flavorDefense

				# Other miscellaneous types
				if homelandMoveType in [HomelandMoveType.explore, HomelandMoveType.exploreSea]:
					priority += flavorExplore

				if homelandMoveType == HomelandMoveType.settle:
					priority += flavorExpand

				if homelandMoveType == HomelandMoveType.worker:
					priority += flavorImprove

				if homelandMoveType == HomelandMoveType.workerSea:
					priority += flavorNavalImprove

				if homelandMoveType == HomelandMoveType.upgrade:
					priority += flavorMilitaryTraining

				if homelandMoveType == HomelandMoveType.ancientRuins:
					priority += flavorExplore

				if homelandMoveType == HomelandMoveType.tradeUnit:
					priority += flavorGold

				# Store off this move and priority
				self.movePriorityList.append(HomelandMove(homelandMoveType, priority))

		# Now sort the moves in priority order
		self.movePriorityList.sort()

	def findHomelandTargets(self, simulation):
		"""Make lists of everything we might want to target with the homeland AI this turn"""
		# Clear out target lists since we rebuild them each turn
		self.targetedCities = []
		self.targetedSentryPoints = []
		self.targetedForts = []
		self.targetedNavalResources = []
		self.targetedHomelandRoads = []
		self.targetedAncientRuins = []

		# Look at every tile on map
		for point in simulation.points():
			tile = simulation.tileAt(point)

			if tile.isVisibleTo(self.player):
				# get some values
				civilianUnit = simulation.unitAt(point, UnitMapType.civilian)
				combatUnit = simulation.unitAt(point, UnitMapType.combat)

				# Have a...
				# ... friendly city?
				city = simulation.cityAt(point)
				if city is not None and city.player == self.player:
					# Don't send another unit, if the tactical AI already sent a garrison here
					addTarget = False

					unit = simulation.unitAt(point, UnitMapType.combat)
					if unit is not None:
						if unit.isUnderTacticalControl():
							addTarget = True
					else:
						addTarget = True

					if addTarget:
						newTarget = HomelandTarget(HomelandTargetType.city)
						newTarget.target = point
						newTarget.city = city
						newTarget.threatValue = city.threatValue()
						self.targetedCities.append(newTarget)

				elif tile.terrain().isWater() and not tile.hasAnyImprovement():
					# ... naval resource?
					if tile.hasAnyResourceFor(self.player):
						workingCity = tile.workingCity()
						if workingCity is not None and workingCity.player == self.player:
							# Find proper improvement
							improvement = next(iter(tile.possibleImprovements()), None)
							if improvement is not None:
								newTarget = HomelandTarget(HomelandTargetType.navalResource)
								newTarget.target = point
								newTarget.improvement = improvement
								self.targetedNavalResources.append(newTarget)

				elif tile.hasImprovement(ImprovementType.goodyHut):
					# ... un-popped goody hut?
					newTarget = HomelandTarget(HomelandTargetType.ancientRuin)
					newTarget.target = point
					self.targetedAncientRuins.append(newTarget)

				elif civilianUnit is not None:
					# ... enemy civilian(or embarked) unit?
					if self.player.diplomacyAI.isAtWarWith(civilianUnit.player) and not civilianUnit.canDefend():
						newTarget = HomelandTarget(HomelandTargetType.ancientRuin)
						newTarget.target = point
						self.targetedAncientRuins.append(newTarget)

				elif tile.terrain().isLand() and combatUnit is None:
					# ... possible sentry point? (must be empty or only have friendly units)

					# Must be at least adjacent to our land
					if tile.owner() is None or tile.owner() == self.player:
						# See how many outside plots are nearby to monitor
						outsidePlots: int = tile.numberOfAdjacentDifferentPlayer(self.player, ignoreWater=True, simulation=simulation)

						if outsidePlots > 0:
							newTarget = HomelandTarget(HomelandTargetType.sentryPoint)
							newTarget.target = point
							newTarget.auxData = tile

							# Get weight for this sentry point
							weight = outsidePlots * 100
							weight += tile.defenseModifierFor(self.player)
							weight += self.player.plotDangerAt(point)

							friendlyCity = self.player.closestFriendlyCity(point, 5, simulation)
							if friendlyCity is not None and friendlyCity.player == self.player:
								weight += friendlyCity.threatValue() * friendlyCity.population() / 50
								if friendlyCity.isCapital():
									weight = (weight * 125) / 100  # AI_MILITARY_CITY_THREAT_WEIGHT_CAPITAL

							if tile.isHills():
								weight *= 2

							if simulation.isCoastalAt(point):
								weight /= 2

							newTarget.auxIntData = weight
							self.targetedSentryPoints.append(newTarget)

				elif tile.hasOwner() and tile.owner() == self.player and tile.hasAnyRoute():
					# ...road segment in friendly territory?
					newTarget = HomelandTarget(HomelandTargetType.homeRoad)
					newTarget.target = point
					self.targetedHomelandRoads.append(newTarget)

		# Post-processing on targets
		self.eliminateAdjacentSentryPoints()
		self.eliminateAdjacentHomelandRoads()
		self.targetedCities.sort()

	def assignHomelandMoves(self, simulation):
		"""Choose which moves to run and assign units to it"""
		# Proceed in priority order
		for movePriorityItem in self.movePriorityList:
			if movePriorityItem.moveType == HomelandMoveType.explore:  # AI_HOMELAND_MOVE_EXPLORE
				self.plotExplorerMoves(simulation)
			elif movePriorityItem.moveType == HomelandMoveType.exploreSea:  # AI_HOMELAND_MOVE_EXPLORE_SEA
				self.plotExplorerSeaMoves(simulation)
			elif movePriorityItem.moveType == HomelandMoveType.settle:  # AI_HOMELAND_MOVE_SETTLE:
				self.plotFirstTurnSettlerMoves(simulation)
			elif movePriorityItem.moveType == HomelandMoveType.garrison:  # AI_HOMELAND_MOVE_GARRISON
				self.plotGarrisonMoves(simulation)
			elif movePriorityItem.moveType == HomelandMoveType.heal:  # AI_HOMELAND_MOVE_HEAL
				self.plotHealMoves(simulation)
			elif movePriorityItem.moveType == HomelandMoveType.toSafety:  # AI_HOMELAND_MOVE_TO_SAFETY
				self.plotMovesToSafety(simulation)
			elif movePriorityItem.moveType == HomelandMoveType.mobileReserve:  # AI_HOMELAND_MOVE_MOBILE_RESERVE
				self.plotMobileReserveMoves(simulation)
			elif movePriorityItem.moveType == HomelandMoveType.sentry:  # AI_HOMELAND_MOVE_SENTRY
				self.plotSentryMoves(simulation)
			elif movePriorityItem.moveType == HomelandMoveType.worker:  # AI_HOMELAND_MOVE_WORKER
				self.plotWorkerMoves(simulation)
			elif movePriorityItem.moveType == HomelandMoveType.workerSea:  # AI_HOMELAND_MOVE_WORKER_SEA
				self.plotWorkerSeaMoves(simulation)
			elif movePriorityItem.moveType == HomelandMoveType.patrol:  # AI_HOMELAND_MOVE_PATROL
				self.plotPatrolMoves(simulation)
			elif movePriorityItem.moveType == HomelandMoveType.upgrade:  # AI_HOMELAND_MOVE_UPGRADE
				self.plotUpgradeMoves(simulation)
			elif movePriorityItem.moveType == HomelandMoveType.ancientRuins:  # AI_HOMELAND_MOVE_ANCIENT_RUINS
				self.plotAncientRuinMoves(simulation)
			elif movePriorityItem.moveType == HomelandMoveType.aircraftToTheFront:  # AI_HOMELAND_MOVE_AIRCRAFT_TO_THE_FRONT
				self.plotAircraftMoves(simulation)
			elif movePriorityItem.moveType == HomelandMoveType.tradeUnit:  # AI_HOMELAND_MOVE_TRADE_UNIT
				self.plotTradeUnitMoves(simulation)
		#
		# TODO
		#             /*case .writer:
		#                  # AI_HOMELAND_MOVE_WRITER:
		#	self.plotWriterMoves()*/
		#             /*case AI_HOMELAND_MOVE_ARTIST_GOLDEN_AGE:
		#                 PlotArtistMoves();
		#                 break;
		#             case AI_HOMELAND_MOVE_MUSICIAN:
		#                 PlotMusicianMoves();
		#                 break;
		#             case AI_HOMELAND_MOVE_SCIENTIST_FREE_TECH:
		#                 PlotScientistMoves();
		#                 break;
		#             case AI_HOMELAND_MOVE_ENGINEER_HURRY:
		#                 PlotEngineerMoves();
		#                 break;
		#             case AI_HOMELAND_MOVE_MERCHANT_TRADE:
		#                 PlotMerchantMoves();
		#                 break;
		#             case AI_HOMELAND_MOVE_GENERAL_GARRISON:
		#                 PlotGeneralMoves();
		#                 break;
		#             case AI_HOMELAND_MOVE_ADMIRAL_GARRISON:
		#                 PlotAdmiralMoves();
		#                 break;
		#             case AI_HOMELAND_MOVE_PROPHET_RELIGION:
		#                 PlotProphetMoves();
		#                 break;
		#             case AI_HOMELAND_MOVE_MISSIONARY:
		#                 PlotMissionaryMoves();
		#                 break;
		#             case AI_HOMELAND_MOVE_INQUISITOR:
		#                 PlotInquisitorMoves();
		#                 break;
		#             case AI_HOMELAND_MOVE_AIRCRAFT_TO_THE_FRONT:
		#                 PlotAircraftMoves();
		#                 break;
		#             case AI_HOMELAND_MOVE_ADD_SPACESHIP_PART:
		#                 PlotSSPartAdds();
		#                 break;
		#             case AI_HOMELAND_MOVE_SPACESHIP_PART:
		#                 PlotSSPartMoves();
		#                 break;*/
		#             /*case AI_HOMELAND_MOVE_ARCHAEOLOGIST:
		#                 PlotArchaeologistMoves();
		#                 break;
		#             case AI_HOMELAND_MOVE_AIRLIFT:
		#                 PlotAirliftMoves();
		#                 break;*/
		#
		#             default:
		#                 logging.debug(f"not implemented: HomelandAI - {movePriorityItem.type}")

		self.reviewUnassignedUnits(simulation)
		return

	def plotExplorerMoves(self, simulation):
		"""Get units with explore AI and plan their moves"""
		self.clearCurrentMoveUnits()

		# Loop through all recruited units
		for currentTurnUnit in self.currentTurnUnits:
			if currentTurnUnit.task() == UnitTaskType.explore or \
				(currentTurnUnit.isAutomated() and currentTurnUnit.domain() == UnitDomainType.land and
				 currentTurnUnit.automateType() == UnitAutomationType.explore):
				homelandUnit = HomelandUnit(currentTurnUnit)
				self.currentMoveUnits.append(homelandUnit)

		if len(self.currentMoveUnits) > 0:
			# Execute twice so explorers who can reach the end of their sight can move again
			self.executeExplorerMoves(land=True, simulation=simulation)
			self.executeExplorerMoves(land=True, simulation=simulation)

		return

	def plotTradeUnitMoves(self, simulation):
		"""Send trade units on their way"""
		self.clearCurrentMoveUnits()

		# Loop through all remaining units
		for currentTurnUnit in self.currentTurnUnits:
			if currentTurnUnit.task() == UnitTaskType.trade:
				unit = HomelandUnit(currentTurnUnit)
				self.currentMoveUnits.append(unit)

		if len(self.currentMoveUnits) > 0:
			self.executeTradeUnitMoves(simulation)

		return

	def clearCurrentMoveUnits(self):
		self.currentMoveUnits = []
		self.currentBestMoveUnit = None
		self.currentBestMoveUnitTurns = sys.maxsize

	def plotExplorerSeaMoves(self, simulation):
		"""Get units with explore AI and plan their moves"""
		self.clearCurrentMoveUnits()

		# Loop through all recruited units
		for currentTurnUnit in self.currentTurnUnits:
			if currentTurnUnit.task() == UnitTaskType.exploreSea or \
				(currentTurnUnit.isAutomated() and currentTurnUnit.domain() == UnitDomainType.sea and
				 currentTurnUnit.automateType() == UnitTaskType.explore):
				self.currentMoveUnits.append(HomelandUnit(currentTurnUnit))

		if len(self.currentMoveUnits) > 0:
			# Execute twice so explorers who can reach the end of their sight can move again
			self.executeExplorerMoves(land=False, simulation=simulation)
			self.executeExplorerMoves(land=False, simulation=simulation)

		return

	def plotFirstTurnSettlerMoves(self, simulation):
		"""Get our first city built"""
		self.clearCurrentMoveUnits()

		# Loop through all recruited units
		for currentTurnUnit in self.currentTurnUnits:
			goingToSettle = False

			if not currentTurnUnit.player.isHuman():
				if len(simulation.citiesOf(self.player)) == 0 and len(self.currentMoveUnits) == 0:
					if currentTurnUnit.canFoundAt(currentTurnUnit.location, simulation):
						homelandUnit = HomelandUnit(currentTurnUnit)
						self.currentMoveUnits.append(homelandUnit)
						goingToSettle = True

			# If we find a settler that isn't in an operation, let's keep him in place
			if not goingToSettle and currentTurnUnit.isFound() and currentTurnUnit.army() is None:
				currentTurnUnit.pushMission(UnitMission(UnitMissionType.skip), simulation)
				currentTurnUnit.finishMoves()

		if len(self.currentMoveUnits) > 0:
			self.executeFirstTurnSettlerMoves(simulation)

		return

	def executeFirstTurnSettlerMoves(self, simulation):
		"""Creates cities for AI civilizations on first turn"""
		for currentMoveUnit in self.currentMoveUnits:
			if currentMoveUnit.unit is not None:
				currentMoveUnit.unit.pushMission(UnitMission(UnitMissionType.found), simulation)
				self.unitProcessed(currentMoveUnit.unit)

				logging.info(f"Founded city at {currentMoveUnit.unit.location}")

		return

	def unitProcessed(self, unit):
		"""Remove a unit that we've allocated from list of units to move this turn"""
		self.currentTurnUnits = list(filter(lambda loopUnit: loopUnit.location != unit.location, self.currentTurnUnits))
		unit.setTurnProcessedTo(True)

	def plotAncientRuinMoves(self, simulation):
		"""Pop goody huts nearby"""
		# Do we have any targets of this type?
		if len(self.targetedAncientRuins) > 0:
			# Prioritize them (LATER)

			# See how many moves of this type we can execute
			for (index, homelandTarget) in enumerate(self.targetedAncientRuins):
				targetTile = simulation.tileAt(homelandTarget.target)

				self.findUnitsForMove(HomelandMoveType.ancientRuins, firstTime=(index == 0), simulation=simulation)

				if (len(self.currentMoveHighPriorityUnits) + len(self.currentMoveUnits)) > 0:
					if self.bestUnitToReachTarget(targetTile, HomelandAI.defensiveMoveTurns, simulation):
						self.executeMoveToTarget(targetTile, garrisonIfPossible=False, simulation=simulation)
						logging.debug(f"Moving to goody hut (non-explorer), {targetTile.point}")

		return

	def plotUpgradeMoves(self, simulation):
		pass

	def plotHealMoves(self, simulation):
		"""Find out which units would like to heal"""
		self.clearCurrentMoveUnits()

		# Loop through all recruited units
		for currentTurnUnit in self.currentTurnUnits:
			tile = simulation.tileAt(currentTurnUnit.location)

			if not currentTurnUnit.isHuman():

				# Am I under 100 % health and not at sea or already in a city?
				if currentTurnUnit.healthPoints() < currentTurnUnit.maxHealthPoints() and \
					not currentTurnUnit.isEmbarked() and simulation.cityAt(currentTurnUnit.location) is None:

					# If I'm a naval unit I need to be in friendly territory
					if currentTurnUnit.domain() != UnitDomainType.sea or tile.isFriendlyTerritoryFor(self.player,
																									 simulation):

						if not currentTurnUnit.isUnderEnemyRangedAttack():
							self.currentMoveUnits.append(HomelandUnit(currentTurnUnit))
							logging.info(f"{currentTurnUnit.unitType} healing at {currentTurnUnit.location}")

			if len(self.currentMoveUnits) > 0:
				self.executeHeals(simulation)

	def plotMovesToSafety(self, simulation):
		"""Moved endangered units to safe hexes"""
		self.clearCurrentMoveUnits()

		# Loop through all recruited units
		for currentTurnUnit in self.currentTurnUnits:
			tile = simulation.tileAt(currentTurnUnit.location)
			dangerLevel = self.player.dangerPlotsAI.dangerAt(currentTurnUnit.location)

			# Danger value of plot must be greater than 0
			if dangerLevel > 0:
				addUnit = False

				# If civilian( or embarked unit) always ready to flee
				# slewis - 4.18.2013 - Problem here is that a combat unit that is a boat can get stuck in a city
				# hiding from barbarians on the land
				if not currentTurnUnit.canDefend():
					if currentTurnUnit.isAutomated() and currentTurnUnit.baseCombatStrength(ignoreEmbarked=True) > 0:
						# then this is our special case
						pass
					else:
						addUnit = True
				elif currentTurnUnit.healthPoints() < currentTurnUnit.maxHealthPoints():
					# Also may be true if a damaged combat unit
					if currentTurnUnit.isBarbarian():
						# Barbarian combat units - only naval units flee (but they flee if they have taken ANY damage)
						if currentTurnUnit.domain() == UnitDomainType.sea:
							addUnit = True
					elif currentTurnUnit.isUnderEnemyRangedAttack() or \
						currentTurnUnit.attackStrengthAgainst(unit=None, city=None, tile=tile,
															  simulation=simulation) * 2 <= \
						currentTurnUnit.baseCombatStrength(ignoreEmbarked=False):
						# Everyone else flees at less than or equal to 50% combat strength
						addUnit = True
				elif not currentTurnUnit.isBarbarian():
					# Also flee if danger is really high in current plot (but not if we're barbarian)
					acceptableDanger = currentTurnUnit.attackStrengthAgainst(unit=None, city=None, tile=tile,
																			 simulation=simulation) * 100
					if int(dangerLevel) > acceptableDanger:
						addUnit = True

				if addUnit:
					# Just one unit involved in this move to execute
					self.currentMoveUnits.append(HomelandUnit(currentTurnUnit))

		if len(self.currentMoveUnits) > 0:
			self.executeMovesToSafestPlot(simulation)

		return

	def plotWorkerMoves(self, simulation):
		"""Find something for all workers to do"""
		self.clearCurrentMoveUnits()

		# Loop through all recruited units
		for currentTurnUnit in self.currentTurnUnits:
			if currentTurnUnit.task() == UnitTaskType.work or (
				currentTurnUnit.isAutomated() and currentTurnUnit.domain() == UnitDomainType.land and currentTurnUnit.automateType() == UnitAutomationType.build):
				homelandUnit = HomelandUnit(currentTurnUnit)
				self.currentMoveUnits.append(homelandUnit)

		if len(self.currentMoveUnits) > 0:
			self.executeWorkerMoves(simulation)

		return

	def plotWorkerSeaMoves(self, simulation):
		"""Send out work boats to harvest resources"""
		self.clearCurrentMoveUnits()

		# Loop through all recruited units
		for currentTurnUnit in self.currentTurnUnits:
			if currentTurnUnit.task() == UnitTaskType.workerSea or \
				(currentTurnUnit.isAutomated() and currentTurnUnit.domain() == UnitDomainType.sea and
				 currentTurnUnit.automateType() == UnitAutomationType.build):
				homelandUnit = HomelandUnit(currentTurnUnit)
				self.currentMoveUnits.append(homelandUnit)

		for currentMoveUnit in self.currentMoveUnits:
			unit = currentMoveUnit.unit
			targetIndex: Optional[HomelandTarget] = None
			targetMoves: int = sys.maxsize

			pathFinderDataSource = simulation.ignoreUnitsPathfinderDataSource(
				unit.movementType(), unit.player,
				canEmbark=unit.player.canEmbark(), canEnterOcean=unit.player.canEnterOcean())
			pathFinder = AStarPathfinder(pathFinderDataSource)

			# See how many moves of this type we can execute
			for target in self.targetedNavalResources:
				build = target.improvement.buildType()
				targetLocation = target.target

				if not currentMoveUnit.canBuild(build, targetLocation, testVisible=True, testGold=True,
												simulation=simulation):
					continue

				moves = pathFinder.turnsToReachTarget(unit, targetLocation, simulation)
				if moves < targetMoves:
					targetMoves = moves
					targetIndex = target

			if targetIndex is not None:
				# Queue best one up to capture it
				targetLocation = targetIndex.target

				result = False
				path = unit.pathTowards(targetLocation, options=None, simulation=simulation)
				if path is not None:
					unit.pushMission(UnitMission(UnitMissionType.moveTo, target=targetLocation), simulation)
					if unit.location == targetLocation:
						mission = UnitMission(
							UnitMissionType.build,
							buildType=targetIndex.improvement.buildType(),
							target=targetLocation,
							path=path,
							options=None
						)
						unit.pushMission(mission, simulation)
						result = True
					else:
						unit.finishMoves()

					# Delete this unit from those we have to move
					self.unitProcessed(unit)
				else:
					if unit.location == targetLocation:
						mission = UnitMission(
							UnitMissionType.build,
							buildType=BuildType.fromImprovement(targetIndex.improvement),
							target=targetLocation,
							path=None,
							options=None
						)
						unit.pushMission(mission, simulation)
						result = True

				if result:
					logging.debug(f"Harvesting naval resource at: {targetLocation}")
				else:
					logging.debug(f"Moving toward naval resource at: {targetLocation}")

	def plotSentryMoves(self, simulation):
		"""Send units to sentry points around borders"""
		# Do we have any targets of this type?
		if len(self.targetedSentryPoints) > 0:
			# Prioritize them (LATER)

			# See how many moves of this type we can execute
			for (index, targetedSentryPoint) in enumerate(self.targetedSentryPoints):
				# AI_PERF_FORMAT("Homeland-perf.csv", ("PlotSentryMoves, Turn %03d, %s", GC.getGame().getElapsedGameTurns(), m_pPlayer->getCivilizationShortDescription()) );

				# CvPlot * pTarget = GC.getMap().plot(m_TargetedSentryPoints[iI].GetTargetX(), m_TargetedSentryPoints[iI].GetTargetY());
				targetTile = simulation.tileAt(targetedSentryPoint.target)

				self.findUnitsForMove(HomelandMoveType.sentry, firstTime=(index == 0), simulation=simulation)

				if (len(self.currentMoveHighPriorityUnits) + len(self.currentMoveUnits)) > 0:
					if self.bestUnitToReachTarget(targetTile, maxTurns=sys.maxsize, simulation=simulation):
						self.executeMoveToTarget(targetTile, garrisonIfPossible=False, simulation=simulation)
						logging.debug(
								f"Moving to sentry point, {targetedSentryPoint.target or constants.invalidHexPoint}), " +
								f"Priority: {targetedSentryPoint.threatValue}")

		return

	def plotMobileReserveMoves(self, simulation):
		"""Send units to roads for quick movement to face any threat"""
		# Do we have any targets of this type?
		if len(self.targetedHomelandRoads) > 0:
			# Prioritize them (LATER)

			# See how many moves of this type we can execute
			for (index, targetedHomelandRoad) in enumerate(self.targetedHomelandRoads):
				if targetedHomelandRoad.target is None:
					continue

				targetTile = simulation.tileAt(targetedHomelandRoad.target)

				if targetTile is None:
					continue

				self.findUnitsForMove(HomelandMoveType.mobileReserve, firstTime=(index == 0), simulation=simulation)

				if (len(self.currentMoveHighPriorityUnits) + len(self.currentMoveUnits)) > 0:
					if self.bestUnitToReachTarget(targetTile, maxTurns=sys.maxsize, simulation=simulation):
						self.executeMoveToTarget(targetTile, garrisonIfPossible=False, simulation=simulation)
						logging.debug(f"Moving to mobile reserve muster pt, {targetedHomelandRoad.target}")

		return

	def plotGarrisonMoves(self, simulation):
		"""Send units to garrison cities"""
		# Do we have any targets of this type?
		if len(self.targetedCities) > 0:
			firstRun: bool = True

			for targetedCity in self.targetedCities:
				targetPoint = targetedCity.target
				if targetPoint is None:
					continue

				target = simulation.tileAt(targetPoint)

				if target is None:
					continue

				city = simulation.cityAt(targetPoint)

				if city is None:
					continue

				if city.lastTurnGarrisonAssigned() < simulation.currentTurn:
					# Grab units that make sense for this move type
					self.findUnitsForMove(HomelandMoveType.garrison, firstTime=firstRun, simulation=simulation)

					if (len(self.currentMoveHighPriorityUnits) + len(self.currentMoveUnits)) > 0:
						if self.bestUnitToReachTarget(target, maxTurns=HomelandAI.defensiveMoveTurns, simulation=simulation):
							self.executeMoveToTarget(target, garrisonIfPossible=True, simulation=simulation)
							city.setLastTurnGarrisonAssigned(simulation.currentTurn)

				firstRun = False

		return

	def plotPatrolMoves(self, simulation):
		"""When nothing better to do, have units patrol to an adjacent tiles"""
		self.clearCurrentMoveUnits()

		# Loop through all remaining units
		for currentTurnUnit in self.currentTurnUnits:
			unit = currentTurnUnit

			if not unit.isHuman() and unit.domain() != UnitDomainType.air and not unit.isTrading():
				target = self.findPatrolTarget(unit, simulation)
				if target is not None:
					homelandUnit = HomelandUnit(unit)
					homelandUnit.target = target
					self.currentMoveUnits.append(homelandUnit)

					logging.debug(f"{unit.name()} patrolling to, {target}, Current {unit.location}")

		if len(self.currentMoveUnits) > 0:
			self.executePatrolMoves(simulation)

		return

	def reviewUnassignedUnits(self, simulation):
		"""Log that we couldn't find assignments for some units"""
		# Loop through all remaining units
		for currentTurnUnit in self.currentTurnUnits:
			currentTurnUnit.pushMission(UnitMission(UnitMissionType.skip), simulation)
			currentTurnUnit.setTurnProcessedTo(True)

			logging.warning(f"<< HomelandAI ### Unassigned {currentTurnUnit.name()} at {currentTurnUnit.location} ### >>")

	def findAutomatedUnits(self, simulation):
		"""Mark all the units that will be under tactical AI control this turn"""
		self.currentTurnUnits = []

		# Loop through our units
		for loopUnit in simulation.unitsOf(self.player):
			if loopUnit.isAutomated() and not loopUnit.processedInTurn() and loopUnit.task() != UnitTaskType.unknown \
				and loopUnit.canMove():
				self.currentTurnUnits.append(loopUnit)

	def executeWorkerMoves(self, simulation):
		"""Moves units to explore the map"""
		dangerPlotsAI = self.player.dangerPlotsAI

		for currentMoveUnit in self.currentMoveUnits:
			unit = currentMoveUnit.unit

			if unit is not None:
				danger = dangerPlotsAI.dangerAt(unit.location)
				if danger > 0.0:
					if self.moveCivilianToSafety(unit, simulation=simulation):
						logging.debug(
							f"{self.player.leader} moves {unit.name()} in turn {simulation.currentTurn} to 1st Safety,")
						unit.finishMoves()
						self.unitProcessed(unit)
						continue

				actionPerformed = self.executeWorkerMove(unit, simulation)
				if actionPerformed:
					continue

				# if there's nothing else to do, move to the safest spot nearby
				if self.moveCivilianToSafety(unit, ignoreUnits=True, simulation=simulation):
					logging.debug(f"{self.player.leader} moves {unit.name()} in turn {simulation.currentTurn} to 2nd Safety,")

					unit.pushMission(UnitMission(UnitMissionType.skip), simulation)

					if not self.player.isHuman():
						unit.finishMoves()

					self.unitProcessed(unit)
					continue

				# slewis - this was removed because a unit would eat all its moves.
				# So if it didn't do anything this turn, it wouldn't be able to work
				unit.pushMission(UnitMission(UnitMissionType.skip), simulation)

				if not self.player.isHuman():
					unit.finishMoves()

				self.unitProcessed(unit)
		return

	def executeWorkerMove(self, unit, simulation) -> bool:
		# evaluator
		directive: Optional[BuilderDirective] = self.player.builderTaskingAI.evaluateBuilder(unit, simulation=simulation)

		if directive is not None:
			if directive.directiveType == BuilderDirectiveType.buildImprovementOnResource or \
				directive.directiveType == BuilderDirectiveType.buildImprovement or \
				directive.directiveType == BuilderDirectiveType.repair or \
				directive.directiveType == BuilderDirectiveType.buildRoute or \
				directive.directiveType == BuilderDirectiveType.chop or \
				directive.directiveType == BuilderDirectiveType.removeRoad:

				# are we already there?
				if directive.target == unit.location:
					# check to see if we already have this mission as the unit's head mission
					pushMission = True
					missionData: UnitMission = unit.peekMission()
					if missionData is not None:
						if missionData.missionType == UnitMissionType.build and missionData.buildType == directive.build:
							pushMission = False

					if pushMission:
						unitMission = UnitMission(UnitMissionType.build)
						unitMission.buildType = directive.build
						unit.pushMission(unitMission, simulation)

					if unit.readyToMove():
						unit.finishMoves()

					self.unitProcessed(unit)

				else:
					unit.pushMission(UnitMission(UnitMissionType.moveTo, target=directive.target), simulation)
					unit.finishMoves()
					self.unitProcessed(unit)

				return True
		else:
			logging.warning("builder has no directive")
			unit.doCancelOrder(simulation)

		return False

	def executeExplorerMoves(self, land: bool, simulation):
		"""Moves units to explore the map"""
		self.player.economicAI.updatePlots(simulation)
		foundNearbyExplorePlot = False

		pathfinderDataSource = simulation.ignoreUnitsPathfinderDataSource(
			UnitMovementType.walk if land else UnitMovementType.swimShallow,
			self.player,
			self.player.canEmbark(),
			canEnterOcean=self.player.canEnterOcean()
		)
		pathfinder = AStarPathfinder(pathfinderDataSource)

		for homelandUnit in self.currentMoveUnits:
			if homelandUnit.unit is None:
				continue

			unit = homelandUnit.unit
			if unit.processedInTurn():
				continue

			unitPlayer = unit.player
			if unitPlayer is None:
				continue

			goodyPlot = self.player.economicAI.unitTargetGoodyPlot(unit, simulation)
			if goodyPlot is not None:
				logging.debug(f"Unit {unit.name()} at {unit.location} has goody target at {goodyPlot.point}")

				if (goodyPlot.hasImprovement(ImprovementType.goodyHut) or
					goodyPlot.hasImprovement(ImprovementType.barbarianCamp)) and \
					simulation.visibleEnemyAt(goodyPlot.point, self.player) is None:

					path = pathfinder.shortestPath(unit.location, goodyPlot.point)
					if path is not None:
						firstStep = path.firstSegments(unit.moves())
						if firstStep is not None:
							stepPoint = firstStep.points()[-1]
							logging.debug(f"Unit {unit.name()} Moving to goody hut, from {unit.location}")

							unit.pushMission(UnitMission(UnitMissionType.moveTo, target=stepPoint), simulation)
							unit.finishMoves()
							self.unitProcessed(unit)
						else:
							logging.debug(f"Unit {unit.name()} no end turn plot to goody from {unit.location}")

						continue
					else:
						logging.warning(f"Unit {unit.name()} can't find path to goody from {unit.location}")

			bestPlot = None
			bestPlotScore = 0

			sightRange = unit.sight()
			movementRange = unit.movesLeft()  # / GC.getMOVE_DENOMINATOR();
			for evalPoint in unit.location.areaWithRadius(movementRange):
				evalPlot = simulation.tileAt(evalPoint)

				if evalPlot is None:
					continue

				if not self.isValidExplorerEndTurnPlot(unit, evalPlot, simulation):
					continue

				path = pathfinder.shortestPath(unit.location, evalPoint)

				if path is None:
					continue

				distance = len(path.points())
				if distance > 1:
					continue

				domain = unit.domain()
				score = self.player.economicAI.scoreExplore(evalPoint, self.player, sightRange, domain, simulation)
				if score > 0:
					if domain == UnitDomainType.land and evalPlot.hasHills():
						score += 50
					elif domain == UnitDomainType.sea and simulation.adjacentToLand(evalPoint):
						score += 200
					elif domain == UnitDomainType.land and unit.isEmbarkAllWater() and not evalPlot.isShallowWater():
						score += 200

				if score > bestPlotScore:
					bestPlot = evalPlot
					bestPlotScore = score
					foundNearbyExplorePlot = True

			if bestPlot is not None and movementRange > 0:
				explorationPlots = self.player.economicAI.explorationPlots()
				if len(explorationPlots) > 0:
					bestPlotScore = 0

					for explorationPlot in explorationPlots:
						evalPlot = simulation.tileAt(explorationPlot.location)
						if evalPlot is None:
							continue

						plotScore = 0

						if not self.isValidExplorerEndTurnPlot(unit, evalPlot, simulation):
							continue

						rating = explorationPlot.rating

						# hitting the pathfinder, may not be the best idea...
						path = pathfinder.shortestPath(unit.location, explorationPlot.location)
						if path is None:
							continue

						distance = path.cost() + random.uniform(0.0, 5.0)
						if distance == 0:
							plotScore = 1000 * rating
						else:
							plotScore = (1000 * rating) / int(distance)

						if plotScore > bestPlotScore:
							endTurnPoint = path.points()[-1]
							endTurnPlot = simulation.tileAt(endTurnPoint)

							if endTurnPoint == unit.location:
								bestPlot = None
								bestPlotScore = plotScore
							elif self.isValidExplorerEndTurnPlot(unit, endTurnPlot, simulation):
								bestPlot = endTurnPlot
								bestPlotScore = plotScore
							else:
								# not a valid destination
								continue

			if bestPlot is not None:
				unitMission = UnitMission(UnitMissionType.moveTo, buildType=None, target=bestPlot.point, options=[])
				unit.pushMission(unitMission, simulation)

				# Only mark as done if out of movement
				if unit.moves() <= 0:
					self.unitProcessed(unit)
			else:
				if unitPlayer.isHuman():
					unit.automate(UnitAutomationType.none, simulation)
					self.unitProcessed(unit)
				else:
					# If this is a land explorer and there is no ignore unit path to a friendly city, then disband him
					if unit.task() == UnitTaskType.explore:
						foundPath = False

						for city in simulation.citiesOf(self.player):
							if pathfinder.doesPathExist(unit.location, city.location):
								foundPath = True
								break

							if not foundPath:
								self.unitProcessed(unit)
								unit.doKill(delayed=False, otherPlayer=None, simulation=simulation)
								self.player.economicAI.incrementExplorersDisbanded()
					elif unit.task() == UnitTaskType.exploreSea:
						# NOOP
						pass

		return

	def executeTradeUnitMoves(self, simulation):
		"""Get a trade unit and send it to a city!"""
		goldFlavor: float = float(self.player.leader.flavor(FlavorType.gold))
		foodFlavor: float = float(self.player.leader.flavor(FlavorType.growth))
		scienceFlavor: float = float(self.player.leader.flavor(FlavorType.science))

		for currentMoveUnit in self.currentMoveUnits:
			unit = currentMoveUnit.unit

			originCity = simulation.cityAt(unit.origin())
			if originCity is not None:

				bestTradeRoute: Optional[TradeRoute] = None
				bestTradeRouteValue: float = -1.0

				possibleTradeRoutes: [TradeRoute] = self.player.possibleTradeRoutes(originCity, simulation)

				for possibleTradeRoute in possibleTradeRoutes:
					# skip, if already has trade route between these cities
					if self.player.hasTradeRouteFrom(originCity.location, possibleTradeRoute.end()):
						continue

					tradeRouteYields: Yields = possibleTradeRoute.yields(simulation)
					value: float = 0.0
					value += tradeRouteYields.gold * goldFlavor
					value += tradeRouteYields.food * foodFlavor
					value += tradeRouteYields.science * scienceFlavor

					if value > bestTradeRouteValue:
						bestTradeRoute = possibleTradeRoute
						bestTradeRouteValue = value

				if bestTradeRoute is not None:
					targetCity = simulation.cityAt(bestTradeRoute.end())

					unit.doEstablishTradeRouteTo(targetCity, simulation)
					self.unitProcessed(unit)
					# unit.finishMoves()
					logging.info(f"Trade unit founded trade route between {originCity.name} and {targetCity.name}")
				else:
					logging.warning("Trade unit idling")

					self.unitProcessed(unit)

					unit.pushMission(UnitMission(UnitMissionType.skip), simulation)
					unit.finishMoves()
			else:
				# try to relocate trader to random city
				randomCity = random.choice(simulation.citiesOf(self.player))
				if randomCity is not None:
					unit.doRebaseTo(randomCity.location)

					logging.debug(f"Trade unit rebased to {randomCity.name}")
				else:
					logging.warning("Trade unit idling")

					self.unitProcessed(unit)

					unit.pushMission(UnitMission(UnitMissionType.skip), simulation)
					unit.finishMoves()

		return

	def findUnitsForMove(self, moveType: HomelandMoveType, firstTime: bool, simulation) -> bool:
		"""Finds both high and normal priority units we can use for this homeland move
		(returns true if at least 1 unit found)"""
		rtnValue: bool = False

		if firstTime:
			self.currentMoveUnits = []
			self.currentMoveHighPriorityUnits = []

			# Loop through all units available to homeland AI this turn
			for loopUnit in self.currentTurnUnits:
				loopUnitPlayer = loopUnit.player
				economicAI = self.player.economicAI

				if not loopUnitPlayer.isHuman():
					# Civilians aren't useful for any of these moves
					if not loopUnit.isCombatUnit():
						continue

					# Scouts aren't useful unless recon is entirely shut off
					if loopUnit.task() == UnitTaskType.explore and economicAI.reconState() != ReconStateType.enough:
						continue

					suitableUnit = False
					highPriority = False

					if moveType == HomelandMoveType.garrison:
						# Want to put ranged units in cities to give them a ranged attack
						if loopUnit.isRanged() and not loopUnit.hasTask(UnitTaskType.cityBombard):
							suitableUnit = True
							highPriority = True

						elif loopUnit.canAttack():  # Don't use non-combatants
							# Don't put units with a combat strength boosted from promotions in cities, these boosts are ignored
							if loopUnit.defenseModifierAgainst(unit=None, city=None, tile=None, ranged=False,
															   simulation=simulation) == 0 \
								and loopUnit.attackModifierAgainst(unit=None, city=None, tile=None,
																   simulation=simulation) == 0:
								suitableUnit = True

					elif moveType == HomelandMoveType.sentry:
						# No ranged units as sentries
						if not loopUnit.isRanged():  # and !loopUnit->noDefensiveBonus()
							suitableUnit = True

							# Units with extra sight are especially valuable
							if loopUnit.sight() > 2:
								highPriority = True

						elif loopUnit.sight() > 2:  # and loopUnit->noDefensiveBonus()
							suitableUnit = True
							highPriority = True

					elif moveType == HomelandMoveType.mobileReserve:
						# Ranged units are excellent in the mobile reserve as are fast movers
						if loopUnit.isRanged() or loopUnit.hasTask(UnitTaskType.fastAttack):
							suitableUnit = True
							highPriority = True
						elif loopUnit.canAttack():
							suitableUnit = True

					elif moveType == HomelandMoveType.ancientRuins:
						# Fast movers are top priority
						if loopUnit.hasTask(UnitTaskType.fastAttack):
							suitableUnit = True
							highPriority = True
						elif loopUnit.canAttack():
							suitableUnit = True

					else:
						# NOOP
						pass

					# If unit was suitable, add it to the proper list
					if suitableUnit:
						unit = HomelandUnit(loopUnit)
						if highPriority:
							self.currentMoveHighPriorityUnits.append(unit)
						else:
							self.currentMoveUnits.append(unit)
						rtnValue = True

		else:  # not first time
			# Normal priority units
			tempList: [HomelandUnit] = [c.copy() for c in self.currentMoveUnits]
			self.currentMoveUnits = []

			for it in tempList:
				if contains(lambda u: u.location == it.unit.location, self.currentTurnUnits):
					self.currentMoveUnits.append(it)
					rtnValue = True

			# High priority units
			tempList = [c.copy() for c in self.currentMoveHighPriorityUnits]
			self.currentMoveHighPriorityUnits = []

			for it in tempList:
				if contains(lambda u: u.location == it.unit.location, self.currentTurnUnits):
					self.currentMoveHighPriorityUnits.append(it)
					rtnValue = True

		return rtnValue

	def isValidExplorerEndTurnPlot(self, unit, plot, simulation):
		if unit.location == plot.point:
			return False

		if not plot.isDiscoveredBy(unit.player):
			return False

		# domain = unit.domain()
		# if plot.sameContinent( as: <  # T##AbstractTile#>) (pPlot->area() != pUnit->area())
		# 	if (!pUnit->CanEverEmbark())
		# 		if (!(eDomain == DOMAIN_SEA and pPlot->isWater()))
		# 			return false;

		# don't let the auto-explore end it's turn in a city
		if plot.isCity():
			return False

		if not unit.canMoveInto(plot.point, options=[], simulation=simulation):
			return False

		return True

	def moveCivilianToSafety(self, unit, ignoreUnits: bool = False, simulation=None) -> bool:
		"""Fleeing to safety for civilian units"""
		if simulation is None:
			raise Exception('simulation must not be None')

		dangerPlotsAI = self.player.dangerPlotsAI
		searchRange = unit.searchRange(1, simulation)

		bestValue = -999999
		bestPlot = None

		for point in unit.location.areaWithRadius(searchRange):
			tile = simulation.tileAt(point)

			if tile is None:
				continue

			if not unit.validTarget(point, simulation):
				continue

			if simulation.isEnemyVisibleAt(point, self.player):
				continue

			# if we can't get there this turn, skip it
			turns = unit.turnsToReach(point, simulation)
			if turns == sys.maxsize or turns > 1:
				continue

			value = 0
			if tile.owner() is not None and tile.owner() == self.player:
				# if this is within our territory, provide a minor benefit
				value += 1

			city = simulation.cityAt(point)

			if city is not None and city.player == self.player:
				value += city.defensiveStrengthAgainst(unit=None, tile=tile, ranged=False, simulation=simulation)

			elif not ignoreUnits:
				otherUnit = simulation.unitAt(point, UnitMapType.combat)
				if otherUnit is not None:
					if otherUnit.player == unit.player:
						if otherUnit.canDefend() and otherUnit.location != unit.location:
							if otherUnit.isWaiting() or not otherUnit.canMove():
								value += otherUnit.defensiveStrengthAgainst(unit=None, city=None, tile=tile, ranged=False, simulation=simulation)

			value -= int(dangerPlotsAI.dangerAt(point))

			if value > bestValue:
				bestValue = value
				bestPlot = tile

		if bestPlot is not None:
			if unit.location == bestPlot.point:
				# logging.debug("\(unit.name()) tried to move to safety, but is already at the best spot, \(bestPlot.point)")
				if unit.canHoldAt(bestPlot.point, simulation):
					logging.debug(f"{unit.name()} tried to move to safety, but is already at the best spot, {bestPlot.point}")
					unit.pushMission(UnitMission(UnitMissionType.skip), simulation)
					return True
				else:
					logging.debug(f"{unit.name()} tried to move to safety, but cannot hold in current location, {bestPlot.point}")
					unit.automate(UnitAutomationType.none, simulation)
			else:
				logging.debug(f"{unit.name()} moving to safety, {bestPlot.point}")
				unit.pushMission(UnitMission(UnitMissionType.moveTo, target=bestPlot.point), simulation)
				return True
		else:
			logging.debug(f"{unit.name()} tried to move to a safe point but couldn't find a good place to go")

		return False

	def executeMovesToSafestPlot(self, simulation):
		"""Moves units to the hex with the lowest danger"""
		dangerPlotsAI = self.player.dangerPlotsAI

		for currentUnit in self.currentTurnUnits:
			radius = currentUnit.moves()

			lowestDanger = 100000000000.0
			bestPlot: Optional[HexPoint] = None

			resultHasZeroDangerMove = False
			resultInTerritory = False
			resultInCity = False
			resultInCover = False

			# For each plot within movement range of the fleeing unit
			for neighbor in currentUnit.location.areaWithRadius(radius):
				if not simulation.valid(neighbor):
					continue

				# Can't be a plot with another player's unit in it or another of our unit of same type
				otherUnit = simulation.unitAt(neighbor, UnitMapType.combat)
				if otherUnit is not None:
					if otherUnit.player == currentUnit.player:
						continue
					elif currentUnit.hasSameType(otherUnit):
						continue

				if not currentUnit.canReachAt(neighbor, 1, simulation):
					continue

				# prefer being in a city with the lowest danger value
				# prefer being in a plot with no danger value
				# prefer being under a unit with the lowest danger value
				# prefer being in your own territory with the lowest danger value
				# prefer the lowest danger value
				danger = dangerPlotsAI.dangerAt(neighbor)
				isZeroDanger = danger <= 0.0
				city = simulation.cityAt(neighbor)
				isInCity = city.player == self.player if city is not None else False
				unit = simulation.unitAt(neighbor, UnitMapType.combat)
				isInCover = unit is not None
				tile = simulation.tileAt(neighbor)
				isInTerritory = tile.owner() == self.player if tile is not None and tile.hasOwner() else False

				updateBestValue = False

				if isInCity:
					if not resultInCity or danger < lowestDanger:
						updateBestValue = True
				elif isZeroDanger:
					if not resultInCity:
						if resultHasZeroDangerMove:
							if isInTerritory and not resultInTerritory:
								updateBestValue = True
						else:
							updateBestValue = True
				elif isInCover:
					if not resultInCity and not resultHasZeroDangerMove:
						if not resultInCover or danger < lowestDanger:
							updateBestValue = True
				elif isInTerritory:
					if not resultInCity and not resultInCover and not resultHasZeroDangerMove:
						if not resultInTerritory or danger < lowestDanger:
							updateBestValue = True
				elif not resultInCity and not resultInCover and not resultInTerritory and not resultHasZeroDangerMove:
					# if we have no good home, head to the lowest danger value
					if danger < lowestDanger:
						updateBestValue = True

				if updateBestValue:
					bestPlot = neighbor
					lowestDanger = danger

					resultInTerritory = isInTerritory
					resultInCity = isInCity
					resultInCover = isInCover
					resultHasZeroDangerMove = isZeroDanger

			if  bestPlot is not None:
				# Move to the lowest danger value found
				currentUnit.pushMission(UnitMission(UnitMissionType.moveTo, target=bestPlot), simulation=simulation)  # FIXME:, .ignoreDanger
				currentUnit.finishMoves()
				self.unitProcessed(currentUnit)

				logging.debug(f"Moving {currentUnit} to safety, {bestPlot}")

		return

	def plotAircraftMoves(self, simulation):
		"""Send units to cities near the front (or carriers)"""
		self.clearCurrentMoveUnits()

		# Loop through all recruited units
		for unit in self.currentTurnUnits:
			if unit.domain == UnitDomainType.air and unit.damage() < 50:
				self.currentMoveUnits.append(HomelandUnit(unit))

		if len(self.currentMoveUnits) > 0:
			self.executeAircraftMoves(simulation)

		return

	def eliminateAdjacentSentryPoints(self):
		"""Don't allow adjacent tiles to both be sentry points"""
		self.targetedSentryPoints.sort()

		# Create temporary copy of list
		sys.setrecursionlimit(2000)
		tempPoints = [pt.copy() for pt in self.targetedSentryPoints]

		# Clear out main list
		self.targetedSentryPoints = []

		# Loop through all points in copy
		for it in tempPoints:
			foundAdjacent: bool = False

			# Is it adjacent to a point in the main list?
			for it2 in self.targetedSentryPoints:
				if it.target.distance(it2.target) == 1:
					foundAdjacent = True
					break

			if not foundAdjacent:
				self.targetedSentryPoints.append(it)

		return

	def eliminateAdjacentHomelandRoads(self):
		"""Don't allow adjacent tiles to both be mobile reserve muster points"""
		# Create temporary copy of list
		self.targetedSentryPoints.sort()

		# Create temporary copy of list
		tempPoints = [pt.copy() for pt in self.targetedHomelandRoads]

		# Clear out main list
		self.targetedHomelandRoads = []

		# Loop through all points in copy
		for it in tempPoints:
			foundAdjacent: bool = False

			# Is it adjacent to a point in the main list?
			for it2 in self.targetedHomelandRoads:
				if it.target.distance(it2.target) == 1:
					foundAdjacent = True
					break

			if not foundAdjacent:
				self.targetedHomelandRoads.append(it)

		return

	def executeAircraftMoves(self, simulation):
		raise Exception('not implemented')

	def findPatrolTarget(self, unit, simulation) -> Optional[HexPoint]:
		"""See if there is an adjacent plot we can wander to"""
		bestValue: int = 0
		bestPlot: Optional[HexPoint] = None
		unitPlayer = unit.player

		for adjacentPoint in unit.location.neighbors():

			if simulation.tileAt(adjacentPoint) is None:
				continue

			if unit.canMoveInto(adjacentPoint, options=[], simulation=simulation):
				if not simulation.isEnemyVisibleAt(adjacentPoint, self.player):
					if unit.pathTowards(adjacentPoint, options=[], simulation=simulation) is not None:
						value = (1 + random.randint(0, 10000))

						# Prefer wandering in our own territory
						if unitPlayer == unit.player:
							value += 10000

						logging.debug(f"Adjacent Patrol Plot Score, {value}, {adjacentPoint}")

						if value > bestValue:
							bestValue = value
							bestPlot = adjacentPoint
					else:
						logging.debug(f"Adjacent Patrol Plot !GeneratePath(), {adjacentPoint}")
				else:
					logging.debug(f"Adjacent Patrol Plot !isVisibleEnemyUnit(), {adjacentPoint}")
			else:
				logging.debug(f"Adjacent Patrol Plot not valid, {adjacentPoint}")

		if bestPlot is not None:
			logging.debug(f"Patrol Target FOUND, {bestValue}, {bestPlot}")
			# CvAssert(!pUnit->atPlot(*pBestPlot));
			return bestPlot
		else:
			logging.debug("Patrol Target NOT FOUND")

		return None

	def executePatrolMoves(self, simulation):
		"""Patrol with chosen units"""
		for currentMoveUnit in self.currentMoveUnits:
			unit = currentMoveUnit.unit

			if unit is None:
				continue

			target = currentMoveUnit.target

			if target is None:
				continue

			unit.pushMission(UnitMission(UnitMissionType.moveTo, target=target), simulation)
			unit.finishMoves()

			self.unitProcessed(unit)

		return

	def bestUnitToReachTarget(self, target, maxTurns: int, simulation) -> bool:
		"""Compute the best unit to reach a target in the current normal and high priority move list"""
		# Normal priority units
		for currentMoveUnit in self.currentMoveUnits:
			loopUnit = currentMoveUnit.unit

			if loopUnit is None:
				continue

			# Make sure domain matches
			if loopUnit.domain() == UnitDomainType.sea and not target.terrain().isWater() or \
				loopUnit.domain() == UnitDomainType.land and target.terrain().isWater():

				currentMoveUnit.movesToTarget = sys.maxsize
				continue

			# Make sure we can move into the destination. The pathfinder will do a similar check near the beginning, but it is best to get this out of the way before then
			if not loopUnit.canMoveInto(target.point, options = [], simulation=simulation):
				currentMoveUnit.movesToTarget = sys.maxsize
				continue

			plotDistance = loopUnit.location.distance(target.point)
			currentMoveUnit.movesToTarget = plotDistance

		# High priority units
		for currentMoveHighPriorityUnit in self.currentMoveHighPriorityUnits:
			loopUnit = currentMoveHighPriorityUnit.unit

			if loopUnit is None:
				continue

			# Make sure domain matches
			if loopUnit.domain() == UnitDomainType.sea and not target.terrain().isWater() or \
				loopUnit.domain() == UnitDomainType.land and target.terrain().isWater():
				currentMoveHighPriorityUnit.movesToTarget = sys.maxsize
				continue

			# Make sure we can move into the destination. The pathfinder will do a similar check near the beginning, but it is best to get this out of the way before then
			if not loopUnit.canMoveInto(target.point, options=[], simulation=simulation):
				currentMoveHighPriorityUnit.movesToTarget = sys.maxsize
				continue

			plotDistance = loopUnit.location.distance(target.point)
			currentMoveHighPriorityUnit.movesToTarget = plotDistance

		# Sort by raw distance
		self.currentMoveUnits.sort(key=lambda a: a.movesToTarget)
		self.currentMoveHighPriorityUnits.sort(key=lambda a: a.movesToTarget)

		# Find the one with the best true moves distance
		(self.currentBestMoveUnit, _) = self.closestUnitByTurnsToTarget(
			moveUnits=self.currentMoveUnits,
			target=target,
			maxTurns=maxTurns,
			simulation=simulation
		)
		(self.currentBestMoveHighPriorityUnit, _) = self.closestUnitByTurnsToTarget(
			moveUnits=self.currentMoveHighPriorityUnits,
			target=target,
			maxTurns=maxTurns,
			simulation=simulation
		)

		return self.currentBestMoveHighPriorityUnit is not None or self.currentBestMoveUnit is not None

	def closestUnitByTurnsToTarget(self, moveUnits: [HomelandUnit], target, maxTurns: int, simulation) -> (Optional[Unit], int):
		"""Get the closest"""
		minTurns: int = sys.maxsize
		bestUnit: Optional[Unit] = None
		failedPaths: int = 0

		# If we see this many failed pathing attempts, we assume no unit can get to the target
		kMaxFailedPaths = 2

		# If the last failed pathing attempt was this far (raw distance) from the target, we assume no one can
		# reach the target, even if we have not reached MAX_FAILED_PATHS
		kEarlyOutFailedPathDistance = 12

		# Now go through and figure out the actual number of turns, and as a result, even if it can get there at all.
		# We will try and do as few as possible by stopping if we find a unit that can make it in one turn.
		for moveUnit in moveUnits:
			loopUnit = moveUnit.unit

			if loopUnit is None:
				continue

			# Raw distance
			distance = moveUnit.movesToTarget
			if distance is None:
				continue

			if distance == sys.maxsize:
				continue

			moves = loopUnit.turnsToReach(target.point, simulation)
			moveUnit.movesToTarget = moves

			# Did we make it at all?
			if moves != sys.maxsize:
				# Reasonably close?
				if distance == 0 or (moves <= distance and moves <= maxTurns and moves < minTurns):
					bestUnit = loopUnit
					minTurns = moves
					break

				if moves < minTurns:
					bestUnit = loopUnit
					minTurns = moves

				# Were we far away? If so, this is probably the best we are going to do
				if distance >= 8:  # AI_HOMELAND_ESTIMATE_TURNS_DISTANCE
					break
			else:
				failedPaths += 1
				if failedPaths >= kMaxFailedPaths:
					break

				if distance >= kEarlyOutFailedPathDistance:
					break

		return bestUnit, minTurns

	def executeMoveToTarget(self, target, garrisonIfPossible, simulation):
		"""Find one unit to move to target, starting with high priority list"""
		# Do we have a pre-calculated 'best' unit?
		bestUnit: Optional[Unit] = None

		if self.currentBestMoveHighPriorityUnit is not None:
			# Don't move high priority unit if regular priority unit is closer
			if self.currentBestMoveUnit is not None and self.currentBestMoveUnitTurns < self.currentBestMoveHighPriorityUnitTurns:
				bestUnit = self.currentBestMoveUnit
			else:
				bestUnit = self.currentBestMoveHighPriorityUnit
		else:
			bestUnit = self.currentBestMoveUnit

		if bestUnit is not None:
			if bestUnit.location == target.point and bestUnit.canFortifyAt(bestUnit.location, simulation):
				bestUnit.pushMission(UnitMission(UnitMissionType.fortify), simulation)
				bestUnit.doFortify(simulation)
				self.unitProcessed(bestUnit)
				return
			elif garrisonIfPossible and bestUnit.location == target.point and bestUnit.canGarrisonAt(target.point, simulation):
				bestUnit.pushMission(UnitMission(UnitMissionType.garrison), simulation)
				bestUnit.finishMoves()
				self.unitProcessed(bestUnit)
				return
			else:
				# Best units have already had a full path check to the target, so just add the move
				bestUnit.pushMission(UnitMission(UnitMissionType.moveTo, target=target.point), simulation)
				bestUnit.finishMoves()
				self.unitProcessed(bestUnit)
				return

		# Start with high priority list
		for currentMoveHighPriorityUnit in self.currentMoveHighPriorityUnits:
			loopUnit = currentMoveHighPriorityUnit.unit

			if loopUnit is None:
				continue

			# Don't move high priority unit if regular priority unit is closer
			firstCurrentMoveUnit = firstOrNone(self.currentMoveUnits)
			if firstCurrentMoveUnit is not None:
				if firstCurrentMoveUnit.movesToTarget < currentMoveHighPriorityUnit.movesToTarget:
					break

			if loopUnit.location == target.point and loopUnit.canFortifyAt(loopUnit.location, simulation):
				loopUnit.pushMission(UnitMission(UnitMissionType.fortify), simulation)
				loopUnit.doFortify(simulation)
				self.unitProcessed(loopUnit)
				return
			elif garrisonIfPossible and loopUnit.location == target.point and loopUnit.canGarrisonAt(target.point, simulation):
				loopUnit.pushMission(UnitMission(UnitMissionType.garrison), simulation)
				loopUnit.finishMoves()
				self.unitProcessed(loopUnit)
				return
			elif currentMoveHighPriorityUnit.movesToTarget < 8 or \
				loopUnit.turnsToReach(target.point, simulation) != sys.maxsize:  # AI_HOMELAND_ESTIMATE_TURNS_DISTANCE

				loopUnit.pushMission(UnitMission(UnitMissionType.moveTo, target=target.point), simulation)
				loopUnit.finishMoves()
				self.unitProcessed(loopUnit)
				return

		# Then regular priority
		for currentMoveUnit in self.currentMoveUnits:
			loopUnit = currentMoveUnit.unit

			if loopUnit is None:
				continue

			if loopUnit.location == target.point and loopUnit.canFortifyAt(loopUnit.location, simulation):
				loopUnit.pushMission(UnitMission(UnitMissionType.fortify), simulation)
				loopUnit.doFortify(simulation)
				self.unitProcessed(loopUnit)
				return
			elif currentMoveUnit.movesToTarget < 8 or \
				loopUnit.turnsToReach(target.point, simulation) != sys.maxsize:  # AI_HOMELAND_ESTIMATE_TURNS_DISTANCE

				loopUnit.pushMission(UnitMission(UnitMissionType.moveTo, target=target.point), simulation)
				loopUnit.finishMoves()
				self.unitProcessed(loopUnit)
				return

		return

	def executeHeals(self, simulation):
		"""Heal chosen units"""
		for currentMoveUnit in self.currentMoveUnits:
			unit = currentMoveUnit.unit
			if unit is None:
				continue

			if unit.canFortifyAt(unit.location, simulation):
				unit.pushMission(UnitMission(UnitMissionType.fortify), simulation)
				unit.setFortifiedThisTurn(True, simulation)
			else:
				unit.pushMission(UnitMission(UnitMissionType.skip), simulation)

			self.unitProcessed(unit)

		return
