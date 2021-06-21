import pytest
from cubist import Cubist


@pytest.mark.parametrize(
    "expected_output",
    [
        True
    ]
)
def test_spam(expected_output):
    mdl = Cubist()
    assert isinstance(mdl, Cubist) == expected_output
