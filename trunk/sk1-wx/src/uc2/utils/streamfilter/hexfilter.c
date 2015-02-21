/*
 *  Copyright (C) 1998, 1999, 2002 by Bernhard Herzog.
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

#include <ctype.h>
#include "hexfilter.h"

#define FBUFLEN 1024

/*
 *	Hex Encode
 */

typedef struct {
    int	column;
    int maxcolumn;
} HexEncodeState;

static size_t
write_hex(void* clientdata, PyObject * target, const char * buf, size_t length)
{
    static char * hexdigits = "0123456789abcdef";
    HexEncodeState * state = (HexEncodeState*)clientdata;
    int i, todo = length, chunk, maxbinary;
    char encoded[FBUFLEN];
    char * dest;

    /* Estimate the number of unencoded bytes that fit into the buffer
     * in encoded form. Each encoded line will have state->maxcolumn + 1
     * characters which represent state->maxcolumn / 2 binary bytes.
     */
    /* assume that state->maxcolumn is even */
    maxbinary = (FBUFLEN / (state->maxcolumn + 1)) * (state->maxcolumn / 2);
    if (maxbinary == 0)
	/* for small FBUFLEN or large maxcolumn */
	maxbinary = FBUFLEN / 3;

    if (todo > maxbinary)
	chunk = maxbinary;
    else
	chunk = todo;
	
    for (i = 0, dest = encoded; i < chunk; i++, buf++)
    {
	*dest++ = hexdigits[(int)((*buf & 0xF0) >> 4)];
	*dest++ = hexdigits[(int)(*buf & 0x0F)];
	state->column += 2;
	if (state->column >= state->maxcolumn)
	{
	    *dest++ = '\n';
	    state->column = 0;
	}
    }
    
    if (Filter_Write(target, encoded, dest - encoded) < 0)
	return 0;

    return chunk;
}

static int
close_hex(void * clientdata, PyObject * target)
{
    if (((HexEncodeState*)clientdata)->column > 0)
    {
	if (Filter_Write(target, "\n", 1) == 0)
	    return EOF;
    }
    return 0;
}

PyObject *
Filter_HexEncode(PyObject * self, PyObject * args)
{
    PyObject * target;
    HexEncodeState * state;
    int maxcolumn = 72;

    if (!PyArg_ParseTuple(args, "O|i", &target, &maxcolumn))
	return NULL;

    state = malloc(sizeof(HexEncodeState));
    if (!state)
	return PyErr_NoMemory();
    state->maxcolumn = maxcolumn - (maxcolumn & 1);
    state->column = 0;

    return Filter_NewEncoder(target, "HexEncode", 0, write_hex, close_hex,
			     free, state);
}



/*
 *	Hex Decode
 */


typedef struct {
    int last_digit;
} HexDecodeState;


static size_t
read_hex(void * clientdata, PyObject * source, char * buf, size_t length)
{
    size_t i, srclen, bytesread;
    char encoded[FBUFLEN];
    char *dest = buf;
    HexDecodeState * state = (HexDecodeState*)clientdata;
    int last_digit = state->last_digit;

    if (2 * length > FBUFLEN)
	srclen = FBUFLEN;
    else
	srclen = 2 * length;
    
    bytesread = Filter_Read(source, encoded, srclen);
    if (bytesread == 0)
    {
	/* end of file or data */
	if (state->last_digit >= 0)
	{
	    /* assume a trailing 0 (this is the PostScript filter behaviour */
	    *((unsigned char*)dest) = state->last_digit * 16;
	    return 1;
	}
	return 0;
    }

    for (i = 0; i < bytesread; i++)
    {
	if (isxdigit(encoded[i]))
	{
	    int digit = ((unsigned char*)encoded)[i];
	    if ('0' <= digit && digit <= '9')
	    {
		digit = digit - '0';
	    }
	    else if ('a' <= digit && digit <= 'f')
	    {
		digit = digit - 'a' + 10;
	    }
	    else if ('A' <= digit && digit <= 'F')
	    {
		digit = digit - 'A' + 10;
	    }
	    if (last_digit >= 0)
	    {
		*((unsigned char*)dest) = last_digit * 16 + digit;
		last_digit = -1;
		dest += 1;
	    }
	    else
	    {
		last_digit = digit;
	    }
	}
	/* else maybe raise error if not whitespace */
    }

    state->last_digit = last_digit;

    return dest - buf;
}


PyObject *
Filter_HexDecode(PyObject * self, PyObject * args)
{
    PyObject * source;
    HexDecodeState * state;
    
    if (!PyArg_ParseTuple(args, "O", &source))
	return NULL;

    state = malloc(sizeof(HexDecodeState));
    if (!state)
	return PyErr_NoMemory();
    state->last_digit = -1;

    return Filter_NewDecoder(source, "HexDecode", 0, read_hex, NULL, free,
			     state);
}

