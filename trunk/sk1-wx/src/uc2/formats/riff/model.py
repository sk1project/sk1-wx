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


from uc2.formats.generic import BinaryModelObject
from uc2.formats.riff.utils import dword2py_int, py_int2dword

RIFF_ROOT = 1
RIFF_LIST = 2
RIFF_UNPARSED_LIST = 4
RIFF_CMPR_LIST = 5
RIFF_PACK = 9
RIFF_OBJECT = 10

class RiffModelObject(BinaryModelObject):
	"""
	Generic RIFF model object.
	The class provides basic RIFF object features.
	
	Details about RIFF format:
	http://en.wikipedia.org/wiki/Resource_Interchange_File_Format
	"""

	identifier = ''
	chunk_tag = ''
	chunk_size = 0
	version = ''

	def resolve(self):
		name = ''
		if self.chunk_tag:
			name = '<%s>' % (self.chunk_tag)
		if self.cid < RIFF_OBJECT: return (False, name, str(self.chunk_size))
		return (True, name, str(self.chunk_size))

	def get_chunk(self):
		chunk = ''
		for child in self.childs:
			chunk += child.get_chunk()
		chunk = self.chunk + chunk
		return chunk

	def update(self):pass

	def do_update(self, presenter):
		for child in self.childs:
			child.parent = self
			child.version = self.version
			child.config = self.config
			child.do_update(presenter)
		self.update()

	def translate(self, translator):
		for child in self.childs:
			child.translate(translator)


class RiffList(RiffModelObject):
	"""
	RIFF model list.
	The class provides RIFF list features. The object is a RIFF model node.
	
	Details about RIFF format:
	http://en.wikipedia.org/wiki/Resource_Interchange_File_Format
	"""

	cid = RIFF_LIST

	def __init__(self, chunk):
		self.childs = []
		self.chunk = chunk
		self.identifier = 'LIST'
		self.chunk_tag = self.chunk[8:12]
		self.chunk_size = dword2py_int(chunk[4:8])
		self.cache_fields = [
						(0, 4, 'list identifier'),
						(4, 4, 'chunk size'),
						(8, 4, 'chunk tag')
						]

class RiffRootList(RiffList):
	"""
	Root RIFF model list.
	The class provides root RIFF list features. According to RIFF specification
	the object has always 'RIFF' identifier. The root list size is a file
	size excluding the list header 12 bytes.
	
	Details about RIFF format:
	http://en.wikipedia.org/wiki/Resource_Interchange_File_Format
	"""

	cid = RIFF_ROOT

	def __init__(self, chunk=''):
		if not chunk:
			chunk = 'RIFF' + py_int2dword(4) + 'riff'
		RiffList.__init__(self, chunk)
		self.version = self.chunk_tag

class RiffUnparsedList(RiffList):
	"""
	Unparsed RIFF model list.
	Some list objects contain non-RIFF content. This list type is used
	for such cases. The object just stores unparsed internal list content.
	
	Details about RIFF format:
	http://en.wikipedia.org/wiki/Resource_Interchange_File_Format
	"""

	cid = RIFF_UNPARSED_LIST

	def __init__(self, chunk):
		RiffList.__init__(self, chunk)

class RiffCmprList(RiffUnparsedList):
	"""
	Compressed RIFF model list.
	The list has unusual structure because packed child object size is redefined
	in special list. For CDR format the list type contains all graphics data.
	
	Details about RIFF format:
	http://en.wikipedia.org/wiki/Resource_Interchange_File_Format
	"""

	cid = RIFF_CMPR_LIST

	def __init__(self, chunk):
		RiffList.__init__(self, chunk)

		self.compressedsize = dword2py_int(chunk[12:16])
		self.uncompressedsize = dword2py_int(chunk[16:20])
		self.blocksizessize = dword2py_int(chunk[20:24])

	def get_chunk(self):
		return self.chunk

class RiffObject(RiffModelObject):
	"""
	RIFF model object.
	The class provides RIFF object features. The object is a RIFF model leaf.
	
	Details about RIFF format:
	http://en.wikipedia.org/wiki/Resource_Interchange_File_Format
	"""

	cid = RIFF_OBJECT

	def __init__(self, chunk):
		self.chunk = chunk
		self.identifier = chunk[:4]
		self.chunk_size = dword2py_int(chunk[4:8])
		self.chunk_tag = '' + self.identifier
		self.cache_fields = [
						(0, 4, 'identifier'),
						(4, 4, 'chunk size'),
						]

	def get_chunk(self):
		return self.chunk

class RiffPackObject(RiffObject):
	"""
	Compressed RIFF object.
	Actually the object serves as a list because contains a lot of childs,
	but according to RIFF specification the object is not a list.
	It seems the object is CDRX format specific. 
	
	Details about RIFF format:
	http://en.wikipedia.org/wiki/Resource_Interchange_File_Format
	"""

	cid = RIFF_PACK

	def __init__(self, chunk):
		RiffObject.__init__(self, chunk)
		self.childs = []


TAG_TO_CLASS = {
'RIFF':RiffRootList,
'LIST':RiffList,
'pack':RiffPackObject,
'generic':RiffObject
}
