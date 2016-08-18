# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2016 by Igor E. Novikov
#
# 	This program is free software: you can redistribute it and/or modify
# 	it under the terms of the GNU General Public License as published by
# 	the Free Software Foundation, either version 3 of the License, or
# 	(at your option) any later version.
#
# 	This program is distributed in the hope that it will be useful,
# 	but WITHOUT ANY WARRANTY; without even the implied warranty of
# 	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# 	GNU General Public License for more details.
#
# 	You should have received a copy of the GNU General Public License
# 	along with this program.  If not, see <http://www.gnu.org/licenses/>.

import math
import wal
import cairo

from uc2 import cms, uc2const

from sk1 import config
from sk1.resources import icons, get_icon
from sk1.document.ruler import VFONT, HFONT

class PreviewCorner(wal.HPanel, wal.Canvas):

	icon = None

	def __init__(self, parent):
		size = config.ruler_size
		wal.HPanel.__init__(self, parent)
		wal.Canvas.__init__(self)
		self.pack((size, size))
		self.set_bg(wal.WHITE)
		self.icon = get_icon(icons.ORIGIN_LL)

	def paint(self):
		w, h = self.get_size()
		self.set_stroke()
		self.set_fill(cms.val_255(config.ruler_bg))
		self.draw_rect(0, 0, w, h)

		stop_clr = cms.val_255(config.ruler_fg) + [255]
		start_clr = cms.val_255(config.ruler_fg) + [0]

		rect = (0, h - 1, w * 2, 1)
		self.gc_draw_linear_gradient(rect, start_clr, stop_clr)

		rect = (w - 1, 0, 1, h * 2)
		self.gc_draw_linear_gradient(rect, start_clr, stop_clr, True)

		shift = (w - 19) / 2 + 1
		self.draw_bitmap(self.icon, shift, shift)


