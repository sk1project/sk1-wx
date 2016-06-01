# -*- coding: utf-8 -*-
#
#	Copyright (C) 2017 by Igor E. Novikov
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

from points import distance, midpoint, get_point_angle
from trafo import apply_trafo_to_paths
from flattering import flat_path
from bezier_ops import reverse_path

def _get_point_on_path(flat_path, pos):
	start = flat_path[0]
	end = flat_path[0]
	point = None
	l = 0
	for item in flat_path[1]:
		start, end = end, item
		l += distance(start, end)
		if l >= pos:
			coef = 1.0 - (l - pos) / distance(start, end)
			point = midpoint(start, end, coef)
			break
	if not point:
		last = distance(start, end)
		coef = (pos - l + last) / last
		point = midpoint(start, end, coef)
	angle = get_point_angle(end, start)
	return point, angle

def set_text_on_path(path_obj, text_obj, data):
	curve = path_obj.to_curve()
	path = apply_trafo_to_paths(curve.paths, curve.trafo)[0]
	if data[2]: path = reverse_path(path)
	fpath = flat_path(path)

	pos_dict = {}
	xmin = xmax = 0
	index = 0
	for item in text_obj.cache_layout_data:
		if index < len(text_obj.cache_cpath) and \
		text_obj.cache_cpath[index]:
			x = item[0]
			y = item[4]
			xmin = min(xmin, x)
			xmax = max(xmax, x)
			pos_dict[index] = (x, y)
		index += 1

	sx = 0 - xmin

	trafos = {}
	for index in pos_dict.keys():
		x, y = pos_dict[index]
		shift = text_obj.cache_layout_data[index][2] / 2.0
		point, angle = _get_point_on_path(fpath, x + sx + shift)

		center_x, center_y = x + shift, y
		m21 = math.sin(angle)
		m11 = m22 = math.cos(angle)
		m12 = -m21
		dx = center_x - m11 * center_x + m21 * center_y;
		dy = center_y - m21 * center_x - m11 * center_y;

		trafos[index] = [m11, m21, m12, m22,
						dx + point[0] - x - shift, dy + point[1] - y]

	text_obj.trafos = trafos