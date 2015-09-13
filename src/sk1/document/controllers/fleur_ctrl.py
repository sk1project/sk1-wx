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

from generic import AbstractController

from sk1 import modes
from sk1.appconst import RENDERING_DELAY

class FleurController(AbstractController):

	mode = modes.FLEUR_MODE
	move = False
	fleur_timer = None

	def __init__(self, canvas, presenter):
		AbstractController.__init__(self, canvas, presenter)

	def escape_pressed(self):
		if not self.start:
			self.canvas.set_mode()

	def mouse_down(self, event):
		self.move = True
		self.start = event.get_point()
		if not self.timer.IsRunning(): self.timer.Start(RENDERING_DELAY)

	def mouse_up(self, event):
		if self.timer.IsRunning(): self.timer.Stop()
		if self.start:
			self.start = []
			self.end = []
			self.move = False

	def repaint(self, *args):pass

	def mouse_move(self, event):
		if not self.timer.IsRunning(): self.timer.Start(RENDERING_DELAY)
		if self.move:
			if self.start:
				self.end = event.get_point()
			else:
				self.start = event.get_point()

	def on_timer(self):
		if self.start and self.end:
			dx = self.end[0] - self.start[0]
			dy = self.end[1] - self.start[1]
			if dx <> 0 or dy <> 0:
				self.start = self.end
				self.canvas.scroll(dx, dy)


class TempFleurController(FleurController):

	mode = modes.TEMP_FLEUR_MODE
	move = True

	def __init__(self, canvas, presenter):
		FleurController.__init__(self, canvas, presenter)

	def mouse_down(self, event):pass

	def mouse_middle_up(self, event):
		FleurController.mouse_up(self, event)
		self.canvas.release_mouse()
		self.move = True
		self.canvas.restore_mode()

	def mouse_right_up(self, event):
		self.mouse_middle_up(event)
