"""Visualization class for the Cubist Coverage Display"""

import operator

import pandas as pd
from sklearn.utils.validation import check_is_fitted

from .cubist import Cubist
from ._cubist_display_mixin import _CubistDisplayMixin


OPERATORS = {
    "<": operator.lt,
    "<=": operator.le,
    ">": operator.gt,
    ">=": operator.ge,
    "==": operator.eq,
}


class CubistCoverageDisplay(_CubistDisplayMixin):
    """Visualization of rule split coverage for input variables for a trained Cubist
    model.

    This tool plots the percents and ranges (coverage) per rule of input
    variables from a given dataset. One subplot is created for each variable
    used to make splits with the rule number or committee/rule pair on the
    y-axis. The coverage percentages for the given variable and rule pair or
    variable and committee/rule pair are plotted along the x-axis.

    See the details in the docstrings of
    :func:`~cubist.CubistCoefficientDisplay.from_estimator`to
    create a visualizer. All parameters are stored as attributes.

    .. versionadded:: 1.0.0

    Parameters
    ----------
    splits : pd.DataFrame
        DataFrame containing the model split values by variable,
        committee, and rule.

    Attributes
    ----------
    ax_ : matplotlib Axes
        Axes with the different matplotlib axis.

    figure_ : matplotlib Figure
        Figure containing the scatter and lines.

    See Also
    --------
    CubistCoverageDisplay.from_estimator : Cubist input variable coverage
        visualization.

    Examples
    --------
    >>> import matplotlib.pyplot as plt
    >>> from sklearn.datasets import load_iris
    >>> from cubist import Cubist, CubistCoverageDisplay
    >>> X, y = load_iris(return_X_y=True, as_frame=True)
    >>> model = Cubist(n_rules=2).fit(X, y)
    >>> display = CubistCoverageDisplay.from_estimator(estimator=model)
    <...>
    >>> plt.show()
    """

    def __init__(self, *, splits: pd.DataFrame):
        self.splits = splits
        self.ax_ = None
        self.figure_ = None

    def plot(  # pylint: disable=R0913
        self,
        ax=None,
        y_label_map: dict = None,
        *,
        y_axis_label: str = None,
        gridspec_kwargs: dict = None,
        line_kwargs: dict = None,
    ):
        """Plot visualization.

        Extra keyword arguments will be passed to matplotlib's ``subplots`` and
        ``plot``.

        Parameters
        ----------
        ax : matplotlib axes, default=None
            Axes object to plot on. If `None`, a new figure and axes is
            created.

        y_label_map : dict, default=None
            Dictionary mapping ordered value to the y-axis tick label so that
            matplotlib correctly orders committee/rule pairs in addition to rule
            numbers along the y-axis.

        y_axis_label : str, default=None
            Y-axis label for plot.

        **gridspec_kwargs : dict
            Additional keywords arguments passed to matplotlib
            `matplotlib.pyplot.subplots` function.

        **line_kwargs : dict
            Additional keywords arguments passed to matplotlib
            `matplotlib.pyplot.plot` function.

        Returns
        -------
        display : :class:`~cubist.CubistCoverageDisplay`
            Object that stores computed values.
        """
        self.figure_, self.ax_ = self._validate_plot_params(
            ax=ax, df=self.splits, gridspec_kwargs=gridspec_kwargs
        )

        if line_kwargs is None:
            line_kwargs = {}

        for i, var in enumerate(list(self.splits.variable.unique())):
            # get the data for the current variable/subplot
            data = self.splits.loc[self.splits.variable == var]
            # add gray trellis lines
            for label in sorted(list(data.label.unique())):
                self.ax_[i].plot([0, 1], [label, label], color="#e9e9e9", zorder=0)
            # plot data
            for _, row in data.iterrows():
                # plot line
                self.ax_[i].plot(
                    [row["x0"], row["x1"]],
                    [row["label"], row["label"]],
                    color=row["color"],
                    **line_kwargs,
                )
                # set the subplot title
                self.ax_[i].set_title(var)
                # set the x-axis limits of the subplot
                self.ax_[i].set_xlim([-0.05, 1.05])
                # set the y-axis tick labels
                self.ax_[i].set_yticks(
                    list(y_label_map.keys()), list(y_label_map.values())
                )

        # turn off any unused plots
        for j in range(i + 1, self.ax_.shape[0]):  # noqa W0631, pylint: disable=W0631
            self.ax_[j].set_axis_off()

        self.figure_.supxlabel("Data Coverage")
        self.figure_.supylabel(y_axis_label)
        self.figure_.suptitle(f"Data Coverage by {y_axis_label} and Variable")

        return self

    @classmethod
    def from_estimator(  # pylint: disable=R0913
        cls,
        estimator: Cubist,
        X,
        *,
        committee: int = None,
        rule: int = None,
        ax=None,
        line_kwargs=None,
        gridspec_kwargs=None,
    ):
        """Plot the input variable coverage for rules used in the Cubist model.

        .. versionadded:: 1.0.0

        Parameters
        ----------
        estimator : Cubist instance
            Fitted Cubist regressor.

        X : array-like of shape (n_samples, n_features)
            Training data, where `n_samples` is the number of samples and
            `n_features` is the number of features.

        committee : int
            Max committee number to be included in plot.

        rule : int
            Max rule number to be included in plot.

        ax : matplotlib axes, default=None
            Axes object to plot on. If `None`, a new figure and axes is
            created.

        line_kwargs : dict, default=None
            Dictionary with keywords passed to the `matplotlib.pyplot.plot`
            call.

        gridspec_kwargs : dict, default=None
            Dictionary with keyword passed to the `matplotlib.pyplot.subplots`
            call to configure the subplot.

        Returns
        -------
        display : :class:`~cubist.CubistCoverageDisplay`
            Object that stores the computed values.

        See Also
        --------
        CubistCoverageDisplay : Cubist input variable coverage visualization.

        Examples
        --------
        >>> import matplotlib.pyplot as plt
        >>> from sklearn.datasets import load_iris
        >>> from cubist import Cubist, CubistCoverageDisplay
        >>> X, y = load_iris(return_X_y=True, as_frame=True)
        >>> model = Cubist(n_rules=2).fit(X, y)
        >>> display = CubistCoverageDisplay.from_estimator(estimator=model)
        <...>
        >>> plt.show()
        """
        check_is_fitted(estimator)

        df = estimator.splits_.copy()

        # get rows that are continuous-type splits
        df = df.loc[df.type == "continuous"]

        # remove missing values based on the variable column
        df = df.dropna(subset=["variable"]).reset_index(drop=True)

        # if none of the rows were continuous-type splits, break here
        if df.empty:
            raise ValueError(
                "No splits of continuous predictors were used in this model"
            )

        def _get_coverage(x):
            split_coverage = []
            for var in list(x.variable.unique()):
                current_splits = x.loc[x.variable == var]

                if current_splits.shape[0] > 1:
                    lower_split = current_splits.loc[
                        current_splits.dir.str.contains("<")
                    ].to_records()[0]
                    # get the current value threshold and comparison operator
                    var_value = lower_split["value"]
                    comp_operator = lower_split["dir"]
                    # convert the data to numeric and remove NaNs
                    x_col = pd.to_numeric(X[lower_split["variable"]]).dropna()
                    # evaluate and get the percentage of data
                    lower_percentile = (
                        OPERATORS[comp_operator](x_col, var_value).sum() / X.shape[0]
                    )
                    upper_split = current_splits.loc[
                        current_splits.dir.str.contains(">")
                    ].to_records()[0]
                    # get the current value threshold and comparison operator
                    var_value = upper_split["value"]
                    comp_operator = upper_split["dir"]
                    # convert the data to numeric and remove NaNs
                    x_col = pd.to_numeric(X[upper_split["variable"]]).dropna()
                    # evaluate and get the percentage of data
                    upper_percentile = (
                        OPERATORS[comp_operator](x_col, var_value).sum() / X.shape[0]
                    )
                    split_coverage.append(
                        {
                            "variable": var,
                            "color": "#EE7733",
                            "x0": lower_percentile,
                            "x1": upper_percentile,
                        }
                    )
                    continue
                current_splits = current_splits.to_records()[0]
                # get the current value threshold and comparison operator
                var_value = current_splits["value"]
                comp_operator = current_splits["dir"]
                # convert the data to numeric and remove NaNs
                x_col = pd.to_numeric(X[current_splits["variable"]]).dropna()
                # evaluate and get the percentage of data
                percentile = (
                    OPERATORS[comp_operator](x_col, var_value).sum() / X.shape[0]
                )
                if "<" in comp_operator:
                    split_coverage.append(
                        {"variable": var, "color": "#0077BB", "x0": 0, "x1": percentile}
                    )
                else:
                    split_coverage.append(
                        {
                            "variable": var,
                            "color": "#33BBEE",
                            "x0": 1 - percentile,
                            "x1": 1,
                        }
                    )

            return pd.DataFrame(split_coverage)

        df = df.groupby(["committee", "rule"]).apply(_get_coverage).reset_index()

        df, y_axis_label, y_label_map = cls._validate_from_estimator_params(
            df=df, committee=committee, rule=rule
        )

        viz = cls(splits=df)

        return viz.plot(
            ax=ax,
            y_label_map=y_label_map,
            y_axis_label=y_axis_label,
            line_kwargs=line_kwargs,
            gridspec_kwargs=gridspec_kwargs,
        )
