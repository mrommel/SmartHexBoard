import logging
from typing import Optional, List

from smarthexboard.smarthexboardlib.game.combat import Combat, CombatResultType
from smarthexboard.smarthexboardlib.game.states.builds import BuildType
from smarthexboard.smarthexboardlib.game.states.ui import PopupType
from smarthexboard.smarthexboardlib.game.unitTypes import UnitMissionType, MoveOption, UnitActivityType, UnitTaskType, UnitMapType
from smarthexboard.smarthexboardlib.map.base import HexPoint
from smarthexboard.smarthexboardlib.map.path_finding.path import HexPath
from smarthexboard.smarthexboardlib.map.types import UnitDomainType


class UnitMission:
	def __init__(self, missionType: UnitMissionType, buildType: Optional[BuildType] = None,
				 target: Optional[HexPoint] = None, path: Optional[HexPath] = None,
				 options: List[MoveOption] = []):

		self.missionType: UnitMissionType = missionType
		self.buildType: Optional[BuildType] = buildType
		self.target: Optional[HexPoint] = target
		self.path: Optional[HexPath] = path
		self.options: List[MoveOption] = options
		self.unit = None

		self.startedInTurn: int = -1

		if missionType.needsTarget() and (target is None and path is None):
			raise Exception(f"mission of type {missionType} need target or path")

	def start(self, simulation):
		"""Initiate a mission"""
		self.startedInTurn = simulation.currentTurn

		delete = False
		notify = False
		action = False

		if self.unit.canMove():
			self.unit.setActivityType(UnitActivityType.mission, simulation)
		else:
			self.unit.setActivityType(UnitActivityType.hold, simulation)

		if not self.unit.canStartMission(self, simulation):
			delete = True
		else:
			if self.missionType == UnitMissionType.skip:
				self.unit.setActivityType(UnitActivityType.hold, simulation)
				delete = True
			elif self.missionType == UnitMissionType.sleep:
				self.unit.setActivityType(UnitActivityType.sleep, simulation)
				delete = True
				notify = True
			elif self.missionType == UnitMissionType.fortify:
				self.unit.setActivityType(UnitActivityType.sleep, simulation)
				delete = True
				notify = True
			elif self.missionType == UnitMissionType.heal:
				self.unit.setActivityType(UnitActivityType.heal, simulation)
				delete = True
				notify = True

			if self.unit.canMove():

				if self.missionType == UnitMissionType.fortify or self.missionType == UnitMissionType.heal or \
					self.missionType == UnitMissionType.alert or self.missionType == UnitMissionType.skip:

					self.unit.setFortifiedThisTurnTo(True, simulation)

					# start the animation right now to give feedback to the player
					if not self.unit.isFortified() and not self.unit.hasMoved(simulation) and \
						self.unit.canFortifyAt(self.unit.location, simulation):
						simulation.userInterface.refreshUnit(self.unit)
				elif self.unit.isFortified():
					# unfortify for any other mission
					simulation.userInterface.refreshUnit(self.unit)

				# ---------- now the real missions with action -----------------------

				if self.missionType == UnitMissionType.embark or self.missionType == UnitMissionType.disembark:
					action = True

				# FIXME nuke, paradrop, airlift
				elif self.missionType == UnitMissionType.rebase:
					if self.unit.doRebaseTo(self.target):
						action = True
				elif self.missionType == UnitMissionType.rangedAttack:
					if not self.unit.canRangeStrikeAt(self.target, needWar=False, noncombatAllowed=False, simulation=simulation):
						# Invalid, delete the mission
						delete = True
				elif self.missionType == UnitMissionType.pillage:
					if self.unit.doPillage(simulation):
						action = True
				elif self.missionType == UnitMissionType.found:
					if self.unit.doFoundWith(None, simulation):
						action = True

		if action and self.unit.player.isHuman():
			timer = self.calculateMissionTimerFor(self.unit)
			self.unit.setMissionTimerTo(timer)

		if delete:
			self.unit.popMission()
		elif self.unit.activityType() == UnitActivityType.mission:
			self.continueMission(steps=0, simulation=simulation)

		return

	def calculateMissionTimerFor(self, unit, steps: int = 0) -> int:
		"""
			---------------------------------------------------------------------------
			Update the mission timer to a new value based on the mission (or lack thereof) in the queue
			KWG: The mission timer controls when the next time the unit's mission will be checked, not
				in absolute time, but in passes through the Game Core update loop.  Previously,
				this was used to delay processing so that the user could see the visualization of
				units.  The Game Core no longer deals with visualization timing, but this system is
				still used to keep the units sequencing their missions with each other.
				i.e. each unit will get a chance to complete a mission segment, rather than a unit
				exhausting its mission queue all in one go.
		"""
		peekMission = unit.peekMission()

		if not unit.player.isHuman():
			time = 0
		elif peekMission is not None:
			time = 1

			if peekMission.missionType == UnitMissionType.moveTo:  # or peekMission.type ==.routeTo or peekMission.type ==.moveToUnit

				# targetPlot: Optional[HexPoint] = None
				# / * if peekMission.type ==.moveToUnit
				# {
				# 	pTargetUnit = GET_PLAYER((PlayerTypes)
				# kMissionData.iData1).getUnit(kMissionData.iData2);
				# if (pTargetUnit) {
				# pTargetPlot = pTargetUnit->plot();
				# } else {
				# pTargetPlot = NULL;
				# }
				# } else {* /
				targetPlot = peekMission.target

				if targetPlot is not None and unit.location == targetPlot:
					time += steps
				else:
					time = min(time, 2)

			if unit.player.isHuman() and unit.isAutomated():
				time = min(time, 1)
		else:
			time = 0

		return time

	def continueMission(self, steps: int, simulation):
		continueMissionRestart = True  # to make this function no longer recursive
		while continueMissionRestart:

			continueMissionRestart = False
			done = False  # are we done with mission?
			action = False  # are we taking an action this turn?

			if self.startedInTurn == simulation.currentTurn:

				if self.missionType == UnitMissionType.moveTo and self.unit.canMove():

					if self.target is not None:
						tile = simulation.tileAt(self.target)

						# configs
						cityAttackInterrupt = True  # gDLL->GetAdvisorCityAttackInterrupt();
						badAttackInterrupt = True  # gDLL->GetAdvisorBadAttackInterrupt();

						if self.unit.player.isHuman() and badAttackInterrupt:

							if self.unit.canMoveInto(self.target, [MoveOption.attack], simulation) and \
								tile.isDiscoveredBy(self.unit.player):

								if tile.isCity():
									if cityAttackInterrupt:
										# show tutorial
										if simulation.showTutorialInfos():
											# do city alert
											city = simulation.cityAt(self.target)
											simulation.userInterface.showPopup(PopupType.tutorialCityAttack, attacker=self.unit, city=city)
											return
								elif badAttackInterrupt:
									defender = simulation.visibleEnemyAt(self.target, self.unit.player)

									if defender is not None:

										result = Combat.predictMeleeAttack(self.unit, defender, simulation)
										if result.value == CombatResultType.totalDefeat or result.value == CombatResultType.majorDefeat:
											# show tutorial
											if simulation.showTutorialInfos():
												simulation.userInterface.showPopup(PopupType.tutorialBadUnitAttack, attacker=self.unit, defender=defender)
												return

						if self.unit.doAttackInto(self.target, steps=steps, simulation=simulation):
							done = True

			# If there are units in the selection group, they can all move, and we're not done \
			#   then try to follow the mission
			if not done and self.unit.canMove():

				if self.missionType == UnitMissionType.moveTo or self.missionType == UnitMissionType.embark or \
					self.missionType == UnitMissionType.disembark:

					if self.unit.domain() == UnitDomainType.air:
						if self.unit.doMoveOnPathTowards(self.target, previousETA=0, buildingRoute=False, simulation=simulation) > 0:
							done = True
					else:
						cost = self.unit.doMoveOnPathTowards(self.target, previousETA=0, buildingRoute=False, simulation=simulation)

						if cost > self.unit.movesLeft():
							action = True
						else:
							done = True

				elif self.missionType == UnitMissionType.routeTo:
					oldLocation = self.unit.location
					movesToDo = self.unit.doMoveOnPathTowards(self.target, previousETA=0, buildingRoute=False, simulation=simulation)

					if movesToDo > 0:
						action = True
					else:
						action = oldLocation != self.target
						done = True

				elif self.missionType == UnitMissionType.followPath:

					if self.path is None:
						raise Exception("we need a path to follow")

					currentIndexInPath: Optional[int] = self.path.firstIndexOf(self.unit.location)
					if currentIndexInPath is not None:
						if currentIndexInPath + 1 < len(self.path.points()):
							nextPoint: HexPoint = self.path.points()[currentIndexInPath + 1]
						else:
							nextPoint: HexPoint = self.path.points()[currentIndexInPath]

						movesToDo = self.unit.doMoveOnPathTowards(nextPoint, previousETA=0, buildingRoute=False, simulation=simulation)

						if movesToDo > 0:
							action = True

						done = self.path.points()[-1] == self.unit.location

					else:
						logging.debug("cant find current position in path - move to start")

						startPoint = self.path.points()[0]
						movesToDo = self.unit.doMoveOnPathTowards(startPoint, previousETA=0, buildingRoute=False, simulation=simulation)

						if movesToDo > 0:
							action = True

						done = self.path.points()[-1] == startPoint

				elif self.missionType == UnitMissionType.swapUnits:

					# Get target plot
					unit2 = simulation.unitAt(self.target, UnitMapType.combat)
					if unit2 is not None:
						if unit2.hasSameTypeAs(self.unit) and unit2.readyToMove():
							# Start the swap
							self.unit.doMoveOnPathTowards(unit2.location, previousETA=0, buildingRoute=False, simulation=simulation)

							# Move the other unit back out
							unit2.doMoveOnPathTowards(self.unit.location, previousETA=0, buildingRoute=False, simulation=simulation)

							done = True
					else:
						action = False
						done = True
						break

				elif self.missionType == UnitMissionType.moveToUnit:
					targetUnit = simulation.unitAt(self.target, UnitMapType.combat)
					if targetUnit is not None:

						if self.unit.hasTask(UnitTaskType.shadow) and self.missionType != UnitMissionType.group:
							# FIXME: this seems to be wrong
							pass

						if self.unit.doMoveOnPathTowards(targetUnit.location, previousETA=0, buildingRoute=False, simulation=simulation) > 0:
							action = True
						else:
							done = True
					else:
						done = True

				elif self.missionType == UnitMissionType.garrison:
					if self.target is None:
						targetCity = simulation.cityAt(self.target)
						if targetCity is not None:
							# check to see if the city exists, is on our team, and does not have a garrisoned unit
							if targetCity.player.leader != self.unit.player.leader or \
									simulation.unitAt(self.target, UnitMapType.combat) is not None:
								action = False
								done = True
								break

							# are we there yet
							if self.unit.location != self.target:
								if self.unit.doMoveOnPathTowards(self.target, previousETA=0, buildingRoute=False, simulation=simulation) > 0:
									action = True
								else:
									done = True

				elif self.missionType == UnitMissionType.rangedAttack:
					if self.unit.doRangeAttackAt(self.target, simulation):
						done = True

				elif self.missionType == UnitMissionType.build:
					if not self.unit.continueBuilding(self.buildType, simulation):
						done = True

			# slewis - I added this because garrison should not consume any moves, and the logic above checks to see
			# if there are any moves available
			if not done:
				if self.missionType == UnitMissionType.garrison:
					if self.target is None:
						self.target = self.unit.location

					targetCity = simulation.cityAt(self.target)
					if targetCity is not None:
						# check to see if the city exists, is on our team, and does not have a garrisoned unit
						if targetCity.player.leader != self.unit.player.leader:
							action = False
							done = True
							break

						# are we there yet?
						if self.unit.location == self.target:
							self.unit.doGarrison(simulation)
							self.unit.setActivityType(UnitActivityType.sleep, simulation)  # sleep here after we complete the mission
							action = True

			# check to see if mission is done
			if not done:
				if self.missionType == UnitMissionType.moveTo or self.missionType == UnitMissionType.swapUnits or \
					self.missionType == UnitMissionType.embark or self.missionType == UnitMissionType.disembark:
					if self.unit.location == self.target:
						done = True

				elif self.missionType == UnitMissionType.routeTo:
					if self.unit.location == self.target:
						done = True

				elif self.missionType == UnitMissionType.moveToUnit:
					oppositeType: UnitMapType = UnitMapType.combat if self.unit.unitClassType() == UnitMapType.civilian else UnitMapType.civilian
					targetUnit = simulation.unitAt(self.target, oppositeType)
					if targetUnit is not None:
						if targetUnit.location == self.unit.location:
							done = True

				elif self.missionType == UnitMissionType.garrison:
					# if the garrison is called from a stationary unit (one just built in a city) then the locations will be -1.
					# If the garrison action is directed from outside the city, then it will be the plot of the city.
					if (self.target is None or self.target == self.unit.location) and self.unit.isGarrisoned():
						done = True

				elif self.missionType == UnitMissionType.rebase or self.missionType == UnitMissionType.rangedAttack or \
					self.missionType == UnitMissionType.pillage or self.missionType == UnitMissionType.found:
					done = True

			# if there is an action, if it's done or there are not moves left, and a player is watching, watch the movement
			if action and (done or not self.unit.canMove()):
				# self.updateMissionTimer(hUnit, steps)
				pass

			if done:
				# Was unit.IsBusy(), but it's ok to clear the mission if the unit is just completing a move visualization
				if self.unit.missionTimer() == 0:
					self.unit.publishQueuedVisualizationMoves(simulation)
					self.unit.popMission()

				# trader has reached a target but has moves left
				if self.unit.isTrading() and self.unit.movesLeft() > 0:
					self.unit.continueTrading(simulation)
					self.unit.finishMoves()
			else:
				# if we can still act, process the mission again
				if self.unit.canMove():
					# steps *= 1
					continueMissionRestart = True  # keep looping
				elif not self.unit.isBusy():
					# GC.GetEngineUserInterface()->changeCycleSelectionCounter(1);
					pass

		return
