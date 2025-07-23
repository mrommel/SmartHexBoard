import logging
from typing import Optional, List

from smarthexboard.smarthexboardlib.core.base import ExtendedEnum, InvalidEnumError
from smarthexboard.smarthexboardlib.map.base import HexPoint
from smarthexboard.smarthexboardlib.map.types import ResourceType, ResourceUsage


class PeaceTreatyType:
	pass


class DiplomaticStatementType(ExtendedEnum):
	none = 'NO_DIPLO_STATEMENT_TYPE'  # NO_DIPLO_STATEMENT_TYPE

	requestPeace = 'requestPeace'  # DIPLO_STATEMENT_REQUEST_PEACE

	aggressiveMilitaryWarning = 'aggressiveMilitaryWarning'  # DIPLO_STATEMENT_AGGRESSIVE_MILITARY_WARNING
	# 	DIPLO_STATEMENT_KILLED_PROTECTED_CITY_STATE
	# 	DIPLO_STATEMENT_ATTACKED_PROTECTED_CITY_STATE
	# 	DIPLO_STATEMENT_BULLIED_PROTECTED_CITY_STATE
	expansionSeriousWarning = 'expansionSeriousWarning'  # DIPLO_STATEMENT_EXPANSION_SERIOUS_WARNING
	expansionWarning = 'expansionWarning'  # DIPLO_STATEMENT_EXPANSION_WARNING
	expansionBrokenPromise = 'expansionBrokenPromise'  # DIPLO_STATEMENT_EXPANSION_BROKEN_PROMISE
	# 	DIPLO_STATEMENT_PLOT_BUYING_SERIOUS_WARNING
	plotBuyingWarning = 'plotBuyingWarning'  # DIPLO_STATEMENT_PLOT_BUYING_WARNING
	plotBuyingBrokenPromise = 'plotBuyingBrokenPromise'  # DIPLO_STATEMENT_PLOT_BUYING_BROKEN_PROMISE
	# 	DIPLO_STATEMENT_WE_ATTACKED_YOUR_MINOR
	# 	DIPLO_STATEMENT_WE_BULLIED_YOUR_MINOR
	workWithUs = 'workWithUs'  # DIPLO_STATEMENT_WORK_WITH_US
	workWithUsRandFailed = 'workWithUsRandFailed'  # DIPLO_STATEMENT_WORK_WITH_US_RANDFAILED
	# 	DIPLO_STATEMENT_END_WORK_WITH_US
	denounce = 'denounce'  # DIPLO_STATEMENT_DENOUNCE
	denounceRandFailed = 'denounceRandFailed'  # DIPLO_STATEMENT_DENOUNCE_RANDFAILED
	# 	DIPLO_STATEMENT_END_WORK_AGAINST_SOMEONE
	# 	DIPLO_STATEMENT_COOP_WAR_REQUEST
	coopWarTime = 'coopWarTime'  # DIPLO_STATEMENT_COOP_WAR_TIME
	# 	DIPLO_STATEMENT_NOW_UNFORGIVABLE
	# 	DIPLO_STATEMENT_NOW_ENEMY
	#
	# 	DIPLO_STATEMENT_CAUGHT_YOUR_SPY
	# 	DIPLO_STATEMENT_KILLED_YOUR_SPY
	# 	DIPLO_STATEMENT_KILLED_MY_SPY
	# 	DIPLO_STATEMENT_SHARE_INTRIGUE
	#
	# 	DIPLO_STATEMENT_STOP_CONVERSIONS
	#
	demand = 'demand'  # DIPLO_STATEMENT_DEMAND

	request = 'request'  # DIPLO_STATEMENT_REQUEST
	requestRandFailed = 'requestRandFailed'  # DIPLO_STATEMENT_REQUEST_RANDFAILED

	# 	DIPLO_STATEMENT_GIFT
	# 	DIPLO_STATEMENT_GIFT_RANDFAILED
	#
	# 	DIPLO_STATEMENT_LUXURY_TRADE
	delegationExchange = 'delegationExchange'  # unique to civ6
	delegationOffer = 'delegationOffer'  # unique to civ6
	embassyExchange = 'embassyExchange'  # DIPLO_STATEMENT_EMBASSY_EXCHANGE
	embassyOffer = 'embassyOffer'  # DIPLO_STATEMENT_EMBASSY_OFFER
	openBordersExchange = 'openBordersExchange'  # DIPLO_STATEMENT_OPEN_BORDERS_EXCHANGE
	openBordersOffer = 'openBordersOffer'  # DIPLO_STATEMENT_OPEN_BORDERS_OFFER
	planResearchAgreement = 'planResearchAgreement'  # DIPLO_STATEMENT_PLAN_RESEARCH_AGREEMENT
	researchAgreementOffer = 'researchAgreementOffer'  # DIPLO_STATEMENT_RESEARCH_AGREEMENT_OFFER
	# 	DIPLO_STATEMENT_RENEW_DEAL
	#
	insult = 'insult'  # DIPLO_STATEMENT_INSULT
	# 	DIPLO_STATEMENT_COMPLIMENT
	bootKissing = 'bootKissing'  # DIPLO_STATEMENT_BOOT_KISSING
	warmonger = 'warmonger'  # DIPLO_STATEMENT_WARMONGER
	minorCivCompetition = 'minorCivCompetition'  # DIPLO_STATEMENT_MINOR_CIV_COMPETITION
	#
	# 	DIPLO_STATEMENT_DENOUNCE_FRIEND
	# 	DIPLO_STATEMENT_REQUEST_FRIEND_DENOUNCE
	# 	DIPLO_STATEMENT_REQUEST_FRIEND_DENOUNCE_RANDFAILED
	# 	DIPLO_STATEMENT_REQUEST_FRIEND_WAR
	#
	# 	DIPLO_STATEMENT_ANGRY_BEFRIEND_ENEMY
	# 	DIPLO_STATEMENT_ANGRY_BEFRIEND_ENEMY_RANDFAILED
	# 	DIPLO_STATEMENT_ANGRY_DENOUNCED_FRIEND
	# 	DIPLO_STATEMENT_ANGRY_DENOUNCED_FRIEND_RANDFAILED
	# 	DIPLO_STATEMENT_HAPPY_DENOUNCED_ENEMY
	# 	DIPLO_STATEMENT_HAPPY_DENOUNCED_ENEMY_RANDFAILED
	# 	DIPLO_STATEMENT_HAPPY_BEFRIENDED_FRIEND
	# 	DIPLO_STATEMENT_HAPPY_BEFRIENDED_FRIEND_RANDFAILED
	# 	DIPLO_STATEMENT_FYI_BEFRIEND_HUMAN_ENEMY
	# 	DIPLO_STATEMENT_FYI_BEFRIEND_HUMAN_ENEMY_RANDFAILED
	# 	DIPLO_STATEMENT_FYI_DENOUNCED_HUMAN_FRIEND
	# 	DIPLO_STATEMENT_FYI_DENOUNCED_HUMAN_FRIEND_RANDFAILED
	# 	DIPLO_STATEMENT_FYI_DENOUNCED_HUMAN_ENEMY
	# 	DIPLO_STATEMENT_FYI_DENOUNCED_HUMAN_ENEMY_RANDFAILED
	# 	DIPLO_STATEMENT_FYI_BEFRIEND_HUMAN_FRIEND
	# 	DIPLO_STATEMENT_FYI_BEFRIEND_HUMAN_FRIEND_RANDFAILED
	#
	#     DIPLO_STATEMENT_SAME_POLICIES_FREEDOM
	#     DIPLO_STATEMENT_SAME_POLICIES_ORDER
	#     DIPLO_STATEMENT_SAME_POLICIES_AUTOCRACY
	#
	# 	DIPLO_STATEMENT_STOP_DIGGING
	#
	# 	# League statements
	# 	DIPLO_STATEMENT_WE_LIKED_THEIR_PROPOSAL
	# 	DIPLO_STATEMENT_WE_DISLIKED_THEIR_PROPOSAL
	# 	DIPLO_STATEMENT_THEY_SUPPORTED_OUR_PROPOSAL
	# 	DIPLO_STATEMENT_THEY_FOILED_OUR_PROPOSAL
	# 	DIPLO_STATEMENT_THEY_SUPPORTED_OUR_HOSTING
	#
	# 	# Ideological statements
	# 	DIPLO_STATEMENT_YOUR_IDEOLOGY_CAUSING_CIVIL_UNREST_FREEDOM
	# 	DIPLO_STATEMENT_YOUR_IDEOLOGY_CAUSING_CIVIL_UNREST_ORDER
	# 	DIPLO_STATEMENT_YOUR_IDEOLOGY_CAUSING_CIVIL_UNREST_AUTOCRACY
	# 	DIPLO_STATEMENT_OUR_IDEOLOGY_CAUSING_CIVIL_UNREST_FREEDOM
	# 	DIPLO_STATEMENT_OUR_IDEOLOGY_CAUSING_CIVIL_UNREST_ORDER
	# 	DIPLO_STATEMENT_OUR_IDEOLOGY_CAUSING_CIVIL_UNREST_AUTOCRACY
	# 	DIPLO_STATEMENT_SWITCH_OUR_IDEOLOGY_FREEDOM
	# 	DIPLO_STATEMENT_SWITCH_OUR_IDEOLOGY_ORDER
	# 	DIPLO_STATEMENT_SWITCH_OUR_IDEOLOGY_AUTOCRACY
	# 	DIPLO_STATEMENT_YOUR_CULTURE_INFLUENTIAL
	# 	DIPLO_STATEMENT_OUR_CULTURE_INFLUENTIAL


