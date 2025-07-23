import logging
import os
import unittest

import django

from smarthexboard.smarthexboardlib.game.ai.baseTypes import MilitaryStrategyType
from smarthexboard.smarthexboardlib.game.baseTypes import HandicapType, GameState
from smarthexboard.smarthexboardlib.game.civilizations import LeaderType
from smarthexboard.smarthexboardlib.game.game import GameModel
from smarthexboard.smarthexboardlib.game.generation import UserInterfaceImpl, GameGenerator
from smarthexboard.smarthexboardlib.game.players import Player
from smarthexboard.smarthexboardlib.game.states.builds import BuildType
from smarthexboard.smarthexboardlib.game.states.victories import VictoryType
from smarthexboard.smarthexboardlib.game.types import TechType, CivicType
from smarthexboard.smarthexboardlib.game.unitTypes import UnitType, UnitActivityType, UnitAutomationType
from smarthexboard.smarthexboardlib.game.units import Unit
from smarthexboard.smarthexboardlib.map.base import HexPoint
from smarthexboard.smarthexboardlib.map.generation import MapOptions, MapGenerator
from smarthexboard.smarthexboardlib.map.improvements import ImprovementType
from smarthexboard.smarthexboardlib.map.map import MapModel, Tile
from smarthexboard.smarthexboardlib.map.types import TerrainType, MapSize, MapType
from smarthexboard.tests.test_utils import MapModelMock

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()


class TestPlayerTechs(unittest.TestCase):
	def setUp(self) -> None:
		self.map = MapModel(10, 10)
		self.simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=self.map
		)

		self.player = Player(leader=LeaderType.alexander, cityState=None, human=False)
		self.player.initialize()

		self.playerTechs = self.player.techs

	def test_possible_techs(self):
		# GIVEN
		self.playerTechs.discover(tech=TechType.pottery, simulation=self.simulation)
		self.playerTechs.discover(tech=TechType.animalHusbandry, simulation=self.simulation)
		self.playerTechs.discover(tech=TechType.mining, simulation=self.simulation)
		self.playerTechs.discover(tech=TechType.sailing, simulation=self.simulation)
		self.playerTechs.discover(tech=TechType.astrology, simulation=self.simulation)
		self.playerTechs.discover(tech=TechType.irrigation, simulation=self.simulation)
		self.playerTechs.discover(tech=TechType.writing, simulation=self.simulation)
		self.playerTechs.discover(tech=TechType.bronzeWorking, simulation=self.simulation)

		# WHEN
		possibleTechs = self.playerTechs.possibleTechs()

		# THEN
		# self.assertEqual(playerTech.currentTech(), None)
		expected = [
			TechType.masonry,
			TechType.archery,
			TechType.wheel,
			TechType.celestialNavigation,
			TechType.horsebackRiding,
			TechType.currency,
			TechType.ironWorking,
			TechType.shipBuilding
		]
		self.assertCountEqual(possibleTechs, expected)

	def test_current_tech(self):
		# GIVEN
		self.playerTechs.discover(tech=TechType.pottery, simulation=self.simulation)

		# WHEN
		self.playerTechs.setCurrentTech(TechType.writing, self.simulation)

		# THEN
		self.assertEqual(self.playerTechs.currentTech(), TechType.writing)

	def test_choose_next_techs(self):
		# GIVEN

		# WHEN
		nextTech = self.playerTechs.chooseNextTech()

		# THEN
		expected = [
			TechType.mining,
			TechType.pottery,
			TechType.animalHusbandry
		]
		self.assertTrue(nextTech in expected, f'{nextTech} not in {expected}')

	def test_eureka(self):
		# GIVEN
		self.playerTechs.discover(tech=TechType.pottery, simulation=self.simulation)

		self.playerTechs.setCurrentTech(TechType.writing, self.simulation)
		progressBefore = self.playerTechs.currentScienceProgress()

		# WHEN
		self.playerTechs.triggerEurekaFor(tech=TechType.writing, simulation=self.simulation)
		progressAfter = self.playerTechs.currentScienceProgress()

		# THEN
		self.assertEqual(self.playerTechs.eurekaTriggeredFor(TechType.writing), True)
		self.assertEqual(progressBefore, 0.0)
		self.assertEqual(progressAfter, 25.0)


