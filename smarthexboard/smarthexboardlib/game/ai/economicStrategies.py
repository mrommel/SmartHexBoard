import abc
import logging
from typing import Optional

from smarthexboard.smarthexboardlib.game.ai.baseTypes import MilitaryStrategyType, PlayerStateAllWars
from smarthexboard.smarthexboardlib.game.ai.cities import CityStrategyType
from smarthexboard.smarthexboardlib.game.flavors import Flavor, FlavorType, Flavors
from smarthexboard.smarthexboardlib.core.base import ExtendedEnum, InvalidEnumError
from smarthexboard.smarthexboardlib.game.ai.grandStrategies import GrandStrategyAIType
from smarthexboard.smarthexboardlib.game.ai.militaryStrategies import ReconStateType
from smarthexboard.smarthexboardlib.game.states.builds import BuildType
from smarthexboard.smarthexboardlib.game.types import TechType
from smarthexboard.smarthexboardlib.game.unitTypes import UnitOperationType, UnitTaskType, UnitAbilityType
from smarthexboard.smarthexboardlib.game.wonders import WonderType
from smarthexboard.smarthexboardlib.map.base import HexArea, HexPoint, BoundingBox
from smarthexboard.smarthexboardlib.map.types import TerrainType, UnitDomainType, YieldType


class EconomicStrategyType(ExtendedEnum):
	needRecon = 'needRecon'
	enoughRecon = 'enoughRecon'
	reallyNeedReconSea = 'reallyNeedReconSea'  # ECONOMICAISTRATEGY_REALLY_NEED_RECON_SEA
	needReconSea = 'needReconSea'
	enoughReconSea = 'enoughReconSea'
	earlyExpansion = 'earlyExpansion'
	enoughExpansion = 'enoughExpansion'
	needHappiness = 'needHappiness'
	needHappinessCritical = 'needHappinessCritical'
	needNavalGrowth = 'needNavalGrowth'  # ECONOMICAISTRATEGY_CITIES_NEED_NAVAL_GROWTH
	needNavalTileImprovement = 'needNavalTileImprovement'  # ECONOMICAISTRATEGY_CITIES_NEED_NAVAL_TILE_IMPROVEMENT
	foundCity = 'foundCity'
	tradeWithCityState = 'tradeWithCityState'  # ECONOMICAISTRATEGY_TRADE_WITH_CITY_STATE
	needImprovementFood = 'needImprovementFood'
	needImprovementProduction = 'needImprovementProduction'
	oneOrFewerCoastalCities = 'oneOrFewerCoastalCities'
	losingMoney = 'losingMoney'
	haltGrowthBuildings = 'haltGrowthBuildings'
	tooManyUnits = 'tooManyUnits'
	islandStart = 'islandStart'
	expandToOtherContinents = 'expandToOtherContinents'
	expandLikeCrazy = 'expandLikeCrazy'  # ECONOMICAISTRATEGY_EXPAND_LIKE_CRAZY
	# ECONOMICAISTRATEGY_GROW_LIKE_CRAZY
	# ECONOMICAISTRATEGY_MOSTLY_ON_THE_COAST
	navalMap = 'navalMap'  # ECONOMICAISTRATEGY_NAVAL_MAP

	# The following Player Strategies are associated with the Grand Strategy the player has adopted
	# ECONOMICAISTRATEGY_GS_CULTURE
	# ECONOMICAISTRATEGY_GS_CONQUEST
	# ECONOMICAISTRATEGY_GS_DIPLOMACY
	# ECONOMICAISTRATEGY_GS_SPACESHIP
	# ECONOMICAISTRATEGY_GS_SPACESHIP_HOMESTRETCH

	def name(self) -> str:
		return EconomicStrategies().strategy(self).name

	def isNoMinorCivs(self) -> bool:
		return EconomicStrategies().strategy(self).noMinorCivs

	def requiredTech(self):
		return EconomicStrategies().strategy(self).requiredTech

	def obsoleteTech(self):
		return EconomicStrategies().strategy(self).obsoleteTech

	def notBeforeTurnElapsed(self):
		return EconomicStrategies().strategy(self).notBeforeTurnElapsed

	def shouldBeActive(self, player, simulation):
		return EconomicStrategies().strategy(self).shouldBeActive(player, simulation)

	def flavors(self) -> Flavors:
		return EconomicStrategies().strategy(self).flavors

	def checkEachTurns(self) -> int:
		return EconomicStrategies().strategy(self).checkTriggerTurnCount

	def minimumAdoptionTurns(self) -> int:
		return EconomicStrategies().strategy(self).minimumNumTurnsExecuted


class EconomicStrategy(abc.ABC):
	def __init__(self, name):
		self.name = name
		self.noMinorCivs = False
		self.checkTriggerTurnCount = 1
		self.minimumNumTurnsExecuted = 1
		self.weightThreshold = 1
		self.requiredTech = None
		self.obsoleteTech = None
		self.notBeforeTurnElapsed = 0
		self.flavors = Flavors()
		self.flavorThresholdModifiers = Flavors()

	# Figure out what the WeightThreshold Mod should be by looking at the Flavors for this player & the Strategy
	def weightThresholdModifier(self, player):
		modifier = 0

		# Look at all Flavors for the Player & this Strategy
		for flavorType in list(FlavorType):
			personalityFlavor = player.valueOfPersonalityIndividualFlavor(flavorType)
			strategyFlavorMod = self.flavorThresholdModifiers.value(flavorType)

			modifier += (personalityFlavor * strategyFlavorMod)

		return modifier

	def shouldBeActive(self, player, simulation) -> bool:
		raise NotImplementedError

	def __str__(self):
		return self.name


