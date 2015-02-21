/* Sketch - A Python-based interactive drawing program
 * Copyright (C) 1997, 1998, 1999, 2000, 2001, 2002, 2006 by Bernhard Herzog
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

#include <math.h>
#include <Python.h>
#include <structmember.h>

#include "_sketchmodule.h"
#include "skcolor.h"

/*
 *	RGBColor
 */

#define SKCOLOR_COUNT_ALLOC 1
#define SKCOLOR_SUBALLOCATE 1


#if SKCOLOR_COUNT_ALLOC
static int skcolor_allocated = 0;
#endif

#if SKCOLOR_SUBALLOCATE
#define BLOCK_SIZE	1000	/* 1K less typical malloc overhead */
#define N_COLOROBJECTS	(BLOCK_SIZE / sizeof(SKColorObject))
static SKColorObject *
fill_free_list(void)
{
    SKColorObject *p, *q;
    p = PyMem_Malloc(sizeof(SKColorObject) * N_COLOROBJECTS);
    if (p == NULL)
	return (SKColorObject *)PyErr_NoMemory();
    q = p + N_COLOROBJECTS;
    while (--q > p)
	q->ob_type = (PyTypeObject*)(q-1);
    q->ob_type = NULL;
    return p + N_COLOROBJECTS - 1;
}

static SKColorObject *free_list = NULL;
#endif /* SKCOLOR_SUBALLOCATE */

#define SKColor_CHECK_COMPONENT(comp) (0.0 <= (comp) && (comp) <= 1.0)
PyObject *
SKColor_FromRGB(double red, double green, double blue)
{
    SKColorObject * self;

    if (!SKColor_CHECK_COMPONENT(red)
	|| !SKColor_CHECK_COMPONENT(green)
	|| !SKColor_CHECK_COMPONENT(blue))
    {
	/*fprintf(stderr, "SKColor_FromRGB %g, %g, %g\n", red, green, blue);*/
	PyErr_SetString(PyExc_ValueError,
			"color components must be in the range [0.0 .. 1.0]");
	return NULL;
    }
    
#if SKCOLOR_SUBALLOCATE
    if (free_list == NULL) {
	if ((free_list = fill_free_list()) == NULL)
	    return NULL;
    }
    self = free_list;
    free_list = (SKColorObject *)(free_list->ob_type);
    self->ob_type = &SKColorType;
    _Py_NewReference(self);
#else
    self = PyObject_New(SKColorObject, &SKColorType);
    if (!self)
	return NULL;
#endif
    self->red = red;
    self->green = green;
    self->blue = blue;

#if SKCOLOR_COUNT_ALLOC
    skcolor_allocated++;
#endif

    return (PyObject*)self;
}

static void
skcolor_dealloc(SKColorObject * self)
{
#if SKCOLOR_SUBALLOCATE
    self->ob_type = (PyTypeObject*)free_list;
    free_list = self;
#else
    PyObject_Del(self);
#endif
#if SKCOLOR_COUNT_ALLOC
    skcolor_allocated--;
#endif
}

#define COMPARE(c1,c2) ((c1) < (c2) ? -1 : ((c1) > (c2) ? +1 : 0 ))
static int
skcolor_compare(SKColorObject * v, SKColorObject * w)
{
    int result;

    if ((result = COMPARE(v->red, w->red)) != 0)
	return result;
    if ((result = COMPARE(v->green, w->green)) != 0)
	return result;
    return COMPARE(v->blue, w->blue);
}
#undef COMPARE

static long
skcolor_hash(SKColorObject * self)
{
    long x;

    x = self->red * 65535.0;
    x = (255 * x) ^ (long)(self->green * 65535.0);
    x = (255 * x) ^ (long)(self->blue * 65535.0);
    
    if (x == -1)
	return -2;
    return x;
}

static PyObject *
skcolor_repr(SKColorObject * self)
{
    char buf[1000];
    sprintf(buf, "RGBColor(%g,%g,%g)", self->red, self->green, self->blue);
    return PyString_FromString(buf);
}


static int
skcolor_length(PyObject *self)
{
    return 3;
}

