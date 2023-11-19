import random
from typing import Optional

from smarthexboard.smarthexboardlib.core.base import ExtendedEnum
from smarthexboard.smarthexboardlib.core.types import EraType


class GreatPersonType(ExtendedEnum):
	greatGeneral = 'greatGeneral'
	greatAdmiral = 'greatAdmiral'
	greatEngineer = 'greatEngineer'
	greatMerchant = 'greatMerchant'
	greatProphet = 'greatProphet'
	greatScientist = 'greatScientist'
	greatWriter = 'greatWriter'
	greatArtist = 'greatArtist'
	greatMusician = 'greatMusician'


class GreatWork:
	symphony40Mvt1 = None
	eineKleineNachtmusik = None
	laNotteConcerto = None
	fourSeasonsWinter = None
	hachidanNoShirabe = None
	rokudanNoShirabe = None
	celloSuiteNo1 = None
	littleFugueInGMinor = None
	symphony3EroicaSymphonyMvt1 = None
	odeToJoySymphony9 = None
	theHaywainTriptych = None
	theLastJudgement = None
	theGardenOfEarthlyDelights = None
	judithSlayingHolofernes = None
	gattamelata = None
	saintMark = None
	david = None
	pieta = None
	sistineChapelCeiling = None
	ascension = None
	saviourInGlory = None
	annunciation = None
	theTaleOfGenji = None
	theDiaryOfLadyMurasaki = None
	inTheMountainsOnASummerDay = None
	drinkingAloneByMoonlight = None
	troilusAndCriseyde = None
	heroides = None
	metamorphoses = None
	theCanterburyTales = None
	lamentForYing = None
	chuCi = None
	pratimaNataka = None
	theMadhyamaVyayoga = None
	odyssey = None
	iliad = None
	artOfWar = None


class GreatPersonData:
	def __init__(self, name: str, greatPersonType: GreatPersonType, era: EraType, bonus: str, charges: int, works: [GreatWork]):
		self.name: str = name
		self.greatPersonType: GreatPersonType = greatPersonType
		self.era: EraType = era
		self.bonus: str = bonus
		self.charges: int = charges
		self.works: [GreatWork] = works


