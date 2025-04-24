import re
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
	# '[HexPoint x: 14, y: 4]'
	for coord_str in re.findall(r'x: \d+, y: \d+', location):
		# print(f'coor: {coor}')
		coord_str = coord_str.replace('x: ', '')
		coord_str = coord_str.replace('y: ', '')

		location = coord_str

	location_parts = location.split(',')

	if len(location_parts) == 2:
		if not is_integer(location_parts[0].strip()):
			return None

		if not is_integer(location_parts[1].strip()):
			return None

		location: HexPoint = HexPoint(int(location_parts[0].strip()), int(location_parts[1].strip()))
		return location

	return None


def parseUnitMapType(unit_type: str) -> Optional[UnitMapType]:
	if unit_type == 'combat':
		return UnitMapType.combat

	if unit_type == 'civilian':
		return UnitMapType.civilian

	print(f'Warning: Unknown unit type "{unit_type}"')

	return None
