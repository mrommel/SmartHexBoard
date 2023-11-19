from typing import Optional

from smarthexboard.smarthexboardlib.game.buildings import BuildingType
from smarthexboard.smarthexboardlib.game.districts import DistrictType
from smarthexboard.smarthexboardlib.game.flavors import Flavor, FlavorType
from smarthexboard.smarthexboardlib.game.greatworks import GreatWorkSlotType
from smarthexboard.smarthexboardlib.game.religions import ReligionType
from smarthexboard.smarthexboardlib.game.types import CivicType, TechType, EraType
from smarthexboard.smarthexboardlib.map.base import HexPoint
from smarthexboard.smarthexboardlib.map.improvements import ImprovementType
from smarthexboard.smarthexboardlib.map.types import Yields, FeatureType, TerrainType, ResourceType
from smarthexboard.smarthexboardlib.core.base import ExtendedEnum, InvalidEnumError


class WonderTypeData:
	def __init__(self, name: str, effects: [str], era: EraType, productionCost: int, requiredTech: Optional[TechType],
	             requiredCivic: Optional[CivicType], obsoleteEra: EraType, amenities: float, yields: Yields,
	             slots: [GreatWorkSlotType], flavors: [Flavor]):
		self.name = name
		self.effects = effects
		self.era = era
		self.productionCost = productionCost
		self.requiredTech = requiredTech
		self.requiredCivic = requiredCivic
		self.obsoleteEra = obsoleteEra
		self.amenities = amenities
		self.yields = yields
		self.slots = slots
		self.flavors = flavors


class WonderType:
	pass


