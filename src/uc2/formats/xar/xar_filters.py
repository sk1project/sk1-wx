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

from uc2.formats.generic_filters import AbstractLoader, AbstractSaver
from uc2.formats.xar import xar_const
from uc2.formats.xar.zipio import ZipIO
from uc2.formats.xar.xar_method import make_record_header
from uc2.formats.xar import xar_datatype, xar_model


class XARLoader(AbstractLoader):
    name = 'XAR_Loader'
    parent_stack = None

    def do_load(self):
        stream = raw_stream = self.fileptr

        # read file header
        self.model.chunk = stream.read(8)
        self.model.childs = []
        rec = self.model
        parent_stack = [rec]
        record_idx = 0
        while rec.cid != xar_const.TAG_ENDOFFILE:

            record_idx += 1
            record_cid = xar_datatype.unpack_u4(stream.read(4))
            record_size = xar_datatype.unpack_u4(stream.read(4))

            if record_cid == xar_const.TAG_ENDCOMPRESSION:
                compression_crc = stream.crc32 & 0xffffffff
                num_bytes = stream.bytes
                stream.close()
                stream = raw_stream

            chunk = stream.read(record_size) if record_size else b''
            rec = xar_model.XARRecord(record_cid, record_idx, chunk)

            if rec.cid == xar_const.TAG_STARTCOMPRESSION:
                rec.update()
                if rec.compression_type is 0:
                    stream = ZipIO(raw_stream)
                else:
                    msg = 'Unknown compression type %s' % rec.compression_type
                    raise Exception(msg)
            elif rec.cid == xar_const.TAG_ENDCOMPRESSION:
                rec.update()
                if rec.num_bytes != num_bytes:
                    msg = 'Expected %s bytes (%s given)' % \
                          (rec.num_bytes, stream.bytes)
                    raise Exception(msg)
                if rec.compression_crc != compression_crc:
                    raise Exception('Invalid crc')

            if rec.cid == xar_const.TAG_DOWN:
                parent_rec = parent_stack[-1].childs[-1]
                parent_stack.append(parent_rec)
                parent_stack[-1].add(rec)
            elif rec.cid == xar_const.TAG_UP:
                parent_stack[-1].add(rec)
                parent_stack = parent_stack[:-1]
            else:
                parent_stack[-1].add(rec)


class XARSaver(AbstractSaver):
    name = 'XAR_Saver'

    def do_save(self):
        stream = raw_stream = self.fileptr

        # write file header
        stream.write(self.model.chunk)

        rec = self.model
        stack = rec.childs[::-1]

        while stack:

            rec = stack.pop()

            if rec.cid == xar_const.TAG_STARTCOMPRESSION:
                stream.write(make_record_header(rec))
                stream.write(rec.chunk)
                stream = ZipIO(raw_stream)
                s = rec.childs[::-1]
                stack.extend(s)
                continue
            elif rec.cid == xar_const.TAG_ENDCOMPRESSION:
                stream.write(make_record_header(rec))
                stream.close()
                # TODO: update rec.compression_crc, rec.num_bytes
                stream = stream.raw_stream
                stream.write(rec.chunk)
                continue
            elif rec.childs:
                # stack.append(xar_model.XARRecord(xar_const.TAG_UP))
                stack.extend(rec.childs[::-1])
                # stack.append(xar_model.XARRecord(xar_const.TAG_DOWN))

            stream.write(make_record_header(rec))
            stream.write(rec.chunk)
