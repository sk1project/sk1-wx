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


    if is_padding:
        markup += [(len(chunk) - 1, 1, 'padding byte')]
    return markup
