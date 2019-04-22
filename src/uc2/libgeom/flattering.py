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

from points import add_points, mult_point, get_point_angle
from trafo import apply_trafo_to_paths, NORMAL_TRAFO


# ------------- Flattering -------------

def split_segment(start_point, end_point, t=0.5):
    p0 = start_point[2] if len(start_point) > 2 else start_point
    p1, p2, p3 = end_point[:3]
    flag = end_point[3] if len(end_point) == 4 else 0
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


def base_point(point):
    return point if len(point) == 2 else point[2]


def check_flatness(p0, p1, p2, tlr=0.5):
    p0, p1, p2 = (base_point(p) for p in (p0, p1, p2))
    if p0 == p1 or p1 == p2:
        return True
    a1 = get_point_angle(p1, p0)
    a2 = get_point_angle(p2, p1)
    return abs(a2 - a1) < tlr


def flat_segment(start_point, end_point, tlr=0.5):
    ret = []
    p0 = start_point
    p1, p2 = split_segment(start_point, end_point)
    if check_flatness(p0, p1, p2, tlr):
        ret += [base_point(p) for p in (p0, p1, p2)]
    else:
        ret += flat_segment(p0, p1, tlr)[:-1]
        ret += flat_segment(p1, p2, tlr)
    return ret


def flat_path(path, tlr=0.1):
    path = deepcopy(path)
    ret_points = []
    start = path[0]
    for point in path[1]:
        if len(point) == 2:
            ret_points.append(point)
        else:
            ret_points += flat_segment(start, point, tlr)[1:]
        start = point
    if path[2] and path[0] != ret_points[-1]:
        ret_points.append([] + path[0])
    return [path[0], ret_points, path[2]]


def flat_paths(paths, tlr=0.1):
    return [flat_path(path, tlr) for path in paths if path[1]]


def get_flattened_paths(curve_obj, trafo=NORMAL_TRAFO, tolerance=0.1):
    paths = flat_paths(curve_obj.paths, tolerance)
    paths = apply_trafo_to_paths(paths, curve_obj.trafo)
    if trafo != NORMAL_TRAFO:
        paths = apply_trafo_to_paths(paths, trafo)
    return paths
