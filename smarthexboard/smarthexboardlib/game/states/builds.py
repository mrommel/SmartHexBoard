import sys
from typing import Optional

from smarthexboard.smarthexboardlib.game.types import TechType, EraType
from smarthexboard.smarthexboardlib.map.improvements import ImprovementType
from smarthexboard.smarthexboardlib.map.types import FeatureType, RouteType
from smarthexboard.smarthexboardlib.core.base import ExtendedEnum


class BuildTypeData:
	# noinspection PyShadowingNames
	def __init__(self, name: str, repair: bool = False, requiredTech: Optional[TechType] = None,
	             era: Optional[EraType] = None, improvement: Optional[ImprovementType] = None,
	             route: Optional[RouteType] = None, removeRoad: bool = False, duration: int = 0,
	             isWater: bool = True, isKill: bool = False):
		"""

		:type requiredTech: object
		"""
		self.name = name
		self.repair = repair
		self.requiredTech = requiredTech
		self.era = era
		self.improvement = improvement
		self.route = route
		self.removeRoad = removeRoad
		self.duration = duration
		self.isWater = isWater
		self.featureBuilds = []
		self.featuresKept = []
		self.isKill = isKill


class FeatureBuild:
	def __init__(self, featureType: FeatureType, required: TechType, production: int, duration: int, isRemove: bool):
		self.featureType = featureType
		self.required = required
		self.production = production
		self.duration = duration
		self.isRemove = isRemove


class BuildType:
	pass


