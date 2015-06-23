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
from sk1.dialogs import palette_info_dlg, palette_collection_dlg

from generic import PrefPanel
from collection import CollectionButton

PAL_ORIENT = [_('Horizontal'), _('Vertical')]

class PalettesPrefs(PrefPanel):

	pid = 'Palettes'
	name = _('Palettes')
	title = _('Palette options and palette management')
	icon_id = icons.PD_PREFS_PALETTE

	def __init__(self, app, dlg, fmt_config=None):
		PrefPanel.__init__(self, app, dlg)

	def build(self):

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
		btm_panel.pack(cell_panel, expand=True, fill=True, padding_all=5)

		#===
		txt = _('Vertical palette')
		vcell_panel = wal.LabeledPanel(cell_panel, text=txt)

		grid = wal.GridPanel(vcell_panel, cols=4, hgap=5, vgap=2)

		grid.pack((15, 1))
		grid.pack(wal.Label(grid, _('Cell width:')))
		self.vcell_width = wal.IntSpin(grid, config.palette_vcell_width,
									(10, 20), spin_overlay=config.spin_overlay)
		self.vcell_width.set_enable(False)
		grid.pack(self.vcell_width)
		grid.pack(wal.Label(grid, _('px')))

		grid.pack((15, 1))
		grid.pack(wal.Label(grid, _('Cell height:')))
		self.vcell_height = wal.IntSpin(grid, config.palette_vcell_height,
									(10, 100), spin_overlay=config.spin_overlay)
		grid.pack(self.vcell_height)
		grid.pack(wal.Label(grid, _('px')))

		vcell_panel.pack(grid, align_center=False, padding_all=5)
		cell_panel.pack(vcell_panel, fill=True)

		#===
		txt = _('Horizontal palette')
		hcell_panel = wal.LabeledPanel(cell_panel, text=txt)

		grid = wal.GridPanel(hcell_panel, cols=4, hgap=5, vgap=2)

		grid.pack((15, 1))
		grid.pack(wal.Label(grid, _('Cell width:')))
		self.hcell_width = wal.IntSpin(grid, config.palette_hcell_width,
									(10, 100), spin_overlay=config.spin_overlay)
		grid.pack(self.hcell_width)
		grid.pack(wal.Label(grid, _('px')))

		grid.pack((15, 1))
		grid.pack(wal.Label(grid, _('Cell height:')))
		self.hcell_height = wal.IntSpin(grid, config.palette_hcell_height,
									(10, 20), spin_overlay=config.spin_overlay)
		self.hcell_height.set_enable(False)
		grid.pack(self.hcell_height)
		grid.pack(wal.Label(grid, _('px')))

		hcell_panel.pack(grid, align_center=False, padding_all=5)
		cell_panel.pack(hcell_panel, fill=True, padding=5)
		#===

		txt = _('Expand short palettes')
		self.expand = wal.Checkbox(cell_panel, txt, config.palette_expand)
		cell_panel.pack(self.expand, align_center=False)

#		cell_panel.pack(wal.HPanel(cell_panel), expand=True, fill=True)

		self.palviewer = PaletteViewer(self.app, btm_panel, current_palette)
		btm_panel.pack(self.palviewer, fill=True, padding_all=5)

		self.nb.add_page(pal_opt, _('Palette options'))

		#========Palette management
		self.nb.add_page(PaletteManager(self.app, self, self.nb),
						_('Palette management'))

		self.pack(self.nb, expand=True, fill=True)
		self.built = True

	def update_palette_list(self):
		pal_list = self.get_palette_list()
		self.pal.set_items(pal_list)
		current_palette = self.get_current_palette()
		current_palette_name = current_palette.model.name
		self.pal.set_active(pal_list.index(current_palette_name))
		self.palviewer.draw_palette(current_palette)

	def change_palette(self):
		palette_name = self.get_palette_name_by_index(self.pal.get_active())
		current_palette = self.get_palette_by_name(palette_name)
		self.palviewer.draw_palette(current_palette)

	def apply_changes(self):
		config.palette = self.get_palette_name_by_index(self.pal.get_active())
		config.palette_orientation = self.pal_orient.get_active()
		config.palette_hcell_width = self.hcell_width.get_value()
		config.palette_vcell_height = self.vcell_height.get_value()
		config.palette_expand = self.expand.get_value()

	def restore_defaults(self):
		defaults = config.get_defaults()
		self.pal.set_active(self.get_index_by_palette_name(defaults['palette']))
		self.change_palette()
		self.pal_orient.set_active(defaults['palette_orientation'])
		self.hcell_width.set_value(defaults['palette_hcell_width'])
		self.vcell_height.set_value(defaults['palette_vcell_height'])
		self.expand.set_value(defaults['palette_expand'])


	#===Stuff
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


