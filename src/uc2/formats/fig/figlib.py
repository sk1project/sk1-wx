# -*- coding: utf-8 -*-
#
#  Copyright (C) 2018 by Maxim S. Barabash
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


import re
from math import ceil
from uc2 import libgeom
from . import fig_const


RE_CHUNK = re.compile(r'(\s*[\S]+\s?)')


def list_chunks(items, size):
    """Yield successive sized chunks from iteml."""
    for i in range(0, len(items), size):
        yield items[i:i + size]


def octal_escape(char):
    if char == '\\':
        return '\\\\'
    code = ord(char)
    return char if 1 < code <= 127 else '\\{:03o}'.format(code)


def un_escape(source):
    return source.decode("unicode-escape").encode('utf-8')


def escape(encoded):
    return ''.join(octal_escape(c) for c in encoded.decode('utf-8'))


def unpack(fmt, string):
    """
    Unpack the string according to the given format.
    :param fmt: format characters have the following meaning:
        i - int
        f - float
        s - string
    :param string: string to unpack
    :return: generator
    """
    chunks = RE_CHUNK.findall(string)
    for i, c in enumerate(fmt):
        chunk = chunks[i]
        if c == 'i':
            chunk = int(chunk)
        elif c == 'f':
            chunk = float(chunk)
        elif c == 's':
            chunk = ''.join(chunks[i:])
        yield chunk


def pack(data, fmt):
    chunks = []
    for idx, c in enumerate(fmt):
        val = data[idx]
        if c == 'i':
            chunks.append('{:.0f}'.format(ceil(val)))
        elif c == 'f':
            chunks.append('{}'.format(val))
        elif c == 's':
            chunks.append(val)
    return ' '.join(chunks)


def ctrl_points(p0, p1, p2, t=1.0):
    d01 = libgeom.distance(p1, p0)
    d12 = libgeom.distance(p2, p1)
    if not d01 or not d12:
        return p0[:], p1[:]

    fa = t * d01 / (d01 + d12)
    fb = t * d12 / (d01 + d12)

    p1x = p1[0] - fa * (p2[0] - p0[0])
    p1y = p1[1] - fa * (p2[1] - p0[1])

    p2x = p1[0] + fb * (p2[0] - p0[0])
    p2y = p1[1] + fb * (p2[1] - p0[1])
    return [p1x, p1y], [p2x, p2y]


def spline_sub_type(sub_type, version):
    if version >= 3.2:
        t_open = (
            fig_const.T_OPEN_APPROX,
            fig_const.T_OPEN_INTERPOLATED,
        )
        t_closed = (
            fig_const.T_CLOSED_APPROX,
            fig_const.T_CLOSED_INTERPOLATED,
        )
        if sub_type in t_open:
            sub_type = fig_const.T_OPEN_XSPLINE
        elif sub_type in t_closed:
            sub_type = fig_const.T_CLOSED_XSPLINE
    return sub_type


def font_description(font):
    # FIXME: This is a dirty implementation. requires reimplementation
    font_family, _, font_face = font.partition('-')
    if not font_family or font_family == "Default":
        font_family = 'Times'
    font_face = font_face or 'Regular'
    font_face = re.findall('[A-Z][^A-Z]*', font_face)
    for i, face in enumerate(font_face):
        if face == 'Demi':
            font_face[i] = 'Bold'
    return font_family, font_face


def font(font_family, font_face):
    # FIXME: This is a dirty implementation. requires reimplementation
    font_face = [face for face in font_face.split(' ') if face != 'Regular']
    if font_face:
        font_name = '{}-{}'.format(font_family, ''.join(font_face))
    else:
        font_name = font_family
    for font_idx, base_fn in fig_const.PS_FONT.items():
        base_fn = base_fn.replace('Demi', 'Bold')
        if font_name == base_fn:
            return font_idx
    return fig_const.DEF_PS_FONT
