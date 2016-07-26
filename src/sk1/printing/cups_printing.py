# -*- coding: utf-8 -*-
#
# 	Copyright (C) 2016 by Igor E. Novikov
#
# 	This program is free software: you can redistribute it and/or modify
# 	it under the terms of the GNU General Public License as published by
# 	the Free Software Foundation, either version 3 of the License, or
# 	(at your option) any later version.
#
# 	This program is distributed in the hope that it will be useful,
# 	but WITHOUT ANY WARRANTY; without even the implied warranty of
# 	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# 	GNU General Public License for more details.
#
# 	You should have received a copy of the GNU General Public License
# 	along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os, sys

import wal

from sk1 import _, config, appconst

class GeneralPanel(wal.VPanel):

	name = _('General')

	def __init__(self, parent):
		wal.VPanel.__init__(self, parent)

		ppanel = wal.LabeledPanel(self, _('Printer'))

		grid = wal.GridPanel(ppanel, 4, 3)

		grid.pack(wal.Label(grid, _('Name:')))
		self.prn_list = wal.Combolist(grid)
		grid.pack(self.prn_list)
		self.prop_btn = wal.Button(grid, _('Properties...'))
		grid.pack(self.prop_btn)

		grid.pack(wal.Label(grid, _('Driver:')))
		self.driver_label = wal.Label(grid, _(''))
		grid.pack(self.driver_label)
		grid.pack((1, 1))

		grid.pack(wal.Label(grid, _('Connection:')))
		self.conn_label = wal.Label(grid, _(''))
		grid.pack(self.driver_label)
		grid.pack((1, 1))

		grid.pack(wal.Label(grid, _('Status:')))
		self.status_label = wal.Label(grid, _(''))
		grid.pack(self.driver_label)
		grid.pack((1, 1))
		ppanel.pack(grid, fill=True, expand=True, padding_all=5)

		self.pack(ppanel, fill=True, padding_all=5)

class CUPSPrintDialog(wal.OkCancelDialog):

	printsys = None
	printer = None
	printout = None

	def __init__(self, parent, title, presenter):
		self.app = parent.app
		self.presenter = presenter
		size = config.print_dlg_size
		wal.OkCancelDialog.__init__(self, parent, title, size, resizable=True,
								action_button=wal.BUTTON_PRINT, add_line=False)
		self.set_minsize(config.print_dlg_minsize)

	def build(self):
		self.nb = wal.Notebook(self.panel)

		self.general_tab = GeneralPanel(self.nb)
		self.nb.add_page(self.general_tab, self.general_tab.name)

		self.layouts_tab = wal.VPanel(self.nb)
		self.nb.add_page(self.layouts_tab, 'Layouts')

		self.prepress_tab = wal.VPanel(self.nb)
		self.nb.add_page(self.prepress_tab, 'Prepress')

		self.preflight_tab = wal.VPanel(self.nb)
		self.nb.add_page(self.preflight_tab, 'Prefligh')

		self.panel.pack(self.nb, expand=True, fill=True)

	def set_dialog_buttons(self):
		wal.OkCancelDialog.set_dialog_buttons(self)
		self.preview_btn = wal.Button(self.left_button_box, _('Print Prieviw'),
								onclick=self.print_preview)
		self.left_button_box.pack(self.preview_btn)

	def print_preview(self):pass




def cups_print_dlg(parent, presenter):
	dlg = CUPSPrintDialog(parent, _("Print"), presenter)
	dlg.show()
