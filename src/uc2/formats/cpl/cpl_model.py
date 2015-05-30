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

import struct

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
	ncolors = 0

	def __init__(self):
		self.childs = []
		self.cache_fields = []

	def parse(self, loader):
		self.ncolors = loader.readword()
		loader.fileptr.seek(0)
		self.chunk = loader.readbytes(4)
		for i in range(self.ncolors):
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
	ncolors = 0

	def __init__(self):
		self.childs = []
		self.cache_fields = []

	def parse(self, loader):
		size = loader.readbyte()
		self.name = loader.readstr(size)
		self.ncolors = loader.readword()
		loader.fileptr.seek(0)
		self.chunk = loader.readbytes(2 + 1 + size + 2)
		for i in range(self.ncolors):
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
	palette_type = 0
	ncolors = 0


	def __init__(self):
		self.childs = []
		self.cache_fields = []

	def parse(self, loader):
		self.nheaders = loader.readdword()
		chunk_size = 2 + 4
		chunk_size += self.nheaders * 8

		self.headers = {}
		for i in range(self.nheaders):
			hid, offset = loader.read_pair_dword()
			self.headers[hid] = offset

		#Palette name (header 0)
		loader.fileptr.seek(self.headers[0], 0)
		name_size = loader.readbyte()
		self.name = loader.readbytes(name_size * 2).decode('utf_16_le')
		chunk_size += 1 + name_size * 2

		#Palette type (header 1)
		loader.fileptr.seek(self.headers[1], 0)
		self.palette_type = loader.readword()
		chunk_size += 2

		#Number of colors (header 2)
		loader.fileptr.seek(self.headers[2], 0)
		self.ncolors = loader.readword()
		chunk_size += 2

# TODO: data for structural object in the palette end(?)
#		if 3 in self.headers:
#			loader.fileptr.seek(self.headers[3], 0)
#			ninks = loader.readword()
#
#		if 4 in self.headers:
#			loader.fileptr.seek(self.headers[4], 0)
#			size = self.headers[5] - self.headers[4]
#			unknown = loader.readbytes()
#
#		if 5 in self.headers:
#			loader.fileptr.seek(self.headers[5], 0)
#			cols, rows = struct.unpack('<2H', loader.readbytes(4))


		loader.fileptr.seek(0)
		self.chunk = loader.readbytes(chunk_size)

		for i in range(self.ncolors):
			color = CPL12_Color()
			color.parse(loader)
			self.childs.append(color)


	def update_for_sword(self):
		self.cache_fields.append((0, 2, 'version'))
		self.cache_fields.append((2, 4, 'number of headers'))
		size = self.nheaders * 8
		self.cache_fields.append((6, size, 'header offsets'))
		self.cache_fields.append((self.headers[0], 1, 'palette name lenght'))
		size = len(self.name) * 2
		self.cache_fields.append((self.headers[0] + 1, size, 'palette name'))
		self.cache_fields.append((self.headers[1], 2, 'palette type'))
		self.cache_fields.append((self.headers[2], 2, 'number of colors'))


	def resolve(self, name=''):
		is_leaf = False
		info = '%d' % (len(self.childs))
		name = 'CPL12 Palette'
		return (is_leaf, name, info)

class CPL12_Color(CPL7_Color):
	"""
	Represents CPL12 palette color object.
	Color values stored in valbytes field.
	"""
	def __init__(self):
		CPL7_Color.__init__(self)

	def parse(self, loader):
		self.model = loader.readword()
		self.valbytes = loader.readbytes(10)
		size = loader.readbyte()
		self.name = loader.readstr(size * 2).decode('utf_16_le')
		ln = 2 + 10 + 1 + size * 2
		loader.fileptr.seek(-ln, 1)
		self.chunk = loader.readbytes(ln)

	def update_for_sword(self):
		self.cache_fields.append((0, 2, 'color model'))
		self.cache_fields.append((2, 10, 'color values'))
		self.cache_fields.append((12, 1, 'color name size'))
		self.cache_fields.append((13, len(self.name) * 2, 'color name'))
