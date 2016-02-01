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

from uc2.formats.sk2 import sk2_const
from sk1 import _, config
from sk1.pwidgets import SolidFill, GradientFill, PatternFill

class FillDialog(wal.OkCancelDialog):

	presenter = None
	orig_fill = []
	start = True

	def __init__(self, parent, title, presenter, fill_style):
		self.presenter = presenter
		self.app = presenter.app
		self.cms = presenter.cms
		self.orig_fill = fill_style
		size = config.fill_dlg_size
		wal.OkCancelDialog.__init__(self, parent, title, style=wal.VERTICAL,
								size=size, add_line=False)

	def build(self):
		self.nb = wal.Notebook(self, on_change=self.on_change)
		self.tabs = [SolidFill(self.nb, self, self.cms),
				GradientFill(self.nb, self, self.cms),
				PatternFill(self.nb, self, self.cms)
				]
		for item in self.tabs:
			self.nb.add_page(item, item.name)
		self.pack(self.nb, fill=True, expand=True)

		if not self.orig_fill or self.orig_fill[1] == sk2_const.FILL_SOLID:
			self.nb.set_active_index(0)
		elif self.orig_fill[1] == sk2_const.FILL_GRADIENT:
			self.nb.set_active_index(1)
		elif self.orig_fill[1] == sk2_const.FILL_PATTERN:
			self.nb.set_active_index(2)
		self.start = False

	def on_change(self, index):
		new_color = None
		if self.tabs[0].active_panel and not self.start:
			new_color = self.tabs[0].active_panel.get_color()
		if index in (1, 2) and new_color:
			self.nb.get_active_page().activate(self.orig_fill, new_color)
		else:
			self.nb.get_active_page().activate(self.orig_fill)

	def get_result(self):
		return self.nb.get_active_page().get_result()

def fill_dlg(parent, presenter, fill_style, title=_('Fill')):
	return FillDialog(parent, title, presenter, fill_style).show()
