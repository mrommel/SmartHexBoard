import os
import unittest

from smarthexboard.smarthexboardlib.game.baseTypes import HandicapType
from smarthexboard.smarthexboardlib.game.civilizations import LeaderType
from smarthexboard.smarthexboardlib.game.generation import GameGenerator, UserInterfaceImpl
from smarthexboard.smarthexboardlib.game.governments import GovernmentType
from smarthexboard.smarthexboardlib.game.states.victories import VictoryType
from smarthexboard.smarthexboardlib.map.base import HexPoint
from smarthexboard.smarthexboardlib.map.evaluators import MapAnalyzer
from smarthexboard.smarthexboardlib.map.generation import MapOptions, MapGenerator
from smarthexboard.smarthexboardlib.map.map import Tile, MapModel
from smarthexboard.smarthexboardlib.map.types import TerrainType, MapSize, FeatureType, MapType
from smarthexboard.smarthexboardlib.serialisation.game import GameModelSchema
from smarthexboard.smarthexboardlib.serialisation.map import TileSchema, MapModelSchema
from smarthexboard.tests.test_utils import MapModelMock


class TestSerialisation(unittest.TestCase):
	def setUp(self):
		self.last_state_value = 0.0

	def test_tile_serialization(self):
		tile = Tile(HexPoint(1, 13), TerrainType.desert)
		json_str = TileSchema().dumps(tile)

		self.assertGreater(len(json_str), 0)

		obj = TileSchema().loads(json_str)
		# obj = Tile(obj_dict)

		self.assertEqual(obj.point.x, tile.point.x)
		self.assertEqual(obj.point.y, tile.point.y)
		self.assertEqual(obj.terrain(), tile.terrain())
		self.assertEqual(obj.feature(), tile.feature())

	def test_map_serialization(self):
		mapModel = MapModelMock(MapSize.duel, TerrainType.ocean)
		mapModel.modifyTerrainAt(HexPoint(2, 3), TerrainType.desert)
		mapModel.modifyFeatureAt(HexPoint(2, 3), FeatureType.oasis)

		json_str = MapModelSchema().dumps(mapModel)

		self.assertGreater(len(json_str), 0)

		obj_dict = MapModelSchema().loads(json_str)
		obj = MapModel(obj_dict)

		self.assertEqual(obj.width, mapModel.width)
		self.assertEqual(obj.height, mapModel.height)
		self.assertEqual(obj.tileAt(HexPoint(0, 0)).terrain(), mapModel.tileAt(HexPoint(0, 0)).terrain())

		self.assertEqual(obj.tileAt(HexPoint(2, 3)).terrain(), mapModel.tileAt(HexPoint(2, 3)).terrain())
		self.assertEqual(obj.tileAt(HexPoint(2, 3)).feature(), mapModel.tileAt(HexPoint(2, 3)).feature())

	def test_map_deserialization_from_file(self):
		path = f'{os.getcwd()}/game/tests/files/duel.map'
		if os.path.exists(f'{os.getcwd()}/files/duel.map'):
			path = f'{os.getcwd()}/files/duel.map'

		with open(path, "r") as file:
			fileContent = file.read()

			obj_dict = MapModelSchema().loads(fileContent)
			obj = MapModel(obj_dict)

			self.assertEqual(obj.width, 32)
			self.assertEqual(obj.height, 22)

			self.assertGreater(len(obj.startLocations), 0)
			self.assertGreater(len(obj.cityStateStartLocations), 0)

			self.assertGreater(len(obj.continents), 0)
			self.assertGreater(len(obj.oceans), 0)
			self.assertGreater(len(obj.areas), 0)

	def _test_generate_testfile(self):
		def _callback(state):
			# print(f'Progress: {state.value} - {state.message} ', flush=True)
			self.last_state_value = state.value

		options = MapOptions(mapSize=MapSize.duel, mapType=MapType.continents, leader=LeaderType.trajan)
		generator = MapGenerator(options)

		mapModel = generator.generate(_callback)

		analyzer = MapAnalyzer(mapModel)
		analyzer.analyze()

		json_str = MapModelSchema().dumps(mapModel)

		with open('duel.map', "w") as file:
			file.write(json_str)

	def test_game_serialization(self):
		def callbackFunc(state):
			print(f'Progress: {state.value} - {state.message}')

		options = MapOptions(MapSize.duel, MapType.continents, LeaderType.qin)
		generator = MapGenerator(options)

		mapModel = generator.generate(callbackFunc)

		gameGenerator = GameGenerator()
		gameModel = gameGenerator.generate(mapModel, HandicapType.king)

		humanPlayer = gameModel.humanPlayer()
		self.assertIsNotNone(humanPlayer)

		gameModel.userInterface = UserInterfaceImpl()
		# gameModel.update()

		# add additional data
		self.assertEqual(humanPlayer.government.currentGovernment(), GovernmentType.chiefdom)
		# print(humanPlayer.government.possiblePolicyCards())

		json_str = GameModelSchema().dumps(gameModel)
		self.assertGreater(len(json_str), 0)

		obj = GameModelSchema().loads(json_str)
		# obj = GameModel(obj_dict)
		obj.userInterface = UserInterfaceImpl()
		# print(json_str)
		self.assertListEqual(obj.victoryTypes, [VictoryType.science, VictoryType.cultural, VictoryType.conquest, VictoryType.domination, VictoryType.religious, VictoryType.diplomatic, VictoryType.score])
		self.assertEqual(obj.handicap, HandicapType.king)
		self.assertEqual(obj.currentTurn, 0)
		# self.assertListEqual(obj.players, [barbarianPlayer, playerVictoria, humanPlayer])
		self.assertEqual(obj._map.width, mapModel.width)
		self.assertEqual(obj._map.height, mapModel.height)

		# test if both serialisations are equal
		# json_str2 = GameModelSchema().dumps(obj)
		# self.assertEqual(json_str, json_str2)

		obj.update()
