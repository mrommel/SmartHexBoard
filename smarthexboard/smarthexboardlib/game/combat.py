import math
import random

from smarthexboard.smarthexboardlib.core.base import ExtendedEnum
from smarthexboard.smarthexboardlib.game.cityStates import CityStateType
from smarthexboard.smarthexboardlib.game.greatPersons import GreatPersonPoints
from smarthexboard.smarthexboardlib.game.notifications import NotificationType
from smarthexboard.smarthexboardlib.game.states.ui import CityAnimationType
from smarthexboard.smarthexboardlib.game.types import TechType
from smarthexboard.smarthexboardlib.game.unitTypes import UnitType, UnitAutomationType, UnitAnimationType
from smarthexboard.smarthexboardlib.map.types import UnitDomainType, ArchaeologicalRecordType
from smarthexboard.smarthexboardlib.utils.base import isinstance_string


class CombatResultType(ExtendedEnum):
	totalDefeat = 'totalDefeat'
	majorDefeat = 'majorDefeat'
	minorDefeat = 'minorDefeat'
	stalemate = 'stalemate'
	minorVictory = 'minorVictory'
	majorVictory = 'majorVictory'
	totalVictory = 'totalVictory'


class CombatResult:
	def __init__(self, defenderDamage: int, attackerDamage: int, value: CombatResultType):
		self.defenderDamage = defenderDamage
		self.attackerDamage = attackerDamage
		self.value = value


