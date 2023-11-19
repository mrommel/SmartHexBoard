from smarthexboard.smarthexboardlib.core.base import ExtendedEnum


class ProjectType(ExtendedEnum):
	none = 'none'
	breadAndCircuses = 'breadAndCircuses'
	launchEarthSatellite = 'launchEarthSatellite'
	launchMoonLanding = 'launchMoonLanding'
	launchMarsColony = 'launchMarsColony'
	exoplanetExpedition = 'exoplanetExpedition'
	terrestrialLaserStation = 'terrestrialLaserStation'

	def productionCost(self) -> float:
		return 0.0

	def unique(self) -> bool:
		return False
