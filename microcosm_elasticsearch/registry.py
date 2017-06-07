"""
Manage a set of indexes and/or aliases.

"""
from elasticsearch_dsl import Index
from inflection import underscore


class IndexRegistry(object):
    """
    A registry of application indexes.

    """
    def __init__(self, graph):
        self.graph = graph
        self.indexes = {}

    def register(self, name=None, version=None):
        """
        Register an index locally.

        Note that `createall` is needed to save the index to Elasticsearch.

        The index will be named per convention such that:
         -  The graph's name is used by default
         -  The "test" suffix is added for unit testing (to avoid clobbering real data)

        If version is provided, it will be used to create generate an alias (to the unversioned name).

        """
        if version is None:
            index_name = IndexRegistry.name_for(self.graph, name=name)
            alias_name = None
        else:
            # create index with full version, alias to shortened version
            index_name = IndexRegistry.name_for(self.graph, name=name, version=version)
            alias_name = IndexRegistry.name_for(self.graph, name=name)

        if index_name in self.indexes:
            raise Exception("Index already registered for name: {}".format(index_name))

        index = Index(
            name=index_name,
            using=self.graph.elasticsearch_client,
        )
        if alias_name is not None:
            index.aliases(**{alias_name: {}})

        self.indexes[index_name] = index
        return index

    def createall(self, force=False, only=(), skip=()):
        """
        Create all indexes in Elasticsearch.

        """
        for index in self.indexes.values():
            if only and index._name not in only:
                continue
            if skip and index._name in skip:
                continue
            if force and index.exists():
                index.delete()
            index.create()

    @staticmethod
    def name_for(graph, name=None, version=None):
        """
        Generate a convention-aware index name.

        In particular: uses a different index name for unit testing.

        """
        name_parts = [
            name or graph.metadata.name,
        ]

        if version is not None:
            name_parts.append(str(version))

        if graph.metadata.testing:
            name_parts.append("test")

        return "_".join([underscore(name_part) for name_part in name_parts])
