import unittest

import pytest

from smarthexboard.smarthexboardlib.game.ai.militaryTypes import TacticalDominanceTerritoryType, TacticalDominanceType, \
	TacticalTargetType
from smarthexboard.smarthexboardlib.game.ai.tactics import TacticalAnalysisCell, TacticalDominanceZone, TacticalTarget, \
	TacticalAnalysisMap
from smarthexboard.smarthexboardlib.game.baseTypes import HandicapType
from smarthexboard.smarthexboardlib.game.cities import City
from smarthexboard.smarthexboardlib.game.civilizations import LeaderType
from smarthexboard.smarthexboardlib.game.game import GameModel
from smarthexboard.smarthexboardlib.game.generation import UserInterfaceImpl
from smarthexboard.smarthexboardlib.game.players import Player
from smarthexboard.smarthexboardlib.game.states.victories import VictoryType
from smarthexboard.smarthexboardlib.game.unitTypes import UnitType, UnitOperationType
from smarthexboard.smarthexboardlib.game.units import Unit
from smarthexboard.smarthexboardlib.map.base import HexPoint, HexArea, Size
from smarthexboard.smarthexboardlib.map.map import Tile
from smarthexboard.smarthexboardlib.map.types import TerrainType, UnitDomainType, MapSize
from smarthexboard.tests.test_utils import MapModelMock


