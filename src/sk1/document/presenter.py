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

import os, sys
from copy import deepcopy

from uc2.formats import get_loader, get_saver
from uc2.formats.sk2.sk2_presenter import SK2_Presenter
from uc2 import uc2const
from uc2.utils.fs import change_file_extension

from sk1 import _, config, events
from sk1.document.eventloop import EventLoop
from sk1.document.selection import Selection
from sk1.document.api import PresenterAPI
from sk1.document.snapping import SnapManager
from sk1.dialogs import ProgressDialog

class PD_Presenter:

	api = None
	doc_presenter = None
	doc_file = ''
	doc_name = ''


	model = None
	cms = None
	methods = None
	renderer = None
	active_page = None
	active_layer = None

	saved = True

	eventloop = None
	docarea = None
	canvas = None
	selection = None
	traced_objects = None
	snap = None

	def __init__(self, app, doc_file='', silent=False):
		self.app = app

		self.eventloop = EventLoop(self)
		self.selection = Selection(self)

		if doc_file:
			loader = get_loader(doc_file)
			if loader is None:
				raise IOError(_('Unknown file format'), doc_file)

			if silent:
				self.doc_presenter = loader(app.appdata, doc_file)
			else:
				pd = ProgressDialog(_('Opening file...'), self.app.mw)
				ret = pd.run(loader, [self.app.appdata, doc_file])
				if ret:
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
			self.doc_name = change_file_extension(self.doc_name,
									uc2const.FORMAT_EXTENSION[uc2const.SK2][0])
		else:
			self.doc_presenter = SK2_Presenter(app.appdata)
			self.doc_name = self.app.get_new_docname()

		self.methods = self.doc_presenter.methods
		self.model = self.doc_presenter.model
		self.set_active_page()


		self.cms = self.doc_presenter.cms
		#self.app.default_cms.registry_cm(self.cms)

		self.api = PresenterAPI(self)
		self.docarea = self.app.mdi.create_docarea(self)
		self.canvas = self.docarea.canvas
		self.canvas.set_mode()
		self.eventloop.connect(self.eventloop.DOC_MODIFIED, self.modified)
		self.snap = SnapManager(self)
		self.set_title()

	def set_title(self):
		if self.saved:
			title = self.doc_name
		else:
			title = self.doc_name + '*'
		self.app.mdi.set_tab_title(self.docarea, title)
		if self == self.app.current_doc:
			self.app.mw.set_title(title)

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
			saver = get_saver(self.doc_file)
			if saver is None:
				raise IOError(_('Unknown file format is requested for saving!'),
							 self.doc_file)

			pd = ProgressDialog(_('Saving file...'), self.app.mw)
			ret = pd.run(saver, [self.doc_presenter, self.doc_file], False)
			if ret:
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

	def save_selected(self, doc_file):
		doc = SK2_Presenter(self.app.appdata)
		origin = self.doc_presenter.model.doc_origin
		doc.methods.set_doc_origin(origin)
		doc_units = self.doc_presenter.model.doc_units
		doc.methods.set_doc_units(doc_units)
		page = doc.methods.get_page()
		page_format = deepcopy(self.active_page.page_format)
		doc.methods.set_page_format(page, page_format)
		objs = []
		for item in self.selection.objs:
			objs.append(item.copy())
		layer = doc.methods.get_layer(page)
		layer.childs = objs

		saver = get_saver(doc_file)
		if saver is None:
			doc.close()
			raise IOError(_('Unknown file format is requested for saving!'),
						 self.doc_file)

		pd = ProgressDialog(_('Saving file...'), self.app.mw)
		ret = pd.run(saver, [doc, doc_file], False)
		if ret:
			if not pd.error_info is None:
				pd.destroy()
				doc.close()
				raise IOError(*pd.error_info)
			pd.destroy()
			doc.close()
		else:
			pd.destroy()
			doc.close()
			raise IOError(_('Error while saving'), doc_file)

	def close(self):
		self.app.mdi.remove_doc(self)
