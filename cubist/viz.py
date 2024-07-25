from warnings import warn

from .cubist import Cubist


def dotplot(x: Cubist, data=None, what="splits", committee=None, rule=None):
    rules = x.rules_
    if rules.empty:
        warn("No splits were used in this model")

    if committee:
        rules = rules[rules.committee <= committee]
    if rule:
        rules = rules[rules.rule <= rule]

    if max(rules.committee) == 1:
        lab = "Rule"
        rules.label = rules.rule.apply(lambda x: x.replace(" ", 0))
    else:
        lab = "Committee/Rule"
        rules.label = rules[["committee", "rule"]].apply(lambda x: x.replace())
    print(lab)
    return
