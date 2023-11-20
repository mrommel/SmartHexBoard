import logging
import operator
import random
from typing import Optional, Union, List

from smarthexboard.smarthexboardlib.core.base import WeightedBaseList
from smarthexboard.smarthexboardlib.game.ai.barbarians import BarbarianAI
from smarthexboard.smarthexboardlib.game.ai.religions import Religions
from smarthexboard.smarthexboardlib.game.ai.tactics import TacticalAnalysisMap
from smarthexboard.smarthexboardlib.game.baseTypes import HandicapType, GameState, ArtifactType, ReplayEventType
from smarthexboard.smarthexboardlib.game.buildings import BuildingType
from smarthexboard.smarthexboardlib.game.cities import City
from smarthexboard.smarthexboardlib.game.cityStates import CityStateType, CityStateQuestType
from smarthexboard.smarthexboardlib.game.civilizations import LeaderType, CivilizationType
from smarthexboard.smarthexboardlib.game.deals import GameDeals
from smarthexboard.smarthexboardlib.game.districts import DistrictType
from smarthexboard.smarthexboardlib.game.governments import GovernmentType
from smarthexboard.smarthexboardlib.game.greatPersons import GreatPersonType, GreatPersons, GreatPerson
from smarthexboard.smarthexboardlib.game.moments import MomentType
from smarthexboard.smarthexboardlib.game.notifications import NotificationType
from smarthexboard.smarthexboardlib.game.players import Player, PlayerReligion
from smarthexboard.smarthexboardlib.game.promotions import UnitPromotionType
from smarthexboard.smarthexboardlib.game.religions import PantheonType, ReligionType
from smarthexboard.smarthexboardlib.game.states.accessLevels import AccessLevel
from smarthexboard.smarthexboardlib.game.states.builds import BuildType
from smarthexboard.smarthexboardlib.game.states.gossips import GossipType, GossipSourceType, GossipItem
from smarthexboard.smarthexboardlib.game.states.ui import ScreenType
from smarthexboard.smarthexboardlib.game.states.victories import VictoryType
from smarthexboard.smarthexboardlib.game.types import TechType, EraType, CivicType
from smarthexboard.smarthexboardlib.game.unitTypes import UnitMapType, UnitAbilityType, MoveOption
from smarthexboard.smarthexboardlib.game.units import Unit, UnitType
from smarthexboard.smarthexboardlib.game.wonders import WonderType
from smarthexboard.smarthexboardlib.map import constants
from smarthexboard.smarthexboardlib.map.base import HexPoint, Size, HexArea
from smarthexboard.smarthexboardlib.map.evaluators import CitySiteEvaluator, MapAnalyzer
from smarthexboard.smarthexboardlib.map.improvements import ImprovementType
from smarthexboard.smarthexboardlib.map.map import MapModel, Tile, ContinentType, Continent
from smarthexboard.smarthexboardlib.map.path_finding.finder import AStarPathfinder, MoveTypeIgnoreUnitsOptions, \
	MoveTypeIgnoreUnitsPathfinderDataSource, InfluencePathfinderDataSource, MoveTypeUnitAwarePathfinderDataSource, \
	MoveTypeUnitAwareOptions
from smarthexboard.smarthexboardlib.map.path_finding.path import HexPath
from smarthexboard.smarthexboardlib.map.types import FeatureType, Tutorials, UnitMovementType, MapSize, ArchaeologicalRecord, ArchaeologicalRecordType, \
	ResourceType, TerrainType


class GameRankingData:
	def __init__(self, rankingDict: Optional[dict] = None):
		pass

	def addCulturePerTurn(self, culture: float, leader: LeaderType):
		pass

	def addGoldBalance(self, gold: float, leader: LeaderType):
		pass

	def addTotalCities(self, cities: int, leader: LeaderType):
		pass

	def addTotalCitiesFounded(self, citiesFounded: int, leader: LeaderType):
		pass

	def addTotalCitiesLost(self, citiesLost: int, leader: LeaderType):
		pass

	def addTotalDistrictsConstructed(self, districtsConstructed: int, leader: LeaderType):
		pass

	def addTotalWondersConstructed(self, wondersConstructed: int, leader: LeaderType):
		pass

	def addTotalBuildingsConstructed(self, buildingsConstructed: int, leader: LeaderType):
		pass

	def addTotalScore(self, score: float, leader: LeaderType):
		pass

	def addSciencePerTurn(self, science: float, leader: LeaderType):
		pass

	def addFaithPerTurn(self, faith: float, leader: LeaderType):
		pass

	def addTotalReligionsFounded(self, religionsFounded: int, leader: LeaderType):
		pass

	def addTotalGreatPeopleEarned(self, greatPeopleEarned: int, leader: LeaderType):
		pass

	def addTotalWarDeclarationsReceived(self, warDeclarationsReceived: int, leader: LeaderType):
		pass

	def addTotalPantheonsFounded(self, pantheonsFounded: int, leader: LeaderType):
		pass


class GameWonders:
	def __init__(self):
		self._wonders: [WonderType] = []


	def buildWonder(self, wonderType: WonderType):
		self._wonders.append(wonderType)


class EraHistogram(WeightedBaseList):
	def __init__(self):
		super().__init__()

	def fill(self):
		for era in list(EraType):
			self.addWeight(0.0, era)


class ReplayEvent:
	def __init__(self, turn: int, eventType: ReplayEventType, message: str, location: HexPoint):
		self.turn: int = turn
		self.eventType: ReplayEventType = eventType
		self.message: str = message
		self.location: HexPoint = location


class GameModel:
	pass


