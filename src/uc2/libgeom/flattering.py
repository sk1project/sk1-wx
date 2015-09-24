# -*- coding: utf-8 -*-
#
#	Copyright (C) 2015 by Igor E. Novikov
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


from points import midpoint, sub_points, abs_point, normalize_point, \
mult_points, cr_points, add_points

from trafo import apply_trafo_to_paths

#------------- Flattering -------------

def _flat_segment(p0, p1, p2, p3, tlr):
	p4 = midpoint(p0, p1)
	p5 = midpoint(p1, p2)
	p6 = midpoint(p2, p3)
	p7 = midpoint(p4, p5)
	p8 = midpoint(p5, p6)
	p9 = midpoint(p7, p8)

	b = sub_points(p3, p0)
	s = sub_points(p9, p0)
	c1 = sub_points(p1, p0)
	c2 = sub_points(p2, p3)

	if abs_point(c1) > abs_point(b) or abs_point(c2) > abs_point(b):
		return _flat_segment(p0, p4, p7, p9, tlr) + _flat_segment(p9, p8, p6, p3, tlr)

	elif abs_point(b) < tlr / 2.0:
		return [p9, p3]
	else:
		N = normalize_point(b)
		if ((mult_points(c1, N)) < -tlr
			or (mult_points(c2, N)) > tlr
			or cr_points(c1, b) * cr_points(c2, b) < 0
			or abs(cr_points(N, s)) > tlr):
			return _flat_segment(p0, p4, p7, p9, tlr) + _flat_segment(p9, p8, p6, p3, tlr)
		else:
			return [p9, p3]

def flat_path(path, tlr):
	result = []
	result.append([] + path[0])
	start = [] + path[0]
	for point in path[1]:
		if len(point) == 2:
			result.append([] + point)
			start = [] + point
		else:
			p0 = sub_points(point[0], start)
			p1 = sub_points(point[1], start)
			p2 = sub_points(point[2], start)
			points = _flat_segment([0.0, 0.0], p0, p1, p2, tlr)
			for item in points:
				p = add_points(item, start)
				result.append(p)
			start = [] + point[2]
	return [result[0], result[1:], path[2]]

def flat_paths(paths, tlr):
	result = []
	for path in paths:
		result.append(flat_path(path, tlr))
	return result

def get_flattened_path(obj, trafo, tolerance=0.5):
	if obj.cache_paths is None:
		obj.update()
	if obj.cache_paths is None: return None
	paths = apply_trafo_to_paths(obj.cache_paths, trafo)
	return flat_paths(paths, tolerance)
