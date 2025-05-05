import math
import uuid
from typing import Optional, Union

from smarthexboard.smarthexboardlib.core.base import ExtendedEnum


class Size:
	"""class that store a size object with a width and a height parameter"""

	def __init__(self, width, height):
		"""
            constructs a Size object from given width and height (both int)
            @param width: given width of object
            @param height: given height of object
        """
		if isinstance(width, int) and isinstance(height, int):
			self._width = width
			self._height = height
		else:
			raise AttributeError(f'Size with wrong attributes: {width} / {height}')

	def width(self) -> int:
		return self._width

	def height(self) -> int:
		return self._height

	def __str__(self):
		"""returns a string representation of the Size"""
		return f'Size(width={self._width}, height={self._height})'

	def __repr__(self):
		"""returns a string representation of the Size"""
		return f'Size(width={self._width}, height={self._height})'


class Point:
	"""class that stores coordinates"""

	def __init__(self, x: int, y: int):
		"""
            constructs a Point object from x and y coordinates

            @param x: x coordinate
            @param y: y coordinate
        """
		if isinstance(x, int) and isinstance(y, int):
			self.x = x
			self.y = y
		else:
			raise AttributeError(f'Point with wrong attributes: {x} / {y}')

	def __str__(self):
		"""returns a string representation of the Point"""
		return f'[Point x: {self.x}, y: {self.y}]'


class HexPoint:
	pass


class BoundingBox:
	def __init__(self, points=None):
		if points is None:
			points = []

		self.minX = -1
		self.minY = -1
		self.maxX = -1
		self.maxY = -1

		if len(points) > 0:
			self.minX = points[0].x
			self.minY = points[0].y
			self.maxX = points[0].x
			self.maxY = points[0].y

			for pt in points:
				self.minX = min(self.minX, pt.x)
				self.minY = min(self.minY, pt.y)
				self.maxX = max(self.maxX, pt.x)
				self.maxY = max(self.maxY, pt.y)

	def width(self) -> int:
		return self.maxX - self.minX

	def height(self) -> int:
		return self.maxY - self.minY

	def __eq__(self, other):
		if isinstance(other, BoundingBox):
			return self.minX == other.minX and self.minY == other.minY and \
				self.maxX == other.maxX and self.maxY == other.maxY

		return False

	def __str__(self):
		return f'BoundingBox( ({self.minX}, {self.minY}) -> ({self.maxX}, {self.maxY}) )'

	def __repr__(self):
		return f'BoundingBox( ({self.minX}, {self.minY}) -> ({self.maxX}, {self.maxY}) )'


class HexArea:
	pass


