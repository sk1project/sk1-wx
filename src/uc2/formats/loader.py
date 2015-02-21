# -*- coding: utf-8 -*-
#
#	Copyright (C) 2013 by Igor E. Novikov
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

import sys, os

from uc2 import _, events, msgconst

class AbstractLoader:
	name = 'Abstract Loader'

	presenter = None
	config = None

	filepath = ''
	file = None
	position = 0
	file_size = 0

	model = None

	def __init__(self):pass

	def load(self, presenter, path):
		self.filepath = path
		self.presenter = presenter
		self.config = self.presenter.config
		self.file_size = os.path.getsize(path)
		try:
			self.file = open(path, 'rb')
		except:
			errtype, value, traceback = sys.exc_info()
			msg = _('Cannot open %s file for writing') % (path)
			events.emit(events.MESSAGES, msgconst.ERROR, msg)
			raise IOError(errtype, msg + '\n' + value, traceback)

		self.do_load()

		self.file.close()
		self.position = 0
		return self.model

	def do_load(self):pass

	def parsing_msg(self, val):
		msg = _('Parsing in progress...')
		self.send_progress_message(msg, val)

	def saving_msg(self, val):
		msg = _('Saving in progress...')
		self.send_progress_message(msg, val)

	def send_progress_message(self, msg, val):
		events.emit(events.FILTER_INFO, msg, val)

	def send_ok(self, msg):
		events.emit(events.MESSAGES, msgconst.OK, msg)

	def send_info(self, msg):
		events.emit(events.MESSAGES, msgconst.INFO, msg)

	def send_warning(self, msg):
		events.emit(events.MESSAGES, msgconst.WARNING, msg)

	def send_error(self, msg):
		events.emit(events.MESSAGES, msgconst.ERROR, msg)
