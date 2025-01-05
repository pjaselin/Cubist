"""Test Cubist against a variety of datasets"""

import random

import pytest

import pandas as pd
import numpy as np
from sklearn.datasets import load_diabetes
from sklearn.model_selection import train_test_split
from sklearn.utils.validation import check_is_fitted

from ..cubist import Cubist, CubistError


def test_one_model_one_committee(california_housing):
    """Test one model/one committee"""
    model = Cubist(n_rules=1, n_committees=1).fit(*california_housing)
    check_is_fitted(model)
    assert model.splits_ is not None
    assert model.coeffs_ is not None


def test_small_ds_warning():
    """Test small dataset"""
    with pytest.warns(Warning):
        X = pd.DataFrame(
            {
                "a": pd.Series(random.sample(range(10, 30), 5)),
                "b": pd.Series(random.sample(range(10, 30), 5)),
                "c": pd.Series(random.sample(range(10, 30), 5)),
            }
        )
        y = pd.Series(random.sample(range(10, 30), 5))
        model = Cubist(sample=0.8)
        model.fit(X, y)
        check_is_fitted(model)


def test_undefined_cases():
    """Catch when undefined cases are raised"""
    X, y = load_diabetes(return_X_y=True, as_frame=True)

    X_train, X_test, y_train, _ = train_test_split(
        X, y, test_size=0.33, random_state=42
    )

    new_col = np.array([random.choice("AB") for i in range(y_train.shape[0])]).reshape(
        (y_train.shape[0], 1)
    )
    X_train = np.hstack((X_train, new_col))

    model = Cubist()
    model.fit(X_train, y_train)
    check_is_fitted(model)

    new_col = np.array([random.choice("AC") for i in range(X_test.shape[0])]).reshape(
        (X_test.shape[0], 1)
    )

    X_test = np.hstack((X_test, new_col))

    with pytest.raises(CubistError) as e:
        y = model.predict(X_test)
        assert "undefined.cases" in str(e)
