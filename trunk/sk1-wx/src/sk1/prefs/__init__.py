# -*- coding: utf-8 -*-
#
#	Copyright (C) 2015 by Igor E. Novikov
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

import wal

from sk1 import _, config
from sk1.resources import icons
from generic import RootItem, PrefPanel


PREFS_APP = [wal.TreeElement, wal.TreeElement, wal.TreeElement, wal.TreeElement]
PREFS_DOC = [wal.TreeElement, wal.TreeElement, wal.TreeElement]

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

	def __init__(self, parent, title):
		self.app = parent.app
		size = config.prefs_dlg_size
		wal.OkCancelDialog.__init__(self, parent, title, size, resizable=True)
		self.set_minsize(config.prefs_dlg_minsize)

	def build(self):
		self.splitter = wal.Splitter(self.panel)
		self.panel.pack(self.splitter, expand=True, fill=True)
		if not PREFS_DATA:
			PREFS_DATA.append(PrefsAppItem(PREFS_APP))
			PREFS_DATA.append(PrefsDocItem(PREFS_DOC))
			for item in PREFS_DATA:
				item.init_prefs()
		self.tree = wal.TreeWidget(self.splitter, data=PREFS_DATA)
		self.container = wal.VPanel(self.splitter)
		self.splitter.split_vertically(self.tree, self.container, 200)
		self.splitter.set_min_size(150)
		self.tree.set_indent(5)
		self.tree.expand_all()

	def set_dialog_buttons(self):
		wal.OkCancelDialog.set_dialog_buttons(self)
		title = _('Restore defaults')
		self.redo_btn = wal.Button(self.left_button_box, title,
								onclick=self.restore_defaults)
		self.left_button_box.pack(self.redo_btn)

	def apply_changes(self):pass
	def restore_defaults(self, event):pass

	def show(self):
		if self.show_modal() == wal.BUTTON_OK:
			self.apply_changes()
		config.prefs_dlg_size = self.get_size()
		self.destroy()

def get_prefs_dialog(parent):
	dlg = PrefsDialog(parent, _("sK1 Preferences"))
	dlg.show()
