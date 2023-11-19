import random
from typing import Optional

from smarthexboard.smarthexboardlib.game.baseTypes import ArtifactType
from smarthexboard.smarthexboardlib.game.civilizations import CivilizationType, LeaderType
from smarthexboard.smarthexboardlib.game.notifications import NotificationType
from smarthexboard.smarthexboardlib.game.unitTypes import UnitTaskType, UnitType
from smarthexboard.smarthexboardlib.game.units import Unit
from smarthexboard.smarthexboardlib.map.base import Array2D, HexArea, HexPoint
from smarthexboard.smarthexboardlib.map.improvements import ImprovementType
from smarthexboard.smarthexboardlib.map.map import Tile
from smarthexboard.smarthexboardlib.map.types import UnitMovementType, FeatureType
from smarthexboard.smarthexboardlib.utils.base import isinstance_string


class BarbarianAI:
	def __init__(self, simulation):
		if isinstance_string(simulation, 'GameModel'):
			mapSize = simulation.mapSize()
			self._barbCampSpawnCounter = Array2D(mapSize.size())
			self._barbCampSpawnCounter.fill(-1)
			self._barbCampNumUnitsSpawned = Array2D(mapSize.size())
			self._barbCampNumUnitsSpawned.fill(-1)
		elif isinstance(simulation, dict):
			barbarian_dict: dict = simulation
			width: int = len(barbarian_dict['_barbCampSpawnCounter'][0])
			height: int = len(barbarian_dict['_barbCampSpawnCounter'])
			self._barbCampSpawnCounter = Array2D(width, height)
			self._barbCampNumUnitsSpawned = Array2D(width, height)

			for y in range(height):
				for x in range(width):
					self._barbCampSpawnCounter.values[y][x] = barbarian_dict['_barbCampSpawnCounter'][y][x]
					self._barbCampNumUnitsSpawned.values[y][x] = barbarian_dict['_barbCampNumUnitsSpawned'][y][x]
					pass

	def doTurn(self, simulation):
		"""Called every turn
		CvBarbarians::BeginTurn()"""
		mapSize = simulation.mapSize().size()

		for x in range(mapSize.width()):
			for y in range(mapSize.height()):
				if self._barbCampSpawnCounter.values[y][x] > 0:
					# No Camp here anymore
					plot = simulation.tileAt(x, y)

					if plot.hasImprovement(ImprovementType.barbarianCamp):
						self._barbCampSpawnCounter.values[y][x] -= 1
					else:
						self._barbCampSpawnCounter.values[y][x] -= 1
						self._barbCampNumUnitsSpawned.values[y][x] = -1
				elif self._barbCampSpawnCounter.values[y][x] < -1:
					# Counter is negative, meaning a camp was cleared here recently and isn't allowed to respawn
					# in the area for a while
					self._barbCampSpawnCounter.values[y][x] += 1

	def doCamps(self, simulation):
		"""CvBarbarians::DoCamps()"""
		barbarianPlayer = simulation.barbarianPlayer()

		numCampsInExistence = 0
		numNotVisiblePlots = 0
		numValidCampPlots = 0
		alwaysRevealedBarbCamp = False

		# Figure out how many Non-visible tiles we have to base # of camps to spawn on
		mapSize = simulation.mapSize()

		for x in range(mapSize.size().width()):
			for y in range(mapSize.size().height()):
				loopPlot = simulation.tileAt(x, y)
				# See how many camps we already have
				if loopPlot.hasImprovement(ImprovementType.barbarianCamp):
					numCampsInExistence += 1

				if not loopPlot.isWater():
					if not loopPlot.isVisibleToAny():
						numNotVisiblePlots += 1

		numValidCampPlots = numNotVisiblePlots

		fogTilesPerBarbarianCamp = mapSize.fogTilesPerBarbarianCamp()
		campTargetNum = numValidCampPlots / fogTilesPerBarbarianCamp if (fogTilesPerBarbarianCamp != 0) else 0
		numCampsToAdd = campTargetNum - numCampsInExistence

		# added the barbarian chance for the FoR scenario
		if numCampsToAdd > 0:
			# First turn of the game add 1 / 3 of the Target number of Camps
			if simulation.currentTurn == 0:
				numCampsToAdd *= 33  # BARBARIAN_CAMP_FIRST_TURN_PERCENT_OF_TARGET_TO_ADD
				numCampsToAdd /= 100
			else:
				# Every other turn of the game there's a 1 in 2 chance of adding a new camp
				if random.uniform(0.0, 1.0) > 0.5:
					numCampsToAdd = 1
				else:
					numCampsToAdd = 0

			# Don't want to get stuck in an infinite or almost so loop
			count = 0
			numLandPlots = simulation.numberOfLandPlots()

			# Do a random roll to bias in favor of Coastal land Tiles so that the Barbs will spawn Boats:) - required 1 / 6 of the time
			wantsCoastal = random.randint(0, 6) == 0  # BARBARIAN_CAMP_COASTAL_SPAWN_ROLL

			playerCapitalMinDistance = 4  # BARBARIAN_CAMP_MINIMUM_DISTANCE_CAPITAL
			barbCampMinDistance = 7  # BARBARIAN_CAMP_MINIMUM_DISTANCE_ANOTHER_CAMP
			maxDistanceToLook = playerCapitalMinDistance if playerCapitalMinDistance > barbCampMinDistance else barbCampMinDistance

			# Find Plots to put the Camps
			while numCampsToAdd > 0 and count < numLandPlots:
				count += 1

				plotLocation = simulation.randomLocation()
				loopPlot: Optional[Tile] = simulation.tileAt(plotLocation)

				if loopPlot is None:
					continue

				# Plot must be valid(not Water, nonvisible)
				if not loopPlot.isWater():
					if not loopPlot.isImpassable(UnitMovementType.walk) and not loopPlot.hasFeature(FeatureType.mountains):
						if not loopPlot.hasOwner() and not loopPlot.isVisibleToAny():
							# NO RESOURCES FOR NOW, MAY REPLACE WITH SOMETHING COOLER
							if loopPlot.hasAnyResourceFor(None):
								# No camps on 1 - tile islands
								loopPlotArea: Optional[HexArea] = loopPlot.area()
								if loopPlotArea is not None and len(loopPlotArea.points()) > 1:

									if simulation.isCoastalAt(loopPlot.point) or not wantsCoastal:

										# Max Camps for this area
										maxCampsThisArea = campTargetNum * len(loopPlot.area().points()) / numLandPlots
										# Add 1 just in case the above algorithm rounded something off
										maxCampsThisArea += 1

										# Already enough Camps in this Area?
										if loopPlot.area().numberOfImprovements(ImprovementType.barbarianCamp, simulation) <= maxCampsThisArea:
											# Don't look at Tiles that already have a Camp
											if not loopPlot.hasAnyImprovement():
												# Don't look at Tiles that can't have an improvement
												if not loopPlot.hasAnyFeature() or not loopPlot.feature().isNoImprovement():
													somethingTooClose = False

													# Look at nearby Plots to make sure another camp isn't too close
													for nearbyCampLocation in plotLocation.areaWithRadius(maxDistanceToLook):

														nearbyCampPlot = simulation.tileAt(nearbyCampLocation)
														if nearbyCampPlot is None:
															continue

														plotDistance = nearbyCampLocation.distance(plotLocation)

														# Can't be too close to a player
														if plotDistance <= playerCapitalMinDistance:
															if nearbyCampPlot.isCity():
																nearbyCity = simulation.cityAt(nearbyCampPlot.point)
																if nearbyCity is not None:
																	if nearbyCity.isCapital():
																		somethingTooClose = True
																		break

														# Can't be too close to another Camp
														if plotDistance <= barbCampMinDistance:
															if nearbyCampPlot.hasImprovement(ImprovementType.barbarianCamp):
																somethingTooClose = True
																break

														if somethingTooClose:
															break

													# Found a camp too close, check another Plot
													if somethingTooClose:
														continue

													# Last check
													if not self.isValidForBarbarianCampAt(plotLocation, simulation):
														continue

													loopPlot.setImprovement(ImprovementType.barbarianCamp)
													self.doCampActivationNoticeAt(plotLocation, simulation)

													# show notification, when tile is visible to human player
													if loopPlot.isVisibleTo(simulation.humanPlayer()):
														simulation.humanPlayer().notifications.addNotification(NotificationType.barbarianCampDiscovered, location=loopPlot.point)

													bestUnitType: Optional[UnitType] = self.randomBarbarianUnitTypeIn(loopPlot.area(), UnitTaskType.defense, simulation)
													if bestUnitType is not None:
														barbarianUnit = Unit(loopPlot.point, bestUnitType, barbarianPlayer)
														simulation.addUnit(barbarianUnit)
														simulation.userInterface.showUnit(barbarianUnit, loopPlot.point)

													numCampsToAdd -= 1

													# Seed the next Camp for Coast or not
													wantsCoastal = random.randint(0, 5) == 0 # BARBARIAN_CAMP_COASTAL_SPAWN_ROLL

		if alwaysRevealedBarbCamp:
			# GC.getMap().updateDeferredFog();
			pass

		return

	def doUnits(self, simulation):
		pass

	def canBarbariansSpawn(self, simulation) -> bool:
		"""What turn are we now allowed to Spawn Barbarians on?"""
		return simulation.areBarbariansReleased()

	def isValidForBarbarianCampAt(self, point: HexPoint, simulation) -> bool:
		rangeValue = 4

		for loopLocation in point.areaWithRadius(rangeValue):
			if simulation.valid(loopLocation):
				if self._barbCampSpawnCounter.values[loopLocation.y][loopLocation.x] < -1:
					return False

		return True

	def doCampActivationNoticeAt(self, point: HexPoint, simulation):
		"""Gameplay informing us when a Camp has either been created or spawned a Unit so we can reseed the spawn counter"""
		# Default to between 8 and 12 turns per spawn
		numTurnsToSpawn = 8 + random.randint(0, 5)

		# Raging
		# if (kGame.isOption(GAMEOPTION_RAGING_BARBARIANS))
		# iNumTurnsToSpawn /= 2;

		# Num Units Spawned
		numUnitsSpawned = self._barbCampNumUnitsSpawned.values[point.y][point.x]

		# Reduce turns between spawn if we've pumped out more guys (meaning we're further into the game)
		numTurnsToSpawn -= min(3, numUnitsSpawned)  # -1 turns if we've spawned one Unit, -3 turns if we've spawned three

		# Increment  # of barbs spawned from this camp
		# This starts at - 1 so when a camp is first created it will bump up to 0, which is correct
		self._barbCampNumUnitsSpawned.values[point.y][point.x] += 1

		# Difficulty level can add time between spawns(e.g.Settler is +8 turns)
		numTurnsToSpawn += simulation.handicap.barbarianSpawnModifier()

		self._barbCampSpawnCounter.values[point.y][point.x] = numTurnsToSpawn

	def randomBarbarianUnitTypeIn(self, area: HexArea, task: UnitTaskType, simulation) -> Optional[UnitType]:
		barbarianPlayer = simulation.barbarianPlayer()

		bestUnitType: Optional[UnitType] = None
		bestValue: int = -1

		for unitTypeLoop in list(UnitType):
			# only barbarian unit types are allowed
			if unitTypeLoop.civilization() == CivilizationType.barbarian:
				continue

			valid = False

			unitTypeValue = unitTypeLoop.unitTypeFor(CivilizationType.barbarian)
			if unitTypeValue is not None:
				valid = unitTypeValue.meleeStrength() > 0 or unitTypeValue.rangedStrength() > 0

				if valid:
					# Unit has combat strength, make sure it isn't only defensive (and with no ranged combat ability)
					if unitTypeValue.range() == 0:
						# / * for (int iLoop = 0; iLoop < GC.getNumPromotionInfos(); iLoop++)
						# {
						# const PromotionTypes ePromotion = static_cast < PromotionTypes > (iLoop);
						# CvPromotionEntry * pkPromotionInfo = GC.getPromotionInfo(ePromotion);
						# if (pkPromotionInfo)
						# {
						# if (kUnit.GetFreePromotions(iLoop))
						# {
						# if (pkPromotionInfo->IsOnlyDefensive())
						# {
						# valid = false
						# break
						# }
						# }
						# }
						# } * /
						pass

				# / * if valid
				# {
				# if (pArea->isWater() & & kUnit.GetDomainType() != DOMAIN_SEA) {
				# 	valid = false;
				# } else if (!pArea->isWater() & & kUnit.GetDomainType() != DOMAIN_LAND) {
				# valid = false;
				# }
				# } * /

				if valid:
					if not barbarianPlayer.canTrain(unitTypeValue, continueFlag=False, testVisible=False, ignoreCost=True, ignoreUniqueUnitStatus=False):
						valid = False

				if valid:
					requiredTech = unitTypeValue.requiredTech()
					if requiredTech is not None:
						if not barbarianPlayer.hasTech(requiredTech):
							valid = False

				if valid:
					value = 1 + random.randint(0, 1000)

					if task in unitTypeValue.unitTasks():
						value += 200

					if value > bestValue:
						bestUnitType = unitTypeValue
						bestValue = value

		return bestUnitType

	def doBarbarianCampCleared(self, leader: LeaderType, point: HexPoint, simulation):
		"""Camp cleared, so reset counter"""
		self._barbCampSpawnCounter.values[point.y][point.x] = -16

		tile = simulation.tileAt(point)

		if tile is None:
			return

		tile.addArchaeologicalRecord(ArtifactType.barbarianCamp, era=simulation.worldEra(), leader1=leader, leader2=LeaderType.none)

		return

	def doCampAttackedAt(self, point: HexPoint):
		"""Gameplay informing a camp has been attacked - make it more likely to spawn"""
		counter: int = self._barbCampSpawnCounter.values[point.y][point.x]

		# Halve the amount of time to spawn
		newValue = int(counter / 2)

		self._barbCampSpawnCounter.values[point.y][point.x] = newValue
