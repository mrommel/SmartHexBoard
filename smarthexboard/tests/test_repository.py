import os
import random

import django
import pytest
from django.test import TestCase

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from smarthexboard.repositories import GameDataRepository
from smarthexboard.smarthexboardlib.game.baseTypes import HandicapType
from smarthexboard.smarthexboardlib.game.cityStates import CityStateType
from smarthexboard.smarthexboardlib.game.civilizations import LeaderType
from smarthexboard.smarthexboardlib.game.game import GameModel
from smarthexboard.smarthexboardlib.game.generation import UserInterfaceImpl
from smarthexboard.smarthexboardlib.game.players import Player
from smarthexboard.smarthexboardlib.game.states.victories import VictoryType
from smarthexboard.tests.test_utils import MapModelMock


class TestRepository(TestCase):
	def setUp(self) -> None:
		self.mapModel = MapModelMock.duelMap()

		# players
		self.playerBarbarian = Player(LeaderType.barbar, human=False)
		self.playerBarbarian.initialize()

		self.seoulCityState = Player(LeaderType.cityState, cityState=CityStateType.seoul, human=False)
		self.seoulCityState.initialize()

		self.playerAlexander = Player(LeaderType.alexander, human=False)
		self.playerAlexander.initialize()

		self.playerTrajan = Player(LeaderType.trajan, human=True)
		self.playerTrajan.initialize()

		self.simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[self.playerBarbarian, self.seoulCityState, self.playerAlexander, self.playerTrajan],
			map=self.mapModel
		)

		# add UI
		self.simulation.userInterface = UserInterfaceImpl()

	@pytest.mark.django_db
	def test_not_in_cache_and_db(self):
		game_id = f'{random.randint(1, 10000)}'
		in_db = GameDataRepository._inDB(game_id)
		self.assertFalse(in_db, "Game model should not be in database")

		in_cache = GameDataRepository._inCache(game_id)
		self.assertFalse(in_cache, "Game model should not be in cache")

	@pytest.mark.django_db
	def test_in_cache_and_db(self):
		# Store to database and cache
		game_id = GameDataRepository._storeToDatabase(None, self.simulation)
		GameDataRepository._storeToCache(game_id, self.simulation)

		in_db = GameDataRepository._inDB(game_id)
		self.assertTrue(in_db, "Game model should be in database after storing")

		in_cache = GameDataRepository._inCache(game_id)
		self.assertTrue(in_cache, "Game model should be in cache after storing")
