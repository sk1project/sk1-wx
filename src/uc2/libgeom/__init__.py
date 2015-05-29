# -*- coding: utf-8 -*-
#
#	Copyright (C) 2012 by Igor E. Novikov
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

from copy import deepcopy
import math

from uc2 import libcairo
from uc2.formats.sk2 import sk2_const as const


"""
Package provides basic routines for Bezier curves.

PATHS DEFINITION:
[path0, path1, ...]

PATH DEFINITION:
[start_point, points, end_marker]
start_pont - [x,y]
end_marker - is closed CURVE_CLOSED = 1, if not CURVE_OPENED = 0

POINTS DEFINITION:
[point0, point1,...]
line point - [x,y]
curve point - [[x1,y1],[x2,y2],[x3,y3], marker]
marker - NODE_CUSP = 0; NODE_SMOOTH = 1; NODE_SYMMETRICAL = 2 
"""


#------------- Point operations -------------


def div_point(p, k):
	return [p[0] / k, p[1] / k]

def abs_point(p):
	return math.hypot(p[0], p[1])

def mult_point(p, k):
	return [p[0] * k, p[1] * k]

def normalize_point(p):
	return [p[0] / abs_point(p), p[1] / abs_point(p)]

def midpoint(p0, p1):
	return [(p1[0] + p0[0]) / 2.0, (p1[1] + p0[1]) / 2.0]

def contra_point(p0, p1):
	return [2.0 * p1[0] - p0[0], 2.0 * p1[1] - p0[1]]


def add_points(p1, p0):
	return [p1[0] + p0[0], p1[1] + p0[1]]

def sub_points(p1, p0):
	return [p1[0] - p0[0], p1[1] - p0[1]]

def mult_points(p0, p1):
	return p0[0] * p1[0] + p0[1] * p1[1]

def cr_points(p0, p1):
	return p0[0] * p1[1] - p0[1] * p1[0]

def is_equal_points(p1, p0):
	ret = False
	if p1[0] == p0[0] and p1[1] == p0[1]:
		ret = True
	return ret

def distance(p0, p1):
	x0, y0 = p0
	x1, y1 = p1
	return math.sqrt(math.pow((x1 - x0), 2) + math.pow((y1 - y0), 2))

#------------- Bbox operations -------------

def normalize_bbox(bbox):
	x0, y0, x1, y1 = bbox
	new_bbox = [0, 0, 0, 0]
	if x0 < x1:
		new_bbox[0] = x0
		new_bbox[2] = x1
	else:
		new_bbox[0] = x1
		new_bbox[2] = x0
	if y0 < y1:
		new_bbox[1] = y0
		new_bbox[3] = y1
	else:
		new_bbox[1] = y1
		new_bbox[3] = y0
	return new_bbox

def bbox_points(bbox):
	x0, y0, x1, y1 = normalize_bbox(bbox)
	return [[x0, y0], [x0, y1], [x1, y0], [x1, y1]]

def bbox_middle_points(bbox):
	x0, y0, x1, y1 = normalize_bbox(bbox)
	mx = (x1 - x0) / 2.0 + x0
	my = (y1 - y0) / 2.0 + y0
	return [[x0, my], [mx, y1], [x1, my], [mx, y0]]

def bbox_center(bbox):
	x0, y0, x1, y1 = normalize_bbox(bbox)
	mx = (x1 - x0) / 2.0 + x0
	my = (y1 - y0) / 2.0 + y0
	return [mx, my]

def bbox_trafo(bbox0, bbox1):
	x0_0, y0_0, x1_0, y1_0 = normalize_bbox(bbox0)
	x0_1, y0_1, x1_1, y1_1 = normalize_bbox(bbox1)
	w0 = x1_0 - x0_0
	h0 = y1_0 - y0_0
	w1 = x1_1 - x0_1
	h1 = y1_1 - y0_1
	m11 = w1 / w0
	m22 = h1 / h0
	dx = x0_1 - x0_0
	dy = y0_1 - y0_0
	return [m11, 0.0, 0.0, m22, dx, dy]


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

#------------- generic Bezier math stuff -------------
def apply_trafo_to_paths(paths, trafo):
	new_paths = []
	for path in paths:
		new_paths.append(apply_trafo_to_path(path, trafo))
	return new_paths

