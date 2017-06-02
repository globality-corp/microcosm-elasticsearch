"""
Test fixtures.

"""
from elasticsearch_dsl import Q, Text
from microcosm.api import binding

from microcosm_elasticsearch.indexing import make_index
from microcosm_elasticsearch.models import Model
from microcosm_elasticsearch.store import Store


@binding("example_index")
def create_example_index(graph):
    return make_index(graph)


class Person(Model):
    first = Text(required=True)
    middle = Text(required=False)
    last = Text(required=True)


@binding("person_store")
class PersonStore(Store):
    def __init__(self, graph):
        super(PersonStore, self).__init__(graph, graph.example_index, Person)

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
        return super(PersonStore, self)._filter(query, **kwargs)
