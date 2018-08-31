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

     -  It can restrict the search to specific document types.

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

    def _search(self, explain=False, **kwargs):
        query = self._query()
        query = self._order_by(query, **kwargs)
        query = self._filter(query, **kwargs)
        if explain:
            query = query.extra(explain=True)
        return query

    def _to_instance(self, hit):
        """
        Resolve this hit into a model instance.

        """
        hit_doc_type = getattr(hit, self.doc_type_field, None)
        hit_model_class = self.doc_types.get(hit_doc_type)
        if hit_doc_type is not None and hit_model_class is not None:
            return hit_model_class(meta=hit.meta.to_dict(), **hit._d_)
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
        return self.index.search()

    def _order_by(self, query, **kwargs):
        """
        Add an order by clause to a (search) query.

        By default, uses reverse chronogical creation order.

        """
        return query.sort("-created_at")

    def _filter(self, query, offset=None, limit=None, doc_type=None, doc_types=(), **kwargs):
        """
        Filter a query with user-supplied arguments.

        :param doc_types: a list of legal doc types
        :param offset: pagination offset, if any
        :param limit: pagination limit, if any

        """
        if doc_type or doc_types:
            query = query.filter(
                "terms",
                **{
                    self.doc_type_field: [
                        doc_type_
                        for doc_type_ in self._iter_doc_types(doc_type, doc_types)
                    ],
                },
            )

        if offset is not None:
            query = query.extra(from_=offset)

        if limit is not None:
            query = query.extra(size=limit)

        return query

    def _iter_doc_types(self, doc_type=None, doc_types=()):
        if doc_type:
            yield doc_type
        yield from doc_types
