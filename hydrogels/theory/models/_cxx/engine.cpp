#include <Python.h>
#include "functions.hpp"
#include "utils.hpp"

static PyObject* 
engine_addNumbers(PyObject* self, PyObject* args) {
    // declare variables
    double n1, n2, result;

    // parse arguments
    if (!PyArg_ParseTuple(args, "dd", &n1, &n2)) {
        return NULL;
    };

    // function here
    result = addNumbers(n1, n2);

    // return correct Type
    return PyFloat_FromDouble(result);
    
};

static PyObject*
engine_vectorNorm(PyObject* self, PyObject* args) {
    PyObject* py_vect;
    if (!PyArg_ParseTuple(args, "O", &py_vect)) {
        return NULL;
    }
    std::vector<double> vect = listTupleToVector_Double(py_vect);
    double result = vectorNorm(vect);
    return PyFloat_FromDouble(result);
};

// Define docstrings
PyDoc_STRVAR(engine_docs, "Package for running iterative numerical simulations");
PyDoc_STRVAR(engine_addNumbers_docs, "addNumbers(n1 : number, n2 : number) -> float: add two numbers together\n");
PyDoc_STRVAR(engine_vectorNorm_docs, "vectorNorm(vector : list) -> float: returns the magnitude of a 1D Vector");

// Create list of PyMethodDefs
static PyMethodDef EngineFunctions[] = {
    {
        "addNumbers", 
        (PyCFunction)engine_addNumbers,
        METH_VARARGS, 
        engine_addNumbers_docs
    },
    {
        "vectorNorm", 
        (PyCFunction)engine_vectorNorm,
        METH_VARARGS, 
        engine_vectorNorm_docs
    },
    {NULL, NULL, 0, NULL} /* Sentinel */
};

// Create the Module
static struct PyModuleDef enginemodule = {
    PyModuleDef_HEAD_INIT,
    "engine", /* module name */
    engine_docs, /* documentation */
    -1, /* Leave this as -1 */
    EngineFunctions /* function list */
};

// Export module when __init__ is called
PyMODINIT_FUNC 
PyInit_engine(void) {
    return PyModule_Create(&enginemodule);
};
