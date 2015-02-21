/* Sketch - A Python-based interactive drawing program
 * Copyright (C) 1997, 1998, 1999 by Bernhard Herzog
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

#include "sktrafo.h"
#include "curveobject.h"

#include "curvefunc.h"
#include "curvelow.h"

/*
 *  Module Functions
 */


PyObject *
SKCurve_PyCreatePath(PyObject * self, PyObject * args)
{
    int length = 2;

    if (!PyArg_ParseTuple(args, "|i", &length))
	return NULL;

    return SKCurve_New(length);
}


/*
 * SKCurve_TestTransformed(PATHS, TRAFO, X, Y, FILLED)
 *
 * Test whether a multipath object is hit by a mouse click at (X, Y).
 *
 * PATHS	tuple of bezier objects
 * TRAFO	SKTrafo mapping doccoords to window coords
 * X, Y		Window coords of mouse click
 * FILLED	Whether object is filled or not
 *
 * Return:
 *
 *  0	Object was not hit
 * -1	Object was hit on the border
 * +1	Object was hit in the interior (even odd rule). Only if FILLED
 *	is true
 */
PyObject *
SKCurve_PyTestTransformed(PyObject * self, PyObject * args)
{
    PyObject * paths;
    PyObject * trafo;
    int x, y, filled;
    int i, cross_count = 0, result;

    if (!PyArg_ParseTuple(args, "O!O!iii", &PyTuple_Type, &paths, &SKTrafoType,
			  &trafo, &x, &y, &filled))
	return NULL;

    for (i = 0; i < PyTuple_Size(paths); i++)
    {
	PyObject * path = PyTuple_GetItem(paths, i);
	if (!SKCurve_Check(path))
	{
	    PyErr_SetString(PyExc_TypeError,
			    "First argument must be tuple of bezier paths");
	    return NULL;
	}
    }

    for (i = 0; i < PyTuple_Size(paths); i++)
    {
	SKCurveObject * path = (SKCurveObject*)PyTuple_GetItem(paths, i);
	result = SKCurve_TestTransformed(path, trafo, x, y, filled);
	if (result < 0)
	{
	    cross_count = -1;
	    break;
	}
	cross_count += result;
    }

    if (cross_count >= 0 && filled)
	return PyInt_FromLong(cross_count & 1);

    return PyInt_FromLong(cross_count >= 0 ? 0 : -1);
}


/*
 *
 */

PyObject *
SKCurve_PyBlendPaths(PyObject * self, PyObject * args)
{
    SKCurveObject *path1 = NULL, *path2 = NULL, *result;
    CurveSegment *seg1, *seg2, *resseg;
    double frac1, frac2, f13 = 1.0 / 3.0, f23 = 2.0 / 3.0;
    int i, length;

    if (!PyArg_ParseTuple(args, "O!O!dd", &SKCurveType, &path1,
			  &SKCurveType, &path2, &frac1, &frac2))
	return NULL;

    length = path1->len > path2->len ? path2->len : path1->len;

    result = (SKCurveObject*)SKCurve_New(length);
    if (!result)
	return NULL;

    seg1 = path1->segments;
    seg2 = path2->segments;
    resseg = result->segments;

    resseg->x = frac1 * seg1->x + frac2 * seg2->x;
    resseg->y = frac1 * seg1->y + frac2 * seg2->y;
    resseg->cont = seg1->cont == seg2->cont ? seg1->cont : ContAngle;

    resseg += 1; seg1 += 1; seg2 += 1;

    for (i = 1; i < length; i++, seg1++, seg2++, resseg++)
    {
	resseg->x = frac1 * seg1->x + frac2 * seg2->x;
	resseg->y = frac1 * seg1->y + frac2 * seg2->y;
	resseg->cont = seg1->cont == seg2->cont ? seg1->cont : ContAngle;

	if (seg1->type == seg2->type && seg1->type == CurveLine)
	{
	    resseg->type = CurveLine;
	}
	else
	{
	    /* at least one of the segments is a bezier segment convert the
	       other into a bezier segment first if necessary */
	    double x11, y11, x12, y12, x21, y21, x22, y22;

	    if (seg1->type == CurveLine)
	    {
		x11 = f13 * seg1[-1].x + f23 * seg1->x;
		y11 = f13 * seg1[-1].y + f23 * seg1->y;
		x12 = f23 * seg1[-1].x + f13 * seg1->x;
		y12 = f23 * seg1[-1].y + f13 * seg1->y;
	    }
	    else
	    {
		x11 = seg1->x1; y11 = seg1->y1;
		x12 = seg1->x2; y12 = seg1->y2;
	    }

	    if (seg2->type == CurveLine)
	    {
		x21 = f13 * seg2[-1].x + f23 * seg2->x;
		y21 = f13 * seg2[-1].y + f23 * seg2->y;
		x22 = f23 * seg2[-1].x + f13 * seg2->x;
		y22 = f23 * seg2[-1].y + f13 * seg2->y;
	    }
	    else
	    {
		x21 = seg2->x1; y21 = seg2->y1;
		x22 = seg2->x2; y22 = seg2->y2;
	    }

	    resseg->x1 = frac1 * x11 + frac2 * x21;
	    resseg->y1 = frac1 * y11 + frac2 * y21;
	    resseg->x2 = frac1 * x12 + frac2 * x22;
	    resseg->y2 = frac1 * y12 + frac2 * y22;
	    resseg->type = CurveBezier;
	}
    }

    if (path1->len == path2->len && path1->closed &&path2->closed)
	result->closed = 1;
    else
	result->closed = 0;
    result->len = length;

    return (PyObject*)result;
}


