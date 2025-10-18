"""Shared pytest fixtures:
https://docs.pytest.org/en/stable/reference/fixtures.html#conftest-py-sharing-fixtures-across-multiple-files"""

from contextlib import contextmanager

import pandas as pd
import pytest
from sklearn.datasets import fetch_california_housing, fetch_openml, load_iris


@contextmanager
def no_raise():
    """Utility context for not raising an error"""
    yield


@pytest.fixture(scope="session")
def ames_housing_dataset():
    """Fixture for ames housing dataset"""
    return fetch_openml(  # pylint: disable=W0621
        "ames_housing", version=1, as_frame=True, return_X_y=True, parser="auto"
    )


@pytest.fixture(scope="session")
def california_housing_dataset():
    """Fixture for california housing dataset"""
    return fetch_california_housing(return_X_y=True, as_frame=True)  # pylint: disable=W0621


@pytest.fixture(scope="session")
def iris_dataset():
    """Fixture for iris dataset"""
    return load_iris(return_X_y=True, as_frame=True)  # pylint: disable=W0621


@pytest.fixture(scope="session")
def boston_dataset():
    """Fixture for the Boston housing dataset"""
    X = pd.read_csv(
        "https://raw.githubusercontent.com/selva86/datasets/refs/heads/master/BostonHousing.csv"
    )
    y = X.medv
    X = X.drop(columns=["medv"])
    return X, y
