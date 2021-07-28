"""
Test fixtures.

"""
from enum import Enum, auto

from elasticsearch_dsl import Keyword, Q, Text
from microcosm.api import binding

from microcosm_elasticsearch.fields import EnumField
from microcosm_elasticsearch.mapping import create_mapping
from microcosm_elasticsearch.models import Model
from microcosm_elasticsearch.searching import SearchIndex
from microcosm_elasticsearch.store import Store


class SelectorAttribute(Enum):
    ONE = auto()
    TWO = auto()


class Planet(Enum):
    EARTH = "EARTH"
    MARS = "MARS"

    def __str__(self):
        return self.name


@binding("example_index")
def create_example_index(graph):
    return graph.elasticsearch_index_registry.register(
        version="v1",
        mapping=create_mapping(Person),
    )


@binding("first_attribute_index")
def create_first_index(graph):
    return graph.elasticsearch_index_registry.register(
        version="v1",
        name="first-attribute",
        mapping=create_mapping(Person),
    )


class Person(Model):
    first = Text(required=True)
    middle = Text(required=False)
    last = Text(required=True)

    origin_planet = EnumField(Planet)


class Player(Person):
    jersey_number = Keyword(required=False)


class PersonSearchIndex(SearchIndex):
    def _filter(self, query, q=None, **kwargs):
        if q is not None:
            query = query.query(
                Q(
                    "multi_match",
                    query=q,
                    fields=[
                        "first",
                        "last",
                    ],
                )
            )
        return super()._filter(query, **kwargs)


@binding("example_search_index")
def create_example_search_index(graph):
    return PersonSearchIndex(
        graph=graph,
        index=graph.example_index,
    )


@binding("person_store")
class PersonStore(Store):
    def __init__(self, graph):
        super().__init__(graph, graph.example_index, Person, graph.example_search_index)


@binding("player_store")
class PlayerStore(Store):
    def __init__(self, graph):
        super().__init__(graph, graph.example_index, Player, graph.example_search_index)


@binding("first_attribute_search_index")
def create_first_attribute_search_index(graph):
    return PersonSearchIndex(
        graph=graph,
        index=graph.first_attribute_index
    )


@binding("person_overloaded_store")
class PersonOverloadedStore(Store):
    def __init__(self, graph):
        super().__init__(
            graph, graph.first_attribute_index, Person, graph.first_attribute_search_index)
        self.first_attribute_index = graph.first_attribute_index
        self.first_attribute_search_index = graph.first_attribute_search_index

        self.second_attribute_index = graph.elasticsearch_index_registry.register(
            version="v1",
            name="second-attribute",
            mapping=create_mapping(Person),
        )
        self.second_attribute_search_index = SearchIndex(
            graph=graph,
            index=self.second_attribute_index
        )

    def get_index(
            self,
            selector_attribute: SelectorAttribute = SelectorAttribute.ONE,
            **kwargs
    ):
        if selector_attribute == SelectorAttribute.ONE:
            return self.first_attribute_index
        elif selector_attribute == SelectorAttribute.TWO:
            return self.second_attribute_index
        else:
            raise Exception("Index not found")

    def get_search_index(
            self,
            selector_attribute: SelectorAttribute = SelectorAttribute.ONE,
            **kwargs
    ):
        if selector_attribute == SelectorAttribute.ONE:
            return self.first_attribute_search_index
        elif selector_attribute == SelectorAttribute.TWO:
            return self.second_attribute_search_index
        else:
            raise Exception("Index not found")
