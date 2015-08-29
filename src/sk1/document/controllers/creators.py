# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2013 by Igor E. Novikov
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

from sk1 import modes
from generic import AbstractController

class AbstractCreator(AbstractController):

	check_snap = True

	def __init__(self, canvas, presenter):
		AbstractController.__init__(self, canvas, presenter)

	def escape_pressed(self):
		self.canvas.set_mode()

	def mouse_down(self, event):
		AbstractController.mouse_down(self, event)

	def mouse_move(self, event):
		if self.draw:
			AbstractController.mouse_move(self, event)
		else:
			self.counter += 1
			if self.counter > 5:
				self.counter = 0
				point = list(event.GetPositionTuple())
				dpoint = self.canvas.win_to_doc(point)
				if self.selection.is_point_over_marker(dpoint):
					mark = self.selection.is_point_over_marker(dpoint)[0]
					self.canvas.resize_marker = mark
					self.canvas.set_temp_mode(modes.RESIZE_MODE)

	def _calc_points(self, event):
		self.end = list(event.GetPositionTuple())
		ctrl = event.ControlDown()
		shift = event.ShiftDown()
		if shift and ctrl:
			if not self.center: self.center = self.start
			self.end = self._get_proportional(self.center, self.end)
			self.start = self._get_mirror(self.center, self.end)
		elif shift:
			if not self.center: self.center = self.start
			self.start = self._get_mirror(self.center, self.end)
		elif ctrl:
			if self.center: self.start = self.center; self.center = []
			self.end = self._get_proportional(self.start, self.end)
		else:
			if self.center: self.start = self.center; self.center = []
		if self.check_snap:
			self.start, self.start_doc = self.snap.snap_point(self.start)[1:]
			self.end, self.end_doc = self.snap.snap_point(self.end)[1:]

class RectangleCreator(AbstractCreator):

	mode = modes.RECT_MODE

	def __init__(self, canvas, presenter):
		AbstractCreator.__init__(self, canvas, presenter)

	def do_action(self, event):
		if self.start and self.end:
			if abs(self.end[0] - self.start[0]) > 2 and \
			abs(self.end[1] - self.start[1]) > 2:
				rect = self.start_doc + self.end_doc
				self.api.create_rectangle(rect)
		return True

class EllipseCreator(AbstractCreator):

	mode = modes.ELLIPSE_MODE

	def __init__(self, canvas, presenter):
		AbstractCreator.__init__(self, canvas, presenter)

	def do_action(self, event):
		if self.start and self.end:
			if abs(self.end[0] - self.start[0]) > 2 and \
			abs(self.end[1] - self.start[1]) > 2:
				rect = self.start_doc + self.end_doc
				self.api.create_ellipse(rect)
		return True

class PolygonCreator(AbstractCreator):

	mode = modes.POLYGON_MODE

	def __init__(self, canvas, presenter):
		AbstractCreator.__init__(self, canvas, presenter)

	def do_action(self, event):
		if self.start and self.end:
			if abs(self.end[0] - self.start[0]) > 2 and \
			abs(self.end[1] - self.start[1]) > 2:
				rect = self.start_doc + self.end_doc
				self.api.create_polygon(rect)
		return True
