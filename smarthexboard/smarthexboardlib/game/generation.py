import logging

from smarthexboard.smarthexboardlib.game.baseTypes import HandicapType
from smarthexboard.smarthexboardlib.game.civilizations import LeaderType
from smarthexboard.smarthexboardlib.game.game import GameModel
from smarthexboard.smarthexboardlib.game.governments import GovernmentType
from smarthexboard.smarthexboardlib.game.players import Player
from smarthexboard.smarthexboardlib.game.states.ui import Interface
from smarthexboard.smarthexboardlib.game.states.victories import VictoryType
from smarthexboard.smarthexboardlib.game.unitTypes import UnitType
from smarthexboard.smarthexboardlib.game.units import Unit
from smarthexboard.smarthexboardlib.map.base import HexPoint
from smarthexboard.smarthexboardlib.map.map import MapModel


class UserInterfaceImpl(Interface):
	def updateCity(self, city):
		pass

	def updatePlayer(self, player):
		pass

	def isShown(self, screenType) -> bool:
		return False

	def refreshTile(self, tile):
		pass


class GameGenerator:
	def __init__(self):
		pass

	def freeCityStateStartingUnitTypes(self) -> [UnitType]:
		return [UnitType.settler, UnitType.warrior, UnitType.builder]

	def generate(self, map: MapModel, handicap: HandicapType) -> GameModel:
		players: [Player] = []
		units: [Unit] = []

		# ---- Barbar
		playerBarbar = Player(leader=LeaderType.barbar, human=False)
		playerBarbar.initialize()
		players.append(playerBarbar)

		for startLocation in map.startLocations:
			# print("startLocation: \(startLocation.leader) (\(startLocation.isHuman ? "human" : "AI")) => \(
			# startLocation.point)")

			# player
			player = Player(leader=startLocation.leader, human=startLocation.isHuman)
			player.initialize()

			# free techs
			if startLocation.isHuman:
				for tech in handicap.freeHumanTechs():
					player.techs.discover(tech, None)

				for civic in handicap.freeHumanCivics():
					player.civics.discover(civic, None)
			else:
				for tech in handicap.freeAITechs():
					player.techs.discover(tech, None)

				for civic in handicap.freeAICivics():
					player.civics.discover(civic, None)

			# set first government
			player.government.setGovernment(GovernmentType.chiefdom, None)

			players.append(player)

			# units
			if startLocation.isHuman:
				self._allocateUnits(units, startLocation.location, handicap.freeHumanStartingUnitTypes(), player)
			else:
				self._allocateUnits(units, startLocation.location, handicap.freeAIStartingUnitTypes(), player)

		# check that ai players are only in the list once
		player_dict = dict()
		for player in players:
			key = f'{player.leader}'
			player_dict[key] = player_dict.get(key, 0) + 1

		for key, val in player_dict.items():
			assert val == 1, f'{key} has more than one player in the game'

		# handle city states
		for startLocation in map.cityStateStartLocations:
			cityStatePlayer = Player(leader=startLocation.leader, human=False)
			cityStatePlayer.cityState = startLocation.cityState
			cityStatePlayer.initialize()
			players.insert(1, cityStatePlayer)

			self._allocateUnits(units, startLocation.location, self.freeCityStateStartingUnitTypes(), cityStatePlayer)

		gameModel = GameModel(
			victoryTypes=[VictoryType.science, VictoryType.cultural, VictoryType.conquest, VictoryType.domination, VictoryType.religious, VictoryType.diplomatic, VictoryType.score],
			handicap=handicap,
			turnsElapsed=0,
			players=players,
			map=map
		)

		# add UI
		gameModel.userInterface = UserInterfaceImpl()

		# add units
		self._addUnits(units, gameModel)

		return gameModel

	def _allocateUnits(self, units, startLocation: HexPoint, unitTypes: [UnitType], player):
		for unitType in unitTypes:
			unit = Unit(startLocation, unitType, player)
			units.append(unit)

	def _addUnits(self, units, gameModel):
		lastLeader: LeaderType = LeaderType.none
		for unit in units:
			gameModel.addUnit(unit)
			gameModel.sightAt(unit.location, unit.sight(), unit, unit.player)

			if lastLeader == unit.player.leader:
				if len(gameModel.unitsAt(unit.location)) > 1:
					jumped = unit.jumpToNearestValidPlotWithin(2, gameModel)
					if not jumped:
						logging.warning("--- could not jump unit to nearest valid plot ---")

			lastLeader = unit.player.leader

		return
