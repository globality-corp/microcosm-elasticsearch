"""
Test Elasticsearch persistence.

"""
from datetime import timedelta
from unittest.mock import patch

from hamcrest import (
    all_of,
    assert_that,
    calling,
    contains,
    equal_to,
    has_entry,
    has_key,
    has_property,
    is_,
    none,
    raises,
)
from microcosm.api import create_object_graph
from nose.plugins.attrib import attr

from microcosm_elasticsearch.assertions import assert_that_eventually, assert_that_not_eventually
from microcosm_elasticsearch.errors import ElasticsearchConflictError, ElasticsearchNotFoundError
from microcosm_elasticsearch.tests.fixtures import Person, Planet, SelectorAttribute


class TestStore:

    def setup(self):
        self.graph = create_object_graph("example", testing=True)
        self.store = self.graph.person_store
        self.overloaded_store = self.graph.person_overloaded_store

        self.graph.elasticsearch_index_registry.createall(force=True)

        self.kevin = Person(
            first="Kevin",
            last="Durant",
            origin_planet=Planet.EARTH,
        )
        self.steph = Person(
            first="Steph",
            last="Curry",
            origin_planet=Planet.MARS,
        )

        self.person_in_one = Person(
            first="One",
            last="Person",
            origin_planet=Planet.MARS,
        )
        self.person_in_two = Person(
            first="Two",
            last="Person",
            origin_planet=Planet.MARS,
        )

    def test_retrieve_not_found(self):
        assert_that(
            calling(self.store.retrieve).with_args(self.store.new_object_id()),
            raises(ElasticsearchNotFoundError),
        )

    def test_create(self):
        self.store.create(self.kevin)
        assert_that(
            self.store.retrieve(self.kevin.id),
            all_of(
                has_property("id", self.kevin.id),
                has_property("first", "Kevin"),
                has_property("middle", none()),
                has_property("last", "Durant"),
                has_property("origin_planet", Planet.EARTH),
            ),
        )

    def test_create_duplicate(self):
        self.store.create(self.kevin)
        assert_that(
            calling(self.store.create).with_args(self.kevin),
            raises(ElasticsearchConflictError),
        )

    def test_count(self):
        with self.store.flushing():
            self.store.create(self.kevin)
            self.store.create(self.steph)
        assert_that(self.store.count(), is_(equal_to(2)))

    @attr("slow")
    def test_count_slow(self):
        self.store.create(self.kevin)
        self.store.create(self.steph)
        assert_that_eventually(
            self.store.count,
            is_(equal_to(2)),
            tries=5,
            sleep_seconds=1.0,
        )

    def test_delete_not_found(self):
        assert_that(
            calling(self.store.delete).with_args(self.store.new_object_id()),
            raises(ElasticsearchNotFoundError),
        )

    def test_delete(self):
        self.store.create(self.kevin)
        assert_that(self.store.delete(self.kevin.id), is_(equal_to(True)))
        assert_that(
            calling(self.store.retrieve).with_args(self.kevin.id),
            raises(ElasticsearchNotFoundError),
        )

    def test_search(self):
        with self.store.flushing():
            self.store.create(self.kevin)

        assert_that(
            self.store.search(),
            contains(
                all_of(
                    has_property("id", self.kevin.id),
                    has_property("first", "Kevin"),
                    has_property("last", "Durant"),
                ),
            ),
        )

    def test_search_with_count(self):
        with self.store.flushing():
            self.store.create(self.kevin)

        items, count = self.store.search_with_count()
        assert_that(
            items,
            contains(
                all_of(
                    has_property("id", self.kevin.id),
                    has_property("first", "Kevin"),
                    has_property("last", "Durant"),
                ),
            ),
        )
        assert_that(count, is_(equal_to(1)))

    @attr("slow")
    def test_search_slow(self):
        self.store.create(self.kevin)
        assert_that_eventually(
            self.store.search,
            contains(
                all_of(
                    has_property("id", self.kevin.id),
                    has_property("first", "Kevin"),
                    has_property("last", "Durant"),
                ),
            ),
            tries=5,
            sleep_seconds=1.0,
        )

    def test_search_order_reverse_chronological(self):
        with self.store.flushing():
            self.store.create(self.kevin)
            with patch.object(self.store, "new_timestamp") as mocked:
                # ensure we have >= 1s created at delta
                mocked.return_value = self.kevin.created_at + timedelta(seconds=1).seconds * 1000
                self.store.create(self.steph)

        assert_that(
            self.store.search(),
            contains(
                has_property("id", self.steph.id),
                has_property("id", self.kevin.id),
            ),
        )

    def test_search_paging(self):
        with self.store.flushing():
            self.store.create(self.kevin)
            with patch.object(self.store, "new_timestamp") as mocked:
                # ensure we have >= 1s created at delta
                mocked.return_value = self.kevin.created_at + timedelta(seconds=1).seconds * 1000
                self.store.create(self.steph)

        result = self.store.search(offset=1, limit=1)
        assert_that(result, contains(has_property("id", self.kevin.id)))

        assert_that(
            self.store.search(offset=0, limit=1),
            contains(
                has_property("id", self.steph.id),
            ),
        )

    def test_search_filter(self):
        with self.store.flushing():
            self.store.create(self.kevin)

        assert_that(
            self.store.search(q=self.kevin.first),
            contains(
                all_of(
                    has_property("id", self.kevin.id),
                    has_property("first", "Kevin"),
                    has_property("last", "Durant"),
                ),
            ),
        )

    def test_search_filter_out(self):
        with self.store.flushing():
            self.store.create(self.kevin)

        assert_that(
            self.store.search(q=self.steph.first),
            contains(),
        )

    @attr("slow")
    def test_search_filter_out_slow(self):
        self.store.create(self.kevin)
        assert_that_not_eventually(
            calling(self.store.search).with_args(q=self.steph.first),
            contains(
                all_of(
                    has_property("id", self.kevin.id),
                    has_property("first", "Kevin"),
                    has_property("last", "Durant"),
                ),
            ),
        )

    def test_update_not_found(self):
        assert_that(
            calling(self.store.update).with_args(self.store.new_object_id(), self.kevin),
            raises(ElasticsearchNotFoundError),
        )

    def test_update(self):
        self.store.create(self.kevin)
        self.kevin.middle = "MVP"
        self.store.update(self.kevin.id, self.kevin)
        assert_that(
            self.store.retrieve(self.kevin.id),
            all_of(
                has_property("id", self.kevin.id),
                has_property("first", "Kevin"),
                has_property("middle", "MVP"),
                has_property("last", "Durant"),
            ),
        )

    def test_replace_not_found(self):
        self.kevin.middle = "MVP"
        self.store.replace(self.kevin.id, self.kevin)
        assert_that(
            self.store.retrieve(self.kevin.id),
            all_of(
                has_property("id", self.kevin.id),
                has_property("first", "Kevin"),
                has_property("middle", "MVP"),
                has_property("last", "Durant"),
            ),
        )

    def test_replace(self):
        self.store.create(self.kevin)
        self.kevin.middle = "MVP"
        self.store.replace(self.kevin.id, self.kevin)
        assert_that(
            self.store.retrieve(self.kevin.id),
            all_of(
                has_property("id", self.kevin.id),
                has_property("first", "Kevin"),
                has_property("middle", "MVP"),
                has_property("last", "Durant"),
            ),
        )

    def test_bulk(self):
        self.store.bulk(
            actions=[
                ("index", self.kevin)
            ],
            batch_size=1,
        )
        assert_that(
            self.store.retrieve(self.kevin.id),
            all_of(
                has_property("id", self.kevin.id),
                has_property("first", "Kevin"),
                has_property("middle", none()),
                has_property("last", "Durant"),
            ),
        )

    def test_bulk_with_report(self):
        results = self.store.bulk(
            actions=[
                ("index", self.kevin),
                ("delete", self.steph),
            ],
            batch_size=2,
        )
        assert_that(
            self.store.retrieve(self.kevin.id),
            all_of(
                has_property("id", self.kevin.id),
                has_property("first", "Kevin"),
                has_property("middle", none()),
                has_property("last", "Durant"),
            ),
        )
        result = results[0]
        # Updated items
        assert_that(result[0], is_(equal_to(1)))
        # Report on failed to delete items
        assert_that(result[1], contains(
            has_key('delete'),
        ))
        assert_that(result[1][0]['delete'], has_entry('result', 'not_found'))

    def test_overloaded_store(self):
        with self.overloaded_store.flushing(selector_attribute=SelectorAttribute.ONE):
            self.overloaded_store.create(
                self.person_in_one,
                selector_attribute=SelectorAttribute.ONE
            )

        with self.overloaded_store.flushing(selector_attribute=SelectorAttribute.TWO):
            self.overloaded_store.create(
                self.person_in_two,
                selector_attribute=SelectorAttribute.TWO
            )

        result, count = self.overloaded_store.search_with_count(selector_attribute=SelectorAttribute.ONE)
        assert_that(result[0], has_property("id", self.person_in_one.id))
        assert_that(count, is_(equal_to(1)))

        result, count = self.overloaded_store.search_with_count(selector_attribute=SelectorAttribute.TWO)
        assert_that(result[0], has_property("id", self.person_in_two.id))
        assert_that(count, is_(equal_to(1)))
