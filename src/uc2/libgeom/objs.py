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

from uc2 import libcairo
from uc2.formats.sk2 import sk2_const

from points import rotate_point

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

def get_circle_paths(angle1, angle2, circle_type):
	paths = []
	if angle1 == angle2:
		paths = deepcopy(sk2_const.STUB_CIRCLE)
		if circle_type:
			return paths
		else:
			paths[0][2] = sk2_const.CURVE_OPENED
			return paths

	libcairo.CTX.set_matrix(libcairo.DIRECT_MATRIX)
	libcairo.CTX.new_path()
	libcairo.CTX.arc(0.5, 0.5, 0.5, angle1, angle2)
	cairo_path = libcairo.CTX.copy_path()
	paths = libcairo.get_path_from_cpath(cairo_path)
	if circle_type:
		start_point = [] + paths[0][0]
		paths[0][2] = sk2_const.CURVE_CLOSED
		if circle_type == sk2_const.ARC_PIE_SLICE:
			paths[0][1].append([0.5, 0.5])
		paths[0][1].append(start_point)
	return paths


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
