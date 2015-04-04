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


from uc2.formats.generic import BinaryModelObject
from uc2.formats.cpl import cpl_const


class CPL10_Palette(BinaryModelObject):
	"""
	Represents CPL10 palette object.
	This is a root DOM instance of CPL10 file format.
	All palette colors are members of childs list.
	"""

	version = cpl_const.CPL10
	name = ''
	ncolors = 0

	def __init__(self):
		self.childs = []
		self.cache_fields = []

	def update(self):
		size = len(self.name)
		self.cache_fields.append((0, 2, 'version'))
		self.cache_fields.append((2, 1, 'palette name size'))
		self.cache_fields.append((3, size, 'palette name'))
		self.cache_fields.append((3 + size, 2, 'number of palette colors'))

	def resolve(self, name=''):
		is_leaf = False
		info = '%d' % (len(self.childs))
		name = 'CPL10 Palette'
		return (is_leaf, name, info)

class CPL10_Color(BinaryModelObject):
	"""
	Represents CPL10 palette color object.
	Color values stored in valbytes field.
	"""

	model = 0
	name = ''
	valbytes = ''
	def __init__(self):
		self.cache_fields = []

	def update(self):
		self.cache_fields.append((0, 2, 'color model'))
		self.cache_fields.append((2, 10, 'color values'))
		self.cache_fields.append((12, 1, 'color name size'))
		self.cache_fields.append((13, len(self.name), 'color name'))

	def resolve(self, name=''):
		name = cpl_const.CDR_COLOR_NAMES[self.model]
		return (True, '%s color' % name, '')
