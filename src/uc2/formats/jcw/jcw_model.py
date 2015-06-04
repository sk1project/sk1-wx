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

from uc2 import utils, cms
from uc2.formats.generic import BinaryModelObject
from uc2.formats.jcw.jcw_const import JCW_ID

class JCW_Palette(BinaryModelObject):

	resolve_name = 'JCW Palette'
	palette_id = JCW_ID
	version = 0
	ncolors = 0
	palette_type = 0
	namesize = 21

	def __init__(self):
		self.childs = []
		self.cache_fields = []

	def parse(self, loader):
		self.palette_id = loader.readbytes(3)
		self.version = loader.readbyte()
		self.ncolors = loader.readword()
		self.palette_type = loader.readbyte()
		self.namesize = loader.readbyte()
		loader.fileptr.seek(0)
		self.chunk = loader.readbytes(8)

	def update_for_sword(self):
		self.cache_fields.append((0, 3, 'palette id'))
		self.cache_fields.append((3, 1, 'palette version'))
		self.cache_fields.append((4, 2, 'number of colors'))
		self.cache_fields.append((6, 1, 'palette type'))
		self.cache_fields.append((7, 1, 'size of color name'))

	def save(self, saver):pass

	def resolve(self, name=''):
		is_leaf = False
		info = '%d' % (len(self.childs))
		return (is_leaf, self.resolve_name, info)
