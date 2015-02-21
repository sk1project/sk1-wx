/* Sketch - A Python-based interactive drawing program
 * Copyright (C) 1998, 1999 by Bernhard Herzog
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

#include "sktrafo.h"
#include "skrect.h"
#include "curvemisc.h"
#include "curvelow.h"


#define EVAL(coeff, t) (((coeff[0]*t + coeff[1])*t + coeff[2]) * t + coeff[3])

PyObject *
curve_local_coord_system(SKCurveObject * self, PyObject * args)
{
    double pos, t;
    int index;
    double x[4], y[4];
    double point_x, point_y, tangent_x, tangent_y, length;

    if(!PyArg_ParseTuple(args, "d", &pos))
	return NULL;

    index = floor(pos);
    if (index >= self->len - 1 || index < 0)
    {
	PyErr_SetString(PyExc_ValueError, "parameter out of range");
	return NULL;
    }

    t = pos - index;

    x[0] = self->segments[index].x;
    y[0] = self->segments[index].y;
    x[3] = self->segments[index + 1].x;
    y[3] = self->segments[index + 1].y;
    if (self->segments[index].type == CurveBezier)
    {
	x[1] = self->segments[index + 1].x1;
	y[1] = self->segments[index + 1].y1;
	x[2] = self->segments[index + 1].x2;
	y[2] = self->segments[index + 1].y2;
	bezier_point_at(x, y, t, &point_x, &point_y);
	bezier_tangent_at(x, y, t, &tangent_x, &tangent_y);
    }
    else
    {
	point_x = x[0] * (1 - t) + x[3] * t;
	point_y = y[0] * (1 - t) + y[3] * t;
	tangent_x = x[3] - x[0];
	tangent_y = y[3] - y[0];
    }
    
    length = hypot(tangent_x, tangent_y);
    if (length > 0)
    {
	/* XXX what to do in degenerate case length == 0?*/
	tangent_x /= length;
	tangent_y /= length;
    }
    return SKTrafo_FromDouble(tangent_x, tangent_y, -tangent_y, tangent_x,
			      point_x, point_y);
}


static int
add_point(PyObject * list, double length, PyObject * point)
{
    PyObject * tuple = NULL;
    int result = -1;
    
    if (point)
    {
	tuple = Py_BuildValue("dO", length, point);
	if (tuple)
	    result = PyList_Append(list, tuple);
    }
    Py_XDECREF(tuple);
    Py_XDECREF(point);
    return result;
}
	

static int
curve_arc_length_curve(double * xs, double * ys, double start_param,
		       double * length, PyObject * list)
{
    double	coeff_x[4], coeff_y[4];
    int		i, j;
    double	delta, t, t2, t3, x, y, lastx, lasty;
    int		num_steps = BEZIER_NUM_STEPS;
    
    for (i = 0; i < 4; i++)
    {
	coeff_x[i] = 0;
	coeff_y[i] = 0;
	for (j = 0; j < 4; j++)
	{
	    coeff_x[i] += bezier_basis[i][j] * xs[j];
	    coeff_y[i] += bezier_basis[i][j] * ys[j];
	}
    }
    
    lastx = EVAL(coeff_x, start_param);
    lasty = EVAL(coeff_y, start_param);

    delta = 1.0 / num_steps;
    t = start_param;
    num_steps = (1.0 - start_param) / delta;
    for (i = 0; i < num_steps; i++)
    {
	t += delta;
	t2 = t * t;
	t3 = t2 * t;
	x = coeff_x[0] * t3 + coeff_x[1] * t2 + coeff_x[2] * t + coeff_x[3];
	y = coeff_y[0] * t3 + coeff_y[1] * t2 + coeff_y[2] * t + coeff_y[3];
	*length += hypot(x - lastx, y - lasty);
	if (add_point(list, *length, SKPoint_FromXY(x, y)) < 0)
	    return -1;
	lastx = x;
	lasty = y;
    }

    return 0;
}

