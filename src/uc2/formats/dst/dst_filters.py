# -*- coding: utf-8 -*-
#
#  Copyright (C) 2009-2019 by Maxim S. Barabash
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


from uc2.formats.generic_filters import AbstractLoader, AbstractSaver
from uc2.formats.edr_pal import EDR_Palette
from uc2.formats.dst import dst_model
from uc2.formats.dst import dst_const


class DST_Loader(AbstractLoader):
    name = 'DST_Loader'

    def do_load(self):
        stream = self.fileptr
        self.presenter.palette = EDR_Palette(self.filepath)

        self.model.childs = []
        parent_stack = self.model.childs

        chunk = stream.read(dst_const.DST_HEADER_SIZE)
        header = dst_model.DstHeader(chunk)
        parent_stack.append(header)

        while True:
            chunk = stream.read(3)
            if chunk:
                stitch = dst_model.DstStitch(chunk)
                parent_stack.append(stitch)
            else:
                break


class DST_Saver(AbstractSaver):
    name = 'DST_Saver'

    def do_save(self):
        header = b""
        body = b""
        parent_stack = self.model.childs
        if len(parent_stack) > 1:
            for child in parent_stack[1:]:
                body += child.chunk  # get_content()
            header = parent_stack[0].get_content()  # b'\x20' * DST_HEADER_SIZE

        self.fileptr.write(header)
        self.fileptr.write(body)