class EarlyExpansionStrategy(EconomicStrategy):
	"""
		ECONOMICAISTRATEGY_EARLY_EXPANSION
		'Early Expansion' Player Strategy: An early Strategy simply designed to get player up to 3 Cities quickly.
	"""

	def __init__(self):
		super().__init__('Early Expansion')

		self.noMinorCivs = True
		self.checkTriggerTurnCount = 5
		self.minimumNumTurnsExecuted = 10
		self.weightThreshold = 3
		# advisor:.economic,
		# advisorCounsel: "TXT_KEY_ECONOMICAISTRATEGY_EARLY_EXPANSION",
		# advisorCounselImportance: 2,
		self.flavors = Flavors([
			# Flavor(FlavorType.tileImprovement, value=10),
			# Flavor(FlavorType.expansion, value=10),
			Flavor(FlavorType.navalGrowth, value=-5),
			Flavor(FlavorType.expansion, value=75),
			Flavor(FlavorType.production, value=-4),
			Flavor(FlavorType.gold, value=-4),
			Flavor(FlavorType.science, value=-4),
			Flavor(FlavorType.culture, value=-4)
		])
		self.flavorThresholdModifiers = [
		]

	def shouldBeActive(self, player, simulation) -> bool:
		flavorExpansion = player.valueOfStrategyAndPersonalityFlavor(FlavorType.expansion)
		flavorGrowth = player.valueOfStrategyAndPersonalityFlavor(FlavorType.growth)
		maxCultureCities = 6  # AI_GS_CULTURE_MAX_CITIES

		desiredCities = (3 * flavorExpansion) / max(flavorGrowth, 1)
		difficulty = max(0, simulation.handicap.value() - 3)
		desiredCities += difficulty

		if player.grandStrategyAI.activeStrategy == GrandStrategyAIType.culture:
			desiredCities = min(desiredCities, maxCultureCities)

		desiredCities = max(desiredCities, maxCultureCities)

		# scale this based on world size
		# standardMapSize: MapSize = .standard
		# desiredCities = desiredCities * gameModel.mapSize().numberOfTiles() / standardMapSize.numberOfTiles()

		# See how many unowned Tiles there are on this player's landmass
		capital = simulation.capitalOf(player)
		if capital is not None:
			# Make sure city specialization has gotten one chance to specialize the capital before we adopt this
			if simulation.currentTurn > 25:  # AI_CITY_SPECIALIZATION_EARLIEST_TURN
				numberOfCities = len(simulation.citiesOf(player))
				return numberOfCities < desiredCities

		return False


class NeedReconStrategy(EconomicStrategy):
	"""ECONOMICAISTRATEGY_NEED_RECON"""
	def __init__(self):
		super().__init__('Need Recon')

		self.noMinorCivs = True
		self.checkTriggerTurnCount = 1
		self.minimumNumTurnsExecuted = 1
		self.firstTurnExecuted = 5
		# Advisor="FOREIGN";
		# AdvisorCounsel=[=[We should continue exploring the world to discover ancient ruins, natural wonders, and other civilizations!]=];
		# AdvisorCounselImportance=2;};
		self.flavors = Flavors([
			Flavor(FlavorType.recon, value=10)
		])

	def shouldBeActive(self, player, simulation) -> bool:
		militaryStrategyAdoption = player.militaryAI.militaryStrategyAdoption

		# Never desperate for explorers, if we are at war
		if militaryStrategyAdoption.adopted(MilitaryStrategyType.atWar):
			return False

		return player.economicAI.reconState() == ReconStateType.needed


class EnoughReconStrategy(EconomicStrategy):
	"""ECONOMICAISTRATEGY_ENOUGH_RECON"""
	def __init__(self):
		super().__init__('Enough recon')

		self.noMinorCivs = True
		self.checkTriggerTurnCount = 1
		self.minimumNumTurnsExecuted = 1
		self.firstTurnExecuted = 5
		# self.advisor:.economic,
		# self.advisorCounsel: "TXT_KEY_ECONOMICAISTRATEGY_ENOUGH_RECON",
		# self.advisorCounselImportance: 2,
		self.flavors = Flavors([Flavor(FlavorType.recon, value=-25)])
		self.flavorThresholdModifiers = []

	def shouldBeActive(self, player, simulation) -> bool:
		return player.economicAI.reconState() == ReconStateType.enough


class ReallyNeedReconSeaStrategy(EconomicStrategy):
	"""ECONOMICAISTRATEGY_REALLY_NEED_RECON_SEA"""
	def __init__(self):
		super().__init__('Really Need Recon Sea')

		self.noMinorCivs = True
		self.checkTriggerTurnCount = 1
		self.minimumNumTurnsExecuted = 1
		self.firstTurnExecuted = 50
		self.flavors = Flavors([
			Flavor(FlavorType.navalRecon, value=50),
			Flavor(FlavorType.naval, value=10)
		])
		self.flavorThresholdModifiers = []

	def shouldBeActive(self, player, simulation) -> bool:
		if player.economicAI.navalReconState() == ReconStateType.needed:
			if player.canEnterOcean():  # get a caravel out there NOW!
				# check current units - if we have already an ocean recon unit - we don't need to hurry
				for unit in simulation.unitsOf(player):
					if unit.task() == UnitTaskType.escortSea and not unit.isImpassableTerrain(TerrainType.ocean):
						return False

				# check cities, if an ocean recon units is already training
				for city in simulation.citiesOf(player):
					if city._buildQueue.isCurrentlyTrainingUnit():
						for unitType in city._buildQueue.unitTypesTraining():
							if unitType.domain() == UnitDomainType.sea and unitType.defaultTask() == UnitTaskType.exploreSea:
								if UnitAbilityType.oceanImpassable not in unitType.abilities():
									return False

				return True
			elif player.canEmbark():  # get a trireme out there NOW!
				# check current units - if we have already an ocean recon unit - we don't need to hurry
				for unit in simulation.unitsOf(player):
					if unit.task() == UnitTaskType.escortSea:
						return False

				# check cities, if an ocean recon units is already training
				for city in simulation.citiesOf(player):
					if city._buildQueue.isCurrentlyTrainingUnit():
						for unitType in city._buildQueue.unitTypesTraining():
							if unitType.domain() == UnitDomainType.sea and unitType.defaultTask() == UnitTaskType.exploreSea:
								return False

				return True

		return False