static int
curve_arc_length_straight(double x1, double y1, double x2, double y2,
			  double start_param, double * length, PyObject * list)
{
    *length += (1.0 - start_param) * hypot(x2 - x1, y2 - y1);
    return add_point(list, *length, SKPoint_FromXY(x2, y2));
}
    

PyObject *
curve_arc_lengths(SKCurveObject * self, PyObject * args)
{
    PyObject * list;
    int index, first = 1;
    double length = 0;
    double start_param = 0.0;

    if (!PyArg_ParseTuple(args, "|d", &start_param))
	return NULL;

    index = floor(start_param);
    start_param = start_param - index;
    index = index + 1;

    if (index < 1 || index > self->len)
    {
	PyErr_SetString(PyExc_ValueError, "invalid start parameter");
	return NULL;
    }
    if (index == self->len)
    {
	index = self->len - 1;
	start_param = 1.0;
    }

    list = PyList_New(0);
    if (!list)
	return NULL;

    for (; index < self->len; index++)
    {
	if (self->segments[index].type == CurveBezier)
	{
	    double x[4], y[4];
	    double sx, sy;
	    CurveSegment * segment = self->segments + index;

	    x[0] = segment[-1].x;	y[0] = segment[-1].y;
	    x[1] = segment->x1;		y[1] = segment->y1;
	    x[2] = segment->x2;		y[2] = segment->y2;
	    x[3] = segment->x;		y[3] = segment->y;
	    if (first)
	    {
		bezier_point_at(x, y, start_param, &sx, &sy);
		if (add_point(list, 0, SKPoint_FromXY(sx, sy)) < 0)
		    goto fail;
		first = 0;
	    }
	    if (curve_arc_length_curve(x, y, start_param, &length, list) < 0)
		goto fail;
	}
	else
	{
	    if (first)
	    {
		double sx, sy;
		sx = (1 - start_param) * self->segments[index - 1].x
		    + start_param * self->segments[index].x;
		sy = (1 - start_param) * self->segments[index - 1].y
		    + start_param * self->segments[index].y;
		if (add_point(list, 0, SKPoint_FromXY(sx, sy)) < 0)
		    goto fail;
		first = 0;
	    }
	    if (curve_arc_length_straight(self->segments[index - 1].x,
					  self->segments[index - 1].y,
					  self->segments[index].x,
					  self->segments[index].y,
					  start_param, &length, list) < 0)
		goto fail;
	}
	start_param = 0.0;
    }

    return list;
    
 fail:
    Py_DECREF(list);
    return NULL;
}



/*
 *
 */


static double
nearest_on_line(double x1, double y1, double x2, double y2, double x, double y,
		double * t)
{
    double vx = x2 - x1;
    double vy = y2 - y1;
    double length = hypot(vx, vy);
    double dx = x - x1;
    double dy = y - y1;
    double distance, linepos;

    if (length > 0)
    {
	distance = abs((dx * vy - dy * vx) / length);
	linepos = (dx * vx + dy * vy) / length;
	if (linepos < 0.0)
	{
	    *t = 0;
	    distance = hypot(dx, dy);
	}
	else if (linepos > length)
	{
	    *t = 1;
	    distance = hypot(x - x2, y - y2);
	}
	else
	{
	    *t = linepos / length;
	}
    }
    else
    {
	distance = hypot(dx, dy);
	*t = 0;
    }
    return distance;
}

double
nearest_on_curve(double *x, double *y, double px, double py, double *pt)
{
    double coeff_x[4], coeff_y[4];
    int i, j;
    double t, lt, mint = 0, mindist = 1e100, dist;
    double x1, y1, x2, y2;

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

    x1 = coeff_x[3]; y1 = coeff_y[3];
    for (t = 0.015625; t <= 1.0; t += 0.015625)
    {
	x2 = EVAL(coeff_x, t);
	y2 = EVAL(coeff_y, t);

	dist = nearest_on_line(x1, y1, x2, y2, px, py, &lt);
	if (dist < mindist)
	{
	    mindist = dist;
	    mint = t + (lt - 1) * 0.015625;
	}
	x1 = x2; y1 = y2;
    }
    *pt = mint;
    return mindist;
}

