import json

from django.core.exceptions import BadRequest
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.template import loader
import uuid
from django_q.tasks import async_task

from smarthexboard.models import MapGeneration, MapGenerationState, GameModel
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
	template = loader.get_template('styleguide/index.html')
	context = {
		'abc': 'def',
	}
	return HttpResponse(template.render(context, request))


# ####################################
#
#     API methods
#
# ####################################

def generate_map(request):
	map_uuid = uuid.uuid4()
	async_task("smarthexboard.services.generate_map", map_uuid)
	json_payload = {'uuid': map_uuid}
	return JsonResponse(json_payload, status=201)


def generate_status(request, map_uuid):
	if not is_valid_uuid(map_uuid):
		json_payload = {'uuid': map_uuid, 'status': 'Invalid request: not a valid uuid format'}
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


def create_game(request, map_uuid, player, difficulty):
	# create map object
	# copy map data into game
	# remove map generation
	# create game object
	#game = GameModel()
	#game.save()

	# serialize game
	json_payload = {
		#'uuid': game.uuid,

	}
	return JsonResponse(json_payload, status=201)