#		self.app.default_cms.unregistry_cm(self.cms)
		self.eventloop.destroy()
		self.api.destroy()
		self.doc_presenter.close()
		self.docarea.destroy()
		self.selection.destroy()
		self.snap.destroy()

		items = self.__dict__.keys()
		for item in items:
			self.__dict__[item] = None

	def import_file(self, doc_file):
		retval = True
		loader = get_loader(doc_file)
		if loader is None:
			raise IOError(_('Unknown file format'), doc_file)
		pd = ProgressDialog(_('Opening file...'), self.app.mw)
		ret = pd.run(loader, [self.app.appdata, doc_file])
		if ret:
			if pd.result is None:
				pd.destroy()
				raise IOError(*pd.error_info)

			doc_presenter = pd.result
			pd.destroy()
		else:
			pd.destroy()
			raise IOError(_('Error while opening'), doc_file)
		pages = doc_presenter.methods.get_pages()
		if len(pages) == 1:
			page = doc_presenter.methods.get_page()
			objs = []
			for layer in page.childs:
				for child in layer.childs:
					objs.append(child)
				layer.childs = []
			if objs:
				self.api.paste_selected(objs)
			else:
				retval = False
		else:
			pages = doc_presenter.methods.get_pages()
			pages_obj = doc_presenter.methods.get_pages_obj()
			pages_obj.childs = []
			if pages:
				self.api.add_pages(pages)
			else:
				retval = False
		doc_presenter.close()
		return retval

	def modified(self, *args):
		self.saved = False
		self.set_title()
		events.emit(events.DOC_MODIFIED, self)

	def reflect_saving(self):
		self.saved = True
		self.set_title()
		self.api.save_mark()
		events.emit(events.DOC_SAVED, self)

	def set_active_page(self, page_num=0):
		self.active_page = self.doc_presenter.methods.get_page(page_num)
		self.set_active_layer(self.active_page)

	def get_pages(self):
		return self.doc_presenter.methods.get_pages()

	def next_page(self):
		pages = self.get_pages()
		if pages.index(self.active_page) < len(pages) - 1:
			self.api.set_active_page(pages.index(self.active_page) + 1)
			self.eventloop.emit(self.eventloop.PAGE_CHANGED)
			events.emit(events.PAGE_CHANGED, self)

	def previous_page(self):
		pages = self.get_pages()
		if pages.index(self.active_page):
			self.api.set_active_page(pages.index(self.active_page) - 1)
			self.eventloop.emit(self.eventloop.PAGE_CHANGED)
			events.emit(events.PAGE_CHANGED, self)

	def goto_page(self, index):
		pages = self.get_pages()
		current_index = pages.index(self.active_page)
		if index >= 0 and index <> current_index:
			self.api.set_active_page(index)
			self.eventloop.emit(self.eventloop.PAGE_CHANGED)
			events.emit(events.PAGE_CHANGED, self)

	def set_active_layer(self, page, layer_num=-1):
		self.active_layer = self.doc_presenter.methods.get_layer(page, layer_num)

	def get_editable_layers(self, page=None):
		if page is None: page = self.active_page
		layers = []
		for layer in self.methods.get_desktop_layers():
			if layer.properties[1]:layers.append(layer)
		for layer in page.childs:
			if layer.properties[1]:layers.append(layer)
		for layer in self.methods.get_master_layers():
			if layer.properties[1]:layers.append(layer)
		return layers

	def get_visible_layers(self, page=None):
		if page is None: page = self.active_page
		layers = []
		for layer in self.methods.get_desktop_layers():
			if layer.properties[0]:layers.append(layer)
		for layer in page.childs:
			if layer.properties[0]:layers.append(layer)
		for layer in self.methods.get_master_layers():
			if layer.properties[0]:layers.append(layer)
		return layers

	def get_page_size(self, page=None):
		if page is None:
			page = self.active_page
		w, h = page.page_format[1]
		return w, h
