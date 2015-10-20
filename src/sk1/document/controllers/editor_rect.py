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
	midpoints = []
	resizing = False
	res_index = 0
	orig_rect = []

	def __init__(self, canvas, presenter):
		AbstractController.__init__(self, canvas, presenter)

	def start_(self):
		self.snap = self.presenter.snap
		self.target = self.selection.objs[0]
		self.update_points()
		self.api.set_mode()
		self.selection.clear()
		msg = _('Rectangle in editing')
		events.emit(events.APP_STATUS, msg)

	def update_points(self):
		self.points = []
		self.midpoints = []
		mps = self.target.get_midpoints()
		for item in mps:
			self.midpoints.append(MidPoint(self.canvas, self.target, item))
		corner_points = self.target.get_corner_points()
		stops = self.target.get_stops()
		for index in range(4):
			if self.target.corners[index]:
				start = corner_points[index]
				stop = stops[index - 1]
				if len(stop) == 2: stop = stop[1]
				else: stop = stop[0]
				coef = self.target.corners[index]
				self.points.append(ControlPoint(self.canvas, self.target,
											start, stop, coef))

				stop = stops[index][0]
				self.points.append(ControlPoint(self.canvas, self.target,
											start, stop, coef))
			else:
				start = corner_points[index]
				stop = stops[index][0]
				coef = self.target.corners[index]
				self.points.append(ControlPoint(self.canvas, self.target,
											start, stop, coef))

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
		for item in self.midpoints: item.repaint()
		for item in self.points: item.repaint()

	#----- CHANGE APPLY
	def apply_resizing(self, point, final=False):
		wpoint = self.canvas.point_win_to_doc(point)
		invtrafo = libgeom.invert_trafo(self.target.trafo)
		wpoint = libgeom.apply_trafo_to_point(wpoint, invtrafo)
		rect = self.target.get_rect()
		if self.res_index == 0:
			rect[2] -= wpoint[0] - rect[0]
			rect[0] = wpoint[0]
			if rect[2] < 0:self.res_index = 2
		elif self.res_index == 1:
			rect[3] = wpoint[1] - rect[1]
			if rect[3] < 0:self.res_index = 3
		elif self.res_index == 2:
			rect[2] = wpoint[0] - rect[0]
			if rect[2] < 0:self.res_index = 0
		elif self.res_index == 3:
			rect[3] -= wpoint[1] - rect[1]
			rect[1] = wpoint[1]
			if rect[3] < 0:self.res_index = 1
		rect = libgeom.normalize_rect(rect)
		if final:
			self.api.set_rect_final(self.target, rect, self.orig_rect)
			self.orig_rect = self.target.get_rect()
		else:
			self.api.set_rect(self.target, rect)
		self.update_points()

	#----- MOUSE CONTROLLING
	def mouse_down(self, event):
		self.resizing = False
		for item in self.midpoints:
			if item.is_pressed(event.get_point()):
				self.resizing = True
				self.res_index = self.midpoints.index(item)
				self.orig_rect = self.target.get_rect()

	def mouse_up(self, event):
		if self.resizing:
			self.resizing = False
			self.apply_resizing(event.get_point(), True)

	def mouse_move(self, event):
		if self.resizing:
			self.apply_resizing(event.get_point())

class ControlPoint:

	canvas = None
	target = None
	start = []
	stop = []
	stop2 = []
	coef = 0.0

	def __init__(self, canvas, target, start, stop, coef=0.0):
		self.canvas = canvas
		self.target = target
		self.start = start
		self.stop = stop
		self.coef = coef

	def get_point(self):
		p = libgeom.midpoint(self.start, self.stop, self.coef)
		return libgeom.apply_trafo_to_point(p, self.target.trafo)

	def get_screen_point(self):
		return self.canvas.point_doc_to_win(self.get_point())

	def is_pressed(self, win_point):
		wpoint = self.canvas.point_doc_to_win(self.get_point())
		bbox = libgeom.bbox_for_point(wpoint, config.point_sensitivity_size)
		return libgeom.is_point_in_bbox(win_point, bbox)

	def repaint(self):
		self.canvas.renderer.draw_rect_point(self.get_screen_point())

class MidPoint:

	canvas = None
	target = None
	point = []
	callback = None

	def __init__(self, canvas, target, point):
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
		self.canvas.renderer.draw_rect_midpoint(self.get_screen_point())
