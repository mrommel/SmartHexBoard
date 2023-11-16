import json
import unittest
from time import sleep
from urllib.parse import urlencode

import pytest

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
		response = client.post('/smarthexboard/create_game', data, content_type="application/x-www-form-urlencoded")
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
		response = client.post('/smarthexboard/create_game', data, content_type="application/x-www-form-urlencoded")
		print(response.content)
		json_object = json.loads(response.content)
		status = json_object['status']
		errors = json_object['errors']

		self.assertEqual(response.status_code, 400)
		self.assertEqual(status, 'Form not valid')
		self.assertEqual(errors, {'leader': ['No matching case for leaderName: "random"']})

	@pytest.mark.django_db
	def test_valid_map_size_generate_map_request(self):
		"""Test that the map generation request (async) is successful with correct map sizes"""
		client = Client()

		response = client.post('/smarthexboard/generate_map/duel/CONTINENTS/')
		json_object = json.loads(response.content)
		map_uuid = json_object['uuid']
		self.assertEqual(response.status_code, 201)
		self.assertEqual(is_valid_uuid(map_uuid), True)

		response = client.post('/smarthexboard/generate_map/DUEL/CONTINENTS/')
		json_object = json.loads(response.content)
		map_uuid = json_object['uuid']
		self.assertEqual(response.status_code, 201)
		self.assertEqual(is_valid_uuid(map_uuid), True)

	@pytest.mark.django_db
	def test_invalid_map_type_generate_map_request(self):
		"""Test that the map generation request (async) fails when map type is wrong"""
		client = Client()

		response = client.post('/smarthexboard/generate_map/DUEL/WRONG/')
		# print(response.content)
		json_object = json.loads(response.content)
		error = json_object['error']
		field = json_object['field']
		value = json_object['value']
		self.assertEqual(response.status_code, 400)
		self.assertEqual(error, 'invalid arg')
		self.assertEqual(field, 'map_type')
		self.assertEqual(value, 'WRONG')

	@pytest.mark.django_db
	def test_valid_map_type_generate_map_request(self):
		"""Test that the map generation request (async) is successful with correct map types"""
		client = Client()

		response = client.post('/smarthexboard/generate_map/DUEL/CONTINENTS/')
		json_object = json.loads(response.content)
		map_uuid = json_object['uuid']
		self.assertEqual(response.status_code, 201)
		self.assertEqual(is_valid_uuid(map_uuid), True)

		response = client.post('/smarthexboard/generate_map/DUEL/continents/')
		json_object = json.loads(response.content)
		map_uuid = json_object['uuid']
		self.assertEqual(response.status_code, 201)
		self.assertEqual(is_valid_uuid(map_uuid), True)

	@pytest.mark.django_db
	def test_generation_status_invalid_uuid(self):
		"""Test that the map generation request status returns error for invalid """
		client = Client()

		response = client.get(f'/smarthexboard/generate_status/123-324/')
		# print(response.content)
		self.assertEqual(response.status_code, 400)

		json_object = json.loads(response.content)
		error = json_object['error']
		field = json_object['field']
		value = json_object['value']
		self.assertEqual(error, 'invalid arg')
		self.assertEqual(field, 'map_uuid')
		self.assertEqual(value, '123-324')


	@pytest.mark.django_db
	def test_map_generation_request(self):
		"""Test that the game generation request (async)"""
		client = Client()

		# 1 - start map creation
		response = client.post('/smarthexboard/generate_map/DUEL/CONTINENTS/')
		# print(response.content)
		self.assertEqual(response.status_code, 201)

		json_object = json.loads(response.content)
		map_uuid = json_object['uuid']
		self.assertEqual(is_valid_uuid(map_uuid), True)

		# fake the async generation - not working with the test currently
		generate_map(map_uuid, MapSizeModel.DUEL, MapTypeModel.CONTINENTS)
		sleep(1)

		# check that there is an entry in the database
		map_generation = MapGenerationData.objects.filter(uuid=map_uuid).first()
		if map_generation is None:
			self.fail()

		# 2 - check status
		testing_count = 0
		testing_status = MapGenerationState.RUNNING
		while testing_status != MapGenerationState.READY and not testing_count > 10:
			response = client.get(f'/smarthexboard/generate_status/{map_uuid}/')
			self.assertEqual(response.status_code, 200)

			json_object = json.loads(response.content)
			generation_map_uuid = json_object['uuid']
			self.assertEqual(is_valid_uuid(generation_map_uuid), True)
			self.assertEqual(generation_map_uuid, map_uuid)

			generation_status = json_object['status'].upper()
			testing_status = MapGenerationState(generation_status[0:2]).value
			print(f'Got status {testing_status} in iteration: {testing_count}')
			testing_count += 1
			sleep(1)

		self.assertEqual(testing_status, MapGenerationState.READY)
		self.assertEqual(testing_count < 10, True)

		# get map
		response = client.get(f'/smarthexboard/generated_map/{map_uuid}/')
		self.assertEqual(response.status_code, 200)

		# create game
		response = client.get(f'/smarthexboard/create_game/{map_uuid}/Alexander/Settler/')
		# print(response.content)
		self.assertEqual(response.status_code, 201)


if __name__ == '__main__':
	unittest.main()
