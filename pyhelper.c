#include "pyhelper.h"

bool is_pystring(PyObject *pystr) {
#if PY_MAJOR_VERSION >= 3
	return PyUnicode_Check(pystr);
#else
	return PyString_Check(pystr);
#endif
}

const char *pystring(PyObject *pystr) {
#if PY_MAJOR_VERSION >= 3
	return PyUnicode_AsUTF8(pystr);
#else
	return PyString_AsString(pystr);
#endif
}

bool is_pytable(PyObject *pyobj) {
	return PyList_Check(pyobj) || PyTuple_Check(pyobj);
}

Py_ssize_t pytable_size(PyObject *pyobj) {
	if (PyList_Check(pyobj))
		return PyList_Size(pyobj);
	else if (PyTuple_Check(pyobj))
		return PyTuple_Size(pyobj);
	PyErr_SetNone(PyExc_NotImplementedError);
	return 0;
}

const char *pytable_string(PyObject *pyobj, int index) {
	PyObject *str = NULL;
	if (PyList_Check(pyobj))
		str =  PyList_GetItem(pyobj, index);
	else if (PyTuple_Check(pyobj))
		str = PyTuple_GetItem(pyobj, index);
	else
		PyErr_SetNone(PyExc_NotImplementedError);

	if (!str)
		return NULL;
	return pystring(str);
}
