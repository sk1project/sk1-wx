/*
 *  Copyright (C) 1998, 1999, 2006 by Bernhard Herzog.
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

#include "subfilefilter.h"

typedef struct {
    char * delim;
    int chars_matched;
    int length;
    PyObject * delim_object;
    int shift[1];
} SubFileDecodeState;

static size_t
read_subfile(void* clientdata, PyObject * source, char * buf, size_t length)
{
    char * data = buf;
    size_t bytesread = 0, datalen = 0;
    int *shift;
    SubFileDecodeState *state = (SubFileDecodeState*)clientdata;

    if (!state->delim)
	/* eof data */
	return 0;

    if (state->chars_matched)
    {
	memcpy(data, state->delim, state->chars_matched);
	datalen = state->chars_matched;
    }

    while (datalen < state->length)
    {
	bytesread = Filter_ReadToChar(source, buf + datalen, length - datalen,
				      state->delim[state->length - 1]);
	if (bytesread == 0)
	{
	    if (PyErr_Occurred())
		return 0;
	    return datalen;
	}
	datalen += bytesread;
    }

    /* now, if the delimiter is contained in the the first datalen bytes
     * of the buffer, it is located at the end.
     */

    data = buf + datalen;
    if (!memcmp(data - state->length, state->delim, state->length))
    {
	state->delim = NULL;
	return datalen - state->length;
    }

    for (shift = state->shift; *shift > 0; shift++)
    {
	if (!memcmp(data - *shift, state->delim, *shift))
	{
	    state->chars_matched = *shift;
	    return datalen - *shift;
	}
    }
    state->chars_matched = 0;
    return datalen;
}


static void
dealloc_subfile(void * clientdata)
{
    SubFileDecodeState * state = (SubFileDecodeState*)clientdata;
    Py_DECREF(state->delim_object);
    PyMem_Free(state);
}

static void
init_shift(SubFileDecodeState * state)
{
    int i, j;
    int lastchar = state->delim[state->length - 1];

    for (i = 0, j = 0; i < state->length; i++)
	if (state->delim[i] == lastchar)
	    state->shift[j++] = i + 1;
    state->shift[j - 1] = -1;
}

PyObject *
Filter_SubFileDecode(PyObject * self, PyObject * args)
{
    PyObject * target;
    PyObject * delim_object;
    SubFileDecodeState * state;
    int length;

    if (!PyArg_ParseTuple(args, "OS", &target, &delim_object))
	return NULL;

    length = PyString_Size(delim_object);
    if (length < 1)
	return PyErr_Format(PyExc_ValueError, "empty delimiter");
    state = PyMem_Malloc(sizeof (SubFileDecodeState) + length * sizeof(int));
    if (!state)
	return PyErr_NoMemory();
    state->delim_object = delim_object;
    Py_INCREF(state->delim_object);
    state->delim = PyString_AsString(delim_object);
    state->chars_matched = 0;
    state->length = length;
    init_shift(state);
    
    return Filter_NewDecoder(target, "SubFileDecode", 0, read_subfile,
			     NULL, dealloc_subfile, state);
}

