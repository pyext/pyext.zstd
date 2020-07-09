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

#include <zstd.h>

static const char ext_name[] = "_zstd";

#ifdef __cplusplus
extern "C" {
#endif

static PyObject *
zstd_info(PyObject *self, PyObject *args)
{
    const char *command;
    int sts;

    if (!PyArg_ParseTuple(args, "s", &command))
        return NULL;
    sts = printf("zstd: %s\n", command);

    ZSTD_versionNumber();

    return PyLong_FromLong(sts);
}

static PyMethodDef zstd_methods[] = {
    {"info",  zstd_info, METH_VARARGS, "print information"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

#ifdef IS_PY3K

static struct PyModuleDef zstd_module = {
    PyModuleDef_HEAD_INIT,
    ext_name,   /* name of module */
    /*zstd_doc*/ NULL, /* module documentation, may be NULL */
    -1,             /* size of per-interpreter state of the module,
                    or -1 if the module keeps state in global variables. */
    zstd_methods
};

PyMODINIT_FUNC PyInit__zstd(void)
#else
PyMODINIT_FUNC init_zstd(void)
#endif
{
#ifdef IS_PY3K
    PyObject *module = PyModule_Create(&zstd_module);
#else
    PyObject *module = Py_InitModule(ext_name, zstd_methods);
#endif

    if (module == NULL)
        INITERROR;

#ifdef IS_PY3K
    return module;
#endif
}

#ifdef __cplusplus
}
#endif
