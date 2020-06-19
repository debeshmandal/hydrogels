#include "functions.hpp"

double addNumbers (double a, double b) {
    double sum;
    sum = a+b;
    return sum;
}

double vectorNorm (std::vector<double> vect) {
    double result;
    result = 0;
    for (int i=0; i<vect.size(); i++)
        result += vect[i] * vect[i];
    result = sqrt(result);
    return result;
}