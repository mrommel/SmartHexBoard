import logging
import math
import random
import sys
from typing import Optional

from smarthexboard.smarthexboardlib.game.cityStates import CityStateType
from smarthexboard.smarthexboardlib.game.civilizations import LeaderType
from smarthexboard.smarthexboardlib.game.unitTypes import BitArray
from smarthexboard.smarthexboardlib.map.areas import OceanType, ContinentType, Continent, Ocean
from smarthexboard.smarthexboardlib.map.base import HexPoint, HexDirection, Array2D, HexArea
from smarthexboard.smarthexboardlib.map.improvements import ImprovementType
from smarthexboard.smarthexboardlib.map.map import MapModel, Tile
from smarthexboard.smarthexboardlib.map.path_finding.finder import MoveTypeIgnoreUnitsOptions, MoveTypeIgnoreUnitsPathfinderDataSource, AStarPathfinder
from smarthexboard.smarthexboardlib.map.perlin_noise.perlinNoise import PerlinNoise
from smarthexboard.smarthexboardlib.map.types import TerrainType, MapType, MapAge, MapSize, ResourceType, ClimateZone, FeatureType, ResourceUsage, \
	UnitMovementType, StartLocation
from smarthexboard.smarthexboardlib.core.base import WeightedStringList
from smarthexboard.smarthexboardlib.utils.translation import gettext_lazy as _


# https://www.redblobgames.com/maps/terrain-from-noise/
class HeightMap(Array2D):
	def __init__(self, width: int, height: int, octaves: int = 4):
		super().__init__(width, height, 0.0)
		self.width = width
		self.height = height
		self._generate(octaves)
		self._normalize()

	def _generate(self, octaves: int):
		"""
			generates the heightmap based on the input parameters

			@param octaves: object
		"""

		noise1 = PerlinNoise(octaves=1 * octaves)
		noise2 = PerlinNoise(octaves=2 * octaves)
		noise3 = PerlinNoise(octaves=4 * octaves)
		noise4 = PerlinNoise(octaves=8 * octaves)

		for x in range(self.width):
			for y in range(self.height):
				nx = float(x) / float(self.width)
				ny = float(y) / float(self.height)

				value0 = 1.00 * noise1.noise([nx, ny])
				value1 = 0.50 * noise2.noise([nx, ny])
				value2 = 0.25 * noise3.noise([nx, ny])
				value3 = 0.125 * noise4.noise([nx, ny])

				value = math.fabs(value0 + value1 + value2 + value3)  # / 1.875

				self.values[y][x] = value

	def _normalize(self):
		min_value = 1000.0
		max_value = -1000.0

		for x in range(self.width):
			for y in range(self.height):
				min_value = min(min_value, self.values[y][x])
				max_value = max(max_value, self.values[y][x])

		for x in range(self.width):
			for y in range(self.height):
				self.values[y][x] = (self.values[y][x] - min_value) / (max_value - min_value)

	def findThresholdAbove(self, percentage):
		"""
			this function takes the complete height map into account for land only

			@param percentage: value to check
			@return: heightmap value where percentage is above
		"""
		tmp_array = []

		# fill from map
		for x in range(self.width):
			for y in range(self.height):
				tmp_array.append(self.values[y][x])

		# sorted smallest first, highest last
		tmp_array.sort()
		tmp_array.reverse()

		threshold_index = math.floor(len(tmp_array) * percentage)

		return tmp_array[threshold_index]


class ResourcesInfo:
	def __init__(self, resource: ResourceType, num_possible: int, already_placed: int):
		self.resource = resource
		self.num_possible = num_possible
		self.already_placed = already_placed


class MapOptions:
	def __init__(self, mapSize: MapSize, mapType: MapType, leader: LeaderType, aiLeaders=None):
		self.mapSize = mapSize
		self.mapType = mapType
		self.rivers = 20
		self.age = MapAge.normal
		self.leader = leader
		self.aiLeaders = [] if aiLeaders is None else aiLeaders

	def mountains_percentage(self):
		""" Percentage of mountain on land """
		if self.age == MapAge.young:
			return 0.08
		elif self.age == MapAge.normal:
			return 0.06
		elif self.age == MapAge.old:
			return 0.04

	def waterPercentage(self):
		""" abc """
		if self.mapType == MapType.empty:
			return 0.52  # fixme
		elif self.mapType == MapType.continents:
			return 0.52  # low
		elif self.mapType == MapType.earth:
			return 0.65
		elif self.mapType == MapType.pangaea:
			return 0.65
		elif self.mapType == MapType.archipelago:
			return 0.65
		#
		#         case .custom:
		#
		#             switch enhanced.sealevel {
		#
		#             case .low:
		#                 return 0.52
		#             case .normal:
		#                 return 0.65
		#             case .high:
		#                 return 0.81
		else:
			raise Exception(f'MapType not supported: {self.mapType}')

	def land_percentage(self):
		return 1.0 - self.waterPercentage()


class MapGeneratorState:
	def __init__(self, value, message):
		self.value = value
		self.message = message


class BaseSiteEvaluator:
	def __init__(self, map: MapModel):
		self.map = map

	def valueOfArea(self, area: HexArea, player) -> float:
		raise Exception('method must be overloaded')


class TileFertilityEvaluator(BaseSiteEvaluator):
	def __init__(self, map: MapModel):
		super().__init__(map)

	def placementFertility(self, tile: Tile, checkForCoastalLand: bool) -> float:
		plotFertility = 0

		# Measure Fertility - - Any cases absent from the process have a 0 value.
		if tile.feature() == FeatureType.mountains:  # Note, mountains cannot belong to a landmass AreaID, so they usually go unmeasured.
			plotFertility = 1  # mountains are better than ice because they allow special buildings and mine bonuses
		elif tile.feature() == FeatureType.forest:
			plotFertility = 4  # 2Y
		elif tile.feature() == FeatureType.rainforest:
			plotFertility = 3  # 1Y, but can be removed
		elif tile.feature() == FeatureType.marsh:
			plotFertility = 3  # 1Y, but can be removed
		elif tile.feature() == FeatureType.ice:
			plotFertility = -1  # useless
		elif tile.feature() == FeatureType.oasis:
			plotFertility = 6  # 4Y, but can't be improved (7 with fresh water bonus)
		elif tile.feature() == FeatureType.floodplains:
			plotFertility = 6  # 3Y (8 with river and fresh water bonuses)
		elif tile.terrain() == TerrainType.grass:
			plotFertility = 4  # 2Y
		elif tile.terrain() == TerrainType.plains:
			plotFertility = 4  # 2Y
		elif tile.terrain() == TerrainType.desert:
			plotFertility = 1  # 0Y
		elif tile.terrain() == TerrainType.tundra:
			plotFertility = 2  # 1Y
		elif tile.terrain() == TerrainType.snow:
			plotFertility = 1  # 0Y
		elif tile.terrain() == TerrainType.shore:
			plotFertility = 4  # 2Y
		elif tile.terrain() == TerrainType.ocean:
			plotFertility = 2  # 1Y

		if tile.isHills() and plotFertility == 1:
			plotFertility = 2  # hills give +1 production even on worthless terrains like desert and snow

		if tile.feature() == FeatureType.reef or tile.feature() == FeatureType.greatBarrierReef:
			plotFertility += 2  # +1 yield
		elif tile.feature() == FeatureType.atoll:
			plotFertility += 4  # +2 yields

		if self.map.riverAt(tile.point):
			plotFertility += 1

		if self.map.isFreshWaterAt(tile.point):
			plotFertility += 1

		if checkForCoastalLand:
			# When measuring only one AreaID, this shortcut helps account for coastal plots not measured.
			if self.map.isCoastalAt(tile.point) and tile.feature() != FeatureType.mountains:
				plotFertility += 2

		return plotFertility


