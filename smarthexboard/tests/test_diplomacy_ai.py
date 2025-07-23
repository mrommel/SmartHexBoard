import os
import unittest

import django
import pytest
from django.test import TestCase

from smarthexboard.smarthexboardlib.game.ai.baseTypes import PlayerStateAllWars
from smarthexboard.smarthexboardlib.game.ai.diplomaticTypes import MajorPlayerApproachType, MinorPlayerApproachType, \
	DiplomaticDeal
from smarthexboard.smarthexboardlib.game.baseTypes import HandicapType, AggressivePostureType
from smarthexboard.smarthexboardlib.game.cities import City
from smarthexboard.smarthexboardlib.game.cityStates import CityStateType
from smarthexboard.smarthexboardlib.game.civilizations import LeaderType
from smarthexboard.smarthexboardlib.game.game import GameModel
from smarthexboard.smarthexboardlib.game.generation import UserInterfaceImpl
from smarthexboard.smarthexboardlib.game.moments import MomentType
from smarthexboard.smarthexboardlib.game.notifications import NotificationType
from smarthexboard.smarthexboardlib.game.playerMechanics import DiplomaticAI
from smarthexboard.smarthexboardlib.game.players import Player
from smarthexboard.smarthexboardlib.game.states.victories import VictoryType
from smarthexboard.smarthexboardlib.game.types import CivicType
from smarthexboard.smarthexboardlib.game.unitTypes import UnitType
from smarthexboard.smarthexboardlib.game.units import Unit
from smarthexboard.smarthexboardlib.map.base import HexPoint
from smarthexboard.tests.test_utils import MapModelMock

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smarthexboard.settings')
django.setup()


