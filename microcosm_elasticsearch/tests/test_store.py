"""
Test Elasticsearch persistence.

"""
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

from microcosm_elasticsearch.assertions import assert_that_eventually, assert_that_not_eventually
from microcosm_elasticsearch.errors import (
    ElasticsearchConflictError,
    ElasticsearchNotFoundError,
)
from microcosm_elasticsearch.indexing import createall
from microcosm_elasticsearch.tests.fixtures import Person


class TestStore(object):

    def setup(self):
        self.graph = create_object_graph("example", testing=True)
        self.store = self.graph.person_store
        createall(self.graph.example_index, force=True)

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
        self.store.create(self.kevin)
        self.store.create(self.steph)
        assert_that_eventually(
            calling(self.store.count),
            is_(equal_to(2)),
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
        )

    def test_search_order_reverse_chronological(self):
        self.store.create(self.kevin)
        self.store.create(self.steph)
        assert_that_eventually(
            calling(self.store.search),
            contains(
                has_property("id", self.steph.id),
                has_property("id", self.kevin.id),
            ),
        )

    def test_search_paging(self):
        self.store.create(self.kevin)
        self.store.create(self.steph)
        assert_that_eventually(
            calling(self.store.search).with_args(offset=1, limit=1),
            contains(
                has_property("id", self.kevin.id),
            ),
        )
        assert_that_eventually(
            calling(self.store.search).with_args(offset=0, limit=1),
            contains(
                has_property("id", self.steph.id),
            ),
        )

    def test_search_filter(self):
        self.store.create(self.kevin)
        assert_that_eventually(
            calling(self.store.search).with_args(q=self.kevin.first),
            contains(
                all_of(
                    has_property("id", self.kevin.id),
                    has_property("first", "Kevin"),
                    has_property("last", "Durant"),
                ),
            ),
        )

    def test_search_filter_out(self):
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