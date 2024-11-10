# class BaseCubistDisplay:
#     def __init__(self):
#         pass

#     def plot(self):
#         raise NotImplementedError

#     @classmethod
#     def _from_predictions(cls, what: str, estimator):
#         expected_what = ("splits", "coeffs")
#         if what not in expected_what:
#             raise ValueError(
#                 f"`what` must be one of {', '.join(expected_what)}. "
#                 f"Got {what!r} instead."
#             )

#         # import matplotlib.pyplot as plt

#         if what == "splits":
#             df = estimator.splits_.copy()
#         else:
#             df = estimator.coeffs_.copy()

#         if df.empty:
#             warn(f"No {what} were used in this model")
#             return

#         if committee is not None:
#             if not isinstance(committee, int):
#                 raise TypeError(
#                     f"`committee` must be an integer but got {type(committee)}"
#                 )
#             df = df.loc[df.committee <= committee]

#         if rule is not None:
#             if not isinstance(rule, int):
#                 raise TypeError(f"`rule` must be an integer but got {type(rule)}")
#             df = df.loc[df.rule <= rule]

#         if df.committee.max() == 1:
#             lab = "Rule"
#             df["label"] = df.rule.astype(str).str.replace(" ", "0", regex=False)
#         else:
#             lab = "Committee/Rule"
#             df["label"] = (
#                 df[["committee", "rule"]]
#                 .astype(str)
#                 .apply(
#                     lambda x: f"{x.committee.str.replace(' ', '0', regex=False)}/{x.rule.str.replace(' ', '0', regex=False)}",
#                     axis=1,
#                 )
#             )
