import pytest

import pandas as pd
from sklearn.utils.validation import check_is_fitted

from .conftest import no_raise
from ..cubist import Cubist


@pytest.fixture
def titanic():
    df = pd.read_csv(
        "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/raw/titanic.csv"
    )
    df = df.drop(["name", "ticket"], axis=1)
    return df


@pytest.fixture
def X(titanic):
    return titanic.drop(["fare"], axis=1)


@pytest.fixture
def y(titanic):
    return titanic["fare"]


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
def test_n_rules(n_rules, raises, X, y):
    model = Cubist(n_rules=n_rules)
    with raises:
        model.fit(X, y)
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
def test_n_committees(n_committees, raises, X, y):
    model = Cubist(n_committees=n_committees)
    with raises:
        model.fit(X, y)
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
def test_neighbors(neighbors, auto, expected, raises, X, y):
    model = Cubist(neighbors=neighbors, auto=auto)
    with raises:
        assert expected == model._check_neighbors()  # noqa W0212
        model.fit(X, y)
        check_is_fitted(model)


@pytest.mark.parametrize(
    "unbiased,raises",
    [
        (True, no_raise()),
        (False, no_raise()),
        (None, pytest.raises(ValueError)),
        ("aasdf", pytest.raises(ValueError)),
    ],
)
def test_unbiased(unbiased, raises, X, y):
    model = Cubist(unbiased=unbiased)
    with raises:
        model.fit(X, y)
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
def test_extrapolation(extrapolation, raises, X, y):
    model = Cubist(extrapolation=extrapolation)
    with raises:
        model.fit(X, y)
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
def test_sample(sample, raises, X, y):
    model = Cubist(sample=sample)
    with raises:
        model.fit(X, y)
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
def test_cv(cv, expected, raises, X, y):
    model = Cubist(cv=cv)
    with raises:
        assert expected == model._check_cv()  # noqa W0212
        model.fit(X, y)
        check_is_fitted(model)


@pytest.mark.parametrize(
    "auto,expected,n,raises",
    [
        (True, "auto", 5, no_raise()),
        (False, "yes", 5, no_raise()),
        (False, "no", 0, no_raise()),
        ("1234", "", 5, pytest.raises(ValueError)),
    ],
)
def test_auto(auto, expected, n, raises, X, y):
    model = Cubist(auto=auto)
    with raises:
        assert expected == model._check_composite(n)  # noqa W0212
        model.fit(X, y)
        check_is_fitted(model)


@pytest.mark.parametrize(
    "i, raises",
    [(0, no_raise()), (5, pytest.raises(ValueError)), (1, pytest.raises(ValueError))],
)
def test_missing_column_name(i, raises, X, y):
    model = Cubist()
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