class StartArea:
	def __init__(self, area: HexArea, fertility: float, used: bool = False):
		self.area = area
		self.fertility = fertility
		self.used = used


class StartPositioner:
	def __init__(self, mapModel, numberOfPlayers: int, numberOfCityStates: int):
		self.mapModel = mapModel
		self.numberOfPlayers = numberOfPlayers
		self.numberOfCityStates = numberOfCityStates

		# internal
		self.tileFertilityEvaluator = TileFertilityEvaluator(self.mapModel)
		self.startAreas = []
		self.fertilityMap = Array2D(self.mapModel.width, self.mapModel.height)

		# result
		self.startLocations = []
		self.cityStateStartLocations = []

	def generateRegions(self):
		logging.info(f'starting with: {self.numberOfPlayers} civs and {self.numberOfCityStates} city states')

		self.fertilityMap.fill(0)

		landAreaFert = WeightedStringList()

		# Obtain info on all landmasses for comparison purposes.
		globalFertilityOfLands = 0
		numberOfLandPlots = 0

		# Cycle through all plots in the world, checking their Start Placement Fertility and AreaID.
		for x in range(self.mapModel.width):
			for y in range(self.mapModel.height):
				tile = self.mapModel.tileAt(x, y)
				if tile is not None:
					# Land plot, process it.
					if tile.terrain().isLand():
						numberOfLandPlots += 1
						continentIdentifier = tile.continentIdentifier

						# Check for coastal land is enabled.
						plotFertility = self.tileFertilityEvaluator.placementFertility(tile, checkForCoastalLand=True)
						globalFertilityOfLands += plotFertility

						self.fertilityMap.values[y][x] = plotFertility
						landAreaFert.addWeight(plotFertility, continentIdentifier)

		# init number of civs on each continent
		numberOfCivsPerArea = WeightedStringList()

		for landAreaFertKey, _ in landAreaFert.items():
			numberOfCivsPerArea.setWeight(0.0, landAreaFertKey)

		# Assign continents to receive start plots.Record number of civs assigned to each landmass.
		for _ in range(self.numberOfPlayers + self.numberOfCityStates):
			bestRemainingAreaIdentifier: str = "---"
			bestRemainingFertility = 0.0

			# Loop through areas, find the one with the best remaining fertility (civs added
			# to a landmass reduces its fertility rating for subsequent civs).
			for areaItemKey, areaItemValue in landAreaFert.items():

				thisLandmassCurrentFertility = areaItemValue / (1 + numberOfCivsPerArea.weight(areaItemKey))

				if thisLandmassCurrentFertility > bestRemainingFertility:
					bestRemainingAreaIdentifier = areaItemKey
					bestRemainingFertility = thisLandmassCurrentFertility

			# Record results for this pass.(A landmass has been assigned to receive one more start point than it previously had).
			numberOfCivsPerArea.addWeight(1.0, bestRemainingAreaIdentifier)

		for numberOfCivsPerAreaKey, numberOfCivsPerAreaValue in numberOfCivsPerArea.items():
			numberOfCivsOnCurrentArea = int(numberOfCivsPerAreaValue)

			if numberOfCivsOnCurrentArea <= 0:
				continue

			logging.info(f'numberOfCivsOnCurrentArea: {numberOfCivsOnCurrentArea} on continent {numberOfCivsPerAreaKey}')
			continent = self.mapModel.continent(numberOfCivsPerAreaKey)
			if continent is not None:
				area = HexArea(continent.points, 0)

				# Divide this landmass into a number of regions equal to civs assigned here.
				if 0 < numberOfCivsOnCurrentArea <= 12:
					self.divideIntoRegions(int(numberOfCivsPerAreaValue), area)

		self.startAreas = sorted(self.startAreas, key=lambda startArea: len(startArea.area.points()),
								 reverse=True)  # by: { $0.area.points.count > $1.area.points.count})

		# debug
		logging.info("stats")
		logging.info(f'  number of land plots: {numberOfLandPlots}')
		logging.info(f'  global fertility of land plots: {globalFertilityOfLands}')
		logging.info("  start areas")
		for startArea in self.startAreas:
			logging.info(f'  - start era: {startArea.area.boundingBox()} / {len(startArea.area.points())} points')

		logging.info("----")

	def chooseLocations(self, aiLeaders, human):
		combined: [LeaderType] = aiLeaders
		combined.append(human)
		random.shuffle(combined)

		for leader in combined:
			logging.debug(f'choose location for {leader.title()}')
			civ = leader.civilization()

			bestArea: Optional[StartArea] = None
			bestValue: int = 0
			bestLocation: HexPoint = HexPoint(0, 0)

			# find best spot for civ in all areas
			for startArea in self.startAreas:
				if startArea.used:
					continue

				logging.debug(f'evaluate area with {len(startArea.area.points())} points')

				for startPoint in startArea.area.points():
					smallestDistanceOther = min(
						list(map(lambda n: startPoint.distance(n.location), self.startLocations)), default=10000)

					if smallestDistanceOther < 8:
						continue

					valueSum: int = 0
					for loopPoint in startPoint.areaWithRadius(2):
						if not self.mapModel.valid(loopPoint):
							continue

						tile = self.mapModel.tileAt(loopPoint)

						tileValue: int = 0
						# count center 3 times
						if loopPoint == startPoint:
							tileValue += 3 * self.fertilityMap.values[tile.point.y][tile.point.x]
							tileValue += 3 * civ.startingBias(tile, self.mapModel)
						else:
							tileValue += self.fertilityMap.values[tile.point.y][tile.point.x]
							tileValue += civ.startingBias(tile, self.mapModel)

						valueSum += tileValue
						# logging.debug("value of \(tile.point) => \(tileValue)")

					if valueSum > bestValue:
						bestValue = valueSum
						bestLocation = startPoint
						bestArea = startArea
						logging.debug(f'new best location: {bestLocation} - {bestValue}')

			# remove current start area
			self.startAreas = list(
				filter(lambda area: area.area.identifier != bestArea.area.identifier, self.startAreas))

			# sanity check - should restart guard
			if bestLocation == HexPoint(0, 0):
				raise Exception("Can't find valid start location")

			self.startLocations.append(StartLocation(bestLocation, leader, cityState=None, isHuman=leader == human))

		# sort human to the end
		self.startLocations = sorted(self.startLocations, key=lambda loc: 1 if loc.isHuman else 0)

		# debug
		# logging.debug(self.startLocations)
		allLeaders = aiLeaders
		allLeaders.append(human)

		for leader in allLeaders:
			leaderPos = next((pos for pos in self.startLocations if pos.leader == leader), None)
			leaderType = "human" if leaderPos.isHuman else "ai"
			logging.info(f'- {leader} ({leaderType}) has start position {leaderPos.location}')

			for leader2 in allLeaders:
				if leader == leader2:
					continue

				leader2Pos = next((pos for pos in self.startLocations if pos.leader == leader2), None)
				distance = leaderPos.location.distance(leader2Pos.location)
				logging.debug(f'   - distance: {distance} to {leader2}')

	def divideIntoRegions(self, numberOfDivisions: int, area: HexArea):
		numDivides = 0
		subDivisions = 0

		if numberOfDivisions == 1:
			averageFertility = 2.0  # float(area.points.map({self.fertilityMap[$0]!}).reduce(0, +)) / Double(len(area.points)
			self.startAreas.append(StartArea(area, averageFertility, False))
			return
		elif numberOfDivisions == 2:
			numDivides = 2
			subDivisions = 1
		elif numberOfDivisions == 3:
			numDivides = 3
			subDivisions = 1
		elif numberOfDivisions == 4:
			numDivides = 2
			subDivisions = 2
		elif numberOfDivisions == 5 or numberOfDivisions == 6:
			numDivides = 3
			subDivisions = 2
		elif numberOfDivisions == 7 or numberOfDivisions == 8:
			numDivides = 2
			subDivisions = 4
		elif numberOfDivisions == 9:
			numDivides = 3
			subDivisions = 3
		elif numberOfDivisions == 10:
			numDivides = 2
			subDivisions = 5
		elif numberOfDivisions == 11 or numberOfDivisions == 12:
			numDivides = 3
			subDivisions = 4
		else:
			raise Exception(f'Erroneous number of regional divisions : {numberOfDivisions}')

		if numDivides == 2:
			# area1, area2: HexArea
			boundingBox = area.boundingBox()

			if boundingBox.width() > boundingBox.height():
				midX = area.center().x
				(area1, area2) = area.divideHorizontally(midX)
			else:
				midY = area.center().y
				(area1, area2) = area.divideVertically(midY)

			self.divideIntoRegions(subDivisions, area1)
			self.divideIntoRegions(subDivisions, area2)
		elif numDivides == 3:
			# area1, area2, area3, areaTmp: HexArea
			boundingBox = area.boundingBox()

			if boundingBox.width() > boundingBox.height():
				(area1, areaTmp) = area.divideHorizontally(boundingBox.minX + boundingBox.width() / 3)
				(area2, area3) = areaTmp.divideHorizontally(boundingBox.minX + 2 * boundingBox.width() / 3)
			else:
				(area1, areaTmp) = area.divideVertically(boundingBox.minY + boundingBox.height() / 3)
				(area2, area3) = areaTmp.divideVertically(boundingBox.minY + 2 * boundingBox.height() / 3)

			self.divideIntoRegions(subDivisions, area1)
			self.divideIntoRegions(subDivisions, area2)
			self.divideIntoRegions(subDivisions, area3)
		else:
			raise Exception("wrong number of sub divisions")

	def chooseCityStateLocations(self, cityStateTypes: [CityStateType]):
		for cityState in cityStateTypes:
			bestArea: Optional[StartArea] = None
			bestValue: int = 0
			bestLocation: HexPoint = HexPoint(-1, -1)

			# find best spot for civ in all areas
			for startArea in self.startAreas:
				if startArea.used:
					continue

				for startPoint in startArea.area:
					valueSum: int = 0
					tooClose: bool = False

					# other start locations
					for otherStartLocation in self.startLocations:
						if startPoint.distance(otherStartLocation.location) < 8:
							tooClose = True
							break

					if tooClose:
						continue

					for loopPoint in startPoint.areaWithRadius(2):
						if not self.mapModel.valid(loopPoint):
							continue

						tile = self.mapModel.tileAt(loopPoint)
						valueSum += self.fertilityMap.values[tile.point.y][tile.point.x]

					if valueSum > bestValue:
						bestValue = valueSum
						bestLocation = startPoint
						bestArea = startArea

			if bestArea is None:
				logging.warning(f'Warning: Can\'t find valid start location for city state: {cityState}')
				continue

			# remove current start area
			self.startAreas = list(
				filter(lambda startArea: startArea.area.identifier != bestArea.area.identifier, self.startAreas))

			# sanity check - should restart
			if bestLocation == HexPoint(-1, -1):
				logging.warning(f'Warning: Can\'t find valid start location for city state: {cityState}')
			else:
				self.cityStateStartLocations.append(StartLocation(bestLocation, LeaderType.cityState, cityState, False))

		# sort human to the end
		self.startLocations = sorted(self.startLocations, key=lambda loc: 1 if loc.isHuman else 0)


