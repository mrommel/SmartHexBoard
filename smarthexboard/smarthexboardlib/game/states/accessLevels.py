from smarthexboard.smarthexboardlib.core.base import ExtendedEnum, InvalidEnumError
from smarthexboard.smarthexboardlib.utils.translation import gettext_lazy as _


class AccessLevel:
	pass


class AccessLevelData:
	def __init__(self, name: str, increased: AccessLevel, decreased: AccessLevel):
		self.name = name
		self.increased = increased
		self.decreased = decreased


class AccessLevel(ExtendedEnum):
	none = -1, 'none'

	limited = 0, 'limited'
	open = 1, 'open'
	secret = 2, 'secret'
	topSecret = 3, 'topSecret'

	def __new__(cls, value, name):
		member = object.__new__(cls)
		member._value = value
		member._name = name
		return member

	def name(self) -> str:
		return self._data().name

	def increased(self):
		return self._data().increased

	def decreased(self):
		return self._data().decreased

	def __gt__(self, other):
		if isinstance(other, AccessLevel):
			return self._value > other._value

		return False

	def _data(self) -> AccessLevelData:
		if self == AccessLevel.none:
			return AccessLevelData(
				name=_("TXT_KEY_ACCESS_LEVEL_NONE_NAME"),
				increased=AccessLevel.limited,
				decreased=AccessLevel.none
			)
		elif self == AccessLevel.limited:
			return AccessLevelData(
				name=_("TXT_KEY_ACCESS_LEVEL_LIMITED_NAME"),
				increased=AccessLevel.open,
				decreased=AccessLevel.none
			)
		elif self == AccessLevel.open:
			return AccessLevelData(
				name=_("TXT_KEY_ACCESS_LEVEL_OPEN_NAME"),
				increased=AccessLevel.secret,
				decreased=AccessLevel.limited
			)
		elif self == AccessLevel.secret:
			return AccessLevelData(
				name=_("TXT_KEY_ACCESS_LEVEL_SECRET_NAME"),
				increased=AccessLevel.topSecret,
				decreased=AccessLevel.open
			)
		elif self == AccessLevel.topSecret:
			return AccessLevelData(
				name=_("TXT_KEY_ACCESS_LEVEL_TOP_SECRET_NAME"),
				increased=AccessLevel.topSecret,
				decreased=AccessLevel.secret
			)

		raise InvalidEnumError(self)
