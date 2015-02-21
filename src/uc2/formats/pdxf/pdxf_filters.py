# -*- coding: utf-8 -*-
#
#	Copyright (C) 2011 by Igor E. Novikov
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

import os
import sys

import zipfile
from zipfile import ZipFile

import xml.sax
from xml.sax.xmlreader import InputSource
from xml.sax import handler

from uc2 import _
from uc2 import events, msgconst, uc2const
from uc2.formats.pdxf import model
from uc2.formats.pdxf import const
from uc2.formats.pdxf import methods
from uc2.formats.generic import GENERIC_TAGS, IDENT
from uc2.utils import fs



def encode_quotes(line):
	result = line.replace('"', '&quot;')
#	result = result.replace("'", "&#039;")
	return result

def decode_quotes(line):
	result = line.replace('&quot;', '"')
	result = result.replace("&#039;", "'")
	return result

def escape_quote(line):
	return line.replace("'", "\\'")



class PDXF_Loader:
	name = 'PDXF_Loader'
	options = {}
	model = None
	file_handler = None

	def __init__(self):
		pass

	def load(self, presenter, path):
		self.presenter = presenter
		self.path = path

		if not zipfile.is_zipfile(self.path):
			msg = _('It seems the file is not PDXF file')
			events.emit(events.MESSAGES, msgconst.ERROR, msg)
			raise IOError(2, msg)


		self._extract_content()
		self._build_model()
		return self.model

	def _extract_content(self):
		pdxf_file = ZipFile(self.path, 'r')
		try:
			fl = pdxf_file.namelist()
		except:
			errtype, value, traceback = sys.exc_info()
			msg = _('It seems the PDXF file is corrupted') + '\n' + value
			events.emit(events.MESSAGES, msgconst.ERROR, msg)
			raise IOError(errtype, msg , traceback)
		if not 'mimetype' in fl or not pdxf_file.read('mimetype') == const.DOC_MIME:
			msg = _('The file is corrupted or not PDXF file')
			events.emit(events.MESSAGES, msgconst.ERROR, msg)
			raise IOError(2, msg)

		filelist = []
		for item in fl:
			if item == 'mimetype' or item[-1] == '/':
				continue
			filelist.append(item)

		for item in filelist:
			source = pdxf_file.read(item)
			dest = open(os.path.join(self.presenter.doc_dir, item), 'wb')
			dest.write(source)
			dest.close()
		msg = _('The file content is extracted successfully')
		events.emit(events.MESSAGES, msgconst.OK, msg)

	def _build_model(self):
		content_handler = XMLDocReader(self.presenter)
		error_handler = ErrorHandler()
		entity_resolver = EntityResolver()
		dtd_handler = DTDHandler()
		try:
			filename = os.path.join(self.presenter.doc_dir, 'content.xml')
			handler = open(filename, 'r')
			lines = float(sum(1 for l in handler))
			handler.close()
			self.file_handler = open(filename, "r")
			input_source = InputSource()
			input_source.setByteStream(self.file_handler)
			content_handler.lines = lines
			xml_reader = xml.sax.make_parser()
			xml_reader.setContentHandler(content_handler)
			xml_reader.setErrorHandler(error_handler)
			xml_reader.setEntityResolver(entity_resolver)
			xml_reader.setDTDHandler(dtd_handler)
			xml_reader.parse(input_source)
			self.file_handler.close()
			content_handler.file = None
		except:
			errtype, value, traceback = sys.exc_info()
			msg = _('It seems content.xml is corrupted') + '\n' + value
			events.emit(events.MESSAGES, msgconst.ERROR, msg)
			raise IOError(errtype, msg , traceback)
		self.model = content_handler.model

		msg = _('Content.xml is parsed successfully')
		events.emit(events.MESSAGES, msgconst.OK, msg)

class XMLDocReader(handler.ContentHandler):

	def __init__(self, presenter):
		self.model = None
		self.presenter = presenter
		self.parent_stack = []
		self.content = False
		self.lines = 0
		self.position = 0
		self.locator = None

	def setDocumentLocator(self, locator):
		self.locator = locator

	def startElement(self, name, attrs):
		if name == 'Content':
			pass
		else:
			position = float(self.locator.getLineNumber()) / self.lines
			if position - self.position > 0.05:
				msg = _('Parsing in process...')
				events.emit(events.FILTER_INFO, msg, position)
				self.position = position
			obj = None
			cid = model.TAGNAME_TO_CID[name]
			obj = model.CID_TO_CLASS[cid](self.presenter.config)
			obj.tag = name
			for item in attrs._attrs.keys():
				line = 'self.value=' + attrs._attrs[item]
				code = compile(line, '<string>', 'exec')
				exec code
				obj.__dict__[item] = self.value

			if self.parent_stack:
				parent = self.parent_stack[-1]
				methods.add_child(parent, obj)
			else:
				self.model = obj

			self.parent_stack.append(obj)


	def endElement(self, name):
		if name == 'Content':
			pass
		else:
			self.parent_stack = self.parent_stack[:-1]

	def characters(self, data):
		pass


class ErrorHandler(handler.ErrorHandler): pass
class EntityResolver(handler.EntityResolver): pass
class DTDHandler(handler.DTDHandler): pass


