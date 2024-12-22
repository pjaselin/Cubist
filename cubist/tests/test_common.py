"""common scikit-learn estimator tests"""

from sklearn.utils.estimator_checks import parametrize_with_checks
from sklearn.datasets import make_regression

from ..cubist import Cubist


@parametrize_with_checks([Cubist()])
def test_sklearn_compatible_estimator(estimator, check):
    """perform common scikit-learn estimator tests"""
    return check(estimator)


def test_reasonable_score():
    """determine whether Cubist returns a 'reasonable' score per:
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
