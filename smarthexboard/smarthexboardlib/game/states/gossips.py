from typing import Optional

from smarthexboard.smarthexboardlib.core.base import ExtendedEnum
from smarthexboard.smarthexboardlib.game.civilizations import LeaderType
from smarthexboard.smarthexboardlib.game.districts import DistrictType
from smarthexboard.smarthexboardlib.game.states.accessLevels import AccessLevel
from smarthexboard.smarthexboardlib.game.types import TechType, CivicType
from smarthexboard.smarthexboardlib.game.unitTypes import UnitType
from smarthexboard.smarthexboardlib.utils.translation import gettext_lazy as _


class GossipTypeData:
	def __init__(self, name: str, accessLevel: AccessLevel):
		self.name = name
		self.accessLevel = accessLevel


class GossipType(ExtendedEnum):
	# AccessLevel: none
	cityConquests = 'cityConquests'  # (cityName: String)
	pantheonCreated = 'pantheonCreated'  # (pantheonName: String)
	religionsFounded = 'religionsFounded'  # (religionName: String)
	declarationsOfWar = 'declarationsOfWar'  # (leader: LeaderType)
	weaponsOfMassDestructionStrikes = 'weaponsOfMassDestructionStrikes'  # fixme
	spaceRaceProjectsCompleted = 'spaceRaceProjectsCompleted'  # fixme

	# AccessLevel: limited
	alliance = 'alliance'  # (leader: LeaderType) fixme
	friendship = 'alliance'  # (leader: LeaderType)
	governmentChange = 'governmentChange'  # (government: GovernmentType)
	denunciation = 'denunciation'  # (leader: LeaderType)
	cityFounded = 'cityFounded'  # (cityName: String)
	cityLiberated = 'cityLiberated'  # (cityName: String, originalOwner: LeaderType)
	cityRazed = 'cityRazed'  # (cityName: String, originalOwner: LeaderType)
	cityBesieged = 'cityBesieged'  # (cityName: String) fixme
	tradeDealEnacted = 'tradeDealEnacted'  # fixme
	tradeDealReneged = 'tradeDealReneged'  # fixme
	barbarianCampCleared = 'barbarianCampCleared'  # (unit: UnitType)

	# AccessLevel: open
	buildingConstructed = 'buildingConstructed'  # (building: BuildingType)
	districtConstructed = 'districtConstructed'  # (district: DistrictType)
	greatPeopleRecruited = 'greatPeopleRecruited'  # (greatPeople: GreatPerson)
	wonderStarted = 'wonderStarted'  # (wonder: WonderType, cityName: String)
	artifactsExtracted = 'artifactsExtracted'  # fixme
	inquisitionLaunched = 'inquisitionLaunched'  # fixme

	# AccessLevel: secret
	cityStatesInfluenced = 'cityStatesInfluenced'  # fixme
	civicCompleted = 'civicCompleted'  # (civic: CivicType)
	technologyResearched = 'technologyResearched'  # (tech: TechType)
	settlerTrained = 'settlerTrained'  # (cityName: String)

	# AccessLevel: top secret
	weaponOfMassDestructionBuilt = 'weaponOfMassDestructionBuilt'  # fixme
	attacksLaunched = 'attacksLaunched'  # fixme
	projectsStarted = 'projectsStarted'  # fixme
	victoryStrategyChanged = 'victoryStrategyChanged'  # fixme
	warPreparations = 'warPreparations'  # fixme

	def name(self) -> str:
		return self._data().name

	def accessLevel(self) -> AccessLevel:
		return self._data().accessLevel

	def _data(self) -> GossipTypeData:
		# AccessLevel: none
		if self == GossipType.cityConquests:
			return GossipTypeData(
				name=_("TXT_KEY_DIPLOMACY_GOSSIP_NAME_CITY_CONQUEST"),
				accessLevel=AccessLevel.none
			)
		elif self == GossipType.pantheonCreated:
			return GossipTypeData(
				name=_("TXT_KEY_DIPLOMACY_GOSSIP_NAME_PANTHEON_CREATED"),
				accessLevel=AccessLevel.none
			)
		elif self == GossipType.religionsFounded:
			return GossipTypeData(
				name=_("TXT_KEY_DIPLOMACY_GOSSIP_NAME_RELIGIONS_FOUNDED"),
				accessLevel=AccessLevel.none
			)
		elif self == GossipType.declarationsOfWar:
			return GossipTypeData(
				name=_("TXT_KEY_DIPLOMACY_GOSSIP_NAME_DECLARATIONS_OF_WAR"),
				accessLevel=AccessLevel.none
			)
		elif self == GossipType.weaponsOfMassDestructionStrikes:
			return GossipTypeData(
				name=_("TXT_KEY_DIPLOMACY_GOSSIP_NAME_WEAPONS_OF_MASS_DESTRUCTION_STRIKES"),
				accessLevel=AccessLevel.none
			)
		elif self == GossipType.spaceRaceProjectsCompleted:
			return GossipTypeData(
				name=_("TXT_KEY_DIPLOMACY_GOSSIP_NAME_SPACE_RACE_PROJECTS_COMPLETED"),
				accessLevel=AccessLevel.none
			)

		# AccessLevel: limited
		elif self == GossipType.alliance:
			return GossipTypeData(
				name=_("TXT_KEY_DIPLOMACY_GOSSIP_NAME_ALLIANCES"),
				accessLevel=AccessLevel.limited
			)
		elif self == GossipType.friendship:
			return GossipTypeData(
				name=_("TXT_KEY_DIPLOMACY_GOSSIP_NAME_FRIENDSHIPS"),
				accessLevel=AccessLevel.limited
			)
		elif self == GossipType.governmentChange:
			return GossipTypeData(
				name=_("TXT_KEY_DIPLOMACY_GOSSIP_NAME_GOVERNMENT_CHANGES"),
				accessLevel=AccessLevel.limited
			)
		elif self == GossipType.denunciation:
			return GossipTypeData(
				name=_("TXT_KEY_DIPLOMACY_GOSSIP_NAME_DENUNCIATION"),
				accessLevel=AccessLevel.limited
			)
		elif self == GossipType.cityFounded:
			return GossipTypeData(
				name=_("TXT_KEY_DIPLOMACY_GOSSIP_NAME_CITIES_FOUNDED"),
				accessLevel=AccessLevel.limited
			)
		elif self == GossipType.cityLiberated:
			return GossipTypeData(
				name=_("TXT_KEY_DIPLOMACY_GOSSIP_NAME_CITIES_LIBERATED"),
				accessLevel=AccessLevel.limited
			)
		elif self == GossipType.cityRazed:
			return GossipTypeData(
				name=_("TXT_KEY_DIPLOMACY_GOSSIP_NAME_CITIES_RAZED"),
				accessLevel=AccessLevel.limited
			)
		elif self == GossipType.cityBesieged:
			return GossipTypeData(
				name=_("TXT_KEY_DIPLOMACY_GOSSIP_NAME_CITIES_BESIEGED"),
				accessLevel=AccessLevel.limited
			)
		elif self == GossipType.tradeDealEnacted:
			return GossipTypeData(
				name=_("TXT_KEY_DIPLOMACY_GOSSIP_NAME_TRADE_DEALS_ENACTED"),
				accessLevel=AccessLevel.limited
			)
		elif self == GossipType.tradeDealReneged:
			return GossipTypeData(
				name=_("TXT_KEY_DIPLOMACY_GOSSIP_NAME_TRADE_DEALS_RENEGED"),
				accessLevel=AccessLevel.limited
			)
		elif self == GossipType.barbarianCampCleared:
			return GossipTypeData(
				name=_("TXT_KEY_DIPLOMACY_GOSSIP_NAME_BARBARIAN_CAMP_CLEARED"),
				accessLevel=AccessLevel.limited
			)

		# AccessLevel: open
		elif self == GossipType.buildingConstructed:
			return GossipTypeData(
				name=_("TXT_KEY_DIPLOMACY_GOSSIP_NAME_BUILDINGS_CONSTRUCTED"),
				accessLevel=AccessLevel.open
			)
		elif self == GossipType.districtConstructed:
			return GossipTypeData(
				name=_("TXT_KEY_DIPLOMACY_GOSSIP_NAME_DISTRICTS_CONSTRUCTED"),
				accessLevel=AccessLevel.open
			)
		elif self == GossipType.greatPeopleRecruited:
			return GossipTypeData(
				name=_("TXT_KEY_DIPLOMACY_GOSSIP_NAME_GREAT_PEOPLE_RECRUITED"),
				accessLevel=AccessLevel.open
			)
		elif self == GossipType.wonderStarted:
			return GossipTypeData(
				name=_("TXT_KEY_DIPLOMACY_GOSSIP_NAME_WONDERS_STARTED"),
				accessLevel=AccessLevel.open
			)
		elif self == GossipType.artifactsExtracted:
			return GossipTypeData(
				name=_("TXT_KEY_DIPLOMACY_GOSSIP_NAME_ARTIFACTS_EXTRACTED"),
				accessLevel=AccessLevel.open
			)
		elif self == GossipType.inquisitionLaunched:
			return GossipTypeData(
				name=_("TXT_KEY_DIPLOMACY_GOSSIP_NAME_INQUISITION_LAUNCHED"),
				accessLevel=AccessLevel.open
			)

		# AccessLevel: secret
		elif self == GossipType.cityStatesInfluenced:
			return GossipTypeData(
				name=_("TXT_KEY_DIPLOMACY_GOSSIP_NAME_CITY_STATE_INFLUENCED"),
				accessLevel=AccessLevel.secret
			)
		elif self == GossipType.civicCompleted:
			return GossipTypeData(
				name=_("TXT_KEY_DIPLOMACY_GOSSIP_NAME_CIVICS_COMPLETED"),
				accessLevel=AccessLevel.secret
			)
		elif self == GossipType.technologyResearched:
			return GossipTypeData(
				name=_("TXT_KEY_DIPLOMACY_GOSSIP_NAME_TECHNOLOGIES_RESEARCHED"),
				accessLevel=AccessLevel.secret
			)
		elif self == GossipType.settlerTrained:
			return GossipTypeData(
				name=_("TXT_KEY_DIPLOMACY_GOSSIP_NAME_SETTLERS_TRAINED"),
				accessLevel=AccessLevel.secret
			)

		# AccessLevel: top secret
		elif self == GossipType.weaponOfMassDestructionBuilt:
			return GossipTypeData(
				name=_("TXT_KEY_DIPLOMACY_GOSSIP_NAME_WEAPON_OF_MASS_DESTRUCTION_BUILT"),
				accessLevel=AccessLevel.topSecret
			)
		elif self == GossipType.attacksLaunched:
			return GossipTypeData(
				name=_("TXT_KEY_DIPLOMACY_GOSSIP_NAME_ATTACKS_LAUNCHED"),
				accessLevel=AccessLevel.topSecret
			)
		elif self == GossipType.projectsStarted:
			return GossipTypeData(
				name=_("TXT_KEY_DIPLOMACY_GOSSIP_NAME_PROJECTS_STARTED"),
				accessLevel=AccessLevel.topSecret
			)
		elif self == GossipType.victoryStrategyChanged:
			return GossipTypeData(
				name=_("TXT_KEY_DIPLOMACY_GOSSIP_NAME_VICTORY_STRATEGY_CHANGED"),
				accessLevel=AccessLevel.topSecret
			)
		elif self == GossipType.warPreparations:
			return GossipTypeData(
				name=_("TXT_KEY_DIPLOMACY_GOSSIP_NAME_WAR_PREPARATIONS"),
				accessLevel=AccessLevel.topSecret
			)


class GossipSourceType(ExtendedEnum):
	spy = 'spy'


class GossipItem:
	def __init__(self, gossipType: GossipType, turn: int, source: GossipSourceType):
		self.gossipType = gossipType
		self.turn = turn
		self.source = source

		self.cityName: Optional[str] = None
		self.tech: Optional[TechType] = None
		self.civic: Optional[CivicType] = None
		self.leader: Optional[LeaderType] = None
		self.building = None
		self.district: Optional[DistrictType] = None
		self.wonder = None
		self.pantheonName: Optional[str] = None
		self.government = None
		self.unit: Optional[UnitType] = None

	def __repr__(self):
		return f'GossipItem({self.gossipType}, {self.turn}, {self.source})'
