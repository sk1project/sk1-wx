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
from uc2.formats.generic import BinaryModelObject
from uc2.formats.xar.xar_datatype import READER_DATA_TYPES_MAP
from uc2.formats.xar.xar_datatype import WRITER_DATA_TYPES_MAP
import logging


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
    _spec = None
    _types = {}

    def __new__(cls, cid, idx, *args, **kwargs):
        new_cls = cls._types.get(cid)
        if new_cls is None:
            spec = xar_const.XAR_TYPE_RECORD.get(cid, {})
            attributedict = {
                '__doc__': spec.get('doc'),
                '_spec': spec.get('sec')
            }
            new_cls = type(b'XARRecord%s' % cid, (XARRecord,), attributedict)
            cls._types[cid] = new_cls
        return BinaryModelObject.__new__(new_cls, cid, idx, *args)

    def __init__(self, cid, idx, chunk=None):
        self.cid = cid
        self.idx = idx
        self.chunk = chunk or b''
        self.childs = []

    def resolve(self):
        xar_record = xar_const.XAR_TYPE_RECORD.get(self.cid, {})
        icon_type = not bool(self.childs)
        if not self._spec and self.chunk:
            icon_type = 'gtk-new' if icon_type else 'gtk-open'
        if xar_record.get('deprecated', False):
            icon_type = 'gtk-media-record'
        name = xar_record.get('name') or str(self.cid)
        info = str(len(self.chunk))
        return icon_type, name, info

    def update_for_sword(self):
        markup = []
        offset = 0
        chunk_length = len(self.chunk)
        for item in self._spec or []:
            reader = READER_DATA_TYPES_MAP.get(item['type'])
            if reader and chunk_length - offset > 0:
                offset2, val = self._deserialize(reader, item, offset)
                markup.append((offset, offset2-offset, item['id']))
                offset = offset2
            else:
                break
        self.cache_fields = markup

    def update(self):
        if self.chunk:
            self.deserialize()
        else:
            self.serialize()

    def serialize(self):
        for item in self._spec or []:
            default = item.get('enum', {}).get('0')  # XXX
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
        for item in self._spec or []:
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
            val = []
            if number < 0:
                number = len(self.chunk[offset:number])
                if item['type'] == 'byte':
                    number /= 1
            for i in range(number):
                size, v = reader(self.chunk, offset=offset, **item)
                offset += size
                val.append(v)
        return offset, val

    def _get_element_number(self, element):
        number = element.get('number', None)
        if number is not None and type(number) not in [int, float]:
            number = getattr(self, number)
        return number
