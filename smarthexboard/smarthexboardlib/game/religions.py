from typing import Optional, List

from smarthexboard.smarthexboardlib.core.base import ExtendedEnum, InvalidEnumError
from smarthexboard.smarthexboardlib.core.types import EraType
from smarthexboard.smarthexboardlib.map.improvements import ImprovementType
from smarthexboard.smarthexboardlib.map.types import TerrainType, YieldType, FeatureType, ResourceType


class TerrainYieldChange:
	def __init__(self, terrainType: TerrainType, yieldType: YieldType, value: int):
		self.terrainType: TerrainType = terrainType
		self.yieldType: YieldType = yieldType
		self.value: int = value


class FeatureYieldChange:
	def __init__(self, featureType: FeatureType, yieldType: YieldType, value: int):
		self.featureType: FeatureType = featureType
		self.yieldType: YieldType = yieldType
		self.value: int = value


class ImprovementYieldChange:
	def __init__(self, improvementType: ImprovementType, yieldType: YieldType, value: int):
		self.improvementType: ImprovementType = improvementType
		self.yieldType: YieldType = yieldType
		self.value: int = value


class ImprovedResourceYieldChanges:
	def __init__(self, resourceType: ResourceType, improvementType: ImprovementType, yieldType: YieldType, value: int):
		self.resourceType: ResourceType = resourceType
		self.improvementType: ImprovementType = improvementType
		self.yieldType: YieldType = yieldType
		self.value: int = value


class PantheonTypeData:
	def __init__(self, name: str, bonus: str, faithFromKills: int = 0, maxDistance: int = 0,
	             terrainYieldChanges=None, featureYieldChanges=None, improvedResourceYieldChanges=None,
	             improvementYieldChanges=None, cityGrowthModifier: int = 0, militaryUnitProductionModifier: int = 0,
	             obsoleteEra: Optional[EraType] = None, wonderProductionModifier: int = 0,
	             districtProductionModifier: int = 0):
		self.name: str = name
		self.bonus: str = bonus
		self.faithFromKills: int = faithFromKills
		self.maxDistance: int = maxDistance

		if terrainYieldChanges is None:
			self.terrainYieldChanges: List[TerrainYieldChange] = []
		else:
			self.terrainYieldChanges: List[TerrainYieldChange] = terrainYieldChanges

		if featureYieldChanges is None:
			self.featureYieldChanges: List[FeatureYieldChange] = []
		else:
			self.featureYieldChanges: List[FeatureYieldChange] = featureYieldChanges

		if improvedResourceYieldChanges is None:
			self.improvedResourceYieldChanges: List[ImprovedResourceYieldChanges] = []
		else:
			self.improvedResourceYieldChanges: List[ImprovedResourceYieldChanges] = improvedResourceYieldChanges

		if improvementYieldChanges is None:
			self.improvementYieldChanges: List[ImprovementYieldChange] = []
		else:
			self.improvementYieldChanges: List[ImprovementYieldChange] = improvementYieldChanges

		self.cityGrowthModifier: int = cityGrowthModifier
		self.militaryUnitProductionModifier: int = militaryUnitProductionModifier
		self.obsoleteEra: Optional[EraType] = obsoleteEra
		self.wonderProductionModifier: int = wonderProductionModifier
		self.districtProductionModifier: int = districtProductionModifier


class PantheonType:
	pass


