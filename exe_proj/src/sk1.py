#! /usr/bin/python
# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2016 by Igor E. Novikov
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

import os, sys

cur_path = os.getcwd()
_bindir = os.path.join(cur_path, 'dlls')
_magickdir = os.path.join(cur_path, 'dlls', 'modules')

os.environ["PATH"] = _magickdir + os.pathsep + os.environ["PATH"]
os.environ["PATH"] = _bindir + os.pathsep + os.environ["PATH"]
os.environ["MAGICK_CODER_MODULE_PATH"] = _magickdir
os.environ["MAGICK_HOME"] = _magickdir

libs_path = os.path.join(cur_path, 'libs')
sys.path.insert(0, libs_path)

import sk1

sk1.sk1_run()
