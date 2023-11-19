from smarthexboard.smarthexboardlib.core.base import ExtendedEnum, InvalidEnumError


class AgeThresholds:
	def __init__(self, lower: int, upper: int):
		self.lower = lower
		self.upper = upper


class AgeTypeData:
	def __init__(self, name: str, loyalityFactor: float, loyalityEffect: str, numDedicationsSelectable: int):
		self.name = name
		self.loyalityFactor = loyalityFactor
		self.loyalityEffect = loyalityEffect
		self.numDedicationsSelectable = numDedicationsSelectable


class AgeType(ExtendedEnum):
	normal = 'normal'
	golden = 'golden'
	dark = 'dark'
	heroic = 'heroic'

	def title(self) -> str:  # cannot be 'name
		return self._data().name

	def _data(self) -> AgeTypeData:
		if self == AgeType.normal:
			return AgeTypeData(
				name="TXT_KEY_AGE_NORMAL_NAME",
                loyalityFactor=1.0,
                loyalityEffect="TXT_KEY_AGE_NORMAL_LOYALTY",
                numDedicationsSelectable=1
			)
		elif self == AgeType.golden:
			return AgeTypeData(
				name="TXT_KEY_AGE_GOLDEN_NAME",
                loyalityFactor=1.5,
                loyalityEffect="TXT_KEY_AGE_GOLDEN_LOYALTY",
                numDedicationsSelectable=1
			)
		elif self == AgeType.dark:
			return AgeTypeData(
				name='TXT_KEY_AGE_DARK_NAME',
				loyalityFactor=0.5,
				loyalityEffect="TXT_KEY_AGE_DARK_LOYALTY",
				numDedicationsSelectable=1
			)
		elif self == AgeType.heroic:
			return AgeTypeData(
				name="TXT_KEY_AGE_HEROIC_NAME",
				loyalityFactor=1.5,
				loyalityEffect="TXT_KEY_AGE_HEROIC_LOYALTY",
				numDedicationsSelectable=3
			)

		raise InvalidEnumError(self)

	def loyalityFactor(self):
		return self._data().loyalityFactor

	def numDedicationsSelectable(self) -> int:
		return self._data().numDedicationsSelectable
	