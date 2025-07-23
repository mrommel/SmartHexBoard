import os

import django
from django.test import TestCase

from smarthexboard.smarthexboardlib.game.civilizations import LeaderType
from smarthexboard.smarthexboardlib.game.players import Player
from smarthexboard.smarthexboardlib.game.promotions import UnitPromotions, UnitPromotionType
from smarthexboard.smarthexboardlib.game.unitTypes import UnitType
from smarthexboard.smarthexboardlib.game.units import Unit
from smarthexboard.smarthexboardlib.map.base import HexPoint

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SmartHexBoard.settings')
django.setup()


class TestUnitPromotions(TestCase):
	def test_possiblePromotions_melee(self):
		# GIVEN
		playerTrajan = Player(leader=LeaderType.trajan, cityState=None, human=False)
		playerTrajan.initialize()
		warrior = Unit(HexPoint(5, 5), UnitType.warrior, playerTrajan)
		promotions = UnitPromotions(warrior)

		# WHEN
		initialPromotions = promotions.possiblePromotions()

		promotions.earnPromotion(UnitPromotionType.battlecry)
		promotions.earnPromotion(UnitPromotionType.tortoise)
		secondPromotions = promotions.possiblePromotions()

		# THEN
		self.assertEqual(initialPromotions, [UnitPromotionType.embarkation, UnitPromotionType.healthBoostMelee,
		                                     UnitPromotionType.battlecry, UnitPromotionType.tortoise])
		self.assertEqual(secondPromotions, [UnitPromotionType.embarkation, UnitPromotionType.healthBoostMelee,
		                                    UnitPromotionType.commando, UnitPromotionType.amphibious,
		                                    UnitPromotionType.zweihander])

	def test_warrior_promotion(self):
		# GIVEN
		playerTrajan = Player(leader=LeaderType.trajan, cityState=None, human=False)
		playerTrajan.initialize()

		warrior = Unit(HexPoint(5, 5), UnitType.warrior, playerTrajan)
		# promotions = UnitPromotions(warrior)

		# WHEN
		battlecryValue = warrior._promotionValue(UnitPromotionType.battlecry)

		# THEN
		self.assertEqual(36, battlecryValue)
