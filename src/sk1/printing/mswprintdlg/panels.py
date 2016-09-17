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

import wal

from sk1 import _
from sk1.printing import prn_events

SPACER = (10, 10)

class FLabeledPanel(wal.VPanel):

	def __init__(self, parent, label='CAPTION'):
		self.title = label.upper()
		wal.VPanel.__init__(self, parent)
		hpanel = wal.HPanel(self)
		hpanel.pack(SPACER)
		self.cont = wal.VPanel(hpanel)
		self.cont.pack(wal.Label(self.cont, self.title, fontsize=3),
					padding=5, align_center=False)

		self.build()

		hpanel.pack(self.cont, fill=True, expand=True)
		hpanel.pack(SPACER)
		self.pack(hpanel, fill=True)
		panel = wal.VPanel(self)
		panel.set_bg(wal.UI_COLORS['workspace'])
		panel.pack((1, 1))
		self.pack(panel, fill=True)

	def build(self):pass

class PageRangePanel(FLabeledPanel):

	def __init__(self, parent, printout):
		self.printout = printout
		FLabeledPanel.__init__(self, parent, _('Page range'))

	def build(self):

		grid = wal.GridPanel(self.cont, 7, 1, 5, 15)
		grid.add_growable_col(0)
		self.all_opt = wal.Radiobutton(grid, _('All'), group=True,
									onclick=self.update)
		self.sel_opt = wal.Radiobutton(grid, _('Selection'),
									onclick=self.update)
		self.cpage_opt = wal.Radiobutton(grid, _('Current page'),
									onclick=self.update)
		self.pages_opt = wal.Radiobutton(grid, _('Pages:'),
									onclick=self.update)
		self.pages_entry = wal.Entry(grid, '1', onchange=self.pages_changed)
		self.pages_entry.set_enable(False)
		self.all_opt.set_value(True)
		if not self.printout.is_selection():
			self.sel_opt.set_enable(False)
		if not self.printout.get_num_pages() > 1:
			self.cpage_opt.set_enable(False)
			self.pages_opt.set_enable(False)
		grid.pack(self.all_opt)
		grid.pack(self.sel_opt)
		grid.pack(self.cpage_opt)
		hpanel = wal.HPanel(grid)
		hpanel.pack(self.pages_opt)
		hpanel.pack(self.pages_entry, fill=True, expand=True)
		grid.pack(hpanel, fill=True)

		title = _('Enter page numbers or page ranges.')
		title += '\n' + _('For example: 1,2,5-6')
		grid.pack(wal.Label(self, title, fontsize=-1))
		grid.pack((5, 5))

		self.reverse = wal.Checkbox(grid, _('Reverse order'))
		grid.pack(self.reverse)

		self.cont.pack(grid, fill=True, padding_all=5)

	def update(self):pass
	def pages_changed(self):pass


class PrinterPanel(FLabeledPanel):

	ready_flag = False

	def __init__(self, parent, win, printsys, printout):
		self.printsys = printsys
		self.printout = printout
		self.win = win
		self.printer = self.printsys.get_default_printer()
		FLabeledPanel.__init__(self, parent, _('Printer'))

	def build(self):
		plist = self.printsys.get_printer_names()
		self.prn_list = wal.Combolist(self.cont, items=plist,
									onchange=self.on_printer_change)
		self.prn_list.set_active(plist.index(self.printer.get_name()))
		self.cont.pack(self.prn_list, fill=True, expand=True)

		hpanel = wal.HPanel(self.cont)
		hpanel.pack((1, 1), fill=True, expand=True)
		self.print_btn = wal.Button(hpanel, _('Print'), onclick=self.on_print)
		hpanel.pack(self.print_btn)

		self.cont.pack(hpanel, fill=True, padding=5)
		self.ready_flag = True

	def on_printer_change(self):
		if not self.ready_flag: return
		name = self.prn_list.get_active_value()
		self.printer = self.printsys.get_printer_by_name(name)
		prn_events.emit(prn_events.PRINTER_CHANGED, self.printer)

	def on_print(self):
		self.printer.run_printdlg(self.win, self.printout)
