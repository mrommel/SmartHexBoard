import json

from smarthexboard.map.generation import MapOptions, MapGenerator
from smarthexboard.map.types import MapSize, MapType
from smarthexboard.models import MapGeneration, MapGenerationState


def generate_map(uuid):
	def callbackFunc(state):
		print(f'Progress: {state.value} - {state.message} - {uuid}')
		# write state to db
		map_generation_callback_obj = MapGeneration.objects.filter(uuid=uuid).first()
		map_generation_callback_obj.state = MapGenerationState.RUNNING
		map_generation_callback_obj.save()
		print(f'saved state: MapGenerationState.RUNNING')

	print(f'start creating map: {uuid}')
	map_generation_obj = MapGeneration(uuid=uuid, map='', state=MapGenerationState.OPEN)
	map_generation_obj.save()

	options = MapOptions(map_size=MapSize.duel, map_type=MapType.continents)
	generator = MapGenerator(options)

	grid = generator.generate(callbackFunc)

	map_generation_final_obj = MapGeneration.objects.filter(uuid=uuid).first()
	map_generation_final_obj.map = str(json.dumps(grid.to_dict()))
	map_generation_final_obj.state = MapGenerationState.READY
	map_generation_final_obj.save()

	print(f'map created: {uuid} - can be retrieved')
