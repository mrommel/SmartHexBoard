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


class TechTypeData:
    def __init__(self, name, eureka_summary, eureka_description, era, cost, required):
        self.name = name
        self.eureka_summary = eureka_summary
        self.eureka_description = eureka_description
        self.era = era
        self.cost = cost
        self.required = required


class TechType:
    pass


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
                era=EraType.ancient,
                cost=0,
                required=[]
            )

        # ancient
        if self == TechType.mining:
            return TechTypeData(
                name='TXT_KEY_TECH_MINING_NAME',
                eureka_summary='TXT_KEY_TECH_MINING_EUREKA',
                eureka_description='TXT_KEY_TECH_MINING_EUREKA_TEXT',
                era=EraType.ancient,
                cost=25,
                required=[]
            )
        elif self == TechType.pottery:
            return TechTypeData(
                name='TXT_KEY_TECH_POTTERY_NAME',
                eureka_summary='TXT_KEY_TECH_POTTERY_EUREKA',
                eureka_description='TXT_KEY_TECH_POTTERY_EUREKA_TEXT',
                era=EraType.ancient,
                cost=25,
                required=[]
            )
        elif self == TechType.animalHusbandry:
            return TechTypeData(
                name='TXT_KEY_TECH_ANIMAL_HUSBANDRY_NAME',
                eureka_summary='TXT_KEY_TECH_ANIMAL_HUSBANDRY_EUREKA',
                eureka_description='TXT_KEY_TECH_ANIMAL_HUSBANDRY_EUREKA_TEXT',
                era=EraType.ancient,
                cost=25,
                required=[]
            )
        elif self == TechType.sailing:
            return TechTypeData(
                name='TXT_KEY_TECH_SAILING_NAME',
                eureka_summary='TXT_KEY_TECH_SAILING_EUREKA',
                eureka_description='TXT_KEY_TECH_SAILING_EUREKA_TEXT',
                era=EraType.ancient,
                cost=50,
                required=[]
            )
        elif self == TechType.astrology:
            return TechTypeData(
                name='TXT_KEY_TECH_ASTROLOGY_NAME',
                eureka_summary='TXT_KEY_TECH_ASTROLOGY_EUREKA',
                eureka_description='TXT_KEY_TECH_ASTROLOGY_EUREKA_TEXT',
                era=EraType.ancient,
                cost=50,
                required=[]
            )
        elif self == TechType.irrigation:
            return TechTypeData(
                name='TXT_KEY_TECH_IRRIGATION_NAME',
                eureka_summary='TXT_KEY_TECH_IRRIGATION_EUREKA',
                eureka_description='TXT_KEY_TECH_IRRIGATION_EUREKA_TEXT',
                era=EraType.ancient,
                cost=50,
                required=[TechType.pottery]
            )
        elif self == TechType.writing:
            return TechTypeData(
                name='TXT_KEY_TECH_WRITING_NAME',
                eureka_summary='TXT_KEY_TECH_WRITING_EUREKA',
                eureka_description='TXT_KEY_TECH_WRITING_EUREKA_TEXT',
                era=EraType.ancient,
                cost=50,
                required=[TechType.pottery]
            )
        elif self == TechType.masonry:
            return TechTypeData(
                name='TXT_KEY_TECH_MASONRY_NAME',
                eureka_summary='TXT_KEY_TECH_MASONRY_EUREKA',
                eureka_description='TXT_KEY_TECH_MASONRY_EUREKA_TEXT',
                era=EraType.ancient,
                cost=80,
                required=[TechType.mining]
            )
        elif self == TechType.archery:
            return TechTypeData(
                name='TXT_KEY_TECH_ARCHERY_NAME',
                eureka_summary='TXT_KEY_TECH_ARCHERY_EUREKA',
                eureka_description='TXT_KEY_TECH_ARCHERY_EUREKA_TEXT',
                era=EraType.ancient,
                cost=50,
                required=[TechType.animalHusbandry]
            )
        elif self == TechType.bronzeWorking:
            return TechTypeData(
                name='TXT_KEY_TECH_BRONZE_WORKING_NAME',
                eureka_summary='TXT_KEY_TECH_BRONZE_WORKING_EUREKA',
                eureka_description='TXT_KEY_TECH_BRONZE_WORKING_EUREKA_TEXT',
                era=EraType.ancient,
                cost=80,
                required=[TechType.mining]
            )
        elif self == TechType.wheel:
            return TechTypeData(
                name='TXT_KEY_TECH_WHEEL_NAME',
                eureka_summary='TXT_KEY_TECH_WHEEL_EUREKA',
                eureka_description='TXT_KEY_TECH_WHEEL_EUREKA_TEXT',
                era=EraType.ancient,
                cost=80,
                required=[TechType.mining]
            )

        # classical
        elif self == TechType.celestialNavigation:
            return TechTypeData(
                name='TXT_KEY_TECH_CELESTIAL_NAVIGATION_NAME',
                eureka_summary='TXT_KEY_TECH_CELESTIAL_NAVIGATION_EUREKA',
                eureka_description='TXT_KEY_TECH_CELESTIAL_NAVIGATION_EUREKA_TEXT',
                era=EraType.classical,
                cost=120,
                required=[TechType.sailing, TechType.astrology]
            )
        elif self == TechType.horsebackRiding:
            return TechTypeData(
                name='TXT_KEY_TECH_HORSEBACK_RIDING_NAME',
                eureka_summary='TXT_KEY_TECH_HORSEBACK_RIDING_EUREKA',
                eureka_description='TXT_KEY_TECH_HORSEBACK_RIDING_EUREKA_TEXT',
                era=EraType.classical,
                cost=120,
                required=[TechType.animalHusbandry]
            )
        elif self == TechType.currency:
            return TechTypeData(
                name='TXT_KEY_TECH_CURRENCY_NAME',
                eureka_summary='TXT_KEY_TECH_CURRENCY_EUREKA',
                eureka_description='TXT_KEY_TECH_CURRENCY_EUREKA_TEXT',
                era=EraType.classical,
                cost=120,
                required=[TechType.writing]
            )
        elif self == TechType.construction:
            return TechTypeData(
                name='TXT_KEY_TECH_CONSTRUCTION_NAME',
                eureka_summary='TXT_KEY_TECH_CONSTRUCTION_EUREKA',
                eureka_description='TXT_KEY_TECH_CONSTRUCTION_EUREKA_TEXT',
                era=EraType.classical,
                cost=200,
                required=[TechType.masonry, TechType.horsebackRiding]
            )
        elif self == TechType.ironWorking:
            return TechTypeData(
                name='TXT_KEY_TECH_IRON_WORKING_NAME',
                eureka_summary='TXT_KEY_TECH_IRON_WORKING_EUREKA',
                eureka_description='TXT_KEY_TECH_IRON_WORKING_EUREKA_TEXT',
                era=EraType.classical,
                cost=120,
                required=[TechType.bronzeWorking]
            )
        elif self == TechType.shipBuilding:
            return TechTypeData(
                name='TXT_KEY_TECH_SHIP_BUILDING_NAME',
                eureka_summary='TXT_KEY_TECH_SHIP_BUILDING_EUREKA',
                eureka_description='TXT_KEY_TECH_SHIP_BUILDING_EUREKA_TEXT',
                era=EraType.classical,
                cost=200,
                required=[TechType.sailing]
            )
        elif self == TechType.mathematics:
            return TechTypeData(
                name='TXT_KEY_TECH_MATHEMATICS_NAME',
                eureka_summary='TXT_KEY_TECH_MATHEMATICS_EUREKA',
                eureka_description='TXT_KEY_TECH_MATHEMATICS_EUREKA_TEXT',
                era=EraType.classical,
                cost=200,
                required=[TechType.currency]
            )
        elif self == TechType.engineering:
            return TechTypeData(
                name='TXT_KEY_TECH_ENGINEERING_NAME',
                eureka_summary='TXT_KEY_TECH_ENGINEERING_EUREKA',
                eureka_description='TXT_KEY_TECH_ENGINEERING_EUREKA_TEXT',
                era=EraType.classical,
                cost=200,
                required=[TechType.wheel]
            )

        # medieval
        elif self == TechType.militaryTactics:
            return TechTypeData(
                name='TXT_KEY_TECH_MILITARY_TACTICS_NAME',
                eureka_summary='TXT_KEY_TECH_MILITARY_TACTICS_EUREKA',
                eureka_description='TXT_KEY_TECH_MILITARY_TACTICS_EUREKA_TEXT',
                era=EraType.medieval,
                cost=275,
                required=[TechType.mathematics]
            )
        elif self == TechType.buttress:
            return TechTypeData(
                name='TXT_KEY_TECH_BUTTRESS_NAME',
                eureka_summary='TXT_KEY_TECH_BUTTRESS_EUREKA',
                eureka_description='TXT_KEY_TECH_BUTTRESS_EUREKA_TEXT',
                era=EraType.medieval,
                cost=300,
                required=[TechType.shipBuilding, TechType.mathematics]
            )
        elif self == TechType.apprenticeship:
            return TechTypeData(
                name='TXT_KEY_TECH_APPRENTICESHIP_NAME',
                eureka_summary='TXT_KEY_TECH_APPRENTICESHIP_EUREKA',
                eureka_description='TXT_KEY_TECH_APPRENTICESHIP_EUREKA_TEXT',
                era=EraType.medieval,
                cost=275,
                required=[TechType.currency, TechType.horsebackRiding]
            )
        elif self == TechType.stirrups:
            return TechTypeData(
                name='TXT_KEY_TECH_STIRRUPS_NAME',
                eureka_summary='TXT_KEY_TECH_STIRRUPS_EUREKA',
                eureka_description='TXT_KEY_TECH_STIRRUPS_EUREKA_TEXT',
                era=EraType.medieval,
                cost=360,
                required=[TechType.horsebackRiding]
            )
        elif self == TechType.machinery:
            return TechTypeData(
                name='TXT_KEY_TECH_MACHINERY_NAME',
                eureka_summary='TXT_KEY_TECH_MACHINERY_EUREKA',
                eureka_description='TXT_KEY_TECH_MACHINERY_EUREKA_TEXT',
                era=EraType.medieval,
                cost=275,
                required=[TechType.ironWorking, TechType.engineering]
            )
        elif self == TechType.education:
            return TechTypeData(
                name='TXT_KEY_TECH_EDUCATION_NAME',
                eureka_summary='TXT_KEY_TECH_EDUCATION_EUREKA',
                eureka_description='TXT_KEY_TECH_EDUCATION_EUREKA_TEXT',
                era=EraType.medieval,
                cost=335,
                required=[TechType.apprenticeship, TechType.mathematics]
            )
        elif self == TechType.militaryEngineering:
            # https://civilization.fandom.com/wiki/Military_Engineering_(Civ6)
            return TechTypeData(
                name='TXT_KEY_TECH_MILITARY_ENGINEERING_NAME',
                eureka_summary='TXT_KEY_TECH_MILITARY_ENGINEERING_EUREKA',
                eureka_description='TXT_KEY_TECH_MILITARY_ENGINEERING_EUREKA_TEXT',
                era=EraType.medieval,
                cost=335,
                required=[TechType.construction]
            )
        elif self == TechType.castles:
            # https://civilization.fandom.com/wiki/Castles_(Civ6)
            return TechTypeData(
                name='TXT_KEY_TECH_CASTLES_NAME',
                eureka_summary='TXT_KEY_TECH_CASTLES_EUREKA',
                eureka_description='TXT_KEY_TECH_CASTLES_EUREKA_TEXT',
                era=EraType.medieval,
                cost=390,
                required=[TechType.construction]
            )

        # renaissance
        elif self == TechType.cartography:
            # https://civilization.fandom.com/wiki/Cartography_(Civ6)
            return TechTypeData(
                name='TXT_KEY_TECH_CARTOGRAPHY_NAME',
                eureka_summary='TXT_KEY_TECH_CARTOGRAPHY_EUREKA',
                eureka_description='TXT_KEY_TECH_CARTOGRAPHY_EUREKA_TEXT',
                era=EraType.renaissance,
                cost=490,
                required=[TechType.shipBuilding]
            )
        elif self == TechType.massProduction:
            # https://civilization.fandom.com/wiki/Mass_Production_(Civ6)
            return TechTypeData(
                name='TXT_KEY_TECH_MASS_PRODUCTION_NAME',
                eureka_summary='TXT_KEY_TECH_MASS_PRODUCTION_NAME',
                eureka_description='TXT_KEY_TECH_MASS_PRODUCTION_EUREKA_TEXT',
                era=EraType.renaissance,
                cost=490,
                required=[TechType.shipBuilding, TechType.education]
            )
        elif self == TechType.banking:
            # https://civilization.fandom.com/wiki/Banking_(Civ6)
            return TechTypeData(
                name='TXT_KEY_TECH_BANKING_NAME',
                eureka_summary='TXT_KEY_TECH_BANKING_NAME',
                eureka_description='TXT_KEY_TECH_BANKING_EUREKA_TEXT',
                era=EraType.renaissance,
                cost=490,
                required=[TechType.education, TechType.apprenticeship, TechType.stirrups]
            )
        elif self == TechType.gunpowder:
            # https://civilization.fandom.com/wiki/Gunpowder_(Civ6)
            return TechTypeData(
                name='TXT_KEY_TECH_GUNPOWDER_NAME',
                eureka_summary='TXT_KEY_TECH_GUNPOWDER_EUREKA',
                eureka_description='TXT_KEY_TECH_GUNPOWDER_EUREKA_TEXT',
                era=EraType.renaissance,
                cost=490,
                required=[TechType.militaryEngineering, TechType.apprenticeship, TechType.stirrups]
            )
        elif self == TechType.printing:
            # https://civilization.fandom.com/wiki/Printing_(Civ6)
            return TechTypeData(
                name='TXT_KEY_TECH_PRINTING_NAME',
                eureka_summary='TXT_KEY_TECH_PRINTING_EUREKA',
                eureka_description='TXT_KEY_TECH_PRINTING_EUREKA_TEXT',
                era=EraType.renaissance,
                cost=490,
                required=[TechType.machinery]
            )
        elif self == TechType.squareRigging:
            # https://civilization.fandom.com/wiki/Square_Rigging_(Civ6)
            return TechTypeData(
                name='TXT_KEY_TECH_SQUARE_RIGGING_NAME',
                eureka_summary='TXT_KEY_TECH_SQUARE_RIGGING_EUREKA',
                eureka_description='TXT_KEY_TECH_SQUARE_RIGGING_EUREKA_TEXT',
                era=EraType.renaissance,
                cost=600,
                required=[TechType.cartography]
            )
        elif self == TechType.astronomy:
            # https://civilization.fandom.com/wiki/Astronomy_(Civ6)
            return TechTypeData(
                name='TXT_KEY_TECH_ASTRONOMY_NAME',
                eureka_summary='TXT_KEY_TECH_ASTRONOMY_NAME',
                eureka_description='TXT_KEY_TECH_ASTRONOMY_NAME',
                era=EraType.renaissance,
                cost=600,
                required=[TechType.education]
            )
        elif self == TechType.metalCasting:
            # https://civilization.fandom.com/wiki/Metal_Casting_(Civ6)
            return TechTypeData(
                name='TXT_KEY_TECH_METAL_CASTING_NAME',
                eureka_summary='TXT_KEY_TECH_METAL_CASTING_EUREKA',
                eureka_description='TXT_KEY_TECH_METAL_CASTING_EUREKA_TEXT',
                era=EraType.renaissance,
                cost=660,
                required=[TechType.gunpowder]
            )
        elif self == TechType.siegeTactics:
            # https://civilization.fandom.com/wiki/Siege_Tactics_(Civ6)
            return TechTypeData(
                name='TXT_KEY_TECH_SIEGE_TACTICS_NAME',
                eureka_summary='TXT_KEY_TECH_SIEGE_TACTICS_EUREKA',
                eureka_description='TXT_KEY_TECH_SIEGE_TACTICS_EUREKA_TEXT',
                era=EraType.renaissance,
                cost=660,
                required=[TechType.castles]
            )

        # industrial
        elif self == TechType.industrialization:
            return TechTypeData(
                name='TXT_KEY_TECH_INDUSTRIALIZATION_NAME',
                eureka_summary='TXT_KEY_TECH_INDUSTRIALIZATION_EUREKA',
                eureka_description='TXT_KEY_TECH_INDUSTRIALIZATION_EUREKA_TEXT',
                era=EraType.industrial,
                cost=700,
                required=[""".massProduction, .squareRigging"""]
            )

        # modern
        elif self == TechType.refining:
            return TechTypeData(
                name='TXT_KEY_TECH_REFINING_NAME',
                eureka_summary='TXT_KEY_TECH_REFINING_EUREKA',
                eureka_description='TXT_KEY_TECH_REFINING_EUREKA_TEXT',
                era=EraType.modern,
                cost=1250,
                required=[""".rifling"""]
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
