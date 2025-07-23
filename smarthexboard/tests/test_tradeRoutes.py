import unittest

from smarthexboard.smarthexboardlib.core.types import EraType
from smarthexboard.smarthexboardlib.game.ai.cities import BuildableItem
from smarthexboard.smarthexboardlib.game.baseTypes import HandicapType
from smarthexboard.smarthexboardlib.game.buildings import BuildingType
from smarthexboard.smarthexboardlib.game.civilizations import LeaderType
from smarthexboard.smarthexboardlib.game.game import GameModel
from smarthexboard.smarthexboardlib.game.generation import UserInterfaceImpl
from smarthexboard.smarthexboardlib.game.governments import GovernmentType
from smarthexboard.smarthexboardlib.game.players import Player
from smarthexboard.smarthexboardlib.game.states.victories import VictoryType
from smarthexboard.smarthexboardlib.game.types import TechType, CivicType
from smarthexboard.smarthexboardlib.game.unitTypes import UnitType
from smarthexboard.smarthexboardlib.game.units import Unit, UnitTradeRouteData
from smarthexboard.smarthexboardlib.map.base import HexPoint
from smarthexboard.smarthexboardlib.map.generation import MapOptions, MapGenerator
from smarthexboard.smarthexboardlib.map.types import MapSize, TerrainType, MapType, ResourceType
from smarthexboard.tests.test_utils import MapModelMock


