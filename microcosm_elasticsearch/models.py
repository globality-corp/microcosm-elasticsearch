"""
Base classes for models

"""
from elasticsearch_dsl import Date, Document, Keyword


class Model(Document):
    """
    Base for all models. Any model instance has a primary key and created/updated timestamps,
    as well as a field indicating the doctype.

    See README#polymorphic-models for more details

    """
    # Every persistent entity should have a primary key id and created/updated timestamps.
    id = Keyword(required=True)
    created_at = Date(required=True)
    updated_at = Date(required=True)

    # In ES6+ indices have a single mapping type
    # To allow for polymorphic documents, we define a field holding the document type
    doctype = Keyword(required=True)

    def __init__(self, meta=None, **kwargs):
        cls = self.__class__
        kwargs["doctype"] = cls.get_model_doctype()
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

    @property
    def _id(self):
        return self.meta.id

    @_id.setter
    def _id(self, value):
        self.meta.id = value

    @property
    def _index(self):
        return self.meta.index

    @_index.setter
    def _index(self, value):
        self.meta.index = value

    @property
    def _score(self):
        return self.meta.score

    @_score.setter
    def _score(self, value):
        self.meta.score = value

    @property
    def _version(self):
        return self.meta.version

    @_version.setter
    def _version(self, value):
        self.meta.version = value
