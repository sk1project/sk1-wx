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
import struct

from uc2 import utils, libgeom
from uc2.formats.cmx import cmx_const
from uc2.formats.generic import BinaryModelObject

LOG = logging.getLogger(__name__)


class CmxObject(BinaryModelObject):
    toplevel = False
    data = None
    offset = 0

    def get_root(self):
        parent = self
        while not parent.toplevel:
            parent = parent.parent
        return parent

    def get(self, name, default=None):
        return self.data.get(name, default)

    def set(self, name, value):
        self.data[name] = value

    def is_padding(self):
        sz = len(self.chunk)
        return sz > (sz // 2) * 2

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
    bbox = None
    is_layer = False
    is_page = False

    def __init__(self, config, chunk=None, offset=0, **kwargs):
        self.config = config
        self.offset = offset
        self.childs = []
        self.data = {}
        self.bbox = None

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

    def get_bbox(self):
        def _sum_bbox(bbox0, bbox1):
            if bbox0 is None and bbox1 is None:
                return None
            if bbox0 is None:
                return [] + bbox1
            if bbox1 is None:
                return [] + bbox0
            return libgeom.sum_bbox(bbox0, bbox1)
        self.bbox = None
        for child in self.childs:
            self.bbox = _sum_bbox(self.bbox, child.get_bbox())
        return self.bbox

    def resolve(self, name=''):
        sz = '%d' % len(self.chunk)
        offset = hex(self.get_offset())
        name = '[%s]' % self.get_name()
        return len(self.childs) == 0, name, offset  # sz

    def update(self):
        if self.is_padding():
            self.chunk += '\x00'
        size = len(self.chunk)
        sz = utils.py_int2word(size, self.config.rifx)
        self.chunk = sz + self._get_code_str() + self.chunk[4:]

    def update_for_sword(self):
        self.cache_fields = [(0, 2, 'Instruction Size'),
                             (2, 2, 'Instruction Code\n')]


class Inst16BeginPage(CmxInstruction):
    is_page = True

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
    is_layer = True

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


class Inst16JumpAbsolute(CmxInstruction):
    def update_from_chunk(self):
        rifx = self.config.rifx
        self.data['jump'] = utils.dword2py_int(self.chunk[4:8], rifx)

    def update(self):
        rifx = self.config.rifx
        pos = self.get_offset()
        jump = self.data['jump'] = len(self.chunk) + pos
        data = self.chunk[8:]
        self.chunk = '\x08\x00\x6f\x00'
        self.chunk += utils.py_int2dword(jump, rifx) + data

    def update_for_sword(self):
        CmxInstruction.update_for_sword(self)
        sz = len(self.chunk) - 8
        self.cache_fields += [
            (4, 8, 'Jump absolute offset'),
            (8, sz, 'Data'),
        ]


class Inst16PolyCurve(CmxInstruction):
    def update_from_chunk(self):
        rifx = self.config.rifx
        self.data['tail'] = ''
        flags = self.data['style_flags'] = utils.byte2py_int(self.chunk[4])
        pos = 5
        if flags & cmx_const.INSTR_FILL_FLAG:
            fill = utils.word2py_int(self.chunk[pos:pos + 2], rifx)
            self.data['fill_type'] = fill
            pos += 2
            # FILL
            if fill == cmx_const.INSTR_FILL_EMPTY:
                pass
            elif fill == cmx_const.INSTR_FILL_UNIFORM:
                # (color, screen)
                sig = '>hh' if rifx else '<hh'
                self.data['fill'] = struct.unpack(sig, self.chunk[pos:pos + 4])
                pos += 4
            elif fill == cmx_const.INSTR_FILL_FOUNTAIN:
                # (type, screen, padding, angle, x, y, steps, mode, clr_count)
                sig = '>hhhihhhh' if rifx else '<hhhihhhh'
                self.data['fill'] = struct.unpack(sig, self.chunk[pos:pos + 18])
                pos += 18
                # steps: [(color, pos)]
                sig = '>hh' if rifx else '<hh'
                steps = self.data['steps'] = []
                for _ in range(self.data['fill'][-1]):
                    steps.append(struct.unpack(sig, self.chunk[pos:pos + 4]))
                    pos += 4
            else:
                self.data['tail'] = self.chunk[pos:]
                return

        # OUTLINE
        if flags & cmx_const.INSTR_STROKE_FLAG:
            self.data['outline'] = utils.word2py_int(
                self.chunk[pos:pos + 2], rifx)
            pos += 2

        if flags >= cmx_const.INSTR_LENS_FLAG:
            self.data['tail'] = self.chunk[pos:]
            return

        # POINTS & NODES
        # points: [(x,y),...]
        count = utils.word2py_int(self.chunk[pos:pos + 2], rifx)
        pos += 2
        points = self.data['points'] = []
        sig = '>hh' if rifx else '<hh'
        for _ in range(count):
            points.append(struct.unpack(sig, self.chunk[pos:pos + 4]))
            pos += 4
        # nodes: (node,...)
        sig = count * 'B'
        self.data['nodes'] = struct.unpack(sig, self.chunk[pos:pos + count])
        pos += count
        # BBOX
        sig = '>hhhh' if rifx else '<hhhh'
        self.data['bbox'] = struct.unpack(sig, self.chunk[pos:pos + 8])
        pos += 8

        if pos < len(self.chunk):
            self.data['tail'] = self.chunk[pos:]

    def update(self):
        rifx = self.config.rifx
        int2word = utils.py_int2word
        self.chunk = '\x00\x00' + int2word(self.data['code'], rifx)
        self.chunk += utils.py_int2byte(self.data['style_flags'])
        skip = False
        flags = self.data['style_flags']
        # FILL
        if flags & cmx_const.INSTR_FILL_FLAG:
            self.chunk += int2word(self.data['fill_type'], rifx)
            if self.data['fill_type'] == cmx_const.INSTR_FILL_EMPTY:
                pass
            elif self.data['fill_type'] == cmx_const.INSTR_FILL_UNIFORM:
                # (color, screen)
                sig = '>hh' if rifx else '<hh'
                self.chunk += struct.pack(sig, *self.data['fill'])
            elif self.data['fill_type'] == cmx_const.INSTR_FILL_FOUNTAIN:
                sig = '>hhhihhhh' if rifx else '<hhhihhhh'
                self.chunk += struct.pack(sig, *self.data['fill'])
                sig = '>hh' if rifx else '<hh'
                for item in self.data['steps']:
                    self.chunk += struct.pack(sig, *item)
            else:
                skip = True

        if not skip:
            # OUTLINE
            if flags & cmx_const.INSTR_STROKE_FLAG:
                self.chunk += int2word(self.data['outline'], rifx)

            if not flags >= cmx_const.INSTR_LENS_FLAG:
                # POINTS
                self.chunk += int2word(len(self.data['points']), rifx)
                for point in self.data['points']:
                    sig = '>hh' if rifx else '<hh'
                    self.chunk += struct.pack(sig, *point)
                # NODES
                self.chunk += struct.pack('B' * len(self.data['nodes']),
                                          *self.data['nodes'])
                # BBOX
                sig = '>hhhh' if rifx else '<hhhh'
                self.chunk += struct.pack(sig, *self.data['bbox'])

        self.chunk += self.data['tail']
        CmxInstruction.update(self)

    def update_for_sword(self):
        rifx = self.config.rifx
        CmxInstruction.update_for_sword(self)
        flags = utils.byte2py_int(self.chunk[4])
        self.cache_fields += [(4, 1, 'Style flags'), ]
        pos = 5
        if flags & cmx_const.INSTR_FILL_FLAG:
            fill = utils.word2py_int(self.chunk[pos:pos + 2], rifx)
            f = cmx_const.FILL_TYPE_MAP.get(fill, 'UNKNOWN')
            self.cache_fields += [(pos, 2, 'Fill type: %s' % f), ]
            pos += 2
            if fill == cmx_const.INSTR_FILL_EMPTY:
                pass
            elif fill == cmx_const.INSTR_FILL_UNIFORM:
                self.cache_fields += [(pos, 2, 'Color ref.'), ]
                pos += 2
                self.cache_fields += [(pos, 2, 'Screen ref.'), ]
                pos += 2
            elif fill == cmx_const.INSTR_FILL_FOUNTAIN:
                f = utils.word2py_int(self.chunk[pos:pos + 2], rifx)
                f = cmx_const.FILL_FOUNTAINS.get(f, 'unknown')
                self.cache_fields += [(pos, 2, 'Fountain type: %s' % f), ]
                pos += 2
                self.cache_fields += [(pos, 2, 'Screen ref.'), ]
                pos += 2
                self.cache_fields += [(pos, 2, 'Padding'), ]
                pos += 2
                self.cache_fields += [(pos, 4, 'Angle'), ]
                pos += 4
                self.cache_fields += [(pos, 4, 'Offset (x,y) int16'), ]
                pos += 4
                self.cache_fields += [(pos, 2, 'Steps'), ]
                pos += 2
                self.cache_fields += [(pos, 2, 'Mode'), ]
                pos += 2
                color_count = utils.word2py_int(self.chunk[pos:pos + 2], rifx)
                self.cache_fields += [(pos, 2,
                                       'Color count (%d)' % color_count), ]
                pos += 2
                for _i in range(color_count):
                    self.cache_fields += [(pos, 2, 'Color ref.'), ]
                    pos += 2
                    self.cache_fields += [(pos, 2, 'Position'), ]
                    pos += 2
            else:
                pos, sz, txt = self.cache_fields[-1]
                txt += '\n       UNSUPPORTED FILL TYPE!'
                self.cache_fields[-1] = (pos, sz, txt)
                return

        if flags & cmx_const.INSTR_STROKE_FLAG:
            self.cache_fields += [(pos, 2, 'Outline ref.'), ]
            pos += 2

        if flags >= cmx_const.INSTR_LENS_FLAG:
            pos, sz, txt = self.cache_fields[-1]
            sp = '\n       '
            txt += '%sUNSUPPORTED LENS, CANVAS %sOR CONTAINER!' % (sp, sp)
            self.cache_fields[-1] = (pos, sz, txt)
            return

        count = utils.word2py_int(self.chunk[pos:pos + 2], rifx)
        self.cache_fields += [(pos, 2, 'Point count (%d)' % count), ]
        pos += 2
        self.cache_fields += [(pos, 4 * count, 'Points [(x,y),] int16'), ]
        pos += 4 * count
        self.cache_fields += [(pos, count, 'Nodes [byte,]'), ]
        pos += count
        self.cache_fields += [(pos, 8, 'Curve bbox'), ]
        pos += 8

    def get_bbox(self):
        bbox = self.data.get('bbox')
        return list(bbox) if bbox else None

INSTR_16bit = {
    cmx_const.BEGIN_PAGE: Inst16BeginPage,
    cmx_const.BEGIN_LAYER: Inst16BeginLayer,
    cmx_const.BEGIN_GROUP: Inst16BeginGroup,
    cmx_const.POLYCURVE: Inst16PolyCurve,
    cmx_const.JUMP_ABSOLUTE: Inst16JumpAbsolute,
}

INSTR_32bit = {}


def make_instruction(config, chunk=None, offset=0, identifier=None, **kwargs):
    instructions = INSTR_16bit if config.v16bit else INSTR_32bit
    if chunk is not None:
        identifier = abs(utils.signed_word2py_int(chunk[2:4], config.rifx))
    cls = instructions.get(identifier, CmxInstruction)
    kwargs['code'] = identifier
    return cls(config, chunk, offset, **kwargs)
