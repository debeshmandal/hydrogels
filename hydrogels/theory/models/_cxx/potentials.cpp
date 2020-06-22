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

double macroPower2D (double sig, double eps, double rho, double n, double r) {
    double result;
    double numerator = 2 * M_PI * eps * rho * sig * sig * sig;
    double denominator = n * n - 5 * n + 6;
    double power = pow(sig / r, n - 3);
    result = (numerator * power) / denominator;
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
    m.def("macro_power2D", &macroPower2D, R"pbdoc(2D Power Law Sphere)pbdoc", py::arg("sig"), py::arg("eps"), py::arg("rho"), py::arg("n"), py::arg("r"));

    #ifdef VERSION_INFO
        m.attr("__version__") = VERSION_INFO;
    #else
        m.attr("__version__") = "dev";
    #endif
}