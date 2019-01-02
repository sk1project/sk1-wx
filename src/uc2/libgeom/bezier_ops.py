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

from copy import deepcopy

from uc2 import sk2const

from flattering import flat_path
from points import distance, mult_point, add_points
from cwrap import get_cpath_bbox, create_cpath


def is_curve_point(point):
    return len(point) != 2


def bezier_base_point(point):
    return [] + point if len(point) == 2 else [] + point[2]


def get_path_length(path, tolerance=0.5):
    fpath = flat_path(path, tolerance)
    ret = 0
    start = fpath[0]
    for item in fpath[1]:
        ret += distance(start, item)
        start = item
    return ret


def get_paths_length(paths):
    return sum(get_path_length(item) for item in paths)


def get_paths_bbox(paths):
    return get_cpath_bbox(create_cpath(paths))


def split_bezier_curve(start_point, end_point, t=0.5):
    p0 = start_point[2] if len(start_point) > 2 else start_point
    p1, p2, p3 = end_point[:3]
    flag = end_point[3] if len(end_point) == 4 else sk2const.NODE_CUSP
    p0_1 = add_points(mult_point(p0, (1.0 - t)), mult_point(p1, t))
    p1_2 = add_points(mult_point(p1, (1.0 - t)), mult_point(p2, t))
    p2_3 = add_points(mult_point(p2, (1.0 - t)), mult_point(p3, t))
    p01_12 = add_points(mult_point(p0_1, (1.0 - t)), mult_point(p1_2, t))
    p12_23 = add_points(mult_point(p1_2, (1.0 - t)), mult_point(p2_3, t))
    p0112_1223 = add_points(mult_point(p01_12, (1.0 - t)),
                            mult_point(p12_23, t))
    new_point = [p0_1, p01_12, p0112_1223, flag]
    new_end_point = [p12_23, p2_3, p3, flag]
    return new_point, new_end_point


def split_bezier_line(start_point, end_point, point):
    if len(start_point) > 2:
        start_point = start_point[2]
    dist1 = distance(start_point, end_point)
    dist2 = distance(start_point, point)
    coef = dist2 / dist1
    x = coef * (end_point[0] - start_point[0]) + start_point[0]
    y = coef * (end_point[1] - start_point[1]) + start_point[1]
    return [x, y]


def reverse_path(path):
    end_marker = path[2]
    points = [path[0], ] + path[1]
    points.reverse()
    data = []
    new_points = []
    for index in range(len(points)):
        if is_curve_point(points[index]) and data:
            p0 = [] + data[1]
            p1 = [] + data[0]
            p2 = [] + points[index][2]
            new_points.append([p0, p1, p2])
            data = deepcopy(points[index])
        elif is_curve_point(points[index]) and not data:
            new_points.append([] + points[index][2])
            data = deepcopy(points[index])
        elif not is_curve_point(points[index]) and data:
            p0 = [] + data[1]
            p1 = [] + data[0]
            p2 = [] + points[index]
            new_points.append([p0, p1, p2])
            data = []
        elif not is_curve_point(points[index]) and not data:
            new_points.append([] + points[index])
    start_point = new_points[0]
    points = new_points[1:]
    return [start_point, points, end_marker]


def reverse_paths(paths):
    return [reverse_path(path) for path in paths]
