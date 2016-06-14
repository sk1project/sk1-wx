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


import cgi

import _libpango
from core import PANGO_LAYOUT

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

#---Font sampling

def _set_sample_layout(layout, text, family, fontsize):
	text = text.encode('utf-8')
	_libpango.set_layout_width(layout, -1)
	fnt_descr = family + ', ' + str(fontsize)
	fnt_descr = _libpango.create_font_description(fnt_descr)
	_libpango.set_layout_font_description(layout, fnt_descr)
	markup = cgi.escape(text)
	_libpango.set_layout_markup(layout, markup)

def get_sample_size(text, family, fontsize):
	_set_sample_layout(PANGO_LAYOUT, text, family, fontsize)
	return _libpango.get_layout_pixel_size(PANGO_LAYOUT)

def render_sample(ctx, text, family, fontsize):
	ctx.new_path()
	ctx.move_to(0, 0)
	layout = _libpango.create_layout(ctx)
	_set_sample_layout(layout, text, family, fontsize)
	_libpango.layout_path(ctx, layout)

#---Font sampling end