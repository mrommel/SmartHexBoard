from typing import Optional

from smarthexboard.smarthexboardlib.map.base import HexPoint


class HexPath:
	pass


class HexPath:
	def __init__(self, points: [HexPoint], costs=None):
		if costs is None:
			costs = []

		self._points = points
		self._costs = costs

	def __repr__(self):
		strValue = 'HexPath('

		for pt in self._points:
			strValue += f'({pt.x}, {pt.y}), '

		strValue += ')'
		return strValue

	def __str__(self):
		strValue = 'HexPath('

		for pt in self._points:
			strValue += f'({pt.x}, {pt.y}), '

		strValue += ')'
		return strValue

	def __eq__(self, other):
		if isinstance(other, HexPath):
			for idx, pt in enumerate(self._points):
				if pt != other.points()[idx]:
					return False

			return True
		else:
			return False

	def points(self) -> [HexPoint]:
		return self._points

	def addCost(self, cost: float):
		self._costs.append(cost)

	def costs(self) -> [float]:
		return self._costs

	def cost(self) -> float:
		return sum(self._costs)

	def cropPointsUntil(self, location):
		cropIndex = self.firstIndexOf(location)

		if cropIndex is not None:
			self._points = self._points[0:cropIndex]
			self._costs = self._costs[0:cropIndex]

	def firstIndexOf(self, location) -> Optional[int]:
		cropIndex = None

		for (index, point) in enumerate(self._points):
			if point == location:
				cropIndex = index

		return cropIndex

	def prepend(self, point: HexPoint, cost: float):
		self._points.insert(0, point)
		self._costs.insert(0, cost)

		return

	def append(self, point: HexPoint, cost: float):
		self._points.append(point)
		self._costs.append(cost)

		return

	def pathWithoutFirst(self) -> HexPath:
		return HexPath(self._points[1:], self._costs[1:])

	def pathWithout(self, amount: int) -> HexPath:
		sanitizedAmount = min(amount, len(self._points) - 1)
		return HexPath(self._points[sanitizedAmount:], self._costs[sanitizedAmount:])

	def reversed(self) -> HexPath:
		return HexPath(list(reversed(self._points)), list(reversed(self._costs)))

	def firstSegments(self, numberOfPoints: int) -> HexPath:
		if numberOfPoints <= 0:
			raise Exception('cannot get negative or zero segments of path')

		return HexPath(self._points[0:numberOfPoints], self._costs[0:numberOfPoints])

