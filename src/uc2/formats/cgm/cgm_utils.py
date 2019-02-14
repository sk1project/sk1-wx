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
    header = utils.uint16(chunk[:2])
    element_class = header >> 12
    element_id = header & 0xffe0
    size = header & 0x001f
    if len(chunk) == 4:
        size = utils.uint16(chunk[2:]) & 0x7fff
    return element_class, element_id, size


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

    if element_id == cgm_const.BEGIN_METAFILE and params:
        title_sz = utils.byte2py_int(params[0])
        markup += [(hdsz, 1, 'text length'), (hdsz + 1, title_sz, 'file title')]
    elif element_id == cgm_const.METAFILE_VERSION and params:
        markup += [(hdsz, 2, 'version'), ]
    elif element_id == cgm_const.METAFILE_DESCRIPTION and params:
        markup += [(hdsz, 1, 'text length'),
                   (hdsz + 1, params_sz, 'description'), ]

    if is_padding:
        markup += [(len(chunk) - 1, 1, 'padding byte')]
    return markup
