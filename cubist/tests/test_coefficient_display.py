"""tests for CubistCoefficientDisplay"""

import matplotlib.pyplot as plt
import pandas as pd

from cubist import Cubist, CubistCoefficientDisplay


def test_coverage_display():
    """test creating the plot"""
    X = pd.read_csv(
        "https://raw.githubusercontent.com/selva86/datasets/refs/heads/master/BostonHousing.csv"
    )
    y = X.medv
    X = X.drop(columns=["medv", "dis"])
    # X, y = load_iris(return_X_y=True, as_frame=True)
    model = Cubist()  # <- model parameters here, e.g. verbose=1
    model.fit(X, y)

    CubistCoefficientDisplay.from_estimator(model)
    plt.savefig("dotplottest.png")


def test_coverage_display_scatter_kwargs():
    """test scatter_kwargs parameter"""
    X = pd.read_csv(
        "https://raw.githubusercontent.com/selva86/datasets/refs/heads/master/BostonHousing.csv"
    )
    y = X.medv
    X = X.drop(columns=["medv", "dis"])

    model = Cubist()
    model.fit(X, y)

    CubistCoefficientDisplay.from_estimator(model, scatter_kwargs={"alpha": 0.5})
