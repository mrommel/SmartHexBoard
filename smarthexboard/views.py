import json

from django.core.exceptions import BadRequest
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.template import loader
import uuid
from django_q.tasks import async_task

from smarthexboard.models import MapGeneration, MapGenerationState
from smarthexboard.utils import is_valid_uuid


def index(request):
	template = loader.get_template('index.html')
	context = {
		'navi_home': 'active',
	}
	return HttpResponse(template.render(context, request))


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

	json_payload = json.loads(map_generation.map)
	return JsonResponse(json_payload, status=200)


def tests(request):
	template = loader.get_template('tests.html')
	context = {
		'abc': 'def',
		'navi_home': 'active',
	}
	return HttpResponse(template.render(context, request))
