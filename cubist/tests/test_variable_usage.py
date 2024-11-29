"""test variable usage functions"""

import pytest

from .._variable_usage import _variable_usage


def test_variable_usage():
    """test that variable usage function works"""
    with pytest.raises(ValueError):
        _variable_usage("", ["A"])
