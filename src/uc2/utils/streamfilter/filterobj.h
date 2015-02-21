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

#ifndef FILTEROBJ_H
#define FILTEROBJ_H
#include <Python.h>

#if defined(__cplusplus)
extern "C" {
#endif

typedef size_t (*filter_read_proc)(void *, PyObject * source,
				   char * buffer, size_t length);
typedef size_t (*filter_write_proc)(void *, PyObject * target,
				    const char * buffer, size_t length);
typedef int (*filter_close_proc)(void *, PyObject * target);
typedef void (*filter_dealloc_proc)(void * client_data);



PyObject * Filter_NewEncoder(PyObject * target,
			     const char * filtername,
			     int flags,
			     filter_write_proc,
			     filter_close_proc,
			     filter_dealloc_proc,
			     void * client_data);
PyObject * Filter_NewDecoder(PyObject * source,
			     const char * filtername,
			     int flags,
			     filter_read_proc,
			     filter_close_proc,
			     filter_dealloc_proc,
			     void * client_data);
/* decoder methods */
size_t Filter_Read(PyObject * filter, char * buffer, size_t length);
size_t Filter_ReadToChar(PyObject * filter, char * buffer, size_t length,
			 int character);
PyObject * Filter_GetLine(PyObject * filter, int);

int Filter_Ungetc(PyObject * filter, int);

/* encoder methods */
int Filter_Write(PyObject * filter, const char * buffer, size_t length);
int Filter_Flush(PyObject * filter, int flush_target);

/* common filter methods */
int Filter_Close(PyObject * filter);

#define FILTER_CLOSED		0x0001
#define FILTER_EOF		0x0002
#define FILTER_BAD		0x0004
#define FILTER_CLOSE_STREAM	0x0100

typedef struct {
    PyObject_HEAD
    char * buffer;
    char * buffer_end;
    char * current;
    char * end;
    char * base;
    int flags;
    long streampos;
    PyObject * stream;	/* source or target */
    PyObject * filtername;
    filter_read_proc read;
    filter_write_proc write;
    filter_close_proc close;
    filter_dealloc_proc dealloc;
    void * client_data;
} FilterObject;

extern DL_IMPORT(PyTypeObject) FilterType;

#define Filter_Check(op) ((op)->ob_type == &FilterType)


int _Filter_Underflow(FilterObject*);
int _Filter_Overflow(FilterObject*, int);

#define __Filter_PUTC(filter, c, overflow)\
   ((filter)->current >= (filter)->end \
    ? (overflow)((filter),(unsigned char)(c))\
    : (unsigned char)(*((filter)->current++) = (c)))

#define __Filter_GETC(filter, underflow)\
    ((filter)->current >= (filter)->end ? (underflow)(filter)\
     : *(unsigned char*)((filter)->current++))

#define Filter_PUTC(filter, c) __Filter_PUTC((filter), (c), _Filter_Overflow)
#define Filter_GETC(filter)    __Filter_GETC((filter), _Filter_Underflow)


typedef struct {
    int (*Filter_Underflow)(FilterObject*);
    int (*Filter_Overflow)(FilterObject*, int);
    
    /* decoder methods */
    size_t (*Filter_Read)(PyObject * filter, char * buffer, size_t length);
    size_t (*Filter_ReadToChar)(PyObject * filter, char * buffer,
				size_t length, int character);
    PyObject * (*Filter_GetLine)(PyObject * filter, int);
    int (*Filter_Ungetc)(PyObject*, int);
    
    /* endcoder methods */
    int (*Filter_Write)(PyObject * filter, const char * buffer, size_t length);
    int (*Filter_Flush)(PyObject * filter, int flush_target);

    /* common filter methods */
    int (*Filter_Close)(PyObject * filter);
} Filter_Functions;

#define Filter_DL_PUTC(func, filter, c) \
	__Filter_PUTC((filter), (c), ((func)->Filter_Overflow))
#define Filter_DL_GETC(func, filter)  \
	__Filter_GETC((filter), ((func)->Filter_Underflow))

#if defined(__cplusplus)
}
#endif

#endif /* FILTEROBJ_H */
