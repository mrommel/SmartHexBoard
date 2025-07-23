from typing import List

from smarthexboard.smarthexboardlib.core.base import ExtendedEnum
from smarthexboard.smarthexboardlib.core.types import EraType
from smarthexboard.smarthexboardlib.game.flavors import Flavor, FlavorType
from gettext import gettext as _


class OperationHelpers:
	@staticmethod
	def gatherRangeFor(numberOfUnits: int) -> int:
		if numberOfUnits <= 2:
			return 1
		elif numberOfUnits <= 6:
			return 2
		elif numberOfUnits <= 10:
			return 3
		else:
			return 4


class CityFocusType(ExtendedEnum):
	none = 'none'  # NO_CITY_AI_FOCUS_TYPE
	food = 'food'  # CITY_AI_FOCUS_TYPE_FOOD,
	production = 'production'  # CITY_AI_FOCUS_TYPE_PRODUCTION,
	gold = 'gold'  # CITY_AI_FOCUS_TYPE_GOLD,
	greatPeople = 'greatPeople'  # CITY_AI_FOCUS_TYPE_GREAT_PEOPLE,
	science = 'science'  # CITY_AI_FOCUS_TYPE_SCIENCE,
	culture = 'culture'  # CITY_AI_FOCUS_TYPE_CULTURE,
	productionGrowth = 'productionGrowth'  # CITY_AI_FOCUS_TYPE_PROD_GROWTH, // default
	goldGrowth = 'goldGrowth'  # CITY_AI_FOCUS_TYPE_GOLD_GROWTH,
	faith = 'faith'  # CITY_AI_FOCUS_TYPE_FAITH,


class TechType:
	pass


class TechTypeData:
	def __init__(self, name: str, eureka_summary: str, eureka_description: str, quoteTexts: List[str], era: EraType,
				 cost: int, required: List[TechType], flavors: List[Flavor]):
		self.name = name
		self.eureka_summary = eureka_summary
		self.eureka_description = eureka_description
		self.quoteTexts = quoteTexts
		self.era = era
		self.cost = cost
		self.required = required
		self.flavors = flavors


