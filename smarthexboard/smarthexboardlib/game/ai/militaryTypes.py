from smarthexboard.smarthexboardlib.core.base import ExtendedEnum, InvalidEnumError
from smarthexboard.smarthexboardlib.game.unitTypes import UnitTaskType
from smarthexboard.smarthexboardlib.map import constants
from smarthexboard.smarthexboardlib.map.base import HexPoint


class MilitaryThreatType(ExtendedEnum):
	none = -1, 'none'

	minor = 0, 'minor'
	major = 1, 'major'
	severe = 2, 'severe'
	critical = 3, 'critical'

	def __new__(cls, value, name):
		member = object.__new__(cls)
		member._value = value
		member._name = name
		return member

	def __lt__(self, other):
		if isinstance(other, MilitaryThreatType):
			return self._value < other._value

		raise Exception(f'cannot compare MilitaryThreatType and {type(other)}')

	def __ge__(self, other):
		if isinstance(other, MilitaryThreatType):
			return self._value >= other._value

		raise Exception(f'cannot compare MilitaryThreatType and {type(other)}')

	def value(self) -> int:
		return int(self._value)

	def weight(self) -> int:
		if self == MilitaryThreatType.none:
			return 0
		elif self == MilitaryThreatType.minor:
			return 1
		elif self == MilitaryThreatType.major:
			return 3
		elif self == MilitaryThreatType.severe:
			return 6
		elif self == MilitaryThreatType.critical:
			return 10


class ArmyState(ExtendedEnum):
	waitingForUnitsToReinforce = 'waitingForUnitsToReinforce'
	recruitingUnits = 'recruitingUnits'
	waitingForUnitsToCatchUp = 'waitingForUnitsToCatchUp'
	gatheringForces = 'gatheringForces'
	movingToDestination = 'movingToDestination'


class TacticalMoveTypeData:
	def __init__(self, operationsCanRecruit: bool, dominanceZoneMove: bool, offenseFlavorWeight: int,
				 defenseFlavorWeight: int, priority: int):
		self.operationsCanRecruit: bool = operationsCanRecruit
		self.dominanceZoneMove: bool = dominanceZoneMove
		self.offenseFlavorWeight: int = offenseFlavorWeight
		self.defenseFlavorWeight: int = defenseFlavorWeight
		self.priority: int = priority


class TacticalMoveType:
	pass


