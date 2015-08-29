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

ZOOM_IN = 1.25
ZOOM_OUT = 0.8

class ZoomController(AbstractController):

	mode = modes.ZOOM_MODE

	def __init__(self, canvas, presenter):
		AbstractController.__init__(self, canvas, presenter)

	def escape_pressed(self):
		if not self.start:
			self.canvas.set_mode()

	def mouse_right_down(self, event):
		self.start = list(event.GetPositionTuple())
		cursor = self.canvas.app.cursors[modes.ZOOM_OUT_MODE]
		self.canvas.set_temp_cursor(cursor)

	def mouse_right_up(self, event):
		if not self.draw:
			self.canvas.zoom_at_point(self.start, ZOOM_OUT)
			self.canvas.restore_cursor()

	def do_action(self, event):
		if self.start and self.end:
			change_x = abs(self.end[0] - self.start[0])
			change_y = abs(self.end[1] - self.start[1])
			if change_x < 5 and change_y < 5:
				self.canvas.zoom_at_point(self.start, ZOOM_IN)
			else:
				self.canvas.zoom_to_rectangle(self.start, self.end)
			self.start = []
			self.end = []
		return False
