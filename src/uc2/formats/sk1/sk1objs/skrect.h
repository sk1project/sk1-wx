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


#ifndef SKRECT_MODULE_H
#define SKRECT_MODULE_H

#if defined(__cplusplus)
extern "C" {
#endif

#include "skpoint.h"

typedef struct {
    PyObject_HEAD
    SKCoord	left, top, right, bottom;
} SKRectObject;

extern PyTypeObject SKRectType;
#define SKRect_Check(v)		((v)->ob_type == &SKRectType)

extern SKRectObject * SKRect_InfinityRect;
extern SKRectObject * SKRect_EmptyRect;

PyObject * SKRect_FromDouble(double left, double top,
			     double right, double bottom);

int SKRect_ContainsXY(SKRectObject * self, double x, double y);

/* SKRect_AddXY and Co modify self! see comments in skrectmodule.c */
int SKRect_AddXY(SKRectObject * self, double x, double y);
int SKRect_AddX(SKRectObject * self, double x);
int SKRect_AddY(SKRectObject * self, double y);



PyObject * skrect_allocated(PyObject * self, PyObject * args);
PyObject * skrect_PointsToRect(PyObject * self, PyObject * args);
PyObject * skrect_intersect(PyObject * self, PyObject * args);
PyObject * skrect_unionrects(PyObject * self, PyObject * args);
PyObject * skrect_skrect(PyObject * self, PyObject * args);

#if defined(__cplusplus)
}
#endif

#endif
