"""Visualization class for the Cubist Coefficient Display"""

from typing import Any

import pandas as pd
from sklearn.utils._optional_dependencies import check_matplotlib_support
from sklearn.utils.validation import check_is_fitted

from ._cubist_display_mixin import _CubistDisplayMixin
from .cubist import Cubist


class CubistCoefficientDisplay(_CubistDisplayMixin):
    """Visualization of the regression coefficients used in the Cubist model.

    This tool plots the linear coefficients and intercepts created for a Cubist
    model and stored in the `coeffs_` attribute. One subplot is created for each
    variable or intercept with the rule number or committee/rule pair on the
    y-axis. The coefficient values for the given variable and rule pair or
    variable and committee/rule pair are plotted along the x-axis.

    See the details in the docstrings of
    :func:`~cubist.CubistCoefficientDisplay.from_estimator` to
    create a visualizer. All parameters are stored as attributes.

    .. versionadded:: 1.0.0

    Parameters
    ----------
    coeffs : pd.DataFrame
        DataFrame containing the linear model coefficients by variable,
        committee, and rule.

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
    >>> from sklearn.datasets import load_iris
    >>> from cubist import Cubist, CubistCoefficientDisplay
    >>> X, y = load_iris(return_X_y=True, as_frame=True)
    >>> model = Cubist(n_rules=2).fit(X, y)
    >>> display = CubistCoefficientDisplay.from_estimator(estimator=model)
    >>> plt.show()
    """

    def __init__(self, *, coeffs: pd.DataFrame):
        self.coeffs = coeffs
        self.ax_ = None
        self.figure_ = None

    def plot(  # pylint: disable=R0913
        self,
        ax=None,
        y_label_map: dict[str, Any] | None = None,
        *,
        y_axis_label: str | None = None,
        gridspec_kwargs: dict[str, Any] | None = None,
        scatter_kwargs: dict[str, Any] | None = None,
    ):
        """Plot visualization.

        Extra keyword arguments will be passed to matplotlib's ``subplots`` and
        ``scatter``.

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

        **scatter_kwargs : dict
            Additional keywords arguments passed to matplotlib
            `matplotlib.pyplot.scatter` function.

        Returns
        -------
        display : :class:`~cubist.CubistCoefficientDisplay`
            Object that stores computed values.
        """
        check_matplotlib_support(f"{self.__class__.__name__}.plot")
        from matplotlib.ticker import MaxNLocator  # pylint: disable=C0415

        self.figure_, self.ax_ = self._validate_plot_params(
            ax=ax, df=self.coeffs, gridspec_kwargs=gridspec_kwargs
        )

        if scatter_kwargs is None:
            scatter_kwargs = {}

        # for each variable in the variable table
        for i, var in enumerate(list(self.coeffs.variable.unique())):
            # get the data for the current variable/subplot
            data = self.coeffs.loc[self.coeffs.variable == var]
            # add gray trellis lines
            for label in sorted(list(data.label.unique())):
                self.ax_[i].axhline(y=label, color="#e9e9e9", linestyle="-", zorder=0)
            # make a scatter plot of the value vs. label
            self.ax_[i].scatter(
                "value",
                "label",
                data=data,
                **scatter_kwargs,
            )
            # set the subplot title as the variable name
            self.ax_[i].set_title(var)
            self.ax_[i].xaxis.set_major_locator(MaxNLocator(prune="both"))
            # set the y-axis ticks
            if y_label_map is not None:
                self.ax_[i].set_yticks(
                    list(y_label_map.keys()), list(y_label_map.values())
                )

        # turn off any remaining unused plots
        for j in range(i + 1, self.ax_.shape[0]):  # noqa W0631, pylint: disable=W0631
            self.ax_[j].set_axis_off()

        self.figure_.supxlabel("Coefficient Value")
        self.figure_.supylabel(y_axis_label)
        self.figure_.suptitle(f"Model Coefficients by {y_axis_label} and Variable")

    @classmethod
    def from_estimator(  # pylint: disable=R0913
        cls,
        estimator: Cubist,
        *,
        committee: int | None = None,
        rule: int | None = None,
        feature_names: list[str] | None = None,
        ax=None,
        scatter_kwargs=None,
        gridspec_kwargs=None,
    ):
        """Plot the coefficients used in the Cubist model.

        .. versionadded:: 1.0.0

        Parameters
        ----------
        estimator : Cubist instance
            Fitted Cubist regressor.

        committee : int
            Max committee number to be included in plot.

        rule : int
            Max rule number to be included in plot.

        feature_names : list[str]
            Feature names to filter to in the plot. Leaving unset plots all
            features.

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
        CubistCoefficientDisplay : Cubist coefficient visualization.

        Examples
        --------
        >>> import matplotlib.pyplot as plt
        >>> from sklearn.datasets import load_iris
        >>> from cubist import Cubist, CubistCoefficientDisplay
        >>> X, y = load_iris(return_X_y=True, as_frame=True)
        >>> model = Cubist(n_rules=2).fit(X, y)
        >>> display = CubistCoefficientDisplay.from_estimator(estimator=model)
        >>> plt.show()
        """
        check_is_fitted(estimator)

        # melt coeffs dataframe to show each coefficient variable/value pair by
        # committee/rule
        df = pd.melt(estimator.coeffs_, id_vars=["committee", "rule"])
        df = df.loc[df.notna().all(axis="columns")]

        df, y_axis_label, y_label_map = cls._validate_from_estimator_params(
            df=df, committee=committee, rule=rule, feature_names=feature_names
        )

        viz = cls(coeffs=df)

        return viz.plot(
            ax=ax,
            y_label_map=y_label_map,
            y_axis_label=y_axis_label,
            scatter_kwargs=scatter_kwargs,
            gridspec_kwargs=gridspec_kwargs,
        )
