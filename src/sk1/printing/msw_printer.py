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

from sk1 import _, config
from sk1.printing.generic import AbstractPrinter, AbstractPS

class MSW_PS(AbstractPS):

	printers = []
	default_printer = ''

	def __init__(self, app, physical_only=False):
		self.app = app
		self.collect_printers()

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
				if color == '2':printer.color_supported = True
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
		for item in self.printers:
			if item.get_name() == name:
				return item
		return None

	def get_default_printer(self):
		for item in self.printers:
			if not item.is_virtual():
				if item.name == self.default_printer:
					return item
		if self.printers:
			return self.printers[0]
		else:
			return None

	def get_printer_names(self):
		ret = []
		for item in self.printers:
			ret.append(item.get_name())
		return ret


class MSWPrinter(AbstractPrinter):

	color_supported = False

	def __init__(self, app, name=_('Default printer')):
		self.app = app
		self.name = name

	def is_virtual(self): return False
	def is_color(self): return self.color_supported

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

	def run_printdlg(self, win, printout):
		data = wx.PrintDialogData(self.get_print_data())
		printer = wx.Printer(data)
		return printer.Print(win, printout, True)
