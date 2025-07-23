"""admin module description"""
from django.contrib import admin

from smarthexboard.models import GameGenerationData, GameData

# Register your models here.
admin.site.register(GameGenerationData)
admin.site.register(GameData)
