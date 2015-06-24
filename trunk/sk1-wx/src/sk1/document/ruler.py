# -*- coding: utf-8 -*-
#
#	Copyright (C) 2013 by Igor E. Novikov
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

import os, math
import wx
import cairo

from uc2 import uc2const, cms
from uc2.formats.sk2.sk2_const import DOC_ORIGIN_CENTER, DOC_ORIGIN_LL, \
DOC_ORIGIN_LU, ORIGINS

from wal.const import HORIZONTAL, is_mac, is_msw
from wal import HPanel
from wal import copy_surface_to_bitmap

from sk1 import config, modes, events
from sk1.appconst import RENDERING_DELAY
from sk1.resources import get_icon, icons

HFONT = {}
VFONT = {}

def load_font():
	fntdir = 'ruler-font%dpx' % config.ruler_font_size
	fntdir = os.path.join(config.resource_dir, 'fonts', fntdir)
	for char in '.,-0123456789':
		if char in '.,': file_name = os.path.join(fntdir, 'hdot.png')
		else: file_name = os.path.join(fntdir, 'h%s.png' % char)
		surface = cairo.ImageSurface.create_from_png(file_name)
		HFONT[char] = (surface.get_width(), surface)

		if char in '.,': file_name = os.path.join(fntdir, 'vdot.png')
		else: file_name = os.path.join(fntdir, 'v%s.png' % char)
		surface = cairo.ImageSurface.create_from_png(file_name)
		VFONT[char] = (surface.get_height(), surface)

BITMAPS = {}

CAIRO_WHITE = [1.0, 1.0, 1.0]
CAIRO_BLACK = [0.0, 0.0, 0.0]

class RulerCorner(HPanel):

	bitmaps = {}
	presenter = None
	eventloop = None
	origin = DOC_ORIGIN_LL

	def __init__(self, presenter, parent):
		self.presenter = presenter
		self.eventloop = presenter.eventloop
		HPanel.__init__(self, parent)
		size = config.ruler_size
		if not BITMAPS:
			BITMAPS[DOC_ORIGIN_CENTER] = get_icon(icons.ORIGIN_CENTER)
			BITMAPS[DOC_ORIGIN_LL] = get_icon(icons.ORIGIN_LL)
			BITMAPS[DOC_ORIGIN_LU] = get_icon(icons.ORIGIN_LU)
		self.add((size, size))
		self.SetBackgroundColour(wx.WHITE)
		self.Bind(wx.EVT_PAINT, self._on_paint, self)
		self.eventloop.connect(self.eventloop.DOC_MODIFIED, self.changes)
		self.Bind(wx.EVT_LEFT_UP, self.left_click)
		events.connect(events.CONFIG_MODIFIED, self.check_config)
		self.changes()

	def check_config(self, attr, value):
		if attr == 'ruler_size':
			size = config.ruler_size
			self.remove_all()
			self.add((size, size))
			self.parent.layout()
		if attr[:6] == 'ruler_':
			self.refresh()

	def changes(self, *args):
		if not self.origin == self.presenter.model.doc_origin:
			self.origin = self.presenter.model.doc_origin
			self.refresh()

	def left_click(self, *args):
		origin = self.presenter.model.doc_origin
		if origin < ORIGINS[-1]: origin += 1
		else: origin = ORIGINS[0]
		self.presenter.api.set_doc_origin(origin)

	def destroy(self):
		items = self.__dict__.keys()
		for item in items:
			self.__dict__[item] = None

	def refresh(self, x=0, y=0, w=0, h=0):
		if not w: w, h = self.GetSize()
		self.Refresh(rect=wx.Rect(x, y, w, h))

	def _on_paint(self, event):
		w, h = self.panel.GetSize()
		pdc = wx.PaintDC(self.panel)
		try:dc = wx.GCDC(pdc)
		except:dc = pdc
		pdc.BeginDrawing()
		dc.BeginDrawing()
		dc.SetPen(wx.NullPen)
		dc.SetBrush(wx.Brush(wx.Colour(*cms.val_255(config.ruler_bg))))
		dc.DrawRectangle(0, 0, w, h)
		color = cms.val_255(config.ruler_fg)
		grad_start = wx.Colour(*(color + [255]))
		grad_end = wx.Colour(*(color + [0]))
		rect = wx.Rect(0, h - 1, w * 2, 1)
		dc.GradientFillLinear(rect, grad_start, grad_end, nDirection=wx.WEST)
		rect = wx.Rect(w - 1, 0, 1, h * 2)
		dc.GradientFillLinear(rect, grad_start, grad_end, nDirection=wx.NORTH)
		shift = (w - 19) / 2 + 1
		dc.DrawBitmap(BITMAPS[self.origin], shift, shift, True)

