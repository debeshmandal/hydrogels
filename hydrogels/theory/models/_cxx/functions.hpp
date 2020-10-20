#ifndef FUNCTION_HPP
#define FUNCTION_HPP
#include <bits/stdc++.h>
#include <cmath>
#include "pybind11/pybind11.h"
double addNumbers (double a, double b);
double massFromRadius (double R, double rho);
double radiusFromMass (double mass, double rho);
double boltzmann (double beta, double U);
double rateFromPotentialEnergy (double K_V, double c_0, double U, double beta);
double radiusFromNumber (double N, double nV);
double updateNumberFromRate (double N, double k, double dt);
double vectorNorm (std::vector<double> vect);
double KVFromR (double R, double rate, double thickness);
#endif