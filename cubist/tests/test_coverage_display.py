"""Tests for cubist.cubist_coverage_display.CubistCoverageDisplay"""

import matplotlib.pyplot as plt
import pytest

from cubist import Cubist, CubistCoverageDisplay


def test_coverage_display(ames_housing):
    """Test creating the plot"""
    model = Cubist().fit(*ames_housing)
    CubistCoverageDisplay.from_estimator(model, ames_housing[0])
    plt.savefig("coverage_display_test.png")


def test_iris_coverage_display(iris):
    """Test creating the readme iris coverage plot"""
    model = Cubist().fit(*iris)
    CubistCoverageDisplay.from_estimator(estimator=model, X=iris[0])
    plt.savefig("static/iris_coverage_display.png")


def test_coverage_display_line_kwargs(california_housing):
    """Test line_kwargs parameter"""
    model = Cubist().fit(*california_housing)
    CubistCoverageDisplay.from_estimator(
        model, california_housing[0], line_kwargs={"linewidth": 2}
    )


def test_validate_from_estimator_params_empty_dataframe(california_housing):
    """Test checking for empty dataframe"""
    model = Cubist(n_committees=5).fit(*california_housing)
    # set all rows of column type to be categorical so the plotting function ignores all rows
    model.splits_.type = "categorical"
    with pytest.raises(ValueError):
        CubistCoverageDisplay.from_estimator(
            model, california_housing[0], line_kwargs={"linewidth": 2}
        )
