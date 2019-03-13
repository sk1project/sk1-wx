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


class CgmFolder(BinaryModelObject):
    cgm_folder_name = ''
    element_id = -1

    def __init__(self):
        self.childs = []
        self.chunk = ''

    def resolve(self, name=''):
        sz = '%d' % len(self.childs)
        return False, self.cgm_folder_name, sz


class CgmMetafile(CgmFolder):
    cgm_folder_name = 'CGM_METAFILE'


class CgmPicture(CgmFolder):
    cgm_folder_name = 'CGM_PICTURE'


def get_empty_cgm():
    return CgmMetafile()


ICONS = {
    cgm_const.BEGIN_METAFILE: 'gtk-media-play',
    cgm_const.BEGIN_PICTURE: 'gtk-goto-bottom',
    cgm_const.BEGIN_PICTURE_BODY: 'gtk-go-down',
    cgm_const.END_PICTURE: 'gtk-goto-top',
    cgm_const.END_METAFILE: 'gtk-media-stop',
    cgm_const.NOOP: 'gtk-no',
}


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
        icon = ICONS.get(self.element_id, True)
        if isinstance(icon, bool):
            icon = 'gtk-new' if cgm_utils.check_status(self.element_id) \
                else icon
        title = cgm_const.CGM_ID.get(self.element_id, hex(self.element_id))
        return icon, title, 0

    def update_for_sword(self):
        self.cache_fields = cgm_utils.get_markup(
            self.command_header, self.params)


class CgmDefReplacement(CgmElement):
    cgm_folder_name = ''

    def __init__(self, command_header, params):
        CgmElement.__init__(self, command_header, params)
        self.childs = []
        self.params = ''
        self.chunk = command_header
        self.cgm_folder_name = cgm_const.CGM_ID[self.element_id]
        self.parse_childs(params)

    def parse_childs(self, chunk):
        while chunk:
            header, chunk = chunk[:2], chunk[2:]
            cls, eid, sz = parse_header(header)
            if sz == 0x1f:
                header += chunk[:2]
                chunk = chunk[2:]
                sz = parse_header(header)[2]
            params, chunk = chunk[:sz], chunk[sz:]
            self.add(CgmElement(header, params))

    def resolve(self, name=''):
        sz = '%d' % len(self.childs)
        return False, self.cgm_folder_name, sz


ID_TO_CLS = {
    cgm_const.METAFILE_DEFAULTS_REPLACEMENT: CgmDefReplacement,
}


def padding(params):
    sz = len(params)
    return params + '\x00' if sz > (sz // 2) * 2 else params


def element_factory(header, params):
    element_id = parse_header(header)[1]
    return ID_TO_CLS.get(element_id, CgmElement)(header, padding(params))
