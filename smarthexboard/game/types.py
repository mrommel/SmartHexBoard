from smarthexboard.map.base import ExtendedEnum
from django.utils.translation import gettext_lazy as _


class EraType(ExtendedEnum):
    # default
    ancient = 'ancient'
    classical = 'classical'
    medieval = 'medieval'
    renaissance = 'renaissance'
    industrial = 'industrial'
    modern = 'modern'
    atomic = 'atomic'
    information = 'information'

    def name(self) -> str:
        if self == EraType.ancient:
            return _('TXT_KEY_ERA_ANCIENT')
        elif self == EraType.classical:
            return _('TXT_KEY_ERA_CLASSICAL')
        elif self == EraType.medieval:
            return _('TXT_KEY_ERA_MEDIEVAL')
        elif self == EraType.renaissance:
            return _('TXT_KEY_ERA_RENAISSANCE')
        elif self == EraType.industrial:
            return _('TXT_KEY_ERA_INDUSTRIAL')
        elif self == EraType.modern:
            return _('TXT_KEY_ERA_MODERN')
        elif self == EraType.atomic:
            return _('TXT_KEY_ERA_ATOMIC')
        elif self == EraType.information:
            return _('TXT_KEY_ERA_INFORMATION')

        raise AttributeError(f'cant get name of {self}')


class FlavorType(ExtendedEnum):
    # default
    none = 'none'

    production = 'production'
    tileImprovement = 'tileImprovement'
    mobile = 'mobile'
    growth = 'growth'
    naval = 'naval'
    navalTileImprovement = 'navalTileImprovement'
    wonder = 'wonder'
    navalRecon = 'navalRecon'
    amenities = 'amenities'
    science = 'science'
    diplomacy = 'diplomacy'
    cityDefense = 'cityDefense'
    ranged = 'ranged'
    offense = 'offense'
    defense = 'defense'
    militaryTraining = 'militaryTraining'
    infrastructure = 'infrastructure'
    gold = 'gold'
    navalGrowth = 'navalGrowth'


class Flavor:
    def __init__(self, flavor: FlavorType, value: int):
        self.flavor = flavor
        self.value = value


class TechType:
    pass


