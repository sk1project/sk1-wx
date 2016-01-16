# -*- coding: utf-8 -*-
#
#	Copyright (C) 2016 by Igor E. Novikov
#	Copyright (C) 2002 by Tamito KAJIYAMA
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


import math, cairo
from copy import deepcopy

from uc2 import libcairo

from bbox import is_bbox_overlap, is_bbox_in_bbox, sum_bbox, enlarge_bbox
from points import mult_point, add_points
from bezier_ops import bezier_base_point, get_paths_bbox
from cwrap import create_cpath

PRECISION = 8

def is_bezier(point):
	return len(point) > 2

def unpack_seg(seg):
	if is_bezier(seg): return [True, [seg[0], seg[1]] , seg[2], seg[3]]
	return [False, None, seg, None]

def pack_seg(seg_type, ctrls, node, cont):
	if not seg_type: return node
	return [ctrls[0], ctrls[1], node, cont]


class ObjHitSurface:

	surface = None
	ctx = None
	canvas = None
	cpaths = None

	def __init__(self, obj):
		self.obj = obj
		self.surface = cairo.ImageSurface(cairo.FORMAT_RGB24, 1, 1)
		self.ctx = cairo.Context(self.surface)

	def destroy(self):
		for item in self.__dict__.keys():
			self.__dict__[item] = None

	def clear(self):
		self.ctx.set_source_rgb(1, 1, 1)
		self.ctx.paint()
		self.ctx.set_source_rgb(0, 0, 0)

	def set_trafo(self, point):
		trafo = [1.0, 0.0, 0.0, 1.0, -point[0], -point[1]]
		self.ctx.set_matrix(libcairo.get_matrix_from_trafo(trafo))

	def check_point(self, point):
		self.clear()
		self.set_trafo(point)
		if self.cpaths is None: self.cpaths = self.obj.get_cpaths()
		self.ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
		self.ctx.new_path()
		self.ctx.append_path(self.cpaths)
		self.ctx.fill()
		self.ctx.set_line_width(2.0)
		self.ctx.new_path()
		self.ctx.append_path(self.cpaths)
		self.ctx.stroke()
		return not libcairo.check_surface_whiteness(self.surface)


#--- HASHABLE CONTAINERS

class CurveObject:

	obj_id = None
	path_objs = None
	hit_test = None

	def __init__(self, paths, obj_id=0):
		self.path_objs = []
		self.obj_id = obj_id
		for path in paths:
			self.path_objs.append(PathObject(path, obj_id))

	def destroy(self):
		if self.hit_test: self.hit_test.destroy()
		for item in self.__dict__.keys():
			self.__dict__[item] = None

	def get_bbox(self):
		self.path_objs[0].update_bbox()
		bbox = [] + self.path_objs[0].bbox
		for i in range(1, len(self.path_objs)):
			self.path_objs[i].update_bbox()
			bbox = sum_bbox(bbox, self.path_objs[i].bbox)
		return bbox

	def update_bbox(self):
		self.bbox = self.get_bbox()

	def paths(self):
		return self.path_objs

	def get_cpaths(self):
		paths = []
		for item in self.path_objs:
			paths.append(item.get_path())
		return create_cpath(paths)

	def is_point_inside(self, point):
		if self.hit_test is None:
			self.hit_test = ObjHitSurface(self)
		return self.hit_test.check_point(point)

