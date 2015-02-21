/* Sketch - A Python-based interactive drawing program
 * Copyright (C) 1996, 1997, 1998, 2001, 2002, 2006 by Bernhard Herzog
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

/* A Python Object, `SKPoint', representing a single 2D point or vector
 * with float coordinates.
 *
 * SKPoint objects are immutable.
 */

#include <math.h>
#include <Python.h>
#include <structmember.h>

#include "skpoint.h"

#if defined(PY_MAJOR_VERSION) && PY_VERSION_HEX >= 0x02010000
/* Beginning with Python 2.1, use the new style numbers */
#define USE_NEWSTYLE_NUMBERS
#endif

#define SKPOINT_COUNT_ALLOC 1

#if SKPOINT_COUNT_ALLOC
static int allocated = 0;
#endif


PyObject *
SKPoint_FromXY(SKCoord x, SKCoord y)
{
    SKPointObject * self;

    self = PyObject_New(SKPointObject, &SKPointType);
    if (self == NULL)
	return NULL;

    self->x = x;
    self->y = y;

#if SKPOINT_COUNT_ALLOC
    allocated += 1;
#endif

    return (PyObject*)self;
}

static void
skpoint_dealloc(SKPointObject * self)
{
    PyObject_Del(self);
#if SKPOINT_COUNT_ALLOC
    allocated -= 1;
#endif
}


static int
skpoint_compare(SKPointObject * v, SKPointObject * w)
{
    int ret;

    if (!SKPoint_Check(v) || !SKPoint_Check(w))
    {
	return strcmp(v->ob_type->tp_name, w->ob_type->tp_name);
    }

    ret = (v->x < w->x) ?  -1  :  (v->x > w->x) ? +1 : 0;

    if (ret)
	return ret;

    return (v->y < w->y) ?  -1  :  (v->y > w->y) ? +1 : 0;
}

static PyObject *
skpoint_repr(SKPointObject * self)
{
    char buf[1000];
    sprintf(buf, "Point(%g, %g)", self->x, self->y);
    return PyString_FromString(buf);
}


/* mathematical operations */
#define POINT(w) ((SKPointObject*)w)

static PyObject *
skpoint_add(SKPointObject * v, PyObject * w)
{
    if (SKPoint_Check(v) && SKPoint_Check(w))
	return SKPoint_FromXY(v->x + POINT(w)->x, v->y + POINT(w)->y);
    
#ifdef USE_NEWSTYLE_NUMBERS
    Py_INCREF(Py_NotImplemented);
    return Py_NotImplemented;
#else
    PyErr_SetString(PyExc_TypeError, "Points must be added to Points");
    return NULL;
#endif
}

static PyObject *
skpoint_sub(SKPointObject * v, PyObject * w)
{
    if (SKPoint_Check(v) && SKPoint_Check(w))
	return SKPoint_FromXY(v->x - POINT(w)->x, v->y - POINT(w)->y);

#ifdef USE_NEWSTYLE_NUMBERS
    Py_INCREF(Py_NotImplemented);
    return Py_NotImplemented;
#else
    PyErr_SetString(PyExc_TypeError, "Points must be subtracted from Points");
    return NULL;
#endif
}


#define FLOAT_AS_DOUBLE(object, var) \
(var = PyFloat_AsDouble(object), \
 PyErr_Occurred() ? (PyErr_Clear(), 0) : 1)


static PyObject *
skpoint_multiply(PyObject * v, PyObject * w)
{
    /* We want to allow products of two points as well as products of
     * points and numbers. Python garantees that at least one of the
     * operands is a point, so we first test whether both operands are
     * points and compute the inner product in that case. Otherwise, at
     * least one parameter must be a number, so try to convert that
     * number to float and return the product of the number and the
     * point
     */

    double number;
    SKPointObject * point = NULL;

    if (SKPoint_Check(v) && SKPoint_Check(w))
    {
	/* Both are points, return the inner product */
	return PyFloat_FromDouble(POINT(v)->x * POINT(w)->x
				  + POINT(v)->y * POINT(w)->y);
    }
    else if (FLOAT_AS_DOUBLE(w, number))
    {
	/* w is a number, so v must be the point */
	point = (SKPointObject*)v;
    }
    else if (FLOAT_AS_DOUBLE(v, number))
    {
	/* v is a number, so w must be the point */
	point = (SKPointObject*)w;
    }

    if (point)
    {
	return SKPoint_FromXY(number * point->x, number * point->y);
    }

#ifdef USE_NEWSTYLE_NUMBERS
    Py_INCREF(Py_NotImplemented);
    return Py_NotImplemented;
#else
    PyErr_SetString(PyExc_TypeError,
		    "Point can only be multiplied by a Point or a number");
    return NULL;
#endif
}

