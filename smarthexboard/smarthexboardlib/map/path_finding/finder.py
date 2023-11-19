import sys
from typing import Optional

from smarthexboard.smarthexboardlib.game.unitTypes import UnitMapType
from smarthexboard.smarthexboardlib.map.base import HexPoint
# from map.map import MapModel
from smarthexboard.smarthexboardlib.map.path_finding.base import AStar
from smarthexboard.smarthexboardlib.map.path_finding.path import HexPath
from smarthexboard.smarthexboardlib.map.types import UnitMovementType, TerrainType, FeatureType


class AStarDataSource:
	def __init__(self, grid, movement_type: UnitMovementType):
		self.grid = grid
		self.movement_type = movement_type

	def walkableAdjacentTilesCoords(self, tile_coord: HexPoint) -> [HexPoint]:
		pass

	def costToMove(self, from_tile_coord: HexPoint, to_adjacent_tile_coord: HexPoint) -> float:
		pass


class MoveTypeIgnoreUnitsOptions:
	def __init__(self, ignore_sight, can_embark, can_enter_ocean):
		self.ignore_sight = ignore_sight
		self.can_embark = can_embark
		self.can_enter_ocean = can_enter_ocean
		# self.wrapX = wrapX


class MoveTypeIgnoreUnitsPathfinderDataSource(AStarDataSource):
	def __init__(self, grid, movement_type: UnitMovementType, player, options: MoveTypeIgnoreUnitsOptions):
		super().__init__(grid, movement_type)
		self.player = player
		self.options = options

	def walkableAdjacentTilesCoords(self, tile_coord: HexPoint) -> [HexPoint]:
		walkable_coords = []

		for neighbor in tile_coord.neighbors():
			if not self.grid.valid(neighbor):
				continue

			to_tile = self.grid.tileAt(neighbor)

			if self.movement_type == UnitMovementType.walk:
				if to_tile.terrain() == TerrainType.ocean and not self.options.can_enter_ocean:
					continue
				if to_tile.isWater() and self.options.can_embark and to_tile.isImpassable(UnitMovementType.swim):
					continue

				if to_tile.isLand() and to_tile.isImpassable(UnitMovementType.walk):
					continue
			else:
				if to_tile.terrain() == TerrainType.ocean and not self.options.can_enter_ocean:
					continue

				if to_tile.isWater() and to_tile.isImpassable(UnitMovementType.swim):
					continue

			# use sight?
			if not self.options.ignore_sight:
				# skip if not in sight or discovered
				if not to_tile.isDiscoveredBy(self.player):
					continue

				if not to_tile.isVisibleTo(self.player):
					continue

			from_tile = self.grid.tileAt(tile_coord)

			if to_tile.movementCost(self.movement_type, from_tile) < UnitMovementType.max.value:
				walkable_coords.append(neighbor)

		return walkable_coords

	def costToMove(self, from_tile_coord: HexPoint, to_adjacent_tile_coord: HexPoint) -> float:
		from_tile = self.grid.tileAt(from_tile_coord)
		to_tile = self.grid.tileAt(to_adjacent_tile_coord)

		return to_tile.movementCost(self.movement_type, from_tile)


class MoveTypeUnitAwareOptions:
	def __init__(self, unitMapType: UnitMapType, ignore_sight: bool, can_embark: bool, can_enter_ocean: bool):
		self.unitMapType: UnitMapType = unitMapType
		self.ignore_sight: bool = ignore_sight
		self.can_embark: bool = can_embark
		self.can_enter_ocean: bool = can_enter_ocean


class MoveTypeUnitAwarePathfinderDataSource(AStarDataSource):
	def __init__(self, grid, movement_type: UnitMovementType, player, options: MoveTypeUnitAwareOptions):
		super().__init__(grid, movement_type)
		self.player = player
		self.options = options

	def walkableAdjacentTilesCoords(self, tile_coord: HexPoint) -> [HexPoint]:
		walkable_coords = []

		for neighbor in tile_coord.neighbors():
			if not self.grid.valid(neighbor):
				continue

			to_tile = self.grid.tileAt(neighbor)

			if self.movement_type == UnitMovementType.walk:
				if to_tile.terrain() == TerrainType.ocean and not self.options.can_enter_ocean:
					continue
				if to_tile.isWater() and self.options.can_embark and to_tile.isImpassable(UnitMovementType.swim):
					continue

				if to_tile.isLand() and to_tile.isImpassable(UnitMovementType.walk):
					continue
			else:
				if to_tile.terrain() == TerrainType.ocean and not self.options.can_enter_ocean:
					continue

				if to_tile.isWater() and to_tile.isImpassable(UnitMovementType.swim):
					continue

			# use sight?
			if not self.options.ignore_sight:
				# skip if not in sight or discovered
				if not to_tile.isDiscoveredBy(self.player):
					continue

				if not to_tile.isVisibleTo(self.player):
					continue

			unitsAtTarget = self.grid.unitsAt(neighbor)
			blocked: bool = False
			for unit in unitsAtTarget:
				if self.player == unit.player:
					# fixme: walk thru?
					if unit.unitMapType() == self.options.unitMapType:
						# one cannot go into tiles with own units with same type
						blocked = True
				elif not self.player.isAtWarWith(unit.player):
					# one cannot step on tiles of friendly units
					# or the other way around: only attack hostile units
					blocked = True

			if blocked:
				continue

			from_tile = self.grid.tileAt(tile_coord)

			if to_tile.movementCost(self.movement_type, from_tile) < UnitMovementType.max.value:
				walkable_coords.append(neighbor)

		return walkable_coords

	def costToMove(self, from_tile_coord: HexPoint, to_adjacent_tile_coord: HexPoint) -> float:
		from_tile = self.grid.tileAt(from_tile_coord)
		to_tile = self.grid.tileAt(to_adjacent_tile_coord)

		return to_tile.movementCost(self.movement_type, from_tile)


