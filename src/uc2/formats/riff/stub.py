# -*- coding: utf-8 -*-
#
#  Copyright (C) 2012 by Igor E. Novikov
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
import zlib


class RiffChunk:
    fourcc = '????'
    hdroffset = 0
    rawsize = 0
    data = ''
    contents = []
    fullname = ''
    chunkname = ''
    chunksize = ''
    compression = False
    infocollector = None
    number = 0

    def __init__(self, infocollector=None):
        if infocollector:
            self.infocollector = infocollector
        else:
            self.infocollector = InfoCollector()
            self.infocollector.image = None
            self.infocollector.bitmap = None

    def load_pack(self):
        self.compression = True
        self.infocollector.compression = True
        decomp = zlib.decompressobj()
        self.uncompresseddata = decomp.decompress(self.data[12:])
        chunk = RiffChunk(infocollector=self.infocollector)
        offset = 0
        self.contents = []
        while offset < len(self.uncompresseddata):
            chunk = RiffChunk(infocollector=self.infocollector)
            chunk.parent = self
            chunk.load(self.uncompresseddata, offset)
            self.contents.append(chunk)
            offset += 8 + chunk.rawsize

    def loadcompressed(self):
        if self.data[0:4] != 'cmpr':
            raise Exception("can't happen")
        self.compression = True
        self.infocollector.compression = True
        [compressedsize] = struct.unpack('<I', self.data[4:8])
        [uncompressedsize] = struct.unpack('<I', self.data[8:12])
        [blocksizessize] = struct.unpack('<I', self.data[12:16])

        decomp = zlib.decompressobj()
        self.uncompresseddata = decomp.decompress(self.data[28:])

        blocksizesdata = zlib.decompress(self.data[28 + compressedsize:])
        blocksizes = []
        for i in range(0, len(blocksizesdata), 4):
            blocksizes.append(struct.unpack('<I', blocksizesdata[i:i + 4])[0])
        offset = 0
        self.contents = []
        while offset < len(self.uncompresseddata):
            chunk = RiffChunk(infocollector=self.infocollector)
            chunk.parent = self
            chunk.load(self.uncompresseddata, offset, blocksizes)
            self.contents.append(chunk)
            offset += 8 + chunk.rawsize

    def load(self, buf, offset=0, blocksizes=()):
        self.hdroffset = offset
        self.fourcc = buf[offset:offset + 4]
        self.chunksize = buf[offset + 4:offset + 8]
        [self.rawsize] = struct.unpack('<I', buf[offset + 4:offset + 8])
        if len(blocksizes):
            self.rawsize = blocksizes[self.rawsize]
        self.data = buf[offset + 8:offset + 8 + self.rawsize]
        if self.rawsize & 1:
            self.rawsize += 1
        self.number = self.infocollector.numcount
        self.infocollector.numcount += 1

        self.contents = []
        self.fullname = self.full_name()
        self.chunkname = self.chunk_name()
        if self.fourcc == 'pack':
            self.load_pack()
        if self.fourcc == 'RIFF' or self.fourcc == 'LIST':
            self.listtype = buf[offset + 8:offset + 12]
            self.fullname = self.full_name()
            self.chunkname = self.chunk_name()

            if self.listtype == 'stlt':
                self.chunkname = '<stlt>'
            # pass     # dunno what's up with these, but they're not lists
            elif self.listtype == 'cmpr':
                self.loadcompressed()
            else:
                offset += 12
                while offset < self.hdroffset + 8 + self.rawsize:
                    chunk = RiffChunk(infocollector=self.infocollector)
                    chunk.parent = self
                    chunk.load(buf, offset, blocksizes)
                    self.contents.append(chunk)
                    offset += 8 + chunk.rawsize

    def full_name(self):
        if hasattr(self, 'parent'):
            name = self.parent.fullname + '.'
            if hasattr(self, 'listtype'):
                return name + self.listtype
            return name + self.fourcc
        else:
            return self.fourcc

    def chunk_name(self):
        if self.fourcc == 'RIFF':
            return '<' + self.fourcc + '>'
        if hasattr(self, 'listtype'):
            return '<' + self.listtype + '>'
        return '<' + self.fourcc + '>'
