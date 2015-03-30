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

from uc2.formats.generic_filters import AbstractLoader, AbstractSaver
from uc2.formats.riff import model
from uc2.formats.riff.utils import get_chunk_size, dword2py_int, py_int2dword

class RIFF_Loader(AbstractLoader):

	name = 'RIFF_Loader'

	def do_load(self):
		self.model = None
		self.parent_stack = []
		self.model = self.parse_file(self.file)

	def parse_file(self, fileptr):
		identifier = fileptr.read(4)
		size_field = fileptr.read(4)
		list_identifier = fileptr.read(4)
		obj = model.RiffRootList(identifier + size_field + list_identifier)

		size = get_chunk_size(size_field)
		while fileptr.tell() < size + 8:
			ret = self.parse_stream(fileptr)
			obj.childs.append(ret)

		return obj

	def parse_stream(self, fileptr):
		identifier = fileptr.read(4)
		if identifier == 'LIST':
			return self.parse_list(fileptr, identifier)
		elif identifier == 'pack':
			return self.parse_pack(fileptr, identifier)
		else:
			return self.parse_object(fileptr, identifier)

	def parse_list(self, fileptr, identifier):
		size_field = fileptr.read(4)
		list_identifier = fileptr.read(4)

		size = get_chunk_size(size_field)
		offset = fileptr.tell()

		if list_identifier == 'cmpr':
			fileptr.seek(offset)
			chunk = fileptr.read(size - 4)
			return self.parse_cmpr_list(identifier + size_field + \
									list_identifier + chunk)

		obj = model.RiffList(identifier + size_field + list_identifier)

		while fileptr.tell() <= offset + size - 8:
			ret = self.parse_stream(fileptr)
			if ret is None:
				fileptr.seek(offset)
				chunk = fileptr.read(size - 4)
				return model.RiffUnparsedList(identifier + size_field + \
										list_identifier + chunk)
			else:
				obj.childs.append(ret)

		return obj

	def parse_object(self, fileptr, identifier):
		if not identifier[:3].isalnum():
			return None
		size_field = fileptr.read(4)
		size = get_chunk_size(size_field)
		chunk = fileptr.read(size)
		return model.RiffObject(identifier + size_field + chunk)

	def parse_pack(self, fileptr, identifier):
		size_field = fileptr.read(4)
		size = get_chunk_size(size_field)
		chunk = fileptr.read(size)
		obj = model.RiffPackObject(identifier + size_field + chunk)

		import StringIO, zlib
		decomp = zlib.decompressobj()
		uncompresseddata = decomp.decompress(chunk[12:])
		stream = StringIO.StringIO(uncompresseddata)

		while stream.tell() < len(uncompresseddata):
			ret = self.parse_stream(stream)
			obj.childs.append(ret)

		return obj

	def parse_cmpr_list(self, buff):
		obj = model.RiffCmprList(buff)
		import StringIO, zlib
		compressedsize = dword2py_int(buff[12:16])

		decomp = zlib.decompressobj()
		uncompresseddata = decomp.decompress(buff[36:])

		blocksizesdata = zlib.decompress(buff[36 + compressedsize:])
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
		print list_identifier

		size = blocksizes[rawsize]

		size_field = py_int2dword(size)
		if size & 1:size += 1

		offset = stream.tell()

		obj = model.RiffList(identifier + size_field + list_identifier)

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
		return model.RiffObject(identifier + size_field + chunk)


class RIFF_Saver(AbstractSaver):

	name = 'RIFF_Saver'

	def do_save(self):
		self.fileptr.write(self.model.get_chunk())
