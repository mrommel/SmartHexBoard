"""django models module"""
import uuid

from django.db import models
from django.db.models import CheckConstraint, Q


class GameGenerationState(models.TextChoices):
	OPEN = 'OP', 'Open'
	RUNNING = 'RU', 'Running'
	READY = 'RE', 'Ready'


class GameGenerationData(models.Model):
	game = models.CharField(max_length=500000)
	state = models.CharField(
		max_length=2,
		choices=GameGenerationState.choices,
		default=GameGenerationState.OPEN,
	)
	progress = models.FloatField(default=0.0)

	objects = models.Manager()

	def __str__(self):
		return f'{self.id}, {self.state}, {self.progress}'

	class Meta:
		constraints = [
			CheckConstraint(
				condition=Q(state__in=GameGenerationState.values),
				name="valid_state"
			)
		]


class GameData(models.Model):
	"""Represents a game instance."""
	name = models.CharField(max_length=100)
	content = models.CharField(max_length=500000)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	# # extra metadata
	# leader = EnumField(LeaderType, default=LeaderType.none, verbose_name="Leader Type")
	# civilization = EnumField(CivilizationType, default=CivilizationType.none, verbose_name="Civilization Name")
	# handicap = EnumField(HandicapType, default=HandicapType.chieftain, max_length=74, verbose_name="Handicap Type")
	# # game speed
	# turn = models.IntegerField(default=0, verbose_name="Current Turn")
	# era = EnumField(EraType, default=EraType.ancient, max_length=73, verbose_name="Era Type")
	# mapType = EnumField(MapType, default=MapType.continents, max_length=11, verbose_name="Map Type")
	# mapSize = EnumField(MapSize, default=MapSize.small, verbose_name="Map Size")

	objects = models.Manager()  # Default manager

	def __str__(self):
		return self.name
