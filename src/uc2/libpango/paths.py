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

from uc2 import libcairo

import _libpango

from core import PANGO_UNITS, NONPRINTING_CHARS, PANGO_LAYOUT

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

def check_maynmar(text):
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

def rtl_word_group(text_seq):
	i = 0
	buff = ''
	while i < len(text_seq):
		if not text_seq[i] in NONPRINTING_CHARS:
			buff += text_seq[i]
			text_seq[i] = ' '
		else:
			if buff:
				text_seq[i - 1] = buff
				buff = ''
		i += 1
	if buff:
		text_seq[i - 1] = buff

def rtl_word_group_in_reg(text_seq, reg):
	i = reg[0]
	buff = ''
	while i < reg[1]:
		if not text_seq[i] in NONPRINTING_CHARS:
			buff += text_seq[i]
			text_seq[i] = ' '
		else:
			if buff:
				text_seq[i - 1] = buff
				buff = ''
		i += 1
	if buff:
		text_seq[i - 1] = buff




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

def _get_font_description(text_style, check_nt=False):
	font_size = text_style[2]
	if check_nt and os.name == 'nt': font_size *= 10
	fnt_descr = text_style[0] + ', ' + text_style[1] + ' ' + str(font_size)
	return _libpango.create_font_description(fnt_descr)

def _set_layout(layout, text, width, text_style, attributes, check_nt=False):
	if not width == -1: width *= PANGO_UNITS
	_libpango.set_layout_width(layout, width)
	fnt_descr = _get_font_description(text_style, check_nt)
	_libpango.set_layout_font_description(layout, fnt_descr)
	_libpango.set_layout_alignment(layout, text_style[3])
	text = text.encode('utf-8')
	markup = cgi.escape(text)
	_libpango.set_layout_markup(layout, markup)

def get_line_positions():
	return _libpango.get_layout_line_positions(PANGO_LAYOUT)

def get_char_positions(size):
	return _libpango.get_layout_char_positions(PANGO_LAYOUT, size)

def get_cluster_positions(size):
	return _libpango.get_layout_cluster_positions(PANGO_LAYOUT, size)

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

def utf8_to_ucs4_dict(text):
	text_dict = {}
	index = 0
	ucs4_index = 0
	for item in text:
		for char in item:
			text_dict[index] = ucs4_index
			index += len(char.encode('utf-8'))
		ucs4_index += 1
	text_dict[index] = -1
	return text_dict

def fix_rlt_clusters(clusters_index, byte_dict):
	clusters = []
	for item in clusters_index:
		start, end = item
		start, end = byte_dict[start], byte_dict[end]
		cluster = (min(start, end), max(start, end) + 1)
		clusters.append(cluster)
	return clusters

def fix_rlt_regs(rtl_regs, layout_data, byte_dict):
	regs = []
	for item in rtl_regs:
		start, end = item
		start, end = layout_data[start][5], layout_data[end - 1][5]
		start, end = byte_dict[start], byte_dict[end]
		reg = (min(start, end), max(start, end) + 1)
		regs.append(reg)
	return regs

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

def get_rtl_layout_data(layout_data, rtl_regs):
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
	return data

def get_glyphs(ctx, layout_data, text, width, text_style, attributes):
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
		_set_layout(layout, item, width, text_style, attributes, check_nt=True)
		_libpango.layout_path(ctx, layout)
		cpath = ctx.copy_path()
		m00 = 1.0
		m11 = -1.0
		if os.name == 'nt':
			m00 *= 0.1
			m11 *= 0.1
		matrix = cairo.Matrix(m00, 0.0, 0.0, m11,
							layout_data[i][0], layout_data[i][1])
		libcairo.apply_cmatrix(cpath, matrix)
		glyphs.append(cpath)
	return glyphs

def get_rtl_glyphs(ctx, layout_data, byte_dict, text, width, text_style, attributes):
	glyphs = []
	for item in layout_data:
		try:
			txt = text[byte_dict[item[5]]]
		except:continue

		if txt in NONPRINTING_CHARS:
			glyphs.append(None)
			continue

		ctx.new_path()
		ctx.move_to(0, 0)
		layout = _libpango.create_layout(ctx)
		_set_layout(layout, txt, width, text_style, attributes, check_nt=True)
		_libpango.layout_path(ctx, layout)
		cpath = ctx.copy_path()
		m00 = 1.0
		m11 = -1.0
		if os.name == 'nt':
			m00 *= 0.1
			m11 *= 0.1
		matrix = cairo.Matrix(m00, 0.0, 0.0, m11, item[0], item[1])
		libcairo.apply_cmatrix(cpath, matrix)
		glyphs.append(cpath)
	return glyphs

def is_item_in_rtl(index, rtl_regs):
	for item in rtl_regs:
		if index < item[0]:
			return False
		if index >= item[1]:
			continue
		elif index >= item[0] and index < item[1]:
			return True
	return False

def get_log_layout_data(layout_data, byte_dict, rtl_regs):
	log_layout_data = len(layout_data) * ['', ]
	index = 0
	for item in layout_data:
		if is_item_in_rtl(index, rtl_regs):
			x, y, w, h, bl, j = item
			data = (x + w, y, -w, h, bl, j)
		else:
			data = deepcopy(item)
		log_layout_data[byte_dict[item[5]]] = data
		index += 1
	return log_layout_data

def get_text_paths(orig_text, width, text_style, attributes):
	if not orig_text: orig_text = NONPRINTING_CHARS[0]
	_set_layout(PANGO_LAYOUT, orig_text, width, text_style, attributes)
	w, h = _libpango.get_layout_pixel_size(PANGO_LAYOUT)

	surf = cairo.ImageSurface(cairo.FORMAT_RGB24, 100, 100)
	ctx = cairo.Context(surf)
	ctx.set_matrix(libcairo.DIRECT_MATRIX)

	line_points = []
	for item in get_line_positions():
		line_points.append([0.0, item])

	text = '' + orig_text
	clusters = []
	rtl_regs = []
	rtl_flag = False

	#Ligature support
	if text_style[5]:
		data = get_cluster_positions(len(orig_text))
		layout_data, clusters, clusters_index, bidi_flag, rtl_flag = data

		if not rtl_flag and not bidi_flag:
			if clusters:
				text = cluster_text(text, clusters)
				if check_maynmar(orig_text):
					word_group(text)
			log_layout_data = layout_data
			glyphs = get_glyphs(ctx, layout_data, text,
							width, text_style, attributes)
		else:
			byte_dict = utf8_to_ucs4_dict(text)
			clusters = fix_rlt_clusters(clusters_index, byte_dict)
			text = cluster_text(text, clusters)
			byte_dict = utf8_to_ucs4_dict(text)
			rtl_regs = find_rtl_regs(layout_data)
			log_rtl_regs = fix_rlt_regs(rtl_regs, layout_data, byte_dict)
			for item in log_rtl_regs:
				if check_arabic(text[item[0]:item[1]]):
					rtl_word_group_in_reg(text, item)
			glyphs = get_rtl_glyphs(ctx, layout_data, byte_dict, text,
						width, text_style, attributes)
			log_layout_data = get_log_layout_data(layout_data, byte_dict, rtl_regs)

	#Simple char-by-char rendering
	else:
		layout_data = get_char_positions(len(orig_text))
		log_layout_data = layout_data
		glyphs = get_glyphs(ctx, layout_data, text,
						width, text_style, attributes)

	layout_bbox = [0.0, layout_data[0][1],
					float(w), layout_data[0][1] - float(h)]

	return glyphs, line_points, log_layout_data, layout_bbox, clusters
