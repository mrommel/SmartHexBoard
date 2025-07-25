from marshmallow import Schema, fields, post_load

from marshmallow_enum import EnumField

from smarthexboard.smarthexboardlib.game.ai.militaryTypes import TacticalMoveType
from smarthexboard.smarthexboardlib.game.cities import City
from smarthexboard.smarthexboardlib.game.cityStates import CityStateType
from smarthexboard.smarthexboardlib.game.civilizations import LeaderType
from smarthexboard.smarthexboardlib.game.districts import DistrictType
from smarthexboard.smarthexboardlib.game.governors import GovernorType
from smarthexboard.smarthexboardlib.game.greatPersons import GreatPerson
from smarthexboard.smarthexboardlib.game.states.builds import BuildType
from smarthexboard.smarthexboardlib.game.tradeRoutes import TradeRoute
from smarthexboard.smarthexboardlib.game.unitMissions import UnitMission
from smarthexboard.smarthexboardlib.game.unitTypes import UnitType, UnitTaskType, UnitActivityType, UnitAutomationType, \
	UnitMissionType, MoveOption
from smarthexboard.smarthexboardlib.game.units import Unit, UnitTradeRouteData, UnitTradeRouteDirection, \
	UnitTradeRouteState
from smarthexboard.smarthexboardlib.game.wonders import WonderType
from smarthexboard.smarthexboardlib.map.areas import Ocean, Continent
from smarthexboard.smarthexboardlib.map.base import HexDirection
from smarthexboard.smarthexboardlib.map.improvements import ImprovementType
from smarthexboard.smarthexboardlib.map.map import MapModel, Tile, WeightedBuildList
from smarthexboard.smarthexboardlib.map.path_finding.path import HexPath
from smarthexboard.smarthexboardlib.map.types import StartLocation, ResourceType, YieldType, TerrainType, ClimateZone, \
	FeatureType, RouteType
from smarthexboard.smarthexboardlib.serialisation.base import PointSchema, HexAreaSchema, WeightedListField
from smarthexboard.smarthexboardlib.serialisation.player import PlayerSchema


