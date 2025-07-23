from typing import List

from smarthexboard.smarthexboardlib.game.ai.diplomaticTypes import MajorPlayerApproachType, MinorPlayerApproachType
from smarthexboard.smarthexboardlib.game.flavors import FlavorType, Flavor
from smarthexboard.smarthexboardlib.core.base import ExtendedEnum, InvalidEnumError, WeightedBaseList
from smarthexboard.smarthexboardlib.map.types import TerrainType, FeatureType, ResourceType

from smarthexboard.smarthexboardlib.utils.translation import gettext_lazy as _


class CivilizationAbility(ExtendedEnum):
	none = 'none'

	motherRussia = 'motherRussia'
	allRoadsLeadToRome = 'allRoadsLeadToRome'
	workshopOfTheWorld = 'workshopOfTheWorld'
	platosRepublic = 'platosRepublic'
	grandTour = 'grandTour'
	iteru = 'iteru'
	satrapies = 'satrapies'
	freeImperialCities = 'freeImperialCities'
	legendOfTheFiveSuns = 'legendOfTheFiveSuns'

	def title(self) -> str:
		return 'ability'
	

class StartBiasTerrain:
	def __init__(self, terrainType: TerrainType, isHills: bool, tier: int):
		self.terrainType: TerrainType = terrainType
		self.isHills: bool = isHills
		self.tier: int = tier


class StartBiasFeature:
	def __init__(self, featureType: FeatureType, tier: int):
		self.featureType: FeatureType = featureType
		self.tier: int = tier


class StartBiasResource:
	def __init__(self, resourceType: ResourceType, tier: int):
		self.resourceType: ResourceType = resourceType
		self.tier: int = tier


class CivilizationData:
	def __init__(self, name: str, ability: CivilizationAbility, cityNames: List[str],
	             startBiasTerrains=None, startBiasFeatures=None, startBiasResource=None, startBiasRiverTier: int = 0):
		self.name = name
		self.ability = ability
		self.cityNames = cityNames

		if startBiasTerrains is None:
			self.startBiasTerrains: List[StartBiasTerrain] = []
		else:
			self.startBiasTerrains: List[StartBiasTerrain] = startBiasTerrains

		if startBiasFeatures is None:
			self.startBiasFeatures: List[StartBiasFeature] = []
		else:
			self.startBiasFeatures: List[StartBiasFeature] = startBiasFeatures

		if startBiasResource is None:
			self.startBiasResource: List[StartBiasResource] = []
		else:
			self.startBiasResource: List[StartBiasResource] = startBiasResource

		self.startBiasRiverTier: int = startBiasRiverTier


