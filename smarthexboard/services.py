from smarthexboard.map.generation import MapOptions, MapGenerator
from smarthexboard.map.types import MapSize, MapType


def generate_map(uuid):
	def callbackFunc(state):
		print(f'Progress: {state.value} - {state.message} - {uuid}')
		# write state to db

	print(f'start creating map: {uuid}')

	options = MapOptions(map_size=MapSize.duel, map_type=MapType.continents)
	generator = MapGenerator(options)

	generator.generate(callbackFunc)

	print(f'map created: {uuid} - can be retrieved')


def generate_status(uuid):
	# read status from db
	pass


def map(uuid):
	# read map from db
	pass
