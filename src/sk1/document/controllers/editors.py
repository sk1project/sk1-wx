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

from copy import deepcopy

from uc2 import uc2const, libgeom
from uc2.formats.sk2 import sk2_model
from uc2.formats.sk2 import sk2_const

from sk1 import modes, config, events
from generic import AbstractController

class EditorChooser(AbstractController):

	mode = modes.SHAPER_MODE

	def __init__(self, canvas, presenter):
		AbstractController.__init__(self, canvas, presenter)

	def start_(self):
		sel_objs = self.selection.objs
		if len(sel_objs) == 1 and sel_objs[0].cid == sk2_model.CURVE:
			self.canvas.set_temp_mode(modes.BEZIER_EDITOR_MODE)
		else:
			self.selection.clear()

	def restore(self):
		self.timer.start()

	def stop_(self):pass

	def on_timer(self):
		self.timer.stop()
		self.start_()

	def mouse_down(self, event):pass

	def mouse_up(self, event):
		self.end = event.get_point()
		self.do_action()

	def mouse_move(self, event):pass

	def do_action(self):
		objs = self.canvas.pick_at_point(self.end)
		if objs and objs[0].cid > sk2_model.PRIMITIVE_CLASS \
		and not objs[0].cid == sk2_model.PIXMAP:
			self.selection.set([objs[0], ])
			self.start_()

class BezierEditor(AbstractController):

	mode = modes.BEZIER_EDITOR_MODE
	target = None
	paths = []
	orig_paths = []
	selected_nodes = []
	move_flag = False
	moved_node = None
	selected_obj = None

	def __init__(self, canvas, presenter):
		AbstractController.__init__(self, canvas, presenter)

	def start_(self):
		self.start = []
		self.end = []
		self.snap = self.presenter.snap
		self.target = self.selection.objs[0]
		self.selection.clear()
		self.update_paths()
		self.api.set_mode()

	def update_paths(self):
		self.selected_nodes = []
		self.orig_paths = deepcopy(self.target.paths)
		for item in self.paths: item.destroy()
		self.paths = []
		for item in self.target.paths:
			if not item[1]:continue
			pth = BezierPath(self.canvas, item, self.target.trafo)
			self.paths.append(pth)
		self.canvas.selection_redraw()

	def stop_(self):
		self.selection.set([self.target, ])
		self.target = None
		self.selected_obj = None
		for item in self.paths: item.destroy()
		self.paths = []
		self.start = []
		self.end = []

	def escape_pressed(self):
		self.canvas.set_mode()

	def repaint(self):
		x0, y0, x1, y1 = self.target.cache_bbox
		p0 = self.canvas.point_doc_to_win([x0, y0])
		p1 = self.canvas.point_doc_to_win([x1, y1])
		self.canvas.renderer.draw_frame(p0, p1)
		for item in self.paths:
			item.repaint()

	def repaint_frame(self):
		self.canvas.renderer.cdc_draw_frame(self.start, self.end, True)

	def on_timer(self):
		if self.draw:
			self.repaint_frame()

	def mouse_down(self, event):
		self.timer.stop()
		self.start = []
		self.end = []
		self.draw = False
		self.move_flag = False
		self.selected_obj = None
		self.start = event.get_point()
		points = self.select_point_by_click(self.start)
		if points:
			self.moved_node = points[0]
			if not self.moved_node in self.selected_nodes:
				self.set_selected_nodes(points, event.is_shift())
			self.move_flag = True
		else:
			objs = self.canvas.pick_at_point(self.start)
			if objs and not objs[0] == self.target and \
			objs[0].cid > sk2_model.PRIMITIVE_CLASS \
			and not objs[0].cid == sk2_model.PIXMAP:
				self.selected_obj = objs[0]
			self.timer.start()

	def mouse_up(self, event):
		self.timer.stop()
		self.end = event.get_point()
		if self.draw:
			self.draw = False
			points = self.select_points_by_bbox(self.start + self.end)
			self.set_selected_nodes(points, event.is_shift())
			self.start = []
			self.end = []
			self.canvas.selection_redraw()
		elif self.move_flag:
			if not self.start == self.end:
				self.move_selected_points(self.moved_node,
										event.get_point(), True)
			self.moved_node = None
			self.canvas.selection_redraw()
			self.move_flag = False
		elif self.selected_obj:
			self.target = self.selected_obj
			self.canvas.restore_mode()
		else:
			if self.start == self.end:
				self.set_selected_nodes([])
				self.canvas.selection_redraw()
		self.selected_obj = None

	def mouse_move(self, event):
		if self.start and not self.move_flag:
			self.end = event.get_point()
			self.draw = True
		elif self.start and self.move_flag:
			self.move_selected_points(self.moved_node, event.get_point())
			self.canvas.selection_redraw()
			self.move_flag = True

	def select_points_by_bbox(self, bbox):
		ret = []
		bbox = self.canvas.bbox_win_to_doc(bbox)
		for item in self.paths:
			ret += item.select_points_by_bbox(bbox)
		return ret

	def select_point_by_click(self, win_point):
		paths = [] + self.paths
		paths.reverse()
		for item in paths:
			point = item.pressed_point(win_point)
			if point: return [point, ]
		return []

	def set_selected_nodes(self, points, add_flag=False):
		if not add_flag:
			for item in self.selected_nodes:
				item.selected = False
			self.selected_nodes = []
		for item in points:
			if item.selected and item in self.selected_nodes:
				item.selected = False
				self.selected_nodes.remove(item)
			else:
				item.selected = True
				self.selected_nodes.append(item)
		events.emit(events.SELECTION_CHANGED, self.presenter)

	def select_all_nodes(self, invert=False):
		points = []
		for item in self.paths:
			points += item.get_all_points()
		self.set_selected_nodes(points, invert)
		self.canvas.selection_redraw()

	def move_selected_points(self, base_point, win_point, undable=False):
		x1, y1 = self.snap.snap_point(win_point)[2]
		if len(base_point.point) == 2:
			x0, y0 = [] + base_point.point
		else:
			x0, y0 = [] + base_point.point[2]
		trafo = [1.0, 0.0, 0.0, 1.0, x1 - x0, y1 - y0]
		for item in self.selected_nodes:
			item.path.apply_trafo_to_point(item, trafo)
		paths = self.get_paths()
		if undable:
			self.api.set_new_paths(self.target, paths, self.orig_paths)
			self.orig_paths = paths
		else:
			self.api.set_temp_paths(self.target, paths)

	def get_paths(self):
		ret = []
		for item in self.paths:
			ret.append(item.get_path())
		return ret

	def delete_selected_nodes(self):
		if not self.selected_nodes: return
		for item in self.selected_nodes:
			item.path.delete_point(item)
			if not item.path.points:
				self.paths.remove(item.path)
			item.destroy()
		self.selected_nodes = []
		paths = self.get_paths()
		if not paths:
			parent = self.target.parent
			index = parent.childs.index(self.target)
			self.api.delete_objects([[self.target, parent, index ], ])
			self.target = None
			self.canvas.restore_mode()
		else:
			self.api.set_new_paths(self.target, paths, self.orig_paths)
			self.orig_paths = paths


