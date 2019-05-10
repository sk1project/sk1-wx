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

import struct

from uc2 import utils
from uc2.formats.cmx import cmx_const
from uc2.formats.generic import BinaryModelObject


class CmxObject(BinaryModelObject):
    toplevel = False

    def get_root(self):
        parent = self
        while not parent.toplevel:
            parent = parent.parent
        return parent

    def get_chunk_size(self, recursive=True):
        if recursive:
            return sum([len(self.chunk)] + [item.get_chunk_size()
                                            for item in self.childs])
        return len(self.chunk)

    def get_offset(self):
        offset = 0
        parent = self.parent
        obj = self
        while parent:
            index = parent.childs.index(obj)
            offset += sum([item.get_chunk_size()
                           for item in parent.childs[:index]])
            offset += parent.get_chunk_size(recursive=False)
            obj = parent
            parent = parent.parent if not parent.toplevel else None
        return offset

    def set_defaults(self):
        pass

    def update_from_chunk(self):
        pass


class CmxInstruction(CmxObject):
    toplevel = False

    def __init__(self, config, chunk=None, **kwargs):
        self.config = config
        self.childs = []
        self.data = {}

        if chunk:
            self.chunk = chunk
            self.data['code'] = self._get_code(chunk[2:4])
            self.update_from_chunk()

        if kwargs:
            self.data.update(kwargs)

    def _get_code(self, code_str):
        return abs(utils.signed_word2py_int(code_str, self.config.rifx))

    def _get_code_str(self):
        return utils.py_int2word(self.data['code'], self.config.rifx)

    def get_name(self):
        return cmx_const.INSTR_CODES.get(self.data['code'],
                                         str(self.data['code']))

    def resolve(self, name=''):
        sz = '%d' % len(self.chunk)
        name = '[%s]' % self.get_name()
        return len(self.childs) == 0, name, sz

    def update(self):
        size = len(self.chunk)
        sz = utils.py_int2word(size, self.config.rifx)
        self.chunk = sz + self._get_code_str() + self.chunk[4:]

    def update_for_sword(self):
        self.cache_fields = [(0, 2, 'Instruction Size'),
                             (2, 2, 'Instruction Code\n')]


class Inst16BeginPage(CmxInstruction):
    def update_from_chunk(self):
        rifx = self.config.rifx
        word2int = utils.word2py_int
        dword2int = utils.dword2py_int
        self.data['page_number'] = word2int(self.chunk[4:6], rifx)
        self.data['flags'] = dword2int(self.chunk[6:10], rifx)
        sig = '>iiii' if rifx else '<iiii'
        self.data['bbox'] = struct.unpack(sig, self.chunk[10:26])
        self.data['tail'] = self.chunk[26:]

    def update(self):
        rifx = self.config.rifx
        int2word = utils.py_int2word
        int2dword = utils.py_int2dword
        self.chunk = '\x00\x00' + int2word(self.data['code'], rifx)
        self.chunk += int2word(self.data['page_number'], rifx)
        self.chunk += int2dword(self.data['flags'], rifx)
        sig = '>iiii' if rifx else '<iiii'
        self.chunk += struct.pack(sig, *self.data['bbox'])
        self.chunk += self.data['tail']
        CmxInstruction.update(self)

    def update_for_sword(self):
        CmxInstruction.update_for_sword(self)
        tail_sz = len(self.chunk) - 26
        self.cache_fields += [
            (4, 2, 'Page number'),
            (6, 4, 'Page flags'),
            (10, 16, 'Drawing bbox on page'),
            (26, tail_sz, 'Page tail'),
        ]


