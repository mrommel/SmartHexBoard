from smarthexboard.map.base import ExtendedEnum


class SpecialistType(ExtendedEnum):
	merchant = 'merchant'
	captain = 'captain'
	artist = 'artist'
	priest = 'priest'
	commander = 'commander'


class SpecialistSlots:
	def __init__(self, specialistType: SpecialistType, amount: int):
		self.specialistType = specialistType
		self.amount = amount