class TacticalMoveType(ExtendedEnum):
	none = 'none'

	unassigned = 'unassigned'  # TACTICAL_UNASSIGNED
	moveNoncombatantsToSafety = 'moveNoncombatantsToSafety'  # TACTICAL_MOVE_NONCOMBATANTS_TO_SAFETY
	captureCity = 'captureCity'  # TACTICAL_CAPTURE_CITY
	damageCity = 'damageCity'  # TACTICAL_DAMAGE_CITY
	destroyHighUnit = 'destroyHighUnit'  # TACTICAL_DESTROY_HIGH_UNIT
	destroyMediumUnit = 'destroyMediumUnit'  # TACTICAL_DESTROY_MEDIUM_UNIT
	destroyLowUnit = 'destroyLowUnit'  # TACTICAL_DESTROY_LOW_UNIT
	toSafety = 'toSafety'  # TACTICAL_TO_SAFETY
	attritHighUnit = 'attritHighUnit'  # TACTICAL_ATTRIT_HIGH_UNIT
	attritMediumUnit = 'attritMediumUnit'  # TACTICAL_ATTRIT_MEDIUM_UNIT
	attritLowUnit = 'attritLowUnit'  # TACTICAL_ATTRIT_LOW_UNIT
	reposition = 'reposition'  # TACTICAL_REPOSITION
	barbarianCamp = 'barbarianCamp'  # TACTICAL_BARBARIAN_CAMP
	pillage = 'pillage'  # TACTICAL_PILLAGE
	civilianAttack = 'civilianAttack'  # TACTICAL_CIVILIAN_ATTACK
	safeBombards = 'safeBombards'  # TACTICAL_SAFE_BOMBARDS
	heal = 'heal'  # TACTICAL_HEAL
	ancientRuins = 'ancientRuins'  # TACTICAL_ANCIENT_RUINS
	garrisonToAllowBombards = 'garrisonToAllowBombards'  # TACTICAL_GARRISON_TO_ALLOW_BOMBARD
	bastionAlreadyThere = 'bastionAlreadyThere'  # TACTICAL_BASTION_ALREADY_THERE
	garrisonAlreadyThere = 'garrisonAlreadyThere'  # TACTICAL_GARRISON_ALREADY_THERE
	guardImprovementAlreadyThere = 'guardImprovementAlreadyThere'  # TACTICAL_GUARD_IMPROVEMENT_ALREADY_THERE
	bastionOneTurn = 'bastionOneTurn'  # TACTICAL_BASTION_1_TURN
	garrisonOneTurn = 'garrisonOneTurn'  # TACTICAL_GARRISON_1_TURN
	guardImprovementOneTurn = 'guardImprovementOneTurn'  # TACTICAL_GUARD_IMPROVEMENT_1_TURN
	airSweep = 'airSweep'  # TACTICAL_AIR_SWEEP
	airIntercept = 'airIntercept'  # TACTICAL_AIR_INTERCEPT
	airRebase = 'airRebase'  # TACTICAL_AIR_REBASE
	closeOnTarget = 'closeOnTarget'  # TACTICAL_CLOSE_ON_TARGET
	moveOperation = 'moveOperation'  # TACTICAL_MOVE_OPERATIONS
	emergencyPurchases = 'emergencyPurchases'  # TACTICAL_EMERGENCY_PURCHASES

	# postures
	postureWithdraw = 'postureWithdraw'  # TACTICAL_POSTURE_WITHDRAW
	postureSitAndBombard = 'postureSitAndBombard'  # TACTICAL_POSTURE_SIT_AND_BOMBARD
	postureAttritFromRange = 'postureAttritFromRange'  # TACTICAL_POSTURE_ATTRIT_FROM_RANGE
	postureExploitFlanks = 'postureExploitFlanks'  # TACTICAL_POSTURE_EXPLOIT_FLANKS
	postureSteamroll = 'postureSteamroll'  # TACTICAL_POSTURE_STEAMROLL
	postureSurgicalCityStrike = 'postureSurgicalCityStrike'  # TACTICAL_POSTURE_SURGICAL_CITY_STRIKE
	postureHedgehog = 'postureHedgehog'  # TACTICAL_POSTURE_HEDGEHOG
	postureCounterAttack = 'postureCounterAttack'  # TACTICAL_POSTURE_COUNTERATTACK
	postureShoreBombardment = 'postureShoreBombardment'  # TACTICAL_POSTURE_SHORE_BOMBARDMENT

	# barbarian
	barbarianCaptureCity = 'barbarianCaptureCity'  # AI_TACTICAL_BARBARIAN_CAPTURE_CITY,
	barbarianDamageCity = 'barbarianDamageCity'  # AI_TACTICAL_BARBARIAN_DAMAGE_CITY,
	barbarianDestroyHighPriorityUnit = 'barbarianDestroyHighPriorityUnit'  # AI_TACTICAL_BARBARIAN_DESTROY_HIGH_PRIORITY_UNIT,
	barbarianDestroyMediumPriorityUnit = 'barbarianDestroyMediumPriorityUnit'  # AI_TACTICAL_BARBARIAN_DESTROY_MEDIUM_PRIORITY_UNIT,
	barbarianDestroyLowPriorityUnit = 'barbarianDestroyLowPriorityUnit'  # AI_TACTICAL_BARBARIAN_DESTROY_LOW_PRIORITY_UNIT,
	barbarianMoveToSafety = 'barbarianMoveToSafety'  # AI_TACTICAL_BARBARIAN_MOVE_TO_SAFETY,
	barbarianAttritHighPriorityUnit = 'barbarianAttritHighPriorityUnit'  # AI_TACTICAL_BARBARIAN_ATTRIT_HIGH_PRIORITY_UNIT,
	barbarianAttritMediumPriorityUnit = 'barbarianAttritMediumPriorityUnit'  # AI_TACTICAL_BARBARIAN_ATTRIT_MEDIUM_PRIORITY_UNIT,
	barbarianAttritLowPriorityUnit = 'barbarianAttritLowPriorityUnit'  # AI_TACTICAL_BARBARIAN_ATTRIT_LOW_PRIORITY_UNIT,
	barbarianPillage = 'barbarianPillage'  # AI_TACTICAL_BARBARIAN_PILLAGE,
	barbarianBlockadeResource = 'barbarianBlockadeResource'  # AI_TACTICAL_BARBARIAN_PRIORITY_BLOCKADE_RESOURCE,
	barbarianCivilianAttack = 'barbarianCivilianAttack'  # AI_TACTICAL_BARBARIAN_CIVILIAN_ATTACK,
	barbarianAggressiveMove = 'barbarianAggressiveMove'  # AI_TACTICAL_BARBARIAN_AGGRESSIVE_MOVE,
	barbarianPassiveMove = 'barbarianPassiveMove'  # AI_TACTICAL_BARBARIAN_PASSIVE_MOVE,
	barbarianCampDefense = 'barbarianCampDefense'  # AI_TACTICAL_BARBARIAN_CAMP_DEFENSE,
	barbarianGuardCamp = 'barbarianGuardCamp'
	barbarianDesperateAttack = 'barbarianDesperateAttack'  # AI_TACTICAL_BARBARIAN_DESPERATE_ATTACK,
	barbarianEscortCivilian = 'barbarianEscortCivilian'  # AI_TACTICAL_BARBARIAN_ESCORT_CIVILIAN,
	barbarianPlunderTradeUnit = 'barbarianPlunderTradeUnit'  # AI_TACTICAL_BARBARIAN_PLUNDER_TRADE_UNIT,
	barbarianPillageCitadel = 'barbarianPillageCitadel'  # AI_TACTICAL_BARBARIAN_PILLAGE_CITADEL,
	barbarianPillageNextTurn = 'barbarianPillageNextTurn'  # AI_TACTICAL_BARBARIAN_PILLAGE_NEXT_TURN

	@staticmethod
	def allBarbarianMoves() -> [TacticalMoveType]:
		return [
			TacticalMoveType.barbarianCaptureCity,
			TacticalMoveType.barbarianDamageCity,
			TacticalMoveType.barbarianDestroyHighPriorityUnit,
			TacticalMoveType.barbarianDestroyMediumPriorityUnit,
			TacticalMoveType.barbarianDestroyLowPriorityUnit,
			TacticalMoveType.barbarianMoveToSafety,
			TacticalMoveType.barbarianAttritHighPriorityUnit,
			TacticalMoveType.barbarianAttritMediumPriorityUnit,
			TacticalMoveType.barbarianAttritLowPriorityUnit,
			TacticalMoveType.barbarianPillage,
			TacticalMoveType.barbarianBlockadeResource,
			TacticalMoveType.barbarianCivilianAttack,
			TacticalMoveType.barbarianAggressiveMove,
			TacticalMoveType.barbarianPassiveMove,
			TacticalMoveType.barbarianCampDefense,
			TacticalMoveType.barbarianGuardCamp,
			TacticalMoveType.barbarianDesperateAttack,
			TacticalMoveType.barbarianEscortCivilian,
			TacticalMoveType.barbarianPlunderTradeUnit,
			TacticalMoveType.barbarianPillageCitadel,
			TacticalMoveType.barbarianPillageNextTurn
		]

	@staticmethod
	def allPlayerMoves() -> [TacticalMoveType]:
		return [
			TacticalMoveType.moveNoncombatantsToSafety,
			TacticalMoveType.captureCity,
			TacticalMoveType.damageCity,
			TacticalMoveType.destroyHighUnit,
			TacticalMoveType.destroyMediumUnit,
			TacticalMoveType.destroyLowUnit,
			TacticalMoveType.toSafety,
			TacticalMoveType.attritHighUnit,
			TacticalMoveType.attritMediumUnit,
			TacticalMoveType.attritLowUnit,
			TacticalMoveType.reposition,
			TacticalMoveType.barbarianCamp,
			TacticalMoveType.pillage,
			TacticalMoveType.civilianAttack,
			TacticalMoveType.safeBombards,
			TacticalMoveType.heal,
			TacticalMoveType.ancientRuins,
			TacticalMoveType.garrisonToAllowBombards,
			TacticalMoveType.bastionAlreadyThere,
			TacticalMoveType.garrisonAlreadyThere,
			TacticalMoveType.guardImprovementAlreadyThere,
			TacticalMoveType.bastionOneTurn,
			TacticalMoveType.garrisonOneTurn,
			TacticalMoveType.guardImprovementOneTurn,
			TacticalMoveType.airSweep,
			TacticalMoveType.airIntercept,
			TacticalMoveType.airRebase,
			TacticalMoveType.closeOnTarget,
			TacticalMoveType.moveOperation,
			TacticalMoveType.emergencyPurchases
		]

	def priority(self) -> int:
		return self._data().priority

	def dominanceZoneMove(self) -> bool:
		return self._data().dominanceZoneMove

	def canRecruitForOperations(self) -> bool:
		return self._data().operationsCanRecruit

	def _data(self) -> TacticalMoveTypeData:
		if self == TacticalMoveType.none:
			return TacticalMoveTypeData(
				operationsCanRecruit=False,
				dominanceZoneMove=False,
				offenseFlavorWeight=0,
				defenseFlavorWeight=0,
				priority=-1
			)
		elif self == TacticalMoveType.barbarianGuardCamp:
			return TacticalMoveTypeData(
				operationsCanRecruit=False,
				dominanceZoneMove=False,
				offenseFlavorWeight=0,
				defenseFlavorWeight=0,
				priority=200
			)
		elif self == TacticalMoveType.unassigned:
			return TacticalMoveTypeData(
				operationsCanRecruit=True,
				dominanceZoneMove=False,
				offenseFlavorWeight=0,
				defenseFlavorWeight=0,
				priority=-1)
		elif self == TacticalMoveType.moveNoncombatantsToSafety:
			return TacticalMoveTypeData(
				operationsCanRecruit=True,
				dominanceZoneMove=False,
				offenseFlavorWeight=0,
				defenseFlavorWeight=0,
				priority=0
			)
		elif self == TacticalMoveType.captureCity:
			return TacticalMoveTypeData(
				operationsCanRecruit=False,
				dominanceZoneMove=False,
				offenseFlavorWeight=100,
				defenseFlavorWeight=0,
				priority=150
			)
		elif self == TacticalMoveType.damageCity:
			return TacticalMoveTypeData(
				operationsCanRecruit=True,
				dominanceZoneMove=False,
				offenseFlavorWeight=100,
				defenseFlavorWeight=0,
				priority=15
			)
		elif self == TacticalMoveType.destroyHighUnit:
			return TacticalMoveTypeData(
				operationsCanRecruit=False,
				dominanceZoneMove=False,
				offenseFlavorWeight=0,
				defenseFlavorWeight=100,
				priority=140
			)
		elif self == TacticalMoveType.destroyMediumUnit:
			return TacticalMoveTypeData(
				operationsCanRecruit=False,
				dominanceZoneMove=False,
				offenseFlavorWeight=0,
				defenseFlavorWeight=100,
				priority=120
			)
		elif self == TacticalMoveType.destroyLowUnit:
			return TacticalMoveTypeData(
				operationsCanRecruit=True,
				dominanceZoneMove=False,
				offenseFlavorWeight=0,
				defenseFlavorWeight=100,
				priority=110
			)
		elif self == TacticalMoveType.closeOnTarget:
			return TacticalMoveTypeData(
				operationsCanRecruit=False,
				dominanceZoneMove=True,
				offenseFlavorWeight=0,
				defenseFlavorWeight=0,
				priority=45
			)
		elif self == TacticalMoveType.toSafety:
			return TacticalMoveTypeData(
				operationsCanRecruit=False,
				dominanceZoneMove=False,
				offenseFlavorWeight=0,
				defenseFlavorWeight=100,
				priority=11
			)
		elif self == TacticalMoveType.attritHighUnit:
			return TacticalMoveTypeData(
				operationsCanRecruit=True,
				dominanceZoneMove=False,
				offenseFlavorWeight=0,
				defenseFlavorWeight=100,
				priority=17
			)
		elif self == TacticalMoveType.attritMediumUnit:
			return TacticalMoveTypeData(
				operationsCanRecruit=True,
				dominanceZoneMove=False,
				offenseFlavorWeight=0,
				defenseFlavorWeight=100,
				priority=15
			)
		elif self == TacticalMoveType.attritLowUnit:
			return TacticalMoveTypeData(
				operationsCanRecruit=True,
				dominanceZoneMove=False,
				offenseFlavorWeight=0,
				defenseFlavorWeight=100,
				priority=12
			)
		elif self == TacticalMoveType.reposition:
			return TacticalMoveTypeData(
				operationsCanRecruit=True,
				dominanceZoneMove=False,
				offenseFlavorWeight=50,
				defenseFlavorWeight=50,
				priority=1
			)
		elif self == TacticalMoveType.barbarianCamp:
			return TacticalMoveTypeData(
				operationsCanRecruit=False,
				dominanceZoneMove=False,
				offenseFlavorWeight=100,
				defenseFlavorWeight=0,
				priority=10
			)
		elif self == TacticalMoveType.pillage:
			return TacticalMoveTypeData(
				operationsCanRecruit=False,
				dominanceZoneMove=False,
				offenseFlavorWeight=100,
				defenseFlavorWeight=0,
				priority=40
			)
		elif self == TacticalMoveType.civilianAttack:
			return TacticalMoveTypeData(
				operationsCanRecruit=False,
				dominanceZoneMove=False,
				offenseFlavorWeight=100,
				defenseFlavorWeight=0,
				priority=65
			)
		elif self == TacticalMoveType.safeBombards:
			return TacticalMoveTypeData(
				operationsCanRecruit=False,
				dominanceZoneMove=False,
				offenseFlavorWeight=100,
				defenseFlavorWeight=0,
				priority=60
			)
		elif self == TacticalMoveType.heal:
			return TacticalMoveTypeData(
				operationsCanRecruit=True,
				dominanceZoneMove=False,
				offenseFlavorWeight=0,
				defenseFlavorWeight=100,
				priority=8
			)
		elif self == TacticalMoveType.ancientRuins:
			return TacticalMoveTypeData(
				operationsCanRecruit=True,
				dominanceZoneMove=False,
				offenseFlavorWeight=50,
				defenseFlavorWeight=50,
				priority=25
			)
		elif self == TacticalMoveType.garrisonToAllowBombards:
			return TacticalMoveTypeData(
				operationsCanRecruit=True,
				dominanceZoneMove=False,
				offenseFlavorWeight=0,
				defenseFlavorWeight=100,
				priority=20
			)
		elif self == TacticalMoveType.bastionAlreadyThere:
			return TacticalMoveTypeData(
				operationsCanRecruit=False,
				dominanceZoneMove=False,
				offenseFlavorWeight=0,
				defenseFlavorWeight=100,
				priority=7
			)
		elif self == TacticalMoveType.garrisonAlreadyThere:
			return TacticalMoveTypeData(
				operationsCanRecruit=False,
				dominanceZoneMove=False,
				offenseFlavorWeight=0,
				defenseFlavorWeight=100,
				priority=6
			)
		elif self == TacticalMoveType.guardImprovementAlreadyThere:
			return TacticalMoveTypeData(
				operationsCanRecruit=False,
				dominanceZoneMove=False,
				offenseFlavorWeight=0,
				defenseFlavorWeight=100,
				priority=5
			)
		elif self == TacticalMoveType.bastionOneTurn:
			return TacticalMoveTypeData(
				operationsCanRecruit=True,
				dominanceZoneMove=False,
				offenseFlavorWeight=0,
				defenseFlavorWeight=100,
				priority=4
			)
		elif self == TacticalMoveType.garrisonOneTurn:
			return TacticalMoveTypeData(
				operationsCanRecruit=True,
				dominanceZoneMove=False,
				offenseFlavorWeight=0,
				defenseFlavorWeight=100,
				priority=3
			)
		elif self == TacticalMoveType.guardImprovementOneTurn:
			return TacticalMoveTypeData(
				operationsCanRecruit=True,
				dominanceZoneMove=False,
				offenseFlavorWeight=0,
				defenseFlavorWeight=100,
				priority=2
			)
		elif self == TacticalMoveType.airSweep:
			return TacticalMoveTypeData(
				operationsCanRecruit=False,
				dominanceZoneMove=False,
				offenseFlavorWeight=100,
				defenseFlavorWeight=0,
				priority=10
			)
		elif self == TacticalMoveType.airIntercept:
			return TacticalMoveTypeData(
				operationsCanRecruit=False,
				dominanceZoneMove=False,
				offenseFlavorWeight=0,
				defenseFlavorWeight=100,
				priority=20
			)
		elif self == TacticalMoveType.airRebase:
			return TacticalMoveTypeData(
				operationsCanRecruit=False,
				dominanceZoneMove=False,
				offenseFlavorWeight=0,
				defenseFlavorWeight=100,
				priority=1
			)
		elif self == TacticalMoveType.postureWithdraw:
			return TacticalMoveTypeData(
				operationsCanRecruit=False,
				dominanceZoneMove=True,
				offenseFlavorWeight=0,
				defenseFlavorWeight=0,
				priority=101
			)
		elif self == TacticalMoveType.postureSitAndBombard:
			return TacticalMoveTypeData(
				operationsCanRecruit=False,
				dominanceZoneMove=True,
				offenseFlavorWeight=0,
				defenseFlavorWeight=0,
				priority=105
			)
		elif self == TacticalMoveType.postureAttritFromRange:
			return TacticalMoveTypeData(
				operationsCanRecruit=False,
				dominanceZoneMove=True,
				offenseFlavorWeight=0,
				defenseFlavorWeight=0,
				priority=104
			)
		elif self == TacticalMoveType.postureExploitFlanks:
			return TacticalMoveTypeData(
				operationsCanRecruit=False,
				dominanceZoneMove=True,
				offenseFlavorWeight=0,
				defenseFlavorWeight=0,
				priority=107
			)
		elif self == TacticalMoveType.postureSteamroll:
			return TacticalMoveTypeData(
				operationsCanRecruit=False,
				dominanceZoneMove=True,
				offenseFlavorWeight=0,
				defenseFlavorWeight=0,
				priority=108
			)
		elif self == TacticalMoveType.postureSurgicalCityStrike:
			return TacticalMoveTypeData(
				operationsCanRecruit=False,
				dominanceZoneMove=True,
				offenseFlavorWeight=0,
				defenseFlavorWeight=0,
				priority=106
			)
		elif self == TacticalMoveType.postureHedgehog:
			return TacticalMoveTypeData(
				operationsCanRecruit=False,
				dominanceZoneMove=True,
				offenseFlavorWeight=0,
				defenseFlavorWeight=0,
				priority=50
			)
		elif self == TacticalMoveType.postureCounterAttack:
			return TacticalMoveTypeData(
				operationsCanRecruit=False,
				dominanceZoneMove=True,
				offenseFlavorWeight=0,
				defenseFlavorWeight=0,
				priority=103
			)
		elif self == TacticalMoveType.postureShoreBombardment:
			return TacticalMoveTypeData(
				operationsCanRecruit=False,
				dominanceZoneMove=True,
				offenseFlavorWeight=0,
				defenseFlavorWeight=0,
				priority=100
			)
		elif self == TacticalMoveType.moveOperation:
			return TacticalMoveTypeData(
				operationsCanRecruit=False,
				dominanceZoneMove=False,
				offenseFlavorWeight=0,
				defenseFlavorWeight=0,
				priority=80
			)
		elif self == TacticalMoveType.emergencyPurchases:
			return TacticalMoveTypeData(
				operationsCanRecruit=False,
				dominanceZoneMove=True,
				offenseFlavorWeight=0,
				defenseFlavorWeight=0,
				priority=200
			)

		# https://github.com/chvrsi/BarbariansEvolved/blob/00a6feec72fa7d95ef026d821f008bdbbf3ee3ab/xml/BarbarianDefines.xml
		elif self == TacticalMoveType.barbarianCaptureCity:
			return TacticalMoveTypeData(
				operationsCanRecruit=False,
				dominanceZoneMove=False,
				offenseFlavorWeight=0,
				defenseFlavorWeight=0,
				priority=9
			)
		elif self == TacticalMoveType.barbarianDamageCity:
			return TacticalMoveTypeData(
				operationsCanRecruit=False,
				dominanceZoneMove=False,
				offenseFlavorWeight=0,
				defenseFlavorWeight=0,
				priority=5
			)
		elif self == TacticalMoveType.barbarianDestroyHighPriorityUnit:
			return TacticalMoveTypeData(
				operationsCanRecruit=False,
				dominanceZoneMove=False,
				offenseFlavorWeight=0,
				defenseFlavorWeight=0,
				priority=16
			)
		elif self == TacticalMoveType.barbarianDestroyMediumPriorityUnit:
			return TacticalMoveTypeData(
				operationsCanRecruit=False,
				dominanceZoneMove=False,
				offenseFlavorWeight=0,
				defenseFlavorWeight=0,
				priority=15
			)
		elif self == TacticalMoveType.barbarianDestroyLowPriorityUnit:
			return TacticalMoveTypeData(
				operationsCanRecruit=False,
				dominanceZoneMove=False,
				offenseFlavorWeight=0,
				defenseFlavorWeight=0,
				priority=14
			)
		elif self == TacticalMoveType.barbarianMoveToSafety:
			return TacticalMoveTypeData(
				operationsCanRecruit=False,
				dominanceZoneMove=False,
				offenseFlavorWeight=0,
				defenseFlavorWeight=0,
				priority=10
			)
		elif self == TacticalMoveType.barbarianAttritHighPriorityUnit:
			return TacticalMoveTypeData(
				operationsCanRecruit=False,
				dominanceZoneMove=False,
				offenseFlavorWeight=0,
				defenseFlavorWeight=0,
				priority=10
			)
		elif self == TacticalMoveType.barbarianAttritMediumPriorityUnit:
			return TacticalMoveTypeData(
				operationsCanRecruit=False,
				dominanceZoneMove=False,
				offenseFlavorWeight=0,
				defenseFlavorWeight=0,
				priority=7
			)
		elif self == TacticalMoveType.barbarianAttritLowPriorityUnit:
			return TacticalMoveTypeData(
				operationsCanRecruit=False,
				dominanceZoneMove=False,
				offenseFlavorWeight=0,
				defenseFlavorWeight=0,
				priority=6
			)
		elif self == TacticalMoveType.barbarianPillage:
			return TacticalMoveTypeData(
				operationsCanRecruit=False,
				dominanceZoneMove=False,
				offenseFlavorWeight=0,
				defenseFlavorWeight=0,
				priority=12
			)
		elif self == TacticalMoveType.barbarianBlockadeResource:
			return TacticalMoveTypeData(
				operationsCanRecruit=False,
				dominanceZoneMove=False,
				offenseFlavorWeight=0,
				defenseFlavorWeight=0,
				priority=10
			)
		elif self == TacticalMoveType.barbarianCivilianAttack:
			return TacticalMoveTypeData(
				operationsCanRecruit=False,
				dominanceZoneMove=False,
				offenseFlavorWeight=0,
				defenseFlavorWeight=0,
				priority=13
			)
		elif self == TacticalMoveType.barbarianAggressiveMove:
			return TacticalMoveTypeData(
				operationsCanRecruit=False,
				dominanceZoneMove=False,
				offenseFlavorWeight=0,
				defenseFlavorWeight=0,
				priority=3
			)
		elif self == TacticalMoveType.barbarianPassiveMove:
			return TacticalMoveTypeData(
				operationsCanRecruit=False,
				dominanceZoneMove=False,
				offenseFlavorWeight=0,
				defenseFlavorWeight=0,
				priority=-1
			)
		elif self == TacticalMoveType.barbarianCampDefense:
			return TacticalMoveTypeData(
				operationsCanRecruit=False,
				dominanceZoneMove=False,
				offenseFlavorWeight=0,
				defenseFlavorWeight=0,
				priority=13
			)
		elif self == TacticalMoveType.barbarianDesperateAttack:
			return TacticalMoveTypeData(
				operationsCanRecruit=False,
				dominanceZoneMove=False,
				offenseFlavorWeight=0,
				defenseFlavorWeight=0,
				priority=0
			)
		elif self == TacticalMoveType.barbarianEscortCivilian:
			return TacticalMoveTypeData(
				operationsCanRecruit=False,
				dominanceZoneMove=False,
				offenseFlavorWeight=0,
				defenseFlavorWeight=0,
				priority=30
			)
		elif self == TacticalMoveType.barbarianPlunderTradeUnit:
			return TacticalMoveTypeData(
				operationsCanRecruit=False,
				dominanceZoneMove=False,
				offenseFlavorWeight=0,
				defenseFlavorWeight=0,
				priority=20
			)
		elif self == TacticalMoveType.barbarianPillageCitadel:
			return TacticalMoveTypeData(
				operationsCanRecruit=False,
				dominanceZoneMove=False,
				offenseFlavorWeight=0,
				defenseFlavorWeight=0,
				priority=14
			)
		elif self == TacticalMoveType.barbarianPillageNextTurn:
			return TacticalMoveTypeData(
				operationsCanRecruit=False,
				dominanceZoneMove=False,
				offenseFlavorWeight=0,
				defenseFlavorWeight=0,
				priority=4
			)


