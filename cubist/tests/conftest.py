from contextlib import contextmanager

import pytest

from sklearn.datasets import fetch_openml
from sklearn.utils.validation import check_is_fitted as sklearn_check_is_fitted

from ..cubist import Cubist


@contextmanager
def no_raise():
    yield


@pytest.fixture
def dfs():
    X, y = fetch_openml(  # pylint: disable=C0103, W0621
        "titanic", version=1, as_frame=True, return_X_y=True, parser="auto"
    )
    return (X, y)


@pytest.fixture
def X(dfs):  # pylint: disable=W0621
    return dfs[0].drop(["name", "ticket", "home.dest"], axis=1)


@pytest.fixture
def y(dfs):  # pylint: disable=W0621
    return dfs[1]


@pytest.fixture
def df_set(dfs, X, y):  # pylint: disable=W0621
    return {"dfs": dfs, "(X, y)": (X, y)}


def check_is_fitted(model: Cubist):
    return sklearn_check_is_fitted(
        model, attributes=["model_", "splits_", "coeffs_", "feature_importances_"]
    )
