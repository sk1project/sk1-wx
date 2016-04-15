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
#include <cairo.h>
#include <pycairo.h>

static Pycairo_CAPI_t *Pycairo_CAPI;

static PyObject *
pango_GetVersion(PyObject *self, PyObject *args) {
	return PyString_FromString(pango_version_string());
}

static PyObject *
pango_GetFontMap(PyObject *self, PyObject *args) {

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
		if (!sizes) {
			PyObject *faces_tuple;
			faces_tuple = PyTuple_New(n_faces);
			for (j = 0; j < n_faces; j++) {
				PyTuple_SetItem(faces_tuple, j,
						Py_BuildValue("s",
								pango_font_face_get_face_name(faces[j])));
			}
			PyTuple_SetItem(family, 1, faces_tuple);
		} else {
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

static PyObject *
pango_CreateContext(PyObject *self, PyObject *args) {

	PycairoContext *context;
	cairo_t *ctx;
	PangoContext *pcctx;

	if (!PyArg_ParseTuple(args, "O", &context)) {
		return NULL;
	}
	ctx = context->ctx;

	pcctx = pango_cairo_create_context(ctx);

	return Py_BuildValue("O",
			PyCObject_FromVoidPtr((void *) pcctx, (void *) g_object_unref));
}

static PyObject *
pango_CreateLayout(PyObject *self, PyObject *args) {

	PycairoContext *context;
	cairo_t *ctx;
	PangoLayout *layout;

	if (!PyArg_ParseTuple(args, "O", &context)) {
		return NULL;
	}

	ctx = context->ctx;
	layout = pango_cairo_create_layout(ctx);

	return Py_BuildValue("O",
			PyCObject_FromVoidPtr((void *) layout, (void *) g_object_unref));
}

static PyObject *
pango_CreateFontDescription(PyObject *self, PyObject *args) {

	char *description;
	PangoFontDescription *fd;

	if (!PyArg_ParseTuple(args, "s", &description)) {
		return NULL;
	}

	fd = pango_font_description_from_string(description);

	return Py_BuildValue("O",
			PyCObject_FromVoidPtr((void *) fd,
					(void *) pango_font_description_free));
}

static PyObject *
pango_SetLayoutWidth(PyObject *self, PyObject *args) {

	int width;
	void *LayoutObj;
	PangoLayout *layout;

	if (!PyArg_ParseTuple(args, "Oi", &LayoutObj, &width)) {
		return NULL;
	}

	layout = PyCObject_AsVoidPtr(LayoutObj);
	pango_layout_set_width(layout, width);

	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *
pango_SetLayoutFontDescription(PyObject *self, PyObject *args) {

	void *LayoutObj;
	void *FDObj;
	PangoLayout *layout;
	PangoFontDescription *fd;

	if (!PyArg_ParseTuple(args, "OO", &LayoutObj, &FDObj)) {
		return NULL;
	}

	layout = PyCObject_AsVoidPtr(LayoutObj);
	fd = PyCObject_AsVoidPtr(FDObj);
	pango_layout_set_font_description(layout, fd);

	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *
pango_SetLayoutJustify(PyObject *self, PyObject *args) {

	void *PyObj;
	void *LayoutObj;
	PangoLayout *layout;

	if (!PyArg_ParseTuple(args, "OO", &LayoutObj, &PyObj)) {
		return NULL;
	}

	layout = PyCObject_AsVoidPtr(LayoutObj);
	pango_layout_set_justify(layout, PyObject_IsTrue(PyObj));

	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *
pango_SetLayoutAlignment(PyObject *self, PyObject *args) {

	int alignment;
	void *LayoutObj;
	PangoLayout *layout;

	if (!PyArg_ParseTuple(args, "Oi", &LayoutObj, &alignment)) {
		return NULL;
	}

	layout = PyCObject_AsVoidPtr(LayoutObj);

	if (alignment == 0) {
		pango_layout_set_justify(layout, 0);
		pango_layout_set_alignment(layout, PANGO_ALIGN_LEFT);
	} else if (alignment == 1) {
		pango_layout_set_justify(layout, 0);
		pango_layout_set_alignment(layout, PANGO_ALIGN_CENTER);
	} else if (alignment == 2) {
		pango_layout_set_justify(layout, 0);
		pango_layout_set_alignment(layout, PANGO_ALIGN_RIGHT);
	} else if (alignment == 3) {
		pango_layout_set_justify(layout, 1);
		pango_layout_set_alignment(layout, PANGO_ALIGN_LEFT);
	}

	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *
pango_SetLayoutMarkup(PyObject *self, PyObject *args) {

	void *LayoutObj;
	PangoLayout *layout;
	char *markup;

	if (!PyArg_ParseTuple(args, "Os", &LayoutObj, &markup)) {
		return NULL;
	}

	layout = PyCObject_AsVoidPtr(LayoutObj);

	pango_layout_set_markup(layout, markup, -1);

	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *
pango_GetLayoutPixelSize(PyObject *self, PyObject *args) {

	int width, height;
	void *LayoutObj;
	PangoLayout *layout;
	PyObject *pixel_size;

	if (!PyArg_ParseTuple(args, "O", &LayoutObj)) {
		return NULL;
	}

	layout = PyCObject_AsVoidPtr(LayoutObj);

	pango_layout_get_pixel_size(layout, &width, &height);

	pixel_size = PyTuple_New(2);
	PyTuple_SetItem(pixel_size, 0, PyInt_FromLong(width));
	PyTuple_SetItem(pixel_size, 1, PyInt_FromLong(height));

	return pixel_size;
}

static PyObject *
pango_LayoutPath(PyObject *self, PyObject *args) {

	PycairoContext *context;
	cairo_t *ctx;
	void *LayoutObj;
	PangoLayout *layout;

	if (!PyArg_ParseTuple(args, "OO", &context, &LayoutObj)) {
		return NULL;
	}

	ctx = context->ctx;
	layout = PyCObject_AsVoidPtr(LayoutObj);

	pango_cairo_layout_path(ctx, layout);

	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *
pango_GetLayoutLinePos(PyObject *self, PyObject *args) {

	int i, len;
	double baseline, dy;
	void *LayoutObj;
	PangoLayout *layout;
	PangoLayoutIter *iter;
	PyObject *ret;

	if (!PyArg_ParseTuple(args, "O", &LayoutObj)) {
		return NULL;
	}

	layout = PyCObject_AsVoidPtr(LayoutObj);

	len = pango_layout_get_line_count(layout);
	ret = PyTuple_New(len);
	iter = pango_layout_get_iter(layout);
	dy = ((double) pango_layout_iter_get_baseline(iter)) / PANGO_SCALE;

	for (i = 0; i < len; i++) {
		baseline = -1.0 * ((double) pango_layout_iter_get_baseline(iter))
				/ PANGO_SCALE + dy;
		PyTuple_SetItem(ret, i, PyFloat_FromDouble(baseline));
		pango_layout_iter_next_line(iter);
	}

	pango_layout_iter_free(iter);

	return ret;
}

static PyObject *
pango_GetLayoutCharPos(PyObject *self, PyObject *args) {

	int i, len, w, h;
	double baseline, x, y, width, height, dx, dy;
	void *LayoutObj;
	PangoLayout *layout;
	PangoLayoutIter *iter;
	PangoRectangle rect;
	PyObject *ret;
	PyObject *glyph_data;

	if (!PyArg_ParseTuple(args, "Oi", &LayoutObj, &len)) {
		return NULL;
	}

	layout = PyCObject_AsVoidPtr(LayoutObj);

	pango_layout_get_size(layout, &w, &h);
	dx = 0.0;
	if (pango_layout_get_alignment(layout) == PANGO_ALIGN_CENTER) {
		dx = -0.5 * ((double) w) / PANGO_SCALE;
	} else if (pango_layout_get_alignment(layout) == PANGO_ALIGN_RIGHT) {
		dx = -1.0 * ((double) w) / PANGO_SCALE;
	}


	ret = PyTuple_New(len);
	iter = pango_layout_get_iter(layout);

	dy = ((double) pango_layout_iter_get_baseline(iter)) / PANGO_SCALE;

	for (i = 0; i < len; i++) {
		glyph_data = PyTuple_New(5);
		pango_layout_iter_get_char_extents(iter, &rect);

		x = ((double) rect.x) / PANGO_SCALE + dx;
		PyTuple_SetItem(glyph_data, 0, PyFloat_FromDouble(x));

		y = -1.0 * ((double) rect.y) / PANGO_SCALE + dy;
		PyTuple_SetItem(glyph_data, 1, PyFloat_FromDouble(y));

		width = ((double) rect.width) / PANGO_SCALE;
		PyTuple_SetItem(glyph_data, 2, PyFloat_FromDouble(width));

		height = ((double) rect.height) / PANGO_SCALE;
		PyTuple_SetItem(glyph_data, 3, PyFloat_FromDouble(height));

		baseline = -1.0 * ((double) pango_layout_iter_get_baseline(iter))
				/ PANGO_SCALE + dy;
		PyTuple_SetItem(glyph_data, 4, PyFloat_FromDouble(baseline));

		pango_layout_iter_next_char(iter);

		PyTuple_SetItem(ret, i, glyph_data);
	}

	pango_layout_iter_free(iter);

	return ret;
}

static PyObject *
pango_GetLayoutClusterPos(PyObject *self, PyObject *args) {

	int i, len, w, h, index, prev_index;
	int ltr_flag, rtl_flag;
	double baseline, x, y, width, height, char_width, dx, dy;
	void *LayoutObj;
	PangoLayout *layout;
	PangoLayoutIter *iter;
	PangoLayoutIter *cluster_iter;
	PangoRectangle rect, cluster_rect;
	PangoDirection dir;
	PyObject *ret;
	PyObject *layout_data;
	PyObject *cluster_data;
	PyObject *cluster_range;
	PyObject *cluster_index_data;
	PyObject *cluster_index_range;
	PyObject *glyph_data;

	if (!PyArg_ParseTuple(args, "Oi", &LayoutObj, &len)) {
		return NULL;
	}

	layout = PyCObject_AsVoidPtr(LayoutObj);

	pango_layout_get_size(layout, &w, &h);
	dx = 0.0;
	if (pango_layout_get_alignment(layout) == PANGO_ALIGN_CENTER) {
		dx = -0.5 * ((double) w) / PANGO_SCALE;
	} else if (pango_layout_get_alignment(layout) == PANGO_ALIGN_RIGHT) {
		dx = -1.0 * ((double) w) / PANGO_SCALE;
	}


	ret = PyTuple_New(5);
	layout_data = PyList_New(0);
	cluster_data = PyList_New(0);
	cluster_index_data = PyList_New(0);

	PyTuple_SetItem(ret, 0, layout_data);
	PyTuple_SetItem(ret, 1, cluster_data);
	PyTuple_SetItem(ret, 2, cluster_index_data);

	iter = pango_layout_get_iter(layout);
	cluster_iter = pango_layout_get_iter(layout);

	prev_index = -1;
	rtl_flag = 0;
	ltr_flag = 0;

	dy = ((double) pango_layout_iter_get_baseline(iter)) / PANGO_SCALE;

	for (i = 0; i < len; i++) {
		glyph_data = PyTuple_New(6);

		//Processing EOL

		while (pango_layout_iter_get_baseline(cluster_iter) !=
				pango_layout_iter_get_baseline(iter)) {

			pango_layout_iter_get_char_extents(iter, &rect);

			x = ((double) rect.x) / PANGO_SCALE + dx;
			PyTuple_SetItem(glyph_data, 0, PyFloat_FromDouble(x));

			y = -1.0 * ((double) rect.y) / PANGO_SCALE + dy;
			PyTuple_SetItem(glyph_data, 1, PyFloat_FromDouble(y));

			width = ((double) rect.width) / PANGO_SCALE;
			PyTuple_SetItem(glyph_data, 2, PyFloat_FromDouble(width));

			height = ((double) rect.height) / PANGO_SCALE;
			PyTuple_SetItem(glyph_data, 3, PyFloat_FromDouble(height));

			baseline = -1.0 * ((double) pango_layout_iter_get_baseline(iter))
					/ PANGO_SCALE + dy;
			PyTuple_SetItem(glyph_data, 4, PyFloat_FromDouble(baseline));

			//index processing
			index=pango_layout_iter_get_index(iter);
			prev_index = index;
			PyTuple_SetItem(glyph_data, 5, PyInt_FromLong(index));

			PyList_Append(layout_data, glyph_data);

			pango_layout_iter_next_char(iter);
			i++;
			glyph_data = PyTuple_New(6);
		}

		pango_layout_iter_get_char_extents(iter, &rect);
		pango_layout_iter_get_cluster_extents(cluster_iter, NULL, &cluster_rect);

		//Processing cluster data
		//Layout_data: (x,y,width,height,base_line,byte_index)

		x = ((double) cluster_rect.x) / PANGO_SCALE + dx;
		PyTuple_SetItem(glyph_data, 0, PyFloat_FromDouble(x));

		y = -1.0 * ((double) cluster_rect.y) / PANGO_SCALE + dy;
		PyTuple_SetItem(glyph_data, 1, PyFloat_FromDouble(y));

		width = ((double) cluster_rect.width) / PANGO_SCALE;
		PyTuple_SetItem(glyph_data, 2, PyFloat_FromDouble(width));

		height = ((double) cluster_rect.height) / PANGO_SCALE;
		PyTuple_SetItem(glyph_data, 3, PyFloat_FromDouble(height));

		baseline = -1.0 * ((double) pango_layout_iter_get_baseline(cluster_iter))
				/ PANGO_SCALE + dy;
		PyTuple_SetItem(glyph_data, 4, PyFloat_FromDouble(baseline));

		//index processing
		index=pango_layout_iter_get_index(iter);
		if (prev_index != -1){
			if(index < prev_index){
				rtl_flag=1;
			}else if(index > prev_index){
				ltr_flag=1;
			}
		}
		prev_index = index;
		PyTuple_SetItem(glyph_data, 5, PyInt_FromLong(index));

		PyList_Append(layout_data, glyph_data);

		//Iterating over chars to next cluster

		if(cluster_rect.width > rect.width){
			char_width = rect.width;
			cluster_range = PyTuple_New(2);
			cluster_index_range = PyTuple_New(2);
			PyTuple_SetItem(cluster_range, 0, PyInt_FromLong(i));
			PyTuple_SetItem(cluster_index_range, 0,
					PyInt_FromLong(pango_layout_iter_get_index(iter)));
			while(cluster_rect.width > char_width){
				pango_layout_iter_next_char(iter);
				pango_layout_iter_get_char_extents(iter, &rect);
				char_width = char_width + rect.width;
				i++;
			}
			PyTuple_SetItem(cluster_range, 1, PyInt_FromLong(i + 1));
			PyTuple_SetItem(cluster_index_range, 1,
					PyInt_FromLong(pango_layout_iter_get_index(iter)));
			PyList_Append(cluster_data, cluster_range);
			PyList_Append(cluster_index_data, cluster_index_range);
		}

		pango_layout_iter_next_char(iter);
		pango_layout_iter_next_cluster(cluster_iter);
	}

	pango_layout_iter_free(iter);
	pango_layout_iter_free(cluster_iter);

	if(rtl_flag + ltr_flag == 2){
		PyTuple_SetItem(ret, 3, PyBool_FromLong(1));
	}else{
		PyTuple_SetItem(ret, 3, PyBool_FromLong(0));
	}

	dir = pango_find_base_dir(pango_layout_get_text(layout),-1);
	if(dir == PANGO_DIRECTION_RTL) {
		PyTuple_SetItem(ret, 4, PyBool_FromLong(1));
	} else {
		PyTuple_SetItem(ret, 4, PyBool_FromLong(0));
	}

	return ret;
}

static
PyMethodDef pango_methods[] = {
	{"get_version", pango_GetVersion, METH_VARARGS},
	{"get_fontmap", pango_GetFontMap, METH_VARARGS},
	{"create_pcctx", pango_CreateContext, METH_VARARGS},
	{"create_layout", pango_CreateLayout, METH_VARARGS},
	{"create_font_description", pango_CreateFontDescription, METH_VARARGS},
	{"set_layout_width", pango_SetLayoutWidth, METH_VARARGS},
	{"set_layout_font_description", pango_SetLayoutFontDescription, METH_VARARGS},
	{"set_layout_justify", pango_SetLayoutJustify, METH_VARARGS},
	{"set_layout_alignment", pango_SetLayoutAlignment, METH_VARARGS},
	{"set_layout_markup", pango_SetLayoutMarkup, METH_VARARGS},
	{"get_layout_pixel_size", pango_GetLayoutPixelSize, METH_VARARGS},
	{"layout_path", pango_LayoutPath, METH_VARARGS},
	{"get_layout_line_positions", pango_GetLayoutLinePos, METH_VARARGS},
	{"get_layout_char_positions", pango_GetLayoutCharPos, METH_VARARGS},
	{"get_layout_cluster_positions", pango_GetLayoutClusterPos, METH_VARARGS},
	{NULL, NULL}
};

void
init_libpango(void)
{
    Py_InitModule("_libpango", pango_methods);
    Pycairo_IMPORT;
}
