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

from sk1.resources import get_icon

class RootItem(object):

	pid = ''
	name = ''
	icon_id = None
	icon = None
	childs = []

	built = True
	leaf = False

	def __init__(self, data=[]):
		if self.icon_id: self.icon = get_icon(self.icon_id)
		self.childs = data

	def init_prefs(self, app, dlg, fmt_config=None):
		new_childs = []
		for item in self.childs:
			new_item = item(app, dlg, fmt_config)
			new_item.hide()
			new_childs.append(new_item)
		self.childs = new_childs


class PrefPanel(wal.VPanel):

	pid = ''
	name = ''
	title = ''
	icon_id = None
	icon = None
	childs = []

	built = False
	leaf = True

	app = None
	dlg = None
	fmt_config = None

	def __init__(self, app, dlg, fmt_config=None):
		wal.VPanel.__init__(self, dlg)
		self.fmt_config = fmt_config
		self.app = app
		self.dlg = dlg
		if self.icon_id:self.icon = get_icon(self.icon_id)
		if not self.title: self.title = self.name
		fsize = str(int(wal.get_system_fontsize()) + 3)
		self.pack(wal.Label(self, self.title, fontsize=fsize, fontbold=True))
		self.pack(wal.HLine(self), fill=True, padding=5)

	def build(self):pass
	def update(self):pass
	def apply_changes(self):pass
	def restore_defaults(self):pass
