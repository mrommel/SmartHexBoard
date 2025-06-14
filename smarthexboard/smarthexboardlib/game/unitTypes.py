from enum import Enum
from typing import Optional, Union, List

from smarthexboard.smarthexboardlib.game.civilizations import CivilizationType
from smarthexboard.smarthexboardlib.game.flavors import Flavor, FlavorType
from smarthexboard.smarthexboardlib.game.states.builds import BuildType
from smarthexboard.smarthexboardlib.game.types import EraType, TechType, CivicType
from smarthexboard.smarthexboardlib.map.types import UnitMovementType, ResourceType, UnitDomainType
from smarthexboard.smarthexboardlib.core.base import ExtendedEnum, InvalidEnumError
from smarthexboard.smarthexboardlib.utils.translation import gettext_lazy as _


class UnitMapType(ExtendedEnum):
	civilian = 'civilian'
	combat = 'combat'


class UnitTaskType(ExtendedEnum):
	none = 'none'
	unknown = 'unknown'

	reserveSea = 'reserveSea'
	escortSea = 'escortSea'
	exploreSea = 'exploreSea'
	cityBombard = 'cityBombard'
	attackSea = 'attackSea'
	cityAttack = 'cityAttack'
	trade = 'trade'
	explore = 'explore'
	ranged = 'ranged'
	defense = 'defense'
	attack = 'attack'
	work = 'work'
	settle = 'settle'
	workerSea = 'workerSea'
	pirateSea = 'pirateSea'
	assaultSea = 'assaultSea'
	settlerSea = 'settlerSea'
	carrierSea = 'carrierSea'

	shadow = 'shadow'

	counter = 'counter'
	fastAttack = 'fastAttack'
	citySpecial = 'citySpecial'
	paradrop = 'paradrop'
	attackAir = 'attackAir'
	defenseAir = 'defenseAir'

	general = 'general'
	admiral = 'admiral'


class UnitAbilityType(ExtendedEnum):
	canBuildRoads = 'canBuildRoads'
	ignoreZoneOfControl = 'ignoreZoneOfControl'
	oceanImpassable = 'oceanImpassable'
	experienceFromTribal = 'experienceFromTribal'
	canMoveInRivalTerritory = 'canMoveInRivalTerritory'
	canEstablishTradeRoute = 'canEstablishTradeRoute'
	canImprove = 'canImprove'
	canFound = 'canFound'
	canCapture = 'canCapture'
	canHeal = 'canHeal'


class UnitOperationType(ExtendedEnum):
	foundCity = 'foundCity'  # AI_OPERATION_FOUND_CITY
	cityCloseDefense = 'cityCloseDefense'  # AI_OPERATION_CITY_CLOSE_DEFENSE
	basicCityAttack = 'basicCityAttack'  # AI_OPERATION_BASIC_CITY_ATTACK
	pillageEnemy = 'pillageEnemy'  # AI_OPERATION_PILLAGE_ENEMY
	rapidResponse = 'rapidResponse'  # AI_OPERATION_RAPID_RESPONSE
	destroyBarbarianCamp = 'destroyBarbarianCamp'  # AI_OPERATION_DESTROY_BARBARIAN_CAMP
	navalAttack = 'navalAttack'  # AI_OPERATION_NAVAL_ATTACK
	navalSuperiority = 'navalSuperiority'  # AI_OPERATION_NAVAL_SUPERIORITY
	navalBombard = 'navalBombard'  # AI_OPERATION_NAVAL_BOMBARDMENT
	colonize = 'colonize'  # AI_OPERATION_COLONIZE
	notSoQuickColonize = 'notSoQuickColonize'  # AI_OPERATION_NOT_SO_QUICK_COLONIZE
	quickColonize = 'quickColonize'  # AI_OPERATION_QUICK_COLONIZE

	pureNavalCityAttack = 'pureNavalCityAttack'
	sneakCityAttack = 'sneakCityAttack'  # AI_OPERATION_SNEAK_CITY_ATTACK
	navalSneakAttack = 'navalSneakAttack'  # AI_OPERATION_NAVAL_SNEAK_ATTACK

	smallCityAttack = 'smallCityAttack'  # AI_OPERATION_SMALL_CITY_ATTACK,
	merchantDelegation = 'merchantDelegation'  # AI_OPERATION_MERCHANT_DELEGATION,
	cityStateAttack = 'cityStateAttack'  # AI_OPERATION_CITY_STATE_ATTACK,
	cityStateNavalAttack = 'cityStateNavalAttack'  # AI_OPERATION_CITY_STATE_NAVAL_ATTACK,
	# AI_OPERATION_NUKE_ATTACK,


class CivilianAttackPriorityType(ExtendedEnum):
	none = 'none'

	highEarlyGameOnly = 'highEarlyGameOnly'
	high = 'high'
	low = 'low'


class UnitClassType:
	pass


class UnitClassTypeData:
	def __init__(self, name: str, domain: UnitDomainType):
		self.name = name
		self.domain = domain


class UnitClassType(ExtendedEnum):
	civilian = 'civilian'

	recon = 'recon'
	melee = 'melee'
	antiCavalry = 'antiCavalry'
	lightCavalry = 'lightCavalry'
	heavyCavalry = 'heavyCavalry'
	ranged = 'ranged'
	siege = 'siege'

	navalMelee = 'navalMelee'
	navalRanged = 'navalRanged'
	navalRaider = 'navalRaider'
	navalCarrier = 'navalCarrier'

	airFighter = 'airFighter'
	airBomber = 'airBomber'

	support = 'support'
	city = 'city'

	@classmethod
	def combat(cls) -> List[UnitClassType]:
		return [
			UnitClassType.melee, UnitClassType.recon, UnitClassType.ranged, UnitClassType.antiCavalry,
			UnitClassType.lightCavalry, UnitClassType.heavyCavalry, UnitClassType.siege,
			UnitClassType.navalMelee, UnitClassType.navalRanged, UnitClassType.navalRaider, UnitClassType.navalCarrier,
			UnitClassType.airFighter, UnitClassType.airBomber
		]

	def name(self) -> str:
		return self._data().name

	def domain(self) -> UnitDomainType:
		return self._data().domain

	def _data(self) -> UnitClassTypeData:
		if self == UnitClassType.civilian:
			return UnitClassTypeData(
				name="TXT_KEY_UNIT_CLASS_CIVILIAN_NAME",
				domain=UnitDomainType.land
			)
		elif self == UnitClassType.melee:
			return UnitClassTypeData(
				name="TXT_KEY_UNIT_CLASS_MELEE_NAME",
				domain=UnitDomainType.land
			)
		elif self == UnitClassType.recon:
			return UnitClassTypeData(
				name="TXT_KEY_UNIT_CLASS_RECON_NAME",
				domain=UnitDomainType.land
			)
		elif self == UnitClassType.ranged:
			return UnitClassTypeData(
				name="TXT_KEY_UNIT_CLASS_RANGED_NAME",
				domain=UnitDomainType.land
			)
		elif self == UnitClassType.antiCavalry:
			return UnitClassTypeData(
				name="TXT_KEY_UNIT_CLASS_ANTI_CAVALRY_NAME",
				domain=UnitDomainType.land
			)
		elif self == UnitClassType.lightCavalry:
			return UnitClassTypeData(
				name="TXT_KEY_UNIT_CLASS_LIGHT_CAVALRY_NAME",
				domain=UnitDomainType.land
			)
		elif self == UnitClassType.heavyCavalry:
			return UnitClassTypeData(
				name="TXT_KEY_UNIT_CLASS_HEAVY_CAVALRY_NAME",
				domain=UnitDomainType.land
			)
		elif self == UnitClassType.siege:
			return UnitClassTypeData(
				name="TXT_KEY_UNIT_CLASS_SIEGE_NAME",
				domain=UnitDomainType.land
			)
		elif self == UnitClassType.navalMelee:
			return UnitClassTypeData(
				name="TXT_KEY_UNIT_CLASS_NAVAL_MELEE_NAME",
				domain=UnitDomainType.sea
			)
		elif self == UnitClassType.navalRanged:
			return UnitClassTypeData(
				name="TXT_KEY_UNIT_CLASS_NAVAL_RANGED_NAME",
				domain=UnitDomainType.sea
			)
		elif self == UnitClassType.navalRaider:
			return UnitClassTypeData(
				name="TXT_KEY_UNIT_CLASS_NAVAL_RAIDER_NAME",
				domain=UnitDomainType.sea
			)
		elif self == UnitClassType.navalCarrier:
			return UnitClassTypeData(
				name="TXT_KEY_UNIT_CLASS_NAVAL_CARRIER_NAME",
				domain=UnitDomainType.sea
			)
		elif self == UnitClassType.airFighter:
			return UnitClassTypeData(
				name="TXT_KEY_UNIT_CLASS_AIR_FIGHTER_NAME",
				domain=UnitDomainType.air
			)
		elif self == UnitClassType.airBomber:
			return UnitClassTypeData(
				name="TXT_KEY_UNIT_CLASS_AIR_BOMBER_NAME",
				domain=UnitDomainType.air
			)
		elif self == UnitClassType.support:
			return UnitClassTypeData(
				name="TXT_KEY_UNIT_CLASS_SUPPORT_NAME",
				domain=UnitDomainType.land
			)

		elif self == UnitClassType.city:
			return UnitClassTypeData(
				name="TXT_KEY_UNIT_CLASS_CITY_NAME",
				domain=UnitDomainType.land
			)

		raise InvalidEnumError(self)


