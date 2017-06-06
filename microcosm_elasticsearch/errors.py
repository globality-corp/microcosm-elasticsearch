"""
Elasticsearch errors.

Compatible with `microcosm-flask` HTTP error handling conventions.

"""
from functools import wraps

from elasticsearch.exceptions import ConflictError, NotFoundError, RequestError


def translate_elasticsearch_errors(func):
    """
    Translate Elasticsearch errors into HTTP compatible ones.

    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ConflictError:
            raise ElasticsearchConflictError
        except NotFoundError:
            raise ElasticsearchNotFoundError
        except RequestError as error:
            raise ElasticsearchError(error)
        except KeyError as error:
            # NB: usually caused by a missing index argument
            raise ElasticsearchError(error)
    return wrapper


class ElasticsearchError(Exception):
    """
    Something unexpected happened.

    """
    @property
    def status_code(self):
        # internal server error
        return 500


class ElasticsearchConflictError(ElasticsearchError):
    """
    An attempt to create or update an entity violated a constraint.

    Often expected behavior.

    """
    @property
    def status_code(self):
        # conflict
        return 409

    @property
    def include_stack_trace(self):
        return False


class ElasticsearchNotFoundError(ElasticsearchError):
    """
    A supplied identifier does not refer to a known entity.

    """
    @property
    def status_code(self):
        # not found
        return 404

    @property
    def include_stack_trace(self):
        return False
