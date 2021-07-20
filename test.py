# import pyximport
# pyximport.install()
import pandas as pd
from sklearn.datasets import load_boston
from cubist import Cubist
from cubist._make_data_file import make_data_file
iris = pd.read_csv('https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv')

titanic = pd.read_csv("sample_data/titanic.csv")

# y = titanic["Fare"]
# X = titanic.drop(["Fare"], axis=1)


y = iris["petal_width"]
X = iris.drop(["petal_width"], axis=1)


model = Cubist()

model.fit(X, y)

# test = make_data_file(X, y)
# print(test)
# print(model)