class BuildType(ExtendedEnum):
	none = 'none'

	removeRainforest = 'removeRainforest'
	removeMarsh = 'removeMarsh'
	removeForest = 'removeForest'
	repair = 'repair'
	mine = 'mine'
	ancientRoad = 'ancientRoad'
	classicalRoad = 'classicalRoad'
	removeRoad = 'removeRoad'
	fishingBoats = 'fishingBoats'
	camp = 'camp'
	farm = 'farm'
	quarry = 'quarry'
	plantation = 'plantation'
	pasture = 'pasture'

	@staticmethod
	def fromName(buildName: str) -> BuildType:
		if buildName == 'BuildType.none' or buildName == 'none':
			return BuildType.none
		elif buildName == 'BuildType.removeRainforest' or buildName == 'removeRainforest':
			return BuildType.removeRainforest
		elif buildName == 'BuildType.removeMarsh' or buildName == 'removeMarsh':
			return BuildType.removeMarsh
		elif buildName == 'BuildType.removeForest' or buildName == 'removeForest':
			return BuildType.removeForest
		elif buildName == 'BuildType.repair' or buildName == 'repair':
			return BuildType.repair
		elif buildName == 'BuildType.mine' or buildName == 'mine':
			return BuildType.mine
		elif buildName == 'BuildType.ancientRoad' or buildName == 'ancientRoad':
			return BuildType.ancientRoad
		elif buildName == 'BuildType.classicalRoad' or buildName == 'classicalRoad':
			return BuildType.classicalRoad
		elif buildName == 'BuildType.removeRoad' or buildName == 'removeRoad':
			return BuildType.removeRoad
		elif buildName == 'BuildType.fishingBoats' or buildName == 'fishingBoats':
			return BuildType.fishingBoats
		elif buildName == 'BuildType.camp' or buildName == 'camp':
			return BuildType.camp
		elif buildName == 'BuildType.farm' or buildName == 'farm':
			return BuildType.farm
		elif buildName == 'BuildType.quarry' or buildName == 'quarry':
			return BuildType.quarry
		elif buildName == 'BuildType.plantation' or buildName == 'plantation':
			return BuildType.plantation
		elif buildName == 'BuildType.pasture' or buildName == 'pasture':
			return BuildType.pasture
		else:
			raise Exception(f'Cannot parse BuildType from "{buildName}"')

	def title(self) -> str:  # cannot be 'name'
		return self._data().name

	def requiredTech(self) -> Optional[TechType]:
		return self._data().requiredTech

	def requiredRemoveTechFor(self, feature: FeatureType) -> Optional[TechType]:
		featureBuild = next(filter(lambda fb: fb.featureType == feature, self._data().featureBuilds), None)

		if featureBuild is not None:
			return featureBuild.required

		return None

	def canRemove(self, feature: FeatureType) -> bool:
		featureBuild = next((build for build in self._data().featureBuilds if build.featureType == feature), None)

		if featureBuild is not None:
			return featureBuild.isRemove

		return False

	def productionFromRemovalOf(self, feature: FeatureType) -> int:
		featureBuild = next(filter(lambda fb: fb.featureType == feature, self._data().featureBuilds), None)

		if featureBuild is not None:
			return featureBuild.production

		return 0

	def required(self) -> Optional[TechType]:
		return self._data().requiredTech

	def isKill(self) -> bool:
		return self._data().isKill

	def _data(self) -> BuildTypeData:
		# https://civilization.fandom.com/wiki/Module:Data/Civ5/BNW/Builds
		if self == BuildType.none:
			return BuildTypeData(
				name="None",
				duration=0
			)
		elif self == BuildType.repair:
			return BuildTypeData(
				name="Repair",
				repair=True,
				duration=300
			)

		elif self == BuildType.ancientRoad:
			return BuildTypeData(
				name="Road",
				era=EraType.ancient,
				route=RouteType.ancientRoad,
				duration=300
			)

		elif self == BuildType.classicalRoad:
			return BuildTypeData(
				name="Road",
				era=EraType.classical,
				route=RouteType.classicalRoad,
				duration=300
			)
		elif self == BuildType.removeRoad:
			return BuildTypeData(
				name="Remove Road",
				requiredTech=TechType.wheel,
				removeRoad=True,
				duration=300
			)
		elif self == BuildType.farm:
			farmBuild = BuildTypeData(
				name="Farm",
				improvement=ImprovementType.farm,
				duration=600
			)

			farmBuild.featureBuilds.append(
				FeatureBuild(
					featureType=FeatureType.rainforest,
					required=TechType.bronzeWorking,
					production=0,
					duration=600,
					isRemove=True
				)
			)
			farmBuild.featureBuilds.append(
				FeatureBuild(
					featureType=FeatureType.forest,
					required=TechType.mining,
					production=20,
					duration=300,
					isRemove=True
				)
			)
			farmBuild.featureBuilds.append(
				FeatureBuild(
					featureType=FeatureType.marsh,
					required=TechType.masonry,
					production=0,
					duration=500,
					isRemove=True
				)
			)

			farmBuild.featuresKept.append(FeatureType.floodplains)

			return farmBuild
		elif self == BuildType.mine:
			mineBuild = BuildTypeData(
				name="Mine",
				requiredTech=TechType.mining,
				improvement=ImprovementType.mine,
				duration=600
			)

			mineBuild.featuresKept.append(FeatureType.forest)
			mineBuild.featuresKept.append(FeatureType.rainforest)
			mineBuild.featuresKept.append(FeatureType.marsh)
			mineBuild.featuresKept.append(FeatureType.oasis)

			return mineBuild
		elif self == BuildType.quarry:
			quarryBuild = BuildTypeData(
				name="Quarry",
				requiredTech=TechType.mining,
				improvement=ImprovementType.quarry,
				duration=700
			)

			quarryBuild.featuresKept.append(FeatureType.forest)
			quarryBuild.featuresKept.append(FeatureType.rainforest)
			quarryBuild.featuresKept.append(FeatureType.marsh)

			return quarryBuild
		elif self == BuildType.plantation:
			# https://civilization.fandom.com/wiki/Plantation_(Civ6)
			plantationBuild = BuildTypeData(
				name="Plantation",
				requiredTech=TechType.irrigation,
				improvement=ImprovementType.plantation,
				duration=500
			)

			plantationBuild.featuresKept.append(FeatureType.forest)
			plantationBuild.featuresKept.append(FeatureType.rainforest)
			plantationBuild.featuresKept.append(FeatureType.marsh)

			return plantationBuild
		elif self == BuildType.camp:
			campBuild = BuildTypeData(
				name="Camp",
				requiredTech=TechType.animalHusbandry,
				improvement=ImprovementType.camp,
				duration=600
			)

			campBuild.featuresKept.append(FeatureType.forest)
			campBuild.featuresKept.append(FeatureType.rainforest)

			return campBuild

		elif self == BuildType.pasture:
			# https://civilization.fandom.com/wiki/Pasture_(Civ6)
			pastureBuild = BuildTypeData(
				name="Pasture",
				requiredTech=TechType.animalHusbandry,
				improvement=ImprovementType.pasture,
				duration=700
			)

			pastureBuild.featuresKept.append(FeatureType.forest)
			pastureBuild.featuresKept.append(FeatureType.rainforest)
			pastureBuild.featuresKept.append(FeatureType.marsh)

			return pastureBuild

		elif self == BuildType.fishingBoats:
			fishingBoatsBuild = BuildTypeData(
				name="Fishing Boats",
				requiredTech=TechType.sailing,
				improvement=ImprovementType.fishingBoats,
				duration=700,
				isWater=True,
				isKill=True
			)

			return fishingBoatsBuild

		elif self == BuildType.removeForest:
			removeForestBuild = BuildTypeData(
				name="Remove Forest",
				duration=300
			)

			removeForestBuild.featureBuilds.append(
				FeatureBuild(
					featureType=FeatureType.forest,
					required=TechType.mining,
					production=20,
					duration=300,
					isRemove=True
				)
			)

			return removeForestBuild

		elif self == BuildType.removeRainforest:
			removeRainforestBuild = BuildTypeData(name="Remove Rainforest", duration=600)

			removeRainforestBuild.featureBuilds.append(
				FeatureBuild(
					featureType=FeatureType.rainforest,
					required=TechType.bronzeWorking,
					production=0,
					duration=600,
					isRemove=True
				)
			)

			return removeRainforestBuild

		elif self == BuildType.removeMarsh:
			removeMarshBuild = BuildTypeData(name="Remove Marsh", duration=500)

			removeMarshBuild.featureBuilds.append(
				FeatureBuild(
					featureType=FeatureType.marsh,
					required=TechType.masonry,
					production=0,
					duration=500,
					isRemove=True
				)
			)

			return removeMarshBuild

	def buildTimeOn(self, tile) -> int:
		time = self._data().duration

		for feature in list(FeatureType):
			if feature == FeatureType.none:
				continue

			if tile.hasFeature(feature) and not self.keepsFeature(feature):
				featureBuild = next((fb for fb in self._data().featureBuilds if fb.featureType == feature), None)

				if featureBuild is not None:
					time += featureBuild.duration
				else:
					# build cant handle feature
					return sys.maxsize

		return time

	def keepsFeature(self, feature: FeatureType) -> bool:
		if feature in self._data().featuresKept:
			return True

		return False

	def improvement(self) -> Optional[ImprovementType]:
		return self._data().improvement

	def route(self):
		return self._data().route

	def willRepair(self) -> bool:
		return self._data().repair

	def willRemoveRoute(self) -> bool:
		return self._data().removeRoad

	def isWater(self) -> bool:
		return self._data().isWater

	@classmethod
	def fromImprovement(cls, improvement) -> Optional[BuildType]:
		for build in list(BuildType):
			if build.improvement() == improvement:
				return build

		return None
