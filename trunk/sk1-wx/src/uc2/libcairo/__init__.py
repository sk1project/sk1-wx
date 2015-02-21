# -*- coding: utf-8 -*-
#
#	Copyright (C) 2011 by Igor E. Novikov
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

import cairo
#import pangocairo
import _libcairo


SURFACE = cairo.ImageSurface(cairo.FORMAT_RGB24, 1, 1)
CTX = cairo.Context(SURFACE)
DIRECT_MATRIX = cairo.Matrix()

PANGO_MATRIX = cairo.Matrix(1.0, 0.0, 0.0, -1.0, 0.0, 0.0)
#PCCTX = pangocairo.CairoContext(CTX)
#PANGO_LAYOUT = PCCTX.create_layout()

FAMILIES_LIST = []
FAMILIES_DICT = {}

#def get_fonts(families_list, families_dict):
#	fm = pangocairo.cairo_font_map_get_default()
#	context = fm.create_context()
#	families = context.list_families()
#	for item in families:
#		fcs = []
#		scalable = True
#		for face in item.list_faces():
#			if not face.list_sizes() is None:
#				scalable = False
#			fcs.append(face.get_face_name())
#		if scalable:
#			fcs.sort()
#			families_dict[item.get_name()] = fcs
#			families_list.append(item.get_name())
#	families_list.sort()
#
#get_fonts(FAMILIES_LIST, FAMILIES_DICT)

def create_cpath(paths, cmatrix=None):
	CTX.set_matrix(DIRECT_MATRIX)
	CTX.new_path()
	for path in paths:
		CTX.new_sub_path()
		start_point = path[0]
		points = path[1]
		end = path[2]
		x, y = start_point
		CTX.move_to(x, y)

		for point in points:
			if len(point) == 2:
				x, y = point
				CTX.line_to(x, y)
			else:
				p1, p2, p3, m = point
				x1, y1 = p1
				x2, y2 = p2
				x3, y3 = p3
				CTX.curve_to(x1, y1, x2, y2, x3, y3)
		if end:
			CTX.close_path()

	cairo_path = CTX.copy_path()
	if not cmatrix is None:
		cairo_path = apply_cmatrix(cairo_path, cmatrix)
	return cairo_path

def get_path_from_cpath(cairo_path):
	return _libcairo.get_path_from_cpath(cairo_path)

def get_flattened_path(cairo_path, tolerance=0.1):
	CTX.set_matrix(DIRECT_MATRIX)
	tlr = CTX.get_tolerance()
	CTX.set_tolerance(tolerance)
	CTX.new_path()
	CTX.append_path(cairo_path)
	result = CTX.copy_path_flat()
	CTX.set_tolerance(tlr)
	return result

def apply_cmatrix(cairo_path, cmatrix):
	trafo = get_trafo_from_matrix(cmatrix)
	return apply_trafo(cairo_path, trafo)

def copy_cpath(cairo_path):
	CTX.set_matrix(DIRECT_MATRIX)
	CTX.new_path()
	CTX.append_path(cairo_path)
	return CTX.copy_path()

def apply_trafo(cairo_path, trafo, copy=False):
	if copy:
		cairo_path = copy_cpath(cairo_path)
	m11, m21, m12, m22, dx, dy = trafo
	_libcairo.apply_trafo(cairo_path, m11, m21, m12, m22, dx, dy)
	return cairo_path

def multiply_trafo(trafo1, trafo2):
	matrix1 = get_matrix_from_trafo(trafo1)
	matrix2 = get_matrix_from_trafo(trafo2)
	matrix = matrix1.multiply(matrix2)
	return _libcairo.get_trafo(matrix)

def normalize_bbox(bbox):
	x0, y0, x1, y1 = bbox
	new_bbox = [0, 0, 0, 0]
	if x0 < x1:
		new_bbox[0] = x0
		new_bbox[2] = x1
	else:
		new_bbox[0] = x1
		new_bbox[2] = x0
	if y0 < y1:
		new_bbox[1] = y0
		new_bbox[3] = y1
	else:
		new_bbox[1] = y1
		new_bbox[3] = y0
	return new_bbox

