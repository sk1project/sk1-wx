# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2013 by Igor E. Novikov
#
# 	This program is free software: you can redistribute it and/or modify
# 	it under the terms of the GNU General Public License as published by
# 	the Free Software Foundation, either version 3 of the License, or
# 	(at your option) any later version.
#
# 	This program is distributed in the hope that it will be useful,
# 	but WITHOUT ANY WARRANTY; without even the implied warranty of
# 	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# 	GNU General Public License for more details.
#
# 	You should have received a copy of the GNU General Public License
# 	along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os, sys
import webbrowser

from uc2 import uc2const
from uc2.utils.fs import path_unicode
from uc2.application import UCApplication

from wal import Application

from sk1 import _, config, events, modes, dialogs, appconst
from sk1 import app_plugins, app_actions
from sk1.app_conf import AppData
from sk1.app_history import AppHistoryManager
from sk1.app_insp import AppInspector
from sk1.app_proxy import AppProxy
from sk1.parts.mw import AppMainWindow
from sk1.parts.artprovider import create_artprovider
from sk1.app_cms import AppColorManager
from sk1.document import PD_Presenter
from sk1.clipboard import AppClipboard

class pdApplication(Application, UCApplication):

	appdata = None
	history = None

	actions = {}
	plugins = {}
	docs = []
	current_doc = None
	doc_counter = 0

	proxy = None
	insp = None
	mw = None
	default_cms = None
	cursors = None
	mdiarea = None
	plg_area = None

	def __init__(self, path):

		self.path = path

		Application.__init__(self)
		UCApplication.__init__(self, path)

		self.appdata = AppData(self)
		config.load(self.appdata.app_config)
		config.resource_dir = os.path.join(path_unicode(self.path), 'share')
		plg_dir = os.path.join(self.path, 'share', 'pd_plugins')
		custom_plg_dir = self.appdata.plugin_dir
		config.plugin_dirs = [plg_dir, custom_plg_dir]
		sys.path.insert(1, self.appdata.app_config)
		sys.path.insert(1, os.path.join(self.path, 'share'))

		self.history = AppHistoryManager(self)

		create_artprovider()
		self.cursors = modes.get_cursors()

		self.proxy = AppProxy(self)
		self.insp = AppInspector(self)
		self.plugins = app_plugins.scan_plugins(self)
		self.actions = app_actions.create_actions(self)

		self.mw = AppMainWindow(self)
		self.default_cms = AppColorManager(self)
		self.clipboard = AppClipboard(self)

		self.proxy.update()
		self.insp.update()

	def call_after(self, *args):
		if self.docs: return
		if config.new_doc_on_start: self.new();return
		events.emit(events.NO_DOCS)
		txt = _('To start create new document or open existing')
		events.emit(events.APP_STATUS, txt)

	def stub(self, *args):pass

	def get_new_docname(self):
		self.doc_counter += 1
		return _('Untitled') + ' ' + str(self.doc_counter)

	def set_current_doc(self, doc):
		self.current_doc = doc
		self.current_doc.set_title()
		events.emit(events.DOC_CHANGED, doc)
		msg = _('Document is changed')
		events.emit(events.APP_STATUS, msg)

	def new(self):
		doc = PD_Presenter(self)
		self.docs.append(doc)
		self.set_current_doc(doc)
		events.emit(events.APP_STATUS, _('New document created'))

	def open(self, doc_file='', silent=False):
		if not doc_file:
			doc_file = dialogs.get_open_file_name(self.mw, self, config.open_dir)
		if os.path.lexists(doc_file) and os.path.isfile(doc_file):
			try:
				doc = PD_Presenter(self, doc_file, silent)
			except:
				msg = _('Cannot open file')
				msg = "%s '%s'" % (msg, doc_file) + '\n'
				msg += _('The file may be corrupted or not supported format')
				dialogs.error_dialog(self.mw, self.appdata.app_name, msg)
				if config.print_stacktrace:
					print sys.exc_info()[1].__str__()
					print sys.exc_info()[2].__str__()
				return
			self.docs.append(doc)
			config.open_dir = str(os.path.dirname(doc_file))
			self.history.add_entry(doc_file)
			self.set_current_doc(doc)
			events.emit(events.APP_STATUS, _('Document opened'))

	def save(self, doc=''):
		if not doc:
			doc = self.current_doc
		if not doc.doc_file:
			return self.save_as()
		ext = os.path.splitext(self.current_doc.doc_file)[1]
		if not ext == "." + uc2const.FORMAT_EXTENSION[uc2const.SK2][0]:
			return self.save_as()
		if not os.path.lexists(os.path.dirname(self.current_doc.doc_file)):
			return self.save_as()

		try:
			doc.save()
			self.history.add_entry(self.current_doc.doc_file, appconst.SAVED)
			events.emit(events.DOC_SAVED, doc)
		except:
			msg = _('Cannot save file')
			msg = "%s '%s'" % (msg, self.current_doc.doc_file) + '\n'
			msg += _('Please check file write permissions')
			dialogs.error_dialog(self.mw, self.appdata.app_name, msg)
			if config.print_stacktrace:
				print sys.exc_info()[1].__str__()
				print sys.exc_info()[2].__str__()
			return False
		events.emit(events.APP_STATUS, _('Document saved'))
		return True

	def save_as(self):
		doc_file = '' + self.current_doc.doc_file
		if not doc_file:
			doc_file = '' + self.current_doc.doc_name
		if not os.path.splitext(doc_file)[1] == "." + \
					uc2const.FORMAT_EXTENSION[uc2const.SK2][0]:
			doc_file = os.path.splitext(doc_file)[0] + "." + \
					uc2const.FORMAT_EXTENSION[uc2const.SK2][0]
		if not os.path.lexists(os.path.dirname(doc_file)):
			doc_file = os.path.join(config.save_dir,
								os.path.basename(doc_file))
		doc_file = dialogs.get_save_file_name(self.mw, self, doc_file)
		if doc_file:
			old_file = self.current_doc.doc_file
			old_name = self.current_doc.doc_name
			self.current_doc.set_doc_file(doc_file)
			try:
				self.current_doc.save()
			except IOError:
				self.current_doc.set_doc_file(old_file, old_name)
				first = _('Cannot save document')
				msg = ("%s '%s'.") % (first, self.current_doc.doc_name) + '\n'
				msg += _('Please check file name and write permissions')
				dialogs.error_dialog(self.mw, self.appdata.app_name, msg)
				if config.print_stacktrace:
					print sys.exc_info()[1].__str__()
					print sys.exc_info()[2].__str__()
				return False
			config.save_dir = str(os.path.dirname(doc_file))
			self.history.add_entry(doc_file, appconst.SAVED)
			events.emit(events.DOC_SAVED, self.current_doc)
			events.emit(events.APP_STATUS, _('Document saved'))
			return True
		else:
			return False

	def save_selected(self):
		doc_file = '' + self.current_doc.doc_file
		if not doc_file:
			doc_file = '' + self.current_doc.doc_name
		if not os.path.splitext(doc_file)[1] == "." + \
					uc2const.FORMAT_EXTENSION[uc2const.SK2][0]:
			doc_file = os.path.splitext(doc_file)[0] + "." + \
					uc2const.FORMAT_EXTENSION[uc2const.SK2][0]
		if not os.path.lexists(os.path.dirname(doc_file)):
			doc_file = os.path.join(config.save_dir,
								os.path.basename(doc_file))
		doc_file = dialogs.get_save_file_name(self.mw, self, doc_file,
							_('Save selected objects only as...'))
		if doc_file:
			try:
				self.current_doc.save_selected(doc_file)
				self.history.add_entry(doc_file, appconst.SAVED)
			except:
				first = _('Cannot save document')
				msg = ("%s '%s'.") % (first, doc_file) + '\n'
				msg += _('Please check requested file format and write permissions')
				dialogs.error_dialog(self.mw, self.appdata.app_name, msg)
				if config.print_stacktrace:
					print sys.exc_info()[1].__str__()
					print sys.exc_info()[2].__str__()

	def save_all(self):
		for doc in self.docs:
			if self.insp.is_doc_not_saved(doc):
				self.save(doc)

	def close(self, doc=None):
		if not self.docs: return
		if doc is None: doc = self.current_doc
		if not doc == self.current_doc: self.set_current_doc(doc)

		if self.insp.is_doc_not_saved(doc):
			msg = _("Document '%s' has been modified.") % (doc.doc_name) + '\n'
			msg += _('Do you want to save your changes?')
			ret = dialogs.ync_dialog(self.mw, self.appdata.app_name, msg)

			if ret is None: return False
			if ret:
				if not self.save(): return False

		if doc in self.docs:
			self.docs.remove(doc)
			doc.close()
			events.emit(events.DOC_CLOSED)
			if not len(self.docs):
				self.current_doc = None
				events.emit(events.NO_DOCS)
				msg = _('To start create new or open existing document')
				events.emit(events.APP_STATUS, msg)
				self.mw.set_title()
			else:
				self.set_current_doc(self.docs[-1])
		return True

	def close_all(self):
		result = True
		if self.docs:
			while self.docs:
				result = self.close(self.docs[0])
				if not result: break
		return result

	def import_file(self):
		doc_file = dialogs.get_import_file_name(self.mw, self, config.import_dir)
		if os.path.lexists(doc_file) and os.path.isfile(doc_file):
			try:
				ret = self.current_doc.import_file(doc_file)
				if not ret:
					msg = _('Cannot import graphics from file:')
					msg = "%s\n'%s'" % (msg, doc_file) + '\n'
					msg += _('It seems the document is empty or contains unsupported objects.')
					dialogs.error_dialog(self.mw, self.appdata.app_name, msg)
				config.import_dir = str(os.path.dirname(doc_file))
			except:
				msg = _('Cannot import file')
				msg = "%s '%s'" % (msg, doc_file) + '\n'
				msg += _('The file may be corrupted or not supported format')
				dialogs.error_dialog(self.mw, self.appdata.app_name, msg)
				if config.print_stacktrace:
					print sys.exc_info()[1].__str__()
					print sys.exc_info()[2].__str__()


	def exit(self, *args):
		if not self.insp.is_any_doc_not_saved(): self.mw.Hide()
		if self.close_all():
			self.update_config()
			self.mw.Destroy()
			self.Exit()
			return True
		return False

	def update_config(self):
		config.resource_dir = ''
		w, h = self.mw.GetSize()
		config.mw_maximized = self.mw.IsMaximized()
		if self.mw.IsMaximized():
			w = config.mw_min_width
			h = config.mw_min_height
		config.mw_width = w
		config.mw_height = h
		config.save(self.appdata.app_config)

	def open_url(self, url):
		webbrowser.open_new(url)
