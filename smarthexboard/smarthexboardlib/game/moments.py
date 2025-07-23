from typing import Optional

from smarthexboard.smarthexboardlib.game.cityStates import CityStateType
from smarthexboard.smarthexboardlib.game.civilizations import CivilizationType
from smarthexboard.smarthexboardlib.game.religions import PantheonType
from smarthexboard.smarthexboardlib.game.states.dedications import DedicationType
from smarthexboard.smarthexboardlib.game.types import EraType
from smarthexboard.smarthexboardlib.game.wonders import WonderType
from smarthexboard.smarthexboardlib.map.types import FeatureType
from smarthexboard.smarthexboardlib.core.base import ExtendedEnum, InvalidEnumError


class MomentCategory(ExtendedEnum):
	major = 'major'
	minor = 'minor'
	hidden = 'hidden'


class MomentTypeData:
	def __init__(self, name: str, summary: str, instanceText: Optional[str],
	             category: MomentCategory, eraScore: int, minEra: EraType = EraType.ancient,
                 maxEra: EraType = EraType.future):
		self.name = name
		self.summary = summary
		self.instanceText = instanceText
		self.category = category
		self.eraScore = eraScore
		self.minEra = minEra
		self.maxEra = maxEra


class MomentType(ExtendedEnum):
	# major
	# admiralDefeatsEnemy  # 1 #
	allGovernorsAppointed = 'allGovernorsAppointed'  # 2
	# canalCompleted  # 3 #
	cityNearFloodableRiver = 'cityNearFloodableRiver'  # (cityName: String)  # 4
	cityNearVolcano = 'cityNearVolcano'  # (cityName: String)  # 5
	cityOfAwe = 'cityOfAwe'  # (cityName: String)  # 6
	cityOnNewContinent = 'cityOnNewContinent'  # (cityName: String, continentName: String)  # 7
	cityStatesFirstSuzerain = 'cityStatesFirstSuzerain'  # (cityState: CityStateType)  # 8
	# cityStateArmyLeviedNearEnemy 9
	# climateChangePhase 10
	darkAgeBegins = 'darkAgeBegins'  # 11
	discoveryOfANaturalWonder = 'discoveryOfANaturalWonder'  # (naturalWonder: FeatureType)  # 12
	# emergencyCompletedSuccessfully 13
	# emergencySuccessfullyDefended 14
	# enemyCityAdoptsOurReligion  # 15
	# enemyCityStatePacified 16
	# enemyFormationDefeated  # 17
	# enemyVeteranDefeated  # 18
	# exoplanetExpeditionLaunched  # 19
	# finalForeignCityTaken  # 20
	# firstAerodromeFullyDeveloped  # 21
	# firstBustlingCity(cityName: String)  # 22
	# firstCivicOfNewEra(eraType: EraType)  # 23
	# firstCorporationCreated 24
	# firstCorporationInTheWorld 25
	# firstDiscoveryOfANaturalWonder  # 26
	firstDiscoveryOfANewContinent = 'firstDiscoveryOfANewContinent'  # 27
	# firstEncampmentFullyDeveloped  # 28
	# firstEnormousCity(cityName: String)  # 29
	# firstEntertainmentComplexFullyDeveloped  # 30
	# firstGiganticCity(cityName: String)  # 31
	# firstGreenImprovement 32
	# firstGreenImprovementInWorld 33
	# firstHeroClaimed 34
	# firstHeroDeparted 35
	# firstHeroRecalled 36
	# firstImprovementAfterNaturalDisaster 37
	# firstIndustryCreated 38
	# firstIndustryInTheWorld 39
	# firstLargeCity(cityName: String)  # 40
	# firstLuxuryResourceMonopoly 41
	# firstLuxuryResourceMonopolyInTheWorld 42
	# firstMasterSpyEarned 43
	# firstMountainTunnel 44
	# firstMountainTunnelInTheWorld 45
	firstNeighborhoodCompleted = 'firstNeighborhoodCompleted'  # 46
	# firstRailroadConnection 47
	# firstRailroadConnectionInWorld 48
	# firstResourceConsumedForPower 49
	# firstResourceConsumedForPowerInWorld 50
	# firstRockBandConcert 51
	# firstRockBandConcertInWorld 52
	# firstSeasideResort 53
	# firstShipwreckExcavated  # 54
	firstTechnologyOfNewEra = 'firstTechnologyOfNewEra'  # (eraType: EraType)  # 55
	# firstTier1Government(governmentType: GovernmentType)  # 56
	# firstTier1GovernmentInWorld(governmentType: GovernmentType)  # 57
	# firstTier2Government(governmentType: GovernmentType)  # 58
	# firstTier2GovernmentInWorld(governmentType: GovernmentType)  # 59
	# firstTier3Government(governmentType: GovernmentType)  # 60
	# firstTier3GovernmentInWorld(governmentType: GovernmentType)  # 61
	# firstTier4Government(governmentType: GovernmentType)  # 62
	# firstTier4GovernmentInWorld(governmentType: GovernmentType)  # 63
	# firstTradingPostsInAllCivilizations  # 64
	firstUnitPromotedWithDistinction = 'firstUnitPromotedWithDistinction'  # 65
	# firstWaterParkFullyDeveloped 66
	# freeCityJoins 67
	# generalDefeatsEnemy  # 68
	goldenAgeBegins = 'goldenAgeBegins'  # 69 #
	governorFullyPromoted = 'governorFullyPromoted'  # 70
	# greatPersonLuredByFaith 71
	# greatPersonLuredByGold 72
	# heroicAgeBegins  # 73
	# inquisitionBegins 74
	# leviedArmyStandsDown 75
	# metAllCivilizations  # 76
	# nationalParkFounded  # 77
	# normalAgeBegins  # 78 #
	# onTheWaves  # 79 #
	# religionAdoptsAllBeliefs  # 80
	# religionFounded(religion: ReligionType)  # 81
	# rivalHolyCityConverted  # 82 #
	# splendidCampusCompleted  # 83 #
	# splendidCommercialHubCompleted  # 84
	# splendidHarborCompleted  # 85
	# splendidHolySiteCompleted  # 86
	# splendidIndustrialZoneCompleted  # 87
	# splendidTheaterSquareCompleted  # 88
	# takingFlight  # 89
	# threateningCampDestroyed  # 90
	# tradingPostsInAllCivilizations  # 91
	# uniqueBuildingConstructed 92
	# uniqueDistrictCompleted 93
	# uniqueTileImprovementBuilt 94
	# uniqueUnitMarches 95
	# worldsFirstArmada 96
	# worldsFirstArmy 97
	# worldsFirstBustlingCity(cityName: String)  # 98
	# worldsFirstCircumnavigation  # 99
	# worldsFirstCivicOfNewEra(eraType: EraType)  # 100
	# worldsFirstCorps 101
	# worldsFirstEnormousCity(cityName: String)  # 102
	# worldsFirstExoplanetExpeditionLaunched  # 103
	# worldsFirstFleet  # 104
	# worldsFirstFlight  # 105
	# worldsFirstGiganticCity(cityName: String)  # 106
	# worldsFirstInquisition 107
	# worldsFirstLandingOnTheMoon  # 108
	# worldsFirstLargeCity(cityName: String)  # 109
	# worldsFirstMartianColonyEstablished  # 110
	# worldsFirstNationalPark  # 111
	worldsFirstNeighborhood = 'worldsFirstNeighborhood'  # 112
	worldsFirstPantheon = 'worldsFirstPantheon'  # 113
	# worldsFirstReligion  # 114
	# worldsFirstReligionToAdoptAllBeliefs  # 115
	# worldsFirstSatelliteInOrbit  # 116
	# worldsFirstSeafaring  # 117
	# worldsFirstSeasideResort  # 118
	# worldsFirstShipwreckExcavated  # 119
	# worldsFirstStrategicResourcePotentialUnleashed  # 120
	worldsFirstTechnologyOfNewEra = 'worldsFirstTechnologyOfNewEra'  # (eraType: EraType)  # 121
	# worldsFirstToMeetAllCivilizations  # 122
	worldsLargestCivilization = 'worldsLargestCivilization'  # 123
	worldCircumnavigated = 'worldCircumnavigated'  # 124

	# minor
	# aggressiveCityPlacement  # 200
	# artifactExtracted  # 201
	barbarianCampDestroyed = 'barbarianCampDestroyed'  # 202
	# causeForWar(warType: CasusBelliType, civilizationType: CivilizationType)  # 203
	# cityReturnsToOriginalOwner(cityName: String, originalCivilization: CivilizationType)  # 204
	# cityStateArmyLevied  # 205
	# coastalFloodMitigated  # 206
	desertCity = 'desertCity'  # (cityName: String)  # 207
	# diplomaticVictoryResolutionWon  # 208
	# firstArmada 209
	# firstArmy  # 210
	# firstCorps  # 211
	# firstFleet  # 212
	# foreignCapitalTaken  # 213
	# greatPersonRecruited  # 214
	# heroClaimed  # 215
	# heroDeparted  # 216
	# heroRecalled  # 217
	# landedOnTheMoon  # 218
	# manhattanProjectCompleted  # 219
	# martianColonyEstablished  # 220
	# masterSpyEarned  # 221
	metNewCivilization = 'metNewCivilization'  # 222
	# oldGreatPersonRecruited  # 223
	oldWorldWonderCompleted = 'oldWorldWonderCompleted'  # 224
	# operationIvyCompleted 225
	pantheonFounded = 'pantheonFounded'  # (pantheon: PantheonType)  # 226
	# riverFloodMitigated  # 227 #
	# satelliteLaunchedIntoOrbit  # 228
	snowCity = 'snowCity'  # (cityName: String)  # 229
	# strategicResourcePotentialUnleashed  # 230
	tradingPostEstablishedInNewCivilization = 'tradingPostEstablishedInNewCivilization'  # (civilization: CivilizationType)  # 231
	# tribalVillageContacted  # 232
	tundraCity = 'tundraCity'  # (cityName: String)  # 233
	unitPromotedWithDistinction = 'unitPromotedWithDistinction'  # 234
	wonderCompleted = 'wonderCompleted'  # (wonder: WonderType)  # 235

	# hidden
	# shipSunk  # 300 for artifacts
	battleFought = 'battleFought'  # 301
	dedicationTriggered = 'dedicationTriggered'  # 302 for dedications

	def __repr__(self):
		return f'MomentType.{self.title()}'

	def title(self):
		return self._data().name

	def eraScore(self):
		return self._data().eraScore

	def minEra(self) -> EraType:
		return self._data().minEra

	def maxEra(self) -> EraType:
		return self._data().maxEra

	def _data(self) -> MomentTypeData:
		# major
		# admiralDefeatsEnemy  # 1 #
		if self == MomentType.allGovernorsAppointed:
			# 2
			return MomentTypeData(
				name="TXT_KEY_MOMENT_ALL_GOVERNORS_APPOINTED_TITLE",
				summary="TXT_KEY_MOMENT_ALL_GOVERNORS_APPOINTED_SUMMARY",
				instanceText=None,
				category=MomentCategory.major,
				eraScore=1
			)
		# canalCompleted  # 3 #
		if self == MomentType.cityNearFloodableRiver:  # (cityName: String)
			# 4
			return MomentTypeData(
				name="TXT_KEY_MOMENT_CITY_NEAR_FLOODABLE_RIVER_TITLE",
				summary="TXT_KEY_MOMENT_CITY_NEAR_FLOODABLE_RIVER_SUMMARY",
				instanceText=None,
				category=MomentCategory.major,
				eraScore=1
			)
		elif self == MomentType.cityNearVolcano:  # (cityName: String)
			# 5
			return MomentTypeData(
				name="TXT_KEY_MOMENT_CITY_NEAR_VOLCANO_TITLE",
				summary="TXT_KEY_MOMENT_CITY_NEAR_VOLCANO_SUMMARY",
				instanceText=None,
				category=MomentCategory.major,
				eraScore=1
			)
		elif self == MomentType.cityOfAwe:  # (cityName: String)
			# 6
			return MomentTypeData(
				name="TXT_KEY_MOMENT_CITY_OF_AWE_TITLE",
				summary="TXT_KEY_MOMENT_CITY_OF_AWE_SUMMARY",
				instanceText=None,
				category=MomentCategory.major,
				eraScore=3
			)
		elif self == MomentType.cityOnNewContinent:  # (cityName: String, continentName: String)
			# 7
			return MomentTypeData(
				name="TXT_KEY_MOMENT_CITY_ON_NEW_CONTINENT_TITLE",
				summary="TXT_KEY_MOMENT_CITY_OF_NEW_CONTINENT_SUMMARY",
				instanceText=None,
				category=MomentCategory.major,
				eraScore=2
			)
		elif self == MomentType.cityStatesFirstSuzerain:  # (cityState: CityStateType)
			# 8
			return MomentTypeData(
				name="TXT_KEY_MOMENT_CITY_STATES_FIRST_SUZERAIN_TITLE",
				summary="TXT_KEY_MOMENT_CITY_STATES_FIRST_SUZERAIN_SUMMARY",
				instanceText=None,
				category=MomentCategory.major,
				eraScore=2,
				maxEra=EraType.medieval
			)
		# cityStateArmyLeviedNearEnemy 9
		# climateChangePhase 10
		elif self == MomentType.darkAgeBegins:
			# 11
			return MomentTypeData(
				name="TXT_KEY_MOMENT_DARK_AGE_BEGINS_TITLE",
				summary="TXT_KEY_MOMENT_DARK_AGE_BEGINS_SUMMARY",
				instanceText=None,
				category=MomentCategory.major,
				eraScore=0
			)
		elif self == MomentType.discoveryOfANaturalWonder:  # (naturalWonder: FeatureType)
			# 12
			return MomentTypeData(
				name="TXT_KEY_MOMENT_DISCOVERY_OF_A_NATURAL_WONDER_TITLE",
				summary="TXT_KEY_MOMENT_DISCOVERY_OF_A_NATURAL_WONDER_SUMMARY",
				instanceText=None,
				category=MomentCategory.major,
				eraScore=1
			)
		# emergencyCompletedSuccessfully 13
		# emergencySuccessfullyDefended 14
		# enemyCityAdoptsOurReligion  # 15
		# enemyCityStatePacified 16
		# enemyFormationDefeated  # 17
		# enemyVeteranDefeated  # 18
		# exoplanetExpeditionLaunched  # 19
		# finalForeignCityTaken  # 20
		# firstAerodromeFullyDeveloped  # 21
		# firstBustlingCity(cityName: String)  # 22
		# firstCivicOfNewEra(eraType: EraType)  # 23
		# firstCorporationCreated 24
		# firstCorporationInTheWorld 25
		# firstDiscoveryOfANaturalWonder  # 26
		elif self == MomentType.firstDiscoveryOfANewContinent:
			# 27
			return MomentTypeData(
				name="First Discovery of a New Continent",
				summary="Our civilization's explorers are the first in the world to find this continent.",
				instanceText=None,
				category=MomentCategory.major,
				eraScore=4
			)
		# firstEncampmentFullyDeveloped  # 28
		# firstEnormousCity(cityName: String)  # 29
		# firstEntertainmentComplexFullyDeveloped  # 30
		# firstGiganticCity(cityName: String)  # 31
		# firstGreenImprovement 32
		# firstGreenImprovementInWorld 33
		# firstHeroClaimed 34
		# firstHeroDeparted 35
		# firstHeroRecalled 36
		# firstImprovementAfterNaturalDisaster 37
		# firstIndustryCreated 38
		# firstIndustryInTheWorld 39
		# firstLargeCity(cityName: String)  # 40
		# firstLuxuryResourceMonopoly 41
		# firstLuxuryResourceMonopolyInTheWorld 42
		# firstMasterSpyEarned 43
		# firstMountainTunnel 44
		# firstMountainTunnelInTheWorld 45
		if self == MomentType.firstNeighborhoodCompleted:
			# 46
			return MomentTypeData(
				name="First Neighborhood Completed",
				summary="You have completed your civilization's first Neighborhood district.",
				instanceText=None,
				category=MomentCategory.major,
				eraScore=2
			)
		# firstRailroadConnection 47
		# firstRailroadConnectionInWorld 48
		# firstResourceConsumedForPower 49
		# firstResourceConsumedForPowerInWorld 50
		# firstRockBandConcert 51
		# firstRockBandConcertInWorld 52
		# firstSeasideResort 53
		# firstShipwreckExcavated  # 54
		elif self == MomentType.firstTechnologyOfNewEra:
			# 55
			return MomentTypeData(
				name="First Technology of New Era",
				summary="You have completed your civilization's first technology from a new era of discovery.",
				instanceText=None,
				category=MomentCategory.major,
				eraScore=1
			)
		# firstTier1Government(governmentType: GovernmentType)  # 56
		# firstTier1GovernmentInWorld(governmentType: GovernmentType)  # 57
		# firstTier2Government(governmentType: GovernmentType)  # 58
		# firstTier2GovernmentInWorld(governmentType: GovernmentType)  # 59
		# firstTier3Government(governmentType: GovernmentType)  # 60
		# firstTier3GovernmentInWorld(governmentType: GovernmentType)  # 61
		# firstTier4Government(governmentType: GovernmentType)  # 62
		# firstTier4GovernmentInWorld(governmentType: GovernmentType)  # 63
		# firstTradingPostsInAllCivilizations  # 64
		elif self == MomentType.firstUnitPromotedWithDistinction:
			# 65
			return MomentTypeData(
				name="First Unit Promoted with Distinction",
				summary="For the first time, one of your units reaches its fourth level of promotion.",
				instanceText=None,
				category=MomentCategory.major,
				eraScore=1
			)
		# firstWaterParkFullyDeveloped 66
		# freeCityJoins 67
		# generalDefeatsEnemy  # 68
		elif self == MomentType.goldenAgeBegins:
			# 69
			return MomentTypeData(
				name="Golden Age Begins",
				summary="Golden Age Begins",
				instanceText=None,
				category=MomentCategory.major,
				eraScore=0
			)
		elif self == MomentType.governorFullyPromoted:
			# 70
			return MomentTypeData(
				name="Governor Fully Promoted",
				summary="You have fully promoted a [Governor] Governor for the first time, unlocking powerful " +
				        "abilities to help a city.",
				instanceText=None,
				category=MomentCategory.major,
				eraScore=1
			)
		# greatPersonLuredByFaith 71
		# greatPersonLuredByGold 72
		# heroicAgeBegins  # 73
		# inquisitionBegins 74
		# leviedArmyStandsDown 75
		# metAllCivilizations  # 76
		# nationalParkFounded  # 77
		# normalAgeBegins  # 78 #
		# onTheWaves  # 79 #
		# religionAdoptsAllBeliefs  # 80
		# religionFounded(religion: ReligionType)  # 81
		# rivalHolyCityConverted  # 82 #
		# splendidCampusCompleted  # 83 #
		# splendidCommercialHubCompleted  # 84
		# splendidHarborCompleted  # 85
		# splendidHolySiteCompleted  # 86
		# splendidIndustrialZoneCompleted  # 87
		# splendidTheaterSquareCompleted  # 88
		# takingFlight  # 89
		# threateningCampDestroyed  # 90
		# tradingPostsInAllCivilizations  # 91
		# uniqueBuildingConstructed 92
		# uniqueDistrictCompleted 93
		# uniqueTileImprovementBuilt 94
		# uniqueUnitMarches 95
		# worldsFirstArmada 96
		# worldsFirstArmy 97
		# worldsFirstBustlingCity(cityName: String)  # 98
		# worldsFirstCircumnavigation  # 99
		# worldsFirstCivicOfNewEra(eraType: EraType)  # 100
		# worldsFirstCorps 101
		# worldsFirstEnormousCity(cityName: String)  # 102
		# worldsFirstExoplanetExpeditionLaunched  # 103
		# worldsFirstFleet  # 104
		# worldsFirstFlight  # 105
		# worldsFirstGiganticCity(cityName: String)  # 106
		# worldsFirstInquisition 107
		# worldsFirstLandingOnTheMoon  # 108
		# worldsFirstLargeCity(cityName: String)  # 109
		# worldsFirstMartianColonyEstablished  # 110
		# worldsFirstNationalPark  # 111
		elif self == MomentType.worldsFirstNeighborhood:
			# 112
			return MomentTypeData(
				name="World's First Neighborhood",
				summary="You have completed the world's first Neighborhood district.",
				instanceText=None,
				category=MomentCategory.major,
				eraScore=3
			)
		elif self == MomentType.worldsFirstPantheon:
			# 113
			return MomentTypeData(
				name="World's First Pantheon",
				summary="Your people are the first in the world to adopt Belief in a Pantheon.",
				instanceText=None,
				category=MomentCategory.major,
				eraScore=2
			)
		# worldsFirstReligion  # 114
		# worldsFirstReligionToAdoptAllBeliefs  # 115
		# worldsFirstSatelliteInOrbit  # 116
		# worldsFirstSeafaring  # 117
		# worldsFirstSeasideResort  # 118
		# worldsFirstShipwreckExcavated  # 119
		# worldsFirstStrategicResourcePotentialUnleashed  # 120
		elif self == MomentType.worldsFirstTechnologyOfNewEra:
			# 121
			return MomentTypeData(
				name="World's First Technology of New Era",
				summary="You have completed the world's first technology from a new era of discovery.",
				instanceText=None,
				category=MomentCategory.major,
				eraScore=2
			)
		# worldsFirstToMeetAllCivilizations  # 122
		elif self == MomentType.worldsLargestCivilization:
			# 123
			return MomentTypeData(
				name="World's Largest Civilization",
				summary="Your civilization has become the largest in the world, with at least 3 more cities than its "
				        "next biggest rival.",
				instanceText=None,
				category=MomentCategory.major,
				eraScore=3
			)
		elif self == MomentType.worldCircumnavigated:
			# 124
			return MomentTypeData(
				name="World Circumnavigated",
				summary="Your civilization has revealed a tile in every vertical line of the map. " +
				         "This forms a path around the world, even if the path does not end where it began.",
				instanceText=None,
				category=MomentCategory.major,
				eraScore=3
			)

		# -----------------------------------------
		# minor
		# aggressiveCityPlacement  # 200
		# artifactExtracted  # 201
		elif self == MomentType.barbarianCampDestroyed:
			# 202
			return MomentTypeData(
				name="TXT_KEY_MOMENT_BARBARIAN_CAMP_DESTROYED_TITLE",
				summary="TXT_KEY_MOMENT_BARBARIAN_CAMP_DESTROYED_SUMMARY",
				instanceText="TXT_KEY_MOMENT_BARBARIAN_CAMP_DESTROYED_INSTANCE",
				category=MomentCategory.minor,
				eraScore=2,
				minEra=EraType.ancient,
				maxEra=EraType.medieval
			)
		# causeForWar(warType: CasusBelliType, civilizationType: CivilizationType)  # 203
		# cityReturnsToOriginalOwner(cityName: String, originalCivilization: CivilizationType)  # 204
		# cityStateArmyLevied  # 205
		# coastalFloodMitigated  # 206

		elif self == MomentType.desertCity:  # (cityName: String)
			# 207
			return MomentTypeData(
				name="TXT_KEY_MOMENT_DESERT_CITY_TITLE",
				summary="TXT_KEY_MOMENT_DESERT_CITY_SUMMARY",
				instanceText="TXT_KEY_MOMENT_DESERT_CITY_INSTANCE",
				category=MomentCategory.minor,
				eraScore=1
			)
		# ...
		elif self == MomentType.metNewCivilization:
			# 222
			return MomentTypeData(
				name="Met New Civilization",
				summary="You have made contact with a new civilization.",
				instanceText=None,
				category=MomentCategory.minor,
				eraScore=1
			)
		# oldGreatPersonRecruited  # 223
		elif self == MomentType.oldWorldWonderCompleted:
			# 224
			return MomentTypeData(
				name="Old World Wonder Completed",
				summary="A World Wonder is completed." +
				         "Even though it belongs to a bygone era, it will still show our grandeur over other civilizations.",
				instanceText=None,
				category=MomentCategory.minor,
				eraScore=3
			)
		# operationIvyCompleted 225
		elif self == MomentType.pantheonFounded:  # (pantheon: PantheonType)
			# 226
			return MomentTypeData(
				name="Pantheon Founded",
				summary="Your people adopt the Belief ##pantheon.name()## in a Pantheon.",
				instanceText=None,
				category=MomentCategory.minor,
				eraScore=1,
				maxEra=EraType.classical
			)
		# riverFloodMitigated  # 227 #
		# satelliteLaunchedIntoOrbit  # 228 #
		elif self == MomentType.snowCity:  # (cityName: String)
			# 229
			return MomentTypeData(
				name="TXT_KEY_MOMENT_SNOW_CITY_TITLE",
				summary="TXT_KEY_MOMENT_SNOW_CITY_SUMMARY",
				instanceText="TXT_KEY_MOMENT_SNOW_CITY_INSTANCE",
				category=MomentCategory.minor,
				eraScore=1
			)
		# strategicResourcePotentialUnleashed  # 230 #
		elif self == MomentType.tradingPostEstablishedInNewCivilization: # (civilization: CivilizationType)
			# 231
			return MomentTypeData(
				name="TXT_KEY_MOMENT_TRADING_POST_ESTABLISHED_IN_NEW_CIVILIZATION_TITLE",
				summary="TXT_KEY_MOMENT_TRADING_POST_ESTABLISHED_IN_NEW_CIVILIZATION_SUMMARY",
				instanceText="TXT_KEY_MOMENT_TRADING_POST_ESTABLISHED_IN_NEW_CIVILIZATION_INSTANCE",
				category=MomentCategory.minor,
				eraScore=1
			)
		# tribalVillageContacted  # 232
		elif self == MomentType.tundraCity:  # (cityName: String)
			# 233
			return MomentTypeData(
				name="TXT_KEY_MOMENT_TUNDRA_CITY_TITLE",
				summary="TXT_KEY_MOMENT_TUNDRA_CITY_SUMMARY",
				instanceText="TXT_KEY_MOMENT_TUNDRA_CITY_INSTANCE",
				category=MomentCategory.minor,
				eraScore=1
			)
		elif self == MomentType.unitPromotedWithDistinction:
			# 234
			return MomentTypeData(
				name="Unit Promoted with Distinction",
				summary="One of your units reaches its fourth level of promotion.",
				instanceText=None,
				category=MomentCategory.minor,
				eraScore=1
			)
		elif self == MomentType.wonderCompleted:
			# 235
			return MomentTypeData(
				name="World Wonder Completed",
				summary="A world wonder is completed, showing our grandeur over other civilizations.",
				instanceText=None,
				category=MomentCategory.minor,
				eraScore=4
			)

		# hidden
		# shipSunk  # 300 for artifacts
		elif self == MomentType.battleFought:
			# 301
			return MomentTypeData(
				name="TXT_KEY_MOMENT_BATTLE_FOUGHT_TITLE",
				summary="TXT_KEY_MOMENT_BATTLE_FOUGHT_SUMMARY",
				instanceText=None,
				category=MomentCategory.hidden,
				eraScore=0
			)
		elif self == MomentType.dedicationTriggered:
			# 302
			return MomentTypeData(
				name="Dedication triggered",
				summary="Dedication triggered",
				instanceText=None,
				category=MomentCategory.hidden,
				eraScore=1
			)

		raise InvalidEnumError(self)


