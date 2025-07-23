from typing import Optional, List

from smarthexboard.smarthexboardlib.game.civilizations import CivilizationAbility
from smarthexboard.smarthexboardlib.game.flavors import Flavor, FlavorType
from smarthexboard.smarthexboardlib.game.policyCards import PolicyCardType, PolicyCardSlot
from smarthexboard.smarthexboardlib.game.states.ages import AgeType
from smarthexboard.smarthexboardlib.game.states.gossips import GossipType
from smarthexboard.smarthexboardlib.game.types import CivicType, EraType
from smarthexboard.smarthexboardlib.core.base import ExtendedEnum, WeightedBaseList
from smarthexboard.smarthexboardlib.utils.base import isinstance_string


class PolicyCardSlotType(ExtendedEnum):
	military = 'military'
	economic = 'economic'
	diplomatic = 'diplomatic'
	wildcard = 'wildcard'


class PolicyCardSlots:
	def __init__(self, military: int, economic: int, diplomatic: int, wildcard: int):
		self.military = military
		self.economic = economic
		self.diplomatic = diplomatic
		self.wildcard = wildcard

	def types(self) -> List[PolicyCardSlotType]:
		list: List[PolicyCardSlotType] = []

		for _ in range(self.military):
			list.append(PolicyCardSlotType.military)

		for _ in range(self.economic):
			list.append(PolicyCardSlotType.economic)

		for _ in range(self.diplomatic):
			list.append(PolicyCardSlotType.diplomatic)

		for _ in range(self.wildcard):
			list.append(PolicyCardSlotType.wildcard)

		return list


class GovernmentTypeData:
	def __init__(self, name: str, bonus1Summary: str, bonus2Summary: str, era: EraType,
	             requiredCivic: Optional[CivicType], policyCardSlots: PolicyCardSlots, flavors: List[Flavor],
	             influencePointsPerTurn: int, envoyPerInfluencePoints: int, envoysFromInfluencePoints: int,
	             tourismFactor: int):
		self.name = name
		self.bonus1Summary = bonus1Summary
		self.bonus2Summary = bonus2Summary
		self.era = era
		self.requiredCivic = requiredCivic
		self.policyCardSlots = policyCardSlots
		self.flavors = flavors
		self.influencePointsPerTurn = influencePointsPerTurn
		self.envoyPerInfluencePoints = envoyPerInfluencePoints
		self.envoysFromInfluencePoints = envoysFromInfluencePoints
		self.tourismFactor = tourismFactor


