"""
Base classes for models

"""
from elasticsearch_dsl import Date, DocType, Keyword
from elasticsearch_dsl.document import DocTypeOptions, DocTypeMeta


class ModelMeta(DocTypeMeta):
    def __new__(cls, name, bases, attrs):
        attrs["_doc_type"] = ModelOptions(name, bases, attrs)
        return super(DocTypeMeta, cls).__new__(cls, name, bases, attrs)


class ModelOptions(DocTypeOptions):
    def __init__(self, name, bases, attrs):
        if "__doctype_field__" in attrs:
            # Dynamically set the field for polymorphic doctype
            doctype_field_name = attrs["__doctype_field__"]
            attrs[doctype_field_name] = Keyword(required=True)
        super().__init__(name, bases, attrs)


class Model(DocType, metaclass=ModelMeta):
    """
    Base for all models. Any model instance has a primary key and created/updated timestamps,
    as well as a field indicating the doctype (set via the metaclass, whose value defautls to the lowercased
    model name).

    """
    # By default when creating a document from a `Model` subclass instance
    # Its doctype will be set to the lowercased subclass name
    # To override this declare:
    # __doctype_name__ = "<other name>"

    # The following will set up a field to hold the document's polymorphic doctype
    # By default the field name is "doctype", override in child classes to change this
    # Note that if you change it here you should also override the SearchIndex's `mapping_type_name` property
    __doctype_field__ = "doctype"

    # Every persistent entity should have a primary key id and created/updated timestamps.
    id = Keyword(required=True)
    created_at = Date(required=True)
    updated_at = Date(required=True)

    def __init__(self, meta=None, **kwargs):
        cls = self.__class__
        kwargs[cls.__doctype_field__] = cls.get_model_doctype()
        return super().__init__(meta=meta, **kwargs)

    @classmethod
    def get_model_doctype(cls):
        return getattr(cls, "__doctype_name__", None) or cls.__name__.lower()

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
