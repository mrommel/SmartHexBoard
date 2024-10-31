from typing import Optional
from uuid import UUID

from smarthexboard.smarthexboardlib.game.unitTypes import UnitMapType
from smarthexboard.smarthexboardlib.map.base import HexPoint


def is_valid_uuid(uuid_to_test, version=4):
	"""
	Check if uuid_to_test is a valid UUID.

	 Parameters
	----------
	uuid_to_test : str
	version : {1, 2, 3, 4}

	 Returns
	-------
	`True` if uuid_to_test is a valid UUID, otherwise `False`.

	 Examples
	--------
	>>> is_valid_uuid('c9bf9e57-1685-4c89-bafb-ff5af830be8a')
	True
	>>> is_valid_uuid('c9bf9e58')
	False
	"""

	try:
		uuid_obj = UUID(uuid_to_test, version=version)
	except ValueError:
		return False
	return str(uuid_obj) == uuid_to_test


def is_integer(n):
	try:
		float(n)
	except ValueError:
		return False
	else:
		return float(n).is_integer()


def parseLocation(location: str) -> Optional[HexPoint]:
	location_parts = location.split(',')

	if len(location_parts) == 2:
		if not is_integer(location_parts[0]):
			return None

		if not is_integer(location_parts[1]):
			return None

		location: HexPoint = HexPoint(int(location_parts[0]), int(location_parts[1]))
		return location

	return None


def parseUnitMapType(unit_type: str) -> Optional[UnitMapType]:
	if unit_type == 'combat':
		return UnitMapType.combat

	if unit_type == 'civilian':
		return UnitMapType.civilian

	return None