class CivilizationType(ExtendedEnum):
	none = 'none'
	unmet = 'unmet'
	barbarian = 'barbarian'
	free = 'free'
	cityState = 'cityState'

	greece = 'greece'  # CIVILIZATION_GREECE
	rome = 'rome'  # CIVILIZATION_ROME
	england = 'england'  # CIVILIZATION_ENGLAND
	russia = 'russia'  # CIVILIZATION_RUSSIA
	macedon = 'macedon'  # CIVILIZATION_MACEDON
	china = 'china'  # CIVILIZATION_CHINA
	egypt = 'egypt'  # CIVILIZATION_EGYPT
	germany = 'germany'  # CIVILIZATION_GERMANY
	aztec = 'aztec'  # CIVILIZATION_AZTEC

	def title(self) -> str:
		return self._data().name

	def ability(self) -> CivilizationAbility:
		return self._data().ability

	def isCoastalCiv(self) -> bool:
		for startBiasTerrain in self._data().startBiasTerrains:
			if startBiasTerrain.terrainType == TerrainType.shore:
				return True

		return False

	def startingBias(self, tile, grid) -> int:
		# https://civilization.fandom.com/wiki/Starting_bias_(Civ5)
		biasValue: int = 0

		for startBiasTerrain in self._data().startBiasTerrains:
			if startBiasTerrain.terrainType == tile.terrain() and startBiasTerrain.isHills == tile.isHills():
				biasValue += startBiasTerrain.tier

		for startBiasFeature in self._data().startBiasFeatures:
			if startBiasFeature.featureType == tile.feature():
				biasValue += startBiasFeature.tier

		if self._data().startBiasRiverTier > 0:
			if grid.riverAt(tile.point):
				biasValue += self._data().startBiasRiverTier

		return biasValue

	def _data(self) -> CivilizationData:
		# https://civilization.fandom.com/wiki/Module:Data/Civ6/GS/StartBiasTerrains
		if self == CivilizationType.none:
			return CivilizationData(
				name=_('TXT_KEY_CIVILIZATION_NONE'),
				ability=CivilizationAbility.none,
				cityNames=[],
				startBiasTerrains=[],
				startBiasFeatures=[]
			)
		elif self == CivilizationType.barbarian:
			return CivilizationData(
				name=_('TXT_KEY_CIVILIZATION_BARBARIAN'),
				ability=CivilizationAbility.none,
				cityNames=[],
				startBiasTerrains=[],
				startBiasFeatures=[]
			)
		elif self == CivilizationType.free:
			return CivilizationData(
				name=_('TXT_KEY_CIVILIZATION_FREE'),
				ability=CivilizationAbility.none,
				cityNames=[],
				startBiasTerrains=[],
				startBiasFeatures=[]
			)
		elif self == CivilizationType.unmet:
			return CivilizationData(
				name=_('TXT_KEY_CIVILIZATION_UNMET'),
				ability=CivilizationAbility.none,
				cityNames=[],
				startBiasTerrains=[],
				startBiasFeatures=[]
			)
		elif self == CivilizationType.cityState:
			return CivilizationData(
				name=_('TXT_KEY_CIVILIZATION_CITY_STATE'),
				ability=CivilizationAbility.none,
				cityNames=[],
				startBiasTerrains=[],
				startBiasFeatures=[]
			)

		elif self == CivilizationType.greece:
			# https://civilization.fandom.com/wiki/Greek_(Civ6)
			# cities taken from here: https://civilization.fandom.com/wiki/Greek_cities_(Civ6)
			return CivilizationData(
				name=_('TXT_KEY_CIVILIZATION_GREECE'),
				ability=CivilizationAbility.platosRepublic,
				cityNames=[
					_("TXT_KEY_CITY_NAME_ATHENS"),
					_("TXT_KEY_CITY_NAME_SPARTA"),
					_("TXT_KEY_CITY_NAME_CORINTH"),
					_("TXT_KEY_CITY_NAME_EPHESUS"),
					_("TXT_KEY_CITY_NAME_ARGOS"),
					_("TXT_KEY_CITY_NAME_KNOSSOS"),
					_("TXT_KEY_CITY_NAME_MYCENAE"),
					_("TXT_KEY_CITY_NAME_PHARSALOS"),
					_("TXT_KEY_CITY_NAME_RHODES"),
					_("TXT_KEY_CITY_NAME_OLYMPIA"),
					_("TXT_KEY_CITY_NAME_ERETRIA"),
					_("TXT_KEY_CITY_NAME_PERGAMON"),
					_("TXT_KEY_CITY_NAME_MILETOS"),
					_("TXT_KEY_CITY_NAME_MEGARA"),
					_("TXT_KEY_CITY_NAME_PHOCAEA"),
					_("TXT_KEY_CITY_NAME_DELPHI"),
					_("TXT_KEY_CITY_NAME_MARATHON"),
					_("TXT_KEY_CITY_NAME_PATRAS")
				],
				startBiasTerrains=[
					StartBiasTerrain(TerrainType.desert, isHills=True, tier=3),
					StartBiasTerrain(TerrainType.grass, isHills=True, tier=3),
					StartBiasTerrain(TerrainType.plains, isHills=True, tier=3),
					StartBiasTerrain(TerrainType.tundra, isHills=True, tier=3)
				]
			)
		elif self == CivilizationType.rome:
			# https://civilization.fandom.com/wiki/Roman_(Civ6)
			# cities taken from here: https://civilization.fandom.com/wiki/Roman_cities_(Civ6)
			return CivilizationData(
				name=_("TXT_KEY_CIVILIZATION_ROME"),
				ability=CivilizationAbility.allRoadsLeadToRome,
				cityNames=[
					_("TXT_KEY_CITY_NAME_ROME"),
					_("TXT_KEY_CITY_NAME_OSTIA"),
					_("TXT_KEY_CITY_NAME_ANTIUM"),
					_("TXT_KEY_CITY_NAME_CUMAE"),
					_("TXT_KEY_CITY_NAME_AQUILEIA"),
					_("TXT_KEY_CITY_NAME_RAVENNA"),
					_("TXT_KEY_CITY_NAME_PUTEOLI"),
					_("TXT_KEY_CITY_NAME_ARRETIUM"),
					_("TXT_KEY_CITY_NAME_MEDIOLANUM"),
					_("TXT_KEY_CITY_NAME_LUGDUNUM"),
					_("TXT_KEY_CITY_NAME_ARPINUM"),
					_("TXT_KEY_CITY_NAME_SETIA"),
					_("TXT_KEY_CITY_NAME_VELITRAE"),
					_("TXT_KEY_CITY_NAME_DUROCORTORUM"),
					_("TXT_KEY_CITY_NAME_BRUNDISIUM"),
					_("TXT_KEY_CITY_NAME_CAESARAUGUSTA"),
					_("TXT_KEY_CITY_NAME_PALMYRA"),
					_("TXT_KEY_CITY_NAME_HISPALIS"),
					_("TXT_KEY_CITY_NAME_CAESAREA"),
					_("TXT_KEY_CITY_NAME_ARTAXATA"),
					_("TXT_KEY_CITY_NAME_PAPHOS"),
					_("TXT_KEY_CITY_NAME_SALONAE"),
					_("TXT_KEY_CITY_NAME_EBURACUM"),
					_("TXT_KEY_CITY_NAME_LAURIACUM"),
					_("TXT_KEY_CITY_NAME_VERONA"),
					_("TXT_KEY_CITY_NAME_COLONIA_AGRIPPINA"),
					_("TXT_KEY_CITY_NAME_NARBO"),
					_("TXT_KEY_CITY_NAME_TINGI"),
					_("TXT_KEY_CITY_NAME_SARMIZEGETUSA"),
					_("TXT_KEY_CITY_NAME_SIRMIUM")
				]
			)
		elif self == CivilizationType.england:
			#
			# cities taken from here: https://civilization.fandom.com/wiki/English_cities_(Civ6)
			return CivilizationData(
				name=_('TXT_KEY_CIVILIZATION_ENGLAND'),
				ability=CivilizationAbility.workshopOfTheWorld,
				cityNames=[
					_("TXT_KEY_CITY_NAME_LONDON"),
					_("TXT_KEY_CITY_NAME_LIVERPOOL"),
					_("TXT_KEY_CITY_NAME_MANCHESTER"),
					_("TXT_KEY_CITY_NAME_BIRMINGHAM"),
					_("TXT_KEY_CITY_NAME_LEEDS"),
					_("TXT_KEY_CITY_NAME_SHEFFIELD"),
					_("TXT_KEY_CITY_NAME_BRISTOL"),
					_("TXT_KEY_CITY_NAME_PLYMOUTH"),
					_("TXT_KEY_CITY_NAME_NEWCASTLE_UPON_TYNE"),
					_("TXT_KEY_CITY_NAME_BRADFORD"),
					_("TXT_KEY_CITY_NAME_STOKE_UPON_TRENT"),
					_("TXT_KEY_CITY_NAME_HULL"),
					_("TXT_KEY_CITY_NAME_PORTSMOUTH"),
					_("TXT_KEY_CITY_NAME_PRESTON"),
					_("TXT_KEY_CITY_NAME_SUNDERLAND"),
					_("TXT_KEY_CITY_NAME_BRIGHTON"),
					_("TXT_KEY_CITY_NAME_NORWICH"),
					_("TXT_KEY_CITY_NAME_YORK"),
					_("TXT_KEY_CITY_NAME_NOTTINGHAM"),
					_("TXT_KEY_CITY_NAME_LEICESTER"),
					_("TXT_KEY_CITY_NAME_BLACKBURN"),
					_("TXT_KEY_CITY_NAME_WOLVERHAMPTON"),
					_("TXT_KEY_CITY_NAME_BATH"),
					_("TXT_KEY_CITY_NAME_COVENTRY"),
					_("TXT_KEY_CITY_NAME_EXETER"),
					_("TXT_KEY_CITY_NAME_LINCOLN"),
					_("TXT_KEY_CITY_NAME_CANTERBURY"),
					_("TXT_KEY_CITY_NAME_IPSWICH"),
					_("TXT_KEY_CITY_NAME_DOVER"),
					_("TXT_KEY_CITY_NAME_HASTINGS"),
					_("TXT_KEY_CITY_NAME_OXFORD"),
					_("TXT_KEY_CITY_NAME_SHREWSBURY"),
					_("TXT_KEY_CITY_NAME_CAMBRIDGE"),
					_("TXT_KEY_CITY_NAME_NEWCASTLE"),
					_("TXT_KEY_CITY_NAME_WARWICK")
				],
				startBiasTerrains=[
					StartBiasTerrain(TerrainType.shore, isHills=False, tier=3)
				],
				startBiasResource=[
					StartBiasResource(ResourceType.coal, tier=5),
					StartBiasResource(ResourceType.iron, tier=5)
				]
			)
		elif self == CivilizationType.russia:
			# https://civilization.fandom.com/wiki/Russian_(Civ6)
			# cities taken from here: https://civilization.fandom.com/wiki/Russian_cities_(Civ6)
			return CivilizationData(
				name=_('TXT_KEY_CIVILIZATION_RUSSIA'),
				ability=CivilizationAbility.motherRussia,
				cityNames=[
					_("TXT_KEY_CITY_NAME_ST_PETERSBURG"),
					_("TXT_KEY_CITY_NAME_MOSCOW"),
					_("TXT_KEY_CITY_NAME_NOVGOROD"),
					_("TXT_KEY_CITY_NAME_KAZAN"),
					_("TXT_KEY_CITY_NAME_ASTRAKHAN"),
					_("TXT_KEY_CITY_NAME_YAROSLAVL"),
					_("TXT_KEY_CITY_NAME_SMOLENSK"),
					_("TXT_KEY_CITY_NAME_VORONEZH"),
					_("TXT_KEY_CITY_NAME_TULA"),
					_("TXT_KEY_CITY_NAME_SOLIKAMSK"),
					_("TXT_KEY_CITY_NAME_TVER"),
					_("TXT_KEY_CITY_NAME_NIZHNIY_NOVGOROD"),
					_("TXT_KEY_CITY_NAME_ARKHANGELSK"),
					_("TXT_KEY_CITY_NAME_VOLOGDA"),
					_("TXT_KEY_CITY_NAME_OLONETS"),
					_("TXT_KEY_CITY_NAME_SARATOV"),
					_("TXT_KEY_CITY_NAME_TAMBOV"),
					_("TXT_KEY_CITY_NAME_PSKOV"),
					_("TXT_KEY_CITY_NAME_KRASNOYARSK"),
					_("TXT_KEY_CITY_NAME_IRKUTSK"),
					_("TXT_KEY_CITY_NAME_YEKATERINBURG"),
					_("TXT_KEY_CITY_NAME_ROSTOV"),
					_("TXT_KEY_CITY_NAME_BRYANSK"),
					_("TXT_KEY_CITY_NAME_YAKUTSK"),
					_("TXT_KEY_CITY_NAME_STARAYA_RUSSA"),
					_("TXT_KEY_CITY_NAME_PERM"),
					_("TXT_KEY_CITY_NAME_PETROZAVODSK"),
					_("TXT_KEY_CITY_NAME_OKHOTSK"),
					_("TXT_KEY_CITY_NAME_KOSTROMA"),
					_("TXT_KEY_CITY_NAME_NIZHNEKOLYMSK"),
					_("TXT_KEY_CITY_NAME_SERGIYEV_POSAD"),
					_("TXT_KEY_CITY_NAME_OMSK")
				],
				startBiasTerrains=[
					StartBiasTerrain(TerrainType.tundra, isHills=False, tier=3),
					StartBiasTerrain(TerrainType.tundra, isHills=True, tier=3)
				]
			)
		elif self == CivilizationType.macedon:
			# https://civilization.fandom.com/wiki/Macedonian_(Civ6)
			# cities taken from here: https://civilization.fandom.com/wiki/Macedonian_cities_(Civ6)
			return CivilizationData(
				name=_('TXT_KEY_CIVILIZATION_MACEDON'),
				ability=CivilizationAbility.none,
				cityNames=[
					_("TXT_KEY_CITY_NAME_AIGAI"),
					_("TXT_KEY_CITY_NAME_ALEXANDRIA"),
					_("TXT_KEY_CITY_NAME_METHONE"),
					_("TXT_KEY_CITY_NAME_CHALKIDIKI"),
					_("TXT_KEY_CITY_NAME_DION"),
					_("TXT_KEY_CITY_NAME_ALEXANDROPOULI")
				]
			)
		elif self == CivilizationType.china:
			# https://civilization.fandom.com/wiki/Chinese_(Civ6)
			# cities taken from here: https://civilization.fandom.com/wiki/Chinese_cities_(Civ6)
			return CivilizationData(
				name=_('TXT_KEY_CIVILIZATION_CHINA'),
				ability=CivilizationAbility.none,
				cityNames=[
					_("TXT_KEY_CITY_NAME_TAIYUAN"),
					_("TXT_KEY_CITY_NAME_CHENGDU"),
					_("TXT_KEY_CITY_NAME_JIAODONG"),
					_("TXT_KEY_CITY_NAME_CHANGSHA"),
					_("TXT_KEY_CITY_NAME_LONGXI"),
					_("TXT_KEY_CITY_NAME_GUANGZHOU"),
					_("TXT_KEY_CITY_NAME_HANDAN"),
					_("TXT_KEY_CITY_NAME_SHENYANG"),
					_("TXT_KEY_CITY_NAME_SHANGHAI"),
					_("TXT_KEY_CITY_NAME_WUHAN"),
					_("TXT_KEY_CITY_NAME_YIYANG")
				]
			)
		elif self == CivilizationType.egypt:
			# https://civilization.fandom.com/wiki/Egyptian_(Civ6)
			# cities taken from here: https://civilization.fandom.com/wiki/Egyptian_cities_(Civ6)
			return CivilizationData(
				name=_('TXT_KEY_CIVILIZATION_EGYPT'),
				ability=CivilizationAbility.iteru,
				cityNames=[
					_("TXT_KEY_CITY_NAME_MEMPHIS"),
					_("TXT_KEY_CITY_NAME_AKHETATEN"),
					_("TXT_KEY_CITY_NAME_SHEDET"),
					_("TXT_KEY_CITY_NAME_IWNW"),
					_("TXT_KEY_CITY_NAME_SWENETT"),
					_("TXT_KEY_CITY_NAME_NEKHEN"),
					_("TXT_KEY_CITY_NAME_SAIS"),
					_("TXT_KEY_CITY_NAME_ABYDOS"),
					_("TXT_KEY_CITY_NAME_APU"),
					_("TXT_KEY_CITY_NAME_EDFU"),
					_("TXT_KEY_CITY_NAME_MENDES")
				],
				startBiasFeatures=[
					StartBiasFeature(FeatureType.floodplains, 2)
				],
				startBiasRiverTier=5
			)
		elif self == CivilizationType.germany:
			# https://civilization.fandom.com/wiki/German_(Civ6)
			# cities taken from here: https://civilization.fandom.com/wiki/German_cities_(Civ6)
			return CivilizationData(
				name=_('TXT_KEY_CIVILIZATION_GERMANY'),
				ability=CivilizationAbility.freeImperialCities,
				cityNames=[
					_("TXT_KEY_CITY_NAME_COLOGNE"),
					_("TXT_KEY_CITY_NAME_FRANKFURT"),
					_("TXT_KEY_CITY_NAME_MAGDEBURG"),
					_("TXT_KEY_CITY_NAME_MAINZ"),
					_("TXT_KEY_CITY_NAME_HEIDELBERG"),
					_("TXT_KEY_CITY_NAME_TRIER"),
					_("TXT_KEY_CITY_NAME_BERLIN"),
					_("TXT_KEY_CITY_NAME_ULM"),
					_("TXT_KEY_CITY_NAME_HAMBURG"),
					_("TXT_KEY_CITY_NAME_DORTMUND"),
					_("TXT_KEY_CITY_NAME_NUREMBERG")
				],
				startBiasTerrains=[
					StartBiasTerrain(TerrainType.shore, isHills=False, tier=3)
				],
				startBiasRiverTier=5
			)
		elif self == CivilizationType.aztec:
			# https://civilization.fandom.com/wiki/Aztec_(Civ6)
			# cities taken from here: https://civilization.fandom.com/wiki/Aztec_cities_(Civ6)
			return CivilizationData(
				name=_('TXT_KEY_CIVILIZATION_AZTEC'),
				ability=CivilizationAbility.legendOfTheFiveSuns,
				cityNames=[
					_("TXT_KEY_CITY_NAME_TEXCOCO"),
					_("TXT_KEY_CITY_NAME_ATZCAPOTZALCO"),
					_("TXT_KEY_CITY_NAME_TEOTIHUACAN"),
					_("TXT_KEY_CITY_NAME_TLACOPAN"),
					_("TXT_KEY_CITY_NAME_XOCHICALCO"),
					_("TXT_KEY_CITY_NAME_MALINALCO"),
					_("TXT_KEY_CITY_NAME_TEAYO"),
					_("TXT_KEY_CITY_NAME_CEMPOALA"),
					_("TXT_KEY_CITY_NAME_CHALCO"),
					_("TXT_KEY_CITY_NAME_IXTAPALUCA"),
					_("TXT_KEY_CITY_NAME_TENAYUCA")
				]
			)

		raise InvalidEnumError(self)

	def cityNames(self):
		return self._data().cityNames


