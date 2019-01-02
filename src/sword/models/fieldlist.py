# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2012, 2018 by Igor E. Novikov
#
# 	This program is free software: you can redistribute it and/or modify
# 	it under the terms of the GNU General Public License as published by
# 	the Free Software Foundation, either version 3 of the License, or
# 	(at your option) any later version.
#
# 	This program is distributed in the hope that it will be useful,
# 	but WITHOUT ANY WARRANTY; without even the implied warranty of
# 	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# 	GNU General Public License for more details.
#
# 	You should have received a copy of the GNU General Public License
# 	along with this program.  If not, see <https://www.gnu.org/licenses/>.


import gtk

from uc2.formats.generic import GENERIC_TAGS

BIN_FIELDS = ['chunk']
B64_FIELDS = ['bitmap', 'alpha_channel']


def rpr(val):
    if isinstance(val, str) or isinstance(val, unicode):
        return repr(val.encode('utf-8'))
    return repr(val)


def create_repr(value):
    if isinstance(value, list):
        return '[%s]' % ',\n '.join([rpr(val) for val in value])
    elif isinstance(value, tuple):
        return '(%s)' % ',\n '.join([rpr(val) for val in value])
    elif isinstance(value, dict):
        return '{%s}' % ',\n '.join(['%s = %s' % (rpr(key), rpr(val))
                                     for key, val in value.items()])
    else:
        return repr(value)


class FieldListModel(gtk.TreeStore):
    generic_fields = []
    obj_fields = []
    cache_fields = []

    def __init__(self, obj):
        gtk.TreeStore.__init__(self, str, str)

        self.generic_fields = [] + GENERIC_TAGS
        self.obj_fields = []
        self.cache_fields = []

        items = obj.__dict__.items()

        for item in items:
            key, value = item
            if key in GENERIC_TAGS:
                self.generic_fields[GENERIC_TAGS.index(key)] = '_' + key
            elif key.startswith('cache_'):
                self.cache_fields.append(key)
            else:
                self.obj_fields.append(key)

        tmp_generic = []
        for item in self.generic_fields:
            if item[0] == '_':
                tmp_generic.append(item[1:])

        self.generic_fields = [] + tmp_generic
        self.obj_fields.sort()
        self.cache_fields.sort()

        groups = [('Generic fields', self.generic_fields),
                  ('Object fields', self.obj_fields),
                  ('Cache fields', self.cache_fields), ]

        for group in groups:
            if group[1]:
                ptr = self.append(None)
                self.set(ptr, 0, group[0], 1, None)
                for item in group[1]:
                    child_iter = self.append(ptr)
                    key = str(item)
                    value = create_repr(obj.__dict__[item])
                    if key in BIN_FIELDS:
                        if not len(value) == 4 and not \
                                value[:3] in ['CDR', 'CMX']:
                            value = value.encode('hex')
                            if len(value) > 20:
                                value = value[:20] + '...'
                    if key in B64_FIELDS:
                        if len(value) > 50:
                            value = value[:50] + '...'
                    self.set(child_iter, 0, key + ' ', 1, value)
