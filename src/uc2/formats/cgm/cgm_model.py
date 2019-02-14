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
        self.cache_fields = cgm_utils.get_markup(
            self.command_header, self.params)


USE_FACTORY = False

ID_TO_CLS = {
}


def element_factory(header, params):
    element_id = parse_header(header)[1]
    return ID_TO_CLS.get(element_id, CgmElement)(header, params) \
        if USE_FACTORY else CgmElement(header, params)