class FoundCityStrategy(EconomicStrategy):
	"""ECONOMICAISTRATEGY_FOUND_CITY"""
	def __init__(self):
		super().__init__('Found city')

		self.noMinorCivs = True
		self.checkTriggerTurnCount = 1
		self.minimumNumTurnsExecuted = 1
		self.weightThreshold = 10
		# advisor: .economic,
		# advisorCounsel: "TXT_KEY_ECONOMICAISTRATEGY_FOUND_CITY",
		# advisorCounselImportance: 2,
		self.flavors = Flavors([
		])

	def shouldBeActive(self, player, simulation) -> bool:
		economicAI = player.economicAI

		if player.isHuman() or player.isBarbarian():
			return False

		firstLooseSettler = None
		firstLooseSettlerArea: Optional[HexArea] = None
		looseSettlers = 0

		for unit in simulation.unitsOf(player):
			if unit.hasTask(UnitTaskType.settle):
				if unit.army() is None:
					looseSettlers += 1
					if looseSettlers == 1:
						firstLooseSettler = unit
						firstLooseSettlerArea = simulation.areaOf(unit.location)

		strategyWeight = looseSettlers * 10  # Just one settler will trigger this
		weightThresholdModifier = self.weightThresholdModifier(player)
		weightThreshold = self.weightThreshold + weightThresholdModifier

		# Don't run this strategy if you have 0 cities, in that case we just want to drop down a city wherever we happen
		# to be
		if strategyWeight >= weightThreshold and len(simulation.citiesOf(player)) >= 1:
			(numAreas, bestArea, _) = player.bestSettleAreasWithMinimumSettleFertility(
				economicAI.minimumSettleFertility(), simulation)

			if numAreas == 0:
				return False

			bestSettlePlot = player.bestSettlePlotFor(firstLooseSettler, escorted=True, sameArea=False, simulation=simulation)

			if bestSettlePlot is None:
				return False

			area = bestSettlePlot.area()

			canEmbark = player.canEmbark()
			isAtWarWithSomeone = player.atWarCount() > 0

			# CASE 1: Need a city on this area
			if firstLooseSettlerArea is not None and area is not None and firstLooseSettlerArea == area:
				player.addOperation(UnitOperationType.foundCity, None, None, area, None, simulation)
				return True
			elif canEmbark and self.isSafeForQuickColonyIn(area, simulation, player):
				# CASE 2: Need a city on a safe distant area
				# Have an overseas we can get to safely
				player.addOperation(UnitOperationType.colonize, None, None, area, None, simulation)
				return True

				# CASE 3: My embarked units can fight, I always do quick colonization overseas
				#             /*else if canEmbark && pPlayer->GetPlayerTraits()->IsEmbarkedNotCivilian() {
				#                 player.addOperation(of: .notSoQuickColonize, towards: nil, target: nil, area: iArea)
				#                 return true
				#             }*/
			elif canEmbark and not isAtWarWithSomeone:
				# CASE 3a: Need a city on a not so safe distant area
				# not at war with anyone
				player.addOperation(UnitOperationType.notSoQuickColonize, None, None, area, None, simulation)
				return True
			elif canEmbark:
				# CASE 4: Need a city on distant area
				player.addOperation(UnitOperationType.colonize, None, None, area, None, simulation)
				return True

		return False

	def isSafeForQuickColonyIn(self, area: Optional[HexArea], simulation, player) -> bool:
		"""Do we have an island clear of hostile units to settle on?"""
		if area is not None and area.boundingBox() is not None:
			boundingBox: BoundingBox = area.boundingBox()

			for x in range(boundingBox.minX, boundingBox.maxX):
				for y in range(boundingBox.minY, boundingBox.maxY):
					if simulation.isEnemyVisibleAt(HexPoint(x, y), player):
						return False

		return True


class LosingMoneyStrategy(EconomicStrategy):
	"""ECONOMICAISTRATEGY_LOSING_MONEY"""
	def __init__(self):
		super().__init__('Losing Money')

		self.checkTriggerTurnCount = 5
		self.minimumNumTurnsExecuted = 5
		self.weightThreshold = 2
		self.firstTurnExecuted = 20
		# advisor: .economic,
		# advisorCounsel: "TXT_KEY_ECONOMICAISTRATEGY_LOSING_MONEY",
		# advisorCounselImportance: 2,
		self.flavors = [
            Flavor(FlavorType.gold, value=25),
            Flavor(FlavorType.offense, value=-10), # ?
            Flavor(FlavorType.defense, value=-10) # ?
        ]
		self.flavorThresholdModifiers = []

	def shouldBeActive(self, player, simulation) -> bool:
		# Need a certain number of turns of history before we can turn this on
		if simulation.currentTurn <= self.minimumNumTurnsExecuted:
			return False

		# Is average income below desired threshold over past X turns?
		return player.treasury.averageIncome(self.minimumNumTurnsExecuted) < float(self.weightThreshold)


class ExpandLikeCrazyStrategy(EconomicStrategy):
	"""ECONOMICAISTRATEGY_EXPAND_LIKE_CRAZY"""
	def __init__(self):
		super().__init__('Expand Like Crazy')

		self.noMinorCivs = True
		self.checkTriggerTurnCount = 10
		self.minimumNumTurnsExecuted = 25
		self.weightThreshold = 10
		self.firstTurnExecuted = 25
		# AdvisorCounselImportance = 1
		self.flavors = Flavors([
			Flavor(FlavorType.expansion, value=10)
		])

	def shouldBeActive(self, player, simulation) -> bool:
		"""IsTestStrategy_ExpandLikeCrazy"""
		if player.isHuman() or player.isBarbarian():
			return False

		# Never run this if we are going for a cultural victory since it will derail that
		if player.grandStrategyAI.activeStrategy == GrandStrategyAIType.culture:
			return False

		flavorExpansion: int = player.grandStrategyAI.personalityAndGrandStrategy(FlavorType.expansion)
		weightThresholdModifier = self.weightThresholdModifier(player)
		weightThreshold = self.weightThreshold + weightThresholdModifier

		if flavorExpansion >= weightThreshold:
			return True

		return False


