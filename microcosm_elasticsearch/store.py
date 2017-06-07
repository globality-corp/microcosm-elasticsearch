"""
Abstraction layer for persistence operations.

Allows upstream (e.g. HTTP) operations to use a consistent persistence interface
and avoids leaking persistence abstractions throughout a code base.

Intended to be duck-type compatible with `microcosm_postgres.store.Store`.

"""
from contextlib import contextmanager
from time import time
from uuid import uuid4

from microcosm_elasticsearch.errors import translate_elasticsearch_errors


class Store(object):
    """
    Elasticsearch persistence interface.

    """
    def __init__(self, graph, index, model_class):
        """
        :param graph: the object graph
        :param index: the name of an index to use
        :param model_class: a `elasticsearch_dsl.DocType` subclass to persist.

        """
        self.elasticsearch_client = graph.elasticsearch_client
        self.index = index
        self.model_class = model_class

        # register the model with the index
        self.index.doc_type(self.model_class)

        # NB: do NOT provide a model backref here because "smart" shortcuts on the
        # model will conflict with existing methods on the DocType base class

    @property
    def doc_type(self):
        return self.model_class._doc_type.name

    @property
    def index_name(self):
        return self.index._name

    @contextmanager
    def flushing(self):
        """
        Flush the current session if there's no error.

        Flushing an index is not an expected behavior for Elasticsearch writes, but
        can be very useful for test cases.

        """
        yield
        self.index.flush()

    def new_object_id(self):
        """
        Injectable id generation to facilitate mocking.

        Uses string-valued UUID because ES uuid support is not terrific.

        """
        return str(uuid4())

    def new_timestamp(self):
        """
        Injectable timestamp generation to facilitate mocking.

        """
        # NB: Elasticsearch supports epoch_millis by default
        return int(time() * 1000)

    @translate_elasticsearch_errors
    def create(self, instance):
        """
        Persist an entity into Elasticsearch.

        """
        now_millis = self.new_timestamp()

        if instance.id is None:
            instance.id = self.new_object_id()

        instance._id = instance.id
        instance.created_at = now_millis
        instance.updated_at = now_millis

        # NB: the DSL save function will overwrite existing records; use the raw client
        self.elasticsearch_client.create(
            id=instance.id,
            index=self.index_name,
            doc_type=self.doc_type,
            body=instance.to_dict(),
        )
        return instance

    @translate_elasticsearch_errors
    def retrieve(self, identifier):
        """
        Retrieve a model by primary key and zero or more other criteria.

        :raises `ElasticsearchNotFoundError` if there is no existing model

        """
        return self.model_class.get(
            id=identifier,
            index=self.index_name,
            using=self.elasticsearch_client,
        )

    @translate_elasticsearch_errors
    def update(self, identifier, new_instance):
        """
        Update an existing model with a new one.

        :raises `ElasticsearchNotFoundError` if there is no existing model

        """
        new_instance.id = identifier
        new_instance._id = identifier
        new_instance.updated_at = self.new_timestamp()

        new_instance.update(
            using=self.elasticsearch_client,
            index=self.index_name,
            **new_instance.to_dict()
        )
        return new_instance

    @translate_elasticsearch_errors
    def replace(self, identifier, new_instance):
        """
        Create or update an entity.

        """
        now_millis = self.new_timestamp()

        if new_instance.id is None:
            if identifier is None:
                identifier = self.new_object_id()
            new_instance.id = identifier

        if new_instance.created_at is None:
            new_instance.created_at = now_millis

        new_instance._id = new_instance.id
        new_instance.updated_at = now_millis

        new_instance.save(
            id=new_instance.id,
            using=self.elasticsearch_client,
            index=self.index_name,
            validate=True,
        )
        return new_instance

    @translate_elasticsearch_errors
    def delete(self, identifier):
        """
        Delete a model by primary key.

        :raises `ElasticsearchNotFoundError` if there is no existing model

        """
        instance = self.model_class(
            _id=identifier,
        )
        instance.delete(
            index=self.index_name,
            using=self.elasticsearch_client,
        )
        return True

    @translate_elasticsearch_errors
    def count(self, *criterion, **kwargs):
        """
        Count the number of models matching some criterion.

        """
        query = self._query()
        query = self._filter(query, **kwargs)

        # NB: DSL does not have obvious count support; use the raw client
        result = self.elasticsearch_client.count(
            index=self.index_name,
            doc_type=self.doc_type,
            body=query.to_dict(),
        )
        return result["count"]

    @translate_elasticsearch_errors
    def search(self, **kwargs):
        """
        Return the list of models matching some criterion.

        :param offset: pagination offset, if any
        :param limit: pagination limit, if any

        """
        query = self._query()
        query = self._order_by(query, **kwargs)
        query = self._filter(query, **kwargs)
        return [
            self.model_class(**hit.to_dict())
            for hit in query.execute().hits
        ]

    def _query(self):
        """
        Create a search query.

        """
        return self.model_class.search(
            index=self.index_name,
            using=self.elasticsearch_client,
        )

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
