from typing import Optional, Union

from smarthexboard.smarthexboardlib.game.cityStates import CityStateType
from smarthexboard.smarthexboardlib.game.civilizations import LeaderType, CivilizationType
from smarthexboard.smarthexboardlib.game.greatPersons import GreatPersonType
from smarthexboard.smarthexboardlib.game.moments import MomentType
from smarthexboard.smarthexboardlib.game.religions import PantheonType, ReligionType
from smarthexboard.smarthexboardlib.game.wonders import WonderType
from smarthexboard.smarthexboardlib.map.base import HexPoint
from smarthexboard.smarthexboardlib.core.base import ExtendedEnum, InvalidEnumError
from smarthexboard.smarthexboardlib.map.improvements import ImprovementType


class NotificationTypeData:
	def __init__(self, name: str, message: str):
		self.name = name
		self.message = message


class NotificationType:
	pass


class NotificationType(ExtendedEnum):
	turn = 'turn'  # 0

	generic = 'generic'  # 1

	techNeeded = 'techNeeded'  # 2
	civicNeeded = 'civicNeeded'  # 3
	productionNeeded = 'productionNeeded'  # (cityName: String, location: HexPoint)  # 4
	canChangeGovernment = 'canChangeGovernment'  # 5
	policiesNeeded = 'policiesNeeded'  # 6
	canFoundPantheon = 'canFoundPantheon'  # 7
	governorTitleAvailable = 'governorTitleAvailable'  # 8

	cityGrowth = 'cityGrowth'  # (cityName: String, population: Int, location: HexPoint)  # 9
	starving = 'starving'  # (cityName: String, location: HexPoint)  # 10

	diplomaticDeclaration = 'diplomaticDeclaration'  # (leader: LeaderType) # 11

	war = 'war'  # (leader: LeaderType)  # 12
	enemyInTerritory = 'enemyInTerritory'  # (location: HexPoint, cityName: String)  # 13

	unitPromotion = 'unitPromotion'  # (location: HexPoint)  # 14
	unitNeedsOrders = 'unitNeedsOrders'  # (location: HexPoint)  # 15
	unitDied = 'unitDied'  # (location: HexPoint)  # 16

	greatPersonJoined = 'greatPersonJoined'  # parameter: location # 17

	canRecruitGreatPerson = 'canRecruitGreatPerson'  # (greatPerson: GreatPerson)  # 18

	cityLost = 'cityLost'  # (location: HexPoint)  # 19
	goodyHutDiscovered = 'goodyHutDiscovered'  # (location: HexPoint)  # 20
	barbarianCampDiscovered = 'barbarianCampDiscovered'  # (location: HexPoint)  # 21

	waiting = 'waiting'  # 22

	metCityState = 'metCityState'  # (cityState: CityStateType, first: Bool)  # 23
	questCityStateFulfilled = 'questCityStateFulfilled'  # (cityState: CityStateType, quest: CityStateQuestType)  # 24
	questCityStateObsolete = 'questCityStateObsolete'  # (cityState: CityStateType, quest: CityStateQuestType)  # 25
	questCityStateGiven = 'questCityStateGiven'  # (cityState: CityStateType, quest: CityStateQuestType)  # 26

	momentAdded = 'momentAdded'  # (type: MomentType) 27
	tradeRouteCapacityIncreased = 'tradeRouteCapacityIncreased'  # 28

	naturalWonderDiscovered = 'naturalWonderDiscovered'  # (location: HexPoint) #29
	continentDiscovered = 'continentDiscovered'  # (location: HexPoint, continentName: String)  # 30
	wonderBuilt = 'wonderBuilt'  # (wonder: WonderType, civilization: CivilizationType) #31

	cityCanShoot = 'cityCanShoot'  # (cityName: String, location: HexPoint) #32
	cityAcquired = 'cityAcquired'  # (cityName: String, location: HexPoint) # 33

	envoyEarned = 'envoyEarned'  # 34

	religionFoundedActivePlayer = 'religionFoundedActivePlayer'  # 35
	religionFoundedOther = 'religionFoundedOther'  # 36
	canSelectBeliefs = 'canSelectBeliefs'  # 37
	peace = 'peace'  # 38

	dealExpiredGoldPerTurnFromUs = 'dealExpiredGoldPerTurnFromUs'  # 39
	dealExpiredGoldPerTurnToUs = 'dealExpiredGoldPerTurnToUs'  # 40
	dealExpiredResourceFromUs = 'dealExpiredResourceFromUs'  # 41
	dealExpiredResourceToUs = 'dealExpiredResourceToUs'  # 42
	dealExpiredOpenBordersFromUs = 'dealExpiredOpenBordersFromUs'  # 43
	dealExpiredOpenBordersToUs = 'dealExpiredOpenBordersToUs'  # 44
	dealExpiredDefensivePactFromUs = 'dealExpiredDefensivePactFromUs'  # 45
	dealExpiredDefensivePactToUs = 'dealExpiredDefensivePactToUs'  # 46
	dealExpiredResearchAgreement = 'dealExpiredResearchAgreement'  # 47
	dealExpiredPeaceTreaty = 'dealExpiredPeaceTreaty'  # 48

	@staticmethod
	def fromName(notificationName: str) -> NotificationType:
		if notificationName == 'NotificationType.turn' or notificationName == 'turn':
			return NotificationType.turn

		if notificationName == 'NotificationType.generic' or notificationName == 'generic':
			return NotificationType.generic

		if notificationName == 'NotificationType.techNeeded' or notificationName == 'techNeeded':
			return NotificationType.techNeeded
		if notificationName == 'NotificationType.civicNeeded' or notificationName == 'civicNeeded':
			return NotificationType.civicNeeded
		if notificationName == 'NotificationType.canChangeGovernment' or notificationName == 'canChangeGovernment':
			return NotificationType.canChangeGovernment
		if notificationName == 'NotificationType.policiesNeeded' or notificationName == 'policiesNeeded':
			return NotificationType.policiesNeeded
		if notificationName == 'NotificationType.canFoundPantheon' or notificationName == 'canFoundPantheon':
			return NotificationType.canFoundPantheon
		if notificationName == 'NotificationType.governorTitleAvailable' or notificationName == 'governorTitleAvailable':
			return NotificationType.governorTitleAvailable

		# cityGrowth
		# starving
		#
		# diplomaticDeclaration
		#
		# war
		# enemyInTerritory
		#
		# unitPromotion
		# unitNeedsOrders
		# unitDied
		#
		# greatPersonJoined
		#
		# canRecruitGreatPerson
		#
		# cityLost
		# goodyHutDiscovered
		# barbarianCampDiscovered
		#
		# waiting
		#
		# metCityState
		# questCityStateFulfilled
		# questCityStateObsolete
		# questCityStateGiven
		#
		# momentAdded
		# tradeRouteCapacityIncreased
		#
		# naturalWonderDiscovered
		# continentDiscovered
		# wonderBuilt
		#
		# cityCanShoot
		# cityAcquired
		#
		# envoyEarned
		if notificationName == 'NotificationType.religionFoundedActivePlayer' or notificationName == 'religionFoundedActivePlayer':
			return NotificationType.religionFoundedActivePlayer
		if notificationName == 'NotificationType.religionFoundedOther' or notificationName == 'religionFoundedOther':
			return NotificationType.religionFoundedOther
		if notificationName == 'NotificationType.canSelectBeliefs' or notificationName == 'canSelectBeliefs':
			return NotificationType.canSelectBeliefs
		if notificationName == 'NotificationType.peace' or notificationName == 'peace':
			return NotificationType.peace

		if notificationName == 'NotificationType.dealExpiredGoldPerTurnFromUs' or notificationName == 'dealExpiredGoldPerTurnFromUs':
			return NotificationType.dealExpiredGoldPerTurnFromUs
		if notificationName == 'NotificationType.dealExpiredGoldPerTurnToUs' or notificationName == 'dealExpiredGoldPerTurnToUs':
			return NotificationType.dealExpiredGoldPerTurnToUs
		if notificationName == 'NotificationType.dealExpiredResourceFromUs' or notificationName == 'dealExpiredResourceFromUs':
			return NotificationType.dealExpiredResourceFromUs
		if notificationName == 'NotificationType.dealExpiredResourceToUs' or notificationName == 'dealExpiredResourceToUs':
			return NotificationType.dealExpiredResourceToUs
		if notificationName == 'NotificationType.dealExpiredOpenBordersFromUs' or notificationName == 'dealExpiredOpenBordersFromUs':
			return NotificationType.dealExpiredOpenBordersFromUs
		if notificationName == 'NotificationType.dealExpiredOpenBordersToUs' or notificationName == 'dealExpiredOpenBordersToUs':
			return NotificationType.dealExpiredOpenBordersToUs
		if notificationName == 'NotificationType.dealExpiredDefensivePactFromUs' or notificationName == 'dealExpiredDefensivePactFromUs':
			return NotificationType.dealExpiredDefensivePactFromUs
		if notificationName == 'NotificationType.dealExpiredDefensivePactToUs' or notificationName == 'dealExpiredDefensivePactToUs':
			return NotificationType.dealExpiredDefensivePactToUs
		if notificationName == 'NotificationType.dealExpiredResearchAgreement' or notificationName == 'dealExpiredResearchAgreement':
			return NotificationType.dealExpiredResearchAgreement
		if notificationName == 'NotificationType.dealExpiredPeaceTreaty' or notificationName == 'dealExpiredPeaceTreaty':
			return NotificationType.dealExpiredPeaceTreaty

		raise Exception(f'No matching case for notificationName: "{notificationName}"')

	def title(self) -> str:
		return self._data().name

	def message(self) -> str:
		return self._data().message

	def _data(self) -> NotificationTypeData:
		if self == NotificationType.turn:  # 0
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_TURN_NAME',
				message='KEY_TXT_NOTIFICATION_TURN_MESSAGE'
			)

		elif self == NotificationType.generic:  # 1
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_GENERIC_NAME',
				message='KEY_TXT_NOTIFICATION_GENERIC_MESSAGE'
			)

		elif self == NotificationType.techNeeded:  # 2
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_TECH_NEEDED_NAME',
				message='KEY_TXT_NOTIFICATION_TECH_NEEDED_MESSAGE'
			)
		elif self == NotificationType.civicNeeded:  # 3
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_CIVIC_NEEDED__NAME',
				message='KEY_TXT_NOTIFICATION_CIVIC_NEEDED_MESSAGE'
			)
		elif self == NotificationType.productionNeeded:  # (cityName: String, location: HexPoint)  # 4
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_PRODUCTION_NEEDED_NAME',
				message='KEY_TXT_NOTIFICATION_PRODUCTION_NEEDED_MESSAGE'
			)
		elif self == NotificationType.canChangeGovernment:  # 5
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_CAN_CHANGE_GOVERNMENT_NAME',
				message='KEY_TXT_NOTIFICATION_CAN_CHANGE_GOVERNMENT_MESSAGE'
			)
		elif self == NotificationType.policiesNeeded:  # 6
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_POLICIES_NEEDED_NAME',
				message='KEY_TXT_NOTIFICATION_POLICIES_NEEDED_MESSAGE'
			)
		elif self == NotificationType.canFoundPantheon:  # 7
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_CAN_FOUND_PANTHEON_NAME',
				message='KEY_TXT_NOTIFICATION_CAN_FOUND_PANTHEON_MESSAGE'
			)
		elif self == NotificationType.governorTitleAvailable:  # 8
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_GOVERNOR_TITLE_AVAILABLE_NAME',
				message='KEY_TXT_NOTIFICATION_GOVERNOR_TITLE_AVAILABLE_MESSAGE'
			)

		elif self == NotificationType.cityGrowth:  # (cityName: String, population: Int, location: HexPoint)  # 9
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_CITY_GROWTH_NAME',
				message='KEY_TXT_NOTIFICATION_CITY_GROWTH_MESSAGE'
			)
		elif self == NotificationType.starving:  # (cityName: String, location: HexPoint)  # 10
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_STARVING_NAME',
				message='KEY_TXT_NOTIFICATION_STARVING_MESSAGE'
			)

		elif self == NotificationType.diplomaticDeclaration:  # (leader: LeaderType) # 11
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_DIPLOMATIC_DECLARATION_NAME',
				message='KEY_TXT_NOTIFICATION_DIPLOMATIC_DECLARATION_MESSAGE'
			)

		elif self == NotificationType.war:  # (leader: LeaderType)  # 12
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_WAR_NAME',
				message='KEY_TXT_NOTIFICATION_WAR_MESSAGE'
			)
		elif self == NotificationType.enemyInTerritory:  # (location: HexPoint, cityName: String)  # 13
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_ENEMY_IN_TERRITORY_NAME',
				message='KEY_TXT_NOTIFICATION_ENEMY_IN_TERRITORY_MESSAGE'
			)

		elif self == NotificationType.unitPromotion:  # (location: HexPoint)  # 14
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_UNIT_PROMOTION_NAME',
				message='KEY_TXT_NOTIFICATION_UNIT_PROMOTION_MESSAGE'
			)
		elif self == NotificationType.unitNeedsOrders:  # (location: HexPoint)  # 15
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_UNIT_NEEDS_ORDERS_NAME',
				message='KEY_TXT_NOTIFICATION_UNIT_NEEDS_ORDERS_MESSAGE'
			)
		elif self == NotificationType.unitDied:  # (location: HexPoint)  # 16
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_UNIT_DIED_NAME',
				message='KEY_TXT_NOTIFICATION_UNIT_DIED_MESSAGE'
			)

		elif self == NotificationType.greatPersonJoined:  # parameter: location # 17
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_GREAT_PERSON_JOINED_NAME',
				message='KEY_TXT_NOTIFICATION_GREAT_PERSON_JOINED_MESSAGE'
			)

		elif self == NotificationType.canRecruitGreatPerson:  # (greatPerson: GreatPerson)  # 18
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_CAN_RECRUIT_GREAT_PERSON_NAME',
				message='KEY_TXT_NOTIFICATION_CAN_RECRUIT_GREAT_PERSON_MESSAGE'
			)

		elif self == NotificationType.cityLost:  # (location: HexPoint)  # 19
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_CITY_LOST_NAME',
				message='KEY_TXT_NOTIFICATION_CITY_LOST_MESSAGE'
			)
		elif self == NotificationType.goodyHutDiscovered:  # (location: HexPoint)  # 20
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_GOODY_HUT_DISCOVERED_NAME',
				message='KEY_TXT_NOTIFICATION_GOODY_HUT_DISCOVERED_MESSAGE'
			)
		elif self == NotificationType.barbarianCampDiscovered:  # (location: HexPoint)  # 21
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_BARBARIAN_CAMP_DISCOVERED_NAME',
				message='KEY_TXT_NOTIFICATION_BARBARIAN_CAMP_DISCOVERED_MESSAGE'
			)

		elif self == NotificationType.waiting:  # 22
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_WAITING_NAME',
				message='KEY_TXT_NOTIFICATION_WAITING_MESSAGE'
			)

		elif self == NotificationType.metCityState:  # (cityState: CityStateType, first: Bool)  # 23
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_MET_CITY_STATE_NAME',
				message='KEY_TXT_NOTIFICATION_MET_CITY_STATE_MESSAGE'
			)
		elif self == NotificationType.questCityStateFulfilled:  # (cityState: CityStateType, quest: CityStateQuestType)  # 24
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_CITY_STATE_QUEST_FULFILLED_NAME',
				message='KEY_TXT_NOTIFICATION_CITY_STATE_QUEST_FULFILLED_MESSAGE'
			)
		elif self == NotificationType.questCityStateObsolete:  # (cityState: CityStateType, quest: CityStateQuestType)  # 25
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_CITY_STATE_QUEST_OBSOLETE_NAME',
				message='KEY_TXT_NOTIFICATION_CITY_STATE_QUEST_OBSOLETE_MESSAGE'
			)
		elif self == NotificationType.questCityStateGiven:  # (cityState: CityStateType, quest: CityStateQuestType)  # 26
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_CITY_STATE_QUEST_GIVEN_NAME',
				message='KEY_TXT_NOTIFICATION_CITY_STATE_QUEST_GIVEN_MESSAGE'
			)

		elif self == NotificationType.momentAdded:  # (type: MomentType) 27
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_MOMENT_ADDED_NAME',
				message='KEY_TXT_NOTIFICATION_MOMENT_ADDED_MESSAGE'
			)
		elif self == NotificationType.tradeRouteCapacityIncreased:  # 28
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_TRADE_ROUTE_CAPACITY_INCREASED_NAME',
				message='KEY_TXT_NOTIFICATION_TRADE_ROUTE_CAPACITY_INCREASED_MESSAGE'
			)

		elif self == NotificationType.naturalWonderDiscovered:  # (location: HexPoint) #29
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_NATURAL_WONDER_DISCOVERED_NAME',
				message='KEY_TXT_NOTIFICATION_NATURAL_WONDER_DISCOVERED_MESSAGE'
			)
		elif self == NotificationType.continentDiscovered:  # (location: HexPoint, continentName: String)  # 30
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_CONTINENT_DISCOVERED_NAME',
				message='KEY_TXT_NOTIFICATION_CONTINENT_DISCOVERED_MESSAGE'
			)
		elif self == NotificationType.wonderBuilt:  # (wonder: WonderType, civilization: CivilizationType) #31
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_WONDER_BUILT_NAME',
				message='KEY_TXT_NOTIFICATION_WONDER_BUILT_MESSAGE'
			)

		elif self == NotificationType.cityCanShoot:  # (cityName: String, location: HexPoint) #32
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_CITY_CAN_SHOOT_NAME',
				message='KEY_TXT_NOTIFICATION_CITY_CAN_SHOOT_MESSAGE'
			)
		elif self == NotificationType.cityAcquired:  # (cityName: String, location: HexPoint) #33
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_CITY_ACQUIRED_NAME',
				message='KEY_TXT_NOTIFICATION_CITY_ACQUIRED_MESSAGE'
			)

		elif self == NotificationType.envoyEarned:  # 34
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_ENVOY_EARNED_NAME',
				message='KEY_TXT_NOTIFICATION_ENVOY_EARNED_MESSAGE'
			)

		elif self == NotificationType.religionFoundedActivePlayer:  # 35
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_RELIGION_FOUNDED_ACTIVE_PLAYER_NAME',
				message='KEY_TXT_NOTIFICATION_RELIGION_FOUNDED_ACTIVE_PLAYER_MESSAGE'
			)
		elif self == NotificationType.religionFoundedOther:  # 36
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_RELIGION_FOUNDED_OTHER_NAME',
				message='KEY_TXT_NOTIFICATION_RELIGION_FOUNDED_OTHER_MESSAGE'
			)
		elif self == NotificationType.canSelectBeliefs:  # 37
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_CAN_SELECT_BELIEFS_NAME',
				message='KEY_TXT_NOTIFICATION_CAN_SELECT_BELIEFS_MESSAGE'
			)
		elif self == NotificationType.peace:  # 38
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_PEACE_NAME',
				message='KEY_TXT_NOTIFICATION_PEACE_MESSAGE'
			)

		elif self == NotificationType.dealExpiredGoldPerTurnFromUs:  # 39
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_DEAL_EXPIRED_GOLD_PER_TURN_FROM_US_NAME',
				message='KEY_TXT_NOTIFICATION_DEAL_EXPIRED_GOLD_PER_TURN_FROM_US_MESSAGE'
			)
		elif self == NotificationType.dealExpiredGoldPerTurnToUs:  # 40
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_DEAL_EXPIRED_GOLD_PER_TURN_TO_US_NAME',
				message='KEY_TXT_NOTIFICATION_DEAL_EXPIRED_GOLD_PER_TURN_TO_US_MESSAGE'
			)
		elif self == NotificationType.dealExpiredResourceFromUs:  # 41
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_DEAL_EXPIRED_RESOURCE_FROM_US_NAME',
				message='KEY_TXT_NOTIFICATION_DEAL_EXPIRED_RESOURCE_FROM_US_MESSAGE'
			)
		elif self == NotificationType.dealExpiredResourceToUs:  # 42
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_DEAL_EXPIRED_RESOURCE_TO_US_NAME',
				message='KEY_TXT_NOTIFICATION_DEAL_EXPIRED_RESOURCE_TO_US_MESSAGE'
			)
		elif self == NotificationType.dealExpiredOpenBordersFromUs:  # 43
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_DEAL_EXPIRED_OPEN_BORDERS_FROM_US_NAME',
				message='KEY_TXT_NOTIFICATION_DEAL_EXPIRED_OPEN_BORDERS_FROM_US_MESSAGE'
			)
		elif self == NotificationType.dealExpiredOpenBordersToUs:  # 44
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_DEAL_EXPIRED_OPEN_BORDERS_TO_US_NAME',
				message='KEY_TXT_NOTIFICATION_DEAL_EXPIRED_OPEN_BORDERS_TO_US_MESSAGE'
			)
		elif self == NotificationType.dealExpiredDefensivePactFromUs:  # 45
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_DEAL_EXPIRED_DEFENSIVE_PACT_FROM_US_NAME',
				message='KEY_TXT_NOTIFICATION_DEAL_EXPIRED_DEFENSIVE_PACT_FROM_US_MESSAGE'
			)
		elif self == NotificationType.dealExpiredDefensivePactToUs:  # 46
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_DEAL_EXPIRED_DEFENSIVE_PACT_TO_US_NAME',
				message='KEY_TXT_NOTIFICATION_DEAL_EXPIRED_DEFENSIVE_PACT_TO_US_MESSAGE'
			)
		elif self == NotificationType.dealExpiredResearchAgreement:  # 47
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_DEAL_EXPIRED_RESEARCH_AGREEMENT_NAME',
				message='KEY_TXT_NOTIFICATION_DEAL_EXPIRED_RESEARCH_AGREEMENT_MESSAGE'
			)
		elif self == NotificationType.dealExpiredPeaceTreaty:  # 48
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_DEAL_EXPIRED_PEACE_TREATY_NAME',
				message='KEY_TXT_NOTIFICATION_DEAL_EXPIRED_PEACE_TREATY_MESSAGE'
			)

		raise InvalidEnumError(self)


