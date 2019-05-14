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
#include "pyuci.h"
#include <uci.h>
#include <stdio.h>
#include "pyhelper.h"

// Uci exceptions
static PyObject *UciException;
static PyObject *UciExcNotFound;

// Python Uci object handle
typedef struct {
	PyObject_HEAD
	struct uci_context *ctx;
	bool tainted;
} uci_object;

static void uci_dealloc(uci_object *self) {
	if (self->ctx != NULL)
		uci_free_context(self->ctx);
}

static int uci_init(uci_object *self, PyObject *args, PyObject *kwds) {
	if (self->ctx) // reinitialization so first free previous one
		uci_free_context(self->ctx);
	self->tainted = false;
	self->ctx = uci_alloc_context();
	if (self->ctx == NULL) {
		PyErr_SetString(UciException, "Cannot allocate uci context.");
		return 0;
	}
	static const char *keys[] = {"savedir", "confdir", NULL};
	const char *savedir = NULL, *confdir = NULL;
	PyArg_ParseTupleAndKeywords(args, kwds, "|ss", (char**)keys, &savedir, &confdir);
	// TODO verify exit codes
	if (savedir)
		uci_set_savedir(self->ctx, savedir);
	if (confdir)
		uci_set_confdir(self->ctx, confdir);
	return 0;
}

static PyObject *pyuci_enter(uci_object *self, PyObject *args) {
	if (!self->ctx) {
		PyErr_SetString(UciException, "Entering with non-initialized object is invalid");
		return NULL;
	}
	return (PyObject*)self;
}

static void commit_all(struct uci_context *ctx) {
	struct uci_ptr ptr;
	memset(&ptr, 0, sizeof ptr);
	struct uci_element *e, *tmp;
	uci_foreach_element_safe(&ctx->root, tmp, e) {
		struct uci_package *p = uci_to_package(e);
		if (ptr.p && (ptr.p != p))
			continue;
		ptr.p = p;
		uci_commit(ctx, &p, false);
	}
}

static PyObject *pyuci_exit(uci_object *self, PyObject *args) {
	if (self->ctx) {
		if (self->tainted)
			commit_all(self->ctx);
		uci_free_context(self->ctx);
	}
	self->ctx = NULL;
	Py_RETURN_NONE;
}

static PyObject *pyuci_error(uci_object *self, PyObject *excp) {
	char *str = NULL;
	uci_get_errorstr(self->ctx, &str, NULL);
	if (str) {
		PyErr_SetString(excp, str);
		free(str);
	} else
		PyErr_SetNone(excp);

	return NULL;
}

// Convert uci option to python representation
static PyObject *pyuci_option(struct uci_option *opt) {
	struct uci_element *e;

	switch(opt->type) {
	case UCI_TYPE_STRING:
		return Py_BuildValue("s", opt->v.string);
	case UCI_TYPE_LIST:
		{
			int i = 0;
			uci_foreach_element(&opt->v.list, e)
				i++;
			PyObject *ret = PyTuple_New(i);
			i = 0;
			uci_foreach_element(&opt->v.list, e) {
				PyTuple_SET_ITEM(ret, i, Py_BuildValue("s", e->name));
				i++;
			}
			return ret;
		}
	}
	PyErr_SetNone(PyExc_NotImplementedError);
	return NULL;
}

// Convert uci section to python representation
static PyObject *pyuci_section(struct uci_section *sec) {
	// TODO other variables somehow (such as type, name and index)
	PyObject *ret = PyDict_New();

	struct uci_element *e;
	uci_foreach_element(&sec->options, e) {
		struct uci_option *o = uci_to_option(e);
		PyObject *opt = pyuci_option(o);
		PyDict_SetItemString(ret, o->e.name, opt);
	}

	return ret;
}

// Convert uci package to python representation
static PyObject *pyuci_package(struct uci_package *pkg) {
	PyObject *ret = PyDict_New();

	int index = 0; // TODO pass to section?
	struct uci_element *e;
	uci_foreach_element(&pkg->sections, e) {
		PyObject *sec = pyuci_section(uci_to_section(e));
		PyDict_SetItemString(ret, e->name, sec);
		index++;
	}
	return ret;
}

// Common arguments lookup (package, section, option)
static bool lookup_ptr(uci_object *self, PyObject *args, struct uci_ptr *ptr) {
	memset(ptr, 0, sizeof *ptr);

	if (!PyArg_ParseTuple(args, "s|ss", &ptr->package, &ptr->section, &ptr->option))
		return false;
	if (ptr->section == ptr->option && ptr->option == NULL) {
		const char *str = ptr->package;
		memset(ptr, 0, sizeof *ptr);
		uci_lookup_ptr(self->ctx, ptr, (char*)str, true);
	}
	uci_lookup_ptr(self->ctx, ptr, NULL, true);
	return true;
}

