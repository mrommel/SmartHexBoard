from typing import Optional, Union

from smarthexboard.smarthexboardlib.core.base import ExtendedEnum


class Continent:
	def __init__(self, identifier: Union[int, dict], name: Optional[str]=None, mapModel=None):
		if isinstance(identifier, int):
			self.identifier = identifier
			self.name = name
			self.mapModel = mapModel
			self.points = []
			self.continentType = ContinentType.none
		elif isinstance(identifier, dict):
			param_dict: dict = identifier
			self.identifier = param_dict['identifier']
			self.name = param_dict['name']
			self.mapModel = None
			self.points = []
			self.continentType = ContinentType.none
		else:
			raise Exception('Unsupported parameter combination')

	def add(self, point):
		self.points.append(point)

	def __str__(self):
		return f'Content: {self.identifier} {self.name}'


class ContinentType:
	pass


class ContinentType(ExtendedEnum):
	none = 'none'

	africa = 'africa'
	amasia = 'amasia'
	america = 'america'
	antarctica = 'antarctica'
	arctica = 'arctica'
	asia = 'asia'
	asiamerica = 'asiamerica'
	atlantica = 'atlantica'
	atlantis = 'atlantis'
	australia = 'australia'
	avalonia = 'avalonia'
	azania = 'azania'
	baltica = 'baltica'
	cimmeria = 'cimmeria'
	columbia = 'columbia'
	congocraton = 'congocraton'
	euramerica = 'euramerica'
	europe = 'europe'
	gondwana = 'gondwana'
	kalaharia = 'kalaharia'
	kazakhstania = 'kazakhstania'
	kernorland = 'kernorland'
	kumarikandam = 'kumarikandam'
	laurasia = 'laurasia'
	laurentia = 'laurentia'
	lemuria = 'lemuria'
	mu = 'mu'
	nena = 'nena'
	northAmerica = 'northAmerica'
	novoPangaea = 'novoPangaea'
	nuna = 'nuna'
	pangaea = 'pangaea'
	pangaeaUltima = 'pangaeaUltima'
	pannotia = 'pannotia'
	rodinia = 'rodinia'
	siberia = 'siberia'
	southAmerica = 'southAmerica'
	terraAustralis = 'terraAustralis'
	ur = 'ur'
	vaalbara = 'vaalbara'
	vendian = 'vendian'
	zealandia = 'zealandia'

	@staticmethod
	def fromName(continentName: str) -> ContinentType:
		if continentName == 'ContinentType.none' or continentName == 'none':
			return ContinentType.none

		elif continentName == 'ContinentType.africa' or continentName == 'africa':
			return ContinentType.africa
		elif continentName == 'ContinentType.amasia' or continentName == 'amasia':
			return ContinentType.amasia
		elif continentName == 'ContinentType.america' or continentName == 'america':
			return ContinentType.america
		elif continentName == 'ContinentType.antarctica' or continentName == 'antarctica':
			return ContinentType.antarctica
		elif continentName == 'ContinentType.arctica' or continentName == 'arctica':
			return ContinentType.arctica
		elif continentName == 'ContinentType.asia' or continentName == 'asia':
			return ContinentType.asia
		elif continentName == 'ContinentType.asiamerica' or continentName == 'asiamerica':
			return ContinentType.asiamerica
		elif continentName == 'ContinentType.atlantica' or continentName == 'atlantica':
			return ContinentType.atlantica
		elif continentName == 'ContinentType.atlantis' or continentName == 'atlantis':
			return ContinentType.atlantis
		elif continentName == 'ContinentType.australia' or continentName == 'australia':
			return ContinentType.australia
		elif continentName == 'ContinentType.avalonia' or continentName == 'avalonia':
			return ContinentType.avalonia
		elif continentName == 'ContinentType.azania' or continentName == 'azania':
			return ContinentType.azania
		elif continentName == 'ContinentType.baltica' or continentName == 'baltica':
			return ContinentType.baltica
		elif continentName == 'ContinentType.cimmeria' or continentName == 'cimmeria':
			return ContinentType.cimmeria
		elif continentName == 'ContinentType.columbia' or continentName == 'columbia':
			return ContinentType.columbia
		elif continentName == 'ContinentType.congocraton' or continentName == 'congocraton':
			return ContinentType.congocraton
		elif continentName == 'ContinentType.euramerica' or continentName == 'euramerica':
			return ContinentType.euramerica
		elif continentName == 'ContinentType.europe' or continentName == 'europe':
			return ContinentType.europe
		elif continentName == 'ContinentType.gondwana' or continentName == 'gondwana':
			return ContinentType.gondwana
		elif continentName == 'ContinentType.kalaharia' or continentName == 'kalaharia':
			return ContinentType.kalaharia
		elif continentName == 'ContinentType.kazakhstania' or continentName == 'kazakhstania':
			return ContinentType.kazakhstania
		elif continentName == 'ContinentType.kernorland' or continentName == 'kernorland':
			return ContinentType.kernorland
		elif continentName == 'ContinentType.kumarikandam' or continentName == 'kumarikandam':
			return ContinentType.kumarikandam
		elif continentName == 'ContinentType.laurasia' or continentName == 'laurasia':
			return ContinentType.laurasia
		elif continentName == 'ContinentType.laurentia' or continentName == 'laurentia':
			return ContinentType.laurentia
		elif continentName == 'ContinentType.lemuria' or continentName == 'lemuria':
			return ContinentType.lemuria
		elif continentName == 'ContinentType.mu' or continentName == 'mu':
			return ContinentType.mu
		elif continentName == 'ContinentType.nena' or continentName == 'nena':
			return ContinentType.nena
		elif continentName == 'ContinentType.northAmerica' or continentName == 'northAmerica':
			return ContinentType.northAmerica
		elif continentName == 'ContinentType.novoPangaea' or continentName == 'novoPangaea':
			return ContinentType.novoPangaea
		elif continentName == 'ContinentType.nuna' or continentName == 'nuna':
			return ContinentType.nuna
		elif continentName == 'ContinentType.pangaea' or continentName == 'pangaea':
			return ContinentType.pangaea
		elif continentName == 'ContinentType.pangaeaUltima' or continentName == 'pangaeaUltima':
			return ContinentType.pangaeaUltima
		elif continentName == 'ContinentType.pannotia' or continentName == 'pannotia':
			return ContinentType.pannotia
		elif continentName == 'ContinentType.rodinia' or continentName == 'rodinia':
			return ContinentType.rodinia
		elif continentName == 'ContinentType.siberia' or continentName == 'siberia':
			return ContinentType.siberia
		elif continentName == 'ContinentType.southAmerica' or continentName == 'southAmerica':
			return ContinentType.southAmerica
		elif continentName == 'ContinentType.terraAustralis' or continentName == 'terraAustralis':
			return ContinentType.terraAustralis
		elif continentName == 'ContinentType.ur' or continentName == 'ur':
			return ContinentType.ur
		elif continentName == 'ContinentType.vaalbara' or continentName == 'vaalbara':
			return ContinentType.vaalbara
		elif continentName == 'ContinentType.vendian' or continentName == 'vendian':
			return ContinentType.vendian
		elif continentName == 'ContinentType.zealandia' or continentName == 'zealandia':
			return ContinentType.zealandia
		else:
			raise Exception(f'No matching case for continentName: "{continentName}"')

	def title(self) -> str:  # cannot be "name"
		return f'Continent: {self.value}'


