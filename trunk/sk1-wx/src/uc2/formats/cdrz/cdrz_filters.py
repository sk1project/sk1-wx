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
import traceback

import zipfile
from zipfile import ZipFile

from uc2 import events, msgconst
from uc2.formats.riff import model
from uc2.formats.riff.utils import get_chunk_size, dword2py_int, py_int2dword
from uc2.formats.cdrz.model import generic_dict

class CDRZ_Loader:

	name = 'CDRZ_Loader'
	version = 'CDRF'
	obj_map = {}

	def __init__(self):
		pass

	def load(self, presenter, path):
		self.presenter = presenter
		self.path = path

		if not zipfile.is_zipfile(self.path):
			msg = _('It seems the file is not CDRZ file')
			events.emit(events.MESSAGES, msgconst.ERROR, msg)
			raise IOError(2, msg)

		self._extract_content()
		self.model = None

		path = os.path.join(self.presenter.doc_dir, 'content', 'riffData.cdr')

#		try:
#			file = open(path, 'rb')
#		except:
#			errtype, value, trace = sys.exc_info()
#			msg = _('Cannot open %s file for reading') % (path)
#			events.emit(events.MESSAGES, msgconst.ERROR, msg)
#			raise IOError(errtype, msg + '\n' + value, trace)
#
#		self.model = self.parse_file(file)
#
#		file.close()
		return self.model

	def _extract_content(self):
		pdxf_file = ZipFile(self.path, 'r')
		try:
			fl = pdxf_file.namelist()
		except:
			errtype, value, traceback = sys.exc_info()
			msg = _('It seems the CDR file is corrupted') + '\n' + value
			events.emit(events.MESSAGES, msgconst.ERROR, msg)
			raise IOError(errtype, msg , traceback)

		filelist = []
		for item in fl:
			if item[-1] == '/':

				os.makedirs(self.path)
			filelist.append(item)

		for item in filelist:
			source = pdxf_file.read(item)
			dest = open(os.path.join(self.presenter.doc_dir, item), 'wb')
			dest.write(source)
			dest.close()
		msg = _('The file content is extracted successfully')
		events.emit(events.MESSAGES, msgconst.OK, msg)

	def parse_file(self, file):
		identifier = file.read(4)
		size_field = file.read(4)
		list_identifier = file.read(4)
		self.version = list_identifier
		self.obj_map = generic_dict
		obj = model.RiffRootList(identifier + size_field + list_identifier)

		size = get_chunk_size(size_field)
		while file.tell() < size + 8:
			ret = self.parse_stream(file)
			obj.childs.append(ret)

		return obj

	def get_class(self, identifier, list_identifier=''):
		if list_identifier:
			if self.obj_map.has_key(list_identifier):
				return self.obj_map[list_identifier]
			else:
				return model.RiffList
		else:
			if self.obj_map.has_key(identifier):
				return self.obj_map[identifier]
			else:
				return model.RiffObject

	def parse_stream(self, file):
		identifier = file.read(4)
		if identifier == 'LIST':
			return self.parse_list(file, identifier)
		else:
			return self.parse_object(file, identifier)

	def parse_list(self, file, identifier):
		size_field = file.read(4)
		list_identifier = file.read(4)

		size = get_chunk_size(size_field)
		offset = file.tell()

		if list_identifier == 'cmpr':
			file.seek(offset)
			chunk = file.read(size - 4)
			return self.parse_cmpr_list(identifier + size_field + \
									list_identifier + chunk)

		class_ = self.get_class(identifier, list_identifier)
		obj = class_(identifier + size_field + list_identifier)

		while file.tell() <= offset + size - 8:
			ret = self.parse_stream(file)
			if ret is None:
				file.seek(offset)
				chunk = file.read(size - 4)
				return model.RiffUnparsedList(identifier + size_field + \
										list_identifier + chunk)
			else:
				obj.childs.append(ret)

		return obj

	def parse_object(self, file, identifier):
		if not identifier[:3].isalnum():
			return None
		size_field = file.read(4)
		size = get_chunk_size(size_field)
		chunk = file.read(size)
		class_ = self.get_class(identifier)
		return class_(identifier + size_field + chunk)

	def parse_cmpr_list(self, buffer):
		obj = model.RiffCmprList(buffer)
		import StringIO, zlib
		compressedsize = dword2py_int(buffer[12:16])

		decomp = zlib.decompressobj()
		uncompresseddata = decomp.decompress(buffer[36:])

		blocksizesdata = zlib.decompress(buffer[36 + compressedsize:])
		blocksizes = []
		for i in range(0, len(blocksizesdata), 4):
			blocksizes.append(dword2py_int(blocksizesdata[i:i + 4]))

		stream = StringIO.StringIO(uncompresseddata)
		while stream.tell() < len(uncompresseddata):
			ret = self.parse_comressed_stream(stream, blocksizes)
			obj.childs.append(ret)

		return obj

	def parse_comressed_stream(self, stream, blocksizes):
		identifier = stream.read(4)
		if identifier == 'LIST':
			return self.parse_compressed_list(stream, identifier, blocksizes)
		else:
			return self.parse_compressed_object(stream, identifier, blocksizes)

	def parse_compressed_list(self, stream, identifier, blocksizes):
		rawsize = dword2py_int(stream.read(4))
		list_identifier = stream.read(4)
		size = blocksizes[rawsize]

		size_field = py_int2dword(size)
		if size & 1:size += 1

		offset = stream.tell()

		class_ = self.get_class(identifier, list_identifier)
		obj = class_(identifier + size_field + list_identifier)

		while stream.tell() <= offset + size - 8:
			ret = self.parse_comressed_stream(stream, blocksizes)
			if ret is None:
				stream.seek(offset)
				chunk = stream.read(size - 4)
				return model.RiffUnparsedList(identifier + size_field + \
										list_identifier + chunk)
			else:
				obj.childs.append(ret)

		return obj

	def parse_compressed_object(self, stream, identifier, blocksizes):
		if not identifier[:3].isalnum():
			return None
		rawsize = dword2py_int(stream.read(4))
		size = blocksizes[rawsize]
		size_field = py_int2dword(size)
		if size & 1:size += 1
		chunk = stream.read(size)
		class_ = self.get_class(identifier)
		return class_(identifier + size_field + chunk)


class CDRZ_Saver:

	name = 'CDRZ_Saver'

	def __init__(self):
		pass

	def save(self, presenter, path):

		try:
			file = open(path, 'wb')
		except:
			errtype, value, traceback = sys.exc_info()
			msg = _('Cannot open %s file for writing') % (path)
			events.emit(events.MESSAGES, msgconst.ERROR, msg)
			raise IOError(errtype, msg + '\n' + value, traceback)

		file.write(presenter.model.get_chunk())
		file.close()
