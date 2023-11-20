import logging
import math
import random
import sys
from typing import Optional, Union

from smarthexboard.smarthexboardlib.core.base import ExtendedEnum, WeightedBaseList
from smarthexboard.smarthexboardlib.game.ai.baseTypes import MilitaryStrategyType
from smarthexboard.smarthexboardlib.game.ai.builderTasking import BuilderTaskingAI
from smarthexboard.smarthexboardlib.game.ai.cities import CitySpecializationType, WonderProductionAI, CityStrategyType, BuildableType
from smarthexboard.smarthexboardlib.game.ai.deals import DealAI
from smarthexboard.smarthexboardlib.game.ai.economicStrategies import EconomicStrategyType
from smarthexboard.smarthexboardlib.game.ai.economics import EconomicAI
from smarthexboard.smarthexboardlib.game.ai.grandStrategies import GrandStrategyAI, GrandStrategyAIType
from smarthexboard.smarthexboardlib.game.ai.homeland import HomelandAI
from smarthexboard.smarthexboardlib.game.ai.leagues import LeagueAI
from smarthexboard.smarthexboardlib.game.ai.militaries import MilitaryAI
from smarthexboard.smarthexboardlib.game.ai.tactics import TacticalAI
from smarthexboard.smarthexboardlib.game.ai.traits import PlayerTraits
from smarthexboard.smarthexboardlib.game.baseTypes import GameState, ReplayEventType
from smarthexboard.smarthexboardlib.game.buildings import BuildingType
from smarthexboard.smarthexboardlib.game.cities import City, CityStateType, YieldValues, CityDistrictItem, CityWonderItem
from smarthexboard.smarthexboardlib.game.cityConnections import CityConnections
from smarthexboard.smarthexboardlib.game.cityStates import CityStateQuestType, CityStateQuest, CityStateCategory
from smarthexboard.smarthexboardlib.game.civilizations import LeaderType, CivilizationType, CivilizationAbility
from smarthexboard.smarthexboardlib.game.districts import DistrictType
from smarthexboard.smarthexboardlib.game.envoys import EnvoyEffectLevel
from smarthexboard.smarthexboardlib.game.flavors import Flavors, FlavorType
from smarthexboard.smarthexboardlib.game.governments import PlayerGovernment, GovernmentType
from smarthexboard.smarthexboardlib.game.governors import GovernorType, GovernorTitleType, Governor
from smarthexboard.smarthexboardlib.game.greatPersons import GreatPersonType, GreatPerson, GreatPersonPoints
from smarthexboard.smarthexboardlib.game.loyalties import LoyaltyState
from smarthexboard.smarthexboardlib.game.moments import MomentType
from smarthexboard.smarthexboardlib.game.notifications import Notifications, NotificationType
from smarthexboard.smarthexboardlib.game.operations import Operation, FoundCityOperation, CityCloseDefenseOperation, BasicCityAttackOperation, \
	PillageEnemyOperation, RapidResponseOperation, DestroyBarbarianCampOperation, NavalAttackOperation, \
	NavalSuperiorityOperation, NavalBombardmentOperation, NavalEscortedOperation, QuickColonizeOperation, \
	PureNavalCityAttackOperation, SmallCityAttackOperation, QuickSneakCityAttackOperation, SneakCityAttackOperation, \
	Army, NavalSneakAttackOperation, OperationMoveType
from smarthexboard.smarthexboardlib.game.playerMechanics import PlayerTechs, PlayerCivics, DiplomaticAI, \
	DiplomacyRequests, PlayerMoments, ReligionAI, MajorPlayerApproachType, MinorPlayerApproachType, PlayerProximityType
from smarthexboard.smarthexboardlib.game.playerTypes import MinorPlayerPersonalityType, InfluenceLevelType
from smarthexboard.smarthexboardlib.game.policyCards import PolicyCardType
from smarthexboard.smarthexboardlib.game.projects import ProjectType
from smarthexboard.smarthexboardlib.game.religions import PantheonType, ReligionType, FaithPurchaseType, PantheonFoundingType, BeliefType, \
	BeliefCategory
from smarthexboard.smarthexboardlib.game.states.ages import AgeType, AgeThresholds
from smarthexboard.smarthexboardlib.game.states.builds import BuildType
from smarthexboard.smarthexboardlib.game.states.dedications import DedicationType
from smarthexboard.smarthexboardlib.game.states.gossips import GossipType
from smarthexboard.smarthexboardlib.game.states.ui import ScreenType, PopupType, TooltipType
from smarthexboard.smarthexboardlib.game.states.victories import VictoryType
from smarthexboard.smarthexboardlib.game.tradeRoutes import TradeRoutes, TradeRoute, TradeRoutePathfinderDataSource
from smarthexboard.smarthexboardlib.game.types import EraType, TechType, CivicType
from smarthexboard.smarthexboardlib.game.unitTypes import UnitMissionType, UnitTaskType, UnitType, UnitOperationType
from smarthexboard.smarthexboardlib.game.units import Unit
from smarthexboard.smarthexboardlib.game.wonders import WonderType
from smarthexboard.smarthexboardlib.map import constants
from smarthexboard.smarthexboardlib.map.base import HexPoint, HexArea, Array2D
from smarthexboard.smarthexboardlib.map.constants import invalidHexPoint
from smarthexboard.smarthexboardlib.map.improvements import ImprovementType
from smarthexboard.smarthexboardlib.map.path_finding.finder import AStarPathfinder
from smarthexboard.smarthexboardlib.map.path_finding.path import HexPath
from smarthexboard.smarthexboardlib.map.types import Tutorials, Yields, TerrainType, FeatureType, UnitMovementType, RouteType, UnitDomainType, MapSize, \
	ResourceType, YieldType, YieldList, ResourceUsage
from smarthexboard.smarthexboardlib.utils.base import firstOrNone, lastOrNone, dictToArray
from smarthexboard.smarthexboardlib.utils.plugin import Tests


class Player:
	pass


class PlayerTradeRoutes:
	def __init__(self, player):
		self.player = player
		self._routes: [TradeRoute] = []

	def __iter__(self):
		return self._routes.__iter__()

	def tradeRoutesStartingAt(self, city) -> [TradeRoute]:
		cityLocation = city.location
		return list(filter(lambda route: route.start == cityLocation, self._routes))

	def numberOfTradeRoutesAt(self, location: HexPoint) -> int:
		result: int = 0

		for route in self._routes:
			path: HexPath = route.path()
			if location in path.points():
				result += 1

		return result

	def numberOfTradeRoutes(self) -> int:
		return len(self._routes)

	def yields(self, simulation) -> Yields:
		yields: Yields = Yields(food=0.0, production=0.0, gold=0.0)

		for route in self._routes:
			yields += route.yields(simulation)

		return yields

	def establishTradeRoute(self, originCity, targetCity, trader, simulation):
		originCityLocation: HexPoint = originCity.location
		targetCityLocation: HexPoint = targetCity.location

		tradeRouteFinderDataSource = TradeRoutePathfinderDataSource(
			self.player,
			originCityLocation,
			targetCityLocation,
			simulation
		)
		tradeRouteFinder = AStarPathfinder(tradeRouteFinderDataSource)

		tradeRoutePath = tradeRouteFinder.shortestPath(originCityLocation, targetCityLocation)
		if tradeRoutePath is not None:
			# tradeRoutePath.prepend(originCityLocation, 0) - not needed anymore?

			if tradeRoutePath.points()[-1] != targetCityLocation:
				tradeRoutePath.append(targetCityLocation, 0)

			tradeRoute = TradeRoute(tradeRoutePath)
			trader.start(tradeRoute, simulation)
			self._routes.append(tradeRoute)
			return True

		return False

	def finishTradeRoute(self, tradeRoute):
		self._routes = list(filter(lambda tr: tr.start != tradeRoute.start and tr.end != tradeRoute.end, self._routes))
		return

	def clearTradeRoutesAt(self, location: HexPoint):
		self._routes = list(filter(lambda tr: tr.start != location, self._routes))
		return

	def hasTradeRouteWith(self, otherPlayer, simulation):
		for route in self._routes:
			startCity = route.startCity(simulation)
			if startCity is None:
				continue

			endCity = route.endCity(simulation)
			if endCity is None:
				continue

			if otherPlayer == startCity.player or otherPlayer == endCity.player:
				return True

		return False

	def allTradeValueFromPlayer(self, otherPlayer, yieldType: YieldType, simulation) -> int:
		total: int = 0
		for route in self._routes:
			startPlayer = route.startPlayer(simulation)
			endPlayer = route.endPlayer(simulation)

			if (startPlayer == self.player and endPlayer == otherPlayer) or \
				(startPlayer == otherPlayer and endPlayer == self.player):
				yields: Yields = route.yields(simulation)

				total += yields.value(yieldType)

		return total

	def canEstablishTradeRouteFrom(self, originCity, targetCity, simulation) -> bool:
		originCityLocation = originCity.location
		targetCityLocation = targetCity.location

		tradeRouteFinderDataSource = TradeRoutePathfinderDataSource(
			player=self.player,
			startLocation=originCityLocation,
			targetLocation=targetCityLocation,
			simulation=simulation
		)
		tradeRouteFinder = AStarPathfinder(tradeRouteFinderDataSource)

		if tradeRouteFinder.shortestPath(originCityLocation, targetCityLocation) is not None:
			return True

		return False

	def hasTradeRouteFrom(self, fromPoint: HexPoint, toPoint: HexPoint) -> bool:
		return len(list(filter(lambda r: r.start == fromPoint and r.end == toPoint, self._routes))) > 0


class PlayerGreatPeople:
	def __init__(self, player):
		self.player = player

		self._points = GreatPersonPoints()
		self._retiredGreatPersons = []
		self._spawned = dict()

		for greatPerson in list(GreatPersonType):
			self._spawned[greatPerson] = 0

	def hasRetired(self, greatPerson: GreatPerson) -> bool:
		return greatPerson in self._retiredGreatPersons

	def numberOfSpawnedGreatPersons(self) -> int:
		return len(self._spawned)

	def addPoints(self, points: GreatPersonPoints):
		self._points += points

	def valueFor(self, greatPersonType: GreatPersonType) -> int:
		return self._points.value(greatPersonType)


class PlayerTreasury:
	def __init__(self, player):
		self.player = player

		# internal
		self._gold = 0.0
		self._goldChangeForTurn = []

	def value(self) -> float:
		return self._gold

	def changeGoldBy(self, amount: float):
		self._gold += amount

	def doTurn(self, simulation):
		goldChange = self.calculateGrossGold(simulation)

		self._goldChangeForTurn.append(goldChange)

		# predict treasury
		goldAfterThisTurn = self._gold + goldChange

		# check if we are running low
		if goldAfterThisTurn < 0:
			self._gold = 0

			if goldAfterThisTurn <= -5:  # DEFICIT_UNIT_DISBANDING_THRESHOLD
				# player.doDeficit()
				pass
		else:
			self.changeGoldBy(goldChange)

	def averageIncome(self, numberOfTurns: int) -> float:
		"""Average change in gold balance over N turns"""
		if numberOfTurns <= 0:
			raise Exception(f'Number of turn to check must be positive and not {numberOfTurns}')

		if len(self._goldChangeForTurn) == 0:
			return 0.0

		numberOfElements = min(numberOfTurns, len(self._goldChangeForTurn))
		total = sum(self._goldChangeForTurn[-numberOfElements:])

		return float(total) / float(numberOfElements)

	def calculateGrossGold(self, simulation):
		netGold = 0.0

		# Income
		# //////////////////

		# Gold from Cities
		netGold += self.goldFromCities(simulation)

		# Gold per Turn from Diplomacy
		netGold += self.goldPerTurnFromDiplomacy(simulation)

		# City connection bonuses
		netGold += self.goldFromTradeRoutes(simulation)

		# Costs
		# //////////////////

		# Gold for Unit Maintenance
		netGold -= self.goldForUnitMaintenance(simulation)

		# Gold for Building Maintenance
		netGold -= self.goldForBuildingMaintenance(simulation)

		# Gold per Turn for Diplomacy
		netGold += self.goldPerTurnForDiplomacy(simulation)

		return netGold

	def goldFromCities(self, simulation) -> float:
		"""Gold from Cities"""
		goldValue = 0.0

		for city in simulation.citiesOf(self.player):
			goldValue += city.goldPerTurn(simulation)

		return goldValue

	def goldPerTurnFromDiplomacy(self, simulation) -> float:
		return 0.0

	def goldFromTradeRoutes(self, simulation) -> float:
		return self.player.tradeRoutes.yields(simulation).gold

	def goldForUnitMaintenance(self, simulation) -> float:
		maintenanceCost = 0.0

		for unit in simulation.unitsOf(self.player):
			unitMaintenanceCost: float = float(unit.unitType.maintenanceCost())

			# conscription - Unit maintenance reduced by 1 Gold per turn, per unit.
			if self.player.government.hasCard(PolicyCardType.conscription):
				unitMaintenanceCost = max(0.0, unitMaintenanceCost - 1.0)

			# leveeEnMasse - Unit maintenance cost reduced by 2 Gold per unit.
			if self.player.government.hasCard(PolicyCardType.leveeEnMasse):
				unitMaintenanceCost = max(0.0, unitMaintenanceCost - 2.0)

			# eliteForces - +100 % combat experience for all units.
			# BUT: +2 Gold to maintain each military unit.
			if unit.unitType.maintenanceCost() > 0 and self.player.government.hasCard(PolicyCardType.eliteForces):
				unitMaintenanceCost += 2.0

			maintenanceCost += unitMaintenanceCost

		return maintenanceCost

	def goldForBuildingMaintenance(self, simulation) -> float:
		maintenanceCost = 0.0

		for city in simulation.citiesOf(self.player):
			maintenanceCost += city.maintenanceCostsPerTurn()

		return maintenanceCost

	def goldPerTurnForDiplomacy(self, simulation) -> float:
		return 0.0


class PlayerReligion:
	def __init__(self, player):
		self.player = player

		self._faithVal = 0.0
		self._pantheon: PantheonType = PantheonType.none
		self._religionFounded = ReligionType.none
		self._founderBeliefVal = BeliefType.none
		self._followerBeliefVal = BeliefType.none
		self._worshipBeliefVal = BeliefType.none
		self._enhancerBeliefVal = BeliefType.none
		self._majorityPlayerReligion = ReligionType.none
		self._holyCityLocationVal = constants.invalidHexPoint

	def pantheon(self) -> PantheonType:
		return self._pantheon

	def canFoundPantheon(self, checkFaithTotal: bool, simulation) -> PantheonFoundingType:
		faith = self.faith()

		if self.hasCreatedPantheon() or self.hasCreatedReligion():
			return PantheonFoundingType.alreadyCreatedPantheon

		if checkFaithTotal and faith < self.minimumFaithNextPantheon():
			return PantheonFoundingType.notEnoughFaith

		if len(simulation.availablePantheons()) == 0:
			return PantheonFoundingType.noPantheonAvailable

		return PantheonFoundingType.okay

	def hasCreatedPantheon(self) -> bool:
		return self._pantheon != PantheonType.none

	def foundPantheon(self, pantheon: PantheonType, simulation):
		if not self.canFoundPantheon(True, simulation):
			raise Exception('Cannot')

		# moments
		numPantheonsFounded: int = simulation.numberOfPantheonsFounded()
		if numPantheonsFounded == 0:
			self.player.addMoment(MomentType.worldsFirstPantheon, simulation=simulation)
		else:
			self.player.addMoment(MomentType.pantheonFounded, pantheon=pantheon, simulation=simulation)

		if not self.player.civics.inspirationTriggeredFor(CivicType.mysticism):
			self.player.civics.triggerInspirationFor(CivicType.mysticism, simulation)

		if pantheon == PantheonType.fertilityRites:
			# When chosen receive a Builder in your capital.
			capital = self.player.capitalCity(simulation)
			if capital is not None:
				builder = Unit(capital.location, UnitType.builder, self.player)
				simulation.addUnit(builder)
				simulation.userInterface.showUnit(builder, capital.location)

		if pantheon == PantheonType.religiousSettlements:
			# When chosen receive a Settler in your capital.
			capital = self.player.capitalCity(simulation)
			if capital is not None:
				settler = Unit(capital.location, UnitType.settler, self.player)
				simulation.addUnit(settler)
				simulation.userInterface.showUnit(settler, capital.location)

		self._pantheon = pantheon

		# inform other players, that a pantheon was founded
		simulation.sendGossip(GossipType.pantheonCreated, pantheonName=pantheon.name(), player=self.player)

	def faith(self) -> float:
		return self._faithVal

	def changeFaith(self, faith: float):
		self._faithVal += faith

	def religionInMostCities(self) -> ReligionType:
		return self._majorityPlayerReligion

	def currentReligion(self) -> ReligionType:
		return self._religionFounded

	def foundReligion(self, religion: ReligionType, location: HexPoint, followerBelief: BeliefType, otherBelief: BeliefType, simulation):
		# fixme: do the checks
		# can religion be founded? number and has nobody else already used it
		# numReligionsFounded: Int = simulation.religions()
		#             .count(where: { $0?.currentReligion() != ReligionType.none })
		# if numReligionsFounded == 0:
		#             self.player?.addMoment(of: .worldsFirstReligion, in: gameModel)

		# find city of location and make the holy city
		holyCity = None
		for city in simulation.citiesOf(self.player):
			if location in city.cityCitizens.workingTileLocations():
				holyCity = city

		if holyCity is None:
			raise Exception(f'Cannot found a religion in foreign city - tile did not belong to any player city')

		self._holyCityLocationVal = holyCity.location
		holyCity.cityReligion.doReligionFounded(religion)

		self._religionFounded = religion

		if followerBelief.category() != BeliefCategory.follower:
			raise Exception(f'wrong category of follower belief: {followerBelief.category()}')

		self._followerBeliefVal = followerBelief

		if otherBelief.category() == BeliefCategory.follower:
			raise Exception(f'wrong category of second belief: {followerBelief.category()}')
		elif otherBelief.category() == BeliefCategory.founder:
			self._founderBeliefVal = otherBelief
		elif otherBelief.category() == BeliefCategory.enhancer:
			self._enhancerBeliefVal = otherBelief
		elif otherBelief.category() == BeliefCategory.worship:
			self._worshipBeliefVal = otherBelief

		# Update game systems
		# kPlayer.UpdateReligion();
		# kPlayer.GetReligions()->SetFoundingReligion(false);

		# In case we have another prophet sitting around, make sure he's set to this religion
		# 	int iLoopUnit;
		# 	CvUnit* pLoopUnit;
		# 	for(pLoopUnit = kPlayer.firstUnit(&iLoopUnit); pLoopUnit != NULL; pLoopUnit = kPlayer.nextUnit(&iLoopUnit))
		# 	{
		# 		if(pLoopUnit->getUnitInfo().IsFoundReligion())
		# 		{
		# 			pLoopUnit->GetReligionData()->SetReligion(eReligion);
		# 			pLoopUnit->GetReligionData()->SetSpreadsLeft(pLoopUnit->getUnitInfo().GetReligionSpreads());
		# 			pLoopUnit->GetReligionData()->SetReligiousStrength(pLoopUnit->getUnitInfo().GetReligiousStrength());
		# 		}
		# 	}

		simulation.addReplayEvent(ReplayEventType.religionFounded, "TXT_KEY_NOTIFICATION_RELIGION_FOUNDED", location)

		for loopPlayer in simulation.players:
			if loopPlayer == self.player:
				# Message slightly different for founder player
				loopPlayer.notifications.addNotification(NotificationType.religionFoundedActivePlayer, religion=religion)
			elif self.player.hasMetWith(loopPlayer):
				loopPlayer.notifications.addNotification(NotificationType.religionFoundedActivePlayer, religion=religion)

		logging.debug(f'{self.player} founded religion {religion} in {holyCity.name()}')

		return

	def isEnhanced(self) -> bool:
		return self._worshipBeliefVal != BeliefType.none or self._enhancerBeliefVal != BeliefType.none

	def canAffordFaithPurchase(self, faith: int, simulation) -> bool:
		"""Does this player have enough faith to buy a religious unit or building?"""
		capital = simulation.capitalOf(self.player)
		if capital is not None:
			for unitType in list(UnitType):
				if self.player.canPurchaseUnitInAnyCity(unitType, YieldType.faith, simulation):
					cost = capital.faithPurchaseCostOf(unitType, simulation)

					if 0 < cost < faith:
						return True

			for buildingType in list(BuildingType):
				if self.player.canPurchaseBuildingInAnyCity(buildingType, YieldType.faith, simulation):
					cost = capital.faithPurchaseCostOf(buildingType)

					if 0 < cost < faith:
						return True

			return False

	def hasCreatedReligion(self):
		return self._religionFounded != ReligionType.none

	def minimumFaithNextPantheon(self) -> float:
		return 25.0  # RELIGION_MIN_FAITH_FIRST_PANTHEON

	def greatPersonExpendedFaith(self) -> int:
		value = 0

		value += self._founderBeliefVal.greatPersonExpendedFaith()
		value += self._followerBeliefVal.greatPersonExpendedFaith()
		value += self._worshipBeliefVal.greatPersonExpendedFaith()
		value += self._enhancerBeliefVal.greatPersonExpendedFaith()

		return value


class PlayerTourism:
	def __init__(self, player):
		self.player = player

		self.lifetimeCultureValue = 0.0
		self.lifetimeTourismValue = {}

	def doTurn(self, simulation):
		turnCulture = self.player.culture(simulation, consume=False)
		self.lifetimeCultureValue += turnCulture

		for loopPlayer in simulation.players:
			if loopPlayer.isBarbarian() or self.player == loopPlayer:
				continue

			loopPlayerTourism: int = int(loopPlayer.currentTourism(simulation))

			tourismModifier = loopPlayer.tourismModifierTowards(self.player, simulation)

			loopPlayerTourism *= tourismModifier
			loopPlayerTourism /= 100

			self.lifetimeTourismValue[loopPlayer.leader] = (self.lifetimeTourismValue.get(loopPlayer.leader, 0.0) + float(loopPlayerTourism))

		return

	def lifetimeCulture(self) -> float:
		return self.lifetimeCultureValue

	def lifetimeTourism(self) -> float:
		tmpLifetimeTourism: float = 0.0

		for key, value in self.lifetimeTourismValue.items():
			tmpLifetimeTourism += value

		return tmpLifetimeTourism

	def visitingTourists(self, simulation) -> int:
		tourists: int = 0

		for loopPlayer in simulation.players:
			if loopPlayer.isBarbarian() or self.player == loopPlayer:
				continue

			tourists += self.visitingTouristsFrom(loopPlayer, simulation)

		return tourists

	def domesticTourists(self) -> int:
		civics = self.player.civics

		# eurekas
		eurekaValue: float = 0.0

		for civic in list(CivicType):
			# dont hav civic but eureka enabled
			if not civics.hasCivic(civic) and civics.inspirationTriggeredFor(civic):
				eurekaValue += float(civic.cost()) / 2.0

		return int((self.lifetimeCultureValue + eurekaValue) / 100.0)

	def visitingTouristsFrom(self, otherPlayer, simulation) -> int:
		otherLeader = otherPlayer.leader

		cumulatedTourismValue = self.lifetimeTourismValue.get(otherLeader, 0)

		divider = len(simulation.players) * 200
		return int(cumulatedTourismValue / divider)

	def currentTourism(self, simulation) -> float:
		baseTourism = self.baseTourism(simulation)
		# modifiers ?

		return baseTourism

	def baseTourism(self, simulation) -> float:
		rtnValue: float = 0.0

		for city in simulation.citiesOf(self.player):
			rtnValue += city.baseTourism(simulation)

		return rtnValue

	def influenceOn(self, otherPlayer) -> InfluenceLevelType:
		return InfluenceLevelType.unknown

	def civLowestInfluence(self, checkOpenBorders: bool, simulation):  # Player
		for loopPlayer in simulation.players:
			if loopPlayer.isBarbarian() or self.player == loopPlayer:
				continue

			# fixme - no a valid check
			if self.player.hasMetWith(loopPlayer):
				return loopPlayer

		return None


