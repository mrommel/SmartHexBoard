import sys
from abc import ABC, abstractmethod
from typing import Optional, Union, List

from smarthexboard.smarthexboardlib.core.types import EraType
from smarthexboard.smarthexboardlib.game.baseTypes import ArtifactType
from smarthexboard.smarthexboardlib.game.cities import City
from smarthexboard.smarthexboardlib.game.cityStates import CityStateType
from smarthexboard.smarthexboardlib.game.civilizations import LeaderType, CivilizationType
from smarthexboard.smarthexboardlib.game.districts import DistrictType
from smarthexboard.smarthexboardlib.game.governors import GovernorType, GovernorTitleType
from smarthexboard.smarthexboardlib.game.players import Player
from smarthexboard.smarthexboardlib.game.religions import ReligionType, PantheonType
from smarthexboard.smarthexboardlib.game.states.builds import BuildType
from smarthexboard.smarthexboardlib.game.types import TechType, CivicType
from smarthexboard.smarthexboardlib.game.unitTypes import UnitMapType
from smarthexboard.smarthexboardlib.game.units import Unit
from smarthexboard.smarthexboardlib.game.wonders import WonderType
from smarthexboard.smarthexboardlib.map.areas import Continent, ContinentType, Ocean, OceanType
from smarthexboard.smarthexboardlib.map.base import HexPoint, HexDirection, Size, Array2D, HexArea
from smarthexboard.smarthexboardlib.map.improvements import ImprovementType
from smarthexboard.smarthexboardlib.map.types import TerrainType, FeatureType, ResourceType, ClimateZone, RouteType, UnitMovementType, MapSize, \
	Tutorials, Yields, AppealLevel, UnitDomainType, ResourceUsage, StartLocation, \
	ArchaeologicalRecord, YieldType
from smarthexboard.smarthexboardlib.core.base import WeightedBaseList, ExtendedEnum, InvalidEnumError


class WeightedBuildList(WeightedBaseList):
	def __init__(self, initialDict: Optional[dict] = None):
		super().__init__(initialDict)
		for build in list(BuildType):
			self.setWeight(0.0, build)


class FlowDirection(ExtendedEnum):
	none = 0
	any = -1

	# flow of river on north edge
	east = 1
	west = 2

	# flow of river on north-east edge
	northWest = 4
	southEast = 8

	# flow of river on south-east edge
	northEast = 16
	southWest = 32


class River:
	def __init__(self, name: str):
		self._name = name

	def name(self) -> str:
		return self._name


class BuilderAIScratchPad:
	def __init__(self):
		self.turn: int = -1
		self.routeType: RouteType = RouteType.none
		self.leader: LeaderType = LeaderType.none
		self.value: int = -1


class TileBase(ABC):
	def __init__(self):
		self.point = None

	@abstractmethod
	def isRiverToCrossTowards(self, otherTile: 'TileBase') -> bool:
		pass

	@abstractmethod
	def isRiverInNorth(self) -> bool:
		pass

	@abstractmethod
	def isRiverInNorthEast(self) -> bool:
		pass

	@abstractmethod
	def isRiverInSouthEast(self) -> bool:
		pass


_river_cache = {}


