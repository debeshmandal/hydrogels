#include "./potentials.hpp"

double lennardJones (double sig, double eps, double rc, double r) {
    double result;
    if (r > rc) {
        return 0;
    }
    double sr2i = 1. / (sig * sig * r * r);
    double sr6i = sr2i * sr2i * sr2i;
    result = 4 * eps * (sr2i * sr6i - sr6i);
    return result;
}

double harmonic (double k, double r) {
    double result = k * r * r;
    return result;
}

double zero (double r) {
    return 0.0;
}

double macroLJ (double sig, double eps, double nV, double n, double rE, double r) {

    double numerator = pow((2.0*r - (r+rE) * (r+rE)), (2.0-n/2.0)) - pow((-2.0 * rE * rE - 3 * rE * r),(2.0-n/2.0));
    double denominator = (r+rE) * (n-4.0);
    double result = numerator / denominator;

    denominator = 3.0 - n;
    numerator = pow((2.0 * r + rE), denominator) - pow(rE, denominator);
    result = result - (numerator / denominator);
    
    numerator = 2 * M_PI * nV * pow(sig, n) * eps;
    denominator = 2-n;
    result = result * (numerator / denominator);
    
    return result;
}

double macroPower3D (double r) {
    double result;
}

namespace py = pybind11;

PYBIND11_MODULE(potentials, m) {
    m.def("lennard_jones", &lennardJones, R"pbdoc(LJ)pbdoc", py::arg("sig"), py::arg("eps"), py::arg("rc"), py::arg("r") );
    m.def("harmonic", &harmonic, R"pbdoc(HARM)pbdoc", py::arg("k"), py::arg("r"));
    m.def("zero", &zero, R"pbdoc(ZERO)pbdoc", py::arg("r"));
    m.def("macro_LJ", &macroLJ, R"pbdoc(3D Macroscopic Lennard-Jones Nanoparticle)pbdoc", py::arg("sig"), py::arg("eps"), py::arg("nV"), py::arg("n"), py::arg("rE"), py::arg("r"));

    #ifdef VERSION_INFO
        m.attr("__version__") = VERSION_INFO;
    #else
        m.attr("__version__") = "dev";
    #endif
}