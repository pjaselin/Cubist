# Cubist

A Python package for fitting Quinlan's Cubist regression model

Inspired by the R wrapper for cubist https://github.com/topepo/Cubist

## architecture
Taking inspiration from the R wrapper this is whatneeds to be done
1. Get cubist compiled on own machine so we have binary available
1. Understand the inputs tge binary require. The training fataset needs to
Conform to an exoected format. May eed to write oytgon code that converts
Pandas dataframe to this.
1. Write python code that forks off cubist process with correct arguments
And files
1. Write interpreter that translates cubists model definition to executable
Python code.
1. Write pypi package that bundles all this
1. Enhance package to compile cubist on users machine
1. Submit package to scikit learn 

links:
https://www.linkedin.com/pulse/machine-learning-example-r-using-cubist-kirk-mettler
http://rulequest.com/cubist-info.html

Help welcome
