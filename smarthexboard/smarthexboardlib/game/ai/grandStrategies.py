import logging
import random

from smarthexboard.smarthexboardlib.game.ai.diplomaticTypes import GuessConfidenceType
from smarthexboard.smarthexboardlib.game.flavors import FlavorType, Flavor
from smarthexboard.smarthexboardlib.game.states.victories import VictoryType
from smarthexboard.smarthexboardlib.core.base import InvalidEnumError, ExtendedEnum, WeightedBaseList
from smarthexboard.smarthexboardlib.map.types import Yields
from smarthexboard.smarthexboardlib.utils.base import firstOrNone


class GrandStrategyAIData:
	def __init__(self, name: str, flavorBase: int, flavorModifiers: [Flavor], yields: Yields):
		self.name = name
		self.flavorBase = flavorBase
		self.flavorModifiers: [Flavor] = flavorModifiers
		self.yields = yields


class GrandStrategyAIType(ExtendedEnum):
	none = 'none'

	conquest = 'conquest'
	culture = 'culture'
	council = 'council'

	def name(self) -> str:
		return self._data().name

	def flavor(self, flavorType: FlavorType) -> int:
		return self._flavorBase() + self.flavorModifier(flavorType)

	def _flavorBase(self) -> int:
		return self._data().flavorBase

	def flavorModifier(self, flavorType: FlavorType) -> int:
		item = next((flavorModifier for flavorModifier in self._flavorModifiers() if
					 flavorModifier.flavorType == flavorType), None)

		if item is not None:
			return item.value

		return 0

	def _flavorModifiers(self) -> [Flavor]:
		return self._data().flavorModifiers

	def yields(self) -> Yields:
		return self._data().yields

	def _data(self) -> GrandStrategyAIData:
		if self == GrandStrategyAIType.none:
			return GrandStrategyAIData(
				name="",
				flavorBase=0,
				flavorModifiers=[],
				yields=Yields(food=0.0, production=0.0, gold=0.0)
			)
		elif self == GrandStrategyAIType.conquest:
			return GrandStrategyAIData(
				name="",
				flavorBase=11,
				flavorModifiers=[
					Flavor(FlavorType.militaryTraining, 2),
					Flavor(FlavorType.growth, -1),
					Flavor(FlavorType.amenities, 1)
				],
				yields=Yields(food=0.0, production=200.0, gold=0.0)
			)
		elif self == GrandStrategyAIType.culture:
			return GrandStrategyAIData(
				name="",
				flavorBase=11,
				flavorModifiers=[
					Flavor(FlavorType.defense, 1),
					Flavor(FlavorType.cityDefense, 1),
					Flavor(FlavorType.offense, -1)
				],
				yields=Yields(food=0.0, production=50.0, gold=50.0)
			)
		elif self == GrandStrategyAIType.council:
			return GrandStrategyAIData(
				name="",
				flavorBase=10,
				flavorModifiers=[
					Flavor(FlavorType.defense, 1),
					Flavor(FlavorType.offense, -1),
					Flavor(FlavorType.recon, 1)
				],
				yields=Yields(food=0.0, production=0.0, gold=100.0)
			)

		#              <Row>
		#                  <AIGrandStrategyType>AIGRANDSTRATEGY_SPACESHIP</AIGrandStrategyType>
		#                  <YieldType>YIELD_SCIENCE</YieldType>
		#                  <Yield>100</Yield>
		#              </Row>
		#              <Row>
		#                  <AIGrandStrategyType>AIGRANDSTRATEGY_SPACESHIP</AIGrandStrategyType>
		#                  <YieldType>YIELD_PRODUCTION</YieldType>
		#                  <Yield>100</Yield>
		#              </Row>

		raise InvalidEnumError(self)


class GrandStrategyAIEntry:
	def __init__(self, grandStrategyAIType: GrandStrategyAIType):
		self.grandStrategyAIType = grandStrategyAIType
		self.value = 0


class GrandStrategyAIDict:
	def __init__(self):
		self.conquestStrategy = GrandStrategyAIEntry(GrandStrategyAIType.conquest)
		self.cultureStrategy = GrandStrategyAIEntry(GrandStrategyAIType.culture)
		self.councilStrategy = GrandStrategyAIEntry(GrandStrategyAIType.council)

	def add(self, value, grandStrategyAIType):
		if grandStrategyAIType == GrandStrategyAIType.none:
			pass
		elif grandStrategyAIType == GrandStrategyAIType.conquest:
			self.conquestStrategy.value += value
		elif grandStrategyAIType == GrandStrategyAIType.culture:
			self.cultureStrategy.value += value
		elif grandStrategyAIType == GrandStrategyAIType.council:
			self.councilStrategy.value += value
		else:
			raise InvalidEnumError(grandStrategyAIType)

	def value(self, grandStrategyAIType) -> float:
		if grandStrategyAIType == GrandStrategyAIType.none:
			return 0
		elif grandStrategyAIType == GrandStrategyAIType.conquest:
			return self.conquestStrategy.value
		elif grandStrategyAIType == GrandStrategyAIType.culture:
			return self.cultureStrategy.value
		elif grandStrategyAIType == GrandStrategyAIType.council:
			return self.councilStrategy.value
		else:
			raise InvalidEnumError(grandStrategyAIType)


