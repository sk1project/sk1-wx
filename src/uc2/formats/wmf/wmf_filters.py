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

from struct import calcsize

from uc2.formats.generic_filters import AbstractBinaryLoader, AbstractSaver
from uc2.formats.wmf.wmfconst import WMF_SIGNATURE, META_EOF
from uc2.formats.wmf.wmfconst import struct_wmf_header, struct_placeable_header
from uc2.formats.wmf.wmf_model import WMF_Placeble_Header, WMF_Header, WMF_Record

class WMF_Loader(AbstractBinaryLoader):

	name = 'WMF_Loader'

	def do_load(self):
		self.model = None
		self.parent = None
		sign = self.readbytes(len(WMF_SIGNATURE))
		self.fileptr.seek(0)
		if sign == WMF_SIGNATURE:
			placeable_header = self.readbytes(calcsize(struct_placeable_header))
			header = self.readbytes(calcsize(struct_wmf_header))
			self.model = WMF_Placeble_Header(placeable_header)
			self.parent = WMF_Header(header)
			self.model.childs.append(self.parent)
		else:
			header = self.readbytes(calcsize(struct_wmf_header))
			self.model = self.parent = WMF_Header(header)
		func = -1
		while not func == 0x0000:
			try:
				size = self.readdword()
				func = self.readword()
				self.fileptr.seek(-6, 1)
				chunk = self.readbytes(size * 2)
				self.parent.childs.append(WMF_Record(chunk))
			except:
				func = 0x0000
				self.parent.childs.append(WMF_Record('' + META_EOF))

class WMF_Saver(AbstractSaver):

	name = 'WMF_Saver'

	def do_save(self):
		self.model.save(self)
