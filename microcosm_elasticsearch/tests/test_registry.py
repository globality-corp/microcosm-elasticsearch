"""
Test registry management.

"""
from hamcrest import assert_that, equal_to, is_, calling
from microcosm.api import create_object_graph

from microcosm_elasticsearch.registry import IndexRegistry
from microcosm_elasticsearch.assertions import assert_that_eventually

def test_name_for():
    graph = create_object_graph("example")
    graph.lock()

    assert_that(IndexRegistry.name_for(graph), is_(equal_to("example")))
    assert_that(IndexRegistry.name_for(graph, name="foo"), is_(equal_to("foo")))
    assert_that(IndexRegistry.name_for(graph, version="v1"), is_(equal_to("example_v1")))
    assert_that(IndexRegistry.name_for(graph, name="foo", version="v2"), is_(equal_to("foo_v2")))


def test_name_for_testing():
    graph = create_object_graph("example", testing=True)
    graph.lock()

    assert_that(IndexRegistry.name_for(graph), is_(equal_to("example_test")))
    assert_that(IndexRegistry.name_for(graph, name="foo"), is_(equal_to("foo_test")))
    assert_that(IndexRegistry.name_for(graph, version="v1"), is_(equal_to("example_v1_test")))
    assert_that(IndexRegistry.name_for(graph, name="foo", version="v2"), is_(equal_to("foo_v2_test")))

def test_register():
    graph = create_object_graph("example", testing=True)
    index = graph.elasticsearch_index_registry.register()
    assert_that_eventually(
        calling(index.exists), 
        is_(equal_to(True)),
    )

def test_createall():
    graph = create_object_graph("example", testing=True)
    index = graph.elasticsearch_index_registry.register(name="foo", version="v1")
    graph.elasticsearch_index_registry.createall(force=True)
    assert_that(index.exists(), is_(equal_to(True)))
