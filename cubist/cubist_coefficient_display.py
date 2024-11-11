import pandas as pd

from .cubist import Cubist
from ._cubist_display_mixin import CubistDisplayMixin


class CubistCoefficientDisplay(CubistDisplayMixin):
    def __init__(self, *, coeffs: pd.DataFrame):
        self.coeffs = coeffs
        self.fig_ = None
        self.ax_ = None

    def plot(
        self,
        ax=None,
        *,
        ylabel: str = None,
        scatter_kwargs: dict = None,
        gridspec_kwargs: dict = None,
    ):
        self.fig_, self.ax_ = self._validate_plot_params(
            ax=ax, df=self.coeffs, gridspec_kwargs=gridspec_kwargs
        )

        for i, var in enumerate(list(self.coeffs.variable.unique())):
            self.ax_[i].scatter(
                "value",
                "label",
                data=self.coeffs.loc[self.coeffs.variable == var],
                **scatter_kwargs,
            )
            self.ax_[i].set_title(var)

        for j in range(i + 1, self.ax_.shape[0]):
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
