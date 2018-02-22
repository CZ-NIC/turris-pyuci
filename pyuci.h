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
#ifndef _PYUCI_H_
#define _PYUCI_H_

#include <Python.h>
#include <stdbool.h>

// Initialize Uci object in given module
// This should be called only once!
bool pyuci_object_init(PyObject *module);

#endif /* _PYUCI_H_ */
