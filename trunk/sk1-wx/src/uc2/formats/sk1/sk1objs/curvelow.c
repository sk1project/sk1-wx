/* Sketch - A Python-based interactive drawing program
 * Copyright (C) 2006 by Igor E.Novikov
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


/*
 *	`low level' routines for bezier curves
 */


#include "math.h"
// #include "X11/Xlib.h"
#include "curvelow.h"


#define PREC_BITS 4
#define ROUND(x) (((x) + (1 << (PREC_BITS - 1))) >> PREC_BITS)

#define SMOOTH_EPSILON 8
/* return true if the curve segment given by x[] and y[] is smooth. */
static int
is_smooth(int * x, int * y)
{
    long vx, vy, dx, dy, len = 0, lensqr, dist, par;

    vx = x[3] - x[0]; vy = y[3] - y[0];
    lensqr = vx * vx + vy * vy;

    dx = x[1] - x[0]; dy = y[1] - y[0];
    if (lensqr)
    {
	par = vx * dx + vy * dy;
	if (par < 0 || par > lensqr)
	    return 0;
	len = sqrt(lensqr);
	dist = abs(vx * dy - vy * dx);
	if (dist > len * SMOOTH_EPSILON)
	    return 0;
    }
    else if (dx != 0 || dy != 0)
	return 0;

    dx = x[2] - x[3]; dy = y[2] - y[3];
    if (lensqr)
    {
	par = vx * dx + vy * dy;
	if (par > 0 || par < -lensqr)
	    return 0;
	dist = abs(vx * dy - vy * dx);
	if (dist > len * SMOOTH_EPSILON)
	    return 0;
    }
    else if (dx != 0 || dy != 0)
	return 0;

    return 1;
}


/* determine whether the line fom (SX, SY) to (EX, EY) is `hit' by a
 * click at (PX, PY), or whether a polygon containing this line is hit
 * in the interior at (PX, PY).
 *
 * Return -1 if the line it self his hit. Otherwise, return +1 if a
 * horizontal line from (PX, PY) to (-Infinity, PY) intersects the line
 * and 0 if it doesn't.
 *
 * The nonnegative return values can be used to determine whether (PX, PY)
 * is an interior point of a polygon according to the even-odd rule.
 */

static int
bezier_test_line(int sx, int sy, int ex, int ey, int px, int py)
{
    long vx, vy, dx, dy, len, dist, not_horizontal;

    if (ey < sy)
    {
	dist = ex; ex = sx; sx = dist;
	dist = ey; ey = sy; sy = dist;
    }
    not_horizontal = ey > sy + (2 << PREC_BITS);
    if (not_horizontal && (py >= ey || py < sy))
	return 0;

    vx = ex - sx; vy = ey - sy;

    len = sqrt(vx * vx + vy * vy);
    if (!len)
	/* degenerate case of coincident end points. Assumes that some
	 * other part of the code has already determined whether the end
	 * point is hit.
	 */
	return 0;

    dx = px - sx; dy = py - sy;
    dist = vx * dy - vy * dx;
    if ((not_horizontal || (px >= sx && px <= ex) || (px >= ex && px <= sx))
	&& abs(dist) <= (len << (PREC_BITS + 1)))
	return -1;

    /* horizontal lines (vy == 0) always return 0 here. */
    return vy && py < ey && py >= sy && dx * abs(vy) > vx * abs(dy);
}