class Ocean:
	def __init__(self, identifier: int, name: str, mapModel):
		self.identifier = identifier
		self.name = name
		self.mapModel = mapModel
		self.points = []
		self.oceanType = OceanType.none

	def add(self, point):
		self.points.append(point)

	def __str__(self):
		return f'Ocean: {self.identifier} {self.name}'


class OceanType:
	pass


class OceanType(ExtendedEnum):
	# https://civilization.fandom.com/wiki/Ocean_(Civ6)#Ocean_names
	none = 'none'

	atlantic = 'atlantic'
	pacific = 'pacific'
	northSea = 'northSea'  # => sea?
	mareNostrum = 'mareNostrum'
	balticSea = 'balticSea'  # => sea?
	antarctic = 'antarctic'
	arctic = 'arctic'
	iapetus = 'iapetus'
	indian = 'indian'
	panthalassic = 'panthalassic'
	rheic = 'rheic'
	tethys = 'tethys'

	@staticmethod
	def fromName(oceanName: str) -> OceanType:
		if oceanName == 'OceanType.none' or oceanName == 'none':
			return OceanType.none
		elif oceanName == 'OceanType.atlantic' or oceanName == 'atlantic':
			return OceanType.atlantic
		elif oceanName == 'OceanType.pacific' or oceanName == 'pacific':
			return OceanType.pacific
		elif oceanName == 'OceanType.northSea' or oceanName == 'northSea':
			return OceanType.northSea
		elif oceanName == 'OceanType.mareNostrum' or oceanName == 'mareNostrum':
			return OceanType.mareNostrum
		elif oceanName == 'OceanType.balticSea' or oceanName == 'balticSea':
			return OceanType.balticSea
		elif oceanName == 'OceanType.antarctic' or oceanName == 'antarctic':
			return OceanType.antarctic
		elif oceanName == 'OceanType.arctic' or oceanName == 'arctic':
			return OceanType.arctic
		elif oceanName == 'OceanType.iapetus' or oceanName == 'iapetus':
			return OceanType.iapetus
		elif oceanName == 'OceanType.indian' or oceanName == 'indian':
			return OceanType.indian
		elif oceanName == 'OceanType.panthalassic' or oceanName == 'panthalassic':
			return OceanType.panthalassic
		elif oceanName == 'OceanType.rheic' or oceanName == 'rheic':
			return OceanType.rheic
		elif oceanName == 'OceanType.tethys' or oceanName == 'tethys':
			return OceanType.tethys

		raise Exception(f'No matching case for oceanName: "{oceanName}"')