class WeightedCivilizationList(WeightedBaseList):
	def __init__(self):
		super().__init__()
		for civilization in list(CivilizationType):
			self.setWeight(0.0, civilization)


class LeaderAbility(ExtendedEnum):
	# https://civilization.fandom.com/wiki/Module:Data/Civ6/Base/Traits
	none = 'none'

	trajansColumn = 'trajansColumn'  # trajan, roman, TRAJANS_COLUMN_TRAIT
	grandEmbassy = 'grandEmbassy'  # peter, russian, TRAIT_LEADER_GRAND_EMBASSY
	paxBritannica = 'paxBritannica'  # victoria, english, TRAIT_LEADER_PAX_BRITANNICA
	toTheWorldsEnd = 'toTheWorldsEnd'  # alexander, macedonian, TRAIT_LEADER_TO_WORLDS_END
	holyRomanEmperor = 'holyRomanEmperor'  # barbarossa, german, TRAIT_LEADER_HOLY_ROMAN_EMPEROR
	mediterranean = 'mediterranean'  # cleopatra, egyptian, TRAIT_LEADER_MEDITERRANEAN
	firstEmperor = 'firstEmperor'  # qin, chinese, FIRST_EMPEROR_TRAIT


class MajorCivApproachBias:
	def __init__(self, approach: MajorPlayerApproachType, value: int):
		self.approach: MajorPlayerApproachType = approach
		self.value: int = value


