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

import wal

from sk1.parts.plgtabpanel import PlgTabsPanel

class PlgArea(wal.HPanel):

	app = None
	active_plg = None
	plugins = []
	container = None
	tabs = None

	def __init__(self, app, parent):
		self.app = app
		wal.HPanel.__init__(self, parent)
		self.pack(wal.VLine(self), fill=True)
		self.container = wal.VPanel(self)
		self.pack(self.container, expand=True, fill=True)
		self.tabs = PlgTabsPanel(app, self)
		self.pack(self.tabs, fill=True)
		self.layout()

	def check_pid(self, pid):
		for item in self.plugins:
			if item.pid == pid:
				return item
		return None

	def load_plugin(self, pid):
		item = self.app.plugins[pid]
		item.activate()
		self.plugins.append(item)
		return item

	def show_plugin(self, pid, *args):
		if not pid: return
		if self.active_plg and pid == self.active_plg.pid:
			self.active_plg.show_signal(*args)
			return
		self.app.mdiarea.show_plugin_area()
		item = self.check_pid(pid)
		if self.active_plg:
			self.active_plg.hide()
		if not item:
			item = self.load_plugin(pid)
			self.container.pack(item.panel, expand=True, fill=True)
			self.tabs.plg_tabs.add_new_tab(item)
			item.panel.layout()
		else:
			self.tabs.plg_tabs.set_active(item)
		self.active_plg = item
		self.active_plg.show(*args)
		self.layout()
		self.container.layout()
		self.active_plg.panel.refresh()

	def close_plugin(self, pid):
		item = self.check_pid(pid)
		if not item: return
		self.tabs.plg_tabs.remove_tab(item)
		self.plugins.remove(item)
		self.container.box.Detach(item.panel)
		item.hide()
		if self.active_plg == item:
			self.active_plg = None
			if self.plugins:
				self.show_plugin(self.plugins[-1].pid)
			else:
				self.app.mdiarea.show_plugin_area(False)
