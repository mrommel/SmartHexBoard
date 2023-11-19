from smarthexboard.smarthexboardlib.core.base import ExtendedEnum


class MinorPlayerPersonalityType(ExtendedEnum):
	friendly = 'friendly'  # MINOR_CIV_PERSONALITY_FRIENDLY
	neutral = 'neutral'  # MINOR_CIV_PERSONALITY_NEUTRAL
	hostile = 'hostile'  # MINOR_CIV_PERSONALITY_HOSTILE
	irrational = 'irrational'  # MINOR_CIV_PERSONALITY_IRRATIONAL


class InfluenceLevelType(ExtendedEnum):
	none = -1, 'none'  # NO_INFLUENCE_LEVEL = -1,

	unknown = 0, 'unknown'  # INFLUENCE_LEVEL_UNKNOWN,
	exotic = 1, 'exotic'  # INFLUENCE_LEVEL_EXOTIC,
	familiar = 2, 'familiar'  # INFLUENCE_LEVEL_FAMILIAR,
	popular = 3, 'popular'  # INFLUENCE_LEVEL_POPULAR,
	influential = 4, 'influential'  # INFLUENCE_LEVEL_INFLUENTIAL,
	dominant = 5, 'dominant'  # INFLUENCE_LEVEL_DOMINANT
