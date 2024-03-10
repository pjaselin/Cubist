import glob
import os.path
import codecs

from Cython.Build import cythonize
from setuptools import setup, Extension
import numpy as np


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), "r") as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")


extensions = [
    Extension(
        name="_cubist",
        sources=["cubist/_cubist.pyx"] + glob.glob("cubist/src/*.c"),
        include_dirs=["cubist/src", np.get_include()],
        define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
    )
]

setup(
    ext_modules=cythonize(
        extensions, compiler_directives={"language_level": 3, "profile": False}
    ),
    # version=get_version("cubist/__version__.py"),
)
