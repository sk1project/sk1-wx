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
            try:
                record_header = stream.read(xar_const.XAR_RECORD_HEADER_SIZE)
                record_tag = xar_datatype.unpack_u4(record_header)
                record_size = xar_datatype.unpack_u4(record_header, offset=4)
            except Exception:
                self.send_warning('File is corrupted')
                break
            if record_tag == xar_const.TAG_ENDCOMPRESSION:
                compression_crc = stream.crc32 & 0xffffffff
                num_bytes = stream.bytes
                stream.close()
                stream = raw_stream

            record_data = stream.read(record_size) if record_size else b''
            chunk = record_header + record_data
            rec = xar_model.XARRecord(record_tag, record_idx, chunk)

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
                          (rec.num_bytes, num_bytes)
                    self.send_warning(msg)
                if rec.compression_crc != compression_crc:
                    msg = 'Invalid crc'
                    self.send_warning(msg)
            elif rec.cid == xar_const.TAG_DEFINE_DEFAULTUNITS:
                rec.update()
                if rec.page_units == xar_const.REF_UNIT_PIXELS:
                    userscale = self.config.userscale or 1000.0 / 750.0
                    self.config.userscale = userscale

            if rec.cid == xar_const.TAG_DOWN:
                parent_rec = parent_stack[-1].childs[-1]
                parent_stack.append(parent_rec)
                parent_stack[-1].add(rec)
            elif rec.cid == xar_const.TAG_UP:
                if len(parent_stack) == 1:
                    break
                parent_stack[-1].add(rec)
                parent_stack = parent_stack[:-1]
                self.check_loading()
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
                stream.write(rec.chunk[xar_const.XAR_RECORD_HEADER_SIZE:])
                stream = ZipIO(raw_stream)
                stack.extend(rec.childs[::-1])
                continue
            elif rec.cid == xar_const.TAG_ENDCOMPRESSION:
                stream.write(make_record_header(rec))
                stream.close()
                # TODO: update rec.compression_crc, rec.num_bytes
                stream = stream.raw_stream
                stream.write(rec.chunk[xar_const.XAR_RECORD_HEADER_SIZE:])
                continue
            elif rec.childs:
                # stack.append(xar_model.XARRecord(xar_const.TAG_UP))
                stack.extend(rec.childs[::-1])
                # stack.append(xar_model.XARRecord(xar_const.TAG_DOWN))

            stream.write(make_record_header(rec))
            stream.write(rec.chunk[xar_const.XAR_RECORD_HEADER_SIZE:])