class ContinentFinder:
	notAnalyzed = -2
	noContinent = -1

	def __init__(self, width: int, height: int):
		self.continentIdentifiers = Array2D(width, height)
		self.continentIdentifiers.fill(ContinentFinder.notAnalyzed)

	def evaluated(self, value) -> bool:
		return value != ContinentFinder.notAnalyzed and value != ContinentFinder.noContinent

	def executeOn(self, mapModel):
		for x in range(self.continentIdentifiers.width):
			for y in range(self.continentIdentifiers.height):
				self.evaluate(x, y, mapModel)

		# wrap map
		# if map?.wrapX ?? false {
		#   for y in 0..<self.continentIdentifiers.height {
		#       self.evaluate(x: 0, y: y, on: map)

		continents = []

		for x in range(self.continentIdentifiers.width):
			for y in range(self.continentIdentifiers.height):
				continentIdentifier = self.continentIdentifiers.values[y][x]

				if self.evaluated(continentIdentifier):
					continent = next((continentItem for continentItem in continents if
									  continentItem.identifier == continentIdentifier), None)

					if continent is None:
						continent = Continent(continentIdentifier, f'Continent {continentIdentifier})', mapModel)
						continents.append(continent)

					mapModel.setContinent(continent, HexPoint(x, y))

					continent.add(HexPoint(x, y))

		# set continent types
		availableContinentTypes = list(ContinentType)
		for continent in continents:
			if len(continent.points) < 10:
				continue

			pickContinentType = random.choice(availableContinentTypes)
			continent.continentType = pickContinentType
			availableContinentTypes.remove(pickContinentType)

		return continents

	def evaluate(self, x, y, mapModel):
		currentPoint = HexPoint(x, y)

		if mapModel.tileAt(currentPoint).terrain().isLand():
			northPoint = currentPoint.neighbor(HexDirection.north)
			nortwestPoint = currentPoint.neighbor(HexDirection.northWest)
			southPoint = currentPoint.neighbor(HexDirection.southWest)

			northContinent = self.continentIdentifiers.values[northPoint.y][northPoint.x] if mapModel.valid(
				northPoint) else ContinentFinder.notAnalyzed
			nortwestContinent = self.continentIdentifiers.values[nortwestPoint.y][nortwestPoint.x] if mapModel.valid(
				nortwestPoint) else ContinentFinder.notAnalyzed
			southContinent = self.continentIdentifiers.values[southPoint.y][southPoint.x] if mapModel.valid(
				southPoint) else ContinentFinder.notAnalyzed

			if self.evaluated(northContinent):
				self.continentIdentifiers.values[y][x] = northContinent
			elif self.evaluated(nortwestContinent):
				self.continentIdentifiers.values[y][x] = nortwestContinent
			elif self.evaluated(southContinent):
				self.continentIdentifiers.values[y][x] = southContinent
			else:
				freeIdentifier = self.firstFreeIdentifier()
				self.continentIdentifiers.values[y][x] = freeIdentifier

			# handle continent joins
			if self.evaluated(northContinent) and self.evaluated(
				nortwestContinent) and northContinent != nortwestContinent:
				self.replace(nortwestContinent, northContinent)
			elif self.evaluated(nortwestContinent) and self.evaluated(
				southContinent) and nortwestContinent != southContinent:
				self.replace(nortwestContinent, southContinent)
			elif self.evaluated(northContinent) and self.evaluated(southContinent) and northContinent != southContinent:
				self.replace(northContinent, southContinent)
		else:
			self.continentIdentifiers.values[y][x] = ContinentFinder.noContinent

	def firstFreeIdentifier(self):
		freeIdentifiers = BitArray(256)
		freeIdentifiers.fill(True)

		for x in range(self.continentIdentifiers.width):
			for y in range(self.continentIdentifiers.height):
				continentIndex = self.continentIdentifiers.values[y][x]
				if 0 <= continentIndex < 256:
					freeIdentifiers[continentIndex] = False

		for index in range(256):
			if freeIdentifiers[index]:
				return index

		return ContinentFinder.noContinent

	def replace(self, oldIdentifier: int, newIdentifier: int):
		for x in range(self.continentIdentifiers.width):
			for y in range(self.continentIdentifiers.height):
				if self.continentIdentifiers.values[y][x] == oldIdentifier:
					self.continentIdentifiers.values[y][x] = newIdentifier


