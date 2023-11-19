from enum import Enum

from smarthexboard.smarthexboardlib.game.types import TechType, CivicType
from smarthexboard.smarthexboardlib.game.units import UnitType
from smarthexboard.smarthexboardlib.core.base import InvalidEnumError, ExtendedEnum
from smarthexboard.smarthexboardlib.utils.translation import gettext_lazy as _


class ReplayEventType(ExtendedEnum):
	major = 'major'
	religionFounded = 'religionFounded'
	cityFounded = 'cityFounded'  # REPLAY_MESSAGE_CITY_FOUNDED
	cityCaptured = 'cityCaptured'  # REPLAY_MESSAGE_CITY_CAPTURED
	cityDestroyed = 'cityDestroyed'  # REPLAY_MESSAGE_CITY_DESTROYED
	wonderBuilt = 'wonderBuilt'
	playerKilled = 'playerKilled'
	goldenAge = 'goldenAge'


class HandicapTypeData:
	def __init__(self, name: str, value: int, barbarianCampGold: int, barbarianSpawnMod: int,
	             earliestBarbarianReleaseTurn: int, barbarianLandTargetRange: int, barbarianSpawnModifier: int,
	             freeHumanTechs: [TechType], freeHumanCivics: [CivicType], freeHumanStartingUnitTypes: [UnitType],
	             freeHumanCombatBonus: int, freeAIStartingUnitTypes: [UnitType], freeAICombatBonus: int):
		self.name = name
		self.value = value
		# barbarian
		self.barbarianCampGold = barbarianCampGold
		self.barbarianSpawnMod = barbarianSpawnMod
		self.earliestBarbarianReleaseTurn = earliestBarbarianReleaseTurn
		self.barbarianLandTargetRange = barbarianLandTargetRange
		self.barbarianSpawnModifier = barbarianSpawnModifier
		# human
		self.freeHumanTechs = freeHumanTechs
		self.freeHumanCivics = freeHumanCivics
		self.freeHumanStartingUnitTypes = freeHumanStartingUnitTypes
		self.freeHumanCombatBonus = freeHumanCombatBonus
		# ai
		self.freeAIStartingUnitTypes = freeAIStartingUnitTypes
		self.freeAICombatBonus = freeAICombatBonus


class HandicapType:
	pass


