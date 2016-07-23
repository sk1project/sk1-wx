# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2015 by Igor E. Novikov
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

from sk1 import _, config
from sk1.resources import icons
from generic import RootItem
from prefs_general import GeneralPrefs
from prefs_palettes import PalettesPrefs
from prefs_cms import CMSPrefs
from prefs_ruler import RulersPrefs
from templates import GridPrefs
from prefs_fonts import FontPrefs

PREFS_APP = [GeneralPrefs, CMSPrefs, RulersPrefs, PalettesPrefs, FontPrefs]
PREFS_DOC = [GridPrefs, ]

class PrefsAppItem(RootItem):

	pid = 'Application'
	name = _('Application')
	icon_id = icons.SK1_ICON16

	def __init__(self, data=[]):
		RootItem.__init__(self, data)

class PrefsDocItem(RootItem):

	pid = 'NewDocument'
	name = _('New document')
	icon_id = icons.PD_NEW

	def __init__(self, data=[]):
		RootItem.__init__(self, data)


PREFS_DATA = []

class PrefsDialog(wal.OkCancelDialog):

	current_plugin = None

	def __init__(self, parent, title, pid=''):
		self.app = parent.app
		size = config.prefs_dlg_size
		wal.OkCancelDialog.__init__(self, parent, title, size, resizable=True)
		self.set_minsize(config.prefs_dlg_minsize)
		if not pid: pid = 'General'
		self.tree.set_item_by_reference(self.get_plugin_by_pid(pid))

	def build(self):
		self.splitter = wal.Splitter(self.panel)
		self.panel.pack(self.splitter, expand=True, fill=True)
		if not PREFS_DATA:
			PREFS_DATA.append(PrefsAppItem(PREFS_APP))
#			PREFS_DATA.append(PrefsDocItem(PREFS_DOC))
			for item in PREFS_DATA:
				item.init_prefs(self.app, self)
		self.tree = wal.TreeWidget(self.splitter, data=PREFS_DATA,
								on_select=self.on_select)
		self.container = wal.HPanel(self.splitter)
		self.splitter.split_vertically(self.tree, self.container, 200)
		self.splitter.set_min_size(150)
		if not wal.is_msw(): self.tree.set_indent(5)
		self.tree.expand_all()

	def set_dialog_buttons(self):
		wal.OkCancelDialog.set_dialog_buttons(self)
		title = _('Restore defaults')
		self.redo_btn = wal.Button(self.left_button_box, title,
								onclick=self.restore_defaults)
		self.left_button_box.pack(self.redo_btn)

	def on_select(self, plugin):
		if not self.current_plugin == plugin and plugin.leaf:
			if self.current_plugin:
				self.container.remove(self.current_plugin)
				self.current_plugin.hide()
			self.container.pack(plugin, fill=True, expand=True, padding=5)
			self.current_plugin = plugin
			if not self.current_plugin.built:
				self.current_plugin.build()
				self.current_plugin.layout()
			self.current_plugin.show()
			self.container.layout()

	def get_plugin_by_pid(self, pid):
		ret = None
		plugins = []
		for item in PREFS_DATA:
			plugins += item.childs
		for item in plugins:
			if item.pid == pid:
				ret = item
				break
		return ret

	def apply_changes(self):
		plugins = []
		for item in PREFS_DATA:
			plugins += item.childs
		for item in plugins:
			if item.built:
				item.apply_changes()

	def restore_defaults(self):
		if self.current_plugin:
			self.current_plugin.restore_defaults()

	def show(self):
		if self.show_modal() == wal.BUTTON_OK:
			self.apply_changes()
		if wal.is_unity_16_04():
			w, h = self.get_size()
			h -= 28
			if h < config.prefs_dlg_minsize[1]:
				h = config.prefs_dlg_minsize[1]
			config.prefs_dlg_size = (w, h)
		else:
			config.prefs_dlg_size = self.get_size()
		self.destroy()

def get_prefs_dialog(parent, pid=''):
	dlg = PrefsDialog(parent, _("sK1 Preferences"), pid)
	dlg.show()
#	PREFS_DATA.remove(PREFS_DATA[1])
	PREFS_DATA.remove(PREFS_DATA[0])