class PlayerGovernors:
	def __init__(self, player):
		self.player = player

		self.numTitlesAvailableValue = 0
		self.numTitlesSpentValue = 0
		self.lastEvaluation = 0

		self.governors = []

	def addTitle(self):
		self.numTitlesAvailableValue += 1

	def numberOfTitlesAvailable(self) -> int:
		return self.numTitlesAvailableValue

	def numberOfTitlesSpent(self) -> int:
		return self.numTitlesSpentValue

	def doTurn(self, simulation):
		if self.numTitlesAvailableValue > 0:
			logging.info("title needs to be spent => notification for human")

			if self.player.isHuman():
				self.player.notifications().addNotification(NotificationType.governorTitleAvailable)
			else:
				self.chooseBestGovernorTitleUsage(simulation)

		# check assignments or re-assignments
		if not self.player.isHuman():
			# every 20 turns
			if simulation.currentTurn - self.lastEvaluation > 20:

				# assign to city + reassign to different city
				self.reassignGovernors(simulation)

				self.lastEvaluation = simulation.currentTurn

		return

	def governor(self, governorType: GovernorType) -> Optional[Governor]:
		return next(filter(lambda g: g.governorType == governorType, self.governors), None)

	def appoint(self, governorType: GovernorType, simulation):
		if self.numTitlesAvailableValue <= 0:
			raise Exception("try to appoint a governor without available titles")

		governor = Governor(governorType)
		self.governors.append(governor)

		self.numTitlesSpentValue += 1
		self.numTitlesAvailableValue -= 1

		if len(self.governors) == len(list(GovernorType)) - 1 and not self.player.hasMoment(MomentType.allGovernorsAppointed):
			self.player.addMoment(MomentType.allGovernorsAppointed, simulation=simulation)

	def promote(self, governor: Governor, title: GovernorTitleType, simulation):
		if self.numTitlesAvailableValue <= 0:
			raise Exception("try to appoint a governor without available titles")

		governor.promote(title)

		if governor.numberOfTitles() == 6 and not self.player.hasMoment(MomentType.governorFullyPromoted):
			self.player.addMoment(MomentType.governorFullyPromoted, simulation=simulation)

		self.numTitlesSpentValue += 1
		self.numTitlesAvailableValue -= 1

	def assign(self, governor: Governor, city, simulation):
		"""and remove from any previous city"""
		governor.assignedCity(simulation).assign(GovernorType.none)
		governor.unassign()

		city.assignGovernor(governor.governorType)
		governor.assignTo(city)

	def reassignGovernors(self, simulation):
		"""evaluate the best assignment and do it:
			score each governor for each city
			start assigning the best value
		"""
		cityLocations: [HexPoint] = list(map(lambda c: c.location, simulation.citiesOf(self.player)))
		reassigned: bool = False

		logging.debug(f'Try to distribute {len(self.governors)} governors to {len(cityLocations)} cities')

		for governor in self.governors:

			bestLocation: HexPoint = constants.invalidHexPoint
			bestValue: float = -10000000000000.0

			for cityLocation in cityLocations:
				city = simulation.cityAt(cityLocation)
				if city is None:
					continue

				value = city.valueOfGovernor(governor.governorType(), simulation)

				if value > bestValue:
					bestValue = value
					bestLocation = cityLocation

			if bestLocation == constants.invalidHexPoint:
				logging.warning(f"Player {self.player.name()} could not find a city location for {governor.governorType()}")
				continue

			cityLocations = list(filter(lambda c: c != bestLocation, cityLocations))

			bestCity = simulation.cityAt(bestLocation)

			if bestCity is None:
				raise Exception("cant get best city")

			governorCity = governor.assignedCity(simulation)
			if governorCity is not None and governorCity.location == bestLocation:
				logging.info(f"{self.player.leader.name()} decided to let governor {governor.governorType().name()} stay in city {bestCity.name()}")
				continue

			reassigned = True

			bestCity.assignGovernor(GovernorType.none)
			governor.unassign()

			bestCity.assignGovernor(governor.governorType())
			governor.assignTo(bestCity)

			logging.info(f"{self.player.leader.title()} assigned governor {governor.governorType().name()} to city {bestCity.name()}")

		if not reassigned:
			logging.debug(f"{self.player.leader.title()} did no reassignments of governors")

		return

	def chooseBestGovernorTitleUsage(self, simulation):
		"""AI function"""
		numberOfCities = len(simulation.citiesOf(self.player))
		numberOfActiveGovernors = self.numActiveGovernors(simulation)

		# appoint new or promote existing governors
		if 0 < numberOfActiveGovernors and (
			numberOfCities <= numberOfActiveGovernors or numberOfActiveGovernors >= len(list(GovernorType))):
			# promote
			self._promoteGovernor()
		else:
			# appoint
			self._appointGovernor(simulation)

		return

	def numActiveGovernors(self, simulation) -> int:
		numActiveGovernors: int = 0

		for city in simulation.citiesOf(self.player):
			if city.governor() is not None:
				numActiveGovernors += 1

		return numActiveGovernors

	def _promoteGovernor(self):
		possiblePromotions: [GovernorTitleType] = []

		for governor in self.governors:
			possiblePromotions += governor.possiblePromotions()

		bestPromotion: Optional[GovernorTitleType] = None
		bestValue: int = -100000000

		for promotion in possiblePromotions:
			val: int = 0

			for flavorType in list(FlavorType):
				val += self.player.personalAndGrandStrategyFlavor(flavorType) * promotion.flavorValue(flavorType)

			if val > bestValue:
				bestPromotion = promotion
				bestValue = val

		if bestPromotion is not None:
			didPromote = False

			for governorType in list(GovernorType):
				if bestPromotion in governorType.titles():
					governor = next(filter(lambda g: g.governorType() == governorType, self.governors), None)

					if governor is not None:
						governor.promote(bestPromotion)
						logging.info(f"did promote {governor.governorType().name()} with {bestPromotion.name()}")
						didPromote = True

						self.numTitlesSpentValue += 1
						self.numTitlesAvailableValue -= 1

			if not didPromote:
				raise Exception("did not promote - pls fix me")
		else:
			raise Exception("cant get promotion - pls fix me")

		return

	def _appointGovernor(self, simulation):
		governorType: Optional[GovernorType] = self.chooseBestNewGovernor()
		if governorType is not None:
			# find the best city for this governor
			bestCity = self.bestCity(governorType, simulation)
			if bestCity is not None:
				governor = Governor(governorType)
				self.governors.append(governor)

				self.numTitlesSpentValue += 1
				self.numTitlesAvailableValue -= 1

				if len(self.governors) == len(list(GovernorType)) - 1 and not self.player.hasMoment(MomentType.allGovernorsAppointed):
					self.player.addMoment(MomentType.allGovernorsAppointed, simulation=simulation)

				# directly assign
				bestCity.assignGovernor(governorType)
			else:
				logging.info(f"cant get city for best governor: {governorType.name()}")
		else:
			logging.info("Cant get governor")

		return

	def chooseBestNewGovernor(self) -> Optional[GovernorType]:
		bestGovernorType: Optional[GovernorType] = None
		bestValue: int = -100000000000

		ownGovernorTypes = map(lambda g: g.governorType(), self.governors)

		for governorType in list(GovernorType):
			if governorType in ownGovernorTypes:
				continue

			val = 0

			for flavorType in list(FlavorType):
				val += self.player.personalAndGrandStrategyFlavor(flavorType) * governorType.flavorValue(flavorType)

			if val > bestValue:
				bestGovernorType = governorType
				bestValue = val

		return bestGovernorType

	def bestCity(self,  governorType: GovernorType, simulation):
		bestCity = None
		bestValue: float = -100000000000.0

		for city in simulation.citiesOf(self.player):
			value = city.valueOfGovernor(governorType, simulation)

			if value > bestValue:
				bestCity = city
				bestValue = value

		return bestCity


class ProductionSpecialization(ExtendedEnum):
	none = 'none'

	militaryTraining = 'militaryTraining'  # PRODUCTION_SPECIALIZATION_MILITARY_TRAINING
	emergencyUnits = 'emergencyUnits'  # PRODUCTION_SPECIALIZATION_EMERGENCY_UNITS
	militaryNaval = 'militaryNaval'  # PRODUCTION_SPECIALIZATION_MILITARY_NAVAL
	wonder = 'wonder'  # PRODUCTION_SPECIALIZATION_WONDER
	spaceship = 'spaceship'  # PRODUCTION_SPECIALIZATION_SPACESHIP


class ProductionSpecializationList(WeightedBaseList):
	def __init__(self):
		super().__init__()
		for productionSpecialization in list(ProductionSpecialization):
			self.addWeight(0.0, productionSpecialization)


class CitySpecializationData:
	def __init__(self, city):
		self.city = city
		self.weight = YieldList()


class CitySpecializationAI:
	def __init__(self, player):
		self.player = player

		self.lastTurnEvaluated: int = 0
		self.specializationsDirty: bool = False
		self.interruptWonders: bool = False
		self.yieldWeights = YieldList()

		self.wonderChosen: bool = False
		self.wonderCity = None
		self.specializationsNeeded: [CitySpecializationType] = []
		self.productionSubtypeWeights = ProductionSpecializationList()
		self.nextSpecializationDesired: CitySpecializationType = CitySpecializationType.none

		self.nextWonderWeight: int = 0
		self.nextWonderDesiredValue: WonderType = WonderType.none
		self.nextWonderLocationValue: HexPoint = constants.invalidHexPoint

		self.numSpecializationsForThisYield = YieldList()
		self.numSpecializationsForThisSubtype = ProductionSpecializationList()

		self.bestValue = YieldList()

	def doTurn(self, simulation):
		wonderProductionAI = self.player.wonderProductionAI

		# No city specializations for humans!
		if self.player.isHuman():
			return

		# No city specializations early in the game
		if simulation.currentTurn < 25:  # AI_CITY_SPECIALIZATION_EARLIEST_TURN
			return

		# No city specialization, if we don't have any cities
		if len(simulation.citiesOf(self.player)) < 1:
			return

		# See if need to update assignments
		# AI_CITY_SPECIALIZATION_REEVALUATION_INTERVAL
		if self.specializationsDirty or self.lastTurnEvaluated + 50 > simulation.currentTurn:
			wonderSelection = wonderProductionAI.chooseWonder(
				adjustForOtherPlayers=True,
				nextWonderWeight=self.nextWonderWeight,
				simulation=simulation
			)

			self.nextWonderDesiredValue = wonderSelection.wonder
			self.nextWonderLocationValue = wonderSelection.location
			self.nextWonderWeight = wonderSelection.totalWeights

			self.weightSpecializations(simulation)
			self.assignSpecializations(simulation)

			self.specializationsDirty = False
			self.lastTurnEvaluated = simulation.currentTurn

			# Do we need to choose production again at all our cities?
			if self.interruptWonders:
				for city in simulation.citiesOf(self.player):
					if not city.isBuildingUnitForOperation():
						city.chooseProduction(interruptWonders=True)

			# Reset this flag - - need a new high priority event before we'll interrupt again
			self.interruptWonders = False

		return

	def nextDesiredWonder(self) -> (WonderType, HexPoint, int):
		return self.nextWonderDesiredValue, self.nextWonderLocationValue, self.nextWonderWeight

	def setSpecializationsDirty(self):
		self.specializationsDirty = True

	def wonderBuildCity(self) -> Optional[City]:
		return self.wonderCity

	def weightSpecializations(self, simulation):
		"""Evaluate which specializations we need"""
		economicAI = self.player.economicAI
		diplomacyAI = self.player.diplomacyAI

		foodYieldWeight: float = 0.0
		productionYieldWeight: float = 0.0
		goldYieldWeight: float = 0.0
		scienceYieldWeight: float = 0.0
		# generalEconomicWeight: float = 0.0

		# Clear old weights
		self.yieldWeights = YieldList()
		self.productionSubtypeWeights.clear()

		# Must have a capital to do any specialization
		capital = simulation.capitalOf(self.player)
		if capital is not None:
			capitalArea = simulation.areaOf(capital.location)

			flavorExpansion = max(0.0, float(self.player.valueOfPersonalityFlavor(FlavorType.expansion)))
			flavorWonder = max(0.0, float(self.player.valueOfPersonalityFlavor(FlavorType.wonder)))
			flavorGold = max(0.0, float(self.player.valueOfPersonalityFlavor(FlavorType.gold)))
			flavorScience = max(0.0, float(self.player.valueOfPersonalityFlavor(FlavorType.science)))
			flavorSpaceship = 0.0  # player.valueOfPersonalityFlavor(of:.sp)

			# COMPUTE NEW WEIGHTS

			# Food
			tilesInCapitalArea = simulation.tilesIn(capitalArea)
			numberOfUnownedTiles = len(list(filter(lambda t: not t.hasOwner(), tilesInCapitalArea)))
			numberOfCities = len(simulation.citiesOf(self.player))
			numberOfSettlers = len(list(filter(lambda u: u.task == UnitTaskType.settle, simulation.unitsOf(self.player))))

			if economicAI.isUsingStrategy(EconomicStrategyType.earlyExpansion):
				foodYieldWeight += 500.0  # AI_CITY_SPECIALIZATION_FOOD_WEIGHT_EARLY_EXPANSION

			foodYieldWeight += flavorExpansion * 5.0  # AI_CITY_SPECIALIZATION_FOOD_WEIGHT_FLAVOR_EXPANSION
			foodYieldWeight += (float(numberOfUnownedTiles) * 100.0) / float(len(tilesInCapitalArea)) * 5.0
				# AI_CITY_SPECIALIZATION_FOOD_WEIGHT_PERCENT_CONTINENT_UNOWNED
			foodYieldWeight += float(numberOfCities) * -50.0  # AI_CITY_SPECIALIZATION_FOOD_WEIGHT_NUM_CITIES
			foodYieldWeight += float(numberOfSettlers) * -40.0  # AI_CITY_SPECIALIZATION_FOOD_WEIGHT_NUM_SETTLERS

			if numberOfCities + numberOfSettlers == 1:
				foodYieldWeight *= 3.0  # Really want to get up over 1 city

			if foodYieldWeight < 0.0:
				foodYieldWeight = 0.0

			# Production
			productionYieldWeight = float(self.weightProductionSubtypes(
				flavorWonder=int(flavorWonder),
				flavorSpaceship=int(flavorSpaceship),
				simulation=simulation
			))

			# Trade
			landDisputeLevel = diplomacyAI.totalLandDisputeLevel(simulation)
			goldYieldWeight += flavorGold * 20.0  # AI_CITY_SPECIALIZATION_GOLD_WEIGHT_FLAVOR_GOLD
			goldYieldWeight += float(landDisputeLevel) * 10.0  # AI_CITY_SPECIALIZATION_GOLD_WEIGHT_LAND_DISPUTE

			# Science
			scienceYieldWeight += flavorScience * 20.0  # AI_CITY_SPECIALIZATION_SCIENCE_WEIGHT_FLAVOR_SCIENCE
			scienceYieldWeight += flavorSpaceship * 10.0  # AI_CITY_SPECIALIZATION_SCIENCE_WEIGHT_FLAVOR_SPACESHIP

			# General Economics
			# generalEconomicWeight = 200.0  # AI_CITY_SPECIALIZATION_GENERAL_ECONOMIC_WEIGHT

			# Add in any contribution from the current grand strategy
			for grandStrategyType in list(GrandStrategyAIType):
				if self.player.grandStrategyAI.activeStrategy != grandStrategyType:
					continue

				grandStrategyTypeYield = grandStrategyType.yields()
				foodYieldWeight += grandStrategyTypeYield.food
				goldYieldWeight += grandStrategyTypeYield.gold
				scienceYieldWeight += grandStrategyTypeYield.science

			# Add weights to our weighted vector
			self.yieldWeights.setWeight(foodYieldWeight, YieldType.food)
			self.yieldWeights.setWeight(productionYieldWeight, YieldType.production)
			self.yieldWeights.setWeight(goldYieldWeight, YieldType.gold)
			self.yieldWeights.setWeight(scienceYieldWeight, YieldType.science)

		return

	def weightProductionSubtypes(self, flavorWonder: int, flavorSpaceship: int, simulation) -> int:
		"""Compute the weight of each production subtype (return value is total of all these weights)"""
		militaryAI = self.player.militaryAI

		criticalDefenseOn: bool = False

		militaryTrainingWeight: float = 0.0
		emergencyUnitWeight: float = 0.0
		seaWeight: float = 0.0
		wonderWeight: float = 0.0
		spaceshipWeight: float = 0.0

		flavorOffense = float(self.player.personalAndGrandStrategyFlavor(FlavorType.offense))
		unitsRequested = self.player.numberOfUnitsNeededToBeBuilt()

		# LONG - TERM MILITARY BUILD - UP
		militaryTrainingWeight += flavorOffense * 10.0  # AI_CITY_SPECIALIZATION_PRODUCTION_TRAINING_PER_OFFENSE
		# militaryTrainingWeight += m_pPlayer->GetDiplomacyAI()->GetPersonalityMajorCivApproachBias(MAJOR_CIV_APPROACH_WAR) * 10 / * AI_CITY_SPECIALIZATION_PRODUCTION_TRAINING_PER_PERSONALITY * /

		# EMERGENCY UNITS
		emergencyUnitWeight += float(unitsRequested) * 10.0
		# AI_CITY_SPECIALIZATION_PRODUCTION_WEIGHT_OPERATIONAL_UNITS_REQUESTED

		emergencyUnitWeight += float(militaryAI.numberOfPlayersAtWarWith(simulation)) *100.0
		# AI_CITY_SPECIALIZATION_PRODUCTION_WEIGHT_CIVS_AT_WAR_WITH * /

		# Is our capital under threat?
		capitalUnterThreatCityStrategy: CityStrategyType = CityStrategyType.capitalUnderThreat

		capital = simulation.capitalOf(self.player)
		if capital is not None:
			cityStrategy = capital.cityStrategy
			if cityStrategy.adopted(CityStrategyType.capitalUnderThreat):
				emergencyUnitWeight += 50.0  # AI_CITY_SPECIALIZATION_PRODUCTION_WEIGHT_CAPITAL_THREAT

		# Add in weights depending on what the military AI is up to
		if militaryAI.adopted(MilitaryStrategyType.warMobilization):
			militaryTrainingWeight += 150.0  # AI_CITY_SPECIALIZATION_PRODUCTION_WEIGHT_WAR_MOBILIZATION

		if militaryAI.adopted(MilitaryStrategyType.empireDefense):
			emergencyUnitWeight += 150.0  # AI_CITY_SPECIALIZATION_PRODUCTION_WEIGHT_EMPIRE_DEFENSE

		if militaryAI.adopted(MilitaryStrategyType.empireDefenseCritical):
			criticalDefenseOn = True
			emergencyUnitWeight += 1000.0  # AI_CITY_SPECIALIZATION_PRODUCTION_WEIGHT_EMPIRE_DEFENSE_CRITICAL

		# Override all this if have too many units!
		if militaryAI.adopted(MilitaryStrategyType.enoughMilitaryUnits):
			militaryTrainingWeight = 0.0
			emergencyUnitWeight = 0.0

		if militaryAI.adopted(MilitaryStrategyType.needNavalUnits):
			seaWeight += 50.0  # AI_CITY_SPECIALIZATION_PRODUCTION_WEIGHT_NEED_NAVAL_UNITS

		if militaryAI.adopted(MilitaryStrategyType.needNavalUnitsCritical):
			seaWeight += 250.0  # AI_CITY_SPECIALIZATION_PRODUCTION_WEIGHT_NEED_NAVAL_UNITS_CRITICAL

		if militaryAI.adopted(MilitaryStrategyType.enoughNavalUnits):
			seaWeight = 0.0

		# Wonder is MIN between weight of wonders available to build and value from flavors (but not less than zero)
		wonderFlavorWeight = float(flavorWonder) * 200.0  # AI_CITY_SPECIALIZATION_PRODUCTION_WEIGHT_FLAVOR_WONDER * /
		weightOfWonders = float(self.nextWonderWeight) * 0.8  # AI_CITY_SPECIALIZATION_PRODUCTION_WEIGHT_NEXT_WONDER * /
		wonderWeight = min(wonderFlavorWeight, weightOfWonders)
		wonderWeight = max(wonderWeight, 0.0)

		# One - half of normal weight if critical defense is on
		if criticalDefenseOn:
			wonderWeight /= 2.0

		# if canBuildSpaceshipParts()
		#	spaceshipWeight += iFlavorSpaceship * GC.getAI_CITY_SPECIALIZATION_PRODUCTION_WEIGHT_FLAVOR_SPACESHIP() / * 5 * /;

		for grandStrategy in list(GrandStrategyAIType):
			if self.player.grandStrategyAI.activeStrategy != grandStrategy:
				if grandStrategy.yields().value(YieldType.production) > 0.0:
					if grandStrategy.flavor(FlavorType.offense) > 0:
						militaryTrainingWeight += grandStrategy.yields().production
					# elif (grandStrategy->GetFlavorValue((FlavorTypes)GC.getInfoTypeForString("FLAVOR_SPACESHIP")) > 0)
					# spaceshipWeight += grandStrategy->GetSpecializationBoost(YIELD_PRODUCTION);

		# Add weights to our weighted vector
		self.productionSubtypeWeights.addWeight(float(militaryTrainingWeight), ProductionSpecialization.militaryTraining)
		self.productionSubtypeWeights.addWeight(float(emergencyUnitWeight), ProductionSpecialization.emergencyUnits)
		self.productionSubtypeWeights.addWeight(float(seaWeight), ProductionSpecialization.militaryNaval)
		self.productionSubtypeWeights.addWeight(float(wonderWeight), ProductionSpecialization.wonder)
		self.productionSubtypeWeights.addWeight(float(spaceshipWeight), ProductionSpecialization.spaceship)

		return int(militaryTrainingWeight + emergencyUnitWeight + seaWeight + wonderWeight + spaceshipWeight)

	def assignSpecializations(self, simulation):
		"""Assign specializations to cities"""
		citiesWithoutSpecialization: [CitySpecializationData] = []

		self.nextSpecializationDesired = CitySpecializationType.none
		# citiesWithoutSpecialization.removeAll()

		wonderSpecialization = self.wonderSpecialization()

		# Find specializations needed (including for the next city we build)
		self.selectSpecializations(simulation)

		# OBVIOUS ASSIGNMENTS: Loop through our cities making obvious assignments
		for loopCity in simulation.citiesOf(self.player):
			loopCityStrategy = loopCity.cityStrategy
			loopCityLocation = loopCity.location

			# If this is the city to build our current wonder in, mark all that
			if self.wonderChosen and self.wonderCity is not None and loopCity.location == self.wonderCity.location:
				if wonderSpecialization in self.specializationsNeeded:
					self.specializationsNeeded = list(filter(lambda s: s != wonderSpecialization, self.specializationsNeeded))
					loopCityStrategy.setSpecialization(wonderSpecialization)
					continue

			# If city default is equal to a needed type, go with that
			specialization = loopCityStrategy.defaultSpecialization()
			if specialization in self.specializationsNeeded:
				self.specializationsNeeded = list(filter(lambda s: s != specialization, self.specializationsNeeded))
				loopCityStrategy.setSpecialization(specialization)
			else:
				# If cities' current specialization is needed, stick with that
				specialization = loopCityStrategy.specialization()
				if specialization in self.specializationsNeeded:
					self.specializationsNeeded = list(filter(lambda s: s != specialization, self.specializationsNeeded))
					loopCityStrategy.setSpecialization(specialization)
				else:
					# Save this city off (with detailed data about what it is good at) to assign later
					cityData = CitySpecializationData(loopCity)

					# food
					foodValue = max(0.0, self.plotValueFor(YieldType.food, loopCityLocation, simulation))
					# AdjustValueBasedOnBuildings(pLoopCity, (YieldTypes)iI, cityData.m_iWeight[iI]);
					cityData.weight.setWeight(foodValue, YieldType.food)

					# production
					productionValue = max(0.0, self.plotValueFor(YieldType.production, loopCityLocation, simulation))
					# AdjustValueBasedOnBuildings(pLoopCity, (YieldTypes)iI, cityData.m_iWeight[iI]);
					cityData.weight.setWeight(productionValue, YieldType.production)

					# gold
					goldValue = max(0.0, self.plotValueFor(YieldType.gold, loopCityLocation, simulation))
					# AdjustValueBasedOnBuildings(pLoopCity, (YieldTypes) iI, cityData.m_iWeight[iI]);
					cityData.weight.setWeight(goldValue, YieldType.gold)

					# science
					scienceValue = max(0.0, self.plotValueForScience(loopCityLocation, simulation))
					# AdjustValueBasedOnBuildings(pLoopCity, (YieldTypes) iI, cityData.m_iWeight[iI]);
					cityData.weight.setWeight(scienceValue, YieldType.science)

					citiesWithoutSpecialization.append(cityData)

		# NEXT SPECIALIZATION NEEDED: Now figure out what we want to assign as our "next specialization needed"

		# If only one specialization left, it's easy
		if len(citiesWithoutSpecialization) == 0:
			firstSpecializationsNeeded = firstOrNone(self.specializationsNeeded)
			if firstSpecializationsNeeded is not None:
				self.nextSpecializationDesired = firstSpecializationsNeeded
				return

		# If all specializations left are "general economic", set that as next needed
		allGeneral = True
		for specializationNeeded in self.specializationsNeeded:
			if specializationNeeded != self.economicDefaultSpecialization():
				allGeneral = False

		if allGeneral:
			self.nextSpecializationDesired = self.economicDefaultSpecialization()
			if len(self.specializationsNeeded) > 0:
				del self.specializationsNeeded[0]
		else:
			# Find the best possible sites for each of the yield types
			self.findBestSites(simulation)

			# Compute the yield which we can improve the most with a new city
			# int iCurrentDelta;
			bestDelta: YieldList = YieldList()

			for cityWithoutSpecialization in citiesWithoutSpecialization:
				for yieldType in list(YieldType):
					currentDelta = cityWithoutSpecialization.weight.weight(yieldType) - self.bestValue.weight(yieldType)
					if currentDelta > bestDelta.weight(yieldType):
						bestDelta.setWeight(currentDelta, yieldType)

			# Save yield improvements in a vector we can sort
			yieldImprovements: YieldList = YieldList()

			for yieldType in list(YieldType):
				if bestDelta.weight(yieldType) > 0:
					yieldImprovements.setWeight(0.0, yieldType)
				else:
					yieldImprovements.setWeight(-bestDelta.weight(yieldType), yieldType)

			yieldImprovementsList = sorted(dictToArray(yieldImprovements), key=lambda x: x[1], reverse=True)

			# Take them out in order and see if we need this specialization
			foundIt: bool = False

			for mostImprovedYield in yieldImprovementsList:
				# Loop through needed specializations until we find one that matches
				for specializationNeeded in self.specializationsNeeded:
					yieldType = specializationNeeded.yieldType()
					if yieldType == mostImprovedYield[0]:
						self.nextSpecializationDesired = specializationNeeded
						self.specializationsNeeded = list(filter(lambda s: s != specializationNeeded, self.specializationsNeeded))
						foundIt = True
						break

				if foundIt:
					break

		# REMAINING ASSIGNMENTS: Make the rest of the assignments
		for specializationNeeded in self.specializationsNeeded:
			yieldType = specializationNeeded.yieldType()
			coastal = specializationNeeded.mustBeCoastal()
			bestCity = lastOrNone(citiesWithoutSpecialization)

			# Pick best existing city based on a better computation of existing city's value for a yield type
			bestValue: float = -1.0
			for cityWithoutSpecialization in citiesWithoutSpecialization:
				if coastal:
					city = cityWithoutSpecialization.city
					if city is None:
						continue

					if not simulation.isCoastalAt(city.location):
						continue

				if yieldType == YieldType.none or yieldType is None:
					# General economic is all yields added together
					cityValue = 0.0

					for yieldTypeIterator in list(YieldType):
						cityValue += cityWithoutSpecialization.weight.weight(yieldTypeIterator)

					if cityValue > bestValue:
						bestValue = cityValue
						bestCity = cityWithoutSpecialization
				else:
					if cityWithoutSpecialization.weight.weight(yieldType) > bestValue:
						bestValue = cityWithoutSpecialization.weight.weight(yieldType)
						bestCity = cityWithoutSpecialization

			if len(citiesWithoutSpecialization) > 0:
				# Found a city to set
				lastCityWithoutSpecialization = lastOrNone(citiesWithoutSpecialization)
				firstCityWithoutSpecialization = firstOrNone(citiesWithoutSpecialization)

				if bestCity is not None and bestCity.city is not None and \
					lastCityWithoutSpecialization is not None and lastCityWithoutSpecialization.city is not None and \
					bestCity.city.location != lastCityWithoutSpecialization.city.location:

					bestCity.city.cityStrategy.setSpecialization(specializationNeeded)
					citiesWithoutSpecialization = list(filter(lambda c: c.city.location != bestCity.city.location, citiesWithoutSpecialization))
				elif firstCityWithoutSpecialization is not None:
					# No (coastal) city found, use default specialization as last resort
					city = firstCityWithoutSpecialization.city
					if city is not None:
						city.cityStrategy.setSpecialization(self.economicDefaultSpecialization())
						citiesWithoutSpecialization = list(filter(lambda c: c.city.location != city.location, citiesWithoutSpecialization))

		return

	def wonderSpecialization(self) -> CitySpecializationType:
		"""Find the specialization type for building wonders"""
		for citySpecializationType in list(CitySpecializationType):
			if citySpecializationType.isWonder():
				return citySpecializationType

		return CitySpecializationType.generalEconomic

	def selectSpecializations(self, simulation):
		"""Find specializations needed (including for the next city we build)"""
		specializationsToAssign = len(simulation.citiesOf(self.player)) + 1
		oldWeight = 0.0
		reductionAmount = 0.0

		self.specializationsNeeded = []
		self.wonderChosen = False

		# Clear info about what we've picked
		self.numSpecializationsForThisYield.setWeight(0.0, YieldType.none)
		self.numSpecializationsForThisYield.setWeight(0.0, YieldType.food)
		self.numSpecializationsForThisYield.setWeight(0.0, YieldType.production)
		self.numSpecializationsForThisYield.setWeight(0.0, YieldType.gold)
		self.numSpecializationsForThisYield.setWeight(0.0, YieldType.science)
		self.numSpecializationsForThisYield.setWeight(0.0, YieldType.culture)
		self.numSpecializationsForThisYield.setWeight(0.0, YieldType.faith)

		for productionSpecialization in list(ProductionSpecialization):
			self.numSpecializationsForThisSubtype.setWeight(0.0, productionSpecialization)

		wonderType: Optional[WonderType] = None
		wonderBuildCity = self.wonderBuildCity()
		if wonderBuildCity is not None:
			if wonderBuildCity.currentBuildableItem().buildableType == BuildableType.wonder:
				wonderType = wonderBuildCity.currentBuildableItem().wonderType

		# Do we have a wonder build in progress that we can't interrupt?
		if not self.interruptWonders and wonderType is not None:
			self.specializationsNeeded.append(self.wonderSpecialization())
			self.numSpecializationsForThisYield.addWeight(1.0, YieldType.production)
			oldWeight = self.yieldWeights.weight(YieldType.production)
			reductionAmount = self.productionSubtypeWeights.weight(self.wonderSubtype())
			self.yieldWeights.setWeight(oldWeight - reductionAmount, YieldType.production)

			# Only one wonder at a time, so zero out the weight for this subtype entirely
			self.productionSubtypeWeights.setWeight(0.0, self.wonderSubtype())
			self.wonderChosen = True
		else:
			self.wonderCity = None

		# LOOP as many times as we have cities PLUS ONE
		while len(self.specializationsNeeded) < specializationsToAssign:
			# Find the highest weighted specialization
			# Mark that we need one city of this type
			yieldValue = firstOrNone(dictToArray(self.yieldWeights))
			if yieldValue is None:
				raise Exception("explode")

			tmpCitySpecializationType: CitySpecializationType = CitySpecializationType.none

			if self.numSpecializationsForThisYield.weight(yieldValue[0]) > 1.0:
				if yieldValue[0] == YieldType.production:
					tmpCitySpecializationType = self.selectProductionSpecialization(reductionAmount)

					oldWeight = yieldValue.value
					self.numSpecializationsForThisYield.addWeight(1.0, yieldValue[0])
					newWeight = oldWeight - reductionAmount
					self.yieldWeights.setWeight(newWeight, yieldValue[0])
			else:
				tmpCitySpecializationType = self.firstSpecialization(yieldValue[0])

				# Reduce weight for this specialization based on dividing original weight by <num of this type + 1>
				oldWeight = yieldValue[1]
				self.numSpecializationsForThisYield.addWeight(1.0, yieldValue[0])
				newWeight = oldWeight * self.numSpecializationsForThisYield.weight(yieldValue[0]) / \
					(self.numSpecializationsForThisYield.weight(yieldValue[0]) + 1.0)
				self.yieldWeights.setWeight(newWeight, yieldValue[0])

			self.specializationsNeeded.append(tmpCitySpecializationType)

		return

	def wonderSubtype(self) -> ProductionSpecialization:
		raise Exception('niy')

	def firstSpecialization(self, yieldType: YieldType) -> CitySpecializationType:
		for citySpecializationType in list(CitySpecializationType):
			citySpecializationTypeYieldType = citySpecializationType.yieldType()
			if citySpecializationTypeYieldType is not None:
				if citySpecializationTypeYieldType == yieldType:
					return citySpecializationType

		return CitySpecializationType.generalEconomic

	def economicDefaultSpecialization(self) -> CitySpecializationType:
		for citySpecializationType in list(CitySpecializationType):
			if citySpecializationType.isDefault():
				return citySpecializationType

		return CitySpecializationType.generalEconomic

	def plotValueFor(self, yieldType: YieldType, location: HexPoint, simulation) -> float:
		"""Evaluate strength of an existing city for providing a specific type of yield (except Science!)"""
		totalPotentialYield: float = 0.0
		multiplier: float = 0.0
		potentialYield: float = 0.0
		firstRingMultiplier: float = 8.0 # AI_CITY_SPECIALIZATION_YIELD_WEIGHT_FIRST_RING
		secondRingMultiplier: float = 5.0 # AI_CITY_SPECIALIZATION_YIELD_WEIGHT_SECOND_RING
		thirdRingMultiplier: float = 2.0 # AI_CITY_SPECIALIZATION_YIELD_WEIGHT_THIRD_RING

		# Evaluate potential from plots not currently being worked
		for loopPoint in location.areaWithRadius(2):
			if loopPoint == location:
				continue

			loopPlot = simulation.tileAt(loopPoint)

			if loopPlot is None:
				continue

			potentialYield = loopPlot.yields(self.player, ignoreFeature=False).value(yieldType)

			# If owned by someone else, not worth anything
			if loopPlot.hasOwner() and loopPlot.owner() != self.player:
				multiplier = 0.0
			else:
				distance = loopPoint.distance(location)
				if distance == 1:
					multiplier = firstRingMultiplier
				elif distance == 2:
					multiplier = secondRingMultiplier
				elif distance == 3:
					multiplier = thirdRingMultiplier

			totalPotentialYield += potentialYield * multiplier

		return totalPotentialYield

	def plotValueForScience(self, location: HexPoint, simulation) -> float:
		"""Evaluate strength of a city plot for providing science"""
		# Roughly half of weight comes from food yield
		# The other half will be are there open tiles we can easily build schools on
		totalFoodYield = 0
		totalClearTileWeight = 0
		multiplier = 0
		potentialYield = 0.0
		firstRingMultiplier = 8  # AI_CITY_SPECIALIZATION_YIELD_WEIGHT_FIRST_RING
		secondRingMultiplier = 5  # AI_CITY_SPECIALIZATION_YIELD_WEIGHT_SECOND_RING
		thirdRingMultiplier = 2  # AI_CITY_SPECIALIZATION_YIELD_WEIGHT_THIRD_RING

		# Evaluate potential from plots not currently being worked
		for loopPoint in location.areaWithRadius(2):
			if loopPoint == location:
				continue

			loopPlot = simulation.tileAt(loopPoint)

			if loopPlot is None:
				continue

			isClear = False

			if not loopPlot.hasAnyResourceFor(self.player):
				if not loopPlot.hasAnyFeature():
					if not loopPlot.isHills():
						if loopPlot.improvement() == ImprovementType.none:
							isClear = True

			potentialYield = loopPlot.yields(self.player, ignoreFeature=False).food + \
				loopPlot.yields(self.player, ignoreFeature=False).science

			# If owned by someone else, not worth anything
			if loopPlot.hasOwner() and loopPlot.owner() != self.player:
				multiplier = 0
			else:
				distance = loopPoint.distance(location)
				if distance == 1:
					multiplier = firstRingMultiplier
				elif distance == 2:
					multiplier = secondRingMultiplier
				elif distance == 3:
					multiplier = thirdRingMultiplier

			totalFoodYield += int(potentialYield) * multiplier

			if isClear:
				totalClearTileWeight += multiplier

		return float(totalFoodYield + totalClearTileWeight)

	def findBestSites(self, simulation):
		"""Find the best nearby city site for all yield types"""
		plotValue: float = 0.0

		# Clear output
		for yieldType in list(YieldType):
			self.bestValue.setWeight(0.0, yieldType)

		# Found value drops off based on distance, so safe to only look halfway out
		evalDistance = 30 / 2  # SETTLER_EVALUATION_DISTANCE

		citySiteEvaluator = simulation.citySiteEvaluator()
		mapSize = simulation.mapSize()

		for x in range(mapSize.size().width()):
			for y in range(mapSize.size().height()):
				pt = HexPoint(x, y)
				tile = simulation.tileAt(pt)

				if tile is None:
					continue

				if citySiteEvaluator.canCityBeFoundOn(tile, self.player):
					# Check if within range of our cities
					# pNearestCity = GC.getMap().findCity(pPlot->getX(), pPlot->getY(), m_pPlayer->GetID(), NO_TEAM, true / * bSameArea * /);
					nearestCity: Optional[City] = simulation.nearestCity(pt, self.player)
					if nearestCity is not None:
						if pt.distance(nearestCity.location) <= evalDistance:
							for yieldType in list(YieldType):
								if yieldType != YieldType.science:
									plotValue = self.plotValueFor(yieldType, pt, simulation)
								else:
									plotValue = self.plotValueForScience(pt, simulation)

								if plotValue > self.bestValue.weight(yieldType):
									self.bestValue.setWeight(plotValue, yieldType)

		# self.logBestSites()

		return


