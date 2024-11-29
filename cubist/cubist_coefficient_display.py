import pandas as pd

from .cubist import Cubist
from ._cubist_display_mixin import _CubistDisplayMixin


class CubistCoefficientDisplay(_CubistDisplayMixin):
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

    def __init__(self, *, coeffs: pd.DataFrame):
        self.coeffs = coeffs

    def plot(
        self,
        ax=None,
        *,
        ylabel: str = None,
        gridspec_kwargs: dict = None,
        scatter_kwargs: dict = None,
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
            Additional keywords arguments passed to matplotlib `matplotlib.pyplot.subplots` function.

        **scatter_kwargs : dict
            Additional keywords arguments passed to matplotlib `matplotlib.pyplot.scatter` function.

        Returns
        -------
        display : :class:`~cubist.CubistCoefficientDisplay`
            Object that stores computed values.
        """
        self.figure_, self.ax_ = self._validate_plot_params(
            ax=ax, df=self.coeffs, gridspec_kwargs=gridspec_kwargs
        )

        if scatter_kwargs is None:
            scatter_kwargs = {}

        # for each variable in the variable table
        for i, var in enumerate(list(self.coeffs.variable.unique())):
            # make a scatter plot of the value vs. label
            self.ax_[i].scatter(
                "value",
                "label",
                data=self.coeffs.loc[self.coeffs.variable == var],
                **scatter_kwargs,
            )
            # set the subplot title as the variable name
            self.ax_[i].set_title(var)

        # turn off any remaining unused plots
        for j in range(i + 1, self.ax_.shape[0]):  # noqa W0631, pylint: disable=W0631
            self.ax_[j].set_axis_off()

        self.figure_.supxlabel("Coefficient Value")
        self.figure_.supylabel(ylabel)
        self.figure_.suptitle(f"Model Coefficients by {ylabel} and Variable")

    @classmethod
    def from_estimator(
        cls,
        estimator: Cubist,
        *,
        committee: int = None,
        rule: int = None,
        ax=None,
        scatter_kwargs=None,
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

        df, ylabel = cls._validate_from_estimator_params(
            df=df, committee=committee, rule=rule
        )

        viz = cls(coeffs=df)

        return viz.plot(
            ax=ax,
            ylabel=ylabel,
            scatter_kwargs=scatter_kwargs,
            gridspec_kwargs=gridspec_kwargs,
        )