class BitArray(bytearray):
	mask_for = [2**i for i in range(8)]
	inverse_mask_for = [255 - 2**i for i in range(8)]
	valid_values = (0, 1)

	def __init__(self, source, *args, **kwargs) -> None:
		if isinstance(source, int):
			source = int(source/8)
			if source % 1 != 0:
				source = int(source) + 1

		super().__init__(source, *args, **kwargs)

	def fill(self, val):
		assert val in self.valid_values
		val = 0 if val == 0 else 255
		for byte_idx in range(len(self)):
			super().__setitem__(byte_idx, val)

		return self

	def _assert_key(self, key):
		if not isinstance(key, int) and not isinstance(key, slice):
			raise KeyError(f'{self.__name__} only support int and slices as index')
		if isinstance(key, int):
			if key < 0:
				raise KeyError('Only positive keys are supported')
			if key >= len(self) * 8:
				raise IndexError(key)

	@staticmethod
	def _get_byte_index_and_offset(key: slice):
		# 7th bit in 0th byte, 8/9th bit in 1st byte
		start_byte_idx = key.start // 8
		# 23rd bit in 2nd byte, 24/25th bit in 3rd byte
		# also exclude the last index
		stop_byte_idx = ((key.stop - 1) // 8) + 1
		# if key.start is 10, then ignore first two values from first byte
		start_offset = key.start % 8
		# if key.stop is 19, then ignore last 5 values from last byte
		stop_offset = 8 - (key.stop % 8)
		return start_byte_idx, start_offset, stop_byte_idx, stop_offset

	def __getitem__(self, key) -> Union[int, list[int]]:
		if isinstance(key, slice):
			start_byte_idx, start_offset, stop_byte_idx, stop_offset = self._get_byte_index_and_offset(key)
			byte_list = super().__getitem__(slice(start_byte_idx, stop_byte_idx))
			byte_value_list = [
				int(bool(byte & self.mask_for[i]))
				for byte in byte_list
				for i in range(8)
			]

			return byte_value_list[start_offset: -stop_offset:key.step]

		self._assert_key(key)

		byte_idx = key // 8
		byte = super().__getitem__(byte_idx)
		idx = key % 8
		val = byte & self.mask_for[idx]
		return int(bool(val))

	def __setitem__(self, key, val):
		self._assert_key(key)

		if isinstance(key, slice):
			val_iter = iter(val)
			start_byte_idx, start_offset, stop_byte_idx, stop_offset = self._get_byte_index_and_offset(key)
			byte_list = super().__getitem__(slice(start_byte_idx, stop_byte_idx))

			stop_offset = (stop_byte_idx - start_byte_idx) * 8 - stop_offset
			for byte_idx in range(len(byte_list)):
				for bit_idx in range(8):
					val_idx = byte_idx * 8 + bit_idx
					if val_idx < start_offset or val_idx >= stop_offset:
						continue
					if key.step is not None and (val_idx - start_offset) % key.step != 0:
						continue

					next_val = next(val_iter)
					assert next_val in self.valid_values
					if next_val == 0:
						byte_list[byte_idx] = byte_list[byte_idx] & self.inverse_mask_for[bit_idx]
					else:
						byte_list[byte_idx] = byte_list[byte_idx] | self.mask_for[bit_idx]

			super().__setitem__(slice(start_byte_idx, stop_byte_idx), byte_list)
			return

		if val not in self.valid_values:
			raise ValueError(f"You want to put {val} in a BitArray!")

		byte_idx = key // 8
		byte = super().__getitem__(byte_idx)
		bit_idx = key % 8

		if val == 0:
			new_byte = byte & self.inverse_mask_for[bit_idx]
		else:
			new_byte = byte | self.mask_for[bit_idx]
		super().__setitem__(byte_idx, new_byte)


class UnitType:
	pass


class UnitTypeData:
	def __init__(self, name: str, baseType: Optional[UnitType], domain: UnitDomainType, effects: List[str],
				 abilities: List[UnitAbilityType], era: EraType, requiredResource: Optional[ResourceType],
				 civilization: Optional[CivilizationType], unitTasks: List[UnitTaskType],
				 defaultTask: UnitTaskType, movementType: UnitMovementType, productionCost: int,
				 purchaseCost: int, faithCost: int, maintenanceCost: int, sight: int, range: int,
				 supportDistance: int, strength: int, targetType: UnitClassType, flags: Optional[BitArray],
				 meleeAttack: int, rangedAttack: int, moves: int, requiredTech: Optional[TechType],
				 obsoleteTech: Optional[TechType], requiredCivic: Optional[CivicType],
				 upgradesFrom: List[UnitType], flavors: List[Flavor]):
		self.name = name
		self.baseType = baseType
		self.domain = domain
		self.effects = effects
		self.abilities = abilities
		self.era = era
		self.requiredResource = requiredResource
		self.civilization = civilization
		self.unitTasks = unitTasks
		self.defaultTask = defaultTask
		self.movementType = movementType
		self.productionCost = productionCost
		self.purchaseCost = purchaseCost
		self.faithCost = faithCost
		self.maintenanceCost = maintenanceCost
		self.sight = sight
		self.range = range
		self.supportDistance = supportDistance
		self.strength = strength
		self.targetType = targetType
		self.flags = flags
		self.meleeAttack = meleeAttack
		self.rangedAttack = rangedAttack
		self.moves = moves
		self.requiredTech = requiredTech
		self.obsoleteTech = obsoleteTech
		self.requiredCivic = requiredCivic
		self.upgradesFrom = upgradesFrom
		self.flavors = flavors


class UnitAutomationType(ExtendedEnum):
	none = 'none'

	build = 'build'
	explore = 'explore'


class UnitAnimationType(ExtendedEnum):
	fortify = 'fortify'
	unfortify = 'unfortify'
	attack = 'attack'
	rangeAttack = 'rangeAttack'


class UnitType(ExtendedEnum):
	# default ------------------------------
	none = 'none'

	# civilians ------------------------------
	settler = 'settler'
	builder = 'builder'
	trader = 'trader'

	# recon ------------------------------
	scout = 'scout'  # ancient
	skirmisher = 'skirmisher'  # medieval

	# melee ------------------------------
	warrior = 'warrior'  # ancient
	swordman = 'swordman'  # classical
	manAtArms = 'manAtArms'  # medieval

	# ranged ------------------------------
	slinger = 'slinger'  # ancient
	archer = 'archer'  # ancient
	crossbowman = 'crossbowman'  # medieval

	# anti-cavalry ------------------------------
	spearman = 'spearman'  # ancient
	pikeman = 'pikeman'  # medieval
	# pikeAndShot  # renaissance

	# light cavalry ------------------------------
	horseman = 'horseman'  # classical
	# courser = 'courser'  # medieval
	# cavalry  # industrial

	# heavy cavalry ------------------------------
	heavyChariot = 'heavyChariot'  # ancient
	knight = 'knight'  # medieval
	# cuirassier  # industrial

	# siege ------------------------------
	catapult = 'catapult'  # classical
	trebuchet = 'trebuchet'  # medieval
	# bombard  # renaissance

	# naval melee ------------------------------
	galley = 'galley'  # ancient
	# caravel  # renaissance
	# ironclad  # industrial

	# naval ranged ------------------------------
	quadrireme = 'quadrireme'  # classical

	# naval raider - -----------------------------
	# privateer  # renaissance

	# support - -----------------------------
	batteringRam = 'batteringRam'  # ancient
	# siegeTower  # classical
	# Military Engineer  # medieval
	# medic  # industrial

	# great persons -----------------------------
	general = 'general'
	admiral = 'admiral'
	missionary = 'missionary'
	apostle = 'apostle'
	inquisitor = 'inquisitor'
	prophet = 'prophet'

	# player overrides

	# barbarians  ------------------------------

	barbarianWarrior = 'barbarianWarrior'
	barbarianArcher = 'barbarianArcher'

	@classmethod
	def greatPersons(cls) -> List[UnitType]:
		return [UnitType.general, UnitType.admiral, UnitType.missionary, UnitType.apostle, UnitType.inquisitor, UnitType.prophet]

	def title(self) -> str:  # cannot use 'name'
		return self._data().name

	def baseType(self) -> Optional[UnitType]:
		return self._data().baseType

	def unitClass(self) -> UnitClassType:
		return self._data().targetType

	def civilization(self):
		return self._data().civilization

	def era(self) -> EraType:
		return self._data().era

	def requiredCivic(self) -> CivicType:
		return self._data().requiredCivic

	def requiredTech(self) -> TechType:
		return self._data().requiredTech

	def obsoleteTech(self) -> TechType:
		return self._data().obsoleteTech

	def upgradesTo(self) -> List[UnitType]:
		types: List[UnitType] = []

		for unitType in list(UnitType):
			if self in unitType.upgradesFrom():
				types.append(unitType)

		return types

	def upgradesFrom(self) -> List[UnitType]:
		return self._data().upgradesFrom

	def defaultTask(self) -> UnitTaskType:
		return self._data().defaultTask

	def unitTasks(self) -> List[UnitTaskType]:
		return self._data().unitTasks

	def domain(self) -> UnitDomainType:
		return self._data().domain

	def moves(self) -> int:
		return self._data().moves

	def buildCharges(self) -> int:
		if self == UnitType.builder:
			return 3

		return 0

	def range(self) -> int:
		return self._data().range

	def productionCost(self) -> int:
		return self._data().productionCost

	def requiredResource(self) -> Optional[ResourceType]:
		return self._data().requiredResource

	def meleeStrength(self) -> int:
		return self._data().meleeAttack

	def rangedStrength(self) -> int:
		if self.range() > 0:
			return self._data().rangedAttack

		return 0

	def healingAdjacentUnits(self) -> int:
		if self.hasAbility(UnitAbilityType.canHeal):
			return 20

		return 0

	def canMoveInRivalTerritory(self) -> bool:
		return self.hasAbility(UnitAbilityType.canMoveInRivalTerritory)

	def power(self) -> int:
		# ***************
		# Main Factors - Strength & Moves
		# ***************

		#  We want a Unit that has twice the strength to be roughly worth 3x as much in regard to Power
		powerVal = int(pow(float(self.meleeStrength()), 1.5))

		# Ranged Strength
		rangedPower = int(pow(float(self.rangedStrength()), 1.45))

		# Naval ranged attacks are less useful
		if self.domain() == UnitDomainType.sea:
			rangedPower /= 2

		if rangedPower > 0:
			powerVal = rangedPower

		# We want Movement rate to be important, but not a dominating factor; a Unit with double the moves of a
		# similarly-strengthed Unit should be ~1.5x as Powerful
		powerVal = int(float(powerVal) * pow(float(self.moves()), 0.3))

		# ***************
		# ability modifiers
		# ***************

		# for ability in self.abilities():
		# FIXME

		return powerVal

	def maintenanceCost(self) -> int:
		return self._data().maintenanceCost

	def canFound(self) -> bool:
		return self.hasAbility(UnitAbilityType.canFound)

	def hasAbility(self, ability: UnitAbilityType) -> bool:
		return ability in self.abilities()

	def abilities(self) -> List[UnitAbilityType]:
		return self._data().abilities

	def sight(self) -> int:
		return self._data().sight

	def movementType(self) -> UnitMovementType:
		return self._data().movementType

	def _flavors(self) -> List[Flavor]:
		return self._data().flavors

	def flavor(self, flavorType: FlavorType) -> int:
		item = next((flavor for flavor in self._flavors() if flavor.flavorType == flavorType), None)

		if item is not None:
			return item.value

		return 0

	def workRate(self) -> int:
		# in civ6 builders are building improvements immediately
		if self == UnitType.builder:
			return 1000  # used to be 100

		return 0

	def canBuild(self, buildType: BuildType) -> bool:
		if buildType == BuildType.repair or buildType == BuildType.removeRoad or buildType == BuildType.farm or \
			buildType == BuildType.mine or buildType == BuildType.quarry or buildType == BuildType.plantation or \
			buildType == BuildType.camp or buildType == BuildType.pasture or buildType == BuildType.fishingBoats or \
			buildType == BuildType.removeForest or buildType == BuildType.removeRainforest or \
			buildType == BuildType.removeMarsh:
			return self.hasAbility(UnitAbilityType.canImprove)

		if buildType == BuildType.ancientRoad or buildType == BuildType.classicalRoad:
			return self.hasAbility(UnitAbilityType.canBuildRoads)

		return False

	def canPillage(self) -> bool:
		if self.unitClass() == UnitClassType.civilian:
			return False

		return True

	def captureType(self) -> Optional[UnitType]:
		if self == UnitType.builder or self == UnitType.settler:
			return UnitType.builder

		return None

	def purchaseCost(self) -> int:
		return self._data().purchaseCost

	def faithCost(self) -> int:
		return self._data().faithCost

	def unitMapType(self) -> UnitMapType:
		if self.unitClass() == UnitClassType.civilian:
			return UnitMapType.civilian
		else:
			return UnitMapType.combat

	def _data(self) -> UnitTypeData:
		# https://civilization.fandom.com/wiki/Module:Data/Civ5/BNW/Unit_Values

		# default ------------------------------
		if self == UnitType.none:
			return UnitTypeData(
				name='...',
				baseType=None,
				domain=UnitDomainType.land,
				effects=[],
				abilities=[],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[],
				defaultTask=UnitTaskType.none,
				movementType=UnitMovementType.walk,
				productionCost=0,
				purchaseCost=0,
				faithCost=0,
				maintenanceCost=0,
				sight=0,
				range=0,
				supportDistance=0,
				strength=0,
				targetType=UnitClassType.civilian,
				flags=None,
				meleeAttack=0,
				rangedAttack=0,
				moves=0,
				requiredTech=None,
				requiredCivic=None,
				obsoleteTech=None,
				upgradesFrom=[],
				flavors=[]
			)

		# civilians ------------------------------
		elif self == UnitType.settler:
			return UnitTypeData(
				name=_("TXT_KEY_UNIT_SETTLER_NAME"),
				baseType=UnitType.settler,
				domain=UnitDomainType.land,
				effects=[
					"TXT_KEY_UNIT_SETTLER_EFFECT1",
					"TXT_KEY_UNIT_SETTLER_EFFECT2"
				],
				abilities=[UnitAbilityType.canFound],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[UnitTaskType.settle],
				defaultTask=UnitTaskType.settle,
				movementType=UnitMovementType.walk,
				productionCost=80,
				purchaseCost=320,
				faithCost=-1,
				maintenanceCost=0,
				sight=3,
				range=0,
				supportDistance=0,
				strength=10,
				targetType=UnitClassType.civilian,
				flags=None,
				meleeAttack=0,
				rangedAttack=0,
				moves=2,
				requiredTech=None,
				obsoleteTech=None,
				requiredCivic=None,
				upgradesFrom=[],
				flavors=[
					Flavor(FlavorType.expansion, value=21)
				]
			)
		elif self == UnitType.builder:
			return UnitTypeData(
				name=_("TXT_KEY_UNIT_BUILDER_NAME"),
				baseType=UnitType.builder,
				domain=UnitDomainType.land,
				effects=[
					"TXT_KEY_UNIT_BUILDER_EFFECT1",
					"TXT_KEY_UNIT_BUILDER_EFFECT2"
				],
				abilities=[UnitAbilityType.canImprove],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[UnitTaskType.work],
				defaultTask=UnitTaskType.work,
				movementType=UnitMovementType.walk,
				productionCost=50,
				purchaseCost=200,
				faithCost=-1,
				maintenanceCost=0,
				sight=2,
				range=0,
				supportDistance=0,
				strength=10,
				targetType=UnitClassType.civilian,
				flags=None,
				meleeAttack=0,
				rangedAttack=0,
				moves=2,
				requiredTech=None,
				obsoleteTech=None,
				requiredCivic=None,
				upgradesFrom=[],
				flavors=[
					Flavor(FlavorType.tileImprovement, value=30),
					Flavor(FlavorType.amenities, value=7),
					Flavor(FlavorType.expansion, value=4),
					Flavor(FlavorType.growth, value=4),
					Flavor(FlavorType.gold, value=4),
					Flavor(FlavorType.production, value=4),
					Flavor(FlavorType.science, value=2),
					Flavor(FlavorType.offense, value=1),
					Flavor(FlavorType.defense, value=1)
				]
			)
		elif self == UnitType.trader:
			return UnitTypeData(
				name=_("TXT_KEY_UNIT_TRADER_NAME"),
				baseType=UnitType.trader,
				domain=UnitDomainType.land,
				effects=[
					"TXT_KEY_UNIT_TRADER_EFFECT1",
					"TXT_KEY_UNIT_TRADER_EFFECT2"
				],
				abilities=[
					UnitAbilityType.canEstablishTradeRoute,
					UnitAbilityType.canMoveInRivalTerritory
				],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[UnitTaskType.trade],
				defaultTask=UnitTaskType.trade,
				movementType=UnitMovementType.walk,
				productionCost=40,
				purchaseCost=160,
				faithCost=-1,
				maintenanceCost=0,
				sight=2,
				range=0,
				supportDistance=0,
				strength=10,
				targetType=UnitClassType.civilian,
				flags=None,
				meleeAttack=0,
				rangedAttack=0,
				moves=1,
				requiredTech=None,
				obsoleteTech=None,
				requiredCivic=CivicType.foreignTrade,
				upgradesFrom=[],
				flavors=[
					Flavor(FlavorType.gold, value=10)
				]
			)

		# recon ------------------------------
		elif self == UnitType.scout:
			return UnitTypeData(
				name=_("TXT_KEY_UNIT_SCOUT_NAME"),
				baseType=UnitType.scout,
				domain=UnitDomainType.land,
				effects=[
					"TXT_KEY_UNIT_SCOUT_EFFECT1"
				],
				abilities=[UnitAbilityType.experienceFromTribal],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[UnitTaskType.explore],
				defaultTask=UnitTaskType.explore,
				movementType=UnitMovementType.walk,
				productionCost=30,
				purchaseCost=120,
				faithCost=-1,
				maintenanceCost=0,
				sight=2,
				range=0,
				supportDistance=0,
				strength=10,
				targetType=UnitClassType.recon,
				flags=None,
				meleeAttack=10,
				rangedAttack=0,
				moves=3,
				requiredTech=None,
				obsoleteTech=None,
				requiredCivic=None,
				upgradesFrom=[],
				flavors=[
					Flavor(FlavorType.recon, value=8),
					Flavor(FlavorType.defense, value=2)
				]
			)
		elif self == UnitType.skirmisher:
			return UnitTypeData(
				name=_("TXT_KEY_UNIT_SKIRMISHER_NAME"),
				baseType=UnitType.skirmisher,
				domain=UnitDomainType.land,
				effects=[
					"TXT_KEY_UNIT_SKIRMISHER_EFFECT1",
					"TXT_KEY_UNIT_SKIRMISHER_EFFECT2"
				],
				abilities=[UnitAbilityType.canCapture],
				era=EraType.medieval,
				requiredResource=None,
				civilization=None,
				unitTasks=[UnitTaskType.attack, UnitTaskType.defense, UnitTaskType.explore],
				defaultTask=UnitTaskType.attack,
				movementType=UnitMovementType.walk,
				productionCost=150,
				purchaseCost=600,
				faithCost=-1,
				maintenanceCost=2,
				sight=2,
				range=1,
				supportDistance=0,
				strength=10,
				targetType=UnitClassType.recon,
				flags=None,
				meleeAttack=20,
				rangedAttack=30,
				moves=3,
				requiredTech=TechType.machinery,
				obsoleteTech=None,
				requiredCivic=None,
				upgradesFrom=[UnitType.scout],
				flavors=[
					Flavor(FlavorType.recon, value=8),
					Flavor(FlavorType.offense, value=1),
					Flavor(FlavorType.defense, value=1)
				]
			)

		# melee ------------------------------
		elif self == UnitType.warrior:
			return UnitTypeData(
				name=_("TXT_KEY_UNIT_WARRIOR_NAME"),
				baseType=UnitType.warrior,
				domain=UnitDomainType.land,
				effects=[
					"TXT_KEY_UNIT_WARRIOR_EFFECT1"
				],
				abilities=[UnitAbilityType.canCapture],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[UnitTaskType.attack, UnitTaskType.defense, UnitTaskType.explore],
				defaultTask=UnitTaskType.attack,
				movementType=UnitMovementType.walk,
				productionCost=40,
				purchaseCost=160,
				faithCost=-1,
				maintenanceCost=0,
				sight=2,
				range=0,
				supportDistance=0,
				strength=10,
				targetType=UnitClassType.melee,
				flags=None,
				meleeAttack=20,
				rangedAttack=0,
				moves=2,
				requiredTech=None,
				obsoleteTech=None,
				requiredCivic=None,
				upgradesFrom=[],
				flavors=[
					Flavor(FlavorType.recon, value=1),
					Flavor(FlavorType.offense, value=2),
					Flavor(FlavorType.defense, value=2)
				]
			)
		elif self == UnitType.swordman:
			return UnitTypeData(
				name=_("TXT_KEY_UNIT_SWORDMAN_NAME"),
				baseType=UnitType.swordman,
				domain=UnitDomainType.land,
				effects=[
					"TXT_KEY_UNIT_SWORDMAN_EFFECT1"
				],
				abilities=[UnitAbilityType.canCapture],
				era=EraType.classical,
				requiredResource=ResourceType.iron,
				civilization=None,
				unitTasks=[UnitTaskType.attack, UnitTaskType.defense, UnitTaskType.explore],
				defaultTask=UnitTaskType.attack,
				movementType=UnitMovementType.walk,
				productionCost=90,
				purchaseCost=360,
				faithCost=-1,
				maintenanceCost=2,
				sight=2,
				range=0,
				supportDistance=0,
				strength=10,
				targetType=UnitClassType.melee,
				flags=None,
				meleeAttack=35,
				rangedAttack=0,
				moves=2,
				requiredTech=TechType.ironWorking,
				obsoleteTech=None,
				requiredCivic=None,
				upgradesFrom=[UnitType.warrior],
				flavors=[
					Flavor(FlavorType.offense, value=6),
					Flavor(FlavorType.defense, value=6)
				]
			)
		elif self == UnitType.manAtArms:
			return UnitTypeData(
				name=_("TXT_KEY_UNIT_MAN_AT_ARMS_NAME"),
				baseType=UnitType.manAtArms,
				domain=UnitDomainType.land,
				effects=[
					"TXT_KEY_UNIT_MAN_AT_ARMS_EFFECT1"
				],
				abilities=[UnitAbilityType.canCapture],
				era=EraType.medieval,
				requiredResource=ResourceType.iron,
				civilization=None,
				unitTasks=[UnitTaskType.attack, UnitTaskType.defense, UnitTaskType.explore],
				defaultTask=UnitTaskType.attack,
				movementType=UnitMovementType.walk,
				productionCost=160,
				purchaseCost=640,
				faithCost=-1,
				maintenanceCost=3,
				sight=2,
				range=0,
				supportDistance=0,
				strength=10,
				targetType=UnitClassType.melee,
				flags=None,
				meleeAttack=45,
				rangedAttack=0,
				moves=2,
				requiredTech=TechType.apprenticeship,
				obsoleteTech=None,
				requiredCivic=None,
				upgradesFrom=[UnitType.swordman],
				flavors=[
					Flavor(FlavorType.recon, value=1),
					Flavor(FlavorType.offense, value=8),
					Flavor(FlavorType.defense, value=1)
				]
			)

		# ranged ------------------------------
		elif self == UnitType.slinger:
			return UnitTypeData(
				name=_("TXT_KEY_UNIT_SLINGER_NAME"),
				baseType=UnitType.slinger,
				domain=UnitDomainType.land,
				effects=[
					"TXT_KEY_UNIT_SLINGER_EFFECT1"
				],
				abilities=[UnitAbilityType.canCapture],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[UnitTaskType.ranged],
				defaultTask=UnitTaskType.ranged,
				movementType=UnitMovementType.walk,
				productionCost=35,
				purchaseCost=140,
				faithCost=-1,
				maintenanceCost=0,
				sight=2,
				range=1,
				supportDistance=1,
				strength=10,
				targetType=UnitClassType.ranged,
				flags=None,
				meleeAttack=5,
				rangedAttack=15,
				moves=2,
				requiredTech=None,
				obsoleteTech=None,
				requiredCivic=None,
				upgradesFrom=[],
				flavors=[
					Flavor(FlavorType.ranged, value=8),
					Flavor(FlavorType.recon, value=5),
					Flavor(FlavorType.offense, value=2),
					Flavor(FlavorType.defense, value=1)
				]
			)
		elif self == UnitType.archer:
			return UnitTypeData(
				name=_("TXT_KEY_UNIT_ARCHER_NAME"),
				baseType=UnitType.archer,
				domain=UnitDomainType.land,
				effects=[
					"TXT_KEY_UNIT_ARCHER_EFFECT1"
				],
				abilities=[UnitAbilityType.canCapture],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[UnitTaskType.ranged],
				defaultTask=UnitTaskType.ranged,
				movementType=UnitMovementType.walk,
				productionCost=60,
				purchaseCost=240,
				faithCost=-1,
				maintenanceCost=1,
				sight=2,
				range=2,
				supportDistance=2,
				strength=10,
				targetType=UnitClassType.ranged,
				flags=None,
				meleeAttack=15,
				rangedAttack=25,
				moves=2,
				requiredTech=TechType.archery,
				obsoleteTech=None,
				requiredCivic=None,
				upgradesFrom=[UnitType.slinger],
				flavors=[
					Flavor(FlavorType.ranged, value=6),
					Flavor(FlavorType.recon, value=3),
					Flavor(FlavorType.offense, value=2),
					Flavor(FlavorType.defense, value=2)
				]
			)
		elif self == UnitType.crossbowman:
			return UnitTypeData(
				name=_("TXT_KEY_UNIT_CROSSBOWMAN_NAME"),
				baseType=UnitType.crossbowman,
				domain=UnitDomainType.land,
				effects=[
					"TXT_KEY_UNIT_CROSSBOWMAN_EFFECT1",
					"TXT_KEY_UNIT_CROSSBOWMAN_EFFECT2"
				],
				abilities=[UnitAbilityType.canCapture],
				era=EraType.medieval,
				requiredResource=None,
				civilization=None,
				unitTasks=[UnitTaskType.ranged],
				defaultTask=UnitTaskType.ranged,
				movementType=UnitMovementType.walk,
				productionCost=180,
				purchaseCost=720,
				faithCost=-1,
				maintenanceCost=3,
				sight=2,
				range=2,
				supportDistance=0,
				strength=10,
				targetType=UnitClassType.ranged,
				flags=None,
				meleeAttack=30,
				rangedAttack=40,
				moves=2,
				requiredTech=TechType.machinery,
				obsoleteTech=None,
				requiredCivic=None,
				upgradesFrom=[UnitType.archer],
				flavors=[
					Flavor(FlavorType.recon, value=1),
					Flavor(FlavorType.offense, value=7),
					Flavor(FlavorType.defense, value=2)
				]
			)

		# anti-cavalry ------------------------------
		elif self == UnitType.spearman:
			return UnitTypeData(
				name=_("TXT_KEY_UNIT_SPEARMAN_NAME"),
				baseType=UnitType.spearman,
				domain=UnitDomainType.land,
				effects=[
					"TXT_KEY_UNIT_SPEARMAN_EFFECT1"
				],
				abilities=[UnitAbilityType.canCapture],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[UnitTaskType.attack, UnitTaskType.defense],
				defaultTask=UnitTaskType.defense,
				movementType=UnitMovementType.walk,
				productionCost=65,
				purchaseCost=260,
				faithCost=-1,
				maintenanceCost=1,
				sight=2,
				range=0,
				supportDistance=0,
				strength=10,
				targetType=UnitClassType.antiCavalry,
				flags=None,
				meleeAttack=25,
				rangedAttack=0,
				moves=2,
				requiredTech=TechType.bronzeWorking,
				obsoleteTech=None,
				requiredCivic=None,
				upgradesFrom=[],
				flavors=[
					Flavor(FlavorType.defense, value=4),
					Flavor(FlavorType.recon, value=2),
					Flavor(FlavorType.offense, value=2)
				]
			)
		elif self == UnitType.pikeman:
			return UnitTypeData(
				name=_("TXT_KEY_UNIT_PIKEMAN_NAME"),
				baseType=UnitType.pikeman,
				domain=UnitDomainType.land,
				effects=[
					"TXT_KEY_UNIT_PIKEMAN_EFFECT1"
				],
				abilities=[UnitAbilityType.canCapture],
				era=EraType.medieval,
				requiredResource=None,
				civilization=None,
				unitTasks=[UnitTaskType.attack, UnitTaskType.defense, UnitTaskType.explore],
				defaultTask=UnitTaskType.attack,
				movementType=UnitMovementType.walk,
				productionCost=180,
				purchaseCost=720,
				faithCost=-1,
				maintenanceCost=2,
				sight=2,
				range=0,
				supportDistance=0,
				strength=10,
				targetType=UnitClassType.antiCavalry,
				flags=None,
				meleeAttack=45,
				rangedAttack=0,
				moves=2,
				requiredTech=TechType.militaryTactics,
				obsoleteTech=None,
				requiredCivic=None,
				upgradesFrom=[UnitType.spearman],
				flavors=[
					Flavor(FlavorType.recon, value=1),
					Flavor(FlavorType.offense, value=3),
					Flavor(FlavorType.defense, value=6)
				]
			)
		# pikeAndShot  # renaissance

		# light cavalry ------------------------------
		elif self == UnitType.horseman:
			return UnitTypeData(
				name=_("TXT_KEY_UNIT_HORSEMAN_NAME"),
				baseType=UnitType.horseman,
				domain=UnitDomainType.land,
				effects=[
					"TXT_KEY_UNIT_HORSEMAN_EFFECT1",
					"TXT_KEY_UNIT_HORSEMAN_EFFECT2"
				],
				abilities=[
					UnitAbilityType.canCapture,
					UnitAbilityType.ignoreZoneOfControl
				],
				era=EraType.classical,
				requiredResource=None,
				civilization=None,
				unitTasks=[UnitTaskType.attack, UnitTaskType.explore],
				defaultTask=UnitTaskType.attack,
				movementType=UnitMovementType.walk,
				productionCost=80,
				purchaseCost=320,
				faithCost=-1,
				maintenanceCost=2,
				sight=2,
				range=0,
				supportDistance=0,
				strength=10,
				targetType=UnitClassType.lightCavalry,
				flags=None,
				meleeAttack=36,
				rangedAttack=0,
				moves=4,
				requiredTech=TechType.horsebackRiding,
				obsoleteTech=None,
				requiredCivic=None,
				upgradesFrom=[],
				flavors=[
					Flavor(FlavorType.offense, value=6),
					Flavor(FlavorType.defense, value=2),
					Flavor(FlavorType.mobile, value=4)
				]
			)
		# elif self == UnitType.courser:
		# 	return UnitTypeData(
		# 		name='...',
		# 		baseType=None,
		# 		domain=UnitDomainType.land,
		# 		effects=[],
		# 		abilities=[],
		# 		era=EraType.ancient,
		# 		requiredResource=None,
		# 		civilization=None,
		# 		unitTasks=[],
		# 		defaultTask=UnitTaskType.none,
		# 		movementType=UnitMovementType.walk,
		# 		productionCost=0,
		# 		purchaseCost=0,
		# 		faithCost=0,
		# 		maintenanceCost=0,
		# 		sight=0,
		# 		range=0,
		# 		supportDistance=0,
		# 		strength=0,
		# 		targetType=UnitClassType.civilian,
		# 		flags=None,
		# 		meleeAttack=0,
		# 		rangedAttack=0,
		# 		moves=0,
		# 		requiredTech=None,
		# 		requiredCivic=None,
		# 		obsoleteTech=None,
		# 		upgradesFrom=None,
		# 		flavors=[]
		# 	)
		# cavalry  # industrial

		# heavy cavalry ------------------------------
		elif self == UnitType.heavyChariot:
			return UnitTypeData(
				name=_("TXT_KEY_UNIT_HEAVY_CHARIOT_NAME"),
				baseType=UnitType.heavyChariot,
				domain=UnitDomainType.land,
				effects=[
					"TXT_KEY_UNIT_HEAVY_CHARIOT_EFFECT1",
					"TXT_KEY_UNIT_HEAVY_CHARIOT_EFFECT2"
				],
				abilities=[UnitAbilityType.canCapture],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[UnitTaskType.attack, UnitTaskType.defense, UnitTaskType.explore],
				defaultTask=UnitTaskType.attack,
				movementType=UnitMovementType.walk,
				productionCost=65,
				purchaseCost=260,
				faithCost=-1,
				maintenanceCost=1,
				sight=2,
				range=0,
				supportDistance=0,
				strength=10,
				targetType=UnitClassType.lightCavalry,
				flags=None,
				meleeAttack=28,
				rangedAttack=0,
				moves=2,
				requiredTech=TechType.wheel,
				obsoleteTech=None,
				requiredCivic=None,
				upgradesFrom=[],
				flavors=[
					Flavor(FlavorType.recon, value=9),
					Flavor(FlavorType.ranged, value=5),
					Flavor(FlavorType.mobile, value=10),
					Flavor(FlavorType.offense, value=3),
					Flavor(FlavorType.defense, value=6)
				]
			)
		elif self == UnitType.knight:
			return UnitTypeData(
				name=_("TXT_KEY_UNIT_KNIGHT_NAME"),
				baseType=UnitType.knight,
				domain=UnitDomainType.land,
				effects=[
					"TXT_KEY_UNIT_KNIGHT_EFFECT1"
				],
				abilities=[UnitAbilityType.canCapture],
				era=EraType.medieval,
				requiredResource=None,
				civilization=None,
				unitTasks=[UnitTaskType.attack, UnitTaskType.defense, UnitTaskType.explore],
				defaultTask=UnitTaskType.attack,
				movementType=UnitMovementType.walk,
				productionCost=220,
				purchaseCost=880,
				faithCost=-1,
				maintenanceCost=4,
				sight=2,
				range=0,
				supportDistance=0,
				strength=10,
				targetType=UnitClassType.heavyCavalry,
				flags=None,
				meleeAttack=50,
				rangedAttack=0,
				moves=4,
				requiredTech=TechType.stirrups,
				obsoleteTech=None,
				requiredCivic=None,
				upgradesFrom=[UnitType.heavyChariot],
				flavors=[
					Flavor(FlavorType.recon, value=1),
					Flavor(FlavorType.offense, value=9)
				]
			)
		# cuirassier  # industrial

		# siege ------------------------------
		elif self == UnitType.catapult:
			return UnitTypeData(
				name=_("TXT_KEY_UNIT_CATAPULT_NAME"),
				baseType=UnitType.catapult,
				domain=UnitDomainType.land,
				effects=[
					"TXT_KEY_UNIT_CATAPULT_EFFECT1",
					"TXT_KEY_UNIT_CATAPULT_EFFECT2",
					"TXT_KEY_UNIT_CATAPULT_EFFECT3"
				],
				abilities=[UnitAbilityType.canCapture],
				era=EraType.classical,
				requiredResource=None,
				civilization=None,
				unitTasks=[UnitTaskType.attack, UnitTaskType.ranged, UnitTaskType.cityBombard],
				defaultTask=UnitTaskType.ranged,
				movementType=UnitMovementType.walk,
				productionCost=120,
				purchaseCost=480,
				faithCost=-1,
				maintenanceCost=2,
				sight=2,
				range=2,
				supportDistance=2,
				strength=10,
				targetType=UnitClassType.ranged,
				flags=None,
				meleeAttack=25,
				rangedAttack=35,
				moves=2,
				requiredTech=TechType.engineering,
				obsoleteTech=None,
				requiredCivic=None,
				upgradesFrom=[],
				flavors=[
					Flavor(FlavorType.ranged, value=8),
					Flavor(FlavorType.offense, value=2)
				]
			)
		elif self == UnitType.trebuchet:
			return UnitTypeData(
				name=_("TXT_KEY_UNIT_TREBUCHET_NAME"),
				baseType=UnitType.trebuchet,
				domain=UnitDomainType.land,
				effects=[
					"TXT_KEY_UNIT_TREBUCHET_EFFECT1",
					"TXT_KEY_UNIT_TREBUCHET_EFFECT2",
					"TXT_KEY_UNIT_TREBUCHET_EFFECT3"
				],
				abilities=[],
				era=EraType.classical,
				requiredResource=None,
				civilization=None,
				unitTasks=[UnitTaskType.cityAttack],
				defaultTask=UnitTaskType.cityAttack,
				movementType=UnitMovementType.walk,
				productionCost=200,
				purchaseCost=800,
				faithCost=-1,
				maintenanceCost=3,
				sight=2,
				range=2,
				supportDistance=0,
				strength=10,
				targetType=UnitClassType.siege,
				flags=None,
				meleeAttack=35,
				rangedAttack=45,
				moves=2,
				requiredTech=TechType.militaryEngineering,
				obsoleteTech=None,
				requiredCivic=None,
				upgradesFrom=[UnitType.catapult],
				flavors=[
					Flavor(FlavorType.ranged, value=8),
					Flavor(FlavorType.offense, value=2)
				]
			)
		# bombard  # renaissance

		# naval melee ------------------------------
		elif self == UnitType.galley:
			return UnitTypeData(
				name=_("TXT_KEY_UNIT_GALLEY_NAME"),
				baseType=UnitType.galley,
				domain=UnitDomainType.sea,
				effects=[
					"TXT_KEY_UNIT_GALLEY_EFFECT1",
					"TXT_KEY_UNIT_GALLEY_EFFECT2"
				],
				abilities=[
					UnitAbilityType.oceanImpassable,
					UnitAbilityType.canCapture
				],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[
					UnitTaskType.exploreSea,
					UnitTaskType.attackSea,
					UnitTaskType.escortSea,
					UnitTaskType.reserveSea
				],
				defaultTask=UnitTaskType.attackSea,
				movementType=UnitMovementType.swimShallow,
				productionCost=65,
				purchaseCost=260,
				faithCost=-1,
				maintenanceCost=1,
				sight=2,
				range=0,
				supportDistance=0,
				strength=10,
				targetType=UnitClassType.navalMelee,
				flags=None,
				meleeAttack=30,
				rangedAttack=0,
				moves=3,
				requiredTech=TechType.sailing,
				obsoleteTech=None,
				requiredCivic=None,
				upgradesFrom=[],
				flavors=[
					Flavor(FlavorType.naval, value=2),
					Flavor(FlavorType.navalRecon, value=1),
				]
			)
		# caravel  # renaissance
		# ironclad  # industrial
		#
		# naval ranged ------------------------------
		elif self == UnitType.quadrireme:
			return UnitTypeData(
				name=_("TXT_KEY_UNIT_QUADRIREME_NAME"),
				baseType=UnitType.quadrireme,
				domain=UnitDomainType.sea,
				effects=[
					"TXT_KEY_UNIT_QUADRIREME_EFFECT1",
					"TXT_KEY_UNIT_QUADRIREME_EFFECT2"
				],
				abilities=[UnitAbilityType.oceanImpassable],
				era=EraType.classical,
				requiredResource=None,
				civilization=None,
				unitTasks=[UnitTaskType.attackSea, UnitTaskType.escortSea, UnitTaskType.reserveSea],
				defaultTask=UnitTaskType.attackSea,
				movementType=UnitMovementType.swimShallow,
				productionCost=120,
				purchaseCost=480,
				faithCost=-1,
				maintenanceCost=2,
				sight=2,
				range=1,
				supportDistance=1,
				strength=10,
				targetType=UnitClassType.navalRanged,
				flags=None,
				meleeAttack=20,
				rangedAttack=25,
				moves=3,
				requiredTech=TechType.shipBuilding,
				obsoleteTech=None,
				requiredCivic=None,
				upgradesFrom=[],
				flavors=[
					Flavor(FlavorType.naval, value=6),
					Flavor(FlavorType.navalRecon, value=2),
				]
			)

		elif self == UnitType.batteringRam:
			#
			return UnitTypeData(
				name="TXT_KEY_UNIT_BATTERING_RAM_NAME",
				baseType=UnitType.batteringRam,
				domain=UnitDomainType.land,
				effects=[
					"TXT_KEY_UNIT_BATTERING_RAM_EFFECT1",
					"TXT_KEY_UNIT_BATTERING_RAM_EFFECT2"
				],
				abilities=[],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[UnitTaskType.cityAttack],
				defaultTask=UnitTaskType.cityAttack,
				movementType=UnitMovementType.walk,
				productionCost=65,
				purchaseCost=260,
				faithCost=-1,
				maintenanceCost=1,
				sight=2,
				range=0,
				supportDistance=0,
				strength=10,
				targetType=UnitClassType.support,
				flags=None,
				meleeAttack=0,
				rangedAttack=0,
				moves=2,
				requiredTech=TechType.masonry,
				obsoleteTech=None,
				requiredCivic=None,
				upgradesFrom=[],
				flavors=[
					Flavor(FlavorType.expansion, value=3),
					Flavor(FlavorType.offense, value=7)
				]
			)

		# great persons ----------------------------

		elif self == UnitType.general:
			#
			return UnitTypeData(
				name="TXT_KEY_UNIT_GENERAL_NAME",
				baseType=UnitType.general,
				domain=UnitDomainType.land,
				effects=[
					"TXT_KEY_UNIT_GENERAL_EFFECT1"
				],
				abilities=[],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[],
				defaultTask=UnitTaskType.unknown,
				movementType=UnitMovementType.walk,
				productionCost=-1,
				purchaseCost=-1,
				faithCost=-1,
				maintenanceCost=0,
				sight=2,
				range=0,
				supportDistance=0,
				strength=0,
				targetType=UnitClassType.civilian,
				flags=None,
				meleeAttack=0,
				rangedAttack=0,
				moves=3,
				requiredTech=None,
				obsoleteTech=None,
				requiredCivic=None,
				upgradesFrom=[],
				flavors=[
					Flavor(FlavorType.offense, value=1),
					Flavor(FlavorType.defense, value=1)
				]
			)
		elif self == UnitType.missionary:
			#
			return UnitTypeData(
				name="TXT_KEY_UNIT_MISSIONARY_NAME",
				baseType=UnitType.missionary,
				domain=UnitDomainType.land,
				effects=[
					"TXT_KEY_UNIT_MISSIONARY_EFFECT1"
				],
				abilities=[],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[],
				defaultTask=UnitTaskType.unknown,
				movementType=UnitMovementType.walk,
				productionCost=-1,
				purchaseCost=-1,
				faithCost=-1,
				maintenanceCost=0,
				sight=2,
				range=0,
				supportDistance=0,
				strength=0,
				targetType=UnitClassType.civilian,
				flags=None,
				meleeAttack=0,
				rangedAttack=0,
				moves=3,
				requiredTech=None,
				obsoleteTech=None,
				requiredCivic=None,
				upgradesFrom=[],
				flavors=[
					Flavor(FlavorType.religion, value=1)
				]
			)
		elif self == UnitType.apostle:
			#
			return UnitTypeData(
				name="TXT_KEY_UNIT_APOSTLE_NAME",
				baseType=UnitType.apostle,
				domain=UnitDomainType.land,
				effects=[
					"TXT_KEY_UNIT_APOSTLEY_EFFECT1"
				],
				abilities=[],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[],
				defaultTask=UnitTaskType.unknown,
				movementType=UnitMovementType.walk,
				productionCost=-1,
				purchaseCost=-1,
				faithCost=-1,
				maintenanceCost=0,
				sight=2,
				range=0,
				supportDistance=0,
				strength=0,
				targetType=UnitClassType.civilian,
				flags=None,
				meleeAttack=0,
				rangedAttack=0,
				moves=3,
				requiredTech=None,
				obsoleteTech=None,
				requiredCivic=None,
				upgradesFrom=[],
				flavors=[
					Flavor(FlavorType.religion, value=1)
				]
			)
		elif self == UnitType.inquisitor:
			#
			return UnitTypeData(
				name="TXT_KEY_UNIT_INQUISITOR_NAME",
				baseType=UnitType.inquisitor,
				domain=UnitDomainType.land,
				effects=[
					"TXT_KEY_UNIT_INQUISITOR_EFFECT1"
				],
				abilities=[],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[],
				defaultTask=UnitTaskType.unknown,
				movementType=UnitMovementType.walk,
				productionCost=-1,
				purchaseCost=-1,
				faithCost=-1,
				maintenanceCost=0,
				sight=2,
				range=0,
				supportDistance=0,
				strength=0,
				targetType=UnitClassType.civilian,
				flags=None,
				meleeAttack=0,
				rangedAttack=0,
				moves=3,
				requiredTech=None,
				obsoleteTech=None,
				requiredCivic=None,
				upgradesFrom=[],
				flavors=[
					Flavor(FlavorType.religion, value=1)
				]
			)
		elif self == UnitType.prophet:
			# https://civilization.fandom.com/wiki/Great_Prophet_(Civ6)
			return UnitTypeData(
				name="TXT_KEY_UNIT_PROPHET_NAME",
				baseType=UnitType.prophet,
				domain=UnitDomainType.land,
				effects=[
					"TXT_KEY_UNIT_PROPHET_EFFECT1"
				],
				abilities=[],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[],
				defaultTask=UnitTaskType.unknown,
				movementType=UnitMovementType.walk,
				productionCost=-1,
				purchaseCost=-1,
				faithCost=-1,
				maintenanceCost=0,
				sight=2,
				range=0,
				supportDistance=0,
				strength=0,
				targetType=UnitClassType.civilian,
				flags=None,
				meleeAttack=0,
				rangedAttack=0,
				moves=3,
				requiredTech=None,
				obsoleteTech=None,
				requiredCivic=None,
				upgradesFrom=[],
				flavors=[
					Flavor(FlavorType.religion, value=1)
				]
			)
		elif self == UnitType.admiral:
			# https://civilization.fandom.com/wiki/Great_Admiral_(Civ6)
			return UnitTypeData(
				name="TXT_KEY_UNIT_ADMIRAL_NAME",
				baseType=UnitType.admiral,
				domain=UnitDomainType.land,
				effects=[
					"TXT_KEY_UNIT_ADMIRAL_EFFECT1"
				],
				abilities=[],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[],
				defaultTask=UnitTaskType.unknown,
				movementType=UnitMovementType.walk,
				productionCost=-1,
				purchaseCost=-1,
				faithCost=-1,
				maintenanceCost=0,
				sight=2,
				range=0,
				supportDistance=0,
				strength=0,
				targetType=UnitClassType.civilian,
				flags=None,
				meleeAttack=0,
				rangedAttack=0,
				moves=3,
				requiredTech=None,
				obsoleteTech=None,
				requiredCivic=None,
				upgradesFrom=[],
				flavors=[
					Flavor(FlavorType.naval, value=1)
				]
			)

		# player overrides

		# barbarians  ------------------------------

		elif self == UnitType.barbarianWarrior:
			#
			return UnitTypeData(
				name="Barbarian Warrior",
				baseType=UnitType.warrior,
				domain=UnitDomainType.land,
				effects=[],
				abilities=[UnitAbilityType.canCapture],
				era=EraType.ancient,
				requiredResource=None,
				civilization=CivilizationType.barbarian,
				unitTasks=[UnitTaskType.attack],
				defaultTask=UnitTaskType.attack,
				movementType=UnitMovementType.walk,
				productionCost=-1,
				purchaseCost=-1,
				faithCost=-1,
				maintenanceCost=0,
				sight=2,
				range=0,
				supportDistance=0,
				strength=10,
				targetType=UnitClassType.melee,
				flags=None,
				meleeAttack=15,
				rangedAttack=0,
				moves=2,
				requiredTech=None,
				obsoleteTech=None,
				requiredCivic=None,
				upgradesFrom=[],
				flavors=[
					Flavor(FlavorType.offense, value=1)
				]
			)
		elif self == UnitType.barbarianArcher:
			#
			return UnitTypeData(
				name="Barbarian Archer",
				baseType=UnitType.archer,
				domain=UnitDomainType.land,
				effects=[],
				abilities=[UnitAbilityType.canCapture],
				era=EraType.ancient,
				requiredResource=None,
				civilization=CivilizationType.barbarian,
				unitTasks=[UnitTaskType.ranged],
				defaultTask=UnitTaskType.ranged,
				movementType=UnitMovementType.walk,
				productionCost=-1,
				purchaseCost=-1,
				faithCost=-1,
				maintenanceCost=0,
				sight=2,
				range=1,
				supportDistance=2,
				strength=10,
				targetType=UnitClassType.ranged,
				flags=None,
				meleeAttack=15,
				rangedAttack=20,
				moves=2,
				requiredTech=TechType.archery,
				obsoleteTech=None,
				requiredCivic=None,
				upgradesFrom=[],
				flavors=[
					Flavor(FlavorType.offense, value=1)
				]
			)

		raise AttributeError(f'cant get data for unit {self}')

	def unitTypeFor(self, civilization: CivilizationType) -> Optional[UnitType]:

		if self.civilization() == civilization:
			return self

		# if this unit is not for a special civ - we can use it
		if self.civilization() is None:
			return self

		# otherwise the base type
		return self.baseType()


class MoveOption(Enum):
	none = 'none'

	attack = 'attack'
	declareWar = 'declareWar'


class UnitMissionTypeData:
	def __init__(self, name: str, needsTarget: bool):
		self.name = name
		self.needsTarget = needsTarget


class UnitMissionType(Enum):
	found = 'found'
	moveTo = 'moveTo'
	routeTo = 'routeTo'
	followPath = 'followPath'
	garrison = 'garrison'
	pillage = 'pillage'
	plunderTradeRoute = 'plunderTradeRoute'
	build = 'build'
	skip = 'skip'
	rangedAttack = 'rangedAttack'

	sleep = 'sleep'
	fortify = 'fortify'
	alert = 'alert'
	airPatrol = 'airPatrol'
	heal = 'heal'

	embark = 'embark'
	disembark = 'disembark'
	rebase = 'rebase'
	swapUnits = 'swapUnits'
	moveToUnit = 'moveToUnit'

	group = 'group'

	def title(self) -> str:  # cannot be 'name'
		return self._data().name

	def needsTarget(self) -> bool:
		return self._data().needsTarget

	def _data(self) -> UnitMissionTypeData:
		if self == UnitMissionType.found:
			return UnitMissionTypeData(name='TXT_KEY_MISSION_FOUND_NAME', needsTarget=False)
		elif self == UnitMissionType.moveTo:
			return UnitMissionTypeData(name=_("TXT_KEY_MISSION_MOVE_TO_NAME"), needsTarget=True)
		elif self == UnitMissionType.routeTo:
			return UnitMissionTypeData(name=_("TXT_KEY_MISSION_ROUTE_TO_NAME"), needsTarget=True)
		elif self == UnitMissionType.followPath:
			return UnitMissionTypeData(name=_("TXT_KEY_MISSION_FOLLOW_PATH_NAME"), needsTarget=True)
		elif self == UnitMissionType.garrison:
			return UnitMissionTypeData(name=_("TXT_KEY_MISSION_GARRISON_NAME"), needsTarget=False)
		elif self == UnitMissionType.pillage:
			return UnitMissionTypeData(name=_("TXT_KEY_MISSION_PILLAGE_NAME"), needsTarget=False)
		elif self == UnitMissionType.plunderTradeRoute:
			return UnitMissionTypeData(name=_("TXT_KEY_MISSION_PLUNDER_TRADE_ROUTE_NAME"), needsTarget=True)
		elif self == UnitMissionType.build:
			return UnitMissionTypeData(name=_("TXT_KEY_MISSION_BUILD_NAME"), needsTarget=False)
		elif self == UnitMissionType.skip:
			return UnitMissionTypeData(name='TXT_KEY_MISSION_SKIP_NAME', needsTarget=False)
		elif self == UnitMissionType.rangedAttack:
			return UnitMissionTypeData(name='TXT_KEY_MISSION_RANGED_ATTACK_NAME', needsTarget=True)

		elif self == UnitMissionType.sleep:
			return UnitMissionTypeData(name=_("TXT_KEY_MISSION_SLEEP_NAME"), needsTarget=False)
		elif self == UnitMissionType.fortify:
			return UnitMissionTypeData(name=_("TXT_KEY_MISSION_FORTIFY_NAME"), needsTarget=False)
		elif self == UnitMissionType.alert:
			return UnitMissionTypeData(name=_("TXT_KEY_MISSION_ALERT_NAME"), needsTarget=False)
		elif self == UnitMissionType.airPatrol:
			return UnitMissionTypeData(name=_("TXT_KEY_MISSION_AIR_PATROL_NAME"), needsTarget=False)
		elif self == UnitMissionType.heal:
			return UnitMissionTypeData(name=_("TXT_KEY_MISSION_HEAL_NAME"), needsTarget=False)

		elif self == UnitMissionType.embark:
			return UnitMissionTypeData(name=_("TXT_KEY_MISSION_EMBARK_NAME"), needsTarget=True)
		elif self == UnitMissionType.disembark:
			return UnitMissionTypeData(name=_("TXT_KEY_MISSION_DISEMBARK_NAME"), needsTarget=True)
		elif self == UnitMissionType.rebase:
			return UnitMissionTypeData(name=_("TXT_KEY_MISSION_REBASE_NAME"), needsTarget=True)
		elif self == UnitMissionType.swapUnits:
			return UnitMissionTypeData(name=_("TXT_KEY_MISSION_SWAP_UNITS_NAME"), needsTarget=True)
		elif self == UnitMissionType.moveToUnit:
			return UnitMissionTypeData(name=_("TXT_KEY_MISSION_MOVE_TO_UNIT_NAME"), needsTarget=True)

		raise InvalidEnumError(self)


class UnitActivityType(ExtendedEnum):
	none = 'none'

	heal = 'heal'
	sleep = 'sleep'
	awake = 'awake'
	mission = 'mission'
	hold = 'hold'
	sentry = 'sentry'
	intercept = 'intercept'
	explore = 'explore'
