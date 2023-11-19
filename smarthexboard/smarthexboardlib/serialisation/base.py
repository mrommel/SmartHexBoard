from marshmallow import Schema, fields


class PointSchema(Schema):
	x = fields.Integer()
	y = fields.Integer()


class HexAreaSchema(Schema):
	identifier = fields.String()
	points = fields.List(fields.Nested(PointSchema), attribute="_points")
	value = fields.Integer(attribute="_value", allow_none=True)
