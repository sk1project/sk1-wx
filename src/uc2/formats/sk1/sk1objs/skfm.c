/* Sketch - A Python-based interactive drawing program
 * Copyright (C) 1997, 1998, 2002, 2006 by Bernhard Herzog
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
 *	A Python Object for fontmetrics.
 *
 * A fontmetrics object contains all the information about a scalable
 * font needed to `typeset' some text. It provides some methods that
 * compute various rectangles for given strings.
 *
 * All dimensions are stored as ints in 1000-pixel metric. That means
 * that the ascender of a 12pt instance of a font is 12 * ascender /
 * 1000.0 points, etc.
 *
 * All strings are assumed to be in the same encoding as the
 * fontmetrics. In fact, the fontmetric object doesn't know anything
 * about encodings. That is assumed to be handled appropriately in
 * Python code. (The Fontmetric object has to be changed, of course, if
 * we want to use more than 8 bits per character)
 *
 * Currently, font metrics are read from afm-files by some python code
 * and passed to the constructors for this object type.
 *
 * Fontmetric objects are immutable.
 *
 */

#include <Python.h>
#include <structmember.h>

#include "skpoint.h"


/* the metrics for one character */
struct SKCharMetric_s {
    int width;			/* width */
    int llx, lly, urx, ury;	/* bounding box */
};
typedef struct SKCharMetric_s SKCharMetric;

/* the font metrics */
struct SKFontMetric_s {
    PyObject_HEAD
    int			ascender, descender;	/* global ascender/descender */
    int			llx, lly, urx, ury;	/* font bounding box */
    float		italic_angle;		/* italic angle as in afm
						   file */
    SKCharMetric	char_metric[256];
};
typedef struct SKFontMetric_s SKFontMetric;




static void
skfm_dealloc(SKFontMetric * self)
{
    PyObject_Del(self);
}


/*
 *	fm.string_bbox(STRING)
 *
 * Return the bounding box of STRING as a tuple (llx, lly, urx, ury) in
 * 1000-pixel metric. The first character is positioned at (0, 0).
 */
static PyObject *
skfm_string_bbox(SKFontMetric * self, PyObject * args)
{
    unsigned char * string;
    int length, i;
    int	llx = 0, lly = 0, urx = 0, ury = 0;
    int pos = 0;
    SKCharMetric * metric;

    if (!PyArg_ParseTuple(args, "s#", &string, &length))
	return NULL;

    for (i = 0; i < length; i++)
    {
	metric = self->char_metric + string[i];
	if (pos + metric->llx < llx)
	    llx = pos + metric->llx;
	if (pos + metric->urx > urx)
	    urx = pos + metric->urx;
	if (metric->lly < lly)
	    lly = metric->lly;
	if (metric->ury > ury)
	    ury = metric->ury;
	pos += metric->width;
    }

    return Py_BuildValue("iiii", llx, lly, urx, ury);
}

/*
 *	fm.string_width(STRING[, MAXPOS])
 *
 * Return the setwidth of STRING in 1000-pixel metrics. No kerning or
 * ligatures are taken into account (maybe in the future).
 *
 * If provided, MAXCHAR is equivalent to using STRING[:MAXCHAR] instead
 * of STRING. MAXCHAR defaults to the length of STRING. It usefule to
 * compute the position of a caret (See Font.TextCaretData() in font.py)
 */

static PyObject *
skfm_string_width(SKFontMetric * self, PyObject * args)
{
    unsigned char * string;
    int length, i, maxpos = -1;
    int width = 0;

    if (!PyArg_ParseTuple(args, "s#|i", &string, &length, &maxpos))
	return NULL;

    if (maxpos >= 0 && maxpos < length)
	length = maxpos;

    for (i = 0; i < length; i++)
	width += self->char_metric[string[i]].width;

    return Py_BuildValue("i", width);
}

/*
 *	fm.char_width(CHR)
 *
 * Return the setwidth of the character with code CHR (CHR is an int).
 */
static PyObject *
skfm_char_width(SKFontMetric * self, PyObject * args)
{
    int chr;

    if (!PyArg_ParseTuple(args, "i", &chr))
	return NULL;

    if (0 <= chr && chr < 256)
	return PyInt_FromLong(self->char_metric[chr].width);

    PyErr_SetString(PyExc_ValueError,
		    "argument must be in the range [0 .. 255]");
    return NULL;
}


/*
 *	fm.char_bbox(CHR)
 *
 * Return the bounding box of the character with code CHR (CHR is an
 * int).
 */
static PyObject *
skfm_char_bbox(SKFontMetric * self, PyObject * args)
{
    int chr;

    if (!PyArg_ParseTuple(args, "i", &chr))
	return NULL;

    if (0 <= chr && chr < 256)
    {
	SKCharMetric * metric = self->char_metric + chr;
	return Py_BuildValue("iiii", metric->llx, metric->lly,
			     metric->urx, metric->ury);
    }
    PyErr_SetString(PyExc_ValueError,
		    "argument must be in the range [0 .. 255]");
    return NULL;
}

/*
 *	fm.typeset_string(STRING)
 *
 * Return a list of SKPoint objects, one for each char in STRING,
 * indicating the coordinates of the characters origin. The first char
 * is set at (0, 0).
 */
