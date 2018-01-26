"""
Test that the way we define a SearchIndex, Store and Model is consistent when overriding defaults

The fixtures below are the same as in fixtures.py, but we override defaults to set a different name for the
mapping type and doctype field

"""
from elasticsearch_dsl import analyzer, Completion, Keyword, Text
from hamcrest import (
    assert_that,
    all_of,
    contains_inanyorder,
    has_entries,
    has_key,
    has_length,
    has_property,
    instance_of,
)
from microcosm.api import create_object_graph
from microcosm.decorators import binding

from microcosm_elasticsearch.models import Model
from microcosm_elasticsearch.searching import SearchIndex
from microcosm_elasticsearch.store import Store


@binding("other_example_index")
def create_other_example_index(graph):
    return graph.elasticsearch_index_registry.register(version="v1")


class OtherPerson(Model):
    __doctype_field__ = "other_doctype"
    __doctype_name__ = "modified_person"

    class Meta:
        doc_type = "different_mapping"

    first = Text(required=True)
    middle = Text(required=False)
    last = Text(required=True)


class OtherPlayer(OtherPerson):
    __doctype_name__ = "modified_player"

    jersey_number = Keyword(required=False)

    class Meta:
        doc_type = "different_mapping"


class Car(Model):
    """
    This one does not inherit from `OtherPerson`, we"re testing
    that its mapping doesn"t erase the mapping from the other models

    """
    __doctype_field__ = "other_doctype"
    __doctype_name__ = "car"

    license_plate = Text(required=True)
    # Add complex field to test that mapping is properly merged
    _suggest_field = Completion(
        analyzer=analyzer("simple", tokenizer="standard", filter=["lowercase"]),
        contexts=[{"name": "license_plate", "type": "category", "path": "license_plate"}],
        preserve_separators=False,
        preserve_position_increments=False,
    )

    class Meta:
        doc_type = "different_mapping"


class OtherPersonSearchIndex(SearchIndex):
    @property
    def mapping_type_name(self):
        return "different_mapping"

    @property
    def doc_type_field(self):
        return "other_doctype"


@binding("other_search_index")
def create_other_search_index(graph):
    return OtherPersonSearchIndex(
        graph=graph,
        index=graph.other_example_index,
    )


@binding("other_person_store")
class OtherPersonStore(Store):
    def __init__(self, graph):
        super().__init__(graph, graph.other_example_index, OtherPerson, graph.other_search_index)


@binding("other_player_store")
class OtherPlayerStore(Store):
    def __init__(self, graph):
        super().__init__(graph, graph.other_example_index, OtherPlayer, graph.other_search_index)


@binding("car_store")
class CarStore(Store):
    def __init__(self, graph):
        super().__init__(graph, graph.other_example_index, Car, graph.other_search_index)


class TestMapping:
    def setup(self):
        self.graph = create_object_graph("example", testing=True)
        self.other_person_store = self.graph.other_person_store
        self.other_player_store = self.graph.other_player_store
        self.car_store = self.graph.car_store
        self.search_index = self.graph.other_search_index
        self.graph.elasticsearch_index_registry.createall(force=True)

        self.kevin = OtherPerson(
            first="Kevin",
            last="Durant",
        )
        self.steph = OtherPlayer(
            first="Steph",
            last="Curry",
        )

    def test_mapping(self):
        mapping = self.graph.other_example_index.get_mapping()

        assert_that(
            mapping["example_v1_test"]["mappings"],
            has_key("different_mapping"),
        )

        assert_that(
            mapping["example_v1_test"]["mappings"]["different_mapping"],
            has_entries({
                "properties": has_entries({
                    "created_at": {"type": "date"},
                    "first": {"type": "text"},
                    "id": {"type": "keyword"},
                    "jersey_number": {"type": "keyword"},
                    "license_plate": {"type": "text"},
                    "last": {"type": "text"},
                    "middle": {"type": "text"},
                    "other_doctype": {"type": "keyword"},
                    "updated_at": {"type": "date"},
                    "_suggest_field": {
                        "analyzer": "simple",
                        "contexts": [{
                            "name": "license_plate",
                            "path": "license_plate",
                            "type": "CATEGORY",
                        }],
                        "max_input_length": 50,
                        "preserve_position_increments": False,
                        "preserve_separators": False,
                        "type": "completion"
                    },
                }),
            })
        )

        with self.other_person_store.flushing():
            self.graph.other_person_store.create(self.kevin)
        with self.other_player_store.flushing():
            self.graph.other_player_store.create(self.steph)
        result = self.search_index.search()

        assert_that(
            result,
            has_length(2),
        )

        # Results are cast to the correct class according to their doctypes
        assert_that(
            result,
            contains_inanyorder(
                all_of(
                    has_property("other_doctype", "modified_person"),
                    instance_of(OtherPerson)
                ),
                all_of(
                    has_property("other_doctype", "modified_player"),
                    instance_of(OtherPlayer),
                ),
            )
        )
