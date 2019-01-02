# -*- coding: utf-8 -*-
#
#  Copyright (C) 2011 by Igor E. Novikov
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

import cairo
from cStringIO import StringIO

from uc2 import uc2const
import _libcairo

SURFACE = cairo.ImageSurface(cairo.FORMAT_RGB24, 1, 1)
CTX = cairo.Context(SURFACE)
DIRECT_MATRIX = cairo.Matrix()


def get_version():
    v0, v1, v2 = cairo.version_info
    return cairo.cairo_version_string(), '%d.%d.%d' % (v0, v1, v2)


def create_cpath(paths, cmatrix=None):
    CTX.set_matrix(DIRECT_MATRIX)
    CTX.new_path()
    for path in paths:
        CTX.new_sub_path()
        start_point = path[0]
        points = path[1]
        end = path[2]
        CTX.move_to(*start_point)

        for point in points:
            if len(point) == 2:
                CTX.line_to(*point)
            else:
                p1, p2, p3 = point[:-1]
                CTX.curve_to(*(p1 + p2 + p3))
        if end:
            CTX.close_path()

    cairo_path = CTX.copy_path()
    if cmatrix is not None:
        cairo_path = apply_cmatrix(cairo_path, cmatrix)
    return cairo_path


def get_path_from_cpath(cairo_path):
    return _libcairo.get_path_from_cpath(cairo_path)


def get_flattened_cpath(cairo_path, tolerance=0.1):
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
    return [min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)]


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
    if m11:
        m11 = 1.0 / m11
    if m12:
        m12 = 1.0 / m12
    if m21:
        m21 = 1.0 / m21
    if m22:
        m22 = 1.0 / m22
    dx = -dx
    dy = -dy
    return [m11, m21, m12, m22, dx, dy]


def get_matrix_from_trafo(trafo):
    m11, m21, m12, m22, dx, dy = trafo
    return cairo.Matrix(m11, m21, m12, m22, dx, dy)


def reverse_matrix(cmatrix):
    return get_matrix_from_trafo(_get_trafo(cmatrix))


def invert_trafo(trafo):
    cmatrix = get_matrix_from_trafo(trafo)
    cmatrix.invert()
    return get_trafo_from_matrix(cmatrix)


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


def get_surface_pixel(surface):
    return _libcairo.get_pixel(surface)


def check_surface_whiteness(surface):
    return _libcairo.get_pixel(surface) == [255, 255, 255]


def image_to_surface_n(image):
    png_stream = StringIO()
    image.save(png_stream, format='PNG')
    png_stream.seek(0)
    return cairo.ImageSurface.create_from_png(png_stream)


def image_to_surface(image):
    if image.mode not in (uc2const.IMAGE_RGB, uc2const.IMAGE_RGBA):
        image = image.convert(uc2const.IMAGE_RGBA if image.mode.endswith('A')
                              else uc2const.IMAGE_RGB)
    surface = None
    w,h = image.size
    image.load()
    if image.mode == uc2const.IMAGE_RGBA:
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        _libcairo.draw_rgba_image(surface, image.im, w, h)
    elif image.mode == uc2const.IMAGE_RGB:
        surface = cairo.ImageSurface(cairo.FORMAT_RGB24, w, h)
        _libcairo.draw_rgb_image(surface, image.im, w, h)
    return surface
