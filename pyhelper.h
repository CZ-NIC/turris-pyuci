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
#ifndef _PYHELPER_H_
#define _PYHELPER_H_

#include <Python.h>
#include <stdbool.h>

// Functions for accessing both Lists and Tuples.
bool is_pytable(PyObject *pyobj);
Py_ssize_t pytable_size(PyObject *pyobj);
const char *pytable_string(PyObject *pyobj, int index);


#endif /* _PYHELPER_H_ */
