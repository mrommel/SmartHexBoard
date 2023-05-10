from typing import Optional

from smarthexboard.game.civics import CivicType
from smarthexboard.game.eras import EraType
from smarthexboard.game.flavors import Flavor, FlavorType
from smarthexboard.game.techs import TechType
from smarthexboard.game.civilizations import CivilizationType
from smarthexboard.map.base import ExtendedEnum
from smarthexboard.map.types import ResourceType


class UnitType:
	pass


class UnitDomainType(ExtendedEnum):
	sea = 'sea'
	land = 'land'


class UnitAbilityType(ExtendedEnum):
	ignoreZoneOfControl = 'ignoreZoneOfControl'
	oceanImpassable = 'oceanImpassable'
	experienceFromTribal = 'experienceFromTribal'
	canMoveInRivalTerritory = 'canMoveInRivalTerritory'
	canEstablishTradeRoute = 'canEstablishTradeRoute'
	canImprove = 'canImprove'
	canFound = 'canFound'
	canCapture = 'canCapture'


class UnitTaskType(ExtendedEnum):
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
	none = 'none'


class UnitMovementType(ExtendedEnum):
	swimShallow = 'swimShallow'
	walk = 'walk'


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


class BitArray:
	pass


class UnitTypeData:
	def __init__(self, name: str, baseType: Optional[UnitType], domain: UnitDomainType, effects: [str],
	             abilities: [UnitAbilityType], era: EraType, requiredResource: Optional[ResourceType],
	             civilization: Optional[CivilizationType], unitTasks: [UnitTaskType],
	             defaultTask: UnitTaskType, movementType: UnitMovementType, productionCost: int,
	             purchaseCost: int, faithCost: int, maintenanceCost: int, sight: int, range: int,
	             supportDistance: int, strength: int, targetType: UnitClassType, flags: Optional[BitArray],
	             meleeAttack: int, rangedAttack: int, moves: int, requiredTech: Optional[TechType],
	             obsoleteTech: Optional[TechType], requiredCivic: Optional[CivicType],
	             upgradesFrom: [UnitType], flavours: [Flavor]):
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
		self.flavours = flavours


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

	def name(self):
		return self._data().name

	def civilization(self):
		return self._data().civilization

	def requiredCivic(self):
		return self._data().requiredCivic

	def _data(self) -> UnitTypeData:
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
				upgradesFrom=None,
				flavours=[]
			)

		# civilians ------------------------------
		elif self == UnitType.settler:
			return UnitTypeData(
				name="TXT_KEY_UNIT_SETTLER_NAME",
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
				flavours=[
					Flavor(FlavorType.expansion, value=9)
				]
			)
		elif self == UnitType.builder:
			return UnitTypeData(
				name="TXT_KEY_UNIT_BUILDER_NAME",
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
				flavours=[
					Flavor(FlavorType.tileImprovement, value=10),
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
				name="TXT_KEY_UNIT_TRADER_NAME",
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
				flavours=[
					Flavor(FlavorType.gold, value=10)
				]
			)

		# recon ------------------------------
		elif self == UnitType.scout:
			return UnitTypeData(
				name="TXT_KEY_UNIT_SCOUT_NAME",
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
				flavours=[
					Flavor(FlavorType.recon, value=8),
					Flavor(FlavorType.defense, value=2)
				]
			)
		elif self == UnitType.skirmisher:
			return UnitTypeData(
				name="TXT_KEY_UNIT_SKIRMISHER_NAME",
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
				flavours=[
					Flavor(FlavorType.recon, value=8),
					Flavor(FlavorType.offense, value=1),
					Flavor(FlavorType.defense, value=1)
				]
			)

		# melee ------------------------------
		elif self == UnitType.warrior:
			return UnitTypeData(
				name="TXT_KEY_UNIT_WARRIOR_NAME",
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
				flavours=[
					Flavor(FlavorType.offense, value=3),
					Flavor(FlavorType.recon, value=3),
					Flavor(FlavorType.defense, value=3)
				]
			)
		elif self == UnitType.swordman:
			return UnitTypeData(
				name="TXT_KEY_UNIT_SWORDMAN_NAME",
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
				flavours=[]
			)
		elif self == UnitType.manAtArms:
			return UnitTypeData(
				name="TXT_KEY_UNIT_MAN_AT_ARMS_NAME",
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
				flavours=[
					Flavor(FlavorType.recon, value=1),
					Flavor(FlavorType.offense, value=8),
					Flavor(FlavorType.defense, value=1)
				]
			)

		# ranged ------------------------------
		elif self == UnitType.slinger:
			return UnitTypeData(
				name="TXT_KEY_UNIT_SLINGER_NAME",
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
				flavours=[
					Flavor(FlavorType.ranged, value=8),
					Flavor(FlavorType.recon, value=10),
					Flavor(FlavorType.offense, value=3),
					Flavor(FlavorType.defense, value=4)
				]
			)
		elif self == UnitType.archer:
			return UnitTypeData(
				name="TXT_KEY_UNIT_ARCHER_NAME",
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
				flavours=[
					Flavor(FlavorType.ranged, value=6),
					Flavor(FlavorType.recon, value=3),
					Flavor(FlavorType.offense, value=1),
					Flavor(FlavorType.defense, value=2)
				]
			)
		elif self == UnitType.crossbowman:
			return UnitTypeData(
				name="TXT_KEY_UNIT_CROSSBOWMAN_NAME",
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
				flavours=[
					Flavor(FlavorType.recon, value=1),
					Flavor(FlavorType.offense, value=7),
					Flavor(FlavorType.defense, value=2)
				]
			)

		# anti-cavalry ------------------------------
		elif self == UnitType.spearman:
			return UnitTypeData(
				name="TXT_KEY_UNIT_SPEARMAN_NAME",
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
				flavours=[
					Flavor(FlavorType.defense, value=4),
					Flavor(FlavorType.recon, value=2),
					Flavor(FlavorType.offense, value=2)
				]
			)
		elif self == UnitType.pikeman:
			return UnitTypeData(
				name="TXT_KEY_UNIT_PIKEMAN_NAME",
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
				flavours=[
					Flavor(FlavorType.recon, value=1),
					Flavor(FlavorType.offense, value=3),
					Flavor(FlavorType.defense, value=6)
				]
			)
		# pikeAndShot  # renaissance

		# light cavalry ------------------------------
		elif self == UnitType.horseman:
			return UnitTypeData(
				name="TXT_KEY_UNIT_HORSEMAN_NAME",
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
				flavours=[]
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
		# 		flavours=[]
		# 	)
		# cavalry  # industrial

		# heavy cavalry ------------------------------
		elif self == UnitType.heavyChariot:
			return UnitTypeData(
				name="TXT_KEY_UNIT_HEAVY_CHARIOT_NAME",
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
				flavours=[
					Flavor(FlavorType.recon, value=9),
					Flavor(FlavorType.ranged, value=5),
					Flavor(FlavorType.mobile, value=10),
					Flavor(FlavorType.offense, value=3),
					Flavor(FlavorType.defense, value=6)
				]
			)
		elif self == UnitType.knight:
			return UnitTypeData(
				name="TXT_KEY_UNIT_KNIGHT_NAME",
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
				flavours=[
					Flavor(FlavorType.recon, value=1),
					Flavor(FlavorType.offense, value=9)
				]
			)
		# cuirassier  # industrial

		# siege ------------------------------
		elif self == UnitType.catapult:
			return UnitTypeData(
				name="TXT_KEY_UNIT_CATAPULT_NAME",
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
				flavours=[
					Flavor(FlavorType.ranged, value=8),
					Flavor(FlavorType.offense, value=2)
				]
			)
		elif self == UnitType.trebuchet:
			return UnitTypeData(
				name="TXT_KEY_UNIT_TREBUCHET_NAME",
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
				flavours=[
					Flavor(FlavorType.ranged, value=8),
					Flavor(FlavorType.offense, value=2)
				]
			)
		# bombard  # renaissance

		# naval melee ------------------------------
		elif self == UnitType.galley:
			return UnitTypeData(
				name="TXT_KEY_UNIT_GALLEY_NAME",
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
				flavours=[]
			)
		# caravel  # renaissance
		# ironclad  # industrial
		#
		# naval ranged ------------------------------
		elif self == UnitType.quadrireme:
			return UnitTypeData(
				name="TXT_KEY_UNIT_QUADRIREME_NAME",
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
				flavours=[]
			)

		raise AttributeError(f'cant get data for unit {self}')
