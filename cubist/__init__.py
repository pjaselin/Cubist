"""
cubist: Cubist regression model for Python
==========================================

cubist is a Python module that wraps the C implementation of Quinlan's
regression model of the same name. In the module, "Cubist" is the name of the
model class.

The model requires input data to be particularly formatted as strings and this
module handles this formatting process as well as the model options.

The module is designed after the sklearn API and inherits from the
RegressorMixin and BaseEstimator classes, meaning that Cubist can be dropped
into existing sklearn-based ML pipelines or scripts for experimenting.
"""

from .cubist import Cubist
from .dotplot import DotplotDisplay
from .exceptions import CubistError

__all__ = ["Cubist", "DotplotDisplay", "CubistError"]
