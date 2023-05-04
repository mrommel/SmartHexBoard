from smarthexboard.game.eras import EraType
from smarthexboard.game.flavors import Flavor, FlavorType
from smarthexboard.map.base import ExtendedEnum


class CivicType:
	pass


class CivicTypeData:
	def __init__(self, name: str, inspiration_summary: str, inspiration_description: str, quoteTexts: [str],
				 era: EraType, cost: int, required: [CivicType], flavors: [Flavor], governorTitle: bool, envoys: int):
		self.name = name
		self.inspiration_summary = inspiration_summary
		self.inspiration_description = inspiration_description
		self.quoteTexts = quoteTexts
		self.era = era
		self.cost = cost
		self.required = required
		self.flavors = flavors
		self.governorTitle = governorTitle
		self.envoys = envoys


class CivicType(ExtendedEnum):
	# default
	none = 'none'

	# ancient
	stateWorkforce = 'stateWorkforce'
	craftsmanship = 'craftsmanship'
	codeOfLaws = 'codeOfLaws'  # no eureka
	earlyEmpire = 'earlyEmpire'
	foreignTrade = 'foreignTrade'
	mysticism = 'mysticism'
	militaryTradition = 'militaryTradition'

	# classical
	defensiveTactics = 'defensiveTactics'
	gamesAndRecreation = 'gamesAndRecreation'
	politicalPhilosophy = 'politicalPhilosophy'
	recordedHistory = 'recordedHistory'
	dramaAndPoetry = 'dramaAndPoetry'
	theology = 'theology'
	militaryTraining = 'militaryTraining'

	# medieval
	navalTradition = 'navalTradition'
	feudalism = 'feudalism'
	medievalFaires = 'medievalFaires'
	civilService = 'civilService'
	guilds = 'guilds'
	mercenaries = 'mercenaries'
	divineRight = 'divineRight'

	# renaissance
	enlightenment = 'enlightenment'
	humanism = 'humanism'
	mercantilism = 'mercantilism'
	diplomaticService = 'diplomaticService'
	exploration = 'exploration'
	reformedChurch = 'reformedChurch'

	# industrial
	civilEngineering = 'civilEngineering'
	colonialism = 'colonialism'
	nationalism = 'nationalism'
	operaAndBallet = 'operaAndBallet'
	naturalHistory = 'naturalHistory'
	urbanization = 'urbanization'
	scorchedEarth = 'scorchedEarth'

	# modern
	conservation = 'conservation'
	massMedia = 'massMedia'
	mobilization = 'mobilization'
	capitalism = 'capitalism'
	ideology = 'ideology'
	nuclearProgram = 'nuclearProgram'
	suffrage = 'suffrage'
	totalitarianism = 'totalitarianism'
	classStruggle = 'classStruggle'

	# atomic
	culturalHeritage = 'culturalHeritage'
	coldWar = 'coldWar'
	professionalSports = 'professionalSports'
	rapidDeployment = 'rapidDeployment'
	spaceRace = 'spaceRace'

	# information
	environmentalism = 'environmentalism'
	globalization = 'globalization'
	socialMedia = 'socialMedia'
	nearFutureGovernance = 'nearFutureGovernance'
	# Venture Politics
	# Distributed Sovereignty
	# Optimization Imperative

	# future
	informationWarfare = 'informationWarfare'
	globalWarmingMitigation = 'globalWarmingMitigation'
	culturalHegemony = 'culturalHegemony'
	exodusImperative = 'exodusImperative'
	smartPowerDoctrine = 'smartPowerDoctrine'
	futureCivic = 'futureCivic'

	def name(self) -> str:
		return self._data().name

	def required(self) -> []:
		return self._data().required

	def cost(self) -> int:
		return self._data().cost

	def envoys(self) -> int:
		return self._data().envoys

	def governorTitle(self) -> bool:
		return self._data().governorTitle

	# def achievements(self) -> CivicAchievements:
	#	return CivicAchievements(civic=self)

	def _data(self):
		# default
		if self == CivicType.none:
			return CivicTypeData(
				name='TXT_KEY_CIVIC_NONE',
				inspiration_summary='',
				inspiration_description='',
				quoteTexts=[],
				era=EraType.ancient,
				cost=0,
				required=[],
				flavors=[],
				governorTitle=False,
				envoys=0
			)

		# ancient
		elif self == CivicType.stateWorkforce:
			# https://civilization.fandom.com/wiki/State_Workforce_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_STATE_WORKFORCE_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_STATE_WORKFORCE_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_STATE_WORKFORCE_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_STATE_WORKFORCE_QUOTE1',
					'TXT_KEY_CIVIC_STATE_WORKFORCE_QUOTE2'
				],
				era=EraType.ancient,
				cost=70,
				required=[CivicType.craftsmanship],
				flavors=[],
				governorTitle=True,
				envoys=0
			)
		elif self == CivicType.craftsmanship:
			# https://civilization.fandom.com/wiki/Craftsmanship_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_CRAFTSMANSHIP_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_CRAFTSMANSHIP_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_CRAFTSMANSHIP_EUREKA_TEXT',
				quoteTexts=[
					"TXT_KEY_CIVIC_CRAFTSMANSHIP_QUOTE1",
					"TXT_KEY_CIVIC_CRAFTSMANSHIP_QUOTE2"
				],
				era=EraType.ancient,
				cost=40,
				required=[CivicType.codeOfLaws],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.codeOfLaws:  # no eureka
			# https://civilization.fandom.com/wiki/Code_of_Laws_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_CODE_OF_LAWS_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_CODE_OF_LAWS_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_CODE_OF_LAWS_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_CODE_OF_LAWS_QUOTE1',
					'TXT_KEY_CIVIC_CODE_OF_LAWS_QUOTE2'
				],
				era=EraType.ancient,
				cost=20,
				required=[],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.earlyEmpire:
			# https://civilization.fandom.com/wiki/Early_Empire_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_EARLY_EMPIRE_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_EARLY_EMPIRE_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_EARLY_EMPIRE_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_EARLY_EMPIRE_QUOTE1',
					'TXT_KEY_CIVIC_EARLY_EMPIRE_QUOTE2'
				],
				era=EraType.ancient,
				cost=70,
				required=[CivicType.foreignTrade],
				flavors=[],
				governorTitle=True,
				envoys=0
			)
		elif self == CivicType.foreignTrade:
			# https://civilization.fandom.com/wiki/Foreign_Trade_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_FOREIGN_TRADE_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_FOREIGN_TRADE_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_FOREIGN_TRADE_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_FOREIGN_TRADE_QUOTE1',
					'TXT_KEY_CIVIC_FOREIGN_TRADE_QUOTE2'
				],
				era=EraType.ancient,
				cost=40,
				required=[CivicType.codeOfLaws],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.mysticism:
			# https://civilization.fandom.com/wiki/Mysticism_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_MYSTICISM_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_MYSTICISM_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_MYSTICISM_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_MYSTICISM_QUOTE1',
					'TXT_KEY_CIVIC_MYSTICISM_QUOTE2'
				],
				era=EraType.ancient,
				cost=50,
				required=[CivicType.foreignTrade],
				flavors=[],
				governorTitle=False,
				envoys=1
			)
		elif self == CivicType.militaryTradition:
			# https://civilization.fandom.com/wiki/Military_Training_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_MILITARY_TRADITION_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_MILITARY_TRADITION_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_MILITARY_TRADITION_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_MILITARY_TRADITION_QUOTE1',
					'TXT_KEY_CIVIC_MILITARY_TRADITION_QUOTE2'
				],
				era=EraType.ancient,
				cost=50,
				required=[CivicType.craftsmanship],
				flavors=[],
				governorTitle=False,
				envoys=1
			)

		# classical
		elif self == CivicType.defensiveTactics:
			# https://civilization.fandom.com/wiki/Defensive_Tactics_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_DEFENSIVE_TACTICS_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_DEFENSIVE_TACTICS_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_DEFENSIVE_TACTICS_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_DEFENSIVE_TACTICS_QUOTE1',
					'TXT_KEY_CIVIC_DEFENSIVE_TACTICS_QUOTE2'
				],
				era=EraType.classical,
				cost=175,
				required=[CivicType.gamesAndRecreation, CivicType.politicalPhilosophy],
				flavors=[],
				governorTitle=True,
				envoys=0
			)
		elif self == CivicType.gamesAndRecreation:
			# https://civilization.fandom.com/wiki/Games_and_Recreation_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_GAMES_AND_RECREATION_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_GAMES_AND_RECREATION_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_GAMES_AND_RECREATION_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_GAMES_AND_RECREATION_QUOTE1',
					'TXT_KEY_CIVIC_GAMES_AND_RECREATION_QUOTE2'
				],
				era=EraType.classical,
				cost=110,
				required=[CivicType.stateWorkforce],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.politicalPhilosophy:
			# https://civilization.fandom.com/wiki/Political_Philosophy_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_POLITICAL_PHILOSOPHY_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_POLITICAL_PHILOSOPHY_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_POLITICAL_PHILOSOPHY_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_POLITICAL_PHILOSOPHY_QUOTE1',
					'TXT_KEY_CIVIC_POLITICAL_PHILOSOPHY_QUOTE2'
				],
				era=EraType.classical,
				cost=110,
				required=[CivicType.stateWorkforce, CivicType.earlyEmpire],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.recordedHistory:
			# https://civilization.fandom.com/wiki/Recorded_History_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_RECORDED_HISTORY_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_RECORDED_HISTORY_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_RECORDED_HISTORY_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_RECORDED_HISTORY_QUOTE1',
					'TXT_KEY_CIVIC_RECORDED_HISTORY_QUOTE2'
				],
				era=EraType.classical,
				cost=175,
				required=[CivicType.politicalPhilosophy, CivicType.dramaAndPoetry],
				flavors=[],
				governorTitle=True,
				envoys=0
			)
		elif self == CivicType.dramaAndPoetry:
			# https://civilization.fandom.com/wiki/Drama_and_Poetry_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_DRAMA_AND_POETRY_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_DRAMA_AND_POETRY_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_DRAMA_AND_POETRY_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_DRAMA_AND_POETRY_QUOTE1',
					'TXT_KEY_CIVIC_DRAMA_AND_POETRY_QUOTE2'
				],
				era=EraType.classical,
				cost=110,
				required=[CivicType.earlyEmpire],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.theology:
			# https://civilization.fandom.com/wiki/Theology_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_THEOLOGY_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_THEOLOGY_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_THEOLOGY_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_THEOLOGY_QUOTE1',
					'TXT_KEY_CIVIC_THEOLOGY_QUOTE2'
				],
				era=EraType.classical,
				cost=120,
				required=[CivicType.dramaAndPoetry, CivicType.mysticism],
				flavors=[],
				governorTitle=False,
				envoys=1
			)
		elif self == CivicType.militaryTraining:
			# https://civilization.fandom.com/wiki/Military_Training_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_MILITARY_TRAINING_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_MILITARY_TRAINING_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_MILITARY_TRAINING_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_MILITARY_TRAINING_QUOTE1',
					'TXT_KEY_CIVIC_MILITARY_TRAINING_QUOTE2'
				],
				era=EraType.classical,
				cost=120,
				required=[CivicType.militaryTradition, CivicType.gamesAndRecreation],
				flavors=[],
				governorTitle=False,
				envoys=0
			)

		# medieval
		elif self == CivicType.navalTradition:
			# https://civilization.fandom.com/wiki/Naval_Tradition_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_NAVAL_TRADITION_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_NAVAL_TRADITION_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_NAVAL_TRADITION_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_NAVAL_TRADITION_QUOTE1',
					'TXT_KEY_CIVIC_NAVAL_TRADITION_QUOTE2'
				],
				era=EraType.medieval,
				cost=200,
				required=[CivicType.defensiveTactics],
				flavors=[],
				governorTitle=False,
				envoys=1
			)
		elif self == CivicType.feudalism:
			# https://civilization.fandom.com/wiki/Feudalism_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_FEUDALISM_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_FEUDALISM_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_FEUDALISM_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_FEUDALISM_QUOTE1',
					'TXT_KEY_CIVIC_FEUDALISM_QUOTE2'
				],
				era=EraType.medieval,
				cost=275,
				required=[CivicType.defensiveTactics],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.medievalFaires:
			# https://civilization.fandom.com/wiki/Medieval_Faires_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_MEDIEVAL_FAIRES_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_MEDIEVAL_FAIRES_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_MEDIEVAL_FAIRES_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_MEDIEVAL_FAIRES_QUOTE1',
					'TXT_KEY_CIVIC_MEDIEVAL_FAIRES_QUOTE2'
				],
				era=EraType.medieval,
				cost=385,
				required=[CivicType.feudalism],
				flavors=[],
				governorTitle=True,
				envoys=0
			)
		elif self == CivicType.civilService:
			# https://civilization.fandom.com/wiki/Civil_Service_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_CIVIL_SERVICE_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_CIVIL_SERVICE_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_CIVIL_SERVICE_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_CIVIL_SERVICE_QUOTE1',
					'TXT_KEY_CIVIC_CIVIL_SERVICE_QUOTE2'
				],
				era=EraType.medieval,
				cost=275,
				required=[CivicType.defensiveTactics, CivicType.recordedHistory],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.guilds:
			# https://civilization.fandom.com/wiki/Guilds_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_GUILDS_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_GUILDS_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_GUILDS_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_GUILDS_QUOTE1',
					'TXT_KEY_CIVIC_GUILDS_QUOTE2'
				],
				era=EraType.medieval,
				cost=385,
				required=[CivicType.feudalism, CivicType.civilService],
				flavors=[],
				governorTitle=True,
				envoys=0
			)
		elif self == CivicType.mercenaries:
			# https://civilization.fandom.com/wiki/Mercenaries_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_MERCENARIES_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_MERCENARIES_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_MERCENARIES_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_MERCENARIES_QUOTE1',
					'TXT_KEY_CIVIC_MERCENARIES_QUOTE2'
				],
				era=EraType.medieval,
				cost=290,
				required=[CivicType.feudalism, CivicType.militaryTraining],
				flavors=[],
				governorTitle=False,
				envoys=2
			)
		elif self == CivicType.divineRight:
			# https://civilization.fandom.com/wiki/Divine_Right_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_DIVINE_RIGHT_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_DIVINE_RIGHT_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_DIVINE_RIGHT_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_DIVINE_RIGHT_QUOTE1',
					'TXT_KEY_CIVIC_DIVINE_RIGHT_QUOTE2'
				],
				era=EraType.medieval,
				cost=290,
				required=[CivicType.civilService, CivicType.theology],
				flavors=[],
				governorTitle=False,
				envoys=0
			)

		# renaissance
		elif self == CivicType.enlightenment:
			# https://civilization.fandom.com/wiki/The_Enlightenment_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_ENLIGHTENMENT_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_ENLIGHTENMENT_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_ENLIGHTENMENT_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_ENLIGHTENMENT_QUOTE1',
					'TXT_KEY_CIVIC_ENLIGHTENMENT_QUOTE2'
				],
				era=EraType.renaissance,
				cost=655,
				required=[CivicType.diplomaticService],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.humanism:
			# https://civilization.fandom.com/wiki/Humanism_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_HUMANISM_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_HUMANISM_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_HUMANISM_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_HUMANISM_QUOTE1',
					'TXT_KEY_CIVIC_HUMANISM_QUOTE2'
				],
				era=EraType.renaissance,
				cost=540,
				required=[CivicType.guilds, CivicType.medievalFaires],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.mercantilism:
			# https://civilization.fandom.com/wiki/Mercantilism_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_MERCANTILISM_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_MERCANTILISM_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_MERCANTILISM_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_MERCANTILISM_QUOTE1',
					'TXT_KEY_CIVIC_MERCANTILISM_QUOTE2'
				],
				era=EraType.renaissance,
				cost=655,
				required=[CivicType.humanism],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.diplomaticService:
			# https://civilization.fandom.com/wiki/Diplomatic_Service_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_DIPLOMATIC_SERVICE_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_DIPLOMATIC_SERVICE_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_DIPLOMATIC_SERVICE_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_DIPLOMATIC_SERVICE_QUOTE1',
					'TXT_KEY_CIVIC_DIPLOMATIC_SERVICE_QUOTE2'
				],
				era=EraType.renaissance,
				cost=540,
				required=[CivicType.guilds],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.exploration:
			# https://civilization.fandom.com/wiki/Exploration_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_EXPLORATION_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_EXPLORATION_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_EXPLORATION_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_EXPLORATION_QUOTE1',
					'TXT_KEY_CIVIC_EXPLORATION_QUOTE2'
				],
				era=EraType.renaissance,
				cost=400,
				required=[CivicType.mercenaries, CivicType.medievalFaires],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.reformedChurch:
			# https://civilization.fandom.com/wiki/Reformed_Church_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_REFORMED_CHURCH_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_REFORMED_CHURCH_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_REFORMED_CHURCH_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_REFORMED_CHURCH_QUOTE1',
					'TXT_KEY_CIVIC_REFORMED_CHURCH_QUOTE2'
				],
				era=EraType.renaissance,
				cost=400,
				required=[CivicType.divineRight],
				flavors=[],
				governorTitle=False,
				envoys=0
			)

		# industrial
		elif self == CivicType.civilEngineering:
			# https://civilization.fandom.com/wiki/Civil_Engineering_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_CIVIL_ENGINEERING_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_CIVIL_ENGINEERING_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_CIVIL_ENGINEERING_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_CIVIL_ENGINEERING_QUOTE1',
					'TXT_KEY_CIVIC_CIVIL_ENGINEERING_QUOTE2'
				],
				era=EraType.industrial,
				cost=920,
				required=[CivicType.mercantilism],
				flavors=[],
				governorTitle=True,
				envoys=0
			)
		elif self == CivicType.colonialism:
			# https://civilization.fandom.com/wiki/Colonialism_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_COLONIALISM_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_COLONIALISM_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_COLONIALISM_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_COLONIALISM_QUOTE1',
					'TXT_KEY_CIVIC_COLONIALISM_QUOTE2'
				],
				era=EraType.industrial,
				cost=725,
				required=[CivicType.mercantilism],
				flavors=[],
				governorTitle=False,
				envoys=2
			)
		elif self == CivicType.nationalism:
			# https://civilization.fandom.com/wiki/Nationalism_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_NATIONALISM_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_NATIONALISM_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_NATIONALISM_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_NATIONALISM_QUOTE1',
					'TXT_KEY_CIVIC_NATIONALISM_QUOTE2'
				],
				era=EraType.industrial,
				cost=920,
				required=[CivicType.enlightenment],
				flavors=[],
				governorTitle=True,
				envoys=0
			)
		elif self == CivicType.operaAndBallet:
			# https://civilization.fandom.com/wiki/Opera_and_Ballet_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_OPERA_AND_BALLET_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_OPERA_AND_BALLET_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_OPERA_AND_BALLET_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_OPERA_AND_BALLET_QUOTE1',
					'TXT_KEY_CIVIC_OPERA_AND_BALLET_QUOTE2'
				],
				era=EraType.industrial,
				cost=725,
				required=[CivicType.enlightenment],
				flavors=[],
				governorTitle=False,
				envoys=2
			)
		elif self == CivicType.naturalHistory:
			# https://civilization.fandom.com/wiki/Natural_History_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_NATURAL_HISTORY_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_NATURAL_HISTORY_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_NATURAL_HISTORY_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_NATURAL_HISTORY_QUOTE1',
					'TXT_KEY_CIVIC_NATURAL_HISTORY_QUOTE2'
				],
				era=EraType.industrial,
				cost=870,
				required=[CivicType.colonialism],
				flavors=[],
				governorTitle=False,
				envoys=2
			)
		elif self == CivicType.urbanization:
			# https://civilization.fandom.com/wiki/Urbanization_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_URBANIZATION_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_URBANIZATION_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_URBANIZATION_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_URBANIZATION_QUOTE1',
					'TXT_KEY_CIVIC_URBANIZATION_QUOTE2'
				],
				era=EraType.industrial,
				cost=1060,
				required=[CivicType.civilEngineering, CivicType.nationalism],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.scorchedEarth:
			# https://civilization.fandom.com/wiki/Scorched_Earth_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_SCORCHED_EARTH_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_SCORCHED_EARTH_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_SCORCHED_EARTH_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_SCORCHED_EARTH_QUOTE1',
					'TXT_KEY_CIVIC_SCORCHED_EARTH_QUOTE2'
				],
				era=EraType.industrial,
				cost=1060,
				required=[CivicType.nationalism],
				flavors=[],
				governorTitle=False,
				envoys=2
			)

		# modern
		elif self == CivicType.conservation:
			# https://civilization.fandom.com/wiki/Conservation_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_CONSERVATION_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_CONSERVATION_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_CONSERVATION_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_CONSERVATION_QUOTE1',
					'TXT_KEY_CIVIC_CONSERVATION_QUOTE2'
				],
				era=EraType.modern,
				cost=1255,
				required=[CivicType.naturalHistory, CivicType.urbanization],
				flavors=[],
				governorTitle=False,
				envoys=2
			)
		elif self == CivicType.massMedia:
			# https://civilization.fandom.com/wiki/Mass_Media_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_MASS_MEDIA_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_MASS_MEDIA_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_MASS_MEDIA_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_MASS_MEDIA_QUOTE1',
					'TXT_KEY_CIVIC_MASS_MEDIA_QUOTE2'
				],
				era=EraType.modern,
				cost=1410,
				required=[CivicType.urbanization],
				flavors=[],
				governorTitle=True,
				envoys=0
			)
		elif self == CivicType.mobilization:
			# https://civilization.fandom.com/wiki/Mobilization_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_MOBILIZATION_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_MOBILIZATION_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_MOBILIZATION_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_MOBILIZATION_QUOTE1',
					'TXT_KEY_CIVIC_MOBILIZATION_QUOTE2'
				],
				era=EraType.modern,
				cost=1410,
				required=[CivicType.urbanization],
				flavors=[],
				governorTitle=True,
				envoys=0
			)
		elif self == CivicType.capitalism:
			# https://civilization.fandom.com/wiki/Capitalism_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_CAPITALISM_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_CAPITALISM_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_CAPITALISM_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_CAPITALISM_QUOTE1',
					'TXT_KEY_CIVIC_CAPITALISM_QUOTE2'
				],
				era=EraType.modern,
				cost=1560,
				required=[CivicType.massMedia],
				flavors=[],
				governorTitle=False,
				envoys=3
			)
		elif self == CivicType.ideology:
			# https://civilization.fandom.com/wiki/Ideology_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_IDEOLOGY_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_IDEOLOGY_EUREKA',  # no inspiration
				inspiration_description='TXT_KEY_CIVIC_IDEOLOGY_EUREKA_TEXT',  # no inspiration
				quoteTexts=[
					'TXT_KEY_CIVIC_IDEOLOGY_QUOTE1',
					'TXT_KEY_CIVIC_IDEOLOGY_QUOTE2'
				],
				era=EraType.modern,
				cost=660,
				required=[CivicType.massMedia, CivicType.mobilization],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.nuclearProgram:
			# https://civilization.fandom.com/wiki/Nuclear_Program_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_NUCLEAR_PROGRAM_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_NUCLEAR_PROGRAM_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_NUCLEAR_PROGRAM_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_NUCLEAR_PROGRAM_QUOTE1',
					'TXT_KEY_CIVIC_NUCLEAR_PROGRAM_QUOTE2'
				],
				era=EraType.modern,
				cost=1715,
				required=[CivicType.ideology],
				flavors=[],
				governorTitle=False,
				envoys=3
			)
		elif self == CivicType.suffrage:
			# https://civilization.fandom.com/wiki/Suffrage_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_SUFFRAGE_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_SUFFRAGE_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_SUFFRAGE_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_SUFFRAGE_QUOTE1',
					'TXT_KEY_CIVIC_SUFFRAGE_QUOTE2'
				],
				era=EraType.modern,
				cost=1715,
				required=[CivicType.ideology],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.totalitarianism:
			# https://civilization.fandom.com/wiki/Totalitarianism_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_TOTALITARIANISM_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_TOTALITARIANISM_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_TOTALITARIANISM_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_TOTALITARIANISM_QUOTE1',
					'TXT_KEY_CIVIC_TOTALITARIANISM_QUOTE2'
				],
				era=EraType.modern,
				cost=1715,
				required=[CivicType.ideology],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.classStruggle:
			# https://civilization.fandom.com/wiki/Class_Struggle_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_CLASS_STRUGGLE_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_CLASS_STRUGGLE_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_CLASS_STRUGGLE_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_CLASS_STRUGGLE_QUOTE1',
					'TXT_KEY_CIVIC_CLASS_STRUGGLE_QUOTE2'
				],
				era=EraType.modern,
				cost=1715,
				required=[CivicType.ideology],
				flavors=[],
				governorTitle=False,
				envoys=0
			)

		# atomic
		elif self == CivicType.culturalHeritage:
			# https://civilization.fandom.com/wiki/Cultural_Heritage_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_CULTURAL_HERITAGE_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_CULTURAL_HERITAGE_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_CULTURAL_HERITAGE_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_CULTURAL_HERITAGE_QUOTE1',
					'TXT_KEY_CIVIC_CULTURAL_HERITAGE_QUOTE2'
				],
				era=EraType.atomic,
				cost=1955,
				required=[CivicType.conservation],
				flavors=[],
				governorTitle=False,
				envoys=3
			)
		elif self == CivicType.coldWar:
			# https://civilization.fandom.com/wiki/Cold_War_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_COLD_WAR_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_COLD_WAR_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_COLD_WAR_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_COLD_WAR_QUOTE1',
					'TXT_KEY_CIVIC_COLD_WAR_QUOTE2'
				],
				era=EraType.atomic,
				cost=2185,
				required=[CivicType.ideology],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.professionalSports:
			# https://civilization.fandom.com/wiki/Professional_Sports_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_PROFESSIONAL_SPORTS_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_PROFESSIONAL_SPORTS_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_PROFESSIONAL_SPORTS_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_PROFESSIONAL_SPORTS_QUOTE1',
					'TXT_KEY_CIVIC_PROFESSIONAL_SPORTS_QUOTE2'
				],
				era=EraType.atomic,
				cost=2185,
				required=[CivicType.ideology],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.rapidDeployment:
			# https://civilization.fandom.com/wiki/Rapid_Deployment_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_RAPID_DEPLOYMENT_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_RAPID_DEPLOYMENT_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_RAPID_DEPLOYMENT_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_RAPID_DEPLOYMENT_QUOTE1',
					'TXT_KEY_CIVIC_RAPID_DEPLOYMENT_QUOTE2'
				],
				era=EraType.atomic,
				cost=2415,
				required=[CivicType.coldWar],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.spaceRace:
			# https://civilization.fandom.com/wiki/Space_Race_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_SPACE_RACE_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_SPACE_RACE_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_SPACE_RACE_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_SPACE_RACE_QUOTE1',
					'TXT_KEY_CIVIC_SPACE_RACE_QUOTE2'
				],
				era=EraType.atomic,
				cost=2415,
				required=[CivicType.coldWar],
				flavors=[],
				governorTitle=False,
				envoys=0
			)

		# information
		elif self == CivicType.environmentalism:
			# https://civilization.fandom.com/wiki/Environmentalism_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_ENVIRONMENTALISM_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_ENVIRONMENTALISM_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_ENVIRONMENTALISM_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_ENVIRONMENTALISM_QUOTE1'
				],
				era=EraType.information,
				cost=2880,
				required=[CivicType.culturalHeritage, CivicType.rapidDeployment],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.globalization:
			# https://civilization.fandom.com/wiki/Globalization_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_GLOBALIZATION_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_GLOBALIZATION_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_GLOBALIZATION_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_GLOBALIZATION_QUOTE1',
					'TXT_KEY_CIVIC_GLOBALIZATION_QUOTE2'
				],
				era=EraType.information,
				cost=2880,
				required=[CivicType.rapidDeployment, CivicType.spaceRace],
				flavors=[],
				governorTitle=True,
				envoys=0
			)
		elif self == CivicType.socialMedia:
			# https://civilization.fandom.com/wiki/Social_Media_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_SOCIAL_MEDIA_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_SOCIAL_MEDIA_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_SOCIAL_MEDIA_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_SOCIAL_MEDIA_QUOTE1',
					'TXT_KEY_CIVIC_SOCIAL_MEDIA_QUOTE2'
				],
				era=EraType.information,
				cost=2880,
				required=[CivicType.professionalSports, CivicType.spaceRace],
				flavors=[
					Flavor(FlavorType.growth, 6)
				],
				governorTitle=True,
				envoys=0
			)
		elif self == CivicType.nearFutureGovernance:
			# https://civilization.fandom.com/wiki/Near_Future_Governance_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_NEAR_FUTURE_GOVERNANCE_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_NEAR_FUTURE_GOVERNANCE_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_NEAR_FUTURE_GOVERNANCE_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_NEAR_FUTURE_GOVERNANCE_QUOTE1'
				],
				era=EraType.future,
				cost=3100,
				required=[CivicType.environmentalism, CivicType.globalization],
				flavors=[],
				governorTitle=True,
				envoys=3
			)

		# Venture Politics
		# Distributed Sovereignty
		# Optimization Imperative

		# future
		elif self == CivicType.informationWarfare:
			# https://civilization.fandom.com/wiki/Information_Warfare_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_INFORMATION_WARFARE_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_INFORMATION_WARFARE_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_INFORMATION_WARFARE_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_INFORMATION_WARFARE_QUOTE1',
					'TXT_KEY_CIVIC_INFORMATION_WARFARE_QUOTE2'
				],
				era=EraType.future,
				cost=3200,
				required=[CivicType.socialMedia],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.globalWarmingMitigation:
			# https://civilization.fandom.com/wiki/Global_Warming_Mitigation_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_GLOBAL_WARMING_MITIGATION_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_GLOBAL_WARMING_MITIGATION_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_GLOBAL_WARMING_MITIGATION_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_GLOBAL_WARMING_MITIGATION_QUOTE1',
					'TXT_KEY_CIVIC_GLOBAL_WARMING_MITIGATION_QUOTE2'
				],
				era=EraType.future,
				cost=3200,
				required=[CivicType.informationWarfare],
				flavors=[],
				governorTitle=False,
				envoys=3
			)
		elif self == CivicType.culturalHegemony:
			# https://civilization.fandom.com/wiki/Cultural_Hegemony_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_CULTURAL_HEGEMONY_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_CULTURAL_HEGEMONY_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_CULTURAL_HEGEMONY_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_CULTURAL_HEGEMONY_QUOTE1'
				],
				era=EraType.future,
				cost=3200,
				required=[CivicType.globalWarmingMitigation],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.exodusImperative:
			# https://civilization.fandom.com/wiki/Exodus_Imperative_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_EXODUS_IMPERATIVE_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_EXODUS_IMPERATIVE_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_EXODUS_IMPERATIVE_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_EXODUS_IMPERATIVE_QUOTE1'
				],
				era=EraType.future,
				cost=3200,
				required=[CivicType.smartPowerDoctrine],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.smartPowerDoctrine:
			# https://civilization.fandom.com/wiki/Smart_Power_Doctrine_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_SMART_POWER_DOCTRINE_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_SMART_POWER_DOCTRINE_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_SMART_POWER_DOCTRINE_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_SMART_POWER_DOCTRINE_QUOTE1'
				],
				era=EraType.future,
				cost=3200,
				required=[CivicType.culturalHegemony],
				flavors=[],
				governorTitle=False,
				envoys=0
			)
		elif self == CivicType.futureCivic:
			# https://civilization.fandom.com/wiki/Future_Civic_(Civ6)
			return CivicTypeData(
				name='TXT_KEY_CIVIC_FUTURE_CIVIC_TITLE',
				inspiration_summary='TXT_KEY_CIVIC_FUTURE_CIVIC_EUREKA',
				inspiration_description='TXT_KEY_CIVIC_FUTURE_CIVIC_EUREKA_TEXT',
				quoteTexts=[
					'TXT_KEY_CIVIC_FUTURE_CIVIC_QUOTE1'
				],
				era=EraType.future,
				cost=3200,
				required=[CivicType.exodusImperative],
				flavors=[],
				governorTitle=True,
				envoys=0
			)

		raise AttributeError(f'cant get data for civic {self}')

	def __str__(self):
		return self.value
