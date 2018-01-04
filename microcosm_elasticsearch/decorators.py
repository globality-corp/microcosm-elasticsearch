"""
Some useful decorators

"""
from functools import wraps

from elasticsearch.exceptions import AuthorizationException
from microcosm_flask.errors import as_retryable


def retryable(func):
    """
    Mark authorization error as retryable

    Useful e.g. when using an AWS-hosted ES
    AWS credentials can expire; encourage retries for synchronous requests.

    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AuthorizationException as error:
            raise as_retryable(error)
    return wrapper