class ExpandToOtherContinentsStrategy(EconomicStrategy):
	"""ECONOMICAISTRATEGY_EXPAND_TO_OTHER_CONTINENTS"""
	def __init__(self):
		super().__init__('Expand to other Continents')

		self.noMinorCivs = True
		self.checkTriggerTurnCount = 10
		self.minimumNumTurnsExecuted = 25
		self.weightThreshold = 50
		self.requiredTech = TechType.shipBuilding
		# AdvisorCounselImportance = 1;
		self.flavors = Flavors([
			Flavor(FlavorType.naval, value=20),
			Flavor(FlavorType.navalTileImprovement, value=10),
			Flavor(FlavorType.navalGrowth, value=5),
			Flavor(FlavorType.waterConnection, value=10),
			Flavor(FlavorType.navalRecon, value=5),
			Flavor(FlavorType.offense, value=-10),
			Flavor(FlavorType.defense, value=-10),
			Flavor(FlavorType.expansion, value=75),
			Flavor(FlavorType.cityDefense, value=-10),
			Flavor(FlavorType.recon, value=10),
		])

	def shouldBeActive(self, player, simulation) -> bool:
		"""IsTestStrategy_ExpandToOtherContinents - Are we running out of room on our current landmass?"""
		if player.isHuman() or player.isBarbarian():
			return False

		# Never run this at the same time as island start
		if player.economicAI.isUsingStrategy(EconomicStrategyType.islandStart):
			return False

		# we should settle our island first
		if player.economicAI.isUsingStrategy(EconomicStrategyType.earlyExpansion):
			return False

		# Never desperate to settle distant lands if we are at war (unless we are doing okay at the war)
		if player.militaryAI.militaryStrategyAdoption.adopted(MilitaryStrategyType.losingWars):
			return False

		capitalCity = simulation.capitalOf(player)
		if capitalCity is not None:
			area = simulation.areaOf(capitalCity.location)

			# Do we have another area to settle (either first or second choice)?
			(numAreas, bestArea, secondBestArea) = player.bestSettleAreasWithMinimumSettleFertility(
				player.economicAI.minimumSettleFertility(), simulation)

			if (bestArea is not None and area != bestArea) or (secondBestArea is not None and area != secondBestArea):
				return True

		return False


class NeedHappinessStrategy(EconomicStrategy):
	"""ECONOMICAISTRATEGY_NEED_HAPPINESS"""
	def __init__(self):
		super().__init__('Need Happiness')

		self.checkTriggerTurnCount = 1
		self.minimumNumTurnsExecuted = 1
		self.weightThreshold = 2
		# Advisor="ECONOMIC";
		# AdvisorCounsel=[=[Our people's {{HappinessIcon5}} happiness is becoming a concern. We need to connect luxury resources, build {{HappinessIcon5}}happiness buildings and wonders, and adopt policies that help make our civilization happy!]=];
		# AdvisorCounselImportance=2
		self.flavorThresholdModifiers.set(FlavorType.amenities, 1)
		self.flavors = Flavors([
			Flavor(FlavorType.amenities, value=35),
			Flavor(FlavorType.expansion, value=-10),
			Flavor(FlavorType.growth, value=-5),
		])

	def shouldBeActive(self, player, simulation) -> bool:
		"""IsTestStrategy_NeedHappiness - Need Happiness Player Strategy: Time for Happiness?"""
		if player.totalPopulation(simulation) > 0 and player.unhappiness(simulation) > 0:
			iExcessHappiness = player.excessHappiness()
			iWeightThresholdModifier = self.weightThresholdModifier(player)  # 1 Weight per HAPPINESS Flavor

			# This will range from 0 to 5. If Happiness is less than this we will activate the strategy
			iDivisor = self.weightThreshold
			iWeightThresholdModifier /= iDivisor

			if iExcessHappiness <= iWeightThresholdModifier:
				return True

		return False


class NeedHappinessCriticalStrategy(EconomicStrategy):
	"""ECONOMICAISTRATEGY_NEED_HAPPINESS_CRITICAL"""
	def __init__(self):
		super().__init__('Need Happiness Critical')

		self.checkTriggerTurnCount = 1
		self.minimumNumTurnsExecuted = 1
		self.weightThreshold = -3
		# Advisor="ECONOMIC";
		# AdvisorCounsel=[=[Our people are quite Unhappy! We need to connect luxury resources, build {{HappinessIcon5}}happiness buildings and wonders, and adopt policies that help make our civilization happy quickly!]=];
		# AdvisorCounselImportance=3;};
		self.flavors = Flavors([
			Flavor(FlavorType.amenities, value=250),
			Flavor(FlavorType.expansion, value=-10),
			Flavor(FlavorType.growth, value=-10),
		])

	def shouldBeActive(self, player, simulation) -> bool:
		"""IsTestStrategy_NeedHappinessCritical - "Need Happiness" Player Strategy: REALLY time for Happiness?"""
		# If we're losing at war, return false
		if player.diplomacyAI.stateOfAllWars == PlayerStateAllWars.losing:
			return False

		if player.totalPopulation(simulation) > 0 and player.unhappiness(simulation) > 0:
			iExcessHappiness = player.excessHappiness()
			iThreshold = self.weightThreshold

			if iExcessHappiness <= iThreshold:
				return True

		return False