class Combat:
	@staticmethod
	def predictMeleeAttack(attacker, defender, simulation) -> CombatResult:
		attackerTile = simulation.tileAt(attacker.location)
		defenderTile = simulation.tileAt(defender.location)

		if not isinstance_string(attacker, 'Unit'):
			raise Exception(f'attack of unsupported type: {attacker}')

		if isinstance_string(defender, 'Unit'):
			# attacker strikes
			attackerStrength = attacker.attackStrengthAgainst(defender, None, defenderTile, simulation)
			defenderStrength = defender.defensiveStrengthAgainst(attacker, None, defenderTile, ranged=False, simulation=simulation)
			attackerStrengthDifference = attackerStrength - defenderStrength

			defenderDamage: int = int(30.0 * pow(math.e, 0.04 * float(attackerStrengthDifference)))

			if defenderDamage < 0:
				defenderDamage = 0

			# defender strikes back
			attackerStrength2 = defender.attackStrengthAgainst(attacker, None, attackerTile, simulation)
			defenderStrength2 = attacker.defensiveStrengthAgainst(defender, None, attackerTile, ranged=True, simulation=simulation)

			defenderStrengthDifference = attackerStrength2 - defenderStrength2

			attackerDamage: int = int(30.0 * pow(math.e, 0.04 * float(defenderStrengthDifference)))

			if attackerDamage < 0:
				attackerDamage = 0

			# no damage for attacker, no suppression to cities
			value = Combat.evaluateResult(
				defenderHealth=defender.healthPoints(),
				defenderDamage=defenderDamage,
				attackerHealth=attacker.healthPoints(),
				attackerDamage=attackerDamage
			)
			return CombatResult(defenderDamage=defenderDamage, attackerDamage=attackerDamage, value=value)
		elif isinstance_string(defender, 'City'):
			# attacker strikes
			attackerStrength = attacker.attackStrengthAgainst(None, defender, defenderTile, simulation)
			defenderStrength = defender.defensiveStrengthAgainst(attacker, defenderTile, ranged=False, simulation=simulation)
			attackerStrengthDifference = attackerStrength - defenderStrength

			defenderDamage: int = int(30.0 * pow(math.e, 0.04 * float(attackerStrengthDifference)))

			if defenderDamage < 0:
				defenderDamage = 0

			# defender strikes back
			attackerStrength2 = defender.rangedCombatStrengthAgainst(attacker, attackerTile)
			defenderStrength2 = attacker.defensiveStrengthAgainst(None, defender, attackerTile, ranged=True, simulation=simulation)

			defenderStrengthDifference = attackerStrength2 - defenderStrength2

			attackerDamage: int = int(30.0 * pow(math.e, 0.04 * float(defenderStrengthDifference)))

			if attackerDamage < 0:
				attackerDamage = 0

			# no damage for attacker, no suppression to cities
			value = Combat.evaluateResult(
				defenderHealth=defender.healthPoints(),
				defenderDamage=defenderDamage,
				attackerHealth=attacker.healthPoints(),
				attackerDamage=attackerDamage
			)
			return CombatResult(defenderDamage=defenderDamage, attackerDamage=attackerDamage, value=value)
		else:
			raise Exception(f'attack against unsupported type: {defender}')

	@classmethod
	def predictRangedAttack(cls, attacker, defender, simulation) -> CombatResult:
		# attackerTile = simulation.tileAt(attacker.location)
		defenderTile = simulation.tileAt(defender.location)

		if isinstance_string(attacker, 'City') and isinstance_string(defender, 'Unit'):
			attackerStrength = attacker.rangedCombatStrengthAgainst(defender, defenderTile)
			defenderStrength = defender.defensiveStrengthAgainst(None, attacker, defenderTile, ranged=True, simulation=simulation)
			strengthDifference = attackerStrength - defenderStrength

			damage: int = int(30.0 * pow(math.e, 0.04 * float(strengthDifference)))

			if damage < 0:
				damage = 0

			# no damage for attacker, no suppression to cities
			value = Combat.evaluateResult(
				defenderHealth=defender.healthPoints(),
				defenderDamage=damage,
				attackerHealth=attacker.healthPoints(),
				attackerDamage=0
			)
			return CombatResult(defenderDamage=damage, attackerDamage=0, value=value)
		elif isinstance_string(attacker, 'Unit') and isinstance_string(defender, 'Unit'):
			attackerStrength = attacker.rangedCombatStrengthAgainst(defender, None, defenderTile, attacking=True, simulation=simulation)
			defenderStrength = defender.defensiveStrengthAgainst(attacker, None, defenderTile, ranged=True, simulation=simulation)
			strengthDifference = attackerStrength - defenderStrength

			damage: int = int(30.0 * pow(math.e, 0.04 * float(strengthDifference)))

			if damage < 0:
				damage = 0

			# no damage for attacker
			value = Combat.evaluateResult(
				defenderHealth=defender.healthPoints(),
				defenderDamage=damage,
				attackerHealth=attacker.healthPoints(),
				attackerDamage=0
			)
			return CombatResult(defenderDamage=damage, attackerDamage=0, value=value)
		elif isinstance_string(attacker, 'Unit') and isinstance_string(defender, 'City'):
			attackerStrength = attacker.rangedCombatStrengthAgainst(None, defender, defenderTile, attacking=True, simulation=simulation)
			defenderStrength = defender.defensiveStrengthAgainst(attacker, defenderTile, ranged=True, simulation=simulation)
			strengthDifference = attackerStrength - defenderStrength

			damage: int = int(30.0 * pow(math.e, 0.04 * float(strengthDifference)))

			if damage < 0:
				damage = 0

			# no damage for attacker
			value = Combat.evaluateResult(
				defenderHealth=defender.healthPoints(),
				defenderDamage=damage,
				attackerHealth=attacker.healthPoints(),
				attackerDamage=0
			)
			return CombatResult(defenderDamage=damage, attackerDamage=0, value=value)
		else:
			raise Exception(f'unsupported combination of attacker / defender: {attacker} / {defender}')

	@classmethod
	def doAirAttack(cls, attacker, plot, simulation) -> CombatResult:
		raise Exception('not implemented')

	@classmethod
	def doMeleeAttack(cls, attacker, defender, simulation):
		# CvUnitCombat::Attack
		attackerTile = simulation.tileAt(attacker.location)
		defenderTile = simulation.tileAt(defender.location)
		attackerPlayer = attacker.player
		defenderPlayer = defender.player
		activePlayer = simulation.activePlayer()

		if not isinstance_string(attacker, 'Unit'):
			raise Exception(f'attack of unsupported type: {attacker}')

		attackAgainstUnit = isinstance_string(defender, 'Unit')
		attackAgainstCity = isinstance_string(defender, 'City')

		if not attackAgainstUnit and not attackAgainstCity:
			raise Exception(f'defender of unsupported type: {defender}')

		# Unit that attacks loses his fortification bonus
		attacker.doMobilize(simulation)

		attacker.automate(UnitAutomationType.none, simulation)

		if attackAgainstUnit:
			defender.automate(UnitAutomationType.none, simulation)

		attacker.setMadeAttackTo(True)

		if attacker.isDelayedDeath() or (attackAgainstUnit and defender.isDelayedDeath()):
			raise Exception("Trying to battle and one of the units is already dead!")

		simulation.userInterface.animateUnit(attacker, UnitAnimationType.attack, attacker.location, defender.location)

		# attacker strikes
		attackerStrength = 0
		defenderStrength = 0
		if attackAgainstUnit:
			attackerStrength = attacker.attackStrengthAgainst(defender, None, defenderTile, simulation)
			defenderStrength = defender.defensiveStrengthAgainst(attacker, None, defenderTile, ranged=False,  simulation=simulation)
		elif attackAgainstCity:
			attackerStrength = attacker.attackStrengthAgainst(None, defender, defenderTile, simulation)
			defenderStrength = defender.defensiveStrengthAgainst(attacker, defenderTile, ranged=False, simulation=simulation)

		attackerStrengthDifference = attackerStrength - defenderStrength

		defenderDamage: int = int(30.0 * pow(math.e, 0.04 * float(attackerStrengthDifference) * random.uniform(0.8, 1.2)))

		if defenderDamage < 0:
			defenderDamage = 0

		attackerDamage: int = 0
		attackerStrength2: int = 0
		defenderStrength2: int = 0

		if (attackAgainstUnit and defender.canDefend()) or attackAgainstCity:
			# defender strikes back
			if attackAgainstUnit:
				attackerStrength2 = defender.attackStrengthAgainst(attacker, None, attackerTile, simulation)
				defenderStrength2 = attacker.defensiveStrengthAgainst(defender, None, attackerTile, ranged=False, simulation=simulation)
			elif attackAgainstCity:
				attackerStrength2 = defender.rangedCombatStrengthAgainst(attacker, attackerTile)
				defenderStrength2 = attacker.defensiveStrengthAgainst(None, defender, attackerTile, ranged=True, simulation=simulation)

			defenderStrengthDifference = attackerStrength2 - defenderStrength2

			attackerDamage: int = int(30.0 * pow(math.e, 0.04 * float(defenderStrengthDifference) * random.uniform(0.8, 1.2)))

			if attackerDamage < 0:
				attackerDamage = 0
		else:
			# kill the unit (civilian?)
			defender.doKill(delayed=False, otherPlayer=attackerPlayer, simulation=simulation)

			defenderPlayer.notifications.addNotification(NotificationType.unitDied, location=defender.location)

			# Move forward
			if attacker.canMoveInto(defenderTile.point, options=[], simulation=simulation):
				# attacker.doMoveOn(defenderTile.point, simulation)
				# attacker.queueMoveForVisualization(from: attacker.location, to: defenderTile.point, simulation)
				# attacker.doMoveOnPath(towards: defenderTile.point, previousETA: 0, buildingRoute: false, simulation)
				# simulation.userInterface?.move(unit: attacker, on: [attacker.location, defenderTile.point])
				pass

		value = Combat.evaluateResult(
			defenderHealth=defender.healthPoints(),
			defenderDamage=defenderDamage,
			attackerHealth=attacker.healthPoints(),
			attackerDamage=attackerDamage
		)

		# apply damage
		attacker.changeDamage(attackerDamage, attackerPlayer, simulation)
		if attackAgainstUnit:
			defender.changeDamage(defenderDamage, attackerPlayer, simulation)
		elif attackAgainstCity:
			defender.changeDamage(defenderDamage)

		# experience
		attackerBaseExperience: float = 5.0  # EXPERIENCE_ATTACKING_UNIT_MELEE
		attackerExperienceModifier: float = 1.0

		# kabul suzerain bonus
		if attackerPlayer.isSuzerainOf(CityStateType.kabul, simulation):
			# Your units receive double experience from battles they initiate.
			attackerExperienceModifier += 1.0

		attackerExperienceModifier += attacker.experienceModifier()

		attacker.changeExperienceBy(int(attackerBaseExperience * attackerExperienceModifier), simulation)

		defenderBaseExperience: float = 4.0  # EXPERIENCE_DEFENDING_UNIT_MELEE
		defenderExperienceModifier: float = 1.0
		if attackAgainstUnit:
			defenderExperienceModifier += defender.experienceModifier()
			defender.changeExperienceBy(int(defenderBaseExperience * defenderExperienceModifier), simulation)

		# add archaeological record(only melee combat)
		defenderTile.addArchaeologicalRecord(ArchaeologicalRecordType.battleMelee, simulation.worldEra(), attackerPlayer.leader, defenderPlayer.leader)

		# Attacker died
		if attacker.healthPoints() <= 0:
			if activePlayer is not None and activePlayer == attackerPlayer:
				# simulation.userInterface.showTooltip(
				# 	attackerTile.point,
				# 	TooltipType.unitDiedAttacking,
				# 	attackerName=attacker.name(),
				# 	defenderName=defender.name(),
				# 	defenderDamage=defenderDamage,
				# 	delay: 3
				# )
				pass

			if activePlayer is not None and activePlayer == defenderPlayer:
				# simulation.userInterface?.showTooltip(
				# 	at: defenderTile.point,
				# 	type:.enemyUnitDiedAttacking(
				# 	attackerName: attacker.name(),
				# 	attackerPlayer: attacker.player,
				# 	defenderName: defender.name(),
				# 	defenderDamage: defenderDamage
				# 	),
				# 	delay: 3
				# )

				attacker.doKill(delayed=False, otherPlayer=None, simulation=simulation)
				defender.player.updateWarWearinessAgainst(attackerPlayer, defender.location, killed=False, simulation=simulation)
				attacker.player.updateWarWearinessAgainst(defenderPlayer, defender.location, killed=True, simulation=simulation)

		elif defender.healthPoints() <= 0:  # Defender died
			if activePlayer is not None and activePlayer == attackerPlayer:
				# simulation.userInterface?.showTooltip(
				# 	at: defenderTile.point,
				# 	type:.unitDestroyedEnemyUnit(  conqueredEnemyCity
				# 		attackerName: attacker.name(),
				# 	attackerDamage: attackerDamage,
				# 	defenderName: defender.name()
				# 	),
				# 	delay: 3
				# )
				pass

			if activePlayer is not None and activePlayer == defenderPlayer:
				# simulation.userInterface?.showTooltip(
				# 	at: defenderTile.point,
				# 	type:.unitDiedDefending(   cityCapturedByEnemy
				# 	attackerName: attacker.name(),
				# 	attackerPlayer: attacker.player,
				# 	attackerDamage: attackerDamage,
				# 	defenderName: defender.name()),
				# 	delay: 3
				# )
				pass

			if attackAgainstUnit:
				defender.player.notifications.addNotification(NotificationType.unitDied, location=defenderTile.point)

				# Wolin - suzerain bonus:
				# Receive Great General points when a land unit defeats a major or minor civilization's unit and
				# receive Great Admiral points when a naval unit defeats a major or minor civilization's unit equal
				# to 25% of the opposing unit's strength (Standard Speed).
				if not defenderPlayer.isBarbarian():
					if attackerPlayer.isSuzerainOf(CityStateType.wolin, simulation):
						if attacker.domain() == UnitDomainType.land:
							attackerPlayer.greatPeople.addPoints(GreatPersonPoints(greatGeneral=int(defenderDamage / 4)))
						elif attacker.domain() == UnitDomainType.sea:
							attackerPlayer.greatPeople.addPoints(GreatPersonPoints(greatAdmiral=int(defenderDamage / 4)))

				if attacker.unitType == UnitType.slinger:
					if not attackerPlayer.techs.eurekaTriggeredFor(TechType.archery):
						attackerPlayer.techs.triggerEurekaFor(TechType.archery, simulation)

				defender.doKill(delayed=False, otherPlayer=attackerPlayer, simulation=simulation)
				defenderPlayer.updateWarWearinessAgainst(attackerPlayer, defender.location, killed=True, simulation=simulation)
				attackerPlayer.updateWarWearinessAgainst(defenderPlayer, defender.location, killed=False, simulation=simulation)

			if attackAgainstCity:
				defenderPlayer.notifications.addNotification(NotificationType.cityLost, location=defenderTile.point)

				attackerPlayer.acquireCity(defender, conquest=True, gift=False, simulation=simulation)
				defenderPlayer.updateWarWearinessAgainst(attackerPlayer, defender.location, killed=True, simulation=simulation)
				attackerPlayer.updateWarWearinessAgainst(defenderPlayer, defender.location, killed=False, simulation=simulation)

				# new owner can now decide what to do with this city
				if attackerPlayer.isHuman():
					attackerPlayer.notifications.addNotification(NotificationType.cityAcquired, cityName=defender.name(), location=defenderTile.point)
				else:
					# ai players always keep conquered city for now
					pass

			# Move forward
			if attacker.canMoveInto(defenderTile.point, options=[], simulation=simulation):
				attacker.queueMoveForVisualization(attacker.location, defenderTile.point, simulation)
				attacker.doMoveOnPathTowards(defenderTile.point, previousETA=0, buildingRoute=False, simulation=simulation)
				# simulation.userInterface?.move(unit: attacker, on: [attacker.location, defenderTile.point])

		else:  # just damage to both
			if activePlayer is not None and activePlayer == attackerPlayer:
				# simulation.userInterface.showTooltip(
				# 	defenderTile.point,
				# 	TooltipType.unitAttackingWithdraw,
				# 	attackerName=attacker.name(),
				# 	attackerDamage=attackerDamage,
				# 	defenderName=defender.name(),
				# 	defenderDamage=defenderDamage,
				# 	delay=3
				# )
				pass

			if activePlayer is not None and activePlayer == defenderPlayer:
				# simulation.userInterface.showTooltipAt(
				# 	defenderTile.point,
				# 	TooltipType.enemyAttackingWithdraw,
				# 	attackerName=attacker.name(),
				# 	attackerDamage=attackerDamage,
				# 	defenderName=defender.name(),
				# 	defenderDamage=defenderDamage,
				# 	delay=3
				# )
				pass

			defenderPlayer.updateWarWearinessAgainst(attackerPlayer, defender.location, killed=False, simulation=simulation)
			attacker.player.updateWarWearinessAgainst(defender.player, defender.location, killed=False, simulation=simulation)

		# If a Unit loses his moves after attacking, do so
		if not attacker.canMoveAfterAttacking():
			attacker.finishMoves()
			# GC.GetEngineUserInterface()->changeCycleSelectionCounter(1);

		return CombatResult(defenderDamage=defenderDamage, attackerDamage=attackerDamage, value=value)

	@classmethod
	def doRangedAttack(cls, attacker, defender, simulation):
		# pre-check
		attackerIsUnit = isinstance_string(attacker, 'Unit')
		attackerIsCity = isinstance_string(attacker, 'City')
		defenderIsUnit = isinstance_string(defender, 'Unit')
		defenderIsCity = isinstance_string(defender, 'City')

		if not((attackerIsUnit and defenderIsUnit) or
			(attackerIsCity and defenderIsUnit) or
			(attackerIsUnit and defenderIsCity)):
			raise Exception(f'combination of attacker and defender not supported: {type(attacker)} => {type(defender)}')

		activePlayer = simulation.activePlayer()
		attackerPlayer = attacker.player
		defenderPlayer = defender.player

		defenderTile = simulation.tileAt(defender.location)

		if defenderTile is None:
			raise Exception("cant get defenderTile")

		if defenderIsUnit:
			defender.automate(UnitAutomationType.none, simulation)

		attacker.setMadeAttackTo(True)  # same for city and unit attacker

		if attackerIsCity:
			simulation.userInterface.animateCity(attacker, CityAnimationType.rangeAttack, attacker.location, defender.location)
		elif attackerIsUnit:
			simulation.userInterface.animateUnit(attacker, UnitAnimationType.rangeAttack, attacker.location, defender.location)

		# attacker strikes
		attackerStrength = 0
		if attackerIsCity:
			attackerStrength = attacker.rangedCombatStrengthAgainst(defender, defenderTile)
		elif attackerIsUnit:
			if defenderIsUnit:
				attackerStrength = attacker.rangedCombatStrengthAgainst(defender, None, defenderTile, attacking=True, simulation=simulation)
			elif defenderIsCity:
				attackerStrength = attacker.rangedCombatStrengthAgainst(None, defender, defenderTile, attacking=True, simulation=simulation)
			else:
				raise Exception('Unsupported combination')

		if defenderIsUnit:
			defenderStrength = defender.defensiveStrengthAgainst(attacker, None, defenderTile, ranged=False, simulation=simulation)
		elif defenderIsCity:
			defenderStrength = defender.defensiveStrengthAgainst(attacker, defenderTile, ranged=False, simulation=simulation)
		else:
			raise Exception('Unsupported combination')

		attackerStrengthDifference = attackerStrength - defenderStrength

		defenderDamage: int = int(30.0 * pow(math.e, 0.04 * float(attackerStrengthDifference)) * random.uniform(0.8, 1.2))

		if defenderDamage < 0:
			defenderDamage = 0

		value = Combat.evaluateResult(
			defenderHealth=defender.healthPoints(),
			defenderDamage=defenderDamage,
			attackerHealth=attacker.healthPoints(),
			attackerDamage=0
		)

		# apply damage
		if defenderIsUnit:
			defender.changeDamage(defenderDamage, attackerPlayer, simulation)
		elif defenderIsCity:
			defender.changeDamage(defenderDamage)
		else:
			raise Exception(f'defender must be City or Unit but is {type(defender)}')

		if defender.healthPoints() <= 0:  # Defender died
			if activePlayer is not None and activePlayer == attacker.player:
				# simulation.userInterface.showTooltip(
				# 	at: defenderTile.point,
				# 	type:.unitDestroyedEnemyUnit(
				# 	attackerName: attacker.name,
				# 	attackerDamage: 0,
				# 	defenderName: defender.name()
				# ), delay: 3)
				pass

			if activePlayer is not None and activePlayer == defender.player:
				# simulation.userInterface.showTooltip(
				# 	at: defenderTile.point,
				# 	type:.unitDiedDefending(
				# 	attackerName: attacker.name,
				# 	attackerPlayer: attackerPlayer,
				# 	attackerDamage: 0,
				# 	defenderName: defender.name()
				# ), delay: 3)
				pass

			defenderPlayer.notifications.addNotification(NotificationType.unitDied, location=defender.location)

			if attacker.unitType == UnitType.slinger:
				if not attackerPlayer.techs.eurekaTriggeredFor(TechType.archery):
					attackerPlayer.techs.triggerEurekaFor(TechType.archery, simulation)

			if defenderIsUnit:
				defender.doKill(False, attackerPlayer, simulation)
			elif defenderIsCity:
				defender.preKill(simulation)

			defenderPlayer.updateWarWearinessAgainst(attackerPlayer, defender.location, killed=True, simulation=simulation)
			attackerPlayer.updateWarWearinessAgainst(defenderPlayer, defender.location, killed=False, simulation=simulation)
		else:
			defenderPlayer.updateWarWearinessAgainst(attackerPlayer, defender.location, killed=False, simulation=simulation)
			attackerPlayer.updateWarWearinessAgainst(defenderPlayer, defender.location, killed=False, simulation=simulation)

		return CombatResult(defenderDamage, 0, value)

	@classmethod
	def evaluateResult(cls,
					   defenderHealth: int,
					   defenderDamage: int,
					   attackerHealth: int,
					   attackerDamage: int) -> CombatResultType:

		if defenderDamage > defenderHealth and attackerHealth - attackerDamage > 10:
			return CombatResultType.totalVictory

		if attackerDamage > attackerHealth and defenderHealth - defenderDamage > 10:
			return CombatResultType.totalDefeat

		if defenderDamage > attackerDamage and defenderHealth - defenderDamage < attackerHealth - attackerDamage:
			return CombatResultType.majorVictory

		if defenderDamage < attackerDamage and defenderHealth - defenderDamage > attackerHealth - attackerDamage:
			return CombatResultType.majorDefeat

		if defenderDamage > attackerDamage:
			return CombatResultType.minorVictory

		if defenderDamage < attackerDamage:
			return CombatResultType.minorDefeat

		return CombatResultType.stalemate
