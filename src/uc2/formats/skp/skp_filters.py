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

from uc2.formats.skp.skp_const import SKP_HEADER
from uc2.formats.generic_filters import AbstractLoader, AbstractSaver

class SKP_Loader(AbstractLoader):

	name = 'SKP_Loader'

	def do_load(self):
		self.fileptr.readline()
		while True:
			self.line = self.fileptr.readline()
			if not self.line: break
			self.line = self.line.rstrip('\r\n')

			self.check_loading()

			if self.line:
				try:
					code = compile('self.' + self.line, '<string>', 'exec')
					exec code
				except:
					pass

	def palette(self):pass
	def set_name(self, name): self.model.name = name
	def set_source(self, source): self.model.source = source
	def add_comments(self, txt): self.model.comments += txt + os.linesep
	def set_columns(self, val): self.model.columns = val
	def color(self, color): self.model.colors.append(color)
	def palette_end(self):pass

class SKP_Saver(AbstractSaver):

	name = 'SKP_Saver'

	def do_save(self):
		self.writeln(SKP_HEADER)
		self.writeln('palette()')
		self.writeln("set_name(%s)" % self.field_to_str(self.model.name))
		self.writeln("set_source(%s)" % self.field_to_str(self.model.source))
		for item in self.model.comments.splitlines():
			self.writeln("add_comments(%s)" % self.field_to_str(item))
		self.writeln("set_columns(%s)" % self.field_to_str(self.model.columns))
		for item in self.model.colors:
			self.writeln('color(%s)' % self.field_to_str(item))
		self.writeln('palette_end()')