#ifndef PI
#define PI 3.14159265358979323846264338327
#endif

#define EVAL(coeff, t) (((coeff[0]*t + coeff[1])*t + coeff[2]) * t + coeff[3])
static double
arc_param(double * x, double * y, double angle)
{
    double coeff_x[4], coeff_y[4];
    double min_angle, min_t, max_angle, max_t, cur_angle, cur_t;
    int i, j, depth = 0;

    /* assume angle >= 0 */
    while (angle > PI)
    {
	angle -= 2 * PI;
    }

    for (i = 0; i < 4; i++)
    {
	coeff_x[i] = 0;
	coeff_y[i] = 0;
	for (j = 0; j < 4; j++)
	{
	    coeff_x[i] += bezier_basis[i][j] * x[j];
	    coeff_y[i] += bezier_basis[i][j] * y[j];
	}
    }

    min_angle = atan2(y[0], x[0]);
    max_angle = atan2(y[3], x[3]);
    if (max_angle < min_angle)
	min_angle -= PI + PI;
    if (angle > max_angle)
	angle -= PI + PI;

    min_t = 0.0; max_t = 1.0;

    while (depth < 15)
    {
	cur_t = (max_t + min_t) / 2;
	cur_angle = atan2(EVAL(coeff_y, cur_t), EVAL(coeff_x, cur_t));
	if (angle > cur_angle)
	{
	    min_t = cur_t;
	    min_angle = cur_angle;
	}
	else
	{
	    max_t = cur_t;
	    max_angle = cur_angle;
	}
	depth += 1;
    }

    if (max_angle - angle < angle - min_angle)
	return max_t;

    return min_t;
}
#undef EVAL

static void
subdivide(double * x, double * y, double t, int first)
{
    double s = 1.0 - t;
    double rx[7], ry[7];
    double ax, ay;

    rx[0] = x[0]; ry[0] = y[0]; rx[6] = x[3]; ry[6] = y[3];

    ax = s * x[1] + t * x[2];	 ay = s * y[1] + t * y[2];

    rx[1] = s * rx[0] + t * x[1];    ry[1] = s * ry[0] + t * y[1];
    rx[2] = s * rx[1] + t * ax;	     ry[2] = s * ry[1] + t * ay;

    rx[5] = s *	 x[2] + t * rx[6];   ry[5] = s *  y[2] + t * ry[6];
    rx[4] = s * ax    + t * rx[5];   ry[4] = s * ay    + t * ry[5];

    rx[3] = s * rx[2] + t * rx[4];   ry[3] = s * ry[2] + t * ry[4];

    if (first)
    {
	memcpy(x, rx, 4 * sizeof(double));
	memcpy(y, ry, 4 * sizeof(double));
    }
    else
    {
	memcpy(x, rx + 3, 4 * sizeof(double));
	memcpy(y, ry + 3, 4 * sizeof(double));
    }
}


