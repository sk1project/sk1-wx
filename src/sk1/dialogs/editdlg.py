# -*- coding: utf-8 -*-
#
#	Copyright (C) 2016 by Igor E. Novikov
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

class EditDialog(wal.OkCancelDialog):

	presenter = None

	def __init__(self, parent, title, text, width):
		self.text = text
		self.width = width
		wal.OkCancelDialog.__init__(self, parent, title, style=wal.VERTICAL)

	def build(self):
		self.entry = wal.Entry(self, self.text, width=self.width)
		self.pack(self.entry, padding_all=10, fill=True)

	def get_result(self):
		txt = self.entry.get_value()
		if not txt: txt = self.text
		return txt

def edit_dlg(parent, dlg_name, text, width=25):
	dlg = EditDialog(parent, dlg_name, text, width)
	return dlg.show()
