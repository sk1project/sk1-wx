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
		loader.seek(0, 2)
		filesize = loader.tell()
		loader.seek(0)
		self.version, self.nbcolors = struct.unpack('>2H', loader.read(4))
		loader.seek(0)
		if self.version == aco_const.ACO1_VER:
			pal = ACO1_Header()
			pal.parse(loader)
			self.childs.append(pal)
			if loader.tell() < filesize:
				pal = ACO2_Header()
				pal.parse(loader)
				self.childs.append(pal)
		else:
			pal = ACO2_Header()
			pal.parse(loader)
			self.childs.append(pal)


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
		self.chunk = loader.read(4)
		self.ncolors = struct.unpack('>H', self.chunk[2:])
		for item in range(self.ncolors):
			color = ACO1_Color()
			color.parse(loader)
			self.childs.append(color)


class ACO1_Color(BinaryModelObject):
	"""
	Represents ACO1 color object.
	"""

	def __init__(self):
		self.childs = []
		self.cache_fields = []

	def parse(self, loader):
		self.chunk = loader.read(10)


class ACO2_Header(ACO1_Header):
	"""
	Represents ACO2 header object.
	"""
	version = aco_const.ACO2_VER
	ncolors = 0

	def __init__(self):
		ACO1_Header.__init__(self)

	def parse(self, loader):
		self.chunk = loader.read(4)
		self.ncolors = struct.unpack('>H', self.chunk[2:])
		for item in range(self.ncolors):
			color = ACO2_Color()
			color.parse(loader)
			self.childs.append(color)

class ACO2_Color(ACO1_Color):
	"""
	Represents ACO2 color object.
	"""

	def __init__(self):
		ACO1_Color.__init__(self)

	def parse(self, loader):
		self.chunk = loader.read(10)
		start = loader.read(4)
		strlen = struct.unpack('>H', start[2:])
		self.chunk += start + loader.read(strlen)



