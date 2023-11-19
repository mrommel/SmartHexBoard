from typing import Optional

from smarthexboard.smarthexboardlib.game.districts import DistrictType
from smarthexboard.smarthexboardlib.game.flavors import Flavor, FlavorType
from smarthexboard.smarthexboardlib.game.governments import GovernmentType
from smarthexboard.smarthexboardlib.game.greatworks import GreatWorkSlotType
from smarthexboard.smarthexboardlib.game.specialists import SpecialistSlots, SpecialistType
from smarthexboard.smarthexboardlib.game.types import TechType, EraType, CivicType
from smarthexboard.smarthexboardlib.map.types import Yields
from smarthexboard.smarthexboardlib.core.base import ExtendedEnum


class BuildingCategoryType(ExtendedEnum):
	none = 'none'

	government = 'government'
	population = 'population'
	cultural = 'cultural'
	scientific = 'scientific'
	religious = 'religious'
	defensive = 'defensive'
	military = 'military'
	entertainment = 'entertainment'
	economic = 'economic'
	infrastructure = 'infrastructure'
	production = 'production'
	maritime = 'maritime'
	conservation = 'conservation'


class BuildingType:
	pass


class BuildingTypeData:
	def __init__(self, name: str, effects: [str], category: BuildingCategoryType, era: EraType, district: DistrictType,
				 requiredTech: Optional[TechType], requiredCivic: Optional[CivicType],
				 requiredBuildingsOr: [BuildingType], requiredGovernmentsOr: [GovernmentType],
				 obsoleteBuildingsOr: [BuildingType], productionCost: int,
				 goldCost: int, faithCost: int, maintenanceCost: int, yields: Yields, defense: int,
				 slots: [GreatWorkSlotType], specialSlots: Optional[SpecialistSlots], flavors: [Flavor]):
		self.name = name
		self.effects = effects
		self.category = category
		self.era = era
		self.district = district
		self.requiredTech = requiredTech
		self.requiredCivic = requiredCivic
		self.requiredBuildingsOr = requiredBuildingsOr
		self.requiredGovernmentsOr = requiredGovernmentsOr
		self.obsoleteBuildingsOr = obsoleteBuildingsOr
		self.productionCost = productionCost
		self.goldCost = goldCost
		self.faithCost = faithCost
		self.maintenanceCost = maintenanceCost
		self.yields = yields
		self.defense = defense
		self.slots = slots
		self.specialSlots = specialSlots
		self.flavors = flavors


