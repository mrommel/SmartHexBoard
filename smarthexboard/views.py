import json
import random
import uuid

from django.http import HttpResponse, JsonResponse
from django.template import loader
from django_q.tasks import async_task
from smarthexboardlib.game.baseTypes import HandicapType
from smarthexboardlib.game.civilizations import LeaderType
from smarthexboardlib.game.generation import GameGenerator, UserInterfaceImpl
from smarthexboardlib.map.types import TerrainType, FeatureType, ResourceType, MapType, MapSize

from setup.settings import DEBUG
from smarthexboard.forms import CreateGameForm
from smarthexboard.models import GameGenerationData, GameGenerationState
from smarthexboard.utils import is_valid_uuid


# ####################################
#
#         pages
#
# ####################################

def index(request):
	leader_selection = []
	for leader in list(LeaderType):
		if leader == LeaderType.none:
			continue

		if leader == LeaderType.barbar:
			continue

		if leader == LeaderType.freeCities:
			continue

		if leader == LeaderType.cityState:
			continue

		leader_selection.append((leader.value, f'{leader.title()} ({leader.civilization().name()})'))

	difficulty_selection = []
	for handicap in list(HandicapType):
		difficulty_selection.append((str(handicap), handicap.title()))

	map_type_selection = []
	for mapType in list(MapType):
		map_type_selection.append((mapType.value, mapType.name()))

	map_size_selection = []
	for mapSize in list(MapSize):
		map_size_selection.append((mapSize.value, mapSize.name()))

	template = loader.get_template('index.html')
	context = {
		'navi_home': 'active',
		'debug': DEBUG,
		# create game data
		'leader_selection': leader_selection,
		'difficulty_selection': difficulty_selection,
		'map_type_selection': map_type_selection,
		'map_size_selection': map_size_selection,
	}
	return HttpResponse(template.render(context, request))


def tests(request):
	template = loader.get_template('tests.html')
	context = {
		'abc': 'def',
		'navi_home': 'active',
	}
	return HttpResponse(template.render(context, request))


def styleguide(request):
	terrains = dict()
	features = dict()
	resources = dict()

	for terrain in list(TerrainType):
		if terrain == TerrainType.land or terrain == TerrainType.sea:
			continue

		terrains[terrain.value] = terrain.textures()[0]

	for feature in list(FeatureType):
		if feature == FeatureType.none:
			continue

		feature_textures = feature.textures()

		if len(feature_textures) > 0:
			features[feature.value] = feature_textures[0]

	for resource in list(ResourceType):
		resources[resource.value] = resource.texture()

	template = loader.get_template('styleguide/index.html')
	context = {
		'terrains': terrains,
		'features': features,
		'resources': resources,
	}
	return HttpResponse(template.render(context, request))


# ####################################
#
#     API methods
#
# ####################################


def create_game(request):
	# If this is a POST request then process the Form data
	if request.method == 'POST':

		# Create a form instance and populate it with data from the request (binding):
		form = CreateGameForm(request.POST)

		# Check if the form is valid:
		if form.is_valid():
			game_uuid = uuid.uuid4()
			leader = LeaderType.fromName(form.cleaned_data["leader"])
			handicap = HandicapType.fromName(form.cleaned_data["handicap"])
			mapSize = MapSize.fromName(form.cleaned_data["mapSize"])
			mapType = MapType.fromName(form.cleaned_data["mapType"])

			print(f'generate_game({game_uuid}, {leader}, {handicap}, {mapSize}, {mapType})')
			async_task("smarthexboard.services.generate_game", game_uuid, leader, handicap, mapSize, mapType)

			json_payload = {'status': 'Success'}
			return JsonResponse(json_payload, status=201)
		else:
			# print(form.errors)
			json_payload = {'status': 'Form not valid', 'errors': form.errors}
			return JsonResponse(json_payload, status=400)
	else:
		json_payload = {'status': f'Invalid method {request.method}'}
		return JsonResponse(json_payload, status=400)


