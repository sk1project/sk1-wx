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

from uc2 import uc2const


class AbstractPS(object):

	printers = []
	default_printer = ''

	def get_default_printer(self):
		for item in self.printers:
			if not item.is_virtual():
				if item.get_ps_name() == self.default_printer:
					return item
		if self.printers:
			return self.printers[0]
		else:
			return None

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


MONOCHROME_MODE = 'monochrome'
COLOR_MODE = 'color'

STD_PAGE_FORMAT = ('A4', uc2const.PAGE_FORMATS['A4'])
STD_MARGINS = (10.0, 10.0, 10.0, 10.0)
STD_SHIFTS = (0.0, 0.0)

class AbstractPrinter(object):

	name = 'Abstract Printer'
	copies = 1
	collate = False

	color_mode = MONOCHROME_MODE
	colorspace = uc2const.COLOR_GRAY
	page_format = STD_PAGE_FORMAT
	page_orientation = uc2const.PORTRAIT
	margins = STD_MARGINS
	shifts = STD_SHIFTS

	def get_name(self): return self.name
	def get_ps_name(self): return self.name
	def is_virtual(self): return True
	def get_connection(self): return '---'
	def get_driver_name(self): return '---'
	def get_state(self): return '---'
	def get_filepath(self): return ''
	def is_ready(self): return True
	def get_prn_info(self): return (('---', '---'), ('---', '---'))
	def printing(self, printout): pass
	def set_copies(self, val): self.copies = val
	def set_collate(self, val): self.collate = val
	def run_propsdlg(self, win): return False
	def run_printdlg(self, win, printout): return False

	def get_page_size(self):
		if self.page_orientation == uc2const.PORTRAIT:
			return min(*self.page_format[1]), max(*self.page_format[1])
		return max(*self.page_format[1]), min(*self.page_format[1])
