from pprint import pprint

from marshmallow import Schema, fields, post_load
from marshmallow_enum import EnumField

from smarthexboard.smarthexboardlib.core.types import EraType
from smarthexboard.smarthexboardlib.game.cityStates import CityStateType, CityStateQuestType, CityStateQuest
from smarthexboard.smarthexboardlib.game.civilizations import LeaderType
from smarthexboard.smarthexboardlib.game.governments import GovernmentType, PlayerGovernment, PolicyCardSet
from smarthexboard.smarthexboardlib.game.players import Player
from smarthexboard.smarthexboardlib.game.policyCards import PolicyCardType
from smarthexboard.smarthexboardlib.game.religions import FaithPurchaseType
from smarthexboard.smarthexboardlib.game.states.ages import AgeType
from smarthexboard.smarthexboardlib.game.states.dedications import DedicationType
from smarthexboard.smarthexboardlib.game.types import TechType, CivicType
from smarthexboard.smarthexboardlib.map.areas import ContinentType
from smarthexboard.smarthexboardlib.map.types import FeatureType, ResourceType
from smarthexboard.smarthexboardlib.serialisation.base import PointSchema, HexAreaSchema, WeightedListField


class PolicyCardSetSchema(Schema):
	cards = fields.List(EnumField(PolicyCardType), attribute='_cards')

	class Meta:
		model = PolicyCardSet


class PlayerGovernmentSchema(Schema):
	currentGovernment = EnumField(GovernmentType, attribute='_currentGovernmentValue')
	policyCards = fields.Nested(PolicyCardSetSchema, attribute='_policyCards')
	lastCheckedGovernment = fields.Int(attribute='_lastCheckedGovernment')

	class Meta:
		model = PlayerGovernment


class CityStateQuestSchema(Schema):
	questType = EnumField(CityStateQuestType)
	cityState = EnumField(CityStateType, allow_none=True)
	techType = EnumField(TechType, allow_none=True)
	civicType = EnumField(CivicType, allow_none=True)

	class Meta:
		model = CityStateQuest


class PlayerSchema(Schema):
	leader = EnumField(LeaderType)
	cityState = EnumField(CityStateType, allow_none=True)
	human = fields.Bool()

	# ais
	# grandStrategyAI = GrandStrategyAI(player=self)
	# economicAI = EconomicAI(player=self)
	# militaryAI = MilitaryAI(player=self)
	# tacticalAI = TacticalAI(player=self)
	# diplomacyAI = DiplomaticAI(player=self)
	# homelandAI = HomelandAI(player=self)
	# builderTaskingAI = BuilderTaskingAI(player=self)
	# citySpecializationAI = CitySpecializationAI(player=self)
	# dangerPlotsAI = DangerPlotsAI(player=self)
	# minorCivAI = MinorCivAI(player=self)
	# religionAI = ReligionAI(player=self)
	# wonderProductionAI = None
	# dealAI = DealAI(player=self)
	# leagueAI = LeagueAI(player=self)

	# notifications = Notifications(self)
	# diplomacyRequests = DiplomacyRequests(player=self)

	# special
	# techs = PlayerTechs(self)
	# civics = PlayerCivics(self)
	# moments = PlayerMoments(self)
	# _traits = PlayerTraits(self)
	# personalityFlavors = Flavors()

	# state values
	isAliveVal = fields.Bool()
	turnActive = fields.Bool()
	checkedOperations = fields.Bool(attribute="_checkedOperations")
	finishTurnButtonPressedValue = fields.Bool()
	processedAutoMovesValue = fields.Bool()
	autoMovesValue = fields.Bool()
	endTurnValue = fields.Bool()
	lastSliceMovedValue = fields.Int()

	# cities stats values
	citiesFound = fields.Int(attribute="_citiesFoundValue")
	citiesLost = fields.Int(attribute="_citiesLostValue")
	numberOfPlotsBought = fields.Int(attribute="_numberOfPlotsBoughtValue")
	settledContinents = fields.List(EnumField(ContinentType), attribute="_settledContinents")
	builtCityNames = fields.List(fields.Str())
	originalCapitalLocation = fields.Nested(PointSchema, attribute="originalCapitalLocationValue")
	startingPosition = fields.Nested(PointSchema, attribute="_startingPositionValue", allow_none=True)
	lostCapitalValue = fields.Bool()
	conquerorValue = EnumField(LeaderType, allow_none=True)
	combatThisTurnValue = fields.Bool()
	cramped = fields.Bool(attribute="_cramped")

	government = fields.Nested(PlayerGovernmentSchema)
	# religion = PlayerReligion(player=self)
	# tradeRoutes = PlayerTradeRoutes(player=self)
	# cityConnections = CityConnections(player=self)
	# greatPeople = PlayerGreatPeople(player=self)
	# treasury = PlayerTreasury(player=self)
	# tourism = PlayerTourism(player=self)
	# governors = PlayerGovernors(player=self)
	# operations = PlayerOperations(player=self)
	# armies = PlayerArmies(player=self)
	# envoys = PlayerEnvoys(player=self)

	currentEraValue = EnumField(EraType, attribute="_currentEraValue")
	currentAgeValue = EnumField(AgeType, attribute="_currentAgeValue")
	currentDedicationsValue = fields.List(EnumField(DedicationType), attribute="_currentDedicationsValue")
	numberOfDarkAgesValue = fields.Int(attribute="_numberOfDarkAgesValue")
	numberOfGoldenAgesValue = fields.Int(attribute="_numberOfGoldenAgesValue")
	totalImprovementsBuilt = fields.Int(attribute="_totalImprovementsBuilt")
	trainedSettlersValue = fields.Int(attribute="_trainedSettlersValue")
	tradingCapacityValue = fields.Int(attribute="_tradingCapacityValue")
	boostExoplanetExpedition = fields.Int(attribute="_boostExoplanetExpeditionValue")
	discoveredNaturalWonders = fields.List(EnumField(FeatureType), attribute="_discoveredNaturalWonders")
	discoveredBarbarianCampLocations = fields.List(fields.Nested(PointSchema),
	                                               attribute="_discoveredBarbarianCampLocations")
	area = fields.Nested(HexAreaSchema, attribute='_area')
	faithEarned = fields.Float(attribute='_faithEarned')
	cultureEarned = fields.Float(attribute='_cultureEarned')
	resourceInventory = WeightedListField(ResourceType, attribute='_resourceInventory')
	resourceStockpile = WeightedListField(ResourceType, attribute='_resourceStockpile')
	resourceMaxStockpile = WeightedListField(ResourceType, attribute='_resourceMaxStockpile')
	suzerain = EnumField(LeaderType, attribute='_suzerainValue', allow_none=True)
	oldQuests = fields.List(fields.Nested(CityStateQuestSchema), attribute='_oldQuests')
	quests = fields.List(fields.Nested(CityStateQuestSchema), attribute='_quests')
	influencePoints = fields.Int(attribute='_influencePointsValue')
	canChangeGovernment = fields.Bool(attribute='_canChangeGovernmentValue')
	faithPurchaseType = EnumField(FaithPurchaseType, attribute='_faithPurchaseType')
	greatPersonExpendGold = fields.Int(attribute='_greatPersonExpendGold')
	establishedTradingPosts = fields.List(fields.Int(), attribute='_establishedTradingPosts')

	class Meta:
		model = Player

	# @post_load
	# def make_player(self, data, **kwargs):
	# 	pprint(data)
	# 	return Player(data)
