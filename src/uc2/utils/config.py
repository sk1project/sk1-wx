# -*- coding: utf-8 -*-
#
#	Copyright (C) 2012 by Igor E. Novikov
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


import os, sys

import xml.sax
from xml.sax.xmlreader import InputSource
from xml.sax import handler
from xml.sax.saxutils import XMLGenerator

from uc2.utils.fs import path_system, path_unicode

IDENT = '\t'

def encode_quotes(line):
	result = line.replace('"', '&quot;')
	result = result.replace("'", "&#039;")
	return result

def decode_quotes(line):
	result = line.replace('&quot;', '"')
	result = result.replace("&#039;", "'")
	return result

def escape_quote(line):
	ret=line.replace("\\", "\\\\")
	return ret.replace("'", "\\'")



class XmlConfigParser(object):
	"""
	Represents parent class for application config.
	"""
	filename = ''

	def update(self, cnf={}):
		if cnf:
			for key in cnf.keys():
				if hasattr(self, key):
					setattr(self, key, cnf[key])

	def load(self, filename=None):
		self.filename = filename
		if os.path.lexists(filename):
			content_handler = XMLPrefReader(pref=self)
			error_handler = ErrorHandler()
			entity_resolver = EntityResolver()
			dtd_handler = DTDHandler()
			try:
				input_file = open(filename, "r")
				input_source = InputSource()
				input_source.setByteStream(input_file)
				xml_reader = xml.sax.make_parser()
				xml_reader.setContentHandler(content_handler)
				xml_reader.setErrorHandler(error_handler)
				xml_reader.setEntityResolver(entity_resolver)
				xml_reader.setDTDHandler(dtd_handler)
				xml_reader.parse(input_source)
				input_file.close()
			except:
				print 'ERROR>>> cannot read preferences from %s' % filename
				print sys.exc_info()[1].__str__()
				print sys.exc_info()[2].__str__()

	def save(self, filename=None):
		if self.filename and filename is None: filename = self.filename
		if len(self.__dict__) == 0 or filename == None: return

		try:
			fileobj = open(filename, 'w')
		except:
			print 'ERROR>>> cannot write preferences into %s' % filename
			return

		writer = XMLGenerator(out=fileobj, encoding=self.system_encoding)
		writer.startDocument()
		defaults = XmlConfigParser.__dict__
		items = self.__dict__.items()
		items.sort()
		writer.startElement('preferences', {})
		writer.characters('\n')
		for key, value in items:
			if defaults.has_key(key) and defaults[key] == value: continue
			if key in ['filename', 'app']: continue
			writer.characters('\t')
			writer.startElement('%s' % key, {})

			str_value = path_unicode(value.__str__())
			if isinstance(value, str):
				str_value = "'%s'" % (escape_quote(str_value))

			writer.characters(str_value)

			writer.endElement('%s' % key)
			writer.characters('\n')
		writer.endElement('preferences')
		writer.endDocument()
		fileobj.close

class XMLPrefReader(handler.ContentHandler):
	"""Handler for xml file reading"""
	def __init__(self, pref=None):
		self.key = None
		self.value = None
		self.pref = pref

	def startElement(self, name, attrs):
		self.key = name

	def endElement(self, name):
		if name != 'preferences':
			try:
				line = path_system('self.value=' + self.value)
				code = compile(line, '<string>', 'exec')
				exec code
				self.pref.__dict__[self.key] = self.value
			except Exception:
				print sys.exc_info()[0] + sys.exc_info()[1]


	def characters(self, data):
		self.value = data

class ErrorHandler(handler.ErrorHandler): pass
class EntityResolver(handler.EntityResolver): pass
class DTDHandler(handler.DTDHandler): pass

