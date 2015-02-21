/*
  Copyright (C) 1998, 1999 by Bernhard Herzog.

			All Rights Reserved

  Permission to use, copy, modify, and distribute this software and its
  documentation for any purpose and without fee is hereby granted,
  provided that the above copyright notice appear in all copies and that
  both that copyright notice and this permission notice appear in
  supporting documentation, and that the name of the author not be used
  in advertising or publicity pertaining to distribution of the software
  without specific, written prior permission.

  THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE,
  INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, IN NO
  EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, INDIRECT OR
  CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF
  USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
  OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
  PERFORMANCE OF THIS SOFTWARE.

parts of this file are based on code from the python interpreter, which
comes with the following license:

Copyright 1991, 1992, 1993, 1994 by Stichting Mathematisch Centrum,
Amsterdam, The Netherlands.

                        All Rights Reserved

Permission to use, copy, modify, and distribute this software and its
documentation for any purpose and without fee is hereby granted,
provided that the above copyright notice appear in all copies and that
both that copyright notice and this permission notice appear in
supporting documentation, and that the names of Stichting Mathematisch
Centrum or CWI or Corporation for National Research Initiatives or
CNRI not be used in advertising or publicity pertaining to
distribution of the software without specific, written prior
permission.


*/


#include "base64filter.h"

#define FBUFLEN 1024

/* some code here taken from binascii.c in Python's Modules directory */

static char table_a2b_base64[] = {
	-1,-1,-1,-1, -1,-1,-1,-1, -1,-1,-1,-1, -1,-1,-1,-1,
	-1,-1,-1,-1, -1,-1,-1,-1, -1,-1,-1,-1, -1,-1,-1,-1,
	-1,-1,-1,-1, -1,-1,-1,-1, -1,-1,-1,62, -1,-1,-1,63,
	52,53,54,55, 56,57,58,59, 60,61,-1,-1, -1, 0,-1,-1, /* Note PAD->0 */
	-1, 0, 1, 2,  3, 4, 5, 6,  7, 8, 9,10, 11,12,13,14,
	15,16,17,18, 19,20,21,22, 23,24,25,-1, -1,-1,-1,-1,
	-1,26,27,28, 29,30,31,32, 33,34,35,36, 37,38,39,40,
	41,42,43,44, 45,46,47,48, 49,50,51,-1, -1,-1,-1,-1
};

#define BASE64_PAD '='


typedef struct {
    int leftbits;
    unsigned int leftchar;
} Base64DecodeState;


static size_t
read_base64(void* clientdata, PyObject * source, char * buf, size_t length)
{
    size_t bytes_read;
    unsigned char encoded[FBUFLEN];
    unsigned char * ascii_data;
    unsigned char * bin_data;
    int ascii_len, bin_len = 0;
    Base64DecodeState * state = (Base64DecodeState*)clientdata;
    int leftbits = state->leftbits;
    unsigned int leftchar = state->leftchar;
    unsigned char this_ch;
    int npad;

    bin_data = (unsigned char*)buf;

    while (!bin_len)
    {
	ascii_len = (length / 3) * 4; /* lower bound */
	if (ascii_len > FBUFLEN)
	    ascii_len = FBUFLEN;
	ascii_data = encoded;
	npad = 0;
	bytes_read = Filter_Read(source, (char*)ascii_data, ascii_len);
	if (bytes_read == 0)
	{
	    if (!PyErr_Occurred())
	    {
		if (leftbits != 0)
		    PyErr_Format(PyExc_ValueError,
				 "Base64Decode: premature end of data");
	    }
	    return 0;
	}

	ascii_len = bytes_read;
	for(; ascii_len > 0 ; ascii_len--, ascii_data++)
	{
	    /* Skip some punctuation */
	    this_ch = (*ascii_data & 0x7f);
	    if (this_ch == '\r' || this_ch == '\n' || this_ch == ' ')
		continue;
		
	    if (this_ch == BASE64_PAD)
		npad++;
	    this_ch = table_a2b_base64[(*ascii_data) & 0x7f];
	    if (this_ch == (unsigned char) -1)
		continue;
	    /*
	    ** Shift it in on the low end, and see if there's
	    ** a byte ready for output.
	    */
	    leftchar = (leftchar << 6) | (this_ch);
	    leftbits += 6;
	    if (leftbits >= 8)
	    {
		leftbits -= 8;
		*bin_data++ = (leftchar >> leftbits) & 0xff;
		leftchar &= ((1 << leftbits) - 1);
		bin_len++;
	    }
	}
	bin_len -= npad;
    }

    state->leftbits = leftbits;
    state->leftchar = leftchar;

    return bin_len;
}


