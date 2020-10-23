# hydrogels

[![Manylinux](https://github.com/debeshmandal/hydrogels/workflows/ManyLinux/badge.svg)](https://github.com/debeshmandal/hydrogels/actions?query=workflow%3ALinux)
[![MacOS](https://github.com/debeshmandal/hydrogels/workflows/MacOS/badge.svg)](https://github.com/debeshmandal/hydrogels/actions?query=workflow%3AMacOS)
[![Coverage](https://codecov.io/github/debeshmandal/hydrogels/coverage.svg?branch=master)](https://codecov.io/gh/debeshmandal/hydrogels)

#### Simulation and Numerical Integration for Hydrogel Degradation

This repository contains a variety of tools for simulating hydrogels. The main part of the code is for generating configurations and simulation systems for use with the software package called ReaDDy.

Then, in the `theory` folder, a numerical integration framework for integrating differential equations can be found. This is used for describing the enzymatic degradation of a hydrogel nanoparticle. This module in particular contains C++/Python code that is bound using `pybind11`. Also contained in the main repository, are Jupyter Notebooks with examples of how to use the `hydrogels.theory` module.

## Installation:

`hydrogels` is available on Linux, MacOS and Windows using Python 3.6, 3.7 and 3.8. It is not available yet on Python 3.9 because there is a dependency on SciPy which currently has no wheels built for Python 3.9.

At the time of writing it is only possible to install the package on a Linux architecture. This requires the following prerequisites:
  - gxx
  - pybind11
  - numpy
  - pandas
  - readdy
  - scipy

To install, do the following command from the main directory:

```bash
pip install .
```

And to test (also from the main directory):


```bash
pytest
```

