from elasticsearch import Elasticsearch
from hamcrest import assert_that, instance_of, is_
from microcosm.api import create_object_graph


def test_configure_elasticsearch_client_with_defaults():
    """
    Default configuration works and returns client.

    """
    graph = create_object_graph(name="test", testing=True)
    assert_that(graph.elasticsearch_client, is_(instance_of(Elasticsearch)))


def test_configure_elasticsearch_client_with_aws4auth():
    """
    Support for AWS4Auth works when provided with valid credentials.

    """
    def loader(metadata):
        return dict(
            elasticsearch_client=dict(
                aws_access_key_id="aws-access-key-id",
                aws_secret_access_key="aws-secret-access-key",
                aws_region="aws-region-1",
                use_aws4auth="True",
            )
        )

    graph = create_object_graph(name="test", testing=True, loader=loader)

    assert_that(graph.elasticsearch_client, is_(instance_of(Elasticsearch)))


def test_configure_elasticsearch_client_with_python_2_serializer_works():
    """
    Enabling Python 2.x serializer works.

    """
    def loader(metadata):
        return dict(
            elasticsearch_client=dict(
                use_python2_serializer="True",
            )
        )

    graph = create_object_graph(name="test", loader=loader)
    assert_that(graph.elasticsearch_client, is_(instance_of(Elasticsearch)))
