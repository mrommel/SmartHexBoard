"""django models module"""
import uuid
from enum import Enum

from django.db import models
from django.db.models import CheckConstraint, Q
from django.utils.translation import gettext_lazy as _

from smarthexboard.game.types import TechType
from smarthexboard.map.base import Size


class MapGenerationState(models.TextChoices):
	OPEN = 'OP', _('Open')
	RUNNING = 'RU', _('Running')
	READY = 'RE', _('Ready')


class MapSizeData:
	def __init__(self, name: str, size: Size, num_players: int):
		self.name = name
		self.size = size
		self.num_players = num_players


class MapSize(models.TextChoices):
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
		if self == MapSize.DUEL:
			return MapSizeData(
				name='TXT_KEY_MAP_SIZE_DUEL_NAME',
				size=Size(32, 22),
				num_players=2
			)
		elif self == MapSize.TINY:
			return MapSizeData(
				name='TXT_KEY_MAP_SIZE_TINY_NAME',
				size=Size(42, 32),
				num_players=3
			)
		elif self == MapSize.SMALL:
			return MapSizeData(
				name='TXT_KEY_MAP_SIZE_SMALL_NAME',
				size=Size(52, 42),
				num_players=4
			)
		elif self == MapSize.STANDARD:
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


class MapType(models.TextChoices):
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


class MapGeneration(models.Model):
	uuid = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
	size = models.CharField(
		max_length=2,
		choices=MapSize.choices,
		default=MapSize.DUEL,
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
				check=Q(size__in=MapSize.values),
				name="valid_size"
			),
		]


class MapModel(models.Model):
	uuid = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
	content = models.CharField(max_length=500000)


class HandicapData:
	def __init__(self, name):
		self.name = name


class HandicapType(models.TextChoices):
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
		if self == HandicapType.SETTLER:
			return HandicapData(
				'TXT_KEY_HANDICAP_SETTLER'
			)
		elif self == HandicapType.CHIEFTAIN:
			return HandicapData(
				'TXT_KEY_HANDICAP_CHIEFTAIN'
			)
		elif self == HandicapType.WARLORD:
			return HandicapData(
				'TXT_KEY_HANDICAP_WARLORD'
			)
		elif self == HandicapType.PRINCE:
			return HandicapData(
				'TXT_KEY_HANDICAP_PRINCE'
			)
		elif self == HandicapType.KING:
			return HandicapData(
				'TXT_KEY_HANDICAP_KING'
			)
		elif self == HandicapType.EMPEROR:
			return HandicapData(
				'TXT_KEY_HANDICAP_EMPEROR'
			)
		elif self == HandicapType.IMMORTAL:
			return HandicapData(
				'TXT_KEY_HANDICAP_IMMORTAL'
			)
		elif self == HandicapType.DEITY:
			return HandicapData(
				'TXT_KEY_HANDICAP_DEITY'
			)

		raise AttributeError(f'cant get data for handicap {self}')


class GameModel(models.Model):
	uuid = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
	map = models.ForeignKey(MapModel, on_delete=models.CASCADE, blank=True, default=None)
	name = models.CharField(max_length=100)
	turn = models.IntegerField(default=0)  # game start at turn 0
	handicap = models.CharField(
		max_length=2,
		choices=HandicapType.choices,
		default=HandicapType.SETTLER,
	)

	class Meta:
		constraints = [
			CheckConstraint(
				check=Q(handicap__in=HandicapType.values),
				name="valid_handicap"),
		]

	def players(self):
		return Player.objects.filter(game=self)


class CivilizationType(Enum):
	greek = 'greek'
	roman = 'roman'
	english = 'english'
	aztecs = 'aztecs'
	persian = 'persian'
	french = 'french'
	egyptian = 'egyptian'
	german = 'german'
	russian = 'russian'


class LeaderType(models.TextChoices):
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
		if self == LeaderType.ALEXANDER:
			return CivilizationType.greek

		raise AttributeError(f'civilization for leader type {self} not found')

	def __str__(self):
		return f'{self.label}'


class Player(models.Model):
	leader = models.CharField(
		max_length=2,
		choices=LeaderType.choices,
		default=LeaderType.ALEXANDER,
	)
	human = models.BooleanField(default=False)
	game = models.ForeignKey(GameModel, on_delete=models.CASCADE, blank=True, default=None)

	class Meta:
		constraints = [
			CheckConstraint(
				check=Q(leader__in=LeaderType.values),
				name="valid_leader"),
		]

	def playerTechs(self):
		return PlayerTech.objects.filter(player=self)

	def canResearch(self, tech: TechType):
		playerTechs = self.playerTechs()

		# if tech is already researched, it cannot be researched again
		player_techs = PlayerTech.objects.filter(tech_identifier=tech.value)
		if len(player_techs) == 1:
			if player_techs[0].progress >= tech.cost():
				return False

		# if there are no requirements - this can be researched
		if not tech.required():
			return True

		for required_tech in tech.required():
			required_tech_valid = False
			for player_tech in playerTechs:
				if player_tech.tech_identifier == required_tech.value:
					if player_tech.progress >= required_tech.cost():
						required_tech_valid = True

			if not required_tech_valid:
				return False

		return True

	def updateTechProgress(self, tech: TechType, progress: int):
		player_tech = PlayerTech.objects.filter(tech_identifier=tech.value)
		player_tech.progress = progress

	def __str__(self):
		return f'{self.leader.name}'


class PlayerTech(models.Model):
	player = models.ForeignKey(Player, on_delete=models.CASCADE, blank=True, default=None)
	tech_identifier = models.CharField(
		max_length=20,
		choices=map(lambda tech: (tech.value, tech.name()), TechType.list()),
		default=('none', 'TXT_KEY_TECH_NONE'),
	)
	progress = models.IntegerField(default=0)
	eureka = models.BooleanField(default=False)

	class Meta:
		constraints = [
			CheckConstraint(
				check=Q(tech_identifier__in=map(lambda tech: tech.value, TechType.list())),
				name="valid_tech_identifier"),
		]
