/* Sketch - A Python-based interactive drawing program
 * Copyright (C) 1997 -- 2006 by Bernhard Herzog
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

/* a poly bezier object */

#include <math.h>
#include <string.h>
#include <locale.h>

#include <Python.h>
#include <structmember.h>

#include <assert.h>

#include "skpoint.h"
#include "skrect.h"
#include "sktrafo.h"
#include "curveobject.h"

#include "curvelow.h"
#include "curvemisc.h"


/*
 * gcc stuff
 */

#ifndef __GNUC__
#define FUNCTION_NAME ""
#else
#define FUNCTION_NAME __FUNCTION__
#endif


/*
 *	Methods for segments
 */

static void
init_segment(CurveSegment * segment, int type)
{
    segment->type = type;
    segment->cont = ContAngle;
    segment->selected = 0;
    segment->x1 = segment->y1 = segment->x2 = segment->y2 = 0.0;
    segment->x = segment->y = 0.0;
}


/* compute the new position of a control point, given the other one and
 * the continuity at the node
 */
static void
SKCurve_AdjustControlPoint(SKCoord * x, SKCoord * y,
			   double cur_x, double cur_y,
			   double node_x, double node_y,
			   int cont)
{
    switch (cont)
    {
    case ContSymmetrical:
	*x = 2 * node_x - cur_x;
	*y = 2 * node_y - cur_y;
	break;

    case ContSmooth:
    {
	double dx = cur_x - node_x;
	double dy = cur_y - node_y;
	double length = hypot(*x - node_x, *y - node_y);
	double cur_length = hypot(dx, dy);
	if (cur_length < 0.1)
	    cur_length = 0.1;

	*x = node_x - length * dx / cur_length;
	*y = node_y - length * dy / cur_length;
	break;
    }
    default:
	break;
    }
}


#define CURVE_BLOCK_LEN 9

#define ROUNDUP(n, block) ((n)>0 ? (((n)+(block)-1)/(block))*(block) : (block))

static int paths_allocated = 0;

PyObject *
SKCurve_New(int length)
{
    SKCurveObject * self;
    int i;

    self = PyObject_New(SKCurveObject, &SKCurveType);
    if (self == NULL)
	return NULL;

    length = ROUNDUP(length, CURVE_BLOCK_LEN);
    self->len = 0;
    self->closed = 0;
    self->segments = malloc(length * sizeof(CurveSegment));
    if (!self->segments)
    {
	PyObject_Del(self);
	return PyErr_NoMemory();
    }
    self->allocated = length;

    for (i = 0; i < self->allocated; i++)
    {
	init_segment(self->segments + i, CurveLine);
    }

    paths_allocated++;

    return (PyObject *)self;
}

/*
 *
 */

static int
check_index(SKCurveObject * self, int index, const char * funcname)
{
    if (index < 0)
	index = index + self->len;

    if (index < 0 || index >= self->len)
    {
	char message[1000];
	sprintf(message, "%s: index out of range", funcname);
	PyErr_SetString(PyExc_IndexError, message);
	return -1;
    }

    return index;
}



/*
 *	update internal data
 */


/* Check the state of self and make corrections if necessary. If WARN,
 * print some warning messages to stderr if corrections are made.
 *
 * In particular, do these things: XXX: update
 *
 */
static void
curve_check_state(SKCurveObject * self, int warn, const char * funcname)
{
}


/* Resize the bezier path SELF to have at least NEW_LEN allocated
 * segments.
 * 
 * Return true if successful, otherwise, return false and set an
 * exception.
 */
static int
curve_realloc(SKCurveObject * self, int new_len)
{
    new_len = ROUNDUP(new_len, CURVE_BLOCK_LEN);
    if (new_len != self->allocated)
    {
	CurveSegment * new_segments;
	new_segments = realloc(self->segments, new_len * sizeof(CurveSegment));
	if (!new_segments)
	{
	    PyErr_NoMemory();
	    return 0;
	}
	self->segments = new_segments;
	self->allocated = new_len;
    }

    return 1;
}

/* Make certain that there are at least GROW free nodes.
 *
 * Return true if successful, return false and set an exception
 * otherwise.
 */
static int
curve_grow(SKCurveObject * self, int grow)
{
    return curve_realloc(self, self->len + grow);
}


/*
 *	Some standard python methods
 */

static void
curve_dealloc(SKCurveObject * self)
{
    free(self->segments);
    PyObject_Del(self);
    paths_allocated--;
}

static int
curve_compare(SKCurveObject * v, SKCurveObject * w)
{
    /* there is no true way to order curves, so for now, compare the
     * pointers instead. We should compare all the segments...
     */
    if (v == w)
	return 0;

    return v < w ? -1 : +1;
}

static PyObject *
curve_repr(SKCurveObject * self)
{
    char buf[100];
    sprintf(buf, "<SKCurveObject at %ld with %d nodes>", (long)self,
	    self->len);
    return PyString_FromString(buf);
}



/*
 *	Bezier specific methods
 */

/*
 * curve.duplicate()
 *
 * Return a new SKCurveObject object that is a copy of self. This is
 * essentially the same as the GraphicsObject.Duplicate() method.
 */
static PyObject *
curve_duplicate(SKCurveObject * self, PyObject * args)
{
    SKCurveObject * copy;
    int i;

    copy = (SKCurveObject*)SKCurve_New(self->len);
    if (!copy)
	return NULL;

    copy->len = self->len;
    copy->closed = self->closed;

    for (i = 0; i < self->len; i++)
	copy->segments[i] = self->segments[i];
    
    return (PyObject*)copy;
}

/*
 * curve.node(IDX)
 *
 * Return the node at position IDX as an SKPoint object. A negative IDX
 * is interpreted like a negative list index in Python.
 */
static PyObject *
curve_node(SKCurveObject * self, PyObject *args)
{
    int idx;

    if (!PyArg_ParseTuple(args, "i", &idx))
	return NULL;

    if (idx < 0)
	idx = idx + self->len;

    if (idx < 0 || idx >= self->len)
    {
	PyErr_SetString(PyExc_IndexError,
			"curve_node: index out of range");
	return NULL;
    }

    return SKPoint_FromXY(self->segments[idx].x, self->segments[idx].y);
}

/*
 * curve.node_list()
 *
 * Return all nodes of path as a list of SKPoint objects. For a closed
 * curve, the last node is omitted, since it is identical to the first.
 */
static PyObject *
curve_node_list(SKCurveObject * self, PyObject *args)
{
    int i, length;
    CurveSegment * segment;
    PyObject * list, *point;

    if (!PyArg_ParseTuple(args, ""))
	return NULL;

    length = self->len;
    if (self->closed)
	length -= 1;
    
    list = PyList_New(length);
    if (!list)
	return NULL;

    segment = self->segments;
    for (i = 0; i < length; i++, segment++)
    {
	point = SKPoint_FromXY(segment->x, segment->y);
	if (!point)
	{
	    Py_DECREF(list);
	    return NULL;
	}
	PyList_SetItem(list, i, point);
    }

    return list;
}

/*
 * curve.continuity(IDX)
 *
 * Return the continuity of node IDX. The continuity is one of
 * ContAngle, ContSmooth or ContSymmetrical. A negative IDX is
 * interpreted like a negative list index in Python
 */
