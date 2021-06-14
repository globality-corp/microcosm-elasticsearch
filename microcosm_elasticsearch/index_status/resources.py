"""
Index Status resources.

"""
from marshmallow import Schema, fields


class IndexStatusSchema(Schema):
    name = fields.String()
    data = fields.Raw()
    stats = fields.Raw()
