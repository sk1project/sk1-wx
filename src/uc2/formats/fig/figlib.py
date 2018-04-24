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
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.


def list_chunks(items, size):
    """Yield successive sized chunks from iteml."""
    for i in range(0, len(items), size):
        yield items[i:i + size]


def octal_escape(char):
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
    string = string or ''
    chunks = string.split(' ', len(fmt) - 1)
    for i, f in enumerate(fmt):
        chunk = chunks[i]
        if f == 'i':
            yield int(chunk)
        elif f == 'f':
            yield float(chunk)
        elif f == 's':
            yield str(chunk)
        else:
            yield chunk
