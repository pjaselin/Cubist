import pandas as pd
from sklearn.datasets import load_boston
from cubist import Cubist

X, y = load_boston(return_X_y=True)

model = Cubist(X, y)