class TileSchema(Schema):
	point = fields.Nested(PointSchema)
	terrain = fields.String(attribute='_terrainValue', required=True)
	isHills = fields.Boolean(attribute="_isHills")
	feature = fields.String(attribute='_featureValue', allow_none=True)
	resource = EnumField(ResourceType, attribute='_resourceValue', allow_none=True)
	resourceQuantity = fields.Integer(attribute="_resourceQuantity")

	river = fields.Integer(attribute="_riverValue")
	riverName = fields.String(attribute="_riverName", allow_none=True)

	climateZone = fields.String(attribute='_climateZone', allow_none=True)
	route = fields.String(attribute="_route")
	routePillaged = fields.Boolean(attribute="_routePillagedValue")
	improvement = fields.String(attribute="_improvementValue")
	improvementPillaged = fields.Boolean(attribute="_improvementPillagedValue")
	continentIdentifier = fields.String(allow_none=True)
	oceanIdentifier = fields.String(allow_none=True)
	discovered = fields.Dict(keys=fields.Int())
	visible = fields.Dict(keys=fields.Int())
	# self._cityValue = None  # fixme - needs to be set when map is reconstructed (from city list)
	district = EnumField(DistrictType, attribute='_districtValue', allow_none=True)
	wonder = EnumField(WonderType, attribute='_wonderValue')
	owner = fields.Method("owner_identifier", deserialize="load_owner", allow_none=True)
	# self._workingCity = None  # fixme - needs to be set when map is reconstructed (from city list)
	buildProgress = WeightedListField(BuildType, attribute='_buildProgressList')
	# area = fields.String(attribute="_area")  # fixme - needs to be set when map is reconstructed (from city list)

	def owner_identifier(self, obj):
		return None if obj.owner() is None else hash(obj.owner())

	def load_owner(self, value):
		return value

	@post_load
	def make_tile(self, data, **kwargs):
		# pprint(data, indent=2)
		# Deserialize the point or dict to a HexPoint
		terrainValue = TerrainType.grass
		if '_terrainValue' in data:
			terrainValue = data['_terrainValue']
			if isinstance(terrainValue, str):
				terrainValue = TerrainType.fromName(terrainValue)
			elif isinstance(terrainValue, TerrainType):
				terrainValue = terrainValue
			else:
				raise TypeError(f'Invalid terrain type: {type(terrainValue)} for tile {data["point"]}')

		deserialized_tile = Tile(
			point_or_dict=data['point'],
			terrain=terrainValue
		)

		deserialized_tile._owner = data['owner'] if 'owner' in data else None

		deserialized_tile._buildProgressList = WeightedBuildList()
		if '_buildProgressList' in data:
			for key, value in data['_buildProgressList'].items():
				deserialized_tile._buildProgressList[key] = value

		deserialized_tile.continentIdentifier = data['continentIdentifier']
		deserialized_tile.oceanIdentifier = data['oceanIdentifier']

		# private identifiers
		deserialized_tile._climateZone = ClimateZone.fromName(data['_climateZone'])
		deserialized_tile._districtValue = DistrictType.none
		if '_districtValue' in data:
			districtValue = data['_districtValue']
			if isinstance(districtValue, str):
				deserialized_tile._districtValue = DistrictType.fromName(districtValue)
			elif isinstance(districtValue, DistrictType):
				deserialized_tile._districtValue = districtValue
			else:
				raise TypeError(f'Invalid district type: {type(districtValue)} for tile {data["point"]}')

		# feature deserialization
		deserialized_tile._featureValue = FeatureType.none
		if '_featureValue' in data:
			featureValue = data['_featureValue']
			if isinstance(featureValue, str):
				deserialized_tile._featureValue = FeatureType.fromName(featureValue)
			elif isinstance(featureValue, FeatureType):
				deserialized_tile._featureValue = featureValue
			else:
				raise TypeError(f'Invalid feature type: {type(featureValue)} for tile {data["point"]}')

		deserialized_tile._improvementPillagedValue = data['_improvementPillagedValue']
		deserialized_tile._improvementValue = ImprovementType.fromName(data['_improvementValue'])
		deserialized_tile._isHills = data['_isHills']
		deserialized_tile._resourceQuantity = data['_resourceQuantity']

		# resource deserialization
		deserialized_tile._resourceValue = ResourceType.none
		if '_resourceValue' in data:
			resourceValue = data['_resourceValue']
			if isinstance(resourceValue, str):
				deserialized_tile._resourceValue = ResourceType.fromName(resourceValue)
			elif isinstance(resourceValue, ResourceType):
				deserialized_tile._resourceValue = resourceValue
			else:
				raise TypeError(f'Invalid resource type: {type(resourceValue)} for tile {data["point"]}')

		deserialized_tile._riverName = data['_riverName']
		deserialized_tile._riverValue = data['_riverValue']
		deserialized_tile._route = RouteType.fromName(data['_route'])
		deserialized_tile._routePillagedValue = data['_routePillagedValue'] if '_routePillagedValue' in data else False

		# wonder deserialization
		deserialized_tile._wonderValue = WonderType.none
		if '_wonderValue' in data:
			wonderValue = data['_wonderValue']
			if isinstance(wonderValue, str):
				deserialized_tile._wonderValue = WonderType.fromName(wonderValue)
			elif isinstance(wonderValue, WonderType):
				deserialized_tile._wonderValue = wonderValue
			else:
				raise TypeError(f'Invalid wonder type: {type(wonderValue)} for tile {data["point"]}')

		if 'visible' in data:
			for key, value in data['visible'].items():
				deserialized_tile.visible[key] = value

		if 'discovered' in data:
			for key, value in data['discovered'].items():
				deserialized_tile.discovered[key] = value

		# raise Exception(f'Tile deserialization not implemented yet - {data}')
		return deserialized_tile

	class Meta:
		model = Tile


class StartLocationSchema(Schema):
	location = fields.Nested(PointSchema)
	leader = fields.String(allow_none=True)
	cityState = fields.String(allow_none=True)
	isHuman = fields.Boolean()

	class Meta:
		model = StartLocation


class ContinentSchema(Schema):
	identifier = fields.String()
	name = fields.String()
	points = fields.List(fields.Nested(PointSchema))
	continentType = fields.String()

	class Meta:
		model = Continent


class OceanSchema(Schema):
	identifier = fields.String()
	name = fields.String()
	points = fields.List(fields.Nested(PointSchema))
	oceanType = fields.String()

	class Meta:
		model = Ocean


