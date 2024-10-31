"""django models module"""
import uuid

from django.db import models
from django.db.models import CheckConstraint, Q


class GameGenerationState(models.TextChoices):
	OPEN = 'OP', 'Open'
	RUNNING = 'RU', 'Running'
	READY = 'RE', 'Ready'


class GameGenerationData(models.Model):
	uuid = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
	game = models.CharField(max_length=500000)
	state = models.CharField(
		max_length=2,
		choices=GameGenerationState.choices,
		default=GameGenerationState.OPEN,
	)
	progress = models.FloatField(default=0.0)

	objects = models.Manager()

	def __str__(self):
		return f'{self.uuid}, {self.state}, {self.progress}'

	class Meta:
		constraints = [
			CheckConstraint(
				condition=Q(state__in=GameGenerationState.values),
				name="valid_state"
			)
		]


class GameDataModel(models.Model):
	uuid = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
	content = models.CharField(max_length=5*1024*1024, default='')  # 5MB

	objects = models.Manager()
