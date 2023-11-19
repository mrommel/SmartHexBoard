from typing import Optional

from smarthexboard.smarthexboardlib.core.base import WeightedBaseList
from smarthexboard.smarthexboardlib.core.types import EraType
from smarthexboard.smarthexboardlib.game.ai.diplomaticTypes import DiplomaticDeal, MajorPlayerApproachType, DiplomaticDealItemType, PeaceTreatyType, \
	DiplomaticDealDirectionType, MajorCivOpinionType, MinorPlayerApproachType
from smarthexboard.smarthexboardlib.game.ai.grandStrategies import GrandStrategyAIType
from smarthexboard.smarthexboardlib.game.ai.leagues import VoteCommitment
from smarthexboard.smarthexboardlib.game.baseTypes import WarProjectionType
from smarthexboard.smarthexboardlib.game.cities import City
from smarthexboard.smarthexboardlib.game.playerMechanics import PlayerProximityType
from smarthexboard.smarthexboardlib.game.playerTypes import InfluenceLevelType
from smarthexboard.smarthexboardlib.map.base import HexPoint
from smarthexboard.smarthexboardlib.map.constants import invalidHexPoint
from smarthexboard.smarthexboardlib.map.improvements import ImprovementType
from smarthexboard.smarthexboardlib.map.types import ResourceType, ResourceUsage
from smarthexboard.smarthexboardlib.utils.base import firstOrNone


