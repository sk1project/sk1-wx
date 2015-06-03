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
from uc2.formats.cdr import cdr_const, cdr_utils

class AbstractCPLPalette(BinaryModelObject):

	resolve_name = 'CPL Palette'

	def __init__(self):
		self.childs = []
		self.cache_fields = []

	def resolve(self, name=''):
		is_leaf = False
		info = '%d' % (len(self.childs))
		return (is_leaf, self.resolve_name, info)

	def save(self, saver):
		saver.write(self.chunk)
		for child in self.childs:
			child.save(saver)

class AbstractCPLColor(BinaryModelObject):

	def __init__(self):
		self.cache_fields = []

	def resolve(self, name=''):
		name = cdr_const.CDR_COLOR_NAMES[self.colorspace]
		return (True, '%s color' % name, '')

	def save(self, saver):
		saver.write(self.chunk)

	def get_color(self):
		clr = cdr_utils.parse_cdr_color(self.colorspace, self.valbytes[-4:])
		if clr and not self.colorspace == cdr_const.CDR_COLOR_REGISTRATION:
			clr[3] += self.name
		return clr

class CPL7_Palette(AbstractCPLPalette):
	"""
	Represents CPL7 palette object (CDR7 version).
	This is a root DOM instance of CPL7 file format.
	All palette colors are members of childs list.
	"""
	resolve_name = 'CPL7 Palette'
	version = cpl_const.CPL7
	name = ''
	ncolors = 0

	def __init__(self):
		AbstractCPLPalette.__init__(self)

	def parse(self, loader):
		self.ncolors = loader.readword()
		loader.fileptr.seek(0)
		self.chunk = loader.readbytes(4)
		self.parse_colors(loader)

	def parse_colors(self, loader):
		for i in range(self.ncolors):
			color = CPL7_Color()
			color.parse(loader)
			self.childs.append(color)

	def update_for_sword(self):
		self.cache_fields.append((0, 2, 'version'))
		self.cache_fields.append((2, 2, 'number of palette colors'))

class CPL7_Color(AbstractCPLColor):
	"""
	Represents CPL7 palette color object.
	Color values stored in valbytes field.
	"""

	colorspace = 0
	name = ''
	valbytes = ''

	def __init__(self):
		AbstractCPLColor.__init__(self)

	def parse(self, loader):
		self.colorspace = loader.readword()
		self.valbytes = loader.readbytes(10)
		size = loader.readbyte()
		self.name = loader.readstr(size).decode('latin1')
		ln = 2 + 10 + 1 + size
		loader.fileptr.seek(-ln, 1)
		self.chunk = loader.readbytes(ln)

	def update_for_sword(self):
		self.cache_fields.append((0, 2, 'colorspace'))
		self.cache_fields.append((2, 10, 'color values'))
		self.cache_fields.append((12, 1, 'color name size'))
		self.cache_fields.append((13, len(self.name), 'color name'))

class CPL7_PaletteUTF(CPL7_Palette):
	"""
	Represents CPL7 UTF palette object (found in CDR12 version).
	This is a root DOM instance of CPL7 file format.
	All palette colors are members of childs list.
	"""
	resolve_name = 'CPL7 UTF Palette'
	version = cpl_const.CPL7_UTF

	def __init__(self):
		CPL7_Palette.__init__(self)

	def parse_colors(self, loader):
		for i in range(self.ncolors):
			color = CPL7_ColorUTF()
			color.parse(loader)
			self.childs.append(color)

class CPL7_ColorUTF(AbstractCPLColor):
	"""
	Represents CPL7 UTF palette color object.
	Color values stored in valbytes field.
	"""

	colorspace = 0
	name = ''
	valbytes = ''

	def __init__(self):
		AbstractCPLColor.__init__(self)

	def parse(self, loader):
		self.colorspace = loader.readword()
		self.valbytes = loader.readbytes(10)
		size = loader.readbyte()
		self.name = loader.readstr(size * 2).decode('utf_16_le')
		ln = 2 + 10 + 1 + size * 2
		loader.fileptr.seek(-ln, 1)
		self.chunk = loader.readbytes(ln)

	def update_for_sword(self):
		self.cache_fields.append((0, 2, 'colorspace'))
		self.cache_fields.append((2, 10, 'color values'))
		self.cache_fields.append((12, 1, 'color name size'))
		self.cache_fields.append((13, len(self.name) * 2, 'color name'))


class CPL8_Palette(AbstractCPLPalette):
	"""
	Represents CPL8 palette object (CDR8-11 versions).
	This is a root DOM instance of CPL8 file format.
	All palette colors are members of childs list.
	"""
	resolve_name = 'CPL8 Palette'
	version = cpl_const.CPL8
	name = ''
	ncolors = 0

	def __init__(self):
		AbstractCPLPalette.__init__(self)

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

class CPL8_Color(CPL7_Color):
	"""
	Represents CPL8 palette color object.
	Color values stored in valbytes field.
	"""
	def __init__(self):
		CPL7_Color.__init__(self)

