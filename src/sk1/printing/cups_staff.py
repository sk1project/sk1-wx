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

import cups

from sk1 import _
from generic import AbstractPrinter, AbstractPS
from pdf_printer import PDF_Printer

class CUPS_PS(AbstractPS):

	connection = None
	printers = []
	default_printer = ''

	def __init__(self):
		self.connection = cups.Connection()
		self.printers = []
		prn_dict = self.connection.getPrinters()
		for item in prn_dict.keys():
			prn = CUPS_Printer(self.connection, item, prn_dict[item])
			self.printers.append(prn)
		self.printers.append(PDF_Printer())
		self.default_printer = self.connection.getDefault()

	def get_default_printer(self):
		for item in self.printers:
			if not item.is_virtual():
				if item.cups_name == self.default_printer:
					return item
		return self.printers[0]

	def get_printer_by_name(self, name):
		for item in self.printers:
			if item.get_name() == name:
				return item
		return None

	def get_printer_names(self):
		ret = []
		for item in self.printers:
			ret.append(item.get_name())
		return ret


class CUPS_Printer(AbstractPrinter):

	connection = None
	cups_name = ''
	details = {}
	attrs = {}

	def __init__(self, connection, cups_name, details):
		self.connection = connection
		self.cups_name = cups_name
		self.details = details

	def is_virtual(self): return False
	def get_name(self): return self.details['printer-info']
	def get_driver_name(self): return self.details['printer-make-and-model']
	def get_connection(self): return self.details['device-uri']
	def get_prn_info(self):
		return ((_('Driver:'), self.get_driver_name()),
				(_('Connection'), self.get_connection()))




