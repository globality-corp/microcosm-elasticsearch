"""
Factory that configures Elasticsearch client.

"""
from functools import partial
from urllib.parse import urlparse, urlencode, parse_qs
from os import environ

from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from boto3 import Session
from elasticsearch import Elasticsearch, RequestsHttpConnection
from microcosm.api import defaults
from microcosm.config.types import boolean
from microcosm.config.validation import typed

def make_url_safe(raw_url):
    url = urlparse(raw_url)
    path = url.path or '/'
    querystring = ''
    if url.query:
        querystring = '?' + urlencode(parse_qs(url.query,
                                               keep_blank_values=True),
                                               doseq=True)
    safe_url = (url.scheme +
                '://' +
                url.netloc +
                path +
                querystring)
    return safe_url

def awsv4sign(r, *, session, region):
    request = AWSRequest(method=r.method.upper(),
                         url=make_safe_url(r.url),
                         data=r.body)
    credentials = self.session.get_credentials()
    SigV4Auth(credentials, 'es', self.region).add_auth(request)
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
)
def configure_elasticsearch_client(graph):
    """
    Configure Elasticsearch client using a constructed dictionary config.
    :returns: an Elasticsearch client instance of the configured name
    """
    if graph.config.elasticsearch_client.use_aws4auth:
        region = graph.config.elasticsearch_client.aws_region
        awsauth = functools.partial(aws4sign,
                                    session=Session(),
                                    region=region)
        config = dict(
                      hosts=[{
                          "host": graph.config.elasticsearch_client.host,
                          "port": 443,
                      }],
                      connection_class=RequestsHttpConnection,
                      http_auth=awsauth,
                      use_ssl=True,
                      verify_certs=True,
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
