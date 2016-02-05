# -*- coding: utf-8 -*-
#
#	Copyright (C) 2016 by Igor E. Novikov
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.


import cairo
import cgi

from uc2 import libcairo

import _libpango

PANGO_UNITS = 1024

SURFACE = cairo.ImageSurface(cairo.FORMAT_RGB24, 1, 1)
CTX = cairo.Context(SURFACE)
DIRECT_MATRIX = cairo.Matrix()

PANGO_MATRIX = cairo.Matrix(1.0, 0.0, 0.0, -1.0, 0.0, 0.0)
PANGO_LAYOUT = _libpango.create_layout(CTX)

FAMILIES_LIST = []
FAMILIES_DICT = {}

def bbox_size(bbox):
	x0, y0, x1, y1 = bbox
	w = abs(x1 - x0)
	h = abs(y1 - y0)
	return w, h

def update_fonts():
	FAMILIES_LIST[:] = []
	FAMILIES_DICT.clear()
	font_map = _libpango.get_fontmap()
	for item in font_map:
		font_name = item[0]
		font_faces = item[1]
		if font_faces:
			FAMILIES_LIST.append(font_name)
			FAMILIES_DICT[font_name] = list(font_faces)
	FAMILIES_LIST.sort()

def get_fonts():
	if not FAMILIES_LIST: update_fonts()
	return FAMILIES_LIST, FAMILIES_DICT

def _get_font_description(text_style):
	fnt_descr = text_style[0] + ', ' + text_style[1] + ' ' + str(text_style[2])
	return _libpango.create_font_description(fnt_descr)

def _set_layout(layout, text, width, text_style, attributes):
	_libpango.set_layout_width(layout, width)
	fnt_descr = _get_font_description(text_style)
	_libpango.set_layout_font_description(layout, fnt_descr)
	_libpango.set_layout_alignment(layout, text_style[3])
	_libpango.set_layout_markup(layout, cgi.escape(text))

def get_text_paths(text, width, text_style, attributes):
	_set_layout(PANGO_LAYOUT, text, width, text_style, attributes)
	w, h = _libpango.get_layout_pixel_size(PANGO_LAYOUT)

	surf = cairo.ImageSurface(cairo.FORMAT_RGB24, w, h)
	ctx = cairo.Context(surf)
	ctx.set_matrix(libcairo.DIRECT_MATRIX)
	ctx.new_path()
	ctx.move_to(0, 0)
	layout = _libpango.create_layout(ctx)
	_set_layout(layout, text, width, text_style, attributes)
	_libpango.layout_path(ctx, layout)

	cpath = ctx.copy_path()

	width = bbox_size(libcairo.get_cpath_bbox(cpath))[0]
	dx = 0.0
	if text_style[3] == 1: dx = -width / 2.0
	elif text_style[3] == 2: dx = -width
	matrix = cairo.Matrix(1.0, 0.0, 0.0, -1.0, dx, 0.0)

	libcairo.apply_cmatrix(cpath, matrix)
	return libcairo.get_path_from_cpath(cpath)
