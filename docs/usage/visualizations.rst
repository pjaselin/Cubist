Visualizations
##############

Based on the R Cubist package, a few visualization utilities are provided to allow some exploration of trained Cubist models. Differing from the original package, these are extended somewhat to allow configuration of the subplots as well as for selecting a subset of variables/attributes to plot.

Coefficient Display
*******************

The `CubistCoefficientDisplay` plots the multivariate linear regression coefficients and intercepts selected by the Cubist model. One subplot is created for each variable/attribute with the rule number or committee/rule pair on the y-axis and the coefficient value plotted along the x-axis.

![Sample Cubist Coefficient Display for Iris dataset](./static/iris_coefficient_display.png)

Coverage Display
****************

The `CubistCoverageDisplay` is used to visualize the coverage of rule splits for a given dataset. One subplot is created per input variable/attribute/column with the rule number or comittee/rule pair plotted on the y-axis and the coverage ranges plotted along the x-axis, scaled to the percentage of the variable values.

![Sample Cubist Coverage Display for Iris dataset](./static/iris_coverage_display.png)
