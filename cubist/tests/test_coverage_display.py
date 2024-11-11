# from sklearn.datasets import load_iris
from cubist import Cubist, CubistCoverageDisplay
import matplotlib.pyplot as plt
import pandas as pd


# def test_dotplot_from_estimator():
#     DotplotDisplay.from_estimator()


# def test_dotplot_from_predictions():
#     DotplotDisplay.from_predictions()


def test_coverage_display():
    X = pd.read_csv(
        "https://raw.githubusercontent.com/selva86/datasets/refs/heads/master/BostonHousing.csv"
    )
    y = X.medv
    X = X.drop(columns=["medv", "dis"])
    # X, y = load_iris(return_X_y=True, as_frame=True)
    model = Cubist()  # <- model parameters here, e.g. verbose=1
    model.fit(X, y)

    CubistCoverageDisplay.from_estimator(model)
    plt.savefig("dotplottest.png")


# def test_dotplot_splits():
# X = pd.read_csv(
#     "https://raw.githubusercontent.com/selva86/datasets/refs/heads/master/BostonHousing.csv"
# )
# y = X.medv
# X = X.drop(columns=["medv", "dis"])
# # X, y = load_iris(return_X_y=True, as_frame=True)
# model = Cubist()  # <- model parameters here, e.g. verbose=1
# model.fit(X, y)

# DotplotDisplay.from_estimator(model, what="splits")
# plt.savefig("testdotplotsplits.png")
