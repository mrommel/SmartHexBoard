import json
import os
import unittest
from time import sleep, time
from urllib.parse import urlencode

import django
import pytest
from django.test import Client, TestCase
from parameterized import parameterized

from smarthexboard.models import GameGenerationData, GameGenerationState
from smarthexboard.repositories import GameDataRepository
from smarthexboard.services import generate_game
from smarthexboard.smarthexboardlib.game.baseTypes import HandicapType
from smarthexboard.smarthexboardlib.game.civilizations import LeaderType
from smarthexboard.smarthexboardlib.game.game import GameModel
from smarthexboard.smarthexboardlib.game.players import Player
from smarthexboard.smarthexboardlib.game.states.victories import VictoryType
from smarthexboard.smarthexboardlib.game.unitTypes import UnitType
from smarthexboard.smarthexboardlib.game.units import Unit
from smarthexboard.smarthexboardlib.map.base import HexPoint
from smarthexboard.smarthexboardlib.map.types import MapSize, MapType, FeatureType, TerrainType
from smarthexboard.tests.test_utils import MapModelMock

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()


class TestGenerationRequest(TestCase):

	@pytest.mark.django_db
	def test_completely_invalid_generate_game_request(self):
		"""Test that the map generation request (async) fails when map size is wrong"""
		client = Client()

		data = urlencode({"something": "something"})
		response = client.post('/game/create', data, content_type="application/x-www-form-urlencoded")
		if response.status_code != 200:
			print(response.content)

		self.assertEqual(response.status_code, 400)

		json_object = json.loads(response.content)
		status = json_object['status']
		errors = json_object['errors']

		self.assertEqual(status, 'Form not valid')
		self.assertEqual(errors, {'handicap': ['This field is required.'], 'leader': ['This field is required.'], 'mapSize': ['This field is required.'], 'mapType': ['This field is required.']})

	@pytest.mark.django_db
	def test_invalid_leader_generate_game_request(self):
		"""Test that the map generation request (async) fails when map size is wrong"""
		client = Client()

		data = urlencode({"leader": "random", 'handicap': 'settler', 'mapSize': 'tiny', 'mapType': 'continents'})
		response = client.post('/game/create', data, content_type="application/x-www-form-urlencoded")
		# print(response.content)
		json_object = json.loads(response.content)
		status = json_object['status']
		errors = json_object['errors']

		self.assertEqual(response.status_code, 400)
		self.assertEqual(status, 'Form not valid')
		self.assertEqual(errors, {'leader': ["Cannot map leader from 'random' to LeaderType"]})

	@pytest.mark.django_db
	def test_invalid_map_type_generate_map_request(self):
		"""Test that the map generation request (async) fails when map type is wrong"""
		client = Client()

		data = urlencode({'leader': 'trajan', 'handicap': 'settler', 'mapSize': 'tiny', 'mapType': 'random'})
		response = client.post('/game/create', data, content_type="application/x-www-form-urlencoded")
		# print(response.content)
		json_object = json.loads(response.content)
		status = json_object['status']
		errors = json_object['errors']

		self.assertEqual(response.status_code, 400)
		self.assertEqual(status, 'Form not valid')
		self.assertEqual(errors, {'mapType': ["Cannot map mapType from 'random' to MapType"]})

	@pytest.mark.django_db(transaction=True)
	@parameterized.expand([
		["alexander", "settler", "small", "continents"],
		["qin", "prince", "tiny", "earth"],
		["trajan", "king", "duel", "continents"],
	])
	def test_valid_generate_game_request(self, leader, handicap, mapSize, mapType):
		"""Test that the game generation request (async) is successful with correct values"""
		client = Client()

		data = urlencode({'leader': leader, 'handicap': handicap, 'mapSize': mapSize, 'mapType': mapType})
		response = client.post('/game/create', data, content_type="application/x-www-form-urlencoded")
		# print(response.content)
		json_object = json.loads(response.content)
		game_id = json_object['game_id']
		self.assertEqual(response.status_code, 201)

	@pytest.mark.django_db
	def test_generation_status_invalid_id(self):
		"""Test that the map generation request status returns error for invalid id parameter"""
		client = Client()

		response = client.get(f'/game/123-324/create/status')
		# print(response.content)
		self.assertEqual(response.status_code, 400)

		json_object = json.loads(response.content)
		error = json_object['error']
		field = json_object['field']
		value = json_object['value']
		self.assertEqual(error, 'invalid arg')
		self.assertEqual(field, 'game_id')
		self.assertEqual(value, '123-324')

	@pytest.mark.django_db
	def test_game_generation_request(self):
		"""Test that the game generation request (async)"""
		client = Client()

		# 1 - start map creation
		data = urlencode({'leader': 'alexander', 'handicap': 'settler', 'mapSize': 'tiny', 'mapType': 'continents'})
		response = client.post('/game/create', data, content_type="application/x-www-form-urlencoded")
		# print(response.content)
		json_object = json.loads(response.content)
		game_id = json_object['game_id']
		# print(f'game_id: {game_id}')
		self.assertEqual(response.status_code, 201)

		# fake the async generation - not working with the test currently
		game_id = generate_game(LeaderType.alexander, HandicapType.settler, MapSize.tiny, MapType.continents)
		# print(f'game_id: {game_id}')
		sleep(1)

		# check that there is an entry in the database
		game_generation = GameGenerationData.objects.filter(pk=game_id).first()
		if game_generation is None:
			self.fail(f'GameGenerationData not found in db for game_id: {game_id}')

		# 2 - check status
		testing_count = 0
		testing_status = GameGenerationState.RUNNING
		while testing_status != GameGenerationState.READY and testing_count < 10:
			ts = time()
			response = client.get(f'/game/{game_id}/create/status?timestamp={int(ts * 1000)}')
			print(response.content)
			self.assertEqual(response.status_code, 200)

			json_object = json.loads(response.content)
			generation_map_id = json_object['game_id']
			self.assertEqual(generation_map_id, game_id)

			generation_status = json_object['status'].upper()
			testing_status = GameGenerationState(generation_status[0:2]).value
			# print(f'Got status {testing_status} in iteration: {testing_count}')
			testing_count += 1
			sleep(1)

		self.assertEqual(testing_status, GameGenerationState.READY)
		self.assertEqual(testing_count < 10, True)

		# 3 - get map
		response = client.get(f'/game/{game_id}/map')
		if response.status_code != 200:
			print(response.content)
		self.assertEqual(response.status_code, 200)

		# 4 - info
		response = client.get(f'/game/{game_id}/info')
		if response.status_code != 200:
			print(response.content)
		self.assertEqual(response.status_code, 200)

		# 5 - game status
		human_active: bool = False
		iteration: int = 0
		while not human_active and iteration < 20:
			ts = time()
			response = client.get(f'/game/{game_id}/update?timestamp={int(ts * 1000)}')
			self.assertEqual(response.status_code, 200)
			json_object = json.loads(response.content)
			game_id_status = int(json_object['game_id'])
			current_turn_status = json_object['current_turn']
			human_active = json_object['human_active']
			# current_player = json_object['current_player']
			# print(current_player)
			self.assertEqual(game_id, game_id_status)
			self.assertEqual(current_turn_status, 1)
			iteration += 1
			sleep(1.0)

		self.assertEqual(human_active, True)
		self.assertLess(iteration, 20)

		print(f'--- {iteration} turns ---')

		game = GameDataRepository.fetch(game_id)
		self.assertIsNotNone(game)
		humanPlayer = game.humanPlayer()
		self.assertIsNotNone(humanPlayer)
		humanTiles: int = game.numberOfDiscoveredTilesOf(humanPlayer)
		self.assertLess(humanTiles, MapSize.tiny.numberOfTiles())
		self.assertGreater(humanTiles, 0)


