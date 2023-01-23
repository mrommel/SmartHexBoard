import json
import unittest

from smarthexboard.utils import is_valid_uuid
from django.test import Client


class TestMapGenerationRequest(unittest.TestCase):
	def test_generation_request(self):
		"""Test that the map generation request (async)"""
		client = Client()
		response = client.post('/smarthexboard/generate_map')
		self.assertEqual(response.status_code, 201)

		json_object = json.loads(response.content)
		map_uuid = json_object['uuid']
		self.assertEqual(is_valid_uuid(map_uuid), True)


if __name__ == '__main__':
	unittest.main()
