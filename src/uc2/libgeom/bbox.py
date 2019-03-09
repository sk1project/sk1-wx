# -*- coding: utf-8 -*-
#
#  Copyright (C) 2015 by Igor E. Novikov
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

import cwrap


# ------------- Bbox operations -------------

def normalize_bbox(bbox):
    """Normalizes bounding box: sets minimal coords for first point and maximal
    for second point. Returns new bounding box.

    :type bbox: list
    :param bbox: bounding box

    :rtype: list
    :return: new bounding box
    """
    x0, y0, x1, y1 = bbox
    return [min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)]


def bbox_to_rect(bbox):
    """Normalize bbox and transform it into rectangle

    :param bbox:
    :return: rectangle
    """
    x0, y0, x1, y1 = normalize_bbox(bbox)
    return [x0, y0, x1 - x0, y1 - y0]


def bbox_points(bbox):
    """Converts bounding box to list of four rectangle corners.

    :type bbox: list
    :param bbox: bounding box

    :rtype: list
    :return: four point list
    """
    x0, y0, x1, y1 = normalize_bbox(bbox)
    return [[x0, y0], [x0, y1], [x1, y0], [x1, y1]]


def bbox_middle_points(bbox):
    """Calcs middle points of bounding box edges.

    :type bbox: list
    :param bbox: bounding box

    :rtype: list
    :return: four point list
    """
    x0, y0, x1, y1 = normalize_bbox(bbox)
    mx = (x1 - x0) / 2.0 + x0
    my = (y1 - y0) / 2.0 + y0
    return [[x0, my], [mx, y1], [x1, my], [mx, y0]]


def bbox_center(bbox):
    """Calcs bounding box center.

    :type bbox: list
    :param bbox: bounding box

    :rtype: list
    :return: point
    """
    x0, y0, x1, y1 = normalize_bbox(bbox)
    mx = (x1 - x0) / 2.0 + x0
    my = (y1 - y0) / 2.0 + y0
    return [mx, my]


def enlarge_bbox(bbox, dx=0.0, dy=0.0):
    """Symmetrically enlarge bounding box.

    :type bbox: list
    :param bbox: bounding box

    :type dx: float
    :param dx: horizontal delta

    :type dy: float
    :param dy: vertical delta

    :rtype: list
    :return: new bounding box
    """
    x0, y0, x1, y1 = bbox
    return [x0 - dx / 2.0, y0 - dy / 2.0, x1 + dx / 2.0, y1 + dy / 2.0]


def bbox_trafo(bbox0, bbox1):
    """Calcs affine transformation for changing one bounding box to another.

    :type bbox0: list
    :param bbox0: initial bounding box

    :type bbox1: list
    :param bbox1: final bounding box

    :rtype: list
    :return: affine transformation matrix
    """
    x0_0, y0_0, x1_0, y1_0 = normalize_bbox(bbox0)
    x0_1, y0_1, x1_1, y1_1 = normalize_bbox(bbox1)
    w0 = x1_0 - x0_0
    h0 = y1_0 - y0_0
    w1 = x1_1 - x0_1
    h1 = y1_1 - y0_1
    m11 = w1 / w0
    m22 = h1 / h0
    trafo = cwrap.multiply_trafo([1.0, 0.0, 0.0, 1.0, -x0_0, -y0_0],
                                 [m11, 0.0, 0.0, m22, 0.0, 0.0])
    return cwrap.multiply_trafo(trafo, [1.0, 0.0, 0.0, 1.0, x0_1, y0_1])


def bbox_for_point(point, size):
    """Calcs square bounding box for provided center and bounding box size.

    :type point: list
    :param point: bounding box center

    :type size: float
    :param size: size of square bounding box

    :rtype: list
    :return: new bounding box
    """
    x0 = point[0] - size / 2.0
    y0 = point[1] - size / 2.0
    x1 = point[0] + size / 2.0
    y1 = point[1] + size / 2.0
    return [x0, y0, x1, y1]


def is_point_in_bbox(point, bbox):
    """Checks whether is Bezier curve point inside the bounding box or not.

    :type point: list
    :param point: testing Bezier curve point

    :type bbox: list
    :param bbox: bounding box

    :rtype: boolean
    :return: boolean check result
    """
    if not len(point) == 2:
        point = point[2]
    left_cond = point[0] >= bbox[0] and point[1] >= bbox[1]
    right_cond = point[0] <= bbox[2] and point[1] <= bbox[3]
    return left_cond and right_cond


