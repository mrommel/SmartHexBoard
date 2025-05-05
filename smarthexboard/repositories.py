from typing import Optional

from django.core.cache import cache
from .smarthexboardlib.game.game import GameModel
from .smarthexboardlib.serialisation.game import GameModelSchema

from smarthexboard.models import GameDataModel


class GameDataRepository:
	# https://docs.djangoproject.com/en/4.2/topics/cache/
	cache_timeout = 600  # in seconds = 5 minutes
	size_limit = 5 * 1024 * 1024

	# cache methods

	@staticmethod
	def _cacheKey(game_uuid) -> str:
		return f"game_{game_uuid}"

	@staticmethod
	def _fetchFromCache(game_uuid) -> Optional[GameModel]:
		return cache.get(GameDataRepository._cacheKey(game_uuid))

	@staticmethod
	def _storeToCache(game_uuid, gameModel):
		cache.set(GameDataRepository._cacheKey(game_uuid), gameModel, GameDataRepository.cache_timeout)

	# database methods

	@staticmethod
	def _fetchFromDatabase(game_uuid) -> Optional[GameModel]:
		game_data = GameDataModel.objects.get(uuid=game_uuid)
		if game_data is None:
			return None

		db_content = game_data.content

		# print(f'_fetchFromDatabase: {db_content}')

		obj = GameModelSchema().loads(db_content)
		return obj

	@staticmethod
	def _storeToDatabase(game_uuid, gameModel):
		try:
			obj = GameDataModel.objects.get(uuid=game_uuid)
		except GameDataModel.DoesNotExist:
			obj = None

		json_str = GameModelSchema().dumps(gameModel)

		# print(f'_storeToDatabase: {json_str}')

		if len(json_str) > GameDataRepository.size_limit:
			raise Exception(f'Cannot store game - game data is more than 500.000 bytes: {len(json_str)}')

		if obj is None:
			new_obj = GameDataModel(uuid=game_uuid, content=json_str)
			new_obj.save()
		else:
			obj.content = json_str
			obj.save()

	@staticmethod
	def _inDB(game_uuid) -> bool:
		try:
			GameDataModel.objects.get(uuid=game_uuid)
			return True
		except GameDataModel.DoesNotExist:
			return False

	@staticmethod
	def _inCache(game_uuid) -> bool:
		return cache.get(GameDataRepository._cacheKey(game_uuid), None) is not None

	# public methods

	@staticmethod
	def inCacheOrDB(game_uuid) -> bool:
		return GameDataRepository._inDB(game_uuid) or GameDataRepository._inCache(game_uuid)

	@staticmethod
	def fetch(game_uuid) -> Optional[GameModel]:
		obj = GameDataRepository._fetchFromCache(game_uuid)

		if obj is None:
			obj: Optional[GameModel] = GameDataRepository._fetchFromDatabase(game_uuid)

			if obj is None:
				return None

			GameDataRepository._storeToCache(game_uuid, obj)
		else:
			cache.touch(game_uuid, GameDataRepository.cache_timeout)

		return obj

	@staticmethod
	def store(game_uuid, obj: GameModel):
		GameDataRepository._storeToDatabase(game_uuid, obj)
		GameDataRepository._storeToCache(game_uuid, obj)
