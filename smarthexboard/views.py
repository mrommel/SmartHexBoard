import random
from typing import Optional

from django.core.cache import cache
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django_q.tasks import async_task

from setup.settings import DEBUG
from smarthexboard.forms import CreateGameForm, UnitMoveForm, UnitActionForm, FoundCityForm, CityInfoForm
from smarthexboard.models import GameGenerationData, GameGenerationState
from smarthexboard.repositories import GameDataRepository
from smarthexboard.utils import parseUnitMapType, parseLocation, parseUnitType, is_integer
from .smarthexboardlib.game.baseTypes import HandicapType
from .smarthexboardlib.game.cities import City
from .smarthexboardlib.game.civilizations import LeaderType
from .smarthexboardlib.game.generation import UserInterfaceImpl
from .smarthexboardlib.game.states.builds import BuildType
from .smarthexboardlib.game.unitTypes import UnitType, UnitMapType
from .smarthexboardlib.game.units import Unit
from .smarthexboardlib.map.types import TerrainType, FeatureType, ResourceType, MapType, MapSize
from .smarthexboardlib.serialisation.game import GameModelSchema


class InvalidMethodResponse(JsonResponse):
	def __init__(self, method, status_code, **kwargs):
		response_data = {
			'status': 'Invalid request method',
			'errors': [f'Method "{method}" not allowed.'],
		}
		response_data.update(kwargs)
		super().__init__(data=response_data, status=status_code)


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

		leader_selection.append((leader.value, f'{leader.title()} ({leader.civilization().title()})'))

	difficulty_selection = []
	for handicap in list(HandicapType):
		difficulty_selection.append((str(handicap), handicap.title()))

	map_type_selection = []
	for mapType in list(MapType):
		map_type_selection.append((mapType.value, mapType.title()))

	map_size_selection = []
	for mapSize in list(MapSize):
		map_size_selection.append((mapSize.value, mapSize.title()))

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
			game_id: str = f'{random.randint(100000, 999999)}'

			leader: LeaderType = form.leaderValue()
			handicap: HandicapType = form.handicapValue()
			mapSize: MapSize = form.mapSizeValue()
			mapType: MapType = form.mapTypeValue()

			print(f'generate_game({game_id}, {leader}, {handicap}, {mapSize}, {mapType})')
			# game_id, leader: LeaderType, handicap: HandicapType, mapSize: MapSize, mapType: MapType
			async_task("smarthexboard.services.generate_game", game_id, leader, handicap, mapSize, mapType)

			json_payload = {'status': 'Created', 'game_id': game_id}
			return JsonResponse(json_payload, status=201)
		else:
			# print(form.errors)
			json_payload = {'status': 'Form not valid', 'errors': form.errors}
			return JsonResponse(json_payload, status=400)
	else:
		json_payload = {'status': f'Invalid method {request.method}'}
		return JsonResponse(json_payload, status=400)


def game_create_status(request, game_id: str):
	if not is_integer(game_id):
		json_payload = {
			'error': 'invalid arg',
			'field': 'game_id',
			'value': game_id,
			'message': 'Invalid request: not a valid uuid format'
		}
		return JsonResponse(json_payload, status=400)

	game_generation = GameGenerationData.objects.filter(id=game_id).first()
	if game_generation is None:
		json_payload = {'id': game_id, 'status': f'Cannot find game generation with id: {game_id}'}
		return JsonResponse(json_payload, status=404)

	json_payload = {
		'game_id': game_id,
		'status': GameGenerationState(game_generation.state).label,
		'progress': game_generation.progress
	}
	return JsonResponse(json_payload, status=200)