class Moment:
	def __init__(self, momentType: MomentType, turn: int, civilization: Optional[CivilizationType] = None,
	             cityName: Optional[str] = None, continentName: Optional[str] = None,
	             eraType: Optional[EraType] = None, naturalWonder: Optional[FeatureType] = None,
	             dedication: Optional[DedicationType] = None, wonder: Optional[WonderType] = None,
	             cityState: Optional[CityStateType] = None, pantheon: Optional[PantheonType] = None):
		self.momentType = momentType
		self.turn = turn

		# meta
		self.civilization: Optional[CivilizationType] = civilization
		self.cityName: Optional[str] = cityName
		self.continentName: Optional[str] = continentName
		self.eraType: Optional[EraType] = eraType
		self.naturalWonder: Optional[FeatureType] = naturalWonder
		self.dedication: Optional[DedicationType] = dedication
		self.wonder: Optional[WonderType] = wonder
		self.cityState: Optional[CityStateType] = cityState
		self.pantheon: Optional[PantheonType] = pantheon

	def __repr__(self):
		return f'Moment({self.momentType.name()}, ...)'

	def __eq__(self, other):
		if not isinstance(other, Moment):
			return False

		# 1 - admiralDefeatsEnemy
		# 2 - allGovernorsAppointed
		if self.momentType == MomentType.allGovernorsAppointed and other.momentType == MomentType.allGovernorsAppointed:
			return True

		# 3 - canalCompleted

		# 4 - cityNearFloodableRiver(cityName: String)
		if self.momentType == MomentType.cityNearFloodableRiver and other.momentType == MomentType.cityNearFloodableRiver:
			return self.cityName == other.cityName and other.cityName is not None

		# 5 - cityNearVolcano
		if self.momentType == MomentType.cityNearVolcano and other.momentType == MomentType.cityNearVolcano:
			return self.cityName == other.cityName and other.cityName is not None

		# 6 - cityOfAwe
		elif self.momentType == MomentType.cityOfAwe and other.momentType == MomentType.cityOfAwe:
			return self.cityName == other.cityName and other.cityName is not None

		# 7 - cityOnNewContinent
		elif self.momentType == MomentType.cityOnNewContinent and other.momentType == MomentType.cityOnNewContinent:
			return self.cityName == other.cityName and other.cityName is not None and \
				self.continentName == other.continentName and other.continentName is not None

		# 8 - cityStatesFirstSuzerain(cityState: CityStateType)
		elif self.momentType == MomentType.cityStatesFirstSuzerain and other.momentType == MomentType.cityStatesFirstSuzerain:
			return True  # no need to check the cityState - it can only one be first

		# 9 - cityStateArmyLeviedNearEnemy
		# 10 - climateChangePhase
		# 11 - darkAgeBegins
		elif self.momentType == MomentType.darkAgeBegins and other.momentType == MomentType.darkAgeBegins:
			return True

		# 12 - discoveryOfANaturalWonder
		elif self.momentType == MomentType.discoveryOfANaturalWonder and \
			other.momentType == MomentType.discoveryOfANaturalWonder:
			return self.naturalWonder == other.naturalWonder and other.naturalWonder is not None

		# 13 - emergencyCompletedSuccessfully
		# 14 - emergencySuccessfullyDefended
		# 15 - enemyCityAdoptsOurReligion
		# 16 - enemyCityStatePacified
		# 17 - enemyFormationDefeated
		# 18 - enemyVeteranDefeated
		# 19 - exoplanetExpeditionLaunched
		# 20 - finalForeignCityTaken
		# 21 - firstAerodromeFullyDeveloped
		# 22 - firstBustlingCity(cityName: String)
		# 23 - firstCivicOfNewEra(eraType: EraType)
		# 24 - firstCorporationCreated
		# 25 - firstCorporationInTheWorld
		# 26 - firstDiscoveryOfANaturalWonder
		# 27 - firstDiscoveryOfANewContinent
		elif self.momentType == MomentType.firstDiscoveryOfANewContinent and \
			other.momentType == MomentType.firstDiscoveryOfANewContinent:
			return True

		# 28 - firstEncampmentFullyDeveloped
		# 29 - firstEnormousCity(cityName: String)
		# 30 - firstEntertainmentComplexFullyDeveloped
		# 31 - firstGiganticCity(cityName: String)
		# 32 - firstGreenImprovement
		# 33 - firstGreenImprovementInWorld
		# 34 - firstHeroClaimed
		# 35 - firstHeroDeparted
		# 36 - firstHeroRecalled
		# 37 - firstImprovementAfterNaturalDisaster
		# 38 - firstIndustryCreated
		# 39 - firstIndustryInTheWorld
		# 40 - firstLargeCity(cityName: String)
		# 41 - firstLuxuryResourceMonopoly
		# 42 - firstLuxuryResourceMonopolyInTheWorld
		# 43 - firstMasterSpyEarned
		# 44 - firstMountainTunnel
		# 45 - firstMountainTunnelInTheWorld

		# 46 - firstNeighborhoodCompleted
		elif self.momentType == MomentType.firstNeighborhoodCompleted and \
			other.momentType == MomentType.firstNeighborhoodCompleted:
			return True

		# 47 - firstRailroadConnection
		# 48 - firstRailroadConnectionInWorld
		# 49 - firstResourceConsumedForPower
		# 50 - firstResourceConsumedForPowerInWorld
		# 51 - firstRockBandConcert
		# 52 - firstRockBandConcertInWorld
		# 53 - firstSeasideResort
		# 54 - firstShipwreckExcavated

		# 55 - firstTechnologyOfNewEra
		elif self.momentType == MomentType.firstTechnologyOfNewEra and other.momentType == MomentType.firstTechnologyOfNewEra:
			return self.eraType == other.eraType and other.eraType is not None

		# 56 - firstTier1Government(governmentType: GovernmentType)
		# 57 - firstTier1GovernmentInWorld(governmentType: GovernmentType)
		# 58 - firstTier2Government(governmentType: GovernmentType)
		# 59 - firstTier2GovernmentInWorld(governmentType: GovernmentType)
		# 60 - firstTier3Government(governmentType: GovernmentType)
		# 61 - firstTier3GovernmentInWorld(governmentType: GovernmentType)
		# 62 - firstTier4Government(governmentType: GovernmentType)
		# 63 - firstTier4GovernmentInWorld(governmentType: GovernmentType)
		# 64 - firstTradingPostsInAllCivilizations
		# 65 - firstUnitPromotedWithDistinction
		# 66 - firstWaterParkFullyDeveloped
		# 67 - freeCityJoins
		# 68 - generalDefeatsEnemy

		# 69 - goldenAgeBegins
		elif self.momentType == MomentType.goldenAgeBegins and other.momentType == MomentType.goldenAgeBegins:
			return True

		# 70 - governorFullyPromoted
		elif self.momentType == MomentType.governorFullyPromoted and other.momentType == MomentType.governorFullyPromoted:
			return True

		# 71 - greatPersonLuredByFaith
		# 72 - greatPersonLuredByGold
		# 73 - heroicAgeBegins
		# 74 - inquisitionBegins
		# 75 - leviedArmyStandsDown
		# 76 - metAllCivilizations
		# 77 - nationalParkFounded
		# 78 - normalAgeBegins
		# 79 - onTheWaves
		# 80 - religionAdoptsAllBeliefs
		# 81 - religionFounded(religion: ReligionType)
		# 82 - rivalHolyCityConverted
		# 83 - splendidCampusCompleted
		# 84 - splendidCommercialHubCompleted
		# 85 - splendidHarborCompleted
		# 86 - splendidHolySiteCompleted
		# 87 - splendidIndustrialZoneCompleted
		# 88 - splendidTheaterSquareCompleted
		# 89 - takingFlight
		# 90 - threateningCampDestroyed
		# 91 - tradingPostsInAllCivilizations
		# 92 - uniqueBuildingConstructed
		# 93 - uniqueDistrictCompleted
		# 94 - uniqueTileImprovementBuilt
		# 95 - uniqueUnitMarches
		# 96 - worldsFirstArmada
		# 97 - worldsFirstArmy
		# 98 - worldsFirstBustlingCity(cityName: String)
		# 99 - worldsFirstCircumnavigation
		# 100 - worldsFirstCivicOfNewEra(eraType: EraType)
		# 101 - worldsFirstCorps
		# 102 - worldsFirstEnormousCity(cityName: String)
		# 103 - worldsFirstExoplanetExpeditionLaunched
		# 104 - worldsFirstFleet
		# 105 - worldsFirstFlight
		# 106 - worldsFirstGiganticCity(cityName: String)
		# 107 - worldsFirstInquisition
		# 108 - worldsFirstLandingOnTheMoon
		# 109 - worldsFirstLargeCity(cityName: String)
		# 110 - worldsFirstMartianColonyEstablished
		# 111 - worldsFirstNationalPark

		# 112 - worldsFirstNeighborhood
		elif self.momentType == MomentType.worldsFirstNeighborhood and other.momentType == MomentType.worldsFirstNeighborhood:
			return True

		# 113 - worldsFirstPantheon
		elif self.momentType == MomentType.worldsFirstPantheon and other.momentType == MomentType.worldsFirstPantheon:
			return True

		# 114 - worldsFirstReligion
		# 115 - worldsFirstReligionToAdoptAllBeliefs
		# 116 - worldsFirstSatelliteInOrbit
		# 117 - worldsFirstSeafaring
		# 118 - worldsFirstSeasideResort
		# 119 - worldsFirstShipwreckExcavated
		# 120 - worldsFirstStrategicResourcePotentialUnleashed

		# 121 - worldsFirstTechnologyOfNewEra
		elif self.momentType == MomentType.worldsFirstTechnologyOfNewEra and \
			other.momentType == MomentType.worldsFirstTechnologyOfNewEra:
			return self.eraType == other.eraType and other.eraType is not None

		# 122 - worldsFirstToMeetAllCivilizations

		# 123 - worldsLargestCivilization
		elif self.momentType == MomentType.worldsLargestCivilization and \
			other.momentType == MomentType.worldsLargestCivilization:
			return True

		# 124 - worldCircumnavigated
		elif self.momentType == MomentType.worldCircumnavigated and other.momentType == MomentType.worldCircumnavigated:
			return True

		# minor
		# 200 - aggressiveCityPlacement
		# 201 - artifactExtracted
		# 202 - barbarianCampDestroyed
		# 203 - causeForWar(warType: CasusBelliType, civilizationType: CivilizationType)
		# 204 - cityReturnsToOriginalOwner(cityName: String, originalCivilization: CivilizationType)
		# 205 - cityStateArmyLevied
		# 206 - coastalFloodMitigated

		# 207 - desertCity = 'desertCity'  # (cityName: String)
		elif self.momentType == MomentType.desertCity and other.momentType == MomentType.desertCity:
			return self.cityName == other.cityName and other.cityName is not None

		# 208 - diplomaticVictoryResolutionWon
		# 209 - firstArmada
		# 210 - firstArmy
		# 211 - firstCorps
		# 212 - firstFleet
		# 213 - foreignCapitalTaken
		# 214 - greatPersonRecruited
		# 215 - heroClaimed
		# 216 - heroDeparted
		# 217 - heroRecalled
		# 218 - landedOnTheMoon
		# 219 - manhattanProjectCompleted
		# 220 - martianColonyEstablished
		# 221 - masterSpyEarned

		# 222 - metNewCivilization
		elif self.momentType == MomentType.metNewCivilization and other.momentType == MomentType.metNewCivilization:
			return self.civilization == other.civilization and other.civilization is not None

		# 223 - oldGreatPersonRecruited
		# 224 oldWorldWonderCompleted
		# 225 - operationIvyCompleted
		# 226 - pantheonFounded(pantheon: PantheonType)
		# 227 - riverFloodMitigated
		# 228 - satelliteLaunchedIntoOrbit

		# 229 - snowCity (cityName: String)
		elif self.momentType == MomentType.snowCity and other.momentType == MomentType.snowCity:
			return self.cityName == other.cityName and other.cityName is not None

		# 230 - strategicResourcePotentialUnleashed
		# 231 - tradingPostEstablishedInNewCivilization(civilization: CivilizationType)
		elif self.momentType == MomentType.tradingPostEstablishedInNewCivilization and other.momentType == MomentType.tradingPostEstablishedInNewCivilization:
			return self.civilization == other.civilization and other.civilization is not None

		# 232 - tribalVillageContacted

		# 233 - tundraCity (cityName: String)
		elif self.momentType == MomentType.tundraCity and other.momentType == MomentType.tundraCity:
			return self.cityName == other.cityName and other.cityName is not None

		# 234 - unitPromotedWithDistinction

		# 235 - wonderCompleted(wonder: WonderType)
		elif self.momentType == MomentType.wonderCompleted and other.momentType == MomentType.wonderCompleted:
			return self.wonder == other.wonder

		# hidden
		# 300 - shipSunk
		# 301 - battleFought

		# 302 - dedicationTriggered
		elif self.momentType == MomentType.dedicationTriggered and other.momentType == MomentType.dedicationTriggered:
			return self.dedication == other.dedication and other.dedication is not None

		return False