class TestTacticalAnalysisCell(unittest.TestCase):
	def test_constructor(self):
		cell = TacticalAnalysisCell()

		# check default values
		self.assertEqual(cell.deploymentScore(), 0)
		self.assertEqual(cell.defenseModifier(), 0)
		self.assertIsNone(cell.neutralMilitaryUnit())
		self.assertIsNone(cell.friendlyMilitaryUnit())
		self.assertEqual(cell.isRevealed(), False)
		self.assertIsNone(cell.enemyMilitaryUnit())
		self.assertFalse(cell.isVisible())
		self.assertFalse(cell.isSubjectToAttack())
		self.assertFalse(cell.isEnemyCanMovePast())
		self.assertFalse(cell.isFriendlyTurnEndTile())
		self.assertFalse(cell.isEnemyCity())
		self.assertFalse(cell.isNeutralCity())
		self.assertFalse(cell.isWater())
		self.assertFalse(cell.isOcean())
		self.assertFalse(cell.isCanUseToFlank())
		self.assertFalse(cell.isSafeDeployment())
		self.assertTrue(cell.canUseForOperationGathering())
		self.assertFalse(cell.canUseForOperationGatheringCheckWater(True))
		self.assertTrue(cell.canUseForOperationGatheringCheckWater(False))
		self.assertIsNone(cell.dominanceZone())

	def test_setDeploymentScore(self):
		# given
		cell = TacticalAnalysisCell()

		# when
		cell.setDeploymentScore(12)

		# then
		self.assertEqual(cell.deploymentScore(), 12)

	def test_setDefenseModifier(self):
		# given
		cell = TacticalAnalysisCell()

		# when
		cell.setDefenseModifier(27)

		# then
		self.assertEqual(cell.defenseModifier(), 27)

	def test_neutralMilitaryUnit(self):
		# given
		cell = TacticalAnalysisCell()
		player = Player(LeaderType.alexander, cityState=None, human=False)
		unit = Unit(HexPoint(5, 5), UnitType.warrior, player)

		# when
		cell.setNeutralMilitaryUnit(unit)

		# then
		self.assertEqual(cell.neutralMilitaryUnit(), unit)

	def test_friendlyMilitaryUnit(self):
		# given
		cell = TacticalAnalysisCell()
		player = Player(LeaderType.alexander, cityState=None, human=False)
		unit = Unit(HexPoint(5, 5), UnitType.warrior, player)

		# when
		cell.setFriendlyMilitaryUnit(unit)

		# then
		self.assertEqual(cell.friendlyMilitaryUnit(), unit)

	def test_setRevealed(self):
		# given
		cell = TacticalAnalysisCell()

		# when
		cell.setRevealed(True)

		# then
		self.assertTrue(cell.isRevealed())

	def test_setImpassableTerrain(self):
		# given
		cell = TacticalAnalysisCell()
		self.assertFalse(cell.isImpassableTerrain())

		# when - then
		cell.setImpassableTerrain(True)
		self.assertTrue(cell.isImpassableTerrain())

		cell.setImpassableTerrain(False)
		self.assertFalse(cell.isImpassableTerrain())

	def test_isImpassableTerritory(self):
		# given
		cell = TacticalAnalysisCell()
		self.assertFalse(cell.isImpassableTerritory())

		# when - then
		cell.setImpassableTerritory(True)
		self.assertTrue(cell.isImpassableTerritory())

		cell.setImpassableTerritory(False)
		self.assertFalse(cell.isImpassableTerritory())

	def test_isNotVisibleToEnemy(self):
		# given
		cell = TacticalAnalysisCell()
		self.assertFalse(cell.isImpassableTerritory())

		# when
		cell.setNotVisibleToEnemy(True)

		# then
		self.assertTrue(cell.isNotVisibleToEnemy())

	def test_enemyMilitaryUnit(self):
		# given
		cell = TacticalAnalysisCell()
		player = Player(LeaderType.alexander, cityState=None, human=False)
		unit = Unit(HexPoint(5, 5), UnitType.warrior, player)

		# when
		cell.setEnemyMilitaryUnit(unit)

		# then
		self.assertEqual(cell.enemyMilitaryUnit(), unit)

	def test_isSubjectToAttack(self):
		# given
		cell = TacticalAnalysisCell()

		# when
		cell.setSubjectToAttack(True)

		# then
		self.assertTrue(cell.isSubjectToAttack())

	def test_isEnemyCanMovePast(self):
		# given
		cell = TacticalAnalysisCell()

		# when
		cell.setEnemyCanMovePast(True)

		# then
		self.assertTrue(cell.isEnemyCanMovePast())

	def test_isFriendlyTurnEndTile(self):
		# given
		cell = TacticalAnalysisCell()

		# when
		cell.setFriendlyTurnEndTile(True)

		# then
		self.assertTrue(cell.isFriendlyTurnEndTile())

	def test_isEnemyCity(self):
		# given
		cell = TacticalAnalysisCell()

		# when
		cell.setEnemyCity(True)

		# then
		self.assertTrue(cell.isEnemyCity())

	def test_isNeutralCity(self):
		# given
		cell = TacticalAnalysisCell()

		# when
		cell.setNeutralCity(True)

		# then
		self.assertTrue(cell.isNeutralCity())

	def test_isWater(self):
		# given
		cell = TacticalAnalysisCell()

		# when
		cell.setWater(True)

		# then
		self.assertTrue(cell.isWater())

	def test_isOcean(self):
		# given
		cell = TacticalAnalysisCell()

		# when
		cell.setOcean(True)

		# then
		self.assertTrue(cell.isOcean())

	def test_isWithinRangeOfTarget(self):
		# given
		cell = TacticalAnalysisCell()

		# when
		cell.setWithinRangeOfTarget(True)

		# then
		self.assertTrue(cell.isWithinRangeOfTarget())

	def test_isCanUseToFlank(self):
		# given
		cell = TacticalAnalysisCell()

		# when
		cell.setCanUseToFlank(True)

		# then
		self.assertTrue(cell.isCanUseToFlank())

	def test_isSafeDeployment(self):
		# given
		cell = TacticalAnalysisCell()

		# when
		cell.setSafeDeployment(True)

		# then
		self.assertTrue(cell.isSafeDeployment())

	def test_canUseForOperationGathering(self):
		# given
		cell = TacticalAnalysisCell()
		player = Player(LeaderType.alexander, cityState=None, human=False)
		unit = Unit(HexPoint(5, 5), UnitType.warrior, player)

		# when - then
		self.assertTrue(cell.canUseForOperationGathering())

		cell.setImpassableTerrain(True)
		self.assertFalse(cell.canUseForOperationGathering())
		cell.setImpassableTerrain(False)
		self.assertTrue(cell.canUseForOperationGathering())
		cell.setEnemyMilitaryUnit(unit)
		self.assertFalse(cell.canUseForOperationGathering())
		cell.setEnemyMilitaryUnit(None)

	def test_dominanceZone(self):
		# given
		cell = TacticalAnalysisCell()
		zone = TacticalDominanceZone(
			territoryType=TacticalDominanceTerritoryType.neutral,
			dominanceFlag=TacticalDominanceType.even,
			owner=None,
			area=None,
			isWater=False,
			closestCity=None,
			center=None,
			navalInvasion=False,
			friendlyStrength=1,
			friendlyRangedStrength=2,
			friendlyUnitCount=3,
			friendlyRangedUnitCount=4,
			enemyStrength=5,
			enemyRangedStrength=6,
			enemyUnitCount=7,
			enemyRangedUnitCount=8,
			enemyNavalUnitCount=9,
			rangeClosestEnemyUnit=10,
			dominanceValue=11
		)

		# when
		cell.setDominanceZone(zone)

		# then
		self.assertTrue(cell.dominanceZone(), zone)