class DiplomaticDealItemType(ExtendedEnum):
	gold = 'gold'  # TRADE_ITEM_GOLD
	goldPerTurn = 'goldPerTurn'  # TRADE_ITEM_GOLD_PER_TURN
	maps = 'maps'  # TRADE_ITEM_MAPS
	resources = 'resources'  # TRADE_ITEM_RESOURCES
	cities = 'cities'  # TRADE_ITEM_CITIES
	units = 'units'  # TRADE_ITEM_UNITS
	allowDelegation = 'allowDelegation'  # new in civ6
	allowEmbassy = 'allowEmbassy'  # TRADE_ITEM_ALLOW_EMBASSY
	openBorders = 'openBorders'  # TRADE_ITEM_OPEN_BORDERS
	defensivePact = 'defensivePact'  # TRADE_ITEM_DEFENSIVE_PACT
	researchAgreement = 'researchAgreement'  # TRADE_ITEM_RESEARCH_AGREEMENT
	# -- tradeAgreement = 'tradeAgreement'  # TRADE_ITEM_TRADE_AGREEMENT, not in use
	permanentAlliance = 'permanentAlliance'  # TRADE_ITEM_PERMANENT_ALLIANCE
	surrender = 'surrender'  # TRADE_ITEM_SURRENDER
	truce = 'truce'  # TRADE_ITEM_TRUCE
	peaceTreaty = 'peaceTreaty'  # TRADE_ITEM_PEACE_TREATY
	thirdPartyPeace = 'thirdPartyPeace'  # TRADE_ITEM_THIRD_PARTY_PEACE
	thirdPartyWar = 'thirdPartyWar'  # TRADE_ITEM_THIRD_PARTY_WAR
	# -- TRADE_ITEM_THIRD_PARTY_EMBARGO, # not in use
	declarationOfFriendship = 'declarationOfFriendship'  # TRADE_ITEM_DECLARATION_OF_FRIENDSHIP - Only "traded" between human players
	voteCommitment = 'voteCommitment'  # TRADE_ITEM_VOTE_COMMITMENT


class DiplomaticDealDirectionType(ExtendedEnum):
	give = 'give'
	receive = 'receive'


class DiplomaticDealItem:
	def __init__(self, itemType: DiplomaticDealItemType, direction: DiplomaticDealDirectionType, amount: int, duration: int):
		self.itemType: DiplomaticDealItemType = itemType
		self.direction: DiplomaticDealDirectionType = direction
		self.amount: int = amount
		self.duration: int = duration
		self.resource = None
		self.toRenewed: bool = False
		self.fromRenewed: bool = False
		self.point: Optional[HexPoint] = None
		self.thirdPlayer = None
		self.finalTurn: int = -1


class DiplomaticGoldDealItem(DiplomaticDealItem):
	def __init__(self, direction: DiplomaticDealDirectionType, amount: int):
		super().__init__(DiplomaticDealItemType.gold, direction=direction, amount=amount, duration=0)


class DiplomaticGoldPerTurnDealItem(DiplomaticDealItem):
	def __init__(self, direction: DiplomaticDealDirectionType, amount: int, duration: int):
		super().__init__(DiplomaticDealItemType.goldPerTurn, direction=direction, amount=amount, duration=duration)


class DiplomaticAllowDelegationDealItem(DiplomaticDealItem):
	def __init__(self, direction: DiplomaticDealDirectionType):
		super().__init__(DiplomaticDealItemType.allowDelegation, direction=direction, amount=0, duration=0)