class PathObject:

	bbox = []
	path = []
	cp_indexes = []
	obj_id = 0
	cp_dict = {}
	start_id = None
	end_id = None

	def __init__(self, path, obj_id=0):
		self.path = path
		self.cp_indexes = []
		self.cp_dict = {}
		self.obj_id = obj_id

	def update_bbox(self):
		self.bbox = get_paths_bbox([self.path, ])

	def get_path(self):
		return deepcopy(self.path)

	def get_segments(self):
		return deepcopy(self.path[1])

	def get_points(self):
		result = [self.get_start_point(), ]
		for item in self.get_segments():
			result.append(bezier_base_point(item))
		return result

	def get_len(self):
		return len(self.path[1])

	def get_start_point(self):
		return [] + self.path[0]

	def copy(self):
		return PathObject(deepcopy(self.path))

	def is_closed(self):
		return self.path[-1] == 1

	def close_path(self):
		self.path[-1] = 1
		if not self.path[0] == bezier_base_point(self.path[1][-1]):
			self.path[1].append(self.get_start_point())

	def unclose_path(self):
		self.path[-1] = 0

	def append_seg(self, seg):
		self.path[1].append(seg)
		self.path[-1] = 0

	def append_segs(self, segs):
		self.path[1] += segs

	def get_seg(self, index):
		return [] + self.path[1][index]

	def get_node(self, index):
		index -= 1
		if index < 0: return self.get_start_point()
		return deepcopy(self.path[1][index])

	def get_test_point(self, index=0):
		if index >= len(self.path[1]):
			index = len(self.path[1]) - 1
		if not index:
			base_point = self.get_start_point()
		else:
			base_point = bezier_base_point(self.get_seg(index - 1))
		point = self.get_seg(index)
		return self.split_seg(base_point, point)[1]

	def split_seg(self, base_point, point, t=0.5):
		if is_bezier(point):
			p0 = base_point
			p1, p2, p3 = point[:3]
			t2 = 1.0 - t
			r = add_points(mult_point(p1, t2) , mult_point(p2, t))
			q1 = add_points(mult_point(p0, t2), mult_point(p1, t))
			q2 = add_points(mult_point(q1, t2), mult_point(r, t))
			q5 = add_points(mult_point(p2, t2), mult_point(p3, t))
			q4 = add_points(mult_point(r, t2), mult_point(q5, t))
			q3 = add_points(mult_point(q2, t2), mult_point(q4, t))
			return [[q1, q2, [] + q3, 0], q3, [q4, q5, [] + p3, 0]]
		else:
			new_point = add_points(mult_point(base_point, (1.0 - t)),
						mult_point(point, t))
			return [new_point, [] + new_point, None]

	def split_path_at(self, at, cross_id=0):
		index = int(at)
		t = at - index
		if not at or at == float(self.get_len() - 1):
			new_path = deepcopy(self.path)
			new_path[-1] = 0
			path_obj = PathObject(new_path)
			path_obj.start_id = path_obj.end_id = cross_id
			path_obj.obj_id = self.obj_id
			return[path_obj, ]
		elif not t:
			segs = self.get_segments()
			new_segs1 = segs[:index]
			start1 = self.get_start_point()
			new_segs2 = segs[index:]
			start2 = bezier_base_point(self.get_node(index))
		else:
			segs = self.get_segments()
			base_point = bezier_base_point(self.get_node(index))
			end, start2, seg0 = self.split_seg(base_point, segs[index], t)
			new_segs1 = segs[:index] + [end, ]
			start1 = self.get_start_point()
			new_segs2 = segs[index:]
			if not seg0 is None: new_segs2[0] = seg0
		path_obj1 = PathObject([start1, new_segs1, 0])
		path_obj1.start_id = self.start_id
		path_obj1.end_id = cross_id
		path_obj1.obj_id = self.obj_id
		path_obj2 = PathObject([start2, new_segs2, 0])
		path_obj2.start_id = cross_id
		path_obj2.obj_id = self.obj_id
		path_obj2.end_id = self.end_id
		return[path_obj1, path_obj2]

	def split(self):
		if self.cp_indexes:
			self.cp_indexes.sort()
			self.cp_indexes.reverse()
			target = self
			result = []
			previous_at = None
			self.unclose_path()
			for at in self.cp_indexes:
				real_at = at
				if not previous_at is None and int(previous_at) == int(at):
					real_at = (at - int(at)) / (previous_at - int(previous_at))
					real_at += int(at)
				pths = target.split_path_at(real_at, self.cp_dict[at])
				previous_at = at
				target = pths[0]
				result = pths[1:] + result
			result[-1].append_segs(target.get_segments())
			result[-1].end_id = target.end_id
			return result
		else:
			return [self, ]

	def reverse_path(self):
		start_point = self.get_start_point()
		points = [start_point, ] + self.get_segments()
		points.reverse()
		data = []
		for index in range(len(points)):
			if is_bezier(points[index]) and data:
				p0 = [] + data[1]
				p1 = [] + data[0]
				p2 = [] + points[index][2]
				np = [p0, p1, p2, points[index][3]]
				data = deepcopy(points[index])
				points[index] = np
			elif is_bezier(points[index]) and not data:
				data = deepcopy(points[index])
				points[index] = points[index][2]
			elif not is_bezier(points[index]) and data:
				p0 = [] + data[1]
				p1 = [] + data[0]
				p2 = [] + points[index]
				points[index] = [p0, p1, p2, data[3]]
				data = []
		start = points[0]
		segs = points[1:]
		new_path_obj = PathObject([start, segs, 0])
		new_path_obj.start_id = self.end_id
		new_path_obj.end_id = self.start_id
		return new_path_obj

	def join_path(self, path_obj):
		if self.end_id == path_obj.end_id:
			path_obj = path_obj.reverse_path()
		start = self.get_start_point()
		segs = self.get_segments() + path_obj.get_segments()
		new_path_obj = PathObject([start, segs, 0])
		new_path_obj.start_id = self.start_id
		new_path_obj.end_id = path_obj.end_id
		return new_path_obj

