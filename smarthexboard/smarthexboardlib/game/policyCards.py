from typing import Optional

from smarthexboard.smarthexboardlib.game.flavors import Flavor, FlavorType
from smarthexboard.smarthexboardlib.game.types import CivicType, EraType
from smarthexboard.smarthexboardlib.core.base import ExtendedEnum, InvalidEnumError


class PolicyCardSlotData:
	def __init__(self, name: str):
		self.name = name


class PolicyCardSlot(ExtendedEnum):
	diplomatic = 'diplomatic'
	wildcard = 'wildcard'
	economic = 'economic'
	military = 'military'
	darkAge = 'darkAge'

	def name(self) -> str:
		return self._data().name

	def _data(self) -> PolicyCardSlotData:
		if self == PolicyCardSlot.diplomatic:
			return PolicyCardSlotData(name='TXT_KEY_POLICY_CARD_TYPE_DIPLOMATIC_TITLE')
		elif self == PolicyCardSlot.wildcard:
			return PolicyCardSlotData(name='TXT_KEY_POLICY_CARD_TYPE_WILDCARD_TITLE')
		elif self == PolicyCardSlot.economic:
			return PolicyCardSlotData(name='TXT_KEY_POLICY_CARD_TYPE_ECONOMIC_TITLE')
		elif self == PolicyCardSlot.military:
			return PolicyCardSlotData(name='TXT_KEY_POLICY_CARD_TYPE_MILITARY_TITLE')
		elif self == PolicyCardSlot.darkAge:
			return PolicyCardSlotData(name='TXT_KEY_POLICY_CARD_TYPE_DARK_AGE_TITLE')

		raise InvalidEnumError(self)


class PolicyCardType:
	pass


class PolicyCardTypeData:
	def __init__(self, name: str, bonus: str, slot: PolicyCardSlot, requiredCivic: Optional[CivicType] = None,
	             obsoleteCivic: Optional[CivicType] = None, startEra: Optional[EraType] = None,
	             endEra: Optional[EraType] = None, replace: [PolicyCardType] = [], flavors: [Flavor] = [],
	             requiresDarkAge: bool = False):
		"""
		@param name: name of this policy card
		@param bonus: description of the bonus of this policy card
		@param slot: slot / type of this policy card
		@param requiredCivic: civic that unlocks this policy card
		@param obsoleteCivic: civic that makes this policy card obsolete
		@param startEra: era when this policy card is unlocked
		@param endEra: era when this policy card is obsolete
		@param replace: policy cards that gets removed when this card is active
		@param flavors: flavors for this policy cards
		@param requiresDarkAge: true if this policy cards requires a dark age
		"""
		self.name = name
		self.bonus = bonus
		self.slot = slot
		self.requiredCivic = requiredCivic
		self.obsoleteCivic = obsoleteCivic
		self.startEra = startEra
		self.endEra = endEra
		self.replace = replace,
		self.flavors = flavors
		self.requiresDarkAge = requiresDarkAge