class TechType(ExtendedEnum):
	# default
	none = 'none'

	# ancient
	mining = 'mining'
	pottery = 'pottery'
	animalHusbandry = 'animalHusbandry'
	sailing = 'sailing'
	astrology = 'astrology'
	irrigation = 'irrigation'
	writing = 'writing'
	masonry = 'masonry'
	archery = 'archery'
	bronzeWorking = 'bronzeWorking'
	wheel = 'wheel'

	# classical
	celestialNavigation = 'celestialNavigation'
	horsebackRiding = 'horsebackRiding'
	currency = 'currency'
	construction = 'construction'
	ironWorking = 'ironWorking'
	shipBuilding = 'shipBuilding'
	mathematics = 'mathematics'
	engineering = 'engineering'

	# medieval
	militaryTactics = 'militaryTactics'
	buttress = 'buttress'
	apprenticeship = 'apprenticeship'
	stirrups = 'stirrups'
	machinery = 'machinery'
	education = 'education'
	militaryEngineering = 'militaryEngineering'
	castles = 'castles'

	# renaissance
	cartography = 'cartography'
	massProduction = 'massProduction'
	banking = 'banking'
	gunpowder = 'gunpowder'
	printing = 'printing'
	squareRigging = 'squareRigging'
	astronomy = 'astronomy'
	metalCasting = 'metalCasting'
	siegeTactics = 'siegeTactics'

	# industrial
	industrialization = 'industrialization'
	scientificTheory = 'scientificTheory'
	ballistics = 'ballistics'
	militaryScience = 'militaryScience'
	steamPower = 'steamPower'
	sanitation = 'sanitation'
	economics = 'economics'
	rifling = 'rifling'

	# modern
	flight = 'flight'
	replaceableParts = 'replaceableParts'
	steel = 'steel'
	refining = 'refining'
	electricity = 'electricity'
	radio = 'radio'
	chemistry = 'chemistry'
	combustion = 'combustion'

	# atomic
	advancedFlight = 'advancedFlight'
	rocketry = 'rocketry'
	advancedBallistics = 'advancedBallistics'
	combinedArms = 'combinedArms'
	plastics = 'plastics'
	computers = 'computers'
	nuclearFission = 'nuclearFission'
	syntheticMaterials = 'syntheticMaterials'

	# information
	telecommunications = 'telecommunications'
	satellites = 'satellites'
	guidanceSystems = 'guidanceSystems'
	lasers = 'lasers'
	composites = 'composites'
	stealthTechnology = 'stealthTechnology'
	robotics = 'robotics'
	nuclearFusion = 'nuclearFusion'
	nanotechnology = 'nanotechnology'

	futureTech = 'futureTech'

	def title(self) -> str:
		return self._data().name

	def required(self) -> List['TechType']:
		return self._data().required

	def era(self) -> EraType:
		return self._data().era

	def cost(self) -> int:
		return self._data().cost

	def flavorValue(self, flavorType: FlavorType) -> int:
		flavorOfTech = next((flavor for flavor in self._data().flavors if flavor.flavorType == flavorType), None)

		if flavorOfTech is not None:
			return flavorOfTech.value

		return 0

	def isGoodyTech(self) -> bool:
		return self.era() == EraType.ancient

	def leadsTo(self) -> List[TechType]:
		leadingTo: List[TechType] = []

		for tech in list(TechType):
			if self in tech.required():
				leadingTo.append(tech)

		return leadingTo

	def _data(self):
		if self == TechType.none:
			return TechTypeData(
				name=_('TXT_KEY_TECH_NONE'),
				eureka_summary='',
				eureka_description='',
				quoteTexts=[],
				era=EraType.ancient,
				cost=0,
				required=[],
				flavors=[]
			)

		# ancient
		if self == TechType.mining:
			# https://civilization.fandom.com/wiki/Mining_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_MINING_NAME'),
				eureka_summary=_('TXT_KEY_TECH_MINING_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_MINING_EUREKA_TEXT'),
				quoteTexts=[_('TXT_KEY_TECH_MINING_QUOTE1'), _('TXT_KEY_TECH_MINING_QUOTE2')],
				era=EraType.ancient,
				cost=25,
				required=[],
				flavors=[
					Flavor(FlavorType.production, 3),
					Flavor(FlavorType.tileImprovement, 2)
				]
			)
		elif self == TechType.pottery:
			# https://civilization.fandom.com/wiki/Pottery_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_POTTERY_NAME'),
				eureka_summary=_('TXT_KEY_TECH_POTTERY_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_POTTERY_EUREKA_TEXT'),
				quoteTexts=[_('TXT_KEY_TECH_POTTERY_QUOTE1'), _('TXT_KEY_TECH_POTTERY_QUOTE2')],
				era=EraType.ancient,
				cost=25,
				required=[],
				flavors=[
					Flavor(FlavorType.growth, 5)
				]
			)
		elif self == TechType.animalHusbandry:
			# https://civilization.fandom.com/wiki/Animal_Husbandry_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_ANIMAL_HUSBANDRY_NAME'),
				eureka_summary=_('TXT_KEY_TECH_ANIMAL_HUSBANDRY_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_ANIMAL_HUSBANDRY_EUREKA_TEXT'),
				quoteTexts=[_('TXT_KEY_TECH_ANIMAL_HUSBANDRY_QUOTE1'), _('TXT_KEY_TECH_ANIMAL_HUSBANDRY_QUOTE2')],
				era=EraType.ancient,
				cost=25,
				required=[],
				flavors=[
					Flavor(FlavorType.mobile, 4),
					Flavor(FlavorType.tileImprovement, 1)
				]
			)
		elif self == TechType.sailing:
			# https://civilization.fandom.com/wiki/Sailing_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_SAILING_NAME'),
				eureka_summary=_('TXT_KEY_TECH_SAILING_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_SAILING_EUREKA_TEXT'),
				quoteTexts=[_('TXT_KEY_TECH_SAILING_QUOTE1'), _('TXT_KEY_TECH_SAILING_QUOTE2')],
				era=EraType.ancient,
				cost=50,
				required=[],
				flavors=[
					Flavor(FlavorType.naval, 3),
					Flavor(FlavorType.navalTileImprovement, 3),
					Flavor(FlavorType.wonder, 3),
					Flavor(FlavorType.navalRecon, 2)
				]
			)
		elif self == TechType.astrology:
			# https://civilization.fandom.com/wiki/Astrology_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_ASTROLOGY_NAME'),
				eureka_summary=_('TXT_KEY_TECH_ASTROLOGY_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_ASTROLOGY_EUREKA_TEXT'),
				quoteTexts=[_('TXT_KEY_TECH_ASTROLOGY_QUOTE1'), _('TXT_KEY_TECH_ASTROLOGY_QUOTE2')],
				era=EraType.ancient,
				cost=50,
				required=[],
				flavors=[
					Flavor(FlavorType.amenities, 10),
					Flavor(FlavorType.tileImprovement, 2),
					Flavor(FlavorType.wonder, 4)
				]
			)
		elif self == TechType.irrigation:
			# https://civilization.fandom.com/wiki/Irrigation_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_IRRIGATION_NAME'),
				eureka_summary=_('TXT_KEY_TECH_IRRIGATION_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_IRRIGATION_EUREKA_TEXT'),
				quoteTexts=[_('TXT_KEY_TECH_IRRIGATION_QUOTE1'), _('TXT_KEY_TECH_IRRIGATION_QUOTE2')],
				era=EraType.ancient,
				cost=50,
				required=[TechType.pottery],
				flavors=[
					Flavor(FlavorType.growth, 5)
				]
			)
		elif self == TechType.writing:
			# https://civilization.fandom.com/wiki/Writing_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_WRITING_NAME'),
				eureka_summary=_('TXT_KEY_TECH_WRITING_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_WRITING_EUREKA_TEXT'),
				quoteTexts=[_('TXT_KEY_TECH_WRITING_QUOTE1'), _('TXT_KEY_TECH_WRITING_QUOTE2')],
				era=EraType.ancient,
				cost=50,
				required=[TechType.pottery],
				flavors=[
					Flavor(FlavorType.science, 6),
					Flavor(FlavorType.wonder, 2),
					Flavor(FlavorType.diplomacy, 2)
				]
			)
		elif self == TechType.masonry:
			# https://civilization.fandom.com/wiki/Masonry_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_MASONRY_NAME'),
				eureka_summary=_('TXT_KEY_TECH_MASONRY_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_MASONRY_EUREKA_TEXT'),
				quoteTexts=[_('TXT_KEY_TECH_MASONRY_QUOTE1'), _('TXT_KEY_TECH_MASONRY_QUOTE2')],
				era=EraType.ancient,
				cost=80,
				required=[TechType.mining],
				flavors=[
					Flavor(FlavorType.cityDefense, 4),
					Flavor(FlavorType.amenities, 2),
					Flavor(FlavorType.tileImprovement, 2),
					Flavor(FlavorType.wonder, 2)
				]
			)
		elif self == TechType.archery:
			# https://civilization.fandom.com/wiki/Archery_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_ARCHERY_NAME'),
				eureka_summary=_('TXT_KEY_TECH_ARCHERY_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_ARCHERY_EUREKA_TEXT'),
				quoteTexts=[_('TXT_KEY_TECH_ARCHERY_QUOTE1'), _('TXT_KEY_TECH_ARCHERY_QUOTE2')],
				era=EraType.ancient,
				cost=50,
				required=[TechType.animalHusbandry],
				flavors=[
					Flavor(FlavorType.ranged, 4),
					Flavor(FlavorType.offense, 1)
				]
			)
		elif self == TechType.bronzeWorking:
			# https://civilization.fandom.com/wiki/Bronze_Working_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_BRONZE_WORKING_NAME'),
				eureka_summary=_('TXT_KEY_TECH_BRONZE_WORKING_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_BRONZE_WORKING_EUREKA_TEXT'),
				quoteTexts=[_('TXT_KEY_TECH_BRONZE_WORKING_QUOTE1'), _('TXT_KEY_TECH_BRONZE_WORKING_QUOTE2')],
				era=EraType.ancient,
				cost=80,
				required=[TechType.mining],
				flavors=[
					Flavor(FlavorType.defense, 4),
					Flavor(FlavorType.militaryTraining, 4),
					Flavor(FlavorType.wonder, 2)
				]
			)
		elif self == TechType.wheel:
			# https://civilization.fandom.com/wiki/Wheel_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_WHEEL_NAME'),
				eureka_summary=_('TXT_KEY_TECH_WHEEL_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_WHEEL_EUREKA_TEXT'),
				quoteTexts=[_('TXT_KEY_TECH_WHEEL_QUOTE1'), _('TXT_KEY_TECH_WHEEL_QUOTE2')],
				era=EraType.ancient,
				cost=80,
				required=[TechType.mining],
				flavors=[
					Flavor(FlavorType.mobile, 2),
					Flavor(FlavorType.growth, 2),
					Flavor(FlavorType.ranged, 2),
					Flavor(FlavorType.infrastructure, 2),
					Flavor(FlavorType.gold, 6)
				]
			)

		# classical
		elif self == TechType.celestialNavigation:
			# https://civilization.fandom.com/wiki/Celestial_Navigation_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_CELESTIAL_NAVIGATION_NAME'),
				eureka_summary=_('TXT_KEY_TECH_CELESTIAL_NAVIGATION_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_CELESTIAL_NAVIGATION_EUREKA_TEXT'),
				quoteTexts=[_('TXT_KEY_TECH_CELESTIAL_NAVIGATION_QUOTE1'), _('TXT_KEY_TECH_CELESTIAL_NAVIGATION_QUOTE2')],
				era=EraType.classical,
				cost=120,
				required=[TechType.sailing, TechType.astrology],
				flavors=[
					Flavor(FlavorType.naval, 5),
					Flavor(FlavorType.navalGrowth, 5)
				]
			)
		elif self == TechType.horsebackRiding:
			# https://civilization.fandom.com/wiki/Horseback_Riding_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_HORSEBACK_RIDING_NAME'),
				eureka_summary=_('TXT_KEY_TECH_HORSEBACK_RIDING_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_HORSEBACK_RIDING_EUREKA_TEXT'),
				quoteTexts=[_('TXT_KEY_TECH_HORSEBACK_RIDING_QUOTE1'), _('TXT_KEY_TECH_HORSEBACK_RIDING_QUOTE2')],
				era=EraType.classical,
				cost=120,
				required=[TechType.animalHusbandry],
				flavors=[
					Flavor(FlavorType.mobile, 7),
					Flavor(FlavorType.amenities, 3)
				]
			)
		elif self == TechType.currency:
			# https://civilization.fandom.com/wiki/Currency_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_CURRENCY_NAME'),
				eureka_summary=_('TXT_KEY_TECH_CURRENCY_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_CURRENCY_EUREKA_TEXT'),
				quoteTexts=[_('TXT_KEY_TECH_CURRENCY_QUOTE1'), _('TXT_KEY_TECH_CURRENCY_QUOTE2')],
				era=EraType.classical,
				cost=120,
				required=[TechType.writing],
				flavors=[
					Flavor(FlavorType.gold, 8),
					Flavor(FlavorType.wonder, 2)
				]
			)
		elif self == TechType.construction:
			# https://civilization.fandom.com/wiki/Construction_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_CONSTRUCTION_NAME'),
				eureka_summary=_('TXT_KEY_TECH_CONSTRUCTION_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_CONSTRUCTION_EUREKA_TEXT'),
				quoteTexts=[_('TXT_KEY_TECH_CONSTRUCTION_QUOTE1'), _('TXT_KEY_TECH_CONSTRUCTION_QUOTE2')],
				era=EraType.classical,
				cost=200,
				required=[TechType.masonry, TechType.horsebackRiding],
				flavors=[
					Flavor(FlavorType.amenities, 17),
					Flavor(FlavorType.infrastructure, 2),
					Flavor(FlavorType.wonder, 2)
				]
			)
		elif self == TechType.ironWorking:
			# https://civilization.fandom.com/wiki/Iron_Working_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_IRON_WORKING_NAME'),
				eureka_summary=_('TXT_KEY_TECH_IRON_WORKING_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_IRON_WORKING_EUREKA_TEXT'),
				quoteTexts=[_('TXT_KEY_TECH_IRON_WORKING_QUOTE1'), _('TXT_KEY_TECH_IRON_WORKING_QUOTE2')],
				era=EraType.classical,
				cost=120,
				required=[TechType.bronzeWorking],
				flavors=[
					Flavor(FlavorType.offense, 12),
					Flavor(FlavorType.defense, 6),
					Flavor(FlavorType.militaryTraining, 3)
				]
			)
		elif self == TechType.shipBuilding:
			# https://civilization.fandom.com/wiki/Shipbuilding_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_SHIP_BUILDING_NAME'),
				eureka_summary=_('TXT_KEY_TECH_SHIP_BUILDING_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_SHIP_BUILDING_EUREKA_TEXT'),
				quoteTexts=[_('TXT_KEY_TECH_SHIP_BUILDING_QUOTE1'), _('TXT_KEY_TECH_SHIP_BUILDING_QUOTE2')],
				era=EraType.classical,
				cost=200,
				required=[TechType.sailing],
				flavors=[
					Flavor(FlavorType.naval, 5),
					Flavor(FlavorType.navalGrowth, 3),
					Flavor(FlavorType.navalRecon, 2)
				]
			)
		elif self == TechType.mathematics:
			# https://civilization.fandom.com/wiki/Mathematics_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_MATHEMATICS_NAME'),
				eureka_summary=_('TXT_KEY_TECH_MATHEMATICS_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_MATHEMATICS_EUREKA_TEXT'),
				quoteTexts=[_('TXT_KEY_TECH_MATHEMATICS_QUOTE1'), _('TXT_KEY_TECH_MATHEMATICS_QUOTE2')],
				era=EraType.classical,
				cost=200,
				required=[TechType.currency],
				flavors=[
					Flavor(FlavorType.ranged, 8),
					Flavor(FlavorType.wonder, 2)
				]
			)
		elif self == TechType.engineering:
			# https://civilization.fandom.com/wiki/Engineering_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_ENGINEERING_NAME'),
				eureka_summary=_('TXT_KEY_TECH_ENGINEERING_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_ENGINEERING_EUREKA_TEXT'),
				quoteTexts=[_('TXT_KEY_TECH_ENGINEERING_QUOTE1'), _('TXT_KEY_TECH_ENGINEERING_QUOTE2')],
				era=EraType.classical,
				cost=200,
				required=[TechType.wheel],
				flavors=[
					Flavor(FlavorType.defense, 2),
					Flavor(FlavorType.production, 5),
					Flavor(FlavorType.tileImprovement, 5)
				]
			)

		# medieval
		elif self == TechType.militaryTactics:
			# https://civilization.fandom.com/wiki/Military_Tactics_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_MILITARY_TACTICS_NAME'),
				eureka_summary=_('TXT_KEY_TECH_MILITARY_TACTICS_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_MILITARY_TACTICS_EUREKA_TEXT'),
				quoteTexts=[_('TXT_KEY_TECH_MILITARY_TACTICS_QUOTE1'), _('TXT_KEY_TECH_MILITARY_TACTICS_QUOTE2')],
				era=EraType.medieval,
				cost=275,
				required=[TechType.mathematics],
				flavors=[
					Flavor(FlavorType.offense, 3),
					Flavor(FlavorType.mobile, 3),
					Flavor(FlavorType.cityDefense, 2),
					Flavor(FlavorType.wonder, 2)
				]
			)
		elif self == TechType.buttress:
			# https://civilization.fandom.com/wiki/Buttress_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_BUTTRESS_NAME'),
				eureka_summary=_('TXT_KEY_TECH_BUTTRESS_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_BUTTRESS_EUREKA_TEXT'),
				quoteTexts=[_('TXT_KEY_TECH_BUTTRESS_QUOTE1'), _('TXT_KEY_TECH_BUTTRESS_QUOTE2')],
				era=EraType.medieval,
				cost=300,
				required=[TechType.shipBuilding, TechType.mathematics],
				flavors=[
					Flavor(FlavorType.wonder, 2)
				]
			)
		elif self == TechType.apprenticeship:
			# https://civilization.fandom.com/wiki/Apprenticeship_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_APPRENTICESHIP_NAME'),
				eureka_summary=_('TXT_KEY_TECH_APPRENTICESHIP_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_APPRENTICESHIP_EUREKA_TEXT'),
				quoteTexts=[_('TXT_KEY_TECH_APPRENTICESHIP_QUOTE1'), _('TXT_KEY_TECH_APPRENTICESHIP_QUOTE2')],
				era=EraType.medieval,
				cost=275,
				required=[TechType.currency, TechType.horsebackRiding],
				flavors=[
					Flavor(FlavorType.gold, 5),
					Flavor(FlavorType.production, 3)
				]
			)
		elif self == TechType.stirrups:
			# https://civilization.fandom.com/wiki/Stirrups_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_STIRRUPS_NAME'),
				eureka_summary=_('TXT_KEY_TECH_STIRRUPS_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_STIRRUPS_EUREKA_TEXT'),
				quoteTexts=[_('TXT_KEY_TECH_STIRRUPS_QUOTE1'), _('TXT_KEY_TECH_STIRRUPS_QUOTE2')],
				era=EraType.medieval,
				cost=360,
				required=[TechType.horsebackRiding],
				flavors=[
					Flavor(FlavorType.offense, 3),
					Flavor(FlavorType.mobile, 3),
					Flavor(FlavorType.defense, 2),
					Flavor(FlavorType.wonder, 2)
				]
			)
		elif self == TechType.machinery:
			# https://civilization.fandom.com/wiki/Machinery_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_MACHINERY_NAME'),
				eureka_summary=_('TXT_KEY_TECH_MACHINERY_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_MACHINERY_EUREKA_TEXT'),
				quoteTexts=[_('TXT_KEY_TECH_MACHINERY_QUOTE1'), _('TXT_KEY_TECH_MACHINERY_QUOTE2')],
				era=EraType.medieval,
				cost=275,
				required=[TechType.ironWorking, TechType.engineering],
				flavors=[
					Flavor(FlavorType.ranged, 8),
					Flavor(FlavorType.infrastructure, 2)
				]
			)
		elif self == TechType.education:
			# https://civilization.fandom.com/wiki/Education_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_EDUCATION_NAME'),
				eureka_summary=_('TXT_KEY_TECH_EDUCATION_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_EDUCATION_EUREKA_TEXT'),
				quoteTexts=[_('TXT_KEY_TECH_EDUCATION_QUOTE1'), _('TXT_KEY_TECH_EDUCATION_QUOTE2')],
				era=EraType.medieval,
				cost=335,
				required=[TechType.apprenticeship, TechType.mathematics],
				flavors=[
					Flavor(FlavorType.science, 8),
					Flavor(FlavorType.wonder, 2)
				]
			)
		elif self == TechType.militaryEngineering:
			# https://civilization.fandom.com/wiki/Military_Engineering_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_MILITARY_ENGINEERING_NAME'),
				eureka_summary=_('TXT_KEY_TECH_MILITARY_ENGINEERING_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_MILITARY_ENGINEERING_EUREKA_TEXT'),
				quoteTexts=[_('TXT_KEY_TECH_MILITARY_ENGINEERING_QUOTE1'), _('TXT_KEY_TECH_MILITARY_ENGINEERING_QUOTE2')],
				era=EraType.medieval,
				cost=335,
				required=[TechType.construction],
				flavors=[
					Flavor(FlavorType.defense, 5),
					Flavor(FlavorType.production, 2)
				]
			)
		elif self == TechType.castles:
			# https://civilization.fandom.com/wiki/Castles_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_CASTLES_NAME'),
				eureka_summary=_('TXT_KEY_TECH_CASTLES_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_CASTLES_EUREKA_TEXT'),
				quoteTexts=[_('TXT_KEY_TECH_CASTLES_QUOTE1'), _('TXT_KEY_TECH_CASTLES_QUOTE2')],
				era=EraType.medieval,
				cost=390,
				required=[TechType.construction],
				flavors=[
					Flavor(FlavorType.cityDefense, 5)
				]
			)

		# renaissance
		elif self == TechType.cartography:
			# https://civilization.fandom.com/wiki/Cartography_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_CARTOGRAPHY_NAME'),
				eureka_summary=_('TXT_KEY_TECH_CARTOGRAPHY_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_CARTOGRAPHY_EUREKA_TEXT'),
				quoteTexts=[_('TXT_KEY_TECH_CARTOGRAPHY_QUOTE1'), _('TXT_KEY_TECH_CARTOGRAPHY_QUOTE2')],
				era=EraType.renaissance,
				cost=490,
				required=[TechType.shipBuilding],
				flavors=[
					Flavor(FlavorType.navalRecon, 5)
				]
			)
		elif self == TechType.massProduction:
			# https://civilization.fandom.com/wiki/Mass_Production_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_MASS_PRODUCTION_NAME'),
				eureka_summary=_('TXT_KEY_TECH_MASS_PRODUCTION_NAME'),
				eureka_description=_('TXT_KEY_TECH_MASS_PRODUCTION_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_TECH_MASS_PRODUCTION_QUOTE1'),
					_('TXT_KEY_TECH_MASS_PRODUCTION_QUOTE2')
				],
				era=EraType.renaissance,
				cost=490,
				required=[TechType.shipBuilding, TechType.education],
				flavors=[
					Flavor(FlavorType.production, 7)
				]
			)
		elif self == TechType.banking:
			# https://civilization.fandom.com/wiki/Banking_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_BANKING_NAME'),
				eureka_summary=_('TXT_KEY_TECH_BANKING_NAME'),
				eureka_description=_('TXT_KEY_TECH_BANKING_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_TECH_BANKING_QUOTE1'),
					_('TXT_KEY_TECH_BANKING_QUOTE2')
				],
				era=EraType.renaissance,
				cost=490,
				required=[TechType.education, TechType.apprenticeship, TechType.stirrups],
				flavors=[
					Flavor(FlavorType.gold, 6)
				]
			)
		elif self == TechType.gunpowder:
			# https://civilization.fandom.com/wiki/Gunpowder_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_GUNPOWDER_NAME'),
				eureka_summary=_('TXT_KEY_TECH_GUNPOWDER_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_GUNPOWDER_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_TECH_GUNPOWDER_QUOTE1'),
					_('TXT_KEY_TECH_GUNPOWDER_QUOTE2')
				],
				era=EraType.renaissance,
				cost=490,
				required=[TechType.militaryEngineering, TechType.apprenticeship, TechType.stirrups],
				flavors=[
					Flavor(FlavorType.production, 2),
					Flavor(FlavorType.defense, 3),
					Flavor(FlavorType.cityDefense, 2)
				]
			)
		elif self == TechType.printing:
			# https://civilization.fandom.com/wiki/Printing_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_PRINTING_NAME'),
				eureka_summary=_('TXT_KEY_TECH_PRINTING_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_PRINTING_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_TECH_PRINTING_QUOTE1'),
					_('TXT_KEY_TECH_PRINTING_QUOTE2')
				],
				era=EraType.renaissance,
				cost=490,
				required=[TechType.machinery],
				flavors=[
					Flavor(FlavorType.science, 7)
				]
			)
		elif self == TechType.squareRigging:
			# https://civilization.fandom.com/wiki/Square_Rigging_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_SQUARE_RIGGING_NAME'),
				eureka_summary=_('TXT_KEY_TECH_SQUARE_RIGGING_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_SQUARE_RIGGING_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_TECH_SQUARE_RIGGING_QUOTE1'),
					_('TXT_KEY_TECH_SQUARE_RIGGING_QUOTE2')
				],
				era=EraType.renaissance,
				cost=600,
				required=[TechType.cartography],
				flavors=[
					Flavor(FlavorType.naval, 5),
					Flavor(FlavorType.navalGrowth, 2),
					Flavor(FlavorType.navalRecon, 3)
				]
			)
		elif self == TechType.astronomy:
			# https://civilization.fandom.com/wiki/Astronomy_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_ASTRONOMY_NAME'),
				eureka_summary=_('TXT_KEY_TECH_ASTRONOMY_NAME'),
				eureka_description=_('TXT_KEY_TECH_ASTRONOMY_NAME'),
				quoteTexts=[
					_('TXT_KEY_TECH_ASTRONOMY_QUOTE1'),
					_('TXT_KEY_TECH_ASTRONOMY_QUOTE2')
				],
				era=EraType.renaissance,
				cost=600,
				required=[TechType.education],
				flavors=[
					Flavor(FlavorType.science, 4)
				]
			)
		elif self == TechType.metalCasting:
			# https://civilization.fandom.com/wiki/Metal_Casting_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_METAL_CASTING_NAME'),
				eureka_summary=_('TXT_KEY_TECH_METAL_CASTING_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_METAL_CASTING_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_TECH_METAL_CASTING_QUOTE1'),
					_('TXT_KEY_TECH_METAL_CASTING_QUOTE2')
				],
				era=EraType.renaissance,
				cost=660,
				required=[TechType.gunpowder],
				flavors=[
					Flavor(FlavorType.production, 3)
				]
			)
		elif self == TechType.siegeTactics:
			# https://civilization.fandom.com/wiki/Siege_Tactics_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_SIEGE_TACTICS_NAME'),
				eureka_summary=_('TXT_KEY_TECH_SIEGE_TACTICS_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_SIEGE_TACTICS_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_TECH_SIEGE_TACTICS_QUOTE1'),
					_('TXT_KEY_TECH_SIEGE_TACTICS_QUOTE2')
				],
				era=EraType.renaissance,
				cost=660,
				required=[TechType.castles],
				flavors=[
					Flavor(FlavorType.ranged, 5),
					Flavor(FlavorType.offense, 3)
				]
			)

		# industrial
		elif self == TechType.industrialization:
			# https://civilization.fandom.com/wiki/Industrialization_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_INDUSTRIALIZATION_NAME'),
				eureka_summary=_('TXT_KEY_TECH_INDUSTRIALIZATION_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_INDUSTRIALIZATION_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_TECH_INDUSTRIALIZATION_QUOTE1'),
					_('TXT_KEY_TECH_INDUSTRIALIZATION_QUOTE2')
				],
				era=EraType.industrial,
				cost=700,
				required=[TechType.massProduction, TechType.squareRigging],
				flavors=[
					Flavor(FlavorType.production, 7)
				]
			)
		elif self == TechType.scientificTheory:
			# https://civilization.fandom.com/wiki/Scientific_Theory_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_SCIENTIFIC_THEORY_NAME'),
				eureka_summary=_('TXT_KEY_TECH_SCIENTIFIC_THEORY_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_SCIENTIFIC_THEORY_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_TECH_SCIENTIFIC_THEORY_QUOTE1'),
					_('TXT_KEY_TECH_SCIENTIFIC_THEORY_QUOTE2')
				],
				era=EraType.industrial,
				cost=700,
				required=[TechType.astronomy, TechType.banking],
				flavors=[
					Flavor(FlavorType.diplomacy, 5),
					Flavor(FlavorType.science, 5)
				]
			)
		elif self == TechType.ballistics:
			# https://civilization.fandom.com/wiki/Ballistics_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_BALLISTICS_NAME'),
				eureka_summary=_('TXT_KEY_TECH_BALLISTICS_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_BALLISTICS_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_TECH_BALLISTICS_QUOTE1'),
					_('TXT_KEY_TECH_BALLISTICS_QUOTE2')
				],
				era=EraType.industrial,
				cost=840,
				required=[TechType.metalCasting],
				flavors=[
					Flavor(FlavorType.ranged, 5),
					Flavor(FlavorType.offense, 5)
				]
			)
		elif self == TechType.militaryScience:
			# https://civilization.fandom.com/wiki/Military_Science_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_MILITARY_SCIENCE_NAME'),
				eureka_summary=_('TXT_KEY_TECH_MILITARY_SCIENCE_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_MILITARY_SCIENCE_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_TECH_MILITARY_SCIENCE_QUOTE1'),
					_('TXT_KEY_TECH_MILITARY_SCIENCE_QUOTE2')
				],
				era=EraType.industrial,
				cost=845,
				required=[TechType.printing, TechType.siegeTactics],
				flavors=[
					Flavor(FlavorType.offense, 7)
				]
			)
		elif self == TechType.steamPower:
			# https://civilization.fandom.com/wiki/Steam_Power_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_STEAM_POWER_NAME'),
				eureka_summary=_('TXT_KEY_TECH_STEAM_POWER_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_STEAM_POWER_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_TECH_STEAM_POWER_QUOTE1'),
					_('TXT_KEY_TECH_STEAM_POWER_QUOTE2')
				],
				era=EraType.industrial,
				cost=805,
				required=[TechType.industrialization, TechType.squareRigging],
				flavors=[
					Flavor(FlavorType.mobile, 5),
					Flavor(FlavorType.offense, 2),
					Flavor(FlavorType.navalGrowth, 3)
				]
			)
		elif self == TechType.sanitation:
			# https://civilization.fandom.com/wiki/Sanitation_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_SANITATION_NAME'),
				eureka_summary=_('TXT_KEY_TECH_SANITATION_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_SANITATION_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_TECH_SANITATION_QUOTE1'),
					_('TXT_KEY_TECH_SANITATION_QUOTE2')
				],
				era=EraType.industrial,
				cost=805,
				required=[TechType.scientificTheory],
				flavors=[
					Flavor(FlavorType.growth, 5)
				]
			)
		elif self == TechType.economics:
			# https://civilization.fandom.com/wiki/Economics_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_ECONOMICS_NAME'),
				eureka_summary=_('TXT_KEY_TECH_ECONOMICS_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_ECONOMICS_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_TECH_ECONOMICS_QUOTE1'),
					_('TXT_KEY_TECH_ECONOMICS_QUOTE2')
				],
				era=EraType.industrial,
				cost=805,
				required=[TechType.metalCasting, TechType.scientificTheory],
				flavors=[
					Flavor(FlavorType.wonder, 5)
				]
			)
		elif self == TechType.rifling:
			# https://civilization.fandom.com/wiki/Rifling_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_RIFLING_NAME'),
				eureka_summary=_('TXT_KEY_TECH_RIFLING_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_RIFLING_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_TECH_RIFLING_QUOTE1'),
					_('TXT_KEY_TECH_RIFLING_QUOTE2')
				],
				era=EraType.industrial,
				cost=970,
				required=[TechType.ballistics, TechType.militaryScience],
				flavors=[
					Flavor(FlavorType.offense, 5)
				]
			)

		# modern
		elif self == TechType.flight:
			# https://civilization.fandom.com/wiki/Flight_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_FLIGHT_NAME'),
				eureka_summary=_('TXT_KEY_TECH_FLIGHT_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_FLIGHT_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_TECH_FLIGHT_QUOTE1'),
					_('TXT_KEY_TECH_FLIGHT_QUOTE2')
				],
				era=EraType.modern,
				cost=900,
				required=[TechType.industrialization, TechType.scientificTheory],
				flavors=[
					Flavor(FlavorType.mobile, 5)
				]
			)
		elif self == TechType.replaceableParts:
			# https://civilization.fandom.com/wiki/Replaceable_Parts_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_REPLACEABLE_PARTS_NAME'),
				eureka_summary=_('TXT_KEY_TECH_REPLACEABLE_PARTS_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_REPLACEABLE_PARTS_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_TECH_REPLACEABLE_PARTS_QUOTE1'),
					_('TXT_KEY_TECH_REPLACEABLE_PARTS_QUOTE2')
				],
				era=EraType.modern,
				cost=1250,
				required=[TechType.economics],
				flavors=[
					Flavor(FlavorType.offense, 5),
					Flavor(FlavorType.gold, 3),
					Flavor(FlavorType.production, 3)
				]
			)
		elif self == TechType.steel:
			# https://civilization.fandom.com/wiki/Steel_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_STEEL_NAME'),
				eureka_summary=_('TXT_KEY_TECH_STEEL_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_STEEL_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_TECH_STEEL_QUOTE1'),
					_('TXT_KEY_TECH_STEEL_QUOTE2')
				],
				era=EraType.modern,
				cost=1140,
				required=[TechType.rifling],
				flavors=[
					Flavor(FlavorType.ranged, 5),
					Flavor(FlavorType.wonder, 3)
				]
			)
		elif self == TechType.refining:
			# https://civilization.fandom.com/wiki/Refining_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_REFINING_NAME'),
				eureka_summary=_('TXT_KEY_TECH_REFINING_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_REFINING_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_TECH_REFINING_QUOTE1')
				],
				era=EraType.modern,
				cost=1250,
				required=[TechType.rifling],
				flavors=[
					Flavor(FlavorType.navalGrowth, 5),
					Flavor(FlavorType.tileImprovement, 3)
				]
			)
		elif self == TechType.electricity:
			# https://civilization.fandom.com/wiki/Electricity_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_ELECTRICITY_NAME'),
				eureka_summary=_('TXT_KEY_TECH_ELECTRICITY_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_ELECTRICITY_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_TECH_ELECTRICITY_QUOTE1'),
					_('TXT_KEY_TECH_ELECTRICITY_QUOTE2')
				],
				era=EraType.modern,
				cost=985,
				required=[TechType.steamPower],
				flavors=[
					Flavor(FlavorType.navalGrowth, 5),
					Flavor(FlavorType.energy, 3)
				]
			)
		elif self == TechType.radio:
			# https://civilization.fandom.com/wiki/Radio_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_RADIO_NAME'),
				eureka_summary=_('TXT_KEY_TECH_RADIO_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_RADIO_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_TECH_RADIO_QUOTE1'),
					_('TXT_KEY_TECH_RADIO_QUOTE2')
				],
				era=EraType.modern,
				cost=985,
				required=[TechType.flight, TechType.steamPower],
				flavors=[
					Flavor(FlavorType.expansion, 3)
				]
			)
		elif self == TechType.chemistry:
			# https://civilization.fandom.com/wiki/Chemistry_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_CHEMISTRY_NAME'),
				eureka_summary=_('TXT_KEY_TECH_CHEMISTRY_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_CHEMISTRY_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_TECH_CHEMISTRY_QUOTE1'),
					_('TXT_KEY_TECH_CHEMISTRY_QUOTE2')
				],
				era=EraType.modern,
				cost=985,
				required=[TechType.sanitation],
				flavors=[
					Flavor(FlavorType.growth, 4),
					Flavor(FlavorType.science, 5)
				]
			)
		elif self == TechType.combustion:
			# https://civilization.fandom.com/wiki/Combustion_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_COMBUSTION_NAME'),
				eureka_summary=_('TXT_KEY_TECH_COMBUSTION_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_COMBUSTION_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_TECH_COMBUSTION_QUOTE1'),
					_('TXT_KEY_TECH_COMBUSTION_QUOTE2')
				],
				era=EraType.modern,
				cost=1250,
				required=[TechType.steel, TechType.rifling],
				flavors=[
					Flavor(FlavorType.offense, 4),
					Flavor(FlavorType.wonder, 3)
				]
			)

		# atomic
		elif self == TechType.advancedFlight:
			# https://civilization.fandom.com/wiki/Advanced_Flight_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_ADVANCED_FLIGHT_NAME'),
				eureka_summary=_('TXT_KEY_TECH_ADVANCED_FLIGHT_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_ADVANCED_FLIGHT_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_TECH_ADVANCED_FLIGHT_QUOTE1'),
					_('TXT_KEY_TECH_ADVANCED_FLIGHT_QUOTE2')
				],
				era=EraType.atomic,
				cost=1065,
				required=[TechType.radio],
				flavors=[
					Flavor(FlavorType.offense, 4)
				]
			)
		elif self == TechType.rocketry:
			# https://civilization.fandom.com/wiki/Rocketry_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_ROCKETRY_NAME'),
				eureka_summary=_('TXT_KEY_TECH_ROCKETRY_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_ROCKETRY_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_TECH_ROCKETRY_QUOTE1'),
					_('TXT_KEY_TECH_ROCKETRY_QUOTE2')
				],
				era=EraType.atomic,
				cost=1065,
				required=[TechType.radio, TechType.chemistry],
				flavors=[
					Flavor(FlavorType.science, 5)
				]
			)
		elif self == TechType.advancedBallistics:
			# https://civilization.fandom.com/wiki/Advanced_Ballistics_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_ADVANCED_BALLISTICS_NAME'),
				eureka_summary=_('TXT_KEY_TECH_ADVANCED_BALLISTICS_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_ADVANCED_BALLISTICS_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_TECH_ADVANCED_BALLISTICS_QUOTE1'),
					_('TXT_KEY_TECH_ADVANCED_BALLISTICS_QUOTE2')
				],
				era=EraType.atomic,
				cost=1410,
				required=[TechType.replaceableParts, TechType.steel],
				flavors=[
					Flavor(FlavorType.offense, 5),
					Flavor(FlavorType.defense, 5)
				]
			)
		elif self == TechType.combinedArms:
			# https://civilization.fandom.com/wiki/Combined_Arms_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_COMBINED_ARMS_NAME'),
				eureka_summary=_('TXT_KEY_TECH_COMBINED_ARMS_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_COMBINED_ARMS_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_TECH_COMBINED_ARMS_QUOTE1'),
					_('TXT_KEY_TECH_COMBINED_ARMS_QUOTE2')
				],
				era=EraType.atomic,
				cost=1480,
				required=[TechType.steel],
				flavors=[
					Flavor(FlavorType.navalGrowth, 5)
				]
			)
		elif self == TechType.plastics:
			# https://civilization.fandom.com/wiki/Plastics_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_PLASTICS_NAME'),
				eureka_summary=_('TXT_KEY_TECH_PLASTICS_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_PLASTICS_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_TECH_PLASTICS_QUOTE1'),
					_('TXT_KEY_TECH_PLASTICS_QUOTE2')
				],
				era=EraType.atomic,
				cost=1065,
				required=[TechType.combustion],
				flavors=[
					Flavor(FlavorType.offense, 5),
					Flavor(FlavorType.navalTileImprovement, 4)
				]
			)
		elif self == TechType.computers:
			# https://civilization.fandom.com/wiki/Computers_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_COMPUTERS_NAME'),
				eureka_summary=_('TXT_KEY_TECH_COMPUTERS_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_COMPUTERS_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_TECH_COMPUTERS_QUOTE1'),
					_('TXT_KEY_TECH_COMPUTERS_QUOTE2')
				],
				era=EraType.atomic,
				cost=1195,
				required=[TechType.electricity, TechType.radio],
				flavors=[
					Flavor(FlavorType.growth, 2),
					Flavor(FlavorType.science, 4),
					Flavor(FlavorType.diplomacy, 5)
				]
			)
		elif self == TechType.nuclearFission:
			# https://civilization.fandom.com/wiki/Nuclear_Fission_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_NUCLEAR_FISSION_NAME'),
				eureka_summary=_('TXT_KEY_TECH_NUCLEAR_FISSION_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_NUCLEAR_FISSION_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_TECH_NUCLEAR_FISSION_QUOTE1'),
					_('TXT_KEY_TECH_NUCLEAR_FISSION_QUOTE2')
				],
				era=EraType.atomic,
				cost=1195,
				required=[TechType.combinedArms, TechType.advancedBallistics],
				flavors=[
					Flavor(FlavorType.energy, 5)
				]
			)
		elif self == TechType.syntheticMaterials:
			# https://civilization.fandom.com/wiki/Synthetic_Materials_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_SYNTHETIC_MATERIALS_NAME'),
				eureka_summary=_('TXT_KEY_TECH_SYNTHETIC_MATERIALS_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_SYNTHETIC_MATERIALS_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_TECH_SYNTHETIC_MATERIALS_QUOTE1'),
					_('TXT_KEY_TECH_SYNTHETIC_MATERIALS_QUOTE2')
				],
				era=EraType.atomic,
				cost=1195,
				required=[TechType.plastics],
				flavors=[
					Flavor(FlavorType.gold, 4),
					Flavor(FlavorType.offense, 2)
				]
			)

		# information
		elif self == TechType.telecommunications:
			# https://civilization.fandom.com/wiki/Telecommunications_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_TELECOMMUNICATIONS_NAME'),
				eureka_summary=_('TXT_KEY_TECH_TELECOMMUNICATIONS_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_TELECOMMUNICATIONS_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_TECH_TELECOMMUNICATIONS_QUOTE1'),
					_('TXT_KEY_TECH_TELECOMMUNICATIONS_QUOTE2')
				],
				era=EraType.information,
				cost=1340,
				required=[TechType.computers],
				flavors=[
					Flavor(FlavorType.offense, 3)
				]
			)
		elif self == TechType.satellites:
			# https://civilization.fandom.com/wiki/Satellites_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_SATELLITES_NAME'),
				eureka_summary=_('TXT_KEY_TECH_SATELLITES_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_SATELLITES_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_TECH_SATELLITES_QUOTE1'),
					_('TXT_KEY_TECH_SATELLITES_QUOTE2')
				],
				era=EraType.information,
				cost=1340,
				required=[TechType.advancedFlight, TechType.rocketry],
				flavors=[
					Flavor(FlavorType.science, 3),
					Flavor(FlavorType.expansion, 3)
				]
			)
		elif self == TechType.guidanceSystems:
			# https://civilization.fandom.com/wiki/Guidance_Systems_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_GUIDANCE_SYSTEMS_NAME'),
				eureka_summary=_('TXT_KEY_TECH_GUIDANCE_SYSTEMS_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_GUIDANCE_SYSTEMS_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_TECH_GUIDANCE_SYSTEMS_QUOTE1'),
					_('TXT_KEY_TECH_GUIDANCE_SYSTEMS_QUOTE2')
				],
				era=EraType.information,
				cost=1580,
				required=[TechType.rocketry, TechType.advancedBallistics],
				flavors=[
					Flavor(FlavorType.offense, 5)
				]
			)
		elif self == TechType.lasers:
			# https://civilization.fandom.com/wiki/Lasers_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_LASERS_NAME'),
				eureka_summary=_('TXT_KEY_TECH_LASERS_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_LASERS_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_TECH_LASERS_QUOTE1'),
					_('TXT_KEY_TECH_LASERS_QUOTE2')
				],
				era=EraType.information,
				cost=1340,
				required=[TechType.nuclearFission],
				flavors=[
					Flavor(FlavorType.navalGrowth, 5)
				]
			)
		elif self == TechType.composites:
			# https://civilization.fandom.com/wiki/Composites_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_COMPOSITES_NAME'),
				eureka_summary=_('TXT_KEY_TECH_COMPOSITES_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_COMPOSITES_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_TECH_COMPOSITES_QUOTE1'),
					_('TXT_KEY_TECH_COMPOSITES_QUOTE2')
				],
				era=EraType.information,
				cost=1340,
				required=[TechType.syntheticMaterials],
				flavors=[
					Flavor(FlavorType.offense, 6)
				]
			)
		elif self == TechType.stealthTechnology:
			# https://civilization.fandom.com/wiki/Stealth_Technology_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_STEALTH_TECHNOLOGY_NAME'),
				eureka_summary=_('TXT_KEY_TECH_STEALTH_TECHNOLOGY_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_STEALTH_TECHNOLOGY_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_TECH_STEALTH_TECHNOLOGY_QUOTE1'),
					_('TXT_KEY_TECH_STEALTH_TECHNOLOGY_QUOTE2')
				],
				era=EraType.information,
				cost=1340,
				required=[TechType.syntheticMaterials],
				flavors=[
					Flavor(FlavorType.offense, 3)
				]
			)
		elif self == TechType.robotics:
			# https://civilization.fandom.com/wiki/Robotics_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_ROBOTICS_NAME'),
				eureka_summary=_('TXT_KEY_TECH_ROBOTICS_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_ROBOTICS_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_TECH_ROBOTICS_QUOTE1'),
					_('TXT_KEY_TECH_ROBOTICS_QUOTE2')
				],
				era=EraType.information,
				cost=1560,
				required=[TechType.computers],
				flavors=[
					Flavor(FlavorType.production, 3),
					Flavor(FlavorType.offense, 3)
				]
			)
		elif self == TechType.nuclearFusion:
			# https://civilization.fandom.com/wiki/Nuclear_Fusion_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_NUCLEAR_FUSION_NAME'),
				eureka_summary=_('TXT_KEY_TECH_NUCLEAR_FUSION_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_NUCLEAR_FUSION_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_TECH_NUCLEAR_FUSION_QUOTE1'),
					_('TXT_KEY_TECH_NUCLEAR_FUSION_QUOTE2')
				],
				era=EraType.information,
				cost=1560,
				required=[TechType.lasers],
				flavors=[
					Flavor(FlavorType.energy, 3)
				]
			)
		elif self == TechType.nanotechnology:
			# https://civilization.fandom.com/wiki/Nanotechnology_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_NANOTECHNOLOGY_NAME'),
				eureka_summary=_('TXT_KEY_TECH_NANOTECHNOLOGY_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_NANOTECHNOLOGY_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_TECH_NANOTECHNOLOGY_QUOTE1'),
					_('TXT_KEY_TECH_NANOTECHNOLOGY_QUOTE2')
				],
				era=EraType.information,
				cost=1560,
				required=[TechType.composites],
				flavors=[
					Flavor(FlavorType.science, 3)
				]
			)

		elif self == TechType.futureTech:
			# https://civilization.fandom.com/wiki/Future_Tech_(Civ6)
			return TechTypeData(
				name=_('TXT_KEY_TECH_FUTURE_TECH_NAME'),
				eureka_summary=_('TXT_KEY_TECH_FUTURE_TECH_EUREKA'),
				eureka_description=_('TXT_KEY_TECH_FUTURE_TECH_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_TECH_FUTURE_TECH_QUOTE1'),
					_('TXT_KEY_TECH_FUTURE_TECH_QUOTE2')
				],
				era=EraType.future,
				cost=1780,
				required=[TechType.robotics, TechType.nuclearFusion],
				flavors=[]
			)

		raise AttributeError(f'cant get data for tech {self}')

	def __str__(self):
		return self.title()


