from random import randint
import numpy as np
import pandas as pd
from ._make_names_string import make_names_string
from ._make_data_string import make_data_string, validate_x
from _cubist import _cubist, _predictions
from ._parse_cubist_model import get_rule_splits, get_cubist_coefficients, get_maxd_value
from ._variable_usage import get_variable_usage
from sklearn.base import RegressorMixin, BaseEstimator


class Cubist(RegressorMixin, BaseEstimator):
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
    neighbors
    verbose

    Attributes
    ----------
    names_string
    model
    maxd
    variable_usage
    rule_splits
    coefficients
    vars

    Examples
    --------
    >>> from cubist import Cubist
    >>> from sklearn.datasets import load_boston
    >>> from sklearn.model_selection import train_test_split
    >>> X, y = load_boston(return_X_y=True)
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
                 weights = None,
                 neighbors: int = 0,
                 verbose: bool = False):
        super().__init__()

        # initialize instance variables
        self.n_committees = n_committees
        self.unbiased = unbiased
        self.n_rules = n_rules
        self.extrapolation = extrapolation
        self.sample = sample
        self.seed = seed
        self.target_label = target_label
        self.weights = weights
        self.neighbors = neighbors
        self.verbose = verbose

        # initialize remaining instance variables
        self.names_string = None
        self.model = None
        self.maxd = None
        self.variable_usage = None
        self.rule_splits = None
        self.coefficients = None
        self.vars = None
    
    @property
    def n_committees(self):
        return self._n_committees
    
    @n_committees.setter
    def n_committees(self, value):
        assert value > 1 or value < 100, "number of committees must be between 1 and 100"
        self._n_committees = value

    @property
    def n_rules(self):
        return self._n_rules
    
    @n_rules.setter
    def n_rules(self, value):
        assert value is not None and (value > 1 or value < 1000000), "number of rules must be between 1 and 1000000"
        self._n_rules = value

    @property
    def extrapolation(self):
        return self._extrapolation
    
    @extrapolation.setter
    def extrapolation(self, value):
        assert value >= 0.0 and value <= 1.0, "extrapolation percentage must be between 0.0 and 1.0"
        self._extrapolation = value
    
    @property
    def sample(self):
        return self._sample
    
    @sample.setter
    def sample(self, value):
        assert value >= 0.0 and value <= 1.0, "sampling percentage must be between 0.0 and 1.0"
        self._sample = value
    
    @property
    def seed(self):
        return self._seed
    
    @seed.setter
    def seed(self, value):
        self._seed = value % 4095
    
    @property
    def weights(self):
        return self._weights
    
    @weights.setter
    def weights(self, value):
        assert value is None or isinstance(value, (list, np.ndarray)), "case weights must be numeric"
        self._weights = value
    
    @property
    def neighbors(self):
        return self._neighbors
    
    @neighbors.setter
    def neighbors(self, value):
        assert isinstance(value, int), "Only an integer value for neighbors is allowed"
        assert value <= 10 and value >=0, "'neighbors' must be 0 or greater and 10 or less"
        self._neighbors = value


    def fit(self, X, y):
        assert isinstance(y, (list, pd.Series, np.ndarray)), "Cubist requires a numeric target outcome"
        if not isinstance(y, pd.Series):
            y = pd.Series(y)

        # validate input data
        X = validate_x(X)

        # for safety ensure the indices are reset
        X = X.reset_index(drop=True)
        y = y.reset_index(drop=True)

        # get input column names
        X_columns = list(X.columns)

        # create the names and data strings required for cubist
        self.names_string = make_names_string(X, w=self.weights, label=self.target_label)
        data_string = make_data_string(X, y, w=self.weights)
        print(self.names_string)
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
            # replace "__Sample" with "sample"
            output = output.replace("__Sample", "sample")
            self.model = self.model.replace("__Sample", "sample")
            # clean model string to fix breaking predictions when using reserved sample name
            self.model = self.model[:self.model.index("sample")] + self.model[self.model.index("entries"):]
        
        # print model output if using verbose output
        if self.verbose:
            print(output)

        # get a dataframe containing the rule splits
        self.rule_splits = get_rule_splits(self.model, X)
        
        # extract the maxd value and remove the preceding text from the model string
        maxd = get_maxd_value(self.model)
        self.model = self.model.replace(f'insts=\"1\" nn=\"1\" maxd=\"{maxd}\"', 'insts=\"0\"')
        self.maxd = float(maxd)

        # get the input data variable usage
        self.variable_usage = get_variable_usage(output, X)
        
        # get the model coefficients
        self.coefficients = get_cubist_coefficients(self.model, var_names=X_columns)
        
        # get the names of columns that have no nan values
        not_na_cols = self.coefficients.columns[~self.coefficients.isna().any()].tolist()
        # skip the first three since these are always filled
        not_na_cols = not_na_cols[3:]
        if self.rule_splits is not None:
            used_variables = set(self.rule_splits["variable"]).union(
                set(not_na_cols)
            )
            self.vars = {"all": X_columns,
                         "used": list(used_variables)}

    def predict(self, X):
        # validate input data
        X = validate_x(X)
        
        # for safety ensure indices are reset
        X = X.reset_index(drop=True)
        
        if self.neighbors > 0:
            model = self.model.replace("insts=\"0\"",  f"insts=\"1\" nn=\"{self.neighbors}\" maxd=\"{self.maxd}\"")
        else:
            model = self.model
        
        ## If there are case weights used during training, the C code
        ## will expect a column of weights in the new data but the
        ## values will be ignored. `makeDataFile` puts those last in
        ## the data when `cubist.default` is run, so we will add a
        ## column of NaN values at the end here
        if self.weights:
            X["case_weight_pred"] = np.nan
        
        # make data string for predictions
        data_string = make_data_string(X)

        # get cubist predictions from trained model
        pred, output = _predictions(data_string.encode(),
                                    self.names_string.encode(),
                                    model.encode(),
                                    np.zeros(X.shape[0]),
                                    b"1")
        # TODO: parse and handle errors in output
        if output:
            print(output)
        return pred
