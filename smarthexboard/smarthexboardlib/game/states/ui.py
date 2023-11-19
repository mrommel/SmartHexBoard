from typing import Optional

from smarthexboard.smarthexboardlib.core.base import ExtendedEnum
from smarthexboard.smarthexboardlib.game.civilizations import LeaderType
from smarthexboard.smarthexboardlib.game.types import TechType, CivicType
from smarthexboard.smarthexboardlib.game.wonders import WonderType
from smarthexboard.smarthexboardlib.map.base import HexPoint


class CityAnimationType(ExtendedEnum):
	rangeAttack = 'rangeAttack'


class TooltipType(ExtendedEnum):
	unitDestroyedEnemyUnit = 'unitDestroyedEnemyUnit'
	barbarianCampCleared = 'barbarianCampCleared'


class ScreenType(ExtendedEnum):
	diplomatic = 'diplomatic'
	victory = 'victory'


class PopupType(ExtendedEnum):
	tutorialBadUnitAttack = 'tutorialBadUnitAttack'
	tutorialCityAttack = 'tutorialCityAttack'
	inspirationTriggered = 'inspirationTriggered'
	eurekaTriggered = 'eurekaTriggered'
	wonderBuilt = 'wonderBuilt'
	lostOwnCapital = 'lostOwnCapital'
	lostCapital = 'lostCapital'
	religionNeedNewAutomaticFaithSelection = 'religionNeedNewAutomaticFaithSelection'
	eraEntered = 'eraEntered'
	techDiscovered = 'techDiscovered'
	civicDiscovered = 'civicDiscovered'
	religionCanBuyMissionary = 'religionCanBuyMissionary'
	cityRevolted = 'cityRevolted'
	foreignCityRevolted = 'foreignCityRevolted'


class Interface:
	def __init__(self):
		pass

	def updateCity(self, city):
		pass

	def removeCity(self, city):
		pass

	def updatePlayer(self, player):
		pass

	def isShown(self, screenType) -> bool:
		return False

	def refreshTile(self, tile):
		pass

	def refreshUnit(self, unit):
		pass

	def hideUnit(self, unit, location):
		pass

	def showUnit(self, unit, location):
		pass

	def animateUnit(self, unit, animation, startPoint: [HexPoint]=None, endPoint: [HexPoint]=None):
		pass

	def animateCity(self, unit, animation, startPoint: [HexPoint]=None, endPoint: [HexPoint]=None):
		pass

	def selectTech(self, tech):
		pass

	def selectCivic(self, civic):
		pass

	def enterCity(self, unit, point):
		pass

	def leaveCity(self, unit, point):
		pass

	def addNotification(self, notification):
		pass

	def removeNotification(self, notification):
		pass

	def showScreen(self, screen: ScreenType, city=None, other=None, data=None):
		pass

	def showPopup(self, popup: PopupType, tech: Optional[TechType] = None, civic: Optional[CivicType] = None,
	              wonder: Optional[WonderType] = None, leader: Optional[LeaderType] = None):
		pass

	def updateGameData(self):
		pass
