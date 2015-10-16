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

import cwrap

def _apply_trafo_to_point(point, trafo):
	x0, y0 = point
	m11, m21, m12, m22, dx, dy = trafo
	x1 = m11 * x0 + m12 * y0 + dx
	y1 = m21 * x0 + m22 * y0 + dy
	return [x1, y1]

def apply_trafo_to_point(point, trafo):
	if len(point) == 2:
		return _apply_trafo_to_point(point, trafo)
	else:
		return [_apply_trafo_to_point(point[0], trafo),
			_apply_trafo_to_point(point[1], trafo),
			_apply_trafo_to_point(point[2], trafo), point[3]]

def apply_trafo_to_points(points, trafo):
	ret = []
	for point in points:
		ret.append(apply_trafo_to_point(point, trafo))
	return ret

def apply_trafo_to_path(path, trafo):
	new_path = []
	new_points = []
	new_path.append(apply_trafo_to_point(path[0], trafo))
	for point in path[1]:
			new_points.append(apply_trafo_to_point(point, trafo))
	new_path.append(new_points)
	new_path.append(path[2])
	return new_path

def apply_trafo_to_paths(paths, trafo):
	new_paths = []
	for path in paths:
		new_paths.append(apply_trafo_to_path(path, trafo))
	return new_paths

def apply_trafo_to_bbox(bbox, trafo):
	p0, p1 = apply_trafo_to_points([bbox[:2], bbox[2:]], trafo)
	return p0 + p1

def get_transformed_path(obj):
	if obj.is_curve():
		return apply_trafo_to_paths(obj.paths, obj.trafo)
	else:
		return cwrap._get_transformed_path(obj)