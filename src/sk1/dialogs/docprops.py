# -*- coding: utf-8 -*-
#
#	Copyright (C) 2013-2015 by Igor E. Novikov
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

from copy import deepcopy
from base64 import b64decode, b64encode

import wal

from uc2.uc2const import unit_names, unit_full_names
from uc2.formats.sk2.sk2_const import ORIGINS

from sk1 import _, config
from sk1.resources import icons
from sk1.pwidgets import StaticUnitLabel, UnitSpin

class DP_Panel(wal.VPanel):

	name = 'Panel'

	def __init__(self, parent, app, dlg):
		self.app = app
		self.dlg = dlg
		self.doc = app.current_doc
		self.api = self.doc.api
		wal.VPanel.__init__(self, parent)
		self.build()

	def build(self):pass
	def save(self):pass

class GeneralProps(DP_Panel):

	name = _('Description')
	metainfo = []

	def build(self):
		self.metainfo = deepcopy(self.doc.model.metainfo)
		if self.metainfo[3]: self.metainfo[3] = b64decode(self.metainfo[3])

		grid = wal.GridPanel(self, 4, 2, 5, 5)
		grid.add_growable_col(1)
		grid.add_growable_row(3)

		grid.pack(wal.Label(grid, _('Author:')))
		self.author_field = wal.Entry(grid, '' + self.metainfo[0])
		grid.pack(self.author_field, fill=True)

		grid.pack(wal.Label(grid, _('License:')))
		self.license_field = wal.Entry(grid, '' + self.metainfo[1])
		grid.pack(self.license_field, fill=True)

		grid.pack(wal.Label(grid, _('Keywords:')))
		self.keys_field = wal.Entry(grid, '' + self.metainfo[2])
		grid.pack(self.keys_field, fill=True)

		grid.pack(wal.Label(grid, _('Notes:')))
		self.notes_field = wal.Entry(grid, '' + self.metainfo[3], multiline=True)
		grid.pack(self.notes_field, fill=True)

		self.pack(grid, fill=True, expand=True, padding_all=5)

	def save(self):
		metainfo = [self.author_field.get_value(),
		self.license_field.get_value(),
		self.keys_field.get_value(),
		self.notes_field.get_value()]
		if not self.metainfo == metainfo:
			if metainfo[3]: metainfo[3] = b64encode(metainfo[3])
			self.api.set_doc_metainfo(metainfo)


class PageProps(DP_Panel):

	name = _('Page')

ORIGIN_ICONS = [icons.L_ORIGIN_CENTER, icons.L_ORIGIN_LL, icons.L_ORIGIN_LU]
ORIGIN_NAMES = [_('Page center'),
			_('Left lower page corner'), _('Left upper page corner')]

class GridProps(DP_Panel):

	name = _('Units, grid, origin')
	units = 'mm'
	geom = []
	origin = 0

	def build(self):
		hpanel = wal.HPanel(self)
		hpanel.pack(wal.Label(hpanel, _('Document units') + ':'))
		names = []
		for item in unit_names: names.append(unit_full_names[item])
		self.units_combo = wal.Combolist(hpanel, items=names)
		self.units = self.doc.methods.get_doc_units()
		self.units_combo.set_active(unit_names.index(self.units))
		hpanel.pack(self.units_combo, padding=5)
		self.pack(hpanel, padding_all=5)

		self.geom = self.doc.methods.get_grid_values()
		hpanel = wal.HPanel(self)

		txt = _('Grid origin')
		origin_panel = wal.LabeledPanel(hpanel, text=txt)
		grid = wal.GridPanel(origin_panel, 2, 3, 5, 5)

		grid.pack(wal.Label(grid, 'X:'))
		self.x_val = UnitSpin(self.app, grid, self.geom[0])
		grid.pack(self.x_val)
		grid.pack(StaticUnitLabel(self.app, grid))

		grid.pack(wal.Label(grid, 'Y:'))
		self.y_val = UnitSpin(self.app, grid, self.geom[1])
		grid.pack(self.y_val)
		grid.pack(StaticUnitLabel(self.app, grid))

		origin_panel.pack(grid, padding_all=5)
		hpanel.pack(origin_panel, padding_all=5, fill=True, expand=True)

		txt = _('Grid frequency')
		freq_panel = wal.LabeledPanel(hpanel, text=txt)
		grid = wal.GridPanel(origin_panel, 2, 3, 5, 5)

		grid.pack(wal.Label(grid, 'ΔX:'))
		self.dx_val = UnitSpin(self.app, grid, self.geom[2])
		grid.pack(self.dx_val)
		grid.pack(StaticUnitLabel(self.app, grid))

		grid.pack(wal.Label(grid, 'ΔY:'))
		self.dy_val = UnitSpin(self.app, grid, self.geom[3])
		grid.pack(self.dy_val)
		grid.pack(StaticUnitLabel(self.app, grid))

		freq_panel.pack(grid, padding_all=5)
		hpanel.pack(freq_panel, padding_all=5, fill=True, expand=True)

		self.pack(hpanel, fill=True)

		self.origin = self.doc.methods.get_doc_origin()
		self.pack(wal.Label(self, _('Document origin:')), padding_all=5)
		self.origin_keeper = wal.HToggleKeeper(self, ORIGINS, ORIGIN_ICONS,
											ORIGIN_NAMES)
		self.origin_keeper.set_mode(self.origin)
		self.pack(self.origin_keeper)

	def save(self):
		units = unit_names[self.units_combo.get_active()]
		if not self.units == units:
			self.api.set_doc_units(units)
		geom = [self.x_val.get_value(), self.y_val.get_value(),
			self.dx_val.get_value(), self.dy_val.get_value()]
		if not self.geom == geom:
			self.api.set_grid_values(geom)
		if not self.origin == self.origin_keeper.get_mode():
			self.api.set_doc_origin(self.origin_keeper.get_mode())

class GuidesProps(DP_Panel):

	name = _('Guides')

PANELS = [GeneralProps, PageProps, GridProps, GuidesProps]

class DocPropertiesDialog(wal.OkCancelDialog):

	sizer = None
	app = None
	panels = []

	def __init__(self, app, parent, title, size=config.docprops_dlg_size):
		self.app = app
		wal.OkCancelDialog.__init__(self, parent, title, size)

	def build(self):
		self.panels = []
		nb = wal.Notebook(self)
		for item in PANELS:
			item_panel = item(nb, self.app, self)
			self.panels.append(item_panel)
			nb.add_page(item_panel, item_panel.name)
		self.pack(nb, expand=True, fill=True, padding=5)

	def get_result(self):
		for item in self.panels:
			item.save()
		return None


def docprops_dlg(app, parent):
	title = _('Document properties')
	DocPropertiesDialog(app, parent, title).show()
