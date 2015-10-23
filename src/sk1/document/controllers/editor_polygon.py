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

import math

from uc2 import libgeom

from sk1 import _, modes, config, events
from generic import AbstractController

class PolygonEditor(AbstractController):

	mode = modes.POLYGON_EDITOR_MODE
	target = None

	corner_points = []
	midpoints = []

	orig_angle1 = 0.0
	orig_angle2 = 0.0
	orig_coef1 = 1.0
	orig_coef2 = 1.0

	def __init__(self, canvas, presenter):
		AbstractController.__init__(self, canvas, presenter)

	def start_(self):
		self.snap = self.presenter.snap
		self.target = self.selection.objs[0]
		self.selected_obj = None
		self.api.set_mode()
		self.update_points()
		self.selection.clear()
		msg = _('Polygon in editing')
		events.emit(events.APP_STATUS, msg)

	def stop_(self):
		self.selection.set([self.target, ])
		self.target = None
		self.selected_obj = None

	def escape_pressed(self):
		self.canvas.set_mode()

	def store_props(self):
		self.orig_angle1 = self.target.angle1
		self.orig_angle2 = self.target.angle2
		self.orig_coef1 = self.target.coef1
		self.orig_coef2 = self.target.coef2

	def update_points(self):
		self.corner_points = []
		self.midpoints = []
		coef1 = self.target.coef1
		coef2 = self.target.coef2
		angle1 = self.target.angle1
		angle2 = self.target.angle2
		corners_num = self.target.corners_num
		center = [0.5, 0.5]
		corner_angle = 2.0 * math.pi / float(corners_num)
		corners_start = [0.5, 0.5 + 0.5 * coef1]
		midpoint_start = [0.5, 0.5 + 0.5 * coef2 * math.cos(corner_angle / 2.0)]

		corner_angle_shift = angle1
		midpoint_angle_shift = corner_angle / 2.0 + angle2

		for i in range(0, corners_num):
			angle = float(i) * corner_angle + corner_angle_shift
			point = libgeom.rotate_point(center, corners_start, angle)
			self.corner_points.append(CornerPoint(self.canvas,
												self.target, point, i))

			angle = float(i) * corner_angle + midpoint_angle_shift
			point = libgeom.rotate_point(center, midpoint_start, angle)
			self.midpoints.append(CornerPoint(self.canvas,
												self.target, point, i))
		msg = _('Polygon in editing')
		events.emit(events.APP_STATUS, msg)

	#----- REPAINT

	def repaint(self):
		x0, y0, x1, y1 = self.target.cache_bbox
		p0 = self.canvas.point_doc_to_win([x0, y0])
		p1 = self.canvas.point_doc_to_win([x1, y1])
		self.canvas.renderer.draw_frame(p0, p1)
		for item in self.corner_points: item.repaint()
		for item in self.midpoints: item.repaint()

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


class CornerPoint:

	canvas = None
	target = None
	point = []

	def __init__(self, canvas, target, point, index):
		self.canvas = canvas
		self.target = target
		self.point = point

	def get_point(self):
		return libgeom.apply_trafo_to_point(self.point, self.target.trafo)

	def get_screen_point(self):
		return self.canvas.point_doc_to_win(self.get_point())

	def is_pressed(self, win_point):
		wpoint = self.canvas.point_doc_to_win(self.get_point())
		bbox = libgeom.bbox_for_point(wpoint, config.point_sensitivity_size)
		return libgeom.is_point_in_bbox(win_point, bbox)

	def repaint(self):
		self.canvas.renderer.draw_polygon_point(self.get_screen_point())