class PantheonType(ExtendedEnum):
	none = 'none'

	cityPatronGoddess = 'cityPatronGoddess'
	danceOfTheAurora = 'danceOfTheAurora'
	desertFolklore = 'desertFolklore'
	divineSpark = 'divineSpark'
	earthGoddess = 'earthGoddess'
	fertilityRites = 'fertilityRites'
	fireGoddess = 'fireGoddess'
	godOfCraftsmen = 'godOfCraftsmen'
	godOfHealing = 'godOfHealing'
	godOfTheForge = 'godOfTheForge'
	godOfTheOpenSky = 'godOfTheOpenSky'
	godOfTheSea = 'godOfTheSea'
	godOfWar = 'godOfWar'
	goddessOfFestivals = 'goddessOfFestivals'
	goddessOfTheHarvest = 'goddessOfTheHarvest'
	goddessOfTheHunt = 'goddessOfTheHunt'
	initiationRites = 'initiationRites'
	ladyOfTheReedsAndMarshes = 'ladyOfTheReedsAndMarshes'
	monumentToTheGods = 'monumentToTheGods'
	oralTradition = 'oralTradition'
	religiousIdols = 'religiousIdols'
	religiousSettlements = 'religiousSettlements'
	riverGoddess = 'riverGoddess'
	sacredPath = 'sacredPath'
	stoneCircles = 'stoneCircles'

	@classmethod
	def all(cls) -> List[PantheonType]:
		return [
			PantheonType.cityPatronGoddess,
			PantheonType.danceOfTheAurora,
			PantheonType.desertFolklore,
			PantheonType.divineSpark,
			PantheonType.earthGoddess,
			PantheonType.fertilityRites,
			PantheonType.fireGoddess,
			PantheonType.godOfCraftsmen,
			PantheonType.godOfHealing,
			PantheonType.godOfTheForge,
			PantheonType.godOfTheOpenSky,
			PantheonType.godOfTheSea,
			PantheonType.godOfWar,
			PantheonType.goddessOfFestivals,
			PantheonType.goddessOfTheHarvest,
			PantheonType.goddessOfTheHunt,
			PantheonType.initiationRites,
			PantheonType.ladyOfTheReedsAndMarshes,
			PantheonType.monumentToTheGods,
			PantheonType.oralTradition,
			PantheonType.religiousIdols,
			PantheonType.religiousSettlements,
			PantheonType.riverGoddess,
			PantheonType.sacredPath,
			PantheonType.stoneCircles,
		]

	def title(self) -> str:
		return self._data().name

	def faithFromKills(self) -> int:
		return self._data().faithFromKills

	def maxDistance(self) -> int:
		return self._data().maxDistance

	def terrainYieldChange(self, terrainType: TerrainType, yieldType: YieldType) -> int:
		for change in self._data().terrainYieldChanges:
			if change.terrainType == terrainType and change.yieldType == yieldType:
				return change.value

		return 0

	def featureYieldChange(self, featureType: FeatureType, yieldType: YieldType) -> int:
		for change in self._data().featureYieldChanges:
			if change.featureType == featureType and change.yieldType == yieldType:
				return change.value

		return 0

	def improvedResourceYieldChange(self, resourceType: ResourceType, improvementType: ImprovementType,
	                                yieldType: YieldType) -> int:
		for change in self._data().improvedResourceYieldChanges:
			if change.resourceType == resourceType and change.improvementType == improvementType and \
				change.yieldType == yieldType:
				return change.value

		return 0

	def improvementYieldChange(self, improvementType: ImprovementType, yieldType: YieldType) -> int:
		for change in self._data().improvementYieldChanges:
			if change.improvementType == improvementType and change.yieldType == yieldType:
				return change.value

		return 0

	def cityGrowthModifier(self) -> int:
		return self._data().cityGrowthModifier

	def militaryUnitProductionModifier(self) -> int:
		return self._data().militaryUnitProductionModifier

	def obsoleteEra(self) -> Optional[EraType]:
		return self._data().obsoleteEra

	def wonderProductionModifier(self) -> int:
		return self._data().wonderProductionModifier

	def districtProductionModifier(self) -> int:
		return self._data().districtProductionModifier

	def _data(self) -> PantheonTypeData:
		if self == PantheonType.none:
			return PantheonTypeData(
				name="None",
				bonus=""
			)
		elif self == PantheonType.cityPatronGoddess:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_CITY_PATRON_GODDESS_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_CITY_PATRON_GODDESS_BONUS",
				districtProductionModifier=25  # 25%
			)
		elif self == PantheonType.danceOfTheAurora:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_DANCE_OF_THE_AURORA_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_DANCE_OF_THE_AURORA_BONUS",
				terrainYieldChanges=[TerrainYieldChange(TerrainType.tundra, YieldType.faith, 1)]
			)
		elif self == PantheonType.desertFolklore:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_DESERT_FOLKLORE_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_DESERT_FOLKLORE_BONUS",
				terrainYieldChanges=[TerrainYieldChange(TerrainType.desert, YieldType.faith, 1)]
			)
		elif self == PantheonType.divineSpark:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_DIVINE_SPARK_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_DIVINE_SPARK_BONUS"
			)
		elif self == PantheonType.earthGoddess:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_EARTH_GODDESS_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_EARTH_GODDESS_BONUS"
			)
		elif self == PantheonType.fertilityRites:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_FERTILITY_RITES_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_FERTILITY_RITES_BONUS",
				cityGrowthModifier=10  # 10%
			)
		elif self == PantheonType.fireGoddess:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_FIRE_GODDESS_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_FIRE_GODDESS_BONUS"
			)
		elif self == PantheonType.godOfCraftsmen:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_GOD_OF_CRAFTSMEN_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_GOD_OF_CRAFTSMEN_BONUS"
			)
		elif self == PantheonType.godOfHealing:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_GOD_OF_HEALING_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_GOD_OF_HEALING_BONUS",
				maxDistance = 1,
				# center is holy site
			)
		elif self == PantheonType.godOfTheForge:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_GOD_OF_THE_FORGE_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_GOD_OF_THE_FORGE_BONUS",
				militaryUnitProductionModifier=25,
				obsoleteEra=EraType.medieval
			)
		elif self == PantheonType.godOfTheOpenSky:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_GOD_OF_THE_OPEN_SKY_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_GOD_OF_THE_OPEN_SKY_BONUS",
				improvementYieldChanges=[
					ImprovementYieldChange(ImprovementType.pasture, YieldType.culture, 1)
				]
			)
		elif self == PantheonType.godOfTheSea:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_GOD_OF_THE_SEA_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_GOD_OF_THE_SEA_BONUS",
				improvementYieldChanges=[
					ImprovementYieldChange(ImprovementType.fishingBoats, YieldType.production, 1)
				]
			)
		elif self == PantheonType.godOfWar:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_GOD_OF_WAR_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_GOD_OF_WAR_BONUS",
				faithFromKills=50,  # 50%
				maxDistance=8,
				# center is holy site
			)
		elif self == PantheonType.goddessOfFestivals:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_GODDESS_OF_FESTIVALS_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_GODDESS_OF_FESTIVALS_BONUS",
				improvementYieldChanges=[
					ImprovementYieldChange(ImprovementType.plantation, YieldType.culture, 1)
				]
			)
		elif self == PantheonType.goddessOfTheHarvest:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_GODDESS_OF_THE_HARVEST_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_GODDESS_OF_THE_HARVEST_BONUS"
			)
		elif self == PantheonType.goddessOfTheHunt:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_GODDESS_OF_THE_HUNT_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_GODDESS_OF_THE_HUNT_BONUS",
				improvementYieldChanges=[
					ImprovementYieldChange(ImprovementType.camp, YieldType.food, 1),
					ImprovementYieldChange(ImprovementType.camp, YieldType.production, 1)
				]
			)
		elif self == PantheonType.initiationRites:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_INITIATION_RITES_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_INITIATION_RITES_BONUS"
			)
		elif self == PantheonType.ladyOfTheReedsAndMarshes:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_LADY_OF_THE_REEDS_AND_MARSHES_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_LADY_OF_THE_REEDS_AND_MARSHES_BONUS",
				# +1 Production from Marsh, Oasis, and Desert Floodplains.
				featureYieldChanges=[
					FeatureYieldChange(FeatureType.marsh, YieldType.production, 1),
					FeatureYieldChange(FeatureType.oasis, YieldType.production, 1),
					FeatureYieldChange(FeatureType.floodplains, YieldType.production, 1)
				]
			)
		elif self == PantheonType.monumentToTheGods:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_MONUMENT_TO_THE_GODS_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_MONUMENT_TO_THE_GODS_BONUS",
				obsoleteEra=EraType.medieval,
				wonderProductionModifier=15
			)
		elif self == PantheonType.oralTradition:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_ORAL_TRADITION_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_ORAL_TRADITION_BONUS",
				improvedResourceYieldChanges=[
					ImprovedResourceYieldChanges(ResourceType.banana, ImprovementType.plantation, YieldType.culture, 1),
					ImprovedResourceYieldChanges(ResourceType.citrus, ImprovementType.plantation, YieldType.culture, 1),
					ImprovedResourceYieldChanges(ResourceType.cotton, ImprovementType.plantation, YieldType.culture, 1),
					ImprovedResourceYieldChanges(ResourceType.dyes, ImprovementType.plantation, YieldType.culture, 1),
					ImprovedResourceYieldChanges(ResourceType.silk, ImprovementType.plantation, YieldType.culture, 1),
					ImprovedResourceYieldChanges(ResourceType.spices, ImprovementType.plantation, YieldType.culture, 1),
					ImprovedResourceYieldChanges(ResourceType.sugar, ImprovementType.plantation, YieldType.culture, 1)
				]
			)
		elif self == PantheonType.religiousIdols:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_RELIGIOUS_IDOLS_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_RELIGIOUS_IDOLS_BONUS",
				improvedResourceYieldChanges=[  # +2 Faith from Mines over Luxury and Bonus resources.
					# Bonus
					ImprovedResourceYieldChanges(ResourceType.banana, ImprovementType.mine, YieldType.faith, 1),
					ImprovedResourceYieldChanges(ResourceType.copper, ImprovementType.mine, YieldType.faith, 1),
					ImprovedResourceYieldChanges(ResourceType.cattle, ImprovementType.mine, YieldType.faith, 1),
					ImprovedResourceYieldChanges(ResourceType.crab, ImprovementType.mine, YieldType.faith, 1),
					ImprovedResourceYieldChanges(ResourceType.deer, ImprovementType.mine, YieldType.faith, 1),
					# ImprovedResourceYieldChanges(ResourceType.fish, ImprovementType.mine, YieldType.faith, 1),
					# ImprovedResourceYieldChanges(ResourceType.maize, ImprovementType.mine, YieldType.faith, 1),
					ImprovedResourceYieldChanges(ResourceType.rice, ImprovementType.mine, YieldType.faith, 1),
					ImprovedResourceYieldChanges(ResourceType.sheep, ImprovementType.mine, YieldType.faith, 1),
					ImprovedResourceYieldChanges(ResourceType.stone, ImprovementType.mine, YieldType.faith, 1),
					ImprovedResourceYieldChanges(ResourceType.wheat, ImprovementType.mine, YieldType.faith, 1),
					# Luxury
					# ImprovedResourceYieldChanges(ResourceType.amber, ImprovementType.mine, YieldType.faith, 1),
					# ImprovedResourceYieldChanges(ResourceType.cinnamon, ImprovementType.mine, YieldType.faith, 1),
					ImprovedResourceYieldChanges(ResourceType.citrus, ImprovementType.mine, YieldType.faith, 1),
					# ImprovedResourceYieldChanges(ResourceType.cloves, ImprovementType.mine, YieldType.faith, 1),
					ImprovedResourceYieldChanges(ResourceType.cocoa, ImprovementType.mine, YieldType.faith, 1),
					# ImprovedResourceYieldChanges(ResourceType.coffee, ImprovementType.mine, YieldType.faith, 1),
					# ImprovedResourceYieldChanges(ResourceType.cosmetics, ImprovementType.mine, YieldType.faith, 1),
					ImprovedResourceYieldChanges(ResourceType.cotton, ImprovementType.mine, YieldType.faith, 1),
					ImprovedResourceYieldChanges(ResourceType.dyes, ImprovementType.mine, YieldType.faith, 1),
					# ImprovedResourceYieldChanges(ResourceType.diamonds, ImprovementType.mine, YieldType.faith, 1),
					ImprovedResourceYieldChanges(ResourceType.furs, ImprovementType.mine, YieldType.faith, 1),
					# ImprovedResourceYieldChanges(ResourceType.gypsum, ImprovementType.mine, YieldType.faith, 1),
					# ImprovedResourceYieldChanges(ResourceType.honey, ImprovementType.mine, YieldType.faith, 1),
					ImprovedResourceYieldChanges(ResourceType.incense, ImprovementType.mine, YieldType.faith, 1),
					ImprovedResourceYieldChanges(ResourceType.ivory, ImprovementType.mine, YieldType.faith, 1),
					# ImprovedResourceYieldChanges(ResourceType.jade, ImprovementType.mine, YieldType.faith, 1),
					# ImprovedResourceYieldChanges(ResourceType.jeans, ImprovementType.mine, YieldType.faith, 1),
					ImprovedResourceYieldChanges(ResourceType.marble, ImprovementType.mine, YieldType.faith, 1),
					# ImprovedResourceYieldChanges(ResourceType.mercury, ImprovementType.mine, YieldType.faith, 1),
					# ImprovedResourceYieldChanges(ResourceType.olives, ImprovementType.mine, YieldType.faith, 1),
					ImprovedResourceYieldChanges(ResourceType.pearls, ImprovementType.mine, YieldType.faith, 1),
					# ImprovedResourceYieldChanges(ResourceType.perfume, ImprovementType.mine, YieldType.faith, 1),
					ImprovedResourceYieldChanges(ResourceType.salt, ImprovementType.mine, YieldType.faith, 1),
					ImprovedResourceYieldChanges(ResourceType.silk, ImprovementType.mine, YieldType.faith, 1),
					ImprovedResourceYieldChanges(ResourceType.silver, ImprovementType.mine, YieldType.faith, 1),
					ImprovedResourceYieldChanges(ResourceType.spices, ImprovementType.mine, YieldType.faith, 1),
					ImprovedResourceYieldChanges(ResourceType.sugar, ImprovementType.mine, YieldType.faith, 1),
					ImprovedResourceYieldChanges(ResourceType.tea, ImprovementType.mine, YieldType.faith, 1),
					# ImprovedResourceYieldChanges(ResourceType.tobacco, ImprovementType.mine, YieldType.faith, 1),
					# ImprovedResourceYieldChanges(ResourceType.toys, ImprovementType.mine, YieldType.faith, 1),
					# ImprovedResourceYieldChanges(ResourceType.truffles, ImprovementType.mine, YieldType.faith, 1),
					# ImprovedResourceYieldChanges(ResourceType.turtles, ImprovementType.mine, YieldType.faith, 1),
					ImprovedResourceYieldChanges(ResourceType.whales, ImprovementType.mine, YieldType.faith, 1),
					ImprovedResourceYieldChanges(ResourceType.wine, ImprovementType.mine, YieldType.faith, 1),
				]
			)
		elif self == PantheonType.riverGoddess:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_RIVER_GODDESS_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_RIVER_GODDESS_BONUS"
			)
		elif self == PantheonType.religiousSettlements:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_RELIGIOUS_SETTLEMENTS_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_RELIGIOUS_SETTLEMENTS_BONUS"
			)
		elif self == PantheonType.sacredPath:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_SACRED_PATH_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_SACRED_PATH_BONUS"
			)
		elif self == PantheonType.stoneCircles:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_STONE_CIRCLES_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_STONE_CIRCLES_BONUS",
				improvementYieldChanges=[
					ImprovementYieldChange(ImprovementType.quarry, YieldType.faith, 2)
				]
			)

		raise InvalidEnumError(self)


