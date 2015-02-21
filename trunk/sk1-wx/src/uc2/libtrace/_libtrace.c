/* _libtrace - small module which provides binding to potrace library.
 *
 * Copyright (C) 2013 by Igor E.Novikov
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.

 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#include <Python.h>
#include <potracelib.h>

static PyObject *
libtrace_GetVersion (PyObject *self, PyObject *args) {
	return Py_BuildValue("s", potrace_version());
}

static
PyMethodDef libtrace_methods[] = {
	{"get_libtrace_version", libtrace_GetVersion, METH_VARARGS},
	{NULL, NULL}
};

void
init_libtrace(void)
{
    Py_InitModule("_libtrace", libtrace_methods);
}
