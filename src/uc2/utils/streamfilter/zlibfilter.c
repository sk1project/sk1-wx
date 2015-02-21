/*
 *  Copyright (C) 1998, 1999, 2000, 2006 by Bernhard Herzog.
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

#include <zlib.h>
#include "zlibfilter.h"

#define INBUFSIZE 1024

typedef struct {
    char * buffer;
    size_t buffer_length;
    int eod_reached;
    z_stream zstr;
} FlateDecodeState;

static size_t
read_zlib(void* clientdata, PyObject * source, char * buf, size_t length)
{
    size_t bytesread = 0;
    int result;
    FlateDecodeState *state = (FlateDecodeState*)clientdata;

    if (state->eod_reached)
	return 0;

    state->zstr.next_out = buf;
    state->zstr.avail_out = length;
    do
    {
	if (state->zstr.avail_in == 0)
	{
	    state->zstr.next_in = state->buffer;	    
	    bytesread = Filter_Read(source, state->buffer,
				    state->buffer_length);
	    if (bytesread == 0)
	    {
		if (PyErr_Occurred())
		    return 0;
	    }
	    state->zstr.avail_in = bytesread;
	}
	result = inflate(&state->zstr, Z_SYNC_FLUSH);
	if (result == Z_STREAM_END)
	{
	    state->eod_reached = 1;
	}
	else if (result != Z_OK)
	{
	    if (state->zstr.msg == Z_NULL)
		PyErr_Format(PyExc_IOError, "FlateDecode: Error %i", result); 
	    else
		PyErr_Format(PyExc_IOError, "FlateDecode: Error %i: %.200s",
			     result, state->zstr.msg);
	    return 0;
	}
    } while (state->zstr.avail_out == length && !state->eod_reached);
    return length - state->zstr.avail_out;
}


static void
dealloc_zlib(void * clientdata)
{
    FlateDecodeState * state = (FlateDecodeState*)clientdata;
    inflateEnd(&state->zstr); /* XXX error handling */
    PyMem_Free(state->buffer);
    PyMem_Free(state);
}


PyObject *
Filter_FlateDecode(PyObject * self, PyObject * args)
{
    PyObject * target;
    FlateDecodeState * state;
    int result;

    if (!PyArg_ParseTuple(args, "O", &target))
	return NULL;

    state = PyMem_Malloc(sizeof(FlateDecodeState));
    if (!state)
	return PyErr_NoMemory();
    state->buffer = PyMem_Malloc(INBUFSIZE);
    if (!state->buffer)
    {
	PyMem_Free(state);
	return PyErr_NoMemory();
    }

    state->buffer_length = INBUFSIZE;
    state->zstr.zalloc = NULL;
    state->zstr.zfree = NULL;
    state->zstr.opaque = NULL;
    state->zstr.next_in = state->buffer;
    state->zstr.avail_in = 0;
    state->eod_reached = 0;

    result = inflateInit(&state->zstr);
    if (result != Z_OK)
    {
	if (result == Z_MEM_ERROR)
	{
	    PyErr_SetString(PyExc_MemoryError,
			    "FlateDecode: No memory for z_stream");
	}
	else 
	{
	    if (state->zstr.msg == Z_NULL)
		PyErr_Format(PyExc_IOError, "FlateDecode: Zlib Error %i",
			     result); 
	    else
		PyErr_Format(PyExc_IOError,
			     "FlateDecode: Zlib Error %i: %.200s",
			     result, state->zstr.msg);  
	}
	PyMem_Free(state->buffer);
	PyMem_Free(state);
	return NULL;
    }

    return Filter_NewDecoder(target, "FlateDecode", 0, read_zlib,
			     NULL, dealloc_zlib, state);
}