class ReligionTypeData:
	def __init__(self, name: str):
		self.name = name


class ReligionType(ExtendedEnum):
	none = 'none'

	atheism = 'atheism'

	buddhism = 'buddhism'
	catholicism = 'catholicism'
	confucianism = 'confucianism'
	hinduism = 'hinduism'
	islam = 'islam'
	judaism = 'judaism'
	easternOrthodoxy = 'easternOrthodoxy'
	protestantism = 'protestantism'
	shinto = 'shinto'
	sikhism = 'sikhism'
	taoism = 'taoism'
	zoroastrianism = 'zoroastrianism'

	@classmethod
	def all(cls) -> List['ReligionType']:
		return [
			ReligionType.atheism,
			ReligionType.buddhism,
			ReligionType.catholicism,
			ReligionType.confucianism,
			ReligionType.hinduism,
			ReligionType.islam,
			ReligionType.judaism,
			ReligionType.easternOrthodoxy,
			ReligionType.protestantism,
			ReligionType.shinto,
			ReligionType.sikhism,
			ReligionType.taoism,
			ReligionType.zoroastrianism
		]

	def title(self) -> str:
		return self._data().name

	def _data(self) -> ReligionTypeData:
		if self == ReligionType.none:
			return ReligionTypeData(
				name=''
			)

		if self == ReligionType.atheism:
			return ReligionTypeData(
				name='Atheism'
			)

		if self == ReligionType.buddhism:
			return ReligionTypeData(
				name='Buddhism'
			)
		if self == ReligionType.catholicism:
			return ReligionTypeData(
				name='Catholicism'
			)
		if self == ReligionType.confucianism:
			return ReligionTypeData(
				name='Confucianism'
			)
		if self == ReligionType.hinduism:
			return ReligionTypeData(
				name='Hinduism'
			)
		if self == ReligionType.islam:
			return ReligionTypeData(
				name='Islam'
			)
		if self == ReligionType.judaism:
			return ReligionTypeData(
				name='Judaism'
			)
		if self == ReligionType.easternOrthodoxy:
			return ReligionTypeData(
				name='Eastern Orthodoxy'
			)
		if self == ReligionType.protestantism:
			return ReligionTypeData(
				name='Protestantism'
			)
		if self == ReligionType.shinto:
			return ReligionTypeData(
				name='Shinto'
			)
		if self == ReligionType.sikhism:
			return ReligionTypeData(
				name='Sikhism'
			)
		if self == ReligionType.taoism:
			return ReligionTypeData(
				name='Taoism'
			)
		if self == ReligionType.zoroastrianism:
			return ReligionTypeData(
				name='Zoroastrianism'
			)

		raise InvalidEnumError(self)