static PyObject *
skpoint_divide(PyObject * v, PyObject * w)
{
    /* we can only divide if v is a point and w is a number. Since one
     * of the operands will always be a number, we only have to check w.
     */
    double number;

    if (FLOAT_AS_DOUBLE(w, number))
    {
	return SKPoint_FromXY(POINT(v)->x / number, POINT(v)->y / number);
    }
#ifdef USE_NEWSTYLE_NUMBERS
    Py_INCREF(Py_NotImplemented);
    return Py_NotImplemented;
#else
    PyErr_SetString(PyExc_TypeError, "Point can only be divided by a number");
    return NULL;
#endif
}

static PyObject *
skpoint_neg(SKPointObject * self)
{
    return SKPoint_FromXY(-self->x, -self->y);
}

static PyObject *
skpoint_pos(PyObject * self)
{
    Py_INCREF(self);
    return (PyObject *)self;
}

static PyObject *
skpoint_abs(SKPointObject * self)
{
    return PyFloat_FromDouble(hypot(self->x, self->y));
}


static int
skpoint_nonzero(SKPointObject * self)
{
    return self->x != 0.0 || self->y != 0.0;
}

/* this coercion can be dangerous: We want to be able to multiply a
 * point with a number. To achieve this, we must convert the second
 * operand to a float object.
 *
 * Unfortunately we don't know whether it really was the second operand
 * or even if the results will be multiplied or added. NUMBER + POINT
 * calls this function to coerce, but calls NUMBER's operator method,
 * treating the point object as a float object. In the current Python
 * implementation on Linux, this doesn't lead to segmentation faults,
 * because the C-struct of a float object is at least not larger than
 * the struct for a point, the results are meaningless, though.
 *
 * Fortunately, for multiplication, python swaps the operands if the
 * second operand is a sequence before it attempts to coerce, so that
 * skpoint_multiply is finally called as intended.
 *
 * Another useful coercion would convert sequences of two numbers to
 * point objects, allowing to write e. g. `p + (1, 0)'. This doesn't
 * work, because skpoint_coerce will never be called (at least not in
 * Python 1.5.1)
 *
 * Coerce will only be called when compiled for Python version older
 * than 2.1.
 */
static int
skpoint_coerce(PyObject ** pv, PyObject ** pw)
{
    PyObject * as_float = PyNumber_Float(*pw);

    if (as_float)
    {
	*pw = as_float;
	Py_INCREF(*pv);
	return 0;
    }
    
    return -1;
}

/* point as sequence */

static int
skpoint_length(PyObject *self)
{
    return 2;
}

/* Concatenate Points.
 *
 * Conceptually, points treated as sequences cannot be concatenated. It
 * doesn't make sense: the concatenation of two points in R^2 yields a
 * point in R^4 ?.
 *
 * Normally, we should be able to set the corresponding field in
 * tp_as_sequence to 0. This does not work as some code in the python
 * interpreter just tests whether tp_as_sequence is not NULL and doesn't
 * test sq_concat. Thus we have to provide this method and it should
 * raise an exception to indicte that concat is imposssible.
 *
 * Annoyingly, even this dos not work. PyNumber_Add in abstract.c checks
 * for tp_as_sequence before it checks for tp_as_number which means that
 * whenever we want to add two points skpoint_concat is called! Since
 * concat is only called from abstract.c we might get away with treating
 * `concat' as `add'. (This applies to Python 1.5.1)
 */

   
static PyObject *
skpoint_concat(PyObject *self, PyObject *other)
{
    if (SKPoint_Check(self) && SKPoint_Check(other))
	return skpoint_add((SKPointObject*)self, other);
    PyErr_SetString(PyExc_TypeError,
		    "concat/add requires two SKPoint objects");
    return NULL;
}

/* Repeat is needed for Python 2.1 and higher */
static PyObject *
skpoint_repeat(PyObject *self, int n)
{
    return SKPoint_FromXY(POINT(self)->x * n, POINT(self)->y * n);
}

