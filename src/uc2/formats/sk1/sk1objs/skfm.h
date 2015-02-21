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

#ifndef SKFM_H
#define SKFM_H

#include <Python.h>

#if defined(__cplusplus)
extern "C" {
#endif

PyObject * SKFM_PyCreateMetric(PyObject * self, PyObject * args);

extern DL_IMPORT(PyTypeObject) SKFontMetricType;
#define SKFontMetric_Check(obj) ((v)->ob_type == &SKFontMetricType)

#if defined(__cplusplus)
}
#endif

#endif
