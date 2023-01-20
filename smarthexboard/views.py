from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.template import loader
import uuid
from django_q.tasks import async_task

from smarthexboard.models import MapGeneration, MapGenerationState


def index(request):
	template = loader.get_template('index.html')
	context = {
		'abc': 'def',
		'navi_home': 'active',
	}
	return HttpResponse(template.render(context, request))


def generate_map(request):
	map_uuid = uuid.uuid4()
	async_task("smarthexboard.services.generate_map", map_uuid)
	json_payload = {'uuid': map_uuid}
	return JsonResponse(json_payload, status=201)


def generate_status(request, map_uuid):
	map_generation = get_object_or_404(MapGeneration, uuid=map_uuid)
	json_payload = {'uuid': map_uuid, 'status': MapGenerationState(map_generation.state).label}
	return JsonResponse(json_payload, status=200)


def tests(request):
	template = loader.get_template('tests.html')
	context = {
		'abc': 'def',
		'navi_home': 'active',
	}
	return HttpResponse(template.render(context, request))
