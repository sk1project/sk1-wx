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

import sys

from uc2 import _, events, msgconst
from uc2.formats.plt import model

PLT_CMDS = ['PU', 'PD']

class PLT_Loader:
	name = 'PLT_Loader'
	presenter = None
	path = None
	options = {}
	model = None

	def __init__(self):
		pass

	def load(self, presenter, path):
		self.presenter = presenter
		self.path = path
		self.model = presenter.model
		self.jobs = []

		try:
			file = open(path, 'rb')
		except:
			errtype, value, traceback = sys.exc_info()
			msg = _('Cannot open %s file for writing') % (path)
			events.emit(events.MESSAGES, msgconst.ERROR, msg)
			raise IOError(errtype, msg + '\n' + value, traceback)

		res = file.read().split('IN;')
		file.close()

		if not len(res) == 2:
			msg = _('Wrong content in %s file: "IN;" instruction should be unique') % (path)
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
			self.jobs.append(model.PltJob(string))

		self.model.childs[1].childs = self.jobs
		return self.model


class PLT_Saver:

	name = 'PLT_Saver'

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

		file.write(presenter.model.get_content())
		file.close()

