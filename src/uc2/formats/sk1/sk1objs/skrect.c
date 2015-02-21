/* Sketch - A Python-based interactive drawing program
 * Copyright (C) 1997, 1998, 1999, 2001, 2002, 2006 by Bernhard Herzog
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

/*
 * A Simple Rectangle object: SKRect
 *
 * A rectangle is given by the coordinates of its edges, which are
 * assumed to be parallel to the axes of the coordinate system.
 *
 * The coordinates are: left, bottom, right, top.
 *
 * The origin is assumed to be in the lower left corner and the
 * rectangle keeps its coordinates in a normalized form with
 * left < right and bottom < top.
 *
 * Rectangles are immutable.
 * 
 * In Sketch these rectangles are used to represent bounding rects and
 * similar things.
 */
 
#include <math.h>
#include <Python.h>
#include <structmember.h>

#include "skpoint.h"
#include "skrect.h"

static void skrect_normalize(SKRectObject * self);

SKRectObject * SKRect_InfinityRect = NULL;
SKRectObject * SKRect_EmptyRect = NULL;

#define  SKRECT_COUNT_ALLOC 1
#define  SKRECT_SUBALLOCATE 1

#if SKRECT_COUNT_ALLOC
static int allocated = 0;
#endif

#if SKRECT_SUBALLOCATE
#define BLOCK_SIZE	1000	/* 1K less typical malloc overhead */
#define N_RECTOBJECTS	(BLOCK_SIZE / sizeof(SKRectObject))

static SKRectObject *
fill_free_list(void)
{
    SKRectObject *p, *q;
    p = PyMem_Malloc(sizeof(SKRectObject) * N_RECTOBJECTS);
    if (p == NULL)
	return (SKRectObject *)PyErr_NoMemory();
    q = p + N_RECTOBJECTS;
    while (--q > p)
	q->ob_type = (PyTypeObject*)(q-1);
    q->ob_type = NULL;
    return p + N_RECTOBJECTS - 1;
}

static SKRectObject *free_list = NULL;
#endif

PyObject *
SKRect_FromDouble(double left, double bottom, double right, double top)
{
    SKRectObject * self;

#if SKRECT_SUBALLOCATE
    if (free_list == NULL) {
	if ((free_list = fill_free_list()) == NULL)
	    return NULL;
    }
    self = free_list;
    free_list = (SKRectObject *)(free_list->ob_type);
    self->ob_type = &SKRectType;
    _Py_NewReference(self);
#else
    self = PyObject_New(SKRectObject, &SKRectType);
    if (self == NULL)
	return NULL;
#endif

    self->left = left;
    self->bottom = bottom;
    self->right = right;
    self->top = top;
    skrect_normalize(self);

#if SKRECT_COUNT_ALLOC
    allocated++;
#endif

    return (PyObject*)self;
}

static void
skrect_dealloc(SKRectObject * self)
{
#if SKRECT_SUBALLOCATE
    self->ob_type = (PyTypeObject*)free_list;
    free_list = self;
#else
    PyObject_Del(self);
#endif
#if SKRECT_COUNT_ALLOC
    allocated--;
#endif
}

#define COMPARE(c1,c2) ((c1) < (c2) ? -1 : ((c1) > (c2) ? +1 : 0 ))
static int
skrect_compare(SKRectObject * v, SKRectObject * w)
{
    int result;

    /* In Python 2.1 (and probably later), the interpreter doesn't take
     * a shortcut anymore when comparing and object to itself (in
     * earlier versions an object was always equal to itself. Now we
     * have to take care of that special case here too. */
    if (v == w) return 0;

    /* The EmptyRect is smaller than any other rect. */
    if (v == SKRect_EmptyRect)	return -1;
    if (w == SKRect_EmptyRect)	return +1;

    /* The InfinityRect is larger than any other rect */
    if (v == SKRect_InfinityRect)	return +1;
    if (w == SKRect_InfinityRect)	return -1;

    if ((result = COMPARE(v->left, w->left)) != 0)
	return result;
    if ((result = COMPARE(v->bottom, w->bottom)) != 0)
	return result;
    if ((result = COMPARE(v->right, w->right)) != 0)
	return result;
    return COMPARE(v->top, w->top);
}
#undef COMPARE

