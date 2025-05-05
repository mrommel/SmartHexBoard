import logging
import math
import random
from typing import Union, Optional

from smarthexboard.smarthexboardlib.game.ai.baseTypes import MilitaryStrategyType, PlayerStateAllWars
from smarthexboard.smarthexboardlib.game.buildings import BuildingType
from smarthexboard.smarthexboardlib.game.districts import DistrictType
from smarthexboard.smarthexboardlib.game.flavors import Flavors, FlavorType, Flavor
from smarthexboard.smarthexboardlib.game.projects import ProjectType
from smarthexboard.smarthexboardlib.game.types import TechType, CityFocusType
from smarthexboard.smarthexboardlib.game.unitTypes import UnitTaskType, UnitType
from smarthexboard.smarthexboardlib.game.wonders import WonderType
from smarthexboard.smarthexboardlib.map import constants
from smarthexboard.smarthexboardlib.map.base import HexPoint
from smarthexboard.smarthexboardlib.map.improvements import ImprovementType
from smarthexboard.smarthexboardlib.map.types import YieldType, FeatureType, YieldList
from smarthexboard.smarthexboardlib.core.base import ExtendedEnum, InvalidEnumError, WeightedBaseList
from smarthexboard.smarthexboardlib.utils.base import firstOrNone


class CitySpecializationTypeData:
	def __init__(self, name: str, yieldType: Optional[YieldType], isDefault: bool, isWonder: bool,
	             isOperationUnitProvider: bool, mustBeCoastal: bool, flavors: [Flavor]):
		self.name = name
		self.yieldType = yieldType
		self.isDefault = isDefault
		self.isWonder = isWonder
		self.isOperationUnitProvider = isOperationUnitProvider
		self.mustBeCoastal = mustBeCoastal
		self.flavors = flavors


class CitySpecializationType(ExtendedEnum):
	none = 'none'

	settlerPump = 'settlerPump'  # CITYSPECIALIZATION_SETTLER_PUMP
	militaryTraining = 'militaryTraining'  # CITYSPECIALIZATION_MILITARY_TRAINING
	emergencyUnits = 'emergencyUnits'  # CITYSPECIALIZATION_EMERGENCY_UNITS
	militaryNaval = 'militaryNaval'  # CITYSPECIALIZATION_MILITARY_NAVAL
	productionWonder = 'productionWonder'  # CITYSPECIALIZATION_PRODUCTION_WONDER
	# CITYSPECIALIZATION_PRODUCTION_SPACESHIP
	commerce = 'commerce'  # CITYSPECIALIZATION_COMMERCE
	science = 'science'  # CITYSPECIALIZATION_SCIENCE
	generalEconomic = 'generalEconomic'  # CITYSPECIALIZATION_GENERAL_ECONOMIC

	def name(self) -> str:
		return self._data().name

	def yieldType(self) -> YieldType:
		return self._data().yieldType

	def isWonder(self) -> bool:
		return self._data().isWonder

	def isDefault(self) -> bool:
		return self._data().isDefault

	def mustBeCoastal(self) -> bool:
		return self._data().mustBeCoastal

	def _data(self) -> CitySpecializationTypeData:
		if self == CitySpecializationType.none:
			return CitySpecializationTypeData(
				name="None",
				yieldType=None, 
				isDefault=False, 
				isWonder=False, 
				isOperationUnitProvider=False, 
				mustBeCoastal=False, 
				flavors=[]
			)
		elif self == CitySpecializationType.settlerPump:
			return CitySpecializationTypeData(
				name="settlerPump",
				yieldType=YieldType.food, 
				isDefault=False, 
				isWonder=False, 
				isOperationUnitProvider=False, 
				mustBeCoastal=False, 
				flavors=[
					Flavor(FlavorType.expansion, value=30),
					Flavor(FlavorType.production, value=-4),
					Flavor(FlavorType.gold, value=-4),
					Flavor(FlavorType.science, value=-4),
					Flavor(FlavorType.mobile, value=-2),
					Flavor(FlavorType.navalGrowth, value=-5),
					Flavor(FlavorType.waterConnection, value=-5),
					Flavor(FlavorType.culture, value=-4),
					Flavor(FlavorType.wonder, value=-6),
					Flavor(FlavorType.offense, value=-4),
					Flavor(FlavorType.defense, value=-4),
					Flavor(FlavorType.ranged, value=-4),
					Flavor(FlavorType.naval, value=-4),
					Flavor(FlavorType.militaryTraining, value=-6)
				]
			)
		elif self == CitySpecializationType.militaryTraining:
			return CitySpecializationTypeData(
				name="militaryTraining",
				yieldType=YieldType.production, 
				isDefault=False, 
				isWonder=False, 
				isOperationUnitProvider=True, 
				mustBeCoastal=False, 
				flavors=[
					Flavor(FlavorType.expansion, value=-4),
					Flavor(FlavorType.growth, value=-4),
					Flavor(FlavorType.production, value=-4),
					Flavor(FlavorType.gold, value=-4),
					Flavor(FlavorType.science, value=-4),
					Flavor(FlavorType.offense, value=20),
					Flavor(FlavorType.defense, value=20),
					Flavor(FlavorType.ranged, value=10),
					Flavor(FlavorType.militaryTraining, value=20),
					Flavor(FlavorType.naval, value=-4)
				]
			)
		elif self == CitySpecializationType.emergencyUnits:
			return CitySpecializationTypeData(
				name="emergencyUnits",
				yieldType=YieldType.production, 
				isDefault=False, 
				isWonder=False, 
				isOperationUnitProvider=True, 
				mustBeCoastal=False, 
				flavors=[
					Flavor(FlavorType.expansion, value=-4),
					Flavor(FlavorType.growth, value=-4),
					Flavor(FlavorType.production, value=-4),
					Flavor(FlavorType.gold, value=-4),
					Flavor(FlavorType.science, value=-4),
					Flavor(FlavorType.defense, value=200),
					Flavor(FlavorType.ranged, value=100),
					Flavor(FlavorType.militaryTraining, value=-4),
					Flavor(FlavorType.naval, value=-25),
					Flavor(FlavorType.recon, value=-25)
				]
			)
		elif self == CitySpecializationType.militaryNaval:
			return CitySpecializationTypeData(
				name="militaryNaval",
				yieldType=YieldType.production, 
				isDefault=False, 
				isWonder=False, 
				isOperationUnitProvider=False, 
				mustBeCoastal=True,
				flavors=[
					Flavor(FlavorType.expansion, value=-4),
					Flavor(FlavorType.growth, value=-4),
					Flavor(FlavorType.production, value=-4),
					Flavor(FlavorType.gold, value=-4),
					Flavor(FlavorType.science, value=-4),
					Flavor(FlavorType.naval, value=200),
					Flavor(FlavorType.navalRecon, value=100),
					Flavor(FlavorType.offense, value=-25),
					Flavor(FlavorType.defense, value=-25),
					Flavor(FlavorType.ranged, value=-25)
				]
			)
		elif self == CitySpecializationType.productionWonder:
			return CitySpecializationTypeData(
				name="productionWonder",
				yieldType=YieldType.production, 
				isDefault=False, 
				isWonder=True,
				isOperationUnitProvider=False, 
				mustBeCoastal=False, 
				flavors=[
					Flavor(FlavorType.expansion, value=-4),
					Flavor(FlavorType.growth, value=-4),
					Flavor(FlavorType.production, value=-4),
					Flavor(FlavorType.gold, value=-4),
					Flavor(FlavorType.science, value=-4),
					Flavor(FlavorType.wonder, value=30),
					Flavor(FlavorType.offense, value=-4),
					Flavor(FlavorType.defense, value=-4),
					Flavor(FlavorType.ranged, value=-4),
					Flavor(FlavorType.naval, value=-4)
				]
			)
		elif self == CitySpecializationType.commerce:
			return CitySpecializationTypeData(
				name="commerce",
				yieldType=YieldType.gold, 
				isDefault=False, 
				isWonder=False, 
				isOperationUnitProvider=False, 
				mustBeCoastal=False, 
				flavors=[
					Flavor(FlavorType.expansion, value=-4),
					Flavor(FlavorType.culture, value=10),
					Flavor(FlavorType.production, value=10),
					Flavor(FlavorType.gold, value=30),
					Flavor(FlavorType.science, value=10),
					Flavor(FlavorType.amenities, value=10),
					Flavor(FlavorType.greatPeople, value=5),
					Flavor(FlavorType.offense, value=-4),
					Flavor(FlavorType.defense, value=-4),
					Flavor(FlavorType.ranged, value=-4),
					Flavor(FlavorType.naval, value=-4),
					Flavor(FlavorType.waterConnection, value=20)
				]
			)
		elif self == CitySpecializationType.science:
			return CitySpecializationTypeData(
				name="science",
				yieldType=YieldType.science, 
				isDefault=False, 
				isWonder=False, 
				isOperationUnitProvider=False, 
				mustBeCoastal=False, 
				flavors=[
					Flavor(FlavorType.expansion, value=-4),
					Flavor(FlavorType.culture, value=10),
					Flavor(FlavorType.production, value=10),
					Flavor(FlavorType.gold, value=10),
					Flavor(FlavorType.science, value=30),
					Flavor(FlavorType.amenities, value=10),
					Flavor(FlavorType.greatPeople, value=5),
					Flavor(FlavorType.offense, value=-4),
					Flavor(FlavorType.defense, value=-4),
					Flavor(FlavorType.ranged, value=-4),
					Flavor(FlavorType.naval, value=-4)
				]
			)

		elif self == CitySpecializationType.generalEconomic:
			return CitySpecializationTypeData(
				name="generalEconomic",
				yieldType=YieldType.production, 
				isDefault=True, 
				isWonder=False, 
				isOperationUnitProvider=False, 
				mustBeCoastal=False, 
				flavors=[
					Flavor(FlavorType.expansion, value=-4),
					Flavor(FlavorType.culture, value=30),
					Flavor(FlavorType.production, value=20),
					Flavor(FlavorType.gold, value=20),
					Flavor(FlavorType.science, value=20),
					Flavor(FlavorType.amenities, value=20),
					Flavor(FlavorType.greatPeople, value=10),
					Flavor(FlavorType.offense, value=-4),
					Flavor(FlavorType.defense, value=-4),
					Flavor(FlavorType.ranged, value=-4),
					Flavor(FlavorType.naval, value=-4)
				]
			)
			
		raise InvalidEnumError(self)