class TacticalTargetType(ExtendedEnum):
	none = 'none'  # AI_TACTICAL_TARGET_NONE

	city = 'city'  # AI_TACTICAL_TARGET_CITY
	barbarianCamp = 'barbarianCamp'  # AI_TACTICAL_TARGET_BARBARIAN_CAMP
	improvement = 'improvement'  # AI_TACTICAL_TARGET_IMPROVEMENT
	blockadeResourcePoint = 'blockadeResourcePoint'  # AI_TACTICAL_TARGET_BLOCKADE_RESOURCE_POINT
	lowPriorityUnit = 'lowPriorityUnit'  # AI_TACTICAL_TARGET_LOW_PRIORITY_UNIT # Can't attack one of our cities
	mediumPriorityUnit = 'mediumPriorityUnit'  # AI_TACTICAL_TARGET_MEDIUM_PRIORITY_UNIT - Can damage one of our cities
	highPriorityUnit = 'highPriorityUnit'  # AI_TACTICAL_TARGET_HIGH_PRIORITY_UNIT
	# Can contribute to capturing one of our cities
	cityToDefend = 'cityToDefend'  # AI_TACTICAL_TARGET_CITY_TO_DEFEND
	improvementToDefend = 'improvementToDefend'  # AI_TACTICAL_TARGET_IMPROVEMENT_TO_DEFEND
	defensiveBastion = 'defensiveBastion'  # AI_TACTICAL_TARGET_DEFENSIVE_BASTION
	ancientRuins = 'ancientRuins'  # AI_TACTICAL_TARGET_ANCIENT_RUINS
	bombardmentZone = 'bombardmentZone'  # AI_TACTICAL_TARGET_BOMBARDMENT_ZONE - Used for naval bombardment operation
	embarkedMilitaryUnit = 'embarkedMilitaryUnit'  # AI_TACTICAL_TARGET_EMBARKED_MILITARY_UNIT
	embarkedCivilian = 'embarkedCivilian'  # AI_TACTICAL_TARGET_EMBARKED_CIVILIAN
	lowPriorityCivilian = 'lowPriorityCivilian'  # AI_TACTICAL_TARGET_LOW_PRIORITY_CIVILIAN
	mediumPriorityCivilian = 'mediumPriorityCivilian'  # AI_TACTICAL_TARGET_MEDIUM_PRIORITY_CIVILIAN
	highPriorityCivilian = 'highPriorityCivilian'  # AI_TACTICAL_TARGET_HIGH_PRIORITY_CIVILIAN
	veryHighPriorityCivilian = 'veryHighPriorityCivilian'  # AI_TACTICAL_TARGET_VERY_HIGH_PRIORITY_CIVILIAN

	tradeUnitSea = 'tradeUnitSea'  # AI_TACTICAL_TARGET_TRADE_UNIT_SEA,
	tradeUnitLand = 'tradeUnitLand'  # AI_TACTICAL_TARGET_TRADE_UNIT_LAND,
	tradeUnitSeaPlot = 'tradeUnitSeaPlot'  # AI_TACTICAL_TARGET_TRADE_UNIT_SEA_PLOT - Used for idle unit moves to
	# plunder trade routes that go through our territory
	tradeUnitLandPlot = 'tradeUnitLandPlot'  # AI_TACTICAL_TARGET_TRADE_UNIT_LAND_PLOT,
	citadel = 'citadel'  # AI_TACTICAL_TARGET_CITADEL
	improvementResource = 'improvementResource'  # AI_TACTICAL_TARGET_IMPROVEMENT_RESOURCE