class TestPlayerCivics(unittest.TestCase):
	def setUp(self) -> None:
		self.map = MapModel(10, 10)
		self.simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=self.map
		)

		self.player = Player(leader=LeaderType.alexander, cityState=None, human=False)
		self.player.initialize()

		self.playerCivics = self.player.civics

	def test_possible_civics(self):
		# GIVEN
		self.playerCivics.discover(civic=CivicType.codeOfLaws, simulation=self.simulation)

		# WHEN
		possibleCivics = self.playerCivics.possibleCivics()

		# THEN
		# self.assertEqual(playerCivics.currentCivic(), None)
		expected = [
			CivicType.foreignTrade,
			CivicType.craftsmanship
		]
		self.assertCountEqual(possibleCivics, expected)

	def test_current_civic(self):
		# GIVEN
		self.playerCivics.discover(civic=CivicType.codeOfLaws, simulation=self.simulation)

		# WHEN
		self.playerCivics.setCurrentCivic(CivicType.foreignTrade, self.simulation)

		# THEN
		self.assertEqual(self.playerCivics.currentCivic(), CivicType.foreignTrade)

	def test_inspiration(self):
		# GIVEN
		self.playerCivics.discover(civic=CivicType.codeOfLaws, simulation=self.simulation)

		self.playerCivics.setCurrentCivic(CivicType.foreignTrade, self.simulation)
		progressBefore = self.playerCivics.currentCultureProgress()

		# WHEN
		self.playerCivics.triggerInspirationFor(civic=CivicType.foreignTrade, simulation=self.simulation)
		progressAfter = self.playerCivics.currentCultureProgress()

		# THEN
		self.assertEqual(self.playerCivics.inspirationTriggeredFor(CivicType.foreignTrade), True)
		self.assertEqual(progressBefore, 0.0)
		self.assertEqual(progressAfter, 20.0)

	def test_eureka_of_craftsmanship(self):
		# GIVEN
		self.playerCivics.discover(CivicType.codeOfLaws, simulation=self.simulation)

		tile0: Tile = self.map.tileAt(HexPoint(0, 0))
		tile0.setOwner(self.player)
		tile1: Tile = self.map.tileAt(HexPoint(1, 0))
		tile1.setOwner(self.player)
		tile2: Tile = self.map.tileAt(HexPoint(0, 1))
		tile2.setOwner(self.player)

		# WHEN
		beforeEureka = self.playerCivics.inspirationTriggeredFor(CivicType.craftsmanship)
		tile0.changeBuildProgressOf(BuildType.farm, change=1000, player=self.player, simulation=self.simulation)
		tile1.changeBuildProgressOf(BuildType.farm, change=1000, player=self.player, simulation=self.simulation)
		tile2.changeBuildProgressOf(BuildType.farm, change=1000, player=self.player, simulation=self.simulation)
		afterEureka = self.playerCivics.inspirationTriggeredFor(CivicType.craftsmanship)

		# THEN
		self.assertEqual(beforeEureka, False)
		self.assertEqual(afterEureka, True)


class TestPlayerStrategies(unittest.TestCase):
	def test_eradicate_barbarian(self):
		# GIVEN
		mapModel = MapModelMock(10, 10, TerrainType.ocean)
		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=mapModel
		)

		player = Player(LeaderType.trajan, human=True)
		player.initialize()
		simulation.players.append(player)

		barbarianPlayer = Player(LeaderType.barbar, human=False)
		barbarianPlayer.initialize()
		simulation.players.append(barbarianPlayer)

		simulation.userInterface = UserInterfaceImpl()
		simulation.currentTurn = 30  # not before 25 and check every 5 turns

		tile0 = simulation.tileAt(HexPoint(3, 3))
		# tile0.sightBy(player)
		tile0.discoverBy(player, simulation)
		tile0.setOwner(player)
		tile0.setImprovement(ImprovementType.barbarianCamp)

		tile1 = simulation.tileAt(HexPoint(3, 4))
		tile1.sightBy(player)

		barbarianWarrior = Unit(HexPoint(3, 4), UnitType.barbarianWarrior, player)
		simulation.addUnit(barbarianWarrior)

		# WHEN
		player.doTurn(simulation)

		# THEN
		self.assertEqual(player.militaryAI.adopted(MilitaryStrategyType.eradicateBarbarians), True)


