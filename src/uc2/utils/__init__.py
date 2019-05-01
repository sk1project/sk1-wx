# -*- coding: utf-8 -*-
#
#  Copyright (C) 2003-2015 by Igor E. Novikov
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

import base64
import math
import time
import struct


def generate_base64_id():
    """
    Generates bas64 encoded id based on UNIX time
    """
    time.sleep(0.001)
    return base64.b64encode(str(int(time.time() * 100000)))


def generate_id():
    """
    Generates numeric id based on UNIX time
    """
    time.sleep(0.001)
    return str(int(time.time() * 100000))


def generate_guid():
    import uuid
    time.sleep(0.001)
    return str(uuid.uuid1())


def byte2py_int(data):
    """
    Converts byte to Python int value.
    """
    return struct.unpack('B', data)[0]


def py_int2byte(val):
    """
    Converts Python int value to byte.
    """
    return struct.pack('B', val)


def word2py_int(data, be=False):
    """
    Converts word of bytes to Python int value.
    """
    sig = '>H' if be else '<H'
    return struct.unpack(sig, data)[0]


def signed_word2py_int(data, be=False):
    """
    Converts word of bytes to Python int value.
    """
    sig = '>h' if be else '<h'
    return struct.unpack(sig, data)[0]


def py_int2word(val, be=False):
    """
    Converts Python int value to word of bytes.
    """
    sig = '>H' if be else '<H'
    return struct.pack(sig, val)


def py_int2signed_word(val, be=False):
    """
    Converts Python int value to word of bytes.
    """
    sig = '>h' if be else '<h'
    return struct.pack(sig, val)


def dword2py_int(data, be=False):
    """
    Converts double word of bytes to Python int value.
    """
    sig = '>I' if be else '<I'
    return struct.unpack(sig, data)[0]


def py_int2dword(val, be=False):
    """
    Converts Python int value to double word of bytes.
    """
    sig = '>I' if be else '<I'
    return struct.pack(sig, val)


def py_int2signed_dword(val, be=False):
    """
    Converts Python int value to signed double word of bytes.
    """
    sig = '>i' if be else '<i'
    return struct.pack(sig, val)


def pair_dword2py_int(data):
    """
    Converts pair of double words (8 bytes) to pair ofPython int value.
    """
    return struct.unpack('<2L', data)


def double2py_float(data):
    """
    Converts 8 bytes to Python float value.
    """
    return struct.unpack('<d', data)[0]


def py_float2float(val, be=False):
    """
    Converts Python float to 4 bytes (double)
    """
    sig = '>f' if be else '<f'
    return struct.pack(sig, val)


def py_float2double(val, be=False):
    """
    Converts Python float to 8 bytes (double)
    """
    sig = '>d' if be else '<d'
    return struct.pack(sig, val)


def long2py_float(data):
    """
    Converts 4 bytes to Python float value.
    """
    return struct.unpack('<l', data)[0]


def latin1_bytes_2str(data):
    """
    Converts Latin1 bytes to Python string value.
    """
    length = len(data)
    return unicode(struct.unpack(str(length) + 's', data)[0], 'latin1').\
        encode('utf-8')


def utf_16_le_bytes_2str(data):
    """
    Converts utf16 bytes to Python string value.
    """
    length = len(data)
    return unicode(struct.unpack(str(length) + 's', data)[0], 'utf_16_le').\
        encode('utf-8')


def get_chunk_size(size_field):
    size = dword2py_int(size_field)
    if not size % 2 == 0:
        size += 1
    return size


def uint16_be(chunk):
    """
    Converts 2 bytes to unsigned int (big endian)
    """
    return struct.unpack(">H", chunk)[0]


def dib_to_bmp(dib):
    """
    Reconstructs BMP bitmap file header for DIB

    :param dib: device-independent bitmap string
    :return: BMP string
    """
    #
    offset = dib_header_size = struct.unpack('<I', dib[:4])[0]
    if dib_header_size == 12:
        bitsperpixel = struct.unpack('<h', dib[10:12])[0]
        if not bitsperpixel > 8:
            offset += math.pow(2, bitsperpixel) * 3
    else:
        bitsperpixel = struct.unpack('<h', dib[14:16])[0]
        colorsnum = struct.unpack('<I', dib[32:36])[0]
        if bitsperpixel > 8:
            offset += colorsnum * 3
        else:
            offset += math.pow(2, bitsperpixel) * 3
    offset = math.ceil(offset / 4.0) * 4

    pixel_offset = struct.pack('<I', 14 + offset)
    file_size = struct.pack('<I', 14 + len(dib))
    return 'BM' + file_size + '\x00\x00\x00\x00' + pixel_offset + dib


def bmp_to_dib(bmp):
    """
    Extracts DIB from BMP

    :param bmp: BMP string
    :return: DIB string
    """
    return bmp[14:]