class DangerPlotsAI:
	def __init__(self, player):
		self.player = player

		self._dangerPlots = None
		self._arrayAllocated = False
		self._dirty = True

		# modifiers
		self._majorWarMod = 1.0  # AI_DANGER_MAJOR_APPROACH_WAR
		self._majorHostileMod = 0.2  # AI_DANGER_MAJOR_APPROACH_HOSTILE
		self._majorDeceptiveMod = 0.1  # AI_DANGER_MAJOR_APPROACH_DECEPTIVE
		self._majorGuardedMod = 0.5  # AI_DANGER_MAJOR_APPROACH_GUARDED
		self._majorAfraidMod = 0.9  # AI_DANGER_MAJOR_APPROACH_AFRAID
		self._majorFriendlyMod = 0.0  # AI_DANGER_MAJOR_APPROACH_FRIENDLY
		self._majorNeutralMod = 0.1  # AI_DANGER_MAJOR_APPROACH_NEUTRAL
		self._minorNeutralMod = 0.1  # AI_DANGER_MINOR_APPROACH_NEUTRAL
		self._minorFriendlyMod = 0.0  # AI_DANGER_MINOR_APPROACH_FRIENDLY
		self._minorBullyMod = 0.9  # AI_DANGER_MINOR_APPROACH_BULLY
		self._minorConquestMod = 1.0  # AI_DANGER_MINOR_APPROACH_CONQUEST

	def initialize(self, simulation):
		mapSize = simulation.mapSize().size()
		self._dangerPlots = Array2D(mapSize.width(), mapSize.height())
		self._dangerPlots.fill(0)

		self._arrayAllocated = True

	def dangerAt(self, location: HexPoint) -> float:
		if self._dangerPlots is None:
			return 0.0

		if 0 > location.x or location.x >= self._dangerPlots.width or \
			0 > location.y or location.y >= self._dangerPlots.height:
			return 0.0

		return self._dangerPlots.values[location.y][location.x]

	def updateDanger(self, pretendWarWithAllCivs: bool, ignoreVisibility: bool, simulation):
		"""Updates the danger plots values to reflect threats across the map"""
		# danger plots have not been initialized yet, so no need to update
		if not self._arrayAllocated:
			self.initialize(simulation)

		mapSize = simulation.mapSize().size()
		if self._dangerPlots.width != mapSize.width() or self._dangerPlots.height != mapSize.height():
			raise Exception("map size does not match number of DangerPlots")

		# wipe out values
		self._dangerPlots.fill(0)

		# for each opposing civ
		for loopPlayer in simulation.players:
			if not loopPlayer.isAlive():
				continue

			if loopPlayer == self.player:
				continue

			if self.shouldIgnorePlayer(loopPlayer) and not pretendWarWithAllCivs:
				continue

			# for each unit
			for loopUnit in simulation.unitsOf(loopPlayer):
				if self.shouldIgnoreUnit(loopUnit, ignoreVisibility, simulation):
					continue

				unitRange = loopUnit.baseMoves(simulation=simulation)
				if loopUnit.canAttackRanged():
					unitRange += loopUnit.range()

				unitTile = simulation.tileAt(loopUnit.location)
				self.assignUnitDangerValue(loopUnit, unitTile, simulation)

				for loopPoint in loopUnit.location.areaWithRadius(unitRange):
					if not simulation.valid(loopPoint):
						continue

					if loopPoint == loopUnit.location:
						continue

					loopTile = simulation.tileAt(loopUnit.location)

					if not loopUnit.canMoveOrAttackInto(loopUnit.location, simulation) and \
						not loopUnit.canRangeStrikeAt(loopPoint, needWar=True, noncombatAllowed=True, simulation=simulation):
						continue

					self.assignUnitDangerValue(loopUnit, loopTile, simulation)

			# for each city
			for loopCity in simulation.citiesOf(loopPlayer):
				if self.shouldIgnoreCity(loopCity, ignoreVisibility, simulation):
					continue

				cityRange = City.attackRange
				cityTile = simulation.tileAt(loopCity.location)
				self.assignCityDangerValue(loopCity, cityTile)

				for loopPoint in loopCity.location.areaWithRadius(cityRange):
					if not simulation.valid(loopPoint):
						continue

					loopTile = simulation.tileAt(loopPoint)
					self.assignCityDangerValue(loopCity, loopTile)

		# Citadels
		# 	int iCitadelValue = GetDangerValueOfCitadel();
		# 	int iPlotLoop;
		# 	CvPlot *pPlot, *pAdjacentPlot;
		# 	for (iPlotLoop = 0; iPlotLoop < GC.getMap().numPlots(); iPlotLoop++)
		# 	{
		# 		pPlot = GC.getMap().plotByIndexUnchecked(iPlotLoop);
		#
		# 		if (pPlot->isRevealed(thisTeam))
		# 		{
		# 			ImprovementTypes eImprovement = pPlot->getRevealedImprovementType(thisTeam);
		# 			if (eImprovement != NO_IMPROVEMENT and GC.getImprovementInfo(eImprovement)->GetNearbyEnemyDamage() > 0)
		# 			{
		# 				if (!ShouldIgnoreCitadel(pPlot, bIgnoreVisibility))
		# 				{
		# 					for (int iI = 0; iI < NUM_DIRECTION_TYPES; iI++)
		# 					{
		# 						pAdjacentPlot = plotDirection(pPlot->getX(), pPlot->getY(), ((DirectionTypes)iI));
		#
		# 						if (pAdjacentPlot != NULL)
		# 						{
		# 							AddDanger(pAdjacentPlot->getX(), pAdjacentPlot->getY(), iCitadelValue);
		# 						}
		# 					}
		# 				}
		# 			}
		# 		}
		# 	}

		# testing city danger values
		for loopCity in simulation.citiesOf(self.player):
			threatValue = self.dangerOfCity(loopCity)
			loopCity.setThreatValue(threatValue)

		self._dirty = False

	def setDirty(self):
		self._dirty = True

	def isDirty(self) -> bool:
		return self._dirty

	def shouldIgnorePlayer(self, otherPlayer) -> bool:
		"""Should this player be ignored when creating the danger plots?"""
		if otherPlayer.isCityState() != self.player.isCityState() and not otherPlayer.isBarbarian() and \
			not otherPlayer.isBarbarian():

			if self.player.isCityState():
				minor = self.player
				major = otherPlayer
			else:
				minor = otherPlayer
				major = self.player

			if minor.minorCivAI.isFriends(major):
				return True

			# if we're a major, we should ignore minors that are not at war with us
			if self.player.isCityState():
				if not major.isAtWarWith(minor):
					return True

		return False

	def shouldIgnoreCity(self, city, ignoreVisibility, simulation) -> bool:
		"""Should this city be ignored when creating the danger plots?"""
		# ignore unseen cities
		tile = simulation.tileAt(city.location)
		if not tile.isVisibleTo(self.player) and not ignoreVisibility:
			return True

		return False

	def shouldIgnoreUnit(self, unit, ignoreVisibility, simulation):
		"""Should this unit be ignored when creating the danger plots?"""
		if not unit.canAttack():
			return True

		tile = simulation.tileAt(unit.location)
		if not tile.isVisibleTo(self.player) and not ignoreVisibility:
			return True

		if unit.domain() == UnitDomainType.air:
			return True

		return False

	def dangerOfCity(self, city) -> int:
		"""Sums the danger values of the plots around the city to determine the danger value of the city"""
		if city is None:
			return 0

		evalRange = 5  # AI_DIPLO_PLOT_RANGE_FROM_CITY_HOME_FRONT
		dangerValue = 0
		for pt in city.location.areaWithRadius(evalRange):
			dangerValue += self.dangerAt(pt)

		return dangerValue

	def assignUnitDangerValue(self, unit, tile, simulation):
		"""Contains the calculations to do the danger value for the plot according to the unit"""
		iCombatValueCalc = 100
		iBaseUnitCombatValue = unit.baseCombatStrengthConsideringDamage() * iCombatValueCalc
		# Combat capable? If not, the calculations will always result in 0, so just skip it.
		if iBaseUnitCombatValue > 0:
			# Will any danger be zeroed out?
			if not self.isDangerByRelationshipZero(unit.player, tile):
				# iDistance = plotDistance(pUnitPlot->getX(), pUnitPlot->getY(), pPlot->getX(), pPlot->getY());
				# iRange = pUnit->baseMoves();
				# FAssertMsg(iRange > 0, "0 range? Uh oh");

				dataSource = simulation.ignoreUnitsPathfinderDataSource(unit.movementType(), unit.player, unit.canEmbarkInto(None, simulation=simulation), unit.player.canEnterOcean())  # GC.getIgnoreUnitsPathFinder();
				pathFinder = AStarPathfinder(dataSource)

				# can the unit actually walk there
				iTurnsAway = pathFinder.turnsToReachTarget(unit, tile.point, simulation=simulation)

				if iTurnsAway == sys.maxsize:
					return

				iTurnsAway = max(iTurnsAway, 1)

				iUnitCombatValue = iBaseUnitCombatValue / iTurnsAway
				iUnitCombatValue = self.modifyDangerByRelationship(unit.player, tile, iUnitCombatValue)
				self.addDanger(tile.point, iUnitCombatValue, iTurnsAway <= 1)

		return

	def isDangerByRelationshipZero(self, otherPlayer, tile) -> bool:
		"""
			Returns true if the relationship of the danger plots owner and the input player and plot owner
			would result in a 0 danger.  This helps avoid costly path finder calls if the end result will be 0.
		"""
		bIgnoreInFriendlyTerritory = False

		# Full value if a player we're at war with
		if self.player.isAtWarWith(otherPlayer):
			return False

		# if it's a human player, ignore neutral units
		if self.player.isHuman():
			return True

		bResultMultiplierIsZero = False
		if self.player.isCityState():  # if the evaluator is a minor civ
			if not self.player.isAtWarWith(otherPlayer):  # and they're not at war with the other player
				bIgnoreInFriendlyTerritory = True  # ignore friendly territory
		elif otherPlayer.isMajorAI():
			# should we be using bHideTrueFeelings?
			approach = self.player.diplomacyAI.majorApproachTowards(otherPlayer)  # / * bHideTrueFeelings * / false
			if approach == MajorPlayerApproachType.war:
				bResultMultiplierIsZero = self._majorWarMod == 0.0
			elif approach == MajorPlayerApproachType.hostile:  # MAJOR_CIV_APPROACH_Hostile
				bResultMultiplierIsZero = self._majorHostileMod == 0.0
				bIgnoreInFriendlyTerritory = True
			elif approach == MajorPlayerApproachType.deceptive:  # MAJOR_CIV_APPROACH_DECEPTIVE
				bResultMultiplierIsZero = self._majorDeceptiveMod == 0.0
				bIgnoreInFriendlyTerritory = True
			elif approach == MajorPlayerApproachType.guarded:  # MAJOR_CIV_APPROACH_GUARDED
				bResultMultiplierIsZero = self._majorGuardedMod == 0.0
				bIgnoreInFriendlyTerritory = True
			elif approach == MajorPlayerApproachType.afraid:  # MAJOR_CIV_APPROACH_AFRAID
				bResultMultiplierIsZero = self._majorAfraidMod == 0.0
				bIgnoreInFriendlyTerritory = True
			elif approach == MajorPlayerApproachType.friendly:  # MAJOR_CIV_APPROACH_FRIENDLY
				bResultMultiplierIsZero = self._majorFriendlyMod == 0.0
				bIgnoreInFriendlyTerritory = True
			elif approach == MajorPlayerApproachType.neutral:  # MAJOR_CIV_APPROACH_NEUTRAL
				bResultMultiplierIsZero = self._majorNeutralMod == 0.0
				bIgnoreInFriendlyTerritory = True
		elif otherPlayer.isCityState():
			approach = self.player.diplomacyAI.minorApproachTowards(otherPlayer)
			if approach == MinorPlayerApproachType.ignore:  # MINOR_CIV_APPROACH_IGNORE
				bResultMultiplierIsZero = self._minorNeutralMod == 0.0
				bIgnoreInFriendlyTerritory = True
			elif approach == MinorPlayerApproachType.ignore:  # MINOR_CIV_APPROACH_FRIENDLY:
				bResultMultiplierIsZero = self._minorFriendlyMod == 0.0
				bIgnoreInFriendlyTerritory = True
			elif approach == MinorPlayerApproachType.bully:  # MINOR_CIV_APPROACH_BULLY
				bResultMultiplierIsZero = self._minorBullyMod == 0.0
			elif approach == MinorPlayerApproachType.conquest:  # MINOR_CIV_APPROACH_CONQUEST
				bResultMultiplierIsZero = self._minorConquestMod == 0.0

		# if the plot is in our own territory and, with the current approach, we should ignore danger values
		# in our own territory zero out the value
		if tile is not None and tile.owner() == self.player and bIgnoreInFriendlyTerritory:
			return True

		return bResultMultiplierIsZero

	def modifyDangerByRelationship(self, otherPlayer, tile, danger: int) -> int:
		bIgnoreInFriendlyTerritory = False
		result = danger

		# Full value if a player we're at war with
		if self.player.isAtWarWith(otherPlayer):
			return danger

		# if it's a human player, ignore neutral units
		if self.player.isHuman():
			return 0

		bResultMultiplierIsZero = False
		if self.player.isCityState():  # if the evaluator is a minor civ
			if not self.player.isAtWarWith(otherPlayer):  # and they're not at war with the other player
				bIgnoreInFriendlyTerritory = True  # ignore friendly territory
		elif otherPlayer.isMajorAI():
			# should we be using bHideTrueFeelings?
			approach = self.player.diplomacyAI.majorApproachTowards(otherPlayer)  # / * bHideTrueFeelings * / false
			if approach == MajorPlayerApproachType.war:
				result = result * self._majorWarMod
			elif approach == MajorPlayerApproachType.hostile:  # MAJOR_CIV_APPROACH_Hostile
				result = result * self._majorHostileMod
				bIgnoreInFriendlyTerritory = True
			elif approach == MajorPlayerApproachType.deceptive:  # MAJOR_CIV_APPROACH_DECEPTIVE
				result = result * self._majorDeceptiveMod
				bIgnoreInFriendlyTerritory = True
			elif approach == MajorPlayerApproachType.guarded:  # MAJOR_CIV_APPROACH_GUARDED
				result = result * self._majorGuardedMod
				bIgnoreInFriendlyTerritory = True
			elif approach == MajorPlayerApproachType.afraid:  # MAJOR_CIV_APPROACH_AFRAID
				result = result * self._majorAfraidMod
				bIgnoreInFriendlyTerritory = True
			elif approach == MajorPlayerApproachType.friendly:
				result = result * self._majorFriendlyMod
				bIgnoreInFriendlyTerritory = True
			elif approach == MajorPlayerApproachType.neutral:
				result = result * self._majorNeutralMod
				bIgnoreInFriendlyTerritory = True
		elif otherPlayer.isCityState():
			approach = self.player.diplomacyAI.minorApproachTowards(otherPlayer)
			if approach == MinorPlayerApproachType.ignore:
				result = result * self._minorNeutralMod
				bIgnoreInFriendlyTerritory = True
			elif approach == MinorPlayerApproachType.friendly:  # MINOR_CIV_APPROACH_FRIENDLY
				result = result * self._minorFriendlyMod
				bIgnoreInFriendlyTerritory = True
			elif approach == MinorPlayerApproachType.bully:  # MINOR_CIV_APPROACH_BULLY
				result = result * self._minorBullyMod
			elif approach == MinorPlayerApproachType.conquest:  # MINOR_CIV_APPROACH_CONQUEST
				result = result * self._minorConquestMod

		# if the plot is in our own territory and, with the current approach, we should ignore danger values
		# in our own territory zero out the value
		if tile is not None and tile.hasOwner() and tile.owner() == self.player and bIgnoreInFriendlyTerritory:
			result = 0

		return result

	def addDanger(self, point: HexPoint, value: int, withinOneMove: bool):
		"""Add an amount of danger to a given tile"""
		if value > 0:
			if withinOneMove:
				value = int(value) | 0x1
			else:
				value = int(value) & ~0x1

			self._dangerPlots.values[point.y][point.x] += value

		return

	def assignCityDangerValue(self, city, tile):
		"""Contains the calculations to do the danger value for the plot according to the city"""
		iCombatValue = city.strengthValue()
		iCombatValue = self.modifyDangerByRelationship(city.player, tile, iCombatValue)
		self.addDanger(tile.point, iCombatValue, False)


