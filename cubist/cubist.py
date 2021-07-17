from random import randint
import numpy as np
import pandas as pd
import warnings
from ._make_names_file import make_names_file
from ._make_data_file import make_data_file
from _cubist import _cubist, _predictions
import re
from ._parse_cubist_model import get_splits, get_percentiles, coef_cubist
from ._var_usage import var_usage


class Cubist:
    """
    Cubist Regression Model

    Parameters
    ----------
    committes
    unbiased
    rules
    extrapolation
    sample
    seed
    label
    weights

    Attributes
    ----------

    Examples
    --------
    >>> from cubist import Cubist
    >>> from sklearn.datasets import 
    >>> from sklearn.model_selection import train_test_split

    """
    def __init__(self,
                 committees: int = 1,
                 unbiased: bool = False,
                 rules: int = 100,
                 extrapolation: int = 1.0,
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

        assert extrapolation >= 0.0 and extrapolation <= 1.0, "extrapolation percentage must be between 0.0 and 1.0"
        self.extrapolation = extrapolation

        assert sample >= 0.0 and sample <= 1.0, "sampling percentage must be between 0.0 and 1.0"
        self.sample = sample

        self.seed = seed % 4095

        self.label = label

        assert weights is None or isinstance(weights, (list, np.ndarray)), "case weights must be numeric"
        self.weights = weights

        # initialize remaining class variables
        self.names = None
        self.data = None
        self.model = None
        self.output = None
        self.maxd = None
        self.usage = None
        self.splits = None
        self.dims = None

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
        self.names = make_names_file(x, y, w=self.weights, label=self.label, comments=True)
        self.data = make_data_file(x, y, w=self.weights)

        # call the C implementation of cubist
        self.model, self.output = _cubist(self.names.encode(),
                                          self.data.encode(),
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
        self.model = self.model.decode()
        self.output = self.output.decode()
        
        # correct reserved __Sample names
        has_reserved = re.search("\n__Sample", self.names)
        if has_reserved:
            self.output = self.output.replace("__Sample", "sample")
            self.model = self.model.replace("__Sample", "sample")
        
        # get a dataframe containing the rule splits
        self.splits = get_splits(self.model)

        # get the rule by rule percentiles (?)
        if self.splits is not None:
            nrows = x.shape[0]
            for i in range(self.splits.shape[0]):
                x_col = pd.to_numeric(x[self.splits.loc[i, "variable"]])
                var = self.splits.loc[i, "value"]
                self.splits.loc[i, "percentile"] = get_percentiles(x_col, var, nrows)
        
        # extract the maxd value and remove the preceding text from the model string
        tmp = self.model.split("\n")
        tmp = [c for c in tmp if "maxd" in c][0]
        tmp = tmp.split("\"")
        maxd_i = [i for i, c in enumerate(tmp) if "maxd" in c][0]
        maxd = tmp[maxd_i + 1]
        self.model = self.model.replace(f'insts=\"1\" nn=\"1\" maxd=\"{maxd}\"', 'insts=\"0\"')
        self.maxd = float(maxd)

        self.usage = var_usage(self.output)
        if self.usage is None or self.usage.shape[0] < x.shape[1]:
            x_names = set(x.columns)
            u_names = set(self.usage["Variable"]) if self.usage is not None else set()
            missing_vars = list(x_names - u_names)
            if missing_vars:
                zero_list = [0] * len(missing_vars)
                usage2 = pd.DataFrame({"Conditions": zero_list,
                                       "Model": zero_list,
                                       "Variable": missing_vars})
                self.usage = pd.concat([self.usage, usage2], axis=1)
                self.usage = self.usage.reset_index(drop=True)
        
        self.dims = x.shape

        # TODO: consider capturing function call as in the R scripts
        coefs = coef_cubist(self.model, var_names=list(x.columns))


    def predict(self, new_data, neighbors=0, **kwargs):
        assert new_data is not None, "newdata must be non-null"

        # newdata
        assert isinstance(neighbors, int), "only a single value of neighbors is allowed"
        assert neighbors <= 10, "'neighbors' must be less than 10"
        if neighbors > 0:
            self.model = self.model.replace("insts=\"0\"",  f"insts=\"1\" nn=\"{neighbors}\" maxd=\"{self.maxd}\"")
        
        # for safety ensure indices are reset
        new_data = new_data.reset_index(drop=True)
        
        ## If there are case weights used during training, the C code
        ## will expect a column of weights in the new data but the
        ## values will be ignored. `makeDataFile` puts those last in
        ## the data when `cubist.default` is run, so we will add a
        ## column of NA values at the end here
        if self.weights:
            new_data["case_weight_pred"] = None
        
        # make cases file
        case_string = make_data_file(x=new_data, y=None)
        # print(case_string)

        # fix breaking predictions when using sample parameter
        case_model = "" if "sample" in self.model else self.model

        # get cubist predictions from trained model
        pred, output = _predictions(case_string.encode(),
                                    self.names.encode(),
                                    self.data.encode(),
                                    case_model.encode(),
                                    np.zeros(new_data.shape[0]),
                                    b"1")
        pred = pred.tolist()
        return pred