class HandicapType(ExtendedEnum):
	# https://civ6.gamepedia.com/Game_difficulty

	settler = 'settler'
	chieftain = 'chieftain'
	warlord = 'warlord'
	prince = 'prince'
	king = 'king'
	emperor = 'emperor'
	immortal = 'immortal'
	deity = 'deity'

	@staticmethod
	def fromName(handicapName: str) -> HandicapType:
		if handicapName == 'HandicapType.settler' or handicapName == 'settler':
			return HandicapType.settler
		elif handicapName == 'HandicapType.chieftain' or handicapName == 'chieftain':
			return HandicapType.chieftain
		elif handicapName == 'HandicapType.warlord' or handicapName == 'warlord':
			return HandicapType.warlord
		elif handicapName == 'HandicapType.prince' or handicapName == 'prince':
			return HandicapType.prince
		elif handicapName == 'HandicapType.king' or handicapName == 'king':
			return HandicapType.king
		elif handicapName == 'HandicapType.emperor' or handicapName == 'emperor':
			return HandicapType.emperor
		elif handicapName == 'HandicapType.immortal' or handicapName == 'immortal':
			return HandicapType.immortal
		elif handicapName == 'HandicapType.deity' or handicapName == 'deity':
			return HandicapType.deity

		raise Exception(f'No matching case for handicapName: "{handicapName}"')

	def __gt__(self, other):
		if isinstance(other, HandicapType):
			return self.value() > other.value()

		raise Exception(f'Cannot compare HandicapType and {type(other)}')

	def title(self) -> str:  # cannot be 'name'
		return self._data().name

	def value(self) -> int:
		return self._data().value

	def freeHumanStartingUnitTypes(self) -> [UnitType]:
		return self._data().freeHumanStartingUnitTypes

	def freeHumanCombatBonus(self) -> int:
		return self._data().freeHumanCombatBonus

	def freeAICombatBonus(self) -> int:
		return self._data().freeAICombatBonus

	def earliestBarbarianReleaseTurn(self) -> int:
		return self._data().earliestBarbarianReleaseTurn

	def barbarianLandTargetRange(self) -> int:
		return self._data().barbarianLandTargetRange

	def barbarianSpawnModifier(self) -> int:
		return self._data().barbarianSpawnModifier

	def barbarianCampGold(self) -> int:
		return self._data().barbarianCampGold

	def _data(self) -> HandicapTypeData:
		if self == HandicapType.settler:
			#
			return HandicapTypeData(
				name=_("TXT_KEY_HANDICAP_SETTLER"),
				value=0,
				barbarianCampGold=50,
				barbarianSpawnMod=8,
				earliestBarbarianReleaseTurn=50,
				barbarianLandTargetRange=2,
				barbarianSpawnModifier=8,
				# human
				freeHumanTechs=[TechType.pottery, TechType.animalHusbandry, TechType.mining],
				freeHumanCivics=[],
				freeHumanStartingUnitTypes=[UnitType.settler, UnitType.warrior, UnitType.warrior, UnitType.builder],
				freeHumanCombatBonus=3,
				# ai
				freeAIStartingUnitTypes=[UnitType.settler, UnitType.warrior],
				freeAICombatBonus=-1
			)
		elif self == HandicapType.chieftain:
			#
			return HandicapTypeData(
				name=_("TXT_KEY_HANDICAP_CHIEFTAIN"),
				value=1,
				barbarianCampGold=40,
				barbarianSpawnMod=5,
				earliestBarbarianReleaseTurn=40,
				barbarianLandTargetRange=3,
				barbarianSpawnModifier=5,
				# human
				freeHumanTechs=[TechType.pottery, TechType.animalHusbandry],
				freeHumanCivics=[],
				freeHumanStartingUnitTypes=[UnitType.settler, UnitType.warrior, UnitType.builder],
				freeHumanCombatBonus=2,
				# ai
				freeAIStartingUnitTypes=[UnitType.settler, UnitType.warrior],
				freeAICombatBonus=-1
			)
		elif self == HandicapType.warlord:
			#
			return HandicapTypeData(
				name=_("TXT_KEY_HANDICAP_WARLORD"),
				value=2,
				barbarianCampGold=30,
				barbarianSpawnMod=3,
				earliestBarbarianReleaseTurn=35,
				barbarianLandTargetRange=4,
				barbarianSpawnModifier=3,
				# human
				freeHumanTechs=[TechType.pottery],
				freeHumanCivics=[],
				freeHumanStartingUnitTypes=[
					UnitType.settler, UnitType.warrior, UnitType.builder
				],
				freeHumanCombatBonus=1,
				# ai
				freeAIStartingUnitTypes=[UnitType.settler, UnitType.warrior],
				freeAICombatBonus=-1
			)
		elif self == HandicapType.prince:
			#
			return HandicapTypeData(
				name=_("TXT_KEY_HANDICAP_PRINCE"),
				value=3,
				barbarianCampGold=25,
				barbarianSpawnMod=0,
				earliestBarbarianReleaseTurn=35,
				barbarianLandTargetRange=5,
				barbarianSpawnModifier=0,
				# human
				freeHumanTechs=[],
				freeHumanCivics=[],
				freeHumanStartingUnitTypes=[UnitType.settler, UnitType.warrior],
				freeHumanCombatBonus=0,
				# ai
				freeAIStartingUnitTypes=[UnitType.settler, UnitType.warrior],
				freeAICombatBonus=0
			)
		elif self == HandicapType.king:
			#
			return HandicapTypeData(
				name=_("TXT_KEY_HANDICAP_KING"),
				value=4,
				barbarianCampGold=25,
				barbarianSpawnMod=0,
				earliestBarbarianReleaseTurn=30,
				barbarianLandTargetRange=5,
				barbarianSpawnModifier=0,
				# human
				freeHumanTechs=[],
				freeHumanCivics=[],
				freeHumanStartingUnitTypes=[UnitType.settler, UnitType.warrior],
				freeHumanCombatBonus=0,
				# ai
				freeAIStartingUnitTypes=[UnitType.settler, UnitType.warrior, UnitType.warrior, UnitType.builder],
				freeAICombatBonus=1
			)
		elif self == HandicapType.emperor:
			#
			return HandicapTypeData(
				name=_("TXT_KEY_HANDICAP_EMPEROR"),
				value=5,
				barbarianCampGold=25,
				barbarianSpawnMod=0,
				earliestBarbarianReleaseTurn=20,
				barbarianLandTargetRange=6,
				barbarianSpawnModifier=0,
				# human
				freeHumanTechs=[],
				freeHumanCivics=[],
				freeHumanStartingUnitTypes=[UnitType.settler, UnitType.warrior],
				freeHumanCombatBonus=0,
				# ai
				freeAIStartingUnitTypes=[
					UnitType.settler,
					UnitType.settler,
					UnitType.warrior,
					UnitType.warrior,
					UnitType.warrior,
					UnitType.builder
				],
				freeAICombatBonus=2
			)
		elif self == HandicapType.immortal:
			#
			return HandicapTypeData(
				name=_("TXT_KEY_HANDICAP_IMMORTAL"),
				value=6,
				barbarianCampGold=25,
				barbarianSpawnMod=0,
				earliestBarbarianReleaseTurn=10,
				barbarianLandTargetRange=7,
				barbarianSpawnModifier=0,
				# human
				freeHumanTechs=[],
				freeHumanCivics=[],
				freeHumanStartingUnitTypes=[UnitType.settler, UnitType.warrior],
				freeHumanCombatBonus=0,
				# ai
				freeAIStartingUnitTypes=[
					UnitType.settler,
					UnitType.settler,
					UnitType.warrior,
					UnitType.warrior,
					UnitType.warrior,
					UnitType.warrior,
					UnitType.builder,
					UnitType.builder
				],
				freeAICombatBonus=3
			)
		elif self == HandicapType.deity:
			#
			return HandicapTypeData(
				name=_("TXT_KEY_HANDICAP_DEITY"),
				value=7,
				barbarianCampGold=25,
				barbarianSpawnMod=0,
				earliestBarbarianReleaseTurn=0,
				barbarianLandTargetRange=8,
				barbarianSpawnModifier=0,
				# human
				freeHumanTechs=[],
				freeHumanCivics=[],
				freeHumanStartingUnitTypes=[UnitType.settler, UnitType.warrior],
				freeHumanCombatBonus=0,
				# ai
				freeAIStartingUnitTypes=[
					UnitType.settler,
					UnitType.settler,
					UnitType.settler,
					UnitType.warrior,
					UnitType.warrior,
					UnitType.warrior,
					UnitType.warrior,
					UnitType.warrior,
					UnitType.builder,
					UnitType.builder
				],
				freeAICombatBonus=4
			)

	def freeAIStartingUnitTypes(self) -> [UnitType]:
		return self._data().freeAIStartingUnitTypes

	def firstImpressionBaseValue(self):
		# // -3 - +3
		# Deity -2 to -8
		# Immortal -1 to -7
		# Emperor 0 a -6
		# King1 to -5
		# Prince 2 to -4
		# https://forums.civfanatics.com/threads/first-impression-of-you.613161/ */
		if self == HandicapType.settler:
			return 2
		elif self == HandicapType.chieftain:
			return 1
		elif self == HandicapType.warlord:
			return 0
		elif self == HandicapType.prince:
			return -1
		elif self == HandicapType.king:
			return -2
		elif self == HandicapType.emperor:
			return -3
		elif self == HandicapType.immortal:
			return -4
		elif self == HandicapType.deity:
			return -5

		raise InvalidEnumError(self)

	def freeHumanTechs(self) -> [TechType]:
		return self._data().freeHumanTechs

	def freeHumanCivics(self) -> [CivicType]:
		return self._data().freeHumanCivics

	def freeAITechs(self) -> [TechType]:
		# fixme
		return []

	def freeAICivics(self) -> [CivicType]:
		# fixme
		return []

	def aiDeclareWarProbability(self) -> int:
		"""in percent"""
		# fixme
		return 100