class GovernmentType(ExtendedEnum):
	# ancient
	chiefdom = 'chiefdom'

	# classical
	autocracy = 'autocracy'
	classicalRepublic = 'classicalRepublic'
	oligarchy = 'oligarchy'

	# medieval
	merchantRepublic = 'merchantRepublic'
	monarchy = 'monarchy'

	# renaissance
	theocracy = 'theocracy'

	# modern
	fascism = 'fascism'
	communism = 'communism'
	democracy = 'democracy'

	def title(self) -> str:  # cannot use 'name'
		return self._data().name

	def requiredCivic(self) -> Optional[CivicType]:
		return self._data().requiredCivic

	def tourismFactor(self) -> int:
		return self._data().tourismFactor

	def flavorValue(self, flavorType: FlavorType) -> int:
		flavorOfCard = next((flavor for flavor in self._data().flavors if flavor.flavorType == flavorType), None)

		if flavorOfCard is not None:
			return flavorOfCard.value

		return 0

	def _data(self) -> GovernmentTypeData:
		# ancient
		if self == GovernmentType.chiefdom:
			#
			return GovernmentTypeData(
				name="TXT_KEY_GOVERNMENT_CHIEFDOM_TITLE",
				bonus1Summary="TXT_KEY_GOVERNMENT_CHIEFDOM_BONUS1",
				bonus2Summary="TXT_KEY_GOVERNMENT_CHIEFDOM_BONUS2",
				era=EraType.ancient,
				requiredCivic=CivicType.codeOfLaws,
				policyCardSlots=PolicyCardSlots(military=1, economic=1, diplomatic=0, wildcard=0),
				flavors=[],
				influencePointsPerTurn=1,
				envoyPerInfluencePoints=100,
				envoysFromInfluencePoints=1,
				tourismFactor=0
			)

		# classical
		elif self == GovernmentType.autocracy:
			#
			return GovernmentTypeData(
				name="TXT_KEY_GOVERNMENT_AUTOCRACY_TITLE",
				bonus1Summary="TXT_KEY_GOVERNMENT_AUTOCRACY_BONUS1",
				bonus2Summary="TXT_KEY_GOVERNMENT_AUTOCRACY_BONUS2",
				era=EraType.classical,
				requiredCivic=CivicType.politicalPhilosophy,
				policyCardSlots=PolicyCardSlots(military=2, economic=1, diplomatic=0, wildcard=0),
				flavors=[
					Flavor(FlavorType.growth, value=2),
					Flavor(FlavorType.production, value=3)
				],
				influencePointsPerTurn=3,
				envoyPerInfluencePoints=100,
				envoysFromInfluencePoints=1,
				tourismFactor=-2
			)
		elif self == GovernmentType.classicalRepublic:
			#
			return GovernmentTypeData(
				name="TXT_KEY_GOVERNMENT_CLASSICAL_REPUBLIC_TITLE",
				bonus1Summary="TXT_KEY_GOVERNMENT_CLASSICAL_REPUBLIC_BONUS1",
				bonus2Summary="TXT_KEY_GOVERNMENT_CLASSICAL_REPUBLIC_BONUS2",  #
				era=EraType.classical,
				requiredCivic=CivicType.politicalPhilosophy,
				policyCardSlots=PolicyCardSlots(military=0, economic=2, diplomatic=1, wildcard=1),
				flavors=[Flavor(FlavorType.amenities, value=4)],
				influencePointsPerTurn=3,
				envoyPerInfluencePoints=100,
				envoysFromInfluencePoints=1,
				tourismFactor=-1
			)
		elif self == GovernmentType.oligarchy:
			#
			return GovernmentTypeData(
				name="TXT_KEY_GOVERNMENT_OLIGARCHY_TITLE",
				bonus1Summary="TXT_KEY_GOVERNMENT_OLIGARCHY_BONUS1",
				bonus2Summary="TXT_KEY_GOVERNMENT_OLIGARCHY_BONUS2",
				era=EraType.classical,
				requiredCivic=CivicType.politicalPhilosophy,
				policyCardSlots=PolicyCardSlots(military=1, economic=1, diplomatic=1, wildcard=1),
				flavors=[Flavor(FlavorType.offense, value=4)],
				influencePointsPerTurn=3,
				envoyPerInfluencePoints=100,
				envoysFromInfluencePoints=1,
				tourismFactor=-2
			)

		# medieval
		elif self == GovernmentType.merchantRepublic:
			#
			return GovernmentTypeData(
				name="TXT_KEY_GOVERNMENT_MERCHANT_REPUBLIC_TITLE",
				bonus1Summary="TXT_KEY_GOVERNMENT_MERCHANT_REPUBLIC_BONUS1",  #
				bonus2Summary="TXT_KEY_GOVERNMENT_MERCHANT_REPUBLIC_BONUS2",
				era=EraType.medieval,
				requiredCivic=CivicType.exploration,
				policyCardSlots=PolicyCardSlots(military=1, economic=2, diplomatic=1, wildcard=2),
				flavors=[Flavor(FlavorType.gold, value=4)],
				influencePointsPerTurn=5,
				envoyPerInfluencePoints=150,
				envoysFromInfluencePoints=2,
				tourismFactor=-2
			)
		elif self == GovernmentType.monarchy:
			#
			return GovernmentTypeData(
				name="TXT_KEY_GOVERNMENT_MONARCHY_TITLE",
				bonus1Summary="TXT_KEY_GOVERNMENT_MONARCHY_BONUS1",
				bonus2Summary="TXT_KEY_GOVERNMENT_MONARCHY_BONUS2",  #
				era=EraType.medieval,
				requiredCivic=CivicType.divineRight,
				policyCardSlots=PolicyCardSlots(military=3, economic=1, diplomatic=1, wildcard=1),
				flavors=[Flavor(FlavorType.growth, value=3)],
				influencePointsPerTurn=5,
				envoyPerInfluencePoints=150,
				envoysFromInfluencePoints=2,
				tourismFactor=-3
			)

		# renaissance
		elif self == GovernmentType.theocracy:
			#
			return GovernmentTypeData(
				name="TXT_KEY_GOVERNMENT_THEOCRACY_TITLE",
				bonus1Summary="TXT_KEY_GOVERNMENT_THEOCRACY_BONUS1",  #
				bonus2Summary="TXT_KEY_GOVERNMENT_THEOCRACY_BONUS2",  #
				era=EraType.renaissance,
				requiredCivic=CivicType.reformedChurch,
				policyCardSlots=PolicyCardSlots(military=2, economic=2, diplomatic=1, wildcard=1),
				flavors=[Flavor(FlavorType.religion, value=4)],
				influencePointsPerTurn=5,
				envoyPerInfluencePoints=150,
				envoysFromInfluencePoints=2,
				tourismFactor=-4
			)

		# modern
		elif self == GovernmentType.fascism:
			#
			return GovernmentTypeData(
				name="TXT_KEY_GOVERNMENT_FASCISM_TITLE",
				bonus1Summary="TXT_KEY_GOVERNMENT_FASCISM_BONUS1",  # 2nd
				bonus2Summary="TXT_KEY_GOVERNMENT_FASCISM_BONUS2",
				era=EraType.modern,
				requiredCivic=CivicType.totalitarianism,
				policyCardSlots=PolicyCardSlots(military=4, economic=1, diplomatic=1, wildcard=2),
				flavors=[Flavor(FlavorType.offense, value=5)],
				influencePointsPerTurn=7,
				envoyPerInfluencePoints=200,
				envoysFromInfluencePoints=3,
				tourismFactor=-5
			)
		elif self == GovernmentType.communism:
			#
			return GovernmentTypeData(
				name="TXT_KEY_GOVERNMENT_COMMUNISM_TITLE",
				bonus1Summary="TXT_KEY_GOVERNMENT_COMMUNISM_BONUS1",  #
				bonus2Summary="TXT_KEY_GOVERNMENT_COMMUNISM_BONUS2",
				era=EraType.modern,
				requiredCivic=CivicType.classStruggle,
				policyCardSlots=PolicyCardSlots(military=3, economic=3, diplomatic=1, wildcard=1),
				flavors=[
					Flavor(FlavorType.defense, value=4),
					Flavor(FlavorType.cityDefense, value=2)
				],
				influencePointsPerTurn=7,
				envoyPerInfluencePoints=200,
				envoysFromInfluencePoints=3,
				tourismFactor=-6
			)
		elif self == GovernmentType.democracy:
			#
			return GovernmentTypeData(
				name="TXT_KEY_GOVERNMENT_DEMOCRACY_TITLE",
				bonus1Summary="TXT_KEY_GOVERNMENT_DEMOCRACY_BONUS1",
				bonus2Summary="TXT_KEY_GOVERNMENT_DEMOCRACY_BONUS2",  #
				era=EraType.modern,
				requiredCivic=CivicType.suffrage,
				policyCardSlots=PolicyCardSlots(military=1, economic=3, diplomatic=2, wildcard=2),
				flavors=[
					Flavor(FlavorType.gold, value=2),
					Flavor(FlavorType.greatPeople, value=4)
				],
				influencePointsPerTurn=7,
				envoyPerInfluencePoints=200,
				envoysFromInfluencePoints=3,
				tourismFactor=-3
			)

		raise AttributeError(f'cant get data for government {self}')

	def influencePointsPerTurn(self) -> int:
		return self._data().influencePointsPerTurn

	def envoyPerInfluencePoints(self) -> int:
		return self._data().envoyPerInfluencePoints

	def policyCardSlots(self) -> PolicyCardSlots:
		return self._data().policyCardSlots

	def envoysFromInfluencePoints(self) -> int:
		return self._data().envoysFromInfluencePoints


