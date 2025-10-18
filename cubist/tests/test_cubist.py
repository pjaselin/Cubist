"""Test cubist.cubist.Cubist configuration"""

import random
from copy import deepcopy

import pytest
from sklearn.utils.validation import check_is_fitted

from ..cubist import Cubist, CubistError
from .conftest import no_raise


@pytest.mark.parametrize("expected_output", [True])
def test_model_instance(expected_output):
    """Test model instantiates with the same identity as the class"""
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
def test_n_rules(n_rules, raises, ames_housing_dataset):
    """Test `n_rules` parameter"""
    model = Cubist(n_rules=n_rules)
    with raises:
        model.fit(*ames_housing_dataset)
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
def test_n_committees(n_committees, raises, ames_housing_dataset):
    """Test `n_committees` parameter"""
    model = Cubist(n_committees=n_committees)
    with raises:
        model.fit(*ames_housing_dataset)
        check_is_fitted(model)


@pytest.mark.parametrize(
    "neighbors,auto,expected,raises",
    [
        (0, False, 0, pytest.raises(ValueError)),
        (1, False, 1, no_raise()),
        (9, False, 9, no_raise()),
        (10, False, 10, pytest.raises(ValueError)),
        (None, True, 0, no_raise()),
        (None, False, 0, no_raise()),
        (5.0, False, 5.0, pytest.raises(ValueError)),
        (5, True, 0, pytest.raises(ValueError)),
    ],
)
def test_neighbors(neighbors, auto, expected, raises, ames_housing_dataset):  # pylint: disable=R0913,R0917
    """Test `neighbors` parameter"""
    model = Cubist(neighbors=neighbors, auto=auto)
    with raises:
        assert expected == model._check_neighbors()  # noqa W0212, pylint: disable=W0212
        model.fit(*ames_housing_dataset)
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
def test_unbiased(unbiased, raises, ames_housing_dataset):
    """Test `unbiased` parameter"""
    model = Cubist(unbiased=unbiased)
    with raises:
        model.fit(*ames_housing_dataset)
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
def test_extrapolation(extrapolation, raises, ames_housing_dataset):
    """Test `extrapolation` parameter"""
    model = Cubist(extrapolation=extrapolation)
    with raises:
        model.fit(*ames_housing_dataset)
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
def test_sample(sample, raises, ames_housing_dataset):
    """Test `sample` parameter"""
    model = Cubist(sample=sample)
    with raises:
        model.fit(*ames_housing_dataset)
        check_is_fitted(model)


@pytest.mark.parametrize(
    "cv,raises",
    [
        (10, no_raise()),
        (-0.1, pytest.raises(TypeError)),
        (1, pytest.raises(ValueError)),
        (0, pytest.raises(ValueError)),
    ],
)
def test_cv(cv, raises, ames_housing_dataset):
    """Test `cv` parameter"""
    model = Cubist(cv=cv)
    with raises:
        model.fit(*ames_housing_dataset)


@pytest.mark.parametrize(
    "auto,n,expected,raises,warns",
    [
        (True, 5, "auto", no_raise(), pytest.warns(UserWarning)),
        (False, 5, "yes", no_raise(), no_raise()),
        (False, 0, "no", no_raise(), no_raise()),
        ("1234", 5, "auto", pytest.raises(TypeError), no_raise()),
    ],
)
def test_auto(auto, n, expected, raises, warns, iris_dataset):  # pylint: disable=R0913,R0917
    """Test `auto` parameter"""
    model = Cubist(auto=auto)
    assert expected == model._check_composite(n)  # noqa W0212, pylint: disable=W0212
    with raises:
        with warns:
            model.fit(*iris_dataset)
            check_is_fitted(model)


@pytest.mark.parametrize(
    "i, raises",
    [(0, no_raise()), (5, pytest.raises(ValueError)), (1, pytest.raises(ValueError))],
)
def test_missing_column_name(i, raises, ames_housing_dataset):
    """Test for where a column name is an empty string"""
    X, y = deepcopy(ames_housing_dataset)
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


def test_verbose(capfd, ames_housing_dataset):
    """Test to make sure verbose parameter prints to stdout"""
    model = Cubist(verbose=True, target_label="new outcome label")
    model.fit(*ames_housing_dataset)
    out, _ = capfd.readouterr()
    assert out


def test_training_errors(ames_housing_dataset):
    """Test catching training errors"""
    # valid test
    model = Cubist().fit(*ames_housing_dataset)
    check_is_fitted(model)
    X, y = deepcopy(ames_housing_dataset)
    # set the Sale_Condition column as a string
    X.Sale_Condition = X.Sale_Condition.astype(str)
    # add a bad string
    X.loc[0, "Sale_Condition"] = "test. bad, string"
    # training should now fail
    with pytest.raises(CubistError):
        model = Cubist().fit(X, y)
        check_is_fitted(model)


def test_sample_colnames(ames_housing_dataset):
    """Test using the word 'sample' as a column name"""
    X, y = deepcopy(ames_housing_dataset)
    X.columns = [random.choice(["sample", "Sample"]) + col for col in list(X.columns)]
    model = Cubist().fit(X, y)
    check_is_fitted(model)


def test_feature_importances(ames_housing_dataset):
    """Test `feature_importances_` attribute"""
    model = Cubist().fit(*ames_housing_dataset)
    check_is_fitted(model)
    assert list(model.feature_importances_.columns) == [
        "Conditions",
        "Model",
        "Variable",
    ]