class BezierPath:

	canvas = None
	start_point = []
	points = []
	closed = sk2_const.CURVE_CLOSED
	trafo = []

	def __init__(self, canvas, path, trafo):
		self.canvas = canvas
		path = libgeom.apply_trafo_to_path(path, trafo)
		self.trafo = trafo
		self.start_point = BerzierNode(self.canvas, self, path[0])
		self.points = []
		for item in path[1]:
			self.points.append(BerzierNode(self.canvas, self, item))
		self.closed = path[2]

	def destroy(self):
		for item in [self.start_point, ] + self.points:
			item.destroy()
		items = self.__dict__.keys()
		for item in items:
			self.__dict__[item] = None

	def get_all_points(self):
		return [self.start_point, ] + self.points

	def get_path(self):
		ret = [[], [], self.closed]
		inv_trafo = libgeom.invert_trafo(self.trafo)
		ret[0] = libgeom.apply_trafo_to_point(self.start_point.point, inv_trafo)
		for item in self.points:
			ret[1].append(libgeom.apply_trafo_to_point(item.point, inv_trafo))
		return ret

	def pressed_point(self, win_point):
		points = [self.start_point, ] + self.points
		points.reverse()
		for item in points:
			if item.is_pressed(win_point):
				return item
		return None

	def repaint(self):
		rend = self.canvas.renderer
		if not self.closed == sk2_const.CURVE_CLOSED:
			rend.draw_start_node(self.start_point.get_screen_point(),
								self.start_point.selected)
		for item in self.points[:-1]:
			rend.draw_regular_node(item.get_screen_point(), item.selected)
		if not self.closed == sk2_const.CURVE_CLOSED:
			rend.draw_last_node(self.points[-1].get_screen_point(),
							self.points[-1].selected)
		else:
			rend.draw_regular_node(self.points[-1].get_screen_point(),
							self.points[-1].selected)
			rend.draw_last_node(self.start_point.get_screen_point(),
							self.start_point.selected)

	def select_points_by_bbox(self, bbox):
		ret = []
		if libgeom.is_point_in_bbox(self.start_point.point, bbox):
			ret.append(self.start_point)
		for item in self.points:
			if libgeom.is_point_in_bbox(item.point, bbox):
				ret.append(item)
		return ret

	def apply_trafo_to_point(self, point, trafo):
		if point in self.points + [self.start_point, ]:
			point.apply_trafo(trafo)
			if not point == self.points[-1] and not point == self.start_point:
				index = self.points.index(point) + 1
				self.points[index].apply_trafo_before(trafo)

	def delete_point(self, point):
		if point in self.points:
			self.points.remove(point)
		elif point == self.start_point and self.points:
			self.start_point = self.points[0]
			self.points = self.points[1:]
			if not len(self.start_point.point) == 2:
				self.start_point.point = self.start_point.point[2]


class BerzierNode:

	point = []
	canvas = None
	path = None
	selected = False

	def __init__(self, canvas, path, point):
		self.canvas = canvas
		self.point = point
		self.path = path

	def destroy(self):
		items = self.__dict__.keys()
		for item in items:
			self.__dict__[item] = None

	def is_pressed(self, win_point):
		wpoint = self.canvas.point_doc_to_win(self.point)
		if not len(wpoint) == 2:wpoint = wpoint[2]
		bbox = libgeom.bbox_for_point(wpoint, config.point_sensitivity_size)
		return libgeom.is_point_in_bbox(win_point, bbox)

	def get_screen_point(self):
		wpoint = self.canvas.point_doc_to_win(self.point)
		if len(wpoint) == 2:
			return wpoint
		else:
			return wpoint[2]

	def apply_trafo(self, trafo):
		if len(self.point) == 2:
			self.point = libgeom.apply_trafo_to_point(self.point, trafo)
		else:
			p0, p1, p2, marker = deepcopy(self.point)
			p1 = libgeom.apply_trafo_to_point(p1, trafo)
			p2 = libgeom.apply_trafo_to_point(p2, trafo)
			self.point = [p0, p1, p2, marker]

	def apply_trafo_before(self, trafo):
		if not len(self.point) == 2:
			p0, p1, p2, marker = deepcopy(self.point)
			p0 = libgeom.apply_trafo_to_point(p0, trafo)
			self.point = [p0, p1, p2, marker]
