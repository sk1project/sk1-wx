/* _libpango - small module which provides extended binding to Pango library.
 *
 * Copyright (C) 2016 by Igor E.Novikov
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
#include <pango/pango.h>
#include <pango/pangocairo.h>


static PyObject *
pango_GetFontMap (PyObject *self, PyObject *args) {

	PangoFontMap *fm;
	PangoContext *ctx;

    PangoFontFamily **families;
    int n_families, n_faces, i, j;
    PyObject *ret;

	fm = pango_cairo_font_map_get_default();
	ctx = pango_font_map_create_context(fm);
    pango_context_list_families(ctx, &families, &n_families);

    ret = PyTuple_New(n_families);

    for (i = 0; i < n_families; i++) {

    	PyObject *family;
    	family = PyTuple_New(2);

    	PyTuple_SetItem(family, 0,
    			Py_BuildValue("s", pango_font_family_get_name(families[i])));

        PangoFontFace **faces;
        pango_font_family_list_faces(families[i], &faces, &n_faces);

        int *sizes, n_sizes;

        pango_font_face_list_sizes(faces[0], &sizes, &n_sizes);
        if(!sizes) {
        	PyObject *faces_tuple;
        	faces_tuple = PyTuple_New(n_faces);
			for (j = 0; j < n_faces; j++) {
				PyTuple_SetItem(faces_tuple, j,
				Py_BuildValue("s", pango_font_face_get_face_name(faces[j])));
			}
			PyTuple_SetItem(family, 1, faces_tuple);
        }else{
        	Py_INCREF(Py_None);
        	PyTuple_SetItem(family, 1, Py_None);
        }
        PyTuple_SetItem(ret, i, family);
        g_free(sizes);
        g_free(faces);
    }

    g_free(families);
	g_object_unref(ctx);

	return ret;
}

static
PyMethodDef pango_methods[] = {
	{"get_fontmap", pango_GetFontMap, METH_VARARGS},
	{NULL, NULL}
};

void
init_libpango(void)
{
    Py_InitModule("_libpango", pango_methods);
}