static PyObject *pyuci_get_common(uci_object *self, PyObject *args, bool all) {
	struct uci_ptr ptr;

	if (!lookup_ptr(self, args, &ptr))
		return NULL;
	uci_lookup_ptr(self->ctx, &ptr, NULL, true);
	if (!(ptr.flags & UCI_LOOKUP_COMPLETE)) {
		PyErr_SetNone(UciExcNotFound);
		return NULL;
	}

	struct uci_element *e = ptr.last;
	switch(e->type) {
		case UCI_TYPE_PACKAGE:
			return pyuci_package(ptr.p);
		case UCI_TYPE_SECTION:
			if (all)
				return pyuci_section(ptr.s);
			else
				return Py_BuildValue("s", ptr.s->type);
		case UCI_TYPE_OPTION:
			return pyuci_option(ptr.o);
	default:
		{
			char *msg;
			asprintf(&msg, "Type: %d", e->type);
			PyErr_SetString(PyExc_NotImplementedError, msg);
			return NULL;
		}
	}
}

static PyObject *pyuci_get(uci_object *self, PyObject *args) {
	return pyuci_get_common(self, args, false);
}

static PyObject *pyuci_get_all(uci_object *self, PyObject *args) {
	return pyuci_get_common(self, args, true);
}

static PyObject *pyuci_set(uci_object *self, PyObject *args) {
	struct uci_ptr ptr;
	memset(&ptr, 0, sizeof ptr);

	PyObject *data = NULL;
	switch (PyTuple_Size(args)) {
		// TODO variant with just one argument?
	case 4:
		// Format: uci.set("p", "s", "o", "v")
		if (!PyArg_ParseTuple(args, "sssO", &ptr.package, &ptr.section, &ptr.option, &data))
			return NULL;
		break;
	case 3:
		// Format: uci.set("p", "s", "v")
		if (!PyArg_ParseTuple(args, "ssO", &ptr.package, &ptr.section, &data))
			return NULL;
		break;
	default:
		PyErr_SetString(UciException, "Invalid number of arguments passed to Uci.set()");
		return NULL;
	}

	uci_lookup_ptr(self->ctx, &ptr, NULL, true);

	if (is_pytable(data)) {
		uci_delete(self->ctx, &ptr);
		int i;
		for (i = 0; i < pytable_size(data); i++) {
			if (!(ptr.value = pytable_string(data, i)))
				return NULL;
			if (uci_add_list(self->ctx, &ptr))
				return pyuci_error(self, UciException);
		}
	} else if (PyUnicode_Check(data)) {
		ptr.value = PyUnicode_AsUTF8(data);
		if (!ptr.value)
			return NULL;
		if (uci_set(self->ctx, &ptr))
			return pyuci_error(self, UciException);
	} else {
		PyErr_SetString(UciException, "Unsupported value passed to uci.set()");
		return NULL;
	}
	self->tainted = true;

	Py_RETURN_NONE;
}

static PyObject *pyuci_delete(uci_object *self, PyObject *args) {
	struct uci_ptr ptr;
	if (!lookup_ptr(self, args, &ptr))
		return NULL;

	uci_delete(self->ctx, &ptr);
	self->tainted = true;

	Py_RETURN_NONE;
}

static PyObject *pyuci_add(uci_object *self, PyObject *args) {
	// TODO we need findpkg
	PyErr_SetNone(PyExc_NotImplementedError);
	self->tainted = true;
	return NULL;
}

static PyObject *pyuci_rename(uci_object *self, PyObject *args) {
	struct uci_ptr ptr;
	memset(&ptr, 0, sizeof ptr);

	switch(PyTuple_Size(args)) {
		// TODO? Format: uci.rename("p.s.o=v") or uci.set("p.s=v")
	case 4:
		// Format: uci.rename("p", "s", "o", "v")
		if (!PyArg_ParseTuple(args, "ssss", &ptr.package, &ptr.section, &ptr.option, &ptr.value))
			return NULL;
		break;
	case 3:
		// Format: uci.rename("p", "s", "v")
		if (!PyArg_ParseTuple(args, "sss", &ptr.package, &ptr.section, &ptr.value))
			return NULL;
		break;
	default:
		PyErr_SetString(UciException, "Invalid number of arguments passed to Uci.rename()");
		return NULL;
	}

	if (uci_lookup_ptr(self->ctx, &ptr, NULL, true))
		return pyuci_error(self, UciException);

	if (((ptr.s == NULL) && (ptr.option != NULL)) || (ptr.value == NULL)) {
		// TODO really?
		PyErr_SetString(UciException, "Internal uci error");
		return NULL;
	}

	if(uci_rename(self->ctx, &ptr))
		return pyuci_error(self, UciException);
	self->tainted = true;

	Py_RETURN_NONE;
}