static PyObject *
skcolor_concat(PyObject *self, PyObject *bb)
{
    PyErr_SetString(PyExc_RuntimeError,
		    "concat not supported for SKColorObjects");
    return NULL;
}

static PyObject *
skcolor_repeat(PyObject *self, int n)
{
    PyErr_SetString(PyExc_RuntimeError,
		    "repeat not supported for SKColorObjects");
    return NULL;
}

static PyObject *
skcolor_item(SKColorObject *self, int i)
{
    double item;
    switch (i)
    {
    case 0:
	item = self->red;
	break;
    case 1:
	item = self->green;
	break;
    case 2:
	item = self->blue;
	break;
    default:
	PyErr_SetString(PyExc_IndexError, "index must be 0, 1 or 2");
	return NULL;
    }

    return PyFloat_FromDouble(item);
}

static PyObject *
skcolor_slice(PyObject *self, int ilow, int ihigh)
{
    PyErr_SetString(PyExc_RuntimeError,
		    "slicing not supported for SKColorObjects");
    return NULL;
}

static PySequenceMethods skcolor_as_sequence = {
	skcolor_length,			/*sq_length*/
	skcolor_concat,			/*sq_concat*/
	skcolor_repeat,			/*sq_repeat*/
	(intargfunc)skcolor_item,	/*sq_item*/
	skcolor_slice,			/*sq_slice*/
	0,				/*sq_ass_item*/
	0,				/*sq_ass_slice*/
};



/*
 *	Python methods
 */

static PyObject *
skcolor_blend(SKColorObject * self, PyObject * args)
{
    SKColorObject * color2;
    double frac1, frac2;

    if (!PyArg_ParseTuple(args, "O!dd", &SKColorType, &color2, &frac1, &frac2))
	return NULL;

    return SKColor_FromRGB(frac1 * self->red + frac2 * color2->red,
			   frac1 * self->green + frac2 * color2->green,
			   frac1 * self->blue + frac2 * color2->blue);
}


#define OFF(x) offsetof(SKColorObject, x)
static struct memberlist skcolor_memberlist[] = {
    {"red",		T_FLOAT,	OFF(red),	RO},
    {"green",		T_FLOAT,	OFF(green),	RO},
    {"blue",		T_FLOAT,	OFF(blue),	RO},
    {NULL} 
};
#undef OFF


static struct PyMethodDef skcolor_methods[] = {
    {"Blend",		(PyCFunction)skcolor_blend,		1},
    {NULL,	NULL}
};


static PyObject *
skcolor_getattr(PyObject * self, char * name)
{
    PyObject * result;

    result = Py_FindMethod(skcolor_methods, self, name);
    if (result != NULL)
	return result;
    PyErr_Clear();

    return PyMember_Get((char *)self, skcolor_memberlist, name);
}



PyTypeObject SKColorType = {
	PyObject_HEAD_INIT(NULL)
	0,
	"skcolor",
	sizeof(SKColorObject),
	0,
	(destructor)skcolor_dealloc,	/*tp_dealloc*/
	(printfunc)NULL,		/*tp_print*/
	skcolor_getattr,		/*tp_getattr*/
	0,				/*tp_setattr*/
	(cmpfunc)skcolor_compare,	/*tp_compare*/
	(reprfunc)skcolor_repr,		/*tp_repr*/
	0,				/*tp_as_number*/
	&skcolor_as_sequence,		/*tp_as_sequence*/
	0,				/*tp_as_mapping*/
	(hashfunc)&skcolor_hash,	/*tp_hash*/
	(ternaryfunc)0,			/*tp_call */
};


/*
 *		Module Functions
 */

/*
 *	skcolor.RGBColor(RED, GREEN, BLUE)
 */
PyObject *
skcolor_rgbcolor(PyObject * self, PyObject * args)
{
    double red, green, blue;

    if (!PyArg_ParseTuple(args, "ddd", &red, &green, &blue))
	return NULL;

    return SKColor_FromRGB(red, green, blue);
}

PyObject *
skcolor_num_allocated(PyObject * self, PyObject * args)
{
#if SKCOLOR_COUNT_ALLOC
    return PyInt_FromLong(skcolor_allocated);
#else
    return PyInt_FromLong(-1);
#endif
}
