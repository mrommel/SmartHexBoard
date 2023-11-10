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


class HandicapData:
	def __init__(self, name):
		self.name = name


class HandicapTypeModel(models.TextChoices):
	SETTLER = 'SE', _('Settler')
	CHIEFTAIN = 'CH', _('Chieftain')
	WARLORD = 'WA', _('Warlord')
	PRINCE = 'PR', _('Prince')
	KING = 'KI', _('King')
	EMPEROR = 'EM', _('Emperor')
	IMMORTAL = 'IM', _('Immortal')
	DEITY = 'DE', _('Deity')

	@classmethod
	def from_str(cls, label):
		for k, v in cls.__members__.items():
			if k == label:
				return v
		else:
			raise ValueError(f"'{cls.__name__}' enum not found for '{label}'")

	# def name(self) -> str:
	#	return self._data().name

	def _data(self):
		if self == HandicapTypeModel.SETTLER:
			return HandicapData(
				'TXT_KEY_HANDICAP_SETTLER'
			)
		elif self == HandicapTypeModel.CHIEFTAIN:
			return HandicapData(
				'TXT_KEY_HANDICAP_CHIEFTAIN'
			)
		elif self == HandicapTypeModel.WARLORD:
			return HandicapData(
				'TXT_KEY_HANDICAP_WARLORD'
			)
		elif self == HandicapTypeModel.PRINCE:
			return HandicapData(
				'TXT_KEY_HANDICAP_PRINCE'
			)
		elif self == HandicapTypeModel.KING:
			return HandicapData(
				'TXT_KEY_HANDICAP_KING'
			)
		elif self == HandicapTypeModel.EMPEROR:
			return HandicapData(
				'TXT_KEY_HANDICAP_EMPEROR'
			)
		elif self == HandicapTypeModel.IMMORTAL:
			return HandicapData(
				'TXT_KEY_HANDICAP_IMMORTAL'
			)
		elif self == HandicapTypeModel.DEITY:
			return HandicapData(
				'TXT_KEY_HANDICAP_DEITY'
			)

		raise AttributeError(f'cant get data for handicap {self}')


class GameDataModel(models.Model):
	uuid = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
	map = models.ForeignKey(MapDataModel, on_delete=models.CASCADE, blank=True, default=None)
	name = models.CharField(max_length=100)
	turn = models.IntegerField(default=0)  # game start at turn 0
	handicap = models.CharField(
		max_length=2,
		choices=HandicapTypeModel.choices,
		default=HandicapTypeModel.SETTLER,
	)

	class Meta:
		constraints = [
			CheckConstraint(
				check=Q(handicap__in=HandicapTypeModel.values),
				name="valid_handicap"),
		]

	def players(self):
		return PlayerModel.objects.filter(game=self)


class LeaderTypeModel(models.TextChoices):
	ALEXANDER = 'AL', _('Alexander')
	TRAJAN = 'TR', _('Trajan')
	VICTORIA = 'VI', _('Victoria')
	MONTEZUMA = 'MO', _('Montezuma')
	CYRUS = 'CY', _('Cyrus')
	NAPOLEON = 'NA', _('Napoleon')
	CLEOPATRA = 'CL', _('Cleopatra')
	BARBAROSSA = 'BA', _('Barbarossa')
	PETERTHEGREAT = 'PE', _('Peter the Great')

	@classmethod
	def from_str(cls, label):
		for k, v in cls.__members__.items():
			if k == label:
				return v
		else:
			raise ValueError(f"'{cls.__name__}' enum not found for '{label}'")

	def civilization(self) -> CivilizationType:
		if self == LeaderTypeModel.ALEXANDER:
			return CivilizationType.greece

		raise AttributeError(f'civilization for leader type {self} not found')

	def __str__(self):
		return f'{self.label}'


class PlayerModel(models.Model):
	leader = models.CharField(
		max_length=2,
		choices=LeaderTypeModel.choices,
		default=LeaderTypeModel.ALEXANDER,
	)
	human = models.BooleanField(default=False)
	game = models.ForeignKey(GameDataModel, on_delete=models.CASCADE, blank=True, default=None)

	class Meta:
		constraints = [
			CheckConstraint(
				check=Q(leader__in=LeaderTypeModel.values),
				name="valid_leader"),
		]

	def __str__(self):
		return f'{self.leader.name}'
