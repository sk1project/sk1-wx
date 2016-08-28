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

from uc2 import uc2const, libimg
from uc2.formats.sk2.crenderer import CairoRenderer

from sk1.appconst import PAGEFIT, ZOOM_IN, ZOOM_OUT
from kbd_proc import Kbd_Processor

CAIRO_BLACK = [0.0, 0.0, 0.0]
CAIRO_GRAY = [0.0, 0.0, 0.0, 0.5]
CAIRO_WHITE = [1.0, 1.0, 1.0]
CAIRO_RED = [1.0, 0.0, 0.0]

class PreviewRenderer(CairoRenderer):

	colorspace = uc2const.COLOR_RGB

	def __init__(self, cms):
		CairoRenderer.__init__(self, cms)

	def set_colorspace(self, cs=uc2const.COLOR_RGB):
		if not cs == self.colorspace:
			self.colorspace = cs

	def get_color(self, color):
		if self.colorspace == uc2const.COLOR_RGB:
			r, g, b = self.cms.get_display_color(color)
		elif self.colorspace == uc2const.COLOR_CMYK:
			cmyk_color = self.cms.get_cmyk_color(color)
			r, g, b = self.cms.get_display_color(cmyk_color)
		else:
			gc = self.cms.get_grayscale_color(color)
			r, g, b = self.cms.get_display_color(gc)
		return r, g, b, color[2]

	def get_image(self, pixmap):
		if self.colorspace == uc2const.COLOR_RGB:
			if not pixmap.cache_cdata:
				proofing = self.cms.proofing
				self.cms.proofing = False
				libimg.update_image(self.cms, pixmap)
				self.cms.proofing = proofing
			return pixmap.cache_cdata
		elif self.colorspace == uc2const.COLOR_CMYK:
			if not pixmap.cache_ps_cdata:
				libimg.update_image(self.cms, pixmap, True)
				pixmap.cache_ps_cdata = pixmap.cache_cdata
				pixmap.cache_cdata = None
			return pixmap.cache_ps_cdata
		else:
			if not pixmap.cache_gray_cdata:
				libimg.update_gray_image(self.cms, pixmap)
			return pixmap.cache_gray_cdata

	def get_pattern_image(self, obj):
		if self.colorspace == uc2const.COLOR_RGB:
			if not obj.cache_pattern_img:
				image_obj = self._create_pattern_image(obj)
				obj.cache_pattern_img = image_obj.cache_cdata
			return obj.cache_pattern_img
		elif self.colorspace == uc2const.COLOR_CMYK:
			if not obj.cache_ps_pattern_img:
				image_obj = self._create_pattern_image(obj, force_proofing=True)
				obj.cache_ps_pattern_img = image_obj.cache_cdata
			return obj.cache_ps_pattern_img
		else:
			if not obj.cache_gray_pattern_img:
				image_obj = self._create_pattern_image(obj, gray=True)
				obj.cache_gray_pattern_img = image_obj.cache_gray_cdata
			return obj.cache_gray_pattern_img


