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

from uc2 import libgeom
from uc2.formats.sk2 import sk2_model
from uc2.formats.sk2 import sk2_const

from sk1 import _, modes, config, events
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
	control_points = []
	cpoint = None
	new_node_flag = False
	new_node = None

	def __init__(self, canvas, presenter):
		AbstractController.__init__(self, canvas, presenter)

	def start_(self):
		self.start = []
		self.end = []
		self.control_points = []
		self.snap = self.presenter.snap
		self.target = self.selection.objs[0]
		self.selection.clear()
		self.update_paths()
		self.api.set_mode()

	def update_paths(self):
		self.set_selected_nodes()
		self.new_node = None
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
		self.new_node = None
		self.selected_nodes = []

	def escape_pressed(self):
		self.canvas.set_mode()

	#----- REPAINT

	def repaint(self):
		x0, y0, x1, y1 = self.target.cache_bbox
		p0 = self.canvas.point_doc_to_win([x0, y0])
		p1 = self.canvas.point_doc_to_win([x1, y1])
		self.canvas.renderer.draw_frame(p0, p1)
		for item in self.paths: item.repaint()
		for item in self.control_points: item.repaint()
		if self.new_node: self.new_node.repaint()


	def repaint_frame(self):
		self.canvas.renderer.cdc_draw_frame(self.start, self.end, True)

	def on_timer(self):
		if self.draw:
			self.repaint_frame()

	#----- MOUSE CONTROLLING

	def mouse_down(self, event):
		self.timer.stop()
		self.start = []
		self.end = []
		self.draw = False
		self.move_flag = False
		self.new_node_flag = False
		self.selected_obj = None
		self.start = event.get_point()
		self.cpoint = self.select_control_points_by_click(self.start)
		if not self.cpoint:
			points = self.select_point_by_click(self.start)
			if points:
				self.moved_node = points[0]
				if not self.moved_node in self.selected_nodes:
					self.set_selected_nodes(points, event.is_shift())
				self.move_flag = True
				self.new_node = None
			else:
				if self.is_path_clicked(self.start):
					self.new_node_flag = True
				else:
					self.new_node = None
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
				self.move_selected_points(self.moved_node, self.end, True)
			self.moved_node = None
			self.canvas.selection_redraw()
			self.move_flag = False
		elif self.cpoint:
			if not self.start == self.end:
				self.move_control_point(self.end, True)
		elif self.new_node_flag:
			self.new_node_flag = False
			self.set_new_node(self.end)
			self.canvas.selection_redraw()
		elif self.selected_obj:
			self.target = self.selected_obj
			self.canvas.restore_mode()
		else:
			if self.start == self.end:
				self.set_selected_nodes()
		self.selected_obj = None
		self.cpoint = None

	def mouse_move(self, event):
		if not self.start: return
		if self.cpoint:
			self.move_control_point(event.get_point())
		elif not self.move_flag:
			self.end = event.get_point()
			self.draw = True
		elif self.move_flag:
			self.move_selected_points(self.moved_node, event.get_point())
			self.move_flag = True

	def mouse_double_click(self, event):
		if self.new_node:
			self.insert_new_node()

	#----- POINT METHODS

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

	def select_control_points_by_click(self, win_point):
		for item in self.control_points:
			if item.is_pressed(win_point):
				return item
		return None

	def is_path_clicked(self, win_point):
		hit_surface = self.canvas.hit_surface
		for path in self.paths:
			if hit_surface.is_point_on_path(win_point, path.get_path()):
				return path
		return None

	def set_selected_nodes(self, points=[], add_flag=False):
		if points: self.new_node = None
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
		if len(self.selected_nodes) == 1:
			self.create_control_points()
		else:
			self.clear_control_points()
		events.emit(events.SELECTION_CHANGED, self.presenter)
		msg = _('No selected nodes')
		if self.selected_nodes:
			msg = _('Selected %d node(s)') % len(self.selected_nodes)
		events.emit(events.APP_STATUS, msg)
		self.canvas.selection_redraw()

	def clear_control_points(self):
		if self.control_points:
			for item in self.control_points: item.destroy()
			self.control_points = []

	def create_control_points(self):
		self.clear_control_points()
		cp = self.control_points
		for node in self.selected_nodes:
			before = node.get_point_before()
			after = node.get_point_after()
			if node.is_curve():
				cp.append(ControlPoint(self.canvas, node, before))
				cp.append(ControlPoint(self.canvas, node, node))
			if after and not after in self.selected_nodes:
				if after.is_curve():
					cp.append(ControlPoint(self.canvas, after, node))
					cp.append(ControlPoint(self.canvas, after, after))

	def select_all_nodes(self, invert=False):
		points = []
		for item in self.paths:
			points += item.get_all_points()
		self.set_selected_nodes(points, invert)

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

	def move_control_point(self, win_point, undable=False):
		if not self.cpoint: return
		x1, y1 = self.snap.snap_point(win_point)[2]
		x0, y0 = self.cpoint.get_point()
		trafo = [1.0, 0.0, 0.0, 1.0, x1 - x0, y1 - y0]
		self.cpoint.apply_trafo(trafo)
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

	def apply_changes(self):
		self.new_node = None
		self.new_node_flag = False
		paths = self.get_paths()
		self.api.set_new_paths(self.target, paths, self.orig_paths)
		self.orig_paths = paths

	def delete_selected_nodes(self):
		if not self.selected_nodes: return
		for item in self.selected_nodes:
			path = item.path
			if path in self.paths:
				path.delete_point(item)
				item.destroy()
				if not path.points:
					self.paths.remove(path)
		self.set_selected_nodes()
		if not self.get_paths():
			parent = self.target.parent
			index = parent.childs.index(self.target)
			self.api.delete_objects([[self.target, parent, index ], ])
			self.target = None
			self.canvas.restore_mode()
		else:
			self.apply_changes()

	def set_new_node(self, win_point):
		path = self.is_path_clicked(win_point)
		if not path is None:
			hit_surface = self.canvas.hit_surface
			segments = path.get_segments()
			segment = None
			for item in segments:
				start = item[0].point
				end = item[1].point
				if hit_surface.is_point_on_segment(win_point, start, end):
					segment = item
					break
			if segment and len(segment[1].point) > 2:
				before = segment[0]
				after = segment[1]
				t = hit_surface.get_t_parameter(win_point, start, end)
				new_p, new_end_p = libgeom.split_bezier_curve(start, end, t)
				self.new_node = NewPoint(self.canvas, new_p, new_end_p,
										before, after)
				self.set_selected_nodes()
			elif segment and len(segment[1].point) == 2:
				before = segment[0]
				after = segment[1]
				point = self.canvas.win_to_doc(win_point)
				new_p = libgeom.split_bezier_line(start, end, point)
				new_end_p = [] + after.point
				self.new_node = NewPoint(self.canvas, new_p, new_end_p,
										before, after)
				self.set_selected_nodes()

	def insert_new_node(self):
		if self.new_node:
			path = self.new_node.before.path
			np = BezierPoint(self.canvas, path, self.new_node.new_point)
			index = path.get_point_index(self.new_node.after)
			path.insert_point(np, index)
			self.new_node.after.point = self.new_node.new_end_point
			self.apply_changes()
			return np
		return None

	def can_be_line(self):
		if self.selected_nodes:
			for item in self.selected_nodes:
				if item.is_curve():
					return True
		elif self.new_node:
			return self.new_node.after.is_curve()
		return False

	def can_be_curve(self):
		if self.selected_nodes:
			for item in self.selected_nodes:
				if not item.is_curve():
					return True
		elif self.new_node:
			return not self.new_node.after.is_curve()
		return False

	def convert_to_line(self):
		flag = False
		if self.selected_nodes:
			for item in self.selected_nodes:
				if item.is_curve():
					item.convert_to_line()
					flag = True
		elif self.new_node:
			if self.new_node.after.is_curve():
				self.new_node.after.convert_to_line()
				flag = True
		if flag:
			self.apply_changes()
			if self.selected_nodes:
				nodes = self.selected_nodes
				self.set_selected_nodes()
				self.set_selected_nodes(nodes)
			else:
				events.emit(events.SELECTION_CHANGED, self.presenter)

	def convert_to_curve(self):
		flag = False
		if self.selected_nodes:
			for item in self.selected_nodes:
				if not item.is_curve():
					item.convert_to_curve()
					flag = True
		elif self.new_node:
			if not self.new_node.after.is_curve():
				self.new_node.after.convert_to_curve()
				flag = True
		if flag:
			self.apply_changes()
			if self.selected_nodes:
				nodes = self.selected_nodes
				self.set_selected_nodes()
				self.set_selected_nodes(nodes)
			else:
				events.emit(events.SELECTION_CHANGED, self.presenter)

	def can_be_splited_nodes(self):
		if self.selected_nodes:
			for item in self.selected_nodes:
				if not item.is_terminal():
					return True
		elif self.new_node:
			return True
		return False

	def can_be_joined_nodes(self):
		if len(self.selected_nodes) == 2:
			item0 = self.selected_nodes[0]
			item1 = self.selected_nodes[1]
			if item0.is_terminal() and item1.is_terminal():
				return True
		return False

	def can_be_deleted_seg(self):
		if len(self.selected_nodes) == 2:
			item0 = self.selected_nodes[0]
			item1 = self.selected_nodes[1]
			if item0.get_point_before() == item1 or \
			item0.get_point_after() == item1:
				return True
		elif self.new_node:
			return True
		return False

	def split_nodes(self):
		if self.selected_nodes:
			nodes = [] + self.selected_nodes
			self.set_selected_nodes()
			for item in nodes:
				self._split_node(item)
			self.apply_changes()
		elif self.new_node:
			self._split_node(self.insert_new_node())
			self.apply_changes()

	def _split_node(self, node):
		if not node.is_terminal():
			path = node.path
			index = path.get_point_index(node)
			np = node.get_copy()
			if np.is_curve(): np.point = np.point[2]
			if path.is_closed():
				path.closed = sk2_const.CURVE_OPENED
				if node.is_end():
					path.points = [path.start_point, ] + path.points
					path.start_point = np
				elif node.is_start(): pass
				else:
					new_points = path.points[index + 1:] + [path.start_point, ]
					new_points += path.points[:index + 1]
					path.points = new_points
					path.start_point = np
			elif not index is None:
				new_path = BezierPath(self.canvas)
				new_path.trafo = [] + path.trafo
				new_path.closed = sk2_const.CURVE_OPENED
				new_path.start_point = np
				new_path.points = path.points[index + 1:]
				for item in new_path.points: item.path = new_path
				np.path = new_path
				path.points = path.points[:index + 1]
				path_index = self.paths.index(path)
				self.paths.insert(path_index + 1, new_path)

	def join_nodes(self):
		item0 = self.selected_nodes[0]
		item1 = self.selected_nodes[1]
		self.set_selected_nodes()
		fn = libgeom.midpoint
		np = fn(item0.get_base_point(), item1.get_base_point())
		if item0.path == item1.path:
			item0.set_base_point([] + np)
			item1.set_base_point(np)
			item1.path.closed = sk2_const.CURVE_CLOSED
		else:
			if item0.is_start() and item1.is_start():
				item0.path.reverse()
			elif item0.is_end() and item1.is_end():
				item1.path.reverse()
			elif item0.is_start() and item1.is_end():
				item1, item0 = item0, item1
			item0.set_base_point([] + np)
			path1 = item1.path
			for item in path1.points:
				item.path = item0.path
			item0.path.points += path1.points
			path1.points = []
			self.paths.remove(path1)
			path1.destroy()
		self.apply_changes()

	def delete_seg(self):
		before = None
		after = None
		if self.new_node:
			before = self.new_node.before
			after = self.new_node.after
		elif self.selected_nodes:
			item0 = self.selected_nodes[0]
			item1 = self.selected_nodes[1]
			before = item0
			after = item1
			if item0.get_point_before() == item1:
				before = item1
				after = item0
		path = before.path
		if before.is_start() and after.is_end():
			self.paths.remove(path)
			path.destroy()
		elif before.is_start() and not path.is_closed():
			path.start_point = path.points[0]
			path.points = path.points[1:]
			path.start_point.convert_to_line()
		elif after.is_end() and not path.is_closed():
			path.points = path.points[:-1]
		else:
			self._split_node(before)
			path = after.path
			path.start_point = path.points[0]
			path.points = path.points[1:]
			path.start_point.convert_to_line()
		self.apply_changes()

	def add_seg(self):
		item0 = self.selected_nodes[0]
		item1 = self.selected_nodes[1]
		self.set_selected_nodes()
		if item0.path == item1.path:
			item1.path.closed = sk2_const.CURVE_CLOSED
		else:
			if item0.is_start() and item1.is_start():
				item0.path.reverse()
			elif item0.is_end() and item1.is_end():
				item1.path.reverse()
			elif item0.is_start() and item1.is_end():
				item1, item0 = item0, item1
			path1 = item1.path
			item1.path = item0.path
			for item in path1.points:
				item.path = item0.path
			item0.path.points += [item1, ] + path1.points
			path1.points = []
			path1.start_point = None
			self.paths.remove(path1)
			path1.destroy()
		self.apply_changes()

	def can_be_cusp(self):
		if self.selected_nodes:
			for item in self.selected_nodes:
				if item.can_be_cusp():
					return True
		return False

	def can_be_smooth(self):
		if self.selected_nodes:
			for item in self.selected_nodes:
				if item.can_be_smooth():
					return True
		return False

	def can_be_symmetrical(self):
		if self.selected_nodes:
			for item in self.selected_nodes:
				if item.can_be_symmetrical():
					return True
		return False

	def set_connection_type(self, conn_type=sk2_const.NODE_CUSP):
		if self.selected_nodes:
			for item in self.selected_nodes:
				item.set_connection_type(conn_type)
			sp = [] + self.selected_nodes
			self.set_selected_nodes()
			self.apply_changes()
			self.set_selected_nodes(sp)

