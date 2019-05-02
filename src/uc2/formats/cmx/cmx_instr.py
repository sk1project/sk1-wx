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


class CmxInstruction(BinaryModelObject):
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

    def update_from_chunk(self):
        pass

    def get_chunk_size(self):
        return len(self.chunk)

    def _get_code(self, code_str):
        return abs(utils.signed_word2py_int(code_str, self.config.rifx))

    def _get_code_str(self):
        return utils.py_int2word(self.data['code'], self.config.rifx)

    def get_name(self):
        return cmx_const.INSTR_CODES.get(self.data['code'],
                                         str(self.data['code']))

    def resolve(self, name=''):
        sz = '%d' % self.get_chunk_size()
        name = '[%s]' % self.get_name()
        return len(self.childs) == 0, name, sz

    def update(self):
        size = self.get_chunk_size()
        sz = utils.py_int2word(size, self.config.rifx)
        self.chunk = sz + self._get_code_str() + self.chunk[4:]

    def update_for_sword(self):
        self.cache_fields = [(0, 2, 'Instruction Size'),
                             (2, 2, 'Instruction Code')]


def make_instruction(config, chunk):
    return CmxInstruction(config, chunk)
