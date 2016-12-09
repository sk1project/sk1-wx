# -*- coding: utf-8 -*-
#
# 	 Copyright (C) 2016 by Igor E. Novikov
#
# 	 This program is free software: you can redistribute it and/or modify
# 	 it under the terms of the GNU General Public License as published by
# 	 the Free Software Foundation, either version 3 of the License, or
# 	 (at your option) any later version.
#
# 	 This program is distributed in the hope that it will be useful,
# 	 but WITHOUT ANY WARRANTY; without even the implied warranty of
# 	 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# 	 GNU General Public License for more details.
#
# 	 You should have received a copy of the GNU General Public License
# 	 along with this program.  If not, see <http://www.gnu.org/licenses/>.

import errno, sys
from struct import unpack
from copy import deepcopy

from uc2 import events, msgconst, uc2const, libgeom, libpango, libimg
from uc2.libgeom import multiply_trafo, apply_trafo_to_point
from uc2.formats.wmf import wmfconst, wmf_hatches, wmflib
from uc2.formats.wmf.wmflib import get_data
from uc2.formats.sk2 import sk2_model, sk2_const

SK2_CAPS = {
wmfconst.PS_ENDCAP_FLAT:sk2_const.CAP_BUTT,
wmfconst.PS_ENDCAP_ROUND:sk2_const.CAP_ROUND,
wmfconst.PS_ENDCAP_SQUARE:sk2_const.CAP_SQUARE,
}

SK2_JOIN = {
wmfconst.PS_JOIN_MITER:sk2_const.JOIN_MITER,
wmfconst.PS_JOIN_ROUND:sk2_const.JOIN_ROUND,
wmfconst.PS_JOIN_BEVEL:sk2_const.JOIN_BEVEL,
}

SK2_FILL_RULE = {
wmfconst.ALTERNATE:sk2_const.FILL_EVENODD,
wmfconst.WINDING:sk2_const.FILL_NONZERO,
}

class DC_Data(object):

	style = [[], [], [], []]
	curpoint = [0.0, 0.0]
	trafo = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
	opacity = True
	bgcolor = [1.0, 1.0, 1.0]
	fill_rule = sk2_const.FILL_EVENODD
	text_color = [0.0, 0.0, 0.0]
	text_align = sk2_const.TEXT_ALIGN_LEFT
	text_valign = sk2_const.TEXT_VALIGN_BASELINE
	text_update_cp = True
	text_rtl = False
	# (fontface, size, bold,italic,underline,strikeout, rotate, charset)
	font = ('Sans', 12, False, False, False, False, 0.0, 'cp1252')

