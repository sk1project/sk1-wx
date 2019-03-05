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

from uc2.formats.xar import xar_const
from uc2.formats.xar import xar_model
from uc2.formats.xar import xar_datatype


def create_new_doc(config):
    doc = xar_model.XARDocument(config)
    return doc


def make_record_header(rec):
    r = xar_datatype.packer_u4le.pack(rec.cid)
    r += xar_datatype.packer_u4le.pack(len(rec.chunk))
    return r


def parse_record(stream):
    record_tag = stream.read(4)
    record_size = stream.read(4)
    cid = xar_datatype.read_u4(record_tag)
    size = xar_datatype.read_u4(record_size)
    chunk = b''
    if cid == xar_const.TAG_ENDCOMPRESSION:
        stream.close()
        chunk += stream.raw_stream.read(size)
    elif size > 0:
        chunk += stream.read(size)
        if len(chunk) < size:
            raise IOError("Stream has ended unexpectedly")
    return xar_model.XARRecord(cid, chunk)