class CPL10_Palette(AbstractCPLPalette):
	"""
	Represents CPL10 palette object (some palettes from CDR10 version).
	This is a root DOM instance of CPL10 file format.
	All palette colors are members of childs list.
	"""
	resolve_name = 'CPL10 Palette'
	version = cpl_const.CPL10
	nheaders = 0
	headers = {}
	name = ''
	palette_type = 0
	ncolors = 0


	def __init__(self):
		AbstractCPLPalette.__init__(self)

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
		self.name = loader.readbytes(name_size).decode('latin1')
		chunk_size += 1 + name_size

		#Palette type (header 1)
		loader.fileptr.seek(self.headers[1], 0)
		self.palette_type = loader.readword()
		chunk_size += 2

		#Number of colors (header 2)
		loader.fileptr.seek(self.headers[2], 0)
		self.ncolors = loader.readword()
		chunk_size += 2

		loader.fileptr.seek(0)
		self.chunk = loader.readbytes(chunk_size)

		if self.palette_type < 38 and not self.palette_type  in (5, 16):
			color_class = CPL10_SpotColor
		else:
			color_class = CPL10_Color

		for i in range(self.ncolors):
			color = color_class()
			color.parse(loader)
			self.childs.append(color)

	def update_for_sword(self):
		self.cache_fields.append((0, 2, 'version'))
		self.cache_fields.append((2, 4, 'number of headers'))
		size = self.nheaders * 8
		self.cache_fields.append((6, size, 'header offsets'))
		self.cache_fields.append((self.headers[0], 1, 'palette name lenght'))
		size = len(self.name)
		self.cache_fields.append((self.headers[0] + 1, size, 'palette name'))
		self.cache_fields.append((self.headers[1], 2, 'palette type'))
		self.cache_fields.append((self.headers[2], 2, 'number of colors'))

class CPL10_Color(CPL7_Color):
	"""
	Represents CPL10 palette color object.
	Color values stored in valbytes field.
	"""

	def __init__(self):
		CPL7_Color.__init__(self)

class CPL10_SpotColor(CPL7_Color):
	"""
	Represents CPL10 palette SPOT color object.
	Color values stored in valbytes and valbytes2 field.
	"""
	color_id = 0
	colorspace2 = 0
	valbytes2 = ''

	def __init__(self):
		CPL7_Color.__init__(self)

	def parse(self, loader):
		self.color_id = loader.readdword()
		self.colorspace = loader.readword()
		self.valbytes = loader.readbytes(10)
		self.colorspace2 = loader.readword()
		self.valbytes2 = loader.readbytes(10)
		size = loader.readbyte()
		self.name = loader.readstr(size)
		ln = 4 + 2 + 10 + 2 + 10 + 1 + size
		loader.fileptr.seek(-ln, 1)
		self.chunk = loader.readbytes(ln)

	def update_for_sword(self):
		self.cache_fields.append((0, 4, 'color id'))
		self.cache_fields.append((4, 2, 'colorspace'))
		self.cache_fields.append((6, 10, 'color values'))
		self.cache_fields.append((16, 2, 'colorspace2'))
		self.cache_fields.append((18, 10, 'color values2'))
		self.cache_fields.append((28, 1, 'color name size'))
		self.cache_fields.append((29, len(self.name), 'color name'))

	def resolve(self, name=''):
		return (True, 'SPOT color', '')

	def get_color(self):
		cs = self.colorspace
		vals = self.valbytes[-4:]
		cs2 = self.colorspace2
		vals2 = self.valbytes2[-4:]
		clr = cdr_utils.parse_cdr_spot_color(cs, vals, cs2, vals2)
		if clr: clr[3] += self.name
		return clr


class CPL12_Palette(AbstractCPLPalette):
	"""
	Represents CPL12 palette object (CDR12-X4 versions).
	This is a root DOM instance of CPL12 file format.
	All palette colors are members of childs list.
	"""
	resolve_name = 'CPL12 Palette'
	version = cpl_const.CPL12
	nheaders = 0
	headers = {}
	name = ''
	palette_type = 0
	ncolors = 0


	def __init__(self):
		AbstractCPLPalette.__init__(self)

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

		loader.fileptr.seek(0)
		self.chunk = loader.readbytes(chunk_size)

		self.parse_colors(loader)

	def	parse_colors(self, loader):
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

class CPL12_Color(CPL7_Color):
	"""
	Represents CPL12 palette color object.
	Color values stored in valbytes field.
	"""
	def __init__(self):
		CPL7_Color.__init__(self)

	def parse(self, loader):
		self.colorspace = loader.readword()
		self.valbytes = loader.readbytes(10)
		size = loader.readbyte()
		self.name = loader.readstr(size * 2).decode('utf_16_le')
		ln = 2 + 10 + 1 + size * 2
		loader.fileptr.seek(-ln, 1)
		self.chunk = loader.readbytes(ln)

	def update_for_sword(self):
		self.cache_fields.append((0, 2, 'colorspace'))
		self.cache_fields.append((2, 10, 'color values'))
		self.cache_fields.append((12, 1, 'color name size'))
		self.cache_fields.append((13, len(self.name) * 2, 'color name'))

