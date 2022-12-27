from django.http import HttpResponse
from django.template import loader


def index(request):
    template = loader.get_template('index.html')
    context = {
        'abc': 'def',
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
