# -*- coding: utf-8 -*-
#
#  Copyright (C) 2017-2019 by Igor E. Novikov
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

from uc2 import utils
from uc2.formats.cgm import cgm_const, cgm_utils
from uc2.formats.generic import BinaryModelObject

parse_header = cgm_utils.parse_header


class CgmMetafile(BinaryModelObject):
    def __init__(self):
        self.childs = []
        self.chunk = ''

    def resolve(self, name=''):
        sz = '%d' % len(self.childs)
        return False, 'CGM_METAFILE', sz


def get_empty_cgm():
    return CgmMetafile()


class CgmElement(BinaryModelObject):
    def __init__(self, command_header, params):
        self.cache_fields = []
        self.command_header = command_header
        self.params = params
        self.chunk = command_header + params
        self.element_class, self.element_id, self.params_sz = parse_header(
            self.command_header)
        self.is_padding = self.params_sz < len(self.params)

    def resolve(self, name=''):
        return True, cgm_const.CGM_ID.get(
            self.element_id, hex(self.element_id)), 0

    def update_for_sword(self):
        cgm_cls_name = cgm_const.CGM_CLS.get(self.element_class, '')
        msg = 'Command Header\n' \
              '  %d - element class\n' \
              '  (%s)\n' \
              '  0x%04x - element id\n' \
              '  %d - parameter list size (bytes)' \
              % (self.element_class, cgm_cls_name,
                 self.element_id, self.params_sz)
        msg += '\n' + '.' * 35
        self.cache_fields = [(0, len(self.command_header), msg), ]

    def do_update(self, presenter=None, action=False):
        BinaryModelObject.do_update(self, presenter, action)
        if action and self.is_padding:
            self.cache_fields.append((len(self.chunk) - 1, 1, 'padding byte'))


class CgmBeginMetafile(CgmElement):
    title_sz = 0
    title = ''

    def __init__(self, command_header, params):
        CgmElement.__init__(self, command_header, params)
        if params:
            self.title_sz = utils.byte2py_int(self.params[0])
            self.title = self.params[1:]

    def update_for_sword(self):
        CgmElement.update_for_sword(self)
        pos = len(self.command_header)
        if self.params:
            self.cache_fields += [(pos, 1, 'text length'),
                                  (pos + 1, self.title_sz, 'file title')]


class CgmMetafileVersion(CgmElement):
    def __init__(self, command_header, params):
        CgmElement.__init__(self, command_header, params)

    def update_for_sword(self):
        CgmElement.update_for_sword(self)
        pos = len(self.command_header)
        if self.params:
            self.cache_fields += [(pos, len(self.params), 'version'), ]


class CgmMetafileDescription(CgmElement):
    def __init__(self, command_header, params):
        CgmElement.__init__(self, command_header, params)
        if params:
            pass

    def update_for_sword(self):
        CgmElement.update_for_sword(self)
        pos = len(self.command_header)
        if self.params:
            self.cache_fields += [(pos, len(self.params), 'version'), ]


ID_TO_CLS = {
    0x0020: CgmBeginMetafile,
    0x1020: CgmMetafileVersion,
    0x1040: CgmMetafileDescription,
}


def element_factory(header, params):
    element_id = parse_header(header)[1]
    return ID_TO_CLS.get(element_id, CgmElement)(header, params)
