import os
import unittest

import django
from django.utils.translation.trans_real import get_language, translation

from smarthexboard.smarthexboardlib.map.types import Yields, YieldType, YieldList

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SmartBoardGame.settings')
django.setup()


# mock translation for testing
def mock_gettext(message: str) -> str:
	if message == 'TXT_KEY_YIELD_FOOD_TITLE':
		return 'Food'
	elif message == 'TXT_KEY_YIELD_PRODUCTION_TITLE':
		return 'Production'
	elif message == 'TXT_KEY_YIELD_GOLD_TITLE':
		return 'Gold'
	elif message == 'TXT_KEY_LEADER_BARBARIAN':
		return 'Barbarian'

	# raise f'Translation not available for message: {message}'
	return message


class TestYields(unittest.TestCase):
	def setUp(self):
		translation(get_language()).gettext = mock_gettext

	def test_constructor(self):
		yields = Yields(0.0, 0.0, 0.0)

		self.assertEqual(yields.food, 0.0)
		self.assertEqual(yields.production, 0.0)
		self.assertEqual(yields.gold, 0.0)

	def test_addition(self):
		yields1 = Yields(10.0, 5.0, 2.0)
		yields2 = Yields(3.0, 4.0, 1.0)

		result = yields1 + yields2

		self.assertEqual(result.food, 13.0)
		self.assertEqual(result.production, 9.0)
		self.assertEqual(result.gold, 3.0)

	def test_value(self):
		yields = Yields(10.0, 5.0, 2.0)

		self.assertEqual(yields.food, 10.0)
		self.assertEqual(yields.production, 5.0)
		self.assertEqual(yields.gold, 2.0)

	def test_str(self):
		yields = Yields(10.0, 5.0, 2.0)

		expected_str = '10.0 Food, 5.0 Production, 2.0 Gold'
		self.assertEqual(str(yields), expected_str)


class TestYieldList(unittest.TestCase):
	def setUp(self):
		translation(get_language()).gettext = mock_gettext

	def test_constructor(self):
		yieldList = YieldList()

		actual = list(yieldList.values())
		expected = [0, 0, 0, 0, 0, 0]  # Assuming the order is food, production, gold, science, culture, faith
		self.assertListEqual(actual, expected)

		actual = list(yieldList.keys())
		expected = [
			YieldType.food,
			YieldType.production,
			YieldType.gold,
			YieldType.science,
			YieldType.culture,
			YieldType.faith
		]
		self.assertListEqual(actual, expected)

	def test_addition(self):
		yieldList1 = YieldList()
		yieldList1[YieldType.food] = 10
		yieldList1[YieldType.production] = 5

		yieldList2 = YieldList()
		yieldList2[YieldType.food] = 3
		yieldList2[YieldType.gold] = 7

		yieldList1 += yieldList2

		self.assertEqual(yieldList1[YieldType.food], 13)
		self.assertEqual(yieldList1[YieldType.production], 5)
		self.assertEqual(yieldList1[YieldType.gold], 7)

	def test_value(self):
		yieldList = YieldList()
		yieldList[YieldType.food] = 10
		yieldList[YieldType.production] = 5

		self.assertEqual(yieldList[YieldType.food], 10)
		self.assertEqual(yieldList[YieldType.production], 5)
		self.assertEqual(yieldList[YieldType.gold], 0)

	def test_str(self):
		yieldList = YieldList()
		yieldList[YieldType.food] = 10
		yieldList[YieldType.production] = 5
		yieldList[YieldType.gold] = 7

		expected_str = '10 Food, 5 Production, 7 Gold'
		self.assertEqual(str(yieldList), expected_str)


if __name__ == '__main__':
	unittest.main()
