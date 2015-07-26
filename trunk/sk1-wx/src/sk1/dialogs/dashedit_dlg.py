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

from uc2 import uc2const
from sk1 import _, config
TXT = _("""Dash pattern is a sequence (stroke-space-stroke-space- etc.) of integer 
or float values separated by space which describes size of pattern elements. 
The values are relative to line width. Example: '2 1' or '5 1 1 1'. Empty value
means no dash, i.e. solid line.""")

class DashEditorDialog(wal.OkCancelDialog):

	dash = None

	def __init__(self, parent, title, dash=[]):
		self.dash = dash
		wal.OkCancelDialog.__init__(self, parent, title, style=wal.VERTICAL)

	def build(self):
		self.pack(wal.Label(self, TXT), align_center=False, padding_all=5)
		self.editor = wal.Entry(self, onchange=self.check_input,
							onenter=self.process_input)
		self.pack(self.editor, fill=True, padding_all=5)
		self.set_dash(self.dash)

	def set_dash(self, dash):
		txt = ''
		for item in dash: txt += str(item) + ' '
		self.editor.set_value(txt)

	def check_input(self):
		ret = ''
		val = self.editor.get_value()
		for item in val:
			if item in '0123456789. ':
				ret += item
		if not ret == val:
			self.editor.set_value(ret)

	def process_input(self):
		self.dash = []
		strval = self.editor.get_value()
		if strval:
			seq = strval.split(' ')
			if not seq[-1]: seq = seq[:-1]
			for item in seq:
				val = int(item)
				if '.' in item:val = float(item)
				self.dash.append(val)
		self.set_dash(self.dash)

	def get_result(self):
		self.process_input()
		return self.dash

def dash_editor_dlg(parent, dash):
	dlg = DashEditorDialog(parent, _('Edit dash pattern'), dash)
	return dlg.show()