class TestGamePlayRequest(unittest.TestCase):
	def setUp(self):
		# prepare game
		grid = MapModelMock(10, 10, TerrainType.grass)
		grid.modifyFeatureAt(HexPoint(1, 2), FeatureType.mountains)  # put a mountain into the path

		self.player = Player(LeaderType.alexander, human=False)
		humanPlayer = Player(LeaderType.barbarossa, human=True)
		self.simulation = GameModel(
			victoryTypes=[VictoryType.science],
			handicap=HandicapType.settler,
			turnsElapsed=0,
			players=[self.player, humanPlayer],
			map=grid
		)
		grid.discover(self.player, self.simulation)

		# add AI unit
		scout = Unit(location=HexPoint(1, 1), unitType=UnitType.scout, player=self.player)
		self.simulation.addUnit(scout)

		# add human unit
		self.warrior = Unit(location=HexPoint(2, 2), unitType=UnitType.warrior, player=humanPlayer)
		self.simulation.addUnit(self.warrior)

		self.game_id = GameDataRepository.store(None, self.simulation)

	@pytest.mark.django_db
	def test_unit_move_request_no_game(self):
		"""Test that the unit move"""
		client = Client()
		another_id = 42
		data = {'game_id': another_id, 'unit_type': 'combat', 'old_location': '0,0', 'new_location': '1,1'}
		response = client.post(f'/game/move_unit', data)

		# if response.status_code != 200:
		# 	print(response.status_code)
		# 	print(response.content)

		json_object = json.loads(response.content)
		errors = json_object['errors']
		status = json_object['status']

		self.assertEqual(response.status_code, 404)
		self.assertEqual(status, 'Cannot move unit.')
		self.assertEqual(errors, [f'Game with {another_id} not found in db or cache.'])

	@pytest.mark.django_db
	def test_unit_move_request_no_unit(self):
		"""Test that the unit move"""
		client = Client()
		data = {'game_id': self.game_id, 'unit_type': 'combat', 'old_location': '0,0', 'new_location': '1,1'}
		response = client.post(f'/game/move_unit', data)

		# if response.status_code != 200:
		# 	print(response.status_code)
		# 	print(response.content)

		json_object = json.loads(response.content)
		errors = json_object['errors']
		status = json_object['status']

		self.assertEqual(response.status_code, 404)
		self.assertEqual(status, 'Cannot move unit.')
		self.assertEqual(errors, ['Could find UnitMapType.combat unit at HexPoint(0, 0).'])

	@pytest.mark.django_db
	def test_unit_move_request_invalid_unit_type(self):
		"""Test that the unit move"""
		client = Client()
		data = {'game_id': self.game_id, 'unit_type': 'clown', 'old_location': '0,0', 'new_location': '1,1'}
		response = client.post(f'/game/move_unit', data)

		# if response.status_code != 200:
		# 	print(response.status_code)
		# 	print(response.content)

		json_object = json.loads(response.content)
		errors = json_object['errors']
		status = json_object['status']

		self.assertEqual(response.status_code, 400)
		self.assertEqual(status, 'Cannot move unit.')
		self.assertEqual(errors, ['Could not parse unit map type from clown.'])

	@pytest.mark.django_db
	def test_unit_move_request_invalid_start_location(self):
		"""Test that the unit move"""
		client = Client()
		data = {'game_id': self.game_id, 'unit_type': 'combat', 'old_location': '0,_', 'new_location': '1,1'}
		response = client.post(f'/game/move_unit', data)

		# if response.status_code != 200:
		# 	print(response.status_code)
		# 	print(response.content)

		json_object = json.loads(response.content)
		errors = json_object['errors']
		status = json_object['status']

		self.assertEqual(response.status_code, 400)
		self.assertEqual(status, 'Cannot move unit.')
		self.assertEqual(errors, ['Could not parse location from 0,_.'])

	@pytest.mark.django_db
	def test_unit_move_request_invalid_end_location(self):
		"""Test that the unit move"""
		client = Client()
		data = {'game_id': self.game_id, 'unit_type': 'combat', 'old_location': '0,0', 'new_location': '123'}
		response = client.post(f'/game/move_unit', data)

		# if response.status_code != 400:
		#	print(response.status_code)
		#	print(response.content)

		json_object = json.loads(response.content)
		errors = json_object['errors']
		status = json_object['status']

		self.assertEqual(response.status_code, 400)
		self.assertEqual(status, 'Cannot move unit.')
		self.assertEqual(errors, ['Could not parse location from 123.'])

	@pytest.mark.django_db
	def test_unit_move_request_not_human(self):
		"""Test that the unit move"""
		client = Client()
		data = {'game_id': self.game_id, 'unit_type': 'combat', 'old_location': '1,1', 'new_location': '1,2'}
		response = client.post(f'/game/move_unit', data)

		# if response.status_code != 200:
		# 	print(response.status_code)
		# 	print(response.content)

		json_object = json.loads(response.content)
		errors = json_object['errors']
		status = json_object['status']

		self.assertEqual(response.status_code, 400)
		self.assertEqual(status, 'Cannot move unit.')
		self.assertEqual(errors, ['Cannot move units from another player. The unit you are trying to move is from TXT_KEY_LEADER_ALEXANDER.'])

	@pytest.mark.django_db
	def test_unit_move_request_no_moves_left(self):
		"""Test that the unit move"""
		self.warrior.finishMoves()
		GameDataRepository.store(self.game_id, self.simulation)

		client = Client()
		data = {'game_id': self.game_id, 'unit_type': 'combat', 'old_location': '2,2', 'new_location': '1,2'}
		response = client.post(f'/game/move_unit', data)

		# if response.status_code != 200:
		# 	print(response.status_code)
		# 	print(response.content)

		json_object = json.loads(response.content)
		errors = json_object['errors']
		status = json_object['status']

		self.assertEqual(response.status_code, 400)
		self.assertEqual(status, 'Cannot move unit.')
		# print(errors)
		self.assertEqual(errors, ['Unit Unit(HexPoint(2, 2), UnitType.warrior, TXT_KEY_LEADER_BARBAROSSA, 1 exp) could not be moved from HexPoint(2, 2) to HexPoint(1, 2).'])

	@pytest.mark.django_db
	def test_unit_move_request_success(self):
		"""Test that the unit move"""
		client = Client()
		data = {'game_id': self.game_id, 'unit_type': 'combat', 'old_location': '2,2', 'new_location': '1,2'}
		response = client.post(f'/game/move_unit', data)

		# if response.status_code != 200:
		# 	print(response.status_code)
		# 	print(response.content)

		json_object = json.loads(response.content)
		game_id = json_object['game_id']

		self.assertEqual(response.status_code, 200)
		self.assertNotIn('errors', json_object)
		self.assertNotIn('status', json_object)
		self.assertEqual(game_id, self.game_id)


if __name__ == '__main__':
	unittest.main()
