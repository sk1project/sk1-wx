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

from uc2 import utils
from uc2.formats.cgm import cgm_model, cgm_const


def builder(element_id, **kwargs):
    elf = cgm_model.element_factory
    if element_id == cgm_const.BEGIN_METAFILE:
        txt = kwargs.get('txt', 'Computer Graphics Metafile')
        params = utils.py_int2byte(len(txt)) + txt
        header = utils.py_int2word(0x0020 + len(params), True)
        return elf(header, params)
    elif element_id == cgm_const.METAFILE_VERSION:
        version = kwargs.get('version', 1)
        return elf('\x10\x22', utils.py_int2word(version, True))
    elif element_id == cgm_const.METAFILE_DESCRIPTION:
        txt = kwargs.get('txt', 'Created by UniConvertor')
        params = utils.py_int2byte(len(txt)) + txt
        header = '\x10\x5f' + utils.py_int2word(len(params), True)
        return elf(header, params)


class SK2_to_CGM_Translator(object):
    cgm_doc = None
    cgm_model = None
    sk2_doc = None
    sk2_mtds = None
    picture = None

    def translate(self, sk2_doc, cgm_doc):
        self.cgm_doc = cgm_doc
        self.cgm_model = cgm_doc.model
        self.sk2_doc = sk2_doc
        self.sk2_mtds = sk2_doc.methods
        self.picture = None
