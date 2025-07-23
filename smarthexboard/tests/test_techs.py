import unittest

import pytest

from smarthexboard.smarthexboardlib.game.baseTypes import HandicapType
from smarthexboard.smarthexboardlib.game.civilizations import LeaderType
from smarthexboard.smarthexboardlib.game.game import GameModel
from smarthexboard.smarthexboardlib.game.generation import UserInterfaceImpl
from smarthexboard.smarthexboardlib.game.playerMechanics import TechEurekas, PlayerTechs
from smarthexboard.smarthexboardlib.game.players import Player
from smarthexboard.smarthexboardlib.game.states.victories import VictoryType
from smarthexboard.smarthexboardlib.game.types import TechType
from smarthexboard.smarthexboardlib.map.types import MapSize, TerrainType
from smarthexboard.tests.test_utils import MapModelMock


class TestTechEurekas(unittest.TestCase):
	def test_constructor(self):
		# given
		eurekas = TechEurekas()

		# when - then
		self.assertFalse(eurekas.triggeredFor(TechType.archery))
		self.assertEqual(eurekas.triggerCountFor(TechType.archery), 0)

	def test_triggeredFor(self):
		# given
		eurekas = TechEurekas()

		triggeredBefore = eurekas.triggeredFor(TechType.archery)

		# when
		eurekas.triggerFor(TechType.archery)
		triggeredAfter = eurekas.triggeredFor(TechType.archery)

		# then
		self.assertFalse(triggeredBefore)
		self.assertTrue(triggeredAfter)


class TestPlayerTechs(unittest.TestCase):
	def setUp(self) -> None:
		# players
		self.barbarianPlayer = Player(LeaderType.barbar, human=False)
		self.barbarianPlayer.initialize()

		self.playerTrajan = Player(LeaderType.trajan, human=False)
		self.playerTrajan.initialize()

		self.playerAlexander = Player(LeaderType.alexander, human=True)
		self.playerAlexander.initialize()

		# map
		self.mapModel = MapModelMock(MapSize.duel, TerrainType.grass)

		# game
		self.simulation = GameModel(
			victoryTypes=[VictoryType.domination, VictoryType.cultural, VictoryType.diplomatic],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[self.barbarianPlayer, self.playerTrajan, self.playerAlexander],
			map=self.mapModel
		)
		self.simulation.userInterface = UserInterfaceImpl()

		self.playerTrajan.doFirstContactWith(self.playerAlexander, self.simulation)

	def test_constructor(self):
		# given
		player = Player(LeaderType.alexander, cityState=None, human=False)
		techs = PlayerTechs(player)

		# when - then
		self.assertEqual(techs.numberOfDiscoveredTechs(), 0)
		self.assertEqual(techs.lastScienceEarned(), 1.0)

	def test_eurekaTriggeredFor(self):
		# given
		player = Player(LeaderType.alexander, cityState=None, human=False)
		techs = PlayerTechs(player)

		# when
		triggered = techs.eurekaTriggeredFor(TechType.archery)

		# then
		self.assertFalse(triggered)

	def test_triggerEurekaFor_already_researched(self):
		# given
		techs = PlayerTechs(self.playerTrajan)
		techs.discover(TechType.pottery, self.simulation)

		# when
		triggeredBefore = techs.eurekaTriggeredFor(TechType.pottery)
		techs.triggerEurekaFor(TechType.pottery, self.simulation)

		# then
		triggeredAfter = techs.eurekaTriggeredFor(TechType.pottery)
		self.assertFalse(triggeredBefore)
		self.assertFalse(triggeredAfter)

	def test_triggerEurekaFor_already_triggered(self):
		# given
		techs = PlayerTechs(self.playerTrajan)
		techs.triggerEurekaFor(TechType.pottery, self.simulation)

		# when
		triggeredBefore = techs.eurekaTriggeredFor(TechType.pottery)
		techs.triggerEurekaFor(TechType.pottery, self.simulation)

		# then
		triggeredAfter = techs.eurekaTriggeredFor(TechType.pottery)
		self.assertTrue(triggeredBefore)
		self.assertTrue(triggeredAfter)

	def test_currentScienceProgress(self):
		# given
		techs = PlayerTechs(self.playerTrajan)

		# when
		progressBefore = techs.currentScienceProgress()
		techs.setCurrentTech(TechType.pottery, self.simulation)
		techs.addScience(5)

		# then
		progressAfter = techs.currentScienceProgress()
		self.assertEqual(progressBefore, 0)
		self.assertEqual(progressAfter, 5)

	def test_currentScienceTurnsRemaining(self):
		# given
		techs = PlayerTechs(self.playerTrajan)

		# when - then
		self.assertEqual(techs.currentScienceTurnsRemaining(), 1)

		techs.setCurrentTech(TechType.pottery, self.simulation)
		self.assertEqual(techs.currentScienceTurnsRemaining(), 25)

	def test_setCurrentTech_future(self):
		# given
		techs = PlayerTechs(self.playerTrajan)

		# when - then
		with pytest.raises(Exception):
			techs.setCurrentTech(TechType.futureTech, None)
