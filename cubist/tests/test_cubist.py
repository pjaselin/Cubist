from _pytest.monkeypatch import V
import pytest

import pandas as pd

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
    assert model.is_fitted_


def test_n_rules_fail():
    model = Cubist(n_rules=10000000)
    with pytest.raises(ValueError):
        model.fit(X, y)
        assert model.is_fitted_


def test_n_committees():
    model = Cubist(n_committees=5)
    model.fit(X, y)
    assert model.is_fitted_


def test_n_committees_fail():
    model = Cubist(n_committees=101)
    with pytest.raises(ValueError):
        model.fit(X, y)
        assert model.is_fitted_


def test_neighbors():
    model = Cubist(neighbors=5)
    model.fit(X, y)
    assert model.is_fitted_


def test_neighbors_fail():
    model = Cubist(neighbors=10)
    with pytest.raises(ValueError):
        model.fit(X, y)
        assert model.is_fitted_


def test_unbiased():
    model = Cubist(unbiased=True)
    model.fit(X, y)
    assert model.is_fitted_


def test_extrapolation():
    model = Cubist(extrapolation=0.1)
    model.fit(X, y)
    assert model.is_fitted_


def test_extrapolation_fail():
    model = Cubist(extrapolation=-0.1)
    with pytest.raises(ValueError):
        model.fit(X, y)
        assert model.is_fitted_


def test_sample():
    model = Cubist(sample=0.1)
    model.fit(X, y)
    assert model.is_fitted_


def test_sample_fail():
    model = Cubist(sample=-0.1)
    with pytest.raises(ValueError):
        model.fit(X, y)
        assert model.is_fitted_
