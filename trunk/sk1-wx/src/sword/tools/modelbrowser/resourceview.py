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

from sword import _
from sword import dialogs
from sword.models.filelist import FileListModel
from sword.widgets.buttons import NavigationButton

class ResourceViewWidget(gtk.VBox):

	name = "Resource View"
	caption = _("Resource View")
	caption_label = None
	undo = []
	redo = []

	def __init__(self, app, presenter):
		gtk.VBox.__init__(self, False, 0)
		self.mw = app.mw
		self.app = app
		self.presenter = presenter

		self.root = self.presenter.doc_presenter.doc_dir

		self.current_dir = "" + self.root

		spacer = gtk.VBox()
		self.add(spacer)
		self.set_border_width(5)

		nav_panel = gtk.HBox()
		nav_panel.set_border_width(0)

		self.back_but = NavigationButton(gtk.STOCK_GO_BACK, _('Go Back'))
		nav_panel.pack_start(self.back_but, False)
		self.back_but.connect('clicked', self.action_back)

		self.up_but = NavigationButton(gtk.STOCK_GO_UP, _('Go Up'))
		nav_panel.pack_start(self.up_but, False)
		self.up_but.connect('clicked', self.action_up)

		self.forward_but = NavigationButton(gtk.STOCK_GO_FORWARD, _('Go Forward'))
		nav_panel.pack_start(self.forward_but, False)
		self.forward_but.connect('clicked', self.action_forward)

		self.home_but = NavigationButton(gtk.STOCK_HOME, _('Home directory'))
		nav_panel.pack_start(self.home_but, False)
		self.home_but.connect('clicked', self.action_home)

		separator = gtk.VSeparator()
		nav_panel.pack_start(separator, False, padding=2)

		self.refr_but = NavigationButton(gtk.STOCK_REFRESH, _('Refresh'))
		nav_panel.pack_start(self.refr_but, False)
		self.refr_but.connect('clicked', self.update_view)


		spacer.pack_start(nav_panel, False)

		self.listmodel = FileListModel()

		self.treeview = gtk.TreeView()

		self.column = gtk.TreeViewColumn()
		self.column.set_title(_('Log Entries'))
		render_pixbuf = gtk.CellRendererPixbuf()
		self.column.pack_start(render_pixbuf, expand=False)
		self.column.add_attribute(render_pixbuf, 'pixbuf', 0)
		render_text = gtk.CellRendererText()
		self.column.pack_start(render_text, expand=True)
		self.column.add_attribute(render_text, 'text', 1)
		self.treeview.append_column(self.column)

		self.treeview.connect('row-activated', self.open_file)

		self.scrolledwindow = gtk.ScrolledWindow()
		self.scrolledwindow.add(self.treeview)
		self.scrolledwindow.set_shadow_type(gtk.SHADOW_ETCHED_IN)
		self.scrolledwindow.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
		spacer.pack_end(self.scrolledwindow, True)

		self.treeview.set_model(self.listmodel)
		self.treeview.set_rules_hint(True)
		self.update_view()


	def open_file(self, treeview, path, column):
		model = treeview.get_model()
		pathname = os.path.abspath(model.get_pathname(path))
		if os.path.isdir(pathname):
			self.set_path(pathname)
		else:
			self.app.external_app_open(pathname)

	def set_path(self, pathname, undo=False):
		try:
			os.listdir(pathname)
		except:
			msg = _('Access error to')
			msg = "%s '%s'" % (msg, pathname)
			sec = sys.exc_info()[1].__str__()
			dialogs.msg_dialog(self.mw, self.app.appdata.app_name, msg,
							sec, gtk.MESSAGE_ERROR)
			return

		if undo:
			pass
		else:
			self.undo += [self.current_dir, ]
		self.current_dir = "" + pathname
		self.update_view()

	def update_view(self, *args):
		path = '' + self.current_dir
		if self.root:
			path = path.replace(self.root, '::')
		self.column.set_title(path)

		new_model = FileListModel(self.current_dir,
							[],
							True,
							self.root)
		self.treeview.set_model(new_model)

		if self.undo:
			self.back_but.set_sensitive(True)
		else:
			self.back_but.set_sensitive(False)

		if self.redo:
			self.forward_but.set_sensitive(True)
		else:
			self.forward_but.set_sensitive(False)

		self.home_but.set_sensitive(True)
		if self.current_dir == os.path.expanduser('~'):
			self.home_but.set_sensitive(False)
		if self.root and self.current_dir == self.root:
			self.home_but.set_sensitive(False)

		self.up_but.set_sensitive(True)
		if self.root:
			if self.current_dir == self.root:
				self.up_but.set_sensitive(False)
		else:
			if self.current_dir == os.path.abspath(os.path.join(self.current_dir, '..')):
				self.up_but.set_sensitive(False)

	def action_home(self, *args):
		if self.root:
			self.set_path(self.root)
		else:
			self.set_path(os.path.expanduser('~'))

	def action_up(self, *args):
		path = os.path.abspath(os.path.join(self.current_dir, '..'))
		self.set_path(path)

	def action_back(self, *args):
		if self.undo:
			self.redo.insert(0, self.current_dir)
			path = self.undo[-1]
			self.undo = self.undo[:-1]
			self.set_path(path, True)

	def action_forward(self, *args):
		if self.redo:
			path = self.redo[0]
			self.redo = self.redo[1:]
			self.set_path(path)