class WMF_to_SK2_Translator(object):

	def translate(self, wmf_doc, sk2_doc):
		self.wmf_doc = wmf_doc
		self.sk2_doc = sk2_doc
		self.wmf_mt = wmf_doc.model
		self.sk2_mt = sk2_doc.model
		self.sk2_mtds = sk2_doc.methods

		inch = wmfconst.META_DPI
		left = top = 0
		right = wmfconst.META_W
		bottom = wmfconst.META_H
		header = self.wmf_mt
		self.gdiobjects = []
		self.dcstack = []
		self.dc = DC_Data()

		if self.wmf_mt.is_placeable():
			sig, handle, left, top, right, bottom, inch, rsvd, checksum\
				 = unpack(wmfconst.STRUCT_PLACEABLE, self.wmf_mt.chunk)

			val = 0
			for word in unpack('<10h', self.wmf_mt.chunk[:20]):
				val = val ^ word
			if val != checksum:
				msg = 'Incorrect header checksum'
				events.emit(events.MESSAGES, msgconst.ERROR, msg)
				raise IOError(errno.ENODATA, msg, '')

			header = self.wmf_mt.childs[0]

		self.inch = inch
		self.bbox = (left, top, right, bottom)

		self.coef = uc2const.in_to_pt / self.inch
		self.wx = self.vx = left
		self.vwidth = self.wwidth = right - left
		self.vheight = self.wheight = bottom - top
		self.wy = self.vy = top

		self.base_trafo = [self.coef, 0, 0, -self.coef,
						- self.coef * self.vwidth / 2.0 - self.coef * self.vx,
						self.coef * self.vheight / 2.0 + self.coef * self.vy]
		self.update_trafo()

		self.rec_funcs = {
			wmfconst.META_SETWINDOWORG:self.tr_set_window_org,
			wmfconst.META_SETWINDOWEXT:self.tr_set_window_ext,
			wmfconst.META_SETPOLYFILLMODE:self.tr_set_polyfill_mode,
			wmfconst.META_SETBKMODE:self.tr_set_bg_mode,
			wmfconst.META_SETBKCOLOR:self.tr_set_bg_color,
			wmfconst.META_SAVEDC:self.tr_save_dc,
			wmfconst.META_RESTOREDC: self.tr_restore_dc,

			wmfconst.META_CREATEPENINDIRECT:self.tr_create_pen_in,
			wmfconst.META_CREATEBRUSHINDIRECT:self.tr_create_brush_in,
			wmfconst.META_CREATEFONTINDIRECT:self.tr_create_font_in,
			wmfconst.META_DIBCREATEPATTERNBRUSH:self.tr_dibcreate_pat_brush,
			wmfconst.META_STRETCHDIB:self.tr_stretch_dib,
			#---------
			wmfconst.META_CREATEPALETTE:self.tr_create_noop,
			wmfconst.META_CREATEPATTERNBRUSH:self.tr_create_noop,
			wmfconst.META_CREATEREGION:self.tr_create_noop,
			#---------
			wmfconst.META_SELECTOBJECT:self.tr_select_object,
			wmfconst.META_DELETEOBJECT:self.tr_delete_object,

			wmfconst.META_ELLIPSE:self.tr_ellipse,
			wmfconst.META_RECTANGLE:self.tr_rectangle,
			wmfconst.META_ROUNDRECT:self.tr_round_rectangle,
			wmfconst.META_POLYGON:self.tr_polygon,
			wmfconst.META_POLYPOLYGON:self.tr_polypolygon,
			wmfconst.META_POLYLINE:self.tr_polyline,
			wmfconst.META_ARC:self.tr_arc,
			wmfconst.META_CHORD:self.tr_chord,
			wmfconst.META_PIE:self.tr_pie,
			wmfconst.META_MOVETO:self.tr_moveto,
			wmfconst.META_LINETO:self.tr_lineto,

			wmfconst.META_TEXTOUT:self.tr_textout,
			wmfconst.META_EXTTEXTOUT:self.tr_exttextout,
			wmfconst.META_SETTEXTCOLOR:self.tr_set_text_color,
			wmfconst.META_SETTEXTALIGN:self.tr_set_text_align,
			wmfconst.META_SETTEXTCHAREXTRA:self.noop,
			wmfconst.META_SETTEXTJUSTIFICATION:self.noop,
			}

		self.translate_header(header)
		self.sk2_mt.do_update()

	def update_trafo(self):
		wt = [1.0, 0.0, 0.0, 1.0, -self.wx, -self.wy]
		vt = [1.0, 0.0, 0.0, 1.0, self.vx, self.vy]
		scale = [float(self.vwidth) / self.wwidth, 0.0, 0.0,
			float(self.vheight) / self.wheight, 0.0, 0.0]
		tr = multiply_trafo(multiply_trafo(wt, scale), vt)
		self.set_trafo(multiply_trafo(tr, self.base_trafo))

	def get_size_pt(self, val): return val * self.coef
	def noop(self, *args):pass

	def get_style(self):
		style = deepcopy(self.dc.style)
		if style[0]:style[0][0] = self.dc.fill_rule
		if style[0] and style[0][1] == sk2_const.FILL_PATTERN:
			alpha = 1.0
			if not self.dc.opacity: alpha = 0.0
			style[0][2][2][1][2] = alpha
		return style

	def set_fill_style(self, fill): self.dc.style[0] = fill
	def set_stroke_style(self, stroke): self.dc.style[1] = stroke
	def set_font_style(self, font): self.dc.font = font
	def get_curpoint(self): return [] + self.dc.curpoint
	def set_curpoint(self, point): self.dc.curpoint = [] + point
	def get_trafo(self): return [] + self.dc.trafo
	def set_trafo(self, trafo): self.dc.trafo = [] + trafo
	def get_encoding(self): return '' + self.dc.font[-1]
	def get_text_style(self):
		sk2_style = [[], [], [], []]
		clr = [] + self.dc.text_color
		clr = [uc2const.COLOR_RGB, clr, 1.0, '', '']
		sk2_style[0] = [sk2_const.FILL_EVENODD, sk2_const.FILL_SOLID, clr]

		font = deepcopy(self.dc.font)
		faces = libpango.get_fonts()[1][font[0]]
		font_face = faces[0]
		if 'Regular' in faces: font_face = 'Regular'
		elif 'Normal' in faces: font_face = 'Normal'

		sk2_style[2] = [font[0], font_face, font[1],
								self.dc.text_align, [], True]
		tags = []
		if font[2]:tags.append('b')
		if font[3]:tags.append('i')
		if font[4]:tags.append('u')
		if font[5]:tags.append('s')
		return sk2_style, tags

	def add_gdiobject(self, obj):
		if None in self.gdiobjects:
			idx = self.gdiobjects.index(None)
			self.gdiobjects[idx] = obj
		else:
			self.gdiobjects.append(obj)

	def delete_gdiobject(self, idx):
		self.gdiobjects[idx] = None

	def translate_header(self, header):
		self.sk2_mt.doc_units = uc2const.UNIT_PT
		center = [0.0, 0.0]
		p = [self.wwidth, self.wheight]
		x0, y0 = apply_trafo_to_point(center, self.get_trafo())
		x1, y1 = apply_trafo_to_point(p, self.get_trafo())
		width = abs(x1 - x0)
		height = abs(y1 - y0)

		ornt = uc2const.PORTRAIT
		if width > height: ornt = uc2const.LANDSCAPE
		page_fmt = ['Custom', (width, height), ornt]

		pages_obj = self.sk2_mtds.get_pages_obj()
		pages_obj.page_format = page_fmt
		self.page = sk2_model.Page(pages_obj.config, pages_obj, 'WMF page')
		self.page.page_format = deepcopy(page_fmt)
		pages_obj.childs = [self.page, ]
		pages_obj.page_counter = 1

		self.layer = sk2_model.Layer(self.page.config, self.page)
		self.page.childs = [self.layer, ]

		for record in header.childs:
			try:
				self.translate_record(record)
			except:
				print wmfconst.WMF_RECORD_NAMES[record.func]
				for item in sys.exc_info(): print item

	def translate_record(self, record):
		if record.func in self.rec_funcs:
			self.rec_funcs[record.func](record.chunk[6:])

	def tr_set_window_org(self, chunk):
		self.wy, self.wx = get_data('<hh', chunk)
		self.update_trafo()

	def tr_set_window_ext(self, chunk):
		self.wheight, self.wwidth = get_data('<hh', chunk)
		self.update_trafo()

	def tr_set_polyfill_mode(self, chunk):
		mode = get_data('<h', chunk[:2])[0]
		if mode in SK2_FILL_RULE:
			self.dc.fill_rule = SK2_FILL_RULE[mode]

	def tr_save_dc(self):
		self.dcstack.append(deepcopy(self.dc))

	def tr_restore_dc(self):
		if self.dcstack:
			self.dc = self.dcstack[-1]
			self.dcstack = self.dcstack[:-1]

	def tr_set_bg_mode(self, chunk):
		mode = get_data('<h', chunk[:2])[0]
		self.dc.opacity = mode == wmfconst.OPAQUE

	def tr_set_bg_color(self, chunk):
		r, g, b = get_data('<BBBx', chunk)
		self.dc.bgcolor = [r / 255.0, g / 255.0, b / 255.0]

	def tr_set_text_color(self, chunk):
		r, g, b = get_data('<BBBx', chunk)
		self.dc.text_color = [r / 255.0, g / 255.0, b / 255.0]

	def tr_set_text_align(self, chunk):
		mode = get_data('<h', chunk[:2])[0]

		self.dc.text_update_cp = True
		if not mode & 0x0001: self.dc.text_update_cp = False

		lower = mode & 0x0007
		self.dc.text_align = sk2_const.TEXT_ALIGN_LEFT
		if lower & 0x0006 == wmfconst.TA_CENTER:
			self.dc.text_align = sk2_const.TEXT_ALIGN_CENTER
		elif lower & wmfconst.TA_RIGHT:
			self.dc.text_align = sk2_const.TEXT_ALIGN_RIGHT

		if mode & wmfconst.TA_BASELINE == wmfconst.TA_BASELINE:
			self.dc.text_valign = sk2_const.TEXT_VALIGN_BASELINE
		elif mode & wmfconst.TA_BOTTOM:
			self.dc.text_valign = sk2_const.TEXT_VALIGN_BOTTOM
		else:
			self.dc.text_valign = sk2_const.TEXT_VALIGN_TOP

		self.dc.text_rtl = False
		if mode & wmfconst.TA_RTLREADING:self.dc.text_rtl = True

	def tr_select_object(self, chunk):
		obj = None
		idx = get_data('<h', chunk)[0]
		if idx < len(self.gdiobjects):
			obj = self.gdiobjects[idx]
		if obj:
			if obj[0] == 'stroke':
				self.set_stroke_style(deepcopy(obj[1]))
			elif obj[0] == 'fill':
				self.set_fill_style(deepcopy(obj[1]))
			elif obj[0] == 'font':
				self.set_font_style(deepcopy(obj[1]))

	def tr_delete_object(self, chunk):
		idx = get_data('<h', chunk)[0]
		if idx < len(self.gdiobjects):
			self.gdiobjects[idx] = None

	def tr_create_pen_in(self, chunk):
		stroke = []
		style, width, reserved, r, g, b = get_data('<hhhBBBx', chunk)
		if not style & 0x000F == wmfconst.PS_NULL:
			stroke_rule = sk2_const.STROKE_MIDDLE
			color_vals = [r / 255.0, g / 255.0, b / 255.0]
			color = [uc2const.COLOR_RGB, color_vals, 1.0, '']
			stroke_width = abs(width * self.get_trafo()[0])
			if stroke_width < 1.0:stroke_width = 1.0


			stroke_linecap = sk2_const.CAP_ROUND
			cap = style & 0x0F00
			for item in SK2_CAPS.keys():
				if cap == item: stroke_linecap = SK2_CAPS[item]

			stroke_linejoin = sk2_const.JOIN_MITER
			join = style & 0xF000
			for item in SK2_JOIN.keys():
				if join == item: stroke_linejoin = SK2_JOIN[item]

			dashes = []
			dash = style & 0x000F
			for item in wmfconst.META_DASHES.keys():
				if dash == item: dashes = [] + wmfconst.META_DASHES[item]

			stroke_miterlimit = 9.0

			stroke = [stroke_rule, stroke_width, color, dashes,
						stroke_linecap, stroke_linejoin,
						stroke_miterlimit, 0, 1, []]
		self.add_gdiobject(('stroke', stroke))

	def tr_create_brush_in(self, chunk):
		fill = []
		style, r, g, b, hatch = get_data('<hBBBxh', chunk)
		color_vals = [r / 255.0, g / 255.0, b / 255.0]
		color = [uc2const.COLOR_RGB, color_vals, 1.0, '']
		if style == wmfconst.BS_SOLID:
			fill = [sk2_const.FILL_EVENODD, sk2_const.FILL_SOLID, color]
		elif style == wmfconst.BS_HATCHED:
			if not hatch in wmf_hatches.WMF_HATCHES:
				hatch = wmfconst.HS_HORIZONTAL
			ptrn = wmf_hatches.WMF_HATCHES[hatch]
			ptrn_type = sk2_const.PATTERN_IMG

			bgcolor = [uc2const.COLOR_RGB, [] + self.dc.bgcolor, 1.0, '']
			ptrn_style = [color, bgcolor]

			ptrn_trafo = [] + sk2_const.NORMAL_TRAFO
			ptrn_transf = [] + sk2_const.PATTERN_TRANSFORMS
			pattern = [ptrn_type, ptrn, ptrn_style, ptrn_trafo, ptrn_transf]
			fill = [sk2_const.FILL_EVENODD, sk2_const.FILL_PATTERN, pattern]
		self.add_gdiobject(('fill', fill))

	def tr_create_font_in(self, chunk):
		h, w, esc, ornt, weight = get_data('<hhhhh', chunk[:10])
		size = round(abs(self.coef * h), 1) * .7
		if not size: size = 12.0
		if size < 5.0: size = 5.0
		fl_b = weight >= 500
		fl_i, fl_u, fl_s, charset, op, cp, ql, pf = get_data('<BBBBBBBB',
																chunk[10:18])
		fl_i = fl_i == wmfconst.META_TRUE
		fl_u = fl_u == wmfconst.META_TRUE
		fl_s = fl_s == wmfconst.META_TRUE

		if charset in wmfconst.META_CHARSETS:
			charset = wmfconst.META_CHARSETS[charset]
		else:
			charset = wmfconst.META_CHARSETS[wmfconst.ANSI_CHARSET]

		fontface = wmflib.parse_nt_string(chunk[18:]).encode('utf-8')
		font_family = 'Sans'
		if fontface in libpango.get_fonts()[0]: font_family = fontface

		font = (font_family, size, fl_b, fl_i, fl_u, fl_s, esc / 10.0, charset)
		self.add_gdiobject(('font', font))

	def tr_dibcreate_pat_brush(self, chunk):
		# style, colorusage = get_data('<hh', chunk[:4])
		imagestr = wmflib.dib_to_imagestr(chunk[4:])
		bitsperpixel = get_data('<h', chunk[18:20])[0]

		ptrn, flag = libimg.read_pattern(imagestr)

		ptrn_type = sk2_const.PATTERN_TRUECOLOR
		if flag or bitsperpixel == 1: ptrn_type = sk2_const.PATTERN_IMG
		ptrn_style = [deepcopy(sk2_const.RGB_BLACK),
					deepcopy(sk2_const.RGB_WHITE)]
		ptrn_trafo = [] + sk2_const.NORMAL_TRAFO
		ptrn_transf = [] + sk2_const.PATTERN_TRANSFORMS

		pattern = [ptrn_type, ptrn, ptrn_style, ptrn_trafo, ptrn_transf]
		fill = [sk2_const.FILL_EVENODD, sk2_const.FILL_PATTERN, pattern]
		self.add_gdiobject(('fill', fill))

	def tr_create_noop(self, chunk):
		self.add_gdiobject(('ignore', None))

	def tr_moveto(self, chunk):
		y, x = get_data('<hh', chunk)
		self.set_curpoint([x, y])

	def tr_lineto(self, chunk):
		y, x = get_data('<hh', chunk)
		p = [x, y]
		paths = [[self.get_curpoint(), [p, ], sk2_const.CURVE_OPENED], ]
		self.set_curpoint([] + p)

		cfg = self.layer.config
		sk2_style = self.get_style()
		sk2_style[0] = []
		curve = sk2_model.Curve(cfg, self.layer, paths,
							self.get_trafo(), sk2_style)
		self.layer.childs.append(curve)

	def tr_ellipse(self, chunk):
		bottom, right, top, left = get_data('<hhhh', chunk)
		left, top = apply_trafo_to_point([left, top], self.get_trafo())
		right, bottom = apply_trafo_to_point([right, bottom], self.get_trafo())

		cfg = self.layer.config
		sk2_style = self.get_style()
		rect = [left, top, right - left, bottom - top]
		ellipse = sk2_model.Circle(cfg, self.layer, rect, style=sk2_style)
		self.layer.childs.append(ellipse)

	def tr_arc(self, chunk, arc_type=sk2_const.ARC_ARC):
		ye, xe, ys, xs, bottom, right, top, left = get_data('<hhhhhhhh',
																chunk)
		left, top = apply_trafo_to_point([left, top], self.get_trafo())
		right, bottom = apply_trafo_to_point([right, bottom], self.get_trafo())
		xs, ys = apply_trafo_to_point([xs, ys], self.get_trafo())
		xe, ye = apply_trafo_to_point([xe, ye], self.get_trafo())

		if left != right and top != bottom:
			t = [(right - left) / 2, 0, 0, (bottom - top) / 2,
						(right + left) / 2, (top + bottom) / 2]
			t = libgeom.invert_trafo(t)
			xs, ys = apply_trafo_to_point([xs, ys], t)
			xe, ye = apply_trafo_to_point([xe, ye], t)
			end_angle = libgeom.get_point_angle([xs, ys], [0.0, 0.0])
			start_angle = libgeom.get_point_angle([xe, ye], [0.0, 0.0])
		else:
			start_angle = end_angle = 0.0

		cfg = self.layer.config
		sk2_style = self.get_style()
		if arc_type == sk2_const.ARC_ARC: sk2_style[0] = []
		rect = [left, top, right - left, bottom - top]
		ellipse = sk2_model.Circle(cfg, self.layer, rect, start_angle,
								end_angle, arc_type, sk2_style)
		self.layer.childs.append(ellipse)

	def tr_chord(self, chunk):
		self.tr_arc(chunk, sk2_const.ARC_CHORD)

	def tr_pie(self, chunk):
		self.tr_arc(chunk, sk2_const.ARC_PIE_SLICE)

	def tr_rectangle(self, chunk):
		bottom, right, top, left = get_data('<hhhh', chunk)
		left, top = apply_trafo_to_point([left, top], self.get_trafo())
		right, bottom = apply_trafo_to_point([right, bottom], self.get_trafo())

		cfg = self.layer.config
		sk2_style = self.get_style()
		rect = [left, top, right - left, bottom - top]
		rect = sk2_model.Rectangle(cfg, self.layer, rect, style=sk2_style)
		self.layer.childs.append(rect)

	def tr_round_rectangle(self, chunk):
		eh, ew, bottom, right, top, left = get_data('<hhhhhh', chunk)
		corners = 4 * [0.0, ]
		if eh and ew:
			coef = max(ew / abs(right - left), eh / abs(bottom - top))
			corners = 4 * [coef, ]
		left, top = apply_trafo_to_point([left, top], self.get_trafo())
		right, bottom = apply_trafo_to_point([right, bottom], self.get_trafo())

		cfg = self.layer.config
		sk2_style = self.get_style()
		rect = [left, top, right - left, bottom - top]
		rect = sk2_model.Rectangle(cfg, self.layer, rect,
								style=sk2_style, corners=corners)
		self.layer.childs.append(rect)

	def tr_polygon(self, chunk):
		pointnum = unpack('<h', chunk[:2])[0]
		points = []
		for i in range(pointnum):
			x, y = get_data('<hh', chunk[2 + i * 4:6 + i * 4])
			points.append([float(x), float(y)])
		if not points[0] == points[-1]:points.append([] + points[0])
		if len(points) < 3: return
		paths = [[points[0], points[1:], sk2_const.CURVE_CLOSED], ]

		cfg = self.layer.config
		sk2_style = self.get_style()
		curve = sk2_model.Curve(cfg, self.layer, paths,
							self.get_trafo(), sk2_style)
		self.layer.childs.append(curve)

	def tr_polypolygon(self, chunk):
		polygonnum = unpack('<H', chunk[:2])[0]
		pointnums = []
		pos = 2
		for i in range(polygonnum):
			pointnums.append(unpack('<h', chunk[pos:pos + 2])[0])
			pos += 2
		paths = []
		for pointnum in pointnums:
			points = []
			for i in range(pointnum):
				x, y = get_data('<hh', chunk[pos:4 + pos])
				points.append([float(x), float(y)])
				pos += 4
			if not points[0] == points[-1]:points.append([] + points[0])
			paths.append([points[0], points[1:], sk2_const.CURVE_CLOSED])
		if not paths: return

		cfg = self.layer.config
		sk2_style = self.get_style()
		curve = sk2_model.Curve(cfg, self.layer, paths,
							self.get_trafo(), sk2_style)
		self.layer.childs.append(curve)

	def tr_polyline(self, chunk):
		pointnum = unpack('<h', chunk[:2])[0]
		points = []
		for i in range(pointnum):
			x, y = get_data('<hh', chunk[2 + i * 4:6 + i * 4])
			points.append([float(x), float(y)])
		if len(points) < 2: return
		paths = [[points[0], points[1:], sk2_const.CURVE_OPENED], ]

		cfg = self.layer.config
		sk2_style = self.get_style()
		sk2_style[0] = []
		curve = sk2_model.Curve(cfg, self.layer, paths,
							self.get_trafo(), sk2_style)
		self.layer.childs.append(curve)

	def tr_textout(self, chunk):
		length = unpack('<h', chunk[:2])[0]

		encoding = self.get_encoding()
		txt = chunk[8:8 + length].decode(encoding)
		txt_length = len(txt)
		txt = txt.encode('utf-8')
		y, x, = get_data('<hhhh', chunk[8 + length:16 + length])
		p = apply_trafo_to_point([x, y], self.get_trafo())

		cfg = self.layer.config
		sk2_style, tags = self.get_text_style()
		markup = [[tags, (0, txt_length)]]
		tr = [] + libgeom.NORMAL_TRAFO
		text = sk2_model.Text(cfg, self.layer, p, txt, -1, tr, sk2_style)
		text.markup = markup
		if self.dc.opacity:
			bg_style = [[], [], [], []]
			clr = [] + self.dc.bgcolor
			clr = [uc2const.COLOR_RGB, clr, 1.0, '', '']
			bg_style[0] = [sk2_const.FILL_EVENODD, sk2_const.FILL_SOLID, clr]
			text.update()
			bbox = [] + text.cache_bbox
			rect = bbox[:2] + [bbox[2] - bbox[0], bbox[3] - bbox[1]]
			rect = sk2_model.Rectangle(cfg, self.layer, rect, style=bg_style)
			self.layer.childs.append(rect)
		if self.dc.font[-2]:
			tr = libgeom.trafo_rotate_grad(self.dc.font[-2], p[0], p[1])
			text.trafo = libgeom.multiply_trafo(text.trafo, tr)
			if self.dc.opacity:
				rect.trafo = libgeom.multiply_trafo(rect.trafo, tr)
		self.layer.childs.append(text)

	def tr_exttextout(self, chunk):
		y, x, length, fwopts = get_data('<hhhh', chunk[:8])
		dl = 0
		if length % 2:
			length += 1
			dl += 1
		p = apply_trafo_to_point([x, y], self.get_trafo())

		encoding = self.get_encoding()
		pos = 8
		if not len(chunk) - 8 == length:pos = 16
		txt = chunk[pos:pos + length - dl].decode(encoding)
		txt_length = len(txt)
		txt = txt.encode('utf-8')

		cfg = self.layer.config
		sk2_style, tags = self.get_text_style()
		markup = [[tags, (0, txt_length)]]
		tr = [] + libgeom.NORMAL_TRAFO

		text = sk2_model.Text(cfg, self.layer, p, txt, -1, tr, sk2_style)
		text.markup = markup
		if self.dc.opacity:
			bg_style = [[], [], [], []]
			clr = [] + self.dc.bgcolor
			clr = [uc2const.COLOR_RGB, clr, 1.0, '', '']
			bg_style[0] = [sk2_const.FILL_EVENODD, sk2_const.FILL_SOLID, clr]
			text.update()
			bbox = [] + text.cache_bbox
			rect = bbox[:2] + [bbox[2] - bbox[0], bbox[3] - bbox[1]]
			rect = sk2_model.Rectangle(cfg, self.layer, rect, style=bg_style)
			rect.trafo = tr
			self.layer.childs.append(rect)
		if self.dc.font[-2]:
			tr = libgeom.trafo_rotate_grad(self.dc.font[-2], p[0], p[1])
			text.trafo = libgeom.multiply_trafo(text.trafo, tr)
			if self.dc.opacity:
				rect.trafo = libgeom.multiply_trafo(rect.trafo, tr)
		self.layer.childs.append(text)

	def _draw_point(self, point):
		style = [[], [], [], []]
		clr = [] + sk2_const.RGB_BLACK
		clr[1] = [1.0, 0.0, 0.0]
		style[0] = [sk2_const.FILL_EVENODD, sk2_const.FILL_SOLID, clr]
		rect = point + [3.0, 3.0]
		rect = sk2_model.Rectangle(self.layer.config, self.layer,
								rect, style=style)
		self.layer.childs.append(rect)

	def tr_stretch_dib(self, chunk):
		src_h, src_w, = get_data('<hh', chunk[6:10])
		dst_h, dst_w, dst_y, dst_x = get_data('<hhhh', chunk[14:22])
		imagestr = wmflib.dib_to_imagestr(chunk[22:])

		tr = self.get_trafo()
		p0 = apply_trafo_to_point([dst_x, dst_y], tr)
		p1 = apply_trafo_to_point([dst_w + dst_x, dst_h + dst_y], tr)
		w = abs(p1[0] - p0[0])
		h = abs(p1[1] - p0[1])
		trafo = [w / src_w, 0.0, 0.0, h / src_h, p0[0], p0[1] - h]

		pixmap = sk2_model.Pixmap(self.layer.config)

		libimg.set_image_data(self.sk2_doc.cms, pixmap, imagestr)
		pixmap.trafo = trafo
		self.layer.childs.append(pixmap)


class SK2_to_WMF_Translator(object):

	def translate(self, sk2_doc, wmf_doc):
		self.wmf_doc = wmf_doc
		self.sk2_doc = sk2_doc
		self.wmf_mt = wmf_doc.model
		self.sk2_mt = sk2_doc.model
		self.sk2_mtds = sk2_doc.methods
		self.trafo = [1.0, 0.0, 0.0, -1.0, 0.0, 0.0]
