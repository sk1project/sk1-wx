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

from generic import PrefPanel

class GeneralPrefs(PrefPanel):

	pid = 'General'
	name = _('General')
	title = _('General application preferences')
	icon_id = icons.PD_PROPERTIES

	def __init__(self, app, dlg, fmt_config=None):
		PrefPanel.__init__(self, app, dlg)

	def build(self):
		txt = _('Create new document on start')
		self.newdoc = wal.Checkbox(self, txt, config.new_doc_on_start)
		self.pack(self.newdoc, align_center=False, start_padding=5)

		txt = _('Make backup on document save')
		self.backup = wal.Checkbox(self, txt, config.make_backup)
		self.pack(self.backup, align_center=False)

		txt = _('Make backup on export')
		self.expbackup = wal.Checkbox(self, txt, config.make_export_backup)
		self.pack(self.expbackup, align_center=False)

		grid = wal.GridPanel(self, rows=2, cols=3, hgap=5, vgap=3)
		grid.pack(wal.Label(grid, _('History log size:')))
		self.hist_size = wal.IntSpin(grid, config.history_size,
								(10, 1000), spin_overlay=config.spin_overlay)
		grid.pack(self.hist_size)
		grid.pack(wal.Label(grid, _('records')))
		grid.pack(wal.Label(grid, _('History menu size:')))
		self.hist_menu_size = wal.IntSpin(grid, config.history_list_size,
									(5, 20), spin_overlay=config.spin_overlay)
		grid.pack(self.hist_menu_size)
		grid.pack(wal.Label(grid, _('records')))
		self.pack(grid, align_center=False, padding=5)

		if not config.is_mac():
			txt = _('Use overlay for float spinbox widgets (*)')
			self.spin_overlay = wal.Checkbox(self, txt, config.spin_overlay)
			self.pack(self.spin_overlay, align_center=False)

		if config.is_ubuntu():
			txt = _('Ubuntu related features')
			self.pack(wal.Label(grid, txt, fontsize=2, fontbold=True),
					start_padding=10)
			self.pack(wal.HLine(self), fill=True, padding=2)

			txt = _('Use Unity Global Menu (*)')
			self.ubuntu_gm = wal.Checkbox(self, txt,
										config.ubuntu_global_menu)
			self.pack(self.ubuntu_gm, align_center=False)

			txt = _('Allow overlay for scrollbars (*)')
			self.ubuntu_overlay = wal.Checkbox(self, txt,
										config.ubuntu_scrollbar_overlay)
			self.pack(self.ubuntu_overlay, align_center=False)


		if not config.is_mac():
			self.pack(wal.HPanel(self), expand=True, fill=True)
			txt = _('(*) - These options require application restart')
			self.pack(wal.Label(grid, txt, fontsize=-1), align_center=False)

		self.built = True

	def apply_changes(self):
		config.new_doc_on_start = self.newdoc.get_value()
		config.make_backup = self.backup.get_value()
		config.make_export_backup = self.expbackup.get_value()
		config.history_size = self.hist_size.get_value()
		config.history_list_size = self.hist_menu_size.get_value()
		if not config.is_mac():
			config.spin_overlay = self.spin_overlay.get_value()
		if config.is_ubuntu():
			config.ubuntu_global_menu = self.ubuntu_gm.get_value()
			config.ubuntu_scrollbar_overlay = self.ubuntu_overlay.get_value()

	def restore_defaults(self):
		defaults = config.get_defaults()
		self.newdoc.set_value(defaults['new_doc_on_start'])
		self.backup.set_value(defaults['make_backup'])
		self.expbackup.set_value(defaults['make_export_backup'])
		self.hist_size.set_value(defaults['history_size'])
		self.hist_menu_size.set_value(defaults['history_list_size'])
		if not config.is_mac():
			self.spin_overlay.set_value(defaults['spin_overlay'])
		if config.is_ubuntu():
			self.ubuntu_gm.set_value(defaults['ubuntu_global_menu'])
			self.ubuntu_overlay.set_value(defaults['ubuntu_scrollbar_overlay'])
