"""
Index Status resources.

"""
from marshmallow import fields, Schema


class IndexStatusSchema(Schema):
    name = fields.String()
    data = fields.Raw()
    stats = fields.Raw()
