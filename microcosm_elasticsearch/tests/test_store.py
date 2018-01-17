"""
Test Elasticsearch persistence.

"""
from datetime import timedelta
from hamcrest import (
    all_of,
    assert_that,
    calling,
    contains,
    equal_to,
    has_property,
    is_,
    none,
    raises,
)
from microcosm.api import create_object_graph
from mock import patch
from nose.plugins.attrib import attr


from microcosm_elasticsearch.assertions import assert_that_eventually, assert_that_not_eventually
from microcosm_elasticsearch.errors import (
    ElasticsearchConflictError,
    ElasticsearchNotFoundError,
)
from microcosm_elasticsearch.tests.fixtures import Person


class TestStore:

    def setup(self):
        self.graph = create_object_graph("example", testing=True)
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
            calling(self.store.count),
            is_(equal_to(2)),
            tries=5,
            sleep_seconds=0.5,
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
            calling(self.store.search),
            contains(
                all_of(
                    has_property("id", self.kevin.id),
                    has_property("first", "Kevin"),
                    has_property("last", "Durant"),
                ),
            ),
            tries=5,
            sleep_seconds=0.5,
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

        assert_that(
            self.store.search(offset=1, limit=1),
            contains(
                has_property("id", self.kevin.id),
            ),
        )
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
