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

from uc2.formats.xar import xar_const, xar_model
from uc2.formats.generic_filters import AbstractBinaryLoader, AbstractSaver

from uc2.formats.xar.zipio import ZipIO
from uc2.formats.xar.xar_datatype import read_u4le


class XARLoader(AbstractBinaryLoader):
    name = 'XAR_Loader'
    parent_stack = None

    def do_load(self):
        self.parse(self.fileptr)

    def parse(self, raw_stream):
        stream = raw_stream

        # read file header
        read_u4le(stream)
        read_u4le(stream)

        rec = self.model
        self.parent_stack = [rec]

        while rec.cid != xar_const.TAG_ENDOFFILE:
            rec = self.parse_record(stream)

            if rec.cid == xar_const.TAG_STARTCOMPRESSION:
                rec.update()
                if rec.compression_type is 0:
                    stream = ZipIO(raw_stream)
                else:
                    msg = 'Unknown compression type %s' % rec.compression_type
                    raise Exception(msg)
                self.parent_stack[-1].add(rec)
                self.parent_stack.append(rec)

            elif rec.cid == xar_const.TAG_ENDCOMPRESSION:
                rec.update()
                if rec.num_bytes != stream.bytes:
                    msg = 'Expected %s bytes (%s given)' % \
                          (rec.num_bytes, stream.bytes)
                    raise Exception(msg)
                if rec.compression_crc != stream.crc32:
                    raise Exception('Invalid crc')
                stream = raw_stream
                self.parent_stack[-1].add(rec)
                self.parent_stack = self.parent_stack[:-1]

            elif rec.cid == xar_const.TAG_DOWN:
                parent_rec = self.parent_stack[-1].childs[-1]
                self.parent_stack.append(parent_rec)
                # self.parent_stack[-1].add(rec)

            elif rec.cid == xar_const.TAG_UP:
                # self.parent_stack[-1].add(rec)
                self.parent_stack = self.parent_stack[:-1]

            else:
                self.parent_stack[-1].add(rec)

    def parse_record(self, stream):
        cid = read_u4le(stream)
        size = read_u4le(stream)
        chunk = b''

        if cid == xar_const.TAG_ENDCOMPRESSION:
            stream.close()
            chunk = stream.raw_stream.read(size)
        elif size > 0:
            chunk = stream.read(size)
            if len(chunk) < size:
                raise IOError("Stream has ended unexpectedly")

        return xar_model.XARRecord(cid, chunk)


class XARSaver(AbstractSaver):
    name = 'XAR_Saver'

    def do_save(self):
        self.model.save(self)
