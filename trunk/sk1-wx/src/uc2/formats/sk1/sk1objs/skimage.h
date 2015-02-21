/* Sketch - A Python-based interactive drawing program
 * Copyright (C) 1996, 1997, 1998 by Bernhard Herzog
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Library General Public
 * License as published by the Free Software Foundation; either
 * version 2 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Library General Public License for more details.
 *
 * You should have received a copy of the GNU Library General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

#ifndef SKIMAGE_H
#define SKIMAGE_H

#include <Python.h>

PyObject * skimage_write_ps_hex(PyObject * self, PyObject * args);
PyObject * fill_conical_gradient(PyObject * self, PyObject * args);
PyObject * fill_radial_gradient(PyObject * self, PyObject * args);
PyObject * fill_axial_gradient(PyObject * self, PyObject * args);
PyObject * fill_transformed_tile(PyObject * self, PyObject * args);
PyObject * fill_hsv_z(PyObject * self, PyObject * args);
PyObject * fill_hsv_xy(PyObject * self, PyObject * args);
PyObject * fill_rgb_z(PyObject * self, PyObject * args);
PyObject * fill_rgb_xy(PyObject * self, PyObject * args);


#endif
