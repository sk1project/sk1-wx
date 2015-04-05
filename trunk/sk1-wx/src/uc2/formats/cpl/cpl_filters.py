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

from uc2.formats.generic_filters import AbstractBinaryLoader, AbstractSaver
from uc2.formats.cpl import cpl_const
from uc2.formats.cpl.cpl_model import CPL8_Palette, CPL7_Palette

class CPL_Loader(AbstractBinaryLoader):

	name = 'CPL_Loader'

	def do_load(self):
		ver = self.readbytes(2)
		if ver == cpl_const.CPL8:
			self.model = CPL8_Palette()
		elif ver == cpl_const.CPL7:
			self.model = CPL7_Palette()
		if self.model:
			self.model.parse(self)
			if not self.model.name and self.filepath:
				name = os.path.basename(self.filepath).replace('.cpl', '')
				self.model.name = '%s palette' % name



class CPL_Saver(AbstractSaver):

	name = 'CPL_Saver'

	def do_save(self):pass
