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
from generic import AbstractController

class SelectController(AbstractController):

	mode = modes.SELECT_MODE

	def __init__(self, canvas, presenter):
		AbstractController.__init__(self, canvas, presenter)

	def escape_pressed(self):
		self.selection.clear()

	def mouse_move(self, event):
		self.snap = self.presenter.snap
		if self.draw:
			AbstractController.mouse_move(self, event)
		else:
			self.counter += 1
			if self.counter > 5:
				self.counter = 0
				point = list(event.GetPositionTuple())
				dpoint = self.canvas.win_to_doc(point)
				if self.selection.is_point_over(dpoint):
					self.canvas.set_temp_mode(modes.MOVE_MODE)
				elif self.selection.pick_at_point(dpoint):
					self.canvas.set_temp_mode(modes.MOVE_MODE)
				elif self.selection.is_point_over_marker(dpoint):
					mark = self.selection.is_point_over_marker(dpoint)[0]
					self.canvas.resize_marker = mark
					self.canvas.set_temp_mode(modes.RESIZE_MODE)
				elif self.snap.is_over_guide(point)[0]:
					self.canvas.set_temp_mode(modes.GUIDE_MODE)

	def do_action(self, event):
		if self.start and self.end:
			add_flag = False
			if event.ShiftDown():
				add_flag = True
			change_x = abs(self.end[0] - self.start[0])
			change_y = abs(self.end[1] - self.start[1])
			if change_x < 5 and change_y < 5:
				self.canvas.select_at_point(self.start, add_flag)
			else:
				self.canvas.select_by_rect(self.start, self.end, add_flag)

			dpoint = self.canvas.win_to_doc(self.start)
			if self.selection.is_point_over(dpoint):
				self.canvas.set_temp_mode(modes.MOVE_MODE)
		return True

class PickController(AbstractController):

	mode = modes.PICK_MODE

	def __init__(self, canvas, presenter):
		AbstractController.__init__(self, canvas, presenter)

	def mouse_down(self, event):pass

	def mouse_up(self, event):
		self.end = list(event.GetPositionTuple())
		self.do_action()

	def mouse_move(self, event):pass

	def do_action(self):
		obj = self.canvas.pick_at_point(self.end)
		if not self.callback(obj):
			self.callback = None
			self.canvas.restore_mode()
