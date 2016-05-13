#! /usr/bin/python
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

RESTRICTED = ('UniConvertor', 'Python', 'ImageMagick')

def get_path_var():
	path = '' + os.environ["PATH"]
	paths = path.split(os.pathsep)
	ret = []
	for path in paths:
		allow = True
		for item in RESTRICTED:
			if item in path: allow = False
		if allow: ret.append(path)
	return os.pathsep.join(ret)


cur_path = os.getcwd()
bindir = os.path.join(cur_path, 'dlls') + os.pathsep
magickdir = os.path.join(cur_path, 'dlls', 'modules') + os.pathsep


os.environ["PATH"] = magickdir + bindir + get_path_var()
os.environ["MAGICK_CODER_MODULE_PATH"] = magickdir
os.environ["MAGICK_CODER_FILTER_PATH"] = magickdir
os.environ["MAGICK_CONFIGURE_PATH"] = magickdir
os.environ["MAGICK_HOME"] = magickdir

libs_path = os.path.join(cur_path, 'libs')
sys.path.insert(0, libs_path)

os.chdir(os.path.join(cur_path, 'dlls'))

import sk1

sk1.sk1_run()