class DiplomaticAllowEmbassyDealItem(DiplomaticDealItem):
	def __init__(self, direction: DiplomaticDealDirectionType):
		super().__init__(DiplomaticDealItemType.allowEmbassy, direction=direction, amount=0, duration=0)


class DiplomaticOpenBordersDealItem(DiplomaticDealItem):
	def __init__(self, direction: DiplomaticDealDirectionType, duration: int):
		super().__init__(DiplomaticDealItemType.openBorders, direction=direction, amount=0, duration=duration)


class DiplomaticPeaceTreatyDealItem(DiplomaticDealItem):
	def __init__(self, direction: DiplomaticDealDirectionType, duration: int):
		super().__init__(DiplomaticDealItemType.peaceTreaty, direction=direction, amount=0, duration=duration)


class DiplomaticResourcesDealItem(DiplomaticDealItem):
	def __init__(self, direction: DiplomaticDealDirectionType, resource: ResourceType, amount: int, duration: int):
		super().__init__(DiplomaticDealItemType.resources, direction=direction, amount=amount, duration=duration)
		self.resource = resource


class DiplomaticVoteCommitmentDealItem(DiplomaticDealItem):
	def __init__(self, direction: DiplomaticDealDirectionType, duration: int):
		super().__init__(DiplomaticDealItemType.voteCommitment, direction=direction, amount=0, duration=duration)


class DiplomaticCityDealItem(DiplomaticDealItem):
	def __init__(self, direction: DiplomaticDealDirectionType, point: HexPoint):
		super().__init__(DiplomaticDealItemType.cities, direction=direction, amount=0, duration=0)
		self.point = point


class DiplomaticDealType(ExtendedEnum):
	none = 'none'

	historic = 'historic'
	current = 'current'


