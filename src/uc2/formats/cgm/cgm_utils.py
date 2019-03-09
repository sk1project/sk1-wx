# -*- coding: utf-8 -*-
#
#  Copyright (C) 2017-2019 by Igor E. Novikov
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

import struct

from uc2 import utils
from uc2.formats.cgm import cgm_const


def parse_header(chunk):
    header = utils.uint16_be(chunk[:2])
    element_class = header >> 12
    element_id = header & 0xffe0
    size = header & 0x001f
    if len(chunk) == 4:
        size = utils.uint16_be(chunk[2:]) & 0x7fff
    return element_class, element_id, size


def _unpack(fmt, chunk):
    sz = struct.calcsize(fmt)
    return struct.unpack(fmt, chunk[:sz])[0], chunk[sz:]


def _unpack24(fmt, chunk):
    sz = struct.calcsize(fmt)
    res = struct.unpack(fmt, chunk[:sz])
    return (res[0] << 16) | res[1], chunk[sz:]


def _unpack_fip32(fmt, chunk):
    sz = struct.calcsize(fmt)
    res = struct.unpack(fmt, chunk[:sz])
    return res[0] + res[1] / 65536.0, chunk[sz:]


def _unpack_fip64(fmt, chunk):
    sz = struct.calcsize(fmt)
    res = struct.unpack(fmt, chunk[:sz])
    return res[0] + res[1] / (65536.0 ** 2), chunk[sz:]


CARD_F = (('>B', _unpack), ('>H', _unpack), ('>BH', _unpack24), ('>I', _unpack))
INT_F = (('>b', _unpack), ('>h', _unpack), ('>bH', _unpack24), ('>i', _unpack))
FLOAT_F = (('>f', _unpack), ('>d', _unpack))
FIXED_F = (('>hH', _unpack_fip32), ('>hH', _unpack_fip64))
REAL_F = FIXED_F + FLOAT_F
VDC_F = (INT_F, REAL_F)

_PROCESSED = (
    cgm_const.BEGIN_METAFILE,
    cgm_const.METAFILE_VERSION,
    cgm_const.METAFILE_DESCRIPTION,
    cgm_const.VDC_TYPE,
    cgm_const.APPLICATION_DATA,
    cgm_const.INTEGER_PRECISION,
    cgm_const.REAL_PRECISION,
    cgm_const.INDEX_PRECISION,
    cgm_const.COLOUR_PRECISION,
    cgm_const.COLOUR_INDEX_PRECISION,
    cgm_const.MAXIMUM_COLOUR_INDEX,
    cgm_const.METAFILE_ELEMENT_LIST,
    cgm_const.COLOUR_VALUE_EXTENT,
    cgm_const.FONT_LIST,
    cgm_const.BEGIN_PICTURE,
    cgm_const.VDC_EXTENT,
    cgm_const.SCALING_MODE,
    cgm_const.COLOUR_SELECTION_MODE,
    cgm_const.LINE_WIDTH_SPECIFICATION_MODE,
    cgm_const.MARKER_SIZE_SPECIFICATION_MODE,
    cgm_const.EDGE_WIDTH_SPECIFICATION_MODE,
    cgm_const.BACKGROUND_COLOUR,
    cgm_const.VDC_INTEGER_PRECISION,
    cgm_const.VDC_REAL_PRECISION,
    cgm_const.CLIP_RECTANGLE,
    cgm_const.POLYLINE,
    cgm_const.DISJOINT_POLYLINE,
    cgm_const.TEXT,
    cgm_const.POLYGON,
    cgm_const.POLYGON_SET,
    cgm_const.RECTANGLE,
    cgm_const.CIRCLE,
    cgm_const.ELLIPSE,
    cgm_const.LINE_TYPE,
    cgm_const.LINE_WIDTH,
    cgm_const.LINE_COLOUR,
    cgm_const.MARKER_COLOUR,
    cgm_const.TEXT_FONT_INDEX,
    cgm_const.CHARACTER_EXPANSION_FACTOR,
    cgm_const.CHARACTER_HEIGHT,
    cgm_const.CHARACTER_ORIENTATION,
    cgm_const.TEXT_ALIGNMENT,
    cgm_const.INTERIOR_STYLE,
    cgm_const.FILL_COLOUR,
    cgm_const.EDGE_TYPE,
    cgm_const.EDGE_WIDTH,
    cgm_const.EDGE_COLOUR,
    cgm_const.EDGE_VISIBILITY,
    cgm_const.COLOUR_TABLE,
)


def check_status(element_id):
    return element_id in _PROCESSED