static PyObject *pyuci_reorder(uci_object *self, PyObject *args) {
	struct uci_ptr ptr;
	memset(&ptr, 0, sizeof ptr);
	int pos = 0;

	// Format: uci.reorder("p", "s", v)
	if (!PyArg_ParseTuple(args, "ssi", &ptr.package, &ptr.section, &pos))
		return NULL;

	if (uci_lookup_ptr(self->ctx, &ptr, NULL, true))
		return pyuci_error(self, UciException);

	if ((ptr.s == NULL)  || (ptr.value == NULL)) {
		// TODO really?
		PyErr_SetString(UciException, "Internal uci error");
		return NULL;
	}

	if(uci_reorder_section(self->ctx, ptr.s, pos))
		return pyuci_error(self, UciException);
	self->tainted = true;

	Py_RETURN_NONE;
}

enum pkg_cmd {
	CMD_SAVE,
	CMD_COMMIT,
	CMD_REVERT
};

static PyObject *package_cmd(uci_object *self, PyObject *args, enum pkg_cmd cmd) {
	struct uci_ptr ptr;
	if (!lookup_ptr(self, args, &ptr))
		return NULL;

	struct uci_element *e, *tmp;
	uci_foreach_element_safe(&self->ctx->root, tmp, e) {
		struct uci_package *p = uci_to_package(e);
		if (ptr.p && (ptr.p != p))
			continue;
		ptr.p = p;
		switch (cmd) {
		case CMD_SAVE:
			uci_save(self->ctx, p);
			break;
		case CMD_COMMIT:
			uci_commit(self->ctx, &p, false);
			break;
		case CMD_REVERT:
			uci_revert(self->ctx, &ptr);
			break;
		}
	}
	self->tainted = false;
	Py_RETURN_NONE;
}

static PyObject *pyuci_save(uci_object *self, PyObject *args) {
	return package_cmd(self, args, CMD_SAVE);
}

static PyObject *pyuci_commit(uci_object *self, PyObject *args) {
	return package_cmd(self, args, CMD_COMMIT);
}

static PyObject *pyuci_revert(uci_object *self, PyObject *args) {
	return package_cmd(self, args, CMD_REVERT);
}

static PyObject *pyuci_unload(uci_object *self, PyObject *args) {
	// TODO
	PyErr_SetNone(PyExc_NotImplementedError);
	return NULL;
}

static PyObject *pyuci_load(uci_object *self, PyObject *args) {
	// TODO
	PyErr_SetNone(PyExc_NotImplementedError);
	return NULL;
}

static PyObject *pyuci_changes(uci_object *self, PyObject *args) {
	// TODO
	PyErr_SetNone(PyExc_NotImplementedError);
	return NULL;
}

static PyObject *pyuci_list_configs(uci_object *self, PyObject *args) {
	char **configs = NULL;
	char **ptr;

	if ((uci_list_configs(self->ctx, &configs) != UCI_OK) || !configs)
		return pyuci_error(self, UciException);

	PyObject *ret = PyList_New(0);
	for (ptr = configs; *ptr; ptr++)
		if (PyList_Append(ret, PyUnicode_FromString(*ptr)))
			return NULL;

	return ret;
}

static PyObject *pyuci_confdir(uci_object *self, PyObject *args __attribute__((unused))) {
	return PyUnicode_FromString(self->ctx->confdir);
}

static PyObject *pyuci_set_confdir(uci_object *self, PyObject *args) {
	const char *dir;
	if (PyArg_ParseTuple(args, "s", &dir))
		return NULL;
	if (uci_set_confdir(self->ctx, dir))
		return pyuci_error(self, UciException);
	Py_RETURN_NONE;
}

static PyObject *pyuci_savedir(uci_object *self, PyObject *args __attribute__((unused))) {
	return PyUnicode_FromString(self->ctx->savedir);
}

static PyObject *pyuci_set_savedir(uci_object *self, PyObject *args) {
	const char *dir;
	if (PyArg_ParseTuple(args, "s", &dir))
		return NULL;
	if (uci_set_savedir(self->ctx, dir))
		return pyuci_error(self, UciException);
	Py_RETURN_NONE;
}

