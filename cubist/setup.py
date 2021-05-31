import os

import numpy as np
from numpy import get_include
from numpy.distutils.misc_util import Configuration
from setuptools import setup


def configuration(parent_package='', top_path=None):
    config = Configuration('cubist_src', parent_package, top_path)

    # src_dir = os.path.join(top_path, "src")

    # newrand wrappers
    config.add_extension('_cubist',
                         sources=['_cubist.pyx'],
                         include_dirs=["src", np.get_include()]
                         # Use C++11 random number generator fix
                         # extra_compile_args=['-std=c++11']
                         )
    return config


if __name__ == '__main__':
    setup(**configuration(top_path='').todict())
