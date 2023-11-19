from smarthexboard.smarthexboardlib.core.base import ExtendedEnum


class VictoryType(ExtendedEnum):
    domination = 'domination'
    cultural = 'cultural'
    science = 'science'
    diplomatic = 'diplomatic'
    religious = 'religious'
    score = 'score'
    conquest = 'conquest'