class Inst16BeginLayer(CmxInstruction):
    def update_from_chunk(self):
        rifx = self.config.rifx
        word2int = utils.word2py_int
        dword2int = utils.dword2py_int
        self.data['page_number'] = word2int(self.chunk[4:6], rifx)
        self.data['layer_number'] = word2int(self.chunk[6:8], rifx)
        self.data['flags'] = dword2int(self.chunk[8:12], rifx)
        self.data['tally'] = dword2int(self.chunk[12:16], rifx)
        name_size = word2int(self.chunk[16:18], rifx)
        self.data['layer_name'] = self.chunk[18:18 + name_size]
        self.data['tail'] = self.chunk[18 + name_size:]

    def update(self):
        rifx = self.config.rifx
        int2word = utils.py_int2word
        int2dword = utils.py_int2dword
        self.chunk = '\x00\x00' + int2word(self.data['code'], rifx)
        self.chunk += int2word(self.data['page_number'], rifx)
        self.chunk += int2word(self.data['layer_number'], rifx)
        self.chunk += int2dword(self.data['flags'], rifx)
        self.chunk += int2dword(self.data['tally'], rifx)
        self.chunk += int2word(len(self.data['layer_name']), rifx)
        self.chunk += self.data['layer_name'] + self.data['tail']
        CmxInstruction.update(self)

    def update_for_sword(self):
        CmxInstruction.update_for_sword(self)
        name_sz = utils.word2py_int(self.chunk[16:18], self.config.rifx)
        tail_sz = len(self.chunk) - 18 - name_sz
        self.cache_fields += [
            (4, 2, 'Page number'),
            (6, 2, 'Layer number'),
            (8, 4, 'Layer flags'),
            (12, 4, 'Tally'),
            (16, 2, 'Layer name size'),
            (18, name_sz, 'Layer name'),
            (18 + name_sz, tail_sz, 'Layer tail'),
        ]


class Inst16BeginGroup(CmxInstruction):
    def update_from_chunk(self):
        sig = '>iiii' if self.config.rifx else '<iiii'
        self.data['bbox'] = struct.unpack(sig, self.chunk[4:20])
        self.data['tail'] = self.chunk[20:]

    def update(self):
        rifx = self.config.rifx
        int2word = utils.py_int2word
        self.chunk = '\x00\x00' + int2word(self.data['code'], rifx)
        sig = '>iiii' if rifx else '<iiii'
        self.chunk += struct.pack(sig, *self.data['bbox']) + self.data['tail']
        CmxInstruction.update(self)

    def update_for_sword(self):
        CmxInstruction.update_for_sword(self)
        self.cache_fields += [
            (4, 16, 'Group bbox'),
            (20, 2, 'Group tail'),
        ]


class Inst16PolyCurve(CmxInstruction):
    def update_for_sword(self):
        rifx = self.config.rifx
        CmxInstruction.update_for_sword(self)
        flags = utils.byte2py_int(self.chunk[4])
        self.cache_fields += [(4, 1, 'Style flags'), ]
        pos = 5
        if flags & cmx_const.INSTR_FILL_FLAG:
            fill = utils.word2py_int(self.chunk[pos:pos + 2], rifx)
            self.cache_fields += [(pos, 2, 'Fill type'), ]
            pos += 2
            if fill == cmx_const.INSTR_FILL_EMPTY:
                pass
            elif fill == cmx_const.INSTR_FILL_UNIFORM:
                self.cache_fields += [(pos, 2, 'Color ref.'), ]
                pos += 2
                self.cache_fields += [(pos, 2, 'Screen ref.'), ]
                pos += 2

        if flags & cmx_const.INSTR_STROKE_FLAG:
            self.cache_fields += [(pos, 2, 'Outline ref.'), ]
            pos += 2

        count = utils.word2py_int(self.chunk[pos:pos + 2], rifx)
        self.cache_fields += [(pos, 2, 'Point count'), ]
        pos += 2
        self.cache_fields += [(pos, 4 * count, 'Points (x,y) int16'), ]
        pos += 4 * count
        self.cache_fields += [(pos, count, 'Nodes (byte)'), ]
        pos += count
        self.cache_fields += [(pos, 8, 'Curve bbox'), ]
        pos += 8


INSTR_16bit = {
    cmx_const.BEGIN_PAGE: Inst16BeginPage,
    cmx_const.BEGIN_LAYER: Inst16BeginLayer,
    cmx_const.BEGIN_GROUP: Inst16BeginGroup,
    cmx_const.POLYCURVE: Inst16PolyCurve
}

INSTR_32bit = {}


def make_instruction(config, chunk):
    instructions = INSTR_16bit if config.v16bit else INSTR_32bit
    identifier = abs(utils.signed_word2py_int(chunk[2:4], config.rifx))
    return instructions.get(identifier, CmxInstruction)(config, chunk)
