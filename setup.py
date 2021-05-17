from setuptools import setup
from Cython.Build import cythonize

setup(
    name="helloworldapp",
    ext_modules=cythonize(["cubist/devtest.pyx"]),
    zip_safe=False
)
