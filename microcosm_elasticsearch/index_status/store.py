"""
Index Status Store

"""
from microcosm_elasticsearch.index_status.models import IndexStatus


class IndexStatusStore:

    def __init__(self, graph):
        self.index_registry = graph.elasticsearch_index_registry

    def process_status_data(self, status, stats, index):
        """
        There is a known structure to how ES returns data about itself
        Extract interesting properties to share for introspection

        """
        indices = []
        for name, data in status.items():
            aliases = [
                alias for alias
                in data["aliases"].keys()
            ]
            mapping = [
                dict(name=field, data_type=info["type"])
                for mapping_type in data["mappings"].keys()
                for field, info in data["mappings"][mapping_type]["properties"].items()
            ]
            index_stats = stats["indices"][name]["total"]
            stats = dict(
                docs=index_stats["docs"],
                indexing=index_stats["indexing"]
            )
            indices.append(
                IndexStatus(
                    name=name,
                    aliases=aliases,
                    mapping=mapping,
                    stats=stats
                )
            )
        return indices

    def get_status(self):
        indices = []
        for key, index in self.index_registry.indexes.items():
            indices.extend(
                self.process_status_data(
                    status=index.get(),
                    stats=index.stats(),
                    index=index,
                )
            )
        return indices
