/* Sketch - A Python-based interactive drawing program
 * Copyright (C) 1997, 1998, 2000, 2002, 2006 by Bernhard Herzog
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Library General Public
 * License as published by the Free Software Foundation; either
 * version 2 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	 See the GNU
 * Library General Public License for more details.
 *
 * You should have received a copy of the GNU Library General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307	 USA
 */


#include <math.h>
#include <Python.h>
#include <structmember.h>

#include "skpoint.h"
#include "skrect.h"
#include "sktrafo.h"

/* Trafo implements a 2D affine transformation T:
 *
 *	    / x \   / m11 m12 \ / x \	/ v1 \
 *	T * |	| = |	      | |   | + |    |
 *	    \ y /   \ m21 m22 / \ y /	\ v2 /
 *
 *
 * or, in homogeneous coordinates:
 *
 *		     / m11 m12 v1 \ / x \
 *		     |		  | |	|
 *		  ^= | m21 m22 v2 | | y |
 *		     |		  | |	|
 *		     \ 0   0   1  / \ 1 /
 *
 *
 * SKTrafo objects are immutable.
 */

/* exception raised when a singular matrix is inverted */
PyObject *
SKTrafo_ExcSingular = NULL;


#define SKTRAFO_COUNT_ALLOC 1

#if SKTRAFO_COUNT_ALLOC
static int allocated = 0;
#endif

PyObject *
SKTrafo_FromDouble(double m11, double m21, double m12, double m22,
		   double v1, double v2)
{
    SKTrafoObject * self;

    self = PyObject_New(SKTrafoObject, &SKTrafoType);
    if (self == NULL)
	return NULL;

    self->m11 = m11;
    self->m12 = m12;
    self->m21 = m21;
    self->m22 = m22;
    self->v1 = v1;
    self->v2 = v2;

#if SKTRAFO_COUNT_ALLOC
    allocated++;
#endif

    return (PyObject*)self;
}

static void
sktrafo_dealloc(SKTrafoObject * self)
{
    PyObject_Del(self);
#if SKTRAFO_COUNT_ALLOC
    allocated--;
#endif
}

/* there is no true way to order transforms, so simply test for equality */
static int
sktrafo_compare(SKTrafoObject * v, SKTrafoObject * w)
{
    if (v == w
	|| (v->m11 == w->m11 && v->m12 == w->m12
	    && v->m21 == w->m21 && v->m22 == w->m22
	    && v->v1 == w->v1 && v->v2 == w->v2))
	return 0;

    return v < w ? -1 : +1;
}

static PyObject *
sktrafo_repr(SKTrafoObject * self)
{
    char buf[1000];
    sprintf(buf, "Trafo(%.10g, %.10g, %.10g, %.10g, %.10g, %.10g)",
	    self->m11, self->m21, self->m12, self->m22, self->v1, self->v2);
    return PyString_FromString(buf);
}

/*
 *	trafo(OBJ)
 *
 * If OBJ is a SKPoint return the transformed point.
 *
 * If OBJ is a tuple of two floats treat it as a point. Return a
 * SKPoint. (Should a tuple be returned?)
 *
 * If OBJ is a SKTrafo return the concatenation of trafo and OBJ (such
 * that trafo(OBJ)(x) == trafo(OBJ(x))
 *
 * If OBJ is a SKRect return the the bounding rect of the transformed
 * corners of OBJ as a SKRect. (an alternative would be to return the
 * transformed rect as a list of points)
 *
 */