static PyMethodDef uci_methods[] = {
	{"__enter__", (PyCFunction)pyuci_enter, METH_VARARGS, "Enter context"},
	{"__exit__", (PyCFunction)pyuci_exit, METH_VARARGS, "Exit context"},
	{"get", (PyCFunction)pyuci_get, METH_VARARGS, "Get value"},
	{"get_all", (PyCFunction)pyuci_get_all, METH_VARARGS, "Get all values even for sections"},
	{"set", (PyCFunction)pyuci_set, METH_VARARGS, "Set value"},
	{"delete", (PyCFunction)pyuci_delete, METH_VARARGS, "Delete option"},
	{"add", (PyCFunction)pyuci_add, METH_VARARGS, "Add new anonymous section"},
	{"rename", (PyCFunction)pyuci_rename, METH_VARARGS, "Rename an element"},
	{"reorder", (PyCFunction)pyuci_reorder, METH_VARARGS, "Reposition a section"},
	{"save", (PyCFunction)pyuci_save, METH_VARARGS, "Save change delta for given package"},
	{"commit", (PyCFunction)pyuci_commit, METH_VARARGS, "Commit changed configuration to coresponding file in confdir"},
	{"revert", (PyCFunction)pyuci_revert, METH_VARARGS, "Revert all changes config item"},
	{"unload", (PyCFunction)pyuci_unload, METH_VARARGS, "Unload a config file from uci object"},
	{"load", (PyCFunction)pyuci_load, METH_VARARGS, "Parse an uci file and store it in the uci object"},
	{"changes", (PyCFunction)pyuci_changes, METH_VARARGS, "Return set of changes in loaded configuration"},
	{"list_configs", (PyCFunction)pyuci_list_configs, METH_VARARGS, "List available config files"},
	{"confdir", (PyCFunction)pyuci_confdir, METH_VARARGS, "Returns current confdir"},
	{"set_confdir", (PyCFunction)pyuci_set_confdir, METH_VARARGS, "Change used confdir"},
	{"savedir", (PyCFunction)pyuci_savedir, METH_VARARGS, "Returns current savedir"},
	{"set_savedir", (PyCFunction)pyuci_set_savedir, METH_VARARGS, "Change used savedir"},
	// TODO somehow allow iteration
	{NULL}
};

static PyTypeObject uci_type = {
	PyVarObject_HEAD_INIT(NULL, 0)
	"uci.Uci", /* tp_name */
	sizeof(uci_object), /* tp_basicsize */
	0, /* tp_itemsize */
	(destructor)uci_dealloc, /* tp_dealloc */
	0, /* tp_print */
	0, /* tp_getattr */
	0, /* tp_setattr */
	0, /* tp_reserved */
	0, /* tp_repr */
	0, /* tp_as_number */
	0, /* tp_as_sequence */
	0, /* tp_as_mapping */
	0, /* tp_hash  */
	0, /* tp_call */
	0, /* tp_str */
	0, /* tp_getattro */
	0, /* tp_setattro */
	0, /* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flgs */
	"Top level entry point to uci context. Create instance of this for any uci access", /* tp_doc */
	0, /* tp_traverse */
	0, /* tp_clear */
	0, /* tp_richcompare */
	0, /* tp_weaklistoffset */
	0, /* tp_iter */
	0, /* tp_iternext */
	uci_methods, /* tp_method */
	0, /* tp_members */
	0, /* tp_getset */
	0, /* tp_base */
	0, /* tp_dict */
	0, /* tp_descr_get */
	0, /* tp_descr_set */
	0, /* tp_disctoffset */
	(initproc)uci_init, /* tp_init */
	PyType_GenericAlloc, /* tp_alloc */
	PyType_GenericNew, /* tp_new */
	0, /* tp_free */
	0, /* tp_is_gc */
	0, /* tp_bases */
	0, /* tp_mro */
	0, /* tp_cache */
	0, /* tp_subclasses */
	0, /* tp_weaklist */
};

bool pyuci_object_init(PyObject *module) {
	if (PyType_Ready(&uci_type) < 0)
		return false;

	Py_INCREF(&uci_type);
	PyModule_AddObject(module, "Uci", (PyObject*)&uci_type);

	UciException = PyErr_NewException("uci.UciException", NULL, NULL);
	Py_INCREF(UciException);
	PyModule_AddObject(module, "UciException", UciException);

	UciExcNotFound = PyErr_NewException("uci.UciExceptionNotFound", UciException, NULL);
	Py_INCREF(UciExcNotFound);
	PyModule_AddObject(module, "UciExceptionNotFound", UciExcNotFound);

	return true;
}
