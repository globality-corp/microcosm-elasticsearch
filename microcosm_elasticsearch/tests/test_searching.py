"""
Test Elasticsearch searching.

"""
from hamcrest import (
    all_of,
    assert_that,
    contains,
    equal_to,
    has_property,
    is_,
)
from microcosm.api import create_object_graph


from microcosm_elasticsearch.tests.fixtures import Person


class TestIndexSearch(object):

    def setup(self):
        self.graph = create_object_graph("example", testing=True)
        self.search_index = self.graph.example_search_index
        self.store = self.graph.person_store
        self.graph.elasticsearch_index_registry.createall(force=True)

        self.kevin = Person(
            first="Kevin",
            last="Durant",
        )
        self.steph = Person(
            first="Steph",
            last="Curry",
        )

    def test_count(self):
        with self.store.flushing():
            self.store.create(self.kevin)
            self.store.create(self.steph)
        assert_that(self.search_index.count(), is_(equal_to(2)))

    def test_search(self):
        with self.store.flushing():
            self.store.create(self.kevin)

        assert_that(
            self.search_index.search(),
            contains(
                all_of(
                    has_property("id", self.kevin.id),
                    has_property("first", "Kevin"),
                    has_property("last", "Durant"),
                ),
            ),
        )
