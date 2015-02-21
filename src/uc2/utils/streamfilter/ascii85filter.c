/*
 *  Copyright (C) 2000, 2002 by Bernhard Herzog.
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

/* some small bits were taken from a public domain ASCII85 encoder by
 * Robert Kern
 */

#include <ctype.h>
#include "ascii85filter.h"
#include "subfilefilter.h"

#define FBUFLEN 1024

/*
 *	ASCII85 Encode
 */

typedef struct {
    int	column;
    int maxcolumn;
    unsigned long sum;
    int quartet;
} ASCII85EncodeState;

static const unsigned long eighty_five[5] = {
    1L, 85L, 7225L, 614125L, 52200625L
};


static size_t
write_ASCII85(void* clientdata, PyObject * target, const char * buf,
	      size_t length)
{
    ASCII85EncodeState * state = (ASCII85EncodeState*)clientdata;
    unsigned long sum = state->sum;
    int quartet = state->quartet;
    int column = state->column;
    unsigned char encoded[FBUFLEN];
    unsigned char * dest = (unsigned char *)encoded;
    unsigned char * src = (unsigned char *)buf;
    int i;
    unsigned long res;

    /* at each iteration we write at most 6 bytes into dest. */
    while ((src - (unsigned char*)buf < length)
	   && (dest - encoded) < FBUFLEN - 6)
    {
	sum = (sum << 8) + *src++;
	quartet++;
	if (quartet == 4)
	{
	    if (sum == 0)
	    {
		*dest++ = 'z';
		column++;
	    }
	    else
	    {
		for (i = 4; i >= 0; i--)
		{
		    res = sum / eighty_five[i];
		    *dest++ = res + 33;
		    sum -= res * eighty_five[i];
		}
		sum = 0;
		column += 5;
	    }
	    if (column >= state->maxcolumn)
	    {
		*dest++ = '\n';
		column = 0;
	    }
	    quartet = 0;
	}
    }

    if (Filter_Write(target, encoded, dest - encoded) < 0)
	return 0;

    state->sum = sum;
    state->quartet = quartet;
    state->column = column;

    return src - (unsigned char*)buf;
}

static int
close_ASCII85(void * clientdata, PyObject * target)
{
    ASCII85EncodeState * state = (ASCII85EncodeState*)clientdata;
    unsigned char encoded[10];
    unsigned char * dest = (unsigned char *)encoded;
    int i;
    unsigned long res;
	
    if (state->quartet)
    {
	state->sum <<= 8 * (4 - state->quartet);
	
	for (i = 4; i > (4 - state->quartet); i--)
	{
	    res = state->sum / eighty_five[i];
	    *dest++ = (char)(res + 33);
	    state->sum -= res * eighty_five[i];
	}
	state->column += state->quartet + 1;
	if (state->column >= state->maxcolumn)
	{
	    *dest++ = '\n';
	    state->column = 0;
	}
	if (Filter_Write(target, encoded, dest - encoded) == 0)
	    return EOF;
    }
    if (Filter_Write(target, "~>\n", 3) == 0)
	return EOF;

    return 0;
}

PyObject *
Filter_ASCII85Encode(PyObject * self, PyObject * args)
{
    PyObject * target;
    ASCII85EncodeState * state;
    int maxcolumn = 72;

    if (!PyArg_ParseTuple(args, "O|i", &target, &maxcolumn))
	return NULL;

    state = malloc(sizeof(ASCII85EncodeState));
    if (!state)
	return PyErr_NoMemory();
    state->maxcolumn = maxcolumn - (maxcolumn & 1);
    state->column = 0;
    state->sum = 0;
    state->quartet = 0;

    return Filter_NewEncoder(target, "ASCII85Encode", 0, write_ASCII85,
			     close_ASCII85, free, state);
}



/*
 *	ASCII85 Decode
 */

typedef struct {
    FilterObject * subfiledecode;
    int quintet;
    unsigned long sum;
    int eod;
} ASCII85DecodeState;


static size_t
read_ASCII85(void * clientdata, PyObject * source, char * buf, size_t length)
{
    unsigned char *dest = (unsigned char *)buf;
    ASCII85DecodeState * state = (ASCII85DecodeState*)clientdata;
    int quintet = state->quintet;
    unsigned long sum = state->sum;
    int byte;
    FilterObject * subfile = state->subfiledecode;

    if (state->eod)
	return 0;

    /* in ech iteration, at most 4 bytes are written to buf */
    while (dest - (unsigned char *)buf < length - 4)
    {
	byte = Filter_GETC(subfile);
	if (byte >= '!' && byte <= 'u')
	{
	    sum = sum * 85 + ((unsigned long)byte - '!');
	    quintet++;
	    if (quintet == 5)
	    {
		*dest++ = sum >> 24;
		*dest++ = (sum >> 16) & 0xFF;
		*dest++ = (sum >> 8) & 0xFF;
		*dest++ = sum & 0xFF;
		quintet = 0;
		sum = 0;
	    }
	}
	else if (byte == 'z')
	{
	    if (quintet)
	    {
		PyErr_Format(PyExc_ValueError,
			     "ASCII85Decode: z in wrong position");
		return 0;
	    }
	    *dest++ = 0;
	    *dest++ = 0;
	    *dest++ = 0;
	    *dest++ = 0;
	}
	else if (byte == EOF)
	{
	    if (quintet == 1)
	    {
		PyErr_Format(PyExc_ValueError,
			     "ASCII85Decode: only 1 byte in last quintet");
		return 0;
	    }
	    if (quintet)
	    {
		int i;
		for (i = 0; i < 5 - quintet; i++)
		    sum *= 85;
		if (quintet > 1)
		    sum += (0xFFFFFF >> ((quintet - 2) * 8));
		for (i = 0; i < quintet - 1; i++)
		{
		    *dest++ = (sum >> (24 - 8 * i)) & 0xFF;
		}
		quintet = 0;
	    }
	    state->eod = 1;
	    break;
	}
	else if (!isspace(byte))
	{
	    PyErr_Format(PyExc_ValueError,
			 "ASCII85Decode: invalid character %x (hex)", byte);
	    return 0;
	}
    }

    state->sum = sum;
    state->quintet = quintet;
    return dest - (unsigned char*)buf;
}

static PyObject *
delimiter_string_object = NULL;

PyObject *
Filter_ASCII85Decode(PyObject * self, PyObject * args)
{
    PyObject *source, *subfiledecode, *tuple;
    ASCII85DecodeState * state;
    
    if (!PyArg_ParseTuple(args, "O", &source))
	return NULL;

    if (!delimiter_string_object)
    {
	delimiter_string_object = PyString_FromString("~>");
	if (!delimiter_string_object)
	    return NULL;
    }

    tuple = Py_BuildValue("OO", source, delimiter_string_object);
    if (!tuple)
	return NULL;
    subfiledecode = Filter_SubFileDecode(NULL, tuple);
    Py_DECREF(tuple);
    if (!subfiledecode)
	return NULL;
    
    state = malloc(sizeof(ASCII85DecodeState));
    if (!state)
	return PyErr_NoMemory();
    state->subfiledecode = (FilterObject*)subfiledecode;
    state->eod = 0;
    state->quintet = 0;
    state->sum = 0;

    return Filter_NewDecoder(source, "ASCII85Decode", 0, read_ASCII85, NULL,
			     free, state);
}

