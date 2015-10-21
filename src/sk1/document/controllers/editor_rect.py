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

H_ORIENT = ['00', '11', '20', '31']

class RectEditor(AbstractController):

	mode = modes.BEZIER_EDITOR_MODE
	target = None
	points = []
	midpoints = []

	resizing = False
	res_index = 0
	orig_rect = []

	rounding = False
	rnd_index = 0
	rnd_subindex = 0
	orig_corners = []
	start = []
	stop = []
	start2 = []
	stop2 = []

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
			if not self.target.corners[index]:
				start = corner_points[index]
				stop = stops[index][0]
				stop2 = stops[index - 1]
				if len(stop2) == 2: stop2 = stop2[1]
				else: stop2 = stop2[0]
				coef = self.target.corners[index]
				self.points.append(ControlPoint(self.canvas, self.target, start,
											stop, stop2=stop2,
											coef=coef, index=index))
			elif self.target.corners[index] == 1.0:
				start = corner_points[index]
				stop = stops[index - 1]
				if len(stop) == 2:
					stop = stop[1]
					coef = self.target.corners[index]
					self.points.append(ControlPoint(self.canvas, self.target,
										start, stop, coef=coef, index=index))
				elif not self.target.corners[index - 1] == 1.0:
					stop = stop[0]
					coef = self.target.corners[index]
					self.points.append(ControlPoint(self.canvas, self.target,
										start, stop, coef=coef, index=index))

				stop = stops[index][0]
				start2 = []
				if len(stops[index]) == 1 and \
					self.target.corners[index - 3] == 1.0:
						start2 = corner_points[index - 3]
				coef = self.target.corners[index]
				self.points.append(ControlPoint(self.canvas, self.target, start,
									stop, start2=start2,
									coef=coef, index=index, subindex=1))
			else:
				start = corner_points[index]
				stop = stops[index - 1]
				if len(stop) == 2: stop = stop[1]
				else: stop = stop[0]
				coef = self.target.corners[index]
				self.points.append(ControlPoint(self.canvas, self.target, start,
											stop, coef=coef, index=index))

				stop = stops[index][0]
				self.points.append(ControlPoint(self.canvas, self.target, start,
									stop, coef=coef, index=index, subindex=1))
		msg = _('Rectangle in editing')
		events.emit(events.APP_STATUS, msg)

	def stop_(self):
		self.selection.set([self.target, ])
		self.target = None

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
		corners = [] + self.target.corners
		if self.res_index == 0:
			rect[2] -= wpoint[0] - rect[0]
			rect[0] = wpoint[0]
			if rect[2] < 0:
				self.res_index = 2
				c0, c1, c2, c3 = corners
				corners = [c3, c2, c1, c0]
		elif self.res_index == 1:
			rect[3] = wpoint[1] - rect[1]
			if rect[3] < 0:
				self.res_index = 3
				c0, c1, c2, c3 = corners
				corners = [c1, c0, c3, c2]
		elif self.res_index == 2:
			rect[2] = wpoint[0] - rect[0]
			if rect[2] < 0:
				self.res_index = 0
				c0, c1, c2, c3 = corners
				corners = [c3, c2, c1, c0]
		elif self.res_index == 3:
			rect[3] -= wpoint[1] - rect[1]
			rect[1] = wpoint[1]
			if rect[3] < 0:
				self.res_index = 1
				c0, c1, c2, c3 = corners
				corners = [c1, c0, c3, c2]
		rect = libgeom.normalize_rect(rect)
		if final:
			self.api.set_rect_final(self.target, rect, self.orig_rect)
			if not corners == self.orig_corners:
				self.api.set_rect_corners_final(corners, self.orig_corners,
										self.target)
				self.orig_corners = [] + self.target.corners
			self.orig_rect = self.target.get_rect()
		else:
			self.api.set_rect(self.target, rect)
			if not corners == self.target.corners:
				self.api.set_rect_corners(corners, self.target)
		self.update_points()

	def apply_rounding(self, point, final=False, inplace=False):
		wpoint = self.canvas.point_win_to_doc(point)
		invtrafo = libgeom.invert_trafo(self.target.trafo)
		wpoint = libgeom.apply_trafo_to_point(wpoint, invtrafo)
		corners = [] + self.target.corners
		name = str(self.rnd_index) + str(self.rnd_subindex)

		res = 0.0
		if self.stop2:
			val = abs(wpoint[0] - self.start[0])
			val2 = abs(wpoint[1] - self.start[1])
			start = self.start
			if val > val2:
				if self.rnd_index in (0, 2):
					stop = self.stop2
					res = (wpoint[0] - start[0]) / (stop[0] - start[0])
				else:
					stop = self.stop
					res = (wpoint[0] - start[0]) / (stop[0] - start[0])
			else:
				if self.rnd_index in (0, 2):
					stop = self.stop
					res = (wpoint[1] - start[1]) / (stop[1] - start[1])
				else:
					stop = self.stop2
					res = (wpoint[1] - start[1]) / (stop[1] - start[1])
		else:
			start = self.start
			stop = self.stop
			if name in H_ORIENT:
				res = (wpoint[0] - start[0]) / (stop[0] - start[0])
			else:
				res = (wpoint[1] - start[1]) / (stop[1] - start[1])

		if res < 0.0: res = 0.0
		if res > 1.0: res = 1.0

		if inplace: corners[self.rnd_index] = res
		else: corners = [res, res, res, res]
		if final:
			self.api.set_rect_corners_final(corners, self.orig_corners,
										self.target)
		else:
			self.api.set_rect_corners(corners, self.target)
		self.update_points()

	#----- MOUSE CONTROLLING
	def mouse_down(self, event):
		self.resizing = False
		for item in self.points:
			if item.is_pressed(event.get_point()):
				self.rounding = True
				self.rnd_index = item.index
				self.rnd_subindex = item.subindex
				self.orig_corners = [] + self.target.corners
				self.start = [] + item.start
				self.start2 = [] + item.start2
				self.stop = [] + item.stop
				self.stop2 = [] + item.stop2
				return
		for item in self.midpoints:
			if item.is_pressed(event.get_point()):
				self.resizing = True
				self.res_index = self.midpoints.index(item)
				self.orig_rect = self.target.get_rect()
				self.orig_corners = [] + self.target.corners

	def mouse_up(self, event):
		if self.resizing:
			self.resizing = False
			self.apply_resizing(event.get_point(), True)
		elif self.rounding:
			self.rounding = False
			self.apply_rounding(event.get_point(), True, event.is_ctrl())

	def mouse_move(self, event):
		if self.resizing:
			self.apply_resizing(event.get_point())
		elif self.rounding:
			self.apply_rounding(event.get_point(), inplace=event.is_ctrl())

class ControlPoint:

	canvas = None
	target = None
	start = []
	stop = []
	start2 = []
	stop2 = []
	coef = 0.0
	index = 0
	subindex = 0

	def __init__(self, canvas, target, start, stop, start2=[], stop2=[],
				coef=0.0, index=0, subindex=0):
		self.canvas = canvas
		self.target = target
		self.start = start
		self.start2 = start2
		self.stop = stop
		self.stop2 = stop2
		self.coef = coef
		self.index = index
		self.subindex = subindex

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
