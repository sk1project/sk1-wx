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

import struct
from uc2.formats.dst import dst_const

packer_b = struct.Struct("B")
packer_b3 = struct.Struct("BBB")


def byte(num, i):
    return num >> i & 1


def decode_x(d1, d2, d3):
    x = 1 * byte(d1, 7) - 1 * byte(d1, 6) + 9 * byte(d1, 5) - 9 * byte(d1, 4)
    x += 3 * byte(d2, 7) - 3 * byte(d2, 6) + 27 * byte(d2, 5) - 27 * byte(d2, 4)
    x += 81 * byte(d3, 5) - 81 * byte(d3, 4)
    return x


def decode_y(d1, d2, d3):
    y = 1 * byte(d1, 0) - 1 * byte(d1, 1) + 9 * byte(d1, 2) - 9 * byte(d1, 3)
    y += 3 * byte(d2, 0) - 3 * byte(d2, 1) + 27 * byte(d2, 2) - 27 * byte(d2, 3)
    y += 81 * byte(d3, 2) - 81 * byte(d3, 3)
    return y


def decode_command(d3):
    """
    Bit No.: 7     6     5     4     3     2     1     0
    Byte 3   C0    C1    y+81  y-81  x-81  x+81  set   set
    Control Codes.
    C0    C1   meaning
    0     0    Normal Stitch.
    1     0    Jump Stitch.
    1     1    Color Change
    0     1    Sequin Mode
    """
    if d3 == dst_const.CMD_STOP:
        return dst_const.CMD_STOP
    cmd = d3 & dst_const.MASK_CMD
    return cmd if cmd in dst_const.KNOWN_CMD else dst_const.DST_UNKNOWN


def unpack_stitch(data):
    d1, d2, d3 = packer_b3.unpack(data[:3])
    x = decode_x(d1, d2, d3)
    y = decode_y(d1, d2, d3)
    cmd = decode_command(d3)
    return x, y, cmd
