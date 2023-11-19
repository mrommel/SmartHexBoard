from smarthexboard.smarthexboardlib.core.base import ExtendedEnum, InvalidEnumError
from smarthexboard.smarthexboardlib.map.types import Yields


class SpecialistTypeData:
	def __init__(self, name: str, greatPeopleRateChange: int, yields: Yields):
		self.name = name
		self.greatPeopleRateChange = greatPeopleRateChange
		self.yields = yields


class SpecialistType(ExtendedEnum):
	none = 'none'

	citizen = 'citizen'

	artist = 'artist'
	scientist = 'scientist'
	merchant = 'merchant'
	captain = 'captain'
	priest = 'priest'
	commander = 'commander'
	engineer = 'engineer'

	def name(self) -> str:
		return self._data().name

	def greatPeopleRateChange(self) -> int:
		return self._data().greatPeopleRateChange

	def yields(self) -> Yields:
		return self._data().yields

	def _data(self) -> SpecialistTypeData:
		if self == SpecialistType.none:
			return SpecialistTypeData(
				name='None',
				greatPeopleRateChange=0,
				yields=Yields(food=0.0, production=0.0, gold=0.0)
			)

		elif self == SpecialistType.citizen:
			return SpecialistTypeData(
				name='Citizen',
				greatPeopleRateChange=0,
				yields=Yields(food=0.0, production=0.0, gold=0.0)
			)

		elif self == SpecialistType.artist:
			return SpecialistTypeData(
				name='Artist',
				greatPeopleRateChange=3,
				yields=Yields(food=0.0, production=0.0, gold=0.0, culture=2.0)
			)
		elif self == SpecialistType.scientist:
			return SpecialistTypeData(
				name='Scientist',
				greatPeopleRateChange=3,
				yields=Yields(food=0.0, production=0.0, gold=0.0, science=2.0)
			)
		elif self == SpecialistType.merchant:
			return SpecialistTypeData(
				name='Merchant',
				greatPeopleRateChange=3,
				yields=Yields(food=0.0, production=0.0, gold=2.0)
			)
		elif self == SpecialistType.engineer:
			return SpecialistTypeData(
				name='Engineer',
				greatPeopleRateChange=3,
				yields=Yields(food=0.0, production=2.0, gold=0.0)
			)
		elif self == SpecialistType.captain:
			return SpecialistTypeData(
				name='Captain',
				greatPeopleRateChange=3,
				yields=Yields(food=1.0, production=0.0, gold=2.0)
			)
		elif self == SpecialistType.commander:
			return SpecialistTypeData(
				name='Commander',
				greatPeopleRateChange=3,
				yields=Yields(food=0.0, production=1.0, gold=2.0)
			)
		elif self == SpecialistType.priest:
			return SpecialistTypeData(
				name='Priest',
				greatPeopleRateChange=3,
				yields=Yields(food=0.0, production=0.0, gold=0.0, faith=2.0)
			)

		raise InvalidEnumError(self)


class SpecialistSlots:
	def __init__(self, specialistType: SpecialistType, amount: int):
		self.specialistType = specialistType
		self.amount = amount