class PaletteManager(wal.HPanel):

	def __init__(self, app, prefpanel, parent):
		self.app = app
		self.prefpanel = prefpanel
		wal.HPanel.__init__(self, parent)

		data = self.get_palette_list()
		self.pal_list = wal.SimpleList(self, data, on_select=self.change_palette)
		self.pack(self.pal_list, expand=True, fill=True, padding_all=5)

		self.pal_viewer = PaletteViewer(app, self)
		self.pack(self.pal_viewer, fill=True, padding_all=5)

		btn_box = wal.VPanel(self)
		self.pack(btn_box, fill=True, padding_all=5)

		btn_box.pack(wal.Button(btn_box, _('Import'),
							onclick=self.import_palette),
							fill=True, end_padding=5)

		btn_box.pack(wal.Button(btn_box, _('Export'),
							onclick=self.export_palette),
							fill=True, end_padding=5)

		self.remove_btn = wal.Button(btn_box, _('Remove'),
							onclick=self.remove_palette)
		btn_box.pack(self.remove_btn, fill=True, end_padding=5)

		self.edit_btn = wal.Button(btn_box, _('Edit info'),
							onclick=self.edit_info)
		btn_box.pack(self.edit_btn, fill=True, end_padding=5)

		btn_box.pack(wal.VPanel(btn_box), fill=True, expand=True)

		btn_box.pack(wal.ImageButton(btn_box, icons.PD_DOWNLOAD48,
							tooltip=_('Download more palettes'),
							flat=False,
							onclick=self.download_more),
							fill=True, end_padding=5)

#		btn_box.pack(CollectionButton(btn_box, self.app, self,
#							self.prefpanel.dlg), fill=True, end_padding=5)

		self.update_palette_list()

	def update_palette_list(self):
		self.pal_list.update(self.get_palette_list())
		self.pal_list.set_active(0)
		self.prefpanel.update_palette_list()

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

	def change_palette(self, palette_name=''):
		if not palette_name:
			palette_name = self.app.palettes.get_default_palette_name()
		current_palette = self.get_palette_by_name(palette_name)
		self.pal_viewer.draw_palette(current_palette)
		self.remove_btn.set_enable(not current_palette.model.builtin)
		self.edit_btn.set_enable(not current_palette.model.builtin)

	def export_palette(self):
		palette_name = self.pal_list.get_selected()
		palette = self.get_palette_by_name(palette_name)
		self.app.export_palette(palette, self.prefpanel.dlg)

	def import_palette(self):
		palette_name = self.app.import_palette(self.prefpanel.dlg)
		if not palette_name:return
		self.update_palette_list()
		self.pal_list.set_active(self.get_palette_list().index(palette_name))

	def remove_palette(self):
		palette_name = self.pal_list.get_selected()
		self.app.palettes.remove_palette(palette_name)
		self.update_palette_list()

	def download_more(self):
		palette = palette_collection_dlg(self.app, self.prefpanel.dlg)
		if palette:
			self.app.palettes.add_palette(palette)
			self.update_palette_list()
			pname = palette.model.name
			self.pal_list.set_active(self.get_palette_list().index(pname))


	def edit_info(self):
		palette_name = self.pal_list.get_selected()
		palette = self.get_palette_by_name(palette_name)
		if palette_info_dlg(self.prefpanel.dlg, palette):
			self.app.palettes.remove_palette(palette_name)
			self.app.palettes.add_palette(palette)
			self.update_palette_list()













