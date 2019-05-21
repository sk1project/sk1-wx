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

import logging
from uc2.formats.xar import xar_const
from uc2.formats.xar.xar_const import XAR_RECORD_HEADER
from uc2.formats.xar.xar_const import XAR_RECORD_DATA_SPEC

from uc2.formats.generic import BinaryModelObject
from uc2.formats.xar.xar_datatype import READER_DATA_TYPES_MAP
from uc2.formats.xar.xar_datatype import WRITER_DATA_TYPES_MAP


log = logging.getLogger(__name__)


class XARDocument(BinaryModelObject):
    cid = 'signature'
    chunk = xar_const.XAR_SIGNATURE

    def __init__(self, config):
        self.config = config
        self.childs = []

    def resolve(self):
        return False, 'XARDocument', ''


class XARRecord(BinaryModelObject):

    def __init__(self, cid, idx, chunk=None):
        self.cid = cid
        self.idx = idx
        self.chunk = chunk or b''
        self.childs = []

    def _spec(self):
        for sec in XAR_RECORD_HEADER['sec']:
            yield sec
        xar_record = XAR_RECORD_DATA_SPEC.get(self.cid, {})
        for sec in xar_record.get('sec') or []:
            yield sec

    def resolve(self):
        icon_type = not bool(self.childs)
        xar_record = XAR_RECORD_DATA_SPEC.get(self.cid, {})
        spec = xar_record.get('sec') or []
        chunk_length = len(self.chunk)
        if not spec and chunk_length>xar_const.XAR_RECORD_HEADER_SIZE:
            icon_type = 'gtk-new' if icon_type else 'gtk-open'
        if xar_record.get('deprecated', False):
            icon_type = 'gtk-media-record'
        name = xar_record.get('id') or str(self.cid)
        info = str(chunk_length)
        return icon_type, name, info

    def update_for_sword(self):
        markup = []
        offset = 0
        chunk_length = len(self.chunk)
        for item in self._spec():
            reader = READER_DATA_TYPES_MAP.get(item['type'])
            if reader and chunk_length - offset > 0:
                offset2 = self._deserialize(reader, item, offset)[0]
                markup.append((offset, offset2-offset, item['id']))
                offset = offset2
            else:
                break
        self.cache_fields = markup

    def update(self):
        if self.chunk:
            self.deserialize()
        elif self.chunk is None:
            self.serialize()

    def serialize(self):
        for item in self._spec():
            default = item.get('enum', {}).get('0')
            data = getattr(self, item['id'], default)
            writer = WRITER_DATA_TYPES_MAP.get(item['type'])
            if writer:
                self.chunk += writer(data, **item)
            else:
                log.warn('Unknown type %s', item['type'])
                break

    def deserialize(self):
        offset = 0
        chunk_length = len(self.chunk)
        for item in self._spec():
            reader = READER_DATA_TYPES_MAP.get(item['type'])
            if reader:
                if chunk_length - offset > 0:
                    offset, val = self._deserialize(reader, item, offset)
                    setattr(self, item['id'], val)
                else:
                    break
            else:
                log.warn('Unknown type %s', item['type'])
                break

    def _deserialize(self, reader, item, offset):
        number = self._get_element_number(item)
        if number is None:
            size, val = reader(self.chunk, offset=offset, **item)
            offset += size
        else:
            if number < 0:
                number = len(self.chunk[offset:number+1 or None])
                # if item['type'] == 'byte':
                #    number //= 1
            val = []
            for _i in range(number):
                size, val_item = reader(self.chunk, offset=offset, **item)
                offset += size
                val.append(val_item)
        return offset, val

    def _get_element_number(self, element):
        number = element.get('number', None)
        if number is not None and not isinstance(number, (int, float)):
            number = getattr(self, number)
        return number