def game_map(request, game_id: str):
	if not is_integer(game_id):
		json_payload = {'id': game_id, 'status': 'Invalid request: not a valid game_id format'}
		return JsonResponse(json_payload, status=400)

	if not GameDataRepository.inCacheOrDB(game_id):
		game_generation = GameGenerationData.objects.filter(id=game_id).first()
		if game_generation is None:
			json_payload = {'game_id': game_id, 'status': f'Cannot find game generated with id: {game_id}'}
			return JsonResponse(json_payload, status=404)

		current_state = GameGenerationState(game_generation.state)
		if current_state != GameGenerationState.READY:
			json_payload = {'game_id': game_id, 'status': f'Game with {game_id} is not ready yet: {current_state}'}
			return JsonResponse(json_payload, status=400)

		game_str: str = game_generation.game
		obj = GameModelSchema().loads(game_str)
		GameDataRepository.store(game_id, obj)

		GameGenerationData.objects.filter(id=game_id).delete()
	else:
		obj = GameDataRepository.fetch(game_id)

	map_dict = obj._map.to_dict(human=obj.humanPlayer())

	# convert json string to dict
	json_payload = map_dict
	return JsonResponse(json_payload, status=200)


def game_info(request, game_id: str):
	game = GameDataRepository.fetch(game_id)

	if game is None:
		json_payload = {'game_id': game_id, 'status': f'Game with id {game_id} not found in db or cache.'}
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

	# convert JSON string to dict
	json_payload = {
		'turn': game.currentTurn,
		'turnYear': game.turnYear(),
		'human': human_dict,
		'others': otherPlayers
	}
	return JsonResponse(json_payload, status=200)


def game_update(request, game_id: str):
	game = GameDataRepository.fetch(game_id)
	cache_key = f'game_updating_{game_id}'

	if game is None:
		json_payload = {'game_id': game_id, 'status': f'Game with id {game_id} not found in db or cache.'}
		return JsonResponse(json_payload, status=400)

	if cache.get(cache_key) is not None:
		json_payload = {'game_id': game_id, 'status': f'Game with id {game_id} currently updating.'}
		return JsonResponse(json_payload, status=400)

	game.userInterface = UserInterfaceImpl()

	humanPlayer = game.humanPlayer()

	if humanPlayer.hasProcessedAutoMoves() and humanPlayer.turnFinished():
		json_payload = {'game_id': game_id, 'status': f'Game turn for human is finished.'}
		return JsonResponse(json_payload, status=400)

	cache.set(cache_key, True)
	# print(f'start updating {game_id}')
	game.update()
	cache.delete(cache_key)
	# print(f'stop updating {game_id}')

	currentPlayerName = ''
	if game.activePlayer() is not None:
		if game.activePlayer().isCityState():
			currentPlayerName = f'PLAYER_CITYSTATE_{game.activePlayer().cityState.title().upper()}'
		else:
			currentPlayerName = f'PLAYER_{game.activePlayer().leader.name.upper()}'

	GameDataRepository.store(game_id, game)

	json_payload = {
		'game_id': game_id,
		'current_turn': game.currentTurn,
		'current_player': currentPlayerName,
		'human_active': humanPlayer.turnActive
		# notifications to human?
	}
	return JsonResponse(json_payload, status=200)


def game_turn(request, game_id: str):
	game = GameDataRepository.fetch(game_id)

	if game is None:
		json_payload = {'game_id': game_id, 'status': f'Game with {game_id} not found in db or cache.'}
		return JsonResponse(json_payload, status=400)

	game.userInterface = UserInterfaceImpl()

	humanPlayer = game.humanPlayer()

	if humanPlayer.hasProcessedAutoMoves() and humanPlayer.turnFinished():
		json_payload = {'game_id': game_id, 'status': f'Game turn for human is finished.'}
		return JsonResponse(json_payload, status=400)

	if humanPlayer.isTurnActive():
		humanPlayer.setProcessedAutoMovesTo(True)
		humanPlayer.setEndTurnTo(True, game)
		humanPlayer.finishTurn()
	else:
		raise Exception('unknown')

	GameDataRepository.store(game_id, game)

	json_payload = {
		'game_id': game_id,
		'current_turn': game.currentTurn
		# notifications to human?
	}
	return JsonResponse(json_payload, status=200)


