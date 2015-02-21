/* Sketch - A Python-based interactive drawing program
 * Copyright (C) 1996, 1997, 1998, 1999, 2002, 2006 by Bernhard Herzog
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
#include "curvelow.h"
#include "skrect.h"
#include "sktrafo.h"
#include "_sketchmodule.h"



/*
 *	Bezier functions. Should be in a separate module ?
 */

PyObject *
SKAux_DrawBezier(PyObject * self, PyObject * arg)
{

	return NULL;
}

/*
 *	
 */

PyObject *
SKAux_TransformRectangle(PyObject * self, PyObject * args)
{
    SKRectObject * rect;
    PyObject * trafo;
    SKCoord dx, dy;
    int x[4], y[4];

    if (!PyArg_ParseTuple(args, "O!O!", &SKTrafoType, &trafo,
			  &SKRectType, &rect))
	return NULL;

    SKTrafo_TransformXY(trafo, rect->left,  rect->top,    &dx, &dy);
    x[0] = ceil(dx);	y[0] = ceil(dy);
    SKTrafo_TransformXY(trafo, rect->right, rect->top,    &dx, &dy);
    x[1] = ceil(dx);	y[1] = ceil(dy);
    SKTrafo_TransformXY(trafo, rect->right, rect->bottom, &dx, &dy);
    x[2] = ceil(dx);	y[2] = ceil(dy);
    SKTrafo_TransformXY(trafo, rect->left,  rect->bottom, &dx, &dy);
    x[3] = ceil(dx);	y[3] = ceil(dy);

    if ((x[0] == x[3] && y[0] == y[1])
	|| (y[0] == y[3] && x[0] == x[1]))
    {
	int temp;
	if (x[0] > x[2])
	{
	    temp = x[0]; x[0] = x[2]; x[2] = temp;
	}
	if (y[0] > y[2])
	{
	    temp = y[0]; y[0] = y[2]; y[2] = temp;
	}
	return Py_BuildValue("iiii", x[0], y[0], x[2] - x[0], y[2] - y[0]);
    }

    return Py_BuildValue("[(ii)(ii)(ii)(ii)(ii)]",
			 x[0], y[0], x[1], y[1], x[2], y[2], x[3], y[3],
			 x[0], y[0]);
}

/*
 *
 */

PyObject *
SKAux_IdIndex(PyObject * self, PyObject * args)
{
    PyObject * list, *obj, *item;
    int length, i, equal;

    if (!PyArg_ParseTuple(args, "OO", &list, &obj))
	return NULL;

    if (!PySequence_Check(list))
    {
	PyErr_SetString(PyExc_TypeError, "argument must be a sequence");
	return NULL;
    }

    length = PySequence_Length(list);

    for (i = 0; i < length; i++)
    {
	item = PySequence_GetItem(list, i);
	equal = (item == obj);
	Py_DECREF(item);
	if (equal)
	    break;
    }

    if (i < length)
	return PyInt_FromLong(i);

    Py_INCREF(Py_None);
    return Py_None;
}
	    



/*
 *	xlfd_char_range
 */

PyObject *
xlfd_char_range(PyObject * self, PyObject * args)
{
    unsigned char * text;
    int len;
    PyObject * result;
    int idx, count;
    char used[256];
    char * cur;
    char * ranges;

    if (!PyArg_ParseTuple(args, "s#", &text, &len))
	return NULL;

    if (len == 0)
    {
	return PyString_FromString("");
    }

    for (idx = 0; idx < 256; idx++)
	used[idx] = 0;

    for (idx = 0; idx < len; idx++)
	used[(int)(text[idx])] = 1;

    count = 0;
    for (idx = 0; idx < 256; idx++)
	if (used[idx])
	    count++;

    ranges = malloc(4 * count + 1);
    if (!ranges)
	return NULL;

    cur = ranges;
    idx = 0;
    while (idx < 256)
    {
	if (used[idx])
	{
	    int first = idx, last;
	    while (idx < 256 && used[idx])
		idx++;
	    last = idx - 1;
	    if (first == last)
		cur += sprintf(cur, " %d", first);
	    else
		cur += sprintf(cur, " %d_%d", first, last);
	}
	else
	    idx++;
    }
    
    result = PyString_FromString(ranges + 1);
    free(ranges);
    return result;
}


typedef struct {
    PyObject_HEAD
    PyObject * dict;
} SKCacheObject;


static void
SKCache_dealloc(SKCacheObject * self)
{
    Py_DECREF(self->dict);
    PyObject_Del(self);
}

static PyObject *
SKCache_getattr(SKCacheObject * self, char * name)
{
    return PyObject_GetAttrString(self->dict, name);
}

static int
SKCache_length(SKCacheObject * self)
{
    return PyDict_Size(self->dict);
}

static PyObject *
SKCache_subscript(SKCacheObject * self, PyObject *key)
{
    PyObject * result = PyDict_GetItem(self->dict, key);
    if (result)
    {
    	result = PyCObject_AsVoidPtr(result);
	Py_INCREF(result);
    }
    return result;
}

static int
SKCache_ass_sub(SKCacheObject * self, PyObject * v, PyObject * w)
{
    if (w == NULL)
	return PyDict_DelItem(self->dict, v);
    else
    {
	PyObject * obj = PyCObject_FromVoidPtr(w, NULL);
	int result = PyDict_SetItem(self->dict, v, obj);
	Py_DECREF(obj);
	return result;
    }
}

static PyMappingMethods SKCache_as_mapping = {
	(inquiry)SKCache_length,	/*mp_length*/
	(binaryfunc)SKCache_subscript,  /*mp_subscript*/
	(objobjargproc)SKCache_ass_sub, /*mp_ass_subscript*/
};

PyTypeObject SKCacheType = {
	PyObject_HEAD_INIT(NULL)
	0,
	"SKCache",
	sizeof(SKCacheObject),
	0,
	(destructor)SKCache_dealloc,	/*tp_dealloc*/
	(printfunc)0,			/*tp_print*/
	(getattrfunc)SKCache_getattr,	/*tp_getattr*/
	0,				/*tp_setattr*/
	0,				/*tp_compare*/
	0,				/*tp_repr*/
	0,				/*tp_as_number*/
	0,				/*tp_as_sequence*/
	&SKCache_as_mapping,		/*tp_as_mapping*/
	0,				/*tp_hash*/
	0,				/* tp_call */
};

static PyObject *
SKCache_New(void)
{
    SKCacheObject * self = PyObject_New(SKCacheObject, &SKCacheType);
    if (!self)
	return NULL;

    self->dict = PyDict_New();
    if (!self->dict)
    {
	PyObject_Del(self);
	return NULL;
    }

    return (PyObject*)self;
}


PyObject *
SKCache_PyCreate(PyObject * self, PyObject * args)
{
    return SKCache_New();
}