static PyObject *
sktrafo_call(SKTrafoObject * self, PyObject * args, PyObject * kw)
{
    PyObject * arg;
    double x, y;

    if (PyTuple_Size(args) == 2)
	arg = args;
    else if (!PyArg_ParseTuple(args, "O", &arg))
	return NULL;

    if (skpoint_extract_xy(arg, &x, &y))
    {
	return SKPoint_FromXY(self->m11 * x + self->m12 * y + self->v1,
			      self->m21 * x + self->m22 * y + self->v2);
    }
    else if (SKTrafo_Check(arg))
    {
	register SKTrafoObject * t = (SKTrafoObject *) arg;
	return SKTrafo_FromDouble(self->m11 * t->m11 + self->m12 * t->m21,
				  self->m21 * t->m11 + self->m22 * t->m21,
				  self->m11 * t->m12 + self->m12 * t->m22,
				  self->m21 * t->m12 + self->m22 * t->m22,
				  self->m11*t->v1 + self->m12*t->v2 + self->v1,
				  self->m21*t->v1 + self->m22*t->v2 +self->v2);
    }
    else if (SKRect_Check(arg))
    {
	SKRectObject * result;
	register SKRectObject * r = (SKRectObject*)arg;

	if (r == SKRect_InfinityRect || r == SKRect_EmptyRect)
	{
	    Py_INCREF(r);
	    return (PyObject*)r;
	}
	result = (SKRectObject*) \
	    SKRect_FromDouble(self->m11 * r->left + self->m12 * r->top,
			      self->m21 * r->left + self->m22 * r->top,
			      self->m11 * r->right + self->m12 * r->bottom,
			      self->m21 * r->right + self->m22 * r->bottom);
	if (result)
	{
	    SKRect_AddXY(result, self->m11 * r->right + self->m12 * r->top,
				 self->m21 * r->right + self->m22 * r->top);
	    SKRect_AddXY(result, self->m11 * r->left + self->m12 * r->bottom,
				 self->m21 * r->left + self->m22 * r->bottom);
	    result->left += self->v1;
	    result->right += self->v1;
	    result->top += self->v2;
	    result->bottom += self->v2;
	}
	return (PyObject*) result;
    }

    PyErr_SetString(PyExc_TypeError, "SKTrafo must be applied to SKPoints, "
		    "SKRects or SKTrafos");
    return NULL;
}



#define OFF(x) offsetof(SKTrafoObject, x)
static struct memberlist sktrafo_memberlist[] = {
    {"m11",		T_DOUBLE,	OFF(m11),	RO},
    {"m12",		T_DOUBLE,	OFF(m12),	RO},
    {"m21",		T_DOUBLE,	OFF(m21),	RO},
    {"m22",		T_DOUBLE,	OFF(m22),	RO},
    {"v1",		T_DOUBLE,	OFF(v1),	RO},
    {"v2",		T_DOUBLE,	OFF(v2),	RO},
    {NULL}	/* Sentinel */
};

/* methods */


/*	trafo.DocToWin(POINT)
 * or:	trafo.DocToWin(X, Y)
 *
 * Return the point POINT or (X, Y) in window coordinates as a tuple of ints.
 * POINT may be an SKPointObject or any sequence of two numbers.
 */
PyObject *
sktrafo_DocToWin(SKTrafoObject * self, PyObject * args)
{
    PyObject * arg;
    double docx, docy;
    int x, y;

    if (PyTuple_Size(args) == 2)
	arg = args;
    else if (!PyArg_ParseTuple(args, "O", &arg))
	return NULL;

    if (skpoint_extract_xy(arg, &docx, &docy))
    {
	x = ceil(self->m11 * docx + self->m12 * docy + self->v1);
	y = ceil(self->m21 * docx + self->m22 * docy + self->v2);
	return Py_BuildValue("ii", x, y);
    }

    PyErr_SetString(PyExc_TypeError,
		    "arguments must be either be two numbers, "
		    "a point or a sequence of two numbers");
    return NULL;
}


/* trafo.DTransform(POINT)
 *
 * Transform POINT as a vector. This means that the translation is not
 * applied. (In homogeneous coordinates: if POINT is SKPoint(x, y), treat it as
 * (x, y, 0) and not (x, y, 1))
 */
static PyObject *
sktrafo_dtransform(SKTrafoObject * self, PyObject * args)
{
    PyObject * arg;
    double x, y;

    if (PyTuple_Size(args) == 2)
	arg = args;
    else if (!PyArg_ParseTuple(args, "O", &arg))
	return NULL;

    if (skpoint_extract_xy(arg, &x, &y))
    {
	return SKPoint_FromXY(self->m11 * x + self->m12 * y,
			      self->m21 * x + self->m22 * y);
    }

    PyErr_SetString(PyExc_TypeError,
		    "arguments must be either be two numbers, "
		    "a point or a sequence of two numbers");
    return NULL;
}