class Tile(TileBase):
	"""
		class that holds a single tile of a Map

		it has a TerrainType, FeatureType, ResourceType and a boolean value for being hilly (or not)
	"""

	def __init__(self, point_or_dict: Union[HexPoint, dict], terrain: Optional[TerrainType] = None):
		"""
			constructs a Tile from a TerrainType

			@param point_or_dict: location of the tile or dict (from serialization)
			@param terrain: TerrainType
		"""
		if isinstance(point_or_dict, HexPoint) and terrain is not None:
			self.point = point_or_dict
			self._terrainValue = terrain
			self._isHills = False
			self._featureValue = FeatureType.none
			self._resourceValue = ResourceType.none  # property is hidden
			self._resourceQuantity = 0

			# river
			self._riverValue = 0
			self._riverName = None

			self._climateZone = ClimateZone.temperate
			self._route = RouteType.none
			self._routePillagedValue: bool = False
			self._improvementValue = ImprovementType.none
			self._improvementPillagedValue: bool = False
			self.continentIdentifier = None
			self.oceanIdentifier = None
			self.discovered = dict()
			self.visible = dict()
			self._cityValue = None
			self._districtValue = DistrictType.none
			self._buildingDistrictValue = DistrictType.none
			self._wonderValue = WonderType.none
			self._buildingWonderValue = WonderType.none
			self._owner = None
			self._workingCity = None
			self._buildProgressList = WeightedBuildList()
			self._area = None
		elif isinstance(point_or_dict, dict):
			tmp_point = point_or_dict.get('point', {'x': -1, 'y': -1})
			self.point = tmp_point if isinstance(tmp_point, HexPoint) else HexPoint(tmp_point)
			self._terrainValue = TerrainType.fromName(point_or_dict.get('_terrainValue', 'TerrainType.grass'))
			self._isHills = point_or_dict.get('_isHills', False)
			self._featureValue = FeatureType.fromName(point_or_dict.get('_featureValue', 'FeatureType.none'))
			self._resourceValue = ResourceType.fromName(point_or_dict.get('_resourceValue', 'ResourceType.none'))
			self._resourceQuantity = point_or_dict.get('_resourceQuantity', 0)

			# river
			self._riverValue = point_or_dict.get('_riverValue', 0)
			self._riverName = point_or_dict.get('_riverName', None)

			self._climateZone = ClimateZone.fromName(point_or_dict.get('_climateZone', 'ClimateZone.temperate'))
			self._route = RouteType.fromName(point_or_dict.get('_route', 'RouteType.none'))
			self._routePillagedValue: bool = point_or_dict.get('_routePillagedValue', False)
			self._improvementValue = ImprovementType.fromName(point_or_dict.get('_improvementValue', 'ImprovementType.none'))
			self._improvementPillagedValue: bool = point_or_dict.get('_improvementPillagedValue', False)
			self.continentIdentifier = point_or_dict.get('continentIdentifier', None)
			self.oceanIdentifier = point_or_dict.get('oceanIdentifier', None)
			self.discovered = point_or_dict.get('discovered', dict())
			self.visible = point_or_dict.get('visible', dict())
			self._cityValue = None  # fixme
			self._districtValue = point_or_dict.get('_districtValue', DistrictType.none)
			self._wonderValue = point_or_dict.get('_wonderValue', WonderType.none)
			self._owner = None  # fixme
			self._workingCity = None  # fixme
			self._buildProgressList = WeightedBuildList(point_or_dict.get('_buildProgressList', {}))
			self._area = None  # fixme
		else:
			raise Exception(f'unsupported combination: {point_or_dict}, {terrain}')

		self._builderAIScratchPad = BuilderAIScratchPad()
		self._archaeologicalRecordValue = ArchaeologicalRecord()

	def __repr__(self):
		return f'Tile({self.point}, {self._terrainValue}, hills={self._isHills}, {self._featureValue}, {self._resourceValue})'

	@staticmethod
	def resetRiverCache():
		_river_cache.clear()

	def owner(self) -> Optional[Player]:
		return self._owner

	def ownerLeader(self) -> Optional[LeaderType]:
		if self._owner is None:
			return None

		return self._owner.leader

	def hasOwner(self) -> bool:
		return self._owner is not None

	def removeOwner(self):
		self._owner = None

	def area(self) -> Optional[HexArea]:
		return self._area

	def isWater(self) -> bool:
		"""
			returns if this is a water tile
			:return: True, if this tile is a water tile, False otherwise
		"""
		return self._terrainValue.isWater()

	def isShallowWater(self) -> bool:
		return self._terrainValue == TerrainType.shore

	def isLand(self) -> bool:
		"""
			returns if this is a land tile
			:return: True, if this tile is a land tile, False otherwise
		"""
		return self._terrainValue.isLand()

	def seeThroughLevel(self) -> int:
		# https://civilization.fandom.com/wiki/Sight_(Civ6)
		level = 0

		if self.isHills():
			level += 1

		if self.hasFeature(FeatureType.mountains):
			level += 3

		if self.hasFeature(FeatureType.forest) or self.hasFeature(FeatureType.rainforest):
			level += 1

		return level

	def resourceFor(self, player) -> ResourceType:
		"""
			returns the resource of this tile for player
			if no player is provided, no check for tech
			:return: resource of this if visible to player (if provided)
		"""
		if self._resourceValue != ResourceType.none:
			valid = True

			# check if already visible to player
			reveal_tech = self._resourceValue.revealTech()
			if reveal_tech is not None:
				if player is not None:
					if not player.hasTech(reveal_tech):
						valid = False

			reveal_civic = self._resourceValue.revealCivic()
			if reveal_civic is not None:
				if player is not None:
					if not player.hasCivic(reveal_civic):
						valid = False

			if valid:
				return self._resourceValue

		return ResourceType.none

	def hasAnyResourceFor(self, player) -> bool:
		return self.resourceFor(player) != ResourceType.none

	def hasResource(self, resource: Union[ResourceType, ResourceUsage], player) -> bool:
		if isinstance(resource, ResourceType):
			return self.resourceFor(player) == resource
		elif isinstance(resource, ResourceUsage):
			return self.resourceFor(player).usage() == resource

		return False

	def setResource(self, resource: ResourceType):
		self._resourceValue = resource

	def resourceQuantity(self) -> int:
		return self._resourceQuantity

	def isImpassable(self, movement_type):
		# start with terrain cost
		terrain_cost = self._terrainValue.movementCost(movement_type)

		if terrain_cost == UnitMovementType.max:
			return True

		if self._featureValue != FeatureType.none:
			feature_cost = self._featureValue.movementCost(movement_type)

			if feature_cost == UnitMovementType.max:
				return True

		return False

	def movementCost(self, movement_type: UnitMovementType, from_tile: TileBase) -> int:
		"""
			cost to enter a terrain given the specified movement_type

			@param movement_type: type of movement
			@param from_tile: tile the unit comes from
			@return: movement cost to go from {from_tile} to this tile
		"""
		# start with terrain cost
		terrain_cost = self._terrainValue.movementCost(movement_type)

		if terrain_cost == UnitMovementType.max:
			return UnitMovementType.max.value

		# hills
		hill_costs = 1.0 if self.isHills() else 0.0

		# add feature costs
		feature_costs = 0.0
		if self.hasAnyFeature():
			feature_cost = self._featureValue.movementCost(movement_type)

			if feature_cost == UnitMovementType.max:
				return UnitMovementType.max.value

			feature_costs = feature_cost

		# add river crossing cost
		river_cost = 0.0
		if from_tile.isRiverToCrossTowards(self):
			river_cost = 3.0  # FIXME - river cost per movementType

		# https://civilization.fandom.com/wiki/Roads_(Civ6)
		if self.hasAnyRoute():
			terrain_cost = self._route.movementCost()

			if self._route != RouteType.ancientRoad:
				river_cost = 0.0

			hill_costs = 0.0
			feature_costs = 0.0

		return terrain_cost + hill_costs + feature_costs + river_cost

	def isRiverToCrossTowards(self, target: TileBase) -> bool:
		cache_key = f'{hash(self.point)}-{hash(target.point)}'
		if cache_key in _river_cache:
			return _river_cache[cache_key]

		if not self.isNeighborTo(target.point):
			_river_cache[cache_key] = False
			return False

		direction = self.point.directionTowards(target.point)

		if direction == HexDirection.north:
			tmp_value = self.isRiverInNorth()
			_river_cache[cache_key] = tmp_value
			return tmp_value
		elif direction == HexDirection.northEast:
			tmp_value = self.isRiverInNorthEast()
			_river_cache[cache_key] = tmp_value
			return tmp_value
		elif direction == HexDirection.southEast:
			tmp_value = self.isRiverInSouthEast()
			_river_cache[cache_key] = tmp_value
			return tmp_value
		elif direction == HexDirection.south:
			tmp_value = target.isRiverInNorth()
			_river_cache[cache_key] = tmp_value
			return tmp_value
		elif direction == HexDirection.southWest:
			tmp_value = target.isRiverInNorthEast()
			_river_cache[cache_key] = tmp_value
			return tmp_value
		elif direction == HexDirection.northWest:
			tmp_value = target.isRiverInSouthEast()
			_river_cache[cache_key] = tmp_value
			return tmp_value

		raise InvalidEnumError(direction)

	def setRiver(self, river: River, flow: FlowDirection):
		self._riverName = river.name()
		self.setRiverFlow(flow)

	def isRiver(self) -> bool:
		return self._riverName is not None and (
				self.isRiverInNorth() or self.isRiverInNorthEast() or self.isRiverInSouthEast())

	def to_dict(self):
		return {
			'terrain': self._terrainValue.value,
			'isHills': self._isHills,
			'feature': self._featureValue.value,
			'resource': self._resourceValue.value,
			'resource_quantity': self._resourceQuantity
			# @fixme
		}

	def isNeighborTo(self, candidate: HexPoint) -> bool:
		return self.point.distance(candidate) == 1

	def isRiverInNorth(self):
		"""river in north can flow from east or west direction"""
		return self._riverValue & int(FlowDirection.east.value) > 0 or \
			self._riverValue & int(FlowDirection.west.value) > 0

	def isRiverInNorthEast(self):
		"""river in north-east can flow to northwest or southeast direction"""
		return self._riverValue & int(FlowDirection.northWest.value) > 0 or \
			self._riverValue & int(FlowDirection.southEast.value) > 0

	def isRiverInSouthEast(self):
		"""river in south-east can flow to northeast or southwest direction"""
		return self._riverValue & int(FlowDirection.northEast.value) > 0 or \
			self._riverValue & int(FlowDirection.southWest.value) > 0

	def hasAnyRoute(self) -> bool:
		return self._route != RouteType.none

	def hasRoute(self, route: RouteType) -> bool:
		return self._route == route

	def canHaveResource(self, grid, resource: ResourceType, ignore_latitude: bool = False) -> bool:

		if resource == ResourceType.none:
			return True

		# only one resource per tile
		if self._resourceValue != ResourceType.none:
			return False

		# no resources on natural wonders
		if self._featureValue.isNaturalWonder():
			return False

		# no resources on mountains
		if self._featureValue == FeatureType.mountains:
			return False

		if self._featureValue != FeatureType.none:
			if not resource.canBePlacedOnFeature(self._featureValue):
				return False

			if not resource.canBePlacedOnFeatureTerrain(self._terrainValue):
				return False
		else:
			# only checked if no feature
			if not resource.canBePlacedOnTerrain(self._terrainValue):
				return False

		if self._isHills:
			if not resource.canBePlacedOnHills():
				return False
		elif self.isFlatlands():
			if not resource.canBePlacedOnFlatlands():
				return False

		if grid.riverAt(self.point):
			if not resource.canBePlacedOnRiverSide():
				return False

		return True

	def isFlatlands(self):
		if not self._terrainValue.isLand():
			return False

		if self._featureValue == FeatureType.mountains or self._featureValue == FeatureType.mountEverest or self._featureValue == FeatureType.mountKilimanjaro:
			return False

		return True

	def isDiscoveredBy(self, player) -> bool:
		return self.discovered.get(hash(player), False)

	def discoverBy(self, player, simulation):
		if not self.discovered.get(hash(player), False):
			self.discovered[hash(player)] = True

			# tutorial
			if simulation.tutorial() == Tutorials.movementAndExploration and player.isHuman():
				numberOfDiscoveredPlots = player.numberOfDiscoveredPlots(simulation)
				if numberOfDiscoveredPlots >= Tutorials.tilesToDiscover():
					simulation.userInterface.finishTutorial(Tutorials.movementAndExploration)
					simulation.enableTutorial(Tutorials.none)

	def isVisibleTo(self, player) -> bool:
		if player is None:
			return False

		return self.visible.get(hash(player), False)

	def isVisibleToAny(self):
		for visibleToPlayer in self.visible.values():
			if visibleToPlayer:
				return True

		return False

	def sightBy(self, player):
		self.visible[hash(player)] = True

	def canSeeTile(self, otherTile, player, radius: int, hasSentry: bool, simulation) -> bool:
		if otherTile.point == self.point:
			return True

		# wrappedX: Int = gameModel.wrappedX() ? gameModel.mapSize().width(): -1
		if self.point.isNeighborOf(otherTile.point):
			return True

		seeThruLevel = 2 if hasSentry else 1

		distance = self.point.distance(otherTile.point)
		if distance <= radius:
			tmpPoint = self.point

			while not tmpPoint.isNeighborOf(otherTile.point):
				direction = tmpPoint.directionTowards(otherTile.point)
				tmpPoint = tmpPoint.neighbor(direction)
				# tmpPoint = gameModel.wrap(point: tmpPoint)

				tmpTile = simulation.tileAt(tmpPoint)

				if tmpTile is None:
					continue

				if tmpTile.seeThroughLevel() > seeThruLevel:
					return False

			return True

		return False

	def concealTo(self, player):
		self.visible[hash(player)] = False

	def isCity(self) -> bool:
		return self._cityValue is not None

	def setCity(self, city):
		self._cityValue = city

	def productionFromFeatureRemoval(self, buildType: BuildType) -> int:
		if not self.hasAnyFeature():
			return 0

		production = 0

		for feature in list(FeatureType):
			if self.hasFeature(feature):
				if not buildType.canRemove(feature):
					return 0

				production += buildType.productionFromRemovalOf(feature)

		return production

	def terrain(self) -> TerrainType:
		return self._terrainValue

	def setTerrain(self, terrain: TerrainType):
		self._terrainValue = terrain

	def hasAnyFeature(self) -> bool:
		return self._featureValue != FeatureType.none

	def hasFeature(self, feature: FeatureType) -> bool:
		return self._featureValue == feature

	def feature(self):
		return self._featureValue

	def setFeature(self, feature: FeatureType):
		self._featureValue = feature

	def isHills(self):
		return self._isHills

	def setHills(self, hills: bool):
		self._isHills = hills

	def hasAnyImprovement(self) -> bool:
		return self._improvementValue != ImprovementType.none

	def hasImprovement(self, improvement: ImprovementType) -> bool:
		return self._improvementValue == improvement

	def removeImprovement(self):
		self.setImprovement(ImprovementType.none)

	def doImprovement(self):
		pass

	def route(self) -> RouteType:
		return self._route

	def setRoute(self, route: RouteType):
		self._route = route

	def improvement(self):
		return self._improvementValue

	def setImprovement(self, improvement: ImprovementType):
		self._improvementValue = improvement

	def hasAnyWonder(self) -> bool:
		return self._wonderValue != WonderType.none

	def wonder(self) -> WonderType:
		return self._wonderValue

	def hasDistrict(self, district: DistrictType) -> bool:
		return self._districtValue == district

	def buildDistrict(self, district: DistrictType):
		self._districtValue = district

	def district(self) -> DistrictType:
		return self._districtValue

	def buildWonder(self, wonder: WonderType):
		self._wonderValue = wonder

	def setOwner(self, player):
		self._owner = player

	def workingCity(self):
		return self._workingCity

	def setWorkingCity(self, city):
		self._workingCity = city

	def isWorked(self) -> bool:
		return self._workingCity is not None

	def workingCityName(self) -> Optional[str]:
		if self._workingCity is None:
			return None

		return self._workingCity.name()

	def yields(self, player, ignoreFeature: bool = False):
		returnYields = Yields(food=0, production=0, gold=0, science=0)

		baseYields = self._terrainValue.yields()
		returnYields += baseYields

		if self._isHills and self._terrainValue.isLand():
			returnYields += Yields(food=0, production=1, gold=0, science=0)

		if not ignoreFeature and self._featureValue != FeatureType.none:
			returnYields += self._featureValue.yields()

		visibleResource = self.resourceFor(player)
		returnYields += visibleResource.yields()

		if self._improvementValue is not None and self._improvementValue != ImprovementType.none and \
			not self.isImprovementPillaged():
			returnYields += self._improvementValue.yieldsFor(player)

		return returnYields

	def yieldsWith(self, buildType: BuildType, player, ignoreFeature: bool) -> Yields:
		# Will the build remove the feature?
		if self._featureValue != FeatureType.none:
			if buildType.canRemove(self._featureValue):
				ignoreFeature = True

		yields = self.yields(player, ignoreFeature)

		improvementFromBuild = buildType.improvement()
		if improvementFromBuild is None:
			# might be repair
			if not self.isImprovementPillaged() or buildType == BuildType.repair:
				improvementFromBuild = self.improvement()

		if improvementFromBuild is not None:
			yields += improvementFromBuild.yieldsFor(player)

		routeFromBuild = buildType.route()
		if routeFromBuild is None:
			# might be repair
			if not self.isRoutePillaged() or buildType == BuildType.repair:
				routeFromBuild = self._route

		return yields

	def isImprovementPillaged(self) -> bool:
		return self._improvementPillagedValue

	def setImprovementPillaged(self, value: bool):
		self._improvementPillagedValue = value

	def canBePillaged(self) -> bool:
		if self._improvementValue != ImprovementType.none and not self._improvementPillagedValue:
			return True

		if self._route != RouteType.none and not self._routePillagedValue:
			return True

		return False

	def buildProgressOf(self, buildType: BuildType) -> int:
		return int(self._buildProgressList.weight(buildType))

	def changeBuildProgressOf(self, build: BuildType, change: int, player: Player, simulation) -> bool:
		"""Returns true if build finished ..."""
		finished = False

		if change < 0:
			raise Exception(f'change must be bigger than zero but is {change}')

		if change > 0:
			self._buildProgressList.addWeight(change, build)

			if self.buildProgressFor(build) >= build.buildTimeOn(self):
				self._buildProgressList.setWeight(0, build)

				# Constructed Improvement
				if build.improvement() is not None and build.improvement() != ImprovementType.none:
					# eurekas
					self.updateEurekas(build.improvement(), player, simulation)

					self.setImprovement(build.improvement())

				# Constructed Route
				if build.route() is not None:
					self.setRoute(build.route())

				# Remove Feature
				if self.hasAnyFeature():
					if not build.keepsFeature(self.feature()) and build.canRemove(self.feature()):

						production, city = self.featureProductionBy(build, player)

						if production > 0:
							if city is None:
								raise Exception("no city found")

							city.changeFeatureProduction(float(production))

							if city.player.isHuman():
								# simulation.userInterface.showTooltip(at: self.point,
								# 	type:.clearedFeature(feature: self.feature(), production: production, cityName: city.name),
								# 	delay: 3)
								pass

						self.setFeature(FeatureType.none)

				# Repairing a Pillaged Tile
				if build.willRepair():
					if self.isImprovementPillaged():
						self.setImprovementPillaged(False)
					elif self.isRoutePillaged():
						self.setRoutePillaged(False)

				if build.willRemoveRoute():
					self.setRoute(RouteType.none)

				finished = True

		return finished

	def buildProgressFor(self, build: BuildType) -> int:
		return int(self._buildProgressList.weight(build))

	def updateEurekas(self, improvement: ImprovementType, player, simulation):
		# Techs
		# -----------------------------------------------------

		# Masonry - To Boost: Build a quarry
		if not player.techs.eurekaTriggeredFor(TechType.masonry):
			if improvement == ImprovementType.quarry:
				player.techs.triggerEurekaFor(TechType.masonry, simulation)

		# Wheel - To Boost: Mine a resource
		if not player.techs.eurekaTriggeredFor(TechType.wheel):
			if improvement == ImprovementType.mine and self.hasAnyResourceFor(player):
				player.techs.triggerEurekaFor(TechType.wheel, simulation)

		# Irrigation - To Boost: Farm a resource
		if not player.techs.eurekaTriggeredFor(TechType.irrigation):
			if improvement == ImprovementType.farm and self.hasAnyResourceFor(player):
				player.techs.triggerEurekaFor(TechType.irrigation, simulation)

		# Horseback Riding - To Boost: Build a pasture
		if not player.techs.eurekaTriggeredFor(TechType.horsebackRiding):
			if improvement == ImprovementType.pasture:
				player.techs.triggerEurekaFor(TechType.horsebackRiding, simulation)

		# Iron Working - To Boost: Build an Iron Mine
		if not player.techs.eurekaTriggeredFor(TechType.ironWorking):
			if improvement == ImprovementType.mine and self._resourceValue == ResourceType.iron:
				player.techs.triggerEurekaFor(TechType.ironWorking, simulation)

		# Apprenticeship - To Boost: Build 3 mines
		if not player.techs.eurekaTriggeredFor(TechType.apprenticeship):
			if improvement == ImprovementType.mine:
				player.techs.changeEurekaValue(TechType.apprenticeship, change=1)

				if player.techs.eurekaValue(TechType.apprenticeship) >= 3:
					player.techs.triggerEurekaFor(TechType.apprenticeship, simulation)

		# Ballistics - To Boost: Build 2 Forts
		if not player.techs.eurekaTriggeredFor(TechType.ballistics):
			if improvement == ImprovementType.fort:
				player.techs.changeEurekaValue(TechType.ballistics, change=1)

				if player.techs.eurekaValue(TechType.ballistics) >= 2:
					player.techs.triggerEurekaFor(TechType.ballistics, simulation)

		# Rifling - To Boost: Build a Niter Mine
		if not player.techs.eurekaTriggeredFor(TechType.rifling):
			if improvement == ImprovementType.mine and self._resourceValue == ResourceType.niter:
				player.techs.triggerEurekaFor(TechType.rifling, simulation)

		# Civics
		# -----------------------------------------------------

		# Craftsmanship - To Boost: Improve 3 tiles
		if not player.civics.inspirationTriggeredFor(CivicType.craftsmanship):
			# increase for any improvement
			player.civics.changeInspirationValueFor(CivicType.craftsmanship, change=1)

			if player.civics.inspirationValueOf(CivicType.craftsmanship) >= 3:
				player.civics.triggerInspirationFor(CivicType.craftsmanship, simulation)

		return

	def appeal(self, simulation) -> int:
		# Mountain tiles have a base Appeal of Breathtaking (4),
		# which is unaffected by surrounding features.
		if self._featureValue == FeatureType.mountains:
			return 4

		# Natural wonder tiles have a base Appeal of Breathtaking (5),
		# which is also unaffected by surrounding features.
		if self._featureValue.isNaturalWonder():
			return 5

		appealValue: int = 0
		nextRiverOrLake: bool = simulation.riverAt(self.point)
		neighborCliffsOfDoverOrUluru: bool = False
		neighborPillagedCount: int = 0
		neighborBadFeaturesCount: int = 0
		neighborBadImprovementsCount: int = 0
		neighborBadDistrictsCount: int = 0
		neighborGoodTerrainsCount: int = 0
		neighborGoodDistrictsCount: int = 0
		neighborWondersCount: int = 0
		neighborNaturalWondersCount: int = 0

		for neighbor in self.point.neighbors():
			neighborTile = simulation.tileAt(neighbor)

			if neighborTile is None:
				continue

			if neighborTile.hasFeature(FeatureType.lake):
				nextRiverOrLake = True

			if neighborTile.hasFeature(FeatureType.rainforest) or \
				neighborTile.hasFeature(FeatureType.marsh) or \
				neighborTile.hasFeature(FeatureType.floodplains):
				neighborBadFeaturesCount += 1

			if neighborTile.hasFeature(FeatureType.cliffsOfDover) or neighborTile.hasFeature(FeatureType.uluru):
				neighborCliffsOfDoverOrUluru = True

			if neighborTile.feature().isNaturalWonder() and \
				not (neighborTile.hasFeature(FeatureType.cliffsOfDover) or neighborTile.hasFeature(FeatureType.uluru)):
				neighborNaturalWondersCount += 1

			if neighborTile.isImprovementPillaged():
				neighborPillagedCount += 1

			if neighborTile.hasImprovement(ImprovementType.barbarianCamp) or \
				neighborTile.hasImprovement(ImprovementType.mine) or \
				neighborTile.hasImprovement(ImprovementType.quarry) or \
				neighborTile.hasImprovement(ImprovementType.oilWell):

				neighborBadImprovementsCount += 1

			if neighborTile.hasDistrict(DistrictType.industrialZone) or \
				neighborTile.hasDistrict(DistrictType.encampment) or \
				neighborTile.hasDistrict(DistrictType.spaceport):  # neighborTile.hasDistrict(DistrictType.aerodrome) or

				neighborBadDistrictsCount += 1

			if simulation.isCoastalAt(neighbor) or \
				neighborTile.hasFeature(FeatureType.mountains) or \
				neighborTile.hasFeature(FeatureType.forest) or \
				neighborTile.hasFeature(FeatureType.oasis):

				neighborGoodTerrainsCount += 1

			if neighborTile.hasAnyFeature() and not neighborTile.hasAnyImprovement():
				# check for governor effects of reyna
				city = neighborTile.workingCity()
				if city is not None and city.governor() is not None:
					if city.governor().type == GovernorType.reyna:
						# forestryManagement - Tiles adjacent to unimproved features receive +1 Appeal in this city.
						if city.governor().hasTitle(GovernorTitleType.forestryManagement):
							neighborGoodTerrainsCount += 1

			if neighborTile.hasAnyWonder():
				neighborWondersCount += 1

			if neighborTile.hasDistrict(DistrictType.holySite) or \
				neighborTile.hasDistrict(DistrictType.theaterSquare) or \
				neighborTile.hasDistrict(DistrictType.entertainmentComplex) or \
				neighborTile.hasDistrict(DistrictType.waterPark) or \
				neighborTile.hasDistrict(DistrictType.preserve):  # dam canal

				neighborGoodDistrictsCount += 1

		# +2 for each adjacent Sphinx (in Gathering Storm), Ice Hockey Rink, City Park, or natural wonder (except the
		# ones that provide a larger bonus).
		appealValue += neighborNaturalWondersCount * 2

		# +1 for each adjacent Holy Site, Theater Square, Entertainment Complex, Water Park, Dam, Canal, Preserve,
		# or wonder.
		appealValue += neighborGoodDistrictsCount
		appealValue += neighborWondersCount

		# +1 for each adjacent Sphinx (in vanilla Civilization VI and Rise and Fall), Château, Pairidaeza, Golf Course,
		# Nazca Line, or Rock-Hewn Church.
		#

		# +1 for each adjacent Mountain, Coast, Woods, or Oasis.
		appealValue += neighborGoodTerrainsCount

		# -1 for each adjacent barbarian outpost, Mine, Quarry, Oil Well, Offshore Oil Rig, Airstrip, Industrial Zone,
		# Encampment, Aerodrome, or Spaceport.
		appealValue -= neighborBadImprovementsCount
		appealValue -= neighborBadDistrictsCount

		# -1 for each adjacent Rainforest, Marsh, or Floodplain.
		appealValue -= neighborBadFeaturesCount

		# -1 for each adjacent pillaged tile.
		appealValue -= neighborPillagedCount

		# +1 if the tile is next to a River or Lake.
		if nextRiverOrLake:
			appealValue += 1

		# +4 if adjacent to the Cliffs of Dover (in Gathering Storm) or Uluru.
		if neighborCliffsOfDoverOrUluru:
			appealValue += 4

		return appealValue

	def appealLevel(self, simulation) -> AppealLevel:
		return AppealLevel.fromAppeal(self.appeal(simulation))

	def setRiverFlow(self, flow):
		if flow == FlowDirection.northEast or flow == FlowDirection.southWest:
			self.setRiverFlowInSouthEast(flow)
		elif flow == FlowDirection.northWest or flow == FlowDirection.southEast:
			self.setRiverFlowInNorthEast(flow)
		elif flow == FlowDirection.east or flow == FlowDirection.west:
			self.setRiverFlowInNorth(flow)
		else:
			raise Exception(f'flow: {flow}')

	def canBuild(self, buildType: BuildType, player) -> bool:
		# Can't build nothing!
		if buildType == BuildType.none:
			return False

		improvement = buildType.improvement()
		if improvement is not None:
			if self.district() is not None and self.district() != DistrictType.none:
				return False

			if not improvement.isPossibleOn(self):
				return False

		return True

	def isFriendlyTerritoryFor(self, player, simulation) -> bool:
		"""Is this a plot that's friendly to our team? (owned by us or someone we have Open Borders with)"""
		# No friendly territory for barbs!
		if player.isBarbarian():
			return False

		# Nobody owns this plot
		if not self.hasOwner():
			return False

		# Our territory
		if player == self.owner():
			return True

		# territory of player we have open border with
		if player.diplomacyAI.isOpenBordersAgreementActiveWith(self.owner()):
			return True

		return False

	def isEnemyTerritoryFor(self, player, simulation) -> bool:
		# only enemy territory for barbs!
		if player.isBarbarian():
			return True

		# Nobody owns this plot
		if not self.hasOwner():
			return False

		# Our territory
		if player == self.owner():
			return False

		# territory of player we have open border with
		if player.diplomaticAI.isAtWarWith(self.owner()):
			return True

		return False

	def isVisibleToEnemy(self, player, simulation) -> bool:
		diplomacyAI = player.diplomacyAI

		for loopPlayer in simulation.players:

			if loopPlayer.isBarbarian():
				continue

			if player == loopPlayer:
				continue

			if diplomacyAI.isAtWarWith(loopPlayer):
				if self.isVisibleTo(loopPlayer):
					return True

		return False

	def isRiverIn(self, flow: FlowDirection) -> bool:
		return self._riverValue & int(flow.value) > 0

	def setRiverFlowInNorth(self, flow: FlowDirection):
		if flow != FlowDirection.east and flow != FlowDirection.west:
			raise Exception(f'{flow} unsupported in north')

		# reset cache
		target = self.point.neighbor(HexDirection.north)
		cache_key = f'{hash(self.point)}-{hash(target)}'
		del _river_cache[cache_key]
		r_cache_key = f'{hash(target)}-{hash(self.point)}'
		del _river_cache[r_cache_key]

		if not self.isRiverIn(flow):
			self._riverValue += int(flow._value_)

		return

	def setRiverFlowInSouthEast(self, flow: FlowDirection):
		if flow != FlowDirection.northEast and flow != FlowDirection.southWest:
			raise Exception(f'{flow} unsupported in southEast')

		# reset cache
		target = self.point.neighbor(HexDirection.southEast)
		cache_key = f'{hash(self.point)}-{hash(target)}'
		del _river_cache[cache_key]
		r_cache_key = f'{hash(target)}-{hash(self.point)}'
		del _river_cache[r_cache_key]

		if not self.isRiverIn(flow):
			self._riverValue += int(flow._value_)

		return

	def setRiverFlowInNorthEast(self, flow: FlowDirection):
		if flow != FlowDirection.northWest and flow != FlowDirection.southEast:
			raise Exception(f'{flow} unsupported in northEast')

		# reset cache entries
		target = self.point.neighbor(HexDirection.northEast)
		cache_key = f'{hash(self.point)}-{hash(target)}'
		if cache_key in _river_cache:
			del _river_cache[cache_key]

		r_cache_key = f'{hash(target)}-{hash(self.point)}'
		if r_cache_key in _river_cache:
			del _river_cache[r_cache_key]

		if not self.isRiverIn(flow):
			self._riverValue += int(flow._value_)

		return

	def featureProductionBy(self, build: BuildType, player):
		if self._featureValue == FeatureType.none:
			return 0, None

		city = self.workingCity()
		if city is None:
			raise Exception("niy - try to find next city to give production to")
			# return (0, None)

		# base value
		production = build.productionFromRemovalOf(self._featureValue)

		# Distance mod
		production -= (max(0, self.point.distance(city.location) - 2) * 5)

		return production, city

	def isValidDomainFor(self, unit) -> bool:
		if self.isValidDomainForActionOf(unit):
			return True

		return self.isCity()

	def isValidDomainForActionOf(self, unit):
		if unit.domain() == UnitDomainType.none:
			return False
		elif unit.domain() == UnitDomainType.land or unit.domain() == UnitDomainType.immobile:
			return not (self.terrain().isWater() or unit.canMoveAllTerrain() or unit.isEmbarked())
		elif unit.domain() == UnitDomainType.sea:
			return self.terrain().isWater() or unit.canMoveAllTerrain()
		elif unit.domain() == UnitDomainType.air:
			return False

		return False

	def sameContinentAs(self, otherTile) -> bool:
		if isinstance(otherTile, Tile):
			return otherTile.continentIdentifier == self.continentIdentifier and self.continentIdentifier is not None

		return False

	def builderAIScratchPad(self) -> BuilderAIScratchPad:
		return self._builderAIScratchPad

	def isRoutePillaged(self) -> bool:
		return self._routePillagedValue

	def setRoutePillaged(self, pillaged: bool):
		self._routePillagedValue = pillaged

	def defenseModifierFor(self, player) -> int:
		modifier = 0

		# Can only get Defensive Bonus from ONE thing - they don't stack
		featureModifier = 0
		if self._featureValue != FeatureType.mountains:
			featureModifier = self._featureValue.defenseModifier()

		if self.isHills() or self.hasFeature(FeatureType.mountains):
			# Hill( and mountain)
			modifier += 3  # HILLS_EXTRA_DEFENSE
		elif featureModifier > 0:
			# Features
			modifier = featureModifier
		else:
			# Terrain
			modifier = self.terrain().defenseModifier()

		if self.improvement() != ImprovementType.none:
			modifier += self.improvement().defenseModifier()

		return modifier

	def addArchaeologicalRecord(self, artifact: ArtifactType, era: EraType, leader1: LeaderType, leader2: LeaderType):
		self._archaeologicalRecordValue.artifactType = artifact
		self._archaeologicalRecordValue.era = era
		self._archaeologicalRecordValue.leader1 = leader1
		self._archaeologicalRecordValue.leader2 = leader2

	def archaeologicalRecord(self) -> ArchaeologicalRecord:
		return self._archaeologicalRecordValue

	def possibleImprovements(self) -> [ImprovementType]:
		possibleTileImprovements: [ImprovementType] = []

		for improvementType in list(ImprovementType):
			if improvementType.isPossibleOn(self):
				possibleTileImprovements.append(improvementType)

		return possibleTileImprovements

	def startBuildingDistrict(self, district: DistrictType):
		self._buildingDistrictValue = district

	def startBuildingWonder(self, wonder: WonderType):
		self._buildingWonderValue = wonder

	def numberOfAdjacentDifferentPlayer(self, player, ignoreWater: bool, simulation) -> int:
		points: int = 0

		for neighborPoint in self.point.neighbors():
			neighborTile = simulation.tileAt(neighborPoint)

			if neighborTile is None:
				continue

			if neighborTile.hasOwner() and neighborTile.owner() != player:
				points += 1

		return points
	
	def isCloseToBorderOf(self, player, simulation) -> bool:
		"""Is this Plot within a certain range of any of a player's Cities?"""
		minDistance: int = sys.maxsize

		# do not use estimated turns here, performance is not good
		for city in simulation.citiesOf(player):
			distance = city.location.distance(self.point)
			if distance < minDistance:
				minDistance = distance

		rangeValue: int = 5  # AI_DIPLO_PLOT_RANGE_FROM_CITY_HOME_FRONT

		return minDistance < rangeValue

	def canHaveImprovement(self, improvement: ImprovementType, player) -> bool:
		# is it a civilization based improfement
		civilization: Optional[CivilizationType] = improvement.civilization()
		if civilization is not None:
			if player.leader.civilization() != civilization:
				return False

		# check if player has discovered the required tech
		requiredTech: Optional[TechType] = improvement.requiredTech()
		if requiredTech is not None:
			if not player.techs.hasTech(requiredTech):
				return False

		return improvement.isPossibleOn(self)

	def isHomeFrontFor(self, player, simulation) -> bool:
		"""Is this Plot within a certain range of any player's Cities?"""
		if self.hasOwner():
			if self.owner() == player:
				return True

		iRange: int = 5  # AI_DIPLO_PLOT_RANGE_FROM_CITY_HOME_FRONT

		# Not owned by this player, so we have to check things the hard way,
		# and see how close the Plot is to any of this Player's Cities
		for loopCity in simulation.citiesOf(player):
			if loopCity.location.distance(self.point) < iRange:
				return True

		return False

	def calculateNatureYield(self, yieldType: YieldType, player, ignoreFeature: bool = False) -> int:
		if self.isImpassable(UnitMovementType.walk) or self._featureValue == FeatureType.mountains:
			# No Feature, or the Feature isn't a Natural Wonder (which are impassable but allowed to be worked)
			if self._featureValue == FeatureType.none or self._featureValue.isNaturalWonder():
				return 0

		# const CvYieldInfo & kYield = *GC.getYieldInfo(eYield);
		playerPantheon: PantheonType = PantheonType.none
		majorityReligion: ReligionType = ReligionType.none

		workingCity = self.workingCity()
		if workingCity is not None:
			playerPantheon: PantheonType = workingCity.player.religion.pantheon()
			majorityReligion: ReligionType = workingCity.cityReligion.majorityCityReligion

		yieldValue = self._terrainValue.yields().value(yieldType)

		# Extra yield for religion on this terrain
		if workingCity is not None and playerPantheon != PantheonType.none:
			religionChange: int = playerPantheon.terrainYieldChange(self._terrainValue, yieldType)
			# if majorityReligion != ReligionType.none:
			#	iReligionChange += GC.GetGameBeliefs()->GetEntry(eSecondaryPantheon)->GetTerrainYieldChange(getTerrainType(), eYield);

			yieldValue += religionChange

		if self.isHills():
			yieldValue += yieldType.hillsChange()

		if self._featureValue == FeatureType.mountains:
			yieldValue += yieldType.mountainChange()

		if self._featureValue == FeatureType.lake:
			yieldValue += yieldType.lakeChange()

		if not ignoreFeature:
			if self._featureValue != FeatureType.none:
				# Some Features REPLACE the Yield of the Plot instead of adding to it
				yieldChange = self._featureValue.yields().value(yieldType)

				# Player Trait
				if player is not None and self._improvementValue == ImprovementType.none:
					yieldChange += player.traits().unimprovedFeatureYieldChange(self._featureValue, yieldType)

				# Leagues
				# if workingCity is not None:
				# 	yieldChange += GC.getGame().GetGameLeagues()->GetFeatureYieldChange(pWorkingCity->getOwner(), getFeatureType(), eYield);

				# Religion
				# if (pWorkingCity != NULL & & eMajority != NO_RELIGION):
				# 	CvReligion * pReligion = GC.getGame().GetGameReligions()->GetReligion(eMajority, pWorkingCity->getOwner());
				# 	if (pReligion):
				# 		int iReligionChange = pReligion->m_Beliefs.GetFeatureYieldChange(getFeatureType(), eYield);
				# 		if (eSecondaryPantheon != NO_BELIEF):
				# 			iReligionChange += GC.GetGameBeliefs()->GetEntry(eSecondaryPantheon)->GetFeatureYieldChange(getFeatureType(), eYield);
				#
				# 		iYieldChange += iReligionChange;

				# Natural Wonders
				# if (m_eOwner != NO_PLAYER & & pFeatureInfo->IsNaturalWonder())
				# 	int iMod = 0
				#
				# 	# Boost from religion in nearby city?
				# 	if (pWorkingCity & & eMajority != NO_RELIGION):
				# 		const CvReligion * pReligion = GC.getGame().GetGameReligions()->GetReligion(eMajority, pWorkingCity->getOwner());
				# 		if (pReligion)
				# 			iReligionChange = pReligion->m_Beliefs.GetYieldChangeNaturalWonder(eYield);
				# 			if (eSecondaryPantheon != NO_BELIEF):
				# 				iReligionChange += GC.GetGameBeliefs()->GetEntry(eSecondaryPantheon)->GetYieldChangeNaturalWonder(eYield);
				#
				# 			yieldChange += religionChange
				#
				# 			iReligionMod = pReligion->m_Beliefs.GetYieldModifierNaturalWonder(eYield);
				# 			if (eSecondaryPantheon != NO_BELIEF):
				# 				iReligionMod += GC.GetGameBeliefs()->GetEntry(eSecondaryPantheon)->GetYieldModifierNaturalWonder(eYield);
				#
				# 			iMod += religionMod
				#
				# 	iYieldChange += GET_PLAYER((PlayerTypes)m_eOwner).GetPlayerTraits()->GetYieldChangeNaturalWonder(eYield);
				#
				# 	iMod += GET_PLAYER((PlayerTypes)m_eOwner).GetPlayerTraits()->GetNaturalWonderYieldModifier();
				# 	if (iMod > 0):
				# 		iYieldChange *= (100 + iMod);
				# 		iYieldChange /= 100;

				# if (pFeatureInfo->isYieldNotAdditive()):
				# 	iYield = iYieldChange;
				# else:
				# 	iYield += iYieldChange;

		# if (eTeam != NO_TEAM):
		# 	eResource = getResourceType(eTeam);
		#
		# 	if (eResource != NO_RESOURCE):
		# 		iYield += GC.getResourceInfo(eResource)->getYieldChange(eYield);
		#
		# 		# Extra yield for religion
		# 		if (pWorkingCity != NULL & & eMajority != NO_RELIGION)
		# 			const CvReligion * pReligion = GC.getGame().GetGameReligions()->GetReligion(eMajority, pWorkingCity->getOwner());
		# 			if (pReligion):
		# 				int iReligionChange = pReligion->m_Beliefs.GetResourceYieldChange(eResource, eYield);
		# 				if (eSecondaryPantheon != NO_BELIEF)
		# 					iReligionChange += GC.GetGameBeliefs()->GetEntry(eSecondaryPantheon)->GetResourceYieldChange(eResource, eYield);
		#
		# 				iYield += iReligionChange;

		if self.isRiver():
			yieldValue += self._terrainValue.riverYieldChange(yieldType) if (ignoreFeature or self._featureValue == FeatureType.none) else self._featureValue.riverYieldChange(yieldType)

		if self.isHills():
			yieldValue += self._terrainValue.hillsYieldChange(yieldType) if (ignoreFeature or self._featureValue == FeatureType.none) else self._featureValue.hillsYieldChange(yieldType)

		return int(max(0.0, yieldValue))


	def isUnitFighting(self) -> bool:
		"""Return true if any units are fighting in the plot."""
		return False


