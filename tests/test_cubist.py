import pytest
from cubist import Cubist


@pytest.mark.parametrize(
    "expected_output",
    [
        True
    ]
)
def test_spam(expected_output):
    model = Cubist()
    assert isinstance(model, Cubist) == expected_output
