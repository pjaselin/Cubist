from sklearn.datasets import load_iris, fetch_california_housing
import matplotlib.pyplot as plt
import pytest

from .._cubist_display_mixin import _CubistDisplayMixin
from ..cubist import Cubist


def test_gridspec_kwargs_and_existing_plot():
    fig, ax = plt.subplots()
    X, y = load_iris(return_X_y=True, as_frame=True)
    model = Cubist()
    model.fit(X, y)

    display = _CubistDisplayMixin()
    display._validate_plot_params(
        ax=ax, df=model.splits_, gridspec_kwargs={"hspace": 0.2}
    )


def test_plot_grid_arrangement():
    """test adding one row to the number of rows needed when determining nrows/ncols"""
    X, y = fetch_california_housing(return_X_y=True, as_frame=True)
    model = Cubist()
    # 5 columns will trigger adding one row to the number of rows needed
    model.fit(X.iloc[:, :5], y)

    display = _CubistDisplayMixin()
    display._validate_plot_params(df=model.splits_, gridspec_kwargs={"hspace": 0.2})


def test_validate_from_estimator_params_all_valid():
    X, y = fetch_california_housing(return_X_y=True, as_frame=True)
    model = Cubist(n_committees=5)
    model.fit(X, y)

    display = _CubistDisplayMixin()
    display._validate_from_estimator_params(df=model.splits_, committee=2, rule=2)


def test_validate_from_estimator_params_invalid_committee():
    X, y = fetch_california_housing(return_X_y=True, as_frame=True)
    model = Cubist(n_committees=5)
    model.fit(X, y)

    display = _CubistDisplayMixin()
    with pytest.raises(TypeError):
        display._validate_from_estimator_params(df=model.splits_, committee=2.0)


def test_validate_from_estimator_params_invalid_rule():
    X, y = fetch_california_housing(return_X_y=True, as_frame=True)
    model = Cubist(n_committees=5)
    model.fit(X, y)

    display = _CubistDisplayMixin()
    with pytest.raises(TypeError):
        display._validate_from_estimator_params(df=model.splits_, rule=2.0)