static PyObject *
curve_continuity(SKCurveObject * self, PyObject * args)
{
    int idx;

    if (!PyArg_ParseTuple(args, "i", &idx))
	return NULL;

    if (idx < 0)
	idx = idx + self->len;

    if (idx < 0 || idx >= self->len)
    {
	PyErr_SetString(PyExc_IndexError,
			"curve_continuity: index out of range");
	return NULL;
    }

    return PyInt_FromLong(self->segments[idx].cont);
}


/*
 * curve.segment_type(IDX)
 *
 * Return the type of segment IDX. The type is one of Bezier, Line or
 * Gap. A negative IDX is interpreted like a negative list index in
 * Python.
 */
static PyObject *
curve_segment_type(SKCurveObject * self, PyObject * args)
{
    int idx;

    if (!PyArg_ParseTuple(args, "i", &idx))
	return NULL;

    if (idx < 0)
	idx = idx + self->len;

    if (idx < 0 || idx >= self->len)
    {
	PyErr_SetString(PyExc_IndexError,
			"curve_segment_type: index out of range");
	return NULL;
    }

    return PyInt_FromLong(self->segments[idx].type);
}

/*
 * curve.segment(IDX)
 */

static PyObject *
curve_segment(SKCurveObject * self, PyObject * args)
{
    int idx;
    CurveSegment * segment;
    PyObject * result, *p1, *p2, *p;

    if (!PyArg_ParseTuple(args, "i", &idx))
	return NULL;

    idx = check_index(self, idx, "path.Segment");
    if (idx < 0)
	return NULL;

    segment = self->segments + idx;
    p = SKPoint_FromXY(segment->x, segment->y);
    if (segment->type == CurveBezier)
    {
	p1 = SKPoint_FromXY(segment->x1, segment->y1);
	p2 = SKPoint_FromXY(segment->x2, segment->y2);
	result = Py_BuildValue("i(OO)Oi", segment->type, p1, p2, p,
			       segment->cont);
	Py_XDECREF(p1);
	Py_XDECREF(p2);
    }
    else
    {
	result = Py_BuildValue("i()Oi", segment->type, p, segment->cont); 
    }
    Py_XDECREF(p);
    
    return result;
}


/*
 *
 */
