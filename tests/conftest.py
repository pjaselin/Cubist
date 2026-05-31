"""Shared pytest fixtures:
https://docs.pytest.org/en/stable/reference/fixtures.html#conftest-py-sharing-fixtures-across-multiple-files"""

from contextlib import contextmanager

import pandas as pd
import pytest
from sklearn.datasets import fetch_california_housing, load_iris


@contextmanager
def no_raise():
    """Utility context for not raising an error"""
    yield


@pytest.fixture(scope="session")
def ames_housing_dataset():
    """Fixture for ames housing dataset"""
    X = pd.read_csv(
        "https://raw.githubusercontent.com/wblakecannon/ames/378badd2c9e2e901a4bd4d466e9439d5e0059499/data/housing.csv",
        index_col=0,
    )
    y = X["SalePrice"]
    X = X.drop(columns=["SalePrice"])
    return X, y


@pytest.fixture(scope="session")
def california_housing_dataset():
    """Fixture for california housing dataset"""
    return fetch_california_housing(return_X_y=True, as_frame=True)


@pytest.fixture(scope="session")
def iris_dataset():
    """Fixture for iris dataset"""
    return load_iris(return_X_y=True, as_frame=True)


@pytest.fixture(scope="session")
def boston_dataset():
    """Fixture for the Boston housing dataset"""
    X = pd.read_csv(
        "https://raw.githubusercontent.com/selva86/datasets/5d788b9286864a80bc7b23703f372823bf6c600e/BostonHousing.csv"
    )
    y = X["medv"]
    X = X.drop(columns=["medv"])
    return X, y
