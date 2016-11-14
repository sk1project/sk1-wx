# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2015-2016 by Igor E. Novikov
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

from uc2.formats.generic_filters import AbstractXMLLoader, AbstractSaver
from uc2.formats.xml_.xml_model import XMLObject, XmlContentText

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
			obj.attrs[item] = attrs._attrs[item].strip()

		if self.stack: self.stack[-1].childs.append(obj)
		self.stack.append(obj)

	def element_data(self, data):
		if self.stack[-1].childs and self.stack[-1].childs[-1].is_content():
			self.stack[-1].childs[-1].text += data
		else:
			obj = XmlContentText(data)
			if self.stack: self.stack[-1].childs.append(obj)

	def end_element(self, name):
		if self.stack and self.stack[-1].tag == name:
			self.stack = self.stack[:-1]

class XML_Saver(AbstractSaver):

	name = 'XML_Saver'

	def do_save(self):
		cfg = self.model.config.encoding
		self.writeln('<?xml version="1.0" encoding="%s"?>' % cfg)
		appdata = self.presenter.appdata
		name = "Created with %s" % appdata.app_name
		ver = "%s%s" % (appdata.version, appdata.revision)
		link = "(http://%s/)" % appdata.app_domain
		self.writeln("<!-- %s %s %s -->" % (name, ver, link))
		self.write_obj(self.model)

	def write_obj(self, obj):
		if obj.comments:
			self.writeln('<!--')
			self.writeln(obj.comments)
			self.writeln('-->')

		if obj.tag == 'content_text':
			self.write(obj.text)
			return
		attrs = self.get_obj_attrs(obj)
		if obj.childs:
			start = '<%s%s>' % (obj.tag, attrs)
			self.write(start)
			for child in obj.childs: self.write_obj(child)
			self.write('</%s>' % obj.tag)
		else:
			self.write('<%s%s />' % (obj.tag, attrs))

	def get_obj_attrs(self, obj):
		line = ''
		if not obj.attrs:return line
		for item in obj.attrs.keys():
			line += ' %s="%s"' % (item, obj.attrs[item])
		return line


