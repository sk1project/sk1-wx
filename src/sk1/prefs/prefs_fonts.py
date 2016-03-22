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

from sk1 import _, config
from sk1.resources import icons

from generic import PrefPanel

class FontPrefs(PrefPanel):

	pid = 'Fonts'
	name = _('Fonts')
	title = _('Font preview preferences')
	icon_id = icons.PD_FONT

	def __init__(self, app, dlg, fmt_config=None):
		PrefPanel.__init__(self, app, dlg)

	def build(self):
		grid = wal.GridPanel(self, rows=4, cols=2, hgap=5, vgap=5)
		grid.add_growable_col(1)

		grid.pack(wal.Label(grid, _('Text filler:')))
		self.filler = wal.Entry(grid, config.font_preview_text)
		grid.pack(self.filler, fill=True)

		grid.pack(wal.Label(grid, _('Font size:')))
		self.fontsize = wal.IntSpin(grid, config.font_preview_size, (5, 50))
		grid.pack(self.fontsize)

		grid.pack(wal.Label(grid, _('Font color:')))
		self.fontcolor = wal.ColorButton(grid, config.font_preview_color)
		grid.pack(self.fontcolor)

		grid.pack(wal.Label(grid, _('Preview width:')))
		self.pwidth = wal.IntSpin(grid, config.font_preview_width, (100, 1000))
		grid.pack(self.pwidth)

		self.pack(grid, align_center=False, fill=True, padding=5)
		self.built = True

	def apply_changes(self):
		config.font_preview_text = self.filler.get_value()
		config.font_preview_size = self.fontsize.get_value()
		config.font_preview_color = self.fontcolor.get_value()
		config.font_preview_width = self.pwidth.get_value()

	def restore_defaults(self):
		defaults = config.get_defaults()
		self.filler.set_value(defaults['font_preview_text'])
		self.fontsize.set_value(defaults['font_preview_size'])
		self.fontcolor.set_value(defaults['font_preview_color'])
		self.pwidth.set_value(defaults['font_preview_width'])

