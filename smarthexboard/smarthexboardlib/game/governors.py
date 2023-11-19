from smarthexboard.smarthexboardlib.game.flavors import Flavor, FlavorType
from smarthexboard.smarthexboardlib.map import constants
from smarthexboard.smarthexboardlib.core.base import ExtendedEnum, InvalidEnumError


class GovernorTitleType:
	pass


class GovernorTitleTypeData:
	def __init__(self, name: str, effects: [str], tier: int, requiredOr: [GovernorTitleType], flavors: [Flavor]):
		self.name = name
		self.effects = effects
		self.tier = tier
		self.requiredOr = requiredOr
		self.flavors = flavors
		

class GovernorTitleType(ExtendedEnum):
	none = 'none'

	# reyna
	landAcquisition = 'landAcquisition'
	harbormaster = 'landAcquisition'
	forestryManagement = 'forestryManagement'
	taxCollector = 'taxCollector'
	contractor = 'contractor'
	renewableSubsidizer = 'renewableSubsidizer'

	# victor
	redoubt = 'redoubt'
	garrisonCommander = 'garrisonCommander'
	defenseLogistics = 'defenseLogistics'
	embrasure = 'embrasure'
	airDefenseInitiative = 'airDefenseInitiative'
	armsRaceProponent = 'armsRaceProponent'

	# amani
	messenger = 'messenger'
	emissary = 'emissary'
	affluence = 'affluence'
	localInformants = 'localInformants'
	foreignInvestor = 'foreignInvestor'
	puppeteer = 'puppeteer'

	# magnus
	groundbreaker = 'groundbreaker'
	surplusLogistics = 'surplusLogistics'
	provision = 'provision'
	industrialist = 'industrialist'
	blackMarketeer = 'blackMarketeer'
	verticalIntegration = 'verticalIntegration'

	# moksha
	bishop = 'bishop'
	grandInquisitor = 'grandInquisitor'
	layingOnOfHands = 'layingOnOfHands'
	citadelOfGod = 'citadelOfGod'
	patronSaint = 'patronSaint'
	divineArchitect = 'divineArchitect'

	# Liang
	guildmaster = 'guildmaster'
	zoningCommissioner = 'zoningCommissioner'
	aquaculture = 'aquaculture'
	reinforcedMaterials = 'reinforcedMaterials'
	waterWorks = 'waterWorks'
	parksAndRecreation = 'parksAndRecreation'

	# Pingala
	librarian = 'librarian'
	connoisseur = 'connoisseur'
	researcher = 'researcher'
	grants = 'grants'
	spaceInitiative = 'spaceInitiative'
	curator = 'curator'

	def name(self) -> str:
		return self._data().name

	def _data(self) -> GovernorTitleTypeData:
		if self == GovernorTitleType.none:
			return GovernorTitleTypeData(
				name="",
				effects=[],
				tier=0,
				requiredOr=[],
				flavors=[]  # not needed
			)

		# Reyna
		if self == GovernorTitleType.landAcquisition:
			return GovernorTitleTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_REYNA_LAND_ACQUISITION_TITLE",
				effects=[
					"TXT_KEY_GOVERNMENT_GOVERNOR_REYNA_ACQUISITION_EFFECT1",
					"TXT_KEY_GOVERNMENT_GOVERNOR_REYNA_ACQUISITION_EFFECT2"
				],
				tier=0,
				requiredOr=[],
				flavors=[]  # not needed
			)
		elif self == GovernorTitleType.harbormaster:
			return GovernorTitleTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_REYNA_HARBORMASTER_TITLE",
				effects=[
					"TXT_KEY_GOVERNMENT_GOVERNOR_REYNA_HARBORMASTER_EFFECT1"
				],
				tier=1,
				requiredOr=[],
				flavors=[Flavor(FlavorType.gold, value=6), Flavor(FlavorType.tileImprovement, value=4)]
			)
		elif self == GovernorTitleType.forestryManagement:
			return GovernorTitleTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_REYNA_FORESTRY_MANAGEMENT_TITLE",
				effects=[
					"TXT_KEY_GOVERNMENT_GOVERNOR_REYNA_FORESTRY_MANAGEMENT_EFFECT1",
					"TXT_KEY_GOVERNMENT_GOVERNOR_REYNA_FORESTRY_MANAGEMENT_EFFECT2"
				],
				tier=1,
				requiredOr=[],
				flavors=[Flavor(FlavorType.gold, value=6), Flavor(FlavorType.amenities, value=4)]
			)
		elif self == GovernorTitleType.taxCollector:
			return GovernorTitleTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_REYNA_TAX_COLLECTOR_TITLE",
				effects=[
					"TXT_KEY_GOVERNMENT_GOVERNOR_REYNA_TAX_COLLECTOR_EFFECT1"
				],
				tier=2,
				requiredOr=[GovernorTitleType.harbormaster, GovernorTitleType.forestryManagement],
				flavors=[Flavor(FlavorType.gold, value=6)]
			)
		elif self == GovernorTitleType.contractor:
			return GovernorTitleTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_REYNA_CONTRACTOR_TITLE",
				effects=[
					"TXT_KEY_GOVERNMENT_GOVERNOR_REYNA_CONTRACTOR_EFFECT1"
				],
				tier=3,
				requiredOr=[GovernorTitleType.taxCollector],
				flavors=[Flavor(FlavorType.growth, value=6)]
			)
		elif self == GovernorTitleType.renewableSubsidizer:
			return GovernorTitleTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_REYNA_RENEWABLE_SUBSIDIZER_TITLE",
				effects=[
					"TXT_KEY_GOVERNMENT_GOVERNOR_REYNA_RENEWABLE_SUBSIDIZER_EFFECT1"
				],
				tier=3,
				requiredOr=[GovernorTitleType.taxCollector],
				flavors=[Flavor(FlavorType.energy, value=6), Flavor(FlavorType.tileImprovement, value=4)]
			)

			# ----------------------------------
			# Victor

		elif self == GovernorTitleType.redoubt:
			return GovernorTitleTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_VICTOR_REDOUBT_TITLE",
				effects=[
					"TXT_KEY_GOVERNMENT_GOVERNOR_VICTOR_REDOUBT_EFFECT1",
					"TXT_KEY_GOVERNMENT_GOVERNOR_VICTOR_REDOUBT_EFFECT2"
				],
				tier=0,
				requiredOr=[],
				flavors=[]  # not needed
			)
		elif self == GovernorTitleType.garrisonCommander:
			return GovernorTitleTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_VICTOR_GARRISON_COMMANDER_TITLE",
				effects=[
					"TXT_KEY_GOVERNMENT_GOVERNOR_VICTOR_GARRISON_COMMANDER_EFFECT1",
					"TXT_KEY_GOVERNMENT_GOVERNOR_VICTOR_GARRISON_COMMANDER_EFFECT2"
				],
				tier=1,
				requiredOr=[],
				flavors=[Flavor(FlavorType.defense, value=6), Flavor(FlavorType.cityDefense, value=4)]
			)
		elif self == GovernorTitleType.defenseLogistics:
			return GovernorTitleTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_VICTOR_DEFENSE_LOGISTICS_TITLE",
				effects=[
					"TXT_KEY_GOVERNMENT_GOVERNOR_VICTOR_DEFENSE_LOGISTICS_EFFECT1",
					"TXT_KEY_GOVERNMENT_GOVERNOR_VICTOR_DEFENSE_LOGISTICS_EFFECT2"
				],
				tier=1,
				requiredOr=[],
				flavors=[Flavor(FlavorType.offense, value=5), Flavor(FlavorType.cityDefense, value=6)]
			)
		elif self == GovernorTitleType.embrasure:
			return GovernorTitleTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_VICTOR_EMBRASURE_TITLE",
				effects=[
					"TXT_KEY_GOVERNMENT_GOVERNOR_VICTOR_EMBRASURE_EFFECT1",
					"TXT_KEY_GOVERNMENT_GOVERNOR_VICTOR_EMBRASURE_EFFECT2"
				],
				tier=2,
				requiredOr=[GovernorTitleType.garrisonCommander, GovernorTitleType.defenseLogistics],
				flavors=[Flavor(FlavorType.offense, value=6), Flavor(FlavorType.cityDefense, value=8)]
			)
		elif self == GovernorTitleType.airDefenseInitiative:
			return GovernorTitleTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_VICTOR_AIR_DEFENSE_INITIATIVE_TITLE",
				effects=[
					"TXT_KEY_GOVERNMENT_GOVERNOR_VICTOR_AIR_DEFENSE_INITIATIVE_EFFECT1"
				],
				tier=3,
				requiredOr=[GovernorTitleType.embrasure],
				flavors=[Flavor(FlavorType.defense, value=4), Flavor(FlavorType.cityDefense, value=6)]
			)
		elif self == GovernorTitleType.armsRaceProponent:
			return GovernorTitleTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_VICTOR_ARMS_RACE_PROPONENT_TITLE",
				effects=[
					"TXT_KEY_GOVERNMENT_GOVERNOR_VICTOR_ARMS_RACE_PROPONENT_EFFECT1"
				],
				tier=3,
				requiredOr=[GovernorTitleType.embrasure],
				flavors=[Flavor(FlavorType.defense, value=6), Flavor(FlavorType.cityDefense, value=4)]
			)

			# -------------------
			# Amani
		elif self == GovernorTitleType.messenger:
			return GovernorTitleTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_AMANI_MESSENGER_TITLE",
				effects=[
					"TXT_KEY_GOVERNMENT_GOVERNOR_AMANI_MESSENGER_EFFECT1"
				],
				tier=0,
				requiredOr=[],
				flavors=[]  # not needed
			)
		elif self == GovernorTitleType.emissary:
			return GovernorTitleTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_AMANI_EMISSARY_TITLE",
				effects=[
					"TXT_KEY_GOVERNMENT_GOVERNOR_AMANI_EMISSARY_EFFECT1"
				],
				tier=1,
				requiredOr=[],
				flavors=[Flavor(FlavorType.diplomacy, value=6)]
			)
		elif self == GovernorTitleType.affluence:
			return GovernorTitleTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_AMANI_AFFLUENCE_TITLE",
				effects=[
					"TXT_KEY_GOVERNMENT_GOVERNOR_AMANI_AFFLUENCE_EFFECT1"
				],
				tier=1,
				requiredOr=[],
				flavors=[Flavor(FlavorType.amenities, value=6)]
			)
		elif self == GovernorTitleType.localInformants:
			return GovernorTitleTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_AMANI_LOCAL_INFORMANTS_TITLE",
				effects=[
					"TXT_KEY_GOVERNMENT_GOVERNOR_AMANI_LOCAL_INFORMANTS_EFFECT1"
				],
				tier=2,
				requiredOr=[GovernorTitleType.emissary],
				flavors=[Flavor(FlavorType.diplomacy, value=6), Flavor(FlavorType.cityDefense, value=4)]
			)
		elif self == GovernorTitleType.foreignInvestor:
			return GovernorTitleTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_AMANI_FOREIGN_INVESTOR_TITLE",
				effects=[
					"TXT_KEY_GOVERNMENT_GOVERNOR_AMANI_FOREIGN_INVESTOR_EFFECT1",
					"TXT_KEY_GOVERNMENT_GOVERNOR_AMANI_FOREIGN_INVESTOR_EFFECT2"
				],
				tier=2,
				requiredOr=[GovernorTitleType.affluence],
				flavors=[
					Flavor(FlavorType.tileImprovement, value=6),
					Flavor(FlavorType.defense, value=4),
					Flavor(FlavorType.offense, value=5)
				]
			)
		elif self == GovernorTitleType.puppeteer:
			return GovernorTitleTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_AMANI_PUPPETEER_TITLE",
				effects=[
					"TXT_KEY_GOVERNMENT_GOVERNOR_AMANI_PUPPETEER_EFFECT1"
				],
				tier=3,
				requiredOr=[GovernorTitleType.localInformants, GovernorTitleType.foreignInvestor],
				flavors=[Flavor(FlavorType.diplomacy, value=6)]
			)

			# ----------------------------------
			# Magnus
		elif self == GovernorTitleType.groundbreaker:
			return GovernorTitleTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_MAGNUS_GROUNDBREAKER_TITLE",
				effects=[
					"TXT_KEY_GOVERNMENT_GOVERNOR_MAGNUS_GROUNDBREAKER_EFFECT1"
				],
				tier=0,
				requiredOr=[],
				flavors=[]  # not needed
			)
		elif self == GovernorTitleType.surplusLogistics:
			return GovernorTitleTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_MAGNUS_SURPLUS_LOGISTICS_TITLE",
				effects=[
					"TXT_KEY_GOVERNMENT_GOVERNOR_MAGNUS_SURPLUS_LOGISTICS_EFFECT1",
					"TXT_KEY_GOVERNMENT_GOVERNOR_MAGNUS_SURPLUS_LOGISTICS_EFFECT2"
				],
				tier=1,
				requiredOr=[],
				flavors=[Flavor(FlavorType.growth, value=6), Flavor(FlavorType.diplomacy, value=3)]
			)
		elif self == GovernorTitleType.provision:
			return GovernorTitleTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_MAGNUS_PROVISION_TITLE",
				effects=[
					"TXT_KEY_GOVERNMENT_GOVERNOR_MAGNUS_PROVISION_EFFECT1"
				],
				tier=1,
				requiredOr=[],
				flavors=[Flavor(FlavorType.growth, value=8)]
			)
		elif self == GovernorTitleType.industrialist:
			return GovernorTitleTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_MAGNUS_INDUSTRIALIST_TITLE",
				effects=[
					"TXT_KEY_GOVERNMENT_GOVERNOR_MAGNUS_INDUSTRIALIST_EFFECT1"
				],
				tier=2,
				requiredOr=[GovernorTitleType.surplusLogistics],
				flavors=[Flavor(FlavorType.energy, value=6)]
			)
		elif self == GovernorTitleType.blackMarketeer:
			return GovernorTitleTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_MAGNUS_BLACK_MARKETEER_TITLE",
				effects=[
					"TXT_KEY_GOVERNMENT_GOVERNOR_MAGNUS_BLACK_MARKETEER_EFFECT1"
				],
				tier=2,
				requiredOr=[GovernorTitleType.provision],
				flavors=[Flavor(FlavorType.production, value=4)]
			)
		elif self == GovernorTitleType.verticalIntegration:
			return GovernorTitleTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_MAGNUS_VERTICAL_INTEGRATION_TITLE",
				effects=[
					"TXT_KEY_GOVERNMENT_GOVERNOR_MAGNUS_VERTICAL_INTEGRATION_EFFECT1"
				],
				tier=3,
				requiredOr=[GovernorTitleType.industrialist, GovernorTitleType.blackMarketeer],
				flavors=[Flavor(FlavorType.production, value=6)]
			)

			# -----------------------
			# moksha
		elif self == GovernorTitleType.bishop:
			return GovernorTitleTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_MOKSHA_BISHOP_TITLE",
				effects=[
					"TXT_KEY_GOVERNMENT_GOVERNOR_MOKSHA_BISHOP_EFFECT1",
					"TXT_KEY_GOVERNMENT_GOVERNOR_MOKSHA_BISHOP_EFFECT2"
				],
				tier=0,
				requiredOr=[],
				flavors=[]  # not needed
			)
		elif self == GovernorTitleType.grandInquisitor:
			return GovernorTitleTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_MOKSHA_GRAD_INQUISITOR_TITLE",
				effects=[
					"TXT_KEY_GOVERNMENT_GOVERNOR_MOKSHA_GRAD_INQUISITOR_EFFECT1"
				],
				tier=1,
				requiredOr=[],
				flavors=[Flavor(FlavorType.religion, value=6)]
			)
		elif self == GovernorTitleType.layingOnOfHands:
			return GovernorTitleTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_MOKSHA_LAYING_ON_OF_HANDS_TITLE",
				effects=[
					"TXT_KEY_GOVERNMENT_GOVERNOR_MOKSHA_LAYING_ON_OF_HANDS_EFFECT1"
				],
				tier=1,
				requiredOr=[],
				flavors=[Flavor(FlavorType.religion, value=4), Flavor(FlavorType.defense, value=4)]
			)
		elif self == GovernorTitleType.citadelOfGod:
			return GovernorTitleTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_MOKSHA_CITADEL_OF_GOD_TITLE",
				effects=[
					"TXT_KEY_GOVERNMENT_GOVERNOR_MOKSHA_CITADEL_OF_GOD_EFFECT1",
					"TXT_KEY_GOVERNMENT_GOVERNOR_MOKSHA_CITADEL_OF_GOD_EFFECT2"
				],
				tier=2,
				requiredOr=[GovernorTitleType.grandInquisitor, GovernorTitleType.layingOnOfHands],
				flavors=[Flavor(FlavorType.religion, value=5)]
			)
		elif self == GovernorTitleType.patronSaint:
			return GovernorTitleTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_MOKSHA_PATRON_SAINT_TITLE",
				effects=[
					"TXT_KEY_GOVERNMENT_GOVERNOR_MOKSHA_PATRON_SAINT_EFFECT1"
				],
				tier=3,
				requiredOr=[GovernorTitleType.citadelOfGod],
				flavors=[Flavor(FlavorType.religion, value=5)]
			)
		elif self == GovernorTitleType.divineArchitect:
			return GovernorTitleTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_MOKSHA_DIVINE_ARCHITECT_TITLE",
				effects=[
					"TXT_KEY_GOVERNMENT_GOVERNOR_MOKSHA_DIVINE_ARCHITECT_EFFECT1"
				],
				tier=3,
				requiredOr=[GovernorTitleType.citadelOfGod],
				flavors=[Flavor(FlavorType.religion, value=5)]
			)

			# ----------------------------------
			# Liang
		elif self == GovernorTitleType.guildmaster:
			return GovernorTitleTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_LIANG_GUILDMASTER_TITLE",
				effects=[
					"TXT_KEY_GOVERNMENT_GOVERNOR_LIANG_GUILDMASTER_EFFECT1"
				],
				tier=0,
				requiredOr=[],
				flavors=[]  # not needed
			)
		elif self == GovernorTitleType.zoningCommissioner:
			return GovernorTitleTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_LIANG_ZONING_COMMISSIONER_TITLE",
				effects=[
					"TXT_KEY_GOVERNMENT_GOVERNOR_LIANG_ZONING_COMMISSIONER_EFFECT1"
				],
				tier=1,
				requiredOr=[],
				flavors=[Flavor(FlavorType.production, value=4), Flavor(FlavorType.growth, value=3)]
			)
		elif self == GovernorTitleType.aquaculture:
			return GovernorTitleTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_LIANG_AQUACULTURE_TITLE",
				effects=[
					"TXT_KEY_GOVERNMENT_GOVERNOR_LIANG_AQUACULTURE_EFFECT1",
					"TXT_KEY_GOVERNMENT_GOVERNOR_LIANG_AQUACULTURE_EFFECT2",
					"TXT_KEY_GOVERNMENT_GOVERNOR_LIANG_AQUACULTURE_EFFECT3"
				],
				tier=1,
				requiredOr=[],
				flavors=[Flavor(FlavorType.production, value=6), Flavor(FlavorType.growth, value=4)]
			)
		elif self == GovernorTitleType.reinforcedMaterials:
			return GovernorTitleTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_LIANG_REINFORCED_MATERIALS_TITLE",
				effects=[
					"TXT_KEY_GOVERNMENT_GOVERNOR_LIANG_REINFORCED_MATERIALS_EFFECT1"
				],
				tier=2,
				requiredOr=[GovernorTitleType.zoningCommissioner],
				flavors=[Flavor(FlavorType.growth, value=4)]
			)
		elif self == GovernorTitleType.waterWorks:
			return GovernorTitleTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_LIANG_WATER_WORKS_TITLE",
				effects=[
					"TXT_KEY_GOVERNMENT_GOVERNOR_LIANG_WATER_WORKS_EFFECT1",
					"TXT_KEY_GOVERNMENT_GOVERNOR_LIANG_WATER_WORKS_EFFECT2"
				],
				tier=2,
				requiredOr=[GovernorTitleType.aquaculture],
				flavors=[Flavor(FlavorType.growth, value=6)]
			)
		elif self == GovernorTitleType.parksAndRecreation:
			return GovernorTitleTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_LIANG_PARKS_AND_RECREATION_TITLE",
				effects=[
					"TXT_KEY_GOVERNMENT_GOVERNOR_LIANG_PARKS_AND_RECREATION_EFFECT1",
					"TXT_KEY_GOVERNMENT_GOVERNOR_LIANG_PARKS_AND_RECREATION_EFFECT2",
					"TXT_KEY_GOVERNMENT_GOVERNOR_LIANG_PARKS_AND_RECREATION_EFFECT3",
					"TXT_KEY_GOVERNMENT_GOVERNOR_LIANG_PARKS_AND_RECREATION_EFFECT4"
				],
				tier=3,
				requiredOr=[GovernorTitleType.reinforcedMaterials, GovernorTitleType.waterWorks],
				flavors=[
					Flavor(FlavorType.culture, value=6),
					Flavor(FlavorType.amenities, value=4)
				]
			)

			# ----------------------------------
			# Pingala

		elif self == GovernorTitleType.librarian:
			return GovernorTitleTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_PINGALA_LIBRARIAN_TITLE",
				effects=[
					"TXT_KEY_GOVERNMENT_GOVERNOR_PINGALA_LIBRARIAN_EFFECT1"
				],
				tier=0,
				requiredOr=[],
				flavors=[]  # not needed
			)
		elif self == GovernorTitleType.connoisseur:
			return GovernorTitleTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_PINGALA_CONNOISSEUR_TITLE",
				effects=[
					"TXT_KEY_GOVERNMENT_GOVERNOR_PINGALA_CONNOISSEUR_EFFECT1"
				],
				tier=1,
				requiredOr=[],
				flavors=[Flavor(FlavorType.culture, value=8)]
			)
		elif self == GovernorTitleType.researcher:
			return GovernorTitleTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_PINGALA_RESEARCHER_TITLE",
				effects=[
					"TXT_KEY_GOVERNMENT_GOVERNOR_PINGALA_RESEARCHER_EFFECT1"
				],
				tier=1,
				requiredOr=[],
				flavors=[Flavor(FlavorType.science, value=8)]
			)
		elif self == GovernorTitleType.grants:
			return GovernorTitleTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_PINGALA_GRANTS_TITLE",
				effects=[
					"TXT_KEY_GOVERNMENT_GOVERNOR_PINGALA_GRANTS_EFFECT1"
				],
				tier=2,
				requiredOr=[GovernorTitleType.connoisseur, GovernorTitleType.researcher],
				flavors=[Flavor(FlavorType.greatPeople, value=8)]
			)
		elif self == GovernorTitleType.spaceInitiative:
			return GovernorTitleTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_PINGALA_SPACE_INITIATIVE_TITLE",
				effects=[
					"TXT_KEY_GOVERNMENT_GOVERNOR_PINGALA_SPACE_INITIATIVE_EFFECT1"
				],
				tier=3,
				requiredOr=[GovernorTitleType.grants],
				flavors=[Flavor(FlavorType.science, value=6)]
			)
		elif self == GovernorTitleType.curator:
			return GovernorTitleTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_PINGALA_CURATOR_TITLE",
				effects=[
					"TXT_KEY_GOVERNMENT_GOVERNOR_PINGALA_CURATOR_EFFECT1"
				],
				tier=3,
				requiredOr=[GovernorTitleType.grants],
				flavors=[Flavor(FlavorType.tourism, value=8)]
			)

		raise InvalidEnumError(self)


