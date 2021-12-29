import pandas as pd
from sklearn.model_selection import train_test_split
from cubist import Cubist
import numpy as np
from scipy.stats import pearsonr

from sklearn.datasets import fetch_california_housing
from cubist import Cubist
X, y = fetch_california_housing(return_X_y=True, as_frame=True)

# X, y = load_diabetes(return_X_y=True, as_frame=True)

# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
# model = Cubist(verbose=True)
# model.fit(X, y)

# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = Cubist(composite=False, verbose=True)
model.fit(X, y)
print("score", model.score(X, y))
pred_list = model.predict(X).tolist()

print("pearson", pearsonr(pred_list, y.tolist())[0])
# print(model.data_string_)
# print(model.fit(X_train, y_train, sample_weight=np.ones(y_train.shape[0])).predict(X_test))
# print(model.feature_importances_)
# print(model)
# print(model.predict(X_test).tolist())
# print(model.score(X_train, y_train))
# print(model.score(X_test, y_test))
# print(model)
# test = make_data_file(X, y)
# print(test)
