"""Visualization class for the Cubist Coverage Display"""

import math
import operator

import pandas as pd

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
    """Visualization of the regression coefficients used in the Cubist model.

    This tool can display "residuals vs predicted" or "actual vs predicted"
    using scatter plots to qualitatively assess the behavior of a regressor,
    preferably on held-out data points.

    See the details in the docstrings of
    :func:`~cubist.CubistCoefficientDisplay.from_estimator`to
    create a visualizer. All parameters are stored as attributes.

    .. versionadded:: 1.0.0

    Parameters
    ----------
    coeffs : Pandas DataFrame of shape (n_samples,)
        True values.

    Attributes
    ----------
    ax_ : matplotlib Axes
        Axes with the different matplotlib axis.

    figure_ : matplotlib Figure
        Figure containing the scatter and lines.

    See Also
    --------
    CubistCoefficientDisplay.from_estimator : Plot the coefficients used in the
        Cubist model.

    Examples
    --------
    >>> import matplotlib.pyplot as plt
    >>> from sklearn.datasets import load_diabetes
    >>> from sklearn.linear_model import Ridge
    >>> from sklearn.metrics import PredictionErrorDisplay
    >>> X, y = load_diabetes(return_X_y=True)
    >>> ridge = Ridge().fit(X, y)
    >>> y_pred = ridge.predict(X)
    >>> display = PredictionErrorDisplay(y_true=y, y_pred=y_pred)
    >>> display.plot()
    <...>
    >>> plt.show()
    """

    def __init__(self, *, splits: pd.DataFrame):
        self.splits = splits
        self.ax_ = None
        self.figure_ = None

    def plot(
        self,
        ax=None,
        *,
        ylabel: str = None,
        gridspec_kwargs: dict = None,
        line_kwargs: dict = None,
    ):
        """Plot visualization.

        Parameters
        ----------
        ax : matplotlib axes, default=None
            Axes object to plot on. If `None`, a new figure and axes is
            created.

        ylabel : str, default=None
            Y-axis label for plot.

        **gridspec_kwargs : dict
            Additional keywords arguments passed to matplotlib
            `matplotlib.pyplot.subplots` function.

        **line_kwargs : dict
            Additional keywords arguments passed to matplotlib
            `matplotlib.pyplot.plot` function.

        Returns
        -------
        display : :class:`~cubist.CubistCoefficientDisplay`
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
                # use blue for less than plot and set x points as 0 to some value
                if "<" in row["dir"]:
                    x = [0, row["percentile"]]
                    color = "#1E88E5"
                # use red for greater than plot and set x points as some value to 1
                else:
                    x = [1 - row["percentile"], 1]
                    color = "#ff0d57"
                # plot line
                self.ax_[i].plot(
                    x, [row["label"], row["label"]], color=color, **line_kwargs
                )
                # set the subplot title
                self.ax_[i].set_title(var)
                # set the x-axis limits of the subplot
                self.ax_[i].set_xlim([-0.05, 1.05])

        # turn off any unused plots
        for j in range(i + 1, self.ax_.shape[0]):  # noqa W0631, pylint: disable=W0631
            self.ax_[j].set_axis_off()

        self.figure_.supxlabel("Data Coverage")
        self.figure_.supylabel(ylabel)
        self.figure_.suptitle(f"Data Coverage by {ylabel} and Variable")

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
        """Plot the coefficients used in the Cubist model.

        For general information regarding `scikit-learn` visualization tools,
        read more in the :ref:`Visualization Guide <visualizations>`.
        For details regarding interpreting these plots, refer to the
        :ref:`Model Evaluation Guide <visualization_regression_evaluation>`.

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

        scatter_kwargs : dict, default=None
            Dictionary with keywords passed to the `matplotlib.pyplot.scatter`
            call.

        gridspec_kwargs : dict, default=None
            Dictionary with keyword passed to the `matplotlib.pyplot.subplots`
            call to configure the subplot.

        Returns
        -------
        display : :class:`~cubist.CubistCoefficientDisplay`
            Object that stores the computed values.

        See Also
        --------
        CubistCoefficientDisplay :

        Examples
        --------
        >>> from sklearn.datasets import load_diabetes
        >>> from cubist import Cubist, CubistCoefficientDisplay
        >>> X, y = load_diabetes(return_X_y=True)
        >>> model = Cubist().fit(X, y)
        >>> disp = CubistCoefficientDisplay.from_estimator(model)
        >>> plt.show()
        """
        df = estimator.splits_.copy()

        # get rows that are continuous-type splits
        df = df.loc[df.type == "continuous"]

        # remove missing values based on the variable column
        df = df.dropna(subset=["variable"]).reset_index(drop=True)

        # get the percentage of data covered by each rule
        for i in range(df.shape[0]):
            # get the current value threshold and comparison operator
            var_value = df.loc[i, "value"]
            comp_operator = df.loc[i, "dir"]
            if (var_value is not None) and (not math.isnan(var_value)):
                # convert the data to numeric and remove NaNs
                x_col = pd.to_numeric(X[df.loc[i, "variable"]]).dropna()
                # evaluate and get the percentage of data
                df.loc[i, "percentile"] = (
                    OPERATORS[comp_operator](x_col, var_value).sum() / X.shape[0]
                )

        # if none of the rows were continuous-type splits, break here
        if df.empty:
            raise ValueError(
                "No splits of continuous predictors were used in this model"
            )

        df, ylabel = cls._validate_from_estimator_params(
            df=df, committee=committee, rule=rule
        )

        viz = cls(splits=df)

        return viz.plot(
            ax=ax,
            ylabel=ylabel,
            line_kwargs=line_kwargs,
            gridspec_kwargs=gridspec_kwargs,
        )
