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
from uc2.formats.generic import BinaryModelObject
from uc2.formats.cmx import cmx_const


class CmxRiffElement(BinaryModelObject):
    identifier = cmx_const.LIST_ID
    size = None
    name = None

    def __init__(self, chunk):
        self.childs = []
        self.chunk = chunk
        self.identifier = chunk[:4]
        if not self.is_leaf():
            self.name = chunk[8:12]

    def is_leaf(self):
        return self.identifier not in cmx_const.LIST_IDS

    def get_chunk_size(self):
        return sum([len(self.chunk)] + [item.get_chunk_size()
                                        for item in self.childs])

    def is_padding(self):
        sz = len(self.chunk)
        return sz > (sz // 2) * 2

    def update(self):
        size = self.get_chunk_size() - 8
        sz = utils.py_int2dword(size, self.config.rifx)
        self.chunk = self.identifier + sz + self.chunk[8:]
        if self.is_leaf() and self.is_padding():
            self.chunk += '\x00'

    def resolve(self, name=''):
        sz = '%d' % self.get_chunk_size()
        name = '<%s>' % (self.name or self.identifier)
        return self.is_leaf(), name, sz


class CmxRoot(CmxRiffElement):
    def __init__(self, config, chunk):
        self.config = config
        self.config.rifx = chunk.startswith(cmx_const.ROOTX_ID)
        CmxRiffElement.__init__(self, chunk)


def get_empty_cmx(config):
    return CmxRoot(config, cmx_const.ROOT_ID + 4 * '\x00' + 'CMX1')
