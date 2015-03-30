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

import sys, os, errno

from uc2 import _, events, msgconst

def get_fileptr(path, write=False):
	fileptr = None
	if not file:
		msg = _('There is no file path')
		raise IOError(errno.ENODATA, msg, '')
	if write:
		try:
			fileptr = open(path, 'wb')
		except:
			errtype, value, traceback = sys.exc_info()
			msg = _('Cannot open %s file for writing') % (path)
			events.emit(events.MESSAGES, msgconst.ERROR, msg)
			raise IOError(errtype, msg + '\n' + value, traceback)
	else:
		try:
			fileptr = open(path, 'rb')
		except:
			errtype, value, traceback = sys.exc_info()
			msg = _('Cannot open %s file for reading') % (path)
			events.emit(events.MESSAGES, msgconst.ERROR, msg)
			raise IOError(errtype, msg + '\n' + value, traceback)
	return fileptr

class AbstractLoader(object):
	name = 'Abstract Loader'

	presenter = None
	config = None
	model = None

	filepath = ''
	fileptr = None
	position = 0
	file_size = 0

	def __init__(self):pass

	def load(self, presenter, path=None, fileptr=None):
		self.presenter = presenter
		self.model = presenter.model
		self.config = self.presenter.config
		if path:
			self.filepath = path
			self.file_size = os.path.getsize(path)
			self.fileptr = get_fileptr(path)
		elif fileptr:
			self.fileptr = fileptr
			self.fileptr.seek(0, 2)
			self.file_size = self.fileptr.tell()
			self.fileptr.seek(0)
		else:
			msg = _('There is no file for reading')
			raise IOError(errno.ENODATA, msg, '')

		self.do_load()

		self.fileptr.close()
		self.position = 0
		return self.model

	def do_load(self):pass

	def check_loading(self):
		position = float(self.fileptr.tell()) / float(self.file_size) * 0.95
		if position - self.position > 0.02:
			self.position = position
			self.parsing_msg(position)

	def send_progress_message(self, msg, val):
		events.emit(events.FILTER_INFO, msg, val)

	def parsing_msg(self, val):
		msg = _('Parsing in progress...')
		self.send_progress_message(msg, val)

	def send_ok(self, msg):
		events.emit(events.MESSAGES, msgconst.OK, msg)

	def send_info(self, msg):
		events.emit(events.MESSAGES, msgconst.INFO, msg)

	def send_warning(self, msg):
		events.emit(events.MESSAGES, msgconst.WARNING, msg)

	def send_error(self, msg):
		events.emit(events.MESSAGES, msgconst.ERROR, msg)


class AbstractSaver(object):

	name = 'Abstract Saver'

	presenter = None
	config = None

	filepath = ''
	fileptr = None
	position = 0
	file_size = 0

	model = None

	def __init__(self):pass

	def save(self, presenter, path=None, fileptr=None):
		self.presenter = presenter
		self.model = presenter.model
		if path:
			self.fileptr = get_fileptr(path, True)
		elif fileptr:
			self.fileptr = fileptr
		else:
			msg = _('There is no file for writting')
			raise IOError(errno.ENODATA, msg, '')

		self.presenter.update()
		self.do_save()
		self.fileptr.close()
		self.fileptr = None

	def do_save(self):pass

	def write_line(self, line):
		self.fileptr.write(line + '\n')

	def send_progress_message(self, msg, val):
		events.emit(events.FILTER_INFO, msg, val)

	def saving_msg(self, val):
		msg = _('Saving in progress...')
		self.send_progress_message(msg, val)

	def send_ok(self, msg):
		events.emit(events.MESSAGES, msgconst.OK, msg)

	def send_info(self, msg):
		events.emit(events.MESSAGES, msgconst.INFO, msg)

	def send_warning(self, msg):
		events.emit(events.MESSAGES, msgconst.WARNING, msg)

	def send_error(self, msg):
		events.emit(events.MESSAGES, msgconst.ERROR, msg)
