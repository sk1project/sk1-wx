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

import zlib
from cStringIO import StringIO

from uc2 import utils
from uc2.formats.cmx import cmx_const, cmx_instr
from uc2.formats.generic import BinaryModelObject


class CmxRiffElement(BinaryModelObject):
    toplevel = False
    size = None
    data = None

    def __init__(self, config, chunk=None, **kwargs):
        self.config = config
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

    def update_from_kwargs(self, **kwargs):
        self.data.update(kwargs)
        self.update()

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
            'ccmm': 'gtk-select-color',
            'DISP': 'gtk-missing-image',
            'page': 'gtk-page-setup',
            'pack': 'gtk-paste',
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
            self.cache_fields += [(8, 4, 'List chunk name')]
        else:
            self.cache_fields[1] = (4, 4, 'Chunk data size\n')


class CmxList(CmxRiffElement):
    def __init__(self, config, chunk=None, **kwargs):
        CmxRiffElement.__init__(self, config, chunk, **kwargs)


class CmxInfoElement(CmxRiffElement):
    def __init__(self, config, chunk=None, **kwargs):
        CmxRiffElement.__init__(self, config, chunk, **kwargs)

    def set_defaults(self):
        self.data['identifier'] = cmx_const.IKEY_ID
        self.data['text'] = ''

    def update_from_chunk(self):
        self.data['text'] = self.chunk[8:].rstrip('\x00')

    def update(self):
        self.chunk = self.data['identifier'] + 4 * '\x00'
        self.chunk += self.data['text']
        text_sz = len(self.data['text'])
        padding = (text_sz // 32 + 1) * 32 - text_sz
        self.chunk += padding * '\x00'
        CmxRiffElement.update(self)

    def update_for_sword(self):
        CmxRiffElement.update_for_sword(self)
        sz = len(self.chunk) - 8
        idnt = self.data['identifier']
        msg = 'Notes' if idnt == cmx_const.ICMT_ID else 'Keys'
        self.cache_fields += [(8, sz, msg), ]


class CmxCont(CmxRiffElement):
    def set_defaults(self):
        self.data['identifier'] = cmx_const.CONT_ID
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
        padding_sz = 32 - len(self.data['file_id'])
        self.chunk += self.data['file_id'] + padding_sz * '\x00'
        padding_sz = 16 - len(self.data['os_type'])
        self.chunk += self.data['os_type'] + padding_sz * '\x00'
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


class CmxCcmm(CmxRiffElement):
    def set_defaults(self):
        self.data['identifier'] = cmx_const.CCMM_ID
        self.data['dump'] = \
            '\x50\x50\x00\x00\x00\x04\x00\x00\x4c\x02\x00\x00\x00\x00\x00\x00' \
            '\x04\x00\x00\x00\x80\x6a\xbc\x34\x80\x95\x43\x1b\x8c\x97\x6e\x02' \
            '\xc0\xf1\xd2\x2d\x80\x1e\x85\x5b\x60\x64\x3b\x0f\x80\x3d\x0a\x17' \
            '\xc0\x4b\x37\x09\x00\xc5\x8f\x79\x33\x33\x02\x00\x33\x33\x02\x00' \
            '\x33\x33\x02\x00\x01\x00\x00\x00'

    def update_from_chunk(self):
        self.data['dump'] = self.chunk[8:]

    def update(self):
        self.chunk = self.data['identifier'] + 4 * '\x00'
        self.chunk += self.data['dump']
        CmxRiffElement.update(self)

    def update_for_sword(self):
        CmxRiffElement.update_for_sword(self)
        self.cache_fields += [
            (8, 4, 'lcsSignature'),
            (12, 4, 'lcsVersion'),
            (16, 4, 'lcsSize'),
            (20, 4, 'lcsCSType'),
            (24, 4, 'lcsIntent'),

            (28, 12, 'Red Endpoint'),
            (40, 12, 'Green Endpoint'),
            (52, 12, 'Blue Endpoint'),

            (64, 4, 'Red Gamma'),
            (68, 4, 'Green Gamma'),
            (72, 4, 'Blue Gamma'),

            (76, 4, 'ulRcsCompandType'),
        ]


class CmxDisp(CmxRiffElement):
    def __init__(self, config, chunk=None, **kwargs):
        CmxRiffElement.__init__(self, config, chunk, **kwargs)

    @staticmethod
    def make_chunk_from_bitmap(bitmap_str):
        chunk = cmx_const.DISP_ID + 4 * '\x00' + '\x08' + 3 * '\x00'
        chunk += utils.bmp_to_dib(bitmap_str)
        return chunk

    def update_for_sword(self):
        CmxRiffElement.update_for_sword(self)
        clr_table_sz = 4 * utils.dword2py_int(self.chunk[44:48],
                                              self.config.rifx)
        pos = 52 + clr_table_sz
        self.cache_fields += [
            (8, 4, 'dwClipboardFormat'),
            # BITMAPINFOHEADER
            (12, 4, 'biSize - header size'),
            (16, 4, 'biWidth - image width'),
            (20, 4, 'biHeight - image height'),
            (24, 2, 'biPlanes'),
            (26, 2, 'biBitCount'),
            (28, 4, 'biCompression'),
            (32, 4, 'biSizeImage'),
            (36, 4, 'biXPelsPerMeter'),
            (40, 4, 'biYPelsPerMeter'),
            (44, 4, 'biClrUsed'),
            (48, 4, 'biClrImportant'),
            # COLOR TABLE
            (52, clr_table_sz, 'Color Table'),
            # Pixels
            (pos, len(self.chunk) - pos, 'Pixels'),
        ]


class CmxPage(CmxRiffElement):
    def update_from_chunk(self):
        chunk = self.chunk[8:]
        pos = 0
        rifx = self.config.rifx
        parents = [self]
        while pos < len(chunk):
            size = utils.word2py_int(chunk[pos:pos + 2], rifx)
            instr_id = utils.signed_word2py_int(chunk[pos + 2:pos + 4], rifx)
            instr = chunk[pos:pos + size]
            obj = cmx_instr.make_instruction(self.config, instr)
            name = cmx_const.INSTR_CODES.get(instr_id, '')
            if name.startswith('Begin'):
                parents[-1].add(obj)
                parents.append(obj)
            elif name.startswith('End'):
                parents = parents[:-1]
                parents[-1].add(obj)
            else:
                parents[-1].add(obj)
            pos += size
        self.chunk = self.chunk[:8]


class CdrxPack(CmxRiffElement):
    def update_from_chunk(self):
        chunk = zlib.decompress(self.chunk[20:])
        pos = 0
        parent = self
        while pos < len(chunk):
            identifier = chunk[pos:pos + 4]
            sz = chunk[pos + 4:pos + 8]
            if identifier in cmx_const.LIST_IDS:
                name = chunk[pos + 8:pos + 12]
                obj = make_cmx_chunk(self.config, identifier + sz + name)
                parent.add(obj)
                parent = obj
                pos += 12
                continue
            size = utils.dword2py_int(sz, self.config.rifx)
            size += 1 if size > (size // 2) * 2 else 0
            data = chunk[pos + 8:pos + 8 + size]
            parent.add(make_cmx_chunk(self.config, identifier + sz + data))
            pos += size + 8
        self.data['cpng'] = self.chunk[20:]
        self.chunk = self.chunk[:20]

    def update_for_sword(self):
        CmxRiffElement.update_for_sword(self)
        self.cache_fields += [
            (8, 4, 'Uncompressed size'),
            (12, 4, 'Compressed stream header'),
            (16, 4, 'Compression flags'),
        ]

    def get_chunk_size(self):
        return len(self.chunk)

    def get_childs_size(self):
        return sum([item.get_chunk_size() for item in self.childs])

    def update_cpng(self):
        stream = StringIO()
        for child in self.childs:
            child.save(stream)
        self.data['cpng'] = zlib.compress(stream.getvalue())

    def update(self):
        size = self.get_childs_size()
        sz = utils.py_int2dword(size, self.config.rifx)
        self.update_cpng()
        compr_sz = len(self.data['cpng'])
        compr_sz += 1 if compr_sz > (compr_sz // 2) * 2 else 0
        compr_sz = utils.py_int2dword(compr_sz + 12, self.config.rifx)
        self.chunk = self.data['identifier'] + compr_sz + sz + self.chunk[12:20]
        self.chunk += self.data['cpng']
        self.chunk += '\x00' if self.is_padding() else ''

    def save(self, saver):
        saver.write(self.chunk)


class CmxRoot(CmxList):
    toplevel = True

    def __init__(self, config, chunk=None, root_id=cmx_const.ROOT_ID):
        config.rifx = root_id == cmx_const.ROOTX_ID
        chunk = chunk or self.make_new_doc(config, root_id)
        CmxList.__init__(self, config, chunk)

    def make_new_doc(self, config, root_id):
        chunk = root_id + 4 * '\x00'
        chunk += cmx_const.CDRX_ID if config.pack else cmx_const.CMX_ID

        # TODO: here should be cmx doc creating

        return chunk


CHUNK_MAP = {
    cmx_const.LIST_ID: CmxList,
    cmx_const.CONT_ID: CmxCont,
    cmx_const.CCMM_ID: CmxCcmm,
    cmx_const.DISP_ID: CmxDisp,
    cmx_const.PAGE_ID: CmxPage,
    cmx_const.PACK_ID: CdrxPack,
    cmx_const.IKEY_ID: CmxInfoElement,
    cmx_const.ICMT_ID: CmxInfoElement,
}


def make_cmx_chunk(config, chunk):
    identifier = chunk[:4]
    return CHUNK_MAP.get(identifier, CmxRiffElement)(config, chunk)
