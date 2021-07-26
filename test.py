import pandas as pd
from sklearn.datasets import load_boston, load_diabetes, load_linnerud
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from cubist import Cubist
iris = pd.read_csv('https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv')

# titanic = pd.read_csv("sample_data/titanic.csv")

# y = titanic["Fare"]
# X = titanic.drop(["Fare"], axis=1)


y = iris["petal_width"]
X = iris.drop(["petal_width"], axis=1)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
# print(X_train)

model = Cubist()

model.fit(X_train, y_train)


# print(model.predict(X_test))
# print(model.score(X_train, y_train))
# print(model.score(X_test, y_test))

# test = make_data_file(X, y)
# print(test)
# print(model)
