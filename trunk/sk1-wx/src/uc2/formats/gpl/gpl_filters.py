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

from uc2.formats.gpl.gpl_const import GPL_HEADER
from uc2.formats.generic_filters import AbstractLoader, AbstractSaver

class GPL_Loader(AbstractLoader):

	name = 'GPL_Loader'

	def do_load(self):
		self.fileptr.readline()


class GPL_Saver(AbstractSaver):

	name = 'GPL_Saver'

	def do_save(self):pass
