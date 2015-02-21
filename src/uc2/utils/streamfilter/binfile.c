/*
 *  Copyright (C) 1998, 1999, 2001, 2006 by Bernhard Herzog.
 *
 *			All Rights Reserved
 *
 *  Permission to use, copy, modify, and distribute this software and
 *  its documentation for any purpose and without fee is hereby granted,
 *  provided that the above copyright notice appear in all copies and
 *  that both that copyright notice and this permission notice appear in
 *  supporting documentation, and that the name of the author not be
 *  used in advertising or publicity pertaining to distribution of the
 *  software without specific, written prior permission.
 *
 *  THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE,
 *  INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, IN
 *  NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, INDIRECT OR
 *  CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
 *  OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
 *  NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION
 *  WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
 */

#include <math.h>
#include <Python.h>
#include <structmember.h>
#include "filterobj.h"
#include "binfile.h"

/* some code here taken from structmodule.c in Python's Modules directory */

static PyObject * BinFile_FromStream(PyObject * string,
				     int byte_order, int int_size);


/* helper functions for floats */

static PyObject *
unpack_float(const char *p,  /* Where the high order byte is */
	     int incr) /* 1 for big-endian; -1 for little-endian */
{
	int s;
	int e;
	long f;
	double x;

	/* First byte */
	s = (*p>>7) & 1;
	e = (*p & 0x7F) << 1;
	p += incr;

	/* Second byte */
	e |= (*p>>7) & 1;
	f = (*p & 0x7F) << 16;
	p += incr;

	/* Third byte */
	f |= (*p & 0xFF) << 8;
	p += incr;

	/* Fourth byte */
	f |= *p & 0xFF;

	x = (double)f / 8388608.0;

	/* XXX This sadly ignores Inf/NaN issues */
	if (e == 0)
		e = -126;
	else {
		x += 1.0;
		e -= 127;
	}
	x = ldexp(x, e);

	if (s)
		x = -x;

	return PyFloat_FromDouble(x);
}

static PyObject *
unpack_double(const char *p,  /* Where the high order byte is */
	      int incr) /* 1 for big-endian; -1 for little-endian */
{
	int s;
	int e;
	long fhi, flo;
	double x;

	/* First byte */
	s = (*p>>7) & 1;
	e = (*p & 0x7F) << 4;
	p += incr;

	/* Second byte */
	e |= (*p>>4) & 0xF;
	fhi = (*p & 0xF) << 24;
	p += incr;

	/* Third byte */
	fhi |= (*p & 0xFF) << 16;
	p += incr;

	/* Fourth byte */
	fhi |= (*p & 0xFF) << 8;
	p += incr;

	/* Fifth byte */
	fhi |= *p & 0xFF;
	p += incr;

	/* Sixth byte */
	flo = (*p & 0xFF) << 16;
	p += incr;

	/* Seventh byte */
	flo |= (*p & 0xFF) << 8;
	p += incr;

	/* Eighth byte */
	flo |= *p & 0xFF;
	p += incr;

	x = (double)fhi + (double)flo / 16777216.0; /* 2**24 */
	x /= 268435456.0; /* 2**28 */

	/* XXX This sadly ignores Inf/NaN */
	if (e == 0)
		e = -1022;
	else {
		x += 1.0;
		e -= 1023;
	}
	x = ldexp(x, e);

	if (s)
		x = -x;

	return PyFloat_FromDouble(x);
}

/* converter funcitons */
typedef PyObject* (*UnpackFunction)(const char *);
typedef PyObject* (*UnpackFunctionInt)(const char *, int size);

typedef struct {
    UnpackFunction unpack_char;
    UnpackFunction unpack_float;
    UnpackFunction unpack_double;
    UnpackFunctionInt unpack_signed;
    UnpackFunctionInt unpack_unsigned;
} UnpackFunctionTable;
    
