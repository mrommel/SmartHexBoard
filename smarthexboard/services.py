import json

from smarthexboardlib.game.civilizations import LeaderType
from smarthexboardlib.map.generation import MapOptions, MapGenerator
from smarthexboardlib.map.types import MapSize, MapType

from smarthexboard.models import MapGenerationData, MapGenerationState


def generate_map(uuid, map_size, map_type):
	def callbackFunc(state):
		print(f'Progress: {state.value} - {state.message} - {uuid}')
		# write state to db
		map_generation_callback_obj = MapGenerationData.objects.filter(uuid=uuid).first()
		map_generation_callback_obj.state = MapGenerationState.RUNNING
		map_generation_callback_obj.save()
		print(f'saved state: MapGenerationState.RUNNING')

	print(f'start creating map: {uuid}')
	map_generation_obj = MapGenerationData(uuid=uuid, map='', size=map_size, state=MapGenerationState.OPEN)
	map_generation_obj.save()

	mapSize: MapSize = MapSize.fromName(map_size)
	mapType: MapType = MapType.fromName(map_type)

	options = MapOptions(mapSize=mapSize, mapType=mapType, leader=LeaderType.alexander)
	generator = MapGenerator(options)

	grid = generator.generate(callbackFunc)

	map_generation_final_obj = MapGenerationData.objects.filter(uuid=uuid).first()
	map_generation_final_obj.map = str(json.dumps(grid.to_dict()))
	map_generation_final_obj.state = MapGenerationState.READY
	map_generation_final_obj.save()

	print(f'map created: {uuid} - can be retrieved')
