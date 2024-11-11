import pandas as pd

from .cubist import Cubist
from ._cubist_display_mixin import CubistDisplayMixin


class CubistCoverageDisplay(CubistDisplayMixin):
    def __init__(self, *, splits: pd.DataFrame):
        self.splits = splits

    def plot(
        self,
        ax=None,
        *,
        ylabel: str = None,
        scatter_kwargs: dict = None,
        line_kwargs: dict = None,
        gridspec_kwargs: dict = None,
    ):
        self.fig_, self.ax_ = self._validate_plot_params(
            ax=ax, df=self.splits, gridspec_kwargs=gridspec_kwargs
        )

        for i, var in enumerate(list(self.splits.variable.unique())):
            # add trellis lines
            for label in sorted(list(self.splits.label.unique())):
                self.ax_[i].plot([0, 1], [label, label], color="#e9e9e9")
                self.ax_[i].set_xlim([-0.05, 1.05])
            # plot data
            for _, row in self.splits.loc[self.splits.variable == var].iterrows():
                if "<" in row["dir"]:
                    x = [0, row["percentile"]]
                    color = "#1E88E5"
                else:
                    x = [row["percentile"], 1]
                    color = "#ff0d57"
                self.ax_[i].plot(x, [row["label"], row["label"]], color=color)
                self.ax_[i].set_title(var)

        for j in range(i + 1, ax.shape[0]):
            self.ax_[j].set_axis_off()

        self.fig_.supxlabel("Training Data Coverage")
        self.fig_.supylabel(ylabel)
        self.fig_.suptitle(f"Training Data Coverage by {ylabel} and Variable")

        return self

    @classmethod
    def from_estimator(
        cls,
        estimator: Cubist,
        committee: int = None,
        rule: int = None,
        ax=None,
        scatter_kwargs=None,
        line_kwargs=None,
        gridspec_kwargs=None,
    ):
        df = estimator.splits_.copy()

        df, ylabel = cls._validate_from_estimator_params(
            df=df, committee=committee, rule=rule
        )

        viz = cls(splits=df)

        return viz.plot(
            ax=ax,
            ylabel=ylabel,
            scatter_kwargs=scatter_kwargs,
            line_kwargs=line_kwargs,
            gridspec_kwargs=gridspec_kwargs,
        )