class TestTacticalDominanceZone(unittest.TestCase):
	def test_constructor(self):
		zone = TacticalDominanceZone(
			territoryType=TacticalDominanceTerritoryType.neutral,
			dominanceFlag=TacticalDominanceType.even,
			owner=None,
			area=None,
			isWater=False,
			closestCity=None,
			center=None,
			navalInvasion=False,
			friendlyStrength=1,
			friendlyRangedStrength=2,
			friendlyUnitCount=3,
			friendlyRangedUnitCount=4,
			enemyStrength=5,
			enemyRangedStrength=6,
			enemyUnitCount=7,
			enemyRangedUnitCount=8,
			enemyNavalUnitCount=9,
			rangeClosestEnemyUnit=10,
			dominanceValue=11
		)

		self.assertEqual(zone.territoryType, TacticalDominanceTerritoryType.neutral)

	def test_center(self):
		tile = Tile(HexPoint(5, 5), TerrainType.shore)
		zone = TacticalDominanceZone(
			territoryType=TacticalDominanceTerritoryType.neutral,
			dominanceFlag=TacticalDominanceType.even,
			owner=None,
			area=None,
			isWater=False,
			closestCity=None,
			center=tile,
			navalInvasion=False,
			friendlyStrength=1,
			friendlyRangedStrength=2,
			friendlyUnitCount=3,
			friendlyRangedUnitCount=4,
			enemyStrength=5,
			enemyRangedStrength=6,
			enemyUnitCount=7,
			enemyRangedUnitCount=8,
			enemyNavalUnitCount=9,
			rangeClosestEnemyUnit=10,
			dominanceValue=11
		)

		self.assertEqual(zone.center, tile)

	def test_eq(self):
		tile1 = Tile(HexPoint(5, 5), TerrainType.shore)
		tile2 = Tile(HexPoint(5, 5), TerrainType.plains)

		zone1 = TacticalDominanceZone(
			territoryType=TacticalDominanceTerritoryType.neutral,
			dominanceFlag=TacticalDominanceType.even,
			owner=None,
			area=None,
			isWater=False,
			closestCity=None,
			center=tile1,
			navalInvasion=False,
			friendlyStrength=1,
			friendlyRangedStrength=2,
			friendlyUnitCount=3,
			friendlyRangedUnitCount=4,
			enemyStrength=5,
			enemyRangedStrength=6,
			enemyUnitCount=7,
			enemyRangedUnitCount=8,
			enemyNavalUnitCount=9,
			rangeClosestEnemyUnit=10,
			dominanceValue=11
		)

		zone2 = TacticalDominanceZone(
			territoryType=TacticalDominanceTerritoryType.neutral,
			dominanceFlag=TacticalDominanceType.even,
			owner=None,
			area=None,
			isWater=False,
			closestCity=None,
			center=tile2,
			navalInvasion=False,
			friendlyStrength=1,
			friendlyRangedStrength=2,
			friendlyUnitCount=3,
			friendlyRangedUnitCount=4,
			enemyStrength=5,
			enemyRangedStrength=6,
			enemyUnitCount=7,
			enemyRangedUnitCount=8,
			enemyNavalUnitCount=9,
			rangeClosestEnemyUnit=10,
			dominanceValue=11
		)

		self.assertEqual(zone1, zone2)  # just the point is relevant

		with pytest.raises(Exception):
			self.assertEqual(zone1, tile1)

	def test_hash(self):
		tile1 = Tile(HexPoint(5, 5), TerrainType.shore)
		tile2 = Tile(HexPoint(5, 5), TerrainType.plains)

		zone1 = TacticalDominanceZone(
			territoryType=TacticalDominanceTerritoryType.neutral,
			dominanceFlag=TacticalDominanceType.even,
			owner=None,
			area=None,
			isWater=False,
			closestCity=None,
			center=tile1,
			navalInvasion=False,
			friendlyStrength=1,
			friendlyRangedStrength=2,
			friendlyUnitCount=3,
			friendlyRangedUnitCount=4,
			enemyStrength=5,
			enemyRangedStrength=6,
			enemyUnitCount=7,
			enemyRangedUnitCount=8,
			enemyNavalUnitCount=9,
			rangeClosestEnemyUnit=10,
			dominanceValue=11
		)

		zone2 = TacticalDominanceZone(
			territoryType=TacticalDominanceTerritoryType.neutral,
			dominanceFlag=TacticalDominanceType.even,
			owner=None,
			area=None,
			isWater=False,
			closestCity=None,
			center=tile2,
			navalInvasion=False,
			friendlyStrength=1,
			friendlyRangedStrength=2,
			friendlyUnitCount=3,
			friendlyRangedUnitCount=4,
			enemyStrength=5,
			enemyRangedStrength=6,
			enemyUnitCount=7,
			enemyRangedUnitCount=8,
			enemyNavalUnitCount=9,
			rangeClosestEnemyUnit=10,
			dominanceValue=11
		)

		self.assertEqual(zone1.__hash__(), zone2.__hash__())  # just the point is relevant


