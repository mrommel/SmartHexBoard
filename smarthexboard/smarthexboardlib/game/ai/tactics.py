import logging
import random
import sys
from typing import Optional

from smarthexboard.smarthexboardlib.game.ai.army import ArmyFormationSlotConstants
from smarthexboard.smarthexboardlib.game.ai.baseTypes import PlayerStateAllWars
from smarthexboard.smarthexboardlib.game.ai.militaryTypes import TacticalDominanceType, TacticalTargetType, TacticalDominanceTerritoryType, \
	TacticalMoveType, TacticalPostureType, TemporaryZone, ArmyState, UnitFormationPosition, OperationStateType, \
	OperationStateReason, UnitFormationSlot
from smarthexboard.smarthexboardlib.game.civilizations import LeaderType
from smarthexboard.smarthexboardlib.game.combat import Combat, isinstance_string
from smarthexboard.smarthexboardlib.game.types import OperationHelpers
from smarthexboard.smarthexboardlib.game.unitMissions import UnitMission
from smarthexboard.smarthexboardlib.game.unitTypes import BitArray, UnitTaskType, UnitMapType, UnitMissionType, CivilianAttackPriorityType
from smarthexboard.smarthexboardlib.map import constants
from smarthexboard.smarthexboardlib.map.base import Array2D, Size, HexArea, HexPoint, HexDirection
from smarthexboard.smarthexboardlib.map.improvements import ImprovementType
from smarthexboard.smarthexboardlib.map.path_finding.finder import AStarPathfinder
from smarthexboard.smarthexboardlib.map.types import UnitDomainType, ResourceUsage, TerrainType, UnitMovementType
from smarthexboard.smarthexboardlib.utils.base import firstOrNone, secondOrNone, lastOrNone
from smarthexboard.smarthexboardlib.utils.plugin import Tests


class TacticalDominanceZone:
	pass


class TacticalAnalysisCell:
	def __init__(self):
		self._bits = BitArray(24)

		self._enemyMilitaryUnit = None
		self._enemyCivilianUnit = None
		self._neutralMilitaryUnit = None
		self._neutralCivilianUnit = None
		self._friendlyMilitaryUnit = None
		self._friendlyCivilianUnit = None

		self._defenseModifier = 0
		self._deploymentScore = 0
		self._targetType = TacticalTargetType.none

		self._dominanceZone: Optional[TacticalDominanceZone] = None

	def reset(self):
		self._bits.fill(False)

		self._enemyMilitaryUnit = None
		self._enemyCivilianUnit = None
		self._neutralMilitaryUnit = None
		self._neutralCivilianUnit = None
		self._friendlyMilitaryUnit = None
		self._friendlyCivilianUnit = None

		self._defenseModifier = 0
		self._deploymentScore = 0
		self._targetType = TacticalTargetType.none

		self._dominanceZone = None

	def setDeploymentScore(self, value: int):
		self._deploymentScore = value

	def deploymentScore(self) -> int:
		return self._deploymentScore

	def setDefenseModifier(self, value: int):
		self._defenseModifier = value

	def defenseModifier(self) -> int:
		return self._defenseModifier

	def setNeutralMilitaryUnit(self, unit):
		self._neutralMilitaryUnit = unit

	def neutralMilitaryUnit(self):
		return self._neutralMilitaryUnit

	def setNeutralCivilianUnit(self, unit):
		self._neutralCivilianUnit = unit

	def setFriendlyMilitaryUnit(self, unit):
		self._friendlyMilitaryUnit = unit

	def friendlyMilitaryUnit(self):
		return self._friendlyMilitaryUnit

	def setFriendlyCivilianUnit(self, unit):
		self._friendlyCivilianUnit = unit

	def setEnemyMilitaryUnit(self, unit):
		self._enemyMilitaryUnit = unit

	def enemyMilitaryUnit(self):
		return self._enemyMilitaryUnit

	def setEnemyCivilianUnit(self, unit):
		self._enemyCivilianUnit = unit

	def setRevealed(self, value: bool):
		"""Is this plot revealed to this player?"""
		self._bits[0] = value

	def isRevealed(self) -> bool:
		"""Is this plot revealed to this player?"""
		return self._bits[0] > 0

	def setVisible(self, value: bool):
		"""Is this plot visible to this player?"""
		self._bits[1] = value

	def isVisible(self) -> bool:
		"""Is this plot visible to this player?"""
		return self._bits[1] > 0

	def setImpassableTerrain(self, value: bool):
		"""Is this terrain impassable to this player?"""
		self._bits[2] = value

	def isImpassableTerrain(self) -> bool:
		"""Is this terrain impassable to this player?"""
		return self._bits[2] > 0

	def setImpassableTerritory(self, value: bool):
		"""Is this territory impassable to this player?"""
		self._bits[3] = value

	def isImpassableTerritory(self) -> bool:
		"""Is this neutral territory impassable to this player?"""
		return self._bits[3] > 0

	def setNotVisibleToEnemy(self, value: bool):
		"""A tile no enemy unit can see?"""
		self._bits[4] = value

	def isNotVisibleToEnemy(self) -> bool:
		"""A tile no enemy unit can see?"""
		return self._bits[4] > 0

	def setSubjectToAttack(self, value: bool):
		"""Enemy can strike at a unit here"""
		self._bits[5] = value

	def isSubjectToAttack(self) -> bool:
		"""Enemy can strike at a unit here"""
		return self._bits[5] > 0

	def setEnemyCanMovePast(self, value: bool):
		"""Enemy can move to this tile and still have movement left this turn"""
		self._bits[6] = value

	def isEnemyCanMovePast(self) -> bool:
		"""Enemy can move to this tile and still have movement left this turn"""
		return self._bits[6] > 0

	def setFriendlyTurnEndTile(self, value: bool):
		"""Is one of our friendly units ending its move here?"""
		self._bits[7] = value

	def isFriendlyTurnEndTile(self) -> bool:
		"""Is one of our friendly units ending its move here?"""
		return self._bits[7] > 0

	def setFriendlyCity(self, value: bool):
		"""Friendly city here?"""
		self._bits[8] = value

	def setEnemyCity(self, value: bool):
		"""Enemy city here?"""
		self._bits[9] = value

	def isEnemyCity(self) -> bool:
		"""Enemy city here?"""
		return self._bits[9] > 0

	def setNeutralCity(self, value: bool):
		"""Neutral city here?"""
		self._bits[10] = value

	def isNeutralCity(self) -> bool:
		"""Neutral city here?"""
		return self._bits[10] > 0

	def setWater(self, value: bool):
		"""Water?"""
		self._bits[11] = value

	def isWater(self) -> bool:
		"""Water?"""
		return self._bits[11] > 0

	def setOcean(self, value: bool):
		"""Ocean?"""
		self._bits[12] = value

	def isOcean(self) -> bool:
		"""Ocean?"""
		return self._bits[12] > 0

	def setOwnTerritory(self, value: bool):
		"""Territory owned by the active player"""
		self._bits[13] = value

	def setFriendlyTerritory(self, value: bool):
		"""Territory owned by allies"""
		self._bits[14] = value

	def setEnemyTerritory(self, value: bool):
		"""Territory owned by enemies"""
		self._bits[15] = value

	def setUnclaimedTerritory(self, value: bool):
		"""Territory that is unclaimed"""
		self._bits[16] = value

	def setWithinRangeOfTarget(self, value: bool):
		"""Is this a plot we can use to bombard the target?"""
		self._bits[17] = value

	def isWithinRangeOfTarget(self) -> bool:
		"""Is this a plot we can use to bombard the target?"""
		return self._bits[17] > 0

	def setCanUseToFlank(self, value: bool):
		"""Does this plot help provide a flanking bonus on target?"""
		self._bits[18] = value

	def isCanUseToFlank(self) -> bool:
		"""Does this plot help provide a flanking bonus on target?"""
		return self._bits[18] > 0

	def isHelpsProvidesFlankBonus(self) -> bool:
		"""Does this plot help provide a flanking bonus on target?"""
		return self._bits[18] > 0

	def setSafeDeployment(self, value: bool):
		"""Should be a safe spot to deploy ranged units"""
		self._bits[19] = value

	def isSafeDeployment(self) -> bool:
		"""Should be a safe spot to deploy ranged units"""
		return self._bits[19] > 0

	def canUseForOperationGathering(self) -> bool:
		if self.isImpassableTerrain() or \
			self.isImpassableTerritory() or \
			self._enemyMilitaryUnit is not None or \
			self._neutralMilitaryUnit is not None or \
			self._neutralCivilianUnit is not None or \
			self.isFriendlyTurnEndTile() or \
			self.isEnemyCity() or \
			self.isNeutralCity():

			return False

		return True

	def canUseForOperationGatheringCheckWater(self, isWater: bool) -> bool:
		if isWater != self.isWater() or \
			self.isImpassableTerrain() or \
			self.isImpassableTerritory() or \
			self._enemyMilitaryUnit is not None or \
			self._neutralMilitaryUnit is not None or \
			self._neutralCivilianUnit is not None or \
			self.isFriendlyTurnEndTile() or \
			self.isEnemyCity() or \
			self.isNeutralCity():
			return False

		return True

	def dominanceZone(self) -> Optional[TacticalDominanceZone]:
		return self._dominanceZone

	def setDominanceZone(self, dominanceZone: Optional[TacticalDominanceZone]):
		self._dominanceZone = dominanceZone


class TacticalDominanceZone:
	def __init__(self, territoryType: TacticalDominanceTerritoryType, dominanceFlag: TacticalDominanceType, owner,
				 area: Optional[HexArea], isWater: bool, closestCity, center, navalInvasion: bool, friendlyStrength: int,
				 friendlyRangedStrength: int, friendlyUnitCount: int, friendlyRangedUnitCount: int,
				 enemyStrength: int, enemyRangedStrength: int, enemyUnitCount: int, enemyRangedUnitCount: int,
				 enemyNavalUnitCount: int, rangeClosestEnemyUnit: int, dominanceValue: int):
		self.territoryType: TacticalDominanceTerritoryType = territoryType
		self.dominanceFlag = dominanceFlag
		self.owner = owner
		self.area = area
		self.isWater = isWater
		self.closestCity = closestCity
		self._center = center if isinstance_string(center, 'Tile') else None
		self.navalInvasion = navalInvasion
		self.friendlyStrength = friendlyStrength
		self.friendlyRangedStrength = friendlyRangedStrength
		self.friendlyUnitCount = friendlyUnitCount
		self.friendlyRangedUnitCount = friendlyRangedUnitCount
		self.enemyStrength = enemyStrength
		self.enemyRangedStrength = enemyRangedStrength
		self.enemyUnitCount = enemyUnitCount
		self.enemyRangedUnitCount = enemyRangedUnitCount
		self.enemyNavalUnitCount = enemyNavalUnitCount
		self.rangeClosestEnemyUnit = rangeClosestEnemyUnit
		self.dominanceValue = dominanceValue


	@property
	def center(self):
		return self._center

	def __repr__(self):
		return f'TacticalDominanceZone({self.territoryType}, {self.dominanceFlag}, owner={self.owner}, area={self.area})'

	def __eq__(self, other):
		if isinstance(other, TacticalDominanceZone):
			return self._center.point == other._center.point

		raise Exception(f'Cannot compare TacticalDominanceZone and {type(other)}')

	def __hash__(self):
		return hash(self._center.point)


class TacticalTarget:
	def __init__(self, targetType: TacticalTargetType = TacticalTargetType.none, target: HexPoint=HexPoint(-1, -1), targetLeader: LeaderType = LeaderType.none,
				 dominanceZone: Optional[TacticalDominanceZone] = None):
		self.targetType: TacticalTargetType = targetType
		self.target: HexPoint = target
		self.targetLeader: LeaderType = targetLeader
		self.dominanceZone: Optional[TacticalDominanceZone] = dominanceZone
		self.threatValue: int = 0
		self.unit = None
		self.damage: int = 0

	def __lt__(self, other):
		if isinstance(other, TacticalTarget):
			return self.damage < other.damage

		raise Exception(f'Can only compare TacticalTarget to itself but got {other}')

	def __eq__(self, other):
		if isinstance(other, TacticalTarget):
			return self.damage == other.damage

		raise Exception(f'Can only compare TacticalTarget to itself but got {other}')

	def isTargetValidIn(self, domain: UnitDomainType) -> bool:
		"""This target make sense for this domain of unit/zone?"""
		if self.targetType == TacticalTargetType.none:
			return False

		elif self.targetType == TacticalTargetType.city or \
			self.targetType == TacticalTargetType.cityToDefend or \
			self.targetType == TacticalTargetType.lowPriorityCivilian or \
			self.targetType == TacticalTargetType.mediumPriorityCivilian or \
			self.targetType == TacticalTargetType.highPriorityCivilian or \
			self.targetType == TacticalTargetType.veryHighPriorityCivilian or \
			self.targetType == TacticalTargetType.lowPriorityUnit or \
			self.targetType == TacticalTargetType.mediumPriorityUnit or \
			self.targetType == TacticalTargetType.highPriorityUnit:

			return True  # always valid

		elif self.targetType == TacticalTargetType.barbarianCamp or \
			self.targetType == TacticalTargetType.improvement or \
			self.targetType == TacticalTargetType.improvementToDefend or \
			self.targetType == TacticalTargetType.defensiveBastion or \
			self.targetType == TacticalTargetType.ancientRuins or \
			self.targetType == TacticalTargetType.tradeUnitLand or \
			self.targetType == TacticalTargetType.tradeUnitLandPlot or \
			self.targetType == TacticalTargetType.citadel or \
			self.targetType == TacticalTargetType.improvementResource:

			return domain == UnitDomainType.land  # land targets

		elif self.targetType == TacticalTargetType.blockadeResourcePoint or \
			self.targetType == TacticalTargetType.bombardmentZone or \
			self.targetType == TacticalTargetType.embarkedMilitaryUnit or \
			self.targetType == TacticalTargetType.embarkedCivilian or \
			self.targetType == TacticalTargetType.tradeUnitSea or \
			self.targetType == TacticalTargetType.tradeUnitSeaPlot:

			return domain == UnitDomainType.sea  # sea targets

		return False

	def isTargetStillAliveFor(self, attackingPlayer, simulation) -> bool:
		"""Still a living target?"""
		if self.targetType == TacticalTargetType.lowPriorityUnit or \
			self.targetType == TacticalTargetType.mediumPriorityUnit or \
			self.targetType == TacticalTargetType.highPriorityUnit:

			enemyDefender = simulation.visibleEnemyAt(self.target, attackingPlayer)

			if enemyDefender is not None:
				if not enemyDefender.isDelayedDeath():
					return True
		elif self.targetType == TacticalTargetType.city:
			enemyCity = simulation.visibleEnemyCityAt(self.target, attackingPlayer)

			if enemyCity is not None:
				if self.targetLeader == enemyCity.player.leader:
					return True

		return False


class TacticalAnalysisMap:
	dominancePercentage = 25  # AI_TACTICAL_MAP_DOMINANCE_PERCENTAGE
	tacticalRange = 10  # AI_TACTICAL_RECRUIT_RANGE
	tempZoneRadius = 5  # AI_TACTICAL_MAP_TEMP_ZONE_RADIUS

	def __init__(self, size: Size):
		self.unitStrengthMultiplier = 10 * self.tacticalRange  # AI_TACTICAL_MAP_UNIT_STRENGTH_MULTIPLIER

		self.plots = Array2D(size.width(), size.height())
		for x in range(0, size.width()):
			for y in range(0, size.height()):
				self.plots.values[y][x] = TacticalAnalysisCell()

		self.turnBuild = -1
		self.isBuild = False
		self.enemyUnits = []
		self.dominanceZones: [TacticalDominanceZone] = []
		self.ignoreLineOfSight = False

		self.playerBuild = None

		self._bestFriendlyRangeValue = 0

	# reserve capacity
	# self.dominanceZones.reserveCapacity(mapSize.width() * mapSize.height())

	def bestFriendlyRange(self) -> int:
		return self._bestFriendlyRangeValue

	def zoneAt(self, point: HexPoint) -> Optional[TacticalDominanceZone]:
		return self.plots.values[point.y][point.x].dominanceZone()

	def refreshFor(self, player, simulation):
		"""Fill the map with data for this AI player's turn"""
		# skip for barbarian player
		if player.isBarbarian():
			return

		if self.turnBuild < simulation.currentTurn or player.leader != self.playerBuild.leader:
			self.isBuild = False
			self.playerBuild = player
			self.turnBuild = simulation.currentTurn

			self.dominanceZones = []
			self.addTemporaryZones(simulation)

			for x in range(self.plots.width):
				for y in range(self.plots.height):
					tile = simulation.tileAt(HexPoint(x, y))

					if self.populateCellAt(x, y, tile, simulation):
						zone = self.dominanceZoneForCell(self.plots.values[y][x], tile, simulation)
						if zone is not None:
							# Set zone for this cell
							self.dominanceZones.append(zone)
							self.plots.values[y][x].setDominanceZone(zone)

					else:
						# Erase this cell
						self.plots.values[y][x].reset()

			self.calculateMilitaryStrengths(simulation)
			self.prioritizeZones(simulation)
			self.buildEnemyUnitList(simulation)
			self.markCellsNearEnemy(simulation)

			self.isBuild = True

		return

	def addTemporaryZones(self, simulation):
		"""Add in any temporary dominance zones from tactical AI"""
		tacticalAI = self.playerBuild.tacticalAI

		tacticalAI.dropObsoleteZones(simulation)

		# Can't be a city zone (which is just used to boost priority but not establish a new zone)
		for temporaryZone in tacticalAI.temporaryZones:
			if temporaryZone.targetType == TacticalTargetType.city:
				continue

			tile = simulation.tileAt(temporaryZone.location)

			if tile is not None:
				newZone = TacticalDominanceZone(
					territoryType=TacticalDominanceTerritoryType.tempZone,
					dominanceFlag=TacticalDominanceType.noUnitsPresent,
					owner=None,
					area=tile.area,
					isWater=tile.terrain().isWater(),
					closestCity=None,
					center=tile,
					navalInvasion=temporaryZone.navalMission,
					friendlyStrength=0,
					friendlyRangedStrength=0,
					friendlyUnitCount=0,
					friendlyRangedUnitCount=0,
					enemyStrength=0,
					enemyRangedStrength=0,
					enemyUnitCount=0,
					enemyRangedUnitCount=0,
					enemyNavalUnitCount=0,
					rangeClosestEnemyUnit=0,
					dominanceValue=0
				)

				self.dominanceZones.append(newZone)

		return

	def populateCellAt(self, x: int, y: int, tile, simulation) -> bool:
		"""Update data for a cell: returns whether to add to dominance zones"""
		player = self.playerBuild
		diplomacyAI = player.diplomacyAI

		cell: TacticalAnalysisCell = self.plots.values[y][x]

		if tile is not None:
			cell.reset()

			cell.setRevealed(tile.isDiscoveredBy(self.playerBuild))
			cell.setVisible(tile.isVisibleTo(self.playerBuild))
			impTerrain: bool = tile.isImpassable(UnitMovementType.walk) and tile.isImpassable(UnitMovementType.swim)
			cell.setImpassableTerrain(impTerrain)
			cell.setWater(tile.terrain().isWater())
			cell.setOcean(tile.terrain() == TerrainType.ocean)

			impassableTerritory = False
			if tile.hasOwner():
				city = simulation.cityAt(HexPoint(x, y))
				if tile.owner() != player and diplomacyAI.isAtWarWith(tile.owner()) and \
					not diplomacyAI.isOpenBordersAgreementActiveWith(tile.owner()):
					impassableTerritory = True

				elif city is not None:
					if city.player == player:
						cell.setFriendlyCity(True)
					elif diplomacyAI.isAtWarWith(city.player) or player.isBarbarian():
						cell.setEnemyCity(True)
					else:
						cell.setNeutralCity(True)

				if not tile.owner() == player:
					cell.setOwnTerritory(True)

				if tile.isFriendlyTerritoryFor(player, simulation):
					cell.setFriendlyTerritory(True)

				if diplomacyAI.isAtWarWith(tile.owner()):
					cell.setEnemyTerritory(True)

				if player.isBarbarian():
					cell.setEnemyTerritory(True)

			else:
				cell.setUnclaimedTerritory(True)

			cell.setImpassableTerritory(impassableTerritory)
			cell.setDefenseModifier(tile.defenseModifierFor(player))

			unit = simulation.unitAt(HexPoint(x, y), UnitMapType.combat)
			if unit is not None:
				if unit.player == player:
					if unit.isCombatUnit():
						cell.setFriendlyMilitaryUnit(unit)
					else:
						cell.setFriendlyCivilianUnit(unit)
				elif diplomacyAI.isAtWarWith(unit.player) or player.isBarbarian():
					if unit.isCombatUnit():
						cell.setEnemyMilitaryUnit(unit)
					else:
						cell.setEnemyCivilianUnit(unit)
				else:
					if unit.isCombatUnit():
						cell.setNeutralMilitaryUnit(unit)
					else:
						cell.setNeutralCivilianUnit(unit)

			# Figure out whether to add this to a dominance zone
			if cell.isImpassableTerrain() or cell.isImpassableTerritory() or (
				not cell.isRevealed() and not player.isBarbarian()):
				return False

		return True

	def calculateMilitaryStrengths(self, simulation):
		"""Calculate military presences in each owned dominance zone"""
		player = self.playerBuild

		# Loop through the dominance zones
		for dominanceZone in self.dominanceZones:
			if dominanceZone.territoryType == TacticalDominanceTerritoryType.noOwner:
				continue

			closestCity = dominanceZone.closestCity
			if closestCity is not None:
				# Start with strength of the city itself
				strength = closestCity.rangedCombatStrengthAgainst(None, None) * self.tacticalRange

				if dominanceZone.territoryType == TacticalDominanceTerritoryType.friendly:
					dominanceZone.friendlyStrength += strength
					dominanceZone.friendlyRangedStrength += closestCity.rangedCombatStrengthAgainst(None, None)
				else:
					dominanceZone.enemyStrength += strength
					dominanceZone.enemyRangedStrength += closestCity.rangedCombatStrengthAgainst(None, None)

				# Loop through all of OUR units first
				for unit in simulation.unitsOf(player):
					if unit.isCombatUnit():
						if unit.domain() == UnitDomainType.air or \
							unit.domain() == UnitDomainType.land and not dominanceZone.isWater or \
							unit.domain() == UnitDomainType.sea and dominanceZone.isWater:

							distance = closestCity.location.distance(unit.location)
							multiplier = self.tacticalRange + 1 - distance

							if multiplier > 0:
								unitStrength = unit.attackStrengthAgainst(None, None, None, simulation)

								if unitStrength == 0 and unit.isEmbarked() and not dominanceZone.isWater:
									unitStrength = unit.baseCombatStrength(ignoreEmbarked=True)

								dominanceZone.friendlyStrength += unitStrength * multiplier * self.unitStrengthMultiplier
								dominanceZone.friendlyRangedStrength += unit.rangedCombatStrengthAgainst(None, None, None,
																								  attacking=True,
																								  simulation=simulation)

								if unit.range() > self._bestFriendlyRangeValue:
									self._bestFriendlyRangeValue = unit.range()

								dominanceZone.friendlyUnitCount += 1

				# Repeat for all visible enemy units ( or adjacent to visible)
				for otherPlayer in simulation.players:
					if player.isAtWarWith(otherPlayer):
						for loopUnit in simulation.unitsOf(otherPlayer):
							if loopUnit.isCombatUnit():

								if loopUnit.domain() == UnitDomainType.air or \
									(loopUnit.domain() == UnitDomainType.land and not dominanceZone.isWater) or \
									(loopUnit.domain() == UnitDomainType.sea and dominanceZone.isWater):

									plot = simulation.tileAt(loopUnit.location)

									if plot is not None:
										visible = True
										distance = loopUnit.location.distance(closestCity.location)

										if distance <= self.tacticalRange:
											# "4" so unit strength isn't totally dominated by proximity to city
											multiplier = (self.tacticalRange + 4 - distance)
											if not plot.isVisibleTo(player) and \
												not simulation.isAdjacentDiscovered(loopUnit.location, player):
												visible = False

											if multiplier > 0:
												unitStrength = loopUnit.attackStrengthAgainst(None, None, None, simulation)
												if unitStrength == 0 and loopUnit.isEmbarked() and not dominanceZone.isWater:
													unitStrength = loopUnit.baseCombatStrength(ignoreEmbarked=True)

												if not visible:
													unitStrength /= 2

												dominanceZone.enemyStrength += unitStrength * multiplier * self.unitStrengthMultiplier

												rangedStrength = loopUnit.rangedCombatStrengthAgainst(None, None, None,
																							   attacking=True,
																							   simulation=simulation)
												if not visible:
													rangedStrength /= 2

												dominanceZone.enemyRangedStrength = rangedStrength

												if visible:
													dominanceZone.enemyUnitCount += 1
													if distance < dominanceZone.rangeClosestEnemyUnit:
														dominanceZone.rangeClosestEnemyUnit = distance

													if loopUnit.isRanged():
														dominanceZone.enemyRangedUnitCount += 1

													if loopUnit.domain() == UnitDomainType.sea:
														dominanceZone.enemyNavalUnitCount += 1

		return

	def prioritizeZones(self, simulation):
		"""Establish order of zone processing for the turn"""
		player = self.playerBuild
		diplomacyAI = player.diplomacyAI

		# Loop through the dominance zones
		for dominanceZone in self.dominanceZones:
			# Find the zone and compute dominance here
			dominance = self.calculateDominanceOf(dominanceZone, simulation)
			dominanceZone.dominanceFlag = dominance

			# Establish a base value for the region
			baseValue = 1
			multiplier = 1

			# Temporary zone?
			if dominanceZone.territoryType == TacticalDominanceTerritoryType.tempZone:
				multiplier = 200
			else:
				closestCity = dominanceZone.closestCity

				if closestCity is not None:
					baseValue += closestCity.population()

					if closestCity.isCapital():
						baseValue *= 2

					# How damaged is this city?
					damage = closestCity.damage()
					if damage > 0:
						baseValue *= (damage + 2) / 2

					if player.tacticalAI.isTemporaryZone(closestCity):
						baseValue *= 3

				if not dominanceZone.isWater:
					baseValue *= 8

				# Now compute a multiplier based on current conditions here
				if dominance == TacticalDominanceType.noUnitsPresent or dominance == TacticalDominanceType.notVisible:
					pass  # NOOP
				elif dominance == TacticalDominanceType.friendly:
					if dominanceZone.territoryType == TacticalDominanceTerritoryType.enemy:
						multiplier = 4
					elif dominanceZone.territoryType == TacticalDominanceTerritoryType.friendly:
						multiplier = 1
				elif dominance == TacticalDominanceType.even:
					if dominanceZone.territoryType == TacticalDominanceTerritoryType.enemy:
						multiplier = 3
					elif dominanceZone.territoryType == TacticalDominanceTerritoryType.friendly:
						multiplier = 3
				elif dominance == TacticalDominanceType.enemy:
					if dominanceZone.territoryType == TacticalDominanceTerritoryType.enemy:
						multiplier = 2
					elif dominanceZone.territoryType == TacticalDominanceTerritoryType.friendly:
						multiplier = 4

				if diplomacyAI.stateOfAllWars == PlayerStateAllWars.winning:
					if dominanceZone.territoryType == TacticalDominanceTerritoryType.enemy:
						multiplier *= 2
				elif diplomacyAI.stateOfAllWars == PlayerStateAllWars.losing:
					if dominanceZone.territoryType == TacticalDominanceTerritoryType.friendly:
						multiplier *= 2

			if baseValue * multiplier <= 0:
				raise Exception("Invalid Dominance Zone Value")

			dominanceZone.dominanceValue = baseValue * multiplier

		self.dominanceZones.sort(key=lambda zone: zone.dominanceValue, reverse=True)

	def buildEnemyUnitList(self, simulation):
		"""Find all our enemies (combat units)"""
		player = self.playerBuild
		diplomacyAI = player.diplomacyAI

		self.enemyUnits = []

		for otherPlayer in simulation.players:
			# for each opposing civ
			if player.isAlive() and diplomacyAI.isAtWarWith(otherPlayer):
				for unit in simulation.unitsOf(otherPlayer):
					if unit.canAttack():
						self.enemyUnits.append(unit)

		return

	def markCellsNearEnemy(self, simulation):
		"""Indicate the plots we might want to move to that the enemy can attack"""
		player = self.playerBuild
		diplomacyAI = player.diplomacyAI

		# Look at every cell on the map
		for x in range(self.plots.width):
			for y in range(self.plots.height):
				marked = False
				pt = HexPoint(x, y)
				cell: TacticalAnalysisCell = self.plots.values[y][x]
				tile = simulation.tileAt(pt)

				if tile is not None:
					if tile.isDiscoveredBy(self.playerBuild) and not tile.isImpassable(UnitMovementType.walk):
						if not tile.isVisibleToEnemy(player, simulation):
							cell.setNotVisibleToEnemy(True)
						else:
							# loop all enemy units
							for enemyUnit in self.enemyUnits:
								if marked:
									break

								pathFinderDataSource = simulation.ignoreUnitsPathfinderDataSource(
									enemyUnit.movementType(),
									enemyUnit.player,
									canEmbark=enemyUnit.player.canEmbark(),
									canEnterOcean=enemyUnit.player.canEnterOcean()
								)

								pathFinder = AStarPathfinder(pathFinderDataSource)
								unitArea = simulation.areaOf(enemyUnit.location)
								if tile.area() == unitArea:
									# Distance check before hitting pathfinder
									distance = enemyUnit.location.distance(tile.point)
									if distance == 0:
										cell.setSubjectToAttack(True)
										cell.setEnemyCanMovePast(True)
										marked = True

									# TEMPORARY OPTIMIZATION: Assumes can't use roads or RR
									elif distance <= enemyUnit.baseMoves(UnitDomainType.none, simulation):
										path = pathFinder.shortestPath(enemyUnit.location, tile.point)

										if path is not None:
											turnsToReach = len(path.points()) / enemyUnit.moves()

											if turnsToReach <= 1:
												cell.setSubjectToAttack(True)

											if turnsToReach == 0:
												cell.enemyCanMovePast = True
												marked = True

							# Check adjacent plots for enemy citadels
							if not cell.isSubjectToAttack():
								for direction in list(HexDirection):
									adjacent = tile.point.neighbor(direction)
									adjacentTile = simulation.tileAt(adjacent)

									if adjacentTile is not None:
										if adjacentTile.hasOwner():
											if diplomacyAI.isAtWarWith(adjacentTile.owner()):
												if adjacentTile.hasImprovement(ImprovementType.citadelle):
													cell.setSubjectToAttack(True)
													break

		return

	def isInEnemyDominatedZone(self, point: HexPoint) -> bool:
		"""Is this plot in dangerous territory?"""
		cell: TacticalAnalysisCell = self.plots.values[point.y][point.x]

		if cell.dominanceZone() is None:
			return False

		for dominanceZone in self.dominanceZones:
			if cell.dominanceZone() == dominanceZone:
				return dominanceZone.dominanceFlag == TacticalDominanceType.enemy or \
					dominanceZone.dominanceFlag == TacticalDominanceType.notVisible

		return False

	def clearDynamicFlags(self):
		"""Clear all dynamic data flags from the map"""
		for x in range(0, self.plots.width):
			for y in range(0, self.plots.height):
				self.plots.values[y][x].setWithinRangeOfTarget(False)
				self.plots.values[y][x].setCanUseToFlank(False)
				self.plots.values[y][x].setSafeDeployment(False)
				self.plots.values[y][x].setDeploymentScore(0)

	def setTargetBombardCells(self, target: HexPoint, bestFriendlyRange: int, ignoreLineOfSight: bool, simulation):
		targetPlot = simulation.tileAt(target)

		for dx in range(-bestFriendlyRange, bestFriendlyRange):
			for dy in range(-bestFriendlyRange, bestFriendlyRange):
				loopPoint = HexPoint(target.x + dx, target.y + dy)
				loopPlot = simulation.tileAt(loopPoint)

				if loopPlot is None:
					continue

				distance = loopPoint.distance(target)

				if 0 < distance <= bestFriendlyRange:
					cell: TacticalAnalysisCell = self.plots.values[loopPoint.y][loopPoint.x]

					if cell.isRevealed() and not cell.isImpassableTerrain() and not cell.isImpassableTerritory():
						if not cell.isEnemyCity() and not cell.isNeutralCity():
							canBeSeen = loopPlot.canSeeTile(targetPlot, self.playerBuild, bestFriendlyRange, hasSentry=False, simulation=simulation)

							if ignoreLineOfSight or canBeSeen:
								cell.setWithinRangeOfTarget(True)

		return

	def calculateDominanceOf(self, dominanceZone: TacticalDominanceZone, simulation) -> TacticalDominanceType:
		player = self.playerBuild
		diplomacyAI = player.diplomacyAI
		tacticalAI = player.tacticalAI

		tempZone: bool = False
		tile = None

		closestCity = dominanceZone.closestCity
		if closestCity is not None:
			tempZone = tacticalAI.isTemporaryZone(closestCity)
			tile = simulation.tileAt(closestCity.location)

		tileIsVisible: bool = tile.isVisibleTo(player) if tile is not None else True

		# Look at ratio of friendly to enemy strength
		if dominanceZone.friendlyStrength + dominanceZone.enemyStrength <= 0:
			dominanceValue = TacticalDominanceType.noUnitsPresent
		elif dominanceZone.territoryType == TacticalDominanceTerritoryType.enemy and not tileIsVisible and not tempZone:
			# Enemy zone that we can't see (that isn't one of our temporary targets?
			dominanceValue = TacticalDominanceType.notVisible
		else:
			enemyCanSeeOurCity: bool = False
			if dominanceZone.territoryType == TacticalDominanceTerritoryType.friendly:
				for otherPlayer in simulation.players:
					if otherPlayer.isAlive() and player != otherPlayer:
						if diplomacyAI.isAtWarWith(otherPlayer):
							tileIsVisible: bool = tile.isVisibleTo(player) if tile is not None else False
							if tileIsVisible:
								enemyCanSeeOurCity = True
								break

			if dominanceZone.territoryType == TacticalDominanceTerritoryType.friendly and not enemyCanSeeOurCity:
				dominanceValue = TacticalDominanceType.notVisible
			elif dominanceZone.enemyStrength <= 0:
				# Otherwise compute it by strength
				dominanceValue = TacticalDominanceType.friendly
			else:
				ratio = dominanceZone.friendlyStrength * 100 / dominanceZone.enemyStrength

				if ratio > 100 + self.dominancePercentage:
					dominanceValue = TacticalDominanceType.friendly
				elif ratio < 100 - self.dominancePercentage:
					dominanceValue = TacticalDominanceType.enemy
				else:
					dominanceValue = TacticalDominanceType.even

		return dominanceValue

	def dominanceZoneForCell(self, cell: TacticalAnalysisCell, tile, simulation) -> Optional[TacticalDominanceZone]:
		"""Add data for this cell into dominance zone information"""
		player = self.playerBuild
		diplomacyAI = player.diplomacyAI

		# Compute zone data for this cell
		territoryType: TacticalDominanceTerritoryType = TacticalDominanceTerritoryType.tempZone

		owner = tile.owner()
		if owner is None:
			territoryType = TacticalDominanceTerritoryType.noOwner
		elif owner == player:
			territoryType = TacticalDominanceTerritoryType.friendly
		elif diplomacyAI.isAtWarWith(owner):
			territoryType = TacticalDominanceTerritoryType.enemy
		else:
			territoryType = TacticalDominanceTerritoryType.neutral

		bestCity = None
		bestDistance = sys.maxsize

		if territoryType == TacticalDominanceTerritoryType.enemy or \
			territoryType == TacticalDominanceTerritoryType.neutral or \
			territoryType == TacticalDominanceTerritoryType.friendly:

			if owner is not None:
				for city in simulation.citiesOf(owner):
					distance = city.location.distance(tile.point)

					if distance < bestDistance:
						bestDistance = distance
						bestCity = city

		tempZoneRef: Optional[TacticalDominanceZone] = None

		# Now see if we already have a matching zone
		zone = self.findExistingZoneAt(tile.point, territoryType, owner, bestCity, tile.area())
		if zone is not None:
			tempZoneRef = zone
		else:
			tempZoneRef = TacticalDominanceZone(
				territoryType=territoryType,
				dominanceFlag=TacticalDominanceType.noUnitsPresent,
				owner=owner,
				area=tile.area(),
				isWater=tile.terrain().isWater(),
				closestCity=bestCity,
				center=tile,
				navalInvasion=False,
				friendlyStrength=0,
				friendlyRangedStrength=0,
				friendlyUnitCount=0,
				friendlyRangedUnitCount=0,
				enemyStrength=0,
				enemyRangedStrength=0,
				enemyUnitCount=0,
				enemyRangedUnitCount=0,
				enemyNavalUnitCount=0,
				rangeClosestEnemyUnit=0,
				dominanceValue=0
			)

		# If this isn't owned territory, update zone with military strength info
		if tempZoneRef.territoryType == TacticalDominanceTerritoryType.noOwner or \
			tempZoneRef.territoryType == TacticalDominanceTerritoryType.tempZone:
			if tempZoneRef is not None:
				friendlyUnit = cell.friendlyMilitaryUnit()
				if friendlyUnit is not None:
					if friendlyUnit.domain() == UnitDomainType.air or \
						(friendlyUnit.domain() == UnitDomainType.land and not tempZoneRef.isWater) or \
						(friendlyUnit.domain() == UnitDomainType.sea and tempZoneRef.isWater):

						strength = friendlyUnit.attackStrengthAgainst(None, None, None, simulation)
						if strength == 0 and friendlyUnit.isEmbarked() and not tempZoneRef.isWater:
							strength = friendlyUnit.baseCombatStrength(ignoreEmbarked=True)

						tempZoneRef.friendlyStrength += strength * self.unitStrengthMultiplier
						tempZoneRef.friendlyRangedStrength += friendlyUnit.rangedCombatStrengthAgainst(None, None, None, attacking=True, simulation=simulation)

						if friendlyUnit.range() > self._bestFriendlyRangeValue:
							self.bestFriendlyRangeValue = friendlyUnit.range()

						tempZoneRef.friendlyUnitCount += 1

						if friendlyUnit.range() > 0:
							tempZoneRef.friendlyRangedUnitCount += 1

				enemyUnit = cell.enemyMilitaryUnit()
				if enemyUnit is not None:
					if enemyUnit.domain() == UnitDomainType.air or \
						(enemyUnit.domain() == UnitDomainType.land and not tempZoneRef.isWater) or \
						(enemyUnit.domain() == UnitDomainType.sea and tempZoneRef.isWater):

						strength = enemyUnit.attackStrengthAgainst(None, None, None, simulation)
						if strength == 0 and enemyUnit.isEmbarked() and not tempZoneRef.isWater:
							strength = enemyUnit.baseCombatStrength(ignoreEmbarked=True)

						tempZoneRef.enemyStrength += strength * self.unitStrengthMultiplier
						tempZoneRef.enemyRangedStrength += enemyUnit.rangedCombatStrengthAgainst(None, None, None, attacking=True, simulation=simulation)
						tempZoneRef.enemyUnitCount += 1

						if enemyUnit.range() > 0:
							tempZoneRef.enemyRangedUnitCount += 1

						if enemyUnit.domain() == UnitDomainType.sea:
							tempZoneRef.enemyNavalUnitCount += 1

		# Set zone for this cell
		cell.setDominanceZone(tempZoneRef)

		return tempZoneRef

	def findExistingZoneAt(self, point: HexPoint, territoryType: TacticalDominanceTerritoryType, owner, city, area: Optional[HexArea]) -> Optional[TacticalDominanceZone]:
		max: int = len(self.dominanceZones)
		index: int = 0

		while index < max:
			dominanceZone = self.dominanceZones[index]

			# If this is a temporary zone, matches if unowned and close enough
			if dominanceZone.territoryType == TacticalDominanceTerritoryType.tempZone and \
				(territoryType == TacticalDominanceTerritoryType.noOwner or territoryType == TacticalDominanceTerritoryType.neutral) and \
				point.distance(dominanceZone.center.point) <= self.tempZoneRadius:

				return dominanceZone

			# If not friendly or enemy, just 1 zone per area
			if (dominanceZone.territoryType == TacticalDominanceTerritoryType.noOwner or dominanceZone.territoryType == TacticalDominanceTerritoryType.neutral) and \
				(territoryType == TacticalDominanceTerritoryType.noOwner or territoryType == TacticalDominanceTerritoryType.neutral) and \
				dominanceZone.area is not None and area is not None and dominanceZone.area == area:

				return dominanceZone

			# Otherwise everything needs to match
			if dominanceZone.territoryType == territoryType and \
				dominanceZone.owner == owner and \
				dominanceZone.area is not None and area is not None and dominanceZone.area == area and \
				dominanceZone.closestCity == city:

				return dominanceZone

			index += 1

		return None


