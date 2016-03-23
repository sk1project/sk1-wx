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

import math

from uc2 import libgeom

from sk1 import _, modes, config, events
from generic import AbstractController

class TextEditor(AbstractController):

	mode = modes.TEXT_EDITOR_MODE
	target = None

	points = []

	def __init__(self, canvas, presenter):
		AbstractController.__init__(self, canvas, presenter)

	def start_(self):
		self.snap = self.presenter.snap
		self.target = self.selection.objs[0]
		self.selected_obj = None
		self.api.set_mode()
		self.update_points()
		self.selection.clear()
		msg = _('Text in shaping')
		events.emit(events.APP_STATUS, msg)

	def stop_(self):
		self.selection.set([self.target, ])
		self.target = None
		self.selected_obj = None
		self.points = []

	def escape_pressed(self):
		self.canvas.set_mode()

	def update_points(self):
		cv = self.canvas
		self.points = []
		index = 0
		for item in self.target.cache_layout_data:
			if index < len(self.target.cache_cpath) and \
			self.target.cache_cpath[index]:
				x = item[0]
				y = item[4]
				trafo = self.target.trafo
				flag = False
				if index in self.target.trafos.keys():
					trafo = self.target.trafos[index]
					flag = True
				self.points.append(ControlPoint(cv, index, [x, y], trafo, flag))
			index += 1

	#----- REPAINT
	def repaint(self):
		bbox = self.target.cache_layout_bbox
		self.canvas.renderer.draw_text_frame(bbox, self.target.trafo)
		for item in self.points:
			item.repaint()

class ControlPoint:

	canvas = None
	index = 0
	point = []
	trafo = []
	modified = False

	def __init__(self, canvas, index, point, trafo, modified=False):
		self.canvas = canvas
		self.index = index
		self.point = point
		self.trafo = trafo
		self.modified = modified

	def get_point(self):
		return libgeom.apply_trafo_to_point(self.point, self.trafo)

	def get_screen_point(self):
		return self.canvas.point_doc_to_win(self.get_point())

	def repaint(self):
		self.canvas.renderer.draw_polygon_point(self.get_screen_point())
