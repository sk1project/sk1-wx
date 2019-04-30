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
    size = None
    data = None

    def __init__(self, chunk=None, **kwargs):
        self.childs = []
        self.data = {}

        if chunk:
            self.chunk = chunk
            self.data['identifier'] = chunk[:4]
            if not self.is_leaf():
                self.data['name'] = chunk[8:12]
            self.update_from_chunk()
        else:
            self.data['identifier'] = cmx_const.LIST_ID
            self.set_defaults()

        if kwargs:
            self.data.update(kwargs)

    def set_defaults(self):
        pass

    def update_from_chunk(self):
        pass

    def get(self, name, default=None):
        return self.data.get(name, default)

    def set(self, name, value):
        self.data[name] = value

    def is_leaf(self):
        return self.data['identifier'] not in cmx_const.LIST_IDS

    def get_chunk_size(self):
        return sum([len(self.chunk)] + [item.get_chunk_size()
                                        for item in self.childs])

    def get_name(self):
        return self.data.get('name', self.data['identifier'])

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
        self.chunk = self.data['identifier'] + sz + self.chunk[8:]
        if self.is_leaf() and self.is_padding():
            self.chunk += '\x00'

    def _get_icon(self):
        icon_map = {
            'DISP': 'gtk-missing-image',
            'page': 'gtk-page-setup',
        }
        if self.is_leaf():
            return icon_map.get(self.data['identifier'], 'gtk-dnd')
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


class CmxList(CmxRiffElement):
    def __init__(self, chunk=None, **kwargs):
        CmxRiffElement.__init__(self, chunk, **kwargs)


class CmxRoot(CmxRiffElement):
    toplevel = True

    def __init__(self, config, chunk=None, root_id=cmx_const.ROOT_ID):
        self.config = config
        chunk = chunk or root_id + 4 * '\x00' + 'CMX1'
        self.config.rifx = chunk.startswith(cmx_const.ROOTX_ID)
        CmxRiffElement.__init__(self, chunk)


class CmxCont(CmxRiffElement):
    identifier = cmx_const.CONT_ID

    def set_defaults(self):
        self.data['file_id'] = cmx_const.FILE_ID
        self.data['os_type'] = cmx_const.OS_ID_WIN
        self.data['byte_order'] = cmx_const.BYTE_ORDER_LE
        self.data['coord_size'] = cmx_const.COORDSIZE_32BIT
        self.data['major'] = cmx_const.MAJOR_32BIT
        self.data['minor'] = cmx_const.MINOR
        self.data['unit'] = cmx_const.UNIT_MM
        self.data['factor'] = cmx_const.FACTOR_MM

        self.data['IndexSection'] = 4 * '\x00'
        self.data['InfoSection'] = 4 * '\x00'
        self.data['Thumbnail'] = 4 * '\x00'

        self.data['bbox_x0'] = 4 * '\x00'
        self.data['bbox_y1'] = 4 * '\x00'
        self.data['bbox_x1'] = 4 * '\x00'
        self.data['bbox_y0'] = 4 * '\x00'
        self.data['tally'] = 4 * '\x00'

    def update_from_chunk(self):
        self.data['file_id'] = self.chunk[8:40].rstrip('\x00')
        self.data['os_type'] = self.chunk[40:56].rstrip('\x00')
        self.data['byte_order'] = self.chunk[56:60]
        self.data['coord_size'] = self.chunk[60:62]
        self.data['major'] = self.chunk[62:66]
        self.data['minor'] = self.chunk[66:70]
        self.data['unit'] = self.chunk[70:72]
        self.data['factor'] = self.chunk[72:80]

        self.data['IndexSection'] = self.chunk[92:96]
        self.data['InfoSection'] = self.chunk[96:100]
        self.data['Thumbnail'] = self.chunk[100:104]

        self.data['bbox_x0'] = self.chunk[104:108]
        self.data['bbox_y1'] = self.chunk[108:112]
        self.data['bbox_x1'] = self.chunk[112:116]
        self.data['bbox_y0'] = self.chunk[116:120]
        self.data['tally'] = self.chunk[120:124]

    def update(self):
        self.chunk = self.data['identifier'] + 4 * '\x00'
        self.chunk += self.data['file_id'] + \
                      (32 - len(self.data['file_id'])) * '\x00'
        self.chunk += self.data['os_type'] + \
                      (16 - len(self.data['os_type'])) * '\x00'
        self.chunk += self.data['byte_order']
        self.chunk += self.data['coord_size']
        self.chunk += self.data['major']
        self.chunk += self.data['minor']
        self.chunk += self.data['unit']
        self.chunk += self.data['factor']
        self.chunk += 12 * '\x00'
        self.chunk += self.data['IndexSection']
        self.chunk += self.data['InfoSection']
        self.chunk += self.data['Thumbnail']

        self.chunk += self.data['bbox_x0']
        self.chunk += self.data['bbox_y1']
        self.chunk += self.data['bbox_x1']
        self.chunk += self.data['bbox_y0']
        self.chunk += self.data['tally']
        self.chunk += 64 * '\x00'

        CmxRiffElement.update(self)

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
    'LIST': CmxList,
    'cont': CmxCont,
}


def make_cmx_chunk(chunk):
    identifier = chunk[:4]
    return CHUNK_MAP.get(identifier, CmxRiffElement)(chunk)
