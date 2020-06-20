#include "functions.hpp"

#define PI 3.14159

double addNumbers (double a, double b) {
    double sum;
    sum = a+b;
    return sum;
}

double mass_from_R (double R, double rho) {
    double mass = (4./3.) * PI * R * R * R * rho;
    return mass;
}

double R_from_mass (double mass, double rho) {
    double R = cbrt((0.75 / PI) * (1. / rho) * mass);
    return R;
}

double k_R (double K_V, double c_0, double boltz) {
    double result = K_V * c_0 * boltz;
    return result;
}

double vectorNorm (std::vector<double> vect) {
    double result;
    result = 0;
    for (int i=0; i<vect.size(); i++)
        result += vect[i] * vect[i];
    result = sqrt(result);
    return result;
}