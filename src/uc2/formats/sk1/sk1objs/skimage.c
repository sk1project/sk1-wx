/* Sketch - A Python-based interactive drawing program
 * Copyright (C) 1997, 1998, 1999, 2000 by Bernhard Herzog
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

#define __NO_MATH_INLINES
#include <math.h>
#include <Python.h>
#include <structmember.h>

#include "Imaging.h"

#include "_sketchmodule.h"
#include "sktrafo.h"
#include "skcolor.h"

#ifndef PI
#define PI 3.14159265358979323846264338327
#endif

/* redefine the ImagingObject struct defined in _imagingmodule.c */
/* there should be a better way to do this... */
typedef struct {
    PyObject_HEAD
    Imaging image;
} ImagingObject;


PyObject *
fill_rgb_xy(PyObject * self, PyObject * args)
{
    ImagingObject * image;
    int x, y, width, height;
    int xidx, yidx, otheridx, othercolor;
    double color[3];
    unsigned char *dest;

    if (!PyArg_ParseTuple(args, "Oii(ddd)", &image, &xidx, &yidx,
			  &color[0], &color[1], &color[2]))
	return NULL;

    if (xidx < 0 || xidx > 2 || yidx < 0 || yidx > 2 || xidx == yidx)
	return PyErr_Format(PyExc_ValueError,
			    "xidx and yidx must be different "
			    "and in the range [0..2] (x:%d, y:%d)",
			    xidx, yidx);

    otheridx = 3 - xidx - yidx;
    othercolor = 255 * color[otheridx];
    width = image->image->xsize - 1;
    height = image->image->ysize - 1;
    for (y = 0; y <= height; y++)
    {
	dest = (unsigned char*)(image->image->image32[y]);
	for (x = 0; x <= width; x++, dest += 4)
	{
	    dest[xidx] = (255 * x) / width;
	    dest[yidx] = (255 * (height - y)) / height;
	    dest[otheridx] = othercolor;
	}
    }

    Py_INCREF(Py_None);
    return Py_None;
}

