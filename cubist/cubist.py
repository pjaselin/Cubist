"""Main Cubist estimator class"""

import zlib
from warnings import warn
from numbers import Integral

import numpy as np
import pandas as pd
from sklearn.utils.validation import (
    check_is_fitted,
    check_random_state,
    _check_sample_weight,
    validate_data,
)
from sklearn.utils import RegressorTags
from sklearn.utils._param_validation import Interval, RealNotInt
from sklearn.base import RegressorMixin, BaseEstimator, _fit_context

from _cubist import _cubist, _predictions  # noqa E0611 # pylint: disable=E0611

from ._make_names_string import _make_names_string
from ._make_data_string import _make_data_string
from ._parse_model import _parse_model
from ._attribute_usage import _attribute_usage
from .exceptions import CubistError


class Cubist(RegressorMixin, BaseEstimator):  # pylint: disable=R0902
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

    neighbors : int, default=None
        Number between 1 and 9 for how many instances should be used to correct
        the rule-based prediction. If no value is given, Cubist will build a
        rule-based model only. If this value is set, Cubist will create a
        composite model with the given number of neighbors. Regardless of the
        value set, if auto=True, Cubist may override this input and choose a
        different number of neighbors. Please assess the model for the selected
        value for the number of neighbors used.

    unbiased : bool, default=False
        Should unbiased rules be used? Since Cubist minimizes the MAE of the
        predicted values, the rules may be biased and the mean predicted value
        may differ from the actual mean. This is recommended when there are
        frequent occurrences of the same value in a training dataset. Note that
        MAE may be slightly higher.

    auto : bool, default=False
        A value of True allows the algorithm to choose whether to use
        nearest-neighbor corrections and how many neighbors. In this case,
        `neighbors` must be left as None since the input has no bearing on the
        model's behavior. False will leave the choice of whether to use a
        composite model to value passed to the `neighbors` parameter.

    extrapolation : float, default=0.05
        Adjusts how much rule predictions are adjusted to be consistent with
        the training dataset. Recommended value is 5% as a decimal (0.05)

    sample : float, default=None
        Percentage of the data set to be randomly selected for model building
        and held out for model testing. When using this parameter, Cubist will
        report evaluation results on the testing set in addition to the training
        set results.

    cv : int, default=None
        Whether to carry out cross-validation and how many folds to use
        (recommended value is 10 per Quinlan)

    random_state : int, default=None
        An integer to set the random seed for the C Cubist code.

    target_label : str, default="outcome"
        A label for the outcome variable. This is only used for printing rules.

    verbose : int, default=0
        Should the Cubist output be printed?

    Attributes
    ----------
    model_ : str
        The Cubist model string generated by the C code.

    output_ : str
        The Cubist model pretty print summary generated by the C code.

        .. versionadded:: 1.0.0

    feature_importances_ : pd.DataFrame
        Table of how training data variables are used in the Cubist model. The
        first column for "Conditions" shows the approximate percentage of cases
        for which the named attribute appears in a condition of an applicable
        rule, while the second column "Attributes" gives the percentage of cases
        for which the attribute appears in the linear formula of an applicable
        rule.

    n_features_in_ : int
        Number of features seen during :term:`fit`.

    feature_names_in_ : ndarray of shape (`n_features_in_`,)
        Names of features seen during :term:`fit`. Defined only when `X`
        has feature names that are all strings.

    splits_ : pd.DataFrame
        Table of the splits built by the Cubist model for each rule.

    coeff_ : pd.DataFrame
        Table of the regression coefficients found by the Cubist model for each
        rule.

    version_ : str
        The Cubist version with the time of local build/install.

        .. versionadded:: 1.0.0

    feature_statistics_ : pd.DataFrame
        Table of statistics Cubist generated for each input attribute.

        .. versionadded:: 1.0.0

    committee_error_reduction_ : float
        The reduction in error by using committees.

        .. versionadded:: 1.0.0

    n_committees_used_ : int
        Number of committees actually used by Cubist.

        .. versionadded:: 1.0.0

    Examples
    --------
    >>> from cubist import Cubist
    >>> from sklearn.datasets import fetch_california_housing
    >>> from sklearn.model_selection import train_test_split
    >>> X, y = fetch_california_housing(return_X_y=True, as_frame=True)
    >>> X_train, X_test, y_train, y_test = train_test_split(X, y,
                                                            test_size=0.2,
                                                            random_state=42)
    >>> model = Cubist()
    >>> model.fit(X_train, y_train)
    >>> model.predict(X_test)
    >>> model.score(X_test, y_test)
    """

    _parameter_constraints: dict = {
        "n_rules": [Interval(Integral, 1, 1000000, closed="both")],
        "n_committees": [Interval(Integral, 1, 100, closed="both")],
        "neighbors": [Interval(Integral, 1, 9, closed="both"), None],
        "unbiased": ["boolean"],
        "auto": ["boolean"],
        "extrapolation": [Interval(RealNotInt, 0.0, 1.0, closed="both")],
        "sample": [Interval(RealNotInt, 0.0, 1.0, closed="neither"), None],
        "cv": [Interval(Integral, 1, None, closed="neither"), None],
        "random_state": ["random_state"],
        "target_label": [str],
        "verbose": ["verbose"],
    }

    def __sklearn_tags__(self):
        """scikit-learn estimator configuration method (from v1.6.0 onwards)"""
        tags = super().__sklearn_tags__()
        tags.estimator_type = "regressor"
        tags.regressor_tags = RegressorTags(poor_score=True)
        tags.input_tags.allow_nan = True
        tags.input_tags.string = True
        return tags

    def __init__(  # pylint: disable=R0913
        self,
        n_rules: int = 500,
        *,
        n_committees: int = 1,
        neighbors: int = None,
        unbiased: bool = False,
        auto: bool = False,
        extrapolation: float = 0.05,
        sample: float = None,
        cv: int = None,
        random_state: int = None,
        target_label: str = "outcome",
        verbose: int = 0,
    ):
        super().__init__()

        self.n_rules = n_rules
        self.n_committees = n_committees
        self.neighbors = neighbors
        self.unbiased = unbiased
        self.auto = auto
        self.extrapolation = extrapolation
        self.sample = sample
        self.cv = cv
        self.random_state = random_state
        self.target_label = target_label
        self.verbose = verbose

    def _check_neighbors(self):
        # if auto is True but neighbors is set, raise an error
        if self.auto:
            if self.neighbors is not None:
                raise ValueError(
                    "When `auto`=True, `neighbors` should be None as Cubist ",
                    f"will choose this parameter but got {self.neighbors}.",
                )
            return 0
        # default value must be zero even when not used
        if self.neighbors is None:
            return 0
        return self.neighbors

    def _check_composite(self, neighbors):
        # validate the auto parameter
        if self.auto:
            return "auto"
        # if a number of neighbors is given, make a composite model
        if neighbors > 0:
            return "yes"
        return "no"

    def _check_sample(self, num_samples):
        # default value must be 0 if not used
        if self.sample is None:
            return 0
        # check to see if the sample will create a very small dataset
        trained_num_samples = int(round(self.sample * num_samples, 0))
        if trained_num_samples < 10:
            warn(
                f"Sampling a dataset with {num_samples} rows and a "
                f"sampling percent of {self.sample} means Cubist will "
                f"train with {trained_num_samples} rows. This may lead "
                f"to incorrect or failing predictions. Please increase "
                f"or remove the `sample` parameter.\n",
                stacklevel=3,
            )
        return self.sample

    def _check_cv(self):
        # default value must be 0 if not used
        if self.cv is None:
            return 0
        return self.cv

    @_fit_context(prefer_skip_nested_validation=True)
    def fit(self, X, y, sample_weight=None):  # pylint: disable=R0914
        """Build a Cubist regression model from training set (X, y).

        Parameters
        ----------
        X : {array-like} of shape (n_samples, n_features)
            The training input samples. Must have complete column names or none
            provided at all (NumPy arrays will be given names by column index).

        y : array-like of shape (n_samples,)
            The target values (Real numbers in regression).

        sample_weight : array-like of shape (n_samples,)
            Optional vector of sample weights that is the same length as y for
            how much each instance should contribute to the model fit.

        Returns
        -------
        self : object
        """
        # scikit-learn data validation
        X, y = validate_data(
            self,
            X,
            y,
            dtype=None,
            ensure_all_finite="allow-nan",
            y_numeric=True,
            ensure_min_samples=2,
            reset=True,
        )

        # set the feature names if it hasn't already been done
        if not hasattr(self, "feature_names_in_"):
            self.feature_names_in_ = [f"var{i}" for i in range(X.shape[1])]  # noqa W0201, pylint: disable=W0201

        # check to see if any of the feature names are empty
        if any(n == "" or pd.isnull(n) for n in self.feature_names_in_):
            raise ValueError(
                "At least one column is missing unnamed and is NA \
                             or an empty string."
            )

        # check sample weighting
        if sample_weight is not None:
            sample_weight = _check_sample_weight(sample_weight, X)
            self.is_sample_weighted_ = True  # noqa W0201, pylint: disable=W0201
        else:
            self.is_sample_weighted_ = False  # noqa W0201, pylint: disable=W0201

        neighbors = self._check_neighbors()
        composite = self._check_composite(neighbors)
        sample = self._check_sample(X.shape[0])
        cv = self._check_cv()
        random_state = check_random_state(self.random_state)

        # number of input features
        self.n_features_in_ = X.shape[1]  # noqa W0201, pylint: disable=W0201
        # number of outputs is 1 (single output regression)
        self.n_outputs_ = 1  # noqa W0201, pylint: disable=W0201

        # (re)construct a dataframe from X
        X = pd.DataFrame(X, columns=self.feature_names_in_)
        y = pd.Series(y)

        # create the names and data strings required for cubist
        names_string = _make_names_string(X, w=sample_weight, label=self.target_label)
        data_string = _make_data_string(X, y, w=sample_weight)

        # call the C implementation of cubist
        model, output = _cubist(
            namesv_=names_string.encode(),
            datav_=data_string.encode(),
            unbiased_=self.unbiased,
            compositev_=composite.encode(),
            neighbors_=neighbors,
            committees_=self.n_committees,
            sample_=sample,
            seed_=random_state.randint(0, 4095) % 4096,
            rules_=self.n_rules,
            extrapolation_=self.extrapolation,
            cv_=cv,
            modelv_=b"1",
            outputv_=b"1",
        )

        # convert output from raw to strings
        self.model_ = model.decode()  # pylint: disable=W0201
        self.output_ = output.decode()  # pylint: disable=W0201

        # raise Cubist training errors
        if ("***" in self.output_) or ("Error" in self.output_):
            raise CubistError(self.output_)

        # inform user that they may want to use rules only
        if "Recommend using rules only" in self.output_:
            warn(
                "Cubist recommends using rules only (set auto=False)",
                stacklevel=3,
            )

        # print model output if using verbose output
        if self.verbose:
            print(self.output_)

        # if the model returned nothing, we're doing cross-validation so stop
        if self.model_ == "1":
            return self

        # replace "__Sample" with "sample" if this is used in the model
        if "\n_Sample" in names_string:
            self.output_ = self.output_.replace("_Sample", "sample")  # pylint: disable=W0201
            self.model_ = self.model_.replace("_Sample", "sample")  # pylint: disable=W0201
            # clean model string when using reserved sample name
            self.model_ = (  # pylint: disable=W0201
                self.model_[: self.model_.index("sample")]
                + self.model_[self.model_.index("entries") :]
            )

        # when a composite model has not been used, drop the data_string
        if not (
            (composite == "yes")
            or ("nearest neighbors" in self.output_)
            or (neighbors > 0)
        ):
            data_string = "1"

        # compress and save descriptors/data
        self._names_string = zlib.compress(names_string.encode())  # noqa W0201, pylint: disable=W0201
        self._data_string = zlib.compress(data_string.encode())  # noqa W0201, pylint: disable=W0201

        # parse model contents and store useful information
        (  # noqa W0201, pylint: disable=W0201
            self.version_,
            self.splits_,
            self.coeffs_,
            self.feature_statistics_,
            self.committee_error_reduction_,
            self.n_committees_used_,
        ) = _parse_model(self.model_, list(self.feature_names_in_))

        # get the input data variable usage
        self.feature_importances_ = _attribute_usage(  # noqa W0201, pylint: disable=W0201
            self.output_, list(self.feature_names_in_)
        )

        return self

    def predict(self, X):
        """Predict Cubist regression target for X.

        Parameters
        ----------
        X : {array-like} of shape (n_samples, n_features)
            The input samples. Must have complete column names or none
            provided at all (NumPy arrays will be given names by column index).

        Returns
        -------
        y : ndarray of shape (n_samples,)
            The predicted values.
        """
        # make sure the model has been fitted
        check_is_fitted(self)

        # validate input data
        X = validate_data(
            self, X, dtype=None, ensure_all_finite="allow-nan", reset=False
        )

        # (re)construct a dataframe from X
        X = pd.DataFrame(X, columns=self.feature_names_in_)

        # If there are case weights used during training, the C code will expect
        # a column of weights in the new data but the values will be ignored.
        if self.is_sample_weighted_:
            X["case_weight_pred"] = np.nan

        # make data string for predictions
        data_string = _make_data_string(X)

        # get cubist predictions from trained model
        y_hat, output = _predictions(
            data_string.encode(),
            zlib.decompress(self._names_string),
            zlib.decompress(self._data_string),
            self.model_.encode(),
            np.zeros(X.shape[0]),
            b"1",
        )

        # decode output
        if output := output.decode():
            # raise Cubist prediction errors
            if "***" in output or "Error" in output:
                raise CubistError(output)

            # if using verbose mode, print the output
            if self.verbose:
                print(output)

        return y_hat