class CitySchema(Schema):
	name = fields.String(attribute='_name')
	location = fields.Nested(PointSchema)
	capital = fields.Bool(attribute='_capitalValue')
	everCapital = fields.Bool(attribute='everCapitalValue')
	population = fields.Float(attribute='_populationValue')
	gameTurnFoundedValue = fields.Int()

	foodBasket = fields.Float(attribute='_foodBasketValue')
	lastTurnFoodEarned = fields.Float(attribute='_lastTurnFoodEarnedValue')
	lastTurnFoodHarvested = fields.Float(attribute='_lastTurnFoodHarvestedValue')
	lastTurnGarrisonAssigned = fields.Int(attribute='_lastTurnGarrisonAssigned')

	player = fields.Nested(PlayerSchema(only=("leader",)))  # fields.Function(lambda obj: hash(obj.player))
	originalLeader = EnumField(LeaderType, attribute='originalLeaderValue')
	originalCityState = EnumField(CityStateType, attribute='originalCityStateValue', allow_none=True)
	previousLeader = EnumField(LeaderType, attribute='previousLeaderValue', allow_none=True)
	previousCityState = EnumField(CityStateType, attribute='previousCityStateValue', allow_none=True)

	isFeatureSurrounded = fields.Bool(attribute='_isFeatureSurroundedValue')
	cheapestPlotInfluence = fields.Int(attribute='_cheapestPlotInfluenceValue')
	cultureLevel = fields.Int(attribute='_cultureLevelValue')
	cultureStored = fields.Int(attribute='_cultureStoredValue')
	loyalty = fields.Float(attribute='_loyaltyValue')

	threat = fields.Int(attribute='threatVal')
	# self._garrisonedUnitValue = None  # fixme
	# self._combatUnitValue = None  # fixme
	numberOfAttacksMade = fields.Int(attribute='_numberOfAttacksMade')
	strength = fields.Int(attribute='_strengthVal')

	healthPoints = fields.Int(attribute='healthPointsValue')
	threat = fields.Int(attribute='_threatValue')
	amenitiesForWarWeariness = fields.Int(attribute='amenitiesForWarWearinessValue')

	luxuries = fields.List(EnumField(ResourceType), attribute='_luxuries')

	baseYieldRateFromSpecialists = WeightedListField(YieldType)
	extraSpecialistYield = WeightedListField(YieldType)
	numPlotsAcquiredList = WeightedListField(LeaderType)

	featureProduction = fields.Float(attribute='_featureProductionValue')
	productionLastTurn = fields.Float(attribute='_productionLastTurnValue')
	# self._buildQueue = BuildQueue()  # fixme
	productionAutomated = fields.Bool(attribute='_productionAutomatedValue')
	routeToCapitalConnectedLastTurn = fields.Bool(attribute='_routeToCapitalConnectedLastTurn')
	routeToCapitalConnectedThisTurn = fields.Bool(attribute='_routeToCapitalConnectedThisTurn')
	governor = EnumField(GovernorType, allow_none=True, attribute='_governorValue')
	aiNumPlotsAcquiredByOtherPlayers = WeightedListField(int, attribute='_aiNumPlotsAcquiredByOtherPlayers')

	# ai
	# self.cityStrategyAI = CityStrategyAI(self)  # fixme

	# init later via 'initialize' method
	# self.districts = None  # fixme
	# self.buildings = None  # fixme
	# self.wonders = None  # fixme
	# self.projects = None  # fixme

	# self.cityStrategy = None  # fixme
	# self.cityCitizens = None  # fixme
	# self.greatWorks = None  # fixme
	# self.cityReligion = None  # fixme
	# self.cityTradingPosts = None  # fixme
	# self.cityTourism = None  # fixme

	scratch = fields.Int(attribute='_scratchInt')

	@post_load
	def make_city(self, data, **kwargs):
		# pprint(data, indent=2)
		deserialized_city = City(
			name=data['_name'],
			location=data['location'],
			player=None,  # data['player'] contains {'leader': <LeaderType.alexander: 'alexander'>}
			isCapital=data['_capitalValue']
		)

		deserialized_city.tmp_leader = data['originalLeaderValue']

		return deserialized_city

	class Meta:
		model = City


class PathSchema(Schema):
	points = fields.List(fields.Nested(PointSchema), attribute='_points')
	costs = fields.List(fields.Float(), attribute='_costs')

	class Meta:
		model = HexPath


class MissionSchema(Schema):
	missionType = EnumField(UnitMissionType)
	buildType = EnumField(BuildType, allow_none=True)
	target = fields.Nested(PointSchema)
	path = fields.Nested(PathSchema)  # HexPath
	options = fields.List(EnumField(MoveOption))
	# unit = None  # fixme - needs to be set when deserialize
	startedInTurn = fields.Int()

	class Meta:
		model = UnitMission


class TradeRouteSchema(Schema):
	path = fields.Nested(PathSchema, attribute='_path')  # HexPath

	class Meta:
		model = TradeRoute


