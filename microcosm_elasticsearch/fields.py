from enum import Enum
from elasticsearch_dsl import Keyword
from elasticsearch_dsl.exceptions import ValidationException


class EnumField(Keyword):
    # Force serialization
    _coerce = True
    name = "keyword"

    def __init__(self, enum_class, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Leading underscore prevents attribute from being added to document in ElasticSearch
        if not issubclass(enum_class, Enum):
            raise TypeError("The class passed into an EnumField should a subclass of Enum")
        self._enum_class = enum_class

    def _serialize(self, data):
        return str(data)

    def _deserialize(self, data):
        return self._enum_class[data]

    def clean(self, data):
        """
        Field validation
        Handle both cases where the data comes in as a string or enum

        """
        if isinstance(data, str):
            return super().clean(data)
        elif isinstance(data, Enum):
            if data not in self._enum_class:
                raise ValidationException(f"Value should be a member of {self.enum_class}")
            return data
        else:
            raise ValidationException(f"Value of type {data.__class__} is not acceptable for an EnumField")