class TacticalPostureType(ExtendedEnum):
	"""
		++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
		 CLASS:      CvTacticalPosture
		!  brief        The posture an AI has adopted for fighting in a specific dominance zone
		//
		!  Key Attributes:
		!  - Used to keep consistency in approach from turn-to-turn
		!  - Reevaluated by tactical AI each turn before units are moved for this zone
		++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	"""
	none = 'none'
	withdraw = 'withdraw'
	sitAndBombard = 'sitAndBombard'
	attritFromRange = 'attritFromRange'
	exploitFlanks = 'exploitFlanks'
	steamRoll = 'steamRoll'
	surgicalCityStrike = 'surgicalCityStrike'
	hedgehog = 'hedgehog'
	counterAttack = 'counterAttack'
	shoreBombardment = 'shoreBombardment'
	emergencyPurchases = 'emergencyPurchases'


class TacticalDominanceTerritoryType(ExtendedEnum):
	tempZone = 'tempZone'
	enemy = 'enemy'
	friendly = 'friendly'
	neutral = 'neutral'
	noOwner = 'noOwner'


class TacticalDominanceType(ExtendedEnum):
	none = 'none'

	noUnitsPresent = 'noUnitsPresent'
	notVisible = 'notVisible'
	friendly = 'friendly'  # TACTICAL_DOMINANCE_FRIENDLY
	enemy = 'enemy'
	even = 'even'