class Ruler(HPanel):

	presenter = None
	eventloop = None
	style = None

	init_flag = False
	draw_guide = False
	surface = None
	ctx = None
	default_cursor = None
	guide_cursor = None
	mouse_captured = False
	width = 0
	height = 0
	pointer = []

	def __init__(self, presenter, parent, style=HORIZONTAL):
		self.presenter = presenter
		self.eventloop = presenter.eventloop
		self.style = style
		HPanel.__init__(self, parent)
		if not VFONT: load_font()
		size = config.ruler_size
		self.add((size, size))
		self.default_cursor = self.GetCursor()
		if self.style == HORIZONTAL:
			self.guide_cursor = self.presenter.app.cursors[modes.HGUIDE_MODE]
		else:
			self.guide_cursor = self.presenter.app.cursors[modes.VGUIDE_MODE]
		self.SetBackgroundColour(wx.WHITE)
		self.SetDoubleBuffered(True)
		self.Bind(wx.EVT_PAINT, self._on_paint, self)
		self.Bind(wx.EVT_LEFT_DOWN, self.mouse_down)
		self.Bind(wx.EVT_LEFT_UP, self.mouse_up)
		self.Bind(wx.EVT_MOTION, self.mouse_move)
		self.Bind(wx.EVT_MOUSE_CAPTURE_LOST, self.capture_lost)
		self.eventloop.connect(self.eventloop.VIEW_CHANGED, self.repaint)
		events.connect(events.CONFIG_MODIFIED, self.check_config)
		if is_mac():
			self.timer = wx.Timer(self)
			self.Bind(wx.EVT_TIMER, self._repaint_after)
			self.timer.Start(50)

	def check_config(self, attr, value):
		if not attr[:6] == 'ruler_': return
		if attr == 'ruler_size':
			size = config.ruler_size
			self.remove_all()
			self.add((size, size))
			self.parent.layout()
		if attr == 'ruler_font_size':
			load_font()
		self.repaint()

	def _repaint_after(self, event):
		self.repaint()
		self.timer.Stop()

	def destroy(self):
		items = self.__dict__.keys()
		for item in items:
			self.__dict__[item] = None

	def calc_ruler(self):
		canvas = self.presenter.canvas
		w, h = self.presenter.get_page_size()
		x = y = 0
		dx = dy = uc2const.unit_dict[self.presenter.model.doc_units]
		origin = self.presenter.model.doc_origin
		if origin == DOC_ORIGIN_LL:
			x0, y0 = canvas.point_doc_to_win([-w / 2.0 + x, -h / 2.0 + y])
		elif origin == DOC_ORIGIN_LU:
			x0, y0 = canvas.point_doc_to_win([-w / 2.0 + x, h / 2.0 + y])
		else:
			x0, y0 = canvas.point_doc_to_win([x, y])
		dx = dx * canvas.zoom
		dy = dy * canvas.zoom
		sdist = config.snap_distance

		i = 0.0
		while dx < sdist + 3:
			i = i + 0.5
			dx = dx * 10.0 * i
		if dx / 2.0 > sdist + 3:
			dx = dx / 2.0

		i = 0.0
		while dy < sdist + 3:
			i = i + 0.5
			dy = dy * 10.0 * i
		if dy / 2.0 > sdist + 3:
			dy = dy / 2.0

		sx = (x0 / dx - math.floor(x0 / dx)) * dx
		sy = (y0 / dy - math.floor(y0 / dy)) * dy
		return (x0, y0, dx, dy, sx, sy)

	def get_ticks(self):
		canvas = self.presenter.canvas
		pw, ph = self.presenter.get_page_size()
		origin = self.presenter.model.doc_origin
		unit = uc2const.unit_dict[self.presenter.model.doc_units]
		w, h = self.panel.GetSize()
		x0, y0, dx, dy, sx, sy = self.calc_ruler()
		small_ticks = []
		text_ticks = []

		if self.style == HORIZONTAL:
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
			if origin == DOC_ORIGIN_CENTER: shift = 0.0
			while pos < w:
				pos = sxt + i * dxt
				doc_pos = canvas.point_win_to_doc((pos, 0))[0] + shift
				doc_pos *= uc2const.point_dict[self.presenter.model.doc_units]
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
			shift = 0.0
			if origin == DOC_ORIGIN_LL: shift = ph / 2.0
			if origin == DOC_ORIGIN_LU: shift = -ph / 2.0
			while pos < h:
				pos = syt + i * dyt
				doc_pos = canvas.point_win_to_doc((0, pos))[1] + shift
				if origin == DOC_ORIGIN_LU:doc_pos *= -1.0
				doc_pos *= uc2const.point_dict[self.presenter.model.doc_units]
				if float_flag:
					txt = str(round(doc_pos, 4))
					if not doc_pos:txt = '0'
				else:txt = str(int(round(doc_pos)))
				text_ticks.append((syt + i * dyt, txt))
				i += 1
		return small_ticks, text_ticks

	def repaint(self, *args):
		self.init_flag = True
		self.refresh()

	def refresh(self, x=0, y=0, w=0, h=0):
		if not w: w, h = self.GetSize()
		self.Refresh(rect=wx.Rect(x, y, w, h), eraseBackground=False)

	def _on_paint(self, event):
		w, h = self.panel.GetSize()
		pdc = wx.BufferedPaintDC(self.panel)
		pdc.BeginDrawing()
		if self.presenter is None: return
		shift = 0
		if is_msw():shift = 1
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
		if self.init_flag:
			if self.style == HORIZONTAL: self.hrender(w, h)
			else: self.vrender(w, h)
		pdc.DrawBitmap(copy_surface_to_bitmap(self.surface), 0, 0, True)

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

	#------ Guides creation
	def set_cursor(self, mode=False):
		if not mode: self.SetCursor(self.default_cursor)
		else: self.SetCursor(self.guide_cursor)

	def capture_lost(self, event):
		if self.mouse_captured:
			self.mouse_captured = False
			self.ReleaseMouse()
		self.set_cursor()

	def mouse_down(self, event):
		w, h = self.GetSize()
		w = float(w)
		h = float(h)
		self.width = w
		self.height = h
		self.draw_guide = True
		self.set_cursor(True)
		if is_msw():
			self.CaptureMouse()
			self.mouse_captured = True
		self.presenter.canvas.timer.Start(RENDERING_DELAY)
		self.presenter.canvas.set_temp_mode(modes.GUIDE_MODE)
		if self.style == HORIZONTAL:
			self.presenter.canvas.controller.mode = modes.HGUIDE_MODE
		else:
			self.presenter.canvas.controller.mode = modes.VGUIDE_MODE
		self.presenter.canvas.set_canvas_cursor(self.presenter.canvas.controller.mode)

	def mouse_up(self, event):
		self.pointer = list(event.GetPositionTuple())
		if self.mouse_captured:
			self.mouse_captured = False
			self.ReleaseMouse()
		if self.style == HORIZONTAL:
			y_win = self.pointer[1] - self.height
			if y_win > 0.0:
				p = [self.pointer[0], y_win]
				p, p_doc = self.presenter.snap.snap_point(p, snap_x=False)[1:]
				self.presenter.api.create_guides([[p_doc[1], uc2const.HORIZONTAL], ])
		else:
			x_win = self.pointer[0] - self.width
			if x_win > 0.0:
				p = [x_win, self.pointer[1]]
				p, p_doc = self.presenter.snap.snap_point(p, snap_y=False)[1:]
				self.presenter.api.create_guides([[p_doc[0], uc2const.VERTICAL], ])
		self.set_cursor()
		self.presenter.canvas.timer.Stop()
		self.presenter.canvas.restore_mode()
		self.draw_guide = False
		self.pointer = []
		self.presenter.canvas.dragged_guide = ()
		self.presenter.canvas.force_redraw()

	def mouse_move(self, event):
		if self.draw_guide:
			self.pointer = list(event.GetPositionTuple())
			self.repaint_guide()

	def repaint_guide(self, *args):
		p_doc = []
		orient = uc2const.HORIZONTAL
		if self.draw_guide and self.pointer:
			if self.style == HORIZONTAL:
				y_win = self.pointer[1] - self.height
				p = [self.pointer[0], y_win]
				p, p_doc = self.presenter.snap.snap_point(p, snap_x=False)[1:]
			else:
				x_win = self.pointer[0] - self.width
				p = [x_win, self.pointer[1]]
				p, p_doc = self.presenter.snap.snap_point(p, snap_y=False)[1:]
				orient = uc2const.VERTICAL
		self.presenter.canvas.controller.end = p