static double arc_nodes_x[4] = {1.0, 0.0, -1.0,	 0.0};
static double arc_nodes_y[4] = {0.0, 1.0,  0.0, -1.0};
static double arc_controls_x[8]
= {1.0,	    0.55197, -0.55197, -1.0,	 -1.0,	  -0.55197, 0.55197, 1.0};
static double arc_controls_y[8]
= {0.55197, 1.0,      1.0,	0.55197, -0.55197, -1.0,   -1.0,     -0.55197};


PyObject *
SKCurve_PyApproxArc(PyObject * self, PyObject * args)
{
    double start_angle, end_angle;
    SKCurveObject * arc;
    int start_quad, end_quad, quadrant;
    int type = 0;	/* 0: arc, 1: chord, 2: pie slice as in const.py */
			/* special case: type = 3 for a complete ellipse */

    if (!PyArg_ParseTuple(args, "dd|i", &start_angle, &end_angle, &type))
	return NULL;

    /* normalize start_angle and end_angle */
    start_angle = fmod(start_angle, 2 * PI);
    if (start_angle < 0)
	start_angle += 2 * PI;
    end_angle = fmod(end_angle, 2 * PI);
    if (end_angle < 0)
	end_angle += 2 * PI;
    if (start_angle >= end_angle)
    {
	if (start_angle == end_angle)
	    type = 3;
	end_angle += 2 * PI;
    }
    /* now 0 <= start_angle < 2 * PI and start_angle <= end_angle */

    start_quad = start_angle / (PI / 2);
    end_quad = end_angle / (PI / 2);

    arc = (SKCurveObject*)SKCurve_New(4);
    if (!arc)
	return NULL;

    for (quadrant = start_quad; quadrant <= end_quad; quadrant++)
    {
	double x[4], y[4], t;

	x[0] = arc_nodes_x[quadrant % 4];
	y[0] = arc_nodes_y[quadrant % 4];
	x[1] = arc_controls_x[2 * (quadrant % 4)];
	y[1] = arc_controls_y[2 * (quadrant % 4)];
	x[2] = arc_controls_x[2 * (quadrant % 4) + 1];
	y[2] = arc_controls_y[2 * (quadrant % 4) + 1];
	x[3] = arc_nodes_x[(quadrant + 1) % 4];
	y[3] = arc_nodes_y[(quadrant + 1) % 4];

	if (quadrant == start_quad)
	{
	    t = arc_param(x, y, start_angle);
	    subdivide(x, y, t, 0);
	    /* the path is still empty and we have to create the first
	     * node */
	    SKCurve_AppendLine(arc, x[0], y[0], ContAngle);
	}
	if (quadrant == end_quad)
	{
	    t = arc_param(x, y, end_angle);
	    if (!t)
		break;
	    subdivide(x, y, t, 1);
	}

	SKCurve_AppendBezier(arc, x[1], y[1], x[2], y[2], x[3], y[3],
			     ContAngle);
    }

    if (type > 0)
    {
	if (type < 3)
	{
	    if (type == 2)
	    {
		SKCurve_AppendLine(arc, 0.0, 0.0, ContAngle);
	    }
	    SKCurve_AppendLine(arc, arc->segments[0].x, arc->segments[0].y,
			       ContAngle);
	}
	
	arc->closed = 1;
    }

    return (PyObject*)arc;
}


/*
 *
 */

PyObject *
SKCurve_PyRectanglePath(PyObject * self, PyObject * args)
{
    SKTrafoObject * trafo;
    SKCurveObject * path;

    if (!PyArg_ParseTuple(args, "O!", &SKTrafoType, &trafo))
	return NULL;

    path = (SKCurveObject*)SKCurve_New(5);

    SKCurve_AppendLine(path, trafo->v1, trafo->v2, ContAngle);
    SKCurve_AppendLine(path, trafo->v1 + trafo->m11, trafo->v2 + trafo->m21,
		       ContAngle);
    SKCurve_AppendLine(path, trafo->v1 + trafo->m11 + trafo->m12,
		       trafo->v2 + trafo->m21 + trafo->m22, ContAngle);
    SKCurve_AppendLine(path, trafo->v1 + trafo->m12, trafo->v2 + trafo->m22,
		       ContAngle);
    SKCurve_AppendLine(path, trafo->v1, trafo->v2, ContAngle);
    SKCurve_ClosePath(path);

    return (PyObject*)path;
}


