from django.core.cache import cache

from smarthexboard.models import GameDataModel


class GameDataRepository:
	# https://docs.djangoproject.com/en/4.2/topics/cache/
	@staticmethod
	def _fetchFromCache(clas, game_uuid):
		return cache.get(f"game_{game_uuid}")

	@staticmethod
	def _fetchFromDatabase(cls, game_uuid):
		return GameDataModel.objects.get(uuid=game_uuid)



