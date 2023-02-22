import json
import unittest
from time import sleep

import pytest

from smarthexboard.models import MapGenerationState, MapGeneration, MapSize, MapType
from smarthexboard.services import generate_map
from smarthexboard.utils import is_valid_uuid
from django.test import Client


class TestMapGenerationRequest(unittest.TestCase):
	@pytest.mark.django_db
	def test_map_generation_request(self):
		"""Test that the map generation request (async)"""
		client = Client()

		# 1 - start map creation
		response = client.post('/smarthexboard/generate_map/DUEL/CONTINENTS/')
		# print(response.content)
		self.assertEqual(response.status_code, 201)

		json_object = json.loads(response.content)
		map_uuid = json_object['uuid']
		self.assertEqual(is_valid_uuid(map_uuid), True)

		# fake the async generation - not working with the test currently
		generate_map(map_uuid, MapSize.DUEL, MapType.CONTINENTS)
		sleep(1)

		# check that there is an entry in the database
		map_generation = MapGeneration.objects.filter(uuid=map_uuid).first()
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


if __name__ == '__main__':
	unittest.main()
