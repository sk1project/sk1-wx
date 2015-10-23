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

from uc2 import libgeom

from sk1 import _, modes, config, events
from generic import AbstractController

class PolygonEditor(AbstractController):

	mode = modes.POLYGON_EDITOR_MODE
	target = None

	def __init__(self, canvas, presenter):
		AbstractController.__init__(self, canvas, presenter)

	def start_(self):
		self.snap = self.presenter.snap
		self.target = self.selection.objs[0]
		self.selected_obj = None
		self.api.set_mode()
		self.selection.clear()
		msg = _('Polygon in editing')
		events.emit(events.APP_STATUS, msg)

	def stop_(self):
		self.selection.set([self.target, ])
		self.target = None
		self.selected_obj = None

	def escape_pressed(self):
		self.canvas.set_mode()

	#----- REPAINT

	def repaint(self):
		x0, y0, x1, y1 = self.target.cache_bbox
		p0 = self.canvas.point_doc_to_win([x0, y0])
		p1 = self.canvas.point_doc_to_win([x1, y1])
		self.canvas.renderer.draw_frame(p0, p1)

	#----- MOUSE CONTROLLING
	def mouse_down(self, event):
		self.selected_obj = None

		objs = self.canvas.pick_at_point(event.get_point())
		if objs and not objs[0] == self.target and objs[0].is_primitive():
			self.selected_obj = objs[0]

	def mouse_up(self, event):
		if self.selected_obj:
			self.target = self.selected_obj
			self.canvas.set_mode(modes.SHAPER_MODE)

	def mouse_move(self, event):pass