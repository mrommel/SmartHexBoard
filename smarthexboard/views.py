import uuid
from typing import Optional

from django.core.cache import cache
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django_q.tasks import async_task

from setup.settings import DEBUG
from smarthexboard.forms import CreateGameForm
from smarthexboard.models import GameGenerationData, GameGenerationState
from smarthexboard.repositories import GameDataRepository
from smarthexboard.utils import is_valid_uuid
from .smarthexboardlib.game.baseTypes import HandicapType
from .smarthexboardlib.game.civilizations import LeaderType
from .smarthexboardlib.game.game import GameModel
from .smarthexboardlib.game.generation import UserInterfaceImpl
from .smarthexboardlib.game.unitTypes import UnitMapType
from .smarthexboardlib.game.units import Unit
from .smarthexboardlib.map.base import HexPoint
from .smarthexboardlib.map.types import TerrainType, FeatureType, ResourceType, MapType, MapSize
from .smarthexboardlib.serialisation.game import GameModelSchema


# ####################################
#
#         pages
#
# ####################################

def index(request):
	leader_selection = []
	for leader in list(LeaderType):
		if leader == LeaderType.none:
			continue

		if leader == LeaderType.barbar:
			continue

		if leader == LeaderType.freeCities:
			continue

		if leader == LeaderType.cityState:
			continue

		leader_selection.append((leader.value, f'{leader.title()} ({leader.civilization().name()})'))

	difficulty_selection = []
	for handicap in list(HandicapType):
		difficulty_selection.append((str(handicap), handicap.title()))

	map_type_selection = []
	for mapType in list(MapType):
		map_type_selection.append((mapType.value, mapType.name()))

	map_size_selection = []
	for mapSize in list(MapSize):
		map_size_selection.append((mapSize.value, mapSize.name()))

	template = loader.get_template('index.html')
	context = {
		'navi_home': 'active',
		'debug': DEBUG,
		# create game data
		'leader_selection': leader_selection,
		'difficulty_selection': difficulty_selection,
		'map_type_selection': map_type_selection,
		'map_size_selection': map_size_selection,
	}
	return HttpResponse(template.render(context, request))


def tests(request):
	template = loader.get_template('tests.html')
	context = {
		'abc': 'def',
		'navi_home': 'active',
	}
	return HttpResponse(template.render(context, request))


def styleguide(request):
	terrains = dict()
	features = dict()
	resources = dict()

	for terrain in list(TerrainType):
		if terrain == TerrainType.land or terrain == TerrainType.sea:
			continue

		if len(terrain.textures()) == 0:
			raise Exception(f'Terrain {terrain} does not have any textures')

		terrains[terrain.value] = terrain.textures()[0]

	for feature in list(FeatureType):
		if feature == FeatureType.none:
			continue

		feature_textures = feature.textures()

		if len(feature_textures) > 0:
			features[feature.value] = feature_textures[0]

	for resource in list(ResourceType):
		resources[resource.value] = resource.texture()

	template = loader.get_template('styleguide/index.html')
	context = {
		'terrains': terrains,
		'features': features,
		'resources': resources,
	}
	return HttpResponse(template.render(context, request))


# ####################################
#
#     API methods
#
# ####################################


def game_create(request):
	# If this is a POST request then process the Form data
	if request.method == 'POST':

		# Create a form instance and populate it with data from the request (binding):
		form = CreateGameForm(request.POST)

		# Check if the form is valid:
		if form.is_valid():
			game_uuid = uuid.uuid4()

			leader: LeaderType = form.leaderValue()
			handicap: HandicapType = form.handicapValue()
			mapSize: MapSize = form.mapSizeValue()
			mapType: MapType = form.mapTypeValue()

			print(f'generate_game({game_uuid}, {leader}, {handicap}, {mapSize}, {mapType})')
			# uuid, leader: LeaderType, handicap: HandicapType, mapSize: MapSize, mapType: MapType
			async_task("smarthexboard.services.generate_game", game_uuid, leader, handicap, mapSize, mapType)

			json_payload = {'status': 'Created', 'game_uuid': game_uuid}
			return JsonResponse(json_payload, status=201)
		else:
			# print(form.errors)
			json_payload = {'status': 'Form not valid', 'errors': form.errors}
			return JsonResponse(json_payload, status=400)
	else:
		json_payload = {'status': f'Invalid method {request.method}'}
		return JsonResponse(json_payload, status=400)


