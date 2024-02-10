import pytest

# import pandas as pd
from sklearn.utils.validation import check_is_fitted
from sklearn.datasets import fetch_openml

from .conftest import no_raise
from ..cubist import Cubist


@pytest.fixture
def dfs():
    X, y = fetch_openml("titanic", version=1, as_frame=True, return_X_y=True)
    X = X.drop(["name", "ticket", "home.dest"], axis=1)
    return (X, y)


@pytest.mark.parametrize("expected_output", [True])
def test_model_instance(expected_output):
    """test model instantiates with the same identity as the class"""
    model = Cubist()
    assert isinstance(model, Cubist) == expected_output


@pytest.mark.parametrize(
    "n_rules,raises",
    [
        (1, no_raise()),
        (1000000, no_raise()),
        (0, pytest.raises(ValueError)),
        (1000001, pytest.raises(ValueError)),
        ("asdf", pytest.raises(TypeError)),
    ],
)
def test_n_rules(n_rules, raises, dfs):
    model = Cubist(n_rules=n_rules)
    with raises:
        model.fit(*dfs)
        check_is_fitted(model)


@pytest.mark.parametrize(
    "n_committees,raises",
    [
        (1, no_raise()),
        (100, no_raise()),
        (-1, pytest.raises(ValueError)),
        (0, pytest.raises(ValueError)),
        (500, pytest.raises(ValueError)),
        ("asdf", pytest.raises(TypeError)),
    ],
)
def test_n_committees(n_committees, raises, dfs):
    model = Cubist(n_committees=n_committees)
    with raises:
        model.fit(*dfs)
        check_is_fitted(model)


@pytest.mark.parametrize(
    "neighbors,auto,expected,raises",
    [
        (0, False, None, pytest.raises(ValueError)),
        (1, False, 1, no_raise()),
        (9, False, 9, no_raise()),
        (10, False, None, pytest.raises(ValueError)),
        (0, True, 0, no_raise()),
        (None, False, 0, no_raise()),
        (5.0, False, None, pytest.raises(TypeError)),
    ],
)
def test_neighbors(neighbors, auto, expected, raises, dfs):
    model = Cubist(neighbors=neighbors, auto=auto)
    with raises:
        assert expected == model._check_neighbors()  # noqa W0212
        model.fit(*dfs)
        check_is_fitted(model)


@pytest.mark.parametrize(
    "unbiased,raises",
    [
        (True, no_raise()),
        (False, no_raise()),
        (None, pytest.raises(TypeError)),
        ("aasdf", pytest.raises(TypeError)),
    ],
)
def test_unbiased(unbiased, raises, dfs):
    model = Cubist(unbiased=unbiased)
    with raises:
        model.fit(*dfs)
        check_is_fitted(model)


@pytest.mark.parametrize(
    "extrapolation,raises",
    [
        (0.0, no_raise()),
        (1.0, no_raise()),
        (-0.1, pytest.raises(ValueError)),
        (1.01, pytest.raises(ValueError)),
        (1, pytest.raises(TypeError)),
    ],
)
def test_extrapolation(extrapolation, raises, dfs):
    model = Cubist(extrapolation=extrapolation)
    with raises:
        model.fit(*dfs)
        check_is_fitted(model)


@pytest.mark.parametrize(
    "sample,raises",
    [
        (0.5, no_raise()),
        (0.0, pytest.raises(ValueError)),
        (1.0, pytest.raises(ValueError)),
        (-0.1, pytest.raises(ValueError)),
        (1.01, pytest.raises(ValueError)),
        (0, pytest.raises(TypeError)),
    ],
)
def test_sample(sample, raises, dfs):
    model = Cubist(sample=sample)
    with raises:
        model.fit(*dfs)
        check_is_fitted(model)


@pytest.mark.parametrize(
    "cv,expected,raises",
    [
        (10, 10, no_raise()),
        (-0.1, None, pytest.raises(TypeError)),
        (1, None, pytest.raises(ValueError)),
        (0, None, pytest.raises(ValueError)),
    ],
)
def test_cv(cv, expected, raises, dfs):
    model = Cubist(cv=cv)
    with raises:
        assert expected == model._check_cv()  # noqa W0212
        model.fit(*dfs)
        check_is_fitted(model)


@pytest.mark.parametrize(
    "auto,n,expected,raises",
    [
        (True, 5, "auto", no_raise()),
        (False, 5, "yes", no_raise()),
        (False, 0, "no", no_raise()),
        ("1234", 5, "", pytest.raises(TypeError)),
    ],
)
def test_auto(auto, n, expected, raises, dfs):
    model = Cubist(auto=auto)
    with raises:
        assert expected == model._check_composite(n)  # noqa W0212
        model.fit(*dfs)
        check_is_fitted(model)


@pytest.mark.parametrize(
    "i, raises",
    [(0, no_raise()), (5, pytest.raises(ValueError)), (1, pytest.raises(ValueError))],
)
def test_missing_column_name(i, raises, dfs):
    model = Cubist()
    X = dfs[0]
    y = dfs[1]
    # get the column names as a list
    col_names = list(X.columns)
    # change some number of columns to empty strings
    col_names[0:i] = [""] * i
    # reassign the list as the column names of X
    X.columns = col_names
    # check for ValueError with empty column names or no exceptions otherwise
    with raises:
        model.fit(X, y)
        check_is_fitted(model)