class GameState(Enum):
	on = 'on'
	over = 'over'
	extended = 'extended'


class ArtifactType(ExtendedEnum):
	none = 'none'

	battleRanged = 'battleRanged'
	battleMelee = 'battleMelee'
	barbarianCamp = 'barbarianCamp'
	razedCity = 'razedCity'
	ancientRuin = 'ancientRuin'

	battleSeaMelee = 'battleSeaMelee'
	battleSeaRanged = 'battleSeaRanged'


class PlayerTargetValueType(ExtendedEnum):
	none = -1, 'none'

	impossible = 0, 'impossible'
	bad = 1, 'bad'
	average = 2, 'average'
	favorable = 3, 'favorable'
	soft = 4, 'soft'

	def __new__(cls, value, name):
		member = object.__new__(cls)
		member._value = value
		member._name = name
		return member

	def __lt__(self, other):
		if isinstance(other, PlayerTargetValueType):
			if self == PlayerTargetValueType.none or other == PlayerTargetValueType.none:
				raise InvalidEnumError(self)

			return self._value < other._value

		raise Exception(f'Cannot compare PlayerTargetValueType with {type(other)}')

	def __ge__(self, other):
		if isinstance(other, PlayerTargetValueType):
			if self == PlayerTargetValueType.none or other == PlayerTargetValueType.none:
				raise InvalidEnumError(self)

			return self._value >= other._value

		raise Exception(f'Cannot compare PlayerTargetValueType with {type(other)}')

	def increase(self):
		if self == PlayerTargetValueType.none:
			raise InvalidEnumError(self)

		if self == PlayerTargetValueType.impossible:
			return PlayerTargetValueType.bad
		elif self == PlayerTargetValueType.bad:
			return PlayerTargetValueType.average
		elif self == PlayerTargetValueType.average:
			return PlayerTargetValueType.favorable
		elif self == PlayerTargetValueType.favorable:
			return PlayerTargetValueType.soft
		elif self == PlayerTargetValueType.soft:
			return PlayerTargetValueType.soft

	def decrease(self):
		if self == PlayerTargetValueType.none:
			raise InvalidEnumError(self)

		if self == PlayerTargetValueType.impossible:
			return PlayerTargetValueType.impossible
		elif self == PlayerTargetValueType.bad:
			return PlayerTargetValueType.impossible
		elif self == PlayerTargetValueType.average:
			return PlayerTargetValueType.bad
		elif self == PlayerTargetValueType.favorable:
			return PlayerTargetValueType.average
		elif self == PlayerTargetValueType.soft:
			return PlayerTargetValueType.favorable



