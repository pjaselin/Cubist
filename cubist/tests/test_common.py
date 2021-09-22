import pytest

from sklearn.utils.estimator_checks import check_estimator

from cubist import Cubist


@pytest.mark.parametrize(
    "estimator",
    [Cubist()]
)
def test_all_estimators(estimator):
    return check_estimator(estimator)