static PyObject *
skrect_repr(SKRectObject * self)
{
    if (self == SKRect_EmptyRect)
	return PyString_FromString("EmptyRect");
    else if (self == SKRect_InfinityRect)
	return PyString_FromString("InfinityRect");
    else
    {	
	char buf[1000];
	sprintf(buf, "Rect(%.10g, %.10g, %.10g, %.10g)",
		self->left, self->bottom, self->right, self->top);
	return PyString_FromString(buf);
    }
}

static int
skrect_length(PyObject *self)
{
    return 4;
}

static PyObject *
skrect_concat(PyObject *self, PyObject *bb)
{
    PyErr_SetString(PyExc_RuntimeError,
		    "concat not supported for SKRectObjects");
    return NULL;
}

static PyObject *
skrect_repeat(PyObject *self, int n)
{
    PyErr_SetString(PyExc_RuntimeError,
		    "repeat not supported for SKRectObjects");
    return NULL;
}

static PyObject *
skrect_item(SKRectObject *self, int i)
{
    double item;
    switch (i)
    {
    case 0:
	item = self->left;
	break;
    case 1:
	item = self->bottom;
	break;
    case 2:
	item = self->right;
	break;
    case 3:
	item = self->top;
	break;
    default:
	PyErr_SetString(PyExc_IndexError, "index must be 0, 1, 2 or 3");
	return NULL;
    }

    return PyFloat_FromDouble(item);
}

static PyObject *
skrect_slice(PyObject *self, int ilow, int ihigh)
{
    PyErr_SetString(PyExc_RuntimeError,
		    "slicing not supported for SKRectObjects");
    return NULL;
}

static PySequenceMethods skrect_as_sequence = {
	skrect_length,			/*sq_length*/
	skrect_concat,			/*sq_concat*/
	skrect_repeat,			/*sq_repeat*/
	(intargfunc)skrect_item,	/*sq_item*/
	skrect_slice,			/*sq_slice*/
	0,				/*sq_ass_item*/
	0,				/*sq_ass_slice*/
};


/* normalize the rectangle: make sure that left is smaller than right
 * and bottom is smaller than top.
 */
static void
skrect_normalize(SKRectObject * self)
{
    SKCoord temp;

    if (self->left > self->right)
    {
	temp = self->left;
	self->left = self->right;
	self->right = temp;
    }

    if (self->top < self->bottom)
    {
	temp = self->top;
	self->top = self->bottom;
	self->bottom = temp;
    }
}
/*
 *	Python methods
 */

/*
 *	rect.grown(AMOUNT)
 *
 * Return a new rectangle that is bigger by AMOUNT in each direction.
 */
static PyObject *
skrect_grown(SKRectObject * self, PyObject * args)
{
    double amount;

    if (!PyArg_ParseTuple(args, "d", &amount))
	return NULL;

    if (self != SKRect_InfinityRect && self != SKRect_EmptyRect)
	return SKRect_FromDouble(self->left - amount, self->bottom - amount,
				 self->right + amount, self->top + amount);
    else
    {
	/* XXX: is this appropriate for SKRect_EmptyRect? */
	Py_INCREF(self);
	return (PyObject*)self;
    }
}

/*
 *	rect.translated(P)
 *
 * Return RECT translated by P
 */
static PyObject *
skrect_translated(SKRectObject * self, PyObject * args)
{
    PyObject * arg;
    double x, y;

    if (self == SKRect_EmptyRect || self == SKRect_InfinityRect)
    {
	Py_INCREF(self);
	return (PyObject*)self;
    }
    
    if (PyTuple_Size(args) == 2)
	arg = args;
    else if (!PyArg_ParseTuple(args, "O", &arg))
	return NULL;

    if (skpoint_extract_xy(arg, &x, &y))
    {
	return SKRect_FromDouble(self->left + x,  self->bottom + y,
				 self->right + x, self->top + y);
    }
    
    PyErr_SetString(PyExc_TypeError, "arguments must be either two numbers "
		    "or one seqeuence of two numbers");
    return NULL;
}


/*
 *	rect.contains_point(P)
 *
 * Return true if P lies in rect, false otherwise.
 */
