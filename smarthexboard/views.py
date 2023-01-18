from django.http import HttpResponse, JsonResponse
from django.template import loader

from smarthexboard.map.generation import MapOptions, MapGenerator
from smarthexboard.map.types import MapSize, MapType


def index(request):
    template = loader.get_template('index.html')
    context = {
        'abc': 'def',
        'navi_home': 'active',
    }
    return HttpResponse(template.render(context, request))


def callbackFunc(state):
    print(f'Progress: {state.value} - {state.message}')

def generate(request):

    options = MapOptions(map_size=MapSize.duel, map_type=MapType.continents)
    generator = MapGenerator(options)

    map = generator.generate(callbackFunc)

    context = {
        'map': map.to_dict()
    }
    return JsonResponse(context)


def tests(request):
    template = loader.get_template('tests.html')
    context = {
        'abc': 'def',
        'navi_home': 'active',
    }
    return HttpResponse(template.render(context, request))
