"""tests for CubistCoefficientDisplay"""

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.datasets import load_iris

from cubist import Cubist, CubistCoefficientDisplay


def test_coefficient_display():
    """test creating the plot"""
    X = pd.read_csv(
        "https://raw.githubusercontent.com/selva86/datasets/refs/heads/master/BostonHousing.csv"
    )
    y = X.medv
    X = X.drop(columns=["medv"])

    model = Cubist()
    model.fit(X, y)

    CubistCoefficientDisplay.from_estimator(model)
    plt.savefig("coefficient_display_test.png")


def test_iris_coefficient_display():
    """test creating the readme iris coefficient plot"""
    X, y = load_iris(return_X_y=True, as_frame=True)
    model = Cubist().fit(X, y)
    CubistCoefficientDisplay.from_estimator(estimator=model)
    plt.savefig("www/iris_coefficient_display.png")


def test_coefficient_display_scatter_kwargs():
    """test scatter_kwargs parameter"""
    X = pd.read_csv(
        "https://raw.githubusercontent.com/selva86/datasets/refs/heads/master/BostonHousing.csv"
    )
    y = X.medv
    X = X.drop(columns=["medv", "nox"])
    model = Cubist()
    model.fit(X, y)
    CubistCoefficientDisplay.from_estimator(model, scatter_kwargs={"alpha": 0.5})
