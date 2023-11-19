import logging
import sys
from math import sqrt
from typing import Optional

from smarthexboard.smarthexboardlib.core.base import InvalidEnumError, ExtendedEnum
from smarthexboard.smarthexboardlib.game.ai.baseTypes import MilitaryStrategyType
from smarthexboard.smarthexboardlib.game.ai.economicStrategies import EconomicStrategyType
from smarthexboard.smarthexboardlib.game.ai.militaryStrategies import ReconStateType
from smarthexboard.smarthexboardlib.game.flavors import FlavorType, Flavors
from smarthexboard.smarthexboardlib.game.unitTypes import UnitTaskType, UnitType
from smarthexboard.smarthexboardlib.map.base import HexPoint, HexArea
from smarthexboard.smarthexboardlib.map.improvements import ImprovementType
from smarthexboard.smarthexboardlib.map.path_finding.finder import AStarPathfinder
from smarthexboard.smarthexboardlib.map.types import UnitDomainType, FeatureType, UnitMovementType


class EconomicStrategyAdoptionItem:
	def __init__(self, economicStrategyType: EconomicStrategyType, adopted: bool, turnOfAdoption: int):
		self.economicStrategyType = economicStrategyType
		self.adopted = adopted
		self.turnOfAdoption = turnOfAdoption


class EconomicStrategyAdoptions:
	def __init__(self):
		self.adoptions = []

		for economicStrategyType in list(EconomicStrategyType):
			self.adoptions.append(EconomicStrategyAdoptionItem(economicStrategyType, False, -1))

	def adopted(self, economicStrategyType: EconomicStrategyType) -> bool:
		item = next((adoptionItem for adoptionItem in self.adoptions if
					 adoptionItem.economicStrategyType == economicStrategyType), None)

		if item is not None:
			return item.adopted

		raise InvalidEnumError(economicStrategyType)

	def turnOfAdoption(self, economicStrategyType: EconomicStrategyType) -> int:
		item = next((adoptionItem for adoptionItem in self.adoptions if
					 adoptionItem.economicStrategyType == economicStrategyType), None)

		if item is not None:
			return item.turnOfAdoption

		raise InvalidEnumError

	def adopt(self, economicStrategyType: EconomicStrategyType, turnOfAdoption: int):
		item = next((adoptionItem for adoptionItem in self.adoptions if
					 adoptionItem.economicStrategyType == economicStrategyType), None)

		if item is not None:
			item.adopted = True
			item.turnOfAdoption = turnOfAdoption
		else:
			raise InvalidEnumError(economicStrategyType)

	def abandon(self, economicStrategyType: EconomicStrategyType):
		item = next((adoptionItem for adoptionItem in self.adoptions if
					 adoptionItem.economicStrategyType == economicStrategyType), None)

		if item is not None:
			item.adopted = False
			item.turnOfAdoption = -1
		else:
			raise InvalidEnumError(economicStrategyType)


class GoodyHutUnitAssignment:
	def __init__(self, unit, location: HexPoint):
		self.unit = unit
		self.location = location  # of goody hut

	def copy(self):
		return GoodyHutUnitAssignment(self.unit, self.location)


class ExplorationPlot:
	def __init__(self, location: HexPoint, rating: int):
		self.location = location
		self.rating = rating


class PurchaseType(ExtendedEnum):
	minorCivGift = 'minorCivGift'  # PURCHASE_TYPE_MINOR_CIV_GIFT
	unit = 'unit'  # PURCHASE_TYPE_UNIT
	building = 'building'  # PURCHASE_TYPE_BUILDING
	tile = 'tile'  # PURCHASE_TYPE_TILE
	majorCivTrade = 'majorCivTrade'  # PURCHASE_TYPE_MAJOR_CIV_TRADE


class PurchaseRequest:
	def __init__(self, purchaseType: PurchaseType, amount: int, priority: int = -1):
		self.purchaseType: PurchaseType = purchaseType
		self.amount: int = amount
		self.priority: int = priority

	def copy(self):
		return PurchaseRequest(self.purchaseType, self.amount, self.priority)


