from setuptools import setup, Extension
from Cython.Build import cythonize
import glob

exts = [
    Extension(
        name='_cubist',
        sources=["cubist/_cubist.pyx"] + glob.glob("cubist/src/*.c"),
        include_dirs=["cubist/src"]
    )
]

with open("README.md", 'r') as f:
    long_description = f.read()

setup(
    name="cubist",
    version="0.0.1",
    description="A python port of the R library cubist.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    ext_modules=cythonize(exts),
    zip_safe=False,
    # configuration=configuration,
    include_package_data=True,
    install_requires=[
        "build",
        "cython>=0.29.23",
        "numpy>=1.19.2",
        "pandas>=1.1.3",
        # "setuptools>=52.0.0",
        # "scikit-learn>=0.24.2"
    ]
)
