from random import randint
import numpy as np
import pandas as pd
import warnings
from ._make_names_string import make_names_string
from ._make_data_string import make_data_string
from _cubist import _cubist, _predictions
import re
from ._parse_cubist_model import get_rule_splits, get_percentiles, get_cubist_coefficients, get_maxd_value
from ._variable_usage import get_variable_usage
from sklearn.base import RegressorMixin, BaseEstimator
from abc import ABCMeta


class Cubist(RegressorMixin, BaseEstimator, metaclass=ABCMeta):
    """
    Cubist Regression Model (v2.07)

    Parameters
    ----------
    n_committes
    unbiased
    n_rules
    extrapolation
    sample
    seed
    target_label
    weights

    Attributes
    ----------

    Examples
    --------
    >>> from cubist import Cubist
    >>> from sklearn.datasets import load_boston
    >>> from sklearn.model_selection import train_test_split
    >>> X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    >>> model = Cubist()
    >>> model.fit(X_train, y_train)
    >>> model.predict(X_test)
    >>> model.score(X_test, y_test)

    """
    def __init__(self,
                 n_committees: int = 1,
                 unbiased: bool = False,
                 n_rules: int = 100,
                 extrapolation: int = 1.0,
                 sample: float = 0.0,
                 seed: int = randint(0, 4095),  # TODO fix this since its different from R
                 target_label: str = "outcome",
                 weights=None,
                 verbose: bool=False):
        super().__init__()

        assert n_committees > 1 or n_committees < 100, "number of committees must be between 1 and 100"
        self.n_committees = n_committees

        self.unbiased = unbiased

        assert n_rules is not None and (n_rules > 1 or n_rules < 1000000), "number of rules must be between 1 and 1000000"
        self.n_rules = n_rules

        assert extrapolation >= 0.0 and extrapolation <= 1.0, "extrapolation percentage must be between 0.0 and 1.0"
        self.extrapolation = extrapolation

        assert sample >= 0.0 and sample <= 1.0, "sampling percentage must be between 0.0 and 1.0"
        self.sample = sample

        self.seed = seed % 4095

        self.target_label = target_label

        assert weights is None or isinstance(weights, (list, np.ndarray)), "case weights must be numeric"
        self.weights = weights

        self.verbose = verbose

        # initialize remaining class variables
        self.names_string = None
        self.model = None
        self.maxd = None
        self.variable_usage = None
        self.rule_splits = None
        self.coefficients = None

    def fit(self, X, y):
        assert isinstance(y, (list, pd.Series, np.ndarray)), "Cubist requires a numeric target outcome"
        if not isinstance(y, pd.Series):
            y = pd.Series(y)

        assert isinstance(X, (pd.DataFrame, np.ndarray)), "X must be a Numpy Array or Pandas DataFrame"
        if isinstance(X, np.ndarray):
            assert len(X.shape) == 2, "Input NumPy array has more than two dimensions, only a two dimensional matrix " \
                                      "may be passed."
            warnings.warn("Input data is a NumPy Array, setting column names to default `var0, var1,...`.")
            X = pd.DataFrame(X, columns=[f'var{i}' for i in range(X.shape[1])])

        # for safety ensure the indices are reset
        X = X.reset_index(drop=True)
        y = y.reset_index(drop=True)

        # create the names and data strings required for cubist
        self.names_string = make_names_string(X, w=self.weights, label=self.target_label)
        data_string = make_data_string(X, y, w=self.weights)

        # call the C implementation of cubist
        self.model, output = _cubist(self.names_string.encode(),
                                     data_string.encode(),
                                     self.unbiased,
                                     b"yes",
                                     1,
                                     self.n_committees,
                                     self.sample,
                                     self.seed,
                                     self.n_rules,
                                     self.extrapolation,
                                     b"1",
                                     b"1")
        
        # convert output to strings
        self.model = self.model.decode()
        output = output.decode()
        
        # replace "__Sample" with "sample" if this is used in the model
        if "\n__Sample" in self.names_string:
            output = output.replace("__Sample", "sample")
            self.model = self.model.replace("__Sample", "sample")
        
        # get a dataframe containing the rule splits
        self.rule_splits = get_rule_splits(self.model)

        # get the rule by rule percentiles (?)
        if self.rule_splits is not None:
            nrows = X.shape[0]
            for i in range(self.rule_splits.shape[0]):
                x_col = pd.to_numeric(X[self.rule_splits.loc[i, "variable"]])
                var = self.rule_splits.loc[i, "value"]
                self.rule_splits.loc[i, "percentile"] = get_percentiles(x_col, var, nrows)
        
        # extract the maxd value and remove the preceding text from the model string
        maxd = get_maxd_value(self.model)
        self.model = self.model.replace(f'insts=\"1\" nn=\"1\" maxd=\"{maxd}\"', 'insts=\"0\"')
        self.maxd = float(maxd)

        self.variable_usage = get_variable_usage(output)
        if self.variable_usage is None or self.variable_usage.shape[0] < X.shape[1]:
            x_names = set(X.columns)
            u_names = set(self.variable_usage["Variable"]) if self.variable_usage is not None else set()
            missing_vars = list(x_names - u_names)
            if missing_vars:
                zero_list = [0] * len(missing_vars)
                usage2 = pd.DataFrame({"Conditions": zero_list,
                                       "Model": zero_list,
                                       "Variable": missing_vars})
                self.variable_usage = pd.concat([self.variable_usage, usage2], axis=1)
                self.variable_usage = self.variable_usage.reset_index(drop=True)
        
        self.coefficients = get_cubist_coefficients(self.model, var_names=list(X.columns))
        

        # print model output if using verbose output
        if self.verbose:
            print(output)


    def predict(self, X, neighbors=0):
        assert isinstance(X, (pd.DataFrame, np.ndarray)), "X must be a Numpy Array or Pandas DataFrame"
        if isinstance(X, np.ndarray):
            assert len(X.shape) == 2, "Input NumPy array has more than two dimensions, only a two dimensional matrix " \
                                      "may be passed."
            warnings.warn("Input data is a NumPy Array, setting column names to default `var0, var1,...`.")
            X = pd.DataFrame(X, columns=[f'var{i}' for i in range(X.shape[1])])
        
        # for safety ensure indices are reset
        X = X.reset_index(drop=True)

        assert isinstance(neighbors, int), "Only an integer value for neighbors is allowed"
        assert neighbors <= 10 and neighbors >=0, "'neighbors' must be 0 or greater and 10 or less"
        if neighbors > 0:
            self.model = self.model.replace("insts=\"0\"",  f"insts=\"1\" nn=\"{neighbors}\" maxd=\"{self.maxd}\"")
        
        ## If there are case weights used during training, the C code
        ## will expect a column of weights in the new data but the
        ## values will be ignored. `makeDataFile` puts those last in
        ## the data when `cubist.default` is run, so we will add a
        ## column of NaN values at the end here
        if self.weights:
            X["case_weight_pred"] = np.nan
        
        # make data string for predictions
        data_string = make_data_string(X)

        # clean model string to fix breaking predictions when using reserved sample name
        model = self.model[:self.model.index("sample")] + self.model[self.model.index("entries"):] if "sample" in self.model else self.model

        # get cubist predictions from trained model
        pred, output = _predictions(data_string.encode(),
                                    self.names_string.encode(),
                                    model.encode(),
                                    np.zeros(X.shape[0]),
                                    b"1")
        # TODO: parse and handle errors in output
        return pred
