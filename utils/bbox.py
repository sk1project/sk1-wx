# -*- coding: utf-8 -*-
#
#   BuildBox staff
#
# 	Copyright (C) 2018 by Igor E. Novikov
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
# 	along with this program.  If not, see <http://www.gnu.org/licenses/>.

import datetime
import os
import sys

from .dist import SYSFACTS


TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d")
STDOUT_ENDC = '\033[0m'


class Error(Exception):
    pass


def command(exec_cmd):
    return os.system(exec_cmd)


def echo_msg(msg, newline=True, flush=True, code=''):
    if newline:
        msg += '\n'
    if code:
        msg = code + msg + STDOUT_ENDC
    sys.stdout.write(msg)
    if flush:
        sys.stdout.flush()


def is_path(pth):
    return os.path.lexists(pth)


def get_marker(timestamp=True):
    ver = SYSFACTS.version
    mrk = SYSFACTS.marker
    if SYSFACTS.is_deb:
        if SYSFACTS.is_debian:
            ver = ver.split('.')[0]
        mrk = '_%s_%s_' % (SYSFACTS.marker, ver)
        if timestamp:
            mrk = '_%s%s' % (TIMESTAMP, mrk)
    elif SYSFACTS.is_rpm:
        if not SYSFACTS.is_opensuse and not ver.startswith('42'):
            ver = ver.split('.')[0]
        mrk = SYSFACTS.marker + ver
        if timestamp:
            mrk = '%s.%s' % (TIMESTAMP, mrk)
    return mrk


def get_package_name(pth):
    files = []
    file_items = os.listdir(pth)
    for fn in file_items:
        if os.path.isfile(os.path.join(pth, fn)):
            files.append(fn)
    if SYSFACTS.is_deb:
        if len(files) == 1:
            if files[0].endswith('.deb') or files[0].endswith('.tar.gz'):
                return files[0]
    elif SYSFACTS.is_rpm:
        for fn in files:
            if fn.endswith('.rpm') and not fn.endswith('src.rpm') \
                    and 'debug' not in fn:
                return fn
    elif SYSFACTS.is_msw:
        if len(files) == 1:
            if files[0].endswith('.zip') or files[0].endswith('.msi'):
                return files[0]
    raise Error('Build failed! There is no build result.')