class PolicyCardType(ExtendedEnum):
	none = 'none'

	# ancient
	survey = 'survey'
	godKing = 'godKing'
	discipline = 'discipline'
	urbanPlanning = 'urbanPlanning'
	ilkum = 'ilkum'
	agoge = 'agoge'
	caravansaries = 'caravansaries'
	maritimeIndustries = 'maritimeIndustries'
	maneuver = 'maneuver'
	strategos = 'strategos'
	conscription = 'conscription'
	corvee = 'corvee'
	landSurveyors = 'landSurveyors'
	colonization = 'colonization'
	inspiration = 'inspiration'
	revelation = 'revelation'
	limitanei = 'limitanei'

	# classical
	insulae = 'insulae'
	charismaticLeader = 'charismaticLeader'
	diplomaticLeague = 'diplomaticLeague'
	literaryTradition = 'literaryTradition'
	raid = 'raid'
	veterancy = 'veterancy'
	equestrianOrders = 'equestrianOrders'
	bastions = 'bastions'
	limes = 'limes'
	naturalPhilosophy = 'naturalPhilosophy'
	scripture = 'scripture'
	praetorium = 'praetorium'

	# medieval
	navalInfrastructure = 'navalInfrastructure'
	navigation = 'navigation'
	feudalContract = 'feudalContract'
	serfdom = 'serfdom'
	meritocracy = 'meritocracy'
	retainers = 'retainers'
	sack = 'sack'
	professionalArmy = 'professionalArmy'
	retinues = 'retinues'
	tradeConfederation = 'tradeConfederation'
	merchantConfederation = 'merchantConfederation'
	aesthetics = 'aesthetics'
	medinaQuarter = 'medinaQuarter'
	craftsmen = 'craftsmen'  # added
	townCharters = 'townCharters'
	travelingMerchants = 'travelingMerchants'
	chivalry = 'chivalry'
	gothicArchitecture = 'gothicArchitecture'
	civilPrestige = 'civilPrestige'

	# renaissance
	colonialOffices = 'colonialOffices'
	invention = 'invention'
	frescoes = 'frescoes'
	# machiavellianism
	# warsOfReligion
	# simultaneum
	# religiousOrders
	logistics = 'logistics'
	triangularTrade = 'triangularTrade'
	# drillManuals
	# rationalism
	# freeMarket
	liberalism = 'liberalism'
	# wisselbanken
	pressGangs = 'pressGangs'

	# industrial
	# nativeConquest
	grandeArmee = 'grandeArmee'
	# nationalIdentity
	# colonialTaxes
	# raj
	# publicWorks
	# skyscrapers,
	# grandOpera
	# symphonies
	# publicTransport
	militaryResearch = 'militaryResearch'
	# forceModernization
	# totalWar
	expropriation = 'expropriation'
	militaryOrganization = 'militaryOrganization'

	# modern
	resourceManagement = 'resourceManagement'
	propaganda = 'propaganda'
	leveeEnMasse = 'leveeEnMasse'
	laissezFaire = 'laissezFaire'
	marketEconomy = 'marketEconomy'
	policeState = 'policeState'
	nobelPrize = 'nobelPrize'
	# scienceFoundations
	# nuclearEspionage
	# economicUnion
	theirFinestHour = 'theirFinestHour'
	# arsenalOfDemocracy
	newDeal = 'newDeal'
	lightningWarfare = 'lightningWarfare'
	thirdAlternative = 'thirdAlternative'
	# martialLaw
	# gunboatDiplomacy
	fiveYearPlan = 'fiveYearPlan'
	collectivization = 'collectivization'
	# patrioticWar
	# defenseOfTheMotherland

	# atomic
	# cryptography
	internationalWaters = 'internationalWaters'
	# containment
	# heritageTourism
	# sportsMedia
	militaryFirst = 'militaryFirst'
	# satelliteBroadcasts
	# musicCensorship
	integratedSpaceCell = 'integratedSpaceCell'
	# secondStrikeCapability

	# information
	strategicAirForce = 'strategicAirForce'
	ecommerce = 'ecommerce'
	internationalSpaceAgency = 'internationalSpaceAgency'
	# onlineCommunities
	collectiveActivism = 'collectiveActivism'
	afterActionReports = 'afterActionReports'
	communicationsOffice = 'communicationsOffice'
	# aerospaceContractors

	# future
	# spaceTourism
	# hallyu
	# nonStateActors
	# integratedAttackLogistics
	# rabblerousing
	# diplomaticCapital
	# globalCoalition

	# dark age
	automatedWorkforce = 'automatedWorkforce'
	collectivism = 'collectivism'
	# cyberWarfare
	decentralization = 'decentralization'
	despoticPaternalism = 'despoticPaternalism'
	# disinformationCampaign
	eliteForces = 'eliteForces'
	# flowerPower
	# inquisition
	isolationism = 'isolationism'
	# lettersOfMarque
	monasticism = 'monasticism'
	robberBarons = 'robberBarons'
	# rogueState
	# samoderzhaviye
	# softTargets
	twilightValor = 'twilightValor'

	def name(self) -> str:
		return self._data().name

	def slot(self) -> PolicyCardSlot:
		return self._data().slot

	def requiredCivic(self) -> Optional[CivicType]:
		return self._data().requiredCivic

	def obsoleteCivic(self) -> Optional[CivicType]:
		return self._data().obsoleteCivic

	def startEra(self) -> Optional[EraType]:
		return self._data().startEra

	def endEra(self) -> Optional[EraType]:
		return self._data().endEra

	def requiresDarkAge(self) -> bool:
		return self._data().requiresDarkAge

	def replacePolicyCards(self) -> [PolicyCardType]:
		return self._data().replace

	def flavorValue(self, flavorType: FlavorType) -> int:
		flavorOfCard = next((flavor for flavor in self._data().flavors if flavor.flavorType == flavorType), None)

		if flavorOfCard is not None:
			return flavorOfCard.value

		return 0

	def _data(self) -> PolicyCardTypeData:
		if self == PolicyCardType.none:
			return PolicyCardTypeData(
				name='KEY_NONE',
				bonus='',
				slot=PolicyCardSlot.wildcard,
				requiredCivic=None,
				requiresDarkAge=False
			)

		# ancient
		if self == PolicyCardType.survey:
			# https://civilization.fandom.com/wiki/Survey_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_SURVEY_TITLE",
				bonus="TXT_KEY_POLICY_CARD_SURVEY_BONUS",
				slot=PolicyCardSlot.military,
				requiredCivic=CivicType.codeOfLaws,
				obsoleteCivic=CivicType.exploration,
				replace=[],
				flavors=[
					Flavor(FlavorType.recon, value=5)
				]
			)
		if self == PolicyCardType.godKing:
			# https://civilization.fandom.com/wiki/God_King_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_GOD_KING_TITLE",
				bonus="TXT_KEY_POLICY_CARD_GOD_KING_BONUS",
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.codeOfLaws,
				obsoleteCivic=CivicType.theology,
				replace=[],
				flavors=[
					Flavor(FlavorType.religion, value=3),
					Flavor(FlavorType.gold, value=2)
				]
			)
		if self == PolicyCardType.discipline:
			# https://civilization.fandom.com/wiki/Discipline_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_DISCIPLINE_TITLE",
				bonus="TXT_KEY_POLICY_CARD_DISCIPLINE_BONUS",
				slot=PolicyCardSlot.military,
				requiredCivic=CivicType.codeOfLaws,
				obsoleteCivic=CivicType.colonialism,
				replace=[],
				flavors=[
					Flavor(FlavorType.defense, value=4),
					Flavor(FlavorType.growth, value=1)
				]
			)
		if self == PolicyCardType.urbanPlanning:
			#
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_URBAN_PLANNING_TITLE",
				bonus="TXT_KEY_POLICY_CARD_URBAN_PLANNING_BONUS",
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.codeOfLaws,
				obsoleteCivic=CivicType.gamesAndRecreation,
				replace=[],
				flavors=[
					Flavor(FlavorType.growth, value=2),
					Flavor(FlavorType.production, value=3)
				]
			)
		if self == PolicyCardType.ilkum:
			# https://civilization.fandom.com/wiki/Ilkum_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_ILKUM_TITLE",
				bonus="TXT_KEY_POLICY_CARD_ILKUM_BONUS",
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.craftsmanship,
				obsoleteCivic=CivicType.gamesAndRecreation,
				replace=[],
				flavors=[
					Flavor(FlavorType.growth, value=2),
					Flavor(FlavorType.tileImprovement, value=3)
				]
			)
		if self == PolicyCardType.agoge:
			# https://civilization.fandom.com/wiki/Agoge_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_AGOGE_TITLE",
				bonus="TXT_KEY_POLICY_CARD_AGOGE_BONUS",
				slot=PolicyCardSlot.military,
				requiredCivic=CivicType.craftsmanship,
				obsoleteCivic=CivicType.feudalism,
				replace=[],
				flavors=[
					Flavor(FlavorType.offense, value=3),
					Flavor(FlavorType.defense, value=2)
				]
			)
		if self == PolicyCardType.caravansaries:
			# https://civilization.fandom.com/wiki/Caravansaries_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_CARAVANSARIES_TITLE",
				bonus="TXT_KEY_POLICY_CARD_CARAVANSARIES_BONUS",
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.foreignTrade,
				obsoleteCivic=CivicType.mercantilism,
				replace=[],
				flavors=[
					Flavor(FlavorType.gold, value=5)
				]
			)
		if self == PolicyCardType.maritimeIndustries:
			# https://civilization.fandom.com/wiki/Maritime_Industries_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_MARITIME_INDUSTRIES_TITLE",
				bonus="TXT_KEY_POLICY_CARD_MARITIME_INDUSTRIES_BONUS",
				slot=PolicyCardSlot.military,
				requiredCivic=CivicType.foreignTrade,
				obsoleteCivic=CivicType.colonialism,
				replace=[],
				flavors=[
					Flavor(FlavorType.navalGrowth, value=3),
					Flavor(FlavorType.naval, value=2)
				]
			)
		if self == PolicyCardType.maneuver:
			# https://civilization.fandom.com/wiki/Maneuver_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_MANEUVER_TITLE",
				bonus="TXT_KEY_POLICY_CARD_MANEUVER_BONUS",
				slot=PolicyCardSlot.military,
				requiredCivic=CivicType.militaryTradition,
				obsoleteCivic=CivicType.divineRight,
				replace=[],
				flavors=[
					Flavor(FlavorType.mobile, value=4),
					Flavor(FlavorType.offense, value=1)
				]
			)
		if self == PolicyCardType.strategos:
			# https://civilization.fandom.com/wiki/Strategos_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_STRATEGOS_TITLE",
				bonus="TXT_KEY_POLICY_CARD_STRATEGOS_BONUS",
				slot=PolicyCardSlot.wildcard,
				requiredCivic=CivicType.militaryTradition,
				obsoleteCivic=CivicType.scorchedEarth,
				replace=[],
				flavors=[
					Flavor(FlavorType.greatPeople, value=5)
				]
			)
		if self == PolicyCardType.conscription:
			# https://civilization.fandom.com/wiki/Conscription_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_CONSCRIPTION_TITLE",
				bonus="TXT_KEY_POLICY_CARD_CONSCRIPTION_BONUS",
				slot=PolicyCardSlot.military,
				requiredCivic=CivicType.stateWorkforce,
				obsoleteCivic=CivicType.mobilization,
				replace=[],
				flavors=[
					Flavor(FlavorType.offense, value=4),
					Flavor(FlavorType.gold, value=1)
				]
			)
		if self == PolicyCardType.corvee:
			# https://civilization.fandom.com/wiki/Corv%C3%A9e_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_CORVEE_TITLE",
				bonus="TXT_KEY_POLICY_CARD_CORVEE_BONUS",
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.stateWorkforce,
				obsoleteCivic=CivicType.divineRight,
				replace=[],
				flavors=[
					Flavor(FlavorType.wonder, value=5)
				]
			)
		if self == PolicyCardType.landSurveyors:
			# https://civilization.fandom.com/wiki/Land_Surveyors_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_LAND_SURVEYORS_TITLE",
				bonus="TXT_KEY_POLICY_CARD_LAND_SURVEYORS_BONUS",
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.earlyEmpire,
				obsoleteCivic=CivicType.scorchedEarth,
				replace=[],
				flavors=[
					Flavor(FlavorType.growth, value=3),
					Flavor(FlavorType.tileImprovement, value=2)
				]
			)
		if self == PolicyCardType.colonization:
			# https://civilization.fandom.com/wiki/Colonization_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_COLONIZATION_TITLE",
				bonus="TXT_KEY_POLICY_CARD_COLONIZATION_BONUS",
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.earlyEmpire,
				obsoleteCivic=CivicType.scorchedEarth,
				replace=[],
				flavors=[
					Flavor(FlavorType.growth, value=5)
				]
			)
		if self == PolicyCardType.inspiration:
			# https://civilization.fandom.com/wiki/Inspiration_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_INSPIRATION_TITLE",
				bonus="TXT_KEY_POLICY_CARD_INSPIRATION_BONUS",
				slot=PolicyCardSlot.wildcard,
				requiredCivic=CivicType.mysticism,
				obsoleteCivic=CivicType.nuclearProgram,
				replace=[],
				flavors=[
					Flavor(FlavorType.science, value=2),
					Flavor(FlavorType.greatPeople, value=3)
				]
			)
		if self == PolicyCardType.revelation:
			# https://civilization.fandom.com/wiki/Revelation_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_REVELATION_TITLE",
				bonus="TXT_KEY_POLICY_CARD_REVELATION_BONUS",
				slot=PolicyCardSlot.wildcard,
				requiredCivic=CivicType.mysticism,
				obsoleteCivic=CivicType.humanism,
				replace=[],
				flavors=[
					Flavor(FlavorType.religion, value=2),
					Flavor(FlavorType.greatPeople, value=3)
				]
			)
		if self == PolicyCardType.limitanei:
			# https://civilization.fandom.com/wiki/Limitanei_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_LIMITANEI_TITLE",
				bonus="TXT_KEY_POLICY_CARD_LIMITANEI_BONUS",
				slot=PolicyCardSlot.military,
				requiredCivic=CivicType.earlyEmpire,
				obsoleteCivic=None,
				replace=[],
				flavors=[Flavor(FlavorType.growth, value=5)]
			)

		# classical
		if self == PolicyCardType.insulae:
			# https://civilization.fandom.com/wiki/Insulae_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_INSULAE_TITLE",
				bonus="TXT_KEY_POLICY_CARD_INSULAE_BONUS",
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.gamesAndRecreation,
				obsoleteCivic=CivicType.medievalFaires,
				replace=[],
				flavors=[
					Flavor(FlavorType.growth, value=3),
					Flavor(FlavorType.tileImprovement, value=2)
				]
			)
		if self == PolicyCardType.charismaticLeader:
			# https://civilization.fandom.com/wiki/Charismatic_Leader_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_CHARISMATIC_LEADER_TITLE",
				bonus="TXT_KEY_POLICY_CARD_CHARISMATIC_LEADER_BONUS",  #
				slot=PolicyCardSlot.diplomatic,
				requiredCivic=CivicType.politicalPhilosophy,
				obsoleteCivic=CivicType.totalitarianism,
				replace=[],
				flavors=[]
			)
		if self == PolicyCardType.diplomaticLeague:
			# https://civilization.fandom.com/wiki/Diplomatic_League_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_DIPLOMATIC_LEAGUE_TITLE",
				bonus="TXT_KEY_POLICY_CARD_DIPLOMATIC_LEAGUE_BONUS",  #
				slot=PolicyCardSlot.diplomatic,
				requiredCivic=CivicType.politicalPhilosophy,
				obsoleteCivic=None,
				replace=[],
				flavors=[]
			)
		if self == PolicyCardType.literaryTradition:
			# https://civilization.fandom.com/wiki/Literary_Tradition_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_LITERARY_TRADITION_TITLE",
				bonus="TXT_KEY_POLICY_CARD_LITERARY_TRADITION_BONUS",
				slot=PolicyCardSlot.wildcard,
				requiredCivic=CivicType.dramaAndPoetry,
				obsoleteCivic=None,
				replace=[],
				flavors=[]
			)
		if self == PolicyCardType.raid:
			# https://civilization.fandom.com/wiki/Raid_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_RAID_TITLE",
				bonus="TXT_KEY_POLICY_CARD_RAID_BONUS",  #
				slot=PolicyCardSlot.military,
				requiredCivic=CivicType.militaryTraining,
				obsoleteCivic=CivicType.scorchedEarth,
				replace=[],
				flavors=[]
			)
		if self == PolicyCardType.veterancy:
			# https://civilization.fandom.com/wiki/Veterancy_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_VETERANCY_TITLE",
				bonus="TXT_KEY_POLICY_CARD_VETERANCY_BONUS",  #
				slot=PolicyCardSlot.military,
				requiredCivic=CivicType.militaryTraining,
				obsoleteCivic=None,
				replace=[],
				flavors=[]
			)
		if self == PolicyCardType.equestrianOrders:
			# https://civilization.fandom.com/wiki/Equestrian_Orders_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_EQUESTRIAN_ORDERS_TITLE",
				bonus="TXT_KEY_POLICY_CARD_EQUESTRIAN_ORDERS_BONUS",  #
				slot=PolicyCardSlot.military,
				requiredCivic=CivicType.militaryTraining,
				obsoleteCivic=None,
				replace=[],
				flavors=[]
			)
		if self == PolicyCardType.bastions:
			# https://civilization.fandom.com/wiki/Bastions_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_BASTIONS_TITLE",
				bonus="TXT_KEY_POLICY_CARD_BASTIONS_BONUS",
				slot=PolicyCardSlot.military,
				requiredCivic=CivicType.defensiveTactics,
				obsoleteCivic=CivicType.civilEngineering,
				replace=[],
				flavors=[]
			)
		if self == PolicyCardType.limes:
			# https://civilization.fandom.com/wiki/Limes_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_LIMES_TITLE",
				bonus="TXT_KEY_POLICY_CARD_LIMES_BONUS",  #
				slot=PolicyCardSlot.military,
				requiredCivic=CivicType.defensiveTactics,
				obsoleteCivic=CivicType.totalitarianism,
				replace=[],
				flavors=[]
			)
		if self == PolicyCardType.naturalPhilosophy:
			# https://civilization.fandom.com/wiki/Natural_Philosophy_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_NATURAL_PHILOSOPHY_TITLE",
				bonus="TXT_KEY_POLICY_CARD_NATURAL_PHILOSOPHY_BONUS",  #
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.recordedHistory,
				obsoleteCivic=CivicType.classStruggle,
				replace=[],
				flavors=[]
			)
		if self == PolicyCardType.scripture:
			# https://civilization.fandom.com/wiki/Scripture_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_SCRIPTURE_TITLE",
				bonus="TXT_KEY_POLICY_CARD_SCRIPTURE_BONUS",  #
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.theology,
				obsoleteCivic=None,
				replace=[PolicyCardType.godKing],
				flavors=[]
			)
		if self == PolicyCardType.praetorium:
			# https://civilization.fandom.com/wiki/Praetorium_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_PRAETORIUM_TITLE",
				bonus="TXT_KEY_POLICY_CARD_PRAETORIUM_BONUS",
				slot=PolicyCardSlot.diplomatic,
				requiredCivic=CivicType.recordedHistory,
				obsoleteCivic=CivicType.socialMedia,
				replace=[],
				flavors=[Flavor(FlavorType.growth, value=4)]
			)

		# medieval
		if self == PolicyCardType.navalInfrastructure:
			# https://civilization.fandom.com/wiki/Naval_Infrastructure_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_NAVAL_INFRASTRUCTURE_TITLE",
				bonus="TXT_KEY_POLICY_CARD_NAVAL_INFRASTRUCTURE_BONUS",  #
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.navalTradition,
				obsoleteCivic=CivicType.suffrage,
				replace=[],
				flavors=[]
			)
		if self == PolicyCardType.navigation:
			# https://civilization.fandom.com/wiki/Navigation_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_NAVIGATION_TITLE",
				bonus="TXT_KEY_POLICY_CARD_NAVIGATION_BONUS",
				slot=PolicyCardSlot.wildcard,
				requiredCivic=CivicType.navalTradition,
				obsoleteCivic=None,
				replace=[],
				flavors=[]
			)
		if self == PolicyCardType.feudalContract:
			# https://civilization.fandom.com/wiki/Feudal_Contract_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_FEUDAL_CONTRACT_TITLE",
				bonus="TXT_KEY_POLICY_CARD_FEUDAL_CONTRACT_BONUS",  #
				slot=PolicyCardSlot.military,
				requiredCivic=CivicType.feudalism,
				obsoleteCivic=CivicType.nationalism,
				replace=[PolicyCardType.agoge],
				flavors=[]
			)
		if self == PolicyCardType.serfdom:
			# https://civilization.fandom.com/wiki/Serfdom_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_SERFDOM_TITLE",
				bonus="TXT_KEY_POLICY_CARD_SERFDOM_BONUS",
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.feudalism,
				obsoleteCivic=CivicType.civilEngineering,
				replace=[PolicyCardType.ilkum],
				flavors=[]
			)
		if self == PolicyCardType.meritocracy:
			# https://civilization.fandom.com/wiki/Meritocracy_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_MERITOCRACY_TITLE",
				bonus="TXT_KEY_POLICY_CARD_MERITOCRACY_BONUS",  #
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.civilService,
				obsoleteCivic=None,
				replace=[],
				flavors=[]
			)
		if self == PolicyCardType.retainers:
			# https://civilization.fandom.com/wiki/Retainers_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_RETAINERS_TITLE",
				bonus="TXT_KEY_POLICY_CARD_RETAINERS_BONUS",
				slot=PolicyCardSlot.military,
				requiredCivic=CivicType.civilService,
				obsoleteCivic=CivicType.massMedia,
				replace=[],
				flavors=[]
			)
		if self == PolicyCardType.sack:
			# https://civilization.fandom.com/wiki/Sack_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_SACK_TITLE",
				bonus="TXT_KEY_POLICY_CARD_SACK_BONUS",  #
				slot=PolicyCardSlot.military,
				requiredCivic=CivicType.mercenaries,
				obsoleteCivic=CivicType.scorchedEarth,
				replace=[],
				flavors=[]
			)
		if self == PolicyCardType.professionalArmy:
			# https://civilization.fandom.com/wiki/Professional_Army_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_PROFESSIONAL_ARMY_TITLE",
				bonus="TXT_KEY_POLICY_CARD_PROFESSIONAL_ARMY_BONUS",
				slot=PolicyCardSlot.military,
				requiredCivic=CivicType.mercenaries,
				obsoleteCivic=CivicType.urbanization,
				replace=[],
				flavors=[]
			)
		if self == PolicyCardType.retinues:
			# https://civilization.fandom.com/wiki/Retinues_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_RETINUES_TITLE",
				bonus="TXT_KEY_POLICY_CARD_RETINUES_BONUS",  #
				slot=PolicyCardSlot.military,
				requiredCivic=CivicType.mercenaries,
				obsoleteCivic=CivicType.urbanization,
				replace=[],
				flavors=[]
			)
		if self == PolicyCardType.tradeConfederation:
			# https://civilization.fandom.com/wiki/Trade_Confederation_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_TRADE_CONFEDERATION_TITLE",
				bonus="TXT_KEY_POLICY_CARD_TRADE_CONFEDERATION_BONUS",
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.mercenaries,
				obsoleteCivic=CivicType.capitalism,
				replace=[],
				flavors=[]
			)
		if self == PolicyCardType.merchantConfederation:
			# https://civilization.fandom.com/wiki/Merchant_Confederation_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_MERCHANT_CONFEDERATION_TITLE",
				bonus="TXT_KEY_POLICY_CARD_MERCHANT_CONFEDERATION_BONUS",  #
				slot=PolicyCardSlot.diplomatic,
				requiredCivic=CivicType.medievalFaires,
				obsoleteCivic=None,
				replace=[],
				flavors=[]
			)
		if self == PolicyCardType.aesthetics:
			# https://civilization.fandom.com/wiki/Aesthetics_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_AESTHETICS_TITLE",
				bonus="TXT_KEY_POLICY_CARD_AESTHETICS_BONUS",  #
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.medievalFaires,
				obsoleteCivic=CivicType.professionalSports,
				replace=[],
				flavors=[]
			)
		if self == PolicyCardType.medinaQuarter:
			# https://civilization.fandom.com/wiki/Medina_Quarter_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_MEDINA_QUARTER_TITLE",
				bonus="TXT_KEY_POLICY_CARD_MEDINA_QUARTER_BONUS",  #
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.medievalFaires,
				obsoleteCivic=CivicType.suffrage,
				replace=[PolicyCardType.insulae],
				flavors=[]
			)
		if self == PolicyCardType.craftsmen:
			# https://civilization.fandom.com/wiki/Craftsmen_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_CRAFTSMEN_TITLE",
				bonus="TXT_KEY_POLICY_CARD_CRAFTSMEN_BONUS",  #
				slot=PolicyCardSlot.military,
				requiredCivic=CivicType.guilds,
				obsoleteCivic=CivicType.classStruggle,
				replace=[],
				flavors=[]
			)
		if self == PolicyCardType.townCharters:
			# https://civilization.fandom.com/wiki/Town_Charters_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_TOWN_CHARTERS_TITLE",
				bonus="TXT_KEY_POLICY_CARD_TOWN_CHARTERS_BONUS",  #
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.guilds,
				obsoleteCivic=CivicType.suffrage,
				replace=[],
				flavors=[]
			)
		if self == PolicyCardType.travelingMerchants:
			# https://civilization.fandom.com/wiki/Traveling_Merchants_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_TRAVELING_MERCHANTS_TITLE",
				bonus="TXT_KEY_POLICY_CARD_TRAVELING_MERCHANTS_BONUS",
				slot=PolicyCardSlot.wildcard,
				requiredCivic=CivicType.guilds,
				obsoleteCivic=CivicType.capitalism,
				replace=[],
				flavors=[]
			)
		if self == PolicyCardType.chivalry:
			# https://civilization.fandom.com/wiki/Chivalry_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_CHIVALRY_TITLE",
				bonus="TXT_KEY_POLICY_CARD_CHIVALRY_BONUS",  #
				slot=PolicyCardSlot.military,
				requiredCivic=CivicType.divineRight,
				obsoleteCivic=CivicType.totalitarianism,
				replace=[],
				flavors=[]
			)
		if self == PolicyCardType.gothicArchitecture:
			# https://civilization.fandom.com/wiki/Gothic_Architecture_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_GOTHIC_ARCHITECTURE_TITLE",
				bonus="TXT_KEY_POLICY_CARD_GOTHIC_ARCHITECTURE_BONUS",  #
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.divineRight,
				obsoleteCivic=CivicType.civilEngineering,
				replace=[],
				flavors=[]
			)
		if self == PolicyCardType.civilPrestige:
			# https://civilization.fandom.com/wiki/Civil_Prestige_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_CIVIL_PRESTIGE_TITLE",
				bonus="TXT_KEY_POLICY_CARD_CIVIL_PRESTIGE_BONUS",
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.civilService,
				obsoleteCivic=None,
				replace=[],
				flavors=[]
			)

		# renaissance
		if self == PolicyCardType.colonialOffices:
			# https://civilization.fandom.com/wiki/Colonial_Offices_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_COLONIAL_OFFICE_TITLE",
				bonus="TXT_KEY_POLICY_CARD_COLONIAL_OFFICE_BONUS",
				slot=PolicyCardSlot.diplomatic,
				requiredCivic=CivicType.exploration,
				obsoleteCivic=None,
				replace=[PolicyCardType.urbanPlanning],
				flavors=[]
			)
		if self == PolicyCardType.invention:
			# https://civilization.fandom.com/wiki/Invention_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_INVENTION_TITLE",
				bonus="TXT_KEY_POLICY_CARD_INVENTION_BONUS",
				slot=PolicyCardSlot.wildcard,
				requiredCivic=CivicType.humanism,
				obsoleteCivic=None,
				replace=[PolicyCardType.revelation],
				flavors=[]
			)
		if self == PolicyCardType.frescoes:
			# https://civilization.fandom.com/wiki/Frescoes_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_FRESCOES_TITLE",
				bonus="TXT_KEY_POLICY_CARD_FRESCOES_BONUS",
				slot=PolicyCardSlot.wildcard,
				requiredCivic=CivicType.humanism,
				obsoleteCivic=None,
				replace=[PolicyCardType.revelation],
				flavors=[]
			)
		# machiavellianism
		# warsOfReligion
		# simultaneum
		# religiousOrders
		if self == PolicyCardType.logistics:
			# https://civilization.fandom.com/wiki/Logistics_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_LOGISTICS_TITLE",
				bonus="TXT_KEY_POLICY_CARD_LOGISTICS_BONUS",
				slot=PolicyCardSlot.military,
				requiredCivic=CivicType.mercantilism,
				obsoleteCivic=None,
				replace=[],
				flavors=[]
			)
		if self == PolicyCardType.triangularTrade:
			# https://civilization.fandom.com/wiki/Triangular_Trade_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_TRIANGULAR_TRADE_TITLE",
				bonus="TXT_KEY_POLICY_CARD_TRIANGULAR_TRADE_BONUS",
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.mercantilism,
				obsoleteCivic=CivicType.globalization,
				replace=[PolicyCardType.ecommerce],
				flavors=[]
			)
		# drillManuals
		# rationalism
		# freeMarket
		if self == PolicyCardType.liberalism:
			# https://civilization.fandom.com/wiki/Liberalism_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_LIBERALISM_TITLE",
				bonus="TXT_KEY_POLICY_CARD_LIBERALISM_BONUS",
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.enlightenment,
				obsoleteCivic=None,
				replace=[PolicyCardType.newDeal],
				flavors=[]
			)
		# wisselbanken
		if self == PolicyCardType.pressGangs:
			# https://civilization.fandom.com/wiki/Press_Gangs_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_PRESS_GANGS_TITLE",
				bonus="TXT_KEY_POLICY_CARD_PRESS_GANGS_BONUS",
				slot=PolicyCardSlot.military,
				requiredCivic=CivicType.exploration,
				obsoleteCivic=CivicType.coldWar,
				replace=[PolicyCardType.maritimeIndustries],
				flavors=[]
			)

		# industrial
		# nativeConquest
		if self == PolicyCardType.grandeArmee:
			# https://civilization.fandom.com/wiki/Grande_Arm%C3%A9e_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_GRANDE_ARMEE_TITLE",
				bonus="TXT_KEY_POLICY_CARD_GRANDE_ARMEE_BONUS",
				slot=PolicyCardSlot.military,
				requiredCivic=CivicType.nationalism,
				obsoleteCivic=None,
				replace=[PolicyCardType.militaryFirst],
				flavors=[]
			)
		# nationalIdentity
		# colonialTaxes
		# raj
		# publicWorks
		# skyscrapers,
		# grandOpera
		# symphonies
		# publicTransport
		if self == PolicyCardType.militaryResearch:
			# https://civilization.fandom.com/wiki/Military_Research_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_MILITARY_RESEARCH_TITLE",
				bonus="TXT_KEY_POLICY_CARD_MILITARY_RESEARCH_BONUS",
				slot=PolicyCardSlot.military,
				requiredCivic=CivicType.urbanization,
				obsoleteCivic=None,
				replace=[PolicyCardType.integratedSpaceCell],
				flavors=[]
			)
		# forceModernization
		# totalWar
		if self == PolicyCardType.expropriation:
			# https://civilization.fandom.com/wiki/Expropriation_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_EXPROPRIATION_TITLE",
				bonus="TXT_KEY_POLICY_CARD_EXPROPRIATION_BONUS",
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.scorchedEarth,
				obsoleteCivic=None,
				replace=[PolicyCardType.colonization, PolicyCardType.landSurveyors],
				flavors=[]
			)
		if self == PolicyCardType.militaryOrganization:
			# https://civilization.fandom.com/wiki/Military_Organization_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_MILITARY_ORGANIZATION_TITLE",
				bonus="TXT_KEY_POLICY_CARD_MILITARY_ORGANIZATION_BONUS",
				slot=PolicyCardSlot.wildcard,
				requiredCivic=CivicType.scorchedEarth,
				obsoleteCivic=None,
				replace=[PolicyCardType.strategos],
				flavors=[]
			)

		# ////////////////////
		# modern

		if self == PolicyCardType.resourceManagement:
			# https://civilization.fandom.com/wiki/Resource_Management_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_RESOURCE_MANAGEMENT_TITLE",
				bonus="TXT_KEY_POLICY_CARD_RESOURCE_MANAGEMENT_BONUS",
				slot=PolicyCardSlot.military,
				requiredCivic=CivicType.conservation,
				obsoleteCivic=None,
				replace=[],
				flavors=[]
			)
		if self == PolicyCardType.propaganda:
			# https://civilization.fandom.com/wiki/Propaganda_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_PROPAGANDA_TITLE",
				bonus="TXT_KEY_POLICY_CARD_PROPAGANDA_BONUS",
				slot=PolicyCardSlot.military,
				requiredCivic=CivicType.massMedia,
				obsoleteCivic=None,
				replace=[PolicyCardType.retainers],
				flavors=[]
			)
		if self == PolicyCardType.leveeEnMasse:
			# https://civilization.fandom.com/wiki/Lev%C3%A9e_en_Masse_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_LEVEE_EN_MASSE_TITLE",
				bonus="TXT_KEY_POLICY_CARD_LEVEE_EN_MASSE_BONUS",
				slot=PolicyCardSlot.military,
				requiredCivic=CivicType.mobilization,
				obsoleteCivic=None,
				replace=[PolicyCardType.conscription],
				flavors=[]
			)
		if self == PolicyCardType.laissezFaire:
			# https://civilization.fandom.com/wiki/Laissez-Faire_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_LAISSEZ_FAIRE_TITLE",
				bonus="TXT_KEY_POLICY_CARD_LAISSEZ_FAIRE_BONUS",
				slot=PolicyCardSlot.wildcard,
				requiredCivic=CivicType.capitalism,
				obsoleteCivic=None,
				replace=[PolicyCardType.travelingMerchants],
				flavors=[]
			)
		if self == PolicyCardType.marketEconomy:
			# https://civilization.fandom.com/wiki/Market_Economy_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_MARKET_ECONOMY_TITLE",
				bonus="TXT_KEY_POLICY_CARD_MARKET_ECONOMY_BONUS",
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.capitalism,
				obsoleteCivic=None,
				replace=[PolicyCardType.tradeConfederation],
				flavors=[]
			)
		if self == PolicyCardType.policeState:
			# https://civilization.fandom.com/wiki/Police_State_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_POLICY_STATE_TITLE",
				bonus="TXT_KEY_POLICY_CARD_POLICY_STATE_BONUS",
				slot=PolicyCardSlot.diplomatic,
				requiredCivic=CivicType.ideology,
				obsoleteCivic=None,
				replace=[],
				flavors=[]
			)
		if self == PolicyCardType.nobelPrize:
			# https://civilization.fandom.com/wiki/Nobel_Prize_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_NOBEL_PRIZE_TITLE",
				bonus="TXT_KEY_POLICY_CARD_NOBEL_PRIZE_BONUS",
				slot=PolicyCardSlot.wildcard,
				requiredCivic=CivicType.nuclearProgram,
				obsoleteCivic=None,
				replace=[PolicyCardType.inspiration],
				flavors=[]
			)
		# scienceFoundations
		# nuclearEspionage
		# economicUnion
		if self == PolicyCardType.theirFinestHour:
			# https://civilization.fandom.com/wiki/Their_Finest_Hour_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_THEIR_FINEST_HOUR_TITLE",
				bonus="TXT_KEY_POLICY_CARD_THEIR_FINEST_HOUR_BONUS",
				slot=PolicyCardSlot.wildcard,
				requiredCivic=CivicType.suffrage,
				obsoleteCivic=None,
				replace=[PolicyCardType.strategicAirForce],
				flavors=[]
			)
		# arsenalOfDemocracy
		if self == PolicyCardType.newDeal:
			# https://civilization.fandom.com/wiki/New_Deal_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_NEW_DEAL_TITLE",
				bonus="TXT_KEY_POLICY_CARD_NEW_DEAL_BONUS",
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.suffrage,
				obsoleteCivic=None,
				replace=[
					PolicyCardType.medinaQuarter,
					PolicyCardType.liberalism
				],
				flavors=[]
			)
		if self == PolicyCardType.lightningWarfare:
			# https://civilization.fandom.com/wiki/Lightning_Warfare_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_LIGHTNING_WARFARE_TITLE",
				bonus="TXT_KEY_POLICY_CARD_LIGHTNING_WARFARE_BONUS",
				slot=PolicyCardSlot.military,
				requiredCivic=CivicType.totalitarianism,
				obsoleteCivic=None,
				replace=[PolicyCardType.chivalry, PolicyCardType.maneuver],
				flavors=[]
			)
		if self == PolicyCardType.thirdAlternative:
			# https://civilization.fandom.com/wiki/Third_Alternative_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_THIRD_ALTERNATIVE_TITLE",
				bonus="TXT_KEY_POLICY_CARD_THIRD_ALTERNATIVE_BONUS",
				slot=PolicyCardSlot.military,
				requiredCivic=CivicType.totalitarianism,
				obsoleteCivic=None,
				replace=[],
				flavors=[]
			)
		# martialLaw
		# gunboatDiplomacy
		if self == PolicyCardType.fiveYearPlan:
			# https://civilization.fandom.com/wiki/Five-Year_Plan_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_FIVE_YEAR_PLAN_TITLE",
				bonus="TXT_KEY_POLICY_CARD_FIVE_YEAR_PLAN_BONUS",
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.classStruggle,
				obsoleteCivic=None,
				replace=[PolicyCardType.craftsmen, PolicyCardType.naturalPhilosophy],
				flavors=[]
			)
		if self == PolicyCardType.collectivization:
			# https://civilization.fandom.com/wiki/Collectivization_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_COLLECTIVIZATION_TITLE",
				bonus="TXT_KEY_POLICY_CARD_COLLECTIVIZATION_BONUS",
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.classStruggle,
				obsoleteCivic=None,
				replace=[],
				flavors=[]
			)
		# patrioticWar
		# defenseOfTheMotherland

		# atomic
		# cryptography
		if self == PolicyCardType.internationalWaters:
			# https://civilization.fandom.com/wiki/International_Waters_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_INTERNATIONAL_WATERS_TITLE",
				bonus="TXT_KEY_POLICY_CARD_INTERNATIONAL_WATERS_BONUS",
				slot=PolicyCardSlot.military,
				requiredCivic=CivicType.coldWar,
				obsoleteCivic=None,
				replace=[PolicyCardType.maritimeIndustries, PolicyCardType.pressGangs],
				flavors=[]
			)
		# containment
		# heritageTourism
		# sportsMedia
		if self == PolicyCardType.militaryFirst:
			# https://civilization.fandom.com/wiki/Military_First_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_MILITARY_FIRST_TITLE",
				bonus="TXT_KEY_POLICY_CARD_MILITARY_FIRST_BONUS",
				slot=PolicyCardSlot.military,
				requiredCivic=CivicType.rapidDeployment,
				obsoleteCivic=None,
				replace=[PolicyCardType.grandeArmee],
				flavors=[]
			)
		# satelliteBroadcasts
		# musicCensorship
		if self == PolicyCardType.integratedSpaceCell:
			# https://civilization.fandom.com/wiki/Integrated_Space_Cell_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_INTEGRATED_SPACE_CELL_TITLE",
				bonus="TXT_KEY_POLICY_CARD_INTEGRATED_SPACE_CELL_BONUS",
				slot=PolicyCardSlot.military,
				requiredCivic=CivicType.spaceRace,
				obsoleteCivic=None,
				replace=[PolicyCardType.militaryResearch],
				flavors=[]
			)
		# secondStrikeCapability

		# dark age
		if self == PolicyCardType.automatedWorkforce:
			# https://civilization.fandom.com/wiki/Automated_Workforce_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_AUTOMATED_WORKFORCE_TITLE",
				bonus="TXT_KEY_POLICY_CARD_AUTOMATED_WORKFORCE_BONUS",
				slot=PolicyCardSlot.wildcard,
				requiredCivic=None,
				obsoleteCivic=None,
				startEra=EraType.information,
				endEra=EraType.future,
				replace=[],
				flavors=[],
				requiresDarkAge=True
			)
		if self == PolicyCardType.collectivism:
			# https://civilization.fandom.com/wiki/Collectivism_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_COLLECTIVISM_TITLE",
				bonus="TXT_KEY_POLICY_CARD_COLLECTIVISM_BONUS",
				slot=PolicyCardSlot.wildcard,
				requiredCivic=None,
				obsoleteCivic=None,
				startEra=EraType.modern,
				endEra=EraType.information,
				replace=[],
				flavors=[],
				requiresDarkAge=True
			)
		# cyberWarfare
		if self == PolicyCardType.decentralization:
			# https://civilization.fandom.com/wiki/Decentralization_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_DECENTRALIZATION_TITLE",
				bonus="TXT_KEY_POLICY_CARD_DECENTRALIZATION_BONUS",
				slot=PolicyCardSlot.wildcard,
				requiredCivic=None,
				obsoleteCivic=None,
				startEra=EraType.classical,
				endEra=EraType.renaissance,
				replace=[],
				flavors=[],
				requiresDarkAge=True
			)
		if self == PolicyCardType.despoticPaternalism:
			# https://civilization.fandom.com/wiki/Despotic_Paternalism_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_DESPOTIC_PATERNALISM_TITLE",
				bonus="TXT_KEY_POLICY_CARD_DESPOTIC_PATERNALISM_BONUS",
				slot=PolicyCardSlot.wildcard,
				requiredCivic=None,
				obsoleteCivic=None,
				startEra=EraType.industrial,
				endEra=EraType.information,
				replace=[],
				flavors=[],
				requiresDarkAge=True
			)
		# disinformationCampaign
		if self == PolicyCardType.eliteForces:
			# https://civilization.fandom.com/wiki/Elite_Forces_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_ELITE_FORCES_TITLE",
				bonus="TXT_KEY_POLICY_CARD_ELITE_FORCES_BONUS",
				slot=PolicyCardSlot.wildcard,
				requiredCivic=None,
				obsoleteCivic=None,
				startEra=EraType.industrial,
				endEra=EraType.information,
				replace=[],
				flavors=[],
				requiresDarkAge=True
			)
		# flowerPower
		# inquisition
		if self == PolicyCardType.isolationism:
			# https://civilization.fandom.com/wiki/Isolationism_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_ISOLATIONISM_TITLE",
				bonus="TXT_KEY_POLICY_CARD_ISOLATIONISM_BONUS",
				slot=PolicyCardSlot.wildcard,
				requiredCivic=None,
				obsoleteCivic=None,
				startEra=EraType.classical,
				endEra=EraType.industrial,
				replace=[],
				flavors=[],
				requiresDarkAge=True
			)
		# lettersOfMarque
		if self == PolicyCardType.monasticism:
			# https://civilization.fandom.com/wiki/Monasticism_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_MONASTICISM_TITLE",
				bonus="TXT_KEY_POLICY_CARD_MONASTICISM_BONUS",
				slot=PolicyCardSlot.wildcard,
				requiredCivic=None,
				obsoleteCivic=None,
				startEra=EraType.classical,
				endEra=EraType.medieval,
				replace=[],
				flavors=[],
				requiresDarkAge=True
			)
		if self == PolicyCardType.robberBarons:
			# https://civilization.fandom.com/wiki/Robber_Barons_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_ROBBER_BARONS_TITLE",
				bonus="TXT_KEY_POLICY_CARD_ROBBER_BARONS_BONUS",
				slot=PolicyCardSlot.wildcard,
				requiredCivic=None,
				obsoleteCivic=None,
				startEra=EraType.industrial,
				endEra=EraType.information,
				replace=[],
				flavors=[],
				requiresDarkAge=True
			)
		# rogueState
		# samoderzhaviye
		# softTargets
		if self == PolicyCardType.twilightValor:
			# https://civilization.fandom.com/wiki/Twilight_Valor_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_TWILIGHT_VALOR_TITLE",
				bonus="TXT_KEY_POLICY_CARD_TWILIGHT_VALOR_BONUS",
				slot=PolicyCardSlot.wildcard,
				requiredCivic=None,
				obsoleteCivic=None,
				startEra=EraType.classical,
				endEra=EraType.renaissance,
				replace=[],
				flavors=[],
				requiresDarkAge=True
			)

		# information
		if self == PolicyCardType.strategicAirForce:
			# https://civilization.fandom.com/wiki/Strategic_Air_Force_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_STRATEGIC_AIR_FORCE_TITLE",
				bonus="TXT_KEY_POLICY_CARD_STRATEGIC_AIR_FORCE_BONUS",
				slot=PolicyCardSlot.military,
				requiredCivic=CivicType.globalization,
				obsoleteCivic=None,
				replace=[PolicyCardType.theirFinestHour],
				flavors=[]
			)
		if self == PolicyCardType.ecommerce:
			# https://civilization.fandom.com/wiki/Ecommerce_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_ECOMMERCE_TITLE",
				bonus="TXT_KEY_POLICY_CARD_ECOMMERCE_BONUS",
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.globalization,
				obsoleteCivic=None,
				replace=[PolicyCardType.triangularTrade],
				flavors=[]
			)
		if self == PolicyCardType.internationalSpaceAgency:
			# https://civilization.fandom.com/wiki/International_Space_Agency_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_INTERNATIONAL_SPACE_AGENCY_TITLE",
				bonus="TXT_KEY_POLICY_CARD_INTERNATIONAL_SPACE_AGENCY_BONUS",
				slot=PolicyCardSlot.diplomatic,
				requiredCivic=CivicType.globalization,
				obsoleteCivic=None,
				replace=[],
				flavors=[]
			)
		# onlineCommunities
		if self == PolicyCardType.collectiveActivism:
			# https://civilization.fandom.com/wiki/Collective_Activism_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_COLLECTIVE_ACTIVISM_TITLE",
				bonus="TXT_KEY_POLICY_CARD_COLLECTIVE_ACTIVISM_BONUS",
				slot=PolicyCardSlot.diplomatic,
				requiredCivic=CivicType.socialMedia,
				obsoleteCivic=None,
				replace=[],
				flavors=[]
			)
		if self == PolicyCardType.afterActionReports:
			# https://civilization.fandom.com/wiki/After_Action_Reports_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_AFTER_ACTION_REPORTS_TITLE",
				bonus="TXT_KEY_POLICY_CARD_AFTER_ACTION_REPORTS_BONUS",
				slot=PolicyCardSlot.military,
				requiredCivic=CivicType.rapidDeployment,
				obsoleteCivic=None,
				replace=[],
				flavors=[]
			)
		if self == PolicyCardType.communicationsOffice:
			# https://civilization.fandom.com/wiki/Communications_Office_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_COMMUNICATIONS_OFFICE_TITLE",
				bonus="TXT_KEY_POLICY_CARD_COMMUNICATIONS_OFFICE_BONUS",
				slot=PolicyCardSlot.diplomatic,
				requiredCivic=CivicType.socialMedia,
				obsoleteCivic=None,
				replace=[PolicyCardType.praetorium],
				flavors=[]
			)
		# aerospaceContractors

		raise AttributeError(f'cant get data for policy card {self}')
