"""Tests for cubist.cubist_coverage_display.CubistCoverageDisplay"""

import matplotlib.pyplot as plt
import pytest

from cubist import Cubist, CubistCoverageDisplay


def test_coverage_display(ames_housing_dataset):
    """Test creating a plot"""
    model = Cubist(n_committees=2).fit(*ames_housing_dataset)
    CubistCoverageDisplay.from_estimator(model, ames_housing_dataset[0])
    plt.savefig("coverage_display_test_ames.png")
    CubistCoverageDisplay.from_estimator(
        model, ames_housing_dataset[0], feature_names=["Gr_Liv_Area"]
    )
    plt.savefig("coverage_display_test_ames_subselect.png")


def test_coverage_display_for_r_parity(boston_dataset):
    """Test creating plot from the R package"""
    X, y = boston_dataset
    model = Cubist(n_rules=100, extrapolation=1.0)
    model.fit(X, y)

    CubistCoverageDisplay.from_estimator(model, X)
    plt.savefig("coverage_display_test_r_parity.png")


def test_iris_coverage_display(iris_dataset):
    """Test creating the readme iris coverage plot"""
    model = Cubist().fit(*iris_dataset)
    CubistCoverageDisplay.from_estimator(estimator=model, X=iris_dataset[0])
    plt.savefig("static/iris_coverage_display.png")


def test_coverage_display_line_kwargs(california_housing_dataset):
    """Test line_kwargs parameter"""
    model = Cubist().fit(*california_housing_dataset)
    CubistCoverageDisplay.from_estimator(
        model, california_housing_dataset[0], line_kwargs={"linewidth": 2}
    )


def test_validate_from_estimator_params_empty_dataframe(california_housing_dataset):
    """Test checking for empty dataframe"""
    model = Cubist(n_committees=5).fit(*california_housing_dataset)
    # set all rows of column type to be categorical so the plotting function ignores all rows
    model.splits_.type = "categorical"
    with pytest.raises(ValueError):
        CubistCoverageDisplay.from_estimator(
            model, california_housing_dataset[0], line_kwargs={"linewidth": 2}
        )
