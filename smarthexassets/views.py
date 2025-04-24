from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader

from setup.settings import DEBUG
from smarthexassets.models import Asset


def dashboard(request):
	assets = Asset.objects.all()
	num_assets = Asset.objects.all().count()

	template = loader.get_template('dashboard.html')
	context = {
		'navi_home': 'active',
		'debug': DEBUG,
		#
		'num_assets': num_assets,
		#
		'assets': assets,
	}
	return HttpResponse(template.render(context, request))


def render_asset(request, asset_id: str):
	asset = Asset.objects.get(id=asset_id)
	image = asset.render()

	return HttpResponse(image.tobytes(), content_type='image/png')