class GreatPerson(ExtendedEnum):
	none = 'none'
	
	# generals
	# https://civilization.fandom.com/wiki/Great_General_(Civ6)
	boudica = 'boudica'
	hannibalBarca = 'hannibalBarca'
	sunTzu = 'sunTzu'
	aethelflaed = 'aethelflaed'  # Æthelflæd
	elCid = 'elCid'

	# admirals
	# https://civilization.fandom.com/wiki/Great_Admiral_(Civ6)
	artemisia = 'artemisia'
	gaiusDuilius = 'gaiusDuilius'
	themistocles = 'themistocles'
	leifErikson = 'leifErikson'
	rajendraChola = 'rajendraChola'

	# engineers
	# https://civilization.fandom.com/wiki/Great_Engineer_(Civ6)
	biSheng = 'biSheng'
	isidoreOfMiletus = 'isidoreOfMiletus'
	jamesOfStGeorge = 'jamesOfStGeorge'
	filippoBrunelleschi = 'filippoBrunelleschi'
	leonardoDaVinci = 'leonardoDaVinci'

	# merchants
	# https://civilization.fandom.com/wiki/Great_Merchant_(Civ6)
	colaeus = 'colaeus'
	marcusLiciniusCrassus = 'marcusLiciniusCrassus'
	zhangQian = 'zhangQian'
	ireneOfAthens = 'ireneOfAthens'
	marcoPolo = 'marcoPolo'

	# prophets
	# https://civilization.fandom.com/wiki/Great_Prophet_(Civ6)
	confucius = 'confucius'
	johnTheBaptist = 'johnTheBaptist'
	laozi = 'laozi'
	siddharthaGautama = 'siddharthaGautama'
	simonPeter = 'siddharthaGautama'
	zoroaster = 'zoroaster'
	adiShankara = 'adiShankara'
	bodhidharma = 'bodhidharma'
	irenaeus = 'irenaeus'
	oNoYasumaro = 'oNoYasumaro'
	songtsanGampo = 'songtsanGampo'

	# scientist
	# https://civilization.fandom.com/wiki/Great_Scientist_(Civ6)
	aryabhata = 'aryabhata'
	euclid = 'euclid'
	hypatia = 'hypatia'
	abuAlQasimAlZahrawi = 'abuAlQasimAlZahrawi'
	hildegardOfBingen = 'hildegardOfBingen'
	omarKhayyam = 'omarKhayyam'

	# writers
	# https://civilization.fandom.com/wiki/Great_Writer_(Civ6)
	homer = 'homer'
	bhasa = 'bhasa'
	quYuan = 'quYuan'
	ovid = 'ovid'
	geoffreyChaucer = 'geoffreyChaucer'
	liBai = 'liBai'
	murasakiShikibu = 'murasakiShikibu'

	# artist
	# https://civilization.fandom.com/wiki/Great_Artist_(Civ6)
	andreiRublev = 'andreiRublev'
	michelangelo = 'michelangelo'
	donatello = 'donatello'
	hieronymusBosch = 'hieronymusBosch'

	# musicans
	# https://civilization.fandom.com/wiki/Great_Musician_(Civ6)
	ludwigVanBeethoven = 'ludwigVanBeethoven'
	johannSebastianBach = 'johannSebastianBach'
	yatsuhashiKengyo = 'yatsuhashiKengyo'
	antonioVivaldi = 'antonioVivaldi'
	wolfgangAmadeusMozart = 'wolfgangAmadeusMozart'

	def name(self) -> str:
		return self._data().name

	def era(self) -> EraType:
		return self._data().era

	def greatPersonType(self) -> GreatPersonType:
		return self._data().greatPersonType

	def _data(self) -> GreatPersonData:
		if self == GreatPerson.none:
			return GreatPersonData(
				name="None",
				greatPersonType=GreatPersonType.greatGeneral,
				era=EraType.classical,
				bonus="",
				charges=0,
				works=[]
			)

		# ---------------------
		# generals
		if self == GreatPerson.boudica:
			return GreatPersonData(
				name="Boudica",
				greatPersonType=GreatPersonType.greatGeneral,
				era=EraType.classical,
				bonus="Convert adjacent barbarian units.",
				charges=1,
				works=[]
			)
		if self == GreatPerson.hannibalBarca:
			return GreatPersonData(
				name="Hannibal Barca",
				greatPersonType=GreatPersonType.greatGeneral,
				era=EraType.classical,
				bonus="Grants 1 promotion level to a military land unit.",
				charges=1,
				works=[]
			)
		if self == GreatPerson.sunTzu:
			return GreatPersonData(
				name="Sun Tzu",
				greatPersonType=GreatPersonType.greatGeneral,
				era=EraType.classical,
				bonus="Creates the Art of War Great Work of Writing (+2 Culture, +2 Tourism).",
				charges=1,
				works=[GreatWork.artOfWar]
			)
		if self == GreatPerson.aethelflaed:
			return GreatPersonData(
				name="Æthelflæd",
				greatPersonType=GreatPersonType.greatGeneral,
				era=EraType.medieval,
				bonus="Instantly creates a Knight unit. Grants +2 Loyalty per turn for this city.",
				charges=1,
				works=[]
			)
		if self == GreatPerson.elCid:
			# https://civilization.fandom.com/wiki/El_Cid_(Civ6)
			return GreatPersonData(
				name="El Cid",
				greatPersonType=GreatPersonType.greatGeneral,
				era=EraType.medieval,
				bonus="Forms a Corps out of a military land unit.",
				charges=1,
				works=[]
			)

		# ---------------------
		# admiral
		if self == GreatPerson.artemisia:
			# https://civilization.fandom.com/wiki/Artemisia_(Civ6)
			return GreatPersonData(
				name="Artemisia",
				greatPersonType=GreatPersonType.greatAdmiral,
				era=EraType.classical,
				bonus="Grants 1 promotion level to a military naval unit.",
				charges=1,
				works=[]
			)
		if self == GreatPerson.gaiusDuilius:
			# https://civilization.fandom.com/wiki/Gaius_Duilius_(Civ6)
			return GreatPersonData(
				name="Gaius Duilius",
				greatPersonType=GreatPersonType.greatAdmiral,
				era=EraType.classical,
				bonus="Forms a Fleet out of a military naval unit.",
				charges=1,
				works=[]
			)
		if self == GreatPerson.themistocles:
			# https://civilization.fandom.com/wiki/Themistocles_(Civ6)
			return GreatPersonData(
				name="Themistocles",
				greatPersonType=GreatPersonType.greatAdmiral,
				era=EraType.classical,
				bonus="Instantly creates a Quadrireme unit. Grants +2 Loyalty per turn for this city.",
				charges=1,
				works=[]
			)
		if self == GreatPerson.leifErikson:
			# https://civilization.fandom.com/wiki/Leif_Erikson_(Civ6)
			return GreatPersonData(
				name="Leif Erikson",
				greatPersonType=GreatPersonType.greatAdmiral,
				era=EraType.medieval,
				bonus="Allows all naval units to move over ocean tiles without the required technology.",
				charges=1,
				works=[]
			)
		if self == GreatPerson.rajendraChola:
			# https://civilization.fandom.com/wiki/Rajendra_Chola_(Civ6)
			return GreatPersonData(
				name="Rajendra Chola",
				greatPersonType=GreatPersonType.greatAdmiral,
				era=EraType.medieval,
				bonus="Gain 50 Gold. Military units get +40% rewards to looting.",
				charges=1,
				works=[]
			)

		# ---------------------
		# engineer
		if self == GreatPerson.biSheng:
			# https://civilization.fandom.com/wiki/Bi_Sheng_(Civ6)
			return GreatPersonData(
				name="Bi Sheng",
				greatPersonType=GreatPersonType.greatEngineer,
				era=EraType.medieval,
				bonus="Lets this city build one more district than the population limit allows. Triggers the Eureka moment for Printing technology.",
				charges=1,
				works=[]
			)
		if self == GreatPerson.isidoreOfMiletus:
			# https://civilization.fandom.com/wiki/Isidore_of_Miletus_(Civ6)
			return GreatPersonData(
				name="Isidore of Miletus",
				greatPersonType=GreatPersonType.greatEngineer,
				era=EraType.medieval,
				bonus="Grants 215 Production towards wonder construction at standard speed. (2 charges)",
				charges=2,
				works=[]
			)
		if self == GreatPerson.jamesOfStGeorge:
			# https://civilization.fandom.com/wiki/James_of_St._George_(Civ6)
			return GreatPersonData(
				name="James of St. George",
				greatPersonType=GreatPersonType.greatEngineer,
				era=EraType.medieval,
				bonus="Instantly builds Ancient and Medieval Walls in this city, and provides enough Gold per turn to pay maintenance. (3 charges)",
				charges=3,
				works=[]
			)
		if self == GreatPerson.filippoBrunelleschi:
			# https://civilization.fandom.com/wiki/Filippo_Brunelleschi_(Civ6)
			return GreatPersonData(
				name="Filippo Brunelleschi",
				greatPersonType=GreatPersonType.greatEngineer,
				era=EraType.renaissance,
				bonus="Grants 315 Production towards wonder construction. (2 charges)",
				charges=2,
				works=[]
			)
		if self == GreatPerson.leonardoDaVinci:
			# https://civilization.fandom.com/wiki/Leonardo_da_Vinci_(Civ6)
			return GreatPersonData(
				name="Leonardo da Vinci",
				greatPersonType=GreatPersonType.greatEngineer,
				era=EraType.renaissance,
				bonus="Triggers the Eureka moment for one random technology of the Modern era. Workshops provide +1  Culture.",
				charges=1,
				works=[]
			)

		# ---------------------
		# merchants
		if self == GreatPerson.colaeus:
			# https://civilization.fandom.com/wiki/Colaeus_(Civ6)
			return GreatPersonData(
				name="Colaeus",
				greatPersonType=GreatPersonType.greatMerchant,
				era=EraType.classical,
				bonus="Gain 100 Faith. Grants 1 free copy of the Luxury resource on this tile to your Capital city.",
				charges=1,
				works=[]
			)
		if self == GreatPerson.marcusLiciniusCrassus:
			# https://civilization.fandom.com/wiki/Marcus_Licinius_Crassus_(Civ6)
			return GreatPersonData(
				name="Marcus Licinius Crassus",
				greatPersonType=GreatPersonType.greatMerchant,
				era=EraType.classical,
				bonus="Gain 60 Gold. Your nearest city annexes this tile into its territory. (3 charges)",
				charges=3,
				works=[]
			)
		if self == GreatPerson.zhangQian:
			# https://civilization.fandom.com/wiki/Zhang_Qian_(Civ6)
			return GreatPersonData(
				name="Zhang Qian",
				greatPersonType=GreatPersonType.greatMerchant,
				era=EraType.classical,
				bonus="Increases Trade Route capacity by 1. Foreign Trade Routes to this city provide +2 Gold to both cities.",
				charges=1,
				works=[]
			)
		if self == GreatPerson.ireneOfAthens:
			# https://civilization.fandom.com/wiki/Irene_of_Athens_(Civ6)
			return GreatPersonData(
				name="Irene of Athens",
				greatPersonType=GreatPersonType.greatMerchant,
				era=EraType.medieval,
				bonus="Increase Trade Route capacity by 1. Grants 1 free copy of the Luxury resource on this tile to your  Capital city. Grants 1 Governor Title or recruit a new Governor.",
				charges=1,
				works=[]
			)
		if self == GreatPerson.marcoPolo:
			# https://civilization.fandom.com/wiki/Marco_Polo_(Civ6)
			return GreatPersonData(
				name="Marco Polo",
				greatPersonType=GreatPersonType.greatMerchant,
				era=EraType.medieval,
				bonus="Grants a free Trader unit in this city, and increases Trade Route capacity by 1. Foreign Trade Routes to this city provides +2 Gold to both cities.",
				charges=1,
				works=[]
			)

		# ---------------------
		# prophets
		if self == GreatPerson.confucius:
			# https://civilization.fandom.com/wiki/Confucius_(Civ6)
			return GreatPersonData(
				name="Confucius",
				greatPersonType=GreatPersonType.greatProphet,
				era=EraType.classical,
				bonus="",
				charges=1,
				works=[]
			)
		if self == GreatPerson.johnTheBaptist:
			#
			return GreatPersonData(
				name="John the Baptist",
				greatPersonType=GreatPersonType.greatProphet,
				era=EraType.classical,
				bonus="",
				charges=1,
				works=[]
			)
		if self == GreatPerson.laozi:
			# https://civilization.fandom.com/wiki/Laozi_(Civ6)
			return GreatPersonData(
				name="Laozi",
				greatPersonType=GreatPersonType.greatProphet,
				era=EraType.classical,
				bonus="",
				charges=1,
				works=[]
			)
		if self == GreatPerson.siddharthaGautama:
			# https://civilization.fandom.com/wiki/Siddhartha_Gautama_(Civ6)
			return GreatPersonData(
				name="Siddhartha Gautama",
				greatPersonType=GreatPersonType.greatProphet,
				era=EraType.classical,
				bonus="",
				charges=1,
				works=[]
			)
		if self == GreatPerson.simonPeter:
			# https://civilization.fandom.com/wiki/Simon_Peter_(Civ6)
			return GreatPersonData(
				name="Simon Peter",
				greatPersonType=GreatPersonType.greatProphet,
				era=EraType.classical,
				bonus="",
				charges=1,
				works=[]
			)
		if self == GreatPerson.zoroaster:
			# https://civilization.fandom.com/wiki/Zoroaster_(Civ6)
			return GreatPersonData(
				name="Zoroaster",
				greatPersonType=GreatPersonType.greatProphet,
				era=EraType.classical,
				bonus="",
				charges=1,
				works=[]
			)
		if self == GreatPerson.adiShankara:
			# https://civilization.fandom.com/wiki/Adi_Shankara_(Civ6)
			return GreatPersonData(
				name="Adi Shankara",
				greatPersonType=GreatPersonType.greatProphet,
				era=EraType.medieval,
				bonus="",
				charges=1,
				works=[]
			)
		if self == GreatPerson.bodhidharma:
			# https://civilization.fandom.com/wiki/Bodhidharma_(Civ6)
			return GreatPersonData(
				name="Bodhidharma",
				greatPersonType=GreatPersonType.greatProphet,
				era=EraType.medieval,
				bonus="",
				charges=1,
				works=[]
			)
		if self == GreatPerson.irenaeus:
			# https://civilization.fandom.com/wiki/Irenaeus_(Civ6)
			return GreatPersonData(
				name="Irenaeus",
				greatPersonType=GreatPersonType.greatProphet,
				era=EraType.medieval,
				bonus="",
				charges=1,
				works=[]
			)
		if self == GreatPerson.oNoYasumaro:
			# https://civilization.fandom.com/wiki/O_No_Yasumaro_(Civ6)
			return GreatPersonData(
				name="O No Yasumaro",
				greatPersonType=GreatPersonType.greatProphet,
				era=EraType.medieval,
				bonus="",
				charges=1,
				works=[]
			)
		if self == GreatPerson.songtsanGampo:
			# https://civilization.fandom.com/wiki/Songtsan_Gampo_(Civ6)
			return GreatPersonData(
				name="Songtsan Gampo",
				greatPersonType=GreatPersonType.greatProphet,
				era=EraType.medieval,
				bonus="",
				charges=1,
				works=[]
			)

		# ---------------------
		# scientists
		if self == GreatPerson.aryabhata:
			# https://civilization.fandom.com/wiki/Aryabhata_(Civ6)
			return GreatPersonData(
				name="Aryabhata",
				greatPersonType=GreatPersonType.greatScientist,
				era=EraType.classical,
				bonus="Triggers the Eureka moment for three random technologies from the Classical or Medieval era.",
				charges=1,
				works=[]
			)
		if self == GreatPerson.euclid:
			# https://civilization.fandom.com/wiki/Euclid_(Civ6)
			return GreatPersonData(
				name="Euclid",
				greatPersonType=GreatPersonType.greatScientist,
				era=EraType.classical,
				bonus="Triggers the Eureka moment for Mathematics and one random technology from the Medieval era.",
				charges=1,
				works=[]
			)
		if self == GreatPerson.hypatia:
			# https://civilization.fandom.com/wiki/Hypatia_(Civ6)
			return GreatPersonData(
				name="Hypatia",
				greatPersonType=GreatPersonType.greatScientist,
				era=EraType.classical,
				bonus="Libraries provide +1 Science. Instantly builds a Library in this district.",
				charges=1,
				works=[]
			)
		if self == GreatPerson.abuAlQasimAlZahrawi:
			# https://civilization.fandom.com/wiki/Abu_Al-Qasim_Al-Zahrawi_(Civ6)
			return GreatPersonData(
				name="Abu Al-Qasim Al-Zahrawi",
				greatPersonType=GreatPersonType.greatScientist,
				era=EraType.medieval,
				bonus="Active: Triggers the Eureka for one random Medieval or Renaissance era technology. Wounded units can heal +5 HP per turn. Passive: +20 HP Healing for all units within one tile.",
				charges=1,
				works=[]
			)
		if self == GreatPerson.hildegardOfBingen:
			# https://civilization.fandom.com/wiki/Hildegard_of_Bingen_(Civ6)
			return GreatPersonData(
				name="Hildegard of Bingen",
				greatPersonType=GreatPersonType.greatScientist,
				era=EraType.medieval,
				bonus="Gain 100 Faith. This Holy Site's adjacency bonuses gain an additional Science bonus.",
				charges=1,
				works=[]
			)
		if self == GreatPerson.omarKhayyam:
			# https://civilization.fandom.com/wiki/Omar_Khayyam_(Civ6)
			return GreatPersonData(
				name="Omar Khayyam",
				greatPersonType=GreatPersonType.greatScientist,
				era=EraType.medieval,
				bonus="Triggers the Eureka moment for two technologies and the Inspiration for one Civic from the Medieval or Renaissance era.",
				charges=1,
				works=[]
			)

		# ---------------------
		# writers
		if self == GreatPerson.homer:
			# https://civilization.fandom.com/wiki/Homer_(Civ6)
			return GreatPersonData(
				name="Homer",
				greatPersonType=GreatPersonType.greatWriter,
				era=EraType.classical,
				bonus="Activate on an appropriate tile to create a Great Work",
				charges=2,
				works=[GreatWork.iliad, GreatWork.odyssey]
			)
		if self == GreatPerson.bhasa:
			# https://civilization.fandom.com/wiki/Bhasa_(Civ6)
			return GreatPersonData(
				name="Bhasa",
				greatPersonType=GreatPersonType.greatWriter,
				era=EraType.classical,
				bonus="Activate on an appropriate tile to create a Great Work",
				charges=2,
				works=[GreatWork.theMadhyamaVyayoga, GreatWork.pratimaNataka]
			)
		if self == GreatPerson.quYuan:
			# https://civilization.fandom.com/wiki/Qu_Yuan_(Civ6)
			return GreatPersonData(
				name="Qu Yuan",
				greatPersonType=GreatPersonType.greatWriter,
				era=EraType.classical,
				bonus="Activate on an appropriate tile to create a Great Work",
				charges=2,
				works=[GreatWork.chuCi, GreatWork.lamentForYing]
			)
		if self == GreatPerson.ovid:
			# https://civilization.fandom.com/wiki/Ovid_(Civ6)
			return GreatPersonData(
				name="Ovid",
				greatPersonType=GreatPersonType.greatWriter,
				era=EraType.classical,
				bonus="Activate on an appropriate tile to create a Great Work",
				charges=2,
				works=[GreatWork.metamorphoses, GreatWork.heroides]
			)
		if self == GreatPerson.geoffreyChaucer:
			# https://civilization.fandom.com/wiki/Geoffrey_Chaucer_(Civ6)
			return GreatPersonData(
				name="Geoffrey Chaucer",
				greatPersonType=GreatPersonType.greatWriter,
				era=EraType.medieval,
				bonus="Activate on an appropriate tile to create a Great Work",
				charges=2,
				works=[GreatWork.theCanterburyTales, GreatWork.troilusAndCriseyde]
			)
		if self == GreatPerson.liBai:
			# https://civilization.fandom.com/wiki/Li_Bai_(Civ6)
			return GreatPersonData(
				name="Li Bai",
				greatPersonType=GreatPersonType.greatWriter,
				era=EraType.medieval,
				bonus="Activate on an appropriate tile to create a Great Work",
				charges=2,
				works=[GreatWork.drinkingAloneByMoonlight, GreatWork.inTheMountainsOnASummerDay]
			)
		if self == GreatPerson.murasakiShikibu:
			# https://civilization.fandom.com/wiki/Murasaki_Shikibu_(Civ6)
			return GreatPersonData(
				name="Murasaki Shikibu",
				greatPersonType=GreatPersonType.greatWriter,
				era=EraType.medieval,
				bonus="Activate on an appropriate tile to create a Great Work",
				charges=2,
				works=[GreatWork.theDiaryOfLadyMurasaki, GreatWork.theTaleOfGenji]
			)

		# ---------------------
		# artists
		if self == GreatPerson.andreiRublev:
			# https://civilization.fandom.com/wiki/Andrei_Rublev_(Civ6)
			return GreatPersonData(
				name="Andrei Rublev",
				greatPersonType=GreatPersonType.greatArtist,
				era=EraType.renaissance,
				bonus="Activate on an appropriate tile to create a Great Work",
				charges=3,
				works=[GreatWork.annunciation, GreatWork.saviourInGlory, GreatWork.ascension]
			)
		if self == GreatPerson.michelangelo:
			# https://civilization.fandom.com/wiki/Michelangelo_(Civ6)
			return GreatPersonData(
				name="Michelangelo",
				greatPersonType=GreatPersonType.greatArtist,
				era=EraType.renaissance,
				bonus="Activate on an appropriate tile to create a Great Work",
				charges=3,
				works=[GreatWork.sistineChapelCeiling, GreatWork.pieta, GreatWork.david]
			)
		if self == GreatPerson.donatello:
			# https://civilization.fandom.com/wiki/Donatello_(Civ6)
			return GreatPersonData(
				name="Donatello",
				greatPersonType=GreatPersonType.greatArtist,
				era=EraType.renaissance,
				bonus="Activate on an appropriate tile to create a Great Work",
				charges=3,
				works=[GreatWork.saintMark, GreatWork.gattamelata, GreatWork.judithSlayingHolofernes]
			)
		if self == GreatPerson.hieronymusBosch:
			# https://civilization.fandom.com/wiki/Hieronymus_Bosch_(Civ6)
			return GreatPersonData(
				name="Hieronymus Bosch",
				greatPersonType=GreatPersonType.greatArtist,
				era=EraType.renaissance,
				bonus="Activate on an appropriate tile to create a Great Work",
				charges=3,
				works=[GreatWork.theGardenOfEarthlyDelights, GreatWork.theLastJudgement, GreatWork.theHaywainTriptych]
			)

		# ---------------------
		# musicans
		if self == GreatPerson.ludwigVanBeethoven:
			# https://civilization.fandom.com/wiki/Ludwig_van_Beethoven_(Civ6)
			return GreatPersonData(
				name="Ludwig van Beethoven",
				greatPersonType=GreatPersonType.greatMusician,
				era=EraType.industrial,
				bonus="Activate on an appropriate tile to create a Great Work",
				charges=2,
				works=[GreatWork.odeToJoySymphony9, GreatWork.symphony3EroicaSymphonyMvt1]
			)
		if self == GreatPerson.johannSebastianBach:
			# https://civilization.fandom.com/wiki/Johann_Sebastian_Bach_(Civ6)
			return GreatPersonData(
				name="Johann Sebastian Bach",
				greatPersonType=GreatPersonType.greatMusician,
				era=EraType.industrial,
				bonus="Activate on an appropriate tile to create a Great Work",
				charges=2,
				works=[GreatWork.littleFugueInGMinor, GreatWork.celloSuiteNo1]
			)
		if self == GreatPerson.yatsuhashiKengyo:
			# https://civilization.fandom.com/wiki/Yatsuhashi_Kengyo_(Civ6)
			return GreatPersonData(
				name="Yatsuhashi Kengyo",
				greatPersonType=GreatPersonType.greatMusician,
				era=EraType.industrial,
				bonus="Activate on an appropriate tile to create a Great Work",
				charges=2,
				works=[GreatWork.rokudanNoShirabe, GreatWork.hachidanNoShirabe]
			)
		if self == GreatPerson.antonioVivaldi:
			# https://civilization.fandom.com/wiki/Antonio_Vivaldi_(Civ6)
			return GreatPersonData(
				name="Antonio Vivaldi",
				greatPersonType=GreatPersonType.greatMusician,
				era=EraType.industrial,
				bonus="Activate on an appropriate tile to create a Great Work",
				charges=2,
				works=[GreatWork.fourSeasonsWinter, GreatWork.laNotteConcerto]
			)
		if self == GreatPerson.wolfgangAmadeusMozart:
			# https://civilization.fandom.com/wiki/Wolfgang_Amadeus_Mozart_(Civ6)
			return GreatPersonData(
				name="Wolfgang Amadeus Mozart",
				greatPersonType=GreatPersonType.greatMusician,
				era=EraType.industrial,
				bonus="Activate on an appropriate tile to create a Great Work",
				charges=2,
				works=[GreatWork.eineKleineNachtmusik, GreatWork.symphony40Mvt1]
			)