static PyObject *
skpoint_item(SKPointObject *self, int i)
{
    double item;
    switch (i)
    {
    case 0:
	item = self->x;
	break;
    case 1:
	item = self->y;
	break;
    default:
	PyErr_SetString(PyExc_IndexError, "index must be 0 or 1");
	return NULL;
    }

    return PyFloat_FromDouble(item);
}

static PyObject *
skpoint_slice(PyObject *self, int ilow, int ihigh)
{
    PyErr_SetString(PyExc_RuntimeError,
		    "slicing not supported for SKPointObjects");
    return NULL;
}


/*
 *	Methods
 */

/*
 * point.normalized()
 *
 * Return a point with the same direction but length 1. 
 */
static PyObject *
skpoint_normalized(SKPointObject * self, PyObject * args)
{
    double len;

    if (!PyArg_ParseTuple(args, ""))
	return NULL;

    len = hypot(self->x, self->y);
    if (len == 0)
    {
	PyErr_SetString(PyExc_ZeroDivisionError, "Point().normalized");
	return NULL;
    }
    
    return SKPoint_FromXY(self->x / len, self->y / len);
}


/* in earlier python implementations it seemed impossible to allow
 * multiplication of numbers and point objects. Now it works, so this
 * method is obsolete:
 */
/*
 *	point.scaled(FACTOR)
 *
 * Return FACTOR * point	(scalar multiplication).
 *
 */
#if 0
static PyObject *
skpoint_scaled(SKPointObject * self, PyObject * args)
{
    double scalar;

    if (!PyArg_ParseTuple(args, "d", &scalar))
	return NULL;

    return SKPoint_FromXY(self->x * scalar, self->y * scalar);
}
#endif

/*
 *	point.polar()
 *
 *	Return a tuple (R, PHI), the polar coordinates describing the
 *	same point
 */
static PyObject *
skpoint_polar(SKPointObject * self, PyObject * args)
{
    double r = hypot(self->x, self->y);
    double phi = atan2(self->y, self->x);
    
    if (r == 0.0)
    	phi = 0.0;
	
    return Py_BuildValue("dd", r, phi);
}


static struct PyMethodDef skpoint_methods[] = {
    {"normalized",	(PyCFunction)skpoint_normalized,	1},
    {"polar",		(PyCFunction)skpoint_polar,		1},
    {NULL,	NULL}
};

static PyObject *
skpoint_getattr(PyObject * self, char * name)
{
    if (name[0] == 'x' && name[1] == '\0')
	return PyFloat_FromDouble(((SKPointObject*)self)->x);
    if (name[0] == 'y' && name[1] == '\0')
	return PyFloat_FromDouble(((SKPointObject*)self)->y);

    return Py_FindMethod(skpoint_methods, self, name);
}



static PyObject *
skpoint_not_implemented(void)
{
    PyErr_SetString(PyExc_TypeError, "operator not implemented for SKPoint");
    return NULL;
}

static PyNumberMethods skpoint_as_number = {
	(binaryfunc)skpoint_add,		/*nb_add*/
	(binaryfunc)skpoint_sub,		/*nb_subtract*/
	(binaryfunc)skpoint_multiply,		/*nb_multiply*/
	(binaryfunc)skpoint_divide,		/*nb_divide*/
	(binaryfunc)skpoint_not_implemented,	/*nb_remainder*/
	(binaryfunc)skpoint_not_implemented,	/*nb_divmod*/
	(ternaryfunc)skpoint_not_implemented,	/*nb_power*/
	(unaryfunc)skpoint_neg,			/*nb_negative*/
	(unaryfunc)skpoint_pos,			/*nb_positive*/
	(unaryfunc)skpoint_abs,			/*nb_absolute*/
	(inquiry)skpoint_nonzero,		/*nb_nonzero*/
	(unaryfunc)0,	/*nb_invert*/
	(binaryfunc)0,	/*nb_lshift*/
	(binaryfunc)0,	/*nb_rshift*/
	(binaryfunc)0,	/*nb_and*/
	(binaryfunc)0,	/*nb_xor*/
	(binaryfunc)0,	/*nb_or*/
	skpoint_coerce,	/*nb_coerce*/
	(unaryfunc)0,	/*nb_int*/
	(unaryfunc)0,	/*nb_long*/
	(unaryfunc)0,	/*nb_float*/
	(unaryfunc)0,	/*nb_oct*/
	(unaryfunc)0,	/*nb_hex*/
};

