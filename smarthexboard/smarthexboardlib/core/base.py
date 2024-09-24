import logging
import random
from enum import Enum
from functools import reduce
from typing import Optional


class ExtendedEnum(Enum):

	@classmethod
	def values(cls):
		return list(map(lambda c: c.value, cls))


class InvalidEnumError(Exception):
	def __init__(self, type_value):
		super().__init__(f'enum value {type_value} not handled')


class WeightedBaseList:
	pass


class WeightedBaseList(dict):
	def __init__(self, initialDict: Optional[dict] = None):
		super().__init__()

		if initialDict is not None:
			for k, v in initialDict.items():
				self.setWeight(v, k)

	def addWeight(self, value, identifier):
		self[identifier] = self.get(identifier, 0) + value

	def mulWeight(self, value, identifier):
		self[identifier] = self.get(identifier, 0) * value

	def divWeight(self, value, identifier):
		self[identifier] = self.get(identifier, 0) * value

	def setWeight(self, value, identifier):
		self[identifier] = value

	def weight(self, identifier):
		return self.get(identifier, 0)

	def totalWeights(self) -> float:
		return reduce(lambda a, b: a + b, list(self.values()))

	def removeAll(self):
		self.clear()

	def top3(self):
		top3Dict = dict()

		for key, value in self.items():
			# if not populated, fill it up
			if len(top3Dict) < 3:
				top3Dict[key] = value
				continue

			smallestTop3Key = None

			# find the smallest in top3
			for top3Key, top3Value in top3Dict.items():
				if smallestTop3Key is None:
					smallestTop3Key = top3Key
					continue

				if self[smallestTop3Key] > top3Value:
					smallestTop3Key = top3Key

			# if current value is bigger than smallest in top3, replace it
			if self[smallestTop3Key] < value:
				del top3Dict[smallestTop3Key]
				top3Dict[key] = value

		tmp = WeightedBaseList()

		for top3Key, top3Value in top3Dict.items():
			tmp[top3Key] = top3Value

		return tmp

	def chooseLargest(self):
		bestValue = -1
		bestObject = None

		for key, value in self.items():
			if value > bestValue:
				bestValue = value
				bestObject = key

		return bestObject

	def distributeByWeight(self):
		"""distributes the keys based on the weight - it will return 100 items"""
		if len(self.keys()) == 0:
			raise Exception(f'Cannot distribute weighted array - dict is empty')

		sumValue = sum(self.values())
		output = []

		if len(self.items()) > 0 and sumValue == 0.0:
			logging.warning(f'Cannot distribute weighted array - dict weights sum up to zero - selecting random')
			keysList = list(self.keys())
			for _ in range(100):
				output.append(random.choice(keysList))

			return output

		for key, value in self.items():
			amount = int(value * 100.0 / sumValue)
			for _ in range(amount):
				output.append(key)

		additional = 100 - len(output)
		for _ in range(additional):
			output.append(list(self.keys())[-1])

		assert len(output) == 100

		return output

	def chooseFromTopChoices(self):
		if len(self.keys()) == 0:
			return None

		# select one
		selectedIndex = random.randrange(100)

		weightedLocations = self.top3()
		weightedLocationsArray = weightedLocations.distributeByWeight()
		selectedItem = weightedLocationsArray[selectedIndex]
		return selectedItem

	def addItems(self, items: WeightedBaseList):
		for key in items.keys():
			self[key] = items[key]

	def sortByValue(self, reverse: bool = False):
		tmpDict = dict(sorted(self.items(), key=lambda x: x[1], reverse=reverse))

		self.clear()

		for k, v in tmpDict.items():
			self.setWeight(v, k)


class WeightedStringList(WeightedBaseList):
	pass


def contains(filter, list) -> bool:
	"""
		checks if there is one element in the list that matches the lambda condition

		@see https://stackoverflow.com/a/598407
		´´´
		if contains(lambda x: x.n == 3, myList):  # True if any element has .n==3
			# do stuff
		´´´
	"""
	for x in list:
		if filter(x):
			return True

	return False
