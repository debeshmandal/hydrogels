double lennardJones (double sig, double eps, double r) {
    double result;
    double sr2i = 1. / (sig * sig * r * r);
    double sr6i = sr2i * sr2i * sr2i;
    result = 4 * eps * (sr2i * sr6i - sr6i);
    return result;
}

double harmonic (double k, double r) {
    double result = k * r * r;
    return result;
}