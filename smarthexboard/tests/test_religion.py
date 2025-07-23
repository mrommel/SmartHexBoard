import unittest

from smarthexboard.smarthexboardlib.game.baseTypes import HandicapType
from smarthexboard.smarthexboardlib.game.cities import City
from smarthexboard.smarthexboardlib.game.civilizations import LeaderType
from smarthexboard.smarthexboardlib.game.districts import DistrictType
from smarthexboard.smarthexboardlib.game.game import GameModel
from smarthexboard.smarthexboardlib.game.generation import UserInterfaceImpl
from smarthexboard.smarthexboardlib.game.players import Player
from smarthexboard.smarthexboardlib.game.religions import PantheonFoundingType, PantheonType, ReligionType
from smarthexboard.smarthexboardlib.game.states.victories import VictoryType
from smarthexboard.smarthexboardlib.game.unitTypes import UnitType
from smarthexboard.smarthexboardlib.game.units import Unit
from smarthexboard.smarthexboardlib.map.base import HexPoint
from smarthexboard.smarthexboardlib.map.generation import MapGenerator, MapOptions
from smarthexboard.smarthexboardlib.map.improvements import ImprovementType
from smarthexboard.smarthexboardlib.map.types import MapSize, TerrainType, MapType, ResourceType
from smarthexboard.tests.test_utils import MapModelMock


class TestReligion(unittest.TestCase):
	def setUp(self) -> None:
		# GIVEN
		barbarianPlayer = Player(LeaderType.barbar, human=False)
		barbarianPlayer.initialize()

		self.playerVictoria = Player(LeaderType.victoria, human=False)
		self.playerVictoria.initialize()

		humanPlayer = Player(LeaderType.alexander, human=True)
		humanPlayer.initialize()

		mapModel = MapModelMock(MapSize.small, TerrainType.grass)

		mapOptions = MapOptions(MapSize.duel, MapType.continents, LeaderType.alexander, [LeaderType.victoria])

		mapGenerator = MapGenerator(mapOptions)
		mapGenerator._identifyContinents(mapModel)
		mapGenerator._identifyOceans(mapModel)
		mapGenerator._identifyStartPositions(mapModel)

		self.simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.king,
			turnsElapsed=0,
			players=[barbarianPlayer, self.playerVictoria, humanPlayer],
			map=mapModel
		)

		# add UI
		self.simulation.userInterface = UserInterfaceImpl()

	def test_canFoundPantheon_notEnoughFaith(self):
		# given

		# when
		foundReason: PantheonFoundingType = self.playerVictoria.religion.canFoundPantheon(True, self.simulation)

		# then
		self.assertEqual(foundReason, PantheonFoundingType.notEnoughFaith)

	def test_canFoundPantheon_alreadyCreatedPantheon(self):
		# given
		self.playerVictoria.religion._pantheon = PantheonType.godOfWar
		self.playerVictoria.religion.changeFaith(50)

		# when
		foundReason: PantheonFoundingType = self.playerVictoria.religion.canFoundPantheon(True, self.simulation)

		# then
		self.assertEqual(foundReason, PantheonFoundingType.alreadyCreatedPantheon)

	def test_canFoundPantheon_okay(self):
		# given
		self.playerVictoria.religion.changeFaith(50)

		# when
		foundReason: PantheonFoundingType = self.playerVictoria.religion.canFoundPantheon(True, self.simulation)

		# then
		self.assertEqual(foundReason, PantheonFoundingType.okay)

	def test_doFaith_foundPantheon(self):
		# given
		self.playerVictoria.religion.changeFaith(50)

		self.playerVictoria.foundAt(HexPoint(5, 5), "Berlin", self.simulation)
		self.simulation.tileAt(HexPoint(5, 6)).setImprovement(ImprovementType.camp)
		self.simulation.tileAt(HexPoint(6, 6)).setResource(ResourceType.wheat)

		# when
		pantheonBefore: PantheonType = self.playerVictoria.religion.pantheon()
		self.playerVictoria.doFaith(self.simulation)
		pantheonAfter: PantheonType = self.playerVictoria.religion.pantheon()

		# then
		self.assertEqual(pantheonBefore, PantheonType.none)
		self.assertNotEqual(pantheonAfter, PantheonType.none)

	def test_canFoundReligionInPlace_no_holySite(self):
		# given
		greatProphet = Unit(HexPoint(5, 5), UnitType.prophet, self.playerVictoria)
		self.simulation.addUnit(greatProphet)

		# when
		canFound: bool = greatProphet.canFoundReligionInPlace(self.simulation)

		# then
		self.assertEqual(canFound, False)

	def test_canFoundReligionInPlace_holySite(self):
		# given
		greatProphet = Unit(HexPoint(5, 5), UnitType.prophet, self.playerVictoria)
		self.simulation.addUnit(greatProphet)

		city = City("Berlin", HexPoint(6, 6), True, self.playerVictoria)
		city.initialize(self.simulation)
		self.simulation.addCity(city)

		city.buildDistrict(DistrictType.holySite, HexPoint(5, 5), self.simulation)

		self.playerVictoria.religion.foundPantheon(PantheonType.godOfWar, self.simulation)

		# when
		canFound: bool = greatProphet.canFoundReligionInPlace(self.simulation)

		# then
		self.assertEqual(canFound, True)

	def test_foundReligionInPlace_holySite(self):
		# given
		greatProphet = Unit(HexPoint(5, 5), UnitType.prophet, self.playerVictoria)
		self.simulation.addUnit(greatProphet)

		city = City("Berlin", HexPoint(6, 6), True, self.playerVictoria)
		city.initialize(self.simulation)
		self.simulation.addCity(city)

		city.buildDistrict(DistrictType.holySite, HexPoint(5, 5), self.simulation)

		self.playerVictoria.religion.foundPantheon(PantheonType.godOfWar, self.simulation)

		# when
		canFound: bool = greatProphet.doFoundReligionInPlace(self.simulation)

		# then
		self.assertEqual(canFound, True)
		self.assertEqual(self.playerVictoria.religion.hasCreatedReligion(), True)
		self.assertNotEqual(self.playerVictoria.religion.currentReligion(), ReligionType.none)