class HexArea:
	def __init__(self, center_or_list, radius: int = 0):
		if isinstance(center_or_list, list):
			points = center_or_list
			self._initFromPoints(points, radius)
		elif isinstance(center_or_list, HexPoint):
			points = {center_or_list}
			self._initFromPoints(points, radius)
		elif isinstance(center_or_list, dict):
			points = []
			for point_dict in center_or_list['_points']:
				points.append(HexPoint(point_dict))

			self._points = list(points)
			self._boundingBox = BoundingBox(list(points))
			self.identifier = center_or_list['identifier']
			self.setValue(center_or_list['_value'])
			self._isWater = False

		else:
			raise RuntimeError(f'wrong type {center_or_list} - list or HexPoint expected')

	def _initFromPoints(self, points, radius):
		self.identifier = str(uuid.uuid4())

		for _ in range(radius):
			new_tmp = set()
			for elem in points:
				new_tmp = new_tmp.union(elem.neighbors())
			points = points.union(new_tmp)

		self._points = list(points)

		self._boundingBox = BoundingBox(list(points))
		self._value = None
		self._isWater = False

	def __iter__(self):
		return self._points.__iter__()

	def __eq__(self, other):
		if isinstance(other, HexArea):
			return self.identifier == other.identifier

		raise Exception(f'HexArea can only be compared to HexArea and not to {type(other)}')

	def __repr__(self):
		return f'HexArea({self.identifier}, {len(self._points)} points, {self._boundingBox}, {self._value})'

	def boundingBox(self) -> BoundingBox:
		return self._boundingBox

	def width(self) -> int:
		return self._boundingBox.width()

	def height(self) -> int:
		return self._boundingBox.height()

	def isWater(self) -> bool:
		return self._isWater

	def setWater(self, value: bool):
		self._isWater = value

	def setValue(self, value: Optional[int]):
		self._value = value

	def value(self) -> Optional[int]:
		return self._value

	def center(self) -> HexPoint:
		sum_x = 0
		sum_y = 0
		num = 0

		for point in self._points:
			sum_x += point.x
			sum_y += point.y

			num += 1

		if num == 0:
			return HexPoint(-1, -1)

		return HexPoint(int(sum_x / num), int(sum_y / num))

	def first(self) -> Optional[HexPoint]:
		return next(iter(self._points), None)

	def points(self) -> [HexPoint]:
		return self._points

	def divideHorizontally(self, dx: int) -> (HexArea, HexArea):
		# puts all points left of dx in first area and all points right of dx in second area
		points_first = []
		points_second = []

		for point in self._points:
			if point.x < dx:
				points_first.append(point)
			else:
				points_second.append(point)

		return HexArea(points_first), HexArea(points_second)

	def divideVertically(self, dy: int) -> (HexArea, HexArea):
		# puts all points above of dy in first area and all points below of dy in second area
		points_first = []
		points_second = []

		for point in self._points:
			if point.y < dy:
				points_first.append(point)
			else:
				points_second.append(point)

		return HexArea(points_first), HexArea(points_second)

	def addPoint(self, point):
		self._points.append(point)
		self._boundingBox = BoundingBox(self._points)

	def numberOfImprovements(self, improvement, simulation) -> int:
		improvements = 0
		for pt in self._points:
			tile = simulation.tileAt(pt)

			if tile is not None:
				if tile.hasImprovement(improvement):
					improvements += 1

		return improvements


class HexCube:
	def __init__(self, q_or_hex_point, r=None, s=None):
		if isinstance(q_or_hex_point, HexPoint) and r is None and s is None:
			hex_point = q_or_hex_point
			# even-q
			tmp_q = hex_point.x - (hex_point.y + (hex_point.y & 1)) / 2
			tmp_s = hex_point.y
			self.q = tmp_q
			self.r = -tmp_q - tmp_s
			self.s = tmp_s
		elif isinstance(q_or_hex_point, int) and isinstance(r, int) and isinstance(s, int):
			q = q_or_hex_point
			self.q = q
			self.r = r
			self.s = s
		else:
			raise AttributeError(f'HexCube with wrong attributes: {q_or_hex_point} / {r} / {s}')

	def mul(self, factor):
		return HexCube(int(self.q * factor), int(self.r * factor), int(self.s * factor))

	def add(self, right):
		return HexCube(int(self.q + right.q), int(self.r + right.r), int(self.s + right.s))

	def distance(self, hex_cube):
		return max(abs(self.q - hex_cube.q), abs(self.r - hex_cube.r), abs(self.s - hex_cube.s))

	def toScreen(self) -> Point:
		# function HexOrientation() {
		f0 = 3.0 / 2.0
		f1 = 0.0
		f2 = math.sqrt(3.0) / 2.0
		f3 = math.sqrt(3.0)
		size = Size(36, 26)
		origin = Point(270, 470)

		x = int((f0 * self.q + f1 * self.r) * size.width())
		y = int((f2 * self.q + f3 * self.r) * size.height())

		return Point(x + origin.x, y + origin.y)


class HexDirection:
	pass


