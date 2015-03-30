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

import sys, os
import traceback
import gtk

import uc2
from uc2.utils import system, fs
from uc2 import cms

from sword.app_conf import AppData
from sword import events
from sword import _, config
from sword import dialogs
from sword.proxy import AppProxy
from sword.actions import create_actions
from sword.inspector import DocumentInspector
from sword.presenter import SW_Presenter

from sword.mainwindow import MainWindow

class Application:

	"""Provides main SWord application instance."""

	proxy = None
	appdata = None
	mw = None
	generic_icons = {}

	current_doc = None
	docs = []
	doc_counter = 0

	def __init__(self, path):

		self.path = path

		self.default_cms = cms.ColorManager()

		self.appdata = AppData(self)
		config.load(self.appdata.app_config)
		config.save(self.appdata.app_config)
		config.resource_dir = os.path.join(self.path, 'share')

		self.accelgroup = gtk.AccelGroup()
		self.actiongroup = gtk.ActionGroup('BasicAction')
		self.proxy = AppProxy(self)
		self.inspector = DocumentInspector(self)

		self.actions = create_actions(self)
		self.mw = MainWindow(self)
		self.proxy.update_references()

	def run(self):
		events.emit(events.NO_DOCS)
		events.emit(events.APP_STATUS,
				_('To start create new or open existing document'))
		gtk.main()

	def exit(self):
		if not self.close_all():return False
		self.update_config()
		try:
			fs.xremove_dir(self.appdata.app_temp_dir)
		except:
			pass
		config.save(self.appdata.app_config)
		gtk.main_quit()
		return True

	def update_config(self):
		config.resource_dir = ''
		w, h = self.mw.get_size()
		state = self.mw.window.get_state()
		if state == gtk.gdk.WINDOW_STATE_MAXIMIZED:
			if config.os != system.MACOSX:
				config.mw_maximized = 1
		else:
			config.mw_maximized = 0

			config.mw_width = w
			config.mw_height = h

	def get_new_docname(self):
		self.doc_counter += 1
		return _('Untitled') + ' ' + str(self.doc_counter)

	def set_current_doc(self, doc):
		self.current_doc = doc
		events.emit(events.DOC_CHANGED, doc)

	def new(self):pass