PyObject *
Filter_Base64Decode(PyObject * self, PyObject * args)
{
    PyObject * source;
    Base64DecodeState * state;

    if (!PyArg_ParseTuple(args, "O", &source))
	return NULL;

    state = malloc(sizeof (Base64DecodeState));
    if (!state)
	return PyErr_NoMemory();
    state->leftbits = 0;
    state->leftchar = 0;

    return Filter_NewDecoder(source, "Base64Decode", 0, read_base64, NULL,
			     free, state);
}

#define BASE64_MAXASCII 76	/* Max chunk size (76 char line) */

static unsigned char table_b2a_base64[] =
"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

typedef struct {
    int leftbits;
    unsigned int leftchar;
    int column;
} Base64EncodeState;

static size_t
write_base64(void * clientdata, PyObject * target, const char * buf,
	     size_t length)
{
    Base64EncodeState * state = (Base64EncodeState*)clientdata;
    unsigned char encoded[FBUFLEN];
    unsigned char *ascii_data = encoded;
    const unsigned char *bin_data = (const unsigned char*)buf;
    int leftbits = state->leftbits;
    unsigned char this_ch;
    unsigned int leftchar = state->leftchar;
    int bin_len = ((FBUFLEN / 4) * 3);
    size_t ascii_left;

    if (bin_len > length)
	bin_len = length;

    /* first, fill the ascii buffer and don't care about max. line length */
    for( ; bin_len > 0 ; bin_len--, bin_data++ )
    {
	/* Shift the data into our buffer */
	leftchar = (leftchar << 8) | *bin_data;
	leftbits += 8;

	/* See if there are 6-bit groups ready */
	while ( leftbits >= 6 )
	{
	    this_ch = (leftchar >> (leftbits-6)) & 0x3f;
	    leftbits -= 6;
	    *ascii_data++ = table_b2a_base64[this_ch];
	}
    }
    state->leftbits = leftbits;
    state->leftchar = leftchar;

    /* now output the ascii data line by line */
    ascii_left = ascii_data - encoded;
    while (ascii_left > 0)
    {
	int linelength = BASE64_MAXASCII - state->column;

	if (ascii_left < linelength)
	    linelength = ascii_left;
	if (Filter_Write(target, ((char*)ascii_data) - ascii_left,
			 linelength) == 0)
	    return 0;
	ascii_left -= linelength;
	state->column += linelength;
	if (state->column >= BASE64_MAXASCII)
	{
	    if (Filter_Write(target, "\n", 1) == 0)
		return 0;
	    state->column = 0;
	}
    }

    return bin_data - (const unsigned char *)buf;
}

static int
close_base64encode(void * clientdata, PyObject * target)
{
    Base64EncodeState * state = (Base64EncodeState*)clientdata;
    unsigned char buf[4];
    unsigned char * ascii_data = buf;
    
    if (state->leftbits == 2)
    {
	*ascii_data++ = table_b2a_base64[(state->leftchar & 3) << 4];
	*ascii_data++ = BASE64_PAD;
	*ascii_data++ = BASE64_PAD;
    }
    else if (state->leftbits == 4)
    {
	*ascii_data++ = table_b2a_base64[(state->leftchar & 0xf) << 2];
	*ascii_data++ = BASE64_PAD;
    }
    
    if (ascii_data > buf || state->column != 0)
    {
	*ascii_data++ = '\n';	/* Append a courtesy newline */
    }
    if (ascii_data > buf)
    {
	if (Filter_Write(target, (char*)buf, ascii_data - buf) == 0)
	    return EOF;
    }

    return 0;
}

PyObject *
Filter_Base64Encode(PyObject * self, PyObject * args)
{
    PyObject * target;
    Base64EncodeState * state;

    if (!PyArg_ParseTuple(args, "O", &target))
	return NULL;

    state = malloc(sizeof (Base64EncodeState));
    if (!state)
	return PyErr_NoMemory();
    state->leftbits = 0;
    state->leftchar = 0;
    state->column = 0; /* assume target is at the beginning of a line */

    return Filter_NewEncoder(target, "Base64Decode", 0, write_base64,
			     close_base64encode, free, state);
}
