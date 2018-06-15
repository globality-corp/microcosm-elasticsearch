"""
Index Status Store

"""
from microcosm_elasticsearch.index_status.models import IndexStatus


class IndexStatusStore:

    def __init__(self, graph):
        self.index_registry = graph.elasticsearch_index_registry

    def process_status_data(self, status, stats):
        """
        Iterate through returned data and return related stats

        """
        indices = []
        for name, data in status.items():
            indices.append(
                IndexStatus(
                    name=name,
                    data=data,
                    stats=stats['indices'][name]
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
                )
            )
        return indices
