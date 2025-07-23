import unittest

from smarthexboard.smarthexboardlib.core.types import EraType
from smarthexboard.smarthexboardlib.game.achievements import TechAchievements, CivicAchievements
from smarthexboard.smarthexboardlib.game.ai.baseTypes import MilitaryStrategyType
from smarthexboard.smarthexboardlib.game.ai.economicStrategies import EconomicStrategyType
from smarthexboard.smarthexboardlib.game.ai.homeland import HomelandMoveType
from smarthexboard.smarthexboardlib.game.ai.militaryTypes import UnitFormationType
from smarthexboard.smarthexboardlib.game.baseTypes import HandicapType
from smarthexboard.smarthexboardlib.game.buildings import BuildingType
from smarthexboard.smarthexboardlib.game.cities import City
from smarthexboard.smarthexboardlib.game.cityStates import CityStateType, CityStateCategory
from smarthexboard.smarthexboardlib.game.civilizations import LeaderType, CivilizationType, CivilizationAbility
from smarthexboard.smarthexboardlib.game.districts import DistrictType
from smarthexboard.smarthexboardlib.game.flavors import Flavors, Flavor, FlavorType
from smarthexboard.smarthexboardlib.game.game import GameModel
from smarthexboard.smarthexboardlib.game.generation import UserInterfaceImpl
from smarthexboard.smarthexboardlib.game.governments import GovernmentType
from smarthexboard.smarthexboardlib.game.governors import GovernorType, GovernorTitleType
from smarthexboard.smarthexboardlib.game.loyalties import LoyaltyState
from smarthexboard.smarthexboardlib.game.moments import MomentType
from smarthexboard.smarthexboardlib.game.notifications import NotificationType
from smarthexboard.smarthexboardlib.game.playerMechanics import ApproachModifierType
from smarthexboard.smarthexboardlib.game.players import Player
from smarthexboard.smarthexboardlib.game.policyCards import PolicyCardType
from smarthexboard.smarthexboardlib.game.promotions import UnitPromotionType
from smarthexboard.smarthexboardlib.game.religions import BeliefType, ReligionType, PantheonType
from smarthexboard.smarthexboardlib.game.states.accessLevels import AccessLevel
from smarthexboard.smarthexboardlib.game.states.ages import AgeType
from smarthexboard.smarthexboardlib.game.states.builds import BuildType
from smarthexboard.smarthexboardlib.game.states.dedications import DedicationType
from smarthexboard.smarthexboardlib.game.states.gossips import GossipType
from smarthexboard.smarthexboardlib.game.states.victories import VictoryType
from smarthexboard.smarthexboardlib.game.types import TechType, CivicType
from smarthexboard.smarthexboardlib.game.unitTypes import UnitType, UnitClassType
from smarthexboard.smarthexboardlib.game.wonders import WonderType
from smarthexboard.smarthexboardlib.map.base import HexPoint
from smarthexboard.smarthexboardlib.map.improvements import ImprovementType
from smarthexboard.smarthexboardlib.map.types import TerrainType, FeatureType, ResourceType
from smarthexboard.tests.test_utils import MapModelMock


