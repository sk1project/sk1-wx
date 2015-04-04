# -*- coding: utf-8 -*-
#
#	Copyright (C) 2013 by Igor E. Novikov
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

import sys, os, errno

from uc2 import _, events, msgconst, utils
import xml.sax
from xml.sax.xmlreader import InputSource
from xml.sax import handler

def get_fileptr(path, writable=False):
	fileptr = None
	if not file:
		msg = _('There is no file path')
		raise IOError(errno.ENODATA, msg, '')
	if writable:
		try:
			fileptr = open(path, 'wb')
		except:
			errtype, value, traceback = sys.exc_info()
			msg = _('Cannot open %s file for writing') % (path)
			events.emit(events.MESSAGES, msgconst.ERROR, msg)
			raise IOError(errtype, msg + '\n' + value, traceback)
	else:
		try:
			fileptr = open(path, 'rb')
		except:
			errtype, value, traceback = sys.exc_info()
			msg = _('Cannot open %s file for reading') % (path)
			events.emit(events.MESSAGES, msgconst.ERROR, msg)
			raise IOError(errtype, msg + '\n' + value, traceback)
	return fileptr

class AbstractLoader(object):
	name = 'Abstract Loader'

	presenter = None
	config = None
	model = None

	filepath = ''
	fileptr = None
	position = 0
	file_size = 0

	def __init__(self):pass

	def load(self, presenter, path=None, fileptr=None):
		self.presenter = presenter
		self.model = presenter.model
		self.config = self.presenter.config
		if path:
			self.filepath = path
			self.file_size = os.path.getsize(path)
			self.fileptr = get_fileptr(path)
		elif fileptr:
			self.fileptr = fileptr
			self.fileptr.seek(0, 2)
			self.file_size = self.fileptr.tell()
			self.fileptr.seek(0)
		else:
			msg = _('There is no file for reading')
			raise IOError(errno.ENODATA, msg, '')

		self.init_load()

		self.fileptr.close()
		self.position = 0
		return self.model

	def init_load(self):
		self.do_load()

	def do_load(self):pass

	def readln(self, strip=True):
		line = self.fileptr.readline()
		if strip:line = line.strip()
		return line

	def check_loading(self):
		position = float(self.fileptr.tell()) / float(self.file_size) * 0.95
		if position - self.position > 0.02:
			self.position = position
			self.parsing_msg(position)

	def send_progress_message(self, msg, val):
		events.emit(events.FILTER_INFO, msg, val)

	def parsing_msg(self, val):
		msg = _('Parsing in progress...')
		self.send_progress_message(msg, val)

	def send_ok(self, msg):
		events.emit(events.MESSAGES, msgconst.OK, msg)

	def send_info(self, msg):
		events.emit(events.MESSAGES, msgconst.INFO, msg)

	def send_warning(self, msg):
		events.emit(events.MESSAGES, msgconst.WARNING, msg)

	def send_error(self, msg):
		events.emit(events.MESSAGES, msgconst.ERROR, msg)

class AbstractBinaryLoader(AbstractLoader):

	def readbytes(self, size):
		return self.fileptr.read(size)

	def readbyte(self):
		return utils.byte2py_int(self.fileptr.read(1))

	def readword(self):
		return utils.word2py_int(self.fileptr.read(2))

	def readstr(self, size):
		return utils.latin1_bytes_2str(self.fileptr.read(size))

	def readustr(self, size):
		return utils.utf_16_le_bytes_2str(self.fileptr.read(size * 2))


class ErrorHandler(handler.ErrorHandler): pass
class EntityResolver(handler.EntityResolver): pass
class DTDHandler(handler.DTDHandler): pass

class AbstractXMLLoader(AbstractLoader, handler.ContentHandler):

	xml_reader = None
	input_source = None

	def init_load(self):
		self.input_source = InputSource()
		self.input_source.setByteStream(self.fileptr)
		self.xml_reader = xml.sax.make_parser()
		self.xml_reader.setContentHandler(self)
		self.xml_reader.setErrorHandler(ErrorHandler())
		self.xml_reader.setEntityResolver(EntityResolver())
		self.xml_reader.setDTDHandler(DTDHandler())
		self.do_load()

	def start_parsing(self):
		self.xml_reader.parse(self.input_source)

	def startElement(self, name, attrs):
		self.start_element(name, attrs)

	def endElement(self, name):
		self.end_element(name)

	def characters(self, data):
		self.element_data(data)

	def start_element(self, name, attrs):pass
	def end_element(self, name):pass
	def element_data(self, data):pass

class AbstractSaver(object):

	name = 'Abstract Saver'

	presenter = None
	config = None

	filepath = ''
	fileptr = None
	position = 0
	file_size = 0

	model = None

	def __init__(self):pass

	def save(self, presenter, path=None, fileptr=None):
		self.presenter = presenter
		self.model = presenter.model
		if path:
			self.fileptr = get_fileptr(path, True)
		elif fileptr:
			self.fileptr = fileptr
		else:
			msg = _('There is no file for writting')
			raise IOError(errno.ENODATA, msg, '')

		self.presenter.update()
		self.do_save()
		self.fileptr.close()
		self.fileptr = None

	def do_save(self):pass

	def writeln(self, line):
		self.fileptr.write(line + '\n')

	def field_to_str(self, val):
		val_str = val.__str__()
		if isinstance(val, str):
			val_str = val_str.replace("\n", " ").replace("\r", " ")
			val_str = "'%s'" % val_str.replace("'", "\\'")
		return val_str

	def send_progress_message(self, msg, val):
		events.emit(events.FILTER_INFO, msg, val)

	def saving_msg(self, val):
		msg = _('Saving in progress...')
		self.send_progress_message(msg, val)

	def send_ok(self, msg):
		events.emit(events.MESSAGES, msgconst.OK, msg)

	def send_info(self, msg):
		events.emit(events.MESSAGES, msgconst.INFO, msg)

	def send_warning(self, msg):
		events.emit(events.MESSAGES, msgconst.WARNING, msg)

	def send_error(self, msg):
		events.emit(events.MESSAGES, msgconst.ERROR, msg)
