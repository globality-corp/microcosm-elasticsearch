"""
Abstraction layer for persistence operations.

Allows upstream (e.g. HTTP) operations to use a consistent persistence interface
and avoids leaking persistence abstractions throughout a code base.

Intended to be duck-type compatible with `microcosm_postgres.store.Store`.

"""
from contextlib import contextmanager
from time import time
from uuid import uuid4
from elasticsearch.helpers import bulk

from microcosm_elasticsearch.errors import translate_elasticsearch_errors


class Store:
    """
    Elasticsearch persistence interface.

    """
    def __init__(self, graph, index, model_class, search_index):
        """
        :param graph: the object graph
        :param index: the name of an index to use
        :param model_class: a `elasticsearch_dsl.DocType` subclass to persist.

        """
        self.elasticsearch_client = graph.elasticsearch_client
        self.index = index
        self.model_class = model_class

        search_index.register_doc_type(model_class)
        self.search_index = search_index

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

    def count(self, **kwargs):
        # delegate
        return self.search_index.count(**kwargs)

    def search(self, **kwargs):
        # delegate
        return self.search_index.search(**kwargs)

    def search_with_count(self, **kwargs):
        # delegate
        return self.search_index.search_with_count(**kwargs)

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

        return self.retrieve(identifier)

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

    def _add_id_to_instance(self, instance):
        """
        Defines an ID for an instance if not previously defined

        Set the internal _id equal to the instance ID

        """
        if instance.id is None:
            instance.id = self.new_object_id()

        instance._id = instance.id
        return instance

    def _add_op_type(self, instance, op_type):
        """
        Decorates an instance with a bulk operation type

        """
        instance["_op_type"] = op_type
        return instance

    def _batch_bulk(self, actions, batch_size):
        """
        Breaks list of actions into batches

        """
        num_actions = len(actions)
        for offset in range(0, num_actions, batch_size):
            yield actions[offset:min(offset + batch_size, num_actions)]

    @translate_elasticsearch_errors
    def bulk(self, actions, batch_size):
        """
        Bulk index entities

        actions: list of tuples of (action, instance) to be included in the bulk
        batch_size: number of records for each bulk call

        All errors and exceptions are suppressed and are returned in the response report

        """
        actions = [
            self._add_op_type(
                instance=self._add_id_to_instance(instance).to_dict(True),
                op_type=action,
            )
            for action, instance in actions
        ]

        return [
            bulk(
                client=self.elasticsearch_client,
                actions=actions_batch,
                index=self.index._name,
                raise_on_exception=False,
                raise_on_error=False,
            ) for actions_batch in self._batch_bulk(
                actions=actions,
                batch_size=batch_size,
            )
        ]
