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


class XARDocument(BinaryModelObject):
    cid = 'signature'
    chunk = xar_const.XAR_SIGNATURE

    def __init__(self, config):
        self.config = config
        self.childs = []

    def resolve(self):
        return False, 'XARDocument', ''


class XARRecord(BinaryModelObject):
    spec = None
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
        if not self._spec:
            icon_type = 'gtk-new' if icon_type else 'gtk-open'

        if xar_record.get('deprecated', False):  # XXX
            raise Exception('deprecated')

        name = xar_record.get('name') or str(self.cid)
        info = str(len(self.chunk))
        return icon_type, name, info

    def update_for_sword(self):
        markup = []
        offset = 0
        for item in self._spec or []:
            reader = READER_DATA_TYPES_MAP.get(item['type'])
            if reader:
                size = reader(self.chunk, offset)[0]
                text = item['id']
                markup.append((offset, size, text))
                offset += size
            else:
                break
        self.cache_fields = markup

    def update(self):
        if self.chunk:
            offset = 0
            for item in self._spec or []:
                reader = READER_DATA_TYPES_MAP.get(item['type'])
                if reader:
                    size, val = reader(self.chunk, offset=offset, **item)
                    setattr(self, item['id'], val)
                    offset += size
                else:
                    break
        else:
            for item in self._spec or []:
                default = item.get('enum', {}).get('0')  # XXX
                data = getattr(self, item['id'], default)
                writer = WRITER_DATA_TYPES_MAP.get(item['type'])
                if writer:
                    self.chunk += writer(data, **item)
                else:
                    break
