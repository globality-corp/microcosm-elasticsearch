"""
Assertion support.

Elasticsearch inserts are not immediately indexed for search and count queries.

While it's possible to explicitly flush an index, the Elasticsearch persistence
model typically assumes that inserts are *not* indexed synchronously. For simpler
test code in these cases, it's helpful to have assertions that *eventually* resolve,
after some number of retries.

"""
from time import sleep

from hamcrest import assert_that, calling, raises


DEFAULT_TRIES = 3
DEFAULT_SLEEP_SECONDS = 0.1


def assert_that_eventually(func, matches, tries=DEFAULT_TRIES, sleep_seconds=DEFAULT_SLEEP_SECONDS):
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


def assert_that_not_eventually(func, matches, tries=DEFAULT_TRIES, sleep_seconds=DEFAULT_SLEEP_SECONDS):
    assert_that(
        calling(assert_that_eventually).with_args(func, matches, tries, sleep_seconds),
        raises(AssertionError),
    )
