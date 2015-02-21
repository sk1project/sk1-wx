/*
 *  Copyright (C) 1998, 1999 by Bernhard Herzog.
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


#include "nullfilter.h"

/*
 *	NullEncode filter. Just copy the data to the target.
 *	NullDecode filter. Just copy the data from the source.
 *
 *	These filter are only useful for debugging/testing.
 */

static size_t
write_null(void* clientdata, PyObject * target, const char * buf,
	   size_t length)
{
    return Filter_Write(target, buf, length);
}

PyObject *
Filter_NullEncode(PyObject * self, PyObject * args)
{
    PyObject * target;

    if (!PyArg_ParseTuple(args, "O", &target))
	return NULL;

    return Filter_NewEncoder(target, "NullEncode", 0, write_null, NULL,
			     NULL, NULL);
}

static size_t
read_null(void* clientdata, PyObject * source, char * buf, size_t length)
{
    return Filter_Read(source, buf, length);
}

PyObject *
Filter_NullDecode(PyObject * self, PyObject * args)
{
    PyObject * source;

    if (!PyArg_ParseTuple(args, "O", &source))
	return NULL;

    return Filter_NewDecoder(source, "NullDecode", 0, read_null, NULL,
			     NULL, NULL);
}