class IslandStartStrategy(EconomicStrategy):
	"""ECONOMICAISTRATEGY_ISLAND_START"""
	def __init__(self):
		super().__init__('Island Start')

		self.checkTriggerTurnCount = 1
		self.minimumNumTurnsExecuted = 50
		self.weightThreshold = 200
		# Advisor="SCIENCE";
		# AdvisorCounsel=[=[Our homeland is a small continent without much room for expansion. We need to focus on naval technologies until we can embark units.]=];
		# AdvisorCounselImportance=50;};
		self.flavors = Flavors([
			Flavor(FlavorType.naval, value=20),
			Flavor(FlavorType.navalTileImprovement, value=10),
			Flavor(FlavorType.navalGrowth, value=5),
			Flavor(FlavorType.waterConnection, value=5),
			Flavor(FlavorType.offense, value=-5),
			Flavor(FlavorType.defense, value=-5),
			Flavor(FlavorType.recon, value=-20),
		])

	def shouldBeActive(self, player, simulation) -> bool:
		"""IsTestStrategy_IslandStart - Did we start the game on a small continent (50 tiles or less)?"""
		iCoastalTiles = 0
		iRevealedCoastalTiles = 0

		# CvEconomicAIStrategyXMLEntry * pStrategy = pPlayer->GetEconomicAI()->GetEconomicAIStrategies()->GetEntry(eStrategy);

		# Only kick off this strategy in the first 25 turns of the game (though it will last 50 turns once selected)
		if simulation.currentTurn < 25 and player.startingPoint() is not None:
			if not player.canEmbark():
				startArea: HexArea = simulation.areaOf(player.startingPoint())

				if startArea is None:
					return False

				# Have we revealed a high enough percentage of the coast of our landmass?
				for loopPoint in simulation.points():
					loopTile = simulation.tileAt(loopPoint)

					if loopTile.area() is not None and loopTile.area() == startArea:
						if simulation.isCoastalAt(loopPoint):
							iCoastalTiles += 1

						if loopTile.isDiscoveredBy(player):
							iRevealedCoastalTiles += 1

				# AI_STRATEGY_ISLAND_START_COAST_REVEAL_PERCENT => 80
				if (iRevealedCoastalTiles * 100 / (iCoastalTiles + 1)) > 80 and \
					len(startArea.points()) < self.weightThreshold:
					return True

		return False


class NavalMapStartStrategy(EconomicStrategy):
	"""ECONOMICAISTRATEGY_NAVAL_MAP"""
	def __init__(self):
		super().__init__('Naval Map')

		self.noMinorCivs = True
		self.checkTriggerTurnCount = 1
		self.minimumNumTurnsExecuted = 10
		self.firstTurnExecuted = 1
		# self.advisorCounselImportance = 1
		self.flavors = Flavors([
			Flavor(FlavorType.navalRecon, value=20),
			Flavor(FlavorType.naval, value=20),
			Flavor(FlavorType.waterConnection, value=5)
		])

	def shouldBeActive(self, player, simulation) -> bool:
		"""IsTestStrategy_NavalMap - "Naval Map" Player Strategy: the map script will dictate this"""
		if player.isHuman():
			return False

		return False  # (GC.getMap().GetAIMapHint() & 1);


class NeedReconSeaStrategy(EconomicStrategy):
	"""ECONOMICAISTRATEGY_NEED_RECON_SEA"""
	def __init__(self):
		super().__init__('Need Recon Sea')

		self.noMinorCivs = True
		self.checkTriggerTurnCount = 1
		self.minimumNumTurnsExecuted = 1
		self.firstTurnExecuted = 5
		# self.advisor:.foreign
		# self.advisorCounsel: "TXT_KEY_ECONOMICAISTRATEGY_NEED_RECON_SEA"
		# self.advisorCounselImportance = 2
		self.flavors = Flavors([
			Flavor(FlavorType.navalRecon, value=20)
		])
		self.flavorThresholdModifiers = [Flavor(FlavorType.navalRecon, value=-1)]

	def shouldBeActive(self, player, simulation) -> bool:
		militaryStrategyAdoption = player.militaryAI.militaryStrategyAdoption

		# Never desperate for explorers if we are at war and its not looking good
		if militaryStrategyAdoption.adopted(MilitaryStrategyType.losingWars):
			return False

		return player.economicAI.navalReconState() == ReconStateType.needed


class EnoughReconSeaStrategy(EconomicStrategy):
	"""ECONOMICAISTRATEGY_ENOUGH_RECON_SEA"""
	def __init__(self):
		super().__init__('Enough Recon Sea')

		self.noMinorCivs = True
		self.checkTriggerTurnCount = 1
		self.minimumNumTurnsExecuted = 1
		self.firstTurnExecuted = 5
		# self.advisor = .economic
		# self.advisorCounsel = "TXT_KEY_ECONOMICAISTRATEGY_ENOUGH_RECON"
		# self.advisorCounselImportance = 2
		self.flavors = Flavors([
			Flavor(FlavorType.navalRecon, value=-200)
		])
		self.flavorThresholdModifiers = []

	def shouldBeActive(self, player, simulation) -> bool:
		return player.economicAI.navalReconState() == ReconStateType.enough


class EnoughExpansionStrategy(EconomicStrategy):
	"""ECONOMICAISTRATEGY_ENOUGH_EXPANSION"""
	def __init__(self):
		super().__init__('Enough Expansion')

		self.noMinorCivs = True
		self.checkTriggerTurnCount = 5
		self.minimumNumTurnsExecuted = 1
		self.weightThreshold = 1  # one settler
		# self.advisor:.economic,
		# self.advisorCounsel: "TXT_KEY_ECONOMICAISTRATEGY_ENOUGH_EXPANSION",
		# self.advisorCounselImportance: 2,
		self.flavors = Flavors([
			Flavor(FlavorType.expansion, value=-10)
		])
		self.flavorThresholdModifiers: []

	def shouldBeActive(self, player, simulation) -> bool:
		economicAI = player.economicAI
		militaryAI = player.militaryAI

		if player.isBarbarian() or self.noMinorCivs or player.traits().isNoAnnexing():
			return True

		if len(simulation.citiesOf(player)) <= 1:
			return False

		if player.unhappiness() > 0:
			return True

		if player.countUnitsWithDefaultTask(UnitTaskType.settle, simulation) > 1:
			return True

		if militaryAI.adopted(MilitaryStrategyType.losingWars) and player.isCramped():
			return True

		# Don't self-sabotage with too many cities
		# if (pPlayer->GetPlayerTraits()->IsSmaller() | | pPlayer->GetPlayerTraits()->IsTourism() | | pPlayer->GetDiplomacyAI()->IsGoingForCultureVictory())
		# iNonPuppetCities = pPlayer->GetNumEffectiveCities();
		# iTourismMod = GC.getMap().getWorldInfo().GetNumCitiesTourismCostMod() * (iNonPuppetCities - 1);
		# # the modifier is positive even if the effect is negative, wtf
		# if (iTourismMod > 23 + pPlayer->GetDiplomacyAI()->GetBoldness())
		# return true;

		# If we are running "ECONOMICAISTRATEGY_EXPAND_TO_OTHER_CONTINENTS"
		if economicAI.adopted(EconomicStrategyType.expandToOtherContinents):
			return False

		# If we are running "ECONOMICAISTRATEGY_EARLY_EXPANSION"
		if economicAI.adopted(EconomicStrategyType.earlyExpansion):
			return False

		# do this check last, it can be expensive
		if player.bestSettlePlotFor(player.startingPoint(), escorted=False, sameArea=False, simulation=simulation) is not None:
			return True

		return False


