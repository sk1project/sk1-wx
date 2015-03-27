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
		pal_list = self.app.palettes.palettes.keys()
		self.pal = wal.Combolist(grid, items=pal_list, onchange=None)
		curent_palette = self.app.palettes.palette_in_use.model.name
		self.pal.set_active(pal_list.index(curent_palette))
		grid.pack(self.pal, fill=True)

		txt = _('Palette orientation:')
		grid.pack(wal.Label(grid, txt))
		self.pal_orient = wal.Combolist(grid, items=PAL_ORIENT)
		self.pal_orient.set_active(config.palette_orientation)
		grid.pack(self.pal_orient)

		pal_opt.pack(grid, fill=True, padding_all=5)


		self.nb.add_page(pal_opt, _('Palette options'))

		#========Palette management
		self.nb.add_page(wal.VPanel(self.nb), _('Palette management'))

		self.pack(self.nb, expand=True, fill=True)
		self.built = True

	def apply_changes(self):
		print self.pal_orient.get_active()
		config.palette_orientation = self.pal_orient.get_active()

	def restore_defaults(self):
		defaults = config.get_defaults()
		self.pal_orient.get_active(defaults['palette_orientation'])