class TestTacticalTarget(unittest.TestCase):
	def test_constructor(self):
		target = TacticalTarget(
			targetType=TacticalTargetType.city,
			target=HexPoint(5, 5),
			targetLeader=LeaderType.alexander,
			dominanceZone=None
		)

		self.assertEqual(target.targetType, TacticalTargetType.city)
		self.assertEqual(target.target, HexPoint(5, 5))
		self.assertEqual(target.targetLeader, LeaderType.alexander)
		self.assertIsNone(target.dominanceZone)
		self.assertEqual(target.threatValue, 0)
		self.assertIsNone(target.unit)
		self.assertEqual(target.damage, 0)

	def test_lt(self):
		# given
		target1 = TacticalTarget(
			targetType=TacticalTargetType.city,
			target=HexPoint(5, 5),
			targetLeader=LeaderType.alexander,
			dominanceZone=None
		)
		target2 = TacticalTarget(
			targetType=TacticalTargetType.city,
			target=HexPoint(5, 5),
			targetLeader=LeaderType.alexander,
			dominanceZone=None
		)

		# when - then
		self.assertFalse(target1 < target2)

		target1.damage = 0
		target2.damage = 12
		self.assertTrue(target1 < target2)

		with pytest.raises(Exception):
			self.assertEqual(target1, 3)

	def test_eq(self):
		# given
		target1 = TacticalTarget(
			targetType=TacticalTargetType.city,
			target=HexPoint(5, 5),
			targetLeader=LeaderType.alexander,
			dominanceZone=None
		)
		target2 = TacticalTarget(
			targetType=TacticalTargetType.city,
			target=HexPoint(5, 5),
			targetLeader=LeaderType.alexander,
			dominanceZone=None
		)

		# when - then
		self.assertTrue(target1 == target2)

		target1.damage = 0
		target2.damage = 12
		self.assertFalse(target1 == target2)

		with pytest.raises(Exception):
			self.assertEqual(target1, 3)

	def test_isTargetValidIn_none(self):
		# given
		target = TacticalTarget(
			targetType=TacticalTargetType.none,
			target=HexPoint(5, 5),
			targetLeader=LeaderType.alexander,
			dominanceZone=None
		)

		# when
		result = target.isTargetValidIn(UnitDomainType.land)

		# then
		self.assertFalse(result)

	def test_isTargetValidIn_both(self):
		# given
		target = TacticalTarget(
			targetType=TacticalTargetType.city,
			target=HexPoint(5, 5),
			targetLeader=LeaderType.alexander,
			dominanceZone=None
		)

		# when
		result = target.isTargetValidIn(UnitDomainType.land)

		# then
		self.assertTrue(result)

	def test_isTargetValidIn_land(self):
		# given
		target = TacticalTarget(
			targetType=TacticalTargetType.barbarianCamp,
			target=HexPoint(5, 5),
			targetLeader=LeaderType.alexander,
			dominanceZone=None
		)

		# when
		resultLand = target.isTargetValidIn(UnitDomainType.land)
		resultSea = target.isTargetValidIn(UnitDomainType.sea)

		# then
		self.assertTrue(resultLand)
		self.assertFalse(resultSea)

	def test_isTargetValidIn_sea(self):
		# given
		target = TacticalTarget(
			targetType=TacticalTargetType.tradeUnitSea,
			target=HexPoint(5, 5),
			targetLeader=LeaderType.alexander,
			dominanceZone=None
		)

		# when
		resultLand = target.isTargetValidIn(UnitDomainType.land)
		resultSea = target.isTargetValidIn(UnitDomainType.sea)

		# then
		self.assertFalse(resultLand)
		self.assertTrue(resultSea)

	def test_isTargetStillAliveFor_unit(self):
		# given
		mapModel = MapModelMock(MapSize.tiny, TerrainType.grass)
		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=mapModel
		)

		# players
		playerBarbar = Player(LeaderType.barbar, human=False)
		playerBarbar.initialize()
		simulation.players.append(playerBarbar)

		playerTrajan = Player(LeaderType.trajan, human=False)
		playerTrajan.initialize()
		simulation.players.append(playerTrajan)

		playerAlexander = Player(LeaderType.alexander, human=True)
		playerAlexander.initialize()
		simulation.players.append(playerAlexander)

		# add UI
		simulation.userInterface = UserInterfaceImpl()

		warrior = Unit(HexPoint(5, 5), UnitType.scout, playerAlexander)
		simulation.addUnit(warrior)

		simulation.sightAt(HexPoint(5, 5), 2, player=playerTrajan)

		playerAlexander.doFirstContactWith(playerTrajan, simulation)
		playerAlexander.doDeclareWarTo(playerTrajan, simulation)

		target = TacticalTarget(
			targetType=TacticalTargetType.lowPriorityUnit,
			target=HexPoint(5, 5),
			targetLeader=LeaderType.alexander,
			dominanceZone=None
		)

		# when
		resultLand = target.isTargetStillAliveFor(playerTrajan, simulation)

		# then
		self.assertTrue(resultLand)

	def test_isTargetStillAliveFor_city(self):
		# given
		mapModel = MapModelMock(MapSize.tiny, TerrainType.grass)
		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=mapModel
		)

		# players
		playerBarbar = Player(LeaderType.barbar, human=False)
		playerBarbar.initialize()
		simulation.players.append(playerBarbar)

		playerTrajan = Player(LeaderType.trajan, human=False)
		playerTrajan.initialize()
		simulation.players.append(playerTrajan)

		playerAlexander = Player(LeaderType.alexander, human=True)
		playerAlexander.initialize()
		simulation.players.append(playerAlexander)

		# add UI
		simulation.userInterface = UserInterfaceImpl()

		city = City("Berlin", HexPoint(5, 5), isCapital=False, player=playerAlexander)
		city.initialize(simulation)
		simulation.addCity(city)

		simulation.sightAt(HexPoint(5, 5), 2, player=playerTrajan)

		playerAlexander.doFirstContactWith(playerTrajan, simulation)
		playerAlexander.doDeclareWarTo(playerTrajan, simulation)

		target = TacticalTarget(
			targetType=TacticalTargetType.city,
			target=HexPoint(5, 5),
			targetLeader=LeaderType.alexander,
			dominanceZone=None
		)

		# when
		resultLand = target.isTargetStillAliveFor(playerTrajan, simulation)

		# then
		self.assertTrue(resultLand)


