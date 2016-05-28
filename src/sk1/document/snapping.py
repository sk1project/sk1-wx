# -*- coding: utf-8 -*-
#
#	Copyright (C) 2013 by Igor E. Novikov
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.

import math

from uc2 import libgeom, uc2const
from uc2.formats.sk2 import sk2_const

from sk1 import config
from sk1.appconst import SNAP_TO_GRID, SNAP_TO_GUIDES, SNAP_TO_OBJECTS, SNAP_TO_PAGE

class SnapManager:

	presenter = None
	doc = None
	methods = None
	canvas = None

	active_snap = [None, None]
	active_guide = None

	snap_to_grid = False
	snap_to_guides = False
	snap_to_objects = False
	snap_to_page = False
	snap_dict = {}
	snap_point_dict = {}

	snap_x = True
	snap_y = True

	grid_win = []
	grid_doc = []
	page_grid = []
	objects_grid = []
	guides_grid = []

	def __init__(self, presenter):

		self.active_snap = [None, None]

		self.presenter = presenter
		self.doc = self.presenter.doc_presenter
		self.methods = self.presenter.methods
		self.canvas = self.presenter.canvas
		self.snap_to_grid = config.snap_to_grid
		self.snap_to_guides = config.snap_to_guides
		self.snap_to_objects = config.snap_to_objects
		self.snap_to_page = config.snap_to_page
		self.snap_point_dict = {SNAP_TO_GRID:self.snap_point_to_grid,
						SNAP_TO_GUIDES:self.snap_point_to_guides,
						SNAP_TO_OBJECTS:self.snap_point_to_objects,
						SNAP_TO_PAGE:self.snap_point_to_page, }
		el = self.presenter.eventloop
		el.connect(el.VIEW_CHANGED, self.update)
		el.connect(el.DOC_MODIFIED, self.update)
		el.connect(el.PAGE_CHANGED, self.update)

	def destroy(self):
		items = self.__dict__.keys()
		for item in items:
			self.__dict__[item] = None

	def update(self, *args):
		if self.snap_to_guides:
			self.update_guides_grid()
		if self.snap_to_grid:
			self.update_grid()
		if self.snap_to_objects:
			self.update_objects_grid()
		if self.snap_to_page:
			self.update_page_grid()

	def update_grid(self):
		self._calc_grid()

	def update_guides_grid(self):
		self.guides_grid = [[], []]
		guide_layer = self.methods.get_guide_layer()
		if not self.methods.is_layer_visible(guide_layer): return
		for child in guide_layer.childs:
			if child.is_guide():
				if child.orientation == uc2const.HORIZONTAL:
					self.guides_grid[1].append(child.position)
				else:
					self.guides_grid[0].append(child.position)

	def update_objects_grid(self):
		self.objects_grid = [[], []]
		layers = self.presenter.get_visible_layers()
		for layer in layers:
			for obj in layer.childs:
				points = libgeom.bbox_middle_points(obj.cache_bbox)
				for point in points:
					self.objects_grid[0].append(point[0])
					self.objects_grid[1].append(point[1])

	def update_page_grid(self):
		self._calc_page_grid()

	def _calc_grid(self):
		grid_layer = self.methods.get_grid_layer()
		w, h = self.presenter.get_page_size()
		x, y, dx, dy = grid_layer.grid
		origin = self.presenter.model.doc_origin
		if origin == sk2_const.DOC_ORIGIN_LL:
			x0, y0 = self.canvas.point_doc_to_win([-w / 2.0 + x, -h / 2.0 + y])
			x0_doc, y0_doc = [-w / 2.0 + x, -h / 2.0 + y]
		elif origin == sk2_const.DOC_ORIGIN_LU:
			x0, y0 = self.canvas.point_doc_to_win([-w / 2.0 + x, h / 2.0 + y])
			x0_doc, y0_doc = [-w / 2.0 + x, h / 2.0 + y]
		else:
			x0, y0 = self.canvas.point_doc_to_win([x, y])
			x0_doc, y0_doc = [x, y]
		self.grid_doc = [x0_doc, y0_doc, dx, dy]
		dx = dx * self.canvas.zoom
		dy = dy * self.canvas.zoom
		sdist = config.snap_distance
		i = 0.0
		while dx < sdist + 3:
			i = i + 0.5
			dx = dx * 10.0 * i
			self.grid_doc[2] = self.grid_doc[2] * 10.0 * i
		if dx / 2.0 > sdist + 3:
			dx = dx / 2.0
			self.grid_doc[2] = self.grid_doc[2] / 2.0

		i = 0.0
		while dy < sdist + 3:
			i = i + 0.5
			dy = dy * 10.0 * i
			self.grid_doc[3] = self.grid_doc[3] * 10.0 * i
		if dy / 2.0 > sdist + 3:
			dy = dy / 2.0
			self.grid_doc[3] = self.grid_doc[3] / 2.0

		sx = (x0 / dx - math.floor(x0 / dx)) * dx
		sy = (y0 / dy - math.floor(y0 / dy)) * dy
		self.grid_win = [sx, sy, dx, dy]

	def _calc_page_grid(self):
		w, h = self.presenter.get_page_size()
		self.page_grid = [[-w / 2.0, 0.0, w / 2.0], [-h / 2.0, 0.0, h / 2.0]]

	def _snap_point_to_dict(self, point, doc_point, snap_dict):
		ret = False
		self.active_snap = [None, None]
		x = point[0]
		x_doc = doc_point[0]
		y = point[1]
		y_doc = doc_point[1]
		snap_dist = config.snap_distance / self.canvas.zoom

		if self.snap_x:
			for item in snap_dict[0]:
				if abs(item - doc_point[0]) < snap_dist:
					ret = True
					x = self.canvas.point_doc_to_win([item, doc_point[1]])[0]
					x_doc = item
					self.active_snap[0] = x_doc
					break

		if self.snap_y:
			for item in snap_dict[1]:
				if abs(item - doc_point[1]) < snap_dist:
					ret = True
					y = self.canvas.point_doc_to_win([doc_point[0], item])[1]
					y_doc = item
					self.active_snap[1] = y_doc
					break

		return ret, [x, y], [x_doc, y_doc]

	#---------- Point snapping --------------------

	def snap_point(self, point, win_point=True, snap_x=True, snap_y=True):
		self.snap_dict = {SNAP_TO_GRID:self.snap_to_grid,
						SNAP_TO_GUIDES:self.snap_to_guides,
						SNAP_TO_OBJECTS:self.snap_to_objects,
						SNAP_TO_PAGE:self.snap_to_page, }
		flag = False
		self.snap_x = snap_x
		self.snap_y = snap_y
		self.active_snap = [None, None]

		if win_point:
			result = [] + point
			result_doc = self.canvas.point_win_to_doc(point)
		else:
			result = self.canvas.point_doc_to_win(point)
			result_doc = [] + point
		for item in config.snap_order:
			if self.snap_dict[item]:
				flag, p, p_doc = self.snap_point_dict[item](result, result_doc)
				if flag:
					result = p
					result_doc = p_doc
					break
		return flag, result, result_doc

	def snap_point_to_grid(self, point, doc_point):
		ret = False
		self.active_snap = [None, None]
		x = point[0]
		x_doc = doc_point[0]
		y = point[1]
		y_doc = doc_point[1]
		p = self.canvas.point_win_to_doc([x, y])

		if self.snap_x:
			val = round((point[0] - self.grid_win[0]) / self.grid_win[2])
			val = int(val * self.grid_win[2] + self.grid_win[0])
			if abs(val - point[0]) <= config.snap_distance:
				ret = True
				x = val
				x_doc = round((p[0] - self.grid_doc[0]) / self.grid_doc[2])
				x_doc = x_doc * self.grid_doc[2] + self.grid_doc[0]
				self.active_snap[0] = x_doc

		if self.snap_y:
			val = round((point[1] - self.grid_win[1]) / self.grid_win[3])
			val = int(val * self.grid_win[3] + self.grid_win[1])
			if abs(val - point[1]) <= config.snap_distance:
				ret = True
				y = val
				y_doc = round((p[1] - self.grid_doc[1]) / self.grid_doc[3])
				y_doc = y_doc * self.grid_doc[3] + self.grid_doc[1]
				self.active_snap[1] = y_doc

		return ret, [x, y], [x_doc, y_doc]

	def snap_point_to_guides(self, point, doc_point):
		return self._snap_point_to_dict(point, doc_point, self.guides_grid)

	def snap_point_to_objects(self, point, doc_point):
		return self._snap_point_to_dict(point, doc_point, self.objects_grid)

	def snap_point_to_page(self, point, doc_point):
		return self._snap_point_to_dict(point, doc_point, self.page_grid)

	def is_over_guide(self, point):
		doc_point = self.canvas.point_win_to_doc(point)
		ret = False
		snap_dict = self.guides_grid
		if not snap_dict: return False, None

		pos = 0
		orient = 0
		snap_dist = config.snap_distance / (2.0 * self.canvas.zoom)

		for item in snap_dict[0]:
			if abs(item - doc_point[0]) < snap_dist:
				ret = True
				pos = item
				orient = uc2const.VERTICAL
				break

		for item in snap_dict[1]:
			if abs(item - doc_point[1]) < snap_dist:
				ret = True
				pos = item
				orient = uc2const.HORIZONTAL
				break

		if ret: self.active_guide = self.find_guide(pos, orient)
		return ret, self.active_guide

	def find_guide(self, pos, orient):
		guide_layer = self.methods.get_guide_layer()
		if not self.methods.is_layer_visible(guide_layer): return
		for child in guide_layer.childs:
			if child.is_guide():
				if child.orientation == orient and child.position == pos:
					return child
		return None