class TestFlavors(unittest.TestCase):
	def test_initial_value(self):
		# GIVEN
		self.objectToTest = Flavors()

		# WHEN
		cultureValue = self.objectToTest.value(FlavorType.culture)

		# THEN
		self.assertEqual(cultureValue, 0)

	def test_add_value(self):
		# GIVEN
		self.objectToTest = Flavors()
		self.objectToTest += Flavor(FlavorType.culture, value=5)

		# WHEN
		cultureValue = self.objectToTest.value(FlavorType.culture)

		# THEN
		self.assertEqual(cultureValue, 5)

	def test_add_two_values(self):
		# GIVEN
		self.objectToTest = Flavors()
		self.objectToTest += Flavor(FlavorType.culture, value=5)
		self.objectToTest += Flavor(FlavorType.culture, value=2)

		# WHEN
		cultureValue = self.objectToTest.value(FlavorType.culture)

		# THEN
		self.assertEqual(cultureValue, 7)

	def test_add_values(self):
		# GIVEN
		self.objectToTest = Flavors()
		self.objectToTest += Flavor(FlavorType.culture, value=5)
		self.objectToTest.addFlavor(FlavorType.culture, value=3)

		# WHEN
		cultureValue = self.objectToTest.value(FlavorType.culture)

		# THEN
		self.assertEqual(cultureValue, 8)

	def test_reset(self):
		# GIVEN
		self.objectToTest = Flavors()
		self.objectToTest.addFlavor(FlavorType.culture, value=3)
		self.objectToTest.reset()
		self.objectToTest.addFlavor(FlavorType.culture, value=2)

		# WHEN
		cultureValue = self.objectToTest.value(FlavorType.culture)

		# THEN
		self.assertEqual(cultureValue, 2)


class AccessLevelTests(unittest.TestCase):
	def test_initial_no_contact(self):
		# GIVEN
		barbarianPlayer = Player(LeaderType.barbar, human=False)
		barbarianPlayer.initialize()

		playerAlexander = Player(LeaderType.alexander, human=True)
		playerAlexander.initialize()

		playerTrajan = Player(LeaderType.trajan)
		playerTrajan.initialize()

		# set up the map
		mapModel = MapModelMock(10, 10, TerrainType.ocean)
		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=mapModel
		)

		simulation.userInterface = UserInterfaceImpl()

		# WHEN
		accessLevel = playerAlexander.diplomacyAI.accessLevelTowards(playerTrajan)

		# THEN
		self.assertEqual(accessLevel, AccessLevel.none)

	def test_initial_first_contact(self):
		# GIVEN
		barbarianPlayer = Player(LeaderType.barbar, human=False)
		barbarianPlayer.initialize()

		playerAlexander = Player(LeaderType.alexander, human=True)
		playerAlexander.initialize()

		playerTrajan = Player(LeaderType.trajan)
		playerTrajan.initialize()

		# set up the map
		mapModel = MapModelMock(10, 10, TerrainType.ocean)
		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=mapModel
		)

		simulation.userInterface = UserInterfaceImpl()

		# WHEN
		playerAlexander.doFirstContactWith(playerTrajan, simulation)
		accessLevel = playerAlexander.diplomacyAI.accessLevelTowards(playerTrajan)

		# THEN
		self.assertEqual(accessLevel, AccessLevel.none)

	def test_limited_after_delegation(self):
		# GIVEN
		barbarianPlayer = Player(LeaderType.barbar, human=False)
		barbarianPlayer.initialize()

		playerAlexander = Player(LeaderType.alexander, human=True)
		playerAlexander.initialize()

		playerTrajan = Player(LeaderType.trajan)
		playerTrajan.initialize()

		# set up the map
		mapModel = MapModelMock(10, 10, TerrainType.ocean)
		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=mapModel
		)

		simulation.userInterface = UserInterfaceImpl()

		playerTrajanCapital = City("Capital", HexPoint(5, 5), True, playerTrajan)
		playerTrajanCapital.initialize(simulation)
		simulation.addCity(playerTrajanCapital)

		playerAlexander.treasury.changeGoldBy(50)
		playerAlexander.doFirstContactWith(playerTrajan, simulation)

		# WHEN
		playerAlexander.diplomacyAI.doSendDelegationTo(playerTrajan, simulation)
		accessLevel = playerAlexander.diplomacyAI.accessLevelTowards(playerTrajan)

		# THEN
		self.assertEqual(accessLevel, AccessLevel.limited)


