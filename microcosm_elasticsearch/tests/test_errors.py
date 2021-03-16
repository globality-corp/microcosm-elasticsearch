"""
Test error translation.

"""
from elasticsearch.exceptions import ConflictError, NotFoundError, RequestError
from hamcrest import assert_that, calling, raises

from microcosm_elasticsearch.errors import (
    ElasticsearchConflictError,
    ElasticsearchError,
    ElasticsearchNotFoundError,
    translate_elasticsearch_errors,
)


@translate_elasticsearch_errors
def fixture(error):
    raise error


def test_error():
    assert_that(calling(fixture).with_args(RequestError), raises(ElasticsearchError))


def test_conflict_error():
    assert_that(calling(fixture).with_args(ConflictError), raises(ElasticsearchConflictError))


def test_not_found_error():
    assert_that(calling(fixture).with_args(NotFoundError), raises(ElasticsearchNotFoundError))
