import os
import unittest
from gettext import translation
import django

from django.utils.translation.trans_real import get_language, translation
from django.utils.translation import gettext as _

from smarthexboard.smarthexboardlib.game.baseTypes import HandicapType
from smarthexboard.smarthexboardlib.game.civilizations import LeaderType
from smarthexboard.smarthexboardlib.game.game import GameModel
from smarthexboard.smarthexboardlib.game.generation import UserInterfaceImpl
from smarthexboard.smarthexboardlib.game.players import Player
from smarthexboard.smarthexboardlib.game.states.victories import VictoryType
from smarthexboard.smarthexboardlib.game.types import TechType
from smarthexboard.smarthexboardlib.game.unitTypes import UnitType
from smarthexboard.smarthexboardlib.game.units import Unit
from smarthexboard.smarthexboardlib.game.wonders import WonderType
from smarthexboard.smarthexboardlib.map.base import HexPoint
from smarthexboard.tests.test_utils import MapModelMock

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()


# mock translation for testing
def mock_gettext(message: str) -> str:
	if message == 'TXT_KEY_YIELD_FOOD_TITLE':
		return 'Food'
	elif message == 'TXT_KEY_YIELD_PRODUCTION_TITLE':
		return 'Production'
	elif message == 'TXT_KEY_YIELD_GOLD_TITLE':
		return 'Gold'
	elif message == 'TXT_KEY_LEADER_BARBARIAN':
		return 'Barbarian'
	elif message == 'TXT_KEY_CITY_NAME_AIGAI':
		return 'Aigai'
	elif message == 'TXT_KEY_CITY_NAME_ALEXANDRIA':
		return 'Alexandria'

	raise f'Translation not available for message: "{message}"'


class TestDiplomacyAI(unittest.TestCase):
	def setUp(self) -> None:
		self.mapModel = MapModelMock.duelMap()

		# players
		self.playerBarbarian = Player(LeaderType.barbar, human=False)
		self.playerBarbarian.initialize()

		self.playerAlexander = Player(LeaderType.alexander, human=False)
		self.playerAlexander.initialize()

		self.playerTrajan = Player(LeaderType.trajan, human=True)
		self.playerTrajan.initialize()

		self.simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[self.playerBarbarian, self.playerAlexander, self.playerTrajan],
			map=self.mapModel
		)

		# add UI
		self.simulation.userInterface = UserInterfaceImpl()

		# make visible
		self.mapModel.discover(self.playerAlexander, self.simulation)

		# add human scout (so that the game is not finished)
		playerTrajanScout = Unit(HexPoint(11, 19), UnitType.scout, self.playerTrajan)
		self.simulation.addUnit(playerTrajanScout)

	def test_constructor(self):
		player = Player(LeaderType.trajan)
		self.assertEqual(player.diplomacyAI.player, player)

	def test_atWar(self):
		# GIVEN
		self.playerAlexander.doFirstContactWith(self.playerTrajan, self.simulation)

		# WHEN
		isAtWarBefore = self.playerAlexander.isAtWar()
		self.playerAlexander.doDeclareWarTo(self.playerTrajan, self.simulation)
		isAtWarAfter = self.playerAlexander.isAtWar()

		# THEN
		self.assertEqual(isAtWarBefore, False)
		self.assertEqual(isAtWarAfter, True)


class TestPlayer(unittest.TestCase):
	def setUp(self) -> None:
		# mock translations
		# raise Exception(settings.LOCALE_PATHS)
		# raise Exception(get_language())
		# translation(domain=get_language(), languages=['de', 'en'], localedir='/Users/ROM5BE4/Prog/SmartHexBoard/smarthexboard/locale/').gettext = mock_gettext
		translation(get_language()).gettext = mock_gettext

		self.mapModel = MapModelMock.duelMap()

		# players
		self.playerBarbarian = Player(LeaderType.barbar, human=False)
		self.playerBarbarian.initialize()

		self.playerAlexander = Player(LeaderType.alexander, human=False)
		self.playerAlexander.initialize()

		self.playerTrajan = Player(LeaderType.trajan, human=True)
		self.playerTrajan.initialize()

		self.simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[self.playerBarbarian, self.playerAlexander, self.playerTrajan],
			map=self.mapModel
		)

		# add UI
		self.simulation.userInterface = UserInterfaceImpl()

		# make visible
		self.mapModel.discover(self.playerAlexander, self.simulation)

		# add human scout (so that the game is not finished)
		playerTrajanScout = Unit(HexPoint(11, 19), UnitType.scout, self.playerTrajan)
		self.simulation.addUnit(playerTrajanScout)

	def test_bestSettlePlotFor(self):
		# GIVEN
		settlerOne = Unit(HexPoint(29, 6), UnitType.settler, self.playerAlexander)
		self.simulation.addUnit(settlerOne)

		self.playerAlexander.foundAt(HexPoint(29, 7), "Capital", self.simulation)

		# WHEN
		self.simulation.currentTurn = 100
		bestPlotSame = self.playerAlexander.bestSettlePlotFor(settlerOne, escorted=True, sameArea=True, simulation=self.simulation)
		bestPlotDifferent = self.playerAlexander.bestSettlePlotFor(settlerOne, escorted=True, sameArea=False, simulation=self.simulation)

		# THEN
		self.assertEqual(bestPlotSame.point, HexPoint(28, 4))
		self.assertEqual(bestPlotDifferent.point, HexPoint(28, 4))

	def test_wonderCity(self):
		# GIVEN
		self.playerAlexander.techs.discover(TechType.pottery, self.simulation)
		self.playerAlexander.techs.discover(TechType.masonry, self.simulation)

		self.playerAlexander.foundAt(HexPoint(27, 5), "Capital", self.simulation)
		# capitalCity: City = self.simulation.cityAt(HexPoint(27, 5))
		self.playerAlexander.foundAt(HexPoint(23, 12), "Second", self.simulation)

		# turn must be more than 25
		self.simulation.currentTurn = 30

		# just to be sure - some pre-checks
		self.assertIsNotNone(self.simulation.areaOf(HexPoint(27, 5)))
		self.assertIsNotNone(self.simulation.areaOf(HexPoint(23, 12)))

		# WHEN
		self.playerAlexander.citySpecializationAI.doTurn(self.simulation)

		# THEN
		self.assertEqual(WonderType.pyramids, self.playerAlexander.citySpecializationAI.nextWonderDesiredValue)
		self.assertEqual(HexPoint(22, 11), self.playerAlexander.citySpecializationAI.nextWonderLocationValue)

	def test_duplicate_cityName(self):
		# GIVEN

		# WHEN
		self.playerAlexander.foundAt(HexPoint(29, 7), name=None, simulation=self.simulation)
		firstCityName = self.simulation.cityAt(HexPoint(29, 7)).name()

		self.playerAlexander.foundAt(HexPoint(11, 19), name=None, simulation=self.simulation)
		secondCityName = self.simulation.cityAt(HexPoint(11, 19)).name()

		# THEN
		self.assertEqual(_('TXT_KEY_CITY_NAME_AIGAI'), firstCityName)
		self.assertEqual(_('TXT_KEY_CITY_NAME_ALEXANDRIA'), secondCityName)
