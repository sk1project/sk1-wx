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

from sk1 import _, config, appconst, dialogs
from sk1.resources import get_icon, icons
from sk1.printing import prn_events

from general_tab import GeneralTab
from cupspropsdlg import CUPS_PrnPropsDialog, PDF_PrnPropsDialog


class PrintDialog(wal.OkCancelDialog):

	printsys = None
	printer = None
	printout = None

	def __init__(self, mw, printsys, printout):
		self.app = mw.app
		self.mw = mw
		self.printsys = printsys
		self.printout = printout
		self.printer = self.printsys.get_default_printer()
		size = config.print_dlg_size
		wal.OkCancelDialog.__init__(self, self.mw, _("Print"), size,
							resizable=True, action_button=wal.BUTTON_PRINT)
		self.set_minsize(config.print_dlg_minsize)

	def build(self):
		self.nb = wal.Notebook(self.panel)

		self.general_tab = GeneralTab(self.nb, self,
									self.printsys, self.printout)
		self.printer = self.general_tab.prn_panel.printer
		self.nb.add_page(self.general_tab, self.general_tab.name)

		self.layouts_tab = wal.VPanel(self.nb)
		self.nb.add_page(self.layouts_tab, 'Layouts')

		self.prepress_tab = wal.VPanel(self.nb)
		self.nb.add_page(self.prepress_tab, 'Prepress')

		self.preflight_tab = wal.VPanel(self.nb)
		self.nb.add_page(self.preflight_tab, 'Prefligh')

		self.panel.pack(self.nb, expand=True, fill=True)

		prn_events.connect(prn_events.PRINTER_CHANGED, self.printer_changed)
		prn_events.connect(prn_events.PRINTER_MODIFIED, self.printer_modified)

	def set_dialog_buttons(self):
		wal.OkCancelDialog.set_dialog_buttons(self)
		self.preview_btn = wal.Button(self.left_button_box, _('Print Preview'),
								onclick=self.print_preview)
		self.left_button_box.pack(self.preview_btn)
		self.ok_btn.set_enable(self.printer.is_ready())

	def get_result(self): return self.printer

	def end_modal(self, ret):
		prn_events.clean_all_channels()
		config.print_dlg_size = self.get_size()
		wal.OkCancelDialog.end_modal(self, ret)

	def printer_changed(self, printer):
		self.printer = printer
		self.printer_modified()

	def printer_modified(self):
		self.ok_btn.set_enable(self.printer.is_ready())

	def print_preview(self):pass
