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


from uc2.formats.generic import BinaryModelObject
from uc2.formats.dst import dst_const
from uc2.formats.dst import dst_datatype


class BaseDstModel(BinaryModelObject):
    cid = dst_const.DST_UNKNOWN
    dx = 0
    dy = 0

    def __init__(self, chunk=None):
        self.chunk = chunk

    def update(self):
        if self.chunk:
            self.parse()
        else:
            self.chunk = self.get_content()

    def parse(self):
        pass

    def get_content(self):
        pass

    def resolve(self):
        is_leaf = True
        if self.childs:
            is_leaf = False
        name = dst_const.CID_TO_NAME.get(self.cid) or self.cid
        info = ''
        return is_leaf, name, info


class DstDocument(BaseDstModel):
    cid = dst_const.DST_DOCUMENT


class DstHeader(BaseDstModel):
    """
    prefix  meaning             length
    LA      Label               16+1
    ST      Stitches            7+1
    CO      Colors              3+1
    +X      +X Extends          5+1
    -X      -X Extends          5+1
    +Y      +Y Extends          5+1
    -Y      -Y Extends          5+1
    AX      Difference          6+1
    AY      Difference          6+1
    MX      Multi-Design Start  6+1
    MY      Multi-Design Start  6+1
    PD      Previous Design?    9+1

    Do note that when writing these *are* required. Some machines do load up
    the first aspects of these to calculate things like percent complete for
    the file by counting the process stitches and using ST as the total.
    And may do things like using the extends to calculate whether it fits in
    the hoop, rather than recalculating these from reprocessing the stitches.
    However, AX, AY, MX, and MY are almost always set to zero and PD always
    to "******".

    1.1 Additional headers
    There are some DST files that contain some additional header information
    of arbitrary size:

    These are exceptionally rare. It is unknown what would make files with
    these metadata tags. However these extensions would allow DST files to
    contain proper thread information simply adding on a reference for each
    thread color as needed. The actual used header within DSTs is 125 out of
    the 512 byte static size header so there is clearly 387 bytes of nothing
    in most files. Using these seems to be pretty easy expansion.

    DST Header Information
    prefix  meaning       length               contents
    AU      Author        variable             Author information.
    CP      Copyright     variable             Copyright information.
    TC      Thread Color  7,variable,variable  "#RRGGBB,Description,Catalog Number"
    hex color code, thread description, and catalog number comma delimited.
    """
    cid = dst_const.DST_HEADER
    metadata = None

    def parse(self):
        self.metadata = {}
        for i in self.chunk.split('\r'):
            if i[2] == ':':
                key, val = i.split(':', 1)
                self.metadata[key] = val.replace(' ', '')

    def update_for_sword(self):
        len_meta = self.chunk.index(dst_const.DATA_TERMINATOR)
        self.cache_fields = [
            (0, len_meta, 'metadata'),
            (len_meta, 1, 'end of metadata'),
            (len_meta + 1, len(self.chunk) - len_meta - 1, 'spaces 0x20'),
        ]

    def get_content(self):
        header = b""
        header += b"LA:%-16s\r" % 'name'
        header += b"ST:%7d\r" % 1
        header += b"CO:%3d\r" % 2
        header += b"+X:%5d\r" % 3
        header += b"-X:%5d\r" % 4
        header += b"+Y:%5d\r" % 5
        header += b"-Y:%5d\r" % 6
        header += b"AX:+%5d\r" % 0
        header += b"AY:+%5d\r" % 0
        header += b"MX:+%5d\r" % 0
        header += b"AY:+%5d\r" % 0
        header += b"PD:%6s\r" % b"******"
        header += dst_const.DATA_TERMINATOR

        spaces = dst_const.DST_HEADER_SIZE - len(header)
        if spaces > 0:
            header += b'\x20' * spaces
        return header


class DstStitch(BaseDstModel):
    """
    Decoding of Byte 1 - 3 :
    Bit No.: 7     6     5     4     3     2     1     0
    Byte 1   y+1   y-1   y+9   y-9   x-9   x+9   x-1   x+1
    Byte 2   y+3   y-3   y+27  y-27  x-27  x+27  x-3   x+3
    Byte 3   C0    C1    y+81  y-81  x-81  x+81  set   set

    Control Codes.
    C0    C1   meaning
    0     0    Normal Stitch.
    1     0    Jump Stitch.
    1     1    Color Change
    0     1    Sequin Mode
    """
    cid = dst_const.DST_UNKNOWN

    def parse(self):
        chunk_length = len(self.chunk)
        if chunk_length == 3:
            self.dx, self.dy, self.cid = dst_datatype.unpack_stitch(self.chunk)
        elif chunk_length == 1 and self.chunk == dst_const.DATA_TERMINATOR:
            self.dx, self.dy, self.cid = 0, 0, dst_const.DATA_TERMINATOR
        else:
            self.dx, self.dy, self.cid = 0, 0, dst_const.DST_UNKNOWN

    def update_for_sword(self):
        self.cache_fields = []
        for i, c in enumerate(self.chunk, 0):
            d = dst_datatype.packer_b.unpack(c)[0]
            field = (i, 1, "d{} {:08b}".format(i+1, d))
            self.cache_fields.append(field)

    def get_content(self):
        if self.cid == dst_const.DATA_TERMINATOR:
            data = dst_const.DATA_TERMINATOR
        elif self.cid == dst_const.DST_UNKNOWN:
            data = self.chunk
        else:
            data = dst_datatype.pack_stitch(self.dx, self.dy, self.cid)
        return data
