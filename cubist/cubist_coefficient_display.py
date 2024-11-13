import pandas as pd

from .cubist import Cubist
from ._cubist_display_mixin import _CubistDisplayMixin


class CubistCoefficientDisplay(_CubistDisplayMixin):
    def __init__(self, *, coeffs: pd.DataFrame):
        self.coeffs = coeffs
        self.fig_ = None
        self.ax_ = None

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
        self.fig_, self.ax_ = self._validate_plot_params(
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

        self.fig_.supxlabel("Coefficient Value")
        self.fig_.supylabel(ylabel)
        self.fig_.suptitle(f"Model Coefficients by {ylabel} and Variable")

    @classmethod
    def from_estimator(
        cls,
        estimator: Cubist,
        committee: int = None,
        rule: int = None,
        ax=None,
        scatter_kwargs=None,
        gridspec_kwargs=None,
    ):
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
