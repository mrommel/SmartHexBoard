import copy
import os
import unittest

import django

from smarthexboard.smarthexboardlib.game.baseTypes import HandicapType
from smarthexboard.smarthexboardlib.game.cities import City
from smarthexboard.smarthexboardlib.game.civilizations import LeaderType
from smarthexboard.smarthexboardlib.game.game import GameModel
from smarthexboard.smarthexboardlib.game.generation import UserInterfaceImpl
from smarthexboard.smarthexboardlib.game.greatPersons import GreatPerson
from smarthexboard.smarthexboardlib.game.players import Player
from smarthexboard.smarthexboardlib.game.promotions import UnitPromotionType
from smarthexboard.smarthexboardlib.game.states.ages import AgeType
from smarthexboard.smarthexboardlib.game.states.dedications import DedicationType
from smarthexboard.smarthexboardlib.game.states.victories import VictoryType
from smarthexboard.smarthexboardlib.game.types import TechType
from smarthexboard.smarthexboardlib.game.unitMissions import UnitMission
from smarthexboard.smarthexboardlib.game.unitTypes import UnitType, UnitMissionType, MoveOption
from smarthexboard.smarthexboardlib.game.units import Unit
from smarthexboard.smarthexboardlib.map.base import HexPoint
from smarthexboard.smarthexboardlib.map.improvements import ImprovementType
from smarthexboard.smarthexboardlib.map.types import TerrainType, FeatureType
from smarthexboard.tests.test_utils import MapModelMock

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()


