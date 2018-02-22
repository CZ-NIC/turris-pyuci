/*
 * Copyright 2018, CZ.NIC z.s.p.o. (http://www.nic.cz/)
 *
 * This file is part of the PyUCI.
 *
 * PyUCI is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 * PyUCI is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with PyUCI.  If not, see <http://www.gnu.org/licenses/>.
 */
#include <Python.h>
#include "pyuci.h"

// TODO what about doing uci.get (non-object function)

static PyMethodDef module_methods[] = {
	{NULL, NULL, 0, NULL}
};


#if PY_MAJOR_VERSION >= 3

static struct PyModuleDef moduledef = {
	PyModuleDef_HEAD_INIT,
	"uci",
	"Unified configuration interface bindings",
	-1,
	module_methods,
	NULL, NULL, NULL, NULL
};

#define RETURN_ERROR return NULL

#else

#define RETURN_ERROR return

#endif

#if PY_MAJOR_VERSION >= 3
PyMODINIT_FUNC PyInit_uci(void) {
#else
PyMODINIT_FUNC inituci(void) {
#endif
	PyObject *m;

#if PY_MAJOR_VERSION >= 3
	m = PyModule_Create(&moduledef);
#else
	m = Py_InitModule("uci", module_methods);
#endif
	if (m == NULL)
		RETURN_ERROR;

	// Add Uci type to module
	if (!pyuci_object_init(m))
		RETURN_ERROR;

#if PY_MAJOR_VERSION >= 3
	return m;
#endif
}
