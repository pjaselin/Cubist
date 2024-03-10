import glob

from Cython.Build import cythonize
from setuptools import setup, Extension
import numpy as np

extensions = [
    Extension(
        name="_cubist",
        sources=["cubist/_cubist.pyx"] + glob.glob("cubist/src/*.c"),
        include_dirs=["cubist/src", np.get_include()],
        define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
    )
]

setup(
    name="cubist",
    ext_modules=cythonize(extensions),
)
