#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2013 by Igor E. Novikov
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

import os, platform

if os.name == 'nt':
    cur_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
    if platform.architecture()[0] == '32bit':
        devres = os.path.join(cur_path, 'win32-devres')
        bindir = os.path.join(devres, 'dlls') + os.pathsep
        magickdir = os.path.join(devres, 'dlls', 'modules') + os.pathsep

        os.environ["PATH"] = magickdir + os.environ["PATH"]
        os.environ["PATH"] = bindir + os.environ["PATH"]
        os.environ["MAGICK_CODER_MODULE_PATH"] = magickdir
        os.environ["MAGICK_HOME"] = magickdir

import sk1

sk1.sk1_run()
