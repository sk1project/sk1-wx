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
import pango, pangocairo
import cgi

from uc2 import libcairo
from uc2.formats.sk2 import sk2_const

PANGO_UNITS = 1024.0

ALIGN_MAP = {
sk2_const.TEXT_ALIGN_LEFT:pango.ALIGN_LEFT,
sk2_const.TEXT_ALIGN_CENTER:pango.ALIGN_CENTER,
sk2_const.TEXT_ALIGN_RIGHT:pango.ALIGN_RIGHT,
}

SURFACE = cairo.ImageSurface(cairo.FORMAT_RGB24, 1, 1)
CTX = cairo.Context(SURFACE)
DIRECT_MATRIX = cairo.Matrix()

PANGO_MATRIX = cairo.Matrix(1.0, 0.0, 0.0, -1.0, 0.0, 0.0)
PCCTX = pangocairo.CairoContext(CTX)
PANGO_LAYOUT = PCCTX.create_layout()

FAMILIES_LIST = []
FAMILIES_DICT = {}

def update_fonts():
	FAMILIES_LIST[:] = []
	FAMILIES_DICT.clear()
	fm = pangocairo.cairo_font_map_get_default()
	context = fm.create_context()
	families = context.list_families()
	for item in families:
		fcs = []
		scalable = True
		for face in item.list_faces():
			if not face.list_sizes() is None:
				scalable = False
			fcs.append(face.get_face_name())
		if scalable:
			fcs.sort()
			FAMILIES_DICT[item.get_name()] = fcs
			FAMILIES_LIST.append(item.get_name())
	FAMILIES_LIST.sort()

def get_fonts():
	if not FAMILIES_LIST: update_fonts()
	return FAMILIES_LIST, FAMILIES_DICT

def get_text_paths(text, width, text_style, attributes):

	#Setting cairo context
	CTX.set_matrix(libcairo.DIRECT_MATRIX)
	CTX.new_path()
	CTX.move_to(0, 0)

	PCCTX.update_layout(PANGO_LAYOUT)

	#Processing text properties

	if not width == sk2_const.TEXTBLOCK_WIDTH:
		width = int(width * PANGO_UNITS)
	PANGO_LAYOUT.set_width(width)

	fnt_descr = text_style[0] + ', ' + text_style[1] + ' ' + str(text_style[2])
	PANGO_LAYOUT.set_font_description(pango.FontDescription(fnt_descr))

	if text_style[3] == sk2_const.TEXT_ALIGN_JUSTIFY:
		PANGO_LAYOUT.set_justify(True)
		PANGO_LAYOUT.set_alignment(pango.ALIGN_LEFT)
	else:
		PANGO_LAYOUT.set_alignment(ALIGN_MAP[text_style[3]])

	PANGO_LAYOUT.set_markup(cgi.escape(text))

	#---

	PCCTX.layout_path(PANGO_LAYOUT)
	cairo_path = CTX.copy_path()
	libcairo.apply_cmatrix(cairo_path, PANGO_MATRIX)

	return libcairo.get_path_from_cpath(cairo_path)
