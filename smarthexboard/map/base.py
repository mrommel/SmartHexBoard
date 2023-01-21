""" base types module """
from enum import Enum


class ExtendedEnum(Enum):

	@classmethod
	def list(cls):
		return list(map(lambda c: c, cls))


class Size:
	"""class that store a size object with a width and a height parameter"""

	def __init__(self, width, height):
		"""
			constructs a Size object from given width and height (both int)
			@param width: given width of object
			@param height: given height of object
		"""
		if isinstance(width, int) and isinstance(height, int):
			self.width = width
			self.height = height
		else:
			raise AttributeError(f'Size with wrong attributes: {width} / {height}')

	def __str__(self):
		"""returns a string representation of the Size"""
		return f'[Size x: {self.width}, y: {self.height}]'


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
		elif self == HexDirection.northEast:
			return HexCube(1, 0, -1)
		elif self == HexDirection.southEast:
			return HexCube(1, -1, 0)
		elif self == HexDirection.south:
			return HexCube(0, -1, 1)
		elif self == HexDirection.southWest:
			return HexCube(-1, 0, 1)
		elif self == HexDirection.northWest:
			return HexCube(-1, 1, 0)
		else:
			raise AttributeError(f'HexDirection {self} can\'t get cubeDirection')

	def __str__(self):
		return f'[HexDirection {self.value}]'


class HexPoint(Point):
	def __init__(self, x_or_hex_cube, y=None):
		if isinstance(x_or_hex_cube, int) and isinstance(y, int):
			x = x_or_hex_cube
			self.x = x
			self.y = y
		elif isinstance(x_or_hex_cube, HexCube) and y is None:
			hex_cube = x_or_hex_cube
			# even-q
			self.x = int(hex_cube.q + (hex_cube.s + (hex_cube.s & 1)) / 2)
			self.y = hex_cube.s
		else:
			raise AttributeError(f'HexPoint with wrong attributes: {x_or_hex_cube} / {y}')

	def neighbor(self, direction: HexDirection, distance: int = 1):
		cube_direction = direction.cubeDirection()
		cube_direction = cube_direction.mul(distance)

		cube_neighbor = HexCube(self)
		cube_neighbor = cube_neighbor.add(cube_direction)

		return HexPoint(cube_neighbor)

	def neighbors(self):
		neighboring = []

		neighboring.append(self.neighbor(HexDirection.north))
		neighboring.append(self.neighbor(HexDirection.northEast))
		neighboring.append(self.neighbor(HexDirection.southEast))
		neighboring.append(self.neighbor(HexDirection.south))
		neighboring.append(self.neighbor(HexDirection.southWest))
		neighboring.append(self.neighbor(HexDirection.northWest))

		return neighboring

	def __eq__(self, other):
		"""Overrides the default implementation"""
		if isinstance(other, HexPoint):
			return self.x == other.x and self.y == other.y

		return False

	def __str__(self):
		"""returns a string representation of the HexPoint"""
		return f'[HexPoint x: {self.x}, y: {self.y}]'

	def __reor__(self):
		"""returns a string representation of the HexPoint"""
		return f'[HexPoint x: {self.x}, y: {self.y}]'


class Array2D:
	"""class that stores a 2 dimensional matrix of complex or basic objects"""

	def __init__(self, width, height, fill=None):
		"""
			constructs the array with given width and height
			@param width: int or Size
			@param height: int or initial value, if first param is of type Size
			@param fill: initial value, if not provided as height
		"""
		if isinstance(width, Size):
			size = width
			self.width = size.width
			self.height = size.height
			fill_value = height
		elif isinstance(width, int) and isinstance(height, int):
			self.width = width
			self.height = height
			fill_value = fill
		else:
			raise AttributeError(f'Array2D with wrong attributes: {width} / {height}')

		if fill_value is None:
			fill_value = 0

		self.values = [[fill_value] * self.width for i in range(self.height)]

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
