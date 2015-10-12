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

from trafo import apply_trafo_to_point

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

def contra_point(p0, p1, p3=None):
	if not p3:
		return [2.0 * p1[0] - p0[0], 2.0 * p1[1] - p0[1]]
	else:
		l = distance(p1, p3)
		l1 = distance(p1, p0)
		coef = 1.0 + l / l1
		dx = coef * (p1[0] - p0[0])
		dy = coef * (p1[1] - p0[1])
		return [p0[0] + dx, p0[1] + dy]

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

def bezier_base_point(point):
	if len(point) == 2: return point
	return point[2]

def rotate_point(center, point, angle):
	m21 = math.sin(angle)
	m11 = m22 = math.cos(angle)
	m12 = -m21
	dx = center[0] - m11 * center[0] + m21 * center[1];
	dy = center[1] - m21 * center[0] - m11 * center[1];
	trafo = [m11, m21, m12, m22, dx, dy]
	return apply_trafo_to_point(point, trafo)