class PlayerOperations:
	def __init__(self, player):
		self.player = player

		self._operations = []

	def doDelayedDeath(self, simulation):
		operationsToDelete: [Operation] = []

		for operation in self._operations:
			if operation.doDelayedDeath(simulation):
				operationsToDelete.append(operation)

		for operationToDelete in operationsToDelete:
			self.deleteOperation(operationToDelete)

	def doTurn(self, simulation):
		for operation in self._operations:
			operation.doTurn()

	def __iter__(self):
		return self._operations.__iter__()

	def addOperation(self, operation: Operation):
		self._operations.append(operation)

	def deleteOperation(self, operation: Operation):
		self._operations = list(filter(lambda op: op != operation, self._operations))

	def operationsOfType(self, operationType: UnitOperationType) -> [Operation]:
		return list(filter(lambda op: op.operationType == operationType, self._operations))

	def numberOfOperationsOfType(self, operationType: UnitOperationType) -> int:
		return len(self.operationsOfType(operationType))

	def hasOperationsOfType(self, operationType: UnitOperationType) -> bool:
		return len(self.operationsOfType(operationType)) > 0

	def plotArmyMoves(self, simulation):
		# Update all operations(moved down - previously was in the PlayerAI object)
		for operation in self._operations:
			if operation.lastTurnMoved() < simulation.currentTurn:
				if operation.moveType == OperationMoveType.singleHex:
					self.player.tacticalAI.plotSingleHexOperationMoves(operation, simulation)  # EscortedOperation
				elif operation.moveType == OperationMoveType.enemyTerritory:
					self.player.tacticalAI.plotEnemyTerritoryOperationMoves(operation, simulation)  # EnemyTerritoryOperation
				elif operation.moveType == OperationMoveType.navalEscort:
					self.player.tacticalAI.plotNavalEscortOperationMoves(operation, simulation)  # NavalEscortedOperation
				elif operation.moveType == OperationMoveType.freeformNaval:
					self.player.tacticalAI.plotFreeformNavalOperationMoves(operation, simulation)  # NavalOperation
				elif operation.moveType == OperationMoveType.rebase:
					# NOOP
					pass

				operation.setLastTurnMoved(simulation.currentTurn)
				operation.checkOnTarget(simulation)

		killedSomething: bool = True

		while killedSomething:
			killedSomething = False

			for operation in self._operations:
				if operation.doDelayedDeath(simulation):
					killedSomething = True
					break

		return

	def numberOfUnitsNeededToBeBuilt(self) -> int:
		rtnValue = 0

		for operation in self._operations:
			rtnValue += operation.numberOfUnitsNeededToBeBuilt()

		return rtnValue

	def isCityAlreadyTargeted(self, city, domain: UnitDomainType, percentToTarget: int = 100, simulation = None) -> bool:
		if city is None:
			raise Exception('city must not be none')

		if simulation is None:
			raise Exception('simulation must not be none')

		for operation in self._operations:
			if operation.targetPosition == city.location and operation.percentFromMusterPointToTarget(simulation) < percentToTarget:

				# Naval attacks are mixed land/naval operations
				if (domain == UnitDomainType.none or domain == UnitDomainType.sea) and operation.isMixedLandNavalOperation():
					return True

				if (domain == UnitDomainType.none or domain == UnitDomainType.land) and not operation.isMixedLandNavalOperation():
					return True

		return False


class PlayerArmies:
	def __init__(self, player):
		self.player = player
		self._armies = []

	def __iter__(self):
		return self._armies.__iter__()

	def doDelayedDeath(self):
		for army in self._armies:
			army.doDelayedDeath()

	def doTurn(self, simulation):
		for army in self._armies:
			army.doTurn(simulation)

	def removeArmy(self, army: Army):
		self._armies = list(filter(lambda armyIt: armyIt != army, self._armies))


class EnvoyEffect:
	def __init__(self, cityState: CityStateType, level: EnvoyEffectLevel, enabled: bool = True):
		self.cityState = cityState
		self.level = level
		self.enabled = enabled

	def isEqual(self, category: CityStateCategory, level: EnvoyEffectLevel) -> bool:
		return self.cityState.category() == category and self.level == level


class PlayerEnvoys:
	def __init__(self, player):
		self.player = player

		self._envoyArray = WeightedBaseList()
		self._unassignedEnvoysValue = 0

	def unassignedEnvoys(self) -> int:
		return self._unassignedEnvoysValue

	def meet(self, cityState: CityStateType, isFirst: bool):
		self._envoyArray.addWeight(1 if isFirst else 0, cityState)

	def envoysIn(self, cityState: CityStateType) -> int:
		return int(self._envoyArray.weight(cityState))

	def changeUnassignedEnvoysBy(self, value: int):
		if self._unassignedEnvoysValue + value < 0:
			raise Exception('unhandled yet - need to unassign envoys until unassignedEnvoys is zero')

		if self.player.isCityState():
			return

		self._unassignedEnvoysValue += value

	def assignEnvoyTo(self, cityState: CityStateType) -> bool:
		"""
			assigns an envoy to `cityState`

			@param cityState: cityState to assign the envoy to
			@return:
		"""
		# check that there are unassigned envoys to assign to the selected city state
		if self._unassignedEnvoysValue <= 0:
			return False

		self.changeUnassignedEnvoysBy(-1)
		self._envoyArray.addWeight(1, cityState)

		return True

	def unassignEnvoyTo(self, cityState: CityStateType) -> bool:
		"""
			unassigns an envoy from `cityState`
			@param cityState: cityState to unassign the envoy from
			@return:
		"""
		# check that there is at least one envoy currently assigned to this city state
		if self._envoyArray.weight(cityState) <= 0:
			return False

		self.changeUnassignedEnvoysBy(1)
		self._envoyArray.addWeight(-1, cityState)

		return True

	def envoyEffects(self, simulation) -> [EnvoyEffect]:
		diplomacyAI = self.player.diplomacyAI

		effects: [EnvoyEffect] = []

		for loopPlayer in simulation.players:
			if loopPlayer == self.player:
				continue

			if loopPlayer.isCityState():
				if diplomacyAI.hasMetWith(loopPlayer):
					cityState = loopPlayer.cityState
					envoys = self.envoysIn(cityState)

					if envoys >= 1:
						effects.append(EnvoyEffect(cityState, EnvoyEffectLevel.first))

					if envoys >= 3:
						effects.append(EnvoyEffect(cityState, EnvoyEffectLevel.third))

					if envoys >= 6:
						effects.append(EnvoyEffect(cityState, EnvoyEffectLevel.sixth))

					suzerainLeader = loopPlayer.suzerain()
					if suzerainLeader is not None:
						suzerainPlayer = simulation.playerFor(suzerainLeader)
						if suzerainPlayer is not None:
							if suzerainPlayer == self.player:
								effects.append(EnvoyEffect(cityState, EnvoyEffectLevel.suzerain))

		return effects

	def isSuzerainOf(self, cityState, simulation):
		diplomacyAI = self.player.diplomacyAI
		cityStatePlayer = simulation.cityStatePlayerFor(cityState)

		if cityStatePlayer is None:
			return False

		if not diplomacyAI.hasMetWith(cityStatePlayer):
			return False

		envoys = self.envoysIn(cityState)

		if envoys < 3:
			return False

		suzerainLeader = cityStatePlayer.suzerain()
		if suzerainLeader is not None:
			suzerainPlayer = simulation.playerFor(suzerainLeader)
			if suzerainPlayer is not None:
				if suzerainPlayer == self.player:
					return True

		return False


class MinorCivAI:
	def __init__(self, player):
		self.player = player

		self._pledgeToProtect = WeightedBaseList()

	def isFriends(self, otherPlayer) -> bool:
		return False

	def numberResourcesMajorLacks(self, otherPlayer) -> int:
		"""How many resources does this minor own that eMajor doesn't?"""
		numTheyLack: int = 0

		if not otherPlayer.isMajorAI():
			return 0

		# Loop through all resources to see what this minor has
		for loopResource in list(ResourceType):
			# Must not be a Bonus resource
			if loopResource.usage() == ResourceUsage.bonus:
				continue

			# We must have it
			if self.player.numberOfItemsInStockpile(loopResource) == 0:
				continue

			# They must not have it
			if otherPlayer.numberOfItemsInStockpile(loopResource) > 0:
				continue

			numTheyLack += 1

		return numTheyLack

	def isProtectedByMajor(self, otherPlayer) -> bool:
		return self._pledgeToProtect.weight(hash(otherPlayer)) > 0

	def personality(self) -> MinorPlayerPersonalityType:
		return MinorPlayerPersonalityType.neutral

	def isEverBulliedByMajor(self, otherPlayer) -> bool:
		return False

	def isActiveQuestFor(self, otherPlayer, quest: CityStateQuestType) -> bool:
		return False

	def canMajorProtect(self, otherPlayer) -> bool:
		return False

	def isAllyOf(self, otherPlayer) -> bool:
		return False

	def ally(self):
		return None


