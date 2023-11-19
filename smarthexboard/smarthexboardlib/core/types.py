from smarthexboard.smarthexboardlib.core.base import ExtendedEnum
from smarthexboard.smarthexboardlib.utils.translation import gettext_lazy as _


class EraTypeData:
	def __init__(self, name: str, nextEra, formalWarWeariness: int, surpriseWarWeariness: int):
		self.name = name
		self.nextEra = nextEra
		self.formalWarWeariness = formalWarWeariness
		self.surpriseWarWeariness = surpriseWarWeariness


class EraType:
	pass


class EraType(ExtendedEnum):
	# default
	ancient = 0, 'ancient'
	classical = 1, 'classical'
	medieval = 2, 'medieval'
	renaissance = 3, 'renaissance'
	industrial = 4, 'industrial'
	modern = 5, 'modern'
	atomic = 6, 'atomic'
	information = 7, 'information'
	future = 8, 'future'

	def __new__(cls, value, name):
		member = object.__new__(cls)
		member._value = value
		member._name = name
		return member

	def title(self) -> str:  # cannot be 'name'
		return self._data().name

	def value(self) -> int:
		return int(str(self._value))

	def __le__(self, other):
		if isinstance(other, EraType):
			return self._value <= other._value

		raise Exception('cannot compare EraType to other type')

	def __lt__(self, other):
		if isinstance(other, EraType):
			return self._value < other._value

		raise Exception('cannot compare EraType to other type')

	def warWearinessValue(self, formal: bool) -> int:
		return self._data().formalWarWeariness if formal else self._data().surpriseWarWeariness
	
	def next(self) -> EraType:
		return self._data().nextEra

	def _data(self) -> EraTypeData:
		if self == EraType.ancient:
			return EraTypeData(
				name=_('TXT_KEY_ERA_ANCIENT'),
				nextEra=EraType.classical,
				formalWarWeariness=16,
				surpriseWarWeariness=16
			)
		elif self == EraType.classical:
			return EraTypeData(
				name=_('TXT_KEY_ERA_CLASSICAL'),
				nextEra=EraType.medieval,
				formalWarWeariness=22,
				surpriseWarWeariness=25
			)
		elif self == EraType.medieval:
			return EraTypeData(
				name=_('TXT_KEY_ERA_MEDIEVAL'),
				nextEra=EraType.renaissance,
				formalWarWeariness=28,
				surpriseWarWeariness=34
			)
		elif self == EraType.renaissance:
			return EraTypeData(
				name=_('TXT_KEY_ERA_RENAISSANCE'),
				nextEra=EraType.industrial,
				formalWarWeariness=34,
				surpriseWarWeariness=43
			)
		elif self == EraType.industrial:
			return EraTypeData(
				name=_('TXT_KEY_ERA_INDUSTRIAL'),
				nextEra=EraType.modern,
				formalWarWeariness=40,
				surpriseWarWeariness=52
			)
		elif self == EraType.modern:
			return EraTypeData(
				name=_('TXT_KEY_ERA_MODERN'),
				nextEra=EraType.atomic,
				formalWarWeariness=40,
				surpriseWarWeariness=52
			)
		elif self == EraType.atomic:
			return EraTypeData(
				name=_('TXT_KEY_ERA_ATOMIC'),
				nextEra=EraType.information,
				formalWarWeariness=40,
				surpriseWarWeariness=52
			)
		elif self == EraType.information:
			return EraTypeData(
				name=_('TXT_KEY_ERA_INFORMATION'),
				nextEra=EraType.future,
				formalWarWeariness=40,
				surpriseWarWeariness=52
			)
		elif self == EraType.future:
			return EraTypeData(
				name=_('TXT_KEY_ERA_FUTURE'),
				nextEra=EraType.future,
				formalWarWeariness=40,
				surpriseWarWeariness=52
			)

		raise AttributeError(f'cant get name of {self}')
