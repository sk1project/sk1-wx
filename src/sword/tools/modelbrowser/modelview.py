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

from uc2 import uc2const

from sword import _
from sword.models.modeltreelist import ObjectTreeModel
from sword.widgets.buttons import ImageButton, ActionButton

class ModelViewWidget(gtk.VBox):

	name = "Model View"
	caption = _("Model View")
	undo = []
	redo = []

	treeview = None
	listmodel = None

	action_flag = False
	current_path = ''


	def __init__(self, app, presenter):
		gtk.VBox.__init__(self, False, 0)
		self.mw = app.mw
		self.app = app
		self.presenter = presenter
		model_cid = self.presenter.doc_presenter.cid
		model_name = uc2const.FORMAT_EXTENSION[model_cid][0].upper()


		spacer = gtk.VBox()
		self.add(spacer)
		self.set_border_width(5)

		nav_panel = gtk.HBox()
		nav_panel.set_border_width(0)


		self.back_but = ActionButton(self.app.actions['BACKWARD'])
		nav_panel.pack_start(self.back_but, False)

		self.forward_but = ActionButton(self.app.actions['FORWARD'])
		nav_panel.pack_start(self.forward_but, False)

		self.home_but = ActionButton(self.app.actions['ROOT'])
		nav_panel.pack_start(self.home_but, False)

		separator = gtk.VSeparator()
		nav_panel.pack_start(separator, False, padding=2)

		self.refr_but = ActionButton(self.app.actions['REFRESH_MODEL'])
		nav_panel.pack_start(self.refr_but, False)


		self.expand_but = ImageButton('expand.png', _('Expand All'))
		nav_panel.pack_end(self.expand_but, False)
		self.expand_but.connect('clicked', self.expand_all)

		self.collapse_but = ImageButton('collapse.png', _('Collapse All'))
		nav_panel.pack_end(self.collapse_but, False)
		self.collapse_but.connect('clicked', self.collapse_all)

		spacer.pack_start(nav_panel, False)

		self.listmodel = ObjectTreeModel(self.presenter.doc_presenter.model)

		self.treeview = gtk.TreeView()

		self.column = gtk.TreeViewColumn()
		self.column.set_title(model_name + ' ' + _('File Format Model'))
		render_pixbuf = gtk.CellRendererPixbuf()
		self.column.pack_start(render_pixbuf, expand=False)
		self.column.add_attribute(render_pixbuf, 'pixbuf', 0)
		render_text = gtk.CellRendererText()
		self.column.pack_start(render_text, expand=True)
		self.column.add_attribute(render_text, 'text', 1)
		self.treeview.append_column(self.column)

		self.column1 = gtk.TreeViewColumn()
		render_text = gtk.CellRendererText()
		self.column1.pack_start(render_text, expand=False)
		self.column1.add_attribute(render_text, 'text', 2)
		self.column1.add_attribute(render_text, 'foreground', 3)
		self.treeview.append_column(self.column1)

		self.treeview.connect('cursor-changed', self.view_object)

		self.scrolledwindow = gtk.ScrolledWindow()
		self.scrolledwindow.add(self.treeview)
		self.scrolledwindow.set_shadow_type(gtk.SHADOW_ETCHED_IN)
		self.scrolledwindow.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
		spacer.pack_end(self.scrolledwindow, True)

		self.treeview.set_model(self.listmodel)
		self.treeview.set_rules_hint(True)
		self.treeview.set_enable_tree_lines(True)
		eventloop = self.presenter.eventloop
		eventloop.connect(eventloop.SELECTION_CHANGED, self.reflect_selection)
		self.update_view()

	def update_view(self):
		self.presenter.selection.clear_history()
		self.presenter.selection.selected = []
		self.listmodel = ObjectTreeModel(self.presenter.doc_presenter.model)
		self.treeview.set_model(self.listmodel)
		self.expand_all()

	def view_object(self, *args):
		if self.action_flag:
			self.action_flag = False
			return

		path = self.treeview.get_cursor()[0]

		if not self.current_path == path.__str__():
			self.current_path = path.__str__()
		else:
			return

		obj = self.listmodel.get_obj_by_path(path)
		self.action_flag = True
		self.presenter.selection.set_selection(obj, path)

	def collapse_all(self, *args):
		self.treeview.collapse_all()

	def expand_all(self, *args):
		self.treeview.expand_all()

	def reflect_selection(self, *args):
		self.action_flag = True
		self.treeview.set_cursor(args[0][0][1])
