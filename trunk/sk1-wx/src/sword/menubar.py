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

import types
import gtk

from sword import _

class AppMenubar(gtk.MenuBar):

	def __init__(self, mw):
		gtk.MenuBar.__init__(self)
		self.mw = mw
		self.app = mw.app
		self.actions = self.app.actions

		#----FILE MENU
		self.file_item, self.file_menu = self.create_menu(_("_File"))
		items = ['NEW',
				 None,
				 'OPEN',
				 'SAVE',
				 'SAVE_AS',
				 'SAVE_ALL',
				 None,
				 'CLOSE',
				 'CLOSE_ALL',
				 None,
				 'QUIT'
		]
		self.add_items(self.file_menu, items)

		#----EDIT MENU
		self.edit_item, self.edit_menu = self.create_menu(_("_Edit"))
		items = ['CUT',
				 'COPY',
				 'PASTE',
				 'DELETE',
				 None,
				 'PREFERENCES'
		]
		self.add_items(self.edit_menu, items)

		#----VIEW MENU
		self.view_item, self.view_menu = self.create_menu(_("_View"))
		items = ['BACKWARD',
				 'FORWARD',
				 'ROOT',
				 None,
				 'CLEAR_HISTORY',
				 None,
				 'REFRESH_OBJ',
				 'REFRESH_MODEL',
		]
		self.add_items(self.view_menu, items)

		#----TOOLS MENU
		self.tools_item, self.tools_menu = self.create_menu(_("_Tools"))
		items = ['ABOUT',
		]
		self.add_items(self.tools_menu, items)

		#----HELP MENU
		self.help_item, self.help_menu = self.create_menu(_("_Help"))
		items = ['REPORT_BUG',
				None,
				'PROJECT_WEBSITE',
				'PROJECT_FORUM',
				None,
				'ABOUT',
		]
		self.add_items(self.help_menu, items)

		self.append(self.file_item)
		self.append(self.edit_item)
		self.append(self.view_item)
#		self.append(self.tools_item)
		self.append(self.help_item)

	def create_menu(self, text):
		menu = gtk.Menu()
		item = gtk.MenuItem(text)
		item.set_submenu(menu)
		return item, menu

	def add_items(self, parent, items):
		for item in items:
			if item is None:
				parent.append(gtk.SeparatorMenuItem())
			elif type(item)is types.TupleType:
				action = self.actions[item[0]]
				menuitem = gtk.CheckMenuItem(action.tooltip)
				action.connect_proxy(menuitem)
				action.menuitem = menuitem
				menuitem.set_active(False)
				parent.append(menuitem)
			else:
				action = self.actions[item]
				menuitem = action.create_menu_item()
				action.menuitem = menuitem
				parent.append(menuitem)
