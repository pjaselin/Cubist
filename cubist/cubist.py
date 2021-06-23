from random import randint
import numpy as np
import pandas as pd
import warnings
from ._make_names_file import make_names_file
from ._make_data_file import make_data_file
from _cubist import _cubist, _predictions
import re
from ._parse_cubist_model import get_splits, get_percentiles
from ._var_usage import var_usage


class Cubist:
    def __init__(self,
                 committees: int = 1,
                 unbiased: bool = False,
                 rules: int = 100,
                 extrapolation: int = 100,
                 sample: float = 0.0,
                 seed: int = randint(0, 4095),  # TODO fix this since its different from R
                 label: str = "outcome",
                 weights=None,
                 **kwargs):
        assert committees > 1 or committees < 100, "number of committees must be between 1 and 100"
        self.committees = committees

        self.unbiased = unbiased

        assert rules is not None and (rules > 1 or rules < 1000000), "number of rules must be between 1 and 1000000"
        self.rules = rules

        assert extrapolation > 0 or extrapolation < 100, "percent extrapolation must be between 0 and 100"
        self.extrapolation = extrapolation / 100

        assert sample > 0.0 or sample < 99.9, "sampling percentage must be between 0.0 and 99"
        self.sample = sample / 100

        self.seed = seed % 4095

        self.label = label

        assert weights is None or isinstance(weights, (list, np.ndarray)), "case weights must be numeric"
        self.weights = weights

    def __repr__(self):
        return f'{self.__class__.__name__}(x, y, committees={self.committees}, unbiased={self.unbiased}, ' \
               f'rules={self.rules}, extrapolation={self.extrapolation}, sample={self.sample}, seed={self.seed}, ' \
               f'label={self.label}, weights)'

    def fit(self, x, y):
        assert isinstance(y, (list, pd.Series, np.ndarray)), "cubist models require a numeric outcome"
        if not isinstance(y, pd.Series):
            y = pd.Series(y)

        assert isinstance(x, (pd.DataFrame, np.ndarray)), "x must be a Numpy Array or a Pandas DataFrame"
        if isinstance(x, np.ndarray):
            assert len(x.shape) == 2, "Input NumPy array has more than two dimensions, only a two dimensional matrix " \
                                      "may be passed."
            warnings.warn("Input data is a NumPy Array, setting column names to default `var0, var1,...`.")
            x = pd.DataFrame(x, columns=[f'var{i}' for i in range(x.shape[1])])

        # for safety ensure the indices are reset
        x = x.reset_index(drop=True)
        y = y.reset_index(drop=True)

        # create the names and data strings required for cubist
        names_string = make_names_file(x, y, w=self.weights, label=self.label, comments=True)
        data_string = make_data_file(x, y, w=self.weights)

        # call the C implementation of cubist
        model, output = _cubist(names_string.encode(),
                                data_string.encode(),
                                self.unbiased,
                                b"yes",
                                1,
                                self.committees,
                                self.sample,
                                self.seed,
                                self.rules,
                                self.extrapolation,
                                b"1",
                                b"1")
        
        # convert output to strings
        model = model.decode()
        output = output.decode()
        
        # correct reserved names
        has_reserved = re.search("\n__Sample", names_string)
        if has_reserved:
            output = output.replace("__Sample", "sample")
            model = model.replace("__Sample", "sample")
        
        # get a dataframe containing the rule s[;ots]
        splits = get_splits(model)
        # get the rule by rule percentiles (?)
        if splits is not None:
            nrows = x.shape[0]
            for i in range(splits.shape[0]):
                x_col = pd.to_numeric(x[splits.loc[i, "variable"]])
                var =  splits.loc[i, "value"]
                splits.loc[i, "percentile"] = get_percentiles(x_col, var, nrows)
        
        # extract the maxd value and remove the preceding text from the model string
        tmp = model.split("\n")
        tmp = [c for c in tmp if "maxd" in c][0]
        tmp = tmp.split("\"")
        maxd_i = [i for i, c in enumerate(tmp) if "maxd" in c][0]
        maxd = tmp[maxd_i + 1]
        model = model.replace(f'insts=\"1\" nn=\"1\" maxd=\"{maxd}\"', 'insts=\"0\"')
        maxd = float(maxd)

        usage = var_usage(output)

    def predict(new_data, neighbors=0, **kwargs):
        assert new_data is not None, "newdata must be non-null"
        return