class PreviewRuler(wal.HPanel, wal.Canvas):

	horizontal = True
	units = uc2const.UNIT_MM
	canvas = None
	surface = None
	ctx = None

	def __init__(self, parent, canvas, units=uc2const.UNIT_MM, horizontal=True):
		self.canvas = canvas
		self.units = units
		self.horizontal = horizontal
		size = config.ruler_size
		wal.HPanel.__init__(self, parent)
		wal.Canvas.__init__(self)
		self.pack((size, size))
		self.set_bg(wal.WHITE)

	def calc_ruler(self):
		canvas = self.canvas
		w, h = self.canvas.get_page_size()
		x = y = 0
		udx = udy = uc2const.unit_dict[self.units]
		x0, y0 = canvas.point_doc_to_win([-w / 2.0 + x, -h / 2.0 + y])
		dx = udx * canvas.zoom
		dy = udy * canvas.zoom
		sdist = config.snap_distance

		i = 0.0
		while dx < sdist + 3:
			i = i + 0.5
			dx = dx * 10.0 * i
		if dx / 2.0 > sdist + 3 and \
		dx / 2.0 > udx * canvas.zoom:
			dx = dx / 2.0

		i = 0.0
		while dy < sdist + 3:
			i = i + 0.5
			dy = dy * 10.0 * i
		if dy / 2.0 > sdist + 3 and \
		dy / 2.0 > udy * canvas.zoom:
			dy = dy / 2.0

		sx = (x0 / dx - math.floor(x0 / dx)) * dx
		sy = (y0 / dy - math.floor(y0 / dy)) * dy
		return (x0, y0, dx, dy, sx, sy)

	def get_ticks(self):
		canvas = self.canvas
		pw, ph = self.canvas.get_page_size()
		unit = uc2const.unit_dict[self.units]
		w, h = self.get_size()
		x0, y0, dx, dy, sx, sy = self.calc_ruler()
		small_ticks = []
		text_ticks = []

		if self.horizontal:
			i = -1
			pos = 0
			while pos < w:
				pos = sx + i * dx
				small_ticks.append(sx + i * dx)
				if dx > 10:small_ticks.append(pos + dx * .5)
				i += 1

			coef = round(50.0 / dx)
			if not coef:coef = 1.0
			dxt = dx * coef
			sxt = (x0 / dxt - math.floor(x0 / dxt)) * dxt

			float_flag = False
			unit_dx = dxt / (unit * canvas.zoom)
			if unit_dx < 1.0:float_flag = True

			i = -1
			pos = 0
			shift = pw / 2.0
			while pos < w:
				pos = sxt + i * dxt
				doc_pos = canvas.point_win_to_doc((pos, 0))[0] + shift
				doc_pos *= uc2const.point_dict[self.units]
				if float_flag:
					txt = str(round(doc_pos, 4))
					if not doc_pos:txt = '0'
				else:txt = str(int(round(doc_pos)))
				text_ticks.append((sxt + i * dxt, txt))
				i += 1

		else:
			i = -1
			pos = 0
			while pos < h:
				pos = sy + i * dy
				small_ticks.append(sy + i * dy)
				if dy > 10:small_ticks.append(pos + dy * .5)
				i += 1

			coef = round(50.0 / dy)
			if not coef:coef = 1.0
			dyt = dy * coef
			syt = (y0 / dyt - math.floor(y0 / dyt)) * dyt

			float_flag = False
			unit_dy = dyt / (unit * canvas.zoom)
			if unit_dy < 1.0:float_flag = True

			i = -1
			pos = 0
			shift = ph / 2.0
			while pos < h:
				pos = syt + i * dyt
				doc_pos = canvas.point_win_to_doc((0, pos))[1] + shift
				doc_pos *= uc2const.point_dict[self.units]
				if float_flag:
					txt = str(round(doc_pos, 4))
					if not doc_pos:txt = '0'
				else:txt = str(int(round(doc_pos)))
				text_ticks.append((syt + i * dyt, txt))
				i += 1
		return small_ticks, text_ticks

	def paint(self):
		w, h = self.get_size()
		shift = 0
		if wal.is_msw():shift = 1
		if self.surface is None:
			self.surface = cairo.ImageSurface(cairo.FORMAT_RGB24, w - shift, h - shift)
			self.width = w
			self.height = h
		elif self.width <> w or self.height <> h:
			self.surface = cairo.ImageSurface(cairo.FORMAT_RGB24, w - shift, h - shift)
			self.width = w
			self.height = h
		self.ctx = cairo.Context(self.surface)
		self.ctx.set_matrix(cairo.Matrix(1.0, 0.0, 0.0, 1.0, 0.0, 0.0))
		self.ctx.set_source_rgb(*config.ruler_bg)
		self.ctx.paint()
		self.ctx.set_antialias(cairo.ANTIALIAS_NONE)
		self.ctx.set_line_width(1.0)
		self.ctx.set_dash([])
		self.ctx.set_source_rgb(*config.ruler_fg)
		if self.horizontal: self.hrender(w, h)
		else: self.vrender(w, h)
		self.draw_bitmap(wal.copy_surface_to_bitmap(self.surface))

	def hrender(self, w, h):
		self.ctx.move_to(0, h)
		self.ctx.line_to(w, h)

		small_ticks, text_ticks = self.get_ticks()
		for item in small_ticks:
			self.ctx.move_to(item, h - config.ruler_small_tick)
			self.ctx.line_to(item, h - 1)

		for pos, txt in text_ticks:
			self.ctx.move_to(pos, h - config.ruler_large_tick)
			self.ctx.line_to(pos, h - 1)

		self.ctx.stroke()

		vshift = config.ruler_text_vshift
		hshift = config.ruler_text_hshift
		for pos, txt in text_ticks:
			for character in txt:
				data = HFONT[character]
				position = int(pos) + hshift
				self.ctx.set_source_surface(data[1], position, vshift)
				self.ctx.paint()
				pos += data[0]

	def vrender(self, w, h):
		self.ctx.move_to(w, 0)
		self.ctx.line_to(w, h)

		small_ticks, text_ticks = self.get_ticks()
		for item in small_ticks:
			self.ctx.move_to(w - config.ruler_small_tick, item)
			self.ctx.line_to(w - 1, item)

		for item, txt in text_ticks:
			self.ctx.move_to(w - config.ruler_large_tick, item)
			self.ctx.line_to(w - 1, item)

		self.ctx.stroke()

		vshift = config.ruler_text_vshift
		hshift = config.ruler_text_hshift
		for pos, txt in text_ticks:
			for character in txt:
				data = VFONT[character]
				position = int(pos) - data[0] - hshift
				self.ctx.set_source_surface(data[1], vshift, position)
				self.ctx.paint()
				pos -= data[0]
