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


class CPL7_Palette(BinaryModelObject):
	"""
	Represents CPL7 palette object (CDR7 version).
	This is a root DOM instance of CPL7 file format.
	All palette colors are members of childs list.
	"""

	version = cpl_const.CPL7
	name = ''

	def __init__(self):
		self.childs = []
		self.cache_fields = []

	def parse(self, loader):
		ncolors = loader.readword()
		loader.fileptr.seek(0)
		self.chunk = loader.readbytes(4)
		for i in range(ncolors):
			color = CPL7_Color()
			color.parse(loader)
			self.childs.append(color)

	def update_for_sword(self):
		size = len(self.name)
		self.cache_fields.append((0, 2, 'version'))
		self.cache_fields.append((2, 2, 'number of palette colors'))

	def resolve(self, name=''):
		is_leaf = False
		info = '%d' % (len(self.childs))
		name = 'CPL7 Palette'
		return (is_leaf, name, info)

class CPL7_Color(BinaryModelObject):
	"""
	Represents CPL7 palette color object.
	Color values stored in valbytes field.
	"""

	model = 0
	name = ''
	valbytes = ''

	def __init__(self):
		self.cache_fields = []

	def parse(self, loader):
		self.model = loader.readword()
		self.valbytes = loader.readbytes(10)
		size = loader.readbyte()
		self.name = loader.readstr(size)
		ln = 2 + 10 + 1 + size
		loader.fileptr.seek(-ln, 1)
		self.chunk = loader.readbytes(ln)

	def update_for_sword(self):
		self.cache_fields.append((0, 2, 'color model'))
		self.cache_fields.append((2, 10, 'color values'))
		self.cache_fields.append((12, 1, 'color name size'))
		self.cache_fields.append((13, len(self.name), 'color name'))

	def resolve(self, name=''):
		name = cpl_const.CDR_COLOR_NAMES[self.model]
		return (True, '%s color' % name, '')


class CPL8_Palette(BinaryModelObject):
	"""
	Represents CPL8 palette object (CDR8-11 versions).
	This is a root DOM instance of CPL8 file format.
	All palette colors are members of childs list.
	"""

	version = cpl_const.CPL8
	name = ''

	def __init__(self):
		self.childs = []
		self.cache_fields = []

	def parse(self, loader):
		size = loader.readbyte()
		self.name = loader.readstr(size)
		ncolors = loader.readword()
		loader.fileptr.seek(0)
		self.chunk = loader.readbytes(2 + 1 + size + 2)
		for i in range(ncolors):
			color = CPL8_Color()
			color.parse(loader)
			self.childs.append(color)

	def update_for_sword(self):
		size = len(self.name)
		self.cache_fields.append((0, 2, 'version'))
		self.cache_fields.append((2, 1, 'palette name size'))
		self.cache_fields.append((3, size, 'palette name'))
		self.cache_fields.append((3 + size, 2, 'number of palette colors'))

	def resolve(self, name=''):
		is_leaf = False
		info = '%d' % (len(self.childs))
		name = 'CPL8 Palette'
		return (is_leaf, name, info)

class CPL8_Color(CPL7_Color):
	"""
	Represents CPL8 palette color object.
	Color values stored in valbytes field.
	"""
	def __init__(self):
		CPL7_Color.__init__(self)


class CPL12_Palette(BinaryModelObject):
	"""
	Represents CPL12 palette object (CDR12-X4 versions).
	This is a root DOM instance of CPL12 file format.
	All palette colors are members of childs list.
	"""

	version = cpl_const.CPL12
	nheaders = 0
	headers = {}
	name = ''

	def __init__(self):
		self.childs = []
		self.cache_fields = []

	def parse(self, loader):
		self.nheaders = loader.readdword()
		self.headers = {}
		for i in range(self.nheaders):
			hid, offset = loader.read_pair_dword()
			self.headers[hid] = offset

		loader.fileptr.seek(0)
		size = self.nheaders * 8
		self.chunk = loader.readbytes(2 + 4 + size)

	def update_for_sword(self):
		self.cache_fields.append((0, 2, 'version'))
		self.cache_fields.append((2, 4, 'number of headers'))
		size = self.nheaders * 8
		self.cache_fields.append((6, size, 'header offsets'))

	def resolve(self, name=''):
		is_leaf = False
		info = '%d' % (len(self.childs))
		name = 'CPL12 Palette'
		return (is_leaf, name, info)