static PyObject *
curve_set_continuity(SKCurveObject * self, PyObject * args)
{
    int idx, cont;

    if (!PyArg_ParseTuple(args, "ii", &idx, &cont))
	return NULL;

    if (idx < 0)
	idx = idx + self->len;

    if (idx < 0 || idx >= self->len)
    {
	PyErr_SetString(PyExc_IndexError,
			"curve_set_continuity: index out of range");
	return NULL;
    }

    if (!CHECK_CONT(cont))
    {
	PyErr_SetString(PyExc_ValueError, "curve_set_continuity: "
			"cont must be one of ContAngle, ContSmooth "
			"or ContSymmetrical");
	return NULL;
    }
    self->segments[idx].cont = cont;
    if (self->closed)
    {
	if (idx == 0)
	    self->segments[self->len - 1].cont = cont;
	else if (idx == self->len - 1)
	    self->segments[0].cont = cont;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


/* Append a new segment to the curve.
 *
 * This only works correctly when the path is not closed. If the path is
 * closed a new node should be inserted, not appended.
 *
 * Return true if successful, otherwise, return false and set an
 * exception.
 */

int
SKCurve_AppendSegment(SKCurveObject * self, CurveSegment * segment)
{
    if (self->len == 0 && segment->type == CurveBezier)
    {
	PyErr_SetString(PyExc_TypeError,
			"The first segment added to a curve must be a line");
	return 0;
    }
    
    if (!curve_grow(self, 1))
	return 0;

    self->segments[self->len] = *segment;
    self->len += 1;

    curve_check_state(self, 1, FUNCTION_NAME);

    return 1;
}

int
SKCurve_AppendLine(SKCurveObject * self, double x, double y, int continuity)
{
    CurveSegment segment;

    segment.type = CurveLine;
    segment.cont = continuity;
    segment.selected = 0;
    segment.x = x;
    segment.y = y;

    return SKCurve_AppendSegment(self, &segment);
}
    
int
SKCurve_AppendBezier(SKCurveObject * self, double x1, double y1,
		     double x2, double y2, double x, double y,
		     int continuity)
{
    CurveSegment segment;

    segment.type = CurveBezier;
    segment.cont = continuity;
    segment.selected = 0;
    segment.x1 = x1;	segment.y1 = y1;
    segment.x2 = x2;	segment.y2 = y2;
    segment.x = x;	segment.y = y;

    return SKCurve_AppendSegment(self, &segment);
}



/* create full undo, i.e. undo info for nodes AND segments */
static PyObject * set_nodes_and_segments_string = NULL; /* init on import*/
static PyObject *
curve_create_full_undo(SKCurveObject * self)
{
    PyObject * undo_segments;
    PyObject * result;
    CurveSegment * segments;

    segments = malloc(self->allocated * sizeof(CurveSegment));
    if (!segments)
	return PyErr_NoMemory();

    memcpy(segments, self->segments, self->allocated * sizeof(CurveSegment));

    undo_segments = PyCObject_FromVoidPtr(segments, free);
    if (!undo_segments)
    {
	free(segments);
	return NULL;
    }

    result = Py_BuildValue("OOiii", set_nodes_and_segments_string,
			   undo_segments, self->len, self->allocated,
			   self->closed);
    Py_DECREF(undo_segments);

    return result;
}

/* undo nodes and segments */
static PyObject *
curve__set_nodes_and_segments(SKCurveObject * self, PyObject * args)
{
    int allocated = -1, length = -1, closed = 0;
    PyObject * undo_segments = NULL;
    PyObject * result;
    
    if (!PyArg_ParseTuple(args, "O!iii",
			  &PyCObject_Type, &undo_segments,
			  &length, &allocated, &closed))
	return NULL;

    result = curve_create_full_undo(self);
    if (!result)
	return NULL;

    if (!curve_realloc(self, allocated))
    {
	Py_DECREF(result);
	return NULL;
    }

    memcpy(self->segments, PyCObject_AsVoidPtr(undo_segments),
	   allocated * sizeof(CurveSegment));
    self->allocated = allocated;
    self->len = length;
    self->closed = closed;

    curve_check_state(self, 1, FUNCTION_NAME);

    return result;
}

/*
 *	Hit tests
 */

static PyObject *
curve_hit_point(SKCurveObject * self, PyObject * args)
{
    SKRectObject * rect;
    int i, result = 0;
    CurveSegment * segment;

    if (!PyArg_ParseTuple(args, "O!", &SKRectType, &rect))
	return NULL;

    segment = self->segments;
    for (i = 0; i < self->len; i++, segment++)
    {
	if (SKRect_ContainsXY(rect, segment->x, segment->y))
	    result = 1;
    }
    
    return PyInt_FromLong(result);
}


/*
 *	Bounding boxes
 */

/* curve.coord_rect([TRAFO])
 *
 * Return the smallest aligned rectangle that contains all nodes and
 * control points. With optional argument TRAFO, compute the rectangle
 * as if the path were transformed by the transformation TRAFO.
 */
static PyObject *
curve_coord_rect(SKCurveObject * self, PyObject * args)
{
    SKRectObject * rect = NULL;
    CurveSegment * segment;
    PyObject * trafo = NULL;
    int i;

    if (!PyArg_ParseTuple(args, "|O!", &SKTrafoType, &trafo))
	return NULL;

    if (self->len == 0)
    {
	Py_INCREF(SKRect_EmptyRect);
	return (PyObject*)SKRect_EmptyRect;
    }

    segment = self->segments;
    if (!trafo)
    {
	rect = (SKRectObject*)SKRect_FromDouble(segment->x, segment->y,
						segment->x, segment->y);
	if (!rect)
	    return NULL;
	segment += 1;
	for (i = 1; i < self->len; i++, segment++)
	{
	    SKRect_AddXY(rect, segment->x, segment->y);
	    if (segment->type == CurveBezier)
	    {
		SKRect_AddXY(rect, segment->x1, segment->y1);
		SKRect_AddXY(rect, segment->x2, segment->y2);
	    }
	}
    }
    else
    {
	SKCoord x, y;

	SKTrafo_TransformXY(trafo, segment->x, segment->y, &x, &y);
	rect = (SKRectObject*)SKRect_FromDouble(x, y, x, y);
	if (!rect)
	    return NULL;
	
	segment += 1;
	for (i = 1; i < self->len; i++, segment++)
	{
	    SKTrafo_TransformXY(trafo, segment->x, segment->y, &x, &y);
	    SKRect_AddXY(rect, x, y);
	    if (segment->type == CurveBezier)
	    {
		SKTrafo_TransformXY(trafo, segment->x1, segment->y1, &x, &y);
		SKRect_AddXY(rect, x, y);
		SKTrafo_TransformXY(trafo, segment->x2, segment->y2, &x, &y);
		SKRect_AddXY(rect, x, y);
	    }
	}
    }
    return (PyObject*)rect;
}

/* Add the `real' bounding rectangle of the bezier segment given by the Ps to
 * RECT. `real' means that it is as tight as possible, not just the bounding
 * box of the Ps.
 *
 * Assumes that the end points are already accounted for
 */
#define DISCR(p1,p2,p3,p4) (p1*p4 - p1*p3 - p2*p3 - p2*p4 + p2*p2 + p3*p3)
#define DENOM(p1,p2,p3,p4) (p1 - 3 * p2 + 3 * p3 - p4)

static void
add_bezier_rect(SKRectObject * rect,
		double p1x, double p1y, double p2x, double p2y,
		double p3x, double p3y, double p4x, double p4y)
{
    double discr, denom, p;

    discr = DISCR(p1x, p2x, p3x, p4x);
    if (discr >= 0)
    {
	double p13 = 3 * p1x, p23 = 3 * p2x, p33 = 3 * p3x;
	double c1 = p23 - p1x - p33 + p4x;
	double c2 = p13 - 2 * p23 + p33;
	double c3 = p23 - p13;
	double t;

	denom = DENOM(p1x, p2x, p3x, p4x);
	if (denom)
	{
	    discr = sqrt(discr);
	    p = p1x - 2 * p2x + p3x;

	    t = (p + discr) / denom;
	    if (0 < t && t < 1)
		SKRect_AddX(rect, ((c1 * t + c2) * t  + c3) * t + p1x);
	    t = (p - discr) / denom;
	    if (0 < t && t < 1)
		SKRect_AddX(rect, ((c1 * t + c2) * t  + c3) * t + p1x);
	}
	else
	{
	    denom = p1x - 2 * p2x + p3x;
	    if (denom)
	    {
		t = 0.5 * (p1x - p2x) / denom;
		if (0 < t && t < 1)
		    SKRect_AddX(rect, ((c1 * t + c2) * t  + c3) * t + p1x);
	    }
	}
    }

    discr = DISCR(p1y, p2y, p3y, p4y);
    if (discr >= 0)
    {
	double p13 = 3 * p1y, p23 = 3 * p2y, p33 = 3 * p3y;
	double c1 = p23 - p1y - p33 + p4y;
	double c2 = p13 - 2 * p23 + p33;
	double c3 = p23 - p13;
	double t;

	denom = DENOM(p1y, p2y, p3y, p4y);
	if (denom)
	{
	    discr = sqrt(discr);
	    p = p1y - 2 * p2y + p3y;

	    t = (p + discr) / denom;
	    if (0 < t && t < 1)
		SKRect_AddY(rect, ((c1 * t + c2) * t  + c3) * t + p1y);
	    t = (p - discr) / denom;
	    if (0 < t && t < 1)
		SKRect_AddY(rect, ((c1 * t + c2) * t  + c3) * t + p1y);
	}
	else
	{
	    denom = p1y - 2 * p2y + p3y;
	    if (denom)
	    {
		t = 0.5 * (p1y - p2y) / denom;
		if (0 < t && t < 1)
		    SKRect_AddY(rect, ((c1 * t + c2) * t  + c3) * t + p1y);
	    }
	}
    }
}


static PyObject *
curve_accurate_rect(SKCurveObject * self, PyObject * args)
{
    SKRectObject * rect = NULL;
    CurveSegment * segment;
    PyObject * trafo = NULL;
    int i;

    if (!PyArg_ParseTuple(args, "|O!", &SKTrafoType, &trafo))
	return NULL;

    if (self->len == 0)
    {
	Py_INCREF(SKRect_EmptyRect);
	return (PyObject*)SKRect_EmptyRect;;
    }

    segment = self->segments;
    if (!trafo)
    {
	rect = (SKRectObject*)SKRect_FromDouble(segment->x, segment->y,
						segment->x, segment->y);
	if (!rect)
	    return NULL;
	
	segment += 1;
	for (i = 1; i < self->len; i++, segment++)
	{
	    SKRect_AddXY(rect, segment->x, segment->y);
	    if (segment->type == CurveBezier)
	    {
		add_bezier_rect(rect, segment[-1].x, segment[-1].y,
				segment->x1, segment->y1,
				segment->x2, segment->y2,
				segment->x, segment->y);
	    }
	}
    }
    else
    {
	SKCoord x, y;

	SKTrafo_TransformXY(trafo, segment->x, segment->y, &x, &y);
	rect = (SKRectObject*)SKRect_FromDouble(x, y, x, y);
	if (!rect)
	    return NULL;

	segment += 1;
	for (i = 1; i < self->len; i++, segment++)
	{
	    SKTrafo_TransformXY(trafo, segment->x, segment->y, &x, &y);
	    SKRect_AddXY(rect, x, y);
	    if (segment->type == CurveBezier)
	    {
		SKCoord p1x, p1y, p2x, p2y, p3x, p3y;
		SKTrafo_TransformXY(trafo, segment[-1].x, segment[-1].y,
				    &p1x, &p1y);
		SKTrafo_TransformXY(trafo, segment->x1, segment->y1,
				    &p2x, &p2y);
		SKTrafo_TransformXY(trafo, segment->x2, segment->y2,
				    &p3x, &p3y);
		add_bezier_rect(rect, p1x, p1y, p2x, p2y, p3x, p3y, x, y);
	    }
	}
    }
    return (PyObject*)rect;
}


/*
 *	Transformation
 */


int
SKCurve_Transform(SKCurveObject * self, PyObject * trafo)
{
    int i;
    CurveSegment * segment;

    segment = self->segments;
    for (i = 0; i < self->len; i++, segment++)
    {
	SKTrafo_TransformXY(trafo, segment->x, segment->y,
			    &segment->x, &segment->y);
	if (segment->type == CurveBezier)
	{
	    SKTrafo_TransformXY(trafo, segment->x1, segment->y1,
				&segment->x1, &segment->y1);
	    SKTrafo_TransformXY(trafo, segment->x2, segment->y2,
				&segment->x2, &segment->y2);
	}
    }
    return 0;
}    

static PyObject *
curve_apply_trafo(SKCurveObject * self, PyObject * args)
{
    PyObject * trafo;
    PyObject * undo;

    if (!PyArg_ParseTuple(args, "O!", &SKTrafoType, &trafo))
	return NULL;

    undo = curve_create_full_undo(self);
    if (!undo)
	return NULL;

    SKCurve_Transform(self, trafo);

    return undo;
}

static PyObject *
curve_apply_translation(SKCurveObject * self, PyObject * args)
{
    double x, y;
    int i;
    CurveSegment * segment;
    
    if (!PyArg_ParseTuple(args, "dd", &x, &y))
    {
	PyObject * sequence;
	PyErr_Clear();
	if (!PyArg_ParseTuple(args, "O", &sequence))
	    return NULL;
	if (!skpoint_extract_xy(sequence, &x, &y))
	{
	    PyErr_SetString(PyExc_TypeError,
		     "argument is neither number nor sequence of two numbers");
	    return NULL;
	}
    }


    segment = self->segments;
    for (i = 0; i < self->len; i++, segment++)
    {
	segment->x += x;
	segment->y += y;
	if (segment->type == CurveBezier)
	{
	    segment->x1 += x;
	    segment->y1 += y;
	    segment->x2 += x;
	    segment->y2 += y;
	}
    }

    Py_INCREF(Py_None);
    return Py_None;
}


/*
 *	close the contour
 */

#define SWAP(tmp,a,b) tmp = a; a = b; b = tmp
static PyObject * undo_close_string = NULL; /* initialized in initbezierobj()*/
static PyObject *
curve__undo_close(SKCurveObject * self, PyObject * args)
{
    int closed = 0, itemp;
    double last_x, last_y, dtemp;
    int first_cont, last_cont;
    int lastidx = self->len - 1;

    if (!PyArg_ParseTuple(args, "iiidd", &closed, &first_cont, &last_cont,
			  &last_x, &last_y))
	return NULL;

    SWAP(itemp, self->segments[0].cont, first_cont);
    SWAP(dtemp, self->segments[lastidx].x, last_x);
    SWAP(dtemp, self->segments[lastidx].y, last_y);
    SWAP(itemp, self->segments[lastidx].cont, last_cont);
    
    self->closed = closed;

    if (self->segments[lastidx].type == CurveBezier)
    {
	self->segments[lastidx].x2 += self->segments[lastidx].x - last_x;
	self->segments[lastidx].y2 += self->segments[lastidx].y - last_y;
    }

    curve_check_state(self, 1, FUNCTION_NAME);

    return Py_BuildValue("Oiiidd", undo_close_string, !self->closed,
			 first_cont, last_cont, last_x, last_y);
}
#undef SWAP


int
SKCurve_ClosePath(SKCurveObject * self)
{
    double last_x, last_y;
    int lastidx = self->len - 1;

    if (lastidx <= 0)
    {
	return 0;
    }

    last_x = self->segments[lastidx].x;
    last_y = self->segments[lastidx].y;
    self->segments[lastidx].x = self->segments[0].x;
    self->segments[lastidx].y = self->segments[0].y;
    self->segments[0].cont = self->segments[lastidx].cont = ContAngle;
    self->closed = 1;

    if (self->segments[lastidx].type == CurveBezier)
    {
	self->segments[lastidx].x2 += self->segments[lastidx].x - last_x;
	self->segments[lastidx].y2 += self->segments[lastidx].y - last_y;
    }
    
    curve_check_state(self, 1, FUNCTION_NAME);
    return 0;
}

static PyObject *
curve_close_contour(SKCurveObject * self, PyObject * args)
{
    double last_x, last_y;
    int first_cont, last_cont;
    int lastidx = self->len - 1;

    if (lastidx <= 0)
    {
	Py_INCREF(Py_None);
	return Py_None;
    }

    first_cont = self->segments[0].cont;
    last_x = self->segments[lastidx].x;
    last_y = self->segments[lastidx].y;
    last_cont = self->segments[lastidx].cont;

    SKCurve_ClosePath(self);

    return Py_BuildValue("Oiiidd", undo_close_string, 0, first_cont, last_cont,
			 last_x, last_y);
}


/*
 *	saving and loading
 */

static int
save_segment(PyObject * list, int i, CurveSegment * segment)
{
    PyObject * tuple;
    if (segment->type == CurveBezier)
    {
	tuple = Py_BuildValue("ddddddi",
			      segment->x1, segment->y1,
			      segment->x2, segment->y2,
			      segment->x, segment->y,
			      segment->cont);
    }
    else
    {
	tuple = Py_BuildValue("ddi", segment->x, segment->y, segment->cont);
    }
    if (!tuple)
    {
	Py_DECREF(list);
	return 0;
    }
    if (PyList_SetItem(list, i, tuple) == -1)
    {
	Py_DECREF(tuple);
	Py_DECREF(list);
	return 0;
    }
    return 1;
}

/* curve.get_save()
 *
 * Convert self to a list of tuples. Each tuple may have one of these
 * forms:
 *
 *	(X, Y, CONT)
 *
 *		A line segment ending at (X, Y) with the continuity CONT
 *		at the end point.
 *
 *	(X1, Y1, X2, Y2, X3, Y3, CONT)
 *
 *		A bezier segment with the control points (X1, Y1) and
 *		(X2, Y2) and the node (X3, Y3) with continuity CONT.
 *
 */

static PyObject *
curve_get_save(SKCurveObject * self, PyObject * args)
{
    CurveSegment * segment;
    PyObject * list;
    int i;

    list = PyList_New(self->len);
    if (!list)
	return NULL;

    segment = self->segments;

    for (i = 0; i < self->len; i++, segment++)
    {
	if (!save_segment(list, i, segment))
	    return NULL;
    }
    return list;
}


static int
write_segment(FILE * file, CurveSegment * segment)
{
    int result = 0;

    if (segment->type == CurveBezier)
    {
	result = fprintf(file, "bc(%g,%g,%g,%g,%g,%g,%d)\n",
			 segment->x1, segment->y1, segment->x2, segment->y2,
			 segment->x, segment->y, segment->cont);
    }
    else
    {
	result = fprintf(file, "bs(%g,%g,%d)\n",
			 segment->x, segment->y, segment->cont);
    }

    if (result < 0)
    {
	PyErr_SetFromErrno(PyExc_IOError);
	return 0;
    }
    return 1;
}

static PyObject *
curve_write_to_file(SKCurveObject * self, PyObject * args)
{
    PyObject * pyfile = NULL;
    FILE * file = NULL;
    CurveSegment * segment;
    int i;

    if (!PyArg_ParseTuple(args, "O!", &PyFile_Type, &pyfile))
	return NULL;

    file = PyFile_AsFile(pyfile);

    segment = self->segments;
    for (i = 0; i < self->len; i++, segment++)
    {
	if (!write_segment(file, segment))
	    return NULL;
    }
    Py_INCREF(Py_None);
    return Py_None;
}


/* append a straight line to self. */
static PyObject *
curve_append_straight(SKCurveObject * self, PyObject * args)
{
    double x, y;
    int cont = ContAngle;
    
    if (!PyArg_ParseTuple(args, "dd|i", &x, &y, &cont))
    {
	PyObject * sequence;
	PyErr_Clear();
	if (!PyArg_ParseTuple(args, "O|i", &sequence, &cont))
	    return NULL;
	if (!skpoint_extract_xy(sequence, &x, &y))
	{
	    PyErr_SetString(PyExc_TypeError,
   "first argument is neither number nor sequence of two numbers");
	    return NULL;
	}
    }

    if (!SKCurve_AppendLine(self, x, y, cont))
	return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

/* append a bezier segment to self. */
static PyObject *
curve_append_curve(SKCurveObject * self, PyObject * args)
{
    int cont = ContAngle;
    double x, y, x1, y1, x2, y2;
    
    if (PyTuple_Size(args) > 4)
    {
	if (!PyArg_ParseTuple(args, "dddddd|i", &x1, &y1, &x2, &y2, &x, &y,
			      &cont))
	    return NULL;
    }
    else
    {
	PyObject *p1, *p2, *p3;
	int result;

	if (!PyArg_ParseTuple(args, "OOO|i", &p1, &p2, &p3, &cont))
	    return NULL;

	result = skpoint_extract_xy(p1, &x1, &y1);
	result = result && skpoint_extract_xy(p2, &x2, &y2);
	result = result && skpoint_extract_xy(p3, &x, &y);
	if (!result)
	{
	    PyErr_SetString(PyExc_TypeError, "three points expected");
	    return NULL;
	}
    }
   
    if (!SKCurve_AppendBezier(self, x1, y1, x2, y2, x, y, cont))
	return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}


static PyObject *
curve_append_segment(SKCurveObject * self, PyObject * args)
{
    double x, y, x1, y1, x2, y2;
    int cont = ContAngle;
    int type;
    PyObject * p, *p1, *p2, *tuple;
    
    if (!PyArg_ParseTuple(args, "iOO|i", &type, &tuple, &p, &cont))
	return NULL;

    if (!skpoint_extract_xy(p, &x, &y))
    {
	PyErr_SetString(PyExc_TypeError,
			"third argument must be a point spec");
	return NULL;
    }

    if (type == CurveLine)
    {
	if (!SKCurve_AppendLine(self, x, y, cont))
	    return NULL;
    }
    else if (type == CurveBezier)
    {
	if (!PyArg_ParseTuple(tuple, "OO", &p1, &p2))
	    return NULL;
	if (!skpoint_extract_xy(p1, &x1, &y1)
	    || !skpoint_extract_xy(p2, &x2, &y2))
	{
	    PyErr_SetString(PyExc_TypeError,
			    "for bezier segments, second argument "
			    "must be a sequence of two point specs ");
	    return NULL;
	}

	if (!SKCurve_AppendBezier(self, x1, y1, x2, y2, x, y, cont))
	    return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
curve_set_straight(SKCurveObject * self, PyObject * args)
{
    double x, y;
    int idx, cont = ContAngle;
    
    if (!PyArg_ParseTuple(args, "idd|i", &idx, &x, &y, &cont))
    {
	PyObject * sequence;
	PyErr_Clear();
	if (!PyArg_ParseTuple(args, "iO|i", &idx, &sequence, &cont))
	    return NULL;
	if (!skpoint_extract_xy(sequence, &x, &y))
	{
	    PyErr_SetString(PyExc_TypeError,
   "first argument is neither number nor sequence of two numbers");
	    return NULL;
	}
    }

    idx = check_index(self, idx, "SetLine");
    if (idx < 0)
	return NULL;

    self->segments[idx].type = CurveLine;
    self->segments[idx].cont = cont;
    self->segments[idx].x = x;
    self->segments[idx].y = y;

    if (self->closed)
    {
	if (idx == 0)
	{
	    self->segments[self->len - 1].x = x;
	    self->segments[self->len - 1].y = y;
	    self->segments[self->len - 1].cont = cont;
	}
	else if (idx == self->len - 1)
	{
	    self->segments[0].x = x;
	    self->segments[0].y = y;
	    self->segments[0].cont = cont;
	}
    }

    Py_INCREF(Py_None);
    return Py_None;
}

/* append a bezier segment to self. */
static PyObject *
curve_set_curve(SKCurveObject * self, PyObject * args)
{
    int idx, cont = ContAngle;
    double x, y, x1, y1, x2, y2;
    
    if (PyTuple_Size(args) > 5)
    {
	if (!PyArg_ParseTuple(args, "idddddd|i", &idx,
			      &x1, &y1, &x2, &y2, &x, &y, &cont))
	    return NULL;
    }
    else
    {
	PyObject *p1, *p2, *p3;
	int result;

	if (!PyArg_ParseTuple(args, "iOOO|i", &idx, &p1, &p2, &p3,
			      &cont))
	    return NULL;

	result = skpoint_extract_xy(p1, &x1, &y1);
	result = result && skpoint_extract_xy(p2, &x2, &y2);
	result = result && skpoint_extract_xy(p3, &x, &y);
	if (!result)
	{
	    PyErr_SetString(PyExc_TypeError, "three points expected");
	    return NULL;
	}
    }

    idx = check_index(self, idx, "SetBezier");
    if (idx < 0)
	return NULL;


    self->segments[idx].type = CurveBezier;
    self->segments[idx].cont = cont;
    self->segments[idx].x = x;	 self->segments[idx].y = y;
    self->segments[idx].x1 = x1; self->segments[idx].y1 = y1;
    self->segments[idx].x2 = x2; self->segments[idx].y2 = y2;
    
    if (self->closed)
    {
	if (idx == 0)
	{
	    self->segments[self->len - 1].x = x;
	    self->segments[self->len - 1].y = y;
	    self->segments[self->len - 1].cont = cont;
	}
	else if (idx == self->len - 1)
	{
	    self->segments[0].x = x;
	    self->segments[0].y = y;
	    self->segments[0].cont = cont;
	}
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static PyObject *
curve_set_segment(SKCurveObject * self, PyObject * args)
{
    double x, y, x1, y1, x2, y2;
    int cont = ContAngle;
    int idx, type;
    PyObject * p, *p1, *p2, *tuple;
    
    if (!PyArg_ParseTuple(args, "iOO|i", &idx, &type, &tuple, &p, &cont))
	return NULL;

    if (!skpoint_extract_xy(p, &x, &y))
    {
	PyErr_SetString(PyExc_TypeError,
			"third argument must be a point spec");
	return NULL;
    }


    idx = check_index(self, idx, "SetSegment");
    if (idx < 0)
	return NULL;

    self->segments[idx].type = CurveLine;
    self->segments[idx].cont = cont;
    self->segments[idx].x = x;
    self->segments[idx].y = y;

    if (type == CurveBezier)
    {
	if (!PyArg_ParseTuple(tuple, "OO", &p1, &p2))
	    return NULL;
	if (!skpoint_extract_xy(p1, &x1, &y1)
	    || !skpoint_extract_xy(p2, &x2, &y2))
	{
	    PyErr_SetString(PyExc_TypeError,
			    "for bezier segments, second argument "
			    "must be a sequence of two point specs ");
	    return NULL;
	}

	self->segments[idx].x1 = x1;	self->segments[idx].y1 = y1;
	self->segments[idx].x2 = x2;	self->segments[idx].y2 = y2;
    }
    
    if (self->closed)
    {
	if (idx == 0)
	{
	    self->segments[self->len - 1].x = x;
	    self->segments[self->len - 1].y = y;
	    self->segments[self->len - 1].cont = cont;
	}
	else if (idx == self->len - 1)
	{
	    self->segments[0].x = x;
	    self->segments[0].y = y;
	    self->segments[0].cont = cont;
	}
    }

    Py_INCREF(Py_None);
    return Py_None;
}

static int
curve_parse_string_append(SKCurveObject * self, const char * string)
{
    CurveSegment segment;
    char * old_locale;

    old_locale = strdup(setlocale(LC_NUMERIC, NULL));
    setlocale(LC_NUMERIC, "C");
    
    if (string[1] == 'c')
    {
	double x, y, x1, y1, x2, y2;
	int cont;
	
	segment.type = CurveBezier;
	if (sscanf(string, "bc%*[ (]%lf,%lf,%lf,%lf,%lf,%lf,%d",
		   &x1, &y1, &x2, &y2, &x, &y, &cont) != 7)
	{
	    PyErr_SetString(PyExc_ValueError, "cannot parse string");
	    goto fail;
	}

	segment.cont = cont;
	segment.x = x;		segment.y = y;
	segment.x1 = x1;	segment.y1 = y1;
	segment.x2 = x2;	segment.y2 = y2;
	
	if (!SKCurve_AppendSegment(self, &segment))
	    goto fail;
    }
    else if (string[1] == 's')
    {
	double x, y;
	int cont;
	
	segment.type = CurveLine;
	if (sscanf(string, "bs%*[ (]%lf,%lf,%d", &x, &y, &cont) != 3)
	{
	    PyErr_SetString(PyExc_ValueError, "cannot parse string");
	    goto fail;
	}

	segment.cont = cont;
	segment.x = x;		segment.y = y;

	if (!SKCurve_AppendSegment(self, &segment))
	    goto fail;
    }
    else
    {
	PyErr_SetString(PyExc_ValueError,
			"string must begin with 'bc' or 'bs'");
	goto fail;
    }

    return 1;

fail:
    setlocale(LC_NUMERIC, old_locale);
    free(old_locale);
    return 0;
}

static PyObject *
curve_append_from_string(SKCurveObject * self, PyObject * args)
{
    char * string = NULL;
    int len;

    if (!PyArg_ParseTuple(args, "s#", &string, &len))
	return NULL;

    if (len < 4)
    {
	PyErr_SetString(PyExc_ValueError, "string too short");
	return NULL;
    }

    if (!curve_parse_string_append(self, string))
	return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
curve_append_from_file(SKCurveObject * self, PyObject * args)
{
    PyObject * pyfile = NULL;
    PyObject * line = NULL;
    const char *buf;

    if (!PyArg_ParseTuple(args, "O", &pyfile))
	return NULL;

    while ((line = PyFile_GetLine(pyfile, 0)) && (PyString_Size(line) != 0))
    {
	buf = PyString_AsString(line);
	if (buf[0] != 'b' || (buf[1] != 'c' && buf[1] != 's'))
	    break;
	if (!curve_parse_string_append(self, buf))
	{
	    Py_DECREF(line);
	    return NULL;
	}
	Py_DECREF(line);
    }

    return line;
}


/* close self.
 *
 * When importing from a ai-file, the last node is often given twice, by
 * a lineto or curveto and by closepath. In that case, the last node is
 * silently removed.
 *
 * Also (optionally) guess the continuity of the nodes. This is useful
 * when importing from eps files. Adobe Illustrator files already
 * contain some of this information
 */

#define GUESS_EPSILON 0.1
static PyObject *
curve_guess_continuity(SKCurveObject * self, PyObject * args)
{
    int i;
    CurveSegment * segment, *pred;

    segment = self->segments;
    for (i = 0; i < self->len; i++, segment++)
    {
	if (i > 0)
	    pred = segment - 1;
	else if (self->closed)
	    pred = self->segments + self->len - 1;
	else pred = NULL;

	if (pred && pred->type == CurveBezier && segment->type == CurveBezier)
	{
	    if (fabs(pred->x2 + segment->x1 - 2 * segment->x) < GUESS_EPSILON
		&& fabs(pred->y2 + segment->y1 - 2*segment->y) < GUESS_EPSILON)
	    {
		segment->cont = ContSymmetrical;
	    }
	    else
	    {
		SKCoord x, y;
		x = pred->x2; y = pred->y2;
		SKCurve_AdjustControlPoint(&x, &y, segment->x1, segment->y1,
					   segment->x, segment->y, ContSmooth);
		if (fabs(x - pred->x2) < GUESS_EPSILON
		    && fabs(y - pred->y2) < GUESS_EPSILON)
		{
		    segment->cont = ContSmooth;
		}
		else
		{
		    x = segment->x1; y = segment->y1;
		    SKCurve_AdjustControlPoint(&x, &y, pred->x2, pred->y2,
					       segment->x, segment->y,
					       ContSmooth);
		    if (fabs(x - segment->x1) < GUESS_EPSILON
			&& fabs(y - segment->y1) < GUESS_EPSILON)
		    {
			segment->cont = ContSmooth;
		    }
		}

	    }
	    if (i == 0 && self->closed)
		self->segments[self->len - 1].cont = segment->cont;
	}
    }

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
curve_load_close(SKCurveObject * self, PyObject * args)
{
    int copy_cont_from_last = 0;

    if (!PyArg_ParseTuple(args, "|i", &copy_cont_from_last))
	return NULL;

    self->closed = 1;

    if (copy_cont_from_last)
    {
	self->segments[0].cont = self->segments[self->len - 1].cont;
    }

    if (self->len > 2 && self->segments[self->len - 1].type == CurveLine)
    {
	if (self->segments[self->len - 1].x == self->segments[self->len - 2].x
	    && self->segments[self->len-1].y == self->segments[self->len-2].y)
	{
	    self->len -= 1;
	}
    }
    curve_check_state(self, 0, FUNCTION_NAME);

    Py_INCREF(Py_None);
    return Py_None;
}

#define DUMP_TEST 0

int
SKCurve_TestTransformed(SKCurveObject * self, PyObject * trafo,
			int test_x, int test_y, int closed)
{
    CurveSegment * segment;
    SKCoord nx, ny, x1, y1, x2, y2, lastx, lasty, i;
    int x[4], y[4];
    int result;
    int cross_count;

#if DUMP_TEST
    fprintf(stderr, "Testing path %ld at %d, %d\n", (long)self,
	    test_x, test_y);
#endif
    segment = self->segments;
    SKTrafo_TransformXY(trafo, segment->x, segment->y, &lastx, &lasty);

    segment += 1;
    cross_count = 0;
    for (i = 1; i < self->len; i++, segment++)
    {
	if (segment->type == CurveBezier)
	{
	    SKTrafo_TransformXY(trafo, segment->x1, segment->y1, &x1, &y1);
	    SKTrafo_TransformXY(trafo, segment->x2, segment->y2, &x2, &y2);
	    SKTrafo_TransformXY(trafo, segment->x, segment->y, &nx, &ny);
	    x[0] = lastx + 0.5;	y[0] = lasty + 0.5;
	    x[1] = x1 + 0.5;	y[1] = y1 + 0.5;
	    x[2] = x2 + 0.5;	y[2] = y2 + 0.5;
	    x[3] = nx + 0.5;	y[3] = ny + 0.5;
	    result = bezier_hit_segment(x, y, test_x, test_y);
	}
	else
	{
	    /* a line segment */
	    SKTrafo_TransformXY(trafo, segment->x, segment->y, &nx, &ny);
	    result = bezier_hit_line(lastx + 0.5, lasty + 0.5,
				     nx + 0.5, ny + 0.5, test_x, test_y);
	}
	lastx = nx;
	lasty = ny;
	if (result < 0)
	{
	    cross_count = -1;
	    break;
	}
	if (result > 0)
	    cross_count += result;
    }
    if (!self->closed && closed && self->len >= 2 && cross_count >= 0)
    {
	/* an open subpath in a closed multi path berzier object */
	SKTrafo_TransformXY(trafo, self->segments[0].x, self->segments[0].y,
			    &nx, &ny);
	result =  bezier_hit_line(lastx + 0.5, lasty + 0.5,
				  nx + 0.5, ny + 0.5, test_x, test_y);
	if (result > 0)
	    cross_count += result;
    }
#if DUMP_TEST
    fprintf(stderr, "result: cross_count = %d\n", cross_count);
#endif

    return cross_count;
}

/*
 *	Methods for interactive creation
 */

#define DRAW_BEZIER(x1,y1,x2,y2,x3,y3,x4,y4)\
result = PyObject_CallFunction(draw_bezier, "(dd)(dd)(dd)(dd)",\
			       x1,y1,x2,y2,x3,y3,x4,y4);\
if (!result)\
    return 0; \
Py_DECREF(result)

#define DRAW_LINE(x1,y1,x2,y2)\
result = PyObject_CallFunction(draw_line, "(dd)(dd)",x1,y1,x2,y2);\
    if (!result)\
	return 0;\
    Py_DECREF(result)


static PyObject *
creator_draw_not_last(SKCurveObject * curve, PyObject * args)
{
    PyObject * result;
    CurveSegment * segments = curve->segments;
    int i;
    PyObject * draw_bezier;
    PyObject * draw_line;

    if (!PyArg_ParseTuple(args, "OO", &draw_bezier, &draw_line))
	return NULL;

    for (i = 1; i < SKCurve_LENGTH(curve) - 1; i++)
    {
	if (segments[i].type == CurveBezier)
	{
	    DRAW_BEZIER(segments[i - 1].x, segments[i - 1].y,
			segments[i].x1, segments[i].y1,
			segments[i].x2, segments[i].y2,
			segments[i].x, segments[i].y);
	}
	else if (segments[i].type == CurveLine)
	{
	    DRAW_LINE(segments[i - 1].x, segments[i - 1].y,
		      segments[i].x, segments[i].y);
	}
    }

    Py_INCREF(Py_None);
    return Py_None;
}
    
/*
 *	Methods for interactive editing
 */

/* the same as in const.py: */
#define SelectSet	0
#define SelectAdd	1
#define SelectSubtract	2
#define SelectSubobjects 3	/* unused here */
#define SelectDrag	4

/*
 * Return the number of selected nodes as a Python int.
 */

static PyObject *
curve_selection_count(SKCurveObject * self)
{
    int count = 0;
    int i;

    for (i = 0; i < self->len; i++)
    {
	if (self->segments[i].selected && (!self->closed || i < self->len - 1))
	    ++count;
    }
    return PyInt_FromLong(count);
}

/*
 * curve.node_selected(IDX)
 *
 * Return true (1) if the node IDX is marked as selected, false (0)
 * otherwise. A negative IDX is interpreted like a negative list index
 * in Python.
 */
static PyObject *
curve_node_selected(SKCurveObject * self, PyObject * args)
{
    int idx;

    if (!PyArg_ParseTuple(args, "i", &idx))
	return NULL;

    idx = check_index(self, idx, "NodeSelected");
    if (idx < 0)
	return NULL;

    return PyInt_FromLong(self->segments[idx].selected);
}


static PyObject *
curve_select_rect(SKCurveObject * self, PyObject * args)
{
    SKRectObject * rect;
    CurveSegment * segment;
    int i, mode = SelectSet;
    int selected = 0;

    if (!PyArg_ParseTuple(args, "O!|i", &SKRectType, &rect, &mode))
	return NULL;

    segment = self->segments;
    for (i = 0; i < self->len; i++, segment++)
    {
	if (SKRect_ContainsXY(rect, segment->x, segment->y))
	{
	    if (mode == SelectSubtract)
		segment->selected = 0;
	    else
		segment->selected = 1;
	}
	else
	{
	    if (mode == SelectSet)
		segment->selected = 0;
	}
	selected = selected || segment->selected;
    }
    
    curve_check_state(self, 1, FUNCTION_NAME);

    return PyInt_FromLong(selected);
}


static PyObject *
curve_select_segment(SKCurveObject * self, PyObject * args)
{
    int idx, value = 1;

    if (!PyArg_ParseTuple(args, "i|i", &idx, &value))
	return NULL;
    
    if (idx < 0)
	idx = idx + self->len;

    if (idx < 0 || idx >= self->len)
    {
	PyErr_SetString(PyExc_IndexError,
			"curve_continuity: index out of range");
	return NULL;
    }

    self->segments[idx].selected = value;

    if (self->closed)
    {
	if (idx == self->len - 1)
	    self->segments[0].selected = value;
	else if (idx == 0)
	    self->segments[self->len - 1].selected = value;
    }

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
curve_deselect(SKCurveObject * self, PyObject * args)
{
    int i;

    for (i = 0; i < self->len; i++)
    {
	self->segments[i].selected = 0;
    }

    Py_INCREF(Py_None);
    return Py_None;
}



/*
 */

static PyObject *
curve_draw_dragged_nodes(SKCurveObject * self, PyObject * args)
{
    PyObject * draw_bezier;
    PyObject * draw_line;
    PyObject * result;
    SKPointObject * offset;
    CurveSegment * segment = self->segments + 1;
    int partially;
    int i;

    if (!PyArg_ParseTuple(args, "O!iOO", &SKPointType, &offset, &partially,
			  &draw_bezier, &draw_line))
	return NULL;
    
    for (i = 1; i < self->len; i++, segment++)
    {
	if (segment[-1].selected || segment->selected || !partially)
	{
	    double nx = segment[-1].x;
	    double ny = segment[-1].y;
	    CurveSegment seg = *segment;

	    if (segment[-1].selected)
	    {
		nx += offset->x;
		ny += offset->y;
		seg.x1 += offset->x;
		seg.y1 += offset->y;
	    }
	    if (segment->selected)
	    {
		seg.x += offset->x;
		seg.y += offset->y;
		seg.x2 += offset->x;
		seg.y2 += offset->y;
	    }

	    if (segment->type == CurveBezier)
	    {
		DRAW_BEZIER(nx, ny, seg.x1, seg.y1, seg.x2, seg.y2,
			    seg.x, seg.y);
	    }
	    else
	    {
		DRAW_LINE(nx, ny, seg.x, seg.y);
	    }
	}
    }
    
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
curve_move_selected_nodes(SKCurveObject * self, PyObject * args)
{
    SKPointObject * offset;
    int i;
    CurveSegment * segment;
    PyObject * undo_object = NULL;

    if (!PyArg_ParseTuple(args, "O!", &SKPointType, &offset))
	return NULL;

    undo_object = curve_create_full_undo(self);
    if (!undo_object)
	return NULL;

    segment = self->segments;
    for (i = 0; i < self->len; i++, segment++)
    {
	if (segment->selected)
	{
	    segment->x += offset->x;
	    segment->y += offset->y;
	    if (segment->type == CurveBezier)
	    {
		segment->x2 += offset->x;
		segment->y2 += offset->y;
	    }
	    if (i < self->len - 1 && segment[1].type == CurveBezier)
	    {
		segment[1].x1 += offset->x;
		segment[1].y1 += offset->y;
	    }
	}
    }

    return undo_object;
}

static PyObject *
curve_draw_unselected(SKCurveObject * self, PyObject * args)
{
    PyObject * draw_bezier;
    PyObject * draw_line;
    PyObject * result;
    CurveSegment * segment = self->segments + 1;
    int i;

    if (!PyArg_ParseTuple(args, "OO", &draw_bezier, &draw_line))
	return NULL;
    
    for (i = 1; i < self->len; i++, segment++)
    {
	if (segment->type == CurveLine)
	{
	    DRAW_LINE(segment[-1].x, segment[-1].y, segment->x, segment->y);
	}
	else if (!segment[-1].selected && !segment->selected)
	{
	    DRAW_BEZIER(segment[-1].x, segment[-1].y, segment->x1, segment->y1,
			segment->x2, segment->y2, segment->x, segment->y);
	}
    }
    
    Py_INCREF(Py_None);
    return Py_None;
}



/*
 *	tables for python, to access various attributes
 */


#define OFF(x) offsetof(SKCurveObject, x)
static struct memberlist curve_memberlist[] = {
    {"len",		T_INT,	OFF(len),		RO},
    {"closed",		T_BYTE,	OFF(closed),		RO},
    {NULL} 
};


/* for maximum performance, this list should contain the methods called
   most frequently at the beginning */
static struct PyMethodDef curve_methods[] = {
//     {"draw_transformed",(PyCFunction)SKCurve_PyDrawTransformed,	1},
    {"hit_point",	(PyCFunction)curve_hit_point,		1},
    
    {"accurate_rect",	(PyCFunction)curve_accurate_rect,	1},
    {"coord_rect",	(PyCFunction)curve_coord_rect,		1},

    /* new method names */
    {"Translate",	(PyCFunction)curve_apply_translation,	1},
    {"Transform",	(PyCFunction)curve_apply_trafo,		1},
    {"Duplicate",	(PyCFunction)curve_duplicate,		1},
    {"AppendLine",	(PyCFunction)curve_append_straight,	1},
    {"AppendBezier",	(PyCFunction)curve_append_curve,	1},
    {"AppendSegment",	(PyCFunction)curve_append_segment,	1},
    {"NodeList",	(PyCFunction)curve_node_list,		1},
    {"Node",		(PyCFunction)curve_node,		1},
    {"Segment",		(PyCFunction)curve_segment,		1},
    {"SetContinuity",	(PyCFunction)curve_set_continuity,	1},
    {"SetLine",		(PyCFunction)curve_set_straight,	1},
    {"SetBezier",	(PyCFunction)curve_set_curve,		1},
    {"SetSegment",	(PyCFunction)curve_set_segment,		1},
    {"Continuity",	(PyCFunction)curve_continuity,		1},
    {"SegmentType",	(PyCFunction)curve_segment_type,	1},
    {"ClosePath",	(PyCFunction)curve_close_contour,	1},

    /**/
    {"arc_lengths",	(PyCFunction)curve_arc_lengths,		1},
    {"_set_nodes_and_segments",(PyCFunction)curve__set_nodes_and_segments,1},
    {"_undo_close",	(PyCFunction)curve__undo_close,		1},
    {"append_from_file",(PyCFunction)curve_append_from_file,	1},
    {"get_save",	(PyCFunction)curve_get_save,		1},
    {"write_to_file",	(PyCFunction)curve_write_to_file,	1},
    {"guess_continuity",(PyCFunction)curve_guess_continuity,	1},
    {"load_close",	(PyCFunction)curve_load_close,		1},
    {"append_from_string",(PyCFunction)curve_append_from_string,1},

    /* editor methods */
    {"SegmentSelected",	(PyCFunction)curve_node_selected,	1},
    {"SelectSegment",	(PyCFunction)curve_select_segment,	1},
    {"draw_dragged_nodes",(PyCFunction)curve_draw_dragged_nodes,1},
    {"draw_unselected",	(PyCFunction)curve_draw_unselected,	1},
    {"selection_count",	(PyCFunction)curve_selection_count,	1},
    {"node_selected",	(PyCFunction)curve_node_selected,	1},
    {"select_rect",	(PyCFunction)curve_select_rect,		1},
    {"select_segment",	(PyCFunction)curve_select_segment,	1},
    {"deselect",	(PyCFunction)curve_deselect,		1},
    {"move_selected_nodes",(PyCFunction)curve_move_selected_nodes,1},
    {"nearest_point",	(PyCFunction)SKCurve_NearestPointPy,	1},
    {"point_at",	(PyCFunction)SKCurve_PointAtPy,		1},
    
    /* creator methods */
    {"draw_not_last",	(PyCFunction)creator_draw_not_last,	1},

    {NULL,	NULL}
};


static PyObject *
curve_getattr(PyObject * self, char * name)
{
    PyObject * result;

    result = Py_FindMethod(curve_methods, self, name);
    if (result != NULL)
	return result;
    PyErr_Clear();

    return PyMember_Get((char *)self, curve_memberlist, name);
}


PyTypeObject SKCurveType = {
    PyObject_HEAD_INIT(NULL)
    0,
    "SKCurveObject",
    sizeof(SKCurveObject),
    0,
    (destructor)curve_dealloc,	/*tp_dealloc*/
    (printfunc)NULL,		/*tp_print*/
    curve_getattr,		/*tp_getattr*/
    0,				/*tp_setattr*/
    (cmpfunc)curve_compare,	/*tp_compare*/
    (reprfunc)curve_repr,	/*tp_repr*/
    0,				/*tp_as_number*/
    0,				/*tp_as_sequence*/
    0,				/*tp_as_mapping*/
    0,				/*tp_hash*/
    (ternaryfunc)0,		/*tp_call*/
};



PyObject *
_SKCurve_NumAllocated(PyObject * self, PyObject * args)
{
    return PyInt_FromLong(paths_allocated);
}


int
_SKCurve_InitCurveObject(void)
{
    set_nodes_and_segments_string =
	PyString_InternFromString("_set_nodes_and_segments");
    undo_close_string = PyString_InternFromString("_undo_close");
    return 1;
}
