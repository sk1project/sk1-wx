# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2016 by Igor E. Novikov
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

from uc2 import utils, cms
from uc2.formats.generic import BinaryModelObject
from uc2.formats.wmf import wmfconst

class  META_Header_Record(BinaryModelObject):

	resolve_name = 'META_Header_Record'

	def __init__(self, chunk=''):
		if chunk: self.chunk = chunk
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

	def update_for_sword(self):
		self.cache_fields = wmfconst.HEADER_MARKUP

class META_Placeable_Record(META_Header_Record):

	resolve_name = 'META_Placeable_Record'

	def update_for_sword(self):
		self.cache_fields = wmfconst.PLACEABLE_MARKUP

class WMF_Record(BinaryModelObject):

	resolve_name = 'Unknown record'
	func = 0

	def __init__(self, chunk):
		self.cache_fields = []
		self.chunk = chunk
		self.func = utils.word2py_int(self.chunk[4:6])
		if self.func in wmfconst.WMF_RECORD_NAMES:
			self.resolve_name = wmfconst.WMF_RECORD_NAMES[self.func]

	def resolve(self, name=''):
		is_leaf = True
		info = '%d' % (len(self.childs))
		return (is_leaf, self.resolve_name, info)

	def save(self, saver):
		saver.write(self.chunk)

	def update_for_sword(self):
		self.cache_fields = [] + wmfconst.GENERIC_FIELDS
		if self.func in wmfconst.RECORD_MARKUPS:
			self.cache_fields += wmfconst.RECORD_MARKUPS[self.func]