class PolicyCardSet:
	def __init__(self, cards_dict: Optional[dict] = None):
		if cards_dict is None:
			self._cards: List[PolicyCardType] = []
		elif isinstance(cards_dict, dict):
			self._cards = cards_dict['_cards']
		else:
			raise Exception('Unsupported parameter combination')

	def hasCard(self, policyCard: PolicyCardType) -> bool:
		return policyCard in self._cards

	def addCard(self, policyCard: PolicyCardType):
		self._cards.append(policyCard)

	def cards(self) -> List[PolicyCardType]:
		return self._cards

	def removeCard(self, policyCard: PolicyCardType):
		self._cards = list(filter(lambda card: card != policyCard, self._cards))

	def filled(self, slots: PolicyCardSlots) -> bool:
		militaryCards = len(list(filter(lambda card: card.slot() == PolicyCardSlot.military, self._cards)))
		economicCards = len(list(filter(lambda card: card.slot() == PolicyCardSlot.economic, self._cards)))
		diplomaticCards = len(list(filter(lambda card: card.slot() == PolicyCardSlot.diplomatic, self._cards)))
		wildCards = len(list(filter(lambda card: card.slot() == PolicyCardSlot.wildcard, self._cards)))

		deltaMilitary = militaryCards - slots.military
		deltaEconomic = economicCards - slots.economic
		deltaDiplomatic = diplomaticCards - slots.diplomatic

		# check for empty slots
		if deltaMilitary < 0 or deltaEconomic < 0 or deltaDiplomatic < 0:
			return False

		return slots.wildcard - deltaMilitary - deltaEconomic - deltaDiplomatic - wildCards == 0