def apply_trafo_to_path(path, trafo):
	new_path = []
	new_points = []
	new_path.append(apply_trafo_to_point(path[0], trafo))
	for point in path[1]:
			new_points.append(apply_trafo_to_point(point, trafo))
	new_path.append(new_points)
	new_path.append(path[2])
	return new_path

def apply_trafo_to_points(points, trafo):
	ret = []
	for point in points:
		ret.append(apply_trafo_to_point(point, trafo))
	return ret

def apply_trafo_to_point(point, trafo):
	if len(point) == 2:
		return _apply_trafo_to_point(point, trafo)
	else:
		return [_apply_trafo_to_point(point[0], trafo),
			_apply_trafo_to_point(point[1], trafo),
			_apply_trafo_to_point(point[2], trafo), point[3]]

def _apply_trafo_to_point(point, trafo):
	x0, y0 = point
	m11, m21, m12, m22, dx, dy = trafo
	x1 = m11 * x0 + m12 * y0 + dx
	y1 = m21 * x0 + m22 * y0 + dy
	return [x1, y1]

def bezier_base_point(point):
	if len(point) == 2:
		return point
	else:
		return point[2]

def sum_bbox(bbox1, bbox2):
	x0, y0, x1, y1 = bbox1
	_x0, _y0, _x1, _y1 = bbox2
	new_x0 = min(x0, _x0, x1, _x1)
	new_x1 = max(x0, _x0, x1, _x1)
	new_y0 = min(y0, _y0, y1, _y1)
	new_y1 = max(y0, _y0, y1, _y1)
	return [new_x0, new_y0, new_x1, new_y1]

def is_bbox_in_rect(rect, bbox):
	x0, y0, x1, y1 = rect
	_x0, _y0, _x1, _y1 = bbox
	if x0 > _x0: return False
	if y0 > _y0: return False
	if x1 < _x1: return False
	if y1 < _y1: return False
	return True

def is_point_in_rect(point, rect):
	x0, y0, x1, y1 = rect
	x, y = point
	if x0 <= x <= x1 and y0 <= y <= y1:
		return True
	return False

def is_point_in_rect2(point, rect_center, rect_w, rect_h):
	cx, cy = rect_center
	x, y = point
	if abs(x - cx) <= rect_w / 2.0 and abs(y - cy) <= rect_h / 2.0:
		return True
	return False

def rotate_point(center, point, angle):
	m21 = math.sin(angle)
	m11 = m22 = math.cos(angle)
	m12 = -m21
	dx = center[0] - m11 * center[0] + m21 * center[1];
	dy = center[1] - m21 * center[0] - m11 * center[1];
	trafo = [m11, m21, m12, m22, dx, dy]
	return apply_trafo_to_point(point, trafo)


#------------- libcairo wrapper -------------

def create_cpath(cache_paths):
	return libcairo.create_cpath(cache_paths)

def copy_cpath(cache_cpath):
	return libcairo.copy_cpath(cache_cpath)

def get_cpath_bbox(cache_cpath):
	return libcairo.get_cpath_bbox(cache_cpath)

def apply_trafo(cache_cpath, trafo):
	return libcairo.apply_trafo(cache_cpath, trafo)

def multiply_trafo(trafo1, trafo2):
	return libcairo.multiply_trafo(trafo1, trafo2)

def get_flattened_path(obj, trafo, tolerance=0.5):
	if obj.cache_paths is None:
		obj.update()
	if obj.cache_paths is None: return None

#	cpath = libcairo.apply_trafo(obj.cache_cpath, trafo, True)
#	paths = libcairo._libcairo.get_path_from_cpath(cpath)
	paths = apply_trafo_to_paths(obj.cache_paths, trafo)

	return flat_paths(paths, tolerance)

def get_transformed_path(obj):
	if obj.cache_cpath is None:
		obj.update()
	if obj.cache_cpath is None: return None

	return libcairo.get_path_from_cpath(obj.cache_cpath)

#------------- Object specific routines -------------