static PyObject *
skfm_typeset_string(SKFontMetric * self, PyObject * args)
{
    unsigned char * string;
    int length, i;
    int width = 0;
    PyObject * list;
    PyObject * point;

    if (!PyArg_ParseTuple(args, "s#", &string, &length))
	return NULL;

    list = PyList_New(length);
    if (!list)
	return NULL;

    for (i = 0; i < length; i++)
    {
	point = SKPoint_FromXY(width / 1000.0, 0.0);
	if (!point)
	{
	    Py_DECREF(list);
	    return NULL;
	}
	if (PyList_SetItem(list, i, point) < 0)
	{
	    Py_DECREF(list);
	    return NULL;
	}
	width += self->char_metric[string[i]].width;
    }

    return list;
}

#define OFF(x) offsetof(SKFontMetric, x)
static struct memberlist skfm_memberlist[] = {
    {"ascender",	T_INT,		OFF(ascender),		RO},
    {"descender",	T_INT,		OFF(descender),		RO},
    {"llx",		T_INT,		OFF(llx),		RO},
    {"lly",		T_INT,		OFF(lly),		RO},
    {"urx",		T_INT,		OFF(urx),		RO},
    {"ury",		T_INT,		OFF(ury),		RO},
    {"italic_angle",	T_FLOAT,	OFF(italic_angle),	RO},
    {NULL} 
};

static struct PyMethodDef skfm_methods[] = {
    {"typeset_string",	(PyCFunction)skfm_typeset_string,	1},
    {"string_bbox",	(PyCFunction)skfm_string_bbox,		1},
    {"string_width",	(PyCFunction)skfm_string_width,		1},
    {"char_width",	(PyCFunction)skfm_char_width,		1},
    {"char_bbox",	(PyCFunction)skfm_char_bbox,		1},
    {NULL,	NULL}
};

static PyObject *
skfm_getattr(PyObject * self, char * name)
{
    PyObject * result;

    result = Py_FindMethod(skfm_methods, self, name);
    if (result != NULL)
	return result;
    PyErr_Clear();

    return PyMember_Get((char *)self, skfm_memberlist, name);
}

PyTypeObject SKFontMetricType = {
	PyObject_HEAD_INIT(NULL)
	0,
	"skfm",
	sizeof(SKFontMetric),
	0,
	(destructor)skfm_dealloc,	/*tp_dealloc*/
	(printfunc)NULL,		/*tp_print*/
	skfm_getattr,			/*tp_getattr*/
	0,				/*tp_setattr*/
	0,				/*tp_compare*/
	0,				/*tp_repr*/
	0,				/*tp_as_number*/
	0,				/*tp_as_sequence*/
	0,				/*tp_as_mapping*/
	0,				/*tp_hash*/
};


/*
 * Return a new, empty fontmetric object.
 */
PyObject *
SKFontMetric_New()
{
    SKFontMetric * self;

    self = PyObject_New(SKFontMetric, &SKFontMetricType);
    if (self == NULL)
	return NULL;

    return (PyObject*)self;
}

/* the module functions */


/*
 *	skfm.CreateMetric(ASCENDER, DESCENDER, FONTBBOX, ITALIC, CHARMETRICS)
 *
 * Return a new fontmetric object initialized with the given parameters:
 *
 *	ASCENDER	ascender
 *	DESCENDER	descender
 *	FONTBBOX	The font bounding box as a tuple (llx, lly, urx, ury)
 *			in 1000-pixel metrics.
 *	ITALIC		the italic angle in degrees ccw from straight up.
 *	CHARMETRICS	A sequence of 256 tuples (width, llx, lly, urx, ury),
 *			the metrics of each character in 1000-pixel metrics
 */

PyObject *
SKFM_PyCreateMetric(PyObject * self, PyObject * args)
{
    int ascender, descender;
    PyObject * list;
    SKFontMetric * metric;
    int fllx, flly, furx, fury;
    float italic_angle;
    int i;

    if (!PyArg_ParseTuple(args, "ii(iiii)fO", &ascender, &descender,
			  &fllx, &flly, &furx, &fury, &italic_angle, &list))
	return NULL;

    if (!PySequence_Check(list))
    {
	PyErr_SetString(PyExc_TypeError,
			"fifth argument must be a sequence of tuples");
	return NULL;
    }

    if (PySequence_Length(list) < 256)
    {
	PyErr_SetString(PyExc_ValueError,
			"CHARMETRICS must have 256 elements");
	return NULL;
    }

    metric = (SKFontMetric*)SKFontMetric_New();
    if (!metric)
	return NULL;

    metric->ascender = ascender;
    metric->descender = descender;
    metric->llx = fllx;
    metric->lly = flly;
    metric->urx = furx;
    metric->ury = fury;
    metric->italic_angle = italic_angle;

    for (i = 0; i < 256; i++)
    {
	int width, llx, lly, urx, ury;
	PyObject * tuple = PySequence_GetItem(list, i);
	SKCharMetric * char_metric = metric->char_metric + i;

	if (!PyArg_ParseTuple(tuple, "iiiii;"
			   "CHARMETRICS item must be (w, llx, lly, urx, ury)",
			      &width, &llx, &lly, &urx, &ury))
	{
	    Py_DECREF(tuple);
	    return NULL;
	}
	Py_DECREF(tuple);
	char_metric->width = width;
	char_metric->llx = llx;
	char_metric->lly = lly;
	char_metric->urx = urx;
	char_metric->ury = ury;
    }

    return (PyObject*) metric;
}

