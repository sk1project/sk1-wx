/* Sketch - A Python-based interactive drawing program
 * Copyright (C) 1997, 1998 by Bernhard Herzog
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


#ifndef SKTRAFO_MODULE_H
#define SKTRAFO_MODULE_H

#if defined(__cplusplus)
extern "C" {
#endif

#include "skpoint.h"

typedef struct {
    PyObject_HEAD
    double	m11, m21, m12, m22, v1, v2;
} SKTrafoObject;

extern PyTypeObject SKTrafoType;

#define SKTrafo_Check(v)		((v)->ob_type == &SKTrafoType)

PyObject * SKTrafo_FromDouble(double m11, double m21, double m12, double m22,
			      double v1, double v2);

void SKTrafo_TransformXY(PyObject * trafo, double x, double y,
			 SKCoord * out_x, SKCoord * out_y);

void SKTrafo_DTransformXY(PyObject * trafo, double x, double y,
			  SKCoord * out_x, SKCoord * out_y);

extern PyObject * SKTrafo_ExcSingular;

PyObject * sktrafo_rotation(PyObject * self, PyObject * args);
PyObject * sktrafo_translation(PyObject * self, PyObject * args);
PyObject * sktrafo_scale(PyObject * self, PyObject * args);
PyObject * sktrafo_sktrafo(PyObject * self, PyObject * args);
PyObject * sktrafo_allocated(PyObject * self, PyObject * args);

#if defined(__cplusplus)
}
#endif

#endif /* SKTRAFO_MODULE_H */
