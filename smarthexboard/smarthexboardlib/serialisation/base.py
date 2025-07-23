from marshmallow import Schema, fields, post_load

from smarthexboard.smarthexboardlib.map.base import HexPoint


class PointSchema(Schema):
	x = fields.Integer()
	y = fields.Integer()

	@post_load
	def make_point(self, data, **kwargs):
		"""directly convert the deserialized data into a HexPoint object."""
		return HexPoint(data['x'], data['y'])


class HexAreaSchema(Schema):
	identifier = fields.String()
	points = fields.List(fields.Nested(PointSchema), attribute="_points")
	value = fields.Integer(attribute="_value", allow_none=True)


class WeightedListField(fields.Field):
	def __init__(self, key_type, *args, **kwargs):
		fields.Field.__init__(self, *args, **kwargs)
		self.key_type = key_type

	def _serialize(self, value, attr, obj, **kwargs):
		ret = {}
		for key, val in value.items():
			k = str(key)
			ret[k] = val
		return ret

	def _deserialize(self, value, attr, data, **kwargs):
		ret = {}
		for key, val in value.items():
			try:
				k = self.key_type.fromName(key)
				ret[k] = val
			except Exception as e:
				print(f'error when deserializing WeightedListField - cannot get name of key={key}')
				raise e

		return ret