class QueuedAttack:
	"""
	// ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	//  CLASS:      CvQueuedAttack
	// !  \brief        A planned attack waiting to execute
	//
	// !  Key Attributes:
	// !  - Arises during processing of CvTacticalAI::ExecuteAttacks() or ProcessUnit()
	// !  - Created by calling QueueFirstAttack() or QueueSubsequentAttack()
	// !  - Combat animation system calls back into tactical AI when animation completes with call CombatResolved()
	// !  - This callback signals it is time to execute the next attack
	// ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	"""
	def __init__(self):
		self.attackerUnit = None
		self.attackerCity = None
		self.target: Optional[TacticalTarget] = None
		self.ranged: bool = False
		self.cityAttack: bool = False
		self.seriesId: int = -1


class TacticalMove:
	def __init__(self):
		self.moveType: TacticalMoveType = TacticalMoveType.unassigned
		self.priority: int = TacticalMoveType.unassigned.priority()

	def __eq__(self, other):
		if isinstance(other, TacticalMove):
			return self.priority == other.priority and self.moveType == other.moveType

		return False

	def __lt__(self, other):
		# this will sort the highest priority to the beginning
		if isinstance(other, TacticalMove):
			return self.priority > other.priority

		return False

	def __repr__(self):
		return f'TacticalMove({self.moveType}, {self.priority})'


class TacticalPosture:
	"""The posture an AI has adopted for fighting in a specific dominance zone"""
	def __init__(self, postureType: TacticalPostureType, player, city, isWater: bool):
		self.postureType: TacticalPostureType = postureType
		self.player = player
		self.city = city
		self.isWater: bool = isWater


class TacticalCity:
	"""Object stored in the list of current move cities (currentMoveCities)"""

	def __init__(self, attackStrength: int = 0, expectedTargetDamage: int = 0, city=None):
		self.attackStrength = attackStrength
		self.expectedTargetDamage = expectedTargetDamage
		self.city = city

	def __lt__(self, other):
		if isinstance(other, TacticalCity):
			return self.attackStrength > other.attackStrength

		return False

	def __eq__(self, other):
		if isinstance(other, TacticalCity):
			return False

		return False


class TacticalUnit:
	def __init__(self, unit, attackStrength: int = 0, healthPercent: int = 0):
		self.attackStrength = attackStrength
		self.healthPercent = healthPercent
		self.movesToTarget = 0
		self.expectedTargetDamage = 0
		self.expectedSelfDamage = 0
		self.unit = unit

	def attackPriority(self) -> int:
		return self.attackStrength * self.healthPercent

	def __lt__(self, other):
		if isinstance(other, TacticalUnit):
			return self.attackStrength > other.attackStrength

		return False

	def __eq__(self, other):
		if isinstance(other, TacticalUnit):
			return False

		return False


class BlockingUnit:
	def __init__(self, unit, point: HexPoint, numberOfChoices: int = 0, distanceToTarget: int = 0):
		self.unit = unit
		self.point = point
		self.numberOfChoices = numberOfChoices
		self.distanceToTarget = distanceToTarget


class OperationUnit:
	def __init__(self, unit, position: UnitFormationPosition = UnitFormationPosition.none):
		self.unit = unit
		self.position = position


