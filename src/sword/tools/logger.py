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

import gtk

from uc2 import events

from sword import _, config
from sword.widgets.captions import TabIconCaption
from sword.widgets.buttons import NavigationButton

log_icons = {
0:gtk.STOCK_EXECUTE,
1:gtk.STOCK_OK,
2:gtk.STOCK_INFO,
3:gtk.STOCK_DIALOG_WARNING,
4:gtk.STOCK_DIALOG_ERROR,
5:gtk.STOCK_STOP,
}

class Logger(gtk.VBox):

	name = "Logger"
	caption = _("Logger")
	caption_label = None
	logs = []
	connected = False


	def __init__(self, app):

		gtk.VBox.__init__(self)
		self.app = app
		self.logs = []
		self.icon_theme = gtk.icon_theme_get_default()
		self.caption_label = TabIconCaption(gtk.STOCK_MISSING_IMAGE, self.caption)

		spacer = gtk.VBox()
		self.add(spacer)
		self.set_border_width(5)

		nav_panel = gtk.HBox()
		nav_panel.set_border_width(0)

		self.rec_but = NavigationButton(gtk.STOCK_MEDIA_RECORD, _('Start recording'))
		nav_panel.pack_start(self.rec_but, False)
		self.rec_but.connect('clicked', self.start_rec)

		self.stop_but = NavigationButton(gtk.STOCK_MEDIA_STOP, _('Stop recording'))
		nav_panel.pack_start(self.stop_but, False)
		self.stop_but.connect('clicked', self.stop_rec)

		separator = gtk.VSeparator()
		nav_panel.pack_start(separator, False)

		self.clear_but = NavigationButton(gtk.STOCK_CLEAR, _('Clear logs'))
		nav_panel.pack_start(self.clear_but, False)
		self.clear_but.connect('clicked', self.clear_logs)

		spacer.pack_start(nav_panel, False)

		self.treeview = gtk.TreeView()

		self.scrolledwindow = gtk.ScrolledWindow()
		self.scrolledwindow.add(self.treeview)
		self.scrolledwindow.set_shadow_type(gtk.SHADOW_ETCHED_IN)
		self.scrolledwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		spacer.pack_end(self.scrolledwindow, True)

		#-------TreeList--------------
		col = gtk.TreeViewColumn()
		col.set_title(_('Log Entries'))
		render_pixbuf = gtk.CellRendererPixbuf()
		col.pack_start(render_pixbuf, expand=False)
		col.add_attribute(render_pixbuf, 'pixbuf', 0)
		render_text = gtk.CellRendererText()
		col.pack_start(render_text, expand=True)
		col.add_attribute(render_text, 'text', 1)
		self.treeview.append_column(col)
		#-----------------------------
		self.treeview.set_rules_hint(True)

		self.show_all()
		self.update_view()

	def update_view(self):
		if config.log_start_record:
			self.rec_but.set_sensitive(False)
			self.stop_but.set_sensitive(True)
			if not self.connected:
				self.set_listener(True)
		else:
			self.rec_but.set_sensitive(True)
			self.stop_but.set_sensitive(False)
			if self.connected:
				self.set_listener(False)

		store = gtk.ListStore(gtk.gdk.Pixbuf, str)
		for log in self.logs:
			log_type, log_text = log
			store.append((self.icon_theme.load_icon(log_icons[log_type], 16, 0), log_text))

		self.treeview.set_model(store)

	def stop_rec(self, *args):
		config.log_start_record = False
		self.update_view()

	def start_rec(self, *args):
		config.log_start_record = True
		self.update_view()

	def clear_logs(self, *args):
		self.logs = []
		self.update_view()

	def set_listener(self, start=True):
		if start:
			events.connect(events.MESSAGES, self.listener)
			self.connected = True
		else:
			events.disconnect(events.MESSAGES, self.listener)
			self.connected = False

	def listener(self, *args):
		args, = args
		self.logs.append(args)
		self.update_view()
