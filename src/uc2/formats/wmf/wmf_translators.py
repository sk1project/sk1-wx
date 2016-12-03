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

from uc2 import events, msgconst, uc2const, libgeom
from uc2.libgeom import multiply_trafo, apply_trafo_to_point
from uc2.formats.wmf import wmfconst
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

class DC_Data(object):

	style = [[], [], [], []]
	curpoint = [0.0, 0.0]
	trafo = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
	opacity = False
	bgcolor = [0.0, 0.0, 0.0]

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
						- self.coef * self.vwidth / 2.0,
						self.coef * self.vheight / 2.0]
		self.update_trafo()

		self.rec_funcs = {
			wmfconst.META_SETWINDOWORG:self.tr_set_window_org,
			wmfconst.META_SETWINDOWEXT:self.tr_set_window_ext,
			wmfconst.META_SETBKMODE:self.tr_set_bg_mode,
			wmfconst.META_SETBKCOLOR:self.tr_set_bg_color,
			wmfconst.META_SAVEDC:self.tr_save_dc,
			wmfconst.META_RESTOREDC: self.tr_restore_dc,

			wmfconst.META_CREATEPENINDIRECT:self.tr_create_pen_in,
			wmfconst.META_CREATEBRUSHINDIRECT:self.tr_create_brush_in,
			#---------
			wmfconst.META_CREATEFONTINDIRECT:self.tr_create_noop,
			wmfconst.META_CREATEPALETTE:self.tr_create_noop,
			wmfconst.META_CREATEPATTERNBRUSH:self.tr_create_noop,
			wmfconst.META_CREATEREGION:self.tr_create_noop,
			wmfconst.META_DIBCREATEPATTERNBRUSH:self.tr_create_noop,
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
			}

		self.translate_header(header)
		self.sk2_mt.do_update()

	def update_trafo(self):
		wt = [1.0, 0.0, 0.0, 1.0, -self.wx / 2.0, -self.wy / 2.0]
		vt = [1.0, 0.0, 0.0, 1.0, self.vx / 2.0, self.vy / 2.0]
		scale = [float(self.vwidth) / self.wwidth, 0.0, 0.0,
			float(self.vheight) / self.wheight, 0.0, 0.0]
		tr = multiply_trafo(multiply_trafo(wt, scale), vt)
		self.set_trafo(multiply_trafo(tr, self.base_trafo))

	def get_size_pt(self, val): return val * self.coef
	def noop(self, *args):pass
	def get_data(self, fmt, chunk): return unpack(fmt, chunk)

	def get_style(self): return deepcopy(self.dc.style)
	def set_fill_style(self, fill): self.dc.style[0] = fill
	def set_stroke_style(self, stroke): self.dc.style[1] = stroke
	def get_curpoint(self): return [] + self.dc.curpoint
	def set_curpoint(self, point): self.dc.curpoint = [] + point
	def get_trafo(self): return [] + self.dc.trafo
	def set_trafo(self, trafo): self.dc.trafo = [] + trafo

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
		self.wy, self.wx = self.get_data('<hh', chunk)
		self.update_trafo()

	def tr_set_window_ext(self, chunk):
		self.wheight, self.wwidth = self.get_data('<hh', chunk)
		self.update_trafo()

	def tr_save_dc(self):
		self.dcstack.append(deepcopy(self.dc))

	def tr_restore_dc(self):
		if self.dcstack:
			self.dc = self.dcstack[-1]
			self.dcstack = self.dcstack[:-1]

	def tr_set_bg_mode(self, chunk):
		mode = self.get_data('<h', chunk[:2])[0]
		self.dc.opacity = mode == wmfconst.OPAQUE

	def tr_set_bg_color(self, chunk):
		r, g, b = self.get_data('<BBBx', chunk)[0]
		self.dc.bgcolor = [r / 255.0, g / 255.0, b / 255.0]

	def tr_select_object(self, chunk):
		obj = None
		idx = self.get_data('<h', chunk)[0]
		if idx < len(self.gdiobjects):
			obj = self.gdiobjects[idx]
		if obj:
			if obj[0] == 'stroke':
				self.set_stroke_style(deepcopy(obj[1]))
			elif obj[0] == 'fill':
				self.set_fill_style(deepcopy(obj[1]))

	def tr_delete_object(self, chunk):
		idx = self.get_data('<h', chunk)[0]
		if idx < len(self.gdiobjects):
			self.gdiobjects[idx] = None

	def tr_create_pen_in(self, chunk):
		stroke = []
		style, width, reserved, r, g, b = self.get_data('<hhhBBBx', chunk)
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
		style, r, g, b, hatch = self.get_data('<hBBBxh', chunk)
		if not style == 1:
			color_vals = [r / 255.0, g / 255.0, b / 255.0]
			color = [uc2const.COLOR_RGB, color_vals, 1.0, '']
			fill = [sk2_const.FILL_EVENODD, sk2_const.FILL_SOLID, color]
		self.add_gdiobject(('fill', fill))

	def tr_create_noop(self, chunk):
		self.add_gdiobject(('ignore', None))

	def tr_moveto(self, chunk):
		y, x = self.get_data('<hh', chunk)
		self.set_curpoint([x, y])

	def tr_lineto(self, chunk):
		y, x = self.get_data('<hh', chunk)
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
		bottom, right, top, left = self.get_data('<hhhh', chunk)
		left, top = apply_trafo_to_point([left, top], self.get_trafo())
		right, bottom = apply_trafo_to_point([right, bottom], self.get_trafo())

		cfg = self.layer.config
		sk2_style = self.get_style()
		rect = [left, top, right - left, bottom - top]
		ellipse = sk2_model.Circle(cfg, self.layer, rect, style=sk2_style)
		self.layer.childs.append(ellipse)

	def tr_arc(self, chunk, arc_type=sk2_const.ARC_ARC):
		ye, xe, ys, xs, bottom, right, top, left = self.get_data('<hhhhhhhh', chunk)
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
		bottom, right, top, left = self.get_data('<hhhh', chunk)
		left, top = apply_trafo_to_point([left, top], self.get_trafo())
		right, bottom = apply_trafo_to_point([right, bottom], self.get_trafo())

		cfg = self.layer.config
		sk2_style = self.get_style()
		rect = [left, top, right - left, bottom - top]
		rect = sk2_model.Rectangle(cfg, self.layer, rect, style=sk2_style)
		self.layer.childs.append(rect)

	def tr_round_rectangle(self, chunk):
		eh, ew, bottom, right, top, left = self.get_data('<hhhhhh', chunk)
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
			x, y = self.get_data('<hh', chunk[2 + i * 4:6 + i * 4])
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
				x, y = self.get_data('<hh', chunk[pos:4 + pos])
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
			x, y = self.get_data('<hh', chunk[2 + i * 4:6 + i * 4])
			points.append([float(x), float(y)])
		if len(points) < 2: return
		paths = [[points[0], points[1:], sk2_const.CURVE_OPENED], ]

		cfg = self.layer.config
		sk2_style = self.get_style()
		sk2_style[0] = []
		curve = sk2_model.Curve(cfg, self.layer, paths,
							self.get_trafo(), sk2_style)
		self.layer.childs.append(curve)

class SK2_to_WMF_Translator(object):

	def translate(self, sk2_doc, wmf_doc):pass
