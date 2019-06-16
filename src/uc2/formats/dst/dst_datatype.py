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

packer_uint32_be = struct.Struct(">I")

SEQUENCE_X = (81, 40, 2), (27, 13, 10), (9, 4, 18), (3, 1, 8), (1, 0, 16)
SEQUENCE_Y = (81, 40, 5), (27, 13, 13), (9, 4, 21), (3, 1, 15), (1, 0, 23)


def pack_24_be(val):
    return packer_uint32_be.pack(val)[1:]


def bit(num, index):
    return num >> index & 1


def set_bit(value, index):
    mask = 1 << index
    value |= mask  # Set the bit
    return value


def unpack_stitch(data):
    d1, d2, d3 = packer_b3.unpack(data[:3])
    x = decode_x(d1, d2, d3)
    y = decode_y(d1, d2, d3)
    cmd = decode_command(d3)
    return x, y, cmd


def pack_stitch(x, y, cmd):
    val = code_x(x) | code_y(y) | cmd
    return pack_24_be(val)


def decode_x(d1, d2, d3):
    x = 1 * bit(d1, 0) - 1 * bit(d1, 1) + 9 * bit(d1, 2) - 9 * bit(d1, 3)
    x += 3 * bit(d2, 0) - 3 * bit(d2, 1) + 27 * bit(d2, 2) - 27 * bit(d2, 3)
    x += 81 * bit(d3, 2) - 81 * bit(d3, 3)
    return x


def decode_y(d1, d2, d3):
    y = 1 * bit(d1, 7) - 1 * bit(d1, 6) + 9 * bit(d1, 5) - 9 * bit(d1, 4)
    y += 3 * bit(d2, 7) - 3 * bit(d2, 6) + 27 * bit(d2, 5) - 27 * bit(d2, 4)
    y += 81 * bit(d3, 5) - 81 * bit(d3, 4)
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


def code_x(x, maximum=dst_const.MAX_DISTANCE, minimum=-dst_const.MAX_DISTANCE):
    val = 0

    if minimum > x or x > maximum:
        msg = 'The value must be [%s:%s], given %s' % (minimum, maximum, x)
        raise Exception(msg)

    for cubic, quad, idx in SEQUENCE_X:
        if x > quad:
            val = set_bit(val, idx)
            x -= cubic
        elif x < -quad:
            val = set_bit(val, idx + 1)
            x += cubic
    return val


def code_y(y, maximum=dst_const.MAX_DISTANCE, minimum=-dst_const.MAX_DISTANCE):
    val = 0

    if minimum > y or y > maximum:
        msg = 'The value must be [%s:%s], given %s' % (minimum, maximum, y)
        raise Exception(msg)

    for cubic, quad, idx in SEQUENCE_Y:
        if y > quad:
            val = set_bit(val, idx)
            y -= cubic
        elif y < -quad:
            val = set_bit(val, idx - 1)
            y += cubic
    return val