static PyObject *
nu_char(const char *p)
{
	return PyString_FromStringAndSize(p, 1);
}

static PyObject *
bu_int(const char *p, int size)
{
	long x = 0;
	int i = size;
	do {
		x = (x<<8) | (*p++ & 0xFF);
	} while (--i > 0);
	i = 8*(sizeof(long) - size);
	if (i) {
		x <<= i;
		x >>= i;
	}
	return PyInt_FromLong(x);
}

static PyObject *
bu_uint(const char *p, int size)
{
	unsigned long x = 0;
	int i = size;
	do {
		x = (x<<8) | (*p++ & 0xFF);
	} while (--i > 0);
	if (size >= 4)
		return PyLong_FromUnsignedLong(x);
	else
		return PyInt_FromLong((long)x);
}

static PyObject *
bu_float(const char *p)
{
	return unpack_float(p, 1);
}

static PyObject *
bu_double(const char *p)
{
	return unpack_double(p, 1);
}


UnpackFunctionTable bigendian_table =
{
    nu_char,
    bu_float,
    bu_double,
    bu_int,
    bu_uint
};


static PyObject *
lu_int(const char *p, int size)
{
	long x = 0;
	int i = size;
	do {
		x = (x<<8) | (p[--i] & 0xFF);
	} while (i > 0);
	i = 8*(sizeof(long) - size);
	if (i) {
		x <<= i;
		x >>= i;
	}
	return PyInt_FromLong(x);
}

static PyObject *
lu_uint(const char *p, int size)
{
	unsigned long x = 0;
	int i = size;
	do {
		x = (x<<8) | (p[--i] & 0xFF);
	} while (i > 0);
	if (size >= 4)
		return PyLong_FromUnsignedLong(x);
	else
		return PyInt_FromLong((long)x);
}

static PyObject *
lu_float(const char *p)
{
	return unpack_float(p+3, -1);
}

static PyObject *
lu_double(const char *p)
{
	return unpack_double(p+7, -1);
}

UnpackFunctionTable littleendian_table =
{
    nu_char,
    lu_float,
    lu_double,
    lu_int,
    lu_uint
};




typedef struct {
    PyObject_HEAD
    PyObject *  stream;
    int		byte_order;
    int		int_size;
    int		string_pos;
} BinaryInputObject;

enum ByteOrder { LittleEndian, BigEndian };

static void
binfile_dealloc(BinaryInputObject * self)
{
    Py_DECREF(self->stream);
    PyObject_Del(self);
}

static PyObject *
binfile_repr(FilterObject * self)
{
    char buf[1000];
    PyObject * streamrepr;

    streamrepr = PyObject_Repr(self->stream);
    if (!streamrepr)
	return NULL;

    sprintf(buf, "<BinaryInput reading from %.500s>",
	    PyString_AsString(streamrepr));
    Py_DECREF(streamrepr);
    return PyString_FromString(buf);
}



static int
calcsize(BinaryInputObject * self, const char * format)
{
    int size = 0;
    const char * p;

    p = format;
    while (*p)
    {
	switch (*p)
	{
	case 'b': case 'B': case 'c': case 'x':
	    size += 1;
	    break;

	case 'h': case 'H':
	    size += 2;
	    break;

	case 'l': case 'L': case 'f':
	    size += 4;
	    break;
	    
	case 'd':
	    size += 8;
	    break;

	case 'i': case 'I':
	    size += self->int_size;
	    break;

	default:
	    break;
	}
	p += 1;
    }

    return size;
}


static char * read_data(BinaryInputObject * self, int size)
{
    char * result;
    
    if (PyString_Check(self->stream))
    {
	int length = PyString_Size(self->stream);
	if (self->string_pos + size <= length)
	{
	    result = PyString_AsString(self->stream) + self->string_pos;
	    self->string_pos += size;
	}
	else
	{
	    PyErr_Format(PyExc_ValueError, "Only %d bytes left, need %d",
			 length - self->string_pos, size);
	    result = NULL;
	}
    }
    else
    {
	PyErr_SetString(PyExc_TypeError,
			"Only strings as data source supported");
	result = NULL;
    }
    
    return result;
}
	    