class TestDiplomaticAI(unittest.TestCase):
	def setUp(self) -> None:
		self.mapModel = MapModelMock.duelMap()

		# players
		self.playerBarbarian = Player(LeaderType.barbar, human=False)
		self.playerBarbarian.initialize()

		self.seoulCityState = Player(LeaderType.cityState, cityState=CityStateType.seoul, human=False)
		self.seoulCityState.initialize()

		self.playerAlexander = Player(LeaderType.alexander, human=False)
		self.playerAlexander.initialize()

		self.playerTrajan = Player(LeaderType.trajan, human=True)
		self.playerTrajan.initialize()

		self.simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[self.playerBarbarian, self.seoulCityState, self.playerAlexander, self.playerTrajan],
			map=self.mapModel
		)

		# add UI
		self.simulation.userInterface = UserInterfaceImpl()

		# add human scout (so that the game is not finished)
		playerTrajanScout = Unit(HexPoint(11, 19), UnitType.scout, self.playerTrajan)
		self.simulation.addUnit(playerTrajanScout)

	def test_constructor(self):
		diplomacy = DiplomaticAI(self.playerAlexander)

		self.assertEqual(diplomacy.stateOfAllWars(), PlayerStateAllWars.neutral)
		self.assertEqual(diplomacy.isAtWarWith(self.playerTrajan), False)

	def test_update_first_cityState_active_human(self):
		diplomacy = self.seoulCityState.diplomacyAI

		self.seoulCityState.doFirstContactWith(self.playerTrajan, self.simulation)

		self.playerTrajan.turnActive = True
		self.simulation.updateActivePlayer(self.playerTrajan)
		diplomacy.update(self.simulation)

		self.assertTrue(self.seoulCityState.hasMoment(MomentType.metNewCivilization, civilization=self.playerTrajan.leader.civilization()))
		self.assertEqual(self.playerTrajan.envoys.unassignedEnvoys(), 0)  # envoy is assigned to seoul
		self.assertEqual(self.playerTrajan.envoys.envoysIn(CityStateType.seoul), 1)
		self.assertTrue(len(list(filter(lambda n: n.notificationType == NotificationType.metCityState, self.playerTrajan.notifications.notifications))) > 0)

	def test_update_first_cityState_active_cityState(self):
		diplomacy = self.playerAlexander.diplomacyAI

		self.playerAlexander.doFirstContactWith(self.seoulCityState, self.simulation)

		self.seoulCityState.turnActive = True
		self.simulation.updateActivePlayer(self.seoulCityState)
		diplomacy.update(self.simulation)

		self.assertEqual(self.playerAlexander.envoys.unassignedEnvoys(), 0)  # envoy is assigned to seoul
		self.assertEqual(self.playerAlexander.envoys.envoysIn(CityStateType.seoul), 0)

	def test_canSendDelegationTo_no_capital(self):
		# given
		self.playerAlexander.doFirstContactWith(self.playerTrajan, self.simulation)

		# when
		canSend = self.playerAlexander.diplomacyAI.canSendDelegationTo(self.playerTrajan, self.simulation)

		# then
		self.assertFalse(canSend)

	def test_canSendDelegationTo_not_enough_money(self):
		# given
		self.playerAlexander.doFirstContactWith(self.playerTrajan, self.simulation)

		capital = City("Capital", HexPoint(12, 12), isCapital=True, player=self.playerTrajan)
		self.simulation.addCity(capital)

		# when
		canSend = self.playerAlexander.diplomacyAI.canSendDelegationTo(self.playerTrajan, self.simulation)

		# then
		self.assertFalse(canSend)

	def test_canSendDelegationTo_has_already_sent(self):
		# given
		self.playerAlexander.doFirstContactWith(self.playerTrajan, self.simulation)

		capital = City("Capital", HexPoint(12, 12), isCapital=True, player=self.playerTrajan)
		self.simulation.addCity(capital)

		self.playerAlexander.treasury.changeGoldBy(60)

		self.playerAlexander.diplomacyAI.doSendDelegationTo(self.playerTrajan, self.simulation)

		# when
		canSend = self.playerAlexander.diplomacyAI.canSendDelegationTo(self.playerTrajan, self.simulation)

		# then
		self.assertFalse(canSend)

	def test_canSendDelegationTo_blocking_civic(self):
		# given
		self.playerAlexander.doFirstContactWith(self.playerTrajan, self.simulation)

		capital = City("Capital", HexPoint(12, 12), isCapital=True, player=self.playerTrajan)
		self.simulation.addCity(capital)

		self.playerAlexander.treasury.changeGoldBy(50)
		self.playerAlexander.civics.discover(CivicType.diplomaticService, self.simulation)

		# when
		canSend = self.playerAlexander.diplomacyAI.canSendDelegationTo(self.playerTrajan, self.simulation)

		# then
		self.assertFalse(canSend)

	def test_canSendDelegationTo_wrong_approach(self):
		# given
		self.playerAlexander.doFirstContactWith(self.playerTrajan, self.simulation)

		capital = City("Capital", HexPoint(12, 12), isCapital=True, player=self.playerTrajan)
		self.simulation.addCity(capital)

		self.playerAlexander.treasury.changeGoldBy(50)
		self.playerAlexander.diplomacyAI.updateMajorCivApproachTowards(self.playerTrajan, MajorPlayerApproachType.hostile)

		# when
		canSend = self.playerAlexander.diplomacyAI.canSendDelegationTo(self.playerTrajan, self.simulation)

		# then
		self.assertFalse(canSend)

	def test_canSendDelegationTo_success(self):
		# given
		self.playerAlexander.doFirstContactWith(self.playerTrajan, self.simulation)

		capital = City("Capital", HexPoint(12, 12), isCapital=True, player=self.playerTrajan)
		self.simulation.addCity(capital)

		self.playerAlexander.treasury.changeGoldBy(50)

		# when
		canSend = self.playerAlexander.diplomacyAI.canSendDelegationTo(self.playerTrajan, self.simulation)

		# then
		self.assertTrue(canSend)

	def test_majorApproachTowards(self):
		# given
		self.playerAlexander.doFirstContactWith(self.seoulCityState, self.simulation)

		# when - then
		with pytest.raises(Exception):
			self.playerAlexander.diplomacyAI.majorApproachTowards(self.playerBarbarian)

		with pytest.raises(Exception):
			self.playerAlexander.diplomacyAI.majorApproachTowards(self.seoulCityState)

	def test_updateMinorCivApproaches(self):
		# given
		self.playerAlexander.doFirstContactWith(self.seoulCityState, self.simulation)

		self.playerAlexander.diplomacyAI.updateProximityTo(self.seoulCityState, self.simulation)

		# when
		self.playerAlexander.diplomacyAI.updateMinorCivApproaches(self.simulation)

		# then
		self.assertEqual(self.playerAlexander.diplomacyAI.minorApproachTowards(self.seoulCityState), MinorPlayerApproachType.ignore)

	def test_updateMajorCivApproaches(self):
		# given
		self.playerAlexander.doFirstContactWith(self.playerTrajan, self.simulation)

		self.playerAlexander.diplomacyAI.updateProximityTo(self.playerTrajan, self.simulation)
		self.playerAlexander.diplomacyAI.updateMajorCivApproachTowards(self.playerTrajan, MajorPlayerApproachType.hostile)
		self.playerAlexander.diplomacyAI.updateOpinions(self.simulation)

		# when
		self.playerAlexander.diplomacyAI.updateMajorCivApproaches(self.simulation)

		# then
		self.assertEqual(self.playerAlexander.diplomacyAI.majorApproachTowards(self.playerTrajan), MajorPlayerApproachType.neutral)

	def test_doUpdateMilitaryAggressivePostures_openBorders(self):
		# given
		self.playerAlexander.doFirstContactWith(self.playerTrajan, self.simulation)

		self.playerAlexander.diplomacyAI.updateProximityTo(self.playerTrajan, self.simulation)
		self.playerAlexander.diplomacyAI.establishOpenBorderAgreementWith(self.playerTrajan, 0)

		# when
		self.playerAlexander.diplomacyAI.doUpdateMilitaryAggressivePostures(self.simulation)

		# then
		militaryAggressivePosture: AggressivePostureType = self.playerAlexander.diplomacyAI.militaryAggressivePostureOf(self.playerTrajan)
		self.assertEqual(militaryAggressivePosture, AggressivePostureType.none)

	def test_doUpdateMilitaryAggressivePostures_at_war(self):
		# given
		warrior1 = Unit(HexPoint(5, 5), UnitType.knight, self.playerTrajan)
		self.simulation.addUnit(warrior1)

		warrior2 = Unit(HexPoint(5, 6), UnitType.catapult, self.playerTrajan)
		self.simulation.addUnit(warrior2)

		city = City("berlin", HexPoint(8, 8), isCapital=True, player=self.playerAlexander)
		self.simulation.addCity(city)

		self.playerAlexander.doFirstContactWith(self.playerTrajan, self.simulation)

		self.playerAlexander.diplomacyAI.updateProximityTo(self.playerTrajan, self.simulation)
		self.playerAlexander.diplomacyAI.doDeclareWarTo(self.playerTrajan, self.simulation)

		# when
		self.playerAlexander.diplomacyAI.doUpdateMilitaryAggressivePostures(self.simulation)

		# then
		militaryAggressivePosture: AggressivePostureType = self.playerAlexander.diplomacyAI.militaryAggressivePostureOf(self.playerTrajan)
		self.assertEqual(militaryAggressivePosture, AggressivePostureType.low)

	def test_doContactPlayer_normal(self):
		# given
		self.playerAlexander.doFirstContactWith(self.playerTrajan, self.simulation)

		# when
		self.playerAlexander.diplomacyAI.doContactPlayer(self.playerTrajan, self.simulation)

		# then
		# fixme: check deals

	def test_doContactPlayer_atWar(self):
		# given
		self.playerAlexander.doFirstContactWith(self.playerTrajan, self.simulation)

		self.playerAlexander.diplomacyAI.updateProximityTo(self.playerTrajan, self.simulation)
		self.playerAlexander.diplomacyAI.doDeclareWarTo(self.playerTrajan, self.simulation)

		self.simulation.currentTurn = 10

		# when
		self.playerAlexander.diplomacyAI.doContactPlayer(self.playerTrajan, self.simulation)

		# then
		# fixme: check deals


