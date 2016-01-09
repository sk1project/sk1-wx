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

PRECISION = 8

#--- Hashable containers

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

	def get_start_point(self):
		return deepcopy(self.path[0])

#--- CURVE APPROXIMATION

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

def is_bezier(point):
	"""
	Checks point type
	"""
	if len(point) == 2:return False
	return True

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

#--- CURVE INTERSECTION

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