class TacticalDominanceTerritoryType(ExtendedEnum):
	tempZone = 'tempZone'
	noOwner = 'noOwner'
	enemy = 'enemy'
	friendly = 'friendly'
	neutral = 'neutral'


class TacticalDominanceType(ExtendedEnum):
	noUnitsPresent = 'noUnitsPresent'
	notVisible = 'notVisible'
	friendly = 'friendly'
	enemy = 'enemy'
	even = 'even'


class TemporaryZone:
	def __init__(self, location: HexPoint = constants.invalidHexPoint, lastTurn: int = -1,
				 targetType: TacticalTargetType = TacticalTargetType.none, navalMission: bool = False):
		self.location = location
		self.lastTurn = lastTurn
		self.targetType = targetType
		self.navalMission = navalMission


class UnitFormationPosition(ExtendedEnum):
	none = 'none'

	bombard = 'bombard'
	frontline = 'frontline'
	civilianSupport = 'civilianSupport'
	navalEscort = 'navalEscort'


class UnitFormationSlot:
	def __init__(self, primaryUnitTask: UnitTaskType, secondaryUnitTask: UnitTaskType, position: UnitFormationPosition,
	             required: bool = True):
		self.primaryUnitTask: UnitTaskType = primaryUnitTask
		self.secondaryUnitTask: UnitTaskType = secondaryUnitTask
		self.position: UnitFormationPosition = position
		self.required: bool = required

		self.filled: bool = False


