"""django models module"""
import uuid

from django.db import models
from django.db.models import CheckConstraint, Q
from django.utils.translation import gettext_lazy as _
from smarthexboardlib.game.civilizations import CivilizationType
from smarthexboardlib.map.base import Size


class GameGenerationState(models.TextChoices):
	OPEN = 'OP', _('Open')
	RUNNING = 'RU', _('Running')
	READY = 'RE', _('Ready')


class MapSizeModel(models.TextChoices):
	DUEL = 'DU', _('TXT_KEY_MAP_SIZE_DUEL_NAME')
	TINY = 'TI', _('TXT_KEY_MAP_SIZE_TINY_NAME')
	SMALL = 'SM', _('TXT_KEY_MAP_SIZE_SMALL_NAME')
	STANDARD = 'ST', _('TXT_KEY_MAP_SIZE_STANDARD_NAME')


class MapTypeModel(models.TextChoices):
	EMPTY = 'EM', _('TXT_KEY_MAP_TYPE_EMPTY_NAME')
	EARTH = 'EA', _('TXT_KEY_MAP_TYPE_EARTH_NAME')
	PANGAEA = 'PA', _('TXT_KEY_MAP_TYPE_PANGAEA_NAME')
	CONTINENTS = 'CO', _('TXT_KEY_MAP_TYPE_CONTINENTS_NAME')
	ARCHIPELAGO = 'AR', _('TXT_KEY_MAP_TYPE_ARCHIPELAGO_NAME')


class GameGenerationData(models.Model):
	uuid = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
	game = models.CharField(max_length=500000)
	state = models.CharField(
		max_length=2,
		choices=GameGenerationState.choices,
		default=GameGenerationState.OPEN,
	)
	progress = models.FloatField(default=0.0)

	class Meta:
		constraints = [
			CheckConstraint(
				check=Q(state__in=GameGenerationState.values),
				name="valid_state"
			)
		]


class GameDataModel(models.Model):
	uuid = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
	content = models.CharField(max_length=500000, default='')
