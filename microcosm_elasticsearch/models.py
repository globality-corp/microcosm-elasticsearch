"""
Base classes for models

"""
from elasticsearch_dsl import Date, DocType, Keyword


class Model(DocType):
    """
    Every persistent entity should have a primary key id and created/updated timestamps.

    """
    id = Keyword(required=True)
    created_at = Date(required=True)
    updated_at = Date(required=True)

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
