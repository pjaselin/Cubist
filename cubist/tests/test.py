import pandas as pd
from sklearn.datasets import load_boston, load_diabetes, load_linnerud
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from xgboost import XGBRegressor
from ..cubist import Cubist
import numpy as np

iris = pd.read_csv('https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv')
y = iris["petal_width"]
X = iris.drop(["petal_width"], axis=1)

model = RandomForestRegressor()
print(X.drop(['species'], axis=1))
model.fit(X.drop(['species'],axis=1),y)

# X, y = load_diabetes(return_X_y=True, as_frame=True)

# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
# model = Cubist(verbose=True)
# model.fit(X, y)


titanic = pd.read_csv("https://raw.githubusercontent.com/mwaskom/seaborn-data/master/raw/titanic.csv")
titanic = titanic.drop(["name", "ticket", "cabin"], axis=1)
y = titanic["fare"]
X = titanic.drop(["fare"], axis=1)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = Cubist(verbose=True)
print(model.fit(X_train, y_train).predict(X_test))

print(model.fit(X_train, y_train, sample_weight=np.ones(y_train.shape[0])).predict(X_test))
print(model.feature_importances_)
# print(model)
# print(model.predict(X_test).tolist())
# print(model.score(X_train, y_train))
# print(model.score(X_test, y_test))

# test = make_data_file(X, y)
# print(test)
# print(model.rule_splits)
# print(model.coefficients)