static PyObject *
skrect_contains_point(SKRectObject * self, PyObject * args)
{
    PyObject * arg;
    double x, y;

    if (PyTuple_Size(args) == 2)
	arg = args;
    else if (!PyArg_ParseTuple(args, "O", &arg))
	return NULL;

    if (skpoint_extract_xy(arg, &x, &y))
    {
	return PyInt_FromLong(SKRect_ContainsXY(self, x, y));
    }
    
    PyErr_SetString(PyExc_TypeError, "arguments must be either two numbers "
		    "or one seqeuence of two numbers");
    return NULL;
}

/*
 *	rect.contains_rect(RECT)
 *
 * Return true if RECT lies completely inside of rect, false otherwise.
 */
static PyObject *
skrect_contains_rect(SKRectObject * self, PyObject * args)
{
    SKRectObject * r;

    if (!PyArg_ParseTuple(args, "O!", &SKRectType, &r))
	return NULL;

    /* special cases: I = InfinityRect, E = EmptyRect, r = other rect
     *
     *			      self
     *			I	E	r
     *		  +-------------------------
     *		I |	1	0	0
     *	other	E |	1	1	1
     *		r |	1	0	?
     */ 
    if (self == SKRect_InfinityRect || r == SKRect_EmptyRect)
	return PyInt_FromLong(1);
    
    if (self == SKRect_EmptyRect || r == SKRect_InfinityRect)
	return PyInt_FromLong(0);
    
    return PyInt_FromLong(   r->left >= self->left && r->right <= self->right
			  && r->top <= self->top && r->bottom >= self->bottom);
}

/*
 *	rect.overlaps(RECT)
 *
 * Return true if rect contains all or part of RECT, i.e. if they
 * overlap, otherwise, return false.
 */
static PyObject *
skrect_overlaps(SKRectObject * self, PyObject * args)
{
    SKRectObject * r;

    if (!PyArg_ParseTuple(args, "O!", &SKRectType, &r))
	return NULL;

    if (self == SKRect_InfinityRect || self == SKRect_EmptyRect
	|| r == SKRect_InfinityRect || r == SKRect_EmptyRect)
	return PyInt_FromLong(1);
    
    return PyInt_FromLong(   r->left <= self->right && r->right >= self->left
			  && r->top >= self->bottom && r->bottom <= self->top);
}


/*
 *	rect.center()
 *
 * Return the center of rect as a SKPoint.
 */
static PyObject *
skrect_center(SKRectObject * self, PyObject * args)
{
    SKCoord cx, cy;

    if (self != SKRect_InfinityRect && self != SKRect_EmptyRect)
    {
	cx = (self->left + self->right) / 2;
	cy = (self->top + self->bottom) / 2;
    }
    else
    {
	/* the center is really undefined in this case... */
	cx = cy = 0.0;
    }

    return SKPoint_FromXY(cx, cy);
}





#define OFF(x) offsetof(SKRectObject, x)
static struct memberlist skrect_memberlist[] = {
    {"left",		T_SKCOORD,	OFF(left),	RO},
    {"bottom",		T_SKCOORD,	OFF(bottom),	RO},
    {"right",		T_SKCOORD,	OFF(right),	RO},
    {"top",		T_SKCOORD,	OFF(top),	RO},
    {NULL} 
};


static struct PyMethodDef skrect_methods[] = {
    {"contains_point",	(PyCFunction)skrect_contains_point,	METH_VARARGS},
    {"contains_rect",	(PyCFunction)skrect_contains_rect,	METH_VARARGS},
    {"overlaps",	(PyCFunction)skrect_overlaps,		METH_VARARGS},
    {"grown",		(PyCFunction)skrect_grown,		METH_VARARGS},
    {"center",		(PyCFunction)skrect_center,		METH_VARARGS},
    {"translated",	(PyCFunction)skrect_translated,		METH_VARARGS},
    {NULL,	NULL}
};


static PyObject *
skrect_getattr(PyObject * self, char * name)
{
    PyObject * result;

    result = Py_FindMethod(skrect_methods, self, name);
    if (result != NULL)
	return result;
    PyErr_Clear();

    return PyMember_Get((char *)self, skrect_memberlist, name);
}


