"""django models module"""
import uuid

from django.db import models
from django.db.models import CheckConstraint, Q
from django.utils.translation import gettext_lazy as _
from smarthexboardlib.game.civilizations import CivilizationType
from smarthexboardlib.map.base import Size


class MapGenerationState(models.TextChoices):
	OPEN = 'OP', _('Open')
	RUNNING = 'RU', _('Running')
	READY = 'RE', _('Ready')


class MapSizeData:
	def __init__(self, name: str, size: Size, num_players: int):
		self.name = name
		self.size = size
		self.num_players = num_players


class MapSizeModel(models.TextChoices):
	DUEL = 'DU', _('TXT_KEY_MAP_SIZE_DUEL_NAME')
	TINY = 'TI', _('TXT_KEY_MAP_SIZE_TINY_NAME')
	SMALL = 'SM', _('TXT_KEY_MAP_SIZE_SMALL_NAME')
	STANDARD = 'ST', _('TXT_KEY_MAP_SIZE_STANDARD_NAME')

	# def name(self) -> str:
	#	return self._data().name

	def size(self) -> Size:
		return self._data().size

	def numOfPlayers(self) -> int:
		return self._data().num_players

	def _data(self):
		if self == MapSizeModel.DUEL:
			return MapSizeData(
				name='TXT_KEY_MAP_SIZE_DUEL_NAME',
				size=Size(32, 22),
				num_players=2
			)
		elif self == MapSizeModel.TINY:
			return MapSizeData(
				name='TXT_KEY_MAP_SIZE_TINY_NAME',
				size=Size(42, 32),
				num_players=3
			)
		elif self == MapSizeModel.SMALL:
			return MapSizeData(
				name='TXT_KEY_MAP_SIZE_SMALL_NAME',
				size=Size(52, 42),
				num_players=4
			)
		elif self == MapSizeModel.STANDARD:
			return MapSizeData(
				name='TXT_KEY_MAP_SIZE_STANDARD_NAME',
				size=Size(62, 52),
				num_players=6
			)

		raise ValueError(f'Not handled enum: {self}')

	@classmethod
	def from_str(cls, label):
		for k, v in cls.__members__.items():
			if k == label:
				return v
		else:
			raise ValueError(f"'{cls.__name__}' enum not found for '{label}'")


class MapTypeModel(models.TextChoices):
	EMPTY = 'EM', _('TXT_KEY_MAP_TYPE_EMPTY_NAME')
	EARTH = 'EA', _('TXT_KEY_MAP_TYPE_EARTH_NAME')
	PANGAEA = 'PA', _('TXT_KEY_MAP_TYPE_PANGAEA_NAME')
	CONTINENTS = 'CO', _('TXT_KEY_MAP_TYPE_CONTINENTS_NAME')
	ARCHIPELAGO = 'AR', _('TXT_KEY_MAP_TYPE_ARCHIPELAGO_NAME')

	@classmethod
	def from_str(cls, label):
		for k, v in cls.__members__.items():
			if k == label:
				return v
		else:
			raise ValueError(f"'{cls.__name__}' enum not found for '{label}'")


class MapGenerationData(models.Model):
	uuid = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
	size = models.CharField(
		max_length=2,
		choices=MapSizeModel.choices,
		default=MapSizeModel.DUEL,
	)
	map = models.CharField(max_length=500000)
	state = models.CharField(
		max_length=2,
		choices=MapGenerationState.choices,
		default=MapGenerationState.OPEN,
	)
	progress = models.FloatField(default=0.0)

	class Meta:
		constraints = [
			CheckConstraint(
				check=Q(state__in=MapGenerationState.values),
				name="valid_state"
			),
			CheckConstraint(
				check=Q(size__in=MapSizeModel.values),
				name="valid_size"
			),
		]


class MapDataModel(models.Model):
	uuid = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
	content = models.CharField(max_length=500000)


class GameDataModel(models.Model):
	uuid = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
	content = models.CharField(max_length=500000)
