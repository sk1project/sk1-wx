# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2017 by Igor E. Novikov
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

import struct

from uc2.formats.generic import BinaryModelObject
from uc2.formats.aco import aco_const


class ACO_Palette(BinaryModelObject):
	"""
	Represents ACO palette object.
	This is a root DOM instance of ACO file format.
	"""

	chunk = '\x00'
	version = aco_const.ACO1_VER
	ncolors = 0

	def __init__(self):
		self.childs = []
		self.cache_fields = []

	def parse(self, loader):
		loader.fileptr.seek(0, 2)
		filesize = loader.fileptr.tell()
		loader.fileptr.seek(0)
		self.version, self.nbcolors = struct.unpack('>2H', loader.readbytes(4))
		loader.fileptr.seek(0)
		if self.version == 1:
			pal = ACO1_Header()
			pal.parse(loader)
			self.childs.append(pal)
			if loader.fileptr.tell() < filesize:
				pal = ACO2_Header()
				pal.parse(loader)
				self.childs.append(pal)
		else:
			pal = ACO2_Header()
			pal.parse(loader)
			self.childs.append(pal)

	def resolve(self, name=''):
		is_leaf = False
		info = '%d' % (len(self.childs))
		name = 'ACO palette'
		return (is_leaf, name, info)


class ACO1_Header(BinaryModelObject):
	"""
	Represents ACO1 header object.
	"""
	version = aco_const.ACO1_VER
	ncolors = 0

	def __init__(self):
		self.childs = []
		self.cache_fields = []

	def parse(self, loader):
		self.chunk = loader.readbytes(4)
		self.ncolors = struct.unpack('>H', self.chunk[2:])[0]
		for item in range(self.ncolors):
			color = ACO1_Color()
			color.parse(loader)
			self.childs.append(color)

	def resolve(self, name=''):
		is_leaf = False
		info = '%d' % (len(self.childs))
		name = 'ACO1 header'
		return (is_leaf, name, info)


class ACO1_Color(BinaryModelObject):
	"""
	Represents ACO1 color object.
	"""

	def __init__(self):
		self.childs = []
		self.cache_fields = []

	def parse(self, loader):
		self.chunk = loader.readbytes(10)

	def resolve(self, name=''):
		is_leaf = True
		info = '%d' % (len(self.childs))
		name = 'ACO1 Color'
		return (is_leaf, name, info)


class ACO2_Header(ACO1_Header):
	"""
	Represents ACO2 header object.
	"""
	version = aco_const.ACO2_VER
	ncolors = 0

	def __init__(self):
		ACO1_Header.__init__(self)

	def parse(self, loader):
		self.chunk = loader.readbytes(4)
		self.ncolors = struct.unpack('>H', self.chunk[2:])[0]
		for item in range(self.ncolors):
			color = ACO2_Color()
			color.parse(loader)
			self.childs.append(color)

	def resolve(self, name=''):
		is_leaf = False
		info = '%d' % (len(self.childs))
		name = 'ACO2 header'
		return (is_leaf, name, info)

class ACO2_Color(ACO1_Color):
	"""
	Represents ACO2 color object.
	"""

	def __init__(self):
		ACO1_Color.__init__(self)

	def parse(self, loader):
		self.chunk = loader.readbytes(10)
		start = loader.readbytes(4)
		strlen = struct.unpack('>L', start)[0]
		self.chunk += start + loader.readbytes(strlen * 2)

	def resolve(self, name=''):
		is_leaf = True
		info = '%d' % (len(self.childs))
		name = 'ACO1 Color'
		return (is_leaf, name, info)



