"""
Factory that configures Elasticsearch client.

"""
from datetime import datetime, timedelta
from distutils.util import strtobool
from functools import partial
from os import environ

from boto3 import Session
from elasticsearch import Elasticsearch, RequestsHttpConnection
from microcosm.api import defaults
from requests_aws4auth import AWS4Auth

from microcosm_elasticsearch.serialization import JSONSerializerPython2


@defaults(
    aws_access_key_id=environ.get("AWS_ACCESS_KEY_ID"),
    aws_region=environ.get("AWS_DEFAULT_REGION", environ.get("AWS_REGION", "us-east-1")),
    aws_secret_access_key=environ.get("AWS_SECRET_ACCESS_KEY"),
    host="localhost",
    # NB: these are the defaults shipped with the ES docker distribution.
    # We want testing to "just work"; no sane production application should use these.
    username="elastic",
    password="changeme",
    use_aws4auth="false",
    use_aws_instance_metadata="false",
    use_python2_serializer="false",
)
def configure_elasticsearch_client(graph):
    """
    Configure Elasticsearch client using a constructed dictionary config.

    :returns: an Elasticsearch client instance of the configured name

    """
    config = dict()

    if strtobool(graph.config.elasticsearch_client.use_aws4auth):
        configure_elasticsearch_aws(config, graph)
    else:
        configure_elasticsearch(config, graph)

    if strtobool(graph.config.elasticsearch_client.use_python2_serializer):
        config.update(
            serializer=JSONSerializerPython2(),
        )

    return Elasticsearch(**config)


def configure_elasticsearch(config, graph):
    """
    Configure non-AWS elasticsearch

    """
    config.update(
        hosts=[
            graph.config.elasticsearch_client.host,
        ],
    )

    if graph.config.elasticsearch_client.username and graph.config.elasticsearch_client.password:
        config.update(
            http_auth=(
                graph.config.elasticsearch_client.username,
                graph.config.elasticsearch_client.password,
            ),
        )


def _next_aws_credentials(graph):
    # Use the metadata service to get proper temporary access keys for signing requests
    provider = Session()
    credentials = provider.get_credentials()
    return dict(
        access_id=credentials.access_key,
        secret_key=credentials.secret_key,
        region=graph.config.elasticsearch_client.aws_region,
        service="es",
        session_token=credentials.token,
        session_token_expiration=getattr(credentials, "_expiry_time", datetime.now() + timedelta(hours=1)),
        next_keys=partial(_next_aws_credentials, graph),
    )


def configure_elasticsearch_aws(config, graph, host=None):
    """
    Configure requests-aws4auth to sign requests when using AWS hosted Elasticsearch.

    :returns {dict} kwargs to pass the Elasticsearch client constructor

    """
    aws_region = graph.config.elasticsearch_client.aws_region

    if strtobool(graph.config.elasticsearch_client.use_aws_instance_metadata):
        credentials = _next_aws_credentials(graph)

        aws_access_key_id = credentials.get("access_id")
        aws_secret_access_key = credentials.get("secret_key")
        awsauth_kwargs = dict(
            session_token=credentials.get("session_token"),
            session_token_expiration=credentials.get("session_token_expiration"),
            next_keys=credentials.get("next_keys"),
        )
    else:
        aws_access_key_id = graph.config.elasticsearch_client.aws_access_key_id
        aws_secret_access_key = graph.config.elasticsearch_client.aws_secret_access_key
        awsauth_kwargs = {}

    awsauth = AWS4Auth(
        aws_access_key_id,
        aws_secret_access_key,
        aws_region,
        "es",
        **awsauth_kwargs
    )

    config.update(
        hosts=[{
            "host": host or graph.config.elasticsearch_client.host,
            "port": 443,
        }],
        connection_class=RequestsHttpConnection,
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
    )