class Notification:
	def __init__(self, notificationType: NotificationType, city=None, player=None,
	             momentType: Optional[MomentType] = None, cityState: Optional[CityStateType] = None,
	             first: Optional[bool] = None, population: Optional[int] = None, location: Optional[HexPoint] = None,
	             cityName: Optional[str] = None, leader: Optional[LeaderType] = None,
	             wonder: Optional[WonderType] = None, civilization: Optional[CivilizationType] = None,
	             continentName: Optional[str] = None, greatPerson: Optional[GreatPersonType] = None,
	             religion: Optional[ReligionType] = None):
		self.notificationType = notificationType
		self.city = city
		self.player = player
		self.momentType = momentType
		self.cityState = cityState
		self.first = first
		self.population = population
		self.location = location
		self.cityName = cityName
		self.leader = leader
		self.wonder = wonder
		self.civilization = civilization
		self.continentName = continentName
		self.greatPerson = greatPerson
		self.religion = religion

		self.dismissed = False
		self.needsBroadcasting = True
		self.turn = -1  # which turn this event was created on

	def dismiss(self, simulation):
		self.dismissed = True
		simulation.userInterface.removeNotification(self)

	def expiredFor(self, player, simulation) -> bool:
		if self == NotificationType.techNeeded:
			if not player.techs.needToChooseTech():
				# already selected a tech
				return True

			return False

		elif self == NotificationType.civicNeeded:
			if not player.civics.needToChooseCivic():
				# already selected a civic
				return True

			return False

		elif self == NotificationType.productionNeeded:
			city = simulation.cityAt(self.location)

			if city is None:
				return True

			# when the city does no longer belong to this player(revolt),
			# it should be expired
			if not player == city.player:
				return True

			if city.buildQueue.hasBuildable():
				# already has something to build
				return True

			return False

		elif self == NotificationType.canChangeGovernment:
			return True

		elif self == NotificationType.policiesNeeded:
			return player.government.hasPolicyCardsFilled(simulation)

		elif self == NotificationType.unitPromotion:
			if not player.hasPromotableUnit(simulation):
				return True

			return False

		elif self == NotificationType.canFoundPantheon:
			if player.religion.pantheon() != PantheonType.none:
				return True

			return False

		elif self == NotificationType.governorTitleAvailable:
			if player.governors.numTitlesAvailable() == 0:
				return True

			return False

		elif self == NotificationType.greatPersonJoined:
			return True

		elif self == NotificationType.canRecruitGreatPerson:
			return True

		elif self == NotificationType.goodyHutDiscovered:
			tile = simulation.tileAt(self.location)
			if not tile.hasImprovement(ImprovementType.goodyHut):
				return True

			return False

		elif self == NotificationType.barbarianCampDiscovered:
			tile = simulation.tileAt(self.location)
			if not tile.hasImprovement(ImprovementType.barbarianCamp):
				return True

			return False

		elif self == NotificationType.questCityStateFulfilled:
			return False

		elif self == NotificationType.questCityStateGiven:
			return False

		elif self == NotificationType.questCityStateObsolete:
			return False

		elif self == NotificationType.metCityState:
			return False

		elif self == NotificationType.tradeRouteCapacityIncreased:
			return False

		elif self == NotificationType.momentAdded:
			return False

		elif self == NotificationType.cityCanShoot:
			city = simulation.cityAt(self.location)
			if city is None:
				return True

			return city.isOutOfAttacks(simulation)

		elif self == NotificationType.cityAcquired:
			return False

		elif self == NotificationType.envoyEarned:
			return False

		elif self == NotificationType.enemyInTerritory:
			for unit in simulation.unitsAt(self.location):
				if player.isAtWarWith(unit.player):
					return False

			return True

		return False


