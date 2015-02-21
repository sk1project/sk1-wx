/* Sketch - A Python-based interactive drawing program
 * Copyright (C) 1997, 1998 by Bernhard Herzog
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

#ifndef CURVEOBJECT_H
#define CURVEOBJECT_H

#if defined(__cplusplus)
extern "C" {
#endif

#include "skpoint.h"  /* for SKCoord */
#include "sktrafo.h" 

/*
 * A single curve segment
 */

typedef struct {
    char	type;	/* whether segment is a bezier segment or a line */
    char	cont;		/* continuity */
    char	selected;	/* true, if node is selected */
    SKCoord	x1, y1, x2, y2;	    /* for beziers, the coordinates of the
				     * control points */
    SKCoord	x, y;
} CurveSegment;

#define CurveBezier	1
#define CurveLine	2

#define IsValidSegmentType(type) ((type) == CurveBezier || (type) == CurveLine)

/* The values for continuity are ordered by increasing interdependence
 * of the control points of the bezier segments to which the node
 * belongs. For ContAngle, the controlpoints are completely independent,
 * for ContSmooth, the control points and the node lie on a line and for
 * ContSymmetrical the distances between the control points and the node
 * are the same, additionally. Some functions use this fact.
 */

#define ContAngle	0
#define ContSmooth	1
#define ContSymmetrical 2

#define CHECK_CONT(cont) ((cont) >= 0 && (cont) <= 2)

/*
 *	A single open or closed path of bezier or line segments
 */

typedef struct {
    PyObject_HEAD
    int			len;		/* # of nodes */
    int			allocated;	/* # of entries allocated */
    CurveSegment *	segments;	/* list of segments */
    char		closed;		/* true, if path is closed */
} SKCurveObject;



extern PyTypeObject SKCurveType;

#define SKCurve_Check(v)		((v)->ob_type == &SKCurveType)


PyObject * SKCurve_New(int len);

int SKCurve_AppendSegment(SKCurveObject * self, CurveSegment * segment);
int SKCurve_AppendLine(SKCurveObject * self, double x, double y,
		       int continuity);
int SKCurve_AppendBezier(SKCurveObject * self, double x1, double y1,
			 double x2, double y2,
			 double x, double y,
			 int continuity);
int SKCurve_ClosePath(SKCurveObject * self);
int SKCurve_TestTransformed(SKCurveObject * self,
			    PyObject * trafo, int test_x, int test_y,
			    int closed);
int SKCurve_Transform(SKCurveObject * self, PyObject * trafo);

#define SKCurve_LENGTH(curve) (((SKCurveObject*)curve)->len)

/* internal functions */
PyObject * _SKCurve_NumAllocated(PyObject * self, PyObject * args);
int _SKCurve_InitCurveObject(void);


/*
 *	Editor
 */

#define SelNone		0
#define SelNodes	1
#define SelSegmentFirst	2
#define SelSegmentLast	3

#if defined(__cplusplus)
}
#endif

#endif /* CURVEOBJECT_H*/
