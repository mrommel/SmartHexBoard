from typing import Optional

from smarthexboard.game.base import Yields
from smarthexboard.game.civics import CivicType
from smarthexboard.game.districts import DistrictType
from smarthexboard.game.eras import EraType
from smarthexboard.game.flavors import Flavor, FlavorType
from smarthexboard.game.governments import GovernmentType
from smarthexboard.game.greatworks import GreatWorkSlotType
from smarthexboard.game.specialists import SpecialistSlots, SpecialistType
from smarthexboard.game.techs import TechType
from smarthexboard.map.base import ExtendedEnum


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

	# ancestralHall
	# audienceChamber
	# warlordsThrone
	#
	# medieval
	# medievalWalls
	# workshop
	# armory
	# foreignMinistry
	# grandMastersChapel
	# intelligenceAgency
	# university
	#
	# renaissance
	# renaissanceWalls
	# shipyard
	# bank
	# artMuseum
	# archaeologicalMuseum
	#
	# industrial
	# aquarium
	# coalPowerPlant
	# factory
	# ferrisWheel
	# militaryAcademy
	# sewer
	# stockExchange
	# zoo
	#
	# modern
	# broadcastCenter
	# foodMarket
	# hangar
	# hydroelectricDam
	# nationalHistoryMuseum
	# researchLab
	# royalSociety
	# sanctuary
	# seaport
	# shoppingMall
	# warDepartment
	#
	# atomic
	# airport
	# aquaticsCenter
	# floodBarrier
	# nuclearPowerPlant
	# stadium
	#
	# information
	# --

	def name(self) -> str:
		return self._data().name

	def requiredCivic(self) -> CivicType:
		return self._data().requiredCivic

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

		raise AttributeError(f'cant get data for building {self}')

