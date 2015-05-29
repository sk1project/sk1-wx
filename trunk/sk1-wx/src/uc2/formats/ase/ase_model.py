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
		self.version = self.chunk[4:8]
		self.nblocs = struct.unpack('>I', self.chunk[8:12])[0]
		for i in range(self.nblocs):
			bid = loader.readbytes(2)
			loader.fileptr.seek(-2, 1)
			obj = BID_TO_CLASS[bid]()
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

	def update(self):
		self.nblocs = len(self.childs)
		self.chunk = self.header + self.version
		self.chunk += struct.pack('>I', self.nblocs)

	def save(self, saver):
		saver.write(self.chunk)
		for child in self.childs:
			child.save(saver)

class ASE_Block(BinaryModelObject):
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

	def save(self, saver):
		saver.write(self.chunk)

class ASE_Group(ASE_Block):
	"""
	Represent ASE Group object.
	"""
	identifier = ase_const.ASE_GROUP
	group_name = ''

	def __init__(self, name=''):
		ASE_Block.__init__(self)
		if name: self.group_name = name

	def parse(self, loader):
		ASE_Block.parse(self, loader)
		self.group_name = self.chunk[8:-2].decode('utf_16_be')

	def update_for_sword(self):
		ASE_Block.update_for_sword(self)
		self.cache_fields.append((6, 2, 'Group name size'))
		size = struct.unpack('>H', self.chunk[6:8])[0]
		self.cache_fields.append((8, size * 2, 'Group name'))

	def update(self):
		name_size = len(self.group_name) + 1
		self.chunk = struct.pack('>H', name_size)
		self.chunk += self.group_name.encode('utf_16_be') + '\x00\x00'
		size = len(self.chunk)
		self.chunk = self.identifier + struct.pack('>I', size) + self.chunk

class ASE_Group_End(ASE_Block):
	"""
	Represent ASE Group End object.
	"""
	identifier = ase_const.ASE_GROUP_END

	def __init__(self):
		ASE_Block.__init__(self)

	def update(self):
		self.chunk = self.identifier + struct.pack('>I', 0)

class ASE_Color(ASE_Block):
	"""
	Represent ASE Color object.
	"""
	identifier = ase_const.ASE_COLOR
	color_name = ''
	colorspace = ase_const.ASE_RGB
	color_vals = ()
	color_marker = ase_const.ASE_PROCESS

	def __init__(self, name='', cs=ase_const.ASE_RGB, vals=(0, 0, 0),
				marker=ase_const.ASE_PROCESS):
		ASE_Block.__init__(self)
		if name:
			self.color_name = name
			self.colorspace = cs
			self.color_vals = vals
			self.color_marker = marker

	def parse(self, loader):
		ASE_Block.parse(self, loader)
		size = struct.unpack('>H', self.chunk[6:8])[0]
		pos = 8 + 2 * size
		self.color_name = self.chunk[8:pos - 2].decode('utf_16_be')
		self.colorspace = self.chunk[pos:pos + 4]
		pos += 4
		if self.colorspace in (ase_const.ASE_RGB, ase_const.ASE_LAB) :
			self.color_vals = struct.unpack('>3f', self.chunk[pos:pos + 12])
		elif self.colorspace == ase_const.ASE_CMYK:
			self.color_vals = struct.unpack('>4f', self.chunk[pos:pos + 16])
		elif self.colorspace == ase_const.ASE_GRAY:
			self.color_vals = struct.unpack('>f', self.chunk[pos:pos + 4])
		self.color_marker = self.chunk[-2:]

	def update_for_sword(self):
		ASE_Block.update_for_sword(self)
		self.cache_fields.append((6, 2, 'Color name size'))
		size = struct.unpack('>H', self.chunk[6:8])[0]
		self.cache_fields.append((8, size * 2, 'Color name'))
		pos = 8 + 2 * size
		self.cache_fields.append((pos, 4, 'Colorspace'))
		pos += 4
		if self.colorspace in (ase_const.ASE_RGB, ase_const.ASE_LAB) :
			self.cache_fields.append((pos, 12, 'Color values'))
			pos += 12
		elif self.colorspace == ase_const.ASE_CMYK:
			self.cache_fields.append((pos, 16, 'Color values'))
			pos += 16
		elif self.colorspace == ase_const.ASE_GRAY:
			self.cache_fields.append((pos, 4, 'Color values'))
			pos += 4
		self.cache_fields.append((pos, 2, 'Color marker'))

	def update(self):
		name_size = len(self.color_name) + 1
		self.chunk = struct.pack('>H', name_size)
		self.chunk += self.color_name.encode('utf_16_be') + '\x00\x00'
		self.chunk += self.colorspace
		for item in self.color_vals:
			self.chunk += struct.pack('>f', item)
		self.chunk += self.color_marker
		size = len(self.chunk)
		self.chunk = self.identifier + struct.pack('>I', size) + self.chunk


BID_TO_CLASS = {
ase_const.ASE_GROUP: ASE_Group,
ase_const.ASE_GROUP_END: ASE_Group_End,
ase_const.ASE_COLOR: ASE_Color,
}