class UnitFormationType(ExtendedEnum):
	none = 'none'

	smallCityAttackForce = 'smallCityAttackForce'
	basicCityAttackForce = 'basicCityAttackForce'  # MUFORMATION_BASIC_CITY_ATTACK_FORCE
	fastPillagers = 'fastPillagers'  # MUFORMATION_FAST_PILLAGERS
	settlerEscort = 'settlerEscort'  # MUFORMATION_SETTLER_ESCORT
	navalSquadron = 'navalSquadron'  # MUFORMATION_NAVAL_SQUADRON
	navalInvasion = 'navalInvasion'  # MUFORMATION_NAVAL_INVASION
	navalEscort = 'navalEscort'  # MUFORMATION_NAVAL_ESCORT
	navalBombardment = 'navalBombardment'  # MUFORMATION_NAVAL_BOMBARDMENT
	pureNavalCityAttack = 'pureNavalCityAttack'  # MUFORMATION_PURE_NAVAL_CITY_ATTACK
	antiBarbarianTeam = 'antiBarbarianTeam'  # MUFORMATION_ANTI_BARBARIAN_TEAM
	biggerCityAttackForce = 'biggerCityAttackForce'  # MUFORMATION_BIGGER_CITY_ATTACK_FORCE
	colonizationParty = 'colonizationParty'  # MUFORMATION_COLONIZATION_PARTY
	quickColonySettler = 'quickColonySettler'  # MUFORMATION_QUICK_COLONY_SETTLER
	closeCityDefense = 'closeCityDefense'  # MUFORMATION_CLOSE_CITY_DEFENSE
	rapidResponseForce = 'rapidResponseForce'  # MUFORMATION_RAPID_RESPONSE_FORCE
	earlyRush = 'earlyRush'  # MUFORMATION_EARLY_RUSH

	cityStateInvasion = 'cityStateInvasion'  # MUFORMATION_CITY_STATE_INVASION
	cityStateAttackForce = 'cityStateAttackForce'  # MUFORMATION_CITY_STATE_ATTACK_FORCE

	def slots(self) -> [UnitFormationSlot]:
		# https://civilization.fandom.com/wiki/Module:Data/Civ5/BNW/MultiUnitFormation_Values
		# https://github.com/LoneGazebo/Community-Patch-DLL/blob/3783d7f1f870984ebdbfaa486eca181335151322/Community%20Patch/Core%20Files/Core%20Values/New_CIV5MultiUnitFormations.xml

		if self == UnitFormationType.none:
			return []

		elif self == UnitFormationType.smallCityAttackForce:
			return [
				UnitFormationSlot(UnitTaskType.cityBombard, UnitTaskType.ranged, UnitFormationPosition.bombard, required=True),
				UnitFormationSlot(UnitTaskType.cityBombard, UnitTaskType.ranged, UnitFormationPosition.bombard, required=False),
				UnitFormationSlot(UnitTaskType.cityBombard, UnitTaskType.defense, UnitFormationPosition.bombard, required=True),
				UnitFormationSlot(UnitTaskType.attack, UnitTaskType.defense, UnitFormationPosition.frontline, required=True),
				UnitFormationSlot(UnitTaskType.attack, UnitTaskType.defense, UnitFormationPosition.frontline, required=True),
				UnitFormationSlot(UnitTaskType.attack, UnitTaskType.defense, UnitFormationPosition.bombard, required=False)
			]

		elif self == UnitFormationType.basicCityAttackForce:
			return [
				UnitFormationSlot(UnitTaskType.cityBombard, UnitTaskType.ranged, UnitFormationPosition.bombard, required=True),
				UnitFormationSlot(UnitTaskType.cityBombard, UnitTaskType.ranged, UnitFormationPosition.bombard, required=True),
				UnitFormationSlot(UnitTaskType.cityBombard, UnitTaskType.ranged, UnitFormationPosition.bombard, required=True),
				UnitFormationSlot(UnitTaskType.cityBombard, UnitTaskType.ranged, UnitFormationPosition.bombard, required=False),
				UnitFormationSlot(UnitTaskType.cityBombard, UnitTaskType.ranged, UnitFormationPosition.bombard, required=False),
				UnitFormationSlot(UnitTaskType.attack, UnitTaskType.defense, UnitFormationPosition.frontline, required=True),
				UnitFormationSlot(UnitTaskType.attack, UnitTaskType.defense, UnitFormationPosition.frontline, required=True),
				UnitFormationSlot(UnitTaskType.attack, UnitTaskType.defense, UnitFormationPosition.frontline, required=True),
				UnitFormationSlot(UnitTaskType.attack, UnitTaskType.defense, UnitFormationPosition.frontline, required=True),
				UnitFormationSlot(UnitTaskType.attack, UnitTaskType.defense, UnitFormationPosition.frontline, required=False),
				UnitFormationSlot(UnitTaskType.attack, UnitTaskType.defense, UnitFormationPosition.frontline, required=False)
			]
		elif self == UnitFormationType.fastPillagers:
			return [
				UnitFormationSlot(UnitTaskType.attack, UnitTaskType.defense, UnitFormationPosition.frontline, required=True),
				UnitFormationSlot(UnitTaskType.attack, UnitTaskType.defense, UnitFormationPosition.frontline, required=True),
				UnitFormationSlot(UnitTaskType.attack, UnitTaskType.defense, UnitFormationPosition.frontline, required=True)
			]
		elif self == UnitFormationType.settlerEscort:
			return [
				UnitFormationSlot(UnitTaskType.settle, UnitTaskType.settle, UnitFormationPosition.civilianSupport, required=True),
				UnitFormationSlot(UnitTaskType.defense, UnitTaskType.counter, UnitFormationPosition.frontline, required=True)
			]
		elif self == UnitFormationType.navalSquadron:
			return [
				UnitFormationSlot(UnitTaskType.attackSea, UnitTaskType.reserveSea, UnitFormationPosition.frontline, required=True),
				UnitFormationSlot(UnitTaskType.attackSea, UnitTaskType.reserveSea, UnitFormationPosition.frontline, required=True),
				UnitFormationSlot(UnitTaskType.attackSea, UnitTaskType.reserveSea, UnitFormationPosition.frontline, required=False)
			]
		elif self == UnitFormationType.navalInvasion:
			return [
				UnitFormationSlot(UnitTaskType.cityBombard, UnitTaskType.defense, UnitFormationPosition.bombard, required=True),
				UnitFormationSlot(UnitTaskType.cityBombard, UnitTaskType.defense, UnitFormationPosition.bombard, required=True),
				UnitFormationSlot(UnitTaskType.attack, UnitTaskType.defense, UnitFormationPosition.frontline, required=True),
				UnitFormationSlot(UnitTaskType.attack, UnitTaskType.defense, UnitFormationPosition.frontline, required=True),
				UnitFormationSlot(UnitTaskType.attack, UnitTaskType.defense, UnitFormationPosition.frontline, required=True),
				UnitFormationSlot(UnitTaskType.attack, UnitTaskType.defense, UnitFormationPosition.frontline, required=True),
				UnitFormationSlot(UnitTaskType.attack, UnitTaskType.defense, UnitFormationPosition.frontline, required=True),
				UnitFormationSlot(UnitTaskType.escortSea, UnitTaskType.reserveSea, UnitFormationPosition.navalEscort, required=True),
				UnitFormationSlot(UnitTaskType.escortSea, UnitTaskType.reserveSea, UnitFormationPosition.navalEscort, required=True),
				UnitFormationSlot(UnitTaskType.escortSea, UnitTaskType.reserveSea, UnitFormationPosition.navalEscort, required=False),
				UnitFormationSlot(UnitTaskType.escortSea, UnitTaskType.reserveSea, UnitFormationPosition.navalEscort, required=False),
				UnitFormationSlot(UnitTaskType.cityBombard, UnitTaskType.ranged, UnitFormationPosition.bombard, required=False)
			]
		elif self == UnitFormationType.navalEscort:
			return [
				UnitFormationSlot(UnitTaskType.escortSea, UnitTaskType.reserveSea, UnitFormationPosition.frontline, required=True),
				UnitFormationSlot(UnitTaskType.attackSea, UnitTaskType.reserveSea, UnitFormationPosition.frontline, required=True),
				UnitFormationSlot(UnitTaskType.attackSea, UnitTaskType.reserveSea, UnitFormationPosition.frontline, required=False),
				UnitFormationSlot(UnitTaskType.attackSea, UnitTaskType.reserveSea, UnitFormationPosition.frontline, required=False),
				UnitFormationSlot(UnitTaskType.attackSea, UnitTaskType.reserveSea, UnitFormationPosition.frontline, required=False),
				UnitFormationSlot(UnitTaskType.attackSea, UnitTaskType.reserveSea, UnitFormationPosition.frontline, required=False),
				UnitFormationSlot(UnitTaskType.attackSea, UnitTaskType.reserveSea, UnitFormationPosition.frontline, required=False)
			]
		elif self == UnitFormationType.navalBombardment:
			return [
				UnitFormationSlot(UnitTaskType.cityBombard, UnitTaskType.ranged, UnitFormationPosition.bombard, required=True),
				UnitFormationSlot(UnitTaskType.cityBombard, UnitTaskType.ranged, UnitFormationPosition.bombard, required=True),
				UnitFormationSlot(UnitTaskType.attackSea, UnitTaskType.ranged, UnitFormationPosition.bombard, required=False),
				UnitFormationSlot(UnitTaskType.attackSea, UnitTaskType.ranged, UnitFormationPosition.bombard, required=False),
				UnitFormationSlot(UnitTaskType.admiral, UnitTaskType.assaultSea, UnitFormationPosition.civilianSupport, required=False)
			]
		elif self == UnitFormationType.pureNavalCityAttack:
			return [
				UnitFormationSlot(UnitTaskType.attackSea, UnitTaskType.reserveSea, UnitFormationPosition.frontline, required=True),
				UnitFormationSlot(UnitTaskType.attackSea, UnitTaskType.reserveSea, UnitFormationPosition.frontline, required=True),
				UnitFormationSlot(UnitTaskType.cityBombard, UnitTaskType.reserveSea, UnitFormationPosition.bombard, required=True),
				UnitFormationSlot(UnitTaskType.cityBombard, UnitTaskType.reserveSea, UnitFormationPosition.bombard, required=True),
				UnitFormationSlot(UnitTaskType.cityBombard, UnitTaskType.reserveSea, UnitFormationPosition.bombard, required=False),
				UnitFormationSlot(UnitTaskType.carrierSea, UnitTaskType.reserveSea, UnitFormationPosition.bombard, required=False),
				UnitFormationSlot(UnitTaskType.attackSea, UnitTaskType.reserveSea, UnitFormationPosition.frontline, required=True),
				UnitFormationSlot(UnitTaskType.admiral, UnitTaskType.admiral, UnitFormationPosition.civilianSupport, required=False)
			]
		elif self == UnitFormationType.antiBarbarianTeam:
			return [
				UnitFormationSlot(UnitTaskType.fastAttack, UnitTaskType.defense, UnitFormationPosition.frontline, required=True),
				UnitFormationSlot(UnitTaskType.fastAttack, UnitTaskType.defense, UnitFormationPosition.frontline, required=True),
				UnitFormationSlot(UnitTaskType.fastAttack, UnitTaskType.defense, UnitFormationPosition.frontline, required=True),
				UnitFormationSlot(UnitTaskType.cityBombard, UnitTaskType.ranged, UnitFormationPosition.bombard, required=False)
			]

		elif self == UnitFormationType.biggerCityAttackForce:
			return [
				UnitFormationSlot(UnitTaskType.attack, UnitTaskType.fastAttack, UnitFormationPosition.frontline, required=True),
				UnitFormationSlot(UnitTaskType.attack, UnitTaskType.defense, UnitFormationPosition.frontline, required=True),
				UnitFormationSlot(UnitTaskType.attack, UnitTaskType.defense, UnitFormationPosition.frontline, required=True),
				UnitFormationSlot(UnitTaskType.defense, UnitTaskType.counter, UnitFormationPosition.frontline, required=True),
				UnitFormationSlot(UnitTaskType.cityBombard, UnitTaskType.ranged, UnitFormationPosition.bombard, required=True),
				UnitFormationSlot(UnitTaskType.cityBombard, UnitTaskType.ranged, UnitFormationPosition.bombard, required=True),
				UnitFormationSlot(UnitTaskType.cityBombard, UnitTaskType.ranged, UnitFormationPosition.bombard, required=True),
				UnitFormationSlot(UnitTaskType.ranged, UnitTaskType.cityBombard, UnitFormationPosition.bombard, required=True),
				UnitFormationSlot(UnitTaskType.attack, UnitTaskType.counter, UnitFormationPosition.frontline, required=False),
				UnitFormationSlot(UnitTaskType.attack, UnitTaskType.counter, UnitFormationPosition.frontline, required=False),
				UnitFormationSlot(UnitTaskType.general, UnitTaskType.general, UnitFormationPosition.civilianSupport, required=False),
				UnitFormationSlot(UnitTaskType.citySpecial, UnitTaskType.citySpecial, UnitFormationPosition.civilianSupport, required=False)
			]

		elif self == UnitFormationType.colonizationParty:
			return [
				UnitFormationSlot(UnitTaskType.settle, UnitTaskType.settle, UnitFormationPosition.civilianSupport, required=True),
				UnitFormationSlot(UnitTaskType.defense, UnitTaskType.counter, UnitFormationPosition.frontline, required=True),
				UnitFormationSlot(UnitTaskType.escortSea, UnitTaskType.reserveSea, UnitFormationPosition.navalEscort, required=True),
				UnitFormationSlot(UnitTaskType.escortSea, UnitTaskType.reserveSea, UnitFormationPosition.navalEscort, required=False),
				UnitFormationSlot(UnitTaskType.escortSea, UnitTaskType.reserveSea, UnitFormationPosition.navalEscort, required=False)
			]

		elif self == UnitFormationType.quickColonySettler:
			return [
				UnitFormationSlot(UnitTaskType.settle, UnitTaskType.settle, UnitFormationPosition.civilianSupport, required=True)
			]

		elif self == UnitFormationType.closeCityDefense:
			return [
				UnitFormationSlot(UnitTaskType.counter, UnitTaskType.defense, UnitFormationPosition.frontline, required=True),
				UnitFormationSlot(UnitTaskType.ranged, UnitTaskType.defense, UnitFormationPosition.bombard, required=True),
				UnitFormationSlot(UnitTaskType.counter, UnitTaskType.defense, UnitFormationPosition.frontline, required=False),
				UnitFormationSlot(UnitTaskType.ranged, UnitTaskType.defense, UnitFormationPosition.bombard, required=False)
			]

		elif self == UnitFormationType.rapidResponseForce:
			return [
				UnitFormationSlot(UnitTaskType.counter, UnitTaskType.defense, UnitFormationPosition.frontline, required=True),
				UnitFormationSlot(UnitTaskType.fastAttack, UnitTaskType.defense, UnitFormationPosition.frontline, required=True),
				UnitFormationSlot(UnitTaskType.ranged, UnitTaskType.defense, UnitFormationPosition.bombard, required=False),
				UnitFormationSlot(UnitTaskType.fastAttack, UnitTaskType.defense, UnitFormationPosition.frontline, required=False)
			]

		elif self == UnitFormationType.earlyRush:
			return [
				UnitFormationSlot(UnitTaskType.attack, UnitTaskType.fastAttack, UnitFormationPosition.frontline, required=True),
				UnitFormationSlot(UnitTaskType.counter, UnitTaskType.defense, UnitFormationPosition.frontline, required=True),
				UnitFormationSlot(UnitTaskType.cityBombard, UnitTaskType.ranged, UnitFormationPosition.bombard, required=True),
				UnitFormationSlot(UnitTaskType.cityBombard, UnitTaskType.ranged, UnitFormationPosition.bombard, required=True),
				UnitFormationSlot(UnitTaskType.ranged, UnitTaskType.cityBombard, UnitFormationPosition.bombard, required=False),
				UnitFormationSlot(UnitTaskType.ranged, UnitTaskType.cityBombard, UnitFormationPosition.bombard, required=False),
				UnitFormationSlot(UnitTaskType.general, UnitTaskType.general, UnitFormationPosition.civilianSupport, required=False),
				UnitFormationSlot(UnitTaskType.citySpecial, UnitTaskType.citySpecial, UnitFormationPosition.civilianSupport, required=False)
			]
		elif self == UnitFormationType.cityStateInvasion:  # MUFORMATION_CITY_STATE_INVASION
			return [
				UnitFormationSlot(UnitTaskType.cityBombard, UnitTaskType.ranged, UnitFormationPosition.bombard, required=True),
				UnitFormationSlot(UnitTaskType.cityBombard, UnitTaskType.defense, UnitFormationPosition.bombard, required=True),
				UnitFormationSlot(UnitTaskType.attack, UnitTaskType.defense, UnitFormationPosition.frontline, required=True),
				UnitFormationSlot(UnitTaskType.attack, UnitTaskType.defense, UnitFormationPosition.frontline, required=True),
				UnitFormationSlot(UnitTaskType.attackSea, UnitTaskType.reserveSea, UnitFormationPosition.navalEscort, required=True),
				UnitFormationSlot(UnitTaskType.attackSea, UnitTaskType.reserveSea, UnitFormationPosition.navalEscort, required=True),
				UnitFormationSlot(UnitTaskType.assaultSea, UnitTaskType.reserveSea, UnitFormationPosition.navalEscort, required=True),
				UnitFormationSlot(UnitTaskType.assaultSea, UnitTaskType.reserveSea, UnitFormationPosition.navalEscort, required=True),
				UnitFormationSlot(UnitTaskType.assaultSea, UnitTaskType.reserveSea, UnitFormationPosition.navalEscort, required=True),
				UnitFormationSlot(UnitTaskType.admiral, UnitTaskType.admiral, UnitFormationPosition.civilianSupport, required=False)
			]
		elif self == UnitFormationType.cityStateAttackForce:  # MUFORMATION_CITY_STATE_ATTACK_FORCE
			return [
				UnitFormationSlot(UnitTaskType.cityBombard, UnitTaskType.ranged, UnitFormationPosition.bombard, required=True),
				UnitFormationSlot(UnitTaskType.cityBombard, UnitTaskType.ranged, UnitFormationPosition.bombard, required=True),
				UnitFormationSlot(UnitTaskType.cityBombard, UnitTaskType.ranged, UnitFormationPosition.bombard, required=True),
				UnitFormationSlot(UnitTaskType.cityBombard, UnitTaskType.cityBombard, UnitFormationPosition.bombard, required=False),
				UnitFormationSlot(UnitTaskType.cityBombard, UnitTaskType.cityBombard, UnitFormationPosition.bombard, required=False),
				UnitFormationSlot(UnitTaskType.attack, UnitTaskType.defense, UnitFormationPosition.frontline, required=True),
				UnitFormationSlot(UnitTaskType.attack, UnitTaskType.defense, UnitFormationPosition.frontline, required=True),
				UnitFormationSlot(UnitTaskType.attack, UnitTaskType.defense, UnitFormationPosition.frontline, required=True),
				UnitFormationSlot(UnitTaskType.attack, UnitTaskType.defense, UnitFormationPosition.frontline, required=False)
			]

		raise InvalidEnumError(self)

	def isRequiresNavalUnitConsistency(self) -> bool:
		return self == UnitFormationType.navalEscort

	def numberOfFormationSlotEntries(self) -> int:
		return len(self.slots())


