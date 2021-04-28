import pandas as pd
from sklearn.datasets import load_boston
# from cubist import Cubist
from cubist.quinlan_attributes import quinlan_attributes
iris = pd.read_csv('https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv')

X, y = load_boston(return_X_y=True)

# model = Cubist(X, y)

print(quinlan_attributes(iris))
print(quinlan_attributes(5.0))
