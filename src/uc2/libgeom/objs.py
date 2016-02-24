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

import math
from copy import deepcopy

from uc2.formats.sk2 import sk2_const
from uc2 import libpango

from points import rotate_point
from trafo import apply_trafo_to_paths
from bezier_ops import split_bezier_curve, bezier_base_point

#------------- Object specific routines -------------

def normalize_rect(rect):
	x, y, width, height = rect
	if width < 0:
		width = abs(width)
		x -= width
	if height < 0:
		height = abs(height)
		y -= height
	if not width: width = .0000000001
	if not height: height = .0000000001
	return [x, y, width, height]

#------------- RECTANGLE -------------

def get_rect_paths(start, width, height, corners):
	mr = min(width, height) / 2.0
	shift = sk2_const.CIRCLE_CTRL_SHIFT

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
			sk2_const.NODE_SMOOTH
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
			sk2_const.NODE_SMOOTH
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
			sk2_const.NODE_SMOOTH
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
			sk2_const.NODE_SMOOTH
			])

	if not corners[0]:
		points.append([start[0], start[1]])
	else:
		radius = mr * corners[0]
		points.append([start[0] + radius, start[1]])

	path.append(points)
	path.append(sk2_const.CURVE_CLOSED)
	return [path, ]

#------------- CIRCLE -------------

EXTREME_ANGLES = (0.0, math.pi / 2.0, math.pi, 1.5 * math.pi, 2.0 * math.pi)
START_ANGLES = (0.0, 2.0 * math.pi)

def _get_arc_index(angle):
	ret = 0
	for index in range(4):
		if angle > EXTREME_ANGLES[index]:
			ret = index
		else:break
	return ret

def _split_arcs_at_point(angle):
	segments = deepcopy(sk2_const.STUB_ARCS)
	index = _get_arc_index(angle)
	if angle in EXTREME_ANGLES:
		if angle in START_ANGLES:index = 0
		points = segments[index:] + segments[:index]
		start = bezier_base_point(points[-1])
		return [[start, points, sk2_const.CURVE_CLOSED], ]
	else:
		points = segments[index + 1:] + segments[:index]
		seg_start = bezier_base_point(points[-1])
		seg_end = segments[index]
		t = 2.0 * (angle - EXTREME_ANGLES[index]) / math.pi
		new_point, new_end_point = split_bezier_curve(seg_start, seg_end, t)
		new_point[3] = sk2_const.NODE_SMOOTH
		new_end_point[3] = sk2_const.NODE_SMOOTH
		points[-1][3] = sk2_const.NODE_SMOOTH
		start = bezier_base_point(new_point)
		return [[start, [new_end_point, ] + points + [new_point, ],
				sk2_const.CURVE_CLOSED], ]

def _exclude_segment_from_arcs(angle1, angle2):
	segments = deepcopy(sk2_const.STUB_ARCS)
	points = []
	start_index = 0
	end_index = 0
	start_point = None

	if angle1 in EXTREME_ANGLES:
		start_index = _get_arc_index(angle1) + 1
		if angle1 in START_ANGLES:start_index = 0
		start_point = bezier_base_point(segments[start_index - 1])
		points = segments[start_index:] + segments[:start_index]
	else:
		start_index = _get_arc_index(angle1)
		seg_start = bezier_base_point(segments[start_index - 1])
		seg_end = segments[start_index]
		t = 2.0 * (angle1 - EXTREME_ANGLES[start_index]) / math.pi
		new_point, new_end_point = split_bezier_curve(seg_start, seg_end, t)
		new_end_point[3] = sk2_const.NODE_SMOOTH
		points = segments[start_index + 1:] + segments[:start_index]
		points = [new_end_point, ] + points + [new_point, ]
		start_point = bezier_base_point(new_point)

	if angle2 in EXTREME_ANGLES and angle1 in EXTREME_ANGLES:
		end_index = _get_arc_index(angle2) + 1
		if angle2 in START_ANGLES:end_index = 0
		index = points.index(segments[end_index])
		points = points[:index]
	elif angle2 in EXTREME_ANGLES and not angle1 in EXTREME_ANGLES:
		end_index = _get_arc_index(angle2) + 1
		if angle2 in START_ANGLES:end_index = 0
		if segments[end_index] in points:
			index = points.index(segments[end_index])
		else:
			index = -1
		points = points[:index]
	elif not angle2 in EXTREME_ANGLES and angle1 in EXTREME_ANGLES:
		end_index = _get_arc_index(angle2)
		seg_start = bezier_base_point(segments[end_index - 1])
		seg_end = segments[end_index]
		t = 2.0 * (angle2 - EXTREME_ANGLES[end_index]) / math.pi
		new_point = split_bezier_curve(seg_start, seg_end, t)[0]
		index = points.index(segments[end_index])
		points = points[:index]
		points += [new_point, ]
	else:
		end_index = _get_arc_index(angle2)
		if not start_index == end_index:
			seg_start = bezier_base_point(segments[end_index - 1])
			seg_end = segments[end_index]
			t = 2.0 * (angle2 - EXTREME_ANGLES[end_index]) / math.pi
			new_point = split_bezier_curve(seg_start, seg_end, t)[0]
			if segments[end_index] in points:
				index = points.index(segments[end_index])
			else:
				index = -1
			points = points[:index]
			points += [new_point, ]
		elif angle2 > angle1:
			da = angle2 - angle1
			t = da / (math.pi / 2.0 - (angle1 - EXTREME_ANGLES[end_index]))
			seg_start = start_point
			seg_end = points[0]
			new_point = split_bezier_curve(seg_start, seg_end, t)[0]
			points = [new_point, ]
		else:
			da = angle1 - angle2
			t = 1.0 - da / (angle1 - EXTREME_ANGLES[end_index])
			seg_start = bezier_base_point(points[-2])
			seg_end = points[-1]
			points[-1] = split_bezier_curve(seg_start, seg_end, t)[0]
	return [[start_point, points, sk2_const.CURVE_CLOSED], ]


def get_circle_paths(angle1, angle2, circle_type):
	paths = []
	if angle1 in START_ANGLES and angle2 in START_ANGLES:
		angle1 = angle2 = 0.0
	if angle1 == angle2:
		paths = _split_arcs_at_point(angle1)
		if circle_type in (sk2_const.ARC_PIE_SLICE, sk2_const.ARC_CHORD):
			return paths
		else:
			paths[0][2] = sk2_const.CURVE_OPENED
			return paths

	paths = _exclude_segment_from_arcs(angle1, angle2)
	start_point = [] + paths[0][0]
	if circle_type == sk2_const.ARC_PIE_SLICE:
		paths[0][1].append([0.5, 0.5])
		paths[0][1].append(start_point)
	elif circle_type == sk2_const.ARC_CHORD:
		paths[0][1].append(start_point)
	else:
		paths[0][2] = sk2_const.CURVE_OPENED
	return paths

#------------- POLYGON -------------

def get_polygon_paths(corners_num, angle1, angle2, coef1, coef2):

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
	path = [start, points[1:], sk2_const.CURVE_CLOSED]
	return [path, ]

#------------- TEXT -------------

def get_text_glyphs(text, width, text_style, attributes):
	return libpango.get_text_paths(text, width, text_style, attributes)