class WarDamageLevelType(ExtendedEnum):
	none = 'none'

	crippled = 'crippled'
	serious = 'serious'
	major = 'major'
	minor = 'minor'


class WarProjectionType(ExtendedEnum):
	unknown = -1, 'unknown'

	veryGood = 0, 'veryGood'  # WAR_PROJECTION_VERY_GOOD
	good = 1, 'good'  # WAR_PROJECTION_GOOD
	stalemate = 2, 'stalemate'  # WAR_PROJECTION_STALEMATE
	defeat = 3, 'defeat'  # WAR_PROJECTION_DEFEAT
	destruction = 4, 'destruction'  # WAR_PROJECTION_DESTRUCTION

	def __new__(cls, value, name):
		member = object.__new__(cls)
		member._value = value
		member._name = name
		return member

	def value(self) -> int:
		return int(self._value)

	def __lt__(self, other):
		if isinstance(other, WarProjectionType):
			return self._value < other._value

		raise Exception(f'cannot compare WarProjectionType and {type(other)}')

	def __ge__(self, other):
		if isinstance(other, WarProjectionType):
			return self._value >= other._value

		raise Exception(f'cannot compare WarProjectionType and {type(other)}')


class DisputeLevelType(ExtendedEnum):
	none = 0, 'none'  # DISPUTE_LEVEL_NONE

	weak = 1, 'weak'  # DISPUTE_LEVEL_WEAK
	strong = 2, 'strong'  # DISPUTE_LEVEL_STRONG
	fierce = 3, 'fierce'  # DISPUTE_LEVEL_FIERCE

	def __new__(cls, value, name):
		member = object.__new__(cls)
		member._value = value
		member._name = name
		return member

	def value(self) -> int:
		return int(self._value)

	def __lt__(self, other):
		if isinstance(other, DisputeLevelType):
			return self._value < other._value

		raise Exception(f'cannot compare DisputeLevelType and {type(other)}')

	def __ge__(self, other):
		if isinstance(other, DisputeLevelType):
			return self._value >= other._value

		raise Exception(f'cannot compare DisputeLevelType and {type(other)}')


