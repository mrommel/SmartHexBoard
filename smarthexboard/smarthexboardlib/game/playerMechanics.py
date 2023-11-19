import logging
import random
import sys
from functools import reduce
from typing import Optional

from smarthexboard.smarthexboardlib.core.base import WeightedBaseList, ExtendedEnum, InvalidEnumError
from smarthexboard.smarthexboardlib.game.ai.baseTypes import PlayerStateAllWars, WarGoalType, MilitaryStrategyType
from smarthexboard.smarthexboardlib.game.ai.diplomaticTypes import DiplomaticStatementType, DiplomaticDeal, MajorCivOpinionType, \
	MinorPlayerApproachType, PeaceTreatyType, MajorPlayerApproachType, GuessConfidenceType, CoopWarStateType, \
	DiplomaticDealItemType, DiplomaticDealType
from smarthexboard.smarthexboardlib.game.ai.economicStrategies import EconomicStrategyType
from smarthexboard.smarthexboardlib.game.ai.economics import PurchaseType
from smarthexboard.smarthexboardlib.game.ai.grandStrategies import GrandStrategyAIType
from smarthexboard.smarthexboardlib.game.ai.militaries import MilitaryThreatType
from smarthexboard.smarthexboardlib.game.ai.militaryTypes import OperationStateReason
from smarthexboard.smarthexboardlib.game.baseTypes import HandicapType, LeaderAgendaType, StrengthType, PlayerWarStateType, PlayerTargetValueType, \
	WarDamageLevelType, WarProjectionType, DisputeLevelType, AggressivePostureType
from smarthexboard.smarthexboardlib.game.cityStates import CityStateType, CityStateQuestType, CityStateCategory
from smarthexboard.smarthexboardlib.game.civilizations import CivilizationType, LeaderType
from smarthexboard.smarthexboardlib.game.flavors import FlavorType
from smarthexboard.smarthexboardlib.game.moments import Moment, MomentType
from smarthexboard.smarthexboardlib.game.notifications import NotificationType
from smarthexboard.smarthexboardlib.game.playerTypes import MinorPlayerPersonalityType
from smarthexboard.smarthexboardlib.game.religions import ReligionType, PantheonType, BeliefType
from smarthexboard.smarthexboardlib.game.states.accessLevels import AccessLevel
from smarthexboard.smarthexboardlib.game.states.ages import AgeType
from smarthexboard.smarthexboardlib.game.states.dedications import DedicationType
from smarthexboard.smarthexboardlib.game.states.diplomaticMessages import DiplomaticRequestState, DiplomaticRequestMessage, LeaderEmotionType
from smarthexboard.smarthexboardlib.game.states.gossips import GossipType, GossipItem
from smarthexboard.smarthexboardlib.game.states.ui import PopupType
from smarthexboard.smarthexboardlib.game.types import TechType, CivicType, EraType
from smarthexboard.smarthexboardlib.game.unitTypes import UnitClassType, UnitTaskType, UnitType
from smarthexboard.smarthexboardlib.game.wonders import WonderType
from smarthexboard.smarthexboardlib.map import constants
from smarthexboard.smarthexboardlib.map.base import HexPoint
from smarthexboard.smarthexboardlib.map.improvements import ImprovementType
from smarthexboard.smarthexboardlib.map.types import FeatureType, UnitDomainType, YieldType, TerrainType, ResourceType
from smarthexboard.smarthexboardlib.utils.base import firstOrNone, secondOrNone
from smarthexboard.smarthexboardlib.utils.plugin import Tests


class WeightedTechList(WeightedBaseList):
	def __init__(self):
		super().__init__()
		for tech in list(TechType):
			self.setWeight(0.0, tech)


class TechEurekas:
	def __init__(self):
		self._eurekaTrigger = WeightedTechList()

	def triggerFor(self, tech: TechType):
		self._eurekaTrigger.setWeight(1.0, tech)

	def triggeredFor(self, tech: TechType) -> bool:
		return self._eurekaTrigger.weight(tech) > 0.0

	def triggerIncreaseFor(self, tech: TechType, change: float = 1.0):
		self._eurekaTrigger.addWeight(change, tech)

	def triggerCountFor(self, tech: TechType) -> int:
		return int(self._eurekaTrigger.weight(tech))


class PlayerTechs:
	def __init__(self, player):
		self.player = player
		self._techs: [TechType] = []
		self._currentTechValue: Optional[TechType] = None
		self._overflowValue: float = 0.0
		self._lastScienceEarnedValue: float = 1.0
		self._progresses = WeightedTechList()
		self._eurekas = TechEurekas()

	def eurekaTriggeredFor(self, tech: TechType) -> bool:
		return self._eurekas.triggeredFor(tech)

	def triggerEurekaFor(self, tech: TechType, simulation):
		# check if eureka is still needed
		if self.hasTech(tech):
			return

		# check if eureka is already active
		if self.eurekaTriggeredFor(tech):
			return

		self._eurekas.triggerFor(tech)

		# update progress
		eurekaBoost = 0.5

		# freeInquiry + golden - Eureka provide an additional 10% of Technology costs.
		if self.player.currentAge() == AgeType.golden and self.player.hasDedication(DedicationType.freeInquiry):
			eurekaBoost += 0.1

		self._progresses.addWeight(float(tech.cost()) * eurekaBoost, tech)

		# freeInquiry + normal - Gain +1 Era Score when you trigger a [Eureka] Eureka
		if self.player.currentAge() == AgeType.normal and self.player.hasDedication(DedicationType.freeInquiry):
			self.player.addMoment(MomentType.dedicationTriggered, dedication=DedicationType.freeInquiry, simulation=simulation)

		# check quests
		for quest in self.player.ownQuests(simulation):
			if quest.questType == CityStateQuestType.triggerEureka:
				if tech == quest.techType:
					cityStatePlayer = simulation.cityStatePlayerFor(quest.cityState)
					cityStatePlayer.fulfillQuestBy(self.player.leader, simulation)

		# trigger event to user
		if self.player.isHuman():
			simulation.userInterface.showPopup(PopupType.eurekaTriggered, tech=tech)

		return

	def changeEurekaValue(self, tech: TechType, change: float = 1.0):
		return self._eurekas.triggerIncreaseFor(tech, change)

	def eurekaValue(self, tech: TechType):
		return self._eurekas.triggerCountFor(tech)

	def needToChooseTech(self) -> bool:
		return self._currentTechValue is None

	def discover(self, tech: TechType, simulation):
		# check if this tech is the first of a new era
		techsInEra = sum(1 for t in self._techs if t.era() == tech.era())
		if techsInEra == 0 and tech.era() != EraType.ancient:
			if simulation.anyHasMoment(MomentType.worldsFirstTechnologyOfNewEra, eraType=tech.era()):
				self.player.addMoment(MomentType.firstTechnologyOfNewEra, eraType=tech.era(), simulation=simulation)
			else:
				self.player.addMoment(MomentType.worldsFirstTechnologyOfNewEra, eraType=tech.era(),
									  simulation=simulation)

		if simulation is not None:
			self.updateEurekas(simulation)

		# check quests
		if simulation is not None:
			for quest in self.player.ownQuests(simulation):
				if quest.questType == CityStateQuestType.trainUnit:
					obsolete = False
					unitType: UnitType = quest.unitType

					for upgradeUnitType in unitType.upgradesTo():
						requiredTech: Optional[TechType] = upgradeUnitType.requiredTech()
						if requiredTech is not None:
							if requiredTech == tech:
								obsolete = True

					obsoleteTech: Optional[TechType] = unitType.obsoleteTech()
					if obsoleteTech is not None:
						if obsoleteTech == tech:
							obsolete = True

					if obsolete:
						cityStatePlayer = simulation.cityStatePlayerFor(quest.cityState)
						if cityStatePlayer is not None:
							cityStatePlayer.obsoleteQuestBy(self.player.leader, simulation)

				if quest.questType == CityStateQuestType.triggerEureka:
					questTechType: Optional[TechType] = quest.techType
					if questTechType == tech:
						cityStatePlayer = simulation.cityStatePlayerFor(quest.cityState)
						if cityStatePlayer is not None:
							cityStatePlayer.obsoleteQuestBy(self.player.leader, simulation)

		# send gossip
		if simulation is not None:
			simulation.sendGossip(GossipType.technologyResearched, tech=tech, player=self.player)

		# check for printing
		# Researching the Printing technology. This will increase your visibility with all civilizations by one level.
		if simulation is not None:
			if tech == TechType.printing:
				for loopPlayer in simulation.players:
					if loopPlayer.isBarbarian() or loopPlayer.isFreeCity() or loopPlayer.isCityState():
						continue

					if loopPlayer == self.player:
						continue

					if self.player.hasMetWith(loopPlayer):
						self.player.diplomacyAI.increaseAccessLevelTowards(loopPlayer)

		self._techs.append(tech)

	def hasTech(self, tech: TechType) -> bool:
		return tech in self._techs

	def updateEurekas(self, simulation):
		# Games and Recreation - Research the Construction technology.
		if self.hasTech(TechType.construction):
			if not self.player.civics.inspirationTriggeredFor(CivicType.gamesAndRecreation):
				self.player.civics.triggerInspirationFor(CivicType.gamesAndRecreation, simulation)

		# Mass Media - Research Radio.
		if self.hasTech(TechType.radio):
			if not self.player.civics.inspirationTriggeredFor(CivicType.massMedia):
				self.player.civics.triggerInspirationFor(CivicType.massMedia, simulation)

	def possibleTechs(self) -> [TechType]:
		returnTechs: [TechType] = []

		for tech in list(TechType):
			if tech == TechType.none:
				continue

			if self.hasTech(tech):
				continue

			allRequiredPresent = True

			for req in tech.required():

				if not self.hasTech(req):
					allRequiredPresent = False

			if allRequiredPresent:
				returnTechs.append(tech)

		return returnTechs

	def setCurrentTech(self, tech: TechType, simulation):
		if tech not in self.possibleTechs():
			raise Exception(f'cannot choose current tech: {tech}')

		self._currentTechValue = tech

		if self._overflowValue > 0.0:
			self.addScience(self._overflowValue)
			self._overflowValue = 0.0

		if self.player.isHuman():
			simulation.userInterface.selectTech(tech=tech)

	def currentTech(self) -> Optional[TechType]:
		return self._currentTechValue

	def currentScienceProgress(self) -> float:
		if self._currentTechValue is None:
			return 0.0

		return self._progresses.weight(self._currentTechValue)

	def turnsRemainingFor(self, tech: TechType) -> int:

		if self._lastScienceEarnedValue > 0.0:
			cost: float = float(tech.cost())
			remaining = cost - self._progresses.weight(tech)

			return int(remaining / self._lastScienceEarnedValue + 0.5)

		return 1

	def currentScienceTurnsRemaining(self) -> int:
		if self._currentTechValue is None:
			return 1

		return self.turnsRemainingFor(self._currentTechValue)

	def lastScienceEarned(self) -> float:
		return self._lastScienceEarnedValue

	def flavorWeightedOf(self, tech: TechType, flavor: FlavorType) -> float:
		if self.player is None:
			return 0.0

		return float(tech.flavorValue(flavor) * self.player.leader.flavor(flavor))

	def chooseNextTech(self) -> Optional[TechType]:
		weightedTechs: WeightedTechList = WeightedTechList()
		weightedTechs.removeAll()

		possibleTechsList = self.possibleTechs()

		for possibleTech in possibleTechsList:
			weightByFlavor = 0.0

			# weight of current tech
			for flavor in list(FlavorType):
				weightByFlavor += self.flavorWeightedOf(possibleTech, flavor)

			# add techs that can be research with this tech, but only with a little less weight
			for activatedTech in possibleTech.leadsTo():

				for flavor in list(FlavorType):
					weightByFlavor += self.flavorWeightedOf(activatedTech, flavor) * 0.75

				for secondActivatedTech in activatedTech.leadsTo():

					for flavor in list(FlavorType):
						weightByFlavor += self.flavorWeightedOf(secondActivatedTech, flavor) * 0.5

					for thirdActivatedTech in secondActivatedTech.leadsTo():

						for flavor in list(FlavorType):
							weightByFlavor += self.flavorWeightedOf(thirdActivatedTech, flavor) * 0.25

			# revalue based on cost / number of turns
			numberOfTurnsLeft = self.turnsRemainingFor(possibleTech)
			additionalTurnCostFactor = 0.015 * float(numberOfTurnsLeft)
			totalCostFactor = 0.15 + additionalTurnCostFactor
			weightDivisor = pow(float(numberOfTurnsLeft), totalCostFactor)

			# modify weight
			weightByFlavor = float(weightByFlavor) / max(0.1, weightDivisor)  # no division by zero

			weightedTechs.addWeight(weightByFlavor, possibleTech)

		# select one
		selectedIndex = 0 if Tests.are_running else random.randrange(100)

		weightedTechs = weightedTechs.top3()
		weightedTechsArray = weightedTechs.distributeByWeight()
		selectedTech = weightedTechsArray[selectedIndex]

		return selectedTech

	def numberOfDiscoveredTechs(self) -> int:
		return len(self._techs)

	def addScience(self, science: float):
		if self._currentTechValue is not None:
			self._progresses.addWeight(science, self._currentTechValue)
		else:
			self._overflowValue += science

		self._lastScienceEarnedValue = science

	def checkScienceProgress(self, simulation):
		currentTech = self._currentTechValue

		if currentTech is None:
			if not self.player.isHuman():
				bestTech = self.chooseNextTech()
				self.setCurrentTech(bestTech, simulation)

			return

		if self.currentScienceProgress() >= float(currentTech.cost()):
			self.discover(currentTech, simulation)

			# trigger event to user
			if self.player.isHuman():
				simulation.userInterface.showPopup(PopupType.techDiscovered, tech=currentTech)

			# enter era
			if currentTech.era() > self.player.currentEra():
				simulation.enterEra(currentTech.era(), self.player)
				self.player.setEra(currentTech.era(), simulation)

				if self.player.isHuman():
					simulation.userInterface.showPopup(PopupType.eraEntered, era=currentTech.era())

			self._currentTechValue = None

			if self.player.isHuman():
				self.player.notifications.addNotification(NotificationType.techNeeded)

		return

	def hasResearchedAllTechs(self) -> bool:
		remainingTechs = self.possibleTechs()
		return len(remainingTechs) == 1 and firstOrNone(remainingTechs) == TechType.futureTech


class WeightedCivicList(WeightedBaseList):
	def __init__(self):
		super().__init__()
		for civic in list(CivicType):
			self.setWeight(0.0, civic)


class CivicInspirations:
	def __init__(self):
		self._inspirationTrigger = WeightedCivicList()
		self._inspirationCount = WeightedCivicList()

	def triggerFor(self, civic: CivicType):
		self._inspirationTrigger.setWeight(1.0, civic)
		self._inspirationCount.setWeight(0.0, civic)

	def triggeredFor(self, civic: CivicType) -> bool:
		return self._inspirationTrigger.weight(civic) > 0.0

	def triggerIncreaseFor(self, civic: CivicType, change: int = 1):
		self._inspirationCount.addWeight(float(change), civic)

	def triggerCountFor(self, civic: CivicType) -> int:
		return int(self._inspirationCount.weight(civic))


class PlayerCivics:
	def __init__(self, player):
		self.player = player

		self._civics: [CivicType] = []
		self._currentCivicValue: Optional[CivicType] = None
		self._lastCultureEarnedValue: float = 1.0
		self._progresses = WeightedCivicList()
		self._inspirations = CivicInspirations()

	def hasCivic(self, civic: CivicType) -> bool:
		return civic in self._civics

	def discover(self, civic: CivicType, simulation):
		if civic in self._civics:
			raise Exception(f'Civic {civic} already discovered')

		if civic.hasGovernorTitle():
			self.player.addGovernorTitle()

		if civic.envoys() > 0:
			self.player.changeUnassignedEnvoysBy(civic.envoys())

			# notify player about envoy to spend
			if self.player.isHuman():
				# player.notifications()?.add(notification:.envoyEarned)
				pass

		# check if this civic is the first of a new era
		civicsInEra = sum(1 for c in self._civics if c.era() == civic.era())
		if civicsInEra == 0 and civic.era() != EraType.ancient:
			# if simulation.anyHasMoment(of: .worldsFirstCivicOfNewEra(eraType: civic.era())):
			# 	self.player?.addMoment(of:.firstCivicOfNewEra(eraType: civic.era()), simulation)
			# else:
			# 	self.player?.addMoment(of:.worldsFirstCivicOfNewEra(eraType: civic.era()), simulation)
			pass

		if simulation is not None:
			self.updateInspirations(simulation)

		# check quests
		if simulation is not None:
			for quest in self.player.ownQuests(simulation):
				if quest.questType == CityStateQuestType.triggerInspiration:
					questCivicType: Optional[CivicType] = quest.civicType
					if questCivicType == civic:
						cityStatePlayer = simulation.cityStatePlayerFor(quest.cityState)
						cityStatePlayer.obsoleteQuestBy(self.player.leader, simulation)

		# send gossip
		if simulation is not None:
			simulation.sendGossip(GossipType.civicCompleted, civic=civic, player=self.player)

		self._civics.append(civic)

		if simulation is not None:
			self.player.doUpdateTradeRouteCapacity(simulation)

		#
		if civic == CivicType.naturalHistory or civic == CivicType.culturalHeritage:
			if simulation is not None:
				simulation.checkArchaeologySites()

		return

	def needToChooseCivic(self):
		pass

	def currentCultureProgress(self) -> float:
		if self._currentCivicValue is None:
			return 0.0

		return self._progresses.weight(self._currentCivicValue)

	def updateInspirations(self, simulation):
		# NOOP
		pass

	def possibleCivics(self):
		returnCivics: [CivicType] = []

		for civic in list(CivicType):
			if civic == CivicType.none:
				continue

			if self.hasCivic(civic):
				continue

			allRequiredPresent = True

			for req in civic.required():
				if not self.hasCivic(req):
					allRequiredPresent = False

			if allRequiredPresent:
				returnCivics.append(civic)

		return returnCivics

	def setCurrentCivic(self, civic: CivicType, simulation):
		if civic not in self.possibleCivics():
			raise Exception(f'cant select current civic: {civic} - its not in {self.possibleCivics()}')

		self._currentCivicValue = civic

		if self.player.isHuman():
			simulation.userInterface.selectCivic(civic)

		return

	def currentCivic(self) -> Optional[CivicType]:
		return self._currentCivicValue

	def inspirationTriggeredFor(self, civic: CivicType):
		return self._inspirations.triggeredFor(civic)

	def triggerInspirationFor(self, civic: CivicType, simulation):
		# check if eureka is still needed
		if self.hasCivic(civic):
			return

		# check if already active
		if self._inspirations.triggeredFor(civic):
			return

		self._inspirations.triggerFor(civic)

		# update progress
		inspirationBoost = 0.5

		# penBrushAndVoice + golden - Inspiration provide an additional 10% of Civic costs.
		if self.player.currentAge() == AgeType.golden and self.player.hasDedication(DedicationType.penBrushAndVoice):
			inspirationBoost += 0.1

		self._progresses.addWeight(float(civic.cost()) * inspirationBoost, civic)

		# penBrushAndVoice + normal - Gain + 1 Era Score when you trigger an Inspiration
		if self.player.currentAge() == AgeType.normal and self.player.hasDedication(DedicationType.penBrushAndVoice):
			self.player.addMoment(MomentType.dedicationTriggered, dedication=DedicationType.penBrushAndVoice, simulation=simulation)

		# check quests
		for quest in self.player.ownQuests(simulation):
			if quest.questType == CityStateQuestType.triggerInspiration:
				if quest.civicType == civic:
					cityStatePlayer = simulation.cityStatePlayerFor(quest.cityState)
					cityStatePlayer.fulfillQuestBy(self.player.leader, simulation)

		# trigger event to user
		if self.player.isHuman():
			simulation.userInterface.showPopup(PopupType.inspirationTriggered, civic=civic)

		return

	def changeInspirationValueFor(self, civic: CivicType, change: int):
		self._inspirations.triggerIncreaseFor(civic, change)

	def inspirationValueOf(self, civic: CivicType) -> int:
		return self._inspirations.triggerCountFor(civic)

	def numberOfDiscoveredCivics(self) -> int:
		return len(self._civics)

	def addCulture(self, cultureVal: float):
		if self._currentCivicValue is not None:
			self._progresses.addWeight(cultureVal, self._currentCivicValue)

		self._lastCultureEarnedValue = cultureVal

	def checkCultureProgress(self, simulation):
		if self._currentCivicValue is None:
			if not self.player.isHuman():
				bestCivic = self.chooseNextCivic()
				self.setCurrentCivic(bestCivic, simulation)

			return

		if self.currentCultureProgress() >= float(self._currentCivicValue.cost()):
			self.discover(self._currentCivicValue, simulation)

			# trigger event to user
			if self.player.isHuman():
				simulation.userInterface.showPopup(PopupType.civicDiscovered, civic=self._currentCivicValue)

			# enter era
			if self._currentCivicValue.era() > self.player.currentEra():
				simulation.enterEra(self._currentCivicValue.era(), self.player)
				self.player.setEra(self._currentCivicValue.era(), simulation)

				if self.player.isHuman():
					simulation.userInterface.showPopup(PopupType.eraEntered, era=self._currentCivicValue.era())

			self._currentCivicValue = None

			if self.player.isHuman():
				self.player.notifications.addNotification(NotificationType.civicNeeded)

			self.player.setCanChangeGovernmentTo(True)

		return

	def chooseNextCivic(self) -> CivicType:
		weightedCivics: WeightedCivicList = WeightedCivicList()
		possibleCivicsList = self.possibleCivics()

		weightedCivics.removeAll()

		for possibleCivic in possibleCivicsList:
			weightByFlavor = 0.0

			# weight of current tech
			for flavor in list(FlavorType):
				weightByFlavor += self.flavorWeightedOf(possibleCivic, flavor)

			# add techs that can be research with this tech, but only with a little less weight
			for activatedCivic in possibleCivic.leadsTo():
				for flavor in list(FlavorType):
					weightByFlavor += self.flavorWeightedOf(activatedCivic, flavor) * 0.75

				for secondActivatedCivic in activatedCivic.leadsTo():
					for flavor in list(FlavorType):
						weightByFlavor += self.flavorWeightedOf(secondActivatedCivic, flavor) * 0.5

					for thirdActivatedCivic in secondActivatedCivic.leadsTo():
						for flavor in list(FlavorType):
							weightByFlavor += self.flavorWeightedOf(thirdActivatedCivic, flavor) * 0.25

			# revalue based on cost / number of turns
			numberOfTurnsLeft = self.turnsRemainingFor(possibleCivic)
			additionalTurnCostFactor = 0.015 * float(numberOfTurnsLeft)
			totalCostFactor = 0.15 + additionalTurnCostFactor
			weightDivisor = pow(float(numberOfTurnsLeft), totalCostFactor)

			# modify weight
			weightByFlavor = float(weightByFlavor) / weightDivisor

			weightedCivics.addWeight(weightByFlavor, possibleCivic)

		# select one
		selectedCivic = weightedCivics.chooseFromTopChoices()
		if selectedCivic is not None:
			return selectedCivic

		raise Exception("cant get civic - not gonna happen")

	def flavorWeightedOf(self, civic: CivicType, flavor: FlavorType) -> float:
		return float(civic.flavorValue(flavor) * self.player.leader.flavor(flavor))

	def turnsRemainingFor(self, civic: CivicType) -> int:
		if self._lastCultureEarnedValue > 0.0 :
			cost: float = float(civic.cost())
			remaining = cost - self._progresses.weight(civic)

			return int(remaining / self._lastCultureEarnedValue + 0.5)

		return 1

class DiplomaticPact:
	noDuration = -1
	noStarted = -1

	def __init__(self, duration: int = 25):
		self._duration = duration

		self._enabled = False
		self._turnOfActivation = DiplomaticPact.noStarted

	def isActive(self) -> bool:
		return self._enabled

	def isExpired(self, turn: int) -> bool:
		# it can't expire, when it is not active
		if not self._enabled:
			return False

		# it can't expire, if no duration
		if self._duration == DiplomaticPact.noDuration:
			return False

		return self._turnOfActivation + self._duration <= turn

	def activate(self, turn: int = -1):
		self._enabled = True
		self._turnOfActivation = turn

	def abandon(self):
		self._enabled = False
		self._turnOfActivation = DiplomaticPact.noStarted

	def pactIsActiveSince(self) -> int:
		return self._turnOfActivation


class PlayerProximityType(ExtendedEnum):
	none = -1, 'none'

	far = 0, 'far'
	distant = 1, 'distant'
	close = 2, 'close'
	neighbors = 3, 'neighbors'

	def __new__(cls, value: int, name):
		member = object.__new__(cls)
		member._value = value
		member._name = name
		return member

	def __gt__(self, other):
		if isinstance(other, PlayerProximityType):
			return self._value > other._value

		raise Exception('wrong type to compare to')

	def __ge__(self, other):
		if isinstance(other, PlayerProximityType):
			return self._value >= other._value

		raise Exception('wrong type to compare to')

	def value(self) -> int:
		return self._value


class PlayerWarFaceType(ExtendedEnum):
	none = 'none'

	hostile = 'hostile'  # WAR_FACE_HOSTILE
	neutral = 'neutral'  # WAR_FACE_NEUTRAL
	friendly = 'friendly'  # WAR_FACE_FRIENDLY


class ApproachModifierTypeData:
	def __init__(self, summary: str, initialValue: int, reductionTurns: int, reductionValue: int,
				 hiddenAgenda: Optional[LeaderAgendaType]):
		self.summary = summary
		self.initialValue = initialValue
		self.reductionTurns = reductionTurns
		self.reductionValue = reductionValue
		self.hiddenAgenda = hiddenAgenda


class ApproachModifierType(ExtendedEnum):
	delegation = 'delegation'  # STANDARD_DIPLOMATIC_DELEGATION
	embassy = 'embassy'  # STANDARD_DIPLOMACY_RESIDENT_EMBASSY
	declaredFriend = 'declaredFriend'  # STANDARD_DIPLOMATIC_DECLARED_FRIEND
	denounced = 'denounced'  # STANDARD_DIPLOMATIC_DENOUNCED
	firstImpression = 'firstImpression'  # STANDARD_DIPLOMACY_RANDOM ??
	establishedTradeRoute = 'establishedTradeRoute'  # STANDARD_DIPLOMACY_TRADE_RELATIONS
	nearBorder = 'nearBorder'  # STANDARD_DIPLOMATIC_NEAR_BORDER_WARNING

	def summary(self) -> str:
		return self._data().summary

	def initialValue(self) -> int:
		return self._data().initialValue

	def reductionTurns(self) -> int:
		return self._data().reductionTurns

	def reductionValue(self) -> int:
		return self._data().reductionValue

	def _data(self) -> ApproachModifierTypeData:
		if self == ApproachModifierType.delegation:
			return ApproachModifierTypeData(
				summary="TXT_KEY_DIPLOMACY_MODIFIER_DELEGATION",
				initialValue=3,
				reductionTurns=-1,
				reductionValue=0,
				hiddenAgenda=None
			)
		if self == ApproachModifierType.embassy:
			return ApproachModifierTypeData(
				summary="TXT_KEY_DIPLOMACY_MODIFIER_RESIDENT_EMBASSY",
				initialValue=5,
				reductionTurns=-1,
				reductionValue=0,
				hiddenAgenda=None
			)
		if self == ApproachModifierType.declaredFriend:
			return ApproachModifierTypeData(
				summary="TXT_KEY_DIPLOMACY_MODIFIER_DECLARED_FRIEND",
				initialValue=-9,
				reductionTurns=10,
				reductionValue=-1,
				hiddenAgenda=None
			)
		if self == ApproachModifierType.denounced:
			return ApproachModifierTypeData(
				summary="TXT_KEY_DIPLOMACY_MODIFIER_DENOUNCED",
				initialValue=-9,
				reductionTurns=10,
				reductionValue=-1,
				hiddenAgenda=None
			)
		if self == ApproachModifierType.firstImpression:
			return ApproachModifierTypeData(
				summary="TXT_KEY_DIPLOMACY_MODIFIER_FIRST_IMPRESSION",
				initialValue=0,  # overriden
				reductionTurns=10,
				reductionValue=-1,  # overriden
				hiddenAgenda=None
			)
		if self == ApproachModifierType.establishedTradeRoute:
			return ApproachModifierTypeData(
				summary="TXT_KEY_DIPLOMACY_MODIFIER_ESTABLISHED_TRADE_ROUTE",
				initialValue=2,
				reductionTurns=1,
				reductionValue=-1,
				hiddenAgenda=None
			)
		if self == ApproachModifierType.nearBorder:
			return ApproachModifierTypeData(
				summary="TXT_KEY_DIPLOMACY_MODIFIER_NEAR_BORDER_WARNING",
				initialValue=-2,
				reductionTurns=20,
				reductionValue=-1,
				hiddenAgenda=None
			)

		raise InvalidEnumError(self)


class DiplomaticAIPlayerApproachItem:
	def __init__(self, approachModifierType: ApproachModifierType, initialValue: Optional[int] = None,
				 reductionValue: Optional[int] = None):
		self.approachModifierType = approachModifierType

		if initialValue is not None:
			self.value = initialValue
		else:
			self.value = approachModifierType.initialValue()

		self.remainingTurn = approachModifierType.reductionTurns()

		if reductionValue is not None:
			self.reductionValue = reductionValue
		else:
			self.reductionValue = approachModifierType.reductionValue()

		self.expiredValue = False


class DiplomaticPlayerArrayItem:
	def __init__(self, leader: LeaderType, cityState: CityStateType, value, counter: int):
		self.leader: LeaderType = leader
		self.cityState: CityStateType = cityState
		self.value = value  # CoopWarStateType or bool
		self.counter = counter


class DiplomaticPlayerArray:
	def __init__(self):
		self._items = []

	def _agreementAgainst(self, leader: LeaderType, cityState: CityStateType) -> Optional[DiplomaticPlayerArrayItem]:
		return next((item for item in self._items if item.leader == leader and item.cityState == cityState), None)

	def agreementAgainst(self, otherPlayer) -> Optional[DiplomaticPlayerArrayItem]:
		otherLeader = otherPlayer.leader
		otherCityState: CityStateType = otherPlayer.cityState
		return self._agreementAgainst(otherLeader, otherCityState)

	def _hasAgreementAgainst(self, leader: LeaderType, cityState: CityStateType) -> bool:
		return self._agreementAgainst(leader, cityState) is not None

	def hasAgreementAgainst(self, otherPlayer) -> bool:
		otherLeader = otherPlayer.leader
		otherCityState: CityStateType = otherPlayer.cityState
		return self._hasAgreementAgainst(otherLeader, otherCityState)

	def addAgreementAgainst(self, otherPlayer, value, counter: int):
		otherLeader = otherPlayer.leader
		otherCityState: CityStateType = otherPlayer.cityState
		self._items.append(DiplomaticPlayerArrayItem(otherLeader, otherCityState, value, counter))


class DiplomaticAIPlayerItem:
	def __init__(self, leader: LeaderType, cityState: CityStateType, turnOfFirstContact: int):
		self.leader: LeaderType = leader
		self.cityState: CityStateType = cityState
		self.turnOfFirstContact: int = turnOfFirstContact
		self.accessLevel: AccessLevel = AccessLevel.none
		self.gossipItems = []
		self.majorCivOpinion: MajorCivOpinionType = MajorCivOpinionType.none
		self.militaryStrengthComparedToUs: StrengthType = StrengthType.average
		self.militaryThreat: MilitaryThreatType = MilitaryThreatType.none
		self.economicStrengthComparedToUs: StrengthType = StrengthType.average
		self.approachItems = []
		self.approachTowardsUsGuess: MajorPlayerApproachType = MajorPlayerApproachType.none
		self.approachTowardsUsGuessCounter: int = 0

		self.majorApproach: int = 50  # default = neutral
		self.minorApproach: MinorPlayerApproachType = MinorPlayerApproachType.ignore
		self.warFace: PlayerWarFaceType = PlayerWarFaceType.none
		self.warState: PlayerWarStateType = PlayerWarStateType.none
		self.warGoal: WarGoalType = WarGoalType.none
		self.targetValue = PlayerTargetValueType.none
		self.warDamageLevel: WarDamageLevelType = WarDamageLevelType.none
		self.warProjection: WarProjectionType = WarProjectionType.unknown
		self.lastWarProjection: WarProjectionType = WarProjectionType.unknown
		self.warValueLost: int = 0
		self.warWeariness: int = 0
		self.otherPlayerWarmongerAmount: int = 0
		self.otherPlayerNumberOfMinorsAttacked: int = 0
		self.otherPlayerNumberOfMinorsConquered: int = 0
		self.otherPlayerNumberOfMajorsAttacked: int = 0
		self.otherPlayerNumberOfMajorsConquered: int = 0
		self.otherPlayerTurnsSinceKilledProtectedMinor: int = 0
		self.otherPlayerProtectedMinorKilled = None
		self.otherPlayerNumberOfProtectedMinorsKilled: int = 0
		self.playerMadeAttackCityStatePromise: bool = False
		self.playerBrokenAttackCityStatePromise: bool = False
		self.warmongerThreatValue: MilitaryThreatType = MilitaryThreatType.none

		self.hasDelegationValue: bool = False
		self.hasEmbassyValue: bool = False

		self.landDisputeLevel: DisputeLevelType = DisputeLevelType.none
		self.lastTurnLandDisputeLevel: DisputeLevelType = DisputeLevelType.none
		self.wonderDisputeLevel: DisputeLevelType = DisputeLevelType.none
		self.victoryDisputeLevel: DisputeLevelType = DisputeLevelType.none
		self.minorCivDisputeLevel: DisputeLevelType = DisputeLevelType.none

		self.militaryAggressivePosture: AggressivePostureType = AggressivePostureType.none
		self.lastTurnMilitaryAggressivePosture: AggressivePostureType = AggressivePostureType.none
		self.expansionAggressivePosture: AggressivePostureType = AggressivePostureType.none
		self.plotBuyingAggressivePosture: AggressivePostureType = AggressivePostureType.none

		# pacts
		self.declarationOfWar = DiplomaticPact()
		self.declarationOfFriendship = DiplomaticPact()
		self.openBorderAgreement = DiplomaticPact(duration=15)  # has a runtime of 15 turns
		self.defensivePact = DiplomaticPact(duration=15)  # has a runtime of 15 turns
		self.peaceTreaty = DiplomaticPact(duration=15)  # has a runtime of 15 turns
		self.alliance = DiplomaticPact()
		self.researchAgreement = DiplomaticPact()

		# deals
		self.deals: [DiplomaticDeal] = []  # fixme: peaceTreaty alredy included here?

		self.isDenounced: bool = False  # this player has been denounced by us
		self.isRecklessExpander: bool = False
		self.isForcePeace: bool = False

		self.proximity: PlayerProximityType = PlayerProximityType.none

		# counter
		self.turnOfWarDeclaration: int = 0
		self.recentTradeValue: int = 0
		self.numberOfWondersBeaten: int = 0

		self.turnOfLastMeeting: int = -1
		self.numTurnsLockedIntoWar: int = 0
		self.wantPeaceCounter: int = 0
		self.resurrectedOnTurn: int = -1  # in which turn have we been resurrected by this other player (-1 = never)
		self.musteringForAttack: bool = False
		self.wantResearchAgreement: bool = False

		# agreements
		self.coopAgreements = DiplomaticPlayerArray()
		self.workingAgainstAgreements = DiplomaticPlayerArray()

		# peace treaty willingness
		self.peaceTreatyWillingToOffer: PeaceTreatyType = PeaceTreatyType.none
		self.peaceTreatyWillingToAccept: PeaceTreatyType = PeaceTreatyType.none

		# statement log
		self.proposedStatements: [StatementLogEntry] = []


class DiplomaticAIPlayersItem:
	"""class that stores data that belong to/references one other player"""
	def __init__(self, fromPlayer, toPlayer):
		self.fromLeader = fromPlayer.leader
		self.fromCityState = fromPlayer.cityState
		self.toLeader = toPlayer.leader
		self.toCityState = toPlayer.cityState

		self.warValueLost: int = 0
		self.warDamageLevel: WarDamageLevelType = WarDamageLevelType.none
		self.landDisputeLevel: DisputeLevelType = DisputeLevelType.none
		self.victoryDisputeLevel: DisputeLevelType = DisputeLevelType.none
		self.militaryThreat: MilitaryThreatType = MilitaryThreatType.none
		self.opinion: MajorCivOpinionType = MajorCivOpinionType.none


def randomPersonalityWeight(originalValue: int) -> int:
	minValue: int = 0
	maxValue: int = 20
	plusMinus: int = 2

	adjust: int = plusMinus + 1 if Tests.are_running else random.randint(0, plusMinus * 2 + 1)
	rtnValue: int = originalValue + adjust - plusMinus

	if rtnValue < minValue:
		rtnValue = minValue
	elif rtnValue > maxValue:
		rtnValue = maxValue

	return rtnValue


class StatementLogEntry:
	def __init__(self, statement: DiplomaticStatementType, turn: int):
		self.statement: DiplomaticStatementType = statement
		self.turn: int = turn


class DiplomaticPlayerDict:
	def __init__(self):
		self.items: [DiplomaticAIPlayerItem] = []
		self.itemsOther: [DiplomaticAIPlayersItem] = []

		self._personalityMajorCivApproachBiases = WeightedBaseList()
		self._personalityMinorCivApproachBiases = WeightedBaseList()

		self._victoryCompetitiveness: int = 0
		self._wonderCompetitiveness: int = 0
		self._minorCivCompetitiveness: int = 0
		self._boldness: int = 0
		self._diplomaticBalance: int = 0
		self._warmongerHate: int = 0
		self._denounceWillingness: int = 0
		self._declarationOfFriendshipWillingness: int = 0
		self._loyalty: int = 0
		self._neediness: int = 0
		self._forgiveness: int = 0
		self._chattiness: int = 0
		self._meanness: int = 0

	def doInitializePersonality(self, player):
		"""Initializes Personality Members for this player (XML value + random element)"""
		if player.isHuman():
			for approach in MajorPlayerApproachType.all():
				self._personalityMajorCivApproachBiases.setWeight(5, approach)  # DEFAULT_FLAVOR_VALUE

			for approach in MinorPlayerApproachType.all():
				self._personalityMinorCivApproachBiases.setWeight(5, approach)  # DEFAULT_FLAVOR_VALUE

			self._victoryCompetitiveness = 5
			self._wonderCompetitiveness = 5
			self._minorCivCompetitiveness = 5
			self._boldness = 5
			self._diplomaticBalance = 5
			self._warmongerHate = 5
			self._denounceWillingness = 5
			self._declarationOfFriendshipWillingness = 5
			self._loyalty = 5
			self._neediness = 5
			self._forgiveness = 5
			self._chattiness = 5
			self._meanness = 5
		else:
			for approach in MajorPlayerApproachType.all():
				value = player.leader.majorCivApproachBiasTowards(approach)
				self._personalityMajorCivApproachBiases.setWeight(value, approach)

			for approach in MinorPlayerApproachType.all():
				value = player.leader.minorCivApproachBiasTowards(approach)
				self._personalityMinorCivApproachBiases.setWeight(value, approach)

			self._victoryCompetitiveness = randomPersonalityWeight(player.leader.victoryCompetitiveness())
			self._wonderCompetitiveness = randomPersonalityWeight(player.leader.wonderCompetitiveness())
			self._minorCivCompetitiveness = randomPersonalityWeight(player.leader.minorCivCompetitiveness())
			self._boldness = randomPersonalityWeight(player.leader.boldness())
			self._diplomaticBalance = randomPersonalityWeight(player.leader.diplomaticBalance())
			self._warmongerHate = randomPersonalityWeight(player.leader.warmongerHate())
			self._denounceWillingness = randomPersonalityWeight(player.leader.denounceWillingness())
			self._declarationOfFriendshipWillingness = randomPersonalityWeight(player.leader.declarationOfFriendshipWillingness())
			self._loyalty = randomPersonalityWeight(player.leader.loyalty())
			self._neediness = randomPersonalityWeight(player.leader.neediness())
			self._forgiveness = randomPersonalityWeight(player.leader.forgiveness())
			self._chattiness = randomPersonalityWeight(player.leader.chattiness())
			self._meanness = randomPersonalityWeight(player.leader.meanness())

	def victoryCompetitiveness(self) -> int:
		return self._victoryCompetitiveness

	def wonderCompetitiveness(self) -> int:
		return self._wonderCompetitiveness

	def minorCivCompetitiveness(self) -> int:
		return self._minorCivCompetitiveness

	def boldness(self) -> int:
		return self._boldness

	def warmongerHate(self) -> int:
		return self._warmongerHate

	def diplomaticBalance(self) -> int:
		return self._diplomaticBalance

	def warmongerHate(self) -> int:
		return self._warmongerHate

	def denounceWillingness(self) -> int:
		return self._denounceWillingness

	def declarationOfFriendshipWillingness(self) -> int:
		return self._declarationOfFriendshipWillingness

	def loyalty(self) -> int:
		return self._loyalty

	def neediness(self) -> int:
		return self._neediness

	def forgiveness(self) -> int:
		return self._forgiveness

	def chattiness(self) -> int:
		return self._chattiness

	def meanness(self) -> int:
		return self._meanness

	def initContactWith(self, otherPlayer, turn: int):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.turnOfFirstContact = turn
		else:
			otherLeader: LeaderType = otherPlayer.leader
			otherCityState: CityStateType = otherPlayer.cityState
			self.items.append(DiplomaticAIPlayerItem(otherLeader, otherCityState, turnOfFirstContact=turn))

		return
	
	def _itemOf(self, otherPlayer) -> Optional[DiplomaticAIPlayerItem]:
		otherLeader = otherPlayer.leader
		otherCityState: CityStateType = otherPlayer.cityState
		return next((item for item in self.items if item.leader == otherLeader and item.cityState == otherCityState), None)

	def _itemsOfOther(self, fromPlayer, toPlayer) -> Optional[DiplomaticAIPlayersItem]:
		fromLeader = fromPlayer.leader
		fromCityState = fromPlayer.cityState
		toLeader = toPlayer.leader
		toCityState = toPlayer.cityState
		return next((item for item in self.itemsOther if
		             item.fromLeader == fromLeader and item.fromCityState == fromCityState and
		             item.toLeader == toLeader and item.toCityState == toCityState), None)

	def hasMetWith(self, otherPlayer) -> bool:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.turnOfFirstContact != -1

		return False

	def turnOfFirstContactWith(self, otherPlayer) -> int:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.turnOfFirstContact

		return -1

	def updateMilitaryStrengthComparedToUsOf(self, otherPlayer, strength: StrengthType):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.militaryStrengthComparedToUs = strength
			return
			
		raise Exception("not gonna happen")		

	def majorApproachTowards(self, otherPlayer) -> MajorPlayerApproachType:
		value = self.majorApproachValueTowards(otherPlayer)
		return MajorPlayerApproachType.fromValue(value)

	def majorApproachValueTowards(self, otherPlayer) -> int:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.majorApproach

		return 50  # default

	def minorApproachTowards(self, otherPlayer) -> MinorPlayerApproachType:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.minorApproach

		return MinorPlayerApproachType.ignore

	def addApproachOf(self, approachModifierType: ApproachModifierType, initialValue: int, reductionValue: int, otherPlayer):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			approachItem = DiplomaticAIPlayerApproachItem(approachModifierType, initialValue, reductionValue)
			item.approachItems.append(approachItem)
			return

		raise Exception("not gonna happen")

	def militaryThreatOf(self, otherPlayer) -> MilitaryThreatType:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.militaryThreat

		raise Exception("not gonna happen")

	def updateMilitaryThreatOf(self, otherPlayer, militaryThreat: MilitaryThreatType):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.militaryThreat = militaryThreat
			return

		raise Exception("not gonna happen")

	def accessLevelTowards(self, otherPlayer) -> AccessLevel:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.accessLevel

		return AccessLevel.none

	def hasSentDelegationTo(self, otherPlayer) -> bool:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.hasDelegationValue

		return False

	def sendDelegationTo(self, otherPlayer, send: bool=True):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.hasDelegationValue = send
			return

		raise Exception("not gonna happen")

	def hasEstablishedEmbassyTo(self, otherPlayer) -> bool:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.hasEmbassyValue

		return False

	def establishEmbassyTo(self, otherPlayer, send: bool=True):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.hasEmbassyValue = send
			return

		raise Exception("not gonna happen")

	def addApproachTowards(self, otherPlayer, approachModifier: ApproachModifierType, initialValue: Optional[int] = None,
					reductionValue: Optional[int] = None):
		if otherPlayer is None:
			raise Exception('otherPlayer must be filled')

		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			approachItem = DiplomaticAIPlayerApproachItem(
				approachModifierType=approachModifier,
				initialValue=initialValue,
				reductionValue=reductionValue
			)
			item.approachItems.append(approachItem)
			return

		raise Exception("not gonna happen")

	def removeApproachTowards(self, otherPlayer, approachModifier: ApproachModifierType):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.approachItems = list(filter(lambda i: i.approachModifierType != approachModifier, item.approachItems))
			return

		raise Exception("not gonna happen")

	def updateAccessLevelTo(self, accessLevel: AccessLevel, otherPlayer):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.accessLevel = accessLevel
			return

		raise Exception("not gonna happen")

	def isAtWarWith(self, otherPlayer):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.warState != PlayerWarStateType.none

		return False

	def isAtWar(self) -> bool:
		for item in self.items:
			if item.warState != PlayerWarStateType.none:
				return True

		return False

	def declaredWarTowards(self, otherPlayer, turn: int):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.declarationOfWar.activate(turn)
			item.peaceTreaty.abandon()  # just in case
			item.warState = PlayerWarStateType.offensive

			self.updateMajorApproachValueTowards(otherPlayer, MajorPlayerApproachType.war.level())
			self.updateWarStateTowards(otherPlayer, PlayerWarStateType.offensive)  # fixme: duplicate?

			return

		raise Exception("not gonna happen")

	def cancelAllDefensivePacts(self):
		for item in self.items:
			if item.defensivePact.isActive():
				item.defensivePact.abandon()

		return

	def cancelDealsWith(self, otherPlayer):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			# FIXME: inform someone?
			item.deals = []
			return

		raise Exception("not gonna happen")

	def updateMajorApproachValueTowards(self, otherPlayer, value: int):
		if otherPlayer.isBarbarian():
			raise Exception('No major approach towards barbarian')

		if otherPlayer.isCityState():
			raise Exception('No major approach towards city state')

		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.majorApproach = value
			return

		raise Exception("not gonna happen")

	def allPlayersWithDefensivePacts(self) -> [LeaderType]:
		defPlayers: [LeaderType] = []

		for item in self.items:
			if item.defensivePact.isActive():
				defPlayers.append(item.leader)

		return defPlayers

	def updateWarStateTowards(self, otherPlayer, warStateType: PlayerWarStateType):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.warState = warStateType
			return
	
		raise Exception("not gonna happen")

	def isPeaceTreatyActiveWith(self, otherPlayer) -> bool:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.peaceTreaty.isActive()

		return False

	def turnMadePeaceTreatyWith(self, otherPlayer) -> int:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			if item.peaceTreaty.isActive():
				return item.peaceTreaty.pactIsActiveSince()

		return -1

	def addGossipItem(self, gossipItem: GossipItem, otherPlayer):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.gossipItems.append(gossipItem)
			return
	
		raise Exception("not gonna happen")

	def proximityTo(self, otherPlayer) -> PlayerProximityType:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.proximity

		raise Exception("not gonna happen")

	def updateProximityTo(self, otherPlayer, proximity):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.proximity = proximity
			return

		raise Exception("not gonna happen")

	def isOpenBordersAgreementActiveWith(self, otherPlayer) -> bool:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.openBorderAgreement.isActive()

		return False

	def establishOpenBorderAgreementWith(self, otherPlayer, turn: int):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.openBorderAgreement.activate(turn)
			return

		raise Exception('not gonna happen')

	def cancelOpenBorderAgreementWith(self, otherPlayer):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.openBorderAgreement.abandon()
			return

		raise Exception('not gonna happen')

	def otherPlayerWarValueLostFrom(self, fromPlayer, toPlayer) -> int:
		item = self._itemsOfOther(fromPlayer, toPlayer)

		if item is not None:
			return item.warValueLost

		return 0

	def updateOtherPlayerWarValueLostFrom(self, fromPlayer, toPlayer, value: int):
		item: Optional[DiplomaticAIPlayersItem] = self._itemsOfOther(fromPlayer, toPlayer)

		if item is not None:
			item.warValueLost = value
		else:
			newItem = DiplomaticAIPlayersItem(fromPlayer, toPlayer)
			newItem.warValueLost = value
			self.itemsOther.append(newItem)

		return

	def warValueLostWith(self, otherPlayer) -> int:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.warValueLost

		raise Exception('not gonna happen')

	def updateWarValueLostWith(self, otherPlayer, value: int):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.warValueLost = value
			return

		raise Exception('not gonna happen')

	def changeWarWearinessWith(self, otherPlayer, value: int):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.warWeariness = max(item.warWeariness + value, 0)
			return

		raise Exception('not gonna happen')

	def atWarCount(self) -> int:
		return len(list(filter(lambda item: item.warState != PlayerWarStateType.none, self.items)))

	def numberOfTurnsLockedIntoWarWith(self, otherPlayer) -> int:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.numTurnsLockedIntoWar

		raise Exception("not gonna happen")

	def updateNumberOfTurnsLockedIntoWarWith(self, otherPlayer, value: int):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.numTurnsLockedIntoWar = value
			return

		raise Exception("not gonna happen")

	def warStateTowards(self, otherPlayer) -> PlayerWarStateType:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.warState

		raise Exception("not gonna happen")

	def warGoalTowards(self, otherPlayer) -> WarGoalType:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.warGoal

		raise Exception("not gonna happen")

	def militaryStrengthComparedToUsOf(self, otherPlayer) -> StrengthType:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.militaryStrengthComparedToUs

		return StrengthType.average

	def targetValueOf(self, otherPlayer) -> PlayerTargetValueType:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.targetValue

		raise Exception("not gonna happen")

	def landDisputeLevelWith(self, otherPlayer) -> DisputeLevelType:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.landDisputeLevel

		raise Exception("not gonna happen")

	def lastTurnLandDisputeLevelWith(self, otherPlayer) -> DisputeLevelType:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.lastTurnLandDisputeLevel

		raise Exception("not gonna happen")

	def updateLastTurnLandDisputeLevelWith(self, otherPlayer, landDisputeLevel: DisputeLevelType):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.lastTurnLandDisputeLevel = landDisputeLevel
			return

		raise Exception("not gonna happen")

	def expansionAggressivePostureTowards(self, otherPlayer) -> AggressivePostureType:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.expansionAggressivePosture

		raise Exception("not gonna happen")

	def updateExpansionAggressivePosture(self, otherPlayer, aggressivePosture: AggressivePostureType):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.expansionAggressivePosture = aggressivePosture
			return

		raise Exception("not gonna happen")

	def plotBuyingAggressivePostureTowards(self, otherPlayer) -> AggressivePostureType:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.plotBuyingAggressivePosture

		raise Exception("not gonna happen")

	def updateLandDisputeLevelWith(self, otherPlayer, landDisputeLevel: DisputeLevelType):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.landDisputeLevel = landDisputeLevel
			return

		raise Exception("not gonna happen")

	def updateWarDamageLevelWith(self, otherPlayer, warDamageLevel: WarDamageLevelType):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.warDamageLevel = warDamageLevel
			return

		raise Exception("not gonna happen")

	def updateEconomicStrengthComparedToUs(self, otherPlayer, economicStrengthComparedToUs: StrengthType):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.economicStrengthComparedToUs = economicStrengthComparedToUs
			return

		raise Exception("not gonna happen")

	def economicStrengthComparedToUsOf(self, otherPlayer) -> StrengthType:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.economicStrengthComparedToUs

		raise Exception("not gonna happen")

	def majorCivOpinionOf(self, otherPlayer) -> MajorCivOpinionType:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.majorCivOpinion

		raise Exception("not gonna happen")

	def warFaceWith(self, otherPlayer) -> PlayerWarFaceType:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.warFace

		raise Exception("not gonna happen")

	def updateMajorCivApproachTowards(self, otherPlayer, approach: MajorPlayerApproachType):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.majorApproach = approach.level()
			return

		raise Exception("not gonna happen")

	def updateTreatyWillingToOfferWith(self, otherPlayer, treaty: PeaceTreatyType):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.peaceTreatyWillingToOffer = treaty
			return

		raise Exception("not gonna happen")

	def treatyWillingToOfferWith(self, otherPlayer) -> PeaceTreatyType:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.peaceTreatyWillingToOffer

		raise Exception("not gonna happen")

	def updateTreatyWillingToAcceptWith(self, otherPlayer, treaty: PeaceTreatyType):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.peaceTreatyWillingToAccept = treaty
			return

		raise Exception("not gonna happen")

	def treatyWillingToAcceptWith(self, otherPlayer) -> PeaceTreatyType:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.peaceTreatyWillingToAccept

		raise Exception("not gonna happen")

	def warProjectionAgainst(self, otherPlayer) -> WarProjectionType:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.warProjection

		raise Exception(f"not gonna happen")

	def updateWarProjectionAgainst(self, otherPlayer, warProjection: WarProjectionType):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.warProjection = warProjection
			return

		raise Exception(f"not gonna happen")

	def updateLastWarProjectionAgainst(self, otherPlayer, warProjection: WarProjectionType):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.lastWarProjection = warProjection
			return

		raise Exception(f"not gonna happen")

	def warDamageLevelFrom(self, otherPlayer) -> WarDamageLevelType:
		"""How much damage have we taken in a war against a particular Player?"""
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.warDamageLevel

		raise Exception("not gonna happen")

	def updateMinorCivApproachTowards(self, otherPlayer, approach: MinorPlayerApproachType):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.minorApproach = approach
			return

		raise Exception("not gonna happen")

	def updateTargetValueOf(self, otherPlayer, targetValue: PlayerTargetValueType):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.targetValue = targetValue
			return

		raise Exception("not gonna happen")

	def turnsOfWarWith(self, otherPlayer, turn: int) -> int:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return turn - item.turnOfWarDeclaration

		raise Exception("not gonna happen")

	def turnsSinceMeetingWith(self, otherPlayer) -> int:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.turnOfLastMeeting

		raise Exception("not gonna happen")

	def militaryAggressivePostureOf(self, otherPlayer) -> AggressivePostureType:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.militaryAggressivePosture

		raise Exception("not gonna happen")

	def lastTurnMilitaryAggressivePosture(self, otherPlayer) -> AggressivePostureType:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.lastTurnMilitaryAggressivePosture

		raise Exception("not gonna happen")

	def updateLastTurnMilitaryAggressivePostureOf(self, otherPlayer, posture: AggressivePostureType):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.lastTurnMilitaryAggressivePosture = posture
			return

		raise Exception("not gonna happen")

	def updateMilitaryAggressivePosture(self, otherPlayer, posture: AggressivePostureType):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.militaryAggressivePosture = posture
			return

		raise Exception("not gonna happen")

	def isDeclarationOfFriendshipActiveWith(self, otherPlayer) -> bool:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.declarationOfFriendship.isActive()

		raise Exception("not gonna happen")
	
	def signDeclarationOfFriendshipWith(self, otherPlayer, sign: bool, turn: int):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			if sign:
				item.declarationOfFriendship.activate(turn)
			else:
				item.declarationOfFriendship.abandon()
			return

		raise Exception('not gonna happen')

	def isDefensivePactActiveWith(self, otherPlayer):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.defensivePact.isActive()

		raise Exception("not gonna happen")

	def signDefensivePactWith(self, otherPlayer, turn: int):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.defensivePact.activate(turn)
			return

		raise Exception("not gonna happen")

	def cancelDefensivePactWith(self, otherPlayer):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.defensivePact.abandon()
			return

		raise Exception("not gonna happen")

	def changeTurnsAtWarWith(self, otherPlayer, delta: int):
		# not needed
		pass

	def turnsAtWarWith(self, otherPlayer, turn: int) -> int:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			if not item.declarationOfWar.isActive():
				return 0
			else:
				return turn - item.declarationOfWar.pactIsActiveSince()

		raise Exception("not gonna happen")

	def isAlliedWith(self, otherPlayer) -> bool:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.alliance.isActive()

		raise Exception("not gonna happen")

	def updateMajorCivOpinionTowards(self, otherPlayer, opinion: MajorCivOpinionType):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.majorCivOpinion = opinion
			return

		raise Exception("not gonna happen")

	def wonderDisputeLevelWith(self, otherPlayer) -> DisputeLevelType:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.wonderDisputeLevel

		raise Exception("not gonna happen")

	def updateWonderDisputeLevel(self, otherPlayer, disputeLevel: DisputeLevelType):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.wonderDisputeLevel = disputeLevel
			return

		raise Exception("not gonna happen")

	def updateMinorCivDisputeLevelTowards(self, otherPlayer, disputeLevel: DisputeLevelType):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.minorCivDisputeLevel = disputeLevel
			return

		raise Exception("not gonna happen")

	def updateWarFaceWith(self, otherPlayer, warFace: PlayerWarFaceType):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.warFace = warFace
			return

		raise Exception("not gonna happen")

	def numberOfWondersBeatenBy(self, otherPlayer) -> int:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.numberOfWondersBeaten

		raise Exception("not gonna happen")

	def personalityMajorCivApproachBias(self, approach: MajorPlayerApproachType) -> int:
		return int(self._personalityMajorCivApproachBiases.weight(approach))

	def minorCivDisputeLevelWith(self, otherPlayer) -> DisputeLevelType:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.minorCivDisputeLevel

		raise Exception("not gonna happen")

	def otherPlayerWarmongerAmountTowards(self, otherPlayer) -> int:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.otherPlayerWarmongerAmount

		raise Exception("not gonna happen")

	def warmongerThreatOf(self, otherPlayer) -> MilitaryThreatType:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.warmongerThreatValue

		raise Exception("not gonna happen")

	def updateVictoryDisputeLevel(self, otherPlayer, disputeLevel: DisputeLevelType):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.victoryDisputeLevel = disputeLevel
			return

		raise Exception("not gonna happen")

	def isDenouncedPlayer(self, otherPlayer) -> bool:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.isDenounced

		raise Exception("not gonna happen")

	def updatePlotBuyingAggressivePosture(self, otherPlayer, posture: AggressivePostureType):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.plotBuyingAggressivePosture = posture
			return

		raise Exception("not gonna happen")

	def updateCoopWarAcceptedState(self, treatyPlayer, otherPlayer, coopWarState: CoopWarStateType):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(treatyPlayer)

		if item is not None:
			agreement: Optional[DiplomaticPlayerArrayItem] = item.coopAgreements.agreementAgainst(otherPlayer)
			if agreement is not None:
				agreement.value = coopWarState
			else:
				item.coopAgreements.addAgreementAgainst(otherPlayer, coopWarState, 0)

			return

		raise Exception("not gonna happen")

	def isMusteringForAttackAgainst(self, otherPlayer) -> bool:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.musteringForAttack

		raise Exception("not gonna happen")

	def updateMusteringForAttackAgainst(self, otherPlayer, value: bool):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.musteringForAttack = value
			return

		raise Exception("not gonna happen")

	def updateWarGoalTowards(self, otherPlayer, warGoal: WarGoalType):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.warGoal = warGoal
			return

		raise Exception("not gonna happen")

	def coopWarCounterWith(self, treatyPlayer, otherPlayer) -> int:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(treatyPlayer)

		if item is not None:
			agreement: Optional[DiplomaticPlayerArrayItem] = item.coopAgreements.agreementAgainst(otherPlayer)
			if agreement is not None:
				return agreement.counter
			else:
				return -1

		raise Exception("not gonna happen")

	def updateCoopWarCounterWith(self, treatyPlayer, otherPlayer, value: int):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(treatyPlayer)

		if item is not None:
			agreement: Optional[DiplomaticPlayerArrayItem] = item.coopAgreements.agreementAgainst(otherPlayer)
			if agreement is not None:
				agreement.counter = value
			else:
				raise Exception("Cannot update coop war counter when no agreement exists")

		raise Exception("not gonna happen")

	def coopWarAcceptedStateOf(self, treatyPlayer, otherPlayer) -> CoopWarStateType:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(treatyPlayer)

		if item is not None:
			agreement: Optional[DiplomaticPlayerArrayItem] = item.coopAgreements.agreementAgainst(otherPlayer)
			if agreement is not None:
				return agreement.value
			else:
				return CoopWarStateType.none

		raise Exception("not gonna happen")

	def doAddNewStatementToDiploLog(self, otherPlayer, statement: DiplomaticStatementType, turn: int):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.proposedStatements.append(StatementLogEntry(statement, turn))
			return

		raise Exception("not gonna happen")

	def numberOfTurnsSinceStatementSent(self, otherPlayer, statement: DiplomaticStatementType) -> int:
		lastTurnOfStatement: int = 9999
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			for statementLogEntry in item.proposedStatements:
				if statementLogEntry.statement == statement:
					lastTurnOfStatement = min(lastTurnOfStatement, statementLogEntry.turn)

			return lastTurnOfStatement

		return 9999

	def wantPeaceCounterWith(self, otherPlayer) -> int:
		"""How long have we had our current War Goal with otherPlayer?"""
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.wantPeaceCounter

		raise Exception("not gonna happen")

	def updateWantPeaceCounterWith(self, otherPlayer, value: int):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.wantPeaceCounter = value
			return

		raise Exception("not gonna happen")

	def changeWantPeaceCounterWith(self, otherPlayer, delta: int):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.wantPeaceCounter += delta
			return

		raise Exception("not gonna happen")

	def resurrectedOnTurnBy(self, otherPlayer) -> int:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.resurrectedOnTurn

		raise Exception("not gonna happen")

	def isWantsResearchAgreementWith(self, otherPlayer) -> bool:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.wantResearchAgreement

		raise Exception("not gonna happen")

	def updateWantsResearchAgreementWith(self, otherPlayer, value: bool):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.wantResearchAgreement = value
			return

		raise Exception("not gonna happen")

	def updateOtherPlayerWarDamageLevelBetween(self, fromPlayer, toPlayer, warDamageLevel: WarDamageLevelType):
		item: Optional[DiplomaticAIPlayersItem] = self._itemsOfOther(fromPlayer, toPlayer)

		if item is not None:
			item.warDamageLevel = warDamageLevel
		else:
			newItem = DiplomaticAIPlayersItem(fromPlayer, toPlayer)
			newItem.warDamageLevel = warDamageLevel
			self.itemsOther.append(newItem)

	def otherPlayerWarDamageLevelBetween(self, fromPlayer, toPlayer) -> WarDamageLevelType:
		item: Optional[DiplomaticAIPlayersItem] = self._itemsOfOther(fromPlayer, toPlayer)

		if item is not None:
			return item.warDamageLevel

		return WarDamageLevelType.none

	def updateEstimateOtherPlayerLandDisputeLevelBetween(self, fromPlayer, toPlayer, disputeLevel: DisputeLevelType):
		item: Optional[DiplomaticAIPlayersItem] = self._itemsOfOther(fromPlayer, toPlayer)

		if item is not None:
			item.landDisputeLevel = disputeLevel
		else:
			newItem = DiplomaticAIPlayersItem(fromPlayer, toPlayer)
			newItem.landDisputeLevel = disputeLevel
			self.itemsOther.append(newItem)

	def estimateOtherPlayerLandDisputeLevelBetween(self, fromPlayer, toPlayer) -> DisputeLevelType:
		item: Optional[DiplomaticAIPlayersItem] = self._itemsOfOther(fromPlayer, toPlayer)

		if item is not None:
			return item.landDisputeLevel

		return DisputeLevelType.none

	def updateEstimateOtherPlayerVictoryDisputeLevelBetween(self, fromPlayer, toPlayer, disputeLevel: DisputeLevelType):
		item: Optional[DiplomaticAIPlayersItem] = self._itemsOfOther(fromPlayer, toPlayer)

		if item is not None:
			item.victoryDisputeLevel = disputeLevel
		else:
			newItem = DiplomaticAIPlayersItem(fromPlayer, toPlayer)
			newItem.victoryDisputeLevel = disputeLevel
			self.itemsOther.append(newItem)

	def estimateOtherPlayerVictoryDisputeLevelBetween(self, fromPlayer, toPlayer) -> DisputeLevelType:
		item: Optional[DiplomaticAIPlayersItem] = self._itemsOfOther(fromPlayer, toPlayer)

		if item is not None:
			return item.victoryDisputeLevel

		return DisputeLevelType.none

	def updateEstimateOtherPlayerMilitaryThreatBetween(self, fromPlayer, toPlayer, militaryThreat: MilitaryThreatType):
		item: Optional[DiplomaticAIPlayersItem] = self._itemsOfOther(fromPlayer, toPlayer)

		if item is not None:
			item.militaryThreat = militaryThreat
		else:
			newItem = DiplomaticAIPlayersItem(fromPlayer, toPlayer)
			newItem.militaryThreat = militaryThreat
			self.itemsOther.append(newItem)

	def updateMajorCivOtherPlayerOpinionBetween(self, fromPlayer, toPlayer, opinion: MajorCivOpinionType):
		item: Optional[DiplomaticAIPlayersItem] = self._itemsOfOther(fromPlayer, toPlayer)

		if item is not None:
			item.opinion = opinion
		else:
			newItem = DiplomaticAIPlayersItem(fromPlayer, toPlayer)
			newItem.militaryThreat = opinion
			self.itemsOther.append(newItem)

	def otherPlayerNumberOfMinorsAttackedBy(self, otherPlayer) -> int:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.otherPlayerNumberOfMinorsAttacked

		raise Exception("not gonna happen")

	def otherPlayerNumberOfMinorsConqueredBy(self, otherPlayer) -> int:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.otherPlayerNumberOfMinorsConquered

		raise Exception("not gonna happen")

	def otherPlayerNumberOfMajorsAttackedBy(self, otherPlayer) -> int:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.otherPlayerNumberOfMajorsAttacked

		raise Exception("not gonna happen")

	def otherPlayerNumberOfMajorsConqueredBy(self, otherPlayer) -> int:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.otherPlayerNumberOfMajorsConquered

		raise Exception("not gonna happen")

	def updateWarmongerThreatBy(self, otherPlayer, threatType: MilitaryThreatType):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.warmongerThreatValue = threatType
			return

		raise Exception("not gonna happen")

	def changeOtherPlayerWarmongerAmount(self, otherPlayer, delta: int):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.otherPlayerWarmongerAmount += delta
			return

		raise Exception("not gonna happen")

	def approachTowardsUsGuessOf(self, otherPlayer) -> MajorPlayerApproachType:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.approachTowardsUsGuess

		raise Exception("not gonna happen")

	def updateApproachTowardsUsGuessOf(self, otherPlayer, approach: MajorPlayerApproachType):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.approachTowardsUsGuess = approach
			return

		raise Exception("not gonna happen")

	def changeApproachTowardsUsGuessCounterOf(self, otherPlayer, delta: int):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.approachTowardsUsGuessCounter += delta
			return

		raise Exception("not gonna happen")

	def updateApproachTowardsUsGuessCounterOf(self, otherPlayer, value: int):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.approachTowardsUsGuessCounter = value
			return

		raise Exception("not gonna happen")

	def approachTowardsUsGuessCounterOf(self, otherPlayer) -> int:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.approachTowardsUsGuessCounter

		raise Exception("not gonna happen")

	def isHasResearchAgreementWith(self, otherPlayer) -> bool:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.researchAgreement.isActive()

		raise Exception("not gonna happen")

	def cancelResearchAgreementWith(self, otherPlayer):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.researchAgreement.abandon()

		raise Exception("not gonna happen")

	def changeOtherPlayerNumberOfMajorsConqueredBy(self, otherPlayer, delta: int):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.otherPlayerNumberOfMajorsConquered += delta
			return

		raise Exception("not gonna happen")

	def changeOtherPlayerNumberOfMinorsConqueredBy(self, otherPlayer, delta: int):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.otherPlayerNumberOfMinorsConquered += delta
			return

		raise Exception("not gonna happen")

	def isForcePeaceWith(self, otherPlayer) -> bool:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.isForcePeace

		raise Exception("not gonna happen")

	def updateForcePeaceWith(self, otherPlayer, value: bool):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.isForcePeace = value
			return

		raise Exception("not gonna happen")

	def updateOtherPlayerTurnsSinceKilledProtectedMinorBy(self, otherPlayer, value: int):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.otherPlayerTurnsSinceKilledProtectedMinor = value
			return

		raise Exception("not gonna happen")

	def updateOtherPlayerProtectedMinorKilledBy(self, otherPlayer, deadPlayer):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.otherPlayerProtectedMinorKilled = deadPlayer
			return

		raise Exception("not gonna happen")

	def changeOtherPlayerNumberOfProtectedMinorsKilledBy(self, otherPlayer, delta: int):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.otherPlayerNumberOfProtectedMinorsKilled += delta
			return

		raise Exception("not gonna happen")

	def isPlayerMadeAttackCityStatePromiseBy(self, otherPlayer) -> bool:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.playerMadeAttackCityStatePromise

		raise Exception("not gonna happen")

	def updatePlayerBrokenAttackCityStatePromiseBy(self, otherPlayer, value: bool):
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			item.playerBrokenAttackCityStatePromise = value
			return

		raise Exception("not gonna happen")

	def isPlayerBrokenAttackCityStatePromise(self, otherPlayer) -> bool:
		item: Optional[DiplomaticAIPlayerItem] = self._itemOf(otherPlayer)

		if item is not None:
			return item.playerBrokenAttackCityStatePromise

		raise Exception("not gonna happen")


class DiplomaticAI:
	def __init__(self, player):
		self.playerDict = DiplomaticPlayerDict()
		self.playerDict.doInitializePersonality(player)
		self._stateOfAllWars: PlayerStateAllWars = PlayerStateAllWars.neutral
		self.player = player
		self.greetPlayers = []

		self._hasBrokenPeaceTreatyValue: bool = False
		self._earlyGameHiddenAgendaVal: Optional[LeaderAgendaType] = None
		self._lateGameHiddenAgendaVal: Optional[LeaderAgendaType] = None
		self._demandTargetPlayer = None
		self._demandReady: bool = False

		# helper
		self._paeApproachScratchPad = WeightedBaseList()
		self._paDiploLogStatementTurnCountScratchPad = WeightedBaseList()
		self._paiPersonalityMinorCivApproachBiases = WeightedBaseList()

	def doTurn(self, simulation):
		# Military Stuff
		self.doLockedIntoWarDecay(simulation)
		self.doWarDamageDecay(simulation)
		self.doUpdateWarDamageLevel(simulation)
		self.updateMilitaryStrengths(simulation)
		self.updateEconomicStrengths(simulation)

		self.doUpdateWarmongerThreats(simulation)
		self.updateMilitaryThreats(simulation)
		self.updatePlayerTargetValues(simulation)  # DoUpdatePlayerTargetValues
		self.updateWarStates(simulation)
		self.doUpdateWarProjections(simulation)
		self.doUpdateWarGoals(simulation)

		self.doUpdatePeaceTreatyWillingness(simulation)

		# Issues of Dispute
		self.doUpdateLandDisputeLevels(simulation)
		self.doUpdateVictoryDisputeLevels(simulation)
		self.doUpdateWonderDisputeLevels(simulation)
		self.doUpdateMinorCivDisputeLevels(simulation)

		# Has any player gone back on any promises he made?
		# DoTestPromises()

		# What we think other Players are up to
		self.doUpdateOtherPlayerWarDamageLevel(simulation)
		self.doUpdateEstimateOtherPlayerLandDisputeLevels(simulation)
		self.doUpdateEstimateOtherPlayerVictoryDisputeLevels(simulation)
		self.doUpdateEstimateOtherPlayerMilitaryThreats(simulation)
		self.doEstimateOtherPlayerOpinions(simulation)
		# LogOtherPlayerGuessStatus()

		# Look at the situation
		self.doUpdateMilitaryAggressivePostures(simulation)
		self.doUpdateExpansionAggressivePostures(simulation)
		self.doUpdatePlotBuyingAggressivePosture(simulation)

		# Player Opinion & Approach
		self.doUpdateApproachTowardsUsGuesses(simulation)

		self.doHiddenAgenda(simulation)
		self.updateOpinions(simulation)
		self.updateMajorCivApproaches(simulation)
		self.updateMinorCivApproaches(simulation)

		self.updateProximities(simulation)

		# These functions actually DO things, and we don't want the shadow AI behind a human player doing things for him
		if not self.player.isHuman():
			self.doMakeWar(simulation)
			self.doMakePeaceWithMinors(simulation)

			self.doUpdateDemands(simulation)

			self.doUpdatePlanningExchanges(simulation)
			self.doContactMinorCivs(simulation)
			self.doContactMajorCivs(simulation)

		# Update Counters
		self.doCounters(simulation)

	def hasMetWith(self, otherPlayer) -> bool:
		return self.playerDict.hasMetWith(otherPlayer)

	def turnOfFirstContactWith(self, otherPlayer) -> int:
		return self.playerDict.turnOfFirstContactWith(otherPlayer)

	def update(self, simulation):
		activePlayer = simulation.activePlayer()
		if activePlayer is not None:
			# check if activePlayer is in greetPlayers of this player
			if reduce(lambda b0, b1: b0 or b1, list(map(lambda player: activePlayer == player, self.greetPlayers)),
					  False):
				if self.player.isCityState() or activePlayer.isCityState():
					if activePlayer.isHuman() and self.player.isCityState():
						cityState = self.player.cityState
						# is `activePlayer the first major player to meet this city state
						if simulation.countMajorCivilizationsMetWith(cityState) == 1:
							# first player gets a free envoy
							activePlayer.changeUnassignedEnvoysBy(1)

							# this free envoy is assigned to
							activePlayer.assignEnvoyTo(cityState, simulation)

							# inform human player
							activePlayer.notifications.addNotification(
								NotificationType.metCityState,
								cityState=cityState,
								first=True
							)
						else:
							activePlayer.notifications.addNotification(
								NotificationType.metCityState,
								cityState=cityState,
								first=False
							)

						# reveal city state to player
						cityStateCapital = simulation.capitalOf(self.player)
						if cityStateCapital is not None:
							simulation.discoverAt(cityStateCapital.location, sight=3, player=activePlayer)

					elif activePlayer.isCityState() and self.player.isHuman():
						cityState = activePlayer.cityState

						# is ´player´ the first major player to meet this city state
						if simulation.countMajorCivilizationsMetWith(cityState) == 1:
							# first player gets a free envoy
							self.player.changeUnassignedEnvoysBy(1)

							# this free envoy is assigned to
							self.player.assignEnvoyTo(cityState, simulation)

							# inform human player
							self.player.notifications.addNotification(
								NotificationType.metCityState,
								cityState=cityState,
								first=True
							)
						else:
							self.player.notifications.addNotification(
								NotificationType.metCityState,
								cityState=cityState,
								first=False
							)

						# reveal city state to player
						cityStateCapital = simulation.capitalOf(activePlayer)
						if cityStateCapital is not None:
							simulation.discoverAt(cityStateCapital.location, sight=3, player=self.player)
					else:
						self.player.diplomacyRequests.sendRequest(
							activePlayer.leader,
							state=DiplomaticRequestState.intro,
							message=DiplomaticRequestMessage.messageIntro,
							emotion=LeaderEmotionType.intro,
							simulation=simulation
						)

					self.greetPlayers = [item for item in self.greetPlayers if not activePlayer == item]

		return

	def doFirstContactWith(self, otherPlayer, simulation):
		if self.hasMetWith(otherPlayer):
			return

		if self.player.isBarbarian() or otherPlayer.isBarbarian():
			return

		self.playerDict.initContactWith(otherPlayer, simulation.currentTurn)
		self.updateMilitaryStrengthOf(otherPlayer, simulation)

		impression = simulation.handicap.firstImpressionBaseValue() + (0 if Tests.are_running else random.randrange(-3, 3))
		self.playerDict.addApproachOf(ApproachModifierType.firstImpression, impression, 1 if impression > 0 else -1,
									  otherPlayer)

		# Humans don't say hi to ai player automatically
		if not self.player.isHuman():
			# Should fire off a diplo message, when we meet a human
			if otherPlayer.isHuman():
				# Put in the list of people to greet human, when the human turn comes up.
				self.greetPlayers.append(otherPlayer)

			# if self.player.isMajorAI() and otherPlayer.isCityState():
			# 	# is ´player´ the first major player to meet this city state
			# 	if simulation.countMajorCivilizationsMetWith(otherPlayer.cityState) == 1:
			# 		# first player gets a free envoy
			# 		self.player.changeUnassignedEnvoysBy(1)
			#
			# 		# this free envoy is assigned to
			# 		self.player.assignEnvoyTo(otherPlayer.cityState, simulation)
			#
			# 		# inform human player
			# 		self.player.notifications.addNotification(
			# 			NotificationType.metCityState,
			# 			cityState=otherPlayer.cityState,
			# 			first=True
			# 		)
			# 	else:
			# 		self.player.notifications.addNotification(
			# 			NotificationType.metCityState,
			# 			cityState=otherPlayer.cityState,
			# 			first=False
			# 		)
			#
			# 	# reveal city state to player
			# 	cityStateCapital = simulation.capitalOf(otherPlayer)
			# 	if cityStateCapital is not None:
			# 		simulation.discoverAt(cityStateCapital.location, sight=3, player=self.player)

		return

	def doLockedIntoWarDecay(self, simulation):
		for loopPlayer in simulation.players:
			if not loopPlayer.isAlive():
				continue

			if loopPlayer == self.player:
				continue

			if not self.player.hasMetWith(loopPlayer):
				continue

			# decay
			if self.numberOfTurnsLockedIntoWarWith(loopPlayer) > 0:
				self.changeNumberOfTurnsLockedIntoWarWith(loopPlayer, -1)

	def doWarDamageDecay(self, simulation):
		"""Every turn we're at peace war damage goes down a bit"""
		# Loop through all (known) Players
		for loopPlayer in simulation.players:
			if not loopPlayer.isAlive():
				continue

			if loopPlayer == self.player:
				continue

			if not self.player.hasMetWith(loopPlayer):
				continue

			# Update war damage we've suffered
			if not self.isAtWarWith(loopPlayer):
				value = self.warValueLostWith(loopPlayer)

				if value > 0:
					# Go down by 1/20th every turn at peace
					value /= 20

					# Make sure it's changing by at least 1
					value = max(1, value)

					self.changeWarValueLostWith(loopPlayer, -value)

			# Update war damage other players have suffered from our viewpoint
			# /*for(iThirdPlayerLoop = 0 iThirdPlayerLoop < MAX_CIV_PLAYERS iThirdPlayerLoop++)
			# {
			#     eLoopThirdPlayer = (PlayerTypes) iThirdPlayerLoop
			#     eLoopThirdTeam = GET_PLAYER(eLoopThirdPlayer).getTeam()
			#
			#     # These two players not at war?
			#     if(!GET_TEAM(eLoopThirdTeam).isAtWar(eLoopTeam))
			#     {
			#         iValue = GetOtherPlayerWarValueLost(eLoopPlayer, eLoopThirdPlayer)
			#
			#         if(iValue > 0)
			#         {
			#             # Go down by 1/20th every turn at peace
			#             iValue /= 20
			#
			#             # Make sure it's changing by at least 1
			#             iValue = max(1, iValue)
			#
			#             ChangeOtherPlayerWarValueLost(eLoopPlayer, eLoopThirdPlayer, -iValue)
			#         }
			#     }
			# }*/
		return

	def updateMilitaryStrengths(self, simulation):
		for otherPlayer in simulation.players:
			if otherPlayer.leader != self.player.leader and self.player.hasMetWith(otherPlayer):
				self.updateMilitaryStrengthOf(otherPlayer, simulation)

	def updateMilitaryStrengthOf(self, otherPlayer, simulation):
		ownMilitaryStrength = self.player.militaryMight(simulation) + 30
		otherMilitaryStrength = otherPlayer.militaryMight(simulation) + 30
		militaryRatio = otherMilitaryStrength * 100 / ownMilitaryStrength

		if militaryRatio >= 250:
			self.playerDict.updateMilitaryStrengthComparedToUsOf(otherPlayer, StrengthType.immense)
		elif militaryRatio >= 165:
			self.playerDict.updateMilitaryStrengthComparedToUsOf(otherPlayer, StrengthType.powerful)
		elif militaryRatio >= 115:
			self.playerDict.updateMilitaryStrengthComparedToUsOf(otherPlayer, StrengthType.strong)
		elif militaryRatio >= 85:
			self.playerDict.updateMilitaryStrengthComparedToUsOf(otherPlayer, StrengthType.average)
		elif militaryRatio >= 60:
			self.playerDict.updateMilitaryStrengthComparedToUsOf(otherPlayer, StrengthType.poor)
		elif militaryRatio >= 40:
			self.playerDict.updateMilitaryStrengthComparedToUsOf(otherPlayer, StrengthType.weak)
		else:
			self.playerDict.updateMilitaryStrengthComparedToUsOf(otherPlayer, StrengthType.pathetic)

	def militaryThreatOf(self, otherPlayer) -> MilitaryThreatType:
		return self.playerDict.militaryThreatOf(otherPlayer)

	def updateMilitaryThreats(self, simulation):
		ownMilitaryMight = self.player.militaryMight(simulation)

		if ownMilitaryMight == 0:
			ownMilitaryMight = 1

		# Add in City Defensive Strength per city
		for city in simulation.citiesOf(self.player):
			damageFactor = (25.0 - float(city.damage())) / 25.0

			cityStrengthModifier = int(float(city.power(simulation)) * damageFactor)
			cityStrengthModifier *= 33
			cityStrengthModifier /= 100
			cityStrengthModifier /= 10

			ownMilitaryMight += cityStrengthModifier

		# Loop through all(known) Players
		for otherPlayer in simulation.players:
			if otherPlayer.leader != self.player.leader and self.player.hasMetWith(otherPlayer):
				otherMilitaryMight = otherPlayer.militaryMight(simulation)

				# If another player has double the Military strength of us, the Ratio will be 200
				militaryRatio = otherMilitaryMight * 100 / ownMilitaryMight
				militaryThreat = militaryRatio

				# At war: what is the current status of things?
				if self.isAtWarWith(otherPlayer):
					warStateValue = self.warStateTowards(otherPlayer)

					if warStateValue == PlayerWarStateType.none:
						# NOOP
						pass
					elif warStateValue == PlayerWarStateType.nearlyDefeated:
						militaryThreat += 150  # MILITARY_THREAT_WAR_STATE_NEARLY_DEFEATED
					elif warStateValue == PlayerWarStateType.defensive:
						militaryThreat += 80  # MILITARY_THREAT_WAR_STATE_DEFENSIVE
					elif warStateValue == PlayerWarStateType.stalemate:
						militaryThreat += 30  # MILITARY_THREAT_WAR_STATE_STALEMATE
					elif warStateValue == PlayerWarStateType.calm:
						militaryThreat += 0  # MILITARY_THREAT_WAR_STATE_CALM
					elif warStateValue == PlayerWarStateType.offensive:
						militaryThreat += -40  # MILITARY_THREAT_WAR_STATE_OFFENSIVE
					elif warStateValue == PlayerWarStateType.nearlyWon:
						militaryThreat += -100  # MILITARY_THREAT_WAR_STATE_NEARLY_WON

				# Factor in Friends this player has

				# TBD

				# Factor in distance
				proximityValue = self.proximityTo(otherPlayer)

				if proximityValue == PlayerProximityType.none:
					# NOOP
					pass
				elif proximityValue == PlayerProximityType.neighbors:
					militaryThreat += 100  # MILITARY_THREAT_NEIGHBORS
				elif proximityValue == PlayerProximityType.close:
					militaryThreat += 40  # MILITARY_THREAT_CLOSE
				elif proximityValue == PlayerProximityType.far:
					militaryThreat += -40  # MILITARY_THREAT_FAR
				elif proximityValue == PlayerProximityType.distant:
					militaryThreat += -100  # MILITARY_THREAT_DISTANT

				# Don't factor in # of players attacked or at war with now if we ARE at war with this guy already

				# FIXME

				# Now do the final assessment
				if militaryThreat >= 300:
					# MILITARY_THREAT_CRITICAL_THRESHOLD
					self.playerDict.updateMilitaryThreatOf(otherPlayer, MilitaryThreatType.critical)
				elif militaryThreat >= 220:  # MILITARY_THREAT_SEVERE_THRESHOLD
					self.playerDict.updateMilitaryThreatOf(otherPlayer, MilitaryThreatType.severe)
				elif militaryThreat >= 170:  # MILITARY_THREAT_MAJOR_THRESHOLD
					self.playerDict.updateMilitaryThreatOf(otherPlayer, MilitaryThreatType.major)
				elif militaryThreat >= 100:  # MILITARY_THREAT_MINOR_THRESHOLD
					self.playerDict.updateMilitaryThreatOf(otherPlayer, MilitaryThreatType.minor)
				else:
					self.playerDict.updateMilitaryThreatOf(otherPlayer, MilitaryThreatType.none)

		return

	def doUpdateWarmongerThreats(self, simulation):
		"""Updates how much of a threat each player is to run amok and break everything"""
		numPlayersEver: int = simulation.countCivPlayersEverAlive()

		for loopPlayer in simulation.players:
			if not loopPlayer.isHuman() and not loopPlayer.isMajorAI():
				continue

			if not loopPlayer.isAlive():
				continue

			if loopPlayer == self.player:
				continue

			if not self.player.hasMetWith(loopPlayer):
				continue

			threatType: MilitaryThreatType = MilitaryThreatType.none
			threatValue = self.otherPlayerWarmongerScoreWith(loopPlayer)

			# Now do the final assessment
			if threatValue >= 200:  # WARMONGER_THREAT_CRITICAL_THRESHOLD
				threatType = MilitaryThreatType.critical  # THREAT_CRITICAL
			elif threatValue >= 100:  # WARMONGER_THREAT_SEVERE_THRESHOLD
				threatType = MilitaryThreatType.severe  # THREAT_SEVERE
			elif threatValue >= 50:  # WARMONGER_THREAT_MAJOR_THRESHOLD
				threatType = MilitaryThreatType.major  # THREAT_MAJOR
			elif threatValue >= 20:  # WARMONGER_THREAT_MINOR_THRESHOLD
				threatType = MilitaryThreatType.minor  # THREAT_MINOR

			# Also test %of players killed (in case we're on a map with very few players or something)
			numPlayersKilled = self.otherPlayerNumberOfMinorsConqueredBy(loopPlayer) + self.otherPlayerNumberOfMajorsConqueredBy(loopPlayer)
			playersKilledPercent = 0
			if numPlayersKilled > 0:
				playersKilledPercent = numPlayersKilled * 100 / numPlayersEver

			warmongerMod = self.warmongerHate() - 5  # DEFAULT_FLAVOR_VALUE - Calculate difference from default
			warmongerMod *= 10  # WARMONGER_THREAT_PERSONALITY_MOD - This will range from -50 to 50 ( % )
			playersKilledPercent += (playersKilledPercent * warmongerMod / 100)

			if playersKilledPercent >= 40:  # WARMONGER_THREAT_CRITICAL_PERCENT_THRESHOLD
				threatType = MilitaryThreatType.critical  # THREAT_CRITICAL
			if playersKilledPercent >= 25:  # WARMONGER_THREAT_SEVERE_PERCENT_THRESHOLD
				threatType = MilitaryThreatType.severe  # THREAT_SEVERE

			# Set the Threat
			self.playerDict.updateWarmongerThreatBy(loopPlayer, threatType)

			# decay score
			self.playerDict.changeOtherPlayerWarmongerAmount(loopPlayer, -5)  # WARMONGER_THREAT_PER_TURN_DECAY

		return

	def accessLevelTowards(self, otherPlayer) -> AccessLevel:
		return self.playerDict.accessLevelTowards(otherPlayer)

	def doSendDelegationTo(self, otherPlayer, simulation):
		if self.canSendDelegationTo(otherPlayer, simulation):
			self.playerDict.sendDelegationTo(otherPlayer, send=True)
			self.playerDict.addApproachTowards(otherPlayer, ApproachModifierType.delegation)

			# sight capital - our guys are there
			capital = simulation.capitalOf(otherPlayer)
			simulation.sightAt(capital.location, sight=3, player=self.player)

			# update access level
			self.increaseAccessLevelTowards(otherPlayer)

		return

	def canSendDelegationTo(self, otherPlayer, simulation) -> bool:
		# you can only send a delegation, if the `otherPlayer` has a capital
		if simulation.capitalOf(otherPlayer) is None:
			return False

		if self.player.treasury.value() < 25:
			return False

		if self.hasSentDelegationTo(otherPlayer):
			return False

		# Once the Diplomatic Service civic is developed, all your Delegations are revoked and need to be replaced by
		# Resident Embassies (which may lower your relationship temporarily).
		if self.player.civics.hasCivic(CivicType.diplomaticService):
			return False

		# If your relationship with a rival is worse than Neutral they will not accept your delegation/Embassy.
		approach = self.majorApproachTowards(otherPlayer)
		if approach < MajorPlayerApproachType.neutral:
			return False

		return True

	def hasSentDelegationTo(self, otherPlayer):
		return self.playerDict.hasSentDelegationTo(otherPlayer)

	def doRevokeDelegation(self, otherPlayer, simulation):
		playerDiplomacy = self.player.diplomacyAI

		self.playerDict.sendDelegationTo(otherPlayer, send=False)
		self.playerDict.removeApproachTowards(self.player, ApproachModifierType.delegation)

		# conceal capital - our guys are no longer there
		capital = simulation.capitalOf(otherPlayer)
		simulation.conceal(capital.location, sight=3, player=self.player)

		# update access level
		playerDiplomacy.decreaseAccessLevelTowards(otherPlayer)

	def majorApproachTowards(self, otherPlayer) -> MajorPlayerApproachType:
		if otherPlayer.isBarbarian():
			raise Exception('No major approach towards barbarian')

		if otherPlayer.isCityState():
			raise Exception('No major approach towards city state')

		return self.playerDict.majorApproachTowards(otherPlayer)

	def minorApproachTowards(self, otherPlayer) -> MinorPlayerApproachType:
		if otherPlayer.isBarbarian():
			raise Exception('No minor approach towards barbarian')

		if not otherPlayer.isCityState():
			raise Exception('No minor approach towards major civilization')

		return self.playerDict.minorApproachTowards(otherPlayer)

	def increaseAccessLevelTowards(self, otherPlayer):
		currentAccessLevel = self.accessLevelTowards(otherPlayer)
		increasedAccessLevel = currentAccessLevel.increased()
		self.playerDict.updateAccessLevelTo(increasedAccessLevel, otherPlayer)

	def decreaseAccessLevelTowards(self, otherPlayer):
		currentAccessLevel = self.accessLevelTowards(otherPlayer)
		decreasedAccessLevel = currentAccessLevel.decreased()
		self.playerDict.updateAccessLevelTo(decreasedAccessLevel, otherPlayer)

	def doUpdateWarDamageLevel(self, simulation):
		"""Updates how much damage have we taken in a war against all Players"""
		militaryAI = self.player.militaryAI

		# Calculate the value of what we have currently
		# This is invariant, so we will just do it once
		currentValue = 0

		typicalPower = militaryAI.powerOfStrongestBuildableUnit(UnitDomainType.land)

		# City value
		for loopCity in simulation.citiesOf(self.player):
			currentValue += loopCity.population() * 150  # WAR_DAMAGE_LEVEL_INVOLVED_CITY_POP_MULTIPLIER

			if loopCity.isCapital():
				currentValue *= 3
				currentValue /= 2

		# Unit value
		for loopUnit in simulation.unitsOf(self.player):
			unitValue = loopUnit.unitType.power()

			if typicalPower > 0:
				unitValue = unitValue * 100 / typicalPower  # DEFAULT_WAR_VALUE_FOR_UNIT
			else:
				unitValue = 100  # DEFAULT_WAR_VALUE_FOR_UNIT

			currentValue += unitValue

		# Loop through all (known) Players
		for loopPlayer in simulation.players:
			if not loopPlayer.isAlive():
				continue

			if loopPlayer == self.player:
				continue

			if not self.player.hasMetWith(loopPlayer):
				continue

			warDamageLevel: WarDamageLevelType = WarDamageLevelType.none
			valueLost = self.warValueLostWith(loopPlayer)

			if valueLost > 0:
				# Total original value is the current value plus the amount lost, so compute the percentage on that
				valueLostRatio: int = 0
				if currentValue > 0:
					valueLostRatio = int(valueLost * 100 / (currentValue + valueLost))
				else:
					valueLostRatio = valueLost

				if valueLostRatio >= 67:  # WAR_DAMAGE_LEVEL_THRESHOLD_CRIPPLED
					warDamageLevel = WarDamageLevelType.crippled
				elif valueLostRatio >= 50:  # WAR_DAMAGE_LEVEL_THRESHOLD_SERIOUS
					warDamageLevel = WarDamageLevelType.serious
				elif valueLostRatio >= 25:  # WAR_DAMAGE_LEVEL_THRESHOLD_MAJOR
					warDamageLevel = WarDamageLevelType.major
				elif valueLostRatio >= 10:  # WAR_DAMAGE_LEVEL_THRESHOLD_MINOR
					warDamageLevel = WarDamageLevelType.minor

			self.updateWarDamageLevelWith(loopPlayer, warDamageLevel)

		return

	def updateEconomicStrengths(self, simulation):
		for loopPlayer in simulation.players:
			if loopPlayer == self.player:
				continue
				
			if not self.player.hasMetWith(loopPlayer):
				continue

			self.updateEconomicStrengthOf(loopPlayer, simulation)
		
		return

	def updatePlayerTargetValues(self, simulation):
		for loopPlayer in simulation.players:
			if loopPlayer == self.player:
				continue

			if not loopPlayer.isAlive():
				continue

			if not self.player.hasMetWith(loopPlayer):
				continue

			self.updateOnePlayerTargetValueOf(loopPlayer, simulation)

		return

	def updateOnePlayerTargetValueOf(self, otherPlayer, simulation):
		"""DoUpdateOnePlayerTargetValue - Updates what our assessment is of all players' value as a military target"""
		if not self.player.isAlive():
			return

		targetIntValue: int = 0
		targetValue: PlayerTargetValueType = PlayerTargetValueType.none

		otherPlayerMilitaryStrength: int = otherPlayer.militaryMight(simulation)
		myMilitaryStrength: int = self.player.militaryMight(simulation)

		# Prevent divide by 0
		if myMilitaryStrength == 0:
			myMilitaryStrength = 1

		cityDamage = 0
		numCities = 0

		# City Defensive Strength
		for otherCity in simulation.citiesOf(otherPlayer):
			cityStrengthMod = otherCity.power(simulation)
			cityStrengthMod *= 33
			cityStrengthMod /= 100

			otherPlayerMilitaryStrength += cityStrengthMod

			cityDamage += otherCity.damage()
			numCities += 1

		# Depending on how damaged a player's Cities are, he can become a much more attractive target
		if numCities > 0:
			cityDamage /= numCities
			cityDamage *= 100
			cityDamage /= 25  # MAX_CITY_HIT_POINTS

			# iCityDamage is now a percentage of global City damage
			cityDamage *= otherPlayerMilitaryStrength
			cityDamage /= 200 # divide by 200 instead of 100 so that if all Cities have no health it only HALVES our strength instead of taking it all the way to 0

			otherPlayerMilitaryStrength -= cityDamage

		militaryRatio = otherPlayerMilitaryStrength * 100 / myMilitaryStrength # MILITARY_STRENGTH_RATIO_MULTIPLIER
		# Example: If another player has double the Military strength of us, the Ratio will be 200
		targetIntValue += militaryRatio

		# Increase target value if the player is already at war with other players
		warCount: int = otherPlayer.atWarCount()

		# Reduce by 1 if WE'RE already at war with him
		if self.isAtWarWith(otherPlayer):
			warCount -= 1

		targetIntValue += warCount * 30  # TARGET_ALREADY_WAR_EACH_PLAYER

		# Factor in distance
		proximity: PlayerProximityType = self.proximityTo(otherPlayer)
		if proximity == PlayerProximityType.neighbors:
			targetIntValue += -10  # TARGET_NEIGHBORS
		elif proximity == PlayerProximityType.close:
			targetIntValue += 0  # TARGET_CLOSE
		elif proximity == PlayerProximityType.far:
			targetIntValue += 20  # TARGET_FAR
		elif proximity == PlayerProximityType.distant:
			targetIntValue += 60  # TARGET_DISTANT

		# Now do the final assessment
		if targetIntValue >= 200:  # TARGET_IMPOSSIBLE_THRESHOLD
			targetValue = PlayerTargetValueType.impossible
		elif targetIntValue >= 125:  # TARGET_BAD_THRESHOLD
			targetValue = PlayerTargetValueType.bad
		elif targetIntValue >= 80:  # TARGET_AVERAGE_THRESHOLD
			targetValue = PlayerTargetValueType.average
		elif targetIntValue >= 50:  # TARGET_FAVORABLE_THRESHOLD
			targetValue = PlayerTargetValueType.favorable
		else:
			targetValue = PlayerTargetValueType.soft

		# If the player is expanding aggressively, bump things down a level
		if targetValue < PlayerTargetValueType.soft and self.isRecklessExpanderTowards(otherPlayer, simulation):
			targetValue.increase()

		# If it's a city-state and we've been at war for a LONG time, bump things up
		if targetValue > PlayerTargetValueType.impossible and self.playerDict.turnsOfWarWith(otherPlayer, simulation.currentTurn) > 50:  # TARGET_INCREASE_WAR_TURNS
			targetValue.decrease()

		# If the player is too far from us then we can't consider them Soft
		if targetValue == PlayerTargetValueType.soft:
			if proximity < PlayerProximityType.far:
				targetValue = PlayerTargetValueType.favorable

		# Set the value
		self.playerDict.updateTargetValueOf(otherPlayer, targetValue)

		return

	def updateStateOfAllWars(self, stateValue: PlayerStateAllWars):
		self._stateOfAllWars = stateValue

	def stateOfAllWars(self) -> PlayerStateAllWars:
		return self._stateOfAllWars

	def updateWarStates(self, simulation):
		"""Updates what the state of war is with all Players"""
		# Reset overall war state
		stateAllWarsValue: int = 0  # Used to assess overall war state in this function
		self.updateStateOfAllWars(PlayerStateAllWars.neutral)

		# Loop through all (known) Players
		for loopPlayer in simulation.players:
			if not loopPlayer.isMajorAI() and not loopPlayer.isHuman():
				continue

			if not self.isValid(loopPlayer):
				continue

			# War?
			if self.isAtWarWith(loopPlayer):
				myLocalMilitaryStrength: int = 0
				enemyInHisLandsMilitaryStrength: int = 0

				myForeignMilitaryStrength: int = 0
				enemyInMyLandsMilitaryStrength: int = 0

				# Loop through our units
				for loopUnit in simulation.unitsOf(self.player):
					loopTile = simulation.tileAt(loopUnit.location)

					# On our home front
					if loopTile.isHomeFrontFor(self.player, simulation):
						myLocalMilitaryStrength += loopUnit.power()

					# Enemy's home front
					if loopTile.isHomeFrontFor(loopPlayer, simulation):
						myForeignMilitaryStrength += loopUnit.power()

				# Loop through our Enemy's units
				for loopUnit in simulation.unitsOf(loopPlayer):
					loopTile = simulation.tileAt(loopUnit.location)

					# On our home front
					if loopTile.isHomeFrontFor(self.player, simulation):
						enemyInMyLandsMilitaryStrength += loopUnit.power()

					# Enemy's home front
					if loopTile.isHomeFrontFor(loopPlayer, simulation):
						enemyInHisLandsMilitaryStrength += loopUnit.power()

				# Loop through our Cities
				for loopCity in simulation.citiesOf(self.player):
					percentHealthLeft = (loopCity.maxHealthPoints() - loopCity.damage()) * 100 / loopCity.maxHealthPoints()
					myLocalMilitaryStrength += (loopCity.power(simulation) * percentHealthLeft / 100 / 100)

				# Loop through our Enemy's Cities
				for loopCity in simulation.citiesOf(loopPlayer):
					percentHealthLeft = (loopCity.maxHealthPoints() - loopCity.damage()) * 100 / loopCity.maxHealthPoints()
					enemyInHisLandsMilitaryStrength += (loopCity.power(simulation) * percentHealthLeft / 100 / 100)

				# Percentage of our forces in our locales & each other's locales

				# No Units!
				if myLocalMilitaryStrength + myForeignMilitaryStrength == 0:
					myPercentLocal = 100
					myPercentForeign = 0
				else:
					myPercentLocal = myLocalMilitaryStrength * 100 / (myLocalMilitaryStrength + myForeignMilitaryStrength)
					myPercentForeign = 100 - myPercentLocal

				# No Units!
				if enemyInHisLandsMilitaryStrength + enemyInMyLandsMilitaryStrength == 0:
					enemyPercentInHisLands = 100
					enemyPercentInMyLands = 0
				else:
					enemyPercentInHisLands = enemyInHisLandsMilitaryStrength * 100 / (enemyInHisLandsMilitaryStrength + enemyInMyLandsMilitaryStrength)
					enemyPercentInMyLands = 100 - enemyPercentInHisLands

				# Ratio of Me VS Him in our two locales
				if myLocalMilitaryStrength == 0:
					myLocalMilitaryStrength = 1

				localRatio = myLocalMilitaryStrength * 100 / (myLocalMilitaryStrength + enemyInMyLandsMilitaryStrength)

				if enemyInHisLandsMilitaryStrength == 0:
					enemyInHisLandsMilitaryStrength = 1
				foreignRatio = myForeignMilitaryStrength * 100 / (myForeignMilitaryStrength + enemyInHisLandsMilitaryStrength)

				# Calm: Not much happening on either front
				warStateCalmThresholdForeignForces = 25  # WAR_STATE_CALM_THRESHOLD_FOREIGN_FORCES
				if foreignRatio < warStateCalmThresholdForeignForces and localRatio > 100 - warStateCalmThresholdForeignForces:
					eWarState = PlayerWarStateType.calm
				else:  # SOMETHING is happening
					warStateValue = localRatio  # Will be between 0 and 100. Anything less than 75 is bad news though! We want a very high percentage in our own lands.
					warStateValue += foreignRatio  # Will be between 0 and 100. Will vary wildly though, depending on the status of an offensive. A number of 50 is very good.
					warStateValue /= 2

					# Some Example WarStateValues:
					# Local Foreign WarStateValue
					# 100 % 70 % 85
					# 100 % 40 % 70
					# 80 % 30 %: 55
					# 100 % 0 %: 50
					# 60 % 40 %: 50
					# 60 % 10 %: 35
					# 40 % 0 %: 20
					if warStateValue >= 75:  # WAR_STATE_THRESHOLD_NEARLY_WON
						eWarState = PlayerWarStateType.nearlyWon  # WAR_STATE_NEARLY_WON
					elif warStateValue >= 57:  # WAR_STATE_THRESHOLD_OFFENSIVE
						eWarState = PlayerWarStateType.offensive  # WAR_STATE_OFFENSIVE
					elif warStateValue >= 42:  # WAR_STATE_THRESHOLD_STALEMATE
						eWarState = PlayerWarStateType.stalemate  # WAR_STATE_STALEMATE
					elif warStateValue >= 25:  # WAR_STATE_THRESHOLD_DEFENSIVE
						eWarState = PlayerWarStateType.defensive  # WAR_STATE_DEFENSIVE
					else:
						eWarState = PlayerWarStateType.nearlyDefeated  # WAR_STATE_NEARLY_DEFEATED

				# // // // // // // // // // // // // // // // // // // // // // // // // // // // //
				# WAR STATE MODIFICATIONS - We crunched the numbers above, but are there any special cases to consider?
				# // // // // // // // // // // // // // // // // // // // // // // // // // // // //

				# If the war is calm, but they're an easy target consider us on Offense
				if eWarState == PlayerWarStateType.calm:
					if self.targetValueOf(loopPlayer) >= PlayerTargetValueType.favorable:
						eWarState = PlayerWarStateType.offensive

				# If the other guy happens to have a guy or two near us, but we vastly outnumber him overall,
				# we're not really on the defensive
				if eWarState <= PlayerWarStateType.defensive:
					if myLocalMilitaryStrength >= enemyInMyLandsMilitaryStrength + enemyInMyLandsMilitaryStrength:
						eWarState = PlayerWarStateType.stalemate

				# If this is a major power, determine what the impact of this war is on our global situation
				if not loopPlayer.isCityState():
					if eWarState == PlayerWarStateType.nearlyWon:
						stateAllWarsValue += 2
					elif eWarState == PlayerWarStateType.offensive:
						stateAllWarsValue += 1
					elif eWarState == PlayerWarStateType.defensive:
						stateAllWarsValue -= 1

						# If we are defensive in this war and our capital has been damaged, overall state should be defensive
						capital = simulation.capitalOf(self.player)
						if capital is not None:
							if capital.damage() > 0:
								self.updateStateOfAllWars(PlayerStateAllWars.losing)
					elif eWarState == PlayerWarStateType.nearlyDefeated:
						# If nearly defeated in any war, overall state should be defensive
						self.updateStateOfAllWars(PlayerStateAllWars.losing)

			# Not at war
			else:
				eWarState = PlayerWarStateType.none

			self.playerDict.updateWarStateTowards(loopPlayer, eWarState)

		# Finalize overall assessment
		if stateAllWarsValue < 0 or self.stateOfAllWars() == PlayerStateAllWars.losing:
			self.updateStateOfAllWars(PlayerStateAllWars.losing)
		elif stateAllWarsValue > 0:
			self.updateStateOfAllWars(PlayerStateAllWars.winning)

	def doUpdateWarProjections(self, simulation):
		"""Updates what the Projection of war is with all Players"""
		# Loop through all (known) Players
		for loopPlayer in simulation.players:
			if self.player == loopPlayer:
				continue

			if not self.hasMetWith(loopPlayer):
				continue

			if not loopPlayer.isAlive():
				continue

			warScore = self.warScoreTowards(loopPlayer, simulation)

			# Do the final math
			if warScore >= 100:  # WAR_PROJECTION_THRESHOLD_VERY_GOOD
				warProjection = WarProjectionType.veryGood  # WAR_PROJECTION_VERY_GOOD
			elif warScore >= 25:  # WAR_PROJECTION_THRESHOLD_GOOD
				warProjection = WarProjectionType.good  # WAR_PROJECTION_GOOD
			elif warScore <= -100:  # WAR_PROJECTION_THRESHOLD_DESTRUCTION
				warProjection = WarProjectionType.destruction  # WAR_PROJECTION_DESTRUCTION
			elif warScore <= -25:  # WAR_PROJECTION_THRESHOLD_DEFEAT
				warProjection = WarProjectionType.defeat  # WAR_PROJECTION_DEFEAT
			elif warScore <= 0:  # WAR_PROJECTION_THRESHOLD_STALEMATE
				warProjection = WarProjectionType.stalemate  # WAR_PROJECTION_STALEMATE
			else:
				warProjection = WarProjectionType.unknown  # WAR_PROJECTION_UNKNOWN

			# If they're a bad target then the best we can do is a stalemate
			if self.targetValueOf(loopPlayer) <= PlayerTargetValueType.bad:  # TARGET_VALUE_BAD
				if warProjection >= WarProjectionType.good:  # WAR_PROJECTION_GOOD
					warProjection = WarProjectionType.stalemate  # WAR_PROJECTION_STALEMATE

			if self.warProjectionAgainst(loopPlayer) != WarProjectionType.unknown:  # NO_WAR_PROJECTION_TYPE
				self.playerDict.updateLastWarProjectionAgainst(loopPlayer, self.warProjectionAgainst(loopPlayer))
			else:
				# for now, set it to be unknown because we can't set it to NO_WAR_PROJECTION_TYPE
				self.playerDict.updateLastWarProjectionAgainst(loopPlayer, WarProjectionType.unknown)

			self.playerDict.updateWarProjectionAgainst(loopPlayer, warProjection)

		return

	def doUpdateWarGoals(self, simulation):
		"""Updates what the Goal of war is with all Players"""
		# Are we going for World conquest?  If so, then we want to fight our wars to the death
		worldConquest: bool = False

		if self.isGoingForWorldConquest():
			worldConquest = True

		# Loop through all (known) Players
		for loopPlayer in simulation.players:
			if self.player == loopPlayer:
				continue

			if not self.hasMetWith(loopPlayer):
				continue

			if not loopPlayer.isAlive():
				continue

			warGoal: WarGoalType = WarGoalType.none

			if self.player.isAtWarWith(loopPlayer):
				isMinor: bool = loopPlayer.isCityState()

				# Higher ups want war with this Minor Civ
				if isMinor:
					higherUpsWantWar = self.playerDict.minorApproachTowards(loopPlayer) == MinorPlayerApproachType.conquest
				# Higher ups want war with this Major Civ
				else:
					higherUpsWantWar = self.majorCivApproachTowards(loopPlayer, hideTrueFeelings=False) == MajorPlayerApproachType.war

				projection: WarProjectionType = self.playerDict.warProjectionAgainst(loopPlayer)

				# //////////////////////////////
				# Higher ups want war, figure out what kind we're waging
				if higherUpsWantWar:
					# Minor Civs
					if isMinor:
						# If we're going for the conquest victory, conquest is our goal with minors
						if worldConquest:
							warGoal = WarGoalType.conquest  # WAR_GOAL_CONQUEST
						else:
							warGoal = WarGoalType.damage  # WAR_GOAL_DAMAGE

					# Major Civs - depends on how things are going
					else:
						# Default goal is Damage
						warGoal = WarGoalType.damage  # WAR_GOAL_DAMAGE

						# If we're locked into a coop war, we're out for conquest
						if self.isLockedIntoCoopWarAgainst(loopPlayer, simulation):
							warGoal = WarGoalType.conquest  # WAR_GOAL_CONQUEST

						# If we think the war will go well, we can aim for conquest, which means we will not make peace
						if projection >= WarProjectionType.unknown:
							# If they're unforgivable we're out to destroy them, no less
							if self.majorCivOpinion(loopPlayer) == MajorCivOpinionType.unforgivable:
								warGoal = WarGoalType.conquest  # WAR_GOAL_CONQUEST
							# Out for world conquest?
							elif worldConquest:
								warGoal = WarGoalType.conquest  # WAR_GOAL_CONQUEST

				# //////////////////////////////
				# Higher ups don't want to be at war, figure out how bad things are
				else:
					# If we're about to cause some mayhem then hold off on the peace stuff for a bit - not against Minors though
					if not isMinor and self.warStateTowards(loopPlayer) == PlayerWarStateType.nearlyWon and self.stateOfAllWars() != PlayerStateAllWars.losing:
						warGoal = WarGoalType.damage  # WAR_GOAL_DAMAGE
					# War isn't decisively in our favor, so we'll make peace if possible
					else:
						warGoal = WarGoalType.peace  # WAR_GOAL_PEACE
			# Getting ready to attack
			elif self.warGoalTowards(loopPlayer) == WarGoalType.prepare:
				warGoal = WarGoalType.prepare  # WAR_GOAL_PREPARE
			# Getting ready to make a forceful demand
			elif self.warGoalTowards(loopPlayer) == WarGoalType.demand:
				warGoal = WarGoalType.demand  # WAR_GOAL_DEMAND

			# Update the counter for how long we've wanted peace for (used to determine when to ask for peace)
			if warGoal == WarGoalType.peace:
				self.playerDict.changeWantPeaceCounterWith(loopPlayer, 1)
			else:
				self.playerDict.updateWantPeaceCounterWith(loopPlayer, 0)

			# Set the War Goal
			self.playerDict.updateWarGoalTowards(loopPlayer, warGoal)

		return

	def doUpdatePeaceTreatyWillingness(self, simulation):
		"""Updates what peace treaties we're willing to offer and accept"""
		# Loop through all (known) Players
		for loopPlayer in simulation.players:
			loopDiplomacyAI = loopPlayer.diplomacyAI

			if self.player == loopPlayer:
				continue

			if not self.hasMetWith(loopPlayer):
				continue

			if not loopPlayer.isAlive():
				continue

			treatyWillingToOffer: PeaceTreatyType = PeaceTreatyType.none
			treatyWillingToAccept: PeaceTreatyType = PeaceTreatyType.none

			willingToOfferScore: int = 0
			willingToAcceptScore: int = 0

			if self.isAtWarWith(loopPlayer):
				# Have to be at war with the human for a certain amount of time before the AI will agree to peace
				if loopPlayer.isHuman():
					if not self.isWillingToMakePeaceWithHumanPlayer(loopPlayer, simulation):
						self.updateTreatyWillingToOfferWith(loopPlayer, PeaceTreatyType.none)
						self.updateTreatyWillingToAcceptWith(loopPlayer, PeaceTreatyType.none)

						continue

				# If we're out for conquest, then no peace!
				if self.warGoalTowards(loopPlayer) != WarGoalType.conquest:
					warProjection: WarProjectionType = self.warProjectionAgainst(loopPlayer)

					# What we're willing to give up.  The higher the number the more we're willing to part with

					# How is the war going?
					if warProjection == WarProjectionType.destruction:
						willingToOfferScore += 100  # PEACE_WILLINGNESS_OFFER_PROJECTION_DESTRUCTION
					elif warProjection == WarProjectionType.defeat:
						willingToOfferScore += 60  # PEACE_WILLINGNESS_OFFER_PROJECTION_DEFEAT
					elif warProjection == WarProjectionType.stalemate:
						willingToOfferScore += 20  # PEACE_WILLINGNESS_OFFER_PROJECTION_STALEMATE
					elif warProjection == WarProjectionType.unknown:
						willingToOfferScore += 0  # PEACE_WILLINGNESS_OFFER_PROJECTION_UNKNOWN
					elif warProjection == WarProjectionType.good:
						willingToOfferScore += -20  # PEACE_WILLINGNESS_OFFER_PROJECTION_GOOD
					elif warProjection == WarProjectionType.veryGood:
						willingToOfferScore += -50  # PEACE_WILLINGNESS_OFFER_PROJECTION_VERY_GOOD

					# How much damage have we taken?
					warDamageLevel: WarDamageLevelType = self.warDamageLevelFrom(loopPlayer)

					if warDamageLevel == WarDamageLevelType.none:
						willingToOfferScore += 0  # PEACE_WILLINGNESS_OFFER_WAR_DAMAGE_NONE
					elif warDamageLevel == WarDamageLevelType.minor:
						willingToOfferScore += 10  # PEACE_WILLINGNESS_OFFER_WAR_DAMAGE_MINOR
					elif warDamageLevel == WarDamageLevelType.major:
						willingToOfferScore += 20  # PEACE_WILLINGNESS_OFFER_WAR_DAMAGE_MAJOR
					elif warDamageLevel == WarDamageLevelType.serious:
						willingToOfferScore += 50  # PEACE_WILLINGNESS_OFFER_WAR_DAMAGE_SERIOUS
					elif warDamageLevel == WarDamageLevelType.crippled:
						willingToOfferScore += 80  # PEACE_WILLINGNESS_OFFER_WAR_DAMAGE_CRIPPLED

					# How much damage have we dished out?
					ownWarDamageLevel: WarDamageLevelType = loopDiplomacyAI.warDamageLevelFrom(self.player)

					if ownWarDamageLevel == WarDamageLevelType.none:
						willingToOfferScore -= 0  # PEACE_WILLINGNESS_OFFER_WAR_DAMAGE_NONE
					elif ownWarDamageLevel == WarDamageLevelType.minor:
						willingToOfferScore -= 10  # PEACE_WILLINGNESS_OFFER_WAR_DAMAGE_MINOR
					elif ownWarDamageLevel == WarDamageLevelType.major:
						willingToOfferScore -= 20  # PEACE_WILLINGNESS_OFFER_WAR_DAMAGE_MAJOR
					elif ownWarDamageLevel == WarDamageLevelType.serious:
						willingToOfferScore -= 50  # PEACE_WILLINGNESS_OFFER_WAR_DAMAGE_SERIOUS
					elif ownWarDamageLevel == WarDamageLevelType.crippled:
						willingToOfferScore -= 80  # PEACE_WILLINGNESS_OFFER_WAR_DAMAGE_CRIPPLED

					# Do the final assessment
					if willingToOfferScore >= 180:  # PEACE_WILLINGNESS_OFFER_THRESHOLD_UN_SURRENDER
						treatyWillingToOffer = PeaceTreatyType.unconditionalSurrender
					elif willingToOfferScore >= 150:  # PEACE_WILLINGNESS_OFFER_THRESHOLD_CAPITULATION
						treatyWillingToOffer = PeaceTreatyType.capitulation
					elif willingToOfferScore >= 120:  # PEACE_WILLINGNESS_OFFER_THRESHOLD_CESSION
						treatyWillingToOffer = PeaceTreatyType.cession
					elif willingToOfferScore >= 95:  # PEACE_WILLINGNESS_OFFER_THRESHOLD_SURRENDER
						treatyWillingToOffer = PeaceTreatyType.surrender
					elif willingToOfferScore >= 70:  # PEACE_WILLINGNESS_OFFER_THRESHOLD_SUBMISSION
						treatyWillingToOffer = PeaceTreatyType.submission
					elif willingToOfferScore >= 55:  # PEACE_WILLINGNESS_OFFER_THRESHOLD_BACKDOWN
						treatyWillingToOffer = PeaceTreatyType.backDown
					elif willingToOfferScore >= 40:  # PEACE_WILLINGNESS_OFFER_THRESHOLD_SETTLEMENT
						treatyWillingToOffer = PeaceTreatyType.settlement
					elif willingToOfferScore >= 20:  # PEACE_WILLINGNESS_OFFER_THRESHOLD_ARMISTICE
						treatyWillingToOffer = PeaceTreatyType.armistice
					else:
						# War Score could be negative here, but we're already assuming this player wants peace.
						# But he's not willing to give up anything for it
						treatyWillingToOffer = PeaceTreatyType.whitePeace

					# If they've broken a peace deal before then we're not going to give them anything
					if loopDiplomacyAI.hasBrokenPeaceTreaty():
						if treatyWillingToOffer > PeaceTreatyType.whitePeace:
							treatyWillingToOffer = PeaceTreatyType.whitePeace

					# What we're willing to accept from eLoopPlayer.  The higher the number the more we want

					# How is the war going?
					if warProjection == WarProjectionType.destruction:
						willingToAcceptScore += -50  # PEACE_WILLINGNESS_ACCEPT_PROJECTION_DESTRUCTION
					elif warProjection == WarProjectionType.defeat:
						willingToAcceptScore += -20  # PEACE_WILLINGNESS_ACCEPT_PROJECTION_DEFEAT
					elif warProjection == WarProjectionType.stalemate:
						willingToAcceptScore += -10  # PEACE_WILLINGNESS_ACCEPT_PROJECTION_STALEMATE
					elif warProjection == WarProjectionType.unknown:
						willingToAcceptScore += 0  # PEACE_WILLINGNESS_ACCEPT_PROJECTION_UNKNOWN
					elif warProjection == WarProjectionType.good:
						willingToAcceptScore += 50  # PEACE_WILLINGNESS_ACCEPT_PROJECTION_GOOD
					elif warProjection == WarProjectionType.veryGood:
						willingToAcceptScore += 100  # PEACE_WILLINGNESS_ACCEPT_PROJECTION_VERY_GOOD

					# How easy would it be for us to squash them?
					target: PlayerTargetValueType = self.targetValueOf(loopPlayer)
					if target == PlayerTargetValueType.impossible:
						willingToAcceptScore += -50  # PEACE_WILLINGNESS_ACCEPT_TARGET_IMPOSSIBLE
					elif target == PlayerTargetValueType.bad:
						willingToAcceptScore += -20  # PEACE_WILLINGNESS_ACCEPT_TARGET_BAD
					elif target == PlayerTargetValueType.average:
						willingToAcceptScore += 0  # PEACE_WILLINGNESS_ACCEPT_TARGET_AVERAGE
					elif target == PlayerTargetValueType.favorable:
						willingToAcceptScore += 20  # PEACE_WILLINGNESS_ACCEPT_TARGET_FAVORABLE
					elif target == PlayerTargetValueType.soft:
						willingToAcceptScore += 50  # PEACE_WILLINGNESS_ACCEPT_TARGET_SOFT

					# Do the final assessment
					if willingToAcceptScore >= 150:  # PEACE_WILLINGNESS_ACCEPT_THRESHOLD_UN_SURRENDER
						treatyWillingToAccept = PeaceTreatyType.unconditionalSurrender
					elif willingToAcceptScore >= 115:  # PEACE_WILLINGNESS_ACCEPT_THRESHOLD_CAPITULATION
						treatyWillingToAccept = PeaceTreatyType.capitulation
					elif willingToAcceptScore >= 80:  # PEACE_WILLINGNESS_ACCEPT_THRESHOLD_CESSION
						treatyWillingToAccept = PeaceTreatyType.cession
					elif willingToAcceptScore >= 65:  # PEACE_WILLINGNESS_ACCEPT_THRESHOLD_SURRENDER
						treatyWillingToAccept = PeaceTreatyType.surrender
					elif willingToAcceptScore >= 50:  # PEACE_WILLINGNESS_ACCEPT_THRESHOLD_SUBMISSION
						treatyWillingToAccept = PeaceTreatyType.submission
					elif willingToAcceptScore >= 35:  # PEACE_WILLINGNESS_ACCEPT_THRESHOLD_BACKDOWN
						treatyWillingToAccept = PeaceTreatyType.backDown
					elif willingToAcceptScore >= 20:  # PEACE_WILLINGNESS_ACCEPT_THRESHOLD_SETTLEMENT
						treatyWillingToAccept = PeaceTreatyType.settlement
					elif willingToAcceptScore >= 10:  # PEACE_WILLINGNESS_ACCEPT_THRESHOLD_ARMISTICE
						treatyWillingToAccept = PeaceTreatyType.armistice
					else:
						treatyWillingToAccept = PeaceTreatyType.whitePeace

					# If we're losing all wars then let's go ahead and accept a white peace
					if self._stateOfAllWars == PlayerStateAllWars.losing:
						treatyWillingToAccept = PeaceTreatyType.whitePeace

			self.updateTreatyWillingToOfferWith(loopPlayer, treatyWillingToOffer)
			self.updateTreatyWillingToAcceptWith(loopPlayer, treatyWillingToAccept)

		return

	def doUpdateLandDisputeLevels(self, simulation):
		"""Updates what is our level of Dispute with a player is over Land"""
		landDisputeWeight = 0
		expansionFlavor = 0

		# Loop through all (known) Players
		for loopPlayer in simulation.players:
			if not loopPlayer.isAlive():
				continue

			if self.player == loopPlayer:
				continue

			if not self.player.hasMetWith(loopPlayer):
				continue

			# store last turn's values
			lastTurnLandDisputeLevel = self.landDisputeLevelWith(loopPlayer)
			self.playerDict.updateLastTurnLandDisputeLevelWith(loopPlayer, lastTurnLandDisputeLevel)

			landDisputeWeight = 0

			# Expansion aggression
			aggression = self.expansionAggressivePostureTowards(loopPlayer)

			if aggression == AggressivePostureType.none:
				landDisputeWeight += 0  # LAND_DISPUTE_EXP_AGGRESSIVE_POSTURE_NONE
			elif aggression == AggressivePostureType.low:
				landDisputeWeight += 10  # LAND_DISPUTE_EXP_AGGRESSIVE_POSTURE_LOW
			elif aggression == AggressivePostureType.medium:
				landDisputeWeight += 32  # LAND_DISPUTE_EXP_AGGRESSIVE_POSTURE_MEDIUM
			elif aggression == AggressivePostureType.high:
				landDisputeWeight += 50  # LAND_DISPUTE_EXP_AGGRESSIVE_POSTURE_HIGH
			elif aggression == AggressivePostureType.incredible:
				landDisputeWeight += 60  # LAND_DISPUTE_EXP_AGGRESSIVE_POSTURE_INCREDIBLE

			# Plot Buying aggression
			aggression = self.plotBuyingAggressivePostureTowards(loopPlayer)

			if aggression == AggressivePostureType.none:
				landDisputeWeight += 0  # LAND_DISPUTE_PLOT_BUY_AGGRESSIVE_POSTURE_NONE
			elif aggression == AggressivePostureType.low:
				landDisputeWeight += 5  # LAND_DISPUTE_PLOT_BUY_AGGRESSIVE_POSTURE_LOW
			elif aggression == AggressivePostureType.medium:
				landDisputeWeight += 12  # LAND_DISPUTE_PLOT_BUY_AGGRESSIVE_POSTURE_MEDIUM
			elif aggression == AggressivePostureType.high:
				landDisputeWeight += 20  # LAND_DISPUTE_PLOT_BUY_AGGRESSIVE_POSTURE_HIGH
			elif aggression == AggressivePostureType.incredible:
				landDisputeWeight += 30  # LAND_DISPUTE_PLOT_BUY_AGGRESSIVE_POSTURE_INCREDIBLE

			# Look at our Proximity to the other Player
			proximity = self.proximityTo(loopPlayer)

			if proximity == PlayerProximityType.distant:
				landDisputeWeight += 0  # LAND_DISPUTE_DISTANT
			elif proximity == PlayerProximityType.far:
				landDisputeWeight += 10  # LAND_DISPUTE_FAR
			elif proximity == PlayerProximityType.close:
				landDisputeWeight += 18  # LAND_DISPUTE_CLOSE
			elif proximity == PlayerProximityType.neighbors:
				landDisputeWeight += 30  # LAND_DISPUTE_NEIGHBORS

			# JON: Turned off to counter-balance the lack of the next block functioning
			# Is the player already cramped?
			# if self.player.isCramped():
			#	iLandDisputeWeight += 0  # LAND_DISPUTE_CRAMPED_MULTIPLIER

			# If the player has deleted the EXPANSION Flavor we have to account for that
			expansionFlavor = 5  # DEFAULT_FLAVOR_VALUE
			expansionFlavor = self.player.personalAndGrandStrategyFlavor(FlavorType.expansion)

			# Add weight for Player's natural EXPANSION preference
			landDisputeWeight *= expansionFlavor

			# Now See what our new Dispute Level should be
			disputeLevel: DisputeLevelType = DisputeLevelType.none
			if landDisputeWeight >= 400:  # LAND_DISPUTE_FIERCE_THRESHOLD
				disputeLevel = DisputeLevelType.fierce
			elif landDisputeWeight >= 230:  # LAND_DISPUTE_STRONG_THRESHOLD
				disputeLevel = DisputeLevelType.strong
			elif landDisputeWeight >= 100:  # LAND_DISPUTE_WEAK_THRESHOLD
				disputeLevel = DisputeLevelType.weak

			# Actually set the Level
			self.playerDict.updateLandDisputeLevelWith(loopPlayer, disputeLevel)

		return

	def doUpdateMilitaryAggressivePostures(self, simulation):
		"""Updates how aggressively all players' military Units are positioned in relation to us"""
		playerMilitaryAI = self.player.militaryAI

		typicalLandPower = playerMilitaryAI.powerOfStrongestBuildableUnit(UnitDomainType.land)
		typicalNavalPower = playerMilitaryAI.powerOfStrongestBuildableUnit(UnitDomainType.sea)
		typicalAirPower = playerMilitaryAI.powerOfStrongestBuildableUnit(UnitDomainType.air)

		# Loop through all (known) Players
		for loopPlayer in simulation.players:
			if loopPlayer.isBarbarian():
				continue

			if not loopPlayer.isAlive():
				continue

			if self.player == loopPlayer:
				continue

			if not self.player.hasMetWith(loopPlayer):
				continue

			# Keep a record of last turn
			currentPosture: AggressivePostureType = self.playerDict.militaryAggressivePostureOf(loopPlayer)
			self.playerDict.updateLastTurnMilitaryAggressivePostureOf(loopPlayer, currentPosture)

			# We're allowing them Open Borders? We shouldn't care.
			if self.isOpenBordersAgreementActiveWith(loopPlayer):
				self.playerDict.updateMilitaryAggressivePosture(loopPlayer, AggressivePostureType.none)
				return

			# We're working together, so don't worry about it
			if self.isDeclarationOfFriendshipActiveWith(loopPlayer) or \
				self.isDefensivePactActiveWith(loopPlayer):
				self.playerDict.updateMilitaryAggressivePosture(loopPlayer, AggressivePostureType.none)
				return

			# They resurrected us, so don't worry about it
			# if ((WasResurrectedBy(otherPlayer) or IsMasterLiberatedMeFromVassalage(loopPlayer)) and
			#    not self.isAtWarWith(loopPlayer)):
			# self.playerDict.updateMilitaryAggressivePosture(loopPlayer, AggressivePostureType.none)
			# 				return

			unitValueOnMyHomeFront: int = 0
			unitScore: int = 0
			isAtWarWithSomeone: int = loopPlayer.atWarCount() > 0

			# For humans (Move Troops request) or if at war with them, ignore other wars the player may be waging
			ignoreOtherWars: bool = self.player.isHuman() or self.player.isAtWarWith(loopPlayer)

			# Loop through the other guy's units
			for loopUnit in simulation.unitsOf(loopPlayer):
				# Don't be scared of noncombat Units!
				if loopUnit.unitType.unitClass() == UnitClassType.civilian or \
					loopUnit.unitType.defaultTask() == UnitTaskType.explore or \
					loopUnit.unitType.defaultTask() == UnitTaskType.exploreSea:
					continue

				unitPlot = simulation.tileAt(loopUnit.location)
				if unitPlot is None:
					continue  # could also raise an exception here

				# Can we actually see this Unit? No cheating!
				if unitPlot.isVisibleTo(self.player):
					continue

				# Must be close to us
				if not unitPlot.isCloseToBorderOf(self.player, simulation):
					continue

				# At war with someone? Because if this Unit is in the vicinity of another player he's
				# already at war with, don't count this Unit as aggressive
				if isAtWarWithSomeone and not ignoreOtherWars:
					# Loop through all players ...
					for otherLoopPlayer in simulation.players:
						# At war with this player?
						if not otherLoopPlayer == self.player and loopPlayer.isAtWarWith(otherLoopPlayer):
							# Is the unit close to the other player?
							if unitPlot.isCloseToBorderOf(otherLoopPlayer, simulation):
								continue

				valueToAdd = 100

				# Adjust based on unit power compared to us
				# Units stronger than ours are worth more, units weaker than ours are worth less
				unitValuePercent = loopUnit.power() * 100

				if unitValuePercent > 0:
					# Compare to strongest unit we can build in that domain, for an apples to apples comparison
					# Best unit that can be currently built in a domain is given a value of 100
					domain = loopUnit.domain()

					if domain == UnitDomainType.air:
						if typicalAirPower > 0:
							unitValuePercent /= typicalAirPower
						else:
							unitValuePercent = 100  # DEFAULT_WAR_VALUE_FOR_UNIT
					elif domain == UnitDomainType.sea:
						if typicalNavalPower > 0:
							unitValuePercent /= typicalNavalPower
						else:
							unitValuePercent = 100  # DEFAULT_WAR_VALUE_FOR_UNIT
					else:
						if typicalLandPower > 0:
							unitValuePercent /= typicalLandPower
						else:
							unitValuePercent = 100  # DEFAULT_WAR_VALUE_FOR_UNIT

					valueToAdd *= unitValuePercent
					valueToAdd /= 100
				else:
					continue

				# If the Unit is in the other team's territory, halve its "aggression value", since he may just be defending himself
				if unitPlot.hasOwner() and loopPlayer == unitPlot.owner():
					valueToAdd /= 2
					unitScore += 1
				else:
					unitScore += 2

				unitValueOnMyHomeFront += valueToAdd

			aggressivePosture: AggressivePostureType = AggressivePostureType.none

			# So how threatening is he being?
			if unitValueOnMyHomeFront >= 800:  # MILITARY_AGGRESSIVE_POSTURE_THRESHOLD_INCREDIBLE
				aggressivePosture = AggressivePostureType.incredible
			elif unitValueOnMyHomeFront >= 500:  # MILITARY_AGGRESSIVE_POSTURE_THRESHOLD_HIGH
				aggressivePosture = AggressivePostureType.high
			elif unitValueOnMyHomeFront >= 300:  # MILITARY_AGGRESSIVE_POSTURE_THRESHOLD_MEDIUM
				aggressivePosture = AggressivePostureType.medium
			elif unitValueOnMyHomeFront >= 100:  # MILITARY_AGGRESSIVE_POSTURE_THRESHOLD_LOW
				aggressivePosture = AggressivePostureType.low

			# Common sense override in case they have a large number of low-power units nearby
			if aggressivePosture < AggressivePostureType.incredible and unitScore >= 18:  # 9 units
				aggressivePosture = AggressivePostureType.incredible
			elif aggressivePosture < AggressivePostureType.high and unitScore >= 14:  # 7 units
				aggressivePosture = AggressivePostureType.high
			elif aggressivePosture < AggressivePostureType.medium and unitScore >= 10:  # 5 units
				aggressivePosture = AggressivePostureType.medium

			self.playerDict.updateMilitaryAggressivePosture(loopPlayer, aggressivePosture)

			if aggressivePosture > currentPosture and aggressivePosture >= AggressivePostureType.medium:
				# v.push_back(otherPlayer)
				pass

		# If someone's aggressive posture rose, reevaluate our approach towards them immediately \
		# DoReevaluatePlayers(v)
		return

	def doUpdateExpansionAggressivePostures(self, simulation):
		"""Updates how aggressively this player's Units are positioned in relation to us"""
		if self.player.capitalCity(simulation) is None:
			return

		# Loop through all (known) Players
		for loopPlayer in simulation.players:
			self.doUpdateOnePlayerExpansionAggressivePosture(loopPlayer, simulation)

		return

	def doUpdateOnePlayerExpansionAggressivePosture(self, otherPlayer, simulation):
		"""Updates how aggressively this player's Units are positioned in relation to us"""
		if self.player.capitalCity(simulation) is None:
			return

		if not self.isValid(otherPlayer):
			return

		# Irrelevant if we can't declare war on these guys
		if not self.isAtWarWith(otherPlayer) and not self.player.canDeclareWarTowards(otherPlayer):
			return

		myCapitalLocation: HexPoint = self.player.capitalCity(simulation).location

		# If they have no capital then, uh... just stop I guess
		if otherPlayer.capitalCity(simulation) is None:
			return

		theirCapitalLocation: HexPoint = otherPlayer.capitalCity(simulation).location
		distanceCapitals = theirCapitalLocation.distance(myCapitalLocation)

		mostAggressiveCityPosture: AggressivePostureType = AggressivePostureType.none
		iNumMostAggressiveCities: int = 0

		# Loop through all of this player's Cities
		for loopCity in simulation.citiesOf(otherPlayer):
			# Don't look at their capital
			if loopCity.isCapital():
				continue

			# Don't look at Cities they've captured
			if loopCity.originalLeaderValue != loopCity.player.leader:
				continue

			eAggressivePosture: AggressivePostureType = AggressivePostureType.none
			cityLocation: HexPoint = loopCity.location

			# First calculate distances
			iDistanceUsToThem: int = myCapitalLocation.distance(cityLocation)
			iDistanceThemToTheirCapital: int = theirCapitalLocation.distance(cityLocation)

			if iDistanceUsToThem <= 3:  # EXPANSION_CAPITAL_DISTANCE_AGGRESSIVE_POSTURE_HIGH())
				eAggressivePosture = AggressivePostureType.high  # AGGRESSIVE_POSTURE_HIGH
			elif iDistanceUsToThem <= 5:  # EXPANSION_CAPITAL_DISTANCE_AGGRESSIVE_POSTURE_MEDIUM())
				eAggressivePosture = AggressivePostureType.medium  # AGGRESSIVE_POSTURE_MEDIUM
			elif iDistanceUsToThem <= 9:  # EXPANSION_CAPITAL_DISTANCE_AGGRESSIVE_POSTURE_LOW())
				eAggressivePosture = AggressivePostureType.low  # AGGRESSIVE_POSTURE_LOW

			# If this City is closer to our capital than the other player's then it's immediately at least Mediumly aggressive
			if eAggressivePosture == AggressivePostureType.low:
				if iDistanceUsToThem < iDistanceThemToTheirCapital:
					eAggressivePosture = AggressivePostureType.medium  # AGGRESSIVE_POSTURE_MEDIUM

			# If this City is further from their capital then our capitals are then it's super-aggressive
			if eAggressivePosture >= AggressivePostureType.medium:
				if distanceCapitals < iDistanceThemToTheirCapital:
					eAggressivePosture = AggressivePostureType.incredible  # AGGRESSIVE_POSTURE_INCREDIBLE

			# Increase number of Cities at this Aggressiveness level
			if eAggressivePosture == mostAggressiveCityPosture:
				iNumMostAggressiveCities += 1

			# If this City is the most aggressive one yet, replace the old record
			elif eAggressivePosture > mostAggressiveCityPosture:
				mostAggressiveCityPosture = eAggressivePosture
				iNumMostAggressiveCities = 0

			# If we're already at the max aggression level we don't need to look at more Cities
			if mostAggressiveCityPosture == AggressivePostureType.incredible:
				break

		# If we have multiple Cities that tie for being the highest then bump us up a level
		if iNumMostAggressiveCities > 1:
			# If every City is low then we don't care that much, and if we're already at the highest level we can't go higher
			if AggressivePostureType.low < mostAggressiveCityPosture < AggressivePostureType.incredible:
				mostAggressiveCityPosture = AggressivePostureType.fromValue(mostAggressiveCityPosture.value() + 1)

		self.playerDict.updateExpansionAggressivePosture(otherPlayer, mostAggressiveCityPosture)

	def doUpdatePlotBuyingAggressivePosture(self, simulation):
		"""Updates how aggressively otherPlayer is buying land near us"""
		# Loop through all (known) Players
		for loopPlayer in simulation.players:
			if not loopPlayer.isMajorAI() and not loopPlayer.isHuman():
				continue

			if not self.isValid(loopPlayer):
				continue

			iAggressionScore: int = 0

			# Loop through all of our Cities to see if this player has bought land near them
			for loopCity in simulation.citiesOf(loopPlayer):
				iAggressionScore += loopCity.numberOfPlotsAcquiredBy(loopPlayer)

			# Now See what our new Dispute Level should be
			if iAggressionScore >= 10:  # PLOT_BUYING_POSTURE_INCREDIBLE_THRESHOLD
				ePosture = AggressivePostureType.incredible  # AGGRESSIVE_POSTURE_INCREDIBLE
			elif iAggressionScore >= 7:  # PLOT_BUYING_POSTURE_HIGH_THRESHOLD
				ePosture = AggressivePostureType.high  # AGGRESSIVE_POSTURE_HIGH
			elif iAggressionScore >= 4:  # PLOT_BUYING_POSTURE_MEDIUM_THRESHOLD
				ePosture = AggressivePostureType.medium  # AGGRESSIVE_POSTURE_MEDIUM
			elif iAggressionScore >= 2:  # PLOT_BUYING_POSTURE_LOW_THRESHOLD
				ePosture = AggressivePostureType.low  # AGGRESSIVE_POSTURE_LOW
			else:
				ePosture = AggressivePostureType.none  # AGGRESSIVE_POSTURE_NONE

			self.playerDict.updatePlotBuyingAggressivePosture(loopPlayer, ePosture)

		return

	def doHiddenAgenda(self, simulation):
		# fixme
		pass

	def updateOpinions(self, simulation):
		"""What is our basic opinion of the role a player has in our game?"""
		# Loop through all (known) Majors
		for loopPlayer in simulation.players:
			if not loopPlayer.isMajorAI() and not loopPlayer.isHuman():
				continue

			self.doUpdateOnePlayerOpinionOf(loopPlayer, simulation)

		return

	def doUpdateOnePlayerOpinionOf(self, otherPlayer, simulation):
		"""What is our basic opinion of the role a player has in our game?"""
		if not self.isValid(otherPlayer):
			return

		opinion: MajorCivOpinionType = MajorCivOpinionType.none

		# Teammates?
		if self.playerDict.isAlliedWith(otherPlayer):
			opinion = MajorCivOpinionType.ally  # MAJOR_CIV_OPINION_ALLY
		# Different teams
		else:
			opinionWeight = self.majorCivOpinionWeightTowards(otherPlayer)

			if opinionWeight >= 50:  # OPINION_THRESHOLD_UNFORGIVABLE
				opinion = MajorCivOpinionType.unforgivable  # MAJOR_CIV_OPINION_UNFORGIVABLE
			elif opinionWeight >= 30:  # OPINION_THRESHOLD_ENEMY
				opinion = MajorCivOpinionType.enemy  # MAJOR_CIV_OPINION_ENEMY
			elif opinionWeight >= 10:  # OPINION_THRESHOLD_COMPETITOR
				opinion = MajorCivOpinionType.competitor  # MAJOR_CIV_OPINION_COMPETITOR
			elif opinionWeight >= -10:  # OPINION_THRESHOLD_FAVORABLE
				opinion = MajorCivOpinionType.neutral  # MAJOR_CIV_OPINION_NEUTRAL
			elif opinionWeight >= -30:  # OPINION_THRESHOLD_FRIEND
				opinion = MajorCivOpinionType.favorable  # MAJOR_CIV_OPINION_FAVORABLE
			elif opinionWeight >= -50:  # OPINION_THRESHOLD_ALLY
				opinion = MajorCivOpinionType.friend  # MAJOR_CIV_OPINION_FRIEND
			else:
				opinion = MajorCivOpinionType.ally  # MAJOR_CIV_OPINION_ALLY

			# If we've agreed to work against someone, then the worst we can feel towards this guy is enemy
			# if (IsWorkingAgainstPlayer(otherPlayer) & & eOpinion < MAJOR_CIV_OPINION_COMPETITOR)
			# eOpinion = MAJOR_CIV_OPINION_COMPETITOR

		# Finally, set the Opinion
		self.playerDict.updateMajorCivOpinionTowards(otherPlayer, opinion)
	
		# LogOpinionUpdate(otherPlayer, viOpinionWeights)
		return

	def isValid(self, otherPlayer) -> bool:
		# Alive?
		if not otherPlayer.isAlive():
			return False

		if self.player == otherPlayer:
			return False

		# A player we've met?
		if not self.hasMetWith(otherPlayer):
			return False

		return True

	def updateMajorCivApproaches(self, simulation):
		"""Determine our general approach to each Player we've met"""
		# Transfer Approaches from last turn to a separate array so we still have access to the info, then clear out the real one
		for loopPlayer in simulation.players:
			if not loopPlayer.isMajorAI() and not loopPlayer.isHuman():
				continue

			self._paeApproachScratchPad.setWeight(-1, hash(loopPlayer))

			if self.isValid(loopPlayer):
				self._paeApproachScratchPad.setWeight(self.majorCivApproachTowards(loopPlayer, hideTrueFeelings=False), hash(loopPlayer))
				self.updateMajorCivApproachTowards(loopPlayer, MajorPlayerApproachType.none)

		numCivsWereLookingAt = 0
		vePlayerApproachOrder = []
		veTiedPlayerApproachWeights = WeightedBaseList()

		# Look at the players we feel are our biggest opponents first
		for opinion in MajorCivOpinionType.all():
			numCivsWeHaveThisOpinionTowards = self.numMajorCivOpinion(opinion, simulation)

			if numCivsWeHaveThisOpinionTowards > 0:
				veTiedPlayerApproachWeights.removeAll()

				# Loop through all (known) Majors and determine the order of who we pick our Approach for first
				for loopPlayer in simulation.players:
					if not loopPlayer.isMajorAI():
						continue

					if self.isValid(loopPlayer):
						if self.majorCivOpinion(loopPlayer) == opinion:
							# If there's only civ we feel this way about then there's no need to look at anything else
							if numCivsWeHaveThisOpinionTowards == 1:
								numCivsWereLookingAt += 1
								vePlayerApproachOrder.append(loopPlayer)
								break
							# More than one other leader we feel this way about - have to rank them now
							else:
								# Just grab the highest weight for sorting later
								highestWeight, _, _ = self.bestApproachTowardsMajorCiv(loopPlayer, lookAtOtherPlayers=False, log=False, simulation=simulation)
								veTiedPlayerApproachWeights.setWeight(highestWeight, loopPlayer)

				# Order players
				if numCivsWeHaveThisOpinionTowards > 1:
					veTiedPlayerApproachWeights.sortByValue(reverse=True)

					# Now add sorted players to the overall vector that we'll look at in the next code block
					for loopPlayer, _ in veTiedPlayerApproachWeights.items():
						numCivsWereLookingAt += 1
						vePlayerApproachOrder.append(loopPlayer)

		# Assert for Release build!
		assert numCivsWereLookingAt == len(vePlayerApproachOrder)

		# MajorCivApproachTypes eApproach
		# WarFaceTypes eWarFace

		# Now that we have our order for who to decide Approaches for, actually decide now!
		for loopPlayer in vePlayerApproachOrder:
			# See which Approach is best
			_, approach, warFace = self.bestApproachTowardsMajorCiv(loopPlayer, lookAtOtherPlayers=True, log=True, simulation=simulation)

			# If we're going to war, and we haven't picked a War Face yet choose one
			if approach == MajorPlayerApproachType.war and self.warFaceWith(loopPlayer) == PlayerWarFaceType.none:
				self.playerDict.updateWarFaceWith(loopPlayer, warFace)

			# CvAssertMsg(eApproach >= 0, "DIPLOMACY_AI: Invalid MajorCivApproachType.  Please send Jon this with your last 5 autosaves and what changelist # you're playing.")

			# Actually assign the (possibly) new Approach
			self.updateMajorCivApproachTowards(loopPlayer, approach)

		return

	def updateMinorCivApproaches(self, simulation):
		"""Determine our general approach to each Minor Civ we've met"""
		# Transfer Approaches from last turn to a separate array, so we still have access to the info,
		# then clear out the real one
		for loopPlayer in simulation.players:
			self._paeApproachScratchPad.setWeight(-1, hash(loopPlayer))

			if not loopPlayer.isCityState():
				continue

			if not self.isValid(loopPlayer):
				continue

			minorCivApproachValue: MinorPlayerApproachType = self.minorApproachTowards(loopPlayer)
			self._paeApproachScratchPad.setWeight(minorCivApproachValue, hash(loopPlayer))
			self.updateMinorCivApproachTowards(loopPlayer, MinorPlayerApproachType.none)

		playerApproachWeights = WeightedBaseList()

		# Loop through all (known) Minors and determine the order of who we pick our Approach for first based
		# on PROXIMITY - this is different from Majors
		for loopPlayer in simulation.players:
			if not self.isValid(loopPlayer):
				continue

			# Note that the order in the PlayerProximityTypes enum is very important here: be sure to verify that
			# NEIGHBORS is the last entry
			highestWeight = self.player.proximityTo(loopPlayer)
			playerApproachWeights.setWeight(highestWeight, loopPlayer)

		# Now sort the list if there's anything in it
		if len(playerApproachWeights.items()) > 0:
			playerApproachWeights.sortByValue(reverse=True)

			# Now that Minors are sorted, ACTUALLY figure out what our Approach will be, taking everything into account
			for loopPlayer, _ in playerApproachWeights.items():
				# See which Approach is best
				_, approach = self.bestApproachTowardsMinorCiv(loopPlayer, lookAtOtherPlayers=True, log=True, simulation=simulation)
				# lastTurnApproach = (MinorCivApproachTypes) m_paeApproachScratchPad[eLoopPlayer]
				self.updateMinorCivApproachTowards(loopPlayer, approach)

		return

	def updateProximities(self, simulation):
		for otherPlayer in simulation.players:
			if otherPlayer.leader != self.player.leader and self.player.hasMetWith(otherPlayer):
				self.updateProximityTo(otherPlayer, simulation)

	def updateProximityTo(self, otherPlayer, simulation):
		smallestDistanceBetweenCities = sys.maxsize
		averageDistanceBetweenCities = 0
		numCityConnections = 0

		# Loop through all of MY Cities
		for myCity in simulation.citiesOf(self.player):
			# Loop through all of THEIR Cities
			for otherCity in simulation.citiesOf(otherPlayer):
				numCityConnections += 1
				distance = myCity.location.distance(otherCity.location)

				if distance < smallestDistanceBetweenCities:
					smallestDistanceBetweenCities = distance

				averageDistanceBetweenCities += distance

		# Seed this value with something reasonable to start.This will be the value assigned if one player has 0 Cities.
		proximity: PlayerProximityType = PlayerProximityType.none

		if numCityConnections > 0:
			averageDistanceBetweenCities /= numCityConnections

			if smallestDistanceBetweenCities <= 7:  # PROXIMITY_NEIGHBORS_CLOSEST_CITY_REQUIREMENT
				# Closest Cities must be within a certain range
				proximity = PlayerProximityType.neighbors
			elif smallestDistanceBetweenCities <= 11:
				# If our closest Cities are pretty near one another and our average is less than the max then we
				# can be considered CLOSE (will also look at City average below)
				proximity = PlayerProximityType.close

			if proximity == PlayerProximityType.none:
				mapFactor = (simulation.mapSize().size().width() + simulation.mapSize().size().height()) / 2

				# Normally base distance on map size, but cap it at a certain point
				closeDistance = mapFactor * 25 / 100  # PROXIMITY_CLOSE_DISTANCE_MAP_MULTIPLIER

				if closeDistance > 20:  # PROXIMITY_CLOSE_DISTANCE_MAX
					# Close can't be so big that it sits on Far's turf
					closeDistance = 20  # PROXIMITY_CLOSE_DISTANCE_MAX
				elif closeDistance < 10:  # PROXIMITY_CLOSE_DISTANCE_MIN
					# Close also can't be so small that it sits on Neighbor's turf
					closeDistance = 10  # PROXIMITY_CLOSE_DISTANCE_MIN

				farDistance = mapFactor * 45 / 100  # PROXIMITY_FAR_DISTANCE_MAP_MULTIPLIER

				if farDistance > 50:  # PROXIMITY_CLOSE_DISTANCE_MAX
					# Far can't be so big that it sits on Distant's turf
					farDistance = 50  # PROXIMITY_CLOSE_DISTANCE_MAX
				elif farDistance < 20:  # PROXIMITY_CLOSE_DISTANCE_MIN
					# Close also can't be so small that it sits on Neighbor's turf
					farDistance = 20  # PROXIMITY_CLOSE_DISTANCE_MIN

				if averageDistanceBetweenCities <= closeDistance:
					proximity = PlayerProximityType.close
				elif averageDistanceBetweenCities <= farDistance:
					proximity = PlayerProximityType.far
				else:
					proximity = PlayerProximityType.distant

			# Players NOT on the same landmass - bump up PROXIMITY by one level (unless we're already distant)
			if proximity != PlayerProximityType.distant:
				# FIXME
				pass

		numPlayerLeft = len(list(filter(lambda p: p.isAlive(), simulation.players)))
		if numPlayerLeft == 2:
			proximity = proximity if proximity > PlayerProximityType.close else PlayerProximityType.close
		elif numPlayerLeft <= 4:
			proximity = proximity if proximity > PlayerProximityType.far else PlayerProximityType.far

		self.playerDict.updateProximityTo(otherPlayer, proximity)

	def doContactMajorCivs(self, simulation):
		"""Anyone we want to chat with?"""
		# NOTE: This function is broken up into two sections: AI contact opportunities, and then human contact opportunities
		# This is to prevent a nasty bug where the AI will continue making decisions as the diplo screen is firing up. Making humans
		# handled at the end prevents the Diplo AI from having this problem
		# Loop through AI Players
		for loopPlayer in simulation.players:
			if not self.isValid(loopPlayer):
				continue

			# No humans
			if loopPlayer.isHuman():
				continue

			self.doContactPlayer(loopPlayer, simulation)

		# Loop through HUMAN Players - if we're not in MP
		for loopPlayer in simulation.players:
			if not self.isValid(loopPlayer):
				continue

			if not loopPlayer.isHuman():
				continue

			self.doContactPlayer(loopPlayer, simulation)

		return

	def doContactPlayer(self, otherPlayer, simulation):
		"""Individual contact opportunity"""
		if not self.isValidUIDiplomacyTarget(otherPlayer):
			return  # Can't contact the UI for this player at the moment.

		# We can use this deal pointer to form a trade offer
		deal = DiplomaticDeal(self.player, otherPlayer)

		# These can be used for info about deal items, e.g.what Minor Civ we're telling the guy to stay away from, etc.

		# If this is the same turn we've met a player, don't send anything his way quite yet -
		# wait until we've said hello at least
		if self.player.turnsSinceMeetingWith(otherPlayer) == 0:
			return

		# Clear out the scratch pad
		for diplomaticStatement in list(DiplomaticStatementType):
			self._paDiploLogStatementTurnCountScratchPad.setWeight(constants.maxTurnsSafeEstimate, diplomaticStatement)  # MAX_TURNS_SAFE_ESTIMATE

		# Make a scratch pad keeping track of the last time we sent each message. This way we can know what we've said in the past already - this member array will be used in the function calls below
		# for (iDiploLogStatement = 0 iDiploLogStatement < MAX_DIPLO_LOG_STATEMENTS iDiploLogStatement++)
		# 	{
		# 		eStatement = GetDiploLogStatementTypeForIndex(otherPlayer, iDiploLogStatement)
		#
		# 	if (eStatement != NO_DIPLO_STATEMENT_TYPE)
		# 	{
		# 	CvAssert(eStatement < NUM_DIPLO_LOG_STATEMENT_TYPES)
		#
		# 	m_paDiploLogStatementTurnCountScratchPad[eStatement] = GetDiploLogStatementTurnForIndex(otherPlayer, iDiploLogStatement)
		# 	}
		# 	}
		#
		statement = DiplomaticStatementType.none  # NO_DIPLO_STATEMENT_TYPE

		data1: int = -1
		# data2: int = -1

		# JON: Add in some randomization here?
		# How predictable do we want the AI to be in regard to what state they're in?
		# Note that the order in which the following functions are called is very important to how the AI behaves -
		# first come, first served

		# AT PEACE
		if not self.player.isAtWarWith(otherPlayer):
			statement, data1 = self.doCoopWarTimeStatementWith(otherPlayer, statement, data1, simulation)
			# DoCoopWarStatement(otherPlayer, eStatement, iData1)

			# Some things we don't say to teammates
			if not self.player.isAlliedWith(otherPlayer):
				statement = self.doMakeDemand(otherPlayer, statement, deal)

				# STATEMENTS - all members but otherPlayer passed by address
				statement = self.doAggressiveMilitaryStatementTowards(otherPlayer, statement, simulation)
				# DoKilledCityStateStatement(otherPlayer, eStatement, iData1)
				# DoAttackedCityStateStatement(otherPlayer, eStatement, iData1)
				# DoBulliedCityStateStatement(otherPlayer, eStatement, iData1)
				# --DoSeriousExpansionWarningStatement(otherPlayer, eStatement)
				statement = self.doExpansionWarningStatementTowards(otherPlayer, statement, simulation)
				statement = self.doExpansionBrokenPromiseStatementTowards(otherPlayer, statement)
				# --DoSeriousPlotBuyingWarningStatement(otherPlayer, eStatement)
				statement = self.doPlotBuyingWarningStatementTowards(otherPlayer, statement)
				statement = self.doPlotBuyingBrokenPromiseStatementTowards(otherPlayer, statement)
				#
				# DoWeAttackedYourMinorStatement(otherPlayer, eStatement, iData1)
				# DoWeBulliedYourMinorStatement(otherPlayer, eStatement, iData1)
				#
				# DoKilledYourSpyStatement(otherPlayer, eStatement)
				# DoKilledMySpyStatement(otherPlayer, eStatement)
				# DoCaughtYourSpyStatement(otherPlayer, eStatement)
				#
				# DoTheySupportedOurHosting(otherPlayer, eStatement)
				# DoWeLikedTheirProposal(otherPlayer, eStatement)
				# DoWeDislikedTheirProposal(otherPlayer, eStatement)
				# DoTheySupportedOurProposal(otherPlayer, eStatement)
				# DoTheyFoiledOurProposal(otherPlayer, eStatement)
				#
				# DoConvertedMyCityStatement(otherPlayer, eStatement)
				#
				# DoDugUpMyYardStatement(otherPlayer, eStatement)
				#
				statement = self.doDeclarationOfFriendshipStatementTowards(otherPlayer, statement, simulation)
				# DoDenounceFriendStatement(otherPlayer, eStatement)
				statement = self.doDenounceStatementTowards(otherPlayer, statement, simulation)
				# DoRequestFriendDenounceStatement(otherPlayer, eStatement, iData1)
				# --DoWorkAgainstSomeoneStatement(otherPlayer, eStatement, iData1)
				# --DoEndWorkAgainstSomeoneStatement(otherPlayer, eStatement, iData1)

			# OFFERS - deal is passed by address
			# DoLuxuryTrade(otherPlayer, eStatement, pDeal)
			statement = self.doDelegationExchangeWith(otherPlayer, statement, deal, simulation)
			statement = self.doDelegationOfferTowards(otherPlayer, statement, deal, simulation)
			statement = self.doEmbassyExchangeWith(otherPlayer, statement, deal, simulation)
			statement = self.doEmbassyOfferTowards(otherPlayer, statement, deal, simulation)
			statement = self.doOpenBordersExchangeWith(otherPlayer, statement, deal, simulation)
			statement = self.doOpenBordersOfferTowards(otherPlayer, statement, deal, simulation)
			statement = self.doResearchAgreementOfferTowards(otherPlayer, statement, deal, simulation)
			# DoRenewExpiredDeal(otherPlayer, eStatement, pDeal)
			# DoShareIntrigueStatement(otherPlayer, eStatement)
			# --DoResearchAgreementPlan(otherPlayer, eStatement)

			statement = self.doRequestTowards(otherPlayer, statement, deal, simulation)

			# Second set of things we don't say to teammates
			if not self.player.isAlliedWith(otherPlayer):
				# --DoNowUnforgivableStatement(otherPlayer, eStatement)
				# --DoNowEnemyStatement(otherPlayer, eStatement)

				statement = self.doHostileStatementTowards(otherPlayer, statement, simulation)
				# --DoFriendlyStatement(otherPlayer, eStatement)
				statement = self.doAfraidStatementTowards(otherPlayer, statement)
				statement = self.doWarmongerStatementTowards(otherPlayer, statement, simulation)
				statement, minorPlayer = self.doMinorCivCompetitionStatement(otherPlayer, statement, simulation=simulation)

				# Don't bother with this fluff stuff it's just AI on AI stuff
				if otherPlayer.isHuman():
					# DoAngryBefriendedEnemy(otherPlayer, eStatement, iData1)
					# DoAngryDenouncedFriend(otherPlayer, eStatement, iData1)
					# DoHappyDenouncedEnemy(otherPlayer, eStatement, iData1)
					# DoHappyBefriendedFriend(otherPlayer, eStatement, iData1)
					# DoFYIBefriendedHumanEnemy(otherPlayer, eStatement, iData1)
					# DoFYIDenouncedHumanFriend(otherPlayer, eStatement, iData1)
					# DoFYIDenouncedHumanEnemy(otherPlayer, eStatement, iData1)
					# DoFYIBefriendedHumanFriend(otherPlayer, eStatement, iData1)
					# DoHappySamePolicyTree(otherPlayer, eStatement)
					statement = self.doIdeologicalStatementTowards(otherPlayer, statement)

		# AT WAR
		else:  # (!GC.getGame().isOption(GAMEOPTION_ALWAYS_WAR))
			# OFFERS - all members but otherPlayer passed by address
			statement = self.doPeaceOfferWith(otherPlayer, statement, deal, simulation)

		# Now see if it's a valid time to send this message (we may have already sent it)
		if statement != DiplomaticStatementType.none:  # NO_DIPLO_STATEMENT_TYPE
			# if (bSendStatement):
			self.logStatementToPlayer(otherPlayer, statement)
			self.doSendStatementToPlayer(otherPlayer, statement, data1, deal, simulation)
			self.playerDict.doAddNewStatementToDiploLog(otherPlayer, statement, simulation.currentTurn)

	def logStatementToPlayer(self, otherPlayer, statement: DiplomaticStatementType):
		logging.info(f'send {statement} to {otherPlayer}')
		return

	def doRequestTowards(self, otherPlayer, statement: DiplomaticStatementType, deal: DiplomaticDeal, simulation) -> DiplomaticStatementType:
		"""Possible Contact Statement - Request"""
		if statement == DiplomaticStatementType.none:
			tempStatement = DiplomaticStatementType.request

			# If a request was accepted or rejected, wait 60 turns.
			# If we rolled for rand and failed, wait 15 turns before we try again
			if (self.playerDict.numberOfTurnsSinceStatementSent(otherPlayer, tempStatement) >= 60 and
				self.playerDict.numberOfTurnsSinceStatementSent(otherPlayer, DiplomaticStatementType.requestRandFailed) >= 15):

				# This is used to see if we had made a request, but the rand roll failed (so add an entry to the log)
				makeRequest, randPassed = self.isMakeRequest(otherPlayer, deal, simulation)

				# Want to make a request of ePlayer? Pass pDeal in to see if there's actually anything we want
				if makeRequest:
					statement = tempStatement
					deal.updateRequestingPlayer(self.player)
				else:  # Clear out the deal if we don't want to offer it so that it's not tainted for the next trade possibility we look at
					deal.clearItems()

				# Add this statement to the log, so we don't evaluate it again until 15 turns has come back around
				if not randPassed:
					self.playerDict.doAddNewStatementToDiploLog(otherPlayer, DiplomaticStatementType.requestRandFailed, simulation.currentTurn)

		return statement

	def doCoopWarTimeStatementWith(self, otherPlayer, statement: DiplomaticStatementType, data1: int, simulation) -> (DiplomaticStatementType, int):
		"""Possible Contact Statement"""
		if statement == DiplomaticStatementType.none:  # NO_DIPLO_STATEMENT_TYPE
			# Don't send this to AI players - coop war timer is automatically handled in DoCounters()
			if not otherPlayer.isHuman():
				return statement, data1

			for loopPlayer in simulation.players:
				# Agreed to go to war soon...what's the counter at?
				if self.playerDict.coopWarAcceptedStateOf(otherPlayer, loopPlayer) == CoopWarStateType.soon:  # COOP_WAR_STATE_SOON
					if self.playerDict.coopWarCounterWith(otherPlayer, loopPlayer) == 10:  # COOP_WAR_SOON_COUNTER
						# If we're already at war, don't bother
						if not self.player.isAtWarWith(loopPlayer) and loopPlayer.isAlive():
							statement = DiplomaticStatementType.coopWarTime  # DIPLO_STATEMENT_COOP_WAR_TIME
							data1 = hash(loopPlayer)

							# Don't evaluate other players
							break
						# Human is already at war - process what we would have if he'd agreed at this point
						else:
							self.playerDict.updateCoopWarAcceptedState(otherPlayer, loopPlayer, CoopWarStateType.accepted)

							# AI declaration
							if not self.isAtWarWith(loopPlayer) and loopPlayer.isAlive():
								self.doDeclareWarTo(loopPlayer, simulation)
								self.player.militaryAI.requestBasicAttackTowards(loopPlayer, 1, simulation)

		return statement, data1

	def doPeaceOfferWith(self, otherPlayer, statement: DiplomaticStatementType, deal: DiplomaticDeal, simulation) -> DiplomaticStatementType:
		"""Possible Contact Statement - Peace"""
		if statement == DiplomaticStatementType.none:  # NO_DIPLO_STATEMENT_TYPE
			otherDiplomacyAI = otherPlayer.diplomacyAI

			# Have to have been at war for at least a little while
			if self.playerDict.turnsAtWarWith(otherPlayer, simulation.currentTurn) > 5:
				# We can't be locked into war with them, or them with us
				if self.playerDict.numberOfTurnsLockedIntoWarWith(otherPlayer) == 0 and \
					otherDiplomacyAI.numberOfTurnsLockedIntoWarWith(self.player) == 0:
					if self.isWantsPeaceWith(otherPlayer):
						tempStatement: DiplomaticStatementType = DiplomaticStatementType.requestPeace  # DIPLO_STATEMENT_REQUEST_PEACE
						turnsBetweenStatements: int = 10

						if self.playerDict.numberOfTurnsSinceStatementSent(otherPlayer, tempStatement) >= turnsBetweenStatements:
							# deal can be modified in this function
							if self.player.dealAI.isOfferPeace(otherPlayer, deal, equalizingDeals=False):
								statement = tempStatement
							else:
								# Clear out the deal if we don't want to offer it so that it's not tainted
								# for the next trade possibility we look at
								deal.clearItems()

		return statement

	def isWantsPeaceWith(self, otherPlayer) -> bool:
		"""Do we actually want peace with otherPlayer? - IsWantsPeaceWithPlayer"""
		requestPeaceTurnThreshold: int = 4  # REQUEST_PEACE_TURN_THRESHOLD

		if not self.canChangeWarPeaceWith(otherPlayer):
			return False

		if self.playerDict.wantPeaceCounterWith(otherPlayer) >= requestPeaceTurnThreshold:
			return True

		return False

	def doMakeDemand(self, otherPlayer, statement: DiplomaticStatementType, deal: DiplomaticDeal) -> DiplomaticStatementType:
		"""Possible Contact Statement - Demand"""
		if statement == DiplomaticStatementType.none:
			if self.demandTargetPlayer() is not None and self.demandTargetPlayer() == otherPlayer:
				if self.isDemandReady():
					# deal can be modified in this function
					if self.player.dealAI.isMakeDemand(otherPlayer, deal):
						tempStatement: DiplomaticStatementType = DiplomaticStatementType.demand  # DIPLO_STATEMENT_DEMAND
						turnsBetweenStatements: int = 40

						if self.playerDict.numberOfTurnsSinceStatementSent(otherPlayer, tempStatement) >= turnsBetweenStatements:
							statement = tempStatement
						else:
							# Clear out the deal if we don't want to offer it so that it's not tainted for the
							# next trade possibility we look at
							deal.clearItems()

		return statement

	def doDelegationExchangeWith(self, otherPlayer, statement: DiplomaticStatementType, deal: DiplomaticDeal, simulation) -> DiplomaticStatementType:
		"""Possible Contact Statement - delegation Exchange"""
		if statement == DiplomaticStatementType.none:
			# Can both sides send a delegation?
			if deal.isPossibleToTradeItem(self.player, otherPlayer, DiplomaticDealItemType.allowDelegation, simulation=simulation) and \
				deal.isPossibleToTradeItem(otherPlayer, self.player, DiplomaticDealItemType.allowDelegation, simulation=simulation):

				# Does this guy want to exchange embassies?
				if self.isDelegationExchangeAcceptable(otherPlayer):
					tempStatement: DiplomaticStatementType = DiplomaticStatementType.delegationExchange
					turnsBetweenStatements: int = 20

					if self.playerDict.numberOfTurnsSinceStatementSent(otherPlayer, tempStatement) >= turnsBetweenStatements and \
						self.playerDict.numberOfTurnsSinceStatementSent(otherPlayer, DiplomaticStatementType.delegationOffer) >= turnsBetweenStatements:

						sendStatement: bool = False

						# AI
						if not otherPlayer.isHuman():
							if otherPlayer.diplomacyAI.isDelegationExchangeAcceptable(self.player):
								sendStatement = True
						# Human
						else:
							sendStatement = True

						# 1 in 2 chance we don't actually send the message (don't want full predictability)
						if not Tests.are_running and 50 < random.randint(0, 100):  # Diplomacy AI: rand roll to see if we ask to exchange embassies
							sendStatement = False

						if sendStatement:
							deal.addSendDelegationTowards(self.player, simulation)
							deal.addSendDelegationTowards(otherPlayer, simulation)

							statement = tempStatement
						else:
							self.playerDict.doAddNewStatementToDiploLog(otherPlayer, tempStatement, simulation.currentTurn)

		return statement

	def doDelegationOfferTowards(self, otherPlayer, statement: DiplomaticStatementType, deal: DiplomaticDeal, simulation) -> DiplomaticStatementType:
		"""Possible Contact Statement - delegation offer"""
		if statement == DiplomaticStatementType.none:
			if self.player.dealAI.makeOfferForDelegationTowards(otherPlayer, deal, simulation):
				tempStatement:DiplomaticStatementType = DiplomaticStatementType.delegationOffer
				turnsBetweenStatements: int = 20

				if self.playerDict.numberOfTurnsSinceStatementSent(otherPlayer, tempStatement) >= turnsBetweenStatements and \
					self.playerDict.numberOfTurnsSinceStatementSent(otherPlayer, DiplomaticStatementType.delegationExchange) >= 10:
					statement = tempStatement
			else:
				# Clear out the deal if we don't want to offer it so that it's not tainted for the next trade possibility we look at
				deal.clearItems()

		return statement

	def isDelegationExchangeAcceptable(self, otherPlayer) -> bool:
		"""If your relationship with a rival is worse than Neutral they will not accept your delegation/Embassy."""
		if self.player.isBarbarian() or self.player.isCityState():
			return False

		if otherPlayer.isBarbarian() or otherPlayer.isCityState():
			return False

		if not self.player.hasMetWith(otherPlayer):
			return False

		if self.player.civics.hasCivic(CivicType.diplomaticService):
			return False

		approach: MajorPlayerApproachType = self.player.diplomacyAI.majorCivApproachTowards(otherPlayer)

		return approach >= MajorPlayerApproachType.neutral

	def isEmbassyExchangeAcceptable(self, otherPlayer) -> bool:
		"""If your relationship with a rival is worse than Neutral they will not accept your delegation/Embassy."""
		if self.player.isBarbarian() or self.player.isCityState():
			return False

		if otherPlayer.isBarbarian() or otherPlayer.isCityState():
			return False

		if not self.player.hasMetWith(otherPlayer):
			return False

		if not self.player.civics.hasCivic(CivicType.diplomaticService):
			return False

		approach: MajorPlayerApproachType = self.player.diplomacyAI.majorCivApproachTowards(otherPlayer)

		return approach >= MajorPlayerApproachType.neutral

	def demandTargetPlayer(self):
		"""Is there a player we're targeting to make a demand from, backed with force?"""
		return self._demandTargetPlayer

	def updateDemandTargetPlayer(self, otherPlayer):
		"""Sets a player we're targeting to make a demand from, backed with force"""
		self._demandTargetPlayer = otherPlayer

	def doSendStatementToPlayer(self, otherPlayer, statement: DiplomaticStatementType, data1: int, deal: DiplomaticDeal, simulation):
		human: bool = otherPlayer.isHuman()
		shouldShowLeaderScene: bool = human

		# Aggressive Military warning
		if statement == DiplomaticStatementType.aggressiveMilitaryWarning:  # DIPLO_STATEMENT_AGGRESSIVE_MILITARY_WARNING)
			if shouldShowLeaderScene:
				if self.isActHostileTowardsHuman(otherPlayer, simulation):
					szText = DiplomaticRequestMessage.hostileAggressiveMilitaryWarning.text()  # DIPLO_MESSAGE_HOSTILE_AGGRESSIVE_MILITARY_WARNING
				else:
					szText = DiplomaticRequestMessage.aggressiveMilitaryWarning.text()  # DIPLO_MESSAGE_AGGRESSIVE_MILITARY_WARNING
				DiplomacyRequests.sendRequest(self.player, otherPlayer, DiplomaticRequestState.discussAggressiveMilitaryWarning, szText, LeaderEmotionType.negative)
		# Player Killed a City State we're protecting
		# 	elif statement == DIPLO_STATEMENT_KILLED_PROTECTED_CITY_STATE
		# 		if shouldShowLeaderScene:
		# 			PlayerTypes eMinorCiv = (PlayerTypes) iData1
		# 			CvAssert(eMinorCiv != NO_PLAYER)
		# 			if(eMinorCiv != NO_PLAYER)
		# 			{
		# 				const char* strMinorCivKey = GET_PLAYER(eMinorCiv).getNameKey()
		#
		# 				szText = GetDiploStringForMessage(DIPLO_MESSAGE_HUMAN_KILLED_PROTECTED_CITY_STATE, NO_PLAYER, strMinorCivKey)
		# 				DiplomacyRequests.sendRequest(self.player.GetID(), otherPlayer, DIPLO_UI_STATE_BLANK_DISCUSSION_MEAN_HUMAN, szText, LeaderEmotionType.hateNegative)
		# 			}
		# 		}
		# 	}
		#
		# Player Attacked a City State we're protecting
		# 	elif statement == DIPLO_STATEMENT_ATTACKED_PROTECTED_CITY_STATE
		# 		if shouldShowLeaderScene:
		# 			PlayerTypes eMinorCiv = (PlayerTypes) iData1
		# 			CvAssert(eMinorCiv != NO_PLAYER)
		# 			if(eMinorCiv != NO_PLAYER)
		# 			{
		# 				const char* strMinorCivKey = GET_PLAYER(eMinorCiv).getNameKey()
		#
		# 				szText = GetDiploStringForMessage(DIPLO_MESSAGE_HUMAN_ATTACKED_PROTECTED_CITY_STATE, NO_PLAYER, strMinorCivKey)
		# 				DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_DISCUSS_YOU_ATTACKED_MINOR_CIV, szText, LeaderEmotionType.hateNegative)
		# 			}
		# 		}
		# 	}
		#
		# Player Bullied a City State we're protecting
		# 	elif statement == DIPLO_STATEMENT_BULLIED_PROTECTED_CITY_STATE
		# 		if shouldShowLeaderScene:
		# 			PlayerTypes eMinorCiv = (PlayerTypes) iData1
		# 			CvAssert(eMinorCiv != NO_PLAYER)
		# 			if(eMinorCiv != NO_PLAYER)
		# 			{
		# 				const char* strMinorCivKey = GET_PLAYER(eMinorCiv).getNameKey()
		#
		# 				szText = GetDiploStringForMessage(DIPLO_MESSAGE_HUMAN_BULLIED_PROTECTED_CITY_STATE, NO_PLAYER, strMinorCivKey)
		# 				DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_DISCUSS_YOU_BULLIED_MINOR_CIV, szText, LeaderEmotionType.hateNegative)
		# 			}
		# 		}
		# 	}
		#
		# Serious Expansion warning
		elif statement == DiplomaticStatementType.expansionSeriousWarning:
			if shouldShowLeaderScene:
				szText: str = DiplomaticRequestMessage.expansionSeriousWarning.text()  # DIPLO_MESSAGE_EXPANSION_SERIOUS_WARNING
				DiplomacyRequests.sendRequest(self.player, otherPlayer, DiplomaticRequestState.discussYouExpansionSeriousWarning, szText, LeaderEmotionType.hateNegative)

		# Expansion warning
		elif statement == DiplomaticStatementType.expansionWarning:
			if shouldShowLeaderScene:
				szText: str = DiplomaticRequestMessage.expansionWarning.text()  # DIPLO_MESSAGE_EXPANSION_WARNING
				DiplomacyRequests.sendRequest(self.player, otherPlayer, DiplomaticRequestState.discussYouExpansionWarning, szText, LeaderEmotionType.negative)

		# Expansion Broken Promise
		# 	elif statement == DIPLO_STATEMENT_EXPANSION_BROKEN_PROMISE
		# 		if shouldShowLeaderScene:
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_EXPANSION_BROKEN_PROMISE)
		# 			DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_BLANK_DISCUSSION_MEAN_HUMAN, szText, LeaderEmotionType.hateNegative)
		# 		}
		# 	}
		#
		# Serious Plot Buying warning
		# 	elif statement == DIPLO_STATEMENT_PLOT_BUYING_SERIOUS_WARNING
		# 		if shouldShowLeaderScene:
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_PLOT_BUYING_SERIOUS_WARNING)
		# 			DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_DISCUSS_YOU_PLOT_BUYING_SERIOUS_WARNING, szText, LeaderEmotionType.hateNegative)
		# 		}
		# 	}
		#
		# Plot Buying warning
		# 	elif statement == DIPLO_STATEMENT_PLOT_BUYING_WARNING
		# 		if shouldShowLeaderScene:
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_PLOT_BUYING_WARNING)
		# 			DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_DISCUSS_YOU_PLOT_BUYING_WARNING, szText, LeaderEmotionType.negative)
		# 		}
		# 	}
		#
		# Plot Buying broken promise
		# 	elif statement == DIPLO_STATEMENT_PLOT_BUYING_BROKEN_PROMISE
		# 		if shouldShowLeaderScene:
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_PLOT_BUYING_BROKEN_PROMISE)
		# 			DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_BLANK_DISCUSSION_MEAN_HUMAN, szText, LeaderEmotionType.hateNegative)
		# 		}
		# 	}
		#
		# We attacked a Minor someone has a PtP with
		# 	elif statement == DIPLO_STATEMENT_WE_ATTACKED_YOUR_MINOR
		# 		if shouldShowLeaderScene:
		# 			PlayerTypes eMinorCiv = (PlayerTypes) iData1
		# 			CvAssert(eMinorCiv != NO_PLAYER)
		# 			if(eMinorCiv != NO_PLAYER)
		# 			{
		# 				const char* strMinorCivKey = GET_PLAYER(eMinorCiv).getNameKey()
		# 				if(IsActHostileTowardsHuman(otherPlayer, simulation))
		# 					szText = GetDiploStringForMessage(DIPLO_MESSAGE_HOSTILE_WE_ATTACKED_YOUR_MINOR, NO_PLAYER, strMinorCivKey)
		# 				else
		# 					szText = GetDiploStringForMessage(DIPLO_MESSAGE_WE_ATTACKED_YOUR_MINOR, NO_PLAYER, strMinorCivKey)
		#
		# 				DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_DISCUSS_I_ATTACKED_YOUR_MINOR_CIV, szText, LeaderEmotionType.positive, eMinorCiv)
		#
		# 				// Extra flag, since diplo log does not save which minor civ the message was about
		# 				SetSentAttackProtectedMinorTaunt(otherPlayer, eMinorCiv, true)
		# 			}
		# 		}
		# 	}
		#
		# We bullied a Minor someone has a PtP with
		# 	elif statement == 	DIPLO_STATEMENT_WE_BULLIED_YOUR_MINOR
		# 		if shouldShowLeaderScene:
		# 			PlayerTypes eMinorCiv = (PlayerTypes) iData1
		# 			CvAssert(eMinorCiv != NO_PLAYER)
		# 			if (eMinorCiv != NO_PLAYER)
		# 			{
		# 				const char* strMinorCivKey = GET_PLAYER(eMinorCiv).getNameKey()
		# 				if(IsActHostileTowardsHuman(otherPlayer, simulation))
		# 					szText = GetDiploStringForMessage(DIPLO_MESSAGE_HOSTILE_WE_BULLIED_YOUR_MINOR, NO_PLAYER, strMinorCivKey)
		# 				else
		# 					szText = GetDiploStringForMessage(DIPLO_MESSAGE_WE_BULLIED_YOUR_MINOR, NO_PLAYER, strMinorCivKey)
		#
		# 				DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_DISCUSS_I_BULLIED_YOUR_MINOR_CIV, szText, LeaderEmotionType.positive, eMinorCiv)
		# 			}
		# 		}
		# 	}
		#
		# We'd like to work with a player
		# 	elif statement == DIPLO_STATEMENT_WORK_WITH_US
		# 		// Send message to human
		# 		if shouldShowLeaderScene:
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_WORK_WITH_US)
		#
		# 			DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_DISCUSS_WORK_WITH_US, szText, LeaderEmotionType.request)
		# 		}
		# 		// AI resolution
		# 		elif not human:
		# 		{
		# 			SetDoFCounter(otherPlayer, 0)
		# 			GET_PLAYER(otherPlayer).GetDiplomacyAI()->SetDoFCounter(self.player, 0)
		#
		# 			// Accept - reject is assumed from the counter
		# 			if(GET_PLAYER(otherPlayer).GetDiplomacyAI()->IsDoFAcceptable(self.player))
		# 			{
		# 				SetDoFAccepted(otherPlayer, true)
		# 				GET_PLAYER(otherPlayer).GetDiplomacyAI()->SetDoFAccepted(self.player, true)
		#
		# 				LogDoF(otherPlayer)
		# 			}
		# 		}
		# 	}
		#
		# We no longer want to work with a player
		# 	elif statement == DIPLO_STATEMENT_END_WORK_WITH_US
		# 		SetDoFAccepted(otherPlayer, false)
		# 		SetDoFCounter(otherPlayer, -666)
		#
		# 		// If we had agreed to not settle near the player, break that off
		# 		SetPlayerNoSettleRequestAccepted(otherPlayer, false)
		# 		SetPlayerNoSettleRequestCounter(otherPlayer, -666)
		#
		# 		// If we had agreed to not spy on the player, break that off
		# 		SetPlayerStopSpyingRequestAccepted(otherPlayer, false)
		# 		SetPlayerStopSpyingRequestCounter(otherPlayer, -666)
		#
		# 		// Send message to human
		# 		if shouldShowLeaderScene:
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_END_WORK_WITH_US, otherPlayer)
		#
		# 			DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_BLANK_DISCUSSION_MEAN_AI, szText, LeaderEmotionType.negative)
		# 		}
		# 		elif not human:
		# 		{
		# 			GET_PLAYER(otherPlayer).GetDiplomacyAI()->SetDoFAccepted(self.player, false)
		# 			GET_PLAYER(otherPlayer).GetDiplomacyAI()->SetDoFCounter(self.player, -666)
		# 		}
		# 	}
		#
		# Denounce
		# 	elif statement == DIPLO_STATEMENT_DENOUNCE
		# 		DoDenouncePlayer(otherPlayer)
		# 		LogDenounce(otherPlayer)
		#
		# 		// Send message to human
		# 		if shouldShowLeaderScene:
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_WORK_AGAINST_SOMEONE, otherPlayer)
		#
		# 			DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_BLANK_DISCUSSION_MEAN_AI, szText, LeaderEmotionType.hateNegative)
		# 		}
		# 	}
		#
		# Denounce Friend (backstab)
		# 	elif statement == DIPLO_STATEMENT_DENOUNCE_FRIEND
		# 		DoDenouncePlayer(otherPlayer)
		# 		LogDenounce(otherPlayer, /*bBackstab*/ true)
		#
		# 		// Send message to human
		# 		if shouldShowLeaderScene:
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_AI_DOF_BACKSTAB, otherPlayer)
		#
		# 			DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_BLANK_DISCUSSION, szText, LeaderEmotionType.hateNegative)
		# 		}
		# 	}
		#
		# Request Friend Denounce Someone
		# 	elif statement == DIPLO_STATEMENT_REQUEST_FRIEND_DENOUNCE
		# 		PlayerTypes eTarget = (PlayerTypes) iData1
		# 		CvAssert(eTarget != NO_PLAYER)
		# 		if(eTarget != NO_PLAYER)
		# 		{
		# 			const char* strTargetCivKey = GET_PLAYER(eTarget).getCivilizationShortDescriptionKey()
		#
		# 			// Send message to human
		# 			if(bShouldShowLeaderScene)
		# 			{
		# 				szText = GetDiploStringForMessage(DIPLO_MESSAGE_DOF_AI_DENOUNCE_REQUEST, otherPlayer, strTargetCivKey)
		#
		# 				DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_DISCUSS_AI_REQUEST_DENOUNCE, szText, LeaderEmotionType.positive, eTarget)
		# 			}
		# 			elif not human:
		# 			{
		# 				bool bAgree = IsDenounceAcceptable(eTarget, /*bBias*/ true)
		#
		# 				LogFriendRequestDenounce(otherPlayer, eTarget, bAgree)
		#
		# 				if(bAgree)
		# 				{
		# 					GET_PLAYER(otherPlayer).GetDiplomacyAI()->DoDenouncePlayer(eTarget)
		# 					GET_PLAYER(otherPlayer).GetDiplomacyAI()->LogDenounce(eTarget)
		#
		# 					// Denounced a human?
		# 					if(eTarget == GC.getGame().getActivePlayer())
		# 					{
		# 						szText = GetDiploStringForMessage(DIPLO_MESSAGE_WORK_AGAINST_SOMEONE, eTarget)
		# 						DiplomacyRequests.sendDealRequest(otherPlayer, eTarget, DIPLO_UI_STATE_BLANK_DISCUSSION_MEAN_AI, szText, LeaderEmotionType.hateNegative)
		# 					}
		# 				}
		# 				else
		# 				{
		# 					// Oh, you're gonna say no, are you?
		# 					if(IsFriendDenounceRefusalUnacceptable(otherPlayer, eTarget))
		# 					{
		# 						DoDenouncePlayer(otherPlayer)
		# 						LogDenounce(otherPlayer, /*bBackstab*/ false, /*bRefusal*/ true)
		# 					}
		# 				}
		# 			}
		# 		}
		# 	}
		#
		# We'd like to declare war on someone
		# 	elif statement == DIPLO_STATEMENT_COOP_WAR_REQUEST
		# 		PlayerTypes eAgainstPlayer = (PlayerTypes) iData1
		# 		CvAssert(eAgainstPlayer != NO_PLAYER)
		# 		if(eAgainstPlayer != NO_PLAYER)
		# 		{
		# 			// Send message to human
		# 			if(bShouldShowLeaderScene)
		# 			{
		# 				const char* strAgainstPlayerKey = GET_PLAYER(eAgainstPlayer).getNameKey()
		# 				szText = GetDiploStringForMessage(DIPLO_MESSAGE_COOP_WAR_REQUEST, otherPlayer, strAgainstPlayerKey)
		#
		# 				DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_DISCUSS_COOP_WAR, szText, LeaderEmotionType.positive, eAgainstPlayer)
		# 			}
		# 			// AI resolution
		# 			elif not human:
		# 			{
		# 				SetCoopWarCounter(otherPlayer, eAgainstPlayer, 0)
		# 				GET_PLAYER(otherPlayer).GetDiplomacyAI()->SetCoopWarCounter(self.player, eAgainstPlayer, 0)
		#
		# 				// Will they agree?
		# 				CoopWarStates eAcceptedState = GET_PLAYER(otherPlayer).GetDiplomacyAI()->GetWillingToAgreeToCoopWarState(self.player, eAgainstPlayer)
		# 				GET_PLAYER(otherPlayer).GetDiplomacyAI()->SetCoopWarAcceptedState(self.player, eAgainstPlayer, eAcceptedState)
		#
		# 				if(eAcceptedState == COOP_WAR_STATE_ACCEPTED)
		# 				{
		# 					DeclareWar(eAgainstPlayer)
		# 					GetPlayer()->GetMilitaryAI()->RequestBasicAttack(eAgainstPlayer, 1)
		#
		# 					GET_PLAYER(otherPlayer).GetDiplomacyAI()->DeclareWar(eAgainstPlayer)
		# 					GET_PLAYER(otherPlayer).GetMilitaryAI()->RequestBasicAttack(eAgainstPlayer, 1)
		#
		# 					int iLockedTurns = 15  # COOP_WAR_LOCKED_LENGTH()
		# 					GET_TEAM(GetPlayer()->getTeam()).ChangeNumTurnsLockedIntoWar(GET_PLAYER(eAgainstPlayer).getTeam(), iLockedTurns)
		# 					GET_TEAM(GET_PLAYER(otherPlayer).getTeam()).ChangeNumTurnsLockedIntoWar(GET_PLAYER(eAgainstPlayer).getTeam(), iLockedTurns)
		# 				}
		#
		# 				LogCoopWar(otherPlayer, eAgainstPlayer, eAcceptedState)
		#
		# 				// If the other player didn't agree then we don't need to change our state from what it was (NO_STATE)
		# 				if(eAcceptedState != COOP_WAR_STATE_REJECTED)
		# 					SetCoopWarAcceptedState(otherPlayer, eAgainstPlayer, eAcceptedState)
		# 			}
		# 		}
		# 	}
		#
		# We'd like to declare war on someone
		# 	elif statement == DIPLO_STATEMENT_COOP_WAR_TIME
		# 		PlayerTypes eAgainstPlayer = (PlayerTypes) iData1
		# 		CvAssert(eAgainstPlayer != NO_PLAYER)
		# 		if(eAgainstPlayer != NO_PLAYER)
		# 		{
		# 			// Send message to human
		# 			if(bShouldShowLeaderScene)
		# 			{
		# 				const char* strAgainstPlayerKey = GET_PLAYER(eAgainstPlayer).getNameKey()
		# 				szText = GetDiploStringForMessage(DIPLO_MESSAGE_COOP_WAR_TIME, otherPlayer, strAgainstPlayerKey)
		#
		# 				DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_DISCUSS_COOP_WAR_TIME, szText, LeaderEmotionType.positive, eAgainstPlayer)
		# 			}
		# 		}
		#
		# 		// No AI resolution! This is handled automatically in DoCounters() - no need for diplo exchange
		# 	}
		#
		# We're making a demand of Player
		# 	elif statement == DIPLO_STATEMENT_DEMAND
		# 		// Active human
		# 		if shouldShowLeaderScene:
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_DEMAND)
		# 			CvDiplomacyRequests::SendDealRequest(self.player, otherPlayer, pDeal, DIPLO_UI_STATE_TRADE_AI_MAKES_DEMAND, szText, LeaderEmotionType.demand)
		# 		}
		# 		// AI player
		# 		elif not human:
		# 		{
		# 			// For now the AI will always give in
		#
		# 			CvDeal kDeal = *pDeal
		#
		# 			GC.getGame().GetGameDeals()->AddProposedDeal(kDeal)
		# 			GC.getGame().GetGameDeals()->FinalizeDeal(self.player, otherPlayer, true)
		# 		}
		# 	}
		#
		# We're making a request of Player
		# 	elif statement == DIPLO_STATEMENT_REQUEST
		# 		// Active human
		# 		if shouldShowLeaderScene:
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_REQUEST)
		# 			CvDiplomacyRequests::SendDealRequest(self.player, otherPlayer, pDeal, DIPLO_UI_STATE_TRADE_AI_MAKES_REQUEST, szText, LeaderEmotionType.request)
		# 		}
		# 		// AI player
		# 		elif not human:
		# 		{
		# 			// For now the AI will always give in - may eventually write additional logic here
		#
		# 			CvDeal kDeal = *pDeal
		#
		# 			GC.getGame().GetGameDeals()->AddProposedDeal(kDeal)
		# 			GC.getGame().GetGameDeals()->FinalizeDeal(self.player, otherPlayer, true)
		# 		}
		# 	}
		#
		# Player has a Luxury we'd like
		# 	elif statement == DIPLO_STATEMENT_LUXURY_TRADE
		# 		// Active human
		# 		if shouldShowLeaderScene:
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_LUXURY_TRADE)
		# 			CvDiplomacyRequests::SendDealRequest(self.player, otherPlayer, pDeal, DIPLO_UI_STATE_TRADE_AI_MAKES_OFFER, szText, LeaderEmotionType.request)
		# 		}
		# 		// Offer to an AI player
		# 		elif not human:
		# 		{
		# 			CvDeal kDeal = *pDeal
		#
		# 			// Don't need to call DoOffer because we check to see if the deal works for both sides BEFORE sending
		# 			GC.getGame().GetGameDeals()->AddProposedDeal(kDeal)
		# 			GC.getGame().GetGameDeals()->FinalizeDeal(self.player, otherPlayer, true)
		# 		}
		# 	}
		#
		# Offer Delegation Exchange
		elif statement == DiplomaticStatementType.delegationExchange:
			if shouldShowLeaderScene:
				szText = DiplomaticRequestMessage.embassyExchange.text()
				DiplomacyRequests.sendRequest(self.player, otherPlayer, DiplomaticRequestState.tradeAIMakesOffer, szText, LeaderEmotionType.request)
			elif not human:
				# Don't need to call DoOffer because we check to see if the deal works for both sides BEFORE sending
				simulation.gameDeals.addProposedDeal(deal, simulation)
				simulation.gameDeals.finalizeDeal(self.player, otherPlayer, True, simulation)
		# Offer Delegation
		# 	elif statement == DIPLO_STATEMENT_Delegation_OFFER
		# 		if shouldShowLeaderScene:
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_EMBASSY_OFFER)
		# 			CvDiplomacyRequests::SendDealRequest(self.player, otherPlayer, pDeal, DIPLO_UI_STATE_TRADE_AI_MAKES_OFFER, szText, LeaderEmotionType.request)
		# 		}
		# 		elif not human:
		# 		{
		# 			CvDeal kDeal = *pDeal
		#
		# 			// Don't need to call DoOffer because we check to see if the deal works for both sides BEFORE sending
		# 			GC.getGame().GetGameDeals()->AddProposedDeal(kDeal)
		# 			GC.getGame().GetGameDeals()->FinalizeDeal(self.player, otherPlayer, true)
		# 		}
		# 	}
		#
		# Offer Embassy Exchange
		# 	elif statement == DIPLO_STATEMENT_EMBASSY_EXCHANGE
		# 		if shouldShowLeaderScene:
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_EMBASSY_EXCHANGE)
		# 			CvDiplomacyRequests::SendDealRequest(self.player, otherPlayer, pDeal, DIPLO_UI_STATE_TRADE_AI_MAKES_OFFER, szText, LeaderEmotionType.request)
		# 		}
		# 		elif not human:
		# 		{
		# 			CvDeal kDeal = *pDeal
		#
		# 			// Don't need to call DoOffer because we check to see if the deal works for both sides BEFORE sending
		# 			GC.getGame().GetGameDeals()->AddProposedDeal(kDeal)
		# 			GC.getGame().GetGameDeals()->FinalizeDeal(self.player, otherPlayer, true)
		# 		}
		# 	}
		#
		# Offer Embassy
		# 	elif statement == DIPLO_STATEMENT_EMBASSY_OFFER
		# 		if shouldShowLeaderScene:
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_EMBASSY_OFFER)
		# 			CvDiplomacyRequests::SendDealRequest(self.player, otherPlayer, pDeal, DIPLO_UI_STATE_TRADE_AI_MAKES_OFFER, szText, LeaderEmotionType.request)
		# 		}
		# 		elif not human:
		# 		{
		# 			CvDeal kDeal = *pDeal
		#
		# 			// Don't need to call DoOffer because we check to see if the deal works for both sides BEFORE sending
		# 			GC.getGame().GetGameDeals()->AddProposedDeal(kDeal)
		# 			GC.getGame().GetGameDeals()->FinalizeDeal(self.player, otherPlayer, true)
		# 		}
		# 	}
		#
		# Offer Open Borders Exchange
		# 	elif statement == DIPLO_STATEMENT_OPEN_BORDERS_EXCHANGE
		# 		// Active human
		# 		if shouldShowLeaderScene:
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_OPEN_BORDERS_EXCHANGE)
		# 			CvDiplomacyRequests::SendDealRequest(self.player, otherPlayer, pDeal, DIPLO_UI_STATE_TRADE_AI_MAKES_OFFER, szText, LeaderEmotionType.request)
		# 		}
		# 		// Offer to an AI player
		# 		elif not human:
		# 		{
		# 			CvDeal kDeal = *pDeal
		#
		# 			// Don't need to call DoOffer because we check to see if the deal works for both sides BEFORE sending
		# 			GC.getGame().GetGameDeals()->AddProposedDeal(kDeal)
		# 			GC.getGame().GetGameDeals()->FinalizeDeal(self.player, otherPlayer, true)
		# 		}
		# 	}
		#
		# Offer Open Borders
		# 	elif statement == DIPLO_STATEMENT_OPEN_BORDERS_OFFER
		# 		// Active human
		# 		if shouldShowLeaderScene:
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_OPEN_BORDERS_OFFER)
		# 			CvDiplomacyRequests::SendDealRequest(self.player, otherPlayer, pDeal, DIPLO_UI_STATE_TRADE_AI_MAKES_OFFER, szText, LeaderEmotionType.request)
		# 		}
		# 		// Offer to an AI player
		# 		elif not human:
		# 		{
		# 			CvDeal kDeal = *pDeal
		#
		# 			// Don't need to call DoOffer because we check to see if the deal works for both sides BEFORE sending
		# 			GC.getGame().GetGameDeals()->AddProposedDeal(kDeal)
		# 			GC.getGame().GetGameDeals()->FinalizeDeal(self.player, otherPlayer, true)
		# 		}
		# 	}
		#
		# Offer plans to make Research Agreement
		elif statement == DiplomaticStatementType.planResearchAgreement:  # DIPLO_STATEMENT_PLAN_RESEARCH_AGREEMENT
			# Active human
			if shouldShowLeaderScene:
				szText = DiplomaticRequestMessage.planResearchAgreement.text()
				DiplomacyRequests.sendRequest(self.player, otherPlayer, DiplomaticRequestState.discussPlanResearchAgreement, szText, LeaderEmotionType.request)
			# Offer to an AI player
			elif not human:
				if not otherPlayer.diplomacyAI.isWantsResearchAgreementWith(self.player):
					otherPlayer.diplomacyAI.doAddWantsResearchAgreementWith(self.player)  # just auto-reciprocate right now
		# Offer Research Agreement
		# 	elif statement == DIPLO_STATEMENT_RESEARCH_AGREEMENT_OFFER
		# 		// Active human
		# 		if shouldShowLeaderScene:
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_RESEARCH_AGREEMENT_OFFER)
		# 			CvDiplomacyRequests::SendDealRequest(self.player, otherPlayer, pDeal, DIPLO_UI_STATE_TRADE_AI_MAKES_OFFER, szText, LeaderEmotionType.request)
		# 		}
		# 		// Offer to an AI player
		# 		elif not human:
		# 		{
		# 			CvDeal kDeal = *pDeal
		#
		# 			// Don't need to call DoOffer because we check to see if the deal works for both sides BEFORE sending
		# 			GC.getGame().GetGameDeals()->AddProposedDeal(kDeal)
		# 			GC.getGame().GetGameDeals()->FinalizeDeal(self.player, otherPlayer, true)
		# 		}
		# 	}
		#
		# 	// Offer to renew deal
		# 	elif statement == DIPLO_STATEMENT_RENEW_DEAL
		# 		// Active human
		# 		if shouldShowLeaderScene:
		# 			int iDealValueToMe, iValueImOffering, iValueTheyreOffering, iAmountOverWeWillRequest, iAmountUnderWeWillOffer
		# 			DiploMessageTypes eMessageType = NUM_DIPLO_MESSAGE_TYPES
		# 			bool bCantMatchOffer
		# 			bool bDealAcceptable = m_pPlayer->GetDealAI()->IsDealWithHumanAcceptable(pDeal, otherPlayer, iDealValueToMe, iValueImOffering, iValueTheyreOffering, iAmountOverWeWillRequest, iAmountUnderWeWillOffer, bCantMatchOffer)
		#
		# 			if(!bDealAcceptable)
		# 			{
		# 				if(iValueTheyreOffering > iValueImOffering)
		# 				{
		# 					bDealAcceptable = true
		# 				}
		# 			}
		#
		# 			if(bDealAcceptable)
		# 			{
		# 				eMessageType = DIPLO_MESSAGE_RENEW_DEAL
		# 			}
		# 			// We want more from this Deal
		# 			elif(iDealValueToMe > -75 &&
		# 			        iValueImOffering < (iValueTheyreOffering * 5))	// The total value of the deal might not be that bad, but if he's asking for WAY more than he's offering (e.g. something for nothing) then it's not unacceptable, but insulting
		# 			{
		# 				eMessageType = DIPLO_MESSAGE_WANT_MORE_RENEW_DEAL
		# 			}
		# 			else
		# 			{
		# 				CvDeal* pRenewDeal = GetDealToRenew()
		# 				if (pRenewDeal)
		# 				{
		# 					pRenewDeal->m_bCheckedForRenewal = true
		# 				}
		# 				ClearDealToRenew()
		# 			}
		#
		# 			if(eMessageType != NUM_DIPLO_MESSAGE_TYPES)
		# 			{
		# 				CvDeal* pRenewDeal = GetDealToRenew()
		# 				if (pRenewDeal)
		# 				{
		# 					pRenewDeal->m_bCheckedForRenewal = true
		# 				}
		# 				szText = GetDiploStringForMessage(eMessageType)
		# 				CvDiplomacyRequests::SendDealRequest(self.player, otherPlayer, pDeal, DIPLO_UI_STATE_TRADE_AI_MAKES_OFFER, szText, LeaderEmotionType.request)
		# 			}
		# 		}
		# 		// Offer to an AI player
		# 		elif not human:
		# 		{
		# 			CvDeal kDeal = *pDeal
		# 			int iDealType = -1
		# 			CvDeal* pRenewedDeal = m_pPlayer->GetDiplomacyAI()->GetDealToRenew(&iDealType)
		# 			if(pRenewedDeal)
		# 			{
		# 				if (iDealType != 0) // this is not a historic deal, so don't change the resource allocations
		# 				{
		# 					CvGameDeals::PrepareRenewDeal(m_pPlayer->GetDiplomacyAI()->GetDealToRenew(), &kDeal)
		# 				}
		# 				pRenewedDeal->m_bCheckedForRenewal = true
		# 				m_pPlayer->GetDiplomacyAI()->ClearDealToRenew()
		# 			}
		#
		# 			// Don't need to call DoOffer because we check to see if the deal works for both sides BEFORE sending
		# 			GC.getGame().GetGameDeals()->AddProposedDeal(kDeal)
		# 			GC.getGame().GetGameDeals()->FinalizeDeal(self.player, otherPlayer, true)
		# 		}
		# 	}
		#
		# They're now unforgivable
		# 	elif statement == DIPLO_STATEMENT_NOW_UNFORGIVABLE
		# 		if shouldShowLeaderScene:
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_NOW_UNFORGIVABLE)
		# 			DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_BLANK_DISCUSSION_MEAN_HUMAN, szText, LeaderEmotionType.hateNegative)
		# 		}
		# 	}
		#
		# They're now an enemy
		# 	elif statement == DIPLO_STATEMENT_NOW_ENEMY
		# 		if shouldShowLeaderScene:
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_NOW_ENEMY)
		# 			DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_BLANK_DISCUSSION_MEAN_HUMAN, szText, LeaderEmotionType.hateNegative)
		# 		}
		# 	}
		#
		# They caught one of our spies
		# 	elif statement == DIPLO_STATEMENT_CAUGHT_YOUR_SPY
		# 		if shouldShowLeaderScene:
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_CAUGHT_YOUR_SPY)
		# 			DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_CAUGHT_YOUR_SPY, szText, LeaderEmotionType.hateNegative)
		# 		}
		# 	}
		#
		# They killed one of our spies
		# 	elif statement == DIPLO_STATEMENT_KILLED_YOUR_SPY
		# 		if shouldShowLeaderScene:
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_KILLED_YOUR_SPY)
		# 			DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_KILLED_YOUR_SPY, szText, LeaderEmotionType.negative)
		# 		}
		# 	}
		#
		# We killed one of their spies
		# 	elif statement == DIPLO_STATEMENT_KILLED_MY_SPY
		# 		if shouldShowLeaderScene:
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_KILLED_MY_SPY)
		# 			DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_KILLED_MY_SPY, szText, LeaderEmotionType.defeated)
		# 		}
		# 	}
		#
		# We (the AI) have intrigue information to share with them
		# 	elif statement == DIPLO_STATEMENT_SHARE_INTRIGUE
		# 		IntrigueNotificationMessage* pNotificationMessage = GetPlayer()->GetEspionage()->GetRecentIntrigueInfo(otherPlayer)
		# 		CvAssertMsg(pNotificationMessage, "pNotificationMessage is null. Whut?")
		# 		if (pNotificationMessage)
		# 		{
		# 			CvAssertMsg(pNotificationMessage->m_eSourcePlayer != NO_PLAYER, "There is no plotter! What's going on")
		# 			PlayerTypes ePlotterPlayer = pNotificationMessage->m_eSourcePlayer
		# 			CvIntrigueType eIntrigueType = (CvIntrigueType)pNotificationMessage->m_iIntrigueType
		# 			// don't share intrigue about two parties if they are already at war
		# 			if (!GET_TEAM(GET_PLAYER(otherPlayer).getTeam()).isAtWar(GET_PLAYER(ePlotterPlayer).getTeam()))
		# 			{
		# 				CvCity* pCity = NULL
		# 				if(pNotificationMessage->m_iCityX != -1 && pNotificationMessage->m_iCityY != -1)
		# 				{
		# 					CvPlot* pPlot = GC.getMap().plot(pNotificationMessage->m_iCityX, pNotificationMessage->m_iCityY)
		# 					if(pPlot)
		# 					{
		# 						pCity = pPlot->getPlotCity()
		# 					}
		# 				}
		#
		# 				// add the notification to the
		# 				GET_PLAYER(otherPlayer).GetEspionage()->AddIntrigueMessage(m_pPlayer->GetID(), ePlotterPlayer, otherPlayer, NO_BUILDING, NO_PROJECT, eIntrigueType, 0, pCity, false)
		#
		# 				if(bShouldShowLeaderScene)
		# 				{
		# 					const char* szPlayerName
		# 					if(GC.getGame().isGameMultiPlayer() && GET_PLAYER(ePlotterPlayer).isHuman())
		# 					{
		# 						szPlayerName = GET_PLAYER(ePlotterPlayer).getNickName()
		# 					}
		# 					else
		# 					{
		# 						szPlayerName = GET_PLAYER(ePlotterPlayer).getNameKey()
		# 					}
		#
		# 					szText = ""
		#
		# 					switch(eIntrigueType)
		# 					{
		# 					case INTRIGUE_TYPE_ARMY_SNEAK_ATTACK:
		# 						if(pCity)
		# 						{
		# 							szText = GetDiploStringForMessage(DIPLO_MESSAGE_SHARE_INTRIGUE_ARMY_SNEAK_ATTACK_KNOWN_CITY, NO_PLAYER, szPlayerName, pCity->getNameKey())
		# 						}
		# 						else
		# 						{
		# 							szText = GetDiploStringForMessage(DIPLO_MESSAGE_SHARE_INTRIGUE_ARMY_SNEAK_ATTACK_UNKNOWN_CITY, NO_PLAYER, szPlayerName)
		# 						}
		# 						break
		# 					case INTRIGUE_TYPE_AMPHIBIOUS_SNEAK_ATTACK:
		# 						if(pCity)
		# 						{
		# 							szText = GetDiploStringForMessage(DIPLO_MESSAGE_SHARE_INTRIGUE_AMPHIBIOUS_SNEAK_ATTACK_KNOWN_CITY, NO_PLAYER, szPlayerName, pCity->getNameKey())
		# 						}
		# 						else
		# 						{
		# 							szText = GetDiploStringForMessage(DIPLO_MESSAGE_SHARE_INTRIGUE_AMPHIBIOUS_SNEAK_ATTACK_UNKNOWN_CITY, NO_PLAYER, szPlayerName)
		# 						}
		# 						break
		# 					case INTRIGUE_TYPE_DECEPTION:
		# 						szText = GetDiploStringForMessage(DIPLO_MESSAGE_SHARE_INTRIGUE, NO_PLAYER, szPlayerName)
		# 						break
		# 					default:
		# 						CvAssertMsg(false, "Unknown intrigue type")
		# 						break
		# 					}
		#
		# 					DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_BLANK_DISCUSSION, szText, LeaderEmotionType.positive)
		# 				}
		#
		# 			}
		#
		# 			// mark the messages as shared so the player isn't told the same thing repeatedly
		# 			for(uint ui = 0 ui < MAX_MAJOR_CIVS ui++)
		# 			{
		# 				PlayerTypes eLoopPlayer = (PlayerTypes)ui
		# 				GET_PLAYER(eLoopPlayer).GetEspionage()->MarkRecentIntrigueAsShared(otherPlayer, ePlotterPlayer, eIntrigueType)
		# 			}
		# 		}
		# 	}
		#
		# Stop converting our cities
		# 	elif statement == DIPLO_STATEMENT_STOP_CONVERSIONS
		# 		if shouldShowLeaderScene:
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_STOP_CONVERSIONS)
		# 			DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_STOP_CONVERSIONS, szText, LeaderEmotionType.negative)
		# 		}
		# 	}
		#
		# Stop digging up our yard
		# 	elif statement == DIPLO_STATEMENT_STOP_DIGGING
		# 		if shouldShowLeaderScene:
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_STOP_DIGGING)
		# 			DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_STOP_DIGGING, szText, LeaderEmotionType.negative)
		# 		}
		# 	}
		#
		# Insult
		# 	elif statement == DIPLO_STATEMENT_INSULT
		# 		// Change other players' guess as to our Approach (right now it falls in line exactly with the Approach...)
		# 		GET_PLAYER(otherPlayer).GetDiplomacyAI()->SetApproachTowardsUsGuess(self.player, MAJOR_CIV_APPROACH_HOSTILE)
		# 		GET_PLAYER(otherPlayer).GetDiplomacyAI()->SetApproachTowardsUsGuessCounter(self.player, 0)
		#
		# 		if shouldShowLeaderScene:
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_INSULT_ROOT)
		# 			DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_BLANK_DISCUSSION_MEAN_AI, szText, LeaderEmotionType.hateNegative)
		# 		}
		# 	}
		#
		# Compliment
		# 	elif statement == DIPLO_STATEMENT_COMPLIMENT
		# 		// Change other players' guess as to our Approach (right now it falls in line exactly with the Approach...)
		# 		GET_PLAYER(otherPlayer).GetDiplomacyAI()->SetApproachTowardsUsGuess(self.player, MAJOR_CIV_APPROACH_FRIENDLY)
		# 		GET_PLAYER(otherPlayer).GetDiplomacyAI()->SetApproachTowardsUsGuessCounter(self.player, 0)
		#
		# 		if shouldShowLeaderScene:
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_COMPLIMENT)
		# 			DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_BLANK_DISCUSSION, szText, LeaderEmotionType.positive)
		# 		}
		# 	}
		#
		# Boot-kissing of a stronger power
		# 	elif statement == DIPLO_STATEMENT_BOOT_KISSING
		# 		// Change other players' guess as to our Approach (right now it falls in line exactly with the Approach...)
		# 		GET_PLAYER(otherPlayer).GetDiplomacyAI()->SetApproachTowardsUsGuess(self.player, MAJOR_CIV_APPROACH_AFRAID)
		# 		GET_PLAYER(otherPlayer).GetDiplomacyAI()->SetApproachTowardsUsGuessCounter(self.player, 0)
		#
		# 		if shouldShowLeaderScene:
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_BOOT_KISSING)
		# 			DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_BLANK_DISCUSSION, szText, LeaderEmotionType.positive)
		# 		}
		# 	}
		#
		# We're warning a player his warmongering behavior is attracting attention
		# 	elif statement == DIPLO_STATEMENT_WARMONGER
		# 		if shouldShowLeaderScene:
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_WARMONGER)
		# 			DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_BLANK_DISCUSSION_MEAN_HUMAN, szText, LeaderEmotionType.hateNegative)
		# 		}
		# 	}
		#
		# We're warning a player his interactions with city states is not to our liking
		# 	elif statement == DIPLO_STATEMENT_MINOR_CIV_COMPETITION
		# 		if shouldShowLeaderScene:
		# 			PlayerTypes eMinorCiv = (PlayerTypes) iData1
		# 			const char* strMinorCivKey = GET_PLAYER(eMinorCiv).getNameKey()
		#
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_MINOR_CIV_COMPETITION, NO_PLAYER, strMinorCivKey)
		# 			DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_BLANK_DISCUSSION_MEAN_HUMAN, szText, LeaderEmotionType.negative)
		# 		}
		# 	}
		#
		# Human befriended an enemy of this AI!
		# 	elif statement == DIPLO_STATEMENT_ANGRY_BEFRIEND_ENEMY
		# 		if shouldShowLeaderScene:
		# 			PlayerTypes eTarget = (PlayerTypes) iData1
		# 			const char* strTargetCivKey = GET_PLAYER(eTarget).getCivilizationShortDescriptionKey()
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_HUMAN_DOFED_ENEMY, otherPlayer, strTargetCivKey)
		#
		# 			DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_BLANK_DISCUSSION_MEAN_HUMAN, szText, LeaderEmotionType.hateNegative)
		# 		}
		# 	}
		#
		# Human denounced a friend of this AI!
		# 	elif statement == DIPLO_STATEMENT_ANGRY_DENOUNCED_FRIEND
		# 		if shouldShowLeaderScene:
		# 			PlayerTypes eTarget = (PlayerTypes) iData1
		# 			const char* strTargetCivKey = GET_PLAYER(eTarget).getCivilizationShortDescriptionKey()
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_HUMAN_DENOUNCED_FRIEND, otherPlayer, strTargetCivKey)
		#
		# 			DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_BLANK_DISCUSSION_MEAN_HUMAN, szText, LeaderEmotionType.hateNegative)
		# 		}
		# 	}
		#
		# Human denounced an enemy of this AI!
		# 	elif statement == DIPLO_STATEMENT_HAPPY_DENOUNCED_ENEMY
		# 		if shouldShowLeaderScene:
		# 			PlayerTypes eTarget = (PlayerTypes) iData1
		# 			const char* strTargetCivKey = GET_PLAYER(eTarget).getCivilizationShortDescriptionKey()
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_HUMAN_DENOUNCED_ENEMY, otherPlayer, strTargetCivKey)
		#
		# 			DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_BLANK_DISCUSSION, szText, LeaderEmotionType.positive)
		# 		}
		# 	}
		#
		# Human befriended a friend of this AI!
		# 	elif statement == DIPLO_STATEMENT_HAPPY_BEFRIENDED_FRIEND
		# 		if shouldShowLeaderScene:
		# 			PlayerTypes eTarget = (PlayerTypes) iData1
		# 			const char* strTargetCivKey = GET_PLAYER(eTarget).getCivilizationShortDescriptionKey()
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_HUMAN_DOFED_FRIEND, otherPlayer, strTargetCivKey)
		#
		# 			DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_BLANK_DISCUSSION, szText, LeaderEmotionType.positive)
		# 		}
		# 	}
		#
		# 	// AI befriended an enemy of the human!
		# 	elif statement == DIPLO_STATEMENT_FYI_BEFRIEND_HUMAN_ENEMY
		# 		if shouldShowLeaderScene:
		# 			PlayerTypes eTarget = (PlayerTypes) iData1
		# 			const char* strTargetCivKey = GET_PLAYER(eTarget).getCivilizationShortDescriptionKey()
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_HUMAN_DENOUNCE_SO_AI_DOF, otherPlayer, strTargetCivKey)
		#
		# 			DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_BLANK_DISCUSSION_MEAN_AI, szText, LeaderEmotionType.hateNegative)
		# 		}
		# 	}
		#
		# 	// AI denounced a friend of the human!
		# 	elif statement == DIPLO_STATEMENT_FYI_DENOUNCED_HUMAN_FRIEND
		# 		if shouldShowLeaderScene:
		# 			PlayerTypes eTarget = (PlayerTypes) iData1
		# 			const char* strTargetCivKey = GET_PLAYER(eTarget).getCivilizationShortDescriptionKey()
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_HUMAN_DOF_SO_AI_DENOUNCE, otherPlayer, strTargetCivKey)
		#
		# 			DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_BLANK_DISCUSSION_MEAN_AI, szText, LeaderEmotionType.hateNegative)
		# 		}
		# 	}
		#
		# 	// AI denounced an enemy of the human!
		# 	elif statement == DIPLO_STATEMENT_FYI_DENOUNCED_HUMAN_ENEMY
		# 		if shouldShowLeaderScene:
		# 			PlayerTypes eTarget = (PlayerTypes) iData1
		# 			const char* strTargetCivKey = GET_PLAYER(eTarget).getCivilizationShortDescriptionKey()
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_HUMAN_DENOUNCE_SO_AI_DENOUNCE, otherPlayer, strTargetCivKey)
		#
		# 			DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_BLANK_DISCUSSION, szText, LeaderEmotionType.positive)
		# 		}
		# 	}
		#
		# 	// AI befriended a friend of the human!
		# 	elif statement == DIPLO_STATEMENT_FYI_BEFRIEND_HUMAN_FRIEND
		# 		if shouldShowLeaderScene:
		# 			PlayerTypes eTarget = (PlayerTypes) iData1
		# 			const char* strTargetCivKey = GET_PLAYER(eTarget).getCivilizationShortDescriptionKey()
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_HUMAN_DOF_SO_AI_DOF, otherPlayer, strTargetCivKey)
		#
		# 			DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_BLANK_DISCUSSION, szText, LeaderEmotionType.positive)
		# 		}
		# 	}
		#
		# 	// AI chose same late game policy tree!
		# 	elif statement == DIPLO_STATEMENT_SAME_POLICIES_FREEDOM
		# 		if shouldShowLeaderScene:
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_SAME_POLICIES_FREEDOM)
		# 			DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_BLANK_DISCUSSION, szText, LeaderEmotionType.positive)
		# 		}
		# 	}
		#
		# 	elif statement == DIPLO_STATEMENT_SAME_POLICIES_ORDER
		# 		if shouldShowLeaderScene:
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_SAME_POLICIES_ORDER)
		# 			DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_BLANK_DISCUSSION, szText, LeaderEmotionType.positive)
		# 		}
		# 	}
		#
		# 	elif statement == DIPLO_STATEMENT_SAME_POLICIES_AUTOCRACY
		# 		if shouldShowLeaderScene:
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_SAME_POLICIES_AUTOCRACY)
		# 			DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_BLANK_DISCUSSION, szText, LeaderEmotionType.positive)
		# 		}
		# 	}
		#
		# 	elif statement == DIPLO_STATEMENT_WE_LIKED_THEIR_PROPOSAL
		# 		if shouldShowLeaderScene:
		# 			Localization::String sLeagueName = Localization::Lookup("TXT_KEY_LEAGUE_WORLD_CONGRESS_GENERIC")
		# 			CvLeague* pLeague = GC.getGame().GetGameLeagues()->GetActiveLeague()
		# 			if (pLeague != NULL)
		# 			{
		# 				sLeagueName = pLeague->GetName()
		# 			}
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_WE_LIKED_THEIR_PROPOSAL, otherPlayer, sLeagueName)
		# 			DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_BLANK_DISCUSSION, szText, LeaderEmotionType.positive)
		# 		}
		# 	}
		#
		# 	elif statement == DIPLO_STATEMENT_WE_DISLIKED_THEIR_PROPOSAL
		# 		if shouldShowLeaderScene:
		# 			Localization::String sLeagueName = Localization::Lookup("TXT_KEY_LEAGUE_WORLD_CONGRESS_GENERIC")
		# 			CvLeague* pLeague = GC.getGame().GetGameLeagues()->GetActiveLeague()
		# 			if (pLeague != NULL)
		# 			{
		# 				sLeagueName = pLeague->GetName()
		# 			}
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_WE_DISLIKED_THEIR_PROPOSAL, otherPlayer, sLeagueName)
		# 			DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_BLANK_DISCUSSION, szText, LeaderEmotionType.negative)
		# 		}
		# 	}
		#
		# 	elif statement == DIPLO_STATEMENT_THEY_SUPPORTED_OUR_PROPOSAL
		# 		if shouldShowLeaderScene:
		# 			Localization::String sLeagueName = Localization::Lookup("TXT_KEY_LEAGUE_WORLD_CONGRESS_GENERIC")
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_THEY_SUPPORTED_OUR_PROPOSAL, otherPlayer, sLeagueName)
		# 			DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_BLANK_DISCUSSION, szText, LeaderEmotionType.positive)
		# 		}
		# 	}
		#
		# 	elif statement == DIPLO_STATEMENT_THEY_FOILED_OUR_PROPOSAL
		# 		if shouldShowLeaderScene:
		# 			Localization::String sLeagueName = Localization::Lookup("TXT_KEY_LEAGUE_WORLD_CONGRESS_GENERIC")
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_THEY_FOILED_OUR_PROPOSAL, otherPlayer, sLeagueName)
		# 			DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_BLANK_DISCUSSION, szText, LeaderEmotionType.negative)
		# 		}
		# 	}
		#
		# 	elif statement == DIPLO_STATEMENT_THEY_SUPPORTED_OUR_HOSTING
		# 		if shouldShowLeaderScene:
		# 			Localization::String sLeagueName = Localization::Lookup("TXT_KEY_LEAGUE_WORLD_CONGRESS_GENERIC")
		# 			CvLeague* pLeague = GC.getGame().GetGameLeagues()->GetActiveLeague()
		# 			if (pLeague != NULL)
		# 			{
		# 				sLeagueName = pLeague->GetName()
		# 			}
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_THEY_SUPPORTED_OUR_HOSTING, otherPlayer, sLeagueName)
		# 			DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_BLANK_DISCUSSION, szText, LeaderEmotionType.positive)
		# 		}
		# 	}
		#
		# 	// Ideological statements
		# 	elif statement == DIPLO_STATEMENT_YOUR_IDEOLOGY_CAUSING_CIVIL_UNREST_FREEDOM
		# 		if shouldShowLeaderScene:
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_YOUR_IDEOLOGY_CAUSING_CIVIL_UNREST_FREEDOM)
		# 			DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_BLANK_DISCUSSION, szText, LeaderEmotionType.negative)
		# 		}
		# 	}
		# 	elif statement == DIPLO_STATEMENT_YOUR_IDEOLOGY_CAUSING_CIVIL_UNREST_ORDER
		# 		if shouldShowLeaderScene:
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_YOUR_IDEOLOGY_CAUSING_CIVIL_UNREST_ORDER)
		# 			DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_BLANK_DISCUSSION, szText, LeaderEmotionType.negative)
		# 		}
		# 	}
		# 	elif statement == DIPLO_STATEMENT_YOUR_IDEOLOGY_CAUSING_CIVIL_UNREST_AUTOCRACY
		# 		if shouldShowLeaderScene:
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_YOUR_IDEOLOGY_CAUSING_CIVIL_UNREST_AUTOCRACY)
		# 			DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_BLANK_DISCUSSION, szText, LeaderEmotionType.negative)
		# 		}
		# 	}
		# 	elif statement == DIPLO_STATEMENT_OUR_IDEOLOGY_CAUSING_CIVIL_UNREST_FREEDOM
		# 		if shouldShowLeaderScene:
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_OUR_IDEOLOGY_CAUSING_CIVIL_UNREST_FREEDOM)
		# 			DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_BLANK_DISCUSSION, szText, LeaderEmotionType.positive)
		# 		}
		# 	}
		# 	elif statement == DIPLO_STATEMENT_OUR_IDEOLOGY_CAUSING_CIVIL_UNREST_ORDER
		# 		if shouldShowLeaderScene:
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_OUR_IDEOLOGY_CAUSING_CIVIL_UNREST_ORDER)
		# 			DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_BLANK_DISCUSSION, szText, LeaderEmotionType.positive)
		# 		}
		# 	}
		# 	elif statement == DIPLO_STATEMENT_OUR_IDEOLOGY_CAUSING_CIVIL_UNREST_AUTOCRACY
		# 		if shouldShowLeaderScene:
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_OUR_IDEOLOGY_CAUSING_CIVIL_UNREST_AUTOCRACY)
		# 			DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_BLANK_DISCUSSION, szText, LeaderEmotionType.positive)
		# 		}
		# 	}
		# 	elif statement == DIPLO_STATEMENT_SWITCH_OUR_IDEOLOGY_FREEDOM
		# 		if shouldShowLeaderScene:
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_SWITCH_OUR_IDEOLOGY_FREEDOM)
		# 			DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_BLANK_DISCUSSION, szText, LeaderEmotionType.positive)
		# 		}
		# 	}
		# 	elif statement == DIPLO_STATEMENT_SWITCH_OUR_IDEOLOGY_ORDER
		# 		if shouldShowLeaderScene:
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_SWITCH_OUR_IDEOLOGY_ORDER)
		# 			DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_BLANK_DISCUSSION, szText, LeaderEmotionType.positive)
		# 		}
		# 	}
		# 	elif statement == DIPLO_STATEMENT_SWITCH_OUR_IDEOLOGY_AUTOCRACY
		# 		if shouldShowLeaderScene:
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_SWITCH_OUR_IDEOLOGY_AUTOCRACY)
		# 			DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_BLANK_DISCUSSION, szText, LeaderEmotionType.positive)
		# 		}
		# 	}
		# 	elif statement == DIPLO_STATEMENT_YOUR_CULTURE_INFLUENTIAL
		# 		if shouldShowLeaderScene:
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_YOUR_CULTURE_INFLUENTIAL)
		# 			DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_BLANK_DISCUSSION, szText, LeaderEmotionType.negative)
		# 		}
		# 	}
		# 	elif statement == DIPLO_STATEMENT_OUR_CULTURE_INFLUENTIAL
		# 		if shouldShowLeaderScene:
		# 			szText = GetDiploStringForMessage(DIPLO_MESSAGE_OUR_CULTURE_INFLUENTIAL)
		# 			DiplomacyRequests.sendRequest(self.player, otherPlayer, DIPLO_UI_STATE_BLANK_DISCUSSION, szText, LeaderEmotionType.positive)
		# 		}
		# 	}
		#
		# Do we want peace with otherPlayer?
		elif statement == DiplomaticStatementType.requestPeace:  # DIPLO_STATEMENT_REQUEST_PEACE
			if shouldShowLeaderScene:  # Active human
				szText = DiplomaticRequestMessage.peaceOffer.text()  # DIPLO_MESSAGE_PEACE_OFFER
				DiplomacyRequests.sendDealRequest(self.player, otherPlayer, deal, DiplomaticRequestState.tradeAIMakesOffer, szText, LeaderEmotionType.positive)
			elif not human:  # Offer to an AI player
				# Don't need to call DoOffer because we check to see if the deal works for both sides BEFORE sending
				simulation.gameDeals.addProposedDeal(deal, simulation)
				simulation.gameDeals.finalizeDeal(self, otherPlayer, True, simulation)
				self.logPeaceMadeWith(otherPlayer, simulation)
		else:
			raise Exception(f'{statement} not handled')
			
		return

	def doCounters(self, simulation):
		"""Increment our turn counters"""
		# Loop through AI Players
		for otherPlayer in simulation.players:
			if otherPlayer.isBarbarian():
				continue

			if self.player == otherPlayer:
				continue

			if not otherPlayer.isAlive():
				continue

			if not self.player.hasMetWith(otherPlayer):
				continue

			# War Counter
			# no need to update the counters - the start of the war is logged

			# // // // // // // // // // // // // // // /
			# Major Civs only!
			# // // // // // // // // // // // // // // /

			# Trade value counter
			self.changeRecentTradeValueWith(otherPlayer, -3)  # DEAL_VALUE_PER_TURN_DECAY

			# ChangeCommonFoeValue(eLoopPlayer, -25)  # COMMON_FOE_VALUE_PER_TURN_DECAY

			# if (GetRecentAssistValue(eLoopPlayer) > 0):
			# 	iMin = min(GetRecentAssistValue(eLoopPlayer), 3)  # DEAL_VALUE_PER_TURN_DECAY
			# 	ChangeRecentAssistValue(eLoopPlayer, -iMin)
			# elif (GetRecentAssistValue(eLoopPlayer) < 0):
			# 	iMin = min(-GetRecentAssistValue(eLoopPlayer), 3)  # DEAL_VALUE_PER_TURN_DECAY
			# 	ChangeRecentAssistValue(eLoopPlayer, iMin)
			#
			# iBrokenPromisePreValue = GetBrokenExpansionPromiseValue(eLoopPlayer)
			# ChangeBrokenExpansionPromiseValue(eLoopPlayer, -3)  # DEAL_VALUE_PER_TURN_DECAY
			# iIgnoredPromisePreValue = GetIgnoredExpansionPromiseValue(eLoopPlayer)
			# ChangeIgnoredExpansionPromiseValue(eLoopPlayer, -GC.getEXPANSION_PROMISE_IGNORED_PER_TURN_DECAY())
			#
			# --if the promise penalty of breaking a promise has expired, reset the ability to ask the promise again
			# if ((iBrokenPromisePreValue != 0 and GetBrokenExpansionPromiseValue(eLoopPlayer) == 0 and GetIgnoredExpansionPromiseValue(eLoopPlayer) == 0) or
			# (iIgnoredPromisePreValue != 0 and GetIgnoredExpansionPromiseValue(eLoopPlayer) == 0 and GetBrokenExpansionPromiseValue(
			# 	eLoopPlayer) == 0)):
			# 	SetPlayerMadeExpansionPromise(eLoopPlayer, False)
			# 	SetPlayerBrokenExpansionPromise(eLoopPlayer, False)
			# 	SetPlayerIgnoredExpansionPromise(eLoopPlayer, False)
			#
			# iBrokenPromisePreValue = GetBrokenBorderPromiseValue(eLoopPlayer)
			# ChangeBrokenBorderPromiseValue(eLoopPlayer, -GC.getBORDER_PROMISE_BROKEN_PER_TURN_DECAY())
			# iIgnoredPromisePreValue = GetIgnoredBorderPromiseValue(eLoopPlayer)
			# ChangeIgnoredBorderPromiseValue(eLoopPlayer, -GC.getBORDER_PROMISE_IGNORED_PER_TURN_DECAY())
			#
			# --if the promise penalty of breaking a promise has expired, reset the ability to ask the promise again
			# if ((iBrokenPromisePreValue != 0 and GetBrokenBorderPromiseValue(eLoopPlayer) == 0 and GetIgnoredBorderPromiseValue(eLoopPlayer) == 0) or
			# (iIgnoredPromisePreValue != 0 and GetIgnoredBorderPromiseValue(eLoopPlayer) == 0 and GetBrokenBorderPromiseValue(
			# 	eLoopPlayer) == 0)):
			# 	SetPlayerMadeBorderPromise(eLoopPlayer, False)
			# 	SetPlayerBrokenBorderPromise(eLoopPlayer, False)
			# 	SetPlayerIgnoredBorderPromise(eLoopPlayer, False)
			#
			# ChangeDeclaredWarOnFriendValue(eLoopPlayer, -80)  # DECLARED_WAR_ON_FRIEND_PER_TURN_DECAY
			#
			# --Diplo Statement Log Counter
			# for (iItem = 0 iItem < MAX_DIPLO_LOG_STATEMENTS iItem++)
			# 	eStatement = GetDiploLogStatementTypeForIndex(eLoopPlayer, iItem)
			#
			# 	if (eStatement != NO_DIPLO_STATEMENT_TYPE)
			# 		ChangeDiploLogStatementTurnForIndex(eLoopPlayer, iItem, 1)
			# 	else
			# 		SetDiploLogStatementTurnForIndex(eLoopPlayer, iItem, 0)
			#
			# --Attacked Protected Minor Counter
			# if (GetOtherPlayerProtectedMinorAttacked(eLoopPlayer) != NO_PLAYER):
			# 	ChangeOtherPlayerTurnsSinceAttackedProtectedMinor(eLoopPlayer, 1)
			#
			# --Killed Protected Minor Counter
			# if (GetOtherPlayerProtectedMinorKilled(eLoopPlayer) != NO_PLAYER):
			# 	ChangeOtherPlayerTurnsSinceKilledProtectedMinor(eLoopPlayer, 1)
			#
			# --They sided with their Protected Minor Counter
			# if (IsOtherPlayerSidedWithProtectedMinor(eLoopPlayer)):
			# 	ChangeOtherPlayerTurnsSinceSidedWithProtectedMinor(eLoopPlayer, 1)
			#
			# --Did this player ask us not to settle near them?
			# if (GetPlayerNoSettleRequestCounter(eLoopPlayer) > -1):
			# 	ChangePlayerNoSettleRequestCounter(eLoopPlayer, 1)
			#
			# 	if (GetPlayerNoSettleRequestCounter(eLoopPlayer) >= 50:  # IC_MEMORY_TURN_EXPIRATION
			# 		SetPlayerNoSettleRequestAccepted(eLoopPlayer, False)
			# 		SetPlayerNoSettleRequestCounter(eLoopPlayer, -666)
			#
			# --Did this player ask us to stop spying on them?
			# if (GetPlayerStopSpyingRequestCounter(eLoopPlayer) > -1):
			# 	ChangePlayerStopSpyingRequestCounter(eLoopPlayer, 1)
			#
			# 	if (GetPlayerStopSpyingRequestCounter(eLoopPlayer) >= 50:  # STOP_SPYING_MEMORY_TURN_EXPIRATION
			# 		SetPlayerStopSpyingRequestAccepted(eLoopPlayer, False)
			# 		SetPlayerStopSpyingRequestCounter(eLoopPlayer, -666)
			#
			# --World Congress mood counters
			# if (GetTurnsSinceWeLikedTheirProposal(eLoopPlayer) > -1):
			# 	ChangeTurnsSinceWeLikedTheirProposal(eLoopPlayer, 1)
			#
			# if (GetTurnsSinceWeDislikedTheirProposal(eLoopPlayer) > -1):
			# 	ChangeTurnsSinceWeDislikedTheirProposal(eLoopPlayer, 1)
			#
			# if (GetTurnsSinceTheySupportedOurProposal(eLoopPlayer) > -1):
			# 	ChangeTurnsSinceTheySupportedOurProposal(eLoopPlayer, 1)
			#
			# if (GetTurnsSinceTheyFoiledOurProposal(eLoopPlayer) > -1):
			# 	ChangeTurnsSinceTheyFoiledOurProposal(eLoopPlayer, 1)
			#
			# if (GetTurnsSinceTheySupportedOurHosting(eLoopPlayer) > -1):
			# 	ChangeTurnsSinceTheySupportedOurHosting(eLoopPlayer, 1)
			#
			# --Did this player make a demand of us?
			# if (GetDemandCounter(eLoopPlayer) > -1):
			# 	ChangeDemandCounter(eLoopPlayer, 1)
			#
			# --DoF?
			# if (GetDoFCounter(eLoopPlayer) > -1):
			# 	ChangeDoFCounter(eLoopPlayer, 1)
			#
			# --Denounced?
			# if (GetDenouncedPlayerCounter(eLoopPlayer) > -1):
			# 	ChangeDenouncedPlayerCounter(eLoopPlayer, 1)
			#
			# --Are we ready to forget our denunciation?
			# if (IsDenouncedPlayer(eLoopPlayer) and GetDenouncedPlayerCounter(eLoopPlayer) >= 50:  # RelationshipDuration of gamespeed standard
			# 	SetDenouncedPlayer(eLoopPlayer, False)
			# 	SetDenouncedPlayerCounter(eLoopPlayer, -1)
			# 	# Let's become open to becoming friends again
			# 	SetDoFCounter(eLoopPlayer, -1)
			#
			# 	# They no longer hate us either
			# 	GET_PLAYER(eLoopPlayer).GetDiplomacyAI()->SetDoFCounter(self.player, -1)
			# 	GET_PLAYER(eLoopPlayer).GetDiplomacyAI()->SetFriendDenouncedUs(self.player, False)
			#
			# 	for (iThirdPlayerLoop = 0 iThirdPlayerLoop < MAX_MAJOR_CIVS iThirdPlayerLoop++):
			# 		eThirdPlayer = (PlayerTypes) iThirdPlayerLoop
			#
			# 		# We may even do co-op wars in the future
			# 		if (GetCoopWarCounter(eLoopPlayer, eThirdPlayer) < -1):
			# 			SetCoopWarCounter(eLoopPlayer, eThirdPlayer, -1)
			# 			GET_PLAYER(eLoopPlayer).GetDiplomacyAI()->SetCoopWarCounter(self.player, eThirdPlayer, -1)
			#
			# 	# Notify the target of the denouncement that it has expired.
			# 	CvNotifications * pNotifications = GET_PLAYER(eLoopPlayer).GetNotifications()
			# 	if (pNotifications){
			# 	CvString                            strSummary = GetLocalizedText("TXT_KEY_NOTIFICATION_THEIR_DENUNCIATION_EXPIRED_S")
			# 	Localization::
			# 		String
			# 	strInfo = Localization::Lookup("TXT_KEY_NOTIFICATION_THEIR_DENUNCIATION_EXPIRED")
			# 	Localization::String
			# 	strTemp = strInfo
			# 	strTemp << GET_PLAYER(self.player).getCivilizationShortDescriptionKey()
			# 	pNotifications->Add(NOTIFICATION_DENUNCIATION_EXPIRED, strTemp.toUTF8(), strSummary, -1, -1,
			# 	                    self.player, eLoopPlayer)
			#
			# -- Has our Friendship expired?
			# if (IsDoFAccepted(eLoopPlayer) and GetDoFCounter(eLoopPlayer) >= GC.getGame().getGameSpeedInfo().getRelationshipDuration())
			# 	SetDoFCounter(eLoopPlayer, -1)
			# 	SetDoFAccepted(eLoopPlayer, False)
			#
			# 	GET_PLAYER(eLoopPlayer).GetDiplomacyAI()->SetDoFCounter(self.player, -1)
			# 	GET_PLAYER(eLoopPlayer).GetDiplomacyAI()->SetDoFAccepted(self.player, False)
			#
			# 	# Notify both parties that our friendship has expired.
			# 	CvNotifications * pNotifications = GET_PLAYER(eLoopPlayer).GetNotifications()
			# 	if (pNotifications):
			# 	CvString strBuffer = GetLocalizedText("TXT_KEY_NOTIFICATION_FRIENDSHIP_EXPIRED", GET_PLAYER(self.player).getCivilizationShortDescriptionKey())
			# 	CvString strSummary = GetLocalizedText("TXT_KEY_NOTIFICATION_FRIENDSHIP_EXPIRED_S")
			# 	pNotifications->Add(NOTIFICATION_FRIENDSHIP_EXPIRED, strBuffer, strSummary, -1, -1, self.player, eLoopPlayer)
			#
			#
			# 	pNotifications = GET_PLAYER(self.player).GetNotifications()
			# 	if (pNotifications):
			# 	CvString strBuffer = GetLocalizedText("TXT_KEY_NOTIFICATION_FRIENDSHIP_EXPIRED", GET_PLAYER(eLoopPlayer).getCivilizationShortDescriptionKey())
			# 	CvString strSummary = GetLocalizedText("TXT_KEY_NOTIFICATION_FRIENDSHIP_EXPIRED_S")
			# 	pNotifications->Add(NOTIFICATION_FRIENDSHIP_EXPIRED, strBuffer, strSummary, -1, -1, eLoopPlayer, self.player)

		# // // // // // // // // // // // // // // // /
		# Declaration Log Counter
		# // // // // // // // // // // // // // // // /

		# for (iItem = 0 iItem < MAX_DIPLO_LOG_STATEMENTS iItem++)
		# 	eDeclaration = GetDeclarationLogTypeForIndex(iItem)
		#
		# 	if (eDeclaration != NO_PUBLIC_DECLARATION_TYPE):
		# 		ChangeDeclarationLogTurnForIndex(iItem, 1)
		# 	else:
		# 		SetDeclarationLogTurnForIndex(iItem, 0)

	def isAtWarWith(self, otherPlayer) -> bool:
		# player is not at war with his self
		if self.player == otherPlayer:
			return False

		if self.player.isBarbarian():
			return True

		if otherPlayer.isBarbarian():
			return True

		return self.playerDict.isAtWarWith(otherPlayer)

	def isAtWar(self):
		return self.playerDict.isAtWar()

	def atWarCount(self) -> int:
		return self.playerDict.atWarCount()

	def canDeclareWarTowards(self, otherPlayer) -> bool:
		if self.player == otherPlayer:
			return False

		if not self.player.isAlive():
			return False

		if self.isAtWarWith(otherPlayer):
			return False

		if not self.hasMetWith(otherPlayer):
			return False

		if self.isForcePeaceWith(otherPlayer):
			return False

		if not self.canChangeWarPeaceWith(otherPlayer):
			return False

		# if (GC.getGame().isOption(GAMEOPTION_ALWAYS_PEACE)):
		# 	return False

		return True

	def doDeclareWarTo(self, otherPlayer, simulation):
		"""We've decided to declare war on someone"""
		# Only do it if we are not already at war.
		if self.isAtWarWith(otherPlayer):
			return

		if not self.hasMetWith(otherPlayer):
			self.doFirstContactWith(otherPlayer, simulation)

		# Since we declared war, all of OUR Defensive Pacts are nullified
		self.doCancelDefensivePacts()

		# and we also remove our delegation
		if self.hasSentDelegationTo(otherPlayer):
			self.doRevokeDelegation(otherPlayer, simulation)

		# Cancel Trade Deals
		self.doCancelDealsWith(otherPlayer)
		# fixme
		# GC.getGame().GetGameTrade()->DoAutoWarPlundering(m_eID, eTeam)
		# GC.getGame().GetGameTrade()->CancelTradeBetweenTeams(m_eID, eTeam)

		# Auto War for Defensive Pacts
		otherPlayer.diplomacyAI.activateDefensivePactsAgainst(self, simulation)

		# Cancel Trade Deals, RAs, diplomats
		simulation.gameDeals.doCancelDealsBetween(self.player, otherPlayer, simulation)
		self.closeEmbassyAt(otherPlayer)
		otherPlayer.diplomacyAI.closeEmbassyAt(self.player)
		self.cancelResearchAgreementWith(otherPlayer)
		otherPlayer.diplomacyAI.cancelResearchAgreementWith(self.player)
		# EvacuateDiplomatsAtTeam(eTeam)
		# GET_TEAM(eTeam).EvacuateDiplomatsAtTeam(m_eID)

		# Update the ATTACKED players' Diplomatic AI
		otherPlayer.diplomacyAI.doHaveBeenDeclaredWarBy(self.player, simulation)

		self.player.citySpecializationAI.setSpecializationsDirty()  # SPECIALIZATION_UPDATE_NOW_AT_WAR

		# If we've made a peace treaty before, this is bad news
		if self.isPeaceTreatyActiveWith(otherPlayer):
			self.updateHasBrokenPeaceTreatyTo(True)
		# FIXME: => update counter of everyone who knows us

		# Update what every Major Civ sees
		# FIXME: let everyone know, we have attacked

		self.playerDict.declaredWarTowards(otherPlayer, simulation.currentTurn)

		# inform player that some declared war
		if otherPlayer.isHuman():
			self.player.notifications.addNotification(NotificationType.war, leader=otherPlayer.leader)

		# inform other players, that a war was declared
		simulation.sendGossip(GossipType.declarationsOfWar, leader=otherPlayer.leader, player=otherPlayer)

	def doCancelDefensivePacts(self):
		self.playerDict.cancelAllDefensivePacts()

	def doCancelDealsWith(self, otherPlayer):
		self.playerDict.cancelDealsWith(otherPlayer)
		otherPlayer.diplomacyAI.playerDict.cancelDealsWith(self.player)

	def isPeaceTreatyActiveWith(self, otherPlayer):
		return self.playerDict.isPeaceTreatyActiveWith(otherPlayer)

	def updateHasBrokenPeaceTreatyTo(self, value: bool):
		self._hasBrokenPeaceTreatyValue = value

	def proximityTo(self, otherPlayer) -> PlayerProximityType:
		return self.playerDict.proximityTo(otherPlayer)

	def doHaveBeenDeclaredWarBy(self, otherPlayer, simulation):
		# Auto War for Defensive Pacts of other player
		self.activateDefensivePactsAgainst(otherPlayer, simulation)

		if otherPlayer.isCityState():
			self.playerDict.updateMinorCivApproachTowards(otherPlayer, MinorPlayerApproachType.bully)
			self.playerDict.updateWarStateTowards(otherPlayer, PlayerWarStateType.defensive)
		else:
			self.playerDict.updateMajorApproachValueTowards(otherPlayer, MajorPlayerApproachType.war.level())
			self.playerDict.updateWarStateTowards(otherPlayer, PlayerWarStateType.defensive)

	def activateDefensivePactsAgainst(self, otherPlayer, simulation):
		for friendLeader in self.allPlayersWithDefensivePacts():
			friendPlayer = simulation.playerFor(friendLeader)
			friendPlayer.diplomacyAI.doDeclareWarFromDefensivePactTo(otherPlayer, simulation)

		return

	def signDefensivePactWith(self, otherPlayer, turn: int):
		self.playerDict.signDefensivePactWith(otherPlayer, turn)
		return

	def cancelDefensivePactWith(self, otherPlayer):
		self.playerDict.cancelDefensivePactWith(otherPlayer)
		return

	def allPlayersWithDefensivePacts(self) -> [LeaderType]:
		return self.playerDict.allPlayersWithDefensivePacts()

	def addGossipItem(self, gossipItem: GossipItem, otherPlayer):
		self.playerDict.addGossipItem(gossipItem, otherPlayer)

	def isOpenBordersExchangeAcceptableWith(self, otherPlayer) -> bool:
		"""Are we willing to swap Open Borders with otherPlayer?"""
		approach: MajorPlayerApproachType = self.majorCivApproachTowards(otherPlayer, hideTrueFeelings=True)

		if approach == MajorPlayerApproachType.friendly:
			return True
		elif approach == MajorPlayerApproachType.afraid:
			return True

		return False

	def isOpenBordersAgreementActiveWith(self, otherPlayer) -> bool:
		return self.playerDict.isOpenBordersAgreementActiveWith(otherPlayer)

	def changeOtherPlayerWarValueLostBy(self, fromPlayer, toPlayer, delta: int):
		value = self.playerDict.otherPlayerWarValueLostFrom(fromPlayer, toPlayer)
		self.playerDict.updateOtherPlayerWarValueLostFrom(fromPlayer, toPlayer, value + delta)

	def otherPlayerWarValueLostBy(self, fromPlayer, toPlayer) -> int:
		return self.playerDict.otherPlayerWarValueLostFrom(fromPlayer, toPlayer)

	def changeWarValueLostBy(self, otherPlayer, delta: int):
		if self.player == otherPlayer:
			return

		value = self.playerDict.warValueLostWith(otherPlayer)
		self.playerDict.updateWarValueLostWith(otherPlayer, value + delta)

	def changeWarWearinessWith(self, otherPlayer, value):
		self.playerDict.changeWarWearinessWith(otherPlayer, value)

	def numberOfTurnsLockedIntoWarWith(self, otherPlayer) -> int:
		return self.playerDict.numberOfTurnsLockedIntoWarWith(otherPlayer)

	def changeNumberOfTurnsLockedIntoWarWith(self, otherPlayer, delta: int):
		value = self.playerDict.numberOfTurnsLockedIntoWarWith(otherPlayer)
		self.playerDict.updateNumberOfTurnsLockedIntoWarWith(otherPlayer, value + delta)

	def warStateTowards(self, otherPlayer) -> PlayerWarStateType:
		return self.playerDict.warStateTowards(otherPlayer)

	def warGoalTowards(self, otherPlayer) -> WarGoalType:
		return self.playerDict.warGoalTowards(otherPlayer)

	def isWarGoalDamageTowards(self, otherPlayer) -> bool:
		return self.warGoalTowards(otherPlayer) < WarGoalType.damage

	def militaryStrengthOf(self, otherPlayer) -> StrengthType:
		return self.playerDict.militaryStrengthComparedToUsOf(otherPlayer)

	def targetValueOf(self, otherPlayer) -> PlayerTargetValueType:
		return self.playerDict.targetValueOf(otherPlayer)

	def totalLandDisputeLevel(self, simulation) -> int:
		"""Returns an integer that increases as the number and severity of land disputes rises"""
		rtnValue = 0  # slewis added, to fix a compile error. I'm guessing zero is correct.

		for otherPlayer in simulation.players:
			if not otherPlayer.isAlive():
				continue
			
			if otherPlayer == self.player:
				continue
				
			if not self.hasMetWith(otherPlayer):
				continue

			landDisputeLevelValue = self.landDisputeLevelWith(otherPlayer)

			if landDisputeLevelValue == DisputeLevelType.fierce:
				rtnValue += 5  # AI_DIPLO_LAND_DISPUTE_WEIGHT_FIERCE
			elif landDisputeLevelValue == DisputeLevelType.strong:
				rtnValue += 3  # AI_DIPLO_LAND_DISPUTE_WEIGHT_STRONG
			elif landDisputeLevelValue == DisputeLevelType.weak:
				rtnValue += 1  # AI_DIPLO_LAND_DISPUTE_WEIGHT_WEAK

		return rtnValue

	def landDisputeLevelWith(self, otherPlayer) -> DisputeLevelType:
		return self.playerDict.landDisputeLevelWith(otherPlayer)

	def lastTurnLandDisputeLevelWith(self, otherPlayer) -> DisputeLevelType:
		return self.playerDict.lastTurnLandDisputeLevelWith(otherPlayer)

	def warValueLostWith(self, otherPlayer) -> int:
		return self.playerDict.warValueLostWith(otherPlayer)

	def changeWarValueLostWith(self, otherPlayer, value: int):
		return self.playerDict.updateWarValueLostWith(otherPlayer, value)

	def expansionAggressivePostureTowards(self, otherPlayer) -> AggressivePostureType:
		return self.playerDict.expansionAggressivePostureTowards(otherPlayer)

	def plotBuyingAggressivePostureTowards(self, otherPlayer) -> AggressivePostureType:
		return self.playerDict.plotBuyingAggressivePostureTowards(otherPlayer)

	def updateWarDamageLevelWith(self, otherPlayer, warDamageLevel: WarDamageLevelType):
		self.playerDict.updateWarDamageLevelWith(otherPlayer, warDamageLevel)

	def updateEconomicStrengthOf(self, otherPlayer, simulation):
		ownEconomicStrength = self.player.economicMight(simulation)
		otherEconomicStrength = otherPlayer.economicMight(simulation)
		economicRatio = otherEconomicStrength * 100 / ownEconomicStrength

		if ownEconomicStrength < 0:
			economicRatio = 500

		# Now do the final assessment
		if economicRatio >= 250:
			self.playerDict.updateEconomicStrengthComparedToUs(otherPlayer, StrengthType.immense)
		elif economicRatio >= 153:
			self.playerDict.updateEconomicStrengthComparedToUs(otherPlayer, StrengthType.powerful)
		elif economicRatio >= 120:
			self.playerDict.updateEconomicStrengthComparedToUs(otherPlayer, StrengthType.strong)
		elif economicRatio >= 83:
			self.playerDict.updateEconomicStrengthComparedToUs(otherPlayer, StrengthType.average)
		elif economicRatio >= 65:
			self.playerDict.updateEconomicStrengthComparedToUs(otherPlayer, StrengthType.poor)
		elif economicRatio >= 40:
			self.playerDict.updateEconomicStrengthComparedToUs(otherPlayer, StrengthType.weak)
		else:
			self.playerDict.updateEconomicStrengthComparedToUs(otherPlayer, StrengthType.pathetic)

		return

	def numMajorCivOpinion(self, opinion: MajorCivOpinionType, simulation) -> int:
		"""How many Majors do we have a particular Opinion towards?"""
		count = 0

		for loopPlayer in simulation.players:
			if not loopPlayer.isMajorAI() and not loopPlayer.isHuman():
				continue
				
			if not self.isValid(loopPlayer):
				continue
				
			if self.majorCivOpinion(loopPlayer) == opinion:
				count += 1

		return count

	def majorCivOpinion(self, otherPlayer) -> MajorCivOpinionType:
		"""What is our Diplomatic Opinion of this Major Civ?"""
		return self.playerDict.majorCivOpinionOf(otherPlayer)

	def majorCivApproachTowards(self, otherPlayer, hideTrueFeelings: bool=True) -> MajorPlayerApproachType:
		"""What is our Diplomatic approach to this Major Civ?"""
		approach: MajorPlayerApproachType = self.playerDict.majorApproachTowards(otherPlayer)

		# If we're hiding our true feelings then use the War Face or Friendly if we're Deceptive
		if hideTrueFeelings:
			# Deceptive => Friendly
			if approach == MajorPlayerApproachType.deceptive:
				approach = MajorPlayerApproachType.friendly

			# check War Face
			elif approach == MajorPlayerApproachType.war:
				warFace: PlayerWarFaceType = self.warFaceWith(otherPlayer)
				if warFace == PlayerWarFaceType.hostile:
					approach = MajorPlayerApproachType.hostile
				elif warFace == PlayerWarFaceType.friendly:
					approach = MajorPlayerApproachType.friendly
				elif warFace == PlayerWarFaceType.neutral:
					approach = MajorPlayerApproachType.neutral

		return approach

	def warFaceWith(self, otherPlayer) -> PlayerWarFaceType:
		return self.playerDict.warFaceWith(otherPlayer)

	def updateMajorCivApproachTowards(self, otherPlayer, approach: MajorPlayerApproachType):
		self.playerDict.updateMajorCivApproachTowards(otherPlayer, approach)

	def bestApproachTowardsMajorCiv(self, otherPlayer, lookAtOtherPlayers: bool, log: bool, simulation) -> (int, MajorPlayerApproachType, PlayerWarFaceType):
		"""What is the best approach to take towards a player?  Can also pass in iHighestWeight by reference
		if you just want to know what the player feels most strongly about without actually caring about WHAT it is"""
		viApproachWeights = WeightedBaseList()

		# init the weights
		for loopApproach in MajorPlayerApproachType.all():
			viApproachWeights.setWeight(0, loopApproach)

		# // // // // // // // // // // // // // // // // // //
		# NEUTRAL DEFAULT WEIGHT
		# // // // // // // // // // // // // // // // // // //

		viApproachWeights.addWeight(4, MajorPlayerApproachType.neutral)  # APPROACH_NEUTRAL_DEFAULT

		# // // // // // // // // // // // // // // // // // //
		# CURRENT APPROACH BIASES
		# // // // // // // // // // // // // // // // // // //

		# Bias for our current Approach.This should prevent it from jumping around from turn-to-turn as much
		# We use the scratch pad here since the normal array has been cleared so that we have knowledge of who
		# we've already assigned an Approach for this turn this should be the only place the scratch pad is used
		oldApproach: MajorPlayerApproachType = self._paeApproachScratchPad.weight(hash(otherPlayer))
		if oldApproach == MajorPlayerApproachType.none:
			oldApproach = MajorPlayerApproachType.neutral

		viApproachWeights.addWeight(5, oldApproach)  # APPROACH_BIAS_FOR_CURRENT

		# If our previous Approach was deceptive, this gives us a bonus for war
		if oldApproach == MajorPlayerApproachType.deceptive:
			viApproachWeights.addWeight(2, MajorPlayerApproachType.war)  # APPROACH_WAR_CURRENTLY_DECEPTIVE

		# If our previous Approach was Hostile, boost the strength (so we're unlikely to switch out of it)
		if oldApproach == MajorPlayerApproachType.hostile:
			viApproachWeights.addWeight(5, MajorPlayerApproachType.hostile)  # APPROACH_HOSTILE_CURRENTLY_HOSTILE

		# Wanted war last turn bias: war must be calm or better to apply
		warState: PlayerWarStateType = self.warStateTowards(otherPlayer)
		if warState > PlayerWarStateType.stalemate:
			# If we're planning a war then give it a bias so that we don't get away from it too easily
			if oldApproach == MajorPlayerApproachType.war:
				viApproachWeights.addWeight(3, MajorPlayerApproachType.war)  # APPROACH_WAR_CURRENTLY_WAR

		# Conquest bias: must be a stalemate or better to apply (or not at war yet)
		if warState == PlayerWarStateType.none or warState > PlayerWarStateType.defensive:
			if self.isGoingForWorldConquest():
				viApproachWeights.addWeight(5, MajorPlayerApproachType.war)  # APPROACH_WAR_CONQUEST_GRAND_STRATEGY

		# // // // // // // // // // // // // // // // // // //
		# PERSONALITY
		# // // // // // // // // // // // // // // // // // //

		for loopApproach in MajorPlayerApproachType.all():
			personalityApproachBias = self.playerDict.personalityMajorCivApproachBias(loopApproach)
			viApproachWeights.addWeight(personalityApproachBias, loopApproach)

		# // // // // // // // // // // // // // // // // // //
		# OPINION
		# // // // // // // // // // // // // // // // // // //

		majorCivOpinion = self.majorCivOpinion(otherPlayer)
		if majorCivOpinion == MajorCivOpinionType.unforgivable:  # MAJOR_CIV_OPINION_UNFORGIVABLE:
			viApproachWeights.addWeight(10, MajorPlayerApproachType.war)  # APPROACH_OPINION_UNFORGIVABLE_WAR
			viApproachWeights.addWeight(4, MajorPlayerApproachType.hostile)  # APPROACH_OPINION_UNFORGIVABLE_HOSTILE
			viApproachWeights.addWeight(0, MajorPlayerApproachType.deceptive)  # APPROACH_OPINION_UNFORGIVABLE_DECEPTIVE
			viApproachWeights.addWeight(4, MajorPlayerApproachType.guarded)  # APPROACH_OPINION_UNFORGIVABLE_GUARDED
		elif majorCivOpinion == MajorCivOpinionType.enemy:  # MAJOR_CIV_OPINION_ENEMY:
			viApproachWeights.addWeight(8, MajorPlayerApproachType.war)  # APPROACH_OPINION_ENEMY_WAR
			viApproachWeights.addWeight(4, MajorPlayerApproachType.hostile)  # APPROACH_OPINION_ENEMY_HOSTILE
			viApproachWeights.addWeight(1, MajorPlayerApproachType.deceptive)  # APPROACH_OPINION_ENEMY_DECEPTIVE
			viApproachWeights.addWeight(4, MajorPlayerApproachType.guarded)  # APPROACH_OPINION_ENEMY_GUARDED
		elif majorCivOpinion == MajorCivOpinionType.competitor:  # MAJOR_CIV_OPINION_COMPETITOR:
			viApproachWeights.addWeight(4, MajorPlayerApproachType.war)  # APPROACH_OPINION_COMPETITOR_WAR
			viApproachWeights.addWeight(4, MajorPlayerApproachType.hostile)  # APPROACH_OPINION_COMPETITOR_HOSTILE
			viApproachWeights.addWeight(2, MajorPlayerApproachType.deceptive)  # APPROACH_OPINION_COMPETITOR_DECEPTIVE
			viApproachWeights.addWeight(2, MajorPlayerApproachType.guarded)  # APPROACH_OPINION_COMPETITOR_GUARDED
		elif majorCivOpinion == MajorCivOpinionType.neutral:  # MAJOR_CIV_OPINION_NEUTRAL:
			viApproachWeights.addWeight(0, MajorPlayerApproachType.deceptive)  # APPROACH_OPINION_NEUTRAL_DECEPTIVE
			viApproachWeights.addWeight(2, MajorPlayerApproachType.friendly)  # APPROACH_OPINION_NEUTRAL_FRIENDLY
		elif majorCivOpinion == MajorCivOpinionType.favorable:  # MAJOR_CIV_OPINION_FAVORABLE:
			viApproachWeights.addWeight(-5, MajorPlayerApproachType.hostile)  # APPROACH_OPINION_FAVORABLE_HOSTILE
			viApproachWeights.addWeight(0, MajorPlayerApproachType.deceptive)  # APPROACH_OPINION_FAVORABLE_DECEPTIVE
			viApproachWeights.addWeight(4, MajorPlayerApproachType.friendly)  # APPROACH_OPINION_FAVORABLE_FRIENDLY
		elif majorCivOpinion == MajorCivOpinionType.friend:  # MAJOR_CIV_OPINION_FRIEND:
			viApproachWeights.addWeight(-5, MajorPlayerApproachType.hostile)  # APPROACH_OPINION_FRIEND_HOSTILE
			viApproachWeights.addWeight(10, MajorPlayerApproachType.friendly)  # APPROACH_OPINION_FRIEND_FRIENDLY
		elif majorCivOpinion == MajorCivOpinionType.ally:  # MAJOR_CIV_OPINION_ALLY:
			viApproachWeights.addWeight(10, MajorPlayerApproachType.friendly)  # APPROACH_OPINION_ALLY_FRIENDLY

		# // // // // // // // // // // // // // // // // // //
		# DECLARATION OF FRIENDSHIP
		# // // // // // // // // // // // // // // // // // //

		if self.isDeclarationOfFriendshipAcceptedBy(otherPlayer):
			viApproachWeights.addWeight(3, MajorPlayerApproachType.deceptive)  # APPROACH_DECEPTIVE_WORKING_WITH_PLAYER
			viApproachWeights.addWeight(15, MajorPlayerApproachType.friendly)  # APPROACH_FRIENDLY_WORKING_WITH_PLAYER
			viApproachWeights.addWeight(-100, MajorPlayerApproachType.hostile)  # APPROACH_HOSTILE_WORKING_WITH_PLAYER
			viApproachWeights.addWeight(-100, MajorPlayerApproachType.guarded)  # APPROACH_GUARDED_WORKING_WITH_PLAYER

		# // // // // // // // // // // // // // // // // // //
		# DENOUNCE
		# // // // // // // // // // // // // // // // // // //

		# We denounced them
		if self.isDenouncedPlayer(otherPlayer):
			viApproachWeights.addWeight(10, MajorPlayerApproachType.war)  # APPROACH_WAR_DENOUNCED
			viApproachWeights.addWeight(10, MajorPlayerApproachType.hostile)  # APPROACH_HOSTILE_DENOUNCED
			viApproachWeights.addWeight(5, MajorPlayerApproachType.guarded)  # APPROACH_GUARDED_DENOUNCED
			viApproachWeights.addWeight(-100, MajorPlayerApproachType.friendly)  # APPROACH_FRIENDLY_DENOUNCED
			viApproachWeights.addWeight(-100, MajorPlayerApproachType.deceptive)  # APPROACH_DECEPTIVE_DENOUNCED

		# We were friends and they betrayed us!
		if self.isFriendDenouncedUs(otherPlayer):
			viApproachWeights.addWeight(10, MajorPlayerApproachType.war)  # APPROACH_WAR_DENOUNCED
			viApproachWeights.addWeight(10, MajorPlayerApproachType.hostile)  # APPROACH_HOSTILE_DENOUNCED
			viApproachWeights.addWeight(5, MajorPlayerApproachType.guarded)  # APPROACH_GUARDED_DENOUNCED
			viApproachWeights.addWeight(-100, MajorPlayerApproachType.friendly)  # APPROACH_FRIENDLY_DENOUNCED
			viApproachWeights.addWeight(-100, MajorPlayerApproachType.deceptive)  # APPROACH_DECEPTIVE_DENOUNCED

		# They denounced us
		if otherPlayer.hasMetWith(self.player) and otherPlayer.diplomacyAI.isDenouncedPlayer(self.player):
			viApproachWeights.addWeight(10, MajorPlayerApproachType.war)  # APPROACH_WAR_DENOUNCED
			viApproachWeights.addWeight(10, MajorPlayerApproachType.hostile)  # APPROACH_HOSTILE_DENOUNCED
			viApproachWeights.addWeight(5, MajorPlayerApproachType.guarded)  # APPROACH_GUARDED_DENOUNCED
			viApproachWeights.addWeight(-100, MajorPlayerApproachType.friendly)  # APPROACH_FRIENDLY_DENOUNCED
			viApproachWeights.addWeight(-100, MajorPlayerApproachType.deceptive)  # APPROACH_DECEPTIVE_DENOUNCED

		# // // // // // // // // // // // // // // // // // //
		# WORKING AGAINST THIS PLAYER?
		# // // // // // // // // // // // // // // // // // //

		# if (IsWorkingAgainstPlayer(otherPlayer))
		# viApproachWeights.addWeight(10, MajorPlayerApproachType.deceptive)  # APPROACH_DECEPTIVE_WORKING_AGAINST_PLAYER
		# viApproachWeights.addWeight(10, MajorPlayerApproachType.hostile)  # APPROACH_HOSTILE_WORKING_AGAINST_PLAYER
		# viApproachWeights.addWeight(10, MajorPlayerApproachType.war)  # APPROACH_WAR_WORKING_AGAINST_PLAYER

		# // // // // // // // // // // // // // // // // // //
		# MISTREATED OUR PROTECTED MINORS?
		# // // // // // // // // // // // // // // // // // //

		# antonjs: consider: add cases for IsAngryAboutProtectedMinorBullied, IsAngryAboutSidedWithTheirProtectedMinor

		if self.isAngryAboutProtectedMinorKilled(otherPlayer) or self.isAngryAboutProtectedMinorAttacked(otherPlayer):
			turnsSinceMinorAttack = self.turnsSincePlayerAttackedProtectedMinor(otherPlayer)
			if self.isAngryAboutProtectedMinorKilled(otherPlayer) or turnsSinceMinorAttack < 50:  # OPINION_WEIGHT_ATTACKED_PROTECTED_MINOR_RECENTLY_NUM_TURNS())
				viApproachWeights.addWeight(6, MajorPlayerApproachType.war)  # APPROACH_ATTACKED_PROTECTED_MINOR_WAR
				viApproachWeights.addWeight(2, MajorPlayerApproachType.hostile)  # APPROACH_ATTACKED_PROTECTED_MINOR_HOSTILE
				viApproachWeights.addWeight(1, MajorPlayerApproachType.guarded)  # APPROACH_ATTACKED_PROTECTED_MINOR_GUARDED
			else:
				viApproachWeights.addWeight(4, MajorPlayerApproachType.war)  # APPROACH_ATTACKED_PROTECTED_MINOR_PAST_WAR
				viApproachWeights.addWeight(1, MajorPlayerApproachType.hostile)  # APPROACH_ATTACKED_PROTECTED_MINOR_PAST_HOSTILE
				viApproachWeights.addWeight(1, MajorPlayerApproachType.guarded)  # APPROACH_ATTACKED_PROTECTED_MINOR_PAST_GUARDED

		# // // // // // // // // // // // // // // // // // //
		# They made a demand
		# // // // // // // // // // // // // // // // // // //

		if self.isDemandEverMade(otherPlayer):
			viApproachWeights.addWeight(-6, MajorPlayerApproachType.deceptive)  # APPROACH_DECEPTIVE_DEMAND
			viApproachWeights.addWeight(-6, MajorPlayerApproachType.friendly)  # APPROACH_FRIENDLY_DEMAND

		# // // // // // // // // // // // // // // // // // //
		# BROKEN PROMISES _
		# // // // // // // // // // // // // // // // // // //

		# Broken military promise with us?
		if self.isPlayerBrokenMilitaryPromise(otherPlayer):
			viApproachWeights.addWeight(4, MajorPlayerApproachType.war)  # APPROACH_WAR_BROKEN_MILITARY_PROMISE
			viApproachWeights.addWeight(-10, MajorPlayerApproachType.deceptive)  # APPROACH_DECEPTIVE_BROKEN_MILITARY_PROMISE
			viApproachWeights.addWeight(-10, MajorPlayerApproachType.friendly)  # APPROACH_FRIENDLY_BROKEN_MILITARY_PROMISE

		# Broken military promise with someone?
		# elif (pTeam->IsBrokenMilitaryPromise())
		#	viApproachWeights.addWeight(5, MajorPlayerApproachType.war)  # APPROACH_WAR_BROKEN_MILITARY_PROMISE_WORLD
		#	viApproachWeights.addWeight(-4, MajorPlayerApproachType.deceptive)  # APPROACH_DECEPTIVE_BROKEN_MILITARY_PROMISE_WORLD
		#	viApproachWeights.addWeight(-4, MajorPlayerApproachType.friendly)  # APPROACH_FRIENDLY_BROKEN_MILITARY_PROMISE_WORLD

		# Ignored our request for them to make a military promise?
		elif self.isPlayerIgnoredMilitaryPromise(otherPlayer):
			viApproachWeights.addWeight(-4, MajorPlayerApproachType.deceptive)  # APPROACH_DECEPTIVE_IGNORED_MILITARY_PROMISE
			viApproachWeights.addWeight(-4, MajorPlayerApproachType.friendly)  # APPROACH_FRIENDLY_IGNORED_MILITARY_PROMISE

		# Broken Expansion promise with us?
		if self.isPlayerBrokenExpansionPromiseTowards(otherPlayer):
			viApproachWeights.addWeight(4, MajorPlayerApproachType.war)  # APPROACH_WAR_BROKEN_EXPANSION_PROMISE
			viApproachWeights.addWeight(-6, MajorPlayerApproachType.deceptive)  # APPROACH_DECEPTIVE_BROKEN_EXPANSION_PROMISE
			viApproachWeights.addWeight(-6, MajorPlayerApproachType.friendly)  # APPROACH_FRIENDLY_BROKEN_EXPANSION_PROMISE

		# Ignored our request for them to make a Expansion promise?
		elif self.isPlayerIgnoredExpansionPromiseTowards(otherPlayer):
			viApproachWeights.addWeight(3, MajorPlayerApproachType.war)  # APPROACH_WAR_IGNORED_EXPANSION_PROMISE
			viApproachWeights.addWeight(-4, MajorPlayerApproachType.deceptive)  # APPROACH_DECEPTIVE_IGNORED_EXPANSION_PROMISE
			viApproachWeights.addWeight(-4, MajorPlayerApproachType.friendly)  # APPROACH_FRIENDLY_IGNORED_EXPANSION_PROMISE

		# Broken Border promise with us?
		if self.isPlayerBrokenBorderPromiseTowards(otherPlayer):
			viApproachWeights.addWeight(4, MajorPlayerApproachType.war)  # APPROACH_WAR_BROKEN_BORDER_PROMISE
			viApproachWeights.addWeight(-6, MajorPlayerApproachType.deceptive)  # APPROACH_DECEPTIVE_BROKEN_BORDER_PROMISE
			viApproachWeights.addWeight(-6, MajorPlayerApproachType.friendly)  # APPROACH_FRIENDLY_BROKEN_BORDER_PROMISE

		# Ignored our request for them to make a Border promise?
		elif self.isPlayerIgnoredBorderPromiseTowards(otherPlayer):
			viApproachWeights.addWeight(3, MajorPlayerApproachType.war)  # APPROACH_WAR_IGNORED_BORDER_PROMISE
			viApproachWeights.addWeight(-4, MajorPlayerApproachType.deceptive)  # APPROACH_DECEPTIVE_IGNORED_BORDER_PROMISE
			viApproachWeights.addWeight(-4, MajorPlayerApproachType.friendly)  # APPROACH_FRIENDLY_IGNORED_BORDER_PROMISE

		# Broken CityState attack promise with us?
		if self.isPlayerBrokenAttackCityStatePromise(otherPlayer):
			# antonjs: todo: rename these constants
			viApproachWeights.addWeight(4, MajorPlayerApproachType.war)  # APPROACH_WAR_BROKEN_CITY_STATE_PROMISE
			viApproachWeights.addWeight(-10, MajorPlayerApproachType.deceptive)  # APPROACH_DECEPTIVE_BROKEN_CITY_STATE_PROMISE
			viApproachWeights.addWeight(-10, MajorPlayerApproachType.friendly)  # APPROACH_FRIENDLY_BROKEN_CITY_STATE_PROMISE

		# Broken CityState attack promise with someone?
		#elif pTeam->IsBrokenCityStatePromise():
		#	# antonjs: todo: rename these constants
		#	viApproachWeights.addWeight(3, MajorPlayerApproachType.war)  # APPROACH_WAR_BROKEN_CITY_STATE_PROMISE_WORLD
		#	viApproachWeights.addWeight(-3, MajorPlayerApproachType.deceptive)  # APPROACH_DECEPTIVE_BROKEN_CITY_STATE_PROMISE_WORLD
		#	viApproachWeights.addWeight(-3, MajorPlayerApproachType.friendly)  # APPROACH_FRIENDLY_BROKEN_CITY_STATE_PROMISE_WORLD

		# Ignored our request for them to make a CityState attack promise?
		elif self.isPlayerIgnoredAttackCityStatePromise(otherPlayer):
			# antonjs: todo: rename these constants
			viApproachWeights.addWeight(4, MajorPlayerApproachType.war)  # APPROACH_WAR_IGNORED_CITY_STATE_PROMISE
			viApproachWeights.addWeight(-4, MajorPlayerApproachType.deceptive)  # APPROACH_DECEPTIVE_IGNORED_CITY_STATE_PROMISE
			viApproachWeights.addWeight(-4, MajorPlayerApproachType.friendly)  # APPROACH_FRIENDLY_IGNORED_CITY_STATE_PROMISE

		# Promise to not bully a city - state
		if self.isPlayerBrokenBullyCityStatePromise(otherPlayer):
			# antonjs: todo: custom constants
			viApproachWeights.addWeight(4, MajorPlayerApproachType.war)  # APPROACH_WAR_BROKEN_CITY_STATE_PROMISE() / 2
			viApproachWeights.addWeight(-10, MajorPlayerApproachType.deceptive)  # APPROACH_DECEPTIVE_BROKEN_CITY_STATE_PROMISE() / 2
			viApproachWeights.addWeight(-10, MajorPlayerApproachType.friendly)  # APPROACH_FRIENDLY_BROKEN_CITY_STATE_PROMISE() / 2
		elif self.isPlayerIgnoredBullyCityStatePromise(otherPlayer):
			# antonjs: todo: custom constants
			viApproachWeights.addWeight(4, MajorPlayerApproachType.war)  # APPROACH_WAR_IGNORED_CITY_STATE_PROMISE() / 2
			viApproachWeights.addWeight(-4, MajorPlayerApproachType.deceptive)  # APPROACH_DECEPTIVE_IGNORED_CITY_STATE_PROMISE() / 2
			viApproachWeights.addWeight(-4, MajorPlayerApproachType.friendly)  # APPROACH_FRIENDLY_IGNORED_CITY_STATE_PROMISE() / 2

		# // // // // // // // // // // // // // // // // // //
		# MILITARY THREAT
		# // // // // // // // // // // // // // // // // // //

		militaryThreatValue = self.militaryThreatOf(otherPlayer)
		if militaryThreatValue == MilitaryThreatType.critical:  # THREAT_CRITICAL
			viApproachWeights.addWeight(0, MajorPlayerApproachType.deceptive)  # APPROACH_DECEPTIVE_MILITARY_THREAT_CRITICAL
			viApproachWeights.addWeight(4, MajorPlayerApproachType.guarded)  # APPROACH_GUARDED_MILITARY_THREAT_CRITICAL
			viApproachWeights.addWeight(4, MajorPlayerApproachType.afraid)  # APPROACH_AFRAID_MILITARY_THREAT_CRITICAL
			viApproachWeights.addWeight(0, MajorPlayerApproachType.friendly)  # APPROACH_FRIENDLY_MILITARY_THREAT_CRITICAL
		elif militaryThreatValue == MilitaryThreatType.severe:  # THREAT_SEVERE:
			viApproachWeights.addWeight(0, MajorPlayerApproachType.deceptive)  # APPROACH_DECEPTIVE_MILITARY_THREAT_SEVERE
			viApproachWeights.addWeight(3, MajorPlayerApproachType.guarded)  # APPROACH_GUARDED_MILITARY_THREAT_SEVERE
			viApproachWeights.addWeight(2, MajorPlayerApproachType.afraid)  # APPROACH_AFRAID_MILITARY_THREAT_SEVERE
			viApproachWeights.addWeight(0, MajorPlayerApproachType.friendly)  # APPROACH_FRIENDLY_MILITARY_THREAT_SEVERE
		elif militaryThreatValue == MilitaryThreatType.major:  # THREAT_MAJOR:
			viApproachWeights.addWeight(0, MajorPlayerApproachType.deceptive)  # APPROACH_DECEPTIVE_MILITARY_THREAT_MAJOR
			viApproachWeights.addWeight(2, MajorPlayerApproachType.guarded) # APPROACH_GUARDED_MILITARY_THREAT_MAJOR
			viApproachWeights.addWeight(1, MajorPlayerApproachType.afraid)  # APPROACH_AFRAID_MILITARY_THREAT_MAJOR
			viApproachWeights.addWeight(0, MajorPlayerApproachType.friendly)  # APPROACH_FRIENDLY_MILITARY_THREAT_MAJOR
		elif militaryThreatValue == MilitaryThreatType.minor:  # THREAT_MINOR:
			viApproachWeights.addWeight(0, MajorPlayerApproachType.deceptive)  # APPROACH_DECEPTIVE_MILITARY_THREAT_MINOR
			viApproachWeights.addWeight(0, MajorPlayerApproachType.guarded)  # APPROACH_GUARDED_MILITARY_THREAT_MINOR
			viApproachWeights.addWeight(1, MajorPlayerApproachType.afraid)  # APPROACH_AFRAID_MILITARY_THREAT_MINOR
			viApproachWeights.addWeight(0, MajorPlayerApproachType.friendly)  # APPROACH_FRIENDLY_MILITARY_THREAT_MINOR
		elif militaryThreatValue == MilitaryThreatType.none:  # THREAT_NONE:
			viApproachWeights.addWeight(2, MajorPlayerApproachType.hostile) # APPROACH_HOSTILE_MILITARY_THREAT_NONE

		# // // // // // // // // // // // // // // // // //
		# NUKES
		# // // // // // // // // // // // // // // // // //

		theirNukes = otherPlayer.numberOfNukeUnits(simulation)
		ourNukes = self.player.numberOfNukeUnits(simulation)
		howLikelyAreTheyToNukeUs = 100 if otherPlayer.isHuman() else 0  # assume humans will use'em if they've got'em
		if howLikelyAreTheyToNukeUs == 0:
			if self.isNukedBy(otherPlayer) or otherPlayer.diplomacyAI.isNukedBy(self.player):  # nukes have been used already
				howLikelyAreTheyToNukeUs = 100
			# elif (otherPlayer.diplomacyAI.warProjection(self.player) == WAR_PROJECTION_DESTRUCTION)  # they are surely going to lose a war with
			# howLikelyAreTheyToNukeUs = 100
			else:
				flavorNuke = otherPlayer.grandStrategyAI.personalityAndGrandStrategy(FlavorType.useNuke) + 1
				howLikelyAreTheyToNukeUs = flavorNuke * flavorNuke  # use nukes has to pass 2 rolls

		# do we have nukes and they don't
		if theirNukes == 0 and ourNukes > 0:
			viApproachWeights.addWeight(25, MajorPlayerApproachType.war)
			viApproachWeights.addWeight(25, MajorPlayerApproachType.hostile)
			viApproachWeights.addWeight(25, MajorPlayerApproachType.deceptive)
			viApproachWeights.addWeight(-25, MajorPlayerApproachType.guarded)
			viApproachWeights.addWeight(-50, MajorPlayerApproachType.afraid)

		# do they have nukes and we don't
		elif theirNukes > 0 and ourNukes == 0 and howLikelyAreTheyToNukeUs > 50:
			viApproachWeights.addWeight(50, MajorPlayerApproachType.afraid)
			viApproachWeights.addWeight(50, MajorPlayerApproachType.guarded)
			viApproachWeights.addWeight(-25, MajorPlayerApproachType.deceptive)
			viApproachWeights.addWeight(-50, MajorPlayerApproachType.war)

		# do we both have nukes
		elif theirNukes > 0 and ourNukes > 0 and howLikelyAreTheyToNukeUs > 25:
			viApproachWeights.addWeight(25, MajorPlayerApproachType.guarded)
			viApproachWeights.addWeight(-25, MajorPlayerApproachType.deceptive)
			viApproachWeights.addWeight(-25, MajorPlayerApproachType.war)
			viApproachWeights.addWeight(25, MajorPlayerApproachType.neutral)

		# // // // // // // // // // // // // // // // // //
		# AT WAR RIGHT NOW
		# // // // // // // // // // // // // // // // // //

		for loopPlayer in simulation.players:
			if not loopPlayer.isMajorAI():
				continue

			if self.player == loopPlayer:
				continue

			# Don't look at the guy we're already thinking about or anyone on his team
			if otherPlayer == loopPlayer:
				continue

			if self.isValid(loopPlayer):
				if self.isAtWarWith(loopPlayer):
					if self._stateOfAllWars == PlayerStateAllWars.neutral:  # STATE_ALL_WARS_NEUTRAL
						viApproachWeights.addWeight(-9, MajorPlayerApproachType.war)  # APPROACH_WAR_AT_WAR_WITH_PLAYER_WARS_NEUTRAL
					elif self._stateOfAllWars == PlayerStateAllWars.winning:  # STATE_ALL_WARS_WINNING
						viApproachWeights.addWeight(-3, MajorPlayerApproachType.war)  # APPROACH_WAR_AT_WAR_WITH_PLAYER_WARS_WINNING
					else:
						viApproachWeights.addWeight(-12, MajorPlayerApproachType.war)  # APPROACH_WAR_AT_WAR_WITH_PLAYER_WARS_LOSING

					viApproachWeights.addWeight(-2, MajorPlayerApproachType.hostile)  # APPROACH_HOSTILE_AT_WAR_WITH_PLAYER
					viApproachWeights.addWeight(2, MajorPlayerApproachType.deceptive)  # APPROACH_DECEPTIVE_AT_WAR_WITH_PLAYER
					viApproachWeights.addWeight(0, MajorPlayerApproachType.guarded)  #APPROACH_GUARDED_AT_WAR_WITH_PLAYER
					viApproachWeights.addWeight(2, MajorPlayerApproachType.friendly)  # APPROACH_FRIENDLY_AT_WAR_WITH_PLAYER

		# // // // // // // // // // // // // // // // // //
		# APPROACHES TOWARDS OTHER PLAYERS
		# // // // // // // // // // // // // // // // // //

		# Look at Approaches we've already adopted for players we feel more strongly about
		if lookAtOtherPlayers:
			minorCiv: bool = False

			for loopPlayer in simulation.players:
				if self.player == loopPlayer:
					continue

				# Don't look at the guy we're already thinking about
				if otherPlayer == loopPlayer:
					continue

				if self.isValid(loopPlayer):
					minorCiv: bool = loopPlayer.isCityState()
					approach: MajorPlayerApproachType = self.majorCivApproachTowards(loopPlayer, hideTrueFeelings=False)

					# Planning war with this player? (Can't ONLY use the War Approach because this could have been
					# cleared before, but we have to also check it because it could have just been set for someone
					# else earlier this turn)
					if self.warGoalTowards(loopPlayer) == WarGoalType.prepare or \
						(not minorCiv and approach == MajorPlayerApproachType.war):
						# Major Civs only
						viApproachWeights.addWeight(-12, MajorPlayerApproachType.war)  # APPROACH_WAR_PLANNING_WAR_WITH_ANOTHER_PLAYER
						viApproachWeights.addWeight(-2, MajorPlayerApproachType.hostile)  # APPROACH_HOSTILE_PLANNING_WAR_WITH_ANOTHER_PLAYER
						viApproachWeights.addWeight(2, MajorPlayerApproachType.deceptive)  # APPROACH_DECEPTIVE_PLANNING_WAR_WITH_ANOTHER_PLAYER
						viApproachWeights.addWeight(0, MajorPlayerApproachType.guarded)  # APPROACH_GUARDED_PLANNING_WAR_WITH_ANOTHER_PLAYER
						viApproachWeights.addWeight(2, MajorPlayerApproachType.friendly)  # APPROACH_FRIENDLY_PLANNING_WAR_WITH_ANOTHER_PLAYER

					# Approaches already assigned to other higher-priority Majors
					if not minorCiv:
						if approach == MajorPlayerApproachType.hostile:  # MAJOR_CIV_APPROACH_HOSTILE
							viApproachWeights.addWeight(-2, MajorPlayerApproachType.war)  # APPROACH_WAR_HOSTILE_WITH_ANOTHER_PLAYER
							viApproachWeights.addWeight(-2, MajorPlayerApproachType.hostile)  # APPROACH_HOSTILE_HOSTILE_WITH_ANOTHER_PLAYER
							viApproachWeights.addWeight(2, MajorPlayerApproachType.deceptive)  # APPROACH_DECEPTIVE_HOSTILE_WITH_ANOTHER_PLAYER
							viApproachWeights.addWeight(2, MajorPlayerApproachType.friendly)  # APPROACH_FRIENDLY_HOSTILE_WITH_ANOTHER_PLAYER
						elif approach == MajorPlayerApproachType.afraid:  # MAJOR_CIV_APPROACH_AFRAID:
							viApproachWeights.addWeight(-4, MajorPlayerApproachType.war)  # APPROACH_WAR_AFRAID_WITH_ANOTHER_PLAYER
							viApproachWeights.addWeight(-4, MajorPlayerApproachType.hostile)  # APPROACH_HOSTILE_AFRAID_WITH_ANOTHER_PLAYER
							viApproachWeights.addWeight(2, MajorPlayerApproachType.deceptive)  # APPROACH_DECEPTIVE_AFRAID_WITH_ANOTHER_PLAYER
							viApproachWeights.addWeight(2, MajorPlayerApproachType.friendly)  # APPROACH_FRIENDLY_AFRAID_WITH_ANOTHER_PLAYER

		# // // // // // // // // // // // // // // // // //
		# Are we getting money from trade with them
		# // // // // // // // // // // // // // // // // //
		currentTradeValue = self.player.tradeRoutes.allTradeValueFromPlayer(otherPlayer, YieldType.gold, simulation)
		if currentTradeValue > 0:  # todo: add thresholds
			# todo: constant / XML
			viApproachWeights.addWeight(-5, MajorPlayerApproachType.war)
			viApproachWeights.addWeight(-5, MajorPlayerApproachType.hostile)
			viApproachWeights.addWeight(5, MajorPlayerApproachType.deceptive)
			viApproachWeights.addWeight(-1, MajorPlayerApproachType.guarded)
			viApproachWeights.addWeight(-1, MajorPlayerApproachType.afraid)
			viApproachWeights.addWeight(5, MajorPlayerApproachType.friendly)
			viApproachWeights.addWeight(-2, MajorPlayerApproachType.neutral)

			# sanity check - if we will go negative from war with this player, don't go to war
			gpt = self.player.treasury.calculateGrossGold(simulation)
			deltaGPT = gpt - currentTradeValue
			if gpt >= 0 and (deltaGPT < 0):
				viApproachWeights.addWeight(deltaGPT, MajorPlayerApproachType.war)

		# // // // // // // // // // // // // // // // // //
		# WAR PROJECTION - how do we think a war against otherPlayer will go?
		# // // // // // // // // // // // // // // // // //

		warProjection: WarProjectionType = self.warProjectionAgainst(otherPlayer)

		if warProjection == WarProjectionType.destruction:  # WAR_PROJECTION_DESTRUCTION
			viApproachWeights.mulWeight(45, MajorPlayerApproachType.war)  # APPROACH_WAR_PROJECTION_DESTRUCTION_PERCENT
			viApproachWeights.divWeight(100, MajorPlayerApproachType.war)
			viApproachWeights.mulWeight(45, MajorPlayerApproachType.deceptive)  # APPROACH_WAR_PROJECTION_DESTRUCTION_PERCENT
			viApproachWeights.divWeight(100, MajorPlayerApproachType.deceptive)
			viApproachWeights.mulWeight(125, MajorPlayerApproachType.guarded)  # APPROACH_GUARDED_PROJECTION_DESTRUCTION_PERCENT
			viApproachWeights.divWeight(100, MajorPlayerApproachType.guarded)
		elif warProjection == WarProjectionType.defeat:  # WAR_PROJECTION_DEFEAT
			viApproachWeights.mulWeight(60, MajorPlayerApproachType.war)  # APPROACH_WAR_PROJECTION_DEFEAT_PERCENT
			viApproachWeights.divWeight(100, MajorPlayerApproachType.war)
			viApproachWeights.mulWeight(60, MajorPlayerApproachType.deceptive)  # APPROACH_WAR_PROJECTION_DEFEAT_PERCENT
			viApproachWeights.divWeight(100, MajorPlayerApproachType.deceptive)
			viApproachWeights.mulWeight(115, MajorPlayerApproachType.guarded)  # APPROACH_GUARDED_PROJECTION_DEFEAT_PERCENT
			viApproachWeights.divWeight(100, MajorPlayerApproachType.guarded)
		elif warProjection == WarProjectionType.stalemate:  # WAR_PROJECTION_STALEMATE
			viApproachWeights.mulWeight(80, MajorPlayerApproachType.war)  # APPROACH_WAR_PROJECTION_STALEMATE_PERCENT
			viApproachWeights.divWeight(100, MajorPlayerApproachType.war)
			viApproachWeights.mulWeight(105, MajorPlayerApproachType.guarded)  # APPROACH_GUARDED_PROJECTION_STALEMATE_PERCENT
			viApproachWeights.divWeight(100, MajorPlayerApproachType.guarded)
		elif warProjection == WarProjectionType.unknown:  # WAR_PROJECTION_UNKNOWN
			viApproachWeights.mulWeight(100, MajorPlayerApproachType.war)  # APPROACH_WAR_PROJECTION_UNKNOWN_PERCENT
			viApproachWeights.divWeight(100, MajorPlayerApproachType.war)
			viApproachWeights.mulWeight(100, MajorPlayerApproachType.guarded)  # APPROACH_GUARDED_PROJECTION_UNKNOWN_PERCENT
			viApproachWeights.divWeight(100, MajorPlayerApproachType.guarded)
		elif warProjection == WarProjectionType.good:  # WAR_PROJECTION_GOOD
			viApproachWeights.mulWeight(150, MajorPlayerApproachType.war)  # APPROACH_WAR_PROJECTION_GOOD_PERCENT
			viApproachWeights.divWeight(100, MajorPlayerApproachType.war)
			viApproachWeights.mulWeight(150, MajorPlayerApproachType.deceptive)  # APPROACH_WAR_PROJECTION_GOOD_PERCENT
			viApproachWeights.divWeight(100, MajorPlayerApproachType.deceptive)
			viApproachWeights.mulWeight(80, MajorPlayerApproachType.guarded)  # APPROACH_GUARDED_PROJECTION_GOOD_PERCENT
			viApproachWeights.divWeight(100, MajorPlayerApproachType.guarded)
		elif warProjection == WarProjectionType.veryGood:  # WAR_PROJECTION_VERY_GOOD
			viApproachWeights.mulWeight(180, MajorPlayerApproachType.war)  # APPROACH_WAR_PROJECTION_VERY_GOOD_PERCENT
			viApproachWeights.divWeight(100, MajorPlayerApproachType.war)
			viApproachWeights.mulWeight(180, MajorPlayerApproachType.deceptive)  # APPROACH_WAR_PROJECTION_VERY_GOOD_PERCENT
			viApproachWeights.divWeight(100, MajorPlayerApproachType.deceptive)
			viApproachWeights.mulWeight(60, MajorPlayerApproachType.guarded)  # APPROACH_GUARDED_PROJECTION_VERY_GOOD_PERCENT
			viApproachWeights.divWeight(100, MajorPlayerApproachType.guarded)

		# // // // // // // // // // // // // // // // // //
		# Is this player a reckless expander?
		# // // // // // // // // // // // // // // // // //

		if self.isRecklessExpanderTowards(otherPlayer, simulation):
			viApproachWeights.mulWeight(160, MajorPlayerApproachType.war)  # APPROACH_WAR_RECKLESS_EXPANDER
			viApproachWeights.divWeight(100, MajorPlayerApproachType.war)
			viApproachWeights.mulWeight(160, MajorPlayerApproachType.deceptive)  # APPROACH_WAR_RECKLESS_EXPANDER
			viApproachWeights.divWeight(100, MajorPlayerApproachType.deceptive)

		# // // // // // // // // // // // // // // // // //
		# Is this player already in a war with someone who isn't us?
		# // // // // // // // // // // // // // // // // //

		thinkingAboutDogpiling: bool = False
		for loopPlayer in simulation.players:
			if self.player == loopPlayer:
				continue

			if otherPlayer == loopPlayer:
				continue

			# Don't look at the guy we're already thinking about
			if not loopPlayer.isAlive():
				continue

			# Is this a player we have relations with?
			if not self.hasMetWith(loopPlayer):
				continue

			if not otherPlayer.hasMetWith(loopPlayer):
				continue

			loopWarState: PlayerWarStateType = otherPlayer.diplomacyAI.warStateTowards(loopPlayer)
			if loopWarState != PlayerWarStateType.none:
				thinkingAboutDogpiling = True

		if thinkingAboutDogpiling:
			viApproachWeights.mulWeight(200, MajorPlayerApproachType.war)
			viApproachWeights.divWeight(100, MajorPlayerApproachType.war)
			viApproachWeights.mulWeight(150, MajorPlayerApproachType.deceptive)
			viApproachWeights.divWeight(100, MajorPlayerApproachType.deceptive)

		# // // // // // // // // // // // // // // // // //
		# DISTANCE - the farther away a player is the less likely we are to want to attack them!
		# // // // // // // // // // // // // // // // // //

		# Factor in distance
		proximity: PlayerProximityType = self.proximityTo(otherPlayer)
		if proximity == PlayerProximityType.neighbors:  # PLAYER_PROXIMITY_NEIGHBORS
			viApproachWeights.mulWeight(115, MajorPlayerApproachType.war)  # APPROACH_WAR_PROXIMITY_NEIGHBORS
			viApproachWeights.divWeight(100, MajorPlayerApproachType.war)
			viApproachWeights.mulWeight(115, MajorPlayerApproachType.deceptive)  # APPROACH_WAR_PROXIMITY_NEIGHBORS
			viApproachWeights.divWeight(100, MajorPlayerApproachType.deceptive)
		elif proximity == PlayerProximityType.close:  # PLAYER_PROXIMITY_CLOSE:
			viApproachWeights.mulWeight(100, MajorPlayerApproachType.war)  # APPROACH_WAR_PROXIMITY_CLOSE
			viApproachWeights.divWeight(100, MajorPlayerApproachType.war)
			viApproachWeights.mulWeight(100, MajorPlayerApproachType.deceptive)  # APPROACH_WAR_PROXIMITY_CLOSE
			viApproachWeights.divWeight(100, MajorPlayerApproachType.deceptive)
		elif proximity == PlayerProximityType.far:  # PLAYER_PROXIMITY_FAR:
			viApproachWeights.mulWeight(60, MajorPlayerApproachType.war)  # APPROACH_WAR_PROXIMITY_FAR
			viApproachWeights.divWeight(100, MajorPlayerApproachType.war)
			viApproachWeights.mulWeight(60, MajorPlayerApproachType.deceptive)  # APPROACH_WAR_PROXIMITY_FAR
			viApproachWeights.divWeight(100, MajorPlayerApproachType.deceptive)
		elif proximity == PlayerProximityType.distant:  # PLAYER_PROXIMITY_DISTANT:
			viApproachWeights.mulWeight(50, MajorPlayerApproachType.war)  # APPROACH_WAR_PROXIMITY_DISTANT
			viApproachWeights.divWeight(100, MajorPlayerApproachType.war)
			viApproachWeights.mulWeight(50, MajorPlayerApproachType.deceptive)  # APPROACH_WAR_PROXIMITY_DISTANT
			viApproachWeights.divWeight(100, MajorPlayerApproachType.deceptive)

		# // // // // // // // // // // // // // // // // //
		# PEACE TREATY - have we made peace with this player before?  If so, reduce war weight
		# // // // // // // // // // // // // // // // // //

		peaceTreatyTurn = self.turnMadePeaceTreatyWith(otherPlayer)
		if peaceTreatyTurn > -1:
			turnsSincePeace = simulation.currentTurn - peaceTreatyTurn
			if turnsSincePeace < 25:  # TURNS_SINCE_PEACE_WEIGHT_DAMPENER
				viApproachWeights.mulWeight(65, MajorPlayerApproachType.war)  # APPROACH_WAR_HAS_MADE_PEACE_BEFORE_PERCENT
				viApproachWeights.divWeight(100, MajorPlayerApproachType.war)

		# // // // // // // // // // // // // // // // // //
		# DUEL - If there's only 2 players in this game, no friendly or deceptive
		# // // // // // // // // // // // // // // // // //

		numMajorsLeft = simulation.countMajorCivsAlive()
		if numMajorsLeft == 2:
			viApproachWeights.setWeight(0, MajorPlayerApproachType.deceptive)
			viApproachWeights.setWeight(0, MajorPlayerApproachType.friendly)

		# // // // // // // // // // // // // // // // // //
		# COOP WAR - agreed to go to war with someone?
		# // // // // // // // // // // // // // // // // //

		if self.isLockedIntoCoopWarWith(otherPlayer):
			viApproachWeights.addWeight(1000, MajorPlayerApproachType.war)  # COOP_WAR_LOCKED_TURNS_WAR_WEIGHT

		# // // // // // // // // // // // // // // // // //
		# RANDOM FACTOR
		# // // // // // // // // // // // // // // // // //

		for loopApproach in MajorPlayerApproachType.all():
			# Increase weights to hundreds to give us more fidelity
			viApproachWeights.mulWeight(100, loopApproach)

			randAmount = viApproachWeights.weight(loopApproach) * 15  # APPROACH_RANDOM_PERCENT

			# If the amount is negative, only bad things can happen. Plus, it's not likely we're going to pick this anyways
			if randAmount > 0:
				randAmount /= 100
				randValue = 0 if Tests.are_running else random.randint(0, int(randAmount))
				viApproachWeights.addWeight(randValue, loopApproach)

		# // // // // // // // // // // // // // // // // // //
		# CAN WE DECLARE WAR?
		# // // // // // // // // // // // // // // // // // //

		if not self.player.canDeclareWarTowards(otherPlayer):
			# If we're already at war with this player don't cancel out the weight for them!
			if not self.player.isAtWarWith(otherPlayer):
				viApproachWeights.setWeight(0, MajorPlayerApproachType.war)

		# // // // // // // // // // // // // // // // // // //
		# On the same team?
		# // // // // // // // // // // // // // // // // // //

		if self.isAlliedWith(otherPlayer):
			viApproachWeights.setWeight(0, MajorPlayerApproachType.war)
			viApproachWeights.setWeight(0, MajorPlayerApproachType.hostile)
			viApproachWeights.setWeight(0, MajorPlayerApproachType.deceptive)
			viApproachWeights.setWeight(0, MajorPlayerApproachType.guarded)
			viApproachWeights.setWeight(0, MajorPlayerApproachType.afraid)
			viApproachWeights.setWeight(0, MajorPlayerApproachType.neutral)
			viApproachWeights.setWeight(100, MajorPlayerApproachType.friendly)

		# // // // // // // // // // // // // // // // // // //
		# MODIFY WAR BASED ON HUMAN DIFFICULTY LEVEL
		# // // // // // // // // // // // // // // // // // //

		if otherPlayer.isHuman():
			handicap: HandicapType = simulation.handicap  # otherPlayer.getHandicapType
			warModifier: int = handicap.aiDeclareWarProbability()

			viApproachWeights.mulWeight(warModifier, MajorPlayerApproachType.war)
			viApproachWeights.divWeight(100, MajorPlayerApproachType.war)
			viApproachWeights.mulWeight(warModifier, MajorPlayerApproachType.deceptive)
			viApproachWeights.divWeight(100, MajorPlayerApproachType.deceptive)

		# This vector is what we'll use to sort
		approachWeightsForSorting = WeightedBaseList()

		# Transfer values from our normal int vector (which we need for logging) to the Weighted Vector we can sort
		for loopApproach in MajorPlayerApproachType.all():
			value = viApproachWeights.weight(loopApproach)
			approachWeightsForSorting.setWeight(value, loopApproach)

		approachWeightsForSorting.sortByValue(reverse=True)

		highestApproach = firstOrNone(approachWeightsForSorting.keys())
		highestWeight = firstOrNone(approachWeightsForSorting.values())

		# If we're going to war then update how we're acting
		if highestApproach == MajorPlayerApproachType.war:
			warFace = self.warFaceWith(otherPlayer)

			# If we haven't set WarFace on a previous turn, figure out what it should be
			if warFace == PlayerWarFaceType.none:
				# Use index of 1 since we already know element 0 is war that will give us the most reasonable approach
				tempApproach: MajorPlayerApproachType = secondOrNone(list(approachWeightsForSorting.keys()))

				# Pick among the Approach types
				if tempApproach == MajorPlayerApproachType.hostile:
					warFace = PlayerWarFaceType.hostile  # WAR_FACE_HOSTILE

				elif tempApproach == MajorPlayerApproachType.deceptive or \
					tempApproach == MajorPlayerApproachType.afraid or \
					tempApproach == MajorPlayerApproachType.friendly:

					# Denounced them? If so, let's not be too friendly
					if self.isDenouncedPlayer(otherPlayer):
						warFace = PlayerWarFaceType.neutral
					else:
						warFace = PlayerWarFaceType.friendly
				else:
					warFace = PlayerWarFaceType.neutral
		else:
			warFace = PlayerWarFaceType.none

		# Don't want to log if we're just seeing what the highest weight is and don't care about what Approach we like
		if log:
			self.logMajorCivApproachUpdate(otherPlayer, viApproachWeights, highestApproach, oldApproach, warFace)

		return highestWeight, highestApproach, warFace

	def logMajorCivApproachUpdate(self, otherPlayer, weights: WeightedBaseList, highestApproach: MajorPlayerApproachType, oldApproach: MajorPlayerApproachType, warFace: PlayerWarFaceType):
		"""Log Major Civ Approach Update"""
		if highestApproach != oldApproach:
			logging.info(f'Player {self.player} has change the opinion of player {otherPlayer} from {oldApproach} to {oldApproach} ({warFace})')

		return

	def isWillingToMakePeaceWithHumanPlayer(self, humanPlayer, simulation) -> bool:
		"""Need some special rules for humans so that the AI isn't exploited"""
		humanDiplomacyAI = humanPlayer.diplomacyAI
		playerDiplomacyAI = self.player.diplomacyAI

		if humanPlayer.isHuman():
			willMakePeace = self.playerDict.turnsOfWarWith(humanPlayer, simulation.currentTurn) >= 5

			if not self.canChangeWarPeaceWith(humanPlayer):
				return False

			# If either of us are locked in, then we're not willing to make peace (this prevents weird greetings and
			# stuff) - we use > 1 because it'll get decremented after it appears the human make peace again
			if playerDiplomacyAI.numberOfTurnsLockedIntoWarWith(humanPlayer) > 1:
				return False

			if humanDiplomacyAI.numberOfTurnsLockedIntoWarWith(self.player) > 1:
				return False

			return willMakePeace

		return True

	def canChangeWarPeaceWith(self, otherPlayer) -> bool:
		if self.isAlliedWith(otherPlayer):
			return False

		return True

	def isAlliedWith(self, otherPlayer) -> bool:
		return self.playerDict.isAlliedWith(otherPlayer)

	def updateTreatyWillingToOfferWith(self, otherPlayer, treaty: PeaceTreatyType):
		self.playerDict.updateTreatyWillingToOfferWith(otherPlayer, treaty)

	def updateTreatyWillingToAcceptWith(self, otherPlayer, treaty: PeaceTreatyType):
		self.playerDict.updateTreatyWillingToAcceptWith(otherPlayer, treaty)

	def warProjectionAgainst(self, otherPlayer) -> WarProjectionType:
		"""What is the Projection of war with this Player"""
		return self.playerDict.warProjectionAgainst(otherPlayer)

	def warDamageLevelFrom(self, otherPlayer) -> WarDamageLevelType:
		return self.playerDict.warDamageLevelFrom(otherPlayer)

	def hasBrokenPeaceTreaty(self) -> bool:
		return self._hasBrokenPeaceTreatyValue

	def bestApproachTowardsMinorCiv(self, otherPlayer, lookAtOtherPlayers: bool, log: bool, simulation) -> (int, MinorPlayerApproachType):
		"""What is the best approach to take towards a Minor Civ?  Can also pass in iHighestWeight by reference
		if you just want to know what the player feels most strongly about without actually caring about WHAT it is"""
		# This vector is what we'll stuff the values into first, and pass it into our logging function (which can't
		# take a CvWeightedVector, which we need to sort...)
		viApproachWeights = WeightedBaseList()

		for loopApproach in MinorPlayerApproachType.all():
			viApproachWeights.setWeight(0, loopApproach)

		# // // // // // // // // // // // // // // // // // //
		# NEUTRAL DEFAULT WEIGHT
		# // // // // // // // // // // // // // // // // // //

		viApproachWeights.addWeight(1, MinorPlayerApproachType.ignore)  # MINOR_APPROACH_IGNORE_DEFAULT

		# // // // // // // // // // // // // // // // // // //
		# CURRENT SITUATION BIASES
		# // // // // // // // // // // // // // // // // // //

		# Bias for our current Approach.This should prevent it from jumping around from turn-to-turn as much
		# We use the scratch pad here since the normal array has been cleared so that we have knowledge of who we've
		# already assigned an Approach for this turn this should be the only place the scratch pad is used
		if self._paeApproachScratchPad.weight(hash(otherPlayer)) not in MinorPlayerApproachType.all():
			return 0, MinorPlayerApproachType.none

		oldApproach: MinorPlayerApproachType = self._paeApproachScratchPad.weight(hash(otherPlayer))
		viApproachWeights.addWeight(2, oldApproach)  # MINOR_APPROACH_BIAS_FOR_CURRENT

		# If we're planning a war then give it a bias so that we don't get away from it too easily
		if oldApproach == MinorPlayerApproachType.conquest:
			# Add some bias to Ignore to help us get out in case things get sticky
			viApproachWeights.addWeight(3, MinorPlayerApproachType.ignore)  # MINOR_APPROACH_IGNORE_CURRENTLY_WAR

			# Don't give this bias if war is going poorly
			warState: PlayerWarStateType = self.warStateTowards(otherPlayer)
			if warState > PlayerWarStateType.stalemate:
				viApproachWeights.addWeight(4, MinorPlayerApproachType.conquest)  # APPROACH_WAR_CURRENTLY_WAR

		# If we're Protective then knock Conquest down & pump Protective up
		elif oldApproach == MinorPlayerApproachType.protective:
			viApproachWeights.addWeight(-10, MinorPlayerApproachType.conquest)  # MINOR_APPROACH_WAR_CURRENTLY_PROTECTIVE
			viApproachWeights.addWeight(10, MinorPlayerApproachType.protective)  # MINOR_APPROACH_PROTECTIVE_CURRENTLY_PROTECTIVE
			viApproachWeights.addWeight(-10, MinorPlayerApproachType.bully)  # antonjs: todo: constant / XML

		# If we're ALREADY at war with this player then we're much less likely to be Protective
		if self.isAtWarWith(otherPlayer):
			viApproachWeights.addWeight(-15, MinorPlayerApproachType.protective)  # MINOR_APPROACH_PROTECTIVE_CURRENTLY_WAR
			viApproachWeights.addWeight(-6, MinorPlayerApproachType.friendly)  # MINOR_APPROACH_FRIENDLY_CURRENTLY_WAR

		# // // // // // // // // // // // // // // // // // //
		# RESOURCES
		# // // // // // // // // // // // // // // // // // //

		numWeLack = otherPlayer.minorCivAI.numberResourcesMajorLacks(self.player)
		if numWeLack > 0:
			viApproachWeights.addWeight(numWeLack * 1, MinorPlayerApproachType.friendly)  # MINOR_APPROACH_FRIENDLY_RESOURCES
			viApproachWeights.addWeight(numWeLack * 1, MinorPlayerApproachType.protective)  # MINOR_APPROACH_PROTECTIVE_RESOURCES
			viApproachWeights.addWeight(numWeLack * 1, MinorPlayerApproachType.conquest)  # MINOR_APPROACH_PROTECTIVE_RESOURCES

		# // // // // // // // // // // // // // // // // // //
		# FRIENDS WITH MINOR
		# // // // // // // // // // // // // // // // // // //

		if otherPlayer.minorCivAI.isFriends(self.player):
			viApproachWeights.addWeight(-100, MinorPlayerApproachType.conquest)  # MINOR_APPROACH_WAR_FRIENDS
			viApproachWeights.addWeight(4, MinorPlayerApproachType.friendly)  # MINOR_APPROACH_FRIENDLY_FRIENDS
			viApproachWeights.addWeight(2, MinorPlayerApproachType.protective)  # MINOR_APPROACH_PROTECTIVE_FRIENDS // antonjs: todo: increase
			viApproachWeights.addWeight(-10, MinorPlayerApproachType.bully)  # antonjs: todo: constant / XML

		# // // // // // // // // // // // // // // // // // //
		# PLEDGE TO PROTECT - have we pledged to protect this minor?
		# // // // // // // // // // // // // // // // // // //
		# antonjs: consider: disable this weight after a certain amount of turns, to have this player "reevaluate" its PtP
		if otherPlayer.minorCivAI.isProtectedByMajor(self.player):
			viApproachWeights.addWeight(2, MinorPlayerApproachType.protective)  # antonjs: todo: constant / XML
			viApproachWeights.addWeight(-1, MinorPlayerApproachType.bully)  # antonjs: todo: constant / XML
			viApproachWeights.addWeight(-2, MinorPlayerApproachType.conquest)  # antonjs: todo: constant / XML

		# // // // // // // // // // // // // // // // // // //
		# PERSONALITY
		# // // // // // // // // // // // // // // // // // //

		for loopApproach in MinorPlayerApproachType.all():
			viApproachWeights.addWeight(self.personalityMinorCivApproachBias(loopApproach), loopApproach)

		isGoodWarTarget: bool = False
		checkIfGoodWarTarget: bool = False

		# // // // // // // // // // // // // // // // // // //
		# CONQUEST GRAND STRATEGY
		# // // // // // // // // // // // // // // // // // //

		if self.isGoingForWorldConquest():
			viApproachWeights.addWeight(10, MinorPlayerApproachType.conquest)  # MINOR_APPROACH_WAR_CONQUEST_GRAND_STRATEGY
			viApproachWeights.addWeight(-15, MinorPlayerApproachType.protective)  # MINOR_APPROACH_PROTECTIVE_CONQUEST_GRAND_STRATEGY
			viApproachWeights.addWeight(-5, MinorPlayerApproachType.friendly)  # MINOR_APPROACH_FRIENDLY_CONQUEST_GRAND_STRATEGY
			viApproachWeights.addWeight(8, MinorPlayerApproachType.bully)  # antonjs: todo: constant / XML

			# if we're neighbors, make it even more likely we'll go to war
			if self.player.proximityTo(otherPlayer) == PlayerProximityType.neighbors:
				isGoodWarTarget = True

		# // // // // // // // // // // // // // // // // // //
		# DIPLO GRAND STRATEGY
		# // // // // // // // // // // // // // // // // // //

		elif self.isGoingForDiploVictory():
			viApproachWeights.addWeight(-20, MinorPlayerApproachType.conquest)  # MINOR_APPROACH_WAR_DIPLO_GRAND_STRATEGY
			viApproachWeights.addWeight(-15, MinorPlayerApproachType.ignore)  # MINOR_APPROACH_IGNORE_DIPLO_GRAND_STRATEGY
			viApproachWeights.addWeight(-15, MinorPlayerApproachType.bully)  # antonjs: todo: constant / XML

			# Neighbors and Close: +5 to Protective
			if self.player.proximityTo(otherPlayer) >= PlayerProximityType.close:
				viApproachWeights.addWeight(5, MinorPlayerApproachType.protective)  # MINOR_APPROACH_PROTECTIVE_DIPLO_GRAND_STRATEGY_NEIGHBORS

		# // // // // // // // // // // // // // // // // // //
		# CULTURE GRAND STRATEGY
		# // // // // // // // // // // // // // // // // // //

		elif self.isGoingForCultureVictory():
			viApproachWeights.addWeight(-20, MinorPlayerApproachType.conquest)  # MINOR_APPROACH_WAR_CULTURE_GRAND_STRATEGY
			viApproachWeights.addWeight(-15, MinorPlayerApproachType.ignore)  # MINOR_APPROACH_IGNORE_CULTURE_GRAND_STRATEGY
			viApproachWeights.addWeight(-10, MinorPlayerApproachType.bully)  # antonjs: todo: constant / XML

			# Minor is cultural
			if otherPlayer.cityState.category() == CityStateCategory.cultural:
				viApproachWeights.addWeight(5, MinorPlayerApproachType.protective)  # MINOR_APPROACH_PROTECTIVE_CULTURE_GRAND_STRATEGY_CST
			else:
				checkIfGoodWarTarget = True

		# // // // // // // // // // // // // // // // // // //
		# SCIENCE GRAND STRATEGY
		# // // // // // // // // // // // // // // // // // //

		else:
			checkIfGoodWarTarget = True

		# See if this minor is on same continent as a major power we want to attack
		isGoodWarTarget: bool = False
		if checkIfGoodWarTarget:
			for loopPlayer in simulation.players:
				if not self.isValid(loopPlayer):
					continue

				# Make sure it is another valid player and not already at war with them
				if loopPlayer == self.player:
					continue

				if not loopPlayer.isMajorAI():
					continue

				if not self.player.isAtWarWith(loopPlayer):
					# Do we want to attack them?
					if self.majorCivApproachTowards(loopPlayer, hideTrueFeelings=False) == MajorPlayerApproachType.war:
						# All of us neighbors on same landmass?
						loopPlayerArea = simulation.areaOfCapitalOf(loopPlayer)
						otherPlayerArea = simulation.areaOfCapitalOf(otherPlayer)
						ownPlayerArea = simulation.areaOfCapitalOf(self.player)

						if loopPlayerArea is not None and otherPlayerArea is not None and ownPlayerArea is not None and \
							loopPlayerArea == otherPlayerArea and ownPlayerArea == loopPlayerArea:

							if loopPlayer.proximityTo(otherPlayer) >= PlayerProximityType.neighbors and \
								self.player.proximityTo(otherPlayer) >= PlayerProximityType.neighbors:
								isGoodWarTarget = True

		if isGoodWarTarget:
			viApproachWeights.addWeight(10, MinorPlayerApproachType.conquest)  # MINOR_APPROACH_WAR_CONQUEST_GRAND_STRATEGY_NEIGHBORS
			viApproachWeights.addWeight(8, MinorPlayerApproachType.bully)  # antonjs: todo: constant / XML

		# // // // // // // // // // // // // // // // // // //
		# TRAITS THAT EFFECT MINORS - These are heavy handed, but that is intentional
		# // // // // // // // // // // // // // // // // // //

		iBonusTraitMod = 0
		iBonusTraitMod += 100 if self.player.traits().cityStateFriendshipModifier() > 0 else 0
		iBonusTraitMod += 100 if self.player.traits().cityStateBonusModifier() > 0 else 0
		iBonusTraitMod += -100 if self.player.traits().cityStateCombatModifier() > 0 else 0
		if iBonusTraitMod > 0:
			viApproachWeights.addWeight(-iBonusTraitMod, MinorPlayerApproachType.conquest)
			viApproachWeights.addWeight(-iBonusTraitMod / 5, MinorPlayerApproachType.bully)
			viApproachWeights.addWeight(iBonusTraitMod / 5, MinorPlayerApproachType.friendly)
			viApproachWeights.addWeight(iBonusTraitMod, MinorPlayerApproachType.protective)

		if iBonusTraitMod >= 0 and self.player.numberOfCities(simulation) <= 1:
			viApproachWeights.addWeight(-200, MinorPlayerApproachType.conquest)

		# // // // // // // // // // // // // // // // // // //
		# RELIGION
		# // // // // // // // // // // // // // // // // // //
		# antonjs: todo: befriend / protect religious minors if we have a religion strategy

		# // // // // // // // // // // // // // // // // // //
		# HAPPINESS
		# // // // // // // // // // // // // // // // // // //
		# antonjs: todo: befriend / protect mercantile minors if we are in need of happiness

		# // // // // // // // // // // // // // // // // // //
		# MILITARY THREAT
		# // // // // // // // // // // // // // // // // // //

		# switch(GetMilitaryThreat(otherPlayer))
		# case THREAT_CRITICAL:
		# viApproachWeights[MAJOR_CIV_APPROACH_DECEPTIVE] += 0  # APPROACH_DECEPTIVE_MILITARY_THREAT_CRITICAL
		# break
		# case THREAT_SEVERE:
		# case THREAT_MAJOR:
		# case THREAT_MINOR:
		# case THREAT_NONE:
		# break

		# // // // // // // // // // // // // // // // // // //
		# AT WAR RIGHT NOW
		# // // // // // // // // // // // // // // // // // //

		for loopPlayer in simulation.players:
			if not self.isValid(loopPlayer):
				continue

			# Don't look at the guy we're already thinking about or anyone on his team
			if loopPlayer == self.player or loopPlayer == otherPlayer:
				continue

			if not loopPlayer.isMajorAI():
				continue

			if self.player.isAtWarWith(loopPlayer):
				if self._stateOfAllWars == PlayerStateAllWars.neutral:
					viApproachWeights.addWeight(-9, MinorPlayerApproachType.conquest)  # APPROACH_WAR_AT_WAR_WITH_PLAYER_WARS_NEUTRAL
				elif self._stateOfAllWars == PlayerStateAllWars.winning:
					viApproachWeights.addWeight(-3, MinorPlayerApproachType.conquest)  # APPROACH_WAR_AT_WAR_WITH_PLAYER_WARS_WINNING
				else:
					viApproachWeights.addWeight(-12, MinorPlayerApproachType.conquest)  # APPROACH_WAR_AT_WAR_WITH_PLAYER_WARS_LOSING

		# // // // // // // // // // // // // // // // // // //
		# APPROACHES TOWARDS OTHER PLAYERS
		# // // // // // // // // // // // // // // // // // //

		# Look at Approaches we've already adopted for players we feel more strongly about
		if lookAtOtherPlayers:
			# Major Civs
			for loopPlayer in simulation.players:
				if not self.isValid(loopPlayer):
					continue

				# Don't look at the guy we're already thinking about or anyone on his team
				if loopPlayer == self.player or loopPlayer == otherPlayer:
					continue

				if not loopPlayer.isMajorAI():
					continue

				minorCiv = loopPlayer.isCityState()

				# Planning war with this player? (Can't ONLY use the War Approach because this could have been
				# cleared before, but we have to also check it because it could have just been set for someone else
				# earlier this turn)
				if self.warGoalTowards(loopPlayer) == WarGoalType.prepare or \
					(not minorCiv and self.majorCivApproachTowards(loopPlayer, hideTrueFeelings=False) == MajorPlayerApproachType.war):
					viApproachWeights.addWeight(-20, MinorPlayerApproachType.conquest)  # MINOR_APPROACH_WAR_PLANNING_WAR_WITH_ANOTHER_PLAYER

				# Approaches already assigned to other higher-priority Minors
				if minorCiv:
					minorCivApproach: MinorPlayerApproachType = self.minorApproachTowards(loopPlayer)

					if minorCivApproach == MinorPlayerApproachType.conquest:  # MINOR_CIV_APPROACH_CONQUEST
						viApproachWeights.addWeight(-20, MinorPlayerApproachType.conquest)  # MINOR_APPROACH_WAR_PLANNING_WAR_WITH_ANOTHER_PLAYER
					elif minorCivApproach == MinorPlayerApproachType.protective:  # MINOR_CIV_APPROACH_PROTECTIVE:
						# If we're already protecting other Minors then we've already been stretched thin
						viApproachWeights.addWeight(-2, MinorPlayerApproachType.protective)  # MINOR_APPROACH_PROTECTIVE_WITH_ANOTHER_PLAYER
					elif minorCivApproach == MinorPlayerApproachType.bully:  # MINOR_CIV_APPROACH_BULLY:
						# If we're already bullying another player, we don't want to piss off too many
						viApproachWeights.addWeight(-2, MinorPlayerApproachType.bully)  # antonjs: todo: constant / XML

		# // // // // // // // // // // // // // // // // // //
		# PROXIMITY
		# // // // // // // // // // // // // // // // // // //

		proximityValue: PlayerProximityType = self.proximityTo(otherPlayer)
		if proximityValue == PlayerProximityType.neighbors:  # PLAYER_PROXIMITY_NEIGHBORS
			viApproachWeights.addWeight(-2, MinorPlayerApproachType.ignore)  # MINOR_APPROACH_IGNORE_PROXIMITY_NEIGHBORS
			viApproachWeights.addWeight(-1, MinorPlayerApproachType.friendly)  # MINOR_APPROACH_FRIENDLY_PROXIMITY_NEIGHBORS
			viApproachWeights.addWeight(1, MinorPlayerApproachType.protective)  # MINOR_APPROACH_PROTECTIVE_PROXIMITY_NEIGHBORS
			viApproachWeights.addWeight(1, MinorPlayerApproachType.conquest)  # MINOR_APPROACH_CONQUEST_PROXIMITY_NEIGHBORS
			viApproachWeights.addWeight(1, MinorPlayerApproachType.bully)  # antonjs: todo: constant / XML
		elif proximityValue == PlayerProximityType.close:  # PLAYER_PROXIMITY_CLOSE:
			viApproachWeights.addWeight(-1, MinorPlayerApproachType.ignore)  # MINOR_APPROACH_IGNORE_PROXIMITY_CLOSE
			viApproachWeights.addWeight(1, MinorPlayerApproachType.protective)  # MINOR_APPROACH_PROTECTIVE_PROXIMITY_CLOSE
			viApproachWeights.addWeight(-2, MinorPlayerApproachType.conquest)  # MINOR_APPROACH_CONQUEST_PROXIMITY_CLOSE
			viApproachWeights.addWeight(1, MinorPlayerApproachType.bully)  # antonjs: todo: constant / XML
		elif proximityValue == PlayerProximityType.far:  # PLAYER_PROXIMITY_FAR:
			viApproachWeights.addWeight(2, MinorPlayerApproachType.friendly)  # MINOR_APPROACH_FRIENDLY_PROXIMITY_FAR
			viApproachWeights.addWeight(-4, MinorPlayerApproachType.conquest)  # MINOR_APPROACH_CONQUEST_PROXIMITY_FAR
		elif proximityValue == PlayerProximityType.distant:  # PLAYER_PROXIMITY_DISTANT:
			viApproachWeights.addWeight(2, MinorPlayerApproachType.friendly)  # MINOR_APPROACH_FRIENDLY_PROXIMITY_DISTANT
			viApproachWeights.addWeight(-10, MinorPlayerApproachType.conquest)  # MINOR_APPROACH_CONQUEST_PROXIMITY_DISTANT
			viApproachWeights.addWeight(-2, MinorPlayerApproachType.bully)  # antonjs: todo: constant / XML

		# // // // // // // // // // // // // // // // // // //
		# MINOR PERSONALITY
		# // // // // // // // // // // // // // // // // // //

		personality: MinorPlayerPersonalityType = self.player.minorCivAI.personality()
		if personality == MinorPlayerPersonalityType.friendly:  # MINOR_CIV_PERSONALITY_FRIENDLY:
			viApproachWeights.addWeight(0, MinorPlayerApproachType.friendly)  # MINOR_APPROACH_FRIENDLY_PERSONALITY_FRIENDLY
			viApproachWeights.addWeight(0, MinorPlayerApproachType.protective)  # MINOR_APPROACH_PROTECTIVE_PERSONALITY_PROTECTIVE
		elif personality == MinorPlayerPersonalityType.neutral:  # MINOR_CIV_PERSONALITY_NEUTRAL:
			viApproachWeights.addWeight(0, MinorPlayerApproachType.friendly)  # MINOR_APPROACH_FRIENDLY_PERSONALITY_NEUTRAL
			viApproachWeights.addWeight(0, MinorPlayerApproachType.protective)  # MINOR_APPROACH_PROTECTIVE_PERSONALITY_NEUTRAL
		elif personality == MinorPlayerPersonalityType.hostile:  # MINOR_CIV_PERSONALITY_HOSTILE:
			viApproachWeights.addWeight(-1, MinorPlayerApproachType.friendly)  # MINOR_APPROACH_FRIENDLY_PERSONALITY_HOSTILE
			viApproachWeights.addWeight(-2, MinorPlayerApproachType.protective)  # MINOR_APPROACH_PROTECTIVE_PERSONALITY_HOSTILE
			viApproachWeights.addWeight(1, MinorPlayerApproachType.conquest)  # MINOR_APPROACH_CONQUEST_PERSONALITY_HOSTILE
			viApproachWeights.addWeight(1, MinorPlayerApproachType.bully)  # antonjs: todo: constant / XML
		elif personality == MinorPlayerPersonalityType.irrational:  # MINOR_CIV_PERSONALITY_IRRATIONAL:
			viApproachWeights.addWeight(0, MinorPlayerApproachType.friendly)  # MINOR_APPROACH_FRIENDLY_PERSONALITY_IRRATIONAL
			viApproachWeights.addWeight(0, MinorPlayerApproachType.protective)  # MINOR_APPROACH_PROTECTIVE_PERSONALITY_IRRATIONAL

		# // // // // // // // // // // // // // // // // // //
		# MINOR TRAIT
		# // // // // // // // // // // // // // // // // // //

		# Since Militaristic CS are harder to successfully bully
		if otherPlayer.cityState.category() == CityStateCategory.militaristic:  # MINOR_CIV_TRAIT_MILITARISTIC
			viApproachWeights.addWeight(-2, MinorPlayerApproachType.bully)  # antonjs: todo: XML

		# // // // // // // // // // // // // // // // // // //
		# TRIBUTE HISTORY - have we bullied this player before? If so, we are more likely to keep bullying
		# // // // // // // // // // // // // // // // // // //
		if otherPlayer.minorCivAI.isEverBulliedByMajor(self.player):
			viApproachWeights.addWeight(2, MinorPlayerApproachType.bully)  # antonjs: todo: constant / XML

		# // // // // // // // // // // // // // // // // // //
		# QUESTS - are there any active quests that might sway our decision?
		# // // // // // // // // // // // // // // // // // //
		if otherPlayer.minorCivAI.isActiveQuestFor(self.player, CityStateQuestType.pledgeToProtect):  # MINOR_CIV_QUEST_PLEDGE_TO_PROTECT
			viApproachWeights.addWeight(3, MinorPlayerApproachType.protective)  # antonjs: todo: constant / XML

		# Are we getting money from trade with them
		currentTradeValue = self.player.tradeRoutes.allTradeValueFromPlayer(otherPlayer, YieldType.gold, simulation)
		if currentTradeValue > 0:
			# todo: constant / XML
			viApproachWeights.addWeight(3, MinorPlayerApproachType.protective)
			viApproachWeights.addWeight(-3, MinorPlayerApproachType.bully)
			viApproachWeights.addWeight(5, MinorPlayerApproachType.friendly)
			viApproachWeights.addWeight(-5, MinorPlayerApproachType.conquest)

			# sanity check
			gpt = self.player.treasury.calculateGrossGold(simulation)
			deltaGPT = gpt - currentTradeValue
			if gpt >= 0 and deltaGPT < 0:
				viApproachWeights.addWeight(deltaGPT, MinorPlayerApproachType.conquest)

		# // // // // // // // // // // // // // // // // // //
		# TARGET VALUE - can we conquer these guys?
		# // // // // // // // // // // // // // // // // // //

		targetValue: PlayerTargetValueType = self.targetValueOf(otherPlayer)
		# if (self.player.GetPlayerTraits()->GetCityStateCombatModifier() > 0)
		#	iPTV + +
		#	iPTV = iPTV > TARGET_VALUE_SOFT ? TARGET_VALUE_SOFT: iPTV

		if targetValue == PlayerTargetValueType.impossible:  # TARGET_VALUE_IMPOSSIBLE
			viApproachWeights.mulWeight(10, MinorPlayerApproachType.conquest)  # MINOR_APPROACH_WAR_TARGET_IMPOSSIBLE
			viApproachWeights.divWeight(100, MinorPlayerApproachType.conquest)
		elif targetValue == PlayerTargetValueType.bad:  # TARGET_VALUE_BAD
			viApproachWeights.mulWeight(20, MinorPlayerApproachType.conquest)  # MINOR_APPROACH_WAR_TARGET_BAD
			viApproachWeights.divWeight(100, MinorPlayerApproachType.conquest)
		elif targetValue == PlayerTargetValueType.average:  # TARGET_VALUE_AVERAGE
			viApproachWeights.mulWeight(40, MinorPlayerApproachType.conquest)  # MINOR_APPROACH_WAR_TARGET_AVERAGE
			viApproachWeights.divWeight(100, MinorPlayerApproachType.conquest)
		elif targetValue == PlayerTargetValueType.favorable:  # TARGET_VALUE_FAVORABLE
			viApproachWeights.mulWeight(110, MinorPlayerApproachType.conquest)  # MINOR_APPROACH_WAR_TARGET_FAVORABLE
			viApproachWeights.divWeight(100, MinorPlayerApproachType.conquest)
		elif targetValue == PlayerTargetValueType.soft:  # TARGET_VALUE_SOFT
			viApproachWeights.mulWeight(130, MinorPlayerApproachType.conquest)  # MINOR_APPROACH_WAR_TARGET_SOFT
			viApproachWeights.divWeight(100, MinorPlayerApproachType.conquest)

		# // // // // // // // // // // // // // // // // // // //
		# WAR PROJECTION - how do we think a war against otherPlayer will go?
		# // // // // // // // // // // // // // // // // // // //

		# switch(GetWarProjection(otherPlayer))
		# WAR_PROJECTION_DESTRUCTION:
		# viApproachWeights[MAJOR_CIV_APPROACH_WAR] *= 25  # MINOR_APPROACH_WAR_PROJECTION_DESTRUCTION_PERCENT
		# viApproachWeights[MAJOR_CIV_APPROACH_WAR] /= 100
		# WAR_PROJECTION_DEFEAT:
		# viApproachWeights[MAJOR_CIV_APPROACH_WAR] *= 40  # MINOR_APPROACH_WAR_PROJECTION_DEFEAT_PERCENT
		# viApproachWeights[MAJOR_CIV_APPROACH_WAR] /= 100
		# WAR_PROJECTION_STALEMATE:
		# viApproachWeights[MAJOR_CIV_APPROACH_WAR] *= 60  # MINOR_APPROACH_WAR_PROJECTION_STALEMATE_PERCENT
		# viApproachWeights[MAJOR_CIV_APPROACH_WAR] /= 100
		# WAR_PROJECTION_UNKNOWN:
		# viApproachWeights[MAJOR_CIV_APPROACH_WAR] *= 70  # MINOR_APPROACH_WAR_PROJECTION_UNKNOWN_PERCENT
		# viApproachWeights[MAJOR_CIV_APPROACH_WAR] /= 100
		# WAR_PROJECTION_GOOD:
		# viApproachWeights[MAJOR_CIV_APPROACH_WAR] *= 100  # MINOR_APPROACH_WAR_PROJECTION_GOOD_PERCENT
		# viApproachWeights[MAJOR_CIV_APPROACH_WAR] /= 100
		# WAR_PROJECTION_VERY_GOOD:
		# viApproachWeights[MAJOR_CIV_APPROACH_WAR] *= 110  # MINOR_APPROACH_WAR_PROJECTION_VERY_GOOD_PERCENT
		# viApproachWeights[MAJOR_CIV_APPROACH_WAR] /= 100

		# // // // // // // // // // // // // // // // // // //
		# PEACE TREATY - have we made peace with this player before?  If so, reduce war weight
		# // // // // // // // // // // // // // // // // // //

		peaceTreatyTurn = self.player.diplomacyAI.turnMadePeaceTreatyWith(otherPlayer)
		if peaceTreatyTurn > -1:
			turnsSincePeace = simulation.currentTurn - peaceTreatyTurn
			if turnsSincePeace < 25:  # TURNS_SINCE_PEACE_WEIGHT_DAMPENER
				viApproachWeights.mulWeight(65, MinorPlayerApproachType.conquest)  # APPROACH_WAR_HAS_MADE_PEACE_BEFORE_PERCENT
				viApproachWeights.divWeight(100, MinorPlayerApproachType.conquest)

		# // // // // // // // // // // // // // // // // // //
		# DEBUGGING
		# // // // // // // // // // // // // // // // // // //
		# if (BULLY_DEBUGGING)
		# 	viApproachWeights.addWeight(50, MinorPlayerApproachType.conquest)
		# 	viApproachWeights.addWeight(0, MinorPlayerApproachType.bully)
		# 	viApproachWeights.addWeight(0, MinorPlayerApproachType.protective)

		# // // // // // // // // // // // // // // // // // //
		# RANDOM FACTOR
		# // // // // // // // // // // // // // // // // // //

		for loopApproach in MinorPlayerApproachType.all():
			# Increase weights to hundreds to give us more fidelity
			viApproachWeights.mulWeight(100, loopApproach)

			randAmount = viApproachWeights.weight(loopApproach) * 15 # APPROACH_RANDOM_PERCENT

			# If the amount is negative, only bad things can happen.Plus, it's not likely we're going to pick this anyways
			if randAmount > 0:
				randAmount /= 100
				randValue = 0 if Tests.are_running else random.randint(0, int(randAmount))
				viApproachWeights.addWeight(randValue, loopApproach)

		# // // // // // // // // // // // // // // // // // //
		# CAN WE PLEDGE TO PROTECT?
		# // // // // // // // // // // // // // // // // // //
		if not otherPlayer.minorCivAI.canMajorProtect(self.player):
			# Disfavor protective if we can't actually pledge protection!
			if viApproachWeights.weight(MinorPlayerApproachType.protective) > 0:
				viApproachWeights.setWeight(0, MinorPlayerApproachType.protective)

		# // // // // // // // // // // // // // // // // // //
		# CAN WE DECLARE WAR?
		# // // // // // // // // // // // // // // // // // //
		if not self.player.canDeclareWarTowards(otherPlayer):
			if not self.player.isAtWarWith(otherPlayer):
				# Disfavor conquest if we can't even do war with them!
				if viApproachWeights.weight(MinorPlayerApproachType.conquest) > 0:
					viApproachWeights.setWeight(0, MinorPlayerApproachType.conquest)

		# // // // // // // // // // // // // // // // // //
		# ALLIES WITH MINOR?
		# // // // // // // // // // // // // // // // // //
		if otherPlayer.minorCivAI.isAllyOf(self.player):
			# Disfavor conquest and bullying if they are our ally
			if viApproachWeights.weight(MinorPlayerApproachType.conquest) > 0:
				viApproachWeights.setWeight(0, MinorPlayerApproachType.conquest)

			if viApproachWeights.weight(MinorPlayerApproachType.bully) > 0:
				viApproachWeights.setWeight(0, MinorPlayerApproachType.bully)

		# This vector is what we'll use to sort
		vApproachWeightsForSorting = WeightedBaseList()

		# Transfer values from our normal int vector (which we need for logging) to the Weighted Vector we can sort
		for loopApproach in MinorPlayerApproachType.all():
			vApproachWeightsForSorting.setWeight(viApproachWeights.weight(loopApproach), loopApproach)

		vApproachWeightsForSorting.sortByValue(reverse=True)

		approach = firstOrNone(vApproachWeightsForSorting.keys())
		highestWeight = firstOrNone(vApproachWeightsForSorting.values())

		# Don't want to log if we're just seeing what the highest weight is and don't care about what Approach we like
		if log:
			self.logMinorCivApproachUpdate(otherPlayer, viApproachWeights, approach, oldApproach, simulation)

		return highestWeight, approach

	def updateMinorCivApproachTowards(self, otherPlayer, approach: MinorPlayerApproachType):
		self.playerDict.updateMinorCivApproachTowards(otherPlayer, approach)

	def isValidUIDiplomacyTarget(self, otherPlayer) -> bool:
		return True

	def personalityMinorCivApproachBias(self, approach: MinorPlayerApproachType) -> int:
		"""What is our bias towards a particular Minor Civ Approach?"""
		return self._paiPersonalityMinorCivApproachBiases.weight(approach)

	def isGoingForWorldConquest(self) -> bool:
		"""Does this player want to conquer the world?"""
		return self.player.grandStrategyAI.activeStrategy == GrandStrategyAIType.conquest

	def isGoingForDiploVictory(self) -> bool:
		"""Does this player want to win by diplo?"""
		return self.player.grandStrategyAI.activeStrategy == GrandStrategyAIType.council

	def isGoingForCultureVictory(self) -> bool:
		"""Does this player want to win by diplo?"""
		return self.player.grandStrategyAI.activeStrategy == GrandStrategyAIType.culture

	def turnMadePeaceTreatyWith(self, otherPlayer) -> int:
		return self.playerDict.turnMadePeaceTreatyWith(otherPlayer)

	def logMinorCivApproachUpdate(self, otherPlayer, viApproachWeights: WeightedBaseList, approach: MinorPlayerApproachType, oldApproach: MinorPlayerApproachType, simulation):
		"""Log Minor Civ Approach Update"""
		if not self.player.isCityState():
			return

		if approach == oldApproach:
			return

		logging.debug(f'approach of {self.player} to minor {otherPlayer} changed from {oldApproach} to {approach}')

	def isRecklessExpanderTowards(self, otherPlayer, simulation):
		"""IsPlayerRecklessExpander - Is otherPlayer expanding recklessly?"""
		# If the player is too far away from us, we don't care
		if self.player.proximityTo(otherPlayer) < PlayerProximityType.close:
			return False

		# If the player has too few cities, don't worry about it
		numberOfCities = otherPlayer.numberOfCities(simulation)
		if numberOfCities < 4:
			return False

		fAverageNumCities = 0
		iNumPlayers = 0

		# Find out what the average is (minus the player we're looking at)
		for loopPlayer in simulation.players:
			# Not alive
			if not loopPlayer.isAlive():
				continue

			# Not the guy we're looking at
			if loopPlayer == otherPlayer:
				continue

			iNumPlayers += 1
			fAverageNumCities += loopPlayer.numberOfCities(simulation)

		# Not sure how this would happen, but we'll be safe anyways since we'll be dividing by this value
		if iNumPlayers == 0:
			raise Exception("0 players to evaluate when trying to identify if someone is a reckless expander. Not sure how this would happen without the game being over yet.")

		fAverageNumCities /= iNumPlayers

		# Must have way more cities than the average player in the game
		if numberOfCities < fAverageNumCities * 1.5:
			return False

		# If this guy's military is as big as ours, then it probably means he's just stronger than us
		if self.playerDict.militaryStrengthComparedToUsOf(otherPlayer) >= StrengthType.average:
			return False

		return True

	def doContactMinorCivs(self, simulation):
		"""Anyone we want to chat with?"""
		iDiplomacyFlavor: int = self.player.grandStrategyAI.personalityAndGrandStrategy(FlavorType.diplomacy)
		iGoldFlavor: int = self.player.grandStrategyAI.personalityAndGrandStrategy(FlavorType.gold)
		iTileImprovementFlavor: int = self.player.grandStrategyAI.personalityAndGrandStrategy(FlavorType.tileImprovement)
		iExpansionFlavor: int = self.player.grandStrategyAI.personalityAndGrandStrategy(FlavorType.expansion)

		bFoundCity: bool = self.player.economicAI.isUsingStrategy(EconomicStrategyType.foundCity)  # ECONOMICAISTRATEGY_FOUND_CITY
		bExpandLikeCrazy: bool = self.player.economicAI.isUsingStrategy(EconomicStrategyType.expandLikeCrazy)  # ECONOMICAISTRATEGY_EXPAND_LIKE_CRAZY
		bExpandToOtherContinents: bool = self.player.economicAI.isUsingStrategy(EconomicStrategyType.expandToOtherContinents)  # ECONOMICAISTRATEGY_EXPAND_TO_OTHER_CONTINENTS
		bNeedHappiness: bool = self.player.economicAI.isUsingStrategy(EconomicStrategyType.needHappiness)  # ECONOMICAISTRATEGY_NEED_HAPPINESS
		bNeedHappinessCritical: bool = self.player.economicAI.isUsingStrategy(EconomicStrategyType.needHappinessCritical)  # ECONOMICAISTRATEGY_NEED_HAPPINESS_CRITICAL
		bLosingMoney: bool = self.player.economicAI.isUsingStrategy(EconomicStrategyType.losingMoney)  # ECONOMICAISTRATEGY_LOSING_MONEY

		# **************************
		# Would we like to buyout a minor this turn?  (Austria UA)
		# **************************
		bWantsToBuyout: bool = False

		# 	if(GetPlayer()->IsAbleToAnnexCityStates()
		# 		if(bFoundCity or bExpandLikeCrazy or bExpandToOtherContinents ||
		# 		        GetStateAllWars() == STATE_ALL_WARS_LOSING ||
		# 		        IsGoingForWorldConquest() ||
		# 		        self.player.treasury.calculateGrossGold(simulation) > 100)
		# 		{
		# 			bWantsToBuyout = true
		# 		}
		# 		else
		# 		{
		# 			int iThreshold = iExpansionFlavor * 5 //antonjs: todo: xml
		# 			int iRandRoll = GC.getGame().getJonRandNum(100, "Diplomacy AI: good turn to buyout a minor?")
		#
		# 			if(iRandRoll < iThreshold)
		# 				bWantsToBuyout = true
		# 		}
		# 	}

		# **************************
		# Would we like to give a gold gift this turn?
		# **************************
		bWantsToMakeGoldGift: bool = False

		# If we're a highly diplomatic leader, then always look for an opportunity
		minorCivAlwaysGiftThreshold: int = 4  # MC_ALWAYS_GIFT_DIPLO_THRESHOLD
		if iDiplomacyFlavor >= minorCivAlwaysGiftThreshold or \
			self.isGoingForDiploVictory() or \
			self.isGoingForCultureVictory() or \
			self.player.economicAI.isSavingForPurchase(PurchaseType.minorCivGift) or \
			self.player.hasActiveGoldQuest(simulation) or \
			self.player.treasury.calculateGrossGold(simulation) > 100:  # if we are very wealthy always do this
			bWantsToMakeGoldGift = True
		else:
			# Otherwise, do a random roll
			iThreshold: int = iDiplomacyFlavor * 5  # MC_SOMETIMES_GIFT_RAND_MULTIPLIER
			iRandRoll = 0 if Tests.are_running else random.randint(0, 100)  # Diplomacy AI: good turn to make a gold gift to a minor?

			# Threshold will be 15 for a player (3 flavor * 5)
			# Threshold will be 5 for non - diplomatic player (2 flavor * 5)

			if iRandRoll < iThreshold:
				bWantsToMakeGoldGift = True

		# **************************
		# Would we like to get a unit by bullying this turn?
		# **************************
		bWantsToBullyUnit: bool = False

		if self.player.economicAI.buildersToCitiesRatio(simulation) < 0.25 and \
			self.player.economicAI.improvedToImprovablePlotsRatio(simulation) < 0.50:
			bWantsToBullyUnit = True
		else:
			# Otherwise, do a random roll
			iThreshold = iTileImprovementFlavor * 3
			iRandRoll = 0 if Tests.are_running else random.randint(0, 100)  # Diplomacy AI: good turn to bully a unit (worker) from a minor?

			if iRandRoll < iThreshold:
				bWantsToBullyUnit = True
			# antonjs: todo: if too many workers then set to False (ex. want to disband workers you have)

		# **************************
		# Would we like to get some gold by bullying this turn?
		# **************************
		bWantsToBullyGold: bool = False
		minorCivBullyGoldThreshold: int = 4  # MC_ALWAYS_BULLY_GOLD_THRESHOLD

		if iGoldFlavor >= minorCivBullyGoldThreshold or \
			self.isGoingForWorldConquest() or \
			self.player.economicAI.isSavingForPurchase(PurchaseType.unit) or \
			self.player.economicAI.isSavingForPurchase(PurchaseType.building) or \
			bLosingMoney or \
			self.player.treasury.calculateGrossGold(simulation) < 0:  # if we are losing gold per turn
			bWantsToBullyGold = True
		else:
			# Otherwise, do a random roll
			iThreshold = iGoldFlavor * 4  # antonjs: todo: XML
			iRandRoll = 0 if Tests.are_running else random.randint(0, 100)  # Diplomacy AI: good turn to bully gold from a minor?

			if iRandRoll < iThreshold:
				bWantsToBullyGold = True

		# 	CvWeightedVector<PlayerTypes, MAX_PLAYERS, true> veMinorsToBuyout // Austria UA
		# 	CvWeightedVector<MinorGoldGiftInfo, MAX_PLAYERS, true> veMinorsToGiveGold
		# 	CvWeightedVector<PlayerTypes, MAX_PLAYERS, true> veMinorsToBullyGold
		# 	CvWeightedVector<PlayerTypes, MAX_PLAYERS, true> veMinorsToBullyUnit
		#
		# 	int iLargeGift = 1000  # MINOR_GOLD_GIFT_LARGE()
		# 	int iMediumGift = 500  # MINOR_GOLD_GIFT_MEDIUM()
		# 	int iSmallGift = 250  # MINOR_GOLD_GIFT_SMALL()
		# 	int iLargeGiftFriendship
		# 	int iMediumGiftFriendship
		# 	int iSmallGiftFriendship
		# 	bool bMediumGiftAllies
		# 	bool bSmallGiftAllies
		#
		# 	PlayerTypes eID = GetPlayer()->GetID()
		#
		# 	CvMinorCivInfo* pMinorInfo
		# 	CvPlayer* pMinor
		# 	CvMinorCivAI* pMinorCivAI
		#
		# 	bool bIntruding
		#
		# 	int iOtherMajorLoop
		# 	PlayerTypes eOtherMajor
		# 	int iFriendshipWithMinor
		# 	int iOtherPlayerFriendshipWithMinor
		#
		# 	bool bWantsToConnect
		#
		# 	MinorCivApproachTypes eApproach
		#
		# 	iGrowthFlavor = self.player.grandStrategyAI.personalityAndGrandStrategy(FlavorType.growth)
		#
		# 	// Loop through all (known) Minors
		# 	PlayerTypes eMinor
		# 	TeamTypes eMinorTeam
		# 	for(int iMinorLoop = MAX_MAJOR_CIVS iMinorLoop < MAX_CIV_PLAYERS iMinorLoop++
		# 		eMinor = (PlayerTypes) iMinorLoop
		#
		# 		pMinor = &GET_PLAYER(eMinor)
		# 		pMinorCivAI = pMinor->GetMinorCivAI()
		# 		eMinorTeam = pMinor->getTeam()
		#
		# 		bWantsToConnect = False
		# 		bool bWantsToGiveGoldToThisMinor = False
		# 		bool bWantsToBullyUnitFromThisMinor = False
		# 		bool bWantsToBullyGoldFromThisMinor = False
		# 		bool bWantsToBuyoutThisMinor = False
		#
		# 		if(IsPlayerValid(eMinor))
		# 		{
		# 			# Can't do anything with minors we're at war with, besides make peace (which isn't done here, but in DoMakePeaceWithMinors())
		# 			if(IsAtWar(eMinor))
		# 				continue
		#
		# 			eApproach = GetMinorCivApproach(eMinor)
		#
		# 			# Do we want to change our protection of this minor?
		# 			DoUpdateMinorCivProtection(eMinor, eApproach)
		#
		# 			# Do we want to connect to this player?
		# 			if(pMinorCivAI->IsActiveQuestForPlayer(eID, MINOR_CIV_QUEST_ROUTE))
		# 			{
		# 				if(eApproach == MINOR_CIV_APPROACH_PROTECTIVE ||
		# 				        eApproach == MINOR_CIV_APPROACH_FRIENDLY)
		# 				{
		# 					if(GetPlayer()->GetProximityToPlayer(eMinor) == PLAYER_PROXIMITY_NEIGHBORS)
		# 						bWantsToConnect = true
		# 				}
		# 			}
		#
		# 			bIntruding = true
		#
		# 			# We have open borders so we're definitely not intruding
		# 			if(pMinorCivAI->IsPlayerHasOpenBorders(eID))
		# 				bIntruding = False
		#
		# 			else
		# 			{
		# 				# Cares and doesn't yet have enough friendship for Open Borders
		# 				if(eApproach == MINOR_CIV_APPROACH_PROTECTIVE or eApproach == MINOR_CIV_APPROACH_FRIENDLY)
		# 					bIntruding = False
		# 			}
		#
		# 			pMinorCivAI->SetMajorIntruding(eID, bIntruding)
		#
		# 			# Calculate desirability to buyout this minor
		# 			if(bWantsToBuyout)
		# 			{
		# 				int iValue = 100 # antonjs: todo: xml
		# 				# Only bother if we actually can buyout
		# 				CvCity* pMinorCapital = pMinor->getCapitalCity()
		# 				if(GetPlayer()->IsAbleToAnnexCityStates() and pMinorCivAI->CanMajorBuyout(eID) and pMinorCapital != NULL)
		# 				{
		# 					# Determine presence of player cities on this continent
		# 					int iMinorArea = pMinorCapital->getArea()
		# 					CvArea* pMinorArea = GC.getMap().getArea(iMinorArea)
		# 					bool bPresenceInArea = False
		# 					int iMajorCapitalsInArea = 0
		# 					if(pMinorArea)
		# 					{
		# 						// Do we have a city here?
		# 						if(pMinorArea->getCitiesPerPlayer(eID) > 0)
		# 							bPresenceInArea = true
		#
		# 						// Does another major civ have their capital here? (must be visible)
		# 						for(int iMajorRivalLoop = 0 iMajorRivalLoop < MAX_MAJOR_CIVS iMajorRivalLoop++)
		# 						{
		# 							PlayerTypes eMajorRivalLoop = (PlayerTypes) iMajorRivalLoop
		# 							if(eMajorRivalLoop == eID)
		# 								continue
		#
		# 							if(GET_PLAYER(eMajorRivalLoop).isAlive())
		# 							{
		# 								CvCity* pCapital = GET_PLAYER(eMajorRivalLoop).getCapitalCity()
		# 								if(pCapital and pCapital->plot())
		# 								{
		# 									CvPlot* pPlot = pCapital->plot()
		# 									if(pPlot->isVisible(GetPlayer()->getTeam()))
		# 										iMajorCapitalsInArea++
		# 								}
		# 							}
		# 						}
		# 					}
		# 					else
		# 					{
		# 						CvAssertMsg(False, "Could not lookup minor civ's area! Please send Anton your save file and version.")
		# 					}
		#
		# 					# How many units does the city-state have?
		# 					int iMinorMilitaryUnits = 0
		# 					int iMinorUnits = 0
		# 					CvUnit* pLoopUnit
		# 					int iLoop
		# 					for(pLoopUnit = pMinor->firstUnit(&iLoop) pLoopUnit != NULL pLoopUnit = pMinor->nextUnit(&iLoop))
		# 					{
		# 						if(pLoopUnit->IsCanAttack() and pLoopUnit->AI_getUnitAIType() != UNITAI_EXPLORE and pLoopUnit->AI_getUnitAIType() != UNITAI_EXPLORE_SEA)
		# 						{
		# 							iMinorMilitaryUnits++
		# 						}
		# 						iMinorUnits++
		# 					}
		#
		# 					// Foreign continent
		# 					if(!bPresenceInArea)
		# 					{
		# 						// Military foothold to attack other majors
		# 						if(IsGoingForWorldConquest() and iMajorCapitalsInArea > 0)
		# 						{
		# 							iValue += 100 //antonjs: todo: xml
		# 						}
		# 						// Expansion
		# 						elif(bExpandToOtherContinents)
		# 						{
		# 							iValue += 60 //antonjs: todo: xml
		# 						}
		# 						else
		# 						{
		# 							iValue += -50 //antonjs: todo: xml
		# 						}
		# 					}
		# 					// Continent we have presence on
		# 					else
		# 					{
		# 						// Proximity plays a large factor, since we don't want a remote, isolated city
		# 						if(GetPlayer()->GetProximityToPlayer(eMinor) == PLAYER_PROXIMITY_NEIGHBORS)
		# 						{
		# 							iValue += 100 //antonjs: todo: xml
		# 							// Military units could come to our rescue quickly
		# 							if(GetStateAllWars() == STATE_ALL_WARS_LOSING)
		# 							{
		# 								if(iMinorMilitaryUnits > 0)  //antonjs: todo: xml
		# 								{
		# 									iValue += (iMinorMilitaryUnits) * 10 //antonjs: todo: xml
		# 								}
		# 								else
		# 								{
		# 									iValue -= 50 //antonjs: todo: xml
		# 								}
		# 							}
		# 						}
		# 						elif(GetPlayer()->GetProximityToPlayer(eMinor) == PLAYER_PROXIMITY_CLOSE)
		# 						{
		# 							iValue += 10 //antonjs: todo: xml
		# 						}
		# 						elif(GetPlayer()->GetProximityToPlayer(eMinor) == PLAYER_PROXIMITY_FAR)
		# 						{
		# 							iValue += -50 //antonjs: todo: xml
		# 						}
		# 						elif(GetPlayer()->GetProximityToPlayer(eMinor) == PLAYER_PROXIMITY_DISTANT)
		# 						{
		# 							iValue += -100 //antonjs: todo: xml
		# 						}
		# 					}
		#
		# 					// Military units - How many, and can we support them?
		# 					if(GetPlayer()->GetNumUnitsSupplied() >= GetPlayer()->getNumUnits() + iMinorUnits)
		# 					{
		# 						iValue += (iMinorMilitaryUnits) * 5
		# 					}
		#
		# 					// Happiness
		# 					if(bNeedHappiness)
		# 						iValue += -50 //antonjs: todo: xml
		# 					if(bNeedHappinessCritical)
		# 						iValue += -150 //antonjs: todo: xml
		#
		# 					// Potential bonuses lost
		# 					MinorCivTraitTypes eTrait = pMinorCivAI->GetTrait()
		# 					if(eTrait == MINOR_CIV_TRAIT_CULTURED and IsGoingForCultureVictory())
		# 					{
		# 						iValue += -70 //antonjs: todo: xml
		# 					}
		# 					elif(eTrait == MINOR_CIV_TRAIT_MERCANTILE)
		# 					{
		# 						if(bNeedHappiness)
		# 							iValue += -100 //antonjs: todo: xml
		# 						if(bNeedHappinessCritical)
		# 							iValue += -150 //antonjs: todo: xml
		# 					}
		#
		# 					// Time to decide - Do we want it enough?
		# 					if(iValue > 100)  //antonjs: todo: xml
		# 					{
		# 						veMinorsToBuyout.push_back(eMinor, iValue)
		# 						bWantsToBuyoutThisMinor = true
		# 					}
		# 				}
		# 			}
		#
		# 			// Calculate desirability to give this minor gold
		# 			if(bWantsToMakeGoldGift and !bWantsToBuyoutThisMinor)
		# 			{
		# 				int iValue = 100  # MC_GIFT_WEIGHT_THRESHOLD()
		# 				// If we're not protective or friendly, then don't bother with minor diplo
		# 				if(eApproach == MINOR_CIV_APPROACH_PROTECTIVE or eApproach == MINOR_CIV_APPROACH_FRIENDLY)
		# 				{
		# 					MinorGoldGiftInfo sGiftInfo
		# 					sGiftInfo.eMinor = eMinor
		# 					sGiftInfo.eMajorRival = NO_PLAYER
		# 					sGiftInfo.bQuickBoost = False
		# 					sGiftInfo.iGoldAmount = 0
		#
		# 					// if we are rich we are more likely to, conversely if we are poor...
		# 					iValue += min(max(0, self.player.treasury.calculateGrossGold(simulation) - 50),100)
		#
		# 					pMinorInfo = GC.getMinorCivInfo(pMinorCivAI->GetMinorCivType())
		#
		# 					// Diplo victory makes us more likely to spend gold
		# 					if(IsGoingForDiploVictory())
		# 						iValue += 100  # MC_GIFT_WEIGHT_DIPLO_VICTORY()
		# 					// double up if this is the home stretch
		# 					if(GC.getGame().IsUnitedNationsActive())
		# 					{
		# 						iValue += 100  # MC_GIFT_WEIGHT_DIPLO_VICTORY()
		# 					}
		# 					// Going for Culture victory, focus on Cultural city states
		# 					elif(IsGoingForCultureVictory())
		# 					{
		# 						if(pMinorInfo->GetMinorCivTrait() == MINOR_CIV_TRAIT_CULTURED)
		# 							iValue += 100  # MC_GIFT_WEIGHT_CULTURE_VICTORY()
		# 					}
		# 					// Going for Conquest victory, focus on Militaristic city states
		# 					elif(IsGoingForWorldConquest())
		# 					{
		# 						if(pMinorInfo->GetMinorCivTrait() == MINOR_CIV_TRAIT_MILITARISTIC)
		# 							iValue += 100  # MC_GIFT_WEIGHT_CONQUEST_VICTORY()
		# 					}
		#
		# 					//antonjs: todo: work extra gold quest INF potential into the friends/allies/passing logic as well
		# 					// Gold gift quest is active, so we would get more bang for our bucks
		# 					if(pMinorCivAI->IsActiveQuestForPlayer(eID, MINOR_CIV_QUEST_GIVE_GOLD))
		# 					{
		# 						iValue += 150 //antonjs: todo: constant/XML
		# 					}
		#
		# 					// Invest quest is active, so we would get more bang for our bucks
		# 					if(pMinorCivAI->IsActiveQuestForPlayer(eID, MINOR_CIV_QUEST_INVEST))
		# 					{
		# 						iValue += 100 //antonjs: todo: constant/XML
		# 					}
		#
		# 					// having traits that give us bonuses also make us want to spend gold
		# 					if(m_pPlayer->GetPlayerTraits()->GetCityStateFriendshipModifier() > 0 or m_pPlayer->GetPlayerTraits()->GetCityStateBonusModifier())
		# 					{
		# 						iValue += 100  # MC_GIFT_WEIGHT_DIPLO_VICTORY()
		# 					}
		#
		# 					// Nearly everyone likes to grow
		# 					if(pMinorInfo->GetMinorCivTrait() == MINOR_CIV_TRAIT_MARITIME and !GetPlayer()->IsEmpireUnhappy())
		# 					{
		# 						iValue += 20  # MC_GIFT_WEIGHT_MARITIME_GROWTH() * iGrowthFlavor * max(1, GetPlayer()->getNumCities() / 3)
		# 					}
		#
		# 					// Slight negative weight towards militaristic
		# 					if(pMinorInfo->GetMinorCivTrait() == MINOR_CIV_TRAIT_MILITARISTIC and !IsGoingForWorldConquest())
		# 						iValue += -50  # MC_GIFT_WEIGHT_MILITARISTIC()
		#
		# 					// If they have a resource we don't have, add extra weight
		# 					int iResourcesWeLack = pMinorCivAI->GetNumResourcesMajorLacks(eID)
		# 					if(iResourcesWeLack > 0)
		# 						iValue += (iResourcesWeLack* /*80  # MC_GIFT_WEIGHT_RESOURCE_WE_NEED())
		#
		# 					// If we're protective this is worth more than if we're friendly
		# 					if(eApproach == MINOR_CIV_APPROACH_PROTECTIVE)
		# 						iValue += 10  # MC_GIFT_WEIGHT_PROTECTIVE()
		#
		# 					// If the minor is hostile, then reduce the weighting
		# 					if(pMinorCivAI->GetPersonality() == MINOR_CIV_PERSONALITY_HOSTILE)
		# 						iValue += -20  # MC_GIFT_WEIGHT_HOSTILE()
		#
		# 					// The closer we are the better
		# 					if(GetPlayer()->GetProximityToPlayer(eMinor) == PLAYER_PROXIMITY_NEIGHBORS)
		# 						iValue += 5  # MC_GIFT_WEIGHT_NEIGHBORS()
		# 					elif(GetPlayer()->GetProximityToPlayer(eMinor) == PLAYER_PROXIMITY_CLOSE)
		# 						iValue += 4  # MC_GIFT_WEIGHT_CLOSE()
		# 					elif(GetPlayer()->GetProximityToPlayer(eMinor) == PLAYER_PROXIMITY_FAR)
		# 						iValue += 3  # MC_GIFT_WEIGHT_FAR()
		#
		# 					iLargeGiftFriendship = pMinorCivAI->GetFriendshipFromGoldGift(eID, iLargeGift)
		# 					iMediumGiftFriendship = pMinorCivAI->GetFriendshipFromGoldGift(eID, iMediumGift)
		# 					iSmallGiftFriendship = pMinorCivAI->GetFriendshipFromGoldGift(eID, iSmallGift)
		#
		# 					iFriendshipWithMinor = pMinorCivAI->GetEffectiveFriendshipWithMajor(eID)
		#
		# 					// Loop through other players to see if we can pass them
		# 					for(iOtherMajorLoop = 0 iOtherMajorLoop < MAX_MAJOR_CIVS iOtherMajorLoop++)
		# 					{
		# 						eOtherMajor = (PlayerTypes) iOtherMajorLoop
		#
		# 						// Player must be alive
		# 						if(!GET_PLAYER(eOtherMajor).isAlive())
		# 							continue
		#
		# 						iOtherPlayerFriendshipWithMinor = pMinorCivAI->GetEffectiveFriendshipWithMajor(eOtherMajor)
		#
		# 						// Player must have friendship with this major
		# 						if(iOtherPlayerFriendshipWithMinor <= 0)
		# 							continue
		#
		# 						// They must have more friendship with this guy than us
		# 						if(iFriendshipWithMinor <= iOtherPlayerFriendshipWithMinor)
		# 							continue
		#
		# 						// Only care if we'll actually be Allies or better
		# 						bMediumGiftAllies = iFriendshipWithMinor + iMediumGiftFriendship >= pMinorCivAI->GetAlliesThreshold()
		# 						bSmallGiftAllies = iFriendshipWithMinor + iSmallGiftFriendship >= pMinorCivAI->GetAlliesThreshold()
		#
		# 						// If we can pass them with a small gift, great
		# 						if(bSmallGiftAllies and iOtherPlayerFriendshipWithMinor - iFriendshipWithMinor < iSmallGiftFriendship)
		# 						{
		# 							iValue += 15  # MC_SMALL_GIFT_WEIGHT_PASS_OTHER_PLAYER()
		# 							sGiftInfo.bQuickBoost = true
		# 							sGiftInfo.eMajorRival = eOtherMajor
		# 						}
		# 						// If a medium gift passes them up, that's good too
		# 						elif(bMediumGiftAllies and iOtherPlayerFriendshipWithMinor - iFriendshipWithMinor < iMediumGiftFriendship)
		# 						{
		# 							iValue += 10  # MC_GIFT_WEIGHT_PASS_OTHER_PLAYER()
		# 							sGiftInfo.eMajorRival = eOtherMajor
		# 						}
		# 						// We're behind and we can't catch up right now, so zero-out the value
		# 						else
		# 							iValue = 0
		# 					}
		#
		# 					// Are we already allies?
		# 					if(pMinorCivAI->IsAllies(eID))
		# 					{
		# 						// Are we close to losing our status?
		# 						if(pMinorCivAI->IsCloseToNotBeingAllies(eID))
		# 						{
		# 							iValue += 150  # MC_GIFT_WEIGHT_ALMOST_NOT_ALLIES()
		# 							sGiftInfo.bQuickBoost = true
		# 						}
		# 						// Not going to lose status, so not worth going after this guy
		# 						else
		# 							iValue = 0
		# 					}
		# 					// Are we already Friends?
		# 					elif(pMinorCivAI->IsFriends(eID))
		# 					{
		# 						// Are we close to losing our status?
		# 						if(pMinorCivAI->IsCloseToNotBeingFriends(eID))
		# 						{
		# 							iValue += 125  # MC_GIFT_WEIGHT_ALMOST_NOT_FRIENDS()
		# 							sGiftInfo.bQuickBoost = true
		# 						}
		# 						// Not going to lose status, so not worth going after this guy
		# 						elif(!IsGoingForDiploVictory() or !GC.getGame().IsUnitedNationsActive())
		# 							iValue = 0
		# 					}
		#
		# 					// Did we bully you recently?  If so, giving you gold now would be very odd.
		# 					if(pMinorCivAI->IsRecentlyBulliedByMajor(eID))
		# 					{
		# 						iValue -= 100 //antonjs: todo: constant/XML
		# 					}
		#
		# 					//antonjs: consider: different behavior to CS that have been bullied by others, bullied by rival, etc.
		#
		# 					// Do we want it enough?
		# 					if(iValue > GC.getMC_GIFT_WEIGHT_THRESHOLD())
		# 					{
		# 						veMinorsToGiveGold.push_back(sGiftInfo, iValue)
		# 						bWantsToGiveGoldToThisMinor = true
		# 					}
		# 				}
		# 			}
		#
		# 			// Calculate desirability to bully a unit from this minor
		# 			if(bWantsToBullyUnit and !bWantsToBuyoutThisMinor and !bWantsToGiveGoldToThisMinor)  //antonjs: todo: xml
		# 			{
		# 				int iValue = 100 //antonjs: todo: XML, bully threshold
		# 				if(eApproach == MINOR_CIV_APPROACH_BULLY)
		# 				{
		# 					// Only bother if we can successfully bully
		# 					if(pMinor->GetMinorCivAI()->CanMajorBullyUnit(eID))
		# 					{
		# 						// The closer we are the better, because the unit travels less distance to get home
		# 						if(GetPlayer()->GetProximityToPlayer(eMinor) == PLAYER_PROXIMITY_NEIGHBORS)
		# 							iValue += 50
		# 						elif(GetPlayer()->GetProximityToPlayer(eMinor) == PLAYER_PROXIMITY_CLOSE)
		# 							iValue += 30
		# 						elif(GetPlayer()->GetProximityToPlayer(eMinor) == PLAYER_PROXIMITY_FAR)
		# 							iValue += -30
		# 						elif(GetPlayer()->GetProximityToPlayer(eMinor) == PLAYER_PROXIMITY_DISTANT)
		# 							iValue += -50
		#
		# 						//antonjs: consider: knock it down if is there a chance the worker will get captured by a nearby rival
		#
		# 						//antonjs: consider: if military unit, it would be a good thing to get it near a rival or ongoing war
		#
		# 						// If this minor has a PtP from someone, bullying it could have big consequences
		# 						if(pMinor->GetMinorCivAI()->IsProtectedByAnyMajor())
		# 						{
		# 							iValue += -20
		# 							//antonjs: consider: scale based on which major is protecting it
		# 						}
		# 						else
		# 						{
		# 							iValue += 20
		# 						}
		#
		# 						//antonjs: consider: allies or friends with another major
		# 						//antonjs: consider: distance to other majors
		#
		# 						// If we are getting a bonus, don't mess that up!
		# 						if(pMinor->GetMinorCivAI()->IsAllies(eID) or pMinor->GetMinorCivAI()->IsFriends(eID))
		# 						{
		# 							iValue = 0
		# 						}
		#
		# 						// Do we want it enough?
		# 						if(iValue > 100)  //antonjs: todo: XML for threshold
		# 						{
		# 							veMinorsToBullyUnit.push_back(eMinor, iValue)
		# 							bWantsToBullyUnitFromThisMinor = true
		# 						}
		# 					}
		# 				}
		# 			}
		#
		# 			// Calculate desirability to bully gold from this minor
		# 			if(bWantsToBullyGold and !bWantsToBuyoutThisMinor and !bWantsToGiveGoldToThisMinor and !bWantsToBullyUnitFromThisMinor)
		# 			{
		# 				int iValue = 100 //antonjs: todo: XML, bully threshold
		# 				if(eApproach == MINOR_CIV_APPROACH_BULLY)
		# 				{
		# 					// Only bother if we can successfully bully
		# 					if(pMinor->GetMinorCivAI()->CanMajorBullyGold(eID))
		# 					{
		# 						// The closer we are the better
		# 						if(GetPlayer()->GetProximityToPlayer(eMinor) == PLAYER_PROXIMITY_NEIGHBORS)
		# 							iValue += 40
		# 						elif(GetPlayer()->GetProximityToPlayer(eMinor) == PLAYER_PROXIMITY_CLOSE)
		# 							iValue += 20
		#
		# 						// We like to keep bullying the same minor
		# 						if(pMinor->GetMinorCivAI()->IsEverBulliedByMajor(eID))
		# 						{
		# 							iValue += 20
		# 						}
		#
		# 						// If we have not bullied this minor recently, but someone else has, it might be good to wait for an opportunity to gain a lot of INF
		# 						if(!pMinor->GetMinorCivAI()->IsRecentlyBulliedByMajor(eID) and pMinor->GetMinorCivAI()->IsRecentlyBulliedByAnyMajor())
		# 						{
		# 							iValue += -10
		# 							//antonjs: consider: but if everyone near the minor has bullied it, then there is nobody to come to its rescue, so we can bully safely
		# 						}
		#
		# 						// If this minor has a PtP from someone, bullying it could have big consequences
		# 						if(pMinor->GetMinorCivAI()->IsProtectedByAnyMajor())
		# 						{
		# 							iValue += -10
		# 							//antonjs: consider: scale based on which major is protecting it
		# 						}
		# 						else
		# 						{
		# 							iValue += 10
		# 						}
		#
		# 						//antonjs: consider: allies or friends another major
		# 						//antonjs: consider: distance to other majors
		#
		# 						// If we are getting a bonus, don't mess that up!
		# 						if(pMinor->GetMinorCivAI()->IsAllies(eID) or pMinor->GetMinorCivAI()->IsFriends(eID))
		# 						{
		# 							iValue = 0
		# 						}
		#
		# 						// Do we want it enough?
		# 						if(iValue > 100)  //antonjs: todo: XML for threshold
		# 						{
		# 							veMinorsToBullyGold.push_back(eMinor, iValue)
		# 							bWantsToBullyGoldFromThisMinor = true
		# 						}
		# 					}
		# 				}
		# 			}
		#
		# 		}
		#
		# 		SetWantToRouteConnectToMinor(eMinor, bWantsToConnect)
		# 	}
		#
		# 	int iGoldReserve = GetPlayer()->GetTreasury()->GetGold()
		#
		# 	// Do we want to buyout a minor?
		# 	if(veMinorsToBuyout.size() > 0
		# 		veMinorsToBuyout.SortItems()
		# 		int iGoldLeft = GetPlayer()->GetTreasury()->GetGold()
		# 		PlayerTypes eLoopMinor = NO_PLAYER
		# 		for(int i = 0 i < veMinorsToBuyout.size() i++)
		# 		{
		# 			eLoopMinor = veMinorsToBuyout.GetElement(i)
		# 			int iBuyoutCost = GET_PLAYER(eLoopMinor).GetMinorCivAI()->GetBuyoutCost(eID)
		# 			if(iGoldLeft >= iBuyoutCost)
		# 			{
		# 				if(GET_PLAYER(eLoopMinor).GetMinorCivAI()->CanMajorBuyout(eID))
		# 				{
		# 					GC.getGame().DoMinorBuyout(eID, eLoopMinor)
		# 					iGoldLeft -= iBuyoutCost
		# 					break // Don't buyout more than once in a single turn
		# 				}
		# 				else
		# 				{
		# 					CvAssertMsg(False, "Chose a minor to buyout that cannot actually be bought! Please send Anton your save file and version.")
		# 				}
		# 			}
		# 			else
		# 			{
		# 				if(!GetPlayer()->GetEconomicAI()->IsSavingForThisPurchase(PURCHASE_TYPE_MINOR_CIV_GIFT))
		# 				{
		# 					LogMinorCivBuyout(eLoopMinor, iBuyoutCost, /*bSaving*/ true)
		#
		# 					int iPriority = GC.getAI_GOLD_PRIORITY_BUYOUT_CITY_STATE()
		# 					GetPlayer()->GetEconomicAI()->StartSaveForPurchase(PURCHASE_TYPE_MINOR_CIV_GIFT, iBuyoutCost, iPriority)
		# 				}
		# 			}
		# 		}
		# 	}
		#
		# 	// Do we want to give someone Gold enough to actually do it?
		# 	if(veMinorsToGiveGold.size() > 0
		# 		veMinorsToGiveGold.SortItems() // Sort from highest desirability to lowest
		# 		for(int i = 0 i < veMinorsToGiveGold.size() i++)
		# 		{
		# 			int iGoldLeft = GetPlayer()->GetTreasury()->GetGold()
		# 			MinorGoldGiftInfo sGift = veMinorsToGiveGold.GetElement(i)
		# 			sGift.iGoldAmount = 0
		#
		# 			if(iGoldLeft >= iSmallGift and sGift.bQuickBoost)
		# 				sGift.iGoldAmount = iSmallGift
		# 			elif(iGoldLeft >= iLargeGift)
		# 				sGift.iGoldAmount = iLargeGift
		# 			elif(iGoldLeft >= iMediumGift)
		# 				sGift.iGoldAmount = iMediumGift
		#
		# 			int iOldFriendship = GET_PLAYER(sGift.eMinor).GetMinorCivAI()->GetEffectiveFriendshipWithMajor(eID)
		#
		# 			// Able to give a gift?  Don't gift more than half of the gold we have in one turn
		# 			if(sGift.iGoldAmount > 0 and iGoldLeft >= (iGoldReserve / 2))
		# 			{
		# 				GET_PLAYER(sGift.eMinor).GetMinorCivAI()->DoGoldGiftFromMajor(self.player, sGift.iGoldAmount)  # antonjs: todo: go through CvGame instead?
		#
		# 				LogMinorCivGiftGold(sGift.eMinor, iOldFriendship, sGift.iGoldAmount, /*bSaving*/ False, sGift.bQuickBoost, sGift.eMajorRival)
		#
		# 				if(GetPlayer()->GetEconomicAI()->IsSavingForThisPurchase(PURCHASE_TYPE_MINOR_CIV_GIFT))
		# 					GetPlayer()->GetEconomicAI()->CancelSaveForPurchase(PURCHASE_TYPE_MINOR_CIV_GIFT)
		# 			}
		# 			// Can't afford gift yet, so start saving
		# 			else
		# 			{
		# 				if(!GetPlayer()->GetEconomicAI()->IsSavingForThisPurchase(PURCHASE_TYPE_MINOR_CIV_GIFT))
		# 				{
		# 					int iAmountToSaveFor = iMediumGift
		#
		# 					if(sGift.bQuickBoost)
		# 						iAmountToSaveFor = iSmallGift
		#
		# 					LogMinorCivGiftGold(sGift.eMinor, iOldFriendship, iAmountToSaveFor, /*bSaving*/ true, sGift.bQuickBoost, sGift.eMajorRival)
		#
		# 					int iPriority = GC.getAI_GOLD_PRIORITY_DIPLOMACY_BASE()
		# 					iPriority += GC.getAI_GOLD_PRIORITY_DIPLOMACY_PER_FLAVOR_POINT() * iDiplomacyFlavor
		# 					GetPlayer()->GetEconomicAI()->StartSaveForPurchase(PURCHASE_TYPE_MINOR_CIV_GIFT, iAmountToSaveFor, iPriority)
		# 				}
		# 			}
		# 		}
		# 	}
		#
		# 	// Do we want a unit enough to bully someone?
		# 	if(veMinorsToBullyUnit.size() > 0
		# 		veMinorsToBullyUnit.SortItems()
		# 		PlayerTypes eLoopMinor = NO_PLAYER
		# 		for(int i = 0 i < veMinorsToBullyUnit.size() i++)
		# 		{
		# 			eLoopMinor = veMinorsToBullyUnit.GetElement(i)
		# 			CvAssertMsg(eLoopMinor != NO_PLAYER, "Trying to bully a unit from NO_PLAYER! Please send Anton your save file and version.")
		# 			if(GET_PLAYER(eLoopMinor).GetMinorCivAI()->CanMajorBullyUnit(eID))
		# 			{
		# 				GC.getGame().DoMinorBullyUnit(eID, eLoopMinor)
		# 				break // Don't bully a unit more than once in a single turn
		# 			}
		# 			else
		# 			{
		# 				CvAssertMsg(False, "Chose a minor to bully unit from that cannot actually be bullied! Please send Anton your save file and version.")
		# 			}
		# 		}
		# 	}
		#
		# 	// Do we want gold enough to bully someone?
		# 	if(veMinorsToBullyGold.size() > 0
		# 		veMinorsToBullyGold.SortItems()
		# 		PlayerTypes eLoopMinor = NO_PLAYER
		# 		for(int i = 0 i < veMinorsToBullyGold.size() i++)
		# 		{
		# 			eLoopMinor = veMinorsToBullyGold.GetElement(i)
		# 			CvAssertMsg(eLoopMinor != NO_PLAYER, "Trying to bully gold from NO_PLAYER! Please send Anton your save file and version.")
		# 			if(GET_PLAYER(eLoopMinor).GetMinorCivAI()->CanMajorBullyGold(eID))
		# 			{
		# 				GC.getGame().DoMinorBullyGold(eID, eLoopMinor)
		# 			}
		# 			else
		# 			{
		# 				CvAssertMsg(False, "Chose a minor to bully gold from that cannot actually be bullied! Please send Anton your save file and version.")
		# 			}
		# 		}
		# 	}

	def establishOpenBorderAgreementWith(self, otherPlayer, turn: int):
		self.playerDict.establishOpenBorderAgreementWith(otherPlayer, turn)

	def militaryAggressivePostureOf(self, otherPlayer) -> AggressivePostureType:
		return self.playerDict.militaryAggressivePostureOf(otherPlayer)

	def lastTurnMilitaryAggressivePosture(self, otherPlayer) -> AggressivePostureType:
		return self.playerDict.lastTurnMilitaryAggressivePosture(otherPlayer)

	def isDeclarationOfFriendshipActiveWith(self, otherPlayer) -> bool:
		return self.playerDict.isDeclarationOfFriendshipActiveWith(otherPlayer)

	def isDefensivePactActiveWith(self, otherPlayer):
		return self.playerDict.isDefensivePactActiveWith(otherPlayer)

	def changeRecentTradeValueWith(self, otherPlayer, param):
		pass

	def majorCivOpinionWeightTowards(self, otherPlayer) -> int:
		"""What is the number value of our opinion towards otherPlayer?"""
		opinionWeight: int = 0

		# // // // // // // // // // // // // // // // // // //
		# How nasty am I?
		# // // // // // // // // // // // // // // // // // //
		hostility = self.playerDict.personalityMajorCivApproachBias(MajorPlayerApproachType.hostile)  # MAJOR_CIV_APPROACH_HOSTILE
		friendliness = self.playerDict.personalityMajorCivApproachBias(MajorPlayerApproachType.friendly)  # MAJOR_CIV_APPROACH_FRIENDLY
		opinionWeight += (hostility - friendliness) * 2

		opinionWeight += self.landDisputeLevelScoreWith(otherPlayer)
		opinionWeight += self.wonderDisputeLevelScoreWith(otherPlayer)
		opinionWeight += self.minorCivDisputeLevelScoreWith(otherPlayer)
		opinionWeight += self.warmongerThreatScoreWith(otherPlayer)

		# // // // // // // // // // // // // // // // // // //
		# Player has done nice stuff
		# // // // // // // // // // // // // // // // // // //
		# opinionWeight += GetCiviliansReturnedToMeScore(otherPlayer)
		# opinionWeight += GetLandmarksBuiltForMeScore(otherPlayer)
		# opinionWeight += GetResurrectedScore(otherPlayer)
		# opinionWeight += GetLiberatedCitiesScore(otherPlayer)
		# opinionWeight += GetEmbassyScore(otherPlayer)
		# opinionWeight += GetForgaveForSpyingScore(otherPlayer)
		# opinionWeight += GetTimesIntrigueSharedScore(otherPlayer)

		# // // // // // // // // // // // // // // // // // //
		# Player has asked us to do stuff we don't like
		# // // // // // // // // // // // // // // // // // //
		# opinionWeight += GetNoSetterRequestScore(otherPlayer)
		# opinionWeight += GetStopSpyingRequestScore(otherPlayer)
		# opinionWeight += GetDemandEverMadeScore(otherPlayer)
		# opinionWeight += GetTimesCultureBombedScore(otherPlayer)
		# opinionWeight += GetReligiousConversionPointsScore(otherPlayer)

		# opinionWeight += GetHasAdoptedHisReligionScore(otherPlayer)
		# opinionWeight += GetHasAdoptedMyReligionScore(otherPlayer)

		# opinionWeight += GetSameLatePoliciesScore(otherPlayer)
		# opinionWeight += GetDifferentLatePoliciesScore(otherPlayer)

		# opinionWeight += GetTimesRobbedScore(otherPlayer)

		# // // // // // // // // // // // // // // // // // //
		# BROKEN PROMISES :_:
		# // // // // // // // // // // // // // // // // // //
		# opinionWeight += GetBrokenMilitaryPromiseScore(ePlayer);
		# opinionWeight += GetBrokenMilitaryPromiseWithAnybodyScore(ePlayer);
		# opinionWeight += GetIgnoredMilitaryPromiseScore(ePlayer);
		# opinionWeight += GetBrokenExpansionPromiseScore(ePlayer);
		# opinionWeight += GetIgnoredExpansionPromiseScore(ePlayer);
		# opinionWeight += GetBrokenBorderPromiseScore(ePlayer);
		# opinionWeight += GetIgnoredBorderPromiseScore(ePlayer);
		#
		# opinionWeight += GetBrokenAttackCityStatePromiseScore(ePlayer);
		# opinionWeight += GetBrokenAttackCityStatePromiseWithAnybodyScore(ePlayer);
		# opinionWeight += GetIgnoredAttackCityStatePromiseScore(ePlayer);
		#
		# opinionWeight += GetBrokenBullyCityStatePromiseScore(ePlayer);
		# opinionWeight += GetIgnoredBullyCityStatePromiseScore(ePlayer);
		#
		# opinionWeight += GetBrokenNoConvertPromiseScore(ePlayer);
		# opinionWeight += GetIgnoredNoConvertPromiseScore(ePlayer);
		#
		# opinionWeight += GetBrokenNoDiggingPromiseScore(ePlayer);
		# opinionWeight += GetIgnoredNoDiggingPromiseScore(ePlayer);
		#
		# opinionWeight += GetBrokenSpyPromiseScore(ePlayer);
		# opinionWeight += GetIgnoredSpyPromiseScore(ePlayer);
		#
		# opinionWeight += GetBrokenCoopWarPromiseScore(ePlayer);

		# // // // // // // // // // // // // // // // // // //
		# PROTECTED MINORS
		# // // // // // // // // // // // // // // // // // //
		# opinionWeight += GetAngryAboutProtectedMinorKilledScore(otherPlayer)
		# opinionWeight += GetAngryAboutProtectedMinorAttackedScore(otherPlayer)
		# opinionWeight += GetAngryAboutProtectedMinorBulliedScore(otherPlayer)

		# // // // // // // // // // // // // // // // // // //
		# BULLIED MINORS
		# // // // // // // // // // // // // // // // // // //
		# opinionWeight += GetAngryAboutSidedWithProtectedMinorScore(otherPlayer)

		# // // // // // // // // // // // // // // // // // //
		# DECLARATION OF FRIENDSHIP
		# // // // // // // // // // // // // // // // // // //
		# opinionWeight += GetDOFAcceptedScore(otherPlayer)
		# opinionWeight += GetDOFWithAnyFriendScore(otherPlayer)
		# opinionWeight += GetDOFWithAnyEnemyScore(otherPlayer)

		# // // // // // // // // // // // // // // // // // //
		# FRIENDS NOT GETTING ALONG
		# // // // // // // // // // // // // // // // // // //

		# Beginning TraitorOpinion bit
		# traitorOpinion = self.friendDenouncementScore(otherPlayer)
		# traitorOpinion = max(traitorOpinion, self.weDenouncedFriendScore(otherPlayer))
		# traitorOpinion = max(traitorOpinion, self.friendDenouncedUsScore(otherPlayer))
		# traitorOpinion = max(traitorOpinion, self.weDeclaredWarOnFriendScore(otherPlayer))
		# traitorOpinion = max(traitorOpinion, self.friendDeclaredWarOnUsScore(otherPlayer))
		# opinionWeight += traitorOpinion
		# End TraitorOpinion bit

		# opinionWeight += GetRequestsRefusedScore(otherPlayer)

		# // // // // // // // // // // // // // // // // // //
		# DENOUNCING
		# // // // // // // // // // // // // // // // // // //

		# opinionWeight += GetDenouncedUsScore(otherPlayer)
		# opinionWeight += GetDenouncedThemScore(otherPlayer)
		# opinionWeight += GetDenouncedFriendScore(otherPlayer)
		# opinionWeight += GetDenouncedEnemyScore(otherPlayer)

		# // // // // // // // // // // // // // // // // // //
		# RECKLESS EXPANDER
		# // // // // // // // // // // // // // // // // // //
		# opinionWeight += GetRecklessExpanderScore(otherPlayer)

		# // // // // // // // // // // // // // // // // // //
		# JUNE 2011 ADDITIONS
		# // // // // // // // // // // // // // // // // // //
		# opinionWeight += GetRecentTradeScore(otherPlayer)
		# opinionWeight += GetCommonFoeScore(otherPlayer)
		# opinionWeight += GetRecentAssistScore(otherPlayer)

		# opinionWeight += GetNukedByScore(otherPlayer)
		# opinionWeight += GetCapitalCapturedByScore(otherPlayer)

		# opinionWeight += GetGaveAssistanceToScore(otherPlayer)
		# opinionWeight += GetPaidTributeToScore(otherPlayer)

		# // // // // // // // // // // // // // // // // // //
		# XP2
		# // // // // // // // // // // // // // // // // // //

		# opinionWeight += GetLikedTheirProposalScore(otherPlayer)
		# opinionWeight += GetDislikedTheirProposalScore(otherPlayer)
		# opinionWeight += GetSupportedMyProposalScore(otherPlayer)
		# opinionWeight += GetFoiledMyProposalScore(otherPlayer)
		# opinionWeight += GetSupportedMyHostingScore(otherPlayer)

		# // // // // // // // // // // // // // // // // // //
		# SCENARIO - SPECIFIC
		# // // // // // // // // // // // // // // // // // //
		# opinionWeight += GetScenarioModifier1(otherPlayer)
		# opinionWeight += GetScenarioModifier2(otherPlayer)
		# opinionWeight += GetScenarioModifier3(otherPlayer)

		return opinionWeight

	# // // // // // // // // // // // // // // // // // // // // // // // // // // // /
	# Opinion modifiers
	# // // // // // // // // // // // // // // // // // // // // // // // // // // // /

	def landDisputeLevelScoreWith(self, otherPlayer) -> int:
		# Look at Land Dispute
		opinionWeight: int = 0
		landDisputeLevelValue: DisputeLevelType = self.landDisputeLevelWith(otherPlayer)
		if landDisputeLevelValue == DisputeLevelType.fierce:  # DISPUTE_LEVEL_FIERCE
			opinionWeight += 30  # OPINION_WEIGHT_LAND_FIERCE
		elif landDisputeLevelValue == DisputeLevelType.strong:  # DISPUTE_LEVEL_STRONG
			opinionWeight += 20  # OPINION_WEIGHT_LAND_STRONG
		elif landDisputeLevelValue == DisputeLevelType.weak:  # DISPUTE_LEVEL_WEAK
			opinionWeight += 10  # OPINION_WEIGHT_LAND_WEAK
		elif landDisputeLevelValue == DisputeLevelType.none:  # DISPUTE_LEVEL_NONE
			opinionWeight += -6  # OPINION_WEIGHT_LAND_NONE

		return opinionWeight

	def wonderDisputeLevelScoreWith(self, otherPlayer) -> int:
		"""Look at Wonder Competition Dispute"""
		opinionWeight: int = 0
		wonderDisputeLevelValue: DisputeLevelType = self.wonderDisputeLevelWith(otherPlayer)
		if wonderDisputeLevelValue == DisputeLevelType.fierce:  # DISPUTE_LEVEL_FIERCE
			opinionWeight += 20  # OPINION_WEIGHT_WONDER_FIERCE
		elif wonderDisputeLevelValue == DisputeLevelType.strong:  # DISPUTE_LEVEL_STRONG
			opinionWeight += 15  # OPINION_WEIGHT_WONDER_STRONG
		elif wonderDisputeLevelValue == DisputeLevelType.weak:  # DISPUTE_LEVEL_WEAK
			opinionWeight += 10  # OPINION_WEIGHT_WONDER_WEAK
		elif wonderDisputeLevelValue == DisputeLevelType.none:  # DISPUTE_LEVEL_NONE
			opinionWeight += 0  # OPINION_WEIGHT_WONDER_NONE
	
		return opinionWeight

	def wonderDisputeLevelWith(self, otherPlayer) -> DisputeLevelType:
		return self.playerDict.wonderDisputeLevelWith(otherPlayer)

	def doUpdateVictoryDisputeLevels(self, simulation):
		"""Updates what is our level of Dispute with a player is over Victory"""
		myGrandStrategy = self.player.grandStrategyAI.activeStrategy

		# Loop through all (known) Players
		for loopPlayer in simulation.players:
			if not self.isValid(loopPlayer):
				continue

			disputeLevel: DisputeLevelType = DisputeLevelType.none

			# Minors can't really be an issue with Victory!
			if loopPlayer.isMajorAI() or loopPlayer.isHuman():
				victoryDisputeWeight: int = 0

				# Does the other player's (estimated) Grand Strategy match our own?
				if self.player.grandStrategyAI.guessOtherPlayerActiveGrandStrategyOf(loopPlayer) == myGrandStrategy:
					guessConfidence: GuessConfidenceType = self.player.grandStrategyAI.guessOtherPlayerActiveGrandStrategyConfidenceOf(loopPlayer)

					if guessConfidence == GuessConfidenceType.positive:  # GUESS_CONFIDENCE_POSITIVE
						victoryDisputeWeight += 14  # VICTORY_DISPUTE_GRAND_STRATEGY_MATCH_POSITIVE
					elif guessConfidence == GuessConfidenceType.likely:  # GUESS_CONFIDENCE_LIKELY
						victoryDisputeWeight += 10  # VICTORY_DISPUTE_GRAND_STRATEGY_MATCH_LIKELY
					elif guessConfidence == GuessConfidenceType.unsure:  # GUESS_CONFIDENCE_UNSURE
						victoryDisputeWeight += 6  # VICTORY_DISPUTE_GRAND_STRATEGY_MATCH_UNSURE

				# Add weight for Player's competitiveness (0 - 10)
				victoryDisputeWeight *= self.playerDict.victoryCompetitiveness()

				# Grand Strategy Matches: 10
				# VictoryCompetitiveness 10 : 100
				# VictoryCompetitiveness 5	: 50
				# VictoryCompetitiveness 1	: 10

				# Now See what our new Dispute Level should be
				if victoryDisputeWeight >= 80:  # VICTORY_DISPUTE_FIERCE_THRESHOLD
					disputeLevel = DisputeLevelType.fierce  # DISPUTE_LEVEL_FIERCE
				elif victoryDisputeWeight >= 50:  # VICTORY_DISPUTE_STRONG_THRESHOLD
					disputeLevel = DisputeLevelType.strong  # DISPUTE_LEVEL_STRONG
				elif victoryDisputeWeight >= 30:  # VICTORY_DISPUTE_WEAK_THRESHOLD
					disputeLevel = DisputeLevelType.weak  # DISPUTE_LEVEL_WEAK

			# Actually set the Level
			self.playerDict.updateVictoryDisputeLevel(loopPlayer, disputeLevel)

		return

	def doUpdateWonderDisputeLevels(self, simulation):
		"""Updates what is our level of Dispute with a player is over Wonder"""
		# Loop through all (known) Players
		for loopPlayer in simulation.players:
			if not loopPlayer.isMajorAI() and not loopPlayer.isHuman():
				continue
				
			if not self.isValid(loopPlayer):
				continue

			disputeLevel: DisputeLevelType = DisputeLevelType.none  # DISPUTE_LEVEL_NONE

			wonderDisputeWeight: int = self.numberOfWondersBeatenBy(loopPlayer)

			# Add weight for Player's competitiveness (0 - 10)
			wonderDisputeWeight *= self.playerDict.wonderCompetitiveness()

			# Now See what our new Dispute Level should be
			if wonderDisputeWeight >= 10:  # WONDER_DISPUTE_FIERCE_THRESHOLD
				disputeLevel = DisputeLevelType.fierce  # DISPUTE_LEVEL_FIERCE
			elif wonderDisputeWeight >= 7:  # WONDER_DISPUTE_STRONG_THRESHOLD
				disputeLevel = DisputeLevelType.strong  # DISPUTE_LEVEL_STRONG
			elif wonderDisputeWeight >= 5:  # WONDER_DISPUTE_WEAK_THRESHOLD
				disputeLevel = DisputeLevelType.weak  # DISPUTE_LEVEL_WEAK

			# Actually set the Level
			self.playerDict.updateWonderDisputeLevel(loopPlayer, disputeLevel)

		return

	def doUpdateMinorCivDisputeLevels(self, simulation):
		"""Updates what is our level of Dispute with a player is over Minor Civ Friendship"""
		minorCivDisputeWeight: int = 0

		# Personality factors in quite a bit here, which is why we square the value
		personalityMod = self.player.leader.minorCivCompetitiveness() * self.player.leader.minorCivCompetitiveness()  # Ranges from 0 to 100

		# Loop through all (known) Players
		for loopPlayer in simulation.players:
			if not loopPlayer.isMajorAI() and not loopPlayer.isHuman():
				continue

			if not self.isValid(loopPlayer):
				continue

			disputeLevel: DisputeLevelType = DisputeLevelType.none  # DISPUTE_LEVEL_NONE
			minorDisputeWeight = 0

			# Loop through all minors to check our relationship with them
			for loopMinor in simulation.players:
				if not loopMinor.isCityState():
					continue

				if not self.isValid(loopMinor):
					continue

				# We have a PtP with this minor
				if loopMinor.minorCivAI.isProtectedByMajor(self.player):
					# Player is Allies with this minor
					if loopMinor.minorCivAI.isAllies(loopPlayer):
						minorCivDisputeWeight += personalityMod * 10  # MINOR_CIV_DISPUTE_ALLIES_WEIGHT
					# Player is Friends with this minor
					elif loopMinor.minorCivAI.isFriends(loopPlayer):
						minorCivDisputeWeight += personalityMod * 5  # MINOR_CIV_DISPUTE_FRIENDS_WEIGHT

			# Now See what our new Dispute Level should be
			if minorCivDisputeWeight >= 700:  # MINOR_CIV_DISPUTE_FIERCE_THRESHOLD
				disputeLevel = DisputeLevelType.fierce  # DISPUTE_LEVEL_FIERCE
			elif minorCivDisputeWeight >= 400:  # GC.getMINOR_CIV_DISPUTE_STRONG_THRESHOLD
				disputeLevel = DisputeLevelType.strong  # DISPUTE_LEVEL_STRONG
			elif minorCivDisputeWeight >= 200:  # GC.getMINOR_CIV_DISPUTE_WEAK_THRESHOLD
				disputeLevel = DisputeLevelType.weak  # DISPUTE_LEVEL_WEAK

			# Actually set the Level
			self.playerDict.updateMinorCivDisputeLevelTowards(loopPlayer, disputeLevel)

		return

	def numberOfWondersBeatenBy(self, otherPlayer) -> int:
		"""GetNumWondersBeatenTo - How many wonders has otherPlayer beaten us to?"""
		return self.playerDict.numberOfWondersBeatenBy(otherPlayer)

	def changeNumberOfWondersBeatenBy(self, otherPlayer, delta: int):
		raise Exception()

	def minorCivDisputeLevelScoreWith(self, otherPlayer) -> int:
		opinionWeight: int = 0
		# Look at Minor Civ Friendship Dispute
		minorCivDisputeLevelValue: DisputeLevelType = self.playerDict.minorCivDisputeLevelWith(otherPlayer)
		if minorCivDisputeLevelValue == DisputeLevelType.fierce:  # DISPUTE_LEVEL_FIERCE
			opinionWeight += 30  # OPINION_WEIGHT_MINOR_CIV_FIERCE
		if minorCivDisputeLevelValue == DisputeLevelType.strong:  # DISPUTE_LEVEL_STRONG:
			opinionWeight += 20  # OPINION_WEIGHT_MINOR_CIV_STRONG
		if minorCivDisputeLevelValue == DisputeLevelType.weak:  # DISPUTE_LEVEL_WEAK:
			opinionWeight += 10  # OPINION_WEIGHT_MINOR_CIV_WEAK
		if minorCivDisputeLevelValue == DisputeLevelType.none:  # DISPUTE_LEVEL_NONE:
			opinionWeight += 0  # OPINION_WEIGHT_MINOR_CIV_NONE

		return opinionWeight

	def minorCivDisputeLevelWith(self, otherPlayer) -> DisputeLevelType:
		return self.playerDict.minorCivDisputeLevelWith(otherPlayer)

	def warmongerThreatScoreWith(self, otherPlayer) -> int:
		opinionWeight: int = self.otherPlayerWarmongerScoreWith(otherPlayer)
		if opinionWeight < 5:
			opinionWeight = 0

		return opinionWeight

	def otherPlayerWarmongerScoreWith(self, otherPlayer) -> int:
		"""The value of the warmonger amount adjusted by how much this player hates warmongers"""
		returnValue = self.otherPlayerWarmongerAmountTowards(otherPlayer)

		# Value at this point is from 250 (DOW) to upwards of 2000 (after capturing several cities)
		# Want final value to be about 1/20th that (Jon wanted max Opinion hit to be 100)
		# Average WarmongerHate is 5, so divide by 100 to get to 1/20th.
		returnValue *= self.warmongerHate()
		returnValue /= 100
		return returnValue

	def otherPlayerWarmongerAmountTowards(self, otherPlayer) -> int:
		"""Get amount of warmongerishness felt toward this player"""
		return self.playerDict.otherPlayerWarmongerAmountTowards(otherPlayer)

	def warmongerHate(self) -> int:
		return self.playerDict.warmongerHate()

	def otherPlayerNumberOfMinorsAttackedBy(self, otherPlayer) -> int:
		return self.playerDict.otherPlayerNumberOfMinorsAttackedBy(otherPlayer)

	def otherPlayerNumberOfMinorsConqueredBy(self, otherPlayer) -> int:
		return self.playerDict.otherPlayerNumberOfMinorsConqueredBy(otherPlayer)

	def otherPlayerNumberOfMajorsAttackedBy(self, otherPlayer) -> int:
		return self.playerDict.otherPlayerNumberOfMajorsAttackedBy(otherPlayer)

	def otherPlayerNumberOfMajorsConqueredBy(self, otherPlayer) -> int:
		return self.playerDict.otherPlayerNumberOfMajorsConqueredBy(otherPlayer)

	def isDeclarationOfFriendshipAcceptedBy(self, otherPlayer) -> bool:
		return self.playerDict.isDeclarationOfFriendshipActiveWith(otherPlayer)

	def isDeclarationOfFriendshipAcceptableBy(self, otherPlayer) -> bool:
		"""Is this AI willing to work with otherPlayer?"""
		# Can't declare friendship with a civ you're at war with
		if self.player.isAtWarWith(otherPlayer):  # or GC.getGame().isOption(GAMEOPTION_ALWAYS_WAR))
			return False

		# Haven't known this guy for long enough
		if self.isTooEarlyForDeclarationOfFriendshipTowards(otherPlayer):
			return False

		approach: MajorPlayerApproachType = self.majorCivApproachTowards(otherPlayer, hideTrueFeelings=False)

		# If player is planning War, always say no
		if approach == MajorPlayerApproachType.war:
			return False
		# If player is Hostile, always say no
		elif approach == MajorPlayerApproachType.hostile:
			return False
		# If player is afraid, always say yes
		elif approach == MajorPlayerApproachType.afraid:
			return True

		opinion: MajorCivOpinionType = self.majorCivOpinion(otherPlayer)

		# If player is unforgivable, always say no
		if opinion == MajorCivOpinionType.unforgivable:
			return False
		# If player is an enemy, always say no
		elif opinion == MajorCivOpinionType.enemy:
			return False

		# Has there been a denouncement either direction?
		if self.isDenouncedPlayer(otherPlayer):
			return False

		if otherPlayer.diplomacyAI.isDenouncedPlayer(self.player):
			return False

		# Are we working AGAINST otherPlayer with someone else ?
		# if (IsWorkingAgainstPlayer(otherPlayer))
		# return false

		iWeight = 0

		# Base Personality value ranges from 0 to 10(ish)
		iWeight += self.playerDict.declarationOfFriendshipWillingness()

		# Weight for Approach
		if approach == MajorPlayerApproachType.deceptive:
			iWeight += 3
		elif approach == MajorPlayerApproachType.guarded:
			iWeight += -1
		elif approach == MajorPlayerApproachType.friendly:
			iWeight += 3

		# Weight for Opinion
		if opinion == MajorCivOpinionType.competitor:
			iWeight += -3
		elif opinion == MajorCivOpinionType.favorable:
			iWeight += 2
		elif opinion == MajorCivOpinionType.friend:
			iWeight += 5
		elif opinion == MajorCivOpinionType.ally:
			iWeight += 10

		# Rand
		iWeight += 0 if Tests.are_running else random.randint(0, 5)  # Diplomacy AI: Rand for whether AI wants to work with player

		if iWeight >= 12:  # DOF_THRESHOLD:
			return True

		return False

	def isDenouncedPlayer(self, otherPlayer) -> bool:
		return self.playerDict.isDenouncedPlayer(otherPlayer)

	def isFriendDenouncedUs(self, otherPlayer) -> bool:
		# fixme
		return False

	def isAngryAboutProtectedMinorKilled(self, otherPlayer) -> bool:
		# fixme
		return False

	def isAngryAboutProtectedMinorAttacked(self, otherPlayer) -> bool:
		# fixme
		return False

	def isDemandEverMade(self, otherPlayer) -> bool:
		# fixme
		return False

	def isPlayerBrokenMilitaryPromise(self, otherPlayer) -> bool:
		# fixme
		return False

	def isPlayerIgnoredMilitaryPromise(self, otherPlayer) -> bool:
		# fixme
		return False

	def everMadeExpansionPromiseTowards(self, otherPlayer) -> bool:
		# fixme
		return False

	def isPlayerMadeExpansionPromiseTowards(self, otherPlayer) -> bool:
		# fixme
		return False

	def isPlayerBrokenExpansionPromiseTowards(self, otherPlayer) -> bool:
		# fixme
		return False

	def isPlayerIgnoredExpansionPromiseTowards(self, otherPlayer) -> bool:
		# fixme
		return False

	def isPlayerBrokenExpansionPromiseTowards(self, otherPlayer) -> bool:
		# fixme
		return False

	def isPlayerBrokenBorderPromiseTowards(self, otherPlayer) -> bool:
		# fixme
		return False

	def everMadeBorderPromiseTowards(self, otherPlayer) -> bool:
		# fixme
		return False

	def isPlayerMadeBorderPromiseTowards(self, otherPlayer) -> bool:
		# fixme
		return False

	def isPlayerIgnoredBorderPromiseTowards(self, otherPlayer) -> bool:
		# fixme
		return False

	def isPlayerBrokenAttackCityStatePromise(self, otherPlayer) -> bool:
		return self.playerDict.isPlayerBrokenAttackCityStatePromise(otherPlayer)

	def isPlayerIgnoredAttackCityStatePromise(self, otherPlayer) -> bool:
		# fixme
		return False

	def isPlayerBrokenBullyCityStatePromise(self, otherPlayer) -> bool:
		# fixme
		return False

	def isPlayerIgnoredBullyCityStatePromise(self, otherPlayer) -> bool:
		# fixme
		return False

	def isNukedBy(self, otherPlayer) -> bool:
		# fixme
		return False

	def isLockedIntoCoopWarWith(self, otherPlayer) -> bool:
		# fixme
		return False

	def turnsSincePlayerAttackedProtectedMinor(self, otherPlayer) -> int:
		# fixme
		return 9999

	def doMakeWar(self, simulation):
		"""Handles declarations of War for this AI"""
		playerList = WeightedBaseList()

		for loopPlayer in simulation.players:
			if loopPlayer.isBarbarian():
				continue

			if not self.isValid(loopPlayer):
				continue

			if self.player == loopPlayer:
				continue

			weight = self.warProjectionAgainst(loopPlayer).value() + 1

			# Square the distance enum to make it crucial
			weight *= (1 + self.proximityTo(loopPlayer).value())
			weight *= (1 + self.proximityTo(loopPlayer).value())

			if loopPlayer.isMajorAI() or loopPlayer.isHuman():
				if self.majorCivOpinion(loopPlayer) == MajorCivOpinionType.unforgivable:  # MAJOR_CIV_OPINION_UNFORGIVABLE
					weight *= 2

				weight *= 10  # Make sure majors are looked at before city states

			playerList.setWeight(weight, loopPlayer)

		playerList.sortByValue(reverse=True)  # biggest first

		for loopPlayer in playerList.keys():
			self.doMakeWarOnPlayer(loopPlayer, simulation)

		# Increment counters for co-op wars we have agreed to - this may trigger war
		for loopPlayer in simulation.players:
			if loopPlayer == self.player:
				continue

			if not self.isValid(loopPlayer):
				continue

			# AI players will always declare war at 10 turns, so we simplify things here -
			# humans are handled by DoCoopWarTimeStatement()
			if not loopPlayer.isMajorAI():
				continue

			for thirdPlayer in simulation.players:
				if thirdPlayer == self.player or thirdPlayer == loopPlayer:
					continue

				if not self.isValid(thirdPlayer):
					continue

				if not thirdPlayer.isMajorAI() and not thirdPlayer.isHuman():
					continue

				if not loopPlayer.diplomacyAI.hasMetWith(thirdPlayer):
					continue

				currentCoopWarCounter: int = self.coopWarCounterWith(loopPlayer, thirdPlayer)
				if currentCoopWarCounter > 0:
					self.updateCoopWarCounterWith(loopPlayer, thirdPlayer, currentCoopWarCounter + 1)

				if self.coopWarCounterWith(loopPlayer, thirdPlayer) > 10:  # COOP_WAR_SOON_COUNTER
					# Us
					self.updateCoopWarAcceptedState(loopPlayer, thirdPlayer, CoopWarStateType.accepted)  # COOP_WAR_STATE_ACCEPTED
					self.updateCoopWarCounterWith(loopPlayer, thirdPlayer, 0)
					self.doDeclareWarTo(thirdPlayer, simulation)
					self.player.militaryAI.requestShowOfForce(thirdPlayer)

					lockedTurns = 15  # COOP_WAR_LOCKED_LENGTH
					self.playerDict.updateNumberOfTurnsLockedIntoWarWith(thirdPlayer, lockedTurns)

	def doMakeWarOnPlayer(self, targetPlayer, simulation):
		"""Handles declarations of War for this AI"""
		wantToAttack: bool = False
		declareWar: bool = False

		if targetPlayer.isBarbarian():
			return

		if not self.isValid(targetPlayer):
			return

		if self.warGoalTowards(targetPlayer) == WarGoalType.demand:  # WAR_GOAL_DEMAND
			return

		if self.isAtWarWith(targetPlayer):
			return

		atWarWithAtLeastOneMajor = self.player.militaryAI.adopted(MilitaryStrategyType.atWar)

		# Minor Civ
		if targetPlayer.isCityState():
			minorCivApp: MinorPlayerApproachType = self.minorApproachTowards(targetPlayer)
			wantToAttack = not atWarWithAtLeastOneMajor and (minorCivApp == MinorPlayerApproachType.conquest)
			operation = self.player.militaryAI.cityStateAttackOperationAgainst(targetPlayer)
		else:  # Major Civ
			majorCivApp: MajorPlayerApproachType = self.majorCivApproachTowards(targetPlayer, hideTrueFeelings=False)
			wantToAttack = (majorCivApp == MajorPlayerApproachType.war or (
					majorCivApp == MajorPlayerApproachType.deceptive and self.isGoingForWorldConquest()))
			wantToAttack = wantToAttack and not atWarWithAtLeastOneMajor  # let 's not get into another war right now
			operation = self.player.militaryAI.sneakAttackOperationAgainst(targetPlayer)

		# Not yet readying an attack
		# If we're "mustering" it means we had a Sneak Attack Operation that finished
		if operation is None and not self.playerDict.isMusteringForAttackAgainst(targetPlayer):
			if not self.isAtWarWith(targetPlayer):
				if self.canDeclareWarTowards(targetPlayer):
					# Want to declare war on someone
					if wantToAttack:
						self.playerDict.updateWarGoalTowards(targetPlayer, WarGoalType.prepare)

						# Attack on minor
						if targetPlayer.isCityState():
							self.player.militaryAI.requestCityStateAttackAgainst(targetPlayer, simulation)
						else:  # Attack on major
							self.player.militaryAI.requestSneakAttackAgainst(targetPlayer, simulation)

		else:  # We already have an attack on the way
			# Our Approach with this player calls for war
			if wantToAttack:
				if not self.isAtWarWith(targetPlayer):
					if self.canDeclareWarTowards(targetPlayer):
						# If we're at least 85% of the way to our objective, let loose the dogs of war!
						# If we're "mustering" it means we have a Sneak Attack Operation that's in position to attack
						if (self.playerDict.isMusteringForAttackAgainst(targetPlayer) or
							(operation is not None and operation.percentFromMusterPointToTarget(simulation) >= 85)):
							declareWar = True
							self.playerDict.updateMusteringForAttackAgainst(targetPlayer, False)
			else:  # We were planning an attack, but changed our minds so abort
				if operation is not None:
					operation.kill(OperationStateReason.diploOpinionChange)
					self.updateWarGoalAgainst(targetPlayer, WarGoalType.none)  # NO_WAR_GOAL_TYPE
					self.playerDict.updateMusteringForAttackAgainst(targetPlayer, False)

			# If our Sneak Attack is read then actually initiate the DoW
			if declareWar:
				self.doDeclareWarTo(targetPlayer, simulation)

		return

	def updateCoopWarAcceptedState(self, treatyPlayer, otherPlayer, coopWarState: CoopWarStateType):
		self.playerDict.updateCoopWarAcceptedState(treatyPlayer, otherPlayer, coopWarState)

	def updateCoopWarCounterWith(self, treatyPlayer, otherPlayer, value: int):
		"""
		updates the value of the duration the coop war treaty with treatyPlayer against otherPlayer

		@param treatyPlayer: player we have an agreement or not
		@param otherPlayer: player the agreement is against
		@param value: new value counted in turn increments
		"""
		self.playerDict.updateCoopWarCounterWith(treatyPlayer, otherPlayer, value)

	def coopWarCounterWith(self, treatyPlayer, otherPlayer) -> int:
		"""
		when does this player promised any coop war against otherPlayer?

		@param treatyPlayer: player we have an agreement or not
		@param otherPlayer: player the agreement is against
		@return: current duration of the coop war agreement
		"""
		return self.playerDict.coopWarCounterWith(treatyPlayer, otherPlayer)

	def updateWarGoalAgainst(self, otherPlayer, warGoal: WarGoalType):
		self.playerDict.updateWarGoalTowards(otherPlayer, warGoal)

	def dealToRenew(self, simulation) -> (Optional[DiplomaticDeal], DiplomaticDealType):
		"""Deal to renew"""
		gameDeals = simulation.gameDeals

		# if (piDealType):
		# 	*piDealType = -1

		for dealType in list(DiplomaticDealType):
			if dealType == DiplomaticDealType.none:
				continue

			for deal in gameDeals.dealsOf(self.player, dealType):
				if deal.consideringForRenewal:
					return deal, dealType

		return None, DiplomaticDealType.none

	def doAggressiveMilitaryStatementTowards(self, otherPlayer, statement: DiplomaticStatementType, simulation) -> DiplomaticStatementType:
		"""Possible Contact Statement - guy has his military positioned aggressively near us"""
		if statement == DiplomaticStatementType.none:
			bSendStatement: bool = False

			# They must be able to declare war on us
			if not otherPlayer.canDeclareWarTowards(self.player):
				return DiplomaticStatementType.none

			# Don't threaten if this person resurrected us
			if self.wasResurrectedBy(otherPlayer):
				return DiplomaticStatementType.none

			# They're HIGH this turn and weren't last turn
			if (
				self.militaryAggressivePostureOf(otherPlayer) >= AggressivePostureType.high > self.lastTurnMilitaryAggressivePosture(otherPlayer)):
				bSendStatement = True
			# They're MEDIUM this turn and were NONE last turn
			elif (self.militaryAggressivePostureOf(otherPlayer) >= AggressivePostureType.medium and
			      self.lastTurnMilitaryAggressivePosture(otherPlayer) <= AggressivePostureType.none):
				bSendStatement = True

			# We're working together, so don't worry about it
			if self.isDeclarationOfFriendshipAcceptedBy(otherPlayer):
				return DiplomaticStatementType.none

			# Check other player status
			for thirdPlayer in simulation.players:
				if not thirdPlayer.isHuman() and not thirdPlayer.isMajorAI():
					continue

				if thirdPlayer == self.player or thirdPlayer == otherPlayer:
					continue

				if not thirdPlayer.isAlive():
					continue

				if not self.hasMetWith(thirdPlayer):
					continue

				# Are we already at war with the same player?
				if self.isAtWarWith(thirdPlayer) and otherPlayer.isAtWarWith(thirdPlayer):
					return DiplomaticStatementType.none

				# Are they at war with anyone we're neighbors with?
				if self.proximityTo(thirdPlayer) == PlayerProximityType.neighbors and \
					otherPlayer.isAtWarWith(thirdPlayer):
					return DiplomaticStatementType.none

			if bSendStatement:
				tempStatement = DiplomaticStatementType.aggressiveMilitaryWarning  # DIPLO_STATEMENT_AGGRESSIVE_MILITARY_WARNING
				turnsBetweenStatements: int = 40

				if self.playerDict.numberOfTurnsSinceStatementSent(otherPlayer, tempStatement) >= turnsBetweenStatements:
					statement = tempStatement

		return statement

	def wasResurrectedBy(self, otherPlayer) -> bool:
		return self.playerDict.resurrectedOnTurnBy(otherPlayer) != -1

	def doExpansionWarningStatementTowards(self, otherPlayer, statement: DiplomaticStatementType, simulation) -> DiplomaticStatementType:
		"""Possible Contact Statement"""
		# Comment on aggressive expansion
		if statement == DiplomaticStatementType.none:
			sendStatement: bool = False
			if (otherPlayer.turnsSinceSettledLastCity(simulation) < 10 and
				not self.everMadeExpansionPromiseTowards(otherPlayer) and
				not self.isPlayerMadeExpansionPromiseTowards(otherPlayer) and
				not self.isPlayerIgnoredExpansionPromiseTowards(otherPlayer) and
				not self.isPlayerBrokenExpansionPromiseTowards(otherPlayer)):

				# We're fiercely opposed to their expansion
				if self.landDisputeLevelWith(otherPlayer) >= DisputeLevelType.fierce:
					sendStatement = True

				# Have a strong dispute over land now, and didn't last turn
				elif self.landDisputeLevelWith(otherPlayer) >= DisputeLevelType.strong > self.lastTurnLandDisputeLevelWith(otherPlayer):
					if self.expansionAggressivePostureTowards(otherPlayer) >= AggressivePostureType.medium:
						sendStatement = True

			if sendStatement:
				tempStatement = DiplomaticStatementType.expansionWarning
				turnsBetweenStatements = 50  # EXPANSION_PROMISE_TURNS_EFFECTIVE() * getGameSpeedInfo().getOpinionDurationPercent()) / 100

				if self.playerDict.numberOfTurnsSinceStatementSent(otherPlayer, tempStatement) >= turnsBetweenStatements:
					statement = tempStatement

		return statement

	def doExpansionBrokenPromiseStatementTowards(self, otherPlayer, statement: DiplomaticStatementType) -> DiplomaticStatementType:
		"""Possible Contact Statement"""
		# Tell the player he broke a promise
		if statement == DiplomaticStatementType.none:
			if self.isPlayerBrokenExpansionPromiseTowards(otherPlayer):
				tempStatement = DiplomaticStatementType.expansionBrokenPromise  # DIPLO_STATEMENT_EXPANSION_BROKEN_PROMISE
				turnsBetweenStatements = 9999  # MAX_TURNS_SAFE_ESTIMATE

				if self.playerDict.numberOfTurnsSinceStatementSent(otherPlayer, tempStatement) >= turnsBetweenStatements:
					statement = tempStatement

		return statement

	def doPlotBuyingWarningStatementTowards(self, otherPlayer, statement: DiplomaticStatementType) -> DiplomaticStatementType:
		"""Possible Contact Statement"""
		# Comment on aggressive Plot Buying
		if statement == DiplomaticStatementType.none:
			sendStatement: bool = False
			if (not self.everMadeBorderPromiseTowards(otherPlayer) and
				not self.isPlayerMadeBorderPromiseTowards(otherPlayer) and
				not self.isPlayerBrokenBorderPromiseTowards(otherPlayer) and
				not self.isPlayerIgnoredBorderPromiseTowards(otherPlayer)):

				if self.landDisputeLevelWith(otherPlayer) >= DisputeLevelType.strong:
					# We've spotten them buying up Plots
					if self.plotBuyingAggressivePostureTowards(otherPlayer) >= AggressivePostureType.low:
						sendStatement = True

			if sendStatement:
				tempStatement: DiplomaticStatementType = DiplomaticStatementType.plotBuyingWarning  # DIPLO_STATEMENT_PLOT_BUYING_WARNING
				turnsBetweenStatements: int = 50  # BORDER_PROMISE_TURNS_EFFECTIVE * getGameSpeedInfo().getOpinionDurationPercent()) / 100

				if self.playerDict.numberOfTurnsSinceStatementSent(otherPlayer, tempStatement) >= turnsBetweenStatements:
					statement = tempStatement

		return statement

	def doPlotBuyingBrokenPromiseStatementTowards(self, otherPlayer, statement: DiplomaticStatementType) -> DiplomaticStatementType:
		"""Possible Contact Statement"""
		# Tell the player he broke a promise
		if statement == DiplomaticStatementType.none:
			if self.isPlayerBrokenBorderPromiseTowards(otherPlayer):
				tempStatement: DiplomaticStatementType = DiplomaticStatementType.plotBuyingBrokenPromise  # DIPLO_STATEMENT_PLOT_BUYING_BROKEN_PROMISE
				turnsBetweenStatements: int = 9999  # MAX_TURNS_SAFE_ESTIMATE

				if self.playerDict.numberOfTurnsSinceStatementSent(otherPlayer, tempStatement) >= turnsBetweenStatements:
					statement = tempStatement

		return statement

	def doDeclarationOfFriendshipStatementTowards(self, otherPlayer, statement: DiplomaticStatementType, simulation) -> DiplomaticStatementType:
		"""Possible Contact Statement"""
		if statement == DiplomaticStatementType.none:
			# Have we already made the agreement?
			if not self.isDeclarationOfFriendshipAcceptedBy(otherPlayer):
				if self.isDeclarationOfFriendshipAcceptableBy(otherPlayer):
					tempStatement: DiplomaticStatementType = DiplomaticStatementType.workWithUs  # DIPLO_STATEMENT_WORK_WITH_US

					if (self.playerDict.numberOfTurnsSinceStatementSent(otherPlayer, tempStatement) >= 60 and
						self.playerDict.numberOfTurnsSinceStatementSent(otherPlayer, DiplomaticStatementType.workWithUsRandFailed) >= 10):
							sendStatement: bool = True

							# Chance we don't actually send the message (don't want full predictability)
							if not Tests.are_running and 50 < random.randint(0, 100):  # Diplomacy AI: rand roll to see if we ask to work with a player
								sendStatement = False

							if sendStatement:
								statement = tempStatement
							# Add this statement to the log, so we don't evaluate it again until 10 turns has come back around
							else:
								self.playerDict.doAddNewStatementToDiploLog(otherPlayer, DiplomaticStatementType.workWithUsRandFailed, simulation.currentTurn)

		return statement

	def isTooEarlyForDeclarationOfFriendshipTowards(self, otherPlayer) -> bool:
		"""AI won't agree to a DoF until they've known a player for at least a few turns"""
		doFBuffer = 20  # DOF_TURN_BUFFER

		if self.playerDict.turnsSinceMeetingWith(otherPlayer) < doFBuffer:
			return True

		return False

	def doDenounceStatementTowards(self, otherPlayer, statement: DiplomaticStatementType, simulation) -> DiplomaticStatementType:
		"""Possible Contact Statement"""
		if statement == DiplomaticStatementType.none:
			if self.isDenounceAcceptableTowards(otherPlayer, bias=False, simulation=simulation):
				tempStatement: DiplomaticStatementType = DiplomaticStatementType.denounce

				if (self.playerDict.numberOfTurnsSinceStatementSent(otherPlayer, tempStatement) >= 60 and
					self.playerDict.numberOfTurnsSinceStatementSent(otherPlayer, DiplomaticStatementType.denounceRandFailed) >= 10):
					sendStatement: bool = True

					# 1 in 2 chance we don't actually send the message (don't want full predictability)
					if not Tests.are_running and 50 < random.randint(0, 100):  # Diplomacy AI: rand roll to see if we ask to work with a player
						sendStatement = False

					if sendStatement:
						statement = tempStatement
					# Add this statement to the log, so we don't evaluate it again until time has passed
					else:
						self.playerDict.doAddNewStatementToDiploLog(otherPlayer, DiplomaticStatementType.denounceRandFailed, simulation.currentTurn)

		return statement

	def isDenounceAcceptableTowards(self, otherPlayer, bias: bool, simulation) -> bool:
		"""Does this player feel it's time to denounce otherPlayer?"""
		# Can't denounce with a civ you're at war with
		if self.player.isAtWarWith(otherPlayer):  # or GC.getGame().isOption(GAMEOPTION_ALWAYS_WAR))
			return False

		# If we've already denounced, it's no good
		if self.isDenouncedPlayer(otherPlayer):
			return False

		# If we're friends, return false - this is handled in IsDenounceFriendAcceptable
		if self.isDeclarationOfFriendshipAcceptedBy(otherPlayer):
			return False

		weight: int = self.denounceWeight(otherPlayer, bias, simulation)
		if weight >= 18:
			return True

		return False

	def denounceWeight(self, otherPlayer, bias: bool, simulation) -> int:
		iWeight: int = 0

		# Base Personality value ranges from 0 to 10(ish)
		iWeight += self.playerDict.denounceWillingness()

		approach: MajorPlayerApproachType = self.majorCivApproachTowards(otherPlayer, hideTrueFeelings=False)

		# Hostile: Bonus
		if approach == MajorPlayerApproachType.hostile:
			iWeight += 6
		# Afraid: Penalty
		elif approach == MajorPlayerApproachType.afraid:
			iWeight += -10

		opinion: MajorCivOpinionType = self.majorCivOpinion(otherPlayer)

		# Unforgivable: Big Bonus
		if opinion == MajorCivOpinionType.unforgivable:
			iWeight += 10
		# Enemy: Bonus
		elif opinion == MajorCivOpinionType.enemy:
			iWeight += 5
		# Competitor: Small Bonus
		elif opinion == MajorCivOpinionType.competitor:
			iWeight += 2
		# Good Relations: Penalty
		elif opinion == MajorCivOpinionType.favorable:
			iWeight += -10
		elif opinion == MajorCivOpinionType.friend:
			iWeight += -25
		elif opinion == MajorCivOpinionType.ally:
			iWeight += -50

		# We are at war
		if self.isAtWarWith(otherPlayer):
			iWeight += 2

		# Look for other players we like or are strong, and add a bonus if they've denounced this guy, or are at war with him
		for thirdPlayer in simulation.players:
			if not thirdPlayer.isHuman() and not thirdPlayer.isMajorAI():
				continue

			if thirdPlayer == self.player or thirdPlayer == otherPlayer:
				continue

			if not thirdPlayer.isAlive():
				continue

			if not self.player.hasMetWith(thirdPlayer):
				continue

			if not otherPlayer.hasMetWith(thirdPlayer):
				continue

			thirdPlayerDiplomacyAI = thirdPlayer.diplomacyAI

			# War or Denounced otherPlayer, so we know eThirdParty doesn't like him
			if not thirdPlayerDiplomacyAI.isDenouncedPlayer(otherPlayer):  # & & !pThirdPartyDiplo->IsAtWar(otherPlayer))
				continue

			# We must not be on bad relations with eThirdParty
			if self.majorCivOpinion(thirdPlayer) <= MajorCivOpinionType.competitor:
				continue

			# If we're hostile or planning war, we don't care about this guy
			thirdPartyApproach: MajorPlayerApproachType = self.majorCivApproachTowards(thirdPlayer, hideTrueFeelings=False)
			if thirdPartyApproach == MajorPlayerApproachType.hostile or thirdPartyApproach == MajorPlayerApproachType.war:
				continue

			# We 're close to this guy who's at war - want to gain favor
			if self.player.proximityTo(thirdPlayer) == PlayerProximityType.neighbors:
				iWeight += 1

			# Are they strong?
			comparedStrength: StrengthType = self.playerDict.militaryStrengthComparedToUsOf(thirdPlayer)
			if comparedStrength > StrengthType.average:
				# Ex: if they're immense, this will add 3 to the weight
				iWeight += (comparedStrength.value - StrengthType.average.value)

			# Are we friends with them?
			if self.isDeclarationOfFriendshipAcceptedBy(thirdPlayer):
				iWeight += 4

		# Rand: 0 - 5
		iWeight += 0 if Tests.are_running else random.randint(0, 5)  # Diplomacy AI: Rand for whether AI wants to work with player

		# Used when friends are asking us to denounce someone
		if bias:
			iWeight += 3

		return iWeight

	def doEmbassyExchangeWith(self, otherPlayer, statement: DiplomaticStatementType, deal: DiplomaticDeal, simulation) -> DiplomaticStatementType:
		"""Possible Contact Statement - Embassy Exchange"""
		if statement == DiplomaticStatementType.none:
			# Can both sides open an embassy
			if (deal.isPossibleToTradeItem(self.player, otherPlayer, DiplomaticDealItemType.allowEmbassy, simulation=simulation) and
				deal.isPossibleToTradeItem(otherPlayer, self.player, DiplomaticDealItemType.allowEmbassy, simulation=simulation)):

				# Does this guy want to exchange embassies?
				if self.isEmbassyExchangeAcceptable(otherPlayer):
					tempStatement: DiplomaticStatementType = DiplomaticStatementType.embassyExchange
					turnsBetweenStatements: int = 20

					if (self.playerDict.numberOfTurnsSinceStatementSent(otherPlayer, tempStatement) >= turnsBetweenStatements) and \
						self.playerDict.numberOfTurnsSinceStatementSent(otherPlayer, DiplomaticStatementType.embassyOffer) >= 10:
						sendStatement: bool = False

						# AI
						if not otherPlayer.isHuman():
							if otherPlayer.diplomacyAI.isEmbassyExchangeAcceptable(self.player):
								sendStatement = True
						# Human
						else:
							sendStatement = True

						# 1 in 2 chance we don't actually send the message (don't want full predictability)
						if not Tests.are_running and 50 < random.randint(0, 100):  # Diplomacy AI: rand roll to see if we ask to exchange embassies
							sendStatement = False

						if sendStatement:
							deal.addAllowEmbassy(self.player, simulation)
							deal.addAllowEmbassy(otherPlayer, simulation)

							statement = tempStatement
						else:
							self.playerDict.doAddNewStatementToDiploLog(otherPlayer, tempStatement, simulation.currentTurn)

		return statement

	def doEmbassyOfferTowards(self, otherPlayer, statement: DiplomaticStatementType, deal: DiplomaticDeal, simulation) -> DiplomaticStatementType:
		"""Possible Contact Statement - Embassy"""
		if statement == DiplomaticStatementType.none:
			if self.player.dealAI.makeOfferForEmbassyTowards(otherPlayer, deal, simulation=simulation):
				tempStatement: DiplomaticStatementType = DiplomaticStatementType.embassyOffer
				turnsBetweenStatements: int = 20

				if ((self.playerDict.numberOfTurnsSinceStatementSent(otherPlayer, tempStatement) >= turnsBetweenStatements) and
					self.playerDict.numberOfTurnsSinceStatementSent(otherPlayer, DiplomaticStatementType.embassyExchange) >= 10):
					statement = tempStatement
				else:
					# Clear out the deal if we don't want to offer it so that it's not tainted for the next trade
					# possibility we look at
					deal.clearItems()

		return statement

	def doOpenBordersExchangeWith(self, otherPlayer, statement: DiplomaticStatementType, deal: DiplomaticDeal, simulation) -> DiplomaticStatementType:
		"""Possible Contact Statement - Open Borders Exchange"""
		if statement == DiplomaticStatementType.none:
			duration: int = 30  # GC.getGame().GetDealDuration()

			# Can both sides trade OB?
			if (deal.isPossibleToTradeItem(self.player, otherPlayer, DiplomaticDealItemType.openBorders, duration, simulation=simulation) and
				deal.isPossibleToTradeItem(otherPlayer, self.player, DiplomaticDealItemType.openBorders, duration, simulation=simulation)):
				# Does this guy want to exchange OB?
				if self.isOpenBordersExchangeAcceptableWith(otherPlayer):
					tempStatement: DiplomaticStatementType = DiplomaticStatementType.openBordersExchange
					turnsBetweenStatements: int = 20

					if self.playerDict.numberOfTurnsSinceStatementSent(otherPlayer, tempStatement) >= turnsBetweenStatements:
						sendStatement: bool = False

						# AI
						if not otherPlayer.isHuman():
							if otherPlayer.diplomacyAI.isOpenBordersExchangeAcceptableWith(self.player):
								sendStatement = True
						# Human
						else:
							sendStatement = True

						# 1 in 2 chance we don't actually send the message (don't want full predictability)
						if not Tests.are_running and 50 < random.randint(0, 100):  # Diplomacy AI: rand roll to see if we ask to exchange open borders
							sendStatement = False

						if sendStatement:
							# OB on each side
							deal.addOpenBorders(self.player, duration, simulation)
							deal.addOpenBorders(otherPlayer, duration, simulation)

							statement = tempStatement
						# Add this statement to the log, so we don't evaluate it again until 20 turns has come back around
						else:
							self.playerDict.doAddNewStatementToDiploLog(otherPlayer, tempStatement, simulation.currentTurn)

		return statement

	def doOpenBordersOfferTowards(self, otherPlayer, statement: DiplomaticStatementType, deal: DiplomaticDeal, simulation) -> DiplomaticStatementType:
		"""Possible Contact Statement - Open Borders"""
		if statement == DiplomaticStatementType.none:
			if self.player.dealAI.isMakeOfferForOpenBorders(otherPlayer, deal, simulation=simulation):
				tempStatement: DiplomaticStatementType = DiplomaticStatementType.openBordersOffer
				turnsBetweenStatements: int = 20

				if self.playerDict.numberOfTurnsSinceStatementSent(otherPlayer, tempStatement) >= turnsBetweenStatements:
					statement = tempStatement
			else:
				# Clear out the deal if we don't want to offer it so that it's not tainted for the next trade possibility we look at
				deal.clearItems()

		return statement

	def doResearchAgreementOfferTowards(self, otherPlayer, statement: DiplomaticStatementType, deal: DiplomaticDeal, simulation) -> DiplomaticStatementType:
		"""Possible Contact Statement - Research Agreement Offer"""
		if statement == DiplomaticStatementType.none:
			if self.isCanMakeResearchAgreementRightNow(otherPlayer, simulation):
				if self.player.dealAI.isMakeOfferForResearchAgreement(otherPlayer, deal):
					tempStatement: DiplomaticStatementType = DiplomaticStatementType.researchAgreementOffer
					turnsBetweenStatements: int = 20

					if self.playerDict.numberOfTurnsSinceStatementSent(otherPlayer, tempStatement) >= turnsBetweenStatements:
						statement = tempStatement
					else:
						# Clear out the deal if we don't want to offer it so that it's not tainted for the next trade possibility we look at
						deal.clearItems()

		return statement

	def isCanMakeResearchAgreementRightNow(self, otherPlayer, simulation) -> bool:
		"""Are we able to make a Research Agreement with otherPlayer right now?"""
		# Either side already have all techs?
		if self.player.techs.hasResearchedAllTechs() or otherPlayer.techs.hasResearchedAllTechs():
			return False

		# We don't want a RA with this guy
		if not self.isWantsResearchAgreementWith(otherPlayer):
			return False

		# Already have a RA?
		if self.player.isHasResearchAgreementWith(otherPlayer):
			return False

		# Can we have a research agreement right now?
		if (not self.player.isResearchAgreementTradingAllowedWith(otherPlayer) or
			not otherPlayer.isResearchAgreementTradingAllowedWith(self.player)):
			return False

		goldAmount = simulation.gameDeals.tradeItemGoldCost(DiplomaticDealItemType.researchAgreement, self.player, otherPlayer, simulation)

		# We don't have enough Gold
		if self.player.treasury.value() < goldAmount:
			return False

		# They don't have enough Gold
		if otherPlayer.treasury.value() < goldAmount:
			return False

		return True

	def isWantsResearchAgreementWith(self, otherPlayer) -> bool:
		"""Does this AI want to make a Research Agreement with otherPlayer?"""
		return self.playerDict.isWantsResearchAgreementWith(otherPlayer)

	def doAddWantsResearchAgreementWith(self, otherPlayer, simulation):
		"""AI wants a Research Agreement with otherPlayer, so handle everything that means"""
		self.playerDict.updateWantsResearchAgreementWith(otherPlayer, True)

		# Start saving the Gold
		goldAmount = simulation.gameDeals.tradeItemGoldCost(DiplomaticDealItemType.researchAgreement, self.player, otherPlayer, simulation)
		self.player.economicAI.startSavingForPurchase(PurchaseType.majorCivTrade, goldAmount, priority=1)

		logging.info(f'{self.player} wants research agreement with {otherPlayer}')

	def doCancelWantsResearchAgreementWith(self, otherPlayer, simulation):
		"""AI wants to cancel a Research Agreement with otherPlayer, so handle everything that means"""
		self.playerDict.updateWantsResearchAgreementWith(otherPlayer, False)

		self.player.economicAI.cancelSaveForPurchase(PurchaseType.majorCivTrade)

	def doHostileStatementTowards(self, otherPlayer, statement: DiplomaticStatementType, simulation) -> DiplomaticStatementType:
		"""Possible Contact Statement"""
		if statement == DiplomaticStatementType.none:
			approach: MajorPlayerApproachType = self.majorCivApproachTowards(otherPlayer, hideTrueFeelings=True)
			if approach == MajorPlayerApproachType.hostile:
				# If we've made peace recently, don't go mouthing off right away
				peaceTreatyTurn = self.playerDict.turnMadePeaceTreatyWith(otherPlayer)
				if peaceTreatyTurn != -1:
					turnsSincePeace = simulation.currentTurn - peaceTreatyTurn
					if turnsSincePeace < 25:  # TURNS_SINCE_PEACE_WEIGHT_DAMPENER
						return DiplomaticStatementType.none

				tempStatement: DiplomaticStatementType = DiplomaticStatementType.insult  # DIPLO_STATEMENT_INSULT
				turnsBetweenStatements = 35

				if self.playerDict.numberOfTurnsSinceStatementSent(otherPlayer, tempStatement) >= turnsBetweenStatements:
					statement = tempStatement

		return statement

	def doAfraidStatementTowards(self, otherPlayer, statement: DiplomaticStatementType) -> DiplomaticStatementType:
		"""Possible Contact Statement"""
		if statement == DiplomaticStatementType.none:
			approach: MajorPlayerApproachType = self.majorCivApproachTowards(otherPlayer, hideTrueFeelings=True)
			if approach == MajorPlayerApproachType.afraid:
				tempStatement: DiplomaticStatementType = DiplomaticStatementType.bootKissing  # DIPLO_STATEMENT_BOOT_KISSING
				turnsBetweenStatements: int = 35

				if self.playerDict.numberOfTurnsSinceStatementSent(otherPlayer, tempStatement) >= turnsBetweenStatements:
					statement = tempStatement

		return statement

	def doWarmongerStatementTowards(self, otherPlayer, statement: DiplomaticStatementType, simulation) -> DiplomaticStatementType:
		"""Possible Contact Statement"""
		if statement == DiplomaticStatementType.none:
			warmongerThreatValue = self.playerDict.warmongerThreatOf(otherPlayer)
			if warmongerThreatValue >= MilitaryThreatType.severe:
				sendStatement: bool = True

				# Don't send statement, if we're going for conquest ourselves
				if self.player.isGoingForWorldConquest():
					sendStatement = False

				# 2 in 3 chance we don't actually send the message (don't want to bombard the player from all sides)
				if not Tests.are_running and 33 < random.randint(0, 100):  # Diplomacy AI: rand roll to see if we warn a player about being a warmonger"))
					sendStatement = False

				tempStatement: DiplomaticStatementType = DiplomaticStatementType.warmonger
				turnsBetweenStatements: int = 9999  # MAX_TURNS_SAFE_ESTIMATE

				if sendStatement:
					if self.playerDict.numberOfTurnsSinceStatementSent(otherPlayer, tempStatement) >= turnsBetweenStatements:
						statement = tempStatement
					# Add this statement to the log, so we don't evaluate it again next turn
				else:
					self.playerDict.doAddNewStatementToDiploLog(otherPlayer, tempStatement, simulation.currentTurn)

		return statement

	def doMinorCivCompetitionStatement(self, otherPlayer, statement: DiplomaticStatementType, ignoreTurnsBetweenLimit: bool=True, simulation=None) -> (DiplomaticStatementType, object):
		"""Possible Contact Statement"""
		if simulation is None:
			raise Exception('simulation must not be none')

		minorPlayer = None

		if statement == DiplomaticStatementType.none:
			if self.minorCivDisputeLevelWith(otherPlayer) >= DisputeLevelType.strong:
				tempStatement: DiplomaticStatementType = DiplomaticStatementType.minorCivCompetition
				turnsBetweenStatements: int = 9999  # MAX_TURNS_SAFE_ESTIMATE

				if self.playerDict.numberOfTurnsSinceStatementSent(otherPlayer, tempStatement) >= turnsBetweenStatements or ignoreTurnsBetweenLimit:
					# Find a city state we're upset over
					for loopPlayer in simulation.players:
						if not loopPlayer.isCityState():
							continue

						if not loopPlayer.isAlive():
							continue

						if not self.player.hasMetWith(loopPlayer):
							continue

						if not otherPlayer.hasMetWith(loopPlayer):
							continue

						# We have a PtP with this minor
						if loopPlayer.minorCivAI.isProtectedByMajor(self.player):
							if loopPlayer.minorCivAI.isAlly(otherPlayer):
								minorPlayer = loopPlayer
								break
							elif loopPlayer.minorCivAI.isFriends(otherPlayer):
								minorPlayer = loopPlayer
								break

					# Don't change the statement unless we found a minor to complain about
					if minorPlayer is not None:
						statement = tempStatement

		return statement, minorPlayer

	def doIdeologicalStatementTowards(self, otherPlayer, statement: DiplomaticStatementType) -> DiplomaticStatementType:
		# turnsBetweenStatements: int = 9999  # MAX_TURNS_SAFE_ESTIMATE
		# if statement == DiplomaticStatementType.none:
		# 	sendStatement: bool = False
		#
		# 	if self.player.government.currentGovernment() != otherPlayer.government.currentGovernment():
		# fixme - not implemented

		return statement

	def doUpdateOtherPlayerWarDamageLevel(self, simulation):
		"""Updates what is our guess as to amount of war damage a player has suffered to another player"""
		# Loop through all (known) Majors
		for loopPlayer in simulation.players:
			if not loopPlayer.isMajorAI() and not loopPlayer.isHuman():
				continue

			if not self.isValid(loopPlayer):
				continue

			# Now loop through every player HE knows
			for thirdPlayer in simulation.players:
				if not thirdPlayer.isMajorAI() and not thirdPlayer.isHuman():
					continue

				# Don't compare a player to himself
				if loopPlayer == thirdPlayer:
					continue

				# Do both we and the guy we're looking about know the third guy?
				if self.isValid(thirdPlayer) and loopPlayer.diplomacyAI.isValid(thirdPlayer):
					# At War?
					if loopPlayer.isAtWarWith(thirdPlayer):
						valueLost = self.otherPlayerWarValueLostBy(loopPlayer, thirdPlayer)

						# Calculate the value of what we have currently
						currentValue = 0

						# City value
						if loopPlayer.numberOfCities(simulation) > 0:
							for loopCity in simulation.citiesOf(loopPlayer):
								currentValue += loopCity.population() * 150  # WAR_DAMAGE_LEVEL_INVOLVED_CITY_POP_MULTIPLIER
								if loopCity.isOriginalCapital():  # anybody's
									currentValue *= 3
									currentValue /= 2

						# Prevents divide by 0
						currentValue = max(1, currentValue)

						valueLostRatio = valueLost * 100 / currentValue

						if valueLostRatio >= 50:  # WAR_DAMAGE_LEVEL_THRESHOLD_CRIPPLED
							warDamageLevel = WarDamageLevelType.crippled  # WAR_DAMAGE_LEVEL_CRIPPLED
						elif valueLostRatio >= 35:  # WAR_DAMAGE_LEVEL_THRESHOLD_SERIOUS
							warDamageLevel = WarDamageLevelType.serious  # WAR_DAMAGE_LEVEL_SERIOUS
						elif valueLostRatio >= 20:  # WAR_DAMAGE_LEVEL_THRESHOLD_MAJOR
							warDamageLevel = WarDamageLevelType.major  # WAR_DAMAGE_LEVEL_MAJOR
						elif valueLostRatio >= 10:  # WAR_DAMAGE_LEVEL_THRESHOLD_MINOR
							warDamageLevel = WarDamageLevelType.minor  # WAR_DAMAGE_LEVEL_MINOR
						else:
							warDamageLevel = WarDamageLevelType.none  # WAR_DAMAGE_LEVEL_NONE
					else:
						warDamageLevel = WarDamageLevelType.none  # WAR_DAMAGE_LEVEL_NONE

					self.playerDict.updateOtherPlayerWarDamageLevelBetween(loopPlayer, thirdPlayer, warDamageLevel)

		return

	def doUpdateEstimateOtherPlayerLandDisputeLevels(self, simulation):
		"""Updates what is our guess as to the levels of Dispute between other players over Land is"""
		# Cache world average # of Cities to compare each player we know against later
		worldAverageNumCities: int = 0
		numPlayers: int = 0
		for loopPlayer in simulation.players:
			if not loopPlayer.isMajorAI() and not loopPlayer.isHuman():
				continue

			if loopPlayer.isAlive():
				worldAverageNumCities += loopPlayer.numberOfCities(simulation)
				numPlayers += 1

		worldAverageNumCities *= 100
		worldAverageNumCities /= numPlayers

		# Loop through all (known) Majors
		for loopPlayer in simulation.players:
			if not loopPlayer.isMajorAI() and not loopPlayer.isHuman():
				continue

			if self.isValid(loopPlayer):
				# Before looking at anyone else, try to guess how much this player values Expansion based on how many Cities he has relative the rest of the world
				cityRatio = loopPlayer.numberOfCities(simulation) * 10000
				cityRatio /= worldAverageNumCities 	# 100 means 1 City, which is why we multiplied by 10000 on the line above... 10000/100 = 100

				if cityRatio >= 200:  # LAND_DISPUTE_CITY_RATIO_EXPANSION_GUESS_10())
					expansionFlavorGuess = 10
				elif cityRatio >= 180:  # LAND_DISPUTE_CITY_RATIO_EXPANSION_GUESS_9())
					expansionFlavorGuess = 9
				elif cityRatio >= 160:  # LAND_DISPUTE_CITY_RATIO_EXPANSION_GUESS_8())
					expansionFlavorGuess = 8
				elif cityRatio >= 130:  # LAND_DISPUTE_CITY_RATIO_EXPANSION_GUESS_7())
					expansionFlavorGuess = 7
				elif cityRatio >= 110:  # LAND_DISPUTE_CITY_RATIO_EXPANSION_GUESS_6())
					expansionFlavorGuess = 6
				elif cityRatio >= 90:  # LAND_DISPUTE_CITY_RATIO_EXPANSION_GUESS_5())
					expansionFlavorGuess = 5
				elif cityRatio >= 80:  # LAND_DISPUTE_CITY_RATIO_EXPANSION_GUESS_4())
					expansionFlavorGuess = 4
				elif cityRatio >= 55:  # LAND_DISPUTE_CITY_RATIO_EXPANSION_GUESS_3())
					expansionFlavorGuess = 3
				elif cityRatio >= 30:  # LAND_DISPUTE_CITY_RATIO_EXPANSION_GUESS_2())
					expansionFlavorGuess = 2
				else:
					expansionFlavorGuess = 1

				# LogOtherPlayerExpansionGuess(eLoopPlayer, iExpansionFlavorGuess)
				logging.info(f'{self.player} is guessing that {loopPlayer} is {expansionFlavorGuess}')

				# Now loop through every player HE knows
				for thirdPlayer in simulation.players:
					if not thirdPlayer.isMajorAI() and not thirdPlayer.isHuman():
						continue

					# Don't compare a player to himself
					if loopPlayer == thirdPlayer:
						continue

					# Do both we and the guy we're looking about know the third guy?
					if self.isValid(thirdPlayer) and loopPlayer.diplomacyAI.isValid(thirdPlayer):

							disputeLevel = DisputeLevelType.none
							landDisputeWeight = 0

							# Look at our Proximity to the other Player
							proximity = loopPlayer.proximityTo(thirdPlayer)

							if proximity ==  PlayerProximityType.distant:
								landDisputeWeight += 0  # LAND_DISPUTE_DISTANT
							elif proximity == PlayerProximityType.far:
								landDisputeWeight += 5  # LAND_DISPUTE_FAR
							elif proximity == PlayerProximityType.close:
								landDisputeWeight += 20  # LAND_DISPUTE_CLOSE
							elif proximity == PlayerProximityType.neighbors:
								landDisputeWeight += 40  # LAND_DISPUTE_NEIGHBORS

							# Is the player already cramped?  If so, multiply our current Weight by 1.5x
							if loopPlayer.isCramped():
								landDisputeWeight *= 0  # LAND_DISPUTE_CRAMPED_MULTIPLIER
								landDisputeWeight /= 100

							# Add weight for Player's estimated EXPANSION preference
							landDisputeWeight *= expansionFlavorGuess

							# Max Value (Cramped, Neighbors) - 60
							# EXPANSION 10	: 600
							# EXPANSION 5		: 300
							# EXPANSION 1		: 60

							# "Typical" Value (Not Cramped, Close) - 20
							# EXPANSION 10	: 200
							# EXPANSION 5		: 100
							# EXPANSION 1		: 20

							# Now See what our new Dispute Level should be
							if landDisputeWeight >= 300:  # LAND_DISPUTE_FIERCE_THRESHOLD())
								disputeLevel = DisputeLevelType.fierce  # DISPUTE_LEVEL_FIERCE
							elif landDisputeWeight >= 200:  # LAND_DISPUTE_STRONG_THRESHOLD())
								disputeLevel = DisputeLevelType.strong  # DISPUTE_LEVEL_STRONG
							elif landDisputeWeight >= 100:  # LAND_DISPUTE_WEAK_THRESHOLD())
								disputeLevel = DisputeLevelType.weak  # DISPUTE_LEVEL_WEAK

							# Actually set the Level
							self.playerDict.updateEstimateOtherPlayerLandDisputeLevelBetween(loopPlayer, thirdPlayer, disputeLevel)

		return

	def doUpdateEstimateOtherPlayerVictoryDisputeLevels(self, simulation):
		"""Updates what is our guess as to the levels of Dispute between other players over Victory is"""
		# Loop through all (known) Majors
		for loopPlayer in simulation.players:
			if not loopPlayer.isMajorAI() and not loopPlayer.isHuman():
				continue

			if not self.isValid(loopPlayer):
				continue

			# Now loop through every player HE knows
			for thirdPlayer in simulation.players:
				if not thirdPlayer.isMajorAI() and not thirdPlayer.isHuman():
					continue

				# Don't compare a player to himself
				if loopPlayer == thirdPlayer:
					continue

				# Do both we and the guy we're looking about know the third guy?
				if self.isValid(thirdPlayer) and loopPlayer.diplomacyAI.isValid(thirdPlayer):
					disputeLevel = DisputeLevelType.none
					victoryDisputeWeight: int = 0

					# Do we think their Grand Strategies match?
					if self.player.grandStrategyAI.guessOtherPlayerActiveGrandStrategyOf(loopPlayer) == self.player.grandStrategyAI.guessOtherPlayerActiveGrandStrategyOf(thirdPlayer):
						confidence: GuessConfidenceType = self.player.grandStrategyAI.guessOtherPlayerActiveGrandStrategyConfidenceOf(loopPlayer)
						if confidence == GuessConfidenceType.positive:
							victoryDisputeWeight += 7  # VICTORY_DISPUTE_OTHER_PLAYER_GRAND_STRATEGY_MATCH_POSITIVE
						elif confidence == GuessConfidenceType.likely:
							victoryDisputeWeight += 5  # VICTORY_DISPUTE_OTHER_PLAYER_GRAND_STRATEGY_MATCH_LIKELY
						elif confidence == GuessConfidenceType.unsure:
							victoryDisputeWeight += 3  # VICTORY_DISPUTE_OTHER_PLAYER_GRAND_STRATEGY_MATCH_UNSURE

						confidence: GuessConfidenceType = self.player.grandStrategyAI.guessOtherPlayerActiveGrandStrategyConfidenceOf(thirdPlayer)
						if confidence == GuessConfidenceType.positive:
							victoryDisputeWeight += 7  # VICTORY_DISPUTE_OTHER_PLAYER_GRAND_STRATEGY_MATCH_POSITIVE
						elif confidence == GuessConfidenceType.likely:
							victoryDisputeWeight += 5  # VICTORY_DISPUTE_OTHER_PLAYER_GRAND_STRATEGY_MATCH_LIKELY
						elif confidence == GuessConfidenceType.unsure:
							victoryDisputeWeight += 3  # VICTORY_DISPUTE_OTHER_PLAYER_GRAND_STRATEGY_MATCH_UNSURE

						# Add weight for Player's competitiveness: assume default (5),
						# since we can't actually know how competitive a player is
						victoryDisputeWeight *= 5  # DEFAULT_FLAVOR_VALUE

						# Example Victory Dispute Weights
						# Positive on Both:		70
						# Positive, Unsure:		50
						# Unsure, Unsure:			30

						# Now See what our new Dispute Level should be
						if victoryDisputeWeight >= 70:  # VICTORY_DISPUTE_OTHER_PLAYER_FIERCE_THRESHOLD
							disputeLevel = DisputeLevelType.fierce  # DISPUTE_LEVEL_FIERCE
						elif victoryDisputeWeight >= 50:  # VICTORY_DISPUTE_OTHER_PLAYER_STRONG_THRESHOLD
							disputeLevel = DisputeLevelType.strong  # DISPUTE_LEVEL_STRONG
						elif victoryDisputeWeight >= 30:  # VICTORY_DISPUTE_OTHER_PLAYER_WEAK_THRESHOLD
							disputeLevel = DisputeLevelType.weak  # DISPUTE_LEVEL_WEAK

						# Actually set the Level
						self.playerDict.updateEstimateOtherPlayerVictoryDisputeLevelBetween(loopPlayer, thirdPlayer, disputeLevel)

		return

	def doUpdateEstimateOtherPlayerMilitaryThreats(self, simulation):
		"""Updates what our guess is as to the level of Military Threat one player feels from another"""
		militaryThreat = 0

		# Loop through all (known) Majors
		for loopPlayer in simulation.players:
			if not loopPlayer.isMajorAI() and not loopPlayer.isHuman():
				continue

			if not self.isValid(loopPlayer):
				continue

			playerMilitaryStrength = loopPlayer.militaryMight(simulation)

			# Add in City Defensive Strength
			for loopCity in simulation.citiesOf(loopPlayer):
				cityStrengthMod = loopCity.power(simulation)
				cityStrengthMod *= (loopCity.maxHealthPoints() - loopCity.damage())
				cityStrengthMod /= loopCity.maxHealthPoints()
				cityStrengthMod /= 100
				cityStrengthMod *= 33  # MILITARY_STRENGTH_CITY_MOD
				cityStrengthMod /= 100
				playerMilitaryStrength += (max(cityStrengthMod, 0))

			# Prevent divide by 0
			if playerMilitaryStrength == 0:
				playerMilitaryStrength = 1

			# Now loop through every player HE knows
			for thirdPlayer in simulation.players:
				if not thirdPlayer.isMajorAI() and not thirdPlayer.isHuman():
					continue

				# Don't compare a player to himself
				if loopPlayer == thirdPlayer:
					continue

				# Do both we and the guy we're looking about know the third guy?
				if self.isValid(thirdPlayer) and loopPlayer.diplomacyAI.isValid(thirdPlayer):
					militaryThreatType = MilitaryThreatType.none
					militaryThreatType = 0

					thirdPlayerMilitaryStrength = thirdPlayer.militaryMight(simulation)

					# Example: If another player has double the Military strength of us, the Ratio will be 200
					militaryRatio = thirdPlayerMilitaryStrength * 100 / playerMilitaryStrength  # MILITARY_STRENGTH_RATIO_MULTIPLIER

					militaryThreat += militaryRatio

					# Factor in Friends this player has

					# TBD

					# Factor in distance
					proximityValue = loopPlayer.proximityTo(thirdPlayer)
					if proximityValue == PlayerProximityType.neighbors:
						militaryThreat += 100  # MILITARY_THREAT_NEIGHBORS
					elif proximityValue == PlayerProximityType.close:
						militaryThreat += 40  # MILITARY_THREAT_CLOSE
					elif proximityValue == PlayerProximityType.far:
						militaryThreat += -40  # MILITARY_THREAT_FAR
					elif proximityValue == PlayerProximityType.distant:
						militaryThreat += -100  # MILITARY_THREAT_DISTANT

					# Don't factor in # of players attacked or at war with now if we ARE at war with this guy already
					# Increase threat based on how many Player's we've already seen this guy attack and conquer
					militaryThreat += (self.otherPlayerNumberOfMinorsAttackedBy(thirdPlayer) * 20)  # MILITARY_THREAT_PER_MINOR_ATTACKED
					militaryThreat += (self.otherPlayerNumberOfMinorsConqueredBy(thirdPlayer) * 10)  # MILITARY_THREAT_PER_MINOR_CONQUERED
					militaryThreat += (self.otherPlayerNumberOfMajorsAttackedBy(thirdPlayer) * 40)  # MILITARY_THREAT_PER_MAJOR_ATTACKED
					militaryThreat += (self.otherPlayerNumberOfMajorsConqueredBy(thirdPlayer) * 20)  # MILITARY_THREAT_PER_MAJOR_CONQUERED

					# Reduce the Threat (dramatically) if the player is already at war with other players
					warCount = thirdPlayer.atWarCount()
					if warCount > 0:
						militaryThreat += (-30 * warCount * militaryThreat / 100)  # MILITARY_THREAT_ALREADY_WAR_EACH_PLAYER_MULTIPLIER

					# Now do the final assessment
					if militaryThreat >= 300:  # MILITARY_THREAT_CRITICAL_THRESHOLD
						militaryThreatType = MilitaryThreatType.critical
					elif militaryThreat >= 220:  # MILITARY_THREAT_SEVERE_THRESHOLD
						militaryThreatType = MilitaryThreatType.severe
					elif militaryThreat >= 170:  # MILITARY_THREAT_MAJOR_THRESHOLD
						militaryThreatType = MilitaryThreatType.major
					elif militaryThreat >= 100:  # MILITARY_THREAT_MINOR_THRESHOLD
						militaryThreatType = MilitaryThreatType.minor

					# Set the Threat
					self.playerDict.updateEstimateOtherPlayerMilitaryThreatBetween(loopPlayer, thirdPlayer, militaryThreatType)

		return

	def doEstimateOtherPlayerOpinions(self, simulation):
		"""What is our guess as to other players' Opinions about everyone else?"""
		# Loop through all (known) Majors
		for loopPlayer in simulation.players:
			if not loopPlayer.isMajorAI() and not loopPlayer.isHuman():
				continue

			if not self.isValid(loopPlayer):
				continue

			# Now loop through every player HE knows
			for thirdPlayer in simulation.players:
				if not thirdPlayer.isMajorAI() and not thirdPlayer.isHuman():
					continue

				# Don't compare a player to himself
				if loopPlayer == thirdPlayer:
					continue

				# Do both we and the guy we're looking about know the third guy?
				if self.isValid(thirdPlayer) and loopPlayer.diplomacyAI.isValid(thirdPlayer):
					opinionWeight = 0

					# Look at Land Dispute
					estimatedOtherPlayerLandDisputeLevel = self.playerDict.estimateOtherPlayerLandDisputeLevelBetween(loopPlayer, thirdPlayer)
					if estimatedOtherPlayerLandDisputeLevel == DisputeLevelType.fierce:
						opinionWeight += 30  # OPINION_WEIGHT_LAND_FIERCE
					elif estimatedOtherPlayerLandDisputeLevel == DisputeLevelType.strong:
						opinionWeight += 20  # OPINION_WEIGHT_LAND_STRONG
					elif estimatedOtherPlayerLandDisputeLevel == DisputeLevelType.weak:
						opinionWeight += 10  # OPINION_WEIGHT_LAND_WEAK
					elif estimatedOtherPlayerLandDisputeLevel == DisputeLevelType.none:
						opinionWeight += 0  # OPINION_WEIGHT_LAND_NONE

					# Look at Victory Competition Dispute
					estimatedOtherPlayerVictoryDisputeLevel = self.playerDict.estimateOtherPlayerVictoryDisputeLevelBetween(loopPlayer, thirdPlayer)
					if estimatedOtherPlayerVictoryDisputeLevel == DisputeLevelType.fierce:
						opinionWeight += 30  # OPINION_WEIGHT_VICTORY_FIERCE
					elif estimatedOtherPlayerVictoryDisputeLevel == DisputeLevelType.strong:
						opinionWeight += 20  # OPINION_WEIGHT_VICTORY_STRONG
					elif estimatedOtherPlayerVictoryDisputeLevel == DisputeLevelType.weak:
						opinionWeight += 10  # OPINION_WEIGHT_VICTORY_WEAK
					elif estimatedOtherPlayerVictoryDisputeLevel == DisputeLevelType.none:
						opinionWeight += 0  # OPINION_WEIGHT_VICTORY_NONE

					# Now do the final assessment
					if opinionWeight >= 50:  # OPINION_THRESHOLD_UNFORGIVABLE())
						opinion = MajorCivOpinionType.unforgivable  # MAJOR_CIV_OPINION_UNFORGIVABLE
					elif opinionWeight >= 30:  # OPINION_THRESHOLD_ENEMY())
						opinion = MajorCivOpinionType.enemy  # MAJOR_CIV_OPINION_ENEMY
					elif opinionWeight >= 10:  # OPINION_THRESHOLD_COMPETITOR())
						opinion = MajorCivOpinionType.competitor  # MAJOR_CIV_OPINION_COMPETITOR
					elif opinionWeight < -10:  # OPINION_THRESHOLD_FAVORABLE())
						opinion = MajorCivOpinionType.favorable  # MAJOR_CIV_OPINION_FAVORABLE
					elif opinionWeight < -30:  # OPINION_THRESHOLD_FRIEND())
						opinion = MajorCivOpinionType.friend  # MAJOR_CIV_OPINION_FRIEND
					elif opinionWeight < -50:  # OPINION_THRESHOLD_ALLY())
						opinion = MajorCivOpinionType.ally  # MAJOR_CIV_OPINION_ALLY
					else:
						opinion = MajorCivOpinionType.neutral  # MAJOR_CIV_OPINION_NEUTRAL

					# Finally, set the Opinion
					self.playerDict.updateMajorCivOtherPlayerOpinionBetween(loopPlayer, thirdPlayer, opinion)

	def doUpdateApproachTowardsUsGuesses(self, simulation):
		"""See if there's anything we need to change with our guesses as to other players' Approaches towards us"""
		for loopPlayer in simulation.players:
			if not loopPlayer.isMajorAI() and not loopPlayer.isHuman():
				continue

			if not self.isValid(loopPlayer):
				continue

			# We have a guess as to what another player's Approach is towards us
			if self.playerDict.approachTowardsUsGuessOf(loopPlayer) != MajorPlayerApproachType.neutral:
				self.playerDict.changeApproachTowardsUsGuessCounterOf(loopPlayer, 1)

				if self.playerDict.approachTowardsUsGuessCounterOf(loopPlayer) > 30:
					self.playerDict.updateApproachTowardsUsGuessOf(loopPlayer, MajorPlayerApproachType.neutral)
					self.playerDict.updateApproachTowardsUsGuessCounterOf(loopPlayer, 0)

		return

	def doMakePeaceWithMinors(self, simulation):
		"""Do we want to make peace with anyone Minors we're at war with?"""
		if self._demandTargetPlayer is not None:
			return

		for loopPlayer in simulation.players:
			# we only want to check city states
			if not loopPlayer.isCityState():
				continue

			if not self.isValid(loopPlayer):
				continue

			if not self.isAtWarWith(loopPlayer):
				continue

			# Locked into war for a period of time? (coop war, war deal, etc.)
			if self.isWantsPeaceWith(loopPlayer) and self.numberOfTurnsLockedIntoWarWith(loopPlayer) == 0:
				if not loopPlayer.minorCivAI.isPeaceBlockedWith(self.player):
					self.player.makePeaceWith(loopPlayer)
					self.logPeaceMadeWith(loopPlayer, simulation.currentTurn)

		return

	def logPeaceMadeWith(self, otherPlayer, turn: int):
		logging.info(f'***** PEACE MADE! ***** by {self.player} and {otherPlayer} in turn {turn}')
		return

	def doUpdateDemands(self, simulation):
		"""Update out desire to make a demand from a player"""
		demandTargetPlayers = WeightedBaseList()
		for loopPlayer in simulation.players:
			if not loopPlayer.isMajorAI() and not loopPlayer.isHuman():
				continue

			if not self.isValid(loopPlayer):
				continue

			# Is eLoopPlayer a good target for making a demand?
			if self.isPlayerDemandAttractiveFrom(loopPlayer, simulation):
				weight = 0 if Tests.are_running else random.randint(0, 100)  # DIPLOMACY_AI: Random weight for player to make demand of.
				demandTargetPlayers.addWeight(weight, hash(loopPlayer))

		cancelDemand: bool = False

		# Any valid possibilities?
		if len(demandTargetPlayers.keys()) > 0:
			cancelDemand = False

			# Only assign a player to be the target if we don't already have one
			if self._demandTargetPlayer is not None:
				demandTargetPlayers.sortByValue(reverse=True)

				# Maybe change this later to a lower value(10 %?) - leaving it at 100 for now because
				# the AI has a bit of trouble getting everything together to make a demand right now
				chanceOfDemand: int = 100  # DEMAND_RAND
				if chanceOfDemand > random.randint(0, 100):  # DIPLOMACY_AI: Should AI make demand of player it's hostile towards?
					demandPlayer = simulation.playerForHash(firstOrNone(demandTargetPlayers.keys()))
					self.doStartDemandProcessFrom(demandPlayer, simulation)
		# No one we're hostile towards to make a demand of
		else:
			cancelDemand = True

		# If we're planning on making a demand, make sure it's still a good idea
		if self._demandTargetPlayer is not None:
			if not self.isPlayerDemandAttractiveFrom(self._demandTargetPlayer, simulation):
				cancelDemand = True

		# We're not hostile towards any one so cancel any demand work we have underway (if there's anything going on)
		if cancelDemand:
			self.doCancelHaltDemandProcess()

		# See If we have a demand ready to make
		self.doTestDemandReady(simulation)
		return

	def doCancelHaltDemandProcess(self):
		"""Stop any current progress towards making a demand"""
		# Are we actually targeting anyone for a demand?
		if self._demandTargetPlayer is not None:
			if self.warGoalTowards(self._demandTargetPlayer) == WarGoalType.demand:
				self.playerDict.updateWarGoalTowards(self._demandTargetPlayer, WarGoalType.none)

				# Get rid of the operation to put Units near them
				operation = self.player.militaryAI.showOfForceOperationAgainst(self._demandTargetPlayer)
				if operation is not None:
					operation.kill(OperationStateReason.diploOpinionChange)
					self.playerDict.updateMusteringForAttackAgainst(self._demandTargetPlayer, False)

			self._demandTargetPlayer = None
			self._demandReady = False

		return

	def doTestDemandReady(self, simulation):
		"""Are we ready to make a demand, backed with force?"""
		# Are we actually targeting anyone for a demand?
		if self._demandTargetPlayer is not None:
			if self.warGoalTowards(self._demandTargetPlayer) == WarGoalType.demand:
				operation = self.player.militaryAI.showOfForceOperationAgainst(self._demandTargetPlayer)
				if operation is not None:
					if not self.isAtWarWith(self._demandTargetPlayer):
						# If we're at least 85% of the way to our objective, let loose the dogs of war!
						# If we're "mustering" it means we have a Sneak Attack Operation that's in position to attack
						if self.playerDict.isMusteringForAttackAgainst(self._demandTargetPlayer) or \
							operation.percentFromMusterPointToTarget(simulation) >= 85:
							self.playerDict.updateMusteringForAttackAgainst(self._demandTargetPlayer, False)
							self._demandReady = True

		return

	def doUpdatePlanningExchanges(self, simulation):
		numRAsWanted: int = self.numberOfResearchAgreementsWanted(simulation)

		# Loop through all (known) Players
		for loopPlayer in simulation.players:
			if not loopPlayer.isMajorAI() and not loopPlayer.isHuman():
				continue

			if not self.isValid(loopPlayer):
				continue

			# RESEARCH AGREEMENT
			# Do we already have a RA?
			if not self.playerDict.isHasResearchAgreementWith(loopPlayer):
				# If we're Friendly and have the appropriate Tech, there's a chance we want to make a Research Agreement
				if not self.isWantsResearchAgreementWith(loopPlayer):
					# We have Tech & embassy to make a RA or they have Tech & embassy to make RA
					if self.player.isResearchAgreementTradingAllowedWith(loopPlayer) or \
						loopPlayer.isResearchAgreementTradingAllowedWith(self.player):
						self.doAddWantsResearchAgreementWith(loopPlayer, simulation)
						numRAsWanted += 1  # This was calculated above, increment it by one since we know we've added another

			# Already planning an RA?
			if self.isWantsResearchAgreementWith(loopPlayer):
				cancel: bool = False
				if self.majorCivApproachTowards(loopPlayer, hideTrueFeelings=True) == MajorPlayerApproachType.hostile:
					cancel = True
				# We have Tech & embassy to make a RA or They have Tech & embassy to make RA
				elif not self.player.isResearchAgreementTradingAllowedWith(loopPlayer) or \
					loopPlayer.isResearchAgreementTradingAllowedWithTeam(self.player):
					cancel = True

				if cancel:
					self.doCancelWantsResearchAgreementWith(loopPlayer, simulation)

		return

	def numberOfResearchAgreementsWanted(self, simulation) -> int:
		"""How many different players does this AI want a RA with?"""
		num: int = 0

		# Loop through all (known) Players
		for loopPlayer in simulation.players:
			if not loopPlayer.isMajorAI() and not loopPlayer.isHuman():
				continue

			if not self.isValid(loopPlayer):
				continue

			if self.isWantsResearchAgreementWith(loopPlayer):
				num += 1

		return num

	def otherPlayerNumberOfMinorsConqueredBy(self, otherPlayer) -> int:
		return self.playerDict.otherPlayerNumberOfMinorsConqueredBy(otherPlayer)

	def otherPlayerNumberOfMajorsConqueredBy(self, otherPlayer) -> int:
		return self.playerDict.otherPlayerNumberOfMajorsConqueredBy(otherPlayer)

	def doPlayerKilledSomeone(self, otherPlayer, deadPlayer):
		"""otherPlayer killed deadPlayer, so figure out what that means"""
		if self.isValid(otherPlayer):
			# Minor Civ
			if deadPlayer.isCityState():
				self.playerDict.changeOtherPlayerNumberOfMinorsConqueredBy(otherPlayer, 1)

				# Did they kill a Minor we're protecting?
				if deadPlayer.minorCivAI.isProtectedByMajor(self.player):
					self.playerDict.updateOtherPlayerTurnsSinceKilledProtectedMinorBy(otherPlayer, 0)
					self.playerDict.updateOtherPlayerProtectedMinorKilledBy(otherPlayer, deadPlayer)
					self.playerDict.changeOtherPlayerNumberOfProtectedMinorsKilledBy(otherPlayer, 1)

					# Player broke a promise that he wasn't going to kill the Minor
					if self.playerDict.isPlayerMadeAttackCityStatePromiseBy(otherPlayer):
						self.playerDict.updatePlayerBrokenAttackCityStatePromiseBy(otherPlayer, True)
			# Major Civ
			else:
				self.playerDict.changeOtherPlayerNumberOfMajorsConqueredBy(otherPlayer, 1)

		return

	def isPlayerDemandAttractiveFrom(self, otherPlayer, simulation) -> bool:
		"""Are we willing to make a demand of otherPlayer?"""
		# Being hostile towards this guy? (ignore war face, as if we're planning a war already, making a demand doesn't mesh well with that)
		if self.majorCivApproachTowards(otherPlayer, hideTrueFeelings=False) != MajorPlayerApproachType.hostile:
			return False

		# Player can't be distant
		if self.player.proximityToPlayer(otherPlayer) < PlayerProximityType.far:
			return False

		# If they're a bad or impossible target then that's not good at all for us
		if self.playerDict.targetValueOf(otherPlayer) < PlayerTargetValueType.average:
			return False

		# Don't make demands of them too often
		if self.playerDict.numberOfTurnsSinceStatementSent(otherPlayer, DiplomaticStatementType.demand) < 40:
			return False

		# If we're planning a war or at war with anyone, making a demand is unwise
		for loopPlayer in simulation.players:
			if not loopPlayer.isMajorAI() and not loopPlayer.isHuman():
				continue

			if not self.isValid(loopPlayer):
				continue

			if self.warGoalTowards(loopPlayer) == WarGoalType.prepare:
				return False

			if self.isAtWarWith(loopPlayer):
				return False

		# Player has to be on the same area as us
		ownCapital = simulation.capitalOf(self.player)
		otherCapital = simulation.capitalOf(otherPlayer)
		if ownCapital is not None and otherCapital is not None:
			if simulation.areaOf(ownCapital.location) == simulation.areaOf(otherCapital.location):
				return True

		return False

	def closeEmbassyAt(self, otherPlayer):
		self.playerDict.sendDelegationTo(otherPlayer, False)
		self.playerDict.establishEmbassyTo(otherPlayer, False)
		self.playerDict.cancelOpenBorderAgreementWith(otherPlayer)
		self.playerDict.cancelDefensivePactWith(otherPlayer)
		return

	def cancelResearchAgreementWith(self, otherPlayer):
		self.playerDict.cancelResearchAgreementWith(otherPlayer)

	def hasEstablishedEmbassyTo(self, otherPlayer) -> bool:
		return self.playerDict.hasEstablishedEmbassyTo(otherPlayer)

	def wantsDelegationFrom(self, otherPlayer) -> bool:
		# May want to make this logic more sophisticated eventually.  This will do for now
		approach = self.majorCivApproachTowards(otherPlayer, hideTrueFeelings=True)
		if approach == MajorPlayerApproachType.hostile or approach == MajorPlayerApproachType.war:
			return False

		return True

	def wantsEmbassyAt(self, otherPlayer) -> bool:
		""" Do we want to have an embassy in the player's capital?"""
		# May want to make this logic more sophisticated eventually.  This will do for now
		approach = self.majorCivApproachTowards(otherPlayer, hideTrueFeelings=True)
		if approach == MajorPlayerApproachType.hostile or approach == MajorPlayerApproachType.war:
			return False

		return True

	def isMakeRequest(self, otherPlayer, deal, simulation) -> (bool, bool):
		"""Is this AI willing to make a request of otherPlayer"""
		friendly: bool = self.majorCivApproachTowards(otherPlayer, hideTrueFeelings=True) == MajorPlayerApproachType.friendly

		if friendly and self.playerDict.isDeclarationOfFriendshipActiveWith(otherPlayer):
			# Is there something we want?
			wantsSomething: bool = False
			# Is there a strong reason why we want something? (added to rand roll)
			iWeightBias: int = 0

			# Luxury Request
			if not wantsSomething:
				wantsSomething, iWeightBias = self.isLuxuryRequestBy(otherPlayer, deal, simulation)
			
			# Gold Request
			if not wantsSomething:
				wantsSomething, iWeightBias = self.isGoldRequestBy(otherPlayer, deal, simulation)

			if wantsSomething:
				# Random element
				iRand = 70 if Tests.are_running else random.randint(0, 100)  # Diplomacy AI: Friendly civ request roll.
				iRand += iWeightBias

				if iRand >= 67:
					return True, True
				else:
					return False, False

		return False, False

	def isLuxuryRequestBy(self, otherPlayer, deal: DiplomaticDeal, simulation) -> (bool, int):
		"""Does this AI want something?"""
		iWeightBias: int = 0
		luxuryToAskFor: ResourceType = ResourceType.none

		# See if the other player has a Resource to trade
		for loopResource in ResourceType.luxury():
			# Any extras?
			if otherPlayer.numberOfAvailableResource(loopResource) < 2:
				continue

			# Can they actually give us this item
			if not deal.isPossibleToTradeItem(otherPlayer, self.player, DiplomaticDealItemType.resources, resource=loopResource, amount=1, simulation=simulation):
				continue

			luxuryToAskFor = loopResource
			break

		# Didn't find something they could give us?
		if luxuryToAskFor == ResourceType.none:
			return False, iWeightBias

		# See if there's any Luxuries WE can trade (because if there are then we shouldn't be asking for hand outs)
		for loopResource in ResourceType.luxury():
			# Any extras?
			if otherPlayer.numberOfAvailableResource(loopResource) < 2:
				continue

			# Can they actually give us this item
			if not deal.isPossibleToTradeItem(self.player, otherPlayer, DiplomaticDealItemType.resources, resource=loopResource, amount=1, simulation=simulation):
				continue

			# Found something we can trade to them, so abort
			return False, iWeightBias

		# Add a little something extra since we're in dire straights
		if self.player.isEmpireUnhappy(simulation):
			iWeightBias += 25

		# Now seed the deal
		deal.addResourceTrade(otherPlayer, luxuryToAskFor, 1, 30, simulation)

		return True, iWeightBias

	def warScoreTowards(self, otherPlayer, simulation) -> int:
		"""What is the integer value of how well we think the war with otherPlayer is going?"""
		warScore: int = 0

		# Military Strength compared to us
		militaryStrengthComparedToUs: StrengthType = self.playerDict.militaryStrengthComparedToUsOf(otherPlayer)
		if militaryStrengthComparedToUs == StrengthType.pathetic:  # STRENGTH_PATHETIC
			warScore += 100  # WAR_PROJECTION_THEIR_MILITARY_STRENGTH_PATHETIC
		elif militaryStrengthComparedToUs == StrengthType.weak:  # STRENGTH_WEAK
			warScore += 60  # WAR_PROJECTION_THEIR_MILITARY_STRENGTH_WEAK
		elif militaryStrengthComparedToUs == StrengthType.poor:  # STRENGTH_POOR
			warScore += 25  # WAR_PROJECTION_THEIR_MILITARY_STRENGTH_POOR
		elif militaryStrengthComparedToUs == StrengthType.average:  # STRENGTH_AVERAGE
			warScore += 0  # WAR_PROJECTION_THEIR_MILITARY_STRENGTH_AVERAGE
		elif militaryStrengthComparedToUs == StrengthType.strong:  # STRENGTH_STRONG
			warScore += -25  # WAR_PROJECTION_THEIR_MILITARY_STRENGTH_STRONG
		elif militaryStrengthComparedToUs == StrengthType.powerful:  # STRENGTH_POWERFUL
			warScore += -60  # WAR_PROJECTION_THEIR_MILITARY_STRENGTH_POWERFUL
		elif militaryStrengthComparedToUs == StrengthType.immense:  # STRENGTH_IMMENSE
			warScore += -100  # WAR_PROJECTION_THEIR_MILITARY_STRENGTH_IMMENSE

		# Economic Strength compared to us
		economicStrengthComparedToUs: StrengthType = self.playerDict.economicStrengthComparedToUsOf(otherPlayer)
		if economicStrengthComparedToUs == StrengthType.pathetic:  # STRENGTH_PATHETIC
			warScore += 50  # WAR_PROJECTION_THEIR_ECONOMIC_STRENGTH_PATHETIC
		elif economicStrengthComparedToUs == StrengthType.weak:  # STRENGTH_WEAK
			warScore += 30  # WAR_PROJECTION_THEIR_ECONOMIC_STRENGTH_WEAK
		elif economicStrengthComparedToUs == StrengthType.poor:  # STRENGTH_POOR
			warScore += 12  # WAR_PROJECTION_THEIR_ECONOMIC_STRENGTH_POOR
		elif economicStrengthComparedToUs == StrengthType.average:  # STRENGTH_AVERAGE
			warScore += 0  # WAR_PROJECTION_THEIR_ECONOMIC_STRENGTH_AVERAGE
		elif economicStrengthComparedToUs == StrengthType.strong:  # STRENGTH_STRONG
			warScore += -12  # WAR_PROJECTION_THEIR_ECONOMIC_STRENGTH_STRONG
		elif economicStrengthComparedToUs == StrengthType.powerful:  # STRENGTH_POWERFUL
			warScore += -30  # WAR_PROJECTION_THEIR_ECONOMIC_STRENGTH_POWERFUL
		elif economicStrengthComparedToUs == StrengthType.immense:  # STRENGTH_IMMENSE
			warScore += -50  # WAR_PROJECTION_THEIR_ECONOMIC_STRENGTH_IMMENSE

		# War Damage inflicted on US
		warDamageLevel: WarDamageLevelType = self.warDamageLevelFrom(otherPlayer)
		if warDamageLevel == WarDamageLevelType.none:  # WAR_DAMAGE_LEVEL_NONE
			warScore += 0  # WAR_PROJECTION_WAR_DAMAGE_US_NONE
			# If they're aggressively expanding, it makes them a better target to go after,
			# If they've hurt us, this no longer applies
			if self.isRecklessExpanderTowards(otherPlayer, simulation):
				warScore += 25  # WAR_PROJECTION_RECKLESS_EXPANDER
		elif warDamageLevel == WarDamageLevelType.minor:  # WAR_DAMAGE_LEVEL_MINOR
			warScore += -10  # WAR_PROJECTION_WAR_DAMAGE_US_MINOR
		elif warDamageLevel == WarDamageLevelType.major:  # WAR_DAMAGE_LEVEL_MAJOR
			warScore += -20  # WAR_PROJECTION_WAR_DAMAGE_US_MAJOR
		elif warDamageLevel == WarDamageLevelType.serious:  # WAR_DAMAGE_LEVEL_SERIOUS
			warScore += -30  # WAR_PROJECTION_WAR_DAMAGE_US_SERIOUS
		elif warDamageLevel == WarDamageLevelType.crippled:  # WAR_DAMAGE_LEVEL_CRIPPLED
			warScore += -40  # WAR_PROJECTION_WAR_DAMAGE_US_CRIPPLED

		# War Damage inflicted on THEM (less than what's been inflicted on us for the same amount of damage)
		otherPlayerWarDamageLevel: WarDamageLevelType = self.playerDict.otherPlayerWarDamageLevelBetween(otherPlayer, self.player)
		if otherPlayerWarDamageLevel == WarDamageLevelType.none:  # WAR_DAMAGE_LEVEL_NONE
			warScore += 0  # WAR_PROJECTION_WAR_DAMAGE_THEM_NONE
		elif otherPlayerWarDamageLevel == WarDamageLevelType.minor:  # WAR_DAMAGE_LEVEL_MINOR
			warScore += 5  # WAR_PROJECTION_WAR_DAMAGE_THEM_MINOR
		elif otherPlayerWarDamageLevel == WarDamageLevelType.major:  # WAR_DAMAGE_LEVEL_MAJOR
			warScore += 10  # WAR_PROJECTION_WAR_DAMAGE_THEM_MAJOR
		elif otherPlayerWarDamageLevel == WarDamageLevelType.serious:  # WAR_DAMAGE_LEVEL_SERIOUS
			warScore += 15  # WAR_PROJECTION_WAR_DAMAGE_THEM_SERIOUS
		elif otherPlayerWarDamageLevel == WarDamageLevelType.crippled:  # WAR_DAMAGE_LEVEL_CRIPPLED
			warScore += 20  # WAR_PROJECTION_WAR_DAMAGE_THEM_CRIPPLED

		# the intangibles - our score vs their score
		ourScore: int = self.player.score(simulation)
		ourScore = ourScore if ourScore > 100 else 100
		theirScore = otherPlayer.score(simulation)
		theirScore = theirScore if theirScore > 100 else 100
		ratio = ((ourScore - theirScore) * 100) / (theirScore if ourScore > theirScore else ourScore)
		ratio = (ratio if ratio <= 50 else 50) if ratio >= -50 else -50
		warScore += ratio

		# Decrease war score if we've been fighting for a long time - after 60 turns the effect is -20 on the WarScore
		turnsAtWar: int = self.playerDict.turnsAtWarWith(otherPlayer, simulation.currentTurn)
		turnsAtWar /= 3
		warScore -= min(turnsAtWar, 20)  # WAR_PROJECTION_WAR_DURATION_SCORE_CAP

		return warScore

	def isGoldRequestBy(self, otherPlayer, deal: DiplomaticDeal, simulation) -> (bool, int):
		"""Does this AI want something?"""
		iWeightBias = 0

		iOurGold = self.player.treasury.value()
		iOurGPT = self.player.treasury.calculateGrossGold(simulation)
		iOurExpenses = self.player.treasury.calculateInflatedCosts(simulation)
		iOurGrossIncome = iOurGPT + iOurExpenses

		# If we have no expenses, don't ask (and also don't crash)
		if iOurExpenses == 0:
			return False

		# If we already have some gold saved up then don't bother
		if iOurGold > 100:
			return False

		# If we're making 35% more than we're spending then don't ask, we're doing alright
		if iOurGrossIncome * 100 / iOurExpenses > 135:
			return False

		iTheirGold = otherPlayer.treasury.value()
		iTheirGPT = otherPlayer.treasury.calculateGrossGold(simulation)
		iTheirExpenses = otherPlayer.treasury.calculateInflatedCosts(simulation)
		iTheirGrossIncome = iTheirGPT + iTheirExpenses

		# Don't divide by zero please
		if iTheirExpenses != 0:
			# If they're making less than 35% more than they're spending then don't ask, they're not in great shape
			if iTheirGrossIncome * 100 / iTheirExpenses < 135:
				return False
		elif iTheirGPT <= iOurGPT:
			return False

		# Add a little something extra since we're in dire straights
		if iOurGPT < 0:
			iWeightBias += 25

		# If we've made it this far we'd like to ask, so figure out how much we want to ask for
		iGoldToAskFor = iTheirGPT * 30 / 5
		iGPTToAskFor = 0

		if iGoldToAskFor > iTheirGold:
			iGoldToAskFor = 0
			iGPTToAskFor = max(1, iTheirGPT / 6)

		# Now seed the deal
		if iGoldToAskFor > 0:
			deal.addGoldTradeFrom(otherPlayer, iGoldToAskFor, simulation)
		elif iGPTToAskFor > 0:
			deal.addGoldPerTurnTradeFrom(otherPlayer, iGPTToAskFor, 30, simulation)

		return True

	def isForcePeaceWith(self, otherPlayer) -> bool:
		return self.playerDict.isForcePeaceWith(otherPlayer)

	def isLockedIntoCoopWarAgainst(self, otherPlayer, simulation) -> bool:
		"""Are we locked into a war with otherPlayer?"""
		coopWarState: CoopWarStateType = self.globalCoopWarAcceptedStateOf(otherPlayer, simulation)

		if coopWarState == CoopWarStateType.accepted or coopWarState == CoopWarStateType.soon:
			if self.globalCoopWarCounterWith(otherPlayer, simulation) <= 20:  # COOP_WAR_LOCKED_TURNS
				return True

		return False

	def globalCoopWarAcceptedStateOf(self, otherPlayer, simulation) -> CoopWarStateType:
		"""Check everyone we know to see if we're planning a coop war against them"""
		bestState: CoopWarStateType = CoopWarStateType.none

		for loopPlayer in simulation.players:
			if not loopPlayer.isHuman() and not loopPlayer.isMajorAI():
				continue

			if not self.isValid(loopPlayer):
				continue

			tempState = self.playerDict.coopWarAcceptedStateOf(loopPlayer, otherPlayer)
			if tempState > bestState:
				bestState = tempState

		return bestState

	def globalCoopWarCounterWith(self, otherPlayer, simulation) -> int:
		"""What is the SHORTEST amount of time on any coop counter?"""
		bestCount: int = 9999  # MAX_TURNS_SAFE_ESTIMATE

		for loopPlayer in simulation.players:
			if not loopPlayer.isHuman() and not loopPlayer.isMajorAI():
				continue

			if not self.isValid(loopPlayer):
				continue

			tempCount = self.playerDict.coopWarCounterWith(loopPlayer, otherPlayer)

			# No valid count against this guy
			if tempCount < 0:
				continue

			if tempCount < bestCount:
				bestCount = tempCount

		return bestCount

	def isDemandReady(self) -> bool:
		return self._demandReady

	def isActHostileTowardsHuman(self, humanPlayer, simulation) -> bool:
		"""Is the AI acting mean to the active human player?"""
		opinion: MajorCivOpinionType = self.majorCivOpinion(humanPlayer)
		visibleApproach: MajorPlayerApproachType = self.majorCivApproachTowards(humanPlayer, hideTrueFeelings=True)

		atWar: bool = self.isAtWarWith(humanPlayer)
		# Have to be at war +
		# High-level AI has to want peace +
		# Special rules for peace with human (turn count) have to be met
		atWarButWantsPeace: bool = atWar and self.playerDict.treatyWillingToOfferWith(humanPlayer) >= PeaceTreatyType.whitePeace and \
			self.playerDict.treatyWillingToAcceptWith(humanPlayer) >= PeaceTreatyType.whitePeace and \
			                       self.isWillingToMakePeaceWithHumanPlayer(humanPlayer, simulation)

		if visibleApproach == MajorPlayerApproachType.hostile:  # Hostile Approach
			return True
		elif atWar and not atWarButWantsPeace:  # At war and don't want peace
			return True
		elif opinion <= MajorCivOpinionType.enemy and visibleApproach != MajorPlayerApproachType.friendly:  # Enemy or worse, and not pretending to be friendly
			return True

		return False

	def doStartDemandProcessFrom(self, demandPlayer, simulation):
		"""AI has picked someone to make a demand of... what does this mean?"""
		self.updateDemandTargetPlayer(demandPlayer)

		operation = self.player.militaryAI.showOfForceOperationAgainst(demandPlayer)

		# Not yet readying an attack
		# If we're "mustering" it means we had a Sneak Attack Operation that finished
		if operation is None and not self.playerDict.isMusteringForAttackAgainst(demandPlayer):
			if not self.player.isAtWarWith(demandPlayer):
				if self.player.canDeclareWarTowards(demandPlayer):
					self.player.militaryAI.requestShowOfForce(demandPlayer, simulation)
					self.updateWarGoalAgainst(demandPlayer, WarGoalType.demand)

		return

	def wantsEmbassyFromPlayer(self, otherPlayer) -> bool:
		"""WantsEmbassyAtPlayer - Do we want to have an embassy in the player's capital?"""
		# May want to make this logic more sophisticated eventually.  This will do for now
		approach: MajorPlayerApproachType = self.majorCivApproachTowards(otherPlayer, hideTrueFeelings=True)
		if approach == MajorPlayerApproachType.hostile or approach == MajorPlayerApproachType.war:
			return False

		return True


class DiplomacyRequests:
	def __init__(self, player):
		self.player = player
		self.nextAIPlayer = None

		self.requests = []
		self.requestActive: bool = False
		self.requestActiveFromPlayer = None

	def beginTurn(self, simulation):
		# set nextAIPlayer to first ai player
		for loopPlayer in simulation.players:
			if not loopPlayer.isAlive():
				continue

			if not loopPlayer.isMajorAI():
				continue

			self.nextAIPlayer = loopPlayer
			break

		return

	def endTurn(self):
		self.nextAIPlayer = None

	@classmethod
	def sendRequest(cls, fromPlayer, toPlayer, state: DiplomaticRequestState, szText: str, emotion: LeaderEmotionType):
		DiplomacyRequests.sendDealRequest(fromPlayer, toPlayer, None, state, szText, emotion)

	@classmethod
	def sendDealRequest(cls, fromPlayer, toPlayer, deal: Optional[DiplomaticDeal], state: DiplomaticRequestState, szText: str, emotion: LeaderEmotionType):
		raise Exception('DiplomacyRequests.sendDealRequest not implemented')

	def hasActiveRequestFrom(self, sourcePlayer) -> bool:
		return self.requestActive and self.requestActiveFromPlayer == sourcePlayer

	def hasActiveRequest(self) -> bool:
		return self.requestActive

	def hasPendingRequests(self) -> bool:
		return len(self.requests) > 0 or self.requestActive

	@classmethod
	def hasActiveDiploRequestWithHuman(cls, sourcePlayer, simulation) -> bool:
		"""Return true if the supplied player has an active diplo request with a human.
		The diplo requests are stored on the target player, so we have to check each player
		Overall, this really only needs to check the active player, since this is not currently valid in MP
		but it will be one less thing to change if AI initiated diplo is ever added to MP."""
		for targetPlayer in simulation.players:
			if targetPlayer.isHuman() and targetPlayer.isAlive() and targetPlayer != sourcePlayer:
				if targetPlayer.diplomacyRequests.hasActiveRequestFrom(sourcePlayer):
					return True

		return False


class PlayerMoments:
	def __init__(self, player):
		self.player = player
		self._momentsArray: [Moment] = []
		self._currentEraScore: int = 0

	def add(self, moment: Moment):
		self._momentsArray.append(moment)
		self._currentEraScore += moment.momentType.eraScore()

	def addMomentOf(self, momentType: MomentType, turn: int, civilization: Optional[CivilizationType] = None,
					cityName: Optional[str] = None, continentName: Optional[str] = None,
					eraType: Optional[EraType] = None, naturalWonder: [FeatureType] = None,
					dedication: Optional[DedicationType] = None, wonder: Optional[WonderType] = None,
					cityState: Optional[CityStateType] = None, pantheon: Optional[PantheonType] = None):
		self._momentsArray.append(Moment(momentType, turn, civilization=civilization, cityName=cityName,
										 continentName=continentName, eraType=eraType, naturalWonder=naturalWonder,
										 dedication=dedication, wonder=wonder, cityState=cityState,
		                                 pantheon=pantheon))

		self._currentEraScore += momentType.eraScore()

	def moments(self) -> [Moment]:
		return self._momentsArray

	def eraScore(self) -> int:
		return self._currentEraScore

	def resetEraScore(self):
		self._currentEraScore = 0

	def hasMoment(self, momentType: MomentType, civilization: Optional[CivilizationType] = None,
				  eraType: Optional[EraType] = None, cityName: Optional[str] = None,
				  continentName: Optional[str] = None, naturalWonder: Optional[FeatureType] = None,
				  dedication: Optional[DedicationType] = None) -> bool:

		tmpMoment = Moment(momentType=momentType, civilization=civilization, eraType=eraType, cityName=cityName,
						   continentName=continentName, naturalWonder=naturalWonder, dedication=dedication, turn=0)

		# check all player moments
		for moment in self._momentsArray:
			if moment == tmpMoment:
				return True

		return False


class ReligionAI:
	def __init__(self, player):
		self.player = player

	def religionToSpread(self) -> ReligionType:
		"""What religion should this AI civ be spreading?"""
		currentReligion: ReligionType = self.player.religion.currentReligion()

		if currentReligion != ReligionType.none:
			return currentReligion

		religionInMostCities: ReligionType = self.player.religion.religionInMostCities()

		if religionInMostCities != ReligionType.none:
			return religionInMostCities

		return ReligionType.none

	def choosePantheonType(self, simulation) -> PantheonType:
		takenPantheonTypes: [PantheonType] = [r.pantheon() for r in simulation.religions()]
		availablePantheons: [PantheonType] = list(filter(lambda r: r not in takenPantheonTypes, PantheonType.all()))

		weights: WeightedBaseList = WeightedBaseList()

		for pantheonType in availablePantheons:
			score = self._scoreOfPantheon(pantheonType, simulation)
			weights.addWeight(score, pantheonType)

		bestPantheon: Optional[PantheonType] = weights.chooseFromTopChoices()
		if bestPantheon is not None:
			return bestPantheon

		return PantheonType.none

	def _scoreOfPantheon(self, pantheonType: PantheonType, simulation) -> int:
		"""AI's perceived worth of a belief"""
		rtnValue: int = 0  # Base value since everything has SOME value

		# scorePlot: int = 0
		# scoreCity: int = 0
		# scorePlayer: int = 0

		# Loop through each plot on map
		for loopPoint in simulation.points():
			tile = simulation.tileAt(loopPoint)

			# Skip if not revealed or ...
			if not tile.isDiscoveredBy(self.player):
				continue

			# ... in enemy territory
			if tile.hasOwner() and tile.owner() != self.player:
				continue

			# Skip if closest city of ours has no chance to work the plot
			closestCity = self.player.closestFriendlyCity(loopPoint, radius=3, simulation=simulation)
			if closestCity is None:
				continue

			#  Score it
			scoreAtPlot = self._scoreOfPantheonAtTile(pantheonType, tile, simulation)

			if scoreAtPlot <= 0:
				continue

			# Apply multiplier based on whether being worked, within culture borders, or not
			if tile.isWorked():
				scoreAtPlot *= 8  # RELIGION_BELIEF_SCORE_WORKED_PLOT_MULTIPLIER
			elif tile.hasOwner():
				scoreAtPlot *= 5  # RELIGION_BELIEF_SCORE_OWNED_PLOT_MULTIPLIER
			else:
				scoreAtPlot *= 3  # RELIGION_BELIEF_SCORE_UNOWNED_PLOT_MULTIPLIER

			rtnValue += scoreAtPlot

		# Add in value at city level
		for city in simulation.citiesOf(self.player):
			scoreAtCity = self._scoreOfPantheonAtCity(pantheonType, city, simulation)
			scoreAtCity *= 10  # RELIGION_BELIEF_SCORE_CITY_MULTIPLIER

			rtnValue += scoreAtCity

		# Add in player - level value
		scorePlayer = self._scoreOfPantheonForPlayer(pantheonType, simulation)
		rtnValue += scorePlayer

		# Final calculations
		# / * if ((pEntry->GetRequiredCivilization() != NO_CIVILIZATION) & & (pEntry
		#                                                                     ->GetRequiredCivilization() == m_pPlayer->getCivilizationType()))
		# {
		# 	iRtnValue *= 5
		# }
		# if (m_pPlayer->GetPlayerTraits()->IsBonusReligiousBelief() & & bForBonus)
		# {
		# int iModifier = 0
		# if (pEntry->IsFounderBelief())
		# iModifier += 5
		# elif (pEntry->IsPantheonBelief())
		# iModifier += -5
		# elif (pEntry->IsEnhancerBelief())
		# iModifier += 5
		# elif (pEntry->IsFollowerBelief())
		# {
		# bool
		# bNoBuilding = true
		# for (int iI = 0 iI < GC.getNumBuildingClassInfos() iI++)
		# {
		# if (pEntry->IsBuildingClassEnabled(iI))
		# {
		# 	BuildingTypes
		# eBuilding = (BuildingTypes)
		# m_pPlayer->getCivilizationInfo().getCivilizationBuildings(iI)
		# CvBuildingEntry * pBuildingEntry = GC.GetGameBuildings()->GetEntry(eBuilding)
		#
		# if (pBuildingEntry)
		# {
		# 	bNoBuilding = false
		# if (m_pPlayer->GetPlayerTraits()->GetFaithCostModifier() != 0)
		# {
		# 	modifier += 5
		# } else {
		# 	modifier += 1
		# }
		# break
		# }
		# }
		# }
		# if noBuilding {
		# modifier += -2
		# }
		# }
		#
		# if modifier != 0 {
		# iModifier *= 100
		# bool ShouldSpread = false
		#
		# // Increase based on nearby cities that lack our faith.
		# // Subtract the %of enhanced faiths.More enhanced = less room for spread.
		# int iNumEnhancedReligions = GC.getGame().GetGameReligions()->GetNumReligionsEnhanced()
		# int iReligionsEnhancedPercent = (100 * iNumEnhancedReligions) /GC.getMap().getWorldInfo().getMaxActiveReligions()
		#
		# // Let's look at all cities and get their religious status. Gives us a feel for what we can expect to gain in the near future.
		# int iNumNearbyCities = GetNumCitiesWithReligionCalculator(m_pPlayer->GetReligions()->GetCurrentReligion(), pEntry->IsPantheonBelief())
		#
		# int iSpreadTemp = 100
		# // Increase based on nearby cities that lack our faith.
		# iSpreadTemp *= iNumNearbyCities
		# // Divide by estimated total  # of cities on map.
		# iSpreadTemp /= GC.getMap().getWorldInfo().GetEstimatedNumCities()
		#
		# if (iReligionsEnhancedPercent <= 50 | | iSpreadTemp >= 25)
		# ShouldSpread = true
		#
		# iRtnValue += ShouldSpread ? iModifier: iModifier * -1

		if rtnValue <= 0:
			rtnValue = 1

		return rtnValue

	def _scoreOfPantheonAtTile(self, pantheonType: PantheonType, tile, simulation):
		"""AI's evaluation of this belief's usefulness at this one plot"""
		iRtnValue: int = 0

		for yieldType in list(YieldType):
			# Terrain
			terrain: TerrainType = tile.terrain()
			iRtnValue += pantheonType.terrainYieldChange(terrain, yieldType)

			# Feature
			feature: FeatureType = tile.feature()
			if feature != FeatureType.none:
				iRtnValue += pantheonType.featureYieldChange(feature, yieldType)

			# Resource
			resource: ResourceType = tile.resourceFor(self.player)
			improvement: ImprovementType = tile.improvement()
			if resource != ResourceType.none:
				iRtnValue += pantheonType.improvedResourceYieldChange(resource, improvement, yieldType)

				# Improvement
				for improvement in list(ImprovementType):
					if tile.canHaveImprovement(improvement, self.player):
						iRtnValue += pantheonType.improvementYieldChange(improvement, yieldType) * 2

		return iRtnValue

	def _scoreOfPantheonForPlayer(self, pantheonType: PantheonType, simulation):
		"""AI's evaluation of this belief's usefulness to this player"""
		iRtnValue: int = 0

		iFlavorOffense = self.player.personalAndGrandStrategyFlavor(FlavorType.offense)

		# ------------------------------
		# PLAYER - LEVEL PANTHEON BELIEFS
		# ------------------------------
		if pantheonType.faithFromKills() > 0:
			iTemp = pantheonType.faithFromKills() * pantheonType.maxDistance() * iFlavorOffense / 100
			if self.player.diplomacyAI.isGoingForWorldConquest():
				iTemp *= 2

			iRtnValue += iTemp

		return iRtnValue

	def _scoreOfPantheonAtCity(self, pantheonType: PantheonType, city, simulation) -> int:
		"""AI's evaluation of this belief's usefulness at this one city"""
		iRtnValue: int = 0

		# Simple ones
		iRtnValue += pantheonType.cityGrowthModifier() / 3

		# Wonder production multiplier
		if pantheonType.obsoleteEra() is not None:
			if pantheonType.obsoleteEra() > simulation.worldEra():
				iRtnValue += (pantheonType.wonderProductionModifier() * pantheonType.obsoleteEra().value()) / 10
		else:
			iRtnValue += pantheonType.wonderProductionModifier() / 3

		return iRtnValue

	def chooseReligionType(self, simulation) -> ReligionType:
		if not self.player.canFoundReligion(simulation):
			raise Exception('Cannot choose religion - player cannot found')

		availableReligions: [ReligionType] = simulation.availableReligions()

		if len(availableReligions) == 0:
			raise Exception('Cannot choose religion - no religion left')

		# check free religions if player likes on
		# if self.player.leader.preferredReligion() in availableReligions:
		#	return self.player.leader.preferredReligion()

		# select random
		return random.choice(availableReligions)

	def chooseFollowerBelief(self, simulation) -> BeliefType:
		return BeliefType.choralMusic

	def chooseNonFollowerBelief(self, simulation) -> BeliefType:
		return BeliefType.churchProperty