PyTypeObject SKRectType = {
	PyObject_HEAD_INIT(NULL)
	0,
	"skrect",
	sizeof(SKRectObject),
	0,
	(destructor)skrect_dealloc,	/*tp_dealloc*/
	(printfunc)NULL,		/*tp_print*/
	skrect_getattr,			/*tp_getattr*/
	0,				/*tp_setattr*/
	(cmpfunc)skrect_compare,	/*tp_compare*/
	(reprfunc)skrect_repr,		/*tp_repr*/
	0,				/*tp_as_number*/
	&skrect_as_sequence,		/*tp_as_sequence*/
	0,				/*tp_as_mapping*/
	0,				/*tp_hash*/
	(ternaryfunc)0,			/*tp_call */
};


/*
 *		Module Functions
 */

/*
 *	skrect.Rect(LEFT, BOTTOM, RIGHT, TOP)
 *	skrect.Rect(LLCORNER, URCORNER)
 *
 * Return a new Rect object with the coordinates LEFT, BOTTOM, RIGHT and
 * TOP or the opposite corners LLCORNER and URCORNER given as SKPoints.
 * The rectangle is automaticall normalized, so you can swap LEFT/RIGHT
 * or TOP/BOTTOM or choose any opposite corners.
 */
PyObject *
skrect_skrect(PyObject * self, PyObject * args)
{
    double left, top, right, bottom;

    if (PyTuple_Size(args) == 2)
    {
	/* two opposite corners */
	SKPointObject * p1, *p2;
	if (!PyArg_ParseTuple(args, "O!O!", &SKPointType, &p1,
			      &SKPointType, &p2))
	    return NULL;
	return SKRect_FromDouble(p1->x, p1->y, p2->x, p2->y);
    }

    /* four numbers */
    if (!PyArg_ParseTuple(args, "dddd", &left, &bottom, &right, &top))
	return NULL;

    return SKRect_FromDouble(left, bottom, right, top);
}

/*
 *	skrect.UnionRects(RECT1, RECT2)
 *
 * Return the smallest rectangle that contains RECT1 and RECT2.
 */

PyObject *
skrect_unionrects(PyObject * self, PyObject * args)
{
    SKRectObject * r1, * r2;

    if (!PyArg_ParseTuple(args, "O!O!", &SKRectType, &r1, &SKRectType, &r2))
	return NULL;

    if (r1 == SKRect_EmptyRect)
    {
	Py_INCREF(r2);
	return (PyObject*)r2;
    }
    if (r2 == SKRect_EmptyRect)
    {
	Py_INCREF(r1);
	return (PyObject*)r1;
    }
    if (r1 == SKRect_InfinityRect || r2 == SKRect_InfinityRect)
    {
	Py_INCREF(SKRect_InfinityRect);
	return (PyObject*)SKRect_InfinityRect;
    }
    return SKRect_FromDouble((r1->left	< r2->left)  ? r1->left  : r2->left,
			     (r1->bottom<r2->bottom) ? r1->bottom: r2->bottom,
			     (r1->right > r2->right) ? r1->right : r2->right,
			     (r1->top	> r2->top)   ? r1->top   : r2->top);
}



/*
 *	skrect.IntersectRects(RECT1, RECT2)
 *
 * Return the largest rectangle contained in  RECT1 and RECT2.
 */
PyObject *
skrect_intersect(PyObject * self, PyObject * args)
{
    SKRectObject * r1, * r2;
    double left, bottom, right, top;

    if (!PyArg_ParseTuple(args, "O!O!", &SKRectType, &r1, &SKRectType, &r2))
	return NULL;

    /* special cases: I = InfinityRect, E = EmptyRect, r = other rect
     *
     *			      r1
     *			I	E	r
     *		  +-------------------------
     *		I |	I	E	r2
     *	r2	E |	E	E	E
     *		r |	r1	E	?
     */ 
    if (r1 == SKRect_InfinityRect)
    {
	Py_INCREF(r2);
	return (PyObject*)r2;
    }
    if (r2 == SKRect_InfinityRect)
    {
	Py_INCREF(r1);
	return (PyObject*)r1;
    }
    if (r1 == SKRect_EmptyRect || r2 == SKRect_EmptyRect)
    {
	Py_INCREF(SKRect_EmptyRect);
	return (PyObject*)SKRect_EmptyRect;
    }

    left   = (r1->left	 > r2->left)   ? r1->left   : r2->left;
    bottom = (r1->bottom > r2->bottom) ? r1->bottom : r2->bottom;
    right  = (r1->right  < r2->right)  ? r1->right  : r2->right;
    top    = (r1->top	 < r2->top)    ? r1->top    : r2->top;
    if (left > right || bottom > top)
    {
	Py_INCREF(SKRect_EmptyRect);
	return (PyObject*)SKRect_EmptyRect;
    }	    
    
    return SKRect_FromDouble(left, bottom, right, top);
}

