from enum import Enum

from smarthexboard.map.base import Size, ExtendedEnum


class MapType(Enum):
	empty = 'empty'
	earth = 'earth'
	pangaea = 'pangaea'
	continents = 'continents'
	archipelago = 'archipelago'


class MapSize(Enum):
	duel = 'duel'
	tiny = 'tiny'
	small = 'small'
	standard = 'standard'

	def size(self) -> Size:
		if self == MapSize.duel:
			return Size(32, 22)
		elif self == MapSize.tiny:
			return Size(42, 32)
		elif self == MapSize.small:
			return Size(52, 42)
		else:  # standard
			return Size(62, 52)


class TerrainType(Enum):
	desert = 'desert'
	grass = 'grass'
	ocean = 'ocean'
	plains = 'plains'
	shore = 'shore'
	snow = 'snow'
	tundra = 'tundra'

	land = 'land'
	sea = 'sea'


class FeatureType(Enum):
	none = 'none'
	atoll = 'atoll'
	fallout = 'fallout'
	floodplains = 'floodplains'
	forest = 'forest'
	ice = 'ice'
	marsh = 'marsh'
	mountains = 'mountains'
	oasis = 'oasis'
	pine = 'pine'  # special case for pine forest
	rainforest = 'rainforest'
	reef = 'reef'


class ResourceType(Enum):
	none = 'none'
	aluminium = 'aluminium'
	antiquitySite = 'antiquitySite'
	banana = 'banana'
	cattle = 'cattle'
	citrus = 'citrus'
	coal = 'coal'
	fish = 'fish'
	oil = 'oil'
	sheep = 'sheep'
	whales = 'whales'
	wheat = 'wheat'


class ClimateZone(ExtendedEnum):
	polar = 'polar'
	sub_polar = 'sub_polar'
	temperate = 'temperate'
	sub_tropic = 'sub_tropic'
	tropic = 'tropic'

	def moderate(self):
		if self == ClimateZone.polar:
			return ClimateZone.sub_polar
		elif self == ClimateZone.sub_polar:
			return ClimateZone.temperate
		elif self == ClimateZone.temperate:
			return ClimateZone.sub_tropic
		elif self == ClimateZone.sub_tropic:
			return ClimateZone.tropic
		else:
			return ClimateZone.tropic