class CityStrategyTypeData:
	def __init__(self, name: str, requiredTech: Optional[TechType], obsoleteTech: Optional[TechType],
				 weightThreshold: int, flavorModifiers: [Flavor], flavorThresholdModifiers: [Flavor],
	             permanent: bool, checkEachTurns: int, minimumAdoptionTurns: int):
		self.name = name
		self.requiredTech = requiredTech
		self.obsoleteTech = obsoleteTech
		self.weightThreshold = weightThreshold
		self.flavorModifiers = flavorModifiers
		self.flavorThresholdModifiers = flavorThresholdModifiers
		self.permanent = permanent
		self.checkEachTurns = checkEachTurns
		self.minimumAdoptionTurns = minimumAdoptionTurns


class CityStrategyType(ExtendedEnum):
	none = 'none'

	tinyCity = 'tinyCity'
	smallCity = 'smallCity'
	mediumCity = 'mediumCity'
	largeCity = 'largeCity'
	landLocked = 'landLocked'

	needTileImprovers = 'needTileImprovers'
	wantTileImprovers = 'wantTileImprovers'
	enoughTileImprovers = 'enoughTileImprovers'
	needNavalGrowth = 'needNavalGrowth'
	needNavalTileImprovement = 'needNavalTileImprovement'
	enoughNavalTileImprovement = 'enoughNavalTileImprovement'
	needImprovementFood = 'needImprovementFood'
	needImprovementProduction = 'needImprovementProduction'
	haveTrainingFacility = 'haveTrainingFacility'
	capitalNeedSettler = 'capitalNeedSettler'
	capitalUnderThreat = 'capitalUnderThreat'
	underBlockade = 'underBlockade'

	coastCity = 'coastCity'
	riverCity = 'riverCity'
	mountainCity = 'mountainCity'
	hillCity = 'hillCity'
	forestCity = 'forestCity'
	jungleCity = 'jungleCity'

	def name(self) -> str:
		return self._data().name

	def requiredTech(self) -> Optional[TechType]:
		return self._data().requiredTech

	def obsoleteTech(self) -> Optional[TechType]:
		return self._data().obsoleteTech

	def permanent(self) -> bool:
		return self._data().permanent

	def checkEachTurns(self) -> int:
		return self._data().checkEachTurns

	def minimumAdoptionTurns(self) -> int:
		return self._data().minimumAdoptionTurns

	def flavorModifiers(self) -> [Flavor]:
		return self._data().flavorModifiers

	def weightThreshold(self) -> int:
		return self._data().weightThreshold

	def weightThresholdModifierFor(self, player) -> int:
		value = 0

		for flavor in list(FlavorType):
			value += player.valueOfPersonalityFlavor(flavor) * self.flavorThresholdModifierFor(flavor)

		return value

	def flavorThresholdModifiers(self) -> [Flavor]:
		return self._data().flavorThresholdModifiers

	def flavorThresholdModifierFor(self, flavorType: FlavorType) -> int:
		modifier = next(filter(lambda modifierItem: modifierItem.flavorType == flavorType, self.flavorThresholdModifiers()), None)
		if modifier is not None:
			return modifier.value

		return 0

	def shouldBeActiveFor(self, city, simulation) -> bool:
		if self == CityStrategyType.none:
			return False

		elif self == CityStrategyType.tinyCity:
			return self._shouldBeActiveTinyCity(city)
		elif self == CityStrategyType.smallCity:
			return self._shouldBeActiveSmallCity(city)
		elif self == CityStrategyType.mediumCity:
			return self._shouldBeActiveMediumCity(city)
		elif self == CityStrategyType.largeCity:
			return self._shouldBeActiveLargeCity(city)
		elif self == CityStrategyType.landLocked:
			return self._shouldBeActiveLandLocked(city, simulation)

		elif self == CityStrategyType.needTileImprovers:
			return self._shouldBeActiveNeedTileImprovers(city, simulation)
		elif self == CityStrategyType.wantTileImprovers:
			return self._shouldBeActiveWantTileImprovers(city, simulation)
		elif self == CityStrategyType.enoughTileImprovers:
			return self._shouldBeActiveEnoughTileImprovers(city, simulation)
		elif self == CityStrategyType.needNavalGrowth:
			return self._shouldBeActiveNeedNavalGrowth(city, simulation)
		elif self == CityStrategyType.needNavalTileImprovement:
			return self._shouldBeActiveNeedNavalTileImprovement(city, simulation)
		elif self == CityStrategyType.enoughNavalTileImprovement:
			return self._shouldBeActiveEnoughNavalTileImprovement(city)
		elif self == CityStrategyType.needImprovementFood:
			return self._shouldBeActiveNeedImprovementFood(city, simulation)
		elif self == CityStrategyType.needImprovementProduction:
			return self._shouldBeActiveNeedImprovementProduction(city, simulation)
		elif self == CityStrategyType.haveTrainingFacility:
			return self._shouldBeActiveHaveTrainingFacility(city)
		elif self == CityStrategyType.capitalNeedSettler:
			return self._shouldBeActiveCapitalNeedSettler(city, simulation)
		elif self == CityStrategyType.capitalUnderThreat:
			return self._shouldBeActiveCapitalUnderThreat(city, simulation)
		elif self == CityStrategyType.underBlockade:
			return self._shouldBeActiveUnderBlockade(city)

		elif self == CityStrategyType.coastCity:
			return self._shouldBeActiveCoastCity(city, simulation)
		elif self == CityStrategyType.riverCity:
			return self._shouldBeActiveRiverCity(city, simulation)
		elif self == CityStrategyType.mountainCity:
			return self._shouldBeActiveMountainCity(city, simulation)
		elif self == CityStrategyType.hillCity:
			return self._shouldBeActiveHillCity(city, simulation)
		elif self == CityStrategyType.forestCity:
			return self._shouldBeActiveForestCity(city, simulation)
		elif self == CityStrategyType.jungleCity:
			return self._shouldBeActiveJungleCity(city, simulation)
	
		raise InvalidEnumError(self)

	def _data(self) -> CityStrategyTypeData:
		if self == CityStrategyType.none:
			return CityStrategyTypeData(
				name='None',
				requiredTech=None,
				obsoleteTech=None,
				weightThreshold=0,
				flavorModifiers=[],
				flavorThresholdModifiers=[],
				permanent=False,
				checkEachTurns=10000,
				minimumAdoptionTurns=0
			)

		elif self == CityStrategyType.tinyCity:
			return CityStrategyTypeData(
				name='tinyCity',
				requiredTech=None,
				obsoleteTech=None,
				weightThreshold=0,
				flavorModifiers=[],
				flavorThresholdModifiers=[],
				permanent=False,
				checkEachTurns=5,
				minimumAdoptionTurns=5
			)
		elif self == CityStrategyType.smallCity:
			return CityStrategyTypeData(
				name='smallCity',
				requiredTech=None,
				obsoleteTech=None,
				weightThreshold=0,
				flavorModifiers=[],
				flavorThresholdModifiers=[],
				permanent=False,
				checkEachTurns=5,
				minimumAdoptionTurns=5
			)
		elif self == CityStrategyType.mediumCity:
			return CityStrategyTypeData(
				name='mediumCity',
				requiredTech=None,
				obsoleteTech=None,
				weightThreshold=0,
				flavorModifiers=[],
				flavorThresholdModifiers=[],
				permanent=False,
				checkEachTurns=5,
				minimumAdoptionTurns=5
			)
		elif self == CityStrategyType.largeCity:
			return CityStrategyTypeData(
				name='largeCity',
				requiredTech=None,
				obsoleteTech=None,
				weightThreshold=0,
				flavorModifiers=[],
				flavorThresholdModifiers=[],
				permanent=False,
				checkEachTurns=5,
				minimumAdoptionTurns=5
			)
		elif self == CityStrategyType.landLocked:
			return CityStrategyTypeData(
				name='landLocked',
				requiredTech=None,
				obsoleteTech=None,
				weightThreshold=0,
				flavorModifiers=[],
				flavorThresholdModifiers=[],
				permanent=True,
				checkEachTurns=-1,
				minimumAdoptionTurns=-1
			)

		elif self == CityStrategyType.needTileImprovers:
			return CityStrategyTypeData(
				name='needTileImprovers',
				requiredTech=None,
				obsoleteTech=None,
				weightThreshold=0,
				flavorModifiers=[],
				flavorThresholdModifiers=[],
				permanent=False,
				checkEachTurns=2,
				minimumAdoptionTurns=2
			)
		elif self == CityStrategyType.wantTileImprovers:
			return CityStrategyTypeData(
				name='wantTileImprovers',
				requiredTech=None,
				obsoleteTech=None,
				weightThreshold=0,
				flavorModifiers=[],
				flavorThresholdModifiers=[],
				permanent=False,
				checkEachTurns=2,
				minimumAdoptionTurns=2
			)
		elif self == CityStrategyType.enoughTileImprovers:
			return CityStrategyTypeData(
				name='enoughTileImprovers',
				requiredTech=None,
				obsoleteTech=None,
				weightThreshold=0,
				flavorModifiers=[],
				flavorThresholdModifiers=[],
				permanent=False,
				checkEachTurns=5,
				minimumAdoptionTurns=10
			)
		elif self == CityStrategyType.needNavalGrowth:
			return CityStrategyTypeData(
				name='needNavalGrowth',
				requiredTech=None,
				obsoleteTech=None,
				weightThreshold=0,
				flavorModifiers=[],
				flavorThresholdModifiers=[],
				permanent=False,
				checkEachTurns=5,
				minimumAdoptionTurns=10
			)
		elif self == CityStrategyType.needNavalTileImprovement:
			return CityStrategyTypeData(
				name='needNavalTileImprovement',
				requiredTech=None,
				obsoleteTech=None,
				weightThreshold=0,
				flavorModifiers=[],
				flavorThresholdModifiers=[],
				permanent=False,
				checkEachTurns=1,
				minimumAdoptionTurns=2
			)
		elif self == CityStrategyType.enoughNavalTileImprovement:
			return CityStrategyTypeData(
				name='enoughNavalTileImprovement',
				requiredTech=None,
				obsoleteTech=None,
				weightThreshold=0,
				flavorModifiers=[],
				flavorThresholdModifiers=[],
				permanent=False,
				checkEachTurns=1,
				minimumAdoptionTurns=2
			)
		elif self == CityStrategyType.needImprovementFood:
			return CityStrategyTypeData(
				name='needImprovementFood',
				requiredTech=None,
				obsoleteTech=None,
				weightThreshold=0,
				flavorModifiers=[],
				flavorThresholdModifiers=[],
				permanent=False,
				checkEachTurns=2,
				minimumAdoptionTurns=2
			)
		elif self == CityStrategyType.needImprovementProduction:
			return CityStrategyTypeData(
				name='needImprovementProduction',
				requiredTech=None,
				obsoleteTech=None,
				weightThreshold=0,
				flavorModifiers=[],
				flavorThresholdModifiers=[],
				permanent=False,
				checkEachTurns=2,
				minimumAdoptionTurns=2
			)
		elif self == CityStrategyType.haveTrainingFacility:
			return CityStrategyTypeData(
				name='haveTrainingFacility',
				requiredTech=None,
				obsoleteTech=None,
				weightThreshold=0,
				flavorModifiers=[],
				flavorThresholdModifiers=[],
				permanent=True,
				checkEachTurns=-1,
				minimumAdoptionTurns=-1
			)
		elif self == CityStrategyType.capitalNeedSettler:
			return CityStrategyTypeData(
				name='capitalNeedSettler',
				requiredTech=None,
				obsoleteTech=None,
				weightThreshold=0,
				flavorModifiers=[],
				flavorThresholdModifiers=[],
				permanent=False,
				checkEachTurns=2,
				minimumAdoptionTurns=4
			)
		elif self == CityStrategyType.capitalUnderThreat:
			return CityStrategyTypeData(
				name='capitalUnderThreat',
				requiredTech=None,
				obsoleteTech=None,
				weightThreshold=0,
				flavorModifiers=[],
				flavorThresholdModifiers=[],
				permanent=False,
				checkEachTurns=2,
				minimumAdoptionTurns=2
			)
		elif self == CityStrategyType.underBlockade:
			return CityStrategyTypeData(
				name='underBlockade',
				requiredTech=None,
				obsoleteTech=None,
				weightThreshold=0,
				flavorModifiers=[],
				flavorThresholdModifiers=[],
				permanent=False,
				checkEachTurns=2,
				minimumAdoptionTurns=2
			)

		elif self == CityStrategyType.coastCity:
			return CityStrategyTypeData(
				name='coastCity',
				requiredTech=None,
				obsoleteTech=None,
				weightThreshold=0,
				flavorModifiers=[],
				flavorThresholdModifiers=[],
				permanent=True,
				checkEachTurns=2,
				minimumAdoptionTurns=2
			)
		elif self == CityStrategyType.riverCity:
			return CityStrategyTypeData(
				name='riverCity',
				requiredTech=None,
				obsoleteTech=None,
				weightThreshold=0,
				flavorModifiers=[],
				flavorThresholdModifiers=[],
				permanent=True,
				checkEachTurns=2,
				minimumAdoptionTurns=2
			)
		elif self == CityStrategyType.mountainCity:
			return CityStrategyTypeData(
				name='mountainCity',
				requiredTech=None,
				obsoleteTech=None,
				weightThreshold=0,
				flavorModifiers=[],
				flavorThresholdModifiers=[],
				permanent=True,
				checkEachTurns=2,
				minimumAdoptionTurns=2
			)
		elif self == CityStrategyType.hillCity:
			return CityStrategyTypeData(
				name='hillCity',
				requiredTech=None,
				obsoleteTech=None,
				weightThreshold=0,
				flavorModifiers=[],
				flavorThresholdModifiers=[],
				permanent=True,
				checkEachTurns=2,
				minimumAdoptionTurns=2
			)
		elif self == CityStrategyType.forestCity:
			return CityStrategyTypeData(
				name='forestCity',
				requiredTech=None,
				obsoleteTech=None,
				weightThreshold=0,
				flavorModifiers=[],
				flavorThresholdModifiers=[],
				permanent=False,
				checkEachTurns=2,
				minimumAdoptionTurns=2
			)
		elif self == CityStrategyType.jungleCity:
			return CityStrategyTypeData(
				name='jungleCity',
				requiredTech=None,
				obsoleteTech=None,
				weightThreshold=0,
				flavorModifiers=[],
				flavorThresholdModifiers=[],
				permanent=False,
				checkEachTurns=2,
				minimumAdoptionTurns=2
			)

		raise InvalidEnumError(self)

	def _shouldBeActiveTinyCity(self, city) -> bool:
		""" "Tiny City" City Strategy: If a City is under 2 Population tweak a number of different Flavors"""
		return city.population() == 1

	def _shouldBeActiveSmallCity(self, city) -> bool:
		""" "Small City" City Strategy: If a City is under 3 Population tweak a number of different Flavors"""
		return 2 <= city.population() <= 4

	def _shouldBeActiveMediumCity(self, city) -> bool:
		""" "Medium City" City Strategy: If a City is 8 or above Population boost science"""
		return 5 <= city.population() <= 11

	def _shouldBeActiveLargeCity(self, city) -> bool:
		""" "Large City" City Strategy: If a City is 15 or above, boost science a LOT"""
		return 12 <= city.population()

	def _shouldBeActiveLandLocked(self, city, simulation) -> bool:
		if not simulation.isCoastalAt(city.location):
			return True

		return False

	def _shouldBeActiveNeedTileImprovers(self, city, simulation) -> bool:
		""" "Need Tile Improvers" City Strategy: Do we REALLY need to train some Workers?"""
		currentNumberOfCities = len(simulation.citiesOf(city.player))

		lastTurnBuilderDisbanded = city.player.economicAI.lastTurnBuilderDisbanded()
		if lastTurnBuilderDisbanded is not None:
			if lastTurnBuilderDisbanded > 0 and simulation.currentTurn - lastTurnBuilderDisbanded <= 25:
				return False

		numberOfBuilders = len(list(filter(lambda unit: unit.task() == UnitTaskType.work, simulation.unitsOf(city.player))))
		numberOfCities = max(1, int((currentNumberOfCities * 3) / 4))
		if numberOfBuilders >= numberOfCities:
			return False

		# If we're losing at war, also return false
		if city.player.diplomacyAI.stateOfAllWars == PlayerStateAllWars.losing:
			return False

		# If we're under attack from Barbs and have 1 or fewer Cities and no credible defense then training more
		# Workers will only hurt us
		if currentNumberOfCities <= 1:
			if city.player.militaryAI.adopted(MilitaryStrategyType.eradicateBarbarians) and \
				city.player.militaryAI.adopted(MilitaryStrategyType.empireDefenseCritical):
				return False

		moddedNumberOfBuilders = numberOfBuilders * 67
		moddedNumberOfCities = currentNumberOfCities + len(list(filter(lambda c: c.isFeatureSurrounded(), simulation.citiesOf(city.player))))

		# We have fewer than we think we should, or we have none at all
		if moddedNumberOfBuilders <= moddedNumberOfCities or moddedNumberOfBuilders == 0:
			# If we don't have any Workers by turn 30 we really need to get moving
			if simulation.currentTurn > 30:
				# AI_CITYSTRATEGY_NEED_TILE_IMPROVERS_DESPERATE_TURN
				return True

		return False

	def _shouldBeActiveWantTileImprovers(self, city, simulation) -> bool:
		currentNumberOfCities = len(simulation.citiesOf(city.player))

		lastTurnBuilderDisbanded = city.player.economicAI.lastTurnBuilderDisbanded()
		if lastTurnBuilderDisbanded is not None:
			if lastTurnBuilderDisbanded > 0 and simulation.currentTurn - lastTurnBuilderDisbanded <= 25:
				return False

		playerUnits = simulation.unitsOf(city.player)
		numSettlers = len(list(filter(lambda unit: unit.task() == UnitTaskType.settle, playerUnits)))
		numBuilders = len(list(filter(lambda unit: unit.task() == UnitTaskType.work, playerUnits)))

		numberOfCities = max(1, int((currentNumberOfCities * 3) / 4))
		if numBuilders >= numberOfCities:
			return False

		# Don't get desperate for training a Builder here unless the City is at least of a certain size
		if city.population() >= 2:  # AI_CITYSTRATEGY_WANT_TILE_IMPROVERS_MINIMUM_SIZE
			# If we don't even have 1 builder on map or in a queue, turn this on immediately
			if numBuilders < 1:
				return True


			weightThresholdModifier = self.weightThresholdModifierFor(city.player)  # 2 Extra Weight per TILE_IMPROVEMENT Flavor
			perCityThreshold = self.weightThreshold() + weightThresholdModifier  # 40

			numResources = 0
			numImprovedResources = 0

			# Look at all Tiles this City could potentially work to see if there are any Water Resources that could be improved
			for pt in city.location.areaWithRadius(3):  # City.workRadius - causes circular import
				tile = simulation.tileAt(pt)

				if tile is None:
					continue

				if tile.hasOwner() and tile.owner() == city.player:
					if tile.terrain().isLand():
						if not tile.hasAnyResourceFor(city.player):
							continue

						improvements = tile.possibleImprovements()

						# no valid build found
						if len(improvements) == 0:
							continue

						# already build
						if tile.hasImprovement(improvements[0]):
							numImprovedResources += 1

						numResources += 1

			manyUnimproveResources = (2 * (numResources - numImprovedResources)) > numResources
			multiplier = numberOfCities
			multiplier += len(list(filter(lambda city: city.isFeatureSurrounded(), simulation.citiesOf(city.player))))
			if manyUnimproveResources:
				multiplier += 1

			multiplier += numSettlers

			weightThreshold = (perCityThreshold * multiplier)

			# Do we want more Builders?
			if (numBuilders * 100) < weightThreshold:
				return city.player.treasury.value() > 10

		return False

	def _shouldBeActiveEnoughTileImprovers(self, city, simulation):
		""" "Enough Tile Improvers" City Strategy: This is not a Player Strategy because we only want to prevent the
		training of new Builders, not nullify new Techs or Policies, which could still be very useful"""
		lastTurnWorkerDisbanded = city.player.economicAI.lastTurnBuilderDisbanded()
		if lastTurnWorkerDisbanded is not None and lastTurnWorkerDisbanded >= 0 and \
			(simulation.currentTurn - lastTurnWorkerDisbanded) <= 10:
			return True

		if city.cityStrategyAI.adopted(CityStrategyType.needTileImprovers):
			return False

		numberOfBuilders = city.player.countUnitsWithDefaultTask(UnitTaskType.work, simulation)

		# If it's a minor with at least 1 worker per city, always return true
		# if (GET_PLAYER(pCity->getOwner()).isMinorCiv())
		# 	if (iNumBuilders >= kPlayer.getNumCities())
		# 		return True

		cityStrategy: CityStrategyType = CityStrategyType.enoughTileImprovers

		weightThresholdModifier = cityStrategy.weightThresholdModifierFor(city.player)  # 10 Extra Weight per TILE_IMPROVEMENT Flavor
		perCityThreshold = cityStrategy.weightThreshold() + weightThresholdModifier // 100

		moddedNumberOfCities = city.player.numberOfCities(simulation) + city.player.countCitiesFeatureSurrounded(simulation)
		weightThreshold = (perCityThreshold * moddedNumberOfCities)

		# Average Player wants no more than 1.50 Builders per City[150 Weight is Average; range is 100 to 200]
		if numberOfBuilders * 100 >= weightThreshold:
			return True

		return False

	def _shouldBeActiveNeedNavalGrowth(self, city, simulation) -> bool:
		""" "Need Naval Growth" City Strategy: Looks at the Tiles this City can work, and if there are a lot of Ocean
		tiles prioritizes NAVAL_GROWTH: should give us a Harbor eventually"""
		numOceanPlots = 0
		numTotalWorkablePlots = 0

		# Look at all Tiles this City could potentially work
		for workingTileLocation in city.cityCitizens.workingTileLocations():
			loopPlot = simulation.tileAt(workingTileLocation)

			if loopPlot is None:
				continue

			if loopPlot.isCity():
				continue

			if loopPlot.hasOwner() and not city.player == loopPlot.owner():
				continue

			numTotalWorkablePlots += 1

			if loopPlot.isWater() and loopPlot.feature() != FeatureType.lake:
				numOceanPlots += 1

		if numTotalWorkablePlots > 0:
			cityStrategy: CityStrategyType = CityStrategyType.needNavalGrowth
			weightThresholdModifier = cityStrategy.weightThresholdModifierFor(city.player) # -1 Weight per NAVAL_GROWTH Flavor
			weightThreshold = cityStrategy.weightThreshold() + weightThresholdModifier # 40

			# If at least 35% (Average Player) of a City's workable Tiles are low-food Water then we really should be building a Harbor
			# [35 Weight is Average; range is 30 to 40]
			if (numOceanPlots * 100) / numTotalWorkablePlots >= weightThreshold:
				return True

		return False

	def _shouldBeActiveNeedNavalTileImprovement(self, city, simulation) -> bool:
		""" "Need Naval Tile Improvement" City Strategy: If there's an unimproved Resource in the water that we could
		be using, HIGHLY prioritize NAVAL_TILE_IMPROVEMENT in this City: should give us a Workboat in short order"""
		numUnimprovedWaterResources = 0

		# Look at all Tiles this City could potentially work to see if there are any Water Resources that could
		# be improved
		for workingTileLocation in city.cityCitizens.workingTileLocations():
			loopPlot = simulation.tileAt(workingTileLocation)

			if loopPlot is None:
				continue

			if loopPlot.hasOwner() and not city.player == loopPlot.owner():
				continue

			if loopPlot.isWater():
				# Only look at Tiles THIS City can use; Prevents issue where two Cities can look at the same tile
				# the same turn and both want Workboats for it; By the time this Strategy is called for a City
				# another City isn't guaranteed to have popped its previous order and registered that it's now
				# training a Workboat! :(
				if city.cityCitizens.canWorkAt(workingTileLocation, simulation):
					# Does this Tile already have a Resource, and if so, is it already improved?
					if loopPlot.resourceFor(city.player) != FeatureType.none and loopPlot.improvement() == ImprovementType.none:
						numUnimprovedWaterResources += 1

		numWaterTileImprovers = city.player.countUnitsWithDefaultTask(UnitTaskType.workerSea, simulation)

		# Are there more Water Resources we can build an Improvement on than we have Naval Tile Improvers?
		if numUnimprovedWaterResources > numWaterTileImprovers:
			return True

		return False

	def _shouldBeActiveEnoughNavalTileImprovement(self, city) -> bool:
		""" "Enough Naval Tile Improvement" City Strategy: If we're not running "Need Naval Tile Improvement" then
		there's no need to worry about it at all"""
		if not city.cityStrategyAI.adopted(CityStrategyType.needNavalTileImprovement):
			return True

		return False

	def _shouldBeActiveNeedImprovementFood(self, city, simulation) -> bool:
		""" "Need Improvement" City Strategy: if we need to get an improvement that increases a yield amount"""
		if city.cityStrategyAI.deficientYield(simulation) == YieldType.food:
			return True

		return False

	def _shouldBeActiveNeedImprovementProduction(self, city, simulation) -> bool:
		if city.cityStrategyAI.deficientYield(simulation) == YieldType.production:
			return True

		return False

	def _shouldBeActiveHaveTrainingFacility(self, city) -> bool:
		if city.buildings.hasBuilding(BuildingType.barracks):
			return True

		if city.buildings.hasBuilding(BuildingType.armory):
			return True

		return False

	def _shouldBeActiveCapitalNeedSettler(self, city, simulation) -> bool:
		""" "Capital Need Settler" City Strategy: have capital build a settler ASAP"""
		if not city.isCapital():
			return False

		numberOfCities = len(simulation.citiesOf(city.player))
		numberOfSettlers = city.player.countUnitsWithDefaultTask(UnitTaskType.settle, simulation)
		numberOfCitiesAndSettlers = numberOfCities + numberOfSettlers

		if numberOfCitiesAndSettlers < 3:
			if simulation.currentTurn > 100 and city.cityStrategy.adopted(CityStrategyType.capitalUnderThreat):
				return False

			if city.player.militaryAI.adopted(MilitaryStrategyType.warMobilization):
				return False

			weightThresholdModifier = self.weightThresholdModifierFor(city.player)
			weightThreshold = self.weightThreshold() + weightThresholdModifier

			if numberOfCitiesAndSettlers == 1 and simulation.currentTurn * 4 > weightThreshold:
				return True

			if numberOfCitiesAndSettlers == 2 and simulation.currentTurn > weightThreshold:
				return True

		return False

	def _shouldBeActiveCapitalUnderThreat(self, city, simulation) -> bool:
		""" "Capital Under Threat" City Strategy: need military units, don't build buildings!"""
		if not city.isCapital():
			return False

		mostThreatenedCity = city.player.militaryAI.mostThreatenedCity(simulation)
		if mostThreatenedCity is not None:
			if mostThreatenedCity.location == city.location and mostThreatenedCity.threatValue() > 200:
				return True

		return False

	def _shouldBeActiveUnderBlockade(self, city) -> bool:
		# fixme
		return False

	def _shouldBeActiveCoastCity(self, city, simulation) -> bool:
		""" "Coast City" City Strategy: give a little flavor to this city"""
		return simulation.isCoastalAt(city.location)

	def _shouldBeActiveRiverCity(self, city, simulation) -> bool:
		return simulation.riverAt(city.location)

	def _shouldBeActiveMountainCity(self, city, simulation) -> bool:
		""" "Mountain City" City Strategy: give a little flavor to this city"""
		# scan the nearby tiles to see if there is a mountain close enough to build an observatory
		for pt in city.location.areaWithRadius(3):  # City.workRadius - causes circular import
			tile = simulation.tileAt(pt)

			if tile is not None and tile.hasFeature(FeatureType.mountains):
				return True

		return False

	def _shouldBeActiveHillCity(self, city, simulation) -> bool:
		""" "Hill City" City Strategy: give a little flavor to this city"""
		numHills = 0

		# scan the nearby tiles to see if there are at least *two* hills in the vicinity
		for pt in city.location.areaWithRadius(3):  # City.workRadius - causes circular import
			tile = simulation.tileAt(pt)

			if tile is not None and tile.hasOwner() and tile.owner() == city.player and tile.isHills():
				numHills += 1

				if numHills > 1:
					return True

		return False

	def _shouldBeActiveForestCity(self, city, simulation):
		""" "Forest City" City Strategy: give a little flavor to this city"""
		numForests = 0

		# scan the nearby tiles to see if there are at least two forests in the vicinity
		for pt in city.location.areaWithRadius(3):  # City.workRadius - causes circular import
			tile = simulation.tileAt(pt)

			if tile is not None and tile.hasOwner() and tile.owner() == city.player and \
				tile.hasFeature(FeatureType.forest):
				numForests += 1

				if numForests > 1:
					return True

		return False

	def _shouldBeActiveJungleCity(self, city, simulation):
		""" "Jungle City" City Strategy: give a little flavor to this city"""
		numForests = 0

		# scan the nearby tiles to see if there are at least two jungles in the vicinity
		for pt in city.location.areaWithRadius(3):  # City.workRadius - causes circular import
			tile = simulation.tileAt(pt)

			if tile is not None and tile.hasOwner() and tile.owner() == city.player and \
				tile.hasFeature(FeatureType.rainforest):
				numForests += 1

				if numForests > 1:
					return True

		return False


