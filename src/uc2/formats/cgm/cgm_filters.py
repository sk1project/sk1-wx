# -*- coding: utf-8 -*-
#
#  Copyright (C) 2017-2019 by Igor E. Novikov
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

from uc2.formats.cgm import cgm_utils, cgm_const, cgm_model
from uc2.formats.generic_filters import AbstractBinaryLoader, AbstractSaver


class CgmLoader(AbstractBinaryLoader):
    name = 'CGM_Loader'
    parent_stack = None

    def do_load(self):
        self.model = cgm_model.CgmMetafile()
        self.parent_stack = [self.model]
        self.fileptr.seek(0, 2)
        filesz = self.fileptr.tell()
        self.fileptr.seek(0, 0)
        while self.fileptr.tell() < filesz:
            header = self.fileptr.read(2)
            element_id, size = cgm_utils.parse_header(header)[1:]
            if size == 0x1f:
                header += self.fileptr.read(2)
                size = cgm_utils.parse_header(header)[2]
            params = self.fileptr.read(((size + 1) // 2) * 2)
            if element_id == cgm_const.BEGIN_PICTURE:
                picture = cgm_model.CgmPicture()
                self.parent_stack[-1].add(picture)
                self.parent_stack.append(picture)
            if element_id == cgm_const.END_METAFILE \
                    and len(self.parent_stack) > 1:
                self.parent_stack = self.parent_stack[:-1]

            self.parent_stack[-1].add(cgm_model.element_factory(header, params))

            if element_id == cgm_const.END_PICTURE:
                self.parent_stack = self.parent_stack[:-1]
        self.parent_stack = None


class CgmSaver(AbstractSaver):
    name = 'CGM_Saver'

    def do_save(self):
        self.model.save(self)
