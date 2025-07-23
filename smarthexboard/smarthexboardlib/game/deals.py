import logging
from typing import Optional, List

from smarthexboard.smarthexboardlib.game.ai.diplomaticTypes import DiplomaticDeal, DiplomaticDealItemType, DiplomaticDealType, DiplomaticDealItem
from smarthexboard.smarthexboardlib.game.notifications import NotificationType
from smarthexboard.smarthexboardlib.map.types import ResourceType
from gettext import gettext as _


class GameDeals:
	def __init__(self):
		self.dealCounter = 0

		self.proposedDeals: List[DiplomaticDeal] = []
		self.currentDeals: List[DiplomaticDeal] = []
		self.historicalDeals: List[DiplomaticDeal] = []

	def doTurn(self, simulation):
		"""Update deals for the start of a new turn"""
		if len(self.currentDeals) > 0:
			fromPlayer = None
			toPlayer = None
			somethingChanged: bool = False

			gameTurn = simulation.currentTurn

			# Check to see if any of our TradeItems in any of our Deals expire this turn
			for it in self.currentDeals:
				for itemIter in it.tradeItems:
					finalTurn = itemIter.finalTurn

					if finalTurn > -1 and finalTurn == gameTurn:
						somethingChanged = True

						fromPlayer = itemIter.fromPlayer
						toPlayer = it.otherPlayerOf(fromPlayer)

						self.doEndTradedItem(itemIter, fromPlayer, toPlayer, False, simulation)

			# check to see if one of our deals in no longer valid
			for it in self.currentDeals:
				invalidDeal: bool = False
				unbreakable: bool = False
				for itemIter in it.tradeItems:
					finalTurn = itemIter.finalTurn
					if finalTurn > -1 and finalTurn != gameTurn:  # if this was the last turn the deal was ending anyways
						fromPlayer = itemIter.fromPlayer
						# check to see if we are negative on resource or gold
						haveEnoughGold = True
						haveEnoughResource = True
						if itemIter.itemType == DiplomaticDealItemType.resources:
							resource: ResourceType = itemIter.resource
							haveEnoughResource = fromPlayer.numberOfAvailableResource(resource) >= 0
						elif itemIter.itemType == DiplomaticDealItemType.peaceTreaty:
							unbreakable = True
							break

						if not haveEnoughGold or not haveEnoughResource:
							invalidDeal = True

				if not unbreakable and invalidDeal:
					somethingChanged = True
					it.finalTurn = gameTurn
					it.dealCancelled = True

					for itemIter in it.tradeItems:
						# Cancel individual items
						itemIter.finalTurn = simulation.currentTurn

						fromPlayer = itemIter.fromPlayer
						toPlayer = it.otherPlayerOf(fromPlayer)

						self.doEndTradedItem(itemIter, fromPlayer, toPlayer, True, simulation)

			if somethingChanged:
				# Update UI if we were involved in the deal
				activePlayer = simulation.activePlayer()
				if activePlayer is not None:
					if fromPlayer == activePlayer or toPlayer == activePlayer:
						simulation.userInterface.updateGameData()

			self.doUpdateCurrentDealsList(simulation)

		return

	def doUpdateCurrentDealsList(self, simulation):
		"""If a deal has actually ended, move it from the current list to the historic list"""
		# Copy the deals into a temporary container
		tempDeals = []
		for it in self.currentDeals:
			tempDeals.append(it)

		# Copy them to either current or historical deals based on whether they are still active
		self.currentDeals = []
		for it in tempDeals:
			if it.finalTurn <= simulation.currentTurn:
				self.historicalDeals.append(it)
			else:
				self.currentDeals.append(it)

	def addProposedDeal(self, deal: DiplomaticDeal, simulation):
		# Store Deal away
		self.proposedDeals.append(deal)

		# Update UI if we were involved in the deal
		activePlayer = simulation.activePlayer()
		if activePlayer is not None:
			if deal.fromPlayer == activePlayer or deal.toPlayer == activePlayer:
				simulation.userInterface.updateGameData()

		return

	def finalizeDeal(self, fromPlayer, toPlayer, accepted: bool, simulation) -> bool:
		"""Moves a deal from the proposed list to the active one (returns FALSE if deal not found)"""
		deal: Optional[DiplomaticDeal] = None
		foundId: bool = False
		valid: bool = True

		# Find the deal in the list of proposed deals
		for loopDeal in self.proposedDeals:
			if loopDeal.fromPlayer == fromPlayer and loopDeal.toPlayer == toPlayer:
				deal = loopDeal
				foundId = True

		veNowAtPeacePairs = []

		if foundId:
			for tradeItem in deal.tradeItems:
				if tradeItem.toRenewed:
					continue

				# iter.Data1, iter.Data2, iter.Data3, iter->m_bFlag1, false, True)
				fromPlayer = deal.fromPlayerFor(tradeItem)
				toPlayer = deal.toPlayerFor(tradeItem)
				if not deal.isPossibleToTradeItem(fromPlayer, toPlayer, tradeItem.itemType, tradeItem.amount, simulation=simulation):
					# mark that the deal is no longer valid. We will still delete the deal but not commit its actions
					valid = False
					break

			self.proposedDeals = list(filter(lambda p: p.fromPlayer != fromPlayer or p.toPlayer != toPlayer, self.proposedDeals))

			if valid and accepted:
				# Determine total duration of the Deal
				latestItemLastTurn: int = 0
				longestDuration: int = 0

				for tradeItem in deal.tradeItems:
					# Calculate duration
					if tradeItem.duration > 0:
						tradeItem.finalTurn = tradeItem.duration + simulation.currentTurn
						if tradeItem.duration > longestDuration:
							longestDuration = tradeItem.duration
							latestItemLastTurn = tradeItem.finalTurn

				deal.duration = longestDuration
				deal.finalTurn = latestItemLastTurn
				deal.startTurn = simulation.currentTurn

				# Add to current deals
				# CvAssertMsg(kDeal.m_TradedItems.size() > 0, "New deal has no tradeable items!")
				self.currentDeals.append(deal)

				sentResearchAgreementNotification: bool = False
				cost: int = 0

				# What effects does this Deal have right now?
				for it in deal.tradeItems:
					# if the deal is renewed do not start it up
					if it.toRenewed:
						continue

					acceptedFromPlayer = deal.fromPlayerFor(it)
					acceptedToPlayer = deal.toPlayerFor(it)

					# Deduct Gold cost (if applicable)
					cost: int = self.tradeItemGoldCost(it.itemType, acceptedFromPlayer, acceptedToPlayer, simulation)
					acceptedFromPlayer.treasury.changeGoldBy(-cost)

					# Gold
					if it.itemType == DiplomaticDealItemType.gold:  # TRADE_ITEM_GOLD
						goldAmount: int = it.amount
						acceptedFromPlayer.treasury.changeGoldBy(-goldAmount)
						acceptedToPlayer.treasury.changeGoldBy(goldAmount)
					# Gold Per Turn
					elif it.itemType == DiplomaticDealItemType.goldPerTurn:  # TRADE_ITEM_GOLD_PER_TURN
						goldPerTurn: int = it.amount
						acceptedFromPlayer.treasury.changeGoldPerTurnFromDiplomacyBy(-goldPerTurn)
						acceptedToPlayer.treasury.changeGoldPerTurnFromDiplomacyBy(goldPerTurn)
					# Resource
					elif it.itemType == DiplomaticDealItemType.resources:  # TRADE_ITEM_RESOURCES
						resource: ResourceType = it.resource
						resourceQuantity: int = it.amount
						acceptedFromPlayer.changeResourceExport(resource, resourceQuantity)
						acceptedToPlayer.changeResourceImport(resource, resourceQuantity)
					# City
					elif it.itemType == DiplomaticDealItemType.cities:  # TRADE_ITEM_CITIES
						city = simulation.cityAt(it.point)
						if city is not None:
							acceptedToPlayer.acquireCity(city, False, True, simulation)
					elif it.itemType == DiplomaticDealItemType.allowDelegation:  # TRADE_ITEM_ALLOW_EMBASSY
						acceptedFromPlayer.diplomacyAI.doSendDelegationTo(acceptedToPlayer, simulation)
					elif it.itemType == DiplomaticDealItemType.allowEmbassy:  # TRADE_ITEM_ALLOW_EMBASSY
						acceptedFromPlayer.diplomacyAI.playerDict.establishEmbassyTo(acceptedToPlayer)
					elif it.itemType == DiplomaticDealItemType.declarationOfFriendship:  # TRADE_ITEM_DECLARATION_OF_FRIENDSHIP
						# Declaration of friendship always goes both ways.  We will most likely have two entries in the deal for this
						# but just in case, set both anyway.
						acceptedFromPlayer.diplomacyAI.signDeclarationOfFriendshipWith(acceptedToPlayer, True)
						acceptedFromPlayer.diplomacyAI.SetDoFCounter(acceptedToPlayer, 0)
						acceptedToPlayer.diplomacyAI.SetDoFAccepted(acceptedFromPlayer, True)
						acceptedToPlayer.diplomacyAI.SetDoFCounter(acceptedFromPlayer, 0)
					# Vote Commitment
					# elif(it.itemType == DiplomaticDealItemType.voteCommitment):  # TRADE_ITEM_VOTE_COMMITMENT
					#	acceptedFromPlayer.GetLeagueAI()->AddVoteCommitment(acceptedToPlayer, it.Data1, it.Data2, it.Data3, it->m_bFlag1)
					# Open Borders
					elif it.itemType == DiplomaticDealItemType.openBorders:  # TRADE_ITEM_OPEN_BORDERS
						fromPlayer.diplomacyAI.establishOpenBorderAgreementWith(toPlayer, simulation.currentTurn)
					# Defensive Pact
					elif it.itemType == DiplomaticDealItemType.defensivePact:  # TRADE_ITEM_DEFENSIVE_PACT
						fromPlayer.diplomacyAI.signDefensivePactWith(toPlayer, simulation.currentTurn)
					# Research Agreement
					elif it.itemType == DiplomaticDealItemType.researchAgreement:  # TRADE_ITEM_RESEARCH_AGREEMENT
						raise Exception('not implemented')
						# GET_TEAM(eFromTeam).SetHasResearchAgreement(eToTeam, True)
						# acceptedFromPlayer.GetTreasury()->LogExpenditure(acceptedToPlayer.getCivilizationShortDescription(), cost, 9)

						# if not sentResearchAgreementNotification:
						#	sentResearchAgreementNotification = True
							# GC.getGame().DoResearchAgreementNotification(eFromTeam, eToTeam)
					# Trade Agreement
					# elif(it.itemType == DiplomaticDealItemType.tradeAgreement):  # TRADE_ITEM_TRADE_AGREEMENT):
					#	GET_TEAM(eFromTeam).SetHasTradeAgreement(eToTeam, True)
					# Third Party Peace
					elif it.itemType == DiplomaticDealItemType.thirdPartyPeace:  # TRADE_ITEM_THIRD_PARTY_PEACE
						targetPlayer = it.thirdPlayer
						targetPlayerIsMinor: bool = targetPlayer.isMinorCiv()
						fromPlayer.makePeace(targetPlayer, bumpUnits=True, suppressNotification=targetPlayerIsMinor, simulation=simulation)
						fromPlayer.updateForcePeaceWith(targetPlayer, True)
						targetPlayer.updateForcePeaceWith(fromPlayer, True)

						if targetPlayerIsMinor:
							veNowAtPeacePairs.append((targetPlayer, fromPlayer))  # eFromTeam is second, so we can take advantage of CvWeightedVector's sort by weights
					# Third Party War
					elif it.itemType == DiplomaticDealItemType.thirdPartyWar:  # TRADE_ITEM_THIRD_PARTY_WAR
						targetPlayer = it.thirdPlayer
						fromPlayer.doDeclareWarTo(targetPlayer, simulation)

						lockedTurns: int = 15  # COOP_WAR_LOCKED_LENGTH
						fromPlayer.changeNumberOfTurnsLockedIntoWarWith(targetPlayer, lockedTurns)
					# **** Peace Treaty **** this should always be the last item processed!!!
					elif it.itemType == DiplomaticDealItemType.peaceTreaty:  # TRADE_ITEM_PEACE_TREATY
						fromPlayer.makePeace(toPlayer)
						fromPlayer.updateForcePeaceWith(toPlayer, True)
					else:
						raise Exception(f'{it.itemType} not handled')
					# ////////////////////////////////////////////////////////////////////
					# **** DO NOT PUT ANYTHING AFTER THIS LINE ****
					# ////////////////////////////////////////////////////////////////////

				self.logDealComplete(deal)

		# Update UI if we were involved in the deal
		activePlayer = simulation.activePlayer()
		if activePlayer is not None:
			if fromPlayer == activePlayer or toPlayer == activePlayer:
				simulation.userInterface.updateGameData()

		# Send out a condensed notification if peace was made with third party minor civs in this deal
		if len(veNowAtPeacePairs) > 0:
			# Loop through all teams
			for loopFromPlayer in simulation.players:
				bFromTeamMadePeace: bool = False

				strMessage = _("TXT_KEY_MISC_MADE_PEACE_WITH_MINOR_ALLIES") % {'player': fromPlayer.name()}
				strSummary = _("TXT_KEY_MISC_MADE_PEACE_WITH_MINOR_ALLIES_SUMMARY") % {'player': fromPlayer.name()}

				# Did this team make peace with someone in this deal?
				for (loopTargetPlayer, loopFromPlayer2) in veNowAtPeacePairs:
					if loopFromPlayer == loopFromPlayer2:
						strMessage = strMessage + "[NEWLINE]" + loopTargetPlayer.name()
						bFromTeamMadePeace = True

				# Send out notifications if there was a change
				if bFromTeamMadePeace:
					# Send out the notifications to other players
					for loopNotifyPlayer in simulation.players:
						if not loopNotifyPlayer.isAlive():
							continue

						if loopNotifyPlayer == fromPlayer:
							continue

						if loopNotifyPlayer.isHasMet(fromPlayer):  # antonjs: consider: what if eNotifPlayer hasn't met one or more of the minors that eFromTeam made peace with?
							loopNotifyPlayer.notifications.addNotification(NotificationType.peace, leader=fromPlayer.leader)

		return foundId and valid

	def dealsOf(self, player, dealType: DiplomaticDealType) -> [DiplomaticDeal]:
		if dealType == DiplomaticDealType.historic:
			return list(filter(lambda d: d.toPlayer == player or d.fromPlayer == player, self.historicalDeals))

		elif dealType == DiplomaticDealType.current:
			return list(filter(lambda d: d.toPlayer == player or d.fromPlayer == player, self.currentDeals))

		return []

	def tradeItemGoldCost(self, itemType: DiplomaticDealItemType, fromPlayer, toPlayer, simulation) -> int:
		"""Some trade items require Gold to be spent by both players"""
		iGoldCost: int = 0

		if itemType == DiplomaticDealItemType.researchAgreement:
			iGoldCost = simulation.researchAgreementCost(fromPlayer, toPlayer)
		# elif itemType == DiplomaticDealItemType.tradeAgreement:
		#	iGoldCost = 250

		return iGoldCost

	def doCancelDealsBetween(self, player, otherPlayer, simulation):
		"""Deals between these two teams were interrupted (war or something)"""
		if len(self.currentDeals) > 0:
			# Loop through first set of players
			for fromPlayer in simulation.players:
				if not fromPlayer.isHuman() and not fromPlayer.isMajorAI():
					continue

				if not fromPlayer.isEverAlive():
					continue

				if not fromPlayer.isAlliedWith(player):
					continue

				# Loop through second set of players
				for toPlayer in simulation.players:
					if not toPlayer.isHuman() and not toPlayer.isMajorAI():
						continue

					if not toPlayer.isEverAlive():
						continue

					if not toPlayer.isAlliedWith(otherPlayer):
						continue

					self.doCancelDealsBetweenPlayers(fromPlayer, toPlayer, simulation)

		return

	def doCancelDealsBetweenPlayers(self, fromPlayer, toPlayer, simulation):
		"""Deals between these two Players were interrupted (death)"""
		if len(self.currentDeals) > 0:
			somethingChanged: bool = False
			tempDeals: [DiplomaticDeal] = []

			# Copy the deals into a temporary container
			for currentDeal in self.currentDeals:
				tempDeals.append(currentDeal)

			self.currentDeals = []
			for tempDeal in tempDeals:
				# Players on this deal match?
				if (tempDeal.fromPlayer == fromPlayer and tempDeal.toPlayer == toPlayer) or \
					(tempDeal.fromPlayer == toPlayer and tempDeal.toPlayer == fromPlayer):
					# Change final turn
					tempDeal.finalTurn = simulation.currentTurn

					# Cancel individual items
					for tradeItem in tempDeal.tradeItems:
						somethingChanged = True
						tradeItem.finalTurn = simulation.currentTurn

						fromPlayer = tempDeal.fromPlayer
						toPlayer = tempDeal.other.toPlayer

						self.doEndTradedItem(tradeItem, fromPlayer, toPlayer, True, simulation)

					self.historicalDeals.append(tempDeal)
				else:
					self.currentDeals.append(tempDeal)

			if somethingChanged:
				# Update UI if we were involved in the deal
				activePlayer = simulation.activePlayer()
				if fromPlayer == activePlayer or toPlayer == activePlayer:
					simulation.userInterface.updateGameData()

		return

	def logDealComplete(self, deal):
		logging.info('Deal has been completed:')

		for tradeItem in deal.tradeItems:
			logging.info(f'{tradeItem}')

		return

	def doEndTradedItem(self, tradeItem: DiplomaticDealItem, fromPlayer, toPlayer, cancelled: bool, simulation):
		"""End a TradedItem (if it's an ongoing item)"""
		tradeItem.toRenewed = False # if this item is properly ended, then don't have it marked with "to renew"

		if tradeItem.fromRenewed:
			return

		# Gold Per Turn
		if tradeItem.itemType == DiplomaticDealItemType.goldPerTurn:
			iGoldPerTurn = tradeItem.amount
			fromPlayer.treasury.changeGoldPerTurnFromDiplomacy(iGoldPerTurn)
			toPlayer.treasury.changeGoldPerTurnFromDiplomacy(-iGoldPerTurn)

			if fromPlayer.isHuman():
				fromPlayer.notifications.addNotification(NotificationType.dealExpiredGoldPerTurnFromUs, leader=toPlayer.leader)

			if toPlayer.isHuman():
				toPlayer.notifications.addNotification(NotificationType.dealExpiredGoldPerTurnToUs, leader=fromPlayer.leader)

		# Resource
		elif tradeItem.itemType == DiplomaticDealItemType.resources:
			resource: ResourceType = tradeItem.resource
			resourceQuantity: int = tradeItem.amount

			fromPlayer.changeResourceExport(resource, -resourceQuantity)
			toPlayer.changeResourceImport(resource, -resourceQuantity)

			if fromPlayer.isHuman():
				fromPlayer.notifications.addNotification(NotificationType.dealExpiredResourceFromUs, leader=toPlayer.leader, resource=resource)

			if toPlayer.isHuman():
				toPlayer.notifications.addNotification(NotificationType.dealExpiredResourceToUs, leader=fromPlayer.leader, resource=resource)

		# Open Borders
		elif tradeItem.itemType == DiplomaticDealItemType.openBorders:
			fromPlayer.diplomacyAI.playerDict.cancelOpenBorderAgreementWith(toPlayer)

			if fromPlayer.isHuman():
				fromPlayer.notifications.addNotification(NotificationType.dealExpiredOpenBordersFromUs, leader=toPlayer.leader)

			if toPlayer.isHuman():
				toPlayer.notifications.addNotification(NotificationType.dealExpiredOpenBordersToUs, leader=fromPlayer.leader)

		# Defensive Pact
		elif tradeItem.itemType == DiplomaticDealItemType.defensivePact:
			fromPlayer.diplomacyAI.cancelDefensivePactWith(toPlayer)

			if fromPlayer.isHuman():
				fromPlayer.notifications.addNotification(NotificationType.dealExpiredDefensivePactFromUs, leader=toPlayer.leader)

			if toPlayer.isHuman():
				toPlayer.notifications.addNotification(NotificationType.dealExpiredDefensivePactToUs, leader=fromPlayer.leader)

		# Research Agreement
		elif tradeItem.itemType == DiplomaticDealItemType.researchAgreement:
			fromPlayer.diplomacyAI.cancelResearchAgreementWith(toPlayer)

			if not fromPlayer.isAtWarWith(toPlayer) and not cancelled:
				# Beaker boost = ((sum of both players' beakers over term of RA) / 2) / 3) * (median tech percentage rate)
				toPlayerBeakers = toPlayer.researchAgreementCounter(fromPlayer)
				fromPlayerBeakers = fromPlayer.researchAgreementCounter(toPlayer)
				beakersBonus = min(toPlayerBeakers, fromPlayerBeakers) / 3  # one (third) of minimum contribution
				beakersBonus = (beakersBonus * toPlayer.medianTechPercentage()) / 100

				toPlayer.techs.addScience(beakersBonus)

			if toPlayer.isHuman():
				toPlayer.notifications.addNotification(NotificationType.dealExpiredResearchAgreement, leader=fromPlayer.leader)

		# Trade Agreement
		# elif(tradeItem.itemType == DiplomaticDealItemType.TRADE_AGREEMENT):
		# 	GET_TEAM(eFromTeam).SetHasTradeAgreement(eToTeam, false)
		#
		# 	pNotifications = fromPlayer.GetNotifications()
		# 	if(pNotifications)
		# 		strBuffer = GetLocalizedText("TXT_KEY_NOTIFICATION_DEAL_EXPIRED_TRADE_AGREEMENT_FROM_US", toPlayer.getNameKey())
		# 		strSummary = GetLocalizedText("TXT_KEY_NOTIFICATION_SUMMARY_DEAL_EXPIRED_TRADE_AGREEMENT_FROM_US", toPlayer.getNameKey())
		# 		pNotifications->Add(NOTIFICATION_DEAL_EXPIRED_TRADE_AGREEMENT, strBuffer, strSummary, -1, -1, -1)
		#
		# 	pNotifications = toPlayer.GetNotifications()
		# 	if(pNotifications)
		# 		strBuffer = GetLocalizedText("TXT_KEY_NOTIFICATION_DEAL_EXPIRED_TRADE_AGREEMENT_TO_US", fromPlayer.getNameKey())
		# 		strSummary = GetLocalizedText("TXT_KEY_NOTIFICATION_SUMMARY_DEAL_EXPIRED_TRADE_AGREEMENT_TO_US", fromPlayer.getNameKey())
		# 		pNotifications->Add(NOTIFICATION_DEAL_EXPIRED_TRADE_AGREEMENT, strBuffer, strSummary, -1, -1, -1)

		# Peace Treaty
		elif tradeItem.itemType == DiplomaticDealItemType.peaceTreaty:
			fromPlayer.diplomacyAI.playerDict.updateForcePeaceWith(toPlayer, False)

			if toPlayer.isHuman():
				toPlayer.notifications.addNotification(NotificationType.dealExpiredPeaceTreaty, leader=fromPlayer.leader)

		# Third Party Peace Treaty
		elif tradeItem.itemType == DiplomaticDealItemType.thirdPartyPeace:
			targetPlayer = tradeItem.thirdPlayer
			fromPlayer.diplomacyAI.playerDict.updateForcePeaceWith(targetPlayer, False)
			targetPlayer.diplomacyAI.playerDict.updateForcePeaceWith(fromPlayer, False)

			if targetPlayer.isAlive():
				# Notification for FROM player
				if fromPlayer.isHuman():
					fromPlayer.notifications.addNotification(NotificationType.dealExpiredPeaceTreaty, leader=targetPlayer.leader)

				# Notification for TARGET player
				if targetPlayer.isHuman():
					targetPlayer.notifications.addNotification(NotificationType.dealExpiredPeaceTreaty, leader=fromPlayer.leader)

		# Vote Commitment
		elif tradeItem.itemType == DiplomaticDealItemType.voteCommitment:
			fromPlayer.leagueAI.cancelVoteCommitmentsToPlayer(toPlayer)
			toPlayer.leagueAI.cancelVoteCommitmentsToPlayer(fromPlayer)

		return

	def doCancelAllDealsOf(self, cancelPlayer, simulation):
		"""End EVERYONE's deals with eCancelPlayer (typically upon death)"""
		# Loop through first set of players
		for loopPlayer in simulation.players:
			if not loopPlayer.isMajorAI() and not loopPlayer.isHuman():
				continue

			if not loopPlayer.isEverAlive():
				continue

			if loopPlayer == cancelPlayer:
				continue

			if cancelPlayer.hasMetWith(loopPlayer):
				self.doCancelDealsBetweenPlayers(cancelPlayer, loopPlayer, simulation)

		return
