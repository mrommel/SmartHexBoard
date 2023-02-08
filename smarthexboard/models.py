"""django models module"""
import uuid
from enum import Enum

from django.db import models
from django.db.models import CheckConstraint, Q
from django.utils.translation import gettext_lazy as _

from smarthexboard.game.types import TechType


class MapGenerationState(models.TextChoices):
	OPEN = 'OP', _('Open')
	RUNNING = 'RU', _('Running')
	READY = 'RE', _('Ready')


class MapGeneration(models.Model):
	uuid = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
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
				name="valid_state"),
			]


class MapModel(models.Model):
	uuid = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
	content = models.CharField(max_length=500000)


class HandicapType(models.TextChoices):
	SETTLER = 'SE', _('Settler')
	CHIEFTAIN = 'CH', _('Chieftain')
	WARLORD = 'WA', _('Warlord')
	PRINCE = 'PR', _('Prince')
	KING = 'KI', _('King')
	EMPEROR = 'EM', _('Emperor')
	IMMORTAL = 'IM', _('Immortal')
	DEITY = 'DE', _('Deity')


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
		if not tech.required():
			return True

		playerTechs = self.playerTechs()

		for required_tech in tech.required():
			required_tech_valid = False
			for player_tech in playerTechs:
				if player_tech.tech_identifier == required_tech.value:
					if player_tech.progress >= required_tech.cost():
						required_tech_valid = True

			if not required_tech_valid:
				return False

		return True

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
