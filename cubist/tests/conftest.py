"""Shared pytest fixtures:
https://docs.pytest.org/en/stable/reference/fixtures.html#conftest-py-sharing-fixtures-across-multiple-files"""

from contextlib import contextmanager

import pytest

from sklearn.datasets import fetch_openml, load_iris, fetch_california_housing
import pandas as pd


@contextmanager
def no_raise():
    """Utility context for not raising an error"""
    yield


@pytest.fixture
def ames_housing():
    """Fixture for ames housing dataset"""
    return fetch_openml(  # pylint: disable=W0621
        "ames_housing", version=1, as_frame=True, return_X_y=True, parser="auto"
    )


@pytest.fixture
def california_housing():
    """Fixture for california housing dataset"""
    return fetch_california_housing(return_X_y=True, as_frame=True)  # pylint: disable=W0621


@pytest.fixture
def iris():
    """Fixture for ames housing dataset"""
    return load_iris(return_X_y=True, as_frame=True)  # pylint: disable=W0621


@pytest.fixture
def boston():
    """Fixture for the Boston housing dataset"""
    X = pd.read_csv(
        "https://raw.githubusercontent.com/selva86/datasets/refs/heads/master/BostonHousing.csv"
    )
    y = X.medv
    X = X.drop(columns=["medv"])
    return X, y
