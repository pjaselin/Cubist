import pytest

from .._variable_usage import _variable_usage


def test_variable_usage():
    with pytest.raises(ValueError):
        _variable_usage("", ["A"])
