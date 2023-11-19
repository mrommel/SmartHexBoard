from marshmallow import Schema, fields

from smarthexboard.smarthexboardlib.map.areas import Ocean, Continent
from smarthexboard.smarthexboardlib.map.map import MapModel, Tile
from smarthexboard.smarthexboardlib.map.types import StartLocation
from smarthexboard.smarthexboardlib.serialisation.base import PointSchema, HexAreaSchema


class TileSchema(Schema):
	point = fields.Nested(PointSchema)
	terrain = fields.String(attribute="_terrainValue", required=True)
	isHills = fields.Boolean(attribute="_isHills")
	feature = fields.String(attribute="_featureValue")
	resource = fields.String(attribute="_resourceValue")
	resourceQuantity = fields.Integer(attribute="_resourceQuantity")

	river = fields.Integer(attribute="_riverValue")
	riverName = fields.String(attribute="_riverName", allow_none=True)

	climateZone = fields.String(attribute="_climateZone")
	route = fields.String(attribute="_route")
	routePillaged = fields.Boolean(attribute="_routePillagedValue")
	improvement = fields.String(attribute="_improvementValue")
	improvementPillaged = fields.Boolean(attribute="_improvementPillagedValue")
	continentIdentifier = fields.String(allow_none=True)
	oceanIdentifier = fields.String(allow_none=True)
	# self.discovered = dict()  # fixme
	# self.visible = dict()  # fixme
	# self._cityValue = None  # fixme
	# self._districtValue = None  # fixme
	# self._wonderValue = WonderType.none  # fixme
	# self._owner = None  # fixme
	# self._workingCity = None  # fixme
	# self._buildProgressList = WeightedBuildList()  # fixme
	# area = fields.String(attribute="_area")  # fixme

	class Meta:
		model = Tile


class StartLocationSchema(Schema):
	location = fields.Nested(PointSchema)
	leader = fields.String(allow_none=True)
	cityState = fields.String(allow_none=True)
	isHuman = fields.Boolean()

	class Meta:
		model = StartLocation


class ContinentSchema(Schema):
	identifier = fields.String()
	name = fields.String()
	points = fields.List(fields.Nested(PointSchema))
	continentType = fields.String()

	class Meta:
		model = Continent


class OceanSchema(Schema):
	identifier = fields.String()
	name = fields.String()
	points = fields.List(fields.Nested(PointSchema))
	oceanType = fields.String()

	class Meta:
		model = Ocean


class MapModelSchema(Schema):
	width = fields.Int()
	height = fields.Int()
	tiles = fields.List(fields.List(fields.Nested(TileSchema)))

	# self._cities = []
	# self._units = []
	startLocations = fields.List(fields.Nested(StartLocationSchema))
	cityStateStartLocations = fields.List(fields.Nested(StartLocationSchema))

	continents = fields.List(fields.Nested(ContinentSchema))
	oceans = fields.List(fields.Nested(OceanSchema))
	areas = fields.List(fields.Nested(HexAreaSchema))

	class Meta:
		model = MapModel