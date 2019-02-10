# -*- coding: utf-8 -*-
#
#  Copyright (C) 2016 by Igor E. Novikov
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


from struct import calcsize

from uc2.formats.generic_filters import AbstractBinaryLoader, AbstractSaver
from uc2.formats.wmf.wmf_model import META_Placeable_Record, \
    META_Header_Record, WMF_Record
from uc2.formats.wmf.wmf_const import STRUCT_HEADER, STRUCT_PLACEABLE
from uc2.formats.wmf.wmf_const import WMF_SIGNATURE, EOF_RECORD, META_EOF


class WMF_Loader(AbstractBinaryLoader):
    name = 'WMF_Loader'

    def do_load(self):
        self.model = None
        self.parent = None
        sign = self.readbytes(len(WMF_SIGNATURE))
        self.fileptr.seek(0)
        if sign == WMF_SIGNATURE:
            placeable_header = self.readbytes(calcsize(STRUCT_PLACEABLE))
            header = self.readbytes(calcsize(STRUCT_HEADER))
            self.model = META_Placeable_Record(placeable_header)
            self.parent = META_Header_Record(header)
            self.model.childs.append(self.parent)
        else:
            header = self.readbytes(calcsize(STRUCT_HEADER))
            self.model = self.parent = META_Header_Record(header)
        func = -1
        while not func == META_EOF:
            try:
                size = self.readdword()
                func = self.readword()
                self.fileptr.seek(-6, 1)
                chunk = self.readbytes(size * 2)
                self.parent.childs.append(WMF_Record(chunk))
            except:
                func = META_EOF
                self.parent.childs.append(WMF_Record(EOF_RECORD))


class WMF_Saver(AbstractSaver):
    name = 'WMF_Saver'

    def do_save(self):
        self.model.save(self)