class OperationMoveType(ExtendedEnum):
	none = 'none'

	enemyTerritory = 'enemyTerritory'
	singleHex = 'singleHex'
	navalEscort = 'navalEscort'
	freeformNaval = 'freeformNaval'
	rebase = 'rebase'


class OperationStateType(ExtendedEnum):
	none = 'none'

	aborted = 'aborted'
	recruitingUnits = 'recruitingUnits'
	gatheringForces = 'gatheringForces'
	movingToTarget = 'movingToTarget'
	atTarget = 'atTarget'
	successful = 'successful'


class OperationStateReason(ExtendedEnum):
	none = 'none'

	success = 'success'  # AI_ABORT_SUCCESS
	lostPath = 'lostPath'  # AI_ABORT_LOST_PATH
	lostTarget = 'lostTarget'  # AI_ABORT_LOST_TARGET
	noTarget = 'noTarget'  # AI_ABORT_NO_TARGET
	repeatTarget = 'repeatTarget'  # AI_ABORT_REPEAT_TARGET
	noMuster = 'noMuster'  # AI_ABORT_NO_MUSTER
	targetAlreadyCaptured = 'targetAlreadyCaptured'  # AI_ABORT_TARGET_ALREADY_CAPTURED
	noRoomDeploy = 'noRoomDeploy'  # AI_ABORT_NO_ROOM_DEPLOY
	halfStrength = 'halfStrength'  # AI_ABORT_HALF_STRENGTH
	escortDied = 'escortDied'  # AI_ABORT_ESCORT_DIED
	lostCivilian = 'lostCivilian'  # AI_ABORT_LOST_CIVILIAN
	killed = 'killed'  # AI_ABORT_KILLED
	warStateChange = 'warStateChange'  # AI_ABORT_WAR_STATE_CHANGE
	diploOpinionChange = 'diploOpinionChange'  # AI_ABORT_DIPLO_OPINION_CHANGE


