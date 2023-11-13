import pytest

from src.utils.process_permutations import process_permutations


@pytest.mark.parametrize(
    ("buffer_set", "target_list", "found_dict", "expected"),
    (
        (set(), {""}, {0: set()}, {0: set()}),
        ({"a"}, {""}, {0: set()}, {0: set()}),
        ({"abcd"}, {"abcdefg"}, {0: set()}, {0: {"abcd"}}),
        (
            {"aapxj", "apaxj", "apxaj", "aaxpj", "axpaj", "axapj"},
            {"aapxjdnrbtvldptfzbbdbbzxtndrvaxpajjblnzjfpvhdhhpxjdnrbt"},
            {0: set()},
            {0: {"aapxj", "axpaj"}},
        ),
        (
            {"dnrbt", "dnbrt", "drnbt", "drbnt", "dbnrt", "dbrnt"},
            {"aapxjdnrbtvldptfzbbdbbzxtndrvaxpajjblnzjfpvhdhhpxjdnrbt"},
            {0: set()},
            {0: {"dnrbt"}},
        ),
    ),
)
def test_count_occurrences(buffer_set, target_list, found_dict, expected):
    assert process_permutations(buffer_set, target_list, found_dict) == expected
