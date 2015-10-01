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

from flattering import flat_path
from points import distance, mult_point, add_points

def get_path_length(path):
	fpath = flat_path(path)
	points = [fpath[0], ] + fpath[1]
	if fpath[2] == sk2_const.CURVE_CLOSED:
		points += [fpath[0], ]
	ret = 0
	start = []
	for item in points:
		if not start:
			start = item
			continue
		ret += distance(start, item)
		start = item
	return ret

def get_paths_length(paths):
	ret = 0
	for item in paths:
		ret += get_path_length(item)
	return ret

def split_bezier_curve(start_point, end_point, t=0.5):
	p0 = [] + start_point
	if len(start_point) > 2: p0 = [] + start_point[2]
	p1, p2, p3, flag = deepcopy(end_point)
	p0_1 = add_points(mult_point(p0, (1.0 - t)), mult_point(p1, t))
	p1_2 = add_points(mult_point(p1, (1.0 - t)), mult_point(p2, t))
	p2_3 = add_points(mult_point(p2, (1.0 - t)), mult_point(p3, t))
	p01_12 = add_points(mult_point(p0_1, (1.0 - t)), mult_point(p1_2, t))
	p12_23 = add_points(mult_point(p1_2, (1.0 - t)), mult_point(p2_3, t))
	p0112_1223 = add_points(mult_point(p01_12, (1.0 - t)), mult_point(p12_23, t))
	new_point = [p0_1, p01_12, p0112_1223, flag]
	new_end_point = [p12_23, p2_3, p3, flag]
	return new_point, new_end_point

def split_bezier_line(start_point, end_point, point):
	if len(start_point) > 2: start_point = start_point[2]
	dist1 = distance(start_point, end_point)
	dist2 = distance(start_point, point)
	coef = dist2 / dist1
	x = coef * (end_point[0] - start_point[0]) + start_point[0]
	y = coef * (end_point[1] - start_point[1]) + start_point[1]
	return [x, y]