PyObject *
SKCurve_NearestPointPy(SKCurveObject * self, PyObject * args)
{
    double x, y;
    double bx[4], by[4];
    double min_distance = 1e100, max_distance = 0.0, distance;
    double nearest_t = 0, t;
    double bound_left = 0, bound_right = 0, bound_top = 0, bound_bottom = 0;
    int use_max_dist = 0;
    int i, found = 0;
    CurveSegment * segment;
    PyObject * result;

    if (!PyArg_ParseTuple(args, "dd|d", &x, &y, &max_distance))
	return NULL;

    use_max_dist = max_distance > 0;

    bound_left = x - max_distance;
    bound_right = x + max_distance;
    bound_top = y + max_distance;
    bound_bottom = y - max_distance;
	
    segment = self->segments + 1;
    for (i = 1; i < self->len; i++, segment++)
    {
	if (segment->type == CurveBezier)
	{
	    bx[0] = segment[-1].x;	by[0] = segment[-1].y;
	    bx[1] = segment->x1;	by[1] = segment->y1;
	    bx[2] = segment->x2;	by[2] = segment->y2;
	    bx[3] = segment->x;		by[3] = segment->y;
	    if (use_max_dist)
	    {
		SKRectObject r;
		r.left = r.right = bx[0];
		r.top = r.bottom = by[0];
		SKRect_AddXY(&r, bx[1], by[1]);
		SKRect_AddXY(&r, bx[2], by[2]);
		SKRect_AddXY(&r, bx[3], by[3]);
		
		if (r.left > bound_right || r.right < bound_left
		    || r.top < bound_bottom || r.bottom > bound_top)
		{
		    continue;
		}
	    }
	    distance = nearest_on_curve(bx, by, x, y, &t);
	}
	else
	{
	    distance = nearest_on_line(segment[-1].x, segment[-1].y,
				       segment->x, segment->y, x, y, &t);
	}
	
	if (distance < min_distance)
	{
	    min_distance = distance;
	    nearest_t = (double)(i - 1) + t;
	    found = 1;
	}
    }

    if (found)
    {
	result = PyFloat_FromDouble(nearest_t);
    }
    else
    {
	Py_INCREF(Py_None);
	result = Py_None;
    }

    return result;
}



PyObject *
SKCurve_PointAtPy(SKCurveObject * self, PyObject * args)
{
    double x[4], y[4];
    double t, px, py;
    int i;
    
    if (!PyArg_ParseTuple(args, "d", &t))
	return NULL;

    i = floor(t);
    t = t - i;
    i = i + 1;

    if (i < 1 || i > self->len)
    {
	PyErr_SetString(PyExc_ValueError, "invalid curve parameter");
	return NULL;
    }
    if (i == self->len)
    {
	i = self->len - 1;
	t = 1.0;
    }

    if (self->segments[i].type == CurveBezier)
    {
	x[0] = self->segments[i - 1].x;	y[0] = self->segments[i - 1].y;
	x[1] = self->segments[i].x1;	y[1] = self->segments[i].y1;
	x[2] = self->segments[i].x2;	y[2] = self->segments[i].y2;
	x[3] = self->segments[i].x;		y[3] = self->segments[i].y;

	bezier_point_at(x, y, t, &px, &py);
    }
    else
    {
	px = (1 - t) * self->segments[i - 1].x + t * self->segments[i].x;
	py = (1 - t) * self->segments[i - 1].y + t * self->segments[i].y;
    }

    return SKPoint_FromXY(px, py);
}
    
