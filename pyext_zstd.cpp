#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <cstdio>

static PyObject *
pyext_zstd_info(PyObject *self, PyObject *args)
{
    const char *command;
    int sts;

    if (!PyArg_ParseTuple(args, "s", &command))
        return NULL;
    sts = printf("pyext_zstd: %s\n", command);
    return PyLong_FromLong(sts);
}

static PyMethodDef pyext_zstd_methods[] = {
    {"info",  pyext_zstd_info, METH_VARARGS, "print information"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

static struct PyModuleDef pyext_zstd_module = {
    PyModuleDef_HEAD_INIT,
    "pyext_zstd",   /* name of module */
    /*pyext_zstd_doc*/ NULL, /* module documentation, may be NULL */
    -1,             /* size of per-interpreter state of the module,
                    or -1 if the module keeps state in global variables. */
    pyext_zstd_methods
};

PyMODINIT_FUNC
PyInit_pyext_zstd(void)
{
    return PyModule_Create(&pyext_zstd_module);
}
