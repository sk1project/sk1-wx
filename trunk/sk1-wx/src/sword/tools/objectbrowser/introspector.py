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
import pango

from sword import _
from sword.models.fieldlist import FieldListModel

class Introspector(gtk.TextView):

	def __init__(self, app, presenter):

		self.app = app
		self.presenter = presenter

		self.tb = gtk.TextBuffer()
		gtk.TextView.__init__(self, self.tb)
		self.set_tags()
		self.set_editable(False)
		self.set_indent(10)

		eventloop = self.presenter.eventloop
		eventloop.connect(eventloop.SELECTION_CHANGED, self.reflect_selection)


	def reflect_selection(self, *args):
		obj = args[0][0][0]
		self.tb.set_text('')
		self.iter = self.tb.get_iter_at_offset(0)

		self.show_header(_("Object "))
		self.show_header_bold(obj.resolve()[1] + "\n")
		self.show_subheader(str(obj) + '\n')
		if obj.__doc__:
			self.show_pydoc(obj.__doc__)

		self.new_line()
		self.show_subheader(_('Object fields table:') + "\n\n")

		anchor = self.tb.create_child_anchor(self.iter)
		self.add_child_at_anchor(ObjectFieldTab(obj), anchor)

		self.show_subheader(' \n')


	def new_line(self, text=''):
		self.tb.insert(self.iter, '\n' + text)

	def show_header_bold(self, text):
		self.tb.insert_with_tags_by_name(self.iter, text, "header-bold")

	def show_header(self, text):
		self.tb.insert_with_tags_by_name(self.iter, text, "header")

	def show_subheader(self, text):
		self.tb.insert_with_tags_by_name(self.iter, text, "subheader")

	def show_pydoc(self, text):
		self.tb.insert_with_tags_by_name(self.iter, text, "pydoc")


	def set_tags(self):
		self.tb.create_tag("header-bold",
                    weight=pango.WEIGHT_BOLD,
                    size=15 * pango.SCALE)
		self.tb.create_tag("header",
                    weight=pango.WEIGHT_NORMAL,
                    size=15 * pango.SCALE)
		self.tb.create_tag("subheader",
                    weight=pango.WEIGHT_BOLD,
                    size=10 * pango.SCALE)
		self.tb.create_tag("pydoc",
                    weight=pango.WEIGHT_NORMAL,
                    size=9 * pango.SCALE)


class ObjectFieldTab(gtk.ScrolledWindow):

	def __init__(self, obj):
		gtk.ScrolledWindow.__init__(self)

		self.treeview = gtk.TreeView()

		self.set_shadow_type(gtk.SHADOW_ETCHED_IN)
		self.set_policy(gtk.POLICY_NEVER, gtk.POLICY_NEVER)

		self.listmodel = FieldListModel(obj)

		self.column = gtk.TreeViewColumn()
		self.column.set_title(_('Field'))
		render_text = gtk.CellRendererText()
		self.column.pack_start(render_text, expand=True)
		self.column.add_attribute(render_text, 'text', 0)
		self.treeview.append_column(self.column)

		self.column1 = gtk.TreeViewColumn()
		self.column1.set_title(_('Value'))
		render_text = gtk.CellRendererText()
		self.column1.pack_start(render_text, expand=True)
		self.column1.add_attribute(render_text, 'text', 1)
		self.treeview.append_column(self.column1)

		self.add(self.treeview)

		self.treeview.set_model(self.listmodel)
		self.treeview.set_rules_hint(True)
		self.show_all()
		self.treeview.expand_all()