class GameModel:
	def __init__(self, victoryTypes: Union[dict, List[VictoryType]], handicap: Optional[HandicapType]=None, turnsElapsed: Optional[int]=None, players: Optional[List[Player]]=None, map: Optional[MapModel]=None):
		if isinstance(victoryTypes, List):
			self.turnSliceValue = 0
			self.waitDiploPlayer = None
			self.players: [Player] = players
			self._activePlayer: Optional[Player] = None
			self.currentTurn: int = turnsElapsed
			self.maxTurns: int = 500
			self.victoryTypes: [VictoryType] = victoryTypes
			self.handicap: HandicapType = handicap
			self._map: MapModel = map
			self.userInterface = None
			self._gameStateValue: GameState = GameState.on
			self._tacticalAnalysisMap = TacticalAnalysisMap(Size(map.width, map.height))
			self._rankingData = GameRankingData()

			# game ai
			self.barbarianAI = BarbarianAI(self)
			self._religions = Religions()

			# analyze map
			analyzer = MapAnalyzer(self._map)
			analyzer.analyze()

			# stats
			self.discoveredContinents = []
			self.wondersBuilt = GameWonders()
			self._worldEraValue: EraType = EraType.ancient
			self._gameWinLeaderValue: Optional[LeaderType] = None
			self._gameWinVictoryValue: Optional[VictoryType] = None
			self._spawnedArchaeologySites = False
			self.greatPersons = GreatPersons()
			self.gameDeals = GameDeals()

			self.replayEvents = []
		elif isinstance(victoryTypes, dict):
			self.turnSliceValue = 0
			self.waitDiploPlayer = None
			self.players: [Player] = [Player(player_dict) for player_dict in victoryTypes['players']]
			self._activePlayer: Optional[Player] = None  # fixme
			self.currentTurn: int = victoryTypes['currentTurn']
			self.maxTurns: int = victoryTypes['maxTurns']
			self.victoryTypes: [VictoryType] = victoryTypes['victoryTypes']
			self.handicap: HandicapType = victoryTypes['handicap']
			self._map: MapModel = MapModel(victoryTypes['_map'])

			# post-process
			self._map.postProcess(self)

			self.userInterface = None
			self._gameStateValue: GameState = victoryTypes['_gameStateValue']
			self._tacticalAnalysisMap = TacticalAnalysisMap(Size(self._map.width, self._map.height))
			self._rankingData = GameRankingData(victoryTypes['_rankingData'])

			# game ai
			self.barbarianAI = BarbarianAI(victoryTypes['barbarianAI'])
			self._religions = Religions()  # fixme

			# analyze map
			analyzer = MapAnalyzer(self._map)
			analyzer.analyze()

			# stats
			self.discoveredContinents = victoryTypes['discoveredContinents']
			self.wondersBuilt = victoryTypes['wondersBuilt']
			self._worldEraValue: EraType = victoryTypes['_worldEraValue']
			self._gameWinLeaderValue: Optional[LeaderType] = victoryTypes['_gameWinLeaderValue']
			self._gameWinVictoryValue: Optional[VictoryType] = victoryTypes['_gameWinVictoryValue']
			self._spawnedArchaeologySites = victoryTypes['_spawnedArchaeologySites']
			self.greatPersons = GreatPersons()  # fixme
			self.gameDeals = GameDeals()  # fixme

			self.replayEvents = victoryTypes['replayEvents']
		else:
			raise Exception('Invalid combination of parameters')

	def update(self):
		if self.userInterface is None:
			raise Exception("no UI")

		if self.isWaitingForBlockingInput():
			if not self.userInterface.isShown(ScreenType.diplomatic):
				# when diplomatic screen is visible - we can't update
				self.waitDiploPlayer.doTurnPostDiplomacy(self)
				self.setWaitingForBlockingInput(None)
			else:
				return

		# if the game is single player, it's ok to block all processing until
		# the user selects an extended match or quits.
		if self.gameState() == GameState.over:
			# self.testExtendedGame()
			return

		# self.sendPlayerOptions()

		if self.turnSlice() == 0 and not self.isPaused():
			# gDLL->AutoSave(true);
			pass

		# If there are no active players, move on to the AI
		if self.numGameTurnActive() == 0:
			self.doTurn()

		# Check for paused again, the doTurn call might have called something that paused the game and we don't want
		# an update to sneak through
		if not self.isPaused():
			# self.updateScore()
			# self.updateWar()
			self.updateMoves()

		# And again, the player can change after the automoves and that can pause the game
		if not self.isPaused():
			self.updateTimers()

			self.updatePlayers(self)  # slewis added!

			# self.testAlive()

			if not self.humanPlayer().isAlive():
				self.setGameStateTo(GameState.over)

			# next player ???
			self.checkPlayerTurnDeactivate()

			self.changeTurnSliceBy(1)

	def capitalOf(self, player: Player) -> City:
		return self._map.capitalOf(player)

	def points(self) -> [HexPoint]:
		return self._map.points()

	def unitsOf(self, player: Player) -> [Unit]:
		return self._map.unitsOf(player)

	def unitsAt(self, location: HexPoint) -> [Unit]:
		return self._map.unitsAt(location)

	def unitAt(self, location: HexPoint, unitMapType: UnitMapType) -> Optional[Unit]:
		return self._map.unitAt(location, unitMapType)

	def areUnitsAt(self, location: HexPoint) -> bool:
		return len(self._map.unitsAt(location)) > 0

	def addUnit(self, unit):
		self._map.addUnit(unit)

	def removeUnit(self, unit):
		self._map.removeUnit(unit)

	def cityAt(self, location: HexPoint) -> Optional[City]:
		return self._map.cityAt(location)

	def citiesOf(self, player) -> [City]:
		return self._map.citiesOf(player)

	def citiesInAreaOf(self, player, area) -> [City]:
		return self._map.citiesInAreaOf(player, area)

	def citiesIn(self, area) -> [City]:
		return self._map.citiesIn(area)

	def addCity(self, city):
		tile = self.tileAt(city.location)

		# check feature removal
		featureRemovalSurplus = 0
		featureRemovalSurplus += tile.productionFromFeatureRemoval(BuildType.removeForest)
		featureRemovalSurplus += tile.productionFromFeatureRemoval(BuildType.removeRainforest)
		featureRemovalSurplus += tile.productionFromFeatureRemoval(BuildType.removeMarsh)

		city.changeFeatureProduction(featureRemovalSurplus)

		tile.setFeature(FeatureType.none)

		self._map.addCity(city, simulation=self)
		# self.userInterface?.show(city: city)

		# update area around the city
		for pt in city.location.areaWithRadius(3):
			if not self._map.valid(pt):
				continue

			neighborTile = self.tileAt(pt)
			self.userInterface.refreshTile(neighborTile)

		# update eureka
		if not city.player.techs.eurekaTriggeredFor(TechType.sailing):
			if self._map.isCoastalAt(city.location):
				city.player.techs.triggerEurekaFor(TechType.sailing, self)

		return

	def deleteCity(self, city):
		self._map.deleteCity(city)

	def tileAt(self, x_or_hex: Union[int, HexPoint], y: Optional[int] = None) -> Optional[Tile]:
		return self._map.tileAt(x_or_hex, y)

	def tilesIn(self, area) -> [Tile]:
		return self._map.tilesIn(area)

	def riverAt(self, location) -> bool:
		return self._map.riverAt(location)

	def valid(self, point: HexPoint) -> bool:
		return self._map.valid(point)

	def isCoastalAt(self, location) -> bool:
		return self._map.isCoastalAt(location)

	def tutorial(self) -> Tutorials:
		return Tutorials.none

	def showTutorialInfos(self) -> bool:
		return False

	def isWaitingForBlockingInput(self) -> bool:
		return self.waitDiploPlayer is not None

	def gameState(self) -> GameState:
		return self._gameStateValue

	def setGameStateTo(self, gameState: GameState):
		logging.warning(f'ooo Game has be set to {gameState} in turn {self.currentTurn} ooo')
		self._gameStateValue = gameState

	def turnSlice(self) -> int:
		return self.turnSliceValue

	def setTurnSliceTo(self, value: int):
		self.turnSliceValue = value

	def changeTurnSliceBy(self, delta: int):
		self.turnSliceValue += delta

	def isPaused(self):
		return False

	def numGameTurnActive(self):
		numActive = 0
		for player in self.players:
			if player.isAlive() and player.isActive():
				numActive += 1

		return numActive

	def doTurn(self):
		logging.info('')
		logging.info(f"::: TURN {self.currentTurn + 1} starts now :::")
		logging.info('')

		self.humanPlayer().resetFinishTurnButtonPressed()

		self.barbarianAI.doTurn(self)
		self._religions.doTurn(self)

		# doUpdateCacheOnTurn();
		# DoUpdateCachedWorldReligionTechProgress();

		self.updateScore()

		self.gameDeals.doTurn(self)

		for player in self.players:
			player.prepareTurn(self)

		# map.doTurn()

		# GC.GetEngineUserInterface()->doTurn();

		self.barbarianAI.doCamps(self)
		self.barbarianAI.doUnits(self)

		# incrementGameTurn();
		self.currentTurn += 1

		# Sequential turns.
		# Activate the << FIRST >> player we find from the start, human or AI, who wants a sequential turn.
		for player in self.players:
			if player.isAlive():
				player.startTurn(self)

				break

		# self.doUnitedNationsCountdown();

		self.doWorldEra()

		# Victory stuff
		self.doTestVictory()

		# Who's Winning every 25 turns (to be un-hardcoded later)
		human = self.humanPlayer()
		if human.isAlive():
			if self.currentTurn % 25 == 0:
				# This popup is the sync rand, so beware
				# self.userInterface.showScreen(screenType: .interimRanking, city: nil, other: nil, data: nil)
				pass

	def humanPlayer(self) -> Optional[Player]:
		return next((player for player in self.players if player.isHuman()), None)

	def barbarianPlayer(self) -> Optional[Player]:
		return next((player for player in self.players if player.isBarbarian()), None)

	def freeCityPlayer(self) -> Optional[Player]:
		return next((player for player in self.players if player.leader == LeaderType.freeCities), None)

	def updateScore(self):
		for player in self.players:
			if player.isBarbarian() or player.isFreeCity():
				continue

			culturePerTurn = player.culture(self, consume=False)
			self._rankingData.addCulturePerTurn(culturePerTurn, player.leader)

			goldBalance = player.treasury.value()
			self._rankingData.addGoldBalance(goldBalance, player.leader)

			totalCities = len(self.citiesOf(player))
			self._rankingData.addTotalCities(totalCities, player.leader)

			totalCitiesFounded = player.numberOfCitiesFounded()
			self._rankingData.addTotalCitiesFounded(totalCitiesFounded, player.leader)

			totalCitiesLost = player.numberOfCitiesLost()
			self._rankingData.addTotalCitiesLost(totalCitiesLost, player.leader)

			totalDistrictsConstructed = 0  # self.citiesOf(player)
			# .map { $0?.districts?.numberOfBuiltDistricts() ?? 0}
			# .reduce(0, +)
			self._rankingData.addTotalDistrictsConstructed(totalDistrictsConstructed, player.leader)

			totalWondersConstructed = 0  # self.citiesOf(player)
			# .map { $0?.wonders?.numberOfBuiltWonders() ?? 0}
			# .reduce(0, +)
			self._rankingData.addTotalWondersConstructed(totalWondersConstructed, player.leader)

			totalBuildingsConstructed = 0  # self.citiesOf(player)
			# .map { $0?.buildings?.numberOfBuildings() ?? 0}
			# .reduce(0, +)
			self._rankingData.addTotalBuildingsConstructed(totalBuildingsConstructed, player.leader)

			# ...
			totalScore = player.score(self)
			self._rankingData.addTotalScore(totalScore, player.leader)

			sciencePerTurn = player.science(self)
			self._rankingData.addSciencePerTurn(sciencePerTurn, player.leader)

			faithPerTurn = player.faith(reset=False, simulation=self)
			self._rankingData.addFaithPerTurn(faithPerTurn, player.leader)

			totalReligionsFounded = 0 if player.religion.currentReligion() == ReligionType.none else 1
			self._rankingData.addTotalReligionsFounded(totalReligionsFounded, player.leader)

			totalGreatPeopleEarned = player.greatPeople.numberOfSpawnedGreatPersons()
			self._rankingData.addTotalGreatPeopleEarned(totalGreatPeopleEarned, player.leader)

			totalWarDeclarationsReceived = player.diplomacyAI.atWarCount()
			self._rankingData.addTotalWarDeclarationsReceived(totalWarDeclarationsReceived, player.leader)

			totalPantheonsFounded = 0 if player.religion.pantheon() == PantheonType.none else 1
			self._rankingData.addTotalPantheonsFounded(totalPantheonsFounded, player.leader)

		return

	def doWorldEra(self):
		previousWorldEra = self._worldEraValue

		self.updateWorldEra()

		if previousWorldEra != self._worldEraValue:
			# world era has changed
			# ???

			# invalidate all city state quests
			for player in self.players:
				if not player.isCityState():
					continue

				player.resetQuests(self)

	def doTestVictory(self):
		if self.winnerVictory() is not None:
			return

		self.doTestScienceVictory()
		self.doTestCultureVictory()
		self.doTestDominationVictory()
		self.doTestReligiousVictory()
		# self.doTestDiplomaticVictory()

		self.doTestScoreVictory()
		self.doTestConquestVictory()

	def updateMoves(self):
		playersToProcess = []
		processPlayerAutoMoves = False

		for player in self.players:
			if player.isAlive() and player.isTurnActive() and not player.isHuman():
				playersToProcess.append(player)
				processPlayerAutoMoves = False

				# Notice the break. Even if there is more than one AI with an active turn, we do them sequentially.
				break

		# If no AI with an active turn, check humans.
		if len(playersToProcess) == 0:
			processPlayerAutoMoves = True

			for player in self.players:
				# player.checkInitialTurnAIProcessed()
				if player.isActive() and player.isHuman():
					playersToProcess.append(player)

		if len(playersToProcess) > 0:
			player = playersToProcess[0]

			readyUnitsBeforeMoves = player.countReadyUnits(self)

			if player.isAlive():
				needsAIUpdate = player.hasUnitsThatNeedAIUpdate(self)
				if player.isActive() or needsAIUpdate:
					if not player.isAutoMoves() or needsAIUpdate:
						if needsAIUpdate or not player.isHuman():
							# ------- this is where the important stuff happens! --------------
							player.unitUpdate(self)
							# logging.debug(f"updateMoves() : player.unitUpdate() called for player {player.name()}")

						readyUnitsNow = player.countReadyUnits(self)

						# Was a move completed, if so save off which turn slice this was
						if readyUnitsNow < readyUnitsBeforeMoves:
							player.setLastSliceMoved(self.turnSlice())

						if not player.isHuman() and not player.hasBusyUnitOrCity(self):

							if readyUnitsNow == 0:
								player.setAutoMovesTo(True)
							else:
								if player.hasReadyUnit(self):
									waitTime = 5

									if self.turnSlice() - player.lastSliceMoved() > waitTime:
										logging.warning(
											"GAME HANG - Please show and send save. Stuck units will have their turn ended so game can advance.")
										# debug
										for unit in self.unitsOf(player):
											if not unit.readyToMove():
												continue

											logging.warning(
												f"GAME HANG - unit of {player.leader.name()} has no orders: {unit.name()} at {unit.location}")

										# debug
										player.endTurnsForReadyUnits(self)

						if player.isAutoMoves() and (not player.isHuman() or processPlayerAutoMoves):
							repeatAutomoves = False
							repeatPassCount = 2  # Prevent getting stuck in a loop

							while True:
								for loopUnit in self.unitsOf(player):
									loopUnit.autoMission(self)

									# Does the unit still have movement points left over?
									if player.isHuman() and loopUnit.hasCompletedMoveMission(self) and \
										loopUnit.canMove() and not loopUnit.isAutomated():

										if player.turnFinished():
											repeatAutomoves = True  # Do another pass.

								# This is a short - term solution to a problem where a unit
								# with an auto-mission (a queued, multi-turn) move order cannot reach its destination, but
								# does not re-enter the "need order" list because this code is processed at the end of turns.The result is that the player could easily "miss" moving
								# the unit this turn because it displays "next turn" rather than "skip unit turn" and the unit is not added to the "needs orders" list.
								# To correctly fix this problem, we would need some way to determine if any of the auto-missions are invalid before the player can end the turn and
								# activate the units that have a problem.
								# The problem with evaluating this is that, with one unit per tile, we don't know what is a valid move until other units have moved.
								# (For example, if one unit was to follow another, we would want the unit in the lead to move first and then have the following unit move, in order
								# to prevent the following unit from constantly waking up because it can't move into the next tile. This is currently not supported.)

								# This short-term solution will reactivate a unit after the player clicks "next turn".It will appear strange, because the player will be asked to move
								# a unit after they clicked "next turn", but it is to give the player a chance to move all of their units.

								# jrandall sez: In MP matches, let's not OOS or stall the game.

								repeatPassCount -= 1

								if not (repeatAutomoves and repeatPassCount > 0):
									break

							# check if the(for now human) player is overstacked and move the units
							# if (player.isHuman())

							# slewis - I changed this to only be the AI because human players should have the tools to deal with this now
							if not player.isHuman():
								for loopUnit in self.unitsOf(player):
									loopUnit.doDelayedDeath(self)

						# If we completed the processing of the auto - moves, flag it.
						if player.turnFinished() or not player.isHuman():
							player.setProcessedAutoMovesTo(True)

					# KWG: This code should go into CheckPlayerTurnDeactivate
					if not player.turnFinished() and player.isHuman():
						if not player.hasBusyUnitOrCity(self):
							player.setEndTurnTo(True, self)

							if player.isEndTurn():
								# If the player's turn ended, indicate it in the log. We only do so when the end turn state has changed to prevent useless log spamming in multiplayer.
								# NET_MESSAGE_DEBUG_OSTR_ALWAYS("UpdateMoves() : player.setEndTurnTo(true) called for player " << player.GetID() << " " << player.getName())
								pass
						else:
							# if !player.hasBusyUnitUpdatesRemaining() {
							# NET_MESSAGE_DEBUG_OSTR_ALWAYS("Received turn complete for player " << player.GetID() << " " << player.getName() << " but there is a busy unit. Forcing the turn to advance")
							player.setEndTurnTo(True, self)

	def updateTimers(self):
		activePlayer = self.activePlayer()
		if activePlayer is None or not activePlayer.isHuman():
			return

		for player in self.players:
			if player.isAlive():
				player.updateTimers(self)

	def updatePlayers(self, simulation):
		for player in self.players:
			if player.isAlive() and player.isActive():
				player.updateNotifications(simulation)

	def checkPlayerTurnDeactivate(self):
		""" Check to see if the player's turn should be deactivated.
			This occurs when the player has set its EndTurn and its AutoMoves to true
			and all activity has been completed."""
		if self.userInterface is None:
			raise Exception("no UI")

		for player in self.players:
			if player.isAlive() and player.isTurnActive():
				# For some reason, AI players don't set EndTurn, why not?
				if player.isEndTurn() or (not player.isHuman() and not player.hasActiveDiplomacyRequests()):
					if player.hasProcessedAutoMoves():
						autoMovesComplete = False
						if not player.hasBusyUnitOrCity(self):
							autoMovesComplete = True
							# logging.info("+++ GameModel - CheckPlayerTurnDeactivate() : auto-moves complete for \(player.leader.name())")

						if autoMovesComplete:
							# Activate the next player
							# In that case, the local human is (should be) the player we just deactivated the turn for
							# and the AI players will be activated all at once in CvGame::doTurn, once we have received
							# all the moves from the other human players
							if not self.userInterface.isShown(ScreenType.diplomatic):
								player.endTurn(self)

								# If it is a hot seat game and the player is human and is dead, don't advance the player,
								# we want them to get the defeat screen
								if player.isAlive() or not player.isHuman():
									hasReachedCurrentPlayer = False
									for nextPlayer in self.players:

										if nextPlayer == player:
											hasReachedCurrentPlayer = True
											continue

										if not hasReachedCurrentPlayer:
											continue

										if nextPlayer.isAlive():
											# the player is alive and also running sequential turns.they're up!
											nextPlayer.startTurn(self)
											# self.resetTurnTimer(false)
											break
							else:
								# KWG: This doesn't actually do anything other than print to the debug log
								logging.warning(f"Because the diplomatic screen is blocking, I am bumping this up for player {player.leader}")
							# changeNumGameTurnActive(1, std::string("Because the diplomatic screen is blocking I am
							# bumping this up for player ") + getName());

	def setWaitingForBlockingInput(self, player):
		self.waitDiploPlayer = player

	def activePlayer(self):
		return self._activePlayer  # next((player for player in self.players if player.isAlive() and player.isActive()), None)

	def updateActivePlayer(self, player):
		self._activePlayer = player

	def updateTacticalAnalysisMap(self, player):
		self._tacticalAnalysisMap.refreshFor(player, self)

	def tacticalAnalysisMap(self) -> TacticalAnalysisMap:
		return self._tacticalAnalysisMap

	def refreshDangerPlots(self):
		"""Loop through all the players and do any deferred updates of their danger plots"""
		for loopPlayer in self.players:
			# Must be alive
			if not loopPlayer.isAlive():
				continue

			if loopPlayer.dangerPlotsAI.isDirty():
				loopPlayer.dangerPlotsAI.updateDanger(False, False, self)

		return

	def sightAt(self, location: HexPoint, sight: int, unit=None, player=None):
		if player is None:
			raise Exception("cant get player")

		currentTile = self.tileAt(location)
		hasSentry: bool = unit.hasPromotion(UnitPromotionType.sentry) if unit is not None else False

		for areaPoint in location.areaWithRadius(sight):
			tile = self.tileAt(areaPoint)

			if tile is None:
				continue

			if not tile.canSeeTile(currentTile, player, sight, hasSentry, self):
				continue

			# inform the player about a goody hut
			if tile.hasImprovement(ImprovementType.goodyHut) and not tile.isDiscoveredBy(player):
				player.notifications().addNotification(NotificationType.goodyHutDiscovered, location=areaPoint)

			# inform the player about a barbarian camp
			if tile.hasImprovement(ImprovementType.barbarianCamp) and not player.isBarbarianCampDiscoveredAt(areaPoint):
				player.discoverBarbarianCampAt(areaPoint)

			# check if tile is on another continent than the(original) capital
			continent = self.continentAt(areaPoint)
			if continent is not None:
				tileContinent: ContinentType = continent.continentType
				capitalLocation = player.originalCapitalLocation()
				if capitalLocation != constants.invalidHexPoint:
					capitalContinent = self.continentAt(capitalLocation)
					if capitalContinent is not None:
						if tileContinent != capitalContinent.continentType and \
							capitalContinent.continentType != ContinentType.none and \
							tileContinent != ContinentType.none:
							if not player.civics.inspirationTriggeredFor(CivicType.foreignTrade):
								player.civics.triggerInspirationFor(CivicType.foreignTrade, simulation=self)

			# found Natural wonder
			feature = tile.feature()
			if feature.isNaturalWonder():
				# check if wonder is discovered by player already
				if not player.hasDiscoveredNaturalWonder(feature):
					player.doDiscoverNaturalWonder(feature)
					player.addMoment(MomentType.discoveryOfANaturalWonder, naturalWonder=feature, simulation=self)

					if unit.hasAbility(UnitAbilityType.experienceFromTribal):
						# Gains XP when activating Tribal Villages(+5 XP) and discovering Natural Wonders(+10 XP)
						unit.changeExperienceBy(10, self)

					if player.isHuman():
						player.notifications().addNotification(NotificationType.naturalWonderDiscovered,
															   location=areaPoint)

				if not player.techs.eurekaTriggeredFor(TechType.astrology):
					player.techs.triggerEurekaFor(TechType.astrology, self)

			tile.discoverBy(player, self)
			tile.sightBy(player)
			player.checkWorldCircumnavigated(self)
			if continent is not None:
				self.checkDiscoveredContinent(continent.continentType, areaPoint, player)

			self.userInterface.refreshTile(tile)

		return

	def concealAt(self, location: HexPoint, sight: int, unit=None, player=None):
		currentTile = self.tileAt(location)

		hasSentry: bool = unit.hasPromotion(UnitPromotionType.sentry) if unit is not None else False

		for loopPoint in location.areaWithRadius(sight):
			loopTile = self.tileAt(loopPoint)

			if loopTile is None:
				continue

			if not loopTile.canSeeTile(currentTile, player, sight, hasSentry=hasSentry, simulation=self):
				continue

			loopTile.concealTo(player)
			self.userInterface.refreshTile(loopTile)

		return

	def concealCity(self, city):
		for loopPoint in city.location.areaWithRadius(3):
			loopTile = self.tileAt(loopPoint)

			if loopTile is None:
				continue

			loopTile.concealTo(city.player)
			self.userInterface.refreshTile(loopTile)

		return

	def sightCity(self, city):
		for loopPoint in city.location.areaWithRadius(3):
			loopTile = self.tileAt(loopPoint)

			if loopTile is None:
				continue

			loopTile.sightBy(city.player)
			self.userInterface.refreshTile(loopTile)

		return

	def discoverAt(self, location: HexPoint, sight: int, player):
		if not self.valid(location):
			return

		currentTile = self.tileAt(location)

		for pt in location.areaWithRadius(sight):
			tile = self.tileAt(pt)

			if tile is None:
				continue

			if not tile.canSeeTile(currentTile, player, sight, hasSentry=False, simulation=self):
				continue

			if tile.isDiscoveredBy(player):
				continue

			tile.discoverBy(player, self)
			player.checkWorldCircumnavigated(self)

			continent = self.continentAt(pt)
			if continent is not None:
				self.checkDiscoveredContinent(continent.continentType, pt, player)
			self.userInterface.refreshTile(tile)

		return

	def continentAt(self, location) -> Optional[Continent]:
		if not self.valid(location):
			return None

		tile = self.tileAt(location)
		identifier = tile.continentIdentifier

		if identifier is not None:
			return self._map.continent(identifier)

		return None

	def citySiteEvaluator(self) -> CitySiteEvaluator:
		return CitySiteEvaluator(self._map)

	def isLargestPlayer(self, player) -> bool:
		"""
			check if moment worldsLargestCivilization should trigger

			- Parameter civilization: civilization to check
			- Returns:  has the civilization at least 3 more cities than the next biggest civilization
		"""
		numPlayerCities = len(self.citiesOf(player))
		numAllOtherCities = map(lambda p: len(self.citiesOf(p)), self.players)
		numNextBestPlayersCities = max(numAllOtherCities)

		return numPlayerCities >= (numNextBestPlayersCities + 3)

	def sendGossip(self, gossipType: GossipType, cityName: Optional[str] = None, tech: Optional[TechType] = None,
				   civic: Optional[CivicType] = None, leader: Optional[LeaderType] = None,
				   building: Optional[BuildingType] = None, district: Optional[DistrictType] = None,
				   wonder: Optional[WonderType] = None, pantheonName: Optional[str] = None,
				   government: Optional[GovernmentType] = None, unit: Optional[UnitType]=None, player=None):

		if player is None:
			raise Exception('player must not be none')

		humanPlayer = self.humanPlayer()

		if humanPlayer is None:
			# no human player in this setup - so nothing to report
			return

		humanPlayerDiplomacyAI = humanPlayer.diplomacyAI

		#  when the gossip event is triggered by human, don't send
		if humanPlayer == player:
			return

		# only send gossip to human player, if he has met player
		if not humanPlayer.hasMetWith(player):
			return

		accessLevel: AccessLevel = humanPlayerDiplomacyAI.accessLevelTowards(player)

		# check that this information is accessible to the human player
		if gossipType.accessLevel() > accessLevel:
			return

		gossipSource: GossipSourceType = GossipSourceType.spy  # todo
		gossipItem = GossipItem(gossipType, turn=self.currentTurn, source=gossipSource)
		gossipItem.cityName = cityName
		gossipItem.tech = tech
		gossipItem.civic = civic
		gossipItem.leader = leader
		gossipItem.building = building
		gossipItem.district = district
		gossipItem.wonder = wonder
		gossipItem.pantheonName = pantheonName
		gossipItem.government = government
		gossipItem.unit = unit
		humanPlayerDiplomacyAI.addGossipItem(gossipItem, player)

		return

	def visibleEnemyAt(self, location: HexPoint, player, unitMapType: UnitMapType = UnitMapType.combat) -> Optional[
		Unit]:
		tile = self.tileAt(location)

		if tile.isVisibleTo(player):
			enemyUnit = self.unitAt(location, unitMapType)

			if enemyUnit is not None and player.diplomacyAI.isAtWarWith(enemyUnit.player):
				return enemyUnit

		return None

	def visibleEnemyCityAt(self, location: HexPoint, player) -> Optional[
		City]:
		diplomacyAI = player.diplomacyAI

		tile = self.tileAt(location)

		if tile.isVisibleTo(player):
			enemyCity = self.cityAt(location)

			if enemyCity is not None:
				if diplomacyAI.isAtWarWith(enemyCity.player):
					return enemyCity

		return None

	def unitAwarePathfinderDataSource(self, unit) -> MoveTypeUnitAwarePathfinderDataSource:
		datasourceOptions = MoveTypeUnitAwareOptions(
			unitMapType=unit.unitMapType(),
			ignore_sight=True,
			can_embark=unit.player.canEmbark(),
			can_enter_ocean=unit.player.canEnterOcean()
		)
		return MoveTypeUnitAwarePathfinderDataSource(self._map, unit.movementType(), unit.player, datasourceOptions)

	def ignoreUnitsPathfinderDataSource(self, movementType: UnitMovementType, player,
										canEmbark: bool, canEnterOcean: bool) -> MoveTypeIgnoreUnitsPathfinderDataSource:
		datasourceOptions = MoveTypeIgnoreUnitsOptions(
			ignore_sight=True,
			can_embark=canEmbark,
			can_enter_ocean=canEnterOcean
		)
		return MoveTypeIgnoreUnitsPathfinderDataSource(self._map, movementType, player, datasourceOptions)

	def pathTowards(self, target: HexPoint, options: [MoveOption], unit) -> Optional[HexPath]:
		datasource = self.unitAwarePathfinderDataSource(unit)
		pathFinder = AStarPathfinder(datasource)

		path = pathFinder.shortestPath(unit.location, target)

		if path is None:
			return None

		# add costs
		path.addCost(0.0)  # first location

		lastPoint = None
		for index, point in enumerate(path.points()):
			if index == 0:
				lastPoint = point
				continue

			cost = datasource.costToMove(lastPoint, point)
			path.addCost(cost)
			lastPoint = point

		return path

	def anyHasMoment(self, momentType: MomentType, civilization: Optional[CivilizationType] = None,
					 eraType: Optional[EraType] = None) -> bool:
		for player in self.players:
			if player.hasMoment(momentType, civilization=civilization, eraType=eraType):
				return True

		return False

	def alreadyBuiltWonder(self, wonderType: WonderType) -> bool:
		for player in self.players:
			if player.hasWonder(wonderType, self):
				return True

		return False

	def buildWonder(self, wonderType: WonderType):
		wondersBuilt = self.wondersBuilt
		wondersBuilt.buildWonder(wonderType)

	def checkArchaeologySites(self):
		if not self._spawnedArchaeologySites:
			self.spawnArchaeologySites()
			self._spawnedArchaeologySites = True

	def spawnArchaeologySites(self):
		# we should now have a map of the dig sites
		# turn this map into set of RESOURCE_ARTIFACTS
		randomLandArtifacts: [ArtifactType] = [
			ArtifactType.ancientRuin,
			ArtifactType.ancientRuin,
			ArtifactType.razedCity,
			ArtifactType.barbarianCamp,
			ArtifactType.barbarianCamp,
			ArtifactType.battleMelee,
			ArtifactType.battleRanged
		]

		randomSeaArtifacts: [ArtifactType] = [
			ArtifactType.battleSeaMelee,
			ArtifactType.battleSeaRanged
		]

		# find how many dig sites we need to create
		numMajorCivs = self.countMajorCivilizationsEverAlive()
		minDigSites = 5 * numMajorCivs  # MIN_DIG_SITES_PER_MAJOR_CIV
		maxDigSites = 8 * numMajorCivs  # MAX_DIG_SITES_PER_MAJOR_CIV
		idealNumDigSites = random.randint(minDigSites, maxDigSites)

		# 80 % land / 20 % sea
		idealNumLandDigSites = idealNumDigSites * 4 / 5
		idealNumSeaDigSites = idealNumDigSites * 1 / 5

		# find the highest era any player has gotten to
		highestEra: EraType = EraType.ancient
		for loopPlayer in self.players:

			# Player not ever alive
			if not loopPlayer.isEverAlive():
				continue

			if loopPlayer.currentEra() > highestEra:
				highestEra = loopPlayer.currentEra()

		eraWeights = WeightedBaseList()  # EraType
		maxEraWeight = 0

		for loopEra in list(EraType):
			if loopEra > highestEra:
				continue

			weight: int = highestEra.value() - loopEra.value()
			eraWeights.addWeight(weight, loopEra)
			maxEraWeight += weight

		# find out how many dig sites we have now
		howManyChosenLandDigSites = 0
		howManyChosenSeaDigSites = 0

		# fill the historical buffer with the archaeological data
		gridPoints = self._map.points()
		assert len(gridPoints) > 0, "gridSize is zero"
		historicalDigSites: [ArchaeologicalRecord] = [ArchaeologicalRecord() for _ in range(len(gridPoints))]
		scratchDigSites: [ArchaeologicalRecord] = [ArchaeologicalRecord() for _ in range(len(gridPoints))]

		for index, gridPoint in enumerate(gridPoints):
			plot = self.tileAt(gridPoint)

			if plot is None:
				continue

			resource = plot.resourceFor(None)

			if plot.isLand():
				if plot.isImpassable(UnitMovementType.walk):
					historicalDigSites[index].artifactType = ArchaeologicalRecordType.none
					historicalDigSites[index].era = EraType.ancient
					historicalDigSites[index].leader1 = LeaderType.none
					historicalDigSites[index].leader2 = LeaderType.none

					# Cannot be an antiquity site if we cannot generate an artifact.
					if resource == ResourceType.antiquitySite:
						plot.setResource(ResourceType.none)
				else:
					# If this plot is already marked as an antiquity site, ensure it's populated.
					if resource == ResourceType.antiquitySite:
						if plot.archaeologicalRecord().artifactType == ArchaeologicalRecordType.none:
							# pick an era before this one
							era = eraWeights.chooseFromTopChoices()  # ?? EraType.ancient

							# pick a type of artifact
							artifact: ArtifactType = random.choice(randomLandArtifacts)
							self.populateDigSiteOn(plot, era, artifact)

							# Record in scratch space for weights.
							scratchDigSites[index] = plot.archaeologicalRecord()

						howManyChosenLandDigSites += 1

					historicalDigSites[index] = plot.archaeologicalRecord()
			else:
				if plot.isImpassable(UnitMovementType.swim):
					historicalDigSites[index].artifactType = ArtifactType.none
					historicalDigSites[index].era = EraType.ancient
					historicalDigSites[index].leader1 = LeaderType.none
					historicalDigSites[index].leader2 = LeaderType.none

					# Cannot be an antiquity site if we cannot generate an artifact.
					if resource == ResourceType.shipwreck:
						plot.setResource(ResourceType.none)
				else:
					# If this plot is already marked as an antiquity site, ensure it's populated.
					if resource == ResourceType.shipwreck:
						if plot.archaeologicalRecord().artifactType == ArtifactType.none:
							# pick an era before this one
							era = eraWeights.chooseFromTopChoices()  # ?? EraType.ancient

							# pick a type of artifact
							artifact = random.choice(randomSeaArtifacts)
							self.populateDigSiteOn(plot, era, artifact)

							# Record in scratch space for weights.
							scratchDigSites[index] = plot.archaeologicalRecord()

						howManyChosenLandDigSites += 1

					historicalDigSites[index] = plot.archaeologicalRecord()

		# calculate initial weights
		digSiteWeights: [int] = [0 for _ in range(len(gridPoints))]
		self.calculateDigSiteWeights(len(gridPoints), historicalDigSites, scratchDigSites, digSiteWeights)

		# build a weight vector
		aDigSiteWeights: WeightedBaseList = WeightedBaseList()
		iteration = 0

		# while we are not in the proper range of number of dig sites
		while (howManyChosenLandDigSites < idealNumLandDigSites or howManyChosenSeaDigSites < idealNumSeaDigSites) and iteration < 2 * (idealNumLandDigSites + idealNumSeaDigSites):
			# populate a weight vector
			aDigSiteWeights.items = []

			for index in range(len(gridPoints)):
				if digSiteWeights[index] < 0:
					continue

				aDigSiteWeights.addWeight(digSiteWeights[index], index)

			# add the best dig site
			bestSite: int = aDigSiteWeights.chooseLargest()
			bestLocation = self._map.pointFor(bestSite)
			plot = self._map.tileAt(bestLocation)

			if plot is None:
				continue

			if plot.isLand() and howManyChosenLandDigSites < idealNumLandDigSites:
				plot.setResource(ResourceType.antiquitySite)
				howManyChosenLandDigSites += 1
			elif plot.isWater() and howManyChosenSeaDigSites < idealNumSeaDigSites:
				plot.setResource(ResourceType.shipwreck)
				howManyChosenSeaDigSites += 1

			# if this is not a historical dig site
			if scratchDigSites[bestSite].artifactType == ArtifactType.none:
				# fake the historical data
				# pick an era before this one
				era = eraWeights.chooseFromTopChoices()  # EraType.ancient

				# pick a type of artifact
				artifact = random.choice(randomLandArtifacts)
				self.populateDigSiteOn(plot, era, artifact)

			scratchDigSites[bestSite] = plot.archaeologicalRecord()

			# recalculate weights near the chosen dig site (the rest of the world should still be fine)
			plotPoint: HexPoint = self._map.pointFor(bestSite)
			for loopPoint in plotPoint.areaWithRadius(3):
				if not self.valid(loopPoint):
					continue

				index = self._map.indexFor(loopPoint)
				digSiteWeights[index] = self.calculateDigSiteWeightAt(index, historicalDigSites, scratchDigSites)

			iteration += 1

		return

	def isEnemyVisibleAt(self, location: HexPoint, player, unitMapType: UnitMapType = UnitMapType.combat) -> bool:
		return self.visibleEnemyAt(location, player, unitMapType) is not None

	def mapSize(self) -> MapSize:
		return self._map.bestMatchingSize()

	def checkDiscoveredContinent(self, continentType: ContinentType, location: HexPoint, player):
		"""
		/// method to trigger the firstDiscoveryOfANewContinent moment, when player has discovered a new continent before everybody else
		///
		/// - Parameters:
		///   - continent: continent to check
		///   - player: player to check and trigger the moment for

		@param continentType:
		@param location:
		@param player:
		@return:
		"""
		if player is None:
			raise Exception('player must not be None')

		if not self.hasDiscoveredContinent(continentType):
			self.markContinentDiscovered(continentType)

			continent = self._map.continentBy(continentType)
			if continent is not None:
				# only trigger discovery of new continent, if player has at least one city
				# this prevents first city triggering this
				if len(continent.points) > 8 and len(self.citiesOf(player)) > 0:
					player.addMoment(MomentType.firstDiscoveryOfANewContinent, simulation=self)

					if player.isHuman():
						player.notifications.addNotification(
							NotificationType.continentDiscovered,
							location=location,
							continentName=continentType.title()
						)
		return

	def hasDiscoveredContinent(self, continentType: ContinentType) -> bool:
		return continentType in self.discoveredContinents

	def markContinentDiscovered(self, continentType: ContinentType):
		self.discoveredContinents.append(continentType)

	def calculateInfluenceDistance(self, cityLocation: HexPoint, targetDestination: HexPoint, limit: int) -> int:
		if cityLocation == targetDestination:
			return 0

		influencePathfinderDataSource = InfluencePathfinderDataSource(self._map, cityLocation)
		influencePathfinder = AStarPathfinder(influencePathfinderDataSource)

		path = influencePathfinder.shortestPath(cityLocation, targetDestination)
		if path is not None:
			if len(path.points()) > limit:
				return 0

			return int(path.cost())

		return 0

	def isAdjacentDiscovered(self, point: HexPoint, player) -> bool:
		for neighbor in point.neighbors():
			tile = self._map.tileAt(neighbor)

			if tile is None:
				continue

			if tile.isDiscoveredBy(player):
				return True

		return False

	def isWithinCityRadius(self, tile, player) -> bool:
		playerCities = self.citiesOf(player)

		for city in playerCities:
			if tile.point.distance(city.location) < City.workRadius:
				return True

		return False

	def areas(self):
		return self._map.areas

	def isGreatGeneral(self, greatPerson: GreatPersonType, player, location: HexPoint, range: int) -> bool:
		for unit in self.unitsOf(player):
			if unit.location.distance(location) <= range:
				if unit.greatPerson == greatPerson:
					return True

		return False

	def areBarbariansReleased(self) -> bool:
		return self.earliestBarbarianReleaseTurn() <= self.currentTurn

	def earliestBarbarianReleaseTurn(self) -> int:
		return self.handicap.earliestBarbarianReleaseTurn()

	def numberOfPantheonsFounded(self) -> int:
		numPantheons = 0
		for player in self.players:
			if player.religion.pantheon() != PantheonType.none:
				numPantheons += 1

		return numPantheons

	def worldEra(self) -> EraType:
		return self._worldEraValue

	def playerFor(self, leader: LeaderType) -> Optional[Player]:
		if leader == LeaderType.cityState:
			raise Exception('use cityStatePlayerFor for cityState')

		for player in self.players:
			if player.leader == leader:
				return player

		return None

	def cityStatePlayerFor(self, cityState: CityStateType) -> Optional[Player]:
		for player in self.players:
			if player.leader == LeaderType.cityState and player.cityState == cityState:
				return player

		return None

	def playerForHash(self, hashValue) -> Optional[Player]:
		for player in self.players:
			if hash(player) == hashValue:
				return player

		return None

	def addReplayEvent(self, eventType: ReplayEventType, message: str, location: HexPoint):
		self.replayEvents.append(ReplayEvent(self.currentTurn, eventType, message, location))

	def numberOfLandPlots(self) -> int:
		"""number of land tiles"""
		return self._map.numberOfLandPlots()

	def randomLocation(self) -> HexPoint:
		size: Size = self.mapSize().size()
		x = random.randint(0, size.width())  # Int.random(number: self.mapSize().width())
		y = random.randint(0, size.height())
		return HexPoint(x, y)

	def countMajorCivilizationsEverAlive(self) -> int:
		return len(list(filter(lambda player: player.isEverAlive(), self.players)))

	def mapSizeModifier(self) -> int:
		# percentage of size compared standard map
		numberOfTilesStandard = MapSize.standard.numberOfTiles()
		numberOfTilesMap = self.mapSize().numberOfTiles()

		return int(100 * numberOfTilesMap / numberOfTilesStandard)

	def updateWorldEra(self):
		eraHistogram: EraHistogram = EraHistogram()
		eraHistogram.fill()

		playerCount: float = 0.0

		for player in self.players:
			if player.isBarbarian() or player.isFreeCity() or player.isCityState():
				continue

			playerCount += 1.0

			for era in list(EraType):
				if era <= player.currentEra():
					eraHistogram.addWeight(1.0, era)

		bestEra: EraType = EraType.ancient
		for era in list(EraType):
			if eraHistogram.weight(era) >= (playerCount * 0.5):
				bestEra = era

		self._worldEraValue = bestEra

	def winnerVictory(self) -> Optional[VictoryType]:
		return self._gameWinVictoryValue

	def doTestScienceVictory(self):
		if VictoryType.science not in self.victoryTypes:
			return

		if self.winnerVictory() is not None:
			return

		for player in self.players:
			if not player.isMajorAI() and not player.isHuman():
				continue

			if player.hasScienceVictory(self):
				self.setWinner(player.leader, VictoryType.science)
				self.setGameStateTo(GameState.over)

				self.userInterface.showScreen(ScreenType.victory, city=None, other=None, data=None)

		return

	def setWinner(self, leader: LeaderType, victoryType: VictoryType):
		self._gameWinLeaderValue = leader
		self._gameWinVictoryValue = victoryType

	def doTestCultureVictory(self):
		# https://forums.civfanatics.com/threads/how-tourism-is-calculated-and-a-culture-victory-made.605199/
		if VictoryType.cultural not in self.victoryTypes:
			return

		if self.winnerVictory() is not None:
			return

		for player in self.players:
			if not player.isMajorAI() and not player.isHuman():
				continue

			if player.hasCulturalVictory(self):
				self.setWinner(player.leader, VictoryType.cultural)
				self.setGameStateTo(GameState.over)

				self.userInterface.showScreen(ScreenType.victory, city=None, other=None, data=None)

		return

	def doTestDominationVictory(self):
		if VictoryType.cultural not in self.victoryTypes:
			return

		if self.winnerVictory() is not None:
			return

		# Calculate who owns the most original capitals by iterating through all civs
		# and finding out who owns their original capital now.
		numOriginalCapitals: dict[LeaderType, int] = dict[LeaderType, int]()
		playerNum: int = len(list(filter(lambda player: player.isMajorAI() or player.isHuman(), self.players)))

		for player in self.players:
			if not player.isMajorAI() and not player.isHuman():
				continue

			if player.originalCapitalLocation() != HexPoint(-1, -1):
				capitalCity = self.cityAt(player.originalCapitalLocation())

				if capitalCity is not None:
					capitalOwner = capitalCity.player

					# is the current owner the original owner?
					if player == capitalOwner:
						numOriginalCapitals[capitalOwner.leader] = numOriginalCapitals.get(capitalOwner.leader, 0) + 1

		for leaderKey in numOriginalCapitals.keys():
			numConqueredCapitals = numOriginalCapitals[leaderKey]

			# own capital can't be conquered
			if numConqueredCapitals + 1 >= playerNum:
				winnerKey: LeaderType = leaderKey
				self.setWinner(winnerKey, VictoryType.domination)
				self.setGameStateTo(GameState.over)

				self.userInterface.showScreen(ScreenType.victory, city=None, other=None, data=None)

		return

	def doTestReligiousVictory(self):
		if VictoryType.religious not in self.victoryTypes:
			return

		if self.winnerVictory() is not None:
			return

		for player in self.players:
			if not player.isMajorAI() and not player.isHuman():
				continue

			if player.hasReligiousVictory(self):
				self.setWinner(player.leader, VictoryType.religious)
				self.setGameStateTo(GameState.over)

				self.userInterface.showScreen(ScreenType.victory, city=None, other=None, data=None)

		return

	def doTestScoreVictory(self):
		if self.winnerVictory() is not None:
			return

		# game has reached last turn
		if self.currentTurn >= 500:
			playerScore: dict[LeaderType, int] = dict[LeaderType, int]()

			for player in self.players:
				if not player.isMajorAI() and not player.isHuman():
					continue

				playerScore[player.leader] = player.score(self)

			# the winner is the player with the highest score
			winnerKey: LeaderType = sorted(playerScore.items(), key=operator.itemgetter(1), reverse=True)[0][0]
			self.setWinner(winnerKey, VictoryType.domination)
			self.setGameStateTo(GameState.over)

			self.userInterface.showScreen(ScreenType.victory, city=None, other=None, data=None)

		return

	def doTestConquestVictory(self):
		"""test if only on human or ai player is alive"""
		if self.winnerVictory() is not None:
			return

		numAlivePlayers: int = 0
		winner: LeaderType = LeaderType.none

		# loop through all players
		for player in self.players:
			if not player.isMajorAI() and not player.isHuman():
				continue

			if not player.isAlive():
				continue

			numAlivePlayers += 1
			winner = player.leader

		# if only one (or none) player is alive - this is defeat
		if numAlivePlayers <= 1:
			self.setWinner(winner, VictoryType.conquest)
			self.setGameStateTo(GameState.over)

			self.userInterface.showScreen(ScreenType.victory, city=None, other=None, data=None)

		return

	def calculateDigSiteWeights(self, gridSize: int, historicalDigSites: [ArchaeologicalRecord], scratchDigSites: [ArchaeologicalRecord], digSiteWeights: [int]):
		for index in range(gridSize):
			digSiteWeights[index] = self.calculateDigSiteWeightAt(index, historicalDigSites, scratchDigSites)

		return

	def areaOf(self, point: HexPoint) -> Optional[HexArea]:
		for area in self.areas():
			if point in area.points():
				return area

		return None

	def areaOfCapitalOf(self, player) -> Optional[HexArea]:
		capitalCity = self.capitalOf(player)

		if capitalCity is None:
			return None

		for area in self.areas():
			if capitalCity.location in area.points():
				return area

		return None

	def calculateDigSiteWeightAt(self, index: int, historicalDigSites: [ArchaeologicalRecord], scratchDigSites: [ArchaeologicalRecord]) -> int:
		baseWeight = 0

		# if we have not already chosen this spot for a dig site
		if scratchDigSites[index].artifactType == ArtifactType.none:
			baseWeight = historicalDigSites[index].artifactType._value + 1
			baseWeight *= (10 - historicalDigSites[index].era._value)

			point = self._map.pointFor(index)
			plot = self.tileAt(point)

			# zero this value if this plot has a resource, ice, mountain, or natural wonder
			if plot.resourceFor(None) is not None or \
				(plot.isImpassable(UnitMovementType.walk) and plot.isImpassable(UnitMovementType.swim)) or \
				plot.feature().isNaturalWonder():
				baseWeight = 0

			# if this tile cannot be improved, zero it out
			if baseWeight > 0 and plot.feature() != FeatureType.none:
				if plot.feature().isNoImprovement():
					baseWeight = 0

			# if this tile has a great person improvement, zero it out
			# if baseWeight > 0 & & plot.improvement() !=.none {
			# if plot.improvement().isCreatedByGreatPerson() {
			# baseWeight = 0

			if baseWeight > 0:
				# add a small random factor
				baseWeight += 10 + random.randint(0, 10)

				# increase the value if unowned
				baseWeight *= 9 if plot.hasOwner() else 8
				baseWeight /= 8

				# lower the value if owned by a major
				baseWeight *= 11 # (pPlot->getOwner() > NO_PLAYER & & pPlot->getOwner() < MAX_MAJOR_CIVS) ? 11: 12;
				baseWeight /= 12

				# lower the value if tile has been improved
				baseWeight *= 7 if plot.improvement() != ImprovementType.none else 8
				baseWeight /= 8

				# lower the value if tile has a city
				baseWeight *= 1 if plot.isCity() else 5
				baseWeight /= 5

				# increase the value if in thematic terrain(desert, jungle, or small island)
				baseWeight *= 3 if plot.terrain() == TerrainType.desert else 2
				baseWeight *= 3 if plot.feature() == FeatureType.rainforest else 2

				area = self.areaOf(plot.point)
				baseWeight *= 3 if len(area.points()) <= 4 else 2

				# lower the value by number of neighbors
				divisor = 1

				# lower the value if there is at least one nearby site(say, 3 tiles distance)
				for loopPoint in plot.point.areaWithRadius(3):
					if not self.valid(loopPoint):
						continue

					if scratchDigSites[self._map.indexFor(loopPoint)].artifactType != ArtifactType.none:
						divisor += 1

				for loopPoint in plot.point.areaWithRadius(2):
					if not self.valid(loopPoint):
						continue

					if scratchDigSites[self._map.indexFor(loopPoint)].artifactType != ArtifactType.none:
						divisor += 1

				for loopPoint in plot.point.areaWithRadius(1):
					if not self.valid(loopPoint):
						continue

					if scratchDigSites[self._map.indexFor(loopPoint)].artifactType != ArtifactType.none:
						divisor += 1

				baseWeight /= divisor

		return baseWeight

	def calculateInfluenceDistanceFrom(self, cityLocation: HexPoint, targetDestination: HexPoint, limit: int) -> int:
		if cityLocation == targetDestination:
			return 0

		if cityLocation.distance(targetDestination) > limit:
			return 0

		influencePathfinderDataSource = InfluencePathfinderDataSource(self._map, cityLocation)
		influencePathfinder = AStarPathfinder(influencePathfinderDataSource)

		path = influencePathfinder.shortestPath(cityLocation, targetDestination)
		if path is not None:
			return int(path.cost())

		return 0

	def greatPersonOf(self, greatPersonType: GreatPersonType, greatPersonPoints: int, player) -> Optional[GreatPerson]:
		# find possible person(with correct type)
		greatPersonOfType = next(filter(lambda gp: gp.greatPersonType == greatPersonType, self.greatPersons.current), None)
		if greatPersonOfType is not None:
			#  check if there are enough great person points
			if self.costOf(greatPersonType, player) <= greatPersonPoints:
				return greatPersonOfType

		return None

	def costOf(self, greatPersonType: GreatPersonType, player) -> int:
		# find possible person(with correct type)
		greatPersonOfType = next(filter(lambda gp: gp.greatPersonType == greatPersonType, self.greatPersons.current), None)
		if greatPersonOfType is not None:
			# check if there are enough great person points
			if player.currentEra() < greatPersonOfType.era():
				# If the world's average era is below of the first GP of a new era of a certain type, there's a fixed
				# increase +30% in price
				return greatPersonOfType.cost() * 130 / 100
			else:
				return greatPersonOfType.cost()

		return -1

	def enterEra(self, era: EraType, player):
		# https://civilization.fandom.com/wiki/Era_(Civ6)
		# Roads will upgrade when you enter the Classical Era, again when you enter the Industrial Era,
		# and again on entering the Modern Era.
		# not implemented

		# Many policy cards only work for specific eras.When you progress to a more advanced era, you may find
		# that the policies you were using are no longer working, or have indeed been replaced altogether!
		player.government.verify(self)

		# The price of buying tiles will go up with Individual Eras.
		# not implemented
		return

	def foundPantheonBy(self, player, pantheonType: PantheonType):
		self._religions.foundPantheonBy(player, pantheonType, self)

	def religions(self) -> [PlayerReligion]:
		return self._religions.religions(self)

	def numberOfAvailableReligions(self) -> int:
		return self._religions.numberOfAvailableReligions(self)

	def availableReligions(self) -> [ReligionType]:
		return self._religions.availableReligions(self)

	def maxActiveReligions(self) -> int:
		return self.mapSize().maxActiveReligions()

	def availablePantheons(self) -> [PantheonType]:
		return self._religions.availablePantheons(self)

	def friendlyCityAdjacentTo(self, point: HexPoint, player) -> Optional[City]:
		diplomacyAI = player.diplomacyAI

		for neighbor in point.neighbors():
			loopCity = self.cityAt(neighbor)
			if loopCity is not None:
				if not diplomacyAI.isAtWarWith(loopCity.player):
					return loopCity

		return None

	def nearestCity(self, pt: HexPoint, player, onSameContinent: bool = False) -> Optional[City]:
		"""check if a city (of player or not) is in neighborhood"""
		return self._map.nearestCity(pt, player, onSameContinent)

	def doBarbarianCampCleared(self, leader: LeaderType, point: HexPoint):
		self.barbarianAI.doBarbarianCampCleared(leader, point, self)

		# check quests - is there still a camp
		for cityStatePlayer in self.players:
			if not cityStatePlayer.isCityState():
				continue

			for loopPlayer in self.players:
				if loopPlayer.isBarbarian():
					continue

				if loopPlayer.isFreeCity():
					continue

				if loopPlayer.isCityState():
					continue

				quest = cityStatePlayer.questFor(loopPlayer.leader)

				if quest is not None and quest.questType == CityStateQuestType.destroyBarbarianOutput:
					questLocation: HexPoint = quest.location
					if questLocation == point and loopPlayer.leader == quest.leader:
						cityStatePlayer.obsoleteQuestFor(loopPlayer.leader, self)

		# reset discovered barbarian camps
		for player in self.players:
			player.forgetDiscoverBarbarianCampAt(point)

		return

	def countMajorCivilizationsMetWith(self, cityState: CityStateType) -> int:
		"""
		number of major players / civilization that have met a certain `cityState`

		@param cityState:  city state to get the number
		@return: number of major players that have met the `cityState`
		"""
		numberOfCivilizations: int = 0

		cityStatePlayer = self.cityStatePlayerFor(cityState)

		if cityStatePlayer is None:
			raise Exception(f"cant get player for city state: {cityState}")

		for player in self.players:
			if player.isBarbarian():
				continue

			if player.isFreeCity():
				continue

			if player.isCityState():
				continue

			if player.hasMetWith(cityStatePlayer):
				numberOfCivilizations += 1

		return numberOfCivilizations

	def doCampAttackedAt(self, point: HexPoint):
		self.barbarianAI.doCampAttackedAt(point)

	def isPrimarilyNaval(self) -> bool:
		return False

	def numberOfTradeRoutesAt(self, location: HexPoint) -> int:
		result: int = 0

		for player in self.players:
			result += player.tradeRoutes.numberOfTradeRoutesAt(location)

		return result

	def countMajorCivsAlive(self) -> int:
		result: int = 0

		for loopPlayer in self.players:
			if not loopPlayer.isAlive():
				continue

			if not loopPlayer.isMajorAI() and not loopPlayer.isHuman():
				continue

			result += 1

		return result

	def countCivPlayersEverAlive(self) -> int:
		count = 0

		for loopPlayer in self.players:
			if not loopPlayer.isMajorAI() and not loopPlayer.isHuman():
				continue

			if loopPlayer.isEverAlive():
				count += 1

			return count

	def populateDigSiteOn(self, plot, era, artifact):
		raise Exception('not implemented: populateDigSiteOn')
