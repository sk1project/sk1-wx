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

from copy import deepcopy

from uc2 import libgeom
from uc2.formats.sk2 import sk2_model
from uc2.formats.sk2 import sk2_const

from sk1 import _, modes, config, events
from generic import AbstractController


class RectEditor(AbstractController):

	mode = modes.BEZIER_EDITOR_MODE
	target = None
	points = []

	def __init__(self, canvas, presenter):
		AbstractController.__init__(self, canvas, presenter)

	def start_(self):
		self.points = []
		self.snap = self.presenter.snap
		self.target = self.selection.objs[0]
		self.update_points()
		self.api.set_mode()
		self.selection.clear()
		msg = _('Rectangle in editing')
		events.emit(events.APP_STATUS, msg)

	def update_points(self):pass

	def stop_(self):
		self.selection.set([self.target, ])
		self.target = None
#		for item in self.points: item.destroy()

	def escape_pressed(self):
		self.canvas.set_mode()

	#----- REPAINT

	def repaint(self):
		x0, y0, x1, y1 = self.target.cache_bbox
		p0 = self.canvas.point_doc_to_win([x0, y0])
		p1 = self.canvas.point_doc_to_win([x1, y1])
		self.canvas.renderer.draw_frame(p0, p1)

	#----- MOUSE CONTROLLING
	def mouse_down(self, event):pass
	def mouse_up(self, event):pass
	def mouse_move(self, event):pass
