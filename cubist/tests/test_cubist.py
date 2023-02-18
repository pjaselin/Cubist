import pytest

import pandas as pd
from sklearn.utils.validation import check_is_fitted

from ..cubist import Cubist

titanic = pd.read_csv("https://raw.githubusercontent.com/mwaskom/seaborn-data/master/raw/titanic.csv")
titanic = titanic.drop(["name", "ticket"], axis=1)

y = titanic["fare"]
X = titanic.drop(["fare"], axis=1)


@pytest.mark.parametrize(
    "expected_output",
    [True]
)
def test_model_instance(expected_output):
    model = Cubist()
    assert isinstance(model, Cubist) == expected_output


def test_n_rules():
    model = Cubist(n_rules=500)
    model.fit(X, y)
    check_is_fitted(model)


def test_n_rules_fail():
    model = Cubist(n_rules=10000000)
    with pytest.raises(ValueError):
        model.fit(X, y)
        check_is_fitted(model)


def test_n_committees():
    model = Cubist(n_committees=5)
    model.fit(X, y)
    check_is_fitted(model)


def test_n_committees_fail1():
    model = Cubist(n_committees=-1)
    with pytest.raises(ValueError):
        model.fit(X, y)
        check_is_fitted(model)


def test_n_committees_fail2():
    model = Cubist(n_committees="sdfa")
    with pytest.raises(TypeError):
        model.fit(X, y)
        check_is_fitted(model)


def test_neighbors():
    model = Cubist(neighbors=5, auto=True)
    model.fit(X, y)
    check_is_fitted(model)


def test_neighbors_fail():
    model = Cubist(neighbors=10)
    with pytest.raises(ValueError):
        model.fit(X, y)
        check_is_fitted(model)


def test_unbiased():
    model = Cubist(unbiased=True)
    model.fit(X, y)
    check_is_fitted(model)


def test_extrapolation():
    model = Cubist(extrapolation=0.1)
    model.fit(X, y)
    check_is_fitted(model)


def test_extrapolation_fail():
    model = Cubist(extrapolation=-0.1)
    with pytest.raises(ValueError):
        model.fit(X, y)
        check_is_fitted(model)


def test_sample():
    model = Cubist(sample=0.1)
    model.fit(X, y)
    check_is_fitted(model)


def test_sample_fail():
    model = Cubist(sample=-0.1)
    with pytest.raises(ValueError):
        model.fit(X, y)
        check_is_fitted(model)

def test_cv():
    model = Cubist(cv=10)
    model.fit(X, y)
    check_is_fitted(model)


def test_cv_fail1():
    model = Cubist(cv=-0.1)
    with pytest.raises(TypeError):
        model.fit(X, y)
        check_is_fitted(model)

def test_cv_fail2():
    model = Cubist(cv=-1)
    with pytest.raises(ValueError):
        model.fit(X, y)
        check_is_fitted(model)

@pytest.mark.parametrize("test_input,expected", 
                        [(True, True), 
                         (False, True), 
                         ])
def test_auto(test_input, expected):
    model = Cubist(auto=test_input)
    model.fit(X, y)
    check_is_fitted(model)

def test_auto_fail():
    model = Cubist(auto="1234")
    with pytest.raises(ValueError):
        model.fit(X, y)
        check_is_fitted(model)
