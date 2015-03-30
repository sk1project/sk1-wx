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

from uc2 import _, events, msgconst
from uc2.formats.plt import plt_model
from uc2.formats.generic_filters import AbstractLoader, AbstractSaver

PLT_CMDS = ['PU', 'PD']

class PLT_Loader(AbstractLoader):

	name = 'PLT_Loader'

	def do_load(self):
		self.jobs = []

		res = self.file.read().split('IN;')

		if not len(res) == 2:
			msg = _('Wrong content: "IN;" instruction should be unique')
			events.emit(events.MESSAGES, msgconst.ERROR, msg)
			raise IOError(msg)

		if res[0]:
			self.model.string = res[0]
		cmds = res[1].split(';')
		jobs = []
		job = []
		stack = ''
		for cmd in cmds:
			if cmd[:2] == 'PU':
				stack = cmd
				if job:
					jobs.append(job)
					job = []
			elif cmd[:2] == 'PD':
				if not job:
					if not stack:
						stack = 'PU0,0'
					job.append(stack)
				job.append(cmd)

		for job in jobs:
			string = ''
			for cmd in job:
				string += cmd + ';'
			self.jobs.append(plt_model.PltJob(string))

		self.model.childs[1].childs = self.jobs


class PLT_Saver(AbstractSaver):

	name = 'PLT_Saver'

	def do_save(self):
		self.fileptr.write(self.model.get_content())

