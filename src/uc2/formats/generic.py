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
import os

from uc2 import _, uc2const
from uc2 import events, msgconst
from uc2.utils import fs

class ModelObject(object):
	"""
	Abstract parent class for all model 
	objects. Provides common object properties.
	"""
	cid = 0
	parent = None
	config = None
	childs = []

	def destroy(self):
		for child in self.childs:
			child.destroy()
		fields = self.__dict__
		items = fields.keys()
		for item in items:
			fields[item] = None

	def update(self): pass

	def do_update(self, presenter=None):
		for child in self.childs:
			child.parent = self
			child.config = self.config
			child.do_update(presenter)
		self.update()

	def count(self):
		val = len(self.childs)
		for child in self.childs:
			val += child.count()
		return val

	def resolve(self):
		if self.childs: return (False, 'Node', '')
		return (True, 'Leaf', '')

class TextModelObject(ModelObject):

	properties = []
	string = ''
	end_string = ''

GENERIC_TAGS = ['cid', 'childs', 'parent', 'config', 'tag']
IDENT = '\t'

class TaggedModelObject(ModelObject):

	tag = ''

class BinaryModelObject(ModelObject):

	chunk = ''
	cache_fields = []



class ModelPresenter(object):
	"""
	Abstract parent class for all model 
	presenters. Provides common functionality.
	"""

	cid = 0
	model_type = uc2const.GENERIC_MODEL
	config = None
	doc_dir = ''
	doc_file = ''
	doc_id = ''
	model = None

	loader = None
	saver = None
	methods = None
	obj_num = 0

	def new(self):pass

	def load(self, path=None, fileptr=None):
		if path and os.path.lexists(path):
			self.doc_file = path
		elif not fileptr:
			msg = _('Error while loading:') + ' ' + _('No file')
			self.send_error(msg)
			raise IOError(msg)

		try:
			self.parsing_msg(0.03)
			self.send_info(_('Parsing is started...'))
			self.model = self.loader.load(self, path, fileptr)
		except:
			self.close()
			raise IOError(_('Error while loading') + ' ' + path,
						sys.exc_info()[1], sys.exc_info()[2])

		self.send_ok(_('Document model is created'))
		self.update()

	def update(self):
		if not self.model is None:
			self.obj_num = self.model.count() + 1
			self.update_msg(0.0)
			try:
				self.model.config = self.config
				self.model.do_update(self)
			except:
				print sys.exc_info()[1], sys.exc_info()[2]
				msg = _('Exception while document model update')
				self.send_error(msg)
				raise IOError(msg)

			msg = _('Document model is updated successfully')
			self.send_progress_message(msg, 0.99)
			self.send_ok(msg)

	def save(self, path=None, fileptr=None):
		if path:
			self.doc_file = path
		elif not fileptr:
			msg = _('Error while saving:') + ' ' + _('No file data')
			self.send_error(msg)
			raise IOError(msg)

		try:
			self.saving_msg(0.03)
			self.send_info(_('Saving is started...'))
			self.saver.save(self, path, fileptr)
		except:
			msg = _('Error while saving') + ' ' + path
			self.send_error(msg)
			raise IOError(msg, sys.exc_info()[1], sys.exc_info()[2])

		msg = _('Document model is saved successfully')
		self.send_progress_message(msg, 0.95)
		self.send_ok(msg)

	def close(self):
		filename = self.doc_file
		self.doc_file = ''
		if not self.model is None:
			self.model.destroy()
		self.model = None

		self.send_ok(_('Document model is destroyed for') + ' %s' % (filename))

		if self.doc_dir and os.path.lexists(self.doc_dir):
			try:
				fs.xremove_dir(self.doc_dir)
				self.send_ok(_('Cache is cleared for') + ' %s' % (filename))
			except IOError:
				self.send_srror(_('Cache clearing is unsuccessful'))

	def update_msg(self, val):
		msg = _('%s model update in progress...') % (uc2const.FORMAT_NAMES[self.cid])
		self.send_progress_message(msg, val)

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

	def send_error(self, msg):
		events.emit(events.MESSAGES, msgconst.ERROR, msg)

class TextModelPresenter(ModelPresenter):

	model_type = uc2const.TEXT_MODEL

class TaggedModelPresenter(ModelPresenter):

	model_type = uc2const.TAGGED_MODEL

class BinaryModelPresenter(ModelPresenter):

	model_type = uc2const.BINARY_MODEL