class WeightedFlavorList(WeightedBaseList):
	def __init__(self):
		super().__init__()
		for flavorType in list(FlavorType):
			if flavorType == FlavorType.none:
				continue

			self.setWeight(0.0, flavorType)


class WeightedYieldList(WeightedBaseList):
	def __init__(self):
		super().__init__()
		for yieldType in list(YieldType):
			if yieldType == YieldType.none:
				continue

			self.setWeight(0.0, yieldType)


class CityStrategyAdoptionItem:
	def __init__(self, cityStrategyType: CityStrategyType, adopted: bool, turnOfAdoption: int):
		self.cityStrategyType = cityStrategyType
		self.adopted = adopted
		self.turnOfAdoption = turnOfAdoption


class CityStrategyAdoptions:
	def __init__(self):
		self.adoptions = []

		for cityStrategyType in list(CityStrategyType):
			self.adoptions.append(CityStrategyAdoptionItem(cityStrategyType, False, -1))

	def adopted(self, cityStrategyType: CityStrategyType) -> bool:
		item = next((adoptionItem for adoptionItem in self.adoptions if
					 adoptionItem.cityStrategyType == cityStrategyType), None)

		if item is not None:
			return item.adopted

		raise InvalidEnumError(cityStrategyType)

	def turnOfAdoption(self, cityStrategyType: CityStrategyType) -> int:
		item = next((adoptionItem for adoptionItem in self.adoptions if
					 adoptionItem.cityStrategyType == cityStrategyType), None)

		if item is not None:
			return item.turnOfAdoption

		raise InvalidEnumError(cityStrategyType)

	def adopt(self, cityStrategyType: CityStrategyType, turnOfAdoption: int):
		item = next((adoptionItem for adoptionItem in self.adoptions if
					 adoptionItem.cityStrategyType == cityStrategyType), None)

		if item is not None:
			item.adopted = True
			item.turnOfAdoption = turnOfAdoption
			return

		raise InvalidEnumError(cityStrategyType)

	def abandon(self, cityStrategyType: CityStrategyType):
		item = next((adoptionItem for adoptionItem in self.adoptions if
					 adoptionItem.cityStrategyType == cityStrategyType), None)

		if item is not None:
			item.adopted = False
			item.turnOfAdoption = -1
			return

		raise InvalidEnumError(cityStrategyType)


