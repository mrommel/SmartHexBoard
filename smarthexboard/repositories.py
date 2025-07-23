from typing import Optional

from django.core.cache import cache
from .smarthexboardlib.game.game import GameModel
from .smarthexboardlib.serialisation.game import GameModelSchema

from smarthexboard.models import GameData


class GameDataRepository:
	# https://docs.djangoproject.com/en/4.2/topics/cache/
	cache_timeout = 600  # in seconds = 5 minutes
	size_limit = 5 * 1024 * 1024

	# cache methods

	@staticmethod
	def _cacheKey(game_id) -> str:
		return f"game_{game_id}"

	@staticmethod
	def _fetchFromCache(game_id: str) -> Optional[GameModel]:
		return cache.get(GameDataRepository._cacheKey(game_id))

	@staticmethod
	def _storeToCache(game_id: str, gameModel: GameModel):
		if gameModel is None:
			raise Exception("GameModel is None")
		if not isinstance(gameModel, GameModel):
			raise Exception(f"GameModel is not an instance of GameModel: {type(gameModel)}")
		if game_id is None:
			raise Exception("Game ID is None")
		if isinstance(game_id, str):
			try:
				game_id = int(game_id)
			except ValueError:
				raise Exception(f"Game ID is not an integer: {game_id}")
		if not isinstance(game_id, int):
			raise Exception(f"Game ID is not an integer: {type(game_id)}")

		cache.set(GameDataRepository._cacheKey(game_id), gameModel, GameDataRepository.cache_timeout)

	# database methods

	@staticmethod
	def _fetchFromDatabase(game_id: str) -> Optional[GameModel]:
		game_data = GameDataModel.objects.get(id=game_id)
		if game_data is None:
			return None

		db_content = game_data.content

		# print(f'_fetchFromDatabase: {db_content}')

		obj = GameModelSchema().loads(db_content)
		return obj

	@staticmethod
	def _storeToDatabase(game_id: Optional[str], gameModel: GameModel) -> str:
		if gameModel is None:
			raise Exception("GameModel is None")

		if not isinstance(gameModel, GameModel):
			raise Exception(f"GameModel is not an instance of GameModel: {type(gameModel)}")

		try:
			obj = GameData.objects.get(id=game_id)
		except GameData.DoesNotExist:
			obj = None

		json_str = GameModelSchema().dumps(gameModel)

		# print(f'_storeToDatabase: {json_str}')

		if len(json_str) > GameDataRepository.size_limit:
			raise Exception(f'Cannot store game - game data is more than 5 MB: {len(json_str)}')

		if obj is None:
			game = GameData.objects.create(name='name', content=json_str)
			game_id = game.id
		else:
			obj.content = json_str
			obj.save()

		return game_id

	@staticmethod
	def _inDB(game_id: Optional[str]) -> bool:
		if game_id is None:
			return False

		try:
			GameData.objects.get(id=game_id)
			return True
		except GameData.DoesNotExist:
			return False

	@staticmethod
	def _inCache(game_id: Optional[str]) -> bool:
		if game_id is None:
			return False

		return cache.get(GameDataRepository._cacheKey(game_id), None) is not None

	# public methods

	@staticmethod
	def inCacheOrDB(game_id: str) -> bool:
		return GameDataRepository._inDB(game_id) or GameDataRepository._inCache(game_id)

	@staticmethod
	def fetch(game_id: str) -> Optional[GameModel]:
		obj = GameDataRepository._fetchFromCache(game_id)

		if obj is None:
			obj: Optional[GameModel] = GameDataRepository._fetchFromDatabase(game_id)

			if obj is None:
				return None

			GameDataRepository._storeToCache(game_id, obj)
		else:
			cache.touch(game_id, GameDataRepository.cache_timeout)

		return obj

	@staticmethod
	def store(game_id: Optional[str], obj: GameModel) -> str:
		game_id = GameDataRepository._storeToDatabase(game_id, obj)
		GameDataRepository._storeToCache(game_id, obj)

		return game_id
