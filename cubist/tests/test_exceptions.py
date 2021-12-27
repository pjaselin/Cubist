import pytest
import pandas as pd

from ..cubist import Cubist, CubistError

X_train = pd.DataFrame([0.803949,0.792776,0.698957,0.889468,0.898589,0.780680,0.763039,0.733734,0.880098,0.749216,0.772409,0.397889,0.569687,0.863047,0.901520,0.903672,0.850031,0.967257,0.924921],columns=['X'])
y_train = [9.101007550426122, 10.105041400955075, 9.665428777858954, 11.108833294273804, 10.543686195210283, 10.041306334130462, 10.29213332885503, 10.229124133661102, 10.793787318304165, 9.726502315371054, 10.102863786063018, 7.843001261439629, 9.474707491805574, 10.290439628383432, 11.106171764961289, 11.73360218758805, 11.607825754410422, 11.168213131314303, 11.230738412087772]
X_predict = pd.DataFrame([0.795757],columns=['X'])

def test_cubist_error():
    with pytest.raises(CubistError):
        tree = Cubist(n_committees=5, n_rules=500, neighbors=None, unbiased=False, composite=False, extrapolation=0.05, sample=0.1, cv=None, target_label="outcome", random_state=1, verbose=0)
        tree.fit(X_train, y_train)
        tree.predict(X_predict)