class TechTypeData:
    def __init__(self, name: str, eureka_summary: str, eureka_description: str, quoteTexts: [str], era: EraType, cost: int, required: [TechType], flavors: [Flavor]):
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
            return TechTypeData(
                name='...',
                eureka_summary='...',
                eureka_description='...',
                quoteTexts=[...],
                era=EraType.,
                cost=,
                required=[...],
                flavors=[...]
            )
        elif self == TechType.ballistics:
            return TechTypeData(
                name='...',
                eureka_summary='...',
                eureka_description='...',
                quoteTexts=[...],
                era=EraType.,
                cost=,
                required=[...],
                flavors=[...]
            )
        elif self == TechType.militaryScience:
            return TechTypeData(
                name='...',
                eureka_summary='...',
                eureka_description='...',
                quoteTexts=[...],
                era=EraType.,
                cost=,
                required=[...],
                flavors=[...]
            )
        elif self == TechType.steamPower:
            return TechTypeData(
                name='...',
                eureka_summary='...',
                eureka_description='...',
                quoteTexts=[...],
                era=EraType.,
                cost=,
                required=[...],
                flavors=[...]
            )
        elif self == TechType.sanitation:
            return TechTypeData(
                name='...',
                eureka_summary='...',
                eureka_description='...',
                quoteTexts=[...],
                era=EraType.,
                cost=,
                required=[...],
                flavors=[...]
            )
        elif self == TechType.economics:
            return TechTypeData(
                name='...',
                eureka_summary='...',
                eureka_description='...',
                quoteTexts=[...],
                era=EraType.,
                cost=,
                required=[...],
                flavors=[...]
            )
        elif self == TechType.rifling:
            return TechTypeData(
                name='...',
                eureka_summary='...',
                eureka_description='...',
                quoteTexts=[...],
                era=EraType.,
                cost=,
                required=[...],
                flavors=[...]
            )

        # modern
        elif self == TechType.flight:
            return TechTypeData(
                name='...',
                eureka_summary='...',
                eureka_description='...',
                quoteTexts=[...],
                era=EraType.,
                cost=,
                required=[...],
                flavors=[...]
            )
        elif self == TechType.replaceableParts:
            return TechTypeData(
                name='...',
                eureka_summary='...',
                eureka_description='...',
                quoteTexts=[...],
                era=EraType.,
                cost=,
                required=[...],
                flavors=[...]
            )
        elif self == TechType.steel:
            return TechTypeData(
                name='...',
                eureka_summary='...',
                eureka_description='...',
                quoteTexts=[...],
                era=EraType.,
                cost=,
                required=[...],
                flavors=[...]
            )
        elif self == TechType.refining:
            return TechTypeData(
                name='TXT_KEY_TECH_REFINING_NAME',
                eureka_summary='TXT_KEY_TECH_REFINING_EUREKA',
                eureka_description='TXT_KEY_TECH_REFINING_EUREKA_TEXT',
                quoteTexts=[
                    ...
                ],
                era=EraType.modern,
                cost=1250,
                required=[TechType.rifling],
                flavors=[
                    ...
                ]
            )
        elif self == TechType.electricity:
            return TechTypeData(
                name='...',
                eureka_summary='...',
                eureka_description='...',
                quoteTexts=[...],
                era=EraType.,
                cost=,
                required=[...],
                flavors=[...]
            )
        elif self == TechType.radio:
            return TechTypeData(
                name='...',
                eureka_summary='...',
                eureka_description='...',
                quoteTexts=[...],
                era=EraType.,
                cost=,
                required=[...],
                flavors=[...]
            )
        elif self == TechType.chemistry:
            return TechTypeData(
                name='...',
                eureka_summary='...',
                eureka_description='...',
                quoteTexts=[...],
                era=EraType.,
                cost=,
                required=[...],
                flavors=[...]
            )
        elif self == TechType.combustion:
            return TechTypeData(
                name='...',
                eureka_summary='...',
                eureka_description='...',
                quoteTexts=[...],
                era=EraType.,
                cost=,
                required=[...],
                flavors=[...]
            )

        # atomic
        elif self == TechType.advancedFlight:
            return TechTypeData(
                name='...',
                eureka_summary='...',
                eureka_description='...',
                quoteTexts=[...],
                era=EraType.,
                cost=,
                required=[...],
                flavors=[...]
            )
        elif self == TechType.rocketry:
            return TechTypeData(
                name='...',
                eureka_summary='...',
                eureka_description='...',
                quoteTexts=[...],
                era=EraType.,
                cost=,
                required=[...],
                flavors=[...]
            )
        elif self == TechType.advancedBallistics:
            return TechTypeData(
                name='...',
                eureka_summary='...',
                eureka_description='...',
                quoteTexts=[...],
                era=EraType.,
                cost=,
                required=[...],
                flavors=[...]
            )
        elif self == TechType.combinedArms:
            return TechTypeData(
                name='...',
                eureka_summary='...',
                eureka_description='...',
                quoteTexts=[...],
                era=EraType.,
                cost=,
                required=[...],
                flavors=[...]
            )
        elif self == TechType.plastics:
            return TechTypeData(
                name='...',
                eureka_summary='...',
                eureka_description='...',
                quoteTexts=[...],
                era=EraType.,
                cost=,
                required=[...],
                flavors=[...]
            )
        elif self == TechType.computers:
            return TechTypeData(
                name='...',
                eureka_summary='...',
                eureka_description='...',
                quoteTexts=[...],
                era=EraType.,
                cost=,
                required=[...],
                flavors=[...]
            )
        elif self == TechType.nuclearFission:
            return TechTypeData(
                name='...',
                eureka_summary='...',
                eureka_description='...',
                quoteTexts=[...],
                era=EraType.,
                cost=,
                required=[...],
                flavors=[...]
            )
        elif self == TechType.syntheticMaterials:
            return TechTypeData(
                name='...',
                eureka_summary='...',
                eureka_description='...',
                quoteTexts=[...],
                era=EraType.,
                cost=,
                required=[...],
                flavors=[...]
            )

        # information
        elif self == TechType.telecommunications:
            return TechTypeData(
                name='...',
                eureka_summary='...',
                eureka_description='...',
                quoteTexts=[...],
                era=EraType.,
                cost=,
                required=[...],
                flavors=[...]
            )
        elif self == TechType.satellites:
            return TechTypeData(
                name='...',
                eureka_summary='...',
                eureka_description='...',
                quoteTexts=[...],
                era=EraType.,
                cost=,
                required=[...],
                flavors=[...]
            )
        elif self == TechType.guidanceSystems:
            return TechTypeData(
                name='...',
                eureka_summary='...',
                eureka_description='...',
                quoteTexts=[...],
                era=EraType.,
                cost=,
                required=[...],
                flavors=[...]
            )
        elif self == TechType.lasers:
            return TechTypeData(
                name='...',
                eureka_summary='...',
                eureka_description='...',
                quoteTexts=[...],
                era=EraType.,
                cost=,
                required=[...],
                flavors=[...]
            )
        elif self == TechType.composites:
            return TechTypeData(
                name='...',
                eureka_summary='...',
                eureka_description='...',
                quoteTexts=[...],
                era=EraType.,
                cost=,
                required=[...],
                flavors=[...]
            )
        elif self == TechType.stealthTechnology:
            return TechTypeData(
                name='...',
                eureka_summary='...',
                eureka_description='...',
                quoteTexts=[...],
                era=EraType.,
                cost=,
                required=[...],
                flavors=[...]
            )
        elif self == TechType.robotics:
            return TechTypeData(
                name='...',
                eureka_summary='...',
                eureka_description='...',
                quoteTexts=[...],
                era=EraType.,
                cost=,
                required=[...],
                flavors=[...]
            )
        elif self == TechType.nuclearFusion:
            return TechTypeData(
                name='...',
                eureka_summary='...',
                eureka_description='...',
                quoteTexts=[...],
                era=EraType.,
                cost=,
                required=[...],
                flavors=[...]
            )
        elif self == TechType.nanotechnology:
            return TechTypeData(
                name='...',
                eureka_summary='...',
                eureka_description='...',
                quoteTexts=[...],
                era=EraType.,
                cost=,
                required=[...],
                flavors=[...]
            )

        elif self == TechType.futureTech:
            return TechTypeData(
                name='...',
                eureka_summary='...',
                eureka_description='...',
                quoteTexts=[...],
                era=EraType.,
                cost=,
                required=[...],
                flavors=[...]
            )

        raise AttributeError(f'cant get data for tech {self}')

    def __str__(self):
        return self.value


class CivicTypeData:
    def __init__(self, name, inspiration_summary, inspiration_description, era, cost, required):
        self.name = name
        self.inspiration_summary = inspiration_summary
        self.inspiration_description = inspiration_description
        self.era = era
        self.cost = cost
        self.required = required


class CivicType:
    pass


class CivicType(ExtendedEnum):
    # default
    none = 'none', _('none')

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
    # Near Future Governance
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

    def name(self) -> str:
        return _(self._data().name)

    def required(self) -> []:
        return self._data().required

    def cost(self) -> int:
        return self._data().cost

    def _data(self):
        if self == CivicType.none:
            return CivicTypeData(
                'TXT_KEY_CIVIC_NONE',
                '',
                '',
                EraType.ancient,
                0,
                []
            )

        # ancient

        raise AttributeError(f'cant get data for civic {self}')

    def __str__(self):
        return self.value
