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


from sk1 import modes
from sk1.appconst import ZOOM_IN, ZOOM_OUT

class AbstractController:

	draw = False
	canvas = None
	snap = None
	start = []
	end = []
	center = []
	start_doc = []
	end_doc = []
	check_snap = False

	counter = 0
	timer = None

	mode = None

	def __init__(self, canvas, presenter):
		self.canvas = canvas
		self.app = presenter.app
		self.presenter = presenter
		self.selection = presenter.selection
		self.eventloop = presenter.eventloop
		self.api = presenter.api
		self.start = []
		self.end = []
		self.start_doc = []
		self.end_doc = []
		self.timer = self.canvas.timer

	def destroy(self):
		items = self.__dict__.keys()
		for item in items:
			self.__dict__[item] = None

	def set_cursor(self):
		if self.mode is None:
			self.canvas.set_canvas_cursor(self.canvas.mode)
		else:
			self.canvas.set_canvas_cursor(self.mode)

	def start_(self):pass
	def stop_(self):pass
	def standby(self):pass
	def restore(self):pass
	def do_action(self, event): return True
	def escape_pressed(self):pass
	def mouse_double_click(self, event): pass
	def mouse_right_down(self, event):
		if event.is_ctrl():
			self.canvas.capture_mouse()
			self.canvas.set_temp_mode(modes.TEMP_FLEUR_MODE)
	def mouse_right_up(self, event):
		self.canvas.show_context_menu()
	def mouse_middle_down(self, event):
		self.canvas.capture_mouse()
		self.canvas.set_temp_mode(modes.TEMP_FLEUR_MODE)
	def mouse_middle_up(self, event):pass
	def wheel(self, event):
		point = event.get_point()
		val = event.get_rotation()
		if event.is_ctrl():
			self.canvas.scroll(val, 0)
		elif event.is_shift():
			if val < 0:
				self.canvas.zoom_at_point(point, ZOOM_OUT)
			else:
				self.canvas.zoom_at_point(point, ZOOM_IN)
		else:
			self.canvas.scroll(0, val)

	def mouse_down(self, event):
		self.snap = self.presenter.snap
		self.start = []
		self.center = []
		self.end = []
		self.start_doc = []
		self.end_doc = []
		self.counter = 0
		self.timer.stop()

		self.draw = True
		self.start = event.get_point()
		self.end = event.get_point()
		if self.check_snap:
			self.start, self.start_doc = self.snap.snap_point(self.start)[1:]
			self.end, self.end_doc = self.snap.snap_point(self.end)[1:]
		self.counter = 0
		self.canvas.renderer.cdc_paint_doc()
		self.timer.start()

	def _get_proportional(self, start, end):
		x0, y0 = start
		x1, y1 = end
		dx = x1 - x0
		dy = y1 - y0
		delta = min(abs(dx), abs(dy))
		if dx < 0: dx = -delta
		else: dx = delta
		if dy < 0: dy = -delta
		else: dy = delta
		return [x0 + dx, y0 + dy]

	def _get_mirror(self, center, point):
		x0, y0 = center
		x1, y1 = point
		dx = x1 - x0
		dy = y1 - y0
		return [x0 - dx, y0 - dy]

	def _calc_points(self, event):
		self.end = event.get_point()
		if self.check_snap:
			self.start, self.start_doc = self.snap.snap_point(self.start)[1:]
			self.end, self.end_doc = self.snap.snap_point(self.end)[1:]

	def mouse_up(self, event):
		if self.draw:
			self.timer.Stop()
			self.draw = False
			self.counter = 0
			self._calc_points(event)
			if self.do_action(event):
				self.start = []
				self.center = []
				self.end = []
				self.canvas.selection_redraw()

	def mouse_move(self, event):
		if self.draw: self._calc_points(event)

	def on_timer(self):
		self.repaint()

	def repaint(self):
		if self.end:
			self.canvas.renderer.cdc_draw_frame([] + self.start, [] + self.end)



class WaitController(AbstractController):

	mode = modes.WAIT_MODE
	move = False
	fleur_timer = None

	def __init__(self, canvas, presenter):
		AbstractController.__init__(self, canvas, presenter)

	def mouse_down(self, event):pass
	def mouse_up(self, event):pass
	def repaint(self, *args):pass
	def mouse_move(self, event):pass
	def on_timer(self):pass
