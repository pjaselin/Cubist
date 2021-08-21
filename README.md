# Cubist

A Python package for fitting JR Quinlan's [Cubist](https://www.rulequest.com/cubist-unix.html) v2.07 regression model. Inspired by and based on the [R wrapper](https://github.com/topepo/Cubist) for Cubist. Designed after and inherits from the [scikit-learn](https://scikit-learn.org/stable/) framework.

## Background
Cubist is a regression algorithm develped by Ross Quinlan...

## Use
```python
>>> from cubist import Cubist
>>> model = Cubist()
>>> model.fit(X, y)
>>> model.predict(X)
```

## Model Parameters
- n_rules
- n_committees
- biased

## Benchmarks
From literature, there are examples of Cubist outperforming RandomForest and other boostrapped/boosted models, to demonstrate this, the following benchmarks are provided to compare models. The scripts that achieved these results are provided in the benchmarks folder.

## Building
```bash
python -m build --sdist --wheel .
```

## Installing 
```bash
pip install cubist
```

```bash
pip install --upgrade .
```

## Interesting Links:  
- https://www.linkedin.com/pulse/machine-learning-example-r-using-cubist-kirk-mettler
http://rulequest.com/cubist-info.html

## Literature
- https://sci2s.ugr.es/keel/pdf/algorithm/congreso/1992-Quinlan-AI.pdf
- http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.34.6358&rep=rep1&type=pdf