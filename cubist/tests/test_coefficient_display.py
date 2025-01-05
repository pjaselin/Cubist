"""Tests for cubist.cubist_coefficient_display.CubistCoefficientDisplay"""

import matplotlib.pyplot as plt

from cubist import Cubist, CubistCoefficientDisplay


def test_coefficient_display(ames_housing):
    """Test creating a plot"""
    model = Cubist(n_committees=2).fit(*ames_housing)
    CubistCoefficientDisplay.from_estimator(model)
    plt.savefig("coefficient_display_test_ames.png")
    CubistCoefficientDisplay.from_estimator(model, feature_names=["Gr_Liv_Area"])
    plt.savefig("coefficient_display_test_ames_subselect.png")


def test_coefficient_display_for_r_parity(boston):
    """Test creating plot from the R library"""
    model = Cubist(n_rules=100, extrapolation=1.0)
    model.fit(*boston)
    CubistCoefficientDisplay.from_estimator(model)
    plt.savefig("coefficient_display_test_r_parity.png")


def test_coefficient_iris_display(iris):
    """Test creating the readme iris coefficient plot"""
    model = Cubist().fit(*iris)
    CubistCoefficientDisplay.from_estimator(estimator=model)
    plt.savefig("static/iris_coefficient_display.png")


def test_coefficient_display_scatter_kwargs(ames_housing):
    """Test scatter_kwargs parameter"""
    model = Cubist().fit(*ames_housing)
    CubistCoefficientDisplay.from_estimator(model, scatter_kwargs={"alpha": 0.5})
