from django.contrib import admin, messages
from django.utils.safestring import mark_safe

from smarthexassets.models import Object, Asset


class ListStyleAdminMixin(object):
	def row_css(self, obj, index):
		return ''


class ObjectCitiesInline(admin.TabularInline):
	model = Asset.asset_objects.through
	# form = CityInlineForm
	extra = 1


class AssetModelAdmin(admin.ModelAdmin, ListStyleAdminMixin):
	model = Asset
	inlines = [ObjectCitiesInline, ]
	list_display = ('name', 'hint', 'width', 'height', 'tagging')
	readonly_fields = [
		'tagging',
	]

	def tagging(self, object) -> str:
		return mark_safe(f'<img src="/smarthexassets/asset/{object.id}/render.png" height=144 />')


class ObjectModelAdmin(admin.ModelAdmin, ListStyleAdminMixin):
	model = Object
	list_display = ('name', 'type', 'width', 'height')
	# fields = ('name', 'type', 'width', 'height')
	readonly_fields = ('width', 'height')

	def get_fieldsets(self, request, obj=None):
		fieldsets = list(super().get_fieldsets(request, obj) or [])
		if obj is None:
			fieldsets[0][1]['fields'] = ('name', 'type', 'file')

		return fieldsets

