import zlib
from warnings import warn
from typing import Type, Union

import numpy as np
import pandas as pd

from sklearn.utils.validation import check_is_fitted, check_random_state, \
    _check_sample_weight
from sklearn.base import RegressorMixin, BaseEstimator

from ._make_names_string import make_names_string
from ._make_data_string import make_data_string
from ._parse_model import parse_model
from ._variable_usage import get_variable_usage
from _cubist import _cubist, _predictions


class Cubist(BaseEstimator, RegressorMixin):
    """
    Cubist Regression Model (Public v2.07) developed by Quinlan.

    References:
    - https://www.rdocumentation.org/packages/Cubist/versions/0.3.0
    - https://www.rulequest.com/cubist-unix.html

    Parameters
    ----------
    n_rules : int, default=500
        Limit of the number of rules Cubist will build. Recommended and default
        value is 500.

    n_committees : int, default=1
        Number of committees to construct. Each committee is a rule based model 
        and beyond the first tries to correct the prediction errors of the prior 
        constructed model. Recommended value is 5.

    neighbors : int or None, default=None
        Number between 1 and 9 for how many instances should be used to correct 
        the rule-based prediction. Only used when composite is True or 'auto'. 
        If neighbors=0 and composite=False or 'auto', Cubist will choose a value
        for this parameter.

    unbiased : bool, default=False
        Should unbiased rules be used? Since Cubist minimizes the MAE of the 
        predicted values, the rules may be biased and the mean predicted value 
        may differ from the actual mean. This is recommended when there are 
        frequent occurrences of the same value in a training dataset. Note that 
        MAE may be slightly higher.
    
    composite : bool or 'auto', default=False
        A composite model is a combination of Cubist's rule-based model and 
        instance-based or nearest-neighbor models to improve the predictive
        performance of the returned model. A value of True requires Cubist to
        include the nearest-neighbor model, False will ensure Cubist only
        generates a rule-based model, and 'auto' allows the algorithm to choose
        whether to use nearest-neighbor corrections.

    extrapolation : float, default=0.05
        Adjusts how much rule predictions are adjusted to be consistent with 
        the training dataset. Recommended value is 5% as a decimal (0.05)

    sample : float, default=None
        Percentage of the data set to be randomly selected for model building.
    
    cv : int or None, default=None
        Whether to carry out cross-validation (recommended value is 10)

    random_state : int, default=None
        An integer to set the random seed for the C Cubist code.

    target_label : str, default="outcome"
        A label for the outcome variable. This is only used for printing rules.

    verbose : int, default=0
        Should the Cubist output be printed?

    Attributes
    ----------
    names_string_ : str
        String for the Cubist model that describes the training dataset column 
        names and their data types. This also provides some Python environment 
        information.
    
    data_string_ : str
        String containing the training data. Required for using instance-based
        corrections and compressed after model training.

    model_ : str
        The Cubist model string generated by the C code.

    feature_importances_ : pd.DataFrame
        Table of how training data variables are used in the Cubist model. The 
        first column for "Conditions" shows the approximate percentage of cases 
        for which the named attribute appears in a condition of an applicable 
        rule, while the second column "Attributes" gives the percentage of cases 
        for which the attribute appears in the linear formula of an applicable 
        rule.

    rules_ : pd.DataFrame
        Table of the rules built by the Cubist model.

    coeff_ : pd.DataFrame
        Table of the regression coefficients found by the Cubist model.

    variables_ : dict
        Information about all the variables passed to the model and those that 
        were actually used.

    Examples
    --------
    >>> from cubist import Cubist
    >>> from sklearn.datasets import fetch_california_housing
    >>> from sklearn.model_selection import train_test_split
    >>> X, y = fetch_california_housing(return_X_y=True, as_frame=True)
    >>> X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    >>> model = Cubist()
    >>> model.fit(X_train, y_train)
    >>> model.predict(X_test)
    >>> model.score(X_test, y_test)
    """

    def __init__(self,
                 n_rules: int = 500,
                 *,
                 n_committees: int = 1,
                 neighbors: int = None,
                 unbiased: bool = False,
                 composite: Union[bool, str] = False,
                 extrapolation: float = 0.05,
                 sample: float = None,
                 cv: int = None,
                 random_state: int = None,
                 target_label: str = "outcome",
                 verbose: int = 0):
        super().__init__()

        self.n_rules = n_rules
        self.n_committees = n_committees
        self.neighbors = neighbors
        self.unbiased = unbiased
        self.composite = composite
        self.extrapolation = extrapolation
        self.sample = sample
        self.cv = cv
        self.random_state = random_state
        self.target_label = target_label
        self.verbose = verbose
    
    def _more_tags(self):
        return {"allow_nan": True,
                "X_types": ["2darray", "string"]}
    
    def _validate_model_parameters(self):
        """Validate inputs to the Cubist model

        Raises:
            ValueError for invalid model parameter inputs
        """
        if not isinstance(self.n_rules, int):
            raise TypeError("Number of rules must be an integer")
        elif self.n_rules < 1 or self.n_rules > 1000000:
            raise ValueError("Number of rules must be between 1 and 1000000")

        if not isinstance(self.n_committees, int):
            raise TypeError("Number of committees must be an integer")
        elif self.n_committees < 1 or self.n_committees > 100:
            raise ValueError("Number of committees must be 1 or greater")
        
        if self.neighbors:
            if self.composite is False:
                raise ValueError("`neighbors` should not be set when `composite` is False")
            elif not isinstance(self.neighbors, int):
                raise TypeError("Number of neighbors must be an integer")
            elif self.neighbors < 1 or self.neighbors > 9:
                raise ValueError("'neighbors' must be between 1 and 9")
            else:
                self.neighbors_ = self.neighbors
        else:
            self.neighbors_ = 0
        
        if self.composite not in [True, False, 'auto']:
            raise ValueError(f"Wrong input for parameter `composite`. Expected True, False, or 'auto', got {self.composite}")
        else:
            if self.composite is True:
                self.composite_ = 'yes'
            elif self.composite is False:
                self.composite_ = 'no'
            else:
                self.composite_ = 'auto'

        if not isinstance(self.extrapolation, float):
            raise TypeError("Extrapolation percentage must be a float")
        elif self.extrapolation < 0.0 or self.extrapolation > 1.0:
            raise ValueError("Extrapolation percentage must be between 0.0 and 1.0")

        if self.sample:
            if not isinstance(self.sample, float):
                raise TypeError("Sampling percentage must be a float")
            if self.sample < 0.0 or self.sample >= 1.0:
                raise ValueError("Sampling percentage must be between 0.0 and 1.0")
            self.sample_ = self.sample
        else:
            self.sample_ = 0.0
        
        if not isinstance(self.cv, (int, type(None))):
            raise TypeError("Number of cross-validation folds must be an integer or None")
        if isinstance(self.cv, int):
            if self.cv <= 1 and self.cv != 0:
                raise ValueError("Number of cross-validation folds must be greater than 1")
            else:
                self.cv_ = self.cv
        else:
            self.cv_ = 0

    def fit(self, X, y, sample_weight = None):
        """Build a Cubist regression model from training set (X, y).

        Parameters
        ----------
        X : {array-like} of shape (n_samples, n_features)
            The training input samples.

        y : array-like of shape (n_samples,)
            The target values (Real numbers in regression).

        sample_weight : array-like of shape (n_samples,)
            Optional vector of sample weights that is the same length as y for 
            how much each instance should contribute to the model fit.

        Returns
        -------
        self : object
        """
        # get column name from y if it is a Pandas Series
        if isinstance(y, pd.Series):
            target_label_ = y.name
        else:
            target_label_ = None

        # scikit-learn checks
        X, y = self._validate_data(X, y, 
                                   dtype=None,
                                   force_all_finite='allow-nan', 
                                   y_numeric=True,
                                   ensure_min_samples=2)
        
        # set the feature names if it hasn't already been done
        if not hasattr(self, "feature_names_in_"):
            self.feature_names_in_ = [f'var{i}' for i in range(X.shape[1])]
        
        # check sample weighting
        if sample_weight is not None:
            sample_weight = _check_sample_weight(sample_weight, X)
            self.is_sample_weighted_ = True
        else:
            self.is_sample_weighted_ = False
        
        # validate model parameters
        self._validate_model_parameters()
        
        self.n_features_in_ = X.shape[1]
        self.n_outputs_ = 1

        # (re)construct a dataframe from X
        X = pd.DataFrame(X, columns=self.feature_names_in_)
        y = pd.Series(y)

        random_state = check_random_state(self.random_state)

        # if a Pandas series wasn't used or it has no name,
        # use the passed target_label feature, otherwise use
        # the name of the Pandas series
        self.target_label_ = target_label_ or self.target_label

        # create the names and data strings required for cubist
        names_string = make_names_string(X, w=sample_weight,
                                         label=self.target_label_)
        data_string = make_data_string(X, y, w=sample_weight)
        
        # call the C implementation of cubist
        model, output = _cubist(namesv_=names_string.encode(),
                                datav_=data_string.encode(),
                                unbiased_=self.unbiased,
                                compositev_=self.composite_.encode(),
                                neighbors_=self.neighbors_,
                                committees_=self.n_committees,
                                sample_=self.sample_,
                                seed_=random_state.randint(0, 4095) % 4096,
                                rules_=self.n_rules,
                                extrapolation_=self.extrapolation,
                                cv_=self.cv_,
                                modelv_=b"1",
                                outputv_=b"1")

        # convert output from raw to strings
        self.model_ = model.decode()
        output = output.decode()

        # raise cubist errors
        if "Error" in output:
            raise Exception(output)
        
        # inform user that they may want to use rules only
        if "Recommend using rules only" in output:
            warn("Cubist recommends using rules only (i.e. set composite=False)")

        # print model output if using verbose output
        if self.verbose:
            print(output)
        
        # if the model returned nothing, we're doing cross-validation so stop
        if self.model_ == "1":
            return self

        # replace "__Sample" with "sample" if this is used in the model
        if "\n__Sample" in names_string:
            output = output.replace("__Sample", "sample")
            self.model_ = self.model_.replace("__Sample", "sample")
            # clean model string when using reserved sample name
            self.model_ = self.model_[:self.model_.index("sample")] + \
                          self.model_[self.model_.index("entries"):]
        
        # compress and save descriptors
        self.names_string_ = zlib.compress(names_string.encode())

        # TODO: check to see when a composite model has been used
        # compress and save training data if using a composite model
        if self.composite is True or "nearest neighbors" in output \
            or self.neighbors_ > 0:
            self.data_string_ = zlib.compress(data_string.encode())

        # parse model contents and store useful information
        self.rules_, self.coeff_ = parse_model(self.model_, X)

        # get the input data variable usage
        self.feature_importances_ = get_variable_usage(output, X)

        # get the names of columns that have no nan values
        is_na_col = ~self.coeff_.isna().any()
        not_na_cols = self.coeff_.columns[is_na_col].tolist()

        # skip the first three since these are always filled
        not_na_cols = not_na_cols[3:]

        # store a dictionary containing all the training dataset columns and 
        # those that were used by the model
        if self.rules_ is not None:
            used_variables = set(self.rules_["variable"]).union(
                set(not_na_cols)
            )
            self.variables_ = {"all": list(X.columns),
                               "used": list(used_variables)}
        return self

    def predict(self, X):
        """Predict Cubist regression target for X.

        Parameters
        ----------
        X : {array-like} of shape (n_samples, n_features)
            The input samples.

        Returns
        -------
        y : ndarray of shape (n_samples,)
            The predicted values.
        """
        # make sure the model has been fitted
        check_is_fitted(self, attributes=["model_", "rules_", "coeff_", 
                                          "feature_importances_"])

        # validate input data
        X = self._validate_data(X, 
                                dtype=None, 
                                force_all_finite='allow-nan', 
                                reset=False)

        # (re)construct a dataframe from X
        X = pd.DataFrame(X, columns=self.feature_names_in_)

        # If there are case weights used during training, the C code will expect 
        # a column of weights in the new data but the values will be ignored.
        if self.is_sample_weighted_:
            X["case_weight_pred"] = np.nan

        # make data string for predictions
        data_string = make_data_string(X)

        # if a composite model was used, get the training data
        if hasattr(self, "data_string_"):
            training_data_string = zlib.decompress(self.data_string_)
        else:
            training_data_string = b"1"
        
        # get cubist predictions from trained model
        pred, output = _predictions(data_string.encode(),
                                    zlib.decompress(self.names_string_),
                                    training_data_string,
                                    self.model_.encode(),
                                    np.zeros(X.shape[0]),
                                    b"1")

        # TODO: parse and handle errors in output
        if output:
            print(output.decode())
        return pred
