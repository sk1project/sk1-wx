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
		self.pack(self.newdoc, fill=True, start_padding=5)

		txt = _('Make backup on document save')
		self.backup = wal.Checkbox(self, txt, config.make_backup)
		self.pack(self.backup, fill=True)

		txt = _('Make backup on export')
		self.expbackup = wal.Checkbox(self, txt, config.make_export_backup)
		self.pack(self.expbackup, fill=True)

		self.built = True

	def apply_changes(self):
		config.new_doc_on_start = self.newdoc.get_value()
		config.make_backup = self.backup.get_value()
		config.make_export_backup = self.expbackup.get_value()

	def restore_defaults(self):
		defaults = config.get_defaults()
		self.newdoc.set_value(defaults['new_doc_on_start'])
		self.backup.set_value(defaults['make_backup'])
		self.expbackup.set_value(defaults['make_export_backup'])