class InfluencePathfinderDataSource(AStarDataSource):
	def __init__(self, grid, cityLocation: HexPoint):
		super().__init__(grid, UnitMovementType.walk)
		self.cityLocation = cityLocation

	def walkableAdjacentTilesCoords(self, tile_coord: HexPoint) -> [HexPoint]:
		neighbors: [HexPoint] = []

		for neighbor in tile_coord.neighbors():
			# if mapModel.wrapX
			# 	neighbor = mapModel.wrap(point: neighbor)

			if self.grid.valid(neighbor):
				neighbors.append(neighbor)

		return neighbors

	def costToMove(self, from_tile_coord: HexPoint, to_adjacent_tile_coord: HexPoint) -> float:
		"""Influence pathfinder - compute cost of a path"""
		cost = 0

		cityTile = self.grid.tileAt(self.cityLocation)
		toTile = self.grid.tileAt(to_adjacent_tile_coord)
		fromTile = self.grid.tileAt(from_tile_coord)

		if from_tile_coord != self.cityLocation:
			if cityTile.hasOwner() and toTile.hasOwner() and cityTile.owner().leader != toTile.owner().leader:
				cost += 15

		if fromTile.isRiverToCrossTowards(toTile):
			cost += 1  # INFLUENCE_RIVER_COST

		if toTile.isHills():
			# Hill cost
			cost += 2  # INFLUENCE_HILL_COST
		elif toTile.hasFeature(FeatureType.mountains):
			# Mountain Cost
			cost += 3  # INFLUENCE_MOUNTAIN_COST
		else:
			# Not a hill or mountain - use the terrain cost
			cost += 1  # GC.getTerrainInfo(pToPlot->getTerrainType())->getInfluenceCost();
			cost += 0 if not toTile.hasAnyFeature() else 1  # GC.getFeatureInfo(pToPlot->getFeatureType())->getInfluenceCost()

		cost = max(1, cost)
		return float(cost)


class AStarPathfinder(AStar):

	def __init__(self, data_source):
		self.data_source = data_source

	def heuristic_cost_estimate(self, current: HexPoint, goal: HexPoint):
		return current.distance(goal)

	def distance_between(self, n1, n2):
		return self.data_source.costToMove(n1, n2)

	def neighbors(self, node):
		return self.data_source.walkableAdjacentTilesCoords(node)

	def is_goal_reached(self, current, goal):
		return current == goal

	def shortestPath(self, from_point: HexPoint, to_point: HexPoint) -> Optional[HexPath]:
		if self.data_source is None:
			raise Exception('no datasource')

		if not isinstance(from_point, HexPoint):
			raise Exception(f'from_point {from_point} is no HexPoint but {type(from_point)}')

		if not isinstance(to_point, HexPoint):
			raise Exception(f'to_point {to_point} is no HexPoint but {type(to_point)}')

		pts_or_none = self.astar(from_point, to_point, False)

		if pts_or_none is not None:
			points = []
			costs = []
			for pt, cost in pts_or_none:
				points.append(pt)
				costs.append(max(0.0, cost))

			return HexPath(points, costs)

		return None

	def doesPathExist(self, from_point, to_point) -> bool:
		return self.shortestPath(from_point, to_point) is not None

	def turnsToReachTarget(self, unit, target: HexPoint, simulation) -> int:
		"""
		How many turns will it take a unit to get to a target plot (returns MAX_INT if can't reach at all;
		returns 0 if makes it in 1 turn and has movement left)
        Should call it with bIgnoreStacking true if want foolproof way to see if can make it in 0 turns
        (since that way doesn't open the 2nd layer of the pathfinder)

		@param unit:
		@param target:
		@param simulation:
		@return:
		"""
		if unit.maxMoves(simulation) <= 0:
			return sys.maxsize

		path = self.shortestPath(unit.location, target)
		if path is not None:
			turns: int = 0
			turnCost: float = 0.0
			unitMaxMoves = unit.maxMoves(simulation)

			for cost in path.costs():
				turnCost += cost
				if turnCost >= unitMaxMoves:
					turns += 1
					turnCost = 0.0

			return max(turns, 1)

		return sys.maxsize
