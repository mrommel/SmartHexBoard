import logging
import sys

from smarthexboard.smarthexboardlib.game.cities import ReligiousFollowChangeReasonType
from smarthexboard.smarthexboardlib.game.players import PlayerReligion
from smarthexboard.smarthexboardlib.game.religions import PantheonType, ReligionType


class Religions:
	def __init__(self):
		pass

	def doTurn(self, simulation):
		self.spreadReligion(simulation)

	def foundPantheonBy(self, player, pantheonType: PantheonType, simulation):
		player.religion.foundPantheon(pantheonType, simulation)

	def availablePantheons(self, simulation) -> [PantheonType]:
		availablePantheonList: [PantheonType] = PantheonType.all()

		for player in simulation.players:
			playerReligion = player.religion

			availablePantheonList = list(filter(lambda r: r != playerReligion.pantheon(), availablePantheonList))

		return availablePantheonList

	def availableReligions(self, simulation) -> [ReligionType]:
		availableReligionList: [ReligionType] = ReligionType.all()

		for player in simulation.players:
			playerReligion = player.religion
			playerCurrentReligion: ReligionType = playerReligion.currentReligion()

			availableReligionList = list(filter(lambda r: r != playerCurrentReligion, availableReligionList))

		return availableReligionList

	def estalishedReligions(self, simulation) -> [ReligionType]:
		estalishedReligionList: [ReligionType] = []

		for player in simulation.players:
			playerReligion = player.religion
			playerCurrentReligion: ReligionType = playerReligion.currentReligion()

			if playerCurrentReligion != ReligionType.none:
				estalishedReligionList.append(playerCurrentReligion)

		return estalishedReligionList

	def numberOfAvailableReligions(self, simulation) -> int:
		maxReligions = simulation.mapSize().maxActiveReligions()
		numberOfEstablishedReligions = len(self.estalishedReligions(simulation))

		return max(0, maxReligions - numberOfEstablishedReligions)

	def availableReligions(self, simulation) -> [ReligionType]:
		allReligions: [ReligionType] = ReligionType.all()
		usedReligions: [ReligionType] = self.estalishedReligions(simulation)

		for usedReligion in usedReligions:
			allReligions = list(filter(lambda r: r != usedReligion, allReligions))

		return allReligions

	def religions(self, simulation) -> [PlayerReligion]:
		religionsArray: [PlayerReligion] = []

		for player in simulation.players:
			religionsArray.append(player.religion)

		return religionsArray

	def spreadReligion(self, simulation):
		"""Spread religious pressure into adjacent cities"""
		# Loop through all the players
		for player in simulation.players:
			if not player.isAlive():
				continue

			if player.isBarbarian():
				continue
				
			if player.isFreeCity():
				continue

			# Loop through each of their cities
			for city in simulation.citiesOf(player):
				self.spreadReligionTo(city, simulation)

		return

	def spreadReligionTo(self, city, simulation):
		"""Spread religious pressure to one city"""
		# Used to calculate how many trade routes are applying pressure to this city. 
		# This resets the value so we get a true count every turn.
		city.cityReligion.resetNumberOfTradeRoutePressure()

		# Is this a city where a religion was founded?
		if city.cityReligion.isHolyCityAnyReligion():
			city.cityReligion.addHolyCityPressure(simulation)

		# Loop through all the players
		for player in simulation.players:
			if not player.isAlive():
				continue

			if player.isBarbarian():
				continue

			if player.isFreeCity():
				continue

			# iSpyPressure = kPlayer.GetReligions()->GetSpyPressure((PlayerTypes)
			# iI);
			# if (iSpyPressure > 0)
			# {
			# if (kPlayer.GetEspionage()->GetSpyIndexInCity(pCity) != -1)
			# {
			# 	ReligionTypes
			# eReligionFounded = kPlayer.GetReligions()->GetCurrentReligion(false);
			# if (eReligionFounded == NO_RELIGION)
			# {
			# eReligionFounded = kPlayer.GetReligions()->GetReligionInMostCities();
			# }
			# if (eReligionFounded != NO_RELIGION and eReligionFounded > RELIGION_PANTHEON)
			# {
			# pCity->GetCityReligions()->AddSpyPressure(eReligionFounded, iSpyPressure);
			# }
			# }

			# Loop through each of their cities
			for loopCity in simulation.citiesOf(player):
				# Ignore the same city
				if city.location == loopCity.location:
					continue

				loopCityReligion = loopCity.cityReligion

				for religionType in list(ReligionType):
					if not self.isValidTarget(religionType, loopCity, city):
						continue

					if loopCityReligion.numberOfFollowersOf(religionType) > 0:
						connectedWithTrade: bool = False
						relativeDistancePercent: int = 0

						if not self.isConnected(religionType, loopCity, city, connectedWithTrade, relativeDistancePercent, simulation):
							continue

						(pressure, numTradeRoutes) = self.adjacentCityReligiousPressure(religionType, loopCity, city, True, False, connectedWithTrade, relativeDistancePercent)

						if pressure > 0:
							city.cityReligion.addReligiousPressure(ReligiousFollowChangeReasonType.followerChangeAdjacentPressure, pressure, religionType, simulation)

							if numTradeRoutes > 0:
								city.cityReligion.incrementNumberOfTradeRouteConnectionsBy(numTradeRoutes, religionType)

		return

	def isValidTarget(self, religionType: ReligionType, fromCity, toCity) -> bool:
		if fromCity.player != toCity.player:
			# if fromCity.player.is (GET_PLAYER(pFromCity->getOwner()).GetPlayerTraits()->IsNoNaturalReligionSpread()):
			# 	ReligionTypes ePantheon = GET_PLAYER(pFromCity->getOwner()).GetReligions()->GetReligionCreatedByPlayer(true);
			# 	const CvReligion * pReligion2 = GetReligion(ePantheon, pFromCity->getOwner());
			# 	if (pReligion2 and (pFromCity->GetCityReligions()->GetNumFollowers(ePantheon) > 0) and pReligion2->m_Beliefs.GetUniqueCiv() == GET_PLAYER(pFromCity->getOwner()).getCivilizationType())
			# 		return False;

			# if (GET_PLAYER(pToCity->getOwner()).GetPlayerTraits()->IsNoNaturalReligionSpread()):
			# 	ReligionTypes ePantheon = GET_PLAYER(pToCity->getOwner()).GetReligions()->GetReligionCreatedByPlayer(true);
			# 	const CvReligion * pReligion2 = GetReligion(ePantheon, pToCity->getOwner());
			# 	if (pReligion2 and (pToCity->GetCityReligions()->GetNumFollowers(ePantheon) > 0) and pReligion2->m_Beliefs.GetUniqueCiv() == GET_PLAYER(pToCity->getOwner()).getCivilizationType()):
			# 		return false;
			pass
		else:
			# if (pFromCity->getOwner() == pToCity->getOwner())
			# if (GET_PLAYER(pFromCity->getOwner()).GetPlayerTraits()->IsNoNaturalReligionSpread()):
			# 	ReligionTypes ePantheon = GET_PLAYER(pFromCity->getOwner()).GetReligions()->GetReligionCreatedByPlayer(true);
			# 	const CvReligion * pReligion2 = GetReligion(ePantheon, pFromCity->getOwner());
			# 	if (ePantheon != eReligion and pReligion2 and (pFromCity->GetCityReligions()->GetNumFollowers(ePantheon) > 0) and pReligion2->m_Beliefs.GetUniqueCiv() == GET_PLAYER(pFromCity->getOwner()).getCivilizationType())
			# 		return false;

			# if (GET_PLAYER(pToCity->getOwner()).GetPlayerTraits()->IsNoNaturalReligionSpread())
			# ReligionTypes ePantheon = GET_PLAYER(pToCity->getOwner()).GetReligions()->GetReligionCreatedByPlayer(true);
			# const CvReligion * pReligion2 = GetReligion(ePantheon, pToCity->getOwner());
			# if (ePantheon != eReligion and pReligion2 and (pToCity->GetCityReligions()->GetNumFollowers(ePantheon) > 0) and pReligion2->m_Beliefs.GetUniqueCiv() == GET_PLAYER(pToCity->getOwner()).getCivilizationType())
			# return false;
			pass

		# if (!GET_PLAYER(pToCity->getOwner()).isMinorCiv() and GET_PLAYER(
		# 	pToCity->getOwner()).GetPlayerTraits()->IsForeignReligionSpreadImmune()):
		# 	ReligionTypes eToCityReligion = GET_PLAYER(pToCity->getOwner()).GetReligions()->GetReligionCreatedByPlayer(false);
		# if ((eToCityReligion != NO_RELIGION) and (eReligion != eToCityReligion))
		# return false
		# eToCityReligion = GET_PLAYER(pToCity->getOwner()).GetReligions()->GetReligionInMostCities();
		# if ((eToCityReligion != NO_RELIGION) and (eReligion > RELIGION_PANTHEON) and (eReligion != eToCityReligion))
		# return false

		# if (GET_PLAYER(pToCity->getOwner()).isMinorCiv()):
		# 	PlayerTypes eAlly = GET_PLAYER(pToCity->getOwner()).GetMinorCivAI()->GetAlly();
		# if (eAlly != NO_PLAYER):
		# if (GET_PLAYER(eAlly).GetPlayerTraits()->IsForeignReligionSpreadImmune()):
		# 	ReligionTypes eToCityReligion = GET_PLAYER(eAlly).GetReligions()->GetReligionCreatedByPlayer(false);
		# if ((eToCityReligion != NO_RELIGION) and (eReligion != eToCityReligion)):
		# return False
		# eToCityReligion = GET_PLAYER(eAlly).GetReligions()->GetReligionInMostCities();
		# if ((eToCityReligion != NO_RELIGION) and (eReligion > RELIGION_PANTHEON) and (eReligion != eToCityReligion))
		# return False

		# # if defined(MOD_RELIGION_LOCAL_RELIGIONS)
		# if (MOD_RELIGION_LOCAL_RELIGIONS and GC.getReligionInfo(eReligion)->IsLocalReligion())
		# # Can only spread a local religion to our own cities or City States
		# if (pToCity->getOwner() < MAX_MAJOR_CIVS and pFromCity->getOwner() != pToCity->getOwner()):
		# return False;
		#
		# # Cannot spread if either city is occupied or a puppet
		# if ((pFromCity->IsOccupied() and !pFromCity->IsNoOccupiedUnhappiness()) | | pFromCity->IsPuppet() | |
		# (pToCity->IsOccupied() and !pToCity->IsNoOccupiedUnhappiness()) | | pToCity->IsPuppet()) {
		# return false;
		# # endif*/

		return True

	def isConnected(self, religionType: ReligionType, fromCity, toCity, connectedWithTrade: bool, relativeDistancePercent: int, simulation) -> bool:
		pReligion = fromCity.cityReligion.religiousMajority()

		if pReligion is None:
			return False

		fromCityPlayerReligion = fromCity.player.religion

		connectedWithTrade = False
		relativeDistancePercent = sys.maxsize

		if religionType == pReligion:
			connectedWithTrade = simulation.citiesHaveTradeConnection(fromCity, toCity)

			if connectedWithTrade:
				relativeDistancePercent = 1  # very close
				return True

		# Boost to distance due to belief?
		distanceMod = fromCityPlayerReligion.spreadDistanceModifier()

		raise Exception("not implemented")
		# / * # Boost from policy of other player?
		# if (GET_PLAYER(pToCity->getOwner()).GetReligionDistance() != 0)
		# {
		# if (pToCity->GetCityReligions()->GetReligiousMajority() <= RELIGION_PANTHEON)
		# {
		# # Do we have a religion?
		# ReligionTypes ePlayerReligion = GetReligionCreatedByPlayer(pToCity->getOwner());
		#
		# if (ePlayerReligion <= RELIGION_PANTHEON):
		# 	# No..but did we adopt one?
		# 	ePlayerReligion = GET_PLAYER(pToCity->getOwner()).GetReligions()->GetReligionInMostCities();
		# 	# Nope, so full power.
		# 	if (ePlayerReligion <= RELIGION_PANTHEON)
		# 	{
		# 		iDistanceMod += GET_PLAYER(pToCity->getOwner()).GetReligionDistance();
		# 	}
		# 	# Yes, so only apply distance bonus to adopted faith.
		# 	else if (eReligion == ePlayerReligion)
		# 	{
		# 	iDistanceMod += GET_PLAYER(pToCity->getOwner()).GetReligionDistance();
		# 	}
		# 	}
		# # We did! Only apply bonuses if we founded this faith or it is the religion we have in most of our cities.
		# else if ((pReligion->m_eFounder == pToCity->getOwner()) | | (eReligion == GET_PLAYER(pToCity
		# ->getOwner()).GetReligions()->GetReligionInMostCities()))
		# {
		# 	iDistanceMod += GET_PLAYER(pToCity->getOwner()).GetReligionDistance();
		# }
		# }
		# }
		#
		# int
		# iMaxDistanceLand = GET_PLAYER(pFromCity->getOwner()).GetTrade()->GetTradeRouteRange(DOMAIN_LAND,
		#                                                                                     pFromCity) * SPath::getNormalizedDistanceBase();
		# int
		# iMaxDistanceSea = GET_PLAYER(pFromCity->getOwner()).GetTrade()->GetTradeRouteRange(DOMAIN_SEA,
		#                                                                                    pFromCity) * SPath::getNormalizedDistanceBase();
		#
		# if (iDistanceMod > 0)
		# {
		# iMaxDistanceLand *= (100 + iDistanceMod);
		# iMaxDistanceLand /= 100;
		# iMaxDistanceSea *= (100 + iDistanceMod);
		# iMaxDistanceSea /= 100;
		# }
		#
		# // estimate the distance between the cities from the traderoute cost.
		# // will be influences by terrain features, routes, open borders etc
		# // note: trade routes are not necessarily symmetric in case of unrevealed tiles etc
		# SPath path;
		# if (GC.getGame().GetGameTrade()->HavePotentialTradePath(false, pFromCity, pToCity, & path))
		# {
		# int iPercent = (path.iNormalizedDistanceRaw * 100) /iMaxDistanceLand;
		# iRelativeDistancePercent = min(iRelativeDistancePercent, iPercent);
		# }
		# if (GC.getGame().GetGameTrade()->HavePotentialTradePath(false, pToCity, pFromCity, & path))
		# {
		# int iPercent = (path.iNormalizedDistanceRaw * 100) /iMaxDistanceLand;
		# iRelativeDistancePercent = min(iRelativeDistancePercent, iPercent);
		# }
		# if (GC.getGame().GetGameTrade()->HavePotentialTradePath(true, pFromCity, pToCity, & path))
		# {
		# int iPercent = (path.iNormalizedDistanceRaw * 100) /iMaxDistanceSea;
		# iRelativeDistancePercent = min(iRelativeDistancePercent, iPercent);
		# }
		# if (GC.getGame().GetGameTrade()->HavePotentialTradePath(true, pToCity, pFromCity, & path))
		# {
		# int iPercent = (path.iNormalizedDistanceRaw * 100) /iMaxDistanceSea;
		# iRelativeDistancePercent = min(iRelativeDistancePercent, iPercent);
		# }
		#
		# return (iRelativeDistancePercent < 100);
		# * /

		return False

	def adjacentCityReligiousPressure(self, religionType: ReligionType, fromCity, toCity, actualValue: bool,
									  pretendTradeConnection: bool, connectedWithTrade: bool,
									  relativeDistancePercent: int) -> (int, int):
		"""How much pressure is exerted between these cities?"""
		fromCityReligion = fromCity.cityReligion

		numTradeRoutesInfluencing = 0

		if self.religionOf(religionType, fromCity.player) is None:
			return (0, 0)

		basePressure: int = 150  # ReligiousPressureAdjacentCity
		pressureMod: int = 0

		# Does this city have a majority religion?
		majorityReligion = fromCity.cityReligion.religiousMajority()
		if majorityReligion != religionType:
			return (0, 0)

		# do we have a trade route or pretend to have one
		if connectedWithTrade or pretendTradeConnection:
			if actualValue:
				numTradeRoutesInfluencing += 1

			tradeReligionModifier = 50  # GET_PLAYER(pFromCity->getOwner()).GetPlayerTraits()->GetTradeReligionModifier();
			tradeReligionModifier += 0  # GET_PLAYER(pFromCity->getOwner()).GetTradeReligionModifier();
			tradeReligionModifier += fromCity.religiousTradeRouteModifier()

			pressureMod += tradeReligionModifier
		else:
			# if there is no trade route, base pressure falls off with distance
			pressurePercent = max(100 - relativeDistancePercent, 1)
			# make the scaling quadratic - four times as many cities in range if we double the radius!
			basePressure = int((basePressure * pressurePercent * pressurePercent) / (100 * 100))

		# Building that boosts pressure from originating city?
		pressureMod += fromCityReligion.religiousPressureModifier(religionType)

		pressure = basePressure * (100 + pressureMod)

		logging.debug(f"AdjacentCityReligiousPressure for {religionType} from {fromCity.name} to {toCity.name} is {pressure}")
		return max(0, int(pressure / 100)), numTradeRoutesInfluencing

	def religionOf(self, religionType: ReligionType, player):
		if player.religion.currentReligion() == religionType:
			return player.religion

		return None
