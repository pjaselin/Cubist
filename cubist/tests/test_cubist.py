from contextlib import contextmanager

import pytest

import pandas as pd
from sklearn.utils.validation import check_is_fitted

from ..cubist import Cubist

titanic = pd.read_csv("https://raw.githubusercontent.com/mwaskom/seaborn-data/master/raw/titanic.csv")
titanic = titanic.drop(["name", "ticket"], axis=1)

y = titanic["fare"]
X = titanic.drop(["fare"], axis=1)


@contextmanager
def no_raise():
    yield


@pytest.mark.parametrize("expected_output", [True])
def test_model_instance(expected_output):
    model = Cubist()
    assert isinstance(model, Cubist) == expected_output


@pytest.mark.parametrize("n_rules,raises",
                         [(1, no_raise()),
                          (1000000, no_raise()),
                          (0, pytest.raises(ValueError)),
                          (1000001, pytest.raises(ValueError)),
                          ("asdf", pytest.raises(TypeError))])
def test_n_rules(n_rules, raises):
    model = Cubist(n_rules=n_rules)
    with raises:
        model.fit(X, y)
        check_is_fitted(model)


@pytest.mark.parametrize("n_committees,raises",
                         [(1, no_raise()),
                          (100, no_raise()),
                          (-1, pytest.raises(ValueError)),
                          (0, pytest.raises(ValueError)),
                          (500, pytest.raises(ValueError)),
                          ("asdf", pytest.raises(TypeError))])
def test_n_committees(n_committees, raises):
    model = Cubist(n_committees=n_committees)
    with raises:
        model.fit(X, y)
        check_is_fitted(model)


@pytest.mark.parametrize("neighbors,expected,raises",
                         [(0, None, pytest.raises(ValueError)),
                          (1, 1, no_raise()),
                          (9, 9, no_raise()),
                          (10, None, pytest.raises(ValueError))])
def test_neighbors(neighbors, expected, raises):
    model = Cubist(neighbors=neighbors)
    with raises:
        assert expected == model._check_neighbors()
        model.fit(X, y)
        check_is_fitted(model)


@pytest.mark.parametrize("unbiased,raises",
                         [(True, no_raise()),
                          (False, no_raise()),
                          (None, pytest.raises(ValueError)),
                          ("aasdf", pytest.raises(ValueError))])
def test_unbiased(unbiased, raises):
    model = Cubist(unbiased=unbiased)
    with raises:
        model.fit(X, y)
        check_is_fitted(model)


@pytest.mark.parametrize("extrapolation,raises",
                         [(0.0, no_raise()),
                          (1.0, no_raise()),
                          (-0.1, pytest.raises(ValueError)),
                          (1.01, pytest.raises(ValueError))])
def test_extrapolation(extrapolation, raises):
    model = Cubist(extrapolation=extrapolation)
    with raises:
        model.fit(X, y)
        check_is_fitted(model)


@pytest.mark.parametrize("sample,raises",
                         [(0.5, no_raise()),
                          (0.0, pytest.raises(ValueError)),
                          (1.0, pytest.raises(ValueError)),
                          (-0.1, pytest.raises(ValueError)),
                          (1.01, pytest.raises(ValueError))])
def test_sample(sample, raises):
    model = Cubist(sample=sample)
    with raises:
        model.fit(X, y)
        check_is_fitted(model)


@pytest.mark.parametrize("cv,expected,raises",
                         [(10, 10, no_raise()),
                          (-0.1, None, pytest.raises(TypeError)),
                          (1, None, pytest.raises(ValueError)),
                          (0, None, pytest.raises(ValueError))])
def test_cv(cv, expected, raises):
    model = Cubist(cv=cv)
    with raises:
        assert expected == model._check_cv()
        model.fit(X, y)
        check_is_fitted(model)


@pytest.mark.parametrize("auto,expected,n,raises",
                         [(True, "auto", 5, no_raise()),
                          (False, "yes", 5, no_raise()),
                          (False, "no", 0, no_raise()),
                          ("1234", "", 5, pytest.raises(ValueError))])
def test_auto(auto, expected, n, raises):
    model = Cubist(auto=auto)
    with raises:
        assert expected == model._check_composite(n)
        model.fit(X, y)
        check_is_fitted(model)


@pytest.mark.parametrize("raises",
                         [(pytest.raises(ValueError))])
def test_missing_column_name(raises):
    model = Cubist()
    # copy X so we can change the column names without editing the main object
    X_changed_cols = X.copy(deep=True)
    # change the age column to an empty string
    X_changed_cols = X_changed_cols.rename(columns={"age": ""})
    # make sure we get a ValueError for this
    with raises:
        model.fit(X_changed_cols, y)
        check_is_fitted(model)