class TestDiplomaticDeal(TestCase):
	def setUp(self) -> None:
		self.mapModel = MapModelMock.duelMap()

		# players
		self.playerBarbarian = Player(LeaderType.barbar, human=False)
		self.playerBarbarian.initialize()

		self.seoulCityState = Player(LeaderType.cityState, cityState=CityStateType.seoul, human=False)
		self.seoulCityState.initialize()

		self.playerAlexander = Player(LeaderType.alexander, human=False)
		self.playerAlexander.initialize()

		self.playerVictoria = Player(LeaderType.victoria, human=False)
		self.playerVictoria.initialize()

		self.playerTrajan = Player(LeaderType.trajan, human=True)
		self.playerTrajan.initialize()

		self.simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[self.playerBarbarian, self.seoulCityState, self.playerAlexander, self.playerVictoria, self.playerTrajan],
			map=self.mapModel
		)

		# add UI
		self.simulation.userInterface = UserInterfaceImpl()

		# add human scout (so that the game is not finished)
		playerTrajanScout = Unit(HexPoint(11, 19), UnitType.scout, self.playerTrajan)
		self.simulation.addUnit(playerTrajanScout)

	def test_sendDelegation_fromHuman(self):
		# GIVEN
		self.playerTrajan.treasury.changeGoldBy(200)
		self.playerAlexander.treasury.changeGoldBy(200)
		self.playerVictoria.treasury.changeGoldBy(200)

		# build cities
		self.playerAlexander.foundAt(HexPoint(25, 5), "Alexander Capital", self.simulation)
		self.playerTrajan.foundAt(HexPoint(3, 5), "Trajan Capital", self.simulation)
		self.playerVictoria.foundAt(HexPoint(8, 5), "Victoria City", self.simulation)

		self.playerTrajan.doFirstContactWith(self.playerAlexander, self.simulation)
		self.playerTrajan.doFirstContactWith(self.playerVictoria, self.simulation)
		self.playerAlexander.doFirstContactWith(self.playerVictoria, self.simulation)

		beforeContact = self.playerTrajan.hasSentDelegationTo(self.playerAlexander)

		# WHEN
		self.playerTrajan.diplomacyAI.doContactPlayer(self.playerAlexander, self.simulation)
		afterContact = self.playerTrajan.hasSentDelegationTo(self.playerAlexander)

		# THEN
		self.assertFalse(beforeContact, "Delegation should not have been sent before contact")
		self.assertTrue(afterContact, "Delegation should have been sent after contact")

	def test_sendDelegation_fromAI(self):
		# GIVEN
		self.playerTrajan.treasury.changeGoldBy(200)
		self.playerAlexander.treasury.changeGoldBy(200)
		self.playerVictoria.treasury.changeGoldBy(200)

		# build cities
		self.playerAlexander.foundAt(HexPoint(25, 5), "Alexander Capital", self.simulation)
		self.playerTrajan.foundAt(HexPoint(3, 5), "Trajan Capital", self.simulation)
		self.playerVictoria.foundAt(HexPoint(8, 5), "Victoria City", self.simulation)

		self.playerTrajan.doFirstContactWith(self.playerAlexander, self.simulation)
		self.playerTrajan.doFirstContactWith(self.playerVictoria, self.simulation)
		self.playerAlexander.doFirstContactWith(self.playerVictoria, self.simulation)

		beforeContact = self.playerVictoria.hasSentDelegationTo(self.playerAlexander)

		# WHEN
		self.playerVictoria.diplomacyAI.doContactPlayer(self.playerAlexander, self.simulation)
		afterContact = self.playerVictoria.hasSentDelegationTo(self.playerAlexander)

		# THEN
		self.assertFalse(beforeContact, "Delegation should not have been sent before contact")
		self.assertTrue(afterContact, "Delegation should have been sent after contact")

	def test_doEqualizeDealWithAI_validDeal(self):
		# GIVEN
		self.playerTrajan.treasury.changeGoldBy(200)
		self.playerAlexander.treasury.changeGoldBy(200)
		self.playerVictoria.treasury.changeGoldBy(200)

		# build cities
		self.playerAlexander.foundAt(HexPoint(25, 5), "Alexander Capital", self.simulation)
		self.playerVictoria.foundAt(HexPoint(8, 5), "Victoria City", self.simulation)
		self.playerTrajan.foundAt(HexPoint(3, 5), "Trajan Capital", self.simulation)

		self.playerTrajan.doFirstContactWith(self.playerAlexander, self.simulation)
		self.playerTrajan.doFirstContactWith(self.playerVictoria, self.simulation)
		self.playerAlexander.doFirstContactWith(self.playerVictoria, self.simulation)

		# deal
		deal = DiplomaticDeal(self.playerAlexander, self.playerVictoria)
		deal.addSendDelegationTowards(self.playerAlexander, self.simulation)
		deal.addSendDelegationTowards(self.playerVictoria, self.simulation)
		# deal.

		# WHEN
		result = self.playerAlexander.dealAI.doEqualizeDealWithAI(deal, self.playerVictoria, self.simulation)

		# THEN
		self.assertEqual(result, True)

	def test_doEqualizeDealWithAI_invalidDeal(self):
		# GIVEN
		self.playerTrajan.treasury.changeGoldBy(200)
		self.playerAlexander.treasury.changeGoldBy(200)
		self.playerVictoria.treasury.changeGoldBy(200)

		# build cities
		self.playerAlexander.foundAt(HexPoint(25, 5), "Alexander Capital", self.simulation)
		self.playerVictoria.foundAt(HexPoint(8, 5), "Victoria City", self.simulation)
		self.playerTrajan.foundAt(HexPoint(3, 5), "Trajan Capital", self.simulation)

		self.playerTrajan.doFirstContactWith(self.playerAlexander, self.simulation)
		self.playerTrajan.doFirstContactWith(self.playerVictoria, self.simulation)
		self.playerAlexander.doFirstContactWith(self.playerVictoria, self.simulation)

		# prep
		self.playerAlexander.diplomacyAI.updateOpinions(self.simulation)
		self.playerAlexander.diplomacyAI.playerDict.signDeclarationOfFriendshipWith(self.playerVictoria, True, self.simulation.currentTurn)
		self.playerVictoria.diplomacyAI.playerDict.signDeclarationOfFriendshipWith(self.playerAlexander, True, self.simulation.currentTurn)

		# deal
		deal = DiplomaticDeal(self.playerAlexander, self.playerVictoria)
		deal.addSendDelegationTowards(self.playerAlexander, self.simulation)
		deal.addSendDelegationTowards(self.playerVictoria, self.simulation)
		deal.addGoldPerTurnTradeFrom(self.playerAlexander, 2, 30, self.simulation)
		deal.addGoldTradeFrom(self.playerVictoria, 60, self.simulation)

		# WHEN
		result = self.playerAlexander.dealAI.doEqualizeDealWithAI(deal, self.playerVictoria, self.simulation)

		# THEN
		self.assertEqual(result, True)