class HexDirection(ExtendedEnum):
	north = 'north'
	northEast = 'northEast'
	southEast = 'southEast'
	south = 'south'
	southWest = 'southWest'
	northWest = 'northWest'

	def cubeDirection(self):
		if self == HexDirection.north:
			return HexCube(0, 1, -1)
		if self == HexDirection.northEast:
			return HexCube(1, 0, -1)
		if self == HexDirection.southEast:
			return HexCube(1, -1, 0)
		if self == HexDirection.south:
			return HexCube(0, -1, 1)
		if self == HexDirection.southWest:
			return HexCube(-1, 0, 1)
		if self == HexDirection.northWest:
			return HexCube(-1, 1, 0)

		raise AttributeError(f'HexDirection {self} can\'t get cubeDirection')

	def opposite(self) -> HexDirection:
		if self == HexDirection.north:
			return HexDirection.south
		if self == HexDirection.northEast:
			return HexDirection.southWest
		if self == HexDirection.southEast:
			return HexDirection.northWest
		if self == HexDirection.south:
			return HexDirection.north
		if self == HexDirection.southWest:
			return HexDirection.northEast
		if self == HexDirection.northWest:
			return HexDirection.southEast

		raise AttributeError(f'HexDirection {self} can\'t get opposite')

	def clockwiseNeighbor(self) -> HexDirection:
		if self == HexDirection.north:
			return HexDirection.northEast
		if self == HexDirection.northEast:
			return HexDirection.southEast
		if self == HexDirection.southEast:
			return HexDirection.south
		if self == HexDirection.south:
			return HexDirection.southWest
		if self == HexDirection.southWest:
			return HexDirection.northWest
		if self == HexDirection.northWest:
			return HexDirection.north

		raise AttributeError(f'HexDirection {self} can\'t get clockwiseNeighbor')

	def counterClockwiseNeighbor(self) -> HexDirection:
		if self == HexDirection.north:
			return HexDirection.northWest
		if self == HexDirection.northEast:
			return HexDirection.north
		if self == HexDirection.southEast:
			return HexDirection.northEast
		if self == HexDirection.south:
			return HexDirection.southEast
		if self == HexDirection.southWest:
			return HexDirection.south
		if self == HexDirection.northWest:
			return HexDirection.southWest

		raise AttributeError(f'HexDirection {self} can\'t get counterClockwiseNeighbor')

	def __str__(self):
		return f'[HexDirection {self.value}]'


class HexPoint(Point):
	def __init__(self, x_or_hex_cube: Union[int, HexCube, dict, 'HexPoint'], y: Optional[int] = None):
		if isinstance(x_or_hex_cube, int) and isinstance(y, int):
			x = x_or_hex_cube
			super().__init__(x, y)
			self.x = x
			self.y = y
		elif isinstance(x_or_hex_cube, HexCube) and y is None:
			hex_cube = x_or_hex_cube
			x_value = int(hex_cube.q + (hex_cube.s + (hex_cube.s & 1)) / 2)
			# even-q
			super().__init__(x_value, hex_cube.s)
			self.x = x_value
			self.y = hex_cube.s
		elif isinstance(x_or_hex_cube, dict) and 'x' in x_or_hex_cube and 'y' in x_or_hex_cube and y is None:
			super().__init__(0, 0)
			self.x = x_or_hex_cube['x']
			self.y = x_or_hex_cube['y']
		elif isinstance(x_or_hex_cube, HexPoint):
			super().__init__(0, 0)
			self.x = x_or_hex_cube.x
			self.y = x_or_hex_cube.y
		else:
			raise AttributeError(f'HexPoint with wrong attributes: {x_or_hex_cube} / {y}')

	def neighbor(self, direction: HexDirection, distance: int = 1):
		cube_direction = direction.cubeDirection()
		cube_direction = cube_direction.mul(distance)

		cube_neighbor = HexCube(self)
		cube_neighbor = cube_neighbor.add(cube_direction)

		return HexPoint(cube_neighbor)

	def neighbors(self):
		return [
			self.neighbor(HexDirection.north),
			self.neighbor(HexDirection.northEast),
			self.neighbor(HexDirection.southEast),
			self.neighbor(HexDirection.south),
			self.neighbor(HexDirection.southWest),
			self.neighbor(HexDirection.northWest)
		]

	def isNeighborOf(self, other: HexPoint) -> bool:
		return other in self.neighbors()

	def directionTowards(self, target: HexPoint) -> HexDirection:
		"""
			returns the direction of the neighbor
			@param target:
			@return:
		"""
		for direction in list(HexDirection):
			if self.neighbor(direction, 1) == target:
				return direction

		angle = HexPoint.screenAngle(self, target)
		return HexPoint.degreesToDirection(angle)

	def toScreen(self) -> Point:
		hex_cube = HexCube(self)
		return hex_cube.toScreen()

	@staticmethod
	def screenAngle(from_point: HexPoint, towards_point: HexPoint) -> int:
		fromScreenPoint = from_point.toScreen()
		towardsScreenPoint = towards_point.toScreen()

		delta_x = towardsScreenPoint.x - fromScreenPoint.x
		delta_y = towardsScreenPoint.y - fromScreenPoint.y

		return int(math.atan2(delta_x, delta_y) * (180.0 / math.pi))

	@staticmethod
	def degreesToDirection(angle: int) -> HexDirection:
		if angle < 0:
			angle += 360

		if 30 < angle <= 90:
			return HexDirection.northEast
		if 90 < angle <= 150:
			return HexDirection.southEast
		if 150 < angle <= 210:
			return HexDirection.south
		if 210 < angle <= 270:
			return HexDirection.southWest
		if 270 < angle <= 330:
			return HexDirection.northWest

		return HexDirection.north

	def distance(self, target: HexPoint) -> int:
		self_cube = HexCube(self)
		hex_cube = HexCube(target)
		return self_cube.distance(hex_cube)

	def areaWithRadius(self, radius: int):
		return HexArea(self, radius)

	def __hash__(self):
		return self.x * 1000 + self.y

	def __eq__(self, other):
		"""Overrides the default implementation"""
		if isinstance(other, HexPoint):
			return self.x == other.x and self.y == other.y

		return False

	def __str__(self):
		"""returns a string representation of the HexPoint"""
		return f'HexPoint({self.x}, {self.y})'

	def __repr__(self):
		"""returns a string representation of the HexPoint"""
		return f'HexPoint({self.x}, {self.y})'


