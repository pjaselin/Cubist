import pytest

from .._variable_usage import _get_variable_usage


def test_variable_usage():
    with pytest.raises(ValueError):
        _get_variable_usage("", ["A"])