class BezierPath:

	canvas = None
	start_point = None
	points = []
	closed = sk2_const.CURVE_OPENED
	trafo = []

	def __init__(self, canvas, path=None, trafo=[]):
		self.canvas = canvas
		if path and trafo:
			path = libgeom.apply_trafo_to_path(path, trafo)
			self.trafo = trafo
			self.start_point = BezierPoint(self.canvas, self, path[0])
			self.points = []
			for item in path[1]:
				self.points.append(BezierPoint(self.canvas, self, item))
			self.closed = path[2]

	def destroy(self):
		for item in [self.start_point, ] + self.points:
			if item: item.destroy()
		items = self.__dict__.keys()
		for item in items:
			self.__dict__[item] = None

	def is_closed(self):
		return self.closed == sk2_const.CURVE_CLOSED

	def get_all_points(self):
		return [self.start_point, ] + self.points

	def get_path(self):
		ret = [[], [], self.closed]
		inv_trafo = libgeom.invert_trafo(self.trafo)
		ret[0] = libgeom.apply_trafo_to_point(self.start_point.point, inv_trafo)
		for item in self.points:
			ret[1].append(libgeom.apply_trafo_to_point(item.point, inv_trafo))
		return ret

	def get_segments(self):
		ret = []
		start = self.start_point
		for item in self.points:
			ret.append((start, item))
			start = item
		if self.is_closed():
			ret.append([start, self.start_point])
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
		if not self.is_closed():
			rend.draw_start_node(self.start_point.get_screen_point(),
								self.start_point.selected)
		for item in self.points[:-1]:
			rend.draw_regular_node(item.get_screen_point(), item.selected)
		if not self.is_closed():
			rend.draw_last_node(self.points[-1].get_screen_point(),
							self.points[-1].selected)
		else:
			rend.draw_start_node(self.start_point.get_screen_point(),
							self.start_point.selected)
			rend.draw_last_node(self.points[-1].get_screen_point(),
							self.points[-1].selected)

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
			elif point == self.start_point:
				self.points[0].apply_trafo_before(trafo)

	def delete_point(self, point):
		if point in self.points:
			self.points.remove(point)
		elif point == self.start_point and self.points:
			self.start_point = self.points[0]
			self.points = self.points[1:]
			if not len(self.start_point.point) == 2:
				self.start_point.point = self.start_point.point[2]

	def get_point_index(self, point):
		if point in self.points:
			return self.points.index(point)
		return None

	def insert_point(self, point, index):
		if index is None:
			self.points.append(point)
		else:
			self.points.insert(index, point)

	def reverse(self):
		points = [self.start_point, ] + self.points
		points.reverse()
		data = []
		for index in range(len(points)):
			if points[index].is_curve() and data:
				p0 = [] + data[1]
				p1 = [] + data[0]
				p2 = [] + points[index].point[2]
				np = [p0, p1, p2, points[index].point[3]]
				data = deepcopy(points[index].point)
				points[index].point = np
			elif  points[index].is_curve() and not data:
				data = deepcopy(points[index].point)
				points[index].point = points[index].point[2]
			elif not points[index].is_curve() and data:
				p0 = [] + data[1]
				p1 = [] + data[0]
				p2 = [] + points[index].point
				points[index].point = [p0, p1, p2, data[3]]
				data = []
		self.start_point = points[0]
		self.points = points[1:]


