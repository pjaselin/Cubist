import pyximport
pyximport.install()
import pandas as pd
from sklearn.datasets import load_boston
from cubist import Cubist
from cubist._make_data_file import make_data_file
iris = pd.read_csv('https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv')

y = iris["petal_width"]
X = iris.drop(["petal_width"], axis=1)
X.columns = ["sepal.length", "sepal.width", "petal.length", "species"]
# X, y = load_boston(return_X_y=True)

model = Cubist()

model.fit(X, y)

test = make_data_file(X, y)
print(test)

