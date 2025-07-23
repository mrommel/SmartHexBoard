import os
import unittest

import django
import pytest

from smarthexboard.smarthexboardlib.game.baseTypes import HandicapType, GameState
from smarthexboard.smarthexboardlib.game.cities import City
from smarthexboard.smarthexboardlib.game.civilizations import LeaderType
from smarthexboard.smarthexboardlib.game.combat import Combat
from smarthexboard.smarthexboardlib.game.game import GameModel
from smarthexboard.smarthexboardlib.game.generation import UserInterfaceImpl
from smarthexboard.smarthexboardlib.game.players import Player
from smarthexboard.smarthexboardlib.game.policyCards import PolicyCardType
from smarthexboard.smarthexboardlib.game.promotions import UnitPromotionType, CombatModifier
from smarthexboard.smarthexboardlib.game.states.victories import VictoryType
from smarthexboard.smarthexboardlib.game.types import CivicType, TechType
from smarthexboard.smarthexboardlib.game.unitTypes import UnitType
from smarthexboard.smarthexboardlib.game.units import Unit
from smarthexboard.smarthexboardlib.map.base import HexPoint
from smarthexboard.smarthexboardlib.map.improvements import ImprovementType
from smarthexboard.smarthexboardlib.map.map import Tile
from smarthexboard.smarthexboardlib.map.types import MapSize, TerrainType, ResourceType
from smarthexboard.tests.test_utils import MapModelMock, BetweenAssertMixin

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smarthexboard.setup')
django.setup()


class TestCombatModifier(unittest.TestCase):
	def test_defensive_combat_modifier(self):
		# GIVEN

		# players
		barbarianPlayer = Player(LeaderType.barbar, human=False)
		barbarianPlayer.initialize()

		playerTrajan = Player(LeaderType.trajan, human=False)
		playerTrajan.initialize()

		playerAlexander = Player(LeaderType.alexander, human=True)
		playerAlexander.initialize()

		# map
		mapModel = MapModelMock(MapSize.duel, TerrainType.grass)

		# game
		simulation = GameModel(
			victoryTypes=[VictoryType.domination, VictoryType.cultural, VictoryType.diplomatic],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[barbarianPlayer, playerTrajan, playerAlexander],
			map=mapModel
		)

		warrior = Unit(HexPoint(5, 6), UnitType.warrior, playerTrajan)
		simulation.addUnit(warrior)

		barbarianWarrior = Unit(HexPoint(5, 7), UnitType.warrior, barbarianPlayer)
		simulation.addUnit(barbarianWarrior)

		# WHEN
		modifiersBarbarian = barbarianWarrior.defensiveStrengthModifierAgainst(None, None, None, ranged=False, simulation=simulation)
		modifiersNormal = warrior.defensiveStrengthModifierAgainst(None, None, None, ranged=False, simulation=simulation)

		# policy twilightValor
		playerTrajan.government.addCard(PolicyCardType.twilightValor)
		modifiersTwilightValor = warrior.defensiveStrengthModifierAgainst(None, None, None, ranged=False, simulation=simulation)
		playerTrajan.government.removeCard(PolicyCardType.twilightValor)

		# hills
		tile = Tile(HexPoint(5, 5), TerrainType.grass)
		tile.setHills(True)
		modifiersHills = warrior.defensiveStrengthModifierAgainst(None, None, tile, ranged=False, simulation=simulation)

		# promotion
		warrior.doPromote(UnitPromotionType.battlecry, simulation)
		modifiersPromotion = warrior.defensiveStrengthModifierAgainst(barbarianWarrior, None, None, ranged=False, simulation=simulation)

		# THEN
		self.assertEqual(modifiersBarbarian, [])  # no modifiers for barbarians
		self.assertEqual(modifiersNormal, [CombatModifier(-1, "Bonus due to difficulty")])
		self.assertListEqual(modifiersTwilightValor, [
			CombatModifier(5, "TXT_KEY_POLICY_CARD_TWILIGHT_VALOR_TITLE"),
			CombatModifier(-1, "Bonus due to difficulty")
		])
		self.assertListEqual(modifiersHills, [
			CombatModifier(3, "Ideal terrain"),
			CombatModifier(-1, "Bonus due to difficulty")
		])
		self.assertListEqual(modifiersPromotion, [
			CombatModifier(-1, "Bonus due to difficulty"),
			CombatModifier(7, "TXT_KEY_UNIT_PROMOTION_BATTLECRY_NAME")
		])