class TacticalAI:
	recruitRange = 10  # AI_TACTICAL_RECRUIT_RANGE
	repositionRange = 10  # AI_TACTICAL_REPOSITION_RANGE
	deployRadius = 4  # AI_OPERATIONAL_CITY_ATTACK_DEPLOY_RANGE

	def __init__(self, player):
		self.player = player

		self.temporaryZones: [TemporaryZone] = []
		self.allTargets: [TacticalTarget] = []

		self.queuedAttacks: [QueuedAttack] = []
		self.movePriorityList: [TacticalMove] = []
		self.postures: [TacticalPosture] = []
		self.zoneTargets: [TacticalTarget] = []
		self.tempTargets: [TacticalTarget] = []

		self.currentTurnUnits = []
		self.currentMoveCities: [TacticalCity] = []
		self.currentMoveUnits: [TacticalUnit] = []
		self.currentMoveHighPriorityUnits: [TacticalUnit] = []
		self.currentZoneIndex: Optional[HexPoint] = None

		# Blocking (and flanking) position data
		self.potentialBlocks: [BlockingUnit] = []
		self.temporaryBlocks: [BlockingUnit] = []
		self.chosenBlocks: [BlockingUnit] = []
		self.newlyChosen: [BlockingUnit] = []

		# Operational AI support data
		self.operationUnits: [OperationUnit] = []
		self.generalsToMove: [OperationUnit] = []
		self.paratroopersToMove: [OperationUnit] = []

		self.movePriorityTurn: int = 0
		self.currentSeriesId: int = -1

	def doTurn(self, simulation):
		"""Update the AI for units"""
		# DropOldFocusAreas();
		self.findTacticalTargets(simulation)

		# do this after updating the target list!
		self.recruitUnits(simulation)

		# Loop through each dominance zone assigning moves
		self.processDominanceZones(simulation)

	def dropObsoleteZones(self, simulation):
		"""Remove temporary zones that have expired"""
		self.temporaryZones = list(filter(lambda zone: zone.lastTurn >= simulation.currentTurn, self.temporaryZones))
		return

	def recruitUnits(self, simulation):
		"""Mark all the units that will be under tactical AI control this turn"""
		dangerPlotsAI = self.player.dangerPlotsAI
		self.currentTurnUnits = []

		for unit in simulation.unitsOf(self.player):
			# Never want immobile / dead units, explorers, ones that have already moved
			if unit.task() == UnitTaskType.explore or not unit.canMove():
				continue

			elif self.player.isBarbarian():
				# We want ALL the barbarians that are not guarding a camp
				unit.setTacticalMove(TacticalMoveType.unassigned)
				self.currentTurnUnits.append(unit)

			elif unit.domain() == UnitDomainType.air:
				# and air units
				unit.setTacticalMove(TacticalMoveType.unassigned)
				self.currentTurnUnits.append(unit)

			elif not unit.isCombatUnit() and not unit.isGreatPerson():
				# Now down to land and sea units... in these groups our unit must have a base combat strength...
				# or be a great general
				continue

			else:
				# Is this one in an operation we can't interrupt?
				if unit.army() is not None:
					if unit.army().canTacticalAIInterrupt():
						unit.setTacticalMove(TacticalMoveType.none)
				else:
					# Non-zero danger value, near enemy, or deploying out of an operation?
					danger = dangerPlotsAI.dangerAt(unit.location)
					if danger > 0 or self.isNearVisibleEnemy(unit, 10, simulation):
						unit.setTacticalMove(TacticalMoveType.unassigned)
						self.currentTurnUnits.append(unit)
		return

	def isNearVisibleEnemy(self, unitToTest, distance: int, simulation) -> bool:
		"""Am I within range of an enemy?"""
		diplomacyAI = self.player.diplomacyAI

		# Loop through enemies
		for otherPlayer in simulation.players:
			if otherPlayer.isAlive() and otherPlayer.leader != self.player.leader and diplomacyAI.isAtWarWith(
				otherPlayer):
				# Loop through their units
				for unit in simulation.unitsOf(otherPlayer):
					# Make sure this tile is visible to us
					tile = simulation.tileAt(unit.location)

					if tile is not None:
						if tile.isVisibleTo(self.player) and unitToTest.location.distance(unit.location) < distance:
							return True

				# Loop through their cities
				for city in simulation.citiesOf(otherPlayer):
					# Make sure this tile is visible to us
					tile = simulation.tileAt(city.location)
					if tile.isVisibleTo(self.player) and unitToTest.location.distance(city.location) < distance:
						return True

		return False

	def findTacticalTargets(self, simulation):
		"""Make lists of everything we might want to target with the tactical AI this turn"""
		diplomacyAI = self.player.diplomacyAI
		dangerPlotsAI = self.player.dangerPlotsAI

		# Clear out target list since we rebuild it each turn
		self.allTargets = []

		barbsAllowedYet = simulation.currentTurn >= 20
		mapSize = simulation.mapSize().size()

		# Look at every tile on map
		for x in range(mapSize.width()):
			for y in range(mapSize.height()):
				point = HexPoint(x, y)
				validPlot = False
				tile = simulation.tileAt(point)

				if tile.isVisibleTo(self.player):
					# Make sure player is not a barbarian who can not move into owned territory this early in the game
					if self.player.isBarbarian():
						if barbsAllowedYet or not tile.hasOwner():
							validPlot = True
					else:
						validPlot = True

				if validPlot:
					if self.isAlreadyTargeted(point) is not None:
						validPlot = False

				if validPlot:
					dominanceZone = simulation.tacticalAnalysisMap().plots.values[point.y][point.x].dominanceZone()
					newTarget = TacticalTarget(
						targetType=TacticalTargetType.none,
						target=point,
						targetLeader=LeaderType.none,
						dominanceZone=dominanceZone
					)

					enemyDominatedPlot = simulation.tacticalAnalysisMap().isInEnemyDominatedZone(point)

					# Have a...
					city = simulation.cityAt(tile.point)

					if city is not None:
						if self.player == city.player:
							# ...friendly city?
							newTarget.targetType = TacticalTargetType.cityToDefend
							newTarget.city = city
							newTarget.threatValue = city.threatValue()
							self.allTargets.append(newTarget)
						elif diplomacyAI.isAtWarWith(city.player):
							# ... enemy city
							newTarget.targetType = TacticalTargetType.city
							newTarget.city = city
							newTarget.threatValue = city.threatValue()
							self.allTargets.append(newTarget)
					else:
						unit = simulation.unitAt(tile.point, UnitMapType.combat)
						if unit is not None:
							if diplomacyAI.isAtWarWith(unit.player):
								# ... enemy unit?
								newTarget.targetType = TacticalTargetType.lowPriorityUnit
								newTarget.targetLeader = unit.player.leader
								newTarget.unit = unit
								newTarget.damage = unit.damage()
								self.allTargets.append(newTarget)
								continue
						else:
							unit = simulation.unitAt(tile.point, UnitMapType.civilian)

						if tile.hasImprovement(ImprovementType.barbarianCamp):
							# ... undefended camp?
							newTarget.targetType = TacticalTargetType.barbarianCamp
							newTarget.targetLeader = LeaderType.barbar
							newTarget.tile = tile
							self.allTargets.append(newTarget)

						elif tile.hasImprovement(ImprovementType.goodyHut):
							# ... goody hut?
							newTarget.targetType = TacticalTargetType.ancientRuins
							newTarget.tile = tile
							self.allTargets.append(newTarget)

						# ... enemy resource improvement?
						elif tile.hasOwner() and diplomacyAI.isAtWarWith(tile.owner()) and \
							tile.canBePillaged() and not tile.hasAnyResourceFor(self.player):

							# On land, civilizations only target improvements built on resources
							if tile.hasResource(ResourceUsage.strategic, self.player) or \
								tile.hasResource(ResourceUsage.luxury, self.player) or tile.terrain().isWater() or \
								self.player.isBarbarian():

								if tile.terrain().isWater() and self.player.isBarbarian():
									continue
								else:
									newTarget.targetType = TacticalTargetType.improvementResource
									newTarget.targetLeader = tile.owner().leader
									newTarget.tile = tile
									self.allTargets.append(newTarget)

						# Or forts / citadels!
						elif tile.owner() is not None and diplomacyAI.isAtWarWith(tile.owner()) and \
							(tile.hasImprovement(ImprovementType.fort) or tile.hasImprovement(ImprovementType.citadelle)):
							newTarget.targetType = TacticalTargetType.improvement
							newTarget.targetLeader = tile.owner().leader
							newTarget.tile = tile
							self.allTargets.append(newTarget)

						# ... enemy trade route?
						# elif if tile.owner() is not None and diplomacyAI.isAtWarWith(tile.owner()) and \
						#	tile.route
						# else if (atWar (m_pPlayer->getTeam(), pLoopPlot->getTeam()) &&
						# 					pLoopPlot->getRouteType() != NO_ROUTE && !pLoopPlot->IsRoutePillaged() && pLoopPlot->IsTradeRoute() && !bEnemyDominatedPlot)
						# 				{
						# 					newTarget.SetTargetType(AI_TACTICAL_TARGET_IMPROVEMENT);
						# 					newTarget.SetTargetPlayer(pLoopPlot->getOwner());
						# 					newTarget.SetAuxData((void *)pLoopPlot);
						# 					m_AllTargets.push_back(newTarget);
						# 				}

						# ... enemy civilian (or embarked) unit?
						elif unit is not None and unit.player.leader != self.player.leader:
							if diplomacyAI.isAtWarWith(unit.player) and not unit.canDefend():
								newTarget.targetType = TacticalTargetType.lowPriorityUnit
								newTarget.targetLeader = unit.player.leader
								newTarget.unit = unit

								if unit.isEmbarked():
									if unit.isCombatUnit():
										newTarget.targetType = TacticalTargetType.embarkedMilitaryUnit
									else:
										newTarget.targetType = TacticalTargetType.embarkedCivilian
								else:
									numberOfCities = len(simulation.citiesOf(self.player))
									if self.isVeryHighPriorityCivilianTarget(newTarget):
										# AI_TACTICAL_TARGET_VERY_HIGH_PRIORITY_CIVILIAN
										newTarget.targetType = TacticalTargetType.veryHighPriorityCivilian
									elif self.isHighPriorityCivilianTarget(newTarget, simulation.currentTurn, numberOfCities):
										newTarget.targetType = TacticalTargetType.highPriorityCivilian
									elif self.isMediumPriorityCivilianTarget(newTarget, simulation.currentTurn):
										newTarget.targetType = TacticalTargetType.mediumPriorityCivilian

								self.allTargets.append(newTarget)

						elif tile.hasOwner() and self.player == tile.owner() and \
							tile.defenseModifierFor(self.player) > 0 and \
							dangerPlotsAI.dangerAt(point) > 0.0:
							# ... defensive bastion?
							defenseCity = simulation.friendlyCityAdjacentTo(point, self.player)
							if defenseCity is not None:
								newTarget.targetType = TacticalTargetType.defensiveBastion
								newTarget.tile = tile
								newTarget.threatValue = defenseCity.threatValue() + int(
									dangerPlotsAI.dangerAt(point))
								self.allTargets.append(newTarget)

						elif tile.hasOwner() and self.player == tile.owner() and \
							tile.hasAnyImprovement() and \
							not tile.hasImprovement(ImprovementType.goodyHut) and tile.canBePillaged():
							# ... friendly improvement?
							newTarget.targetType = TacticalTargetType.improvementToDefend
							newTarget.tile = tile
							self.allTargets.append(newTarget)

		# POST - PROCESSING ON TARGETS

		# Mark enemy units threatening our cities( or camps) as priority targets
		if self.player.isBarbarian():
			self.identifyPriorityBarbarianTargets(simulation)
		else:
			self.identifyPriorityTargets(simulation)

		# Also add some priority targets that we'd like to hit just because of their unit type (e.g. catapults)
		self.identifyPriorityTargetsByType(simulation)

		# Remove extra targets
		self.eliminateNearbyBlockadePoints()

		# Sort remaining targets by aux data( if used for that target type)
		self.allTargets.sort(key=lambda target: target.threatValue)

	def identifyPriorityBarbarianTargets(self, simulation):
		"""Mark units that can damage our barbarian camps as priority targets"""
		mapSize = simulation.mapSize().size()

		for x in range(mapSize.width()):
			for y in range(mapSize.height()):
				point = HexPoint(x, y)
				tile = simulation.tileAt(point)

				if tile.hasImprovement(ImprovementType.barbarianCamp):
					for unitTarget in self.unitTargets():
						priorityTarget = False
						if unitTarget.targetType != TacticalTargetType.highPriorityUnit:
							enemyUnit = simulation.visibleEnemyAt(unitTarget.target, self.player)
							if enemyUnit is not None:
								if enemyUnit.canAttackRanged() and \
									enemyUnit.rangedCombatStrengthAgainst(None, None, tile, attacking=True,
																		  simulation=simulation) > \
									enemyUnit.attackStrengthAgainst(None, None, tile, simulation=simulation):

									if enemyUnit.location.distance(point) <= enemyUnit.range():
										priorityTarget = True
								elif enemyUnit.canReachAt(point, turns=1, simulation=simulation):
									priorityTarget = True

								if priorityTarget:
									unitTarget.targetType = TacticalTargetType.highPriorityUnit

		return

	def identifyPriorityTargetsByType(self, simulation):
		"""Mark units that we'd like to make opportunity attacks on because of their unit type (e.g. catapults)"""
		# Look through all the enemies we can see
		for target in self.allTargets:
			# Don't consider units that are already medium priority
			if target.targetType == TacticalTargetType.highPriorityUnit or target.targetType == TacticalTargetType.lowPriorityUnit:
				# Ranged units will always be medium priority targets
				if target.unit is not None:
					if target.unit.canAttackRanged():
						target.targetType = TacticalTargetType.mediumPriorityUnit

			# Don't consider units that are already high priority
			if target.targetType == TacticalTargetType.mediumPriorityUnit or target.targetType == TacticalTargetType.lowPriorityUnit:
				if target.unit is not None:
					tile = simulation.tileAt(target.unit.location)
					if tile is not None:
						# Units defending citadels will always be high priority targets
						if tile.hasImprovement(ImprovementType.fort) or tile.hasImprovement(ImprovementType.citadelle):
							target.targetType = TacticalTargetType.highPriorityUnit

		return

	def eliminateNearbyBlockadePoints(self):
		"""Don't allow tiles within 2 to both be blockade points"""
		# fatalError("not implemented yet")
		#
		#         /*# First, sort the sentry points by priority
		#         self.naval
		#         std::stable_sort(m_NavalResourceBlockadePoints.begin(), m_NavalResourceBlockadePoints.end());
		#
		#         # Create temporary copy of list
		#         TacticalList tempPoints;
		#         tempPoints = m_NavalResourceBlockadePoints;
		#
		#         # Clear out main list
		#         m_NavalResourceBlockadePoints.clear();
		#
		#         # Loop through all points in copy
		#         TacticalList::iterator it, it2;
		#         for (it = tempPoints.begin(); it != tempPoints.end(); ++it)
		#         {
		#             bool bFoundAdjacent = False;
		#
		#             # Is it adjacent to a point in the main list?
		#             for (it2 = m_NavalResourceBlockadePoints.begin(); it2 != m_NavalResourceBlockadePoints.end(); ++it2)
		#             {
		#                 if (plotDistance(it->GetTargetX(), it->GetTargetY(), it2->GetTargetX(), it2->GetTargetY()) <= 2)
		#                 {
		#                     bFoundAdjacent = True;
		#                     break;
		#                 }
		#             }
		#
		#             if (!bFoundAdjacent)
		#             {
		#                 m_NavalResourceBlockadePoints.push_back(*it);
		#             }
		#         }
		#
		#         # Now copy all points into main target list
		#         for (it = m_NavalResourceBlockadePoints.begin(); it != m_NavalResourceBlockadePoints.end(); ++it)
		#         {
		#             m_AllTargets.push_back(*it);
		#         } */
		pass

	def processDominanceZones(self, simulation):
		tacticalAnalysisMap = simulation.tacticalAnalysisMap()

		# Barbarian processing is straightforward - - just one big list of priorities and everything is considered at once
		if self.player.isBarbarian():
			self.establishBarbarianPriorities(simulation.currentTurn)
			self.extractTargets()
			self.assignBarbarianMoves(simulation)
		else:
			self.establishTacticalPriorities()
			self.updatePostures(simulation)

			# Proceed in priority order
			for move in self.movePriorityList:
				if move.priority < 0:
					continue

				if move.moveType.dominanceZoneMove():
					for dominanceZone in tacticalAnalysisMap.dominanceZones:
						self.currentDominanceZone = dominanceZone
						postureType = self.findPostureTypeFor(dominanceZone)

						# Is this move of the right type for this zone?
						match = False
						if move.moveType == TacticalMoveType.closeOnTarget:  # This one is okay for all zones
							match = True
						elif postureType == TacticalPostureType.withdraw and \
							move.moveType == TacticalMoveType.postureWithdraw:
							match = True
						elif postureType == TacticalPostureType.sitAndBombard and \
							move.moveType == TacticalMoveType.postureSitAndBombard:
							match = True
						elif postureType == TacticalPostureType.attritFromRange and \
							move.moveType == TacticalMoveType.postureAttritFromRange:
							match = True
						elif postureType == TacticalPostureType.exploitFlanks and \
							move.moveType == TacticalMoveType.postureExploitFlanks:
							match = True
						elif postureType == TacticalPostureType.steamRoll and \
							move.moveType == TacticalMoveType.postureSteamroll:
							match = True
						elif postureType == TacticalPostureType.surgicalCityStrike and \
							move.moveType == TacticalMoveType.postureSurgicalCityStrike:
							match = True
						elif postureType == TacticalPostureType.hedgehog and \
							move.moveType == TacticalMoveType.postureHedgehog:
							match = True
						elif postureType == TacticalPostureType.counterAttack and \
							move.moveType == TacticalMoveType.postureCounterAttack:
							match = True
						elif postureType == TacticalPostureType.shoreBombardment and \
							move.moveType == TacticalMoveType.postureShoreBombardment:
							match = True
						elif dominanceZone.dominanceFlag == TacticalDominanceType.enemy and \
							dominanceZone.territoryType == TacticalDominanceTerritoryType.friendly and \
							move.moveType == TacticalMoveType.emergencyPurchases:
							match = True

						if match:
							if not self.useThisDominanceZone(dominanceZone):
								continue

							self.extractTargets(dominanceZone)

							# Must have some moves to continue, or it must be landed around an enemy city
							# (which we always want to process because we might have an operation targeting it)
							if len(self.zoneTargets) == 0 and \
								dominanceZone.territoryType != TacticalDominanceTerritoryType.tempZone and \
								(dominanceZone.territoryType != TacticalDominanceTerritoryType.enemy or dominanceZone.isWater):
								continue

							self.assignTacticalMove(move, simulation)
				else:
					self.extractTargets()
					self.assignTacticalMove(move, simulation)

		return

	def establishBarbarianPriorities(self, turn: int):
		"""Choose which tactics the barbarians should emphasize this turn"""
		# Only establish priorities once per turn
		if turn <= self.movePriorityTurn:
			return

		self.movePriorityList = []
		self.movePriorityTurn = turn

		# Loop through each possible tactical move(other than "none" or "unassigned")
		for barbarianTacticalMove in TacticalMoveType.allBarbarianMoves():
			priority = barbarianTacticalMove.priority()

			# Make sure base priority is not negative
			if priority >= 0:
				# Finally, add a random die roll to each priority but only if not during test
				if not Tests.are_running:
					priority += random.randint(-2, 2)  # AI_TACTICAL_MOVE_PRIORITY_RANDOMNESS

				# Store off this move and priority
				move = TacticalMove()
				move.moveType = barbarianTacticalMove
				move.priority = priority
				self.movePriorityList.append(move)

		self.movePriorityList.sort()
		return

	def extractTargets(self, dominanceZone: Optional[TacticalDominanceZone] = None):
		"""Sift through the target list and find just those that apply to the dominance zone we are currently looking at"""
		self.zoneTargets = []

		for target in self.allTargets:
			if dominanceZone is not None:
				domain: UnitDomainType = UnitDomainType.sea if dominanceZone.isWater else UnitDomainType.land
				valid = target.isTargetValidIn(domain)
			else:
				valid = True

			if valid:
				if dominanceZone is None or (target.dominanceZone is not None and dominanceZone == target.dominanceZone):
					self.zoneTargets.append(target)
				elif dominanceZone is not None:
					# Not obviously in this zone, but if within 2 of city we want them anyway
					city = dominanceZone.closestCity
					if city is not None:
						if target.target.distance(city.location) <= 2:
							self.zoneTargets.append(target)

		# logging.debug(f"targets extracted: {len(self.zoneTargets)}")
		return

	def assignBarbarianMoves(self, simulation):
		"""Choose which tactics to run and assign units to it (barbarian version)"""
		for move in self.movePriorityList:
			if move.moveType == TacticalMoveType.barbarianCaptureCity:
				# AI_TACTICAL_BARBARIAN_CAPTURE_CITY
				self.plotCaptureCityMoves(simulation)
			elif move.moveType == TacticalMoveType.barbarianDamageCity:
				# AI_TACTICAL_BARBARIAN_DAMAGE_CITY
				self.plotDamageCityMoves(simulation)
			elif move.moveType == TacticalMoveType.barbarianDestroyHighPriorityUnit:
				# AI_TACTICAL_BARBARIAN_DESTROY_HIGH_PRIORITY_UNIT
				self.plotDestroyUnitMoves(TacticalTargetType.highPriorityUnit, mustBeAbleToKill=True,
										  attackAtPoorOdds=False, simulation=simulation)
			elif move.moveType == TacticalMoveType.barbarianDestroyMediumPriorityUnit:
				# AI_TACTICAL_BARBARIAN_DESTROY_MEDIUM_PRIORITY_UNIT
				self.plotDestroyUnitMoves(TacticalTargetType.mediumPriorityUnit, mustBeAbleToKill=True,
										  attackAtPoorOdds=False, simulation=simulation)
			elif move.moveType == TacticalMoveType.barbarianDestroyLowPriorityUnit:
				# AI_TACTICAL_BARBARIAN_DESTROY_LOW_PRIORITY_UNIT
				self.plotDestroyUnitMoves(TacticalTargetType.lowPriorityUnit, mustBeAbleToKill=True,
										  attackAtPoorOdds=False, simulation=simulation)
			elif move.moveType == TacticalMoveType.barbarianMoveToSafety:
				# AI_TACTICAL_BARBARIAN_MOVE_TO_SAFETY
				self.plotMovesToSafety(combatUnits=True, simulation=simulation)
			elif move.moveType == TacticalMoveType.barbarianAttritHighPriorityUnit:
				# AI_TACTICAL_BARBARIAN_ATTRIT_HIGH_PRIORITY_UNIT
				self.plotDestroyUnitMoves(TacticalTargetType.highPriorityUnit, mustBeAbleToKill=False,
										  attackAtPoorOdds=False, simulation=simulation)
			elif move.moveType == TacticalMoveType.barbarianAttritMediumPriorityUnit:
				# AI_TACTICAL_BARBARIAN_ATTRIT_MEDIUM_PRIORITY_UNIT
				self.plotDestroyUnitMoves(TacticalTargetType.mediumPriorityUnit, mustBeAbleToKill=False,
										  attackAtPoorOdds=False, simulation=simulation)
			elif move.moveType == TacticalMoveType.barbarianAttritLowPriorityUnit:
				# AI_TACTICAL_BARBARIAN_ATTRIT_LOW_PRIORITY_UNIT
				self.plotDestroyUnitMoves(TacticalTargetType.lowPriorityUnit, mustBeAbleToKill=False,
										  attackAtPoorOdds=False, simulation=simulation)
			elif move.moveType == TacticalMoveType.barbarianPillage:
				# AI_TACTICAL_BARBARIAN_PILLAGE
				self.plotPillageMoves(TacticalTargetType.improvementResource, firstPass=True, simulation=simulation)
			elif move.moveType == TacticalMoveType.barbarianPillageCitadel:
				# AI_TACTICAL_BARBARIAN_PILLAGE_CITADEL
				self.plotPillageMoves(TacticalTargetType.citadel, firstPass=True, simulation=simulation)
			elif move.moveType == TacticalMoveType.barbarianPillageNextTurn:
				# AI_TACTICAL_BARBARIAN_PILLAGE_NEXT_TURN
				self.plotPillageMoves(TacticalTargetType.citadel, firstPass=False, simulation=simulation)
				self.plotPillageMoves(TacticalTargetType.improvementResource, firstPass=False, simulation=simulation)
			elif move.moveType == TacticalMoveType.barbarianBlockadeResource:
				# AI_TACTICAL_BARBARIAN_PRIORITY_BLOCKADE_RESOURCE \
				# PlotBlockadeImprovementMoves();
				pass
			elif move.moveType == TacticalMoveType.barbarianCivilianAttack:
				# AI_TACTICAL_BARBARIAN_CIVILIAN_ATTACK
				self.plotCivilianAttackMoves(TacticalTargetType.veryHighPriorityCivilian, simulation=simulation)
				self.plotCivilianAttackMoves(TacticalTargetType.highPriorityCivilian, simulation=simulation)
				self.plotCivilianAttackMoves(TacticalTargetType.mediumPriorityCivilian, simulation=simulation)
				self.plotCivilianAttackMoves(TacticalTargetType.lowPriorityCivilian, simulation=simulation)
			elif move.moveType == TacticalMoveType.barbarianCampDefense:
				# AI_TACTICAL_BARBARIAN_CAMP_DEFENSE
				self.plotCampDefenseMoves(simulation)
			elif move.moveType == TacticalMoveType.barbarianAggressiveMove:
				# AI_TACTICAL_BARBARIAN_AGGRESSIVE_MOVE
				self.plotBarbarianMove(aggressive=True, simulation=simulation)
			elif move.moveType == TacticalMoveType.barbarianPassiveMove:
				# AI_TACTICAL_BARBARIAN_PASSIVE_MOVE
				self.plotBarbarianMove(aggressive=False, simulation=simulation)
			elif move.moveType == TacticalMoveType.barbarianDesperateAttack:
				# AI_TACTICAL_BARBARIAN_DESPERATE_ATTACK
				self.plotDestroyUnitMoves(TacticalTargetType.lowPriorityUnit, mustBeAbleToKill=False,
										  attackAtPoorOdds=True, simulation=simulation)
			elif move.moveType == TacticalMoveType.barbarianEscortCivilian:
				# AI_TACTICAL_BARBARIAN_ESCORT_CIVILIAN
				self.plotBarbarianCivilianEscortMove(simulation)
			elif move.moveType == TacticalMoveType.barbarianPlunderTradeUnit:
				# AI_TACTICAL_BARBARIAN_PLUNDER_TRADE_UNIT
				self.plotBarbarianPlunderTradeUnitMove(UnitDomainType.land, simulation)
				self.plotBarbarianPlunderTradeUnitMove(UnitDomainType.sea, simulation)
			elif move.moveType == TacticalMoveType.barbarianGuardCamp:
				self.plotGuardBarbarianCamp(simulation)
			else:
				logging.warning(f"not implemented: TacticalAI - {move.moveType}")

		self.reviewUnassignedBarbarianUnits(simulation)

	def plotGuardBarbarianCamp(self, simulation):
		"""Assigns a barbarian to go protect an undefended camp"""
		if not self.player.isBarbarian():
			return

		self.currentMoveUnits = []

		for loopUnit in self.currentTurnUnits:
			# is unit already at a camp?
			tile = simulation.tileAt(loopUnit.location)
			if tile is not None:
				if tile.hasImprovement(ImprovementType.barbarianCamp):
					unit = TacticalUnit(loopUnit)
					self.currentMoveUnits.append(unit)

		if len(self.currentMoveUnits) > 0:
			self.executeGuardBarbarianCamp(simulation)

		return

	def plotBarbarianCivilianEscortMove(self, simulation):
		"""Escort captured civilians back to barbarian camps"""
		if not self.player.isBarbarian():
			return

		self.currentMoveUnits = []

		for currentTurnUnit in self.currentTurnUnits:
			# Find any civilians we may have "acquired" from the civilizations
			if not currentTurnUnit.canAttack():
				unit = TacticalUnit(currentTurnUnit)
				self.currentMoveUnits.append(unit)

		if len(self.currentMoveUnits) > 0:
			self.executeBarbarianCivilianEscortMove(simulation)

		return

	def plotBarbarianPlunderTradeUnitMove(self, domain: UnitDomainType, simulation):
		"""Plunder trade routes"""
		targetType: TacticalTargetType = TacticalTargetType.none
		navalOnly = False

		if domain == UnitDomainType.land:
			targetType = TacticalTargetType.tradeUnitLand
		elif domain == UnitDomainType.sea:
			targetType = TacticalTargetType.tradeUnitSea
			navalOnly = True

		if targetType == TacticalTargetType.none:
			return

		for target in self.zoneTargetsFor(targetType):
			# See what units we have who can reach target this turn
			if self.findUnitsWithinStrikingDistanceTowards(target.target, numTurnsAway=0, noRangedUnits=False,
														   navalOnly=navalOnly, simulation=simulation):
				# Queue best one up to capture it
				self.executePlunderTradeUnitAt(target.target, simulation)

		return

	def zoneTargetsFor(self, targetType: TacticalTargetType) -> [TacticalTarget]:
		"""Find the first target of a requested type in current dominance zone (call after ExtractTargetsForZone())"""
		tempTargets: [TacticalTarget] = []
		for zoneTarget in self.zoneTargets:
			if targetType == TacticalTargetType.none or zoneTarget.targetType == targetType:
				tempTargets.append(zoneTarget)

		return tempTargets

	def plotDestroyUnitMoves(self, targetType: TacticalTargetType, mustBeAbleToKill: bool, attackAtPoorOdds: bool,
							 simulation):
		"""Assign a group of units to attack each unit we think we can destroy"""
		requiredDamage: int = 0
		expectedDamage: int = 0

		# See how many moves of this type we can execute
		for target in self.zoneTargetsFor(targetType):
			unitCanAttack = False
			cityCanAttack = False

			if target.target is not None:
				targetLocation = target.target
				tile = simulation.tileAt(targetLocation)

				if tile is None:
					continue

				defender = simulation.unitAt(targetLocation, UnitMapType.combat)

				if defender is not None:
					unitCanAttack = self.findUnitsWithinStrikingDistanceTowards(tile.point, numTurnsAway=1,
																				noRangedUnits=False,
																				simulation=simulation)
					cityCanAttack = self.findCitiesWithinStrikingDistanceOf(targetLocation, simulation)

					if unitCanAttack or cityCanAttack:
						expectedDamage = self.computeTotalExpectedDamage(target, tile, simulation)
						expectedDamage += self.computeTotalExpectedBombardDamageAgainst(defender, simulation)
						requiredDamage = defender.healthPoints()

						target.damage = requiredDamage

						if not mustBeAbleToKill:
							# Attack no matter what
							if attackAtPoorOdds:
								self.executeAttack(target, tile, inflictWhatWeTake=False, mustSurviveAttack=False,
												   simulation=simulation)
							else:
								# If we can at least knock the defender to 40 % strength with our combined efforts, go ahead even if each individual attack isn't favorable
								mustInflictWhatWeTake = True
								if expectedDamage >= (requiredDamage * 40) / 100:
									mustInflictWhatWeTake = False

								self.executeAttack(target, tile, inflictWhatWeTake=mustInflictWhatWeTake,
												   mustSurviveAttack=True, simulation=simulation)
						else:
							# Do we have enough firepower to destroy it?
							if expectedDamage > requiredDamage:
								self.executeAttack(target, tile, inflictWhatWeTake=False, mustSurviveAttack=(
										targetType != TacticalTargetType.highPriorityUnit), simulation=simulation)

			return

	def plotPillageMoves(self, targetType: TacticalTargetType, firstPass: bool, simulation):
		"""Assigns units to pillage enemy improvements"""
		for target in self.zoneTargetsFor(targetType):
			# # try paratroopers first, not because they are more effective, just because it looks cooler...
			# / * if (bFirstPass and FindParatroopersWithinStrikingDistance(pPlot))
			# {
			# # Queue best one up to capture it
			# ExecuteParadropPillage(pPlot);
			# } else * /
			if firstPass and self.findUnitsWithinStrikingDistanceTowards(target.target, numTurnsAway=0, noRangedUnits=False,
																  navalOnly=False, mustMoveThrough=True,
																  includeBlockedUnits=False, willPillage=True,
																  simulation=simulation):
				# Queue best one up to capture it
				self.executePillageAt(target.target, simulation)

			elif not firstPass and self.findUnitsWithinStrikingDistanceTowards(target.target, numTurnsAway=2,
																		noRangedUnits=False, navalOnly=False,
																		mustMoveThrough=False,
																		includeBlockedUnits=False, willPillage=True,
																		simulation=simulation):
				# No one can reach it this turn, what about next turn?
				self.executeMoveToTarget(target.target, garrisonIfPossible=False, simulation=simulation)

		return

	def plotCivilianAttackMoves(self, targetType: TacticalTargetType, simulation):
		"""Assigns units to capture undefended civilians"""
		for target in self.zoneTargetsFor(targetType):
			# See what units we have who can reach target this turn
			if self.findUnitsWithinStrikingDistanceTowards(target.target, numTurnsAway=1, noRangedUnits=False, navalOnly=False,
													mustMoveThrough=False, includeBlockedUnits=False, willPillage=False,
													targetUndefended=True, simulation=simulation):
				# Queue best one up to capture it
				self.executeCivilianCapture(target.target, simulation)

		return

	def plotCampDefenseMoves(self, simulation):
		"""Assigns a barbarian to go protect an undefended camp"""
		for target in self.zoneTargetsFor(TacticalTargetType.barbarianCamp):
			if self.findUnitsWithinStrikingDistanceTowards(target.target, numTurnsAway=1, noRangedUnits=True, navalOnly=False,
													mustMoveThrough=False, includeBlockedUnits=False, willPillage=False,
													targetUndefended=True, simulation=simulation):
				self.executeMoveToPlot(target.target, saveMoves=False, simulation=simulation)

		return

	def plotMovesToSafety(self, combatUnits: bool, simulation):
		"""Moved endangered units to safe hexes"""
		dangerPlotsAI = self.player.dangerPlotsAI

		self.currentMoveUnits = []

		# Loop through all recruited units
		for currentUnit in self.currentTurnUnits:

			if currentUnit is not None:
				dangerLevel = dangerPlotsAI.dangerAt(currentUnit.location)

				# Danger value of plot must be greater than 0
				if dangerLevel > 0:
					addUnit = False
					if combatUnits:
						# If under 100% health, might flee to safety
						if currentUnit.damage() > 0:
							if currentUnit.player.isBarbarian():
								# Barbarian combat units - only naval units flee (but they flee if they have taken ANY damage)
								if currentUnit.domain() == UnitDomainType.sea:
									addUnit = True

							# Everyone else flees at less than or equal to 50 %combat strength
							elif currentUnit.damage() > 50:
								addUnit = True

						# Also flee if danger is really high in current plot (but not if we're barbarian)
						elif not currentUnit.player.isBarbarian():
							acceptableDanger = currentUnit.baseCombatStrength(ignoreEmbarked=True) * 100
							if int(dangerLevel) > acceptableDanger:
								addUnit = True

					else:
						# Civilian( or embarked) units always flee from danger
						if not currentUnit.canFortifyAt(currentUnit.location, simulation):
							addUnit = True

					if addUnit:
						# Just one unit involved in this move to execute
						tacticalUnit: TacticalUnit = TacticalUnit(currentUnit)
						self.currentMoveUnits.append(tacticalUnit)

		if len(self.currentMoveUnits) > 0:
			self.executeMovesToSafestPlot(simulation)

		return

	def plotCaptureCityMoves(self, simulation) -> bool:
		"""Assign a group of units to take down each city we can capture"""
		attackMade = False

		# See how many moves of this type we can execute
		for target in self.zoneTargetsFor(TacticalTargetType.city):
			# See what units we have who can reach target this turn
			tile = simulation.tileAt(target.target)
			if tile is None:
				continue

			if self.findUnitsWithinStrikingDistanceTowards(tile.point, numTurnsAway=1, simulation=simulation):
				# Do we have enough firepower to destroy it?
				city = simulation.cityAt(tile.point)
				if city is not None:
					requiredDamage = 200 - city.damage()
					target.damage = requiredDamage

					if self.computeTotalExpectedDamage(target, tile, simulation) >= requiredDamage:
						logging.debug(f"### Attacking city of {city.name} to capture {city.location} by {self.player.leader}")
						# If so, execute enough moves to take it
						self.executeAttack(target, tile, inflictWhatWeTake := False, mustSurviveAttack=False,
										   simulation=simulation)
						attackMade = True

						# Did it work?  If so, don't need a temporary dominance zone if had one here
						if tile.owner() == self.player:
							self.deleteTemporaryZoneAt(tile.point)

		return attackMade

	def plotDamageCityMoves(self, simulation) -> bool:
		"""Assign a group of units to take down each city we can capture"""
		attackMade = False

		# See how many moves of this type we can execute
		for target in self.zoneTargetsFor(TacticalTargetType.city):
			# See what units we have who can reach target this turn
			tile = simulation.tileAt(target.target)
			if tile is None:
				continue

			self.currentMoveCities = []

			if self.findUnitsWithinStrikingDistanceTowards(tile.point, numTurnsAway=1, noRangedUnits=False, navalOnly=False,
													mustMoveThrough=False, includeBlockedUnits=True,
													simulation=simulation):
				city = simulation.cityAt(tile.point)
				if city is not None:
					requiredDamage = city.maxHealthPoints() - city.damage()
					target.damage = requiredDamage

					# Don't want to hammer away to try and take down a city for more than 8 turns
					if self.computeTotalExpectedDamage(target, tile, simulation) > (requiredDamage / 8):
						# If so, execute enough moves to take it
						self.executeAttack(target, tile, inflictWhatWeTake=False, mustSurviveAttack=True,
										   simulation=simulation)
						attackMade = True

		return attackMade

	def plotBarbarianMove(self, aggressive: bool, simulation):
		"""Move barbarians across the map"""
		if not self.player.isBarbarian():
			return

		self.currentMoveUnits = []

		# Loop through all recruited units
		for currentTurnUnit in self.currentTurnUnits:
			unit = TacticalUnit(currentTurnUnit)
			self.currentMoveUnits.append(unit)

		if len(self.currentMoveUnits) > 0:
			self.executeBarbarianMoves(aggressive=aggressive, simulation=simulation)

		return

	def reviewUnassignedBarbarianUnits(self, simulation):
		"""Log that we couldn't find assignments for some units"""
		# Loop through all remaining units
		for currentTurnUnit in self.currentTurnUnits:
			# Barbarians and air units aren't handled by the operational or homeland AIs
			if currentTurnUnit.player.isBarbarian() or currentTurnUnit.domain() == UnitDomainType.air:
				currentTurnUnit.pushMission(UnitMission(UnitMissionType.skip), simulation)
				currentTurnUnit.setTurnProcessed(True)

				logging.debug(f"<< TacticalAI - barbarian ### Unassigned {currentTurnUnit.name()} at {currentTurnUnit.location}")

		return

	def isAlreadyTargeted(self, point: HexPoint) -> Optional[QueuedAttack]:
		"""Do we already have a queued attack running on this plot? Return series ID if yes, nil if no."""
		if len(self.queuedAttacks) == 0:
			return None

		for queuedAttack in self.queuedAttacks:
			target = queuedAttack.target
			if target is not None:
				if target.target == point:
					return queuedAttack

		return None

	def identifyPriorityTargets(self, simulation):
		"""Mark units that we'd like to make opportunity attacks on because of their unit type (e.g. catapults)"""
		# Look through all the enemies we can see
		for target in self.allTargets:
			# Don't consider units that are already medium priority
			if target.targetType == TacticalTargetType.highPriorityUnit or \
				target.targetType == TacticalTargetType.lowPriorityUnit:
				# Ranged units will always be medium priority targets
				unit = target.unit
				if unit is not None:
					if unit.canAttackRanged():
						target.targetType = TacticalTargetType.mediumPriorityUnit

			# Don't consider units that are already high priority
			if target.targetType == TacticalTargetType.mediumPriorityUnit or \
				target.targetType == TacticalTargetType.lowPriorityUnit:

				unit = target.unit
				if unit is not None:
					tile = simulation.tileAt(unit.location)

					# Units defending citadels will always be high priority targets
					if tile.hasImprovement(ImprovementType.fort) or tile.hasImprovement(ImprovementType.citadelle):
						target.targetType = TacticalTargetType.highPriorityUnit

		return

	def establishTacticalPriorities(self):
		"""Choose which tactics to emphasize this turn"""
		self.movePriorityList = []

		for tacticalMove in TacticalMoveType.allPlayerMoves():
			priority = tacticalMove.priority()

			# Make sure base priority is not negative
			if priority >= 0:

				# Finally, add a random die roll to each priority
				priority += random.randint(-2, 2)  # AI_TACTICAL_MOVE_PRIORITY_RANDOMNESS

				# Store off this move and priority
				move = TacticalMove()
				move.moveType = tacticalMove
				move.priority = priority
				self.movePriorityList.append(move)

		# Loop through each possible tactical move
		self.movePriorityList.sort()

	def updatePostures(self, simulation):
		"""Establish postures for each dominance zone (taking into account last posture)"""
		tacticalAnalysisMap = simulation.tacticalAnalysisMap()

		newPostures: [TacticalPosture] = []

		for dominanceZone in tacticalAnalysisMap.dominanceZones:

			# Check to make sure we want to use this zone
			if self.useThisDominanceZone(dominanceZone):

				lastPostureType = self.findPostureTypeFor(dominanceZone)
				newPostureType = self.selectPostureTypeFor(dominanceZone, lastPostureType, tacticalAnalysisMap.dominancePercentage)

				posture = TacticalPosture(
					newPostureType,
					dominanceZone.owner,
					dominanceZone.closestCity,
					dominanceZone.isWater
				)
				newPostures.append(posture)

		self.postures = newPostures

	def assignTacticalMove(self, tacticalMove: TacticalMove, simulation):
		"""Choose which tactics to run and assign units to it"""
		if tacticalMove.moveType == TacticalMoveType.moveNoncombatantsToSafety:
			# TACTICAL_MOVE_NONCOMBATANTS_TO_SAFETY
			self.plotMovesToSafety(combatUnits=False, simulation=simulation)
		elif tacticalMove.moveType == TacticalMoveType.reposition:
			# TACTICAL_REPOSITION
			self.plotRepositionMoves(simulation)
		elif tacticalMove.moveType == TacticalMoveType.garrisonAlreadyThere:
			# TACTICAL_GARRISON_ALREADY_THERE
			self.plotGarrisonMoves(numTurnsAway=0, simulation=simulation)
		elif tacticalMove.moveType == TacticalMoveType.garrisonToAllowBombards:
			# TACTICAL_GARRISON_TO_ALLOW_BOMBARD
			self.plotGarrisonMoves(numTurnsAway=1, mustAllowRangedAttack=True, simulation=simulation)
		elif tacticalMove.moveType == TacticalMoveType.captureCity:
			# TACTICAL_CAPTURE_CITY
			self.plotCaptureCityMoves(simulation)
		elif tacticalMove.moveType == TacticalMoveType.damageCity:
			# TACTICAL_DAMAGE_CITY
			self.plotDamageCityMoves(simulation)
		elif tacticalMove.moveType == TacticalMoveType.destroyHighUnit:
			# TACTICAL_DESTROY_HIGH_UNIT
			self.plotDestroyUnitMoves(TacticalTargetType.highPriorityUnit, mustBeAbleToKill=True, attackAtPoorOdds=False, simulation=simulation)
		elif tacticalMove.moveType == TacticalMoveType.destroyMediumUnit:
			# TACTICAL_DESTROY_MEDIUM_UNIT
			self.plotDestroyUnitMoves(TacticalTargetType.mediumPriorityUnit, mustBeAbleToKill=True, attackAtPoorOdds=False, simulation=simulation)
		elif tacticalMove.moveType == TacticalMoveType.destroyLowUnit:
			# TACTICAL_DESTROY_LOW_UNIT
			self.plotDestroyUnitMoves(TacticalTargetType.lowPriorityUnit, mustBeAbleToKill=True, attackAtPoorOdds=False, simulation=simulation)
		elif tacticalMove.moveType == TacticalMoveType.toSafety:
			# TACTICAL_TO_SAFETY
			self.plotMovesToSafety(combatUnits=True, simulation=simulation)
		elif tacticalMove.moveType == TacticalMoveType.attritHighUnit:
			# TACTICAL_ATTRIT_HIGH_UNIT
			self.plotDestroyUnitMoves(TacticalTargetType.highPriorityUnit, mustBeAbleToKill=False, attackAtPoorOdds=False, simulation=simulation)
		elif tacticalMove.moveType == TacticalMoveType.attritMediumUnit:
			# TACTICAL_ATTRIT_MEDIUM_UNIT
			self.plotDestroyUnitMoves(TacticalTargetType.mediumPriorityUnit, mustBeAbleToKill=False, attackAtPoorOdds=False, simulation=simulation)
		elif tacticalMove.moveType == TacticalMoveType.attritLowUnit:
			# TACTICAL_ATTRIT_LOW_UNIT
			self.plotDestroyUnitMoves(TacticalTargetType.lowPriorityUnit, mustBeAbleToKill=False, attackAtPoorOdds=False, simulation=simulation)
		elif tacticalMove.moveType == TacticalMoveType.barbarianCamp:
			# TACTICAL_BARBARIAN_CAMP
			self.plotBarbarianCampMoves(simulation)
		elif tacticalMove.moveType == TacticalMoveType.pillage:
			# TACTICAL_PILLAGE
			self.plotPillageMoves(TacticalTargetType.improvement, firstPass=True, simulation=simulation)
		elif tacticalMove.moveType == TacticalMoveType.civilianAttack:
			# fatalError("not implemented yet")
			# NOOP
			pass
		elif tacticalMove.moveType == TacticalMoveType.safeBombards:
			# TACTICAL_SAFE_BOMBARDS
			self.plotSafeBombardMoves(simulation)
		elif tacticalMove.moveType == TacticalMoveType.heal:
			# TACTICAL_HEAL
			self.plotHealMoves(simulation)
		elif tacticalMove.moveType == TacticalMoveType.ancientRuins:
			# TACTICAL_ANCIENT_RUINS
			self.plotAncientRuinMoves(turnsAway=1, simulation=simulation)
		elif tacticalMove.moveType == TacticalMoveType.bastionAlreadyThere:
			# TACTICAL_BASTION_ALREADY_THERE
			self.plotBastionMoves(numTurnsAway=0, simulation=simulation)
		elif tacticalMove.moveType == TacticalMoveType.guardImprovementAlreadyThere:
			# TACTICAL_GUARD_IMPROVEMENT_ALREADY_THERE
			self.plotGuardImprovementMoves(numTurnsAway=0, simulation=simulation)
		elif tacticalMove.moveType == TacticalMoveType.bastionOneTurn:
			# TACTICAL_BASTION_1_TURN
			self.plotBastionMoves(numTurnsAway=1, simulation=simulation)
		elif tacticalMove.moveType == TacticalMoveType.garrisonOneTurn:
			# TACTICAL_GARRISON_1_TURN
			self.plotGarrisonMoves(numTurnsAway=1, simulation=simulation)
		elif tacticalMove.moveType == TacticalMoveType.guardImprovementOneTurn:
			# TACTICAL_GUARD_IMPROVEMENT_1_TURN
			self.plotGuardImprovementMoves(numTurnsAway=1, simulation=simulation)
		elif tacticalMove.moveType == TacticalMoveType.airSweep:
			# TACTICAL_AIR_SWEEP
			self.plotAirSweepMoves(simulation)
		elif tacticalMove.moveType == TacticalMoveType.airIntercept:
			# TACTICAL_AIR_INTERCEPT
			self.plotAirInterceptMoves(simulation)
		elif tacticalMove.moveType == TacticalMoveType.airRebase:
			# fatalError("not implemented yet")
			# NOOP
			pass
		elif tacticalMove.moveType == TacticalMoveType.closeOnTarget:
			# TACTICAL_CLOSE_ON_TARGET
			self.plotCloseOnTarget(checkDominance=True, simulation=simulation)
		elif tacticalMove.moveType == TacticalMoveType.moveOperation:
			# TACTICAL_MOVE_OPERATIONS
			self.plotOperationalArmyMoves(simulation)
		elif tacticalMove.moveType == TacticalMoveType.emergencyPurchases:
			# TACTICAL_EMERGENCY_PURCHASES
			self.plotEmergencyPurchases(simulation)
		elif tacticalMove.moveType == TacticalMoveType.postureWithdraw:
			# TACTICAL_POSTURE_WITHDRAW
			self.plotWithdrawMoves(simulation)
		elif tacticalMove.moveType == TacticalMoveType.postureSitAndBombard:
			# TACTICAL_POSTURE_SIT_AND_BOMBARD
			self.plotSitAndBombardMoves(simulation)
		elif tacticalMove.moveType == TacticalMoveType.postureAttritFromRange:
			# TACTICAL_POSTURE_ATTRIT_FROM_RANGE
			self.plotAttritFromRangeMoves(simulation)
		elif tacticalMove.moveType == TacticalMoveType.postureExploitFlanks:
			# TACTICAL_POSTURE_EXPLOIT_FLANKS
			self.plotExploitFlanksMoves(simulation)
		elif tacticalMove.moveType == TacticalMoveType.postureSteamroll:
			# TACTICAL_POSTURE_STEAMROLL
			self.plotSteamrollMoves(simulation)
		elif tacticalMove.moveType == TacticalMoveType.postureSurgicalCityStrike:
			# TACTICAL_POSTURE_SURGICAL_CITY_STRIKE
			self.plotSurgicalCityStrikeMoves(simulation)
		elif tacticalMove.moveType == TacticalMoveType.postureHedgehog:
			# TACTICAL_POSTURE_HEDGEHOG
			self.plotHedgehogMoves(simulation)
		elif tacticalMove.moveType == TacticalMoveType.postureCounterAttack:
			# TACTICAL_POSTURE_COUNTERATTACK
			self.plotCounterAttackMoves(simulation)
		elif tacticalMove.moveType == TacticalMoveType.postureShoreBombardment:
			# TACTICAL_POSTURE_SHORE_BOMBARDMENT
			self.plotShoreBombardmentMoves(simulation)
		else:
			# NOOP
			logging.warning(f"not implemented: TacticalAI - {tacticalMove.moveType}")

	def plotOperationalArmyMoves(self, simulation):
		"""Process units that we recruited out of operational moves.
		Haven't used them, so let them go ahead with those moves"""
		self.player.operations.plotArmyMoves(simulation)

	def plotSafeBombardMoves(self, simulation):
		"""Find all targets that we can bombard easily"""
		tacticalAnalysisMap = simulation.tacticalAnalysisMap()

		for target in self.zoneTargetsFor(TacticalTargetType.highPriorityUnit):
			if target.isTargetStillAliveFor(self.player, simulation):
				bestFriendlyRange = tacticalAnalysisMap.bestFriendlyRange()
				canIgnoreLightOfSight = tacticalAnalysisMap.canIgnoreLightOfSight()

				tacticalAnalysisMap.clearDynamicFlags()
				tacticalAnalysisMap.setTargetBombardCells(
					target.target,
					bestFriendlyRange=bestFriendlyRange,
					canIgnoreLightOfSight=canIgnoreLightOfSight,
					simulation=simulation
				)

				self.executeSafeBombardsOn(target, simulation)

		for target in self.zoneTargetsFor(TacticalTargetType.mediumPriorityUnit):
			if target.isTargetStillAliveFor(self.player, simulation):
				# m_pMap->ClearDynamicFlags();
				# m_pMap->SetTargetBombardCells(pTargetPlot, m_pMap->GetBestFriendlyRange(), m_pMap->CanIgnoreLOS());
				self.executeSafeBombardsOn(target, simulation)

		for target in self.zoneTargetsFor(TacticalTargetType.lowPriorityUnit):
			if target.isTargetStillAliveFor(self.player, simulation):
				# m_pMap->ClearDynamicFlags();
				# m_pMap->SetTargetBombardCells(pTargetPlot, m_pMap->GetBestFriendlyRange(), m_pMap->CanIgnoreLOS());
				self.executeSafeBombardsOn(target, simulation)

		for target in self.zoneTargetsFor(TacticalTargetType.embarkedMilitaryUnit):
			if target.isTargetStillAliveFor(self.player, simulation):
				# m_pMap->ClearDynamicFlags();
				# m_pMap->SetTargetBombardCells(pTargetPlot, m_pMap->GetBestFriendlyRange(), m_pMap->CanIgnoreLOS());
				self.executeSafeBombardsOn(target, simulation)

		return

	def plotAncientRuinMoves(self, turnsAway, simulation):
		"""Pop goody huts nearby"""
		for zoneTarget in self.zoneTargetsFor(TacticalTargetType.ancientRuins):
			# Grab units that make sense for this move type
			plot = simulation.tileAt(zoneTarget.target)

			self.findUnitsFor(TacticalMoveType.ancientRuins, plot, rangedOnly=False, simulation=simulation)

			if (len(self.currentMoveHighPriorityUnits) + len(self.currentMoveUnits)) > 0:
				self.executeMoveToTarget(plot.point, garrisonIfPossible=False, simulation=simulation)

				logging.debug(f"Moving to goody hut, {zoneTarget.target}, Turns Away: {turnsAway}")

		return

	def plotAirInterceptMoves(self, simulation):
		"""Set fighters to intercept"""
		pass

	def plotGarrisonMoves(self, numTurnsAway: int, mustAllowRangedAttack: bool=False, simulation=None):
		"""Make a defensive move to garrison a city"""
		if simulation is None:
			raise Exception('simulation must not be None')

		for target in self.zoneTargetsFor(TacticalTargetType.cityToDefend):
			tile = simulation.tileAt(target.target)

			if tile is None:
				continue

			city = simulation.cityAt(target.target)

			if city is None:
				continue

			if city.lastTurnGarrisonAssigned() < simulation.currentTurn:
				# Grab units that make sense for this move type
				self.findUnitsFor(TacticalMoveType.garrisonAlreadyThere, tile, turnsAway=numTurnsAway, rangedOnly=mustAllowRangedAttack, simulation=simulation)

				if (len(self.currentMoveHighPriorityUnits) + len(self.currentMoveUnits)) > 0:

					self.executeMoveToTarget(target.target, garrisonIfPossible=True, simulation=simulation)
					city.setLastTurnGarrisonAssigned(simulation.currentTurn)

		return

	def findUnitsFor(self, move: TacticalMoveType, targetTile, turnsAway: int = -1, rangedOnly: bool = True, simulation = None) -> bool:
		"""Finds both high and normal priority units we can use for this move (returns True if at least 1 unit found)"""
		if simulation is None:
			raise Exception('simulation must not be None')
		
		rtnValue = False

		self.currentMoveUnits = []
		self.currentMoveHighPriorityUnits = []

		# Loop through all units available to tactical AI this turn
		for loopUnit in self.currentTurnUnits:
			if loopUnit.domain() != UnitDomainType.air and loopUnit.isCombatUnit():

				# Make sure domain matches
				if loopUnit.domain() == UnitDomainType.sea and not targetTile.terrain().isWater() or \
					loopUnit.domain() == UnitDomainType.land and targetTile.terrain().isWater():
					continue

				suitableUnit = False
				highPriority = False

				if move == TacticalMoveType.garrisonAlreadyThere or move == TacticalMoveType.garrisonOneTurn:
					# Want to put ranged units in cities to give them a ranged attack
					if loopUnit.isRanged():
						suitableUnit = True
						highPriority = True
					elif rangedOnly:
						continue

					# Don't put units with a combat strength boosted from promotions in cities, these boosts are ignored
					if loopUnit.defenseModifierAgainst(None, None, None, ranged=False, simulation=simulation) == 0 and \
						loopUnit.attackModifierAgainst(None, None, None, simulation) == 0:
						suitableUnit = True
				elif move == TacticalMoveType.guardImprovementAlreadyThere or \
					move == TacticalMoveType.guardImprovementOneTurn or \
					move == TacticalMoveType.bastionAlreadyThere or move == TacticalMoveType.bastionOneTurn:

					# No ranged units or units without defensive bonuses as plot defenders
					if not loopUnit.isRanged():  # and !loopUnit->noDefensiveBonus()*/ {
						suitableUnit = True

						# Units with defensive promotions are especially valuable
						if loopUnit.defenseModifierAgainst(None, None, None, ranged=False, simulation=simulation) > 0: # or pLoopUnit->getExtraCombatPercent() > 0*/ {
							highPriority = True
				elif move == TacticalMoveType.ancientRuins:

					# Fast movers are top priority
					if loopUnit.hasTask(UnitTaskType.fastAttack):
						suitableUnit = True
						highPriority = True
					elif loopUnit.canAttack():
						suitableUnit = True

				if suitableUnit:
					# Is it even possible for the unit to reach in the number of requested turns (ignoring roads and RR)
					distance = targetTile.point.distance(loopUnit.location)
					if loopUnit.maxMoves(simulation) > 0:
						movesPerTurn = loopUnit.maxMoves(simulation) # / GC.getMOVE_DENOMINATOR();
						leastTurns = (distance + movesPerTurn - 1) / movesPerTurn

						if turnsAway == -1 or leastTurns <= turnsAway:

							# If unit was suitable, and close enough, add it to the proper list
							pathFinderDataSource = simulation.ignoreUnitsPathfinderDataSource(
								loopUnit.movementType(),
								loopUnit.player,
								canEmbark=loopUnit.player.canEmbark(),
								canEnterOcean=self.player.canEnterOcean()
							)
							pathFinder = AStarPathfinder(pathFinderDataSource)
							moves = pathFinder.turnsToReachTarget(loopUnit, targetTile.point, simulation)

							if moves != sys.maxsize and (turnsAway == -1 or (turnsAway == 0 and loopUnit.location == targetTile.point) or moves <= turnsAway):

								unit = TacticalUnit(loopUnit)
								unit.healthPercent = loopUnit.healthPoints() * 100 / loopUnit.maxHealthPoints()
								unit.movesToTarget = moves

								if highPriority:
									self.currentMoveHighPriorityUnits.append(unit)
								else:
									self.currentMoveUnits.append(unit)

								rtnValue = True

		return rtnValue

	def plotBarbarianCampMoves(self, simulation):
		"""Assign a unit to capture an undefended barbarian camp"""
		for target in self.zoneTargetsFor(TacticalTargetType.barbarianCamp):
			targetPoint: Optional[HexPoint] = target.target

			if targetPoint is None:
				continue

			if self.findUnitsWithinStrikingDistanceTowards(
				targetPoint,
				numTurnsAway=1,
				noRangedUnits=False,
				navalOnly=False,
				mustMoveThrough=False,
				includeBlockedUnits=False, willPillage=False, targetUndefended=True, simulation=simulation):

				# Queue best one up to capture it
				self.executeBarbarianCampMove(targetPoint, simulation)

				logging.debug(f"Removing barbarian camp, {targetPoint}")

				self.deleteTemporaryZoneAt(targetPoint)

		return

	def plotAirSweepMoves(self, simulation):
		"""Set fighters to air sweep"""
		pass

	def plotHealMoves(self, simulation):
		"""Assigns units to heal"""
		self.currentMoveUnits = []

		# Loop through all recruited units
		for currentTurnUnit in self.currentTurnUnits:
			unit = currentTurnUnit

			if unit is None:
				continue

			# Am I under 100% health and not embarked or already in a city?
			if unit.healthPoints() < unit.maxHealthPoints() and not unit.isEmbarked() and simulation.cityAt(unit.location) is None:
				# If I'm a naval unit I need to be in friendly territory
				if unit.domain() != UnitDomainType.sea or simulation.tileAt(unit.location).isFriendlyTerritory(self.player, simulation):
					if not unit.isUnderEnemyRangedAttack():
						self.currentMoveUnits.append(TacticalUnit(unit))

						logging.debug(f"Healing at, {unit.location}")

		if len(self.currentMoveUnits) > 0:
			self.executeHeals(simulation)

		return

	def plotBastionMoves(self, numTurnsAway: int, simulation):
		"""Establish a defensive bastion adjacent to a city"""
		for zoneTarget in self.zoneTargetsFor(TacticalTargetType.defensiveBastion):
			plot = simulation.tileAt(zoneTarget.target)

			# Grab units that make sense for this move type
			if plot is None:
				continue

			self.findUnitsFor(TacticalMoveType.bastionAlreadyThere, plot, turnsAway=numTurnsAway, rangedOnly=False, simulation=simulation)

			if (len(self.currentMoveHighPriorityUnits) + len(self.currentMoveUnits)) > 0:
				self.executeMoveToTarget(zoneTarget.target, garrisonIfPossible=False, simulation=simulation)

				logging.debug(f"Bastion, {zoneTarget.target}, Priority: {zoneTarget.threatValue}, Turns Away: {numTurnsAway}")

		return

	def plotGuardImprovementMoves(self, numTurnsAway, simulation):
		"""Make a defensive move to guard an improvement"""
		for zoneTarget in self.zoneTargetsFor(TacticalTargetType.improvementToDefend):
			plot = simulation.tileAt(zoneTarget.target)

			# Grab units that make sense for this move type
			if plot is None:
				continue

			self.findUnitsFor(TacticalMoveType.bastionAlreadyThere, plot, turnsAway=numTurnsAway, rangedOnly=False, simulation=simulation)

			if (len(self.currentMoveHighPriorityUnits) + len(self.currentMoveUnits)) > 0:
				self.executeMoveToTarget(zoneTarget.target, garrisonIfPossible=False, simulation=simulation)

				logging.debug(f"Guard Improvement, {zoneTarget.target}, Turns Away: {numTurnsAway}")

		return

	def plotRepositionMoves(self, simulation):
		"""Move units to a better location"""
		self.currentMoveUnits = []

		# Loop through all recruited units
		for currentTurnUnit in self.currentTurnUnits:
			self.currentMoveUnits.append(TacticalUnit(currentTurnUnit))

		if len(self.currentMoveUnits) > 0:
			self.executeRepositionMoves(simulation)

		return

	def executeBarbarianMoves(self, aggressive: bool, simulation):
		"""Move barbarian to a new location"""
		for currentMoveUnitRef in self.currentMoveUnits:
			unit = currentMoveUnitRef.unit
			if unit.isBarbarian():
				# LAND MOVES
				if unit.domain() == UnitDomainType.land:
					if aggressive:
						bestPlot: Optional[HexPoint] = self.findBestBarbarianLandMoveFor(unit, simulation)
					else:
						bestPlot: Optional[HexPoint] = self.findPassiveBarbarianLandMoveFor(unit, simulation)

					if bestPlot is not None:
						self.moveToEmptySpaceNearTarget(unit, bestPlot, land=True, simulation=simulation)
						unit.finishMoves()
						self.unitProcessed(unit, simulation=simulation)
					else:
						unit.finishMoves()
						self.unitProcessed(unit, simulation=simulation)

				else:  # NAVAL MOVES
					bestPlot: Optional[HexPoint] = None

					# Do I still have a destination from a previous turn?
					currentDestination = unit.tacticalTarget()

					# Compute a new destination if I don't have one or am already there
					if currentDestination is None or currentDestination == unit.location:
						bestPlot = self.findBestBarbarianSeaMove(unit, simulation)
					else:  # Otherwise just keep moving there (assuming a path is available)
						if unit.turnsToReach(currentDestination, simulation) != sys.maxsize:
							bestPlot = currentDestination
						else:
							bestPlot = self.findBestBarbarianSeaMove(unit, simulation)

					if bestPlot is not None:
						unit.setTacticalTarget(bestPlot)
						unit.pushMission(UnitMission(UnitMissionType.moveTo, bestPlot), simulation)
						unit.finishMoves()
						self.unitProcessed(unit, simulation=simulation)
					else:
						unit.resetTacticalTarget()
						unit.finishMoves()
						self.unitProcessed(unit, simulation=simulation)
		
		return

	def findBestBarbarianLandMoveFor(self, unit, simulation) -> Optional[HexPoint]:
		"""Find a multi-turn target for a land barbarian to wander towards"""
		landBarbarianRange = simulation.handicap.barbarianLandTargetRange()
		bestMovePlot = self.findNearbyTargetFor(unit, landBarbarianRange, TacticalTargetType.none, None, simulation=simulation)

		# move toward trade routes
		if bestMovePlot is None:
			bestMovePlot = self.findBarbarianGankTradeRouteTargetFor(unit, simulation)

		# explore wander
		if bestMovePlot is None:
			bestMovePlot = self.findBarbarianExploreTargetFor(unit, simulation)

		return bestMovePlot

	def findPassiveBarbarianLandMoveFor(self, unit, simulation) -> Optional[HexPoint]:
		"""Find a multi-turn target for a land barbarian to wander towards"""
		bestValue: int = sys.maxsize
		bestMovePlot = None

		for target in self.allTargets:
			# Is this target a camp?
			if target.targetType == TacticalTargetType.barbarianCamp:
				value = unit.location.distance(target.target)
				if value < bestValue:
					bestValue = value
					bestMovePlot = target.target

		if bestMovePlot is None:
			bestMovePlot = self.findBarbarianExploreTargetFor(unit, simulation)

		return bestMovePlot

	def findNearbyTargetFor(self, unit, radius: int, targetType: TacticalTargetType=TacticalTargetType.none,
							noLikeUnit=None, simulation=None) -> Optional[HexPoint]:
		if simulation is None:
			raise Exception('simulation must not be None')

		bestMovePlot: Optional[HexPoint] = None
		bestValue: int = sys.maxsize

		# Loop through all appropriate targets to find the closest
		for zoneTarget in self.zoneTargets:
			# Is the target of an appropriate type?
			typeMatch = False

			if targetType == TacticalTargetType.none:
				if zoneTarget.targetType == TacticalTargetType.highPriorityUnit or \
					zoneTarget.targetType == TacticalTargetType.mediumPriorityUnit or \
					zoneTarget.targetType == TacticalTargetType.lowPriorityUnit or \
					zoneTarget.targetType == TacticalTargetType.city or \
					zoneTarget.targetType == TacticalTargetType.improvement:

					typeMatch = True
			elif zoneTarget.targetType == targetType:
				typeMatch = True

			# Is this unit near enough?
			if typeMatch:
				tile = simulation.tileAt(zoneTarget.target)
				unitTile = simulation.tileAt(unit.location)

				if tile is not None and unitTile is not None:
					distance = tile.point.distance(unit.location)

					if distance == 0:
						return tile.point
					elif distance < radius:
						if unitTile.area == tile.area:
							unitAtTile = simulation.unitAt(tile.point, UnitMapType.combat)
							if noLikeUnit is not None and unitAtTile is not None and unitAtTile.hasSameType(noLikeUnit):
								value = unit.turnsToReach(tile.point, simulation)

								if value < bestValue:
									bestMovePlot = tile.point
									bestValue = value

		return bestMovePlot

	def findBarbarianGankTradeRouteTargetFor(self, unit, simulation):
		"""Scan nearby tiles for a trade route to sit and gank from"""
		bestMovePlot: Optional[HexPoint] = None

		# Now looking for BEST score
		bestValue = 0
		movementRange = unit.movesLeft()

		for plot in unit.location.areaWithRadius(movementRange):
			if plot == unit.location:
				continue

			tile = simulation.tileAt(plot)
			if tile is None:
				continue

			if not tile.isDiscoveredBy(self.player):
				continue

			if not unit.canReachAt(plot, movementRange, simulation):
				continue

			value = simulation.numberOfTradeRoutesAt(plot)

			if value > bestValue:
				bestMovePlot = plot
				bestValue = value

		return bestMovePlot

	def findBarbarianExploreTargetFor(self, unit, simulation):
		"""Scan nearby tiles for the best choice, borrowing code from the explore AI"""
		economicAI = self.player.economicAI

		bestValue = 0
		bestMovePlot: Optional[HexPoint] = None
		movementRange = unit.movesLeft()

		# Now looking for BEST score
		for plot in unit.location.areaWithRadius(movementRange):
			if plot == unit.location:
				continue

			tile = simulation.tileAt(plot)
			if tile is None:
				continue

			if not tile.isDiscoveredBy(self.player):
				continue

			if not unit.canReachAt(plot, movementRange, simulation):
				continue

			# Value them based on their explore value
			value = economicAI.scoreExplore(plot, self.player, unit.sight(), unit.domain(), simulation)

			# Add special value for popping up on hills or near enemy lands
			#if (pPlot->isAdjacentOwned())
			#	iValue += 100;
			if tile.hasOwner():
				value += 200

			# If still have no value, score equal to distance from my current plot
			if value == 0:
				value = unit.location.distance(plot)

			if value > bestValue:
				bestMovePlot = plot
				bestValue = value

		return bestMovePlot

	def unitProcessed(self, unit, markTacticalMap: bool = True, simulation=None):
		"""Remove a unit that we've allocated from list of units to move this turn"""
		if simulation is None:
			raise Exception('simulation must not be None')

		self.currentTurnUnits = list(filter(lambda u: not u == unit, self.currentTurnUnits))

		unit.setTurnProcessedTo(True)

		if markTacticalMap:
			map = simulation.tacticalAnalysisMap()

			if map.isBuild:
				cell = map.plots.values[unit.location.y][unit.location.x]
				cell.setFriendlyTurnEndTile(True)

		return

	def findUnitsWithinStrikingDistanceTowards(self, targetLocation: HexPoint, numTurnsAway: int, noRangedUnits: bool = False,
											   navalOnly: bool = False, mustMoveThrough: bool = False,
											   includeBlockedUnits: bool = False, willPillage: bool = False,
											   targetUndefended: bool = False, simulation=None) -> bool:
		"""Fills m_CurrentMoveUnits with all units within X turns of a target (returns TRUE if 1 or more found)"""
		rtnValue = False
		self.currentMoveUnits = []

		# Loop through all units available to tactical AI this turn
		for loopUnit in self.currentTurnUnits:
			if not navalOnly or loopUnit.domain() == UnitDomainType.sea:
				# don't use non-combat units
				if not loopUnit.canAttack():
					continue

				if loopUnit.isOutOfAttacks( simulation):
					continue

				#if not isCityTarget and loopUnit.cityAttackOnly():
				#  	continue

				if willPillage and not loopUnit.canPillageAt(targetLocation, simulation):
					continue

				# ** *Need to make this smarter and account for units that can move up on their targets and then make a ranged attack,
				# all in the same turn.** *
				if not noRangedUnits and not mustMoveThrough and loopUnit.canAttackRanged():
					# Are we in range?
					if loopUnit.location.distance(targetLocation) <= loopUnit.range():
						# Do we have LOS to the target?
						# if loopUnit.canEverRangeStrikeAt(pTarget->getX(), pTarget->getY())) {
						# Will we do any damage
						if self.isExpectedToDamageWithRangedAttack(loopUnit, targetLocation, simulation):
							# Want ranged units to attack first, so inflate this
							# Don't take damage from bombarding, so show as fully healthy
							attackStrength = 100 * loopUnit.rangedCombatStrengthAgainst(None, None, None, attacking=True, simulation=simulation)
							unit = TacticalUnit(loopUnit, attackStrength, healthPercent=100)
							self.currentMoveUnits.append(unit)
							rtnValue = True
				else:
					if loopUnit.canReachAt(targetLocation, numTurnsAway, simulation):
						attackStrength = 100 * loopUnit.rangedCombatStrengthAgainst(None, None, None, attacking=True, simulation=simulation)
						unit = TacticalUnit(loopUnit, attackStrength, healthPercent=loopUnit.healthPoints())
						self.currentMoveUnits.append(unit)
						rtnValue = True

		# Now sort them in the order we'd like them to attack
		self.currentMoveUnits.sort(key=lambda unit: unit.movesToTarget)  #(by: { $0!.movesToTarget < $1!.movesToTarget})

		return rtnValue

	def findCitiesWithinStrikingDistanceOf(self, point: HexPoint, simulation) -> bool:
		"""Fills m_CurrentMoveCities with all cities within bombard range of a target (returns TRUE if 1 or more found)"""
		rtnValue = False
		self.currentMoveCities = []

		# Loop through all of our cities
		for loopCity in simulation.citiesOf(self.player):
			if loopCity.canRangeStrikeAt(point) and not self.isCityInQueuedAttack(loopCity):
				cityTarget = TacticalCity(city=loopCity)
				self.currentMoveCities.append(cityTarget)
				rtnValue = True

		# Now sort them in the order we'd like them to attack
		self.currentMoveCities.sort()

		return rtnValue

	def isVeryHighPriorityCivilianTarget(self, target: TacticalTarget) -> bool:
		"""Is this civilian target of the highest priority?"""
		if target.unit is not None:
			if target.unit.hasTask(UnitTaskType.general):
				return True

		return False

	def isHighPriorityCivilianTarget(self, target: TacticalTarget, turn: int, numberOfCities: int) -> bool:
		"""Is this civilian target of high priority?"""
		if target.unit is None:
			return False

		returnValue = False

		if target.unit.civilianAttackPriority() == CivilianAttackPriorityType.high:
			returnValue = True
		elif target.unit.civilianAttackPriority() == CivilianAttackPriorityType.highEarlyGameOnly:
			if turn < 50:
				returnValue = True

		if returnValue == False and target.unit.task() == UnitTaskType.settle:
			if numberOfCities < 5:
				returnValue = True
			elif turn < 50:
				returnValue = True

		if returnValue == False and self.player.isBarbarian():
			# always high priority for barbs
			returnValue = True

		return returnValue

	def isMediumPriorityCivilianTarget(self, target: TacticalTarget, turn: int) -> bool:
		"""Is this civilian target of medium priority?"""
		unit = target.unit
		if unit is not None:
			# embarked civilians
			if unit.isEmbarked() and not unit.isCombatUnit():
				return True
			elif unit.task() == UnitTaskType.settle and turn >= 50:
				return True
			elif unit.task() == UnitTaskType.work and turn < 50:  # early game?
				return True

		return False

	def executeCivilianCapture(self, target: HexPoint, simulation):
		"""Capture an undefended civilian"""
		# Move first one to target
		currentMoveUnit = next(iter(self.currentMoveUnits), None)
		if currentMoveUnit is not None:
			unit = currentMoveUnit.unit
			if unit is not None:
				unit.pushMission(UnitMission(UnitMissionType.moveTo, buildType=None, target=target), simulation)
				unit.finishMoves()

				# Delete this unit from those we have to move
				self.unitProcessed(unit, simulation=simulation)

				unit.resetTacticalTarget()

		return

	def computeTotalExpectedDamage(self, target, targetPlot, simulation) -> int:
		"""Estimates the damage we can apply to a target"""
		rtnValue = 0

		# Loop through all units who can reach the target
		for currentMoveUnit in self.currentMoveUnits:
			attacker = currentMoveUnit.unit

			if attacker is None:
				continue

			# Is target a unit?
			if target.targetType == TacticalTargetType.highPriorityUnit or \
				target.targetType == TacticalTargetType.mediumPriorityUnit or \
				target.targetType == TacticalTargetType.lowPriorityUnit:

				defender = simulation.unitAt(targetPlot.point, UnitMapType.combat)
				if defender is not None:
					if attacker.canAttackRanged():
						result = Combat.predictRangedAttack(attacker, defender, simulation)
						expectedDamage = result.defenderDamage
						expectedSelfDamage = 0
					else:
						result = Combat.predictMeleeAttack(attacker, defender, simulation)
						expectedDamage = result.defenderDamage
						expectedSelfDamage = result.attackerDamage

					currentMoveUnit.expectedTargetDamage = expectedDamage
					currentMoveUnit.expectedSelfDamage = expectedSelfDamage

					rtnValue += expectedDamage

			elif target.targetType == TacticalTargetType.city:
				city = simulation.cityAt(targetPlot.point)

				if city is not None:
					if attacker.canAttackRanged():
						result = Combat.predictRangedAttack(attacker, city, simulation)
						expectedDamage = result.defenderDamage
						expectedSelfDamage = 0
					else:
						result = Combat.predictMeleeAttack(attacker, city, simulation)
						expectedDamage = result.defenderDamage
						expectedSelfDamage = result.attackerDamage

					currentMoveUnit.expectedTargetDamage = expectedDamage
					currentMoveUnit.expectedSelfDamage = expectedSelfDamage

					rtnValue += expectedDamage

		return rtnValue

	def executeMoveToTarget(self, point: HexPoint, garrisonIfPossible: bool, simulation):
		"""Find one unit to move to target, starting with high priority list"""
		# Start with high priority list
		for currentMoveHighPriorityUnit in self.currentMoveHighPriorityUnits:
			unit = currentMoveHighPriorityUnit.unit
			if unit is None:
				continue

			# Don't move high priority unit, if regular priority unit is closer
			firstCurrentUnit = next(iter(self.currentMoveUnits), None)
			if firstCurrentUnit is not None:
				if firstCurrentUnit.movesToTarget < currentMoveHighPriorityUnit.movesToTarget:
					break

			if unit.location == point and unit.canFortifyAt(point, simulation):
				unit.pushMission(UnitMission(UnitMissionType.fortify), simulation)
				unit.doFortify(simulation)
				self.unitProcessed(unit, simulation=simulation)
				return

			elif garrisonIfPossible and unit.location == point and unit.canGarrisonAt(point, simulation):
				unit.pushMission(UnitMission(UnitMissionType.garrison), simulation)
				unit.finishMoves()
				self.unitProcessed(unit, simulation=simulation)
				return

			elif currentMoveHighPriorityUnit.movesToTarget < sys.maxsize:
				unit.pushMission(UnitMission(UnitMissionType.moveTo, target=point), simulation)
				unit.finishMoves()
				self.unitProcessed(unit, simulation=simulation)
				return

		# Then regular priority
		for currentMoveUnit in self.currentMoveUnits:
			unit = currentMoveUnit.unit

			if unit is None:
				continue

			if unit.location == point and unit.canFortifyAt(unit.location, simulation):
				unit.pushMission(UnitMission(UnitMissionType.fortify), simulation)
				unit.doFortify(simulation)
				self.unitProcessed(unit, simulation=simulation)
				return

			elif currentMoveUnit.movesToTarget < sys.maxsize:
				unit.pushMission(UnitMission(UnitMissionType.moveTo, target=point), simulation)
				unit.finishMoves()
				self.unitProcessed(unit, simulation=simulation)
				return

		return

	def plotSingleHexOperationMoves(self, operation, simulation):
		"""Move a single stack (civilian plus escort) to its destination"""
		if operation is None:
			return

		# Simplification - assume only 1 army per operation now
		army = operation.army
		if army is None:
			return

		civilian = army.unitAt(0)
		if civilian is None:
			return

		# ESCORT AND CIVILIAN MEETING UP
		if army.state == ArmyState.waitingForUnitsToReinforce or army.state == ArmyState.waitingForUnitsToCatchUp:
			escort = army.unitAt(1)
			if escort is None:
				# Escort died or was poached for other tactical action, operation will clean itself up when call CheckOnTarget()
				return

			if escort.processedInTurn():
				return

			# Check to make sure escort can get to civilian
			if escort.pathTowards(civilian.location, options=[], simulation=simulation) is not None:
				# He can, so have civilian remain in place
				self.executeMoveUnitToPlot(civilian, civilian.location, simulation=simulation)

				if army.numberOfSlotsFilled() > 1:
					# Move escort over
					self.executeMoveUnitToPlot(escort, civilian.location, simulation=simulation)

					logging.debug(f"=== Operation: Moving escorting {escort.unitType} to civilian for operation, Civilian at {civilian.location}, {escort.location}")
			else:
				# Find a new place to meet up, look at all hexes adjacent to civilian
				for neighbor in civilian.location.neighbors():
					neighborTile = simulation.tileAt(neighbor)

					if neighborTile is None:
						continue

					if escort.canEnterTerrain(neighborTile) and escort.canEnterTerritory(self.player, ignoreRightOfPassage=False, isDeclareWarMove=False):
						if not simulation.areUnitsAt(neighbor):
							if escort.pathTowards(neighbor, options=[], simulation=simulation) is not None and \
								civilian.pathTowards(neighbor, options=[], simulation=simulation) is not None:
								self.executeMoveUnitToPlot(escort, neighbor, simulation=simulation)
								self.executeMoveUnitToPlot(civilian, neighbor, simulation=simulation)

								logging.debug(f"=== Operation: Moving escorting {escort.unitType} to open hex, Open {neighbor}, {escort.location}")
								logging.debug(f"=== Operation: Moving {civilian.unitType} to open hex, Open {neighbor}, {civilian.location}")

								return

				# Didn't find an alternative, must abort operation
				operation.retargetCivilian(civilian, army, simulation)
				civilian.finishMoves()
				escort.finishMoves()

				logging.debug("=== Operation: Retargeting civilian escort operation. No empty tile adjacent to civilian to meet.")
		else:
			# MOVING TO TARGET
			# If we're not there yet, we have work to do (otherwise CheckOnTarget() will finish operation for us)
			if civilian.location != operation.targetPosition:
				# Look at where we'd move this turn taking units into consideration
				iFlags = 0
				# if army.numberOfSlotsFilled() > 1:
				# iFlags = MOVE_UNITS_IGNORE_DANGER;

				# Handle case of no path found at all for civilian
				path = civilian.pathTowards(operation.targetPosition, options=[], simulation=simulation)
				if path is not None:
					civilianMove = firstOrNone(path.points())

					if civilianMove is None:
						return

					if civilianMove == civilian.location:
						civilianMove = secondOrNone(path.points())

					if civilianMove is None:
						return

					saveMoves = civilianMove == operation.targetPosition

					if army.numberOfSlotsFilled() == 1:
						self.executeMoveUnitToPlot(civilian, point=civilianMove, saveMoves=saveMoves, simulation=simulation)

						# Update army's current location
						army.position = civilianMove

						logging.debug(f"=== Operation: Moving {civilian.unitType} without escort to target, {civilian.location}")
					else:
						escort = army.unitAt(1)
						if escort is None:
							return

						# See if escort can move to the same location in one turn
						if escort.turnsToReach(civilianMove, simulation) <= 1:
							self.executeMoveUnitToPlot(civilian, point=civilianMove, saveMoves=saveMoves, simulation=simulation)
							self.executeMoveUnitToPlot(escort, point=civilianMove, simulation=simulation)

							# Update army's current location
							army.position = civilianMove

							logging.debug(f"=== Operation: Moving {civilian.unitType} to target, {civilian.location}")
							logging.debug(f"=== Operation: Moving escorting {escort.unitType} to target, {escort.location}")
						else:
							tacticalMap = simulation.tacticalAnalysisMap()
							cell = tacticalMap.plots.values[civilianMove.y][civilianMove.x]

							blockingUnit = simulation.unitAt(civilianMove, UnitMapType.combat)

							# See if friendly blocking unit is ending the turn there, or if no blocking unit
							# (which indicates this is somewhere civilian can move that escort can't --
							# like minor civ territory), then find a new path based on moving the escort
							if cell.isFriendlyTurnEndTile() or blockingUnit is None:
								path = escort.pathTowards(operation.targetPosition, options=[], simulation=simulation)

								if path is not None:
									escortMove = firstOrNone(path.points())

									if escortMove is None:
										return

									if escortMove == escort.location:
										escortMove = secondOrNone(path.points())

									if escortMove is None:
										return

									saveMoves = escortMove == operation.targetPosition

									# See if civilian can move to the same location in one turn
									if civilian.turnsToReach(escortMove, simulation) <= 1:
										self.executeMoveUnitToPlot(escort, escortMove, simulation=simulation)
										self.executeMoveUnitToPlot(civilian, escortMove, saveMoves, simulation=simulation)

										# Update army's current location
										army.position = escortMove

										logging.debug(f"=== Operation: Moving escorting {escort.unitType} to target, {escort.location}")
										logging.debug(f"=== Operation: Moving {civilian.unitType} to target, {civilian.location}")
									else:
										# Didn't find an alternative, retarget operation
										operation.retargetCivilian(civilian, army, simulation)
										civilian.finishMoves()
										escort.finishMoves()

										logging.debug("=== Operation: Retargeting civilian escort operation. Too many blocking units.")
								else:
									operation.retargetCivilian(civilian, army, simulation)
									civilian.finishMoves()
									escort.finishMoves()

									logging.debug(f"=== Operation: Retargeting civilian escort operation (path lost to target), {operation.targetPosition}")
							else:
								# Looks like we should be able to move the blocking unit out of the way
								if self.executeMoveOfBlockingUnit(blockingUnit, simulation):
									self.executeMoveUnitToPlot(escort, civilianMove, simulation=simulation)
									self.executeMoveUnitToPlot(civilian, civilianMove, saveMoves, simulation=simulation)

									logging.debug(f"=== Operation: Moving escorting {escort.unitType} to target, {escort.location}")
									logging.debug(f"=== Operation: Moving {civilian.unitType} to target, {civilian.location}")
								else:
									# Didn't find an alternative, try retargeting operation
									operation.retargetCivilian(civilian, army, simulation)
									civilian.finishMoves()
									escort.finishMoves()

									logging.debug("=== Operation: Retargeting civilian escort operation. Could not move blocking unit.")
				else:
					operation.retargetCivilian(civilian, army, simulation)
					civilian.finishMoves()

					escort = army.unitAt(1)

					if escort is not None:
						escort.finishMoves()

					logging.debug(f"=== Operation: Retargeting civilian escort operation (path lost to target), {operation.targetPosition}")

		return

	def plotEnemyTerritoryOperationMoves(self, operation, simulation):
		"""Move a large army to its destination against an enemy target"""
		# Simplification - assume only 1 army per operation now
		thisArmy = operation.army

		if thisArmy is None:
			return

		self.operationUnits = []
		self.generalsToMove = []
		self.paratroopersToMove = []
		thisArmy.updateCheckpointTurns(simulation)

		# RECRUITING
		if thisArmy.state == ArmyState.waitingForUnitsToReinforce:
			# If no estimate for when recruiting will end, let the rest of the AI use these units
			if thisArmy.turnAtNextCheckpoint() == ArmyFormationSlotConstants.unknownTurnAtCheckpoint:
				return
			else:
				for index, slotEntry in enumerate(thisArmy.formation.slots()):
					# See if we are just able to get to muster point in time.If so, time for us to head over there
					unit = thisArmy.unitAt(index)
					if unit is not None:
						if not unit.processedInTurn():
							# Great general?
							if unit.isGreatGeneral() or unit.isGreatAdmiral():
								if unit.moves() > 0:
									self.generalsToMove.append(OperationUnit(unit, UnitFormationPosition.civilianSupport))
							else:
								formationSlotEntry = slotEntry

								# Continue moving to target
								if slotEntry.hasStartedOnOperation():
									self.moveWithFormation(unit, formationSlotEntry.position)
								else:
									# See if we are just able to get to muster point in time. If so, time for us to head over there
									turns = unit.turnsToReach(operation.musterPosition, simulation)
									if turns + simulation.currentTurn >= thisArmy.turnAtNextCheckpoint():
										armySlotEntry = thisArmy.formationEntries[index]
										armySlotEntry.setStartedOnOperation(True)
										self.moveWithFormation(unit, formationSlotEntry.position)

				self.executeGatherMoves(thisArmy, simulation)
		elif thisArmy.state == ArmyState.waitingForUnitsToCatchUp:  # GATHERING FORCES
			self.clearEnemiesNearArmy(thisArmy, simulation)

			# Request moves for all units
			for index, slotEntry in enumerate(thisArmy.formation.slots()):
				unit = thisArmy.unitAt(index)
				if unit is not None:
					if not unit.processedInTurn():
						# Great general or admiral?
						if unit.isGreatGeneral() or unit.isGreatAdmiral():
							if unit.moves() > 0:
								self.generalsToMove.append(OperationUnit(unit, UnitFormationPosition.civilianSupport))
						else:
							armySlotEntry = thisArmy.formationEntries[index]
							armySlotEntry.setStartedOnOperation(True)
							self.moveWithFormation(unit, slotEntry.position)

			self.executeGatherMoves(thisArmy, simulation)

		elif thisArmy.state == ArmyState.movingToDestination:  # MOVING TO TARGET
			# Update army's current location
			closestCurrentCenterOfMassOnPath: HexPoint = constants.invalidHexPoint

			thisTurnTarget = operation.computeCenterOfMassForTurn(closestCurrentCenterOfMassOnPath, simulation)

			if thisTurnTarget is None:
				operation.state = OperationStateType.aborted
				operation.stateReason = OperationStateReason.lostPath
				return

			thisArmy.position = thisTurnTarget
			self.clearEnemiesNearArmy(thisArmy, simulation)

			# Request moves for all units
			for index, slotEntry in enumerate(thisArmy.formation.slots()):
				unit = thisArmy.unitAt(index)
				if unit is not None:
					if not unit.processedInTurn():
						# Great general or admiral?
						if unit.isGreatGeneral() or unit.isGreatAdmiral():
							if unit.moves() > 0:
								self.generalsToMove.append(OperationUnit(unit, UnitFormationPosition.civilianSupport))
						else:
							self.moveWithFormation(unit, slotEntry.position)


			self.executeFormationMoves(thisArmy, closestCurrentCenterOfMassOnPath, simulation)

		if len(self.paratroopersToMove) > 0:
			# MoveParatroopers(pThisArmy);
			pass

		if len(self.generalsToMove) > 0:
			self.moveGreatGeneral(thisArmy, simulation)

		return

	def plotFreeformNavalOperationMoves(self, operation, simulation):
		""" Move a naval force that is roaming for targets"""
		# Simplification - assume only 1 army per operation now
		thisArmy = operation.army

		if thisArmy is None:
			return

		self.operationUnits = []
		thisArmy.updateCheckpointTurns(simulation)

		# RECRUITING
		if thisArmy.state == ArmyState.waitingForUnitsToReinforce:
			# If no estimate for when recruiting will end, let the rest of the AI use these units
			if thisArmy.turnAtNextCheckpoint() == ArmyFormationSlotConstants.unknownTurnAtCheckpoint:
				return
			else:
				for index, slotEntry in enumerate(thisArmy.formation.slots()):
					# See if we are just able to get to muster point in time.If so, time for us to head over there
					unit = thisArmy.unitAt(index)
					if unit is not None and not unit.processedInTurn():
						# Continue moving to target
						if slotEntry.hasStartedOnOperation():
							self.moveWithFormation(unit, slotEntry.position)
						else:
							# See if we are just able to get to muster point in time.If so, time for us to head over there
							turns = unit.turnsToReach(operation.musterPosition, simulation)
							if turns + simulation.currentTurn >= thisArmy.turnAtNextCheckpoint():
								slotEntry.setStartedOnOperation(True)
								self.moveWithFormation(unit, slotEntry.position)

				self.executeNavalFormationMoves(thisArmy, operation.musterPosition, simulation)

		# GATHERING FORCES
		elif thisArmy.state == ArmyState.waitingForUnitsToCatchUp:
			# Get them moving to target without delay
			operation.armyInPosition(thisArmy)
			self.executeFleetMoveToTarget(thisArmy, operation.targetPlot, simulation)

		# MOVING TO TARGET
		elif thisArmy.state == ArmyState.movingToDestination:
			# Get them moving to target without delay
			operation.armyInPosition(thisArmy)
			self.executeFleetMoveToTarget(thisArmy, operation.targetPlot, simulation)

		return

	def executeSafeBombardsOn(self, target: TacticalTarget, simulation) -> bool:
		"""Bombard enemy units from plots they can't reach (return True if some attack made)"""
		firstAttackerCity = None
		firstAttackerUnit = None
		firstAttackCity: bool = False
		requiredDamage: int = 0

		targetPlot = simulation.tileAt(target.target)

		if targetPlot is None:
			raise Exception("can get targetPlot")

		if self.plotAlreadyTargeted(target.target) != -1:
			return False

		# Get required damage on unit target
		defender = simulation.visibleEnemyAt(target.target, self.player)
		if defender is not None:
			requiredDamage = defender.healthPoints()

			# If this is a unit target we might also be able to hit it with a city
			cityCanAttack = self.findCitiesWithinStrikingDistanceOf(target.target, simulation)
			if cityCanAttack:
				self.computeTotalExpectedBombardDamageAgainst(defender, simulation)

				# Start by applying damage from city bombards
				for currentMoveCity in self.currentMoveCities:
					city = currentMoveCity.city

					if city is not None:
						if self.queueCityAttack(city, target=target, ranged=True):
							firstAttackerCity = city
							firstAttackCity = True

						# Subtract off expected damage
						requiredDamage -= currentMoveCity.expectedTargetDamage if currentMoveCity.expectedTargetDamage is not None else 0
		else:
			# Get required damage on city target
			city = simulation.cityAt(target.target)
			if city is not None:
				requiredDamage = city.maxHealthPoints() - city.healthPoints()

				# Can't eliminate a city with ranged fire, so don't target one if that is low on health
				if requiredDamage <= 1:
					return False

		# Need to keep hitting target?
		if requiredDamage <= 0:
			return False

		# For each of our ranged units, see if they are already in a plot that can bombard that can't be attacked.
		# If so, bombs away!
		self.currentMoveUnits = []

		for currentTurnUnit in self.currentTurnUnits:
			unit = currentTurnUnit

			if unit is None:
				continue

			if unit.canAttackRanged() and not unit.isOutOfAttacks(simulation):
				cell = simulation.tacticalAnalysisMap().plots.values[unit.location.y][unit.location.x]

				if cell.isWithinRangeOfTarget() and not cell.isSubjectToAttack() and self.isExpectedToDamageWithRangedAttack(unit, target.target, simulation):
					if unit.canSetUpForRangedAttack():
						unit.setUpForRangedAttackTo(True)

						logging.debug(f"Set up {unit.unitType} for ranged attack")

					if unit.canMove() and unit.canRangeStrikeAt(target.target, needWar=True, noncombatAllowed=True, simulation=simulation):
						logging.debug(f"Making a safe bombard (no move) with {unit.name()}, Target {target.target}, At {unit.location}")

						if self.queueUnitAttack(unit, target, ranged=True):
							firstAttackerUnit = unit

						# Save off ID so can be cleared from list to process for turn
						self.currentMoveUnits.append(TacticalUnit(unit))

		# Clear out the units we just processed from the list for this turn
		for currentMoveUnit in self.currentMoveUnits:
			self.unitProcessed(currentMoveUnit.unit, simulation=simulation)

		# For each plot that we can bombard from that the enemy can't attack, try and move a ranged unit there.
		# If so, make that move and mark that tile as blocked with our unit.If unit has movement left, queue up an attack

		for turnsToReach in range(0, 2):
			friendlyRange = simulation.tacticalAnalysisMap().bestFriendlyRange()

			for dx in range(-friendlyRange, friendlyRange):
				for dy in range(-friendlyRange, friendlyRange):
					loopPoint = HexPoint(target.target.x + dx, target.target.y + dy)
					loopPlot = simulation.tileAt(loopPoint)

					if loopPlot is None:
						continue

					distance = target.target.distance(loopPoint)

					if 0 < distance <= friendlyRange:
						cell = simulation.tacticalAnalysisMap().plots.values[loopPoint.y][loopPoint.x]

						if cell.isRevealed() and cell.canUseForOperationGathering():
							if cell.isWithinRangeOfTarget() and not cell.isSubjectToAttack():
								haveLightOfSight = loopPlot.canSeeTile(targetPlot, self.player, radius=friendlyRange, hasSentry=False, simulation=simulation)

								if self.findClosestUnitTowards(
									target=loopPlot,
									numTurnsAway=turnsToReach,
									mustHaveHalfHP=False,
									mustBeRangedUnit=True,
									rangeRequired=distance,
									needsIgnoreLineOfSight=not haveLightOfSight,
									mustBeMeleeUnit=False,
									ignoreUnits=True,
									rangedAttackTarget=targetPlot,
									simulation=simulation
								):
									if len(self.currentMoveUnits) > 0:
										unit = self.currentMoveUnits[0].unit

										if unit is not None:
											# Check for presence of unmovable friendly units
											blockingUnit = simulation.unitAt(loopPoint, UnitMapType.combat)
											if blockingUnit is None or self.executeMoveOfBlockingUnit(blockingUnit, simulation):
												unit.pushMission(UnitMission(UnitMissionType.moveTo, target=loopPoint), simulation)

												logging.debug(f"Moving closer for safe bombard with {unit.name()}, Target {target.target}, Bombard From {loopPoint}, Now At {unit.location}")

												self.unitProcessed(unit, simulation=simulation)

												if unit.canSetUpForRangedAttackAt(unit.location):
													unit.setUpForRangedAttackTo(True)
													logging.debug(f"Set up {unit.name()} for ranged attack")

												if unit.canMove() and not unit.isOutOfAttacks(simulation) and unit.canRangeStrikeAt(target.target, needWar=False, noncombatAllowed=True, simulation=simulation):
													logging.debug(f"Making a safe bombard (half move) with {unit.name()}, Target {target.target}, At {unit.location}")

													if self.queueUnitAttack(unit, target, ranged=True):
														firstAttackerUnit = unit

		# Launch the initial attack plotted
		city = firstAttackerCity
		unit = firstAttackerUnit
		if city is not None:
			self.launchCityAttack(city, target, firstAttack=True, ranged=True, simulation=simulation)
			return True
		elif unit is not None:
			self.launchUnitAttack(unit, target, firstAttack=True, ranged=True, simulation=simulation)
			return True

		return False

	def unitTargets(self) -> [TacticalTarget]:
		resultList: [TacticalTarget] = []

		for target in self.allTargets:
			if target.targetType == TacticalTargetType.lowPriorityUnit or \
				target.targetType == TacticalTargetType.mediumPriorityUnit or \
				target.targetType == TacticalTargetType.highPriorityUnit:
				resultList.append(target)

		return resultList

	def executeGuardBarbarianCamp(self, simulation):
		# unit should stay
		for currentMoveUnitRef in self.currentMoveUnits:
			currentMoveUnit = currentMoveUnitRef.unit

			if currentMoveUnit is None:
				continue

			currentMoveUnit.finishMoves()
			self.unitProcessed(currentMoveUnit, currentMoveUnit.isCombatUnit(), simulation=simulation)

		return

	def executeRepositionMoves(self, simulation):
		"""Execute moving units to a better location"""
		for currentMoveUnitRef in self.currentMoveUnits:
			unit = currentMoveUnitRef.unit

			# LAND MOVES
			if unit.domain() == UnitDomainType.land:
				bestPlot = self.findNearbyTargetFor(unit, radius=TacticalAI.repositionRange, simulation=simulation)
				if bestPlot is not None:
					if self.moveToEmptySpaceNearTarget(unit, bestPlot, unit.domain() == UnitDomainType.land, simulation):
						unit.finishMoves()
						self.unitProcessed(unit, markTacticalMap=unit.isCombatUnit(), simulation=simulation)

						logging.debug(f"{unit.name()} moved to empty space near target, {bestPlot}, Current {unit.location}")

		return

	def executeMovesToSafestPlot(self, simulation):
		"""Moves units to the hex with the lowest danger"""
		dangerPlotsAI = self.player.dangerPlotsAI

		for currentUnit in self.currentTurnUnits:
			radius = currentUnit.moves()

			lowestDanger: float = 10000000000.0
			bestPlot: Optional[HexPoint] = None

			resultHasZeroDangerMove: bool = False
			resultInTerritory: bool = False
			resultInCity: bool = False
			resultInCover: bool = False

			# For each plot within movement range of the fleeing unit
			for neighbor in currentUnit.location.areaWithRadius(radius):
				if not simulation.valid(neighbor):
					continue

				# Can't be a plot with another player's unit in it or another of our unit of same type
				otherUnit = simulation.unitAt(neighbor, UnitMapType.combat)
				if otherUnit is not None:
					if otherUnit.player == currentUnit.player:
						continue
					elif currentUnit.hasSameType(otherUnit):
						continue

				if not currentUnit.canReachAt(neighbor, 1, simulation):
					continue

				# prefer being in a city with the lowest danger value
				# prefer being in a plot with no danger value
				# prefer being under a unit with the lowest danger value
				# prefer being in your own territory with the lowest danger value
				# prefer the lowest danger value
				danger = dangerPlotsAI.dangerAt(neighbor)
				isZeroDanger = danger <= 0.0
				city = simulation.cityAt(neighbor)
				isInCity = city.player == self.player if city is not None else False
				unit = simulation.unitAt(neighbor, UnitMapType.combat)
				isInCover = unit is not None
				tile = simulation.tileAt(neighbor)
				isInTerritory = tile.owner() == self.player if tile is not None and tile.hasOwner() else False

				updateBestValue = False

				if isInCity:
					if not resultInCity or danger < lowestDanger:
						updateBestValue = True
				elif isZeroDanger:
					if not resultInCity:
						if resultHasZeroDangerMove:
							if isInTerritory and not resultInTerritory:
								updateBestValue = True
						else:
							updateBestValue = True
				elif isInCover:
					if not resultInCity and not resultHasZeroDangerMove:
						if not resultInCover or danger < lowestDanger:
							updateBestValue = True
				elif isInTerritory:
					if not resultInCity and not resultInCover and not resultHasZeroDangerMove:
						if not resultInTerritory or danger < lowestDanger:
							updateBestValue = True
				elif not resultInCity and not resultInCover and not resultInTerritory and not resultHasZeroDangerMove:
					# if we have no good home, head to the lowest danger value
					if danger < lowestDanger:
						updateBestValue = True

				if updateBestValue:
					bestPlot = neighbor
					lowestDanger = danger

					resultInTerritory = isInTerritory
					resultInCity = isInCity
					resultInCover = isInCover
					resultHasZeroDangerMove = isZeroDanger

			if bestPlot is not None:
				# Move to the lowest danger value found
				currentUnit.pushMission(UnitMission(UnitMissionType.moveTo, target=bestPlot), simulation)  # FIXME:, .ignoreDanger
				currentUnit.finishMoves()
				self.unitProcessed(currentUnit, simulation=simulation)

				logging.debug(f"Moving {currentUnit} to safety, {bestPlot}")

		return

	def plotAlreadyTargeted(self, point: HexPoint) -> int:
		"""Do we already have a queued attack running on this plot? Return series ID if yes, -1 if no."""
		if len(self.queuedAttacks) > 0:
			for queuedAttack in self.queuedAttacks:
				if point != queuedAttack.target.target:
					continue

				return queuedAttack.seriesId

		return -1

	def isCityInQueuedAttack(self, city) -> bool:
		"""Is this unit waiting to get its turn to attack?"""
		if len(self.queuedAttacks) > 0:
			for queuedAttack in self.queuedAttacks:
				if queuedAttack.cityAttack and queuedAttack.attackerCity.location == city.location:
					return True

		return False

	def queueUnitAttack(self, unit, target: Optional[TacticalTarget], ranged: bool) -> bool:
		"""Queue up the attack - return TRUE if first attack on this target"""
		rtnValue = True

		# Can we find this target in the queue, if so what is its series ID
		queuedAttack = self.isAlreadyTargeted(target.target)
		if queuedAttack is not None:
			seriesId = queuedAttack.seriesId
			rtnValue = False
		else:
			self.currentSeriesId += 1
			seriesId = self.currentSeriesId

		attack = QueuedAttack()
		attack.attackerUnit = unit
		attack.target = target
		attack.ranged = ranged
		attack.cityAttack = False
		attack.seriesId = seriesId
		self.queuedAttacks.append(attack)

		logging.debug(f"Queued attack with {unit.name()}, To {target.target}, From {unit.location}")

		return rtnValue

	def executeMoveUnitToPlot(self, unit, point: HexPoint, saveMoves: bool = False, simulation=None):
		"""Move unit to protect a specific tile (retrieve unit from first entry in m_CurrentMoveUnits)"""
		if simulation is None:
			raise Exception('simulation must not be None')

		# Unit already at target plot?
		if point == unit.location:
			# Fortify if possible
			if unit.canFortifyAt(point, simulation):
				unit.pushMission(UnitMission(UnitMissionType.fortify), simulation)
				# unit.fort ->SetFortifiedThisTurn(True);
			else:
				unit.pushMission(UnitMission(UnitMissionType.skip), simulation)
				if not saveMoves:
					unit.finishMoves()
		else:
			unit.pushMission(UnitMission(UnitMissionType.moveTo, target=point), simulation)
			if not saveMoves:
				unit.finishMoves()

		self.unitProcessed(unit, markTacticalMap=unit.isCombatUnit(), simulation=simulation)

	def executeMoveToPlot(self, point: HexPoint, saveMoves: bool, simulation):
		"""Move unit to protect a specific tile (retrieve unit from first entry in m_CurrentMoveUnits)"""
		# Move first one to target
		firstCurrentModeUnit = next(iter(self.currentMoveUnits), None)
		if firstCurrentModeUnit is not None:
			unit = firstCurrentModeUnit.unit
			if unit is not None:
				self.executeMoveUnitToPlot(unit, point, saveMoves=saveMoves, simulation=simulation)

		return

	def computeTotalExpectedBombardDamageAgainst(self, defender, simulation) -> int:
		"""Estimates the bombard damage we can apply to a target"""
		rtnValue = 0
		expectedDamage = 0

		# Now loop through all the cities that can bombard it
		for attackingCityRef in self.currentMoveCities:
			attackingCity = attackingCityRef.city
			if attackingCity is None:
				continue

			result = Combat.predictRangedAttack(attackingCity, defender, simulation)

			expectedDamage = result.defenderDamage
			attackingCityRef.expectedTargetDamage = expectedDamage
			rtnValue += expectedDamage

		return rtnValue

	def isExpectedToDamageWithRangedAttack(self, attacker, targetLocation: HexPoint, simulation) -> bool:
		expectedDamage = 0

		city = simulation.cityAt(targetLocation)
		defender = simulation.unitAt(targetLocation, UnitMapType.combat)

		if city is not None:
			result = Combat.predictRangedAttack(attacker, city, simulation)
			expectedDamage = result.defenderDamage
		elif defender is not None:
			result = Combat.predictRangedAttack(attacker, defender, simulation)
			expectedDamage = result.defenderDamage

		return expectedDamage > 0

	def deleteTemporaryZoneAt(self, location: HexPoint):
		"""Remove a temporary dominance zone we no longer need to track"""
		self.temporaryZones = list(filter(lambda zone: zone.location != location, self.temporaryZones))
		return

	def executeAttack(self, target: TacticalTarget, tile, inflictWhatWeTake: bool, mustSurviveAttack: bool, simulation):
		"""Attack a defended space"""
		firstAttacker = None
		firstCity = None
		firstAttackRanged: bool = False
		firstAttackCity: bool = False

		if self.isAlreadyTargeted(target.target) is not None:
			return

		# How much damage do we still need to inflict?
		damageRemaining = (target.damage * 150) / 100

		# Start by applying damage from city bombards
		for currentMoveCity in self.currentMoveCities:
			if damageRemaining <= 0:
				break

			if currentMoveCity.city is not None:
				if self.queueCityAttack(currentMoveCity.city, target, ranged=True):
					firstCity = currentMoveCity.city
					firstAttackRanged = True
					firstAttackCity = True

				# Subtract off expected damage
				damageRemaining -= currentMoveCity.expectedTargetDamage

		# First loop is ranged units only
		for currentMoveUnit in self.currentMoveUnits:
			if damageRemaining <= 0:
				break

			if not inflictWhatWeTake or currentMoveUnit.expectedTargetDamage >= currentMoveUnit.expectedSelfDamage:
				unit = currentMoveUnit.unit
				if unit is not None:
					if unit.moves() > 0:
						if not mustSurviveAttack or ((currentMoveUnit.expectedSelfDamage + unit.damage()) < 100):  # int(Unit.maxHealth)):
							# Are we a ranged unit
							if unit.canAttackRanged():
								# Are we in range?
								dist = unit.location.distance(target.target)
								if dist <= unit.range():
									# Do we have LOS line of sight to the target?
									if unit.canReachAt(target.target, dist, simulation):
										# Do we need to set up to make a ranged attack?
										if unit.canSetUpForRangedAttackAt(None):
											unit.setUpForRangedAttackTo(True)
											logging.debug(f'Set up {unit.name()} for ranged attack')

											if not unit.canMove():
												unit.resetTacticalTarget()
												self.unitProcessed(unit, simulation=simulation)

										# Can we hit it with a ranged attack?  If so, that gets first priority
										# , noncombatAllowed=False
										if unit.canMove() and unit.canRangeStrikeAt(target.target, needWar=True, noncombatAllowed=True, simulation=simulation):
											# Queue up this attack
											if self.queueUnitAttack(unit, target, ranged=True):
												firstAttacker = unit
												firstAttackRanged = True

											unit.resetTacticalMove()
											self.unitProcessed(unit, simulation=simulation)

											# Subtract off expected damage
											damageRemaining -= currentMoveUnit.expectedTargetDamage
						else:
							logging.debug("Not attacking with unit. We'll destroy ourself.")
			else:
				logging.debug("Not attacking with unit. Can't generate a good damage ratio.")

		# If target is city, want to get in one melee attack, so set damage remaining to 1
		if target.targetType == TacticalTargetType.city and damageRemaining < 1:
			damageRemaining = 1

		# Second loop are only melee units
		for currentMoveUnit in self.currentMoveUnits:
			if damageRemaining <= 0:
				break

			if not inflictWhatWeTake or currentMoveUnit.expectedTargetDamage >= currentMoveUnit.expectedSelfDamage:
				unit = currentMoveUnit.unit
				if unit is not None:
					if unit.moves() > 0 and (not mustSurviveAttack or ((currentMoveUnit.expectedSelfDamage + unit.damage()) < 100)):  # Int(Unit.maxHealth)
						# Are we a melee unit
						if not unit.canAttackRanged():
							# Queue up this attack
							if self.queueUnitAttack(unit, target, ranged=False):
								firstAttacker = unit

							unit.resetTacticalMove()
							self.unitProcessed(unit, markTacticalMap=False, simulation=simulation)

							# Subtract off expected damage
							damageRemaining -= currentMoveUnit.expectedTargetDamage
					else:
						logging.debug("Not attacking with unit. We'll destroy ourself.")
			else:
				logging.debug("Not attacking with unit. Can't generate a good damage ratio.")

		# Start up first attack
		if firstAttackCity and firstCity is not None:
			self.launchCityAttack(firstCity, target, firstAttack=True, ranged=firstAttackRanged, simulation=simulation)
		elif not firstAttackCity and firstAttacker is not None:
			self.launchUnitAttack(firstAttacker, target, firstAttack=True, ranged=firstAttackRanged, simulation=simulation)

	def launchUnitAttack(self, unit, target: TacticalTarget, firstAttack: bool, ranged: bool, simulation):
		"""Pushes the mission to launch an attack and logs this activity"""
		rangedStr = "ranged " if ranged else ""
		if firstAttack:
			logging.debug(f"Made initial {rangedStr}attack with {unit.name()} towards {target.target}")
		else:
			logging.debug(f"Made follow-on {rangedStr}attack with {unit.name()} towards {target.target}")

		sendAttack = unit.moves() > 0 and not unit.isOutOfAttacks(simulation)
		if sendAttack:
			if ranged and unit.domain() != UnitDomainType.air:
				# Air attack is ranged, but it goes through the 'move to' mission.
				unit.pushMission(UnitMission(UnitMissionType.rangedAttack, target=target.target), simulation)
		# else if (pUnit->canNuke(NULL))  # NUKE tactical attack (ouch)
		# pUnit->PushMission(CvTypes::getMISSION_NUKE(), pTarget->GetTargetX(), pTarget->GetTargetY());
		else:
			unit.pushMission(UnitMission(UnitMissionType.moveTo, target=target.target), simulation)

		# Make sure we did make an attack, if not we should take out this unit from the queue
		if not sendAttack or not unit.canMove():  # / * and !pUnit->isFighting() * / {
			unit.setTurnProcessedTo(False)
			self.combatResolvedFor(unit, victorious=False, simulation=simulation)

		return

	def combatResolvedFor(self, unit, victorious: bool, simulation):
		seriesId = 0
		foundIt = False

		if len(self.queuedAttacks) > 0:
			# Find first attack with this unit/city
			index: int = 0
			for nextToErase in self.queuedAttacks:
				if unit == nextToErase.attackerUnit:
					seriesId = nextToErase.seriesId
					foundIt = True
					break

				index += 1

			# Couldn't find it ... could have been an accidental attack moving to deploy near a target
			# So safe to ignore these
			if not foundIt:
				return

			# If this attacker gets multiple attacks, release him to be processed again
			if unit.canMoveAfterAttacking() and unit.moves() > 0:
				unit.setTurnProcessedTo(False)

			# If victorious, dump follow - up attacks
			if victorious:
				first = True
				toSkip: int = index
				index = 0

				for nextToErase in self.queuedAttacks:
					if index < toSkip:
						index += 1
						continue

					if nextToErase.seriesId != seriesId:
						break

					# Only the first unit being erased is done for the turn
					if not first and not nextToErase.cityAttack:
						nextToErase.attackerUnit.setTurnProcessedTo(False)

					first = False
					index += 1

				self.queuedAttacks = list(filter(lambda s: s != seriesId, self.queuedAttacks))
			else:
				# Otherwise look for a follow - up attack
				if index + 1 < len(self.queuedAttacks):
					nextInList = self.queuedAttacks[index + 1]
					if nextInList.seriesId == seriesId:
						# Calling LaunchAttack can be recursive if the launched combat is resolved immediately.
						# We'll make a copy of the iterators contents before erasing. This is not technically needed because
						# the current queue is a std::list and iterators don't invalidate on erase, but we'll be safe, in case
						# the container type changes.
						newCityTarget = nextInList.attackerCity
						newUnitTarget = nextInList.attackerUnit
						newTarget = nextInList.target
						newRanged = nextInList.ranged

						del self.queuedAttacks[index + 1]

						if nextInList.cityAttack:
							self.launchCityAttack(newCityTarget, newTarget, firstAttack=False, ranged=newRanged, simulation=simulation)
						else:
							self.launchUnitAttack(newUnitTarget, newTarget, firstAttack=False, ranged=newRanged, simulation=simulation)
					else:
						del self.queuedAttacks[index + 1]

		return

	def clearEnemiesNearArmy(self, army, simulation):
		"""Queues up attacks on enemy units on or adjacent to army's desired center"""
		radius: int = 1
		enemyNear: bool = False

		tacticalAnalysisMap = simulation.tacticalAnalysisMap()

		# Loop through all appropriate targets to see if any is of concern
		for target in self.allTargets:
			# Is the target of an appropriate type?
			if target.targetType == TacticalTargetType.highPriorityUnit or \
				target.targetType == TacticalTargetType.mediumPriorityUnit or \
				target.targetType == TacticalTargetType.lowPriorityUnit:

				# Is this unit near enough?
				if army.position.distance(target.target) <= radius:
					enemyNear = True
					break

		if enemyNear:
			# Add units from army to tactical AI for this turn
			for unit in army.units():
				if unit is None:
					continue

				if not unit.processedInTurn() and not unit.isDelayedDeath() and unit.canMove():
					unitInList = False

					for currentTurnUnit in self.currentTurnUnits:
						if currentTurnUnit.location == unit.location and currentTurnUnit.unitType == unit.unitType:
							unitInList = True

					if not unitInList:
						self.currentTurnUnits.append(unit)

			# Now attack these targets
			for allTarget in self.allTargets:
				# Is the target of an appropriate type?
				if allTarget.targetType == TacticalTargetType.highPriorityUnit or \
					allTarget.targetType == TacticalTargetType.mediumPriorityUnit or \
					allTarget.targetType == TacticalTargetType.lowPriorityUnit:

					if allTarget.isTargetStillAliveFor(self.player, simulation):
						# Is this unit near enough?
						if allTarget.target.distance(army.position) <= radius:
							plot = simulation.tileAt(allTarget.target)

							if plot is None:
								raise Exception('cant get plot')

							tacticalAnalysisMap.clearDynamicFlags()

							bestFriendlyRange = tacticalAnalysisMap.bestFriendlyRange()
							ignoreLineOfSight = tacticalAnalysisMap.ignoreLineOfSight
							tacticalAnalysisMap.setTargetBombardCells(
								target=allTarget.target,
								bestFriendlyRange=bestFriendlyRange,
								ignoreLineOfSight=ignoreLineOfSight,
								simulation=simulation
							)

							attackUnderway = self.executeSafeBombardsOn(allTarget, simulation)
							attackMade: bool = False
							if allTarget.isTargetStillAliveFor(self.player, simulation):
								attackUnderway, attackMade = self.executeProtectedBombards(allTarget, simulation=simulation)

							if attackMade:
								attackUnderway = True

							if allTarget.isTargetStillAliveFor(self.player, simulation):
								defender = simulation.visibleEnemyAt(allTarget.target, self.player)
								if defender is not None:
									allTarget.damage = defender.attackStrengthAgainst(None, None, None, simulation)
									self.currentMoveCities = []

									if self.findUnitsWithinStrikingDistanceTowards(allTarget.target, numTurnsAway=1, simulation=simulation):
										self.computeTotalExpectedDamage(allTarget, plot, simulation)
										self.executeAttack(target=allTarget, tile=plot, inflictWhatWeTake=True, mustSurviveAttack=True, simulation=simulation)

		return

	def moveWithFormation(self, unit, position: UnitFormationPosition):
		"""Store off a new unit that needs to move as part of an operational AI formation"""
		if unit is None:
			return

		if unit.moves() > 0:
			self.operationUnits.append(OperationUnit(unit, position))

	def executeGatherMoves(self, army, simulation):
		"""Gather all units requested through calls to MoveWithFormation() to army's location"""
		if army is None:
			return

		if len(self.operationUnits) == 0:
			return

		target = army.position

		# Gathering - treat everyone as a melee unit; don't need ranged in the rear yet
		numUnits = len(self.operationUnits)

		# Range around target based on number of units we need to place
		radius = OperationHelpers.gatherRangeFor(numUnits)

		# Try one time with computed range
		foundEnoughDeploymentPlots: bool = False
		if self.scoreDeploymentPlots(target, army, numMeleeUnits=numUnits, numRangedUnits=0, radius=radius, simulation=simulation):
			# Did we get twice as many possible plots as units?
			if len(self.tempTargets) >= (numUnits * 2):
				foundEnoughDeploymentPlots = True
			else:
				self.tempTargets = []
				radius = 3

		if not foundEnoughDeploymentPlots:
			if not self.scoreDeploymentPlots(target, army, numMeleeUnits=numUnits, numRangedUnits=0, radius=radius, simulation=simulation):
				logging.debug(f"Operation aborting. Army ID: {army.identifier[0:8]}. Not enough spaces to deploy near target")

				army.operation.state = OperationStateType.aborted
				army.operation.stateReason = OperationStateReason.noRoomDeploy
				return

		# Compute the moves to get the best deployment
		self.tempTargets = sorted(self.tempTargets)
		self.potentialBlocks = []
		done: bool = False

		unitsToPlace = numUnits

		for tempTarget in self.tempTargets:
			loopPlot = simulation.tileAt(tempTarget.target)

			if loopPlot is None:
				continue

			# Don't use if there's already a unit not in the army here
			unitAlreadyThere = simulation.unitAt(tempTarget.target, UnitMapType.combat)
			if unitAlreadyThere is not None:
				if unitAlreadyThere.army() is not None and unitAlreadyThere.army().identifier == army.identifier:
					if self.findClosestOperationUnit(loopPlot, safeForRanged=True, mustBeRangedUnit=False, simulation=simulation):
						for currentMoveUnit in self.currentMoveUnits:
							blockingUnit = BlockingUnit(
								unit=currentMoveUnit.unit,
								point=tempTarget.target,
								numberOfChoices=len(self.currentMoveUnits),
								distanceToTarget=currentMoveUnit.movesToTarget
							)
							self.potentialBlocks.append(blockingUnit)

						unitsToPlace -= 1
						if unitsToPlace == 0:
							done = True

		# Now ready to make the assignments
		self.assignDeployingUnits(numUnitsRequiredToDeploy=numUnits - unitsToPlace, simulation=simulation)

		self.performChosenMoves(simulation=simulation)

		# Log if someone in army didn't get a move assigned (how do we address this in the future?)
		if len(self.chosenBlocks) < numUnits:
			logging.debug(f"No gather move for {numUnits - len(self.chosenBlocks)} units")
			# self.logTacticalMessage(strMsg);

		return

	def scoreDeploymentPlots(self, target, army, numMeleeUnits: int, numRangedUnits: int, radius: int, simulation):
		"""Pick best hexes for deploying our army (based on safety, terrain, and keeping a tight formation).
		Returns false if insufficient free plots."""
		tacticalAnalysisMap = simulation.tacticalAnalysisMap()

		safeForDeployment: bool = False
		forcedToUseWater: bool = False
		numSafePlotsFound: int = 0
		numDeployPlotsFound: int = 0

		# We'll store the hexes we've found here
		self.tempTargets = []

		for dx in range(-radius, radius):
			for dy in range(-radius, radius):
				plotPoint = HexPoint(target.x + dx, target.y + dy)

				if simulation.tileAt(plotPoint) is None:
					continue

				safeForDeployment = True
				forcedToUseWater = False

				plotDistance = plotPoint.distance(target)
				if plotDistance <= radius:
					cell: TacticalAnalysisCell = tacticalAnalysisMap.plots.values[plotPoint.y][plotPoint.x]

					operation = army.operation
					if operation is None:
						continue

					valid = False
					if operation.isMixedLandNavalOperation() and cell.canUseForOperationGatheringCheckWater(isWater=True):
						valid = True
					elif operation.isAllNavalOperation() and cell.canUseForOperationGatheringCheckWater(isWater=True):
						valid = True
					elif not operation.isAllNavalOperation() and not operation.isMixedLandNavalOperation() and \
						(cell.canUseForOperationGatheringCheckWater(isWater=False) or simulation.isPrimarilyNaval()):
						valid = True
						if cell.isWater():
							forcedToUseWater = True

					if operation.isMixedLandNavalOperation() or operation.isAllNavalOperation():
						if not army.isAllOceanGoing(simulation) and cell.isOcean():
							valid = False

					if valid:
						# Skip this plot if friendly unit that isn't in this army
						if cell.friendlyMilitaryUnit() is not None and cell.friendlyMilitaryUnit().army() is not None:
							if cell.friendlyMilitaryUnit().army() != army:
								continue

						numDeployPlotsFound += 1
						score = 600 - (plotDistance * 100)
						if cell.isSubjectToAttack():
							score -= 100
							safeForDeployment = False
						else:
							numSafePlotsFound += 1

						if cell.isEnemyCanMovePast():
							score -= 100

						tmpTile = simulation.tileAt(plotPoint)
						if simulation.cityAt(plotPoint) is not None and tmpTile.hasOwner() and self.player == tmpTile.owner():
							score += 100
						else:
							score += cell.defenseModifier() * 2

						if forcedToUseWater:
							score = 10

						cell.setSafeDeployment(safeForDeployment)
						cell.setDeploymentScore(score)

						# Save this in our list of potential targets
						tacticalTarget = TacticalTarget(TacticalTargetType.none, plotPoint)

						tacticalTarget.threatValue = score  # or damage ?

						# A bit of a hack - - use high priority targets to indicate safe plots for ranged units
						if safeForDeployment:
							tacticalTarget.targetType = TacticalTargetType.highPriorityUnit
						else:
							tacticalTarget.targetType = TacticalTargetType.lowPriorityUnit

						self.tempTargets.append(tacticalTarget)

		# Make sure we found enough
		if numSafePlotsFound < numRangedUnits or numDeployPlotsFound < (numMeleeUnits + numRangedUnits):
			return False

		return True

	def findClosestOperationUnit(self, targetTile, safeForRanged: bool, mustBeRangedUnit: bool, simulation):
		"""Fills m_CurrentMoveUnits with all units in operation that can get to target (returns TRUE if 1 or more found)"""
		rtnValue: bool = False
		self.currentMoveUnits = []

		# Loop through all units available to operation
		for operationUnit in self.operationUnits:
			loopUnit = operationUnit.unit

			if loopUnit is None:
				continue

			validUnit = True

			if loopUnit.hasMoved(simulation):
				validUnit = False
			elif not safeForRanged and loopUnit.canAttackRanged():
				validUnit = False
			elif mustBeRangedUnit and not loopUnit.canAttackRanged():
				validUnit = False

			if validUnit:
				turns = loopUnit.turnsToReach(targetTile.point, simulation)

				if turns != sys.maxsize:
					tacticalUnit = TacticalUnit(loopUnit, attackStrength=1000 - turns, healthPercent=100)
					tacticalUnit.movesToTarget = targetTile.point.distance(loopUnit.location)
					self.currentMoveUnits.append(tacticalUnit)
					rtnValue = True

		# Now sort them by turns to reach
		self.currentMoveUnits = sorted(self.currentMoveUnits, key=lambda a: a.movesToTarget)

		return rtnValue

	def assignDeployingUnits(self, numUnitsRequiredToDeploy: int, simulation) -> bool:
		"""Uses information from m_PotentialBlocks to make final assignments to put deploying unit on target"""
		choseOne = True
		rtnValue = True

		self.temporaryBlocks = []
		self.chosenBlocks = []

		# Loop through potential blocks looking for assignments we MUST make (only one possibility)
		while choseOne:
			choseOne = False
			self.newlyChosen = []

			for potentialBlock in self.potentialBlocks:
				if potentialBlock.numberOfChoices != 1:
					continue

				self.newlyChosen.append(potentialBlock)
				choseOne = True

			if choseOne:
				# Do we have the same unit in m_NewlyChosen twice?
				if self.haveDuplicateUnit():
					return False  # Not going to work
				else:
					# Copy to final list
					for newlyChosenItem in self.newlyChosen:
						self.chosenBlocks.append(newlyChosenItem)

					self.removeChosenUnitsAtStartIndex(0)

					# Do we have enough units left to cover everything?
					if self.numUniqueUnitsLeft() < (numUnitsRequiredToDeploy - len(self.chosenBlocks)):
						return False

		# Pick the closest unit for highest priority assignment until all processed
		potentialBlock = firstOrNone(self.potentialBlocks)
		while potentialBlock is not None:
			choseOne = False
			self.newlyChosen = []

			self.newlyChosen.append(potentialBlock)
			self.chosenBlocks.append(potentialBlock)

			# Don't copy the other entries for this hex so pass in the number of choices here
			self.removeChosenUnitsAtStartIndex(potentialBlock.numberOfChoices)

			# Do we have enough units left to cover everything?
			if self.numUniqueUnitsLeft() < (numUnitsRequiredToDeploy - len(self.chosenBlocks)):
				# Used to abort here, but better if we get the moves in we can
				rtnValue = False

			potentialBlock = firstOrNone(self.potentialBlocks)

		return rtnValue

	def removeChosenUnitsAtStartIndex(self, startIndex: int):
		"""Pull the units we just assigned out of the list of potential assignments"""
		self.temporaryBlocks = []
		self.temporaryBlocks = self.potentialBlocks
		self.potentialBlocks = []

		for index in range(startIndex, len(self.temporaryBlocks)):
			copyIt = True

			blockingUnit = self.temporaryBlocks[index]

			# Loop through chosen array looking for occurrences of this unit
			for index2 in range(0, len(self.newlyChosen)):
				if not copyIt:
					continue

				if blockingUnit.unit == self.newlyChosen[index2].unit:
					copyIt = False

			if copyIt:
				self.potentialBlocks.append(blockingUnit)

		# Rebuild number of choices
		for index in range(0, len(self.potentialBlocks)):
			numberOfFoundBlocks = 0

			plot = self.potentialBlocks[index].point

			if plot is None:
				continue

			for index2 in range(0, len(self.potentialBlocks)):
				if plot != self.potentialBlocks[index2].point:
					continue

				numberOfFoundBlocks += 1

			self.potentialBlocks[index].numberOfChoices = numberOfFoundBlocks

		return

	def numUniqueUnitsLeft(self) -> int:
		"""How many units are left unassigned for a blocking position?"""
		rtnValue: int = 1

		if len(self.potentialBlocks) < 2:
			return len(self.potentialBlocks)

		# Copy data over and sort it so in unit ID order
		self.temporaryBlocks = []
		self.temporaryBlocks = self.potentialBlocks
		self.temporaryBlocks = sorted(self.temporaryBlocks, key=lambda tb: tb.distanceToTarget)

		current = self.temporaryBlocks[0].unit

		for index in range(1, len(self.temporaryBlocks)):
			if not self.temporaryBlocks[index].unit == current:
				rtnValue += 1
				current = self.temporaryBlocks[index].unit

		return rtnValue

	def performChosenMoves(self, fallbackMoveRange: int = 1, simulation=None):
		"""Make and log selected movements"""
		if simulation is None:
			raise Exception('simulation cannot be None')

		# Make moves up into hexes, starting with units already close to their final destination
		self.chosenBlocks = sorted(self.chosenBlocks, key=lambda a: a.distanceToTarget)

		# First loop through is for units that have a unit moving into their hex.They need to leave first!
		for chosenBlock in self.chosenBlocks:
			unit = chosenBlock.unit
			if unit is None:
				continue

			if unit.location != chosenBlock.point and self.isInChosenMoves(unit.location) and \
				simulation.numFriendlyUnits(chosenBlock.point, self.player, unit.unitMapType()) == 0:
				moveWasSafe: bool = False
				self.moveToUsingSafeEmbark(unit, chosenBlock.point, moveWasSafe, simulation)

				logging.debug(f"Deploying {unit.name()} (to get out of way), To {chosenBlock.point}, At {unit.location}, Distance Before Move: {chosenBlock.distanceToTarget}")

				# Use number of choices field to indicate already moved
				chosenBlock.numberOfChoices = -1

		# Second loop is for units moving into their chosen spot normally
		for chosenBlock in self.chosenBlocks:
			unit = chosenBlock.unit
			if unit is None:
				continue

			if unit.location == chosenBlock.point:
				chosenBlock.numberOfChoices = -1
			else:
				# Someone we didn't move above?
				if chosenBlock.numberOfChoices != -1:
					plotBeforeMove: HexPoint = unit.location
					moveWasSafe: bool = False
					self.moveToUsingSafeEmbark(unit, chosenBlock.point, moveWasSafe, simulation)

					logging.debug(f"Deploying {unit.name()}, To {chosenBlock.point}, At {unit.location}, Distance Before Move: {chosenBlock.distanceToTarget}")

					# Use number of choices field to indicate already moved
					if plotBeforeMove != unit.location:
						chosenBlock.numberOfChoices = -1

		# Third loop is for units we still haven't been able to move (other units must be blocking their target for this turn)
		if fallbackMoveRange > 0:
			for chosenBlock in self.chosenBlocks:
				unit = chosenBlock.unit
				if unit is None:
					continue

				# Someone we didn't move above?
				if chosenBlock.numberOfChoices != -1:
					plotBeforeMove = unit.location

					if self.moveToEmptySpaceNearTarget(unit, chosenBlock.point, unit.domain() == UnitDomainType.land, simulation):
						logging.debug(f"Deploying {unit.name()} to space near target, Target {chosenBlock.point}: , At {unit.location}, Distance Before Move: {chosenBlock.distanceToTarget}")

						if plotBeforeMove != unit.location:
							chosenBlock.numberOfChoices = -1

		# Fourth loop let's unit end within 2 of target
		if fallbackMoveRange > 1:
			for chosenBlock in self.chosenBlocks:
				unit = chosenBlock.unit
				if unit is None:
					continue

				# Someone we didn't move above?
				if chosenBlock.numberOfChoices != -1:
					if self.moveToEmptySpaceTwoFromTarget(unit, chosenBlock.point, unit.domain() == UnitDomainType.land, simulation):
						logging.debug(f"Deploying {unit.name()} to space within 2 of target, Target {chosenBlock.point}, At {unit.location}, Distance Before Move: {chosenBlock.distanceToTarget}")


		# Finish moves for all units
		for chosenBlock in self.chosenBlocks:
			unit = chosenBlock.unit
			if unit is None:
				continue

			if not unit.isDelayedDeath():
				if unit.moves() > 0:
					if unit.canPillageAt(unit.location, simulation) and unit.damage() > 0:
						unit.pushMission(UnitMission(UnitMissionType.pillage), simulation)
						logging.debug(f"Already in position, will pillage with {unit.name()}, {chosenBlock.point}")
					elif unit.canFortifyAt(unit.location, simulation):
						unit.pushMission(UnitMission(UnitMissionType.fortify), simulation)
						logging.debug(f"Already in position, will fortify with {unit.name()}, {chosenBlock.point}")
					else:
						logging.debug(f"Already in position, no move for {unit.name()}, {chosenBlock.point}")

					unit.finishMoves()

				self.unitProcessed(unit, simulation=simulation)

		return

	def haveDuplicateUnit(self) -> bool:
		"""Were we forced to select the same unit to block twice?"""
		for index in range(0, len(self.newlyChosen) - 1):
			for index2 in range(index + 1, len(self.newlyChosen)):
				if self.newlyChosen[index].unit == self.newlyChosen[index2].unit:
					return True

		return False

	def executeFormationMoves(self, army, closestCurrentCenterOfMassOnPath, simulation):
		"""Complete moves for all units requested through calls to MoveWithFormation()"""
		if len(self.operationUnits):
			return

		target: HexPoint = army.position
		meleeUnits: int = 0
		rangedUnits: int = 0

		for operationUnit in self.operationUnits:
			unit = operationUnit.unit

			if unit is None:
				continue

			if unit.canAttackRanged():
				rangedUnits += 1
			else:
				meleeUnits += 1

			# See if we have enough places to put everyone
			if not self.scoreFormationPlots(army, target, closestCurrentCenterOfMassOnPath, meleeUnits + rangedUnits, simulation):
				logging.debug(f"Operation aborting. Army ID: {army.identifier[0:8]}. Not enough spaces to deploy along formation's path")

				army.operation.state = OperationStateType.aborted
				army.operation.stateReason = OperationStateReason.noRoomDeploy
			else:
				# Compute the moves to get the best deployment
				self.tempTargets.sort()

				# First loop for melee units who should be out front
				meleeUnitsToPlace: int = meleeUnits + 0
				done: bool = False

				for tempTarget in self.tempTargets:
					if done:
						continue

					loopPlot = simulation.tileAt(tempTarget.target)

					if loopPlot is None:
						continue

					# Don't use if there's already someone here
					if not simulation.areUnitsAt(tempTarget.target):
						if self.findClosestOperationUnit(loopPlot, safeForRanged=False, mustBeRangedUnit=False, simulation=simulation):
							firstCurrentMoveUnits = firstOrNone(self.currentMoveUnits)

							if firstCurrentMoveUnits is None:
								continue

							innerUnit = firstCurrentMoveUnits.unit

							if innerUnit is None:
								continue

							moveWasSafe = False
							self.moveToUsingSafeEmbark(innerUnit, loopPlot.point, moveWasSafe=moveWasSafe, simulation=simulation)
							innerUnit.finishMoves()

							logging.debug(f"Deploying melee unit, {innerUnit.name()}, To {tempTarget.target}, At {innerUnit.location}")

							meleeUnitsToPlace -= 1

					if meleeUnitsToPlace == 0:
						done = True

				# Log if someone in army didn't get a move assigned
				if meleeUnitsToPlace > 0:
					logging.debug(f"No army deployment move for {meleeUnitsToPlace} melee units")

				# Second loop for ranged units
				rangedUnitsToPlace = [r.copy() for r in rangedUnits]
				done = False
				for tempTarget in self.tempTargets:
					targetType = tempTarget.targetType
					loopPlot = simulation.tileAt(tempTarget.target)

					if loopPlot is None:
						continue

					if targetType == TacticalTargetType.highPriorityUnit:
						# Don't use if there's already someone here
						if simulation.unitAt(tempTarget.target, UnitMapType.combat) is None:
							if self.findClosestOperationUnit(loopPlot, safeForRanged=True, mustBeRangedUnit=True, simulation=simulation):
								firstCurrentMoveUnits = firstOrNone(self.currentMoveUnits)

								if firstCurrentMoveUnits is None:
									continue

								innerUnit = firstCurrentMoveUnits.unit

								if innerUnit is None:
									continue

								moveWasSafe = False
								self.moveToUsingSafeEmbark(innerUnit, loopPlot.point, moveWasSafe=moveWasSafe, simulation=simulation)
								innerUnit.finishMoves()

								logging.debug(f"Deploying ranged unit, {innerUnit.name()}, To {loopPlot.point}, At {innerUnit.location}")

								rangedUnitsToPlace -= 1

					if rangedUnitsToPlace == 0:
						done = True

				# Third loop for ranged units we couldn't put in an ideal spot
				for tempTarget in self.tempTargets:
					targetType = tempTarget.targetType

					loopPlot = simulation.tileAt(tempTarget.target)

					if loopPlot is None:
						continue

					if targetType == TacticalTargetType.highPriorityUnit:
						# Don't use if there's already someone here
						if simulation.unitAt(tempTarget.target, UnitMapType.combat) is None:
							if self.findClosestOperationUnit(loopPlot, safeForRanged=True, mustBeRangedUnit=True, simulation=simulation):
								firstCurrentMoveUnits = firstOrNone(self.currentMoveUnits)

								if firstCurrentMoveUnits is None:
									continue

								innerUnit = firstCurrentMoveUnits.unit

								if innerUnit is None:
									continue

								moveWasSafe = False
								self.moveToUsingSafeEmbark(innerUnit, loopPlot.point, moveWasSafe=moveWasSafe, simulation=simulation)
								innerUnit.finishMoves()

								logging.debug(f"Deploying ranged unit (Pass 2), {innerUnit.name()}, To {loopPlot.point}, At {innerUnit.location}")

								rangedUnitsToPlace -= 1

					if rangedUnitsToPlace == 0:
						done = True

				# Log if someone in army didn't get a move assigned
				if rangedUnitsToPlace > 0:
					logging.debug(f"No army deployment move for {rangedUnitsToPlace} ranged units")

		return

	def addTemporaryZone(self, zone: TemporaryZone):
		"""Add a temporary dominance zone around a short-term target"""
		self.temporaryZones.append(zone)

	def useThisDominanceZone(self, dominanceZone):
		"""Do we want to process moves for this dominance zone?"""
		isOurCapital: bool = False

		city = dominanceZone.closestCity
		if city is not None:
			isOurCapital = self.player == city.player and city.isCapital()

		return (isOurCapital or dominanceZone.rangeClosestEnemyUnit <= (TacticalAI.recruitRange / 2) or
			(dominanceZone.dominanceFlag != TacticalDominanceType.noUnitsPresent and dominanceZone.dominanceFlag != TacticalDominanceType.notVisible))

	def findPostureTypeFor(self, dominanceZone: Optional[TacticalDominanceZone]) -> TacticalPostureType:
		"""Find last posture for a specific zone"""
		if dominanceZone is None:
			return TacticalPostureType.none

		if dominanceZone.closestCity is None:
			return TacticalPostureType.none

		postures: Optional[TacticalPosture] = next(filter(lambda p: (p.player is not None and self.player == p.player) and p.isWater == dominanceZone.isWater and (p.city is not None and p.city.location == dominanceZone.closestCity.location), self.postures), None)

		if postures is not None:
			return postures.postureType

		return TacticalPostureType.none

	def selectPostureTypeFor(self, dominanceZone: TacticalDominanceZone, lastPosture: TacticalPostureType, dominancePercentage: int) -> TacticalPostureType:
		"""Select a posture for a specific zone"""
		chosenPosture: TacticalPostureType = TacticalPostureType.none
		rangedDominance: TacticalDominanceType = TacticalDominanceType.even
		unitCountDominance: TacticalDominanceType = TacticalDominanceType.even

		# Compute who is dominant in various areas
		# Ranged strength
		if dominanceZone.enemyRangedStrength <= 0:
			rangedDominance = TacticalDominanceType.friendly
		else:
			ratio = dominanceZone.friendlyRangedStrength * 100 / dominanceZone.enemyRangedStrength
			if ratio > 100 + dominancePercentage:
				rangedDominance = TacticalDominanceType.friendly
			elif ratio < 100 - dominancePercentage:
				rangedDominance = TacticalDominanceType.enemy

		# Number of units
		if dominanceZone.enemyUnitCount <= 0:
			unitCountDominance = TacticalDominanceType.friendly
		else:
			ratio = dominanceZone.friendlyUnitCount * 100 / dominanceZone.enemyUnitCount
			if ratio > 100 + dominancePercentage:
				unitCountDominance = TacticalDominanceType.friendly
			elif ratio < 100 - dominancePercentage:
				unitCountDominance = TacticalDominanceType.enemy

		# Choice based on whose territory this is
		if dominanceZone.territoryType == TacticalDominanceTerritoryType.enemy:
			if dominanceZone.dominanceFlag == TacticalDominanceType.enemy or \
				dominanceZone.friendlyRangedUnitCount == dominanceZone.friendlyUnitCount:
				# Always withdraw if enemy dominant overall
				chosenPosture = TacticalPostureType.withdraw
			elif dominanceZone.enemyUnitCount > 0 and dominanceZone.dominanceFlag == TacticalDominanceType.friendly and \
				(rangedDominance != TacticalDominanceType.enemy or dominanceZone.friendlyStrength > dominanceZone.enemyStrength * 2):
				# Destroy units then assault - for first time need dominance in total strength but not enemy dominance in ranged units OR just double total strength
				chosenPosture = TacticalPostureType.steamRoll
			elif lastPosture == TacticalPostureType.steamRoll and dominanceZone.dominanceFlag == TacticalDominanceType.friendly and dominanceZone.enemyUnitCount > 0:
				# - less stringent if continuing this from a previous turn
				chosenPosture = TacticalPostureType.steamRoll
			elif rangedDominance == TacticalDominanceType.friendly and unitCountDominance != TacticalDominanceType.enemy:
				# Sit and bombard - for first time need dominance in ranged strength and total unit count
				chosenPosture = TacticalPostureType.sitAndBombard
			elif lastPosture == TacticalPostureType.sitAndBombard and rangedDominance != TacticalDominanceType.enemy and unitCountDominance != TacticalDominanceType.enemy:
				# - less stringent if continuing this from a previous turn
				chosenPosture = TacticalPostureType.sitAndBombard
			elif dominanceZone.dominanceFlag == TacticalDominanceType.friendly:
				# Go right after the city - need tactical dominance
				chosenPosture = TacticalPostureType.surgicalCityStrike
			elif unitCountDominance == TacticalDominanceType.friendly and dominanceZone.enemyUnitCount > 1:
				# Exploit flanks - for first time need dominance in unit count
				chosenPosture = TacticalPostureType.exploitFlanks
			elif lastPosture == TacticalPostureType.exploitFlanks and unitCountDominance != TacticalDominanceType.enemy and dominanceZone.enemyUnitCount > 1:
				# - less stringent if continuing this from a previous turn
				chosenPosture = TacticalPostureType.exploitFlanks
			else:
				# Default for this zone
				chosenPosture = TacticalPostureType.surgicalCityStrike
		elif dominanceZone.territoryType == TacticalDominanceTerritoryType.neutral or dominanceZone.territoryType == TacticalDominanceTerritoryType.noOwner:
			if rangedDominance == TacticalDominanceType.friendly and unitCountDominance != TacticalDominanceType.enemy:
				chosenPosture = TacticalPostureType.attritFromRange
			elif lastPosture == TacticalPostureType.attritFromRange and rangedDominance != TacticalDominanceType.enemy:
				# - less stringent if continuing this from a previous turn
				chosenPosture = TacticalPostureType.attritFromRange
			elif unitCountDominance == TacticalDominanceType.friendly and dominanceZone.enemyUnitCount > 0:
				# Exploit flanks - for first time need dominance in unit count
				chosenPosture = TacticalPostureType.exploitFlanks
			elif lastPosture == TacticalPostureType.exploitFlanks and unitCountDominance != TacticalDominanceType.enemy and dominanceZone.enemyUnitCount > 0:
				# - less stringent if continuing this from a previous turn
				chosenPosture = TacticalPostureType.exploitFlanks
			else:
				# Default for this zone
				chosenPosture = TacticalPostureType.exploitFlanks
		elif dominanceZone.territoryType == TacticalDominanceTerritoryType.friendly:
			if rangedDominance == TacticalDominanceType.friendly and dominanceZone.friendlyRangedUnitCount > 1:
				chosenPosture = TacticalPostureType.attritFromRange
			elif lastPosture == TacticalPostureType.attritFromRange and dominanceZone.friendlyRangedUnitCount > 1 and rangedDominance != TacticalDominanceType.enemy:
				# - less stringent if continuing this from a previous turn
				chosenPosture = TacticalPostureType.attritFromRange
			elif unitCountDominance == TacticalDominanceType.friendly and dominanceZone.enemyUnitCount > 0:
				# Exploit flanks - for first time need dominance in unit count
				chosenPosture = TacticalPostureType.exploitFlanks
			elif lastPosture == TacticalPostureType.exploitFlanks and unitCountDominance != TacticalDominanceType.enemy and dominanceZone.enemyUnitCount > 0:
				# - less stringent if continuing this from a previous turn
				chosenPosture = TacticalPostureType.exploitFlanks
			elif dominanceZone.dominanceFlag == TacticalDominanceType.friendly or dominanceZone.dominanceFlag == TacticalDominanceType.even and rangedDominance == TacticalDominanceType.enemy:
				# Counterattack - for first time must be stronger or even with enemy having a ranged advantage
				chosenPosture = TacticalPostureType.counterAttack
			elif lastPosture == TacticalPostureType.counterAttack and dominanceZone.dominanceFlag != TacticalDominanceType.enemy:
				# - less stringent if continuing this from a previous turn
				chosenPosture = TacticalPostureType.counterAttack
			else:
				# Default for this zone
				chosenPosture = TacticalPostureType.hedgehog
		elif dominanceZone.territoryType == TacticalDominanceTerritoryType.tempZone:
			# Land or water?
			if dominanceZone.isWater:
				chosenPosture = TacticalPostureType.shoreBombardment
			else:
				# Should be a barbarian camp
				chosenPosture = TacticalPostureType.exploitFlanks

		return chosenPosture

	def executeProtectedBombards(self, target: TacticalTarget, attackUnderway: bool = False, simulation=None) -> (bool, bool):
		"""Bombard an enemy target from plots we can protect from enemy attack (return True if some attack made)"""
		if simulation is None:
			raise Exception("simulation must not be None")
		
		attackMade: bool = True
		atLeastOneAttackInitiated: bool = False

		while attackMade and target.isTargetStillAliveFor(self.player, simulation):
			attackMade = self.executeOneProtectedBombardOn(target, simulation)
			if attackMade:
				attackUnderway = True
				atLeastOneAttackInitiated = True

		return attackUnderway, atLeastOneAttackInitiated

	def executeOneProtectedBombardOn(self, target: TacticalTarget, simulation) -> bool:
		"""Bombard an enemy target from a single plot we can protect from enemy attack (return True if some attack made)"""
		firstAttacker = None
		numUnitsRequiredToCover: int = 0

		targetPlot = simulation.tileAt(target.target)

		if targetPlot is None:
			return False

		if self.plotAlreadyTargeted(target.target) != -1:
			return False

		city = simulation.cityAt(target.target)
		if city is not None:
			requiredDamage = city.maxHealthPoints() - city.damage()

			# Can't eliminate a city with ranged fire, so don't target one if that low on health
			if requiredDamage <= 1:
				return False

		radius = simulation.tacticalAnalysisMap().bestFriendlyRange()
		self.tempTargets = []

		# Build a list of all plots that have LOS to target where no enemy unit is adjacent
		for point in target.target.areaWithRadius(radius):
			attackPlot = simulation.tileAt(point)

			if attackPlot is None:
				continue

			plotDistance = point.distance(target.target)
			if 0 < plotDistance <= radius:
				cell = simulation.tacticalAnalysisMap().plots.values[point.y][point.x]

				if cell.isRevealed() and cell.canUseForOperationGathering():
					if cell.isWithinRangeOfTarget():
						# Check for adjacent enemy unit
						noEnemyAdjacent: bool = True

						for neighbor in point.neighbors():
							if not noEnemyAdjacent:
								continue

							neighborCell = simulation.tacticalAnalysisMap().plots.values[neighbor.y][neighbor.x]
							if neighborCell.enemyMilitaryUnit is not None:
								noEnemyAdjacent = False

						if noEnemyAdjacent:
							# Do we have a unit that can get off a bombard from here THIS turn
							numTurns: int = -1
							haveLineOfSight = attackPlot.canSeeTile(targetPlot, self.player, radius, hasSentry=False, simulation=simulation)

							if self.findClosestUnitTowards(
								towards=attackPlot,
								numTurnsAway=0,
								mustHaveHalfHP=False,
								mustBeRangedUnit=True,
								rangeRequired=plotDistance,
								needsIgnoreLineOfSight=not haveLineOfSight,
								mustBeMeleeUnit=False,
								ignoreUnits=False,
								rangedAttackTarget=targetPlot,
								simulation=simulation):

								numTurns = 0
							# What about next turn?
							elif self.findClosestUnitTowards(
								towards=attackPlot,
								numTurnsAway=1,
								mustHaveHalfHP=False,
								mustBeRangedUnit=True,
								rangeRequired=plotDistance,
								needsIgnoreLineOfSight=not haveLineOfSight,
								mustBeMeleeUnit=False,
								ignoreUnits=False,
								rangedAttackTarget=targetPlot,
								simulation=simulation):

								numTurns = 1

							# If found a unit that could get here, see if we can cover the hex from enemy attack
							if numTurns >= 0:
								firstMoveUnit = firstOrNone(self.currentMoveUnits)
								attackingUnit = firstMoveUnit.unit if firstMoveUnit is not None else None
								numUnitsRequiredToCover, canCover = self.canCoverFromEnemy(attackPlot, attackingUnit, simulation)
								if canCover:
									tacticalTarget = TacticalTarget(TacticalTargetType.none, point)

									# How desirable is this move?
									# Set up math so having to allocate 3 extra units to defend is worse than waiting a turn to attack
									priority = 300 - (numTurns * 100)
									priority -= 40 * numUnitsRequiredToCover
									tacticalTarget.threatValue = priority
									self.tempTargets.append(tacticalTarget)

		# No plots to shoot from?
		if len(self.tempTargets) == 0:
			return False

		# Sort potential spots
		self.tempTargets.sort()

		# Have to rebuild blocking position info for this specific spot
		attackPlot = simulation.tileAt(firstOrNone(self.tempTargets).target)
		if attackPlot is None:
			return False

		plotDistance = firstOrNone(self.tempTargets).target.distance(target.target)
		haveLineOfSight = attackPlot.canSeeTile(targetPlot, self.player, radius=radius, hasSentry=False, simulation=simulation)

		if self.findClosestUnitTowards(towards=attackPlot, numTurnsAway=0, mustHaveHalfHP=False, mustBeRangedUnit=True,
			rangeRequired=plotDistance, needsIgnoreLineOfSight=not haveLineOfSight, mustBeMeleeUnit=False,
			ignoreUnits=False, rangedAttackTarget=targetPlot, simulation=simulation) or self.findClosestUnit(
			towards=attackPlot, numTurnsAway=1, mustHaveHalfHP=False, mustBeRangedUnit=True, rangeRequired=plotDistance,
			needsIgnoreLineOfSight=not haveLineOfSight, mustBeMeleeUnit=False, ignoreUnits=False,
			rangedAttackTarget=targetPlot, simulation=simulation):

			attackingUnit = firstOrNone(self.currentMoveUnits).unit

			numUnitsRequiredToCover, canCover = self.canCoverFromEnemy(attackPlot, attackingUnit=attackingUnit, simulation=simulation)
			if canCover:
				# Make each blocking move
				for chosenBlock in self.chosenBlocks:
					chosenUnit = chosenBlock.unit
					if chosenUnit is None:
						continue

					if chosenUnit.location != chosenBlock.point:
						logging.debug(f"Moving to cover a protected bombard with {chosenUnit.name()}, at: {chosenBlock.point}")
						chosenUnit.pushMission(UnitMission(UnitMissionType.moveTo, target=chosenBlock.point), simulation)

					elif chosenUnit.canPillageAt(chosenUnit.location, simulation) and chosenUnit.damage() > 0:
						chosenUnit.pushMission(UnitMission(UnitMissionType.pillage), simulation)
						logging.debug(f"Pillaging during a protected bombard with {chosenUnit.name()}, at {chosenBlock.point}")

					elif chosenUnit.canFortifyAt(chosenUnit.location, simulation):
						chosenUnit.pushMission(UnitMission(UnitMissionType.fortify), simulation)
						logging.debug(f"Fortifying during a protected bombard with {chosenUnit.name()}, at {chosenBlock.point}")

					else:
						logging.debug(f"Sitting during a protected bombard with {chosenUnit.name()}, at {chosenBlock.point}")

					chosenUnit.finishMoves()
					self.unitProcessed(chosenUnit, simulation=simulation)

				# Then move the attacking unit
				if attackingUnit is not None:
					unit = attackingUnit
					if attackPlot.point != unit.location:
						unit.pushMission(UnitMission(UnitMissionType.moveTo, target=attackPlot.point), simulation)
						logging.debug(f"Moving closer for protected bombard with {unit.name()}, Target {attackPlot.point}, At {unit.location}")

					self.unitProcessed(attackingUnit, simulation=simulation)

					if unit.canSetUpForRangedAttack():
						unit.setUpForRangedAttackTo(True)
						logging.debug(f"Set up {unit.name()} for ranged attack")

					if unit.canMove() and not unit.isOutOfAttacks(simulation) and \
						unit.canRangeStrikeAt(target.target, needWar=True, noncombatAllowed=True, simulation=simulation):

						logging.debug(f"Making a protected bombard with {unit.name()}, Target {target.target}, At {unit.location}")

						if self.queueUnitAttack(unit, target, ranged=True):
							firstAttacker = unit

			if firstAttacker is not None:
				self.launchUnitAttack(firstAttacker, target, firstAttack=True, ranged=True, simulation=simulation)
				return True

		return False

	def canCoverFromEnemy(self, plot, attackingUnit, simulation) -> (int, bool):
		"""Do I have available friendly units that can stop this hex from being attacked?"""
		numUnitsRequiredToCover = 0

		# Can't melee attack at sea so those hexes are always covered
		if plot.isWater():
			return 0, True

		# Find all the hexes we need to cover
		for neighbor in plot.point.neighbors():
			loopPlot = simulation.tileAt(neighbor)
			if loopPlot is None:
				continue

			# Don't need to cover a water hex
			if not loopPlot.isWater():
				cell = simulation.tacticalAnalysisMap().plots.values[neighbor.y][neighbor.x]

				if cell.isEnemyCanMovePast() and not cell.isFriendlyTurnEndTile():
					numUnitsRequiredToCover += 1

		if numUnitsRequiredToCover == 0:
			self.chosenBlocks = []
			return 0, True
		else:
			if numUnitsRequiredToCover > len(self.currentTurnUnits):
				return 0, False

			# Have some unit that can cover each hex this turn?
			self.potentialBlocks = []

			for neighbor in plot.point.neighbors():
				loopPlot = simulation.tileAt(neighbor)
				if loopPlot is None:
					continue

				if not loopPlot.isWater():
					cell = simulation.tacticalAnalysisMap().plots.values[neighbor.y][neighbor.x]

					if cell.isEnemyCanMovePast() and not cell.isFriendlyTurnEndTile():

						if not self.findClosestUnit(
							towards=loopPlot,
							numTurnsAway=1,
							mustHaveHalfHP=False,
							mustBeRangedUnit=False,
							rangeRequired=2,
							needsIgnoreLineOfSight=False,
							mustBeMeleeUnit=True,
							ignoreUnits=False,
							rangedAttackTarget=None,
							simulation=simulation):

							return 0, False
						else:
							# Save off the units that could get here
							for currentMoveUnit in self.currentMoveUnits:
								if currentMoveUnit.unit is None:
									continue

								if currentMoveUnit != attackingUnit:
									self.potentialBlocks.append(BlockingUnit(currentMoveUnit, neighbor, len(self.currentMoveUnits), currentMoveUnit.movesToTarget))

		# Now select exact covering units, making sure we didn't over commit a unit to covering more than one hex
		return numUnitsRequiredToCover, self.assignCoveringUnits(numUnitsRequiredToCover)

	def assignCoveringUnits(self, numUnitsRequiredToCover) -> bool:
		"""Uses information from m_PotentialBlocks to make final assignments to block a hex (returns false if not possible)"""
		choseOne: bool = True

		self.temporaryBlocks = []
		self.chosenBlocks = []

		while choseOne:
			choseOne = False
			self.newlyChosen = []

			# Loop through potential blocks looking for assignments we MUST make (only one possibility)
			for potentialBlock in self.potentialBlocks:
				if potentialBlock.numberOfChoices == 1:
					self.newlyChosen.append(potentialBlock)
					choseOne = True

			if choseOne:
				# Do we have the same unit in m_NewlyChosen twice?
				if self.haveDuplicateUnit():
					return False  # Not going to work
				else:
					# Copy to final list
					for newlyChosenitem in self.newlyChosen:
						self.chosenBlocks.append(newlyChosenitem)

					self.removeChosenUnits(0)

					# Do we have enough units left to cover everything?
					if self.numUniqueUnitsLeft() < (numUnitsRequiredToCover - len(self.chosenBlocks)):
						return False

		return self.chooseRemainingAssignments(numUnitsRequiredToCover, numUnitsRequiredToCover)

	def chooseRemainingAssignments(self, numUnitsDesired: int, numUnitsAcceptable: int) -> bool:
		"""No clear cut blocking assignments left, have to make search possibilities and score most preferred"""
		bestScore: int = 0
		score: int = 0
		current: [int] = [0 for i in range(6)]
		first: [int] = [0 for i in range(6)]
		last: [int] = [0 for i in range(6)]

		blocksToCreate = numUnitsDesired - len(self.chosenBlocks)

		if blocksToCreate == 0:
			return True

		if blocksToCreate > 6:
			raise Exception("More than NUM_DIRECTION_TYPES hexes to block. Will cause array overflows and performance issues!")

		if 0 < blocksToCreate < 6:
			self.newlyChosen = []

			# Set up indexes pointing to the possible choices
			level = 0
			curIndex = 0

			while level < blocksToCreate:
				first[level] = curIndex
				numChoices = self.potentialBlocks[curIndex].numberOfChoices

				if numChoices <= 0:
					raise Exception("Invalid number of tactical AI move choices. Will cause array overflows and performance issues!")
				if numChoices + curIndex > len(self.potentialBlocks):
					raise Exception("Invalid number of tactical AI move choices. Will cause array overflows and performance issues!")

				last[level] = curIndex + numChoices - 1
				curIndex = last[level] + 1
				level += 1

			for index in range(0, blocksToCreate):
				current[index] = first[index]

			# Loop through each possibility
			done = False
			while not done:
				self.temporaryBlocks = []

				# Create this choice
				for index in range(0, blocksToCreate):
					if index >= len(self.potentialBlocks):
						raise Exception("Invalid fast vector index - show Ed")

					self.temporaryBlocks.append(self.potentialBlocks[current[index]])

				score = self.scoreAssignments(canLeaveOpenings=numUnitsDesired != numUnitsAcceptable)

				# If best so far, save it off
				if score > bestScore:
					self.newlyChosen = []
					for index in range(0, len(self.temporaryBlocks)):
						if self.temporaryBlocks[index].distanceToTarget == sys.maxsize:
							continue

						self.newlyChosen.append(self.temporaryBlocks[index])

					bestScore = score

				# Increment proper index
				incrementDone: bool = False

				for levelIndex in range((blocksToCreate - 1), 0, -1):
					# See if at end of line for this index
					if current[levelIndex] + 1 > last[levelIndex]:
						# Reset to first one and keep iterating
						current[levelIndex] = first[levelIndex]
					else:
						current[levelIndex] += 1
						incrementDone = True

				if not incrementDone:
					done = True

			# Copy final choices into output
			for index in range(0, len(self.newlyChosen)):
				self.chosenBlocks.append(self.newlyChosen[index])

			return len(self.chosenBlocks) >= numUnitsAcceptable

		return False

	def scoreAssignments(self, canLeaveOpenings: bool) -> int:
		"""Score for this set of chosen blocks in m_TemporaryBlocks (-1 if illegal)"""
		score: int = 0

		# Any assignment appear twice?
		for index in range(0, len(self.temporaryBlocks)):
			for index2 in range((index + 1), len(self.temporaryBlocks)):
				unit1 = self.temporaryBlocks[index].unit
				if unit1 is None:
					continue

				unit2 = self.temporaryBlocks[index2].unit
				if unit2 is None:
					continue

				if unit1 == unit2:
					if not canLeaveOpenings:
						return -1
					else:
						# "Clear" the move with greater distance by setting it to MAX_INT distance
						if self.temporaryBlocks[index].distanceToTarget < self.temporaryBlocks[index2].distanceToTarget:
							self.temporaryBlocks[index2].distanceToTarget = sys.maxsize
						else:
							self.temporaryBlocks[index].distanceToTarget = sys.maxsize

		# Legal, so let's score it
		for index in range(0, len(self.temporaryBlocks)):
			if self.temporaryBlocks[index].distanceToTarget == sys.maxsize:
				continue

			score += (10000 - (self.temporaryBlocks[index].distanceToTarget * 1000))
			score += self.temporaryBlocks[index].unit.power()

		return score

	def plotCloseOnTarget(self, checkDominance: bool, simulation):
		"""Close units in on primary target of this dominance zone"""
		zone = self.currentDominanceZone
		if zone is None:
			return

		if checkDominance:
			if zone.dominanceFlag == TacticalDominanceType.enemy:
				return

		# Flank attacks done; if in an enemy zone, close in on target
		if zone.territoryType == TacticalDominanceTerritoryType.tempZone:
			target = TacticalTarget(TacticalTargetType.barbarianCamp, zone.center.point, LeaderType.barbar, zone)
			self.executeCloseOnTarget(target, zone, simulation)

		elif zone.territoryType == TacticalDominanceType.enemy and zone.closestCity is not None:
			tile = simulation.tileAt(zone.closestCity.location)
			canSeeCity = tile.isVisibleTo(self.player)

			# If we can't see the city, be careful advancing on it.  We want to be sure we're not heavily outnumbered
			if not canSeeCity or zone.friendlyStrength > (zone.enemyStrength / 2):
				target = TacticalTarget(
					targetType=TacticalTargetType.city,
					target=zone.closestCity.location,
					targetLeader=zone.closestCity.leader,
					dominanceZone=zone
				)
				self.executeCloseOnTarget(target, zone, simulation)

		return

	def executeCloseOnTarget(self, target: TacticalTarget, zone: TacticalDominanceZone, simulation):
		"""Move forces in toward our target"""
		rangedUnits: int = 0
		meleeUnits: int = 0
		generals: int = 0

		tacticalRadius = simulation.tacticalAnalysisMap().tacticalRange

		self.operationUnits = []
		self.generalsToMove = []

		for currentTurnUnit in self.currentTurnUnits:
			unit = currentTurnUnit
			if unit is None:
				continue

			# If not naval invasion, proper domain of unit?
			if zone.navalInvasion or \
				(zone.isWater and unit.domain() == UnitDomainType.sea or not zone.isWater and unit.domain() == UnitDomainType.land):

				# Find units really close to target or somewhat close that just came out of an operation
				distance = unit.location.distance(target.target)
				if distance <= tacticalRadius or (distance <= (4 * 3) and unit.deployFromOperationTurn() + 5 >= simulation.currentTurn):
					operationUnit = OperationUnit(unit)

					if unit.canAttackRanged():
						operationUnit.position = UnitFormationPosition.bombard
						rangedUnits += 1
						self.operationUnits.append(operationUnit)
					elif unit.isGreatGeneral() or unit.isGreatAdmiral():
						operationUnit.position = UnitFormationPosition.civilianSupport
						generals += 1
						self.generalsToMove.append(operationUnit)
					else:
						operationUnit.position = UnitFormationPosition.frontline
						meleeUnits += 1
						self.operationUnits.append(operationUnit)

		# If have any units to move...
		if len(self.operationUnits) > 0:
			# Land only unless invasion or no enemy naval presence
			landOnly: bool = True
			if zone.navalInvasion or zone.enemyNavalUnitCount == 0:
				landOnly = False

			self.scoreCloseOnPlots(target.target, landOnly, simulation)

			# Compute the moves to get the best deployment
			self.tempTargets.sort()
			self.potentialBlocks = []

			rangedUnitsToPlace = rangedUnits
			meleeUnitsToPlace = meleeUnits

			# First loop for ranged unit spots
			done: bool = False
			for tempTarget in self.tempTargets:
				if done:
					continue

				if tempTarget.targetType == TacticalTargetType.highPriorityUnit:
					loopPlot = simulation.tileAt(tempTarget.target)
					if loopPlot is None:
						continue

					if self.findClosestOperationUnit(loopPlot, safeForRanged=True, mustBeRangedUnit=True, simulation=simulation):
						for currentMoveUnit in self.currentMoveUnits:
							self.potentialBlocks.append(BlockingUnit(currentMoveUnit.unit, loopPlot.point, len(self.currentMoveUnits), currentMoveUnit.movesToTarget))

						rangedUnitsToPlace -= 1
						if rangedUnitsToPlace == 0:
							done = True

			self.assignDeployingUnits(numUnitsRequiredToDeploy=rangedUnits - rangedUnitsToPlace, simulation=simulation)
			self.performChosenMoves(simulation=simulation)

			# Second loop for everyone else (including remaining ranged units)
			self.potentialBlocks = []
			meleeUnits += rangedUnitsToPlace
			meleeUnitsToPlace += rangedUnitsToPlace
			done = False

			for tempTarget in self.tempTargets:
				if done:
					continue

				if tempTarget.targetType == TacticalTargetType.highPriorityUnit:
					loopPlot = simulation.tileAt(tempTarget.target)
					if loopPlot is None:
						continue

					if self.findClosestOperationUnit(loopPlot, safeForRanged=True, mustBeRangedUnit=False, simulation=simulation):
						for currentMoveUnit in self.currentMoveUnits:
							self.potentialBlocks.append(BlockingUnit(currentMoveUnit.unit, loopPlot.point, len(self.currentMoveUnits), currentMoveUnit.movesToTarget))

						meleeUnitsToPlace -= 1
						if meleeUnitsToPlace == 0:
							done = True

			self.assignDeployingUnits(numUnitsRequiredToDeploy=meleeUnits - meleeUnitsToPlace, simulation=simulation)
			self.performChosenMoves(simulation=simulation)

		if len(self.generalsToMove) > 0:
			self.moveGreatGeneral(army=None, simulation=simulation)

		return

	def queueCityAttack(self, city, target: TacticalTarget, ranged: bool) -> bool:
		"""Queue up the attack - return TRUE if first attack on this target"""
		rtnValue: bool = True
		seriesId: int = -1

		# Can we find this target in the queue, if so what is its series ID
		queuedAttack = self.isAlreadyTargeted(target.target)
		if queuedAttack is not None:
			seriesId = queuedAttack.seriesId
			rtnValue = False
		else:
			self.currentSeriesId += 1
			seriesId = self.currentSeriesId

		attack = QueuedAttack()
		attack.attackerCity = city
		attack.target = target
		attack.ranged = ranged
		attack.cityAttack = False
		attack.seriesId = seriesId
		self.queuedAttacks.append(attack)

		logging.info(f"Queued attack with {city.name()}, To {target.target}, From {city.location}")

		return rtnValue

	def launchCityAttack(self, city, target: TacticalTarget, firstAttack: bool, ranged: bool, simulation):
		rangedStr = "ranged " if ranged else ""
		firstAttackStr = "initial" if firstAttack else "follow-on"
		logging.debug(f"Made {firstAttackStr} {rangedStr} attack with {city.name()} towards {target.target}")

		city.doRangeAttackAt(target.target, simulation)

	def scoreCloseOnPlots(self, target: HexPoint, landOnly: bool, simulation) -> int:
		"""Pick best hexes for closing in on an enemy city. Returns number of ranged unit plots found"""
		score: int = 0
		choiceBombardSpot: bool = False
		safeFromAttack: bool = False
		rtnValue = 0

		# We'll store the hexes we've found here
		self.tempTargets = []

		for plotPoint in target.areaWithRadius(3):
			choiceBombardSpot = False
			safeFromAttack = True

			if not simulation.valid(plotPoint):
				continue

			plotDistance = plotPoint.distance(target)
			cell = simulation.tacticalAnalysisMap().plots.values[plotPoint.y][plotPoint.x]

			if (landOnly and cell.canUseForOperationGatheringCheckWater(isWater=False)) or (
				not landOnly and cell.canUseForOperationGathering()):

				closeEnough = False

				for operationUnit in self.operationUnits:
					if closeEnough:
						continue

					unit = operationUnit.unit
					if unit is not None:
						if unit.location.distance(plotPoint) <= TacticalAI.deployRadius:
							closeEnough = True

				if closeEnough:
					score = 600 - (plotDistance * 100)

					# Top priority is hexes to bombard from (within range but not adjacent)
					if cell.isWithinRangeOfTarget() and plotDistance > 1:
						choiceBombardSpot = True
						rtnValue += 1

					if cell.isSubjectToAttack():
						score -= 30
						safeFromAttack = False

					if cell.isEnemyCanMovePast():
						score -= 30

					plot = simulation.tileAt(plotPoint)

					if plot is None:
						continue

					if simulation.cityAt(plotPoint) is not None and plot.hasOwner() and self.player == plot.owner():
						score += 100
					else:
						score += cell.defenseModifier()

					cell.setSafeDeployment(choiceBombardSpot or safeFromAttack)
					cell.setDeploymentScore(score)

					# Save this in our list of potential targets
					tempTarget = TacticalTarget(TacticalTargetType.none, target=plotPoint)
					tempTarget.threatValue = score

					# A bit of a hack -- use high priority targets to indicate good plots for ranged units
					if choiceBombardSpot:
						tempTarget.targetType = TacticalTargetType.highPriorityUnit
					else:
						tempTarget.targetType = TacticalTargetType.lowPriorityUnit

					self.tempTargets.append(tempTarget)

		return rtnValue

	def executeMoveOfBlockingUnit(self, blockingUnit, simulation):
		"""Find an adjacent hex to move a blocking unit to"""
		if blockingUnit is None:
			raise Exception('blockingUnit must not be None')

		if not isinstance_string(blockingUnit, 'Unit'):
			raise Exception(f'blockingUnit is not Unit but {type(blockingUnit)}')

		if not blockingUnit.canMove() or self.isInQueuedAttack(blockingUnit):
			return False

		oldPlot = simulation.tileAt(blockingUnit.location)

		if oldPlot is None:
			raise Exception("cant get old plot")

		for neighbor in blockingUnit.location.neighbors():
			plot = simulation.tileAt(neighbor)

			if plot is None:
				continue

			# Don't embark for one of these moves
			if not oldPlot.isWater() and plot.isWater() and blockingUnit.domain() == UnitDomainType.land:
				continue

			# Has to be somewhere we can move and be empty of other units / enemy cities
			if simulation.visibleEnemyAt(neighbor, self.player) is None and \
				simulation.visibleEnemyCityAt(blockingUnit.location, self.player) is None and \
				blockingUnit.pathTowards(plot.point, options=[], simulation=simulation) is not None:

				self.executeMoveToUnit(blockingUnit, point=neighbor, simulation=simulation)
				return True

		return False

	def isInQueuedAttack(self, blockingUnit) -> bool:
		"""Is this unit waiting to get its turn to attack?"""
		if blockingUnit is None:
			raise Exception('blockingUnit must not be None')

		if not isinstance_string(blockingUnit, 'Unit'):
			raise Exception(f'blockingUnit is not Unit but {type(blockingUnit)}')

		if len(self.queuedAttacks) > 0:
			for queuedAttack in self.queuedAttacks:
				attacker = queuedAttack.attackerUnit
				if attacker is not None:
					if attacker == blockingUnit:
						return True

		return False

	def executeMoveToUnit(self, unit, point: HexPoint, saveMoves: bool = False, simulation=None):
		"""Move unit to protect a specific tile (retrieve unit from first entry in m_CurrentMoveUnits)"""
		if simulation is None:
			raise Exception('simulation must not be None')

		# Unit already at target plot?
		if point == unit.location:
			# Fortify if possible
			if unit.canFortifyAt(point, simulation):
				unit.pushMission(UnitMission(UnitMissionType.fortify), simulation)
				# unit.fort ->SetFortifiedThisTurn(true);
			else:
				unit.pushMission(UnitMission(UnitMissionType.skip), simulation)
				if not saveMoves:
					unit.finishMoves()
		else:
			unit.pushMission(UnitMission(UnitMissionType.moveTo, target=point), simulation)
			if not saveMoves:
				unit.finishMoves()

		self.unitProcessed(unit, markTacticalMap=unit.isCombatUnit(), simulation=simulation)

	def executeBarbarianCampMove(self, point: HexPoint, simulation):
		"""Capture the gold from a barbarian camp"""
		currentMoveUnit = firstOrNone(self.currentMoveUnits)
		if currentMoveUnit is not None:
			# Move first one to target
			unit = currentMoveUnit.unit
			if unit is not None:
				unit.pushMission(UnitMission(UnitMissionType.moveTo, target=point), simulation)
				unit.finishMoves()

				# Delete this unit from those we have to move
				self.unitProcessed(unit, simulation=simulation)

		return

	def moveToEmptySpaceNearTarget(self, unit, target: HexPoint, land: bool, simulation) -> bool:
		"""Move up to our target avoiding our own units if possible"""
		# Look at spaces adjacent to target
		for neighbor in target.neighbors():
			neighborTile = simulation.tileAt(neighbor)
			if neighborTile is None:
				continue

			if neighborTile.terrain().isLand() and land:
				# Must be currently empty of friendly combat units
				# Enemies too
				occupant = simulation.unitAt(neighbor, UnitMapType.combat)

				if occupant is None:
					# And if it is a city, make sure we are friends with them, else we will automatically attack
					city = simulation.cityAt(neighbor)
					if city is None or city.player == unit.player:
						# Find a path to this space
						if unit.canReachAt(neighbor, 1, simulation):
							# Go ahead with mission
							unit.pushMission(UnitMission(UnitMissionType.moveTo, target=neighbor), simulation)
							return True

		return False

	def isTemporaryZone(self, city) -> bool:
		"""Is this a city that an operation just deployed in front of?"""
		for temporaryZone in self.temporaryZones:
			if temporaryZone.location == city.location and temporaryZone.targetType == TacticalTargetType.city:
				return True

		return False

	def plotEmergencyPurchases(self, simulation):
		"""Spend money to buy defenses"""
		# Is this a dominance zone where we're defending a city?
		zone = self.currentDominanceZone
		city = zone.closestCity
		if zone is not None and city is not None:
			if self.player == city.player and zone.territoryType == TacticalDominanceTerritoryType.friendly and zone.enemyUnitCount > 0:
				# this check is not valid for our capital
				if not city.isCapital():
					# Make sure the city isn't about to fall. Test by seeing if there are high priority unit targets
					for zoneTarget in self.zoneTargets:
						if zoneTarget.targetType != TacticalTargetType.highPriorityUnit:
							continue

						# Abandon hope for this city; save our money to use elsewhere
						return

				self.player.militaryAI.buyEmergencyBuildingIn(city, simulation)

				# If two defenders, assume already have land and sea and skip this city
				# FIXME
				if simulation.unitAt(city.location, UnitMapType.combat) is None:
					buyNavalUnit: bool = False
					buyLandUnit: bool = False
					cityDefender = simulation.unitAt(city.location, UnitMapType.combat)

					if cityDefender is not None:
						if cityDefender.domain() == UnitDomainType.land:
							if simulation.isCoastalAt(city.location):
								buyNavalUnit = True
						else:
							buyLandUnit = True
					else:
						buyLandUnit = True
						if simulation.isCoastalAt(city.location):
							buyNavalUnit = True

					if buyLandUnit:
						unit = self.player.militaryAI.buyEmergencyUnit(UnitTaskType.cityBombard, city, simulation)
						if unit is None:
							self.player.militaryAI.buyEmergencyUnit(UnitTaskType.ranged, city, simulation)

					if buyNavalUnit:
						unit = self.player.militaryAI.buyEmergencyUnit(UnitTaskType.attackSea, city, simulation)
						if unit is None:
							# Bought one, don't need to buy melee naval later
							buyNavalUnit = False

					# Always can try to buy air units
					unit = self.player.militaryAI.buyEmergencyUnit(UnitTaskType.attackAir, city, simulation)

					if unit is None:
						self.player.militaryAI.buyEmergencyUnit(UnitTaskType.defenseAir, city, simulation)

	def findClosestUnitTowards(self, target, numTurnsAway: int, mustHaveHalfHP: bool, mustBeRangedUnit: bool,
							   rangeRequired: int, needsIgnoreLineOfSight: bool, mustBeMeleeUnit: bool,
							   ignoreUnits: bool, rangedAttackTarget, simulation) -> bool:
		"""Fills m_CurrentMoveUnits with all units within X turns of a target (returns TRUE if 1 or more found)"""
		rtnValue: bool = False
		self.currentMoveUnits = []

		# Loop through all units available to tactical AI this turn
		for loopUnit in self.currentTurnUnits:
			validUnit: bool = True

			# don't use non-combat units (but consider embarked for now)
			if not loopUnit.isCombatUnit():
				validUnit = False
			elif mustHaveHalfHP and loopUnit.damage() * 2 > 100:
				validUnit = False
			elif mustBeRangedUnit and ((target.isWater() and loopUnit.domain() == UnitDomainType.land) or \
				(not target.isWater() and simulation.cityAt(target.point) is None and loopUnit.domain() == UnitDomainType.sea)):
				validUnit = False
			elif mustBeRangedUnit and not loopUnit.canAttackRanged():
				validUnit = False
			elif mustBeRangedUnit and loopUnit.range() < rangeRequired:
				validUnit = False
			elif mustBeRangedUnit and not loopUnit.canAttackRanged():
				validUnit = False
			elif mustBeRangedUnit and loopUnit.isOutOfAttacks(simulation):
				validUnit = False
			elif rangedAttackTarget is not None and mustBeRangedUnit and not self.isExpectedToDamageWithRangedAttackBy(loopUnit, rangedAttackTarget.point, simulation):
				validUnit = False
			elif needsIgnoreLineOfSight and not loopUnit.isRangeAttackIgnoreLineOfSight():
				validUnit = False
			elif mustBeMeleeUnit and loopUnit.canAttackRanged():
				validUnit = False

			distance: int = loopUnit.location.distance(target.point)

			if numTurnsAway == 0 and distance > (TacticalAI.recruitRange / 2) or numTurnsAway == 1 and distance > TacticalAI.recruitRange:
				validUnit = False

			if validUnit:
				turns = loopUnit.turnsToReach(target.point, simulation)
				if turns <= numTurnsAway:
					tacticalUnit = TacticalUnit(loopUnit, attackStrength=1000 - turns, healthPercent=100)
					tacticalUnit.movesToTarget = distance
					self.currentMoveUnits.append(tacticalUnit)

					rtnValue = True

		# Now sort them by turns to reach
		self.currentMoveUnits.sort(key=lambda a: a.movesToTarget, reverse=True)

		return rtnValue

	def isExpectedToDamageWithRangedAttackBy(self, attacker, targetLocation: HexPoint, simulation) -> bool:
		expectedDamage: int = 0
		city = simulation.cityAt(targetLocation)
		defender = simulation.unitAt(targetLocation, UnitMapType.combat)

		if city is not None:
			result = Combat.predictRangedAttack(attacker, city, simulation)
			expectedDamage = result.defenderDamage
		elif defender is not None:
			result = Combat.predictRangedAttack(attacker, defender, simulation)
			expectedDamage = result.defenderDamage

		return expectedDamage > 0

	def executePillageAt(self, point: HexPoint, simulation):
		"""Pillage an undefended improvement"""
		# Move first one to target
		currentMoveUnit = firstOrNone(self.currentMoveUnits)
		if currentMoveUnit is not None:
			unit = currentMoveUnit.unit
			if unit is not None:
				unit.pushMission(UnitMission(UnitMissionType.moveTo, buildType=None, target=point), simulation)
				unit.pushMission(UnitMission(UnitMissionType.pillage), simulation)
				unit.finishMoves()

				# Delete this unit from those we have to move
				self.unitProcessed(unit, simulation=simulation)

		return

	def executeBarbarianCivilianEscortMove(self, simulation):
		"""Move Barbarian civilian to a camp (with escort if possible)"""
		for civilianMoveUnit in self.currentMoveUnits:
			civilian = civilianMoveUnit.unit

			if civilian is None:
				continue

			target = self.findNearbyTargetFor(civilian, sys.maxsize,TacticalTargetType.barbarianCamp, noLikeUnit=civilian, simulation=simulation)
			if target is not None:
				# If we're not there yet, we have work to do
				current: HexPoint = civilian.location
				if current == target:
					civilian.finishMoves()
					self.unitProcessed(civilian, simulation=simulation)
				else:
					escortUnit = None

					loopUnit = simulation.unitAt(current, UnitMapType.combat)
					if loopUnit is not None:
						if civilian.player == loopUnit.player:
							escortUnit = loopUnit

					# Handle case of no path found at all for civilian
					path = civilian.pathTowards(target, options=[], simulation=simulation)
					if path is not None:
						civilianMove: Optional[HexPoint] = lastOrNone(path.points())

						# Can we reach our target this turn?
						if civilianMove == target:
							# See which defender is stronger
							if escortUnit is not None:
								self.executeMoveUnitToPlot(escortUnit, civilianMove, simulation=simulation)
								self.executeMoveUnitToPlot(civilian, civilianMove, simulation=simulation)
							else:
								self.executeMoveUnitToPlot(civilian, civilianMove, simulation=simulation)
						elif escortUnit is None:
							# Can't reach target and don't have escort...
							self.executeMoveUnitToPlot(civilian, civilianMove, simulation=simulation)
						else:
							# Can't reach target and DO have escort...
							# See if escort can move to the same location in one turn
							if escortUnit is not None:
								if escortUnit.turnsToReach(civilianMove, simulation=simulation) <= 1:
									self.executeMoveUnitToPlot(escortUnit, civilianMove, simulation=simulation)
									self.executeMoveUnitToPlot(civilian, civilianMove, simulation=simulation)
								else:
									# See if friendly blocking unit is ending the turn there, or if no blocking unit (which indicates this is somewhere civilian
									# can move that escort can't), then find a new path based on moving the escort
									blockingUnit = simulation.unitAt(civilianMove, UnitMapType.combat)
									if blockingUnit is not None:
										# Looks like we should be able to move the blocking unit out of the way
										if self.executeMoveOfBlockingUnit(blockingUnit, simulation=simulation):
											self.executeMoveUnitToPlot(escortUnit, civilianMove, simulation=simulation)
											self.executeMoveUnitToPlot(civilian, civilianMove, simulation=simulation)
										else:
											civilian.finishMoves()
											escortUnit.finishMoves()
									else:
										path = civilian.pathTowards(target, options=[], simulation=simulation)
										if path is not None:
											escortMove: Optional[HexPoint] = lastOrNone(path.points())
											# See if civilian can move to the same location in one turn
											if civilian.turnsToReach(escortMove, simulation=simulation) <= 1:
												self.executeMoveUnitToPlot(escortUnit, escortMove, simulation=simulation)
												self.executeMoveUnitToPlot(civilian, escortMove, simulation=simulation)
											else:
												civilian.finishMoves()
												escortUnit.finishMoves()
										else:
											civilian.finishMoves()
											escortUnit.finishMoves()
					else:
						civilian.finishMoves()
						if escortUnit is not None:
							escortUnit.finishMoves()

		return

	def executeHeals(self, simulation):
		"""Heal chosen units"""
		for currentMoveUnit in self.currentMoveUnits:
			unit = currentMoveUnit.unit
			if unit is None:
				continue

			if unit.canFortifyAt(unit.location, simulation):
				unit.pushMission(UnitMission(UnitMissionType.fortify), simulation)
				unit.setFortifiedThisTurn(True, simulation)
			else:
				unit.pushMission(UnitMission(UnitMissionType.skip), simulation)

			self.unitProcessed(unit, simulation=simulation)

		return

	def executeNavalFormationMoves(self, army, musterPosition: HexPoint, simulation):
		"""Complete moves for all units requested through calls to MoveWithFormation()"""
		moreEscorted: bool = True

		if len(self.operationUnits) == 0:
			return

		iNavalUnits: int = 0
		iEscortedUnits: int = 0
		for operationUnit in self.operationUnits:
			opUnit = operationUnit.unit
			if opUnit is not None:
				if opUnit.domain() == UnitDomainType.land:
					iEscortedUnits += 1
				elif opUnit.isGreatAdmiral():
					iEscortedUnits += 1
				else:
					iNavalUnits += 1

		iMostUnits = max(iNavalUnits, iEscortedUnits)
		iLeastUnits = min(iNavalUnits, iEscortedUnits)
		if iNavalUnits > iEscortedUnits:
			moreEscorted = False

		# Range around turn target based on number of units we need to place
		iRange = OperationHelpers.gatherRangeFor(iMostUnits)

		# See if we have enough places to put everyone
		if (not self.scoreDeploymentPlots(musterPosition, army, iMostUnits, 0, iRange, simulation) and
			not self.scoreDeploymentPlots(musterPosition, army, iMostUnits, 0, 3, simulation)):
			logging.debug(f"Operation aborting. Army ID: {army}. Not enough spaces to deploy near turn target")
			army.operation.state = OperationStateType.aborted
			army.operation.stateReason = OperationStateReason.noRoomDeploy
		# Compute moves for whomever has more units first
		else:
			self.tempTargets.sort()
			self.potentialBlocks = []
			done = False
			iMostUnitsToPlace: int = iMostUnits

			for tempTarget in self.tempTargets:
				if done:
					continue

				if self.findClosestNavalOperationUnit(tempTarget.target, moreEscorted, simulation):
					for currentMoveUnit in self.currentMoveUnits:
						block = BlockingUnit(currentMoveUnit.unit, tempTarget.target, len(self.currentMoveUnits), currentMoveUnit.movesToTarget)
						self.potentialBlocks.append(block)

					iMostUnitsToPlace -= 1
					if iMostUnitsToPlace == 0:
						done = True

			# Now ready to make the assignments
			self.assignDeployingUnits(iMostUnits - iMostUnitsToPlace, simulation)
			self.performChosenMoves(2, simulation)

			# Log if someone in army didn't get a move assigned (how do we address this in the future?)
			if len(self.chosenBlocks) < iMostUnits:
				logging.debug(f"No naval deployment move for {iMostUnits - len(self.chosenBlocks)} units in first pass")

			if iLeastUnits > 0:
				# Now repeat for the other type of units, using the same target plots
				self.tempTargets = []

				for chosenBlock in self.chosenBlocks:
					temp = TacticalTarget(target=chosenBlock.point)
					self.tempTargets.append(temp)

				self.potentialBlocks = []
				done = False
				iLeastUnitsToPlace = iLeastUnits

				for tempTarget in self.tempTargets:
					if done:
						continue

					if self.findClosestNavalOperationUnit(tempTarget.target, not moreEscorted, simulation):
						for currentMoveUnit in self.currentMoveUnits:
							block = BlockingUnit(currentMoveUnit.unit, tempTarget.target, len(self.currentMoveUnits),
							                     currentMoveUnit.movesToTarget)
							self.potentialBlocks.append(block)

						iLeastUnitsToPlace -= 1
						if iLeastUnitsToPlace == 0:
							done = True

				# Now ready to make the assignments
				self.assignDeployingUnits(iLeastUnits - iLeastUnitsToPlace, simulation)
				self.performChosenMoves(2, simulation)

				if len(self.chosenBlocks) < iLeastUnits:
					logging.debug(f"No naval deployment move for {iLeastUnits - len(self.chosenBlocks)} units in second pass", )

		return

	def findClosestNavalOperationUnit(self, target: HexPoint, escortedUnits: bool, simulation) -> bool:
		"""Fills currentMoveUnits with all units in naval operation that can get to target (returns TRUE if 1 or more found)"""
		rtnValue: bool = False
		self.currentMoveUnits = []

		# Loop through all units available to operation
		for operationUnit in self.operationUnits:
			loopUnit = operationUnit.unit
			if loopUnit is not None:
				validUnit = True

				if escortedUnits and (not loopUnit.isGreatAdmiral() and loopUnit.domain() != UnitDomainType.land):
					validUnit = False

				if not escortedUnits and (loopUnit.domain() != UnitDomainType.sea or loopUnit.isGreatAdmiral()):
					validUnit = False

				if validUnit:
					turns = loopUnit.turnsToReach(target, simulation)

					if turns != sys.maxsize:
						unit = TacticalUnit(loopUnit, 1000-turns, 100)
						unit.movesToTarget = target.distance(loopUnit.location)
						self.currentMoveUnits.append(unit)
						rtnValue = True

		# Now sort them by turns to reach
		self.currentMoveUnits.sort()

		return rtnValue

	def plotHedgehogMoves(self, simulation):
		"""Build a defensive shell around this city"""
		# Attack priority unit targets
		for zoneTarget in self.zoneTargets:
			if (zoneTarget.targetType == TacticalTargetType.highPriorityUnit or
		        zoneTarget.targetType == TacticalTargetType.mediumPriorityUnit):
				if zoneTarget.isTargetStillAliveFor(self.player):
					self.executePriorityAttacksOnUnitTarget(zoneTarget, simulation)

		self.plotDestroyUnitMoves(TacticalTargetType.highPriorityUnit, True, simulation=simulation)
		self.plotDestroyUnitMoves(TacticalTargetType.mediumPriorityUnit, True, simulation=simulation)

		# But after best attacks are exhausted, go right to playing defense
		zone: Optional[TacticalDominanceZone] = simulation.tacticalAnalysisMap().zoneAt(self.currentZoneIndex)
		if zone.closestCity is not None:
			target = TacticalTarget(TacticalTargetType.city, zone.closestCity.location, zone.closestCity.player.leader, zone)
			self.executeHedgehogDefense(target, zone)

		return

	def executePriorityAttacksOnUnitTarget(self, target: TacticalTarget, simulation):
		"""Bombard and flank attacks (whatever is applicable) against a unit target"""
		attackUnderway: bool = False
		attackMade: bool = False
		# pTarget = GC.getMap().plot(kTarget.GetTargetX(), kTarget.GetTargetY());

		# Try to find a bombard first
		simulation.tacticalAnalysisMap().clearDynamicFlags()
		simulation.tacticalAnalysisMap().setTargetBombardCells(target, simulation.tacticalAnalysisMap().bestFriendlyRange(), simulation.tacticalAnalysisMap().ignoreLineOfSight)

		if target.isTargetStillAliveFor(self.player, simulation):
			attackUnderway = self.executeSafeBombardsOn(target, simulation)

		if target.isTargetStillAliveFor(self.player, simulation):
			self.executeProtectedBombards(target, attackUnderway, simulation)

		# Then try for a flank attack
		if target.isTargetStillAliveFor(self.player, simulation):
			simulation.tacticalAnalysisMap().clearDynamicFlags()
			simulation.tacticalAnalysisMap().setTargetFlankBonusCells(target)

			bAttackMade = self.executeFlankAttackOn(target)
			if attackMade:
				attackUnderway = True

		return

	def executeFlankAttackOn(self, target: TacticalTarget, simulation) -> bool:
		"""Take a multi-hex attack on an enemy unit this turn"""
		iPossibleFlankHexes: int = 0

		# Count number of possible flank attack spaces around target
		for neighborPoint in target.target.neighbors():
			if not simulation.valid(neighborPoint):
				continue

			cell = simulation.tacticalAnalysisMap().plots.values[neighborPoint.y][neighborPoint.x]

			if cell.isHelpsProvidesFlankBonus():
				iPossibleFlankHexes += 1

		# If more than 1, find how many we can fill with units
		if iPossibleFlankHexes > 1:
			iFillableHexes: int = 0
			iNumAttackers: int = 0
			self.tempTargets = []
			for neighborPoint in target.target.neighbors():
				if not simulation.valid(neighborPoint):
					continue

				cell = simulation.tacticalAnalysisMap().plots.values[neighborPoint.y][neighborPoint.x]
				loopPlot = simulation.tileAt(neighborPoint)

				if cell.isHelpsProvidesFlankBonus():
					if self.findClosestUnitTowards(loopPlot, numTurnsAway=0, mustHaveHalfHP=True, mustBeRangedUnit=False,
					                               rangeRequired=0, needsIgnoreLineOfSight=False, mustBeMeleeUnit=False,
					                               ignoreUnits=True, rangedAttackTarget=None, simulation=simulation):
						iFillableHexes += 1
						iNumAttackers += 1
						target = TacticalTarget(TacticalTargetType.none, neighborPoint)
						self.tempTargets.append(target)
					# What about next turn?
					elif self.findClosestUnitTowards(loopPlot, numTurnsAway=1, mustHaveHalfHP=False, mustBeRangedUnit=False,
					                                 rangeRequired=0, needsIgnoreLineOfSight=False, mustBeMeleeUnit=False,
					                                 ignoreUnits=True, rangedAttackTarget=None, simulation=simulation):
						iFillableHexes += 1
						target = TacticalTarget(TacticalTargetType.none, neighborPoint)
						self.tempTargets.append(target)

			# As long as we either get three hexes filled with one attacker, or two we can attack from, then this multi-hex attack is worth considering
			if (iNumAttackers >= 1 and iFillableHexes >= 3) or iNumAttackers >= 2:
				# Compute best way to fill the hexes
				self.potentialBlocks = []
				for tempTarget in self.tempTargets:
					loopPlot = simulation.tileAt(tempTarget.target)

					if not self.findClosestUnitTowards(loopPlot, numTurnsAway=1, mustHaveHalfHP=False, mustBeRangedUnit=False,
					                                   rangeRequired=0, needsIgnoreLineOfSight=False, mustBeMeleeUnit=True,
					                                   ignoreUnits=True, rangedAttackTarget=None, simulation=simulation):
						iFillableHexes -= 1
						if iFillableHexes < 2:
							return False
					else:
						# Save off the units that could get here
						for currentMoveUnit in self.currentMoveUnits:
							block = BlockingUnit(currentMoveUnit.unit, tempTarget.target, len(self.currentMoveUnits), currentMoveUnit.movesToTarget)
							self.potentialBlocks.append(block)

				if self.assignFlankingUnits(iFillableHexes):
					# Make moves up into hexes
					for chosenBlock in self.chosenBlocks:
						unit = chosenBlock.unit

						if unit is not None:
							if unit.location == chosenBlock.point:
								logging.debug(f"Already in a flanking position with {unit.name()}, {chosenBlock.point}")
							else:
								unit.pushMission(UnitMission(UnitMissionType.moveTo, target=chosenBlock.point), simulation)
								logging.debug(f"Moving into a flanking position with {unit.name()}, {chosenBlock.point}")

								if unit.moves() <= 0:
									self.unitProcessed(unit, simulation=simulation)

					# Make attacks
					defender = simulation.unitAt(target.target, UnitMapType.combat)
					if defender is not None and self.player.isAtWarWith(defender.player):
						target.damage = defender.damage()
						self.currentMoveCities = []

						if self.findUnitsWithinStrikingDistanceTowards(target.target, numTurnsAway=1, noRangedUnits=False, simulation=simulation):
							targetPlot = simulation.tileAt(target.target)
							self.computeTotalExpectedDamage(target, targetPlot, simulation)
							self.executeAttack(target, targetPlot, inflictWhatWeTake=False, mustSurviveAttack=True, simulation=simulation)

		return False

	def executeFleetMoveToTarget(self, army, targetPlot, simulation):
		"""Move a squadron of naval units to a target"""
		# Request moves for all units
		for index, formationEntry in enumerate(army.formationEntries):
			unit = formationEntry.unit
			slotEntry: UnitFormationSlot = army.formation.slots()[index]
			if unit is not None and not unit.processedInTurn():
				formationEntry.startedOnOperation = True
				self.moveWithFormation(unit, slotEntry.position)

		self.executeNavalFormationMoves(army, targetPlot, simulation)
	