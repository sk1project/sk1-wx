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

from uc2.formats.generic_filters import AbstractXMLLoader, AbstractSaver
from uc2.formats.xml_.xml_model import XMLObject

class XML_Loader(AbstractXMLLoader):

	name = 'XML_Loader'
	stack = []

	def do_load(self):
		self.stack = []
		self.start_parsing()

	def start_element(self, name, attrs):
		obj = XMLObject()
		obj.tag = name
		if not self.stack: self.model = obj

		for item in attrs._attrs.keys():
			obj.attrs[item] = attrs._attrs[item]

		if self.stack: self.stack[-1].childs.append(obj)
		self.stack.append(obj)

	def element_data(self, data):
		self.stack[-1].content = data

	def end_element(self, name):
		if self.stack and self.stack[-1].tag == name:
			self.stack = self.stack[:-1]

class XML_Saver(AbstractSaver):

	name = 'XML_Saver'
	indent = 0

	def do_save(self):
		self.writeln('<?xml version="1.0"?>')
		self.write_obj(self.model)

	def write_obj(self, obj):pass
