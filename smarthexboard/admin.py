"""admin module description"""
from django.contrib import admin

from smarthexboard.models import GameGenerationData

# Register your models here.
admin.site.register(GameGenerationData)
