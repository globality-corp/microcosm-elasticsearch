"""
Index search.

"""
from elasticsearch_dsl.mapping import Mapping

from microcosm_elasticsearch.errors import translate_elasticsearch_errors


class SearchIndex:
    """
    Encapsulates search against an index.

    An index may have many (polymorphic) document types registered with it. The search index
    handles this complexity in two ways:

     -  It creates instances of a specific model class as the results of any searches.

        If searching a polymorphic index, the model class should be a compatible base class.

     -  It restricts the search to specific document types.

        By default, all document types registered with the index are used. To query a single
        type in a polymorphic index, the model class and document type should be set to the
        same type.

    """
    __mapping_type_name__ = "doc"

    @property
    def mapping_type_name(self):
        return self.__class__.__mapping_type_name__

    @property
    def doc_type_field(self):
        """
        Defines document field used to determine the document's polymorphic type in a single-mapping-type index

        """
        return "doctype"

    def __init__(self, graph, index, doc_type=None):
        """
        :param graph: the object graph
        :param index: the name of an index to use
        :param doc_type: the doc type to search for; uses the index's doc types if omitted

        """
        self.elasticsearch_client = graph.elasticsearch_client
        self.index = index
        # Mapping from ES custom type field to corresponding model class
        self.doc_types = dict()
        self.mapping = Mapping(self.mapping_type_name)
        if doc_type is not None:
            self.register_doc_type(doc_type)

    def register_doc_type(self, model_class):
        model_doctype = model_class.get_model_doctype()
        self.doc_types[model_doctype] = model_class
        self.update_mapping(model_class)

    def update_mapping(self, model_class):
        self.mapping.update(model_class._doc_type.mapping)
        self.index.mapping(self.mapping)

    @property
    def index_name(self):
        return self.index._name

    @translate_elasticsearch_errors
    def count(self, **kwargs):
        """
        Count the number of models matching some criterion.

        """
        query = self._search(**kwargs)
        return query.count()

    @translate_elasticsearch_errors
    def search(self, **kwargs):
        """
        Return the list of models matching some criterion.

        :param offset: pagination offset, if any
        :param limit: pagination limit, if any

        """
        query = self._search(**kwargs)
        results = query.execute()
        return self._to_list(results)

    def search_with_count(self, **kwargs):
        """
        Return the list of models matching some criterion.

        :param offset: pagination offset, if any
        :param limit: pagination limit, if any

        """
        query = self._search(**kwargs)
        results = query.execute()
        return self._to_list(results), query.count()

    def _search(self, **kwargs):
        query = self._query()
        query = self._order_by(query, **kwargs)
        query = self._filter(query, **kwargs)
        return query

    def _to_instance(self, hit):
        """
        Resolve this hit into a model instance.

        """
        hit_doc_type = getattr(hit, self.doc_type_field, None)
        hit_model_class = self.doc_types.get(hit_doc_type)
        if hit_doc_type is not None and hit_model_class is not None:
            return hit_model_class(**hit._d_)
        # Will return be a generic `Hit`
        return hit

    def _to_list(self, results):
        """
        Resolve this hit into a list of instances.

        """
        return [
            self._to_instance(hit)
            for hit in results.hits
        ]

    def _query(self):
        """
        Create a search query.

        Starts with the index's search function; customizes with the provided doc types, if any

        """
        query = self.index.search()
        query = query.filter("terms", **{self.doc_type_field: [type_name for type_name in self.doc_types]})
        return query

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

    @classmethod
    def for_only(cls, graph, index, doc_type):
        return cls(graph, index, doc_type)