def get_markup(header, params):
    chunk = header + params
    element_class, element_id, params_sz = parse_header(header)
    is_padding = params_sz < len(params)
    cgm_cls_name = cgm_const.CGM_CLS.get(element_class, '')
    msg = 'Command Header\n' \
          '  %d - element class\n' \
          '  (%s)\n' \
          '  0x%04x - element id\n' \
          '  %d - parameter list size (bytes)' \
          % (element_class, cgm_cls_name,
             element_id, params_sz)
    msg += '\n' + '.' * 35
    markup = [(0, len(header), msg), ]
    hdsz = len(header)

    if params:
        if element_id == cgm_const.BEGIN_METAFILE:
            title_sz = utils.byte2py_int(params[0])
            markup += [(hdsz, 1, 'text length'),
                       (hdsz + 1, title_sz, 'file title')]
        elif element_id == cgm_const.METAFILE_VERSION:
            markup += [(hdsz, 2, 'version'), ]
        elif element_id == cgm_const.METAFILE_DESCRIPTION:
            markup += [(hdsz, 1, 'text length'),
                       (hdsz + 1, params_sz - 1, 'description'), ]
        elif element_id == cgm_const.VDC_TYPE:
            markup += [(hdsz, 2, 'VDC type (integer/real)'), ]
        elif element_id == cgm_const.APPLICATION_DATA:
            txt_sz = utils.byte2py_int(params[2])
            markup += [(hdsz, 2, 'identifier'),
                       (hdsz + 2, 1, 'data length'),
                       (hdsz + 3, txt_sz, 'application data'), ]
        elif element_id == cgm_const.INTEGER_PRECISION:
            markup += [(hdsz, 2, 'integer precision\n       '
                                 '(8, 16, 24, 32 bit)'), ]
        elif element_id == cgm_const.REAL_PRECISION:
            markup += [(hdsz, 2, 'real precision type'),
                       (hdsz + 2, 2, 'integer part size'),
                       (hdsz + 4, 2, 'fractional part size'), ]
        elif element_id == cgm_const.INDEX_PRECISION:
            markup += [(hdsz, 2, 'index precision\n       '
                                 '(8, 16, 24, 32 bit)'), ]
        elif element_id == cgm_const.COLOUR_PRECISION:
            markup += [(hdsz + params_sz - 2, 2, 'color precision type'), ]
        elif element_id == cgm_const.COLOUR_INDEX_PRECISION:
            markup += [(hdsz + params_sz - 2, 2,
                        'color index precision type'), ]
        elif element_id == cgm_const.MAXIMUM_COLOUR_INDEX:
            markup += [(hdsz, 2, 'max color index'), ]
        elif element_id == cgm_const.METAFILE_ELEMENT_LIST:
            markup += [(hdsz, 2, 'list length'),
                       (hdsz + 2, params_sz - 2, 'list of 2-byte elements'), ]
        elif element_id == cgm_const.COLOUR_VALUE_EXTENT:
            sz = params_sz / 2
            markup += [(hdsz, sz, 'bottom 3-member tuple'),
                       (hdsz + sz, sz, 'top 3-member tuple'), ]
        elif element_id == cgm_const.FONT_LIST:
            pos = 0
            fonts = []
            while pos < params_sz:
                sz = utils.byte2py_int(params[pos])
                pos += 1
                fonts.append(params[pos:pos + sz].strip())
                pos += sz
            markup += [(hdsz, params_sz,
                        'font list pairs:\n'
                        '      1 byte - size of name\n'
                        '      (sz) bytes - name string\n\nFonts:\n  ' +
                        '\n  '.join(fonts) + '\n' + '.' * 35), ]
        elif element_id == cgm_const.BEGIN_PICTURE:
            markup += [(hdsz, 1, 'text length'),
                       (hdsz + 1, params_sz - 1, 'description'), ]
        elif element_id == cgm_const.VDC_EXTENT:
            sz = params_sz / 2
            markup += [(hdsz, sz, 'VDC lower left point'),
                       (hdsz + sz, sz, 'VDC upper right point'), ]
        elif element_id == cgm_const.SCALING_MODE:
            markup += [(hdsz, 2, 'scaling mode'),
                       (hdsz + 2, 4, 'scaling metric'), ]
        elif element_id == cgm_const.COLOUR_SELECTION_MODE:
            markup += [(hdsz, 2, 'color mode'), ]
        elif element_id == cgm_const.LINE_WIDTH_SPECIFICATION_MODE:
            markup += [(hdsz, 2, 'line width specification mode'), ]
        elif element_id == cgm_const.MARKER_SIZE_SPECIFICATION_MODE:
            markup += [(hdsz, 2, 'marker size specification mode'), ]
        elif element_id == cgm_const.EDGE_WIDTH_SPECIFICATION_MODE:
            markup += [(hdsz, 2, 'edge width specification mode'), ]
        elif element_id == cgm_const.BACKGROUND_COLOUR:
            markup += [(hdsz, params_sz, 'bg color'), ]
        elif element_id == cgm_const.VDC_INTEGER_PRECISION:
            markup += [(hdsz, params_sz, 'vdc integer precision'), ]
        elif element_id == cgm_const.VDC_REAL_PRECISION:
            markup += [(hdsz, 2, ' precision type'),
                       (hdsz + 2, params_sz - 2, ' 2 precision fields')]
        elif element_id == cgm_const.CLIP_RECTANGLE:
            markup += [(hdsz, params_sz, 'clip rectangle (2 points)'), ]
        elif element_id == cgm_const.POLYLINE:
            markup += [(hdsz, params_sz, 'polyline points'), ]
        elif element_id == cgm_const.DISJOINT_POLYLINE:
            markup += [(hdsz, params_sz, 'disjoint polyline points'), ]
        elif element_id == cgm_const.TEXT:
            markup += [(hdsz, params_sz, 'point + 2 byte flag + text'), ]
        elif element_id == cgm_const.POLYGON:
            markup += [(hdsz, params_sz, 'points'), ]
        elif element_id == cgm_const.POLYGON_SET:
            markup += [(hdsz, params_sz, 'point + 2 byte flag pairs'), ]
        elif element_id == cgm_const.RECTANGLE:
            sz = params_sz / 2
            markup += [(hdsz, sz, 'rect lower left point'),
                       (hdsz + sz, sz, 'rect upper right point'), ]
        elif element_id == cgm_const.CIRCLE:
            sz = params_sz / 3
            markup += [(hdsz, sz, 'center x'),
                       (hdsz + sz, sz, 'center y'),
                       (hdsz + 2 * sz, sz, 'radius'), ]
        elif element_id == cgm_const.CIRCULAR_ARC_3_POINT:
            markup += [(hdsz, params_sz, '3 points'), ]
        elif element_id == cgm_const.CIRCULAR_ARC_3_POINT_CLOSE:
            markup += [(hdsz, params_sz, '3 points + close flag'), ]

        elif element_id == cgm_const.ELLIPSE:
            markup += [(hdsz, params_sz, 'center + 2 cdp points'), ]

        elif element_id == cgm_const.LINE_TYPE:
            markup += [(hdsz, params_sz, 'line type'), ]
        elif element_id == cgm_const.LINE_WIDTH:
            markup += [(hdsz, params_sz, 'line width'), ]
        elif element_id == cgm_const.LINE_COLOUR:
            markup += [(hdsz, params_sz, 'line color'), ]
        elif element_id == cgm_const.MARKER_COLOUR:
            markup += [(hdsz, params_sz, 'marker color'), ]
        elif element_id == cgm_const.TEXT_FONT_INDEX:
            markup += [(hdsz, params_sz, 'text font index'), ]
        elif element_id == cgm_const.CHARACTER_EXPANSION_FACTOR:
            markup += [(hdsz, params_sz, 'character expansion'), ]
        elif element_id == cgm_const.CHARACTER_HEIGHT:
            markup += [(hdsz, params_sz, 'character height'), ]
        elif element_id == cgm_const.CHARACTER_ORIENTATION:
            markup += [(hdsz, params_sz, 'character orientation'), ]
        elif element_id == cgm_const.TEXT_ALIGNMENT:
            markup += [(hdsz, 2, 'text alignment'), ]
        elif element_id == cgm_const.INTERIOR_STYLE:
            markup += [(hdsz, params_sz, 'fill type'), ]
        elif element_id == cgm_const.FILL_COLOUR:
            markup += [(hdsz, params_sz, 'fill color'), ]
        elif element_id == cgm_const.EDGE_TYPE:
            markup += [(hdsz, params_sz, 'edge type'), ]
        elif element_id == cgm_const.EDGE_WIDTH:
            markup += [(hdsz, params_sz, 'edge width'), ]
        elif element_id == cgm_const.EDGE_COLOUR:
            markup += [(hdsz, params_sz, 'edge color'), ]
        elif element_id == cgm_const.EDGE_VISIBILITY:
            markup += [(hdsz, params_sz, 'edge visibility'), ]
        elif element_id == cgm_const.COLOUR_TABLE:
            markup += [(hdsz, params_sz, 'index + color values'), ]

    if is_padding:
        markup += [(len(chunk) - 1, 1, 'padding byte')]
    return markup