class BezierPoint:

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

	def get_copy(self):
		return BezierPoint(self.canvas, self.path, deepcopy(self.point))

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

	def get_base_point(self):
		if self.is_curve(): return [] + self.point[2]
		return [] + self.point

	def set_base_point(self, point):
		if self.is_curve():
			self.point[2] = point
		else:
			self.point = point

	def get_point_before(self):
		if self.path.start_point == self: return None
		index = self.path.points.index(self)
		if not index: return self.path.start_point
		else: return self.path.points[index - 1]

	def get_point_after(self):
		if self.path.start_point == self: return self.path.points[0]
		index = self.path.points.index(self) + 1
		if index == len(self.path.points):return None
		else: return self.path.points[index]

	def is_curve(self):
		return len(self.point) > 2

	#=========

	def is_cusp(self):
		if self.is_curve():
			return self.point[3] == sk2_const.NODE_CUSP
		else:
			after = self.get_point_after()
			if after and after.is_curve() and not after.is_opp_smooth():
				return True
		return False

	def is_smooth(self):
		if self.is_curve():
			return self.point[3] in (sk2_const.NODE_SMOOTH,
									sk2_const.NODE_SMOOTH_BOTH)
		else:
			after = self.get_point_after()
			if after and after.is_curve() and after.is_opp_smooth():
				return True
		return False

	def is_opp_smooth(self):
		if self.is_curve():
			return self.point[3] in (sk2_const.NODE_SMOOTH_BOTH,
									sk2_const.NODE_SMOOTH_OPP,
									sk2_const.NODE_SYMM_SMOOTH)
		return False

	def is_symmetrical(self):
		if self.is_curve():
			return self.point[3] in (sk2_const.NODE_SYMMETRICAL,
									sk2_const.NODE_SYMM_SMOOTH)
		return False

	def can_be_cusp(self):
		if self.is_curve() and not self.is_cusp():
			return True
		elif not self.is_curve():
			after = self.get_point_after()
			if after and after.is_curve() and after.is_opp_smooth():
				return True
		return False

	def can_be_smooth(self):
		if self.is_curve() and not self.is_smooth():
			return True
		elif not self.is_curve():
			after = self.get_point_after()
			if after and after.is_curve() and not after.is_opp_smooth():
				return True
		return False

	def can_be_symmetrical(self):
		if self.is_curve() and not self.is_symmetrical():
			after = self.get_point_after()
			if after and after.is_curve():
				return True
		return False

	#=================

	def is_terminal(self):
		if not self.path.is_closed():
			if self.path.start_point == self:
				return True
			elif self.path.points[-1] == self:
				return True
		return False

	def is_start(self):
		return self.path.start_point == self

	def is_end(self):
		return self.path.points[-1] == self


	def convert_to_line(self):
		if self.is_curve():
			self.point = [] + self.point[2]

	def convert_to_curve(self):
		before = self.get_point_before()
		if not before is None and not self.is_curve():
			if before.is_curve():
				before_point = [] + before.point[2]
			else:
				before_point = [] + before.point
			point = [] + self.point
			x0 = 1.0 / 3.0 * (point[0] - before_point[0]) + before_point[0]
			y0 = 1.0 / 3.0 * (point[1] - before_point[1]) + before_point[1]
			x1 = 2.0 / 3.0 * (point[0] - before_point[0]) + before_point[0]
			y1 = 2.0 / 3.0 * (point[1] - before_point[1]) + before_point[1]
			self.point = [[x0, y0], [x1, y1], point, sk2_const.NODE_CUSP]

	def get_connection_type(self):
		if self.is_curve():
			return self.point[3]
		return None

	def set_connection_type(self, conn_type):
		if self.is_curve():
			if conn_type == sk2_const.NODE_CUSP and self.can_be_cusp():
				if self.is_opp_smooth():
					self.point[3] = sk2_const.NODE_SMOOTH_OPP
				else:
					self.point[3] = sk2_const.NODE_CUSP
			elif conn_type == sk2_const.NODE_SMOOTH and self.can_be_smooth():
				if self.point[3] in (sk2_const.NODE_SYMM_SMOOTH,
									sk2_const.NODE_SMOOTH_OPP):
					self.point[3] = sk2_const.NODE_SMOOTH_BOTH
				else:
					self.point[3] = sk2_const.NODE_SMOOTH
			elif conn_type == sk2_const.NODE_SYMMETRICAL \
			and self.can_be_symmetrical():
				if self.is_opp_smooth():
					self.point[3] = sk2_const.NODE_SYMM_SMOOTH
				else:
					self.point[3] = sk2_const.NODE_SYMMETRICAL
		else:
			if conn_type == sk2_const.NODE_CUSP and self.can_be_cusp():
				after = self.get_point_after()
				if after and after.is_curve() and after.is_opp_smooth():
					after.point[3] &= sk2_const.NODE_NOT_SMOOTH_OPP
					after.update_connection()
			elif conn_type == sk2_const.NODE_SMOOTH and self.can_be_smooth():
				after = self.get_point_after()
				if after and after.is_curve() and not after.is_opp_smooth():
					after.point[3] |= sk2_const.NODE_SMOOTH_OPP
					after.update_connection()
		self.update_connection()

	def update_connection(self):
		after = self.get_point_after()
		before = self.get_point_before()
		if after and after.is_curve():
			if self.is_symmetrical():
				after.point[0] = libgeom.contra_point(self.point[1],
													self.point[2])
			if self.is_smooth() and self.is_curve():
				after.point[0] = libgeom.contra_point(self.point[1],
												self.point[2], after.point[0])
		elif after and not after.is_curve():
			if self.is_smooth() and self.is_curve():
				l = libgeom.distance(self.point[2], after.point)
				if l:
					self.point[1] = libgeom.contra_point(after.point,
												self.point[2], self.point[1])
		if before and before.is_curve():
			if before.is_symmetrical():
				before.point[1] = libgeom.contra_point(self.point[0],
													before.point[2])
			if before.is_smooth() and self.is_curve():
				before.point[1] = libgeom.contra_point(self.point[0],
											before.point[2], before.point[1])
		elif before and not before.is_curve():
			if self.is_opp_smooth():
				p = before.get_point_before()
				if p:
					p = p.get_base_point()
					l = libgeom.distance(p, before.point)
					if l:
						self.point[0] = libgeom.contra_point(p,
												before.point, self.point[0])



