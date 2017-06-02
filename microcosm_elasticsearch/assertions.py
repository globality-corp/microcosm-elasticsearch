"""
Assertion support.

Elasticsearch inserts are not immediately indexed for search and count queries. For simpler
test code, we use assertions that eventually resolve, after some number of retries.

"""
from time import sleep

from hamcrest import assert_that, calling, raises


def assert_that_eventually(func, matches, tries=3, sleep_seconds=0.1):
    last_error = None
    for _ in range(3):
        try:
            assert_that(func(), matches)
            break
        except Exception as error:
            last_error = error
        sleep(sleep_seconds)
    else:
        raise last_error


def assert_that_not_eventually(func, matches, tries=3, sleep_seconds=0.1):
    assert_that(
        calling(assert_that_eventually).with_args(func, matches, tries, sleep_seconds),
        raises(AssertionError),
    )