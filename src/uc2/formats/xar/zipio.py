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

PREREAD_BUFFER_SIZE = 0xFFFF


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
        self.bytes = 0
        self.crc32 = 0

    def _update_statistics(self, s):
        """Updates the amount of uncompressed data processed and the checksum
        """
        self.bytes += len(s)
        self.crc32 = zlib.crc32(s, self.crc32)

    def read(self, n=-1):
        """Read at most size bytes from the stream

        If the size argument is negative or omitted, read all data.
        """
        r = b''

        if n is None or n < 0:
            n = len(self.raw_stream)

        unconsumed_tail = self.decompressor.unconsumed_tail
        if len(unconsumed_tail) > 0:
            r += self.decompressor.decompress(unconsumed_tail, n)

        if len(r) != n:
            while len(r) < n:
                chunk = self.raw_stream.read(PREREAD_BUFFER_SIZE)
                if len(chunk) == 0:
                    r += self.decompressor.flush()
                    del self.decompressor
                    break
                chunk = self.decompressor.decompress(chunk, n - len(r))
                r += chunk

        self._update_statistics(r)
        return r

    def tell(self):
        """Return the stream's file pointer position.
        """
        return self.raw_stream.tell()

    def write(self, s):
        """Write a bites to the stream.
        """
        self._update_statistics(s)
        data = self.compressor.compress(s)
        self.raw_stream.write(data)

    def flush(self):
        """All pending data is processed
        """
        if self.mode == 'rb':
            unused_data = self.decompressor.unused_data
            self.raw_stream.seek(-len(unused_data), os.SEEK_CUR)
        else:
            data = self.compressor.flush()
            self.raw_stream.write(data)

    def close(self):
        """Free the memory compressor/decompressor.
        """
        self.flush()
        if self.mode == 'rb':
            del self.decompressor
        else:
            del self.compressor
