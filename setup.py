from distutils.core import setup, Extension
from distutils import sysconfig
import setuptools
import os

with open("README.md", "r") as f:
    long_description = f.read()

cpp_args = ['-std=c++11']#, '-stdlib=libc++']#, '-mmacosx-version-min=10.7']

potentials = Extension(
    'potentials', sources = ['./hydrogels/theory/models/_cxx/potentials.cpp'],
    include_dirs=[f'{os.environ["CONDA_PREFIX"]}/include/pybind11/include', './hydrogels/theory/models/_cxx/'],
    language='c++',
    extra_compile_args = cpp_args,
    )

functions = Extension(
    'functions', sources = ['./hydrogels/theory/models/_cxx/functions.cpp'],
    include_dirs=[f'{os.environ["CONDA_PREFIX"]}/include/pybind11/include', './hydrogels/theory/models/_cxx/'],
    language='c++',
    extra_compile_args = cpp_args,
    )

setup(
    name="hydrogels",
    version="0.0.4",
    author="Debesh Mandal",
    description="Package for creating and analysing hydrogels in ReaDDy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/debeshmandal/hydrogels",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
    ],
    python_requires=">=3.5",
    ext_modules=[potentials, functions]
)
