"""Shared pytest fixtures:
https://docs.pytest.org/en/stable/reference/fixtures.html#conftest-py-sharing-fixtures-across-multiple-files"""

from contextlib import contextmanager

import pytest

from sklearn.datasets import fetch_openml


@contextmanager
def no_raise():
    """utility context for not raising an error"""
    yield


@pytest.fixture
def dfs():
    """fixture for titanic dataset"""
    X, y = fetch_openml(  # pylint: disable=W0621
        "titanic", version=1, as_frame=True, return_X_y=True, parser="auto"
    )
    return (X, y)


@pytest.fixture
def X(dfs):  # pylint: disable=W0621
    """fixture for X array of titanic dataset"""
    return dfs[0].drop(["name", "ticket", "home.dest"], axis=1)


@pytest.fixture
def y(dfs):  # pylint: disable=W0621
    """fixture for y array of titanic dataset"""
    return dfs[1]


@pytest.fixture
def df_set(dfs, X, y):  # pylint: disable=W0621
    """fixture for dictionary of titanic dataset"""
    return {"dfs": dfs, "(X, y)": (X, y)}
