# Cubist

A Python package for fitting Quinlan's [Cubist](https://www.rulequest.com/cubist-unix.html) v2.07 regression model. Inspired by and based on the [R wrapper](https://github.com/topepo/Cubist) for Cubist. Designed after and inherits from the [scikit-learn](https://scikit-learn.org/stable/) framework.

## Background
Cubist is a regression algorithm develped by John Ross Quinlan for generating rule-based predictive models. This has been available in the R world thanks to the work of Max Kuhn and his colleagues. With this package it is introduced to the Python ecosystem and made scikit-learn compatible for easy use with existing data and model pipelines.

## Advantages
Unlike other ensemble models such as RandomForest and XGBoost, Cubist generates a set of rules, making it easy to understand precisely how the model makes it's predictive decisions. Thus tools such as SHAP and LIME are not needed as Cubist doesn't exhibit black box behavior. Like XGBoost, Cubist can perform boosting by the addition of more models (here called committees) that correct for the error of prior models (i.e. the second model created corrects for the prediction error of the first, the third for the error of the second, etc.). In addition to boosting, the model can perform instance-based (nearest-neighbor) corrections to create composite models, thus combining the advantages of these two methods.

## Use
```python
>>> from sklearn.datasets import load_boston
>>> from cubist import Cubist
>>> X, y = load_boston(return_X_y=True)
>>> model = Cubist()
>>> model.fit(X, y)
>>> model.predict(X)
>>> model.score(X, y)
```

## Model Parameters
The following parameters can be passed as arguments to the ```Cubist()``` class instantiation:
- n_rules (int, default=500): Limit of the number of rules Cubist will build. Recommended value is 500.
- n_committees (int, default=1): Number of committees to construct. Each committee is a rule based model and beyond the first tries to correct the prediction errors of the prior constructed model. Recommended value is 5.
- neighbors (int, default=1): Number between 1 and 9 for how many instances should be used to correct the rule-based prediction.
- unbiased (bool, default=False): Should unbiased rules be used? Since Cubist minimizes the MAE of the 
        predicted values, the rules may be biased and the mean predicted value may differ from the actual mean. This is recommended when there are frequent occurrences of the same value in a training dataset. Note that MAE may be slightly higher.
- extrapolation (float, default=0.05): Adjusts how much rule predictions are adjusted to be consistent with the training dataset. Recommended value is 5% as a decimal (0.05)
- sample (float, default=0.0): Percentage of the data set to be randomly selected for model building.
- random_state (int, default=randint(0, 4095)): An integer to set the random seed for the C Cubist code.
- target_label (str, default="outcome"): A label for the outcome variable. This is only used for printing rules.
- verbose (int, default=0) Should the Cubist output be printed? 1 if yes, 0 if no.

## Model Attributes
The following attributes are exposed to understand the Cubist model results:
- feature_importances_ (pd.DataFrame): Table of how training data variables are used in the Cubist model.
- rules_ (pd.DataFrame): Table of the rules built by the Cubist model.
- coeff_ (pd.DataFrame): Table of the regression coefficients found by the Cubist model.
- variables_ (dict): Information about all the variables passed to the model and those that were actually used.

## Benchmarks
From literature, there are examples of Cubist outperforming RandomForest and other boostrapped/boosted models, to demonstrate this, the following benchmarks are provided to compare models. The scripts that achieved these results are provided in the benchmarks folder.


## Installing 
```bash
pip install cubist
```
or
```bash
pip install --upgrade cubist
```

## Literature for Cubist Model
- https://sci2s.ugr.es/keel/pdf/algorithm/congreso/1992-Quinlan-AI.pdf
- http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.34.6358&rep=rep1&type=pdf

## Publications Using Cubist
- https://www.rulequest.com/cubist-pubs.html
- https://www.linkedin.com/pulse/machine-learning-example-r-using-cubist-kirk-mettler

## To Do
- Continue adding tests
- Add visualization utilities
- Enable more features from the C-code model
- Make Windows-compatible and continue verifying sklearn API integration