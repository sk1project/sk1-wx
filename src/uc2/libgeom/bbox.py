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


#------------- Bbox operations -------------

def normalize_bbox(bbox):
	x0, y0, x1, y1 = bbox
	return [min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)]

def bbox_points(bbox):
	x0, y0, x1, y1 = normalize_bbox(bbox)
	return [[x0, y0], [x0, y1], [x1, y0], [x1, y1]]

def bbox_middle_points(bbox):
	x0, y0, x1, y1 = normalize_bbox(bbox)
	mx = (x1 - x0) / 2.0 + x0
	my = (y1 - y0) / 2.0 + y0
	return [[x0, my], [mx, y1], [x1, my], [mx, y0]]

def bbox_center(bbox):
	x0, y0, x1, y1 = normalize_bbox(bbox)
	mx = (x1 - x0) / 2.0 + x0
	my = (y1 - y0) / 2.0 + y0
	return [mx, my]

def bbox_trafo(bbox0, bbox1):
	x0_0, y0_0, x1_0, y1_0 = normalize_bbox(bbox0)
	x0_1, y0_1, x1_1, y1_1 = normalize_bbox(bbox1)
	w0 = x1_0 - x0_0
	h0 = y1_0 - y0_0
	w1 = x1_1 - x0_1
	h1 = y1_1 - y0_1
	m11 = w1 / w0
	m22 = h1 / h0
	dx = x0_1 - x0_0
	dy = y0_1 - y0_0
	return [m11, 0.0, 0.0, m22, dx, dy]

def bbox_for_point(point, size):
	x0 = point[0] - size / 2.0
	y0 = point[1] - size / 2.0
	x1 = point[0] + size / 2.0
	y1 = point[1] + size / 2.0
	return [x0, y0, x1, y1]

def is_point_in_bbox(point, bbox):
	if not len(point) == 2: point = point[2]
	return point[0] >= bbox[0] and point[1] >= bbox[1] \
		and point[0] <= bbox[2] and point[1] <= bbox[3]

def sum_bbox(bbox1, bbox2):
	x0, y0, x1, y1 = bbox1
	_x0, _y0, _x1, _y1 = bbox2
	new_x0 = min(x0, _x0, x1, _x1)
	new_x1 = max(x0, _x0, x1, _x1)
	new_y0 = min(y0, _y0, y1, _y1)
	new_y1 = max(y0, _y0, y1, _y1)
	return [new_x0, new_y0, new_x1, new_y1]

def is_bbox_in_rect(rect, bbox):
	x0, y0, x1, y1 = rect
	_x0, _y0, _x1, _y1 = bbox
	if x0 > _x0: return False
	if y0 > _y0: return False
	if x1 < _x1: return False
	if y1 < _y1: return False
	return True

def is_point_in_rect(point, rect):
	x0, y0, x1, y1 = rect
	x, y = point
	if x0 <= x <= x1 and y0 <= y <= y1:
		return True
	return False

def is_point_in_rect2(point, rect_center, rect_w, rect_h):
	cx, cy = rect_center
	x, y = point
	if abs(x - cx) <= rect_w / 2.0 and abs(y - cy) <= rect_h / 2.0:
		return True
	return False

def bbox_size(bbox):
	x0, y0, x1, y1 = bbox
	h = abs(x1 - x0)
	v = (y1 - y0)
	return h, v

def is_bbox_overlap(bbox1, bbox2):
	new_bbox = sum_bbox(bbox1, bbox2)
	w1, h1 = bbox_size(bbox1)
	w2, h2 = bbox_size(bbox2)
	w, h = bbox_size(new_bbox)
	return w <= w1 + w2 and h <= h1 + h2

def is_bbox_in_bbox(bbox1, bbox2):
	new_bbox = sum_bbox(bbox1, bbox2)
	w1, h1 = bbox_size(bbox1)
	w2, h2 = bbox_size(bbox2)
	w, h = bbox_size(new_bbox)
	if w == w2 and h == h2: return True
	if w == w1 and h == h1: return True
	return False