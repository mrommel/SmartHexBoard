from smarthexboard.smarthexboardlib.core.base import ExtendedEnum, InvalidEnumError


class EnvoyEffectLevel(ExtendedEnum):
	first = 'first'
	third = 'third'
	sixth = 'sixth'
	suzerain = 'suzerain'

	def __str__(self):
		if self == EnvoyEffectLevel.first:
			return '1st Envoy'
		elif self == EnvoyEffectLevel.third:
			return '3rd Envoy'
		elif self == EnvoyEffectLevel.sixth:
			return '6th Envoy'
		elif self == EnvoyEffectLevel.suzerain:
			return 'Suzerain'

		raise InvalidEnumError(self)
