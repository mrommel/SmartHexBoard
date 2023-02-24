import json
import random

from django.core.exceptions import BadRequest
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.template import loader
import uuid
from django_q.tasks import async_task

from smarthexboard.map.types import TerrainType, FeatureType
from smarthexboard.models import MapGeneration, MapGenerationState, GameModel, MapModel, Player, LeaderType, \
	HandicapType, MapSize, MapType
from smarthexboard.utils import is_valid_uuid


# ####################################
#
#         pages
#
# ####################################

def index(request):
	template = loader.get_template('index.html')
	context = {
		'navi_home': 'active',
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

	for terrain in TerrainType.list():
		if terrain == TerrainType.land or terrain == TerrainType.sea:
			continue

		terrains[terrain.value] = terrain.textures()[0]

	for feature in FeatureType.list():
		if feature == FeatureType.none:
			continue

		feature_textures = feature.textures()

		if len(feature_textures) > 0:
			features[feature.value] = feature_textures[0]

	template = loader.get_template('styleguide/index.html')
	context = {
		'terrains': terrains,
		'features': features,
	}
	return HttpResponse(template.render(context, request))


# ####################################
#
#     API methods
#
# ####################################

def generate_map(request, map_size: str, map_type: str):
	try:
		size_value = MapSize.from_str(map_size.upper())
	except ValueError as e:
		json_payload = {
			'error': 'invalid arg',
			'field': 'map_size',
			'value': map_size,
			'message': f'Invalid request: not a valid map size: {e}'
		}
		return JsonResponse(json_payload, status=400)

	try:
		type_value = MapType.from_str(map_type.upper())
	except ValueError as e:
		json_payload = {
			'error': 'invalid arg',
			'field': 'map_type',
			'value': map_type,
			'message': f'Invalid request: not a valid map type: {e}'
		}
		return JsonResponse(json_payload, status=400)

	map_uuid = uuid.uuid4()
	async_task("smarthexboard.services.generate_map", map_uuid, size_value, type_value)
	json_payload = {'uuid': map_uuid}
	return JsonResponse(json_payload, status=201)


def generate_status(request, map_uuid):
	if not is_valid_uuid(map_uuid):
		json_payload = {
			'error': 'invalid arg',
			'field': 'map_uuid',
			'value': map_uuid,
			'message': 'Invalid request: not a valid uuid format'
		}
		return JsonResponse(json_payload, status=400)

	map_generation = MapGeneration.objects.filter(uuid=map_uuid).first()
	if map_generation is None:
		json_payload = {'uuid': map_uuid, 'status': f'Cannot find map generation with uuid: {map_uuid}'}
		return JsonResponse(json_payload, status=404)

	json_payload = {'uuid': map_uuid, 'status': MapGenerationState(map_generation.state).label}
	return JsonResponse(json_payload, status=200)


def generated_map(request, map_uuid):
	if not is_valid_uuid(map_uuid):
		json_payload = {'uuid': map_uuid, 'status': 'Invalid request: not a valid uuid format'}
		return JsonResponse(json_payload, status=400)

	map_generation = MapGeneration.objects.filter(uuid=map_uuid).first()
	if map_generation is None:
		json_payload = {'uuid': map_uuid, 'status': f'Cannot find map generated with uuid: {map_uuid}'}
		return JsonResponse(json_payload, status=404)

	current_state = MapGenerationState(map_generation.state)
	if current_state != MapGenerationState.READY:
		json_payload = {'uuid': map_uuid, 'status': f'Map with {map_uuid} is not ready yet: {current_state}'}
		return JsonResponse(json_payload, status=400)

	# convert json string to dict
	json_payload = json.loads(map_generation.map)
	return JsonResponse(json_payload, status=200)


def tech_tree(request, game_uuid, player_id):
	json_payload = {
		# 'uuid': game.uuid,
	}

	return JsonResponse(json_payload, status=200)


def create_game(request, map_uuid, leader, handicap):
	# verify parameters
	if not is_valid_uuid(map_uuid):
		json_payload = {'uuid': map_uuid, 'status': 'Invalid request: not a valid uuid format'}
		return JsonResponse(json_payload, status=400)

	try:
		leader_type = LeaderType.from_str(leader.upper())
	except ValueError as e:
		json_payload = {'leader': leader, 'status': f'Invalid request: not a valid leader name: {e}'}
		return JsonResponse(json_payload, status=400)

	try:
		handicap_type = HandicapType.from_str(handicap.upper())
	except ValueError as e:
		json_payload = {'handicap': handicap, 'status': f'Invalid request: not a valid handicap name: {e}'}
		return JsonResponse(json_payload, status=400)

	# get map generation object
	map_generation = MapGeneration.objects.get(uuid=map_uuid)
	if map_generation is None:
		json_payload = {'uuid': map_uuid, 'status': f'Cannot find map generated with uuid: {map_uuid}'}
		return JsonResponse(json_payload, status=404)

	current_state = MapGenerationState(map_generation.state)
	if current_state != MapGenerationState.READY:
		json_payload = {'uuid': map_uuid, 'status': f'Map with {map_uuid} is not ready yet: {current_state}'}
		return JsonResponse(json_payload, status=400)

	# create map object
	map_model = MapModel(uuid=map_uuid, content=map_generation.map)
	map_model.save()

	# remove map generation object
	map_generation.delete()

	# create game with map
	game = GameModel(uuid=uuid.uuid4(), map=map_model, name='Test game', turn=0, handicap=handicap_type)
	game.save()

	# create players
	map_size = MapSize(map_generation.size)
	num_players = map_size.numOfPlayers()
	leaders = list(filter(lambda x: x != leader_type, LeaderType.values))
	random.shuffle(leaders)

	human_player = Player(leader=leader_type, human=True, game=game)
	human_player.save()

	for _ in range(num_players - 1):
		first_leader = leaders.pop(0)
		player = Player(leader=first_leader, human=False, game=game)
		player.save()

	# serialize game
	json_payload = {
		'game_uuid': game.uuid,
	}
	return JsonResponse(json_payload, status=201)