class AggressivePostureType:
	pass


class AggressivePostureType(ExtendedEnum):
	none = -1, 'none'

	low = 0, 'low'
	medium = 1, 'medium'
	high = 2, 'high'
	incredible = 3, 'incredible'

	def __new__(cls, value, name):
		member = object.__new__(cls)
		member._value = value
		member._name = name
		return member

	def value(self) -> int:
		return int(self._value)

	def __lt__(self, other):
		if isinstance(other, AggressivePostureType):
			return self._value < other._value

		raise Exception(f'cannot compare AggressivePostureType and {type(other)}')

	def __ge__(self, other):
		if isinstance(other, AggressivePostureType):
			return self._value >= other._value

		raise Exception(f'cannot compare AggressivePostureType and {type(other)}')

	@classmethod
	def fromValue(cls, value: int) -> AggressivePostureType:
		for posture in list(AggressivePostureType):
			if value == posture.value():
				return posture

		return AggressivePostureType.none


class LeaderAgendaType(ExtendedEnum):
	pass


class StrengthType(ExtendedEnum):
	pathetic = 0, 'pathetic'  # STRENGTH_PATHETIC
	weak = 1, 'weak'  # STRENGTH_WEAK
	poor = 2, 'poor'  # STRENGTH_POOR
	average = 3, 'average'  # STRENGTH_AVERAGE
	strong = 4, 'strong'  # STRENGTH_STRONG
	powerful = 5, 'powerful'  # STRENGTH_POWERFUL
	immense = 6, 'immense'  # STRENGTH_IMMENSE

	def __new__(cls, value, name):
		member = object.__new__(cls)
		member._value = value
		member._name = name
		return member

	def __ge__(self, other):
		if isinstance(other, StrengthType):
			return self._value >= other._value

		raise Exception(f'Cannot compare StrengthType and {type(other)}')


class PlayerWarStateType(ExtendedEnum):
	none = -1, 'none'

	offensive = 0, 'offensive'
	nearlyDefeated = 1, 'nearlyDefeated'
	defensive = 2, 'defensive'
	calm = 3, 'calm'
	nearlyWon = 4, 'nearlyWon'
	stalemate = 5, 'stalemate'

	def __new__(cls, value, name):
		member = object.__new__(cls)
		member._value = value
		member._name = name
		return member

	def name(self) -> str:
		return self._name

	def __lt__(self, other):
		if isinstance(other, PlayerWarStateType):
			# if self == PlayerWarStateType.none or other == PlayerWarStateType.none:
			#	raise InvalidEnumError(self)

			return self._value < other._value

		raise Exception(f'cannot compare PlayerWarStateType and {type(other)}')

	def __le__(self, other):
		if isinstance(other, PlayerWarStateType):
			if self == PlayerWarStateType.none or other == PlayerWarStateType.none:
				raise InvalidEnumError(self)

			return self._value <= other._value

		raise Exception(f'cannot compare PlayerWarStateType and {type(other)}')
