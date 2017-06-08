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

from microcosm_elasticsearch.tests.fixtures import Person, Player, PersonSearchIndex


class TestIndexSearch(object):

    def setup(self):
        self.graph = create_object_graph("example", testing=True)
        self.search_index = self.graph.example_search_index
        self.person_store = self.graph.person_store
        self.player_store = self.graph.player_store
        self.graph.elasticsearch_index_registry.createall(force=True)

        self.kevin = Person(
            first="Kevin",
            last="Durant",
        )
        self.steph = Player(
            first="Steph",
            last="Curry",
            jersey_number="30",
        )

    def test_count(self):
        with self.person_store.flushing():
            self.person_store.create(self.kevin)

        with self.player_store.flushing():
            self.player_store.create(self.steph)

        assert_that(self.search_index.count(), is_(equal_to(2)))

    def test_search(self):
        with self.person_store.flushing():
            self.person_store.create(self.kevin)

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

    def test_count_single_type(self):
        with self.person_store.flushing():
            self.person_store.create(self.kevin)

        with self.player_store.flushing():
            self.player_store.create(self.steph)

        index = PersonSearchIndex.for_only(self.graph, self.graph.example_index, Player)

        assert_that(
            index.count(),
            is_(equal_to(1)),
        )

    def test_search_single_type(self):
        with self.person_store.flushing():
            self.person_store.create(self.kevin)

        with self.player_store.flushing():
            self.player_store.create(self.steph)

        index = PersonSearchIndex.for_only(self.graph, self.graph.example_index, Player)

        assert_that(
            index.search(),
            contains(
                has_property("id", self.steph.id),
            ),
        )