class TestSimulation(unittest.TestCase):
	def test_found_capital(self):
		# GIVEN
		mapModel = MapModelMock(10, 10, TerrainType.ocean)
		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=mapModel
		)
		
		playerTrajan = Player(LeaderType.trajan, human=True)
		playerTrajan.initialize()

		playerAlexander = Player(LeaderType.alexander, human=False)
		playerAlexander.initialize()

		simulation.players.append(playerAlexander)
		simulation.players.append(playerTrajan)

		simulation.userInterface = UserInterfaceImpl()

		capitalBefore = simulation.capitalOf(playerTrajan)
		totalCitiesFoundedBefore = playerTrajan.numberOfCitiesFounded()

		# WHEN
		playerTrajan.foundAt(HexPoint(4, 5), "Berlin", simulation)

		capitalAfter = simulation.capitalOf(playerTrajan)
		totalCitiesFoundedAfter = playerTrajan.numberOfCitiesFounded()

		# THEN
		self.assertIsNone(capitalBefore)
		self.assertEqual(totalCitiesFoundedBefore, 0)
		self.assertIsNotNone(capitalAfter)
		self.assertEqual(totalCitiesFoundedAfter, 1)

	def test_player_turn(self):
		# GIVEN
		mapModel = MapModelMock(MapSize.tiny, TerrainType.grass)
		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=mapModel
		)

		playerBarbar = Player(LeaderType.barbar, human=False)
		playerBarbar.initialize()
		simulation.players.append(playerBarbar)

		playerTrajan = Player(LeaderType.trajan, human=False)
		playerTrajan.initialize()
		simulation.players.append(playerTrajan)

		playerAlexander = Player(LeaderType.alexander, human=True)
		playerAlexander.initialize()
		simulation.players.append(playerAlexander)

		# add UI
		simulation.userInterface = UserInterfaceImpl()

		playerTrajan.foundAt(HexPoint(4, 5), "Berlin", simulation)

		playerAlexander.foundAt(HexPoint(14, 5), "Potsdam", simulation)

		# WHEN
		iteration = 0
		while not(playerAlexander.hasProcessedAutoMoves() and playerAlexander.turnFinished()) and iteration < 25:
			simulation.update()  # the checks happen here
			logging.debug(f'-- loop {iteration} -- active player: {simulation.activePlayer()} --')

			if playerAlexander.isTurnActive():
				playerAlexander.setProcessedAutoMovesTo(True)  # units have moved
				playerAlexander.finishTurn()  # turn button clicked

			iteration += 1

		# THEN
		self.assertLess(iteration, 25, 'maximum iterations reached')

	def test_remove_unit(self):
		# GIVEN
		mapModel = MapModelMock(MapSize.tiny, TerrainType.grass)
		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=mapModel
		)

		playerBarbar = Player(LeaderType.barbar, human=False)
		playerBarbar.initialize()
		simulation.players.append(playerBarbar)

		# add UI
		simulation.userInterface = UserInterfaceImpl()

		playerBarbarArcher = Unit(HexPoint(6, 6), UnitType.barbarianArcher, playerBarbar)
		simulation.addUnit(playerBarbarArcher)

		playerBarbarWarriorFirst = Unit(HexPoint(5, 7), UnitType.barbarianWarrior, playerBarbar)
		simulation.addUnit(playerBarbarWarriorFirst)

		# WHEN
		unitsBefore = len(simulation.unitsOf(playerBarbar))

		playerBarbarWarrior = Unit(HexPoint(5, 6), UnitType.barbarianWarrior, playerBarbar)
		simulation.addUnit(playerBarbarWarrior)

		unitsMid = len(simulation.unitsOf(playerBarbar))

		simulation.removeUnit(playerBarbarWarrior)

		unitsAfter = len(simulation.unitsOf(playerBarbar))

		# THEN
		self.assertEqual(unitsBefore, 2)
		self.assertEqual(unitsMid, 3)
		self.assertEqual(unitsAfter, 2)


