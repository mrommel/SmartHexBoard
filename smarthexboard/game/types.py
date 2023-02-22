from smarthexboard.map.base import ExtendedEnum
from django.utils.translation import gettext_lazy as _


class EraType(ExtendedEnum):
    # default
    ancient = 'ancient'
    classical = 'classical'

    industrial = 'industrial'
    modern = 'modern'

    def name(self) -> str:
        if self == EraType.ancient:
            return _('TXT_KEY_ERA_ANCIENT')
        elif self == EraType.classical:
            return _('TXT_KEY_ERA_CLASSICAL')

        elif self == EraType.industrial:
            return _('TXT_KEY_ERA_INDUSTRIAL')
        elif self == EraType.modern:
            return _('TXT_KEY_ERA_MODERN')

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

    # renaissance

    # industrial
    industrialization = 'industrialization'

    # modern
    refining = 'refining'

    def name(self) -> str:
        return self._data().name

    def required(self) -> []:
        return self._data().required

    def cost(self) -> int:
        return self._data().cost

    def _data(self):
        if self == TechType.none:
            return TechTypeData(
                'TXT_KEY_TECH_NONE',
                '',
                '',
                EraType.ancient,
                0,
                []
            )

        # ancient
        if self == TechType.mining:
            return TechTypeData(
                'TXT_KEY_TECH_MINING_NAME',
                'TXT_KEY_TECH_MINING_EUREKA',
                'TXT_KEY_TECH_MINING_EUREKA_TEXT',
                EraType.ancient,
                25,
                []
            )
        elif self == TechType.pottery:
            return TechTypeData(
                'TXT_KEY_TECH_POTTERY_NAME',
                'TXT_KEY_TECH_POTTERY_EUREKA',
                'TXT_KEY_TECH_POTTERY_EUREKA_TEXT',
                EraType.ancient,
                25,
                []
            )
        elif self == TechType.animalHusbandry:
            return TechTypeData(
                'TXT_KEY_TECH_ANIMAL_HUSBANDRY_NAME',
                'TXT_KEY_TECH_ANIMAL_HUSBANDRY_EUREKA',
                'TXT_KEY_TECH_ANIMAL_HUSBANDRY_EUREKA_TEXT',
                EraType.ancient,
                25,
                []
            )
        elif self == TechType.sailing:
            return TechTypeData(
                'TXT_KEY_TECH_SAILING_NAME',
                'TXT_KEY_TECH_SAILING_EUREKA',
                'TXT_KEY_TECH_SAILING_EUREKA_TEXT',
                EraType.ancient,
                50,
                []
            )
        elif self == TechType.astrology:
            return TechTypeData(
                'TXT_KEY_TECH_ASTROLOGY_NAME',
                'TXT_KEY_TECH_ASTROLOGY_EUREKA',
                'TXT_KEY_TECH_ASTROLOGY_EUREKA_TEXT',
                EraType.ancient,
                50,
                []
            )
        elif self == TechType.irrigation:
            return TechTypeData(
                'TXT_KEY_TECH_IRRIGATION_NAME',
                'TXT_KEY_TECH_IRRIGATION_EUREKA',
                'TXT_KEY_TECH_IRRIGATION_EUREKA_TEXT',
                EraType.ancient,
                50,
                [TechType.pottery]
            )
        elif self == TechType.writing:
            return TechTypeData(
                'TXT_KEY_TECH_WRITING_NAME',
                'TXT_KEY_TECH_WRITING_EUREKA',
                'TXT_KEY_TECH_WRITING_EUREKA_TEXT',
                EraType.ancient,
                50,
                [TechType.pottery]
            )
        elif self == TechType.masonry:
            return TechTypeData(
                'TXT_KEY_TECH_MASONRY_NAME',
                'TXT_KEY_TECH_MASONRY_EUREKA',
                'TXT_KEY_TECH_MASONRY_EUREKA_TEXT',
                EraType.ancient,
                80,
                [TechType.mining]
            )
        elif self == TechType.archery:
            return TechTypeData(
                'TXT_KEY_TECH_ARCHERY_NAME',
                'TXT_KEY_TECH_ARCHERY_EUREKA',
                'TXT_KEY_TECH_ARCHERY_EUREKA_TEXT',
                EraType.ancient,
                50,
                [TechType.animalHusbandry]
            )
        elif self == TechType.bronzeWorking:
            return TechTypeData(
                'TXT_KEY_TECH_BRONZE_WORKING_NAME',
                'TXT_KEY_TECH_BRONZE_WORKING_EUREKA',
                'TXT_KEY_TECH_BRONZE_WORKING_EUREKA_TEXT',
                EraType.ancient,
                80,
                [TechType.mining]
            )
        elif self == TechType.wheel:
            return TechTypeData(
                'TXT_KEY_TECH_WHEEL_NAME',
                'TXT_KEY_TECH_WHEEL_EUREKA',
                'TXT_KEY_TECH_WHEEL_EUREKA_TEXT',
                EraType.ancient,
                80,
                [TechType.mining]
            )

        # classical
        elif self == TechType.celestialNavigation:
            return TechTypeData(
                'TXT_KEY_TECH_CELESTIAL_NAVIGATION_NAME',
                'TXT_KEY_TECH_CELESTIAL_NAVIGATION_EUREKA',
                'TXT_KEY_TECH_CELESTIAL_NAVIGATION_EUREKA_TEXT',
                EraType.classical,
                120,
                [TechType.sailing, TechType.astrology]
            )
        elif self == TechType.horsebackRiding:
            return TechTypeData(
                'TXT_KEY_TECH_HORSEBACK_RIDING_NAME',
                'TXT_KEY_TECH_HORSEBACK_RIDING_EUREKA',
                'TXT_KEY_TECH_HORSEBACK_RIDING_EUREKA_TEXT',
                EraType.classical,
                120,
                [TechType.animalHusbandry]
            )
        elif self == TechType.currency:
            return TechTypeData(
                'TXT_KEY_TECH_CURRENCY_NAME',
                'TXT_KEY_TECH_CURRENCY_EUREKA',
                'TXT_KEY_TECH_CURRENCY_EUREKA_TEXT',
                EraType.classical,
                120,
                [TechType.writing]
            )
        elif self == TechType.construction:
            return TechTypeData(
                'TXT_KEY_TECH_CONSTRUCTION_NAME',
                'TXT_KEY_TECH_CONSTRUCTION_EUREKA',
                'TXT_KEY_TECH_CONSTRUCTION_EUREKA_TEXT',
                EraType.classical,
                200,
                [TechType.masonry, TechType.horsebackRiding]
            )
        elif self == TechType.ironWorking:
            return TechTypeData(
                'TXT_KEY_TECH_IRON_WORKING_NAME',
                'TXT_KEY_TECH_IRON_WORKING_EUREKA',
                'TXT_KEY_TECH_IRON_WORKING_EUREKA_TEXT',
                EraType.classical,
                120,
                [TechType.bronzeWorking]
            )
        elif self == TechType.shipBuilding:
            return TechTypeData(
                'TXT_KEY_TECH_SHIP_BUILDING_NAME',
                'TXT_KEY_TECH_SHIP_BUILDING_EUREKA',
                'TXT_KEY_TECH_SHIP_BUILDING_EUREKA_TEXT',
                EraType.classical,
                200,
                [TechType.sailing]
            )
        elif self == TechType.mathematics:
            return TechTypeData(
                'TXT_KEY_TECH_MATHEMATICS_NAME',
                'TXT_KEY_TECH_MATHEMATICS_EUREKA',
                'TXT_KEY_TECH_MATHEMATICS_EUREKA_TEXT',
                EraType.classical,
                200,
                [TechType.currency]
            )
        elif self == TechType.engineering:
            return TechTypeData(
                'TXT_KEY_TECH_ENGINEERING_NAME',
                'TXT_KEY_TECH_ENGINEERING_EUREKA',
                'TXT_KEY_TECH_ENGINEERING_EUREKA_TEXT',
                EraType.classical,
                200,
                [TechType.wheel]
            )

        # industrial
        elif self == TechType.industrialization:
            return TechTypeData(
                'TXT_KEY_TECH_INDUSTRIALIZATION_NAME',
                'TXT_KEY_TECH_INDUSTRIALIZATION_EUREKA',
                'TXT_KEY_TECH_INDUSTRIALIZATION_EUREKA_TEXT',
                EraType.industrial,
                700,
                [""".massProduction, .squareRigging"""]
            )

        # modern
        elif self == TechType.refining:
            return TechTypeData(
                'TXT_KEY_TECH_REFINING_NAME',
                'TXT_KEY_TECH_REFINING_EUREKA',
                'TXT_KEY_TECH_REFINING_EUREKA_TEXT',
                EraType.modern,
                1250,
                [""".rifling"""]
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

    def name(self) -> str:
        return self._data().name

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