class PreviewCanvas(wal.Panel, wal.SensitiveCanvas):

	printer = None
	printout = None
	renderer = None
	pages = []
	page_index = 0

	hscroll = None
	vscroll = None
	hruler = None
	vruler = None
	pager = None

	workspace = ()
	matrix = None
	trafo = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
	zoom = 1.0
	zoom_stack = []
	width = 0
	height = 0

	my_changes = False

	def __init__(self, parent, dlg, printer, printout):
		self.dlg = dlg
		self.printer = printer
		self.printout = printout
		self.zoom_stack = []
		wal.Panel.__init__(self, parent, allow_input=True)
		self.kbdproc = Kbd_Processor(self)
		wal.SensitiveCanvas.__init__(self, True)
		self.set_bg(wal.GRAY)
		self.pages = self.printout.get_print_pages()
		self.renderer = PreviewRenderer(self.printout.get_cms())

	def destroy(self):
		items = self.__dict__.keys()
		for item in items:
			self.__dict__[item] = None

	#----- Paging

	def next_page(self):
		if not self.page_index >= len(self.pages) - 1:
			self.page_index += 1
		self.update_page()

	def previous_page(self):
		if self.page_index:
			self.page_index -= 1
		self.update_page()

	def set_page(self, index):
		if index >= 0 and index <= len(self.pages) - 1:
			self.page_index = index
		self.update_page()

	def update_page(self):
		self.pager.set_value(self.page_index + 1)
		self.refresh()

	#----- Mouse control

	def mouse_left_up(self, point):
		self.set_focus()

	def mouse_right_up(self, point):
		self.set_focus()

	#----- SCROLLING

	def set_ctrls(self, hscroll, vscroll, hruler, vruler, pager):
		self.hscroll = hscroll
		self.vscroll = vscroll
		self.hruler = hruler
		self.vruler = vruler
		self.pager = pager
		self.hscroll.set_scrollbar(500, 100, 1100, 100)
		self.vscroll.set_scrollbar(500, 100, 1100, 100)

	def _scrolling(self, *args):
		if self.my_changes:return
		xpos = self.hscroll.get_thumb_pos() / 1000.0
		ypos = (1000 - self.vscroll.get_thumb_pos()) / 1000.0
		x = (xpos - 0.5) * self.workspace[0]
		y = (ypos - 0.5) * self.workspace[1]
		center = self.doc_to_win((x, y))
		self._set_center(center)
		self.refresh()

	def update_scrolls(self):
		if not self.vscroll: return
		self.my_changes = True
		self.set_workspace()
		center = self._get_center()
		x = (center[0] + self.workspace[0] / 2.0) / self.workspace[0]
		y = (center[1] + self.workspace[1] / 2.0) / self.workspace[1]
		hscroll = int(1000 * x)
		vscroll = int(1000 - 1000 * y)
		self.hscroll.set_scrollbar(hscroll, 100, 1100, 100)
		self.vscroll.set_scrollbar(vscroll, 100, 1100, 100)
		self.vruler.refresh()
		self.hruler.refresh()
		self.my_changes = False

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

	def _zoom(self, dzoom=1.0):
		m11, m12, m21, m22, dx, dy = self.trafo
		_dx = (self.width * dzoom - self.width) / 2.0
		_dy = (self.height * dzoom - self.height) / 2.0
		dx = dx * dzoom - _dx
		dy = dy * dzoom - _dy
		self.trafo = [m11 * dzoom, m12, m21, m22 * dzoom, dx, dy]
		self.zoom_stack.append([] + self.trafo)
		self.matrix = cairo.Matrix(*self.trafo)
		self.zoom = m11 * dzoom
		self.update_scrolls()
		self.refresh()

	def zoom_in(self):
		self._zoom(ZOOM_IN)

	def zoom_out(self):
		self._zoom(ZOOM_OUT)

	def zoom_100(self):
		self._zoom(1.0 / self.zoom)

	def zoom_fit_to_page(self):
		self._fit_to_page()
		self.refresh()

	#---Canvas math

	def get_page_size(self):
		return self.printer.get_page_size()

	def _get_center(self):
		x = self.width / 2.0
		y = self.height / 2.0
		return self.win_to_doc((x, y))

	def _set_center(self, center):
		x, y = center
		_dx = self.width / 2.0 - x
		_dy = self.height / 2.0 - y
		m11, m12, m21, m22, dx, dy = self.trafo
		dx += _dx
		dy += _dy
		self.trafo = [m11, m12, m21, m22, dx, dy]
		self.matrix = cairo.Matrix(m11, m12, m21, m22, dx, dy)
		self.update_scrolls()

	def set_workspace(self):
		size = max(self.printer.get_page_size()) * 1.2
		self.workspace = (size, size)

	def doc_to_win(self, point=[0.0, 0.0]):
		x, y = point
		m11 = self.trafo[0]
		m22, dx, dy = self.trafo[3:]
		x_new = m11 * x + dx
		y_new = m22 * y + dy
		return [x_new, y_new]

	def win_to_doc(self, point=[0, 0]):
		x, y = point
		x = float(x)
		y = float(y)
		m11 = self.trafo[0]
		m22, dx, dy = self.trafo[3:]
		x_new = (x - dx) / m11
		y_new = (y - dy) / m22
		return [x_new, y_new]

	def point_doc_to_win(self, point=[0.0, 0.0]):
		if not point:return []
		if len(point) == 2:
			return self.doc_to_win(point)
		else:
			return [self.doc_to_win(point[0]),
				self.doc_to_win(point[1]),
				self.doc_to_win(point[2]), point[3]]

	def point_win_to_doc(self, point=[0.0, 0.0]):
		if not point:return []
		if len(point) == 2:
			return self.win_to_doc(point)
		else:
			return [self.win_to_doc(point[0]),
				self.win_to_doc(point[1]),
				self.win_to_doc(point[2]), point[3]]

	#---PAINTING

	def paint(self):
		if not self.matrix: self._fit_to_page()
		self.renderer.set_colorspace(self.printer.colorspace)
		self._keep_center()
		w, h = self.get_size()
		surface = cairo.ImageSurface(cairo.FORMAT_RGB24, w, h)
		self.ctx = cairo.Context(surface)
		self.ctx.set_source_rgb(*wal.wxcolor_to_dec(wal.GRAY))
		self.ctx.paint()
		self.ctx.set_matrix(self.matrix)

		self._draw_page()
		self._render_page()
		self._draw_page_border()

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
		self.ctx.set_antialias(cairo.ANTIALIAS_DEFAULT)

	def _draw_page_border(self):
		self.ctx.set_antialias(cairo.ANTIALIAS_NONE)
		w, h = self.printer.get_page_size()
		self.ctx.rectangle(-w / 2.0, -h / 2.0, w, h)
		self.ctx.set_source_rgb(*CAIRO_BLACK)
		self.ctx.stroke()
		self.ctx.set_antialias(cairo.ANTIALIAS_DEFAULT)

	def _render_page(self):
		self.ctx.save()
		w, h = self.printer.get_page_size()
		t, r, b, l = self.printer.margins
		rect = (-w / 2.0 + l, -h / 2.0 + b, w - l - r, h - t - b)
		self.ctx.rectangle(*rect)
		self.ctx.clip()

		groups = self.pages[self.page_index].childs
		for group in groups:
			self.renderer.render(self.ctx, group.childs)

		self.ctx.restore()
		self.ctx.set_antialias(cairo.ANTIALIAS_NONE)
		self.ctx.set_source_rgb(*CAIRO_RED)
		width = 1.0 / self.zoom
		self.ctx.set_line_width(1.0 / self.zoom)
		self.ctx.set_dash([3 * width, 3 * width])
		self.ctx.rectangle(*rect)
		self.ctx.stroke()
		self.ctx.set_dash([])
		self.ctx.set_antialias(cairo.ANTIALIAS_DEFAULT)





