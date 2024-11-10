# from ._base_cubist_display import BaseCubistDisplay


# class CubistCoefficientDisplay(BaseCubistDisplay):
#     def __init__(self):
#         super().__init__()

#     def plot(ax, df):
#         if ax is None:
#             nplots = df.variable.nunique()
#             nrows = ncols = int(round(math.sqrt(nplots)))
#             if nplots > (nrows * ncols):
#                 nrows += 1
#             fig, ax = plt.subplots(
#                 ncols=ncols,
#                 nrows=nrows,
#                 sharex="all",
#                 sharey="all",
#                 gridspec_kw=dict(hspace=0.5, wspace=0),
#             )
#             ax = ax.reshape(-1)
#         else:
#             fig = plt.gcf()

#         for i, var in enumerate(list(df.variable.unique())):
#             ax[i].scatter("value", "label", data=df.loc[df.variable == var])
#             ax[i].set_title(var)

#         for j in range(i + 1, ax.shape[0]):
#             ax[j].set_axis_off()

#         fig.supxlabel("Coefficient Value")
#         fig.supylabel(lab)
#         fig.suptitle(f"Model Coefficients by {lab} and Variable")

#     @classmethod
#     def from_predictions(cls, estimator):
#         return super()._from_predictions("splits", estimator)
