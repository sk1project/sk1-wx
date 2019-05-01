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
from uc2.formats.generic_filters import AbstractBinaryLoader, AbstractSaver
from uc2.formats.cmx import cmx_model, cmx_const


class CmxLoader(AbstractBinaryLoader):
    name = 'CMX_Loader'
    parent_stack = None

    def do_load(self):
        self.fileptr.seek(0, 0)
        dwords, size = self.read_header()
        self.model = cmx_model.CmxRoot(self.config, ''.join(dwords))
        self.parent_stack = [self.model]
        self.parse(size)
        self.parent_stack = None

    def read_header(self):
        identifier = self.fileptr.read(4)
        sz = self.fileptr.read(4)
        name = self.fileptr.read(4) \
            if identifier in cmx_const.LIST_IDS else ''
        shift = 4 if name else 0
        size = utils.dword2py_int(sz, self.config.rifx) - shift
        size += 1 if size > (size // 2) * 2 else 0
        return [identifier, sz, name], size

    def parse(self, chunk_size):
        position = self.fileptr.tell()
        while self.fileptr.tell() - position < chunk_size:
            dwords, size = self.read_header()

            if not dwords[2]:
                dwords.append(self.fileptr.read(size))

            node = cmx_model.make_cmx_chunk(self.config, ''.join(dwords))
            self.parent_stack[-1].add(node)

            if dwords[2]:
                self.parent_stack.append(node)
                self.parse(size)
                self.parent_stack = self.parent_stack[:-1]


class CmxSaver(AbstractSaver):
    name = 'CMX_Saver'

    def do_save(self):
        self.model.save(self)
