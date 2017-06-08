"""
Index search.

"""
from microcosm_elasticsearch.errors import translate_elasticsearch_errors


class SearchIndex(object):
    """
    Elasticsearch search interface.

    """
    def __init__(self, graph, index, model_class):
        """
        :param graph: the object graph
        :param index: the name of an index to use

        """
        self.elasticsearch_client = graph.elasticsearch_client
        self.index = index
        self.model_class = model_class

    @property
    def index_name(self):
        return self.index._name

    @translate_elasticsearch_errors
    def count(self, **kwargs):
        """
        Count the number of models matching some criterion.

        """
        query = self._search(**kwargs)
        query.execute()
        return query.count()

    @translate_elasticsearch_errors
    def search(self, **kwargs):
        """
        Return the list of models matching some criterion.

        :param offset: pagination offset, if any
        :param limit: pagination limit, if any

        """
        items, _ = self.search_with_count(**kwargs)
        return items

    def search_with_count(self, **kwargs):
        """
        Return the list of models matching some criterion.

        :param offset: pagination offset, if any
        :param limit: pagination limit, if any

        """
        query = self._search(**kwargs)
        results = query.execute()
        return self._to_list(results.hits), query.count()

    def _search(self, **kwargs):
        query = self._query()
        query = self._order_by(query, **kwargs)
        query = self._filter(query, **kwargs)
        return query

    def _to_list(self, hits):
        return [
            self.model_class(**hit.to_dict())
            for hit in hits
        ]

    def _query(self):
        """
        Create a search query.

        """
        return self.index.search()

    def _order_by(self, query, **kwargs):
        """
        Add an order by clause to a (search) query.

        By default, uses reverse chronogical creation order.

        """
        return query.sort("-created_at")

    def _filter(self, query, offset=None, limit=None, **kwargs):
        """
        Filter a query with user-supplied arguments.

        :param offset: pagination offset, if any
        :param limit: pagination limit, if any

        """
        if offset is not None:
            query = query.extra(from_=offset)

        if limit is not None:
            query = query.extra(size=limit)

        return query