def game_move_unit(request):
	"""
		@param request: incoming request
		@return: JsonResponse with:
			200: when the move was possible
			400: when the move was impossible or the parameters were of wrong type
			404: when the unit or the game was not found
	"""
	# If this is a POST request, then process the Form data
	if request.method == 'POST':

		# Create a form instance and populate it with data from the request (binding):
		form = UnitMoveForm(request.POST)

		# Check if the form is valid:
		if form.is_valid():
			game_id = form.cleaned_data['game_id']

			if not GameDataRepository.inCacheOrDB(game_id):
				json_payload = {
					'game_id': game_id,
					'status': 'Cannot move unit.',
					'errors': [f'Game with {game_id} not found in db or cache.']
				}
				return JsonResponse(json_payload, status=404)

			game = GameDataRepository.fetch(game_id)

			game.userInterface = UserInterfaceImpl()

			humanPlayer = game.humanPlayer()

			if humanPlayer is None:
				json_payload = {
					'game_id': game_id,
					'status': 'Cannot move unit.',
					'errors': ['Cannot find human player in game.']
				}
				return JsonResponse(json_payload, status=400)

			unit_type: str = form.cleaned_data['unit_type']
			old_location: str = form.cleaned_data['old_location']
			new_location: str =form.cleaned_data['new_location']

			unit_map_type = parseUnitMapType(unit_type)
			old_loc = parseLocation(old_location)
			new_loc = parseLocation(new_location)

			print(f'try to move {unit_map_type} unit from: {old_loc} to {new_loc}')

			if unit_map_type is None:
				json_payload = {
					'game_id': game_id,
					'status': 'Cannot move unit.',
					'errors': [f'Could not parse unit map type from {unit_type}.']
				}
				return JsonResponse(json_payload, status=400)

			if old_loc is None:
				json_payload = {
					'game_id': game_id,
					'status': 'Cannot move unit.',
					'errors': [f'Could not parse location from {old_location}.']
				}
				return JsonResponse(json_payload, status=400)

			if new_loc is None:
				json_payload = {
					'game_id': game_id,
					'status': 'Cannot move unit.',
					'errors': [f'Could not parse location from {new_location}.']
				}
				return JsonResponse(json_payload, status=400)

			unit: Optional[Unit] = game.unitAt(location=old_loc, unitMapType=unit_map_type)
			# print(f'unit: {unit}')

			if unit is None:
				json_payload = {
					'game_id': game_id,
					'status': 'Cannot move unit.',
					'errors': [f'Could find {unit_map_type} unit at {old_loc}.']}
				return JsonResponse(json_payload, status=404)

			if unit.player != humanPlayer:
				json_payload = {
					'game_id': game_id,
					'status': 'Cannot move unit.',
					'errors': [f'Cannot move units from another player. The unit you are trying to move is from {unit.player.name()}.']
				}
				return JsonResponse(json_payload, status=400)

			# move the unit
			ret: bool = unit.doMoveOnto(new_loc, game)

			if not ret:
				json_payload = {
					'game_id': game_id,
					'status': 'Cannot move unit.',
					'errors': [f'Unit {unit} could not be moved from {old_loc} to {new_loc}.']
				}
				return JsonResponse(json_payload, status=400)

			GameDataRepository.store(game_id, game)

			json_payload = {
				'game_id': game_id,
				'current_turn': game.currentTurn,
				'moves': unit.movesLeft(),
				# notifications to human?
			}
			return JsonResponse(json_payload, status=200)
		else:
			json_payload = {
				'status': 'Form not valid',
				'errors': form.errors
			}
			return JsonResponse(json_payload, status=400)
	else:
		json_payload = {
			'status': 'Invalid request method',
			'errors': [f'Method {request.method} not allowed.']
		}
		return JsonResponse(json_payload, status=400)


