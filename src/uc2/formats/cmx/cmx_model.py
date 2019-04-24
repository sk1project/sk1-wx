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
from uc2.formats.cmx import cmx_const
from uc2.formats.generic import BinaryModelObject


class CmxRiffElement(BinaryModelObject):
    toplevel = False
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

    def get_name(self):
        return self.name or self.identifier

    def get_child_by_name(self, name):
        for item in self.childs:
            if item.get_name() == name:
                return item
        return None

    def get_chunk_offset(self):
        chunk = self
        offset = 0
        while not chunk.toplevel:
            childs = chunk.parent.childs
            index = childs.index(chunk)
            offset += sum([item.get_chunk_size() for item in childs[:index]])
            offset += len(chunk.parent.chunk)
            chunk = chunk.parent
        return offset

    def is_padding(self):
        sz = len(self.chunk)
        return sz > (sz // 2) * 2

    def update(self):
        size = self.get_chunk_size() - 8
        sz = utils.py_int2dword(size, self.config.rifx)
        self.chunk = self.identifier + sz + self.chunk[8:]
        if self.is_leaf() and self.is_padding():
            self.chunk += '\x00'

    def _get_icon(self):
        icon_map = {
            'DISP': 'gtk-missing-image',
            'page': 'gtk-page-setup',
        }
        if self.is_leaf():
            return icon_map.get(self.identifier, 'gtk-dnd')
        return False

    def resolve(self, name=''):
        sz = '%d' % self.get_chunk_size()
        name = '<%s>' % self.get_name()
        return self._get_icon(), name, sz

    def update_for_sword(self):
        self.cache_fields = [(0, 4, 'Chunk identifier'),
                             (4, 4, 'Chunk data size')]
        if not self.is_leaf():
            self.cache_fields += [(8, 4, 'Chunk name')]


class CmxRoot(CmxRiffElement):
    toplevel = True

    def __init__(self, config, chunk):
        self.config = config
        self.config.rifx = chunk.startswith(cmx_const.ROOTX_ID)
        CmxRiffElement.__init__(self, chunk)


def get_empty_cmx(config):
    return CmxRoot(config, cmx_const.ROOT_ID + 4 * '\x00' + 'CMX1')


class CmxCont(CmxRiffElement):
    def update_for_sword(self):
        CmxRiffElement.update_for_sword(self)
        self.cache_fields += [
            (8, 32, 'file id'),
            (40, 16, 'OS type'),
            (56, 4, 'ByteOrder'),
            (60, 2, 'CoordSize'),
            (62, 4, 'Major'),
            (66, 4, 'Minor'),
            (70, 2, 'Unit'),
            (72, 8, 'Factor'),

            (80, 4, 'lOption (not used, zero)'),
            (84, 4, 'lForeignKey (not used, zero)'),
            (88, 4, 'lCapability (not used, zero)'),

            (92, 4, 'lIndexSection offset'),
            (96, 4, 'InfoSection offset'),
            (100, 4, 'lThumbnail offset'),

            (104, 4, 'lBBLeft - bbox x0'),
            (108, 4, 'lBBTop - bbox y1'),
            (112, 4, 'lBBRight - bbox x1'),
            (116, 4, 'lBBBottom - bbox y0'),
            (120, 4, 'lTally - instructions num'),

            (124, 64, 'Reserved - set to zero'),
        ]


CHUNK_MAP = {
    'cont': CmxCont,
}


def make_cmx_chunk(chunk):
    identifier = chunk[:4]
    return CHUNK_MAP.get(identifier, CmxRiffElement)(chunk)