def game_create_status(request, game_uuid: str):
	if not is_valid_uuid(game_uuid):
		json_payload = {
			'error': 'invalid arg',
			'field': 'game_uuid',
			'value': game_uuid,
			'message': 'Invalid request: not a valid uuid format'
		}
		return JsonResponse(json_payload, status=400)

	game_generation = GameGenerationData.objects.filter(uuid=game_uuid).first()
	if game_generation is None:
		json_payload = {'uuid': game_uuid, 'status': f'Cannot find game generation with uuid: {game_uuid}'}
		return JsonResponse(json_payload, status=404)

	json_payload = {
		'uuid': game_uuid,
		'status': GameGenerationState(game_generation.state).label,
		'progress': game_generation.progress
	}
	return JsonResponse(json_payload, status=200)


def game_map(request, game_uuid: str):
	if not is_valid_uuid(game_uuid):
		json_payload = {'uuid': game_uuid, 'status': 'Invalid request: not a valid uuid format'}
		return JsonResponse(json_payload, status=400)

	if not GameDataRepository.inCacheOrDB(game_uuid):
		game_generation = GameGenerationData.objects.filter(uuid=game_uuid).first()
		if game_generation is None:
			json_payload = {'uuid': game_uuid, 'status': f'Cannot find game generated with uuid: {game_uuid}'}
			return JsonResponse(json_payload, status=404)

		current_state = GameGenerationState(game_generation.state)
		if current_state != GameGenerationState.READY:
			json_payload = {'uuid': game_uuid, 'status': f'Game with {game_uuid} is not ready yet: {current_state}'}
			return JsonResponse(json_payload, status=400)

		game_str: str = game_generation.game
		obj_dict = GameModelSchema().loads(game_str)
		obj = GameModel(obj_dict)
		GameDataRepository.store(game_uuid, obj)

		GameGenerationData.objects.filter(uuid=game_uuid).delete()
	else:
		obj = GameDataRepository.fetch(game_uuid)

	map_dict = obj._map.to_dict(human=obj.humanPlayer())

	# convert json string to dict
	json_payload = map_dict
	return JsonResponse(json_payload, status=200)


def game_info(request, game_uuid: str):
	game = GameDataRepository.fetch(game_uuid)

	if game is None:
		json_payload = {'uuid': game_uuid, 'status': f'Game with id {game_uuid} not found in db or cache.'}
		return JsonResponse(json_payload, status=400)

	humanPlayer = game.humanPlayer()
	human_dict = humanPlayer.to_dict(game)
	otherPlayers = []

	for loopPlayer in game.players:
		if humanPlayer == loopPlayer:
			continue

		if not loopPlayer.isAlive():
			continue

		if loopPlayer.diplomacyAI.hasMetWith(humanPlayer):
			otherPlayers.append(loopPlayer.to_dict())

	# convert json string to dict
	json_payload = {
		'turn': game.currentTurn,
		'turnYear': game.turnYear(),
		'human': human_dict,
		'others': otherPlayers
	}
	return JsonResponse(json_payload, status=200)


def game_update(request, game_uuid: str):
	game = GameDataRepository.fetch(game_uuid)
	cache_key = f'game_updating_{game_uuid}'

	if game is None:
		json_payload = {'uuid': game_uuid, 'status': f'Game with id {game_uuid} not found in db or cache.'}
		return JsonResponse(json_payload, status=400)

	if cache.get(cache_key) is not None:
		json_payload = {'uuid': game_uuid, 'status': f'Game with id {game_uuid} currently updating.'}
		return JsonResponse(json_payload, status=400)

	game.userInterface = UserInterfaceImpl()

	humanPlayer = game.humanPlayer()

	if humanPlayer.hasProcessedAutoMoves() and humanPlayer.turnFinished():
		json_payload = {'uuid': game_uuid, 'status': f'Game turn for human is finished.'}
		return JsonResponse(json_payload, status=400)

	cache.set(cache_key, True)
	# print(f'start updating {game_uuid}')
	game.update()
	cache.delete(cache_key)
	# print(f'stop updating {game_uuid}')

	currentPlayerName = ''
	if game.activePlayer() is not None:
		if game.activePlayer().isCityState():
			currentPlayerName = f'CityState: {game.activePlayer().cityState.title()}'
		else:
			currentPlayerName = game.activePlayer().leader.name

	GameDataRepository.store(game_uuid, game)

	json_payload = {
		'game_uuid': game_uuid,
		'current_turn': game.currentTurn,
		'current_player': currentPlayerName,
		'human_active': humanPlayer.turnActive
		# notifications to human?
	}
	return JsonResponse(json_payload, status=200)