class PDXF_Saver:
	name = 'PDXF_Saver'
	file = None
	options = {}
	ident = 0
	content = []
	counter = 0
	obj_num = 0
	position = 0

	def __init__(self):
		pass

	def save(self, presenter, path):
		self.presenter = presenter
		self.path = path
		self.content = []
		self._save_content()
		self._write_manifest()
		self._pack_content()

	def _save_content(self):
		content_xml = os.path.join(self.presenter.doc_dir, 'content.xml')
		try:
			self.file = open(content_xml, 'wb')
		except:
			errtype, value, traceback = sys.exc_info()
			msg = _('Cannot open %s file for writing') % (content_xml)
			events.emit(events.MESSAGES, msgconst.ERROR, msg)
			raise IOError(errtype, msg + '\n' + value, traceback)

		doc = self.presenter.model
		self.obj_num = doc.count()
		self._start()
		self._write_tree(doc)
		self._finish()

		msg = _('PDXF file content.xml is created')
		events.emit(events.MESSAGES, msgconst.OK, msg)

	def _start(self):
		config = self.presenter.config
		ln = '<?xml version="1.0" encoding="%s"?>\n' % (config.system_encoding)
		self.file.write(ln)

	def _write_tree(self, item):
		self.counter += 1
		position = float(self.counter) / self.obj_num
		if position - self.position > 0.05:
			msg = _('Saving in process...')
			events.emit(events.FILTER_INFO, msg, position)
			self.position = position

		tag = model.CID_TO_TAGNAME[item.cid]
		params = self._get_params(item)
		self._open_tag(tag, params, item.childs)
		if item.childs:
			self.ident += 1
			for child in item.childs:
				self._write_tree(child)
			self.ident -= 1
			self._close_tag(tag)

	def _get_params(self, child):
		result = []
		props = child.__dict__
		items = props.keys()
		items.sort()
		for item in GENERIC_TAGS:
			if item in items:
				items.remove(item)
		for item in items:
			if not item[:5] == 'cache':
				item_str = props[item].__str__()
				if isinstance(props[item], str):
					item_str = "'%s'" % (escape_quote(item_str))
				result.append((item, encode_quotes(item_str)))
		return result

	def _open_tag(self, tag, params, len):
		self.file.write('%s<%s ' % (self.ident * IDENT, tag))
		for item in params:
			param, value = item
			self.file.write('\n%s %s="%s"' % (self.ident * IDENT, param, value))
		if len:
			self.file.write('>\n')
		else:
			self.file.write(' />\n')

	def _close_tag(self, tag):
		self.file.write('%s</%s>\n' % (self.ident * IDENT, tag))

	def _finish(self):
		self.file.close()

	def _write_manifest(self):
		xml = os.path.join(self.presenter.doc_dir, 'META-INF', 'manifest.xml')
		try:
			self.file = open(xml, 'wb')
		except:
			errtype, value, traceback = sys.exc_info()
			msg = _('Cannot open %s file for writing') % (xml)
			events.emit(events.MESSAGES, msgconst.ERROR, msg)
			raise IOError(errtype, msg + '\n' + value, traceback)
		self._start()
		self.file.write('<manifest>\n')
		self._write_manifest_entries()
		self.file.write('</manifest>\n')
		self._finish()
		filename = os.path.join('META-INF', 'manifest.xml')
		self.content.append((xml, filename))

		msg = _('PDXF file manifest.xml is created')
		events.emit(events.MESSAGES, msgconst.OK, msg)

	def _write_manifest_entries(self):
		metainf_content = []
		resources = self.presenter.rm.get_resources()[1]

		#Document
		metainf_content.append((const.DOC_MIME, '/'))

		#Doc MIME
		fn = 'mimetype'
		pt = os.path.join(self.presenter.doc_dir, fn)
		metainf_content.append((self._get_mime(fn), fn))
		self.content.append((pt, fn))

		#content.xml
		fn = 'content.xml'
		pt = os.path.join(self.presenter.doc_dir, fn)
		metainf_content.append((self._get_mime(fn), fn))
		self.content.append((pt, fn))

		#Doc directories
		for path in const.DOC_STRUCTURE:
			pt = os.path.join(self.presenter.doc_dir, path)
			self.content.append((pt, path))
			metainf_content.append(('', path + '/'))
			for item in resources:
				pt, fn = item.split('/')
				filepath = os.path.join(self.presenter.doc_dir, pt, fn)
				if pt == path and os.path.isfile(filepath):
					mime = self._get_mime(fn)
					metainf_content.append((mime, item))
					self.content.append((filepath, fn))

		#Writing manifest.xml
		for item in metainf_content:
			tp, pt = item
			ln = '\t<file-entry media-type="%s" full-path="%s"/>\n' % (tp, pt)
			self.file.write(ln)

	def _get_mime(self, filename):
		ext = os.path.splitext(filename)[1][1:].lower()
		if not ext: return 'text/plain'
		if ext in uc2const.MIMES.keys():return uc2const.MIMES[ext]
		return ''


	def _pack_content(self):
		pdxf_file = ZipFile(self.presenter.doc_file, 'w')
		for item in self.content:
			path, filename = item
			filename = filename.encode('ascii')
			pdxf_file.write(path, filename, zipfile.ZIP_DEFLATED)
		pdxf_file.close()

		msg = _('PDXF file is created successfully')
		events.emit(events.MESSAGES, msgconst.OK, msg)