class EconomicAI:
	def __init__(self, player):
		self.player = player

		self.economicStrategyAdoptions = EconomicStrategyAdoptions()
		self.flavors = []
		self.reconStateValue: ReconStateType = ReconStateType.needed
		self.navalReconStateValue: ReconStateType = ReconStateType.needed
		self.goodyHutUnitAssignments: [GoodyHutUnitAssignment] = []
		self.explorationPlotsDirty: bool = False
		self.explorationPlotsArray: [ExplorationPlot] = []
		self.explorers = []

		self._explorersDisbandedValue: int = 0
		self._lastTurnWorkerDisbanded: int = -1
		self._requestedSavings: [PurchaseRequest] = []

	def doTurn(self, simulation):
		self.updatePlots(simulation)

		# Functions that need to run before we look at strategies
		self.doReconState(simulation)
		self.doAntiquitySites(simulation)

		for economicStrategyType in list(EconomicStrategyType):
			# check tech
			requiredTech = economicStrategyType.requiredTech()
			isTechGiven = True if requiredTech is None else self.player.hasTech(requiredTech)
			obsoleteTech = economicStrategyType.obsoleteTech()
			isTechObsolete = False if obsoleteTech is None else self.player.hasTech(obsoleteTech)

			# Minor Civs can't run some Strategies
			if self.player.isCityState() and economicStrategyType.isNoMinorCivs():
				continue

			# Do we already have this EconomicStrategy adopted?
			shouldCityStrategyStart = True
			if self.economicStrategyAdoptions.adopted(economicStrategyType):
				shouldCityStrategyStart = False
			elif not isTechGiven:
				shouldCityStrategyStart = False
			elif simulation.currentTurn < economicStrategyType.notBeforeTurnElapsed():  # Not time to check this yet?
				shouldCityStrategyStart = False

			shouldCityStrategyEnd = False
			if self.economicStrategyAdoptions.adopted(economicStrategyType):
				turnOfAdoption = self.economicStrategyAdoptions.turnOfAdoption(economicStrategyType)

				if economicStrategyType.checkEachTurns() > 0:
					# Is it a turn where we want to check to see if this Strategy is maintained?
					if (simulation.currentTurn - turnOfAdoption) % economicStrategyType.checkEachTurns() == 0:
						shouldCityStrategyEnd = True

				if shouldCityStrategyEnd and economicStrategyType.minimumAdoptionTurns() > 0:
					# Has the minimum # of turns passed for this Strategy?
					if simulation.currentTurn < (turnOfAdoption + economicStrategyType.minimumAdoptionTurns()):
						shouldCityStrategyEnd = False

			# Check EconomicStrategy Triggers
			# Functionality and existence of specific CityStrategies is hardcoded
			# here, but data is stored in XML so it's easier to modify
			if shouldCityStrategyStart or shouldCityStrategyEnd:
				# Has the Tech which obsoletes this Strategy? If so, Strategy should be deactivated regardless of
				# other factors
				strategyShouldBeActive = False

				# Strategy isn't obsolete, so test triggers as normal
				if not isTechObsolete:
					strategyShouldBeActive = economicStrategyType.shouldBeActive(self.player, simulation)

				# This variable keeps track of whether we should be doing something (i.e. Strategy is active now but
				# should be turned off, OR Strategy is inactive and should be enabled)
				adoptOrEndStrategy = False

				# Strategy should be on, and if it's not, turn it on
				if strategyShouldBeActive:
					if shouldCityStrategyStart:
						adoptOrEndStrategy = True
					elif shouldCityStrategyEnd:
						adoptOrEndStrategy = False
				else:  # Strategy should be off, and if it's not, turn it off
					if shouldCityStrategyStart:
						adoptOrEndStrategy = False
					elif shouldCityStrategyEnd:
						adoptOrEndStrategy = True

				if adoptOrEndStrategy:
					if shouldCityStrategyStart:
						self.economicStrategyAdoptions.adopt(economicStrategyType, simulation.currentTurn)
						logging.debug(f'Player {self.player.leader} has adopted {economicStrategyType} in {simulation.currentTurn}')
						self.updateFlavors()
					elif shouldCityStrategyEnd:
						self.economicStrategyAdoptions.abandon(economicStrategyType)
						logging.debug(f'Player {self.player.leader} has abandoned {economicStrategyType} in {simulation.currentTurn}')
						self.updateFlavors()

		if not self.player.isHuman():
			self.doHurry(simulation)
			self.doPlotPurchases(simulation)
			self.disbandExtraWorkers(simulation)
			self.disbandExtraArchaeologists(simulation)
			# self.player->GetCulture()->DoSwapGreatWorks();

	def reconState(self) -> ReconStateType:
		return self.reconStateValue

	def navalReconState(self) -> ReconStateType:
		return self.navalReconStateValue

	def doReconState(self, simulation):
		"""Determine how our recon efforts are going"""
		iPlotLoop: int = 0
		iDirectionLoop: int = 0
		iUnitLoop: int = 0
		bIsLand: bool = False
		bIsCoastalWater: bool = False

		if self.player.isCityState():
			self.reconStateValue = ReconStateType.enough  # RECON_STATE_ENOUGH
			self.navalReconStateValue = ReconStateType.enough  # RECON_STATE_ENOUGH
			return

		# Start at 1, so we don't get divide-by-0 errors
		# Land recon counters
		iNumLandPlotsRevealed: int = 1
		iNumLandPlotsWithAdjacentFog: int = 1

		# Naval recon counters
		iNumCoastalTilesRevealed: int = 1
		iNumCoastalTilesWithAdjacentFog: int = 1

		bNeedToLookAtDeepWaterAlso = self.player.canEmbarkAllWaterPassage()

		# Look at map size and gauge how much of it we know about
		for loopPoint in simulation.points():
			loopPlot = simulation.tileAt(loopPoint)

			if loopPlot.isDiscoveredBy(self.player):
				bIsLand: bool = False
				bIsCoastalWater: bool = False

				# Count Revealed Land Plots
				if not loopPlot.isWater():
					bIsLand = True
					iNumLandPlotsRevealed += 1
				elif loopPlot.isShallowWater() or bNeedToLookAtDeepWaterAlso:
					bIsCoastalWater = True
					iNumCoastalTilesRevealed += 1

				# Check adjacent Plots for THEIR visibility
				for adjacentPoint in loopPoint.neighbors():
					adjacentPlot = simulation.tileAt(adjacentPoint)

					if adjacentPlot is not None:
						# Check to see if adjacent Tile is land or water...
						if adjacentPlot.isWater():
							# This is a slight cheat (because the AI rules out water tiles) but helps prevents the AI from building too many Land explorers
							if (bNeedToLookAtDeepWaterAlso or adjacentPlot.isShallowWater()) and not adjacentPlot.isDiscoveredBy(self.player):
								iNumCoastalTilesWithAdjacentFog += 1
								break
						else:
							# This is a slight cheat (because the AI rules out water tiles) but helps prevents the AI
							# from building too many Land explorers
							if not adjacentPlot.isDiscoveredBy(self.player):
								iNumLandPlotsWithAdjacentFog += 1
								break

		# RECON ON OUR HOME CONTINENT

		# How many Units do we have exploring or being trained to do this job? The more Units we have the less
		# we want this Strategy
		iNumExploringUnits = self.player.numberOfUnitsOfTask(UnitTaskType.explore, simulation) + self._explorersDisbandedValue  #  WithUnitAI(UNITAI_EXPLORE, true, false)
		iStrategyWeight = 100  # AI_STRATEGY_EARLY_EXPLORATION_STARTING_WEIGHT
		iWeightThreshold = 110  # So result is a number from 10 to 100
		iWeightThreshold -= self.player.grandStrategyAI.personalityAndGrandStrategy(FlavorType.recon) * 10  # AI_STRATEGY_EARLY_EXPLORATION_WEIGHT_PER_FLAVOR

		# Safety check even if personality flavor is higher than expected
		if iWeightThreshold > 100:
			iWeightThreshold = 100

		iStrategyWeight *= iNumLandPlotsWithAdjacentFog
		iNumExplorerDivisor = iNumExploringUnits + 1  # AI_STRATEGY_EARLY_EXPLORATION_EXPLORERS_WEIGHT_DIVISOR
		iStrategyWeight /= (iNumExplorerDivisor * iNumExplorerDivisor)
		iStrategyWeight /= int(sqrt(iNumLandPlotsRevealed))

		if iStrategyWeight > iWeightThreshold:
			self.reconStateValue = ReconStateType.needed  # RECON_STATE_NEEDED
		elif iStrategyWeight > (iWeightThreshold / 4):
			self.reconStateValue = ReconStateType.neutral  # RECON_STATE_NEUTRAL
		else:
			self.reconStateValue = ReconStateType.enough  # RECON_STATE_ENOUGH

			# Return all/most warriors/spears to normal unit AI since have enough recon.
			# Keep at least 1 explorer through Turn 100.
			bSkipFirst: bool = simulation.currentTurn < 100
			for loopUnit in simulation.unitsOf(self.player):
				if loopUnit.task() == UnitTaskType.explore and loopUnit.hasTask(UnitTaskType.attack):
					if bSkipFirst:
						bSkipFirst = False
					else:
						loopUnit.updateTask(UnitTaskType.attack)  # ->AI_setUnitAIType(UNITAI_ATTACK);
						logging.debug(f"Assigning exploring {loopUnit.name()} back to attack AI, {loopUnit.location}")

		# NAVAL RECON ACROSS THE ENTIRE MAP

		# No coastal cities?  Moot point...
		bFoundCoastalCity = False
		for loopCity in simulation.citiesOf(self.player):
			if bFoundCoastalCity:
				continue

			if loopCity.isCoastal(simulation):
				bFoundCoastalCity = True

		if not bFoundCoastalCity:
			self.navalReconStateValue = ReconStateType.enough  # RECON_STATE_ENOUGH
		else:
			# How many Units do we have exploring or being trained to do this job? The more Units
			# we have the less we want this Strategy
			iNumExploringUnits = self.player.numberOfUnitsOfTask(UnitTaskType.exploreSea, simulation)  # getNumUnitsWithUnitAI(UNITAI_EXPLORE_SEA, true, true);
			iStrategyWeight = 100  # AI_STRATEGY_EARLY_EXPLORATION_STARTING_WEIGHT
			iWeightThreshold = 110 # So result is a number from 10 to 100
			iWeightThreshold -= self.player.grandStrategyAI.personalityAndGrandStrategy(FlavorType.navalRecon) * 10  # AI_STRATEGY_EARLY_EXPLORATION_WEIGHT_PER_FLAVOR

			# Safety check even if personality flavor is higher than expected
			if iWeightThreshold > 100:
				iWeightThreshold = 100

			iStrategyWeight *= iNumCoastalTilesWithAdjacentFog
			iNumExplorerDivisor = iNumExploringUnits + 1  # AI_STRATEGY_EARLY_EXPLORATION_EXPLORERS_WEIGHT_DIVISOR
			iStrategyWeight /= (iNumExplorerDivisor * iNumExplorerDivisor)
			iStrategyWeight /= int(sqrt(iNumCoastalTilesRevealed))

			if iStrategyWeight > iWeightThreshold:
				self.navalReconStateValue = ReconStateType.needed  # RECON_STATE_NEEDED
			elif iStrategyWeight > (iWeightThreshold / 4):
				self.navalReconStateValue = ReconStateType.neutral  # RECON_STATE_NEUTRAL
			else:
				self.navalReconStateValue = ReconStateType.enough  # RECON_STATE_ENOUGH

			# Return all/most boats to normal unit AI since have enough recon
			bSkipFirst = (self.navalReconStateValue == ReconStateType.neutral)
			for loopUnit in simulation.unitsOf(self.player):
				if loopUnit.task() == UnitTaskType.exploreSea and loopUnit.hasTask(UnitTaskType.attackSea):
					if bSkipFirst:
						bSkipFirst = False
					else:
						loopUnit.updateTask(UnitTaskType.attackSea)
						logging.debug(f"Assigning naval exploring {loopUnit.name()} back to attack AI, {loopUnit.location}")

		return

	def updateFlavors(self):
		self.flavors = Flavors([])

		for economicStrategyType in list(EconomicStrategyType):
			if self.economicStrategyAdoptions.adopted(economicStrategyType):
				for economicStrategyTypeFlavor in economicStrategyType.flavors():
					self.flavors += economicStrategyTypeFlavor

	def updatePlots(self, simulation):
		"""Go through the plots for the exploration automation to evaluate"""
		# reset all plots
		self.explorationPlotsArray = []
		self.goodyHutUnitAssignments = []

		# find the center of all the cities
		totalX = 0
		totalY = 0
		cityCount = 0

		for city in simulation.citiesOf(self.player):
			totalX += city.location.x
			totalY += city.location.y
			cityCount += 1

		for point in simulation.points():
			tile = simulation.tileAt(point)

			if not tile.isDiscoveredBy(self.player):
				continue

			if tile.hasImprovement(ImprovementType.goodyHut) and not simulation.isEnemyVisibleAt(point, self.player):
				self.goodyHutUnitAssignments.append(GoodyHutUnitAssignment(None, point))

			if tile.hasImprovement(ImprovementType.barbarianCamp) and not simulation.isEnemyVisibleAt(point, self.player):
				self.goodyHutUnitAssignments.append(GoodyHutUnitAssignment(None, point))

			domain: UnitDomainType = UnitDomainType.land
			if tile.terrain().isWater():
				domain = UnitDomainType.sea

			score = self.scoreExplore(point, self.player, range=1, domain=domain, simulation=simulation)
			if score <= 0:
				continue

			self.explorationPlotsArray.append(ExplorationPlot(point, score))

		# assign explorers to goody huts

		# build explorer list
		self.explorers = []

		for unit in simulation.unitsOf(self.player):

			# non - automated human - controlled units should not be considered
			if self.player.isHuman() and not unit.isAutomated():
				continue

			if unit.task() != UnitTaskType.explore and unit.automateType() != UnitTaskType.explore:
				continue

			if unit.army() is not None:
				continue

			self.explorers.append(unit)

		if len(self.explorers) >= len(self.goodyHutUnitAssignments):
			self.assignExplorersToHuts(simulation)
		else:
			self.assignHutsToExplorers(simulation)

		self.explorationPlotsDirty = False

	def lastTurnBuilderDisbanded(self) -> Optional[int]:
		return None

	def unitTargetGoodyPlot(self, unit, simulation):
		if self.explorationPlotsDirty:
			self.updatePlots(simulation)

		for goodyHutUnitAssignment in self.goodyHutUnitAssignments:
			goodyHutUnit = goodyHutUnitAssignment.unit
			if goodyHutUnit is not None:
				if goodyHutUnit == unit:
					goodyHutPlot = simulation.tileAt(goodyHutUnitAssignment.location)
					return goodyHutPlot

		return None

	def assignExplorersToHuts(self, simulation):
		for goodyHutUnitAssignment in self.goodyHutUnitAssignments:
			if simulation.tileAt(goodyHutUnitAssignment.location) is None:
				continue

			closestEstimateTurns = sys.maxsize
			closestUnit = None

			for explorer in self.explorers:
				distance = explorer.location.distance(goodyHutUnitAssignment.location)

				estimateTurns = sys.maxsize
				if explorer.maxMoves(simulation) >= 1:
					estimateTurns = distance / explorer.maxMoves(simulation)

				if estimateTurns < closestEstimateTurns:
					# Now check path
					pathFinderDataSource = simulation.ignoreUnitsPathfinderDataSource(
						explorer.movementType(),
						self.player,
						canEmbark=True,
						canEnterOcean=False
					)
					pathFinder = AStarPathfinder(pathFinderDataSource)

					if pathFinder.doesPathExist(explorer.location, goodyHutUnitAssignment.location):
						closestEstimateTurns = estimateTurns
						closestUnit = explorer

			if closestUnit is not None:
				goodyHutUnitAssignment.unit = closestUnit
				self.explorers = list(filter(lambda ex: ex.location != closestUnit.location, self.explorers))

		return

	def assignHutsToExplorers(self, simulation):
		# Create copy list of huts
		goodyHutUnitAssignmentsCopy = [g.copy() for g in self.goodyHutUnitAssignments]

		for explorer in self.explorers:
			hutLocation: Optional[HexPoint] = None
			closestEstimateTurns: int = sys.maxsize

			for goodyHutUnitAssignment in goodyHutUnitAssignmentsCopy:
				if simulation.tileAt(goodyHutUnitAssignment.location) is None:
					continue

				distance = goodyHutUnitAssignment.location.distance(explorer.location)

				estimateTurns = sys.maxsize
				if explorer.maxMoves(simulation) >= 1:
					estimateTurns = distance / explorer.maxMoves(simulation)

				if estimateTurns < closestEstimateTurns:
					# Now check path
					pathFinderDataSource = simulation.ignoreUnitsPathfinderDataSource(
						explorer.movementType(),
						self.player,
						canEmbark=True,
						canEnterOcean=False
					)
					pathFinder = AStarPathfinder(pathFinderDataSource)

					if pathFinder.shortestPath(explorer.location, goodyHutUnitAssignment.location) is not None:
						closestEstimateTurns = estimateTurns
						hutLocation = goodyHutUnitAssignment.location

			if hutLocation is not None:
				goodyHutUnitAssignmentsCopy = list(filter(lambda it: it.location != hutLocation, goodyHutUnitAssignmentsCopy))

				goodyHutUnitAssignment = next(filter(lambda it: it.location == hutLocation, self.goodyHutUnitAssignments), None)

				if goodyHutUnitAssignment is None:
					raise Exception("cant find good hut assignment")

				goodyHutUnitAssignment.unit = explorer

		return

	def scoreExplore(self, plot: HexPoint, player, range: int, domain: UnitDomainType, simulation) -> int:
		resultValue = 0
		adjacencyBonus = 1
		badScore = 10
		goodScore = 100
		reallyGoodScore = 200

		for evalPoint in plot.areaWithRadius(range):
			if evalPoint == plot:
				continue

			evalTile = simulation.tileAt(evalPoint)

			if evalTile is None:
				continue

			if evalTile.isDiscoveredBy(self.player):
				continue

			if simulation.isAdjacentDiscovered(evalPoint, self.player):

				if evalPoint.distance(plot) > 1:
					viewBlocked = True
					for adjacent in evalPoint.neighbors():

						adjacentTile = simulation.tileAt(adjacent)
						if adjacentTile is None:
							continue

						if adjacentTile.isDiscoveredBy(self.player):
							distance = adjacent.distance(plot)
							if distance > range:
								continue

							# this cheats, because we can't be sure that between the target and the viewer
							if evalTile.canSeeTile(adjacentTile, self.player, range, hasSentry=False, simulation=simulation):
								viewBlocked = False

							if not viewBlocked:
								break

					if viewBlocked:
						continue

				# "cheating" to look to see what the next tile is.
				# a human should be able to do this by looking at the transition from the tile to the next
				if domain == UnitDomainType.sea:
					if evalTile.terrain().isWater():
						resultValue += badScore
					elif evalTile.hasFeature(FeatureType.mountains) or evalTile.isHills():
						resultValue += goodScore
					else:
						resultValue += reallyGoodScore

				elif domain == UnitDomainType.land:
					if evalTile.hasFeature(FeatureType.mountains) or evalTile.isHills():
						resultValue += badScore
					elif evalTile.isHills():
						resultValue += reallyGoodScore
					else:
						resultValue += goodScore

			else:
				resultValue += goodScore

			distance = plot.distance(evalPoint)
			resultValue += (range - distance) * adjacencyBonus

		return resultValue

	def minimumSettleFertility(self) -> int:
		return 50  # AI_STRATEGY_MINIMUM_SETTLE_FERTILITY

	def isUsingStrategy(self, economicStrategy: EconomicStrategyType) -> bool:
		return self.economicStrategyAdoptions.adopted(economicStrategy)

	def incrementExplorersDisbanded(self):
		self._explorersDisbandedValue += 1

	def explorersDisbanded(self) -> int:
		return self._explorersDisbandedValue

	def isSavingForPurchase(self, purchaseType: PurchaseType) -> bool:
		"""Have we put in a request for this type of purchase?"""
		item = self._purchaseOf(purchaseType)
		return item is not None and item.amount > 0

	def buildersToCitiesRatio(self, simulation) -> float:
		"""What is the ratio of workers we have to the number of cities we have? GetWorkersToCitiesRatio"""
		numberOfBuilders: int = self.player.numberOfUnitsOfType(UnitType.builder, simulation)
		numberOfCities: int = self.player.numberOfCities(simulation)

		if numberOfCities == 0:
			return 1.0

		return numberOfBuilders / numberOfCities

	def improvedToImprovablePlotsRatio(self, simulation) -> float:
		"""What is the ratio of our improved plots to all the plots we are able to improve?"""
		aiPlots: HexArea = self.player.area()
		iNumValidPlots: int = 0
		iNumImprovedPlots: int = 0

		for pt in aiPlots.points():
			tile = simulation.tileAt(pt)

			if tile is None:
				continue

			if tile.isWater() or tile.isImpassable(UnitMovementType.walk) or tile.hasFeature(FeatureType.mountains) or tile.isCity():
				continue

			iNumValidPlots += 1

			if tile.hasAnyImprovement() and not tile.isImprovementPillaged():
				iNumImprovedPlots += 1

		# Avoid potential division by 0
		if iNumValidPlots <= 0:
			return 1.0

		return iNumImprovedPlots / iNumValidPlots

	def _purchaseOf(self, purchaseType: PurchaseType) -> Optional[PurchaseRequest]:
		return next((item for item in self._requestedSavings if item.purchaseType == purchaseType), None)

	def startSavingForPurchase(self, purchaseType: PurchaseType, amount: int, priority: int):
		"""Request that the AI set aside this much money"""
		item: Optional[PurchaseRequest] = self._purchaseOf(purchaseType)

		if item is None:
			self._requestedSavings.append(PurchaseRequest(purchaseType, amount, priority))
		else:
			item.amount = amount
			item.priority = priority

	def isSavingForPurchase(self, purchaseType: PurchaseType) -> bool:
		"""Have we put in a request for this type of purchase?"""
		item: Optional[PurchaseRequest] = self._purchaseOf(purchaseType)

		if item is not None:
			return item.amount > 0

		return False

	"""Cancel savings request"""
	def cancelSaveForPurchase(self, purchaseType: PurchaseType):
		item: Optional[PurchaseRequest] = self._purchaseOf(purchaseType)

		if item is not None:
			item.amount = 0
			item.priority = 0

	def canWithdrawMoneyForPurchase(self, purchaseType: PurchaseType, amount: int, priority: int = -1) -> bool:
		""" Returns true if have enough saved up for this purchase. May return false if have enough but higher priority requests have dibs on the gold.
		(Priority of -1 (default parameter) means use existing priority"""
		balance = self.player.treasury.value()

		# Update this item's priority
		if priority != -1:
			item: Optional[PurchaseRequest] = self._purchaseOf(purchaseType)

			if item is None:
				self._requestedSavings.append(PurchaseRequest(purchaseType, 0, priority))
			else:
				item.priority = priority

			# Copy into temp array and sort by priority
			tempRequestedSavings = [g.copy() for g in self._requestedSavings]
			tempRequestedSavings = sorted(tempRequestedSavings, key=lambda x: x.priority, reverse=True)

			for request in tempRequestedSavings:
				# Is this higher priority than the request we care about?
				if request.purchaseType != purchaseType:
					balance -= request.amount

					# No money left?
					if balance <= 0:
						return False

				# Is this the one, if so, check balance remaining
				elif request.purchaseType == purchaseType:
					return balance >= amount

		raise Exception()

	def doAntiquitySites(self, simulation):
		# fixme
		pass

	def disbandExtraWorkers(self, simulation):
		# Are we running at a deficit?
		bInDeficit: bool = self.economicStrategyAdoptions.adopted(EconomicStrategyType.losingMoney)

		iGoldSpentOnUnits = self.player.treasury.goldForUnitMaintenance(simulation)
		iAverageGoldPerUnit = iGoldSpentOnUnits / (max(1, self.player.numberOfUnits(simulation)))

		if not bInDeficit and iAverageGoldPerUnit <= 4:
			return

		# antonjs: consider: make calls to GetWorkersToCitiesRatio and GetImprovedToImprovablePlotsRatio
		# instead, is the code similar enough?

		fWorstCaseRatio = 0.25  # one worker for four cities
		iNumWorkers = self.player.numberOfUnitsOfTask(UnitTaskType.work, simulation)  # (UNITAI_WORKER, true, false);
		iNumCities = self.player.numberOfCities(simulation)

		if iNumCities == 0:
			return

		fCurrentRatio = iNumWorkers / float(iNumCities)
		if fCurrentRatio <= fWorstCaseRatio or iNumWorkers == 1:
			return

		aiPlots: HexArea = self.player.area()
		iNumValidPlots: int = 0
		iNumImprovedPlots: int = 0
		for loopPoint in aiPlots.points():
			loopPlot = simulation.tileAt(loopPoint)

			if loopPlot.isWater() or loopPlot.isImpassable(UnitMovementType.walk) \
				or loopPlot.feature() == FeatureType.mountains or loopPlot.isCity():
				continue

			iNumValidPlots += 1

			if loopPlot.hasAnyImprovement() and not loopPlot.isImprovementPillaged():
				iNumImprovedPlots += 1

		# potential div by zero
		if iNumValidPlots <= 0:
			return

		iNumUnimprovedPlots = iNumValidPlots - iNumImprovedPlots

		# less than two thirds of the plots are improved, don't discard anybody
		fRatio = iNumImprovedPlots / float(iNumValidPlots)
		if fRatio < 2 / 3.0:
			return

		iWorkersPerUnimprovedPlot = 5
		iMinWorkers = iNumUnimprovedPlots / iWorkersPerUnimprovedPlot
		if (iNumUnimprovedPlots % iWorkersPerUnimprovedPlot) > 0:
			iMinWorkers += 1

		pCapital = self.player.capitalCity(simulation)
		if pCapital is None:
			return

		for loopCity in simulation.citiesOf(self.player):
			if loopCity == pCapital:
				continue

			# builder can no longer build roads
			# if (pCapital.area() == loopCity.area() and not loopCity.isRouteToCapitalConnected()):
			#	iMinWorkers += 1
			pass

		if iNumWorkers <= iMinWorkers:
			return

		self._lastTurnWorkerDisbanded = simulation.currentTurn

		unit = self.findWorkerToScrap(simulation)
		if unit is None:
			return

		unit.scrap(simulation)
		# self.logScrapUnit(pUnit, iNumWorkers, iNumCities, iNumImprovedPlots, iNumValidPlots);
		return

	def findWorkerToScrap(self, simulation):
		# Look at map for loose workers
		for loopUnit in simulation.unitsOf(self.player):
			if loopUnit.domain() == UnitDomainType.land and loopUnit.unitType == UnitType.builder and not loopUnit.isCombatUnit():
				return loopUnit

		return None

	def doHurry(self, simulation):
		# fixme
		pass

	def doPlotPurchases(self, simulation):
		"""Spend money buying plots"""
		bestCity = None
		bestLocation: Optional[HexPoint] = None
		tempLocation: Optional[HexPoint] = None

		iScore: int = 0
		iLoop: int = 0

		# No plot buying for minors
		if self.player.isCityState():
			return

		# No plot buying when at war
		if self.player.militaryAI.adopted(MilitaryStrategyType.atWar):
			return

		# Set up the parameters
		iBestScore: int = 150  # AI_GOLD_PRIORITY_MINIMUM_PLOT_BUY_VALUE
		iCurrentCost: int = self.player.buyPlotCost()
		iGoldForHalfCost: int = 1000  # AI_GOLD_BALANCE_TO_HALVE_PLOT_BUY_MINIMUM
		iBalance: int = self.player.treasury.value()

		# Let's always invest any money we have in plot purchases
		# (LATER - - save up money to spend at newly settled cities)
		if iCurrentCost < iBalance and iGoldForHalfCost > iCurrentCost:
			# Lower our requirements if we're building up a sizable treasury
			iDiscountPercent: int = int(50 * (iBalance - iCurrentCost) / (iGoldForHalfCost - iCurrentCost))
			iBestScore = int(iBestScore - (iBestScore * iDiscountPercent / 100))

			# Find the best city to buy a plot
			for loopCity in simulation.citiesOf(self.player):
				if loopCity.canBuyAnyPlot(simulation):
					iScore, tempLocation = loopCity.buyPlotScore(simulation)

					if iScore > iBestScore:
						bestCity = loopCity
						iBestScore = iScore
						bestLocation = tempLocation

			if bestCity is not None and bestLocation is not None:
				iCost = bestCity.buyPlotCost(bestLocation, simulation)

				if self.canWithdrawMoneyForPurchase(PurchaseType.tile, iCost, iBestScore):
					logging.info(f'Buying plot, {bestLocation}, Cost: {iCost}, Balance (before buy): {iBalance}, Priority: {iBestScore}')
					bestCity.doBuyPlot(bestLocation, simulation)

		return

	def disbandExtraArchaeologists(self, simulation):
		# fixme
		pass
