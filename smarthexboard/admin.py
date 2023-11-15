"""admin module description"""
from django.contrib import admin

from smarthexboard.models import GameGenerationData, GameDataModel

# Register your models here.
admin.site.register(GameGenerationData)
admin.site.register(GameDataModel)
