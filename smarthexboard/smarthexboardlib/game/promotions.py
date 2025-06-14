from typing import Optional, List

from smarthexboard.smarthexboardlib.core.base import ExtendedEnum, contains, InvalidEnumError
from smarthexboard.smarthexboardlib.game.flavors import Flavor, FlavorType
from smarthexboard.smarthexboardlib.game.unitTypes import UnitClassType
from smarthexboard.smarthexboardlib.map.types import FeatureType, UnitDomainType


class PromotionCombatModifierDirection(ExtendedEnum):
	attack = 'attack'
	defend = 'defend'
	both = 'both'


class PromotionCombatModifierData:
	def __init__(self, amount: int, unitClasses: List[UnitClassType], combatDirection: PromotionCombatModifierDirection,
	             damagedOnly: bool = False, fortifiedOnly: bool = False, roughOnly: bool = False):
		self.amount = amount
		self.unitClasses = unitClasses
		self.combatDirection = combatDirection
		self.damagedOnly = damagedOnly
		self.fortifiedOnly = fortifiedOnly
		self.roughOnly = roughOnly


def unitClassesOf(domain) -> List[UnitClassType]:
	if isinstance(domain, UnitDomainType):
		unitClasses = []
		for it in list(UnitClassType):
			if it.domain() == domain:
				unitClasses.append(it)

		return unitClasses
	elif isinstance(domain, list):
		unitClasses = []
		for it in list(UnitClassType):
			if it.domain() in domain:
				unitClasses.append(it)

		return unitClasses

	raise InvalidEnumError(domain)


class UnitPromotionType:
	pass


class UnitPromotionTypeData:
	"""
	https://civilization.fandom.com/wiki/Promotions_(Civ6)
	https://github.com/LoneGazebo/Community-Patch-DLL/blob/b33ee4a04e91d27356af0bcc421de1b7899ac073/(2)%20Vox%20Populi/Balance%20Changes/Units/PromotionChanges.xml
	"""

	def __init__(self, name: str, effect: str, tier: int, unitClass: UnitClassType, requiredOr: List[UnitPromotionType],
	             consumable: bool, enemyRoute: bool = False, ignoreZoneOfControl: bool = False,
	             combatModifier: Optional[PromotionCombatModifierData] = None,
	             openAttack: int = 0, openDefense: int = 0, roughAttack: int = 0, roughDefense: int = 0,
	             openRangedAttackModifier: int = 0, movesChange: int = 0, isCanMoveAfterAttacking: bool = False,
	             extraAttacks: int = 0, rangeChange: int = 0, defenseModifier: int = 0, noDefensive: bool = False,
	             flavors: List[Flavor] = []):
		self.name = name
		self.effect = effect
		self.tier = tier
		self.unitClass = unitClass
		self.requiredOr = requiredOr
		self.consumable = consumable
		self.enemyRoute = enemyRoute
		self.ignoreZoneOfControl = ignoreZoneOfControl
		self.combatModifier = combatModifier
		self.openAttack: int = openAttack
		self.openDefense: int = openDefense
		self.roughAttack: int = roughAttack
		self.roughDefense: int = roughDefense
		self.openRangedAttackModifier: int = openRangedAttackModifier
		self.movesChange: int = movesChange
		self.isCanMoveAfterAttacking: bool = isCanMoveAfterAttacking
		self.extraAttacks: int = extraAttacks
		self.rangeChange: int = rangeChange
		self.defenseModifier: int = defenseModifier
		self.noDefensive: bool = noDefensive
		self.flavors = flavors


class CombatModifier:
	def __init__(self, value: int, text: str):
		self.value = value
		self.text = text

	def __repr__(self):
		return f'CombatModifier({self.value}, {self.text})'

	def __eq__(self, other):
		if isinstance(other, CombatModifier):
			return self.value == other.value and self.text == other.text
		else:
			return False


