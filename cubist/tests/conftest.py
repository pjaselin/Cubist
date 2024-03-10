from contextlib import contextmanager

import pytest

from sklearn.datasets import fetch_openml


@contextmanager
def no_raise():
    yield


@pytest.fixture
def dfs():
    X, y = fetch_openml(
        "titanic", version=1, as_frame=True, return_X_y=True, parser="auto"
    )
    return (X, y)


@pytest.fixture
def X(dfs):
    return dfs[0].drop(["name", "ticket", "home.dest"], axis=1)


@pytest.fixture
def y(dfs):
    return dfs[1]


@pytest.fixture
def df_set(dfs, X, y):
    return {"dfs": dfs, "(X, y)": (X, y)}
