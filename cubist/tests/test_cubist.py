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
                         [(500, no_raise()),
                          (0, pytest.raises(ValueError)),
                          (10000000, pytest.raises(ValueError)),
                          ("asdf", pytest.raises(TypeError))])
def test_n_rules(n_rules, raises):
    model = Cubist(n_rules=n_rules)
    with raises:
        model.fit(X, y)
        check_is_fitted(model)


@pytest.mark.parametrize("n_committees,raises",
                         [(5, no_raise()),
                          (-1, pytest.raises(ValueError)),
                          (500, pytest.raises(ValueError)),
                          ("asdf", pytest.raises(TypeError))])
def test_n_committees(n_committees, raises):
    model = Cubist(n_committees=n_committees)
    with raises:
        model.fit(X, y)
        check_is_fitted(model)


@pytest.mark.parametrize("neighbors,raises",
                         [(5, no_raise()),
                          (10, pytest.raises(ValueError))])
def test_neighbors(neighbors, raises):
    model = Cubist(neighbors=neighbors)
    with raises:
        model.fit(X, y)
        check_is_fitted(model)


@pytest.mark.parametrize("unbiased,raises",
                         [(True, no_raise())])
def test_unbiased(unbiased, raises):
    model = Cubist(unbiased=unbiased)
    with raises:
        model.fit(X, y)
        check_is_fitted(model)


@pytest.mark.parametrize("extrapolation,raises",
                         [(0.1, no_raise()),
                          (-0.1, pytest.raises(ValueError))])
def test_extrapolation(extrapolation, raises):
    model = Cubist(extrapolation=extrapolation)
    with raises:
        model.fit(X, y)
        check_is_fitted(model)


@pytest.mark.parametrize("sample,raises",
                         [(0.1, no_raise()),
                          (-0.1, pytest.raises(ValueError))])
def test_sample(sample, raises):
    model = Cubist(sample=sample)
    with raises:
        model.fit(X, y)
        check_is_fitted(model)


@pytest.mark.parametrize("cv,raises",
                         [(10, no_raise()),
                          (-0.1, pytest.raises(TypeError)),
                          (-1, pytest.raises(ValueError))])
def test_cv(cv, raises):
    model = Cubist(cv=cv)
    with raises:
        model.fit(X, y)
        check_is_fitted(model)


@pytest.mark.parametrize("auto,raises",
                         [(True, no_raise()),
                          (False, no_raise()),
                          ("1234", pytest.raises(ValueError))])
def test_auto(auto, raises):
    model = Cubist(auto=auto)
    with raises:
        model.fit(X, y)
        check_is_fitted(model)