class NeedNavalGrowthStrategy(EconomicStrategy):
	"""ECONOMICAISTRATEGY_CITIES_NEED_NAVAL_GROWTH"""
	def __init__(self):
		super().__init__('Need Naval Growth')

		self.heckTriggerTurnCount = 5
		self.minimumNumTurnsExecuted = 5
		self.weightThreshold = 40
		# self.advisor="ECONOMIC";
		# self.advisorCounsel=[=[{1_CityName:textkey} has a considerable number of water tiles. We should focus on constructing buildings like the lighthouse that improve yield from those tiles.]=];
		# self.advisorCounselImportance=1;
		self.flavors = Flavors([
			Flavor(FlavorType.navalGrowth, value=15)
		])

	def shouldBeActive(self, player, simulation) -> bool:
		"""
			IsTestStrategy_CitiesNeedNavalGrowth
			"Cities Need Naval Growth" Player Strategy: Looks at how many of this player's Cities need NAVAL_GROWTH,
			and depending on the intrinsic NAVAL_GROWTH Flavor decides whether it's worth prioritizing this
			Flavor on an empire-wide scale
		"""
		iNumCitiesNeedNavalGrowth: int = 0

		for loopCity in simulation.citiesOf(player):
			if loopCity.cityStrategyAI.adopted(CityStrategyType.needNavalGrowth):
				iNumCitiesNeedNavalGrowth += 1

		if iNumCitiesNeedNavalGrowth > 0:
			iWeightThresholdModifier = EconomicStrategies.weightThresholdModifier(EconomicStrategyType.needNavalGrowth, player)  # 1 Weight per NAVAL_GROWTH Flavor
			iWeightThreshold = self.weightThreshold + iWeightThresholdModifier  # 25

			iCurrentWeight = (player.numberOfCities(simulation) - 1) * 10
			iCurrentWeight /= iWeightThreshold

			# See CvStrategyAI::IsTestStrategy_CitiesNeedBorders
			# for a couple examples on how the math here works

			# Do enough of our Cities want NavalGrowth? [Average is 10 / 30; range is 10 / 25 to 10 / 35]
			if iNumCitiesNeedNavalGrowth > iCurrentWeight:
				return True

		return False


class NeedNavalTileImprovementStrategy(EconomicStrategy):
	"""ECONOMICAISTRATEGY_CITIES_NEED_NAVAL_TILE_IMPROVEMENT"""
	def __init__(self):
		super().__init__('Need Naval Tile Improvement')

		self.checkTriggerTurnCount = 1
		self.minimumNumTurnsExecuted = 5
		self.weightThreshold = 25
		# self.Advisor = "ECONOMIC";
		# self.AdvisorCounsel = "We have water resources that we're not using. Build workboats and deploy them to help our civilization!"
		# self.AdvisorCounselImportance = 2;
		self.flavors = Flavors([
			Flavor(FlavorType.navalTileImprovement, value=20)
		])

	def shouldBeActive(self, player, simulation) -> bool:
		"""
			IsTestStrategy_CitiesNeedNavalGrowth
			"Cities Need Naval Growth" Player Strategy: Looks at how many of this player's Cities need NAVAL_GROWTH,
			and depending on the intrinsic NAVAL_GROWTH Flavor decides whether it's worth prioritizing this
			Flavor on an empire-wide scale
		"""
		iNumCitiesNeedNavalGrowth: int = 0

		for loopCity in simulation.citiesOf(player):
			if loopCity.cityStrategyAI.adopted(CityStrategyType.needNavalTileImprovement):  # AICITYSTRATEGY_NEED_NAVAL_GROWTH
				iNumCitiesNeedNavalGrowth += 1

		if iNumCitiesNeedNavalGrowth > 0:
			iWeightThresholdModifier = EconomicStrategies.weightThresholdModifier(EconomicStrategyType.needNavalTileImprovement, player)  # 1 Weight per NAVAL_GROWTH Flavor
			iWeightThreshold = self.weightThreshold + iWeightThresholdModifier  # 25

			iCurrentWeight = (player.numberOfCities(simulation) - 1) * 10
			iCurrentWeight /= iWeightThreshold

			# See CvStrategyAI::IsTestStrategy_CitiesNeedBorders for a couple examples on how the math here works

			# Do enough of our Cities want NavalGrowth? [Average is 10 / 30; range is 10 / 25 to 10 / 35]
			if iNumCitiesNeedNavalGrowth > iCurrentWeight:
				return True

		return False


