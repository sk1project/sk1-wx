# -*- coding: utf-8 -*-
#
#	Copyright (C) 2016 by Igor E. Novikov
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

from canvas import PreviewCanvas
from toolbar import PreviewToolbar
from ruler import PreviewCorner, PreviewRuler

class PreviewDialog(wal.SimpleDialog):

	printer = None
	printout = None
	win = None
	app = None

	def __init__(self, win, app, printer, printout):
		self.win = win
		self.app = app
		self.printer = printer
		self.printout = printout
		size = config.print_preview_dlg_size
		wal.SimpleDialog.__init__(self, win, _("Print preview"),
						size, resizable=True, add_line=False, margin=0)
		self.set_minsize(config.print_preview_dlg_minsize)

	def build(self):
		r_grid = wal.GridPanel(self)
		cv_grid = wal.GridPanel(r_grid)
		self.canvas = PreviewCanvas(cv_grid, self, self.printer, self.printout)

		units = self.printout.get_units()
		corner = PreviewCorner(r_grid)
		hruler = PreviewRuler(r_grid, self.canvas, units)
		hruler.set_bg(wal.WHITE)
		vruler = PreviewRuler(r_grid, self.canvas, units, False)
		vruler.set_bg(wal.WHITE)

		tb = PreviewToolbar(self, self, self.canvas, self.printer)
		vscroll = wal.ScrollBar(cv_grid, onscroll=self.canvas._scrolling)
		hscroll = wal.ScrollBar(cv_grid, False, onscroll=self.canvas._scrolling)
		self.canvas.set_ctrls(hscroll, vscroll, hruler, vruler, tb.pager)

		self.pack(tb, fill=True)
		self.pack(wal.HLine(self), fill=True)

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

		self.pack(r_grid, fill=True, expand=True)

	def show_modal(self):
		self.canvas.set_focus()
		return wal.SimpleDialog.show_modal(self)

	def end_modal(self, ret):
		config.print_preview_dlg_size = self.get_size()
		wal.SimpleDialog.end_modal(self, ret)
