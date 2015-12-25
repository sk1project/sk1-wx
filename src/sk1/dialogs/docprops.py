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

from sk1 import _, config
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

	name = _('General')
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

class GridProps(DP_Panel):

	name = _('Grid')

	def build(self):
		hpanel = wal.HPanel(self)

		txt = _('Grid origin')
		origin_panel = wal.LabeledPanel(hpanel, text=txt)
		grid = wal.GridPanel(origin_panel, 2, 4, 5, 5)

		grid.pack((10, 1))
		grid.pack(wal.Label(grid, 'X:'))
		self.x_val = UnitSpin(self.app, grid)
		grid.pack(self.x_val)
		grid.pack(StaticUnitLabel(self.app, grid))

		grid.pack((10, 1))
		grid.pack(wal.Label(grid, 'Y:'))
		self.y_val = UnitSpin(self.app, grid)
		grid.pack(self.y_val)
		grid.pack(StaticUnitLabel(self.app, grid))

		origin_panel.pack(grid, align_center=False, padding_all=5)
		hpanel.pack(origin_panel, padding_all=5, fill=True, expand=True)

		txt = _('Grid frequency')
		freq_panel = wal.LabeledPanel(hpanel, text=txt)
		grid = wal.GridPanel(origin_panel, 2, 4, 5, 5)

		grid.pack((10, 1))
		grid.pack(wal.Label(grid, 'ΔX:'))
		self.dx_val = UnitSpin(self.app, grid)
		grid.pack(self.dx_val)
		grid.pack(StaticUnitLabel(self.app, grid))

		grid.pack((10, 1))
		grid.pack(wal.Label(grid, 'ΔY:'))
		self.dy_val = UnitSpin(self.app, grid)
		grid.pack(self.dy_val)
		grid.pack(StaticUnitLabel(self.app, grid))

		freq_panel.pack(grid, align_center=False, padding_all=5)
		hpanel.pack(freq_panel, padding_all=5, fill=True, expand=True)

		self.pack(hpanel, fill=True)

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
