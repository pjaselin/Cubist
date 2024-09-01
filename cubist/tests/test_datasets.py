import random

import pytest

import pandas as pd
import numpy as np
from sklearn.datasets import (
    load_diabetes,
    fetch_california_housing,
    make_regression,
    make_sparse_uncorrelated,
    # fetch_openml,
)
from sklearn.utils.validation import check_is_fitted

from ..cubist import Cubist


def test_sklearn_diabetes_nan():
    X, y = load_diabetes(return_X_y=True, as_frame=True)
    # randomly dropping cells with 20% probability
    X = X.mask(np.random.random(X.shape) < 0.2)
    model = Cubist()
    model.fit(X, y)
    check_is_fitted(model)


def test_sklearn_california_housing():
    X, y = fetch_california_housing(return_X_y=True, as_frame=True)
    model = Cubist()
    model.fit(X, y)
    check_is_fitted(model)


def test_sklearn_regression():
    X, y = make_regression(random_state=0)
    model = Cubist()
    model.fit(X, y)
    check_is_fitted(model)


def test_sklearn_sparse_uncorrelated():
    X, y = make_sparse_uncorrelated(random_state=0)
    model = Cubist()
    model.fit(X, y)
    check_is_fitted(model)


def test_one_model_one_committee():
    X, y = fetch_california_housing(return_X_y=True, as_frame=True)
    model = Cubist(n_rules=1, n_committees=1, verbose=1)
    model.fit(X, y)
    check_is_fitted(model)
    assert model.rules_ is not None
    assert model.coeff_ is not None


# def test_openml_titanic():
#     X, y = fetch_openml(
#         "titanic", version=2, as_frame=True, return_X_y=True, parser="auto"
#     )
#     model = Cubist()
#     model.fit(X, y)
#     check_is_fitted(model)


def test_small_ds_warning():
    with pytest.warns(Warning):
        X = pd.DataFrame(
            dict(
                a=pd.Series(random.sample(range(10, 30), 5)),
                b=pd.Series(random.sample(range(10, 30), 5)),
                c=pd.Series(random.sample(range(10, 30), 5)),
            )
        )
        y = pd.Series(random.sample(range(10, 30), 5))
        model = Cubist(sample=0.8)
        model.fit(X, y)
        check_is_fitted(model)