class TestUsecases(unittest.TestCase):
	def test_first_city_build(self):
		# GIVEN
		mapModel = MapModelMock(MapSize.tiny, TerrainType.grass)
		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=mapModel
		)

		# players
		playerBarbar = Player(LeaderType.barbar, human=False)
		playerBarbar.initialize()
		simulation.players.append(playerBarbar)

		playerTrajan = Player(LeaderType.trajan, human=False)
		playerTrajan.initialize()
		simulation.players.append(playerTrajan)

		playerAlexander = Player(LeaderType.alexander, human=True)
		playerAlexander.initialize()
		simulation.players.append(playerAlexander)

		# add UI
		simulation.userInterface = UserInterfaceImpl()

		# initial units
		playerAlexanderWarrior = Unit(HexPoint(5, 6), UnitType.warrior, playerAlexander)
		simulation.addUnit(playerAlexanderWarrior)

		playerAugustusSettler = Unit(HexPoint(15, 15), UnitType.settler, playerTrajan)
		simulation.addUnit(playerAugustusSettler)

		playerAugustusWarrior = Unit(HexPoint(15, 16), UnitType.warrior, playerTrajan)
		simulation.addUnit(playerAugustusWarrior)

		playerBarbarianWarrior = Unit(HexPoint(10, 10), UnitType.barbarianWarrior, playerBarbar)
		simulation.addUnit(playerBarbarianWarrior)

		# this is cheating
		mapModel.discover(playerAlexander, simulation)
		mapModel.discover(playerTrajan, simulation)
		mapModel.discover(playerBarbar, simulation)

		numberOfCitiesBefore = len(simulation.citiesOf(playerTrajan))
		numberOfUnitsBefore = len(simulation.unitsOf(playerTrajan))

		# WHEN
		iteration = 0
		while not(playerAlexander.hasProcessedAutoMoves() and playerAlexander.turnFinished()) and iteration < 25:
			simulation.update()

			if playerAlexander.isTurnActive():
				playerAlexander.setProcessedAutoMovesTo(True)  # units have moved
				playerAlexander.finishTurn()  # turn button clicked

			iteration += 1

		# THEN
		self.assertEqual(numberOfCitiesBefore, 0)
		self.assertEqual(numberOfUnitsBefore, 2)
		numberOfCitiesAfter = len(simulation.citiesOf(playerTrajan))
		numberOfUnitsAfter = len(simulation.unitsOf(playerTrajan))
		self.assertEqual(numberOfCitiesAfter, 1)
		self.assertEqual(numberOfUnitsAfter, 1)

		self.assertEqual(playerAugustusWarrior.activityType(), UnitActivityType.none)  # warrior has skipped
		# XCTAssertEqual(playerAugustusWarrior.peekMission()!.buildType, BuildType.repair)

	def test_first100turns(self):
		# GIVEN
		mapModel = MapModelMock(MapSize.tiny, TerrainType.grass)
		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=mapModel
		)

		# players
		playerBarbar = Player(LeaderType.barbar, human=False)
		playerBarbar.initialize()
		simulation.players.append(playerBarbar)

		playerTrajan = Player(LeaderType.trajan, human=False)
		playerTrajan.initialize()
		simulation.players.append(playerTrajan)

		playerAlexander = Player(LeaderType.alexander, human=True)
		playerAlexander.initialize()
		simulation.players.append(playerAlexander)

		# add UI
		simulation.userInterface = UserInterfaceImpl()

		# trajan units
		playerTrajanWarrior = Unit(HexPoint(15, 16), UnitType.warrior, playerTrajan)
		simulation.addUnit(playerTrajanWarrior)

		playerTrajanSettler = Unit(HexPoint(15, 15), UnitType.settler, playerTrajan)
		simulation.addUnit(playerTrajanSettler)

		# alexander units
		playerAlexanderScout = Unit(HexPoint(5, 6), UnitType.scout, playerAlexander)
		playerAlexanderScout.automate(UnitAutomationType.explore, simulation)
		simulation.addUnit(playerAlexanderScout)

		# barbarian units
		playerBarbarianWarrior = Unit(HexPoint(10, 10), UnitType.barbarianWarrior, playerBarbar)
		simulation.addUnit(playerBarbarianWarrior)

		# this is cheating
		# mapModel.discover(playerAlexander, simulation)
		mapModel.discover(playerTrajan, simulation)
		mapModel.discover(playerBarbar, simulation)

		numberOfCitiesBefore = len(simulation.citiesOf(playerTrajan))
		numberOfUnitsBefore = len(simulation.unitsOf(playerTrajan))

		# WHEN
		counter = 0
		while simulation.currentTurn < 50:
			simulation.update()

			while not (playerAlexander.hasProcessedAutoMoves() and playerAlexander.turnFinished()):
				simulation.update()

				if playerAlexander.isTurnActive():
					playerAlexander.setProcessedAutoMovesTo(True)
					playerAlexander.setEndTurnTo(True, simulation)
					playerAlexander.finishTurn()

				counter += 1

		# THEN
		self.assertEqual(numberOfCitiesBefore, 0)
		self.assertEqual(numberOfUnitsBefore, 2)
		numberOfCitiesAfter = len(simulation.citiesOf(playerTrajan))
		numberOfUnitsAfter = len(simulation.unitsOf(playerTrajan))
		self.assertGreater(numberOfCitiesAfter, 0)
		self.assertGreater(numberOfUnitsAfter, 0)

		self.assertEqual(simulation.gameState(), GameState.on)
		self.assertEqual(simulation.currentTurn, 50)

		for leader, rankingData in simulation._rankingData.rankingDict.items():
			print(f'Ranking data for {leader.title()}: ')
			print(f'+ Culture per turn: {rankingData.culturePerTurn}')
			print(f'+ Gold balance: {rankingData.goldBalance}')

	def test_units(self):
		# GIVEN
		mapModel = MapModelMock.duelMap()

		# players
		playerBarbar = Player(LeaderType.barbar, human=False)
		playerBarbar.initialize()

		playerTrajan = Player(LeaderType.trajan, human=False)
		playerTrajan.initialize()

		playerAlexander = Player(LeaderType.alexander, human=True)
		playerAlexander.initialize()

		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[playerBarbar, playerTrajan, playerAlexander],
			map=mapModel
		)

		# add UI
		simulation.userInterface = UserInterfaceImpl()

		# trajan units
		self.assertEqual(simulation.tileAt(HexPoint(20, 10)).isLand(), True)
		playerTrajanWarrior = Unit(HexPoint(20, 10), UnitType.warrior, playerTrajan)
		simulation.addUnit(playerTrajanWarrior)

		self.assertEqual(simulation.tileAt(HexPoint(25, 15)).isLand(), True)
		playerTrajanSettler = Unit(HexPoint(25, 15), UnitType.settler, playerTrajan)
		simulation.addUnit(playerTrajanSettler)

		# alexander units
		self.assertEqual(simulation.tileAt(HexPoint(12, 12)).isLand(), True)
		playerAlexanderScout = Unit(HexPoint(12, 12), UnitType.scout, playerAlexander)
		playerAlexanderScout.automate(UnitAutomationType.explore, simulation)
		simulation.addUnit(playerAlexanderScout)

		# barbarian units
		# self.assertEqual(simulation.tileAt(HexPoint(10, 10)).isLand(), True)
		# playerBarbarianWarrior = Unit(HexPoint(10, 10), UnitType.barbarianWarrior, playerBarbar)
		# simulation.addUnit(playerBarbarianWarrior)

		# this is cheating
		# mapModel.discover(playerAlexander, simulation)
		mapModel.discover(playerTrajan, simulation)
		mapModel.discover(playerBarbar, simulation)

		numberOfCitiesBefore = len(simulation.citiesOf(playerTrajan))
		numberOfUnitsBefore = len(simulation.unitsOf(playerTrajan))

		# WHEN
		counter = 0
		while simulation.currentTurn < 50:
			simulation.update()

			while not (playerAlexander.hasProcessedAutoMoves() and playerAlexander.turnFinished()):
				simulation.update()

				if playerAlexander.isTurnActive():
					playerAlexander.setProcessedAutoMovesTo(True)
					playerAlexander.setEndTurnTo(True, simulation)
					playerAlexander.finishTurn()

				counter += 1

		# THEN
		self.assertEqual(numberOfCitiesBefore, 0)
		self.assertEqual(numberOfUnitsBefore, 2)
		numberOfCitiesAfter = len(simulation.citiesOf(playerTrajan))
		numberOfUnitsAfter = len(simulation.unitsOf(playerTrajan))
		self.assertGreater(numberOfCitiesAfter, 0)
		self.assertGreater(numberOfUnitsAfter, 0)

		self.assertEqual(simulation.gameState(), GameState.on)
		self.assertEqual(simulation.currentTurn, 50)


class TestGameGeneration(unittest.TestCase):
	def test_generation_emperor(self):
		# GIVEN
		mapModel = MapModelMock(MapSize.duel, TerrainType.grass)
		options = MapOptions(mapSize=MapSize.duel, mapType=MapType.continents, leader=LeaderType.trajan)
		mapGenerator = MapGenerator(options=options)
		mapGenerator.update(mapModel)

		gameGenerator = GameGenerator()

		# WHEN
		game = gameGenerator.generate(mapModel, HandicapType.emperor)

		# THEN
		self.assertEqual(game.currentTurn, 0)
		self.assertEqual(len(game.players), 6)