class Array2D:
	"""class that stores a 2-dimensional matrix of complex or basic objects"""

	def __init__(self, width_or_size, height=None, fill=None):
		"""
			constructs the array with given width and height
			@param width: int or Size
			@param height: int or initial value, if first param is of type Size
			@param fill: initial value, if not provided as height
		"""
		if isinstance(width_or_size, Size) and height is None:
			size: Size = width_or_size
			self.width = size.width()
			self.height = size.height()
			fill_value = height
		elif isinstance(width_or_size, int) and isinstance(height, int):
			width: int = width_or_size
			self.width = width
			self.height = height
			fill_value = fill
		else:
			raise AttributeError(f'Array2D with wrong attributes: {width_or_size} / {height}')

		if fill_value is None:
			fill_value = 0

		self.values = [[fill_value] * self.width for _ in range(self.height)]

	def __repr__(self):
		return f'Array2D({self.width}, {self.height})'

	def __iter__(self):
		return self.values.__iter__()

	def valid(self, point_or_x, y=None):
		"""
            checks if the given Point is inside the two-dimensional Array
            @param point_or_x: Point or x coordinate to check
            @param y: y coordinate to check
            @return: true, if point is inside the two-dimensional Array
        """
		if isinstance(point_or_x, Point):
			point = point_or_x
			x_val = point.x
			y_val = point.y
		elif isinstance(point_or_x, int) and isinstance(y, int):
			x_val = point_or_x
			y_val = y
		else:
			raise AttributeError(f'Array2D.valid with wrong attributes: {point_or_x} / {y}')

		return 0 <= x_val < self.width and 0 <= y_val < self.height

	def fill(self, value):
		for y in range(self.height):
			for x in range(self.width):
				self.values[y][x] = value

	def __str__(self):
		mtx_str = '------------- output -------------\n'

		for i in range(self.height):
			mtx_str += ('|' + ', '.join(map(lambda x: '{0:8.3f}'.format(x), self.values[i])) + '| \n')

		mtx_str += '----------------------------------'

		return mtx_str

	def to_dict(self):
		"""
		converts the Array2D into a dict for serialization
		@return: dict of Array2D
		"""
		values_dict = {}

		for j in range(self.height):
			row_array = []

			for i in range(self.width):
				if getattr(self.values[j][i], "to_dict", None) is not None:
					row_array.append(self.values[j][i].to_dict())
				else:
					row_array.append(str(self.values[j][i]))

			values_dict[j] = row_array

		# print(values_dict)

		return {
			'width': self.width,
			'height': self.height,
			'values': values_dict
		}