class CPL12_SpotPalette(CPL12_Palette):
	"""
	Represents CPL12 SOPT palette object (CDR12-X4 versions).
	This is a root DOM instance of CPL12 file format.
	All palette colors are members of childs list.
	"""
	resolve_name = 'CPL12 SPOT Palette'
	version = cpl_const.CPL12_SPOT

	def __init__(self):
		CPL12_Palette.__init__(self)

	def parse_colors(self, loader):
		if self.palette_type < 38 and not self.palette_type  in (5, 16):
			color_class = CPL12_SpotColor
		else:
			color_class = CPL12_Color

		for i in range(self.ncolors):
			color = color_class()
			color.parse(loader)
			self.childs.append(color)

class CPL12_SpotColor(CPL10_SpotColor):
	"""
	Represents CPL12 palette SPOT color object.
	Color values stored in valbytes and valbytes2 field.
	"""

	def __init__(self):
		CPL10_SpotColor.__init__(self)

	def parse(self, loader):
		self.color_id = loader.readdword()
		self.colorspace = loader.readword()
		self.valbytes = loader.readbytes(10)
		self.colorspace2 = loader.readword()
		self.valbytes2 = loader.readbytes(10)
		size = loader.readbyte()
		self.name = loader.readstr(size * 2).decode('utf_16_le')
		ln = 4 + 2 + 10 + 2 + 10 + 1 + size * 2
		loader.fileptr.seek(-ln, 1)
		self.chunk = loader.readbytes(ln)

	def update_for_sword(self):
		self.cache_fields.append((0, 4, 'color id'))
		self.cache_fields.append((4, 2, 'colorspace'))
		self.cache_fields.append((6, 10, 'color values'))
		self.cache_fields.append((16, 2, 'colorspace2'))
		self.cache_fields.append((18, 10, 'color values2'))
		self.cache_fields.append((28, 1, 'color name size'))
		self.cache_fields.append((29, len(self.name) * 2, 'color name'))

class CPLX4_SpotPalette(AbstractCPLPalette):
	"""
	Represents CPLX4 palette object ( SPOT palette from CDRX4 versions).
	This is a root DOM instance of CPLX4 file format.
	All palette colors are members of childs list.
	"""
	resolve_name = 'CPLX4 SPOT Palette'
	version = cpl_const.CPLX4_SPOT
	nheaders = 0
	headers = {}
	name = ''
	palette_type = 0
	ncolors = 0
	ninks = 0
	colorspaces = ''
	cols = 0
	rows = 0

	def __init__(self):
		AbstractCPLPalette.__init__(self)

	def parse(self, loader):
		self.nheaders = loader.readdword()

		self.headers = {}
		for i in range(self.nheaders):
			hid, offset = loader.read_pair_dword()
			self.headers[hid] = offset

		#Palette name (header 0)
		loader.fileptr.seek(self.headers[0], 0)
		name_size = loader.readbyte()
		self.name = loader.readbytes(name_size * 2).decode('utf_16_le')

		#Palette type (header 1)
		loader.fileptr.seek(self.headers[1], 0)
		self.palette_type = loader.readword()

		#Number of colors (header 2)
		loader.fileptr.seek(self.headers[2], 0)
		self.ncolors = loader.readword()

		if 3 in self.headers:
			loader.fileptr.seek(self.headers[3], 0)
			self.ninks = loader.readword()

		if 4 in self.headers:
			loader.fileptr.seek(self.headers[4], 0)
			self.colorspaces = loader.readbytes(4)

		if 5 in self.headers:
			loader.fileptr.seek(self.headers[5], 0)
			self.cols = loader.readword()
			self.rows = loader.readword()

		loader.fileptr.seek(0)
		self.chunk = loader.readbytes(self.headers[2] + 2)

		self.parse_colors(loader)

	def	parse_colors(self, loader):
		for i in range(self.ncolors):
			color = CPLX4_SpotColor()
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
		if 3 in self.headers:
			self.cache_fields.append((self.headers[3], 2, 'number of inks'))
		if 4 in self.headers:
			self.cache_fields.append((self.headers[4], 4, 'colorspaces'))

class CPLX4_SpotColor(CPL12_SpotColor):
	"""
	Represents CPLX4 palette color object.
	Color values stored in valbytes and valbytes2 field.
	"""
	row = 0
	col = 0
	version = 0

	def __init__(self):
		CPL12_SpotColor.__init__(self)

	def parse(self, loader):
		CPL12_SpotColor.parse(self, loader)
		self.row = loader.readdword()
		self.col = loader.readdword()
		self.version = loader.readdword()
		loader.fileptr.seek(-12, 1)
		self.chunk += loader.readbytes(12)

	def update_for_sword(self):
		CPL12_SpotColor.update_for_sword(self)
		pos = 29 + len(self.name) * 2
		self.cache_fields.append((pos, 4, 'row number'))
		self.cache_fields.append((pos + 4, 4, 'column number'))
		self.cache_fields.append((pos + 8, 4, 'version'))
