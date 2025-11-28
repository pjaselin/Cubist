"""Test cubist._attribute_usage._attribute_usage functions"""

import pytest

from cubist import Cubist
from cubist._attribute_usage import _attribute_usage


def test_attribute_usage_missing_attribute_info():
    """Test that attribute usage function handles Cubist not returning attribute
    info report"""
    with pytest.raises(ValueError):
        _attribute_usage("", ["A"])


def test_attribute_usage(iris_dataset):
    """Test that attribute usage function works with attributes not included
    in Cubist's report"""
    X, y = iris_dataset
    model = Cubist().fit(X, y)
    df = _attribute_usage(model.output_, list(X.columns) + ["A"])
    assert df.shape[0] == len(X.columns) + 1