class WonderType(ExtendedEnum):
	# default
	none = 'none'

	# ancient
	greatBath = 'greatBath'
	etemenanki = 'etemenanki'
	pyramids = 'pyramids'
	hangingGardens = 'hangingGardens'
	oracle = 'oracle'
	stonehenge = 'stonehenge'
	templeOfArtemis = 'templeOfArtemis'

	# classical
	greatLighthouse = 'greatLighthouse'
	greatLibrary = 'greatLibrary'
	apadana = 'apadana'
	colosseum = 'colosseum'
	colossus = 'colossus'
	jebelBarkal = 'jebelBarkal'
	mausoleumAtHalicarnassus = 'mausoleumAtHalicarnassus'
	mahabodhiTemple = 'mahabodhiTemple'
	petra = 'petra'
	terracottaArmy = 'terracottaArmy'
	machuPicchu = 'machuPicchu'
	statueOfZeus = 'statueOfZeus'

	# medieval
	alhambra = 'alhambra'
	angkorWat = 'angkorWat'
	chichenItza = 'chichenItza'
	hagiaSophia = 'hagiaSophia'
	hueyTeocalli = 'hueyTeocalli'
	kilwaKisiwani = 'kilwaKisiwani'
	kotokuIn = 'kotokuIn'
	meenakshiTemple = 'meenakshiTemple'
	montStMichel = 'montStMichel'
	universityOfSankore = 'universityOfSankore'

	# renaissance
	casaDeContratacion = 'casaDeContratacion'
	forbiddenCity = 'forbiddenCity'
	greatZimbabwe = 'greatZimbabwe'
	potalaPalace = 'potalaPalace'
	stBasilsCathedral = 'stBasilsCathedral'
	tajMahal = 'tajMahal'
	torreDeBelem = 'torreDeBelem'
	venetianArsenal = 'venetianArsenal'

	# industrial
	# Big Ben
	# Bolshoi Theatre
	# Hermitage
	# Országház
	# Oxford University
	# Panama Canal
	# Ruhr Valley
	# Statue of Liberty

	# modern
	# Broadway
	# Cristo Redentor
	# Eiffel Tower
	# Golden Gate Bridge

	# atomic
	# Amundsen - Scott Research Station
	# Biosphère
	# Estádio do Maracanã
	# Sydney Opera House

	@staticmethod
	def fromName(wonderName: str) -> WonderType:
		if wonderName == 'WonderType.none' or wonderName == 'none':
			return WonderType.none

		# ancient
		if wonderName == 'WonderType.greatBath' or wonderName == 'greatBath':
			return WonderType.greatBath
		if wonderName == 'WonderType.etemenanki' or wonderName == 'etemenanki':
			return WonderType.etemenanki
		if wonderName == 'WonderType.pyramids' or wonderName == 'pyramids':
			return WonderType.pyramids
		if wonderName == 'WonderType.hangingGardens' or wonderName == 'hangingGardens':
			return WonderType.hangingGardens
		if wonderName == 'WonderType.oracle' or wonderName == 'oracle':
			return WonderType.oracle
		if wonderName == 'WonderType.stonehenge' or wonderName == 'stonehenge':
			return WonderType.stonehenge
		if wonderName == 'WonderType.templeOfArtemis' or wonderName == 'templeOfArtemis':
			return WonderType.templeOfArtemis

		# classical
		if wonderName == 'WonderType.greatLighthouse' or wonderName == 'greatLighthouse':
			return WonderType.greatLighthouse
		if wonderName == 'WonderType.greatLibrary' or wonderName == 'greatLibrary':
			return WonderType.greatLibrary
		if wonderName == 'WonderType.apadana' or wonderName == 'apadana':
			return WonderType.apadana
		if wonderName == 'WonderType.colosseum' or wonderName == 'colosseum':
			return WonderType.colosseum
		if wonderName == 'WonderType.colossus' or wonderName == 'colossus':
			return WonderType.colossus
		if wonderName == 'WonderType.jebelBarkal' or wonderName == 'jebelBarkal':
			return WonderType.jebelBarkal
		if wonderName == 'WonderType.mausoleumAtHalicarnassus' or wonderName == 'mausoleumAtHalicarnassus':
			return WonderType.mausoleumAtHalicarnassus
		if wonderName == 'WonderType.mahabodhiTemple' or wonderName == 'mahabodhiTemple':
			return WonderType.mahabodhiTemple
		if wonderName == 'WonderType.petra' or wonderName == 'petra':
			return WonderType.petra
		if wonderName == 'WonderType.terracottaArmy' or wonderName == 'terracottaArmy':
			return WonderType.terracottaArmy
		if wonderName == 'WonderType.machuPicchu' or wonderName == 'machuPicchu':
			return WonderType.machuPicchu
		if wonderName == 'WonderType.statueOfZeus' or wonderName == 'statueOfZeus':
			return WonderType.statueOfZeus

		# medieval
		if wonderName == 'WonderType.alhambra' or wonderName == 'alhambra':
			return WonderType.alhambra
		if wonderName == 'WonderType.angkorWat' or wonderName == 'angkorWat':
			return WonderType.angkorWat
		if wonderName == 'WonderType.chichenItza' or wonderName == 'chichenItza':
			return WonderType.chichenItza
		if wonderName == 'WonderType.hagiaSophia' or wonderName == 'hagiaSophia':
			return WonderType.hagiaSophia
		if wonderName == 'WonderType.hueyTeocalli' or wonderName == 'hueyTeocalli':
			return WonderType.hueyTeocalli
		if wonderName == 'WonderType.kilwaKisiwani' or wonderName == 'kilwaKisiwani':
			return WonderType.kilwaKisiwani
		if wonderName == 'WonderType.kotokuIn' or wonderName == 'kotokuIn':
			return WonderType.kotokuIn
		if wonderName == 'WonderType.meenakshiTemple' or wonderName == 'meenakshiTemple':
			return WonderType.meenakshiTemple
		if wonderName == 'WonderType.montStMichel' or wonderName == 'montStMichel':
			return WonderType.montStMichel
		if wonderName == 'WonderType.universityOfSankore' or wonderName == 'universityOfSankore':
			return WonderType.universityOfSankore

		# renaissance
		if wonderName == 'WonderType.casaDeContratacion' or wonderName == 'casaDeContratacion':
			return WonderType.casaDeContratacion
		if wonderName == 'WonderType.forbiddenCity' or wonderName == 'forbiddenCity':
			return WonderType.forbiddenCity
		if wonderName == 'WonderType.greatZimbabwe' or wonderName == 'greatZimbabwe':
			return WonderType.greatZimbabwe
		if wonderName == 'WonderType.potalaPalace' or wonderName == 'potalaPalace':
			return WonderType.potalaPalace
		if wonderName == 'WonderType.stBasilsCathedral' or wonderName == 'stBasilsCathedral':
			return WonderType.stBasilsCathedral
		if wonderName == 'WonderType.tajMahal' or wonderName == 'tajMahal':
			return WonderType.tajMahal
		if wonderName == 'WonderType.torreDeBelem' or wonderName == 'torreDeBelem':
			return WonderType.torreDeBelem
		if wonderName == 'WonderType.venetianArsenal' or wonderName == 'venetianArsenal':
			return WonderType.venetianArsenal

		# industrial
		# Big Ben
		# Bolshoi Theatre
		# Hermitage
		# Országház
		# Oxford University
		# Panama Canal
		# Ruhr Valley
		# Statue of Liberty

		# modern
		# Broadway
		# Cristo Redentor
		# Eiffel Tower
		# Golden Gate Bridge

		# atomic
		# Amundsen - Scott Research Station
		# Biosphère
		# Estádio do Maracanã
		# Sydney Opera House

		raise Exception(f'No matching case for wonderName: "{wonderName}"')

	def name(self) -> str:
		return self._data().name

	def requiredCivic(self) -> Optional[CivicType]:
		return self._data().requiredCivic

	def requiredTech(self) -> Optional[TechType]:
		return self._data().requiredTech

	def obsoleteEra(self) -> EraType:
		return self._data().obsoleteEra

	def productionCost(self) -> float:
		return self._data().productionCost

	def amenities(self) -> float:
		return self._data().amenities

	def _flavors(self) -> [Flavor]:
		return self._data().flavors

	def flavor(self, flavorType: FlavorType) -> int:
		item = next((flavor for flavor in self._flavors() if flavor.flavorType == flavorType), None)

		if item is not None:
			return item.value

		return 0

	def _data(self) -> WonderTypeData:
		# https://civilization.fandom.com/wiki/Module:Data/Civ6/GS/Buildings

		# default
		if self == WonderType.none:
			return WonderTypeData(
				name='',
				effects=[],
				era=EraType.ancient,
				productionCost=-1,
				requiredTech=None,
				requiredCivic=None,
				obsoleteEra=EraType.future,
				amenities=0.0,
				yields=Yields(food=0.0, production=0.0, gold=0.0),
				slots=[],
				flavors=[]
			)

		# ancient
		elif self == WonderType.greatBath:
			# https://civilization.fandom.com/wiki/Great_Bath_(Civ6)
			return WonderTypeData(
				name="TXT_KEY_WONDER_GREAT_BATH_TITLE",
				effects=[
					'TXT_KEY_WONDER_GREAT_BATH_EFFECT1',
					'TXT_KEY_WONDER_GREAT_BATH_EFFECT2',
					'TXT_KEY_WONDER_GREAT_BATH_EFFECT3',
					'TXT_KEY_WONDER_GREAT_BATH_EFFECT4',
					'TXT_KEY_WONDER_GREAT_BATH_EFFECT5'
				],
				era=EraType.ancient,
				productionCost=180,
				requiredTech=TechType.pottery,
				requiredCivic=None,
				obsoleteEra=EraType.medieval,
				amenities=1.0,
				yields=Yields(food=0.0, production=0.0, gold=0.0, housing=3.0),
				slots=[],
				flavors=[
					Flavor(FlavorType.wonder, value=15),
					Flavor(FlavorType.religion, value=10)
				]
			)
		elif self == WonderType.etemenanki:
			# https://civilization.fandom.com/wiki/Etemenanki_(Civ6)
			return WonderTypeData(
				name='TXT_KEY_WONDER_ETEMENANKI_TITLE',
				effects=[
					'TXT_KEY_WONDER_ETEMENANKI_EFFECT1',
					'TXT_KEY_WONDER_ETEMENANKI_EFFECT2',
					'TXT_KEY_WONDER_ETEMENANKI_EFFECT3'
				],
				era=EraType.ancient,
				productionCost=220,
				requiredTech=TechType.writing,
				requiredCivic=None,
				obsoleteEra=EraType.medieval,
				amenities=0,
				yields=Yields(food=0.0, production=0.0, gold=0.0, science=2.0),
				slots=[],
				flavors=[
					Flavor(FlavorType.science, value=7),
					Flavor(FlavorType.production, value=3)
				]
			)
		elif self == WonderType.pyramids:
			# https://civilization.fandom.com/wiki/Pyramids_(Civ6)
			return WonderTypeData(
				name='TXT_KEY_WONDER_PYRAMIDS_TITLE',
				effects=[
					'TXT_KEY_WONDER_PYRAMIDS_EFFECT1',
					'TXT_KEY_WONDER_PYRAMIDS_EFFECT2',
					'TXT_KEY_WONDER_PYRAMIDS_EFFECT3'
				],
				era=EraType.ancient,
				productionCost=220,
				requiredTech=TechType.masonry,
				requiredCivic=None,
				obsoleteEra=EraType.medieval,
				amenities=0.0,
				yields=Yields(food=0.0, production=0.0, gold=0.0, culture=2.0),
				slots=[],
				flavors=[
					Flavor(FlavorType.wonder, value=25),
					Flavor(FlavorType.culture, value=20)
				]
			)
		elif self == WonderType.hangingGardens:
			# https://civilization.fandom.com/wiki/Hanging_Gardens_(Civ6)
			return WonderTypeData(
				name='TXT_KEY_WONDER_HANGING_GARDENS_TITLE',
				effects=[
					'TXT_KEY_WONDER_HANGING_GARDENS_EFFECT1',
					'TXT_KEY_WONDER_HANGING_GARDENS_EFFECT2'
				],
				era=EraType.ancient,
				productionCost=180,
				requiredTech=TechType.irrigation,
				requiredCivic=None,
				obsoleteEra=EraType.medieval,
				amenities=0.0,
				yields=Yields(food=0.0, production=0.0, gold=0.0, housing=2.0),
				slots=[],
				flavors=[
					Flavor(FlavorType.wonder, value=20),
					Flavor(FlavorType.growth, value=20)
				]
			)
		elif self == WonderType.oracle:
			# https://civilization.fandom.com/wiki/Oracle_(Civ6)
			return WonderTypeData(
				name='TXT_KEY_WONDER_ORACLE_TITLE',
				effects=[
					'TXT_KEY_WONDER_ORACLE_EFFECT1',
					'TXT_KEY_WONDER_ORACLE_EFFECT2',
					'TXT_KEY_WONDER_ORACLE_EFFECT3',  #
					'TXT_KEY_WONDER_ORACLE_EFFECT4'
				],
				era=EraType.ancient,
				productionCost=290,
				requiredTech=None,
				requiredCivic=CivicType.mysticism,
				obsoleteEra=EraType.medieval,
				amenities=0.0,
				yields=Yields(food=0.0, production=0.0, gold=0.0, culture=1.0, faith=1.0),
				slots=[],
				flavors=[
					Flavor(FlavorType.wonder, value=20),
					Flavor(FlavorType.culture, value=15)
				]
			)
		elif self == WonderType.stonehenge:
			# https://civilization.fandom.com/wiki/Stonehenge_(Civ6)
			return WonderTypeData(
				name='TXT_KEY_WONDER_STONEHENGE_TITLE',
				effects=[
					'TXT_KEY_WONDER_STONEHENGE_EFFECT1',
					'TXT_KEY_WONDER_STONEHENGE_EFFECT2'
				],
				era=EraType.ancient,
				productionCost=180,
				requiredTech=TechType.astrology,
				requiredCivic=None,
				obsoleteEra=EraType.medieval,
				amenities=0.0,
				yields=Yields(food=0.0, production=0.0, gold=0.0, faith=2.0),
				slots=[],
				flavors=[
					Flavor(FlavorType.wonder, value=25),
					Flavor(FlavorType.culture, value=20)
				]
			)
		elif self == WonderType.templeOfArtemis:
			# https://civilization.fandom.com/wiki/Temple_of_Artemis_(Civ6)
			return WonderTypeData(
				name='TXT_KEY_WONDER_TEMPLE_OF_ARTEMIS_TITLE',
				effects=[
					'TXT_KEY_WONDER_TEMPLE_OF_ARTEMIS_EFFECT1',
					'TXT_KEY_WONDER_TEMPLE_OF_ARTEMIS_EFFECT2',
					'TXT_KEY_WONDER_TEMPLE_OF_ARTEMIS_EFFECT3'
				],
				era=EraType.ancient,
				productionCost=180,
				requiredTech=TechType.archery,
				requiredCivic=None,
				obsoleteEra=EraType.medieval,
				amenities=0.0,
				yields=Yields(food=4.0, production=0.0, gold=0.0, housing=3.0),
				slots=[],
				flavors=[
					Flavor(FlavorType.wonder, value=20),
					Flavor(FlavorType.growth, value=10)
				]
			)

		# classical
		elif self == WonderType.greatLighthouse:
			# https://civilization.fandom.com/wiki/Great_Lighthouse_(Civ6)
			return WonderTypeData(
				name='TXT_KEY_WONDER_GREAT_LIGHTHOUSE_TITLE',
				effects=[
					'TXT_KEY_WONDER_GREAT_LIGHTHOUSE_EFFECT1',
					'TXT_KEY_WONDER_GREAT_LIGHTHOUSE_EFFECT2',
					'TXT_KEY_WONDER_GREAT_LIGHTHOUSE_EFFECT3'
				],
				era=EraType.classical,
				productionCost=290,
				requiredTech=TechType.celestialNavigation,
				requiredCivic=None,
				obsoleteEra=EraType.renaissance,
				amenities=0.0,
				yields=Yields(food=0.0, production=0.0, gold=3.0),
				slots=[],
				flavors=[
					Flavor(FlavorType.greatPeople, value=20),
					Flavor(FlavorType.gold, value=15),
					Flavor(FlavorType.navalGrowth, value=10),
					Flavor(FlavorType.navalRecon, value=8)
				]
			)
		elif self == WonderType.greatLibrary:
			# https://civilization.fandom.com/wiki/Great_Library_(Civ6)
			return WonderTypeData(
				name='TXT_KEY_WONDER_GREAT_LIBRARY_TITLE',
				effects=[
					'TXT_KEY_WONDER_GREAT_LIBRARY_EFFECT1',
					'TXT_KEY_WONDER_GREAT_LIBRARY_EFFECT2',
					'TXT_KEY_WONDER_GREAT_LIBRARY_EFFECT3',
					'TXT_KEY_WONDER_GREAT_LIBRARY_EFFECT4',
					'TXT_KEY_WONDER_GREAT_LIBRARY_EFFECT5'
				],
				era=EraType.classical,
				productionCost=400,
				requiredTech=None,
				requiredCivic=CivicType.recordedHistory,
				obsoleteEra=EraType.renaissance,
				amenities=0.0,
				yields=Yields(food=0.0, production=0.0, gold=0.0, science=2.0),
				slots=[GreatWorkSlotType.written, GreatWorkSlotType.written],
				flavors=[
					Flavor(FlavorType.science, value=20),
					Flavor(FlavorType.greatPeople, value=15)
				]
			)
		elif self == WonderType.apadana:
			# https://civilization.fandom.com/wiki/Apadana_(Civ6)
			return WonderTypeData(
				name='TXT_KEY_WONDER_APADANA_TITLE',
				effects=[
					'TXT_KEY_WONDER_APADANA_EFFECT1',
					'TXT_KEY_WONDER_APADANA_EFFECT2'  #
				],
				era=EraType.classical,
				productionCost=400,
				requiredTech=None,
				requiredCivic=CivicType.politicalPhilosophy,
				obsoleteEra=EraType.renaissance,
				amenities=0.0,
				yields=Yields(food=0.0, production=0.0, gold=0.0),
				slots=[GreatWorkSlotType.any, GreatWorkSlotType.any],
				flavors=[
					Flavor(FlavorType.diplomacy, value=20),
					Flavor(FlavorType.culture, value=7)
				]
			)
		elif self == WonderType.colosseum:
			# https://civilization.fandom.com/wiki/Colosseum_(Civ6)
			return WonderTypeData(
				name='TXT_KEY_WONDER_COLOSSEUM_TITLE',
				effects=[
					'TXT_KEY_WONDER_COLOSSEUM_EFFECT1'
				],
				era=EraType.classical,
				productionCost=400,
				requiredTech=None,
				requiredCivic=CivicType.gamesAndRecreation,
				obsoleteEra=EraType.renaissance,
				amenities=0.0,  # is handled differently !
				yields=Yields(food=0.0, production=0.0, gold=0.0, culture=2.0),
				slots=[],
				flavors=[
					Flavor(FlavorType.amenities, value=20),
					Flavor(FlavorType.culture, value=10)
				]
			)
		elif self == WonderType.colossus:
			# https://civilization.fandom.com/wiki/Colossus_(Civ6)
			return WonderTypeData(
				name='TXT_KEY_WONDER_COLOSSUS_TITLE',
				effects=[
					'TXT_KEY_WONDER_COLOSSUS_EFFECT1',
					'TXT_KEY_WONDER_COLOSSUS_EFFECT2',
					'TXT_KEY_WONDER_COLOSSUS_EFFECT3',
					'TXT_KEY_WONDER_COLOSSUS_EFFECT4'
				],
				era=EraType.classical,
				productionCost=400,
				requiredTech=TechType.shipBuilding,
				requiredCivic=None,
				obsoleteEra=EraType.renaissance,
				amenities=0.0,
				yields=Yields(food=0.0, production=0.0, gold=3.0),
				slots=[],
				flavors=[
					Flavor(FlavorType.gold, value=12),
					Flavor(FlavorType.naval, value=14),
					Flavor(FlavorType.navalRecon, value=3)
				]
			)
		elif self == WonderType.jebelBarkal:
			# https://civilization.fandom.com/wiki/Jebel_Barkal_(Civ6)
			return WonderTypeData(
				name='TXT_KEY_WONDER_JEBEL_BARKAL_TITLE',
				effects=[
					'TXT_KEY_WONDER_JEBEL_BARKAL_EFFECT1',  #
					'TXT_KEY_WONDER_JEBEL_BARKAL_EFFECT2'
				],
				era=EraType.classical,
				productionCost=400,
				requiredTech=TechType.ironWorking,
				requiredCivic=None,
				obsoleteEra=EraType.renaissance,
				amenities=0.0,
				yields=Yields(food=0.0, production=0.0, gold=0.0),
				slots=[],
				flavors=[
					Flavor(FlavorType.religion, value=12),
					Flavor(FlavorType.tileImprovement, value=7)
				]
			)
		elif self == WonderType.mausoleumAtHalicarnassus:
			# https://civilization.fandom.com/wiki/Mausoleum_at_Halicarnassus_(Civ6)
			return WonderTypeData(
				name='TXT_KEY_WONDER_MAUSOLEUM_AT_HALICARNASSUS_TITLE',
				effects=[
					'TXT_KEY_WONDER_MAUSOLEUM_AT_HALICARNASSUS_EFFECT1',
					'TXT_KEY_WONDER_MAUSOLEUM_AT_HALICARNASSUS_EFFECT2'  #
				],
				era=EraType.classical,
				productionCost=400,
				requiredTech=None,
				requiredCivic=CivicType.defensiveTactics,
				obsoleteEra=EraType.renaissance,
				amenities=0.0,
				yields=Yields(food=0.0, production=0.0, gold=0.0, science=1.0, faith=1.0),
				slots=[],
				flavors=[
					Flavor(FlavorType.tileImprovement, value=7),
					Flavor(FlavorType.science, value=5),
					Flavor(FlavorType.religion, value=5),
					Flavor(FlavorType.culture, value=7)
				]
			)
		elif self == WonderType.mahabodhiTemple:
			# https://civilization.fandom.com/wiki/Mahabodhi_Temple_(Civ6)
			return WonderTypeData(
				name='TXT_KEY_WONDER_MAHABODHI_TEMPLE_TITLE',
				effects=[
					'TXT_KEY_WONDER_MAHABODHI_TEMPLE_EFFECT1',
					'TXT_KEY_WONDER_MAHABODHI_TEMPLE_EFFECT2'  #
				],
				era=EraType.classical,
				productionCost=400,
				requiredTech=None,
				requiredCivic=CivicType.theology,
				obsoleteEra=EraType.renaissance,
				amenities=0.0,
				yields=Yields(food=0.0, production=0.0, gold=0.0, faith=4.0),
				slots=[],
				flavors=[
					Flavor(FlavorType.religion, value=20),
					Flavor(FlavorType.greatPeople, value=7)
				]
			)
		elif self == WonderType.petra:
			# https://civilization.fandom.com/wiki/Petra_(Civ6)
			return WonderTypeData(
				name='TXT_KEY_WONDER_PETRA_TITLE',
				effects=[
					'TXT_KEY_WONDER_PETRA_EFFECT1'
				],
				era=EraType.classical,
				productionCost=400,
				requiredTech=TechType.mathematics,
				requiredCivic=None,
				obsoleteEra=EraType.renaissance,
				amenities=0.0,
				yields=Yields(food=2.0, production=1.0, gold=2.0),
				slots=[],
				flavors=[
					Flavor(FlavorType.tileImprovement, value=10),
					Flavor(FlavorType.growth, value=12),
					Flavor(FlavorType.gold, value=10)
				]
			)
		elif self == WonderType.terracottaArmy:
			# https://civilization.fandom.com/wiki/Terracotta_Army_(Civ6)
			return WonderTypeData(
				name='TXT_KEY_WONDER_TERRACOTTA_ARMY_TITLE',
				effects=[
					'TXT_KEY_WONDER_TERRACOTTA_ARMY_EFFECT1',
					'TXT_KEY_WONDER_TERRACOTTA_ARMY_EFFECT2'  #
				],
				era=EraType.classical,
				productionCost=400,
				requiredTech=TechType.construction,
				requiredCivic=None,
				obsoleteEra=EraType.renaissance,
				amenities=0.0,
				yields=Yields(food=0.0, production=0.0, gold=0.0),
				slots=[],
				flavors=[
					Flavor(FlavorType.greatPeople, value=10),
					Flavor(FlavorType.militaryTraining, value=7)
				]
			)
		elif self == WonderType.machuPicchu:
			# https://civilization.fandom.com/wiki/Machu_Picchu_(Civ6)
			return WonderTypeData(
				name='TXT_KEY_WONDER_MACHU_PICCHU_TITLE',
				effects=[
					'TXT_KEY_WONDER_MACHU_PICCHU_EFFECT1',
					'TXT_KEY_WONDER_MACHU_PICCHU_EFFECT2'  #
				],
				era=EraType.classical,
				productionCost=400,
				requiredTech=TechType.engineering,
				requiredCivic=None,
				obsoleteEra=EraType.renaissance,
				amenities=0,
				yields=Yields(food=0.0, production=0.0, gold=4.0),
				slots=[],
				flavors=[
					Flavor(FlavorType.production, value=7)
				]
			)
		elif self == WonderType.statueOfZeus:
			# https://civilization.fandom.com/wiki/Statue_of_Zeus_(Civ6)
			return WonderTypeData(
				name='TXT_KEY_WONDER_STATUE_OF_ZEUS_TITLE',
				effects=[
					'TXT_KEY_WONDER_STATUE_OF_ZEUS_EFFECT1',
					'TXT_KEY_WONDER_STATUE_OF_ZEUS_EFFECT2',
					'TXT_KEY_WONDER_STATUE_OF_ZEUS_EFFECT3'
				],
				era=EraType.classical,
				productionCost=400,
				requiredTech=None,
				requiredCivic=CivicType.militaryTraining,
				obsoleteEra=EraType.renaissance,
				amenities=0,
				yields=Yields(food=0.0, production=0.0, gold=3.0),
				slots=[],
				flavors=[
					Flavor(FlavorType.gold, value=7)
				]
			)

		# ####
		elif self == WonderType.hueyTeocalli:
			# https://civilization.fandom.com/wiki/Huey_Teocalli_(Civ6)
			return WonderTypeData(
				name="TXT_KEY_WONDER_HUEY_TEOCALLI_TITLE",
				effects=[
					"TXT_KEY_WONDER_HUEY_TEOCALLI_EFFECT1",
					"TXT_KEY_WONDER_HUEY_TEOCALLI_EFFECT2"
				],
				era=EraType.medieval,
				productionCost=710,
				requiredTech=TechType.militaryTactics,
				requiredCivic=None,
				obsoleteEra=EraType.industrial,
				amenities=0,
				yields=Yields(food=0.0, production=0.0, gold=0.0),
				slots=[],
				flavors=[
					Flavor(FlavorType.growth, value=7)
				]
			)
		elif self == WonderType.stBasilsCathedral:
			# https://civilization.fandom.com/wiki/St._Basil%27s_Cathedral_(Civ6)
			return WonderTypeData(
				name="TXT_KEY_WONDER_ST_BASILS_CATHEDRAL_TITLE",
				effects=[
					"TXT_KEY_WONDER_ST_BASILS_CATHEDRAL_EFFECT1",
					"TXT_KEY_WONDER_ST_BASILS_CATHEDRAL_EFFECT2",  #
					"TXT_KEY_WONDER_ST_BASILS_CATHEDRAL_EFFECT3"  #
				],
				era=EraType.renaissance,
				productionCost=920,
				requiredTech=None,
				requiredCivic=CivicType.reformedChurch,
				obsoleteEra=EraType.modern,
				amenities=0.0,
				yields=Yields(food=0.0, production=0.0, gold=0.0),
				slots=[GreatWorkSlotType.relic, GreatWorkSlotType.relic, GreatWorkSlotType.relic],
				flavors=[
					Flavor(FlavorType.religion, value=10)
				]
			)
		elif self == WonderType.angkorWat:
			# https://civilization.fandom.com/wiki/Angkor_Wat_(Civ6)
			return WonderTypeData(
				name="TXT_KEY_WONDER_ANGKOR_WAT_TITLE",
				effects=[
					"TXT_KEY_WONDER_ANGKOR_WAT_EFFECT1",
					"TXT_KEY_WONDER_ANGKOR_WAT_EFFECT2",
					"TXT_KEY_WONDER_ANGKOR_WAT_EFFECT3"
				],
				era=EraType.medieval,
				productionCost=710,
				requiredTech=None,
				requiredCivic=CivicType.medievalFaires,
				obsoleteEra=EraType.industrial,
				amenities=0,
				yields=Yields(food=0.0, production=0.0, gold=0.0, faith=2),
				slots=[],
				flavors=[
					Flavor(FlavorType.growth, value=10),
					Flavor(FlavorType.religion, value=2)
				]
			)
		elif self == WonderType.chichenItza:
			# https://civilization.fandom.com/wiki/Chichen_Itza_(Civ6)
			return WonderTypeData(
				name="TXT_KEY_WONDER_CHICHEN_ITZA_TITLE",
				effects=[
					"TXT_KEY_WONDER_CHICHEN_ITZA_EFFECT1"
				],
				era=EraType.medieval,
				productionCost=710,
				requiredTech=None,
				requiredCivic=CivicType.guilds,
				obsoleteEra=EraType.industrial,
				amenities=0,
				yields=Yields(food=0.0, production=0.0, gold=0.0),
				slots=[],
				flavors=[
					Flavor(FlavorType.production, value=4)
				]
			)

		# medieval
		elif self == WonderType.alhambra:
			# https://civilization.fandom.com/wiki/Alhambra_(Civ6)
			return WonderTypeData(
				name="TXT_KEY_WONDER_ALHAMBRA_TITLE",
				effects=[
					"TXT_KEY_WONDER_ALHAMBRA_EFFECT1",
					"TXT_KEY_WONDER_ALHAMBRA_EFFECT2",
					"TXT_KEY_WONDER_ALHAMBRA_EFFECT3",
					"TXT_KEY_WONDER_ALHAMBRA_EFFECT4"  #
				],
				era=EraType.medieval,
				productionCost=710,
				requiredTech=TechType.castles,
				requiredCivic=None,
				obsoleteEra=EraType.industrial,
				amenities=2,
				yields=Yields(food=0.0, production=0.0, gold=0.0),
				slots=[],
				flavors=[
					Flavor(FlavorType.greatPeople, value=8),
					Flavor(FlavorType.cityDefense, value=5)
				]
			)
		elif self == WonderType.angkorWat:
			# https://civilization.fandom.com/wiki/Angkor_Wat_(Civ6)
			return WonderTypeData(
				name="TXT_KEY_WONDER_ANGKOR_WAT_TITLE",
				effects=[
					"TXT_KEY_WONDER_ANGKOR_WAT_EFFECT1",
					"TXT_KEY_WONDER_ANGKOR_WAT_EFFECT2",
					"TXT_KEY_WONDER_ANGKOR_WAT_EFFECT3"
				],
				era=EraType.medieval,
				productionCost=710,
				requiredTech=None,
				requiredCivic=CivicType.medievalFaires,
				obsoleteEra=EraType.industrial,
				amenities=0,
				yields=Yields(food=0.0, production=0.0, gold=0.0, faith=2),
				slots=[],
				flavors=[
					Flavor(FlavorType.growth, value=10),
					Flavor(FlavorType.religion, value=2)
				]
			)
		elif self == WonderType.chichenItza:
			# https://civilization.fandom.com/wiki/Chichen_Itza_(Civ6)
			return WonderTypeData(
				name="TXT_KEY_WONDER_CHICHEN_ITZA_TITLE",
				effects=[
					"TXT_KEY_WONDER_CHICHEN_ITZA_EFFECT1"
				],
				era=EraType.medieval,
				productionCost=710,
				requiredTech=None,
				requiredCivic=CivicType.guilds,
				obsoleteEra=EraType.industrial,
				amenities=0,
				yields=Yields(food=0.0, production=0.0, gold=0.0),
				slots=[],
				flavors=[
					Flavor(FlavorType.production, value=4)
				]
			)
		elif self == WonderType.hagiaSophia:
			# https://civilization.fandom.com/wiki/Hagia_Sophia_(Civ6)
			return WonderTypeData(
				name="TXT_KEY_WONDER_HAGIA_SOPHIA_TITLE",
				effects=[
					"TXT_KEY_WONDER_HAGIA_SOPHIA_EFFECT1",
					"TXT_KEY_WONDER_HAGIA_SOPHIA_EFFECT2"  #
				],
				era=EraType.medieval,
				productionCost=710,
				requiredTech=TechType.buttress,
				requiredCivic=None,
				obsoleteEra=EraType.industrial,
				amenities=0,
				yields=Yields(food=0.0, production=0.0, gold=0.0, faith=4),
				slots=[],
				flavors=[
					Flavor(FlavorType.religion, value=10)
				]
			)
		elif self == WonderType.hueyTeocalli:
			# https://civilization.fandom.com/wiki/Huey_Teocalli_(Civ6)
			return WonderTypeData(
				name="TXT_KEY_WONDER_HUEY_TEOCALLI_TITLE",
				effects=[
					"TXT_KEY_WONDER_HUEY_TEOCALLI_EFFECT1",
					"TXT_KEY_WONDER_HUEY_TEOCALLI_EFFECT2"
				],
				era=EraType.medieval,
				productionCost=710,
				requiredTech=TechType.militaryTactics,
				requiredCivic=None,
				obsoleteEra=EraType.industrial,
				amenities=0,
				yields=Yields(food=0.0, production=0.0, gold=0.0),
				slots=[],
				flavors=[
					Flavor(FlavorType.growth, value=7)
				]
			)
		elif self == WonderType.kilwaKisiwani:
			# https://civilization.fandom.com/wiki/Kilwa_Kisiwani_(Civ6)
			return WonderTypeData(
				name="TXT_KEY_WONDER_KILWA_KISIWANI_TITLE",
				effects=[
					"TXT_KEY_WONDER_KILWA_KISIWANI_EFFECT1",  #
					"TXT_KEY_WONDER_KILWA_KISIWANI_EFFECT2"  #
				],
				era=EraType.medieval,
				productionCost=710,
				requiredTech=TechType.machinery,
				requiredCivic=None,
				obsoleteEra=EraType.industrial,
				amenities=0,
				yields=Yields(food=0.0, production=0.0, gold=0.0),
				slots=[],
				flavors=[
					Flavor(FlavorType.diplomacy, value=4)
				]
			)
		elif self == WonderType.kotokuIn:
			# https://civilization.fandom.com/wiki/Kotoku-in_(Civ6)
			return WonderTypeData(
				name="TXT_KEY_WONDER_KOTOKU_IN_TITLE",
				effects=[
					"TXT_KEY_WONDER_KOTOKU_IN_EFFECT1",
					"TXT_KEY_WONDER_KOTOKU_IN_EFFECT2"  #
				],
				era=EraType.medieval,
				productionCost=710,
				requiredTech=None,
				requiredCivic=CivicType.divineRight,
				obsoleteEra=EraType.industrial,
				amenities=0,
				yields=Yields(food=0.0, production=0.0, gold=0.0),
				slots=[],
				flavors=[
					Flavor(FlavorType.religion, value=10)
				]
			)
		elif self == WonderType.meenakshiTemple:
			# https://civilization.fandom.com/wiki/Meenakshi_Temple_(Civ6)
			return WonderTypeData(
				name="TXT_KEY_WONDER_MEENAKSHI_TEMPLE_TITLE",
				effects=[
					"TXT_KEY_WONDER_MEENAKSHI_TEMPLE_EFFECT1",
					"TXT_KEY_WONDER_MEENAKSHI_TEMPLE_EFFECT2",  #
					"TXT_KEY_WONDER_MEENAKSHI_TEMPLE_EFFECT3",  #
					"TXT_KEY_WONDER_MEENAKSHI_TEMPLE_EFFECT4"  #
				],
				era=EraType.medieval,
				productionCost=710,
				requiredTech=None,
				requiredCivic=CivicType.civilService,
				obsoleteEra=EraType.industrial,
				amenities=0,
				yields=Yields(food=0.0, production=0.0, gold=0.0, faith=3),
				slots=[],
				flavors=[
					Flavor(FlavorType.religion, value=10)
				]
			)
		elif self == WonderType.montStMichel:
			# https://civilization.fandom.com/wiki/Mont_St._Michel_(Civ6)
			return WonderTypeData(
				name="TXT_KEY_WONDER_MONT_ST_MICHEL_TITLE",
				effects=[
					"TXT_KEY_WONDER_MONT_ST_MICHEL_EFFECT1",
					"TXT_KEY_WONDER_MONT_ST_MICHEL_EFFECT2",
					"TXT_KEY_WONDER_MONT_ST_MICHEL_EFFECT3"  #
				],
				era=EraType.medieval,
				productionCost=710,
				requiredTech=None,
				requiredCivic=CivicType.divineRight,
				obsoleteEra=EraType.industrial,
				amenities=0,
				yields=Yields(food=0.0, production=0.0, gold=0.0, faith=2),
				slots=[GreatWorkSlotType.relic, GreatWorkSlotType.relic],
				flavors=[
					Flavor(FlavorType.religion, value=10)
				]
			)
		elif self == WonderType.universityOfSankore:
			# https://civilization.fandom.com/wiki/University_of_Sankore_(Civ6)
			return WonderTypeData(
				name="TXT_KEY_WONDER_UNIVERSITY_OF_SANKORE_TITLE",
				effects=[
					"TXT_KEY_WONDER_UNIVERSITY_OF_SANKORE_EFFECT1",
					"TXT_KEY_WONDER_UNIVERSITY_OF_SANKORE_EFFECT2",
					"TXT_KEY_WONDER_UNIVERSITY_OF_SANKORE_EFFECT3",  #
					"TXT_KEY_WONDER_UNIVERSITY_OF_SANKORE_EFFECT4",  #
					"TXT_KEY_WONDER_UNIVERSITY_OF_SANKORE_EFFECT5",  #
					"TXT_KEY_WONDER_UNIVERSITY_OF_SANKORE_EFFECT6"  #
				],
				era=EraType.medieval,
				productionCost=710,
				requiredTech=TechType.education,
				requiredCivic=None,
				obsoleteEra=EraType.industrial,
				amenities=0,
				yields=Yields(food=0.0, production=0.0, gold=0.0, science=3, faith=1),
				slots=[],
				flavors=[
					Flavor(FlavorType.science, value=8),
					Flavor(FlavorType.gold, value=3)
				]
			)

		# renaissance
		elif self == WonderType.casaDeContratacion:
			# https://civilization.fandom.com/wiki/Casa_de_Contrataci%C3%B3n_(Civ6)
			return WonderTypeData(
				name="TXT_KEY_WONDER_CASA_DE_CONTRATACIO_TITLE",
				effects=[
					"TXT_KEY_WONDER_CASA_DE_CONTRATACIO_EFFECT1",  #
					"TXT_KEY_WONDER_CASA_DE_CONTRATACIO_EFFECT2",  #
					"TXT_KEY_WONDER_CASA_DE_CONTRATACIO_EFFECT3"  #
				],
				era=EraType.renaissance,
				productionCost=920,
				requiredTech=TechType.cartography,
				requiredCivic=None,
				obsoleteEra=EraType.modern,
				amenities=0.0,
				yields=Yields(food=0.0, production=0.0, gold=0.0),
				slots=[],
				flavors=[
					Flavor(FlavorType.greatPeople, value=8)
				]
			)
		elif self == WonderType.forbiddenCity:
			# https://civilization.fandom.com/wiki/Forbidden_City_(Civ6)
			return WonderTypeData(
				name="TXT_KEY_WONDER_FORBIDDEN_CITY_TITLE",
				effects=[
					"TXT_KEY_WONDER_FORBIDDEN_CITY_EFFECT1",  #
					"TXT_KEY_WONDER_FORBIDDEN_CITY_EFFECT2"
				],
				era=EraType.renaissance,
				productionCost=920,
				requiredTech=TechType.printing,
				requiredCivic=None,
				obsoleteEra=EraType.modern,
				amenities=0.0,
				yields=Yields(food=0.0, production=0.0, gold=0.0, culture=5.0),
				slots=[],
				flavors=[
					Flavor(FlavorType.culture, value=8)
				]
			)
		elif self == WonderType.greatZimbabwe:
			# https://civilization.fandom.com/wiki/Great_Zimbabwe_(Civ6)
			return WonderTypeData(
				name="TXT_KEY_WONDER_GREAT_ZIMBABWE_TITLE",
				effects=[
					"TXT_KEY_WONDER_GREAT_ZIMBABWE_EFFECT1",  #
					"TXT_KEY_WONDER_GREAT_ZIMBABWE_EFFECT2",
					"TXT_KEY_WONDER_GREAT_ZIMBABWE_EFFECT3",  #
					"TXT_KEY_WONDER_GREAT_ZIMBABWE_EFFECT4"  #
				],
				era=EraType.renaissance,
				productionCost=920,
				requiredTech=TechType.banking,
				requiredCivic=None,
				obsoleteEra=EraType.modern,
				amenities=0.0,
				yields=Yields(food=0.0, production=0.0, gold=5.0),
				slots=[],
				flavors=[
					Flavor(FlavorType.gold, value=8)
				]
			)
		elif self == WonderType.potalaPalace:
			# https://civilization.fandom.com/wiki/Potala_Palace_(Civ6)
			return WonderTypeData(
				name="TXT_KEY_WONDER_POTALA_PALACE_TITLE",
				effects=[
					"TXT_KEY_WONDER_POTALA_PALACE_EFFECT1",  #
					"TXT_KEY_WONDER_POTALA_PALACE_EFFECT2",
					"TXT_KEY_WONDER_POTALA_PALACE_EFFECT3",
					"TXT_KEY_WONDER_POTALA_PALACE_EFFECT4"  #
				],
				era=EraType.renaissance,
				productionCost=1060,
				requiredTech=TechType.astronomy,
				requiredCivic=None,
				obsoleteEra=EraType.modern,
				amenities=0.0,
				yields=Yields(food=0.0, production=0.0, gold=0.0, culture=2.0, faith=3.0),
				slots=[],
				flavors=[
					Flavor(FlavorType.diplomacy, value=7),
					Flavor(FlavorType.culture, value=3),
					Flavor(FlavorType.religion, value=3)
				]
			)
		elif self == WonderType.stBasilsCathedral:
			# https://civilization.fandom.com/wiki/St._Basil%27s_Cathedral_(Civ6)
			return WonderTypeData(
				name="TXT_KEY_WONDER_ST_BASILS_CATHEDRAL_TITLE",
				effects=[
					"TXT_KEY_WONDER_ST_BASILS_CATHEDRAL_EFFECT1",
					"TXT_KEY_WONDER_ST_BASILS_CATHEDRAL_EFFECT2",  #
					"TXT_KEY_WONDER_ST_BASILS_CATHEDRAL_EFFECT3"  #
				],
				era=EraType.renaissance,
				productionCost=920,
				requiredTech=None,
				requiredCivic=CivicType.reformedChurch,
				obsoleteEra=EraType.modern,
				amenities=0.0,
				yields=Yields(food=0.0, production=0.0, gold=0.0),
				slots=[GreatWorkSlotType.relic, GreatWorkSlotType.relic, GreatWorkSlotType.relic],
				flavors=[
					Flavor(FlavorType.religion, value=10)
				]
			)
		elif self == WonderType.tajMahal:
			# https://civilization.fandom.com/wiki/Taj_Mahal_(Civ6)
			return WonderTypeData(
				name="TXT_KEY_WONDER_TAJ_MAHAL_TITLE",
				effects=[
					"TXT_KEY_WONDER_TAJ_MAHAL_EFFECT1"  #
				],
				era=EraType.renaissance,
				productionCost=920,
				requiredTech=None,
				requiredCivic=CivicType.humanism,
				obsoleteEra=EraType.information,
				amenities=0.0,
				yields=Yields(food=0.0, production=0.0, gold=0.0),
				slots=[],
				flavors=[
					Flavor(FlavorType.religion, value=2)
				]
			)
		elif self == WonderType.torreDeBelem:
			# https://civilization.fandom.com/wiki/Torre_de_Bel%C3%A9m_(Civ6)
			return WonderTypeData(
				name="TXT_KEY_WONDER_TORRE_DE_BELEM_TITLE",
				effects=[
					"TXT_KEY_WONDER_TORRE_DE_BELEM_EFFECT1",  #
					"TXT_KEY_WONDER_TORRE_DE_BELEM_EFFECT2",  #
					"TXT_KEY_WONDER_TORRE_DE_BELEM_EFFECT3",
					"TXT_KEY_WONDER_TORRE_DE_BELEM_EFFECT4"  #
				],
				era=EraType.renaissance,
				productionCost=920,
				requiredTech=None,
				requiredCivic=CivicType.mercantilism,
				obsoleteEra=EraType.modern,
				amenities=0.0,
				yields=Yields(food=0.0, production=0.0, gold=5.0),
				slots=[],
				flavors=[
					Flavor(FlavorType.gold, value=8)
				]
			)
		elif self == WonderType.venetianArsenal:
			# https://civilization.fandom.com/wiki/Venetian_Arsenal_(Civ6)
			return WonderTypeData(
				name="TXT_KEY_WONDER_VENETIAN_ARSENAL_TITLE",
				effects=[
					"TXT_KEY_WONDER_VENETIAN_ARSENAL_EFFECT1",  #
					"TXT_KEY_WONDER_VENETIAN_ARSENAL_EFFECT2"  #
				],
				era=EraType.renaissance,
				productionCost=920,
				requiredTech=TechType.massProduction,
				requiredCivic=None,
				obsoleteEra=EraType.modern,
				amenities=0.0,
				yields=Yields(food=0.0, production=0.0, gold=0.0),
				slots=[],
				flavors=[
					Flavor(FlavorType.navalGrowth, value=8),
					Flavor(FlavorType.naval, value=3)
				]
			)

		raise AttributeError(f'cant get data for wonder {self}')

	def canBuildOn(self, location: HexPoint, simulation):
		tile = simulation.tileAt(location)
		hasReligion = False if tile.owner() is None else tile.owner().religion.currentReligion() != ReligionType.none

		if self == WonderType.none:
			return False

		elif self == WonderType.greatBath:
			# It must be built on Floodplains.
			return tile.hasFeature(FeatureType.floodplains)

		elif self == WonderType.etemenanki:
			# Must be built on Floodplains or Marsh.
			return tile.hasFeature(FeatureType.floodplains) or tile.hasFeature(FeatureType.marsh)

		elif self == WonderType.pyramids:
			# Must be built on Desert(including Floodplains) without Hills.
			if not tile.isLand() or tile.isHills():
				return False

			# no mountains
			if tile.hasFeature(FeatureType.mountains):
				return False

			return tile.terrain() == TerrainType.desert or tile.hasFeature(FeatureType.floodplains)

		elif self == WonderType.hangingGardens:
			# no mountains
			if tile.hasFeature(FeatureType.mountains):
				return False

			# Must be built next to a River.
			return simulation.riverAt(location)

		elif self == WonderType.oracle:
			# Must be built on Hills.
			if not tile.isLand() or not tile.isHills():
				return False

			# no mountains
			if tile.hasFeature(FeatureType.mountains):
				return False

			return True

		elif self == WonderType.stonehenge:
			# no mountains
			if tile.hasFeature(FeatureType.mountains):
				return False

			# Must be built on flat land adjacent to Stone.
			if not tile.isLand() or tile.isHills():
				return False

			return self.adjacentToResource(ResourceType.stone, location, simulation)

		elif self == WonderType.templeOfArtemis:
			# no mountains
			if tile.hasFeature(FeatureType.mountains):
				return False

			# Must be built next to a Camp.
			return self.adjacentToImprovement(ImprovementType.camp, location, simulation)

		elif self == WonderType.greatLighthouse:
			# Must be built on the Coast and adjacent to a Harbor district with a Lighthouse.
			if not tile.terrain() == TerrainType.shore:
				return False

			if not self.adjacentToBuilding(BuildingType.lighthouse, location, simulation):
				return False

			return self.adjacentToDistrict(DistrictType.harbor, location, simulation)

		elif self == WonderType.greatLibrary:
			# Must be built on flat land adjacent to a Campus with a Library.
			if not tile.isLand() or tile.isHills():
				return False

			# no mountains
			if tile.hasFeature(FeatureType.mountains):
				return False

			if not self.adjacentToBuilding(BuildingType.library, location, simulation):
				return False

			return self.adjacentToDistrict(DistrictType.campus, location, simulation)

		elif self == WonderType.apadana:
			# no mountains
			if tile.hasFeature(FeatureType.mountains):
				return False

			# Must be built adjacent to a Capital.
			for player in simulation.players:
				for city in simulation.citiesOf(player):
					if city.isCapital() and location.isNeighborOf(city.location):
						return True

			return False

		elif self == WonderType.colosseum:
			# Must be built on flat land adjacent to an Entertainment Complex district with an Arena.
			if not tile.isLand() or tile.isHills():
				return False

			# no mountains
			if tile.hasFeature(FeatureType.mountains):
				return False

			if not self.adjacentToBuilding(BuildingType.arena, location, simulation):
				return False

			return self.adjacentToDistrict(DistrictType.entertainmentComplex, location, simulation)

		elif self == WonderType.colossus:
			# Must be built on Coast and adjacent to a Harbor district.
			if not tile.terrain() == TerrainType.shore:
				return False

			return self.adjacentToDistrict(DistrictType.harbor, location, simulation)

		elif self == WonderType.jebelBarkal:
			# no mountains
			if tile.hasFeature(FeatureType.mountains):
				return False

			# Must be built on a Desert Hills tile.
			return tile.terrain() == TerrainType.desert

		elif self == WonderType.mausoleumAtHalicarnassus:
			# Must be built on a coastal tile adjacent to a Harbor district.
			if not simulation.isCoastalAt(location):
				return False

			return self.adjacentToDistrict(DistrictType.harbor, location, simulation)

		elif self == WonderType.mahabodhiTemple:
			# Must be built on Woods adjacent to a Holy Site district with a Temple,
			# and player must have founded a religion.
			if not tile.hasFeature(FeatureType.forest):
				return False

			if not hasReligion:
				return False

			if not self.adjacentToBuilding(BuildingType.temple, location, simulation):
				return False

			return self.adjacentToDistrict(DistrictType.holySite, location, simulation)

		elif self == WonderType.petra:
			# Must be built on Desert or Floodplains without Hills.
			if not tile.isLand() or tile.isHills():
				return False

			# no mountains
			if tile.hasFeature(FeatureType.mountains):
				return False

			return tile.terrain() == TerrainType.desert or tile.hasFeature(FeatureType.floodplains)

		elif self == WonderType.terracottaArmy:
			# Must be built on flat Grassland or Plains adjacent to an Encampment district with a Barracks or Stable.
			if not tile.isLand() or tile.isHills():
				return False

			# no mountains
			if tile.hasFeature(FeatureType.mountains):
				return False

			if tile.terrain() != TerrainType.grass and tile.terrain() != TerrainType.plains:
				return False

			if not self.adjacentToBuilding(BuildingType.barracks, location, simulation) and \
				not self.adjacentToBuilding(BuildingType.stable, location, simulation):
				return False

			return self.adjacentToDistrict(DistrictType.encampment, location, simulation)

		elif self == WonderType.machuPicchu:
			# Must be built on a Mountain tile that does not contain a Volcano.
			return tile.hasFeature(FeatureType.mountains)

		elif self == WonderType.statueOfZeus:
			# Must be built on flat land adjacent to an Encampment with a Barracks.
			if not tile.isLand() or tile.isHills():
				return False
			
			# no mountains
			if tile.hasFeature(FeatureType.mountains):
				return False
			
			if not self.adjacentToBuilding(BuildingType.barracks, location, simulation):
				return False
			
			return self.adjacentToDistrict(DistrictType.encampment, location, simulation)

		elif self == WonderType.alhambra:
			# Must be built on Hills adjacent to an Encampment district.
			if not tile.isHills():
				return False

			# no mountains
			if tile.hasFeature(FeatureType.mountains):
				return False

			return self.adjacentToDistrict(DistrictType.encampment, location, simulation)

		elif self == WonderType.angkorWat:
			# no mountains
			if tile.hasFeature(FeatureType.mountains):
				return False

			# Must be built adjacent to an Aqueduct district.
			return self.adjacentToDistrict(DistrictType.aqueduct, location, simulation)

		elif self == WonderType.chichenItza:
			# no  mountains
			if tile.hasFeature(FeatureType.mountains):
				return False

			# Must be built on Rainforest.
			return tile.hasFeature(FeatureType.rainforest)

		elif self == WonderType.hagiaSophia:
			# Must be built on flat land adjacent to a Holy Site district, and player must have founded a religion.
			if tile.isHills() or not tile.isLand():
				return False

			# no mountains
			if tile.hasFeature(FeatureType.mountains):
				return False

			if not hasReligion:
				return False

			return self.adjacentToDistrict(DistrictType.holySite, location, simulation)

		elif self == WonderType.hueyTeocalli:
			# Must be built on a Lake tile adjacent to land.
			if not tile.hasFeature(FeatureType.lake):
				return False
			
			nextToLand: bool = False
			
			for neighbor in location.neighbors():
				neighborTile = simulation.tileAt(neighbor)

				if neighborTile is None:
					continue
			
				if neighborTile.isLand():
					nextToLand = True
			
			return nextToLand
			
		elif self == WonderType.kilwaKisiwani:
			# Must be built on a flat tile adjacent to a Coast.
			if tile.isHills() or not tile.isLand():
				return False
			
			# no mountains
			if tile.hasFeature(FeatureType.mountains):
				return False
			
			nextToCoast: bool = False
			
			for neighbor in location.neighbors():
				neighborTile = simulation.tileAt(neighbor)

				if neighborTile is None:
					continue
			
				if neighborTile.isWater():
					nextToCoast = True
			
			return nextToCoast

		elif self == WonderType.kotokuIn:
			# no mountains
			if tile.hasFeature(FeatureType.mountains):
				return False
			
			# Must be built adjacent to a Holy Site with a Temple.
			if not self.adjacentToDistrict(DistrictType.holySite, location, simulation):
				return False
			
			if not self.adjacentToBuilding(BuildingType.temple, location, simulation):
				return False
			
			return True

		elif self == WonderType.meenakshiTemple:
			# no mountains
			if tile.hasFeature(FeatureType.mountains):
				return False
			
			# Must be built adjacent to a Holy Site district, and player must have founded a religion.
			if not hasReligion:
				return False
			
			return self.adjacentToDistrict(DistrictType.holySite, location, simulation)

		elif self == WonderType.montStMichel:
			# no mountains
			if tile.hasFeature(FeatureType.mountains):
				return False
			
			# Must be built on Floodplains or Marsh.
			if not tile.hasFeature(FeatureType.floodplains) and not tile.hasFeature(FeatureType.marsh):
				return False
			
			return True

		elif self == WonderType.universityOfSankore:
			# Must be built on a Desert or Desert Hill adjacent to a Campus with a University.
			if not tile.terrain() == TerrainType.desert:
				return False
			
			# no mountains
			if tile.hasFeature(FeatureType.mountains):
				return False
			
			if not self.adjacentToDistrict(DistrictType.campus, location, simulation):
				return False
			
			if not self.adjacentToBuilding(BuildingType.university, location, simulation):
				return False
			
			return True

		elif self == WonderType.casaDeContratacion:
			# no mountains
			if tile.hasFeature(FeatureType.mountains):
				return False
			
			# Must be built adjacent to a Government Plaza.
			return self.adjacentToDistrict(DistrictType.governmentPlaza, location, simulation)

		elif self == WonderType.forbiddenCity:
			# Must be built on flat land adjacent to City Center.
			if not tile.isLand() or tile.isHills():
				return False
			
			# no mountains
			if tile.hasFeature(FeatureType.mountains):
				return False
			
			return self.adjacentToDistrict(DistrictType.cityCenter, location, simulation)

		elif self == WonderType.greatZimbabwe:
			# Must be built adjacent to Cattle and a Commercial Hub district with a Market.
			if not self.adjacentToResource(ResourceType.cattle, location, simulation):
				return False
			
			# no mountains
			if tile.hasFeature(FeatureType.mountains):
				return False
			
			if not self.adjacentToDistrict(DistrictType.commercialHub, location, simulation):
				return False
			
			if not self.adjacentToBuilding(BuildingType.market, location, simulation):
				return False
			
			return True

		elif self == WonderType.potalaPalace:
			# no mountains
			if tile.hasFeature(FeatureType.mountains):
				return False
			
			# Must be built on a Hill adjacent to a Mountain.
			if not tile.isHills():
				return False
			
			return self.adjacentToFeature(FeatureType.mountains, location, simulation)

		elif self == WonderType.stBasilsCathedral:
			# no mountains
			if tile.hasFeature(FeatureType.mountains):
				return False
			
			# Must be built adjacent to a City Center
			return self.adjacentToDistrict(DistrictType.cityCenter, location, simulation)

		elif self == WonderType.tajMahal:
			# no mountains
			if tile.hasFeature(FeatureType.mountains):
				return False
			
			# Must be built next to a River.
			return simulation.riverAt(location)

		elif self == WonderType.torreDeBelem:
			# It must be built on Coast adjacent to land and a Harbor. It cannot be built on a Lake.
			if not tile.isWater():
				return False

			return self.adjacentToDistrict(DistrictType.harbor, location, simulation)

		elif self == WonderType.venetianArsenal:
			# It must be built on Coast adjacent to an Industrial Zone. It cannot be built on a Lake.
			if not tile.isWater():
				return False
			
			return self.adjacentToDistrict(DistrictType.industrialZone, location, simulation)
			
		raise InvalidEnumError(self)

	def adjacentToResource(self, resource: ResourceType, location: HexPoint, simulation) -> bool:
		nextToResource: bool = False

		for neighbor in location.neighbors():
			neighborTile = simulation.tileAt(neighbor)

			if neighborTile is None:
				continue

			player = neighborTile.owner()

			if player is None:
				continue

			if neighborTile.hasResource(resource, player):
				nextToResource = True

		return nextToResource

	def adjacentToBuilding(self, building: BuildingType, location: HexPoint, simulation) -> bool:
		# fixme - buildings are in districts and not in city centers
		nextToBuilding: bool = False

		for neighbor in location.neighbors():
			neighborTile = simulation.tileAt(neighbor)

			if neighborTile is None:
				continue

			city = neighborTile.workingCity()

			if city is None:
				continue

			if city.hasBuilding(building):
				nextToBuilding = True

		return nextToBuilding

	def adjacentToDistrict(self, district: DistrictType, location: HexPoint, simulation) -> bool:
		nextToDistrict: bool = False

		for neighbor in location.neighbors():
			neighborTile = simulation.tileAt(neighbor)

			if neighborTile is None:
				continue

			if neighborTile.hasDistrict(district):
				nextToDistrict = True

		return nextToDistrict

	def adjacentToImprovement(self, improvement: ImprovementType, location: HexPoint, simulation) -> bool:
		nextToImprovement: bool = False

		for neighbor in location.neighbors():
			neighborTile = simulation.tileAt(neighbor)

			if neighborTile is None:
				continue

			if neighborTile.hasImprovement(improvement):
				nextToImprovement = True

		return nextToImprovement

	def adjacentToFeature(self, feature: FeatureType, location: HexPoint, simulation) -> bool:
		nextToFeature: bool = False

		for neighbor in location.neighbors():
			neighborTile = simulation.tileAt(neighbor)

			if neighborTile is None:
				continue

			if neighborTile.hasFeature(feature):
				nextToFeature = True

		return nextToFeature

	def slotsForGreatWork(self):
		return self._data().slots

	def era(self) -> EraType:
		return self._data().era