class OceanFinder:
	notAnalyzed = -2
	noContinent = -1

	def __init__(self, width: int, height: int):
		self.oceanIdentifiers = Array2D(width, height)
		self.oceanIdentifiers.fill(OceanFinder.notAnalyzed)

	def evaluated(self, value) -> bool:
		return value != ContinentFinder.notAnalyzed and value != ContinentFinder.noContinent

	def executeOn(self, mapModel):
		for x in range(self.oceanIdentifiers.width):
			for y in range(self.oceanIdentifiers.height):
				self.evaluate(x, y, mapModel)

		# wrap map
		# if map?.wrapX ?? false {
		#   for y in 0..<self.continentIdentifiers.height {
		#       self.evaluate(x: 0, y: y, on: map)

		oceans = []

		for x in range(self.oceanIdentifiers.width):
			for y in range(self.oceanIdentifiers.height):
				oceanIdentifier = self.oceanIdentifiers.values[y][x]

				if self.evaluated(oceanIdentifier):
					ocean = next((oceanItem for oceanItem in oceans if
								  oceanItem.identifier == oceanIdentifier), None)

					if ocean is None:
						ocean = Ocean(oceanIdentifier, f'Ocean {oceanIdentifier})', mapModel)
						oceans.append(ocean)

					mapModel.setOcean(ocean, HexPoint(x, y))

					ocean.add(HexPoint(x, y))

		# set ocean types
		availableOceanTypes = list(OceanType)
		for ocean in oceans:
			if len(ocean.points) < 10:
				continue

			pickOceanType = random.choice(availableOceanTypes)
			ocean.oceanType = pickOceanType
			availableOceanTypes.remove(pickOceanType)

		return oceans

	def evaluate(self, x, y, mapModel):
		currentPoint = HexPoint(x, y)

		if mapModel.tileAt(currentPoint).terrain().isWater():
			northPoint = currentPoint.neighbor(HexDirection.north)
			northwestPoint = currentPoint.neighbor(HexDirection.northWest)
			southPoint = currentPoint.neighbor(HexDirection.southWest)

			northOcean = self.oceanIdentifiers.values[northPoint.y][northPoint.x] if mapModel.valid(
				northPoint) else OceanFinder.notAnalyzed
			northwestOcean = self.oceanIdentifiers.values[northwestPoint.y][northwestPoint.x] if mapModel.valid(
				northwestPoint) else OceanFinder.notAnalyzed
			southOcean = self.oceanIdentifiers.values[southPoint.y][southPoint.x] if mapModel.valid(
				southPoint) else OceanFinder.notAnalyzed

			if self.evaluated(northOcean):
				self.oceanIdentifiers.values[y][x] = northOcean
			elif self.evaluated(northwestOcean):
				self.oceanIdentifiers.values[y][x] = northwestOcean
			elif self.evaluated(southOcean):
				self.oceanIdentifiers.values[y][x] = southOcean
			else:
				freeIdentifier = self.firstFreeIdentifier()
				self.oceanIdentifiers.values[y][x] = freeIdentifier

			# handle continent joins
			if self.evaluated(northOcean) and self.evaluated(
				northwestOcean) and northOcean != northwestOcean:
				self.replace(northwestOcean, northOcean)
			elif self.evaluated(northwestOcean) and self.evaluated(
				southOcean) and northwestOcean != southOcean:
				self.replace(northwestOcean, southOcean)
			elif self.evaluated(northOcean) and self.evaluated(southOcean) and northOcean != southOcean:
				self.replace(northOcean, southOcean)
		else:
			self.oceanIdentifiers.values[y][x] = OceanFinder.noContinent

	def firstFreeIdentifier(self):
		freeIdentifiers = BitArray(256)
		freeIdentifiers.fill(True)

		for x in range(self.oceanIdentifiers.width):
			for y in range(self.oceanIdentifiers.height):
				oceanIndex = self.oceanIdentifiers.values[y][x]
				if 0 <= oceanIndex < 256:
					freeIdentifiers[oceanIndex] = False

		for index in range(256):
			if freeIdentifiers[index]:
				return index

		return OceanFinder.noContinent

	def replace(self, oldIdentifier: int, newIdentifier: int):
		for x in range(self.oceanIdentifiers.width):
			for y in range(self.oceanIdentifiers.height):
				if self.oceanIdentifiers.values[y][x] == oldIdentifier:
					self.oceanIdentifiers.values[y][x] = newIdentifier