#--- PATH APPROXIMATION

def subdivide(m, n, t=0.5):
	return m + t * (n - m)

def subdivide_curve(p0, p1, p2, p3, threshold=1.0, r=(0.0, 1.0)):
	"""
	Subdivide curve recursively so that all line segments get shorter
	than the specified threshold.
	"""
	ret = []
	p10 = [subdivide(p0[0], p1[0]), subdivide(p0[1], p1[1])]
	p11 = [subdivide(p1[0], p2[0]), subdivide(p1[1], p2[1])]
	p12 = [subdivide(p2[0], p3[0]), subdivide(p2[1], p3[1])]
	p20 = [subdivide(p10[0], p11[0]), subdivide(p10[1], p11[1])]
	p21 = [subdivide(p11[0], p12[0]), subdivide(p11[1], p12[1])]
	p30 = [subdivide(p20[0], p21[0]), subdivide(p20[1], p21[1])]
	t = subdivide(r[0], r[1])
	if math.hypot(p0[0] - p30[0], p0[1] - p30[1]) > threshold:
		ret.extend(subdivide_curve(p0, p10, p20, p30, threshold, (r[0], t)))
	ret.append((p30, t))
	if math.hypot(p30[0] - p3[0], p30[1] - p3[1]) > threshold:
		ret.extend(subdivide_curve(p30, p21, p12, p3, threshold, (t, r[1])))
	return ret

def approximate_path(path_obj):
	buff = []
	last = path_obj.get_start_point()
	buff.append((last, 0.0))
	for i in range(path_obj.get_len()):
		stype, control, point = unpack_seg(path_obj.get_seg(i))[:-1]
		if stype:
			for p, t in subdivide_curve(last, control[0], control[1], point):
				buff.append((p, i + t))
			buff.append((point, float(i + 1)))
		else:
			buff.append((point, float(i + 1)))
		last = point
	return buff


#--- PATH INTERSECTION

def coord_rect(points):
	p = points[0][0]
	x1 = x2 = p[0]
	y1 = y2 = p[1]
	for i in range(1, len(points)):
		p = points[i][0]
		x1 = min(x1, p[0])
		x2 = max(x2, p[0])
		y1 = min(y1, p[1])
		y2 = max(y2, p[1])
	return [x1, y1, x2, y2]

def equal(point1, point2):
	return round(point1[0], PRECISION) == round(point2[0], PRECISION) and \
			round(point1[1], PRECISION) == round(point2[1], PRECISION)

def in_range(p, a, b):
	x_min = round(min(a[0], b[0]), PRECISION)
	x_max = round(max(a[0], b[0]), PRECISION)
	y_min = round(min(a[1], b[1]), PRECISION)
	y_max = round(max(a[1], b[1]), PRECISION)
	return x_min <= round(p[0], PRECISION) <= x_max and \
			y_min <= round(p[1], PRECISION) <= y_max

