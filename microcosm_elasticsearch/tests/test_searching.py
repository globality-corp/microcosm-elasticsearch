"""
Test Elasticsearch searching.

"""
from hamcrest import (
    assert_that,
    contains,
    equal_to,
    has_properties,
    is_,
)
from microcosm.api import create_object_graph

from microcosm_elasticsearch.tests.fixtures import Person, Player, PersonSearchIndex


class TestIndexSearch:

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
                has_properties(
                    id=self.kevin.id,
                    first="Kevin",
                    last="Durant",
                ),
            ),
        )

    def test_count_single_type(self):
        with self.person_store.flushing():
            self.person_store.create(self.kevin)

        with self.player_store.flushing():
            self.player_store.create(self.steph)

        index = PersonSearchIndex(self.graph, self.graph.example_index, Player)

        assert_that(
            index.count(doc_type="player"),
            is_(equal_to(1)),
        )

    def test_search_single_type(self):
        with self.person_store.flushing():
            self.person_store.create(self.kevin)

        with self.player_store.flushing():
            self.player_store.create(self.steph)

        index = PersonSearchIndex(self.graph, self.graph.example_index, Player)

        assert_that(
            index.search(doc_type="player"),
            contains(
                has_properties(
                    id=self.steph.id,
                ),
            ),
        )

    def test_search_with_explain(self):
        """
        hit.meta.explanation should exist when searched with explain=True

        """
        with self.person_store.flushing():
            self.person_store.create(self.kevin)

        assert_that(
            self.search_index.search(explain=True),
            contains(
                has_properties(
                    meta=has_properties(
                        explanation=has_properties(
                            value=1.0,
                        ),
                    ),
                ),
            ),
        )