def game_actions(request):
	# If this is a POST request, then process the Form data
	if request.method == 'POST':

		# Create a form instance and populate it with data from the request (binding):
		form = UnitActionForm(request.POST)

		# Check if the form is valid:
		if form.is_valid():
			game_id = form.cleaned_data['game_id']

			if not GameDataRepository.inCacheOrDB(game_id):
				json_payload = {
					'game_id': game_id,
					'status': 'Cannot get unit actions.',
					'errors': [f'Game with {game_id} not found in db or cache.']
				}
				return JsonResponse(json_payload, status=404)

			game = GameDataRepository.fetch(game_id)

			game.userInterface = UserInterfaceImpl()

			humanPlayer = game.humanPlayer()

			if humanPlayer is None:
				json_payload = {
					'game_id': game_id,
					'status': 'Cannot get unit actions.',
					'errors': ['Cannot find human player in game.']
				}
				return JsonResponse(json_payload, status=400)

			unit_type_str: str = form.cleaned_data['unit_type']
			location_str: str = form.cleaned_data['location']

			unit_type: UnitType = parseUnitType(unit_type_str)
			unit_map_type: UnitMapType = unit_type.unitMapType()
			location = parseLocation(location_str)

			# print(f'try get unit actions {unit_type} unit at: {location}')

			if location is None:
				json_payload = {
					'game_id': game_id,
					'status': 'Cannot get unit actions.',
					'errors': [f'Could not parse location from {location_str}.']
				}
				return JsonResponse(json_payload, status=400)

			unit: Optional[Unit] = game.unitAt(location=location, unitMapType=unit_map_type)

			if unit is None:
				json_payload = {
					'game_id': game_id,
					'status': 'Cannot move unit.',
					'errors': [f'Could find {unit_map_type} unit at {location}.']}
				return JsonResponse(json_payload, status=404)

			action_list = list()

			# if unit.canMove():
			#	action_list.append('ACTION_MOVE')
			if unit.canHeal(game):
				action_list.append('ACTION_HEAL')
			if unit.canFoundAt(location, game):
				action_list.append('ACTION_FOUND_CITY')
			if unit.canAttack():
				action_list.append('ACTION_ATTACK')
			if unit.canAttackRanged():
				action_list.append('ACTION_ATTACK_RANGED')
			if unit.canPillageAt(location, game):
				action_list.append('ACTION_PILLAGE')

			for build in list(BuildType):
				if unit.canBuild(build, location, True, True, game):
					action_list.append(f'ACTION_BUILD_{build.name().upper()}')
					break

			if unit.canEverEmbark():
				for embark_location in location.neighbors():
					if unit.canEmbarkInto(embark_location, game):
						action_list.append('ACTION_EMBARK')
						break

			if len(unit.gainedPromotions()) > 0:
				action_list.append('ACTION_PROMOTE')

			action_list.append('ACTION_SKIP')
			action_list.append('ACTION_SLEEP')
			action_list.append('ACTION_DISBAND')

			json_payload = {
				'game_id': game_id,
				'current_turn': game.currentTurn,
				'action_list': action_list
				# notifications to human?
			}
			return JsonResponse(json_payload, status=200)
		else:
			json_payload = {
				'status': 'Form not valid',
				'errors': form.errors
			}
			return JsonResponse(json_payload, status=400)
	else:
		json_payload = {
			'status': 'Invalid request method',
			'errors': [f'Method {request.method} not allowed.']
		}
		return JsonResponse(json_payload, status=400)


