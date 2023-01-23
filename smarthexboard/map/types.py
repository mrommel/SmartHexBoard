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


class MapAge(Enum):
	young = 'young'
	normal = 'normal'
	old = 'old'


class Yields:
	def __init__(self, food, production, gold, science=0, culture=0, faith=0):
		self.food = food
		self.production = production
		self.gold = gold
		self.science = science
		self.culture = culture
		self.faith = faith


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

	def isWater(self):
		return self == TerrainType.sea or self == TerrainType.ocean or self == TerrainType.shore

	def isLand(self):
		return not self.isWater()

	def movementCost(self, movement_type):
		if movement_type == MovementType.immobile:
			return MovementType.max

		if movement_type == MovementType.swim:
			if self == TerrainType.ocean:
				return 1.5

			if self == TerrainType.shore:
				return 1.0

			return MovementType.max

		if movement_type == MovementType.swimShallow:
			if self == TerrainType.shore:
				return 1.0

			return MovementType.max

		if movement_type == MovementType.walk:
			if self == TerrainType.plains:
				return 1.0

			if self == TerrainType.grass:
				return 1.0

			if self == TerrainType.desert:
				return 1.0

			if self == TerrainType.tundra:
				return 1.0

			if self == TerrainType.snow:
				return 1.0

			return MovementType.max


