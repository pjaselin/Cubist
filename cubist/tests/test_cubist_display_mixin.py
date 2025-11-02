"""Tests for cubist._cubist_display_mixin._CubistDisplayMixin"""

import matplotlib.pyplot as plt
import pytest

from .._cubist_display_mixin import _CubistDisplayMixin
from ..cubist import Cubist


def test_gridspec_kwargs_and_existing_plot(iris_dataset):
    """Test using gridspec_kwargs and passing an existing subplots object"""
    _, ax = plt.subplots()
    model = Cubist().fit(*iris_dataset)
    display = _CubistDisplayMixin()
    display._validate_plot_params(  # pylint: disable=W0212
        ax=ax, df=model.splits_, gridspec_kwargs={"hspace": 0.2}
    )


def test_plot_grid_arrangement(california_housing_dataset):
    """Test adding one row to the number of rows needed when determining nrows/ncols"""
    X, y = california_housing_dataset
    model = Cubist()
    # only selecting 5 columns will trigger adding one row to the number of rows needed
    model.fit(X.iloc[:, :5], y)
    display = _CubistDisplayMixin()
    display._validate_plot_params(df=model.splits_, gridspec_kwargs={"hspace": 0.2})  # pylint: disable=W0212


def test_validate_from_estimator_params_all_valid(california_housing_dataset):
    """Test using value commmittee and rule parameters"""
    model = Cubist(n_committees=5).fit(*california_housing_dataset)
    display = _CubistDisplayMixin()
    display._validate_from_estimator_params(df=model.splits_, committee=2, rule=2)  # pylint: disable=W0212


def test_validate_from_estimator_params_invalid_committee(california_housing_dataset):
    """Test using invalid committee parameter"""
    model = Cubist(n_committees=5).fit(*california_housing_dataset)
    display = _CubistDisplayMixin()
    # should raise TypeError
    with pytest.raises(TypeError):
        display._validate_from_estimator_params(df=model.splits_, committee=2.0)  # pylint: disable=W0212


def test_validate_from_estimator_params_invalid_rule(california_housing_dataset):
    """Test using invalid rule parameter"""
    model = Cubist(n_committees=5).fit(*california_housing_dataset)
    display = _CubistDisplayMixin()
    # should raise TypeError
    with pytest.raises(TypeError):
        display._validate_from_estimator_params(df=model.splits_, rule=2.0)  # pylint: disable=W0212


def test_validate_from_estimator_params_invalid_feature_names(
    california_housing_dataset,
):
    """Test using invalid feature_names parameter values"""
    model = Cubist(n_committees=5).fit(*california_housing_dataset)
    display = _CubistDisplayMixin()
    # should raise TypeError
    with pytest.raises(TypeError):
        display._validate_from_estimator_params(df=model.splits_, feature_names="A")  # pylint: disable=W0212
    # should raise ValueError
    with pytest.raises(ValueError):
        display._validate_from_estimator_params(  # pylint: disable=W0212
            df=model.splits_, feature_names=["A", "B", "C"]
        )
