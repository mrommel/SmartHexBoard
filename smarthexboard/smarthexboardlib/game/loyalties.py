from smarthexboard.smarthexboardlib.core.base import ExtendedEnum, InvalidEnumError


class LoyaltyState(ExtendedEnum):
	loyal = 'loyal'
	wavering = 'wavering'
	disloyal = 'disloyal'
	unrest = 'unrest'

	def title(self) -> str:
		if self == LoyaltyState.loyal:
			return "Loyal"
		elif self == LoyaltyState.wavering:
			return "Wavering"
		elif self == LoyaltyState.disloyal:
			return "Disloyal"
		elif self == LoyaltyState.unrest:
			return "Unrest"

		raise InvalidEnumError(self)

	def yieldPercentage(self) -> float:
		if self == LoyaltyState.loyal:
			return 0.0
		elif self == LoyaltyState.wavering:
			return -0.25
		elif self == LoyaltyState.disloyal:
			return -0.5
		elif self == LoyaltyState.unrest:
			return -1.0

		raise InvalidEnumError(self)