class TestTacticalAnalysisMap(unittest.TestCase):
	def test_constructor(self):
		analysisMap = TacticalAnalysisMap(Size(10, 10))

		self.assertEqual(analysisMap.unitStrengthMultiplier, 100)
		self.assertEqual(analysisMap.turnBuild, -1)

	def test_plots(self):
		analysisMap = TacticalAnalysisMap(Size(10, 10))

		cell1: TacticalAnalysisCell = analysisMap.plots.values[0][0]
		cell2: TacticalAnalysisCell = analysisMap.plots.values[0][1]

		self.assertEqual(cell1.defenseModifier(), 0)

		cell1.setDefenseModifier(12)
		self.assertEqual(cell1.defenseModifier(), 12)

		self.assertEqual(cell2.defenseModifier(), 0)

	def test_refreshFor_normal(self):
		# given
		mapModel = MapModelMock.duelMap()

		# players
		playerBarbar = Player(LeaderType.barbar, human=False)
		playerBarbar.initialize()

		playerTrajan = Player(LeaderType.trajan, human=False)
		playerTrajan.initialize()

		playerAlexander = Player(LeaderType.alexander, human=True)
		playerAlexander.initialize()

		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[playerBarbar, playerTrajan, playerAlexander],
			map=mapModel
		)

		# add UI
		simulation.userInterface = UserInterfaceImpl()

		# reveal map for player
		mapModel.discover(playerTrajan, simulation)

		# add some content that creates zones
		playerAlexander.foundAt(HexPoint(26, 17), "Capital", simulation)

		warriorAlexander = Unit(HexPoint(26, 16), UnitType.warrior, playerAlexander)
		simulation.addUnit(warriorAlexander)

		playerAlexander.doFirstContactWith(playerTrajan, simulation)
		playerAlexander.doDeclareWarTo(playerTrajan, simulation)

		tacticalAnalysisMap = simulation.tacticalAnalysisMap()

		# when
		tacticalAnalysisMap.refreshFor(playerTrajan, simulation)

		# then
		self.assertEqual(len(tacticalAnalysisMap.dominanceZones), 641)

	def test_refreshFor_army(self):
		# given
		mapModel = MapModelMock.duelMap()

		# players
		playerBarbar = Player(LeaderType.barbar, human=False)
		playerBarbar.initialize()

		playerTrajan = Player(LeaderType.trajan, human=False)
		playerTrajan.initialize()

		playerAlexander = Player(LeaderType.alexander, human=True)
		playerAlexander.initialize()

		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[playerBarbar, playerTrajan, playerAlexander],
			map=mapModel
		)

		# add UI
		simulation.userInterface = UserInterfaceImpl()

		# reveal map for player
		mapModel.discover(playerTrajan, simulation)

		# add some content that creates zones
		playerAlexander.foundAt(HexPoint(26, 17), "Capital", simulation)
		playerAlexanderCapital: City = simulation.cityAt(HexPoint(26, 17))
		playerAlexanderCapitalArea: HexArea = simulation.areaOf(HexPoint(26, 17))

		warriorAlexander = Unit(HexPoint(26, 16), UnitType.warrior, playerAlexander)
		simulation.addUnit(warriorAlexander)

		# own stuff
		playerTrajan.foundAt(HexPoint(11, 20), "Rome", simulation)
		playerTrajanCapital: City = simulation.cityAt(HexPoint(11, 20))
		playerTrajanCapitalArea: HexArea = simulation.areaOf(HexPoint(11, 20))

		playerTrajanWarrior = Unit(HexPoint(11, 19), UnitType.warrior, playerTrajan)
		simulation.addUnit(playerTrajanWarrior)

		playerTrajanArcher = Unit(HexPoint(11, 18), UnitType.archer, playerTrajan)
		simulation.addUnit(playerTrajanArcher)

		playerAlexander.doFirstContactWith(playerTrajan, simulation)
		playerTrajan.doFirstContactWith(playerAlexander, simulation)
		playerAlexander.doDeclareWarTo(playerTrajan, simulation)
		playerTrajan.doDeclareWarTo(playerAlexander, simulation)

		playerAlexander.addOperation(UnitOperationType.basicCityAttack, playerTrajan, playerTrajanCapital, playerTrajanCapitalArea, playerAlexanderCapital, simulation)

		tacticalAnalysisMap = simulation.tacticalAnalysisMap()

		# when
		tacticalAnalysisMap.refreshFor(playerTrajan, simulation)

		# then
		self.assertEqual(len(tacticalAnalysisMap.dominanceZones), 641)
		# self.assertEqual(tacticalAnalysisMap.isInEnemyDominatedZone(HexPoint(26, 17)), True)
		# z = tacticalAnalysisMap.findExistingZoneAt(HexPoint(26, 17), TacticalDominanceTerritoryType.enemy, playerAlexander, playerAlexanderCapital, playerAlexanderCapitalArea)
		# print()

	def test_clearDynamicFlags(self):
		# given
		mapModel = MapModelMock.duelMap()

		# players
		playerBarbar = Player(LeaderType.barbar, human=False)
		playerBarbar.initialize()

		playerTrajan = Player(LeaderType.trajan, human=False)
		playerTrajan.initialize()

		playerAlexander = Player(LeaderType.alexander, human=True)
		playerAlexander.initialize()

		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[playerBarbar, playerTrajan, playerAlexander],
			map=mapModel
		)

		# add UI
		simulation.userInterface = UserInterfaceImpl()
		tacticalAnalysisMap = simulation.tacticalAnalysisMap()

		# when
		tacticalAnalysisMap.clearDynamicFlags()

		# then
		self.assertTrue(True)

	# def test_findExistingZoneAt(self):