class FeatureData:
	def __init__(self, name, yields, is_wonder):
		self.name = name
		self.yields = yields
		self.is_wonder = is_wonder


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
	lake = 'lake'
	volcano = 'volcano'

	# natural wonder
	mountEverest = 'mountEverest'
	mountKilimanjaro = 'mountEverest'

	def data(self):
		if self == FeatureType.none:
			return FeatureData('None', Yields(0, 0, 0), False)
		if self == FeatureType.forest:
			return FeatureData('Forest', Yields(0, 1, 0), False)
		elif self == FeatureType.rainforest:
			return FeatureData('Rainforest', Yields(1, 0, 0), False)
		elif self == FeatureType.floodplains:
			return FeatureData('Floodplains', Yields(3, 0, 0), False)
		elif self == FeatureType.marsh:
			return FeatureData('Marsh', Yields(3, 0, 0), False)
		elif self == FeatureType.oasis:
			return FeatureData("Oasis", Yields(1, 0, 0), False)
		elif self == FeatureType.reef:
			return FeatureData("Reef", Yields(1, 0, 0), False)
		elif self == FeatureType.ice:
			return FeatureData("Ice", Yields(0, 0, 0), False)
		elif self == FeatureType.atoll:
			return FeatureData("Atoll", Yields(1, 0, 0), False)
		elif self == FeatureType.volcano:
			return FeatureData("Volcano", Yields(0, 0, 0), False)
		elif self == FeatureType.mountains:
			return FeatureData("Mountains", Yields(0, 0, 0), False)
		elif self == FeatureType.lake:
			return FeatureData("Lake", Yields(0, 0, 0), False)
		elif self == FeatureType.fallout:
			return FeatureData("Fallout", Yields(-3, -3, -3), False)

		raise AttributeError(f'FeatureType.data: {self} not handled!')
		# return FeatureData('None', Yields(0, 0, 0), False)

	def movementCost(self, movement_type):
		if movement_type == MovementType.immobile:
			return MovementType.max

		if movement_type == MovementType.swim:
			return MovementType.max  # this means that no unit can enter water features

		if movement_type == MovementType.swimShallow:
			return self.movementCosts()

		if movement_type == MovementType.walk:
			return self.movementCosts()

	def movementCosts(self):
		if self == FeatureType.forest:
			return 2
		elif self == FeatureType.rainforest:
			return 2
		elif self == FeatureType.floodplains:
			return 0
		elif self == FeatureType.marsh:
			return 2
		elif self == FeatureType.oasis:
			return 0
		elif self == FeatureType.reef:
			return 2
		elif self == FeatureType.ice:
			return MovementType.max
		elif self == FeatureType.atoll:
			return 2
		elif self == FeatureType.volcano:
			return MovementType.max
		elif self == FeatureType.mountains:
			return 2  # ???
		elif self == FeatureType.lake:
			return MovementType.max
		elif self == FeatureType.fallout:
			return 2

		return MovementType.max

	def isPossibleOn(self, tile):
		if self == FeatureType.forest: 
			return self._isForestPossibleOn(tile)
		elif self == FeatureType.rainforest: 
			return self._isRainforestPossibleOn(tile)
		elif self == FeatureType.floodplains: 
			return self._isFloodplainsPossibleOn(tile)
		elif self == FeatureType.marsh: 
			return self._isMarshPossibleOn(tile)
		elif self == FeatureType.oasis: 
			return self._isOasisPossibleOn(tile)
		elif self == FeatureType.reef: 
			return self._isReefPossibleOn(tile)
		elif self == FeatureType.ice: 
			return self._isIcePossibleOn(tile)
		elif self == FeatureType.atoll: 
			return self._isAtollPossibleOn(tile)
		elif self == FeatureType.volcano: 
			return self._isVolcanoPossibleOn(tile)
		#
		elif self == FeatureType.mountains: 
			return self._isMountainPossibleOn(tile)
		elif self == FeatureType.lake: 
			return self._isLakePossibleOn(tile)
		elif self == FeatureType.fallout: 
			return self._isFalloutPossibleOn(tile)

		return False

	def _isForestPossibleOn(self, tile):
		"""Grassland, Grassland (Hills), Plains, Plains (Hills), Tundra and Tundra (Hills)."""
		if tile.terrain == TerrainType.tundra or tile.terrain == TerrainType.grass or tile.terrain == TerrainType.plains:
			return True

		return False

	def _isRainforestPossibleOn(self, tile):
		"""Modifies Plains and Plains (Hills)."""
		if tile.terrain == TerrainType.plains:
			return True

		return False

	def _isFloodplainsPossibleOn(self, tile):
		"""Modifies Deserts and also Plains and Grassland."""
		if tile.hasHills():
			return False

		if tile.terrain != TerrainType.desert and tile.terrain != TerrainType.grass and tile.terrain != TerrainType.plains:
			return False

		return True

	def _isMarshPossibleOn(self, tile):
		if tile.hasHills():
			return False

		if tile.terrain != TerrainType.grass:
			return False

		return True

	def _isOasisPossibleOn(self, tile):
		if tile.hasHills():
			return False

		if tile.terrain != TerrainType.desert:
			return False

		return True

	def _isReefPossibleOn(self, tile):
		if not tile.isWater():
			return False

		if tile.terrain != TerrainType.shore:
			return False

		return True

	def _isIcePossibleOn(self, tile):
		if not tile.isWater():
			return False

		return True

	def _isAtollPossibleOn(self, tile):
		if not tile.isWater():
			return False

		return True

	def _isVolcanoPossibleOn(self, tile):
		if tile.feature != FeatureType.mountains:
			return False

		return True

	def _isMountainPossibleOn(self, tile):
		if tile.hasHills():
			return False

		if tile.terrain == TerrainType.desert or tile.terrain == TerrainType.grass or tile.terrain == TerrainType.plains or tile.terrain == TerrainType.tundra or tile.terrain == TerrainType.snow:
			return True

		return False

	def _isLakePossibleOn(self, tile):
		if tile.hasHills():
			return False

		return True

	def _isFalloutPossibleOn(self, tile):
		if tile.isWater():
			return False

		return True

	def isNaturalWonder(self):
		return self.data().is_wonder


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


class MovementType(ExtendedEnum):
	immobile = 'immobile'
	walk = 'walk'
	swim = 'swim'
	swimShallow = 'swimShallow'

	max = 1000


class RouteType(ExtendedEnum):
	none = 'none'
	ancientRoad = 'ancientRoad'
	classicalRoad = 'classicalRoad'
	industrialRoad = 'industrialRoad'
	modernRoad = 'modernRoad'

	def movementCost(self):
		if self == RouteType.none:
			return 200
		elif self == RouteType.ancientRoad:
			# Starting road, well-packed dirt. Most terrain costs 1 MP; crossing rivers still costs 3 MP.
			return 1
		elif self == RouteType.classicalRoad:
			# Adds bridges over rivers; crossing costs reduced to only 1 MP.
			return 1
		elif self == RouteType.industrialRoad:
			# Paved roads are developed; 0.75 MP per tile.
			return 0.75
		elif self == RouteType.modernRoad:
			# Asphalted roads are developed; 0.50 MP per tile.
			return 0.5
