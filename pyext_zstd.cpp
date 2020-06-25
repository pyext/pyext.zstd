#define PY_SSIZE_T_CLEAN
#include <Python.h>

#if PY_MAJOR_VERSION >= 3
#define IS_PY3K 1
#endif

#ifdef IS_PY3K
#define INITERROR return NULL
#else
#define INITERROR return
#endif

#include <cstdio>

static const char ext_name[] = "pyext_zstd";

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

#ifdef IS_PY3K

static struct PyModuleDef pyext_zstd_module = {
    PyModuleDef_HEAD_INIT,
    ext_name,   /* name of module */
    /*pyext_zstd_doc*/ NULL, /* module documentation, may be NULL */
    -1,             /* size of per-interpreter state of the module,
                    or -1 if the module keeps state in global variables. */
    pyext_zstd_methods
};

PyMODINIT_FUNC PyInit_pyext_zstd(void)
#else
void initpyext_zstd(void)
#endif
{
#ifdef IS_PY3K
    PyObject *module = PyModule_Create(&pyext_zstd_module);
#else
    PyObject *module = Py_InitModule(ext_name, pyext_zstd_methods);
#endif

    if (module == NULL)
        INITERROR;

#ifdef IS_PY3K
    return module;
#endif
}
