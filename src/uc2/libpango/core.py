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

import os
import cairo
import cgi
from copy import deepcopy

import _libpango

PANGO_UNITS = 1024

SURFACE = cairo.ImageSurface(cairo.FORMAT_RGB24, 1, 1)
CTX = cairo.Context(SURFACE)
DIRECT_MATRIX = cairo.Matrix()

PANGO_MATRIX = cairo.Matrix(1.0, 0.0, 0.0, -1.0, 0.0, 0.0)
PANGO_LAYOUT = _libpango.create_layout(CTX)
NONPRINTING_CHARS = ' \n\t '.decode('utf-8')

def get_version():
	return _libpango.get_version()


GLYPH_CACHE = {}

def get_glyph_cache(font_name, char):
	ret = None
	char = str(char)
	if font_name in GLYPH_CACHE:
		if char in GLYPH_CACHE[font_name]:
			ret = deepcopy(GLYPH_CACHE[font_name][char])
	return ret

def set_glyph_cache(font_name, char, glyph):
	char = str(char)
	if not font_name in GLYPH_CACHE:
		GLYPH_CACHE[font_name] = {}
	GLYPH_CACHE[font_name][char] = deepcopy(glyph)

#--- Pango context functionality

def create_layout(ctx=CTX):
	return _libpango.create_layout(ctx)

def get_font_description(text_style, check_nt=False):
	font_size = text_style[2]
	if check_nt and os.name == 'nt': font_size *= 10
	fnt_descr = text_style[0] + ', ' + text_style[1] + ' ' + str(font_size)
	return _libpango.create_font_description(fnt_descr)

def set_layout(text, width, text_style, attributes, check_nt=False, layout=PANGO_LAYOUT):
	if not width == -1: width *= PANGO_UNITS
	_libpango.set_layout_width(layout, width)
	fnt_descr = get_font_description(text_style, check_nt)
	_libpango.set_layout_font_description(layout, fnt_descr)
	_libpango.set_layout_alignment(layout, text_style[3])
	text = text.encode('utf-8')
	markup = cgi.escape(text)
	_libpango.set_layout_markup(layout, markup)

def layout_path(ctx=CTX, layout=PANGO_LAYOUT):
	_libpango.layout_path(ctx, layout)

def get_line_positions(layout=PANGO_LAYOUT):
	return _libpango.get_layout_line_positions(layout)

def get_char_positions(size, layout=PANGO_LAYOUT):
	return _libpango.get_layout_char_positions(layout, size)

def get_cluster_positions(size, layout=PANGO_LAYOUT):
	return _libpango.get_layout_cluster_positions(layout, size)

def get_layout_size(layout=PANGO_LAYOUT):
	return _libpango.get_layout_pixel_size(layout)

def get_layout_bbox(layout=PANGO_LAYOUT):
	w, h = get_layout_size(layout)
	return [0.0, 0.0, float(w), float(-h)]
