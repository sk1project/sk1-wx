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

import os, sys
import gtk

from uc2.formats import get_loader, get_saver

from sword import _, config, events
from sword.eventloop import EventLoop
from sword.selection import ModelSelection
from sword.widgets.docarea import DocArea
from sword.dialogs import ProgressDialog

class SW_Presenter:

	doc_presenter = None
	doc_file = ''
	doc_name = ''

	model = None

	saved = True

	eventloop = None
	docarea = None
	traced_objects = []

	def __init__(self, app, doc_file=''):
		self.app = app
		self.eventloop = EventLoop(self)
		self.doc_file = doc_file
		if doc_file:
			loader = get_loader(doc_file, True)
			if loader is None:
				raise IOError(_('Unknown file format'), doc_file)

			pd = ProgressDialog(_('Opening file...'), self.app.mw)
			ret = pd.run(loader, [app.appdata, doc_file, None, False, False])
			if ret == gtk.RESPONSE_OK:
				if pd.result is None:
					pd.destroy()
					raise IOError(*pd.error_info)

				self.doc_presenter = pd.result
				pd.destroy()
			else:
				pd.destroy()
				raise IOError(_('Error while opening'), doc_file)

			self.doc_file = self.doc_presenter.doc_file
			self.doc_name = os.path.basename(self.doc_file)
		else:
			#FIXME: Here should be new model creation
			self.doc_name = self.app.get_new_docname()


		self.selection = ModelSelection(self)
		self.docarea = DocArea(self.app, self)
		self.app.mw.add_tab(self.docarea)
		self.selection.set_root()

	def close(self):
		if not self.docarea is None:
			self.app.mw.remove_tab(self.docarea)
		if not self.doc_presenter is None:
			self.doc_presenter.close()
		for obj in self.traced_objects:
			fields = obj.__dict__
			items = fields.keys()
			for item in items:
				fields[item] = None

	def modified(self, *args):
		self.saved = False
		self.set_title()
		events.emit(events.DOC_MODIFIED, self)

	def reflect_saving(self):
		self.saved = True
		self.set_title()
		events.emit(events.DOC_SAVED, self)

	def set_title(self):
		if self.saved:
			title = self.doc_name
		else:
			title = self.doc_name + '*'
		self.app.mw.set_tab_title(self.docarea, title)

	def set_doc_file(self, doc_file, doc_name=''):
		self.doc_file = doc_file
		if doc_name:
			self.doc_name = doc_name
		else:
			self.doc_name = os.path.basename(self.doc_file)
		self.set_title()

	def save(self):
		try:
			if config.make_backup:
				if os.path.lexists(self.doc_file):
					if os.path.lexists(self.doc_file + '~'):
						os.remove(self.doc_file + '~')
					os.rename(self.doc_file, self.doc_file + '~')
			saver = get_saver(self.doc_file, True)
			if saver is None:
				raise IOError(_('Unknown file format is requested for saving!'),
							 self.doc_file)

			pd = ProgressDialog(_('Saving file...'), self.app.mw)
			ret = pd.run(saver, [self.doc_presenter, self.doc_file, False])
			if ret == gtk.RESPONSE_OK:
				if not pd.error_info is None:
					pd.destroy()
					raise IOError(*pd.error_info)
				pd.destroy()
			else:
				pd.destroy()
				raise IOError(_('Error while saving'), self.doc_file)

		except IOError:
			raise IOError(*sys.exc_info())
		self.reflect_saving()
