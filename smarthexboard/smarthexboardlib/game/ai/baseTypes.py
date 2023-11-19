from typing import Optional

from smarthexboard.smarthexboardlib.core.base import ExtendedEnum, InvalidEnumError
from smarthexboard.smarthexboardlib.game.ai.diplomaticTypes import MajorPlayerApproachType
from smarthexboard.smarthexboardlib.game.ai.grandStrategies import GrandStrategyAIType
from smarthexboard.smarthexboardlib.game.flavors import Flavor, FlavorType
from smarthexboard.smarthexboardlib.game.types import TechType


class PlayerStateAllWars(ExtendedEnum):
	neutral = 'neutral'
	winning = 'winning'
	losing = 'losing'


class WarGoalType(ExtendedEnum):
	none = -1, 'none'

	demand = 0, 'demand'  # WAR_GOAL_DEMAND
	prepare = 1, 'prepare'  # WAR_GOAL_PREPARE
	conquest = 2, 'conquest'  # WAR_GOAL_CONQUEST
	damage = 3, 'damage'  # WAR_GOAL_DAMAGE
	peace = 4, 'peace'  # WAR_GOAL_PEACE

	def __new__(cls, value, name):
		member = object.__new__(cls)
		member._value = value
		member._name = name
		return member

	def __lt__(self, other):
		if isinstance(other, WarGoalType):
			return self._value < other._value

		return False


class MilitaryStrategyTypeData:
	def __init__(self, name: str, noMinorCivs: bool, onlyMinorCivs: bool, requiredTech: Optional[TechType],
	             obsoleteTech: Optional[TechType], notBeforeTurnElapsed: int, checkEachTurns: int,
	             minimumAdoptionTurns: int, flavors: [Flavor]):
		self.name = name
		self.noMinorCivs: bool = noMinorCivs
		self.onlyMinorCivs: bool = onlyMinorCivs
		self.requiredTech: Optional[TechType] = requiredTech
		self.obsoleteTech: Optional[TechType] = obsoleteTech
		self.notBeforeTurnElapsed: int = notBeforeTurnElapsed
		self.checkEachTurns: int = checkEachTurns
		self.minimumAdoptionTurns: int = minimumAdoptionTurns
		self.flavors: [Flavor] = flavors


class DefenseState:
	none = 'none'  # NO_DEFENSE_STATE

	critical = 'critical'  # DEFENSE_STATE_CRITICAL
	needed = 'needed'  # DEFENSE_STATE_NEEDED
	neutral = 'neutral'  # DEFENSE_STATE_NEUTRAL
	enough = 'enough'  # DEFENSE_STATE_ENOUGH


