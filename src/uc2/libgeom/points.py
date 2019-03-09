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

from trafo import apply_trafo_to_point


# ------------- Point operations -------------

def div_point(p, k):
    return [p[0] / k, p[1] / k]


def abs_point(p):
    return math.hypot(p[0], p[1])


def mult_point(p, k):
    return [p[0] * k, p[1] * k]


def normalize_point(p):
    return [p[0] / abs_point(p), p[1] / abs_point(p)]


def midpoint(p0, p1, coef=0.5):
    x = (p1[0] - p0[0]) * coef + p0[0]
    y = (p1[1] - p0[1]) * coef + p0[1]
    return [x, y]


def contra_point(p0, p1, p3=None):
    if not p3:
        return [2.0 * p1[0] - p0[0], 2.0 * p1[1] - p0[1]]
    else:
        lenght = distance(p1, p3)
        lenght1 = distance(p1, p0)
        coef = 1.0 + lenght / lenght1
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


def is_equal_points(p0, p1, precision=None):
    if precision is None:
        return p1[0] == p0[0] and p1[1] == p0[1]
    x_eq = round(p0[0], precision) == round(p1[0], precision)
    y_eq = round(p0[1], precision) == round(p1[1], precision)
    return x_eq and y_eq


def distance(p0, p1=None):
    p1 = p1 or [0.0, 0.0]
    x0, y0 = p0
    x1, y1 = p1
    return math.sqrt(math.pow((x1 - x0), 2) + math.pow((y1 - y0), 2))


def rotate_point(center, point, angle):
    m21 = math.sin(angle)
    m11 = m22 = math.cos(angle)
    m12 = -m21
    dx = center[0] - m11 * center[0] + m21 * center[1]
    dy = center[1] - m21 * center[0] - m11 * center[1]
    trafo = [m11, m21, m12, m22, dx, dy]
    return apply_trafo_to_point(point, trafo)


def round_angle_point(center, point, angle):
    if angle:
        angle = math.radians(angle)
        point_angle = get_point_angle(point, center)
        point_angle = (point_angle + angle / 2.0) // angle * angle
        r = distance(point, center)
        # calculate point on circle
        x = r * math.cos(point_angle)
        y = r * math.sin(point_angle)
        point = add_points([x, y], center)
    return point


def get_point_radius(p, center=None):
    return distance(p, center or [0.5, 0.5])


def get_point_angle(p, center=None):
    center = center or [0.5, 0.5]
    x0, y0 = center
    x, y = p
    r = get_point_radius(p, center)
    if x >= x0 and y == y0:
        return 0.0
    elif x < x0 and y == y0:
        return math.pi
    elif x == x0 and y > y0:
        return math.pi / 2.0
    elif x == x0 and y < y0:
        return math.pi / 2.0 + math.pi
    elif x > x0 and y > y0:
        return math.acos((x - x0) / r)
    elif x < x0 and y > y0:
        return math.pi - math.acos((x0 - x) / r)
    elif x < x0 and y < y0:
        return math.pi + math.acos((x0 - x) / r)
    elif x > x0 and y < y0:
        return 2.0 * math.pi - math.acos((x - x0) / r)


def to_polar(point):
    r = distance(point)
    return r, get_point_angle(point, [0.0, 0.0]) if r else 0.0


def circle_center_by_3points(p1, p2, p3):
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    if not x2 - x1 or not x3 - x2:
        return None
    ma = (y2 - y1) / (x2 - x1)
    mb = (y3 - y2) / (x3 - x2)
    if not mb - ma:
        return None
    d0 = ma * mb * (y1 - y3) + mb * (x1 + x2) - ma * (x2 + x3)
    d1 = 2 * mb - 2 * ma
    if not d1:
        return None
    x0 = d0 / d1
    if ma:
        y0 = -(x0 - (x1 + x2) / 2) / ma + (y1 + y2) / 2
    else:
        y0 = -(x0 - (x2 + x3) / 2) / mb + (y2 + y3) / 2
    return [x0, y0]
