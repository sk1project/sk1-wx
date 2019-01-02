# -*- coding: utf-8 -*-
#
#  Copyright (C) 2016-2018 by Igor E. Novikov
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

import _libpango
import cairo
import os
from copy import deepcopy

from markup import apply_markup, apply_glyph_markup

PANGO_UNITS = 1024

SURFACE = cairo.ImageSurface(cairo.FORMAT_RGB24, 1, 1)
CTX = cairo.Context(SURFACE)
DIRECT_MATRIX = cairo.Matrix()

PANGO_MATRIX = cairo.Matrix(1.0, 0.0, 0.0, -1.0, 0.0, 0.0)
PANGO_LAYOUT = _libpango.create_layout(CTX)
NONPRINTING_CHARS = ' \n\t '.decode('utf-8')


def get_version():
    return _libpango.get_version()


# --- Glyph caching

GLYPH_CACHE = {}


def get_glyph_cache(font_name, char):
    char = str(char)
    if font_name in GLYPH_CACHE and char in GLYPH_CACHE[font_name]:
        return deepcopy(GLYPH_CACHE[font_name][char])


def set_glyph_cache(font_name, char, glyph):
    GLYPH_CACHE[font_name] = GLYPH_CACHE.get(font_name, {})
    GLYPH_CACHE[font_name][str(char)] = deepcopy(glyph)


# --- Pango context functionality

def create_layout(ctx=CTX):
    return _libpango.create_layout(ctx)


def get_font_description(text_style, check_nt=False):
    font_size = text_style[2] * 10.0 \
        if check_nt and os.name == 'nt' else text_style[2]
    fnt_descr = text_style[0] + ', ' + text_style[1] + ' ' + str(font_size)
    return _libpango.create_font_description(fnt_descr)


def set_layout(text, width, text_style, markup, layout=PANGO_LAYOUT):
    if not width == -1:
        width *= PANGO_UNITS
    _libpango.set_layout_width(layout, width)
    fnt_descr = get_font_description(text_style)
    _libpango.set_layout_font_description(layout, fnt_descr)
    _libpango.set_layout_alignment(layout, text_style[3])
    markuped_text = apply_markup(text, markup)
    _libpango.set_layout_markup(layout, markuped_text)


def set_glyph_layout(text, width, text_style, markup, text_range=None,
                     check_nt=False, layout=PANGO_LAYOUT):
    text_range = text_range or []
    if not width == -1:
        width *= PANGO_UNITS
    _libpango.set_layout_width(layout, width)
    fnt_descr = get_font_description(text_style, check_nt)
    _libpango.set_layout_font_description(layout, fnt_descr)
    _libpango.set_layout_alignment(layout, text_style[3])
    markuped_text, vpos = apply_glyph_markup(text, text_range, markup, check_nt)
    _libpango.set_layout_markup(layout, markuped_text)
    return vpos


def layout_path(ctx=CTX, layout=PANGO_LAYOUT):
    _libpango.layout_path(ctx, layout)


def get_line_positions(layout=PANGO_LAYOUT):
    return _libpango.get_layout_line_positions(layout)


def get_char_positions(size, layout=PANGO_LAYOUT):
    return _libpango.get_layout_char_positions(layout, size)


def get_cluster_positions(size, layout=PANGO_LAYOUT):
    return _libpango.get_layout_cluster_positions(layout, size)


def get_layout_size(layout=PANGO_LAYOUT):
    return _libpango.get_layout_pixel_size(layout)


def get_layout_bbox(layout=PANGO_LAYOUT):
    w, h = get_layout_size(layout)
    return [0.0, 0.0, float(w), float(-h)]
