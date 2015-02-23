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

import os

from sword import _, dialogs, config, events
from sword.dialogs import prefs

class AppProxy:

	app = None
	mw = None

	def __init__(self, app):
		self.app = app

	def update_references(self):
		self.mw = self.app.mw

	def exit(self, *args):
		self.app.exit()

	def new(self, *args):
		self.app.new()

	def open(self, *args):
		self.app.open()

	def save(self, *args):
		self.app.save()

	def save_as(self, *args):
		self.app.save_as()

	def save_all(self, *args):
		self.app.save_all()

	def close(self, *args):
		self.app.close()

	def close_all(self, *args):
		self.app.close_all()

	def report_bug(self, *args):
		self.app.open_url('http://www.sk1project.org/contact.php')

	def project_website(self, *args):
		self.app.open_url('http://www.sk1project.org/')

	def project_forum(self, *args):
		self.app.open_url('http://www.sk1project.org/forum/index.php')

	def about(self, *args):
		dialogs.about_dialog(self.mw)

	def prefs(self, *args):
		prefs.get_prefs_dialog(self.app)

	def cut(self, *args):self._edit_stub()
	def copy(self, *args):self._edit_stub()
	def paste(self, *args):self._edit_stub()
	def delete(self, *args):self._edit_stub()

	def _edit_stub(self):
		msg = _('Model editor is not found for ')
		msg = "%s '%s'" % (msg, self.app.current_doc.doc_file)
		sec = _('Install model editor and try again.')
		dialogs.msg_dialog(self.mw, self.app.appdata.app_name, msg, sec)

	def backward_object(self, *args):
		self.app.current_doc.selection.back_action()

	def forward_object(self, *args):
		self.app.current_doc.selection.forward_action()

	def root_object(self, *args):
		self.app.current_doc.selection.set_root()

	def clear_history(self, *args):
		self.app.current_doc.selection.clear_history()

	def refresh_object(self, *args):
		eventloop = self.app.current_doc.eventloop
		selection = self.app.current_doc.selection
		eventloop.emit(eventloop.SELECTION_CHANGED, selection.selected)
		events.emit(events.SELECTION_CHANGED, selection.selected)

	def edit_object(self, *args):
		obj = self.app.current_doc.docarea.objectbrowser.visualizer.viewer.current_obj
		filename = 'chunk[%s]' % (str(obj).split(' at ')[1][:-1])
		filename = os.path.join(self.app.appdata.app_temp_dir, filename)
		file = open(filename, 'wb')
		file.write(obj.chunk)
		file.close()
		self.app.external_bineditor_open(filename)
		eventloop = self.app.current_doc.eventloop
		selection = self.app.current_doc.selection
		eventloop.emit(eventloop.SELECTION_CHANGED, selection.selected)
		events.emit(events.SELECTION_CHANGED, selection.selected)

	def update_object(self, *args):
		obj = self.app.current_doc.docarea.objectbrowser.visualizer.viewer.current_obj
		filename = 'chunk[%s]' % (str(obj).split(' at ')[1][:-1])
		filename = os.path.join(self.app.appdata.app_temp_dir, filename)
		if os.path.lexists(filename):
			try:
				file = open(filename, 'rb')
				obj.chunk = file.read()
				file.close()
				os.remove(filename)
			except:
				pass
		eventloop = self.app.current_doc.eventloop
		selection = self.app.current_doc.selection
		eventloop.emit(eventloop.SELECTION_CHANGED, selection.selected)
		events.emit(events.SELECTION_CHANGED, selection.selected)

	def refresh_model(self, *args):
		self.app.current_doc.docarea.modelbrowser.modeltree.update_view()
		self.app.current_doc.selection.set_root()

	def copy_to_compare(self, *args):pass
	def copy_to_clip(self, *args):pass



	def stub(self, *args):pass
