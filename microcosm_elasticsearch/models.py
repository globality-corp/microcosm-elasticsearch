"""
Base classes for models

"""
from elasticsearch_dsl import Date, DocType, Keyword


class Model(DocType):
    """
    Every persistent entity should have a primary key id and created/updated timestamps.

    """
    __doc_type_field__ = "doctype"
    # By default the doctype will be set to the class name
    # To change this declare:
    # __doc_type_name__ = "<other name>"

    doctype = Keyword(required=True)

    id = Keyword(required=True)
    created_at = Date(required=True)
    updated_at = Date(required=True)

    def __init__(self, meta=None, **kwargs):
        cls = self.__class__
        kwargs["doctype"] = getattr(cls, "__doc_type_name__", None) or cls.__name__.lower()
        return super().__init__(meta=meta, **kwargs)

    def _members(self):
        return {
            key: value
            for key, value in self.to_dict().items()
            # NB: exclude non-persistent fields
            if key not in ("index", "doc_type")
        }

    def __eq__(self, other):
        return type(other) is type(self) and self._members() == other._members()

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return id(self) if self.id is None else hash(self.id)