class UnitTradeRouteDataSchema(Schema):
	tradeRoute = fields.Nested(TradeRouteSchema)
	direction = EnumField(UnitTradeRouteDirection)
	establishedInTurn = fields.Int()
	state = EnumField(UnitTradeRouteState)

	class Meta:
		model = UnitTradeRouteData


class UnitSchema(Schema):
	name = fields.Str(attribute='_name')
	location = fields.Nested(PointSchema)
	originLocation = fields.Nested(PointSchema, attribute='_originLocation')
	originalPlayer = fields.Method(serialize="serialize_originalPlayer", deserialize="deserialize_originalPlayer")
	facingDirection = EnumField(HexDirection, attribute='_facingDirection')
	unitType = EnumField(UnitType)
	greatPerson = EnumField(GreatPerson, allow_none=True)
	player = fields.Method(serialize="serialize_player", deserialize="deserialize_player")
	taskValue = EnumField(UnitTaskType, attribute='_taskValue')

	moves = fields.Int(attribute='_movesValue')
	canMoveImpassableCount = fields.Int(attribute='_canMoveImpassableCount')
	healthPoints = fields.Float(attribute='_healthPointsValue')
	deathDelay = fields.Bool()
	activityType = EnumField(UnitActivityType, attribute='_activityTypeValue')
	automationType = EnumField(UnitAutomationType, attribute='_automationType')
	processedInTurn = fields.Bool(attribute='_processedInTurnValue')
	capturedAsIs = fields.Bool(attribute='_capturedAsIs')

	missions = fields.Nested(MissionSchema, attribute='_missions', many=True)
	missionTimer = fields.Int(attribute='_missionTimerValue')
	buildType = EnumField(BuildType, attribute='_buildTypeValue', allow_none=True)
	buildCharges = fields.Int(attribute='_buildChargesValue')

	fortifyTurns = fields.Int(attribute='_fortifyTurnsValue')
	fortifiedThisTurn = fields.Bool(attribute='_fortifiedThisTurnValue')
	fortify = fields.Int(attribute='_fortifyValue')
	isEmbarked = fields.Bool(attribute='_isEmbarkedValue')

	experience = fields.Float(attribute='_experienceValue')
	experienceModifier = fields.Float(attribute='_experienceModifierValue')
	# self._promotions = UnitPromotions(self)  # fixme
	tacticalMove = EnumField(TacticalMoveType, attribute='_tacticalMoveValue')
	tacticalTarget = fields.Nested(PointSchema, attribute='_tacticalTargetValue', allow_none=True)

	garrisoned = fields.Bool(attribute='_garrisonedValue')
	tradeRouteData = fields.Nested(UnitTradeRouteDataSchema, attribute='_tradeRouteDataValue', allow_none=True)

	numberOfAttacksMade = fields.Int(attribute='_numberOfAttacksMade')
	# self._army = None  # fixme
	deployFromOperationTurn = fields.Int(attribute='_deployFromOperationTurnValue')

	noDefensiveBonusCount = fields.Int(attribute='_noDefensiveBonusCount')

	# self.unitMoved = None

	def serialize_player(self, obj):
		return None if obj.player is None else hash(obj.player)

	def deserialize_player(self, value):
		return value

	def serialize_originalPlayer(self, obj):
		return None if obj.originalPlayer() is None else hash(obj.originalPlayer())

	def deserialize_originalPlayer(self, value):
		return value

	@post_load
	def make_unit(self, data, **kwargs):
		# pprint(data, indent=2)
		deserialized_unit = Unit(
			location=data['location'],
			unitType=data['unitType'],
			player=None
		)

		deserialized_unit.playerHash = data['player']
		deserialized_unit.originalOwnerHash = data['originalPlayer']

		return deserialized_unit

	class Meta:
		model = Unit


class MapModelSchema(Schema):
	width = fields.Int()
	height = fields.Int()
	tiles = fields.List(fields.List(fields.Nested(TileSchema)))
	cities = fields.List(fields.Nested(CitySchema), attribute='_cities')
	units = fields.List(fields.Nested(UnitSchema), attribute='_units')
	startLocations = fields.List(fields.Nested(StartLocationSchema))
	cityStateStartLocations = fields.List(fields.Nested(StartLocationSchema))

	continents = fields.List(fields.Nested(ContinentSchema))
	oceans = fields.List(fields.Nested(OceanSchema))
	areas = fields.List(fields.Nested(HexAreaSchema))

	# def _serialize(self, obj, *, many: bool = False):
	# 	lst = super()._serialize(obj, many=many)
	# 	return lst

	class Meta:
		model = MapModel