class MinorCivApproachBias:
	def __init__(self, approach: MinorPlayerApproachType, value: int):
		self.approach: MinorPlayerApproachType = approach
		self.value: int = value


class LeaderTypeData:
	def __init__(self, name: str, civilization: CivilizationType, ability: LeaderAbility, flavors: List[Flavor],
	             majorCivApproachBiases: List[MajorCivApproachBias], minorCivApproachBiases: List[MinorCivApproachBias],
	             victoryCompetitiveness: int, wonderCompetitiveness: int, minorCivCompetitiveness: int,
	             boldness: int, diplomaticBalance: int, warmongerHate: int, denounceWillingness: int,
	             declarationOfFriendshipWillingness: int, loyalty: int, neediness: int, forgiveness: int,
	             chattiness: int, meanness: int):
		self.name: str = name
		self.civilization: CivilizationType = civilization
		self.ability: LeaderAbility = ability
		self.flavors: List[Flavor] = flavors

		self.majorCivApproachBiases: List[MajorCivApproachBias] = majorCivApproachBiases
		self.minorCivApproachBiases: List[MinorCivApproachBias] = minorCivApproachBiases

		self.victoryCompetitiveness = victoryCompetitiveness
		self.wonderCompetitiveness = wonderCompetitiveness
		self.minorCivCompetitiveness = minorCivCompetitiveness
		self.boldness = boldness
		self.diplomaticBalance = diplomaticBalance
		self.warmongerHate = warmongerHate
		self.denounceWillingness = denounceWillingness
		self.declarationOfFriendshipWillingness = declarationOfFriendshipWillingness
		self.loyalty = loyalty
		self.neediness = neediness
		self.forgiveness = forgiveness
		self.chattiness = chattiness
		self.meanness = meanness


class LeaderType:
	pass


