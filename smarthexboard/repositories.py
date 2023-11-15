from django.core.cache import cache
from smarthexboardlib.game.game import GameModel
from smarthexboardlib.serialisation.game import GameModelSchema

from smarthexboard.models import GameDataModel


class GameDataRepository:
	# https://docs.djangoproject.com/en/4.2/topics/cache/
	cache_timeout = 600  # in seconds = 5 minutes

	# cache methods

	@staticmethod
	def _cacheKey(game_uuid) -> str:
		return f"game_{game_uuid}"

	@staticmethod
	def _fetchFromCache(cls, game_uuid):
		return cache.get(GameDataRepository._cacheKey(game_uuid))

	@staticmethod
	def _storeToCache(cls, game_uuid, gameModel):
		cache.set(GameDataRepository._cacheKey(game_uuid), gameModel, GameDataRepository.cache_timeout)

	# database methods

	@staticmethod
	def _fetchFromDatabase(cls, game_uuid) -> GameModel:
		db_content = GameDataModel.objects.get(uuid=game_uuid).content
		obj_dict = GameModelSchema().loads(db_content)
		return GameModel(obj_dict)

	@staticmethod
	def _storeToDatabase(cls, game_uuid, gameModel):
		obj = GameDataModel.objects.get(uuid=game_uuid)
		json_str = GameModelSchema().dumps(gameModel)

		if obj is None:
			new_obj = GameDataModel(uuid=game_uuid, content=json_str)
			new_obj.save()
		else:
			obj.content = json_str
			obj.save()