class TradeWithCityStateStrategy(EconomicStrategy):
	"""ECONOMICAISTRATEGY_TRADE_WITH_CITY_STATE"""
	def __init__(self):
		super().__init__('Trade With CityState')

		self.checkTriggerTurnCount = 1
		self.minimumNumTurnsExecuted = 1
		self.weightThreshold = 10
		# self.advisorCounselImportance = 1
		self.flavors = Flavors([
		])

	def shouldBeActive(self, player, simulation) -> bool:
		"""IsTestStrategy_TradeWithCityState - "Trade with City State" Player Strategy: If there is a merchant who isn't in an operation?  If so, find him a city state"""
		iLooseMerchant: int = 0

		# Never run this strategy for a human player
		if not player.isHuman():
			# Look at map for loose merchants
			for loopUnit in simulation.unitsOf(player):
				if loopUnit.task() == UnitTaskType.trade:  # and pLoopUnit->GetGreatPeopleDirective() == GREAT_PEOPLE_DIRECTIVE_USE_POWER)
					if loopUnit.army() is None:
						iLooseMerchant += 1

			iStrategyWeight = iLooseMerchant * 10  # Just one merchant will trigger this
			iWeightThresholdModifier = EconomicStrategies.weightThresholdModifier(EconomicStrategyType.tradeWithCityState, player)
			iWeightThreshold = self.weightThreshold + iWeightThresholdModifier

			if iStrategyWeight >= iWeightThreshold:
				# Launch an operation.
				player.addOperation(UnitOperationType.merchantDelegation, None, None, None, None, simulation)  # AI_OPERATION_MERCHANT_DELEGATION

				# Set this strategy active
				return True

		return False


class NeedGenericImprovementStrategy(EconomicStrategy):
	"""ECONOMICAISTRATEGY_NEED_IMPROVEMENT_FOOD"""
	def __init__(self, yieldType: YieldType):
		super().__init__('Need Generic Improvement')

		self.yieldType = yieldType

		self.checkTriggerTurnCount = 1
		self.minimumNumTurnsExecuted = 1
		self.weightThreshold = 10
		self.firstTurnExecuted = 20
		# self.advisor="ECONOMIC";
		# self.advisorCounsel=[=[We are having a {{FoodIcon5}} food crisis! Use Workers to build improvements that increase the amount of {{FoodIcon5}}food that a plot provides.]=];
		# self.advisorCounselImportance=2;
		if self.yieldType == YieldType.food:
			self.flavors = Flavors([
				Flavor(FlavorType.tileImprovement, value=20),
				Flavor(FlavorType.growth, value=20),
			])
		elif self.yieldType == YieldType.production:
			self.flavors = Flavors([
				Flavor(FlavorType.tileImprovement, value=10),
				Flavor(FlavorType.production, value=10)
			])
		else:
			logging.warning("unsupported yield type")

	def shouldBeActive(self, player, simulation) -> bool:
		# find the city strategy associated with this issue

		if self.yieldType == YieldType.food:
			cityStrategyType = CityStrategyType.needImprovementFood
		elif self.yieldType == YieldType.production:
			cityStrategyType = CityStrategyType.needImprovementProduction
		else:
			logging.warning("no city strategy selected")
			return False

		# if enough cities are worried about this problem
		numberOfCities = player.numberOfCities(simulation)
		if numberOfCities == 0:
			return False  # no cities, no problem!

		numberOfCitiesConcerned = 0
		for city in simulation.citiesOf(player):
			cityStrategy = city.cityStrategy

			if cityStrategy.adopted(cityStrategyType):
				numberOfCitiesConcerned += 1

		warningRatio = 0.34  # AI_STRATEGY_NEED_IMPROVEMENT_CITY_RATIO

		# if not enough cities are upset
		if (float(numberOfCitiesConcerned) / float(numberOfCities)) < warningRatio:
			return False

		# see if there's a builder
		builder = None
		for loopUnit in simulation.unitsOf(player):
			if loopUnit.task() == UnitTaskType.work:
				builder = loopUnit
				break

		# if no builder, ignore - perhaps prompt a builder?
		if builder is None:
			return False

		# is there a build that I can create to improve the yield?

		# loop through the build types to find one that we can use
		for build in list(BuildType):
			requiredTech = build.required()
			if requiredTech is not None:
				if not player.hasTech(requiredTech):
					continue

			improvement = build.improvement()

			if improvement is None:
				continue

			canBuild: bool = False
			for plot in player.area().points():
				if player.canBuild(build, plot, testGold=False, simulation=simulation):
					canBuild = True
					break

			if not canBuild:
				continue

			# we can use an improvement that increases the yield
			if improvement.yieldsFor(player).value(self.yieldType) > 0:
				return True

		return False


class OneOrFewerCoastalCitiesStrategy(EconomicStrategy):
	"""
		ECONOMICAISTRATEGY_ONE_OR_FEWER_COASTAL_CITIES
		"One or Fewer Coastal Cities" Player Strategy: If we don't have 2 coastal cities, this runs nullifying the WATER_CONNECTION Flavor
	"""
	def __init__(self):
		super().__init__('One or Fewer Coastal Cities')

		self.checkTriggerTurnCount = 1
		self.minimumNumTurnsExecuted = 10
		self.weightThreshold = 10
		# AdvisorCounselImportance=1
		self.flavors = [
			Flavor(FlavorType.waterConnection, value=-10),
		]

	def shouldBeActive(self, player, simulation) -> bool:
		numberOfCoastalCities = 0
		for city in simulation.citiesOf(player):
			cityLocation = city.location

			if simulation.isCoastalAt(cityLocation):
				numberOfCoastalCities += 1

		return numberOfCoastalCities <= 1


class HaltGrowthBuildingsStrategy(EconomicStrategy):
	"""
		ECONOMICAISTRATEGY_HALT_GROWTH_BUILDINGS
		"Halt Growth Buildings" Player Strategy: Stop building granaries if working on a wonder that provides them for free
	"""
	def __init__(self):
		super().__init__('Halt Growth Buildings')

		self.noMinorCivs = True
		self.checkTriggerTurnCount = 1
		self.minimumNumTurnsExecuted = 1
		self.firstTurnExecuted = 20
		# self.advisor:.economic
		# self.advisorCounsel: "TXT_KEY_ECONOMICAISTRATEGY_HALT_GROWTH_BUILDINGS",
		# self.advisorCounselImportance: 2
		self.flavors = [
			Flavor(FlavorType.growth, value=-15)
		]
		self.flavorThresholdModifiers = []

	def shouldBeActive(self, player, simulation) -> bool:
		"""IsTestStrategy_HaltGrowthBuildings"""
		return False


