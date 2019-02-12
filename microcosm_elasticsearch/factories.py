"""
Factory that configures Elasticsearch client.

"""
from functools import partial
from os import environ
from urllib.parse import parse_qs, urlencode, urlparse

from boto3 import Session
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from elasticsearch import Elasticsearch, RequestsHttpConnection
from microcosm.api import defaults
from microcosm.config.types import boolean
from microcosm.config.validation import typed


def make_url_safe(raw_url):
    """
    Make sure all query parameters are URL encoded

    Some servers can deal with some parameters not being
    strictly urlencoded, but some canonization inside
    the signing logic means that we have to pre-urlencode
    all query parameters.
    """
    url = urlparse(raw_url)
    path = url.path or "/"
    if url.query:
        querystring = "?" + urlencode(parse_qs(url.query,
                                               keep_blank_values=True),
                                      doseq=True)
    else:
        querystring = ""
    return (url.scheme +
            "://" +
            url.netloc +
            path +
            querystring)


def awsv4sign(r, *, session, region):
    request = AWSRequest(method=r.method.upper(),
                         url=make_url_safe(r.url),
                         data=r.body)
    credentials = session.get_credentials()
    SigV4Auth(credentials, 'es', region).add_auth(request)
    r.headers.update(dict(request.headers.items()))
    return r


@defaults(
    aws_region=environ.get("AWS_DEFAULT_REGION", environ.get("AWS_REGION", "us-east-1")),
    host="localhost",
    # NB: these are the defaults shipped with the ES docker distribution.
    # We want testing to "just work"; no sane production application should use these.
    username="elastic",
    password="changeme",
    use_aws4auth=typed(boolean, default_value=False),
    timeout_seconds=typed(int, 10),
)
def configure_elasticsearch_client(graph):
    """
    Configure Elasticsearch client using a constructed dictionary config.

    :returns: an Elasticsearch client instance of the configured name

    """
    if graph.config.elasticsearch_client.use_aws4auth:
        region = graph.config.elasticsearch_client.aws_region
        awsauth = partial(
            awsv4sign,
            session=Session(),
            region=region,
        )
        config = dict(
            hosts=[{
                "host": graph.config.elasticsearch_client.host,
                "port": 443,
            }],
            connection_class=RequestsHttpConnection,
            http_auth=awsauth,
            use_ssl=True,
            verify_certs=True,
            timeout=graph.config.elasticsearch_client.timeout_seconds,
        )
    else:
        config = dict(
            hosts=[
                graph.config.elasticsearch_client.host,
            ],
            http_auth=(
                graph.config.elasticsearch_client.username,
                graph.config.elasticsearch_client.password,
            ),
        )
    return Elasticsearch(**config)
