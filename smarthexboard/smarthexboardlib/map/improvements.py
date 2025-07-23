from typing import Optional

from smarthexboard.smarthexboardlib.game.civilizations import CivilizationType
from smarthexboard.smarthexboardlib.game.flavors import Flavor, FlavorType
from smarthexboard.smarthexboardlib.game.types import TechType, CivicType
from smarthexboard.smarthexboardlib.map.types import Yields, TerrainType, FeatureType, ResourceType
from smarthexboard.smarthexboardlib.core.base import ExtendedEnum, InvalidEnumError


class ImprovementTypeData:
	def __init__(self, name: str, effects: [str], requiredTech: Optional[TechType],
				 civilization: Optional[CivilizationType], canBePillaged: bool, defenseModifier: int,
				 flavors: [Flavor]):
		self.name = name
		self.effects = effects
		self.requiredTech = requiredTech
		self.civilization = civilization
		self.canBePillaged = canBePillaged
		self.defenseModifier = defenseModifier
		self.flavors = flavors


class ImprovementType:
	pass


class ImprovementType(ExtendedEnum):
	none = 'none'

	barbarianCamp = 'barbarianCamp'

	mine = 'mine'
	plantation = 'plantation'
	farm = 'farm'
	quarry = 'quarry'
	camp = 'camp'
	fishingBoats = 'fishingBoats'
	pasture = 'pasture'
	oilWell = 'oilWell'

	fort = 'fort'
	citadelle = 'citadelle'

	goodyHut = 'goodyHut'
	ruins = 'ruins'

	@staticmethod
	def fromName(improvementName: str) -> ImprovementType:
		if improvementName == 'ImprovementType.none' or improvementName == 'none':
			return ImprovementType.none
		elif improvementName == 'ImprovementType.barbarianCamp' or improvementName == 'barbarianCamp':
			return ImprovementType.barbarianCamp
		elif improvementName == 'ImprovementType.mine' or improvementName == 'mine':
			return ImprovementType.mine
		elif improvementName == 'ImprovementType.plantation' or improvementName == 'plantation':
			return ImprovementType.plantation
		elif improvementName == 'ImprovementType.farm' or improvementName == 'farm':
			return ImprovementType.farm
		elif improvementName == 'ImprovementType.quarry' or improvementName == 'quarry':
			return ImprovementType.quarry
		elif improvementName == 'ImprovementType.camp' or improvementName == 'camp':
			return ImprovementType.camp
		elif improvementName == 'ImprovementType.fishingBoats' or improvementName == 'fishingBoats':
			return ImprovementType.fishingBoats
		elif improvementName == 'ImprovementType.pasture' or improvementName == 'pasture':
			return ImprovementType.pasture
		elif improvementName == 'ImprovementType.oilWell' or improvementName == 'oilWell':
			return ImprovementType.oilWell
		elif improvementName == 'ImprovementType.fort' or improvementName == 'fort':
			return ImprovementType.fort
		elif improvementName == 'ImprovementType.citadelle' or improvementName == 'citadelle':
			return ImprovementType.citadelle
		elif improvementName == 'ImprovementType.goodyHut' or improvementName == 'goodyHut':
			return ImprovementType.goodyHut
		elif improvementName == 'ImprovementType.ruins' or improvementName == 'ruins':
			return ImprovementType.ruins

		raise Exception(f'No matching case for improvementName: "{improvementName}"')

	def title(self):
		return self._data().name

	def requiredTech(self) -> Optional[TechType]:
		return self._data().requiredTech

	def canBePillaged(self) -> bool:
		return self._data().canBePillaged

	def flavorValue(self, flavorType: FlavorType) -> int:
		flavorOfCard = next((flavor for flavor in self._data().flavors if flavor.flavorType == flavorType), None)

		if flavorOfCard is not None:
			return flavorOfCard.value

		return 0

	def _data(self) -> ImprovementTypeData:
		if self == ImprovementType.none:
			return ImprovementTypeData(
				name="",
				effects=[],
				requiredTech=None,
				civilization=None,
				canBePillaged=False,
				defenseModifier=0,
				flavors=[]
			)
		elif self == ImprovementType.barbarianCamp:
			#
			return ImprovementTypeData(
				name="Barbarian camp",
				effects=[],
				requiredTech=None,
				civilization=None,
				canBePillaged=False,
				defenseModifier=0,
				flavors=[]
			)
		elif self == ImprovementType.mine:
			# https://civilization.fandom.com/wiki/Mine_(Civ6)
			return ImprovementTypeData(
				name="Mine",
				effects=[
					"-1 Appeal",
					"+1 [Production] Production",
					"+1 [Production] Production (Apprenticeship)",
					"+1 [Production] Production (Industrialization)",
					"+1 [Production] Production (Smart Materials)"
				],
				requiredTech=TechType.mining,
				civilization=None,
				canBePillaged=True,
				defenseModifier=0,
				flavors=[]
			)
		elif self == ImprovementType.plantation:
			# https://civilization.fandom.com/wiki/Plantation_(Civ6)
			return ImprovementTypeData(
				name="Plantation",
				effects=[
					"+2 [Gold] Gold",
					"+0.5 [Housing] Housing",
					"+1 [Food] Food (Scientific Theory)",
					"+2 [Gold] Gold (Globalization)"
				],
				requiredTech=TechType.irrigation,
				civilization=None,
				canBePillaged=True,
				defenseModifier=0,
				flavors=[]
			)
		elif self == ImprovementType.farm:
			# https://civilization.fandom.com/wiki/Farm_(Civ6)
			return ImprovementTypeData(
				name="Farm",
				effects=[
					"+1 [Food] Food",
					"+0.5 [Housing] Housing",
					"+1 [Food] Food with two adjacent Farms (Feudalism)",
					"+1 [Food] Food for each adjacent Farm (Replaceable Parts)"
				],
				requiredTech=None,
				civilization=None,
				canBePillaged=True,
				defenseModifier=0,
				flavors=[]
			)
		elif self == ImprovementType.quarry:
			# https://civilization.fandom.com/wiki/Quarry_(Civ6)
			return ImprovementTypeData(
				name="Quarry",
				effects=[
					"-1 Appeal",
					"+1 [Production] Production",
					"+2 [Gold] Gold (Banking)",
					"+1 [Production] Production (Rocketry)",
					"+1 [Production] Production (Gunpowder)",
					"+1 [Production] Production (Predictive Systems)"
				],
				requiredTech=TechType.mining,
				civilization=None,
				canBePillaged=True,
				defenseModifier=0,
				flavors=[]
			)
		elif self == ImprovementType.camp:
			# https://civilization.fandom.com/wiki/Camp_(Civ6)
			return ImprovementTypeData(
				name="Camp",
				effects=[
					"+2 [Gold] Gold",
					"+0.5 [Housing] Housing",
					"+1 [Food] Food (Mercantilism)",
					"+1 [Production] (Mercantilism)",
					"+1 [Gold] Gold (Synthetic Materials)"
				],
				requiredTech=TechType.animalHusbandry,
				civilization=None,
				canBePillaged=True,
				defenseModifier=0,
				flavors=[]
			)
		elif self == ImprovementType.fishingBoats:
			# https://civilization.fandom.com/wiki/Fishing_Boats_(Civ6)
			return ImprovementTypeData(
				name="Fishing Boats",
				effects=[
					"+1 [Food] Food",
					"+0.5 [Housing] Housing",
					"+2 [Gold] Gold (Cartography)",
					"+1 [Food] Food (Plastics)"
				],
				requiredTech=TechType.sailing,
				civilization=None,
				canBePillaged=True,
				defenseModifier=0,
				flavors=[]
			)
		elif self == ImprovementType.pasture:
			# https://civilization.fandom.com/wiki/Pasture_(Civ6)
			return ImprovementTypeData(
				name="Pasture",
				effects=[
					"+1 [Production] Production",
					"+0.5 [Housing] Housing",
					"+1 [Food] Food (Stirrups)",
					"+1 [Production] Production (Robotics)"
				],
				requiredTech=TechType.animalHusbandry,
				civilization=None,
				canBePillaged=True,
				defenseModifier=0,
				flavors=[]
			)
		elif self == ImprovementType.oilWell:
			# https://civilization.fandom.com/wiki/Oil_Well_(Civ6)
			return ImprovementTypeData(
				name="Oil well",
				effects=[
					"-1 Appeal",
					"+2 [Production] Production"
				],
				requiredTech=TechType.steel,
				civilization=None,
				canBePillaged=True,
				defenseModifier=0,
				flavors=[]
			)
		elif self == ImprovementType.fort:
			# https://civilization.fandom.com/wiki/Fort_(Civ6)
			return ImprovementTypeData(
				name="Fort",
				effects=[
					"Occupying unit receives +4 Defense Strength and 2 turns of fortification.",
					"Built by a Military Engineer."
				],
				requiredTech=TechType.siegeTactics,
				civilization=None,
				canBePillaged=True,
				defenseModifier=4,
				flavors=[]
			)
		elif self == ImprovementType.goodyHut:
			#
			return ImprovementTypeData(
				name="Goodyhut",
				effects=[],
				requiredTech=None,
				civilization=None,
				canBePillaged=False,
				defenseModifier=0,
				flavors=[]
			)
		elif self == ImprovementType.citadelle:
			#
			return ImprovementTypeData(
				name="Citadelle",
				effects=[],
				requiredTech=TechType.siegeTactics,
				civilization=None,
				canBePillaged=True,
				defenseModifier=6,
				flavors=[]
			)
		elif self == ImprovementType.ruins:
			#
			return ImprovementTypeData(
				name="Ruins",
				effects=[],
				requiredTech=None,
				civilization=None,
				canBePillaged=False,
				defenseModifier=0,
				flavors=[]
			)

		raise InvalidEnumError(self)

	def yieldsFor(self, player) -> Yields:
		if self == ImprovementType.none:
			return Yields(food=0, production=0, gold=0, science=0)
		elif self == ImprovementType.barbarianCamp:
			return Yields(food=0, production=0, gold=0, science=0)
		elif self == ImprovementType.goodyHut:
			return Yields(food=0, production=0, gold=0, science=0)

		elif self == ImprovementType.mine:
			# https://civilization.fandom.com/wiki/Mine_(Civ6)
			yieldValue = Yields(food=0, production=1, gold=0, science=0, appeal=-1.0)

			# +1 additional Production (requires Apprenticeship)
			if player.techs.hasTech(TechType.apprenticeship):
				yieldValue.production += 1

			# +1 additional Production (requires Industrialization)
			if player.techs.hasTech(TechType.industrialization):
				yieldValue.production += 1

			# Provides adjacency bonus for Industrial Zones (+1 Production, ½ in GS-Only.png).

			# +1 additional Production (requires Smart Materials)
			#  /*if techs.has(tech: .smartMaterials) {
			#   yieldValue.production += 2

			return yieldValue
		elif self == ImprovementType.plantation:
			# https://civilization.fandom.com/wiki/Plantation_(Civ6)
			yieldValue = Yields(food=0, production=0, gold=2, science=0, housing=0.5)

			if player.civics.hasCivic(CivicType.feudalism):
				yieldValue.food += 1

			# +1 Food (Scientific Theory)
			if player.techs.hasTech(TechType.scientificTheory):
				yieldValue.food += 1

			# +2 Gold (Globalization)
			if player.civics.hasCivic(CivicType.globalization):
				yieldValue.gold += 2

			return yieldValue
		elif self == ImprovementType.farm:
			# https//civilization.fandom.com/wiki/Farm_(Civ6)
			yieldValue = Yields(food=1, production=0, gold=0, science=0, housing=0.5)

			# +1 additional Food with two adjacent Farms (requires Feudalism)
			if player.civics.hasCivic(CivicType.feudalism):
				yieldValue.food += 1

			# +1 additional Food for each adjacent Farm (requires Replaceable Parts)
			if player.techs.hasTech(TechType.replaceableParts):
				yieldValue.food += 1

			return yieldValue
		elif self == ImprovementType.quarry:
			yieldValue = Yields(food=0, production=1, gold=0, science=0, appeal=-1.0)

			# +2 Gold (Banking)
			if player.techs.hasTech(TechType.banking):
				yieldValue.gold += 2

			# +1 Production (Rocketry)
			if player.techs.hasTech(TechType.rocketry):
				yieldValue.production += 1

			# +1 Production (Gunpowder)
			if player.techs.hasTech(TechType.gunpowder):
				yieldValue.production += 1

			# +1 Production (Predictive Systems)
			# if player.techs.hasTech(TechType.predictiveSystems):
			# yieldValue.production += 1

			return yieldValue
		elif self == ImprovementType.camp:
			yieldValue = Yields(food=0, production=0, gold=1, science=0)

			# +1 Food and +1 Production (requires Mercantilism)
			if player.civics.hasCivic(CivicType.mercantilism):
				yieldValue.food += 1
				yieldValue.production += 1

			# +2 additional Gold (requires Synthetic Materials)
			if player.techs.hasTech(TechType.syntheticMaterials):
				yieldValue.gold += 2

			return yieldValue
		elif self == ImprovementType.fishingBoats:
			# https://civilization.fandom.com/wiki/Fishing_Boats_(Civ6)
			yieldValue = Yields(food=1, production=0, gold=0, science=0, housing=0.5)

			if player.techs.hasTech(TechType.cartography):
				yieldValue.gold += 2

			if player.civics.hasCivic(CivicType.colonialism):
				yieldValue.production += 1

			if player.techs.hasTech(TechType.plastics):
				yieldValue.food += 1

			return yieldValue
		elif self == ImprovementType.pasture:
			# https://civilization.fandom.com/wiki/Pasture_(Civ6)
			yieldValue = Yields(food=0, production=1, gold=0, science=0, housing=0.5)

			# +1 Food (requires Stirrups)
			if player.techs.hasTech(TechType.stirrups):
				yieldValue.food += 1

			# +1 additional Production and +1 additional Food (requires Robotics)
			if player.techs.hasTech(TechType.robotics):
				yieldValue.production += 1
				yieldValue.food += 1

			# +1 Production from every adjacent Outback Station (requires Steam Power)

			# +1 additional Production (requires Replaceable Parts)
			if player.techs.hasTech(TechType.replaceableParts):
				yieldValue.production += 1

			return yieldValue
		elif self == ImprovementType.oilWell:
			# https://civilization.fandom.com/wiki/Oil_Well_(Civ6)
			yieldValue = Yields(food=0, production=2, gold=0, appeal=-1)

			# +1 Production(requires Predictive Systems)
			# if player.techs.hasTech(TechType.predictiveSystems):
			#	yieldValue.production += 1

			return yieldValue
		elif self == ImprovementType.fort:
			return Yields(food=0, production=0, gold=0, science=0)
		elif self == ImprovementType.citadelle:
			return Yields(food=0, production=0, gold=0, science=0)
		elif self == ImprovementType.ruins:
			return Yields(food=0, production=0, gold=0, science=0)

		raise InvalidEnumError(self)

	def civilization(self) -> CivilizationType:
		return self._data().civilization

	def isPossibleOn(self, tile) -> bool:
		# can't set an improvement to unowned tile or can we?
		if tile.owner() is None:
			return False

		if self == ImprovementType.none:
			return False  # invalid everywhere

		elif self == ImprovementType.barbarianCamp:
			return self.isBarbarianCampPossibleOn(tile)
		elif self == ImprovementType.goodyHut:
			return self.isGoodyHutPossibleOn(tile)
		elif self == ImprovementType.ruins:
			return False

		elif self == ImprovementType.farm:
			return self.isFarmPossibleOn(tile)
		elif self == ImprovementType.mine:
			return self.isMinePossibleOn(tile)
		elif self == ImprovementType.quarry:
			return self.isQuarryPossibleOn(tile)
		elif self == ImprovementType.camp:
			return self.isCampPossibleOn(tile)
		elif self == ImprovementType.pasture:
			return self.isPasturePossibleOn(tile)
		elif self == ImprovementType.plantation:
			return self.isPlantationPossibleOn(tile)
		elif self == ImprovementType.fishingBoats:
			return self.isFishingBoatsPossibleOn(tile)
		elif self == ImprovementType.oilWell:
			return self.isOilWellPossibleOn(tile)
		elif self == ImprovementType.fort:
			return True  #
		elif self == ImprovementType.citadelle:
			return False  #

		raise InvalidEnumError(self)

	def isFarmPossibleOn(self, tile) -> bool:
		"""
		Farms can be built on non-desert and non-tundra flat lands, which are the most available tiles in Civilization VI.
		https://civilization.fandom.com/wiki/Farm_(Civ6)

		@param tile:
		@return:
		"""
		owner = tile.owner()
		if owner is None:
			return False

		# Initially, it can be constructed only on flatland Grassland, Plains, ...
		if (tile.terrain() == TerrainType.grass or tile.terrain() == TerrainType.plains) and not tile.isHills():
			return True

		# or Floodplains tiles
		if tile.terrain() == TerrainType.desert and not tile.isHills() and tile.hasFeature(FeatureType.floodplains):
			return True

		# but researching Civil Engineering enables Farms to be built on Grassland Hills and Plains Hills.
		if (tile.terrain() == TerrainType.grass or tile.terrain() == TerrainType.plains) and tile.isHills() and \
			owner.hasCivic(CivicType.civilEngineering):
			return True

		return False

	def isMinePossibleOn(self, tile):
		owner = tile.owner()
		if owner is None:
			return False

		if not tile.terrain().isLand():
			return False

		hasSupportedResource = False

		hasSupportedResource = hasSupportedResource or tile.hasResource(ResourceType.iron, owner)
		hasSupportedResource = hasSupportedResource or tile.hasResource(ResourceType.niter, owner)
		hasSupportedResource = hasSupportedResource or tile.hasResource(ResourceType.coal, owner)
		hasSupportedResource = hasSupportedResource or tile.hasResource(ResourceType.aluminum, owner)
		hasSupportedResource = hasSupportedResource or tile.hasResource(ResourceType.uranium, owner)
		# hasSupportedResource = hasSupportedResource or tile.hasResource(ResourceType.diamonds, owner)
		# hasSupportedResource = hasSupportedResource or tile.hasResource(ResourceType.jade, owner)
		# hasSupportedResource = hasSupportedResource or tile.hasResource(ResourceType.mercury, owner)
		hasSupportedResource = hasSupportedResource or tile.hasResource(ResourceType.salt, owner)
		hasSupportedResource = hasSupportedResource or tile.hasResource(ResourceType.silver, owner)
		# hasSupportedResource = hasSupportedResource or tile.hasResource(ResourceType.amber, for: owner)
		hasSupportedResource = hasSupportedResource or tile.hasResource(ResourceType.copper, owner)

		# hills or Iron Niter Coal Aluminum Uranium Diamonds Jade Mercury Salt Silver Amber Copper
		if not tile.isHills() and not hasSupportedResource:
			return False

		if not owner.hasTech(TechType.mining):
			return False

		return True

	def isPasturePossibleOn(self, tile) -> bool:
		owner = tile.owner()
		if owner is None:
			return False

		if not owner.hasTech(TechType.animalHusbandry):
			return False

		requiredResources = [ResourceType.cattle, ResourceType.sheep, ResourceType.horses]
		hasSupportedResource = False

		for requiredResource in requiredResources:
			hasSupportedResource = hasSupportedResource or tile.hasResource(requiredResource, owner)

		return hasSupportedResource

	def isPlantationPossibleOn(self, tile) -> bool:
		owner = tile.owner()
		if owner is None:
			return False

		if not owner.hasTech(TechType.irrigation):
			return False

		# .coffee, .olives, .tobacco
		requiredResources = [
			ResourceType.banana, ResourceType.citrus, ResourceType.cocoa, ResourceType.cotton,
			ResourceType.dyes, ResourceType.incense, ResourceType.silk, ResourceType.spices,
			ResourceType.sugar, ResourceType.tea, ResourceType.wine
		]
		hasSupportedResource = False

		for requiredResource in requiredResources:
			hasSupportedResource = hasSupportedResource or tile.hasResource(requiredResource, owner)

		return hasSupportedResource

	def isCampPossibleOn(self, tile):
		owner = tile.owner()
		if owner is None:
			return False

		if not owner.hasTech(TechType.animalHusbandry):
			return False

		# .truffles
		requiredResources = [ResourceType.deer, ResourceType.furs, ResourceType.ivory]
		hasSupportedResource = False

		for requiredResource in requiredResources:
			hasSupportedResource = hasSupportedResource or tile.hasResource(requiredResource, owner)

		return hasSupportedResource

	def isFishingBoatsPossibleOn(self, tile):
		owner = tile.owner()
		if owner is None:
			return False

		if not owner.hasTech(TechType.sailing):
			return False

		# ResourceType.amber, ResourceType.turtles
		requiredResources = [ResourceType.fish, ResourceType.whales, ResourceType.pearls, ResourceType.crab]
		hasSupportedResource = False

		for requiredResource in requiredResources:
			hasSupportedResource = hasSupportedResource or tile.hasResource(requiredResource, owner)

		return hasSupportedResource

	def defenseModifier(self) -> int:
		return self._data().defenseModifier

	def isQuarryPossibleOn(self, tile) -> bool:
		owner = tile.owner()

		if owner is None:
			return False

		if not owner.hasTech(TechType.animalHusbandry):
			return False

		return tile.hasResource(ResourceType.stone, owner) or tile.hasResource(ResourceType.marble, owner)  # or tile.has(resource:.gypsum, for: owner) * /

	def isOilWellPossibleOn(self, tile) -> bool:
		owner = tile.owner()

		if owner is None:
			return False

		if not owner.hasTech(TechType.refining):
			return False

		return tile.hasResource(ResourceType.oil, owner)

	def isBarbarianCampPossibleOn(self, tile) -> bool:
		return tile.terrain().isLand()

	def isGoodyHutPossibleOn(self, tile) -> bool:
		if tile.terrain() != TerrainType.grass and tile.terrain() != TerrainType.plains and \
			tile.terrain() != TerrainType.desert and tile.terrain() != TerrainType.tundra:
			return False

		if tile.feature() != FeatureType.none and tile.feature() != FeatureType.forest and \
			tile.feature() != FeatureType.rainforest:
			return False

		return True
