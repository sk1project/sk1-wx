# -*- coding: utf-8 -*-
#
#  Copyright (C) 2016 by Igor E. Novikov
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

SVG_ATTRS = {
    "xmlns": "http://www.w3.org/2000/svg",
    "xmlns:xlink": "http://www.w3.org/1999/xlink",
    "version": "1.1",
}

SVG_DPI = 72.0

in_to_pt = 72.0
pt_to_in = 1.0 / 72.0

pt_to_svg_px = pt_to_in * SVG_DPI
svg_px_to_pt = in_to_pt / SVG_DPI

SVG_PX = 'px'
SVG_PC = 'pc'
SVG_PT = 'pt'
SVG_MM = 'mm'
SVG_CM = 'cm'
SVG_IN = 'in'
SVG_FT = 'ft'
SVG_M = 'm'

SVG_UNITS = (SVG_PX, SVG_PC, SVG_PT, SVG_MM, SVG_CM, SVG_IN, SVG_FT, SVG_M)

SVG_STYLE = {
    'opacity': '1',
    'fill': 'black',
    'fill-rule': 'nonzero',
    'fill-opacity': '1',
    'stroke': 'none',
    'stroke-width': '1',
    'stroke-linecap': 'butt',
    'stroke-linejoin': 'miter',
    'stroke-miterlimit': '4',
    'stroke-dasharray': 'none',
    'stroke-dashoffset': '0',
    'stroke-opacity': '1',
    'font-family': 'Sans',
    'font-style': 'normal',
    'font-weight': 'normal',
    'font-size': '12',
    'text-align': 'start',
    'text-anchor': 'start',
}

IMG_SIGS = ('data:image/jpeg;base64,', 'data:image/png;base64,')
