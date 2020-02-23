# -*- coding: utf-8 -*-
#
#  Copyright (C) 2013-2017 by Ihor E. Novikov
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

import os

import wal
from sk1 import _
from uc2 import uc2const


def _get_open_filters(items=None):
    items = items or []
    wildcard = ''
    descr = uc2const.FORMAT_DESCRIPTION
    ext = uc2const.FORMAT_EXTENSION
    if not items:
        items = [] + uc2const.LOADER_FORMATS
    wildcard += _('All supported formats') + '|'
    for item in items:
        for extension in ext[item]:
            wildcard += '*.' + extension + ';'
            wildcard += '*.' + extension.upper() + ';'
    if wal.IS_MAC:
        return wildcard

    wildcard += '|'

    wildcard += _('All files (*.*)') + '|'
    wildcard += '*;*.*|'

    for item in items:
        wildcard += descr[item] + '|'
        for extension in ext[item]:
            wildcard += '*.' + extension + ';'
            wildcard += '*.' + extension.upper() + ';'
        if not item == items[-1]:
            wildcard += '|'

    return wildcard


def get_open_file_name(parent, default_dir, title='', file_types=None):
    file_types = file_types or []
    wildcard = _get_open_filters(file_types)
    return wal.get_open_file_name(parent, title, default_dir, wildcard)


def _get_save_fiters(items=None):
    items = items or []
    wildcard = ''
    descr = uc2const.FORMAT_DESCRIPTION
    ext = uc2const.FORMAT_EXTENSION
    if not items:
        items = [uc2const.SK2]
    for item in items:
        wildcard += descr[item] + '|'
        for extension in ext[item]:
            wildcard += '*.' + extension + ';'
            wildcard += '*.' + extension.upper() + ';'
        if not item == items[-1]:
            wildcard += '|'
    return wildcard


def get_save_file_name(parent, path, title='',
                       file_types=None, path_only=False):
    file_types = file_types or []
    wildcard = _get_save_fiters(file_types)
    ret = wal.get_save_file_name(parent, path, title, wildcard)
    if ret is not None:
        if path_only:
            path = ret[0]
            if not file_types:
                ext = uc2const.FORMAT_EXTENSION[uc2const.SK2][0]
            else:
                ext = uc2const.FORMAT_EXTENSION[file_types[ret[1]]][0]
            ret = os.path.splitext(path)[0] + '.' + ext
    return ret


def get_dir_path(parent, path='~', title=''):
    title = title or _('Select directory')
    return wal.get_dir_path(parent, path, title)