class ArmyType(ExtendedEnum):
	none = 'none'

	navalInvasion = 'navalInvasion'  # ARMY_TYPE_NAVAL_INVASION
	land = 'land'  # ARMY_TYPE_LAND


class MilitaryTarget:
	def __init__(self):
		self.targetCity = None
		self.musterCity = None
		self.attackBySea: bool = False
		self.musterNearbyUnitPower: int = 0
		self.targetNearbyUnitPower: int = 0
		self.pathLength: int = 0

	def __eq__(self, other):
		if isinstance(other, MilitaryTarget):
			if self.targetCity is None or self.musterCity is None:
				return False

			if other.targetCity is None or other.musterCity is None:
				return False

			return self.targetCity.location == other.targetCity.location and \
				self.musterCity.location == other.musterCity.location

		raise Exception(f'cannot compare MilitaryTarget to {type(other)}')

	def __hash__(self):
		return hash((self.musterCity.location, self.targetCity.location))


class AttackApproachType(ExtendedEnum):
	none = 'none'  # ATTACK_APPROACH_NONE

	unrestricted = 'unrestricted'  # ATTACK_APPROACH_UNRESTRICTED
	open = 'open'  # ATTACK_APPROACH_OPEN
	neutral = 'neutral'  # ATTACK_APPROACH_NEUTRAL
	limited = 'limited'  # ATTACK_APPROACH_LIMITED
	restricted = 'restricted'  # ATTACK_APPROACH_RESTRICTED
