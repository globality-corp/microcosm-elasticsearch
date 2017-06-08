"""
Test fixtures.

"""
from elasticsearch_dsl import Keyword, Q, Text
from microcosm.api import binding

from microcosm_elasticsearch.models import Model
from microcosm_elasticsearch.searching import SearchIndex
from microcosm_elasticsearch.store import Store


@binding("example_index")
def create_example_index(graph):
    return graph.elasticsearch_index_registry.register(version="v1")


class Person(Model):
    first = Text(required=True)
    middle = Text(required=False)
    last = Text(required=True)


class Employee(Person):
    employee_id = Keyword(required=False)


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
        model_class=Person,
    )


@binding("person_store")
class PersonStore(Store):
    def __init__(self, graph):
        super(PersonStore, self).__init__(graph, graph.example_index, Person, PersonSearchIndex)


@binding("employee_store")
class EmployeeStore(Store):
    def __init__(self, graph):
        super(EmployeeStore, self).__init__(graph, graph.example_index, Employee, PersonSearchIndex)