def game_found_city(request):
	# If this is a POST request, then process the Form data
	if request.method == 'POST':

		# Create a form instance and populate it with data from the request (binding):
		form = FoundCityForm(request.POST)

		# Check if the form is valid:
		if form.is_valid():
			game_id = form.cleaned_data['game_id']

			if not GameDataRepository.inCacheOrDB(game_id):
				json_payload = {
					'game_id': game_id,
					'status': 'Cannot get unit actions.',
					'errors': [f'Game with {game_id} not found in db or cache.']
				}
				return JsonResponse(json_payload, status=404)

			game = GameDataRepository.fetch(game_id)

			game.userInterface = UserInterfaceImpl()

			humanPlayer = game.humanPlayer()

			if humanPlayer is None:
				json_payload = {
					'game_id': game_id,
					'status': 'Cannot get unit actions.',
					'errors': ['Cannot find human player in game.']
				}
				return JsonResponse(json_payload, status=400)

			# unit_type_str: str = form.cleaned_data['unit_type']
			location_str: str = form.cleaned_data['location']
			city_name: str = form.cleaned_data['city_name']

			# unit_type: UnitType = UnitType. # parseUnitType(unit_type_str)
			unit_map_type: UnitMapType = UnitMapType.civilian  # unit_type.unitMapType()
			location = parseLocation(location_str)

			# print(f'try to get unit actions {unit_type} unit at: {location}')

			if location is None:
				json_payload = {
					'game_id': game_id,
					'status': 'Cannot found city.',
					'errors': [f'Could not parse location from {location_str}.']
				}
				return JsonResponse(json_payload, status=400)

			unit: Optional[Unit] = game.unitAt(location=location, unitMapType=unit_map_type)

			if unit is None:
				json_payload = {
					'game_id': game_id,
					'status': 'Cannot found city.',
					'errors': [f'Could find {unit_map_type} unit at {location}.']}
				return JsonResponse(json_payload, status=404)

			if not unit.canFoundAt(location, game):
				json_payload = {
					'game_id': game_id,
					'status': 'Cannot found city.',
					'errors': [f'Unit {unit} cannot found city at {location}.']
				}
				return JsonResponse(json_payload, status=400)

			print(f'INFO: Found city "{city_name}" at {location}.')
			found = unit.doFoundWith(city_name, game)

			GameDataRepository.store(game_id, game)

			json_payload = {
				'game_id': game_id,
				'current_turn': game.currentTurn,
				'player': unit.player.identifier(),
				'found': found
				# notifications to human?
			}
			return JsonResponse(json_payload, status=200)
		else:
			json_payload = {
				'status': 'Form not valid',
				'errors': form.errors
			}
			return JsonResponse(json_payload, status=400)
	else:
		json_payload = {
			'status': 'Invalid request method',
			'errors': [f'Method {request.method} not allowed.']
		}
		return JsonResponse(json_payload, status=400)


def game_city_info(request):
	# If this is a POST request, then process the Form data
	if request.method == 'POST':

		# Create a form instance and populate it with data from the request (binding):
		form = CityInfoForm(request.POST)

		# Check if the form is valid:
		if form.is_valid():
			game_id = form.cleaned_data['game_id']

			if not GameDataRepository.inCacheOrDB(game_id):
				json_payload = {
					'game_id': game_id,
					'status': 'Cannot find city info.',
					'errors': [f'Game with {game_id} not found in db or cache.']
				}
				return JsonResponse(json_payload, status=404)

			game = GameDataRepository.fetch(game_id)

			game.userInterface = UserInterfaceImpl()

			humanPlayer = game.humanPlayer()

			if humanPlayer is None:
				json_payload = {
					'game_id': game_id,
					'status': 'Cannot find city info.',
					'errors': ['Cannot find human player in game.']
				}
				return JsonResponse(json_payload, status=400)

			location_str: str = form.cleaned_data['location']
			location = parseLocation(location_str)

			# print(f'try to get unit actions {unit_type} unit at: {location}')

			if location is None:
				json_payload = {
					'game_id': game_id,
					'status': 'Cannot find city info.',
					'errors': [f'Could not parse location from {location_str}.']
				}
				return JsonResponse(json_payload, status=400)

			city: Optional[City] = game.cityAt(location=location)
			if city is None:
				json_payload = {
					'game_id': game_id,
					'status': 'Cannot find city info.',
					'errors': [f'Could not find city at {location}.']
				}
				return JsonResponse(json_payload, status=404)

			if city.player != humanPlayer:
				json_payload = {
					'game_id': game_id,
					'status': 'Cannot find city info.',
					'errors': [f'City {city} is not owned by human player.']
				}
				return JsonResponse(json_payload, status=400)

			json_payload = {
				'game_id': game_id,
				'current_turn': game.currentTurn,
				'player': city.player.identifier(),
				'info': city.infoDict(game),
			}
			return JsonResponse(json_payload, status=200)
		else:
			json_payload = {
				'status': 'Form not valid',
				'errors': form.errors
			}
			return JsonResponse(json_payload, status=400)
	else:
		return InvalidMethodResponse(request.method, 400)