class TestCombat(unittest.TestCase, BetweenAssertMixin):
	def setUp(self) -> None:
		# players
		self.barbarianPlayer = Player(LeaderType.barbar, human=False)
		self.barbarianPlayer.initialize()

		self.playerTrajan = Player(LeaderType.trajan, human=False)
		self.playerTrajan.initialize()

		self.playerAlexander = Player(LeaderType.alexander, human=True)
		self.playerAlexander.initialize()

		# map
		self.mapModel = MapModelMock(MapSize.duel, TerrainType.grass)

		# game
		self.simulation = GameModel(
			victoryTypes=[VictoryType.domination, VictoryType.cultural, VictoryType.diplomatic],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[self.barbarianPlayer, self.playerTrajan, self.playerAlexander],
			map=self.mapModel
		)
		self.simulation.userInterface = UserInterfaceImpl()

		self.playerTrajan.doFirstContactWith(self.playerAlexander, self.simulation)

	def test_predict_warrior_against_warrior(self):
		# GIVEN
		attacker = Unit(HexPoint(5, 6), UnitType.warrior, self.playerAlexander)
		self.simulation.addUnit(attacker)

		defender = Unit(HexPoint(6, 6), UnitType.warrior, self.playerTrajan)
		self.simulation.addUnit(attacker)

		# WHEN
		result = Combat.predictMeleeAttack(attacker, defender, self.simulation)

		# THEN
		self.assertEqual(result.attackerDamage, 26)
		self.assertEqual(result.defenderDamage, 33)

	def test_predict_warrior_against_warrior_flanking(self):
		# GIVEN
		self.playerAlexander.civics.discover(CivicType.militaryTradition, self.simulation)

		attacker = Unit(HexPoint(5, 6), UnitType.warrior, self.playerAlexander)
		self.simulation.addUnit(attacker)

		flanking = Unit(HexPoint(5, 5), UnitType.warrior, self.playerAlexander)
		self.simulation.addUnit(flanking)

		defender = Unit(HexPoint(6, 5), UnitType.warrior, self.playerTrajan)
		self.simulation.addUnit(attacker)

		# WHEN
		result = Combat.predictMeleeAttack(attacker, defender, self.simulation)

		# THEN
		self.assertEqual(result.attackerDamage, 24)
		self.assertEqual(result.defenderDamage, 36)

	def test_predict_warrior_against_capital(self):
		# GIVEN
		attacker = Unit(HexPoint(5, 6), UnitType.warrior, self.playerAlexander)
		self.simulation.addUnit(attacker)

		city = City("Berlin", HexPoint(5, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.simulation)
		self.simulation.addCity(city)

		# WHEN
		result = Combat.predictMeleeAttack(attacker, city, self.simulation)

		# THEN
		self.assertEqual(result.attackerDamage, 12)
		self.assertEqual(result.defenderDamage, 17)
		self.assertEqual(city.maxHealthPoints(), 200)

	def test_predict_warrior_against_city(self):
		# GIVEN
		attacker = Unit(HexPoint(5, 6), UnitType.warrior, self.playerAlexander)
		self.simulation.addUnit(attacker)

		city = City("Berlin", HexPoint(5, 5), isCapital=False, player=self.playerTrajan)
		city.initialize(self.simulation)
		self.simulation.addCity(city)

		# WHEN
		result = Combat.predictMeleeAttack(attacker, city, self.simulation)

		# THEN
		self.assertEqual(result.attackerDamage, 12)
		self.assertEqual(result.defenderDamage, 48)
		self.assertEqual(city.maxHealthPoints(), 200)

	def test_predict_city_against_warrior(self):
		# GIVEN
		city = City("Berlin", HexPoint(5, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.simulation)
		self.simulation.addCity(city)

		defender = Unit(HexPoint(5, 6), UnitType.warrior, self.playerAlexander)
		self.simulation.addUnit(defender)

		# WHEN
		result = Combat.predictRangedAttack(city, defender, self.simulation)

		# THEN
		self.assertEqual(result.attackerDamage, 0)
		self.assertEqual(result.defenderDamage, 12)

	def test_predict_archer_against_warrior(self):
		# GIVEN
		attacker = Unit(HexPoint(5, 5), UnitType.archer, self.playerTrajan)
		self.simulation.addUnit(attacker)

		defender = Unit(HexPoint(5, 6), UnitType.warrior, self.playerAlexander)
		self.simulation.addUnit(defender)

		# WHEN
		result = Combat.predictRangedAttack(attacker, defender, self.simulation)

		# THEN
		self.assertEqual(result.attackerDamage, 0)
		self.assertEqual(result.defenderDamage, 32)

	def test_predict_archer_against_city(self):
		# GIVEN
		attacker = Unit(HexPoint(5, 5), UnitType.archer, self.playerTrajan)
		self.simulation.addUnit(attacker)

		city = City("Berlin", HexPoint(5, 6), isCapital=True, player=self.playerAlexander)
		city.initialize(self.simulation)
		self.simulation.addCity(city)

		# WHEN
		result = Combat.predictRangedAttack(attacker, city, self.simulation)

		# THEN
		self.assertEqual(result.attackerDamage, 0)
		self.assertEqual(result.defenderDamage, 9)


class TestRealCombat(unittest.TestCase, BetweenAssertMixin):
	def setUp(self) -> None:
		self.mapModel = MapModelMock(MapSize.duel, TerrainType.grass)

		# players
		self.playerBarbarian = Player(LeaderType.barbar, human=False)
		self.playerBarbarian.initialize()

		self.playerAlexander = Player(LeaderType.alexander, human=False)
		self.playerAlexander.initialize()

		self.playerTrajan = Player(LeaderType.trajan, human=True)
		self.playerTrajan.initialize()

		self.simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[self.playerBarbarian, self.playerAlexander, self.playerTrajan],
			map=self.mapModel
		)

		# add UI
		self.simulation.userInterface = UserInterfaceImpl()

	def test_barbarian_attacks_builder(self):
		# GIVEN
		self.simulation.currentTurn = 45  # otherwise the barbarians won't attack

		barbarianWarrior = Unit(HexPoint(7, 8), UnitType.barbarianWarrior, self.playerBarbarian)
		self.simulation.addUnit(barbarianWarrior)
		self.simulation.sightAt(HexPoint(7, 8), 3, barbarianWarrior, self.playerBarbarian)

		alexanderWarrior = Unit(HexPoint(12, 15), UnitType.warrior, self.playerAlexander)
		self.simulation.addUnit(alexanderWarrior)
		self.simulation.sightAt(HexPoint(12, 15), 3, alexanderWarrior, self.playerAlexander)

		trajanBuilder = Unit(HexPoint(7, 9), UnitType.builder, self.playerTrajan)
		self.simulation.addUnit(trajanBuilder)
		self.simulation.sightAt(HexPoint(7, 9), 3, trajanBuilder, self.playerTrajan)

		# WHEN
		while not (self.playerTrajan.hasProcessedAutoMoves() and self.playerTrajan.turnFinished()) and self.simulation.gameState() != GameState.over:
			self.simulation.update()

			if self.playerTrajan.isTurnActive():
				self.playerTrajan.setProcessedAutoMovesTo(True)
				self.playerTrajan.finishTurn()

		# THEN
		self.assertEqual(barbarianWarrior.location, HexPoint(7, 9))
		# there should be a captured builder and the barbarian warrior
		self.assertEqual(len(self.simulation.unitsAt(HexPoint(7, 9))), 2)

	def test_barbarian_plunder_improvement(self):
		# GIVEN
		self.simulation.currentTurn = 45  # otherwise the barbarians won't attack

		barbarianWarrior = Unit(HexPoint(7, 8), UnitType.barbarianWarrior, self.playerBarbarian)
		self.simulation.addUnit(barbarianWarrior)
		self.simulation.sightAt(HexPoint(7, 8), 3, barbarianWarrior, self.playerBarbarian)

		alexanderWarrior = Unit(HexPoint(12, 15), UnitType.warrior, self.playerAlexander)
		self.simulation.addUnit(alexanderWarrior)
		self.simulation.sightAt(HexPoint(12, 15), 3, alexanderWarrior, self.playerAlexander)

		trajanCity = City("Berlin", HexPoint(7, 10), isCapital=True, player=self.playerTrajan)
		trajanCity.initialize(self.simulation)
		self.simulation.addCity(trajanCity)

		trajanWarrior = Unit(HexPoint(7, 10), UnitType.warrior, self.playerTrajan)
		self.simulation.addUnit(trajanWarrior)
		self.simulation.sightAt(HexPoint(7, 10), 3, trajanWarrior, self.playerTrajan)

		trajanWarrior.doGarrison(self.simulation)

		self.playerTrajan.techs.discover(TechType.irrigation, self.simulation)
		self.simulation.tileAt(HexPoint(7, 9)).setImprovement(ImprovementType.farm)
		self.simulation.tileAt(HexPoint(7, 9)).setResource(ResourceType.sugar)

		# pre-checks
		tile = self.simulation.tileAt(HexPoint(7, 9))
		self.assertEqual(tile.hasOwner(), True)
		self.assertEqual(tile.owner() is not None, True)
		self.assertEqual(self.playerBarbarian.diplomacyAI.isAtWarWith(tile.owner()), True)
		self.assertEqual(tile.canBePillaged(), True)
		self.assertEqual(tile.hasAnyResourceFor(self.playerTrajan), True)

		# WHEN
		while not (self.playerTrajan.hasProcessedAutoMoves() and self.playerTrajan.turnFinished()) and self.simulation.gameState() != GameState.over:
			self.simulation.update()

			if self.playerTrajan.isTurnActive():
				self.playerTrajan.setProcessedAutoMovesTo(True)
				self.playerTrajan.finishTurn()

		# THEN
		self.assertEqual(barbarianWarrior.location, HexPoint(7, 9))
		# the improvement should be pillaged - next turn?
		# self.assertEqual(self.simulation.tileAt(HexPoint(7, 9)).isImprovementPillaged(), True)

	def test_big_war_group(self):
		# GIVEN
		self.simulation.currentTurn = 45  # otherwise the barbarians won't attack

		# barbarian
		barbarianWarrior = Unit(HexPoint(7, 8), UnitType.barbarianWarrior, self.playerBarbarian)
		self.simulation.addUnit(barbarianWarrior)
		self.simulation.sightAt(HexPoint(7, 8), 3, barbarianWarrior, self.playerBarbarian)

		# alexander
		alexanderCity = City("Athens", HexPoint(12, 15), isCapital=True, player=self.playerAlexander)
		alexanderCity.initialize(self.simulation)
		self.simulation.addCity(alexanderCity)

		alexanderWarrior = Unit(HexPoint(12, 15), UnitType.warrior, self.playerAlexander)
		self.simulation.addUnit(alexanderWarrior)
		self.simulation.sightAt(HexPoint(12, 15), 3, alexanderWarrior, self.playerAlexander)

		alexanderWarrior.doGarrison(self.simulation)

		unitTypes = [UnitType.swordman, UnitType.archer, UnitType.archer, UnitType.builder, UnitType.spearman, UnitType.settler]
		for unitType in unitTypes:
			alexanderUnit = Unit(HexPoint(12, 15), unitType, self.playerAlexander)
			self.simulation.addUnit(alexanderUnit)
			self.simulation.sightAt(HexPoint(12, 15), 3, alexanderUnit, self.playerAlexander)
			alexanderUnit.jumpToNearestValidPlotWithin(2, self.simulation)

		# trajan
		trajanCity = City("Berlin", HexPoint(7, 10), isCapital=True, player=self.playerTrajan)
		trajanCity.initialize(self.simulation)
		self.simulation.addCity(trajanCity)

		trajanWarrior = Unit(HexPoint(7, 10), UnitType.warrior, self.playerTrajan)
		self.simulation.addUnit(trajanWarrior)
		self.simulation.sightAt(HexPoint(7, 10), 3, trajanWarrior, self.playerTrajan)

		trajanWarrior.doGarrison(self.simulation)

		# extended
		self.playerTrajan.doFirstContactWith(self.playerAlexander, self.simulation)
		self.playerTrajan.doDeclareWarTo(self.playerAlexander, self.simulation)

		self.playerTrajan.techs.discover(TechType.archery, self.simulation)
		self.playerTrajan.techs.discover(TechType.bronzeWorking, self.simulation)
		self.playerTrajan.techs.discover(TechType.ironWorking, self.simulation)

		# pre-checks
		# tile = self.simulation.tileAt(HexPoint(7, 9))
		# self.assertEqual(tile.hasOwner(), True)
		# self.assertEqual(tile.owner() is not None, True)
		# self.assertEqual(self.playerBarbarian.diplomacyAI.isAtWarWith(tile.owner()), True)
		# self.assertEqual(tile.canBePillaged(), True)
		# self.assertEqual(tile.hasAnyResourceFor(self.playerTrajan), True)

		# WHEN
		for _ in range(3):
			while not (self.playerTrajan.hasProcessedAutoMoves() and self.playerTrajan.turnFinished()) and self.simulation.gameState() != GameState.over:
				self.simulation.update()

				if self.playerTrajan.isTurnActive():
					self.playerTrajan.setProcessedAutoMovesTo(True)
					self.playerTrajan.finishTurn()

		# THEN
		self.assertEqual(len(list(self.playerTrajan.armies)), 0)  # fixme: there should be an attack force

	def test_combat_warrior_against_warrior(self):
		# GIVEN
		attacker = Unit(HexPoint(5, 6), UnitType.warrior, self.playerAlexander)
		self.simulation.addUnit(attacker)

		defender = Unit(HexPoint(5, 5), UnitType.warrior, self.playerTrajan)
		self.simulation.addUnit(defender)

		self.playerTrajan.doFirstContactWith(self.playerAlexander, self.simulation)

		# WHEN
		result = Combat.doMeleeAttack(attacker, defender, self.simulation)

		# THEN
		self.assertBetween(result.attackerDamage, 33, 34)
		self.assertBetween(result.defenderDamage, 25, 27)

	def test_melee_kill_warrior_against_warrior(self):
		# GIVEN
		attacker = Unit(HexPoint(5, 6), UnitType.warrior, self.playerAlexander)
		self.simulation.addUnit(attacker)

		defender = Unit(HexPoint(5, 5), UnitType.warrior, self.playerTrajan)
		defender.changeDamage(90, None, self.simulation)
		self.simulation.addUnit(defender)

		self.playerTrajan.doFirstContactWith(self.playerAlexander, self.simulation)

		unitsBefore = len(self.simulation.unitsOf(self.playerTrajan))

		# WHEN
		Combat.doMeleeAttack(attacker, defender, self.simulation)
		unitsAfter = len(self.simulation.unitsOf(self.playerTrajan))

		# THEN
		self.assertEqual(unitsBefore, 1)
		self.assertEqual(unitsAfter, 0)

	def test_melee_killed_warrior_against_warrior(self):
		# GIVEN
		attacker = Unit(HexPoint(5, 6), UnitType.warrior, self.playerAlexander)
		attacker.changeDamage(93, None, self.simulation)
		self.simulation.addUnit(attacker)

		defender = Unit(HexPoint(5, 5), UnitType.warrior, self.playerTrajan)
		self.simulation.addUnit(defender)

		self.playerTrajan.doFirstContactWith(self.playerAlexander, self.simulation)

		unitsBefore = len(self.simulation.unitsOf(self.playerTrajan))

		# WHEN
		Combat.doMeleeAttack(attacker, defender, self.simulation)
		unitsAfter = len(self.simulation.unitsOf(self.playerTrajan))

		# THEN
		self.assertEqual(unitsBefore, 1)
		self.assertEqual(unitsAfter, 1)

	def test_combat_warrior_against_city(self):
		# GIVEN
		attacker = Unit(HexPoint(5, 6), UnitType.warrior, self.playerAlexander)
		self.simulation.addUnit(attacker)

		city = City("Berlin", HexPoint(5, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.simulation)
		self.simulation.addCity(city)

		self.playerTrajan.doFirstContactWith(self.playerAlexander, self.simulation)

		# WHEN
		result = Combat.doMeleeAttack(attacker, city, self.simulation)

		# THEN
		self.assertBetween(result.attackerDamage, 12, 26)
		self.assertBetween(result.defenderDamage, 13, 21)

	def test_conquer_city(self):
		# GIVEN
		attacker = Unit(HexPoint(5, 6), UnitType.warrior, self.playerAlexander)
		self.simulation.addUnit(attacker)

		city = City("Berlin", HexPoint(5, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.simulation)
		city.setDamage(190)
		self.simulation.addCity(city)

		city2 = City("Potsdam", HexPoint(10, 5), isCapital=False, player=self.playerTrajan)
		city2.initialize(self.simulation)
		self.simulation.addCity(city2)

		numberOfCitiesBefore = len(self.simulation.citiesOf(self.playerTrajan))

		self.playerTrajan.doFirstContactWith(self.playerAlexander, self.simulation)

		# WHEN
		result = Combat.doMeleeAttack(attacker, city, self.simulation)

		# THEN
		self.assertBetween(result.attackerDamage, 12, 26)
		self.assertBetween(result.defenderDamage, 13, 21)

		cityAtLocation = self.simulation.cityAt(HexPoint(5, 5))
		numberOfCitiesAfter = len(self.simulation.citiesOf(self.playerTrajan))
		self.assertEqual(cityAtLocation.player.leader, LeaderType.alexander)
		self.assertEqual(numberOfCitiesBefore, 2)
		self.assertEqual(numberOfCitiesAfter, 1)

	def test_ranged_city_against_city(self):
		# this is impossible in real game

		# GIVEN
		city = City("Berlin", HexPoint(5, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.simulation)
		self.simulation.addCity(city)

		city2 = City("Berlin", HexPoint(5, 7), isCapital=True, player=self.playerAlexander)
		city2.initialize(self.simulation)
		self.simulation.addCity(city2)

		# WHEN + THEN
		with pytest.raises(Exception):
			Combat.doRangedAttack(city, city2, self.simulation)

	def test_ranged_city_against_melee(self):
		# GIVEN
		city = City("Berlin", HexPoint(5, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.simulation)
		self.simulation.addCity(city)

		defender = Unit(HexPoint(5, 6), UnitType.warrior, self.playerAlexander)
		self.simulation.addUnit(defender)

		self.playerTrajan.doFirstContactWith(self.playerAlexander, self.simulation)

		# WHEN
		result = Combat.doRangedAttack(city, defender, self.simulation)

		# THEN
		self.assertBetween(result.defenderDamage, 11, 30)

	def test_ranged_archer_against_melee(self):
		# GIVEN
		attacker = Unit(HexPoint(5, 5), UnitType.archer, self.playerTrajan)
		self.simulation.addUnit(attacker)

		defender = Unit(HexPoint(5, 6), UnitType.warrior, self.playerAlexander)
		self.simulation.addUnit(defender)

		self.playerTrajan.doFirstContactWith(self.playerAlexander, self.simulation)

		# WHEN
		result = Combat.doRangedAttack(attacker, defender, self.simulation)

		# THEN
		self.assertBetween(result.defenderDamage, 33, 49)

	def test_ranged_kill_slinger_against_melee(self):
		# GIVEN
		attacker = Unit(HexPoint(5, 5), UnitType.slinger, self.playerTrajan)
		self.simulation.addUnit(attacker)

		defender = Unit(HexPoint(5, 6), UnitType.warrior, self.playerAlexander)
		defender.changeDamage(95, None, self.simulation)
		self.simulation.addUnit(defender)

		self.playerTrajan.doFirstContactWith(self.playerAlexander, self.simulation)

		numUnitsBefore = len(self.simulation.unitsOf(self.playerAlexander))

		# WHEN
		result = Combat.doRangedAttack(attacker, defender, self.simulation)
		numUnitsAfter = len(self.simulation.unitsOf(self.playerAlexander))

		# THEN
		self.assertBetween(result.defenderDamage, 22, 33)
		self.assertEqual(numUnitsBefore, 1)
		self.assertEqual(numUnitsAfter, 0)
		self.assertTrue(self.playerTrajan.techs.eurekaTriggeredFor(TechType.archery))

	def test_ranged_archer_against_city(self):
		# GIVEN
		attacker = Unit(HexPoint(5, 5), UnitType.archer, self.playerAlexander)
		self.simulation.addUnit(attacker)

		city = City("Berlin", HexPoint(5, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.simulation)
		self.simulation.addCity(city)

		self.playerTrajan.doFirstContactWith(self.playerAlexander, self.simulation)
		self.playerAlexander.startTurn(self.simulation)

		# WHEN
		result = Combat.doRangedAttack(attacker, city, self.simulation)

		# THEN
		self.assertBetween(result.defenderDamage, 7, 11)