def game_turn(request, game_uuid: str):
	game = GameDataRepository.fetch(game_uuid)

	if game is None:
		json_payload = {'uuid': game_uuid, 'status': f'Game with {game_uuid} not found in db or cache.'}
		return JsonResponse(json_payload, status=400)

	game.userInterface = UserInterfaceImpl()

	humanPlayer = game.humanPlayer()

	if humanPlayer.hasProcessedAutoMoves() and humanPlayer.turnFinished():
		json_payload = {'uuid': game_uuid, 'status': f'Game turn for human is finished.'}
		return JsonResponse(json_payload, status=400)

	if humanPlayer.isTurnActive():
		humanPlayer.setProcessedAutoMovesTo(True)
		humanPlayer.setEndTurnTo(True, game)
		humanPlayer.finishTurn()
	else:
		raise Exception('unknown')

	json_payload = {
		'game_uuid': game_uuid,
		'current_turn': game.currentTurn
		# notifications to human?
	}
	return JsonResponse(json_payload, status=200)


def game_move_unit(request, game_uuid: str, unit_type: str, old_location: str, new_location: str):
	"""
		@param request: incoming request
		@param game_uuid: game identifier
		@param unit_type: combat or civilian
		@param old_location: string in format x,y with the source location of the unit to be moved
		@param new_location: string in format x,y with the destination location of the unit to be moved
		@return: JsonResponse with:
			200: when the move was possible
			400: when the move was impossible
			404: when the unit or the game was not found
	"""
	game = GameDataRepository.fetch(game_uuid)

	if game is None:
		json_payload = {'uuid': game_uuid, 'status': f'Game with {game_uuid} not found in db or cache.'}
		return JsonResponse(json_payload, status=400)

	game.userInterface = UserInterfaceImpl()

	humanPlayer = game.humanPlayer()

	unit_map_type = parseUnitMapType(unit_type)
	old_loc = parseLocation(old_location)
	new_loc = parseLocation(new_location)

	print(f'move unit from: {old_loc} to {new_loc}')

	if old_loc is None:
		json_payload = {'uuid': game_uuid, 'status': f'Could not parse location from {old_location}.'}
		return JsonResponse(json_payload, status=400)

	if new_loc is None:
		json_payload = {'uuid': game_uuid, 'status': f'Could not parse location from {new_location}.'}
		return JsonResponse(json_payload, status=400)

	unit: Optional[Unit] = game.unitAt(location=old_loc, unitMapType=unit_map_type)
	print(f'unit: {unit}')

	if unit is None:
		json_payload = {'uuid': game_uuid, 'status': f'Could find unit at {old_loc}.'}
		return JsonResponse(json_payload, status=400)

	if unit.player != humanPlayer:
		json_payload = {
			'uuid': game_uuid,
			'status': f'Cannot move units from another player. The unit you are trying to move is from {unit.player}.'
		}
		return JsonResponse(json_payload, status=400)

	# move the unit
	ret: bool = unit.doMoveOnto(new_loc, game)

	if not ret:
		json_payload = {
			'uuid': game_uuid,
			'status': f'Unit {unit} could not be moved from {old_loc} to {new_loc}.'
		}
		return JsonResponse(json_payload, status=400)

	json_payload = {
		'game_uuid': game_uuid,
		'current_turn': game.currentTurn
		# notifications to human?
	}
	return JsonResponse(json_payload, status=200)
