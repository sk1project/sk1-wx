#!/usr/bin/env python2
#
# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2013-2016 by Igor E. Novikov
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

import os
import sys
import platform

RESTRICTED = ('UniConvertor', 'Python', 'ImageMagick')

sys.path.insert(1, os.path.abspath('../../uniconvertor/src'))
sys.path.insert(1, os.path.abspath('../../wal/src'))


def get_path_var():
    paths = os.environ["PATH"].split(os.pathsep)
    ret = []
    for path in paths:
        for item in RESTRICTED:
            if item not in path:
                ret.append(path)
    return os.pathsep.join(ret)


if os.name == 'nt':

    cur_path = os.path.abspath('..\\..\\sk1-wx-msw')
    arch = platform.architecture()[0]
    devresdir = 'win64-devres' if arch == '64bit' else 'win32-devres'

    devres = os.path.join(cur_path, devresdir)
    bindir = os.path.join(devres, 'dlls') + os.pathsep
    devres_utf8 = devres.decode(sys.getfilesystemencoding()).encode('utf-8')
    magickdir = os.path.join(devres_utf8, 'dlls', 'modules') + os.pathsep

    os.environ["PATH"] = magickdir + bindir + get_path_var()
    os.environ["MAGICK_CODER_MODULE_PATH"] = magickdir
    os.environ["MAGICK_CODER_FILTER_PATH"] = magickdir
    os.environ["MAGICK_CONFIGURE_PATH"] = magickdir
    os.environ["MAGICK_HOME"] = magickdir

    os.chdir(os.path.join(devres, 'dlls'))

import sk1

sk1.sk1_run()