class ControlPoint:

	canvas = None
	point = None
	base_point = None

	def __init__(self, canvas, point, base_point):
		self.canvas = canvas
		self.point = point
		self.base_point = base_point

	def destroy(self):
		items = self.__dict__.keys()
		for item in items:
			self.__dict__[item] = None

	def get_point(self):
		if self.point == self.base_point:
			return self.point.point[1]
		return self.point.point[0]

	def is_pressed(self, win_point):
		wpoint = self.canvas.point_doc_to_win(self.get_point())
		bbox = libgeom.bbox_for_point(wpoint, config.point_sensitivity_size)
		return libgeom.is_point_in_bbox(win_point, bbox)

	def get_screen_points(self):
		bp = self.base_point.point
		if self.base_point.is_curve(): bp = bp[2]
		bp = self.canvas.point_doc_to_win(bp)
		p = self.canvas.point_doc_to_win(self.get_point())
		return bp, p

	def apply_trafo(self, trafo):
		p = libgeom.apply_trafo_to_point(self.get_point(), trafo)
		if self.point == self.base_point:
			self.point.point[1] = p
		else:
			self.point.point[0] = p
		self.point.update_connection()

	def repaint(self):
		self.canvas.renderer.draw_control_point(*self.get_screen_points())

class NewPoint:

	canvas = None
	before = None
	after = None
	new_point = []
	new_end_point = []

	def __init__(self, canvas, new_point, new_end_point, before, after):
		self.canvas = canvas
		self.before = before
		self.after = after
		self.new_point = new_point
		self.new_end_point = new_end_point

	def get_screen_point(self):
		point = [] + self.new_point
		if len(self.new_point) > 2: point = [] + self.new_point[2]
		return self.canvas.doc_to_win(point)

	def repaint(self):
		self.canvas.renderer.draw_new_node(self.get_screen_point())

