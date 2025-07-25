from cProfile import Profile
from pstats import SortKey, Stats

from django.core.management import BaseCommand

from smarthexboard.smarthexboardlib.game.baseTypes import HandicapType
from smarthexboard.smarthexboardlib.game.civilizations import LeaderType
from smarthexboard.smarthexboardlib.game.game import GameModel
from smarthexboard.smarthexboardlib.game.generation import UserInterfaceImpl
from smarthexboard.smarthexboardlib.game.players import Player
from smarthexboard.smarthexboardlib.game.states.victories import VictoryType
from smarthexboard.smarthexboardlib.game.unitTypes import UnitType
from smarthexboard.smarthexboardlib.game.units import Unit
from smarthexboard.smarthexboardlib.map.base import HexPoint
from smarthexboard.smarthexboardlib.map.types import MapSize, TerrainType
from smarthexboard.tests.test_utils import MapModelMock


def game():
	# GIVEN
	mapModel = MapModelMock(MapSize.small, TerrainType.grass)
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

	# initial units
	playerAlexanderWarrior = Unit(HexPoint(5, 6), UnitType.warrior, playerAlexander)
	simulation.addUnit(playerAlexanderWarrior)

	playerAugustusSettler = Unit(HexPoint(15, 15), UnitType.settler, playerTrajan)
	simulation.addUnit(playerAugustusSettler)

	playerAugustusWarrior = Unit(HexPoint(15, 16), UnitType.warrior, playerTrajan)
	simulation.addUnit(playerAugustusWarrior)

	playerBarbarianWarrior = Unit(HexPoint(10, 10), UnitType.barbarianWarrior, playerBarbar)
	simulation.addUnit(playerBarbarianWarrior)

	# this is cheating
	mapModel.discover(playerAlexander, simulation)
	mapModel.discover(playerTrajan, simulation)
	mapModel.discover(playerBarbar, simulation)

	# WHEN
	iteration = 0
	while not (playerAlexander.hasProcessedAutoMoves() and playerAlexander.turnFinished()) and iteration < 100:
		simulation.update()

		if playerAlexander.isTurnActive():
			playerAlexander.setProcessedAutoMovesTo(True)  # units have moved
			playerAlexander.finishTurn()  # turn button clicked

		iteration += 1


class Command(BaseCommand):
	def handle(self, **options):
		with Profile() as profile:
			print(f"{game()}")
			(
				Stats(profile)
				.strip_dirs()
				.sort_stats(SortKey.CUMULATIVE)
				.print_stats()
			)