def get_rect_path(start, width, height, corners):
	mr = min(width, height) / 2.0
	shift = const.CIRCLE_CTRL_SHIFT

	path = []
	points = []

	if corners[0] == 0.0:
		path.append([start[0], start[1]])
	else:
		radius = mr * corners[0]
		path.append([start[0] + radius, start[1]])
		points.append([
			[start[0] + radius * shift, start[1]],
			[start[0], start[1] + radius * shift],
			[start[0], start[1] + radius],
			const.NODE_SMOOTH
			])

	if corners[1] == 0.0:
		points.append([start[0], start[1] + height])
	else:
		radius = mr * corners[1]
		points.append([start[0], start[1] + height - radius])
		points.append([
			[start[0], start[1] + height - radius * shift],
			[start[0] + radius * shift, start[1] + height],
			[start[0] + radius, start[1] + height],
			const.NODE_SMOOTH
			])

	if corners[2] == 0.0:
		points.append([start[0] + width, start[1] + height])
	else:
		radius = mr * corners[2]
		points.append([start[0] + width - radius, start[1] + height])
		points.append([
			[start[0] + width - radius * shift, start[1] + height],
			[start[0] + width, start[1] + height - radius * shift],
			[start[0] + width, start[1] + height - radius],
			const.NODE_SMOOTH
			])

	if corners[3] == 0.0:
		points.append([start[0] + width, start[1]])
	else:
		radius = mr * corners[3]
		points.append([start[0] + width, start[1] + radius])
		points.append([
			[start[0] + width, start[1] + radius * shift],
			[start[0] + width - radius * shift, start[1]],
			[start[0] + width - radius, start[1]],
			const.NODE_SMOOTH
			])

	if not corners[0]:
		points.append([start[0], start[1]])
	else:
		radius = mr * corners[0]
		points.append([start[0] + radius, start[1]])

	path.append(points)
	path.append(const.CURVE_CLOSED)
	return [path, ]

def get_circle_path(angle1, angle2, circle_type):
	paths = []
	if angle1 == angle2:
		paths += const.STUB_CIRCLE
		if circle_type:
			return paths
		else:
			paths[0][2] = const.CURVE_OPENED
			return paths

	libcairo.CTX.set_matrix(libcairo.DIRECT_MATRIX)
	libcairo.CTX.new_path()
	libcairo.CTX.arc(0.5, 0.5, 0.5, angle1, angle2)
	cairo_path = libcairo.CTX.copy_path()
	paths = libcairo._libcairo.get_path_from_cpath(cairo_path)
	if circle_type:
		start_point = [] + paths[0][0]
		paths[0][2] = const.CURVE_CLOSED
		if circle_type == const.ARC_PIE_SLICE:
			paths[0][1].append([0.5, 0.5])
		paths[0][1].append(start_point)
	return paths


def get_polygon_path(corners_num, angle1, angle2, coef1, coef2):

	if corners_num < 3:corners_num = 3
	points = []

	center = [0.5, 0.5]
	corner_angle = 2.0 * math.pi / float(corners_num)
	corners_start = [0.5, 0.5 + 0.5 * coef1]
	midpoint_start = [0.5, 0.5 + 0.5 * coef2 * math.cos(corner_angle / 2.0)]

	corner_angle_shift = angle1
	midpoint_angle_shift = corner_angle / 2.0 + angle2

	for i in range(0, corners_num):
		angle = float(i) * corner_angle + corner_angle_shift
		point = rotate_point(center, corners_start, angle)
		points.append(point)

		angle = float(i) * corner_angle + midpoint_angle_shift
		point = rotate_point(center, midpoint_start, angle)
		points.append(point)

	start = points[0]
	points.append([] + start)
	path = [start, points, const.CURVE_CLOSED]
	return [path, ]

def get_text_path(text, width, style, attributes):
	paths = []

#	libcairo.CTX.set_matrix(libcairo.DIRECT_MATRIX)
#	libcairo.CTX.new_path()
#	libcairo.CTX.move_to(0, 0)
#
#	libcairo.PCCTX.update_layout(libcairo.PANGO_LAYOUT)
#
#	if width == const.TEXTBLOCK_WIDTH:
#		libcairo.PANGO_LAYOUT.set_width(const.TEXTBLOCK_WIDTH)
#	else:
#		libcairo.PANGO_LAYOUT.set_width(int(width * 1000))
#
#	libcairo.PANGO_LAYOUT.set_justify(True)
#	libcairo.PANGO_LAYOUT.set_text(text)
#
#	libcairo.PCCTX.layout_path(libcairo.PANGO_LAYOUT)
#	cairo_path = libcairo.CTX.copy_path()
#	libcairo.apply_cmatrix(cairo_path, libcairo.PANGO_MATRIX)
#	paths = libcairo.get_path_from_cpath(cairo_path)

	return paths


