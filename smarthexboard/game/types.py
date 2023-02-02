from smarthexboard.map.base import ExtendedEnum


class TechType(ExtendedEnum):
    # default
    none = 'none'

    # ancient
    pottery = 'pottery'
    animalHusbandry = 'animalHusbandry'
    bronzeWorking = 'bronzeWorking'

    industrialization = 'industrialization'
    refining = 'refining'


class CivicType(ExtendedEnum):
    # default
    none = 'none'

    # ancient
