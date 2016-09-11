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

import wx

from sk1 import _
from sk1.printing.generic import AbstractPrinter

class MSWPrinter(AbstractPrinter):

	def __init__(self, app):
		self.app = app
		self.name = _('Default printer')

	def get_print_data(self):
		if self.app.print_data is None:
			self.app.print_data = self.create_print_data()
		return self.app.print_data

	def create_print_data(self):
		print_data = wx.PrintData()
		print_data.SetPaperId(wx.PAPER_A4)
		print_data.SetPrintMode(wx.PRINT_MODE_PRINTER)
		return print_data

	def run_propsdlg(self, win):
		data = wx.PageSetupDialogData(self.get_print_data())
		data.CalculatePaperSizeFromId()
		dlg = wx.PageSetupDialog(win, data)
		if dlg.ShowModal() == wx.OK:
			data = wx.PrintData(dlg.GetPageSetupData().GetPrintData())
			self.app.print_data = data
			dlg.Destroy()
			return True
		return False

	def run_printdlg(self, win):
		printer = wx.Printer(self.app.print_data)
		return printer.Print(win, win.printout, True)
