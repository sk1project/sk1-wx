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

#base.intersect_objects([object1, object2])
#base.contained(path, container)
#base.join(parts1)

import math
import UserDict
from copy import deepcopy

from bbox import is_bbox_overlap
from points import mult_point, add_points
from bezier_ops import bezier_base_point

PRECISION = 8

def is_bezier(point):
	return len(point) > 2

def unpack_seg(seg):
	if is_bezier(seg): return [True, [seg[0], seg[1]] , seg[2], seg[3]]
	return [False, None, seg, None]

def pack_seg(seg_type, ctrls, node, cont):
	if not seg_type: return node
	return [ctrls[0], ctrls[1], node, cont]



#--- HASHABLE CONTAINERS

class CurveObject:

	path_objs = None

	def __init__(self, paths):
		self.path_objs = []
		for path in paths:
			self.path_objs.append(PathObject(path))

	def paths(self):
		return self.path_objs

class PathObject:

	path = []

	def __init__(self, path):
		self.path = path

	def get_segments(self):
		return deepcopy(self.path[1])

	def get_len(self):
		if self.is_closed(): return len(self.path[1])
		return len(self.path[1]) + 1

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

	def split_path_at(self, at):
		index = int(at)
		t = at - index
		if self.is_closed():
			if not at or at == float(self.get_len()):
				new_path = deepcopy(self.path)
				new_path[-1] = 0
				return[PathObject(new_path), ]
			elif not t:
				segs = self.get_segments()
				new_segs = segs[index:] + segs[:index]
				start = bezier_base_point(segs[index - 1])
				return[PathObject([start, new_segs, 0]), ]
			else:
				segs = self.get_segments()
				base_point = bezier_base_point(segs[index - 1])
				end, start, seg0 = self.split_seg(base_point, segs[index], t)
				new_segs = segs[index:] + segs[:index] + [end, ]
				if not seg0 is None: new_segs[0] = seg0
				return[PathObject([start, new_segs, 0]), ]
		else:
			if not at or at == float(self.get_len() - 1):
				new_path = deepcopy(self.path)
				new_path[-1] = 0
				return[PathObject(new_path), ]
			elif not t:
				segs = self.get_segments()
				new_segs1 = segs[:index]
				start1 = self.get_start_point()
				new_segs2 = segs[index:]
				start2 = bezier_base_point(segs[index - 1])
				return[PathObject([start1, new_segs1, 0]),
					PathObject([start2, new_segs2, 0])]
			else:
				segs = self.get_segments()
				base_point = bezier_base_point(segs[index - 1])
				end, start2, seg0 = self.split_seg(base_point, segs[index], t)
				new_segs1 = segs[:index] + [end, ]
				start1 = self.get_start_point()
				new_segs2 = segs[index:]
				if not seg0 is None: new_segs2[0] = seg0
				return[PathObject([start1, new_segs1, 0]),
					PathObject([start2, new_segs2, 0])]

	def append_seg(self, seg):
		self.path[1].append(seg)

	def get_seg(self, index):
		return [] + self.path[1][index]

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
	points = path_obj.get_segments()
	ret = []
	last = path_obj.get_start_point()
	for i in range(len(points)):
		if is_bezier(points[i]):
			control0, control1, point = points[i]
			for p, t in subdivide_curve(last, control0, control1, point):
				ret.append((p, i - 1.0 + t))
			ret.append((point, float(i)))
		else:
			point = points[i]
			ret.append((point, float(i)))
		last = point
	return ret

#--- PATH INTERSECTION

class IntersectionIndex(UserDict.UserDict):

	def add(self, curve_obj, path_obj, index, cp):
		index_table = self[curve_obj] = self.get(curve_obj, {})
		segment_table = index_table[path_obj] = index_table.get(path_obj, {})
		segment = int(index)
		indexes = segment_table[segment] = segment_table.get(segment, [])
		indexes.append([index - segment, cp])

	def adjust(self):
		for index_table in self.values():
			for segment_table in index_table.values():
				for indexes in segment_table.values():
					indexes.sort()
					for i in range(len(indexes)):
						r = 1.0 - indexes[i][0]
						for j in range(i + 1, len(indexes)):
							indexes[j][0] = (indexes[j][0] - indexes[i][0]) / r

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

def tidy(path):
	# remove redundant node at the end of the path
	if path.get_len() > 1:
		segs = path.get_segments()
		if not is_bezier(segs[-1]) and segs[-1] == bezier_base_point(segs[-2]):
			start_point = path.get_start_point()
			marker = 0
			if path.is_closed(): marker = 1
			return PathObject([start_point, segs[:-1], marker])
	return path