class TooManyUnitsStrategy(EconomicStrategy):
	"""
		ECONOMICAISTRATEGY_TOO_MANY_UNITS
		Are we paying more in unit maintenance than we are taking in from our cities?
	"""

	def __init__(self):
		super().__init__('Too Many Units')

		self.checkTriggerTurnCount = 1
		self.minimumNumTurnsExecuted = 1
		self.firstTurnExecuted = 20
		# Advisor="ECONOMIC";
		# AdvisorCounsel=[=[Our {{ProductionIcon5}}production is being diminished by the number of units that we have. We should disband any unneeded units so that our civilization can operate at full capacity.]=];
		# AdvisorCounselImportance=2;
		flavors = [
			Flavor(FlavorType.offense, value=-30),
			Flavor(FlavorType.naval, value=-30),
			Flavor(FlavorType.ranged, value=-30),
			Flavor(FlavorType.mobile, value=-30),
			Flavor(FlavorType.recon, value=-50),
			Flavor(FlavorType.gold, value=15),
			Flavor(FlavorType.growth, value=20),
			Flavor(FlavorType.science, value=15),
			Flavor(FlavorType.culture, value=10),
			Flavor(FlavorType.amenities, value=10),
			Flavor(FlavorType.wonder, value=5)
		],
		self.flavorThresholdModifiers = []

	def shouldBeActive(self, player, simulation) -> bool:
		treasury = player.treasury

		goldForUnitMaintenance = treasury.goldForUnitMaintenance(simulation)
		goldFromCities = treasury.goldFromCities(simulation)

		return goldForUnitMaintenance > goldFromCities


class EconomicStrategies(object):
	_instance = None

	def __new__(cls):
		if cls._instance is None:
			cls._instance = super(EconomicStrategies, cls).__new__(cls)

			# populate strategies
			cls._instance.strategies = dict()
			for economicStrategyType in list(EconomicStrategyType):
				cls._instance.strategies[economicStrategyType] = EconomicStrategies._strategy(economicStrategyType)

		return cls._instance

	@classmethod
	def _strategy(cls, economicStrategyType: EconomicStrategyType):
		if economicStrategyType == EconomicStrategyType.needRecon:
			return NeedReconStrategy()
		elif economicStrategyType == EconomicStrategyType.enoughRecon:
			return EnoughReconStrategy()
		elif economicStrategyType == EconomicStrategyType.reallyNeedReconSea:
			return ReallyNeedReconSeaStrategy()
		elif economicStrategyType == EconomicStrategyType.earlyExpansion:
			return EarlyExpansionStrategy()
		elif economicStrategyType == EconomicStrategyType.foundCity:
			return FoundCityStrategy()
		elif economicStrategyType == EconomicStrategyType.losingMoney:
			return LosingMoneyStrategy()
		elif economicStrategyType == EconomicStrategyType.expandLikeCrazy:
			return ExpandLikeCrazyStrategy()
		elif economicStrategyType == EconomicStrategyType.expandToOtherContinents:
			return ExpandToOtherContinentsStrategy()
		elif economicStrategyType == EconomicStrategyType.needHappiness:
			return NeedHappinessStrategy()
		elif economicStrategyType == EconomicStrategyType.needHappinessCritical:
			return NeedHappinessCriticalStrategy()
		elif economicStrategyType == EconomicStrategyType.islandStart:
			return IslandStartStrategy()
		elif economicStrategyType == EconomicStrategyType.navalMap:
			return NavalMapStartStrategy()
		elif economicStrategyType == EconomicStrategyType.needReconSea:
			return NeedReconSeaStrategy()
		elif economicStrategyType == EconomicStrategyType.enoughReconSea:
			return EnoughReconSeaStrategy()
		elif economicStrategyType == EconomicStrategyType.enoughExpansion:
			return EnoughExpansionStrategy()
		elif economicStrategyType == EconomicStrategyType.needNavalGrowth:
			return NeedNavalGrowthStrategy()
		elif economicStrategyType == EconomicStrategyType.needNavalTileImprovement:
			return NeedNavalTileImprovementStrategy()
		elif economicStrategyType == EconomicStrategyType.tradeWithCityState:
			return TradeWithCityStateStrategy()
		elif economicStrategyType == EconomicStrategyType.needImprovementFood:
			return NeedGenericImprovementStrategy(YieldType.food)
		elif economicStrategyType == EconomicStrategyType.needImprovementProduction:
			return NeedGenericImprovementStrategy(YieldType.production)
		elif economicStrategyType == EconomicStrategyType.oneOrFewerCoastalCities:
			return OneOrFewerCoastalCitiesStrategy()
		elif economicStrategyType == EconomicStrategyType.haltGrowthBuildings:
			return HaltGrowthBuildingsStrategy()
		elif economicStrategyType == EconomicStrategyType.tooManyUnits:
			return TooManyUnitsStrategy()

		raise InvalidEnumError(economicStrategyType)

	def strategy(self, economicStrategyType: EconomicStrategyType) -> EconomicStrategy:
		return self._instance.strategies[economicStrategyType]

	@classmethod
	def weightThresholdModifier(cls, economicStrategyType: EconomicStrategyType, player) -> int:
		"""Figure out what the WeightThreshold Mod should be by looking at the Flavors for this player & the Strategy"""
		iWeightThresholdModifier: int = 0

		# Look at all Flavors for the Player & this Strategy
		for loopFlavorType in list(FlavorType):
			iPersonalityFlavor = player.valueOfPersonalityIndividualFlavor(loopFlavorType)
			iStrategyFlavorMod = economicStrategyType.flavors().value(loopFlavorType)

			iWeightThresholdModifier += (iPersonalityFlavor * iStrategyFlavorMod)

		return iWeightThresholdModifier
