import json

from smarthexboardlib.game.baseTypes import HandicapType
from smarthexboardlib.game.civilizations import LeaderType
from smarthexboardlib.game.generation import GameGenerator, UserInterfaceImpl
from smarthexboardlib.map.generation import MapOptions, MapGenerator
from smarthexboardlib.map.types import MapSize, MapType
from smarthexboardlib.serialisation.game import GameModelSchema

from smarthexboard.models import GameGenerationData, GameGenerationState


def generate_game(uuid, leader: LeaderType, handicap: HandicapType, mapSize: MapSize, mapType: MapType):
	def callbackFunc(state):
		print(f'Progress: {state.value} - {state.message} - {uuid}')
		# write state to db
		map_generation_callback_obj = GameGenerationData.objects.filter(uuid=uuid).first()
		map_generation_callback_obj.state = GameGenerationState.RUNNING
		map_generation_callback_obj.progress = state.value
		map_generation_callback_obj.save()
		print(f'saved state: MapGenerationState.RUNNING')

	print(f'start creating map: {uuid}')
	game_generation_obj = GameGenerationData(uuid=uuid, game='', state=GameGenerationState.OPEN, progress=0.0)
	game_generation_obj.save()

	options = MapOptions(mapSize=mapSize, mapType=mapType, leader=leader)
	generator = MapGenerator(options)

	mapModel = generator.generate(callbackFunc)

	gameGenerator = GameGenerator()
	gameModel = gameGenerator.generate(mapModel, handicap)

	# add UI
	gameModel.userInterface = UserInterfaceImpl()

	game_generation_final_obj = GameGenerationData.objects.filter(uuid=uuid).first()
	game_generation_final_obj.game = GameModelSchema().dumps(gameModel)
	game_generation_final_obj.state = GameGenerationState.READY
	game_generation_final_obj.progress = 1.0
	game_generation_final_obj.save()

	print(f'game created: {uuid} - can be retrieved')
