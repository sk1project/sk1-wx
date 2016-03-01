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
from copy import deepcopy

from uc2 import libcairo

import _libpango

PANGO_UNITS = 1024

SURFACE = cairo.ImageSurface(cairo.FORMAT_RGB24, 1, 1)
CTX = cairo.Context(SURFACE)
DIRECT_MATRIX = cairo.Matrix()

PANGO_MATRIX = cairo.Matrix(1.0, 0.0, 0.0, -1.0, 0.0, 0.0)
PANGO_LAYOUT = _libpango.create_layout(CTX)
NONPRINTING_CHARS = ' \n\t'


FAMILIES_LIST = []
FAMILIES_DICT = {}

GLYPH_CACHE = {}

def get_version():
	return _libpango.get_version()

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

def _get_font_description(text_style):
	fnt_descr = text_style[0] + ', ' + text_style[1] + ' ' + str(text_style[2])
	return _libpango.create_font_description(fnt_descr)

def _set_layout(layout, text, width, text_style, attributes):
	text = text.encode('utf-8')
	_libpango.set_layout_width(layout, width)
	fnt_descr = _get_font_description(text_style)
	_libpango.set_layout_font_description(layout, fnt_descr)
	_libpango.set_layout_alignment(layout, text_style[3])
	markup = cgi.escape(text)
	_libpango.set_layout_markup(layout, markup)

def get_line_positions():
	return _libpango.get_layout_line_positions(PANGO_LAYOUT)

def get_char_positions():
	return _libpango.get_layout_char_positions(PANGO_LAYOUT)

def get_cluster_positions():
	return _libpango.get_layout_cluster_positions(PANGO_LAYOUT)

def get_layout_bbox():
	w, h = _libpango.get_layout_pixel_size(PANGO_LAYOUT)
	return [0.0, 0.0, float(w), float(-h)]

def get_text_paths(text, width, text_style, attributes):
	if not text: text = NONPRINTING_CHARS[0]
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

	line_points = []
	for item in get_line_positions():
		line_points.append([0.0, item])

	if text_style[5]:
		layout_data, clusters = get_cluster_positions()
		if clusters:
			index = 0
			text_seq = ()
			for item in clusters:
				if text[index:item[0]]:
					text_seq += tuple(text[index:item[0]])
				text_seq += (text[item[0]:item[1]],)
				index = item[1]
			if text[index:]:
				text_seq += tuple(text[index:item[0]])
			text = text_seq
	else:
		layout_data = get_char_positions()
		clusters = []

	dy = line_points[0][1]
	layout_bbox = get_layout_bbox()

	glyphs = []
	i = -1
	for item in text:
		i += 1
		if item in NONPRINTING_CHARS:
			glyphs.append(None)
			continue
		ctx.new_path()
		ctx.move_to(0, 0)
		layout = _libpango.create_layout(ctx)
		_set_layout(layout, item, width, text_style, attributes)
		_libpango.layout_path(ctx, layout)
		cpath = ctx.copy_path()
		matrix = cairo.Matrix(1.0, 0.0, 0.0, -1.0,
							layout_data[i][0], layout_data[i][4] - dy)
		libcairo.apply_cmatrix(cpath, matrix)
		glyphs.append(cpath)
	return glyphs, line_points, layout_data, layout_bbox, clusters
