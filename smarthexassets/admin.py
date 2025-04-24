from django.contrib import admin

from smarthexassets.admin_forms import ObjectModelAdmin, AssetModelAdmin
from smarthexassets.models import Asset, Object

# Register your models here.
admin.site.register(Asset, AssetModelAdmin)
admin.site.register(Object, ObjectModelAdmin)
