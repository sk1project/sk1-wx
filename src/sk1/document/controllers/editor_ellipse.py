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

class EllipseEditor(AbstractController):

	mode = modes.ELLIPSE_EDITOR_MODE
	target = None
	start_point = None
	end_point = None
	selected_point = None

	orig_type = 0
	orig_angle1 = 0.0
	orig_angle2 = 0.0

	def __init__(self, canvas, presenter):
		AbstractController.__init__(self, canvas, presenter)

	def start_(self):
		self.snap = self.presenter.snap
		self.target = self.selection.objs[0]
		self.selected_obj = None
		self.update_points()
		self.api.set_mode()
		self.selection.clear()
		msg = _('Ellipse in editing')
		events.emit(events.APP_STATUS, msg)

	def stop_(self):
		self.selection.set([self.target, ])
		self.target = None
		self.selected_obj = None

	def escape_pressed(self):
		self.canvas.set_mode()

	def update_points(self):
		self.start_point = ControlPoint(self.canvas, self.target, True)
		self.end_point = ControlPoint(self.canvas, self.target)
		msg = _('Ellipse in editing')
		events.emit(events.APP_STATUS, msg)

	#----- REPAINT

	def repaint(self):
		x0, y0, x1, y1 = self.target.cache_bbox
		p0 = self.canvas.point_doc_to_win([x0, y0])
		p1 = self.canvas.point_doc_to_win([x1, y1])
		self.canvas.renderer.draw_frame(p0, p1)
		self.end_point.repaint()
		self.start_point.repaint()

	#----- CHANGE APPLY
	def apply_moving(self, point, start=False, final=False):
		wpoint = self.canvas.point_win_to_doc(point)
		invtrafo = libgeom.invert_trafo(self.target.trafo)
		x, y = libgeom.apply_trafo_to_point(wpoint, invtrafo)
		x -= 0.5
		y -= 0.5
		angle = 0.0
		if x > 0 and y > 0:
			angle = math.atan(y / x)
		elif x == 0 and y > 0:
			angle = math.pi / 2.0
		elif x < 0 and y > 0:
			angle = math.atan(-x / y) + math.pi / 2.0
		elif x < 0 and y == 0:
			angle = math.pi
		elif x < 0 and y < 0:
			angle = math.atan(y / x) + math.pi
		elif x == 0 and y < 0:
			angle = 1.5 * math.pi
		elif x > 0 and y < 0:
			angle = math.atan(x / -y) + 1.5 * math.pi
		elif x > 0 and y == 0:
			angle = 0.0
		elif x == 0 and y == 0:
			return
		circle_type = self.orig_type
		angle1 = self.orig_angle1
		angle2 = self.orig_angle2
		if start: angle1 = angle
		else: angle2 = angle
		if final:
			self.api.set_circle_properties_final(circle_type, angle1, angle2,
				self.orig_type, self.orig_angle1, self.orig_angle2, self.target)
		else:
			self.api.set_circle_properties(circle_type, angle1,
										angle2, self.target)
		self.update_points()

	def store_props(self):
		self.orig_type = self.target.circle_type
		self.orig_angle1 = self.target.angle1
		self.orig_angle2 = self.target.angle2

	#----- MOUSE CONTROLLING
	def mouse_down(self, event):
		self.selected_obj = None
		self.selected_point = None
		if self.start_point.is_pressed(event.get_point()):
			self.selected_point = self.start_point
			self.store_props()
			return
		if self.end_point.is_pressed(event.get_point()):
			self.selected_point = self.end_point
			self.store_props()
			return
		objs = self.canvas.pick_at_point(event.get_point())
		if objs and not objs[0] == self.target and objs[0].is_primitive():
			self.selected_obj = objs[0]

	def mouse_up(self, event):
		if self.selected_point:
			self.apply_moving(event.get_point(), self.selected_point.start, True)
			self.selected_point = None
			return
		if self.selected_obj:
			self.target = self.selected_obj
			self.canvas.set_mode(modes.SHAPER_MODE)

	def mouse_move(self, event):
		if self.selected_point:
			self.apply_moving(event.get_point(), self.selected_point.start)

class ControlPoint:

	canvas = None
	target = None
	start = False

	def __init__(self, canvas, target, start=False):
		self.canvas = canvas
		self.target = target
		self.start = start

	def get_point(self):
		angle = self.target.angle1
		if not self.start:angle = self.target.angle2
		x = 0.5 * math.cos(angle) + 0.5
		y = 0.5 * math.sin(angle) + 0.5
		return libgeom.apply_trafo_to_point([x, y], self.target.trafo)

	def get_screen_point(self):
		return self.canvas.point_doc_to_win(self.get_point())

	def is_pressed(self, win_point):
		wpoint = self.canvas.point_doc_to_win(self.get_point())
		bbox = libgeom.bbox_for_point(wpoint, config.point_sensitivity_size)
		return libgeom.is_point_in_bbox(win_point, bbox)

	def repaint(self):
		p = self.get_screen_point()
		if self.start: self.canvas.renderer.draw_ellipse_start_point(p)
		else: self.canvas.renderer.draw_ellipse_end_point(p)