class PlayerGovernment:
	def __init__(self, player):
		if isinstance_string(player, 'Player'):
			self.player = player
			self._currentGovernmentValue: GovernmentType = GovernmentType.chiefdom
			self._policyCards: PolicyCardSet = PolicyCardSet()
			self._lastCheckedGovernment: int = -1
		elif isinstance(player, dict):
			self._currentGovernmentValue = player['_currentGovernmentValue']
			self._policyCards = PolicyCardSet(player['_policyCards'])
			self._lastCheckedGovernment = player['_lastCheckedGovernment']
		else:
			raise Exception(f'Cannot serialize PlayerGovernment from {type(player)}')


	def setGovernment(self, governmentType: GovernmentType, simulation):
		#
		if self._currentGovernmentValue != governmentType:
			self._currentGovernmentValue = governmentType
			self._policyCards = PolicyCardSet()  # reset card selection

			if self.player.isHuman():
				self.player.notifications.addNotification("NotificationType.policiesNeeded")

			self.player.doUpdateTradeRouteCapacity(simulation)

			# send gossip to other players
			simulation.sendGossip(GossipType.governmentChange, government=governmentType, player=self.player)

		return

	def currentGovernment(self) -> GovernmentType:
		return self._currentGovernmentValue

	def hasCard(self, policyCard: PolicyCardType) -> bool:
		return self._policyCards.hasCard(policyCard)

	def addCard(self, policyCard: PolicyCardType):
		self._policyCards.addCard(policyCard)

	def removeCard(self, policyCard: PolicyCardType):
		self._policyCards.removeCard(policyCard)

	def hasPolicyCardsFilled(self, simulation) -> bool:
		return self._policyCards.filled(self.policyCardSlots(simulation))

	def policyCardSlots(self, simulation) -> PolicyCardSlots:
		if self._currentGovernmentValue is not None:
			policyCardSlots = self._currentGovernmentValue.policyCardSlots()

			if self.player.leader.civilization().ability() == CivilizationAbility.platosRepublic:
				policyCardSlots.wildcard += 1

			# alhambra: +1 Military policy slot
			if self.player.hasWonder("WonderType.alhambra", simulation):
				policyCardSlots.military += 1

			# forbiddenCity: +1 Wildcard policy slot
			if self.player.hasWonder("WonderType.forbiddenCity", simulation):
				policyCardSlots.wildcard += 1

			# potalaPalace: +1 Diplomatic policy slot
			if self.player.hasWonder("WonderType.potalaPalace", simulation):
				policyCardSlots.diplomatic += 1

			return policyCardSlots

		return PolicyCardSlots(military=0, economic=0, diplomatic=0, wildcard=0)

	def fillPolicyCards(self, simulation):
		civics = self.player.civics
		# all cards
		allPolicyCards = list(PolicyCardType)

		# find possible cards
		policyCards = list(
			filter(lambda pc: True if pc.requiredCivic() is None else civics.hasCivic(pc.requiredCivic()),
			       allPolicyCards))

		# remove obsolete cards
		policyCards = list(
			filter(lambda pc: True if pc.obsoleteCivic() is None else not civics.hasCivic(pc.obsoleteCivic()),
			       policyCards))

		# remove dark age cards (if player is not in dark age)
		policyCards = list(filter(lambda
			                          pc: pc.requiresDarkAge() and self.player.currentAge() == AgeType.dark or not pc.requiresDarkAge() and self.player.currentAge() != AgeType.dark,
		                          policyCards))

		# remove cards from wrong age
		policyCards = list(
			filter(lambda pc: True if pc.startEra() is None else self.player.currentEra() >= pc.startEra(),
			       policyCards))
		policyCards = list(
			filter(lambda pc: True if pc.endEra() is None else self.player.currentEra() <= pc.endEra(), policyCards))

		# remove 'replaces'
		# fixme
		# policyCards = policyCards.filter
		# {
		# for card in $0.replacePolicyCards() {
		# if policyCards.contains(card) {
		# return false
		# }
		# }

		# rate cards
		policyCardRating = WeightedBaseList()

		for policyCard in policyCards:
			value = 0
			for flavourType in list(FlavorType):
				value += self.player.personalAndGrandStrategyFlavor(flavourType) * policyCard.flavorValue(flavourType)

			policyCardRating.addWeight(value, policyCard)

		# select best policy cards for each slot
		slots: PolicyCardSlots = self.policyCardSlots(simulation)
		for slotType in slots.types():
			policyDict = {k: v for k, v in policyCardRating.items() if slotType == PolicyCardSlotType.wildcard or k.slot() == slotType}
			possibleCardsForSlot = WeightedBaseList(policyDict)

			bestCard = possibleCardsForSlot.chooseLargest()

			if bestCard is not None:
				self.addCard(bestCard)

				del policyCardRating[bestCard]

		return

	def chooseBestGovernment(self, simulation):
		if self._currentGovernmentValue is None or self._lastCheckedGovernment + 10 > simulation.currentTurn:
			# all governments
			allGovernmentTypes = list(GovernmentType)

			# find possible governments
			governmentTypes = list(filter(lambda g: self.player.civics.hasCivic(g.requiredCivic()), allGovernmentTypes))

			if len(governmentTypes) > 0:
				# rate governments
				governmentRating = WeightedBaseList()

				for governmentType in governmentTypes:
					value = 0.0
					for flavourType in list(FlavorType):
						value += self.player.personalAndGrandStrategyFlavor(flavourType) * governmentType.flavorValue(
							flavourType)

					governmentRating.addWeight(value, governmentType)

				# select government
				bestGovernment = governmentRating.chooseLargest()
				if bestGovernment is not None:
					if bestGovernment != self._currentGovernmentValue:
						self.setGovernmentType(bestGovernment, simulation)
						self.fillPolicyCards(simulation)
			else:
				self.setGovernmentType(GovernmentType.chiefdom, simulation)
				self.fillPolicyCards(simulation)

			self._lastCheckedGovernment = simulation.currentTurn

		return

	def setGovernmentType(self, governmentType: GovernmentType, simulation):
		if self._currentGovernmentValue != governmentType:

			self._currentGovernmentValue = governmentType
			self._policyCards = PolicyCardSet()  # reset card selection

			if self.player.isHuman():
				self.player.notifications.addNotification("NotificationType.policiesNeeded")

			self.player.doUpdateTradeRouteCapacity(simulation)

			# send gossip to other players
			simulation.sendGossip(GossipType.governmentChange, government=governmentType, player=self.player)

		return

	def verify(self, simulation):
		possibleCards = self.possiblePolicyCards()
		cardTypesToRemove: List[PolicyCardType] = []

		for cardType in self._policyCards.cards():
			if cardType not in possibleCards:
				cardTypesToRemove.append(cardType)

		for cardTypeToRemove in cardTypesToRemove:
			self.removeCard(cardTypeToRemove)

		return

	def possiblePolicyCards(self) -> List[PolicyCardType]:
		cards: List[PolicyCardType] = []

		for cardType in list(PolicyCardType):
			if cardType is PolicyCardType.none:
				continue

			requiredCondition = True

			requiredCivic = cardType.requiredCivic()
			if requiredCivic is not None:
				if not self.player.civics.hasCivic(requiredCivic):
					requiredCondition = False

			obsoleteCondition = False
			obsoleteCivic = cardType.obsoleteCivic()
			if obsoleteCivic is not None:
				if self.player.civics.hasCivic(obsoleteCivic):
					obsoleteCondition = True

			if cardType.requiresDarkAge():
				if self.player.currentAge() != AgeType.dark:
					continue

			startEra = cardType.startEra()
			if startEra is not None:
				if self.player.currentEra() < startEra:
					continue

			endEra = cardType.endEra()
			if endEra is not None:
				if self.player.currentEra() > endEra:
					continue

			if requiredCondition and not obsoleteCondition:
				cards.append(cardType)

		filteredCards: List[PolicyCardType] = []

		# remove 'replaced' (better) cards
		for card in cards:
			# check if card is in replaced list of another card
			inReplacedList = False
			for loopCard in cards:
				if card in loopCard.replacePolicyCards():
					inReplacedList = True

			if not inReplacedList:
				filteredCards.append(card)

		return filteredCards

	def hasPolicyEncouragingGarrisons(self) -> bool:
		return False