def split_paths(curve_obj, index_table):
	buff = []
	paths = curve_obj.paths()
	for i in index_table.keys():
		segments = index_table[i].keys()
		segments.sort()
		first = last = None
		for j in range(len(segments)):
			segment = segments[j]
			for index, cp in index_table[i][segment]:
				index = index + segment
				if j > 0 and segment > 0:
					index = index - segments[j - 1]
				result = paths[i].split_path_at(index)
				if paths[i].is_closed():
					paths[i] = result[0]
					first = cp
				else:
					paths[i] = result[1]
					path = tidy(result[0])
					if path.len > 1:
						buff.append((last, path, cp))
				segment = 0
				last = cp
		assert first is not None
		path = tidy(paths[i])
		if path.get_len() > 1:
			buff.append((last, path, first))
	return buff

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
				partials.append((i, j, partial, coord_rect(partial)))
			if len(partials[-1]) == 1:
				partial = partials.pop()
				partials[-1].extend(partial)
			assert 1 not in map(len, partials)
			approx_paths.append(partials)
	# find intersections for each pair of approximated paths
	table = IntersectionIndex()
	for i in range(len(approx_paths)):
		for j in range(i + 1, len(approx_paths)):
			for object1, path1, approx_path1, rect1 in approx_paths[i]:
				for object2, path2, approx_path2, rect2 in approx_paths[j]:
					if is_bbox_overlap(rect1, rect2):
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
									##print "crossed at", cp
									index1 = index(cp, p0, t0, p1, t1)
									index2 = index(cp, p2, t2, p3, t3)
									table.add(object1, path1, index1, cp)
									table.add(object2, path2, index2, cp)
	table.adjust()
	# split paths at each intersection
	new_paths = []
	for i in table.keys():
		new_paths.append((i, split_paths(curve_objs[i], table[i])))
	# collect untouched paths
	untouched_paths = []
	for i in range(len(curve_objs)):
		paths = curve_objs[i].paths()
		for j in range(len(paths)):
			if not table.has_key(i) or not table[i].has_key(j):
				untouched_paths.append((i, paths[j].copy()))
	return new_paths, untouched_paths


#--- PATH CONCATENATION

def on_line(p, a, b):
	if not in_range(p, a, b):
		return 0
	x1 = round(b[0] - a[0], PRECISION)
	x2 = round(p[0] - a[0], PRECISION)
	y1 = round(b[1] - a[1], PRECISION)
	y2 = round(p[1] - a[1], PRECISION)
	if x1 == 0:
		return x2 == 0
	if y1 == 0:
		return y2 == 0
	return round(x2 / x1, PRECISION) == round(y2 / y1, PRECISION)

def on_outline(p0, p1, object_paths):
	for approx_path in object_paths:
		for i in range(1, len(approx_path)):
			(p2, t), (p3, t) = approx_path[i - 1:i + 1]
			if on_line(p0, p2, p3) and on_line(p1, p2, p3):
				return 1
	return 0

def contained(path_obj, curve_obj, obj_bbox):
	approx_path = approximate_path(path_obj)
	object_paths = map(approximate_path, curve_obj.paths())
	for i in range(1, len(approx_path)):
		(p0, t), (p1, t) = approx_path[i - 1:i + 1]
		if not on_outline(p0, p1, object_paths):
			break
	else:
		return 1
	p0 = [subdivide(p0[0], p1[0]), subdivide(p0[1], p1[1])]
	p1 = [obj_bbox[0] - 1.0, obj_bbox[1] - 1.0]
	count = 0
	for approx_path in object_paths:
		for i in range(1, len(approx_path)):
			(p2, t), (p3, t) = approx_path[i - 1:i + 1]
			cp = intersect_lines(p0, p1, p2, p3)
			if cp is not None and (i == 1 or not equal(cp, p2)):
				count = count + 1
	return count % 2 == 1

def find_circuit(path_objs, start, end, rest, circuit):
	candidates = []
	for i in rest:
		cp1, path, cp2 = path_objs[i]
		if equal(cp1, start):
			candidates.append((i, cp2))
		elif equal(cp2, start):
			candidates.append((i, cp1))
	if not candidates:
		if equal(start, end):
			return circuit
		return None
	longest_circuit = []
	for i, next in candidates:
		rest.remove(i)
		new_circuit = find_circuit(path_objs, next, end, rest, circuit + [i])
		if new_circuit is not None and len(longest_circuit) < len(new_circuit):
			longest_circuit = new_circuit
		rest.append(i)
	return longest_circuit

def join(paths):
#	print "join()"
#	for cp1, path, cp2 in paths:
#		print cp1, "--", path.len, "--", cp2
	buff = []
	while paths:
		end, path, start = paths.pop()
		circuit = find_circuit(paths, start, end, range(len(paths)), [])
		assert circuit is not None
		new_path = path.copy()
		for i in circuit:
			cp1, path, cp2 = paths[i]
			path_len = path.get_len()
			if equal(cp1, start):
				for j in range(1, path_len):
					new_path.append_seg(path.get_seg(j))
				start = cp2
			elif equal(cp2, start):
				seg = path.get_seg(path_len - 1)
				last_type, last_control, node, cont = unpack_seg(seg)
				for j in range(path_len - 2, -1, -1):
					stype, control, node, cont = unpack_seg(path.get_seg(j))
					if last_type:
						last_control = (last_control[1], last_control[0])
					new_seg = pack_seg(last_type, last_control, node, cont)
					new_path.append_seg(new_seg)
					last_type = stype
					last_control = control
				start = cp1
			else:
				raise RuntimeError, "should not reach here"
			paths[i] = None
		new_path.close_path()
		buff.append(new_path)
		paths = filter(lambda x: x is not None, paths)
	return buff

#--- MODULE INTERFACE
