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
from copy import deepcopy

from uc2 import libcairo

import core
from core import NONPRINTING_CHARS
from langs import check_maynmar, check_arabic


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

def get_glyphs(ctx, layout_data, text, width, text_style, markup):
	glyphs = []
	i = -1
	for item in text:
		i += 1

		if item in NONPRINTING_CHARS:
			glyphs.append(None)
			continue

		ctx.new_path()
		ctx.move_to(0, 0)
		layout = core.create_layout(ctx)
		text_range = [i, i + len(item)]
		vpos = core.set_glyph_layout(item, width, text_style, markup,
									text_range, True, layout)
		if vpos:
			for index in range(*text_range):
				x, y, w, h, base_line, byte_index = layout_data[index]
				dh = (y - base_line) * vpos
				layout_data[index] = (x, y + dh, w, h,
									base_line + dh, byte_index)
		core.layout_path(ctx, layout)
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

def get_rtl_glyphs(ctx, layout_data, log_layout_data, byte_dict, rtl_regs,
				 text, width, text_style, markup):
	glyphs = []
	for item in layout_data:
		try:
			index = byte_dict[item[5]]
			txt = text[index]
			if is_item_in_rtl(index, rtl_regs):
				text_range = [index - len(txt) + 1, index + 1]
			else:
				text_range = [index, index + len(txt)]

		except:continue

		if txt in NONPRINTING_CHARS:
			glyphs.append(None)
			continue

		ctx.new_path()
		ctx.move_to(0, 0)
		layout = core.create_layout(ctx)
		vpos = core.set_glyph_layout(txt, width, text_style,
								markup, text_range, True, layout)
		if vpos:
			for index in range(*text_range):
				x, y, w, h, base_line, byte_index = log_layout_data[index]
				dh = (y - base_line) * vpos
				log_layout_data[index] = (x, y + dh, w, h,
									base_line + dh, byte_index)
		core.layout_path(ctx, layout)
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

def get_text_paths(orig_text, width, text_style, markup):
# Test markup
#	markup = [('b', (6, 11)), ('i', (22, 26)), ('b', (28, 39)), ('i', (28, 39)),
#			('sub', (52, 55)), ('sup', (61, 63)), ('s', (73, 79)), ('u', (80, 90)), ]
	if not orig_text:
		orig_text = NONPRINTING_CHARS[0]
		markup = []
	core.set_layout(orig_text, width, text_style, markup)
	w, h = core.get_layout_size()

	surf = cairo.ImageSurface(cairo.FORMAT_RGB24, 100, 100)
	ctx = cairo.Context(surf)
	ctx.set_matrix(libcairo.DIRECT_MATRIX)

	line_points = []
	for item in core.get_line_positions():
		line_points.append([0.0, item])

	text = '' + orig_text
	clusters = []
	rtl_regs = []
	rtl_flag = False

	#Ligature support
	if text_style[5]:
		data = core.get_cluster_positions(len(orig_text))
		layout_data, clusters, clusters_index, bidi_flag, rtl_flag = data

		if not rtl_flag and not bidi_flag:
			if clusters:
				text = cluster_text(text, clusters)
				if check_maynmar(orig_text):
					word_group(text)
			log_layout_data = layout_data
			glyphs = get_glyphs(ctx, layout_data, text,
							width, text_style, markup)
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
			log_layout_data = get_log_layout_data(layout_data, byte_dict, rtl_regs)
			glyphs = get_rtl_glyphs(ctx, layout_data, log_layout_data,
					byte_dict, log_rtl_regs, text, width, text_style, markup)

	#Simple char-by-char rendering
	else:
		layout_data = core.get_char_positions(len(orig_text))
		log_layout_data = layout_data
		glyphs = get_glyphs(ctx, layout_data, text,
						width, text_style, markup)

	layout_bbox = [0.0, layout_data[0][1],
					float(w), layout_data[0][1] - float(h)]

	return glyphs, line_points, log_layout_data, layout_bbox, clusters