def sum_bbox(bbox1, bbox2):
    """Summarizes two bounding boxes. The result will be bounding box which
    contains both provided bboxes.

    :type bbox1: list
    :param bbox1: first bounding box

    :type bbox2: list
    :param bbox2: second bounding box

    :rtype: list
    :return: new bounding box
    """
    if not bbox1 or not bbox2:
        return bbox1 + bbox2
    x0, y0, x1, y1 = bbox1
    _x0, _y0, _x1, _y1 = bbox2
    new_x0 = min(x0, _x0, x1, _x1)
    new_x1 = max(x0, _x0, x1, _x1)
    new_y0 = min(y0, _y0, y1, _y1)
    new_y1 = max(y0, _y0, y1, _y1)
    return [new_x0, new_y0, new_x1, new_y1]


def is_bbox_in_rect(rect, bbox):
    """Checks whether is second bounding box inside the first
    bounding box or not.

    :type rect: list
    :param rect: second bounding box

    :type bbox: list
    :param bbox: first bounding box

    :rtype: boolean
    :return: boolean check result
    """
    x0, y0, x1, y1 = rect
    _x0, _y0, _x1, _y1 = bbox
    if x0 > _x0 or y0 > _y0 or x1 < _x1 or y1 < _y1:
        return False
    return True


def is_point_in_rect(point, rect):
    """Checks whether is coordinate point inside the rectangle or not.
    Rectangle is defined by bounding box.

    :type point: list
    :param point: testing coordinate point

    :type rect: list
    :param rect: bounding box

    :rtype: boolean
    :return: boolean check result
    """
    x0, y0, x1, y1 = rect
    x, y = point
    if x0 <= x <= x1 and y0 <= y <= y1:
        return True
    return False


def is_point_in_rect2(point, rect_center, rect_w, rect_h):
    """Checks whether is coordinate point inside the rectangle or not.
    Rectangle is defined by center and linear sizes.

    :type point: list
    :param point: testing coordinate point

    :type rect_center: list
    :param rect_center: point, center of rectangle

    :type rect_w: float
    :param rect_w: rectangle width

    :type rect_h: float
    :param rect_h: rectangle height

    :rtype: boolean
    :return: boolean check result
    """
    cx, cy = rect_center
    x, y = point
    if abs(x - cx) <= rect_w / 2.0 and abs(y - cy) <= rect_h / 2.0:
        return True
    return False


def bbox_size(bbox):
    """Calcs bounding box width and height.

    :type bbox: list
    :param bbox: bounding box

    :rtype: tuple
    :return: width and height
    """
    x0, y0, x1, y1 = bbox
    return abs(x1 - x0), abs(y1 - y0)


def is_bbox_overlap(bbox1, bbox2):
    """Checks whether are bounding boxes overlapped or not.

    :type bbox1: list
    :param bbox1: first bounding box

    :type bbox2: list
    :param bbox2: second bounding box

    :rtype: boolean
    :return: boolean check result
    """
    new_bbox = sum_bbox(bbox1, bbox2)
    w1, h1 = bbox_size(bbox1)
    w2, h2 = bbox_size(bbox2)
    w, h = bbox_size(new_bbox)
    return w <= w1 + w2 and h <= h1 + h2


def is_bbox_in_bbox(bbox1, bbox2):
    """Checks whether is one bounding box inside another
    bounding box or not.

    :type bbox1: list
    :param bbox1: first bounding box

    :type bbox2: list
    :param bbox2: second bounding box

    :rtype: boolean
    :return: boolean check result
    """
    new_bbox = sum_bbox(bbox1, bbox2)
    w1, h1 = bbox_size(bbox1)
    w2, h2 = bbox_size(bbox2)
    w, h = bbox_size(new_bbox)
    if w == w2 and h == h2:
        return True
    if w == w1 and h == h1:
        return True
    return False


def bbox_for_points(points):
    """Finds bounding box for provided points.

    :type points: list or tuple
    :param points: sequince of coordinate points

    :rtype: list
    :return: bounding box
    """
    xmin = xmax = points[0][0]
    ymin = ymax = points[0][1]
    for point in points:
        xmin = min(xmin, point[0])
        xmax = max(xmax, point[0])
        ymin = min(ymin, point[1])
        ymax = max(ymax, point[1])
    return [xmin, ymin, xmax, ymax]
