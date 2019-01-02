# -*- coding: utf-8 -*-
#
#  Copyright (C) 2015-2018 by Igor E. Novikov
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import math

import cwrap

NORMAL_TRAFO = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]


def trafo_rotate(angle, cx=0.0, cy=0.0):
    m21 = math.sin(angle)
    m11 = m22 = math.cos(angle)
    m12 = -m21
    dx = cx - m11 * cx + m21 * cy
    dy = cy - m21 * cx - m11 * cy
    return [m11, m21, m12, m22, dx, dy]


def trafo_rotate_grad(grad, cx=0.0, cy=0.0):
    angle = math.pi * grad / 180.0
    return trafo_rotate(angle, cx, cy)


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
    return [apply_trafo_to_point(point, trafo) for point in points]


def apply_trafo_to_path(path, trafo):
    return [apply_trafo_to_point(path[0], trafo),
            [apply_trafo_to_point(point, trafo) for point in path[1]],
            path[2]]


def apply_trafo_to_paths(paths, trafo):
    return [apply_trafo_to_path(path, trafo) for path in paths]


def apply_trafo_to_bbox(bbox, trafo):
    p0, p1 = apply_trafo_to_points([bbox[:2], bbox[2:]], trafo)
    return p0 + p1


def get_transformed_paths(obj):
    if obj.is_curve:
        return apply_trafo_to_paths(obj.paths, obj.trafo)
    elif obj.is_text:
        return obj.get_transformed_paths()
    elif obj.cache_paths:
        return apply_trafo_to_paths(obj.cache_paths, obj.trafo)
    else:
        return cwrap.get_transformed_path(obj)
