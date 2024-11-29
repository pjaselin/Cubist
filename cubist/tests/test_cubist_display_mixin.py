"""tests for _CubistDisplayMixin"""

from sklearn.datasets import load_iris, fetch_california_housing
import matplotlib.pyplot as plt
import pytest

from .._cubist_display_mixin import _CubistDisplayMixin
from ..cubist import Cubist


def test_gridspec_kwargs_and_existing_plot():
    """test using gridspec_kwargs and passing an existing subplots object"""
    _, ax = plt.subplots()
    X, y = load_iris(return_X_y=True, as_frame=True)  # pylint: disable=C0103
    model = Cubist()
    model.fit(X, y)
    display = _CubistDisplayMixin()
    display._validate_plot_params(  # pylint: disable=W0212
        ax=ax, df=model.splits_, gridspec_kwargs={"hspace": 0.2}
    )


def test_plot_grid_arrangement():
    """test adding one row to the number of rows needed when determining nrows/ncols"""
    X, y = fetch_california_housing(return_X_y=True, as_frame=True)  # pylint: disable=C0103
    model = Cubist()
    # only selecting 5 columns will trigger adding one row to the number of rows needed
    model.fit(X.iloc[:, :5], y)
    display = _CubistDisplayMixin()
    display._validate_plot_params(df=model.splits_, gridspec_kwargs={"hspace": 0.2})  # pylint: disable=W0212


def test_validate_from_estimator_params_all_valid():
    """test using valie commmittee and rule parameters"""
    X, y = fetch_california_housing(return_X_y=True, as_frame=True)  # pylint: disable=C0103
    model = Cubist(n_committees=5)
    model.fit(X, y)
    display = _CubistDisplayMixin()
    display._validate_from_estimator_params(df=model.splits_, committee=2, rule=2)  # pylint: disable=W0212


def test_validate_from_estimator_params_invalid_committee():
    """test using invalid committee parameter"""
    X, y = fetch_california_housing(return_X_y=True, as_frame=True)  # pylint: disable=C0103
    model = Cubist(n_committees=5)
    model.fit(X, y)
    display = _CubistDisplayMixin()
    # should raise TypeError
    with pytest.raises(TypeError):
        display._validate_from_estimator_params(df=model.splits_, committee=2.0)  # pylint: disable=W0212


def test_validate_from_estimator_params_invalid_rule():
    """test using invalid rule parameter"""
    X, y = fetch_california_housing(return_X_y=True, as_frame=True)  # pylint: disable=C0103
    model = Cubist(n_committees=5)
    model.fit(X, y)
    display = _CubistDisplayMixin()
    # should raise TypeError
    with pytest.raises(TypeError):
        display._validate_from_estimator_params(df=model.splits_, rule=2.0)  # pylint: disable=W0212
