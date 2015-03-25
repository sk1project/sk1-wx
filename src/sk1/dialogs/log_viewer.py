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

import os

import wal

from sk1 import _, config, appconst

class LogViewerDialog(wal.OkCancelDialog):

	sizer = None
	box = None
	button_box = None
	ok_btn = None
	cancel_btn = None
	lc = None
	data = []
	ret = ''

	def __init__(self, parent, title):
		self.app = parent.app
		size = config.history_dlg_size
		wal.OkCancelDialog.__init__(self, parent, title, size, resizable=True,
								action_button=wal.BUTTON_OPEN)
		self.set_minsize(config.history_dlg_minsize)
		self.ok_btn.set_enable(False)
		self.update_list()

	def build(self):
		self.lc = wal.ReportList(self.panel, on_select=self.update,
								on_activate=self.on_ok)
		self.panel.pack(self.lc, expand=True, fill=True)

	def set_dialog_buttons(self):
		wal.OkCancelDialog.set_dialog_buttons(self)
		self.clear_btn = wal.Button(self.left_button_box, _('Clear log'),
								onclick=self.clear_history)
		self.left_button_box.pack(self.clear_btn)

	def update(self, value):
		if value:self.ok_btn.set_enable(True)
		else:self.ok_btn.set_enable(False)
		if self.data: self.clear_btn.set_enable(True)
		else:self.clear_btn.set_enable(False)

	def update_list(self):
		header = [_('Status'), _('File name'), _('Path'), _('Time')]
		data = self.app.history.get_history_entries()
		self.data = []
		for item in data:
			op = _('Opened')
			if item[0] == appconst.SAVED:op = _('Saved')
			self.data.append([op, item[1], item[2], item[4]])
		data = [header] + self.data
		self.lc.update(data)
		self.lc.set_column_width(0, wal.LIST_AUTOSIZE)
		self.lc.set_column_width(1, wal.LIST_AUTOSIZE)
		self.lc.set_column_width(2, wal.LIST_AUTOSIZE)
		self.lc.set_column_width(3, wal.LIST_AUTOSIZE)
		self.update(False)

	def clear_history(self, *args):
		self.app.history.clear_history()
		self.lc.clear_all()

	def on_ok(self, value):
		if value:
			path = value[2]
			if os.path.isfile(path):
				self.ret = path
				self.end_modal(wal.const.BUTTON_OK)
			else:
				txt = "%s '%s' %s" % (_('File'), path, _('is not found.'))
				wal.error_dialog(self, _('File not found'), txt)

	def get_result(self): return self.ret

	def show(self):
		ret = None
		if self.show_modal() == wal.BUTTON_OK:
			ret = self.get_result()
		config.history_dlg_size = self.get_size()
		self.destroy()
		return ret

def log_viewer_dlg(parent):
	dlg = LogViewerDialog(parent, _("Recent documents"))
	ret = dlg.show()
	if ret:parent.app.open(ret)
