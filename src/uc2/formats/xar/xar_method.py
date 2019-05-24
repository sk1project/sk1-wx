# -*- coding: utf-8 -*-
#
#  Copyright (C) 2019 by Maxim S. Barabash
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

from uc2.formats.xar import xar_const
from uc2.formats.xar import xar_model
from uc2.formats.xar import xar_datatype


def create_new_doc(config):
    doc = xar_model.XARDocument(config)
    return doc


def make_record_header(rec):
    r = xar_datatype.packer_uint32_le.pack(rec.cid)
    r += xar_datatype.packer_uint32_le.pack(len(rec.chunk)-8)
    return r


class XARMethods(object):
    presenter = None
    model = None
    config = None

    def __init__(self, presenter):
        self.presenter = presenter

    def update(self):
        self.model = self.presenter.model
        self.config = self.presenter.config

    def read_path_relative(self, data):
        cx, cy = 0, 0
        path = []
        bez_count = 0
        start_flag = True
        for (verb, (x, y)) in data:
            closed = verb & 0x1
            verb = verb & 0xe
            if verb == xar_const.PT_LINETO:
                cx, cy = cx - x, cy - y
                path.append([cx, cy])
                if closed:
                    yield closed, path
                    path = []
            elif verb == xar_const.PT_BEZIERTO:
                if bez_count == 0:
                    cx, cy = cx - x, cy - y
                    cx1, cy1 = cx, cy
                    bez_count += 1
                elif bez_count == 1:
                    cx, cy = cx - x, cy - y
                    cx2, cy2 = cx, cy
                    bez_count += 1
                elif bez_count == 2:
                    cx, cy = cx - x, cy - y
                    cx3, cy3 = cx, cy
                    bez_count = 0
                    path.append(
                        ([cx1, cy1], [cx2, cy2], [cx3, cy3])
                    )
                    if closed:
                        yield closed, path
                        path = []
            elif verb == xar_const.PT_MOVETO:
                if start_flag:
                    start_flag = False
                    cx, cy = x, y
                    path.append([cx, cy])
                else:
                    if path:
                        yield closed, path
                        path = []
                    cx, cy = cx - x, cy - y
                    path.append([cx, cy])

        if path:
            yield closed, path

    def read_path(self, data):
        path = []
        bez_count = 0
        for (verb, (x, y)) in data:
            closed = verb & 0x1
            verb = verb & 0xe
            if verb == xar_const.PT_LINETO:
                path.append([x, y])
                if closed:
                    yield closed, path
                    path = []
            elif verb == xar_const.PT_BEZIERTO:
                if bez_count == 0:
                    cx1, cy1 = x, y
                    bez_count += 1
                elif bez_count == 1:
                    cx2, cy2 = x, y
                    bez_count += 1
                elif bez_count == 2:
                    cx3, cy3 = x, y
                    bez_count = 0
                    path.append(
                        ([cx1, cy1], [cx2, cy2], [cx3, cy3])
                    )
                    if closed:
                        yield closed, path
                        path = []
            elif verb == xar_const.PT_MOVETO:
                if path:
                    yield closed, path
                    path = []
                path.append([x, y])

        if path:
            yield closed, path
