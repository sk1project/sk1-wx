# -*- coding: utf-8 -*-
#
#	Copyright (C) 2015 by Igor E. Novikov
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.

from uc2.formats.sk2 import sk2_const

from flattering import flat_path
from points import distance

def get_path_lenght(path):
	fpath = flat_path(path)
	points = [fpath[0], ] + fpath[1]
	if fpath[2] == sk2_const.CURVE_CLOSED:
		points += [fpath[0], ]
	ret = 0
	start = []
	for item in points:
		if not start:
			start = item
			continue
		ret += distance(start, item)
	return ret

def get_paths_lenght(paths):
	ret = 0
	for item in paths:
		ret += get_path_lenght(item)
	return ret
