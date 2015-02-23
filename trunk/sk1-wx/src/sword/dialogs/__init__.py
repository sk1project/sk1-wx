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
import gtk, gobject

from uc2 import uc2const
from uc2.formats import data
from uc2.utils.fs import expanduser_unicode
from uc2 import events

from sword import _, config

def about_dialog(parent):
	from license import LICENSE
	authors = [
		"\nIgor E. Novikov (SWord, Gtk+ version; CDR Explorer, Tk version)\n\
		<igor.e.novikov@gmail.com>",
		]

	about = gtk.AboutDialog()
	about.set_property('window-position', gtk.WIN_POS_CENTER)
	about.set_icon(parent.get_icon())

	about.set_program_name("")
	logo = os.path.join(config.resource_dir, 'splash.png')
	about.set_logo(gtk.gdk.pixbuf_new_from_file(logo))
	about.set_authors(authors)
	about.set_license(LICENSE)

	about.run()
	about.destroy()

def msg_dialog(parent, title, text, seconary_text='', details='',
			dlg_type=gtk.MESSAGE_ERROR):
	dialog = gtk.MessageDialog(parent,
					flags=gtk.DIALOG_MODAL,
					type=dlg_type,
					buttons=gtk.BUTTONS_OK,
					message_format=text)
	if seconary_text:
		dialog.format_secondary_text(seconary_text)

	if details:
		expander = gtk.expander_new_with_mnemonic("_Additional details")

		text_buffer = gtk.TextBuffer()
		text_buffer.set_text(details)
		editor = gtk.TextView(text_buffer);
		editor.set_editable(False)
		editor.set_wrap_mode(True)

		sw = gtk.ScrolledWindow()
		sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
		sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		sw.add(editor)

		expander.add(sw)
		dialog.vbox.pack_start(expander, True)
		expander.show_all()

	dialog.set_title(title)
	dialog.run()
	dialog.destroy()

def _get_open_fiters():
	result = []
	descr = uc2const.FORMAT_DESCRIPTION
	ext = uc2const.FORMAT_EXTENSION
	items = [] + data.LOADER_FORMATS + data.EXPERIMENTAL_LOADERS

	for item in items:
		filter = gtk.FileFilter()
		filter.set_name(descr[item])
		for extension in ext[item]:
			filter.add_pattern('*.' + extension)
			filter.add_pattern('*.' + extension.upper())
		result.append(filter)

	filter = gtk.FileFilter()
	filter.set_name(_('All files'))
	filter.add_pattern('*')
	result = [filter] + result

	filter = gtk.FileFilter()
	filter.set_name(_('All supported formats'))
	for item in items:
		for extension in ext[item]:
			filter.add_pattern('*.' + extension)
			filter.add_pattern('*.' + extension.upper())
	result = [filter] + result

	return result

def get_open_file_name(parent, app, start_dir):
	result = ''
	dialog = gtk.FileChooserDialog(_('Open file'),
				parent,
				gtk.FILE_CHOOSER_ACTION_OPEN,
				(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
					gtk.STOCK_OPEN, gtk.RESPONSE_OK))

	dialog.set_default_response(gtk.RESPONSE_OK)
	start_dir = expanduser_unicode(start_dir)
	dialog.set_current_folder(start_dir)

	for filter in _get_open_fiters():
		dialog.add_filter(filter)

	ret = dialog.run()
	if not ret == gtk.RESPONSE_CANCEL:
		result = dialog.get_filename()
	dialog.destroy()
	if result is None: result = ''
	return result

def _get_save_fiters():
	result = []
	descr = uc2const.FORMAT_DESCRIPTION
	ext = uc2const.FORMAT_EXTENSION
	items = [] + data.SAVER_FORMATS + data.EXPERIMENTAL_SAVERS

	for item in items:
		filter = gtk.FileFilter()
		filter.set_name(descr[item])
		for extension in ext[item]:
			filter.add_pattern('*.' + extension)
			filter.add_pattern('*.' + extension.upper())
		result.append(filter)

	filter = gtk.FileFilter()
	filter.set_name(_('All supported formats'))
	for item in items:
		for extension in ext[item]:
			filter.add_pattern('*.' + extension)
			filter.add_pattern('*.' + extension.upper())
	result = [filter] + result

	return result

def get_save_file_name(parent, app, path):
	result = ''
	dialog = gtk.FileChooserDialog(_('Save file As...'),
				parent,
				gtk.FILE_CHOOSER_ACTION_SAVE,
				(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
					gtk.STOCK_SAVE, gtk.RESPONSE_OK))
	dialog.set_do_overwrite_confirmation(True)

	dialog.set_default_response(gtk.RESPONSE_OK)
	path = expanduser_unicode(path)

	doc_folder = os.path.dirname(path)
	dialog.set_current_folder(doc_folder)

	doc_name = os.path.basename(path)
	dialog.set_current_name(doc_name)

	for filter in _get_save_fiters():
		dialog.add_filter(filter)

	ret = dialog.run()
	if not ret == gtk.RESPONSE_CANCEL:
		result = dialog.get_filename()
	dialog.destroy()
	if result is None: result = ''
	return result


class ProgressDialog(gtk.Dialog):

	error_info = None

	def __init__(self, caption, parent):
		self.caption = caption

		gtk.Dialog.__init__(self, caption,
                   parent,
                   gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                   (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))
		self.set_resizable(True)
		self.set_size_request(350, -1)
		self.set_resizable(False)

		self.vbox.set_border_width(10)

		self.label = gtk.Label('')
		self.vbox.pack_start(self.label, True, False, 5)
		self.progress_bar = gtk.ProgressBar()
		self.vbox.pack_start(self.progress_bar, False, False, 10)

		self.vbox.show_all()

		self.timer = gobject.timeout_add(100, self.progress_timeout)
		self.flag = False
		self.result = None

	def progress_timeout(self):
		if not self.flag:
			self.flag = True
			try:
				self.result = self.executable(*self.args)
			except:
				self.result = None
				self.error_info = sys.exc_info()

			self.progress_bar.set_text('100 %')
			self.progress_bar.set_fraction(1.0)
			while gtk.events_pending():
				gtk.main_iteration()

			self.response(gtk.RESPONSE_OK)

	def listener(self, *args):
		val = round(args[0][1], 2)
		info = args[0][0]
		self.label.set_label(info)
		self.progress_bar.set_text('%d %%' % (val * 100.0))
		if val > 1.0:val = 1.0
		if val < 0.0:val = 0.0
		self.progress_bar.set_fraction(val)
		while gtk.events_pending():
			gtk.main_iteration()

	def run(self, executable, args):
		events.connect(events.FILTER_INFO, self.listener)
		self.progress_bar.set_text('0 %')
		self.progress_bar.set_fraction(0.0)
		while gtk.events_pending():
			gtk.main_iteration()
		self.executable = executable
		self.args = args
		return gtk.Dialog.run(self)


	def destroy(self):
		events.disconnect(events.FILTER_INFO, self.listener)
		gobject.source_remove(self.timer)
		self.timer = 0
		gtk.Dialog.destroy(self)
