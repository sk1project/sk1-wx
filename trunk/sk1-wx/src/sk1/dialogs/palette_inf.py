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


import wal

from sk1 import _, config

class PaletteInfoDialog(wal.OkCancelDialog):
	def __init__(self, parent, title, palette):
		self.palette = palette
		size = config.palinfo_dlg_size
		wal.OkCancelDialog.__init__(self, parent, title, size, resizable=True,
								action_button=wal.BUTTON_SAVE)
		self.set_minsize(config.palinfo_dlg_minsize)

	def build(self):
#		self.panel
		grid = wal.GridPanel(self.panel, rows=4, cols=2, vgap=5, hgap=5)
		self.panel.pack(grid, expand=True, fill=True, padding_all=5)
		grid.add_growable_col(1)
		grid.add_growable_row(3)

		grid.pack(wal.Label(grid, _('Palette name:')))
		self.name_entry = wal.Entry(grid, value=self.palette.model.name)
		grid.pack(self.name_entry, fill=True)

		grid.pack(wal.Label(grid, _('Palette source:')))
		self.source_entry = wal.Entry(grid, value=self.palette.model.source)
		grid.pack(self.source_entry, fill=True)

		grid.pack(wal.Label(grid, _('Columns:')))
		cols = self.palette.model.columns
		size = len(self.palette.model.colors)
		self.cols = wal.IntSpin(grid, value=cols, range_val=(1, size),
							spin_overlay=config.spin_overlay)
		grid.pack(self.cols)

		grid.pack(wal.Label(grid, _('Description:')))
		self.comm_entry = wal.Entry(grid, value=self.palette.model.comments,
									multiline=True)
		grid.pack(self.comm_entry, fill=True)

	def on_ok(self, *args):
		self.end_modal(wal.BUTTON_OK)

	def show(self):
		ret = False
		if self.show_modal() == wal.BUTTON_OK:
			ret = True
			pal = self.palette.model
			pal.name = self.name_entry.get_value()
			pal.source = self.source_entry.get_value()
			pal.columns = self.cols.get_value()
			pal.comments = self.comm_entry.get_value()
		config.palinfo_dlg_size = self.get_size()
		self.destroy()
		return ret

def palette_info_dlg(parent, palette):
	dlg = PaletteInfoDialog(parent, _("Palette info"), palette)
	return dlg.show()
