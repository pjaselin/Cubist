"""test attribute usage functions"""

import pytest

from .._attribute_usage import _attribute_usage


def test_attribute_usage():
    """test that attribute usage function works"""
    with pytest.raises(ValueError):
        _attribute_usage("", ["A"])