PyObject *
fill_rgb_z(PyObject * self, PyObject * args)
{
    ImagingObject * image;
    int x, y, width, height;
    int idx, idx1, idx2, val1, val2;
    double r, g, b;
    unsigned char *dest;


    if (!PyArg_ParseTuple(args, "Oi(ddd)", &image, &idx, &r, &g, &b))
	return NULL;

    switch (idx)
    {
    case 0:
	idx1 = 1; val1 = 255 * g;
	idx2 = 2; val2 = 255 * b;
	break;
    case 1:
	idx1 = 0; val1 = 255 * r;
	idx2 = 2; val2 = 255 * b;
	break;
    case 2:
	idx1 = 0; val1 = 255 * r;
	idx2 = 1; val2 = 255 * g;
	break;
    default:
	PyErr_SetString(PyExc_ValueError, "idx must 0, 1 or 2");
	return NULL;
    }

    width = image->image->xsize - 1;
    height = image->image->ysize - 1;
    for (y = 0; y <= height; y++)
    {
	dest = (unsigned char*)(image->image->image32[y]);
	for (x = 0; x <= width; x++, dest += 4)
	{
	    dest[idx1] = val1;
	    dest[idx2] = val2;
	    dest[idx] = (255 * (height - y)) / height;
	}
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static void
hsv_to_rgb(double h, double s, double v, unsigned char * rgb)
{
    if (s == 0.0)
    {
	rgb[0] = rgb[1] = rgb[2] = 255 * v;
    }
    else
    {
	double p, q, t, f;
	int i;

	h *= 6;
	i = (int)h;
	f = h - i;
	p = v * (1.0 - s);
	q = v * (1.0 - s * f);
	t = v * (1.0 - s * (1.0 - f));
	switch (i)
	{
	case 0:
	case 6:
	    rgb[0] = 255 * v; rgb[1] = 255 * t; rgb[2] = 255 * p; break;
	case 1:
	    rgb[0] = 255 * q; rgb[1] = 255 * v; rgb[2] = 255 * p; break;
	case 2:
	    rgb[0] = 255 * p; rgb[1] = 255 * v; rgb[2] = 255 * t; break;
	case 3:
	    rgb[0] = 255 * p; rgb[1] = 255 * q; rgb[2] = 255 * v; break;
	case 4:
	    rgb[0] = 255 * t; rgb[1] = 255 * p; rgb[2] = 255 * v; break;
	case 5:
	    rgb[0] = 255 * v; rgb[1] = 255 * p; rgb[2] = 255 * q; break;
	}
    }
}

PyObject *
fill_hsv_xy(PyObject * self, PyObject * args)
{
    ImagingObject * image;
    int x, y, width, height;
    int xidx, yidx;
    double color[3];
    unsigned char *dest;

    if (!PyArg_ParseTuple(args, "Oii(ddd)", &image, &xidx, &yidx,
			  &color[0], &color[1], &color[2]))
	return NULL;

    if (xidx < 0 || xidx > 2 || yidx < 0 || yidx > 2 || xidx == yidx)
	return PyErr_Format(PyExc_ValueError,
			    "xidx and yidx must be different and in the range "
			    "[0..2] (x:%d, y:%d)",
			    xidx, yidx);

    width = image->image->xsize - 1;
    height = image->image->ysize - 1;
    for (y = 0; y <= height; y++)
    {
	dest = (unsigned char*)(image->image->image32[y]);
	for (x = 0; x <= width; x++, dest += 4)
	{
	    color[xidx] = (double)x / width;
	    color[yidx] = (double)(height - y) / height;
	    hsv_to_rgb(color[0], color[1], color[2], dest);
	}
    }

    Py_INCREF(Py_None);
    return Py_None;
}


PyObject *
fill_hsv_z(PyObject * self, PyObject * args)
{
    ImagingObject * image;
    int x, y, width, height;
    int idx;
    double hsv[3];
    unsigned char *dest;


    if (!PyArg_ParseTuple(args, "Oi(ddd)", &image, &idx,
			  &hsv[0], &hsv[1], &hsv[2]))
	return NULL;

    if (idx < 0 || idx > 2)
    {
	PyErr_SetString(PyExc_ValueError, "idx must be in the range [0,2]");
	return NULL;
    }

    width = image->image->xsize - 1;
    height = image->image->ysize - 1;
    for (y = 0; y <= height; y++)
    {
	dest = (unsigned char*)(image->image->image32[y]);
	for (x = 0; x <= width; x++, dest += 4)
	{
	    hsv[idx] = (double)(height - y) / height;
	    hsv_to_rgb(hsv[0], hsv[1], hsv[2], dest);
	}
    }

    Py_INCREF(Py_None);
    return Py_None;
}

/*
 *
 */

static void
fill_transformed_tile_gray(ImagingObject * image, ImagingObject * tile,
			   SKTrafoObject * trafo)
{
    int x, y, width, height, itx, ity;
    int tile_width, tile_height;
    double tx, ty, dx, dy;
    UINT8 *dest, **src;

    width = image->image->xsize;
    height = image->image->ysize;
    tile_width = tile->image->xsize;
    tile_height = tile->image->ysize;
    src = tile->image->image8;
    dx = trafo->m11; dy = trafo->m21;
    for (y = 0; y < height; y++)
    {
	dest = (UINT8*)(image->image->image32[y]);
	tx = y * trafo->m12 + trafo->v1;
	ty = y * trafo->m22 + trafo->v2;
	for (x = 0; x < width; x++, dest += 4, tx += dx, ty += dy)
	{
	    itx = ((int)tx) % tile_width;
	    if (itx < 0)
		itx += tile_width;
	    ity = ((int)ty) % tile_height;
	    if (ity < 0)
		ity += tile_height;
	    dest[0] = dest[1] = dest[2] = src[ity][itx];
	}
    }
}

static void
fill_transformed_tile_rgb(ImagingObject * image, ImagingObject * tile,
			  SKTrafoObject * trafo)
{
    int x, y, width, height, itx, ity;
    int tile_width, tile_height;
    double tx, ty, dx, dy;
    INT32 *dest, **src;

    width = image->image->xsize;
    height = image->image->ysize;
    tile_width = tile->image->xsize;
    tile_height = tile->image->ysize;
    src = tile->image->image32;
    dx = trafo->m11; dy = trafo->m21;
    for (y = 0; y < height; y++)
    {
	dest = image->image->image32[y];
	tx = y * trafo->m12 + trafo->v1;
	ty = y * trafo->m22 + trafo->v2;
	for (x = 0; x < width; x++, dest++, tx += dx, ty += dy)
	{
	    itx = ((int)tx) % tile_width;
	    if (itx < 0)
		itx += tile_width;
	    ity = ((int)ty) % tile_height;
	    if (ity < 0)
		ity += tile_height;
	    *dest = src[ity][itx];
	}
    }
}
	
				  

PyObject *
fill_transformed_tile(PyObject * self, PyObject * args)
{
    ImagingObject * image, *tile;
    SKTrafoObject * trafo;
    

    if (!PyArg_ParseTuple(args, "OOO!", &image, &tile, &SKTrafoType, &trafo))
	return NULL;

    if (strncmp(tile->image->mode, "RGB", 3) == 0)
    {
	fill_transformed_tile_rgb(image, tile, trafo);
    }
    else if (strcmp(tile->image->mode, "L") == 0)
    {
	fill_transformed_tile_gray(image, tile, trafo);
    }
    else
	return PyErr_Format(PyExc_TypeError,
			    "Images of mode %s cannot be used as tiles",
			    tile->image->mode);

    Py_INCREF(Py_None);
    return Py_None;
}

#define POS_FACTOR 65536
typedef struct {
    unsigned int pos;
    int r, g, b;
} GradientEntry;
typedef GradientEntry * Gradient;

static int
convert_color(PyObject * object, GradientEntry * entry)
{
    if (PyTuple_Check(object))
    {
	double red, green, blue;
	if (!PyArg_ParseTuple(object, "ddd", &red, &green, &blue))
	    return 0;
	entry->r = 255 * red;
	entry->g = 255 * green;
	entry->b = 255 * blue;
    }
    else if (SKColor_Check(object))
    {
	entry->r = 255 * ((SKColorObject*)object)->red;
	entry->g = 255 * ((SKColorObject*)object)->green;
	entry->b = 255 * ((SKColorObject*)object)->blue;
    }
    else
    {
	PyErr_SetString(PyExc_TypeError,
		    "color spec must be tuple of floats or color object");
	return 0;
    }
    return 1;
}
	
static Gradient
gradient_from_list(PyObject * list)
{
    int idx, length;
    Gradient gradient;

    length = PySequence_Length(list);
    if (length < 2)
    {
	PyErr_SetString(PyExc_TypeError, "gradient list too short");
	return NULL;
    }
    
    gradient = malloc(length * sizeof(GradientEntry));
    if (!gradient)
    {
	PyErr_NoMemory();
	return NULL;
    }

    for (idx = 0; idx < length; idx++)
    {
	int result;
	double pos;
	PyObject * item = PySequence_GetItem(list, idx);
	result = PyArg_ParseTuple(item, "dO&:"
				  "Gradient Element must be a tuple of "
				  "a float and a color", &pos,
				  convert_color, &(gradient[idx]));
	gradient[idx].pos = POS_FACTOR * pos;
	Py_DECREF(item);
	if (!result)
	    goto fail;
    }

    return gradient;

 fail:
    free(gradient);
    return NULL;
}

void
store_gradient_color(Gradient gradient, int length, double t,
		     unsigned char *dest)
{
    GradientEntry * entry = gradient;
    unsigned int it = (t < 0) ? 0 : POS_FACTOR *  t;

    if (it <= 0 || it >= POS_FACTOR)
    {
	if (it <= 0)
	    entry = gradient;
	else
	    entry = gradient + length - 1;
	dest[0] = entry->r;
	dest[1] = entry->g;
	dest[2] = entry->b;
    }
    else
    {
	int min = 0, max = length - 1, idx = (max + min) / 2;
	unsigned int tt;
	while (max - min != 1)
	{
	    if (gradient[idx].pos < it)
		min = idx;
	    else
		max = idx;
	    idx = (max + min) / 2;
	}
	entry = gradient + min;
	tt = (POS_FACTOR * (it - entry->pos)) / (entry[1].pos - entry->pos);
	dest[0] = entry->r + (tt * (entry[1].r - entry->r)) / POS_FACTOR;
	dest[1] = entry->g + (tt * (entry[1].g - entry->g)) / POS_FACTOR;
	dest[2] = entry->b + (tt * (entry[1].b - entry->b)) / POS_FACTOR;
    }
}

#define free_gradient(gradient) free(gradient)


static void
horizontal_axial_gradient(ImagingObject * image, Gradient gradient, int length,
			  int x0, int x1)
{
    unsigned char *dest;
    int maxx, height, x, y;
    double factor = 1.0 / (x1 - x0);

    maxx = image->image->xsize - x0;
    height = image->image->ysize;

    dest = (unsigned char*)(image->image->image32[0]);
    for (x = -x0; x < maxx; x++, dest += 4)
    {
	store_gradient_color(gradient, length, factor * x, dest);
    }

    for (y = 1; y < height; y++)
    {
	memcpy(image->image->image32[y], image->image->image32[0],
	       4 * image->image->xsize);
    }
}    

static void
vertical_axial_gradient(ImagingObject * image, Gradient gradient, int length,
			int y0, int y1)
{
    INT32 *dest;
    int height, width, x, y;
    double factor = 1.0 / (y1 - y0);

    width = image->image->xsize;
    height = image->image->ysize;
    for (y = 0; y < height; y++)
    {
	dest = image->image->image32[y];
	store_gradient_color(gradient, length, factor * (y - y0),
			     (unsigned char*)dest);
	for (x = 1; x < width; x++)
	{
	    dest[x] = dest[0];
	}
    }
}    


#define ANGLE_EPSILON 0.01
PyObject *
fill_axial_gradient(PyObject * self, PyObject * args)
{
    ImagingObject * image;
    int x, y, maxx, maxy;
    double x0, y0, x1, y1, dx, dy, angle;
    int length;
    unsigned char *dest;
    PyObject * list;
    Gradient gradient;

    if (!PyArg_ParseTuple(args, "OOdddd", &image, &list, &x0, &y0, &x1, &y1))
	return NULL;

    if (!PySequence_Check(list))
    {
	PyErr_SetString(PyExc_TypeError,
			"gradient argument must be a sequence");
	return NULL;
    }

    if (x0 == x1 && y0 == y1)
    {
	Py_INCREF(Py_None);
	return Py_None;
    }

    length = PySequence_Length(list);
    gradient = gradient_from_list(list);
    if (!gradient)
	return NULL;

    dx = x1 - x0; dy = y1 - y0;
    angle = atan2(dy, dx);

    if (fabs(angle) < ANGLE_EPSILON || fabs(fabs(angle) - PI) < ANGLE_EPSILON)
    {
	horizontal_axial_gradient(image, gradient, length,
				  (int)(ceil(x0)), (int)(ceil(x1)));
    }
    else if (fabs(angle - PI/2) < ANGLE_EPSILON
	     || fabs(angle + PI/2) < ANGLE_EPSILON)
    {
	vertical_axial_gradient(image, gradient, length,
				(int)(ceil(y0)), (int)(ceil(y1)));
    }
    else
    {
	double t, dt;
	double lensqr = hypot(dx, dy) ; /*(double)dx * dx +  (double)dy * dy;*/
	lensqr *= lensqr;
	dt = dx / lensqr;
	
	maxx = image->image->xsize;
	maxy = image->image->ysize;
	for (y = 0; y < maxy; y++)
	{
	    dest = (unsigned char*)(image->image->image32[y]);
	    t = (dx * -x0 + dy * (y - y0)) / lensqr;
	    for (x = 0; x < maxx; x++, dest += 4, t += dt)
	    {
		store_gradient_color(gradient, length, t, dest);
	    }
	}
    }
    free_gradient(gradient);

    Py_INCREF(Py_None);
    return Py_None;
}

#if 0
PyObject *
fill_axial_gradient(PyObject * self, PyObject * args)
{
    ImagingObject * image;
    int x, y, maxx, maxy, dx, dy;
    int x0, y0, x1, y1;
    int length;
    unsigned char *dest;
    PyObject * list;
    Gradient gradient;

    if (!PyArg_ParseTuple(args, "OOiiii", &image, &list, &x0, &y0, &x1, &y1))
	return NULL;

    if (!PySequence_Check(list))
    {
	PyErr_SetString(PyExc_TypeError,
			"gradient argument must be a sequence");
	return NULL;
    }

    if (x0 == x1 && y0 == y1)
    {
	Py_INCREF(Py_None);
	return Py_None;
    }

    length = PySequence_Length(list);
    gradient = gradient_from_list(list);
    if (!gradient)
	return NULL;

    dx = x1 - x0; dy = y1 - y0;

    if (dy == 0)
    {
	horizontal_axial_gradient(image, gradient, length, x0, x1);
    }
    else if (dx == 0)
    {
	vertical_axial_gradient(image, gradient, length, y0, y1);
    }
    else
    {
	double t, dt;
	double lensqr = hypot(dx, dy) ; /*(double)dx * dx +  (double)dy * dy;*/
	lensqr *= lensqr;
	dt = dx / lensqr;
	
	maxx = image->image->xsize - x0;
	maxy = image->image->ysize - y0;
	for (y = -y0; y < maxy; y++)
	{
	    dest = (unsigned char*)(image->image->image32[y + y0]);
	    t = (dx * -x0 + dy * y) / lensqr;
	    for (x = -x0; x < maxx; x++, dest += 4, t += dt)
	    {
		store_gradient_color(gradient, length, t, dest);
	    }
	}
    }
    free_gradient(gradient);

    Py_INCREF(Py_None);
    return Py_None;
}
#endif

PyObject *
fill_radial_gradient(PyObject * self, PyObject * args)
{
    ImagingObject * image;
    int x, y, maxx, maxy;
    int cx, cy, r0, r1;
    double factor;
    int length;
    unsigned char *dest;
    PyObject * list;
    Gradient gradient;

    if (!PyArg_ParseTuple(args, "OOiiii", &image, &list, &cx, &cy, &r0, &r1))
	return NULL;

    if (!PySequence_Check(list))
    {
	PyErr_SetString(PyExc_TypeError,
			"gradient argument must be a sequence");
	return NULL;
    }

    length = PySequence_Length(list);
    gradient = gradient_from_list(list);
    if (!gradient)
	return NULL;

    factor = 1.0 / (r1 - r0);
    maxx = image->image->xsize - cx;
    maxy = image->image->ysize - cy;
    for (y = -cy; y < maxy; y++)
    {
	dest = (unsigned char*)(image->image->image32[y + cy]);
	for (x = -cx; x < maxx; x++, dest += 4)
	{
	    store_gradient_color(gradient, length, factor * (hypot(x, y) - r0),
				 dest);
	}
    }
    
    free_gradient(gradient);

    Py_INCREF(Py_None);
    return Py_None;
}

PyObject *
fill_conical_gradient(PyObject * self, PyObject * args)
{
    ImagingObject * image;
    int x, y, maxx, maxy;
    int cx, cy;
    double angle, t;
    int length;
    unsigned char *dest;
    PyObject * list;
    Gradient gradient;

    if (!PyArg_ParseTuple(args, "OOiid", &image, &list, &cx, &cy, &angle))
	return NULL;

    if (!PySequence_Check(list))
    {
	PyErr_SetString(PyExc_TypeError,
			"gradient argument must be a sequence");
	return NULL;
    }

    length = PySequence_Length(list);
    gradient = gradient_from_list(list);
    if (!gradient)
	return NULL;

    angle = fmod(angle, 2 * PI);
    if (angle < -PI)
	angle += 2 * PI;
    else if (angle > PI)
	angle -= 2 * PI;
    
    maxx = image->image->xsize - cx;
    maxy = image->image->ysize - cy;
    for (y = -cy; y < maxy; y++)
    {
	dest = (unsigned char*)(image->image->image32[y + cy]);
	for (x = -cx; x < maxx; x++, dest += 4)
	{
	    if (x || y)
	    {
		t = atan2(y, x) - angle;
		if (t < -PI)
		    t += 2 * PI;
		else if (t > PI)
		    t -= 2 * PI;
		t = fabs(t / PI);
	    }
	    else
		t = 0;
	    store_gradient_color(gradient, length, t, dest);
	}
    }
    
    free_gradient(gradient);

    Py_INCREF(Py_None);
    return Py_None;
}


static char * hexdigit = "0123456789ABCDEF";

static void
write_ps_hex_rgb(FILE * out, int width, int height, char ** data,
		 int line_length, char * prefix)
{
    int x, y;
    char * line;
    int written = 0;

    for (y = 0; y < height; y++)
    {
	line = data[y];

	for (x = 0; x < width; x++)
	{
	    if (x % 4 == 3)
		continue;

	    if (written == 0 && prefix)
	    {
		fputs(prefix, out);
	    }
	    putc(hexdigit[(int)(line[x] >> 4) & 0x0F], out);
	    putc(hexdigit[(int)(line[x] & 0x0F)], out);
	    written += 2;

	    if (written > line_length)
	    {
		putc('\n', out);
		written = 0;
	    }
	}
    }

    if (written)
	putc('\n', out);
}

static void
write_ps_hex_gray(FILE * out, int width, int height, char ** data,
		  int line_length, char * prefix)
{
    int x, y;
    char * line;
    int written = 0;

    for (y = 0; y < height; y++)
    {
	line = data[y];

	for (x = 0; x < width; x++)
	{
	    if (written == 0 && prefix)
	    {
		fputs(prefix, out);
	    }
	    putc(hexdigit[(int)(line[x] >> 4) & 0x0F], out);
	    putc(hexdigit[(int)(line[x] & 0x0F)], out);
	    written += 2;

	    if (written > line_length)
	    {
		putc('\n', out);
		written = 0;
	    }
	}
    }

    if (written)
	putc('\n', out);
}


PyObject *
skimage_write_ps_hex(PyObject * self, PyObject * args)
{
    PyObject * pyfile;
    ImagingObject * imobj;
    int line_length = 80;
    char * prefix = NULL;

    if (!PyArg_ParseTuple(args, "OO!|is", &imobj, &PyFile_Type, &pyfile,
			  &line_length, &prefix))
	return NULL;

    
    line_length = line_length - 2;
    if (line_length < 0)
	line_length = 0;
    if (imobj->image->pixelsize == 4)
	write_ps_hex_rgb(PyFile_AsFile(pyfile), imobj->image->linesize,
			 imobj->image->ysize, imobj->image->image,
			 line_length, prefix);
    else if (imobj->image->pixelsize == 1)
	write_ps_hex_gray(PyFile_AsFile(pyfile), imobj->image->linesize,
			  imobj->image->ysize, imobj->image->image,
			  line_length, prefix);

    Py_INCREF(Py_None);
    return Py_None;
}
