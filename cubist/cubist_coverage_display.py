import pandas as pd

from .cubist import Cubist
from ._cubist_display_mixin import _CubistDisplayMixin


class CubistCoverageDisplay(_CubistDisplayMixin):
    def __init__(self, *, splits: pd.DataFrame):
        self.splits = splits

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
            Additional keywords arguments passed to matplotlib `matplotlib.pyplot.subplots` function.

        **line_kwargs : dict
            Additional keywords arguments passed to matplotlib `matplotlib.pyplot.plot` function.

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
            # add gray trellis lines
            for label in sorted(list(self.splits.label.unique())):
                self.ax_[i].plot([0, 1], [label, label], color="#e9e9e9", **line_kwargs)
                self.ax_[i].set_xlim([-0.05, 1.05])
            # plot data
            for _, row in self.splits.loc[self.splits.variable == var].iterrows():
                # use blue for less than plot and set x points as 0 to some value
                if "<" in row["dir"]:
                    x = [0, row["percentile"]]
                    color = "#1E88E5"
                # use red for greater than plot and set x points as some value to 1
                else:
                    x = [row["percentile"], 1]
                    color = "#ff0d57"
                # plot line
                self.ax_[i].plot(
                    x, [row["label"], row["label"]], color=color, **line_kwargs
                )
                # set the subplot title
                self.ax_[i].set_title(var)

        # turn off any unused plots
        for j in range(i + 1, self.ax_.shape[0]):  # noqa W0631, pylint: disable=W0631
            self.ax_[j].set_axis_off()

        self.figure_.supxlabel("Training Data Coverage")
        self.figure_.supylabel(ylabel)
        self.figure_.suptitle(f"Training Data Coverage by {ylabel} and Variable")

        return self

    @classmethod
    def from_estimator(
        cls,
        estimator: Cubist,
        committee: int = None,
        rule: int = None,
        ax=None,
        line_kwargs=None,
        gridspec_kwargs=None,
    ):
        df = estimator.splits_.copy()

        # get rows that are continuous-type splits
        df = df.loc[df.type == "continuous"]

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
