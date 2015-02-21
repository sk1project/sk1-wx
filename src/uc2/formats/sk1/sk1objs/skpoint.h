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

#ifndef SKPOINT_H
#define SKPOINT_H

#if defined(__cplusplus)
extern "C" {
#endif

#include <Python.h>

/* the type of a coordinate. T_SKCOORD is used for struct member access in
   python and MUST correspond to the typedef */
typedef float SKCoord;
#define T_SKCOORD T_FLOAT

typedef struct {
    PyObject_HEAD
    SKCoord	x, y; 
} SKPointObject;

extern PyTypeObject SKPointType;

#define SKPoint_Check(v)		((v)->ob_type == &SKPointType)

PyObject * SKPoint_FromXY(SKCoord x, SKCoord y);

int skpoint_extract_xy(PyObject * sequence, double * x, double * y);

PyObject * skpoint_allocated(PyObject * self, PyObject * args);
PyObject * SKPoint_PyPolar(PyObject * self, PyObject * args);
PyObject * SKPoint_PyPoint(PyObject * self, PyObject * args);

#if defined(__cplusplus)
}
#endif

#endif