class DiplomaticDeal:
	def __init__(self, fromPlayer: 'Player', toPlayer: 'Player'):
		self.fromPlayer = fromPlayer
		self.toPlayer = toPlayer
		# self.surrendering: LeaderType = LeaderType.none
		self.tradeItems: List[DiplomaticDealItem] = []
		self.peaceTreatyType = PeaceTreatyType.none
		self._surrenderingPlayer = None
		self._requestingPlayer = None

		self.consideringForRenewal: bool = False
		self.checkedForRenewal: bool = False
		self.dealCancelled: bool = False

	def fromPlayerFor(self, item: DiplomaticDealItem):
		if item.direction == DiplomaticDealDirectionType.give:
			return self.fromPlayer
		else:
			return self.toPlayer

	def toPlayerFor(self, item: DiplomaticDealItem):
		if item.direction == DiplomaticDealDirectionType.give:
			return self.toPlayer
		else:
			return self.fromPlayer

	def otherPlayerOf(self, dealPlayer):
		if dealPlayer == self.fromPlayer:
			return self.toPlayer
		elif dealPlayer == self.toPlayer:
			return self.fromPlayer

		raise Exception('try to get other player but this player is not in the current deal')

	def clearItems(self):
		self.tradeItems = []

	def isPossibleToTradeItem(self, fromPlayer, toPlayer, itemType: DiplomaticDealItemType, amount: int=-1,
	                          resource: ResourceType=ResourceType.none, point: Optional[HexPoint]=None,
	                          thirdPlayer=None, checkOtherPlayerValidity: bool=False,
	                          finalizing: bool=False, simulation=None) -> bool:
		"""Is it actually possible for a player to offer up this trade item?"""
		# int iData1, int iData2, int iData3, bool bFlag1, bool bCheckOtherPlayerValidity, bool bFinalizing
		if simulation is None:
			raise Exception('simulation must not be None')

		renewDeal, _ = fromPlayer.diplomacyAI.dealToRenew(simulation)
		if renewDeal is None:
			renewDeal, _ = toPlayer.diplomacyAI.dealToRenew(simulation)

		goldAvailable = self.goldAvailable(fromPlayer, itemType, simulation)

		# Some items require gold be spent (e.g. Research and Trade Agreements)
		cost = simulation.gameDeals.tradeItemGoldCost(itemType, fromPlayer, toPlayer, simulation)
		if cost > 0 and goldAvailable < cost:
			return False

		goldAvailable -= cost

		# ////////////////////////////////////////////////////

		# Gold
		if itemType == DiplomaticDealItemType.gold:
			# DoF has not been made with this player
			if not self.isPeaceTreatyTrade(toPlayer) and not self.isPeaceTreatyTrade(fromPlayer):
				if (not fromPlayer.diplomacyAI.isAlliedWith(toPlayer) and
					(not fromPlayer.diplomacyAI.isDeclarationOfFriendshipAcceptedBy(toPlayer) or
					 not toPlayer.diplomacyAI.isDeclarationOfFriendshipAcceptedBy(fromPlayer))):
					return False

			# Can't trade more Gold than you have
			gold: int = amount
			if gold != -1 and goldAvailable < gold:
				return False
		# Gold per Turn
		elif itemType == DiplomaticDealItemType.goldPerTurn:
			# Can't trade more GPT than you're making
			goldPerTurn: int = amount
			if goldPerTurn != -1 and fromPlayer.treasury.calculateGrossGold(simulation) < goldPerTurn:
				return False
		# Map
		elif itemType == DiplomaticDealItemType.maps:
			return False
		# Resource
		elif itemType == DiplomaticDealItemType.resources:
			if resource != ResourceType.none:
				resourceQuantity: int = amount

				# Can't trade a negative amount of something!
				if resourceQuantity < 0:
					return False

				# if (GC.getGame().GetGameLeagues().IsLuxuryHappinessBanned(fromPlayer, eResource) or GC.getGame().GetGameLeagues().IsLuxuryHappinessBanned(toPlayer, eResource)):
				#	return False

				numAvailable: int = fromPlayer.numberOfAvailableResource(resource)
				numInRenewDeal: int = 0
				numInExistingDeal: int = 0

				if renewDeal is not None:
					# count any that are in the renewal deal
					for it in renewDeal.tradeItems:
						if it.itemType == DiplomaticDealItemType.resources and it.resource == resource:
							# credit the amount
							numInRenewDeal += it.amount

					# remove any that are in this deal
					for it in self.tradeItems:
						if it.itemType == DiplomaticDealItemType.resources and it.resource == resource:
							numInExistingDeal += it.amount

				# Offering up more of a Resource than we have available
				if numAvailable + numInRenewDeal - numInExistingDeal < resourceQuantity:
					return False

				# Must be a Luxury or a Strategic Resource
				usage: ResourceUsage = resource.usage()
				if usage != ResourceUsage.luxury and usage != ResourceUsage.strategic:
					return False

				if usage == ResourceUsage.luxury:
					# Can't trade Luxury if the other player already has one
					if toPlayer.numberOfAvailableResource(resource) > max(numInRenewDeal - numInExistingDeal, 0):
						return False

				# Can't trade them something they're already giving us in the deal
				if self.isResourceTrade(toPlayer, resource):
					return False

				# AI can't trade an obsolete resource
				if not fromPlayer.isHuman() and fromPlayer.IsResourceObsolete(resource):
					return False
		# City
		elif itemType == DiplomaticDealItemType.cities:
			if point is None:
				return False

			city = simulation.cityAt(point)

			if city is not None:
				# Can't trade someone else's city
				if city.player != fromPlayer:
					return False

				# Can't trade one's capital
				if city.isCapital():
					return False

				# Can't trade a city to a human in an OCC game
				# if(GC.getGame().isOption(GAMEOPTION_ONE_CITY_CHALLENGE) and GET_PLAYER(toPlayer).isHuman()):
				#	return False
			# Can't trade a null city
			else:
				return False

			# Can't already have this city in the deal
			if not finalizing and self.isCityTrade(fromPlayer, point):
				return False
		# Unit
		elif itemType == DiplomaticDealItemType.units:
			return False
		# Delegation
		elif itemType == DiplomaticDealItemType.allowDelegation:
			# too few cities
			if toPlayer.numberOfCities(simulation) < 1:
				return False
			# Already has sent delegation
			if not toPlayer.isAllowDelegationTradingAllowed():
				return False
			# Already has embassy
			if toPlayer.diplomacyAI.hasSentDelegationTo(fromPlayer):
				return False
			# Same team
			# if fromPlayer.diplomacyAI.isAlliedWith(toPlayer):
			#	return False
		# Embassy
		elif itemType == DiplomaticDealItemType.allowEmbassy:
			# too few cities
			if toPlayer.numberOfCities(simulation) < 1:
				return False
			# Does not have tech for Embassy trading
			if not toPlayer.isAllowEmbassyTradingAllowed():
				return False
			# Already has embassy
			if toPlayer.diplomacyAI.hasEstablishedEmbassyTo(fromPlayer):
				return False
			# Same team
			# if fromPlayer.diplomacyAI.isAlliedWith(toPlayer):
			#	return False
		# Open Borders
		elif itemType == DiplomaticDealItemType.openBorders:
			# Neither of us yet has the Tech for OP
			if not fromPlayer.isOpenBordersTradingAllowed() and not toPlayer.isOpenBordersTradingAllowed():
				return False
			# Embassy has not been established
			if not fromPlayer.hasEstablishedEmbassyTo(toPlayer):
				return False

			ignoreExistingOP: bool = True
			if renewDeal is not None:
				# count any that are in the re-new deal
				endingTurn: int = -1
				for it in renewDeal.tradeItems:
					if it.itemType == DiplomaticDealItemType.openBorders and (it.fromPlayer == fromPlayer or it.toPlayer == toPlayer):
						endingTurn = it.finalTurn

				if endingTurn == simulation.currentTurn:
					ignoreExistingOP = False

			# Already has OP
			if fromPlayer.isAllowsOpenBordersToTeam(toPlayer) and ignoreExistingOP:
				return False

			# Same Team
			if fromPlayer.diplomacyAI.isAlliedWith(toPlayer):
				return False
		# Defensive Pact
		elif itemType == DiplomaticDealItemType.defensivePact:
			# Neither of us yet has the Tech for DP
			if not fromPlayer.isDefensivePactTradingAllowed() and not toPlayer.isDefensivePactTradingAllowed():
				return False
			# Embassy has not been established
			if not fromPlayer.hasEstablishedEmbassyTo(toPlayer) or not toPlayer.hasEstablishedEmbassyTo(fromPlayer):
				return False
			# Already has DP
			if fromPlayer.isHasDefensivePact(toPlayer):
				return False
			# Same Team
			if fromPlayer.diplomacyAI.isAlliedWith(toPlayer):
				return False

			# Check to see if the other player can trade this item to us as well.  If we can't, we can't trade it either
			if checkOtherPlayerValidity:
				if(not self.isPossibleToTradeItem(toPlayer, fromPlayer, itemType, amount=amount, resource=resource,
				                                  point=point, thirdPlayer=thirdPlayer, checkOtherPlayerValidity=False,
				                                  simulation=simulation)):
					return False
		# Research Agreement
		elif itemType == DiplomaticDealItemType.researchAgreement:
			# if(GC.getGame().isOption(GAMEOPTION_NO_SCIENCE))
			#	return False

			# Neither of us yet has the Tech for RA
			if not fromPlayer.isResearchAgreementTradingAllowed() and not toPlayer.isResearchAgreementTradingAllowed():
				return False
			# Embassy has not been established with this team
			if not fromPlayer.hasEstablishedEmbassyTo(toPlayer) or not toPlayer.hasEstablishedEmbassyTo(fromPlayer):
				return False
			# DoF has not been made with this player
			if(not fromPlayer.diplomacyAI.isDeclarationOfFriendshipAccepted(toPlayer) or
				not toPlayer.diplomacyAI.isDeclarationOfFriendshipAccepted(fromPlayer)):
				return False
			# Already has RA
			if fromPlayer.isHasResearchAgreement(toPlayer):
				return False
			# Same Team
			if fromPlayer.diplomacyAI.isAlliedWith(toPlayer):
				return False
			# Someone already has all techs
			if fromPlayer.techs.hasResearchedAllTechs() or toPlayer.techs.hasResearchedAllTechs():
				return False

			# Check to see if the other player can trade this item to us as well.  If we can't, we can't trade it either
			if checkOtherPlayerValidity:
				if not self.isPossibleToTradeItem(toPlayer, fromPlayer, itemType, amount=amount, resource=resource,
				                                  point=point, thirdPlayer=thirdPlayer, checkOtherPlayerValidity=False,
				                                  simulation=simulation):
					return False
		# Trade Agreement
		# elif(item == DiplomaticDealItemType.TRADE_AGREEMENT):
		# {
		# 	# Neither of us yet has the Tech for TA
		# 	if(not fromPlayer.IsTradeAgreementTradingAllowed() and not toPlayer.IsTradeAgreementTradingAllowed()):
		# 		return False
		# 	# Already has TA
		# 	if(fromPlayer.IsHasTradeAgreement(toPlayer)):
		# 		return False
		# 	# Same Team
		# 	if fromPlayer.diplomacyAI.isAlliedWith(toPlayer):
		# 		return False
		#
		# 	# Check to see if the other player can trade this item to us as well.  If we can't, we can't trade it either
		# 	if(bCheckOtherPlayerValidity):
		# 	{
		# 		if(!IsPossibleToTradeItem(toPlayer, fromPlayer, eItem, iData1, iData2, iData3, bFlag1, /*bCheckOtherPlayerValidity*/ false))
		# 			return False
		# 	}
		# }
		# Permanent Alliance
		elif itemType == DiplomaticDealItemType.permanentAlliance:
			return False
		# Surrender
		elif itemType == DiplomaticDealItemType.surrender:
			return False
		# Truce
		elif itemType == DiplomaticDealItemType.truce:
			return False
		# Peace Treaty
		elif itemType == DiplomaticDealItemType.peaceTreaty:
			if not fromPlayer.isAtWarWith(toPlayer):
				return False

			if not toPlayer.isAtWarWith(fromPlayer):
				return False
		# Third Party Peace
		elif itemType == DiplomaticDealItemType.thirdPartyPeace:
			if thirdPlayer is None:
				return False
			# Can't be the same team
			if fromPlayer == thirdPlayer:
				return False

			# Can't ask teammates
			if toPlayer == fromPlayer:
				return False

			# Must be alive
			if not thirdPlayer.isAlive():
				return False

			# Player that wants Peace hasn't yet met the 3rd Team
			if not toPlayer.isHasMetWith(thirdPlayer):
				return False
			# Player that would go to Peace hasn't yet met the 3rd Team
			if not fromPlayer.isHasMetWith(thirdPlayer):
				return False
			# Player that would go to peace is already at peace with the 3rd Team
			if not fromPlayer.isAtWarWith(thirdPlayer):
				return False

			# Can't already have this in the deal
			# if (IsThirdPartyPeaceTrade( fromPlayer, GET_TEAM(eThirdTeam).getLeaderID() )):
			#	return False

			# Minor civ
			if thirdPlayer.isCityState():
				# Minor at permanent war with this player
				if thirdPlayer.minorCivAI.isPermanentAtWarWith(fromPlayer):
					return False

				# Minor's ally at war with this player?
				elif thirdPlayer.minorCivAI.isPeaceBlockedWith(fromPlayer):
					# If the ally is us, don't block peace here
					if not thirdPlayer.minorCivAI.isAlly(toPlayer):
						return False
			# Major civ
			else:
				# Can't ask them to make peace with a human, because we have no way of knowing if the human wants peace
				if thirdPlayer.isHuman():
					return False

				# Player does not want peace with eOtherPlayer
				if fromPlayer.isHuman() or fromPlayer.diplomacyAI.isWarGoalDamageTowards(thirdPlayer):
					return False

				# Other player does not want peace with toPlayer
				if not thirdPlayer.diplomacyAI.isWantsPeaceWithPlayer(fromPlayer):
					return False
		# Third Party War
		elif itemType == DiplomaticDealItemType.thirdPartyWar:
			# Can't be the same team
			if fromPlayer == thirdPlayer:
				return False

			# Can't ask teammates
			if toPlayer == fromPlayer:
				return False

			# Must be alive
			if not thirdPlayer.isAlive():
				return False

			# Player that would go to war hasn't yet met the 3rd Team
			if not toPlayer.isHasMetWith(thirdPlayer):
				return False
			# Player that wants war not met this team
			if not fromPlayer.isHasMetWith(thirdPlayer):
				return False

			# Player that would go to war is already at war with the 3rd Team
			if fromPlayer.isAtWarWith(thirdPlayer):
				return False

			# Can this player actually declare war?
			if not fromPlayer.canDeclareWarTowards(thirdPlayer):
				return False

			# Can't already have this in the deal
			# if (IsThirdPartyWarTrade(fromPlayer, GET_TEAM(eThirdTeam).getLeaderID() ))
			#	return False

			# Can't ask a player to declare war on their ally
			if thirdPlayer.isCityState():
				if thirdPlayer.minorCivAI.isAlly(fromPlayer):
					return False
		# Third Party Embargo
		# elif(item == DiplomaticDealItemType.THIRD_PARTY_EMBARGO):
		# 	return False
		# Declaration of friendship
		elif itemType == DiplomaticDealItemType.declarationOfFriendship:
			# If we are at war, then we can't until we make peace
			if fromPlayer.isAtWarWith(toPlayer):
				return False

			# Already have a DoF?
			if (fromPlayer.diplomacyAI.isDeclarationOfFriendshipAccepted(toPlayer) and
				toPlayer.diplomacyAI.isDeclarationOfFriendshipAccepted(fromPlayer)):
				return False
		# Promise to Vote in upcoming league session
		elif itemType == DiplomaticDealItemType.voteCommitment:
			# If we are at war, then we can't until we make peace
			if fromPlayer.isAtWarWith(toPlayer):
				return False

			# int iID = iData1;
			# antonjs: todo: verify iChoice is valid as well:
			# int iNumVotes = iData3;
			# bool bRepeal = bFlag1;

			# Can't already have a vote commitment in the deal
			if not finalizing and self.isVoteCommitmentTrade(fromPlayer):
				return False

		return True

	def goldAvailable(self, player, itemToBeChanged: DiplomaticDealItemType, simulation) -> int:
		"""How much Gold does ePlayer have available to be used in this Deal?"""
		goldAvailable: int = player.treasury.value()

		# Remove Gold we're sending to the other player in this deal (unless we're changing it)
		if itemToBeChanged != DiplomaticDealItemType.gold:
			goldAvailable -= self.goldTrade(player)

		# Loop through all trade items to see if they have a cost
		for it in self.tradeItems:
			# Don't count something against itself when trying to add it
			if it.itemType != itemToBeChanged:
				if (self.fromPlayer == player and it.direction == DiplomaticDealDirectionType.give) or \
					(self.toPlayer == player and it.direction == DiplomaticDealDirectionType.receive):
					otherPlayer = self.otherPlayerOf(player)
					goldCost = simulation.gameDeals.tradeItemGoldCost(it.itemType, player, otherPlayer, simulation)

					if goldCost != 0:  # Negative cost valid?  Maybe;-O
						goldAvailable -= goldCost

		return goldAvailable

	def goldTrade(self, player) -> int:
		for it in self.tradeItems:
			if self.fromPlayer == player:
				if it.itemType == DiplomaticDealItemType.gold:
					return it.amount

		return 0

	def addAllowEmbassy(self, dealPlayer, simulation):
		"""Insert adding an embassy to the deal"""
		if dealPlayer != self.fromPlayer and dealPlayer != self.toPlayer:
			raise Exception('DEAL: Adding deal item for a player that\'s not actually in this deal!')

		if self.isPossibleToTradeItem(dealPlayer, self.otherPlayerOf(dealPlayer), DiplomaticDealItemType.allowEmbassy, simulation=simulation):
			direction: DiplomaticDealDirectionType = DiplomaticDealDirectionType.give if dealPlayer == self.fromPlayer else DiplomaticDealDirectionType.receive
			item = DiplomaticAllowEmbassyDealItem(direction)
			self.tradeItems.append(item)
		else:
			logging.warning('DEAL: Trying to add an invalid Allow Embassy item to a deal')

		return

	def addOpenBorders(self, dealPlayer, duration: int, simulation):
		"""Insert an open borders pact"""
		if dealPlayer != self.fromPlayer and dealPlayer != self.toPlayer:
			raise Exception('DEAL: Adding deal item for a player that\'s not actually in this deal!')

		if self.isPossibleToTradeItem(dealPlayer, self.otherPlayerOf(dealPlayer), DiplomaticDealItemType.openBorders, simulation=simulation):
			direction: DiplomaticDealDirectionType = DiplomaticDealDirectionType.give if dealPlayer == self.fromPlayer else DiplomaticDealDirectionType.receive
			item = DiplomaticOpenBordersDealItem(direction, duration)
			self.tradeItems.append(item)
		else:
			logging.warning('DEAL: Trying to add an invalid Open Borders item to a deal')

	def addSendDelegationTowards(self, dealPlayer, simulation):
		if dealPlayer != self.fromPlayer and dealPlayer != self.toPlayer:
			raise Exception('DEAL: Adding deal item for a player that\'s not actually in this deal!')

		if self.isPossibleToTradeItem(dealPlayer, self.otherPlayerOf(dealPlayer), DiplomaticDealItemType.allowDelegation, simulation=simulation):
			direction: DiplomaticDealDirectionType = DiplomaticDealDirectionType.give if dealPlayer == self.fromPlayer else DiplomaticDealDirectionType.receive
			item = DiplomaticAllowDelegationDealItem(direction)
			self.tradeItems.append(item)
		else:
			logging.warning('DEAL: Trying to add an invalid Allow Embassy item to a deal')

		return

	def addGoldPerTurnTradeFrom(self, dealPlayer, amount: int, duration: int, simulation):
		"""Insert a gold per turn trade"""
		if dealPlayer != self.fromPlayer and dealPlayer != self.toPlayer:
			raise Exception('DEAL: Adding deal item for a player that\'s not actually in this deal!')

		if self.isPossibleToTradeItem(dealPlayer, self.otherPlayerOf(dealPlayer), DiplomaticDealItemType.goldPerTurn, amount, simulation=simulation):
			direction: DiplomaticDealDirectionType = DiplomaticDealDirectionType.give if dealPlayer == self.fromPlayer else DiplomaticDealDirectionType.receive
			item = DiplomaticGoldPerTurnDealItem(direction, amount, duration)
			self.tradeItems.append(item)
		else:
			logging.warning('DEAL: Trying to add an invalid gold per turn amount to a deal')

		return

	def addGoldTradeFrom(self, dealPlayer, amount: int, simulation):
		"""Insert an immediate gold trade"""
		if dealPlayer != self.fromPlayer and dealPlayer != self.toPlayer:
			raise Exception('DEAL: Adding deal item for a player that\'s not actually in this deal!')

		if self.isPossibleToTradeItem(dealPlayer, self.otherPlayerOf(dealPlayer), DiplomaticDealItemType.gold, amount, simulation=simulation):
			direction: DiplomaticDealDirectionType = DiplomaticDealDirectionType.give if dealPlayer == self.fromPlayer else DiplomaticDealDirectionType.receive
			item = DiplomaticGoldDealItem(direction, amount)
			self.tradeItems.append(item)
		else:
			logging.warning('DEAL: Trying to add an invalid gold amount to a deal')

		return

	def isPeaceTreatyTrade(self, fromPlayer) -> bool:
		if self.fromPlayer != fromPlayer:
			return False

		for it in self.tradeItems:
			if it.itemType == DiplomaticDealItemType.peaceTreaty:
				return True

		return False

	def addPeaceTreaty(self, dealPlayer, duration: int):
		"""Insert ending a war"""
		if dealPlayer != self.fromPlayer and dealPlayer != self.toPlayer:
			raise Exception('DEAL: Adding deal item for a player that\'s not actually in this deal!')

		if self.isPossibleToTradeItem(dealPlayer, self.otherPlayerOf(dealPlayer), DiplomaticDealItemType.peaceTreaty):
			item = DiplomaticPeaceTreatyDealItem(DiplomaticDealDirectionType.give, duration)
			self.tradeItems.append(item)
		else:
			logging.warning("DEAL: Trying to add an invalid Peace Treaty item to a deal")
		
		return

	def updatePeaceTreatyType(self, peaceTreaty: PeaceTreatyType):
		self.peaceTreatyType = peaceTreaty

	def updateSurrenderingPlayer(self, player):
		self._surrenderingPlayer = player

	def addResourceTrade(self, dealPlayer, resource: ResourceType, amount: int, duration: int, simulation):
		"""Insert a resource trade"""
		if dealPlayer != self.fromPlayer and dealPlayer != self.toPlayer:
			raise Exception('DEAL: Adding deal item for a player that\'s not actually in this deal!')

		if self.isPossibleToTradeItem(dealPlayer, self.otherPlayerOf(dealPlayer), DiplomaticDealItemType.resources, amount, resource, simulation=simulation):
			item = DiplomaticResourcesDealItem(DiplomaticDealDirectionType.give, resource, amount, duration)
			self.tradeItems.append(item)	
		else:
			logging.warning("DEAL: Trying to add an invalid Resource to a deal")
		
		return

	def changeResourceTrade(self, dealPlayer, resource: ResourceType, amount: int, dealDuration: int, simulation) -> bool:
		if dealPlayer != self.fromPlayer and dealPlayer != self.toPlayer:
			raise Exception('DEAL: Adding deal item for a player that\'s not actually in this deal!')

		for it in self.tradeItems:
			if self.fromPlayer == dealPlayer:
				if it.itemType == DiplomaticDealItemType.resources and it.resource == resource:
					if self.isPossibleToTradeItem(dealPlayer, self.otherPlayerOf(dealPlayer), DiplomaticDealItemType.resources, amount=amount, resource=resource, simulation=simulation):
						it.amount = amount
						it.duration = dealDuration
						it.finalTurn = simulation.currentTurn + dealDuration
						return True

		return False

	def isVoteCommitmentTrade(self, fromPlayer) -> bool:
		if self.fromPlayer != fromPlayer:
			return False

		for it in self.tradeItems:
			if it.itemType == DiplomaticDealItemType.voteCommitment:
				return True

		return False

	def isOpenBordersTrade(self, fromPlayer):
		if self.fromPlayer != fromPlayer:
			return False

		for it in self.tradeItems:
			if it.itemType == DiplomaticDealItemType.openBorders:
				return True

		return False

	def goldPerTurnTrade(self, otherPlayer: 'Player') -> int:
		for it in self.tradeItems:
			if self.fromPlayer == otherPlayer:
				if it.itemType == DiplomaticDealItemType.goldPerTurn:
					return it.amount

		return 0

	def addVoteCommitment(self, dealPlayer, duration: int, simulation):
		"""Insert a vote commitment to the deal"""
		if dealPlayer != self.fromPlayer and dealPlayer != self.toPlayer:
			raise Exception('DEAL: Adding deal item for a player that\'s not actually in this deal!')

		if self.isPossibleToTradeItem(dealPlayer, self.otherPlayerOf(dealPlayer), DiplomaticDealItemType.voteCommitment, simulation=simulation):
			item = DiplomaticVoteCommitmentDealItem(DiplomaticDealDirectionType.give, duration)
			self.tradeItems.append(item)
		else:
			logging.warning("DEAL: Trying to add an invalid Vote Commitment item to a deal")

		return

	def isResourceTrade(self, fromPlayer, resource: ResourceType) -> bool:
		if self.fromPlayer != fromPlayer:
			return False

		for it in self.tradeItems:
			if it.itemType == DiplomaticDealItemType.resources and it.resource == resource:
				return True
		
		return False

	def isCityTrade(self, fromPlayer, point: HexPoint):
		if self.fromPlayer != fromPlayer:
			return False

		for it in self.tradeItems:
			if it.itemType == DiplomaticDealItemType.cities and it.point == point:
				return True

		return False

	def updateRequestingPlayer(self, player):
		"""Sets Who (if anyone) is making a request in this Deal"""
		self._requestingPlayer = player

	def surrenderingPlayer(self):
		return self._surrenderingPlayer

	def isAllowEmbassyTrade(self, fromPlayer) -> bool:
		if self.fromPlayer != fromPlayer:
			return False

		for it in self.tradeItems:
			if it.itemType == DiplomaticDealItemType.allowEmbassy:
				return True

		return False

	def changeGoldTrade(self, dealPlayer: 'Player', newAmount: int, simulation) -> bool:
		if dealPlayer != self.fromPlayer and dealPlayer != self.toPlayer:
			raise Exception('DEAL: Changing deal item for a player that\'s not actually in this deal!')

		for it in self.tradeItems:
			if self.fromPlayer == dealPlayer:
				if it.itemType == DiplomaticDealItemType.gold:
					# Reduce Gold value to 0 first, because otherwise IsPossibleToTradeItem will think we're trying to
					# spend more than we have
					oldValue = it.amount
					it.amount = 0

					if self.isPossibleToTradeItem(dealPlayer, self.otherPlayerOf(dealPlayer), DiplomaticDealItemType.gold, newAmount, simulation=simulation):
						it.amount = newAmount
						return True

					# If we can't do this then restore the previous Gold quantity
					else:
						it.amount = oldValue

		return False

	def removeByType(self, itemType: DiplomaticDealItemType, fromPlayer=None):
		"""Delete a trade item that can be identified by type alone"""
		self.tradeItems = list(filter(lambda it: not (it.itemType == itemType and (fromPlayer is None or it.fromPlayer == fromPlayer)), self.tradeItems))
		return

	def changeGoldPerTurnTrade(self, dealPlayer: 'Player', newAmount: int, duration: int, simulation):
		if dealPlayer != self.fromPlayer and dealPlayer != self.toPlayer:
			raise Exception('DEAL: Changing deal item for a player that\'s not actually in this deal!')

		for it in self.tradeItems:
			if self.fromPlayer == dealPlayer:
				if it.itemType == DiplomaticDealItemType.goldPerTurn:
					if self.isPossibleToTradeItem(dealPlayer, self.otherPlayerOf(dealPlayer), DiplomaticDealItemType.goldPerTurn, amount=newAmount, simulation=simulation):
						it.amount = newAmount
						it.duration = duration
						it.finalTurn = simulation.currentTurn + duration
						return True

		return False

	def addCityTradeFrom(self, dealPlayer, location: HexPoint, simulation):
		"""Insert a city trade"""
		if dealPlayer != self.fromPlayer and dealPlayer != self.toPlayer:
			raise Exception('DEAL: Adding deal item for a player that\'s not actually in this deal!')

		if self.isPossibleToTradeItem(dealPlayer, self.otherPlayerOf(dealPlayer), DiplomaticDealItemType.cities, point=location, simulation=simulation):
			item = DiplomaticCityDealItem(DiplomaticDealDirectionType.give, location)
			self.tradeItems.append(item)
		else:
			logging.warning("DEAL: Trying to add an invalid City to a deal")

		return


