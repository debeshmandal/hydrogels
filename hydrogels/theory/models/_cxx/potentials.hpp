#ifndef POTENTIALS_HPP
#define POTENTIALS_HPP
#include <cmath>
#include "pybind11/pybind11.h"
double lennardJones (double sig, double eps, double rc, double r);
double harmonic (double k, double r);
double zero (double r);
#endif