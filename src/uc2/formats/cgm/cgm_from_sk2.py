# -*- coding: utf-8 -*-
#
#  Copyright (C) 2019 by Igor E. Novikov
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

import logging

from uc2 import utils, uc2const
from uc2.formats.cgm import cgm_model, cgm_const

LOG = logging.getLogger(__name__)

SCALE = 39.37 * uc2const.pt_to_mm


def cgm_unit(val):
    return int(round(SCALE * val))


def builder(element_id, **kwargs):
    elf = cgm_model.element_factory
    if element_id == cgm_const.BEGIN_METAFILE:
        txt = kwargs.get('txt', 'Computer Graphics Metafile')
        params = utils.py_int2byte(len(txt)) + txt
        header = utils.py_int2word(0x0020 + len(params), True)
        return elf(header, params)
    elif element_id == cgm_const.END_METAFILE:
        header = '\x00\x40'
        return elf(header, '')
    elif element_id == cgm_const.METAFILE_VERSION:
        version = kwargs.get('version', 1)
        return elf('\x10\x22', utils.py_int2word(version, True))
    elif element_id == cgm_const.METAFILE_DESCRIPTION:
        txt = kwargs.get('description', 'Created by UniConvertor')
        params = utils.py_int2byte(len(txt)) + txt
        header = '\x10\x5f' + utils.py_int2word(len(params), True)
        return elf(header, params)
    elif element_id == cgm_const.METAFILE_ELEMENT_LIST:
        header = '\x11\x66'
        params = '\x00\x01\xff\xff\x00\x01'
        return elf(header, params)
    elif element_id == cgm_const.VDC_TYPE:
        header = '\x10\x62'
        params = '\x00\x00'
        return elf(header, params)
    elif element_id == cgm_const.INTEGER_PRECISION:
        header = '\x10\x82'
        params = '\x00\x10'
        return elf(header, params)
    elif element_id == cgm_const.REAL_PRECISION:
        header = '\x10\xa6'
        params = '\x00\x08'
        return elf(header, params)
    elif element_id == cgm_const.INDEX_PRECISION:
        header = '\x10\xc2'
        params = '\x00\x08'
        return elf(header, params)
    elif element_id == cgm_const.COLOUR_PRECISION:
        header = '\x10\xe2'
        params = '\x00\x08'
        return elf(header, params)
    elif element_id == cgm_const.COLOUR_INDEX_PRECISION:
        header = '\x11\x02'
        params = '\x00\x08'
        return elf(header, params)
    # Page elements
    elif element_id == cgm_const.BEGIN_PICTURE:
        page_number = kwargs.get('page_number', 1)
        txt = 'Page %d' % page_number
        params = utils.py_int2byte(len(txt)) + txt
        header = '\x00' + utils.py_int2byte(len(params) + 0x60)
        return elf(header, params)
    elif element_id == cgm_const.BEGIN_PICTURE_BODY:
        header = '\x00\x80'
        return elf(header, '')
    elif element_id == cgm_const.END_PICTURE:
        header = '\x00\xa0'
        return elf(header, '')
    elif element_id == cgm_const.SCALING_MODE:
        header = '\x20\x26'
        params = '\x00\x01' + '\x3c\xd0\x13\xa9'
        return elf(header, params)
    elif element_id == cgm_const.COLOUR_SELECTION_MODE:
        header = '\x20\x42'
        params = '\x00\x01'
        return elf(header, params)
    elif element_id == cgm_const.LINE_WIDTH_SPECIFICATION_MODE:
        header = '\x20\x62'
        params = '\x00\x01'
        return elf(header, params)
    elif element_id == cgm_const.EDGE_WIDTH_SPECIFICATION_MODE:
        header = '\x20\xa2'
        params = '\x00\x01'
        return elf(header, params)
    elif element_id == cgm_const.VDC_EXTENT:
        bbox = kwargs.get('bbox', (0.0, 0.0, 1.0, 1.0))
        header = '\x20\xc8'
        params = ''.join([utils.py_int2signed_word(cgm_unit(val), True)
                          for val in bbox])
        return elf(header, params)


class SK2_to_CGM_Translator(object):
    cgm_doc = None
    cgm_model = None
    sk2_doc = None
    sk2_mtds = None

    def translate(self, sk2_doc, cgm_doc):
        self.cgm_doc = cgm_doc
        self.cgm_model = cgm_doc.model
        self.sk2_doc = sk2_doc
        self.sk2_mtds = sk2_doc.methods

        self.add(cgm_const.BEGIN_METAFILE)
        self.add(cgm_const.METAFILE_VERSION)
        d = self.sk2_doc.appdata
        txt = 'Created by %s %s%s' % (d.app_name, d.version, d.revision)
        self.add(cgm_const.METAFILE_DESCRIPTION, description=txt)
        self.add(cgm_const.METAFILE_ELEMENT_LIST)
        self.add(cgm_const.VDC_TYPE)
        self.add(cgm_const.INTEGER_PRECISION)
        self.add(cgm_const.REAL_PRECISION)
        self.add(cgm_const.INDEX_PRECISION)
        self.add(cgm_const.COLOUR_PRECISION)
        self.add(cgm_const.COLOUR_INDEX_PRECISION)

        index = 1
        for page in self.sk2_mtds.get_pages():
            self.process_page(page, index)
            index += 1

        self.add(cgm_const.END_METAFILE)

        self.cgm_doc = None
        self.cgm_model = None
        self.sk2_doc = None
        self.sk2_mtds = None

    def add(self, element_id, **kwargs):
        self.cgm_model.add(builder(element_id, **kwargs))

    def process_page(self, page, index=1):
        self.add(cgm_const.BEGIN_PICTURE, page_number=index)

        self.add(cgm_const.SCALING_MODE)
        self.add(cgm_const.COLOUR_SELECTION_MODE)
        self.add(cgm_const.LINE_WIDTH_SPECIFICATION_MODE)
        self.add(cgm_const.EDGE_WIDTH_SPECIFICATION_MODE)

        w, h = self.sk2_mtds.get_page_size(page)
        bbox = (-w / 2.0, -h / 2.0, w / 2.0, h / 2.0)
        self.add(cgm_const.VDC_EXTENT, bbox=bbox)

        self.add(cgm_const.BEGIN_PICTURE_BODY)

        self.add(cgm_const.END_PICTURE)