#define DUMP_TEST 0
static int
bezier_hit_recurse(int * x, int * y, int px, int py, int depth)
{
    int	u[7], v[7];
    int	tx, ty;
    int	i, result1, result2;
    int	minx = *x, maxx = *x, miny = *y, maxy = *y;

    for (i = 1; i < 4; i++)
    {
	if (x[i] < minx)
	    minx = x[i];
	if (x[i] > maxx)
	    maxx = x[i];
	if (y[i] < miny)
	    miny = y[i];
	if (y[i] > maxy)
	    maxy = y[i];
    }

    if (px <= minx || py >= maxy || py < miny)
    {
#if DUMP_TEST
	fprintf(stderr, "/\\/(%d) %d %d: %d %d	%d %d --> 0\n",
		depth, px, py, x[0], y[0], x[3], y[3]);
#endif
	return 0;
    }
    if (px >= maxx && (	  (py >= y[0]	&&   py < y[3])
		       || (py >= y[3]	&&   py < y[0])))
    {
#if DUMP_TEST
	fprintf(stderr, "/\\/(%d) %d %d: %d %d	%d %d --> 1\n",
		depth, px, py, x[0], y[0], x[3], y[3]);
#endif
	return +1;
    }
#if DUMP_TEST
    fprintf(stderr, ">>>(%d) %d %d: %d %d  %d %d [%d, %d, %d, %d]--> ?\n",
	    depth, px, py, x[0], y[0], x[3], y[3], minx, maxx, miny, maxy);
#endif

    u[1] = x[0] + x[1];
    v[1] = y[0] + y[1];
    tx = x[1] + x[2];
    ty = y[1] + y[2];
    u[5] = x[2] + x[3];
    v[5] = y[2] + y[3];

    u[2] = u[1] + tx;
    v[2] = v[1] + ty;
    u[4] = u[5] + tx;
    v[4] = v[5] + ty;

    u[3] = (u[2] + u[4] + 4) >> 3;
    v[3] = (v[2] + v[4] + 4) >> 3;

    if (depth > 0)
    {
	u[0] = x[0];		v[0] = y[0];
	u[1] = (u[1] + 1) >> 1;	v[1] = (v[1] + 1) >> 1;
	u[2] = (u[2] + 2) >> 2;	v[2] = (v[2] + 2) >> 2;
	if (is_smooth(u, v))
	{
	    result1 = bezier_test_line(u[0], v[0], u[3], v[3], px, py);
#if DUMP_TEST
	    if (result1)
		fprintf(stderr, "##1(%d) %d %d: %d %d  %d %d --> %d\n",
			depth, px, py, u[0], v[0], u[3], v[3], result1);
#endif
	}
	else
	{
	    result1 = bezier_hit_recurse(u, v, px, py, depth - 1);
#if DUMP_TEST
	    if (result1)
	  fprintf(stderr, "<<1(%d) %d %d: %d %d	 %d %d	%d %d  %d %d --> %d\n",
		  depth, px, py,
		  u[0], v[0], u[1], v[1], u[2], v[2], u[3], v[3], result1);
#endif
	}
	if (result1 < 0)
	{
	    return result1;
	}

	u[4] = (u[4] + 2) >> 2;	v[4] = (v[4] + 2) >> 2;
	u[5] = (u[5] + 1) >> 1;	v[5] = (v[5] + 1) >> 1;
	u[6] = x[3];		v[6] = y[3];
	if (is_smooth(u + 3, v + 3))
	{
	    result2 = bezier_test_line(u[3], v[3], u[6], v[6], px, py);
#if DUMP_TEST
	    if (result2)
		fprintf(stderr, "##2(%d) %d %d: %d %d  %d %d --> %d\n",
			depth, px, py, u[3], v[3], u[6], v[6], result2);
#endif
	}
	else
	{
	    result2 = bezier_hit_recurse(u + 3, v + 3, px, py, depth - 1);
#if DUMP_TEST
	    if (result2)
	  fprintf(stderr, "<<2(%d) %d %d: %d %d	 %d %d	%d %d  %d %d --> %d\n",
		  depth, px, py,
		  u[0], v[0], u[1], v[1], u[2], v[2], u[3], v[3], result2);
#endif
	}
	if (result2 < 0)
	{
	    return result2;
	}

	if (result1 || result2)
	{
#if DUMP_TEST
	  fprintf(stderr, "+++(%d) %d %d: %d %d	 %d %d	%d %d  %d %d --> %d\n",
		    depth, px, py,
		    u[0], v[0], u[1], v[1], u[2], v[2], u[3], v[3],
		  result1 + result2);
#endif
	  return result1 + result2;
	}
	return 0;
    }

    result1 = bezier_test_line(x[0], y[0], x[3], y[3], px, py);

#if DUMP_TEST
    if (result1)
	fprintf(stderr, "***(%d) %d %d: %d %d  %d %d --> %d\n",
		depth, px, py, x[0], y[0], x[3], y[3], result1);
#endif
    return result1;
}

int
bezier_hit_segment(int * x, int * y, int px, int py)
{
    int i;

    for (i = 0; i < 4; i++)
    {
	x[i] <<= PREC_BITS; y[i] <<= PREC_BITS;
    }

    px = (px << PREC_BITS) + 1;
    py = (py << PREC_BITS) + 1;

    if (is_smooth(x, y))
    {
#if DUMP_TEST
	int result = bezier_test_line(x[0], y[0], x[3], y[3], px, py);
	fprintf(stderr, "---(*) %d %d: %d %d  %d %d --> %d\n",
		px, py, x[0], y[0], x[3], y[3], result);
	return result;
#else
	return bezier_test_line(x[0], y[0], x[3], y[3], px, py);
#endif
    }

    return bezier_hit_recurse(x, y, px, py, BEZIER_DEPTH);
}

int
bezier_hit_line(int sx, int sy, int ex, int ey, int px, int py)
{
    sx <<= PREC_BITS; sy <<= PREC_BITS;
    ex <<= PREC_BITS; ey <<= PREC_BITS;
    px = (px << PREC_BITS) + 1;
    py = (py << PREC_BITS) + 1;

#if DUMP_TEST
    {
	int result = bezier_test_line(sx, sy, ex, ey, px, py);
	fprintf(stderr, "---(-) %d %d: %d %d  %d %d --> %d\n",
		px, py, sx, sy, ex, ey, result);
	return result;
    }
#else
    return bezier_test_line(sx, sy, ex, ey, px, py);
#endif
}

/*
 *
 */

int bezier_basis[4][4] =
{
    {	-1,	3,     -3,	1},
    {	 3,    -6,	3,	0},
    {	-3,	3,	0,	0},
    {	 1,	0,	0,	0}
};




#define EVAL(coeff, t) (((coeff[0]*t + coeff[1])*t + coeff[2]) * t + coeff[3])
void
bezier_point_at(double *x, double *y, double t,
		double * result_x, double * result_y)
{
    double coeff_x[4], coeff_y[4];
    int i, j;

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

    *result_x = EVAL(coeff_x, t);
    *result_y = EVAL(coeff_y, t);
}
    
#define EVALDIFF(coeff, t) ((3 * coeff[0] * t + 2 * coeff[1]) * t + coeff[2])
void
bezier_tangent_at(double *x, double *y, double t,
		  double * result_x, double * result_y)
{
    double coeff_x[3], coeff_y[3];
    int i, j;

    for (i = 0; i < 3; i++)
    {
	coeff_x[i] = 0;
	coeff_y[i] = 0;
	for (j = 0; j < 4; j++)
	{
	    coeff_x[i] += bezier_basis[i][j] * x[j];
	    coeff_y[i] += bezier_basis[i][j] * y[j];
	}
    }

    *result_x = EVALDIFF(coeff_x, t);
    *result_y = EVALDIFF(coeff_y, t);
}
#undef EVAL
#undef EVALDIFF

