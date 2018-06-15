"""
Index Status convention.

"""
from marshmallow import Schema

from microcosm_flask.conventions.base import EndpointDefinition
from microcosm_flask.conventions.crud import configure_crud
from microcosm_flask.operations import Operation
from microcosm_flask.namespaces import Namespace
from microcosm_elasticsearch.index_status.resources import (
    IndexStatusSchema,
)
from microcosm_elasticsearch.index_status.store import IndexStatusStore


def configure_status_convention(graph):
    store = IndexStatusStore(graph)

    ns = Namespace(
        subject="index_status",
    )

    def search(**kwargs):
        status = store.get_status()
        return status, len(status)

    mappings = {
        Operation.Search: EndpointDefinition(
            func=search,
            request_schema=Schema(),
            response_schema=IndexStatusSchema(),
        ),
    }

    configure_crud(graph, ns, mappings)
    return ns