#		doc = SW_Presenter(self)
#		self.docs.append(doc)
#		self.set_current_doc(doc)
#		events.emit(events.APP_STATUS, _('New document created'))

	def open(self, doc_file=''):
		if not doc_file:
			doc_file = dialogs.get_open_file_name(self.mw, self,
												config.open_dir)


		if os.path.lexists(doc_file) and os.path.isfile(doc_file):
			try:
				msg = _('Model creation for') + ' "%s" ' % (doc_file)
				uc2.events.emit(uc2.events.MESSAGES, uc2.msgconst.JOB, msg)

				doc = SW_Presenter(self, doc_file)
			except:
				details = sys.exc_info()[1].__str__() + '\n' + traceback.format_tb(sys.exc_info()[2])[0]
				msg = _('Cannot open file')
				msg = "%s '%s'" % (msg, doc_file)
				sec = _('The file may be corrupted or not supported format')

				uc2.events.emit(uc2.events.MESSAGES, uc2.msgconst.STOP, msg)

				dialogs.msg_dialog(self.mw, self.appdata.app_name, msg, sec, details)
				return
			self.docs.append(doc)
			self.set_current_doc(doc)
			config.open_dir = os.path.dirname(doc_file)
			events.emit(events.APP_STATUS, _('Document opened'))

	def load(self, pathname):
		msg = _('Request to open file')
		msg = "%s '%s'" % (msg, pathname)
		sec = _('The open operation will be implemented soon.')
		dialogs.msg_dialog(self.mw, self.appdata.app_name, msg,
						sec, gtk.MESSAGE_INFO)

	def save(self, doc=''):
		if not doc:
			doc = self.current_doc
		if not doc.doc_file:
			return self.save_as()
		ext = os.path.splitext(self.current_doc.doc_file)[1]
		if not ext[1:]:
			return self.save_as()
		if not os.path.lexists(os.path.dirname(self.current_doc.doc_file)):
			return self.save_as()

		try:
			msg = _('Model saving for') + ' "%s" ' % (doc.doc_file)
			uc2.events.emit(uc2.events.MESSAGES, uc2.msgconst.JOB, msg)

			doc.save()
			events.emit(events.DOC_SAVED, doc)
		except:
			details = sys.exc_info()[1].__str__() + sys.exc_info()[2].__str__()
			msg = _('Cannot save file')
			msg = "%s '%s'" % (msg, self.current_doc.doc_file)
			sec = _('Please check file write permissions')

			uc2.events.emit(uc2.events.MESSAGES, uc2.msgconst.STOP, msg)

			dialogs.msg_dialog(self.mw, self.appdata.app_name, msg, sec, details)
			return False
		events.emit(events.APP_STATUS, _('Document saved'))
		return True

	def save_as(self):
		doc_file = '' + self.current_doc.doc_file
		if not doc_file:
			doc_file = '' + self.current_doc.doc_name
		if not os.path.lexists(os.path.dirname(doc_file)):
			doc_file = os.path.join(config.save_dir,
								os.path.basename(doc_file))
		doc_file = dialogs.get_save_file_name(self.mw, self, doc_file)
		if doc_file:
			old_file = self.current_doc.doc_file
			old_name = self.current_doc.doc_name
			self.current_doc.set_doc_file(doc_file)
			try:
				msg = _('Model saving for') + ' "%s" ' % (doc_file)
				uc2.events.emit(uc2.events.MESSAGES, uc2.msgconst.JOB, msg)

				self.current_doc.save()
			except IOError:
				self.current_doc.set_doc_file(old_file, old_name)
				details = sys.exc_info()[1].__str__() + sys.exc_info()[2].__str__()
				first = _('Cannot save document')
				sec = _('Please check file name and write permissions')
				msg = ("%s '%s'.") % (first, self.current_doc.doc_name)

				uc2.events.emit(uc2.events.MESSAGES, uc2.msgconst.STOP, msg)

				dialogs.msg_dialog(self.mw, self.appdata.app_name, msg, sec, details)

				return False
			config.save_dir = os.path.dirname(doc_file)
			events.emit(events.APP_STATUS, _('Document saved'))
			return True
		else:
			return False

	def save_all(self):
		for doc in [] + self.docs:
			self.save(doc)

	def close(self, doc=None):
		if not self.docs:
			return
		if doc is None:
			doc = self.current_doc

		if not self.mw.nb.page_num(doc.docarea) == self.mw.nb.get_current_page():
			self.mw.set_active_tab(doc.docarea)
		if doc in self.docs:
			self.docs.remove(doc)
			doc.close()
			events.emit(events.DOC_CLOSED)
			if not len(self.docs):
				self.current_doc = None
				events.emit(events.NO_DOCS)
				msg = _('To start create new or open existing document')
				events.emit(events.APP_STATUS, msg)
		return True

	def close_all(self):
		result = True
		if self.docs:
			while self.docs:
				result = self.close(self.docs[0])
				if not result:
					break
		return result

	def open_url(self, url):
		import webbrowser
		webbrowser.open_new(url)

	def external_app_open(self, pathname):
		cmd = '' + config.ext_text_view
		ext = os.path.splitext(pathname)[1][1:]
		if ext in config.pseudomime.keys():
			cmd = '' + config.pseudomime[ext]
		cmd = cmd.replace('$file', pathname) + ' 2>/dev/null &'
		os.popen(cmd)

	def external_bineditor_open(self, pathname):
		cmd = '' + config.ext_text_view
		ext = os.path.splitext(pathname)[1][1:]
		cmd = '' + config.ext_binary_view
		cmd = cmd.replace('$file', pathname) + ' 2>/dev/null &'
		os.popen(cmd)
