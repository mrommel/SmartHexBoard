from smarthexboard.game.eras import EraType
from smarthexboard.game.flavors import Flavor, FlavorType
from smarthexboard.map.base import ExtendedEnum


class TechType:
	pass

class TechTypeData:
	def __init__(self, name: str, eureka_summary: str, eureka_description: str, quoteTexts: [str], era: EraType,
				 cost: int, required: [TechType], flavors: [Flavor]):
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

	def name(self) -> str:
		return self._data().name

	def required(self) -> []:
		return self._data().required

	def cost(self) -> int:
		return self._data().cost

	def _data(self):
		if self == TechType.none:
			return TechTypeData(
				name='TXT_KEY_TECH_NONE',
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
				name='TXT_KEY_TECH_MINING_NAME',
				eureka_summary='TXT_KEY_TECH_MINING_EUREKA',
				eureka_description='TXT_KEY_TECH_MINING_EUREKA_TEXT',
				quoteTexts=['TXT_KEY_TECH_MINING_QUOTE1', 'TXT_KEY_TECH_MINING_QUOTE2'],
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
				name='TXT_KEY_TECH_POTTERY_NAME',
				eureka_summary='TXT_KEY_TECH_POTTERY_EUREKA',
				eureka_description='TXT_KEY_TECH_POTTERY_EUREKA_TEXT',
				quoteTexts=['TXT_KEY_TECH_POTTERY_QUOTE1', 'TXT_KEY_TECH_POTTERY_QUOTE2'],
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
				name='TXT_KEY_TECH_ANIMAL_HUSBANDRY_NAME',
				eureka_summary='TXT_KEY_TECH_ANIMAL_HUSBANDRY_EUREKA',
				eureka_description='TXT_KEY_TECH_ANIMAL_HUSBANDRY_EUREKA_TEXT',
				quoteTexts=['TXT_KEY_TECH_ANIMAL_HUSBANDRY_QUOTE1', 'TXT_KEY_TECH_ANIMAL_HUSBANDRY_QUOTE2'],
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
				name='TXT_KEY_TECH_SAILING_NAME',
				eureka_summary='TXT_KEY_TECH_SAILING_EUREKA',
				eureka_description='TXT_KEY_TECH_SAILING_EUREKA_TEXT',
				quoteTexts=['TXT_KEY_TECH_SAILING_QUOTE1', 'TXT_KEY_TECH_SAILING_QUOTE2'],
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
				name='TXT_KEY_TECH_ASTROLOGY_NAME',
				eureka_summary='TXT_KEY_TECH_ASTROLOGY_EUREKA',
				eureka_description='TXT_KEY_TECH_ASTROLOGY_EUREKA_TEXT',
				quoteTexts=['TXT_KEY_TECH_ASTROLOGY_QUOTE1', 'TXT_KEY_TECH_ASTROLOGY_QUOTE2'],
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
				name='TXT_KEY_TECH_IRRIGATION_NAME',
				eureka_summary='TXT_KEY_TECH_IRRIGATION_EUREKA',
				eureka_description='TXT_KEY_TECH_IRRIGATION_EUREKA_TEXT',
				quoteTexts=['TXT_KEY_TECH_IRRIGATION_QUOTE1', 'TXT_KEY_TECH_IRRIGATION_QUOTE2'],
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
				name='TXT_KEY_TECH_WRITING_NAME',
				eureka_summary='TXT_KEY_TECH_WRITING_EUREKA',
				eureka_description='TXT_KEY_TECH_WRITING_EUREKA_TEXT',
				quoteTexts=['TXT_KEY_TECH_WRITING_QUOTE1', 'TXT_KEY_TECH_WRITING_QUOTE2'],
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
				name='TXT_KEY_TECH_MASONRY_NAME',
				eureka_summary='TXT_KEY_TECH_MASONRY_EUREKA',
				eureka_description='TXT_KEY_TECH_MASONRY_EUREKA_TEXT',
				quoteTexts=['TXT_KEY_TECH_MASONRY_QUOTE1', 'TXT_KEY_TECH_MASONRY_QUOTE2'],
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
				name='TXT_KEY_TECH_ARCHERY_NAME',
				eureka_summary='TXT_KEY_TECH_ARCHERY_EUREKA',
				eureka_description='TXT_KEY_TECH_ARCHERY_EUREKA_TEXT',
				quoteTexts=['TXT_KEY_TECH_ARCHERY_QUOTE1', 'TXT_KEY_TECH_ARCHERY_QUOTE2'],
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
				name='TXT_KEY_TECH_BRONZE_WORKING_NAME',
				eureka_summary='TXT_KEY_TECH_BRONZE_WORKING_EUREKA',
				eureka_description='TXT_KEY_TECH_BRONZE_WORKING_EUREKA_TEXT',
				quoteTexts=['TXT_KEY_TECH_BRONZE_WORKING_QUOTE1', 'TXT_KEY_TECH_BRONZE_WORKING_QUOTE2'],
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
				name='TXT_KEY_TECH_WHEEL_NAME',
				eureka_summary='TXT_KEY_TECH_WHEEL_EUREKA',
				eureka_description='TXT_KEY_TECH_WHEEL_EUREKA_TEXT',
				quoteTexts=['TXT_KEY_TECH_WHEEL_QUOTE1', 'TXT_KEY_TECH_WHEEL_QUOTE2'],
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
				name='TXT_KEY_TECH_CELESTIAL_NAVIGATION_NAME',
				eureka_summary='TXT_KEY_TECH_CELESTIAL_NAVIGATION_EUREKA',
				eureka_description='TXT_KEY_TECH_CELESTIAL_NAVIGATION_EUREKA_TEXT',
				quoteTexts=['TXT_KEY_TECH_CELESTIAL_NAVIGATION_QUOTE1', 'TXT_KEY_TECH_CELESTIAL_NAVIGATION_QUOTE2'],
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
				name='TXT_KEY_TECH_HORSEBACK_RIDING_NAME',
				eureka_summary='TXT_KEY_TECH_HORSEBACK_RIDING_EUREKA',
				eureka_description='TXT_KEY_TECH_HORSEBACK_RIDING_EUREKA_TEXT',
				quoteTexts=['TXT_KEY_TECH_HORSEBACK_RIDING_QUOTE1', 'TXT_KEY_TECH_HORSEBACK_RIDING_QUOTE2'],
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
				name='TXT_KEY_TECH_CURRENCY_NAME',
				eureka_summary='TXT_KEY_TECH_CURRENCY_EUREKA',
				eureka_description='TXT_KEY_TECH_CURRENCY_EUREKA_TEXT',
				quoteTexts=['TXT_KEY_TECH_CURRENCY_QUOTE1', 'TXT_KEY_TECH_CURRENCY_QUOTE2'],
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
				name='TXT_KEY_TECH_CONSTRUCTION_NAME',
				eureka_summary='TXT_KEY_TECH_CONSTRUCTION_EUREKA',
				eureka_description='TXT_KEY_TECH_CONSTRUCTION_EUREKA_TEXT',
				quoteTexts=['TXT_KEY_TECH_CONSTRUCTION_QUOTE1', 'TXT_KEY_TECH_CONSTRUCTION_QUOTE2'],
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
				name='TXT_KEY_TECH_IRON_WORKING_NAME',
				eureka_summary='TXT_KEY_TECH_IRON_WORKING_EUREKA',
				eureka_description='TXT_KEY_TECH_IRON_WORKING_EUREKA_TEXT',
				quoteTexts=['TXT_KEY_TECH_IRON_WORKING_QUOTE1', 'TXT_KEY_TECH_IRON_WORKING_QUOTE2'],
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
				name='TXT_KEY_TECH_SHIP_BUILDING_NAME',
				eureka_summary='TXT_KEY_TECH_SHIP_BUILDING_EUREKA',
				eureka_description='TXT_KEY_TECH_SHIP_BUILDING_EUREKA_TEXT',
				quoteTexts=['TXT_KEY_TECH_SHIP_BUILDING_QUOTE1', 'TXT_KEY_TECH_SHIP_BUILDING_QUOTE2'],
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
				name='TXT_KEY_TECH_MATHEMATICS_NAME',
				eureka_summary='TXT_KEY_TECH_MATHEMATICS_EUREKA',
				eureka_description='TXT_KEY_TECH_MATHEMATICS_EUREKA_TEXT',
				quoteTexts=['TXT_KEY_TECH_MATHEMATICS_QUOTE1', 'TXT_KEY_TECH_MATHEMATICS_QUOTE2'],
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
				name='TXT_KEY_TECH_ENGINEERING_NAME',
				eureka_summary='TXT_KEY_TECH_ENGINEERING_EUREKA',
				eureka_description='TXT_KEY_TECH_ENGINEERING_EUREKA_TEXT',
				quoteTexts=['TXT_KEY_TECH_ENGINEERING_QUOTE1', 'TXT_KEY_TECH_ENGINEERING_QUOTE2'],
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
				name='TXT_KEY_TECH_MILITARY_TACTICS_NAME',
				eureka_summary='TXT_KEY_TECH_MILITARY_TACTICS_EUREKA',
				eureka_description='TXT_KEY_TECH_MILITARY_TACTICS_EUREKA_TEXT',
				quoteTexts=['TXT_KEY_TECH_MILITARY_TACTICS_QUOTE1', 'TXT_KEY_TECH_MILITARY_TACTICS_QUOTE2'],
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
				name='TXT_KEY_TECH_BUTTRESS_NAME',
				eureka_summary='TXT_KEY_TECH_BUTTRESS_EUREKA',
				eureka_description='TXT_KEY_TECH_BUTTRESS_EUREKA_TEXT',
				quoteTexts=['TXT_KEY_TECH_BUTTRESS_QUOTE1', 'TXT_KEY_TECH_BUTTRESS_QUOTE2'],
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
				name='TXT_KEY_TECH_APPRENTICESHIP_NAME',
				eureka_summary='TXT_KEY_TECH_APPRENTICESHIP_EUREKA',
				eureka_description='TXT_KEY_TECH_APPRENTICESHIP_EUREKA_TEXT',
				quoteTexts=['TXT_KEY_TECH_APPRENTICESHIP_QUOTE1', 'TXT_KEY_TECH_APPRENTICESHIP_QUOTE2'],
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
				name='TXT_KEY_TECH_STIRRUPS_NAME',
				eureka_summary='TXT_KEY_TECH_STIRRUPS_EUREKA',
				eureka_description='TXT_KEY_TECH_STIRRUPS_EUREKA_TEXT',
				quoteTexts=['TXT_KEY_TECH_STIRRUPS_QUOTE1', 'TXT_KEY_TECH_STIRRUPS_QUOTE2'],
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
				name='TXT_KEY_TECH_MACHINERY_NAME',
				eureka_summary='TXT_KEY_TECH_MACHINERY_EUREKA',
				eureka_description='TXT_KEY_TECH_MACHINERY_EUREKA_TEXT',
				quoteTexts=['TXT_KEY_TECH_MACHINERY_QUOTE1', 'TXT_KEY_TECH_MACHINERY_QUOTE2'],
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
				name='TXT_KEY_TECH_EDUCATION_NAME',
				eureka_summary='TXT_KEY_TECH_EDUCATION_EUREKA',
				eureka_description='TXT_KEY_TECH_EDUCATION_EUREKA_TEXT',
				quoteTexts=['TXT_KEY_TECH_EDUCATION_QUOTE1', 'TXT_KEY_TECH_EDUCATION_QUOTE2'],
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
				name='TXT_KEY_TECH_MILITARY_ENGINEERING_NAME',
				eureka_summary='TXT_KEY_TECH_MILITARY_ENGINEERING_EUREKA',
				eureka_description='TXT_KEY_TECH_MILITARY_ENGINEERING_EUREKA_TEXT',
				quoteTexts=['TXT_KEY_TECH_MILITARY_ENGINEERING_QUOTE1', 'TXT_KEY_TECH_MILITARY_ENGINEERING_QUOTE2'],
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
				name='TXT_KEY_TECH_CASTLES_NAME',
				eureka_summary='TXT_KEY_TECH_CASTLES_EUREKA',
				eureka_description='TXT_KEY_TECH_CASTLES_EUREKA_TEXT',
				quoteTexts=['TXT_KEY_TECH_CASTLES_QUOTE1', 'TXT_KEY_TECH_CASTLES_QUOTE2'],
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
				name='TXT_KEY_TECH_CARTOGRAPHY_NAME',
				eureka_summary='TXT_KEY_TECH_CARTOGRAPHY_EUREKA',
				eureka_description='TXT_KEY_TECH_CARTOGRAPHY_EUREKA_TEXT',
				quoteTexts=['TXT_KEY_TECH_CARTOGRAPHY_QUOTE1', 'TXT_KEY_TECH_CARTOGRAPHY_QUOTE2'],
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
				name='TXT_KEY_TECH_MASS_PRODUCTION_NAME',
				eureka_summary='TXT_KEY_TECH_MASS_PRODUCTION_NAME',
				eureka_description='TXT_KEY_TECH_MASS_PRODUCTION_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_TECH_MASS_PRODUCTION_QUOTE1',
					'TXT_KEY_TECH_MASS_PRODUCTION_QUOTE2'
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
				name='TXT_KEY_TECH_BANKING_NAME',
				eureka_summary='TXT_KEY_TECH_BANKING_NAME',
				eureka_description='TXT_KEY_TECH_BANKING_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_TECH_BANKING_QUOTE1',
					'TXT_KEY_TECH_BANKING_QUOTE2'
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
				name='TXT_KEY_TECH_GUNPOWDER_NAME',
				eureka_summary='TXT_KEY_TECH_GUNPOWDER_EUREKA',
				eureka_description='TXT_KEY_TECH_GUNPOWDER_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_TECH_GUNPOWDER_QUOTE1',
					'TXT_KEY_TECH_GUNPOWDER_QUOTE2'
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
				name='TXT_KEY_TECH_PRINTING_NAME',
				eureka_summary='TXT_KEY_TECH_PRINTING_EUREKA',
				eureka_description='TXT_KEY_TECH_PRINTING_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_TECH_PRINTING_QUOTE1',
					'TXT_KEY_TECH_PRINTING_QUOTE2'
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
				name='TXT_KEY_TECH_SQUARE_RIGGING_NAME',
				eureka_summary='TXT_KEY_TECH_SQUARE_RIGGING_EUREKA',
				eureka_description='TXT_KEY_TECH_SQUARE_RIGGING_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_TECH_SQUARE_RIGGING_QUOTE1',
					'TXT_KEY_TECH_SQUARE_RIGGING_QUOTE2'
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
				name='TXT_KEY_TECH_ASTRONOMY_NAME',
				eureka_summary='TXT_KEY_TECH_ASTRONOMY_NAME',
				eureka_description='TXT_KEY_TECH_ASTRONOMY_NAME',
				quoteTexts=[
					'TXT_KEY_TECH_ASTRONOMY_QUOTE1',
					'TXT_KEY_TECH_ASTRONOMY_QUOTE2'
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
				name='TXT_KEY_TECH_METAL_CASTING_NAME',
				eureka_summary='TXT_KEY_TECH_METAL_CASTING_EUREKA',
				eureka_description='TXT_KEY_TECH_METAL_CASTING_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_TECH_METAL_CASTING_QUOTE1',
					'TXT_KEY_TECH_METAL_CASTING_QUOTE2'
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
				name='TXT_KEY_TECH_SIEGE_TACTICS_NAME',
				eureka_summary='TXT_KEY_TECH_SIEGE_TACTICS_EUREKA',
				eureka_description='TXT_KEY_TECH_SIEGE_TACTICS_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_TECH_SIEGE_TACTICS_QUOTE1',
					'TXT_KEY_TECH_SIEGE_TACTICS_QUOTE2'
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
				name='TXT_KEY_TECH_INDUSTRIALIZATION_NAME',
				eureka_summary='TXT_KEY_TECH_INDUSTRIALIZATION_EUREKA',
				eureka_description='TXT_KEY_TECH_INDUSTRIALIZATION_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_TECH_INDUSTRIALIZATION_QUOTE1',
					'TXT_KEY_TECH_INDUSTRIALIZATION_QUOTE2'
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
				name='TXT_KEY_TECH_SCIENTIFIC_THEORY_NAME',
				eureka_summary='TXT_KEY_TECH_SCIENTIFIC_THEORY_EUREKA',
				eureka_description='TXT_KEY_TECH_SCIENTIFIC_THEORY_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_TECH_SCIENTIFIC_THEORY_QUOTE1',
					'TXT_KEY_TECH_SCIENTIFIC_THEORY_QUOTE2'
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
				name='TXT_KEY_TECH_BALLISTICS_NAME',
				eureka_summary='TXT_KEY_TECH_BALLISTICS_EUREKA',
				eureka_description='TXT_KEY_TECH_BALLISTICS_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_TECH_BALLISTICS_QUOTE1',
					'TXT_KEY_TECH_BALLISTICS_QUOTE2'
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
				name='TXT_KEY_TECH_MILITARY_SCIENCE_NAME',
				eureka_summary='TXT_KEY_TECH_MILITARY_SCIENCE_EUREKA',
				eureka_description='TXT_KEY_TECH_MILITARY_SCIENCE_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_TECH_MILITARY_SCIENCE_QUOTE1',
					'TXT_KEY_TECH_MILITARY_SCIENCE_QUOTE2'
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
				name='TXT_KEY_TECH_STEAM_POWER_NAME',
				eureka_summary='TXT_KEY_TECH_STEAM_POWER_EUREKA',
				eureka_description='TXT_KEY_TECH_STEAM_POWER_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_TECH_STEAM_POWER_QUOTE1',
					'TXT_KEY_TECH_STEAM_POWER_QUOTE2'
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
				name='TXT_KEY_TECH_SANITATION_NAME',
				eureka_summary='TXT_KEY_TECH_SANITATION_EUREKA',
				eureka_description='TXT_KEY_TECH_SANITATION_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_TECH_SANITATION_QUOTE1',
					'TXT_KEY_TECH_SANITATION_QUOTE2'
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
				name='TXT_KEY_TECH_ECONOMICS_NAME',
				eureka_summary='TXT_KEY_TECH_ECONOMICS_EUREKA',
				eureka_description='TXT_KEY_TECH_ECONOMICS_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_TECH_ECONOMICS_QUOTE1',
					'TXT_KEY_TECH_ECONOMICS_QUOTE2'
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
				name='TXT_KEY_TECH_RIFLING_NAME',
				eureka_summary='TXT_KEY_TECH_RIFLING_EUREKA',
				eureka_description='TXT_KEY_TECH_RIFLING_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_TECH_RIFLING_QUOTE1',
					'TXT_KEY_TECH_RIFLING_QUOTE2'
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
				name='TXT_KEY_TECH_FLIGHT_NAME',
				eureka_summary='TXT_KEY_TECH_FLIGHT_EUREKA',
				eureka_description='TXT_KEY_TECH_FLIGHT_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_TECH_FLIGHT_QUOTE1',
					'TXT_KEY_TECH_FLIGHT_QUOTE2'
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
				name='TXT_KEY_TECH_REPLACEABLE_PARTS_NAME',
				eureka_summary='TXT_KEY_TECH_REPLACEABLE_PARTS_EUREKA',
				eureka_description='TXT_KEY_TECH_REPLACEABLE_PARTS_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_TECH_REPLACEABLE_PARTS_QUOTE1',
					'TXT_KEY_TECH_REPLACEABLE_PARTS_QUOTE2'
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
				name='TXT_KEY_TECH_STEEL_NAME',
				eureka_summary='TXT_KEY_TECH_STEEL_EUREKA',
				eureka_description='TXT_KEY_TECH_STEEL_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_TECH_STEEL_QUOTE1',
					'TXT_KEY_TECH_STEEL_QUOTE2'
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
				name='TXT_KEY_TECH_REFINING_NAME',
				eureka_summary='TXT_KEY_TECH_REFINING_EUREKA',
				eureka_description='TXT_KEY_TECH_REFINING_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_TECH_REFINING_QUOTE1'
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
				name='TXT_KEY_TECH_ELECTRICITY_NAME',
				eureka_summary='TXT_KEY_TECH_ELECTRICITY_EUREKA',
				eureka_description='TXT_KEY_TECH_ELECTRICITY_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_TECH_ELECTRICITY_QUOTE1',
					'TXT_KEY_TECH_ELECTRICITY_QUOTE2'
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
				name='TXT_KEY_TECH_RADIO_NAME',
				eureka_summary='TXT_KEY_TECH_RADIO_EUREKA',
				eureka_description='TXT_KEY_TECH_RADIO_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_TECH_RADIO_QUOTE1',
					'TXT_KEY_TECH_RADIO_QUOTE2'
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
				name='TXT_KEY_TECH_CHEMISTRY_NAME',
				eureka_summary='TXT_KEY_TECH_CHEMISTRY_EUREKA',
				eureka_description='TXT_KEY_TECH_CHEMISTRY_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_TECH_CHEMISTRY_QUOTE1',
					'TXT_KEY_TECH_CHEMISTRY_QUOTE2'
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
				name='TXT_KEY_TECH_COMBUSTION_NAME',
				eureka_summary='TXT_KEY_TECH_COMBUSTION_EUREKA',
				eureka_description='TXT_KEY_TECH_COMBUSTION_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_TECH_COMBUSTION_QUOTE1',
					'TXT_KEY_TECH_COMBUSTION_QUOTE2'
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
				name='TXT_KEY_TECH_ADVANCED_FLIGHT_NAME',
				eureka_summary='TXT_KEY_TECH_ADVANCED_FLIGHT_EUREKA',
				eureka_description='TXT_KEY_TECH_ADVANCED_FLIGHT_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_TECH_ADVANCED_FLIGHT_QUOTE1',
					'TXT_KEY_TECH_ADVANCED_FLIGHT_QUOTE2'
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
				name='TXT_KEY_TECH_ROCKETRY_NAME',
				eureka_summary='TXT_KEY_TECH_ROCKETRY_EUREKA',
				eureka_description='TXT_KEY_TECH_ROCKETRY_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_TECH_ROCKETRY_QUOTE1',
					'TXT_KEY_TECH_ROCKETRY_QUOTE2'
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
				name='TXT_KEY_TECH_ADVANCED_BALLISTICS_NAME',
				eureka_summary='TXT_KEY_TECH_ADVANCED_BALLISTICS_EUREKA',
				eureka_description='TXT_KEY_TECH_ADVANCED_BALLISTICS_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_TECH_ADVANCED_BALLISTICS_QUOTE1',
					'TXT_KEY_TECH_ADVANCED_BALLISTICS_QUOTE2'
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
				name='TXT_KEY_TECH_COMBINED_ARMS_NAME',
				eureka_summary='TXT_KEY_TECH_COMBINED_ARMS_EUREKA',
				eureka_description='TXT_KEY_TECH_COMBINED_ARMS_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_TECH_COMBINED_ARMS_QUOTE1',
					'TXT_KEY_TECH_COMBINED_ARMS_QUOTE2'
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
				name='TXT_KEY_TECH_PLASTICS_NAME',
				eureka_summary='TXT_KEY_TECH_PLASTICS_EUREKA',
				eureka_description='TXT_KEY_TECH_PLASTICS_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_TECH_PLASTICS_QUOTE1',
					'TXT_KEY_TECH_PLASTICS_QUOTE2'
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
				name='TXT_KEY_TECH_COMPUTERS_NAME',
				eureka_summary='TXT_KEY_TECH_COMPUTERS_EUREKA',
				eureka_description='TXT_KEY_TECH_COMPUTERS_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_TECH_COMPUTERS_QUOTE1',
					'TXT_KEY_TECH_COMPUTERS_QUOTE2'
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
				name='TXT_KEY_TECH_NUCLEAR_FISSION_NAME',
				eureka_summary='TXT_KEY_TECH_NUCLEAR_FISSION_EUREKA',
				eureka_description='TXT_KEY_TECH_NUCLEAR_FISSION_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_TECH_NUCLEAR_FISSION_QUOTE1',
					'TXT_KEY_TECH_NUCLEAR_FISSION_QUOTE2'
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
				name='TXT_KEY_TECH_SYNTHETIC_MATERIALS_NAME',
				eureka_summary='TXT_KEY_TECH_SYNTHETIC_MATERIALS_EUREKA',
				eureka_description='TXT_KEY_TECH_SYNTHETIC_MATERIALS_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_TECH_SYNTHETIC_MATERIALS_QUOTE1',
					'TXT_KEY_TECH_SYNTHETIC_MATERIALS_QUOTE2'
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
				name='TXT_KEY_TECH_TELECOMMUNICATIONS_NAME',
				eureka_summary='TXT_KEY_TECH_TELECOMMUNICATIONS_EUREKA',
				eureka_description='TXT_KEY_TECH_TELECOMMUNICATIONS_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_TECH_TELECOMMUNICATIONS_QUOTE1',
					'TXT_KEY_TECH_TELECOMMUNICATIONS_QUOTE2'
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
				name='TXT_KEY_TECH_SATELLITES_NAME',
				eureka_summary='TXT_KEY_TECH_SATELLITES_EUREKA',
				eureka_description='TXT_KEY_TECH_SATELLITES_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_TECH_SATELLITES_QUOTE1',
					'TXT_KEY_TECH_SATELLITES_QUOTE2'
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
				name='TXT_KEY_TECH_GUIDANCE_SYSTEMS_NAME',
				eureka_summary='TXT_KEY_TECH_GUIDANCE_SYSTEMS_EUREKA',
				eureka_description='TXT_KEY_TECH_GUIDANCE_SYSTEMS_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_TECH_GUIDANCE_SYSTEMS_QUOTE1',
					'TXT_KEY_TECH_GUIDANCE_SYSTEMS_QUOTE2'
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
				name='TXT_KEY_TECH_LASERS_NAME',
				eureka_summary='TXT_KEY_TECH_LASERS_EUREKA',
				eureka_description='TXT_KEY_TECH_LASERS_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_TECH_LASERS_QUOTE1',
					'TXT_KEY_TECH_LASERS_QUOTE2'
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
				name='TXT_KEY_TECH_COMPOSITES_NAME',
				eureka_summary='TXT_KEY_TECH_COMPOSITES_EUREKA',
				eureka_description='TXT_KEY_TECH_COMPOSITES_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_TECH_COMPOSITES_QUOTE1',
					'TXT_KEY_TECH_COMPOSITES_QUOTE2'
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
				name='TXT_KEY_TECH_STEALTH_TECHNOLOGY_NAME',
				eureka_summary='TXT_KEY_TECH_STEALTH_TECHNOLOGY_EUREKA',
				eureka_description='TXT_KEY_TECH_STEALTH_TECHNOLOGY_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_TECH_STEALTH_TECHNOLOGY_QUOTE1',
					'TXT_KEY_TECH_STEALTH_TECHNOLOGY_QUOTE2'
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
				name='TXT_KEY_TECH_ROBOTICS_NAME',
				eureka_summary='TXT_KEY_TECH_ROBOTICS_EUREKA',
				eureka_description='TXT_KEY_TECH_ROBOTICS_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_TECH_ROBOTICS_QUOTE1',
					'TXT_KEY_TECH_ROBOTICS_QUOTE2'
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
				name='TXT_KEY_TECH_NUCLEAR_FUSION_NAME',
				eureka_summary='TXT_KEY_TECH_NUCLEAR_FUSION_EUREKA',
				eureka_description='TXT_KEY_TECH_NUCLEAR_FUSION_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_TECH_NUCLEAR_FUSION_QUOTE1',
					'TXT_KEY_TECH_NUCLEAR_FUSION_QUOTE2'
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
				name='TXT_KEY_TECH_NANOTECHNOLOGY_NAME',
				eureka_summary='TXT_KEY_TECH_NANOTECHNOLOGY_EUREKA',
				eureka_description='TXT_KEY_TECH_NANOTECHNOLOGY_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_TECH_NANOTECHNOLOGY_QUOTE1',
					'TXT_KEY_TECH_NANOTECHNOLOGY_QUOTE2'
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
				name='TXT_KEY_TECH_FUTURE_TECH_NAME',
				eureka_summary='TXT_KEY_TECH_FUTURE_TECH_EUREKA',
				eureka_description='TXT_KEY_TECH_FUTURE_TECH_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_TECH_FUTURE_TECH_QUOTE1',
					'TXT_KEY_TECH_FUTURE_TECH_QUOTE2'
				],
				era=EraType.future,
				cost=1780,
				required=[TechType.robotics, TechType.nuclearFusion],
				flavors=[]
			)

		raise AttributeError(f'cant get data for tech {self}')

	def __str__(self):
		return self.value