/*
 *	trafo.inverse()
 *
 * Return the inverse of trafo. If the matrix is singular, raise a
 * SingularMatrix exception.
 */
static PyObject *
sktrafo_inverse(SKTrafoObject * self, PyObject * args)
{
    double det = self->m11 * self->m22 - self->m12 * self->m21;
    double m11, m12, m21, m22;

    if (det == 0.0)
    {
	PyErr_SetString(SKTrafo_ExcSingular, "inverting singular matrix");
	return NULL;
    }

    m11 = self->m22 / det;
    m12 = -self->m12 / det;
    m21 = -self->m21 / det;
    m22 = self->m11 / det;

    return SKTrafo_FromDouble(m11, m21, m12, m22,
			      -m11 * self->v1 - m12 * self->v2,
			      -m21 * self->v1 - m22 * self->v2);
}

/*
 *
 */

static PyObject *
sktrafo_offset(SKTrafoObject * self, PyObject * args)
{
    return SKPoint_FromXY(self->v1, self->v2);
}

static PyObject *
sktrafo_matrix(SKTrafoObject * self, PyObject * args)
{
    return Py_BuildValue("dddd", self->m11, self->m21, self->m12, self->m22);
}

/* trafo.coeff()
 *
 * Return the coefficients of trafo as a 6-tuple in the order used in
 * PostScript: (m11, m21, m12, m22, v1, v2)
 */
static PyObject *
sktrafo_coeff(SKTrafoObject * self, PyObject * args)
{
    return Py_BuildValue("dddddd", self->m11, self->m21, self->m12, self->m22,
			 self->v1, self->v2);
}

/*
 *
 */
static struct PyMethodDef sktrafo_methods[] = {
    {"DocToWin",	(PyCFunction)sktrafo_DocToWin,		1},
    {"DTransform",	(PyCFunction)sktrafo_dtransform,	1},
    {"inverse",		(PyCFunction)sktrafo_inverse,		1},
    {"offset",		(PyCFunction)sktrafo_offset,		1},
    {"matrix",		(PyCFunction)sktrafo_matrix,		1},
    {"coeff",		(PyCFunction)sktrafo_coeff,		1},
    {NULL,	NULL}
};


static PyObject *
sktrafo_getattr(PyObject * self, char * name)
{
    PyObject * result;


    result = Py_FindMethod(sktrafo_methods, self, name);
    if (result != NULL)
	return result;
    PyErr_Clear();

    return PyMember_Get((char *)self, sktrafo_memberlist, name);
}


PyTypeObject SKTrafoType = {
	PyObject_HEAD_INIT(NULL)
	0,
	"sktrafo",
	sizeof(SKTrafoObject),
	0,
	(destructor)sktrafo_dealloc,	/*tp_dealloc*/
	(printfunc)NULL,		/*tp_print*/
	sktrafo_getattr,		/*tp_getattr*/
	0,				/*tp_setattr*/
	(cmpfunc)sktrafo_compare,	/*tp_compare*/
	(reprfunc)sktrafo_repr,		/*tp_repr*/
	0,				/*tp_as_number*/
	0,				/*tp_as_sequence*/
	0,				/*tp_as_mapping*/
	0,				/*tp_hash*/
	(ternaryfunc)sktrafo_call,	/* tp_call */
};


/*
 *	Module Functions
 */

PyObject *
sktrafo_allocated(PyObject * self, PyObject * args)
{
#if SKTRAFO_COUNT_ALLOC
    return PyInt_FromLong(allocated);
#else
    return PyInt_FromLong(-1);
#endif
}

/*
 *	sktrafo.Trafo([m11, m21, m12, m22, v1, v2])
 *
 * Return the transformation given by the m_i_j and the v_i (see above).
 * All arguments are optional. They default to the values of an identity
 * transformation. Note: the order of the parameters is the same as for
 * a transformation matrix in PostScript.
 */