class UnitPromotionType(ExtendedEnum):
	embarkation = 'embarkation'

	# fallback
	healthBoostRecon = 'healthBoostRecon'  # 50 % boost
	healthBoostMelee = 'healthBoostMelee'  # 50 % boost

	# recon
	ranger = 'ranger'  # Faster Movement in Woods and Jungle terrain.
	alpine = 'alpine'  # Faster Movement on Hill terrain.
	sentry = 'sentry'  # Can see through Woods and Jungle.
	guerrilla = 'guerrilla'  # Can move after attacking.
	spyglass = 'spyglass'  # +1 sight range.
	ambush = 'ambush'  # +20 Combat Strength in all situations.
	camouflage = 'camouflage'  # Only adjacent enemy units can reveal this unit.

	# melee
	battlecry = 'battlecry'  # +7 Combat Strength vs. melee and ranged units.
	tortoise = 'tortoise'  # +10 Combat Strength when defending against ranged attacks.
	commando = 'commando'  # Can scale Cliff walls. + 1 Movement.
	amphibious = 'amphibious'  # No Combat Strength and Movement penalty when attacking from Sea or over a River.
	zweihander = 'zweihander'  # +7 Combat Strength vs.anti - cavalry units.
	urbanWarfare = 'urbanWarfare'  # +10 Combat Strength when fighting in a district.
	eliteGuard = 'eliteGuard'  # +1 additional attack per turn if Movement allows. Can move after attacking.

	# ranged
	volley = 'volley'  # +5 Ranged Strength vs. land units.
	garrison = 'garrison'  # +10 Combat Strength when occupying a district or Fort.
	arrowStorm = 'arrowStorm'  # +7 Ranged Strength vs. land and naval units.
	incendiaries = 'incendiaries'  # +7 Ranged Strength vs. district defenses.
	suppression = 'suppression'  # Exercise zone of control.
	emplacement = 'emplacement'  # +10 Combat Strength when defending vs. city attacks.
	expertMarksman = 'expertMarksman'  # +1 additional attack per turn if unit has not moved.

	# antiCavalry
	echelon = 'echelon'
	thrust = 'thrust'
	square = 'square'
	schiltron = 'schiltron'
	redeploy = 'redeploy'
	chokePoints = 'chokePoints'
	holdTheLine = 'holdTheLine'

	# lightCavalry
	caparison = 'caparison'
	coursers = 'coursers'
	depredation = 'depredation'
	doubleEnvelopment = 'doubleEnvelopment'
	spikingTheGuns = 'spikingTheGuns'
	pursuit = 'pursuit'
	escortMobility = 'escortMobility'

	# heavyCavalry
	charge = 'charge'
	barding = 'barding'
	marauding = 'marauding'
	rout = 'rout'
	armorPiercing = 'armorPiercing'
	reactiveArmor = 'reactiveArmor'
	breakthrough = 'breakthrough'

	# siege
	grapeShot = 'grapeShot'
	crewWeapons = 'crewWeapons'
	shrapnel = 'shrapnel'
	shells = 'shells'
	advancedRangefinding = 'shells'
	expertCrew = 'expertCrew'
	forwardObservers = 'forwardObservers'

	# navalMelee
	helmsman = 'helmsman'
	embolon = 'embolon'
	rutter = 'rutter'
	reinforcedHull = 'reinforcedHull'
	convoy = 'convoy'
	auxiliaryShips = 'auxiliaryShips'
	creepingAttack = 'creepingAttack'

	# navalRanged
	lineOfBattle = 'lineOfBattle'
	bombardment = 'bombardment'
	preparatoryFire = 'preparatoryFire'
	rollingBarrage = 'rollingBarrage'
	supplyFleet = 'supplyFleet'
	proximityFuses = 'proximityFuses'
	coincidenceRangefinding = 'coincidenceRangefinding'

	# navalRaider
	# navalCarrier

	# airFighter
	# airBomber

	# support

	def name(self) -> str:
		return self._data().name

	def effect(self) -> str:
		return self._data().effect

	def tier(self) -> int:
		return self._data().tier

	def unitClass(self) -> UnitClassType:
		return self._data().unitClass

	def requiredOr(self) -> List[UnitPromotionType]:
		return self._data().requiredOr

	def consumable(self) -> bool:
		return self._data().consumable

	def isEnemyRoute(self) -> bool:
		return self._data().enemyRoute

	def ignoreZoneOfControl(self) -> bool:
		return self._data().ignoreZoneOfControl

	def isInstantHeal(self) -> bool:
		return True

	def attackStrengthModifierAgainst(self, defender) -> Optional[CombatModifier]:
		combatModifier = self._data().combatModifier

		if combatModifier is None:
			return None

		if combatModifier.combatDirection == PromotionCombatModifierDirection.defend:
			return None

		if combatModifier.damagedOnly and defender.damage() == 0:
			return None

		if combatModifier.fortifiedOnly and not defender.isFortified():
			return None

		if contains(lambda unitClass: unitClass == defender.unitClassType(), combatModifier.unitClasses):
			return CombatModifier(combatModifier.amount, self.name())

		return None

	def defenderStrengthModifierAgainst(self, attacker) -> Optional[CombatModifier]:
		combatModifier = self._data().combatModifier

		if combatModifier is None:
			return None

		if combatModifier.combatDirection == PromotionCombatModifierDirection.attack:
			return None

		if combatModifier.damagedOnly and attacker.damage() == 0:
			return None

		if contains(lambda unitClass: unitClass == attacker.unitClassType(), combatModifier.unitClasses):
			return CombatModifier(combatModifier.amount, self.name())

		return None

	def defenderStrengthModifierOn(self, tile) -> Optional[CombatModifier]:
		combatModifier = self._data().combatModifier

		if combatModifier is None:
			return None

		if combatModifier.combatDirection == PromotionCombatModifierDirection.attack:
			return None

		tileIsRough = tile.hasFeature(FeatureType.forest) or tile.hasFeature(FeatureType.rainforest) or \
		              tile.isHills() or tile.hasFeature(FeatureType.marsh)

		if combatModifier.roughOnly and not tileIsRough:
			return None

		return CombatModifier(combatModifier.amount, self.name())

	def openAttackPercent(self) -> int:
		"""Accessor: Bonus open terrain attack percent"""
		return self._data().openAttack

	def openDefensePercent(self) -> int:
		"""Accessor: Bonus open terrain defense percent"""
		return self._data().openDefense

	def roughAttackPercent(self) -> int:
		return self._data().roughAttack

	def roughDefensePercent(self) -> int:
		return self._data().roughDefense

	def openRangedAttackModifier(self) -> int:
		return self._data().openRangedAttackModifier

	def movesChange(self) -> int:
		return self._data().movesChange

	def isCanMoveAfterAttacking(self) -> bool:
		return self._data().isCanMoveAfterAttacking

	def extraAttacks(self) -> int:
		return self._data().extraAttacks

	def rangeChange(self) -> int:
		return self._data().rangeChange

	def defenseModifier(self) -> int:
		return self._data().defenseModifier

	def noDefensive(self) -> bool:
		return self._data().noDefensive

	def flavorValue(self, flavorType: FlavorType) -> int:
		flavorOfCivic = next((flavor for flavor in self._data().flavors if flavor.flavorType == flavorType), None)

		if flavorOfCivic is not None:
			return flavorOfCivic.value

		return 0

	def _data(self) -> UnitPromotionTypeData:
		if self == UnitPromotionType.embarkation:
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_EMBARKATION_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_EMBARKATION_EFFECT",
				tier=0,
				unitClass=UnitClassType.melee,
				requiredOr=[],
				consumable=False,
				flavors=[
					Flavor(FlavorType.navalGrowth, value=2)
				]
			)

		# ---------------------
		# general

		elif self == UnitPromotionType.healthBoostRecon:
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_HEALTH_BOOST_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_HEALTH_BOOST_EFFECT",
				tier=0,
				unitClass=UnitClassType.recon,
				requiredOr=[],
				consumable=True,
				flavors=[
					Flavor(FlavorType.amenities, value=2)
				]
			)
		elif self == UnitPromotionType.healthBoostMelee:
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_HEALTH_BOOST_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_HEALTH_BOOST_EFFECT",
				tier=0,
				unitClass=UnitClassType.melee,
				requiredOr=[],
				consumable=True,
				flavors=[
					Flavor(FlavorType.amenities, value=2)
				]
			)

		# ---------------------
		# recon

		elif self == UnitPromotionType.ranger:
			# https://civilization.fandom.com/wiki/Ranger_(promotion)_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_RANGER_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_RANGER_EFFECT",
				tier=1,
				unitClass=UnitClassType.recon,
				requiredOr=[],
				consumable=False,
				flavors=[
					Flavor(FlavorType.recon, value=2),
					Flavor(FlavorType.mobile, value=2)
				]
			)
		elif self == UnitPromotionType.alpine:
			# https://civilization.fandom.com/wiki/Alpine_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_ALPINE_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_ALPINE_EFFECT",
				tier=1,
				unitClass=UnitClassType.recon,
				requiredOr=[],
				consumable=False,
				flavors=[
					Flavor(FlavorType.recon, value=1),
					Flavor(FlavorType.mobile, value=2)
				]
			)
		elif self == UnitPromotionType.sentry:
			# https://civilization.fandom.com/wiki/Sentry_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_SENTRY_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_SENTRY_EFFECT",
				tier=2,
				unitClass=UnitClassType.recon,
				requiredOr=[UnitPromotionType.ranger, UnitPromotionType.alpine],
				consumable=False,
				flavors=[
					Flavor(FlavorType.recon, value=2)
				]
			)
		elif self == UnitPromotionType.guerrilla:
			# https://civilization.fandom.com/wiki/Guerrilla_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_GUERRILLA_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_GUERRILLA_EFFECT",
				tier=2,
				unitClass=UnitClassType.recon,
				requiredOr=[UnitPromotionType.ranger, UnitPromotionType.alpine],
				consumable=False,
				flavors=[
					Flavor(FlavorType.offense, value=2),
					Flavor(FlavorType.mobile, value=2)
				]
			)
		elif self == UnitPromotionType.spyglass:
			#
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_SPYGLASS_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_SPYGLASS_EFFECT",
				tier=3,
				unitClass=UnitClassType.recon,
				requiredOr=[UnitPromotionType.sentry],
				consumable=False,
				flavors=[
					Flavor(FlavorType.recon, value=2),
					Flavor(FlavorType.mobile, value=1)
				]
			)
		elif self == UnitPromotionType.ambush:
			# https://civilization.fandom.com/wiki/Ambush_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_AMBUSH_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_AMBUSH_EFFECT",
				tier=3,
				unitClass=UnitClassType.recon,
				requiredOr=[UnitPromotionType.guerrilla],
				consumable=False,
				combatModifier=PromotionCombatModifierData(
					amount=20,
					unitClasses=UnitClassType.combat(),
				    combatDirection=PromotionCombatModifierDirection.both
				),
				flavors=[
					Flavor(FlavorType.offense, value=2)
				]
			)
		elif self == UnitPromotionType.camouflage:
			# https://civilization.fandom.com/wiki/Camouflage_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_CAMOUFLAGE_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_CAMOUFLAGE_EFFECT",
				tier=4,
				unitClass=UnitClassType.recon,
				requiredOr=[UnitPromotionType.spyglass, UnitPromotionType.ambush],
				consumable=False,
				flavors=[
					Flavor(FlavorType.recon, value=2)
				]
			)

		# ---------------------
		# melee

		elif self == UnitPromotionType.battlecry:
			# https://civilization.fandom.com/wiki/Battlecry_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_BATTLECRY_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_BATTLECRY_EFFECT",
				tier=1,
				unitClass=UnitClassType.melee,
				requiredOr=[],
				consumable=False,
				combatModifier=PromotionCombatModifierData(
					amount=7,
					unitClasses=[UnitClassType.melee, UnitClassType.ranged],
					combatDirection=PromotionCombatModifierDirection.both
				),
				openAttack=7,
				defenseModifier=7,
				flavors=[
					Flavor(FlavorType.offense, value=2),
					Flavor(FlavorType.ranged, value=1)
				]
			)

		elif self == UnitPromotionType.tortoise:
			# https://civilization.fandom.com/wiki/Tortoise_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_TORTOISE_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_TORTOISE_EFFECT",
				tier=1,
				unitClass=UnitClassType.melee,
				requiredOr=[],
				consumable=False,
				combatModifier=PromotionCombatModifierData(
					amount=10,
					unitClasses=[UnitClassType.ranged],
					combatDirection=PromotionCombatModifierDirection.defend
				),
				flavors=[
					Flavor(FlavorType.offense, value=3),
					Flavor(FlavorType.ranged, value=1)
				]
			)
		elif self == UnitPromotionType.commando:
			# https://civilization.fandom.com/wiki/Commando_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_COMMANDO_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_COMMANDO_EFFECT",
				tier=2,
				unitClass=UnitClassType.melee,
				requiredOr=[UnitPromotionType.battlecry, UnitPromotionType.amphibious],
				consumable=False,
				flavors=[
					Flavor(FlavorType.mobile, value=3)
				]
			)
		elif self == UnitPromotionType.amphibious:
			# https://civilization.fandom.com/wiki/Amphibious_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_AMPHIBIOUS_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_AMPHIBIOUS_EFFECT",
				tier=2,
				unitClass=UnitClassType.melee,
				requiredOr=[UnitPromotionType.tortoise, UnitPromotionType.commando],
				consumable=False,
				flavors=[
					Flavor(FlavorType.mobile, value=2),
					Flavor(FlavorType.naval, value=2)
				]
			)
		elif self == UnitPromotionType.zweihander:
			# https://civilization.fandom.com/wiki/Zweihander_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_ZWEIHANDER_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_ZWEIHANDER_EFFECT",
				tier=3,
				unitClass=UnitClassType.melee,
				requiredOr=[UnitPromotionType.tortoise, UnitPromotionType.amphibious],
				consumable=False,
				combatModifier=PromotionCombatModifierData(
					amount=7,
					unitClasses=[UnitClassType.antiCavalry],
					combatDirection=PromotionCombatModifierDirection.both
				),
				flavors=[
					Flavor(FlavorType.offense, value=3)
				]
			)
		elif self == UnitPromotionType.urbanWarfare:
			# https://civilization.fandom.com/wiki/Urban_Warfare_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_URBAN_WARFARE_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_URBAN_WARFARE_EFFECT",
				tier=3,
				unitClass=UnitClassType.melee,
				requiredOr=[UnitPromotionType.commando, UnitPromotionType.amphibious],
				consumable=False,
				flavors=[
					Flavor(FlavorType.offense, value=2),
					Flavor(FlavorType.cityDefense, value=2)
				]
			)
		elif self == UnitPromotionType.eliteGuard:
			# https://civilization.fandom.com/wiki/Elite_Guard_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_ELITE_GUARD_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_ELITE_GUARD_EFFECT",
				tier=4,
				unitClass=UnitClassType.melee,
				requiredOr=[UnitPromotionType.zweihander, UnitPromotionType.urbanWarfare],
				consumable=False,
				flavors=[
					Flavor(FlavorType.mobile, value=3),
					Flavor(FlavorType.offense, value=2)
				]
			)

		# ---------------------
		# ranged

		elif self == UnitPromotionType.volley:
			# https://civilization.fandom.com/wiki/Volley_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_VOLLEY_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_VOLLEY_EFFECT",
				tier=1,
				unitClass=UnitClassType.ranged,
				requiredOr=[],
				consumable=False,
				combatModifier=PromotionCombatModifierData(
					amount=5,
					unitClasses=unitClassesOf(UnitDomainType.land),
					combatDirection=PromotionCombatModifierDirection.attack
				),  # only ranged attack!
				flavors=[
					Flavor(FlavorType.offense, value=3)
				]
			)
		elif self == UnitPromotionType.garrison:
			# https://civilization.fandom.com/wiki/Garrison_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_GARRISON_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_GARRISON_EFFECT",
				tier=1,
				unitClass=UnitClassType.ranged,
				requiredOr=[],
				consumable=False,
				flavors=[
					Flavor(FlavorType.cityDefense, value=4)
				]
			)
		elif self == UnitPromotionType.arrowStorm:
			# https://civilization.fandom.com/wiki/Arrow_Storm_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_ARROW_STORM_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_ARROW_STORM_EFFECT",
				tier=2,
				unitClass=UnitClassType.ranged,
				requiredOr=[UnitPromotionType.volley],
				consumable=False,
				combatModifier=PromotionCombatModifierData(
					amount=7,
					unitClasses=unitClassesOf(UnitDomainType.land) + unitClassesOf(UnitDomainType.sea),
					combatDirection=PromotionCombatModifierDirection.attack
				),  # only ranged attack!
				flavors=[
					Flavor(FlavorType.offense, value=3),
					Flavor(FlavorType.naval, value=2)
				]
			)
		elif self == UnitPromotionType.incendiaries:
			# https://civilization.fandom.com/wiki/Incendiaries_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_INCENDIARIES_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_INCENDIARIES_EFFECT",
				tier=2,
				unitClass=UnitClassType.ranged,
				requiredOr=[UnitPromotionType.garrison],
				consumable=False,
				flavors=[
					Flavor(FlavorType.offense, value=4)
				]
			)
		elif self == UnitPromotionType.suppression:
			# https://civilization.fandom.com/wiki/Suppression_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_SUPPRESSION_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_SUPPRESSION_EFFECT",
				tier=3,
				unitClass=UnitClassType.ranged,
				requiredOr=[UnitPromotionType.arrowStorm, UnitPromotionType.incendiaries],
				consumable=False,
				flavors=[
					Flavor(FlavorType.defense, value=3)
				]
			)
		elif self == UnitPromotionType.emplacement:
			# https://civilization.fandom.com/wiki/Emplacement_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_EMPLACEMENT_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_EMPLACEMENT_EFFECT",
				tier=3,
				unitClass=UnitClassType.ranged,
				requiredOr=[UnitPromotionType.arrowStorm, UnitPromotionType.incendiaries],
				consumable=False,
				flavors=[
					Flavor(FlavorType.cityDefense, value=3),
					Flavor(FlavorType.defense, value=2)
				]
			)
		elif self == UnitPromotionType.expertMarksman:
			# https://civilization.fandom.com/wiki/Expert_Marksman_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_EXPERT_MARKSMAN_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_EXPERT_MARKSMAN_EFFECT",
				tier=4,
				unitClass=UnitClassType.ranged,
				requiredOr=[UnitPromotionType.suppression, UnitPromotionType.emplacement],
				consumable=False,
				flavors=[
					Flavor(FlavorType.offense, value=3)
				]
			)

		# ---------------------
		# antiCavalry

		elif self == UnitPromotionType.echelon:
			# https://civilization.fandom.com/wiki/Echelon_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_ECHELON_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_ECHELON_EFFECT",
				tier=1,
				unitClass=UnitClassType.antiCavalry,
				requiredOr=[],
				consumable=False,
				combatModifier=PromotionCombatModifierData(
					amount=5,
					unitClasses=[UnitClassType.lightCavalry, UnitClassType.heavyCavalry],
					combatDirection=PromotionCombatModifierDirection.both
				),
				flavors=[
					Flavor(FlavorType.offense, value=3)
				]
			)
		elif self == UnitPromotionType.thrust:
			# https://civilization.fandom.com/wiki/Thrust_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_THRUST_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_THRUST_EFFECT",
				tier=1,
				unitClass=UnitClassType.antiCavalry,
				requiredOr=[],
				consumable=False,
				combatModifier=PromotionCombatModifierData(
					amount=10,
					unitClasses=[UnitClassType.melee],
					combatDirection=PromotionCombatModifierDirection.both
				),
				flavors=[
					Flavor(FlavorType.offense, value=4)
				]
			)
		elif self == UnitPromotionType.square:
			# https://civilization.fandom.com/wiki/Square_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_SQUARE_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_SQUARE_EFFECT",
				tier=2,
				unitClass=UnitClassType.antiCavalry,
				requiredOr=[UnitPromotionType.echelon],
				consumable=False,
				flavors=[
					Flavor(FlavorType.defense, value=3),
					Flavor(FlavorType.militaryTraining, value=1)
				]
			)
		elif self == UnitPromotionType.schiltron:
			# https://civilization.fandom.com/wiki/Schiltron_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_SCHILTRON_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_SCHILTRON_EFFECT",
				tier=2,
				unitClass=UnitClassType.antiCavalry,
				requiredOr=[UnitPromotionType.thrust],
				consumable=False,
				combatModifier=PromotionCombatModifierData(
					amount=10,
					unitClasses=[UnitClassType.melee],
					combatDirection=PromotionCombatModifierDirection.defend
				),
				flavors=[
					Flavor(FlavorType.offense, value=4)
				]
			)
		elif self == UnitPromotionType.redeploy:
			# Redeploy
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_REDEPLOY_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_REDEPLOY_EFFECT",
				tier=3,
				unitClass=UnitClassType.antiCavalry,
				requiredOr=[UnitPromotionType.square, UnitPromotionType.schiltron],
				consumable=False,
				flavors=[
					Flavor(FlavorType.mobile, value=3)
				]
			)
		elif self == UnitPromotionType.chokePoints:
			# https://civilization.fandom.com/wiki/Choke_Points_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_CHOKE_POINTS_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_CHOKE_POINTS_EFFECT",
				tier=3,
				unitClass=UnitClassType.antiCavalry,
				requiredOr=[UnitPromotionType.square, UnitPromotionType.schiltron],
				consumable=False,
				combatModifier=PromotionCombatModifierData(
					amount=7,
					unitClasses=UnitClassType.combat(),
					combatDirection=PromotionCombatModifierDirection.defend,
					roughOnly=True),
				flavors=[
					Flavor(FlavorType.defense, value=4)
				]
			)
		elif self == UnitPromotionType.holdTheLine:
			# https://civilization.fandom.com/wiki/Hold_the_Line_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_HOLD_THE_LINE_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_HOLD_THE_LINE_EFFECT",
				tier=4,
				unitClass=UnitClassType.antiCavalry,
				requiredOr=[UnitPromotionType.redeploy, UnitPromotionType.chokePoints],
				consumable=False,
				flavors=[
					Flavor(FlavorType.militaryTraining, value=2),
					Flavor(FlavorType.defense, value=3)
				]
			)

		# ---------------------
		# lightCavalry

		elif self == UnitPromotionType.caparison:
			# https://civilization.fandom.com/wiki/Caparison_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_CAPARISON_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_CAPARISON_EFFECT",
				tier=1,
				unitClass=UnitClassType.lightCavalry,
				requiredOr=[],
				consumable=False,
				combatModifier=PromotionCombatModifierData(
					amount=5,
					unitClasses=[UnitClassType.antiCavalry],
					combatDirection=PromotionCombatModifierDirection.both
				),
				flavors=[
					Flavor(FlavorType.offense, value=4)
				]
			)
		elif self == UnitPromotionType.coursers:
			# https://civilization.fandom.com/wiki/Coursers_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_COURSERS_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_COURSERS_EFFECT",
				tier=1,
				unitClass=UnitClassType.lightCavalry,
				requiredOr=[],
				consumable=False,
				combatModifier=PromotionCombatModifierData(
					amount=5,
					unitClasses=[UnitClassType.ranged, UnitClassType.siege],
					combatDirection=PromotionCombatModifierDirection.attack
				),
				flavors=[
					Flavor(FlavorType.offense, value=2)
				]
			)
		elif self == UnitPromotionType.depredation:
			# https://civilization.fandom.com/wiki/Depredation_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_DEPREDATION_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_DEPREDATION_EFFECT",
				tier=2,
				unitClass=UnitClassType.lightCavalry,
				requiredOr=[UnitPromotionType.caparison],
				consumable=False,
				flavors=[
					Flavor(FlavorType.offense, value=3)
				]
			)
		elif self == UnitPromotionType.doubleEnvelopment:
			# https://civilization.fandom.com/wiki/Double_Envelopment_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_DOUBLE_ENVELOPMENT_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_DOUBLE_ENVELOPMENT_EFFECT",
				tier=2,
				unitClass=UnitClassType.lightCavalry,
				requiredOr=[UnitPromotionType.coursers],
				consumable=False,
				flavors=[
					Flavor(FlavorType.militaryTraining, value=3),
					Flavor(FlavorType.offense, value=2)
				]
			)
		elif self == UnitPromotionType.spikingTheGuns:
			# https://civilization.fandom.com/wiki/Spiking_the_Guns_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_SPIKING_THE_GUNS_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_SPIKING_THE_GUNS_EFFECT",
				tier=3,
				unitClass=UnitClassType.lightCavalry,
				requiredOr=[UnitPromotionType.depredation, UnitPromotionType.doubleEnvelopment],
				consumable=False,
				combatModifier=PromotionCombatModifierData(
					amount=7,
					unitClasses=[UnitClassType.siege],
					combatDirection=PromotionCombatModifierDirection.both
				),
				flavors=[
					Flavor(FlavorType.offense, value=2),
					Flavor(FlavorType.defense, value=2)
				]
			)
		elif self == UnitPromotionType.pursuit:
			# https://civilization.fandom.com/wiki/Pursuit_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_PURSUIT_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_PURSUIT_EFFECT",
				tier=3,
				unitClass=UnitClassType.lightCavalry,
				requiredOr=[UnitPromotionType.depredation, UnitPromotionType.doubleEnvelopment],
				consumable=False,
				flavors=[
					Flavor(FlavorType.mobile, value=3)
				]
			)
		elif self == UnitPromotionType.escortMobility:
			# https://civilization.fandom.com/wiki/Escort_Mobility_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_ESCORT_MOBILITY_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_ESCORT_MOBILITY_EFFECT",
				tier=4,
				unitClass=UnitClassType.lightCavalry,
				requiredOr=[UnitPromotionType.spikingTheGuns, UnitPromotionType.pursuit],
				consumable=False,
				flavors=[
					Flavor(FlavorType.mobile, value=3)
				]
			)

		# ---------------------
		# heavyCavalry

		elif self == UnitPromotionType.charge:
			# https://civilization.fandom.com/wiki/Charge_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_CHARGE_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_CHARGE_EFFECT",
				tier=1,
				unitClass=UnitClassType.heavyCavalry,
				requiredOr=[],
				consumable=False,
				combatModifier=PromotionCombatModifierData(
					amount=10,
					unitClasses=UnitClassType.combat(),
					combatDirection=PromotionCombatModifierDirection.attack,
					fortifiedOnly=True
				),
				flavors=[
					Flavor(FlavorType.offense, value=4)
				]
			)
		elif self == UnitPromotionType.barding:
			# https://civilization.fandom.com/wiki/Barding_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_BARDING_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_BARDING_EFFECT",
				tier=1,
				unitClass=UnitClassType.heavyCavalry,
				requiredOr=[],
				consumable=False,
				combatModifier=PromotionCombatModifierData(
					amount=7,
					unitClasses=[UnitClassType.ranged],
					combatDirection=PromotionCombatModifierDirection.defend
				),
				flavors=[
					Flavor(FlavorType.defense, value=3)
				]
			)
		elif self == UnitPromotionType.marauding:
			# https://civilization.fandom.com/wiki/Marauding_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_MARAUDING_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_MARAUDING_EFFECT",
				tier=2,
				unitClass=UnitClassType.heavyCavalry,
				requiredOr=[UnitPromotionType.charge, UnitPromotionType.rout],
				consumable=False,
				flavors=[
					Flavor(FlavorType.offense, value=3)
				]
			)
		elif self == UnitPromotionType.rout:
			# https://civilization.fandom.com/wiki/Rout_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_ROUT_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_ROUT_EFFECT",
				tier=2,
				unitClass=UnitClassType.heavyCavalry,
				requiredOr=[UnitPromotionType.barding, UnitPromotionType.marauding],
				consumable=False,
				combatModifier=PromotionCombatModifierData(
					amount=7,
					unitClasses=UnitClassType.combat(),
					combatDirection=PromotionCombatModifierDirection.both,
					damagedOnly=True
				),
				flavors=[
					Flavor(FlavorType.offense, value=4)
				]
			)
		elif self == UnitPromotionType.armorPiercing:
			# https://civilization.fandom.com/wiki/Armor_Piercing_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_ARMOR_PIERCING_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_ARMOR_PIERCING_EFFECT",
				tier=3,
				unitClass=UnitClassType.heavyCavalry,
				requiredOr=[UnitPromotionType.marauding, UnitPromotionType.rout],
				consumable=False,
				combatModifier=PromotionCombatModifierData(
					amount=7,
					unitClasses=[UnitClassType.heavyCavalry],
					combatDirection=PromotionCombatModifierDirection.both
				),
				flavors=[
					Flavor(FlavorType.offense, value=3)
				]
			)

		elif self == UnitPromotionType.reactiveArmor:
			# https://civilization.fandom.com/wiki/Reactive_Armor_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_REACTIVE_ARMOR_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_REACTIVE_ARMOR_EFFECT",
				tier=3,
				unitClass=UnitClassType.heavyCavalry,
				requiredOr=[UnitPromotionType.rout],
				consumable=False,
				combatModifier=PromotionCombatModifierData(
					amount=7,
					unitClasses=[UnitClassType.heavyCavalry, UnitClassType.antiCavalry],
					combatDirection=PromotionCombatModifierDirection.defend
				),
				flavors=[
					Flavor(FlavorType.defense, value=3)
				]
			)
		elif self == UnitPromotionType.breakthrough:
			# https://civilization.fandom.com/wiki/Breakthrough_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_BREAKTHROUGH_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_BREAKTHROUGH_EFFECT",
				tier=4,
				unitClass=UnitClassType.heavyCavalry,
				requiredOr=[UnitPromotionType.armorPiercing, UnitPromotionType.reactiveArmor],
				consumable=False,
				flavors=[
					Flavor(FlavorType.mobile, value=2),
					Flavor(FlavorType.offense, value=2)
				]
			)

		# ---------------------
		# siege

		elif self == UnitPromotionType.grapeShot:
			# https://civilization.fandom.com/wiki/Grape_Shot_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_GRAPE_SHOT_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_GRAPE_SHOT_EFFECT",
				tier=1,
				unitClass=UnitClassType.siege,
				requiredOr=[],
				consumable=False,
				combatModifier=PromotionCombatModifierData(
					amount=7,
					unitClasses=unitClassesOf(UnitDomainType.land),
					combatDirection=PromotionCombatModifierDirection.both
				),
				flavors=[
					Flavor(FlavorType.ranged, value=2),
					Flavor(FlavorType.offense, value=2)
				]
			)
		elif self == UnitPromotionType.crewWeapons:
			# https://civilization.fandom.com/wiki/Crew_Weapons_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_CREW_WEAPONS_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_CREW_WEAPONS_EFFECT",
				tier=1,
				unitClass=UnitClassType.siege,
				requiredOr=[],
				consumable=False,
				combatModifier=PromotionCombatModifierData(
					amount=7,
					unitClasses=UnitClassType.combat(),
					combatDirection=PromotionCombatModifierDirection.defend
				),
				flavors=[
					Flavor(FlavorType.defense, value=4)
				]
			)
		elif self == UnitPromotionType.shrapnel:
			# https://civilization.fandom.com/wiki/Shrapnel_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_SHRAPNEL_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_SHRAPNEL_EFFECT",
				tier=2,
				unitClass=UnitClassType.siege,
				requiredOr=[UnitPromotionType.grapeShot],
				consumable=False,
				combatModifier=PromotionCombatModifierData(
					amount=10,
					unitClasses=unitClassesOf(UnitDomainType.land),
					combatDirection=PromotionCombatModifierDirection.both
				),
				flavors=[
					Flavor(FlavorType.ranged, value=2),
					Flavor(FlavorType.offense, value=3)
				]
			)
		elif self == UnitPromotionType.shells:
			# https://civilization.fandom.com/wiki/Shells_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_SHELLS_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_SHELLS_EFFECT",
				tier=2,
				unitClass=UnitClassType.siege,
				requiredOr=[UnitPromotionType.crewWeapons],
				consumable=False,
				flavors=[
					Flavor(FlavorType.offense, value=4)
				]
			)
		elif self == UnitPromotionType.advancedRangefinding:
			# https://civilization.fandom.com/wiki/Advanced_Rangefinding_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_ADVANCED_RANGEFINDING_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_ADVANCED_RANGEFINDING_EFFECT",
				tier=3,
				unitClass=UnitClassType.siege,
				requiredOr=[UnitPromotionType.shrapnel, UnitPromotionType.shells],
				consumable=False,
				combatModifier=PromotionCombatModifierData(
					amount=10,
					unitClasses=UnitDomainType.sea.unitClasses(),
					combatDirection=PromotionCombatModifierDirection.both
				),
				flavors=[
					Flavor(FlavorType.naval, value=3)
				]
			)
		elif self == UnitPromotionType.expertCrew:
			# https://civilization.fandom.com/wiki/Expert_Crew_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_EXPERT_CREW_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_EXPERT_CREW_EFFECT",
				tier=3,
				unitClass=UnitClassType.siege,
				requiredOr=[UnitPromotionType.shrapnel, UnitPromotionType.shells],
				consumable=False,
				flavors=[
					Flavor(FlavorType.mobile, value=2),
					Flavor(FlavorType.offense, value=2)
				]
			)
		elif self == UnitPromotionType.forwardObservers:
			# https://civilization.fandom.com/wiki/Forward_Observers_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_FORWARD_OBSERVERS_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_FORWARD_OBSERVERS_EFFECT",
				tier=4,
				unitClass=UnitClassType.siege,
				requiredOr=[UnitPromotionType.advancedRangefinding, UnitPromotionType.expertCrew],
				consumable=False,
				flavors=[
					Flavor(FlavorType.ranged, value=3),
					Flavor(FlavorType.offense, value=1)
				]
			)

		# ---------------------
		# navalMelee

		elif self == UnitPromotionType.helmsman:
			# https://civilization.fandom.com/wiki/Helmsman_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_HELMSMAN_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_HELMSMAN_EFFECT",
				tier=1,
				unitClass=UnitClassType.navalMelee,
				requiredOr=[],
				consumable=False,
				flavors=[
					Flavor(FlavorType.expansion, value=2),
					Flavor(FlavorType.mobile, value=3)
				]
			)
		elif self == UnitPromotionType.embolon:
			# https://civilization.fandom.com/wiki/Embolon_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_EMBOLON_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_EMBOLON_EFFECT",
				tier=1,
				unitClass=UnitClassType.navalMelee,
				requiredOr=[],
				consumable=False,
				combatModifier=PromotionCombatModifierData(
					amount=7,
					unitClasses=unitClassesOf(UnitDomainType.sea),
					combatDirection=PromotionCombatModifierDirection.both
				),
				flavors=[
					Flavor(FlavorType.offense, value=3)
				]
			)
		elif self == UnitPromotionType.rutter:
			# https://civilization.fandom.com/wiki/Rutter_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_RUTTER_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_RUTTER_EFFECT",
				tier=2,
				unitClass=UnitClassType.navalMelee,
				requiredOr=[UnitPromotionType.helmsman],
				consumable=False,
				flavors=[
					Flavor(FlavorType.expansion, value=2)
				]
			)
		elif self == UnitPromotionType.reinforcedHull:
			# https://civilization.fandom.com/wiki/Reinforced_Hull_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_REINFORCED_HULL_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_REINFORCED_HULL_EFFECT",
				tier=2,
				unitClass=UnitClassType.navalMelee,
				requiredOr=[UnitPromotionType.embolon],
				consumable=False,
				combatModifier=PromotionCombatModifierData(
					amount=10,
					unitClasses=[UnitClassType.ranged, UnitClassType.navalRanged],
					combatDirection=PromotionCombatModifierDirection.defend
				),
				flavors=[
					Flavor(FlavorType.defense, value=4)
				]
			)
		elif self == UnitPromotionType.convoy:
			# https://civilization.fandom.com/wiki/Convoy_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_CONVOY_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_CONVOY_EFFECT",
				tier=3,
				unitClass=UnitClassType.navalMelee,
				requiredOr=[UnitPromotionType.rutter, UnitPromotionType.reinforcedHull],
				consumable=False,
				flavors=[
					Flavor(FlavorType.offense, value=3)
				]
			)
		elif self == UnitPromotionType.auxiliaryShips:
			# https://civilization.fandom.com/wiki/Auxiliary_Ships_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_AUXILIARY_SHIPS_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_AUXILIARY_SHIPS_EFFECT",
				tier=3,
				unitClass=UnitClassType.navalMelee,
				requiredOr=[UnitPromotionType.rutter, UnitPromotionType.reinforcedHull],
				consumable=False,
				flavors=[
					Flavor(FlavorType.defense, value=3)
				]
			)
		elif self == UnitPromotionType.creepingAttack:
			# https://civilization.fandom.com/wiki/Creeping_Attack_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_CREEPING_ATTACK_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_CREEPING_ATTACK_EFFECT",
				tier=4,
				unitClass=UnitClassType.navalMelee,
				requiredOr=[UnitPromotionType.convoy, UnitPromotionType.auxiliaryShips],
				consumable=False,
				combatModifier=PromotionCombatModifierData(
					amount=14,
					unitClasses=[UnitClassType.navalRaider],
					combatDirection=PromotionCombatModifierDirection.both
				),
				flavors=[
					Flavor(FlavorType.offense, value=3)
				]
			)

		# ---------------------
		# navalRanged

		elif self == UnitPromotionType.lineOfBattle:
			# https://civilization.fandom.com/wiki/Line_of_Battle_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_LINE_OF_BATTLE_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_LINE_OF_BATTLE_EFFECT",
				tier=1,
				unitClass=UnitClassType.navalRanged,
				requiredOr=[],
				consumable=True,
				combatModifier=PromotionCombatModifierData(
					amount=7,
					unitClasses=unitClassesOf(UnitDomainType.sea),
					combatDirection=PromotionCombatModifierDirection.both
				),
				flavors=[
					Flavor(FlavorType.naval, value=3),
					Flavor(FlavorType.navalGrowth, value=1)
				]
			)
		elif self == UnitPromotionType.bombardment:
			# https://civilization.fandom.com/wiki/Bombardment_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_BOMBARDMENT_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_BOMBARDMENT_EFFECT",
				tier=1,
				unitClass=UnitClassType.navalRanged,
				requiredOr=[],
				consumable=True,
				flavors=[
					Flavor(FlavorType.naval, value=2),
					Flavor(FlavorType.defense, value=3)
				]
			)
		elif self == UnitPromotionType.preparatoryFire:
			# https://civilization.fandom.com/wiki/Preparatory_Fire_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_PREPARATORY_FIRE_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_PREPARATORY_FIRE_EFFECT",
				tier=2,
				unitClass=UnitClassType.navalRanged,
				requiredOr=[UnitPromotionType.lineOfBattle],
				consumable=True,
				combatModifier=PromotionCombatModifierData(
					amount=7,
					unitClasses=unitClassesOf(UnitDomainType.land),
					combatDirection=PromotionCombatModifierDirection.both
				),
				flavors=[
					Flavor(FlavorType.offense, value=3),
					Flavor(FlavorType.defense, value=1)
				]
			)
		elif self == UnitPromotionType.rollingBarrage:
			# https://civilization.fandom.com/wiki/Rolling_Barrage_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_ROLLING_BARRAGE_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_ROLLING_BARRAGE_EFFECT",
				tier=2,
				unitClass=UnitClassType.navalRanged,
				requiredOr=[UnitPromotionType.bombardment],
				consumable=True,
				flavors=[
					Flavor(FlavorType.offense, value=4)
				]
			)
		elif self == UnitPromotionType.supplyFleet:
			# https://civilization.fandom.com/wiki/Supply_Fleet_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_SUPPLY_FLEET_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_SUPPLY_FLEET_EFFECT",
				tier=3,
				unitClass=UnitClassType.navalRanged,
				requiredOr=[UnitPromotionType.preparatoryFire, UnitPromotionType.rollingBarrage],
				consumable=True,
				flavors=[
					Flavor(FlavorType.defense, value=3)
				]
			)
		elif self == UnitPromotionType.proximityFuses:
			# https://civilization.fandom.com/wiki/Proximity_Fuses_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_PROXIMITY_FUSES_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_PROXIMITY_FUSES_EFFECT",
				tier=3,
				unitClass=UnitClassType.navalRanged,
				requiredOr=[UnitPromotionType.preparatoryFire, UnitPromotionType.rollingBarrage],
				consumable=True,
				combatModifier=PromotionCombatModifierData(
					amount=7,
					unitClasses=unitClassesOf(UnitDomainType.air),
					combatDirection=PromotionCombatModifierDirection.defend
				),
				flavors=[
					Flavor(FlavorType.defense, value=3)
				]
			)
		elif self == UnitPromotionType.coincidenceRangefinding:
			# https://civilization.fandom.com/wiki/Coincidence_Rangefinding_(Civ6)
			return UnitPromotionTypeData(
				name="TXT_KEY_UNIT_PROMOTION_COINCIDENCE_RANGEFINDING_NAME",
				effect="TXT_KEY_UNIT_PROMOTION_COINCIDENCE_RANGEFINDING_EFFECT",
				tier=4,
				unitClass=UnitClassType.navalRanged,
				requiredOr=[UnitPromotionType.supplyFleet, UnitPromotionType.proximityFuses],
				consumable=True,
				flavors=[
					Flavor(FlavorType.ranged, value=3),
					Flavor(FlavorType.naval, value=2)
				]
			)

		raise InvalidEnumError(self)


class UnitPromotions:
	def __init__(self, unit):
		self.unit = unit
		self._promotions: List[UnitPromotionType] = []

	def hasPromotion(self, promotion: UnitPromotionType) -> bool:
		return promotion in self._promotions

	def gainedPromotions(self) -> List[UnitPromotionType]:
		return self._promotions

	def earnPromotion(self, promotion: UnitPromotionType) -> bool:
		if self.hasPromotion(promotion):
			return False

		if promotion not in self.possiblePromotions():
			return False

		self._promotions.append(promotion)

		return True

	def possiblePromotions(self) -> List[UnitPromotionType]:
		promotionList: List[UnitPromotionType] = []

		for promotion in list(UnitPromotionType):
			if not self.unit.isOfUnitClass(promotion.unitClass()):
				continue

			if self.hasPromotion(promotion):
				continue

			valid = False
			for requiredPromotion in promotion.requiredOr():
				if self.hasPromotion(requiredPromotion):
					valid = True

			if len(promotion.requiredOr()) == 0:
				valid = True

			if not valid:
				continue

			promotionList.append(promotion)

		return promotionList