class TestUnit(unittest.TestCase):
	def setUp(self) -> None:
		self.mapModel = MapModelMock(24, 20, TerrainType.grass)

		self.playerBarbarian = Player(leader=LeaderType.barbar, cityState=None, human=False)
		self.playerBarbarian.initialize()

		self.playerTrajan = Player(leader=LeaderType.trajan, cityState=None, human=False)
		self.playerTrajan.initialize()

		self.playerVictoria = Player(leader=LeaderType.victoria, cityState=None, human=True)
		self.playerVictoria.initialize()

		self.simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[self.playerBarbarian, self.playerTrajan, self.playerVictoria],
			map=self.mapModel
		)

		# add UI
		self.simulation.userInterface = UserInterfaceImpl()

	def test_move(self):
		# GIVEN
		warrior = Unit(HexPoint(5, 5), UnitType.warrior, self.playerTrajan)

		# WHEN
		warrior.doMoveOnto(HexPoint(6, 5), self.simulation)

		# THEN
		self.assertEqual(warrior.location, HexPoint(6, 5))

	def test_maxMoves(self):
		# GIVEN
		warrior = Unit(HexPoint(5, 5), UnitType.warrior, self.playerTrajan)
		builder = Unit(HexPoint(5, 6), UnitType.builder, self.playerTrajan)
		missionary = Unit(HexPoint(5, 7), UnitType.missionary, self.playerTrajan)
		cavalry = Unit(HexPoint(5, 8), UnitType.horseman, self.playerTrajan)
		swordman = Unit(HexPoint(5, 5), UnitType.swordman, self.playerTrajan)

		# WHEN
		maxMovesWarriorNormal = warrior.maxMoves(self.simulation)
		maxMovesBuilderNormal = builder.maxMoves(self.simulation)

		# golden age + monumentality
		self.playerTrajan._currentAgeValue = AgeType.golden
		self.playerTrajan._currentDedicationsValue = [DedicationType.monumentality]
		maxMovesBuilderGoldenAgeMonumentality = builder.maxMoves(self.simulation)

		# golden age + exodusOfTheEvangelists
		self.playerTrajan._currentAgeValue = AgeType.golden
		self.playerTrajan._currentDedicationsValue = [DedicationType.exodusOfTheEvangelists]
		maxMovesBuilderGoldenAgeExodusOfTheEvangelists = missionary.maxMoves(self.simulation)

		# reset
		self.playerTrajan._currentAgeValue = AgeType.normal
		self.playerTrajan._currentDedicationsValue = []

		# promotion commando
		self.assertTrue(warrior.doPromote(UnitPromotionType.battlecry, self.simulation))
		self.assertTrue(warrior.doPromote(UnitPromotionType.commando, self.simulation))
		maxMovesWarriorCommando = warrior.maxMoves(self.simulation)
		warrior._promotions._promotions = []

		# promotion pursuit
		cavalry._promotions._promotions = []
		self.assertTrue(cavalry.doPromote(UnitPromotionType.caparison, self.simulation))
		self.assertTrue(cavalry.doPromote(UnitPromotionType.depredation, self.simulation))
		self.assertTrue(cavalry.doPromote(UnitPromotionType.pursuit, self.simulation))
		maxMovesCavalryPursuit = cavalry.maxMoves(self.simulation)
		cavalry._promotions._promotions = []

		# generals
		generalBoudica = Unit(HexPoint(5, 4), UnitType.general, self.playerTrajan)
		generalBoudica.greatPerson = GreatPerson.boudica
		self.simulation.addUnit(generalBoudica)
		maxMovesSwordmanGeneral = swordman.maxMoves(self.simulation)

		# THEN
		self.assertEqual(maxMovesWarriorNormal, 2)
		self.assertEqual(maxMovesBuilderNormal, 2)
		self.assertEqual(maxMovesBuilderGoldenAgeMonumentality, 4)
		self.assertEqual(maxMovesBuilderGoldenAgeExodusOfTheEvangelists, 5)

		self.assertEqual(maxMovesWarriorCommando, 3)
		self.assertEqual(maxMovesCavalryPursuit, 5)
		self.assertEqual(maxMovesSwordmanGeneral, 3)

		# fixme more conditions

	def test_readyToMove(self):
		# GIVEN
		warrior = Unit(HexPoint(5, 5), UnitType.warrior, self.playerTrajan)

		# WHEN
		readyToMoveNormal = warrior.readyToMove()

		# garrison
		city = City("Berlin", HexPoint(5, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.simulation)
		self.simulation.addCity(city)
		warrior.doGarrison(self.simulation)
		readyToMoveGarrisoned = warrior.readyToMove()

		# THEN
		self.assertTrue(readyToMoveNormal)
		self.assertFalse(readyToMoveGarrisoned)

	def test_isDead(self):
		# GIVEN
		warrior = Unit(HexPoint(5, 5), UnitType.warrior, self.playerTrajan)

		# WHEN
		isDeadNormal = warrior.isDead()

		warrior.changeDamage(101, None, self.simulation)
		isDeadDamaged = warrior.isDead()

		# THEN
		self.assertFalse(isDeadNormal)
		self.assertTrue(isDeadDamaged)

	def test_isPlayer(self):
		# GIVEN
		warriorAI = Unit(HexPoint(5, 5), UnitType.warrior, self.playerTrajan)
		warriorHuman = Unit(HexPoint(5, 6), UnitType.warrior, self.playerVictoria)

		# WHEN
		# ...

		# THEN
		self.assertFalse(warriorAI.isHuman())
		self.assertTrue(warriorHuman.isHuman())
		self.assertFalse(warriorAI.isBarbarian())
		self.assertFalse(warriorHuman.isBarbarian())

	def test_sight(self):
		# GIVEN
		scout = Unit(HexPoint(5, 5), UnitType.scout, self.playerTrajan)
		galley = Unit(HexPoint(5, 6), UnitType.galley, self.playerTrajan)

		# WHEN
		sightScoutNormal = scout.sight()
		self.assertTrue(scout.doPromote(UnitPromotionType.ranger, self.simulation))
		self.assertTrue(scout.doPromote(UnitPromotionType.sentry, self.simulation))
		self.assertTrue(scout.doPromote(UnitPromotionType.spyglass, self.simulation))
		sightScoutSpyglass = scout.sight()

		sightGalleyNormal = galley.sight()
		self.assertTrue(galley.doPromote(UnitPromotionType.helmsman, self.simulation))
		self.assertTrue(galley.doPromote(UnitPromotionType.rutter, self.simulation))
		sightGalleySpyglass = galley.sight()

		# THEN
		self.assertEqual(sightScoutNormal, 2)
		self.assertEqual(sightScoutSpyglass, 3)
		self.assertEqual(sightGalleyNormal, 2)
		self.assertEqual(sightGalleySpyglass, 3)

	def test_eq(self):
		# GIVEN
		scout = Unit(HexPoint(5, 5), UnitType.scout, self.playerTrajan)
		galley = Unit(HexPoint(5, 6), UnitType.galley, self.playerTrajan)

		# WHEN

		# THEN
		self.assertEqual(scout, scout)
		self.assertNotEqual(scout, galley)
		self.assertNotEqual(scout, None)

	def test_numberOfAttacksPerTurn(self):
		# GIVEN
		warrior = Unit(HexPoint(5, 5), UnitType.warrior, self.playerTrajan)
		knight = Unit(HexPoint(5, 6), UnitType.knight, self.playerTrajan)

		# WHEN
		numberOfAttacksPerTurnNormal = warrior.numberOfAttacksPerTurn(self.simulation)

		self.assertTrue(knight.doPromote(UnitPromotionType.charge, self.simulation))
		self.assertTrue(knight.doPromote(UnitPromotionType.marauding, self.simulation))
		self.assertTrue(knight.doPromote(UnitPromotionType.rout, self.simulation))
		self.assertTrue(knight.doPromote(UnitPromotionType.armorPiercing, self.simulation))
		self.assertTrue(knight.doPromote(UnitPromotionType.breakthrough, self.simulation))
		numberOfAttacksPerTurnBreakthrough = knight.numberOfAttacksPerTurn(self.simulation)

		self.assertTrue(warrior.doPromote(UnitPromotionType.battlecry, self.simulation))
		self.assertTrue(warrior.doPromote(UnitPromotionType.tortoise, self.simulation))
		self.assertTrue(warrior.doPromote(UnitPromotionType.zweihander, self.simulation))
		self.assertTrue(warrior.doPromote(UnitPromotionType.eliteGuard, self.simulation))
		numberOfAttacksPerTurnEliteGuard = warrior.numberOfAttacksPerTurn(self.simulation)

		# THEN
		self.assertEqual(numberOfAttacksPerTurnNormal, 1)
		self.assertEqual(numberOfAttacksPerTurnBreakthrough, 2)
		self.assertEqual(numberOfAttacksPerTurnEliteGuard, 2)

	def test_isGreatPerson(self):
		# GIVEN
		scout = Unit(HexPoint(5, 5), UnitType.scout, self.playerTrajan)
		general = Unit(HexPoint(5, 6), UnitType.general, self.playerTrajan)
		general.greatPerson = GreatPerson.boudica

		# WHEN

		# THEN
		self.assertFalse(scout.isGreatPerson())
		self.assertTrue(general.isGreatPerson())

	def test_doKill(self):
		# GIVEN
		barbarianWarrior = Unit(HexPoint(5, 5), UnitType.barbarianWarrior, self.playerBarbarian)

		# WHEN
		eurekaBefore = self.playerTrajan.techs.eurekaValue(TechType.bronzeWorking)
		barbarianWarrior.doKill(delayed=False, otherPlayer=self.playerTrajan, simulation=self.simulation)
		eurekaAfter = self.playerTrajan.techs.eurekaValue(TechType.bronzeWorking)

		# THEN
		self.assertEqual(eurekaBefore, 0)
		self.assertEqual(eurekaAfter, 1)

	def test_canEmbarkInto(self):
		# GIVEN
		self.mapModel.modifyTerrainAt(HexPoint(6, 5), TerrainType.ocean)
		self.playerTrajan.techs.discover(TechType.shipBuilding, self.simulation)

		warrior = Unit(HexPoint(5, 5), UnitType.warrior, self.playerTrajan)

		# WHEN
		warrior._isEmbarkedValue = True
		canEmbarkIntoEmbarked = warrior.canEmbarkInto(point=None, simulation=self.simulation)
		warrior._isEmbarkedValue = False

		canEmbarkIntoOcean = warrior.canEmbarkInto(point=HexPoint(6, 5), simulation=self.simulation)

		warrior._movesValue = 0
		canEmbarkIntoNoMoves = warrior.canEmbarkInto(point=None, simulation=self.simulation)
		warrior._movesValue = 2

		# THEN
		self.assertEqual(canEmbarkIntoEmbarked, False)
		self.assertEqual(canEmbarkIntoOcean, True)
		self.assertEqual(canEmbarkIntoNoMoves, False)

	def test_doEmbark(self):
		# GIVEN
		self.mapModel.modifyTerrainAt(HexPoint(6, 5), TerrainType.ocean)
		self.playerTrajan.techs.discover(TechType.shipBuilding, self.simulation)

		warrior = Unit(HexPoint(5, 5), UnitType.warrior, self.playerTrajan)

		# WHEN
		doEmbarkNormal = warrior.canEmbarkInto(point=HexPoint(6, 5), simulation=self.simulation)

		# THEN
		self.assertEqual(doEmbarkNormal, True)

	def test_canPillage(self):
		# GIVEN
		self.mapModel.tileAt(HexPoint(5, 5)).setImprovement(ImprovementType.farm)

		warrior = Unit(HexPoint(5, 5), UnitType.warrior, self.playerTrajan)

		# WHEN
		canPillageNormal = warrior.canPillageAt(HexPoint(5, 5), self.simulation)

		warrior._isEmbarkedValue = True
		canPillageEmbarked = warrior.canEmbarkInto(point=None, simulation=self.simulation)
		warrior._isEmbarkedValue = False

		self.mapModel.tileAt(HexPoint(5, 5)).setImprovementPillaged(True)
		canPillagePillaged = warrior.canEmbarkInto(point=None, simulation=self.simulation)
		self.mapModel.tileAt(HexPoint(5, 5)).setImprovementPillaged(False)

		# THEN
		self.assertEqual(canPillageNormal, True)
		self.assertEqual(canPillageEmbarked, False)
		self.assertEqual(canPillagePillaged, False)

	def test_canHeal(self):
		# GIVEN
		warrior = Unit(HexPoint(5, 5), UnitType.warrior, self.playerTrajan)
		barbarianWarrior = Unit(HexPoint(5, 5), UnitType.barbarianWarrior, self.playerBarbarian)

		# WHEN
		canHealNormal = warrior.canHeal(self.simulation)
		canHealBarbarian = barbarianWarrior.canHeal(self.simulation)

		# damage
		warrior.changeDamage(20, None, self.simulation)

		canHealDamaged = warrior.canHeal(self.simulation)

		warrior._isEmbarkedValue = True
		canHealEmbarked = warrior.canHeal(self.simulation)
		warrior._isEmbarkedValue = False

		# todo PolicyCardType.twilightValor

		# THEN
		self.assertEqual(canHealNormal, False)
		self.assertEqual(canHealBarbarian, False)
		self.assertEqual(canHealDamaged, True)
		self.assertEqual(canHealEmbarked, False)

	def test_gainedPromotions(self):
		# GIVEN
		warrior = Unit(HexPoint(5, 5), UnitType.warrior, self.playerTrajan)

		# WHEN
		gainedPromotionsNormal = copy.deepcopy(warrior.gainedPromotions())

		self.assertTrue(warrior._promotions.earnPromotion(UnitPromotionType.battlecry))
		gainedPromotionsBattlecry = warrior.gainedPromotions()

		# THEN
		self.assertListEqual(gainedPromotionsNormal, [])
		self.assertListEqual(gainedPromotionsBattlecry, [UnitPromotionType.battlecry])

	def test_canStartMission(self):
		# GIVEN
		warriorGarrison = Unit(HexPoint(5, 5), UnitType.warrior, self.playerTrajan)
		warriorSkip = Unit(HexPoint(5, 6), UnitType.warrior, self.playerTrajan)

		# WHEN

		# garrison
		canGarrisonOutsideCity = warriorGarrison.canStartMission(UnitMission(UnitMissionType.garrison), self.simulation)
		city = City("Berlin", HexPoint(5, 5), isCapital=False, player=self.playerTrajan)
		city.initialize(self.simulation)
		self.simulation.addCity(city)
		canGarrisonInCity = warriorGarrison.canStartMission(UnitMission(UnitMissionType.garrison), self.simulation)

		canSkipAtLocation = warriorSkip.canStartMission(UnitMission(UnitMissionType.skip), self.simulation)
		canSkipAtTarget = warriorSkip.canStartMission(UnitMission(UnitMissionType.skip, target=HexPoint(5, 6)), self.simulation)

		# THEN
		self.assertFalse(canGarrisonOutsideCity)
		self.assertTrue(canGarrisonInCity)

		self.assertTrue(canSkipAtTarget)
		self.assertTrue(canSkipAtLocation)

	def test_canMoveInto(self):
		# GIVEN
		barbarianWarrior = Unit(HexPoint(5, 4), UnitType.barbarianWarrior, self.playerBarbarian)
		self.simulation.tileAt(HexPoint(5, 3)).setOwner(self.playerTrajan)
		warrior = Unit(HexPoint(5, 5), UnitType.warrior, self.playerTrajan)
		self.simulation.tileAt(HexPoint(4, 5)).setFeature(FeatureType.mountKilimanjaro)

		# WHEN
		barbarianWarriorCanMoveInto = barbarianWarrior.canMoveInto(HexPoint(5, 3), [], self.simulation)
		warriorCanMoveInto = warrior.canMoveInto(HexPoint(5, 6), [], self.simulation)

		warrior._numberOfAttacksMade = 1  # out of attacks
		warriorCanMoveIntoOutOfAttacks = warrior.canMoveInto(HexPoint(5, 6), [MoveOption.attack], self.simulation)
		warrior._numberOfAttacksMade = 0

		# impassable
		warriorCanMoveIntoImpassable = warrior.canMoveInto(HexPoint(4, 5), [], self.simulation)

		# if simulation.isEnemyVisibleAt(point, self.player):
		#   return False

		# THEN
		self.assertFalse(barbarianWarriorCanMoveInto)
		self.assertTrue(warriorCanMoveInto)
		self.assertFalse(warriorCanMoveIntoOutOfAttacks)
		self.assertFalse(warriorCanMoveIntoImpassable)
