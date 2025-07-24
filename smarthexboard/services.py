from smarthexboard.models import GameGenerationData, GameGenerationState
from smarthexboard.smarthexboardlib.game.baseTypes import HandicapType
from smarthexboard.smarthexboardlib.game.civilizations import LeaderType
from smarthexboard.smarthexboardlib.game.generation import GameGenerator, UserInterfaceImpl
from smarthexboard.smarthexboardlib.map.generation import MapOptions, MapGenerator
from smarthexboard.smarthexboardlib.map.types import MapSize, MapType
from smarthexboard.smarthexboardlib.serialisation.game import GameModelSchema


def generate_game(game_id: int, leader: LeaderType, handicap: HandicapType, mapSize: MapSize, mapType: MapType):
	def callbackFunc(state):
		print(f'Progress: {state.value} - {state.message} - {game_id}')
		# write state to db
		map_generation_callback_obj = GameGenerationData.objects.filter(id=game_id).first()
		map_generation_callback_obj.state = GameGenerationState.RUNNING
		map_generation_callback_obj.progress = state.value
		map_generation_callback_obj.save()
		print(f'saved state: MapGenerationState.RUNNING')

	print(f'start creating map: {game_id}')
	game_generation_obj = GameGenerationData(id=game_id, game='', state=GameGenerationState.OPEN, progress=0.0)
	game_generation_obj.save()

	options = MapOptions(mapSize=mapSize, mapType=mapType, leader=leader)
	generator = MapGenerator(options)

	mapModel = generator.generate(callbackFunc)

	gameGenerator = GameGenerator()
	gameModel = gameGenerator.generate(mapModel, handicap)

	# add UI
	gameModel.userInterface = UserInterfaceImpl()

	game_generation_final_obj = GameGenerationData.objects.filter(id=game_id).first()
	game_generation_final_obj.game = GameModelSchema().dumps(gameModel)
	game_generation_final_obj.state = GameGenerationState.READY
	game_generation_final_obj.progress = 1.0
	game_generation_final_obj.save()

	print(f'game created: {game_id} - can be retrieved')