class FaithPurchaseType(ExtendedEnum):
	noAutomaticFaithPurchase = 'noAutomaticFaithPurchase'
	saveForProphet = 'saveForProphet'
	purchaseUnit = 'purchaseUnit'
	purchaseBuilding = 'purchaseBuilding'


class PantheonFoundingType(ExtendedEnum):
	noPantheonAvailable = 'noPantheonAvailable'
	religionEnhanced = 'religionEnhanced'
	notEnoughFaith = 'notEnoughFaith'
	alreadyCreatedPantheon = 'alreadyCreatedPantheon'
	okay = 'okay'


class BeliefCategory(ExtendedEnum):
	none = 'none'

	founder = 'founder'
	follower = 'follower'
	enhancer = 'enhancer'
	worship = 'worship'


class BeliefData:
	def __init__(self, name: str, bonus: str, category: BeliefCategory, minPopulation: int = -1, minFollowers: int = -1,
		maxDistance: int = -1, cityGrowthModifier: int = -1, greatPersonExpendedFaith: int = 0):
		self.name = name
		self.category = category
		self.bonus = bonus

		# values
		self.minPopulation = minPopulation
		self.minFollowers = minFollowers
		self.maxDistance = maxDistance
		self.cityGrowthModifier = cityGrowthModifier
		# ...
		self.greatPersonExpendedFaith = greatPersonExpendedFaith


