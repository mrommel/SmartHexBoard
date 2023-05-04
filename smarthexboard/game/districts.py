from typing import Optional

from smarthexboard.game.civics import CivicType
from smarthexboard.map.base import ExtendedEnum


class DistrictTypeData:
	def __init__(self, name: str, requiredCivic: Optional[CivicType]):
		self.name = name
		self.requiredCivic = requiredCivic


class DistrictType(ExtendedEnum):
	none = 'none'

	cityCenter = 'cityCenter'
	preserve = 'preserve'
	encampment = 'encampment'
	campus = 'campus'
	entertainmentComplex = 'entertainmentComplex'
	commercialHub = 'commercialHub'
	holySite = 'holySite'
	harbor = 'harbor'

	def name(self) -> str:
		return self._data().name

	def requiredCivic(self) -> Optional[CivicType]:
		return self._data().requiredCivic

	def _data(self) -> DistrictTypeData:
		if self == DistrictType.none:
			return DistrictTypeData(
				name='KEY_NAME_NONE',
				requiredCivic=None
			)
		elif self == DistrictType.cityCenter:
			return DistrictTypeData(
				name='KEY_NAME_CITY_CENTER',
				requiredCivic=None
			)
		elif self == DistrictType.preserve:
			return DistrictTypeData(
				name='KEY_NAME_CITY_CENTER',
				requiredCivic=None
			)
		elif self == DistrictType.encampment:
			return DistrictTypeData(
				name='KEY_NAME_CITY_CENTER',
				requiredCivic=None
			)
		elif self == DistrictType.campus:
			return DistrictTypeData(
				name='KEY_NAME_CITY_CENTER',
				requiredCivic=None
			)
		elif self == DistrictType.entertainmentComplex:
			return DistrictTypeData(
				name='KEY_NAME_CITY_CENTER',
				requiredCivic=None
			)
		elif self == DistrictType.commercialHub:
			return DistrictTypeData(
				name='KEY_NAME_CITY_CENTER',
				requiredCivic=None
			)
		elif self == DistrictType.holySite:
			return DistrictTypeData(
				name='KEY_NAME_CITY_CENTER',
				requiredCivic=None
			)
		elif self == DistrictType.harbor:
			return DistrictTypeData(
				name='KEY_NAME_CITY_CENTER',
				requiredCivic=None
			)

		raise AttributeError(f'cant get data for distrct {self}')