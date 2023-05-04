from typing import Optional

from smarthexboard.game.civics import CivicType
from smarthexboard.map.base import ExtendedEnum


class GovernmentTypeData:
	def __init__(self, name: str, requiredCivic: Optional[CivicType]):
		self.name = name
		self.requiredCivic = requiredCivic


class GovernmentType(ExtendedEnum):
	none = 'none'

	chiefdom = 'chiefdom'

	def name(self) -> str:
		return ''

	def requiredCivic(self) -> Optional[CivicType]:
		return None

	def _data(self) -> GovernmentTypeData:
		if self == GovernmentType.none:
			return GovernmentTypeData(
				name='KEY_NONE',
				requiredCivic=None
			)
		elif self == GovernmentType.chiefdom:
			return GovernmentTypeData(
				name='KEY_CHIEF',
				requiredCivic=None
			)
		raise AttributeError(f'cant get data for government {self}')