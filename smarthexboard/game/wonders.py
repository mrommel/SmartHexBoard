from typing import Optional

from smarthexboard.game.civics import CivicType
from smarthexboard.map.base import ExtendedEnum


class WonderTypeData:
	def __init__(self, name: str, requiredCivic: Optional[CivicType]):
		self.name = name
		self.requiredCivic = requiredCivic

class WonderType(ExtendedEnum):
	pyramids = 'pyramids'

	def name(self) -> str:
		return self._data().name

	def requiredCivic(self) -> Optional[CivicType]:
		return self._data().requiredCivic

	def _data(self) -> WonderTypeData:
		if self == WonderType.pyramids:
			return WonderTypeData(
				name='KEY_PYRAMIDS',
				requiredCivic=None
			)

		raise AttributeError(f'cant get data for wonder {self}')
