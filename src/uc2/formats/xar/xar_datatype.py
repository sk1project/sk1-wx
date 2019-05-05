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

import struct
from uc2.formats.xar.xar_const import CO_ORDINATES_DPI
from uc2.uc2const import in_to_pt

CO_ORDINATES = CO_ORDINATES_DPI / in_to_pt

packer_s3_le = struct.Struct("<3s")

packer_byte = struct.Struct('B')

packer_uint16_le = struct.Struct("<H")
packer_int16_le = struct.Struct("<h")

packer_uint32_le = struct.Struct("<I")
packer_int32_le = struct.Struct("<i")

packer_float_le = struct.Struct("<f")
packer_double_le = struct.Struct("<d")


class BitField(object):
    val = None
    bitfield = None

    def __init__(self, val, bitfield):
        self.val = val
        self.bitfield = bitfield

    def __iter__(self):
        for key in sorted(self.bitfield.keys()):
            val = self.bitfield[key]
            yield val.get('id'), self.__getattr__(val.get('id'))

    def __getattr__(self, item):
        for key, val in self.bitfield.items():
            if item == val.get('id'):
                return bool(self.val & 2 ** key)

    def __setattr__(self, name, value):
        if self.bitfield:
            for index, val in self.bitfield.items():
                if name == val.get('id'):
                    mask = 1 << index
                    if value:
                        self.val |= mask  # Set the bit
                    else:
                        self.val &= ~mask  # Clear the bit
                    return self.val
        return super(BitField, self).__setattr__(name, value)

    def __repr__(self):
        return "%s: %s" % (bin(self.val), list(self))


#######################################


def list_chunks(items, size):
    """Yield successive sized chunks from items."""
    for i in range(0, len(items), size):
        yield items[i:i + size]


########################################

def unpack_u1(data, offset=0, bitfield=None, **kw):
    string = data[offset:offset + 1]
    val = packer_byte.unpack(string)[0]
    if bitfield:
        val = BitField(val, bitfield)
    return val


def unpack_float(data, offset=0, **kw):
    string = data[offset:offset + 4]
    return packer_float_le.unpack(string)[0]


def unpack_double(data, offset=0, **kw):
    string = data[offset:offset + 8]
    return packer_double_le.unpack(string)[0]


def unpack_s4(data, offset=0, bitfield=None, **kw):
    string = data[offset:offset + 4]
    val = packer_int32_le.unpack(string)[0]
    if bitfield:
        val = BitField(val, bitfield)
    return val


def unpack_s2(data, offset=0, bitfield=None, **kw):
    string = data[offset:offset + 2]
    val = packer_int16_le.unpack(string)[0]
    if bitfield:
        val = BitField(val, bitfield)
    return val


def unpack_u2(data, offset=0, bitfield=None, **kw):
    string = data[offset:offset + 2]
    val = packer_uint16_le.unpack(string)[0]
    if bitfield:
        val = BitField(val, bitfield)
    return val


def unpack_fixed16_32(data, offset=0, **kw):
    string = data[offset:offset + 4]
    val = packer_uint32_le.unpack(string)[0]
    ret = 0.0
    if val:
        sing = (val & 0x80000000) >> 31
        if not sing:
            man = (val & 0xFFFF0000) >> 16
            exp = (val & 0x0000FFFF) / 65536.0
            ret = man + exp
        else:
            man = (~val & 0xFFFF0000) >> 16
            exp = (val & 0x0000FFFF) / 65536.0
            ret = ~man + exp
    return ret


def unpack_fixed24_32(data, offset=0, **kw):
    string = data[offset:offset + 4]
    val = packer_uint32_le.unpack(string)[0]
    ret = 0.0
    if val:
        sing = (val & 0x80000000) >> 31
        if not sing:
            man = (val & 0xFF000000) >> 24
            exp = (val & 0x00FFFFFF) / 16777215.0
            ret = man + exp
        else:
            man = (~val & 0xFF000000) >> 24
            exp = (val & 0x00FFFFFF) / 16777215.0
            ret = ~man + exp
    return ret


def unpack_u4(data, offset=0, bitfield=None, **kw):
    string = data[offset:offset + 4]
    val = packer_uint32_le.unpack(string)[0]
    if bitfield:
        val = BitField(val, bitfield)
    return val


def unpack_3s(data, offset=0, encoding=None, **kw):  # XXX
    string = data[offset:offset + 3]
    data = packer_s3_le.unpack(string)[0]
    if encoding:
        data = data.encode(encoding)
    return data


def unpack_millipoint(data, offset=0, **kw):  # XXX
    string = data[offset:offset + 4]
    return packer_int32_le.unpack(string)[0] / CO_ORDINATES


def unpack_coord(data, offset=0, **kw):
    p1 = unpack_millipoint(data, offset)
    p2 = unpack_millipoint(data, offset + 4)
    return [p1, p2]


