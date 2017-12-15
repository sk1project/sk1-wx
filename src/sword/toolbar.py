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

class AppToolbar(gtk.Toolbar):

	def __init__(self, mw):
		gtk.Toolbar.__init__(self)
		self.mw = mw
		self.app = mw.app
		self.actions = self.app.actions

		self.set_style(gtk.TOOLBAR_ICONS)
		self.build()

	def create_entries(self):
		return [
				'NEW',
				None,
				'OPEN',
				'SAVE',
				'SAVE_AS',
				'CLOSE',
				None,
				'CUT',
				'COPY',
				'PASTE',
				'DELETE',
				None,
				'PREFERENCES',
			   ]

	def build(self):
		entries = self.create_entries()
		index = 0
		for entry in entries:
			if entry is None:
				button = gtk.SeparatorToolItem()
			else:
				action = self.actions[entry]
				button = action.create_tool_item()
			self.insert(button, index)
			index += 1
