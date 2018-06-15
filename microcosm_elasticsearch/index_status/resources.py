"""
Index Status resources.

"""
from marshmallow import fields, Schema


class FieldSchema(Schema):
    name = fields.String()
    data_type = fields.String()


class DocsSchema(Schema):
    count = fields.Int()
    deleted = fields.Int()


class IndexingSchema(Schema):
    index_current = fields.Int()
    index_failed = fields.Int()
    index_total = fields.Int()
    delete_current = fields.Int()
    delete_total = fields.Int()


class StatsSchema(Schema):
    docs = fields.Nested(DocsSchema)
    indexing = fields.Nested(IndexingSchema)


class IndexStatusSchema(Schema):
    aliases = fields.List(fields.String)
    mapping = fields.List(
        fields.Nested(FieldSchema)
    )
    name = fields.String()
    stats = fields.Nested(StatsSchema)
