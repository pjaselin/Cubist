"""Tests for cubist._cubist_display_mixin._CubistDisplayMixin"""

import matplotlib.pyplot as plt
import pytest

from .._cubist_display_mixin import _CubistDisplayMixin
from ..cubist import Cubist


def test_gridspec_kwargs_and_existing_plot(iris):
    """Test using gridspec_kwargs and passing an existing subplots object"""
    _, ax = plt.subplots()
    model = Cubist().fit(*iris)
    display = _CubistDisplayMixin()
    display._validate_plot_params(  # pylint: disable=W0212
        ax=ax, df=model.splits_, gridspec_kwargs={"hspace": 0.2}
    )


def test_plot_grid_arrangement(california_housing):
    """Test adding one row to the number of rows needed when determining nrows/ncols"""
    X, y = california_housing
    model = Cubist()
    # only selecting 5 columns will trigger adding one row to the number of rows needed
    model.fit(X.iloc[:, :5], y)
    display = _CubistDisplayMixin()
    display._validate_plot_params(df=model.splits_, gridspec_kwargs={"hspace": 0.2})  # pylint: disable=W0212


def test_validate_from_estimator_params_all_valid(california_housing):
    """Test using valie commmittee and rule parameters"""
    model = Cubist(n_committees=5).fit(*california_housing)
    display = _CubistDisplayMixin()
    display._validate_from_estimator_params(df=model.splits_, committee=2, rule=2)  # pylint: disable=W0212


def test_validate_from_estimator_params_invalid_committee(california_housing):
    """Test using invalid committee parameter"""
    model = Cubist(n_committees=5).fit(*california_housing)
    display = _CubistDisplayMixin()
    # should raise TypeError
    with pytest.raises(TypeError):
        display._validate_from_estimator_params(df=model.splits_, committee=2.0)  # pylint: disable=W0212


def test_validate_from_estimator_params_invalid_rule(california_housing):
    """Test using invalid rule parameter"""
    model = Cubist(n_committees=5).fit(*california_housing)
    display = _CubistDisplayMixin()
    # should raise TypeError
    with pytest.raises(TypeError):
        display._validate_from_estimator_params(df=model.splits_, rule=2.0)  # pylint: disable=W0212
