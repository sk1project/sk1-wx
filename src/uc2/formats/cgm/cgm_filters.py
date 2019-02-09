# -*- coding: utf-8 -*-
#
#  Copyright (C) 2017 by Igor E. Novikov
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
from uc2.formats.cgm.cgm_model import CgmElement, CgmMetafile
from uc2.formats.generic_filters import AbstractBinaryLoader, AbstractSaver


class CgmLoader(AbstractBinaryLoader):
    name = 'CGM_Loader'

    def do_load(self):
        self.model = CgmMetafile()
        self.fileptr.seek(0, 2)
        filesz = self.fileptr.tell()
        self.fileptr.seek(0, 0)
        while self.fileptr.tell() < filesz:
            header = self.fileptr.read(2)
            size = utils.uint16(header) & 0x001f

            if size == 31:
                header += self.fileptr.read(2)
                size = utils.uint16(header[2:]) & 0x7fff

            paramsz = ((size + 1) / 2) * 2
            params = self.fileptr.read(paramsz)
            self.model.childs.append(CgmElement(header, params))


class CgmSaver(AbstractSaver):
    name = 'CGM_Saver'

    def do_save(self):
        self.model.save(self)
