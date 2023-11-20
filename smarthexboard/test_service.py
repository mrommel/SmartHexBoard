import json
import unittest
from time import sleep, time
from urllib.parse import urlencode

import pytest
from parameterized import parameterized

from smarthexboard.repositories import GameDataRepository
from smarthexboard.smarthexboardlib.serialisation.game import GameModelSchema
from .smarthexboardlib.game.baseTypes import HandicapType
from .smarthexboardlib.game.civilizations import LeaderType
from .smarthexboardlib.map.types import MapSize, MapType

from smarthexboard.models import GameGenerationState, GameGenerationData
from smarthexboard.services import generate_game
from smarthexboard.utils import is_valid_uuid
from django.test import Client


class TestGenerationRequest(unittest.TestCase):

	@pytest.mark.django_db
	def test_completely_invalid_generate_game_request(self):
		"""Test that the map generation request (async) fails when map size is wrong"""
		client = Client()

		data = urlencode({"something": "something"})
		response = client.post('/smarthexboard/game/create', data, content_type="application/x-www-form-urlencoded")
		print(response.content)
		json_object = json.loads(response.content)
		status = json_object['status']
		errors = json_object['errors']

		self.assertEqual(response.status_code, 400)
		self.assertEqual(status, 'Form not valid')
		self.assertEqual(errors, {'handicap': ['This field is required.'], 'leader': ['This field is required.'], 'mapSize': ['This field is required.'], 'mapType': ['This field is required.']})

	@pytest.mark.django_db
	def test_invalid_leader_generate_game_request(self):
		"""Test that the map generation request (async) fails when map size is wrong"""
		client = Client()

		data = urlencode({"leader": "random", 'handicap': 'settler', 'mapSize': 'tiny', 'mapType': 'continents'})
		response = client.post('/smarthexboard/game/create', data, content_type="application/x-www-form-urlencoded")
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
		response = client.post('/smarthexboard/game/create', data, content_type="application/x-www-form-urlencoded")
		# print(response.content)
		json_object = json.loads(response.content)
		status = json_object['status']
		errors = json_object['errors']

		self.assertEqual(response.status_code, 400)
		self.assertEqual(status, 'Form not valid')
		self.assertEqual(errors, {'mapType': ["Cannot map mapType from 'random' to MapType"]})

	@pytest.mark.django_db
	@parameterized.expand([
		["alexander", "settler", "small", "continents"],
		["qin", "prince", "tiny", "earth"],
		["trajan", "king", "duel", "continents"],
	])
	def test_valid_generate_game_request(self, leader, handicap, mapSize, mapType):
		"""Test that the game generation request (async) is successful with correct values"""
		client = Client()

		data = urlencode({'leader': leader, 'handicap': handicap, 'mapSize': mapSize, 'mapType': mapType})
		response = client.post('/smarthexboard/game/create', data, content_type="application/x-www-form-urlencoded")
		# print(response.content)
		json_object = json.loads(response.content)
		game_uuid = json_object['game_uuid']
		self.assertEqual(response.status_code, 201)
		self.assertEqual(is_valid_uuid(game_uuid), True)

	@pytest.mark.django_db
	def test_generation_status_invalid_uuid(self):
		"""Test that the map generation request status returns error for invalid """
		client = Client()

		response = client.get(f'/smarthexboard/game/123-324/create/status')
		# print(response.content)
		self.assertEqual(response.status_code, 400)

		json_object = json.loads(response.content)
		error = json_object['error']
		field = json_object['field']
		value = json_object['value']
		self.assertEqual(error, 'invalid arg')
		self.assertEqual(field, 'game_uuid')
		self.assertEqual(value, '123-324')

	@pytest.mark.django_db
	def test_game_generation_request(self):
		"""Test that the game generation request (async)"""
		client = Client()

		# 1 - start map creation
		data = urlencode({'leader': 'alexander', 'handicap': 'settler', 'mapSize': 'tiny', 'mapType': 'continents'})
		response = client.post('/smarthexboard/game/create', data, content_type="application/x-www-form-urlencoded")
		# print(response.content)
		json_object = json.loads(response.content)
		game_uuid = json_object['game_uuid']
		# print(game_uuid)
		self.assertEqual(response.status_code, 201)
		self.assertEqual(is_valid_uuid(game_uuid), True)

		# fake the async generation - not working with the test currently
		generate_game(game_uuid, LeaderType.alexander, HandicapType.settler, MapSize.tiny, MapType.continents)
		sleep(1)

		# check that there is an entry in the database
		game_generation = GameGenerationData.objects.filter(uuid=game_uuid).first()
		if game_generation is None:
			self.fail()

		# 2 - check status
		testing_count = 0
		testing_status = GameGenerationState.RUNNING
		while testing_status != GameGenerationState.READY and not testing_count > 10:
			response = client.get(f'/smarthexboard/game/{game_uuid}/create/status')
			self.assertEqual(response.status_code, 200)

			json_object = json.loads(response.content)
			generation_map_uuid = json_object['uuid']
			self.assertEqual(is_valid_uuid(generation_map_uuid), True)
			self.assertEqual(generation_map_uuid, game_uuid)

			generation_status = json_object['status'].upper()
			testing_status = GameGenerationState(generation_status[0:2]).value
			# print(f'Got status {testing_status} in iteration: {testing_count}')
			testing_count += 1
			sleep(1)

		self.assertEqual(testing_status, GameGenerationState.READY)
		self.assertEqual(testing_count < 10, True)

		# 3 - get map
		response = client.get(f'/smarthexboard/game/{game_uuid}/map')
		self.assertEqual(response.status_code, 200)

		# 4 - game status
		human_active: bool = False
		iteration: int = 0
		while not human_active and iteration < 20:
			ts = time()
			response = client.get(f'/smarthexboard/game/{game_uuid}/update?timestamp={int(ts * 1000)}')
			self.assertEqual(response.status_code, 200)
			json_object = json.loads(response.content)
			game_uuid_status = json_object['game_uuid']
			current_turn_status = json_object['current_turn']
			human_active = json_object['human_active']
			current_player = json_object['current_player']
			# print(current_player)
			self.assertEqual(game_uuid, game_uuid_status)
			self.assertEqual(current_turn_status, 1)
			iteration += 1
			sleep(1.0)

		self.assertEqual(human_active, True)
		self.assertLess(iteration, 20)

		print(f'--- {iteration} ---')


if __name__ == '__main__':
	unittest.main()
