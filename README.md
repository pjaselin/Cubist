![Credits to: https://voniart.weebly.com/cubist-animals.html](https://img.shields.io/github/last-commit/apachaves/Cubist)
![](https://img.shields.io/github/languages/code-size/apachaves/Cubist)

<img src='https://voniart.weebly.com/uploads/1/2/3/9/12399176/7832674_orig.jpg' width=125 height=125 align="right">

# PyCubist

A Python package for fitting Quinlan's Cubist regression model.

Inspired by the R wrapper for cubist: https://github.com/topepo/Cubist

## Architecture
Taking inspiration from the R wrapper this is what needs to be done.
1. Get cubist compiled on own machine so we have binary available.
2. Understand the inputs the binary require. The training dataset needs to conform to an expected format. May need to write python code that converts Pandas dataframe to this.
3. Write python code that forks off cubist process with correct arguments and files.
4. Write interpreter that translates cubists model definition to executable Python code.
5. Write pypi package that bundles all this.
6. Enhance package to compile cubist on users machine.
7. Make python translation performant by using scipy or numpy.
8. Adapt api to conform to scikit-learn.
9. Submit package to scikit-learn.


## Building
`python3 -m build --sdist --wheel .`

## Installing
`pip3 install .`

#### Help is welcome!

## Interesting Links:  
- https://www.linkedin.com/pulse/machine-learning-example-r-using-cubist-kirk-mettler
http://rulequest.com/cubist-info.html
