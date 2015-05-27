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
from uc2.formats.ase import ase_const


class ASE_Palette(BinaryModelObject):
	"""
	Represents ASE palette object.
	This is a root DOM instance of ASE file format.
	"""

	header = ase_const.ASEF
	version = ase_const.ASE_VER
	nblocs = 0

	def __init__(self):
		self.childs = []
		self.cache_fields = []

	def parse(self, loader):
		self.chunk = loader.readbytes(12)
		self.header = self.chunk[0:4]
		self.version = self.chunk[5:8]
		self.nblocs = struct.unpack('>I', self.chunk[8:12])[0]
		for i in range(self.nblocs):
			obj = ASE_BLOCK()
			self.childs.append(obj)
			obj.parse(loader)

	def update_for_sword(self):
		self.cache_fields.append((0, 4, 'ASE header'))
		self.cache_fields.append((4, 4, 'ASE version'))
		self.cache_fields.append((8, 4, 'number of blocks'))

	def resolve(self, name=''):
		is_leaf = False
		info = '%d' % (len(self.childs))
		name = 'ASE palette'
		return (is_leaf, name, info)

class ASE_BLOCK(BinaryModelObject):
	"""
	Represents ASE block object.
	"""
	identifier = ase_const.ASE_GROUP
	size = 0

	def __init__(self):
		self.childs = []
		self.cache_fields = []

	def parse(self, loader):
		self.identifier = loader.readbytes(2)
		self.size = struct.unpack('>L', loader.readbytes(4))[0]
		loader.fileptr.seek(-6, 1)
		self.chunk = loader.readbytes(6 + self.size)

	def update_for_sword(self):
		self.cache_fields.append((0, 2, 'Block id'))
		self.cache_fields.append((2, 4, 'Block size'))

	def resolve(self, name=''):
		is_leaf = True
		info = '%d' % (len(self.childs))
		name = ase_const.ASE_NAMES[self.identifier]
		return (is_leaf, name, info)