class GrandStrategyAI:
	def __init__(self, player):
		self.player = player
		self.activeStrategy = GrandStrategyAIType.none
		self.turnActiveStrategySet = 0

		self._eGuessOtherPlayerActiveGrandStrategy = WeightedBaseList()
		self._eGuessOtherPlayerActiveGrandStrategyConfidence = WeightedBaseList()

	def doTurn(self, simulation):
		"""Runs every turn to determine what the player's Active Grand Strategy is and to change Priority Levels as necessary"""
		self.doGuessOtherPlayersActiveGrandStrategy(simulation)

		# hold the score for each strategy
		grandStrategyAIDict = GrandStrategyAIDict()

		for grandStrategyAIType in list(GrandStrategyAIType):
			if grandStrategyAIType == GrandStrategyAIType.none:
				continue

			# Base Priority looks at Personality Flavors (0 - 10) and multiplies * the Flavors attached to a Grand
			# Strategy (0-10), so expect a number between 0 and 100 back from this
			grandStrategyAIDict.add(self.priority(grandStrategyAIType), grandStrategyAIType)

			# real value, based on current game state
			if grandStrategyAIType == GrandStrategyAIType.conquest:
				grandStrategyAIDict.add(self.conquestGameValue(simulation), grandStrategyAIType)
			elif grandStrategyAIType == GrandStrategyAIType.culture:
				grandStrategyAIDict.add(self.cultureGameValue(simulation), grandStrategyAIType)
			elif grandStrategyAIType == GrandStrategyAIType.council:
				grandStrategyAIDict.add(self.councilGameValue(simulation), grandStrategyAIType)

			# random
			grandStrategyAIDict.add(random.randrange(50), grandStrategyAIType)

			# make the current strategy most likely
			if grandStrategyAIType == self.activeStrategy:
				grandStrategyAIDict.add(50, grandStrategyAIType)

		# Now see which Grand Strategy should be active, based on who has the highest Priority right now
		# Grand Strategy must be run for at least 10 turns
		if self.activeStrategy is None or self.numTurnsSinceActiveStrategySet(simulation.currentTurn) > 10:
			bestStrategy: GrandStrategyAIType = GrandStrategyAIType.none
			bestPriority = -1

			for grandStrategyAIType in list(GrandStrategyAIType):
				if grandStrategyAIDict.value(grandStrategyAIType) > bestPriority:
					bestStrategy = grandStrategyAIType
					bestPriority = grandStrategyAIDict.value(grandStrategyAIType)

			if self.activeStrategy != bestStrategy:
				self.activeStrategy = bestStrategy
				self.turnActiveStrategySet = simulation.currentTurn
				# inform about change ?
				logging.info(f'Player {self.player.leader} has adopted {self.activeStrategy} in turn {simulation.currentTurn}')

	def doGuessOtherPlayersActiveGrandStrategy(self, simulation):
		"""Runs every turn to try and figure out what other known Players' Grand Strategies are"""

		vGrandStrategyPriorities = WeightedBaseList()

		# Establish world culture, Military strength and tourism averages
		iNumPlayersAlive: int = 0
		iWorldCultureAverage: int = 0
		iWorldTourismAverage: int = 0
		iWorldMilitaryAverage: int = 0
		iWorldNumTechsAverage: int = 0

		for loopPlayer in simulation.players:
			if not loopPlayer.isMajorAI() and not loopPlayer.isHuman():
				continue

			if not loopPlayer.isAlive():
				continue

			iWorldCultureAverage += loopPlayer.tourism.lifetimeCulture()
			iWorldTourismAverage += loopPlayer.tourism.lifetimeTourism()
			iWorldMilitaryAverage += loopPlayer.militaryMight(simulation)
			iWorldNumTechsAverage += loopPlayer.techs.numberOfDiscoveredTechs()
			iNumPlayersAlive += 1

		iWorldCultureAverage /= iNumPlayersAlive
		iWorldTourismAverage /= iNumPlayersAlive
		iWorldMilitaryAverage /= iNumPlayersAlive
		iWorldNumTechsAverage /= iNumPlayersAlive

		# Look at every Major we've met
		for loopPlayer in simulation.players:
			if not loopPlayer.isMajorAI() and not loopPlayer.isHuman():
				continue

			if loopPlayer == self.player:
				continue

			if not self.player.hasMetWith(loopPlayer):
				continue

			priority = 0

			for loopGrandStrategies in list(GrandStrategyAIType):
				if loopGrandStrategies == GrandStrategyAIType.conquest:
					priority = self.guessOtherPlayerConquestPriorityOf(loopPlayer, iWorldMilitaryAverage, simulation)
				elif loopGrandStrategies == GrandStrategyAIType.culture:
					priority = self.guessOtherPlayerCulturePriorityOf(loopPlayer, iWorldCultureAverage, iWorldTourismAverage, simulation)
				elif loopGrandStrategies == GrandStrategyAIType.council:
					priority = self.guessOtherPlayerUnitedNationsPriorityOf(loopPlayer, simulation)
				# elif (strGrandStrategyName == "AIGRANDSTRATEGY_SPACESHIP"):
				#	priority = self.guessOtherPlayerSpaceshipPriority(eMajor, iWorldNumTechsAverage);

				vGrandStrategyPriorities.setWeight(priority, loopGrandStrategies)
				# vGrandStrategyPrioritiesForLogging.push_back(iPriority);

			if len(vGrandStrategyPriorities.keys()) > 0:
				# Add "No Grand Strategy" in case we just don't have enough info to go on
				priority = 40  # AI_GRAND_STRATEGY_GUESS_NO_CLUE_WEIGHT

				vGrandStrategyPriorities.setWeight(priority, GrandStrategyAIType.none)
				# vGrandStrategyPrioritiesForLogging.push_back(iPriority);

				vGrandStrategyPriorities.sortByValue(reverse=True)

				grandStrategy = firstOrNone(vGrandStrategyPriorities.keys())
				priority = firstOrNone(vGrandStrategyPriorities.values())
				guessConfidence: GuessConfidenceType = GuessConfidenceType.none

				# How confident are we in our Guess?
				if grandStrategy != GrandStrategyAIType.none:
					if priority >= 120:  # AI_GRAND_STRATEGY_GUESS_POSITIVE_THRESHOLD
						guessConfidence = GuessConfidenceType.positive  # GUESS_CONFIDENCE_POSITIVE
					elif priority >= 70:  # AI_GRAND_STRATEGY_GUESS_LIKELY_THRESHOLD
						guessConfidence = GuessConfidenceType.likely  # GUESS_CONFIDENCE_LIKELY
					else:
						guessConfidence = GuessConfidenceType.unsure  # GUESS_CONFIDENCE_UNSURE

				self.updateGuessOtherPlayerActiveGrandStrategy(loopPlayer, grandStrategy, guessConfidence)
				# self.logGuessOtherPlayerGrandStrategy(vGrandStrategyPrioritiesForLogging, eMajor);

			vGrandStrategyPriorities.removeAll()
			# vGrandStrategyPrioritiesForLogging.removeAll()

		return

	def priority(self, grandStrategyAIType: GrandStrategyAIType):
		value = 0

		for flavorType in list(FlavorType):
			value += grandStrategyAIType.flavor(flavorType) * self.player.leader.flavor(flavorType)

		return 0

	def numTurnsSinceActiveStrategySet(self, turnsElapsed):
		return turnsElapsed - self.turnActiveStrategySet

	def conquestGameValue(self, simulation):
		if VictoryType.domination not in simulation.victoryTypes:
			return -100

		priority = 0

		priority += self.player.leader.boldness() * 10

		# How many turns must have passed before we test for having met nobody?
		if simulation.currentTurn > 20:
			metAnybody = False

			for otherPlayer in simulation.players:
				if self.player == otherPlayer:
					continue

				if self.player.hasMetWith(otherPlayer):
					metAnybody = True

			if not metAnybody:
				priority += -50

		if self.player.isAtWar():
			priority += 10

		return priority

	def cultureGameValue(self, simulation):
		"""Returns Priority for Culture Grand Strategy"""
		# If Culture Victory isn't even available then don't bother with anything
		if VictoryType.cultural not in simulation.victoryTypes:
			return -100

		return 0

	def councilGameValue(self, simulation):
		return 0

	def guessOtherPlayerActiveGrandStrategyOf(self, otherPlayer) -> GrandStrategyAIType:
		"""What does this AI BELIEVE another player's Active Grand Strategy to be?"""
		return self._eGuessOtherPlayerActiveGrandStrategy.weight(hash(otherPlayer))

	def guessOtherPlayerActiveGrandStrategyConfidenceOf(self, otherPlayer) -> GuessConfidenceType:
		return self._eGuessOtherPlayerActiveGrandStrategyConfidence.weight(hash(otherPlayer))

	def updateGuessOtherPlayerActiveGrandStrategy(self, otherPlayer, grandStrategy: GrandStrategyAIType, guessConfidence: GuessConfidenceType):
		self._eGuessOtherPlayerActiveGrandStrategy.setWeight(grandStrategy, hash(otherPlayer))
		self._eGuessOtherPlayerActiveGrandStrategyConfidence.setWeight(guessConfidence, hash(otherPlayer))

	def guessOtherPlayerConquestPriorityOf(self, otherPlayer, worldMilitaryAverage: int, simulation) -> int:
		"""Guess as to how much another Player is prioritizing Conquest as his means of winning the game"""
		conquestPriority: int = 0

		# Compare their Military to the world average; Possible range is 100 to -100 (but will typically be around -20 to 20)
		if worldMilitaryAverage > 0:
			conquestPriority += (otherPlayer.militaryMight(simulation) - worldMilitaryAverage) * 100 / worldMilitaryAverage  # AI_GRAND_STRATEGY_CONQUEST_POWER_RATIO_MULTIPLIER

		# Minors attacked
		conquestPriority += self.player.diplomacyAI.otherPlayerNumberOfMinorsAttackedBy(otherPlayer) * 5  # GC.getAI_GRAND_STRATEGY_CONQUEST_WEIGHT_PER_MINOR_ATTACKED

		# Minors Conquered
		conquestPriority += self.player.diplomacyAI.otherPlayerNumberOfMinorsConqueredBy(otherPlayer) * 10  # AI_GRAND_STRATEGY_CONQUEST_WEIGHT_PER_MINOR_CONQUERED

		# Majors attacked
		conquestPriority += self.player.diplomacyAI.otherPlayerNumberOfMajorsAttackedBy(otherPlayer) * 10  # AI_GRAND_STRATEGY_CONQUEST_WEIGHT_PER_MAJOR_ATTACKED

		# Majors Conquered
		conquestPriority += self.player.diplomacyAI.otherPlayerNumberOfMajorsConqueredBy(otherPlayer) * 15  # AI_GRAND_STRATEGY_CONQUEST_WEIGHT_PER_MAJOR_CONQUERED

		return conquestPriority

	def guessOtherPlayerCulturePriorityOf(self, otherPlayer, worldCultureAverage: int, worldTourismAverage: int, simulation) -> int:
		"""Guess as to how much another Player is prioritizing Culture as his means of winning the game"""
		culturePriority: int = 0

		# Compare their Culture to the world average; Possible range is 75 to - 75
		if worldCultureAverage > 0:
			ratio = (otherPlayer.tourism.lifetimeCulture() - worldCultureAverage) * 75 / worldCultureAverage  # AI_GS_CULTURE_RATIO_MULTIPLIER() ;
			if ratio > 75:  # AI_GS_CULTURE_RATIO_MULTIPLIER
				culturePriority += 75  # AI_GS_CULTURE_RATIO_MULTIPLIER
			elif ratio < -75:  # AI_GS_CULTURE_RATIO_MULTIPLIER
				culturePriority += -75  # AI_GS_CULTURE_RATIO_MULTIPLIER

			culturePriority += ratio

		# Compare their Tourism to the world average; Possible range is 75 to - 75
		if worldTourismAverage > 0:
			ratio = (otherPlayer.tourism.lifetimeTourism() - worldTourismAverage) * 75 / worldTourismAverage  # AI_GS_TOURISM_RATIO_MULTIPLIER
			if ratio > 75:  # AI_GS_TOURISM_RATIO_MULTIPLIER
				culturePriority += 75  # AI_GS_TOURISM_RATIO_MULTIPLIER
			elif ratio < -75:  # AI_GS_TOURISM_RATIO_MULTIPLIER
				culturePriority += -75  # AI_GS_TOURISM_RATIO_MULTIPLIER

			culturePriority += ratio

		return culturePriority

	def guessOtherPlayerUnitedNationsPriorityOf(self, otherPlayer, simulation) -> int:
		"""Guess as to how much another Player is prioritizing the UN as his means of winning the game"""
		return 0

	def personalityAndGrandStrategy(self, flavorType: FlavorType) -> int:
		"""Get the base Priority for a Grand Strategy; these are elements common to ALL Grand Strategies"""
		if self.activeStrategy != GrandStrategyAIType.none:
			moddedFlavor = self.activeStrategy.flavorModifier(flavorType) + self.player.valueOfPersonalityIndividualFlavor(flavorType)
			moddedFlavor = max(0, moddedFlavor)
			return moddedFlavor

		return self.player.valueOfPersonalityIndividualFlavor(flavorType)
