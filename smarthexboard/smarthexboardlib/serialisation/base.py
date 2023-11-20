from marshmallow import Schema, fields


class PointSchema(Schema):
	x = fields.Integer()
	y = fields.Integer()


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
			k = self.key_type.fromName(key)
			ret[k] = val
		return ret