class BuildingWeights(WeightedBaseList):
	def __init__(self):
		super().__init__()
		for buildingType in list(BuildingType):
			self.addWeight(0.0, buildingType)

	def reset(self):
		self.removeAll()

		for buildingType in list(BuildingType):
			self.addWeight(0.0, buildingType)


class DistrictWeights(WeightedBaseList):
	def __init__(self):
		super().__init__()
		for districtType in list(DistrictType):
			self.addWeight(0.0, districtType)

	def reset(self):
		self.removeAll()

		for districtType in list(DistrictType):
			self.addWeight(0.0, districtType)


class BuildingProductionAI:
	def __init__(self, player):
		self.player = player

		self.buildingWeights = BuildingWeights()
		self.districtWeights = DistrictWeights()

		self.initWeights()

	def weight(self, itemType: Union[DistrictType, BuildingType]) -> float:
		if isinstance(itemType, DistrictType):
			return self.districtWeights.weight(itemType)
		elif isinstance(itemType, BuildingType):
			return self.buildingWeights.weight(itemType)

		raise InvalidEnumError(itemType)

	def initWeights(self):
		if self.player is None:
			return

		for flavorType in list(FlavorType):
			if flavorType == FlavorType.none:
				continue

			leaderFlavor = self.player.personalAndGrandStrategyFlavor(flavorType)

			for buildingType in list(BuildingType):
				buildingFlavor = buildingType.flavor(flavorType)
				self.buildingWeights.addWeight(buildingFlavor * leaderFlavor, buildingType)

			for districtType in list(DistrictType):
				districtFlavor = districtType.flavor(flavorType)
				self.districtWeights.addWeight(districtFlavor * leaderFlavor, districtType)

		return

	def reset(self):
		self.buildingWeights.reset()
		self.districtWeights.reset()