def intersect_lines(p0, p1, p2, p3):
	a1 = p1[0] - p0[0]
	a2 = p3[0] - p2[0]
	b1 = p0[1] - p1[1]
	b2 = p2[1] - p3[1]
	if b1 * a2 - b2 * a1 == 0 or b2 * a1 - b1 * a2 == 0:
		return None
	c1 = p0[0] * p1[1] - p1[0] * p0[1]
	c2 = p2[0] * p3[1] - p3[0] * p2[1]
	cp = [(a1 * c2 - a2 * c1) / (b1 * a2 - a1 * b2),
		(b1 * c2 - b2 * c1) / (a1 * b2 - b1 * a2)]
	if in_range(cp, p0, p1) and  in_range(cp, p2, p3):
		return cp
	return None

def index(cp, p0, t0, p1, t1):
	if p1[0] - p0[0] == 0:
		return subdivide(t0, t1, (cp[1] - p0[1]) / (p1[1] - p0[1]))
	else:
		return subdivide(t0, t1, (cp[0] - p0[0]) / (p1[0] - p0[0]))

def intersect_objects(curve_objs):
	# approximate paths of each object
	approx_paths = []
	for i in range(len(curve_objs)):
		paths = curve_objs[i].paths()
		for j in range(len(paths)):
			approx_path = approximate_path(paths[j])
			if len(approx_path) < 2:
				continue
			# for better performance, group every 10 line segments
			partials = []
			for k in range(0, len(approx_path), 10):
				partial = approx_path[k:k + 11]
				partials.append((paths[j], partial, coord_rect(partial)))
			if len(partials[-1]) == 1:
				partial = partials.pop()
				partials[-1].extend(partial)
			assert 1 not in map(len, partials)
			approx_paths.append(partials)
	# find intersections for each pair of approximated paths
	cross_point_id = 0
	for i in range(len(approx_paths)):
		for j in range(i + 1, len(approx_paths)):
			for path1, approx_path1, rect1 in approx_paths[i]:
				for path2, approx_path2, rect2 in approx_paths[j]:
					if not path1.obj_id == path2.obj_id and \
								is_bbox_overlap(rect1, rect2):
						for p in range(1, len(approx_path1)):
							(p0, t0), (p1, t1) = approx_path1[p - 1:p + 1]
							for q in range(1, len(approx_path2)):
								(p2, t2), (p3, t3) = approx_path2[q - 1:q + 1]
								if equal(p0, p2):
									cp = p0
								elif equal(p0, p3) or \
										equal(p1, p2) or \
										equal(p1, p3):
									cp = None
								else:
									cp = intersect_lines(p0, p1, p2, p3)
								if cp is not None:
									index1 = index(cp, p0, t0, p1, t1)
									index2 = index(cp, p2, t2, p3, t3)
									path1.cp_indexes.append(index1)
									path1.cp_dict[index1] = cross_point_id
									path2.cp_indexes.append(index2)
									path2.cp_dict[index2] = cross_point_id
									cross_point_id += 1
	result = []
	for obj in curve_objs:
		for path in obj.paths():
			result += path.split()
	return result


def find_cross_id(path_objs, cross_id, obj_id):
	for item in path_objs:
		if item.end_id == cross_id or item.start_id == cross_id:
			return item
	return None

def contained(curve_obj, path_obj):
	for item in path_obj.get_points():
		if not curve_obj.is_point_inside(item):
			return False
	if path_obj.get_len() < 10:
		for i in range(path_obj.get_len()):
			if not curve_obj.is_point_inside(path_obj.get_test_point(i)):
				return False
	return True


#--- MODULE INTERFACE

def intersect_paths(paths1, paths2):
	objs = [CurveObject(paths1, 0), CurveObject(paths2, 1)]
	new_paths = intersect_objects(objs)
	if not new_paths: return None

	buff = []
	closed_paths = []
	for item in new_paths:
		if contained(objs[abs(item.obj_id - 1)], item):
			if item.is_closed():
				closed_paths.append(item)
			else:
				buff.append(item)

	while len(buff):
		start = buff[0]

		if start.start_id == start.end_id:
			start.close_path()
			closed_paths.append(start)
			buff.remove(start)
			continue
		cont = find_cross_id(buff[1:], start.end_id, start.obj_id)
		if cont:
			start = start.join_path(cont)
			buff.remove(cont)
			buff = [start, ] + buff[1:]
		else:
			closed_paths.append(start)
			buff = buff[1:]

	result = []
	for item in closed_paths:
		result.append(item.get_path())

	for obj in objs: obj.destroy()
	return result