static PyObject *
binfile_readstruct(BinaryInputObject * self, PyObject * args)
{
    UnpackFunctionTable * table;
    int size;
    PyObject * list = NULL, *v = NULL;
    const char * format;
    const char * p;
    char * buffer;
    char * data;

    if (!PyArg_ParseTuple(args, "s", &format))
	return NULL;
    
    if (self->byte_order == LittleEndian)
	table = &littleendian_table;
    else
	table = &bigendian_table;

    size = calcsize(self, format);
    buffer = read_data(self, size);
    if (!buffer)
	return NULL;

    list = PyList_New(0);
    if (!list)
	return NULL;

    data = buffer;
    p = format;
    while (*p)
    {
	v = NULL;
	switch (*p)
	{
	case 'c':
	    v = table->unpack_char(data);
	    data += 1;
	    break;
	    
	case 'b':
	    v = table->unpack_signed(data, 1);
	    data += 1;
	    break;

	case 'B':
	    v = table->unpack_unsigned(data, 1);
	    data += 1;
	    break;

	case 'h': 
	    v = table->unpack_signed(data, 2);
	    data += 2;
	    break;

	case 'H':
	    v = table->unpack_unsigned(data, 2);
	    data += 2;
	    break;

	case 'l':
	    v = table->unpack_signed(data, 4);
	    data += 4;
	    break;

	case 'L':
	    v = table->unpack_unsigned(data, 4);
	    data += 4;
	    break;

	case 'f':
	    v = table->unpack_float(data);
	    data += 4;
	    break;

	case 'd':
	    v = table->unpack_double(data);
	    data += 8;
	    break;

	case 'i':
	    v = table->unpack_signed(data, self->int_size);
	    data += self->int_size;
	    break;

	case 'I':
	    v = table->unpack_unsigned(data, self->int_size);
	    data += self->int_size;
	    break;

	case 'x':
	    data += 1;

	default:
	    continue;
	}
	p += 1;

	if (!v)
	    goto error;
	
	if (PyList_Append(list, v) < 0)
	    goto error;
	Py_DECREF(v);
    }

    v = PyList_AsTuple(list);
    Py_DECREF(list);
    return v;

 error:
    Py_XDECREF(v);
    Py_XDECREF(list);
    return NULL;
}

static PyObject *
binfile_subfile(BinaryInputObject * self, PyObject * args)
{
    int length;
    int left;
    PyObject * string, *binfile;

    if (!PyArg_ParseTuple(args, "i", &length))
	return NULL;

    left = PyString_Size(self->stream) - self->string_pos;
    if (left < length)
    {
	PyErr_Format(PyExc_ValueError, "Only %d bytes left, need %d", left,
		     length);
	return NULL;
    }
    string = PyString_FromStringAndSize(PyString_AsString(self->stream)
					+ self->string_pos, length);
    if (!string)
	return NULL;

    binfile = BinFile_FromStream(string, self->byte_order, self->int_size);
    Py_DECREF(string);
    if (binfile)
	self->string_pos += length;
    return binfile;
}

static PyObject *
binfile_read(BinaryInputObject * self, PyObject * args)
{
    int length;
    int left;
    PyObject * string;

    if (!PyArg_ParseTuple(args, "i", &length))
	return NULL;

    left = PyString_Size(self->stream) - self->string_pos;
    if (left < length)
    {
	PyErr_Format(PyExc_ValueError, "Only %d bytes left, need %d", left,
		     length);
	return NULL;
    }
    string = PyString_FromStringAndSize(PyString_AsString(self->stream)
					+ self->string_pos, length);
    if (string)
	self->string_pos += length;
    return string;
}

