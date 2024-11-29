"""test for CubistCoverageDisplay"""

import matplotlib.pyplot as plt
import pandas as pd
import pytest

from cubist import Cubist, CubistCoverageDisplay


def test_coverage_display():
    """test creating plot"""
    X = pd.read_csv(  # pylint: disable=C0103
        "https://raw.githubusercontent.com/selva86/datasets/refs/heads/master/BostonHousing.csv"
    )
    y = X.medv
    X = X.drop(columns=["medv", "dis"])  # pylint: disable=C0103

    model = Cubist()
    model.fit(X, y)

    CubistCoverageDisplay.from_estimator(model)
    plt.savefig("dotplottest.png")


def test_coverage_display_line_kwargs():
    """test line_kwargs parameter"""
    X = pd.read_csv(  # pylint: disable=C0103
        "https://raw.githubusercontent.com/selva86/datasets/refs/heads/master/BostonHousing.csv"
    )
    y = X.medv
    X = X.drop(columns=["medv", "dis"])  # pylint: disable=C0103
    model = Cubist()
    model.fit(X, y)

    CubistCoverageDisplay.from_estimator(model, line_kwargs={"linewidth": 2})


def test_validate_from_estimator_params_empty_dataframe():
    """test checking for empty dataframe"""
    X = pd.read_csv(  # pylint: disable=C0103
        "https://raw.githubusercontent.com/selva86/datasets/refs/heads/master/BostonHousing.csv"
    )
    y = X.medv
    X = X.drop(columns=["medv", "dis"])  # pylint: disable=C0103

    model = Cubist(n_committees=5)
    model.fit(X, y)
    # set all rows of column type to be categorical
    model.splits_.type = "categorical"
    with pytest.raises(ValueError):
        CubistCoverageDisplay.from_estimator(model, line_kwargs={"linewidth": 2})
