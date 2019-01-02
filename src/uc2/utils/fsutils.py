# -*- coding: utf-8 -*-
#
#  Copyright (C) 2003-2017 by Igor E. Novikov
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


import errno
import logging
import os

from uc2 import _, events, msgconst
from uc2.utils import system

LOG = logging.getLogger(__name__)

# Platform
IS_MSW = system.get_os_family() == system.WINDOWS
IS_MAC = system.get_os_family() == system.MACOSX

HOME = os.path.expanduser(u'~').encode('utf-8')


def expanduser(path=''):
    if path.startswith('~'):
        path = path.replace('~', HOME)
    return path


def get_sys_path(path):
    return path if isinstance(path, unicode) else path.decode('utf-8')


def get_utf8_path(path):
    return path.encode('utf-8') if isinstance(path, unicode) else path


def isfile(path):
    return os.path.isfile(get_sys_path(path))


def isdir(path):
    return os.path.isdir(get_sys_path(path))


def get_fileptr(path, writable=False):
    if not path:
        msg = _('There is no file path')
        raise IOError(errno.ENODATA, msg, '')
    path = get_sys_path(path)
    if writable:
        try:
            fileptr = open(path, 'wb')
        except Exception:
            msg = _('Cannot open %s file for writing') % path
            events.emit(events.MESSAGES, msgconst.ERROR, msg)
            LOG.error(msg)
            raise
    else:
        try:
            fileptr = open(path, 'rb')
        except Exception:
            msg = _('Cannot open %s file for reading') % path
            events.emit(events.MESSAGES, msgconst.ERROR, msg)
            LOG.error(msg)
            raise
    return fileptr


def makedirs(path):
    os.makedirs(get_sys_path(path))


def lexists(path):
    return os.path.lexists(get_sys_path(path))
