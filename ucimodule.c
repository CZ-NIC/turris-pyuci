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

static struct PyModuleDef moduledef = {
	PyModuleDef_HEAD_INIT,
	"uci",
	"Unified configuration interface bindings",
	-1,
	module_methods,
	NULL, NULL, NULL, NULL
};


PyMODINIT_FUNC PyInit_uci(void) {
	PyObject *m;

	m = PyModule_Create(&moduledef);
	if (m == NULL)
		return NULL;

	// Add Uci type to module
	if (!pyuci_object_init(m))
		return NULL;

	return m;
}
