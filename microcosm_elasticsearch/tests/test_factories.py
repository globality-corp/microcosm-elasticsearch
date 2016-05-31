from os import environ


from hamcrest import (
    assert_that,
    calling,
    equal_to,
    is_,
    raises,
)

from microcosm.api import create_object_graph


def test_configure_elasticsearch_client_with_defaults():
    """
    Default configuration works and returns client.

    """
    graph = create_object_graph(name="test", testing=True)

    # assert_that(graph.logger, is_(equal_to(getLogger("test"))))
    # assert_that(graph.logger.getEffectiveLevel(), is_(equal_to(INFO)))


def test_configure_elasticsearch_client_with_aws4auth():
    """
    Support for AWS4Auth works when provided with valid credentials.

    """
    def loader(metadata):
        return dict(
            elasticsearch_client=dict(
                use_aws4auth=True,
            )
        )

    graph = create_object_graph(name="test", testing=True, loader=loader)

    # assert_that(graph.logger.getEffectiveLevel(), is_(equal_to(DEBUG)))


def test_configure_elasticsearch_client_with_aws4auth_requires_credentials():
    """
    Enabling AWS4auth request signing requires AWS credentials.

    """
    def loader(metadata):
        return dict(
            elasticsearch_client=dict(
                use_aws4auth=True,
            )
        )

    graph = create_object_graph(name="test", loader=loader)
    assert_that(calling(graph.use).with_args("elasticsearch_client"), raises(AttributeError))


def test_configure_elasticsearch_client_with_python_2_serializer_works():
    """
    Enabling Python 2.x serializer works.

    """
    def loader(metadata):
        return dict(
            elasticsearch_client=dict(
                use_python2_serializer=True,
            )
        )

    graph = create_object_graph(name="test", loader=loader)
    assert_that(type(graph.elasticsearch_client.serializer), object)
