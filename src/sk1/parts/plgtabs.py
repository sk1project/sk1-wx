# -*- coding: utf-8 -*-
#
#  Copyright (C) 2018 by Igor E. Novikov
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import wal


class PlgnTabPanel(wal.VTabPanel):

    def __init__(self, app, parent):
        self.app = app
        self.plgarea = parent
        wal.VTabPanel.__init__(self, parent)

    def add_new_tab(self, plugin):
        return wal.VTabPanel.add_new_tab(self, PlgnTab(self, plugin))

    def set_active(self, plugin):
        wal.VTabPanel.set_active(self, self.find_plugin_tab(plugin))

    def remove_tab(self, plugin):
        wal.VTabPanel.remove_tab(self, self.find_plugin_tab(plugin))

    def find_plugin_tab(self, plugin):
        for tab in self.tabs:
            if plugin == tab.plugin:
                return tab


class PlgnTab(wal.VTab):
    plugin = None
    icon = None

    def __init__(self, parent, plugin, active=True):
        self.plugin = plugin
        self.icon = plugin.icon
        self.text = self.plugin.name
        wal.VTab.__init__(self, parent, active)

    def close(self):
        self.mouse_leaved_tab()
        self.parent.refresh()
        self.parent.plgarea.close_plugin(self.plugin.pid)

    def mouse_left_down(self, point):
        if wal.VTab.mouse_left_down(self, point):
            if not self.active:
                self.parent.plgarea.show_plugin(self.plugin.pid)