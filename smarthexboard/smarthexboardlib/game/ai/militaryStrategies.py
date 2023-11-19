from smarthexboard.smarthexboardlib.core.base import ExtendedEnum, InvalidEnumError
from smarthexboard.smarthexboardlib.game.ai.baseTypes import MilitaryStrategyType


class ReconStateType(ExtendedEnum):
	needed = 'needed'  # RECON_STATE_NEEDED
	neutral = 'neutral'  # RECON_STATE_NEUTRAL;
	enough = 'enough'  # RECON_STATE_ENOUGH


class MilitaryStrategyAdoptionItem:
	def __init__(self, militaryStrategyType: MilitaryStrategyType, adopted: bool, turnOfAdoption: int):
		self.militaryStrategyType = militaryStrategyType
		self.adopted = adopted
		self.turnOfAdoption = turnOfAdoption


class MilitaryStrategyAdoptions:
	def __init__(self):
		self.adoptions = []

		for militaryStrategyType in list(MilitaryStrategyType):
			self.adoptions.append(MilitaryStrategyAdoptionItem(militaryStrategyType, False, -1))

	def adopted(self, militaryStrategyType: MilitaryStrategyType) -> bool:
		item = next((adoptionItem for adoptionItem in self.adoptions if
		             adoptionItem.militaryStrategyType == militaryStrategyType), None)

		if item is not None:
			return item.adopted

		raise InvalidEnumError(militaryStrategyType)

	def turnOfAdoption(self, militaryStrategyType: MilitaryStrategyType) -> int:
		item = next((adoptionItem for adoptionItem in self.adoptions if
		             adoptionItem.militaryStrategyType == militaryStrategyType), None)

		if item is not None:
			return item.turnOfAdoption

		raise Exception()

	def adopt(self, militaryStrategyType: MilitaryStrategyType, turnOfAdoption: int):
		item = next((adoptionItem for adoptionItem in self.adoptions if
		             adoptionItem.militaryStrategyType == militaryStrategyType), None)

		if item is not None:
			item.adopted = True
			item.turnOfAdoption = turnOfAdoption
			return

		raise InvalidEnumError(militaryStrategyType)

	def abandon(self, militaryStrategyType: MilitaryStrategyType):
		item = next((adoptionItem for adoptionItem in self.adoptions if
		             adoptionItem.militaryStrategyType == militaryStrategyType), None)

		if item is not None:
			item.adopted = False
			item.turnOfAdoption = -1
			return

		raise InvalidEnumError(militaryStrategyType)

	def turnOfAdoptionOf(self, militaryStrategyType: MilitaryStrategyType) -> int:
		item = next((adoptionItem for adoptionItem in self.adoptions if
		             adoptionItem.militaryStrategyType == militaryStrategyType), None)

		if item is not None:
			return item.turnOfAdoption

		raise InvalidEnumError(militaryStrategyType)