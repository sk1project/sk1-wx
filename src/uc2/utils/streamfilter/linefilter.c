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


#include "linefilter.h"


#define FBUFLEN 2048


static size_t
read_nl(void * clientdata, PyObject * source, char * buf, size_t length)
{
    size_t i, maxlen, bytesread;
    char encoded[FBUFLEN + 1];
    char * src, *dest = buf;
    int converted_last = *((int*)clientdata);

    if (length > FBUFLEN)
	maxlen = FBUFLEN;
    else
	maxlen = length;
    
    bytesread = Filter_Read(source, encoded, maxlen);
    if (bytesread == 0)
	return 0;

    if (converted_last && encoded[0] == '\n')
    {
	src = encoded + 1;
	bytesread -= 1;
    }
    else
	src = encoded;
    
    for (i = 0; i < bytesread; i++)
    {
	if ((*dest++ = *src++) == '\r')
	{
	    dest[-1] = '\n';
	    if (i + 1 >= bytesread)
		break;
	    if (*src == '\n')
	    {
		src += 1;
		i += 1;
		continue;
	    }
	}
    }

    *((int*)clientdata) = (src[-1] == '\r');
    return dest - buf;
}

PyObject *
Filter_LineDecode(PyObject * self, PyObject * args)
{
    PyObject * source;
    int * data;
    
    if (!PyArg_ParseTuple(args, "O", &source))
	return NULL;

    data = malloc(sizeof(int));
    if (!data)
	return PyErr_NoMemory();
    *data = 0;

    return Filter_NewDecoder(source, "LineDecode", 0, read_nl, NULL, free,
			     data);
}