static void
append_round_corner(SKCurveObject * path, SKTrafoObject * trafo, int quadrant)
{
    double x[4], y[4];
    int i;
    CurveSegment * last_segment;

    x[0] = arc_nodes_x[quadrant % 4];
    y[0] = arc_nodes_y[quadrant % 4];
    x[1] = arc_controls_x[2 * (quadrant % 4)];
    y[1] = arc_controls_y[2 * (quadrant % 4)];
    x[2] = arc_controls_x[2 * (quadrant % 4) + 1];
    y[2] = arc_controls_y[2 * (quadrant % 4) + 1];
    x[3] = arc_nodes_x[(quadrant + 1) % 4];
    y[3] = arc_nodes_y[(quadrant + 1) % 4];

    last_segment = path->segments + path->len - 1;
    /*fprintf(stderr, "last_xy %g %g\n", last_segment->x, last_segment->y);*/
    trafo->v1 = last_segment->x - trafo->m11 * x[0] - trafo->m12 * y[0];
    trafo->v2 = last_segment->y - trafo->m21 * x[0] - trafo->m22 * y[0];
    /*fprintf(stderr, "trafo->vi %g %g\n", trafo->v1, trafo->v2);*/
    for (i = 1; i < 4; i++)
    {
	double tx = x[i], ty = y[i];
	x[i] = trafo->m11 * tx + trafo->m12 * ty + trafo->v1;
	y[i] = trafo->m21 * tx + trafo->m22 * ty + trafo->v2;
    }

    SKCurve_AppendBezier(path, x[1], y[1], x[2], y[2], x[3], y[3], ContSmooth);
}

PyObject *
SKCurve_PyRoundedRectanglePath(PyObject * self, PyObject * args)
{
    SKTrafoObject * trafo;
    SKTrafoObject ellipse_trafo;
    SKCurveObject * path;
    double radius1, radius2;

    if (!PyArg_ParseTuple(args, "O!dd", &SKTrafoType, &trafo,
			  &radius1, &radius2))
	return NULL;

    ellipse_trafo.m11 = radius1 * trafo->m11;
    ellipse_trafo.m21 = radius1 * trafo->m21;

    ellipse_trafo.m12 = radius2 * trafo->m12;
    ellipse_trafo.m22 = radius2 * trafo->m22;

    path = (SKCurveObject*)SKCurve_New(9);

    SKCurve_AppendLine(path, trafo->v1 + ellipse_trafo.m11,
		       trafo->v2 + ellipse_trafo.m21, ContSmooth);
    
    SKCurve_AppendLine(path, trafo->v1 + trafo->m11 - ellipse_trafo.m11,
		       trafo->v2 + trafo->m21 - ellipse_trafo.m21,
		       ContSmooth);
    append_round_corner(path, &ellipse_trafo, 3);
    
    SKCurve_AppendLine(path,
		       trafo->v1 + trafo->m11 + trafo->m12 - ellipse_trafo.m12,
		       trafo->v2 + trafo->m21 + trafo->m22 - ellipse_trafo.m22,
		       ContSmooth);
    append_round_corner(path, &ellipse_trafo, 0);
    
    SKCurve_AppendLine(path,
		       trafo->v1 + ellipse_trafo.m11 + trafo->m12,
		       trafo->v2 + ellipse_trafo.m21 + trafo->m22,
		       ContSmooth);
    append_round_corner(path, &ellipse_trafo, 1);
    
    SKCurve_AppendLine(path, trafo->v1 + ellipse_trafo.m12,
		       trafo->v2 + ellipse_trafo.m22, ContSmooth);
    append_round_corner(path, &ellipse_trafo, 2);
    SKCurve_ClosePath(path);

    return (PyObject*)path;
}
