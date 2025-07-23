from __future__ import annotations

from marshmallow import Schema, fields, post_load
from marshmallow_enum import EnumField

from smarthexboard.smarthexboardlib.game.ai.barbarians import BarbarianAI
from smarthexboard.smarthexboardlib.game.baseTypes import HandicapType, GameState, ReplayEventType
from smarthexboard.smarthexboardlib.game.civilizations import LeaderType
from smarthexboard.smarthexboardlib.game.game import GameModel, GameWonders, ReplayEvent, GameRankingData
from smarthexboard.smarthexboardlib.game.states.victories import VictoryType
from smarthexboard.smarthexboardlib.game.wonders import WonderType
from smarthexboard.smarthexboardlib.map.areas import ContinentType
from smarthexboard.smarthexboardlib.serialisation.base import PointSchema
from smarthexboard.smarthexboardlib.serialisation.map import MapModelSchema
from smarthexboard.smarthexboardlib.serialisation.player import PlayerSchema


class BarbarianAISchema(Schema):
	barbCampSpawnCounter = fields.List(fields.List(fields.Int()), attribute='_barbCampSpawnCounter')
	barbCampNumUnitsSpawned = fields.List(fields.List(fields.Int()), attribute='_barbCampNumUnitsSpawned')

	class Meta:
		model = BarbarianAI


class GameWondersSchema(Schema):
	wonders = fields.List(EnumField(WonderType), attribute='_wonders')

	class Meta:
		model = GameWonders


class ReplayEventSchema(Schema):
	turn = fields.Int()
	eventType = EnumField(ReplayEventType)
	message = fields.Str()
	location = fields.Nested(PointSchema)

	class Meta:
		model = ReplayEvent


class GameRankingDataSchema(Schema):
	pass

	class Meta:
		model = GameRankingData


class GameModelSchema(Schema):
	turnSliceValue = fields.Int()
	# 		waitDiploPlayer = None
	players = fields.List(fields.Nested(PlayerSchema))
	currentTurn = fields.Int()
	maxTurns = fields.Int()
	victoryTypes = fields.List(EnumField(VictoryType))
	handicap = EnumField(HandicapType)
	mapModel = fields.Nested(MapModelSchema, attribute="_map")
	# userInterface = None
	gameState = EnumField(GameState, attribute="_gameStateValue")
	# _tacticalAnalysisMap = TacticalAnalysisMap(Size(map.width, map.height))
	rankingData = fields.Nested(GameRankingDataSchema, attribute="_rankingData")
	#
	# game ai
	barbarianAI = fields.Nested(BarbarianAISchema)
	# _religions = Religions()
	#
	# analyze map
	# analyzer = MapAnalyzer(_map)
	# analyzer.analyze()
	#
	# stats
	discoveredContinents = fields.List(EnumField(ContinentType))
	wondersBuilt = fields.Nested(GameWondersSchema)
	worldEraName = fields.Str(attribute='_worldEraValue')
	gameWinLeader = EnumField(LeaderType, attribute='_gameWinLeaderValue', allow_none=True)
	gameWinVictory = EnumField(VictoryType, attribute='_gameWinVictoryValue', allow_none=True)
	spawnedArchaeologySites = fields.Bool(attribute='_spawnedArchaeologySites')
	# 		greatPersons = GreatPersons()  # fixme
	# 		gameDeals = GameDeals()  # fixme
	#
	replayEvents = fields.List(fields.Nested(ReplayEventSchema))

	@post_load
	def make_game(self, data, **kwargs):
		# pprint.pprint(data)
		tmp_game = GameModel(data)

		for city in tmp_game._map._cities:
			if city.tmp_leader == LeaderType.cityState:
				city.leader = LeaderType.cityState
				city.player = tmp_game.cityStatePlayerFor(city.tmp_leader)
			else:
				city.player = tmp_game.playerFor(city.tmp_leader)

		return tmp_game

	class Meta:
		model = GameModel
