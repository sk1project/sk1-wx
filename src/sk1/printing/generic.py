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

class AbstractPrinter(object):

	name = 'Abstract Printer'
	copies = 1
	collate = False

	colorspace = uc2const.COLOR_GRAY
	page_format = ('A4', uc2const.PAGE_FORMATS['A4'])
	page_orientation = uc2const.PORTRAIT
	margins = (0.0, 0.0, 0.0, 0.0)

	def get_name(self): return self.name
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

	def get_page_size(self):
		if self.page_orientation == uc2const.PORTRAIT:
			return min(*self.page_format[1]), max(*self.page_format[1])
		return max(*self.page_format[1]), min(*self.page_format[1])


class AbstractPS(object):

	def get_default_printer(self): return None
