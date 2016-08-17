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

import cairo
import wal

from sk1 import _, config
from sk1.resources import icons
from sk1.appconst import PAGEFIT, ZOOM_IN, ZOOM_OUT

CAIRO_BLACK = [0.0, 0.0, 0.0]
CAIRO_GRAY = [0.0, 0.0, 0.0, 0.5]
CAIRO_WHITE = [1.0, 1.0, 1.0]

class PreviewCanvas(wal.Panel, wal.SensitiveCanvas):

	printer = None
	printout = None

	matrix = None
	trafo = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
	zoom = 1.0
	zoom_stack = []
	width = 0
	height = 0

	def __init__(self, parent, printer, printout):
		self.printer = printer
		self.printout = printout
		wal.Panel.__init__(self, parent)
		wal.SensitiveCanvas.__init__(self, True)
		self.set_bg(wal.GRAY)

	#----- SCROLLING

	def update_scrolls(self):pass

	#----- ZOOMING

	def _fit_to_page(self):
		width, height = self.printer.get_page_size()
		w, h = self.get_size()
		w = float(w)
		h = float(h)
		self.width = w
		self.height = h
		zoom = min(w / width, h / height) * PAGEFIT
		dx = w / 2.0
		dy = h / 2.0
		self.trafo = [zoom, 0, 0, -zoom, dx, dy]
		self.zoom_stack.append([] + self.trafo)
		self.matrix = cairo.Matrix(zoom, 0, 0, -zoom, dx, dy)
		self.zoom = zoom
		self.update_scrolls()

	def _keep_center(self):
		w, h = self.get_size()
		w = float(w)
		h = float(h)
		if not w == self.width or not h == self.height:
			_dx = (w - self.width) / 2.0
			_dy = (h - self.height) / 2.0
			m11, m12, m21, m22, dx, dy = self.trafo
			dx += _dx
			dy += _dy
			self.trafo = [m11, m12, m21, m22, dx, dy]
			self.matrix = cairo.Matrix(m11, m12, m21, m22, dx, dy)
			self.width = w
			self.height = h
			self.update_scrolls()

	def zoom_fit_to_page(self):
		self._fit_to_page()
		self.refresh()

	def paint(self):
		if not self.matrix: self._fit_to_page()
		self._keep_center()
		w, h = self.get_size()
		surface = cairo.ImageSurface(cairo.FORMAT_RGB24, w, h)
		self.ctx = cairo.Context(surface)
		self.ctx.set_source_rgb(*wal.wxcolor_to_dec(wal.GRAY))
		self.ctx.paint()
		self.ctx.set_matrix(self.matrix)

		self._draw_page()

		self.draw_bitmap(wal.copy_surface_to_bitmap(surface))

	def _draw_page(self):
		self.ctx.set_line_width(1.0 / self.zoom)
		offset = 5.0 / self.zoom
		w, h = self.printer.get_page_size()

		#---Page shadow
		self.ctx.rectangle(-w / 2.0 + offset, -h / 2.0 - offset, w, h)
		self.ctx.set_source_rgba(*CAIRO_GRAY)
		self.ctx.fill()

		#---Page
		self.ctx.set_antialias(cairo.ANTIALIAS_NONE)
		self.ctx.rectangle(-w / 2.0, -h / 2.0, w, h)
		self.ctx.set_source_rgb(*CAIRO_WHITE)
		self.ctx.fill()

		self.ctx.rectangle(-w / 2.0, -h / 2.0, w, h)
		self.ctx.set_source_rgb(*CAIRO_BLACK)
		self.ctx.stroke()
		self.ctx.set_antialias(cairo.ANTIALIAS_DEFAULT)

