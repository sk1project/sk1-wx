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

import os
import zlib

__all__ = ["ZipIO"]


class ZipIO(object):
    """class ZipIO(stream)

    When a ZipIO object is created, it can be initialized to an existing
    stream by passing the stream to the constructor.
    """
    def __init__(self, raw_stream, wbits=-zlib.MAX_WBITS):
        self.raw_stream = raw_stream
        self.mode = raw_stream.mode
        if self.mode == 'rb':
            self.decompressor = zlib.decompressobj(wbits)
        else:
            self.compressor = zlib.compressobj(-1, zlib.DEFLATED, wbits)
        self.uncompress_buf = b''

    @property
    def crc32(self):
        """ Compute a CRC-32 checksum of uncompress buffer.
        """
        return zlib.crc32(self.uncompress_buf) & 0xffffffff

    @property
    def bytes(self):
        return len(self.uncompress_buf)

    @property
    def buf(self):
        return self.decompressor.unconsumed_tail

    def read(self, n=-1):
        """Read at most size bytes from the stream

        If the size argument is negative or omitted, read all data.
        """
        r = b''

        if n is None or n < 0:
            n = len(self.raw_stream)

        if len(self.buf) > 0:
            r += self.decompressor.decompress(self.buf, n)

        if len(r) != n:
            chunk_size = n
            while len(r) < n:
                chunk = self.raw_stream.read(chunk_size)
                if len(chunk) == 0:
                    r += self.decompressor.flush()
                    del self.decompressor
                    break
                chunk = self.decompressor.decompress(chunk, n - len(r))
                r += chunk

        self.uncompress_buf += r
        return r

    def write(self, s):
        """Write a string to the stream.
        """
        self.uncompress_buf += s
        data = self.compressor.compress(s)
        self.raw_stream.write(data)

    def flush(self):
        """All pending input is processed

        Free the memory compressor.
        """
        if self.mode == 'wb':
            data = self.compressor.flush()
            self.raw_stream.write(data)
            del self.compressor

    def close(self):
        """Free the memory decompressor.
        """
        if self.mode == 'rb':
            unused_data = self.decompressor.unused_data
            self.raw_stream.seek(-len(unused_data), os.SEEK_CUR)
            del self.decompressor
        else:
            self.flush()
