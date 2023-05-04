from typing import Optional

from smarthexboard.game.civics import CivicType
from smarthexboard.map.base import ExtendedEnum


class PolicyCardType(ExtendedEnum):
	none = 'none'

	def requiredCivic(self) -> Optional[CivicType]:
		return None

	def requiresDarkAge(self) -> bool:
		return False
