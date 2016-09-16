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

from sk1 import _, config

from sk1.printing import prn_events
from sk1.printing.previewdlg.canvas import PreviewCanvas
from sk1.printing.previewdlg.ruler import PreviewCorner, PreviewRuler

from sk1.printing.msw_print import MSWPrinter, MSW_PS
from sk1.printing.printout import Printout
from toolbar import PreviewToolbar
from panels import PrinterPanel

class MSWPrintDialog(wal.SimpleDialog):

	printer = None
	printout = None
	win = None
	app = None

	def __init__(self, win, app, doc):
		self.win = win
		self.app = app
		self.msw_ps = MSW_PS(app)
		self.printer = self.msw_ps.get_default_printer()
		self.printout = Printout(doc)
		size = config.print_preview_dlg_size
		title = _("Print preview") + ' - %s' % self.printer.get_name()
		wal.SimpleDialog.__init__(self, win, title, size, wal.HORIZONTAL,
								resizable=True, add_line=False, margin=0)
		self.set_minsize(config.print_preview_dlg_minsize)

	def build(self):
		prnpanel = wal.VPanel(self)
		prnpanel.pack(PrinterPanel(prnpanel, self, self.msw_ps, self.printout),
					fill=True)
		self.pack(prnpanel, fill=True)

		self.pack(wal.VLine(self), fill=True)

		cont = wal.VPanel(self)

		r_grid = wal.GridPanel(cont)
		cv_grid = wal.GridPanel(r_grid)
		self.canvas = PreviewCanvas(cv_grid, self, self.printer, self.printout)

		units = self.printout.get_units()
		corner = PreviewCorner(r_grid)
		hruler = PreviewRuler(r_grid, self.canvas, units)
		hruler.set_bg(wal.WHITE)
		vruler = PreviewRuler(r_grid, self.canvas, units, False)
		vruler.set_bg(wal.WHITE)

		tb = PreviewToolbar(cont, self, self.canvas, self.printer)
		vscroll = wal.ScrollBar(cv_grid, onscroll=self.canvas._scrolling)
		hscroll = wal.ScrollBar(cv_grid, False, onscroll=self.canvas._scrolling)
		self.canvas.set_ctrls(hscroll, vscroll, hruler, vruler, tb.pager)

		cont.pack(tb, fill=True)
		cont.pack(wal.HLine(self), fill=True)

		cv_grid.add_growable_col(0)
		cv_grid.add_growable_row(0)
		cv_grid.pack(self.canvas, fill=True)
		cv_grid.pack(vscroll, fill=True)
		cv_grid.pack(hscroll, fill=True)
		cv_grid.pack((1, 1))

		r_grid.add_growable_col(1)
		r_grid.add_growable_row(1)
		r_grid.pack(corner)
		r_grid.pack(hruler, fill=True)
		r_grid.pack(vruler, fill=True)
		r_grid.pack(cv_grid, fill=True)

		cont.pack(r_grid, fill=True, expand=True)

		self.pack(cont, fill=True, expand=True)
		prn_events.connect(prn_events.PRINTER_CHANGED, self.printer_changed)

	def get_result(self): return None, self.printout

	def show_modal(self):
		self.canvas.set_focus()
		return wal.SimpleDialog.show_modal(self)

	def end_modal(self, ret):
		prn_events.clean_all_channels()
		config.print_preview_dlg_size = self.get_size()
		self.canvas.destroy()
		wal.SimpleDialog.end_modal(self, ret)

	def show(self):
		self.show_modal()
		ret = self.get_result()
		self.destroy()
		return ret

	def printer_changed(self, printer):
		self.printer = printer
		self.canvas.printer = printer
		self.canvas.refresh()
		title = _("Print preview") + ' - %s' % self.printer.get_name()
		self.set_title(title)
