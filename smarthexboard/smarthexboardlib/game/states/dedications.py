from typing import List

from smarthexboard.smarthexboardlib.game.types import EraType
from smarthexboard.smarthexboardlib.core.base import ExtendedEnum, InvalidEnumError


class DedicationTypeData:
	def __init__(self, name: str, normalEffect: str, goldenEffect: str, eras: List[EraType]):
		self.name = name
		self.normalEffect = normalEffect
		self.goldenEffect = goldenEffect
		self.eras = eras


class DedicationType(ExtendedEnum):
	# normal, golden
	monumentality = 'monumentality'  # +, +
	penBrushAndVoice = 'penBrushAndVoice'  # +, +
	freeInquiry = 'freeInquiry'  # +, +
	exodusOfTheEvangelists = 'exodusOfTheEvangelists'  #  # , #
	hicSuntDracones = 'hicSuntDracones'  #  # , #
	reformTheCoinage = 'reformTheCoinage'  #  # , #
	heartbeatOfSteam = 'heartbeatOfSteam'  #  # , #
	toArms = 'toArms'  #  # , #
	wishYouWereHere = 'wishYouWereHere'  #  # , #
	bodyguardOfLies = 'bodyguardOfLies'  #  # , #
	skyAndStars = 'skyAndStars'  #  # , #
	automatonWarfare = 'automatonWarfare'  #  # , #

	def title(self) -> str:
		return self._data().name

	def normalEffect(self) -> str:
		return self._data().normalEffect

	def	goldenEffect(self) -> str:
		return self._data().goldenEffect

	def eras(self) -> [EraType]:
		return self._data().eras

	def _data(self):
		if self == DedicationType.monumentality:
			return DedicationTypeData(
				name="TXT_KEY_DEDICATION_MONUMENTALITY_TITLE",
				normalEffect="TXT_KEY_DEDICATION_MONUMENTALITY_NORMAL_EFFECT",
				goldenEffect="TXT_KEY_DEDICATION_MONUMENTALITY_GOLDEN_EFFECT",
				eras=[EraType.classical, EraType.medieval, EraType.renaissance]
			)
		elif self == DedicationType.penBrushAndVoice:
			return DedicationTypeData(
				name="TXT_KEY_DEDICATION_PEN_BRUSH_VOICE_TITLE",
				normalEffect="TXT_KEY_DEDICATION_PEN_BRUSH_VOICE_NORMAL_EFFECT",
				goldenEffect="TXT_KEY_DEDICATION_PEN_BRUSH_VOICE_GOLDEN_EFFECT",
				eras=[EraType.classical, EraType.medieval]
			)
		elif self == DedicationType.freeInquiry:
			return DedicationTypeData(
				name="TXT_KEY_DEDICATION_FREE_INQUIRY_TITLE",
				normalEffect="TXT_KEY_DEDICATION_FREE_INQUIRY_NORMAL_EFFECT",
				goldenEffect="TXT_KEY_DEDICATION_FREE_INQUIRY_GOLDEN_EFFECT",
				eras=[EraType.classical, EraType.medieval]
			)
		elif self == DedicationType.exodusOfTheEvangelists:
			return DedicationTypeData(
				name="TXT_KEY_DEDICATION_EXODUS_EVANGELISTS_TITLE",
				normalEffect="TXT_KEY_DEDICATION_EXODUS_EVANGELISTS_NORMAL_EFFECT",
				goldenEffect="TXT_KEY_DEDICATION_EXODUS_EVANGELISTS_GOLDEN_EFFECT",
				eras=[EraType.classical, EraType.medieval, EraType.renaissance]
			)
		elif self == DedicationType.hicSuntDracones:
			return DedicationTypeData(
				name="TXT_KEY_DEDICATION_DRACONES_TITLE",
				normalEffect="TXT_KEY_DEDICATION_DRACONES_NORMAL_EFFECT",
				goldenEffect="TXT_KEY_DEDICATION_DRACONES_GOLDEN_EFFECT",
				eras=[EraType.renaissance, EraType.industrial, EraType.modern]
			)
		elif self == DedicationType.reformTheCoinage:
			return DedicationTypeData(
				name="TXT_KEY_DEDICATION_REFORM_COINAGE_TITLE",
				normalEffect="TXT_KEY_DEDICATION_REFORM_COINAGE_NORMAL_EFFECT",
				goldenEffect="TXT_KEY_DEDICATION_REFORM_COINAGE_GOLDEN_EFFECT",
				eras=[EraType.renaissance, EraType.industrial, EraType.modern]
			)
		elif self == DedicationType.heartbeatOfSteam:
			return DedicationTypeData(
				name="TXT_KEY_DEDICATION_HEARTBEAT_STEAM_TITLE",
				normalEffect="TXT_KEY_DEDICATION_HEARTBEAT_STEAM_NORMAL_EFFECT",
				goldenEffect="TXT_KEY_DEDICATION_HEARTBEAT_STEAM_GOLDEN_EFFECT",
				eras=[EraType.industrial, EraType.modern]
			)
		elif self == DedicationType.toArms:
			return DedicationTypeData(
				name="TXT_KEY_DEDICATION_ARMS_TITLE",
				normalEffect="TXT_KEY_DEDICATION_ARMS_NORMAL_EFFECT",
				goldenEffect="TXT_KEY_DEDICATION_ARMS_GOLDEN_EFFECT",
				eras=[EraType.industrial, EraType.modern, EraType.atomic, EraType.information]
			)
		elif self == DedicationType.wishYouWereHere:
			return DedicationTypeData(
				name="TXT_KEY_DEDICATION_WISH_HERE_TITLE",
				normalEffect="TXT_KEY_DEDICATION_WISH_HERE_NORMAL_EFFECT",
				goldenEffect="TXT_KEY_DEDICATION_WISH_HERE_GOLDEN_EFFECT",
				eras=[EraType.atomic, EraType.information]
			)
		elif self == DedicationType.bodyguardOfLies:
			return DedicationTypeData(
				name="TXT_KEY_DEDICATION_BODYGUARD_LIES_TITLE",
				normalEffect="TXT_KEY_DEDICATION_BODYGUARD_LIES_NORMAL_EFFECT",
				goldenEffect="TXT_KEY_DEDICATION_BODYGUARD_LIES_GOLDEN_EFFECT",
				eras=[EraType.atomic, EraType.information]
			)
		elif self == DedicationType.skyAndStars:
			return DedicationTypeData(
				name="TXT_KEY_DEDICATION_SKY_STARS_TITLE",
				normalEffect="TXT_KEY_DEDICATION_SKY_STARS_NORMAL_EFFECT",
				goldenEffect="TXT_KEY_DEDICATION_SKY_STARS_GOLDEN_EFFECT",
				eras=[EraType.atomic, EraType.information]
			)
		elif self == DedicationType.automatonWarfare:
			return DedicationTypeData(
				name="TXT_KEY_DEDICATION_AUTOMATON_WARFARE_TITLE",
				normalEffect="TXT_KEY_DEDICATION_AUTOMATON_NORMAL_EFFECT",
				goldenEffect="TXT_KEY_DEDICATION_AUTOMATON_GOLDEN_EFFECT",
				eras=[EraType.information]
			)

		raise InvalidEnumError(self)