class TestAssets(unittest.TestCase):

	def test_handicap_data(self):
		for handicap in list(HandicapType):
			_ = handicap.title()

	def test_gossip_data(self):
		for gossip in list(GossipType):
			_ = gossip.name()

	def test_accessLevel_data(self):
		for accessLevel in list(AccessLevel):
			_ = accessLevel.name()

	def test_terrain_data(self):
		for terrain in list(TerrainType):
			_ = terrain.title()

	def test_feature_data(self):
		for feature in list(FeatureType):
			_ = feature.title()

	def test_resource_data(self):
		for resource in list(ResourceType):
			_ = resource.title()

	def test_era_data(self):
		for era in list(EraType):
			_ = era.title()

	def test_age_data(self):
		for age in list(AgeType):
			_ = age.title()

	def test_techs_data(self):
		for tech in list(TechType):
			_ = tech.title()

	def test_civics_data(self):
		for civic in list(CivicType):
			_ = civic.title()

	def test_districts_data(self):
		for district in list(DistrictType):
			_ = district.title()

			mapModel = MapModelMock(10, 10, TerrainType.grass)
			simulation = GameModel(
				victoryTypes=[VictoryType.domination],
				handicap=HandicapType.chieftain,
				turnsElapsed=0,
				players=[],
				map=mapModel
			)
			_ = district.canBuildOn(HexPoint(1, 1), simulation)

	def test_wonders_data(self):
		for wonder in list(WonderType):
			_ = wonder.title()

			mapModel = MapModelMock(10, 10, TerrainType.grass)
			simulation = GameModel(
				victoryTypes=[VictoryType.domination],
				handicap=HandicapType.chieftain,
				turnsElapsed=0,
				players=[],
				map=mapModel
			)
			_ = wonder.canBuildOn(HexPoint(1, 1), simulation)

	def test_buildings_data(self):
		for building in list(BuildingType):
			_ = building.title()

	def test_improvements_data(self):
		player = Player(LeaderType.trajan)
		player.initialize()

		for improvement in list(ImprovementType):
			_ = improvement.title()
			_ = improvement.yieldsFor(player)

	def test_builds_data(self):
		for build in list(BuildType):
			_ = build.title()

	def test_policyCard_data(self):
		for policyCard in list(PolicyCardType):
			_ = policyCard.title()

	def test_moment_data(self):
		for moment in list(MomentType):
			_ = moment.title()

	def test_dedication_data(self):
		for dedication in list(DedicationType):
			_ = dedication.title()

	def test_cityState_data(self):
		for cityStateCategory in list(CityStateCategory):
			_ = cityStateCategory.title()

		for cityState in list(CityStateType):
			_ = cityState.title()

	def test_civics_envoys(self):
		# https://civilization.fandom.com/wiki/Envoy_(Civ6)
		# The following civics grant free Envoy Envoys upon discovery: Mysticism, Military Training, Theology,
		# Naval Tradition, Mercenaries, Colonialism, Opera and Ballet, Natural History, Scorched Earth, Conservation,
		# Capitalism, Nuclear Program, and Cultural Heritage (and, in Gathering Storm, Near Future Governance and
		# Global Warming Mitigation). The civics between Mercenaries and Conservation grant +2, while Conservation and
		# all others afterward grant +3.
		civics_with_envoys = [
			CivicType.mysticism, CivicType.militaryTradition, CivicType.theology, CivicType.navalTradition,
			CivicType.mercenaries, CivicType.colonialism, CivicType.operaAndBallet, CivicType.naturalHistory,
			CivicType.scorchedEarth, CivicType.conservation, CivicType.capitalism, CivicType.nuclearProgram,
			CivicType.culturalHeritage, CivicType.nearFutureGovernance, CivicType.globalWarmingMitigation
		]

		for civic_with_envoys in civics_with_envoys:
			self.assertGreater(civic_with_envoys.envoys(), 0, f'envoys of {civic_with_envoys} should be greater than zero')

	def test_civics_governors(self):
		# Civic Tree - There are a total of 13 civics that will grant 1 Governor Title. They are State Workforce,
		# Early Empire, Defensive Tactics, Recorded History, Medieval Faires, Guilds, Civil Engineering, Nationalism,
		# Mass Media, Mobilization, Globalization, Social Media, and Near Future Governance. Advancing through the
		# civic tree is the most basic and most common way of acquiring Governor Titles.
		civics_with_governors = [
			CivicType.stateWorkforce, CivicType.earlyEmpire, CivicType.defensiveTactics, CivicType.recordedHistory,
			CivicType.medievalFaires, CivicType.guilds, CivicType.civilEngineering, CivicType.nationalism,
			CivicType.massMedia, CivicType.mobilization, CivicType.globalization, CivicType.socialMedia,
			CivicType.nearFutureGovernance, CivicType.futureCivic
		]

		for civic in list(CivicType):
			if civic in civics_with_governors:
				self.assertTrue(civic.hasGovernorTitle(), f'envoys of {civic} should be True')
			else:
				self.assertFalse(civic.hasGovernorTitle(), f'envoys of {civic} should be False')

	def test_civic_achievements(self):
		achievements = CivicAchievements(CivicType.gamesAndRecreation)

		self.assertCountEqual(achievements.buildingTypes, [BuildingType.arena])
		self.assertCountEqual(achievements.wonderTypes, [WonderType.colosseum])
		self.assertCountEqual(achievements.districtTypes, [DistrictType.entertainmentComplex])
		self.assertCountEqual(achievements.policyCards, [PolicyCardType.insulae])
		self.assertCountEqual(achievements.governments, [])

	def test_tech_achievements(self):
		achievements = TechAchievements(TechType.writing)

		self.assertCountEqual(achievements.buildingTypes, [BuildingType.library])
		self.assertCountEqual(achievements.unitTypes, [])
		self.assertCountEqual(achievements.wonderTypes, [WonderType.etemenanki])
		self.assertCountEqual(achievements.buildTypes, [])
		self.assertCountEqual(achievements.districtTypes, [DistrictType.campus])

	def test_governments_data(self):
		for government in list(GovernmentType):
			_ = government.title()

	def test_military_state_data(self):
		for militaryStrategy in list(MilitaryStrategyType):
			_ = militaryStrategy.title()

	def test_economic_state_data(self):
		for economicStrategy in list(EconomicStrategyType):
			_ = economicStrategy.title()

	def test_civilization_data(self):
		for civilization in list(CivilizationType):
			_ = civilization.title()

		for civilizationAbility in list(CivilizationAbility):
			_ = civilizationAbility.title()

	def test_leader_data(self):
		for leader in list(LeaderType):
			_ = leader.title()

	def test_unit_data(self):
		for unit in list(UnitType):
			_ = unit.title()

			if unit == UnitType.none:
				continue

			self.assertGreater(len(unit._flavors()), 0, f'{unit} has no flavors')

	def test_unit_promotion_data(self):
		for promotion in list(UnitPromotionType):
			_ = promotion.title()

	def test_unit_class_data(self):
		for unitClass in list(UnitClassType):
			_ = unitClass.title()

	def test_loyalties_data(self):
		for loyalty in list(LoyaltyState):
			_ = loyalty.title()
			_ = loyalty.yieldPercentage()

	def test_homelandMoves_data(self):
		for homelandMove in list(HomelandMoveType):
			_ = homelandMove.title()

	def test_notification_data(self):
		for notificationType in list(NotificationType):
			_ = notificationType.title()

	def test_governor_data(self):
		for governor in list(GovernorType):
			_ = governor.title()

		for governorTitle in list(GovernorTitleType):
			_ = governorTitle.title()

	def test_religion_data(self):
		for pantheon in list(PantheonType):
			_ = pantheon.title()

		for religion in list(ReligionType):
			_ = religion.title()

		for belief in list(BeliefType):
			_ = belief.title()

	def test_diplomatic_data(self):
		for approach in list(ApproachModifierType):
			_ = approach.summary()

	def test_formation_slots(self):
		for formation in list(UnitFormationType):
			_ = formation.slots()
