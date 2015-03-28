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
from sk1.pwidgets import PaletteViewer

from generic import PrefPanel

PAL_ORIENT = [_('Horizontal'), _('Vertical')]

class PalettesPrefs(PrefPanel):

	pid = 'Palettes'
	name = _('Palettes')
	title = _('Palette options and palette management')
	icon_id = icons.PD_PREFS_PALETTE

	def __init__(self, app, dlg, fmt_config=None):
		PrefPanel.__init__(self, app, dlg)

		self.nb = wal.Notebook(self)

		#========Palette options
		pal_opt = wal.VPanel(self.nb)
		pal_opt.pack((10, 10))

		grid = wal.GridPanel(self, hgap=5, vgap=5)
		grid.add_growable_col(1)

		txt = _('Current palette:')
		grid.pack(wal.Label(grid, txt))

		pal_list = self.get_palette_list()
		self.pal = wal.Combolist(grid, items=pal_list,
								onchange=self.change_palette)
		current_palette = self.get_current_palette()
		current_palette_name = current_palette.model.name
		self.pal.set_active(pal_list.index(current_palette_name))
		grid.pack(self.pal, fill=True)

		txt = _('Palette orientation:')
		grid.pack(wal.Label(grid, txt))
		self.pal_orient = wal.Combolist(grid, items=PAL_ORIENT)
		self.pal_orient.set_active(config.palette_orientation)
		grid.pack(self.pal_orient)

		pal_opt.pack(grid, fill=True, padding_all=5)

		btm_panel = wal.HPanel(pal_opt)
		pal_opt.pack(btm_panel, expand=True, fill=True)

		cell_panel = wal.VPanel(btm_panel)
		btm_panel.pack(cell_panel, expand=True, fill=True)

		self.palviewer = PaletteViewer(self.app, btm_panel, current_palette)
		btm_panel.pack(self.palviewer, fill=True, padding_all=5)


		self.nb.add_page(pal_opt, _('Palette options'))

		#========Palette management
		self.nb.add_page(wal.VPanel(self.nb), _('Palette management'))

		self.pack(self.nb, expand=True, fill=True)
		self.built = True

	def get_current_palette(self):
		current_palette_name = config.palette
		if not current_palette_name:
			return self.app.palettes.palette_in_use
		return self.get_palette_by_name(current_palette_name)

	def get_palette_list(self):
		palettes = self.app.palettes.palettes
		pal_list = palettes.keys()
		pal_list.sort()
		return pal_list

	def get_palette_by_name(self, name):
		palettes = self.app.palettes.palettes
		pal_list = self.get_palette_list()
		if not name in pal_list:
			name = self.app.palettes.get_default_palette_name()
		return palettes[name]

	def get_palette_name_by_index(self, index):
		pal_list = self.get_palette_list()
		return pal_list[index]

	def get_index_by_palette_name(self, name=''):
		pal_list = self.get_palette_list()
		if not name in pal_list:
			name = self.app.palettes.get_default_palette_name()
		return pal_list.index(name)

	def change_palette(self, event):
		palette_name = self.get_palette_name_by_index(self.pal.get_active())
		current_palette = self.get_palette_by_name(palette_name)
		self.palviewer.draw_palette(current_palette)

	def apply_changes(self):
		config.palette = self.get_palette_name_by_index(self.pal.get_active())
		config.palette_orientation = self.pal_orient.get_active()

	def restore_defaults(self):
		defaults = config.get_defaults()
		self.pal.set_active(self.get_index_by_palette_name(defaults['palette']))
		self.pal_orient.set_active(defaults['palette_orientation'])
