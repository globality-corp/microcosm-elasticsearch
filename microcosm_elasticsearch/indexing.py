"""
Index management.

"""
from elasticsearch_dsl import Index


def make_index(graph, name=None):
    """
    Create a new index using standard naming conventions.

    In particular: uses a different index name for unit testing.

    """
    name = name or graph.metadata.name
    if graph.metadata.testing:
        name = "{}-test".format(name)

    return Index(name=name, using=graph.elasticsearch_client)


def createall(index, force=False):
    """
    Initialize the store's index.

    """
    if force and index.exists():
        index.delete()
    index.create()
