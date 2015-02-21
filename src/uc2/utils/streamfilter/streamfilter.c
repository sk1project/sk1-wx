/*
 *  Copyright (C) 1998, 1999, 2000, 2001 by Bernhard Herzog.
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


#include <Python.h>

#include "filterobj.h"
#include "linefilter.h"
#include "subfilefilter.h"
#include "base64filter.h"
#include "stringfilter.h"
#include "nullfilter.h"
#include "hexfilter.h"
/* hack to deselect the filters not needed by Sketch */
#ifdef ALL_FILTERS
#include "zlibfilter.h"
#include "ascii85filter.h"
#endif
#include "binfile.h"


static PyMethodDef filter_functions[] = {
	{"Base64Decode",	Filter_Base64Decode,	METH_VARARGS},
	{"Base64Encode",	Filter_Base64Encode,	METH_VARARGS},
	{"LineDecode",		Filter_LineDecode,	METH_VARARGS},
	{"SubFileDecode",	Filter_SubFileDecode,	METH_VARARGS},
	{"StringDecode",	Filter_StringDecode,	METH_VARARGS},
	{"NullEncode",		Filter_NullEncode,	METH_VARARGS},
	{"NullDecode",		Filter_NullDecode,	METH_VARARGS},
	{"HexEncode",		Filter_HexEncode,	METH_VARARGS},
	{"HexDecode",		Filter_HexDecode,	METH_VARARGS},
#ifdef ALL_FILTERS
	{"FlateDecode",		Filter_FlateDecode,	METH_VARARGS},
	{"ASCII85Encode",	Filter_ASCII85Encode,	METH_VARARGS},
	{"ASCII85Decode",	Filter_ASCII85Decode,	METH_VARARGS},
#endif
	{"BinaryInput",		BinFile_New,		METH_VARARGS},
	{NULL, NULL} 
};

static Filter_Functions functions = {
    /* internal methods */
    _Filter_Underflow,
    _Filter_Overflow,
    
    /* decoder methods */
    Filter_Read,
    Filter_ReadToChar,
    Filter_GetLine,
    Filter_Ungetc,
    
    /* endcoder methods */
    Filter_Write,
    Filter_Flush,

    /* common filter methods */
    Filter_Close
};


DL_EXPORT(void)
initstreamfilter(void)
{
    PyObject * d, *m, *v;

    FilterType.ob_type = &PyType_Type;

    m = Py_InitModule("streamfilter", filter_functions);
    d = PyModule_GetDict(m);

    PyDict_SetItemString(d, "FilterType", (PyObject*)(&FilterType));
    v = PyCObject_FromVoidPtr(&functions, NULL);
    PyDict_SetItemString(d, "Filter_Functions", v);
    Py_DECREF(v);
}