class BuildingType(ExtendedEnum):
	none = 'none'

	# ancient
	ancientWalls = 'ancientWalls'
	barracks = 'barracks'
	granary = 'granary'
	grove = 'grove'
	library = 'library'
	monument = 'monument'
	palace = 'palace'
	shrine = 'shrine'
	waterMill = 'waterMill'

	# classical
	amphitheater = 'amphitheater'
	lighthouse = 'lighthouse'
	stable = 'stable'
	arena = 'arena'
	market = 'market'
	temple = 'temple'
	ancestralHall = 'ancestralHall'
	audienceChamber = 'audienceChamber'
	warlordsThrone = 'warlordsThrone'

	# medieval
	medievalWalls = 'medievalWalls'
	workshop = 'workshop'
	armory = 'armory'
	foreignMinistry = 'foreignMinistry'
	grandMastersChapel = 'grandMastersChapel'
	intelligenceAgency = 'intelligenceAgency'
	university = 'university'

	# renaissance
	renaissanceWalls = 'renaissanceWalls'
	shipyard = 'shipyard'
	bank = 'bank'
	artMuseum = 'artMuseum'
	archaeologicalMuseum = 'archaeologicalMuseum'

	# industrial
	aquarium = 'aquarium'
	coalPowerPlant = 'coalPowerPlant'
	factory = 'factory'
	ferrisWheel = 'ferrisWheel'
	militaryAcademy = 'militaryAcademy'
	sewer = 'sewer'
	stockExchange = 'stockExchange'
	zoo = 'zoo'

	# modern
	# broadcastCenter = 'broadcastCenter'
	# foodMarket = 'foodMarket'
	# hangar = 'hangar'
	# hydroelectricDam = 'hydroelectricDam'
	# nationalHistoryMuseum = 'nationalHistoryMuseum'
	# researchLab = 'researchLab'
	# royalSociety = 'royalSociety'
	# sanctuary = 'sanctuary'
	# seaport = 'seaport'
	# shoppingMall = 'shoppingMall'
	# warDepartment = 'warDepartment'

	# atomic
	# airport = 'airport'
	# aquaticsCenter = 'aquaticsCenter'
	# floodBarrier = 'floodBarrier'
	# nuclearPowerPlant = 'nuclearPowerPlant'
	# stadium = 'stadium'

	# information
	# --

	def name(self) -> str:
		return self._data().name

	def categoryType(self) -> BuildingCategoryType:
		return self._data().category

	def district(self) -> DistrictType:
		return self._data().district

	def requiredCivic(self) -> CivicType:
		return self._data().requiredCivic

	def requiredBuildings(self) -> [BuildingType]:
		return self._data().requiredBuildingsOr

	def obsoleteBuildings(self) -> [BuildingType]:
		return self._data().obsoleteBuildingsOr

	def requiredTech(self) -> TechType:
		return self._data().requiredTech

	def defense(self):
		return self._data().defense

	def yields(self) -> Yields:
		return self._data().yields

	def maintenanceCost(self) -> float:
		return self._data().maintenanceCost

	def productionCost(self) -> float:
		return self._data().productionCost

	def purchaseCost(self) -> int:
		return self._data().productionCost

	def faithCost(self) -> int:
		return self._data().faithCost

	def specialistCount(self) -> int:
		if self._data().specialSlots is None:
			return 0

		return self._data().specialSlots.amount

	def specialistType(self) -> SpecialistType:
		if self._data().specialSlots is None:
			return SpecialistType.none

		return self._data().specialSlots.specialistType

	def slotsForGreatWork(self) -> [GreatWorkSlotType]:
		return self._data().slots

	def _flavors(self) -> [Flavor]:
		return self._data().flavors

	def flavor(self, flavorType: FlavorType) -> int:
		item = next((flavor for flavor in self._flavors() if flavor.flavorType == flavorType), None)

		if item is not None:
			return item.value

		return 0

	def canAddSpecialist(self) -> bool:
		slots = self._data().specialSlots

		if slots is None:
			return False

		return slots.amount > 0

	def _data(self) -> BuildingTypeData:
		# default
		if self == BuildingType.none:
			return BuildingTypeData(
				name='',
				effects=[],
				category=BuildingCategoryType.none,
				era=EraType.ancient,
				district=DistrictType.cityCenter,
				requiredTech=None,
				requiredCivic=None,
				requiredBuildingsOr=[],
				requiredGovernmentsOr=[],
				obsoleteBuildingsOr=[],
				productionCost=0,
				goldCost=-1,
				faithCost=-1,
				maintenanceCost=0,
				yields=Yields(food=0, production=0, gold=0),
				defense=0,
				slots=[],
				specialSlots=None,
				flavors=[]
			)

		# ancient
		elif self == BuildingType.ancientWalls:
			# https://civilization.fandom.com/wiki/Ancient_Walls_(Civ6)
			return BuildingTypeData(
				name='TXT_KEY_BUILDING_ANCIENT_WALL_TITLE',
				effects=[
					'TXT_KEY_BUILDING_ANCIENT_WALL_EFFECT0',
					'TXT_KEY_BUILDING_ANCIENT_WALL_EFFECT1'
				],
				category=BuildingCategoryType.defensive,
				era=EraType.ancient,
				district=DistrictType.cityCenter,
				requiredTech=TechType.masonry,
				requiredCivic=None,
				requiredBuildingsOr=[],
				requiredGovernmentsOr=[],
				obsoleteBuildingsOr=[],
				productionCost=80,
				goldCost=80,
				faithCost=-1,
				maintenanceCost=0,
				yields=Yields(food=0, production=0, gold=0),
				defense=50,
				slots=[],
				specialSlots=None,
				flavors=[
					Flavor(FlavorType.militaryTraining, 7),
					Flavor(FlavorType.offense, 5),
					Flavor(FlavorType.defense, 5),
					Flavor(FlavorType.production, 2),
					Flavor(FlavorType.naval, 2),
					Flavor(FlavorType.tileImprovement, 2)
				]
			)
		elif self == BuildingType.barracks:
			# https://civilization.fandom.com/wiki/Barracks_(Civ6)
			return BuildingTypeData(
				name='TXT_KEY_BUILDING_BARRACKS_TITLE',
				effects=[
					'TXT_KEY_BUILDING_BARRACKS_EFFECT0',
					'TXT_KEY_BUILDING_BARRACKS_EFFECT1',
					'TXT_KEY_BUILDING_BARRACKS_EFFECT2',
					'TXT_KEY_BUILDING_BARRACKS_EFFECT3',
					'TXT_KEY_BUILDING_BARRACKS_EFFECT4',
					'TXT_KEY_BUILDING_BARRACKS_EFFECT5'
				],
				category=BuildingCategoryType.military,
				era=EraType.ancient,
				district=DistrictType.encampment,
				requiredTech=TechType.bronzeWorking,
				requiredCivic=None,
				requiredBuildingsOr=[],
				requiredGovernmentsOr=[],
				obsoleteBuildingsOr=[BuildingType.stable],
				productionCost=90,
				goldCost=90,
				faithCost=-1,
				maintenanceCost=1,
				yields=Yields(food=0, production=2, gold=0, housing=1),
				defense=0,
				slots=[],
				specialSlots=SpecialistSlots(SpecialistType.commander, 1),
				flavors=[
					Flavor(FlavorType.cityDefense, 8),
					Flavor(FlavorType.greatPeople, 5),
					Flavor(FlavorType.defense, 4),
					Flavor(FlavorType.wonder, 1),
					Flavor(FlavorType.production, 1)
				]
			)
		elif self == BuildingType.granary:
			# https://civilization.fandom.com/wiki/Granary_(Civ6)
			return BuildingTypeData(
				name='TXT_KEY_BUILDING_GRANARY_TITLE',
				effects=[
					'TXT_KEY_BUILDING_GRANARY_EFFECT0',
					'TXT_KEY_BUILDING_GRANARY_EFFECT1'
				],
				category=BuildingCategoryType.population,
				era=EraType.ancient,
				district=DistrictType.cityCenter,
				requiredTech=TechType.pottery,
				requiredCivic=None,
				requiredBuildingsOr=[],
				requiredGovernmentsOr=[],
				obsoleteBuildingsOr=[],
				productionCost=65,
				goldCost=65,
				faithCost=-1,
				maintenanceCost=0,
				yields=Yields(food=1, production=0, gold=0, housing=2),
				defense=0,
				slots=[],
				specialSlots=None,
				flavors=[
					Flavor(FlavorType.growth, 10),
					Flavor(FlavorType.greatPeople, 3),
					Flavor(FlavorType.science, 4),
					Flavor(FlavorType.tileImprovement, 3),
					Flavor(FlavorType.gold, 2),
					Flavor(FlavorType.production, 3),
					Flavor(FlavorType.offense, 1),
					Flavor(FlavorType.defense, 1)
				]
			)
		elif self == BuildingType.grove:
			# https://civilization.fandom.com/wiki/Grove_(Civ6)
			return BuildingTypeData(
				name='TXT_KEY_BUILDING_GROVE_TITLE',
				effects=[
					'TXT_KEY_BUILDING_GROVE_EFFECT0',
					'TXT_KEY_BUILDING_GROVE_EFFECT1'
				],
				category=BuildingCategoryType.conservation,
				era=EraType.ancient,
				district=DistrictType.preserve,
				requiredTech=None,
				requiredCivic=CivicType.mysticism,
				requiredBuildingsOr=[],
				requiredGovernmentsOr=[],
				obsoleteBuildingsOr=[],
				productionCost=150,
				goldCost=150,
				faithCost=-1,
				maintenanceCost=0,
				yields=Yields(food=0, production=0, gold=0),
				defense=0,
				slots=[],
				specialSlots=None,
				flavors=[
					Flavor(FlavorType.growth, 3),
					Flavor(FlavorType.religion, 5)
				]
			)
		elif self == BuildingType.library:
			# https://civilization.fandom.com/wiki/Library_(Civ6)
			return BuildingTypeData(
				name='TXT_KEY_BUILDING_LIBRARY_TITLE',
				effects=[
					'TXT_KEY_BUILDING_LIBRARY_EFFECT0',
					'TXT_KEY_BUILDING_LIBRARY_EFFECT1',
					'TXT_KEY_BUILDING_LIBRARY_EFFECT2'
				],
				category=BuildingCategoryType.scientific,
				era=EraType.ancient,
				district=DistrictType.campus,
				requiredTech=TechType.writing,
				requiredCivic=None,
				requiredBuildingsOr=[],
				requiredGovernmentsOr=[],
				obsoleteBuildingsOr=[],
				productionCost=90,
				goldCost=90,
				faithCost=-1,
				maintenanceCost=0,
				yields=Yields(food=0, production=0, gold=0, science=2),
				defense=0,
				slots=[GreatWorkSlotType.written, GreatWorkSlotType.written],
				specialSlots=None,
				flavors=[
					Flavor(FlavorType.science, 8),
					Flavor(FlavorType.greatPeople, 5),
					Flavor(FlavorType.offense, 3),
					Flavor(FlavorType.defense, 3)  # , Flavor(FlavorType.spaceShip, 2)
				]
			)
		elif self == BuildingType.monument:
			# https://civilization.fandom.com/wiki/Monument_(Civ6)
			return BuildingTypeData(
				name='TXT_KEY_BUILDING_MONUMENT_TITLE',
				effects=[
					'TXT_KEY_BUILDING_MONUMENT_EFFECT0',
					'TXT_KEY_BUILDING_MONUMENT_EFFECT1',
					'TXT_KEY_BUILDING_MONUMENT_EFFECT2'
				],
				category=BuildingCategoryType.cultural,
				era=EraType.ancient,
				district=DistrictType.cityCenter,
				requiredTech=None,
				requiredCivic=None,
				requiredBuildingsOr=[],
				requiredGovernmentsOr=[],
				obsoleteBuildingsOr=[],
				productionCost=60,
				goldCost=60,
				faithCost=-1,
				maintenanceCost=0,
				yields=Yields(food=0, production=0, gold=0, culture=2),
				defense=0,
				slots=[],
				specialSlots=None,
				flavors=[
					# Note: The Monument has so many flavors because culture leads to policies,
					# which help with a number of things
					Flavor(FlavorType.culture, 7),
					Flavor(FlavorType.tourism, 3),
					Flavor(FlavorType.expansion, 2),
					Flavor(FlavorType.growth, 2),
					Flavor(FlavorType.wonder, 1),
					Flavor(FlavorType.gold, 1),
					Flavor(FlavorType.greatPeople, 1),
					Flavor(FlavorType.production, 1),
					Flavor(FlavorType.amenities, 1),
					Flavor(FlavorType.science, 1),
					Flavor(FlavorType.diplomacy, 1),
					Flavor(FlavorType.offense, 1),
					Flavor(FlavorType.defense, 1),
					Flavor(FlavorType.cityDefense, 1),
					Flavor(FlavorType.naval, 1),
					Flavor(FlavorType.navalTileImprovement, 1),
					Flavor(FlavorType.religion, 1)
				]
			)
		elif self == BuildingType.palace:
			# https://civilization.fandom.com/wiki/Palace_(Civ6)
			return BuildingTypeData(
				name='TXT_KEY_BUILDING_PALACE_TITLE',
				effects=[
					'TXT_KEY_BUILDING_PALACE_EFFECT0',
					'TXT_KEY_BUILDING_PALACE_EFFECT1',
					'TXT_KEY_BUILDING_PALACE_EFFECT2',
					'TXT_KEY_BUILDING_PALACE_EFFECT3',
					'TXT_KEY_BUILDING_PALACE_EFFECT4',
					'TXT_KEY_BUILDING_PALACE_EFFECT5'
				],
				category=BuildingCategoryType.government,
				era=EraType.ancient,
				district=DistrictType.cityCenter,
				requiredTech=None,
				requiredCivic=None,
				requiredBuildingsOr=[],
				requiredGovernmentsOr=[],
				obsoleteBuildingsOr=[],
				productionCost=0,
				goldCost=-1,
				faithCost=-1,
				maintenanceCost=0,
				yields=Yields(food=0, production=2, gold=5, science=2, culture=1, housing=1),
				defense=25,
				slots=[GreatWorkSlotType.any],
				specialSlots=None,
				flavors=[]
			)
		elif self == BuildingType.shrine:
			# https://civilization.fandom.com/wiki/Shrine_(Civ6)
			return BuildingTypeData(
				name='TXT_KEY_BUILDING_SHRINE_TITLE',
				effects=[
					'TXT_KEY_BUILDING_SHRINE_EFFECT0',
					'TXT_KEY_BUILDING_SHRINE_EFFECT1',
					'TXT_KEY_BUILDING_SHRINE_EFFECT2',
					'TXT_KEY_BUILDING_SHRINE_EFFECT3'
				],
				category=BuildingCategoryType.religious,
				era=EraType.ancient,
				district=DistrictType.holySite,
				requiredTech=TechType.astrology,
				requiredCivic=None,
				requiredBuildingsOr=[],
				requiredGovernmentsOr=[],
				obsoleteBuildingsOr=[],
				productionCost=70,
				goldCost=70,
				faithCost=-1,
				maintenanceCost=1,
				yields=Yields(food=0, production=0, gold=0, faith=2),
				defense=0,
				slots=[],
				specialSlots=SpecialistSlots(SpecialistType.priest, 1),
				flavors=[
					# Note: The Shrine has a number of flavors because religion improves a variety of game aspects
					Flavor(FlavorType.religion, 9),
					Flavor(FlavorType.culture, 4),
					Flavor(FlavorType.gold, 3),
					Flavor(FlavorType.amenities, 3),
					Flavor(FlavorType.expansion, 2),
					Flavor(FlavorType.tourism, 2),
					Flavor(FlavorType.diplomacy, 1),
					Flavor(FlavorType.offense, 1),
					Flavor(FlavorType.defense, 1),
					Flavor(FlavorType.growth, 1)
				]
			)
		elif self == BuildingType.waterMill:
			# https://civilization.fandom.com/wiki/Water_Mill_(Civ6)
			return BuildingTypeData(
				name='TXT_KEY_BUILDING_WATER_MILL_TITLE',
				effects=[
					'TXT_KEY_BUILDING_WATER_MILL_EFFECT0',
					'TXT_KEY_BUILDING_WATER_MILL_EFFECT1',
					'TXT_KEY_BUILDING_WATER_MILL_EFFECT2'
				],
				category=BuildingCategoryType.military,
				era=EraType.ancient,
				district=DistrictType.cityCenter,
				requiredTech=TechType.wheel,
				requiredCivic=None,
				requiredBuildingsOr=[],
				requiredGovernmentsOr=[],
				obsoleteBuildingsOr=[],
				productionCost=80,
				goldCost=80,
				faithCost=-1,
				maintenanceCost=0,
				yields=Yields(food=1, production=1, gold=0),
				defense=0,
				slots=[],
				specialSlots=None,
				flavors=[
					Flavor(FlavorType.growth, 7),
					Flavor(FlavorType.science, 4),
					Flavor(FlavorType.tileImprovement, 3),
					Flavor(FlavorType.production, 3),
					Flavor(FlavorType.offense, 1),
					Flavor(FlavorType.defense, 1)
				]
			)

		# classical
		elif self == BuildingType.amphitheater:
			# https://civilization.fandom.com/wiki/Amphitheater_(Civ6)
			return BuildingTypeData(
				name='TXT_KEY_BUILDING_AMPHITHEATER_TITLE',
				effects=[
					'TXT_KEY_BUILDING_AMPHITHEATER_EFFECT0',
					'TXT_KEY_BUILDING_AMPHITHEATER_EFFECT1',
					'TXT_KEY_BUILDING_AMPHITHEATER_EFFECT2',
					'TXT_KEY_BUILDING_AMPHITHEATER_EFFECT3'
				],
				category=BuildingCategoryType.cultural,
				era=EraType.classical,
				district=DistrictType.entertainmentComplex,
				requiredTech=None,
				requiredCivic=CivicType.dramaAndPoetry,
				requiredBuildingsOr=[],
				requiredGovernmentsOr=[],
				obsoleteBuildingsOr=[],
				productionCost=150,
				goldCost=150,
				faithCost=-1,
				maintenanceCost=1,
				yields=Yields(food=0, production=0, gold=0, culture=2),
				defense=0,
				slots=[GreatWorkSlotType.written, GreatWorkSlotType.written],
				specialSlots=SpecialistSlots(SpecialistType.artist, 1),
				flavors=[
					Flavor(FlavorType.growth, 4),
					Flavor(FlavorType.culture, 8),
					Flavor(FlavorType.wonder, 1)
				]
			)
		elif self == BuildingType.lighthouse:
			# https://civilization.fandom.com/wiki/Lighthouse_(Civ6)
			return BuildingTypeData(
				name='TXT_KEY_BUILDING_LIGHTHOUSE_TITLE',
				effects=[
					'TXT_KEY_BUILDING_LIGHTHOUSE_EFFECT0',
					'TXT_KEY_BUILDING_LIGHTHOUSE_EFFECT1',
					'TXT_KEY_BUILDING_LIGHTHOUSE_EFFECT2',
					'TXT_KEY_BUILDING_LIGHTHOUSE_EFFECT3',
					'TXT_KEY_BUILDING_LIGHTHOUSE_EFFECT4',
					'TXT_KEY_BUILDING_LIGHTHOUSE_EFFECT5'
				],
				category=BuildingCategoryType.cultural,
				era=EraType.classical,
				district=DistrictType.harbor,
				requiredTech=TechType.celestialNavigation,
				requiredCivic=None,
				requiredBuildingsOr=[],
				requiredGovernmentsOr=[],
				obsoleteBuildingsOr=[],
				productionCost=120,
				goldCost=120,
				faithCost=-1,
				maintenanceCost=0,
				yields=Yields(food=1, production=0, gold=1, housing=1),
				defense=0,
				slots=[],
				specialSlots=SpecialistSlots(SpecialistType.captain, 1),
				flavors=[
					Flavor(FlavorType.growth, 7),
					Flavor(FlavorType.science, 4),
					Flavor(FlavorType.navalTileImprovement, 8),
					Flavor(FlavorType.gold, 3),
					Flavor(FlavorType.offense, 1),
					Flavor(FlavorType.defense, 1)
				]
			)
		elif self == BuildingType.stable:
			# https://civilization.fandom.com/wiki/Stable_(Civ6)
			return BuildingTypeData(
				name='TXT_KEY_BUILDING_STABLE_TITLE',
				effects=[
					'TXT_KEY_BUILDING_STABLE_EFFECT0',
					'TXT_KEY_BUILDING_STABLE_EFFECT1',
					'TXT_KEY_BUILDING_STABLE_EFFECT2',
					'TXT_KEY_BUILDING_STABLE_EFFECT3',
					'TXT_KEY_BUILDING_STABLE_EFFECT4',
					'TXT_KEY_BUILDING_STABLE_EFFECT5'
				],
				category=BuildingCategoryType.military,
				era=EraType.classical,
				district=DistrictType.encampment,
				requiredTech=TechType.horsebackRiding,
				requiredCivic=None,
				requiredBuildingsOr=[],
				requiredGovernmentsOr=[],
				obsoleteBuildingsOr=[BuildingType.barracks],
				productionCost=120,
				goldCost=120,
				faithCost=-1,
				maintenanceCost=1,
				yields=Yields(food=0, production=1, gold=0, housing=1),
				defense=0,
				slots=[],
				specialSlots=SpecialistSlots(SpecialistType.commander, 1),
				flavors=[
					Flavor(FlavorType.cityDefense, 6),
					Flavor(FlavorType.greatPeople, 5),
					Flavor(FlavorType.offense, 8),
					Flavor(FlavorType.defense, 4),
					Flavor(FlavorType.wonder, 1),
					Flavor(FlavorType.production, 1)
				]
			)
		elif self == BuildingType.arena:
			# https://civilization.fandom.com/wiki/Arena_(Civ6)
			return BuildingTypeData(
				name='TXT_KEY_BUILDING_ARENA_TITLE',
				effects=[
					'TXT_KEY_BUILDING_ARENA_EFFECT0',
					'TXT_KEY_BUILDING_ARENA_EFFECT1',
					'TXT_KEY_BUILDING_ARENA_EFFECT2'
				],
				category=BuildingCategoryType.entertainment,
				era=EraType.classical,
				district=DistrictType.entertainmentComplex,
				requiredTech=None,
				requiredCivic=CivicType.gamesAndRecreation,
				requiredBuildingsOr=[],
				requiredGovernmentsOr=[],
				obsoleteBuildingsOr=[],
				productionCost=150,
				goldCost=150,
				faithCost=-1,
				maintenanceCost=1,
				yields=Yields(food=0, production=0, gold=0, culture=1),
				defense=0,
				slots=[],
				specialSlots=None,
				flavors=[
					Flavor(FlavorType.culture, 7),
					Flavor(FlavorType.tourism, 3),
					Flavor(FlavorType.expansion, 2),
					Flavor(FlavorType.growth, 2),
					Flavor(FlavorType.wonder, 1),
					Flavor(FlavorType.gold, 1),
					Flavor(FlavorType.greatPeople, 1),
					Flavor(FlavorType.production, 1),
					Flavor(FlavorType.amenities, 1),
					Flavor(FlavorType.science, 1),
					Flavor(FlavorType.diplomacy, 1),
					Flavor(FlavorType.offense, 1),
					Flavor(FlavorType.defense, 1),
					Flavor(FlavorType.cityDefense, 1),
					Flavor(FlavorType.naval, 1),
					Flavor(FlavorType.navalTileImprovement, 1),
					Flavor(FlavorType.religion, 1)
				]
			)
		elif self == BuildingType.market:
			# https://civilization.fandom.com/wiki/Market_(Civ6)
			return BuildingTypeData(
				name='TXT_KEY_BUILDING_MARKET_TITLE',
				effects=[
					'TXT_KEY_BUILDING_MARKET_EFFECT0',
					'TXT_KEY_BUILDING_MARKET_EFFECT1',
					'TXT_KEY_BUILDING_MARKET_EFFECT2'
				],
				category=BuildingCategoryType.economic,
				era=EraType.classical,
				district=DistrictType.commercialHub,
				requiredTech=TechType.currency,
				requiredCivic=None,
				requiredBuildingsOr=[],
				requiredGovernmentsOr=[],
				obsoleteBuildingsOr=[],
				productionCost=120,
				goldCost=120,
				faithCost=-1,
				maintenanceCost=0,
				yields=Yields(food=0, production=0, gold=3),
				defense=0,
				slots=[],
				specialSlots=SpecialistSlots(SpecialistType.merchant, 1),
				flavors=[
					Flavor(FlavorType.cityDefense, 2),
					Flavor(FlavorType.greatPeople, 5),
					Flavor(FlavorType.gold, 8),
					Flavor(FlavorType.offense, 1),
					Flavor(FlavorType.defense, 1),
					Flavor(FlavorType.wonder, 1),
					Flavor(FlavorType.production, 1)
				]
			)
		elif self == BuildingType.ancestralHall:
			# https://civilization.fandom.com/wiki/Ancestral_Hall_(Civ6)
			return BuildingTypeData(
				name="TXT_KEY_BUILDING_ANCESTRAL_HALL_TITLE",
				effects=[
					"TXT_KEY_BUILDING_ANCESTRAL_HALL_EFFECT1",  #
					"TXT_KEY_BUILDING_ANCESTRAL_HALL_EFFECT2",  #
					"TXT_KEY_BUILDING_ANCESTRAL_HALL_EFFECT3"  #
				],
				category=BuildingCategoryType.government,
				era=EraType.classical,
				district=DistrictType.governmentPlaza,
				requiredTech=None,
				requiredCivic=None,
				requiredBuildingsOr=[],
				requiredGovernmentsOr=[
					GovernmentType.autocracy,
					GovernmentType.classicalRepublic,
					GovernmentType.oligarchy
				],
				obsoleteBuildingsOr=[
					BuildingType.audienceChamber,
					BuildingType.warlordsThrone
				],
				productionCost=150,
				goldCost=150,
				faithCost=-1,
				maintenanceCost=1,
				yields=Yields(food=0, production=0, gold=0),
				defense=0,
				slots=[],
				specialSlots=None,
				flavors=[
					Flavor(FlavorType.growth, value=2),
					Flavor(FlavorType.tileImprovement, value=4)
				]
			)
		elif self == BuildingType.audienceChamber:
			# https://civilization.fandom.com/wiki/Audience_Chamber_(Civ6)
			return BuildingTypeData(
				name="TXT_KEY_BUILDING_AUDIENCE_CHAMBER_TITLE",
				effects=[
					"TXT_KEY_BUILDING_AUDIENCE_CHAMBER_EFFECT1",  #
					"TXT_KEY_BUILDING_AUDIENCE_CHAMBER_EFFECT2",  #
					"TXT_KEY_BUILDING_AUDIENCE_CHAMBER_EFFECT3"  #
				],
				category=BuildingCategoryType.government,
				era=EraType.classical,
				district=DistrictType.governmentPlaza,
				requiredTech=None,
				requiredCivic=None,
				requiredBuildingsOr=[],
				requiredGovernmentsOr=[
					GovernmentType.autocracy,
					GovernmentType.classicalRepublic,
					GovernmentType.oligarchy
				],
				obsoleteBuildingsOr=[
					BuildingType.ancestralHall,
					BuildingType.warlordsThrone
				],
				productionCost=150,
				goldCost=150,
				faithCost=-1,
				maintenanceCost=1,
				yields=Yields(food=0, production=0, gold=0),
				defense=0,
				slots=[],
				specialSlots=None,
				flavors=[
					Flavor(FlavorType.growth, value=4),
					Flavor(FlavorType.amenities, value=2)
				]
			)
		elif self == BuildingType.warlordsThrone:
			# https://civilization.fandom.com/wiki/Warlord%27s_Throne_(Civ6)
			return BuildingTypeData(
				name="TXT_KEY_BUILDING_WARLORDS_THRONE_TITLE",
				effects=[
					"TXT_KEY_BUILDING_WARLORDS_THRONE_EFFECT1",  #
				    "TXT_KEY_BUILDING_WARLORDS_THRONE_EFFECT2"  #
				],
				category=BuildingCategoryType.government,
				era=EraType.classical,
				district=DistrictType.governmentPlaza,
				requiredTech=None,
				requiredCivic=None,
				requiredBuildingsOr=[],
				requiredGovernmentsOr=[
					GovernmentType.autocracy,
					GovernmentType.classicalRepublic,
					GovernmentType.oligarchy
				],
				obsoleteBuildingsOr=[
					BuildingType.ancestralHall,
					BuildingType.audienceChamber
				],
				productionCost=150,
				goldCost=150,
				faithCost=-1,
				maintenanceCost=1,
				yields=Yields(food=0, production=0, gold=0),
				defense=0,
				slots=[],
				specialSlots=None,
				flavors=[
					Flavor(FlavorType.production, value=3),
					Flavor(FlavorType.offense, value=2)
				]
			)
		elif self == BuildingType.temple:
			# https://civilization.fandom.com/wiki/Temple_(Civ6)
			return BuildingTypeData(
				name='TXT_KEY_BUILDING_TEMPLE_TITLE',
				effects=[
					'TXT_KEY_BUILDING_TEMPLE_EFFECT0',
					'TXT_KEY_BUILDING_TEMPLE_EFFECT1',
					'TXT_KEY_BUILDING_TEMPLE_EFFECT2',
					'TXT_KEY_BUILDING_TEMPLE_EFFECT3',
					'TXT_KEY_BUILDING_TEMPLE_EFFECT4'
				],
				category=BuildingCategoryType.religious,
				era=EraType.classical,
				district=DistrictType.holySite,
				requiredTech=None,
				requiredCivic=CivicType.theology,
				requiredBuildingsOr=[BuildingType.shrine],
				requiredGovernmentsOr=[],
				obsoleteBuildingsOr=[],
				productionCost=120,
				goldCost=120,
				faithCost=-1,
				maintenanceCost=2,
				yields=Yields(food=0, production=0, gold=0, faith=4),
				defense=0,
				slots=[GreatWorkSlotType.relic],
				specialSlots=SpecialistSlots(SpecialistType.priest, 1),
				flavors=[
					Flavor(FlavorType.greatPeople, 5),
					Flavor(FlavorType.religion, 10)
				]
			)

		# medieval
		elif self == BuildingType.medievalWalls:
			# https://civilization.fandom.com/wiki/Medieval_Walls_(Civ6)
			return BuildingTypeData(
				name="TXT_KEY_BUILDING_MEDIEVAL_WALLS_TITLE",
				effects=[
					"TXT_KEY_BUILDING_MEDIEVAL_WALLS_EFFECT0",
					"TXT_KEY_BUILDING_MEDIEVAL_WALLS_EFFECT1"  #
				],
				category=BuildingCategoryType.defensive,
				era=EraType.medieval,
				district=DistrictType.cityCenter,
				requiredTech=TechType.castles,
				requiredCivic=None,
				requiredBuildingsOr=[BuildingType.ancientWalls],
				requiredGovernmentsOr=[],
				obsoleteBuildingsOr=[],
				productionCost=225,
				goldCost=-1,
				faithCost=-1,
				maintenanceCost=0,
				yields=Yields(food=0, production=0, gold=0, science=0, culture=0, faith=0, housing=0),
				defense=100,
				slots=[],
				specialSlots=None,
				flavors=[
					Flavor(FlavorType.militaryTraining, value=7),
					Flavor(FlavorType.offense, value=5),
					Flavor(FlavorType.defense, value=6),
					Flavor(FlavorType.production, value=2),
					Flavor(FlavorType.naval, value=2),
					Flavor(FlavorType.tileImprovement, value=2)
				]
			)
		elif self == BuildingType.workshop:
			# https://civilization.fandom.com/wiki/Workshop_(Civ6)
			return BuildingTypeData(
				name="TXT_KEY_BUILDING_WORKSHOP_TITLE",
				effects=[
					"TXT_KEY_BUILDING_WORKSHOP_EFFECT0",
					"TXT_KEY_BUILDING_WORKSHOP_EFFECT1",
					"TXT_KEY_BUILDING_WORKSHOP_EFFECT2"
				],
				category=BuildingCategoryType.production,
				era=EraType.medieval,
				district=DistrictType.industrialZone,
				requiredTech=TechType.apprenticeship,
				requiredCivic=None,
				requiredBuildingsOr=[],
				requiredGovernmentsOr=[],
				obsoleteBuildingsOr=[],
				productionCost=195,
				goldCost=195,
				faithCost=-1,
				maintenanceCost=1,
				yields=Yields(food=0, production=2, gold=0, science=0, culture=0, faith=0, housing=0),
				defense=0,
				slots=[],
				specialSlots=SpecialistSlots(SpecialistType.engineer, amount=1),
				flavors=[
					Flavor(FlavorType.production, value=7)
				]
			)
		elif self == BuildingType.armory:
			# https://civilization.fandom.com/wiki/Armory_(Civ6)
			return BuildingTypeData(
				name="TXT_KEY_BUILDING_ARMORY_TITLE",
				effects=[
					"TXT_KEY_BUILDING_ARMORY_EFFECT0",
					"TXT_KEY_BUILDING_ARMORY_EFFECT1",
					"TXT_KEY_BUILDING_ARMORY_EFFECT2",
					"TXT_KEY_BUILDING_ARMORY_EFFECT3",
					"TXT_KEY_BUILDING_ARMORY_EFFECT4",  #
					"TXT_KEY_BUILDING_ARMORY_EFFECT5"  #
				],
				category=BuildingCategoryType.military,
				era=EraType.medieval,
				district=DistrictType.encampment,
				requiredTech=TechType.militaryEngineering,
				requiredCivic=None,
				requiredBuildingsOr=[
					BuildingType.barracks,
					BuildingType.stable
				],
				requiredGovernmentsOr=[],
				obsoleteBuildingsOr=[],
				productionCost=195,
				goldCost=195,
				faithCost=-1,
				maintenanceCost=2,
				yields=Yields(food=2, production=0, gold=0, science=0, culture=0, faith=0, housing=0),
				defense=0,
				slots=[],
				specialSlots=SpecialistSlots(SpecialistType.commander, amount=1),
				flavors=[
					Flavor(FlavorType.cityDefense, value=6),
					Flavor(FlavorType.greatPeople, value=3),
					Flavor(FlavorType.offense, value=8),
					Flavor(FlavorType.defense, value=4),
					Flavor(FlavorType.wonder, value=1),
					Flavor(FlavorType.production, value=1)
				]
			)
		elif self == BuildingType.foreignMinistry:
			#
			return BuildingTypeData(
				name="TXT_KEY_BUILDING_FOREIGN_MINISTRY_TITLE",
				effects=[
					"TXT_KEY_BUILDING_FOREIGN_MINISTRY_EFFECT1",  #
					"TXT_KEY_BUILDING_FOREIGN_MINISTRY_EFFECT2",  #
					"TXT_KEY_BUILDING_FOREIGN_MINISTRY_EFFECT3",  #
					"TXT_KEY_BUILDING_FOREIGN_MINISTRY_EFFECT4"  #
				],
				category=BuildingCategoryType.government,
				era=EraType.medieval,
				district=DistrictType.governmentPlaza,
				requiredTech=None,
				requiredCivic=None,
				requiredBuildingsOr=[],
				requiredGovernmentsOr=[],
				obsoleteBuildingsOr=[
					BuildingType.grandMastersChapel,
					BuildingType.intelligenceAgency
				],
				productionCost=290,
				goldCost=290,
				faithCost=-1,
				maintenanceCost=2,
				yields=Yields(food=0, production=0, gold=0),
				defense=0,
				slots=[],
				specialSlots=None,
				flavors=[
					Flavor(FlavorType.diplomacy, value=6)  # Flavor(FlavorType.cityState, value=6),
				]
			)
		elif self == BuildingType.grandMastersChapel:
			# https://civilization.fandom.com/wiki/Grand_Master%27s_Chapel_(Civ6)
			return BuildingTypeData(
				name="TXT_KEY_BUILDING_GRAND_MASTERS_CHAPEL_TITLE",
				effects=[
					"TXT_KEY_BUILDING_GRAND_MASTERS_CHAPEL_EFFECT1",
					"TXT_KEY_BUILDING_GRAND_MASTERS_CHAPEL_EFFECT2",
					"TXT_KEY_BUILDING_GRAND_MASTERS_CHAPEL_EFFECT3",
					"TXT_KEY_BUILDING_GRAND_MASTERS_CHAPEL_EFFECT4"
				],
				category=BuildingCategoryType.government,
				era=EraType.medieval,
				district=DistrictType.governmentPlaza,
				requiredTech=None,
				requiredCivic=None,
				requiredBuildingsOr=[],
				requiredGovernmentsOr=[],
				obsoleteBuildingsOr=[
					BuildingType.foreignMinistry,
					BuildingType.intelligenceAgency
				],
				productionCost=290,
				goldCost=290,
				faithCost=-1,
				maintenanceCost=2,
				yields=Yields(food=0, production=0, gold=0, faith=5),
				defense=0,
				slots=[],
				specialSlots=None,
				flavors=[
					Flavor(FlavorType.religion, value=6)
				]
			)
		elif self == BuildingType.intelligenceAgency:
			# https://civilization.fandom.com/wiki/Intelligence_Agency_(Civ6)
			return BuildingTypeData(
				name="TXT_KEY_BUILDING_INTELLIGENCE_AGENCY_TITLE",
				effects=[
					"TXT_KEY_BUILDING_INTELLIGENCE_AGENCY_EFFECT1",
					"TXT_KEY_BUILDING_INTELLIGENCE_AGENCY_EFFECT2",
					"TXT_KEY_BUILDING_INTELLIGENCE_AGENCY_EFFECT3"
				],
				category=BuildingCategoryType.government,
				era=EraType.medieval,
				district=DistrictType.governmentPlaza,
				requiredTech=None,
				requiredCivic=None,
				requiredBuildingsOr=[],
				requiredGovernmentsOr=[],
				obsoleteBuildingsOr=[BuildingType.foreignMinistry, BuildingType.grandMastersChapel],
				productionCost=290,
				goldCost=290,
				faithCost=-1,
				maintenanceCost=2,
				yields=Yields(food=0, production=0, gold=0),
				defense=0,
				slots=[],
				specialSlots=None,
				flavors=[
					Flavor(FlavorType.diplomacy, value=4)
				]
			)
		elif self == BuildingType.university:
			# https://civilization.fandom.com/wiki/University_(Civ6)
			return BuildingTypeData(
				name="TXT_KEY_BUILDING_UNIVERSITY_TITLE",
				effects=[
					"TXT_KEY_BUILDING_UNIVERSITY_EFFECT0",
					"TXT_KEY_BUILDING_UNIVERSITY_EFFECT1",
					"TXT_KEY_BUILDING_UNIVERSITY_EFFECT2",
					"TXT_KEY_BUILDING_UNIVERSITY_EFFECT3"
				],
				category=BuildingCategoryType.scientific,
				era=EraType.medieval,
				district=DistrictType.campus,
				requiredTech=TechType.education,
				requiredCivic=None,
				requiredBuildingsOr=[BuildingType.library],
				requiredGovernmentsOr=[],
				obsoleteBuildingsOr=[],
				productionCost=250,
				goldCost=250,
				faithCost=-1,
				maintenanceCost=2,
				yields=Yields(food=0, production=0, gold=0, science=4, housing=1),
				defense=0,
				slots=[],
				specialSlots=SpecialistSlots(SpecialistType.citizen, amount=1),
				flavors=[
					Flavor(FlavorType.science, value=8)
				]
			)

		# renaissance
		elif self == BuildingType.renaissanceWalls:
			# https://civilization.fandom.com/wiki/Renaissance_Walls_(Civ6)
			return BuildingTypeData(
				name="TXT_KEY_BUILDING_RENAISSANCE_WALLS_TITLE",
				effects=[
					"TXT_KEY_BUILDING_RENAISSANCE_WALLS_EFFECT0"
				],
				category=BuildingCategoryType.defensive,
				era=EraType.renaissance,
				district=DistrictType.cityCenter,
				requiredTech=TechType.siegeTactics,
				requiredCivic=None,
				requiredBuildingsOr=[BuildingType.medievalWalls],
				requiredGovernmentsOr=[],
				obsoleteBuildingsOr=[],
				productionCost=305,
				goldCost=-1,
				faithCost=-1,
				maintenanceCost=0,
				yields=Yields(food=0, production=0, gold=0, science=0, culture=0, faith=0, housing=0),
				defense=100,
				slots=[],
				specialSlots=None,
				flavors=[
					Flavor(FlavorType.militaryTraining, value=7),
					Flavor(FlavorType.offense, value=5),
					Flavor(FlavorType.defense, value=7),
					Flavor(FlavorType.production, value=2),
					Flavor(FlavorType.naval, value=2),
					Flavor(FlavorType.tileImprovement, value=2)
				]
			)

		elif self == BuildingType.shipyard:
			# https://civilization.fandom.com/wiki/Shipyard_(Civ6)
			return BuildingTypeData(
				name="TXT_KEY_BUILDING_SHIPYARD_TITLE",
				effects=[
					"TXT_KEY_BUILDING_SHIPYARD_EFFECT0",
					"TXT_KEY_BUILDING_SHIPYARD_EFFECT1",
					"TXT_KEY_BUILDING_SHIPYARD_EFFECT2",
					"TXT_KEY_BUILDING_SHIPYARD_EFFECT3",
					"TXT_KEY_BUILDING_SHIPYARD_EFFECT4"
				],
				category=BuildingCategoryType.maritime,
				era=EraType.renaissance,
				district=DistrictType.harbor,
				requiredTech=TechType.massProduction,
				requiredCivic=None,
				requiredBuildingsOr=[BuildingType.lighthouse],
				requiredGovernmentsOr=[],
				obsoleteBuildingsOr=[],
				productionCost=290,
				goldCost=290,
				faithCost=-1,
				maintenanceCost=2,
				yields=Yields(food=0, production=0, gold=0, science=0, culture=0, faith=0, housing=0),
				defense=0,
				slots=[],
				specialSlots=SpecialistSlots(SpecialistType.citizen, amount=1),
				flavors=[
					Flavor(FlavorType.naval, value=7),
					Flavor(FlavorType.militaryTraining, value=7)
				]
			)
		elif self == BuildingType.bank:
			# https://civilization.fandom.com/wiki/Bank_(Civ6)
			return BuildingTypeData(
				name="TXT_KEY_BUILDING_BANK_TITLE",
				effects=[
					"TXT_KEY_BUILDING_BANK_EFFECT0",
					"TXT_KEY_BUILDING_BANK_EFFECT1",
					"TXT_KEY_BUILDING_BANK_EFFECT2",
					"TXT_KEY_BUILDING_BANK_EFFECT3"
					# +2 Great Works Slots for any type with Great Merchant Giovanni de Medici activated.
				],
				category=BuildingCategoryType.economic,
				era=EraType.renaissance,
				district=DistrictType.commercialHub,
				requiredTech=TechType.banking,
				requiredCivic=None,
				requiredBuildingsOr=[],
				requiredGovernmentsOr=[],
				obsoleteBuildingsOr=[],
				productionCost=290,
				goldCost=290,
				faithCost=-1,
				maintenanceCost=0,
				yields=Yields(food=0, production=0, gold=5),
				defense=0,
				slots=[],
				specialSlots=SpecialistSlots(SpecialistType.citizen, amount=1),
				flavors=[
					Flavor(FlavorType.gold, value=8)
				]
			)
		elif self == BuildingType.artMuseum:
			# https://civilization.fandom.com/wiki/Art_Museum_(Civ6)
			return BuildingTypeData(
				name="TXT_KEY_BUILDING_ART_MUSEUM_TITLE",
				effects=[
					"TXT_KEY_BUILDING_ART_MUSEUM_EFFECT1",
					"TXT_KEY_BUILDING_ART_MUSEUM_EFFECT2",
					"TXT_KEY_BUILDING_ART_MUSEUM_EFFECT3",  #
					"TXT_KEY_BUILDING_ART_MUSEUM_EFFECT4",  #
					"TXT_KEY_BUILDING_ART_MUSEUM_EFFECT5"
				],
				category=BuildingCategoryType.cultural,
				era=EraType.renaissance,
				district=DistrictType.theaterSquare,
				requiredTech=None,
				requiredCivic=CivicType.humanism,
				requiredBuildingsOr=[],
				requiredGovernmentsOr=[],
				obsoleteBuildingsOr=[BuildingType.archaeologicalMuseum],
				productionCost=290,
				goldCost=290,
				faithCost=-1,
				maintenanceCost=2,
				yields=Yields(food=0, production=0, gold=0, culture=2),
				defense=0,
				slots=[GreatWorkSlotType.artwork, GreatWorkSlotType.artwork, GreatWorkSlotType.artwork],
				specialSlots=SpecialistSlots(SpecialistType.citizen, amount=1),
				flavors=[
					Flavor(FlavorType.culture, value=7)
				]
			)
		elif self == BuildingType.archaeologicalMuseum:
			# https://civilization.fandom.com/wiki/Archaeological_Museum_(Civ6)
			return BuildingTypeData(
				name="TXT_KEY_BUILDING_ARCHAEOLOGICAL_MUSEUM_TITLE",
				effects=[
					"TXT_KEY_BUILDING_ARCHAEOLOGICAL_MUSEUM_EFFECT1",
					"TXT_KEY_BUILDING_ARCHAEOLOGICAL_MUSEUM_EFFECT2",
					"TXT_KEY_BUILDING_ARCHAEOLOGICAL_MUSEUM_EFFECT3",  #
					"TXT_KEY_BUILDING_ARCHAEOLOGICAL_MUSEUM_EFFECT4",  #
					"TXT_KEY_BUILDING_ARCHAEOLOGICAL_MUSEUM_EFFECT5",
					"TXT_KEY_BUILDING_ARCHAEOLOGICAL_MUSEUM_EFFECT6"
				],
				category=BuildingCategoryType.cultural,
				era=EraType.renaissance,
				district=DistrictType.theaterSquare,
				requiredTech=None,
				requiredCivic=CivicType.humanism,
				requiredBuildingsOr=[],
				requiredGovernmentsOr=[],
				obsoleteBuildingsOr=[BuildingType.artMuseum],
				productionCost=290,
				goldCost=290,
				faithCost=-1,
				maintenanceCost=2,
				yields=Yields(food=0, production=0, gold=0, culture=2),
				defense=0,
				slots=[GreatWorkSlotType.artifact, GreatWorkSlotType.artifact, GreatWorkSlotType.artifact],
				specialSlots=SpecialistSlots(SpecialistType.citizen, amount=1),
				flavors=[
					Flavor(FlavorType.culture, value=7)
				]
			)

		# industrial
		elif self == BuildingType.aquarium:
			# https://civilization.fandom.com/wiki/Aquarium_(Civ6)
			return BuildingTypeData(
				name="TXT_KEY_BUILDING_AQUARIUM_TITLE",
				effects=[
					"TXT_KEY_BUILDING_AQUARIUM_EFFECT1", #
				    "TXT_KEY_BUILDING_AQUARIUM_EFFECT2" #
				],
				category=BuildingCategoryType.entertainment,
				era=EraType.industrial,
				district=DistrictType.waterPark,
				requiredTech=None,
				requiredCivic=CivicType.naturalHistory,
				requiredBuildingsOr=[BuildingType.ferrisWheel],
				requiredGovernmentsOr=[],
				obsoleteBuildingsOr=[],
				productionCost=360,
				goldCost=360,
				faithCost=-1,
				maintenanceCost=2,
				yields=Yields(food=0, production=0, gold=0),
				defense=0,
				slots=[],
				specialSlots=None,
				flavors=[
					Flavor(FlavorType.amenities, value=5)
				]
			)
		elif self == BuildingType.coalPowerPlant:
			# https://civilization.fandom.com/wiki/Coal_Power_Plant_(Civ6)
			return BuildingTypeData(
				name="TXT_KEY_BUILDING_COAL_POWER_PLANT_TITLE",
				effects=[
					"TXT_KEY_BUILDING_COAL_POWER_PLANT_EFFECT1",  #
					"TXT_KEY_BUILDING_COAL_POWER_PLANT_EFFECT2",  #
					"TXT_KEY_BUILDING_COAL_POWER_PLANT_EFFECT3",
					"TXT_KEY_BUILDING_COAL_POWER_PLANT_EFFECT4",  #
					"TXT_KEY_BUILDING_COAL_POWER_PLANT_EFFECT5",  #
					"TXT_KEY_BUILDING_COAL_POWER_PLANT_EFFECT6"  #
				],
				category=BuildingCategoryType.production,
				era=EraType.industrial,
				district=DistrictType.industrialZone,
				requiredTech=TechType.industrialization,
				requiredCivic=None,
				requiredBuildingsOr=[BuildingType.factory],  # BuildingType.electronicsFactory],
				requiredGovernmentsOr=[],
				obsoleteBuildingsOr=[],
				productionCost=300,
				goldCost=300,
				faithCost=-1,
				maintenanceCost=3,
				yields=Yields(food=0, production=0, gold=0),
				defense=0,
				slots=[],
				specialSlots=SpecialistSlots(SpecialistType.citizen, amount=1),
				flavors=[
					Flavor(FlavorType.production, value=7)
				]
			)
		elif self == BuildingType.factory:
			# https://civilization.fandom.com/wiki/Factory_(Civ6)
			return BuildingTypeData(
				name="TXT_KEY_BUILDING_FACTORY_TITLE",
				effects=[
					"TXT_KEY_BUILDING_FACTORY_EFFECT1",  #
					"TXT_KEY_BUILDING_FACTORY_EFFECT2",  #
					"TXT_KEY_BUILDING_FACTORY_EFFECT3"  #
				],
				category=BuildingCategoryType.production,
				era=EraType.industrial,
				district=DistrictType.industrialZone,
				requiredTech=TechType.industrialization,
				requiredCivic=None,
				requiredBuildingsOr=[BuildingType.workshop],
				requiredGovernmentsOr=[],
				obsoleteBuildingsOr=[],
				productionCost=330,
				goldCost=330,
				faithCost=-1,
				maintenanceCost=2,
				yields=Yields(food=0, production=0, gold=0),
				defense=0,
				slots=[],
				specialSlots=SpecialistSlots(SpecialistType.citizen, amount=1),
				flavors=[
					Flavor(FlavorType.production, value=8)
				]
			)
		elif self == BuildingType.ferrisWheel:
			# https://civilization.fandom.com/wiki/Ferris_Wheel_(Civ6)
			return BuildingTypeData(
				name="TXT_KEY_BUILDING_FERRIS_WHEEL_TITLE",
				effects=[
					"TXT_KEY_BUILDING_FERRIS_WHEEL_EFFECT1",  #
					"TXT_KEY_BUILDING_FERRIS_WHEEL_EFFECT2",  #
					"TXT_KEY_BUILDING_FERRIS_WHEEL_EFFECT3"
				],
				category=BuildingCategoryType.entertainment,
				era=EraType.industrial,
				district=DistrictType.waterPark,
				requiredTech=None,
				requiredCivic=CivicType.naturalHistory,
				requiredBuildingsOr=[],
				requiredGovernmentsOr=[],
				obsoleteBuildingsOr=[],
				productionCost=290,
				goldCost=290,
				faithCost=-1,
				maintenanceCost=1,
				yields=Yields(food=0, production=0, gold=0, culture=3),
				defense=0,
				slots=[],
				specialSlots=None,
				flavors=[
					Flavor(FlavorType.amenities, value=7),
					Flavor(FlavorType.culture, value=4)
				]
			)
		elif self == BuildingType.militaryAcademy:
			# https://civilization.fandom.com/wiki/Military_Academy_(Civ6)
			return BuildingTypeData(
				name="TXT_KEY_BUILDING_MILITARY_ACADEMY_TITLE",
				effects=[
					"TXT_KEY_BUILDING_MILITARY_ACADEMY_EFFECT1",  #
					"TXT_KEY_BUILDING_MILITARY_ACADEMY_EFFECT2",  #
					"TXT_KEY_BUILDING_MILITARY_ACADEMY_EFFECT3",
					"TXT_KEY_BUILDING_MILITARY_ACADEMY_EFFECT4",
					"TXT_KEY_BUILDING_MILITARY_ACADEMY_EFFECT5",
					"TXT_KEY_BUILDING_MILITARY_ACADEMY_EFFECT6",  #
					"TXT_KEY_BUILDING_MILITARY_ACADEMY_EFFECT7",  #
					"TXT_KEY_BUILDING_MILITARY_ACADEMY_EFFECT8"  #
				],
				category=BuildingCategoryType.military,
				era=EraType.industrial,
				district=DistrictType.encampment,
				requiredTech=TechType.militaryScience,
				requiredCivic=None,
				requiredBuildingsOr=[BuildingType.armory],
				requiredGovernmentsOr=[],
				obsoleteBuildingsOr=[],
				productionCost=330,
				goldCost=330,
				faithCost=-1,
				maintenanceCost=2,
				yields=Yields(food=0, production=4, gold=0, housing=1),
				defense=0,
				slots=[],
				specialSlots=SpecialistSlots(SpecialistType.citizen, amount=1),
				flavors=[
					Flavor(FlavorType.offense, value=4),
					Flavor(FlavorType.production, value=4)
				]
			)
		elif self == BuildingType.sewer:
			# https://civilization.fandom.com/wiki/Sewer_(Civ6)
			return BuildingTypeData(
				name="TXT_KEY_BUILDING_SEWER_TITLE",
				effects=[
					"TXT_KEY_BUILDING_SEWER_EFFECT1"
				],
				category=BuildingCategoryType.infrastructure,
				era=EraType.industrial,
				district=DistrictType.cityCenter,
				requiredTech=TechType.sanitation,
				requiredCivic=None,
				requiredBuildingsOr=[],
				requiredGovernmentsOr=[],
				obsoleteBuildingsOr=[],
				productionCost=200,
				goldCost=200,
				faithCost=-1,
				maintenanceCost=2,
				yields=Yields(food=0, production=0, gold=0, housing=2),
				defense=0,
				slots=[],
				specialSlots=None,
				flavors=[
					Flavor(FlavorType.growth, value=7)
				]
			)
		elif self == BuildingType.stockExchange:
			# https://civilization.fandom.com/wiki/Stock_Exchange_(Civ6)
			return BuildingTypeData(
				name="TXT_KEY_BUILDING_STOCK_EXCHANGE_TITLE",
				effects=[
					"TXT_KEY_BUILDING_STOCK_EXCHANGE_EFFECT1",  #
					"TXT_KEY_BUILDING_STOCK_EXCHANGE_EFFECT2",
					"TXT_KEY_BUILDING_STOCK_EXCHANGE_EFFECT3",  #
					"TXT_KEY_BUILDING_STOCK_EXCHANGE_EFFECT4"  #
				],
				category=BuildingCategoryType.economic,
				era=EraType.industrial,
				district=DistrictType.commercialHub,
				requiredTech=TechType.economics,
				requiredCivic=None,
				requiredBuildingsOr=[BuildingType.bank],
				requiredGovernmentsOr=[],
				obsoleteBuildingsOr=[],
				productionCost=330,
				goldCost=330,
				faithCost=-1,
				maintenanceCost=0,
				yields=Yields(food=0, production=0, gold=7),
				defense=0,
				slots=[],
				specialSlots=SpecialistSlots(SpecialistType.citizen, amount=1),
				flavors=[
					Flavor(FlavorType.gold, value=10)
				]
			)
		elif self == BuildingType.zoo:
			# https://civilization.fandom.com/wiki/Zoo_(Civ6)
			return BuildingTypeData(
				name="TXT_KEY_BUILDING_ZOO_TITLE",
				effects=[
					"TXT_KEY_BUILDING_ZOO_EFFECT1",  #
					"TXT_KEY_BUILDING_ZOO_EFFECT2"  #
				],
				category=BuildingCategoryType.entertainment,
				era=EraType.industrial,
				district=DistrictType.entertainmentComplex,
				requiredTech=None,
				requiredCivic=CivicType.naturalHistory,
				requiredBuildingsOr=[BuildingType.arena],
				requiredGovernmentsOr=[],
				obsoleteBuildingsOr=[],
				productionCost=360,
				goldCost=360,
				faithCost=-1,
				maintenanceCost=2,
				yields=Yields(food=0, production=0, gold=0),
				defense=0,
				slots=[],
				specialSlots=None,
				flavors=[
					Flavor(FlavorType.amenities, value=6)
				]
			)

		# modern
		# elif self == BuildingType.broadcastCenter:
		# 	#
		# 	return BuildingTypeData(
		# 	)
		# elif self == BuildingType.foodMarket:
		# 	#
		# 	return BuildingTypeData(
		# 	)
		# elif self == BuildingType.hangar:
		# 	#
		# 	return BuildingTypeData(
		# 	)
		# elif self == BuildingType.hydroelectricDam:
		# 	#
		# 	return BuildingTypeData(
		# 	)
		# elif self == BuildingType.nationalHistoryMuseum:
		# 	#
		# 	return BuildingTypeData(
		# 	)
		# elif self == BuildingType.researchLab:
		# 	#
		# 	return BuildingTypeData(
		# 	)
		# elif self == BuildingType.royalSociety:
		# 	#
		# 	return BuildingTypeData(
		# 	)
		# elif self == BuildingType.sanctuary:
		# 	#
		# 	return BuildingTypeData(
		# 	)
		# elif self == BuildingType.seaport:
		# 	#
		# 	return BuildingTypeData(
		# 	)
		# elif self == BuildingType.shoppingMall:
		# 	#
		# 	return BuildingTypeData(
		# 	)
		# elif self == BuildingType.warDepartment:
		# 	#
		# 	return BuildingTypeData(
		# 	)
		#
		# # atomic
		# elif self == BuildingType.airport:
		# 	#
		# 	return BuildingTypeData(
		# 	)
		# elif self == BuildingType.aquaticsCenter:
		# 	#
		# 	return BuildingTypeData(
		# 	)
		# elif self == BuildingType.floodBarrier:
		# 	#
		# 	return BuildingTypeData(
		# 	)
		# elif self == BuildingType.nuclearPowerPlant:
		# 	#
		# 	return BuildingTypeData(
		# 	)
		# elif self == BuildingType.stadium:
		# 	#
		# 	return BuildingTypeData(
		# 	)

		# information
		# --

		raise AttributeError(f'cant get data for building {self}')

	def amenities(self) -> int:
		# @fixme move to data
		if self == BuildingType.arena:
			return 1

		return 0

	def canBuildIn(self, city, simulation) -> bool:
		if self == BuildingType.waterMill:
			# It can be built in the City Center, if the city is next to a River.
			return simulation.riverAt(city.location)

		return True
