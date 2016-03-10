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
import unicodedata
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

MYANMAR = (u'\u1000', u'\u109f')
MYANMAR_EXT = (u'\uaa60', u'\uaa7f')
ARABIC = (u'\u0600', u'\u06ff')
ARABIC_SUPPLEMENT = (u'\u0750', u'\u077f')
ARABIC_FORMS_A = (u'\ufb50', u'\ufdff')
ARABIC_FORMS_B = (u'\ufe70', u'\ufeff')


def check_unicode_range(rng, symbol):
	return rng[0] <= symbol and rng[1] >= symbol

def check_lang(text, ranges):
	test = text
	if len(test) > 20: test = test[:20]
	ret = False
	for item in test:
		for reg in ranges:
			if check_unicode_range(reg, item): ret = True
		if ret: break
	return ret

def check_manyamar(text):
	return check_lang(text, (MYANMAR, MYANMAR_EXT))

def check_arabic(text):
	return check_lang(text, (ARABIC, ARABIC_SUPPLEMENT,
							ARABIC_FORMS_A, ARABIC_FORMS_B))

def cluster_text(text, clusters):
	index = 0
	text_seq = []
	for item in clusters:
		if text[index:item[0]]:
			text_seq += list(text[index:item[0]])
		text_seq += [text[item[0]:item[1]], ]
		index = item[1]
	if text[index:]:
		text_seq += list(text[index:])
	return text_seq

def word_group(text_seq):
	i = 0
	index = None
	while i < len(text_seq):
		if not index is None:
			if not text_seq[i] in NONPRINTING_CHARS:
				text_seq[index] += text_seq[i]
				text_seq[i] = ' '
			else:
				index = None
		else:
			if not text_seq[i] in NONPRINTING_CHARS:
				index = i
		i += 1


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

def find_rtl_regs(layout_data):
	rtl_regs = []
	reg = []
	i = 0
	while i < len(layout_data) - 1:
		if not reg and layout_data[i][5] > layout_data[i + 1][5]:
			reg.append(i)
		elif reg and layout_data[i][5] < layout_data[i + 1][5]:
			reg.append(i + 1)
			rtl_regs.append(reg)
			reg = []
		i += 1
	if reg:
		reg.append(i + 1)
		rtl_regs.append(reg)
	return rtl_regs

def fix_embedded_rlt_clusters(clusters, rtl_regs):
	pass

def assemble_to_lines(text, rtl_regs):
	if rtl_regs:
		index = 0
		text_seq = ()
		for item in rtl_regs:
			if text[index:item[0]]:
				text_seq += tuple(text[index:item[0]])
			text_seq += (''.join(text[item[0]:item[1]]),)
			text_seq += (len(text[item[0]:item[1]]) - 1) * (' ',)
			index = item[1]
		if text[index:]:
			text_seq += tuple(text[index:])
		text = text_seq
	return text

def get_text_paths(orig_text, width, text_style, attributes):
	if not orig_text: orig_text = NONPRINTING_CHARS[0]
	_set_layout(PANGO_LAYOUT, orig_text, width, text_style, attributes)
	w, h = _libpango.get_layout_pixel_size(PANGO_LAYOUT)

	surf = cairo.ImageSurface(cairo.FORMAT_RGB24, 100, 100)
	ctx = cairo.Context(surf)
	ctx.set_matrix(libcairo.DIRECT_MATRIX)

	ctx.new_path()
	ctx.move_to(0, 0)
	layout = _libpango.create_layout(ctx)
	_set_layout(layout, orig_text, width, text_style, attributes)
	_libpango.layout_path(ctx, layout)
	cpath = ctx.copy_path()

	line_points = []
	for item in get_line_positions():
		line_points.append([0.0, item])

	text = '' + orig_text
	clusters = []
	rtl_regs = []
	rtl_flag = False

	#Ligature support
	if text_style[5]:
		layout_data, clusters, bidi_flag, rtl_flag = get_cluster_positions()
		if not rtl_flag and not bidi_flag:
			if clusters:
				text = cluster_text(text, clusters)
				if check_manyamar(orig_text):
					word_group(text)

		elif not rtl_flag and bidi_flag:
			rtl_regs = find_rtl_regs(layout_data)
			text = cluster_text(text, clusters)
			text = assemble_to_lines(text, rtl_regs)

		elif rtl_flag and not bidi_flag:
			rtl_regs = find_rtl_regs(layout_data)
			text = cluster_text(text, clusters)
			text = assemble_to_lines(text, rtl_regs)

		elif rtl_flag and bidi_flag:
			rtl_regs = find_rtl_regs(layout_data)
			text = cluster_text(text, clusters)
			text = assemble_to_lines(text, rtl_regs)

	#Simple char-by-char rendering
	else:
		layout_data = get_char_positions()

	layout_bbox = [0.0, layout_data[0][1],
					float(w), layout_data[0][1] - float(h)]


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
							layout_data[i][0], layout_data[i][1])
		libcairo.apply_cmatrix(cpath, matrix)
		glyphs.append(cpath)

	if rtl_regs:
		index = 0
		data = []
		for item in rtl_regs:
			if layout_data[index:item[0]]:
				data += layout_data[index:item[0]]
			rtl = layout_data[item[0]:item[1]]
			rtl.reverse()
			i = 0
			while i < len(rtl):
				x, y, w, h, bl, j = rtl[i]
				rtl[i] = (x + w, y, -w, h, bl, j)
				i += 1
			data += rtl
			index = item[1]
		if layout_data[index:]:
			data += layout_data[index:]
		layout_data = data

	return glyphs, line_points, layout_data, layout_bbox, clusters