class MilitaryStrategyType(ExtendedEnum):
	"""get strategies from https://civilization.fandom.com/wiki/Module:Data/Civ5/BNW/AIMilitaryStrategies"""
	needRanged = 'needRanged'
	enoughRanged = 'enoughRanged'
	needMilitaryUnits = 'needMilitaryUnits'
	enoughMilitaryUnits = 'enoughMilitaryUnits'
	needNavalUnits = 'needNavalUnits'
	needNavalUnitsCritical = 'needNavalUnitsCritical'
	enoughNavalUnits = 'enoughNavalUnits'

	empireDefense = 'empireDefense'
	empireDefenseCritical = 'empireDefenseCritical'
	atWar = 'atWar'
	warMobilization = 'warMobilization'
	eradicateBarbarians = 'eradicateBarbarians'

	winningWars = 'winningWars'
	losingWars = 'losingWars'

	def name(self) -> str:
		return self._data().name

	def isNoMinorCivs(self) -> bool:
		return self._data().noMinorCivs

	def isOnlyMinorCivs(self) -> bool:
		return self._data().onlyMinorCivs

	def requiredTech(self) -> Optional[TechType]:
		return self._data().requiredTech

	def obsoleteTech(self) -> Optional[TechType]:
		return self._data().obsoleteTech

	def notBeforeTurnElapsed(self) -> int:
		return self._data().notBeforeTurnElapsed

	def flavorModifiers(self) -> [Flavor]:
		return self._data().flavors

	def checkEachTurns(self) -> int:
		return self._data().checkEachTurns

	def _data(self) -> MilitaryStrategyTypeData:
		if self == MilitaryStrategyType.needRanged:  # MILITARYAISTRATEGY_NEED_RANGED
			#
			return MilitaryStrategyTypeData(
				name='TXT_KEY_MILITARY_STRATEGY_NONE',
				noMinorCivs=False,
				onlyMinorCivs=False,
				requiredTech=None,
				obsoleteTech=None,
				notBeforeTurnElapsed=25,
				checkEachTurns=2,
				minimumAdoptionTurns=2,
				flavors=[
					Flavor(FlavorType.offense, value=-5),
					Flavor(FlavorType.defense, value=-5),
					Flavor(FlavorType.ranged, value=20)
				]
			)
		elif self == MilitaryStrategyType.enoughRanged:  # MILITARYAISTRATEGY_ENOUGH_RANGED
			return MilitaryStrategyTypeData(
				name='TXT_KEY_MILITARY_STRATEGY_ENOUGH_RANGED',
				noMinorCivs=False,
				onlyMinorCivs=False,
				requiredTech=None,
				obsoleteTech=None,
				notBeforeTurnElapsed=25,
				checkEachTurns=2,
				minimumAdoptionTurns=2,
				flavors=[
					Flavor(FlavorType.offense, value=5),
					Flavor(FlavorType.defense, value=5),
					Flavor(FlavorType.ranged, value=-20)
				]
			)
		elif self == MilitaryStrategyType.needMilitaryUnits:
			return MilitaryStrategyTypeData(
				name='',
				noMinorCivs=False,
				onlyMinorCivs=False,
				requiredTech=None,
				obsoleteTech=None,
				notBeforeTurnElapsed=25,
				checkEachTurns=2,
				minimumAdoptionTurns=2,
				flavors=[]
			)
		elif self == MilitaryStrategyType.enoughMilitaryUnits:  # MILITARYAISTRATEGY_ENOUGH_MILITARY_UNITS
			return MilitaryStrategyTypeData(
				name='TXT_KEY_MILITARY_STRATEGY_ENOUGH_MILITARY_UNITS',
				noMinorCivs=True,
				onlyMinorCivs=False,
				requiredTech=None,
				obsoleteTech=None,
				notBeforeTurnElapsed=25,
				checkEachTurns=2,
				minimumAdoptionTurns=2,
				flavors=[
					Flavor(FlavorType.offense, value=-50),
					Flavor(FlavorType.defense, value=-50),
					Flavor(FlavorType.ranged, value=-50)
				]
			)
		elif self == MilitaryStrategyType.needNavalUnits:  # MILITARYAISTRATEGY_NEED_NAVAL_UNITS
			return MilitaryStrategyTypeData(
				name='TXT_KEY_MILITARY_STRATEGY_NEED_NAVAL_UNITS',
				noMinorCivs=True,
				onlyMinorCivs=False,
				requiredTech=None,
				obsoleteTech=None,
				notBeforeTurnElapsed=50,
				checkEachTurns=2,
				minimumAdoptionTurns=2,
				flavors=[]
			)
		elif self == MilitaryStrategyType.needNavalUnitsCritical:  # MILITARYAISTRATEGY_NEED_NAVAL_UNITS_CRITICAL
			return MilitaryStrategyTypeData(
				name='TXT_KEY_MILITARY_STRATEGY_NEED_NAVAL_UNITS_CRITICAL',
				noMinorCivs=True,
				onlyMinorCivs=False,
				requiredTech=None,
				obsoleteTech=None,
				notBeforeTurnElapsed=50,
				checkEachTurns=2,
				minimumAdoptionTurns=2,
				flavors=[]
			)
		elif self == MilitaryStrategyType.enoughNavalUnits:  # MILITARYAISTRATEGY_ENOUGH_NAVAL_UNITS
			return MilitaryStrategyTypeData(
				name='TXT_KEY_MILITARY_STRATEGY_ENOUGH_NAVAL_UNITS',
				noMinorCivs=True,
				onlyMinorCivs=False,
				requiredTech=None,
				obsoleteTech=None,
				notBeforeTurnElapsed=50,
				checkEachTurns=2,
				minimumAdoptionTurns=2,
				flavors=[]
			)
		elif self == MilitaryStrategyType.empireDefense:  # MILITARYAISTRATEGY_EMPIRE_DEFENSE
			return MilitaryStrategyTypeData(
				name='TXT_KEY_MILITARY_STRATEGY_EMPIRE_DEFENSE',
				noMinorCivs=True,
				onlyMinorCivs=False,
				requiredTech=None,
				obsoleteTech=None,
				notBeforeTurnElapsed=25,
				checkEachTurns=2,
				minimumAdoptionTurns=2,
				flavors=[]
			)
		elif self == MilitaryStrategyType.empireDefenseCritical:  # MILITARYAISTRATEGY_EMPIRE_DEFENSE_CRITICAL
			return MilitaryStrategyTypeData(
				name='TXT_KEY_MILITARY_STRATEGY_EMPIRE_DEFENSE_CRITICAL',
				noMinorCivs=False,
				onlyMinorCivs=False,
				requiredTech=None,
				obsoleteTech=None,
				notBeforeTurnElapsed=25,
				checkEachTurns=2,
				minimumAdoptionTurns=5,
				flavors=[]
			)
		elif self == MilitaryStrategyType.atWar:  # MILITARYAISTRATEGY_AT_WAR
			return MilitaryStrategyTypeData(
				name='TXT_KEY_MILITARY_STRATEGY_AT_WAR',
				noMinorCivs=True,
				onlyMinorCivs=False,
				requiredTech=None,
				obsoleteTech=None,
				notBeforeTurnElapsed=-1,
				checkEachTurns=1,
				minimumAdoptionTurns=5,
				flavors=[
					Flavor(FlavorType.offense, value=15),
					Flavor(FlavorType.defense, value=15),
					Flavor(FlavorType.ranged, value=15),
					Flavor(FlavorType.cityDefense, value=10),
					Flavor(FlavorType.wonder, value=-10)
				]
			)
		elif self == MilitaryStrategyType.warMobilization:  # MILITARYAISTRATEGY_WAR_MOBILIZATION
			return MilitaryStrategyTypeData(
				name='TXT_KEY_MILITARY_STRATEGY_WAR_MOBILIZATION',
				noMinorCivs=True,
				onlyMinorCivs=False,
				requiredTech=None,
				obsoleteTech=None,
				notBeforeTurnElapsed=-1,
				checkEachTurns=5,
				minimumAdoptionTurns=15,
				flavors=[
					Flavor(FlavorType.offense, value=10),
					Flavor(FlavorType.defense, value=10),
					Flavor(FlavorType.ranged, value=10),
					Flavor(FlavorType.militaryTraining, value=10)
				]
			)
		elif self == MilitaryStrategyType.eradicateBarbarians:  # MILITARYAISTRATEGY_ERADICATE_BARBARIANS
			return MilitaryStrategyTypeData(
				name='TXT_KEY_MILITARY_STRATEGY_ERADICATE_BARBARIANS',
				noMinorCivs=True,
				onlyMinorCivs=False,
				requiredTech=None,
				obsoleteTech=None,
				notBeforeTurnElapsed=25,
				checkEachTurns=5,
				minimumAdoptionTurns=5,
				flavors=[
					Flavor(FlavorType.offense, value=5)
				]
			)
		elif self == MilitaryStrategyType.winningWars:  # MILITARYAISTRATEGY_WINNING_WARS
			return MilitaryStrategyTypeData(
				name='TXT_KEY_MILITARY_STRATEGY_WINNING_WARS',
				noMinorCivs=True,
				onlyMinorCivs=False,
				requiredTech=None,
				obsoleteTech=None,
				notBeforeTurnElapsed=-1,
				checkEachTurns=2,
				minimumAdoptionTurns=2,
				flavors=[
					Flavor(FlavorType.offense, value=5),
					Flavor(FlavorType.defense, value=-5)
				]
			)
		elif self == MilitaryStrategyType.losingWars:  # MILITARYAISTRATEGY_LOSING_WARS
			return MilitaryStrategyTypeData(
				name='TXT_KEY_MILITARY_STRATEGY_LOSING_WARS',
				noMinorCivs=True,
				onlyMinorCivs=False,
				requiredTech=None,
				obsoleteTech=None,
				notBeforeTurnElapsed=-1,
				checkEachTurns=2,
				minimumAdoptionTurns=2,
				flavors=[
					Flavor(FlavorType.offense, value=-5),
					Flavor(FlavorType.defense, value=5),
					Flavor(FlavorType.cityDefense, value=25),
					Flavor(FlavorType.expansion, value=-15),
					Flavor(FlavorType.tileImprovement, value=-10),
					Flavor(FlavorType.recon, value=-15),
					Flavor(FlavorType.wonder, value=-15)
				]
			)

		# MILITARYAISTRATEGY_MINOR_CIV_GENERAL_DEFENSE={
		# OnlyMinorCivs=true;
		# CheckTriggerTurnCount=50;
		# MinimumNumTurnsExecuted=50;
		# AdvisorCounselImportance=1;};
		#
		# MILITARYAISTRATEGY_MINOR_CIV_THREAT_ELEVATED={
		# OnlyMinorCivs=true;
		# CheckTriggerTurnCount=5;
		# MinimumNumTurnsExecuted=5;
		# AdvisorCounselImportance=1;};
		#
		# MILITARYAISTRATEGY_MINOR_CIV_THREAT_CRITICAL={
		# OnlyMinorCivs=true;
		# CheckTriggerTurnCount=5;
		# MinimumNumTurnsExecuted=5;
		# AdvisorCounselImportance=1;};

		# MILITARYAISTRATEGY_NEED_MOBILE={
		# CheckTriggerTurnCount=2;
		# FirstTurnExecuted=25;
		# MinimumNumTurnsExecuted=2;
		# AdvisorCounselImportance=1;};
		#
		# MILITARYAISTRATEGY_ENOUGH_MOBILE={
		# CheckTriggerTurnCount=2;
		# FirstTurnExecuted=25;
		# MinimumNumTurnsExecuted=2;
		# AdvisorCounselImportance=1;};
		#
		# MILITARYAISTRATEGY_NEED_AIR={
		# NoMinorCivs=true;
		# CheckTriggerTurnCount=2;
		# FirstTurnExecuted=25;
		# MinimumNumTurnsExecuted=2;
		# TechPrereq="TECH_FLIGHT";
		# AdvisorCounselImportance=1;};
		#
		# MILITARYAISTRATEGY_NEED_NUKE={
		# NoMinorCivs=true;
		# CheckTriggerTurnCount=2;
		# FirstTurnExecuted=25;
		# MinimumNumTurnsExecuted=2;
		# TechPrereq="TECH_ATOMIC_THEORY";
		# AdvisorCounselImportance=1;};
		#
		# MILITARYAISTRATEGY_ENOUGH_AIR={
		# NoMinorCivs=true;
		# CheckTriggerTurnCount=2;
		# FirstTurnExecuted=25;
		# MinimumNumTurnsExecuted=2;
		# TechPrereq="TECH_FLIGHT";
		# AdvisorCounselImportance=1;};
		#
		# MILITARYAISTRATEGY_NEED_ANTIAIR={
		# CheckTriggerTurnCount=2;
		# FirstTurnExecuted=25;
		# MinimumNumTurnsExecuted=2;
		# TechPrereq="TECH_RADIO";
		# AdvisorCounselImportance=1;};
		#
		# MILITARYAISTRATEGY_ENOUGH_ANTIAIR={
		# CheckTriggerTurnCount=2;
		# FirstTurnExecuted=25;
		# MinimumNumTurnsExecuted=2;
		# TechPrereq="TECH_RADIO";
		# AdvisorCounselImportance=1;};
		#
		# MILITARYAISTRATEGY_NEED_AIR_CARRIER={
		# CheckTriggerTurnCount=2;
		# MinimumNumTurnsExecuted=2;
		# TechPrereq="TECH_FLIGHT";
		# AdvisorCounselImportance=1;};

		raise InvalidEnumError(self)

	def shouldBeActiveFor(self, player, simulation) -> bool:
		if self == MilitaryStrategyType.needRanged:
			return self._shouldBeActiveNeedRangedFor(player, simulation)
		elif self == MilitaryStrategyType.enoughRanged:
			return self._shouldBeActiveEnoughRangedFor(player, simulation)
		elif self == MilitaryStrategyType.needMilitaryUnits:
			return self._shouldBeActiveNeedMilitaryUnitsFor(player, simulation)
		elif self == MilitaryStrategyType.enoughMilitaryUnits:
			return self._shouldBeActiveEnoughMilitaryUnitsFor(player, simulation)
		elif self == MilitaryStrategyType.needNavalUnits:
			return self._shouldBeActiveNeedNavalUnitsFor(player, simulation)
		elif self == MilitaryStrategyType.needNavalUnitsCritical:
			return False  # FIXME
		elif self == MilitaryStrategyType.enoughNavalUnits:
			return False  # FIXME
		elif self == MilitaryStrategyType.empireDefense:
			return self._shouldBeActiveEmpireDefenseFor(player, simulation)
		elif self == MilitaryStrategyType.empireDefenseCritical:
			return self._shouldBeActiveEmpireDefenseCriticalFor(player, simulation)
		elif self == MilitaryStrategyType.atWar:
			return self._shouldBeActiveAtWarFor(player, simulation)
		elif self == MilitaryStrategyType.warMobilization:
			return self._shouldBeActiveWarMobilizationFor(player, simulation)
		elif self == MilitaryStrategyType.eradicateBarbarians:
			return self._shouldBeActiveEradicateBarbariansFor(player, simulation)
		elif self == MilitaryStrategyType.winningWars:
			return self._shouldBeActiveWinningWarsFor(player)
		elif self == MilitaryStrategyType.losingWars:
			return self._shouldBeActiveLosingWarsFor(player)

	def _shouldBeActiveNeedRangedFor(self, player, simulation) -> bool:
		# @fixme
		return False

	def _shouldBeActiveEnoughRangedFor(self, player, simulation) -> bool:
		# @fixme
		return False

	def _shouldBeActiveNeedMilitaryUnitsFor(self, player, simulation) -> bool:
		# @fixme
		return False

	def _shouldBeActiveEnoughMilitaryUnitsFor(self, player, simulation) -> bool:
		# @fixme
		return False

	def _shouldBeActiveEmpireDefenseFor(self, player, simulation) -> bool:
		"""
		Empire Defense" Player Strategy: Adjusts military flavors if the player doesn't have the recommended number of units
		@param player:
		@param simulation:
		@return:
		"""
		if player.militaryAI.landDefenseState() == DefenseState.needed:  # DEFENSE_STATE_NEEDED
			return True

		return False

	def _shouldBeActiveEmpireDefenseCriticalFor(self, player, simulation) -> bool:
		# @fixme
		return False

	def _shouldBeActiveAtWarFor(self, player, simulation) -> bool:
		return player.atWarCount() > 0

	def _shouldBeActiveWarMobilizationFor(self, player, simulation) -> bool:
		# If we're at war don't bother with this Strategy
		militaryAI = player.militaryAI
		diplomacyAI = player.diplomacyAI
		grandStrategyAI = player.grandStrategyAI

		if militaryAI.militaryStrategyAdoption.adopted(MilitaryStrategyType.atWar):
			return False

		iCurrentWeight: int = 0

		# Are we running the Conquest Grand Strategy?
		if grandStrategyAI.activeStrategy == GrandStrategyAIType.conquest:
			iCurrentWeight += 25

		for otherPlayer in simulation.players:
			if otherPlayer != player:
				if not player.hasMetWith(otherPlayer):
					continue

				if diplomacyAI.warGoalTowards(otherPlayer) == WarGoalType.prepare:
					iCurrentWeight += 100

				if otherPlayer.isMajorAI() or otherPlayer.isHuman():
					approach = player.diplomacyAI.majorApproachTowards(otherPlayer)

					# Add in weight for each civ we're on really bad terms with
					if approach == MajorPlayerApproachType.war or \
						approach == MajorPlayerApproachType.hostile or \
						approach == MajorPlayerApproachType.afraid:
						iCurrentWeight += 50

					# And some if on fairly bad terms
					# Add in weight for each civ we're on really bad terms with
					if approach == MajorPlayerApproachType.guarded or \
						approach == MajorPlayerApproachType.deceptive:
						iCurrentWeight += 25

		return iCurrentWeight >= 100

	def _shouldBeActiveEradicateBarbariansFor(self, player, simulation) -> bool:
		# If we're at war don't bother with this Strategy
		if player.militaryAI.militaryStrategyAdoption.adopted(MilitaryStrategyType.atWar):
			return False

		# Also don't bother, if we're building up for a sneak attack
		for loopPlayer in simulation.players:
			if not player == loopPlayer and loopPlayer.isAlive() and player.hasMetWith(loopPlayer):
				if player.diplomacyAI.warGoalTowards(loopPlayer) == WarGoalType.prepare:
					return False

		# If we have an operation of this type running, we don't want to turn this strategy off
		# FIXME
		# if (pPlayer->haveAIOperationOfType(AI_OPERATION_DESTROY_BARBARIAN_CAMP)):
		# return true;

		# Two visible camps or 4 Barbarians will trigger this
		strategyWeight = player.militaryAI.barbarianData().barbarianCampCount * 50 + \
		                 player.militaryAI.barbarianData().visibleBarbarianCount * 25

		if strategyWeight >= 100:
			return True

		return False

	def _shouldBeActiveWinningWarsFor(self, player) -> bool:
		return player.diplomacyAI.stateOfAllWars == PlayerStateAllWars.winning

	def _shouldBeActiveLosingWarsFor(self, player) -> bool:
		return player.diplomacyAI.stateOfAllWars == PlayerStateAllWars.losing

	def _shouldBeActiveNeedNavalUnitsFor(self, player, simulation) -> bool:
		""" "Need Naval Units Critical" Strategy: build navies NOW"""
		if player.militaryAI.navalDefenseState() == DefenseState.critical:  # DEFENSE_STATE_CRITICAL
			return True
		
		return False