class MapGenerator:
	def __init__(self, options: MapOptions):
		self.options = options
		self.width = options.mapSize.size().width()
		self.height = options.mapSize.size().height()

		# prepare terrain, distanceToCoast and zones
		self.plots = Array2D(self.width, self.height)

		for y in range(self.height):
			for x in range(self.width):
				self.plots.values[y][x] = TerrainType.sea

		self.distance_to_coast = Array2D(self.width, self.height, 0)
		self.climate_zones = Array2D(self.width, self.height)

		for y in range(self.height):
			for x in range(self.width):
				self.climate_zones.values[y][x] = ClimateZone.polar

		self.spring_locations = []

	def generate(self, callback):
		callback(MapGeneratorState(0.0, _("TXT_KEY_MAP_GENERATOR_START")))
		mapModel = MapModel(self.width, self.height)

		height_map = self._generateHeightMap()
		moisture_map = HeightMap(self.width, self.height)

		callback(MapGeneratorState(0.1, _("TXT_KEY_MAP_GENERATOR_INITED")))

		# 1st step: land / water
		threshold = height_map.findThresholdAbove(0.40)  # 40 % is land
		self._fillFromElevation(height_map, threshold)

		callback(MapGeneratorState(0.3, _("TXT_KEY_MAP_GENERATOR_ELEVATION")))

		# 2nd step: climate
		self._setClimateZones(mapModel)

		callback(MapGeneratorState(0.35, _("TXT_KEY_MAP_GENERATOR_CLIMATE")))

		# 2.1nd step: refine climate based on cost distance
		self._prepareDistanceToCoast()
		self._refineClimate()

		callback(MapGeneratorState(0.4, _("TXT_KEY_MAP_GENERATOR_COASTAL")))

		# 3rd step: refine terrain
		self._refineTerrain(mapModel, height_map, moisture_map)
		self._blendTerrains(mapModel)

		callback(MapGeneratorState(0.5, _("TXT_KEY_MAP_GENERATOR_TERRAIN")))

		self._placeResources(mapModel)

		callback(MapGeneratorState(0.6, _("TXT_KEY_MAP_GENERATOR_RESOURCES")))

		# 4th step: rivers
		self._placeRivers(self.options.rivers, mapModel, height_map)

		callback(MapGeneratorState(0.7, _("TXT_KEY_MAP_GENERATOR_RIVERS")))

		# 5th step: features
		self._refineFeatures(mapModel)

		callback(MapGeneratorState(0.8, _("TXT_KEY_MAP_GENERATOR_FEATURES")))

		# 6th step: features
		self._refineNaturalWonders(mapModel)

		callback(MapGeneratorState(0.83, _("TXT_KEY_MAP_GENERATOR_NATURAL_WONDERS")))

		# 7th step: continents & oceans
		self._identifyContinents(mapModel)

		callback(MapGeneratorState(0.86, _("TXT_KEY_MAP_GENERATOR_CONTINENTS")))

		self._identifyOceans(mapModel)

		callback(MapGeneratorState(0.9, _("TXT_KEY_MAP_GENERATOR_OCEANS")))

		self._identifyStartPositions(mapModel)

		callback(MapGeneratorState(0.95, "TXT_KEY_MAP_GENERATOR_POSITIONS"))

		self._addGoodyHuts(mapModel)

		callback(MapGeneratorState(0.99, _("TXT_KEY_MAP_GENERATOR_GOODIES")))

		# debug
		# mapModel.modifyIsHillsAt(2, 2, True)
		# mapModel.modifyIsHillsAt(2, 3, True)

		callback(MapGeneratorState(1.0, _("TXT_KEY_MAP_GENERATOR_READY")))

		return mapModel

	def update(self, map: MapModel):
		self._placeResources(map)

		# 4th step: rivers
		# self._placeRivers(self.options.rivers, map, height_map)

		# 5th step: features
		self._refineFeatures(map)

		# 6th step: features
		self._refineNaturalWonders(map)

		# 7th step: continents & oceans
		self._identifyContinents(map)
		self._identifyOceans(map)
		self._identifyStartPositions(map)

		self._addGoodyHuts(map)

	def _generateHeightMap(self):
		if self.options.mapType == MapType.continents:
			return HeightMap(self.width, self.height, 4)
		elif self.options.mapType == MapType.pangaea:
			return HeightMap(self.width, self.height, 2)
		elif self.options.mapType == MapType.archipelago:
			return HeightMap(self.width, self.height, 8)
		else:
			return HeightMap(self.width, self.height, 4)  # fallback

	def _fillFromElevation(self, height_map, threshold):

		for x in range(self.width):
			for y in range(self.height):
				tile_height = height_map.values[y][x]
				if tile_height > threshold:
					self.plots.values[y][x] = TerrainType.land
				else:
					self.plots.values[y][x] = TerrainType.sea

	def _setClimateZones(self, mapModel):
		self.climate_zones.fill(ClimateZone.temperate)

		for x in range(self.width):
			for y in range(self.height):
				latitude = abs((self.height / 2 - y)) / (self.height / 2.0)

				if latitude > 0.9 or y == 0 or y == (self.height - 1):
					self.climate_zones.values[y][x] = ClimateZone.polar
				elif latitude > 0.65:
					self.climate_zones.values[y][x] = ClimateZone.sub_polar
				elif latitude > 0.4:
					self.climate_zones.values[y][x] = ClimateZone.temperate
				elif latitude > 0.2:
					self.climate_zones.values[y][x] = ClimateZone.sub_tropic
				else:
					self.climate_zones.values[y][x] = ClimateZone.tropic

	def _prepareDistanceToCoast(self):
		self.distance_to_coast.fill(sys.maxsize)

		action_happened = True
		while action_happened:
			# reset
			action_happened = False

			for x in range(self.width):
				for y in range(self.height):
					# this needs to be analyzed
					if self.distance_to_coast.values[y][x] == sys.maxsize:
						# if field is ocean = > no distance
						if self.plots.values[y][x] == TerrainType.sea:
							self.distance_to_coast.values[y][x] = 0
							action_happened = True
						else:
							# check neighbors
							distance = sys.maxsize
							point = HexPoint(x, y)

							for direction in list(HexDirection):
								neighbor = point.neighbor(direction, 1)

								if 0 <= neighbor.x < self.width and 0 <= neighbor.y < self.height:
									if self.distance_to_coast.values[neighbor.y][neighbor.x] < sys.maxsize:
										distance = min(distance,
													   self.distance_to_coast.values[neighbor.y][neighbor.x] + 1)

							if distance < sys.maxsize:
								self.distance_to_coast.values[y][x] = distance
								action_happened = True

	def _refineClimate(self):
		for x in range(self.width):
			for y in range(self.height):
				distance = self.distance_to_coast.values[y][x]

				if distance < 2:
					self.climate_zones.values[y][x] = self.climate_zones.values[y][x].moderate()

	# 3rd step methods
	def _refineTerrain(self, mapModel, height_map, moisture_map):
		land_plots = 0

		for x in range(self.width):
			for y in range(self.height):
				point = HexPoint(x, y)

				if self.plots.values[y][x] == TerrainType.sea:
					# check is next continent
					next_to_continent = any(
						map(lambda n: mapModel.valid(n) and mapModel.terrainAt(n).isLand(), point.neighbors())
					)

					if height_map.values[y][x] > 0.1 or next_to_continent:
						mapModel.modifyTerrainAt(point, TerrainType.shore)
					else:
						mapModel.modifyTerrainAt(point, TerrainType.ocean)
				else:
					land_plots = land_plots + 1

					# mapModel.modifyTerrainAt(point, TerrainType.grass)
					self._updateBiome(
						point,
						mapModel,
						height_map.values[y][x],
						moisture_map.values[y][x],
						self.climate_zones.values[y][x]
					)

		for x in range(self.width):
			for y in range(self.height):
				point = HexPoint(x, y)

				if mapModel.terrainAt(point) == TerrainType.ocean:
					should_be_shore = False

					for neighbor in point.neighbors():
						if not mapModel.valid(neighbor):
							continue

						neighbor_terrain = mapModel.terrainAt(neighbor)

						if neighbor_terrain.isLand():
							should_be_shore = True
							break

					if should_be_shore:
						mapModel.modifyTerrainAt(point, TerrainType.shore)

		# Expanding coasts (MapGenerator.Lua)
		# Chance for each eligible plot to become an expansion is 1 / iExpansionDiceroll.
		# Default is two passes at 1/4 chance per eligible plot on each pass.
		for _ in range(2):
			shallow_water_plots = []
			for x in range(self.width):
				for y in range(self.height):
					point = HexPoint(x, y)

					if mapModel.terrainAt(point) == TerrainType.ocean:
						is_adjacent_to_shallow_water = False

						for neighbor in point.neighbors():
							if not mapModel.valid(neighbor):
								continue
							neighbor_terrain = mapModel.terrainAt(neighbor)

							if neighbor_terrain == TerrainType.shore and random.random() <= 0.2:
								is_adjacent_to_shallow_water = True
								break

						if is_adjacent_to_shallow_water:
							shallow_water_plots.append(point)

			for shallow_water_plot in shallow_water_plots:
				mapModel.modifyTerrainAt(shallow_water_plot, TerrainType.shore)

		# get the highest percent tiles from height map
		combined_percentage = self.options.mountains_percentage() * self.options.land_percentage()
		mountain_threshold = height_map.findThresholdAbove(combined_percentage)

		number_of_mountains = 0

		for x in range(self.width):
			for y in range(self.height):
				point = HexPoint(x, y)

				if height_map.values[y][x] >= mountain_threshold:
					mapModel.modifyFeatureAt(point, FeatureType.mountains)
					number_of_mountains += 1

		# remove some mountains, where there are mountain neighbors
		points = mapModel.points()
		random.shuffle(points)

		for point in points:
			# just check mountains
			if mapModel.featureAt(point) != FeatureType.mountains:
				continue

			mountain_neighbors = 0
			number_neighbors = 0

			for neighbor in point.neighbors():
				if not mapModel.valid(neighbor):
					continue

				neighbor_tile = mapModel.tileAt(neighbor)

				if neighbor_tile._featureValue == FeatureType.mountains or neighbor_tile._featureValue == FeatureType.mountEverest or neighbor_tile._featureValue == FeatureType.mountKilimanjaro:
					mountain_neighbors += 1

				number_neighbors += 1

			if (number_neighbors == 6 and mountain_neighbors >= 5) or (
				number_neighbors == 5 and mountain_neighbors >= 4):
				mapModel.modifyFeatureAt(point, FeatureType.none)
				mapModel.modifyIsHillsAt(point, True)
				number_of_mountains -= 1
				logging.debug("mountain removed")

		logging.info(f"Number of Mountains: {number_of_mountains}")

	def _updateBiome(self, point: HexPoint, mapModel, elevation, moisture, climate_zone):
		# from http://www.redblobgames.com/maps/terrain-from-noise/
		if climate_zone == ClimateZone.polar:
			self._updateBiomeForPolar(point, mapModel, elevation, moisture)
		elif climate_zone == ClimateZone.sub_polar:
			self._updateBiomeForSubpolar(point, mapModel, elevation, moisture)
		elif climate_zone == ClimateZone.temperate:
			self._updateBiomeForTemperate(point, mapModel, elevation, moisture)
		elif climate_zone == ClimateZone.sub_tropic:
			self._updateBiomeForSubtropic(point, mapModel, elevation, moisture)
		else:  # tropic
			self._updateBiomeForTropic(point, mapModel, elevation, moisture)

	def _updateBiomeForPolar(self, point: HexPoint, mapModel, elevation, moisture):
		if random.random() > 0.5:
			mapModel.modifyIsHillsAt(point, True)

		mapModel.modifyTerrainAt(point, TerrainType.snow)

	def _updateBiomeForSubpolar(self, point: HexPoint, mapModel, elevation, moisture):
		if elevation > 0.7 and random.random() > 0.7:
			mapModel.modifyIsHillsAt(point, True)
			mapModel.modifyTerrainAt(point, TerrainType.snow)
			return

		if elevation > 0.5 and random.random() > 0.6:
			mapModel.modifyTerrainAt(point, TerrainType.snow)
			return

		if random.random() > 0.85:
			mapModel.modifyIsHillsAt(point, True)

		mapModel.modifyTerrainAt(point, TerrainType.tundra)

	def _updateBiomeForTemperate(self, point: HexPoint, mapModel, elevation, moisture):
		if elevation > 0.7 and random.random() > 0.7:
			mapModel.modifyIsHillsAt(point, True)
			mapModel.modifyTerrainAt(point, TerrainType.grass)
			return

		if random.random() > 0.85:
			mapModel.modifyIsHillsAt(point, True)

		if moisture < 0.5:
			mapModel.modifyTerrainAt(point, TerrainType.plains)
		else:
			mapModel.modifyTerrainAt(point, TerrainType.grass)

	def _updateBiomeForSubtropic(self, point: HexPoint, mapModel, elevation, moisture):
		if elevation > 0.7 and random.random() > 0.7:
			mapModel.modifyIsHillsAt(point, True)
			mapModel.modifyTerrainAt(point, TerrainType.plains)
			return

		if random.random() > 0.85:
			mapModel.modifyIsHillsAt(point, True)

		if moisture < 0.2:
			if random.random() < 0.3:
				mapModel.modifyTerrainAt(point, TerrainType.desert)
			else:
				mapModel.modifyTerrainAt(point, TerrainType.plains)
		elif moisture < 0.6:
			mapModel.modifyTerrainAt(point, TerrainType.plains)
		else:
			mapModel.modifyTerrainAt(point, TerrainType.grass)

	def _updateBiomeForTropic(self, point: HexPoint, mapModel, elevation, moisture):
		if elevation > 0.7 and random.random() > 0.7:
			mapModel.modifyIsHillsAt(point, True)
			mapModel.modifyTerrainAt(point, TerrainType.plains)
			return

		if random.random() > 0.85:
			mapModel.modifyIsHillsAt(point, True)

		# arid
		if moisture < 0.3:
			if random.random() < 0.4:
				mapModel.modifyTerrainAt(point, TerrainType.desert)
			else:
				mapModel.modifyTerrainAt(point, TerrainType.plains)
		else:
			mapModel.modifyTerrainAt(point, TerrainType.plains)

	def _blendTerrains(self, mapModel):
		# hillsBlendPercent = 0.45 -- Chance for flat land to become hills per near mountain. Requires at least 2 near mountains.
		terrain_blend_range = 3  # range to smooth terrain (desert surrounded by plains turns to plains, etc)
		terrain_blend_random = 0.6  # random modifier for terrain smoothing

		points = mapModel.points()
		random.shuffle(points)

		for pt in points:
			tile: Tile = mapModel.tileAt(pt)

			if tile.terrain().isWater():
				continue

			if tile.hasFeature(FeatureType.mountains):
				num_near_mountains = 0

				for neighbor in pt.neighbors():
					if not mapModel.valid(neighbor):
						continue

					neighbor_feature = mapModel.featureAt(neighbor)

					if neighbor_feature == FeatureType.mountains:
						num_near_mountains = num_near_mountains + 1

				if 2 <= num_near_mountains <= 4:
					self._createPossibleMountainPass(mapModel, pt)
			else:
				rand_percent = 1.0 + random.random() * 2.0 * terrain_blend_random - terrain_blend_random
				plot_percents = mapModel.tileStatistics(pt, terrain_blend_range)
				if tile.terrain == TerrainType.grass:
					if plot_percents.desert + plot_percents.snow >= 0.33 * rand_percent:
						tile.terrain = TerrainType.plains
						if tile._featureValue == FeatureType.marsh:
							tile._featureValue = FeatureType.forest
				elif tile.terrain == TerrainType.plains:
					if plot_percents.desert >= 0.5 * rand_percent:
						# plot:SetTerrainType(TerrainTypes.TERRAIN_DESERT, true, true)
						pass
				elif tile.terrain == TerrainType.desert:
					if plot_percents.grass + plot_percents.snow >= 0.25 * rand_percent:
						tile.terrain = TerrainType.plains
				elif tile._featureValue == FeatureType.rainforest and tile._featureValue == FeatureType.marsh:
					if plot_percents.snow + plot_percents.tundra + plot_percents.desert >= 0.25 * rand_percent:
						tile._featureValue = FeatureType.none
				elif tile.terrain == TerrainType.tundra:
					if 2.0 * plot_percents.grass + plot_percents.plains + plot_percents.desert >= 0.5 * rand_percent:
						tile.terrain = TerrainType.plains

	def _createPossibleMountainPass(self, mapModel, point):

		if not mapModel.valid(point):
			return

		tile = mapModel.tileAt(point)

		if tile._featureValue == FeatureType.mountains:
			return

		options = MoveTypeIgnoreUnitsOptions(ignore_sight=True, can_embark=False, can_enter_ocean=False)
		pathFinderDataSource = MoveTypeIgnoreUnitsPathfinderDataSource(mapModel, UnitMovementType.walk, options)
		pathFinder = AStarPathfinder(pathFinderDataSource)

		longestRoute = 0

		for dirA in [HexDirection.north, HexDirection.northEast, HexDirection.southEast]:
			neighborA = point.neighbor(dirA, 1)

			if not mapModel.valid(neighborA):
				continue

			plotA = mapModel.tileAt(neighborA)

			if plotA.terrain().isLand() and plotA.feature() != FeatureType.mountains:

				opposite_dir = dirA.opposite()
				dirs = [
					opposite_dir.counterClockwiseNeighbor(),
					opposite_dir,
					opposite_dir.clockwiseNeighbor()
				]

				for dirB in dirs:
					neighborB = point.neighbor(dirB, 1)

					if not mapModel.valid(neighborB):
						continue

					plotB = mapModel.tileAt(neighborB)

					if plotB.terrain.isLand() and plotB.feature() != FeatureType.mountains:

						path = pathFinder.shortestPath(plotA.point, plotB.point)

						if path is not None:
							longestRoute = max(longestRoute, len(path.points()))

						if longestRoute == 0 or longestRoute > 15:
							logging.debug(f'-- CreatePossibleMountainPass path distance = {longestRoute} - Change to Hills at {point}')
							# plot.set(feature: .none)
							# plot.set(hills: true)

	def _placeResources(self, mapModel):
		resources = filter(lambda res: res.usage() != ResourceUsage.artifacts, list(ResourceType))
		resources = sorted(resources, key=lambda res: res.placementOrder(), reverse=True)

		# Add resources
		for resource in resources:
			if resource == ResourceType.none:
				continue

			self._addNonUniqueResource(mapModel, resource)

		logging.info("-------------------------------")

		# Show number of resources placed
		for resource in resources:

			if resource == ResourceType.none:
				continue

			resource_placed = 0

			for x in range(self.width):
				for y in range(self.height):
					point = HexPoint(x, y)
					tile = mapModel.tileAt(point)

					if tile._resourceValue == resource:
						resource_placed += 1

			logging.info(f'Counted {resource_placed} of {resource.title()} placed on map')

	def _addNonUniqueResource(self, mapModel, resource):
		resource_count = self._numberOfResourcesToAdd(mapModel, resource)

		if resource_count == 0:
			return

		points = mapModel.points()
		random.shuffle(points)

		for pt in points:
			tile = mapModel.tileAt(pt)

			if tile.canHaveResource(mapModel, resource, ignore_latitude=True):
				resource_num = 1

				if resource == ResourceType.horses or resource == ResourceType.iron or resource == ResourceType.niter or resource == ResourceType.aluminum:
					resource_num = 2
				elif resource == ResourceType.oil or resource == ResourceType.coal or resource == ResourceType.uranium:
					resource_num = 3

				tile._resourceQuantity = resource_num
				tile._resourceValue = resource

				resource_count -= 1

				# FIXME: groups

			if resource_count <= 0:
				return

	def _numberOfResourcesToAdd(self, mapModel, resource: ResourceType) -> int:
		# https://github.com/Gedemon/Civ5-YnAEMP/blob/db7cd1bc6a0684411aba700838184bcc6272b166/Override/WorldBuilderRandomItems.lua
		# get info about current resource in map
		info = self.numberOfResources(mapModel, resource)
		mapFactor = mapModel.width * mapModel.height * 100 / (
				MapSize.standard.size().width() * MapSize.standard.size().height())
		absolute_amount = max(1, resource.baseAmount() * mapFactor / 100)

		# skip random altering for tests
		# if !Utils.isRunningUnitTests {
		if resource.absoluteVarPercent() > 0:
			rand1 = absolute_amount - (absolute_amount * resource.absoluteVarPercent() / 100)
			rand2 = absolute_amount + (absolute_amount * resource.absoluteVarPercent() / 100)
			absolute_amount = int(random.uniform(rand1, rand2))

		absolute_amount -= info.already_placed

		# limit to possible
		absolute_amount = max(0, min(absolute_amount, info.num_possible))

		logging.debug(f'try to place {absolute_amount} of {resource.title()} on {info.num_possible} possible ({info.already_placed} already placed)')
		return absolute_amount

	def numberOfResources(self, mapModel, resource: ResourceType) -> ResourcesInfo:
		# Calculate numPossible, the number of plots that are eligible to have this resource:
		num_possible = 0
		already_placed = 0

		# iterate all points
		for point in mapModel.points():

			tile = mapModel.tileAt(point)

			if tile.canHaveResource(mapModel, resource, ignore_latitude=True):
				num_possible += 1
			elif tile.resourceFor(None) == resource:
				num_possible += 1
				already_placed += 1

		return ResourcesInfo(resource=resource, num_possible=num_possible, already_placed=already_placed)

	def _placeRivers(self, rivers, mapModel, height_map):
		pass

	def _refineFeatures(self, mapModel):
		# presets
		rain_forest_percent = 15
		forest_percent = 36
		marsh_percent = 3
		oasis_percent = 1
		reef_percent = 5

		water_tiles_with_ice_possible = []
		water_tiles_with_reef_possible = []
		land_tiles_with_feature_possible = []

		# statistics
		ice_features = 0
		reef_features = 0
		flood_plains_features = 0
		oasis_features = 0
		marsh_features = 0
		rain_forest_features = 0
		forest_features = 0

		for x in range(self.width):
			for y in range(self.height):
				point = HexPoint(x, y)

				tile = mapModel.tileAt(point)

				if (tile.isImpassable(UnitMovementType.walk) and tile.isImpassable(
					UnitMovementType.swim)) or tile._featureValue != FeatureType.none:
					continue

				if tile.terrain().isWater():
					can_have_ice = False
					if mapModel.canHaveFeature(point, FeatureType.ice) and not mapModel.riverAt(point) and (
						y == 0 or y == self.height - 1):
						water_tiles_with_ice_possible.append(point)
						can_have_ice = True

					if not can_have_ice and mapModel.canHaveFeature(point, FeatureType.reef):
						water_tiles_with_reef_possible.append(point)
				else:
					land_tiles_with_feature_possible.append(point)

		# ice ice baby
		for ice_location in water_tiles_with_ice_possible:
			mapModel.modifyFeatureAt(ice_location, FeatureType.ice)
			ice_features += 1

		# reef reef baby => 10% chance for reefs
		random.shuffle(water_tiles_with_reef_possible)
		for reef_location in water_tiles_with_reef_possible:
			if reef_features * 100 / len(water_tiles_with_reef_possible) > reef_percent:
				continue

			# logging.debug("add reef at \(reefLocation)")
			mapModel.modifyFeatureAt(reef_location, FeatureType.reef)
			reef_features += 1

		# second pass, add features to all land plots as appropriate based on the count and percentage of that type
		random.shuffle(land_tiles_with_feature_possible)
		for feature_location in land_tiles_with_feature_possible:

			feature_tile = mapModel.tileAt(feature_location)
			distance = self.distance_to_coast.values[feature_location.y][feature_location.x]

			floodplains_desert_modifier = 0.2 if feature_tile.terrain == TerrainType.desert else 0.0
			random_modifier = random.uniform(0.0, 0.1)
			floodplains_possibility = 0.5 if distance < 3 else 0.1 + floodplains_desert_modifier + random_modifier

			if mapModel.canHaveFeature(feature_location, FeatureType.floodplains) and \
				floodplains_possibility > random.uniform(0.0, 1.0):

				mapModel.modifyFeatureAt(feature_location, FeatureType.floodplains)
				flood_plains_features += 1

				continue

			elif mapModel.canHaveFeature(feature_location, FeatureType.oasis) and \
				(oasis_features * 100 / len(land_tiles_with_feature_possible)) <= oasis_percent:

				mapModel.modifyFeatureAt(feature_location, FeatureType.oasis)
				oasis_features += 1

				continue

			if mapModel.canHaveFeature(feature_location, FeatureType.marsh) and \
				(marsh_features * 100 / len(land_tiles_with_feature_possible)) <= marsh_percent:
				# First check to add Marsh
				mapModel.modifyFeatureAt(feature_location, FeatureType.marsh)
				marsh_features += 1
			elif mapModel.canHaveFeature(feature_location, FeatureType.rainforest) and \
				(rain_forest_features * 100 / len(land_tiles_with_feature_possible)) <= rain_forest_percent:

				# First check to add Jungle
				mapModel.modifyFeatureAt(feature_location, FeatureType.rainforest)
				rain_forest_features += 1
			elif mapModel.canHaveFeature(feature_location, FeatureType.forest) and \
				(forest_features * 100 / len(land_tiles_with_feature_possible)) <= forest_percent:

				# First check to add Forest
				mapModel.modifyFeatureAt(feature_location, FeatureType.forest)
				forest_features += 1

		# stats
		logging.info("----------------------------------------------")
		logging.info(f'Number of Ices: {ice_features}')
		logging.info(f'Number of Reefs: {reef_features} / {reef_percent}%')
		logging.info(f'Number of Floodplains: {flood_plains_features}')
		logging.info(f'Number of Marshes: {marsh_features} / {marsh_percent}%')
		logging.info(f'Number of Jungle: {rain_forest_features} / {rain_forest_percent}%')
		logging.info(f'Number of Forest: {forest_features} / {forest_percent}%')
		logging.info(f'Number of Oasis: {oasis_features} / {oasis_percent}%')
		logging.info('----------------------------------------------')

	def _refineNaturalWonders(self, mapModel):
		pass

	def _identifyContinents(self, mapModel):
		finder = ContinentFinder(mapModel.width, mapModel.height)

		continents = finder.executeOn(mapModel)

		mapModel.continents = continents

		# set area on plots
		for continent in continents:
			for point in continent.points:
				mapModel.setContinent(continent, point)

		logging.info(f'found: {len(continents)} continents')

	def _identifyOceans(self, mapModel):
		finder = OceanFinder(mapModel.width, mapModel.height)

		oceans = finder.executeOn(mapModel)

		mapModel.oceans = oceans

		# set area on plots
		for ocean in oceans:
			for point in ocean.points:
				mapModel.setOcean(ocean, point)

		logging.info(f'found: {len(oceans)} oceans')

	def _identifyStartPositions(self, mapModel):
		numberOfPlayers = self.options.mapSize.numberOfPlayers()
		numberOfCityStates = self.options.mapSize.numberOfCityStates()

		startPositioner = StartPositioner(mapModel, numberOfPlayers, numberOfCityStates)
		startPositioner.generateRegions()

		# reset random number
		# srand48(self.options.seed)

		aiLeaders: [LeaderType] = self.options.aiLeaders

		if len(aiLeaders) == 0:
			exclude_leaders = [self.options.leader, LeaderType.barbar, LeaderType.none, LeaderType.cityState]
			aiLeaders = list(filter(lambda leader: leader not in exclude_leaders, list(LeaderType)))
			assert len(aiLeaders) >= (numberOfPlayers - 1), f'need {(numberOfPlayers - 1)} ai leaders but only have {len(aiLeaders)}'
			aiLeaders = random.sample(aiLeaders, numberOfPlayers - 1)

		cityStateTypes: [CityStateType] = []
		for _ in range(self.options.mapSize.numberOfCityStates()):
			selectedCityStates: [CityStateType] = list(
				filter(lambda cityState: cityState not in cityStateTypes, list(CityStateType)))
			selectedCityState = random.choice(selectedCityStates)
			cityStateTypes.append(selectedCityState)

		startPositioner.chooseLocations(aiLeaders, self.options.leader)
		startPositioner.chooseCityStateLocations(cityStateTypes)

		foundLocations = len(startPositioner.cityStateStartLocations)
		neededLocations = self.options.mapSize.numberOfCityStates()
		if foundLocations != neededLocations:
			logging.warning(f'WARNING: could not get correct number start locations ({foundLocations}) for city state leaders ({neededLocations})')

		mapModel.startLocations = startPositioner.startLocations
		mapModel.cityStateStartLocations = startPositioner.cityStateStartLocations

	def _addGoodyHuts(self, grid: MapModel):
		# CvMapGenerator::addGoodies()
		# grid.analyze()

		points: [HexPoint] = grid.points()
		random.shuffle(points)

		tilesPerGoody = 40
		goodyHutsAdded: int = 0
		goodyRange: int = 3

		for point in points:
			tile = grid.tileAt(point)

			if tile.isWater():
				continue

			if tile.area() is not None:
				if tile.area().numberOf(ImprovementType.goodyHut) < ((len(tile.area().points()) + tilesPerGoody / 2) / tilesPerGoody):
					if ImprovementType.goodyHut.isGoodyHutPossibleOn(tile):
						tile.setImprovement(ImprovementType.goodyHut)
						goodyHutsAdded += 1

						# goodyhuts should not be to near to each other
						points = list(filter(lambda point: point.distance(tile.point) > goodyRange, points))
						# .removeAll(where: { $0.distance(to: tile.point, wrapX: grid.wrapX ? grid.size.width(): -1) <= goodyRange})

		logging.info(f"-------------------------------")
		logging.info(f"{goodyHutsAdded} goody huts added")


