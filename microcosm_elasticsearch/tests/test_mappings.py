"""
Test mapping constructions.

"""
from hamcrest import assert_that, has_entries

from microcosm_elasticsearch.tests.fixtures import AutoComplete


def test_auto_complete_mapping():
    model = AutoComplete
    assert_that(
        model._doc_type.mapping.to_dict(),
        has_entries(
            auto_complete=has_entries(
                properties=has_entries(
                    text=has_entries(
                        type="completion",
                    ),
                    id=has_entries(
                        type="keyword",
                    ),
                    created_at=has_entries(
                        type="date",
                    ),
                    updated_at=has_entries(
                        type="date",
                    ),
                ),
            ),
        ),
    )
