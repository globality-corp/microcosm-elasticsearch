"""
Factory that configures Elasticsearch client.

"""
from os import environ

import boto3
from elasticsearch import Elasticsearch, RequestsHttpConnection
from microcosm.api import defaults
from requests_aws4auth import AWS4Auth

from microcosm_elasticsearch.serialization import JSONSerializerPython2


@defaults(
    aws_access_key_id=environ.get('AWS_ACCESS_KEY_ID'),
    aws_region=environ.get('AWS_REGION'),
    aws_secret_access_key=environ.get('AWS_SECRET_ACCESS_KEY'),
    host='localhost:9200',
    use_aws4auth=False,
    use_aws_instance_metadata=False,
    use_python2_serializer=True,
)
def configure_elasticsearch_client(graph):
    """
    Configure Elasticsearch client using a constructed dictionary config.

    :returns: an Elasticsearch client instance of the configured name

    """
    if graph.config.elasticsearch_client.use_aws4auth:
        kwargs = _configure_aws4auth(graph)
    else:
        kwargs = dict(
            hosts=[graph.config.elasticsearch_client.host]
        )

    if graph.config.elasticsearch_client.use_python2_serializer:
        kwargs.update(dict(
            serializer=JSONSerializerPython2(),
        ))

    return Elasticsearch(**kwargs)


def _configure_aws4auth(graph):
    """
    Configure requests-aws4auth to sign requests when using AWS hosted Elasticsearch.

    :returns {dict} kwargs to pass the Elasticsearch client constructor

    """
    aws_region = graph.config.elasticsearch_client.aws_region
    if graph.config.elasticsearch_client.use_aws_instance_metadata:
        # Use the metadata service to get proper temporary access keys for signing requests
        provider = boto3.Session()
        credentials = provider.get_credentials()
        aws_access_key_id = credentials.access_key
        aws_secret_access_key = credentials.secret_key
        awsauth_kwargs = dict(
            session_token=credentials.token,
        )
    else:
        aws_access_key_id = graph.config.elasticsearch_client.aws_access_key_id
        aws_secret_access_key = graph.config.elasticsearch_client.aws_secret_access_key
        awsauth_kwargs = {}

    awsauth = AWS4Auth(
        aws_access_key_id,
        aws_secret_access_key,
        aws_region,
        'es',
        **awsauth_kwargs
    )

    return dict(
        hosts=[{'host': graph.config.elasticsearch_client.host, 'port': 443}],
        connection_class=RequestsHttpConnection,
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
    )
