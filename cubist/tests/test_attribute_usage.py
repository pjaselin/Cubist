"""test attribute usage functions"""

import pytest
from sklearn.datasets import load_iris

from cubist import Cubist
from .._attribute_usage import _attribute_usage


def test_attribute_usage_missing_attribute_info():
    """test that attribute usage function handles missing attribute info"""
    with pytest.raises(ValueError):
        _attribute_usage("", ["A"])


def test_attribute_usage():
    """test that attribute usage function works"""
    X, y = load_iris(return_X_y=True, as_frame=True)
    model = Cubist().fit(X, y)
    _attribute_usage(model.output_, list(X.columns) + ["A"])
