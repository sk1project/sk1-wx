/* _cairo - small module which provides extended binding to Cairo library.
 *
 * Copyright (C) 2011 by Igor E.Novikov
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
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

#include <Python.h>
#include <pycairo.h>
#include <cairo.h>
#include "Imaging.h"

static Pycairo_CAPI_t *Pycairo_CAPI;

/* redefine the ImagingObject struct defined in _imagingmodule.c */
typedef struct {
    PyObject_HEAD
    Imaging image;
} ImagingObject;

static PyObject *
cairo_DrawRectangle (PyObject *self, PyObject *args) {

	double x, y, w, h;
	PycairoContext *context;
	cairo_t *ctx;

	if (!PyArg_ParseTuple(args, "Odddd", &context, &x, &y, &w, &h)) {
		return NULL;
	}

	ctx = context -> ctx;
	cairo_rectangle(ctx, x, y, w, h);

	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *
cairo_GetSurfaceFirstPixel (PyObject *self, PyObject *args) {

	PycairoSurface *pysurface;
	cairo_surface_t *surface;
	unsigned char* src;

	if (!PyArg_ParseTuple(args, "O", &pysurface)) {
		return NULL;
	}

	surface = pysurface ->surface;
	src = cairo_image_surface_get_data( surface );
	return Py_BuildValue("[iii]", src[0], src[1], src[2]);
}

static PyObject *
cairo_ApplyTrafoToPath (PyObject *self, PyObject *args) {

	double m11, m12, m21, m22, dx, dy, x, y;
    int i;
	PycairoPath *pypath;
    cairo_path_t *path;
    cairo_path_data_t *data;

	if (!PyArg_ParseTuple(args, "Odddddd",
			&pypath, &m11, &m21, &m12, &m22, &dx, &dy)) {
		return NULL;
	}

    path = pypath ->path;

    for (i=0; i < path->num_data; i += path->data[i].header.length) {
        data = &path->data[i];
		switch (data->header.type) {
			case CAIRO_PATH_MOVE_TO:
				x = data[1].point.x;
				y = data[1].point.y;
				data[1].point.x = m11 * x + m12 * y + dx;
				data[1].point.y = m21 * x + m22 * y + dy;
				break;
			case CAIRO_PATH_LINE_TO:
				x = data[1].point.x;
				y = data[1].point.y;
				data[1].point.x = m11 * x + m12 * y + dx;
				data[1].point.y = m21 * x + m22 * y + dy;
				break;
			case CAIRO_PATH_CURVE_TO:
				x = data[1].point.x;
				y = data[1].point.y;
				data[1].point.x = m11 * x + m12 * y + dx;
				data[1].point.y = m21 * x + m22 * y + dy;

				x = data[2].point.x;
				y = data[2].point.y;
				data[2].point.x = m11 * x + m12 * y + dx;
				data[2].point.y = m21 * x + m22 * y + dy;

				x = data[3].point.x;
				y = data[3].point.y;
				data[3].point.x = m11 * x + m12 * y + dx;
				data[3].point.y = m21 * x + m22 * y + dy;
				break;
			case CAIRO_PATH_CLOSE_PATH:
				break;
        }
    }

	Py_INCREF(Py_None);
	return Py_None;
}


static PyObject *
cairo_GetPDPathFromPath (PyObject *self, PyObject *args) {

	double x0, y0, x1, y1, x2, y2;
    int i, path_counter;
	PycairoPath *pypath;
    cairo_path_t *path;
    cairo_path_data_t *data;

    PyObject *pd_paths;
    PyObject *pd_path;
    PyObject *pd_points;
    PyObject *pd_point;
    PyObject *pd_subpoint;

	if (!PyArg_ParseTuple(args, "O",
			&pypath)) {
		return NULL;
	}

	path_counter = 0;
    path = pypath ->path;

    pd_paths = PyList_New(0);
    pd_path = PyList_New(3);
    pd_points = PyList_New(0);

    for (i=0; i < path->num_data; i += path->data[i].header.length) {
        data = &path->data[i];
		switch (data->header.type) {
			case CAIRO_PATH_MOVE_TO:
				if(path_counter>0){
					PyList_SetItem(pd_path, 1, pd_points);
					PyList_Append(pd_paths, pd_path);
				}

				pd_path = PyList_New(3);
				pd_points = PyList_New(0);

				pd_point = PyList_New(0);
				x0 = data[1].point.x;
				y0 = data[1].point.y;
				PyList_Append(pd_point, PyFloat_FromDouble(x0));
				PyList_Append(pd_point, PyFloat_FromDouble(y0));
				PyList_SetItem(pd_path, 0, pd_point);
				PyList_SetItem(pd_path, 2, PyInt_FromLong(0L));
				path_counter++;
				break;

			case CAIRO_PATH_LINE_TO:
				pd_point = PyList_New(0);
				x0 = data[1].point.x;
				y0 = data[1].point.y;
				PyList_Append(pd_point, PyFloat_FromDouble(x0));
				PyList_Append(pd_point, PyFloat_FromDouble(y0));
				PyList_Append(pd_points, pd_point);
				break;

			case CAIRO_PATH_CURVE_TO:
				pd_point = PyList_New(0);

				pd_subpoint = PyList_New(0);
				x0 = data[1].point.x;
				y0 = data[1].point.y;
				PyList_Append(pd_subpoint, PyFloat_FromDouble(x0));
				PyList_Append(pd_subpoint, PyFloat_FromDouble(y0));
				PyList_Append(pd_point, pd_subpoint);

				pd_subpoint = PyList_New(0);
				x1 = data[2].point.x;
				y1 = data[2].point.y;
				PyList_Append(pd_subpoint, PyFloat_FromDouble(x1));
				PyList_Append(pd_subpoint, PyFloat_FromDouble(y1));
				PyList_Append(pd_point, pd_subpoint);

				pd_subpoint = PyList_New(0);
				x2 = data[3].point.x;
				y2 = data[3].point.y;
				PyList_Append(pd_subpoint, PyFloat_FromDouble(x2));
				PyList_Append(pd_subpoint, PyFloat_FromDouble(y2));
				PyList_Append(pd_point, pd_subpoint);

				PyList_Append(pd_point, PyInt_FromLong(0L));
				PyList_Append(pd_points, pd_point);
				break;

			case CAIRO_PATH_CLOSE_PATH:
				PyList_SetItem(pd_path, 2, PyInt_FromLong(1L));
				break;
        }
    }
    PyList_SetItem(pd_path, 1, pd_points);
    PyList_Append(pd_paths, pd_path);

    return pd_paths;
}

static PyObject *
cairo_ConvertMatrixToTrafo (PyObject *self, PyObject *args) {

	double m11, m12, m21, m22, dx, dy;
	PycairoMatrix *py_matrix;
	cairo_matrix_t *matrix;

	if (!PyArg_ParseTuple(args, "O", &py_matrix)) {
		return NULL;
	}

	matrix = &(py_matrix -> matrix);
	m11 = matrix -> xx;
	m21 = matrix -> yx;
	m12 = matrix -> xy;
	m22 = matrix -> yy;
	dx = matrix -> x0;
	dy = matrix -> y0;

	return Py_BuildValue("[dddddd]", m11, m21, m12, m22, dx, dy);
}

static PyObject *
cairo_DrawRGBImage (PyObject *self, PyObject *args) {

	PycairoSurface *pysurface;
	cairo_surface_t *surface;
	int width, height, offset, x, y, stride;
	ImagingObject* src;
	Imaging imaging;

	char* imagebuf;
	unsigned char* rgb;
	unsigned char *dest;

	if (!PyArg_ParseTuple(args, "OOii", &pysurface, &src, &width, &height)) {
		return NULL;
	}


	surface = pysurface -> surface;
	imaging = src -> image;

	cairo_surface_flush(surface);
	dest = cairo_image_surface_get_data(surface);
	stride = cairo_image_surface_get_stride(surface);
	offset=0;
	for(y=0; y<height; y++) {
		imagebuf = imaging -> image[y];
		for(x=0; x<width; x++) {
		    rgb = (unsigned char*)(imagebuf + x*4);
            dest[offset + x*4 + 2] = rgb[0];//R
            dest[offset + x*4 + 1] = rgb[1];//G
            dest[offset + x*4] = rgb[2];//B
            dest[offset + x*4 + 3] = 0;//A
			//resulted order BGR
        }
		offset += stride;
    }
    cairo_surface_mark_dirty(surface);

	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *
cairo_DrawRGBAImage (PyObject *self, PyObject *args) {

	PycairoSurface *pysurface;
	cairo_surface_t *surface;
	int width, height, offset, x, y, stride;
	ImagingObject* src;
	Imaging imaging;

	char* imagebuf;
	unsigned char* rgb;
	unsigned char *dest;

	if (!PyArg_ParseTuple(args, "OOii", &pysurface, &src, &width, &height)) {
		return NULL;
	}


	surface = pysurface -> surface;
	imaging = src -> image;

	cairo_surface_flush(surface);
	dest = cairo_image_surface_get_data(surface);
	stride = cairo_image_surface_get_stride(surface);
	offset=0;
	for(y=0; y<height; y++) {
		imagebuf = imaging -> image[y];
		for(x=0; x<width; x++) {
		    rgb = (unsigned char*)(imagebuf + x*4);
            dest[offset + x*4 + 2] = rgb[0]*rgb[3]/256;//R
            dest[offset + x*4 + 1] = rgb[1]*rgb[3]/256;//G
            dest[offset + x*4] = rgb[2]*rgb[3]/256;//B
            dest[offset + x*4 + 3] = rgb[3];//A
			//resulted order BGRA
        }
		offset += stride;
    }
    cairo_surface_mark_dirty(surface);

	Py_INCREF(Py_None);
	return Py_None;
}

static
PyMethodDef cairo_methods[] = {
	{"get_path_from_cpath", cairo_GetPDPathFromPath, METH_VARARGS},
	{"draw_rect", cairo_DrawRectangle, METH_VARARGS},
	{"get_trafo", cairo_ConvertMatrixToTrafo, METH_VARARGS},
	{"apply_trafo", cairo_ApplyTrafoToPath, METH_VARARGS},
	{"get_pixel", cairo_GetSurfaceFirstPixel, METH_VARARGS},
	{"draw_rgb_image", cairo_DrawRGBImage, METH_VARARGS},
	{"draw_rgba_image", cairo_DrawRGBAImage, METH_VARARGS},
	{NULL, NULL}
};

void
init_libcairo(void)
{
    Py_InitModule("_libcairo", cairo_methods);
    Pycairo_IMPORT;
}
