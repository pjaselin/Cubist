from sklearn.utils.estimator_checks import parametrize_with_checks

from ..cubist import Cubist


@parametrize_with_checks([Cubist()])
def test_sklearn_compatible_estimator(estimator, check):
    """perform common scikit-learn tests"""
    return check(estimator)