class UnitWeights(WeightedBaseList):
	def __init__(self):
		super().__init__()
		for unitType in list(UnitType):
			self.addWeight(0.0, unitType)

	def reset(self):
		self.removeAll()
		for unitType in list(UnitType):
			self.addWeight(0.0, unitType)


class CityStrategyAIHelpers:
	@classmethod
	def reweightByTurnsLeft(cls, originalWeight: int, turnsLeft: int) -> int:
		"""Routine to reweight a city buildable based on time to build"""
		# 10 turns will add 0.02; 80 turns will add 0.16
		additionalTurnCostFactor = turnsLeft * 0.004  # AI_PRODUCTION_WEIGHT_MOD_PER_TURN_LEFT
		totalCostFactor = additionalTurnCostFactor + 0.15  # AI_PRODUCTION_WEIGHT_BASE_MOD
		weightDivisor = pow(float(turnsLeft), totalCostFactor)

		if weightDivisor == 0.0:
			return originalWeight

		return int(float(originalWeight) / weightDivisor)


class UnitProductionAI:
	def __init__(self, city):
		self.city = city
		self.unitWeights = UnitWeights()

		self.initWeights()

	def addWeight(self, weight: int, flavorType: FlavorType):
		if weight == 0:
			return

		for unitType in list(UnitType):
			flavor = next(filter(lambda flavorIterator: flavorIterator.flavorType == flavorType, unitType.flavors()), None)
			if flavor is not None:
				self.unitWeights.setWeight(flavor.value * weight, unitType)

		return

	def weight(self, unitType: UnitType) -> float:
		return self.unitWeights.weight(unitType)

	def initWeights(self):
		if self.city.player is None:
			return

		for flavorType in list(FlavorType):
			if flavorType == FlavorType.none:
				continue

			leaderFlavor = self.city.player.personalAndGrandStrategyFlavor(flavorType)

			for unitType in list(UnitType):
				unitFlavor = unitType.flavor(flavorType)
				self.unitWeights.addWeight(unitFlavor * leaderFlavor, unitType)

		return

	def recommendUnit(self, task: UnitTaskType, simulation) -> UnitType:
		"""Recommend highest-weighted unit"""
		if task == UnitTaskType.none:
			return UnitType.none

		# Reset list of all the possible units
		buildables = UnitWeights()
		buildables.clear()

		# Loop through adding the available units
		for loopUnitType in list(UnitType):
			# Make sure this unit can be built now
			if self.city.canTrainUnit(loopUnitType, simulation):
				# Make sure it matches the requested unit AI type
				if loopUnitType.defaultTask() == task:
					# Update weight based on turns to construct
					turnsLeft = self.city.unitProductionTurnsLeftFor(loopUnitType)
					weight = CityStrategyAIHelpers.reweightByTurnsLeft(self.unitWeights.weight(loopUnitType), turnsLeft)
					buildables.setWeight(weight, loopUnitType)

		# Sort items and grab the first one
		if len(buildables.keys()) > 0:
			buildables.sortByValue(reverse=True)
			# LogPossibleBuilds(eUnitAIType);
			return firstOrNone(buildables.keys())
		else:
			# Unless we didn't find any
			return UnitType.none


