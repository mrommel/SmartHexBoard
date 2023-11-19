from smarthexboard.smarthexboardlib.game.civilizations import LeaderAbility
from smarthexboard.smarthexboardlib.map.types import FeatureType, YieldType


class PlayerTraits:
	def __init__(self, player):
		self.player = player

	def cityStateFriendshipModifier(self) -> int:
		return 0

	def cityStateBonusModifier(self) -> int:
		return 0

	def cityStateCombatModifier(self) -> int:
		if self.player.leader.ability() == LeaderAbility.holyRomanEmperor:
			# Additional Military policy slot. +7 {{StrengthIcon6}} Combat Strength when attacking city-states.
			return 7

		return 0

	def isNoAnnexing(self) -> bool:
		return False

	def unimprovedFeatureYieldChange(self, featureValue: FeatureType, yieldType: YieldType) -> int:
		return 0

	def luxuryHappinessRetention(self) -> int:
		return 0
