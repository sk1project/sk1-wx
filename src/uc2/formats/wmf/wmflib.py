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

import math
from struct import unpack, pack

from uc2.formats.wmf import wmf_const


def get_markup(record):
    markup = [] + wmf_const.GENERIC_FIELDS
    if record.func in wmf_const.RECORD_MARKUPS:
        markup += wmf_const.RECORD_MARKUPS[record.func]

    if record.func == wmf_const.META_POLYGON:
        last = markup[-1]
        pos = last[0] + last[1]
        length = 4 * unpack('<h', record.chunk[last[0]:last[0] + 2])[0]
        markup.append((pos, length, 'aPoints (32-bit points)'))
    elif record.func == wmf_const.META_POLYPOLYGON:
        pos = 6
        markup.append((pos, 2, 'NumberofPolygons'))
        polygonnum = unpack('<h', record.chunk[pos:pos + 2])[0]
        pos += 2
        pointnums = []
        for i in range(polygonnum):
            pointnums.append(unpack('<h', record.chunk[pos:pos + 2])[0])
            markup.append((pos, 2, 'NumberofPoints'))
            pos += 2
        for pointnum in pointnums:
            length = 4 * pointnum
            markup.append((pos, length, 'aPoints (32-bit points)'))
            pos += length
    elif record.func == wmf_const.META_POLYLINE:
        pos = 6
        markup.append((pos, 2, 'NumberofPoints'))
        pointnum = unpack('<h', record.chunk[pos:pos + 2])[0]
        pos += 2
        length = 4 * pointnum
        markup.append((pos, length, 'aPoints (32-bit points)'))
    elif record.func == wmf_const.META_TEXTOUT:
        pos = 6
        markup.append((pos, 2, 'StringLength'))
        length = unpack('<h', record.chunk[pos:pos + 2])[0]
        if length % 2: length += 1
        pos += 2
        markup.append((pos, length, 'String'))
        pos += length
        markup.append((pos, 2, 'YStart'))
        pos += 2
        markup.append((pos, 2, 'XStart'))
    elif record.func == wmf_const.META_EXTTEXTOUT:
        pos = 6
        markup.append((pos, 2, 'Y'))
        pos += 2
        markup.append((pos, 2, 'X'))
        pos += 2
        markup.append((pos, 2, 'StringLength'))
        length = unpack('<h', record.chunk[pos:pos + 2])[0]
        if length % 2: length += 1
        pos += 2
        markup.append((pos, 2, 'fwOpts'))
        pos += 2
        if len(record.chunk) - pos == length:
            markup.append((pos, length, 'String'))
        else:
            markup.append((pos, 8, 'Rectangle'))
            pos += 8
            markup.append((pos, length, 'String'))
            pos += length
            if not len(record.chunk) == pos:
                length = len(record.chunk) - pos
                markup.append((pos, length, 'Dx'))
    elif record.func == wmf_const.META_CREATEFONTINDIRECT:
        pos = 6
        markup.append((pos, 2, 'Height'))
        pos += 2
        markup.append((pos, 2, 'Width'))
        pos += 2
        markup.append((pos, 2, 'Escapement'))
        pos += 2
        markup.append((pos, 2, 'Orientation'))
        pos += 2
        markup.append((pos, 2, 'Weight'))
        pos += 2
        markup.append((pos, 1, 'Italic'))
        pos += 1
        markup.append((pos, 1, 'Underline'))
        pos += 1
        markup.append((pos, 1, 'StrikeOut'))
        pos += 1
        markup.append((pos, 1, 'CharSet'))
        pos += 1
        markup.append((pos, 1, 'OutPrecision'))
        pos += 1
        markup.append((pos, 1, 'ClipPrecision'))
        pos += 1
        markup.append((pos, 1, 'Quality'))
        pos += 1
        markup.append((pos, 1, 'PitchAndFamily'))
        pos += 1
        length = len(record.chunk) - pos
        markup.append((pos, length, 'Facename'))
    elif record.func == wmf_const.META_DIBCREATEPATTERNBRUSH:
        pos = 6
        markup.append((pos, 2, 'Style'))
        pos += 2
        markup.append((pos, 2, 'ColorUsage'))
        pos += 2
        length = len(record.chunk) - pos
        markup.append((pos, length, 'Variable-bit DIB Object'))
    elif record.func == wmf_const.META_STRETCHDIB:
        pos = 6
        markup.append((pos, 4, 'RasterOperation'))
        pos += 4
        markup.append((pos, 2, 'ColorUsage'))
        pos += 2
        markup.append((pos, 2, 'SrcHeight'))
        pos += 2
        markup.append((pos, 2, 'SrcWidth'))
        pos += 2
        markup.append((pos, 2, 'YSrc'))
        pos += 2
        markup.append((pos, 2, 'XSrc'))
        pos += 2
        markup.append((pos, 2, 'DestHeight'))
        pos += 2
        markup.append((pos, 2, 'DestWidth'))
        pos += 2
        markup.append((pos, 2, 'yDst'))
        pos += 2
        markup.append((pos, 2, 'xDst'))
        pos += 2
        length = len(record.chunk) - pos
        markup.append((pos, length, 'Variable-bit DIB Object'))

    return markup


def get_data(fmt, chunk):
    return unpack(fmt, chunk)


def rnd2int(val):
    return int(round(val))


def rndpoint(point):
    return [rnd2int(point[0]), rnd2int(point[1])]


def dib_to_imagestr(dib):
    # Reconstrution of BMP bitmap file header
    offset = dib_header_size = get_data('<I', dib[:4])[0]
    if dib_header_size == 12:
        bitsperpixel = get_data('<h', dib[10:12])[0]
        if not bitsperpixel > 8:
            offset += math.pow(2, bitsperpixel) * 3
    else:
        bitsperpixel = get_data('<h', dib[14:16])[0]
        colorsnum = get_data('<I', dib[32:36])[0]
        if bitsperpixel > 8:
            offset += colorsnum * 3
        else:
            offset += math.pow(2, bitsperpixel) * 3
    offset = math.ceil(offset / 4.0) * 4

    pixel_offset = pack('<I', 14 + offset)
    file_size = pack('<I', 14 + len(dib))
    return 'BM' + file_size + '\x00\x00\x00\x00' + pixel_offset + dib


def parse_nt_string(ntstring):
    ret = ''
    for item in ntstring:
        if item == '\x00': break
        ret += item
    return ret