class GovernorTypeData:
	def __init__(self, name: str, title: str, turnsToEstablish: int, defaultTitle: GovernorTitleType,
				 titles: [GovernorTitleType], flavors: [Flavor]):
		self.name = name
		self.title = title
		self.turnsToEstablish = turnsToEstablish
		self.defaultTitle = defaultTitle
		self.titles = titles
		self.flavors = flavors


class GovernorType(ExtendedEnum):
	none = 'none'

	reyna = 'reyna'
	victor = 'victor'
	amani = 'amani'
	magnus = 'magnus'
	moksha = 'moksha'
	liang = 'liang'
	pingala = 'pingala'

	def name(self) -> str:
		return self._data().name

	def defaultTitle(self) -> GovernorTitleType:
		return self._data().defaultTitle

	def flavorValue(self, flavorType: FlavorType) -> int:
		flavorOfCard = next((flavor for flavor in self._data().flavors if flavor.flavorType == flavorType), None)

		if flavorOfCard is not None:
			return flavorOfCard.value

		return 0
	
	def _data(self) -> GovernorTypeData:
		if self == GovernorType.none:
			return GovernorTypeData(
				name="",
				title="",
				turnsToEstablish=0,
				defaultTitle=GovernorTitleType.none,
				titles=[],
				flavors=[]
			)

		if self == GovernorType.reyna:
			# https://civilization.fandom.com/wiki/Reyna_(Financier)_(Civ6)
			return GovernorTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_REYNA_NAME",
				title="TXT_KEY_GOVERNMENT_GOVERNOR_REYNA_TITLE",
				turnsToEstablish=5,
				defaultTitle=GovernorTitleType.landAcquisition,
				titles=[
					GovernorTitleType.harbormaster, GovernorTitleType.forestryManagement,  # tier 1
					GovernorTitleType.taxCollector,  # tier 2
					GovernorTitleType.contractor, GovernorTitleType.renewableSubsidizer  # tier 3
				],
				flavors=[Flavor(FlavorType.expansion, value=8), Flavor(FlavorType.gold, value=6)]
			)
		elif self == GovernorType.victor:
			# https://civilization.fandom.com/wiki/Victor_(Castellan)_(Civ6)
			return GovernorTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_VICTOR_NAME",
				title="TXT_KEY_GOVERNMENT_GOVERNOR_VICTOR_TITLE",
				turnsToEstablish=3,
				defaultTitle=GovernorTitleType.redoubt,
				titles=[
					GovernorTitleType.garrisonCommander, GovernorTitleType.defenseLogistics,  # tier 1
					GovernorTitleType.embrasure,  # tier 2
					GovernorTitleType.airDefenseInitiative, GovernorTitleType.armsRaceProponent  # tier 3
				],
				flavors=[Flavor(FlavorType.cityDefense, value=9)]
			)

		elif self == GovernorType.amani:
			# https://civilization.fandom.com/wiki/Amani_(Diplomat)_(Civ6)
			return GovernorTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_AMANI_NAME",
				title="TXT_KEY_GOVERNMENT_GOVERNOR_AMANI_TITLE",
				turnsToEstablish=5,
				defaultTitle=GovernorTitleType.messenger,
				titles=[
					GovernorTitleType.emissary, GovernorTitleType.affluence,  # tier 1
					GovernorTitleType.localInformants, GovernorTitleType.foreignInvestor,  # tier 2
					GovernorTitleType.puppeteer  # tier 3
				],
				flavors=[Flavor(FlavorType.diplomacy, value=9)]
			)

		elif self == GovernorType.magnus:
			# https://civilization.fandom.com/wiki/Magnus_(Steward)_(Civ6)
			return GovernorTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_MAGNUS_NAME",
				title="TXT_KEY_GOVERNMENT_GOVERNOR_MAGNUS_TITLE",
				turnsToEstablish=5,
				defaultTitle=GovernorTitleType.groundbreaker,
				titles=[
					GovernorTitleType.surplusLogistics, GovernorTitleType.provision,  # tier 1
					GovernorTitleType.industrialist, GovernorTitleType.blackMarketeer,  # tier 2
					GovernorTitleType.verticalIntegration  # tier 3
				],
				flavors=[Flavor(FlavorType.tileImprovement, value=6)]
			)

		elif self == GovernorType.moksha:
			# https://civilization.fandom.com/wiki/Moksha_(Cardinal)_(Civ6)
			return GovernorTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_MOKSHA_NAME",
				title="TXT_KEY_GOVERNMENT_GOVERNOR_MOKSHA_TITLE",
				turnsToEstablish=5,
				defaultTitle=GovernorTitleType.bishop,
				titles=[
					GovernorTitleType.grandInquisitor, GovernorTitleType.layingOnOfHands,  # tier 1
					GovernorTitleType.citadelOfGod,  # tier 2
					GovernorTitleType.patronSaint, GovernorTitleType.divineArchitect  # tier 3
				],
				flavors=[Flavor(FlavorType.religion, value=8)]
			)

		elif self == GovernorType.liang:
			# https://civilization.fandom.com/wiki/Liang_(Surveyor)_(Civ6)
			return GovernorTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_LIANG_NAME",
				title="TXT_KEY_GOVERNMENT_GOVERNOR_LIANG_TITLE",
				turnsToEstablish=5,
				defaultTitle=GovernorTitleType.guildmaster,
				titles=[
					GovernorTitleType.zoningCommissioner, GovernorTitleType.aquaculture,  # tier 1
					GovernorTitleType.reinforcedMaterials, GovernorTitleType.waterWorks,  # tier 2
					GovernorTitleType.parksAndRecreation  # tier 3
				],
				flavors=[Flavor(FlavorType.tileImprovement, value=7)]
			)

		elif self == GovernorType.pingala:
			# https://civilization.fandom.com/wiki/Pingala_(Educator)_(Civ6)
			return GovernorTypeData(
				name="TXT_KEY_GOVERNMENT_GOVERNOR_PINGALA_NAME",
				title="TXT_KEY_GOVERNMENT_GOVERNOR_PINGALA_TITLE",
				turnsToEstablish=5,
				defaultTitle=GovernorTitleType.librarian,
				titles=[
					GovernorTitleType.connoisseur, GovernorTitleType.researcher,  # tier 1
					GovernorTitleType.grants,  # tier 2
					GovernorTitleType.spaceInitiative, GovernorTitleType.curator  # tier 3
				],
				flavors=[Flavor(FlavorType.science, value=5), Flavor(FlavorType.culture, value=5)]
			)

		raise InvalidEnumError(self)


class Governor:
	def __init__(self, governorType: GovernorType):
		self._governorType = governorType
		self._location = constants.invalidHexPoint
		self._titles = []

	def governorType(self) -> GovernorType:
		return self._governorType

	def defaultTitle(self) -> GovernorTitleType:
		return self._governorType.defaultTitle()

	def hasTitle(self, title: GovernorTitleType) -> bool:
		return title in self._titles

	def numberOfTitles(self) -> int:
		return len(self._titles)

	def assignedCity(self, simulation):
		return simulation.cityAt(self._location)

	def assignTo(self, city):
		self._location = city.location

	def unassign(self):
		self._location = constants.invalidHexPoint
