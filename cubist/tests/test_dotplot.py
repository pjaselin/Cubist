from sklearn.datasets import load_iris
from cubist import Cubist
from cubist.dotplot import dotplot
import matplotlib.pyplot as plt


# def test_dotplot_from_estimator():
#     DotplotDisplay.from_estimator()


# def test_dotplot_from_predictions():
#     DotplotDisplay.from_predictions()


def test_dotplot_coeffs():
    X, y = load_iris(return_X_y=True, as_frame=True)
    model = Cubist()  # <- model parameters here, e.g. verbose=1
    model.fit(X, y)

    dotplot(model, what="coeffs")
    plt.savefig("dotplottest.png")


def test_dotplot_splits():
    X, y = load_iris(return_X_y=True, as_frame=True)
    model = Cubist()  # <- model parameters here, e.g. verbose=1
    model.fit(X, y)

    dotplot(model, what="splits")
    plt.savefig("testdotplotsplits.png")
