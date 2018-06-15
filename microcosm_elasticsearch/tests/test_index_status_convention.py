"""
Index status convention tests.

"""

from hamcrest import (
    assert_that,
    equal_to,
    is_,
)

from microcosm.api import create_object_graph


def test_index_status():
    """
    Default index status check returns OK.

    """
    graph = create_object_graph(name="test", testing=True)
    graph.use("index_status_convention")
    graph.elasticsearch_index_registry.createall(force=True)

    client = graph.flask.test_client()

    response = client.get("/api/index_status")
    assert_that(response.status_code, is_(equal_to(200)))
