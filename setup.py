from setuptools import setup, Extension
from Cython.Build import cythonize
import glob
import numpy as np

exts = [
    Extension(
        name='_cubist',
        sources=["cubist/_cubist.pyx"] + glob.glob("cubist/src/*.c"),
        include_dirs=["cubist/src", np.get_include()]
    )
]

with open("README.md", 'r') as f:
    long_description = f.read()

with open("requirements.txt", 'r') as f:
    requires = f.read()

version = {}
with open("cubist/version.py") as f:
    exec(f.read(), version)


setup(
    name="cubist",
    version=version['__version__'],
    description="A python port of the R library cubist.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    ext_modules=cythonize(exts),
    zip_safe=False,
    include_package_data=True,
    install_requires=requires
)
