"""
Test fixtures.

"""
from enum import Enum

from elasticsearch_dsl import Keyword, Q, Text
from microcosm.api import binding

from microcosm_elasticsearch.fields import EnumField
from microcosm_elasticsearch.models import Model
from microcosm_elasticsearch.searching import SearchIndex
from microcosm_elasticsearch.store import Store


class Planet(Enum):
    EARTH = "EARTH"
    MARS = "MARS"

    def __str__(self):
        return self.name


@binding("example_index")
def create_example_index(graph):
    return graph.elasticsearch_index_registry.register(version="v1")


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
        return super(PersonSearchIndex, self)._filter(query, **kwargs)


@binding("example_search_index")
def create_example_search_index(graph):
    return PersonSearchIndex(
        graph=graph,
        index=graph.example_index,
    )


@binding("person_store")
class PersonStore(Store):
    def __init__(self, graph):
        super(PersonStore, self).__init__(graph, graph.example_index, Person, graph.example_search_index)


@binding("player_store")
class PlayerStore(Store):
    def __init__(self, graph):
        super(PlayerStore, self).__init__(graph, graph.example_index, Player, graph.example_search_index)
