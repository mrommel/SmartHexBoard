import sys

from smarthexboard.smarthexboardlib.core.base import ExtendedEnum
from smarthexboard.smarthexboardlib.game.civilizations import LeaderType
from smarthexboard.smarthexboardlib.game.players import Player
from smarthexboard.smarthexboardlib.map.base import HexPoint, HexArea
from smarthexboard.smarthexboardlib.map.generation import OceanFinder, ContinentFinder, RegionFinder


class BaseSiteEvaluator:
	def __init__(self):
		pass

	def valueOfPoint(self, point: HexPoint, player) -> float:
		raise Exception('must be overloaded by sub class')

	def valueOfArea(self, area: HexArea, player) -> float:
		sumValue = 0.0

		for point in area:
			sumValue += self.valueOfPoint(point, player)

		return sumValue

	def bestPointOfArea(self, area: HexArea, player) -> (HexPoint, float):
		bestValue = sys.float_info.min
		bestPoint: HexPoint = area.first()

		for point in area:
			value = self.valueOfPoint(point, player)

			if value > bestValue:
				bestValue = value
				bestPoint = point

		return bestPoint, bestValue


class CitySiteEvaluationType(ExtendedEnum):
	freshWater = 'freshWater'
	coastalWater = 'coastalWater'
	noWater = 'noWater'
	tooCloseToAnotherCity = 'tooCloseToAnotherCity'
	invalidTerrain = 'invalidTerrain'


class TileFertilityEvaluator(BaseSiteEvaluator):
	def __init__(self, mapModel):
		super().__init__()
		self.mapModel = mapModel

	def valueOfPoint(self, point: HexPoint, player) -> float:
		tile = self.mapModel.tileAt(point)

		if tile is None:
			return 0.0

		#  FIXME improvements
		return tile.yields(player, ignoreFeature=False).food


class CitySiteEvaluator(BaseSiteEvaluator):

	minCityDistance = 2

	def __init__(self, mapModel):
		super().__init__()
		self.mapModel = mapModel
		self.tileFertilityEvaluator = TileFertilityEvaluator(mapModel)

	def canCityBeFoundOn(self, tile, player) -> bool:
		# check if tile is owned by another player
		if tile.owner() is not None:
			if not tile.owner() == player:
				return False

		# check if already found a city here
		if self.mapModel.cityAt(tile.point) is not None:
			return False

		# can't found on water
		if tile.terrain().isWater():
			return False

		# check for distance (cities inside the area)
		area = tile.point.areaWithRadius(self.minCityDistance)

		for areaPoint in area:
			if self.mapModel.cityAt(areaPoint) is not None:
				return False

		return True

	def valueOfPoint(self, point: HexPoint, player) -> float:
		tile = self.mapModel.tileAt(point)

		if not self.canCityBeFoundOn(tile, player):
			return 0

		area = point.areaWithRadius(self.minCityDistance)

		sumValue: float = 0.0
		for areaPoint in area:
			if self.mapModel.cityAt(areaPoint) is not None:
				continue

			sumValue += self.tileFertilityEvaluator.valueOfPoint(areaPoint, player)

		# if map.isAdjacentToRiver(at: point):
		#	sumValue *= 2

		# if map.isAdjacentToOcean(at: point):
		#	sumValue *= 2

		return sumValue


class MapAnalyzer:
	def __init__(self, mapModel):
		self.mapModel = mapModel

	def analyze(self):
		if len(self.mapModel.oceans) == 0:
			oceanFinder = OceanFinder(self.mapModel.width, self.mapModel.height)
			oceans = oceanFinder.executeOn(self.mapModel)
			self.mapModel.oceans = oceans

		if len(self.mapModel.continents) == 0:
			continentFinder = ContinentFinder(self.mapModel.width, self.mapModel.height)
			continents = continentFinder.executeOn(self.mapModel)
			self.mapModel.continents = continents

		if len(self.mapModel.areas) == 0:
			# dummy player
			player = Player(LeaderType.alexander)
			player.initialize()

			# map is divided into regions
			fertilityEvaluator = CitySiteEvaluator(self.mapModel)
			finder = RegionFinder(self.mapModel, fertilityEvaluator, player)
			areas = finder.divideInto(2)
			self.mapModel.areas = areas

			# set area to tile
			for area in self.mapModel.areas:
				for pt in area:
					tile = self.mapModel.tileAt(pt)
					tile._area = area

		self.mapModel.updateStatistics()