class Notifications:
	def __init__(self, player):
		self.player = player
		self.notifications = []

	def add(self, notification: Notification):
		self.notifications.append(notification)

	def cleanUp(self, simulation):
		"""removing notifications at the end turns"""
		for notification in self.notifications:
			# city growth should vanish at the end of turn (if not already)
			if notification.notificationType == NotificationType.cityGrowth:
				if not notification.dismissed:
					notification.dismiss(simulation)

			# city starving too
			if notification.notificationType == NotificationType.starving:
				if not notification.dismissed:
					notification.dismiss(simulation)

		self.notifications = list(filter(lambda notification: not notification.dismissed, self.notifications))

	def addNotification(self, notificationType: Union[NotificationType, str], momentType: Optional[MomentType] = None,
	                    cityState: Optional[CityStateType] = None, cityName: Optional[str] = None,
	                    first: Optional[bool] = None, population: Optional[int] = None,
	                    location: Optional[HexPoint] = None, leader: Optional[LeaderType] = None,
	                    wonder: Optional[WonderType] = None, civilization: Optional[CivilizationType] = None,
	                    continentName: Optional[str] = None, greatPerson: Optional[GreatPersonType] = None,
	                    religion: Optional[ReligionType] = None):

		if isinstance(notificationType, str):
			notificationType = NotificationType.fromName(notificationType)

		notification = Notification(
			notificationType=notificationType,
			momentType=momentType,
			cityState=cityState,
			first=first,
			population=population,
			cityName=cityName,
			location=location,
			leader=leader,
			wonder=wonder,
			civilization=civilization,
			continentName=continentName,
			greatPerson=greatPerson,
			religion=religion
		)
		self.notifications.append(notification)

	def update(self, simulation):
		for notification in self.notifications:
			if notification.dismissed:
				continue

			if notification.expiredFor(self.player, simulation):
				notification.dismiss(simulation)
			else:
				if notification.needsBroadcasting:
					simulation.userInterface.addNotification(notification)
					notification.needsBroadcasting = False

		return
