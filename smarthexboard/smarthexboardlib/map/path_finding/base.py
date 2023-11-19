# -*- coding: utf-8 -*-
""" generic A-Star path searching algorithm based on
https://github.com/jrialland/python-astar/blob/master/astar/__init__.py"""

from abc import ABC, abstractmethod
from heapq import heappush, heappop
from typing import Iterable, Union, TypeVar, Generic

# infinity as a constant
Infinite = float("inf")

# introduce generic type
T = TypeVar("T")


class AStar(ABC, Generic[T]):
	__slots__ = ()

	class SearchNode:
		"""Representation of a search node"""

		__slots__ = ("data", "gscore", "fscore", "rscore", "closed", "came_from", "out_openset")

		def __init__(
			self, data: T, gscore: float = Infinite, fscore: float = Infinite
		) -> None:
			self.data = data
			self.gscore = gscore
			self.fscore = fscore
			self.rscore = -1.0
			self.closed = False
			self.out_openset = True
			self.came_from = None

		def __lt__(self, b: "AStar.SearchNode") -> bool:
			return self.fscore < b.fscore

	class SearchNodeDict(dict):
		def __missing__(self, k):
			v = AStar.SearchNode(k)
			self.__setitem__(k, v)
			return v

	@abstractmethod
	def heuristic_cost_estimate(self, current: T, goal: T) -> float:
		"""
		Computes the estimated (rough) distance between a node and the goal.
		The second parameter is always the goal.
		This method must be implemented in a subclass.
		"""
		raise NotImplementedError

	@abstractmethod
	def distance_between(self, n1: T, n2: T) -> float:
		"""
		Gives the real distance between two adjacent nodes n1 and n2 (i.e n2
		belongs to the list of n1's neighbors).
		n2 is guaranteed to belong to the list returned by the call to neighbors(n1).
		This method must be implemented in a subclass.
		"""

	@abstractmethod
	def neighbors(self, node: T) -> Iterable[T]:
		"""
		For a given node, returns (or yields) the list of its neighbors.
		This method must be implemented in a subclass.
		"""
		raise NotImplementedError

	def is_goal_reached(self, current: T, goal: T) -> bool:
		"""
		Returns true when we can consider that 'current' is the goal.
		The default implementation simply compares `current == goal`, but this
		method can be overwritten in a subclass to provide more refined checks.
		"""
		return current == goal

	def reconstruct_path(self, last: SearchNode, reverse_path=False) -> Iterable[T]:
		def _gen():
			current = last
			while current:
				yield current.data, current.rscore
				current = current.came_from

		if reverse_path:
			return _gen()
		else:
			return reversed(list(_gen()))

	def astar(self, start: T, goal: T, reverse_path: bool = False) -> Union[Iterable[T], None]:
		if self.is_goal_reached(start, goal):
			return [(start, 0)]
		search_nodes = AStar.SearchNodeDict()
		start_node = search_nodes[start] = AStar.SearchNode(
			start, gscore=0.0, fscore=self.heuristic_cost_estimate(start, goal)
		)
		open_set: list = []
		heappush(open_set, start_node)
		while open_set:
			current = heappop(open_set)
			if self.is_goal_reached(current.data, goal):
				return self.reconstruct_path(current, reverse_path)

			current.out_openset = True
			current.closed = True
			for neighbor in map(lambda n: search_nodes[n], self.neighbors(current.data)):
				if neighbor.closed:
					continue

				# Compute the cost from the current step to that step
				rscore = self.distance_between(current.data, neighbor.data)
				tentative_gscore = current.gscore + rscore
				if tentative_gscore >= neighbor.gscore:
					continue
				neighbor.came_from = current
				neighbor.gscore = tentative_gscore
				neighbor.fscore = tentative_gscore + self.heuristic_cost_estimate(neighbor.data, goal)
				neighbor.rscore = rscore

				if neighbor.out_openset:
					neighbor.out_openset = False
					heappush(open_set, neighbor)
				else:
					# re-add the node in order to re-sort the heap
					open_set.remove(neighbor)
					heappush(open_set, neighbor)

		return None
