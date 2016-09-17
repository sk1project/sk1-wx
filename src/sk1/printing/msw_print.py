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

import os
import wx

from uc2 import uc2const

from sk1 import _, config
from sk1.printing import prn_events
from generic import AbstractPrinter, AbstractPS, COLOR_MODE
from pdf_printer import PDF_Printer

def get_print_data(app):
	if app.print_data is None:
		app.print_data = create_print_data()
	return app.print_data

def create_print_data():
	print_data = wx.PrintData()
	print_data.SetPaperId(wx.PAPER_A4)
	print_data.SetPrintMode(wx.PRINT_MODE_PRINTER)
	return print_data


class MSW_PS(AbstractPS):

	printers = []
	default_printer = ''

	def __init__(self, app, physical_only=False):
		self.app = app
		self.collect_printers()
		if not physical_only:
			self.printers.append(PDF_Printer())

	def readline(self, fileptr):
		return fileptr.readline().replace('\n', '').replace('\r', '').strip()

	def collect_printers(self):
		script = os.path.join(config.resource_dir, 'templates',
						'list_printers.vbs')
		appdata = self.app.appdata
		stdout = os.path.join(appdata.app_temp_dir, 'stdout.txt')
		os.system('cscript.exe %s>%s' % (script, stdout))
		fileptr = open(stdout, 'rb')
		line = self.readline(fileptr)
		while not line == '===': line = self.readline(fileptr)
		self.printers = []
		line = self.readline(fileptr)
		while not line == '===':
			if '::' in line:
				name, color = line.split('::', 1)
				printer = MSWPrinter(self.app, name)
				if color == '2':
					printer.color_supported = True
					printer.colorspace = uc2const.COLOR_RGB
				self.printers.append(printer)
			line = self.readline(fileptr)
		line = self.readline(fileptr)
		while not line == '===':
			if '::' in line:
				name, val = line.split('::', 1)
				if val == 'True':
					self.default_printer = name
					break

	def get_printer_by_name(self, name):
		if not name: self.get_default_printer()
		return AbstractPS.get_printer_by_name(self, name)


class MSWPrinter(AbstractPrinter):

	color_supported = False
	name = ''

	def __init__(self, app, name=_('Default printer')):
		self.app = app
		self.name = name
		AbstractPrinter.__init__(self)

	def is_virtual(self): return False
	def is_color(self): return self.color_supported

	def update_from_psd(self, page_setup_data):
		#--- Margins
		x0, y0 = page_setup_data.GetMarginTopLeft()
		x1, y1 = page_setup_data.GetMarginBottomRight()
		mrgns = (y0, x1, y1, x0)
		self.margins = tuple(map(lambda x:uc2const.mm_to_pt * x, mrgns))
		#--- Page Orientation
		print_data = self.app.print_data
		self.page_orientation = uc2const.PORTRAIT
		if print_data.GetOrientation() == wx.LANDSCAPE:
			self.page_orientation = uc2const.LANDSCAPE
		#--- Page format
		page_id = page_setup_data.GetPaperId()
		page_size = tuple(page_setup_data.GetPaperSize())
		page_size = tuple(map(lambda x:uc2const.mm_to_pt * x, page_size))
		self.page_format = (page_id, page_size)

	def run_propsdlg(self, win):
		print_data = get_print_data(self.app)
		print_data.SetPrinterName(self.name)
		data = wx.PageSetupDialogData(print_data)
		data.CalculatePaperSizeFromId()
		#--- Margins
		mrgns = map(lambda x:uc2const.pt_to_mm * x, self.margins)
		data.SetMarginTopLeft(wx.Point(mrgns[-1], mrgns[0]))
		data.SetMarginBottomRight(wx.Point(mrgns[1], mrgns[2]))

		dlg = wx.PageSetupDialog(win, data)
		if dlg.ShowModal() == wx.ID_OK:
			data = wx.PrintData(dlg.GetPageSetupData().GetPrintData())
			self.app.print_data = data
			self.update_from_psd(dlg.GetPageSetupData())
			dlg.Destroy()
			prn_events.emit(prn_events.PRINTER_MODIFIED)
			return True
		return False

	def run_printdlg(self, win, printout):
		print_data = get_print_data(self.app)
		print_data.SetPrinterName(self.name)
		print_data.SetColour(self.color_mode == COLOR_MODE)
		data = wx.PrintDialogData(print_data)
		data.EnablePageNumbers(False)
		printer = wx.Printer(data)
		return printer.Print(win, printout, True)