class LeaderType(ExtendedEnum):
	# https://civilization.fandom.com/wiki/Module:Data/Civ6/RF/Leaders
	none = 'none'
	barbar = 'barbar'
	cityState = 'cityState'
	freeCities = 'freeCities'
	unmet = 'unmet'

	alexander = 'alexander'  # LEADER_ALEXANDER
	trajan = 'trajan'  # LEADER_TRAJAN
	victoria = 'victoria'  # LEADER_VICTORIA
	peter = 'peter'  # LEADER_PETER_GREAT
	barbarossa = 'barbarossa'  # LEADER_BARBAROSSA
	cleopatra = 'cleopatra'  # LEADER_CLEOPATRA
	montezuma = 'montezuma'  # LEADER_MONTEZUMA
	qin = 'qin'  # LEADER_QIN

	@staticmethod
	def fromName(leaderName: str) -> LeaderType:
		if leaderName == 'LeaderType.none' or leaderName == 'none':
			return LeaderType.none
		elif leaderName == 'LeaderType.barbar' or leaderName == 'barbar':
			return LeaderType.barbar
		elif leaderName == 'LeaderType.cityState' or leaderName == 'cityState':
			return LeaderType.cityState
		elif leaderName == 'LeaderType.freeCities' or leaderName == 'freeCities':
			return LeaderType.freeCities

		elif leaderName == 'LeaderType.alexander' or leaderName == 'alexander':
			return LeaderType.alexander
		elif leaderName == 'LeaderType.trajan' or leaderName == 'trajan':
			return LeaderType.trajan
		elif leaderName == 'LeaderType.victoria' or leaderName == 'victoria':
			return LeaderType.victoria
		elif leaderName == 'LeaderType.peter' or leaderName == 'peter':
			return LeaderType.peter
		elif leaderName == 'LeaderType.barbarossa' or leaderName == 'barbarossa':
			return LeaderType.barbarossa
		elif leaderName == 'LeaderType.cleopatra' or leaderName == 'cleopatra':
			return LeaderType.cleopatra
		elif leaderName == 'LeaderType.montezuma' or leaderName == 'montezuma':
			return LeaderType.montezuma
		elif leaderName == 'LeaderType.qin' or leaderName == 'qin':
			return LeaderType.qin
		elif leaderName == 'LeaderType.unmet' or leaderName == 'unmet':
			return LeaderType.unmet

		raise Exception(f'No matching case for leaderName: "{leaderName}"')

	def title(self) -> str:  # cannot be 'name'
		return self._data().name

	def civilization(self) -> CivilizationType:
		return self._data().civilization

	def ability(self) -> LeaderAbility:
		return self._data().ability

	def majorCivApproachBiasTowards(self, approach: MajorPlayerApproachType) -> int:
		item = next((app for app in self._majorCivApproachBiases() if app.approach == approach), None)

		if item is not None:
			return item.value

		# raise Exception(f'Leader majorCivApproachBiases of {self} does not contain a value for {approach}')
		return 0

	def _majorCivApproachBiases(self) -> List[MajorCivApproachBias]:
		return self._data().majorCivApproachBiases

	def minorCivApproachBiasTowards(self, approach: MinorPlayerApproachType) -> int:
		item = next((app for app in self._minorCivApproachBiases() if app.approach == approach), None)

		if item is not None:
			return item.value

		# raise Exception(f'Leader minorCivApproachBiases of {self} does not contain a value for {approach}')
		return 0

	def _minorCivApproachBiases(self) -> List[MinorCivApproachBias]:
		return self._data().minorCivApproachBiases

	def victoryCompetitiveness(self) -> int:
		return self._data().victoryCompetitiveness

	def wonderCompetitiveness(self) -> int:
		return self._data().wonderCompetitiveness

	def minorCivCompetitiveness(self) -> int:
		return self._data().minorCivCompetitiveness

	def boldness(self) -> int:
		return self._data().boldness

	def warmongerHate(self) -> int:
		return self._data().warmongerHate

	def diplomaticBalance(self) -> int:
		return self._data().diplomaticBalance

	def warmongerHate(self) -> int:
		return self._data().warmongerHate

	def denounceWillingness(self) -> int:
		return self._data().denounceWillingness

	def declarationOfFriendshipWillingness(self) -> int:
		return self._data().declarationOfFriendshipWillingness

	def loyalty(self) -> int:
		return self._data().loyalty

	def neediness(self) -> int:
		return self._data().neediness

	def forgiveness(self) -> int:
		return self._data().forgiveness

	def chattiness(self) -> int:
		return self._data().chattiness

	def meanness(self) -> int:
		return self._data().meanness

	def flavor(self, flavorType: FlavorType) -> int:
		item = next((flavor for flavor in self._flavors() if flavor.flavorType == flavorType), None)

		if item is not None:
			return item.value

		return 0

	def _flavors(self) -> List[Flavor]:
		return self._data().flavors

	def _data(self) -> LeaderTypeData:
		"""
		https://github.com/LoneGazebo/Community-Patch-DLL/blob/4a483b28353f38dd5a10d5e75c7a68e59b9bee5c/(2)%20Vox%20Populi/Balance%20Changes/AI/LeaderPersonalities.sql#L9
		https://civilization.fandom.com/wiki/Module:Data/Civ5/BNW/Leader_Values
		@return:
		"""
		if self == LeaderType.none:
			return LeaderTypeData(
				name='None',
				civilization=CivilizationType.none,
				ability=LeaderAbility.none,
				flavors=[],
				majorCivApproachBiases=[],
				minorCivApproachBiases=[],
				victoryCompetitiveness=5,
				wonderCompetitiveness=5,
				minorCivCompetitiveness=5,
				boldness=5,
				diplomaticBalance=5,
				warmongerHate=5,
				denounceWillingness=5,
				declarationOfFriendshipWillingness=5,
				loyalty=5,
				neediness=5,
				forgiveness=5,
				chattiness=5,
				meanness=5
			)
		elif self == LeaderType.cityState:
			return LeaderTypeData(
				name='CityState',
				civilization=CivilizationType.cityState,
				ability=LeaderAbility.none,
				flavors=[],
				majorCivApproachBiases=[],
				minorCivApproachBiases=[],
				victoryCompetitiveness=5,
				wonderCompetitiveness=5,
				minorCivCompetitiveness=5,
				boldness=5,
				diplomaticBalance=5,
				warmongerHate=5,
				denounceWillingness=5,
				declarationOfFriendshipWillingness=5,
				loyalty=5,
				neediness=5,
				forgiveness=5,
				chattiness=5,
				meanness=5
			)
		elif self == LeaderType.barbar:
			return LeaderTypeData(
				name=_('TXT_KEY_LEADER_BARBARIAN'),
				civilization=CivilizationType.barbarian,
				ability=LeaderAbility.none,
				flavors=[],
				majorCivApproachBiases=[],
				minorCivApproachBiases=[],
				victoryCompetitiveness=5,
				wonderCompetitiveness=5,
				minorCivCompetitiveness=5,
				boldness=5,
				diplomaticBalance=5,
				warmongerHate=5,
				denounceWillingness=5,
				declarationOfFriendshipWillingness=5,
				loyalty=5,
				neediness=5,
				forgiveness=5,
				chattiness=5,
				meanness=5
			)
		elif self == LeaderType.freeCities:
			return LeaderTypeData(
				name=_('TXT_KEY_LEADER_FREE_CITIES'),
				civilization=CivilizationType.barbarian,
				ability=LeaderAbility.none,
				flavors=[],
				majorCivApproachBiases=[],
				minorCivApproachBiases=[],
				victoryCompetitiveness=5,
				wonderCompetitiveness=5,
				minorCivCompetitiveness=5,
				boldness=5,
				diplomaticBalance=5,
				warmongerHate=5,
				denounceWillingness=5,
				declarationOfFriendshipWillingness=5,
				loyalty=5,
				neediness=5,
				forgiveness=5,
				chattiness=5,
				meanness=5
			)

		elif self == LeaderType.alexander:
			return LeaderTypeData(
				name=_('TXT_KEY_LEADER_ALEXANDER'),
				civilization=CivilizationType.macedon,
				ability=LeaderAbility.toTheWorldsEnd,
				flavors=[
					Flavor(FlavorType.cityDefense, 5),
					Flavor(FlavorType.culture, 7),
					Flavor(FlavorType.defense, 5),
					Flavor(FlavorType.diplomacy, 9),
					Flavor(FlavorType.expansion, 8),
					Flavor(FlavorType.gold, 3),
					Flavor(FlavorType.growth, 4),
					Flavor(FlavorType.amenities, 5),
					Flavor(FlavorType.infrastructure, 4),
					Flavor(FlavorType.militaryTraining, 5),
					Flavor(FlavorType.mobile, 8),
					Flavor(FlavorType.naval, 5),
					Flavor(FlavorType.navalGrowth, 6),
					Flavor(FlavorType.navalRecon, 5),
					Flavor(FlavorType.navalTileImprovement, 6),
					Flavor(FlavorType.offense, 8),
					Flavor(FlavorType.production, 5),
					Flavor(FlavorType.recon, 5),
					Flavor(FlavorType.science, 6),
					Flavor(FlavorType.tileImprovement, 4),
					Flavor(FlavorType.wonder, 6)
				],
				majorCivApproachBiases=[
					MajorCivApproachBias(MajorPlayerApproachType.war, 9),
					MajorCivApproachBias(MajorPlayerApproachType.hostile, 7),
					MajorCivApproachBias(MajorPlayerApproachType.deceptive, 2),
					MajorCivApproachBias(MajorPlayerApproachType.guarded, 5),
					MajorCivApproachBias(MajorPlayerApproachType.afraid, 1),
					MajorCivApproachBias(MajorPlayerApproachType.neutral, 4),
					MajorCivApproachBias(MajorPlayerApproachType.friendly, 7)
				],
				minorCivApproachBiases=[
					MinorCivApproachBias(MinorPlayerApproachType.ignore, 1),
					MinorCivApproachBias(MinorPlayerApproachType.protective, 9),
					MinorCivApproachBias(MinorPlayerApproachType.bully, 2),
					MinorCivApproachBias(MinorPlayerApproachType.conquest, 6),
				],
				victoryCompetitiveness=6,
				wonderCompetitiveness=3,
				minorCivCompetitiveness=10,
				boldness=10,
				diplomaticBalance=7,
				warmongerHate=2,
				denounceWillingness=7,
				declarationOfFriendshipWillingness=5,
				loyalty=7,
				neediness=3,
				forgiveness=4,
				chattiness=4,
				meanness=8
			)
		elif self == LeaderType.trajan:
			return LeaderTypeData(
				name=_('TXT_KEY_LEADER_TRAJAN'),
				civilization=CivilizationType.rome,
				ability=LeaderAbility.trajansColumn,
				flavors=[
					Flavor(FlavorType.cityDefense, 5),
					Flavor(FlavorType.culture, 5),
					Flavor(FlavorType.defense, 6),
					Flavor(FlavorType.diplomacy, 5),
					Flavor(FlavorType.expansion, 8),
					Flavor(FlavorType.gold, 6),
					Flavor(FlavorType.growth, 5),
					Flavor(FlavorType.amenities, 8),
					Flavor(FlavorType.infrastructure, 8),
					Flavor(FlavorType.militaryTraining, 7),
					Flavor(FlavorType.mobile, 4),
					Flavor(FlavorType.naval, 5),
					Flavor(FlavorType.navalGrowth, 4),
					Flavor(FlavorType.navalRecon, 5),
					Flavor(FlavorType.navalTileImprovement, 4),
					Flavor(FlavorType.offense, 5),
					Flavor(FlavorType.production, 6),
					Flavor(FlavorType.recon, 3),
					Flavor(FlavorType.science, 5),
					Flavor(FlavorType.tileImprovement, 7),
					Flavor(FlavorType.wonder, 6)
				],
				majorCivApproachBiases=[
					MajorCivApproachBias(MajorPlayerApproachType.war, 9),
					MajorCivApproachBias(MajorPlayerApproachType.hostile, 3),
					MajorCivApproachBias(MajorPlayerApproachType.deceptive, 1),
					MajorCivApproachBias(MajorPlayerApproachType.guarded, 5),
					MajorCivApproachBias(MajorPlayerApproachType.afraid, 5),
					MajorCivApproachBias(MajorPlayerApproachType.neutral, 8),
					MajorCivApproachBias(MajorPlayerApproachType.friendly, 2)
				],
				minorCivApproachBiases=[
					MinorCivApproachBias(MinorPlayerApproachType.ignore, 2),
					MinorCivApproachBias(MinorPlayerApproachType.protective, 2),
					MinorCivApproachBias(MinorPlayerApproachType.bully, 3),
					MinorCivApproachBias(MinorPlayerApproachType.conquest, 12),
				],
				victoryCompetitiveness=6,
				wonderCompetitiveness=8,
				minorCivCompetitiveness=2,
				boldness=7,
				diplomaticBalance=3,
				warmongerHate=5,
				denounceWillingness=2,
				declarationOfFriendshipWillingness=2,
				loyalty=3,
				neediness=4,
				forgiveness=1,
				chattiness=4,
				meanness=8
			)
		elif self == LeaderType.victoria:
			return LeaderTypeData(
				name=_('TXT_KEY_LEADER_VICTORIA'),
				civilization=CivilizationType.england,
				ability=LeaderAbility.none,
				flavors=[
					Flavor(FlavorType.cityDefense, 6),
					Flavor(FlavorType.culture, 6),
					Flavor(FlavorType.defense, 6),
					Flavor(FlavorType.diplomacy, 6),
					Flavor(FlavorType.expansion, 6),
					Flavor(FlavorType.gold, 8),
					Flavor(FlavorType.growth, 4),
					Flavor(FlavorType.amenities, 5),
					Flavor(FlavorType.infrastructure, 5),
					Flavor(FlavorType.militaryTraining, 5),
					Flavor(FlavorType.mobile, 3),
					Flavor(FlavorType.naval, 8),
					Flavor(FlavorType.navalGrowth, 7),
					Flavor(FlavorType.navalRecon, 8),
					Flavor(FlavorType.navalTileImprovement, 7),
					Flavor(FlavorType.offense, 3),
					Flavor(FlavorType.production, 6),
					Flavor(FlavorType.recon, 6),
					Flavor(FlavorType.science, 6),
					Flavor(FlavorType.tileImprovement, 6),
					Flavor(FlavorType.wonder, 5)
				],
				majorCivApproachBiases=[
					MajorCivApproachBias(MajorPlayerApproachType.war, 6),
					MajorCivApproachBias(MajorPlayerApproachType.hostile, 8),
					MajorCivApproachBias(MajorPlayerApproachType.deceptive, 8),
					MajorCivApproachBias(MajorPlayerApproachType.guarded, 10),
					MajorCivApproachBias(MajorPlayerApproachType.afraid, 5),
					MajorCivApproachBias(MajorPlayerApproachType.neutral, 7),
					MajorCivApproachBias(MajorPlayerApproachType.friendly, 5)
				],
				minorCivApproachBiases=[
					MinorCivApproachBias(MinorPlayerApproachType.ignore, 2),
					MinorCivApproachBias(MinorPlayerApproachType.protective, 9),
					MinorCivApproachBias(MinorPlayerApproachType.bully, 4),
					MinorCivApproachBias(MinorPlayerApproachType.conquest, 7),
				],
				victoryCompetitiveness=7,
				wonderCompetitiveness=5,
				minorCivCompetitiveness=8,
				boldness=7,
				diplomaticBalance=10,
				warmongerHate=5,
				denounceWillingness=8,
				declarationOfFriendshipWillingness=6,
				loyalty=6,
				neediness=7,
				forgiveness=4,
				chattiness=4,
				meanness=8
			)
		elif self == LeaderType.peter:
			return LeaderTypeData(
				name=_('TXT_KEY_LEADER_PETER'),
				civilization=CivilizationType.russia,
				ability=LeaderAbility.grandEmbassy,
				flavors=[
					Flavor(FlavorType.offense, value=6),
					Flavor(FlavorType.defense, value=6),
					Flavor(FlavorType.cityDefense, value=6),
					Flavor(FlavorType.militaryTraining, value=5),
					Flavor(FlavorType.recon, value=5),
					Flavor(FlavorType.ranged, value=5),
					Flavor(FlavorType.mobile, value=6),
					Flavor(FlavorType.naval, value=3),
					Flavor(FlavorType.navalRecon, value=3),
					Flavor(FlavorType.navalGrowth, value=3),
					Flavor(FlavorType.navalTileImprovement, value=3),
					Flavor(FlavorType.air, value=3),
					Flavor(FlavorType.expansion, value=8),
					Flavor(FlavorType.growth, value=3),
					Flavor(FlavorType.tileImprovement, value=5),
					Flavor(FlavorType.infrastructure, value=5),
					Flavor(FlavorType.production, value=6),
					Flavor(FlavorType.gold, value=5),
					Flavor(FlavorType.science, value=8),
					Flavor(FlavorType.culture, value=6),
					Flavor(FlavorType.amenities, value=3),
					Flavor(FlavorType.greatPeople, value=6),
					Flavor(FlavorType.wonder, value=5),
					Flavor(FlavorType.religion, value=6),
					Flavor(FlavorType.diplomacy, value=5),
					# Flavor("FLAVOR_SPACESHIP", value=9),
					Flavor(FlavorType.waterConnection, value=3),
					# Flavor("FLAVOR_NUKE", value=8),
					# Flavor("FLAVOR_USE_NUKE", value=8),
					# Flavor("FLAVOR_ESPIONAGE", value=8),
					# Flavor("FLAVOR_ANTIAIR", value=5),
					# Flavor("FLAVOR_AIR_CARRIER", value=5),
					# Flavor("FLAVOR_ARCHAEOLOGY", value=5),
					# Flavor("FLAVOR_I_LAND_TRADE_ROUTE", value=5),
					# Flavor("FLAVOR_I_SEA_TRADE_ROUTE", value=5),
					# Flavor("FLAVOR_I_TRADE_ORIGIN", value=5),
					# Flavor("FLAVOR_I_TRADE_DESTINATION", value=5),
					# Flavor("FLAVOR_AIRLIFT", value=5),
				],
				majorCivApproachBiases=[
					MajorCivApproachBias(MajorPlayerApproachType.war, 4),
					MajorCivApproachBias(MajorPlayerApproachType.hostile, 6),
					MajorCivApproachBias(MajorPlayerApproachType.deceptive, 7),
					MajorCivApproachBias(MajorPlayerApproachType.guarded, 5),
					MajorCivApproachBias(MajorPlayerApproachType.afraid, 5),
					MajorCivApproachBias(MajorPlayerApproachType.friendly, 7),
					MajorCivApproachBias(MajorPlayerApproachType.neutral, 5),
				],
				minorCivApproachBiases=[
					MinorCivApproachBias(MinorPlayerApproachType.ignore, 4),
					MinorCivApproachBias(MinorPlayerApproachType.friendly, 6),
					MinorCivApproachBias(MinorPlayerApproachType.protective, 6),
					MinorCivApproachBias(MinorPlayerApproachType.conquest, 7),
					MinorCivApproachBias(MinorPlayerApproachType.bully, 5),
				],
				victoryCompetitiveness=5,
				wonderCompetitiveness=5,
				minorCivCompetitiveness=5,
				boldness=5,
				diplomaticBalance=5,
				warmongerHate=5,
				denounceWillingness=5,
				declarationOfFriendshipWillingness=5,
				loyalty=5,
				neediness=5,
				forgiveness=5,
				chattiness=5,
				meanness=5
			)
		elif self == LeaderType.barbarossa:  # LEADER_BARBAROSSA
			return LeaderTypeData(
				name=_('TXT_KEY_LEADER_BARBAROSSA'),
				civilization=CivilizationType.germany,  #
				ability=LeaderAbility.none,  #
				flavors=[
					Flavor(FlavorType.offense, value=5),
					Flavor(FlavorType.defense, value=6),
					Flavor(FlavorType.cityDefense, value=6),
					Flavor(FlavorType.militaryTraining, value=8),
					Flavor(FlavorType.recon, value=8),
					Flavor(FlavorType.ranged, value=5),
					Flavor(FlavorType.mobile, value=7),
					Flavor(FlavorType.naval, value=3),
					Flavor(FlavorType.navalRecon, value=3),
					Flavor(FlavorType.navalGrowth, value=4),
					Flavor(FlavorType.navalTileImprovement, value=4),
					Flavor(FlavorType.air, value=6),
					Flavor(FlavorType.expansion, value=7),
					Flavor(FlavorType.growth, value=5),
					Flavor(FlavorType.tileImprovement, value=6),
					Flavor(FlavorType.infrastructure, value=5),
					Flavor(FlavorType.production, value=8),
					Flavor(FlavorType.gold, value=5),
					Flavor(FlavorType.science, value=7),
					Flavor(FlavorType.culture, value=5),
					Flavor(FlavorType.amenities, value=5),
					Flavor(FlavorType.greatPeople, value=5),
					Flavor(FlavorType.wonder, value=4),
					Flavor(FlavorType.religion, value=3),
					Flavor(FlavorType.diplomacy, value=5),
					# Flavor("FLAVOR_SPACESHIP, value=8),
					Flavor(FlavorType.waterConnection, value=4),
					# Flavor("FLAVOR_NUKE, value=7),
					# Flavor("FLAVOR_USE_NUKE, value=5),
					# Flavor("FLAVOR_ESPIONAGE, value=5),
					# Flavor("FLAVOR_ANTIAIR, value=5),
					# Flavor("FLAVOR_AIR_CARRIER, value=5),
					# Flavor("FLAVOR_ARCHAEOLOGY, value=5),
					# Flavor("FLAVOR_I_LAND_TRADE_ROUTE, value=5),
					# Flavor("FLAVOR_I_SEA_TRADE_ROUTE, value=5),
					# Flavor("FLAVOR_I_TRADE_ORIGIN, value=5),
					# Flavor("FLAVOR_I_TRADE_DESTINATION, value=5),
					# Flavor("FLAVOR_AIRLIFT, value=5),
				],
				majorCivApproachBiases=[
					MajorCivApproachBias(MajorPlayerApproachType.war, 6),
					MajorCivApproachBias(MajorPlayerApproachType.hostile, 4),
					MajorCivApproachBias(MajorPlayerApproachType.deceptive, 7),
					MajorCivApproachBias(MajorPlayerApproachType.guarded, 7),
					MajorCivApproachBias(MajorPlayerApproachType.afraid, 4),
					MajorCivApproachBias(MajorPlayerApproachType.friendly, 7),
					MajorCivApproachBias(MajorPlayerApproachType.neutral, 4),
				],
				minorCivApproachBiases=[
					MinorCivApproachBias(MinorPlayerApproachType.ignore, 4),
					MinorCivApproachBias(MinorPlayerApproachType.friendly, 5),
					MinorCivApproachBias(MinorPlayerApproachType.protective, 7),
					MinorCivApproachBias(MinorPlayerApproachType.conquest, 4),
					MinorCivApproachBias(MinorPlayerApproachType.bully, 4),
				],
				victoryCompetitiveness=5,
				wonderCompetitiveness=5,
				minorCivCompetitiveness=5,
				boldness=5,
				diplomaticBalance=5,
				warmongerHate=5,
				denounceWillingness=5,
				declarationOfFriendshipWillingness=5,
				loyalty=5,
				neediness=5,
				forgiveness=5,
				chattiness=5,
				meanness=5
			)
		elif self == LeaderType.cleopatra:  # LEADER_CLEOPATRA
			return LeaderTypeData(
				name=_('TXT_KEY_LEADER_CLEOPATRA'),
				civilization=CivilizationType.egypt,
				ability=LeaderAbility.mediterranean,
				flavors=[
				],
				majorCivApproachBiases=[],
				minorCivApproachBiases=[],
				victoryCompetitiveness=5,
				wonderCompetitiveness=5,
				minorCivCompetitiveness=5,
				boldness=5,
				diplomaticBalance=5,
				warmongerHate=5,
				denounceWillingness=5,
				declarationOfFriendshipWillingness=5,
				loyalty=5,
				neediness=5,
				forgiveness=5,
				chattiness=5,
				meanness=5
			)
		elif self == LeaderType.montezuma:  # LEADER_MONTEZUMA
			return LeaderTypeData(
				name=_('TXT_KEY_LEADER_MONTEZUMA'),
				civilization=CivilizationType.aztec,  #
				ability=LeaderAbility.none,  #
				flavors=[
					Flavor(FlavorType.offense, value=9),
					Flavor(FlavorType.defense, value=3),
					Flavor(FlavorType.cityDefense, value=4),
					Flavor(FlavorType.militaryTraining, value=4),
					Flavor(FlavorType.recon, value=6),
					Flavor(FlavorType.ranged, value=5),
					Flavor(FlavorType.mobile, value=5),
					Flavor(FlavorType.naval, value=3),
					Flavor(FlavorType.navalRecon, value=3),
					Flavor(FlavorType.navalGrowth, value=4),
					Flavor(FlavorType.navalTileImprovement, value=4),
					Flavor(FlavorType.air, value=4),
					Flavor(FlavorType.expansion, value=8),
					Flavor(FlavorType.growth, value=5),
					Flavor(FlavorType.tileImprovement, value=5),
					Flavor(FlavorType.infrastructure, value=5),
					Flavor(FlavorType.production, value=5),
					Flavor(FlavorType.gold, value=5),
					Flavor(FlavorType.science, value=4),
					Flavor(FlavorType.culture, value=6),
					Flavor(FlavorType.amenities, value=6),
					Flavor(FlavorType.greatPeople, value=5),
					Flavor(FlavorType.wonder, value=6),
					Flavor(FlavorType.religion, value=7),
					Flavor(FlavorType.diplomacy, value=4),
					# Flavor("FLAVOR_SPACESHIP, value=7),
					Flavor(FlavorType.waterConnection, value=4),
					# Flavor("FLAVOR_NUKE, value=8),
					# Flavor("FLAVOR_USE_NUKE, value=8),
					# Flavor("FLAVOR_ESPIONAGE, value=5),
					# Flavor("FLAVOR_ANTIAIR, value=5),
					# Flavor("FLAVOR_AIR_CARRIER, value=6),
					# Flavor("FLAVOR_ARCHAEOLOGY, value=5),
					# Flavor("FLAVOR_I_LAND_TRADE_ROUTE, value=5),
					# Flavor("FLAVOR_I_SEA_TRADE_ROUTE, value=5),
					# Flavor("FLAVOR_I_TRADE_ORIGIN, value=5),
					# Flavor("FLAVOR_I_TRADE_DESTINATION, value=5),
					# Flavor("FLAVOR_AIRLIFT, value=5),
				],
				majorCivApproachBiases=[
					MajorCivApproachBias(MajorPlayerApproachType.war, 8),
					MajorCivApproachBias(MajorPlayerApproachType.hostile, 6),
					MajorCivApproachBias(MajorPlayerApproachType.deceptive, 7),
					MajorCivApproachBias(MajorPlayerApproachType.guarded, 5),
					MajorCivApproachBias(MajorPlayerApproachType.afraid, 7),
					MajorCivApproachBias(MajorPlayerApproachType.friendly, 4),
					MajorCivApproachBias(MajorPlayerApproachType.neutral, 5),
				],
				minorCivApproachBiases=[
					MinorCivApproachBias(MinorPlayerApproachType.ignore, 3),
					MinorCivApproachBias(MinorPlayerApproachType.friendly, 3),
					MinorCivApproachBias(MinorPlayerApproachType.protective, 3),
					MinorCivApproachBias(MinorPlayerApproachType.conquest, 8),
					MinorCivApproachBias(MinorPlayerApproachType.bully, 8),
				],
				victoryCompetitiveness=5,
				wonderCompetitiveness=5,
				minorCivCompetitiveness=5,
				boldness=5,
				diplomaticBalance=5,
				warmongerHate=5,
				denounceWillingness=5,
				declarationOfFriendshipWillingness=5,
				loyalty=5,
				neediness=5,
				forgiveness=5,
				chattiness=5,
				meanness=5
			)
		elif self == LeaderType.qin:  # LEADER_QIN
			return LeaderTypeData(
				name=_('TXT_KEY_LEADER_QIN'),
				civilization=CivilizationType.china,
				ability=LeaderAbility.firstEmperor,
				flavors=[
					Flavor(FlavorType.offense, value=5),
					Flavor(FlavorType.defense, value=7),
					Flavor(FlavorType.cityDefense, value=5),
					Flavor(FlavorType.militaryTraining, value=4),
					Flavor(FlavorType.recon, value=4),
					Flavor(FlavorType.ranged, value=7),
					Flavor(FlavorType.mobile, value=5),
					Flavor(FlavorType.naval, value=5),
					Flavor(FlavorType.navalRecon, value=4),
					Flavor(FlavorType.navalGrowth, value=5),
					Flavor(FlavorType.navalTileImprovement, value=5),
					Flavor(FlavorType.air, value=3),
					Flavor(FlavorType.expansion, value=6),
					Flavor(FlavorType.growth, value=8),
					Flavor(FlavorType.tileImprovement, value=4),
					Flavor(FlavorType.infrastructure, value=5),
					Flavor(FlavorType.production, value=5),
					Flavor(FlavorType.gold, value=5),
					Flavor(FlavorType.science, value=8),
					Flavor(FlavorType.culture, value=6),
					Flavor(FlavorType.amenities, value=6),
					Flavor(FlavorType.greatPeople, value=6),
					Flavor(FlavorType.wonder, value=6),
					Flavor(FlavorType.religion, value=5),
					Flavor(FlavorType.diplomacy, value=3),
					# Flavor("FLAVOR_SPACESHIP, value=8),
					Flavor(FlavorType.waterConnection, value=5),
					# Flavor("FLAVOR_NUKE, value=5),
					# Flavor("FLAVOR_USE_NUKE, value=5),
					# Flavor("FLAVOR_ANTIAIR, value=5),
					# Flavor("FLAVOR_AIR_CARRIER, value=5),
					# Flavor("FLAVOR_ESPIONAGE, value=7),
					# Flavor("FLAVOR_ARCHAEOLOGY, value=5),
					# Flavor("FLAVOR_I_LAND_TRADE_ROUTE, value=5),
					# Flavor("FLAVOR_I_SEA_TRADE_ROUTE, value=5),
					# Flavor("FLAVOR_I_TRADE_ORIGIN, value=5),
					# Flavor("FLAVOR_I_TRADE_DESTINATION, value=5),
					# Flavor("FLAVOR_AIRLIFT, value=5),
				],
				majorCivApproachBiases=[
					MajorCivApproachBias(MajorPlayerApproachType.war, 4),
					MajorCivApproachBias(MajorPlayerApproachType.hostile, 6),
					MajorCivApproachBias(MajorPlayerApproachType.deceptive, 7),
					MajorCivApproachBias(MajorPlayerApproachType.guarded, 7),
					MajorCivApproachBias(MajorPlayerApproachType.afraid, 5),
					MajorCivApproachBias(MajorPlayerApproachType.friendly, 7),
					MajorCivApproachBias(MajorPlayerApproachType.neutral, 5),
				],
				minorCivApproachBiases=[
					MinorCivApproachBias(MinorPlayerApproachType.ignore, 4),
					MinorCivApproachBias(MinorPlayerApproachType.friendly, 6),
					MinorCivApproachBias(MinorPlayerApproachType.protective, 7),
					MinorCivApproachBias(MinorPlayerApproachType.conquest, 5),
					MinorCivApproachBias(MinorPlayerApproachType.bully, 4),
				],
				victoryCompetitiveness=5,
				wonderCompetitiveness=5,
				minorCivCompetitiveness=5,
				boldness=5,
				diplomaticBalance=5,
				warmongerHate=5,
				denounceWillingness=5,
				declarationOfFriendshipWillingness=5,
				loyalty=5,
				neediness=5,
				forgiveness=5,
				chattiness=5,
				meanness=5
			)
		elif self == LeaderType.unmet:
			return LeaderTypeData(
				name=_('TXT_KEY_LEADER_UNMET'),
				civilization=CivilizationType.unmet,
				ability=LeaderAbility.none,
				flavors=[],
				majorCivApproachBiases=[],
				minorCivApproachBiases=[],
				victoryCompetitiveness=5,
				wonderCompetitiveness=5,
				minorCivCompetitiveness=5,
				boldness=5,
				diplomaticBalance=5,
				warmongerHate=5,
				denounceWillingness=5,
				declarationOfFriendshipWillingness=5,
				loyalty=5,
				neediness=5,
				forgiveness=5,
				chattiness=5,
				meanness=5
			)

		raise InvalidEnumError(self)


class LeaderWeightList(WeightedBaseList):
	def __init__(self):
		super().__init__()

		for leaderType in list(LeaderType):
			self.setWeight(0.0, leaderType)