class GreatPersons:
	def __init__(self):
		self.spawned = []
		self.current = []

		self.fillCurrent(EraType.ancient)

	def fillCurrent(self, era: EraType):
		for greatPersonType in list(GreatPersonType):
			# check for empty slots
			if next(filter(lambda gp: gp.greatPersonType == greatPersonType, self.current), None) is None:
				possibleGreatPersons = list(filter(lambda gp: gp.era() == era and gp.greatPersonType() == greatPersonType and gp not in self.spawned, list(GreatPerson)))

				# consider next era
				if len(possibleGreatPersons) == 0:
					possibleGreatPersons = list(filter(lambda gp: gp.era() == era.next() and gp.greatPersonType() == greatPersonType and gp not in self.spawned, list(GreatPerson)))

				if len(possibleGreatPersons) > 0:
					self.current.append(random.choice(possibleGreatPersons))

		return


class GreatPersonPoints:
	def __init__(self, greatAdmiral: Optional[int] = None, greatArtist: Optional[int] = None,
	             greatEngineer: Optional[int] = None, greatGeneral: Optional[int] = None,
	             greatMerchant: Optional[int] = None, greatMusician: Optional[int] = None,
	             greatProphet: Optional[int] = None, greatScientist: Optional[int] = None,
	             greatWriter: Optional[int] = None):
		self.greatAdmiral: int = 0 if greatAdmiral is None else greatAdmiral
		self.greatArtist: int = 0 if greatArtist is None else greatArtist
		self.greatEngineer: int = 0 if greatEngineer is None else greatEngineer
		self.greatGeneral: int = 0 if greatGeneral is None else greatGeneral
		self.greatMerchant: int = 0 if greatMerchant is None else greatMerchant
		self.greatMusician: int = 0 if greatMusician is None else greatMusician
		self.greatProphet: int = 0 if greatProphet is None else greatProphet
		self.greatScientist: int = 0 if greatScientist is None else greatScientist
		self.greatWriter: int = 0 if greatWriter is None else greatWriter

	def __add__(self, other):
		if isinstance(other, GreatPersonPoints):
			self.greatAdmiral += other.greatAdmiral
			self.greatArtist += other.greatArtist
			self.greatEngineer += other.greatEngineer
			self.greatGeneral += other.greatGeneral
			self.greatMerchant += other.greatMerchant
			self.greatMusician += other.greatMusician
			self.greatProphet += other.greatProphet
			self.greatScientist += other.greatScientist
			self.greatWriter += other.greatWriter

			return self

		raise Exception(f'wrong type: {type(other)}')

	def value(self, greatPersonType: GreatPersonType) -> int:
		if greatPersonType == GreatPersonType.greatAdmiral:
			return self.greatAdmiral
		if greatPersonType == GreatPersonType.greatArtist:
			return self.greatArtist
		if greatPersonType == GreatPersonType.greatEngineer:
			return self.greatEngineer
		if greatPersonType == GreatPersonType.greatGeneral:
			return self.greatGeneral
		if greatPersonType == GreatPersonType.greatMerchant:
			return self.greatMerchant
		if greatPersonType == GreatPersonType.greatMusician:
			return self.greatMusician
		if greatPersonType == GreatPersonType.greatProphet:
			return self.greatProphet
		if greatPersonType == GreatPersonType.greatScientist:
			return self.greatScientist
		if greatPersonType == GreatPersonType.greatWriter:
			return self.greatWriter

		raise Exception(f'{greatPersonType} not handled')

	def modifyBy(self, modifier: float):
		self.greatGeneral = int(float(self.greatGeneral) * modifier)
		self.greatAdmiral = int(float(self.greatAdmiral) * modifier)
		self.greatEngineer = int(float(self.greatEngineer) * modifier)
		self.greatMerchant = int(float(self.greatMerchant) * modifier)
		self.greatProphet = int(float(self.greatProphet) * modifier)
		self.greatScientist = int(float(self.greatScientist) * modifier)
		self.greatWriter = int(float(self.greatWriter) * modifier)
		self.greatArtist = int(float(self.greatArtist) * modifier)
		self.greatMusician = int(float(self.greatMusician) * modifier)