class PeaceTreatyType(ExtendedEnum):
	none = -1, 'none'

	whitePeace = 0, 'whitePeace'  # PEACE_TREATY_WHITE_PEACE
	armistice = 1, 'armistice'  # PEACE_TREATY_ARMISTICE
	settlement = 2, 'settlement'  # PEACE_TREATY_SETTLEMENT
	backDown = 3, 'backDown'  # PEACE_TREATY_BACKDOWN
	submission = 4, 'submission'  # PEACE_TREATY_SUBMISSION
	surrender = 5, 'surrender'  # PEACE_TREATY_SURRENDER
	cession = 6, 'cession'  # PEACE_TREATY_CESSION
	capitulation = 7, 'capitulation'  # PEACE_TREATY_CAPITULATION
	unconditionalSurrender = 8, 'unconditionalSurrender'  # PEACE_TREATY_UNCONDITIONAL_SURRENDER

	def __new__(cls, value, name):
		member = object.__new__(cls)
		member._value = value
		member._name = name
		return member

	def value(self) -> int:
		return int(self._value)

	def __lt__(self, other):
		if isinstance(other, PeaceTreatyType):
			return self._value < other._value

		raise Exception(f'cannot compare PeaceTreatyType and {type(other)}')

	def __ge__(self, other):
		if isinstance(other, PeaceTreatyType):
			return self._value >= other._value

		raise Exception(f'cannot compare PeaceTreatyType and {type(other)}')

	@classmethod
	def fromValue(cls, value: int) -> PeaceTreatyType:
		for peaceTreaty in list(PeaceTreatyType):
			if peaceTreaty.value() == value:
				return peaceTreaty

		return PeaceTreatyType.none