static PyObject *
binfile_seek(BinaryInputObject * self, PyObject * args)
{
    int pos;

    if (!PyArg_ParseTuple(args, "i", &pos))
	return NULL;

    if (pos >= 0 && pos <= PyString_Size(self->stream))
    {
	self->string_pos = pos;
    }
    else
    {
	PyErr_Format(PyExc_ValueError, "Can't seek to %d", pos);
	return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
binfile_tell(BinaryInputObject * self, PyObject * args)
{
    return PyInt_FromLong(self->string_pos);
}


#define OFF(x) offsetof(BinaryInputObject, x)
static struct memberlist binfile_memberlist[] = {
    {"stream",		T_OBJECT,	OFF(stream),	RO},
    {NULL}
};

static struct PyMethodDef binfile_methods[] = {
    {"read_struct",	(PyCFunction)binfile_readstruct,	1},
    {"read",		(PyCFunction)binfile_read,		1},
    {"subfile",		(PyCFunction)binfile_subfile,		1},
    {"seek",		(PyCFunction)binfile_seek,		1},
    {"tell",		(PyCFunction)binfile_tell,		1},
    {NULL,	NULL}
};

static PyObject *
binfile_getattr(PyObject * self, char * name)
{
    PyObject * result;

    result = Py_FindMethod(binfile_methods, self, name);
    if (result != NULL)
	return result;
    PyErr_Clear();

    return PyMember_Get((char *)self, binfile_memberlist, name);
}



static int
binfile_setattr(PyObject * self, char * name, PyObject * v)
{
    if (v == NULL) {
	PyErr_SetString(PyExc_AttributeError,
			"can't delete object attributes");
	return -1;
    }
    return PyMember_Set((char *)self, binfile_memberlist, name, v);
}

staticforward PyTypeObject BinaryInputType;

statichere PyTypeObject BinaryInputType = {
	PyObject_HEAD_INIT(NULL)
	0,
	"binaryinput",
	sizeof(BinaryInputObject),
	0,
	(destructor)binfile_dealloc,	/*tp_dealloc*/
	(printfunc)0,			/*tp_print*/
	binfile_getattr,		/*tp_getattr*/
	binfile_setattr,		/*tp_setattr*/
	(cmpfunc)0,			/*tp_compare*/
	(reprfunc)binfile_repr,		/*tp_repr*/
	0,				/*tp_as_number*/
	0,				/*tp_as_sequence*/
	0,				/*tp_as_mapping*/
	0,				/*tp_hash*/
};

static PyObject *
BinFile_FromStream(PyObject * stream, int byte_order, int int_size)
{
    BinaryInputObject * binfile;

    if (byte_order != LittleEndian && byte_order != BigEndian)
    {
	PyErr_Format(PyExc_ValueError, "Invalid byte order %d", byte_order);
	return NULL;
    }
    if (int_size != 2 && int_size != 4)
    {
	PyErr_Format(PyExc_ValueError, "Invalid int size %d, must be 2 or 4",
		     int_size);
	return NULL;
    }

    if (!PyString_Check(stream))
    {
	PyErr_SetString(PyExc_TypeError, "Only strings supported as input");
	return NULL;
    }

    BinaryInputType.ob_type = &PyType_Type;

    binfile = PyObject_New(BinaryInputObject, &BinaryInputType);
    if (!binfile)
	return NULL;

    binfile->stream = stream;
    Py_INCREF(binfile->stream);
    binfile->int_size = int_size;
    binfile->byte_order = byte_order;
    binfile->string_pos = 0;

    return (PyObject*)binfile;
}    

PyObject *
BinFile_New(PyObject * self, PyObject * args)
{
    PyObject * stream;
    int byte_order, int_size;

    if (!PyArg_ParseTuple(args, "Oii", &stream, &byte_order, &int_size))
	return NULL;
    return BinFile_FromStream(stream, byte_order, int_size);
}