def read_string(data, offset=0, **kw):
    idx = data.index(b'\0\0', offset)
    size = idx - offset
    size = (size + 1) // 2 * 2
    string = data[offset:offset + size]
    string = string.decode('utf_16_le').encode('utf-8')
    return size + 2, string


def read_ascii_string(data, offset=0, **kw):
    idx = data.index(b'\0', offset)
    size = idx - offset
    return size + 1, data[offset:offset + size]


def read_verb_and_coord_list(data, offset=0, **kw):
    data = data[offset:]
    size = len(data)
    r = []
    for chunk in list_chunks(data, 9):
        verb = packer_byte.unpack(chunk[0:1])[0]
        s = chunk[1:]
        coord_data = s[6:7] + s[4:5] + s[2:3] + s[0:1]
        coord_data += s[7:8] + s[5:6] + s[3:4] + s[1:2]
        coord = unpack_coord(coord_data, 0)
        r.append((verb, coord))
    return size, r


def read_tag_description(data, offset=0, **kw):
    tag = unpack_u4(data, offset)
    offset += 4
    description_size, description = read_string(data, offset)
    offset += description_size
    return 4 + description_size, [tag, description]


def read_stop_colour(data, offset=0, **kw):
    position = unpack_double(data, offset)
    colour = unpack_s4(data, offset + 8)
    return 12, [position, colour]


def read_bitmap_data(data, offset=0, **kw):
    length = len(data) - offset
    return length, (data, offset, length)


# return (size in byte, value)
READER_DATA_TYPES_MAP = {
    'byte': lambda *a, **b: (1, unpack_u1(*a, **b)),
    'uint16': lambda *a, **b: (2, unpack_u2(*a, **b)),
    'uint32': lambda *a, **b: (4, unpack_u4(*a, **b)),

    'fixed24': lambda *a, **b: (4, unpack_fixed24_32(*a, **b)),
    'fixed16': lambda *a, **b: (4, unpack_fixed16_32(*a, **b)),
    'float': lambda *a, **b: (4, unpack_float(*a, **b)),
    'double': lambda *a, **b: (8, unpack_double(*a, **b)),

    'int16': lambda *a, **b: (2, unpack_s2(*a, **b)),
    'int32': lambda *a, **b: (4, unpack_s4(*a, **b)),
    'DATAREF': lambda *a, **b: (4, unpack_s4(*a, **b)),
    'COLOURREF': lambda *a, **b: (4, unpack_s4(*a, **b)),
    'BITMAPREF': lambda *a, **b: (4, unpack_s4(*a, **b)),
    'UNITSREF': lambda *a, **b: (4, unpack_s4(*a, **b)),

    'MILLIPOINT': lambda *a, **b: (4, unpack_millipoint(*a, **b)),
    '3bytes': lambda *a, **b: (3, unpack_3s(*a, **b)),
    'Simple RGBColour': lambda *a, **b: (3, unpack_3s(*a, **b)),
    'COORD': lambda *a, **b: (8, unpack_coord(*a, **b)),

    'STRING': read_string,
    'ASCII_STRING': read_ascii_string,
    'BITMAP_DATA': read_bitmap_data,
    'Tag Description': read_tag_description,
    'Verb and Coord List': read_verb_and_coord_list,
    'StopColour': read_stop_colour,

}


def pack_u1(data, **kw):
    data = data or 0
    return packer_byte.pack(data)


def pack_double(data, **kw):
    data = data or 0
    return packer_double_le.pack(data)


def pack_s4(data, **kw):
    data = data or 0
    return packer_int32_le.pack(data)


def pack_u4(data, **kw):
    data = data or 0
    return packer_uint32_le.pack(data)


def pack_3s(data, encoding=None, **kw):
    data = data or b''
    if encoding:
        data = data.decode(encoding)
    return packer_s3_le.pack(data)


def pack_string(data, **kw):
    data = data or b''
    return data + b'\0\0'


def pack_ascii_string(data, **kw):
    data = data or b''
    return data + b'\0'


def pack_coord(data, **kw):
    data = data or (0, 0)
    p1 = pack_millipoint(data[0])
    p2 = pack_millipoint(data[1])
    return p1 + p2


def pack_millipoint(data, **kw):
    data = data or 0
    data = int(data * CO_ORDINATES)
    return packer_uint32_le.pack(data)


WRITER_DATA_TYPES_MAP = {
    'byte': pack_u1,
    'uint32': pack_u4,
    'double': pack_double,
    '3bytes': pack_3s,
    'STRING': pack_string,
    'ASCII_STRING': pack_ascii_string,
    'MILLIPOINT': pack_millipoint,
    'COORD': pack_coord,
    'Simple RGBColour': pack_3s,
    'COLOURREF': pack_u4,
    # 'BITMAP_DATA':       pack_bitmap_data,
    'UNITSREF': pack_s4,
}
