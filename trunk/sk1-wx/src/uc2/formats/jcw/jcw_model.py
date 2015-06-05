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

from uc2 import utils
from uc2.formats.generic import BinaryModelObject
from uc2.formats.jcw.jcw_const import JCW_ID, JCW_NAMESIZE, JCW_COLOR_NAMES, \
JCW_VER, JCW_CMYK
from uc2.formats.jcw.jcw_utils import parse_jcw_color, get_jcw_color

class JCW_Palette(BinaryModelObject):

	resolve_name = 'JCW Palette'
	name = ''
	palette_id = JCW_ID
	version = JCW_VER
	ncolors = 0
	colorspace = 0
	namesize = 21

	def __init__(self, colorspace=JCW_CMYK, namesize=0):
		self.childs = []
		self.cache_fields = []
		if namesize:
			self.colorspace = colorspace
			self.namesize = namesize

	def parse(self, loader):
		self.palette_id = loader.readbytes(3)
		self.version = loader.readbytes(1)
		self.ncolors = loader.readword()
		self.colorspace = loader.readbyte()
		self.namesize = loader.readbyte()
		loader.fileptr.seek(0)
		self.chunk = loader.readbytes(8)
		for i in range(self.ncolors):
			clr = JCW_Color(self.colorspace, self.namesize)
			clr.parse(loader)
			self.childs.append(clr)

	def update_for_sword(self):
		self.cache_fields.append((0, 3, 'palette id'))
		self.cache_fields.append((3, 1, 'palette version'))
		self.cache_fields.append((4, 2, 'number of colors'))
		self.cache_fields.append((6, 1, 'palette colorspace'))
		self.cache_fields.append((7, 1, 'size of color name'))

	def update_for_save(self):
		for child in self.childs: child.update_for_save()
		self.chunk = '' + JCW_ID
		self.chunk += JCW_VER
		self.chunk += utils.py_int2word(len(self.childs))
		self.chunk += utils.py_int2byte(self.colorspace)
		self.chunk += utils.py_int2byte(self.namesize)

	def save(self, saver):
		saver.write(self.chunk)
		for child in self.childs:
			child.save(saver)

	def resolve(self, name=''):
		is_leaf = False
		info = '%d' % (len(self.childs))
		return (is_leaf, self.resolve_name, info)

class JCW_Color(BinaryModelObject):

	valbytes = ''
	name = ''
	namesize = JCW_NAMESIZE
	colorspace = 0

	def __init__(self, colorspace, namesize, color=None):
		self.childs = []
		self.cache_fields = []
		self.colorspace = colorspace
		self.namesize = namesize
		if color:
			self.valbytes = get_jcw_color(color)
			self.name = '' + color[3]

	def parse(self, loader):
		self.chunk = loader.readbytes(8 + self.namesize)
		self.valbytes = self.chunk[0:8]
		self.name = self.chunk[8:].decode('iso-8859-1')

	def update_for_sword(self):
		self.cache_fields.append((0, 8, 'color vals'))
		self.cache_fields.append((8, self.namesize, 'color name'))

	def update_for_save(self):
		self.chunk = ''
		self.chunk += self.valbytes
		self.chunk += self.name.encode('iso-8859-1')
		if len(self.name) < self.namesize:
			self.chunk += '\x00' * (self.namesize - len(self.name))

	def save(self, saver):
		saver.write(self.chunk)

	def resolve(self, name=''):
		name = JCW_COLOR_NAMES[self.colorspace] + ' color'
		return ('True', name, 0)

	def get_color(self):
		clr = parse_jcw_color(self.colorspace, self.valbytes)
		if clr: clr[3] += self.name
		return clr

