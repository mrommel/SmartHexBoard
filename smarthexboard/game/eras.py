from smarthexboard.map.base import ExtendedEnum


class EraType(ExtendedEnum):
	# default
	ancient = 'ancient'
	classical = 'classical'
	medieval = 'medieval'
	renaissance = 'renaissance'
	industrial = 'industrial'
	modern = 'modern'
	atomic = 'atomic'
	information = 'information'
	future = 'future'

	def name(self) -> str:
		if self == EraType.ancient:
			return _('TXT_KEY_ERA_ANCIENT')
		elif self == EraType.classical:
			return _('TXT_KEY_ERA_CLASSICAL')
		elif self == EraType.medieval:
			return _('TXT_KEY_ERA_MEDIEVAL')
		elif self == EraType.renaissance:
			return _('TXT_KEY_ERA_RENAISSANCE')
		elif self == EraType.industrial:
			return _('TXT_KEY_ERA_INDUSTRIAL')
		elif self == EraType.modern:
			return _('TXT_KEY_ERA_MODERN')
		elif self == EraType.atomic:
			return _('TXT_KEY_ERA_ATOMIC')
		elif self == EraType.information:
			return _('TXT_KEY_ERA_INFORMATION')
		elif self == EraType.future:
			return _('TXT_KEY_ERA_FUTURE')

		raise AttributeError(f'cant get name of {self}')