class TestTradeRoutes(unittest.TestCase):

	def setUp(self) -> None:
		self.sourceLocation = HexPoint(3, 5)
		self.targetLocation = HexPoint(8, 5)

		self.hasVisited = False
		self.targetVisited = 0
		self.sourceVisited = 0
		self.hasExpired = False

	def moveCallback(self, location: HexPoint):
		if location == self.targetLocation:
			self.hasVisited = True
			self.targetVisited += 1

		if location == self.sourceLocation:
			self.sourceVisited += 1

		# print(f'moveCallback({location})')

	def test_canEstablishTraderoute_no_civic(self):
		# GIVEN
		barbarianPlayer = Player(LeaderType.barbar, human=False)
		barbarianPlayer.initialize()

		playerVictoria = Player(LeaderType.victoria, human=False)
		playerVictoria.initialize()

		humanPlayer = Player(LeaderType.alexander, human=True)
		humanPlayer.initialize()

		mapModel = MapModelMock(MapSize.small, TerrainType.grass)

		mapOptions = MapOptions(MapSize.duel, MapType.continents, LeaderType.alexander, [LeaderType.victoria])

		mapGenerator = MapGenerator(mapOptions)
		mapGenerator._identifyContinents(mapModel)
		mapGenerator._identifyOceans(mapModel)
		mapGenerator._identifyStartPositions(mapModel)

		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.king,
			turnsElapsed=0,
			players=[barbarianPlayer, playerVictoria, humanPlayer],
			map=mapModel
		)

		# add UI
		simulation.userInterface = UserInterfaceImpl()

		playerVictoria.doUpdateTradeRouteCapacity(simulation)

		# when
		canEstablish = playerVictoria.canEstablishTradeRoute()

		# then
		self.assertEqual(canEstablish, False)

	def test_both_cities_homeland(self):
		# GIVEN
		barbarianPlayer = Player(LeaderType.barbar, human=False)
		barbarianPlayer.initialize()

		aiPlayer = Player(LeaderType.victoria, human=False)
		aiPlayer.initialize()

		humanPlayer = Player(LeaderType.alexander, human=True)
		humanPlayer.initialize()

		mapModel = MapModelMock(MapSize.small, TerrainType.grass)
		mapModel.modifyTerrainAt(HexPoint(1, 2), TerrainType.plains)
		mapModel.modifyIsHillsAt(HexPoint(1, 2), True)
		mapModel.modifyResourceAt(HexPoint(1, 2), ResourceType.wheat)
		mapModel.modifyTerrainAt(HexPoint(3, 2), TerrainType.plains)
		mapModel.modifyResourceAt(HexPoint(3, 2), ResourceType.iron)

		mapOptions = MapOptions(MapSize.duel, MapType.continents, LeaderType.alexander, [LeaderType.victoria])

		mapGenerator = MapGenerator(mapOptions)
		mapGenerator._identifyContinents(mapModel)
		mapGenerator._identifyOceans(mapModel)
		mapGenerator._identifyStartPositions(mapModel)

		gameModel = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.king,
			turnsElapsed=0,
			players=[barbarianPlayer, aiPlayer, humanPlayer],
			map=mapModel
		)

		# add UI
		gameModel.userInterface = UserInterfaceImpl()

		# Human - setup
		humanPlayer.techs.discover(TechType.pottery, gameModel)
		humanPlayer.techs.setCurrentTech(TechType.irrigation, gameModel)
		humanPlayer.civics.discover(CivicType.codeOfLaws, gameModel)
		humanPlayer.civics.discover(CivicType.foreignTrade, gameModel)
		humanPlayer.civics.setCurrentCivic(CivicType.craftsmanship, gameModel)
		humanPlayer.government.setGovernment(GovernmentType.chiefdom, gameModel)
		# humanPlayer.government.set(policyCardSet: PolicyCardSet(cards: [.godKing, .discipline]))

		# AI units
		aiPlayer.foundAt(HexPoint(25, 5), "AI Capital", gameModel)

		# Human - city 1
		humanPlayer.foundAt(HexPoint(3, 5), "Human Capital", gameModel)

		humanCapital = gameModel.cityAt(HexPoint(3, 5))
		humanCapital._buildQueue.append(BuildableItem(BuildingType.granary))

		# Human - city 2
		humanPlayer.foundAt(HexPoint(8, 5), "Human City", gameModel)
		humanCity = gameModel.cityAt(HexPoint(8, 5))
		humanCity._buildQueue.append(BuildableItem(BuildingType.granary))

		traderUnit = Unit(HexPoint(4, 5), UnitType.trader, humanPlayer)
		traderUnit._originLocation = HexPoint(3, 5)
		gameModel.addUnit(traderUnit)
		gameModel.userInterface.showUnit(traderUnit, HexPoint(4, 5))

		mapModel.discover(humanPlayer, gameModel)

		traderUnit.unitMoved = self.moveCallback

		# WHEN
		traderUnit.doEstablishTradeRouteTo(humanCity, gameModel)

		self.sourceLocation = HexPoint(3, 5)
		self.targetLocation = HexPoint(8, 5)

		self.hasVisited = False
		self.targetVisited = 0
		self.sourceVisited = 0
		self.hasExpired = False

		while gameModel.currentTurn < 35 and not self.hasExpired:
			gameModel.update()

			while not(humanPlayer.hasProcessedAutoMoves() and humanPlayer.turnFinished()):
				gameModel.update()

				if humanPlayer.isTurnActive():
					humanPlayer.setProcessedAutoMovesTo(True)
					humanPlayer.setEndTurnTo(True, gameModel)
					humanPlayer.finishTurn()

			if not traderUnit.isTrading():
				self.hasExpired = True

		# THEN
		self.assertEqual(self.hasVisited, True, "not visited trade city within first 30 turns")
		self.assertEqual(self.targetVisited, 3)
		self.assertEqual(self.sourceVisited, 3)
		self.assertEqual(self.hasExpired, True)

	def test_durations(self):
		tradeRouteData = UnitTradeRouteData(None, 0)

		self.assertEqual(tradeRouteData.tradeRouteDurationIn(None), 21)
		self.assertEqual(tradeRouteData.tradeRouteDurationIn(EraType.ancient), 21)
		self.assertEqual(tradeRouteData.tradeRouteDurationIn(EraType.classical), 21)
		self.assertEqual(tradeRouteData.tradeRouteDurationIn(EraType.medieval), 31)
		self.assertEqual(tradeRouteData.tradeRouteDurationIn(EraType.renaissance), 31)
		self.assertEqual(tradeRouteData.tradeRouteDurationIn(EraType.industrial), 41)
		self.assertEqual(tradeRouteData.tradeRouteDurationIn(EraType.modern), 41)
		self.assertEqual(tradeRouteData.tradeRouteDurationIn(EraType.atomic), 41)
		self.assertEqual(tradeRouteData.tradeRouteDurationIn(EraType.information), 51)
		self.assertEqual(tradeRouteData.tradeRouteDurationIn(EraType.future), 51)

	def test_possibleTradeRouteTargets(self):
		# GIVEN
		barbarianPlayer = Player(LeaderType.barbar, human=False)
		barbarianPlayer.initialize()

		aiPlayer = Player(LeaderType.victoria, human=False)
		aiPlayer.initialize()

		humanPlayer = Player(LeaderType.alexander, human=True)
		humanPlayer.initialize()

		mapModel = MapModelMock(MapSize.small, TerrainType.grass)
		mapOptions = MapOptions(MapSize.duel, MapType.continents, LeaderType.alexander, [LeaderType.victoria])

		mapGenerator = MapGenerator(mapOptions)
		mapGenerator._identifyContinents(mapModel)
		mapGenerator._identifyOceans(mapModel)
		mapGenerator._identifyStartPositions(mapModel)

		gameModel = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.king,
			turnsElapsed=0,
			players=[barbarianPlayer, aiPlayer, humanPlayer],
			map=mapModel
		)

		# add UI
		gameModel.userInterface = UserInterfaceImpl()

		# Human - setup
		humanPlayer.techs.discover(TechType.pottery, gameModel)
		humanPlayer.techs.setCurrentTech(TechType.irrigation, gameModel)
		humanPlayer.civics.discover(CivicType.codeOfLaws, gameModel)
		humanPlayer.civics.discover(CivicType.foreignTrade, gameModel)
		humanPlayer.civics.setCurrentCivic(CivicType.craftsmanship, gameModel)
		humanPlayer.government.setGovernment(GovernmentType.chiefdom, gameModel)
		# humanPlayer.government.set(policyCardSet: PolicyCardSet(cards: [.godKing, .discipline]))

		# AI cities - capital
		aiPlayer.foundAt(HexPoint(15, 5), "AI Capital", gameModel)

		# AI cities - city 2
		aiPlayer.foundAt(HexPoint(8, 5), "AI City", gameModel)
		aiPlayerCity = gameModel.cityAt(HexPoint(8, 5))
		aiPlayerCity.cityTradingPosts.buildTradingPost(humanPlayer.leader)

		# Human - city 1
		humanPlayer.foundAt(HexPoint(3, 5), "Human Capital", gameModel)
		humanCapital = gameModel.cityAt(HexPoint(3, 5))

		mapModel.discover(humanPlayer, gameModel)

		# when
		cities = humanPlayer.possibleTradeRouteTargetsFrom(humanCapital, gameModel)

		# then
		self.assertEqual(len(cities), 2)
