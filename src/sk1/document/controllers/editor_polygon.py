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

	midpoint_index = None
	corner_index = None

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

	#----- CHANGE APPLY
	def apply_corner_change(self, point, index, control=False, final=False):
		wpoint = self.canvas.point_win_to_doc(point)
		invtrafo = libgeom.invert_trafo(self.target.trafo)
		x, y = libgeom.apply_trafo_to_point(wpoint, invtrafo)
		radius = self.target.get_corner_radius()
		angle = self.target.get_corner_angle(index)
		coef1 = libgeom.get_point_radius([x, y]) / radius
		if control:
			props = [self.orig_angle1, self.orig_angle2,
					coef1, self.orig_coef2]
		else:
			angle1 = libgeom.get_point_angle([x, y]) - angle
			props = [angle1, self.orig_angle2,
					coef1, self.orig_coef2]
		if final:
			props_before = [self.orig_angle1, self.orig_angle2,
					self.orig_coef1, self.orig_coef2]
			self.api.set_polygon_properties_final(props, props_before,
												self.target)
		else:
			self.api.set_polygon_properties(props, self.target)
		self.update_points()

	def apply_midpoint_change(self, point, index, control=False, final=False):
		wpoint = self.canvas.point_win_to_doc(point)
		invtrafo = libgeom.invert_trafo(self.target.trafo)
		x, y = libgeom.apply_trafo_to_point(wpoint, invtrafo)
		radius = self.target.get_midpoint_radius()
		angle = self.target.get_midpoint_angle(index)
		coef2 = libgeom.get_point_radius([x, y]) / radius
		if control:
			props = [self.orig_angle1, self.orig_angle2,
					self.orig_coef1, coef2]
		else:
			angle2 = libgeom.get_point_angle([x, y]) - angle
			props = [self.orig_angle1, angle2,
					self.orig_coef1, coef2]
		if final:
			props_before = [self.orig_angle1, self.orig_angle2,
					self.orig_coef1, self.orig_coef2]
			self.api.set_polygon_properties_final(props, props_before,
												self.target)
		else:
			self.api.set_polygon_properties(props, self.target)
		self.update_points()

	#----- MOUSE CONTROLLING
	def mouse_down(self, event):
		self.selected_obj = None
		self.corner_index = None
		self.midpoint_index = None
		for item in self.corner_points:
			if item.is_pressed(event.get_point()):
				self.corner_index = item.index
				self.store_props()
				return
		for item in self.midpoints:
			if item.is_pressed(event.get_point()):
				self.midpoint_index = item.index
				self.store_props()
				return
		objs = self.canvas.pick_at_point(event.get_point())
		if objs and not objs[0] == self.target and objs[0].is_primitive():
			self.selected_obj = objs[0]

	def mouse_up(self, event):
		if not self.corner_index is None:
			self.apply_corner_change(event.get_point(), self.corner_index,
									event.is_ctrl(), True)
			self.corner_index = None
		elif not self.midpoint_index is None:
			self.apply_midpoint_change(event.get_point(), self.midpoint_index,
									event.is_ctrl(), True)
			self.midpoint_index = None
		elif self.selected_obj:
			self.target = self.selected_obj
			self.selected_obj = None
			self.canvas.set_mode(modes.SHAPER_MODE)

	def mouse_move(self, event):
		if not self.corner_index is None:
			self.apply_corner_change(event.get_point(), self.corner_index,
									event.is_ctrl())
		elif not self.midpoint_index is None:
			self.apply_midpoint_change(event.get_point(), self.midpoint_index,
									event.is_ctrl())


class CornerPoint:

	canvas = None
	target = None
	point = []
	index = 0

	def __init__(self, canvas, target, point, index):
		self.canvas = canvas
		self.target = target
		self.point = point
		self.index = index

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
