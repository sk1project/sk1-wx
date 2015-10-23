# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2015 by Igor E. Novikov
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

class EditorChooser(AbstractController):

	mode = modes.SHAPER_MODE
	target = None

	def __init__(self, canvas, presenter):
		AbstractController.__init__(self, canvas, presenter)

	def start_(self):
		sel_objs = self.selection.objs
		if not sel_objs:
			self.selection.clear()
		else:
			obj = sel_objs[0]
			if obj.is_curve():
				self.canvas.set_mode(modes.BEZIER_EDITOR_MODE)
			elif obj.is_rect():
				self.canvas.set_mode(modes.RECT_EDITOR_MODE)
			elif obj.is_circle():
				self.canvas.set_mode(modes.ELLIPSE_EDITOR_MODE)
			else:
				self.selection.clear()

	def restore(self):
		self.timer.start()

	def stop_(self):pass

	def on_timer(self):
		self.timer.stop()
		self.start_()

	def mouse_down(self, event):pass

	def mouse_up(self, event):
		self.end = event.get_point()
		self.do_action()

	def mouse_move(self, event):pass

	def do_action(self):
		objs = self.canvas.pick_at_point(self.end)
		if objs and objs[0].is_primitive() and not objs[0].is_pixmap():
			self.selection.set([objs[0], ])
			self.start_()
