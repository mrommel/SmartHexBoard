"""django models module"""
import uuid

from django.db import models
from django.db.models import CheckConstraint, Q
from django.utils.translation import gettext_lazy as _


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
