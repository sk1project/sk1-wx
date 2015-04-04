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

import os

from uc2 import cms
from uc2.formats.generic_filters import AbstractBinaryLoader, AbstractSaver
from uc2.formats.cpl import cpl_const
from uc2.formats.cpl.cpl_model import CPL10_Palette, CPL10_Color

class CPL_Loader(AbstractBinaryLoader):

	name = 'CPL_Loader'

	def do_load(self):
		ver = self.readbytes(2)
		if ver == cpl_const.CPL10: self.do_cpl10_load()
		if not self.model.name and self.doc_file:
			name = os.path.basename(self.filepath).replace('.cpl', '')
			self.model.name = name + ' palette'

	def do_cpl10_load(self):
		self.model = CPL10_Palette()
		size = self.readbyte()
		self.model.name = self.readstr(size)
		ncolors = self.readword()
		self.fileptr.seek(0)
		self.model.chunk = self.readbytes(2 + 1 + size + 2)
		for i in range(ncolors):
			color = CPL10_Color()
			color.model = self.readword()
			color.valbytes = self.readbytes(10)
			size = self.readbyte()
			color.name = self.readstr(size)
			ln = 2 + 10 + 1 + size
			self.fileptr.seek(-ln, 1)
			color.chunk = self.readbytes(ln)
			self.model.childs.append(color)



class CPL_Saver(AbstractSaver):

	name = 'CPL_Saver'

	def do_save(self):pass