class TileStatistics:
	def __init__(self):
		self.ocean = 0.0
		self.shore = 0.0
		self.plains = 0.0
		self.grass = 0.0
		self.desert = 0.0
		self.tundra = 0.0
		self.snow = 0.0

	def normalize(self, factor):
		self.ocean /= factor
		self.shore /= factor
		self.plains /= factor
		self.grass /= factor
		self.desert /= factor
		self.tundra /= factor
		self.snow /= factor


class MapModel:
	def __init__(self, width_or_size: Union[Size, int, dict], height: Optional[int] = None):
		self._numberOfLandPlotsValue = 0
		self._numberOfWaterPlotsValue = 0

		if isinstance(width_or_size, Size) and height is None:
			size = width_or_size
			self.width = size.width()
			self.height = size.height()
			self._initialize()
		elif isinstance(width_or_size, int) and isinstance(height, int):
			self.width = width_or_size
			self.height = height
			self._initialize()
		elif isinstance(width_or_size, dict) and height is None:
			dict_obj = width_or_size
			self.width = dict_obj.get('width', 0)
			self.height = dict_obj.get('height', 0)

			tiles_dict = dict_obj.get('tiles', 0)
			self.tiles = Array2D(self.width, self.height)

			for y in range(self.height):
				for x in range(self.width):
					self.tiles.values[y][x] = tiles_dict[y][x]

			self._cities = dict_obj.get('_cities', [])
			self._units = dict_obj.get('_units', [])

			startLocations_list = dict_obj.get('startLocations', [])
			self.startLocations = []
			for startLocation_dict in startLocations_list:
				location = HexPoint(startLocation_dict.get('location', {'x': -1, 'y': -1}))
				leader = LeaderType.fromName(startLocation_dict.get('leader', 'none'))
				cityState = None
				isHuman = startLocation_dict.get('isHuman', False)
				self.startLocations.append(StartLocation(location, leader, cityState, isHuman))

			cityStateStartLocations_list = dict_obj.get('cityStateStartLocations', [])
			self.cityStateStartLocations = []
			for cityStateStartLocation_dict in cityStateStartLocations_list:
				location = HexPoint(cityStateStartLocation_dict.get('location', {'x': -1, 'y': -1}))
				leader = LeaderType.fromName(cityStateStartLocation_dict.get('leader', 'none'))
				if cityStateStartLocation_dict.get('cityState', None) is not None:
					cityState = CityStateType.fromName(cityStateStartLocation_dict.get('cityState', 'none'))
				else:
					raise Exception('cityState must not be None')
				isHuman = cityStateStartLocation_dict.get('isHuman', False)
				self.cityStateStartLocations.append(StartLocation(location, leader, cityState, isHuman))

			continents_list = dict_obj.get('continents', [])
			self.continents = []
			for continent_dict in continents_list:
				identifier: int = int(continent_dict.get('identifier', '0'))
				name: str = continent_dict.get('name', '')
				continentType: ContinentType = ContinentType.fromName(continent_dict.get('continentType', ''))
				points_list = continent_dict.get('points', [])
				points = []
				for point_dict in points_list:
					points.append(HexPoint(point_dict))

				continent = Continent(identifier, name, self)
				continent.continentType = continentType
				for point in points:
					continent.add(point)
				self.continents.append(continent)

			oceans_list = dict_obj.get('oceans', [])
			self.oceans = []
			for ocean_dict in oceans_list:
				identifier: int = int(ocean_dict.get('identifier', '0'))
				name: str = ocean_dict.get('name', '')
				oceanType: OceanType = OceanType.fromName(ocean_dict.get('oceanType', ''))
				points_list = ocean_dict.get('points', [])
				points = []
				for point_dict in points_list:
					points.append(HexPoint(point_dict))

				ocean = Ocean(identifier, name, self)
				ocean.oceanType = oceanType
				for point in points:
					ocean.add(point)
				self.oceans.append(ocean)

			self.areas = []
			areas_list = dict_obj.get('areas', [])
			for area_dict in areas_list:
				identifier: str = area_dict.get('identifier', '')
				points_list = area_dict.get('_points', [])
				points = []
				for point_dict in points_list:
					points.append(HexPoint(point_dict))

				value = area_dict.get('_value', None)

				onlyWater: bool = True
				onlyLand: bool = True
				for pt in points:
					if self.tiles.values[pt.y][pt.x].terrain().isWater():
						onlyLand = False
					if self.tiles.values[pt.y][pt.x].terrain().isLand():
						onlyWater = False

				area = HexArea(points)
				area.identifier = identifier
				area.setValue(value)
				area.setWater(onlyWater and not onlyLand)

				# assign area to corresponding tile
				for point in area.points():
					self.tiles.values[point.y][point.x]._area = area

				self.areas.append(area)
		else:
			raise AttributeError(f'Map with wrong attributes: {width_or_size} / {height}')

	def _initialize(self):
		self.tiles = Array2D(self.width, self.height)

		# create a unique Tile per place
		for y in range(self.height):
			for x in range(self.width):
				self.tiles.values[y][x] = Tile(HexPoint(x, y), TerrainType.ocean)

		self._cities = []
		self._units = []
		self.startLocations = []
		self.cityStateStartLocations = []

		self.continents = []
		self.oceans = []
		self.areas = []

	def postProcess(self, simulation):
		for unit in self._units:
			unit.player = simulation.playerForHash(unit.playerHash)
			unit._originalOwner = simulation.playerForHash(unit.originalOwnerHash)

		for y in range(self.tiles.height):
			for x in range(self.tiles.width):
				tile = self.tiles.values[y][x]
				# self._cityValue = None  # fixme
				if tile._owner is not None:
					tile._owner = simulation.playerForHash(tile._owner)
				# self._workingCity = None  # fixme
				# self._area = None  # fixme

	def updateStatistics(self):
		# reset
		self._numberOfLandPlotsValue = 0
		self._numberOfWaterPlotsValue = 0

		for x in range(self.width):
			for y in range(self.height):
				tile = self.tiles.values[y][x]

				if tile.isWater():
					self._numberOfWaterPlotsValue += 1
				else:
					self._numberOfLandPlotsValue += 1

			return

	# def save(self, filename: str) -> bool:

	def valid(self, x_or_hex: Union[int, HexPoint], y: Optional[int] = None) -> bool:
		if isinstance(x_or_hex, HexPoint) and y is None:
			hex_point = x_or_hex
			return 0 <= hex_point.x < self.width and 0 <= hex_point.y < self.height
		elif isinstance(x_or_hex, int) and isinstance(y, int):
			x = x_or_hex
			return 0 <= x < self.width and 0 <= y < self.height
		else:
			raise AttributeError(f'Map.valid with wrong attributes: {x_or_hex} / {y}')

	def points(self) -> List[HexPoint]:
		point_arr = []

		for x in range(self.width):
			for y in range(self.height):
				point_arr.append(HexPoint(x, y))

		return point_arr

	def tileAt(self, x_or_hex: Union[int, HexPoint], y: Optional[int] = None) -> Optional[Tile]:
		if isinstance(x_or_hex, HexPoint) and y is None:
			hex_point = x_or_hex

			if not self.valid(hex_point.x, hex_point.y):
				return None

			return self.tiles.values[hex_point.y][hex_point.x]
		elif isinstance(x_or_hex, int) and isinstance(y, int):
			x = x_or_hex

			if not self.valid(x, y):
				return None

			return self.tiles.values[y][x]
		else:
			raise AttributeError(f'Map.tileAt with wrong attributes: {x_or_hex} / {y}')

	def tilesIn(self, area) -> [Tile]:
		tilesList = []
		for pt in area:
			tile = self.tileAt(pt)

			if tile is not None:
				tilesList.append(tile)

		return tilesList

	def terrainAt(self, x_or_hex: Union[int, HexPoint], y: Optional[int] = None) -> Optional[TerrainType]:
		"""
			terrain of the tile at the location

			@param x_or_hex: int (x-coordinate) or HexPoint to identify the tile to get the terrain from
			@param y: int (y-coordinate)
			@return: terrain of the tile at the location
		"""
		if isinstance(x_or_hex, HexPoint) and y is None:
			hex_point = x_or_hex

			if not self.valid(hex_point.x, hex_point.y):
				return None

			return self.tiles.values[hex_point.y][hex_point.x].terrain()
		elif isinstance(x_or_hex, int) and isinstance(y, int):
			x = x_or_hex

			if not self.valid(x, y):
				return None

			return self.tiles.values[y][x].terrain()
		else:
			raise AttributeError(f'Map.terrainAt with wrong attributes: {x_or_hex} / {y}')

	def modifyTerrainAt(self, x_or_hex: Union[int, HexPoint], y_or_terrain: Union[int, TerrainType], terrain: Optional[TerrainType] = None):
		if isinstance(x_or_hex, HexPoint) and isinstance(y_or_terrain, TerrainType) and terrain is None:
			hex_point = x_or_hex
			terrain_type = y_or_terrain
			self.tiles.values[hex_point.y][hex_point.x].setTerrain(terrain_type)
		elif isinstance(x_or_hex, int) and isinstance(y_or_terrain, int) and isinstance(terrain, TerrainType):
			x = x_or_hex
			y = y_or_terrain
			terrain_type = terrain
			self.tiles.values[y][x].setTerrain(terrain_type)
		else:
			raise AttributeError(f'Map.modifyTerrainAt with wrong attributes: {x_or_hex} / {y_or_terrain} / {terrain}')

	def isHillsAt(self, x_or_hex: Union[int, HexPoint], y: Optional[int] = None) -> bool:
		"""
			get the information if the tile at the location has hills

			@param x_or_hex: int (x-coordinate) or HexPoint to identify the tile to get the hills information from
			@param y: int (y-coordinate)
			@return: True if the tile at the location has hills
		"""
		if isinstance(x_or_hex, HexPoint) and y is None:
			hex_point = x_or_hex
			return self.tiles.values[hex_point.y][hex_point.x].isHills()
		elif isinstance(x_or_hex, int) and isinstance(y, int):
			x = x_or_hex
			return self.tiles.values[y][x].isHills()
		else:
			raise AttributeError(f'Map.isHillsAtt with wrong attributes: {x_or_hex} / {y}')

	def modifyIsHillsAt(self, x_or_hex: Union[HexPoint, int], y_or_is_hills: Union[int, bool], is_hills: Optional[bool] = None):
		if isinstance(x_or_hex, HexPoint) and isinstance(y_or_is_hills, bool) and is_hills is None:
			hex_point = x_or_hex
			is_hills = y_or_is_hills
			self.tiles.values[hex_point.y][hex_point.x].setHills(is_hills)
		elif isinstance(x_or_hex, int) and isinstance(y_or_is_hills, int) and isinstance(is_hills, bool):
			x = x_or_hex
			y = y_or_is_hills
			self.tiles.values[y][x].setHills(is_hills)
		else:
			raise AttributeError(
				f'Map.modifyIsHillsAt with wrong attributes: {x_or_hex} / {y_or_is_hills} / {is_hills}')

	def featureAt(self, x_or_hex: Union[int, HexPoint], y: Optional[int] = None) -> FeatureType:
		if isinstance(x_or_hex, HexPoint) and y is None:
			hex_point = x_or_hex
			return self.tiles.values[hex_point.y][hex_point.x].feature()
		elif isinstance(x_or_hex, int) and isinstance(y, int):
			x = x_or_hex
			return self.tiles.values[y][x].feature()
		else:
			raise AttributeError(f'Map.featureAt with wrong attributes: {x_or_hex} / {y}')

	def modifyFeatureAt(self, x_or_hex: Union[int, HexPoint], y_or_feature: Union[int, FeatureType], feature: Optional[FeatureType] = None):
		if isinstance(x_or_hex, HexPoint) and isinstance(y_or_feature, FeatureType) and feature is None:
			hex_point = x_or_hex
			feature_type = y_or_feature
			self.tiles.values[hex_point.y][hex_point.x].setFeature(feature_type)
		elif isinstance(x_or_hex, int) and isinstance(y_or_feature, int) and isinstance(feature, FeatureType):
			x = x_or_hex
			y = y_or_feature
			feature_type = feature
			self.tiles.values[y][x].setFeature(feature_type)
		else:
			raise AttributeError(f'Map.modifyTerrainAt with wrong attributes: {x_or_hex} / {y_or_feature} / {feature}')

	def modifyResourceAt(self, x_or_hex: Union[int, HexPoint], y_or_resource: Union[int, ResourceType], resource: Optional[ResourceType] = None):
		if isinstance(x_or_hex, HexPoint) and isinstance(y_or_resource, ResourceType) and resource is None:
			hex_point = x_or_hex
			resource_type = y_or_resource
			self.tiles.values[hex_point.y][hex_point.x].setResource(resource_type)
		elif isinstance(x_or_hex, int) and isinstance(y_or_resource, int) and isinstance(resource, TerrainType):
			x = x_or_hex
			y = y_or_resource
			resource_type = resource
			self.tiles.values[y][x].setResource(resource_type)
		else:
			raise AttributeError(f'Map.modifyResourceAt with wrong attributes: {x_or_hex} / {y_or_resource} / {resource}')

	def riverAt(self, x_or_hex: Union[int, HexPoint], y: Optional[int] = None) -> bool:
		"""@return True, if this tile has a river - False otherwise"""
		if isinstance(x_or_hex, HexPoint) and y is None:
			hex_point = x_or_hex
		elif isinstance(x_or_hex, int) and isinstance(y, int):
			hex_point = HexPoint(x_or_hex, y)
		else:
			raise AttributeError(f'Map.riverAt with wrong attributes: {x_or_hex} / {y}')

		# north, north-east and south-east
		if self.tiles.values[hex_point.y][hex_point.x].isRiver():
			return True

		# south
		neighbor_south = hex_point.neighbor(HexDirection.south, 1)
		if self.valid(neighbor_south) and self.tiles.values[neighbor_south.y][neighbor_south.x].isRiverInNorth():
			return True

		# south-west
		neighbor_southWest = hex_point.neighbor(HexDirection.southWest, 1)
		if self.valid(neighbor_southWest) and self.tiles.values[neighbor_southWest.y][neighbor_southWest.x].isRiverInNorthEast():
			return True

		# north-west
		neighbor_northWest = hex_point.neighbor(HexDirection.northWest, 1)
		if self.valid(neighbor_northWest) and self.tiles.values[neighbor_northWest.y][neighbor_northWest.x].isRiverInSouthEast():
			return True

		return False

	def isFreshWaterAt(self, x_or_hex: Union[int, HexPoint], y: Optional[int] = None) -> bool:
		if isinstance(x_or_hex, HexPoint) and y is None:
			hex_point = x_or_hex
			return self._isFreshWaterAt(hex_point.x, hex_point.y)
		elif isinstance(x_or_hex, int) and isinstance(y, int):
			x = x_or_hex
			return self._isFreshWaterAt(x, y)
		else:
			raise AttributeError(f'Map.riverAt with wrong attributes: {x_or_hex} / {y}')

	def _isFreshWaterAt(self, x: int, y: int) -> bool:
		tile = self.tileAt(x, y)

		if tile.terrain().isWater() or tile.isImpassable(UnitMovementType.walk):
			return False

		if self.riverAt(x, y):
			return True

		for neighbors in HexPoint(x, y).neighbors():
			loopTile = self.tileAt(neighbors)

			if loopTile is None:
				continue

			if loopTile._featureValue == FeatureType.lake:
				return True

			if loopTile._featureValue == FeatureType.oasis:
				return True

		return False

	def capitalOf(self, player: Player) -> Optional[City]:
		item = next((city for city in self._cities if city.player == player and city.isCapital()), None)
		return item

	def unitsOf(self, player: Player) -> List[Unit]:
		return list(filter(lambda unit: unit.player == player, self._units))

	def unitsAt(self, location) -> List[Unit]:
		return list(filter(lambda unit: unit.location == location, self._units))

	def unitAt(self, location, unitMapType: UnitMapType) -> Optional[Unit]:
		return next(filter(lambda unit: unit.location == location and unit.unitMapType() == unitMapType, self._units), None)

	def addUnit(self, unit: Unit):
		self._units.append(unit)

	def removeUnit(self, unit):
		self._units = list(filter(lambda loopUnit: unit.location != loopUnit.location or unit.unitType != loopUnit.unitType, self._units))

	def cityAt(self, location: HexPoint) -> Optional[City]:
		return next(filter(lambda city: city.location == location, self._cities), None)

	def citiesOf(self, player) -> List[City]:
		return list(filter(lambda city: city.player == player, self._cities))

	def citiesInAreaOf(self, player, area) -> List[City]:
		return list(filter(lambda city: city.player == player and city.location in area, self._cities))

	def citiesIn(self, area) -> List[City]:
		return list(filter(lambda city: city.location in area, self._cities))

	def addCity(self, city: City, simulation):
		self._cities.append(city)

		tile = self.tileAt(city.location)
		tile.setCity(city)

		self._sightCity(city, simulation)

	def deleteCity(self, city):
		self._cities = list(filter(lambda c: c.location != city.location, self._cities))

	def _sightCity(self, city, simulation):
		for pt in city.location.areaWithRadius(3):
			tile = self.tileAt(pt)

			if tile is not None:
				tile.discoverBy(city.player, simulation)
				tile.sightBy(city.player)

	def tileStatistics(self, grid_point: HexPoint, radius: int):

		valid_tiles = 0.0
		stats = TileStatistics()

		for pt in grid_point.areaWithRadius(radius):
			if not self.valid(pt):
				continue

			tile = self.tileAt(pt)

			if tile.terrain == TerrainType.ocean:
				stats.ocean += 1
			elif tile.terrain == TerrainType.shore:
				stats.shore += 1
			elif tile.terrain == TerrainType.plains:
				stats.plains += 1
			elif tile.terrain == TerrainType.grass:
				stats.grass += 1
			elif tile.terrain == TerrainType.desert:
				stats.desert += 1
			elif tile.terrain == TerrainType.tundra:
				stats.tundra += 1
			elif tile.terrain == TerrainType.snow:
				stats.snow += 1

			valid_tiles += 1.0

		# normalize
		stats.normalize(valid_tiles)

		return stats

	def canHaveFeature(self, grid_point: HexPoint, feature_type: FeatureType):
		tile = self.tileAt(grid_point)

		# check tile itself (no surroundings)
		if feature_type.isPossibleOn(tile):
			# additional check for flood plains
			if feature_type == FeatureType.floodplains:
				return self.riverAt(grid_point)

			#  no natural wonders on resources
			if feature_type.isNaturalWonder() and tile.hasAnyResourceFor(None):
				return False

			return True

		return False

	def bestMatchingSize(self) -> MapSize:
		bestDelta = 100000
		bestMapSize = MapSize.tiny

		for mapSize in list(MapSize):
			delta = abs((mapSize.size().width() * mapSize.size().height()) - (self.width * self.height))
			if delta < bestDelta:
				bestDelta = delta
				bestMapSize = mapSize

		return bestMapSize

	def to_dict(self, human=None):
		values_dict = {}

		for y in range(self.height):
			row_array = []

			for x in range(self.width):
				tile: Tile = self.tiles.values[y][x]
				if tile.isDiscoveredBy(human):
					row_array.append(tile.to_dict())
				else:
					emptyTile = Tile(HexPoint(x, y), TerrainType.undiscovered)
					row_array.append(emptyTile.to_dict())

			values_dict[y] = row_array

		tiles_dict = {
			'width': self.width,
			'height': self.height,
			'values': values_dict
		}

		units_arr = []
		for unit in self._units:
			tile: Tile = self.tiles.values[unit.location.y][unit.location.x]
			if tile.isDiscoveredBy(human):
				units_arr.append(unit.to_dict())

		return {
			'width': self.width,
			'height': self.height,
			'tiles': tiles_dict,  # self.tiles.to_dict()
			'units': units_arr,
			'cities': []
		}

	def isCoastalAt(self, point: HexPoint):
		terrain = self.tileAt(point).terrain()
		# we are only coastal, if we are on land
		if terrain.isWater():
			return False

		for neighborPoint in point.neighbors():
			neighborTile = self.tileAt(neighborPoint)

			if neighborTile is None:
				continue

			neighborTerrain = neighborTile.terrain()
			if neighborTerrain.isWater():
				return True

		return False

	def continent(self, identifier: int) -> Continent:
		return next((continent for continent in self.continents if continent.identifier == identifier), None)

	def continentAt(self, location: HexPoint) -> Optional[Continent]:
		tile = self.tileAt(location)
		return next((continent for continent in self.continents if continent.identifier == tile.continentIdentifier), None)

	def continentBy(self, continentType: ContinentType) -> Optional[Continent]:
		return next((continent for continent in self.continents if continent.continentType == continentType), None)

	def setContinent(self, continent: Continent, location: HexPoint):
		tile = self.tileAt(location)
		tile.continentIdentifier = continent.identifier

	def setOcean(self, ocean: Ocean, location: HexPoint):
		tile = self.tileAt(location)
		tile.oceanIdentifier = ocean.identifier

	def improvementAt(self, location: HexPoint) -> ImprovementType:
		tile = self.tileAt(location)
		return tile.improvement()

	def discover(self, player, simulation):
		pass  # placeholder for mock

	def discoverRadius(self, playerAlexander, param, param1, simulation):
		pass  # placeholder for mock

	def numberOfLandPlots(self) -> int:
		return self._numberOfLandPlotsValue

	def numberOfTiles(self):
		return self._numberOfLandPlotsValue + self._numberOfWaterPlotsValue

	def indexFor(self, point: HexPoint) -> int:
		return point.y * self.width + point.x

	def pointFor(self, index: int) -> HexPoint:
		y = index / self.width
		x = index - self.width * y
		return HexPoint(x, y)

	def nearestCity(self, pt: HexPoint, player, onSameContinent: bool = False) -> Optional[City]:
		bestCity: Optional[City] = None
		bestDistance: int = sys.maxsize

		tile = self.tileAt(pt)
		if tile is None:
			return None

		for city in self._cities:
			cityTile = self.tileAt(city.location)

			if cityTile is None:
				continue

			# need to check the owner?
			if player is not None:
				# if owner does not match, skip this city
				if player != city.player:
					continue

			if onSameContinent:
				if not cityTile.sameContinentAs(tile):
					continue

			distance = city.location.distance(pt)

			if distance < bestDistance:
				bestDistance = distance
				bestCity = city

		return bestCity