class DealAI:
	def __init__(self, player):
		self.player = player

		self._cachedValueOfPeaceWithHuman: int = 0

	def makeOfferForDelegationTowards(self, otherPlayer, deal: DiplomaticDeal, simulation) -> bool:
		"""A good time to make an offer to get a delegation"""
		# Don't ask for Delegation if we're hostile or planning war
		approach: MajorPlayerApproachType = self.player.diplomacyAI.majorCivApproachTowards(otherPlayer, hideTrueFeelings=False)
		if (approach == MajorPlayerApproachType.hostile or
			approach == MajorPlayerApproachType.war or
			approach == MajorPlayerApproachType.guarded):
			return False

		# Can we actually complete this deal?
		if not deal.isPossibleToTradeItem(otherPlayer, self.player, DiplomaticDealItemType.allowDelegation, simulation=simulation):
			return False

		# Do we actually want OB with otherPlayer?
		if self.player.diplomacyAI.wantsDelegationFrom(otherPlayer):
			# Seed the deal with the item we want
			deal.addSendDelegationTowards(otherPlayer, simulation)
			dealAcceptable = False

			# AI evaluation
			if not otherPlayer.isHuman():
				# Change the deal as necessary to make it work
				dealAcceptable = self.doEqualizeDealWithAI(deal, otherPlayer, simulation)
			else:
				# Change the deal as necessary to make it work
				dealAcceptable, _, cantMatchOffer = self.doEqualizeDealWithHuman(deal, otherPlayer, False, True, simulation)

			return dealAcceptable

		return False

	def makeOfferForEmbassyTowards(self, otherPlayer, deal: DiplomaticDeal, simulation) -> bool:
		"""A good time to make an offer to get an embassy"""
		# Don't ask for Embassy if we're hostile or planning war
		approach: MajorPlayerApproachType = self.player.diplomacyAI.majorCivApproachTowards(otherPlayer, hideTrueFeelings=False)
		if (approach == MajorPlayerApproachType.hostile or
			approach == MajorPlayerApproachType.war or
			approach == MajorPlayerApproachType.guarded):
			return False

		# Can we actually complete this deal?
		if not deal.isPossibleToTradeItem(otherPlayer, self.player, DiplomaticDealItemType.allowEmbassy, simulation=simulation):
			return False

		# Do we actually want OB with otherPlayer?
		if self.player.diplomacyAI.wantsEmbassyFromPlayer(otherPlayer):
			# Seed the deal with the item we want
			deal.addAllowEmbassy(otherPlayer, simulation)

			# AI evaluation
			if not otherPlayer.isHuman():
				# Change the deal as necessary to make it work
				dealAcceptable = self.doEqualizeDealWithAI(deal, otherPlayer, simulation)
			else:
				# Change the deal as necessary to make it work
				dealAcceptable, _, cantMatchOffer = self.doEqualizeDealWithHuman(deal, otherPlayer, False, True, simulation)

			return dealAcceptable

		return False

	def isMakeOfferForOpenBorders(self, otherPlayer, deal: DiplomaticDeal, simulation) -> bool:
		"""A good time to make an offer to get Open Borders?"""
		# Don't ask for Open Borders if we're hostile or planning war
		approach: MajorPlayerApproachType = self.player.diplomacyAI.majorCivApproachTowards(otherPlayer, hideTrueFeelings=False)
		if approach == MajorPlayerApproachType.hostile or approach == MajorPlayerApproachType.war:
			return False

		# Can we actually complete this deal?
		if not deal.isPossibleToTradeItem(otherPlayer, self.player, DiplomaticDealItemType.openBorders, simulation=simulation):
			return False

		# Do we actually want OB with otherPlayer?
		if self.player.diplomacyAI.isWantsOpenBordersWith(otherPlayer):
			# Seed the deal with the item we want
			deal.addOpenBorders(otherPlayer, 30, simulation)  # GC.getGame().GetDealDuration()

			# AI evaluation
			if not otherPlayer.isHuman():
				# Change the deal as necessary to make it work
				dealAcceptable = self.doEqualizeDealWithAI(deal, otherPlayer, simulation)
			else:
				# Change the deal as necessary to make it work
				dealAcceptable, _, cantMatchOffer = self.doEqualizeDealWithHuman(deal, otherPlayer, False, True, simulation)

			return dealAcceptable

		return False

	def doEqualizeDealWithAI(self, deal: DiplomaticDeal, otherPlayer, simulation) -> bool:
		"""Try to even out the value on both sides. If bFavorMe is true we'll bias things in our favor if necessary"""
		if otherPlayer is None or self.player == otherPlayer:
			raise Exception("DEAL_AI: Trying to equalize AI deal, but both players are the same.")

		totalValue, iEvenValueImOffering, iEvenValueTheyreOffering = self.dealValue(deal, useEvenValue=True, simulation=simulation)

		dealDuration: int = 30  # GC.getGame().GetDealDuration()
		makeOffer: bool = False

		# // // // // // // // // // // // // // // /
		# Outline the boundaries for an acceptable deal
		# // // // // // // // // // // // // // // /

		percentOverWeWillRequest: int = self.dealPercentLeewayWithAI()
		percentUnderWeWillOffer: int = -self.dealPercentLeewayWithAI()

		dealSumValue = iEvenValueImOffering + iEvenValueTheyreOffering

		amountOverWeWillRequest: int = dealSumValue
		amountOverWeWillRequest *= percentOverWeWillRequest
		amountOverWeWillRequest /= 100

		amountUnderWeWillOffer: int = dealSumValue
		amountUnderWeWillOffer *= percentUnderWeWillOffer
		amountUnderWeWillOffer /= 100

		# Deal is already even enough for us
		if amountOverWeWillRequest >= totalValue >= amountUnderWeWillOffer:
			makeOffer = True

		counterDeal = DiplomaticDeal(deal.fromPlayer, deal.toPlayer)

		if not makeOffer:
			# // // // // // // // // // // // // // // /
			# See if there are items we can add or remove from either side to balance out the deal if it's not already even
			# // // // // // // // // // // // // // // /
			useEvenValue: bool = True
			totalValue: int = 0

			totalValue += self.doAddVoteCommitmentToThem(counterDeal, otherPlayer, False, totalValue, amountOverWeWillRequest, useEvenValue, simulation)
			totalValue += self.doAddVoteCommitmentToUs(counterDeal, otherPlayer, False, totalValue, amountUnderWeWillOffer, useEvenValue, simulation)

			totalValue += self.doAddResourceToThem(counterDeal, otherPlayer, False, totalValue, amountOverWeWillRequest, dealDuration, useEvenValue, simulation)
			totalValue += self.doAddResourceToUs(counterDeal, otherPlayer, False, totalValue, amountUnderWeWillOffer, dealDuration, useEvenValue, simulation)

			totalValue += self.doAddOpenBordersToThem(counterDeal, otherPlayer, True, totalValue, amountOverWeWillRequest, dealDuration, useEvenValue, simulation)
			totalValue += self.doAddOpenBordersToUs(counterDeal, otherPlayer, True, totalValue, amountUnderWeWillOffer, dealDuration, useEvenValue, simulation)

			totalValue += self.doAddGoldPerTurnToThem(counterDeal, otherPlayer, False, totalValue, dealDuration, useEvenValue, simulation)
			totalValue += self.doAddGoldPerTurnToUs(counterDeal, otherPlayer, False, totalValue, dealDuration, useEvenValue, simulation)

			totalValue += self.doAddGoldToThem(counterDeal, otherPlayer, False, totalValue, useEvenValue, simulation)
			totalValue += self.doAddGoldToUs(counterDeal, otherPlayer, False, totalValue, useEvenValue, simulation)

			totalValue += self.doRemoveGoldPerTurnFromThem(counterDeal, otherPlayer, totalValue, dealDuration, useEvenValue, simulation)
			totalValue += self.doRemoveGoldPerTurnFromUs(counterDeal, otherPlayer, totalValue, dealDuration, useEvenValue, simulation)

			totalValue += self.doRemoveGoldFromUs(counterDeal, otherPlayer, totalValue, useEvenValue, simulation)
			totalValue += self.doRemoveGoldFromThem(counterDeal, otherPlayer, totalValue, useEvenValue, simulation)

			# Make sure we haven't removed everything from the deal!
			if len(counterDeal.tradeItems) > 0:
				_, valueIThinkImOffering, valueIThinkImGetting = self.dealValue(deal, useEvenValue=False, simulation=simulation)

				# We don't think we're getting enough for what's on our side of the table
				lowEndOfWhatIWillAccept = valueIThinkImOffering - (valueIThinkImOffering * -percentUnderWeWillOffer / 100)
				if valueIThinkImGetting < lowEndOfWhatIWillAccept:
					return False

				_, valueTheyThinkTheyreOffering, valueTheyThinkTheyreGetting = otherPlayer.dealAI.dealValue(deal, useEvenValue=False)

				# They don't think they're getting enough for what's on their side of the table
				lowEndOfWhatTheyWillAccept = valueTheyThinkTheyreOffering - (valueTheyThinkTheyreOffering * otherPlayer.dealAI.dealPercentLeewayWithAI() / 100)
				if valueTheyThinkTheyreGetting < lowEndOfWhatTheyWillAccept:
					return False

				makeOffer = True

		return makeOffer

	def doAddResourceToThem(self, deal: DiplomaticDeal, otherPlayer, dontChangeTheirExistingItems: bool, totalValue: int, amountOverWeWillRequest: int, dealDuration: int, useEvenValue: bool, simulation) -> int:
		"""See if adding a Resource to their side of the deal helps even out deal"""
		if otherPlayer == self.player:
			raise Exception("DEAL_AI: Trying to add Resource to Them, but them is us.")

		if not dontChangeTheirExistingItems:
			if totalValue < 0:
				# Look to trade Luxuries first
				for loopResource in ResourceType.luxury():
					resourceQuantity = otherPlayer.numberOfAvailableResource(loopResource)

					# Don't bother looking at this Resource if the other player doesn't even have any of it
					if resourceQuantity <= 0:
						continue

					# Don't bother if we wouldn't get Happiness from it due to World Congress
					# if(GC.getGame().GetGameLeagues()->IsLuxuryHappinessBanned(self.player, resource))
					# continue

					# Quantity is always 1 if it's a Luxury, 5 if Strategic
					resourceQuantity = 1

					# See if they can actually trade it to us
					if deal.isPossibleToTradeItem(otherPlayer, self.player, DiplomaticDealItemType.resources, resource=loopResource, amount=resourceQuantity):
						itemValue = self.tradeItemValue(DiplomaticDealItemType.resources, False, otherPlayer, resourceQuantity, loopResource, duration=dealDuration, useEven=useEvenValue, simulation=simulation)

						# If adding this to the deal doesn't take it over the limit, do it
						if itemValue + totalValue <= amountOverWeWillRequest:
							# Try to change the current item if it already exists, otherwise add it
							if not deal.changeResourceTrade(otherPlayer, loopResource, resourceQuantity, dealDuration, simulation):
								deal.addResourceTrade(otherPlayer, loopResource, resourceQuantity, dealDuration, simulation)
								totalValue, valueImOffering, valueTheyreOffering = self.dealValue(deal, useEvenValue, simulation=simulation)

				# Now look at Strategic Resources
				for loopResource in ResourceType.strategic():
					resourceQuantity = otherPlayer.numberOfAvailableResource(loopResource)

					# Don't bother looking at this Resource if the other player doesn't even have any of it
					if resourceQuantity <= 0:
						continue

					# Quantity is always 1 if it's a Luxury, 5 if Strategic
					resourceQuantity = min(5, resourceQuantity)  # 5 or what they have, whichever is less

					# See if they can actually trade it to us
					if deal.isPossibleToTradeItem(otherPlayer, self.player, DiplomaticDealItemType.resources, amount=resourceQuantity, resource=loopResource):
						itemValue = self.tradeItemValue(DiplomaticDealItemType.resources, False, otherPlayer, amount=resourceQuantity, resource=loopResource, duration=dealDuration, useEven=useEvenValue, simulation=simulation)

						# If adding this to the deal doesn't take it over the limit, do it
						if itemValue + totalValue <= amountOverWeWillRequest:
							# Try to change the current item if it already exists, otherwise add it
							if not deal.changeResourceTrade(otherPlayer, loopResource, resourceQuantity, dealDuration, simulation):
								deal.addResourceTrade(otherPlayer, loopResource, resourceQuantity, dealDuration, simulation)
								totalValue, _, _ = self.dealValue(deal, useEvenValue, simulation=simulation)

		return totalValue

	def doAddResourceToUs(self, deal: DiplomaticDeal, otherPlayer, dontChangeMyExistingItems: bool, totalValue: int, amountOverWeWillRequest: int, dealDuration: int, useEvenValue: bool, simulation) -> int:
		"""See if adding a Resource to our side of the deal helps even out deal"""
		if otherPlayer == self.player:
			raise Exception("DEAL_AI: Trying to add Resource to Us, but them is us.")

		if not dontChangeMyExistingItems:
			if totalValue > 0:
				for loopResource in (ResourceType.luxury() + ResourceType.strategic()):
					resourceQuantity = otherPlayer.numberOfAvailableResource(loopResource)

					# Don't bother looking at this Resource if the other player doesn't even have any of it
					if resourceQuantity <= 0:
						continue

					if loopResource.usage() == ResourceUsage.luxury:
						# Quantity is always 1 if it's a Luxury, 5 if Strategic
						resourceQuantity = 1

						# Don't bother if they wouldn't get Happiness from it due to World Congress
						# if (GC.getGame().GetGameLeagues()->IsLuxuryHappinessBanned(otherPlayer, resource))
						#	continue
					elif loopResource.usage() == ResourceUsage.strategic:
						resourceQuantity = min(5, resourceQuantity)  # 5 or what we have, whichever is less

					# See if we can actually trade it to them
					if deal.isPossibleToTradeItem(self.player, otherPlayer, DiplomaticDealItemType.resources, resourceQuantity, loopResource, simulation=simulation):
						itemValue = self.tradeItemValue(DiplomaticDealItemType.resources, True, otherPlayer, resourceQuantity, loopResource, dealDuration, useEven=useEvenValue, simulation=simulation)

						# If adding this to the deal doesn't take it under the min limit, do it
						if -itemValue + totalValue >= amountOverWeWillRequest:
							# Try to change the current item if it already exists, otherwise add it
							if not deal.changeResourceTrade(self.player, resource=loopResource, amount=resourceQuantity, dealDuration=dealDuration, simulation=simulation):
								deal.addResourceTrade(self.player, resource=loopResource, amount=resourceQuantity, duration=dealDuration, simulation=simulation)
								totalValue, _, _ = self.dealValue(deal, useEvenValue, simulation=simulation)

		return totalValue

	def dealValue(self, deal: DiplomaticDeal, useEvenValue: bool, simulation) -> (int, int, int):
		"""What do we think of a Deal?"""
		dealValue: int = 0
		valueImOffering: int = 0
		valueTheyreOffering: int = 0

		if self.player == deal.fromPlayer:
			fromMe = True
			otherPlayer = deal.otherPlayerOf(self.player)
		else:
			fromMe = False
			otherPlayer = deal.fromPlayer

		# Multiplier is -1 if we're giving something away, 1 if we're receiving something
		iValueMultiplier = -1 if fromMe else 1

		for it in deal.tradeItems:
			itemValue = self.tradeItemValue(it.itemType, fromMe, otherPlayer, amount=it.amount, resource=it.resource,
			                                 duration=it.duration, point=it.point, thirdPlayer=it.thirdPlayer,
			                                 useEven=useEvenValue, simulation=simulation)

			itemValue *= iValueMultiplier if it.direction == DiplomaticDealDirectionType.give else -iValueMultiplier
			dealValue += itemValue

			# Figure out whose offering what, and keep track of the overall value on both sides of the deal
			if itemValue < 0:
				valueImOffering -= itemValue
			else:
				valueTheyreOffering += itemValue

		return dealValue, valueImOffering, valueTheyreOffering

	def tradeItemValue(self, itemType: DiplomaticDealItemType, fromMe: bool, otherPlayer, amount: int=-1,
	                   resource: ResourceType=ResourceType.none, duration: int=-1, point: Optional[HexPoint]=None,
	                   thirdPlayer=None, useEven: bool=False, simulation=None) -> int:
		"""What is a particular item worth?"""
		if simulation is None:
			raise Exception("simulation must not be None")

		if itemType == DiplomaticDealItemType.gold:
			itemValue = self.goldForValueExchange(amount, False, fromMe, otherPlayer, useEven, False)
		elif itemType == DiplomaticDealItemType.goldPerTurn:
			itemValue = self.goldPerTurnForValueExchange(amount, False, duration, fromMe, otherPlayer, useEven, False)
		elif itemType == DiplomaticDealItemType.resources:
			itemValue = self.resourceValue(resource, amount, duration, fromMe, otherPlayer, simulation)
		elif itemType == DiplomaticDealItemType.cities:
			itemValue = self.cityValue(point, fromMe, otherPlayer, useEven, simulation)
		elif itemType == DiplomaticDealItemType.allowDelegation:
			itemValue = self.delegationValue(fromMe, otherPlayer, useEven)
		elif itemType == DiplomaticDealItemType.allowEmbassy:
			itemValue = self.embassyValue(fromMe, otherPlayer, useEven)
		elif itemType == DiplomaticDealItemType.openBorders:
			itemValue = self.openBordersValue(fromMe, otherPlayer, useEven, simulation)
		elif itemType == DiplomaticDealItemType.defensivePact:
			itemValue = self.defensivePactValue(fromMe, otherPlayer, useEven)
		elif itemType == DiplomaticDealItemType.researchAgreement:
			itemValue = self.researchAgreementValue(fromMe, otherPlayer, useEven)
		# elif itemType == DiplomaticDealItemType.TRADE_AGREEMENT:
		#	itemValue = GetTradeAgreementValue(fromMe, otherPlayer, useEvenValue)
		elif itemType == DiplomaticDealItemType.peaceTreaty:
			itemValue = self.peaceTreatyValue(otherPlayer)
		elif itemType == DiplomaticDealItemType.thirdPartyPeace:
			itemValue = self.thirdPartyPeaceValue(fromMe, otherPlayer, thirdPlayer, simulation)
		elif itemType == DiplomaticDealItemType.thirdPartyWar:
			itemValue = self.thirdPartyWarValue(fromMe, otherPlayer, thirdPlayer, simulation)
		elif itemType == DiplomaticDealItemType.voteCommitment:
			itemValue = self.voteCommitmentValue(fromMe, otherPlayer, useEven)  # , iData1, iData2, iData3, bFlag1
		else:
			raise Exception(f'Type not handled: {itemType}')

		if itemValue < 0:
			raise Exception("DEAL_AI: Trade Item value is negative.")

		return itemValue

	def delegationValue(self, fromMe: bool, otherPlayer, useEven: bool) -> int:
		"""How much is a delegation worth?"""
		itemValue: int = 35

		if fromMe:  # giving the other player an embassy in my capital
			# Approach is important
			approach = self.player.diplomacyAI.majorCivApproachTowards(otherPlayer, hideTrueFeelings=True)
			if approach == MajorPlayerApproachType.hostile:
				itemValue *= 250
			elif approach == MajorPlayerApproachType.guarded:
				itemValue *= 130
			elif approach == MajorPlayerApproachType.afraid:
				itemValue *= 80
			elif approach == MajorPlayerApproachType.friendly:
				itemValue *= 100
			elif approach == MajorPlayerApproachType.neutral:
				itemValue *= 100
			else:
				raise Exception("DEAL_AI: AI player has no valid Approach for Research Agreement valuation.")

			itemValue /= 100

		# Are we trying to find the middle point between what we think this item is worth and
		# what another player thinks it's worth?
		if useEven:
			itemValue += otherPlayer.dealAI.delegationValue(not fromMe, self.player, useEven=False)
			itemValue /= 2

		return itemValue

	def dealPercentLeewayWithAI(self) -> int:
		""" How much are we willing to back off on what our perceived value of a deal is with an AI player to make
		something work?"""
		return 25

	def dealPercentLeewayWithHuman(self) -> int:
		"""How much are we willing to back off on what our perceived value of a deal is with a human player to make
		something work?"""
		return 10

	def doEqualizeDealWithHuman(self, deal: DiplomaticDeal, otherPlayer, dontChangeMyExistingItems: bool,
	                            dontChangeTheirExistingItems: bool, simulation) -> (bool, bool, bool):
		"""Try to even out the value on both sides. If bFavorMe is true we'll bias things in our favor if necessary"""
		if self.player == otherPlayer:
			raise Exception("DEAL_AI: Trying to equalize human deal, but both players are the same.")

		dealDuration = 30  # GC.getGame().GetDealDuration()
		cantMatchOffer = False
		dealGoodToBeginWith = False

		# Is this a peace deal?
		if deal.isPeaceTreatyTrade(otherPlayer):
			deal.clearItems()
			makeOffer = self.isOfferPeace(otherPlayer, deal, True, simulation)
		else:
			activePlayer = simulation.activePlayer()
			makeOffer, totalValueToMe, valueImOffering, valueTheyreOffering, amountOverWeWillRequest, amountUnderWeWillOffer, cantMatchOffer = self.isDealWithHumanAcceptable(deal, activePlayer, simulation)

			if totalValueToMe < 0 and dontChangeTheirExistingItems:
				return False, dealGoodToBeginWith, cantMatchOffer

			if makeOffer:
				dealGoodToBeginWith = True
			else:
				dealGoodToBeginWith = False

			if not makeOffer:
				# // // // // // // // // // // // // // // /
				# See if there are items we can add or remove from either side to balance out the deal if it's not already even
				# // // // // // // // // // // // // // // /
				useEvenValue: bool = False
				totalValue: int = 0

				# Maybe reorder these based on the AI's priorities (e.g. if it really doesn't want to give up
				# Strategic Resources try adding those from us last)

				# --DoAddCitiesToThem(deal, otherPlayer, bDontChangeTheirExistingItems, totalValueToMe, valueImOffering, valueTheyreOffering, amountOverWeWillRequest, dealDuration, useEvenValue)

				totalValue += self.doAddVoteCommitmentToThem(deal, otherPlayer, dontChangeTheirExistingItems, totalValueToMe, amountOverWeWillRequest, useEvenValue=useEvenValue, simulation=simulation)
				totalValue += self.doAddVoteCommitmentToUs(deal, otherPlayer, dontChangeMyExistingItems, totalValueToMe, amountUnderWeWillOffer, useEvenValue=useEvenValue, simulation=simulation)

				# fixme doAddDelegationToThem
				# fixme doAddDelegationToUs

				totalValue += self.doAddEmbassyToThem(deal, otherPlayer, dontChangeTheirExistingItems, totalValueToMe, amountOverWeWillRequest, useEvenValue, simulation=simulation)
				totalValue += self.doAddEmbassyToUs(deal, otherPlayer, dontChangeMyExistingItems, totalValueToMe, amountUnderWeWillOffer, useEvenValue, simulation=simulation)

				totalValue += self.doAddResourceToThem(deal, otherPlayer, dontChangeTheirExistingItems, totalValueToMe, amountOverWeWillRequest, dealDuration, useEvenValue, simulation=simulation)
				totalValue += self.doAddResourceToUs(deal, otherPlayer, dontChangeMyExistingItems, totalValueToMe, amountUnderWeWillOffer, dealDuration, useEvenValue, simulation=simulation)

				totalValue += self.doAddOpenBordersToThem(deal, otherPlayer, dontChangeTheirExistingItems, totalValueToMe, amountOverWeWillRequest, dealDuration=dealDuration, useEvenValue=useEvenValue, simulation=simulation)
				totalValue += self.doAddOpenBordersToUs(deal, otherPlayer, dontChangeMyExistingItems, totalValueToMe, amountUnderWeWillOffer, dealDuration=dealDuration, useEvenValue=useEvenValue, simulation=simulation)

				totalValue += self.doAddGoldPerTurnToThem(deal, otherPlayer, dontChangeTheirExistingItems, totalValueToMe, dealDuration, useEvenValue, simulation=simulation)
				totalValue += self.doAddGoldPerTurnToUs(deal, otherPlayer, dontChangeMyExistingItems, totalValueToMe, dealDuration, useEvenValue, simulation=simulation)

				totalValue += self.doAddGoldToThem(deal, otherPlayer, dontChangeTheirExistingItems, totalValueToMe, useEvenValue, simulation=simulation)
				totalValue += self.doAddGoldToUs(deal, otherPlayer, dontChangeMyExistingItems, totalValueToMe, useEvenValue, simulation=simulation)

				if not dontChangeTheirExistingItems:
					totalValue += self.doRemoveGoldPerTurnFromThem(deal, otherPlayer, totalValueToMe, dealDuration, useEvenValue, simulation=simulation)

				if not dontChangeMyExistingItems:
					totalValue += self.doRemoveGoldPerTurnFromUs(deal, otherPlayer, totalValueToMe, dealDuration, useEvenValue, simulation=simulation)

				totalValue += self.doRemoveGoldFromUs(deal, otherPlayer, totalValueToMe, useEvenValue, simulation=simulation)
				totalValue += self.doRemoveGoldFromThem(deal, otherPlayer, totalValueToMe, useEvenValue, simulation=simulation)

				totalValue += self.doAddCitiesToUs(deal, otherPlayer, dontChangeMyExistingItems, totalValueToMe, amountUnderWeWillOffer, useEvenValue, simulation=simulation)

				# Make sure we haven't removed everything from the deal!
				if len(deal.tradeItems) > 0:
					makeOffer, totalValueToMe, valueImOffering, valueTheyreOffering, amountOverWeWillRequest, amountUnderWeWillOffer, cantMatchOffer = self.isDealWithHumanAcceptable(deal, activePlayer, simulation=simulation)

		return makeOffer, dealGoodToBeginWith, cantMatchOffer

	def isOfferPeace(self, otherPlayer, deal: DiplomaticDeal, equalizingDeals: bool, simulation) -> bool:
		"""Offer peace"""
		result: bool = False

		# Can we actually complete this deal?
		if not deal.isPossibleToTradeItem(self.player, otherPlayer, DiplomaticDealItemType.peaceTreaty, simulation=simulation):
			return False

		if not deal.isPossibleToTradeItem(otherPlayer, self.player, DiplomaticDealItemType.peaceTreaty, simulation=simulation):
			return False

		peaceTreatyImWillingToOffer: PeaceTreatyType = self.player.diplomacyAI.treatyWillingToOffer(otherPlayer)
		peaceTreatyImWillingToAccept: PeaceTreatyType = self.player.diplomacyAI.treatyWillingToAccept(otherPlayer)

		# Peace between AI players
		if not otherPlayer.isHuman():
			peaceTreatyTheyreWillingToAccept: PeaceTreatyType = otherPlayer.diplomacyAI.GetTreatyWillingToAccept(self.player)
			peaceTreatyTheyreWillingToOffer: PeaceTreatyType = otherPlayer.diplomacyAI.GetTreatyWillingToOffer(self.player)

			# Is what we're willing to offer acceptable to otherPlayer?
			if peaceTreatyImWillingToOffer < peaceTreatyTheyreWillingToAccept:
				return False

			# Is what otherPlayer is willing to offer acceptable to us?
			if peaceTreatyTheyreWillingToOffer < peaceTreatyImWillingToAccept:
				return False

			# If we're both willing to give something up (for whatever reason) reduce the surrender level of both
			# parties until White Peace is on one side
			if peaceTreatyImWillingToOffer > PeaceTreatyType.whitePeace and \
				peaceTreatyTheyreWillingToOffer > PeaceTreatyType.whitePeace:
				amountToReduce = min(peaceTreatyImWillingToOffer, peaceTreatyTheyreWillingToOffer)

				peaceTreatyImWillingToOffer = PeaceTreatyType.fromValue(peaceTreatyImWillingToOffer.value() - amountToReduce.value())
				peaceTreatyTheyreWillingToOffer = PeaceTreatyType.fromValue(peaceTreatyTheyreWillingToOffer.value() - amountToReduce.value())

			# Get the Peace in between if there's a gap
			if peaceTreatyImWillingToOffer > peaceTreatyTheyreWillingToAccept:
				peaceTreatyImWillingToOffer = PeaceTreatyType.fromValue(int((peaceTreatyImWillingToOffer.value() + peaceTreatyTheyreWillingToAccept.value()) / 2))
			if peaceTreatyTheyreWillingToOffer > peaceTreatyImWillingToAccept:
				peaceTreatyTheyreWillingToOffer = PeaceTreatyType.fromValue(int((peaceTreatyTheyreWillingToOffer.value() + peaceTreatyImWillingToAccept.value()) / 2))

			if peaceTreatyImWillingToOffer < PeaceTreatyType.whitePeace:
				raise Exception("DEAL_AI: I'm offering a peace treaty with negative ID.")
			if peaceTreatyTheyreWillingToOffer < PeaceTreatyType.whitePeace:
				raise Exception("DEAL_AI: They're offering a peace treaty with negative ID.")

			# I'm surrendering in this deal
			if peaceTreatyImWillingToOffer > peaceTreatyTheyreWillingToOffer:
				deal.updateSurrenderingPlayer(self.player)
				deal.updatePeaceTreatyType(peaceTreatyImWillingToOffer)

				self.doAddItemsToDealForPeaceTreaty(otherPlayer, deal, peaceTreatyImWillingToOffer, meSurrendering=True, simulation=simulation)

			# They're surrendering in this deal
			elif peaceTreatyImWillingToOffer < peaceTreatyTheyreWillingToOffer:
				deal.updateSurrenderingPlayer(otherPlayer)
				deal.updatePeaceTreatyType(peaceTreatyTheyreWillingToOffer)

				self.doAddItemsToDealForPeaceTreaty(otherPlayer, deal, peaceTreatyTheyreWillingToOffer, meSurrendering=False, simulation=simulation)

			# Add the peace items to the deal so that we actually stop the war
			peaceTreatyLength = 10  # GC.getGame().getGameSpeedInfo().getPeaceDealDuration()
			deal.addPeaceTreaty(self.player, peaceTreatyLength)
			deal.addPeaceTreaty(otherPlayer, peaceTreatyLength)

			result = True
		# Peace with a human
		else:
			# AI is surrendering
			if peaceTreatyImWillingToOffer > PeaceTreatyType.whitePeace:
				deal.updateSurrenderingPlayer(self.player)
				deal.updatePeaceTreatyType(peaceTreatyImWillingToOffer)

				self.doAddItemsToDealForPeaceTreaty(otherPlayer, deal, peaceTreatyImWillingToOffer, meSurrendering=True, simulation=simulation)

				# Store the value of the deal with the human so that we have a number to use for renegotiation ( if necessary)
				_, valueImOffering, valueTheyreOffering = self.dealValue(deal, useEvenValue=False, simulation=simulation)
				if not equalizingDeals:
					self.setCachedValueOfPeaceWithHuman(-valueImOffering)
			# AI is asking human to surrender
			elif peaceTreatyImWillingToAccept > PeaceTreatyType.whitePeace:
				deal.updateSurrenderingPlayer(otherPlayer)
				deal.updatePeaceTreatyType(peaceTreatyImWillingToAccept)

				self.doAddItemsToDealForPeaceTreaty(otherPlayer, deal, peaceTreatyImWillingToAccept, meSurrendering=False, simulation=simulation)

				# Store the value of the deal with the human so that we have a number to use for renegotiation ( if necessary)
				_, valueImOffering, valueTheyreOffering = self.dealValue(deal, useEvenValue=False, simulation=simulation)
				if not equalizingDeals:
					self.setCachedValueOfPeaceWithHuman(valueTheyreOffering)
			else:
				# if the case is that we both want white peace, don't forget to add the city-states into the peace deal.
				self.doAddPlayersAlliesToTreaty(otherPlayer, deal, simulation)

			peaceTreatyLength = 10  # GC.getGame().getGameSpeedInfo().getPeaceDealDuration()
			deal.addPeaceTreaty(self.player, peaceTreatyLength)
			deal.addPeaceTreaty(otherPlayer, peaceTreatyLength)

			result = True

		return result

	def isDealWithHumanAcceptable(self, deal: DiplomaticDeal, otherPlayer, simulation) -> (bool, int, int, int, int, int, bool):
		"""Will this AI accept deal? Handles deal from both human and AI players"""
		cantMatchOffer: bool = False

		# Deal leeway with human
		percentOverWeWillRequest: int = self.dealPercentLeewayWithHuman()
		percentUnderWeWillOffer: int = 0

		# Now do the valuation
		totalValueToMe, valueImOffering, valueTheyreOffering = self.dealValue(deal, useEvenValue=False, simulation=simulation)

		# If no Gold in deal and within value of 1 GPT, then it's close enough
		if deal.goldTrade(otherPlayer) == 0 and deal.goldTrade(self.player) == 0:
			iOneGPT: int = 25
			iDiff = abs(valueTheyreOffering - valueImOffering)
			if iDiff < iOneGPT:
				return True, totalValueToMe, valueImOffering, valueTheyreOffering, percentOverWeWillRequest, percentUnderWeWillOffer, cantMatchOffer

		dealSumValue: int = valueImOffering + valueTheyreOffering

		amountOverWeWillRequest = dealSumValue
		amountOverWeWillRequest *= percentOverWeWillRequest
		amountOverWeWillRequest /= 100

		amountUnderWeWillOffer = dealSumValue
		amountUnderWeWillOffer *= percentUnderWeWillOffer
		amountUnderWeWillOffer /= 100

		# We're surrendering
		if deal.surrenderingPlayer() is not None and deal.surrenderingPlayer() == self.player:
			if totalValueToMe >= self.cachedValueOfPeaceWithHuman():
				return True, totalValueToMe, valueImOffering, valueTheyreOffering, percentOverWeWillRequest, percentUnderWeWillOffer, cantMatchOffer

		# Peace deal where we're not surrendering, value must equal cached value
		elif deal.isPeaceTreatyTrade(otherPlayer):
			if totalValueToMe >= self.cachedValueOfPeaceWithHuman():
				return True, totalValueToMe, valueImOffering, valueTheyreOffering, percentOverWeWillRequest, percentUnderWeWillOffer, cantMatchOffer

		# If we've gotten the deal to a point where we're happy, offer it up
		elif amountOverWeWillRequest >= totalValueToMe >= amountUnderWeWillOffer:
			return True, totalValueToMe, valueImOffering, valueTheyreOffering, percentOverWeWillRequest, percentUnderWeWillOffer, cantMatchOffer

		elif totalValueToMe > amountOverWeWillRequest:
			cantMatchOffer = True

		return False, totalValueToMe, valueImOffering, valueTheyreOffering, percentOverWeWillRequest, percentUnderWeWillOffer, cantMatchOffer

	def setCachedValueOfPeaceWithHuman(self, value):
		"""Sets what are we willing to give/receive for peace with the active human player"""
		self._cachedValueOfPeaceWithHuman = value

	def cachedValueOfPeaceWithHuman(self) -> int:
		"""What are we willing to give/receive for peace with the active human player?"""
		return self._cachedValueOfPeaceWithHuman

	def doAddPlayersAlliesToTreaty(self, otherPlayer, deal, simulation):
		"""Add third party peace for allied city-states"""
		iPeaceDuration: int = 10  # GC.getGame().getGameSpeedInfo().getPeaceDealDuration()
		for minorPlayer in simulation.players:
			if not minorPlayer.isCityState():
				continue

			# Minor not alive?
			if not minorPlayer.isAlive():
				continue

			ally = minorPlayer.minorCivAI.ally()

			# ally of other player
			if ally is not None and ally == otherPlayer:
				# if they are not at war with us, continue
				if not self.player.isAtWarWith(minorPlayer):
					continue

				# if they are always at war with us, continue
				if minorPlayer.minorCivAI.isPermanentWar(self.player):
					continue

				# Add peace with this minor to the deal
				# slewis - if there is not a peace deal with them already on the table and we can trade it
				if not deal.isThirdPartyPeaceTrade(self.player, minorPlayer) and deal.isPossibleToTradeItem(self.player, otherPlayer, DiplomaticDealItemType.thirdPartyPeace, minorPlayer):
					deal.addThirdPartyPeace(self.player, minorPlayer, iPeaceDuration)
			# ally with us
			elif ally == self.player:
				# if they are not at war with the opponent, continue
				if not otherPlayer.isAtWarWith(minorPlayer):
					continue

				# if they are always at war with them, continue
				if minorPlayer.minorCivAI.isPermanentWar(otherPlayer):
					continue

				# Add peace with this minor to the deal
				# slewis - if there is not a peace deal with them already on the table and we can trade it
				if not deal.isThirdPartyPeaceTrade(otherPlayer, minorPlayer) and deal.isPossibleToTradeItem(otherPlayer, self.player, DiplomaticDealItemType.thirdPartyPeace, minorPlayer):
					deal.addThirdPartyPeace(otherPlayer, minorPlayer, iPeaceDuration)

		return

	def goldPerTurnForValueExchange(self, amount, numberGPTFromValue: bool, duration: int, fromMe: bool, otherPlayer, useEven: bool, roundUp: bool) -> int:
		"""GetGPTforForValueExchange - How much GPT should be provided if we're trying to make it worth iValue?"""
		if self.player == otherPlayer:
			raise Exception("DEAL_AI: Trying to check value of GPT with oneself.")

		# We passed in Value, we want to know how much GPT we get for it
		if numberGPTFromValue:
			preCalculationDurationMultiplier = 1
			multiplier = 100
			divisor = 80  # EACH_GOLD_PER_TURN_VALUE_PERCENT
			postCalculationDurationDivider = duration  # Divide value by number of turns to get GPT

			# Example: want amount of GPT for 100 value.
			# 100v * 1 = 100
			# 100 * 100 / 80 = 125
			# 125 / 20 turns = 6.25GPT
		# We passed in an amount of GPT, we want to know how much it's worth
		else:
			preCalculationDurationMultiplier = duration  # Multiply GPT by number of turns to get value
			multiplier = 80  # EACH_GOLD_PER_TURN_VALUE_PERCENT
			divisor = 100
			postCalculationDurationDivider = 1

			# Example: want value for 6 GPT
			# 6GPT * 20 turns = 120
			# 120 * 80 / 100 = 96
			# 96 / 1 = 96v

		# Convert based on the rules above
		returnValue = amount * preCalculationDurationMultiplier
		returnValue *= multiplier

		# While we have a big number shall we apply some modifiers to it?
		if fromMe:
			# AI values it's GPT more highly because it's easy to exploit this
			# See whether we should multiply or divide
			if not numberGPTFromValue:
				returnValue *= 130
				returnValue /= 100
			else:
				returnValue *= 100
				returnValue /= 130

			# Approach is important
			approach = self.player.diplomacyAI.majorCivApproachTowards(otherPlayer, hideTrueFeelings=True)
			if approach == MajorPlayerApproachType.hostile:
				modifier = 150
			elif approach == MajorPlayerApproachType.guarded:
				modifier = 110
			elif approach == MajorPlayerApproachType.afraid:
				modifier = 100
			elif approach == MajorPlayerApproachType.friendly:
				modifier = 100
			elif approach == MajorPlayerApproachType.neutral:
				modifier = 100
			else:
				raise Exception("DEAL_AI: AI player has no valid Approach for Gold valuation.")

			# See whether we should multiply or divide
			if not numberGPTFromValue:
				returnValue *= modifier
				returnValue /= 100
			else:
				returnValue *= 100
				returnValue /= modifier

			# Opinion also matters
			opinion = self.player.diplomacyAI.majorCivOpinion(otherPlayer)
			if opinion == MajorCivOpinionType.ally:
				modifier = 100
			elif opinion == MajorCivOpinionType.friend:
				modifier = 100
			elif opinion == MajorCivOpinionType.favorable:
				modifier = 100
			elif opinion == MajorCivOpinionType.neutral:
				modifier = 100
			elif opinion == MajorCivOpinionType.competitor:
				modifier = 115
			elif opinion == MajorCivOpinionType.enemy:
				modifier = 140
			elif opinion == MajorCivOpinionType.unforgivable:
				modifier = 200
			else:
				raise Exception(f"DEAL_AI: AI player has no valid Opinion for Gold valuation: {opinion}")

			# See whether we should multiply or divide
			if not numberGPTFromValue:
				returnValue *= modifier
				returnValue /= 100
			else:
				returnValue *= 100
				returnValue /= modifier

		# Sometimes we want to round up. Let's say a the AI offers a deal to the human. We have to ensure that the
		# human can also offer that deal back and the AI will accept (and vice versa)
		if roundUp:
			returnValue += 99

		returnValue /= divisor
		returnValue /= postCalculationDurationDivider

		# Are we trying to find the middle point between what we think this item is worth and what another player
		# thinks it's worth?
		if useEven:
			returnValue += otherPlayer.dealAI.goldPerTurnForValueExchange(amount, numberGPTFromValue, duration, not fromMe, self.player, useEven=False, roundUp=roundUp)
			returnValue /= 2

		return returnValue

	def doAddVoteCommitmentToThem(self, deal: DiplomaticDeal, otherPlayer, dontChangeTheirExistingItems: bool, totalValue: int, amountOverWeWillRequest: int,
	                              useEvenValue: bool, simulation) -> int:
		"""See if adding Vote Commitment to their side of the deal helps even out deal"""
		if self.player == otherPlayer:
			raise Exception("DEAL_AI: Trying to add Vote Commitment to Them, but them is us.")

		if not dontChangeTheirExistingItems:
			if totalValue < 0:
				# Can't already be a Vote Commitment in the Deal
				if not deal.isVoteCommitmentTrade(otherPlayer) and not deal.isVoteCommitmentTrade(self.player):
					desiredCommitments: [VoteCommitment] = self.player.leagueAI.desiredVoteCommitments(otherPlayer)
					for it in desiredCommitments:
						proposalID: int = it.resolutionID
						# iVoteChoice: int = it.voteChoice
						# numVotes: int = it.numVotes
						bRepeal: bool = not it.enact

						if proposalID != -1 and deal.isPossibleToTradeItem(otherPlayer, self.player, DiplomaticDealItemType.voteCommitment, simulation=simulation):
							itemValue = self.tradeItemValue(DiplomaticDealItemType.voteCommitment, False, otherPlayer, useEven=useEvenValue, simulation=simulation)

							# If adding this to the deal doesn't take it over the limit, do it
							if itemValue + totalValue <= amountOverWeWillRequest:
								deal.addVoteCommitment(otherPlayer, 30, simulation)
								totalValue, _, _ = self.dealValue(deal, useEvenValue, simulation=simulation)

		return totalValue

	def doAddVoteCommitmentToUs(self, deal: DiplomaticDeal, otherPlayer, dontChangeMyExistingItems: bool, totalValue: int, amountUnderWeWillOffer: int,
	                            useEvenValue: bool, simulation) -> int:
		"""See if adding a Vote Commitment to our side of the deal helps even out deal"""
		if self.player == otherPlayer:
			raise Exception("DEAL_AI: Trying to add Vote Commitment to Us, but them is us.")

		if not dontChangeMyExistingItems:
			if totalValue > 0:
				# Can't already be a Vote Commitment in the Deal
				if not deal.isVoteCommitmentTrade(otherPlayer) and not deal.isVoteCommitmentTrade(self.player):
					desiredCommitments: [VoteCommitment] = self.player.leagueAI.desiredVoteCommitments(otherPlayer)
					for it in desiredCommitments:
						proposalID: int = it.resolutionID
						# iVoteChoice: int = it.voteChoice
						# numVotes: int = it.numVotes
						bRepeal: bool = not it.enact

						if proposalID != -1 and deal.isPossibleToTradeItem(self.player, otherPlayer, DiplomaticDealItemType.voteCommitment, simulation=simulation):
							itemValue = self.tradeItemValue(DiplomaticDealItemType.voteCommitment, True, otherPlayer, useEven=useEvenValue, simulation=simulation)

							# If adding this to the deal doesn't take it under the min limit, do it
							if -itemValue + totalValue >= amountUnderWeWillOffer:
								deal.addVoteCommitment(self.player, 30, simulation)
								totalValue, _, _ = self.dealValue(deal, useEvenValue, simulation=simulation)

		return totalValue

	def doAddOpenBordersToThem(self, deal: DiplomaticDeal, otherPlayer, dontChangeTheirExistingItems: bool, totalValue: int, amountOverWeWillRequest: int,
	                           dealDuration: int, useEvenValue: bool, simulation) -> int:
		"""See if adding Open Borders to their side of the deal helps even out deal"""
		if self.player == otherPlayer:
			raise Exception("DEAL_AI: Trying to add Open Borders to Them, but them is us.")

		if not dontChangeTheirExistingItems:
			if totalValue < 0:
				if not deal.isOpenBordersTrade(otherPlayer):
					# See if they can actually trade it to us
					if deal.isPossibleToTradeItem(otherPlayer, self.player, DiplomaticDealItemType.openBorders, simulation=simulation):
						itemValue = self.tradeItemValue(DiplomaticDealItemType.openBorders, False, otherPlayer, duration=dealDuration, useEven=useEvenValue, simulation=simulation)

						# If adding this to the deal doesn't take it over the limit, do it
						if itemValue + totalValue <= amountOverWeWillRequest:
							deal.addOpenBorders(otherPlayer, dealDuration, simulation=simulation)
							totalValue, _, _ = self.dealValue(deal, useEvenValue, simulation=simulation)

		return totalValue

	def doAddOpenBordersToUs(self, deal: DiplomaticDeal, otherPlayer, dontChangeMyExistingItems: bool, totalValue: int,
	                         amountUnderWeWillOffer: int, dealDuration: int, useEvenValue: bool, simulation) -> int:
		"""See if adding Open Borders to our side of the deal helps even out deal"""
		if self.player == otherPlayer:
			raise Exception("DEAL_AI: Trying to add Open Borders to Us, but them is us.")

		if not dontChangeMyExistingItems:
			if totalValue > 0:
				if not deal.isOpenBordersTrade(self.player):
					# See if we can actually trade it to them
					if deal.isPossibleToTradeItem(self.player, otherPlayer, DiplomaticDealItemType.openBorders, simulation=simulation):
						itemValue = self.tradeItemValue(DiplomaticDealItemType.openBorders, True, otherPlayer, duration=dealDuration, useEven=useEvenValue, simulation=simulation)

						# If adding this to the deal doesn't take it under the min limit, do it
						if -itemValue + totalValue >= amountUnderWeWillOffer:
							deal.addOpenBorders(self.player, dealDuration, simulation=simulation)
							totalValue, _, _ = self.dealValue(deal, useEvenValue, simulation=simulation)

		return totalValue

	def doAddGoldPerTurnToThem(self, deal: DiplomaticDeal, otherPlayer, dontChangeTheirExistingItems: bool,
	                           totalValue: int, dealDuration: int, useEvenValue: bool, simulation) -> int:
		"""DoAddGPTToThem - See if adding Gold Per Turn to their side of the deal helps even out deal"""
		if self.player == otherPlayer:
			raise Exception("DEAL_AI: Trying to add GoldPerTurn to Them, but them is us.")

		if not dontChangeTheirExistingItems:
			if totalValue < 0:
				if otherPlayer.treasury.calculateGrossGold(simulation) > 0:
					# Can't already be GPT from the other player in the Deal
					if deal.goldPerTurnTrade(self.player) == 0:
						numGoldPerTurn = self.goldPerTurnForValueExchange(-totalValue, numberGPTFromValue=True, duration=dealDuration, fromMe=False, otherPlayer=otherPlayer, useEven=useEvenValue, roundUp=False)
						numGoldPerTurnAlreadyInTrade = deal.goldPerTurnTrade(otherPlayer)
						numGoldPerTurn += numGoldPerTurnAlreadyInTrade
						numGoldPerTurn = min(numGoldPerTurn, otherPlayer.treasury.calculateGrossGold(simulation))

						if numGoldPerTurn != numGoldPerTurnAlreadyInTrade and not deal.changeGoldPerTurnTrade(otherPlayer, numGoldPerTurn, dealDuration, simulation):
							deal.addGoldPerTurnTradeFrom(otherPlayer, numGoldPerTurn, dealDuration, simulation)

						totalValue, _, _ = self.dealValue(deal, useEvenValue, simulation=simulation)

		return totalValue

	def doAddGoldPerTurnToUs(self, deal: DiplomaticDeal, otherPlayer, dontChangeMyExistingItems: bool, totalValue: int,
	                         dealDuration: int, useEvenValue: bool, simulation) -> int:
		"""DoAddGPTToUs - See if adding Gold Per Turn to our side of the deal helps even out deal"""
		if self.player == otherPlayer:
			raise Exception("DEAL_AI: Trying to add GPT to Us, but them is us.")

		if not dontChangeMyExistingItems:
			if totalValue > 0:
				if self.player.treasury.calculateGrossGold(simulation) > 0:
					# Can't already be GPT from the other player in the Deal
					if deal.goldPerTurnTrade(otherPlayer) == 0:
						numGoldPerTurn = self.goldPerTurnForValueExchange(totalValue, True, dealDuration, True, otherPlayer, useEven=useEvenValue, roundUp=False)
						numGoldPerTurnAlreadyInTrade = deal.goldPerTurnTrade(self.player)
						numGoldPerTurn += numGoldPerTurnAlreadyInTrade
						numGoldPerTurn = min(numGoldPerTurn, self.player.treasury.calculateGrossGold(simulation))

						if numGoldPerTurn != numGoldPerTurnAlreadyInTrade and not deal.changeGoldPerTurnTrade(self.player, numGoldPerTurn, dealDuration, simulation):
							deal.addGoldPerTurnTradeFrom(self.player, numGoldPerTurn, dealDuration, simulation)

						totalValue, _, _ = self.dealValue(deal, useEvenValue, simulation=simulation)

		return totalValue

	def doAddGoldToThem(self, deal: DiplomaticDeal, otherPlayer, dontChangeTheirExistingItems: bool, totalValue: int,
	                    useEvenValue: bool, simulation) -> int:
		"""See if adding Gold to their side of the deal helps even out deal"""
		if self.player == otherPlayer:
			raise Exception("DEAL_AI: Trying to add Gold to Them, but them is us.")

		if not dontChangeTheirExistingItems:
			if totalValue < 0:
				# Can't already be Gold from the other player in the Deal
				if deal.goldTrade(self.player) == 0:
					numGold = self.goldForValueExchange(-totalValue, True, False, otherPlayer, useEvenValue, False)
					numGoldAlreadyInTrade = deal.goldTrade(otherPlayer)
					numGold += numGoldAlreadyInTrade
					numGold = min(numGold, deal.goldAvailable(otherPlayer, DiplomaticDealItemType.gold, simulation))
					# -- numGold = min(numGold, GET_PLAYER(otherPlayer).GetTreasury()->GetGold())

					if numGold != numGoldAlreadyInTrade and not deal.changeGoldTrade(otherPlayer, numGold, simulation):
						deal.addGoldTradeFrom(otherPlayer, numGold, simulation)

					totalValue, _, _ = self.dealValue(deal, useEvenValue, simulation=simulation)

		return totalValue

	def doAddGoldToUs(self, deal: DiplomaticDeal, otherPlayer, dontChangeMyExistingItems: bool, totalValue: int,
	                  useEvenValue: bool, simulation) -> int:
		"""See if adding Gold to our side of the deal helps even out deal"""
		if self.player == otherPlayer:
			raise Exception("DEAL_AI: Trying to add Gold to Us, but them is us.")

		if not dontChangeMyExistingItems:
			if totalValue > 0:
				# Can't already be Gold from the other player in the Deal
				if deal.goldTrade(otherPlayer) == 0:
					numGold: int = self.goldForValueExchange(totalValue, True, True, otherPlayer, useEvenValue, False)
					numGoldAlreadyInTrade: int = deal.goldTrade(self.player)
					numGold += numGoldAlreadyInTrade
					numGold = min(numGold, deal.goldAvailable(self.player, DiplomaticDealItemType.gold, simulation))
					# -- numGold = min(numGold, GET_PLAYER(self.player).GetTreasury()->GetGold())

					if numGold != numGoldAlreadyInTrade and not deal.changeGoldTrade(self.player, numGold, simulation):
						deal.addGoldTradeFrom(self.player, numGold, simulation)

					totalValue, _, _ = self.dealValue(deal, useEvenValue, simulation=simulation)

		return totalValue

	def doRemoveGoldPerTurnFromThem(self, deal: DiplomaticDeal, otherPlayer, totalValue: int, dealDuration: int,
	                                useEvenValue: bool, simulation) -> int:
		"""See if removing Gold Per Turn from their side of the deal helps even out deal"""
		if self.player == otherPlayer:
			raise Exception("DEAL_AI: Trying to remove GPT from Them, but them is us.")

		if totalValue > 0:
			# Try to remove a bit more than the actual value discrepancy, as this should get us closer to even in the long - run
			valueToRemove: int = totalValue * 150
			valueToRemove /= 100

			numGoldPerTurnToRemove = self.goldPerTurnForValueExchange(valueToRemove, True, dealDuration, False, otherPlayer, useEvenValue, True)

			numGoldPerTurnInThisDeal = deal.goldPerTurnTrade(otherPlayer)
			if numGoldPerTurnInThisDeal > 0:
				# Found some GoldPerTurn to remove
				numGoldPerTurnToRemove = min(numGoldPerTurnToRemove, numGoldPerTurnInThisDeal)
				numGoldPerTurnInThisDeal -= numGoldPerTurnToRemove

				# Removing ALL GoldPerTurn, so just erase the item from the deal
				if numGoldPerTurnInThisDeal == 0:
					deal.removeByType(DiplomaticDealItemType.goldPerTurn)
					totalValue, _, _ = self.dealValue(deal, useEvenValue, simulation=simulation)
				# Remove some of the GoldPerTurn from the deal
				else:
					if not deal.changeGoldPerTurnTrade(otherPlayer, numGoldPerTurnInThisDeal, dealDuration, simulation):
						raise Exception("DEAL_AI: DealAI is trying to remove GoldPerTurn from a deal but couldn't find "
						                "the item for some reason.")

					totalValue, _, _ = self.dealValue(deal, useEvenValue, simulation=simulation)

		return totalValue

	def doRemoveGoldPerTurnFromUs(self, deal: DiplomaticDeal, otherPlayer, totalValue: int, dealDuration: int,
	                              useEvenValue: bool, simulation) -> int:
		"""DoRemoveGPTFromUs - See if removing Gold Per Turn from our side of the deal helps even out deal"""
		if self.player == otherPlayer:
			raise Exception("DEAL_AI: Trying to remove GPT from Us, but them is us.")

		if totalValue < 0:
			# Try to remove a bit more than the actual value discrepancy, as this should get us closer to even in the long-run
			valueToRemove: int = -totalValue * 150
			valueToRemove /= 100

			numGoldPerTurnToRemove = self.goldPerTurnForValueExchange(valueToRemove, True, dealDuration, True, otherPlayer, useEvenValue, True)

			numGoldPerTurnInThisDeal = deal.goldPerTurnTrade(self.player)
			if numGoldPerTurnInThisDeal > 0:
				# Found some GoldPerTurn to remove
				numGoldPerTurnToRemove = min(numGoldPerTurnToRemove, numGoldPerTurnInThisDeal)
				numGoldPerTurnInThisDeal -= numGoldPerTurnToRemove

				# Removing ALL GoldPerTurn, so just erase the item from the deal
				if numGoldPerTurnInThisDeal == 0:
					deal.removeByType(DiplomaticDealItemType.goldPerTurn)
					totalValue, _, _ = self.dealValue(deal, useEvenValue, simulation=simulation)
				# Remove some of the GoldPerTurn from the deal
				else:
					if not deal.changeGoldPerTurnTrade(self.player, numGoldPerTurnInThisDeal, dealDuration, simulation):
						raise Exception("DEAL_AI: DealAI is trying to remove GoldPerTurn from a deal but couldn't find "
						                "the item for some reason.")

					totalValue, _, _ = self.dealValue(deal, useEvenValue, simulation=simulation)

		return totalValue

	def doRemoveGoldFromUs(self, deal: DiplomaticDeal, otherPlayer, totalValue: int, useEvenValue: bool, simulation) -> int:
		"""See if removing Gold from our side of the deal helps even out deal"""
		if self.player == otherPlayer:
			raise Exception("DEAL_AI: Trying to remove Gold from Us, but them is us.")

		if totalValue < 0:
			numGoldInThisDeal = deal.goldTrade(self.player)
			if numGoldInThisDeal > 0:
				# Found some Gold to remove
				valueToRemove = self.goldForValueExchange(-totalValue, True, True, otherPlayer, useEvenValue, True)
				numGoldToRemove: int = min(numGoldInThisDeal, valueToRemove)
				numGoldInThisDeal -= numGoldToRemove

				# Removing ALL Gold, so just erase the item from the deal
				if numGoldInThisDeal == 0:
					deal.removeByType(DiplomaticDealItemType.gold)
					totalValue, _, _ = self.dealValue(deal, useEvenValue, simulation=simulation)
				# Remove some of the Gold from the deal
				else:
					if not deal.changeGoldTrade(self.player, numGoldInThisDeal, simulation):
						raise Exception("DEAL_AI: DealAI is trying to remove Gold from a deal but couldn't find the item for some reason.")

					totalValue, _, _ = self.dealValue(deal, useEvenValue, simulation=simulation)

		return totalValue

	def doRemoveGoldFromThem(self, deal: DiplomaticDeal, otherPlayer, totalValue: int, useEvenValue: bool, simulation) -> int:
		"""See if removing Gold from their side of the deal helps even out deal"""
		if self.player == otherPlayer:
			raise Exception("DEAL_AI: Trying to remove Gold from Them, but them is us.")

		if totalValue > 0:
			numGoldInThisDeal: int = deal.goldTrade(otherPlayer)
			if numGoldInThisDeal > 0:
				# Found some Gold to remove
				goldToRemove = self.goldForValueExchange(totalValue, True, False, otherPlayer, useEvenValue, True)
				numGoldToRemove: int = min(numGoldInThisDeal, goldToRemove)
				numGoldInThisDeal -= numGoldToRemove

				# Removing ALL Gold, so just erase the item from the deal
				if numGoldInThisDeal == 0:
					deal.removeByType(DiplomaticDealItemType.gold)
					totalValue, _, _ = self.dealValue(deal, useEvenValue, simulation=simulation)
				# Remove some of the Gold from the deal
				else:
					if not deal.changeGoldTrade(otherPlayer, numGoldInThisDeal, simulation):
						raise Exception("DEAL_AI: DealAI is trying to remove Gold from a deal but couldn't find the item for some reason.")

					totalValue, _, _ = self.dealValue(deal, useEvenValue, simulation=simulation)
			
		return totalValue

	def goldForValueExchange(self, goldOrValue: int, numGoldFromValue: bool, fromMe: bool, otherPlayer, useEven: bool,
	                         roundUp: bool) -> int:
		"""How much Gold should be provided if we're trying to make it worth iValue?"""
		# We passed in Value, we want to know how much Gold we get for it
		if numGoldFromValue:
			multiplier = 100
			divisor = 100  # EACH_GOLD_VALUE_PERCENT

			# Protect against a modder setting this to 0
			if divisor == 0:
				divisor = 1
		# We passed in an amount of Gold, we want to know how much it's worth
		else:
			multiplier = 100  # EACH_GOLD_VALUE_PERCENT
			divisor = 100

		# Convert based on the rules above
		returnValue = goldOrValue * multiplier

		# While we have a big number shall we apply some modifiers to it?
		if fromMe:
			# Approach is important
			approach = self.player.diplomacyAI.majorCivApproachTowards(otherPlayer, hideTrueFeelings=True)
			if approach == MajorPlayerApproachType.hostile:
				modifier = 150
			elif approach == MajorPlayerApproachType.guarded:
				modifier = 110
			elif approach == MajorPlayerApproachType.afraid:
				modifier = 100
			elif approach == MajorPlayerApproachType.friendly:
				modifier = 100
			elif approach == MajorPlayerApproachType.neutral:
				modifier = 100
			else:
				raise Exception("DEAL_AI: AI player has no valid Approach for Gold valuation.")

			# See whether we should multiply or divide
			if not numGoldFromValue:
				returnValue *= modifier
				returnValue /= 100
			else:
				returnValue *= 100
				returnValue /= modifier

			# Opinion also matters
			opinion = self.player.diplomacyAI.majorCivOpinion(otherPlayer)
			if opinion == MajorCivOpinionType.ally:
				modifier = 100
			elif opinion == MajorCivOpinionType.friend:
				modifier = 100
			elif opinion == MajorCivOpinionType.favorable:
				modifier = 100
			elif opinion == MajorCivOpinionType.neutral:
				modifier = 100
			elif opinion == MajorCivOpinionType.competitor:
				modifier = 115
			elif opinion == MajorCivOpinionType.enemy:
				modifier = 140
			elif opinion == MajorCivOpinionType.unforgivable:
				modifier = 200
			else:
				raise Exception("DEAL_AI: AI player has no valid Opinion for Gold valuation.")

			# See whether we should multiply or divide
			if not numGoldFromValue:
				returnValue *= modifier
				returnValue /= 100
			else:
				returnValue *= 100
				returnValue /= modifier

		# Sometimes we want to round up. Let's say an AI offers a deal to the human. We have to ensure that the
		# human can also offer that deal back and the AI will accept (and vice versa)
		if roundUp:
			returnValue += 99

		returnValue /= divisor

		# Are we trying to find the middle point between what we think this item is worth and what another player
		# thinks it's worth?
		if useEven:
			returnValue += otherPlayer.dealAI.goldForValueExchange(goldOrValue, numGoldFromValue, not fromMe, self.player, False, roundUp)
			returnValue /= 2

		return returnValue

	def resourceValue(self, resource: ResourceType, amount: int, duration: int, fromMe: bool, otherPlayer, simulation) -> int:
		"""How much is a Resource worth?"""
		if self.player == otherPlayer:
			raise Exception("DEAL_AI: Trying to check value of a Resource with oneself.")

		itemValue: int = 0

		usage = resource.usage()

		# Luxury Resource
		if usage == ResourceUsage.luxury:
			#if (GC.getGame().GetGameLeagues()->IsLuxuryHappinessBanned(self.player, resource))
			#	itemValue = 0
			#else
			happinessFromResource: int = resource.happiness()
			itemValue += (amount * happinessFromResource * duration * 2)  # Ex: 1 Silk for 4 Happiness * 30 turns * 2 = 240

			# If we only have 1 of a Luxury then we value it much more
			if fromMe:
				if self.player.numberOfAvailableResource(resource) == 1:
					itemValue *= 3
					if self.player.traits.luxuryHappinessRetention() > 0:
						itemValue /= 2
		# Strategic Resource
		elif usage == ResourceUsage.strategic:
			# tricksy humans trying to spoil us
			if not fromMe:
				# if we already have a big surplus of this resource
				numberOfCities: int = self.player.numberOfCities(simulation)
				if self.player.numberOfAvailableResource(resource) > numberOfCities:
					amount = 0
				else:
					amount = min(max(5, numberOfCities), amount)

			if not self.player.isResourceObsolete(resource):
				itemValue += (amount * duration * 150 / 100)  # Ex: 5 Iron for 30 turns * 2 = value of 300
			else:
				itemValue = 0

		# Increase value if it's from us, and we don't like the guy
		if fromMe:
			# Opinion also matters
			opinion: MajorCivOpinionType = self.player.diplomacyAI.majorCivOpinion(otherPlayer)
			if opinion == MajorCivOpinionType.ally:
				modifier = 100
			elif opinion == MajorCivOpinionType.friend:
				modifier = 100
			elif opinion == MajorCivOpinionType.favorable:
				modifier = 100
			elif opinion == MajorCivOpinionType.neutral:
				modifier = 100
			elif opinion == MajorCivOpinionType.competitor:
				modifier = 175
			elif opinion == MajorCivOpinionType.enemy:
				modifier = 400
			elif opinion == MajorCivOpinionType.unforgivable:
				modifier = 1000
			else:
				raise Exception("DEAL_AI: AI player has no valid Opinion for Resource valuation.")

			# Approach is important
			approach: MajorPlayerApproachType = self.player.diplomacyAI.GetMajorCivApproach(otherPlayer, hideTrueFeelings=True)
			if approach == MajorPlayerApproachType.hostile:
				modifier += 300
			elif approach == MajorPlayerApproachType.guarded:
				modifier += 150
			elif approach == MajorPlayerApproachType.afraid:
				modifier = 200  # Forced value
			elif approach == MajorPlayerApproachType.friendly:
				modifier = 200  # Forced value
			elif approach == MajorPlayerApproachType.neutral:
				modifier += 100
			else:
				raise Exception("DEAL_AI: AI player has no valid Approach for Resource valuation.")

			itemValue *= modifier
			itemValue /= 200  # 200 because we've added two mods together

		return itemValue

	def cityValue(self, point: HexPoint, fromMe, otherPlayer, useEven: bool, simulation) -> int:
		"""How much is a City worth?"""
		if self.player == otherPlayer:
			raise Exception("DEAL_AI: Trying to check value of City with oneself.")

		itemValue: int = 0
		city = simulation.cityAt(point)

		if city is not None:
			itemValue = 440 + (city.population() * 200)

			# add in the value of every plot this city owns (plus improvements and resources) okay, I'm only going to
			# count in the 3-rings plots since we can't actually use any others (I realize there may be a resource way
			# out there)
			goldPerPlot: int = self.player.buyPlotCost() # this is how much ANY plot is worth to me right now

			goldValueOfPlots: int = 0
			goldValueOfImprovedPlots: int = 0
			goldValueOfResourcePlots: int = 0
			for loopPoint in city.location.areaWithRadius(City.workRadius):
				loopPlot = simulation.tileAt(loopPoint)

				if loopPlot is None:
					continue

				if loopPlot.workingCity() is not None and loopPlot.workingCity() == city:
					if city.location.distance(loopPoint) > 1:
						goldValueOfPlots += goldPerPlot  # this is a bargain, but at least it's in the ballpark

					if loopPlot.improvement() != ImprovementType.none:
						goldValueOfImprovedPlots += goldPerPlot * 25

					resource = loopPlot.resourceFor(self.player)
					if resource != ResourceType.none and not self.player.isResourceObsolete(resource):
						usage = resource.usage()
						resourceQuantity = loopPlot.resourceQuantity()

						# Luxury Resource
						if usage == ResourceUsage.luxury:
							numTurns: int = min(1, simulation.maxTurn - simulation.currentTurn)
							numTurns = max(120,numTurns) # let's not go hog wild here
							happinessFromResource: int = resource.happiness()
							goldValueOfResourcePlots += (resourceQuantity * happinessFromResource * numTurns * 2)  # Ex: 1 Silk for 4 Happiness * 30 turns * 2 = 240
							# If we only have 1 of a Luxury then we value it much more
							if fromMe:
								if self.player.numberOfAvailableResource(resource) == 1:
									goldValueOfResourcePlots += (resourceQuantity * happinessFromResource * numTurns * 4)
						# Strategic Resource
						elif usage == ResourceUsage.strategic:
							numTurns: int = 60 # okay, this is a reasonable estimate
							goldValueOfResourcePlots += (resourceQuantity * numTurns * 150 / 100)

			goldValueOfImprovedPlots /= 100

			itemValue += goldValueOfPlots + goldValueOfImprovedPlots + goldValueOfResourcePlots

			# add in the (gold) value of the buildings (Or should we?  Will they transfer?)

			# From this player - add extra weight (don't want the human giving the AI a bit of gold for good cities)
			if fromMe:
				# Wonders are nice
				if city.hasActiveWorldWonder():
					itemValue *= 2

				# Adjust for how well a war against this player would go (or is going)
				warProjection: WarProjectionType = self.player.diplomacyAI.warProjectionAgainst(otherPlayer)
				if warProjection == WarProjectionType.destruction:
					itemValue *= 100
				elif warProjection == WarProjectionType.defeat:
					itemValue *= 180
				elif warProjection == WarProjectionType.stalemate:
					itemValue *= 220
				elif warProjection == WarProjectionType.unknown:
					itemValue *= 250
				elif warProjection == WarProjectionType.good:
					itemValue *= 400
				elif warProjection == WarProjectionType.veryGood:
					itemValue *= 400
				else:
					raise Exception("DEAL_AI: AI player has no valid War Projection for City valuation.")

				itemValue /= 100

				# AI players should be less willing to trade cities when not at war
				if not self.player.isAtWarWith(otherPlayer):
					itemValue *= 2
				# END fromMe
			else:
				if not self.player.isAtWarWith(otherPlayer):
					if otherPlayer.isHuman():  # he is obviously trying to trick us
						bestDistance: int = 99
						for loopCity in simulation.citiesOf(self.player):
							distFromThisCity = loopCity.location.distance(point)
							if distFromThisCity < bestDistance:
								bestDistance = distFromThisCity

						bestDistance = bestDistance if (bestDistance > 4) else 5
						itemValue /= bestDistance - 4
						itemValue = itemValue if (itemValue >= 100) else 100

			# slewis - Due to rule changes, value of major capitals should go up quite a bit because someone can win
			# the game by owning them
			if city.isOriginalMajorCapital():
				itemValue *= 2

		# Are we trying to find the middle point between what we think this item is worth and what another player
		# thinks it's worth?
		if useEven:
			itemValue += otherPlayer.dealAI.cityValue(point, not fromMe, self.player, useEven=False, simulation=simulation)
			itemValue /= 2

		return itemValue

	def doAddEmbassyToThem(self, deal: DiplomaticDeal, otherPlayer, dontChangeTheirExistingItems: bool, totalValue: int,
	                       amountOverWeWillRequest, useEvenValue: bool, simulation) -> int:
		"""See if adding Embassy to their side of the deal helps even out deal"""
		if self.player == otherPlayer:
			raise Exception("DEAL_AI: Trying to add Embassy to Them, but them is us.")

		if not dontChangeTheirExistingItems:
			if totalValue < 0:
				if not deal.isAllowEmbassyTrade(otherPlayer):
					# See if they can actually trade it to us
					if deal.isPossibleToTradeItem(otherPlayer, self.player, DiplomaticDealItemType.allowEmbassy, simulation=simulation):
						itemValue = self.tradeItemValue(DiplomaticDealItemType.allowEmbassy, False, otherPlayer, useEven=useEvenValue, simulation=simulation)

						# If adding this to the deal doesn't take it over the limit, do it
						if itemValue + totalValue <= amountOverWeWillRequest:
							deal.addAllowEmbassy(otherPlayer, simulation)
							totalValue, _, _ = self.dealValue(deal, useEvenValue, simulation)

		return totalValue

	def doAddEmbassyToUs(self, deal: DiplomaticDeal, otherPlayer, dontChangeMyExistingItems: bool, totalValue: bool,
	                     amountUnderWeWillOffer: int, useEvenValue: bool, simulation) -> int:
		"""See if adding Embassy to our side of the deal helps even out deal"""
		if self.player == otherPlayer:
			raise Exception("DEAL_AI: Trying to add Embassy to Us, but them is us.")

		if not dontChangeMyExistingItems:
			if totalValue > 0:
				if not deal.isAllowEmbassyTrade(self.player):
					# See if we can actually trade it to them
					if deal.isPossibleToTradeItem(self.player, otherPlayer, DiplomaticDealItemType.allowEmbassy, simulation=simulation):
						itemValue = self.tradeItemValue(DiplomaticDealItemType.allowEmbassy, True, otherPlayer, useEven=useEvenValue, simulation=simulation)

						# If adding this to the deal doesn't take it under the min limit, do it
						if -itemValue + totalValue >= amountUnderWeWillOffer:
							deal.addAllowEmbassy(self.player, simulation)
							totalValue, _, _ = self.dealValue(deal, useEvenValue, simulation)

		return totalValue

	def embassyValue(self, fromMe: bool, otherPlayer, useEven: bool) -> int:
		"""How much is an embassy worth?"""
		if self.player == otherPlayer:
			raise Exception("DEAL_AI: Trying to check value of a Embassy with oneself.")

		itemValue: int = 35

		if fromMe:  # giving the other player an embassy in my capital
			# Approach is important
			approach: MajorPlayerApproachType = self.player.diplomacyAI.majorCivApproachTowards(otherPlayer, hideTrueFeelings=True)
			if approach == MajorPlayerApproachType.hostile:  # MAJOR_CIV_APPROACH_HOSTILE
				itemValue *= 250
			elif approach == MajorPlayerApproachType.guarded:  # MAJOR_CIV_APPROACH_GUARDED:
				itemValue *= 130
			elif approach == MajorPlayerApproachType.afraid:  # MAJOR_CIV_APPROACH_AFRAID:
				itemValue *= 80
			elif approach == MajorPlayerApproachType.friendly:  # MAJOR_CIV_APPROACH_FRIENDLY:
				itemValue *= 100
			elif approach == MajorPlayerApproachType.neutral:  # MAJOR_CIV_APPROACH_NEUTRAL:
				itemValue *= 100
			else:
				raise Exception("DEAL_AI: AI player has no valid Approach for Research Agreement valuation.")

			itemValue /= 100

		# Are we trying to find the middle point between what we think this item is worth and what another player
		# thinks it's worth?
		if useEven:
			itemValue += otherPlayer.dealAI.embassyValue(not fromMe, self.player, useEven=False)
			itemValue /= 2

		return itemValue

	def openBordersValue(self, fromMe: bool, otherPlayer, useEven: bool, simulation) -> int:
		"""How much in V-POINTS (aka value) is Open Borders worth?  You gotta admit that V-POINTS sound pretty cool though"""
		if self.player == otherPlayer:
			raise Exception("DEAL_AI: Trying to check value of Open Borders with oneself.")

		approach: MajorPlayerApproachType = self.player.diplomacyAI.majorCivApproachTowards(otherPlayer, hideTrueFeelings=True)

		# If we're friends, then OB is always equally valuable to both parties
		if approach == MajorPlayerApproachType.friendly:
			return 50

		# Me giving Open Borders to the other guy
		if fromMe:
			# Approach is important
			if approach == MajorPlayerApproachType.hostile:  # MAJOR_CIV_APPROACH_HOSTILE:
				itemValue = 1000
			elif approach == MajorPlayerApproachType.guarded:  # MAJOR_CIV_APPROACH_GUARDED:
				itemValue = 100
			elif approach == MajorPlayerApproachType.afraid:  # MAJOR_CIV_APPROACH_AFRAID:
				itemValue = 20
			elif approach == MajorPlayerApproachType.friendly:  # MAJOR_CIV_APPROACH_FRIENDLY:
				itemValue = 50
			elif approach == MajorPlayerApproachType.neutral:  # MAJOR_CIV_APPROACH_NEUTRAL:
				itemValue = 75
			else:
				raise Exception("DEAL_AI: AI player has no valid Approach for Open Borders valuation.")

			# Opinion also matters
			opinion: MajorCivOpinionType = self.player.diplomacyAI.majorCivOpinion(otherPlayer)
			if opinion == MajorCivOpinionType.ally:  # MAJOR_CIV_OPINION_ALLY
				itemValue = 0
			elif opinion == MajorCivOpinionType.friend:  # MAJOR_CIV_OPINION_FRIEND:
				itemValue *= 35
				itemValue /= 100
			elif opinion == MajorCivOpinionType.favorable:  # MAJOR_CIV_OPINION_FAVORABLE:
				itemValue *= 70
				itemValue /= 100
			elif opinion == MajorCivOpinionType.neutral:  # MAJOR_CIV_OPINION_NEUTRAL:
				pass
			elif opinion == MajorCivOpinionType.competitor:  # MAJOR_CIV_OPINION_COMPETITOR:
				itemValue *= 150
				itemValue /= 100
			elif opinion == MajorCivOpinionType.enemy:  # MAJOR_CIV_OPINION_ENEMY:
				itemValue *= 400
				itemValue /= 100
			elif opinion == MajorCivOpinionType.unforgivable:  # MAJOR_CIV_OPINION_UNFORGIVABLE:
				itemValue = 10000
			else:
				raise Exception("DEAL_AI: AI player has no valid Opinion for Open Borders valuation.")

			# If they're at war with our enemies then we're more likely to give them OB
			numEnemiesAtWarWith = self.player.diplomacyAI.numOurEnemiesPlayerAtWarWith(otherPlayer)
			if numEnemiesAtWarWith >= 2:
				itemValue *= 10
				itemValue /= 100
			elif numEnemiesAtWarWith == 1:
				itemValue *= 25
				itemValue /= 100

			# Do we think he's going for culture victory?
			if self.player.grandStrategyAI.guessOtherPlayerActiveGrandStrategyOf(otherPlayer) == GrandStrategyAIType.culture:
				# If he has tourism, and he's not influential on us yet, resist!
				if otherPlayer.tourism.currentTourism(simulation) > 0 and otherPlayer.tourism.influenceOn(self.player) < InfluenceLevelType.influential:
					itemValue *= 500
					itemValue /= 100
		# Other guy giving me Open Borders
		else:
			# Proximity is very important
			proximity: PlayerProximityType = self.player.proximityToPlayer(otherPlayer)
			if proximity == PlayerProximityType.distant:  # PLAYER_PROXIMITY_DISTANT
				itemValue = 5
			elif proximity == PlayerProximityType.far:  # PLAYER_PROXIMITY_FAR
				itemValue = 10
			elif proximity == PlayerProximityType.close:  # PLAYER_PROXIMITY_CLOSE
				itemValue = 15
			elif proximity == PlayerProximityType.neighbors:  # PLAYER_PROXIMITY_NEIGHBORS
				itemValue = 30
			else:
				raise Exception("DEAL_AI: AI player has no valid Proximity for Open Borders valuation.")

			# Reduce value by half if the other guy only has a single City
			if otherPlayer.numberOfCities(simulation) == 1:
				itemValue *= 50
				itemValue /= 100

			# Boost value greatly if we are going for a culture win
			# If going for culture win always want open borders against civs we need influence on
			if self.player.grandStrategyAI.activeStrategy == GrandStrategyAIType.culture and otherPlayer.tourism.currentTourism(simulation) > 0:
				# The civ we need influence on the most should ALWAYS be included
				if self.player.tourism.civLowestInfluence(checkOpenBorders=False) == otherPlayer:
					itemValue *= 1000
					itemValue /= 100

				# If have influence over half the civs, want OB with the other half
				# elif (self.player.GetCulture()->GetNumCivsToBeInfluentialOn() <= self.player.GetCulture()->GetNumCivsInfluentialOn())
				# 	if (self.player.GetCulture()->GetInfluenceLevel(otherPlayer.) < INFLUENCE_LEVEL_INFLUENTIAL):
				# 		itemValue *= 500
				# 		itemValue /= 100
				# fixme

				elif proximity == PlayerProximityType.neighbors:
					# If we're cramped then we want OB more with our neighbors
					if self.player.isCramped():
						itemValue *= 300
						itemValue /= 100

		# Are we trying to find the middle point between what we think this item is worth and what another player
		# thinks it's worth?
		if useEven:
			itemValue += otherPlayer.dealAI.openBordersValue(not fromMe, self.player, useEven=False, simulation=simulation)
			itemValue /= 2

		return itemValue

	def defensivePactValue(self, fromMe: bool, otherPlayer, useEven: bool) -> int:
		"""How much is a Defensive Pact worth?"""
		if self.player == otherPlayer:
			raise Exception("DEAL_AI: Trying to check value of a Defensive Pact with oneself.")

		# What is a Defensive Pact with otherPlayer worth to US?
		if not fromMe:
			itemValue = 100
		# How much do we value giving away a Defensive Pact?
		else:
			# Opinion also matters
			opinion: MajorCivOpinionType = self.player.diplomacyAI.majorCivOpinion(otherPlayer)
			if opinion == MajorCivOpinionType.ally:  # MAJOR_CIV_OPINION_ALLY:
				itemValue = 100
			elif opinion == MajorCivOpinionType.friend:  # MAJOR_CIV_OPINION_FRIEND:
				itemValue = 100
			elif opinion == MajorCivOpinionType.favorable:  # MAJOR_CIV_OPINION_FAVORABLE:
				itemValue = 100
			elif opinion == MajorCivOpinionType.neutral:  # MAJOR_CIV_OPINION_NEUTRAL:
				itemValue = 100000
			elif opinion == MajorCivOpinionType.competitor:  # MAJOR_CIV_OPINION_COMPETITOR:
				itemValue = 100000
			elif opinion == MajorCivOpinionType.enemy:  # MAJOR_CIV_OPINION_ENEMY:
				itemValue = 100000
			elif opinion == MajorCivOpinionType.unforgivable:  # MAJOR_CIV_OPINION_UNFORGIVABLE:
				itemValue = 100000
			else:
				raise Exception("DEAL_AI: AI player has no valid Opinion for Defensive Pact valuation.")

		# Are we trying to find the middle point between what we think this item is worth and what another player
		# thinks it's worth?
		if useEven:
			itemValue += otherPlayer.dealAI.defensivePactValue(not fromMe, self.player, useEven=False)
			itemValue /= 2

		return itemValue

	def researchAgreementValue(self, fromMe: bool, otherPlayer, useEven: bool) -> int:
		"""How much is a Research Agreement worth?"""
		if self.player == otherPlayer:
			raise Exception("DEAL_AI: Trying to check value of a Research Agreement with oneself.")

		itemValue: int = 100

		if fromMe:
			# if they are ahead of me in tech by one or more eras ratchet up the value since they are more likely to
			# get a good tech than I am
			myEra: EraType = self.player.currentEra()
			theirEra: EraType = otherPlayer.currentEra()

			additionalValue = itemValue * max(0, (theirEra.value() - myEra.value()))
			itemValue += additionalValue

			# Approach is important
			approach: MajorPlayerApproachType = self.player.diplomacyAI.majorCivApproachTowards(otherPlayer, hideTrueFeelings=True)
			if approach == MajorPlayerApproachType.hostile:  # MAJOR_CIV_APPROACH_HOSTILE:
				itemValue *= 1000
			elif approach == MajorPlayerApproachType.guarded:  # MAJOR_CIV_APPROACH_GUARDED:
				itemValue *= 100
			elif approach == MajorPlayerApproachType.afraid:  # MAJOR_CIV_APPROACH_AFRAID:
				itemValue *= 80
			elif approach == MajorPlayerApproachType.friendly:  # MAJOR_CIV_APPROACH_FRIENDLY:
				itemValue *= 100
			elif approach == MajorPlayerApproachType.neutral:  # MAJOR_CIV_APPROACH_NEUTRAL:
				itemValue *= 100
			else:
				raise Exception("DEAL_AI: AI player has no valid Approach for Research Agreement valuation.")

			itemValue /= 100

		# Are we trying to find the middle point between what we think this item is worth and what another player
		# thinks it's worth?
		if useEven:
			itemValue += otherPlayer.dealAI.researchAgreementValue(not fromMe, self.player, useEven=False)
			itemValue /= 2

		return itemValue

	def peaceTreatyValue(self, otherPlayer) -> int:
		"""How much is a Peace Treaty worth?"""
		if self.player == otherPlayer:
			raise Exception("DEAL_AI: Trying to check value of a Peace Treaty with oneself.")
		
		return 0

	def thirdPartyPeaceValue(self, fromMe: bool, otherPlayer, thirdPlayer, simulation) -> int:
		"""What is the value of peace with eWithTeam? NOTE: This deal item should be disabled if eWithTeam doesn't
		want to go to peace"""
		if self.player == otherPlayer:
			raise Exception("DEAL_AI: Trying to check value of a Third Party Peace with oneself.")

		itemValue: int = 0
		ownDiplomacyAI = self.player.diplomacyAI
		withPlayer = None

		# find the first player associated with the team
		for loopPlayer in simulation.players:
			if not loopPlayer.isMajorAI() and not loopPlayer.isHuman():
				continue

			if not ownDiplomacyAI.isValid(loopPlayer):
				continue

			if loopPlayer == thirdPlayer or loopPlayer.isAlliedWith(thirdPlayer):
				withPlayer = loopPlayer
				break

			pass

		if withPlayer is None:
			return 0

		warProjection: WarProjectionType = ownDiplomacyAI.warProjectionAgainst(withPlayer)
		ourEra: EraType = self.player.currentEra()

		opinionTowardsAskingPlayer: MajorCivOpinionType = ownDiplomacyAI.majorCivOpinion(otherPlayer)
		opinionTowardsWarPlayer: MajorCivOpinionType = MajorCivOpinionType.none

		minor: bool = False

		# Minor
		if withPlayer.isCityState():
			# if we're at war with the opponent, then this must be a peace deal. In this case we should evaluate minor
			# civ peace deals as zero
			if self.player.isAtWarWith(otherPlayer):
				minorAlly = withPlayer.minorCivAI.ally()
				# if they are allied with the city state or we are allied with the city state
				if minorAlly == otherPlayer or minorAlly == self.player:
					return 0

			minor = True
		# Major
		else:
			opinionTowardsWarPlayer = ownDiplomacyAI.majorCivOpinion(withPlayer)

		# From me
		if fromMe:
			if warProjection == WarProjectionType.veryGood:  # WAR_PROJECTION_VERY_GOOD
				itemValue = 600
			elif warProjection == WarProjectionType.good:  # WAR_PROJECTION_GOOD
				itemValue = 400
			elif warProjection == WarProjectionType.unknown:  # WAR_PROJECTION_UNKNOWN
				itemValue = 250
			else:
				itemValue = 200

			# Add 50 gold per era
			extraCost = ourEra.value() * 50
			itemValue += extraCost

			# Minors
			if minor:
				pass
			# Majors
			else:
				# Modify for our feelings towards the player we're at war with
				if opinionTowardsWarPlayer == MajorCivOpinionType.unforgivable:
					itemValue *= 300
					itemValue /= 100
				elif opinionTowardsWarPlayer == MajorCivOpinionType.enemy:
					itemValue *= 200
					itemValue /= 100
			# Modify for our feelings towards the asking player
			if opinionTowardsAskingPlayer == MajorCivOpinionType.ally:
				itemValue *= 30
				itemValue /= 100
			elif opinionTowardsAskingPlayer == MajorCivOpinionType.friend:
				itemValue *= 50
				itemValue /= 100
			elif opinionTowardsAskingPlayer == MajorCivOpinionType.favorable:
				itemValue *= 75
				itemValue /= 100
		# From them
		else:
			itemValue = -10000

		return itemValue

	def thirdPartyWarValue(self, fromMe: bool, otherPlayer, thirdPlayer, simulation) -> int:
		"""What is the value of war with withPlayer?"""
		if self.player == otherPlayer:
			raise Exception("DEAL_AI: Trying to check value of a Third Party War with oneself.")
		
		itemValue: int = 0
		ownDiplomacyAI = self.player.diplomacyAI

		# How much does this AI like to go to war? If it's a 3 or less, never accept
		warApproachWeight = ownDiplomacyAI.playerDict.personalityMajorCivApproachBias(MajorPlayerApproachType.war)
		if fromMe and warApproachWeight < 4:
			return 100000

		withPlayer = None

		# find the first player associated with the team
		for loopPlayer in simulation.players:
			if not loopPlayer.isMajorAI() and not loopPlayer.isHuman():
				continue

			if not ownDiplomacyAI.isValid(loopPlayer):
				continue

			if loopPlayer == thirdPlayer or loopPlayer.isAlliedWith(thirdPlayer):
				withPlayer = loopPlayer
				break

			pass

		warProjection: WarProjectionType = ownDiplomacyAI.warProjection(withPlayer)
	
		ourEra: EraType = self.player.currentEra()
	
		opinionTowardsAskingPlayer: MajorCivOpinionType = ownDiplomacyAI.majorCivOpinion(otherPlayer)
		opinionTowardsWarPlayer: MajorCivOpinionType = MajorCivOpinionType.none
		minorApproachTowardsWarPlayer: MinorPlayerApproachType = MinorPlayerApproachType.none
	
		minor: bool = False
	
		# Minor
		if withPlayer.isCityState():
			bMinor = True
			minorApproachTowardsWarPlayer = ownDiplomacyAI.GetMinorCivApproach(withPlayer)
		# Major
		else:
			opinionTowardsWarPlayer = ownDiplomacyAI.GetMajorCivOpinion(withPlayer)
	
		# From me
		if fromMe:
			if warProjection >= WarProjectionType.good:
				itemValue = 400
			elif warProjection == WarProjectionType.unknown:
				itemValue = 600
			elif warProjection == WarProjectionType.stalemate:
				itemValue = 1000
			else:
				itemValue = 50000
	
			# Add 50 gold per era
			extraCost: int = ourEra.value() * 50
			itemValue += extraCost
	
			# Modify based on our War Approach
			warBias = 5 - warApproachWeight  # DEFAULT_FLAVOR_VALUE
			warMod = warBias * 10	# EX: 5 - War Approach of 9 = -4 * 10 = -40% cost
			warMod *= itemValue
			warMod /= 100
	
			itemValue += warMod
	
			# Minor
			if minor:
				if minorApproachTowardsWarPlayer == MinorPlayerApproachType.friendly:
					itemValue = 100000
				elif minorApproachTowardsWarPlayer == MinorPlayerApproachType.protective:
					itemValue = 100000
			# Major
			else:
				# Modify for our feelings towards the player we're would go to war with
				if opinionTowardsWarPlayer == MajorCivOpinionType.unforgivable:
					itemValue *= 25
					itemValue /= 100
				elif opinionTowardsWarPlayer == MajorCivOpinionType.enemy:
					itemValue *= 50
					itemValue /= 100
				elif opinionTowardsWarPlayer == MajorCivOpinionType.competitor:
					itemValue *= 75
					itemValue /= 100
	
			# Modify for our feelings towards the asking player
			if opinionTowardsAskingPlayer == MajorCivOpinionType.ally:
				itemValue *= 50
				itemValue /= 100
			elif opinionTowardsAskingPlayer == MajorCivOpinionType.friend:
				itemValue *= 75
				itemValue /= 100
			elif opinionTowardsAskingPlayer == MajorCivOpinionType.favorable:
				itemValue *= 85
				itemValue /= 100
			elif opinionTowardsAskingPlayer == MajorCivOpinionType.competitor:
				itemValue *= 125
				itemValue /= 100
		# From them
		else:
			# Minor
			if minor:
				itemValue = -100000
			# Major
			else:
				# Modify for our feelings towards the player they would go to war with
				if opinionTowardsWarPlayer == MajorCivOpinionType.unforgivable:
					itemValue = 200
				elif opinionTowardsWarPlayer == MajorCivOpinionType.enemy:
					itemValue = 100
				else:
					itemValue = -100000
	
		return itemValue

	def voteCommitmentValue(self, fromMe: bool, otherPlayer, useEven: bool) -> int:
		"""What is the value of trading a vote commitment?"""
		if self.player == otherPlayer:
			raise Exception("DEAL_AI: Trying to check value of a Third Party War with oneself.")
		
		# fixme
		
		return 0

	def doAddCitiesToUs(self, deal, otherPlayer, dontChangeMyExistingItems, totalValue: int, amountUnderWeWillOffer, useEvenValue, simulation):
		"""See if adding Cities to our side of the deal helps even out deal"""
		if self.player == otherPlayer:
			raise Exception("DEAL_AI: Trying to add Open Borders to Us, but them is us.")

		surrenderingPlayer = deal.surrenderingPlayer()

		# If we're not the one surrendering here, don't bother
		if surrenderingPlayer is not None and surrenderingPlayer != self.player:
			return
	
		# Don't change things
		if dontChangeMyExistingItems:
			return
	
		# We don't owe them anything
		if totalValue <= 0:
			return
	
		losingPlayer = self.player
		winningPlayer = otherPlayer
	
		# If the player only has 1 City then we can't get any more from him
		if losingPlayer.numberOfCities(simulation) == 1:
			return
	
		# int iCityValue = 0
	
		cityDistanceFromWinnersCapital: int = 0
		winnerCapitalLocation: HexPoint = invalidHexPoint
	
		# If winner has no capital then we can't use proximity - it will stay at 0
		winnerCapital = winningPlayer.capitalCity(simulation)
		if winnerCapital is not None:
			winnerCapitalLocation = winnerCapital.location
	
		# Create vector of the losing players' Cities so we can see which are the closest to the winner
		viCityProximities = WeightedBaseList()

		# cities
		losingPlayerCities = simulation.citiesOf(losingPlayer)
	
		# Loop through all the loser's Cities
		for loopCity in losingPlayerCities:
			# Get total city value of the loser
			# iCityValue += self.cityValue(pLoopCity->getX(), pLoopCity->getY(), /*bFromMe*/ True, eThem, bUseEvenValue)
			# iCityValue += self.cityValue(pLoopCity->getX(), pLoopCity->getY(), /*bFromMe*/ True, eThem, /*bUseEvenValue*/ True)
	
			# If winner has no capital, Distance defaults to 0
			if winnerCapital is not None:
				cityDistanceFromWinnersCapital = winnerCapitalLocation.distance(loopCity.location)
	
			# Don't include the capital in the list of Cities the winner can receive
			if not loopCity.isCapital():
				viCityProximities.addWeight(cityDistanceFromWinnersCapital, hash(loopCity))
	
		# Sort the vector based on distance from winner's capital
		viCityProximities.sortByValue(reverse=True)
	
		# Loop through sorted Cities and add them to the deal if they're under the amount to give up - start from the
		# back of the list, because that's where the CLOSEST cities are
		for cityHash in viCityProximities.keys():
			loopCity = firstOrNone(list(filter(lambda city: hash(city) == cityHash, losingPlayerCities)))
			# iCityValue = self.cityValue(pLoopCity->getX(), pLoopCity->getY(), meSurrendering, otherPlayer, /*bUseEvenValue*/ True)
	
			# See if we can actually trade it to them
			if deal.isPossibleToTradeItem(self.player, otherPlayer, DiplomaticDealItemType.cities, loopCity.location, simulation=simulation):
				# if (deal.isPossibleToTradeItem(self.player, eThem, DiplomaticDealItemType.OPEN_BORDERS))
				itemValue = self.cityValue(loopCity, True, otherPlayer, useEvenValue, simulation)
				# int iItemValue = GetTradeItemValue(DiplomaticDealItemType.CITIES, /*bFromMe*/ True, eThem, pLoopCity->getX(), pLoopCity->getY(), iDealDuration, bUseEvenValue)
				# int iItemValue = GetTradeItemValue(DiplomaticDealItemType.OPEN_BORDERS, /*bFromMe*/ True, eThem, -1, -1, iDealDuration, bUseEvenValue)
	
				# If adding this to the deal doesn't take it under the min limit, do it
				if -itemValue + totalValue >= amountUnderWeWillOffer:
					# deal.AddOpenBorders(self.player, iDealDuration)
					deal.addCityTrade(self.player, loopCity.location, simulation)
					totalValue, _, _ = self.dealValue(deal, useEvenValue, simulation)

		return totalValue

	def doAddItemsToDealForPeaceTreaty(self, otherPlayer, deal: DiplomaticDeal, treaty: PeaceTreatyType, meSurrendering: bool,
	                                   simulation):
		"""Add appropriate items to pDeal based on what type of PeaceTreaty eTreaty is"""
		percentGoldToGive: int = 0
		percentGoldPerTurnToGive: int = 0
		giveOpenBorders: bool = False
		giveOnlyOneCity: bool = False
		percentCitiesGiveUp: int = 0  # 100 = all but capital
		giveUpStratResources: bool = False
		giveUpLuxuryResources: bool = False

		# Setup what needs to be given up based on the level of the treaty
		if treaty == PeaceTreatyType.whitePeace:  #  PEACE_TREATY_WHITE_PEACE:
			# White Peace: nothing changes hands
			pass
		elif treaty == PeaceTreatyType.armistice:  # PEACE_TREATY_ARMISTICE:
			percentGoldToGive = 50
			percentGoldPerTurnToGive = 50
		elif treaty == PeaceTreatyType.settlement:  # PEACE_TREATY_SETTLEMENT:
			percentGoldToGive = 100
			percentGoldPerTurnToGive = 100
		elif treaty == PeaceTreatyType.backDown:  # PEACE_TREATY_BACKDOWN:
			percentGoldToGive = 100
			percentGoldPerTurnToGive = 100
			giveOpenBorders = True
			giveUpStratResources = True
		elif treaty == PeaceTreatyType.submission:  # PEACE_TREATY_SUBMISSION:
			percentGoldToGive = 100
			percentGoldPerTurnToGive = 100
			giveOpenBorders = True
			giveUpStratResources = True
			giveUpLuxuryResources = True
		elif treaty == PeaceTreatyType.surrender:  # PEACE_TREATY_SURRENDER:
			giveOnlyOneCity = True
		elif treaty == PeaceTreatyType.cession:  # PEACE_TREATY_CESSION:
			percentCitiesGiveUp = 25
			percentGoldToGive = 50
		elif treaty == PeaceTreatyType.capitulation:  # PEACE_TREATY_CAPITULATION:
			percentCitiesGiveUp = 33
			percentGoldToGive = 100
		elif treaty == PeaceTreatyType.unconditionalSurrender:  # PEACE_TREATY_UNCONDITIONAL_SURRENDER:
			percentCitiesGiveUp = 100
			percentGoldToGive = 100

		duration = 30  # GC.getGame().GetDealDuration()

		losingPlayer = self.player if meSurrendering else otherPlayer
		winningPlayer = otherPlayer if meSurrendering else self.player

		self.doAddPlayersAlliesToTreaty(otherPlayer, deal, simulation)

		# Gold
		if percentGoldToGive > 0:
			goldValue: int = deal.goldAvailable(losingPlayer, DiplomaticDealItemType.gold, simulation)
			if goldValue > 0:
				goldValue = int(goldValue * percentGoldToGive / 100)

				if deal.isPossibleToTradeItem(losingPlayer, winningPlayer, DiplomaticDealItemType.gold, amount=goldValue, simulation=simulation):
					deal.addGoldTradeFrom(losingPlayer, goldValue, simulation)

		# Gold per turn
		if percentGoldPerTurnToGive > 0:
			goldPerTurnValue: int = min(losingPlayer.calculateGoldRate(), winningPlayer.treasury.calculateGrossGold(simulation) / 3)  # ARMISTICE_GPT_DIVISOR
			if goldPerTurnValue > 0:
				goldPerTurnValue = int(goldPerTurnValue * percentGoldPerTurnToGive / 100)

				if goldPerTurnValue > 0 and deal.isPossibleToTradeItem(losingPlayer, winningPlayer, DiplomaticDealItemType.goldPerTurn, amount=goldPerTurnValue, simulation=simulation):
					deal.addGoldPerTurnTradeFrom(losingPlayer, goldPerTurnValue, duration, simulation)

		# Open Borders
		if giveOpenBorders:
			if deal.isPossibleToTradeItem(losingPlayer, winningPlayer, DiplomaticDealItemType.openBorders):
				deal.addOpenBorders(losingPlayer, duration, simulation)

		# Resources
		for loopResource in list(ResourceType):
			usage: ResourceUsage = loopResource.usage()

			# Can't trade bonus Resources
			if usage == ResourceUsage.bonus:
				continue

			iResourceQuantity = losingPlayer.getNumResourceAvailable(loopResource, False)

			# Don't bother looking at this Resource if the other player doesn't even have any of it
			if iResourceQuantity == 0:
				continue

			# Match with deal type
			if usage == ResourceUsage.luxury and not giveUpLuxuryResources:
				continue

			if usage == ResourceUsage.strategic and not giveUpStratResources:
				continue

			# Can only get 1 copy of a Luxury
			if usage == ResourceUsage.luxury:
				iResourceQuantity = 1

			if deal.isPossibleToTradeItem(losingPlayer, winningPlayer, DiplomaticDealItemType.resources, loopResource, iResourceQuantity):
				deal.addResourceTrade(losingPlayer, resource=loopResource, amount=iResourceQuantity, duration=duration, simulation=simulation)

		# Give up all but capital?
		if percentCitiesGiveUp == 100:
			# All Cities but the capital
			for loopCity in simulation.citiesOf(losingPlayer):
				if loopCity.isCapital():
					continue

				if deal.isPossibleToTradeItem(losingPlayer, winningPlayer, DiplomaticDealItemType.cities, point=loopCity.location, simulation=simulation):
					deal.addCityTradeFrom(losingPlayer, loopCity.location, simulation)

		# If the player only has 1 City then we can't get any more from him
		elif percentCitiesGiveUp > 0 or giveOnlyOneCity and losingPlayer.numberOfCities(simulation) > 1:
			cityValue: int = 0
			cityDistanceFromWinnersCapital: int = 0
			winnerCapitalLocation: HexPoint = invalidHexPoint

			# If winner has no capital then we can't use proximity - it will stay at 0
			winnerCapital = winningPlayer.capitalCity(simulation)
			if winnerCapital is not None:
				winnerCapitalLocation = winnerCapital.location

			# Create vector of the losing players' Cities so we can see which are the closest to the winner
			viCityProximities = WeightedBaseList()

			# cities
			losingPlayerCities = simulation.citiesOf(losingPlayer)

			# Loop through all the loser's Cities
			for loopCity in losingPlayerCities:
				# Get total city value of the loser
				cityValue += self.cityValue(loopCity.location, meSurrendering, otherPlayer, useEven=True, simulation=simulation)

				# If winner has no capital, Distance defaults to 0
				if winnerCapital is not None:
					cityDistanceFromWinnersCapital = winnerCapitalLocation.distance(loopCity.location)

				# Divide the distance by three if the city was originally owned by the winning player to make these cities more likely
				if loopCity.originalLeader() == winningPlayer.leader:
					cityDistanceFromWinnersCapital /= 3

				# Don't include the capital in the list of Cities the winner can receive
				if not loopCity.isCapital():
					viCityProximities.addWeight(cityDistanceFromWinnersCapital, hash(loopCity))

			# Sort the vector based on distance from winner's capital
			viCityProximities.sortByValue(reverse=True)

			# Just one city?
			if giveOnlyOneCity:
				firstCityHash = firstOrNone(viCityProximities.keys())
				loopCity = firstOrNone(list(filter(lambda city: hash(city) == firstCityHash, losingPlayerCities)))
				deal.addCityTradeFrom(losingPlayer, loopCity.location, simulation)
			else:
				# Determine the value of Cities to be given up
				cityValueToSurrender: int = int(cityValue * percentCitiesGiveUp / 100)

				# Loop through sorted Cities and add them to the deal if they're under the amount to give up - start
				# from the back of the list, because that's where the CLOSEST cities are
				for cityHash in viCityProximities.keys():
					loopCity = firstOrNone(list(filter(lambda city: hash(city) == cityHash, losingPlayerCities)))

					cityValue = self.cityValue(loopCity.location, meSurrendering, otherPlayer, useEven=True, simulation=simulation)

					# City is worth less than what is left to be added to the deal, so add it
					if cityValue < cityValueToSurrender:
						if deal.isPossibleToTradeItem(losingPlayer, winningPlayer, DiplomaticDealItemType.cities, point=loopCity, simulation=simulation):
							deal.addCityTradeFrom(losingPlayer, loopCity.location, simulation)
							cityValueToSurrender -= cityValue

		return