class MinorPlayerApproachType:
	pass


class MinorPlayerApproachType(ExtendedEnum):
	none = 'none'  # NO_MINOR_CIV_APPROACH

	ignore = 'ignore'  # MINOR_CIV_APPROACH_IGNORE
	friendly = 'friendly'  # MINOR_CIV_APPROACH_FRIENDLY
	protective = 'protective'  # MINOR_CIV_APPROACH_PROTECTIVE
	conquest = 'conquest'  # MINOR_CIV_APPROACH_CONQUEST
	bully = 'bully'  # MINOR_CIV_APPROACH_BULLY

	@staticmethod
	def all() -> List[MinorPlayerApproachType]:
		return [
			MinorPlayerApproachType.ignore,
			MinorPlayerApproachType.friendly,
			MinorPlayerApproachType.protective,
			MinorPlayerApproachType.conquest,
			MinorPlayerApproachType.bully
		]


class MajorPlayerApproachType:
	pass


class MajorPlayerApproachType(ExtendedEnum):
	none = 'none'

	war = 'war'  # MAJOR_CIV_APPROACH_WAR
	hostile = 'hostile'  # MAJOR_CIV_APPROACH_HOSTILE
	deceptive = 'deceptive'  # MAJOR_CIV_APPROACH_DECEPTIVE
	neutral = 'neutral'  # MAJOR_CIV_APPROACH_NEUTRAL
	guarded = 'guarded'  # MAJOR_CIV_APPROACH_GUARDED
	afraid = 'afraid'  # MAJOR_CIV_APPROACH_AFRAID
	friendly = 'friendly'  # MAJOR_CIV_APPROACH_FRIENDLY

	@staticmethod
	def all() -> List[MajorPlayerApproachType]:
		return [
			MajorPlayerApproachType.war,
			MajorPlayerApproachType.hostile,
			MajorPlayerApproachType.deceptive,
			MajorPlayerApproachType.neutral,
			MajorPlayerApproachType.guarded,
			MajorPlayerApproachType.afraid,
			MajorPlayerApproachType.friendly
		]

	@classmethod
	def fromValue(cls, value) -> MajorPlayerApproachType:
		if value > 91:
			return MajorPlayerApproachType.friendly
		elif value > 74:
			return MajorPlayerApproachType.afraid
		elif value > 58:
			return MajorPlayerApproachType.guarded
		elif value > 41:
			return MajorPlayerApproachType.neutral
		elif value > 24:
			return MajorPlayerApproachType.deceptive
		elif value > 8:
			return MajorPlayerApproachType.hostile
		else:
			return MajorPlayerApproachType.war

	def level(self) -> int:
		if self == MajorPlayerApproachType.war:
			return 0
		elif self == MajorPlayerApproachType.hostile:
			return 16
		elif self == MajorPlayerApproachType.deceptive:
			return 33
		elif self == MajorPlayerApproachType.neutral or self == MajorPlayerApproachType.none:
			return 50
		elif self == MajorPlayerApproachType.guarded:
			return 66
		elif self == MajorPlayerApproachType.afraid:
			return 83
		elif self == MajorPlayerApproachType.friendly:
			return 100

		raise InvalidEnumError(self)

	def __repr__(self):
		if self == MajorPlayerApproachType.none:
			return 'None'
		elif self == MajorPlayerApproachType.war:
			return 'War'
		elif self == MajorPlayerApproachType.hostile:
			return 'Hostile'
		elif self == MajorPlayerApproachType.deceptive:
			return 'Deceptive'
		elif self == MajorPlayerApproachType.neutral:
			return 'Neutral'
		elif self == MajorPlayerApproachType.guarded:
			return 'Guarded'
		elif self == MajorPlayerApproachType.afraid:
			return 'Afraid'
		elif self == MajorPlayerApproachType.friendly:
			return 'Friendly'

		raise InvalidEnumError(self)

	def __lt__(self, other):
		if isinstance(other, MajorPlayerApproachType):
			return self.level() < other.level()

		raise Exception(f'Cannot compare MajorPlayerApproachType to {type(other)}')

	def __ge__(self, other):
		if isinstance(other, MajorPlayerApproachType):
			return self.level() >= other.level()

		raise Exception(f'Cannot compare MajorPlayerApproachType to {type(other)}')


