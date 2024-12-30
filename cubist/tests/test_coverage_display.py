"""test for CubistCoverageDisplay"""

import matplotlib.pyplot as plt
import pandas as pd
import pytest
from sklearn.datasets import load_iris

from cubist import Cubist, CubistCoverageDisplay


def test_coverage_display():
    """test creating the plot"""
    X = pd.read_csv(
        "https://raw.githubusercontent.com/selva86/datasets/refs/heads/master/BostonHousing.csv"
    )
    y = X.medv
    X = X.drop(columns=["medv"])

    model = Cubist().fit(X, y)

    CubistCoverageDisplay.from_estimator(model, X)
    plt.savefig("coverage_display_test.png")


def test_iris_coverage_display():
    """test creating the readme iris coverage plot"""
    X, y = load_iris(return_X_y=True, as_frame=True)
    model = Cubist().fit(X, y)
    CubistCoverageDisplay.from_estimator(estimator=model, X=X)
    plt.savefig("www/iris_coverage_display.png")


def test_titanic_coverage_display(X, y):
    """test creating titanic coverage plot"""

    X = X.drop(columns=["cabin", "boat", "sex"])

    model = Cubist(n_rules=11, n_committees=2).fit(X, y)

    CubistCoverageDisplay.from_estimator(model, X)
    plt.savefig("titanic_coverage_display_test.png")


def test_coverage_display_line_kwargs():
    """test line_kwargs parameter"""
    X = pd.read_csv(
        "https://raw.githubusercontent.com/selva86/datasets/refs/heads/master/BostonHousing.csv"
    )
    y = X.medv
    X = X.drop(columns=["medv", "dis"])
    model = Cubist()
    model.fit(X, y)

    CubistCoverageDisplay.from_estimator(model, X, line_kwargs={"linewidth": 2})


def test_validate_from_estimator_params_empty_dataframe():
    """test checking for empty dataframe"""
    X = pd.read_csv(
        "https://raw.githubusercontent.com/selva86/datasets/refs/heads/master/BostonHousing.csv"
    )
    y = X.medv
    X = X.drop(columns=["medv", "dis"])

    model = Cubist(n_committees=5)
    model.fit(X, y)
    # set all rows of column type to be categorical
    model.splits_.type = "categorical"
    with pytest.raises(ValueError):
        CubistCoverageDisplay.from_estimator(model, X, line_kwargs={"linewidth": 2})
