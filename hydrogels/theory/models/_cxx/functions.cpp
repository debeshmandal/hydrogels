#include "functions.hpp"

double addNumbers (double a, double b) {
    double sum;
    sum = a+b;
    return sum;
}

double boltzmann (double beta, double U) {
    double result = exp(beta * U * -1.0);
    return result;
}

double massFromRadius (double R, double rho) {
    double mass = (4./3.) * M_PI * R * R * R * rho;
    return mass;
}

double radiusFromMass (double mass, double rho) {
    double R = cbrt((0.75 / M_PI) * (1.0 / rho) * mass);
    return R;
}

double radiusFromNumber (double N, double nV) {
    double result = cbrt( ( 0.75 * M_PI ) * N * nV);
    return result;
}

double rateFromPotentialEnergy (double K_V, double c_0, double U, double beta) {
    double result = K_V * c_0 * boltzmann(beta, U);
    return result;
}

double updateNumberFromRate (double N, double k, double dt) {
    double result = N - k * dt;
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

namespace py = pybind11;

PYBIND11_MODULE(functions, m) {
    m.def("boltzmann", &boltzmann, R"pbdoc(Boltzmann Factor)pbdoc", py::arg("beta"), py::arg("U"));
    m.def("radius_from_number", &radiusFromNumber, R"pbdoc(Radius from number of particles and number density)pbdoc", py::arg("N"), py::arg("nV"));
    m.def("rate_from_potential_energy", &rateFromPotentialEnergy, R"pbdoc(Rate from Potential Energy at surface and bulk concentration)pbdoc", py::arg("KV"), py::arg("c0"), py::arg("U"), py::arg("beta"));
    m.def("update_number_from_rate", &updateNumberFromRate, R"pbdoc(New number of particles using rate and timestep)pbdoc", py::arg("N"), py::arg("k"), py::arg("dt"));

    #ifdef VERSION_INFO
        m.attr("__version__") = VERSION_INFO;
    #else
        m.attr("__version__") = "dev";
    #endif
}