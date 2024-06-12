"""
Test polymorphic loading of subtypes.

"""
from math import pi

from elasticsearch_dsl import Keyword
from hamcrest import (
    assert_that,
    contains,
    has_length,
    instance_of,
    is_,
)
from microcosm.api import binding, create_object_graph

from microcosm_elasticsearch.models import Model
from microcosm_elasticsearch.searching import SearchIndex
from microcosm_elasticsearch.store import Store


@binding("shape_index")
def create_shape_index(graph):
    return graph.elasticsearch_index_registry.register(version="v1")


@binding("shape_search_index")
class ShapeSearchIndex(SearchIndex):

    def __init__(self, graph):
        super().__init__(graph, graph.shape_index)


class Shape(Model):

    area = Keyword()


class Circle(Shape):

    circumference = Keyword()

    @property
    def radius(self):
        return self.circumference / 2 / pi


class Square(Shape):

    perimeter = Keyword()

    @property
    def side_length(self):
        return self.perimeter / 4


@binding("shape_store")
class ShapeStore(Store):

    def __init__(self, graph):
        super().__init__(graph, graph.shape_index, Shape, graph.shape_search_index)


@binding("circle_store")
class CircleStore(Store):

    def __init__(self, graph):
        super().__init__(graph, graph.shape_index, Circle, graph.shape_search_index)


@binding("square_store")
class SquareStore(Store):

    def __init__(self, graph):
        super().__init__(graph, graph.shape_index, Square, graph.shape_search_index)


class TestPolymorphism:

    def setup_method(self):
        self.graph = create_object_graph("example", testing=True)
        self.circle_store = self.graph.circle_store
        self.shape_store = self.graph.shape_store
        self.square_store = self.graph.square_store
        self.graph.elasticsearch_index_registry.createall(force=True)

        self.circle = Circle(
            id="circle",
            circumfrance=20,
        )
        self.shape = Shape(
            id="shape",
            area=10,
        )
        self.square = Square(
            id="square",
            perimeter=30,
        )

    def test_shape(self):
        with self.shape_store.flushing():
            self.shape_store.create(self.shape)

        assert_that(
            self.shape_store.search(),
            contains(
                self.shape,
            ),
        )

    def test_circle(self):
        with self.circle_store.flushing():
            self.circle_store.create(self.circle)

        assert_that(
            self.circle_store.search(),
            contains(
                self.circle,
            ),
        )

    def test_square(self):
        with self.square_store.flushing():
            self.square_store.create(self.square)

        assert_that(
            self.square_store.search(),
            contains(
                self.square,
            ),
        )

    def test_circle_shape_square(self):
        with self.shape_store.flushing():
            self.shape_store.create(self.circle)
            self.shape_store.create(self.square)
            self.shape_store.create(self.shape)

        results = self.shape_store.search()
        assert_that(results, has_length(3))
        assert_that(
            results,
            contains(
                self.shape,
                self.square,
                self.circle,
            ),
        )
        assert_that(
            results,
            contains(
                is_(instance_of(Shape)),
                is_(instance_of(Square)),
                is_(instance_of(Circle)),
            ),
        )

        assert_that(
            self.shape_store.search(doc_types=["circle", "shape"]),
            contains(
                self.shape,
                self.circle,
            ),
        )