class MajorCivOpinionType:
	pass


class MajorCivOpinionType(ExtendedEnum):
	none = 'none'  # NO_MAJOR_CIV_OPINION_TYPE

	unforgivable = 'unforgivable'  # MAJOR_CIV_OPINION_UNFORGIVABLE
	enemy = 'enemy'  # MAJOR_CIV_OPINION_ENEMY
	competitor = 'competitor'  # MAJOR_CIV_OPINION_COMPETITOR
	neutral = 'neutral'  # MAJOR_CIV_OPINION_NEUTRAL
	favorable = 'favorable'  # MAJOR_CIV_OPINION_FAVORABLE
	friend = 'friend'  # MAJOR_CIV_OPINION_FRIEND
	ally = 'ally'  # MAJOR_CIV_OPINION_ALLY

	@staticmethod
	def all() -> List[MajorCivOpinionType]:
		return [
			MajorCivOpinionType.unforgivable,
			MajorCivOpinionType.enemy,
			MajorCivOpinionType.competitor,
			MajorCivOpinionType.neutral,
			MajorCivOpinionType.favorable,
			MajorCivOpinionType.friend,
			MajorCivOpinionType.ally
		]


class GuessConfidenceType(ExtendedEnum):
	none = 'none'  # NO_GUESS_CONFIDENCE_TYPE

	positive = 'positive'  # GUESS_CONFIDENCE_POSITIVE
	likely = 'likely'  # GUESS_CONFIDENCE_LIKELY
	unsure = 'unsure'  # GUESS_CONFIDENCE_UNSURE


class CoopWarStateType(ExtendedEnum):
	none = -1, 'none'  # NO_COOP_WAR_STATE

	rejected = 0, 'rejected'  # COOP_WAR_STATE_REJECTED
	soon = 1, 'soon'  # COOP_WAR_STATE_SOON
	accepted = 2, 'accepted'  # COOP_WAR_STATE_ACCEPTED

	def __new__(cls, value, name):
		member = object.__new__(cls)
		member._value = value
		member._name = name
		return member

	def value(self) -> int:
		return int(self._value)

	def __gt__(self, other):
		if isinstance(other, CoopWarStateType):
			return self._value > other._value

		raise Exception(f'cannot compare CoopWarStateType and {type(other)}')