class WonderWeights(WeightedBaseList):
	def __init__(self):
		super().__init__()
		for wonderType in list(WonderType):
			self.addWeight(0.0, wonderType)


class WonderSelection:
	def __init__(self, wonder: WonderType, location: HexPoint, totalWeights: int):
		self.wonder: WonderType = wonder
		self.location: HexPoint = location
		self.totalWeights: int = totalWeights


class WonderProductionAI:
	def __init__(self, player):
		self.player = player
		self._weights = WonderWeights()

		self.initWeights()

	def initWeights(self):
		if self.player is None:
			return

		for flavorType in list(FlavorType):
			leaderFlavor = self.player.personalAndGrandStrategyFlavor(flavorType)

			for wonderType in list(WonderType):
				wonderFlavor = wonderType.flavor(flavorType)
				self._weights.addWeight(wonderFlavor * leaderFlavor, wonderType)

		return

	def weight(self, wonderType: WonderType) -> float:
		return self._weights.weight(wonderType)

	def chooseWonder(self, adjustForOtherPlayers: bool, nextWonderWeight: int, simulation):
		citySpecializationAI = self.player.citySpecializationAI

		cities = simulation.citiesOf(self.player)

		if len(cities) == 0:
			raise Exception("cant get cities")

		# Reset list of all the possible wonders
		buildables = WonderWeights()

		# Guess which city will be producing this (doesn't matter that much since weights are all relative)
		wonderCity = citySpecializationAI.wonderBuildCity()
		if wonderCity is None:
			wonderCity = firstOrNone(cities)

		if wonderCity is None:
			return WonderSelection(WonderType.none, location=constants.invalidHexPoint, totalWeights=0)

		estimatedProductionPerTurn = wonderCity.productionLastTurn()  # getProduction
		if estimatedProductionPerTurn < 1.0:
			estimatedProductionPerTurn = 1.0

		# Loop through adding the available wonders
		for wonderType in list(WonderType):
			# Make sure this wonder can be built now
			if self.haveCityToBuild(wonderType, simulation):
				turnsRequired = max(1.0, float(wonderType.productionCost()) / estimatedProductionPerTurn)

				# 10 turns will add 0.02; 80 turns will add 0.16
				additionalTurnCostFactor = 0.015 * float(turnsRequired)  # AI_PRODUCTION_WEIGHT_MOD_PER_TURN_LEFT
				totalCostFactor = 0.15 + additionalTurnCostFactor  # AI_PRODUCTION_WEIGHT_BASE_MOD
				weightDivisor = pow(float(turnsRequired), totalCostFactor)

				weight = self._weights.weight(wonderType) / weightDivisor

				if adjustForOtherPlayers:
					# Adjust weight for this wonder down based on number of other players currently working on it
					# int iNumOthersConstructing = 0;
					# for (int iPlayerLoop = 0; iPlayerLoop < MAX_MAJOR_CIVS; iPlayerLoop++)
					# 	PlayerTypes eLoopPlayer = (PlayerTypes) iPlayerLoop;
					# 	if (GET_PLAYER(eLoopPlayer).getBuildingClassMaking((BuildingClassTypes)kBuilding.GetBuildingClassType()) > 0)
					# 		iNumOthersConstructing++;
					#
					# iWeight = iWeight/ (1 + iNumOthersConstructing); * /
					pass

				buildables.addWeight(weight, wonderType)

		# Sort items and grab the first one
		if len(buildables.items()) > 0:
			# buildables = sorted(buildables, key=lambda b: b[1])

			# LogPossibleWonders();
			if buildables.totalWeights() > 0.0:
				selectedWonder = buildables.chooseFromTopChoices()
				if selectedWonder is not None:
					selectedLocation: HexPoint = constants.invalidHexPoint
					for loopCity in cities:
						cityCitizens = loopCity.cityCitizens

						for loopLocation in cityCitizens.workingTileLocations():
							if loopCity.canBuildWonder(selectedWonder, loopLocation, simulation):
								selectedLocation = loopLocation

					return WonderSelection(selectedWonder, selectedLocation, totalWeights=int(buildables.totalWeights()))

			# Nothing with any weight
			return WonderSelection(WonderType.none, constants.invalidHexPoint, totalWeights=0)
		else:
			# Unless we didn't find any
			return WonderSelection(WonderType.none, constants.invalidHexPoint, totalWeights=0)

	def haveCityToBuild(self, wonder: WonderType, simulation) -> bool:
		"""Check to make sure some city can build this wonder"""
		for loopCity in simulation.citiesOf(self.player):
			cityCitizens = loopCity.cityCitizens

			for loopLocation in cityCitizens.workingTileLocations():
				if loopCity.canBuildWonder(wonder, loopLocation, simulation):
					return True

		return False


class BuildableItemWeights(WeightedBaseList):
	pass


class BuildableType(ExtendedEnum):
	district = 'district'
	building = 'building'
	wonder = 'wonder'
	project = 'project'
	unit = 'unit'


class BuildableItem:
	def __init__(self, item: Union[DistrictType, BuildingType, WonderType, UnitType, ProjectType],
				 location: Optional[HexPoint] = None):
		if isinstance(item, DistrictType):
			self.buildableType = BuildableType.district
			self.districtType: DistrictType = item
			self.buildingType = None
			self.unitType = None
			self.wonderType = None
			self.projectType = None
			self.location = location
			self.production = 0.0
		elif isinstance(item, BuildingType):
			self.buildableType = BuildableType.building
			self.districtType = None
			self.buildingType: BuildingType = item
			self.unitType = None
			self.wonderType = None
			self.projectType = None
			self.location = None  # buildings don't need a location
			self.production = 0.0
		elif isinstance(item, UnitType):
			self.buildableType = BuildableType.unit
			self.districtType = None
			self.buildingType = None
			self.unitType: UnitType = item
			self.wonderType = None
			self.projectType = None
			self.location = None  # units don't need a location
			self.production = 0.0
		elif isinstance(item, WonderType):
			self.buildableType = BuildableType.wonder
			self.districtType = None
			self.buildingType = None
			self.unitType = None
			self.wonderType: WonderType = item
			self.projectType = None
			self.location = location
			self.production = 0.0
		elif isinstance(item, ProjectType):
			self.buildableType = BuildableType.project
			self.districtType = None
			self.buildingType = None
			self.unitType = None
			self.wonderType = None
			self.projectType: ProjectType = item
			self.location = location
			self.production = 0.0
		else:
			raise Exception(f'unsupported buildable type: {type(item)}')

	def __repr__(self):
		if self.buildableType == BuildableType.district:
			return f'BuildableItem(BuildableType.district, {self.districtType}, {self.location})'
		elif self.buildableType == BuildableType.building:
			return f'BuildableItem(BuildableType.building, {self.buildingType})'
		elif self.buildableType == BuildableType.unit:
			return f'BuildableItem(BuildableType.unit, {self.unitType})'
		elif self.buildableType == BuildableType.wonder:
			return f'BuildableItem(BuildableType.wonder, {self.wonderType}, {self.location})'
		elif self.buildableType == BuildableType.project:
			return f'BuildableItem(BuildableType.project, {self.projectType})'

		raise Exception(f'unsupported buildable type: {self.buildableType}')

	def __eq__(self, other):
		if isinstance(other, BuildableItem):
			if self.buildableType == BuildableType.district:
				if other.buildableType != BuildableType.district:
					return False

				return self.districtType == other.districtType and self.location == other.location
			elif self.buildableType == BuildableType.building:
				if other.buildableType != BuildableType.building:
					return False

				return self.buildingType == other.buildingType
			elif self.buildableType == BuildableType.unit:
				if other.buildableType != BuildableType.unit:
					return False

				return self.unitType == other.unitType
			elif self.buildableType == BuildableType.wonder:
				if other.buildableType != BuildableType.wonder:
					return False

				return self.wonderType == other.wonderType and self.location == other.location
			elif self.buildableType == BuildableType.project:
				if other.buildableType != BuildableType.project:
					return False

				return self.projectType == other.projectType

			raise Exception(f'unsupported buildable type: {self.buildableType}')

		raise Exception(f'unsupported buildable type: {self.buildableType}')

	def __hash__(self):
		if self.buildableType == BuildableType.district:
			return hash((self.buildableType, self.districtType, self.location))
		elif self.buildableType == BuildableType.building:
			return hash((self.buildableType, self.buildingType))
		elif self.buildableType == BuildableType.unit:
			return hash((self.buildableType, self.unitType))
		elif self.buildableType == BuildableType.wonder:
			return hash((self.buildableType, self.wonderType, self.location))
		elif self.buildableType == BuildableType.project:
			return hash((self.buildableType, self.projectType))

		raise Exception(f'unsupported buildable type: {self.buildableType}')

	def addProduction(self, productionDelta: float):
		self.production += productionDelta

	def productionLeftFor(self, player) -> float:

		if self.buildableType == BuildableType.unit:
			unitType = self.unitType
			return float(player.productionCostOfUnit(unitType)) - self.production

		elif self.buildableType == BuildableType.building:
			buildingType = self.buildingType
			return float(buildingType.productionCost()) - self.production

		elif self.buildableType == BuildableType.wonder:
			wonderType = self.wonderType
			return float(wonderType.productionCost()) - self.production

		elif self.buildableType == BuildableType.district:
			districtType = self.districtType
			return float(districtType.productionCost()) - self.production

		elif self.buildableType == BuildableType.project:
			projectType = self.projectType
			return float(projectType.productionCost()) - self.production

	def ready(self, player) -> bool:
		return self.productionLeftFor(player) <= 0