/*
 *	skrect.PointsToRect(SEQUENCE)
 *
 * Return the smallest rectangle that contains all the points in
 * SEQUENCE. SEQUENCE is a sequence (any sequence type) of SKPoint
 * objects.
 */
PyObject *
skrect_PointsToRect(PyObject * self, PyObject * args)
{
    PyObject * points;
    int length, idx;
    SKRectObject * rect = NULL;

    if (!PyArg_ParseTuple(args, "O", &points))
	return NULL;

    length = PySequence_Length(points);
    if (length <= 0)
    {
	Py_INCREF(SKRect_EmptyRect);
	return (PyObject*)SKRect_EmptyRect;
    }

    for (idx = 0; idx < length; idx++)
    {
	double x, y;
	PyObject * p;
	int is_point = 0;

	p = PySequence_GetItem(points, idx);
	is_point = skpoint_extract_xy(p, &x, &y);
	Py_DECREF(p);
	
	if (!is_point)
	{
	    PyErr_SetString(PyExc_TypeError,
			    "nonempty sequence of points expected");
	    return NULL;
	}

	if (!rect)
	{
	    rect = (SKRectObject*)SKRect_FromDouble(x, y, x, y);
	    if (!rect)
		return NULL;
	}

	SKRect_AddXY(rect, x, y);
    }

    return (PyObject*)rect;
}

/*
 *
 */

PyObject *
skrect_allocated(PyObject * self, PyObject * args)
{
#if SKRECT_COUNT_ALLOC
    return PyInt_FromLong(allocated);
#else
    return PyInt_FromLong(-1);
#endif
}





/*
 *	some functions that can be called from other modules
 */

/*
 * Return true if the point (X, Y) lies in rect, false otherwise.
 */

int
SKRect_ContainsXY(SKRectObject * self, double x, double y)
{
    if (self != SKRect_EmptyRect
	&& (self == SKRect_InfinityRect
	    || (self->left <= x && self->right >= x
		&& self->top  >= y && self->bottom <= y)))
	return 1;
    return 0;
}

/* If (x, y) lies outside of self, make self larger to include (x,y).
 * Assume self is normalized.
 *
 * While SKRects are considered immutable, this function actually
 * changes self. It is only meant to be called for `new' rectangles that
 * are created by a C-function. Once the rect has been passed to the
 * python interpreter or is known by some other parts of the code, the
 * rect should not be changed anymore.
 */

int
SKRect_AddXY(SKRectObject * self, double x, double y)
{
    skrect_normalize(self);
    
    if (x < self->left)
	self->left = x;
    else if (x > self->right)
	self->right = x;

    if (y > self->top)
	self->top = y;
    else if (y < self->bottom)
	self->bottom = y;

    return 1;
}

/*
 * If X lies outside of self, make self larger to include X.
 * See SKRect_AddXY for comments on immutablility.
 */
int
SKRect_AddX(SKRectObject * self, double x)
{
    skrect_normalize(self);
    
    if (x < self->left)
	self->left = x;
    else if (x > self->right)
	self->right = x;
    return 1;
}


/*
 * If Y lies outside of self, make self larger to include Y.
 * See SKRect_AddXY for comments on immutablility.
 */
int
SKRect_AddY(SKRectObject * self, double y)
{
    skrect_normalize(self);
    
    if (y > self->top)
	self->top = y;
    else if (y < self->bottom)
	self->bottom = y;

    return 1;
}
    
