import pytest

from cubist._make_names_string import _escapes


@pytest.mark.parametrize(
    ("input", "expected"),
    [
        (["a", "b"], ["a", "b"]),
        (["a", 1], ["a", "1"]),
        (["a", None], ["a", "None"]),
        (["a:", "b|"], ["a\\\\:", "b\\\\\\|"]),
    ],
)
def test_escapes(input, expected):
    """make sure column titles are correctly escaped"""
    assert _escapes(input) == expected