class YieldValue:
	def __init__(self, location: HexPoint, value: float):
		self.location = location
		self.value = value

	def __lt__(self, other):
		if isinstance(other, YieldValue):
			return self.value > other.value


class CityStrategyAI:
	"""
		++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
		CLASS:      CvCityStrategyAI
		!  brief        Manages operations for a single city in the game world

		!  Key Attributes:
		!  - One instance for each city
		!  - Receives instructions from other AI components (usually as flavor changes) to
		!    specialize, switch production, etc.
		!  - Oversees both the city governor AI and the AI managing what the city is building
		++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	"""

	def __init__(self, city):
		self.city = city

		self.cityStrategyAdoption = CityStrategyAdoptions()
		self.flavors = Flavors()
		self.focusYield: YieldType = YieldType.none

		self.buildingProductionAI = BuildingProductionAI(city.player)
		self.unitProductionAI = UnitProductionAI(city)
		self.wonderProductionAI = WonderProductionAI(city.player)

		self.specializationValue = CitySpecializationType.generalEconomic
		self.defaultSpecializationValue = CitySpecializationType.generalEconomic
		self.flavorWeights = WeightedFlavorList()
		self.bestYieldAverage = WeightedYieldList()
		self.yieldDeltaValue = WeightedYieldList()

	def doTurn(self, simulation):
		for cityStrategyType in list(CityStrategyType):
			# Minor Civs can't run some Strategies
			# if self.city.player.isCityState():
			#	cont

			# check tech
			requiredTech = cityStrategyType.requiredTech()
			isTechGiven = True if requiredTech is None else self.city.player.hasTech(requiredTech)
			obsoleteTech = cityStrategyType.obsoleteTech()
			isTechObsolete = False if obsoleteTech is None else self.city.player.hasTech(obsoleteTech)

			# Do we already have this CityStrategy adopted?
			shouldCityStrategyStart = True
			if self.cityStrategyAdoption.adopted(cityStrategyType=cityStrategyType):
				shouldCityStrategyStart = False
			elif not isTechGiven:
				shouldCityStrategyStart = False

			shouldCityStrategyEnd = False
			if self.cityStrategyAdoption.adopted(cityStrategyType=cityStrategyType):
				# If Strategy is Permanent we can't ever turn it off
				if not cityStrategyType.permanent():
					if cityStrategyType.checkEachTurns() > 0:
						# Is it a turn where we want to check to see if this Strategy is maintained?
						if simulation.currentTurn - self.cityStrategyAdoption.turnOfAdoption(cityStrategyType) % cityStrategyType.checkEachTurns() == 0:
							shouldCityStrategyEnd = True

					if shouldCityStrategyEnd and cityStrategyType.minimumAdoptionTurns() > 0:
						# Has the minimum  # of turns passed for this Strategy?
						if simulation.currentTurn < self.cityStrategyAdoption.turnOfAdoption(cityStrategyType) + cityStrategyType.minimumAdoptionTurns():
							shouldCityStrategyEnd = False

			# Check CityStrategy Triggers
			# Functionality and existence of specific CityStrategies is hardcoded here, but data is stored in XML so it's easier to modify
			if shouldCityStrategyStart or shouldCityStrategyEnd:
				# Has the Tech which obsoletes this Strategy? If so, Strategy should be deactivated regardless of other factors
				strategyShouldBeActive = False

				# Strategy isn't obsolete, so test triggers as normal
				if not isTechObsolete:
					strategyShouldBeActive = cityStrategyType.shouldBeActiveFor(self.city, simulation)

				# This variable keeps track of whether or not we should be doing something(i.e.Strategy is active now but should be turned off, OR Strategy is inactive and should be enabled)
				bAdoptOrEndStrategy = False

				# Strategy should be on, and if it's not, turn it on
				if strategyShouldBeActive:
					if shouldCityStrategyStart:
						bAdoptOrEndStrategy = True
					elif shouldCityStrategyEnd:
						bAdoptOrEndStrategy = False

				# Strategy should be off, and if it's not, turn it off
				else:
					if shouldCityStrategyStart:
						bAdoptOrEndStrategy = False
					elif shouldCityStrategyEnd:
						bAdoptOrEndStrategy = True

				if bAdoptOrEndStrategy:
					if shouldCityStrategyStart:
						self.cityStrategyAdoption.adopt(cityStrategyType=cityStrategyType, turnOfAdoption=simulation.currentTurn)
					elif shouldCityStrategyEnd:
						self.cityStrategyAdoption.abandon(cityStrategyType=cityStrategyType)

		self.updateFlavors()

	def adopted(self, cityStrategyType: CityStrategyType) -> bool:
		return self.cityStrategyAdoption.adopted(cityStrategyType=cityStrategyType)

	def specialization(self) -> CitySpecializationType:
		return self.specializationValue

	def setSpecialization(self, specialization: CitySpecializationType):
		self.specializationValue = specialization

	def defaultSpecialization(self) -> CitySpecializationType:
		return self.defaultSpecializationValue

	def updateFlavors(self):
		self.flavors.reset()

		for cityStrategyType in list(CityStrategyType):
			if self.cityStrategyAdoption.adopted(cityStrategyType=cityStrategyType):
				for cityStrategyTypeFlavor in cityStrategyType.flavorModifiers():
					self.flavors += cityStrategyTypeFlavor

		# FIXME: inform sub AI
		for flavorType in list(FlavorType):
			flavorValue = self.flavors.value(flavorType)

			# limit
			if flavorValue < 0:
				flavorValue = 0

			self.unitProductionAI.addWeight(flavorValue, flavorType)

	def chooseProduction(self, simulation):
		if simulation is None:
			raise Exception('simulation must not be None')
		unitsOfPlayer = simulation.unitsOf(self.city.player)
		buildables = BuildableItemWeights()
		settlersOnMap: int = sum(map(lambda unit: 1 if unit.task() == UnitTaskType.settle else 0, unitsOfPlayer))
		buildersOnMap: int = sum(map(lambda unit: 1 if unit.task() == UnitTaskType.work else 0, unitsOfPlayer))
		numberOfCities: int = self.city.player.numberOfCities(simulation)

		# Check units for operations first
		unitForArmy = self.city.player.militaryAI.unitTypeForArmyIn(self.city, simulation)
		if unitForArmy is not None and unitForArmy != UnitType.none:
			buildableItem = BuildableItem(unitForArmy)
			tempWeight = 750  # AI_CITYSTRATEGY_ARMY_UNIT_BASE_WEIGHT
			offenseFlavor = self.city.player.grandStrategyAI.personalityAndGrandStrategy(FlavorType.offense)
			bonusMultiplier = max(1, simulation.handicap.value() - 5)  # more at the higher difficulties
			tempWeight += (250 * offenseFlavor * bonusMultiplier)  # AI_CITYSTRATEGY_OPERATION_UNIT_FLAVOR_MULTIPLIER
			# add in the weight of this unit as if I were deciding to build it without having a reason
			tempWeight += self.unitProductionAI.weight(unitForArmy)
			buildables.addWeight(tempWeight, buildableItem)

		# Loop through adding the available districts
		for districtType in list(DistrictType):
			if districtType == DistrictType.none or districtType == DistrictType.cityCenter:
				continue

			if self.city.canBuildDistrict(districtType, simulation=simulation):
				weight: float = float(self.buildingProductionAI.weight(districtType))
				bestDistrictLocation = self.city.bestLocationForDistrict(districtType, simulation)

				if bestDistrictLocation is None:
					logging.debug(f'no location found for District {districtType} - skipping')
					continue

				if self.city.canBuildDistrict(districtType, bestDistrictLocation, simulation):
					buildableItem = BuildableItem(districtType, bestDistrictLocation)
					# re-weight ?
					buildables.addWeight(weight, buildableItem)

		# Loop through adding the available buildings
		for buildingType in list(BuildingType):
			if self.city.canBuildBuilding(buildingType, simulation):
				weight: float = float(self.buildingProductionAI.weight(buildingType))
				buildableItem = BuildableItem(buildingType)

				# re-weight
				turnsLeft = self.city.buildingProductionTurnsLeftFor(buildingType)
				totalCostFactor = 0.15 + 0.004 * float(turnsLeft)  # AI_PRODUCTION_WEIGHT_BASE_MOD / AI_PRODUCTION_WEIGHT_MOD_PER_TURN_LEFT
				weightDivisor = pow(float(turnsLeft), totalCostFactor)
				weight /= weightDivisor

				buildables.addWeight(weight, buildableItem)

		# Loop through adding the available units
		for unitType in list(UnitType):
			if self.city.canTrainUnit(unitType, simulation):
				weight = float(self.unitProductionAI.weight(unitType))
				buildableItem = BuildableItem(unitType)

				# re-weight
				turnsLeft = self.city.unitProductionTurnsLeftFor(unitType)
				totalCostFactor = 0.15 + 0.004 * float(turnsLeft)  # AI_PRODUCTION_WEIGHT_BASE_MOD / AI_PRODUCTION_WEIGHT_MOD_PER_TURN_LEFT
				weightDivisor = pow(float(turnsLeft), totalCostFactor)
				weight = float(weight) / weightDivisor

				if unitType.defaultTask() == UnitTaskType.settle:
					if settlersOnMap >= 2:
						weight = 0.0

				if unitType.defaultTask() == UnitTaskType.work:
					if buildersOnMap > numberOfCities:
						weight = 0.0

				buildables.addWeight(weight, buildableItem)

		# Loop through adding the available wonders
		for wonderType in list(WonderType):
			if self.city.canBuildWonder(wonderType, location=None, simulation=simulation):
				weight: float = float(self.wonderProductionAI.weight(wonderType))
				bestWonderLocation = self.city.bestLocationForWonder(wonderType, simulation)

				if bestWonderLocation is None:
					# raise Exception("cant get valid wonder location")
					continue

				if self.city.canBuildWonder(wonderType, bestWonderLocation, simulation):
					buildableItem = BuildableItem(wonderType, bestWonderLocation)

					# re-weight
					turnsLeft = self.city.wonderProductionTurnsLeftFor(wonderType)
					totalCostFactor = 0.15 + 0.004 * float(turnsLeft)  # AI_PRODUCTION_WEIGHT_BASE_MOD / AI_PRODUCTION_WEIGHT_MOD_PER_TURN_LEFT
					weightDivisor = pow(float(turnsLeft), totalCostFactor)
					weight /= weightDivisor

					buildables.addWeight(weight, buildableItem)

		# Loop through adding the available projects
		for projectType in list(ProjectType):
			if self.city.canBuildProject(projectType):
				# FIXME
				pass

		# select one
		selectedIndex = random.randrange(100)

		weightedBuildable = buildables.top3()
		weightedBuildableArray = weightedBuildable.distributeByWeight()
		selectedBuildable = weightedBuildableArray[selectedIndex]

		if selectedBuildable is not None:
			if selectedBuildable.buildableType == BuildableType.unit:
				unitType = selectedBuildable.unitType
				if unitType is not None:
					self.city.startTrainingUnit(unitType)

			elif selectedBuildable.buildableType == BuildableType.building:
				buildingType = selectedBuildable.buildingType
				if buildingType is not None:
					self.city.startBuildingBuilding(buildingType)

			elif selectedBuildable.buildableType == BuildableType.wonder:
				wonderType = selectedBuildable.wonderType
				wonderLocation = selectedBuildable.location
				if wonderType is not None and wonderLocation is not None:
					self.city.startBuildingWonder(wonderType, wonderLocation, simulation)

			elif selectedBuildable.buildableType == BuildableType.district:
				districtType = selectedBuildable.districtType
				districtLocation = selectedBuildable.location
				if districtType is not None and districtLocation is not None:
					self.city.startBuildingDistrict(districtType, districtLocation, simulation)

			elif selectedBuildable.buildableType == BuildableType.project:
				projectType = selectedBuildable.projectType
				projectLocation = selectedBuildable.location
				if projectType is not None and projectLocation is not None:
					self.city.startBuildingProject(projectType, projectLocation, simulation)

		return

	def deficientYield(self, simulation) -> YieldType:
		"""Determines what yield type is in a deficient state. If none, then NO_YIELD is returned"""
		if self.isDeficientFor(YieldType.food, simulation):
			return YieldType.food
		elif self.isDeficientFor(YieldType.production, simulation):
			return YieldType.production

		return YieldType.none

	def isDeficientFor(self, yieldType: YieldType, simulation) -> bool:
		"""Determines if the yield is below a sustainable amount"""
		fDesiredYield: float = self.deficientYieldValue(yieldType)
		fYieldAverage: float = self.yieldAverage(yieldType, simulation)

		iDesiredYield = int(CityStrategyAI.round(fDesiredYield * 100))
		iYieldAverage = int(CityStrategyAI.round(fYieldAverage * 100))

		return iYieldAverage < iDesiredYield

	def yieldAverage(self, yieldType: YieldType, simulation) -> float:
		"""Get the average value of the yield for this city"""
		aiPlots = self.city.player.area().points()
		iTilesWorked: int = 0
		iYieldAmount: int = 0
		for loopPoint in aiPlots:
			loopPlot = simulation.tileAt(loopPoint)

			if loopPlot is None:
				continue

			iTilesWorked += 1
			iYieldAmount += loopPlot.yields(self.city.player, ignoreFeature=False).value(yieldType)

		ratio = 0.0
		if iTilesWorked > 0:
			ratio = iYieldAmount / float(iTilesWorked)

		return ratio

	def deficientYieldValue(self, yieldType: YieldType) -> float:
		"""Get the deficient value of the yield for this city"""
		if yieldType == YieldType.food:
			return 2  # AI_CITYSTRATEGY_YIELD_DEFICIENT_FOOD
		elif yieldType == YieldType.production:
			return 1  # AI_CITYSTRATEGY_YIELD_DEFICIENT_PRODUCTION
		elif yieldType == YieldType.science:
			return 0  # AI_CITYSTRATEGY_YIELD_DEFICIENT_SCIENCE
		elif yieldType == YieldType.gold:
			return 0  # AI_CITYSTRATEGY_YIELD_DEFICIENT_GOLD

		return -999.0

	@staticmethod
	def round(x: float) -> float:
		return math.floor(x + .5) if (x >= 0) else math.ceil(x - .5)

	def updateBestYields(self, simulation):
		self.focusYield = YieldType.none

		self.resetBestYields()

		populationToEvaluate = self.city.population() + 2

		bestFoodYields: [YieldValue] = []
		bestProductionYields: [YieldValue] = []
		bestGoldYields: [YieldValue] = []

		for workingTileLocation in self.city.cityCitizens.workingTileLocations():
			workingTile = simulation.tileAt(workingTileLocation)
			if workingTile is None:
				continue

			if workingTile.workingCity() is not None and workingTile.workingCity().location != self.city.location:
				continue

			yields = workingTile.yields(self.city.player, ignoreFeature=False)
			bestFoodYields.append(YieldValue(location=workingTileLocation, value=yields.food))
			bestProductionYields.append(YieldValue(location=workingTileLocation, value=yields.production))
			bestGoldYields.append(YieldValue(location=workingTileLocation, value=yields.gold))

		bestFoodYields.sort()
		bestProductionYields.sort()
		bestGoldYields.sort()

		slotsToEvaluate = min(len(bestFoodYields), populationToEvaluate)
		if slotsToEvaluate <= 0:
			return

		# add in additional food from the city plot and the city buildings that provide food
		buildingFood = sum(map(lambda building: building.yields().food if self.city.buildings.hasBuilding(building) else 0.0, list(BuildingType)))
		avgValue = (sum(map(lambda bfy: bfy.value, bestFoodYields)) + buildingFood) / float(slotsToEvaluate)
		self.bestYieldAverage.setWeight(avgValue, YieldType.food)
		avgValue = (sum(map(lambda bfy: bfy.value, bestProductionYields)))
		self.bestYieldAverage.setWeight(avgValue, YieldType.production)
		avgValue = (sum(map(lambda bfy: bfy.value, bestGoldYields)))
		self.bestYieldAverage.setWeight(avgValue, YieldType.gold)

		citySpecialization: CitySpecializationType = self.city.cityStrategy.specialization()
		if citySpecialization == CitySpecializationType.none:
			if self.city.player.isHuman():
				# find a specialization type according to the citizen focus type
				focusType = self.city.cityCitizens.focusType()

				if focusType == CityFocusType.food:
					citySpecialization = CitySpecializationType.settlerPump
				elif focusType == CityFocusType.gold:
					citySpecialization = CitySpecializationType.commerce

				# if the human did not have a city ai specialization
				if citySpecialization == CitySpecializationType.none:
					citySpecialization = CitySpecializationType.generalEconomic

		self.yieldDeltaValue.setWeight(self.bestYieldAverage.weight(YieldType.food), YieldType.food)
		self.yieldDeltaValue.setWeight(self.bestYieldAverage.weight(YieldType.production), YieldType.production)
		self.yieldDeltaValue.setWeight(self.bestYieldAverage.weight(YieldType.gold), YieldType.gold)

		self.focusYield = citySpecialization.yieldType() or YieldType.none

		return

	def resetBestYields(self):
		self.bestYieldAverage = YieldList()
		self.yieldDeltaValue = YieldList()

	def yieldDeltaFor(self, yieldType: YieldType) -> float:
		return self.yieldDeltaValue.weight(yieldType)
