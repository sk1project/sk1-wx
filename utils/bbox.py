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
import platform

WINDOWS = 'Windows'
LINUX = 'Linux'
MACOS = 'Darwin'

MINT = 'LinuxMint'
UBUNTU = 'Ubuntu'
DEBIAN = 'debian'
FEDORA = 'fedora'
OPENSUSE = 'SuSE'

MARKERS = {
    MINT: 'mint',
    UBUNTU: 'ubuntu',
    DEBIAN: 'debian',
    FEDORA: 'fc',
    OPENSUSE: 'opensuse',
}

TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d")
STDOUT_ENDC = '\033[0m'


class Error(Exception):
    pass


def command(exec_cmd):
    os.system(exec_cmd)


def echo_msg(msg, newline=True, flush=True, code=''):
    if newline:
        msg += '\n'
    if code:
        msg = code + msg + STDOUT_ENDC
    sys.stdout.write(msg)
    if flush:
        sys.stdout.flush()


def is_64bit():
    return platform.architecture()[0] == '64bit'


def is_msw():
    return platform.system() == WINDOWS


def is_linux():
    return platform.system() == LINUX


def is_macos():
    return platform.system() == MACOS


def is_path(pth):
    return os.path.lexists(pth)


def is_deb():
    return platform.dist()[0] in [MINT, UBUNTU, DEBIAN]


def is_debian():
    return platform.dist()[0] == DEBIAN


def is_ubuntu():
    return platform.dist()[0] == UBUNTU


def is_fedora():
    return platform.dist()[0] == FEDORA


def is_opensuse():
    return platform.dist()[0] == OPENSUSE


def is_rpm():
    return platform.dist()[0] in [FEDORA, OPENSUSE]


def is_src():
    return is_deb() and platform.dist()[1] == '16.04' and is_64bit()


def get_marker(timestamp=True):
    if is_deb():
        ver = platform.dist()[1]
        if is_debian():
            ver = ver.split('.')[0]
        mrk = '_%s_%s_' % (MARKERS[platform.dist()[0]], ver)
        if timestamp:
            mrk = '_%s%s' % (TIMESTAMP, mrk)
        return mrk
    elif is_rpm():
        ver = platform.dist()[1].split('.')[0]
        if platform.dist()[0] == OPENSUSE:
            ver = platform.dist()[1]
        mrk = MARKERS[platform.dist()[0]] + ver
        if timestamp:
            mrk = '%s.%s' % (TIMESTAMP, mrk)
        return mrk
    return MARKERS[platform.dist()[0]]


def get_package_name(pth):
    files = []
    file_items = os.listdir(pth)
    for fn in file_items:
        if os.path.isfile(os.path.join(pth, fn)):
            files.append(fn)
    if is_deb():
        if len(files) == 1:
            if files[0].endswith('.deb') or files[0].endswith('.tar.gz'):
                return files[0]
    elif is_rpm():
        for fn in files:
            if fn.endswith('.rpm') and not fn.endswith('src.rpm') \
                    and 'debug' not in fn:
                return fn
    elif is_msw():
        if len(files) == 1:
            if files[0].endswith('.zip') or files[0].endswith('.msi'):
                return files[0]
    raise Error('Build failed! There is no build result.')