class RegionFinder:
	def __init__(self, mapModel, evaluator, player):
		self.mapModel = mapModel
		self.evaluator = evaluator
		self.player = player

	def divideInto(self, regions: int):
		areas: [HexArea] = []

		# fill from continents
		continents = self.mapModel.continents
		# assert len(continents) > 0

		for continent in continents:
			area = HexArea(continent.points)

			# skip small islands
			if len(area.points()) < 6:
				# FIXME: move to constants
				continue

			value = self.evaluator.valueOfArea(area, self.player)

			if value == 0.0:
				continue

			area.setValue(value)
			area.setWater(False)
			areas.append(area)

		# assert (areas.count >= continents.count, "no valid areas in map -> map invalid")

		if len(areas) > 0:
			while len(areas) < regions:
				# order smallest value first
				areas.sort(key=lambda item: item.value())

				lastArea = areas.pop()

				(firstArea, secondArea) = self.divideArea(lastArea)

				areas.append(firstArea)
				areas.append(secondArea)

		return areas

	def divideArea(self, area: HexArea) -> (HexArea, HexArea):
		if area.width() > area.height():
			return self.divideAreaHorizontally(area)
		else:
			return self.divideAreaVertically(area)

	def divideAreaHorizontally(self, area: HexArea) -> (HexArea, HexArea):
		minX = area.boundingBox().minX + 1
		maxX = area.boundingBox().maxX

		targetValue = area.value() / 2
		dx = (minX + maxX) / 2

		while minX < dx < maxX:
			# evaluation run
			(firstArea, secondArea) = area.divideHorizontally(dx)

			firstValue = self.evaluator.valueOfArea(firstArea, self.player)
			firstArea.setValue(firstValue)

			if firstArea.value() < (targetValue * 9 / 10):
				dx += 1
			elif firstArea.value() > (targetValue * 11 / 10):
				dx -= 1
			else:
				return firstArea, secondArea

		raise Exception("can't find split")

	def divideAreaVertically(self, area: HexArea) -> (HexArea, HexArea):
		minY = area.boundingBox().minY + 1
		maxY = area.boundingBox().maxY

		targetValue = area.value() / 2
		dy = (minY + maxY) / 2

		while minY < dy < maxY:
			# evaluation run
			(firstArea, secondArea) = area.divideVertically(dy)

			firstValue = self.evaluator.valueOfArea(firstArea, self.player)
			firstArea.setValue(firstValue)

			if firstArea.value() < (targetValue * 9 / 10):
				dy += 1
			elif firstArea.value() > (targetValue * 11 / 10):
				dy -= 1
			else:
				return firstArea, secondArea

		raise Exception("can't find split")