def generate_status(request, game_uuid):
	if not is_valid_uuid(game_uuid):
		json_payload = {
			'error': 'invalid arg',
			'field': 'game_uuid',
			'value': game_uuid,
			'message': 'Invalid request: not a valid uuid format'
		}
		return JsonResponse(json_payload, status=400)

	game_generation = GameGenerationData.objects.filter(uuid=game_uuid).first()
	if game_generation is None:
		json_payload = {'uuid': game_uuid, 'status': f'Cannot find game generation with uuid: {game_uuid}'}
		return JsonResponse(json_payload, status=404)

	json_payload = {
		'uuid': game_uuid,
		'status': GameGenerationState(game_generation.state).label,
		'progress': game_generation.progress
	}
	return JsonResponse(json_payload, status=200)


def generated_map(request, game_uuid):
	if not is_valid_uuid(game_uuid):
		json_payload = {'uuid': game_uuid, 'status': 'Invalid request: not a valid uuid format'}
		return JsonResponse(json_payload, status=400)

	game_generation = GameGenerationData.objects.filter(uuid=game_uuid).first()
	if game_generation is None:
		json_payload = {'uuid': game_uuid, 'status': f'Cannot find game generated with uuid: {game_uuid}'}
		return JsonResponse(json_payload, status=404)

	current_state = GameGenerationState(game_generation.state)
	if current_state != GameGenerationState.READY:
		json_payload = {'uuid': game_uuid, 'status': f'Game with {game_uuid} is not ready yet: {current_state}'}
		return JsonResponse(json_payload, status=400)

	# convert json string to dict
	json_payload = json.loads(game_generation.map)
	return JsonResponse(json_payload, status=200)


	# verify parameters
	# if not is_valid_uuid(map_uuid):
	# 	json_payload = {'uuid': map_uuid, 'status': 'Invalid request: not a valid uuid format'}
	# 	return JsonResponse(json_payload, status=400)

	# try:
	# 	leader_type = LeaderTypeModel.from_str(leader.upper())
	# except ValueError as e:
	# 	json_payload = {'leader': leader, 'status': f'Invalid request: not a valid leader name: {e}'}
	# 	return JsonResponse(json_payload, status=400)
	#
	# try:
	# 	handicap_type = HandicapTypeModel.from_str(handicap.upper())
	# except ValueError as e:
	# 	json_payload = {'handicap': handicap, 'status': f'Invalid request: not a valid handicap name: {e}'}
	# 	return JsonResponse(json_payload, status=400)

	# get map generation object
	# map_generation = MapGenerationData.objects.get(uuid=map_uuid)
	# if map_generation is None:
	# 	json_payload = {'uuid': map_uuid, 'status': f'Cannot find map generated with uuid: {map_uuid}'}
	# 	return JsonResponse(json_payload, status=404)
	#
	# current_state = MapGenerationState(map_generation.state)
	# if current_state != MapGenerationState.READY:
	# 	json_payload = {'uuid': map_uuid, 'status': f'Map with {map_uuid} is not ready yet: {current_state}'}
	# 	return JsonResponse(json_payload, status=400)
	#
	# # create map object
	# map_model = MapDataModel(uuid=map_uuid, content=map_generation.map)
	# map_model.save()

	# remove map generation object
	# map_generation.delete()
	#
	# gameGenerator = GameGenerator()
	# simulation = gameGenerator.generate(map_generation.map, HandicapType.settler)
	#
	# # add UI
	# simulation.userInterface = UserInterfaceImpl()
	#
	# # create game with map
	# simulation_content = str(json.dumps(simulation))
	# game = GameDataModel(uuid=uuid.uuid4(), content=simulation_content)
	# game.save()

	# creat

	# serialize game
	# json_payload = {
	# 	'game_uuid': game.uuid,
	# }
	# return JsonResponse(json_payload, status=201)


def game_turn(request, game_uuid):
	json_payload = {
		'game_uuid': game_uuid,
	}

	return JsonResponse(json_payload, status=200)
