# -*- coding: utf-8 -*-
#
#	Copyright (C) 2013 by Igor E. Novikov
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

import wx
from wal import HPanel, VPanel, ALL, EXPAND, VLine
from sk1.parts.plgtabpanel import PlgTabsPanel

class PlgArea(HPanel):

	app = None
	active_plg = None
	plugins = []
	container = None
	tabs = None

	def __init__(self, app, parent):
		self.app = app
		HPanel.__init__(self, parent)
		line = VLine(self)
		self.add(line, 0, ALL | EXPAND)
		self.container = VPanel(self)
		self.add(self.container, 1, ALL | EXPAND)
		self.tabs = PlgTabsPanel(app, self)
		self.add(self.tabs, 0, ALL | EXPAND)
		self.Layout()

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

	def show_plugin(self, pid):
		if not pid: return
		if self.active_plg and pid == self.active_plg.pid: return
		self.app.mdiarea.show_plugin_area()
		item = self.check_pid(pid)
		if self.active_plg:
			self.active_plg.hide()
		if not item:
			item = self.load_plugin(pid)
			self.container.add(item.panel, 1, ALL | EXPAND)
			self.tabs.plg_tabs.add_new_tab(item)
		else:
			self.tabs.plg_tabs.set_active(item)
		self.active_plg = item
		self.active_plg.show()
		self.container.Layout()
		self.Layout()

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
