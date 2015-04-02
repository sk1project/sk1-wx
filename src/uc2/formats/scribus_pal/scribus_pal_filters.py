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
from uc2.formats.scribus_pal.scribus_pal_model import ScribusPalette, SPColor, SPObject

class ScribusPalette_Loader(AbstractXMLLoader):

	name = 'ScribusPalette_Loader'
	stack = []

	def do_load(self):
		self.stack = []
		self.start_parsing()

	def start_element(self, name, attrs):
		if name == ScribusPalette.tag:
			obj = self.model
		elif name == SPColor.tag:
			obj = SPColor()
		else:
			obj = SPObject()
			obj.tag = name

		for item in attrs._attrs.keys():
			obj.__dict__[item] = attrs._attrs[item]

		if self.stack: self.stack[-1].childs.append(obj)
		self.stack.append(obj)

	def end_element(self, name):
		if self.stack and self.stack[-1].tag == name:
			self.stack = self.stack[:-1]

class ScribusPalette_Saver(AbstractSaver):

	name = 'ScribusPalette_Saver'

	def do_save(self):
		self.writeln('<?xml version="1.0" encoding="UTF-8"?>')
		if self.model.comments:
			self.writeln('<!--')
			self.fileptr.write(self.model.comments)
			self.writeln('-->')
		self.writeln('<%s Name="%s" >' % (self.model.tag, self.model.Name))
		for item in self.model.childs:
			self.write_color(item)
		self.writeln('</%s>' % self.model.tag)

	def write_color(self, color):
		line = '\t<%s' % color.tag
		if color.RGB: line += ' RGB="%s"' % color.RGB
		if color.CMYK: line += ' CMYK="%s"' % color.CMYK
		if color.Spot == '1':line += ' Spot="%s"' % color.Spot
		if color.Register == '1':line += ' Register="%s"' % color.Register
		line += ' NAME="%s" />' % color.NAME
		self.writeln(line)

