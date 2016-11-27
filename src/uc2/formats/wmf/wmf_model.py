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
from uc2.formats.wmf.wmfconst import wmf_functions

class WMF_Header(BinaryModelObject):

	resolve_name = 'WMF_Header'

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

	def update_for_save(self):pass

class WMF_Placeble_Header(WMF_Header):

	resolve_name = 'WMF_Placeble_Header'

class WMF_Record(BinaryModelObject):

	resolve_name = 'Unknown record'

	def __init__(self, chunk):
		self.chunk = chunk

	def resolve(self, name=''):
		is_leaf = True
		func = utils.word2py_int(self.chunk[4:6])
		if func in wmf_functions:
			self.resolve_name = wmf_functions[func]
		info = '%d' % (len(self.childs))
		return (is_leaf, self.resolve_name, info)

	def save(self, saver):
		saver.write(self.chunk)