class CivicType:
	pass


class CivicTypeData:
	def __init__(self, name: str, inspiration_summary: str, inspiration_description: str, quoteTexts: List[str],
				 era: EraType, cost: int, required: List[CivicType], flavors: List[Flavor], governorTitle: bool,
				 envoys: int):
		self.name = name
		self.inspiration_summary = inspiration_summary
		self.inspiration_description = inspiration_description
		self.quoteTexts = quoteTexts
		self.era = era
		self.cost = cost
		self.required = required
		self.flavors = flavors
		self.governorTitle = governorTitle
		self.envoys = envoys


class CivicType(ExtendedEnum):
	# default
	none = 'none'

	# ancient
	stateWorkforce = 'stateWorkforce'
	craftsmanship = 'craftsmanship'
	codeOfLaws = 'codeOfLaws'  # no eureka
	earlyEmpire = 'earlyEmpire'
	foreignTrade = 'foreignTrade'
	mysticism = 'mysticism'
	militaryTradition = 'militaryTradition'

	# classical
	defensiveTactics = 'defensiveTactics'
	gamesAndRecreation = 'gamesAndRecreation'
	politicalPhilosophy = 'politicalPhilosophy'
	recordedHistory = 'recordedHistory'
	dramaAndPoetry = 'dramaAndPoetry'
	theology = 'theology'
	militaryTraining = 'militaryTraining'

	# medieval
	navalTradition = 'navalTradition'
	feudalism = 'feudalism'
	medievalFaires = 'medievalFaires'
	civilService = 'civilService'
	guilds = 'guilds'
	mercenaries = 'mercenaries'
	divineRight = 'divineRight'

	# renaissance
	enlightenment = 'enlightenment'
	humanism = 'humanism'
	mercantilism = 'mercantilism'
	diplomaticService = 'diplomaticService'
	exploration = 'exploration'
	reformedChurch = 'reformedChurch'

	# industrial
	civilEngineering = 'civilEngineering'
	colonialism = 'colonialism'
	nationalism = 'nationalism'
	operaAndBallet = 'operaAndBallet'
	naturalHistory = 'naturalHistory'
	urbanization = 'urbanization'
	scorchedEarth = 'scorchedEarth'

	# modern
	conservation = 'conservation'
	massMedia = 'massMedia'
	mobilization = 'mobilization'
	capitalism = 'capitalism'
	ideology = 'ideology'
	nuclearProgram = 'nuclearProgram'
	suffrage = 'suffrage'
	totalitarianism = 'totalitarianism'
	classStruggle = 'classStruggle'

	# atomic
	culturalHeritage = 'culturalHeritage'
	coldWar = 'coldWar'
	professionalSports = 'professionalSports'
	rapidDeployment = 'rapidDeployment'
	spaceRace = 'spaceRace'

	# information
	environmentalism = 'environmentalism'
	globalization = 'globalization'
	socialMedia = 'socialMedia'
	nearFutureGovernance = 'nearFutureGovernance'
	# Venture Politics
	# Distributed Sovereignty
	# Optimization Imperative

	# future
	informationWarfare = 'informationWarfare'
	globalWarmingMitigation = 'globalWarmingMitigation'
	culturalHegemony = 'culturalHegemony'
	exodusImperative = 'exodusImperative'
	smartPowerDoctrine = 'smartPowerDoctrine'
	futureCivic = 'futureCivic'

	def title(self) -> str:
		return self._data().name

	def required(self) -> []:
		return self._data().required

	def cost(self) -> int:
		return self._data().cost

	def envoys(self) -> int:
		return self._data().envoys

	def hasGovernorTitle(self) -> bool:
		return self._data().governorTitle

	def era(self) -> EraType:
		return self._data().era

	def leadsTo(self) -> List[CivicType]:
		leadingTo: List[CivicType] = []

		for civic in list(CivicType):
			if self in civic.required():
				leadingTo.append(civic)

		return leadingTo

	def flavorValue(self, flavorType: FlavorType) -> int:
		flavorOfCivic = next((flavor for flavor in self._data().flavors if flavor.flavorType == flavorType), None)

		if flavorOfCivic is not None:
			return flavorOfCivic.value

		return 0

	def _data(self):
		# default
		if self == CivicType.none:
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_NONE'),
				inspiration_summary='',
				inspiration_description='',
				quoteTexts=[],
				era=EraType.ancient,
				cost=0,
				required=[],
				flavors=[],
				governorTitle=False,
				envoys=0
			)

		# ancient
		elif self == CivicType.stateWorkforce:
			# https://civilization.fandom.com/wiki/State_Workforce_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_STATE_WORKFORCE_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_STATE_WORKFORCE_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_STATE_WORKFORCE_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_STATE_WORKFORCE_QUOTE1'),
					_('TXT_KEY_CIVIC_STATE_WORKFORCE_QUOTE2')
				],
				era=EraType.ancient,
				cost=70,
				required=[CivicType.craftsmanship],
				flavors=[],
				governorTitle=True,
				envoys=0
			)
		elif self == CivicType.craftsmanship:
			# https://civilization.fandom.com/wiki/Craftsmanship_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_CRAFTSMANSHIP_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_CRAFTSMANSHIP_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_CRAFTSMANSHIP_EUREKA_TEXT'),
				quoteTexts=[
					"TXT_KEY_CIVIC_CRAFTSMANSHIP_QUOTE1",
					"TXT_KEY_CIVIC_CRAFTSMANSHIP_QUOTE2"
				],
				era=EraType.ancient,
				cost=40,
				required=[CivicType.codeOfLaws],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.codeOfLaws:  # no eureka
			# https://civilization.fandom.com/wiki/Code_of_Laws_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_CODE_OF_LAWS_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_CODE_OF_LAWS_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_CODE_OF_LAWS_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_CODE_OF_LAWS_QUOTE1'),
					_('TXT_KEY_CIVIC_CODE_OF_LAWS_QUOTE2')
				],
				era=EraType.ancient,
				cost=20,
				required=[],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.earlyEmpire:
			# https://civilization.fandom.com/wiki/Early_Empire_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_EARLY_EMPIRE_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_EARLY_EMPIRE_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_EARLY_EMPIRE_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_EARLY_EMPIRE_QUOTE1'),
					_('TXT_KEY_CIVIC_EARLY_EMPIRE_QUOTE2')
				],
				era=EraType.ancient,
				cost=70,
				required=[CivicType.foreignTrade],
				flavors=[],
				governorTitle=True,
				envoys=0
			)
		elif self == CivicType.foreignTrade:
			# https://civilization.fandom.com/wiki/Foreign_Trade_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_FOREIGN_TRADE_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_FOREIGN_TRADE_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_FOREIGN_TRADE_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_FOREIGN_TRADE_QUOTE1'),
					_('TXT_KEY_CIVIC_FOREIGN_TRADE_QUOTE2')
				],
				era=EraType.ancient,
				cost=40,
				required=[CivicType.codeOfLaws],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.mysticism:
			# https://civilization.fandom.com/wiki/Mysticism_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_MYSTICISM_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_MYSTICISM_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_MYSTICISM_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_MYSTICISM_QUOTE1'),
					_('TXT_KEY_CIVIC_MYSTICISM_QUOTE2')
				],
				era=EraType.ancient,
				cost=50,
				required=[CivicType.foreignTrade],
				flavors=[],
				governorTitle=False,
				envoys=1
			)
		elif self == CivicType.militaryTradition:
			# https://civilization.fandom.com/wiki/Military_Training_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_MILITARY_TRADITION_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_MILITARY_TRADITION_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_MILITARY_TRADITION_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_MILITARY_TRADITION_QUOTE1'),
					_('TXT_KEY_CIVIC_MILITARY_TRADITION_QUOTE2')
				],
				era=EraType.ancient,
				cost=50,
				required=[CivicType.craftsmanship],
				flavors=[],
				governorTitle=False,
				envoys=1
			)

		# classical
		elif self == CivicType.defensiveTactics:
			# https://civilization.fandom.com/wiki/Defensive_Tactics_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_DEFENSIVE_TACTICS_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_DEFENSIVE_TACTICS_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_DEFENSIVE_TACTICS_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_DEFENSIVE_TACTICS_QUOTE1'),
					_('TXT_KEY_CIVIC_DEFENSIVE_TACTICS_QUOTE2')
				],
				era=EraType.classical,
				cost=175,
				required=[CivicType.gamesAndRecreation, CivicType.politicalPhilosophy],
				flavors=[],
				governorTitle=True,
				envoys=0
			)
		elif self == CivicType.gamesAndRecreation:
			# https://civilization.fandom.com/wiki/Games_and_Recreation_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_GAMES_AND_RECREATION_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_GAMES_AND_RECREATION_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_GAMES_AND_RECREATION_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_GAMES_AND_RECREATION_QUOTE1'),
					_('TXT_KEY_CIVIC_GAMES_AND_RECREATION_QUOTE2')
				],
				era=EraType.classical,
				cost=110,
				required=[CivicType.stateWorkforce],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.politicalPhilosophy:
			# https://civilization.fandom.com/wiki/Political_Philosophy_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_POLITICAL_PHILOSOPHY_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_POLITICAL_PHILOSOPHY_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_POLITICAL_PHILOSOPHY_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_POLITICAL_PHILOSOPHY_QUOTE1'),
					_('TXT_KEY_CIVIC_POLITICAL_PHILOSOPHY_QUOTE2')
				],
				era=EraType.classical,
				cost=110,
				required=[CivicType.stateWorkforce, CivicType.earlyEmpire],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.recordedHistory:
			# https://civilization.fandom.com/wiki/Recorded_History_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_RECORDED_HISTORY_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_RECORDED_HISTORY_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_RECORDED_HISTORY_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_RECORDED_HISTORY_QUOTE1'),
					_('TXT_KEY_CIVIC_RECORDED_HISTORY_QUOTE2')
				],
				era=EraType.classical,
				cost=175,
				required=[CivicType.politicalPhilosophy, CivicType.dramaAndPoetry],
				flavors=[],
				governorTitle=True,
				envoys=0
			)
		elif self == CivicType.dramaAndPoetry:
			# https://civilization.fandom.com/wiki/Drama_and_Poetry_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_DRAMA_AND_POETRY_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_DRAMA_AND_POETRY_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_DRAMA_AND_POETRY_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_DRAMA_AND_POETRY_QUOTE1'),
					_('TXT_KEY_CIVIC_DRAMA_AND_POETRY_QUOTE2')
				],
				era=EraType.classical,
				cost=110,
				required=[CivicType.earlyEmpire],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.theology:
			# https://civilization.fandom.com/wiki/Theology_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_THEOLOGY_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_THEOLOGY_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_THEOLOGY_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_THEOLOGY_QUOTE1'),
					_('TXT_KEY_CIVIC_THEOLOGY_QUOTE2')
				],
				era=EraType.classical,
				cost=120,
				required=[CivicType.dramaAndPoetry, CivicType.mysticism],
				flavors=[],
				governorTitle=False,
				envoys=1
			)
		elif self == CivicType.militaryTraining:
			# https://civilization.fandom.com/wiki/Military_Training_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_MILITARY_TRAINING_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_MILITARY_TRAINING_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_MILITARY_TRAINING_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_MILITARY_TRAINING_QUOTE1'),
					_('TXT_KEY_CIVIC_MILITARY_TRAINING_QUOTE2')
				],
				era=EraType.classical,
				cost=120,
				required=[CivicType.militaryTradition, CivicType.gamesAndRecreation],
				flavors=[],
				governorTitle=False,
				envoys=0
			)

		# medieval
		elif self == CivicType.navalTradition:
			# https://civilization.fandom.com/wiki/Naval_Tradition_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_NAVAL_TRADITION_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_NAVAL_TRADITION_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_NAVAL_TRADITION_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_NAVAL_TRADITION_QUOTE1'),
					_('TXT_KEY_CIVIC_NAVAL_TRADITION_QUOTE2')
				],
				era=EraType.medieval,
				cost=200,
				required=[CivicType.defensiveTactics],
				flavors=[],
				governorTitle=False,
				envoys=1
			)
		elif self == CivicType.feudalism:
			# https://civilization.fandom.com/wiki/Feudalism_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_FEUDALISM_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_FEUDALISM_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_FEUDALISM_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_FEUDALISM_QUOTE1'),
					_('TXT_KEY_CIVIC_FEUDALISM_QUOTE2')
				],
				era=EraType.medieval,
				cost=275,
				required=[CivicType.defensiveTactics],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.medievalFaires:
			# https://civilization.fandom.com/wiki/Medieval_Faires_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_MEDIEVAL_FAIRES_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_MEDIEVAL_FAIRES_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_MEDIEVAL_FAIRES_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_MEDIEVAL_FAIRES_QUOTE1'),
					_('TXT_KEY_CIVIC_MEDIEVAL_FAIRES_QUOTE2')
				],
				era=EraType.medieval,
				cost=385,
				required=[CivicType.feudalism],
				flavors=[],
				governorTitle=True,
				envoys=0
			)
		elif self == CivicType.civilService:
			# https://civilization.fandom.com/wiki/Civil_Service_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_CIVIL_SERVICE_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_CIVIL_SERVICE_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_CIVIL_SERVICE_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_CIVIL_SERVICE_QUOTE1'),
					_('TXT_KEY_CIVIC_CIVIL_SERVICE_QUOTE2')
				],
				era=EraType.medieval,
				cost=275,
				required=[CivicType.defensiveTactics, CivicType.recordedHistory],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.guilds:
			# https://civilization.fandom.com/wiki/Guilds_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_GUILDS_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_GUILDS_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_GUILDS_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_GUILDS_QUOTE1'),
					_('TXT_KEY_CIVIC_GUILDS_QUOTE2')
				],
				era=EraType.medieval,
				cost=385,
				required=[CivicType.feudalism, CivicType.civilService],
				flavors=[],
				governorTitle=True,
				envoys=0
			)
		elif self == CivicType.mercenaries:
			# https://civilization.fandom.com/wiki/Mercenaries_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_MERCENARIES_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_MERCENARIES_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_MERCENARIES_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_MERCENARIES_QUOTE1'),
					_('TXT_KEY_CIVIC_MERCENARIES_QUOTE2')
				],
				era=EraType.medieval,
				cost=290,
				required=[CivicType.feudalism, CivicType.militaryTraining],
				flavors=[],
				governorTitle=False,
				envoys=2
			)
		elif self == CivicType.divineRight:
			# https://civilization.fandom.com/wiki/Divine_Right_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_DIVINE_RIGHT_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_DIVINE_RIGHT_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_DIVINE_RIGHT_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_DIVINE_RIGHT_QUOTE1'),
					_('TXT_KEY_CIVIC_DIVINE_RIGHT_QUOTE2')
				],
				era=EraType.medieval,
				cost=290,
				required=[CivicType.civilService, CivicType.theology],
				flavors=[],
				governorTitle=False,
				envoys=0
			)

		# renaissance
		elif self == CivicType.enlightenment:
			# https://civilization.fandom.com/wiki/The_Enlightenment_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_ENLIGHTENMENT_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_ENLIGHTENMENT_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_ENLIGHTENMENT_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_ENLIGHTENMENT_QUOTE1'),
					_('TXT_KEY_CIVIC_ENLIGHTENMENT_QUOTE2')
				],
				era=EraType.renaissance,
				cost=655,
				required=[CivicType.diplomaticService],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.humanism:
			# https://civilization.fandom.com/wiki/Humanism_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_HUMANISM_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_HUMANISM_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_HUMANISM_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_HUMANISM_QUOTE1'),
					_('TXT_KEY_CIVIC_HUMANISM_QUOTE2')
				],
				era=EraType.renaissance,
				cost=540,
				required=[CivicType.guilds, CivicType.medievalFaires],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.mercantilism:
			# https://civilization.fandom.com/wiki/Mercantilism_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_MERCANTILISM_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_MERCANTILISM_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_MERCANTILISM_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_MERCANTILISM_QUOTE1'),
					_('TXT_KEY_CIVIC_MERCANTILISM_QUOTE2')
				],
				era=EraType.renaissance,
				cost=655,
				required=[CivicType.humanism],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.diplomaticService:
			# https://civilization.fandom.com/wiki/Diplomatic_Service_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_DIPLOMATIC_SERVICE_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_DIPLOMATIC_SERVICE_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_DIPLOMATIC_SERVICE_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_DIPLOMATIC_SERVICE_QUOTE1'),
					_('TXT_KEY_CIVIC_DIPLOMATIC_SERVICE_QUOTE2')
				],
				era=EraType.renaissance,
				cost=540,
				required=[CivicType.guilds],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.exploration:
			# https://civilization.fandom.com/wiki/Exploration_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_EXPLORATION_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_EXPLORATION_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_EXPLORATION_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_EXPLORATION_QUOTE1'),
					_('TXT_KEY_CIVIC_EXPLORATION_QUOTE2')
				],
				era=EraType.renaissance,
				cost=400,
				required=[CivicType.mercenaries, CivicType.medievalFaires],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.reformedChurch:
			# https://civilization.fandom.com/wiki/Reformed_Church_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_REFORMED_CHURCH_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_REFORMED_CHURCH_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_REFORMED_CHURCH_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_REFORMED_CHURCH_QUOTE1'),
					_('TXT_KEY_CIVIC_REFORMED_CHURCH_QUOTE2')
				],
				era=EraType.renaissance,
				cost=400,
				required=[CivicType.divineRight],
				flavors=[],
				governorTitle=False,
				envoys=0
			)

		# industrial
		elif self == CivicType.civilEngineering:
			# https://civilization.fandom.com/wiki/Civil_Engineering_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_CIVIL_ENGINEERING_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_CIVIL_ENGINEERING_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_CIVIL_ENGINEERING_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_CIVIL_ENGINEERING_QUOTE1'),
					_('TXT_KEY_CIVIC_CIVIL_ENGINEERING_QUOTE2')
				],
				era=EraType.industrial,
				cost=920,
				required=[CivicType.mercantilism],
				flavors=[],
				governorTitle=True,
				envoys=0
			)
		elif self == CivicType.colonialism:
			# https://civilization.fandom.com/wiki/Colonialism_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_COLONIALISM_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_COLONIALISM_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_COLONIALISM_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_COLONIALISM_QUOTE1'),
					_('TXT_KEY_CIVIC_COLONIALISM_QUOTE2')
				],
				era=EraType.industrial,
				cost=725,
				required=[CivicType.mercantilism],
				flavors=[],
				governorTitle=False,
				envoys=2
			)
		elif self == CivicType.nationalism:
			# https://civilization.fandom.com/wiki/Nationalism_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_NATIONALISM_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_NATIONALISM_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_NATIONALISM_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_NATIONALISM_QUOTE1'),
					_('TXT_KEY_CIVIC_NATIONALISM_QUOTE2')
				],
				era=EraType.industrial,
				cost=920,
				required=[CivicType.enlightenment],
				flavors=[],
				governorTitle=True,
				envoys=0
			)
		elif self == CivicType.operaAndBallet:
			# https://civilization.fandom.com/wiki/Opera_and_Ballet_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_OPERA_AND_BALLET_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_OPERA_AND_BALLET_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_OPERA_AND_BALLET_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_OPERA_AND_BALLET_QUOTE1'),
					_('TXT_KEY_CIVIC_OPERA_AND_BALLET_QUOTE2')
				],
				era=EraType.industrial,
				cost=725,
				required=[CivicType.enlightenment],
				flavors=[],
				governorTitle=False,
				envoys=2
			)
		elif self == CivicType.naturalHistory:
			# https://civilization.fandom.com/wiki/Natural_History_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_NATURAL_HISTORY_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_NATURAL_HISTORY_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_NATURAL_HISTORY_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_NATURAL_HISTORY_QUOTE1'),
					_('TXT_KEY_CIVIC_NATURAL_HISTORY_QUOTE2')
				],
				era=EraType.industrial,
				cost=870,
				required=[CivicType.colonialism],
				flavors=[],
				governorTitle=False,
				envoys=2
			)
		elif self == CivicType.urbanization:
			# https://civilization.fandom.com/wiki/Urbanization_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_URBANIZATION_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_URBANIZATION_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_URBANIZATION_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_URBANIZATION_QUOTE1'),
					_('TXT_KEY_CIVIC_URBANIZATION_QUOTE2')
				],
				era=EraType.industrial,
				cost=1060,
				required=[CivicType.civilEngineering, CivicType.nationalism],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.scorchedEarth:
			# https://civilization.fandom.com/wiki/Scorched_Earth_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_SCORCHED_EARTH_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_SCORCHED_EARTH_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_SCORCHED_EARTH_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_SCORCHED_EARTH_QUOTE1'),
					_('TXT_KEY_CIVIC_SCORCHED_EARTH_QUOTE2')
				],
				era=EraType.industrial,
				cost=1060,
				required=[CivicType.nationalism],
				flavors=[],
				governorTitle=False,
				envoys=2
			)

		# modern
		elif self == CivicType.conservation:
			# https://civilization.fandom.com/wiki/Conservation_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_CONSERVATION_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_CONSERVATION_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_CONSERVATION_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_CONSERVATION_QUOTE1'),
					_('TXT_KEY_CIVIC_CONSERVATION_QUOTE2')
				],
				era=EraType.modern,
				cost=1255,
				required=[CivicType.naturalHistory, CivicType.urbanization],
				flavors=[],
				governorTitle=False,
				envoys=2
			)
		elif self == CivicType.massMedia:
			# https://civilization.fandom.com/wiki/Mass_Media_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_MASS_MEDIA_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_MASS_MEDIA_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_MASS_MEDIA_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_MASS_MEDIA_QUOTE1'),
					_('TXT_KEY_CIVIC_MASS_MEDIA_QUOTE2')
				],
				era=EraType.modern,
				cost=1410,
				required=[CivicType.urbanization],
				flavors=[],
				governorTitle=True,
				envoys=0
			)
		elif self == CivicType.mobilization:
			# https://civilization.fandom.com/wiki/Mobilization_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_MOBILIZATION_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_MOBILIZATION_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_MOBILIZATION_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_MOBILIZATION_QUOTE1'),
					_('TXT_KEY_CIVIC_MOBILIZATION_QUOTE2')
				],
				era=EraType.modern,
				cost=1410,
				required=[CivicType.urbanization],
				flavors=[],
				governorTitle=True,
				envoys=0
			)
		elif self == CivicType.capitalism:
			# https://civilization.fandom.com/wiki/Capitalism_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_CAPITALISM_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_CAPITALISM_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_CAPITALISM_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_CAPITALISM_QUOTE1'),
					_('TXT_KEY_CIVIC_CAPITALISM_QUOTE2')
				],
				era=EraType.modern,
				cost=1560,
				required=[CivicType.massMedia],
				flavors=[],
				governorTitle=False,
				envoys=3
			)
		elif self == CivicType.ideology:
			# https://civilization.fandom.com/wiki/Ideology_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_IDEOLOGY_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_IDEOLOGY_EUREKA'),  # no inspiration
				inspiration_description=_('TXT_KEY_CIVIC_IDEOLOGY_EUREKA_TEXT'),  # no inspiration
				quoteTexts=[
					_('TXT_KEY_CIVIC_IDEOLOGY_QUOTE1'),
					_('TXT_KEY_CIVIC_IDEOLOGY_QUOTE2')
				],
				era=EraType.modern,
				cost=660,
				required=[CivicType.massMedia, CivicType.mobilization],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.nuclearProgram:
			# https://civilization.fandom.com/wiki/Nuclear_Program_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_NUCLEAR_PROGRAM_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_NUCLEAR_PROGRAM_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_NUCLEAR_PROGRAM_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_NUCLEAR_PROGRAM_QUOTE1'),
					_('TXT_KEY_CIVIC_NUCLEAR_PROGRAM_QUOTE2')
				],
				era=EraType.modern,
				cost=1715,
				required=[CivicType.ideology],
				flavors=[],
				governorTitle=False,
				envoys=3
			)
		elif self == CivicType.suffrage:
			# https://civilization.fandom.com/wiki/Suffrage_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_SUFFRAGE_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_SUFFRAGE_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_SUFFRAGE_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_SUFFRAGE_QUOTE1'),
					_('TXT_KEY_CIVIC_SUFFRAGE_QUOTE2')
				],
				era=EraType.modern,
				cost=1715,
				required=[CivicType.ideology],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.totalitarianism:
			# https://civilization.fandom.com/wiki/Totalitarianism_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_TOTALITARIANISM_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_TOTALITARIANISM_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_TOTALITARIANISM_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_TOTALITARIANISM_QUOTE1'),
					_('TXT_KEY_CIVIC_TOTALITARIANISM_QUOTE2')
				],
				era=EraType.modern,
				cost=1715,
				required=[CivicType.ideology],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.classStruggle:
			# https://civilization.fandom.com/wiki/Class_Struggle_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_CLASS_STRUGGLE_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_CLASS_STRUGGLE_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_CLASS_STRUGGLE_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_CLASS_STRUGGLE_QUOTE1'),
					_('TXT_KEY_CIVIC_CLASS_STRUGGLE_QUOTE2')
				],
				era=EraType.modern,
				cost=1715,
				required=[CivicType.ideology],
				flavors=[],
				governorTitle=False,
				envoys=0
			)

		# atomic
		elif self == CivicType.culturalHeritage:
			# https://civilization.fandom.com/wiki/Cultural_Heritage_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_CULTURAL_HERITAGE_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_CULTURAL_HERITAGE_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_CULTURAL_HERITAGE_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_CULTURAL_HERITAGE_QUOTE1'),
					_('TXT_KEY_CIVIC_CULTURAL_HERITAGE_QUOTE2')
				],
				era=EraType.atomic,
				cost=1955,
				required=[CivicType.conservation],
				flavors=[],
				governorTitle=False,
				envoys=3
			)
		elif self == CivicType.coldWar:
			# https://civilization.fandom.com/wiki/Cold_War_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_COLD_WAR_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_COLD_WAR_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_COLD_WAR_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_COLD_WAR_QUOTE1'),
					_('TXT_KEY_CIVIC_COLD_WAR_QUOTE2')
				],
				era=EraType.atomic,
				cost=2185,
				required=[CivicType.ideology],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.professionalSports:
			# https://civilization.fandom.com/wiki/Professional_Sports_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_PROFESSIONAL_SPORTS_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_PROFESSIONAL_SPORTS_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_PROFESSIONAL_SPORTS_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_PROFESSIONAL_SPORTS_QUOTE1'),
					_('TXT_KEY_CIVIC_PROFESSIONAL_SPORTS_QUOTE2')
				],
				era=EraType.atomic,
				cost=2185,
				required=[CivicType.ideology],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.rapidDeployment:
			# https://civilization.fandom.com/wiki/Rapid_Deployment_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_RAPID_DEPLOYMENT_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_RAPID_DEPLOYMENT_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_RAPID_DEPLOYMENT_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_RAPID_DEPLOYMENT_QUOTE1'),
					_('TXT_KEY_CIVIC_RAPID_DEPLOYMENT_QUOTE2')
				],
				era=EraType.atomic,
				cost=2415,
				required=[CivicType.coldWar],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.spaceRace:
			# https://civilization.fandom.com/wiki/Space_Race_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_SPACE_RACE_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_SPACE_RACE_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_SPACE_RACE_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_SPACE_RACE_QUOTE1'),
					_('TXT_KEY_CIVIC_SPACE_RACE_QUOTE2')
				],
				era=EraType.atomic,
				cost=2415,
				required=[CivicType.coldWar],
				flavors=[],
				governorTitle=False,
				envoys=0
			)

		# information
		elif self == CivicType.environmentalism:
			# https://civilization.fandom.com/wiki/Environmentalism_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_ENVIRONMENTALISM_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_ENVIRONMENTALISM_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_ENVIRONMENTALISM_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_ENVIRONMENTALISM_QUOTE1')
				],
				era=EraType.information,
				cost=2880,
				required=[CivicType.culturalHeritage, CivicType.rapidDeployment],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.globalization:
			# https://civilization.fandom.com/wiki/Globalization_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_GLOBALIZATION_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_GLOBALIZATION_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_GLOBALIZATION_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_GLOBALIZATION_QUOTE1'),
					_('TXT_KEY_CIVIC_GLOBALIZATION_QUOTE2')
				],
				era=EraType.information,
				cost=2880,
				required=[CivicType.rapidDeployment, CivicType.spaceRace],
				flavors=[],
				governorTitle=True,
				envoys=0
			)
		elif self == CivicType.socialMedia:
			# https://civilization.fandom.com/wiki/Social_Media_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_SOCIAL_MEDIA_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_SOCIAL_MEDIA_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_SOCIAL_MEDIA_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_SOCIAL_MEDIA_QUOTE1'),
					_('TXT_KEY_CIVIC_SOCIAL_MEDIA_QUOTE2')
				],
				era=EraType.information,
				cost=2880,
				required=[CivicType.professionalSports, CivicType.spaceRace],
				flavors=[
					Flavor(FlavorType.growth, 6)
				],
				governorTitle=True,
				envoys=0
			)
		elif self == CivicType.nearFutureGovernance:
			# https://civilization.fandom.com/wiki/Near_Future_Governance_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_NEAR_FUTURE_GOVERNANCE_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_NEAR_FUTURE_GOVERNANCE_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_NEAR_FUTURE_GOVERNANCE_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_NEAR_FUTURE_GOVERNANCE_QUOTE1')
				],
				era=EraType.future,
				cost=3100,
				required=[CivicType.environmentalism, CivicType.globalization],
				flavors=[],
				governorTitle=True,
				envoys=3
			)

		# Venture Politics
		# Distributed Sovereignty
		# Optimization Imperative

		# future
		elif self == CivicType.informationWarfare:
			# https://civilization.fandom.com/wiki/Information_Warfare_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_INFORMATION_WARFARE_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_INFORMATION_WARFARE_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_INFORMATION_WARFARE_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_INFORMATION_WARFARE_QUOTE1'),
					_('TXT_KEY_CIVIC_INFORMATION_WARFARE_QUOTE2')
				],
				era=EraType.future,
				cost=3200,
				required=[CivicType.socialMedia],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.globalWarmingMitigation:
			# https://civilization.fandom.com/wiki/Global_Warming_Mitigation_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_GLOBAL_WARMING_MITIGATION_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_GLOBAL_WARMING_MITIGATION_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_GLOBAL_WARMING_MITIGATION_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_GLOBAL_WARMING_MITIGATION_QUOTE1'),
					_('TXT_KEY_CIVIC_GLOBAL_WARMING_MITIGATION_QUOTE2')
				],
				era=EraType.future,
				cost=3200,
				required=[CivicType.informationWarfare],
				flavors=[],
				governorTitle=False,
				envoys=3
			)
		elif self == CivicType.culturalHegemony:
			# https://civilization.fandom.com/wiki/Cultural_Hegemony_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_CULTURAL_HEGEMONY_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_CULTURAL_HEGEMONY_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_CULTURAL_HEGEMONY_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_CULTURAL_HEGEMONY_QUOTE1')
				],
				era=EraType.future,
				cost=3200,
				required=[CivicType.globalWarmingMitigation],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.exodusImperative:
			# https://civilization.fandom.com/wiki/Exodus_Imperative_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_EXODUS_IMPERATIVE_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_EXODUS_IMPERATIVE_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_EXODUS_IMPERATIVE_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_EXODUS_IMPERATIVE_QUOTE1')
				],
				era=EraType.future,
				cost=3200,
				required=[CivicType.smartPowerDoctrine],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.smartPowerDoctrine:
			# https://civilization.fandom.com/wiki/Smart_Power_Doctrine_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_SMART_POWER_DOCTRINE_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_SMART_POWER_DOCTRINE_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_SMART_POWER_DOCTRINE_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_SMART_POWER_DOCTRINE_QUOTE1')
				],
				era=EraType.future,
				cost=3200,
				required=[CivicType.culturalHegemony],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.futureCivic:
			# https://civilization.fandom.com/wiki/Future_Civic_(Civ6)
			return CivicTypeData(
				name=_('TXT_KEY_CIVIC_FUTURE_CIVIC_TITLE'),
				inspiration_summary=_('TXT_KEY_CIVIC_FUTURE_CIVIC_EUREKA'),
				inspiration_description=_('TXT_KEY_CIVIC_FUTURE_CIVIC_EUREKA_TEXT'),
				quoteTexts=[
					_('TXT_KEY_CIVIC_FUTURE_CIVIC_QUOTE1')
				],
				era=EraType.future,
				cost=3200,
				required=[CivicType.exodusImperative],
				flavors=[],
				governorTitle=True,
				envoys=0
			)

		raise AttributeError(f'cant get data for civic {self}')

	def __str__(self):
		return self.title()
