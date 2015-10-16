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

from uc2 import libcairo

def create_cpath(cache_paths):
	return libcairo.create_cpath(cache_paths)

def copy_cpath(cache_cpath):
	return libcairo.copy_cpath(cache_cpath)

def get_cpath_bbox(cache_cpath):
	return libcairo.get_cpath_bbox(cache_cpath)

def apply_trafo(cache_cpath, trafo):
	return libcairo.apply_trafo(cache_cpath, trafo)

def multiply_trafo(trafo1, trafo2):
	return libcairo.multiply_trafo(trafo1, trafo2)

def invert_trafo(trafo):
	return libcairo.invert_trafo(trafo)

def _get_transformed_path(obj):
	if obj.cache_cpath is None:
		obj.update()
	if obj.cache_cpath is None: return None

	return libcairo.get_path_from_cpath(obj.cache_cpath)
