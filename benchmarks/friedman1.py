"""ML-ENSEMBLE

Benchmark of ML-Ensemble against Scikit-learn estimators using Scikit-learn's
friedman1 dataset.

All estimators are instantiated with default settings, and all estimators in
the ensemble are part of the benchmark.

The default ensemble configuration achieves a 25% score improvement as compared
to the best benchmark estimator (GradientBoostingRegressor).

"""

from time import time
import os

import numpy as np
import pandas as pd

from mlens.ensemble import SuperLearner
from mlens.utils import safe_print
from mlens.metrics import rmse

from sklearn.datasets import make_friedman1
from sklearn.base import clone
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import Lasso, ElasticNet
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.kernel_ridge import KernelRidge

from cubist import Cubist

from sklearn.linear_model import LinearRegression
from lineartree import LinearTreeRegressor

import warnings

warnings.filterwarnings(action="ignore", module="scipy", message="^internal gelsd")


def build_ensemble(**kwargs):
    """Generate ensemble."""

    ens = SuperLearner(**kwargs)
    prep = {
        "Standard Scaling": [StandardScaler()],
        "Min Max Scaling": [MinMaxScaler()],
        "No Preprocessing": [],
    }

    est = {
        "Standard Scaling": [ElasticNet(), Lasso(), KNeighborsRegressor()],
        "Min Max Scaling": [SVR()],
        "No Preprocessing": [
            RandomForestRegressor(random_state=0),
            GradientBoostingRegressor(),
        ],
    }

    ens.add(est, prep)

    ens.add(GradientBoostingRegressor(), meta=True)

    return ens


if __name__ == "__main__":
    safe_print("\nML-ENSEMBLE\n")
    safe_print(
        "Benchmark of ML-ENSEMBLE against Scikit-learn estimators "
        "on the friedman1 dataset.\n"
    )
    safe_print("Scoring metric: Root Mean Squared Error.\n")

    safe_print("Available CPUs: %i\n" % os.cpu_count())

    SEED = 2017
    np.random.seed(SEED)

    step = 40000
    mi = step
    mx = 400000 + step

    ens_multi = build_ensemble(folds=2, shuffle=False, n_jobs=-1)

    ESTIMATORS = {
        "Ensemble": ens_multi,
        "Random F": RandomForestRegressor(random_state=SEED, n_jobs=-1),
        "   elNet": make_pipeline(StandardScaler(), ElasticNet()),
        "   Lasso": make_pipeline(StandardScaler(), Lasso()),
        "Kern Rid": make_pipeline(MinMaxScaler(), KernelRidge()),
        "     SVR": make_pipeline(MinMaxScaler(), SVR()),
        "     GBM": GradientBoostingRegressor(),
        "     KNN": KNeighborsRegressor(n_jobs=-1),
        "  Cubist": Cubist(),
        "LineTree": LinearTreeRegressor(base_estimator=LinearRegression()),
    }

    names = {k.strip(" "): k for k in ESTIMATORS}
    times = {e: [] for e in ESTIMATORS}
    scores = {e: [] for e in ESTIMATORS}

    sizes = range(mi, mx, step)

    safe_print("Ensemble architecture")
    safe_print("Num layers: %i" % len(ens_multi.layers))

    safe_print("\nBenchmark estimators", end=": ")
    for name in sorted(names):
        if name == "Ensemble":
            continue
        safe_print(name, end=" ")
    safe_print("\n")

    safe_print("Data")
    safe_print("Features: %i" % 10)
    safe_print(
        "Training set sizes: from %i to %i with step size %i.\n"
        % (np.floor(mi / 2), np.floor((mx - step) / 2), np.floor(step / 2))
    )

    safe_print("SCORES")
    safe_print("%6s" % "size", end=" | ")

    for name in sorted(names):
        safe_print("%s" % names[name], end=" | ")
    safe_print()

    for size in sizes:
        n = int(np.floor(size / 2))

        X, y = make_friedman1(n_samples=size, random_state=SEED)

        safe_print("%6i" % n, end=" | ")
        for name in sorted(names):
            e = clone(ESTIMATORS[names[name]])
            t0 = time()
            e.fit(X[:n], y[:n])
            t1 = time() - t0
            times[names[name]].append(t1)

            s = rmse(y[n:], e.predict(X[n:]))
            scores[names[name]].append(s)

            safe_print("%8.2f" % (s), end=" | ", flush=True)

        safe_print()

    safe_print("\nFIT TIMES")
    safe_print("%6s" % "size", end=" | ")

    for name in sorted(names):
        safe_print("%s" % names[name], end=" | ")
    safe_print()

    for i, size in enumerate(sizes):
        n = int(np.floor(size / 2))
        safe_print("%6i" % n, end=" | ")

        for name in sorted(names):
            t = times[names[name]][i]
            m, s = divmod(t, 60)
            safe_print("%5d:%02d" % (m, s), end=" | ")
        safe_print()

    times = pd.DataFrame(times)
    scores = pd.DataFrame(scores)