class BeliefType(ExtendedEnum):
	# https://civilization.fandom.com/wiki/Module:Data/Civ5/BNW/Beliefs
	none = 'none'

	# founder
	churchProperty = 'churchProperty'  # BELIEF_CHURCH_PROPERTY
	tithe = 'tithe'  # BELIEF_TITHE
	papalPrimacy = 'papalPrimacy'  # BELIEF_PAPAL_PRIMACY
	pilgrimage = 'pilgrimage'  # BELIEF_PILGRIMAGE
	worldChurch = 'worldChurch'  # BELIEF_WORLD_CHURCH
	layMinistry = 'layMinistry'  # BELIEF_LAY_MINISTRY
	stewardship = 'stewardship'  # BELIEF_STEWARDSHIP
	crossCulturalDialogue = 'crossCulturalDialogue'  # BELIEF_CROSS_CULTURAL_DIALOGUE
	religiousUnits = 'religiousUnits'  # BELIEF_RELIGIOUS_UNITY

	# follower
	choralMusic = 'choralMusic'  # BELIEF_CHORAL_MUSIC#
	religiousCommunity = 'religiousCommunity'  # BELIEF_RELIGIOUS_COMMUNITY#
	divineInspiration = 'divineInspiration'  # BELIEF_DIVINE_INSPIRATION#
	jesuitEducation = 'jesuitEducation'  # BELIEF_JESUIT_EDUCATION#
	feedTheWorld = 'feedTheWorld'  # BELIEF_FEED_THE_WORLD
	reliquaries = 'reliquaries'  # BELIEF_RELIQUARIES
	workEthic = 'workEthic'  # BELIEF_WORK_ETHIC
	zenMeditation = 'zenMeditation'  # BELIEF_ZEN_MEDITATION
	warriorMonks = 'warriorMonks'  # BELIEF_WARRIOR_MONKS

	# enhancer
	justWar = 'justWar'  # BELIEF_JUST_WAR#
	defenderFaith = 'defenderFaith'  # BELIEF_DEFENDER_FAITH#
	itinerantPreachers = 'itinerantPreachers'  # BELIEF_ITINERANT_PREACHERS#
	missionaryZeal = 'missionaryZeal'  # BELIEF_MISSIONARY_ZEAL#
	holyOrder = 'holyOrder'  # BELIEF_HOLY_ORDER#
	monasticIsolation = 'monasticIsolation'  # BELIEF_MONASTIC_ISOLATION
	scripture = 'scripture'  # BELIEF_SCRIPTURE
	burialGrounds = 'burialGrounds'  # BELIEF_BURIAL_GROUNDS
	religiousColonization = 'religiousColonization'  # BELIEF_RELIGIOUS_COLONIZATION

	# worship
	cathedral = 'cathedral'  # BELIEF_CATHEDRAL
	gurdwara = 'gurdwara'  # BELIEF_GURDWARA
	meetingHouse = 'meetingHouse'  # BELIEF_MEETING_HOUSE
	mosque = 'mosque'  # BELIEF_MOSQUE
	pagoda = 'pagoda'  # BELIEF_PAGODA
	synagogue = 'synagogue'  # BELIEF_SYNAGOGUE
	wat = 'wat'  # BELIEF_WAT
	stupa = 'stupa'  # BELIEF_STUPA
	darEMehr = 'darEMehr'  # BELIEF_DAR_E_MEHR

	def title(self) -> str:
		return self._data().name

	def category(self) -> BeliefCategory:
		return self._data().category

	def greatPersonExpendedFaith(self) -> int:
		return self._data().greatPersonExpendedFaith

	def _data(self) -> BeliefData:
		if self == BeliefType.none:
			return BeliefData(
				name='None',
				category=BeliefCategory.none,
				bonus=''
			)

		# founder
		elif self == BeliefType.churchProperty:  # BELIEF_CHURCH_PROPERTY
			return BeliefData(
				name='TXT_KEY_BELIEF_CHURCH_PROPERTY_NAME',
				category=BeliefCategory.founder,
				bonus='TXT_KEY_BELIEF_CHURCH_PROPERTY_BONUS'
			)
		elif self == BeliefType.tithe:  # BELIEF_TITHE
			return BeliefData(
				name='TXT_KEY_BELIEF_TITHE_NAME',
				category=BeliefCategory.founder,
				bonus='TXT_KEY_BELIEF_TITHE_BONUS'
			)
		elif self == BeliefType.papalPrimacy:  # BELIEF_PAPAL_PRIMACY
			return BeliefData(
				name='TXT_KEY_BELIEF_PAPAL_PRIMACY_NAME',
				category=BeliefCategory.founder,
				bonus='TXT_KEY_BELIEF_PAPAL_PRIMACY_BONUS'
			)
		elif self == BeliefType.pilgrimage:  # BELIEF_PILGRIMAGE
			return BeliefData(
				name='TXT_KEY_BELIEF_PILGRIMAGE_NAME',
				category=BeliefCategory.founder,
				bonus='TXT_KEY_BELIEF_PILGRIMAGE_BONUS'
			)
		elif self == BeliefType.worldChurch:  # BELIEF_WORLD_CHURCH
			return BeliefData(
				name='TXT_KEY_BELIEF_WORLD_CHURCH_NAME',
				category=BeliefCategory.founder,
				bonus='TXT_KEY_BELIEF_WORLD_CHURCH_BONUS'
			)
		elif self == BeliefType.layMinistry:  # BELIEF_LAY_MINISTRY
			return BeliefData(
				name='TXT_KEY_BELIEF_LAY_MINISTRY_NAME',
				category=BeliefCategory.founder,
				bonus='TXT_KEY_BELIEF_LAY_MINISTRY_BONUS'
			)
		elif self == BeliefType.stewardship:  # BELIEF_STEWARDSHIP
			return BeliefData(
				name='TXT_KEY_BELIEF_STEWARDSHIP_NAME',
				category=BeliefCategory.founder,
				bonus='TXT_KEY_BELIEF_STEWARDSHIP_BONUS'
			)
		elif self == BeliefType.crossCulturalDialogue:  # BELIEF_CROSS_CULTURAL_DIALOGUE
			return BeliefData(
				name='TXT_KEY_BELIEF_CROSS_CULTURAL_DIALOGUE_NAME',
				category=BeliefCategory.founder,
				bonus='TXT_KEY_BELIEF_CROSS_CULTURAL_DIALOGUE_BONUS'
			)
		elif self == BeliefType.religiousUnits:  # BELIEF_RELIGIOUS_UNITY
			return BeliefData(
				name='TXT_KEY_BELIEF_RELIGIOUS_UNITY_NAME',
				category=BeliefCategory.founder,
				bonus='TXT_KEY_BELIEF_RELIGIOUS_UNITY_BONUS'
			)

		# follower
		elif self == BeliefType.choralMusic:  # BELIEF_CHORAL_MUSIC
			return BeliefData(
				name='TXT_KEY_BELIEF_CHORAL_MUSIC_NAME',
				category=BeliefCategory.follower,
				bonus='TXT_KEY_BELIEF_CHORAL_MUSIC_BONUS'
			)
		elif self == BeliefType.religiousCommunity:  # BELIEF_RELIGIOUS_COMMUNITY
			return BeliefData(
				name='TXT_KEY_BELIEF_RELIGIOUS_COMMUNITY_NAME',
				category=BeliefCategory.follower,
				bonus='TXT_KEY_BELIEF_RELIGIOUS_COMMUNITY_BONUS'
			)
		elif self == BeliefType.divineInspiration:  # BELIEF_DIVINE_INSPIRATION
			return BeliefData(
				name='TXT_KEY_BELIEF_DIVINE_INSPIRATION_NAME',
				category=BeliefCategory.follower,
				bonus='TXT_KEY_BELIEF_DIVINE_INSPIRATION_BONUS'
			)
		elif self == BeliefType.jesuitEducation:  # BELIEF_JESUIT_EDUCATION
			return BeliefData(
				name='TXT_KEY_BELIEF_JESUIT_EDUCATION_NAME',
				category=BeliefCategory.follower,
				bonus='TXT_KEY_BELIEF_JESUIT_EDUCATION_BONUS'
			)
		elif self == BeliefType.feedTheWorld:  # BELIEF_FEED_THE_WORLD
			return BeliefData(
				name='TXT_KEY__NAME',
				category=BeliefCategory.follower,
				bonus='TXT_KEY__BONUS'
			)
		elif self == BeliefType.reliquaries:  # BELIEF_RELIQUARIES
			return BeliefData(
				name='TXT_KEY_BELIEF_RELIQUARIES_NAME',
				category=BeliefCategory.follower,
				bonus='TXT_KEY_BELIEF_RELIQUARIES_BONUS'
			)
		elif self == BeliefType.workEthic:  # BELIEF_WORK_ETHIC
			return BeliefData(
				name='TXT_KEY_BELIEF_WORK_ETHIC_NAME',
				category=BeliefCategory.follower,
				bonus='TXT_KEY_BELIEF_WORK_ETHIC_BONUS'
			)
		elif self == BeliefType.zenMeditation:  # BELIEF_ZEN_MEDITATION
			return BeliefData(
				name='TXT_KEY__NAME',
				category=BeliefCategory.follower,
				bonus='TXT_KEY__BONUS'
			)
		elif self == BeliefType.warriorMonks:  # BELIEF_WARRIOR_MONKS
			return BeliefData(
				name='TXT_KEY_BELIEF_WARRIOR_MONKS_NAME',
				category=BeliefCategory.follower,
				bonus='TXT_KEY_BELIEF_WARRIOR_MONKS_BONUS'
			)

		# enhancer
		elif self == BeliefType.justWar:  # BELIEF_JUST_WAR
			return BeliefData(
				name='TXT_KEY_BELIEF_JUST_WAR_NAME',
				category=BeliefCategory.enhancer,
				bonus='TXT_KEY_BELIEF_JUST_WAR_BONUS'
			)
		elif self == BeliefType.defenderFaith:  # BELIEF_DEFENDER_FAITH
			return BeliefData(
				name='TXT_KEY_BELIEF_DEFENDER_FAITH_NAME',
				category=BeliefCategory.enhancer,
				bonus='TXT_KEY_BELIEF_DEFENDER_FAITH_BONUS'
			)
		elif self == BeliefType.itinerantPreachers:  # BELIEF_ITINERANT_PREACHERS
			return BeliefData(
				name='TXT_KEY_BELIEF_ITINERANT_PREACHERS_NAME',
				category=BeliefCategory.enhancer,
				bonus='TXT_KEY_BELIEF_ITINERANT_PREACHERS_BONUS'
			)
		elif self == BeliefType.missionaryZeal:  # BELIEF_MISSIONARY_ZEAL
			return BeliefData(
				name='TXT_KEY_BELIEF_MISSIONARY_ZEAL_NAME',
				category=BeliefCategory.enhancer,
				bonus='TXT_KEY_BELIEF_MISSIONARY_ZEAL_BONUS'
			)
		elif self == BeliefType.holyOrder:  # BELIEF_HOLY_ORDER
			return BeliefData(
				name='TXT_KEY_BELIEF_HOLY_ORDER_NAME',
				category=BeliefCategory.enhancer,
				bonus='TXT_KEY_BELIEF_HOLY_ORDER_BONUS'
			)
		elif self == BeliefType.monasticIsolation:  # BELIEF_MONASTIC_ISOLATION
			return BeliefData(
				name='TXT_KEY_BELIEF_MONASTIC_ISOLATION_NAME',
				category=BeliefCategory.enhancer,
				bonus='TXT_KEY_BELIEF_MONASTIC_ISOLATION_BONUS'
			)
		elif self == BeliefType.scripture:  # BELIEF_SCRIPTURE
			return BeliefData(
				name='TXT_KEY_BELIEF_SCRIPTURE_NAME',
				category=BeliefCategory.enhancer,
				bonus='TXT_KEY_BELIEF_SCRIPTURE_BONUS'
			)
		elif self == BeliefType.burialGrounds:  # BELIEF_BURIAL_GROUNDS
			return BeliefData(
				name='TXT_KEY_BELIEF_BURIAL_GROUNDS_NAME',
				category=BeliefCategory.enhancer,
				bonus='TXT_KEY_BELIEF_BURIAL_GROUNDS_BONUS'
			)
		elif self == BeliefType.religiousColonization:  # BELIEF_RELIGIOUS_COLONIZATION
			return BeliefData(
				name='TXT_KEY_BELIEF_RELIGIOUS_COLONIZATION_NAME',
				category=BeliefCategory.enhancer,
				bonus='TXT_KEY_BELIEF_RELIGIOUS_COLONIZATION_BONUS'
			)

		# worship
		elif self == BeliefType.cathedral:  # BELIEF_CATHEDRAL
			return BeliefData(
				name='TXT_KEY_BELIEF_CATHEDRAL_NAME',
				category=BeliefCategory.worship,
				bonus='TXT_KEY_BELIEF_CATHEDRAL_BONUS'
			)
		elif self == BeliefType.gurdwara:  # BELIEF_GURDWARA
			return BeliefData(
				name='TXT_KEY_BELIEF_GURDWARA_NAME',
				category=BeliefCategory.worship,
				bonus='TXT_KEY_BELIEF_GURDWARA_BONUS'
			)
		elif self == BeliefType.meetingHouse:  # BELIEF_MEETING_HOUSE
			return BeliefData(
				name='TXT_KEY_BELIEF_MEETING_HOUSE_NAME',
				category=BeliefCategory.worship,
				bonus='TXT_KEY_BELIEF_MEETING_HOUSE_BONUS'
			)
		elif self == BeliefType.mosque:  # BELIEF_MOSQUE
			return BeliefData(
				name='TXT_KEY_BELIEF_MOSQUE_NAME',
				category=BeliefCategory.worship,
				bonus='TXT_KEY_BELIEF_MOSQUE_BONUS'
			)
		elif self == BeliefType.pagoda:  # BELIEF_PAGODA
			return BeliefData(
				name='TXT_KEY_BELIEF_PAGODA_NAME',
				category=BeliefCategory.worship,
				bonus='TXT_KEY_BELIEF_PAGODA_BONUS'
			)
		elif self == BeliefType.synagogue:  # BELIEF_SYNAGOGUE
			return BeliefData(
				name='TXT_KEY_BELIEF_SYNAGOGUE_NAME',
				category=BeliefCategory.worship,
				bonus='TXT_KEY_BELIEF_SYNAGOGUE_BONUS'
			)
		elif self == BeliefType.wat:  # BELIEF_WAT
			return BeliefData(
				name='TXT_KEY_BELIEF_WAT_NAME',
				category=BeliefCategory.worship,
				bonus='TXT_KEY_BELIEF_WAT_BONUS'
			)
		elif self == BeliefType.stupa:  # BELIEF_STUPA
			return BeliefData(
				name='TXT_KEY_BELIEF_STUPA_NAME',
				category=BeliefCategory.worship,
				bonus='TXT_KEY_BELIEF_STUPA_BONUS'
			)
		elif self == BeliefType.darEMehr:  # BELIEF_DAR_E_MEHR
			return BeliefData(
				name='TXT_KEY_BELIEF_DAR_E_MEHR_NAME',
				category=BeliefCategory.worship,
				bonus='TXT_KEY_BELIEF_DAR_E_MEHR_BONUS'
			)

		raise InvalidEnumError(self)
