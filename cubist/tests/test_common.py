"""Common scikit-learn estimator tests"""

from sklearn.datasets import make_regression
from sklearn.utils.estimator_checks import parametrize_with_checks

from ..cubist import Cubist


def expected_failed_checks(estimator):
    """Callable to pass sklearn checks that are known to fail"""
    if isinstance(estimator, Cubist):
        return {
            "check_sample_weight_equivalence_on_dense_data": "Cubist only accepts integers for `cv`",  # pylint: disable=C0301
        }
    return {}


@parametrize_with_checks([Cubist()], expected_failed_checks=expected_failed_checks)
def test_sklearn_compatible_estimator(estimator, check):
    """Perform common scikit-learn estimator tests"""
    return check(estimator)


def test_reasonable_score():
    """
    Determine whether Cubist returns a 'reasonable' score per:
    https://scikit-learn.org/stable/modules/generated/sklearn.utils.RegressorTags.html#sklearn.utils.RegressorTags
    """
    X, y = make_regression(  # pylint: disable=W0632
        n_samples=200,
        n_features=10,
        n_informative=1,
        bias=5.0,
        noise=20,
        random_state=42,
    )
    model = Cubist()
    model.fit(X, y)
    assert model.score(X, y) != 0.5