class Player:
	BaseStockPileAmount = 50

	def __init__(self, leader: Union[LeaderType, dict], cityState: Optional[CityStateType]=None, human: bool=False):
		if isinstance(leader, LeaderType):
			self.leader = leader
			self.cityState = cityState
			self.human = human

			# ais
			self.grandStrategyAI = GrandStrategyAI(player=self)
			self.economicAI = EconomicAI(player=self)
			self.militaryAI = MilitaryAI(player=self)
			self.tacticalAI = TacticalAI(player=self)
			self.diplomacyAI = DiplomaticAI(player=self)
			self.homelandAI = HomelandAI(player=self)
			self.builderTaskingAI = BuilderTaskingAI(player=self)
			self.citySpecializationAI = CitySpecializationAI(player=self)
			self.dangerPlotsAI = DangerPlotsAI(player=self)
			self.minorCivAI = MinorCivAI(player=self)
			self.religionAI = ReligionAI(player=self)
			self.wonderProductionAI = None
			self.dealAI = DealAI(player=self)
			self.leagueAI = LeagueAI(player=self)

			self.notifications = Notifications(self)
			self.diplomacyRequests = DiplomacyRequests(player=self)

			# special
			self.techs = PlayerTechs(self)
			self.civics = PlayerCivics(self)
			self.moments = PlayerMoments(self)
			self._traits = PlayerTraits(self)
			self.personalityFlavors = Flavors()

			# state values
			self.isAliveVal: bool = True
			self.turnActive: bool = False
			self._checkedOperations: bool = False
			self.finishTurnButtonPressedValue: bool = False
			self.processedAutoMovesValue: bool = False
			self.autoMovesValue: bool = False
			self.endTurnValue: bool = False
			self.lastSliceMovedValue: int = 0
			# cities stats values
			self._citiesFoundValue: int = 0
			self._citiesLostValue: int = 0
			self._numberOfPlotsBoughtValue: int = 0
			self._settledContinents = []
			self.builtCityNames = []
			self.originalCapitalLocationValue = constants.invalidHexPoint
			self._startingPositionValue: Optional[HexPoint] = None
			self.lostCapitalValue: bool = False
			self.conquerorValue = None
			self.combatThisTurnValue: bool = False
			self._cramped: bool = False

			self.government = PlayerGovernment(player=self)
			self.religion = PlayerReligion(player=self)
			self.tradeRoutes = PlayerTradeRoutes(player=self)
			self.cityConnections = CityConnections(player=self)
			self.greatPeople = PlayerGreatPeople(player=self)
			self.treasury = PlayerTreasury(player=self)
			self.tourism = PlayerTourism(player=self)
			self.governors = PlayerGovernors(player=self)
			self.operations = PlayerOperations(player=self)
			self.armies = PlayerArmies(player=self)
			self.envoys = PlayerEnvoys(player=self)

			self._currentEraValue: EraType = EraType.ancient
			self._currentAgeValue: AgeType = AgeType.normal
			self._currentDedicationsValue: [DedicationType] = []
			self._numberOfDarkAgesValue: int = 0
			self._numberOfGoldenAgesValue: int = 0
			self._totalImprovementsBuilt: int = 0
			self._trainedSettlersValue: int = 0
			self._tradingCapacityValue: int = 0
			self._boostExoplanetExpeditionValue: int = 0
			self._discoveredNaturalWonders: [FeatureType] = []
			self._discoveredBarbarianCampLocations: [HexPoint] = []
			self._area = HexArea([])
			self._faithEarned = 0.0
			self._cultureEarned = 0.0
			self._resourceInventory = WeightedBaseList()
			self._resourceStockpile = WeightedBaseList()
			self._resourceMaxStockpile = WeightedBaseList()
			self._suzerainValue: Optional[LeaderType] = None
			self._oldQuests: [CityStateQuest] = []
			self._quests: [CityStateQuest] = []
			self._influencePointsValue: int = 0
			self._canChangeGovernmentValue: bool = False
			self._faithPurchaseType: FaithPurchaseType = FaithPurchaseType.noAutomaticFaithPurchase
			self._greatPersonExpendGold = 0
			self._establishedTradingPosts = []
		elif isinstance(leader, dict):
			player_dict: dict = leader
			self.leader = player_dict['leader']
			self.cityState = player_dict['cityState']
			self.human = player_dict['human']

			# ais
			self.grandStrategyAI = GrandStrategyAI(player=self)  # fixme
			self.economicAI = EconomicAI(player=self)  # fixme
			self.militaryAI = MilitaryAI(player=self)  # fixme
			self.tacticalAI = TacticalAI(player=self)  # fixme
			self.diplomacyAI = DiplomaticAI(player=self)  # fixme
			self.homelandAI = HomelandAI(player=self)  # fixme
			self.builderTaskingAI = BuilderTaskingAI(player=self)  # fixme
			self.citySpecializationAI = CitySpecializationAI(player=self)  # fixme
			self.dangerPlotsAI = DangerPlotsAI(player=self)  # fixme
			self.minorCivAI = MinorCivAI(player=self)  # fixme
			self.religionAI = ReligionAI(player=self)  # fixme
			self.wonderProductionAI = None  # fixme
			self.dealAI = DealAI(player=self)  # fixme
			self.leagueAI = LeagueAI(player=self)  # fixme

			self.notifications = Notifications(self)  # fixme
			self.diplomacyRequests = DiplomacyRequests(player=self)  # fixme

			# special
			self.techs = PlayerTechs(self)  # fixme
			self.civics = PlayerCivics(self)  # fixme
			self.moments = PlayerMoments(self)  # fixme
			self._traits = PlayerTraits(self)  # fixme
			self.personalityFlavors = Flavors()  # fixme

			# state values
			self.isAliveVal = player_dict['isAliveVal']
			self.turnActive = player_dict['turnActive']
			self._checkedOperations = player_dict['_checkedOperations']
			self.finishTurnButtonPressedValue = player_dict['finishTurnButtonPressedValue']
			self.processedAutoMovesValue = player_dict['processedAutoMovesValue']
			self.autoMovesValue = player_dict['autoMovesValue']
			self.endTurnValue = player_dict['endTurnValue']
			self.lastSliceMovedValue = player_dict['lastSliceMovedValue']
			# cities stats values
			self._citiesFoundValue = player_dict['_citiesFoundValue']
			self._citiesLostValue = player_dict['_citiesLostValue']
			self._numberOfPlotsBoughtValue = player_dict['_numberOfPlotsBoughtValue']
			self._settledContinents = player_dict['_settledContinents']
			self.builtCityNames = player_dict['builtCityNames']
			self.originalCapitalLocationValue = player_dict['originalCapitalLocationValue']
			self._startingPositionValue = player_dict['_startingPositionValue']
			self.lostCapitalValue = player_dict['lostCapitalValue']
			self.conquerorValue = player_dict['conquerorValue']
			self.combatThisTurnValue = player_dict['combatThisTurnValue']
			self._cramped = player_dict['_cramped']

			self.government = PlayerGovernment(player_dict['government'])
			self.government.player = self
			self.religion = PlayerReligion(player=self)  # fixme
			self.tradeRoutes = PlayerTradeRoutes(player=self)  # fixme
			self.cityConnections = CityConnections(player=self)  # fixme
			self.greatPeople = PlayerGreatPeople(player=self)  # fixme
			self.treasury = PlayerTreasury(player=self)  # fixme
			self.tourism = PlayerTourism(player=self)  # fixme
			self.governors = PlayerGovernors(player=self)  # fixme
			self.operations = PlayerOperations(player=self)  # fixme
			self.armies = PlayerArmies(player=self)  # fixme
			self.envoys = PlayerEnvoys(player=self)  # fixme

			self._currentEraValue = player_dict['_currentEraValue']
			self._currentAgeValue = player_dict['_currentAgeValue']
			self._currentDedicationsValue = player_dict['_currentDedicationsValue']
			self._numberOfDarkAgesValue = player_dict['_numberOfDarkAgesValue']
			self._numberOfGoldenAgesValue = player_dict['_numberOfGoldenAgesValue']
			self._totalImprovementsBuilt = player_dict['_totalImprovementsBuilt']
			self._trainedSettlersValue = player_dict['_trainedSettlersValue']
			self._tradingCapacityValue = player_dict['_tradingCapacityValue']
			self._boostExoplanetExpeditionValue = player_dict['_boostExoplanetExpeditionValue']
			self._discoveredNaturalWonders = player_dict['_discoveredNaturalWonders']
			self._discoveredBarbarianCampLocations = player_dict['_discoveredBarbarianCampLocations']
			self._area = HexArea(player_dict['_area'])
			self._faithEarned = player_dict['_faithEarned']
			self._cultureEarned = player_dict['_cultureEarned']
			self._resourceInventory = WeightedBaseList()  # fixme
			self._resourceStockpile = WeightedBaseList()  # fixme
			self._resourceMaxStockpile = WeightedBaseList()  # fixme
			self._suzerainValue: Optional[LeaderType] = None  # fixme
			self._oldQuests: [CityStateQuest] = []  # fixme
			self._quests: [CityStateQuest] = []  # fixme
			self._influencePointsValue: int = 0  # fixme
			self._canChangeGovernmentValue: bool = False  # fixme
			self._faithPurchaseType: FaithPurchaseType = FaithPurchaseType.noAutomaticFaithPurchase  # fixme
			self._greatPersonExpendGold = 0  # fixme
			self._establishedTradingPosts = []  # fixme
		else:
			raise Exception('Invalid combination of parameters')

	def initialize(self):
		self.setupFlavors()

		self.wonderProductionAI = WonderProductionAI(player=self)

	def __repr__(self):
		if self.isBarbarian():
			return f'Player({self.leader}, {self.leader.civilization()}, Barbarian)'
		elif self.human:
			return f'Player({self.leader}, {self.leader.civilization()}, Human)'
		elif self.isCityState():
			return f'Player(CityState, {self.cityState}, CityState)'
		else:
			return f'Player({self.leader}, {self.leader.civilization()}, AI)'

	def __hash__(self):
		return hash((self.leader, self.cityState))

	def doTurn(self, simulation):
		if self.startingPoint() is None:
			firstUnit = firstOrNone(simulation.unitsOf(self))
			if firstUnit is not None:
				self.updateStartingPoint(firstUnit.location)

		self.dangerPlotsAI.updateDanger(False, False, simulation)
		self.doEurekas(simulation)
		self.doResourceStockpile(simulation)
		self.doSpaceRace(simulation)
		self.tourism.doTurn(simulation)

		# inform ui about new notifications
		self.notifications.update(simulation)

		hasActiveDiploRequest = False
		if self.isAlive():
			if not self.isBarbarian() and not self.isFreeCity() and not self.isCityState():

				# self.doUnitDiversity()
				self.doUpdateCramped(simulation)
				# DoUpdateUprisings();
				# DoUpdateCityRevolts();
				# CalculateNetHappiness();
				# SetBestWonderCities();
				self.doUpdateTradeRouteCapacity(simulation)

				self.grandStrategyAI.doTurn(simulation)

				# Do diplomacy for toward everyone
				self.diplomacyAI.doTurn(simulation)
				self.governors.doTurn(simulation)

				if self.isHuman():
					hasActiveDiploRequest = self.hasActiveDiploRequestWithHuman(simulation)

			if self.isCityState():
				self.doQuests(simulation)

		if (hasActiveDiploRequest or simulation.userInterface.isShown(ScreenType.diplomatic)) and not self.isHuman():
			simulation.setWaitingForBlockingInputOf(self)
		else:
			self.doTurnPostDiplomacy(simulation)

	def area(self) -> HexArea:
		return self._area

	def startingPoint(self) -> Optional[HexPoint]:
		return self._startingPositionValue

	def updateStartingPoint(self, value: Optional[HexPoint]):
		if value is not None and not isinstance(value, HexPoint):
			raise Exception(f'value must be None or HexPoint but is {type(HexPoint)}')

		self._startingPositionValue = value

	def doTurnPostDiplomacy(self, simulation):
		if self.isAlive():
			if not self.isBarbarian() and not self.isFreeCity():
				self.economicAI.doTurn(simulation)
				self.militaryAI.doTurn(simulation)
				self.citySpecializationAI.doTurn(simulation)

		# Golden Age
		self.doProcessAge(simulation)

		self.doUpdateWarWeariness(simulation)

		# balance amenities
		self.doCityAmenities(simulation)

		# Do turn for all Cities
		for city in simulation.citiesOf(self):
			city.doTurn(simulation)

		# Gold GetTreasury()->DoGold();
		self.treasury.doTurn(simulation)

		# Culture / Civics
		self.doCivics(simulation)

		# Science / Techs
		self.doTechs(simulation)  # doResearch

		# government
		self.doGovernment(simulation)

		# faith / religion
		self.doFaith(simulation)

		# great people
		self.doGreatPeople(simulation)

		self.doTurnPost(simulation)

		return

	def isFreeCity(self) -> bool:
		return False

	def traits(self) -> PlayerTraits:
		return self._traits

	def doTurnUnits(self, simulation):
		# Start: OPERATIONAL AI UNIT PROCESSING
		self.operations.doDelayedDeath(simulation)
		self.armies.doDelayedDeath()

		for unit in simulation.unitsOf(self):
			unit.doDelayedDeath(simulation)

		self.operations.doTurn(simulation)
		self.operations.doDelayedDeath(simulation)

		self.armies.doTurn(simulation)

		# Homeland AI
		# self.homelandAI?.doTurn( simulation) is empty

		# Start: old unit AI processing
		for passValue in range(4):
			for loopUnit in simulation.unitsOf(self):

				if loopUnit.domain() == UnitDomainType.air:
					if passValue == 1:
						loopUnit.doTurn(simulation)
				elif loopUnit.domain() == UnitDomainType.sea:
					if passValue == 2:
						loopUnit.doTurn(simulation)
				elif loopUnit.domain() == UnitDomainType.land:
					if passValue == 3:
						loopUnit.doTurn(simulation)
				elif loopUnit.domain() == UnitDomainType.immobile:
					if passValue == 0:
						loopUnit.doTurn(simulation)
				elif loopUnit.domain() == UnitDomainType.none:
					raise Exception("Unit with no Domain")

		self.doTurnUnitsPost(simulation)  # AI_doTurnUnitsPost();

	def doTurnUnitsPost(self, simulation):
		if self.isHuman():
			return

		for loopUnit in simulation.unitsOf(self):
			loopUnit.doPromotion(simulation)

		return

	def name(self) -> str:
		return self.leader.title()

	def isAtWar(self) -> bool:
		"""is player at war with any player/leader?"""
		return self.diplomacyAI.isAtWar()

	def isAtWarWith(self, otherPlayer) -> bool:
		return self.diplomacyAI.isAtWarWith(otherPlayer)

	def isAlliedWith(self, otherPlayer) -> bool:
		return self.diplomacyAI.isAlliedWith(otherPlayer)

	def valueOfStrategyAndPersonalityFlavor(self, flavorType: FlavorType) -> int:
		activeStrategy = self.grandStrategyAI.activeStrategy

		if activeStrategy is None:
			return self.personalityFlavors.value(flavorType)

		return self.personalityFlavors.value(flavorType) + activeStrategy.flavor(flavorType)

	def valueOfPersonalityFlavor(self, flavor: FlavorType) -> int:
		return self.leader.flavor(flavor)

	def valueOfPersonalityIndividualFlavor(self, flavorType: FlavorType) -> int:
		return self.personalityFlavors.value(flavorType)

	def isHuman(self) -> bool:
		return self.human

	def isBarbarian(self) -> bool:
		return self.leader == LeaderType.barbar

	def hasMetWith(self, otherPlayer) -> bool:
		if self.isBarbarian() or otherPlayer.isBarbarian():
			return False

		return self.diplomacyAI.hasMetWith(otherPlayer)

	def canFinishTurn(self) -> bool:
		if not self.isHuman():
			return False

		if not self.isAlive():
			return False

		if not self.isActive():
			return False

		if not self.hasProcessedAutoMoves():
			return False

		if self.blockingNotification() is not None:
			return False

		return True

	def turnFinished(self) -> bool:
		return self.finishTurnButtonPressedValue

	def finishTurn(self):
		self.finishTurnButtonPressedValue = True

	def resetFinishTurnButtonPressed(self):
		self.finishTurnButtonPressedValue = False

	def lastSliceMoved(self) -> int:
		return self.lastSliceMovedValue

	def setLastSliceMoved(self, value: int):
		self.lastSliceMovedValue = value

	def isTurnActive(self) -> bool:
		return self.turnActive

	def __eq__(self, other):
		if isinstance(other, Player):
			if self.leader == LeaderType.cityState and other.leader == LeaderType.cityState:
				return self.cityState == other.cityState

			return self.leader == other.leader

		raise Exception(f'Wrong type to compare: {type(other)}')

	def __str__(self):
		return f'Player {self.leader}'

	def isActive(self) -> bool:
		return self.turnActive

	def numberOfCitiesFounded(self) -> int:
		return self._citiesFoundValue

	def science(self, simulation) -> float:
		value: YieldValues = YieldValues(value=0.0, percentage=1.0)

		# Science from our Cities
		value += self.scienceFromCities(simulation)
		value += self.scienceFromCityStates(simulation)

		return max(value.calc(), 0)

	def scienceFromCities(self, simulation) -> YieldValues:
		scienceVal: YieldValues = YieldValues(value=0.0, percentage=0.0)

		for city in simulation.citiesOf(player=self):
			scienceVal += city.sciencePerTurn(simulation)

		return scienceVal

	def scienceFromCityStates(self, simulation) -> YieldValues:
		scienceVal = 0.0
		scienceModifier = 0.0

		# internationalSpaceAgency - 5% Science per City-State you are the Suzerain of.
		if self.government.hasCard(PolicyCardType.internationalSpaceAgency):
			numberOfCityStatesMet: int = 0
			for cityState in self.metCityStates(simulation):
				if self.isSuzerainOf(cityState, simulation):
					numberOfCityStatesMet += 1

			scienceModifier += 0.05 * float(numberOfCityStatesMet)

		return YieldValues(value=scienceVal, percentage=scienceModifier)

	def culture(self, simulation, consume: bool) -> float:
		value = YieldValues(value=0.0, percentage=1.0)

		# culture from our Cities
		value += self.cultureFromCities(simulation)
		value += self.cultureFromCityStates(simulation)
		value += YieldValues(value=float(self._cultureEarned))
		# ....

		if consume:
			self._cultureEarned = 0

		return value.calc()

	def cultureFromCities(self, simulation) -> YieldValues:
		cultureVal = 0.0

		for city in simulation.citiesOf(self):
			cultureVal += city.culturePerTurn(simulation)

		return YieldValues(value=cultureVal)

	def cultureFromCityStates(self, simulation) -> YieldValues:
		cultureVal = 0.0
		cultureModifier = 0.0

		# antananarivo suzerain bonus
		# Your Civilization gains +2% Culture for each Great Person it has ever earned (up to 30 %).
		if self.isSuzerainOf(CityStateType.antananarivo, simulation):
			numberOfSpawnedGreatPersons: int = self.greatPeople.numberOfSpawnedGreatPersons()
			cultureModifier += min(0.02 * float(numberOfSpawnedGreatPersons), 0.3)

		# collectiveActivism - 5% Culture per City - State you are the Suzerain of.
		if self.government.hasCard(PolicyCardType.collectiveActivism):
			numberOfCityStatesMet: int = 0
			for cityState in self.metCityStates(simulation):
				if self.isSuzerainOf(cityState, simulation):
					numberOfCityStatesMet += 1

			cultureModifier += 0.05 * float(numberOfCityStatesMet)

		return YieldValues(value=cultureVal, percentage=cultureModifier)

	def isAlive(self) -> bool:
		return self.isAliveVal

	def isEverAlive(self) -> bool:
		return True

	def prepareTurn(self, simulation):
		# Barbarians get all Techs that 3 / 4 of alive players get
		if self.isBarbarian():
			# self.doBarbarianTech()
			pass

		# / * for (iI = 0; iI < GC.getNumTechInfos();
		# iI + +)  {
		#     GetTeamTechs()->SetNoTradeTech(((TechTypes)iI), false);
		# }
		#
		# DoTestWarmongerReminder();
		#
		# DoTestSmallAwards(); * /
		self.checkWorldCircumnavigated(simulation)

	def startTurn(self, simulation):
		if self.isTurnActive():
			logging.warning("try to start already active turn")
			return

		if self.isHuman():
			logging.info(f'--- start turn for HUMAN player {self.leader} ---')
		elif self.isBarbarian():
			logging.info("--- start turn for barbarian player ---")
		elif self.leader == LeaderType.cityState:
			logging.info(f'--- start turn for city state {self.cityState.title()} ---')
		elif self.isMajorAI():
			logging.info(f'--- start turn for AI player {self.leader} ---')

		simulation.userInterface.updatePlayer(self)

		self.turnActive = True
		simulation.updateActivePlayer(self)
		self._checkedOperations = False
		self.setEndTurnTo(False, simulation)
		self.setAutoMovesTo(False)

		# ##################################################################
		# TURN IS BEGINNING
		# ##################################################################

		if self.dangerPlotsAI.isDirty():
			self.dangerPlotsAI.updateDanger(False, False, simulation)

		# self.doUnitAttrition()
		self.verifyAlive(simulation)

		self.setAllUnitsUnprocessed(simulation)

		simulation.updateTacticalAnalysisMap(self)

		self.updateTimers(simulation)

		# This block all has things which might change based on city connections changing
		self.cityConnections.doTurn(simulation)
		self.builderTaskingAI.update(simulation)

		if simulation.currentTurn > 0:
			if self.isAlive():
				self.diplomacyRequests.beginTurn(simulation)
				self.doTurn(simulation)
				self.doTurnUnits(simulation)

		if simulation.currentTurn == 1 and simulation.showTutorialInfos():
			if self.isHuman():
				# simulation.userInterface.showPopup(popupType: .tutorialStart(tutorial: simulation.tutorialInfos()))
				pass

	def endTurn(self, simulation):
		if not self.isTurnActive():
			raise Exception("try to end an inactive turn")

		# logging.debug("--- unit animation running: \(gameModel?.userInterface?.animationsAreRunning(for: self.leader)) ---")
		if self.isHuman():
			logging.info(f'--- end turn for HUMAN player {self.leader} ---')
		elif self.isBarbarian():
			logging.info("--- end turn for barbarian player ---")
		elif self.leader == LeaderType.cityState:
			logging.info(f'--- end turn for city state {self.cityState.title()} ---')
		elif self.isMajorAI():
			logging.info(f'--- end turn for AI player {self.leader} ---')

		self.turnActive = False

		# /////////////////////////////////////////////
		# // TURN IS ENDING
		# /////////////////////////////////////////////

		self.doUnitReset(simulation)
		self.setCanChangeGovernmentTo(False)

		self.notifications.cleanUp(simulation)

		self.diplomacyRequests.endTurn()

	def hasProcessedAutoMoves(self) -> bool:
		return self.processedAutoMovesValue

	def setProcessedAutoMovesTo(self, value: bool):
		self.processedAutoMovesValue = value

	def doUnitReset(self, simulation):
		"""Units heal and then get their movement back"""
		for loopUnit in simulation.unitsOf(self):
			# HEAL UNIT?
			if not loopUnit.isEmbarked():
				if not loopUnit.hasMoved(simulation):
					if loopUnit.isHurt():
						loopUnit.doHeal(simulation)

			# Finally(now that healing is done), restore movement points
			loopUnit.resetMoves(simulation)
			# pLoopUnit->SetIgnoreDangerWakeup(false);
			loopUnit.setMadeAttackTo(False)
			# pLoopUnit->setMadeInterception(false);

			if not self.isHuman():
				mission = loopUnit.peekMission()
				if mission is not None:
					if mission.missionType == UnitMissionType.rangedAttack:
						# CvAssertMsg(0, "An AI unit has a combat mission queued at the end of its turn.");
						loopUnit.clearMissions()  # Clear the whole thing, the AI will re-evaluate next turn.

	def setCanChangeGovernmentTo(self, canChangeGovernment: bool):
		self._canChangeGovernmentValue = canChangeGovernment

	def checkWorldCircumnavigated(self, simulation):
		pass

	def updatePlots(self, simulation):
		"""This determines what plots the player has under control"""
		# init
		tmpArea = HexArea([])
		mapSize = simulation.mapSize().size()
		# tmpArea.points.reserveCapacity(mapSize.numberOfTiles())

		for x in range(mapSize.width()):
			for y in range(mapSize.height()):
				pt = HexPoint(x, y)
				tile = simulation.tileAt(pt)

				if tile is not None:
					if tile.hasOwner() and self == tile.owner():
						tmpArea.addPoint(pt)

		self._area = tmpArea

	def setCapitalCity(self, city, simulation):
		if city is None:
			for city in simulation.citiesOf(self):
				city.setIsCapitalTo(False)
		else:
			currentCapitalCity = self.capitalCity(simulation)

			if currentCapitalCity is not None and \
				(currentCapitalCity.location != city.location or currentCapitalCity.name != city.name):

				# Need to set our original capital x, y?
				if self.originalCapitalLocationValue == constants.invalidHexPoint:
					self.originalCapitalLocationValue = city.location

			city.setEverCapitalTo(True)

		return

	def currentAge(self) -> AgeType:
		return self._currentAgeValue

	def hasDedication(self, dedication: DedicationType) -> bool:
		return dedication in self._currentDedicationsValue

	def hasWonder(self, wonderType: Union[WonderType, str], simulation) -> bool:
		if isinstance(wonderType, str):
			wonderType: WonderType = WonderType.fromName(wonderType)

		for city in simulation.citiesOf(self):
			if city.hasWonder(wonderType):
				return True

		return False

	def isSuzerainOf(self, cityState: CityStateType, simulation) -> bool:
		return self.envoys.isSuzerainOf(cityState, simulation)

	def suzerain(self):
		return self._suzerainValue

	def isMajorAI(self) -> bool:
		# return not self.isHuman() and not self.isFreeCity() and not self.isBarbarian() and not self.isCityState()
		return not self.isHuman() and not self.isBarbarian() and not self.isCityState()

	def isCityState(self) -> bool:
		return self.leader == LeaderType.cityState

	def setEndTurnTo(self, value: bool, simulation):
		if not self.isEndTurn() and self.isHuman() and simulation.activePlayer() != self:
			if self.hasBusyUnitOrCity(simulation) or self.hasReadyUnit(simulation):
				return
		elif not self.isHuman():
			if self.hasBusyUnitOrCity(simulation):
				return

		if self.isEndTurn() != value:
			if not self.isTurnActive():
				raise Exception("isTurnActive is expected to be true")

			self.endTurnValue = value

			if self.isEndTurn():
				self.setAutoMovesTo(True)
			else:
				self.setAutoMovesTo(False)
		else:
			# This check is here for the AI.
			# Currently, the setEndTurn(true) never seems to get called for AI players, the auto moves are just
			# set directly
			# Why is this?  It would be great if all players were processed the same.
			if not value and self.isAutoMoves():
				self.setAutoMovesTo(False)

	def isEndTurn(self) -> bool:
		return self.endTurnValue

	def hasBusyUnitOrCity(self, simulation) -> bool:
		if not self.isHuman() and not self._checkedOperations:
			return True

		if self.hasBusyUnit(simulation):
			return True

		return self.hasBusyCity(simulation)

	def hasBusyUnit(self, simulation) -> bool:
		for unit in simulation.unitsOf(self):
			if unit.isBusy():
				return True

		return False

	def hasBusyCity(self, simulation) -> bool:
		for city in simulation.citiesOf(self):
			if city.isBusy():
				return True

		return False

	def isAutoMoves(self) -> bool:
		return self.autoMovesValue

	def setAutoMovesTo(self, value: bool):
		if self.autoMovesValue != value:
			self.autoMovesValue = value
			self.processedAutoMovesValue = False

	def hasReadyUnit(self, simulation) -> bool:
		activePlayer = simulation.activePlayer()

		for loopUnit in simulation.unitsOf(activePlayer):
			if loopUnit.readyToMove() and not loopUnit.isDelayedDeath():
				return True

		return False

	def countReadyUnits(self, simulation) -> int:
		rtnValue = 0

		for loopUnit in simulation.unitsOf(self):
			if loopUnit.readyToMove() and not loopUnit.isDelayedDeath():
				rtnValue += 1

		return rtnValue

	def hasUnitsThatNeedAIUpdate(self, simulation) -> bool:
		for loopUnit in simulation.unitsOf(self):
			if not loopUnit.processedInTurn() and (loopUnit.isAutomated() and loopUnit.task() != UnitTaskType.none and loopUnit.canMove()):
				return True

		return False

	def unitUpdate(self, simulation):
		self._checkedOperations = True

		if self.dangerPlotsAI.isDirty():
			self.dangerPlotsAI.updateDanger(False, False, simulation)

		# CvPlayerAI::AI_unitUpdate()
		# Now it's the homeland AI's turn.
		if self.isHuman():
			self.homelandAI.doTurn(simulation)
		else:
			# Now let the tactical AI run.  Putting it after the operations update allows units who have
			# just been handed off to the tactical AI to get a move in the same turn they switch between
			self.tacticalAI.doTurn(simulation)
			self.homelandAI.doTurn(simulation)

	def verifyAlive(self, simulation):
		if self.isAlive():
			if not self.isBarbarian():  # and not self.isFreeCity():
				if self.numberOfCities(simulation) == 0 and self.numberOfUnits(simulation) == 0:
					self.setAliveTo(False, simulation)
		else:
			# if dead but has received units / cities - revive
			if self.numberOfUnits(simulation) > 0 or self.numberOfCities(simulation) > 0:
				self.setAliveTo(True, simulation)

	def numberOfCities(self, simulation) -> int:
		return len(simulation.citiesOf(player=self))

	def numberOfUnits(self, simulation) -> int:
		return len(simulation.unitsOf(player=self))

	def numberOfUnitsOfType(self, unitType: UnitType, simulation) -> int:
		units = 0

		for unit in simulation.unitsOf(player=self):
			if unit.unitType == unitType:
				units += 1

		return units

	def numberOfUnitsOfTask(self, unitTaskType: UnitTaskType, simulation) -> int:
		units = 0

		for unit in simulation.unitsOf(player=self):
			if unit.task() == unitTaskType:
				units += 1

		return units

	def setAliveTo(self, alive, simulation):
		if self.isAliveVal != alive:
			self.isAliveVal = alive

			if not alive:
				# cleanup
				# killUnits();
				# killCities();
				simulation.gameDeals.doCancelAllDealsOf(self, simulation)
				simulation.addReplayEvent(ReplayEventType.playerKilled, "TXT_KEY_NOTIFICATION_PLAYER_KILLED", invalidHexPoint)

				if self.isHuman():
					simulation.setGameStateTo(GameState.over)

				self.endTurn(simulation)

	def setAllUnitsUnprocessed(self, simulation):
		for unit in simulation.unitsOf(player=self):
			unit.setTurnProcessedTo(False)

	def updateTimers(self, simulation):
		for unit in simulation.unitsOf(player=self):
			unit.updateMission(simulation)
			unit.doDelayedDeath(simulation)

		self.diplomacyAI.update(simulation)

	def updateNotifications(self, simulation):
		self.notifications.update(simulation)

	def hasActiveDiplomacyRequests(self) -> bool:
		return False

	def doUpdateTradeRouteCapacity(self, simulation):
		numberOfTradingCapacity = 0

		# The Foreign Trade Civic (one of the earliest of the Ancient Era) grants a Trading Capacity of one,
		# meaning that your empire can have one Trade Route at a time.
		if self.civics.hasCivic(CivicType.foreignTrade):
			numberOfTradingCapacity += 1
		else:
			self._tradingCapacityValue = 0
			return

		if self.leader.civilization().ability() == CivilizationAbility.satrapies and \
			self.civics.hasCivic(CivicType.politicalPhilosophy):
			# Gains + 1 Trade Route capacity with Political Philosophy.
			numberOfTradingCapacity += 1

		for loopCity in simulation.citiesOf(self):

			# Each city with a Commercial Hub or a Harbor ( or, from Rise and Fall onwards, a Market or a Lighthouse)
			# increases a civilization's Trading Capacity by one. These bonuses are not cumulative: a city with both
			# a Commercial Hub/Market and a Harbor/Lighthouse adds only one Trading Capacity, not two.
			if loopCity.hasDistrict(DistrictType.harbor) or \
				loopCity.hasDistrict(DistrictType.commercialHub) or \
				loopCity.hasBuilding(BuildingType.market) or \
				loopCity.hasBuilding(BuildingType.lighthouse):

				numberOfTradingCapacity += 1

			# The effects of the Colossus and Great Zimbabwe wonders increase Trading Capacity by one.
			if loopCity.hasWonder(WonderType.colossus) or loopCity.hasWonder(WonderType.greatZimbabwe):
				# +1 Trade Route capacity
				numberOfTradingCapacity += 1

		if self.government.currentGovernment() == GovernmentType.merchantRepublic:
			numberOfTradingCapacity += 2

		if self.hasRetired(GreatPerson.zhangQian):
			# Increases Trade Route capacity by 1.
			numberOfTradingCapacity += 1

		if self._tradingCapacityValue != numberOfTradingCapacity:
			if self._tradingCapacityValue < numberOfTradingCapacity:
				if self.isHuman():
					self.notifications.addNotification(NotificationType.tradeRouteCapacityIncreased)

			self._tradingCapacityValue = numberOfTradingCapacity

		return

	def envoyEffects(self, simulation):
		return self.envoys.envoyEffects(simulation)

	def doFirstContactWith(self, otherPlayer, simulation):
		self.diplomacyAI.doFirstContactWith(otherPlayer, simulation)
		otherPlayer.diplomacyAI.doFirstContactWith(self, simulation)

		if otherPlayer.isMajorAI() or otherPlayer.isHuman():
			# moment
			self.addMoment(MomentType.metNewCivilization, civilization=otherPlayer.leader.civilization(), simulation=simulation)

		# update eurekas
		if not self.techs.eurekaTriggeredFor(TechType.writing):
			self.techs.triggerEurekaFor(TechType.writing, simulation)

		if self.isCityState():
			self.doQuests(simulation)

		if otherPlayer.isCityState():
			otherPlayer.doQuests(simulation)

		return

	def addMoment(self, momentType: MomentType, civilization: Optional[CivilizationType] = None,
				  cityName: Optional[str] = None, continentName: Optional[str] = None,
				  eraType: Optional[EraType] = None, naturalWonder: Optional[FeatureType] = None,
				  dedication: Optional[DedicationType] = None, wonder: Optional[WonderType] = None,
	              cityState: Optional[CityStateType] = None, pantheon: Optional[PantheonType] = None,
				  simulation = None):
		if simulation is None:
			raise Exception('simulation not provided')

		if not momentType.minEra() <= self._currentEraValue <= momentType.maxEra():
			return

		self.moments.addMomentOf(momentType, simulation.currentTurn, civilization=civilization,
								 cityName=cityName, continentName=continentName, eraType=eraType,
								 naturalWonder=naturalWonder, dedication=dedication, wonder=wonder,
								 cityState=cityState, pantheon=pantheon)

		# also show a notification, when the moment brings era score
		if momentType.eraScore() > 0:
			if self.isHuman():
				self.notifications.addNotification(NotificationType.momentAdded, momentType=momentType)

	def hasMoment(self, momentType: MomentType, civilization: Optional[CivilizationType] = None,
				  eraType: Optional[EraType] = None, cityName: Optional[str] = None,
				  continentName: Optional[str] = None, naturalWonder: Optional[FeatureType] = None,
				  dedication: Optional[DedicationType] = None) -> bool:
		return self.moments.hasMoment(momentType=momentType, civilization=civilization, eraType=eraType,
									  cityName=cityName, continentName=continentName, naturalWonder=naturalWonder,
									  dedication=dedication)

	def militaryMight(self, simulation) -> int:
		might = 0.0

		# Current combat strength
		for unit in simulation.unitsOf(player=self):
			might += float(unit.power())

		# Simplistic increase based on player's gold
		# 500 gold will increase might by 22%, 2000 by 45%, 8000 gold by 90%
		treasureValue = max(0.0, self.treasury.value())
		goldMultiplier = 1.0 + math.sqrt(treasureValue) / 100.0
		if goldMultiplier > 2.0:
			goldMultiplier = 2.0

		might *= goldMultiplier

		return int(might)

	def doEurekas(self, simulation):
		if not self.civics.inspirationTriggeredFor(CivicType.earlyEmpire):
			if self.population(simulation) >= 6:
				self.civics.triggerInspirationFor(CivicType.earlyEmpire, simulation)

	def population(self, simulation) -> int:
		populationVal = 0

		for city in simulation.citiesOf(self):
			populationVal += city.population()

		return populationVal

	def doResourceStockpile(self, simulation):
		# check max stockpile
		for resource in ResourceType.strategic():
			amount: float = self.BaseStockPileAmount

			# Strategic Resource stockpiles increased by 10
			numArmories = self.numberOfBuildingsOfType(BuildingType.armory, simulation)
			amount += 10.0 * float(numArmories)

			self._resourceMaxStockpile.setWeight(amount, resource)

		for resource in ResourceType.strategic():
			newResource = self.numberOfAvailableResource(resource)

			# equestrianOrders - All improved Horses and Iron resources yield 1 additional resource per turn.
			if self.government.hasCard(PolicyCardType.equestrianOrders) and newResource > 0:
				if resource == ResourceType.horses or resource == ResourceType.iron:
					newResource += 1

			for governorType in list(GovernorType):
				governor = self.governors.governor(governorType)
				if governor is not None:
					# defenseLogistics - Accumulating Strategic resources gain an additional +1 per turn.
					if governor.hasTitle(GovernorTitleType.defenseLogistics):
						newResource += 1

			self._resourceStockpile.addWeight(newResource, resource)

			# limit
			maxStockpileValue = self._resourceMaxStockpile.weight(resource)
			if self._resourceStockpile.weight(resource) > maxStockpileValue:
				self._resourceStockpile.setWeight(maxStockpileValue, resource)

		return

	def doSpaceRace(self, simulation):
		for city in simulation.citiesOf(self):
			if city.hasProject(ProjectType.terrestrialLaserStation):
				self._boostExoplanetExpeditionValue += 1

		return

	def doUpdateCramped(self, simulation):
		"""Determines if the player is cramped in his current area.  Not a perfect algorithm, as it will double-count
		Plots shared by different Cities, but it should be good enough"""
		totalPlotsNearby: int = 0
		usablePlotsNearby: int = 0

		range: int = 5  # CRAMPED_RANGE_FROM_CITY

		for loopCity in simulation.citiesOf(self):
			for areaPoint in loopCity.location.areaWithRadius(range):
				areaPlot = simulation.tileAt(areaPoint)

				if areaPlot is None:
					continue

				# Plot not owned by me
				if not areaPlot.hasOwner() or areaPlot.owner() != self:
					totalPlotsNearby += 1

					# A "good" unowned Plot
					if (not areaPlot.hasOwner() and not areaPlot.isImpassable(UnitMovementType.walk) and
					    not areaPlot.feature() == FeatureType.mountains and not areaPlot.isWater()):
						usablePlotsNearby += 1

		if totalPlotsNearby > 0:
			if 100 * usablePlotsNearby / totalPlotsNearby <= 25:  # CRAMPED_USABLE_PLOT_PERCENT
				self._cramped = True
			else:
				self._cramped = False

		return

	def hasActiveDiploRequestWithHuman(self, simulation) -> bool:
		return DiplomacyRequests.hasActiveDiploRequestWithHuman(self, simulation)

	def doProcessAge(self, simulation):
		pass

	def doUpdateWarWeariness(self, simulation):
		pass

	def doCityAmenities(self, simulation):
		pass

	def doCivics(self, simulation):
		if self.isBarbarian():
			return

		cultureVal = self.culture(simulation, consume=True)
		self.civics.addCulture(cultureVal)

		self.civics.checkCultureProgress(simulation)

	def doTechs(self, simulation):
		"""How long until a RA with a player takes effect"""
		if self.isBarbarian():
			return

		scienceVal = self.science(simulation)
		self.techs.addScience(scienceVal)

		self.techs.checkScienceProgress(simulation)

	def doGovernment(self, simulation):
		# update influence points
		currentGovernmentType = self.government.currentGovernment()
		if currentGovernmentType is not None:
			self._influencePointsValue += currentGovernmentType.influencePointsPerTurn()

			if self._influencePointsValue > currentGovernmentType.envoyPerInfluencePoints():
				self.changeUnassignedEnvoysBy(currentGovernmentType.envoysFromInfluencePoints())
				self._influencePointsValue = 0

		if self.canChangeGovernment():
			if self.isHuman():
				self.notifications.addNotification(NotificationType.canChangeGovernment)
			else:
				self.government.chooseBestGovernment(simulation)

		if not self.government.hasPolicyCardsFilled(simulation) and self.capitalCity(simulation) is not None:
			if self.isHuman():
				self.notifications.addNotification(NotificationType.policiesNeeded)
			else:
				self.government.fillPolicyCards(simulation)

	def doFaith(self, simulation):
		"""Religious activities at the start of a player's turn"""
		faithAtStart = self.religion.faith()
		faithPerTurn = self.faith(reset=True, simulation=simulation)

		if faithPerTurn > 0:
			self.religion.changeFaith(faithPerTurn)

		# If just now can afford missionary, add a notification
		sendFaithPurchaseNotification = self.isHuman() and self.faithPurchaseType() == FaithPurchaseType.noAutomaticFaithPurchase

		if sendFaithPurchaseNotification:
			couldAtStartAffordFaithPurchase = self.religion.canAffordFaithPurchase(int(faithAtStart), simulation)
			canNowAffordFaithPurchase = self.religion.canAffordFaithPurchase(int(self.religion.faith()), simulation)  # faith has been updated

			sendFaithPurchaseNotification = not couldAtStartAffordFaithPurchase and canNowAffordFaithPurchase

		if sendFaithPurchaseNotification:
			if self.isHuman():
				simulation.userInterface.showPopup(PopupType.religionCanBuyMissionary)

		# Check for pantheon or great prophet spawning (now restricted - so must occur before Industrial era)
		if self.religion.faith() > 0 and self.currentEra() <= EraType.renaissance:
			if self.religion.canFoundPantheon(checkFaithTotal=True, simulation=simulation) == PantheonFoundingType.okay:
				# Create the pantheon
				if self.isHuman():
					# If the player is human then a net message will be received which will pick the pantheon.
					# You have enough faith to found a pantheon!
					self.notifications.addNotification(NotificationType.canFoundPantheon)
				else:
					pantheonType: PantheonType = self.religionAI.choosePantheonType(simulation)
					self.religion.foundPantheon(pantheonType, simulation)
					simulation.foundPantheonBy(self, pantheonType)

		# Pick a Reformation belief?
		# / *ReligionTypes
		# eReligionCreated = GetFounderBenefitsReligion(ePlayer);
		# if (eReligionCreated > RELIGION_PANTHEON & & !HasAddedReformationBelief(ePlayer) & & (
		# kPlayer.GetPlayerPolicies()->HasPolicyGrantingReformationBelief() | | kPlayer.IsReformation()))
		# {
		# if (!kPlayer.isHuman())
		# {
		# 	BeliefTypes
		# eReformationBelief = kPlayer.GetReligionAI()->ChooseReformationBelief(ePlayer, eReligionCreated);
		# AddReformationBelief(ePlayer, eReligionCreated, eReformationBelief);
		# }
		# else
		# {
		# 	CvNotifications * pNotifications;
		# pNotifications = kPlayer.GetNotifications();
		# if (pNotifications)
		# {
		# CvString strBuffer = GetLocalizedText("TXT_KEY_NOTIFICATION_ADD_REFORMATION_BELIEF");
		# CvString strSummary = GetLocalizedText("TXT_KEY_NOTIFICATION_SUMMARY_ADD_REFORMATION_BELIEF");
		# pNotifications->Add(NOTIFICATION_ADD_REFORMATION_BELIEF, strBuffer, strSummary, -1, -1, -1);
		# }
		# }
		# } * /

		# Automatic faith purchases?
		selectionStillValid: bool = True
		religionType: ReligionType = self.religionAI.religionToSpread()
		purchaseType = self.faithPurchaseType()

		if purchaseType == FaithPurchaseType.saveForProphet:
			raise Exception("FAITH_PURCHASE_SAVE_PROPHET")
			# 		/ * if (eReligion <= RELIGION_PANTHEON & & GetNumReligionsStillToFound() <= 0 & &
			# 		        !kPlayer.GetPlayerTraits()->IsAlwaysReligion())
			# {
			# 	UnitTypes
			# eProphetType = kPlayer.GetSpecificUnitType("UNITCLASS_PROPHET", true);
			# szItemName = GetLocalizedText("TXT_KEY_RO_AUTO_FAITH_PROPHET_PARAM",
			#                               GC.getUnitInfo(eProphetType)->GetDescription());
			# bSelectionStillValid = false;
			# }
			# else if (kPlayer.GetCurrentEra() >= GetFaithPurchaseGreatPeopleEra( & kPlayer))
			# {
			# UnitTypes eProphetType = kPlayer.GetSpecificUnitType("UNITCLASS_PROPHET", true);
			# szItemName = GetLocalizedText("TXT_KEY_RO_AUTO_FAITH_PROPHET_PARAM", GC.getUnitInfo(eProphetType)->GetDescription());
			#
			# bSelectionStillValid = false;
			# }
			# break; * /
		elif purchaseType == FaithPurchaseType.purchaseUnit:
			raise Exception("FAITH_PURCHASE_UNIT")
			# / *UnitTypes
			# eUnit = (UnitTypes)
			# kPlayer.GetFaithPurchaseIndex();
			# CvUnitEntry * pkUnit = GC.getUnitInfo(eUnit);
			# if (pkUnit)
			# 	{
			# 		szItemName = pkUnit->GetDescriptionKey();
			# 	}
			#
			# 	if (
			# 	!kPlayer.IsCanPurchaseAnyCity(false, false/ * Don't worry about faith balance */, eUnit, NO_BUILDING, YIELD_FAITH))
			# 	{
			# 	bSelectionStillValid = false;
			# 	}
			# 	else
			# 	{
			# 	if (kPlayer.IsCanPurchaseAnyCity(true, true/ * Check faith balance * /, eUnit, NO_BUILDING, YIELD_FAITH))
			# 	{
			# 	CvCity * pCity = CvReligionAIHelpers::
			# 		GetBestCityFaithUnitPurchase(kPlayer, eUnit, eReligion);
			# 	if (pCity)
			# 	{
			# 	pCity->Purchase(eUnit, NO_BUILDING, NO_PROJECT, YIELD_FAITH);
			#
			# 	CvNotifications * pNotifications = kPlayer.GetNotifications();
			# 	if (pNotifications)
			# 	{
			# 	CvString strBuffer = GetLocalizedText("TXT_KEY_NOTIFICATION_AUTOMATIC_FAITH_PURCHASE", szItemName, pCity->getNameKey());
			# 	CvString strSummary = GetLocalizedText("TXT_KEY_NOTIFICATION_SUMMARY_AUTOMATIC_FAITH_PURCHASE");
			# 	pNotifications->Add(NOTIFICATION_CAN_BUILD_MISSIONARY, strBuffer, strSummary, pCity->getX(), pCity->getY(), -1);
			# 	}
			# 	}
			# 	else
			# 	{
			# 	bSelectionStillValid = false;
			# 	}
			# 	}
			# 	} * /

		elif purchaseType == FaithPurchaseType.purchaseBuilding:
			raise Exception("FAITH_PURCHASE_BUILDING")
			# 	/ * BuildingTypes
			# eBuilding = (BuildingTypes)
			# kPlayer.GetFaithPurchaseIndex();
			# CvBuildingEntry * pkBuilding = GC.getBuildingInfo(eBuilding);
			# if (pkBuilding)
			# {
			# szItemName = pkBuilding->GetDescriptionKey();
			# }
			#
			# if (!kPlayer.IsCanPurchaseAnyCity(false, false, NO_UNIT, eBuilding, YIELD_FAITH))
			# {
			# bSelectionStillValid = false;
			# }
			# else
			# {
			# if (kPlayer.IsCanPurchaseAnyCity(true, true/ * Check faith balance * /, NO_UNIT, eBuilding, YIELD_FAITH))
			# {
			# CvCity * pCity = CvReligionAIHelpers::
			# 	GetBestCityFaithBuildingPurchase(kPlayer, eBuilding, eReligion);
			# if (pCity)
			# {
			# pCity->Purchase(NO_UNIT, eBuilding, NO_PROJECT, YIELD_FAITH);
			#
			# CvNotifications * pNotifications = kPlayer.GetNotifications();
			# if (pNotifications)
			# {
			# CvString strBuffer = GetLocalizedText("TXT_KEY_NOTIFICATION_AUTOMATIC_FAITH_PURCHASE", szItemName, pCity->getNameKey());
			# CvString strSummary = GetLocalizedText("TXT_KEY_NOTIFICATION_SUMMARY_AUTOMATIC_FAITH_PURCHASE");
			# pNotifications->Add(NOTIFICATION_CAN_BUILD_MISSIONARY, strBuffer, strSummary, -1, -1, -1);
			# }
			# }
			# else
			# {
			# bSelectionStillValid = false;
			# }
			# }
			# } * /

		if not selectionStillValid:
			if self.isHuman():
				simulation.userInterface.showPopup(PopupType.religionNeedNewAutomaticFaithSelection)

	def canFoundReligion(self, simulation) -> bool:
		if simulation.numberOfAvailableReligions() <= 0:
			return False

		if not self.religion.hasCreatedPantheon():
			return False

		if self.religion.hasCreatedReligion():
			return False

		return True

	def doGreatPeople(self, simulation):
		if self.isBarbarian():
			# no great people for barbarians
			return

		# effects from builds / wonders in each city
		for city in simulation.citiesOf(self):
			greatPeoplePoints = city.greatPeoplePointsPerTurn(simulation)
			self.greatPeople.addPoints(greatPeoplePoints)

		# add effects from policy cards
		self.greatPeople.addPoints(self.greatPeoplePointsFromPolicyCards(simulation))

		# add effects from dedication
		# exodusOfTheEvangelists + golden - +4 Great Prophet points per turn.
		if self._currentAgeValue == AgeType.golden and self.hasDedication(DedicationType.exodusOfTheEvangelists):
			self.greatPeople.addPoints(GreatPersonPoints(greatProphet=4))

		# check if points are enough to gain a great person
		for greatPersonType in list(GreatPersonType):
			greatPersonValue = self.greatPeople.valueFor(greatPersonType)
			greatPersonToSpawn = simulation.greatPersonOf(greatPersonType, greatPersonValue, self)
			if greatPersonToSpawn is not None:
				if self.isHuman():
					# User get notification
					self.notifications.addNotification(NotificationType.canRecruitGreatPerson, greatPerson=greatPersonToSpawn)
				else:
					# AI always takes great persons
					self.recruitGreatPerson(greatPersonToSpawn, simulation)

		return

	def doTurnPost(self, simulation):
		if self.isHuman():
			return

		if self.isBarbarian():
			return

		for victory in simulation.victoryTypes:
			# self.launchVictory(victory)
			pass

		return

	def canFoundAt(self, location: HexPoint, simulation) -> bool:
		# FIXME check deals
		# Has the AI agreed to not settle here?

		# FIXME Settlers cannot found cities while empire is very unhappy

		tile = simulation.tileAt(location)
		if simulation.citySiteEvaluator().canCityBeFoundOn(tile, self):
			return True

		return False

	def canEnterOcean(self) -> bool:
		return False

	def foundAt(self, location: HexPoint, name: Optional[str], simulation):
		tile = simulation.tileAt(location)
		cityName = name if name is not None else self.newCityName(simulation)
		self.builtCityNames.append(cityName)

		# moments
		# check if tile is on a continent that the player has not settler yet
		tileContinent = simulation.continentAt(location)
		if tileContinent is not None:
			if not self.hasSettledOnContinent(tileContinent):
				self.markSettledOnContinent(tileContinent)

				# only from second city (capital == first city is also founded on a 'new' continent)
				if len(simulation.citiesOf(self)) > 0:
					self.addMoment(MomentType.cityOnNewContinent, cityName=cityName, continentName=tileContinent.name, simulation=simulation)

		if tile.terrain() == TerrainType.tundra:
			self.addMoment(MomentType.tundraCity, cityName=cityName, simulation=simulation)
		elif tile.terrain() == TerrainType.desert:
			self.addMoment(MomentType.desertCity, cityName=cityName, simulation=simulation)
		elif tile.terrain() == TerrainType.snow:
			self.addMoment(MomentType.snowCity, cityName=cityName, simulation=simulation)

		if simulation.isLargestPlayer(self) and not self.hasMoment(MomentType.worldsLargestCivilization):
			self.addMoment(MomentType.worldsLargestCivilization, simulation=simulation)

		nearVolcano: bool = False
		nearNaturalWonder: bool = False
		for neighbor in location.areaWithRadius(2):
			neighborTile = simulation.tileAt(neighbor)

			if neighborTile is None:
				continue

			if neighborTile.hasFeature(FeatureType.volcano):
				nearVolcano = True

			if neighborTile.feature().isNaturalWonder():
				nearNaturalWonder = True

		if nearVolcano and not self.hasMoment(MomentType.cityNearVolcano):
			self.addMoment(MomentType.cityNearVolcano, cityName=cityName, simulation=simulation)

		if nearNaturalWonder and not self.hasMoment(MomentType.cityOfAwe):
			self.addMoment(MomentType.cityOfAwe, cityName=cityName, simulation=simulation)

		isCapital = len(simulation.citiesOf(self)) == 0

		city = City(cityName, location, isCapital, self)
		city.initialize(simulation)

		simulation.addCity(city)

		if self.isHuman():
			# Human player is prompted to choose production BEFORE the AI runs for the turn.
			# So we'll force the AI strategies on the city now, just after it is founded.
			# And if the very first turn, we haven't even run player strategies once yet, so do that too.
			if simulation.currentTurn == 0:
				self.economicAI.doTurn(simulation)
				self.militaryAI.doTurn(simulation)

			city.cityStrategy.doTurn(simulation)

			if self.isActive():
				self.notifications.addNotification(NotificationType.productionNeeded, cityName=city.name(), location=city.location)

			city.doFoundMessage(simulation)

			# If this is the first city(or we still aren't getting tech for some other reason) notify the player
			if self.techs.needToChooseTech() and self.science(simulation) > 0.0:
				self.notifications.addNotification(NotificationType.techNeeded)

			# If this is the first city( or..) notify the player
			if self.civics.needToChooseCivic() and self.culture(simulation, consume=False) > 0.0:
				self.notifications.addNotification(NotificationType.civicNeeded)

			if isCapital:
				self.notifications.addNotification(NotificationType.policiesNeeded)
		else:
			city.doFoundMessage(simulation)

			# AI civ, may need to redo city specializations
			self.citySpecializationAI.setSpecializationsDirty()

		# roman roads
		if self.leader.civilization().ability() == CivilizationAbility.allRoadsLeadToRome:
			if not isCapital:
				capital = simulation.capitalOf(self)

				datasource = simulation.ignoreUnitsPathfinderDataSource(UnitMovementType.walk, self, canEmbark=False, canEnterOcean=False)
				pathFinder = AStarPathfinder(datasource)

				path = pathFinder.shortestPath(location, capital.location)

				# If within Trade Route range of the Capital, a road to it.
				if path is not None and len(path.points()) <= TradeRoutes.landRange:

					for pathLocation in path.points():
						pathTile = simulation.tileAt(pathLocation)
						pathTile.setRoute(self.bestRouteAt(None))

		# send gossip
		simulation.sendGossip(GossipType.cityFounded, cityName=cityName, player=self)

		self._citiesFoundValue += 1

		if simulation.tutorial() == Tutorials.foundFirstCity and self.isHuman():
			if self._citiesFoundValue >= Tutorials.citiesToFound():
				simulation.userInterface.finishTutorial(Tutorials.foundFirstCity)
				simulation.enableTutorial(Tutorials.none)

	def newCityName(self, simulation):
		possibleNames = self.leader.civilization().cityNames()

		if self.isCityState() and len(possibleNames) == 0:
			possibleNames.append(self.cityState.title())

		for builtCityName in self.builtCityNames:
			possibleNames = list(filter(lambda name: name != builtCityName, possibleNames))

		for city in simulation.citiesOf(self):
			possibleNames = list(filter(lambda name: name != city.name, possibleNames))

		if len(possibleNames) > 0:
			return possibleNames[0]

		return "TXT_KEY_CITY_NAME_GENERIC"

	def hasBuilding(self, buildingType: BuildingType, simulation) -> bool:
		for city in simulation.citiesOf(self):
			if city.hasBuilding(buildingType):
				return True

		return False

	def canEmbark(self) -> bool:
		return self.hasTech(TechType.shipBuilding)

	def canEmbarkAllWaterPassage(self) -> bool:
		return self.hasTech(TechType.cartography)

	def hasTech(self, techType: TechType) -> bool:
		return self.techs.hasTech(techType)

	def hasCivic(self, civicType: CivicType) -> bool:
		return self.civics.hasCivic(civicType)

	def personalAndGrandStrategyFlavor(self, flavorType: FlavorType) -> int:
		if self.grandStrategyAI.activeStrategy == GrandStrategyAIType.none:
			return self.personalityFlavors.value(flavorType)

		value = self.personalityFlavors.value(flavorType) + self.grandStrategyAI.activeStrategy.flavorModifier(flavorType)

		if value < 0:
			return 0

		return value

	def numberOfTradeRoutes(self) -> int:
		return self.tradeRoutes.numberOfTradeRoutes()

	def numberOfUnassignedTraders(self, simulation) -> int:
		return len(list(filter(lambda u: u.defaultTask() == UnitTaskType.trade, simulation.unitsOf(self))))

	def tradingCapacity(self) -> int:
		return self._tradingCapacityValue

	def possibleTradeRoutes(self, originCity, simulation) -> [TradeRoute]:
		routes: [TradeRoute] = []

		tmpTrader = Unit(originCity.location, UnitType.trader, self)
		pathFinderDataSource = simulation.unitAwarePathfinderDataSource(tmpTrader)
		pathFinder = AStarPathfinder(pathFinderDataSource)

		if originCity is None:
			return []

		targetCities = self.possibleTradeRouteTargetsFrom(originCity, simulation)

		for targetCity in targetCities:
			path = pathFinder.shortestPath(originCity.location, targetCity.location)
			if path is not None:
				path.prepend(originCity.location, 0.0)

				if lastOrNone(path.points()) != targetCity.location:
					path.append(targetCity.location, 0.0)

				routes.append(TradeRoute(path))
			else:
				logging.debug(f"Player.possibleTradeRoutes - cant get route from {originCity.name()} to {targetCity.name()}")

		return routes

	def possibleTradeRouteTargetsFrom(self, originCity, simulation):
		sourceCities = [originCity]
		cities = []

		if originCity.player != self:
			raise Exception(f'Can only start trade route for own cities - own player: {self} / city: {originCity.player}')

		while len(sourceCities) > 0:
			cityToCheck = sourceCities.pop(0)

			for loopPlayer in simulation.players:
				for loopCity in simulation.citiesOf(loopPlayer):
					cityLocation = loopCity.location
					cityTile = simulation.tileAt(cityLocation)

					if cityTile is None:
						continue

					if cityToCheck.location == cityLocation:
						continue

					if not cityTile.isDiscoveredBy(self):
						continue

					# check if is within reach
					if self.tradeRoutes.canEstablishTradeRouteFrom(cityToCheck, loopCity, simulation):
						if loopCity not in cities and originCity != loopCity:
							cities.append(loopCity)

						# do we have a trading post in this city?
						if loopCity.cityTradingPosts.hasTradingPostOf(originCity.player.leader):
							# if so, then we can use this city as a hub to extend our trade route
							sourceCities.append(loopCity)

		return cities

	def setupFlavors(self):
		if not self.personalityFlavors.isEmpty():
			return

		defaultFlavorValue = 5  # DEFAULT_FLAVOR_VALUE

		if self.isHuman():
			# Human player, just set all flavors to average(5)
			for flavorType in list(FlavorType):
				self.personalityFlavors.set(flavorType, defaultFlavorValue)
		else:
			for flavorType in list(FlavorType):
				leaderFlavor = self.leader.flavor(flavorType)

				# If no Flavor value is set use the Default
				if leaderFlavor == 0:
					leaderFlavor = defaultFlavorValue

				self.personalityFlavors.set(flavorType, leaderFlavor)

			# Tweak from default values
			# Make a random adjustment to each flavor value for this leader so they don't play exactly the same
			for flavorType in list(FlavorType):
				currentFlavor = self.personalityFlavors.value(flavorType)

				# Don't modify it if it's zero - ed out in the XML
				if currentFlavor == 0:
					continue

				adjustedFlavor = Flavors.adjustedValue(currentFlavor, plusMinus=2, minimum=0, maximum=20)
				self.personalityFlavors.set(flavorType, adjustedFlavor)

		return

	def hasRetired(self, greatPerson: GreatPerson) -> bool:
		return self.greatPeople.hasRetired(greatPerson)

	def canBuild(self, buildType: BuildType, location: HexPoint, testGold: bool, simulation) -> bool:
		tile = simulation.tileAt(location)

		if not tile.canBuild(buildType, self):
			return False

		required = buildType.required()
		if required is not None:
			if not self.hasTech(required):
				return False

		# Is this an improvement that is only useable by a specific civ?
		improvement = buildType.improvement()
		if improvement is not None and improvement != ImprovementType.none:
			improvementCivilization = improvement.civilization()
			if improvementCivilization is not None:
				if improvementCivilization != self.leader.civilization():
					return False

		# IsBuildBlockedByFeature
		if tile.hasAnyFeature():
			for feature in list(FeatureType):
				if tile.hasFeature(feature):
					if buildType.keepsFeature(feature):
						continue

					if not buildType.canRemove(feature):
						return False

					removeTech = buildType.requiredRemoveTechFor(feature)
					if removeTech is not None:
						if not self.hasTech(removeTech):
							return False

		if testGold:
			# if (max(0, self.treasury.value()) < getBuildCost(pPlot, eBuild)):
			#	return False
			pass

		return True

	def changeTotalImprovementsBuiltBy(self, change: int):
		self._totalImprovementsBuilt += change

	def changeUnassignedEnvoysBy(self, envoys: int):
		self.envoys.changeUnassignedEnvoysBy(envoys)

	def productionCostOfUnit(self, unitType: UnitType) -> float:
		if unitType == UnitType.settler:
			policyCardModifier: float = 1.0

			# expropriation - Settler cost reduced by 50%. Plot purchase cost reduced by 20 %.
			if self.government.hasCard(PolicyCardType.expropriation):
				policyCardModifier -= 0.5

			# The Production cost of a Settler scales according to the following formula, in which x is the number of
			# Settlers you've trained (including your initial one): 30*x+50
			return int(float(30 * self._trainedSettlersValue + 50) * policyCardModifier)

		return unitType.productionCost()

	def countUnitsWithDefaultTask(self, taskType: UnitTaskType, simulation) -> int:
		playerUnits = simulation.unitsOf(self)
		return len(list(filter(lambda unit: unit.defaultTask() == taskType, playerUnits)))

	def countCitiesFeatureSurrounded(self, simulation) -> int:
		playerCities = simulation.citiesOf(self)
		return len(list(filter(lambda city: city.isFeatureSurrounded(), playerCities)))

	def hasDiscovered(self, naturalWonder: FeatureType) -> bool:
		return naturalWonder in self._discoveredNaturalWonders

	def doDiscover(self, naturalWonder: FeatureType):
		self._discoveredNaturalWonders.append(naturalWonder)

	def numberOfDistricts(self, district: DistrictType, simulation) -> int:
		"""Counts the number districts of type 'district' in all cities of this player"""
		numberOfDistricts = 0

		for city in simulation.citiesOf(self):
			if city.hasDistrict(district):
				numberOfDistricts += 1

		return numberOfDistricts

	def numberBuildings(self, building: BuildingType, simulation) -> int:
		"""Counts the number buildings of type 'building' in all cities of this player"""
		numberOfBuildings = 0

		for city in simulation.citiesOf(self):
			if city.hasBuilding(building):
				numberOfBuildings += 1

		return numberOfBuildings

	def doDeclareWarTo(self, otherPlayer, simulation):
		self.diplomacyAI.doDeclareWarTo(otherPlayer, simulation)

		# update danger plots
		simulation.refreshDangerPlots()

		# inform other players, that war was declared
		otherLeader = otherPlayer.leader
		simulation.sendGossip(GossipType.declarationsOfWar, leader=otherLeader, player=self)

	def capitalCity(self, simulation):
		return simulation.capitalOf(self)

	def originalCapitalLocation(self) -> HexPoint:
		return self.originalCapitalLocationValue

	def canEstablishTradeRoute(self) -> bool:
		tradingCapacity = self._tradingCapacityValue
		numberOfTradeRoutes = self.numberOfTradeRoutes()

		if numberOfTradeRoutes >= tradingCapacity:
			return False

		return True

	def doEstablishTradeRoute(self, originCity, targetCity, trader, simulation) -> bool:
		targetPlayer = targetCity.player

		if targetPlayer != self:
			if not self.hasEverEstablishedTradingPostWith(targetPlayer):
				self.markEstablishedTradingPostWith(targetPlayer)

				self.addMoment(
					MomentType.tradingPostEstablishedInNewCivilization,
					civilization=targetPlayer.leader.civilization(),
					simulation=simulation
				)

				# possibleTradingPosts = (simulation.players.filter {$0.isAlive()}.count - 1)
				# if self.numEverEstablishedTradingPosts( simulation) == possibleTradingPosts
				# 	if simulation.anyHasMoment(of: .firstTradingPostsInAllCivilizations) {
				# 		self.addMoment(of:.tradingPostsInAllCivilizations, simulation=simulation)
				# 	else:
				# 		self.addMoment(of:.firstTradingPostsInAllCivilizations, simulation=simulation)

			# update access level
			if not self == targetCity.player:
				# if this is the first trade route with this player, increase the access level
				if not self.tradeRoutes.hasTradeRouteWith(targetCity.player, simulation):
					self.diplomacyAI.increaseAccessLevelTowards(targetCity.player)

		if not self.techs.eurekaTriggeredFor(TechType.currency):
			self.techs.triggerEurekaFor(TechType.currency, simulation)

		# check city state quests
		if targetPlayer.isCityState():
			for quest in self.ownQuests(simulation):
				if quest.questType == CityStateQuestType.sendTradeRoute and \
					targetCity.player.cityStateType == quest.cityState and quest.leader == self.leader:
					targetCity.player.fulfillQuestBy(self.leader, simulation)

		# no check ?

		return self.tradeRoutes.establishTradeRoute(originCity, targetCity, trader, simulation)

	def doFinishTradeRoute(self, tradeRoute, simulation):
		targetCity = simulation.cityAt(tradeRoute.end())

		self.tradeRoutes.finishTradeRoute(tradeRoute)

		# update access level
		if not self == targetCity.player:
			# if this was the last trade route with this player, decrease the access level
			if not self.tradeRoutes.hasTradeRouteWith(targetCity.player, simulation):
				self.diplomacyAI.decreaseAccessLevelTowards(targetCity.player)

		return

	def bestRouteAt(self, tile=None) -> RouteType:
		for buildType in list(BuildType):
			routeType = buildType.route()
			if routeType is not None:
				if self.canBuildAt(buildType, tile):
					return routeType

		return RouteType.none

	def canBuildAt(self, buildType: BuildType, tile) -> bool:
		if tile is not None:
			if not tile.canBuild(buildType, self):
				return False

		requiredTech = buildType.required()
		if requiredTech is not None:
			if not self.hasTech(requiredTech):
				return False

		requiredEra = buildType.route().era()
		if requiredEra is not None:
			if self.currentEra() != requiredEra:
				return False

		# FIXME: check cost

		return True

	def currentEra(self) -> EraType:
		return self._currentEraValue

	def changeTrainedSettlersBy(self, delta: int):
		self._trainedSettlersValue += delta

	def bestSettleAreasWithMinimumSettleFertility(self, minimumSettleFertility: int, simulation) \
		-> (int, Optional[HexArea], Optional[HexArea]):

		bestScore: int = -1
		bestArea: Optional[HexArea] = None
		secondBestScore: int = -1
		secondBestArea: Optional[HexArea] = None

		# Find best two scores above minimum
		for area in simulation.areas():
			value = area.value()
			if value is None:
				continue

			score = value

			if score > minimumSettleFertility:
				if score > bestScore:
					# Already have the best area? If so demote to 2nd
					if bestScore > minimumSettleFertility:
						secondBestScore = bestScore
						secondBestArea = bestArea

					bestScore = score
					bestArea = area

				elif score > secondBestScore:
					secondBestScore = score
					secondBestArea = area

		tmp = 1 if secondBestScore != -1 else 0
		numberOfAreas = 1 if bestScore != -1 else tmp

		return numberOfAreas, bestArea, secondBestArea

	def hasSettledOnContinent(self, continent) -> bool:
		return continent in self._settledContinents

	def markSettledOnContinent(self, continent):
		self._settledContinents.append(continent)

	def firstPromotableUnit(self, simulation):
		for loopUnit in simulation.unitsOf(self):
			if loopUnit.isPromotionReady() and not loopUnit.isDelayedDeath():
				return loopUnit

		return None

	def hasPromotableUnit(self, simulation):
		return self.firstPromotableUnit(simulation) is not None

	def doQuests(self, simulation):
		pass

	def endTurnsForReadyUnits(self, simulation):
		for loopUnit in simulation.unitsOf(self):
			if loopUnit.readyToMove() and not loopUnit.isDelayedDeath():
				loopUnit.finishMoves()

		return

	def addPlotAt(self, point: HexPoint):
		self._area.addPoint(point)

	def acquireCity(self, oldCity, conquest: bool, gift: bool, simulation):
		diplomacyAI = self.diplomacyAI
		otherDiplomacyAI = oldCity.player.diplomacyAI

		units = simulation.unitsAt(oldCity.location)
		for loopUnit in units:
			if loopUnit.player.leader != self.leader:
				if loopUnit.isImmobile():
					loopUnit.doKill(delayed=True, otherPlayer=self, simulation=simulation)
					self.doUnitKilledCombat(loopUnit.player, loopUnit.unitType)

		if conquest:
			# / * CvNotifications * pNotifications = GET_PLAYER(pOldCity->getOwner()).GetNotifications();
			# if (pNotifications)
			# {
			# Localization::String
			# locString = Localization::Lookup("TXT_KEY_NOTIFICATION_CITY_LOST");
			# locString << pOldCity->getNameKey() << getNameKey();
			# Localization::String
			# locSummary = Localization::Lookup("TXT_KEY_NOTIFICATION_SUMMARY_CITY_LOST");
			# locSummary << pOldCity->getNameKey();
			# pNotifications->Add(NOTIFICATION_CITY_LOST, locString.toUTF8(), locSummary.toUTF8(),
			#                     pOldCity->getX(), pOldCity->getY(), -1);
			# } * /

			if not self.isBarbarian() and not oldCity.isBarbarian():
				defaultCityValue = 150  # WAR_DAMAGE_LEVEL_CITY_WEIGHT

				# Notify Diplo AI that damage has been done
				value = defaultCityValue
				value += oldCity.population() * 100  # WAR_DAMAGE_LEVEL_INVOLVED_CITY_POP_MULTIPLIER
				# My viewpoint
				diplomacyAI.changeOtherPlayerWarValueLostBy(oldCity.player, self, value)
				# Bad guy's viewpoint
				otherDiplomacyAI.changeWarValueLostBy(self, value)

				value = defaultCityValue
				value += oldCity.population() * 120 # WAR_DAMAGE_LEVEL_UNINVOLVED_CITY_POP_MULTIPLIER

				# Now update everyone else in the world, but use a different multiplier(since they don't have complete info on
				# the situation - they don't know when Units are killed)
				for loopPlayer in simulation.players:
					# Not us and not the player we acquired City from
					if not self == loopPlayer and not loopPlayer == oldCity.player:
						loopPlayer.diplomacyAI.changeOtherPlayerWarValueLostBy(oldCity.player, self, value)

		if oldCity.originalLeader() == oldCity.player.leader and oldCity.originalCityState() == oldCity.player.cityState:
			if oldCity.originalLeader() == LeaderType.cityState:
				originalPlayer = simulation.cityStatePlayerFor(oldCity.originalCityState())
			else:
				originalPlayer = simulation.playerFor(oldCity.originalLeader())

			if originalPlayer is not None:
				originalPlayer.changeCitiesLostBy(1)
		elif oldCity.originalLeader() == self.leader:
			self.changeCitiesLostBy(-1)

		if conquest:
			activePlayer = simulation.activePlayer()
			if activePlayer is not None and self == activePlayer:
				# simulation.userInterface?.showTooltip(at: oldCity.location,
				# 	type:.capturedCity(cityName: oldCity.name),
				# 	delay: 3
				# )
				pass

			message = f"{oldCity.name()} was captured by the {self.leader.civilization().name()}!!!"
			simulation.addReplayEvent(ReplayEventType.cityCaptured, message, oldCity.location)

			# inform other players, that a city was conquered or liberated
			if self.leader == oldCity.originalLeader():
				simulation.sendGossip(GossipType.cityLiberated, cityName=oldCity.name, originalOwner=oldCity.originalLeader(), player=self)
			else:
				simulation.sendGossip(GossipType.cityConquests, cityName=oldCity.name, player=self)

		captureGold = 0

		if conquest:
			captureGold += 200  # BASE_CAPTURE_GOLD
			captureGold += oldCity.population() * 40  # CAPTURE_GOLD_PER_POPULATION
			captureGold += random.randint(0, 40)  # CAPTURE_GOLD_RAND1
			captureGold += random.randint(0, 20)  # CAPTURE_GOLD_RAND2

			foundedTurnsAgo = simulation.currentTurn - oldCity.turnFounded()
			captureGold *= min(500, max(0, foundedTurnsAgo)) # CAPTURE_GOLD_MAX_TURNS
			captureGold /= 500  # CAPTURE_GOLD_MAX_TURNS

			# captureGold *= (100 + oldCity.capturePlunderModifier()) / 100
			# captureGold *= (100 + self.leader.traits().plunderModifier()) / 100

		self.treasury.changeGoldBy(float(captureGold))

		oldPlayer = oldCity.player
		oldCityLocation = oldCity.location
		oldLeader = oldCity.player.leader
		oldCityState = oldCity.player.cityState
		originalOwner = oldCity.originalLeader()
		oldTurnFounded = oldCity.turnFounded()
		oldPopulation = oldCity.population()
		# iHighestPopulation = pOldCity->getHighestPopulation();
		everCapital = oldCity.isEverCapital()
		oldName = oldCity.name
		oldCultureLevel = oldCity.cultureLevel()
		hasMadeAttack = oldCity.isOutOfAttacks(simulation)
		oldBattleDamage = oldCity.damage()

		# Traded cities between humans don't heal (an exploit would be to trade a city back and forth between
		# teammates to get an instant heal.)
		oldPlayerHuman: bool = oldCity.player.isHuman()
		if not gift or not self.isHuman() or not oldPlayerHuman:
			battleDamageThreshold = 200 * 50  # MAX_CITY_HIT_POINTS, CITY_CAPTURE_DAMAGE_PERCENT
			battleDamageThreshold /= 100

			if oldBattleDamage > battleDamageThreshold:
				oldBattleDamage = battleDamageThreshold

		oldDistricts: [CityDistrictItem] = []
		for districtType in list(DistrictType):
			if districtType == DistrictType.cityCenter:
				continue

			if oldCity.hasDistrict(districtType):
				oldLocation = oldCity.locationOfDistrict(districtType)
				oldDistricts.append(CityDistrictItem(districtType, oldLocation))

		oldBuildings: [BuildingType] = []
		for buildingType in list(BuildingType):
			if oldCity.hasBuilding(buildingType):
				oldBuildings.append(buildingType)

		oldWonders: [CityWonderItem] = []
		for wonderType in list(WonderType):
			if oldCity.hasWonder(wonderType):
				oldLocation = oldCity.locationOfWonder(wonderType)
				oldWonders.append(CityWonderItem(wonderType, oldLocation))

		recapture = False
		capital = oldCity.isCapital()

		oldCity.preKill(simulation)

		simulation.userInterface.removeCity(oldCity)

		simulation.deleteCity(oldCity)
		# adapted from PostKill()

		# GC.getGame().addReplayMessage(REPLAY_MESSAGE_CITY_CAPTURED, m_eID, "", pCityPlot->getX(), pCityPlot->getY());

		# Update Proximity between this Player and all others
		for loopPlayer in simulation.players:
			if not loopPlayer == self and loopPlayer.isAlive() and loopPlayer.hasMetWith(self):
				self.doUpdateProximityTowards(loopPlayer, simulation)
				loopPlayer.doUpdateProximityTowards(self, simulation)

		for neighbor in oldCityLocation.areaWithRadius(3):
			tile = simulation.tileAt(neighbor)
			simulation.userInterface.refreshTile(tile)

		# Lost the capital!
		if capital:
			oldPlayer.setHasLostCapital(True, self, simulation)
			oldPlayer.findNewCapital(simulation)

		# GC.GetEngineUserInterface()->setDirty(NationalBorders_DIRTY_BIT, true);
		# end adapted from PostKill()

		newCity = City(oldName, oldCityLocation, False, self)
		newCity.initialize(simulation)

		newCity.setOriginalLeader(originalOwner)
		newCity.setGameTurnFounded(oldTurnFounded)
		newCity.setPreviousLeader(oldLeader)
		newCity.setPreviousCityState(oldCityState)
		newCity.setEverCapitalTo(everCapital)

		# Population change for capturing a city
		if not recapture and conquest:
			# Don't drop it if we're recapturing our own City
			oldPopulation = max(1, oldPopulation * 50 / 100)  # CITY_CAPTURE_POPULATION_PERCENT

		newCity.setPopulation(oldPopulation, reassignCitizen=False, simulation=simulation)
		# pNewCity->setHighestPopulation(iHighestPopulation);
		newCity.setName(oldName)
		# pNewCity->setNeverLost(false);
		newCity.setDamage(oldBattleDamage)
		newCity.setMadeAttackTo(hasMadeAttack)

		#for (iI = 0; iI < MAX_PLAYERS; iI++)
		#	pNewCity->setEverOwned(((PlayerTypes)iI), abEverOwned[iI]);

		newCity.changeCultureLevelBy(oldCultureLevel)

		for district in oldDistricts:
			newCity.districts.build(district.district, district.location)

		for building in oldBuildings:
			newCity.buildings.build(building)

		for wonder in oldWonders:
			newCity.wonders.build(wonder.wonder, wonder.location)

		# Did we re-acquire our Capital?
		if self.originalCapitalLocation() == oldCityLocation:
			self.setHasLostCapital(False, None, simulation)

		simulation.addCity(newCity)

		# If the old owner is "killed", then notify everyone's Grand Strategy AI
		numberOfCities = len(simulation.citiesOf(oldPlayer))
		if numberOfCities == 0:
			if not self.isCityState() and not self.isBarbarian():
				for loopPlayer in simulation.players:
					if not self == loopPlayer and loopPlayer.isAlive():
						# Have I met the player who killed the guy?
						if loopPlayer.hasMetWith(self):
							loopPlayer.diplomacyAI.doPlayerKilledSomeone(self, oldPlayer)
		else:
			# If not, old owner should look at city specializations
			oldPlayer.citySpecializationAI.setSpecializationsDirty()

		# Do the same for the new owner
		self.citySpecializationAI.setSpecializationsDirty()

		return

	def doUpdateProximityTowards(self, otherPlayer, simulation):
		self.diplomacyAI.updateProximityTo(otherPlayer, simulation)

	def proximityTo(self, otherPlayer) -> PlayerProximityType:
		return self.diplomacyAI.proximityTo(otherPlayer)

	def changeCitiesLostBy(self, delta: int):
		self._citiesLostValue += delta

	def setHasLostCapital(self, value: bool, conqueror, simulation):
		"""
		Sets us to having lost our capital in war
		also checks for domination victory
		void CvPlayer::SetHasLostCapital(bool bValue, PlayerTypes eConqueror)
		@param value:
		@param conqueror:
		@param simulation:
		@return:
		"""
		if value != self.lostCapitalValue:
			self.lostCapitalValue = value
			self.conquerorValue = conqueror.leader

			# Someone just lost their capital, test to see if someone wins
			if value:
				# slewis - Moved Conquest victory elsewhere so that victory is more accurately awarded
				# -- simulation.DoTestConquestVictory();

				# notify users about another player lost his capital
				if self.isHuman():
					simulation.userInterface.showPopup(PopupType.lostOwnCapital)
				else:
					if self.hasMetWith(simulation.humanPlayer()):
						simulation.userInterface.showPopup(PopupType.lostCapital, leader=self.leader)
					else:
						simulation.userInterface.showPopup(PopupType.lostCapital, leader=LeaderType.unmet)

				# todo: add replay message
				# GC.getGame().addReplayMessage(REPLAY_MESSAGE_MAJOR_EVEN

		return

	def findNewCapital(self, simulation):
		bestCity = None
		bestValue = 0

		for loopCity in simulation.citiesOf(self):
			value = loopCity.population() * 4

			yieldValueTimes100: int = int(loopCity.foodPerTurn(simulation)) * 100
			yieldValueTimes100 += int(loopCity.productionPerTurn(simulation)) *100 * 3
			yieldValueTimes100 += int(loopCity.goldPerTurn(simulation)) *100 * 2
			value += (yieldValueTimes100 / 100)

			if value > bestValue:
				bestValue = value
				bestCity = loopCity

		if bestCity is None:
			return

		bestCity.buildings.build(BuildingType.palace)
		bestCity.setIsCapitalTo(True)

		# update UI
		simulation.userInterface.updateCity(bestCity)
		simulation.userInterface.refreshTile(simulation.tileAt(bestCity.location))

		return

	def updateWarWearinessAgainst(self, otherPlayer, point, killed: bool, simulation):
		# https://civilization.fandom.com/wiki/War_weariness_(Civ6)
		tile = simulation.tileAt(point)

		# the fight against barbarians does not trigger war weariness
		if self.isBarbarian() or otherPlayer.isBarbarian():
			return

		# war type / Casus Belli not implemented
		baseValue = self._currentEraValue.warWearinessValue(formal=False)
		ownTerritory: bool = tile.hasOwner() and self == tile.owner()

		warWearinessVal = baseValue * (1 if ownTerritory else 2) + baseValue * (0 if killed else 3)

		logging.info(f"### add war weariness for {self.leader} against {otherPlayer.leader}: {warWearinessVal}")
		self.changeWarWearinessWith(otherPlayer, warWearinessVal)

		self.combatThisTurnValue = True

	def changeWarWearinessWith(self, otherPlayer, value: int):
		self.diplomacyAI.changeWarWearinessWith(otherPlayer, value)

	def numberOfCitiesLost(self) -> int:
		return self._citiesLostValue

	def score(self, simulation) -> int:
		"""
			https://civilization.fandom.com/wiki/Victory_(Civ6)
			Era Score points.
			15 points for each wonder owned.
			10 points for founding a religion.
			5 points for each Great Person earned.
			5 points for each city owned.
			3 points for each civic researched.
			2 points for each foreign city following the player's religion.
			2 points for each technology researched.
			2 points for each district owned (4 points if it is a unique district).
			1 point for each building (including the Palace).
			1 point for each Citizen in the player's empire.
			@param simulation:
			@return:
		"""
		if not self.isAliveVal:
			# no need to update, the player died
			return 0

		scoreVal = 0

		scoreVal += self.scoreFromCities(simulation)
		scoreVal += self.scoreFromBuildings(simulation)
		scoreVal += self.scoreFromPopulation(simulation)
		scoreVal += self.scoreFromTechs(simulation)
		scoreVal += self.scoreFromLand(simulation)
		scoreVal += self.scoreFromCivics(simulation)
		scoreVal += self.scoreFromWonder(simulation)
		# scoreVal += self.scoreFromTech(simulation)
		scoreVal += self.scoreFromReligion(simulation)

		return scoreVal

	def scoreFromCities(self, simulation) -> int:
		# 5 points for each city owned.
		cities = simulation.citiesOf(self)
		mapSizeModifier = simulation.mapSizeModifier()
		score = len(cities) * 5

		# weight with map size
		score *= 100
		score /= mapSizeModifier

		return score

	def scoreFromBuildings(self, simulation) -> int:
		# 1 point for each building (including the Palace).
		cities = simulation.citiesOf(self)
		mapSizeModifier = simulation.mapSizeModifier()

		score = 0

		for city in cities:
			score += city.buildings.numberOfBuildings()

		# weight with map size
		score *= 100
		score /= mapSizeModifier

		return score

	def scoreFromPopulation(self, simulation) -> int:
		# 1 point for each Citizen in the player's empire.
		cities = simulation.citiesOf(self)
		mapSizeModifier = simulation.mapSizeModifier()

		score = 0

		for city in cities:
			score += city.population() * 1

		# weight with map size
		score *= 100
		score /= mapSizeModifier

		return score

	def scoreFromTechs(self, simulation) -> int:
		# 2 points for each technology researched.
		return self.techs.numberOfDiscoveredTechs() * 2

	def scoreFromLand(self, simulation) -> int:
		# 2 points for each district owned
		mapSizeModifier = simulation.mapSizeModifier()

		score = len(self.area().points()) * 2  # SCORE_LAND_MULTIPLIER

		# weight with map size
		score *= 100
		score /= mapSizeModifier

		return score

	def scoreFromCivics(self, simulation) -> int:
		# 3 points for each civic researched.
		return self.civics.numberOfDiscoveredCivics() * 3

	def scoreFromWonder(self, simulation) -> int:
		# Score from world wonders: 15 points for each wonder owned.
		number = 0

		for city in simulation.citiesOf(self):
			number += city.wonders.numberOfBuiltWonders()

		score = number * 15  # SCORE_WONDER_MULTIPLIER
		return score

	def scoreFromReligion(self, simulation) -> int:
		# 10 points for founding a religion.
		# 2 points for each foreign city following the player's religion.
		score = 0

		if self.religion.currentReligion() != ReligionType.none:
			# 10 points for founding a religion.
			score += 10

			numberOfCitiesFollowingReligion = 0
			for player in simulation.players:
				if player == self:
					continue

				for city in simulation.citiesOf(player):
					if city.religiousMajority() == self.religion.currentReligion():
						numberOfCitiesFollowingReligion += 1

			# 2 points for each foreign city following the player's religion.
			score += numberOfCitiesFollowingReligion * 2

		return score

	def faith(self, reset: bool, simulation) -> float:
		if self.isCityState() or self.isBarbarian():
			return 0.0

		value = 0.0

		# faith from our Cities
		value += self.faithFromCities(simulation)
		value += float(self._faithEarned)

		# ....
		if reset:
			self._faithEarned = 0

		return value

	def faithFromCities(self, simulation) -> float:
		if self.isCityState() or self.isBarbarian():
			return 0.0

		faithVal = 0.0

		for city in simulation.citiesOf(self):
			faithVal += city.faithPerTurn(simulation)

		return faithVal

	def AI_captureUnit(self, unitType: UnitType, tile, simulation) -> bool:
		if self.isHuman():
			raise Exception('Human should call this method')

		# Barbs always capture
		if self.isBarbarian():
			return True

		# we own it
		if tile.owner() == self:
			return True

		# no man's land - may as well
		if not tile.hasOwner():
			return True

		# friendly, sure(okay, this is pretty much just means open borders)
		if tile.isFriendlyTerritoryFor(self, simulation):
			return True

		# not friendly, but "near" us
		nearestCities = simulation.citiesIn(HexArea(tile.point, 7))
		for city in nearestCities:
			if city.player == self:
				return True

		# very near someone we aren't friends with (and far from our nearest city)
		nearestCities = simulation.citiesIn(HexArea(tile.point, 4))
		for city in nearestCities:
			if city.player.isAtWarWith(self):
				return False

		# I'd rather we grab it and run than destroy it
		return True

	def bestSettlePlotFor(self, firstSettler, escorted: bool, sameArea: bool = False, simulation = None):
		"""Find the best spot in the entire world for this unit to settle"""
		if simulation is None:
			raise Exception('simulation must not be None')

		unitArea = simulation.areaOf(firstSettler.location)

		bestFoundValue = 0.0
		bestFoundPlot = None  # : Optional[Tile]

		evalDistance = 12  # SETTLER_EVALUATION_DISTANCE
		distanceDropoffMod = 99  # SETTLER_DISTANCE_DROPOFF_MODIFIER

		evalDistance += (simulation.currentTurn * 5) / 100

		# scale this based on world size
		defaultNumTiles = MapSize.standard.numberOfTiles()
		defaultEvalDistance = evalDistance
		evalDistance = (evalDistance * simulation.mapSize().numberOfTiles()) / defaultNumTiles
		evalDistance = max(defaultEvalDistance, evalDistance)

		# is this primarily a naval map
		if escorted and False:  # simulation.isPrimarilyNaval():
			evalDistance *= 3
			evalDistance /= 2

		# Stay close to home if you don't have an escort
		if not escorted:
			evalDistance /= 2

		foundEvaluator = simulation.citySiteEvaluator()

		mapPoints = simulation.points()

		if not Tests.are_running:
			random.shuffle(mapPoints)

		for loc in mapPoints:
			tile = simulation.tileAt(loc)
			if tile is None:
				continue

			if tile.hasOwner() and tile.owner().leader != self.leader:
				continue

			if not tile.isDiscoveredBy(self):
				continue

			if not self.canFoundAt(loc, simulation):
				continue

			if sameArea and tile.area() is not None and unitArea is not None and tile.area() != unitArea:
				continue

			# Do we have to check if this is a safe place to go?
			if escorted or not simulation.isEnemyVisibleAt(loc, self):
				value = 100.0 * foundEvaluator.valueOfPoint(loc, self)

				# FIXME - used to be 5000
				if value > 2000.0:
					settlerDistance = loc.distance(firstSettler.location)
					distanceDropoff = (distanceDropoffMod * settlerDistance) / evalDistance
					distanceDropoff = max(0.0, min(99.0, distanceDropoff))
					value = value * (100.0 - distanceDropoff) / 100.0

					if tile.area() is not None and tile.area() != unitArea:
						value *= 2.0
						value /= 3.0

					if value > bestFoundValue:
						bestFoundValue = value
						bestFoundPlot = tile

		return bestFoundPlot

	def atWarCount(self) -> int:
		return self.diplomacyAI.atWarCount()

	def addOperation(self, operationType: UnitOperationType, otherPlayer, targetCity, area, musterCity, simulation) -> Operation:
		operation: Optional[Operation] = None

		if operationType == UnitOperationType.foundCity:
			operation = FoundCityOperation()
		elif operationType == UnitOperationType.cityCloseDefense:
			operation = CityCloseDefenseOperation()
		elif operationType == UnitOperationType.basicCityAttack:
			operation = BasicCityAttackOperation()
		elif operationType == UnitOperationType.pillageEnemy:
			operation = PillageEnemyOperation()
		elif operationType == UnitOperationType.rapidResponse:
			operation = RapidResponseOperation()
		elif operationType == UnitOperationType.destroyBarbarianCamp:
			operation = DestroyBarbarianCampOperation()
		elif operationType == UnitOperationType.navalAttack:
			operation = NavalAttackOperation()
		elif operationType == UnitOperationType.navalSuperiority:
			operation = NavalSuperiorityOperation()
		elif operationType == UnitOperationType.navalBombard:
			operation = NavalBombardmentOperation()
		elif operationType == UnitOperationType.colonize:
			operation = NavalEscortedOperation()
		elif operationType == UnitOperationType.notSoQuickColonize:
			operation = QuickColonizeOperation()  # ???
		elif operationType == UnitOperationType.quickColonize:
			operation = QuickColonizeOperation()
		elif operationType == UnitOperationType.pureNavalCityAttack:
			operation = PureNavalCityAttackOperation()
		elif operationType == UnitOperationType.smallCityAttack:
			operation = SmallCityAttackOperation()
		elif operationType == UnitOperationType.sneakCityAttack:
			if simulation.currentTurn < 50 and self.leader.boldness() >= 5:
				operation = QuickSneakCityAttackOperation()
			else:
				operation = SneakCityAttackOperation()
		elif operationType == UnitOperationType.navalSneakAttack:
			operation = NavalSneakAttackOperation()

		if operation is not None:
			targetLocation: Optional[HexPoint] = None if targetCity is None else targetCity.location
			musterLocation: Optional[HexPoint] = None if musterCity is None else musterCity.location
			operation.initialize(self, otherPlayer, area, targetLocation, musterLocation, simulation)
			self.operations.addOperation(operation)

		return operation

	def canTrain(self, unitType: UnitType, continueFlag: bool, testVisible: bool, ignoreCost: bool, ignoreUniqueUnitStatus: bool) -> bool:
		# Should we check whether this Unit has been blocked out by the civ XML?
		if not ignoreUniqueUnitStatus:
			# If the player isn't allowed to train this Unit (via XML) then return false
			if unitType.unitTypeFor(self.leader.civilization()) is None:
				return False

		if not ignoreCost:
			if unitType.productionCost() < 0:
				return False

		# Civic Requirement
		civic = unitType.requiredCivic()
		if civic is not None:
			if not self.civics.hasCivic(civic):
				return False

		if not continueFlag:
			if not testVisible:
				# Builder Limit
				if unitType.workRate() > 0 and unitType.domain() == UnitDomainType.land:
					# if (GetMaxNumBuilders() > -1 & & GetNumBuilders() >= GetMaxNumBuilders())
					# return false;
					pass

		# Tech requirements
		tech = unitType.requiredTech()
		if tech is not None:
			if not self.techs.hasTech(tech):
				return False

		# Obsolete Tech
		obsoleteTech = unitType.obsoleteTech()
		if obsoleteTech is not None:
			if self.techs.hasTech(obsoleteTech):
				return False

		# Spaceship part we already have?
		# / *ProjectTypes
		# eProject = (ProjectTypes)
		# pUnitInfo.GetSpaceshipProject();
		# if (eProject != NO_PROJECT)
		# {
		# if (GET_TEAM(getTeam()).isProjectMaxedOut(eProject))
		# return false;
		#
		# int
		# iUnitAndProjectCount = GET_TEAM(getTeam()).getProjectCount(eProject) + getUnitClassCount(eUnitClass) + GET_TEAM(
		# 	getTeam()).getUnitClassMaking(eUnitClass) + ((bContinue) ? -1: 0);
		# if (iUnitAndProjectCount >= pkUnitClassInfo->getMaxPlayerInstances())
		# {
		# return false;


		if not testVisible:
			# Settlers
			if unitType.canFound():
				# / * if (IsEmpireVeryUnhappy() & & GC.getVERY_UNHAPPY_CANT_TRAIN_SETTLERS() == 1)
				# {
				# 	GC.getGame().BuildCannotPerformActionHelpText(toolTipSink, "TXT_KEY_NO_ACTION_VERY_UNHAPPY_SETTLERS");
				# if (toolTipSink == NULL)
				# return false;
				# } * /
				pass

			# Project required?
			# / *ProjectTypes
			# ePrereqProject = (ProjectTypes)
			# pUnitInfo.GetProjectPrereq();
			# if (ePrereqProject != NO_PROJECT)
			# {
			# 	CvProjectEntry * pkProjectInfo = GC.getProjectInfo(ePrereqProject);
			# if (pkProjectInfo)
			# {
			# if (GET_TEAM(getTeam()).getProjectCount(ePrereqProject) == 0)
			# 	{
			# 		GC.getGame().BuildCannotPerformActionHelpText(toolTipSink, "TXT_KEY_NO_ACTION_UNIT_PROJECT_REQUIRED",
			# 		                                              pkProjectInfo->GetDescription());
			# 	if (toolTipSink == NULL)
			# 		return false;

			# Resource Requirements
			resource = unitType.requiredResource()
			if resource is not None:
				if self.numberOfAvailableResource(resource) <= 0:
					return False

			# / * if (pUnitInfo.IsTrade())
			# {
			# if (GetTrade()->GetNumTradeRoutesRemaining(bContinue) <= 0)
			# {
			# GC.getGame().BuildCannotPerformActionHelpText(toolTipSink, "TXT_KEY_TRADE_UNIT_CONSTRUCTION_NO_EXTRA_SLOTS");
			# if (toolTipSink == NULL)
			# 	return false;
			# }
			#
			# DomainTypes
			# eDomain = (DomainTypes)
			# pUnitInfo.GetDomainType();
			# if (!GetTrade()->CanCreateTradeRoute(eDomain))
			# {
			# if (eDomain == DOMAIN_LAND)
			# 	{
			# 		GC.getGame().BuildCannotPerformActionHelpText(toolTipSink, "TXT_KEY_TRADE_UNIT_CONSTRUCTION_NONE_OF_TYPE_LAND");
			# 	}
			# 	else if (eDomain == DOMAIN_SEA)
			# 		{
			# 			GC.getGame().BuildCannotPerformActionHelpText(toolTipSink,
			# 			                                              "TXT_KEY_TRADE_UNIT_CONSTRUCTION_NONE_OF_TYPE_SEA");
			# 		}
			# 		if (toolTipSink == NULL)
			# 			return false;
			# 		}
			# 		} * /

		return True

	def hasCulturalVictory(self, simulation) -> bool:
		if not VictoryType.cultural in simulation.victoryTypes:
			return False

		visitingTourists: int = self.visitingTourists(simulation)
		maxDomesticTourists: int = 0

		for loopPlayer in simulation.players:
			if loopPlayer.isBarbarian() or self == loopPlayer:
				continue

			maxDomesticTourists = max(maxDomesticTourists, loopPlayer.domesticTourists())

		return visitingTourists > maxDomesticTourists

	def hasScienceVictory(self, simulation) -> bool:
		return self.scienceVictoryProgress(simulation) >= 5

	def scienceVictoryProgress(self, simulation) -> int:
		scienceVictoryProgressValue: int = 0

		for city in simulation.citiesOf(self):
			if city.hasProject(ProjectType.launchEarthSatellite):
				scienceVictoryProgressValue += 1

			if city.hasProject(ProjectType.launchMoonLanding):
				scienceVictoryProgressValue += 1

			if city.hasProject(ProjectType.launchMarsColony):
				scienceVictoryProgressValue += 1

			if city.hasProject(ProjectType.exoplanetExpedition):
				scienceVictoryProgressValue += 1

		if self._boostExoplanetExpeditionValue >= 50:
			scienceVictoryProgressValue += 1

		return scienceVictoryProgressValue

	def hasReligiousVictory(self, simulation) -> bool:
		playerReligion = self.religion

		if playerReligion.currentReligion() == ReligionType.none:
			return False

		for loopPlayer in simulation.players:
			if not loopPlayer.isMajorAI() and not loopPlayer.isHuman():
				continue

			if not loopPlayer.majorityOfCitiesFollowsReligion(playerReligion.currentReligion(), simulation):
				return False

		return True

	def visitingTourists(self, simulation) -> int:
		return self.tourism.visitingTourists(simulation)

	def domesticTourists(self) -> int:
		return self.tourism.domesticTourists()

	def currentTourism(self, simulation) -> float:
		return self.tourism.currentTourism(simulation)

	def tourismModifierTowards(self, otherPlayer, simulation) -> int:
		"""At the player level, what is the modifier for tourism between these players?
			in percent / CvPlayerCulture::GetTourismModifierWith
			https://forums.civfanatics.com/threads/how-tourism-is-calculated-and-a-culture-victory-made.605199/"""
		playerGovernmentType: Optional[GovernmentType] = self.government.currentGovernment()
		otherPlayerGovernmentType: Optional[GovernmentType] = otherPlayer.government.currentGovernment()

		if playerGovernmentType is None:
			playerGovernmentType = GovernmentType.chiefdom

		if otherPlayerGovernmentType is None:
			otherPlayerGovernmentType = GovernmentType.chiefdom

		modifier: int = 0

		# Open Borders
		if self.diplomacyAI.isOpenBordersAgreementActiveWith(otherPlayer):
			modifier += 25  # TOURISM_MODIFIER_OPEN_BORDERS

		# Trade Route
		if self.tradeRoutes.hasTradeRouteWith(otherPlayer, simulation) or \
			otherPlayer.tradeRoutes.hasTradeRouteWith(self, simulation):
			modifier += 25  # TOURISM_MODIFIER_TRADE_ROUTE

			# Civic Online Communities provides + 50% tourism to civs you have a trade route with

		# Different Religion
		# ...

		# Enlightenment
		# ...

		# Different Governments
		# (Gov1_factor + Gov2_factor) x Base Government tourist factor
		if playerGovernmentType != otherPlayerGovernmentType:
			differentGovFactor = (playerGovernmentType.tourismFactor() + otherPlayerGovernmentType.tourismFactor()) * 3
			modifier += differentGovFactor

		return modifier

	def doClearBarbarianCampAt(self, tile, simulation):
		if not self.isBarbarian() and not self.isFreeCity():
			# See if we need to remove a temporary dominance zone
			self.tacticalAI.deleteTemporaryZoneAt(tile.point)

			numGold = simulation.handicap.barbarianCampGold()

			tile.setImprovement(ImprovementType.none)

			# check quests
			for quest in self.ownQuests(simulation):
				if quest.questType == CityStateQuestType.destroyBarbarianOutput:
					if quest.location == tile.point and self.leader == quest.leader:
						cityStatePlayer = simulation.cityStatePlayerFor(quest.cityState)
						cityStatePlayer.fulfillQuestBy(self.leader, simulation)

			simulation.doBarbarianCampCleared(self.leader, tile.point)

			self.addMoment(MomentType.barbarianCampDestroyed, simulation=simulation)

			if not self.civics.inspirationTriggeredFor(CivicType.militaryTradition):
				self.civics.triggerInspirationFor(CivicType.militaryTradition, simulation)

			# initiationRites - +50 Faith for each Barbarian Outpost cleared. The unit that cleared the Barbarian
			# Outpost heals +100 HP.
			if self.religion.pantheon() == PantheonType.initiationRites:
				self._faithEarned += 50

			self.treasury.changeGoldBy(float(numGold))

			# If it's the active player then show the popup
			if self == simulation.humanPlayer():
				simulation.userInterface.showTooltip(tile.point, TooltipType.barbarianCampCleared, gold=numGold, delay=3)

	def changeNumberOfAvailableResource(self, resource: ResourceType, change: float):
		self._resourceInventory.addWeight(change, resource)

	def numberOfAvailableResource(self, resource: ResourceType) -> float:
		return self._resourceInventory.weight(resource)

	def numberOfItemsInStockpile(self, resource: ResourceType) -> float:
		return self._resourceStockpile.weight(resource)

	def numberOfBuildingsOfType(self, building: BuildingType, simulation):
		numberOfBuildings = 0

		for city in simulation.citiesOf(self):
			if city.hasBuilding(building):
				numberOfBuildings += 1

		return numberOfBuildings

	def canChangeGovernment(self) -> bool:
		return self._canChangeGovernmentValue

	def faithPurchaseType(self):
		return self._faithPurchaseType

	def greatPeoplePointsFromPolicyCards(self, simulation) -> GreatPersonPoints:
		greatPeoplePointsFromPolicyCards: GreatPersonPoints = GreatPersonPoints()

		# strategos - +2 Great General points per turn.
		if self.government.hasCard(PolicyCardType.strategos):
			greatPeoplePointsFromPolicyCards.greatGeneral += 2

		# inspiration - +2 Great Scientist points per turn.
		if self.government.hasCard(PolicyCardType.inspiration):
			greatPeoplePointsFromPolicyCards.greatScientist += 2

		# revelation - +2 Great Prophet points per turn.
		if self.government.hasCard(PolicyCardType.revelation):
			greatPeoplePointsFromPolicyCards.greatProphet += 2

		# literaryTradition - +2 Great Writer points per turn.
		if self.government.hasCard(PolicyCardType.literaryTradition):
			greatPeoplePointsFromPolicyCards.greatWriter += 2

		# navigation - +2 Great Admiral points per turn.
		if self.government.hasCard(PolicyCardType.navigation):
			greatPeoplePointsFromPolicyCards.greatAdmiral += 2

		# travelingMerchants - +2 Great Merchant points per turn.
		if self.government.hasCard(PolicyCardType.travelingMerchants):
			greatPeoplePointsFromPolicyCards.greatMerchant += 2

		# invention - +4 Great Engineer points per turn. +2 additional Great Engineer points for every Workshop.
		if self.government.hasCard(PolicyCardType.invention):
			greatPeoplePointsFromPolicyCards.greatEngineer += 4

		# frescoes - +2 Great Artist points per turn. +2 additional Great Artist points for every Art Museum.
		if self.government.hasCard(PolicyCardType.frescoes):
			greatPeoplePointsFromPolicyCards.greatArtist += 2

		# nobelPrize - +4 Great Scientist points per turn.
		if self.government.hasCard(PolicyCardType.nobelPrize):
			greatPeoplePointsFromPolicyCards.greatArtist += 4

		return greatPeoplePointsFromPolicyCards

	def addGovernorTitle(self):
		self.governors.addTitle()

	def canPurchaseUnitInAnyCity(self, unitType: UnitType, yieldType: YieldType, simulation) -> bool:
		for city in simulation.citiesOf(self):
			if city.canPurchaseUnit(unitType, yieldType, simulation):
				return True

		return False

	def canPurchaseBuildingInAnyCity(self, buildingType: BuildingType, yieldType: YieldType, simulation) -> bool:
		for city in simulation.citiesOf(self):
			if city.canPurchaseBuilding(buildingType, yieldType, simulation):
				return True

		return False

	def setEra(self, era: EraType, simulation):
		techs = self.techs

		if era <= self._currentEraValue:
			raise Exception("era should be greater")

		self._currentEraValue = era
		self.selectCurrentAge(simulation)

		self.moments.resetEraScore()

		# Seoul suzerain bonus
		# When you enter a new era, earn 1 random Eureka from that era.
		if self.isSuzerainOf(CityStateType.seoul, simulation):
			possibleTechs = list(filter(lambda t: t.era() == self._currentEraValue and not techs.eurekaTriggeredFor(t), list(TechType)))  # TechType.all

			if len(possibleTechs) > 0:
				selectedTech = random.choice(possibleTechs)
				techs.triggerEurekaFor(selectedTech, simulation)

		if not self.isHuman():
			dedications: [DedicationType] = list(filter(lambda d: era in d.eras(), list(DedicationType)))
			selectable = self._currentAgeValue.numDedicationsSelectable()
			selected: [DedicationType] = []
			for _ in range(selectable):
				selectedDedication = random.choice(dedications)
				selected.append(selectedDedication)
				dedications = list(filter(lambda d: d != selectedDedication, dedications))

			self.selectDedications(selected)

		return

	def selectDedications(self, dedications: [DedicationType]):
		self._currentDedicationsValue = dedications

	def currentDedications(self) -> [DedicationType]:
		return self._currentDedicationsValue

	def selectCurrentAge(self, simulation):
		nextAge = self.estimateNextAge(simulation)

		if nextAge == AgeType.dark:
			self._numberOfDarkAgesValue += 1
			self.addMoment(MomentType.darkAgeBegins, simulation=simulation)
		elif nextAge == AgeType.golden:
			self._numberOfGoldenAgesValue += 1
			self.addMoment(MomentType.goldenAgeBegins, simulation=simulation)
			simulation.addReplayEvent(ReplayEventType.goldenAge, "TXT_KEY_NOTIFICATION_GOLDEN_AGE_BEGUN", invalidHexPoint)

		self._currentAgeValue = nextAge

		return

	def estimateNextAge(self, simulation) -> AgeType:
		eraScore: int = self.eraScore()

		thresholds = self.ageThresholds(simulation)

		if eraScore < thresholds.lower:
			return AgeType.dark
		elif eraScore >= thresholds.upper:
			return AgeType.golden
		else:
			return AgeType.normal

	def eraScore(self) -> int:
		return self.moments.eraScore()

	def ageThresholds(self, simulation) -> AgeThresholds:
		"""https://civilization.fandom.com/wiki/Age_(Civ6)"""
		numberOfGoldenAges = self._numberOfGoldenAgesValue
		numberOfDarkAges = self._numberOfDarkAgesValue
		cities = len(simulation.citiesOf(self))
		lowerThreshold = 11 + numberOfGoldenAges * 5 - numberOfDarkAges * 5 + cities
		upperThreshold = lowerThreshold + 12

		return AgeThresholds(lowerThreshold, upperThreshold)

	def resetQuests(self, simulation):
		for quest in self._quests:
			player = simulation.playerFor(quest.leader)

			if player is None:
				continue

			if player.isHuman():
				player.notifications.addNotification(NotificationType.questCityStateObsolete, cityState=quest.cityState, quest=quest.questType)

		self._quests = []

	def hasActiveGoldQuest(self, simulation) -> bool:
		for quest in self.ownQuests(simulation):
			if quest.questType == CityStateQuestType.gold:
				return True

		return False

	def isBarbarianCampDiscoveredAt(self, point: HexPoint) -> bool:
		return point in self._discoveredBarbarianCampLocations

	def discoverBarbarianCampAt(self, point: HexPoint):
		self._discoveredBarbarianCampLocations.append(point)

		self.notifications.addNotification(NotificationType.barbarianCampDiscovered, location=point)

	def forgetDiscoverBarbarianCampAt(self, point: HexPoint):
		self._discoveredBarbarianCampLocations = list(filter(lambda c: c != point, self._discoveredBarbarianCampLocations))

	def ownQuests(self, simulation) -> [CityStateQuest]:
		return []  # fixme

	def canDeclareWarTowards(self, otherPlayer) -> bool:
		return self.diplomacyAI.canDeclareWarTowards(otherPlayer)

	def deleteOperation(self, operation: Operation):
		self.operations.deleteOperation(operation)
		return

	def operationsOfType(self, operationType: UnitOperationType) -> [Operation]:
		return self.operations.operationsOfType(operationType)

	def numberOfOperationsOfType(self, operationType: UnitOperationType) -> int:
		return self.operations.numberOfOperationsOfType(operationType)

	def hasOperationsOfType(self, operationType: UnitOperationType) -> bool:
		return self.operations.hasOperationsOfType(operationType)

	def numberOfUnitsNeededToBeBuilt(self) -> int:
		return self.operations.numberOfUnitsNeededToBeBuilt()

	def forgetDiscoverBarbarianCampAt(self, point: HexPoint):
		self._discoveredBarbarianCampLocations = list(filter(lambda d: d != point, self._discoveredBarbarianCampLocations))

	def plotDangerAt(self, point: HexPoint) -> float:
		return self.dangerPlotsAI.dangerAt(point)

	def closestFriendlyCity(self, point: HexPoint, radius: int, simulation) -> Optional[City]:
		bestValue: int = 10000000
		bestCity: Optional[City] = None

		for pt in HexArea(point, radius):
			city = simulation.cityAt(pt)

			if city is None:
				continue

			if city.player == self:
				dist = pt.distance(city.location)

				if dist < bestValue:
					bestValue = dist
					bestCity = city

		return bestCity

	def doUnitKilledCombat(self, otherPlayer, unitType: UnitType):
		"""Do effects when a unit is killed in combat"""
		pass

	def assignEnvoyTo(self, cityState: CityStateType, simulation) -> bool:
		playerEnvoys = self.envoys
		cityStatePlayer = simulation.cityStatePlayerFor(cityState)

		previouslyAssignedEnvoys = playerEnvoys.envoysIn(cityState)
		result = playerEnvoys.assignEnvoyTo(cityState)

		if result:
			if previouslyAssignedEnvoys == 0:
				# diplomaticLeague - The first Envoy you send to each city-state counts as two Envoys.
				if self.government.hasCard(PolicyCardType.diplomaticLeague):
					self.changeUnassignedEnvoysBy(1)
					playerEnvoys.assignEnvoyTo(cityState)  # ignore return value

			cityStateSuzerain = simulation.player(cityStatePlayer.suzerain()) if cityStatePlayer.suzerain() is not None else None

			# check if player is suzerain
			if playerEnvoys.envoysIn(cityState) >= 3 and self != cityStateSuzerain:
				playerWithMostEnvoys = simulation.playerWithMostEnvoysIn(cityState)
				if playerWithMostEnvoys is not None:
					if playerWithMostEnvoys == self:
						cityStatePlayer.setSuzerain(self.leader)

						if not simulation.anyHasMoment(MomentType.cityStatesFirstSuzerain):
							self.addMoment(MomentType.cityStatesFirstSuzerain, cityState=cityState, simulation=simulation)
				else:
					# no player with most envoys
					cityStatePlayer.resetSuzerain()

		return result

	def economicMight(self, simulation) -> int:
		# Default to 5 so that a fluctuation in Population early doesn't swing things wildly
		might = 5

		for city in simulation.citiesOf(self):
			might += city.population()

		return might

	def totalPopulation(self, simulation) -> int:
		pop: int = 0

		for city in simulation.citiesOf(self):
			pop += city.population()

		return pop

	def questFor(self, leader: LeaderType) -> Optional[CityStateQuest]:
		if not self.isCityState():
			return None

		return next(filter(lambda q: q.leader == leader, self._quests), None)

	def turnsSinceMeetingWith(self, otherPlayer) -> int:
		return self.diplomacyAI.playerDict.turnsSinceMeetingWith(otherPlayer)

	def numberOfNukeUnits(self, simulation) -> int:
		# fixme
		return 0

	def unhappiness(self, simulation) -> int:
		"""number of unhappy cities"""
		unhappyCities: int = 0

		for city in simulation.citiesOf(self):
			if city.loyaltyState() in [LoyaltyState.disloyal, LoyaltyState.unrest]:
				unhappyCities += 1

		return unhappyCities

	def isEmpireUnhappy(self, simulation) -> bool:
		return self.unhappiness(simulation) > 0

	def excessHappiness(self) -> int:
		return 0

	def buyPlotCost(self) -> int:
		cost = 50  # PLOT_BASE_COST
		cost += self.numberOfPlotsBought() * 5  # PLOT_ADDITIONAL_COST_PER_PLOT

		# Cost Mod (Policies, etc.)
		# if GetPlotGoldCostMod() != 0:
		#	iCost *= (100 + GetPlotGoldCostMod());
		#	iCost /= 100;

		return cost

	def numberOfPlotsBought(self) -> int:
		return self._numberOfPlotsBoughtValue

	def changeNumberOfPlotsBought(self, delta: int):
		self._numberOfPlotsBoughtValue += delta

	def isForcePeaceWith(self, otherPlayer) -> bool:
		return self.diplomacyAI.playerDict.isForcePeaceWith(otherPlayer)

	def updateForcePeaceWith(self, otherPlayer, value: bool):
		self.diplomacyAI.playerDict.updateForcePeaceWith(otherPlayer, value)

	def doGreatPersonExpended(self, unitType: UnitType):
		"""Do effects when a GP is consumed"""
		if unitType not in UnitType.greatPersons():
			raise Exception(f'{unitType} is not a great person')

		# Gold gained
		iExpendGold = self.greatPersonExpendedGold()
		if iExpendGold > 0:
			self.treasury.changeGoldBy(iExpendGold)

			if self.isHuman():
				# Update Steam stat and check achievement
				# HALICARNASSUS_ACHIEVEMENT_GOLD = 1000;
				# iHalicarnassus = GC.getInfoTypeForString("BUILDINGCLASS_MAUSOLEUM_HALICARNASSUS");
				# Does player have DLC_06, and if so, do they have the Mausoleum of Halicarnassus?
				pass

		# Faith gained
		religionFounded: ReligionType = self.religion.currentReligion()
		if religionFounded != ReligionType.none:
			iFaith = self.religion.greatPersonExpendedFaith()

			# if iFaith > 0:
			# 	iFaith *= GC.getGame().getGameSpeedInfo().getTrainPercent();
			# 	iFaith /= 100;

			self.religion.changeFaith(iFaith)

		return

	def greatPersonExpendedGold(self) -> int:
		return self._greatPersonExpendGold

	def cityWithWonder(self, wonderType: WonderType, simulation) -> Optional[City]:
		for loopCity in simulation.citiesOf(self):
			if loopCity.hasWonder(wonderType):
				return loopCity

		return None

	def hasTradeRouteFrom(self, fromPoint: HexPoint, toPoint: HexPoint) -> bool:
		return self.tradeRoutes.hasTradeRouteFrom(fromPoint, toPoint)

	def hasEverEstablishedTradingPostWith(self, targetPlayer) -> bool:
		return hash(targetPlayer) in self._establishedTradingPosts

	def markEstablishedTradingPostWith(self, targetPlayer):
		if not self.hasEverEstablishedTradingPostWith(targetPlayer):
			self._establishedTradingPosts.append(hash(targetPlayer))

	def doCivilianReturnLogic(self, returned: bool, toPlayer, capturedUnit, simulation):
		"""Someone sent us a present!"""
		if capturedUnit is None:
			return

		# Kill any units this guy is transporting
		for loopUnit in simulation.unitsAt(capturedUnit.location):
			if loopUnit.transportUnit() == capturedUnit:
				loopUnit.doKill(delayed=True, otherPlayer=None, simulation=simulation)

		# What are the details for the new unit?
		newUnitType: UnitType = capturedUnit.unitType

		if not returned:
			newUnitType = capturedUnit.captureUnitType(self.leader.civilization())

		capturedUnitLocation: HexPoint = capturedUnit.location

		# Returns to the previous owner
		if returned:
			capturedUnit.doKill(delayed=True, otherPlayer=None, simulation=simulation)
			newUnit = Unit(capturedUnitLocation, newUnitType, self)

			if not newUnit.jumpToNearestValidPlotWithin(2, simulation):
				newUnit.doKill(delayed=False, otherPlayer=None, simulation=simulation)  # Could not find a spot!

			# Returned to a city-state
			if toPlayer is not None and toPlayer.isCityState():
				iInfluence = 45  # RETURN_CIVILIAN_FRIENDSHIP
				toPlayer.minorCivAI.changeFriendshipWithMajor(self, iInfluence)
			elif toPlayer is not None and not toPlayer.isHuman():  # Returned to major power (but not human)
				toPlayer.diplomacyAI.changeNumberOfCiviliansReturnedToMeBy(self, 1)
		else:  # Kept for oneself
			# Make a new unit because the kind we should capture doesn't match (e.g. Settler to Worker)
			if newUnitType != capturedUnit.unitType:
				capturedUnit.doKill(delayed=True, otherPlayer=None, simulation=simulation)
				newUnit = Unit(capturedUnitLocation, newUnitType, self)
				newUnit.finishMoves()

		return

	def isCityAlreadyTargeted(self, city, domain: UnitDomainType, percentToTarget: int, simulation) -> bool:
		"""Is an existing operation already going after this city?"""
		for operation in self.operations:
			if operation.targetPosition == city.location and operation.percentFromMusterPointToTarget(simulation) < percentToTarget:
				# Naval attacks are mixed land/naval operations
				if (domain == UnitDomainType.none or domain == UnitDomainType.sea) and operation.isMixedLandNavalOperation():
					return True

				if (domain == UnitDomainType.none or domain == UnitDomainType.land) and not operation.isMixedLandNavalOperation():
					return True

		return False

	def changeNumberOfItemsInStockpileOf(self, resource: ResourceType, delta: int):
		self._resourceStockpile.addWeight(delta, resource)
		return

	def isEnemyOf(self, otherPlayer) -> bool:
		# barbarians are always enemies
		if self.isBarbarian() or otherPlayer.isBarbarian():
			return True

		return self.isAtWarWith(otherPlayer)

	def isAllowDelegationTradingAllowed(self) -> bool:
		return True

	def isAllowEmbassyTradingAllowed(self) -> bool:
		return self.civics.hasCivic(CivicType.diplomaticService)

	def canChangeWarPeaceTowards(self, otherPlayer) -> bool:
		if self.isAlliedWith(otherPlayer):
			return False

		# if (GC.getGame().isOption(GAMEOPTION_NO_CHANGING_WAR_PEACE)):
		# 	return False
		#
		# if (GC.getGame().isOption(GAMEOPTION_ALWAYS_PEACE)):
		# 	return False
		#
		# if (GC.getGame().isOption(GAMEOPTION_ALWAYS_WAR))
		# 	return False

		if self == otherPlayer:
			return False

		if (self.isPermanentWarPeaceWith(otherPlayer) or otherPlayer.isPermanentWarPeaceWith(self)):
			return False

		return True

	def isPermanentWarPeaceWith(self, otherPlayer) -> bool:
		return False

	def canChangeWarPeaceWith(self, otherPlayer) -> bool:
		return self.diplomacyAI.canChangeWarPeaceWith(otherPlayer)

	def turnsSinceSettledLastCity(self, simulation) -> int:
		lastCityFoundingTurn: int = 0

		for city in simulation.citiesOf(self):
			lastCityFoundingTurn = max(lastCityFoundingTurn, city.gameTurnFoundedValue)

		return simulation.currentTurn - lastCityFoundingTurn

	def isOpenBordersTradingAllowed(self) -> bool:
		return self.civics.hasCivic(CivicType.earlyEmpire)

	def isResearchAgreementTradingAllowedWith(self, otherPlayer) -> bool:
		return self.diplomacyAI.hasEstablishedEmbassyTo(otherPlayer) and self.techs.hasTech(TechType.scientificTheory)

	def hasEstablishedEmbassyTo(self, otherPlayer) -> bool:
		return self.diplomacyAI.hasEstablishedEmbassyTo(otherPlayer)

	def hasSentDelegationTo(self, otherPlayer) -> bool:
		return self.diplomacyAI.hasSentDelegationTo(otherPlayer)

	def isCramped(self) -> bool:
		"""Is the player is cramped in his current area?"""
		return self._cramped

	def isResourceObsolete(self, resource: ResourceType) -> bool:
		"""Can we use this resource?"""
		# If this is a luxury or bonus resource it doesn't go obsolete
		if resource != ResourceUsage.strategic:
			return False

		obsoleteEra: Optional[EraType] = resource.peakEra()

		# AI will always trade for this
		if obsoleteEra is None:
			return False

		# Not obsolete yet
		if self._currentEraValue < obsoleteEra:
			return False

		return True
