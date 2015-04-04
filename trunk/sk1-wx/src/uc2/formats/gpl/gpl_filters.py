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
from uc2.formats.gpl.gpl_const import GPL_HEADER, COL_STR, NAME_STR
from uc2.formats.generic_filters import AbstractLoader, AbstractSaver

class GPL_Loader(AbstractLoader):

	name = 'GPL_Loader'

	def do_load(self):
		comments = ''
		self.readln()
		self.model.name = self.readln().split(NAME_STR)[1].strip()
		line = self.readln()
		if line[:len(COL_STR)] == COL_STR:
			self.model.columns = int(line.split(COL_STR)[1].strip())
		while True:
			line = self.readln(False)
			if not line[0] == '#':break
			if len(line) > 1:line = line[1:].strip()
			else:line = ''
			comments += line + os.linesep
		self.set_comments(comments)
		while True:
			self.add_color(line)
			line = self.readln(False)
			if not line:break

	def set_comments(self, comments):
		if not len(comments):return
		lines = comments.splitlines()
		if len(lines) < 2:return
		while not lines[0]: lines = lines[1:]
		while not lines[-1]: lines = lines[:-1]
		for item in lines:
			self.model.comments += item + os.linesep

	def add_color(self, line):
		if line[0] == '#' or not line:return
		r = int(line[:4])
		g = int(line[4:8])
		b = int(line[8:12])
		name = ''
		if len(line) > 11:
			name = line[12:].strip()
		else:
			if self.config.set_color_name:
				name = cms.rgb_to_hexcolor(cms.val_255_to_dec((r, g, b)))
		self.model.colors.append([r, g, b, name])


class GPL_Saver(AbstractSaver):

	name = 'GPL_Saver'

	def do_save(self):
		self.writeln(GPL_HEADER)
		self.writeln('%s %s' % (NAME_STR, self.model.name))
		if self.model.columns > 1:
			self.writeln('%s %u' % (COL_STR, self.model.columns))
		self.writeln('#')
		if self.model.comments:
			lines = self.model.comments.splitlines()
			while True:
				if not lines[-1].strip(): lines = lines[-1]
				else: break
			for line in lines:
				self.writeln('# %s' % line)
			self.writeln('#')
		for item in self.model.colors:
			line = '%3u %3u %3u' % (item[0], item[1], item[2])
			if item[3]:
				line += '\t' + item[3]
			self.writeln(line)
