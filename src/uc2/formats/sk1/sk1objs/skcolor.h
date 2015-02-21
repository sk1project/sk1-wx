/* Sketch - A Python-based interactive drawing program
 * Copyright (C) 1998 by Bernhard Herzog
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


#ifndef SKCOLOR_H
#define SKCOLOR_H

#if defined(__cplusplus)
extern "C" {
#endif

typedef struct {
    PyObject_HEAD
    float		red;
    float		green;
    float		blue;
} SKColorObject;

extern PyTypeObject SKColorType;
#define SKColor_Check(v)		((v)->ob_type == &SKColorType)

PyObject * SKColor_FromRGB(double red, double green, double blue);


typedef union
{
    unsigned short s[2];
    unsigned char c[4];
}  SKDitherInfo;




extern PyTypeObject SKVisualType;
#define SKVisual_Check(v)		((v)->ob_type == &SKVisualType)


/* Python functions */

PyObject * skcolor_rgbcolor(PyObject * self, PyObject * args);
PyObject * skcolor_num_allocated(PyObject * self, PyObject * args);

#if defined(__cplusplus)
}
#endif

#endif /* SKCOLOR_H */
