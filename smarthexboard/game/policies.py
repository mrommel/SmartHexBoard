from typing import Optional

from smarthexboard.game.civics import CivicType
from smarthexboard.map.base import ExtendedEnum


class PolicyCardTypeData:
	def __init__(self, name: str, requiredCivic: Optional[CivicType], requiresDarkAge: bool):
		self.name = name
		self.requiredCivic = requiredCivic
		self.requiresDarkAge = requiresDarkAge


class PolicyCardType(ExtendedEnum):
	none = 'none'

	def requiredCivic(self) -> Optional[CivicType]:
		return self._data().requiredCivic

	def requiresDarkAge(self) -> bool:
		return self._data().requiresDarkAge

	def _data(self) -> PolicyCardTypeData:
		if self == PolicyCardType.none:
			return PolicyCardTypeData(
				name='KEY_NONE',
				requiredCivic=None,
				requiresDarkAge=False
			)

		raise AttributeError(f'cant get data for policy card {self}')

