from typing import Optional

from smarthexboard.smarthexboardlib.game.flavors import Flavor, FlavorType
from smarthexboard.smarthexboardlib.game.types import CivicType, TechType
from smarthexboard.smarthexboardlib.map.base import HexPoint
from smarthexboard.smarthexboardlib.map.types import Yields, TerrainType, FeatureType
from smarthexboard.smarthexboardlib.core.base import ExtendedEnum, InvalidEnumError


class DistrictTypeData:
	def __init__(self, name: str, specialty: bool, effects: [str], productionCost: int, maintenanceCost: int,
	             requiredTech: Optional[TechType], requiredCivic: Optional[CivicType], domesticTradeYields: Yields,
	             foreignTradeYields: Yields, flavors: [Flavor], oncePerCivilization: bool = False):
		self.name = name
		self.specialty = specialty
		self.effects = effects
		self.productionCost = productionCost
		self.maintenanceCost = maintenanceCost
		self.requiredTech = requiredTech
		self.requiredCivic = requiredCivic

		self.domesticTradeYields = domesticTradeYields
		self.foreignTradeYields = foreignTradeYields

		self.flavors = flavors
		self.oncePerCivilization = oncePerCivilization


class DistrictType(ExtendedEnum):
	none = 'none'

	cityCenter = 'cityCenter'
	preserve = 'preserve'
	encampment = 'encampment'
	campus = 'campus'
	entertainmentComplex = 'entertainmentComplex'
	commercialHub = 'commercialHub'
	harbor = 'harbor'
	holySite = 'holySite'
	neighborhood = 'neighborhood'
	governmentPlaza = 'governmentPlaza'
	aqueduct = 'aqueduct'
	industrialZone = 'industrialZone'
	theaterSquare = 'theaterSquare'
	spaceport = 'spaceport'
	waterPark = 'waterPark'

	def title(self) -> str:  # cannot use 'name'
		return self._data().name

	def requiredCivic(self) -> Optional[CivicType]:
		return self._data().requiredCivic

	def requiredTech(self) -> Optional[TechType]:
		return self._data().requiredTech

	def maintenanceCost(self) -> float:
		return self._data().maintenanceCost

	def _flavors(self) -> [Flavor]:
		return self._data().flavors

	def flavor(self, flavorType: FlavorType) -> int:
		item = next((flavor for flavor in self._flavors() if flavor.flavorType == flavorType), None)

		if item is not None:
			return item.value

		return 0

	def productionCost(self) -> int:
		return self._data().productionCost

	def yields(self) -> Yields:
		return Yields(food=0, production=0, gold=0)

	def domesticTradeYields(self) -> Yields:
		return self._data().domesticTradeYields

	def foreignTradeYields(self) -> Yields:
		return self._data().foreignTradeYields

	def _data(self) -> DistrictTypeData:
		if self == DistrictType.none:
			return DistrictTypeData(
				name='TXT_KEY_DISTRICT_NONE_TITLE',
				specialty=False,
				effects=[],
				productionCost=-1,
				maintenanceCost=-1,
				requiredTech=None,
				requiredCivic=None,
				domesticTradeYields=Yields(food=0.0, production=0.0, gold=0.0),
				foreignTradeYields=Yields(food=0.0, production=0.0, gold=0.0),
				flavors=[]
			)
		elif self == DistrictType.cityCenter:
			# https://civilization.fandom.com/wiki/City_Center_(Civ6)
			return DistrictTypeData(
				name='TXT_KEY_DISTRICT_CITY_CENTER_TITLE',
				specialty=False,
				effects=[
					'TXT_KEY_DISTRICT_CITY_CENTER_EFFECT1'
				],
				productionCost=0,
				maintenanceCost=0,
				requiredTech=None,
				requiredCivic=None,
				domesticTradeYields=Yields(food=1.0, production=1.0, gold=0.0),
				foreignTradeYields=Yields(food=0.0, production=0.0, gold=3.0),
				flavors=[
					Flavor(FlavorType.cityDefense, 7)
				]
			)
		elif self == DistrictType.preserve:
			# https://civilization.fandom.com/wiki/Preserve_(Civ6)
			return DistrictTypeData(
				name='TXT_KEY_DISTRICT_PRESERVE_TITLE',
				specialty=True,
				effects=[
					'TXT_KEY_DISTRICT_PRESERVE_EFFECT1',
					'TXT_KEY_DISTRICT_PRESERVE_EFFECT2',
					'TXT_KEY_DISTRICT_PRESERVE_EFFECT3'
				],
				productionCost=54,
				maintenanceCost=0,
				requiredTech=None,
				requiredCivic=CivicType.mysticism,
				domesticTradeYields=Yields(food=0, production=0, gold=0),
				foreignTradeYields=Yields(food=0, production=0, gold=0),
				flavors=[
					Flavor(FlavorType.culture, 6)
				]
			)
		elif self == DistrictType.encampment:
			# https://civilization.fandom.com/wiki/Encampment_(Civ6)
			return DistrictTypeData(
				name='TXT_KEY_DISTRICT_ENCAMPMENT_TITLE',
				specialty=True,
				effects=[
					'TXT_KEY_DISTRICT_ENCAMPMENT_EFFECT1',
					'TXT_KEY_DISTRICT_ENCAMPMENT_EFFECT2',
					'TXT_KEY_DISTRICT_ENCAMPMENT_EFFECT3',
					'TXT_KEY_DISTRICT_ENCAMPMENT_EFFECT4',
					'TXT_KEY_DISTRICT_ENCAMPMENT_EFFECT5',
					'TXT_KEY_DISTRICT_ENCAMPMENT_EFFECT6',
					'TXT_KEY_DISTRICT_ENCAMPMENT_EFFECT7',
					'TXT_KEY_DISTRICT_ENCAMPMENT_EFFECT8',
					'TXT_KEY_DISTRICT_ENCAMPMENT_EFFECT9'
				],
				productionCost=54,
				maintenanceCost=0,
				requiredTech=TechType.bronzeWorking,
				requiredCivic=None,
				domesticTradeYields=Yields(food=0.0, production=1.0, gold=0.0),
				foreignTradeYields=Yields(food=0.0, production=1.0, gold=0.0),
				flavors=[
					Flavor(FlavorType.militaryTraining, value=7),
					Flavor(FlavorType.cityDefense, value=3)
				]
			)
		elif self == DistrictType.campus:
			# https://civilization.fandom.com/wiki/Campus_(Civ6)
			return DistrictTypeData(
				name='TXT_KEY_DISTRICT_CAMPUS_TITLE',
				specialty=True,
				effects=[
					'TXT_KEY_DISTRICT_CAMPUS_EFFECT1',
					'TXT_KEY_DISTRICT_CAMPUS_EFFECT2',
					'TXT_KEY_DISTRICT_CAMPUS_EFFECT3',
					'TXT_KEY_DISTRICT_CAMPUS_EFFECT4',
					'TXT_KEY_DISTRICT_CAMPUS_EFFECT5',
					'TXT_KEY_DISTRICT_CAMPUS_EFFECT6'
				],
				productionCost=54,
				maintenanceCost=1,
				requiredTech=TechType.writing,
				requiredCivic=None,
				domesticTradeYields=Yields(food=1.0, production=0.0, gold=0.0),
				foreignTradeYields=Yields(food=0.0, production=0.0, gold=0.0, science=1.0),
				flavors=[
					Flavor(FlavorType.science, 8)
				]
			)
		elif self == DistrictType.entertainmentComplex:
			# https://civilization.fandom.com/wiki/Entertainment_Complex_(Civ6)
			return DistrictTypeData(
				name='TXT_KEY_DISTRICT_ENTERTAINMENT_COMPLEX_TITLE',
				specialty=True,
				effects=[
					'TXT_KEY_DISTRICT_ENTERTAINMENT_COMPLEX_EFFECT1',
					'TXT_KEY_DISTRICT_ENTERTAINMENT_COMPLEX_EFFECT2',
					'TXT_KEY_DISTRICT_ENTERTAINMENT_COMPLEX_EFFECT3',
					'TXT_KEY_DISTRICT_ENTERTAINMENT_COMPLEX_EFFECT4',
					'TXT_KEY_DISTRICT_ENTERTAINMENT_COMPLEX_EFFECT5'
				],
				productionCost=54,
				maintenanceCost=1,
				requiredTech=None,
				requiredCivic=CivicType.gamesAndRecreation,
				domesticTradeYields=Yields(food=1.0, production=0.0, gold=0.0),
				foreignTradeYields=Yields(food=1.0, production=0.0, gold=0.0),
				flavors=[
					Flavor(FlavorType.amenities, 7)
				]
			)
		elif self == DistrictType.commercialHub:
			# https://civilization.fandom.com/wiki/Commercial_Hub_(Civ6)
			return DistrictTypeData(
				name='TXT_KEY_DISTRICT_COMMERCIAL_HUB_TITLE',
				specialty=True,
				effects=[
					'TXT_KEY_DISTRICT_COMMERCIAL_HUB_EFFECT1',
					'TXT_KEY_DISTRICT_COMMERCIAL_HUB_EFFECT2',
					'TXT_KEY_DISTRICT_COMMERCIAL_HUB_EFFECT3',
					'TXT_KEY_DISTRICT_COMMERCIAL_HUB_EFFECT4',
					'TXT_KEY_DISTRICT_COMMERCIAL_HUB_EFFECT5'
				],
				productionCost=54,
				maintenanceCost=0,
				requiredTech=TechType.currency,
				requiredCivic=None,
				domesticTradeYields=Yields(food=0.0, production=1.0, gold=0.0),
				foreignTradeYields=Yields(food=0.0, production=0.0, gold=3.0),
				flavors=[
					Flavor(FlavorType.gold, 7)
				]
			)
		elif self == DistrictType.harbor:
			# https://civilization.fandom.com/wiki/Harbor_(Civ6)
			return DistrictTypeData(
				name='TXT_KEY_DISTRICT_HARBOR_TITLE',
				specialty=True,
				effects=[
					'TXT_KEY_DISTRICT_HARBOR_EFFECT1',
					'TXT_KEY_DISTRICT_HARBOR_EFFECT2',
					'TXT_KEY_DISTRICT_HARBOR_EFFECT3',
					'TXT_KEY_DISTRICT_HARBOR_EFFECT4',
					'TXT_KEY_DISTRICT_HARBOR_EFFECT5',
					'TXT_KEY_DISTRICT_HARBOR_EFFECT6',
					'TXT_KEY_DISTRICT_HARBOR_EFFECT7',
					'TXT_KEY_DISTRICT_HARBOR_EFFECT8',
					'TXT_KEY_DISTRICT_HARBOR_EFFECT9',
					'TXT_KEY_DISTRICT_HARBOR_EFFECT10',
					'TXT_KEY_DISTRICT_HARBOR_EFFECT11',
					'TXT_KEY_DISTRICT_HARBOR_EFFECT12'
				],
				productionCost=54,
				maintenanceCost=0,
				requiredTech=TechType.celestialNavigation,
				requiredCivic=None,
				domesticTradeYields=Yields(food=0.0, production=1.0, gold=0.0),
				foreignTradeYields=Yields(food=0.0, production=0.0, gold=3.0),
				flavors=[
					Flavor(FlavorType.naval, value=3),
					Flavor(FlavorType.navalGrowth, value=7)
				]
			)
		elif self == DistrictType.holySite:
			# https://civilization.fandom.com/wiki/Holy_Site_(Civ6)
			return DistrictTypeData(
				name='TXT_KEY_DISTRICT_HOLY_SITE_TITLE',
				specialty=True,
				effects=[
					'TXT_KEY_DISTRICT_HOLY_SITE_EFFECT1',
					'TXT_KEY_DISTRICT_HOLY_SITE_EFFECT2',
					'TXT_KEY_DISTRICT_HOLY_SITE_EFFECT3',
					'TXT_KEY_DISTRICT_HOLY_SITE_EFFECT4',
					'TXT_KEY_DISTRICT_HOLY_SITE_EFFECT5',
					'TXT_KEY_DISTRICT_HOLY_SITE_EFFECT6',
					'TXT_KEY_DISTRICT_HOLY_SITE_EFFECT7',
					'TXT_KEY_DISTRICT_HOLY_SITE_EFFECT8',
					'TXT_KEY_DISTRICT_HOLY_SITE_EFFECT9',
					'TXT_KEY_DISTRICT_HOLY_SITE_EFFECT10'
				],
				productionCost=54,
				maintenanceCost=1,
				requiredTech=TechType.astrology,
				requiredCivic=None,
				domesticTradeYields=Yields(food=1.0, production=0.0, gold=0.0),
				foreignTradeYields=Yields(food=0.0, production=0.0, gold=0.0, faith=1.0),
				flavors=[
					Flavor(FlavorType.religion, 7)
				]
			)
		elif self == DistrictType.neighborhood:
			# https://civilization.fandom.com/wiki/Neighborhood_(Civ6)
			return DistrictTypeData(
				name='TXT_KEY_DISTRICT_NEIGHBORHOOD_TITLE',
				specialty=False,
				effects=[
					'TXT_KEY_DISTRICT_NEIGHBORHOOD_EFFECT1'
				],
				productionCost=54,
				maintenanceCost=0,
				requiredTech=None,
				requiredCivic=CivicType.urbanization,
				domesticTradeYields=Yields(food=0.0, production=0.0, gold=0.0),
				foreignTradeYields=Yields(food=0.0, production=0.0, gold=0.0),
				flavors=[
					Flavor(FlavorType.growth, 2),
					Flavor(FlavorType.expansion, 3)
				]
			)
		elif self == DistrictType.governmentPlaza:
			# https://civilization.fandom.com/wiki/Government_Plaza_(Civ6)
			return DistrictTypeData(
				name="TXT_KEY_DISTRICT_GOVERNMENT_PLAZA_TITLE",
				specialty=True,
				effects=[
					"TXT_KEY_DISTRICT_GOVERNMENT_PLAZA_EFFECT1",
					"TXT_KEY_DISTRICT_GOVERNMENT_PLAZA_EFFECT2",
					"TXT_KEY_DISTRICT_GOVERNMENT_PLAZA_EFFECT3"
				],
				productionCost=30,
				maintenanceCost=1,
				requiredTech=None,
				requiredCivic=CivicType.stateWorkforce,
				domesticTradeYields=Yields(food=1, production=1, gold=0),
				foreignTradeYields=Yields(food=0, production=0, gold=2),
				flavors=[
					Flavor(FlavorType.diplomacy, 8)
				],
				oncePerCivilization=True
			)

		elif self == DistrictType.aqueduct:
			# https://civilization.fandom.com/wiki/Aqueduct_(Civ6)
			return DistrictTypeData(
				name="TXT_KEY_DISTRICT_AQUEDUCT_TITLE",
				specialty=False,
				effects=[
					"TXT_KEY_DISTRICT_AQUEDUCT_EFFECT1",
					"TXT_KEY_DISTRICT_AQUEDUCT_EFFECT2",
					"TXT_KEY_DISTRICT_AQUEDUCT_EFFECT3",
					"TXT_KEY_DISTRICT_AQUEDUCT_EFFECT4",
					"TXT_KEY_DISTRICT_AQUEDUCT_EFFECT5",
					"TXT_KEY_DISTRICT_AQUEDUCT_EFFECT6"
				],
				productionCost=36,
				maintenanceCost=0,
				requiredTech=TechType.engineering,
				requiredCivic=None,
				domesticTradeYields=Yields(food=0.0, production=0.0, gold=0.0),
				foreignTradeYields=Yields(food=0.0, production=0.0, gold=0.0),
				flavors=[
					Flavor(FlavorType.tileImprovement, value=7),
					Flavor(FlavorType.growth, value=2)
				]
			)
		elif self == DistrictType.industrialZone:
			# https://civilization.fandom.com/wiki/Industrial_Zone_(Civ6)
			return DistrictTypeData(
				name="TXT_KEY_DISTRICT_INDUSTRIAL_ZONE_TITLE",
				specialty=True,
				effects=[
					"TXT_KEY_DISTRICT_INDUSTRIAL_ZONE_EFFECT1",
					"TXT_KEY_DISTRICT_INDUSTRIAL_ZONE_EFFECT2",
					"TXT_KEY_DISTRICT_INDUSTRIAL_ZONE_EFFECT3",
					"TXT_KEY_DISTRICT_INDUSTRIAL_ZONE_EFFECT4",
					"TXT_KEY_DISTRICT_INDUSTRIAL_ZONE_EFFECT5",
					"TXT_KEY_DISTRICT_INDUSTRIAL_ZONE_EFFECT6"
				],
				productionCost=54,
				maintenanceCost=0,
				requiredTech=TechType.apprenticeship,
				requiredCivic=None,
				domesticTradeYields=Yields(food=0.0, production=1.0, gold=0.0),
				foreignTradeYields=Yields(food=0.0, production=1.0, gold=0.0),
				flavors=[
					Flavor(FlavorType.production, value=9)
				]
			)
		elif self == DistrictType.theaterSquare:
			# https://civilization.fandom.com/wiki/Theater_Square_(Civ6)
			return DistrictTypeData(
				name="TXT_KEY_DISTRICT_THEATER_SQUARE_TITLE",
				specialty=True,
				effects=[
					"TXT_KEY_DISTRICT_THEATER_SQUARE_EFFECT1",
					"TXT_KEY_DISTRICT_THEATER_SQUARE_EFFECT2",
					"TXT_KEY_DISTRICT_THEATER_SQUARE_EFFECT3",
					"TXT_KEY_DISTRICT_THEATER_SQUARE_EFFECT4",
					"TXT_KEY_DISTRICT_THEATER_SQUARE_EFFECT5",
					"TXT_KEY_DISTRICT_THEATER_SQUARE_EFFECT6",
					"TXT_KEY_DISTRICT_THEATER_SQUARE_EFFECT7",
					"TXT_KEY_DISTRICT_THEATER_SQUARE_EFFECT8",
					"TXT_KEY_DISTRICT_THEATER_SQUARE_EFFECT9"
				],
				productionCost=54,
				maintenanceCost=1,
				requiredTech=None,
				requiredCivic=CivicType.dramaAndPoetry,
				domesticTradeYields=Yields(food=0.0, production=0.0, gold=0.0),
				foreignTradeYields=Yields(food=0.0, production=0.0, gold=0.0),
				flavors=[
					Flavor(FlavorType.culture, value=6),
					Flavor(FlavorType.greatPeople, value=4)
				]
			)
		elif self == DistrictType.spaceport:
			# https://civilization.fandom.com/wiki/Spaceport_(Civ6)
			return DistrictTypeData(
				name="TXT_KEY_DISTRICT_SPACEPORT_TITLE",
				specialty=False,
				effects=[
					"TXT_KEY_DISTRICT_SPACEPORT_EFFECT1"
				],
				productionCost=1800,
				maintenanceCost=0,
				requiredTech=TechType.rocketry,
				requiredCivic=None,
				domesticTradeYields=Yields(food=0.0, production=0.0, gold=0.0),
				foreignTradeYields=Yields(food=0.0, production=0.0, gold=0.0),
				flavors=[
					Flavor(FlavorType.science, value=7)
				]
			)
		elif self == DistrictType.waterPark:
			# https://civilization.fandom.com/wiki/Water_Park_(Civ6)
			return DistrictTypeData(
				name="TXT_KEY_DISTRICT_WATER_PARK_TITLE",
				specialty=True,
				effects=[
					"TXT_KEY_DISTRICT_WATER_PARK_EFFECT1"
				],
				productionCost=54,
				maintenanceCost=1,
				requiredTech=None,
				requiredCivic=CivicType.naturalHistory,
				domesticTradeYields=Yields(food=1.0, production=0.0, gold=0.0),
				foreignTradeYields=Yields(food=1.0, production=0.0, gold=0.0),
				flavors=[
					Flavor(FlavorType.growth, value=4),
					Flavor(FlavorType.amenities, value=5)
				]
			)

		raise AttributeError(f'cant get data for district {self}')

	def isSpecialty(self):
		return self._data().specialty

	def oncePerCivilization(self):
		return self._data().oncePerCivilization

	def canBuildOn(self, point, simulation) -> bool:
		tile = simulation.tileAt(point)

		# Districts and wonders(except for Machu Picchu) cannot be placed on Mountains tiles.
		if tile.hasFeature(FeatureType.mountains):
			return False

		# natural wonders can't be used for districts
		if tile.feature().isNaturalWonder():
			return False

		if self == DistrictType.none:
			return False
		elif self == DistrictType.cityCenter:
			return True
		elif self == DistrictType.campus:
			return tile.isLand()
		elif self == DistrictType.theaterSquare:
			return tile.isLand()
		elif self == DistrictType.holySite:
			return tile.isLand()
		elif self == DistrictType.encampment:
			return tile.isLand()
		elif self == DistrictType.commercialHub:
			return tile.isLand()
		elif self == DistrictType.harbor:
			# must be built on water adjacent to land
			return tile.terrain() == TerrainType.shore
		elif self == DistrictType.entertainmentComplex:
			return tile.isLand()
		elif self == DistrictType.industrialZone:
			return tile.isLand()
		elif self == DistrictType.waterPark:
			# must be built on a Coast or Lake tile adjacent to land.
			return tile.terrain() == TerrainType.shore or tile.hasFeature(FeatureType.lake)
		elif self == DistrictType.aqueduct:
			return DistrictType.canBuildAqueductOn(tile.point, simulation)
		elif self == DistrictType.neighborhood:
			return tile.isLand()
		# canal
		# dam
		# areodrome
		elif self == DistrictType.preserve:
			return DistrictType.canBuildPreserveOn(tile.point, simulation)  # Cannot be adjacent to the City Center
		elif self == DistrictType.spaceport:
			return tile.isLand() and not tile.isHills()
		elif self == DistrictType.governmentPlaza:
			return tile.isLand()

		raise InvalidEnumError(self)

	@staticmethod
	def canBuildAqueductOn(point, simulation):
		tile = simulation.tileAt(point)

		# Must be built adjacent to both the City Center and one of the following: River, Lake, Oasis, or Mountain.
		nextToCityCenter: bool = False
		nextToWaterSource: bool = False

		for neighbor in point.neighbors():
			neighborTile = simulation.tileAt(neighbor)

			if neighborTile is None:
				continue

			if neighborTile.isRiver() or neighborTile.hasFeature(FeatureType.lake) or \
				neighborTile.hasFeature(FeatureType.oasis) or \
				neighborTile.hasFeature(FeatureType.mountains):
				nextToWaterSource = True

			if tile.workingCity() is not None and tile.workingCity().location == neighbor:
				nextToCityCenter = True

		return nextToCityCenter and nextToWaterSource

	@staticmethod
	def canBuildPreserveOn(point: HexPoint, simulation) -> bool:
		"""Cannot be adjacent to the City Center"""
		tile = simulation.tileAt(point)

		for neighbor in point.neighbors():
			if simulation.cityAt(neighbor) is not None:
				return False

		return tile.isLand()