def get_cpath_bbox(cpath):
	CTX.set_matrix(DIRECT_MATRIX)
	CTX.new_path()
	CTX.append_path(cpath)
	return normalize_bbox(CTX.path_extents())

def _get_trafo(cmatrix):
	result = []
	val = cmatrix.__str__()
	val = val.replace('cairo.Matrix(', '')
	val = val.replace(')', '')
	items = val.split(', ')
	for item in items:
		val = item.replace(',', '.')
		result.append(float(val))
	return result

def get_trafo_from_matrix(cmatrix):
	return _libcairo.get_trafo(cmatrix)

def reverse_trafo(trafo):
	m11, m21, m12, m22, dx, dy = trafo
	if m11: m11 = 1.0 / m11
	if m12: m12 = 1.0 / m12
	if m21: m21 = 1.0 / m21
	if m22: m22 = 1.0 / m22
	dx = -dx
	dy = -dy
	return [m11, m21, m12, m22, dx, dy]

def get_matrix_from_trafo(trafo):
	m11, m21, m12, m22, dx, dy = trafo
	return cairo.Matrix(m11, m21, m12, m22, dx, dy)

def reverse_matrix(cmatrix):
	return get_matrix_from_trafo(_get_trafo(cmatrix))

def apply_trafo_to_point(point, trafo):
	x0, y0 = point
	m11, m21, m12, m22, dx, dy = trafo
	x1 = m11 * x0 + m12 * y0 + dx
	y1 = m21 * x0 + m22 * y0 + dy
	return [x1, y1]

def apply_trafo_to_bbox(bbox, trafo):
	x0, y0, x1, y1 = bbox
	start = apply_trafo_to_point([x0, y0], trafo)
	end = apply_trafo_to_point([x1, y1], trafo)
	return start + end

def convert_bbox_to_cpath(bbox):
	x0, y0, x1, y1 = bbox
	CTX.set_matrix(DIRECT_MATRIX)
	CTX.new_path()
	CTX.move_to(x0, y0)
	CTX.line_to(x1, y0)
	CTX.line_to(x1, y1)
	CTX.line_to(x0, y1)
	CTX.line_to(x0, y0)
	CTX.close_path()
	return CTX.copy_path()

def is_point_in_path(point, trafo, obj, stroke_width=5.0, fill_flag=True):
	dx, dy = point
	trafo = [] + trafo
	trafo[4] -= dx
	trafo[5] -= dy
	CTX.set_matrix(DIRECT_MATRIX)
	CTX.set_tolerance(3.0)
	CTX.set_source_rgb(1, 1, 1)
	CTX.paint()
	_draw_object(obj, trafo, stroke_width, fill_flag)
	pixel = _libcairo.get_pixel(SURFACE)
	CTX.set_tolerance(0.1)
	if pixel[0] == pixel[1] == pixel[2] == 255:
		return False
	else:
		return True

def _draw_object(obj, trafo, stroke_width, fill_flag):
	if obj.childs:
		for child in obj.childs:
			_draw_object(child, trafo, stroke_width, fill_flag)
	else:
		fill_anyway = False
		path = obj.cache_cpath

		if obj.cid in [205, 206]:
			path = convert_bbox_to_cpath(obj.cache_bbox)
			fill_anyway = True
		if obj.cid == 204 and len(obj.paths) > 100:
			path = convert_bbox_to_cpath(obj.cache_bbox)
			fill_anyway = True

		CTX.set_matrix(get_matrix_from_trafo(trafo))
		CTX.set_source_rgb(0, 0, 0)
		CTX.new_path()
		CTX.append_path(path)
		if fill_flag and obj.style[0]:
			CTX.fill_preserve()
		if fill_anyway:
			CTX.fill_preserve()
		if obj.style[1]:
			stroke = obj.style[1]
			width = stroke[1] * trafo[0]
			stroke_width /= trafo[0]
			if width < stroke_width: width = stroke_width
			CTX.set_source_rgb(0, 0, 0)
			CTX.set_line_width(width)
			CTX.stroke()