static PySequenceMethods skpoint_as_sequence = {
	skpoint_length,			/*sq_length*/
	skpoint_concat,			/*sq_concat*/
	skpoint_repeat,			/*sq_repeat*/
	(intargfunc)skpoint_item,	/*sq_item*/
	skpoint_slice,			/*sq_slice*/
	0,				/*sq_ass_item*/
	0,				/*sq_ass_slice*/
};



PyTypeObject SKPointType = {
	PyObject_HEAD_INIT(NULL)
	0,
	"skpoint",
	sizeof(SKPointObject),
	0,
	(destructor)skpoint_dealloc,	/*tp_dealloc*/
	(printfunc)NULL,		/*tp_print*/
	skpoint_getattr,		/*tp_getattr*/
	0,				/*tp_setattr*/
	(cmpfunc)skpoint_compare,	/*tp_compare*/
	(reprfunc)skpoint_repr,		/*tp_repr*/
	&skpoint_as_number,		/*tp_as_number*/
	&skpoint_as_sequence,		/*tp_as_sequence*/
	0,				/*tp_as_mapping*/
	0,				/*tp_hash*/
        0,				/*tp_call*/
        0,				/*tp_str*/
	0,				/*tp_getattro*/
	0,				/*tp_setattro*/
	0,				/*tp_as_buffer*/
#ifdef USE_NEWSTYLE_NUMBERS
	Py_TPFLAGS_CHECKTYPES		/*tp_flags*/
#endif
};


/*
 *		Module Functions
 */


/*
 *	skpoint.Point(X, Y)
 *
 * Return a new point object with coordinates X, Y.
 */
PyObject *
SKPoint_PyPoint(PyObject * self, PyObject * args)
{
    double x, y;
    PyObject * coords;

    if (PyTuple_Size(args) == 1)
    {
	coords = PyTuple_GET_ITEM(args, 0);
	if (SKPoint_Check(coords))
	{
	    Py_INCREF(coords);
	    return coords;
	}
    }
    else
	coords = args;

    if (!skpoint_extract_xy(coords, &x, &y))
    {
	PyErr_SetString(PyExc_TypeError,
			"expected two numbers or a sequence of two numbers");
	return NULL;
    }
    
    return SKPoint_FromXY(x, y);
}

/*
 *	skpoint.Polar(R, PHI)
 *	skpoint.Polar(PHI)
 *
 * Return a new point object given in polar coordinates R and PHI.
 */
PyObject *
SKPoint_PyPolar(PyObject * self, PyObject * args)
{
    double r = 1.0, phi;

    if (PyTuple_Size(args) == 2)
    {
	if (!PyArg_ParseTuple(args, "dd", &r, &phi))
	    return NULL;
    }
    else
    {
	if (!PyArg_ParseTuple(args, "d", &phi))
	    return NULL;
    }

    return SKPoint_FromXY(r * cos(phi), r * sin(phi));
}


/*
 *
 */

PyObject *
skpoint_allocated(PyObject * self, PyObject * args)
{
#if SKPOINT_COUNT_ALLOC
    return PyInt_FromLong(allocated);
#else
    return PyInt_FromLong(-1);
#endif
}


/*
 *	Convenience functions for other C modules
 */

/* Extract a coordinate pair from SEQUENCE and store it in *X, *Y.
 * SEQUENCE may be an SKPointObject or any sequence of two objects that
 * can be converted to a double. Return 1 on success, 0 otherwise.
 */
int
skpoint_extract_xy(PyObject * sequence, double * x, double * y)
{
    if (SKPoint_Check(sequence))
    {
	*x = ((SKPointObject*)sequence)->x;
	*y = ((SKPointObject*)sequence)->y;
	return 1;
    }
    
    if (PySequence_Check(sequence) && PySequence_Length(sequence) == 2)
    {
	PyObject * xo = PySequence_GetItem(sequence, 0);
	PyObject * yo = PySequence_GetItem(sequence, 1);
	if (xo && yo)
	{
	    *x = PyFloat_AsDouble(xo);
	    *y = PyFloat_AsDouble(yo);
	}
	Py_XDECREF(xo);
	Py_XDECREF(yo);
	
	if(PyErr_Occurred())
	    return 0;
	return 1;
    }
    return 0;
}