PyObject *
sktrafo_sktrafo(PyObject * self, PyObject * args)
{
    /* default trafo is identity */
    double m11 = 1.0, m12 = 0.0, m21 = 0.0, m22 = 1.0;
    double v1 = 0.0, v2 = 0.0;

    if (!PyArg_ParseTuple(args, "|dddddd", &m11, &m21, &m12, &m22, &v1, &v2))
	return NULL;

    return SKTrafo_FromDouble(m11, m21, m12, m22, v1, v2);
}

/*
 *	Some standard transformations
 */

/* Scale: XXX allow specification of a centerpoint. */
PyObject *
sktrafo_scale(PyObject * self, PyObject * args)
{
    double factorx, factory;

    if (PyTuple_Size(args) == 1)
    {
	if (!PyArg_ParseTuple(args, "d", &factorx))
	    return NULL;
	factory = factorx;
    }
    else
    {
	if (!PyArg_ParseTuple(args, "dd", &factorx, &factory))
	    return NULL;
    }

    return SKTrafo_FromDouble(factorx, 0.0, 0.0, factory, 0.0, 0.0);
}

PyObject *
sktrafo_translation(PyObject * self, PyObject * args)
{
    double offx, offy;

    if (PyTuple_Size(args) == 1)
    {
	PyObject * point;
	if (!PyArg_ParseTuple(args, "O", &point))
	    return NULL;
	if (!skpoint_extract_xy(point, &offx, &offy))
	{
	    PyErr_SetString(PyExc_ValueError, "Offset must be a point object "
			    "or a tuple of floats");
	    return NULL;
	}
    }
    else if (!PyArg_ParseTuple(args, "dd", &offx, &offy))
	return NULL;

    return SKTrafo_FromDouble(1.0, 0.0, 0.0, 1.0, offx, offy);
}

PyObject *
sktrafo_rotation(PyObject * self, PyObject * args)
{
    double angle, cx = 0.0, cy = 0.0;
    double s, c, offx, offy;
    if (PyTuple_Size(args) == 2)
    {
	PyObject * point;
	if (!PyArg_ParseTuple(args, "dO", &angle, &point))
	    return NULL;
	if (!skpoint_extract_xy(point, &cx, &cy))
	{
	    PyErr_SetString(PyExc_ValueError, "Center must be a point object "
			    "or a tuple of floats");
	    return NULL;
	}
    }
    else if (!PyArg_ParseTuple(args, "d|dd", &angle, &cx, &cy))
	return NULL;

    s = sin(angle);
    c = cos(angle);
    /* compute offset.
     * The rotation around center is
     * T(p) = center + M * (p - center)
     * => offset = center - M * center
     */
    offx = cx - c * cx + s * cy;
    offy = cy - s * cx - c * cy;

    return SKTrafo_FromDouble(c, s, -s, c, offx, offy);
}


/*
 *	C Functions for other modules
 */


/*
 * Apply SELF to the point (x, y) and store the result in *OUT_X, *OUT_Y.
 */
#define SELF ((SKTrafoObject*)self)
void
SKTrafo_TransformXY(PyObject * self, double x, double y,
		    SKCoord * out_x, SKCoord * out_y)
{
    if (SKTrafo_Check(self))
    {
	*out_x = SELF->m11 * x + SELF->m12 * y + SELF->v1;
	*out_y = SELF->m21 * x + SELF->m22 * y + SELF->v2;
    }
}

/*
 * Apply SELF to the vector (x, y) and store the result in *OUT_X, *OUT_Y.
 * (see the comments for sktrafo_dtransform() above.
 */
void
SKTrafo_DTransformXY(PyObject * self, double x, double y,
		     SKCoord * out_x, SKCoord * out_y)
{
    if (SKTrafo_Check(self))
    {
	*out_x = SELF->m11 * x + SELF->m12 * y;
	*out_y = SELF->m21 * x + SELF->m22 * y;
    }
}

#undef SELF
