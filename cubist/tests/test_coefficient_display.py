"""Tests for cubist.cubist_coefficient_display.CubistCoefficientDisplay"""

import matplotlib.pyplot as plt

from cubist import Cubist, CubistCoefficientDisplay


def test_coefficient_display(ames_housing):
    """Test creating the plot"""
    model = Cubist().fit(*ames_housing)
    CubistCoefficientDisplay.from_estimator(model)
    plt.savefig("coefficient_display_test.png")


def test_coefficient_iris_display(iris):
    """Test creating the readme iris coefficient plot"""
    model = Cubist().fit(*iris)
    CubistCoefficientDisplay.from_estimator(estimator=model)
    plt.savefig("static/iris_coefficient_display.png")


def test_coefficient_display_scatter_kwargs(ames_housing):
    """Test scatter_kwargs parameter"""
    model = Cubist().fit(*ames_housing)
    CubistCoefficientDisplay.from_estimator(model, scatter_kwargs={"alpha": 0.5})
